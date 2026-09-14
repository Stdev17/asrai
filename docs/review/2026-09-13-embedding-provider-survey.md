# Embedding providers reachable through OpenRouter

> Written 2026-09-13, for the package author choosing a default for the vector cache.
> **Status:** the survey behind `spec.md` §10. The decision it produced lives in the spec; the prices
> and token figures live here, because a vendor's price list is not a contract asrai can keep. Read a
> number below as what was true on the day, not as what you will be billed.

## What was surveyed

Two multimodal embedding models, against the requirement in `spec.md` §10: one model and one dimension
per index, per-asset input is the rendered evidence, and deleting the cache must cost only retrieval
speed and visual neighbours.

| model | dimensions | image tokenisation | price |
|---|---|---|---|
| `google/gemini-embedding-2` | 128–3072, MRL; default 3072; recommended 768 / 1536 / 3072 | about 258 tokens per image `[estimated: Google lists $0.00012 per image at $0.45 per M]`; up to 6 images per input; 8,192 tokens per input | $0.20/M text, $0.45/M image tokens |
| `voyageai/voyage-multimodal-3.5` | 256 / 512 / 1024 (default) / 2048 | 1 token per 560 pixels: 64² ≈ 7, 256² ≈ 117, 512² ≈ 468, 1024² ≈ 1,872, 1920×1080 ≈ 3,703; 16 M pixels max | $0.12/M tokens |

At this corpus size the cost is negligible either way: a thousand sprites is about $0.12 on Gemini and
under $0.10 on Voyage. Cost was therefore not the deciding factor, and a later price change is not a
reason to revisit the choice.

## What it decided

`google/gemini-embedding-2` at **768** dimensions. A corpus of hundreds to a few thousand items gains
nothing from 3072, and the cache is rebuildable if that proves wrong — a model or dimension change is a
cold cache, not a corruption.

## What it did not settle

Whether the zero-retention terms of Google and Voyage survive the OpenRouter route is `[unverified]`.
Until a team checks, `allow_external_embedding = false` is the safe setting, and it costs only visual
neighbours. Whether "about 258 tokens per image" holds at every image size is also unverified; it is an
estimate derived from a per-image price, not a published tokenisation rule.
