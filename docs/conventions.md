# Conventions

How code in this repository is written. The **contract** — what the tools promise, what the records
mean — is [spec.md](spec.md); when the two disagree, spec.md wins and this file is amended.

Two audiences, and they want opposite things:

- **A model reads the surface.** MCP tool names and parameters, record field names, term ids, enum
  members, error strings. It sees a name, a type and one description line, with no prior turn. §1.
- **A person reads the source.** Module bodies, comments, commits. It sees the whole file and can
  scroll. §2.

Terseness is a virtue in the second and a liability in the first. `a` and `b` are good parameter names
in `pairwise`; `a` would be a terrible field name in a record a model has to fill.

---

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

## 1a. Canonical examples

Append-only. Every name this repository weighed against §1 lands here with its verdict, so the next
decision argues with a precedent instead of re-deriving one. Entries are never edited away; a reversal
is a new row.

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
| `vocab_get(id=)` | `vocab_get(lookup=)` | ambiguous alone | `id` is the most overloaded word in programming and shadows a builtin. It also held three different things, so no name could be honest about it; `lookup` at least admits it is a selector, and the description now enumerates all three forms with literal examples. The overload itself is a structural note below |
| `doctor(lock=False)` | `doctor(write_lock=False)` | wrong prior | `lock` reads as a state query; the parameter *writes a file*. A model asked to check the environment could plausibly send `lock=true` and silently overwrite `asrai.lock.json` |
| `scale ∈ "1.0"\|"target"\|"64"` | `native\|target\|thumbnail` | wrong prior | string members that look numeric. `scale=64` and `scale=1.0` — the two most natural things to send — were both rejected. These are also the keys of `measure`'s `scales` map, so the output became self-describing in the same change. Taken while no record existed and before fixtures froze the keys; the same fix a month later is a migration |

**Left alone — stability beats a nicer word.**

| name | the objection | why it stays |
|---|---|---|
| `measure(path=)` | does not say *image* | works on the first try; the description carries the formats |
| `level ∈ asserted\|estimated\|unknown` | "level" leans ordinal | the values genuinely are ordered by evidence strength, so the prior is not wrong |
| `record(record=)` | tool and parameter share a word | nothing else reads better, and the tool takes exactly one thing |

**Structural notes — not naming problems, and not fixable by renaming.**

- `vocab_get` runs three operations through one string parameter because spec.md §6 caps the surface at
  eight tools and two slots are reserved for `retrieve` and `preview`. The name is honest now, but a
  model still cannot discover `categories` from the type. Revisit when those slots are spent.
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
`vocab`, `measure`, `records` or `doctor`, so the two transports cannot disagree (spec.md §2, invariant
9). A transport that reaches past the core into Pillow or a JSON file is a bug even when it works.

**Do not touch unrelated code.** No drive-by comments on blocks you did not write or change. The
smallest diff that fixes the thing, and nothing else in the same commit.

## 3. Tests

**One command.** `uv run pytest` checks the code *and* the shipped corpus — the vocabulary lives inside
the wheel, so its validators are tests, not a README step. Nothing that gates a release lives outside
that command.

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

Subject: imperative, capitalized, no trailing period, 50 characters (72 hard). It must complete
*"If applied, this commit will ___"*. Blank line. Body wrapped at 72, explaining **what and why**;
the diff already shows how.

```
Bound the pixel count measure will accept

target_width reaches measure() straight from a model, and stats() peaks
near 320 bytes per pixel, so 4x4 upscaled to 50000 wide asked for 800 GB
and the OOM killer took the process. Refuse above 12 Mpx on both the
decoded source and the target rescale; a 4K capture still fits.
```

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
