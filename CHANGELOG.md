# Changelog

Hand-written changes for users and contributors. An unreleased entry is not a published package.

## Unreleased

- Add a `persona-build` skill: end-user personas as spec-perturbation mode 2 over an artifact that already
  exists, recorded as projections with what they may and may not claim, rather than as descriptions of
  people.
- Let the overlay override the reader profile on vocabulary, and on nothing else: a term a team's records
  have used is named even for the reader with no art training, because it is what that team says.
- Scope the ten-node diagram threshold to the feature realm. A realm is not a subsystem, and the data
  realm's size is the point rather than a symptom.
- Add the reader overlay: what a team's records demonstrate about the vocabulary they work in, projected
  from `records.jsonl` and cached beside it. It is derived, so deleting it loses only time, and it says
  what a corpus demonstrates rather than anything about a person. Nothing consumes it yet.
- Add a `cache` realm to the architecture ledger for derived views that own no invariant. It is a row and
  not a node: nothing propagates from a projection that may be deleted at any time.
- Add `--profile` to `asrai light-ledger` and `profile` to the `light_ledger` MCP tool: with one, the
  result carries `sentences`, the same findings said for that reader; without one, the result is
  unchanged. The profile never reaches the measurement — both transports apply it to a finished result.
- Ship reader profiles (`profiles.v1.json`) as stock data: four axes over the three readers `spec.md` §1
  already names, selecting how a finished verdict is said. A profile is a view, not a truth — the same
  asset and answers produce an identical verdict and record under every one, and none is the default.
- Say the lighting verdict as sentences for a reader with no art vocabulary: an id, a box and a direction
  per finding, with a surface nobody answered said out loud rather than omitted. It is a projection of a
  finished verdict and is not yet reachable from the CLI or the MCP tools.
- Scope translation to the path a vocabulary contribution walks, and presume a contributor who works in
  English everywhere else. `CONTRIBUTING.md` and the locale bundles' README become candidates; a directory
  README elsewhere does not.
- Rename the CLI's `asrai vocab get --compact` to `--full / --no-full`, so one word carries the axis on the CLI,
  the MCP tools and the library. The default is unchanged: `get` returns the whole entry, `search` does not.
- Issue every subject surface of the lighting answer form as `null` and read an unanswered surface as
  `unknown`. A form handed back as issued previously reported `yes` on specular, light colour, ambient,
  rim and albedo — five surfaces nobody had looked at. An answered surface still passes every subject it
  does not list.
- Partition the repository into realms — spec, feature, data, support — and record what each one owns,
  how far its errors travel, who may write it and what checks it. `architecture.md` now carries that
  ledger and each realm's interior is drawn one level down in its own README.
- Add a repository-operating skill covering document ownership, write-policy scoping, diagram nesting
  and evidence discipline, and replace the development skill it supersedes. `AGENTS.md` now carries the
  three rules an agent breaks before reading anything, each linking to the document that owns it.
- Check that a directory whose README enumerates its contents still lists all of them, alongside the
  existing broken-link walk. Three reviews had fallen out of their index.
- Adopt compact revision references for cited evidence, keeping full commit identity and shortening
  only the display. Machine records, manifests and translation stamps stay full.
- Narrow the write-policy globs so that a directory's own README is no longer formally unwritable, and
  rule that within one layer of the judgment hierarchy the later revision wins.
- Add asrai commit policy and local hooks that check the actual commit before moving the branch,
  including amendments; use independent temporary histories for the checker tests.
- Make the runbook's judgment hierarchy explicit: human decisions and maintained intent govern
  generated specifications, code and tests.
- Label the existing lighting agreement cutoffs and surface selection as unverified policy; remove
  unsupported empirical claims without changing the measurements or verdict behavior.
- Build a hash-locked install bundle and check its installed CLI, MCP and shipped data outside the
  checkout. Dependency locking does not guarantee identical results across OS or JPEG decoders.
- Add CI for locked tests, links, translation stamps and wheel installation; a trusted default-branch
  workflow requires DCO signoff trailers on new pull-request commits, with fixed pre-adoption history
  exempted.
- Add a pull-request template for rationale, verification, provenance and human review holds.
- Make fixture tests enforce the documented byte equality, including serialization; fixture images
  and expected outputs are unchanged.
