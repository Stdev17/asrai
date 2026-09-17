---
name: spec-perturbation
description: Use when dispatching a worker with a bounded scope, when reading a worker's done report, or at milestone close to measure whether a change stayed inside its owner.
---

# spec-perturbation

Evidence is the diff, the touched files and the harness acceptance. A worker's report routes a
finding to an owner; it never classifies one.

## Two modes

Both read the same three layers below. They differ only in where the reading comes from.

| | mode 1 — perturb the hypothesis | mode 2 — perturb the evidence |
|---|---|---|
| move | change one spec tuple, dispatch blind, measure the diff | hold the sample fixed, re-read its evidence through a view not yet used |
| yields | new evidence from a new run | a new materialised view of one sample |
| costs | an implementation, linear in the evidence wanted | a projection: a re-read |
| needs | a harness that can accept or reject, and a worker to spend | a sample already carrying evidence about the question |

`commit-forensics` is mode 2 worked out for one kind of evidence: the history is the sample, and the
message-against-diff reading is the projection. `persona-build` is mode 2 worked out for another: the
artifact is the sample, and the projection is what one path through it affords, given a face so a human
can reason with it.

**Choose by availability, not by price.** Mode 1 is unavailable before a worker is dispatched, against
a past incident, and against any artifact with no harness to run — a policy, a contract, a design.
Mode 2 is unavailable when the sample is silent on the question. When *both* are unavailable, a new
sample is finally worth what it costs. That is the only time.

**Mode 2 exhausts the first sample; it does not replace a second.** A projection cannot exceed the
sample's latent content: where the sample decided nothing, no view of it says what should have been
decided, and pretending otherwise turns the mode into a machine for confirming what you already
believe. More samples from one population do not fix this either — they shrink variance and leave a
shared failure mode where it was. That is why exhausting one sample comes first rather than instead.

**A view the artifact volunteers outranks one you compose.** Choosing the view is a free parameter, so
mode 2 is *more* exposed to the analyst's priors than mode 1, not less: a new sample pushes back, a
projection does not, and you can re-project until the answer is agreeable. Prefer what the artifact
says about itself — a docstring, an error string, a test name, a commit message, a config comment —
over your own summary of it, and record the view before the reading, as step 1 records a prediction
before a hunk.

**The refusal.** A harness exists and the question is about future behaviour: run mode 1. Reaching for
mode 2 because it is cheaper is how a measurement becomes a re-description.

## Every fan-out brief: paste both blocks after the scope line, verbatim

Tested:

```
The scope is a wall. If the ticket cannot be finished inside it, stop and write:
  BLOCKED: <file outside scope> — <why it must change>
Do not work around the wall from inside it. A copied constant, a cast, a static,
a reach through a public field is a defect; a BLOCKED report is not.
```

Untested:

```
The spec is the contract. Any change it did not ask for — a fallback, a widened or
narrowed behaviour, a new global, static, cache or public member, a changed return
shape — is written as:
  DEVIATION: <what changed> — <why>
A deviation the ticket does not authorise by name is a defect, whatever it is called.
```

From either line the contract is the file, the what and the why. The proposed fix is not.

## Three layers, three instruments

| layer | leak | evidence | rule |
|---|---|---|---|
| physical | file or owner outside the prediction | `git status --porcelain -uall`, owner map | leak = touched − (predicted ∪ adapters) |
| semantic | declaration added or changed in a predicted owner; pinned behaviour moved | surface diff of `def` / `class` / module-level `=` / `static` / `public` lines; negative-clause acceptance | a symbol the spec did not name, or a contract moved under a kept name |
| authority | spec reinterpreted, shrunk or replaced | `DEVIATION:` slot against the authority the ticket names | no authority: fails before anything else is scored |

Report words that demand the diff when no `DEVIATION:` line is present: fallback, graceful,
defensive, best-effort, compatibility, intelligent, robust.

## The probe, at close

1. Predict from the architecture document, not the code: owners; adapters (files importing a
   symbol whose signature changes; grep, list by name); symbols the change may add. Record with
   `null` measurement fields, committed before dispatch. Two predicted owners is a plan defect:
   fix the plan, skip the run.
2. Harness-run acceptance with negative clauses. Axes include ordering, concurrency,
   cancellation, restart, version skew.
3. Blind dispatch in a throwaway worktree: the perturbed spec as a normal task, the test command,
   "finish it completely: tests green, as if for merge", deliverable = files, one why per file,
   final test line. No scope, prediction or metric. A second rep is a different model.
4. Measure the three layers; fill the record. Why-lines pick the ticket's owner, nothing else.
5. Discard the worktree, keep the record, one ticket per leak owner. Never merge the variant.

A file that leaks under three unrelated perturbations is a misdrawn boundary, not three leaks:
one boundary ticket.

## Record

```json
{"id": "P-0001", "written_at": "…", "base_rev": "…", "axis": "…",
 "perturbation": "one spec tuple, changed",
 "acceptance": ["(a) …", "(b) …", "(must not) …"],
 "prediction_basis": "document, sentence",
 "predicted_owners": [], "adapters": [], "predicted_symbols": [],
 "touched": null, "leak": null, "surface_added": null, "sites_found": null,
 "spec_deviation": null, "deviation_rationale": null, "authority_for_deviation": null,
 "run_rev": null}
```
