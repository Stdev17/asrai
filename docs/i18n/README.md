# `docs/i18n/` — translated documents

A translation is a **quality-control device**, not a translation service: it exists so a contributor
who thinks in Korean, Japanese or Chinese carries the same mental model as one who thinks in English.
That is also why it is bounded — a translation that has drifted teaches the wrong model, which is
worse than no translation at all.

## What may be translated, and what may never be

| document | translated? | why |
|---|---|---|
| [`README.md`](../../README.md) | yes | the entry point; a reader decides here whether the project is for them |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | reviewed | process, not contract, and on the vocabulary path |
| [`locales/README.md`](../../src/asrai/data/stock/locales/README.md) | reviewed | how a locale bundle is written; the vocabulary path runs through it |
| a directory `README.md` elsewhere | no | its reader has already crossed into English |
| [`spec.md`](../spec.md), [`conventions.md`](../conventions.md), `SKILL.md` | **never** | a translated contract is a second source of truth. When two say different things, work stops to find out which one the code obeys |
| [`review/`](../review/) | never | dated records, never edited at all |

`docs/README.md` carries the same rule in one paragraph. This file is the mechanics.

## Who a translation is for

> 2026-09-17 · verified at e30bea9 · Shelby Yoon

Translation is reviewed for the whole path a **vocabulary** contribution walks, and nowhere else.
That path is the entry point, the contribution steps, and the locale bundle's own README. It gets
the exception because it is the one realm this repository cannot maintain for itself: an industry's
vocabulary map is polymorphic across language communities, so the term a studio in that language
actually says is the single thing only a contributor who works in it can supply. Asking for it in
English asks the wrong person.

Everywhere else presumes a contributor who can work in English. Code, tests, tools, the contracts
and the operating documents stay English-only, and a reader who has reached them has already
crossed a boundary where English is the working language. This says which documents are candidates,
not that each one is translated today; every translation still arrives with a named owner below,
and a missing owner is why a candidate stays a candidate.

## Layout

One directory per language, mirroring the repository path of the source:

```text
docs/i18n/ko/README.md        <- README.md
docs/i18n/ja/CONTRIBUTING.md  <- CONTRIBUTING.md
docs/i18n/zh-Hans/src/asrai/data/stock/locales/README.md  <- the locale bundles' README
```

Nothing needs to be added to the tooling to extend this: `tools/check_translations.py` reads the path
out of each file's own stamp, so a new language or a new document is a new file and nothing else. The
language codes are the ones the vocabulary already uses (`locales/README.md`), so a contributor is
never asked to learn a second set.

## The stamp

Line 1 of every translated file, exactly:

```text
<!-- translation-of: README.md@3ae09cad96b075595d6ac077eb7dbe582f97c1ae -->
```

The path is repository-relative; the hash is the source's commit at the moment the translation was
made, and it **stays a full OID**. The compact `path@short` form in
[runbook §5](../runbook.md#revision-references) is for prose that cites a revision; a stamp is where
the full identity is retained, so shortening it would leave the citation nothing to resolve against.
`check_translations.py` accepts a shorter prefix, which is a tolerance for hand-written stamps, not an
invitation. Below the stamp, one blockquote in the target language saying English is canonical.

```bash
uv run python tools/check_translations.py
```

reports, for every file here: a missing or malformed stamp, a source that does not exist, a source
that may never be translated — those are errors — and how many commits the source has moved since
the stamp, with their subjects, so a human can see whether the change was a typo or a promise.
**Staleness is reported, never enforced** — decided 2026-09-15: a stale translation does not block a
pull request. What holds a language current is a person, below.

## Owners

A language is accepted with a named owner: someone who reads it natively, has read the translation
through, and answers for its staleness when `check_translations.py` reports it. A gate cannot do that
job — Kubernetes' localization retrospective is the record of a translated page being unsupported from
the moment it merged — so the gate is not asked to.

| language | owner |
|---|---|
| `ko` | none yet |
| `ja` | none yet |
| `zh-Hans` | none yet |

The three that exist predate the rule and are the exception it starts from: until a name is in this
table the maintainer answers for them, and they stay marked unconfirmed. A new language is not
accepted without a name here.

## Numbers

A number in a translated document is checked by the same gate as the English one: `tests/claims.json`
registers what computes it, and the suite requires the numeral to appear in every translation of a
document that states it. So write numbers as **numerals** — `용어 475개`, not `사백칠십오 개의 용어` —
even where the English spells them out. That is the one place where a translation is deliberately not
a mirror of its source.

Translators do not edit `claims.json`. It is keyed on the English file; the translations are found
from it.

## Status

All three are LLM-drafted and unconfirmed by a native speaker of the industry's language, exactly as
the locale bundles are (`src/asrai/data/stock/locales/README.md`). Where a settled spelling matters,
get a local team to confirm it. Corrections are the cheapest contribution this repository takes.
