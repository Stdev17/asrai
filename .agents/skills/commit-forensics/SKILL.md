---
name: commit-forensics
description: Use before choosing a gate or at a milestone refactor: spec-perturbation run backwards over a commit history — message as spec, diff as footprint — scoring physical, semantic and authority leaks from git alone.
---

# commit-forensics

spec-perturbation **mode 2**: the sample is the history, and the projection is the message read
against the diff. Nothing here dispatches a worker, so nothing here needs a harness.

Evidence is the diff, the numstat and what the tests at that commit accepted. A message is a claim:
the spec its footprint is scored against, and itself checked against the diff. A commit's hunks are
read only after its prediction is on disk.

## The record directory is the context

`docs/experiments/<date>-commit-forensics/`, gitignored. Every step reads and writes there; the
context holds one batch of 25 commits. After a reset, `ls` and resume from the last complete
artifact. Never `git log -p` into context. Read a hunk as `--stat`, then at most 120 lines by
`sed -n`; larger, its first and last 30 plus `grep` for the message's nouns. Template commits are
listed and excluded.

## 1. Dump and map

`git log --reverse --format='=== %H %h %an %ad%n%B' > messages.txt`, and `--numstat >
commits.numstat`. Write `owner(path)` once, from the repository's own documents (where a thing is
written, write policies): one owner per file, tests their own, a rename on both sides. The map is a
hypothesis: a file that keeps planting document-kind defects while mapped as data is cut wrong.
Apply spec-perturbation's convergence rule to it.

## 2. Predict per batch, before any hunk

`predictions.jsonl`, one line per commit: `{sha, stated: {owner: quoted sentence}, adapters: {owner:
rule}, unlocated: [changes claimed but not placed], bootstrap}`. Adapters only from coupling rules
the repository wrote down, by name. If numstat was seen first, say so in the file. Resume = last sha
present.

## 3. Footprint, by script

`unstated = touched − (stated ∪ adapters)`; `omitted = (stated ∪ adapters) − touched`; lines per
owner; each unstated hunk to `hunks/<sha>--<path>.diff`. Read each; class: intended-unnamed, ripple,
cargo (independent of the stated work — a new file the message never names, until read), drive-by.
"Also" in a message marks bundling: read what follows it.

## 4. Three layers

- **physical**: step 3.
- **semantic**, inside a predicted owner: `git log -G` on module-level constants, public names and
  any signature under `src/`; assertions removed under `tests/`; `"value":` in the claims file;
  `[decided]` on contract files only. Pair each removed assertion with its replacement. A pinned
  value that vanished or loosened, or a hit no sentence of the message names, is a semantic leak.
- **authority**: a contract changed with nothing recorded — a `[decided]` item added or edited with
  no review or conventions entry in that commit; an assertion flipped or a fixture regenerated with
  no measurement named; a claim moved with no basis. Apply spec-perturbation's report-word list; the diff
  it demands is this commit's. No authority is a leak whatever the footprint says.

## 5. Defects

Candidates: `grep -inE 'fix|drift|silent|never|claimed|wrong|leak|dead|stale' messages.txt` to a
file, plus steps 3–4; 25 at a time. Each: confirm the fix is in the diff — a claimed fix the diff
lacks is a finding, not a row; `git log -S`/`-G` for the planting commit; one row `{id, defect,
planted_at, files, site: stated|adapter|unstated|omitted, hunk, layer, class, found_at, found_by,
latency, open}`. Note that the population is what someone found, and that one author planting and
finding is a correlated sample.

## 6. Numbers → `report.json`

Per commit: files, lines, unstated owners and lines, omitted, defects planted. Spearman of defects
against unstated owners and against files, with and without the largest commit. Counts by site,
layer, class, found_by; latency by site; cargo commits (unnamed files, lines, defects, latency);
open items. Those keys, no others; the prose report is written from that file alone, every number
traceable to a key.

## 7. Decide by mechanism; repair only the mechanical

cargo → each message names every owner, else split · fan-out → a claims registry · omission → the
coupling rule as a test · silence → negative-clause tests · authority → a `[decided]` edit needs a
recorded reason · misdrawn owner → one boundary ticket. An unsourced number is reported, never
invented. Open items go to the status log.

## Mistakes

- predicting after reading the diff: the prediction then contains the answer
- a clean footprint read as a clean commit: an untouched paragraph in a touched file is invisible
