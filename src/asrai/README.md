# `src/asrai/` — the package

Twelve modules include transports, core owners and version metadata; **nothing in the core imports a
transport**, which is what makes invariant 9 (`CLI and MCP produce the same output for the same
fixture`) structural rather than a promise.

This page is the **feature realm's interior**, one level below the
[realm ledger](../../docs/architecture.md). Module count is not responsibility count: every module
drawn in the graph below owns an invariant, while `cli`, `server`, `profile` and `__init__` do not.
`run` is drawn and owns one: it is the only module that opens the asset, and the only one that
presents what a run concluded. `reading` is drawn and owns one too, which is why it is a module and
not a section of `run`: presenting a run is not a question about light, and a renderer that lived
inside a family would be a renderer with a branch per family. The graph stays inside the node and
owner limits §0 of [conventions.md](../../docs/conventions.md) sets; crossing either is the signal to
stop and review scope, never to shrink the drawing.
`profile` is the exception worth naming: it projects a cache, and the `cache` realm owns nothing by
construction, so a module that only writes one cannot own an invariant either.

## Owner dependencies

Arrows point from consumer to provider; labels contain only the signatures or data declarations
crossing that boundary, and a wrapped line is part of the same signature. `DATA: Path` and
`SILHOUETTE_ALPHA: int` describe inferred constant types, not newly declared interfaces. Solid edges
include Python references; dashed edges are data-only contracts, including values passed through
transports. `light` constructs observation dictionaries that `records` validates when submitted, and
finding dictionaries that `reading` renders; it calls neither module. Findings ride back inside
`pass_`'s return, `run` takes them out and hands them to `reading`, and they reach no transport: a
reply carrying both them and the sentences built from them would say one thing twice under different
names, with nothing to stop the copies drifting apart.

```mermaid
flowchart TB
    CONFIG["config"]
    RUN["run"]
    LIGHT["light"]
    READING["reading"]
    DOCTOR["doctor"]
    MEASURE["measure"]
    RECORDS["records"]
    VOCAB["vocab"]

    LIGHT -->|"load(path: Path)<br/>→ tuple[np.ndarray, dict]<br/>luminance(rgb: np.ndarray)<br/>→ np.ndarray<br/>hsl(rgb: np.ndarray)<br/>→ tuple[np.ndarray,<br/>np.ndarray, np.ndarray]<br/>_r(x) → float<br/>layer_index(value, where)<br/>→ int #124; None<br/>SILHOUETTE_ALPHA: int"| MEASURE
    RUN -->|"pass_(ctx: dict,<br/>out_dir: Path #124; None,<br/>answers: dict #124; None)<br/>→ dict"| LIGHT
    RUN -->|"sentences(<br/>findings: list[dict] #124; None,<br/>profile: str,<br/>overlay: dict #124; None)<br/>→ list[str]"| READING
    RUN -->|"load(path: Path)<br/>→ tuple[np.ndarray, dict]<br/>layer_index(value, where)<br/>→ int #124; None<br/>SILHOUETTE_ALPHA: int"| MEASURE
    LIGHT -->|"DATA: Path<br/>term_id: str"| VOCAB
    READING -->|"DATA: Path"| VOCAB
    DOCTOR -->|"sha256_file(path)<br/>→ str"| RECORDS
    DOCTOR -->|"pack() → dict[str, Any]<br/>index()<br/>→ dict[str, dict[str, Any]]<br/>DATA: Path"| VOCAB
    RECORDS -->|"index()<br/>→ dict[str, dict[str, Any]]<br/>lint_instruction(<br/>request: dict[str, Any])<br/>→ list[str]"| VOCAB
    LIGHT -.->|"observation.v1: dict"| RECORDS
    LIGHT -.->|"finding: {say, terms,<br/>settled, basis, evidence}"| READING
    DOCTOR -.->|"cfg: dict"| CONFIG
    RECORDS -..->|"scale: 'native' #124;<br/>'target' #124; 'thumbnail'"| MEASURE
```

`doctor` consumes `config.load()` output through the transports, including `observer` and `_root`. The
scale literals accepted by `records` mirror the keys of `measure.v1.scales`. `light` uses canonical
vocabulary term IDs from surface policy and a literal ID in its observation builder; that dependency
remains even if the data directory moves. These are inferred data contracts, not additional typed
Python APIs, so the graph cannot be recovered faithfully from an import count. No core owner imports
`cli.py` or `server.py`, and the transports' fan-out is not an extra product responsibility.

| module | owns | public surface | the rule it enforces |
|---|---|---|---|
| `config.py` | `asrai.toml` in the project root, overlaid on defaults | `root`, `load`, `team_dir` | transports resolve configured project and team-corpus paths here |
| `vocab.py` | stock vocabulary v2 — lookup, search, locales, instruction lint | `get`, `search`, `categories`, `category`, `translations`, `langs`, `locale`, `localize`, `expand`, `compact`, `pack`, `index`, `lint_instruction`, `scalar_change`, `resolve_lang`, `locale_codes` | invariant 3 — a `proxy_only \| qualitative \| relational \| structural` term never takes `set` or a delta, and `lint` blocks it |
| `measure.py` | deterministic V0 measurement with Pillow and numpy | `load`, `measure`, `luminance`, `hsl`, `stats` | same bytes in, same JSON out. It never writes a file, and it refuses above 12 Mpx before decoding |
| `run.py` | one run: the asset read once, its subjects, the identity a form is stamped with, and everything the run then says | `open_run`, `ledger`, `SUBJECTS_MAX` | every family in a run sees the same pixels, the same subjects and the same `run_sha256`, and none of them decides who hears what it found. A family is handed a run and cannot open a file, choose a subject, name a run or address a reader, so families cannot disagree about the thing they are all looking at, or speak about it in as many voices as there are of them |
| `light.py` | the surface pass: `surfaces.v1` instantiated as a two-phase ledger over a run | `pass_`, `surfaces` | direction may be measured; magnitude may not be invented. Every number it returns is a measurement, a count or a sign |
| `reading.py` | every surface that presents a run: the reader profiles and the sentences one reader is handed | `sentences`, `profiles` | judgment outranks expression. A reading is a projection of findings under a profile and there is no verdict in the module to move, so what changes per reader is what is said and never what is true |
| `records.py` | append-only JSONL — `observation.v1`, `pairwise.v1`, `instruction.v2` | `validate`, `append`, `read`, `canonical_json`, `sha256_file`, `new_id` | invariants 6 and 12 — nothing is edited or deleted, and `L2_ONLY` terms stay `unknown` at L1 |
| `doctor.py` | the environment report and `asrai.lock.json` | `run`, `snapshot`, `tool_version`, `pinned_view` | invariant 14 — every run can say what it ran with, and drift is reported |
| `profile.py` | the overlay: what a team's records demonstrate about the vocabulary, cached beside them | `project`, `overlay`, `digest` | none. It is a projection of `records.jsonl`, and the [`cache` realm](../../docs/architecture.md) owns no invariant: a wrong row is deleted, never repaired |
| `cli.py` | the CLI transport | `main`, `build_parser` | one JSON document per command, printed, never written into an input |
| `server.py` | the stdio MCP transport | the seven tools below, `main` | the byte budget of spec.md §6: the tool surface measures 3,843 bytes and is held under 1,200 tokens by a test, and detail goes to `SKILL.md`; `retrieve` and `preview` are still to come |
| `__init__.py` | the version string | — | — |

MCP tools, and the CLI verb each mirrors:

| tool | CLI |
|---|---|
| `vocab_search` | `asrai vocab search` |
| `vocab_get` | `asrai vocab get \| category \| categories \| langs \| translations` |
| `measure` | `asrai measure` |
| `light_ledger` | `asrai light-ledger` |
| `record` | `asrai record` |
| `lint` | `asrai lint` |
| `doctor` | `asrai doctor` |

Not built: `retrieve`, `preview`, `apply`, `rasterize`, `render`. The bundled skill says so; an agent
that improvises them is a bug, not a feature.

## What this boundary currently exposes

- `light` imports `measure._r`, a private rounding helper, and `SILHOUETTE_ALPHA`. The private import
  violates the intended public boundary; drawing it records the defect rather than authorizing it.
- `measure` also owns `label` and `layer_index`, which are neither measurements nor pixels in the
  sense the rest of that module is. They are there because two owners need each and a predicate with
  no owner gets written twice — which is what `light` and `measure` had already done with one flood
  fill, before a second family existed to blame for it. If a third such helper appears, the module
  they belong in is the question, not where to put that one.
- `light` reads its surface-policy file through `vocab.DATA`, and `reading` reads the reader profiles
  the same way. That is a directory dependency in both cases, not a vocabulary lookup interface; the
  second one arrived with the profiles and is the same seam, not a new one.
- `doctor` reaches `records` only for `sha256_file`. Environment reporting does not need the record
  lifecycle; the edge reflects where the generic helper currently lives.
- Observation dictionaries, configuration fields, scale keys and canonical term IDs cross owners
  without Python imports.

These are existing seams to address when their boundary is changed, not reasons to create new owners or
to refactor runtime code in a documentation change. The graph does not demand a subsystem split, does
not establish that the lighting policies are empirically valid, and does not pre-approve retrieval,
rendering, recipes or publishing. Evaluate those against the single job before adding them.

## Working here

- `light.py` carries its reasoning at the top. Read it before changing a threshold. The agreement
  cutoffs remain unverified implementation policy; do not mistake their presence for measured validity.
- A new measurement belongs in `measure.py` only if it is deterministic and asset-wide. Anything that
  needs a subject, an emitter or an observer belongs in `light.py`.
- Anything a reader or a model is handed belongs in `reading.py`, and what a family knows about it is
  a finding row. A family that wants a sentence said differently changes the finding, never the reader.
- A new field crossing the MCP or record boundary is a naming decision first: [docs/conventions.md](../../docs/conventions.md) §1.
- The contract is [docs/spec.md](../../docs/spec.md). When this file disagrees with it, spec.md wins.
