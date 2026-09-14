# Contributing a vocabulary translation

Each `<code>.json` gives one language's head term and spoken description for the 475 entries of
`vocab.v2.json`. **The English bundle and the spec are not translated** — units, operations,
quantification profiles and guidance exist only in `vocab.v2.json`, in English.

Eleven languages ship: `de`, `es`, `fr`, `it`, `ja`, `ko`, `ms`, `pt`, `th`, `zh-Hans`, `zh-Hant`.
`en` is the base bundle itself, not an overlay.

## File shape

```jsonc
{
  "locale": "de",
  "base": "vocab.v2.json",
  "terms": {
    "shape.silhouette": {
      "label": "Silhouette",            // this language's head term. Required
      "aliases": ["Umriss"],            // only where a parallel spelling is genuinely used. Optional
      "description": "…",               // one sentence, for speaking aloud, not a spec. Required
      "review": "confirm_loanword"      // left by the automatic check; see below
    }
  }
}
```

## `review` values

`tools/review_locales.py` recomputes these on every run. Fix the entry and the flag disappears on the
next one.

| value | what it means | what to do |
|---|---|---|
| `confirm_loanword` | the head term is letter-for-letter the English one | if the industry in that language really does use the English word, leave it; otherwise translate it |
| `confirm_script` | a non-Latin-script language whose head term contains none of that script | same as above. `PBR`, `UV` and `LOD` staying as they are is normal |
| `missing` | the head term or the description is empty | fill it in |

No flag does not mean the translation is verified. It means a machine found nothing it can catch.

## Rules

1. **Head terms must be unique within a language.** If one spelling points at two entries, there is no
   way to decide which entry a comment belongs to. The validator fails on it.
2. **The tool's own wording wins.** Where that language's Illustrator, Blender or Unity has a spelling,
   follow it.
3. **One sentence for the description.** Do not transcribe the spec. Conditions, units and operations
   stay in the English canon.
4. **`aliases` is for real parallel spellings only.** No invented synonyms to help search.
5. **The keys of `terms` must match the entry ids in `vocab.v2.json` exactly.** Never add or remove one.

## Before opening a pull request

```bash
uv run python tools/review_locales.py
uv run python tools/validate_stock.py
```

The first refreshes the flags, the second checks coverage, head-term collisions and field constraints.
Both must pass, and both also run inside `uv run pytest`.

## Current state

Translations are LLM-drafted **editorial counterparts** and have not been checked against each
language's industry corpus. Each file says so in its `translation_basis`. `ko` was carried over from the
v1 original and so has zero flags; the rest still have entries to confirm. Anywhere a settled spelling
matters — a contract, a style guide — get a local team to confirm it first.
