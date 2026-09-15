> 2026-09-16 · verified at `78266a1` · Codex

# Owner boundaries for a single skill

The responsible human requested an agent-skill adaptation of DeliveryKnight's conventions and a
signature-only owner graph. Their scope decision is explicit: reaching the owner-review threshold
in conventions §0 is a feature-creep signal for a single skill, even if a drawing fits. A crowded diagram calls
for a boundary review; it does not authorize converting asrai into a general tool system.

## Source identity

Inspected local source: `DeliveryKnight/docs/conventions.md`, at checkout HEAD
`c02f26c02821721c8de9137bb3df1c0590100c7a`. The source file was **untracked**, so that HEAD is checkout
context, not the revision containing the copied content. Exact source bytes have SHA-256
`1c87ceb5a43a8d93bce89fcc64997361de6a7e9dcf7cf41c7527a5bdd59da60d`.

Conventions §5 normally requires a source commit SHA. In this task, the responsible human explicitly
approved using the content hash for this copy only: "이번 사본만 해시 출처 허용". The commit records
the uncommitted source in its body and a scoped `Deviation:` trailer. The `Source:` value is the
SHA-256 above, not a commit identity. The general commit policy remains in force; DeliveryKnight
is not changed.

## Adaptation

- Carry over decomposition by owned invariant and visible boundary signatures, stateless-agent naming,
  stable contract meaning, the smallest adequate dependency, and write-set walls with evidence.
- Retain asrai's existing Python core/transport split, append-only records, numeric claims, authority
  hierarchy and typed commit format. DeliveryKnight's older commit section does not replace it.
- Do not import Unity assemblies, scenes, serialized assets, gameplay timing, the larger game-system
  capacity, or its exception deferring diagram enforcement until a future split.
- Keep the development procedure in `.agents/skills/asrai-development/SKILL.md` and the inspectable
  graph in `docs/architecture.md`. The bundled asset-use skill gains no development responsibilities.

## Judgment and reconsideration

The current owner inventory follows independent invariants, not filenames or commit buckets. Config
and environment reporting support reproducible evidence; lookup/lint, measurement, qualified lighting
observation and durable records belong to the same art-direction job. Transports, version metadata,
helpers and data-only dictionaries do not add independent product responsibilities.

The graph exposes private rounding, a shared data directory, a generic hash helper coupled to records,
and record, configuration, scale and term-ID contracts not visible in imports. Those seams merit repair when changed; they
do not justify another subsystem merely to improve the picture. A future renderer, scheduler,
publisher or other independently useful job needs a fresh scope decision. Code and a readable graph
alone cannot establish that this human decision has been made.
