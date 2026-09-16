# Changelog

Hand-written changes for users and contributors. An unreleased entry is not a published package.

## Unreleased

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
