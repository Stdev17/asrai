#!/usr/bin/env python3
"""Mechanically review the stock translations and mark what a human still has to confirm.

These are the checks a script can honestly make. Whether a term is the one a studio in
that language actually says is not among them, which is why flagged rows stay in the file
as a worklist for translation pull requests rather than being silently accepted.

Idempotent: every run recomputes the flags, so a fixed row loses its flag.
Run after tools/trim_vocab.py.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import unicodedata
from typing import Any

ROOT=Path(__file__).resolve().parent.parent
STOCK=ROOT/'src'/'asrai'/'data'/'stock'
# Languages whose terms are normally written in a non-Latin script. A Latin-only label
# there is either a loanword the field really uses (PBR, UV, LOD) or an untranslated row.
NATIVE_SCRIPT={'ko':('HANGUL',),'ja':('HIRAGANA','KATAKANA','CJK'),'th':('THAI',),
               'zh-Hans':('CJK',),'zh-Hant':('CJK',)}

def has_script(text: str, prefixes: tuple[str,...]) -> bool:
    for ch in text:
        try:name=unicodedata.name(ch)
        except ValueError:continue
        if any(name.startswith(p) for p in prefixes):return True
    return False

def review_locale(code: str, terms: dict[str,Any], base: dict[str,Any]) -> tuple[Counter,list[str]]:
    counts: Counter[str]=Counter()
    errors: list[str]=[]
    by_label=defaultdict(list)
    for tid,row in terms.items():by_label[row['label'].casefold()].append(tid)
    collisions={label:ids for label,ids in by_label.items() if len(ids)>1}
    for label,ids in sorted(collisions.items()):
        errors.append(f'{code}: {label!r} is the label of {len(ids)} different terms: {", ".join(sorted(ids))}')
    for tid,row in terms.items():
        row.pop('review',None)
        english=base[tid]['label']
        if row['label'].casefold()==english.casefold():
            row['review']='confirm_loanword';counts['confirm_loanword']+=1
        elif code in NATIVE_SCRIPT and not has_script(row['label'],NATIVE_SCRIPT[code]):
            row['review']='confirm_script';counts['confirm_script']+=1
        if not row['description'].strip() or not row['label'].strip():
            row['review']='missing';counts['missing']+=1
    counts['reviewed']=len(terms)
    return counts,errors

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=STOCK)
    parser.add_argument('--check',action='store_true',help='Report without writing flags; fail on a hard defect.')
    args=parser.parse_args()
    base={e['id']:e for e in json.loads((args.root/'vocab.v2.json').read_text(encoding='utf-8'))['entries']}
    summary,errors={},[]
    for path in sorted((args.root/'locales').glob('*.json')):
        doc=json.loads(path.read_text(encoding='utf-8'))
        counts,errs=review_locale(doc['locale'],doc['terms'],base)
        errors.extend(errs)
        flagged=sum(v for k,v in counts.items() if k!='reviewed')
        summary[doc['locale']]={'terms':counts['reviewed'],'needs_confirmation':flagged,
                                **{k:v for k,v in sorted(counts.items()) if k!='reviewed'}}
        if not args.check:
            doc['review_summary']={'checked_by':'tools/review_locales.py','needs_confirmation':flagged}
            path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'locales':summary,'hard_defects':errors},ensure_ascii=False,indent=2))
    return 1 if errors else 0

if __name__=='__main__':raise SystemExit(main())
