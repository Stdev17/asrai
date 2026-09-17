#!/usr/bin/env python3
"""Validate the stock vocabulary v2 and its illustrative instructions.

Standalone by design: the stock layer must not import from the origin corpus, so the
numeric semantics and lint live here rather than being borrowed from ad_ta_vocab.
Passing is not permission to execute anything.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT=Path(__file__).resolve().parent.parent
STOCK=ROOT/'src'/'asrai'/'data'/'stock'
# Numeric ops whose magnitude is meaningless without a fixed reference state.
DELTA_OPS=('relative_delta','multiply','add_delta','percentage_point_delta')
DIRECT_OPS=('set',)+DELTA_OPS
# Material scalars whose number only means something inside a declared shader model.
MATERIAL_SCALARS=('material.roughness','material.smoothness','material.metallic')

def load(path: Path) -> Any:
    def reject(token: str) -> None:
        raise ValueError(f'Non-JSON numeric literal: {token}')
    with path.open(encoding='utf-8') as handle:
        return json.load(handle,parse_constant=reject)

def scalar_change(baseline: float, operation: str, value: float) -> float:
    """Pure illustrative numeric semantics; never reads or changes an asset."""
    if not all(isinstance(n,(int,float)) and not isinstance(n,bool) and math.isfinite(n) for n in (baseline,value)):
        raise ValueError('Finite numbers required')
    if operation=='set':return value
    if operation=='add_delta':return baseline+value
    if operation=='multiply':return baseline*value
    if operation=='relative_delta':return baseline*(1+value/100)
    if operation=='percentage_point_delta':return baseline+value/100
    raise ValueError(f'Unsupported scalar operation: {operation}')

def lint_instruction(request: dict[str,Any], pack: dict[str,Any]) -> list[str]:
    """Representative semantic checks. Passing is not permission to execute."""
    errors: list[str]=[]
    index={e['id']:e for e in pack['entries']}
    context=request.get('context',{})
    applied=request.get('status')=='applied'
    for i,change in enumerate(request.get('changes',[])):
        prefix=f'changes[{i}]'
        tid=change.get('term_id')
        if tid not in index:
            errors.append(f'{prefix}: unknown term_id {tid!r}');continue
        entry=index[tid];q=entry['quantification'];op=change.get('operation')
        if op not in pack['operation_registry']:
            errors.append(f'{prefix}: unknown operation {op!r}');continue
        if op not in q['allowed_operations']:
            errors.append(f'{prefix}: operation {op!r} not allowed by this term profile')
        basis=change.get('magnitude_basis')
        if applied and basis=='llm':
            errors.append(f'{prefix}: a model-invented magnitude must not reach an applied instruction')
        quantity=change.get('quantity')
        if quantity and basis in (None,'none'):
            errors.append(f'{prefix}: a quantity requires a magnitude_basis')
        if op in DELTA_OPS and not context.get('baseline_ref'):
            errors.append(f'{prefix}: fixed baseline_ref required')
        if q['mode'] in ('proxy_only','qualitative','undefined') and op in DIRECT_OPS:
            errors.append(f'{prefix}: perceptual term is not a direct numeric property')
        if op=='define_metric' and not change.get('metric'):
            errors.append(f'{prefix}: explicit metric definition required')
        if quantity:
            unit=quantity.get('unit')
            if unit not in pack['unit_registry']:
                errors.append(f'{prefix}: unknown or ambiguous unit {unit!r}')
            elif op not in ('relative_delta','multiply','percentage_point_delta') and unit not in q['allowed_units']:
                errors.append(f'{prefix}: unit {unit!r} is not admitted by profile {q["profile_id"]}')
            expected={'relative_delta':'percent_relative','multiply':'factor',
                      'percentage_point_delta':'percentage_point'}.get(op)
            if expected and unit!=expected:errors.append(f'{prefix}: {op} requires {expected}')
            if unit in ('px','px2','texel'):
                if not context.get('image_ref',context.get('grid_ref')) or not context.get('resolution'):
                    errors.append(f'{prefix}: named image/grid and resolution required')
            if unit=='svg_user_unit' and 'viewBox' not in context:
                errors.append(f'{prefix}: SVG viewBox required')
            if unit=='frame':
                tb=context.get('timebase',{});fps=tb.get('fps')
                if not isinstance(fps,(int,float)) or isinstance(fps,bool) or fps<=0 or not tb.get('clock'):
                    errors.append(f'{prefix}: positive timebase.fps and clock required')
            val=quantity.get('value')
            values=val if isinstance(val,list) else [val]
            if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in values):
                errors.append(f'{prefix}: quantity must contain finite numbers')
        if tid=='camera.fov' and op=='set':
            if context.get('fov_axis') not in ('vertical','horizontal','diagonal'):
                errors.append(f'{prefix}: FOV axis required')
            if context.get('projection')!='perspective':
                errors.append(f'{prefix}: FOV request requires explicit perspective projection')
        if tid in MATERIAL_SCALARS and op in DIRECT_OPS and not context.get('shader_model'):
            errors.append(f'{prefix}: shader_model required')
        if op=='set_sequence':
            seq=change.get('sequence',[])
            if not seq or len(seq)!=len(set(seq)):
                errors.append(f'{prefix}: nonempty unique ordered stage list required')
    ex=request.get('execution',{})
    if ex.get('authorized') and not (ex.get('adapter') and ex.get('binding_resolved')):
        errors.append('execution: authorization requires a bound adapter and a resolved binding')
    if applied and not ex.get('run_ref'):
        errors.append('execution: an applied instruction must carry a run_ref')
    return errors

def validate(root: Path) -> dict[str,Any]:
    pack=load(root/'vocab.v2.json')
    examples=load(root/'instruction_examples.v2.json')['examples']
    checks=0
    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks+=1
        if not condition:raise ValueError(message)
    schema_result='not_run_jsonschema_not_installed'
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        pass
    else:
        for name,doc in (('vocab.v2.schema.json',pack),):
            schema=load(root/name);Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(doc)
        schema=load(root/'instruction.v2.schema.json');Draft202012Validator.check_schema(schema)
        validator=Draft202012Validator(schema)
        for ex in examples:validator.validate(ex)
        schema_result='passed_draft_2020_12'

    ids=[e['id'] for e in pack['entries']]
    require(len(ids)==len(set(ids)),'Duplicate term ids')
    stats=pack['derivation_stats']
    require(len(ids)==stats['source_entries']-stats['dropped_entries'],
            'Entry count does not match the declared derivation: stock = source - learning layer')
    require(set(stats['dropped_learning_categories'])<={'methods'},
            'Only the learning category may be removed from the v1 domain vocabulary')
    # A learning-category entry may survive only as a named exception that says why it is here.
    unexplained=[e['id'] for e in pack['entries']
                 if e['category'] in stats['dropped_learning_categories'] and 'scope_note' not in e]
    require(not unexplained,f'Learning-category terms survive without a scope_note: {unexplained}')
    require(set(stats['reincluded_from_learning'])=={e['id'] for e in pack['entries'] if e['category']=='methods'},
            'The surviving methods entries do not match the declared re-inclusion set')
    require(len(ids)==pack['metadata']['entry_count'],'Entry count mismatch')
    require(pack['language']=='en','The stock vocabulary is English-canonical')
    kept=set(ids)
    def walk_keys(node: Any) -> Any:
        if isinstance(node,dict):
            for key,value in node.items():
                yield key
                yield from walk_keys(value)
        elif isinstance(node,list):
            for value in node:yield from walk_keys(value)
    stray=sorted({k for k in walk_keys(pack) if k.endswith('_ko') or k=='curriculum_weeks'})
    require(not stray,f'Education-era or language-suffixed keys survive: {stray}')
    cats={c['id']:c for c in pack['categories']}
    for entry in pack['entries']:
        require(entry['category'] in cats,f'{entry["id"]}: unknown category')
        require(len(entry['origin']['entry_sha256'])==64,f'{entry["id"]}: missing origin.entry_sha256')
        require(bool(entry['description'].strip()) and bool(entry['operationalization']['guidance'].strip()),
                f'{entry["id"]}: empty description or guidance')
        require(bool(entry['aliases']),f'{entry["id"]}: no aliases to match against')
        require(entry['quantification']['profile_id'] in pack['quantification_profiles'],
                f'{entry["id"]}: unknown quantification profile')
        for unit in entry['quantification']['allowed_units']:
            require(unit in pack['unit_registry'],f'{entry["id"]}: unknown unit {unit}')
        for op in entry['quantification']['allowed_operations']:
            require(op in pack['operation_registry'],f'{entry["id"]}: unknown operation {op}')
        for ref in entry['confusable_with']:
            require(ref['term_id'] in kept,f'{entry["id"]}: confusable_with points outside v2: {ref["term_id"]}')
            require(ref['term_id']!=entry['id'],f'{entry["id"]}: self confusion reference')
    for token in pack['ambiguous_tokens']:
        require(len(token['candidate_ids'])>1,f'{token["token"]}: an ambiguity needs at least two candidates')
        for ref in token['candidate_ids']:
            require(ref in kept,f'{token["token"]}: candidate outside v2: {ref}')
    counts=Counter(e['category'] for e in pack['entries'])
    for cat,count in counts.items():require(count==cats[cat]['entry_count'],f'{cat}: category count mismatch')

    locales={}
    for path in sorted((root/'locales').glob('*.json')):
        doc=load(path)
        require(doc['locale']==path.stem and doc['spec_language']=='en',
                f'{path.name}: locale code must match the filename and spec_language must be "en"')
        require(set(doc['terms'])<=kept,f'{path.name}: term ids outside v2')
        require(len(doc['terms'])==len(ids),f'{path.name}: covers {len(doc["terms"])}/{len(ids)} terms')
        seen: dict[str,str]={}
        flagged=0
        for tid,row in doc['terms'].items():
            require(not set(row)-{'label','aliases','description','review'},
                    f'{path.name}: {tid} carries fields beyond label/aliases/description/review')
            require(bool(str(row['label']).strip()) and bool(str(row['description']).strip()),
                    f'{path.name}: {tid} has an empty label or description')
            # One label must not name two terms, or a comment mentioning it cannot be routed.
            key=row['label'].casefold()
            require(key not in seen,f'{path.name}: {row["label"]!r} labels both {seen.get(key)} and {tid}')
            seen[key]=tid
            flagged+='review' in row
        locales[doc['locale']]={'term_count':len(doc['terms']),'translation_basis':doc['translation_basis'],
                                'needs_confirmation':flagged}

    example_results=[]
    for ex in examples:
        errors=lint_instruction(ex,pack)
        require(not errors,f'Example lint failed: {ex["id"]}: {errors}')
        example_results.append({'id':ex['id'],'lint':'passed','ready_for_execution':False})
    numeric_tests=[
      ('relative decrease',scalar_change(.5,'relative_delta',-20),.4),
      ('percentage-point decrease',scalar_change(.5,'percentage_point_delta',-20),.3),
      ('multiply',scalar_change(1,'multiply',1.2),1.2),
      ('baseline repeat',scalar_change(.5,'relative_delta',-20),scalar_change(.5,'relative_delta',-20)),
      ('length-to-area',1.2**2,1.44),
      ('area-to-length',math.sqrt(1.2)**2,1.2),
      ('authored frames',8/12,2/3),
      ('display frames',8/60,2/15)]
    for name,value,expected in numeric_tests:
        require(math.isclose(value,expected,rel_tol=1e-12,abs_tol=1e-12),f'numeric: {name}')
    negative=[]
    def rejected(name: str, ex: dict[str,Any]) -> None:
        errs=lint_instruction(ex,pack);require(bool(errs),f'Ambiguous request not rejected: {name}')
        negative.append({'name':name,'rejected':True,'reasons':errs})
    by={e['id']:e for e in examples}
    bad=deepcopy(by['example.body_width']);del bad['context']['baseline_ref']
    rejected('percentage without baseline',bad)
    bad=deepcopy(by['example.silhouette_gap']);del bad['context']['resolution']
    rejected('px without image resolution',bad)
    bad=deepcopy(by['example.camera_fov']);del bad['context']['fov_axis']
    rejected('FOV without axis',bad)
    bad=deepcopy(by['example.anticipation']);del bad['context']['timebase']
    rejected('frames without fps/clock',bad)
    bad=deepcopy(by['example.material_smoothness']);del bad['context']['shader_model']
    rejected('material scalar without model',bad)
    bad=deepcopy(by['example.readability_proxy'])
    bad['changes'][0]={'term_id':'perception.readability','operation':'relative_delta',
                       'quantity':{'value':20,'unit':'percent_relative'},'property_binding':None,
                       'magnitude_basis':'example'}
    rejected('readability as direct numeric property',bad)
    bad=deepcopy(by['example.body_width']);bad['changes'][0]['quantity']['unit']='%'
    rejected('ambiguous percent unit',bad)
    bad=deepcopy(by['example.vector_anchor']);del bad['context']['viewBox']
    rejected('SVG coordinate without viewBox',bad)
    bad=deepcopy(by['example.body_width']);bad['execution']['authorized']=True
    rejected('authorization without adapter or binding',bad)

    return {
      'validation_date':'2026-09-13','status':'passed','json_schema':schema_result,
      'programmatic_checks_passed':checks,'entry_count':len(ids),'category_count':len(cats),
      'judgment_term_count':pack['metadata']['judgment_term_count'],
      'manipulation_term_count':pack['metadata']['manipulation_term_count'],
      'ambiguous_token_count':len(pack['ambiguous_tokens']),
      'head_term_locales':locales,'entry_counts_by_category':dict(counts),
      'numeric_test_count':len(numeric_tests),'negative_lint_test_count':len(negative),
      'negative_tests':negative,'example_results':example_results,
      'derivation_stats':pack['derivation_stats'],
      'limitations':[
        'Scope selection is a category and surface rule plus a hand-written allowlist. It is not evidence '
        'that these 475 terms are the industry-standard set for game art direction.',
        'Descriptions and guidance are editorial English carrying translated_by: llm. Terms marked '
        'translation_review: needed have not been confirmed by a human.',
        'The lint guards representative errors only; it is not a complete type checker for any tool.',
        'No number in the examples is a recommended threshold.']}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=STOCK)
    parser.add_argument('--report',type=Path,help='Write JSON report; otherwise stdout only.')
    args=parser.parse_args()
    try:
        result=validate(args.root)
        rendered=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
        if args.report:args.report.write_text(rendered,encoding='utf-8')
        print(rendered,end='');return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'failed','error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
