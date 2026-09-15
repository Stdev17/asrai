# Changelog

Hand-written changes for users and contributors. An unreleased entry is not a published package.

## Unreleased

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
