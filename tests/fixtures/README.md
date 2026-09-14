# `tests/fixtures/` — the byte-equality corpus

Six small images and their expected `measure` output. Together they are the promise that the same bytes
in give the same JSON out, on any machine, for as long as the schema stands.

| image | covers |
|---|---|
| `sprite_rgba.png` | the ordinary case: a sprite with a straight alpha channel |
| `antialiased_rgba.png` | a soft edge, where the silhouette threshold decides |
| `indexed_alpha.png` | an indexed PNG with transparency, which Pillow decodes differently |
| `gray16.png` | 16-bit greyscale, which `convert()` would clip to white and which `load` rescales explicitly |
| `screenshot_rgb.png` | a frame with no alpha at all |
| `flat.jpg` | a lossy source, and a reminder that one is reported rather than corrected |

`expected/` holds one JSON per image. `test_fixtures.py` compares them byte for byte, which is stricter
than comparing parsed values on purpose: a change in key order or float formatting is a change in what
a downstream reader sees.

## Regenerating

```bash
uv run python tools/make_fixtures.py
```

**This is a deliberate act, never a fix for a red test.** A fixture diff means one of two things:

- a *bug* — the measurement changed and should not have. Fix the code; do not regenerate.
- an *intended change* to what `measure` reports. Then regenerate, and the diff of `expected/` goes into
  the same commit as the code change, so a reviewer sees exactly which numbers moved.

If you cannot say which of the two it is, it is the first one.
