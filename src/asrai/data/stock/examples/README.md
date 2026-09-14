# `src/asrai/data/stock/examples/` — illustrative instructions

Eight `instruction.v2` documents, one per shape a real instruction can take. They exist so a model can
see a correct document before it writes one, and so `lint` has something to be tested against.

| file | shows |
|---|---|
| `anticipation.json` | a timing term with no scalar to set |
| `body_width.json` | a proportion change with a measured basis |
| `camera_fov.json` | a numeric parameter carrying its unit |
| `compositing.json` | a frame-level instruction |
| `material_smoothness.json` | a material parameter with a range |
| `readability_proxy.json` | a `proxy_only` term, which may never take `set` or a delta |
| `silhouette_gap.json` | a structural observation turned into a change |
| `vector_anchor.json` | an SVG/L0 instruction naming its render profile |

## Rules

- **Zero taste.** These demonstrate *shape*, never preference. `readability_proxy.json` is here to show
  that the operation is refused, not to argue a value is too low.
- Every one of them is linted by `tools/validate_stock.py`, which runs inside `pytest`. An example that
  does not pass `lint` cannot be committed.
- They are examples, not fixtures: changing one is a documentation change, and changing what `lint`
  accepts is a contract change that belongs in [docs/spec.md](../../../../../docs/spec.md) first.
