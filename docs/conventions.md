# Conventions

How code in this repository is written. [`runbook.md`](runbook.md) §1 owns the judgment hierarchy.
Within that hierarchy, [spec.md](spec.md) defines what the tools promise and what records mean, while
this document governs code and naming; neither filename can override sourced human decisions or
human-maintained policy.

Two audiences, and they want opposite things:

- **A model reads the surface.** MCP tool names and parameters, record field names, term ids, enum
  members, error strings. It sees a name, a type and one description line, with no prior turn. §1.
- **A person reads the source.** Module bodies, comments, commits. It sees the whole file and can
  scroll. §2.

Terseness is a virtue in the second and a liability in the first. `a` and `b` are good parameter names
in `pairwise`; `a` would be a terrible field name in a record a model has to fill.

---

## 0. Owner boundaries

Before changing a responsibility boundary, draw its proposed dependencies in the README of the realm
that owns it — for the package core, [`src/asrai/README.md`](../src/asrai/README.md) — then verify the
finished graph against code and data flow. A change that adds, removes or moves a realm is drawn in the
[realm ledger](architecture.md) instead, one level up.
Each node names an invariant owner; each edge names only the signatures or data contracts crossing
that boundary. An owner may enforce deterministic policy without mutable state. Helpers, DTOs,
modules and MCP tools are not automatically owners; commit `Owners:` path buckets are a different
classification. Grouping independent invariants under a facade does not reduce the owner count.

**Single-skill scope.** At **10 or more responsibility owners**, pause the proposed expansion and
review feature creep with the responsible human, even if the diagram is readable. asrai should do
one job well. Name the new invariant and explain whether it belongs to that job or to a separate tool.
Community demand may justify a broader system, but only an explicit human scope decision can adopt it.

**Diagram fit, in the feature realm.** More than **10 nodes**, or crowding at an ordinary repository
reading width, is a signal to reconsider a subsystem boundary. Do not hide dependencies, shrink text or
split a drawing into pages to make it pass. Split along independent invariants, never to satisfy a
count. For this single-skill product, first revisit scope; introducing another subsystem is not
automatic permission to keep growing. A readable graph below the count is evidence of legibility, not
proof of good scope.

The count binds the feature realm's own graph and nothing else. A realm is not a subsystem: the ledger
one level up draws boundaries that own a class of invariant, and the data realm's interior is a
vocabulary whose size is the point rather than a symptom. A threshold that fires on those would be
measuring the wrong thing, and the general rule the `repository-operating` skill carries is
per-level
fan-out, which stays true at any repository's scale precisely because it is not one number. This is
that rule instantiated for the one realm here whose growth is a scope question.

The `repository-operating` skill carries the general
shape these two thresholds are an instance of, and separates the legibility question from the scope one.
The [adaptation record](review/2026-09-16-owner-boundaries.md) identifies the source and the
Unity-specific policies not adopted here.

## 1. Names a model reads

**The test.** A stateless model sees only `name`, `type` and `description`. Can it produce a correct
value on the first try? If it needs a prior turn, the repo's tribal context, or a look at the source,
the name has failed. This is the primary design criterion for anything crossing the MCP or record
boundary — not a polish pass afterwards.

**Four ways a name fails.** Check each before adding a field. They are failure modes, not a score:
counting a name out of 40 invents precision and licenses churn.

| failure | what it looks like | asrai |
|---|---|---|
| **Ambiguous alone** | the name needs the description to mean anything: `status`, `type`, `value`, `data`, an abbreviation | `magnitude_basis` passes: the name alone says it holds *where a number came from* |
| **Wrong prior** | the name triggers a pretrained association that pulls away from the real value | `level` reads as an ordinal magnitude; it actually holds evidence strength (`asserted`/`estimated`/`unknown`) |
| **Thin description** | missing range or enum, missing unit, missing provenance when it matters downstream, missing example | a numeric field without its unit is never finished |
| **Blurs with a sibling** | two fields in reach of each other read alike, or one axis gets two names | `vocab_search(full=)` against `vocab_get(compact=)`: the same axis, opposite poles, two words |

**Put the unit in the name.** `target_width` over `width`; `timeout_seconds` over `timeout`. A number
whose unit lives only in a description gets filled from the wrong one.

**Enum members carry their own weight.** A model sees `L1` with no table. Either the member is
self-describing or the description enumerates every member and what it means. No third option.

**Say which word and why.** English near-synonyms are not interchangeable to a model that was trained
on how the field actually uses them. When a name is not obvious, leave the choice in a comment or the
commit body: *generated* implies a model produced it, *derived* implies a deterministic transform,
*computed* implies arithmetic. Picking the wrong one teaches the model the wrong provenance. One line
is enough; this is for the next author as much as the model.

**Do not churn a working name.** A name a model already fills correctly has value *because* it is
stable. Rename only to fix a failure above, never for a nicer word. Renaming anything on the MCP tool
surface or in a record schema is a contract change: it needs a spec.md amendment in the same commit,
and old records stay readable.

**Redundant or overlapping fields are a structural problem, not a naming one.** Two fields that mean
the same thing do not get better names; one of them gets deleted. Raise it separately.

**Stable names retain meaning.** A changed input, return shape, fallback or guarantee is a contract
change even when the identifier stays the same. Make it visible in the spec and migration or versioned
surface; do not hide changed meaning under an old name. Old records remain readable.

## 1a. Canonical examples

Append-only. Every name this repository weighed against §1 lands here with its verdict, so the next
decision argues with a precedent instead of re-deriving one. Entries are never edited away; a reversal
is a new row.

**A row names the surface, not only the name.** One word can name a core function, an MCP tool and a
CLI verb at once, and a decision taken on one of them does not bind the others: `light.ledger()` takes
no profile while `light_ledger` and `light-ledger` both do, and that is the design rather than a drift.
Most rows already carry the surface in the call form they are written in — `vocab_get(lookup=)`,
`measure(path=)`, `doctor(write_lock=)`. Prose inside a row owes the same.

**Mirrors — imitate these.**

| name | why it works |
|---|---|
| `magnitude_basis ∈ none\|example\|precedent\|measurement\|human\|llm` | the name states the dimension, the members state the position on it. Fillable from the name alone, and the one field the whole safety story rests on |
| `target_width` | the unit is in the name, so it cannot be filled in the wrong one |
| `pairwise.a`, `pairwise.b` | terse and still unambiguous, because `verdict ∈ prefer_a\|prefer_b` disambiguates them completely. Terseness is safe exactly this far |
| `perceptual_review_required` | a boolean whose name reads as the question it answers |

**Fixed.**

| was | became | failure mode | why |
|---|---|---|---|
| `vocab_get(compact=False)` beside `vocab_search(full=False)` | `full` on both | blurs with a sibling | one axis, one word. The defaults still differ — search returns many rows, get returns one — and a default belongs in the description, not in a second name |
| `asrai vocab get --compact` | `--full / --no-full` | blurs with a sibling | the row above and this flag shipped in the same commit (`91a4bc7`): the decision was written down and applied to the MCP signature, and the CLI beside it kept the word the row rejects. The blur therefore survived on the surface a human types, with the README use block printing it and `§1a` reading as though nothing were left. A naming decision is not landed until every surface carrying the name is changed — here that is the CLI, the README and its three translations, and `tools/check_wheel.py`, which runs the installed CLI from outside the checkout and was the only check pinning the old spelling |
| `vocab_get(id=)` | `vocab_get(lookup=)` | ambiguous alone | `id` is the most overloaded word in programming and shadows a builtin. It also held three different things, so no name could be honest about it; `lookup` at least admits it is a selector, and the description now enumerates all three forms with literal examples. The overload itself is a structural note below |
| `doctor(lock=False)` | `doctor(write_lock=False)` | wrong prior | `lock` reads as a state query; the parameter *writes a file*. A model asked to check the environment could plausibly send `lock=true` and silently overwrite `asrai.lock.json` |
| `scale ∈ "1.0"\|"target"\|"64"` | `native\|target\|thumbnail` | wrong prior | string members that look numeric. `scale=64` and `scale=1.0` — the two most natural things to send — were both rejected. These are also the keys of `measure`'s `scales` map, so the output became self-describing in the same change. Taken while no record existed and before fixtures froze the keys; the same fix a month later is a migration |
| `subjects.<surface>: {no: [], unknown: []}` issued filled | issued `null`, a dict once answered | wrong prior | the only field of the form not issued null, so a surface nobody looked at was indistinguishable from one the observer answered with nothing to except, and the verdict fell through to `yes`. A form handed back as issued — the path [spec §7.1](spec.md#71-surface-pass-built) tells the first reviewer to take — read `yes` on `specular`, `light_color`, `ambient`, `rim` and `albedo`, against that section's own rule that `observer` defaults to `unknown`. An empty list still means answered with no exception; `null` means nobody looked. No version bump: no answer sheet is stored anywhere, and a filled sheet keeps exactly the meaning it had |

**Left alone — stability beats a nicer word.**

| name | the objection | why it stays |
|---|---|---|
| `measure(path=)` | does not say *image* | works on the first try; the description carries the formats |
| `level ∈ asserted\|estimated\|unknown` | "level" leans ordinal | the values genuinely are ordered by evidence strength, so the prior is not wrong |
| `record(record=)` | tool and parameter share a word | nothing else reads better, and the tool takes exactly one thing |

**Chosen at birth — alternatives rejected.**

| name | rejected | why |
|---|---|---|
| `light_ledger` | `decompose`, `surfaces` (as a tool) | `decompose` is ambiguous alone; `surfaces` collides with the vocabulary's `candidate_surfaces`, where a surface is the place a parameter lives. A ledger of lights says what the rows are |
| `bright_side.vector` beside `contour_fit.vector` | one merged `light_direction` | two estimates of one quantity stay under the method that produced them, so a fit's number is never cited as if it were the bright side's |
| `global.alignment` | `coherence` | blurs with the `asset_cohesion` axis |
| `mirror` (boolean) | `flip` | `flip` reads as a vertical flip to a game artist; a boolean at the tool surface per section 2 |
| `emitters[].kind: proposed` | `confirmed: false` | the value names what the row is, not what it lacks; `confirmed` is what an observation later says |
| `key_fit` with `median_deg`, `within_tolerance` | `global.alignment` (mean resultant length) | a resultant length assumes one directional light and hides its unit; residual degrees per hypothesis say which light explains the frame and how badly |
| `irradiance_proxy` | `irradiance`, `weight` | luminance × area over squared distance in pixels is not an irradiance; the suffix keeps a model from citing it as one |
| `depth` as a layer index | `z`, `distance` | for stacked 2-D art depth is an ordering (Illustrator's Depth, Maruani et al. 2025); a distance would invite invented numbers |
| `form` / `answers` | `questions` as the only interface | a typed sheet whose null fields are the whole ask; prose questions remain, derived from it |
| `emitters[].spill` | `glow`, `bloom`, `halo` | those name a render effect the artist applied; this is a measurement of the neighbourhood, which a flat cel light can fail while still being a light |
| `emitters[].receivers` | `used_by`, `lit_subjects` | a count, and the subjects that point at it are already in `agreement`; the plural noun says what the number counts |
| `subjects[].shadow` with `opposition_deg` | `cast_shadow_direction`, `dark_side` | the field is named for the mass it found, and the number for the only thing measured about it: the angle by which it fails to oppose the lit side. `dark_side` would pair with `bright_side` and imply the two were measured the same way, which is what `opposition_deg` compares |
| `SHADED_STRENGTH` | `BAKED_STRENGTH` | one measured constant answers two questions, so the name says what it measures (a subject carries directional shading), not the first use it was written for |
| `verdict.emitters[].verdict: lights_nothing` | `unused`, `orphan`, `fake` | `unused` is an engine word, `orphan` a graph word, `fake` a judgement the style_exemption may overturn; what is measured is that nothing takes its light |
| `style.mode ∈ physical/fake_lighting/engine_lit` | `fake_lighting: bool` | three expectations, not two; a boolean could not say "the engine lights this" |
| `answers.run_sha256` | `answers.image_sha256`, `answers.path`, a form id, nothing at all | every answer is addressed to an id and the ids belong to the run that assigned them, so the stamp is over the file's bytes, the subjects and the mirror flag together. The image sha was the first name and it under-bound: the same bytes measured with other boxes, or mirrored, accepted a sheet answered for other blobs. A path would match after a re-export, an id would need a store. The field is optional so a hand-written sheet still runs |
| `observation.axes` | `axis_scores`, a summed `score`, an `axis` on each observation item | spec.md section 7 names the axes and says they are never summed, so the field is each of them on its own with no total. It sits on the record and not on an item because the judgment is the run's and not one observation's, and `instruction.v2` already spends the singular `axis` on where a change is placed. Optional, because an observation written by hand has no run behind it to have judged one — but all three or none, since a subset lets a reader take silence for a pass. The same values appear under `verdict`: that copy is the live one, this is the one that outlives the reply, and a test holds them equal |
| `SPILL_MIN_Y` (both rings clear the bottom 3% of the 8-bit range) | a standard-error gate on the difference, a relative gain | the flip that motivated it was six standard errors of a real pixel difference, so no statistic rejects it; a ratio in near-black divides by the quantisation step. What is actually wrong is that both rings are crushed, which is what the constant says, and the magnitude comes from the file format rather than from taste |
| `subjects[].mask` | `subjects[].alpha`, `segment: true`, a `material_id` per box | the value is a file the artist already exports, so the name is the thing rather than the flag; deriving it was rejected outright, since a rock and the sand under one warm light share their chroma and the ledger does not segment |
| `emitter_floor: {value, basis}` reported | a `color_space` input field | the caller who hands over a PNG usually cannot answer what encodes it, and a wrong answer is worse than none. Every rank-based measurement in the pass is already invariant to a transfer function (18 emitters across three references held their sign under gamma 2.2 and 1/2.2); the one constant that is not is reported instead of asked |
| `source.lossy` reported | a JPEG deringing pass | undoing ringing needs the encoder's tables, and guessing them is an invented magnitude at the trust boundary. Detect and disclose; the answer to a lossy source is the original file |
| `emitters[].kind: unknown` as a hold; `verdict: unclassified` beside `unreadable` | treating `unknown` as a rejection, as `paint` is | `paint` is a judgment — the blob does not emit — so it may void its pairs. `unknown` is the absence of one, and rejecting on it made the honest answer the only one that cleared a frame: on one decoy scene, naming e1 a lamp read `fail` while saying "I cannot tell" read `pass` and dropped the row entirely. A hold keeps its row and holds the axis. The sibling `unknown` on `verdict.emitters[].verdict` was renamed `unreadable` in the same change, because two near-synonyms on one enum is the fourth failure mode of §1 |
| `sentences(findings, profile)` | `explain`, `summarise`, `report`; a `profile=` parameter on `light.ledger()` | the name says what comes back, and the signature says what may happen: it takes findings somebody else decided and returns strings, so the reader it serves can never be the reason a verdict reads the way it does. It took a whole finished result until the presentation layer moved to the run owner ([the 2026-09-20 review](review/2026-09-20-one-run-one-voice.md)); taking findings instead is what keeps the renderer from knowing which family spoke. The rejected parameter is the one that matters — threading an audience into `light.ledger()` is the cheap way to add a profile and the one way to let expression outrank judgment, which [the 2026-09-17 review](review/2026-09-17-profile-alignment.md) settles the other way. `explain` and `report` both promise a document; this returns one line per finding |
| `for_reader(result, profile)` — retired | `rendered`, `as_read`, `with_sentences` | `rendered` was rejected on a wrong prior: in a tool about game art it reads as producing pixels, which is a stated non-goal, and a function that returns prose must not borrow that word. The chosen name said the dimension — which reader — and it existed so `None` meant one thing in both transports: no profile is the default, and a result is complete before any is applied. `run.ledger` became that one place when the presentation layer moved to it, leaving the wrapper one caller and one line, so it was deleted ([the 2026-09-20 review](review/2026-09-20-one-run-one-voice.md)). The row stays: the rejected names are still rejected, and a later `rendered` would be the same wrong prior |
| `finding: {say, terms, settled, basis, evidence}` | one rendered list per profile; a `severity` or `level`; an `axis` on each finding | what a family hands the run's output stage. Three pre-rendered lists were the obvious alternative and the wrong one: three renderings is three chances to disagree about one run, and a family cannot make them anyway — the overlay that widens a reader's vocabulary is a team's corpus, which nothing below the transport may know about. The fields beside `say` are exactly what a reader profile may do to a line, and `settled` is named after the axis that reads it, so the one thing a profile may withhold is the one thing the field says. `severity` was rejected because the three axes already carry the judgment and a per-finding scale nobody reduces is a second one; `axis` because a finding is evidence for an axis rather than a value of it |
| `profiles.v1.json` axes `settled`/`contested` | one `emphasis ∈ all|contested_only` | two names because they answer different questions — what to suppress and what to enrich — and today only one profile differs on either, which is the argument for merging them. The file says so in `open` rather than hiding the co-variance; a profile that suppresses without enriching is the row that decides it. The rejected merge would also have bundled two meanings under one word, which is §1's second failure mode |
| `asset_cohesion: warn` for an unchecked light | leaving it `pass`, or `unknown` | `pass` was the axis reading evidence it never had, and `unknown` would throw away the shaded masses that were measured. `warn` is the axis saying which half it could not see |
| `run.open_run` / `light.pass_(ctx)` | `run.ledger` for both; `light.ledger(ctx)`; `judge`; `findings` | the run owns the entry point, so `ledger` is its word and the family needed another. Reusing it for both would have put one name on two surfaces, which is the ambiguity §1a's preamble forbids and the row above it records. `judge` overclaims — the pass measures and asks; an observer judges. `findings` undersells a return that also carries a form, questions and an overlay. `pass_` is what [spec.md §7.1](spec.md#71-surface-pass-built) already calls it, and the trailing underscore is the keyword collision, not a second meaning. Taking `ctx` rather than a path is the contract: a family that cannot open a file cannot disagree with another about what it opened |

**Structural notes — not naming problems, and not fixable by renaming.**

- `vocab_get` runs three operations through one string parameter. It began as a way to stay under an
  eight-tool cap; the cap is now a byte budget (spec.md §6) and the overload survives on it, because splitting
  it into `vocab_get`, `vocab_category` and `vocab_categories` measured 462 more bytes of schema — about a
  hundred tokens on every turn — for nothing the one parameter cannot say (2026-09-14). The name is honest,
  but a model still cannot discover `categories` from the type. Revisit only if the budget is raised for it.
- `record` and `lint` take `object` with no declared properties, so the schema offers a model no help at
  all; the shape lives only in spec.md §4 and `SKILL.md`.
- `mode` means three unrelated things across the surface: `observer.mode`, `quantification.mode`, and
  `[observer] mode` in `asrai.toml`.

## 2. Code a person reads

**Words.** Comments, commit messages and replies use as few words as possible. No superlatives, no
praise, no restating the code in prose. If a paragraph defends a simplification, delete the paragraph.

**Constants.** Extract a recurring or meaningful value into a named constant; keep a self-explanatory
one-off inline. A value that comes from a spec or a measurement is always a constant, with the
derivation beside it:

```python
# stats() peaks near 320 bytes per pixel (float64 sRGB->linear over the whole plane), so a pixel
# count is a memory budget: 12 Mpx is roughly 4 GB. A 4K capture (8.3 Mpx) fits; 8K does not.
MAX_PIXELS = 12_000_000
```

A magic number with no note is a number nobody can ever change, because nobody knows what it protects.

The unit is the **formula, not its coefficients**. Naming each number in a published transfer function
hides the shape a reader would otherwise recognise on sight, so name the standard once in a comment and
leave the coefficients inline:

```python
# sRGB electro-optical transfer function (IEC 61966-2-1). The coefficients are the standard's
# own and stay inline: naming each one hides the formula a reader would otherwise recognise.
lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
```

A threshold *this repository chose* is the opposite case and always gets a name — and so do its
siblings. `CHROMA_MIN_S` sitting beside a bare `0.05` on the same line is the inconsistency to avoid.

**Shape.** Early return and `continue` over nesting. Blank lines between logical blocks. Function
names short — under 30 characters, and usually far under. Test functions are exempt: a test name is
the failure report, and `test_lint_implementations_agree_on_rejections` is worth its 45 characters.

**Comments say what the block does and why, never how.** The code is the how. Prefer a concrete
example or an ASCII sketch to an adjective. Comments that earn their line in this repo look like:

```python
if img.mode in SIXTEEN_BIT:  # convert() would clip 16-bit grey to white; rescale explicitly
```

**Booleans are allowed at the tool surface.** A flag parameter is usually worse than an enum in library
code, but MCP parameters are JSON Schema: a `boolean` is the cheapest thing for a model to fill
correctly and an enum of two strings is not clearer. Keep booleans on tool parameters; prefer an enum
for an internal parameter with more than two states, present or future.

**Private by default.** A module's public names are the ones `cli.py`, `server.py` or another module
calls; everything else is `_`-prefixed. Widening `_helper` to `helper` is a design change — it means a
second caller now exists — so say so in the commit body rather than doing it in passing.

**Levels of abstraction, no punching through.** `cli.py` and `server.py` are transports. They parse
arguments, call one core function, and serialize the result; they hold no rules. Every rule lives in
its [core owner](architecture.md), so the two transports cannot disagree (spec.md §2, invariant
9). A transport that reaches past the core into Pillow or a JSON file is a bug even when it works.

**Do not touch unrelated code.** No drive-by comments on blocks you did not write or change. The
smallest diff that fixes the thing, and nothing else in the same commit.

**Work stops at its write-set boundary.** Name the invariant and allowed files before delegating.
Disjoint intentions do not prevent edits to the same file from colliding. If the change needs a file
outside that boundary, report the file and reason; never substitute a copied constant, hidden state,
extra public member or changed return contract. A deviation needs sourced human authority and the
commit trailer below. A task ends at reproducible evidence, not an amount of code.

## 3. Tests

**One package command.** `uv run pytest` checks the code *and* the shipped corpus — the vocabulary lives
inside the wheel, so its validators are tests, not a README step. Repository and distribution checks
also gate landing; the [runbook](runbook.md) owns that procedure.

**A bug fix starts with the failing test.** Write it, watch it fail for the reason you expect, then fix
it. A test written after the fix only proves the code does what it currently does.

> Exception, learned the hard way: when the failure mode is resource exhaustion, bound it first. A test
> that reproduces an unbounded allocation reproduces it on your machine. Land the guard, then let the
> test prove the guard fires.

**One runnable check per non-trivial rule.** A branch, a parser, a numeric rule, a trust boundary. Not
per function. A one-line passthrough needs no test.

**Prefer a property over a fixture list** when the fixture list would have to be maintained by hand.
`test_lint_implementations_agree_on_rejections` drops one context key at a time from every shipped
example: it cannot go stale as examples are added, and a hand-written list of nine cases would.

**Test what a model will actually send.** The input at an MCP boundary is model-generated, so
wrong-typed and out-of-range values are the expected case, not the exotic one.

## 4. The package

`uv` manages everything. `uv sync` to set up, `uv run <cmd>` to run. No bare `pip`, no bare `python`,
no activating the venv by hand.

| | |
|---|---|
| add a runtime dependency | `uv add "pillow>=12,<13"` — with an upper bound; never hand-edit `[project.dependencies]` |
| add a dev tool | `uv add --dev pytest` — lands in `[dependency-groups] dev`, stays out of the wheel |
| `uv.lock` | committed, and the reproducibility story for Python packages (spec.md §11) |
| `requires-python` | `>=3.11`. The floor is a promise: no syntax or stdlib newer than 3.11, whatever the dev machine runs |
| end users | `uvx asrai` — the package must work with no install step and no repo checkout |

Data files ship inside the wheel under `src/asrai/data/`. Anything the package reads at runtime goes
there and is addressed relative to `__file__`, never relative to the working directory.

## 5. Commits

The responsible human adopted this format for new work. It replaces the former untyped, capitalized
subject convention; historical commits are not rewritten to adopt it.

Subject: `type(scope): why-subject`, no trailing period, 50 characters (72 hard). The scope is an
owner below. Blank line. Body wrapped at 72, explaining **why**; the diff already shows how.
Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `build`, `ci`, `revert`, `style`.

```
fix(runtime): prevent measurement memory exhaustion

target_width reaches measure() straight from a model, and stats() peaks
near 320 bytes per pixel, so 4x4 upscaled to 50000 wide asked for 800 GB
and the OOM killer took the process. Refuse above 12 Mpx on both the
decoded source and the target rescale; a 4K capture still fits.

Owners: runtime, tests
Fixes: <commit-that-introduced-the-defect>
Values: <name> <old>-><new>
Signed-off-by: <name> <email>
```

The placeholders above must be replaced by actual evidence. Trailers form the final paragraph.

| trailer | obligation |
|---|---|
| `Owners: a, b` | every owner touched, exactly; a rename touches both the old and new owners |
| `Fixes: <sha>` | required on `fix`; identify the introducing commit, not an arbitrary nearby commit. The checker verifies that the commit exists and touches an affected file; review establishes causality |
| `Values: name old->new; ...` | every changed number, with its stable name and actual old/new values; qualify an ambiguous name as `path:name` |
| `Deviation: what — why — authority` | an exception needs an existing, sourced human approval. Writing a trailer never grants authority |
| `Source: <repo> <rev>` | a copy needs its source repository and commit SHA; the body names source paths and any adaptation. Review verifies provenance and copied content |
| `Signed-off-by: Name <email>` | the existing DCO policy in `CONTRIBUTING.md` |

| owner | paths, with the more specific match taking precedence |
|---|---|
| `stock` | `src/asrai/data/stock/` |
| `skill` | `src/asrai/data/skill/` |
| `runtime` | the rest of `src/asrai/` |
| `tests` | `tests/` |
| `ci` | `.github/` |
| `process` | `tools/`, `.claude/`, `.agents/`, `AGENTS.md`, `CLAUDE.md`, `.mcp.json`, `.gitignore` |
| `docs` | `docs/`, root `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` |
| `package` | `pyproject.toml`, `uv.lock`, `LICENSE` |
| `root` | anything not mapped above; review whether a newly introduced area needs an owner |

**Machine evidence has a boundary.** [`commit_check.py`](../tools/commit_check.py) enforces the
closed conditions and prints the schema on failure. It compares module-level Python literal
assignments and numeric leaves in JSON, JSONL and TOML, using decoded values and dotted/indexed
field names. Added/deleted fields, local assignments, computed expressions, prose, versions and
other formats still require the author and reviewer to supply the appropriate `Values` evidence.
This coverage limit does not exempt those changes from the rule. A nearby occurrence of an old
number in a test is not evidence that the test pins that parameter; run the tests and review the
actual dependency. The checker validates `Source` syntax; it cannot infer external copying or
human approval from Git. A passing hook is not a provenance or authority verdict.

**A generated lockfile is outside `Values`.** The numbers in `uv.lock` are the resolver's — wheel
sizes, and the indices that shift when any dependency moves — rather than magnitudes an author
chose, and adding one development tool rewrites them wholesale. The evidence a lockfile has is
`uv sync --locked` in the gate, which checks the whole file against `pyproject.toml` instead of one
leaf at a time. Decided on 2026-09-18, when the first lockfile change under this policy arrived;
the exemption is the tuple `GENERATED` in [`commit_check.py`](../tools/commit_check.py) and covers
that file alone, so a second generated file is a decision and not an inference.

Install and exercise the hooks as described in [runbook.md §7](runbook.md#7-landing-a-change).
`commit-msg` checks message structure. `reference-transaction` checks the actual new commit objects
before local branch or detached-HEAD updates, including `amend`. Existing reachable history,
remote-tracking refs and tags are left to the explicit range review. A merge is compared with its
first parent. Local hooks are contributor feedback; reviewers still check the exact PR range.

---

## Appendix: reviewing a schema against §1

For a systematic pass over a schema, rather than a single new field. Give a model the schema and this:

> You are reviewing a JSON Schema whose consumer is a stateless LLM, not a human developer. For every
> field, judge one thing: seeing only the field name, type and description, with no prior conversation,
> can the model produce a correct value on the first try?
>
> Report only fields that fail, and name which of the four failure modes applies — ambiguous alone,
> wrong prior, thin description, blurs with a sibling. For each, give three replacement
> `{name, description}` pairs that differ in **strategy**, not wording: (1) terse name carrying a strong
> description, (2) self-explanatory compound name needing almost no description, (3) the convention
> already visible elsewhere in this schema, even if verbose. Gloss why each word beats its near
> synonyms. Recommend one, tied to what this schema's consumer actually does.
>
> Do not propose a rename that changes a field's type or meaning — that is a redesign, not a naming
> fix. List redundant or overlapping fields separately as structural notes; they are not naming
> problems. Leave working names alone.
