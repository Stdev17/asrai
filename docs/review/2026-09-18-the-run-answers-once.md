# The run answers once — 2026-09-18

> 2026-09-18 · verified at `9ea08f1` · Claude Opus 5

For the package author, after the run owner exists and before it judges anything. `250a335` gave the
run the asset: it reads the file once, settles the subjects once and takes the run identity. It did not
give the run a judgment. `run.ledger` is one line that hands the run to `light` and returns whatever
comes back, so everything a run *says* — its verdict, its record, its reading — is still the lighting
family's, built in `light.py` and checked by nobody.

`2026-09-17-family-and-run.md` §5 listed five things the run owner takes over. Two of them, **the record
builder** and **the three axes**, are the two that were not moved, and they are the two that decide what
a run is worth to the corpus. This settles who owns them and on what rule.

What it adds to §5 is that the rule is not a tidiness argument. Three defects were measured at `9ea08f1`
against the flow `spec.md` §7.1 calls valid, and all three are the same missing owner. They are in §2.

## 1. Where the run stands against its own list

| §5 says the run owns | where it lives at `9ea08f1` |
|---|---|
| the subject primitive | `run._subjects` — moved |
| capture contract ingestion | `run._subjects` — moved |
| the two-phase form/answers protocol, with the run stamp | split: `run.open_run` takes the identity, `light._form` and `light._answers` hold the protocol |
| **the record builder** | `light._records` — not moved |
| **the three axes** | `light._verdict` — not moved |
| every surface that presents a run | `light.for_reader`, `light.sentences` — not moved; both transports call them |

The first two are structural and hold by construction: a family takes a run and never a path, so it
cannot open a file or name a subject. The last four hold by nothing. Nothing stops a second family from
building its own record, deriving its own axes or writing its own reader; each would be a second
definition of a word the corpus already uses.

## 2. What that costs today, measured

The probe is the flow §7.1 names valid — *handing the form back unfilled is a valid phase two* — run
over every fixture in `tests/fixtures/`, at `9ea08f1`.

**The record the ledger returns is rejected by the tool that stores it.** On all four fixtures, phase two
of an unfilled form returns `observations: []`, and `records.validate` answers `observations must be a
non-empty list`. The model is told to call `light_ledger` and then `record`; on this flow the second call
fails on what the first call handed it. Nothing between them looks, because a record is validated only
inside `records.append` — the production path never calls `records.validate` at all, and the two places
that do are tests.

**A run warns a reader and tells the corpus nothing.** On `flat.jpg` the verdict is
`asset_cohesion: warn`, the reason being a proposed emitter nobody classified, and the reader profile
says so out loud: *e1 is a bright area nobody has said is a light or not.* The record for that same run
carries no observation about `e1`, because `light._records` writes an emissive item only when the
observer answered a kind, and an unanswered emitter is not an answer of `unknown`. The verdict, the
reading and the record disagree about one run, and no owner compares them.

**The observer is invented at the deepest point in the stack, past a check that cannot see it.**
`light._records` bakes `{"mode": "host", "model": None, "prompt_rev": "v1"}` into the record.
`config.DEFAULTS["observer"]` holds `model: "unknown"` and only `doctor.py` reads it, so the configured
observer reaches nothing that observes. `records._validate_observation` requires `observer.model`, and
the requirement does not fire: it tests `str(obs.get(key, "")).strip()`, and `str(None)` is the string
`None`, which is truthy. An empty string is caught and a null is not, so a null is what the corpus gets.
The enforcer exists, is in the right module, and lets through exactly the value the code produces.

None of the three is a lighting defect. Each is a sentence about a *run* that no unit is responsible for.

## 3. The rule

> **A run answers once.** The verdict, the record and every reading say the same thing about the same
> run, and what a run hands out is valid before it leaves.

This is the third invariant of the run owner, beside *the input is read once* and *subjects are derived
once*. It qualifies as an owner's invariant on the same test §3 of the earlier review used: it is about
what happens **between** a family's answer and the world, so no family can hold it — a family that
validated its own record would be validating its own opinion, and two families would validate two.

It decomposes into three sentences that can each be checked, and together they close §2.

**a. A record is valid before the run returns it.** The run assembles the record, runs
`records.validate` on it, and raises if it fails. The tool that persists a record is then never the
first thing to look at it. This is a trust boundary in the direction the package has not yet guarded:
`_answers` guards what a model sends *in*, and nothing guards what the package hands *out*.

**b. A record exists exactly when the run observed something.** A run that decided nothing returns
`record: null` rather than an empty record, because an append-only corpus is worse off holding a row
that observed nothing. Null rather than an absent key: an omitted field reads as a clean one, which is
the defect this repository has now fixed three times in the reader layer and should not reintroduce in
the record layer.

**c. An axis at `warn` or `fail` is backed by at least one observation in that record.** A `pass` needs
no backing — a pass is the absence of a finding — but a run may not warn a human and leave the corpus
silent, which is precisely `flat.jpg`. The family supplies the observation; the run enforces that one
exists. That split is the same one §9 of the earlier review arrived at for the read-once rule: the rule
belongs to the run and is written as a check over what any family returns, so the second family inherits
it without being named in it.

The two halves interlock, which is how the design is one thing rather than three patches. Once **c**
forces the unclassified emitter into the record, the only runs left with nothing to record are the runs
whose axes are all `unknown` — so **b**'s null is exactly the run that judged nothing, and never a run
that judged something and dropped it. `sprite_rgba.png` is that run today: no emitters, one subject too
faint to place its shaded mass, three axes `unknown`, nothing to say.

## 4. The slice this decides

Filled as `domain-ownership-review` plan records, one per rule, because that is the shape §9 of the
earlier review was written in and the shape this slice will be reviewed against.

```json
[
 {"rule": "run.py — a record is valid before the run returns it",
  "owner": "run", "enforcers": ["run.ledger -> records.validate"], "boundary": "object",
  "authority": "this review, §3a",
  "check": "every fixture, phase two of an unfilled form: record is null or validate returns []"},

 {"rule": "run.py — a record exists exactly when the run observed something",
  "owner": "run", "enforcers": ["run.ledger"], "boundary": "object",
  "authority": "this review, §3b",
  "check": "observations == [] implies record is null, and record is not null implies observations"},

 {"rule": "run.py — an axis at warn or fail is backed by an observation",
  "owner": "run", "enforcers": ["run.ledger"], "boundary": "object",
  "authority": "this review, §3c",
  "check": "for every fixture and both phase-two flows, warn or fail implies a non-empty record"},

 {"rule": "records.py — observer.model is required",
  "owner": "records", "enforcers": ["records._validate_observation"], "boundary": "object",
  "authority": "spec.md §4, the observation.v1 row",
  "check": "a record whose observer.model is null is rejected, as one whose model is empty already is"},

 {"rule": "spec.md §4 — the observer that signs a record is the configured one",
  "owner": "config", "enforcers": ["run.ledger takes it as a parameter"], "boundary": "object",
  "authority": "spec.md §4 and §10",
  "check": "no module under src/asrai other than config names the observer keys"}
]
```

Five records, four files. `records.py` changes first and alone, because it is the root: a required
field that accepts null is why the other four are reachable, and fixing it turns §2's third defect from
a silent corpus row into a failing test. The source scan is the cheap form of the last rule and the same
instrument `dd18c2c` used for the read-once rule; it is a per-package test, so it binds the second
family without mentioning it.

What moves out of `light.py` is the record's envelope — `asset_kind`, `evidence_layer`, `scale`,
`asset_sha256`, `observer` — all of which are facts about the run and are already on the run's envelope
or in config. What stays is every observation item, because what is worth recording about light is what
the lighting family is. `light` gains one item, for the proposed emitter nobody classified, which is the
observation §3c finds missing.

## 5. Designed here, deliberately not built

Three things this settles on paper and leaves out of the slice, each because building it now would be a
guess with no enforcer.

**The axes reduce across families.** With one family the run's axes are the family's axes and any
reduction is the identity function, so a reduction written today is untested code shaped by an imagined
second family. The rule it will need is already written once, inside `light._verdict`, where the axes
reduce over subjects: worst wins, and `unknown` only when nothing decided. The same reduction over
families is the obvious one and should be lifted, not invented, when the second family makes it
observable.

One distinction has to be taken before then, and it is the reason this paragraph exists rather than a
note in the next review: **abstaining is not `unknown`.** `light._verdict` writes
`intentional_contrast: unknown` whenever the mode is not `fake_lighting` — which does not mean the
family tried and could not tell, but that the family does not judge that axis in that mode. With one
family the two are indistinguishable because the run reports whatever the family said. With two, a run
would report `unknown` on an axis one family abstained from and the other never reached, and a reader
cannot tell that from an axis that was genuinely contested. The reduction needs abstention dropped
before it runs, so the family's answer needs a value for it.

**Family order and the withholding rule.** §3 of the earlier review gives these to the run, and
`spec.md` §7 states the gate order they follow. There is one family and it sits outside the eight gates,
so there is nothing to order and no later judgment to withhold. It stays prose until readability lands,
which is the commit that makes it testable.

**A run with no family.** The spec makes the run responsible for an asset whether one family looks at it
or none, and the honest answer for none is the same shape as §3b's: three axes `unknown`, no record, and
a reading that says nobody looked. It is not reachable from either transport, because `ledger` has no
`families` parameter and always calls `light`; it becomes reachable and testable in the same commit that
adds the parameter. Writing it now would be a branch no call can enter.

## 6. What this does not decide

- **Whether the presentation layer moves with the rest.** §5 of the earlier review gives `for_reader`
  and `sentences` to the run owner and its §8 leaves the file question open; both transports import them
  from `light` today. Nothing here depends on the move, and doing it in the same slice would mix a
  contract change with a judgment change.
- **Whether the three axes belong in `observation.v1`.** `spec.md` §7.1's diagram draws `AXES --> RECORD`
  and the schema in §4 has no field for them, so the axes are computed, read aloud and dropped. That is
  either a missing field or a wrong arrow, and it is a contract question for the author under
  `conventions.md` §1 rather than something a slice decides on the way past.
- **Whether `record: null` is the right shape** for a run that observed nothing, against the alternative
  of omitting the key as phase one does. §3b takes null on the silence argument; the author may take
  omission on the symmetry argument.
- **The lighting thresholds**, which remain unverified implementation policy
  (`2026-09-16-authority-and-release-gate.md`).
