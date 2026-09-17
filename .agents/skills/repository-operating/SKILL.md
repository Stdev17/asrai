---
name: repository-operating
description: Use when writing, moving, splitting or reviewing a repository's operating documents — policy, contracts, indexes, per-directory READMEs and the diagrams in them — or when deciding which document owns a rule.
---

# Operating a repository's documents

Documents here are code that generates code. A wrong line in a module fails a test. A wrong line in an
operating document is executed by every agent that reads it, propagates into code, tests and further
documents, and fails nothing. That asymmetry, not volume, is why these rules are stricter than ordinary
code hygiene: there is no runtime that rejects a bad document, so the arrangement has to.

This skill is orthogonal to the documents it protects. It states how they may be arranged, never what
they say, and the dependency runs one way: delete this file and every governing document is still
valid; delete a governing document and this file has nothing to operate on. Nothing here may be cited
as authority over a document it points at.

## Realms and the binding ledger

Invariant 1 asks which document owns a fact. Nothing answers that until the repository is partitioned
into **realms** — boundaries that own a class of invariant — and each realm names the one document that
states its rules. That partition is the ledger, and it is what turns invariant 1 from advice into a
lookup. The rules below name realms; the ledger is the only repository-specific thing in this file.

A realm is not a directory. It is the answer to four questions, and two boundaries share a realm only
when all four answers match.

| question | why it changes the rules |
|---|---|
| what **invariant** does it own? | the thing a leak breaks |
| how far does an error **propagate**? | sets how hard invariant 1 has to be enforced here |
| **who may write** it? | a realm the world contributes to cannot be held by review alone |
| **what verifies** a claim in it? | a realm with no verifier is one where prose is the only evidence |

### Where the ledger lives

The ledger is a fact about one repository, so it lives in that repository and this file only binds to
it. **asrai's is [`docs/architecture.md`](../../../docs/architecture.md).** Copying its rows here would
break invariant 1 inside the document that defines invariant 1.

### What the realm changes

Invariant 1 is one rule with four enforcements, because a duplicate costs a different amount in each.
Read a realm's row and apply the matching one.

- **Wide propagation, maintainer-written** — never duplicate; link. A second copy conflicts with
  implementation as soon as one of the two is read, which is the shortest path from a documentation
  edit to a defect. Most contract and policy realms are here.
- **World-written** — duplicate only under a validator. A realm the public contributes to will contain
  parallel copies by design (per-language bundles, per-platform manifests), and what makes that safe is
  that a machine, not a reviewer, holds them equal. Hand-maintained duplication here is unreachable by
  the very contributors who would have to repair it.
- **Behavioural** — the duplicate to watch is one rule living in two entry points. Rules stay in the
  owner; entry points adapt and hold none.
- **Downstream sink** — may restate freely, because it holds no authority. A test docstring quoting a
  rule is evidence of intent, not a second source of truth.

A repository's centre of gravity is the realm needing contribution it cannot get from one person. That
realm is usually not the one with the most code, and it is the one whose validators must be written
first.

### When the owner is not reachable

A realm can name an owner this repository cannot ask to fix anything: content accepted from a third
party and then frozen, or a canon that lives in another repository. Invariant 1 still holds — the fact
has one owner — but that owner is outside the write set, so **repair is not an available move**, and
editing the local copy forks it without saying so.

Two exits, declared in the ledger row rather than chosen when the problem appears:

- **supersede** — the local statement wins under an explicit precedence rule and the imported content
  stays exactly as accepted. A correction is a new record pointing at what it replaces.
- **project** — the external canon wins and the local statement is a pinned copy carrying the revision
  it was taken from. It is re-taken, never edited.

The write set is what makes this non-optional: a repository may only repair what it owns. State that
boundary in the ledger. A reader arriving with different ticket discipline, or none, gets the
constraint from the row instead of being assumed to share yours.

### A declared absence of authority stays false-detectable

A realm that owns no invariant holds no authority, and that is a **declaration, not an observation**.
It goes false quietly: a suite starts being cited as the contract, a fixture becomes the definition of
correct, a status log starts settling arguments. Cite such a document as evidence of behaviour; never
as the source of a rule. The violation is a string — a path in a no-authority realm cited as the
*reason* for a statement in a realm that has authority — so the declaration can be held to itself.

### Managing the ledger

The ledger is reviewed, not inferred. Which realm a path joins is a human judgment and deliberately not
derivable from the tree; a generated guess would be confidently wrong at exactly the boundaries that
matter.

A machine may check that:

- every tracked path falls in **exactly one** realm — total and disjoint
- every realm's stated document exists, and every stated verifier that *is* a command runs
- a realm with no verifier is *declared* as such, not discovered by a reader

Review settles the rest: which realm a new path joins, and whether a new boundary is a realm at all or
an extent of an existing one. Adding a realm carries the weight of adding an owner — name the
invariant, say what propagates, and take it to the responsible human.

A ledger row declares six things, and the last two are the ones repositories leave out:

| field | admits |
|---|---|
| extent | paths. A file straddling two realms is a split-the-file ticket, not a row |
| invariant | one, or an explicit *none* for a realm that only carries another's evidence |
| propagation | the realms an error reaches |
| who writes | and whether they are reachable for repair — if not, the row names supersede or project |
| verifier | a command, a **named human process**, or an explicit *none*. Not every verifier is executable, and a realm that fakes a command to satisfy a checker is worse than one that admits a panel |
| derivation | authored, or **derived from a named realm**. A derived realm's facts are owned by its source: editing it is a defect and its write policy is regeneration |

Untracked and ignored space is outside the ledger by definition. Declare that once, so that "every
tracked path falls in exactly one realm" cannot quietly widen to cover scratch and experiment records.

**The ledger obeys these invariants too.** It is a document, so a repository too large to draw its
realms once nests them: a parent row names a child ledger and does not draw its interior, exactly as
invariant 4 nests READMEs. **No realm may be a default.** A path matching no row is reported
unassigned, never swept into whichever realm is broadest — a catch-all realm silently authorises
whatever lands in it, which is the ledger granting itself the authority the rest of this file spends
its length withholding. A repository with one realm says so in a line and keeps no table.

A repository that already has path tables — commit-attribution buckets, ownership or code-owner files —
keeps them. They are a finer partition for a different purpose. The ledger says which realm each bucket
refines; it does not replace them, and duplicating their contents here would break invariant 1 in the
document that defines it.

## Four invariants

**1. One fact, one owner.** Every normative statement has exactly one document that may state it;
every other document links. A second copy is not redundancy, it is a second source of truth, and it is
found by the reader who acted on the stale one. Before adding a paragraph, find the document that
already owns its subject. If the copy feels necessary because the owner is hard to reach, the routing
is what is broken, not the ownership.

**2. A write policy never swallows its own index.** A glob over a directory targets a prefix that
directory's `README.md` cannot match — a date, a language code, an id. A directory's README is the
index of what lives there, or the policy itself; it is never an instance of what the policy governs.
An unprefixed glob makes a maintained index formally unwritable, and nobody can then tell whether
correcting it is permitted.

**3. The provider owns the edge.** A signature, field or contract crossing a boundary is written once,
by the side that owns the invariant. The consumer names the dependency and does not restate what
crosses. Two documents describing one edge is invariant 1 failing in the one place decentralised
documents make likely.

**4. One diagram per README, one level deep.** A diagram's nodes are its own directory's children,
plus a stub for each outside owner it touches. It never draws a grandchild and never redraws a
sibling's interior. The budget is therefore per-level fan-out, not a total: a system that outgrows one
drawing becomes two levels, and three when it outgrows that, while every drawing stays readable. A
README that names a node more than one hop away has leaked, and one hop is the containment boundary —
a leak that cannot travel cannot propagate.

## One count, two questions

A repository sets one threshold on a boundary and then uses it to answer two different questions. They
coincide while the repository is small and separate as it grows, so say which is being asked before
responding to the number. The number itself belongs to the binding — for asrai,
[`conventions.md`](../../../docs/conventions.md#0-owner-boundaries) §0 — and
is deliberately not repeated here.

| question | what crossing it means | response |
|---|---|---|
| **legibility** — can this be read? | too many nodes in one drawing, or crowding at ordinary reading width | deepen. Introduce the intermediate directory the nodes already cluster into and give it a README. Never shrink text, hide an edge, or split one drawing across pages |
| **scope** — should one team hold this? | too many responsibility owners under a single boundary | stop and take it to the responsible human. Name the new invariant and say whether it belongs to this job |

A subsystem is owned by at most a two-pizza team, so the owner count is a proxy for what that team can
hold in its head. Crossing it is a feature-creep or bottleneck signal about the team, not only about
the drawing — which is why deepening answers the first question and never the second. A readable graph
below the count is evidence of legibility, never proof of good scope.

Where the two coincide, as they do at asrai's root, a single number serves both and the distinction
only matters the first time a subsystem appears. Answering a scope question by deepening is the
failure this section exists to prevent.

## Evidence, numbers and staleness

Pin what you cite and keep its identity; the revision-reference policy owns the form. A number stated
in prose is registered where the repository computes it, so a number that moves fails a check instead
of drifting through documents. A claim nothing computes is prose, and prose that reads as measured is
the defect this repository has already fixed twice.

## What may be mechanised, and what may not

Mechanise the rule whose violation is a string, and only once a second real instance exists. A check
written for one hypothetical case is the speculative scaffolding these documents forbid elsewhere.

| rule | mechanisable as |
|---|---|
| every file in an enumerated directory appears in its index | membership |
| a write-policy glob agrees with the tool that applies it | glob against tool scope |
| a cross-boundary signature appears in two READMEs | string equality |
| a README names a node two hops away | name reachability |
| a naming decision cites a name that resolves to more than one surface | the name against the surfaces carrying it |
| a no-authority realm cited as the reason for a rule | string, path against citation |
| a realm's stated command verifier does not run | execution |
| a rule stated in two documents | — |
| a document that is semantically stale | — |

How many instances a repository actually has, which of these it has written, and what each written one
is called are facts about that repository and live in its binding, never here. A count copied into this
file goes stale the week a check is written and nothing catches it — the same argument that keeps the
realm ledger out of this file, applied to the row below it. **asrai's is
[`docs/runbook.md`](../../../docs/runbook.md) §1.**

Say which of these hold and which do not. Claiming a gate that does not exist is the same defect as an
axis reading `pass` on evidence it never had, and so is describing a written check as still to be
written.

## Hooks

A deterministic repository question belongs in a script, not in this file: a model should spend its
turn on whether a document is *right*, not on recomputing what Git already knows. Where such a check
exists, the binding names it and it runs from that repository's landing checks; call it by name and do
not read a hook's implementation into context in order to decide whether to run it.

## Before you change an operating document

- Name the document that owns the subject. If it is not the one open in front of you, link instead.
- Say which layer of the hierarchy the change sits in, and whether anything at that layer already says
  the opposite. Within a layer the later revision wins; what the hierarchy cannot order goes to the
  responsible human.
- Trace the rule to every document that repeats or depends on it, and move them together or say why not.
- Leave the smallest check that would fail if the rule were violated again, or state that none exists.
