# Commit policy adoption — 2026-09-16

The responsible human supplied the typed subject and `Owners`, `Fixes`, `Values`, `Deviation`,
and `Source` rules, then authorized adapting the checker to asrai after the failure diagnosis.
The instruction is the policy source; the checker must implement it, and its error text exposes
the mechanical schema. The old untyped subject convention in `conventions.md` is superseded.

## What the diagnosis established

The supplied, untracked `tools/commit_check.py` in the main asrai checkout was byte-identical to
the untracked checker in the local DeliveryKnight checkout. Its SHA-256 was
`15580c7b2c8f8e3254c93f609fd158fce4c77b143892e0c413ae587854b8aadb`.
Neither checkout had committed that file, so no source commit is claimed for those bytes.
This change adapts the supplied asrai file; it does not invent an upstream revision for it.
The original wrapper's SHA-256 was
`236e294348f9c5abfeeb36d0d7c9ab185b2de3dfdee71411ebf38839d725a667`.

Independent defects explained the failure:

- Unity paths classified asrai runtime, tests and CI as `root`, and numeric checks only recognized
  Unity assets. The self-test required commits that existed only in another repository.
- Git errors became empty output. An invalid revision range returned success and a missing self-test
  revision crashed while parsing a nonexistent message.
- `core.hooksPath` was unset, no default commit-message hook was installed, and the hardening
  worktree did not contain the untracked checker. These observations establish current state,
  not which earlier action or person caused it.
- The staged diff described a new commit but not a message-only amendment. Git's `commit-msg`
  interface supplies the message file, not an unambiguous amend flag.

## Decision and boundary

Retain the generic message checker and replace the project policy and unavailable-history behavior.
Asrai owners are defined in `conventions.md`; literal numeric comparisons supplement human review.
The old search for any test containing the old number is removed: textual coincidence cannot
establish that a test pins that parameter. Existing package tests and claims remain the behavior gate.

Use Git's native `reference-transaction` hook in the `prepared` phase for exact commit-tree checks.
The ordinary message hook checks structure; the transaction hook sees the created commit and its
parents before refs move. Both new commits and amendments use the same comparison. Renames expose
both paths and merges compare to the first parent. Hook rejection does not move the branch.
The parser accepts both object IDs and symbolic values from the current
[Git hook protocol](https://git-scm.com/docs/githooks#_reference_transaction). Symbolic-only changes
introduce no commit; a transition to detached HEAD still checks its new object ID. Local native
history tests use Apple Git; direct protocol cases cover symbolic rows that version does not emit.

The transaction hook checks newly introduced commits on local branches and detached HEAD. It does
not enforce policy on already reachable history, fetched remote-tracking refs or tags. Exact range
review remains required, and local hooks do not establish a remote security boundary. The DCO
workflow remains separate; this change does not claim remote commit-schema enforcement.

Temporary Git repositories replace foreign history dependencies. The same runnable tests exercise
the real hooks through root commits, normal commits, amendments, merges, renames and linked
worktrees, plus malformed trailers and unavailable or shallow history. No source asset, fixture,
runtime magnitude, prior checkpoint entry or prior review is changed by this adoption.
