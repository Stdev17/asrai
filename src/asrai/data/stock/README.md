# Stock art-direction vocabulary v2

A game art-direction vocabulary any team can use unchanged. It is derived mechanically from
`ad_ta_vocab` v1 with **only the learning layer** removed. **v1 is read-only and is never edited from
this directory.**

## Files

- `vocab.v2.json` — 475 head terms in 22 categories. English is canonical. Every entry points at its v1
  original through `origin.entry_sha256`.
- `vocab.v2.schema.json` — the JSON Schema for the above (Draft 2020-12).
- `instruction.v2.schema.json` — the design-request schema. `status` is
  `proposed|previewed|approved|applied|rejected|superseded`, and `execution` is a real field,
  `{adapter, binding_resolved, authorized, run_ref}`.
- `instruction_examples.v2.json`, `examples/` — 8 serialised examples.
- `surfaces.v1.json` — the appearance surfaces of the lighting pass (`docs/spec.md` §7.1).
- `locales/<code>.json` — eleven languages beside English. **These files are canonical for their
  translations.** How to contribute: `locales/README.md`.
- `validation_report.json`, `manifest.sha256.json`.

## Checking it

```bash
uv run python tools/validate_stock.py    # also runs inside pytest
uv run python tools/review_locales.py    # flags what a human still has to confirm
```

The derivation script that produced this corpus from v1 (`trim_vocab.py`) and its scope notes ran once,
in the origin repository, and are recorded by digest in `manifest.sha256.json` rather than shipped here.
They are not re-run: this corpus is now edited directly, and `validate_stock.py` is what holds it to its
invariants. A regeneration from v1 would overwrite translations, which is the thing the original script
was written to avoid.

## What was removed

492 → **475**. Only the learning layer left.

- The `methods` category, **17 entries** — observation, copying, active recall, thumbnailing, prop
  studies and other practice exercises. They describe no property of an asset. The remaining 3 stayed
  because they are **production review activities**, not exercises: `screenshot_audit` (checking a
  finished frame axis by axis), `markup` (marking problem areas and intent over the original), and
  `feedback` (separating observation from judgment and settling on one next change). The reasons are in
  `tools/stock_scope_notes.json` in the origin repository and travel with each entry as `scope_note`.
  With 3 entries left, the category label also changed from v1's "Observation, copying, variation,
  recall and review" to `Review, markup and feedback`.
- The `curriculum_weeks` field — deleted from every entry.
- v1's citation apparatus — `sources`, `provenance.evidence`, `verified_doc_ids`, `tools`,
  `coverage_audit`, `technical_verification_sources`, `extraction_contract`. These are quotations,
  hashes and offsets from Korean-language teaching interviews, not domain vocabulary. When evidence is
  needed, look the entry up in v1 through `origin.entry_sha256`.
- `operationalization.binding_state`, `is_executable_command`, `normalization_note`.

**The domain vocabulary is kept whole, 2-D and 3-D alike.** All 22 categories, `material`, `geometry`,
`uv_texture`, `rig_animation`, `shader` and `render` included. The vocabulary being wider than any one
tool adapter's reach is deliberate.

`provenance.term_basis`, `description_basis` and `operationalization_basis` are kept. Note that the
source `attested_in_in_scope_source` points at is a Korean teaching-context conversation, so read it as
**a record of usage**, not as an industry-standard warrant.

The 2 `local_meta` entries stayed — they are not a learning category — but their v1 definitions say "in
this discussion" and "in this request", which point at the corpus itself. They are marked
`scope: uncertain`.

## Where this differs from playbook §3 Phase 0

1. **How much was deleted.** The playbook directed deleting 8 categories (6 for 3-D, plus `methods` and
   `local_meta`) and applying a 2-D surface filter, with an entry count of 300±15 as the acceptance
   criterion. On the author's instruction this became **delete the learning context only**, which left
   the 2-D surface filter (§3-3) without a rationale, so it was dropped. The result is 475 entries. The
   scope table in report §7.3 is superseded by this decision.
2. **The acceptance criterion.** A derivation invariant replaces the entry count: `stock = source −
   the deleted learning entries`, and every survivor of a learning category carries a `scope_note` and
   matches the declared re-inclusion list exactly.
3. **i18n.** Eleven `locales/<code>.json` files instead of an inline `i18n.ko.label`. Inlining twelve
   languages would push `vocab.v2.json` past a megabyte. `aliases[{text, lang}]` stays inline as
   specified, because ingest must match a comment in any language without loading a locale file.
4. **`quantification.note`.** Owned by `quantification_profiles[profile_id].note` rather than copied
   onto every entry (v1 had already de-duplicated it).
5. **`description`.** Not newly translated: v1 was already in English, and these came from
   `ad_ta_vocab/locales/en.json`. Every entry is `translated_by: llm`.
6. **`example` added to `magnitude_basis`.** A number from an example is neither a precedent nor a
   measurement, and leaving it as `none` made it indistinguishable from "no quantity at all".
7. **Report §7.3's "68 manipulation terms" is wrong.** Counted by the definition the same document
   gives (`direct_with_context` or `measurable_with_context`), that set of 291 contains 104. The 51
   judgment terms were correct. Following the reproducible definition, across all 475 entries it is 70
   judgment and 155 manipulation.

The 8 numeric tests and 9 rejection tests pass exactly as they did against v1.

## Limits

- 475 entries is the v1 corpus minus practice exercises. That is not evidence it is the industry's
  standard set.
- Descriptions and guidance are editorial prose. The 70 judgment terms and 155 manipulation terms are
  marked `translation_review: needed` and have not been confirmed by a human.
- Translations are LLM-drafted counterparts. Head-term collisions are resolved and anything needing
  confirmation carries a `review` flag. See `locales/README.md`.
- `quantification_profiles` only says what must be fixed for a number to mean anything. It gives no
  recommended values, and no threshold anywhere here is normative.
- A perceptual goal is not a numeric property. A proxy measures the proxy, never the whole goal.
