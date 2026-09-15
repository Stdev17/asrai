> 2026-09-16 · verified at `149656a` · Codex, recording the maintainer's instruction and the implementation rationale

# Human authority, propagated specifications and the first release gate

For contributors and future maintainers. This records the maintainer's instruction in the current
task: human-maintained documents take precedence; a conflicting implementation is wrong. An
AI-generated spec is itself an implementation artifact, but sits above code because downstream
changes propagate through it. The live rule is runbook §1, not this historical record.

## Authority

The old spec opening inverted responsibility by saying that disagreement made the document wrong.
The docs index also put spec above every other document, including maintained operating policy.
Both conflict with the maintainer's instruction. A generated spec must first agree with the human's
intent; implementation and tests must then agree with the spec. A test proves behavior, not approval.
Authorship alone cannot establish adoption; the source of a material human decision must be reachable.

This decision also supersedes the historical review index's last sentence describing CHECKPOINT as
rewritten. It has been append-only since the earlier decision. Existing dated reviews and the index
remain unchanged, and the live docs index routes here.

## Unverified art-direction policy

The earlier art-direction rationale identified an unsupported disagreement cutoff, an unsupported
claim about typical hand-drawn key variation and an unexplained surface selection. The newest
checkpoint added the unsupported suspicion boundary. No new artist study or human validation was
provided in this task. The empirical-sounding assertions therefore leave operative guidance; existing
cutoffs and surfaces remain explicitly unverified implementation policy. Retaining their behavior is
not a claim that the maintainer approved their magnitudes. Measurements still measure angles;
the choice of which angle settles an art judgment remains unvalidated.

The claims registry prevents drift between code and prose. It cannot prove that a number is warranted.
The prior review remains the evidence of what was found, and a later human validation must name its
source before these policies can be promoted.

## Reproducibility and distribution

The source lock is not consumed by a user invoking a pinned package through uvx. The initial supported
path is a wheel plus a runtime requirements export derived from that same checkout's uv.lock, with
artifact hashes and a Python version file. The checker installs them into an empty environment and
calls the installed CLI and stdio MCP away from the checkout. The export is generated release output,
not a second hand-maintained dependency source.

The wheel hash identifies what was tested. The environment report identifies platform and decoder.
This fixes package selection without pretending that native artifacts on different operating systems
are identical. Existing exact fixture comparisons remain; no arbitrary tolerance is introduced.
The existing fixture test compared parsed JSON although the contract promised byte equality. The test
now uses the generator's serialization and compares UTF-8 bytes, honoring the governing document.
The fixture README describes the toolchain boundary instead of promising equality on untested decoders.

The CI workflow runs existing checks and this installation check with read-only repository access and
immutable Action references. DCO runs separately under `pull_request_target`: the workflow and checker
come from the trusted default branch, only Git objects for the event's exact base and head SHAs are
fetched, and no PR file is checked out, imported, installed or executed. It exempts only ancestry
predating adoption, not forgeable commit dates. The first workflow and checker change cannot enforce
itself; it requires explicit review and local validation before landing on the default branch. Only
then can signed and unsigned PR cases prove the remote check before a ruleset requires it. Human
judgments about terms, translations and images remain review or named holds. Artifacts still require
release attachment, and required checks still require repository-side configuration; writing YAML
proves neither.

Sources: [uv tools](https://docs.astral.sh/uv/guides/tools/),
[uv lock export](https://docs.astral.sh/uv/concepts/projects/export/),
[uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/),
[GitHub secure workflow use](https://docs.github.com/en/actions/reference/security/secure-use).
