# CHECKPOINT

**Append-only.** The newest entry is on top and is what is true now. Nothing below it is ever edited or
removed — the rule the record corpus already follows (`spec.md` invariant 6), applied to status. A
correction is a new entry that names what it supersedes.

Every entry is stamped `YYYY-MM-DD · verified at <sha> · <author>`, where the sha is the commit the
entry's facts were checked against.

Three consequences of the rule, all deliberate:

- **`tests/claims.json` never anchors a number here.** An old entry is a frozen observation and a claim
  has to stay true; the two rules would fight. A number that must stay true lives in `spec.md`, a README
  or `CONTRIBUTING.md`.
- **Each entry restates the volatile lists in full** — what is built, what is limited, who is waited on —
  because the entry above it may not be edited. That restatement is what the rule costs, and it is
  cheaper than two people reconciling one rewritten snapshot.
- **Two pull requests that each add an entry still conflict**, now on the first lines of the file. The
  resolution is mechanical: keep both, newest first. That is the whole point; the old shape needed a
  judgment.

Entries dated before 2026-09-15 were reconstructed from the single rewritten snapshot this file used to
be, on the day the policy changed. Their wording is unchanged; only the shape is new.

---

## 2026-09-17 · verified at `e30bea9` · Claude Opus 5

A dogfooding pass: three personas — a developer with no art training, a technical artist, and a
non-English-speaking TA arriving to contribute vocabulary — landed cold and ran an end-to-end asset
diagnosis, with perturbation on each path. Intended gaps were excluded from the tour by the
responsible human: stock unimplemented, onboarding unreviewed, only the light family built, the CLI
tools unreviewed, and host registration for Claude Code, Codex, OpenCode and Hermes unreviewed. This
entry supersedes the state, limits and waiting list of the entry below; that entry's account of the
realm split stands unchanged.

**State.**

- phase: 1 (core and transports) and 1b (surface pass) remain complete; phase 2 is not implemented
- last_acceptance_passed: 62 tests on CPython 3.14.7. Links: 0 broken, 0 unindexed. Translation
  stamps: 3 current, 0 stale, 0 broken. A fresh wheel install passes CLI, actual stdio MCP, bundled
  data and input preservation; its bundle is `dist/repro-answer-default`, and it is the check that
  exercised the renamed CLI flag from outside the checkout. Every commit in this series passed both
  installed hooks. Earlier entries retain Python 3.11, cross-version wheel and negative-hash
  installation evidence
- in_progress: everything landed here is local only; remote CI execution, DCO bootstrap,
  required-check activation and release publication are untouched and still unverified
- next_slice: when remote publication is authorized, land the reviewed DCO workflow/checker on the
  remote default branch, exercise signed and unsigned PR cases, then require `Checks (Python 3.11)`,
  `Checks (Python 3.14)` and `DCO`, and attach the verified install bundle to a release. Phase 2
  remains separate: recipes, adapters, alpha policy, recipe hashes, preview/apply/diff
- next_command: the landing checks in `runbook.md` §1 and commit range validation in §7
- working_tree: main is the only worktree, `core.hooksPath=tools/hooks` active through
  worktree-specific config. Nothing was pushed and no repository setting changed

**What landed.**

- **Silence stopped reading as agreement at the answer contract.** The lighting form issued every
  subject surface pre-filled as `{no: [], unknown: []}` and the verdict fell through to `yes`, so a
  form handed back exactly as issued — the path `spec.md` §7.1 tells the first reviewer to take —
  reported `yes` on `specular`, `light_color`, `ambient`, `rim` and `albedo`. Perturbation showed the
  default was unconditional: deleting the `subjects` key entirely still produced `yes`, while an
  explicit `unknown` list produced `unknown`, so the mechanism existed and was simply never the
  default. The form now issues `null`, an unanswered surface returns `unknown` and records nothing,
  an answered one still passes every subject it does not list, and `cast_shadow` still falls through
  to the measurement that owns it. Third occurrence of this defect class in the repository's history,
  first at the answer contract. No schema bump: no answer sheet is persisted anywhere
- The covering test walked that path and asserted nothing about the five surfaces, which is how the
  default survived a suite that ran over it every time. It asserts them now
- `asrai vocab get --compact` became `--full / --no-full`. `91a4bc7` had written the conventions §1a
  row choosing `full` *and* shipped `--compact` on the CLI beside it, so the table read as though the
  decision were carried out while the surface a human types kept the rejected word, printed on the
  front page in four languages
- The Korean, Japanese and Chinese READMEs were two commits behind and asserting deleted English:
  the removed layout paragraph naming `cli` and `server` as core while omitting `light`, `uv sync`
  without `--locked`, pytest as "the single gate", and byte equality against fixtures. All three are
  current and restamped. No check was added — semantic staleness is what a stamp and a named owner
  exist for, which the repository-operating skill already records
- `docs/i18n/README.md` now scopes translation to the vocabulary contribution path and says why:
  an industry's vocabulary map is polymorphic across language communities, so the term a studio in
  that language actually says is the one thing only a contributor working in it can supply.
  Everywhere else presumes a contributor who can work in English. `CONTRIBUTING.md` and the locale
  bundles' README become candidates; a directory README elsewhere does not

**Known limits.**

- **The untrained reader still gets no sentence.** `spec.md` §1 owes reader one "an id, a box, a
  direction, in a sentence they can hand to whoever fixes it". Phase one returns eight
  artist-vocabulary questions and phase two a verdict object; no sentence is produced anywhere. The
  `subjects.<surface>` questions render a literal `<subject>` placeholder, which is deliberate — the
  question asks which subjects the statement is false for — but reads as an unsubstituted template
- The repair for it is **decided in shape, not built**: align terms and phrasing per user profile
  across the CLI and the MCP tools, and let a caller switch that alignment on and off. Nothing is
  designed yet — not where a profile is declared, not whether it is a flag, a config key or a
  parameter on every verb, and not what a profile may rename without becoming a second vocabulary.
  It touches the tool descriptions, which are re-sent every turn and are on the byte budget
- The realm ledger is a reviewed partition, not an enforced one. Nothing checks that every tracked
  path falls in exactly one realm, that a stated verifier runs, or that a no-authority realm is never
  cited as the reason for a rule. The skill names all three; none is written
- The index check covers one directory through a hardcoded row, deliberately. A second index is a
  second row, not a generalization written in advance
- `2026-09-16-commit-policy.md` carries no stamp although it was written after the rule. A review is
  never edited, so it cannot be repaired; its three values are in the index's provenance table instead
- A perturbation pass over the skill proposed re-carving its four duplication archetypes as two
  independent axes, after the responsible human rejected an unsupported correlation between
  propagation range and authorship. That re-carving is **not applied** and remains a proposal
- The owner graph is a reviewed model, not compiler enforcement. Private rounding, a shared stock
  directory, a hash helper located in records and shared dictionary/literal contracts remain seams
- Hooks are installed locally; a fresh clone still needs explicit installation, and local enforcement
  is not a remote required check. Native hook tests ran on Apple Git 2.39.3
- Local results are not GitHub Actions results. Ubuntu jobs, Windows installation, signed/unsigned
  remote PR behaviour and required checks have not been exercised
- A bundle pins Python and dependency versions and constrains artifact hashes; it does not make
  OS/CPU wheels or native decoders identical. Ordinary `uvx asrai==<version>` does not consume the
  repository lock, and `doctor --lock` reports drift without refusing
- Agreement bands and surface selection still need measured evidence or a sourced human decision.
  Synthetic estimator tests do not establish art-direction validity
- `measure` refuses above 12 Mpx; 16-bit colour PNGs are measured at 8-bit precision. A heavy vignette
  can bend shaded-mass direction into the observer band; the eight brightest blobs and at most sixteen
  subjects are measured. Cast-shadow evidence needs known subject pixels and cannot separate cast from
  form shadow inside one box
- Precedent retrieval, recipes, previews/apply, ingest/promotion, the pairwise bootstrap and external
  rendering remain unbuilt. Blender and Inkscape are not installed in the verified environment

**Waiting on a human.**

- Design the per-profile term alignment named above, or rule it out; the sentence spec.md §1 promises
  reader one is blocked behind whichever answer that gets
- Authorize remote publication, then activate and verify the remote gates and release path
- Decide whether the skill's duplication archetypes are re-carved as two axes, as proposed above
- Validate or explicitly adopt the lighting policy and surface selection with a recorded basis
- Review `docs/spec.md` and the artist brief
- Name native industry-language owners for `ko`, `ja` and `zh-Hans`; their translations are current
  as of this entry, so what is missing is the name, not the text
- Decide whether `CONTRIBUTING.md` and the locale bundles' README are translated now that they are
  candidates, and into which of the three languages
- Decide `observer.mode` default and embedding egress (`spec.md` §10)
- Confirm external-tool versions on team machines before implementing their adapters

**Standing facts.**

- Inputs are immutable; outputs are new files; corpus records and prior checkpoint entries are
  append-only; dated reviews remain historical and unedited
- The runbook owns the judgment hierarchy and procedures. A conflicting implementation is defective
- Documents are code that generates code: a wrong line in an operating document is executed by every
  agent that reads it and fails nothing, which is why their arrangement is gated rather than trusted
- An answer that was never given is not an answer. The three occurrences of this defect were at an
  axis, at a measurement, and at the answer contract; each time the shape that carried it was a
  default that looked like a value

---

## 2026-09-17 · verified at `f2dea6e` · Claude Opus 5

The revision above is this pass's last code/documentation commit; the entry itself follows it. The
responsible human authorized the realm split, the skill replacement, the index check and this
commit series. The Codex entry below records the revision-reference policy, which landed inside
`78cb8a9` rather than separately.

**State.**

- phase: 1 (core and transports) and 1b (surface pass) remain complete; phase 2 is not implemented
- last_acceptance_passed: 61 tests on CPython 3.14.7. Links: 0 broken, 0 unindexed. Translation
  stamps: 0 current, 3 stale, 0 broken (advisory, unchanged). A fresh wheel install passes CLI,
  actual stdio MCP, bundled data and input preservation; its bundle is `dist/repro-doc-realms`.
  Every commit in this series passed both installed hooks. Earlier entries retain Python 3.11,
  cross-version wheel and negative-hash installation evidence
- in_progress: the documentation architecture is local only; remote CI execution, DCO bootstrap,
  required-check activation and release publication are untouched and still unverified
- next_slice: when remote publication is authorized, land the reviewed DCO workflow/checker on the
  remote default branch, exercise signed and unsigned PR cases, then require `Checks (Python 3.11)`,
  `Checks (Python 3.14)` and `DCO`, and attach the verified install bundle to a release. Phase 2
  remains separate: recipes, adapters, alpha policy, recipe hashes, preview/apply/diff
- next_command: the landing checks in `runbook.md` §1 and commit range validation in §7
- working_tree: main is the only worktree, `core.hooksPath=tools/hooks` active through
  worktree-specific config. Nothing was pushed and no repository setting changed

**What landed.**

- The repository is partitioned into four realms — spec, feature, data, support — and
  `architecture.md` is now that ledger at level 0, with propagation, authorship, verifier and the
  document each realm states its rules in. The six-module signature graph and its seams moved to
  `src/asrai/README.md`, so the top-level drawing no longer grows with the core. `README.md` keeps
  the directory map as navigation; its layout line, which duplicated that map while omitting `light`
  and calling the transports core, is gone
- data is recorded as **projected, not authored**: stock derives from an origin corpus and each entry
  keeps `origin.entry_sha256`, so a correction is re-taken rather than edited here. The planned
  `corpus/packs/` is named in advance as a realm whose writers cannot be asked for a fix, with
  supersede as its exit, which `spec.md` §5 already implies
- The development skill, which was largely a restatement of conventions and the runbook, is replaced
  by a repository-operating skill owning only what no other document does: which document owns a
  fact, how a write policy is scoped, how a diagram nests one level per README, what a ledger row
  declares, and what happens when the owner of a fact is unreachable. It binds to this repository in
  one line. `AGENTS.md` carries the three rules an agent breaks first, each linking to its owner
- Two additions settle a conflict the hierarchy could not reach: within one layer the later revision
  wins, and a write policy targets a prefix a directory's own `README.md` cannot match. `review/*.md`
  had made its own index formally unwritable while `check_translations.py` already scoped `i18n`
  correctly in code
- The human's revision-reference procedure is in runbook §5, and `docs/i18n/README.md` now says why a
  translation stamp is exempt from it — the stamp is where full identity is retained
- `check_links.py` also names a file an enumerating README has stopped listing. The review index
  gained its three missing rows, links on every row, and a pin per post-rule review
- `CONTRIBUTING.md` stopped restating runbook §3 and §6; its copy listed three of the five procedures,
  so translations and images had dropped out of that path. `CHANGELOG.md` gained the five unlogged
  changes and, in runbook §2, the rule saying when a line is required

**Known limits.**

- The realm ledger is a reviewed partition, not an enforced one. Nothing checks that every tracked
  path falls in exactly one realm, that a stated verifier runs, or that a no-authority realm is never
  cited as the reason for a rule. The skill names all three; none is written
- The index check covers one directory through a hardcoded row, deliberately. A second index is a
  second row, not a generalization written in advance
- `2026-09-16-commit-policy.md` carries no stamp although it was written after the rule. A review is
  never edited, so it cannot be repaired; its three values are in the index's provenance table instead
- A perturbation pass over the skill proposed re-carving its four duplication archetypes as two
  independent axes, after the responsible human rejected an unsupported correlation between
  propagation range and authorship. That re-carving is **not applied** and remains a proposal
- The owner graph is a reviewed model, not compiler enforcement. Private rounding, a shared stock
  directory, a hash helper located in records and shared dictionary/literal contracts remain seams
- Hooks are installed locally; a fresh clone still needs explicit installation, and local enforcement
  is not a remote required check. Native hook tests ran on Apple Git 2.39.3
- Local results are not GitHub Actions results. Ubuntu jobs, Windows installation, signed/unsigned
  remote PR behaviour and required checks have not been exercised
- A bundle pins Python and dependency versions and constrains artifact hashes; it does not make
  OS/CPU wheels or native decoders identical. Ordinary `uvx asrai==<version>` does not consume the
  repository lock, and `doctor --lock` reports drift without refusing
- Agreement bands and surface selection still need measured evidence or a sourced human decision.
  Synthetic estimator tests do not establish art-direction validity
- `measure` refuses above 12 Mpx; 16-bit colour PNGs are measured at 8-bit precision. A heavy vignette
  can bend shaded-mass direction into the observer band; the eight brightest blobs and at most sixteen
  subjects are measured. Cast-shadow evidence needs known subject pixels and cannot separate cast from
  form shadow inside one box
- Precedent retrieval, recipes, previews/apply, ingest/promotion, the pairwise bootstrap and external
  rendering remain unbuilt. Blender and Inkscape are not installed in the verified environment

**Waiting on a human.**

- Authorize remote publication, then activate and verify the remote gates and release path
- Decide whether the skill's duplication archetypes are re-carved as two axes, as proposed above
- Validate or explicitly adopt the lighting policy and surface selection with a recorded basis
- Review `docs/spec.md` and the artist brief
- Name native industry-language owners for `ko`, `ja` and `zh-Hans` and restamp their translations
- Decide `observer.mode` default and embedding egress (`spec.md` §10)
- Confirm external-tool versions on team machines before implementing their adapters

**Standing facts.**

- Inputs are immutable; outputs are new files; corpus records and prior checkpoint entries are
  append-only; dated reviews remain historical and unedited
- The runbook owns the judgment hierarchy and procedures. A conflicting implementation is defective
- Documents are code that generates code: a wrong line in an operating document is executed by every
  agent that reads it and fails nothing, which is why their arrangement is gated rather than trusted

---

## 2026-09-17 · verified at `ba31bc3` · Codex

Source repository: `https://github.com/Stdev17/asrai.git`; full baseline OID:
`ba31bc3676db359a1b8d96678b0beedffbf8ba14`. Verification includes the uncommitted policy
changes below; that commit names the baseline, not these pending edits.

**State.**

- phase: 1 (core and transports) and 1b (surface pass) remain complete; phase 2 is not implemented
- last_acceptance_passed: locked offline sync and the package suite pass on CPython 3.14.7.
  Links: 0 broken. Translation stamps: 0 current, 3 stale, 0 broken (existing advisory warnings).
  A fresh wheel install passes CLI, actual stdio MCP, bundled data and input preservation;
  its local bundle is `/private/tmp/revision-ref-policy-20260917/wheel`. Executed document commands
  resolve actual commits in both repositories. A disposable Git history verifies a real prefix
  collision, missing-source refusal, frozen snapshot reads and committed/index/worktree drift,
  including staged and unstaged edits that cancel in the combined working-tree diff
- in_progress: revision-reference policy is applied locally; commit/integration and remote CI,
  DCO bootstrap, required-check activation and release publication remain outside this change
- next_slice: when remote publication is authorized, land the reviewed DCO workflow/checker on the
  remote default branch, exercise signed and unsigned PR cases, require the documented CI checks,
  and attach the verified install bundle to a release. Phase 2 remains separate
- next_command: the landing checks in `runbook.md` §1 and exact commit range validation in §7
- working_tree: policy edits remain uncommitted; no branch, hook, remote setting or push was changed.
  The companion DeliveryKnight policy preserves its existing dirty/untracked documents and all
  other captured files byte-for-byte. This task does not commit that repository's pending work

**What changed.**

- The responsible human requested evaluation and adoption of compact revision references, then
  replaced the supporting attachment with `ref_hash_v2.md`. Runbook §5 owns the asrai procedure;
  AGENTS.md routes to it. DeliveryKnight conventions §8 owns its locally adopted equivalent,
  with AGENTS.md/CLAUDE.md routing and an appended insight-log decision
- Evidence citations retain repository/path/full-OID identity and use a Git-generated display
  with a minimum of 7 hex characters. Current-policy navigation remains live. Reuse reviews source
  changes; unresolved evidence holds the dependent claim. Existing machine hashes and historical
  records are not shortened or rewritten. The existing numeric-claim gate pins the display minimum
- No resolver, alias registry, automatic freshness gate, runtime behavior or asset changed.
  A missing policy phrase failed the numeric-claim check before the policy was added. The completed
  package suite passes. Token savings and model-quality effects were not measured

**Known limits.**

- Citation freshness remains a contributor/reviewer procedure. Full OIDs do not retain Git objects;
  cited history must remain available. Raw Markdown can still expose full permalink targets
- The owner graph remains a reviewed model; private rounding, stock-directory coupling, a hash
  helper in records and shared dictionary/literal contracts remain existing seams
- Local hooks and local passing checks are not remote enforcement. Native hooks on newer Git,
  Ubuntu CI, Windows installation, remote signed/unsigned PR cases and required checks remain
  unverified. Numeric detection still has the coverage limits documented in conventions §5
- Install bundles constrain packages, not arbitrary OS/CPU/decoder identity. Ordinary `uvx` does
  not consume the repository lock; doctor drift refusal and complete per-run stamps remain planned
- Lighting bands and surface selection still need measured evidence or sourced human adoption.
  Image bounds, reduced precision for 16-bit color, vignette/transfer-function sensitivity, bounded
  emitter/subject proposals, bright-paint ambiguity and neighborhood-dependent spill remain
- Shadow evidence still needs known subject pixels; one box cannot separate cast from form shadow
  or judge a flat subject. A baked checkerboard remains insufficient alpha evidence
- Precedent retrieval, recipes, previews/apply, ingest/promotion, pairwise bootstrap and external
  rendering remain unbuilt. Blender/Inkscape installation was not rechecked in this documentation task

**Waiting on a human.**

- Authorize remote publication, then activate and verify the remote gates and release path
- Validate or explicitly adopt/replace lighting policy and surface selection with a recorded basis
- Review `docs/spec.md` and the artist brief
- Name native industry-language owners for `ko`, `ja` and `zh-Hans` and review/restamp the README
  translations; shipped locale translations also remain unconfirmed

---

## 2026-09-16 · verified at `efe9802` · Codex

The revision above is the fast-forwarded main tree verified before this status-only entry.
The responsible human authorized local main integration and worktree cleanup in this task.

**State.**

- phase: 1 (core and transports) and 1b (surface pass) remain complete; phase 2 is not implemented
- last_acceptance_passed: 61 tests on CPython 3.14.7 in main, after locked editable installation;
  the same 61 tests passed in the linked worktree before integration. Links: 0 broken. Translation
  stamps: 0 current, 3 stale, 0 broken (advisory). A fresh wheel install passes CLI, actual stdio MCP,
  bundled data and input preservation. dist/repro-main-integration records clean source efe9802.
  The exact incoming commit range passes commit policy. Earlier entries retain Python 3.11,
  independent skill/graph review, source-hash approval and negative-hash installation evidence
- in_progress: local hardening and main integration are complete; remote CI execution, DCO bootstrap
  and required-check activation remain unverified
- next_slice: when remote publication is authorized, land the reviewed DCO workflow/checker on the
  remote default branch, exercise signed and unsigned PR cases, then require
  `Checks (Python 3.11)`, `Checks (Python 3.14)` and `DCO`. Attach the exact verified install bundle to
  a release. Phase 2 remains separate: recipes, adapters, alpha policy, recipe hashes, preview/apply/diff
- next_command: the landing checks in `runbook.md` §1 and commit range validation in §7
- working_tree: main is the only registered worktree. The fully merged codex/oss-hardening branch
  and /private/tmp/asrai-oss-hardening worktree were removed; prune leaves no stale registration.
  Main uses core.hooksPath=tools/hooks through worktree-specific Git config. No remote was pushed

**What landed.**

- Main fast-forwarded from 149656a to efe9802 without rewriting the accepted commits. Its native
  hooks are active. A sandbox DNS failure during editable installation was resolved by running the
  locked installation with network permission; the subsequent main tests passed before cleanup
- The original untracked checker and commit-msg hook are preserved byte-for-byte under
  scratch/main-integration-20260916/tools/, with original-tools.sha256.json. All 30 saved distribution
  artifacts moved to dist/hardening-worktree/ with their hashes checked before and after; the
  relocation manifest is scratch/main-integration-20260916/relocated-dist.sha256.json.
  Historical artifact metadata and prior checkpoint entries retain their original paths and bytes

- A repository development skill applies the runbook, conventions and signature-only owner graph.
  The product asset-use skill and runtime behavior are unchanged. Conventions now hold the human's
  single-skill scope review at 10 owners and diagram-boundary signal above 10 nodes; claims pin both
  values. The existing typed commit policy remains authoritative, including exact Owners, Values,
  source provenance and scoped deviations. DeliveryKnight's older commit convention is not imported
- The graph identifies 6 core owners and includes Python and data-contract dependencies. Independent
  review caught config, scale and term-ID coupling that an import-only view missed. The package README
  routes to this graph instead of keeping a competing picture. No new subsystem or runtime API is added
- The responsible human authorized this copy's uncommitted DeliveryKnight source to use its exact
  content hash in Source with an explicit Deviation. The dated adaptation review records that scope
  and the full hash; it does not claim the source file existed in DeliveryKnight's HEAD. DeliveryKnight
  remains unchanged; asrai now contains the adopted changes on main

- Asrai-native Owners and conditional trailers replace the supplied Unity policy. Failed Git lookups
  remain errors; disposable histories replace foreign commit ids. `commit-msg` validates structure,
  and the prepared reference transaction checks the actual first-parent diff before a branch moves.
  Existing subject policy is propagated through conventions, runbook and contribution guidance
- The original hardening commit `e51d61b` was reworded as `ea6ae95` through the installed hooks. Its
  tree stayed exactly `0840ce03d81e90438158c5f5be3459502fd1b32e`. Its message now names every owner;
  inherited history was not rewritten. The policy rationale records the supplied files' actual byte
  provenance without inventing a source revision for untracked files
- Runbook §1 continues to own judgment authority: explicit responsible human decisions,
  human-maintained documents, derived specs, then executable code/tests. A conflicting implementation
  is defective. Spec, conventions, contribution guidance and the docs index route through that rule
- Operative spec, skill, lighting comments and shipped surfaces mark unsupported alignment and
  suspicion claims as unverified policy. Existing cutoffs and selected surfaces are not newly approved
  magnitudes. Numeric behavior, fixture images and expected fixture bytes remain unchanged
- Fixture tests enforce byte equality using the generator's shared serialization. The wheel checker
  derives an install bundle from `uv.lock`, with hashes, Python version, source and environment
  evidence; installed CLI and MCP operate away from the editable checkout. Runbook §9 covers setup
- CI runs locked checks on Python 3.11 and 3.14 and uploads verified install bundles. DCO remains a
  trusted-default-branch workflow: proposed commits are data and the fixed pre-adoption history is
  exempt. Local schema hooks are not a remote gate. The PR template and changelog remain in place

**Known limits.**

- The owner graph is a reviewed model, not compiler enforcement. Private rounding, a shared stock
  directory, a hash helper located in records, and shared dictionary/literal contracts remain visible
  seams. They are not repaired by this documentation change. Readability and owner count do not prove
  product scope or artistic validity; future independent responsibilities need the human scope review

- Main's hooks are installed locally; a fresh clone still needs explicit hook installation.
  Local enforcement is not a remote required check. No remote repository setting has changed
- Native hook tests ran on Apple Git 2.39.3. Direct protocol regression cases cover newer Git's
  symbolic-reference rows, including detached-HEAD transitions; native execution on newer Git is
  not yet verified. Hooks cover new local commit objects; exact range review still covers reachable
  history. Numeric detection covers documented literal fields, while other numbers, copying,
  causal Fixes and human exception authority remain author/reviewer obligations

- Local passing results are not GitHub Actions results. Ubuntu jobs, Windows installation commands,
  signed/unsigned remote PR behavior and required checks have not yet been exercised. The DCO workflow
  cannot protect its own initial adoption; that needs explicit review before it becomes trusted policy
- A bundle pins Python and dependency versions and constrains artifact hashes. It does not make
  OS/CPU-specific wheels or native decoders identical. Both local installations used Pillow 12.3.0
  with libjpeg-turbo 3.1.4.1; NumPy was 2.4.6 on Python 3.11 and 2.5.3 on Python 3.14, as selected by
  the lock's markers. JPEG fixture drift must be investigated, never hidden by invented tolerances
- Ordinary `uvx asrai==<version>` does not consume the repository lock. `doctor --lock` records drift;
  automatic strict refusal and per-run complete environment stamps remain planned. Install bundles
  are local/CI artifacts until attached to a release
- Agreement bands and surface selection still need measured evidence or an explicit, sourced human
  decision. Synthetic estimator tests do not establish art-direction validity
- `measure` refuses above 12 Mpx; 16-bit color PNGs are measured at 8-bit precision, while 16-bit grey
  is rescaled. A 4K capture fits; 8K does not
- A heavy vignette can bend shaded-mass direction into the observer band; a vignette can also dim a
  border emitter below the global proposal floor. The eight brightest blobs and at most sixteen
  subjects are measured, not every possible source or object
- The absolute emitter floor depends on the transfer function; its basis is reported, not corrected.
  Bright paint is proposed as a possible emitter and a bright painted band can supply the highlight
- Spill depends on the neighborhood: a real lamp by a lit floor and dark wall can read negative.
  Spill and receivers are both considered, and an unmeasurable neighborhood remains unknown
- Cast-shadow evidence needs known subject pixels (a mask or file alpha), cannot separate cast from
  form shadow inside one box, and cannot judge a flat subject. A baked checkerboard is not alpha;
  request the original asset instead of interpreting the preview as the asset
- Precedent retrieval, recipes, previews/apply, ingest/promotion, pairwise bootstrap and external
  rendering remain unbuilt. Blender and Inkscape are not installed in the verified local environment

**Waiting on a human.**

- Authorize remote publication, then activate and verify the remote gates and release path
- Validate or explicitly adopt/replace the lighting policy and surface selection with a recorded basis
- Review `docs/spec.md` and the artist brief
- Name native industry-language owners for `ko`, `ja` and `zh-Hans` and review/restamp their README
  translations; the shipped locale translations also remain unconfirmed
- Decide `observer.mode` default and embedding egress (`spec.md` §10)
- Confirm external-tool versions on team machines before implementing their adapters

**Standing facts.**

- Inputs are immutable; output files are new; corpus records and prior checkpoint entries are
  append-only. Dated reviews remain historical. All prior checkpoint and review bytes are preserved
- Spec §1 retains the three intended readers and `surfaces.v1` retains its measurement/evidence/
  observer distinction. Tests show implementation behavior, not artistic approval
- The runbook owns hierarchy and procedures; the docs index routes to the current sources. Scratch
  stays outside tracked documentation, under the already permitted ignored names

---

## 2026-09-16 · verified at `78266a1` · Codex

The revision above is the inspected hardening base; acceptance includes this entry's development-skill
and architecture changes in `codex/oss-hardening`. The commit containing this entry identifies those changes.

**State.**

- phase: 1 (core and transports) and 1b (surface pass) remain complete; phase 2 is not implemented
- last_acceptance_passed: 61 tests on CPython 3.11.9 and 3.14.7, macOS 14.6.1 arm64. Package,
  corpus, fixture-byte and real Git-hook checks pass. Links: 0 broken. Translation stamps: 0 current,
  3 stale, 0 broken (advisory). A fresh wheel install passes CLI, actual stdio MCP, bundled data and
  input preservation on CPython 3.14.7; dist/repro-owner-skill records base 78266a1 with the worktree
  changes present. The development skill passes its format validator and independent application
  scenarios for exactly 10 owners, hidden owners behind a facade, and pure helpers without new
  invariants. Source review checks signatures and data contracts; the rendered graph is inspected
  at a 900 px content width. Earlier entries retain the cross-version wheel and negative-hash proof
- in_progress: local hardening, commit policy and development conventions are ready for integration; remote CI execution,
  DCO bootstrap and required-check activation remain unverified
- next_slice: integrate the branch and local hook adoption, land the reviewed DCO workflow/checker on
  the remote default branch, exercise signed and unsigned PR cases, then require
  `Checks (Python 3.11)`, `Checks (Python 3.14)` and `DCO`. A release needs its successful run's exact
  install bundle attached. Phase 2 follows separately: recipes, adapters, alpha policy, recipe hashes,
  preview/apply/diff (`spec.md` §8)
- next_command: the landing checks in `runbook.md` §1 and commit range validation in §7
- working_tree: `codex/oss-hardening` contains the adopted tools. Git's worktree-specific config is
  enabled and `core.hooksPath=tools/hooks` is set only here. Main's tracked and untracked file bytes
  are unchanged; no merge, remote branch, release or repository setting was published

**What landed.**

- A repository development skill applies the runbook, conventions and signature-only owner graph.
  The product asset-use skill and runtime behavior are unchanged. Conventions now hold the human's
  single-skill scope review at 10 owners and diagram-boundary signal above 10 nodes; claims pin both
  values. The existing typed commit policy remains authoritative, including exact Owners, Values,
  source provenance and scoped deviations. DeliveryKnight's older commit convention is not imported
- The graph identifies 6 core owners and includes Python and data-contract dependencies. Independent
  review caught config, scale and term-ID coupling that an import-only view missed. The package README
  routes to this graph instead of keeping a competing picture. No new subsystem or runtime API is added
- The responsible human authorized this copy's uncommitted DeliveryKnight source to use its exact
  content hash in Source with an explicit Deviation. The dated adaptation review records that scope
  and the full hash; it does not claim the source file existed in DeliveryKnight's HEAD. DeliveryKnight
  and the main asrai checkout are unchanged

- Asrai-native Owners and conditional trailers replace the supplied Unity policy. Failed Git lookups
  remain errors; disposable histories replace foreign commit ids. `commit-msg` validates structure,
  and the prepared reference transaction checks the actual first-parent diff before a branch moves.
  Existing subject policy is propagated through conventions, runbook and contribution guidance
- The original hardening commit `e51d61b` was reworded as `ea6ae95` through the installed hooks. Its
  tree stayed exactly `0840ce03d81e90438158c5f5be3459502fd1b32e`. Its message now names every owner;
  inherited history was not rewritten. The policy rationale records the supplied files' actual byte
  provenance without inventing a source revision for untracked files
- Runbook §1 continues to own judgment authority: explicit responsible human decisions,
  human-maintained documents, derived specs, then executable code/tests. A conflicting implementation
  is defective. Spec, conventions, contribution guidance and the docs index route through that rule
- Operative spec, skill, lighting comments and shipped surfaces mark unsupported alignment and
  suspicion claims as unverified policy. Existing cutoffs and selected surfaces are not newly approved
  magnitudes. Numeric behavior, fixture images and expected fixture bytes remain unchanged
- Fixture tests enforce byte equality using the generator's shared serialization. The wheel checker
  derives an install bundle from `uv.lock`, with hashes, Python version, source and environment
  evidence; installed CLI and MCP operate away from the editable checkout. Runbook §9 covers setup
- CI runs locked checks on Python 3.11 and 3.14 and uploads verified install bundles. DCO remains a
  trusted-default-branch workflow: proposed commits are data and the fixed pre-adoption history is
  exempt. Local schema hooks are not a remote gate. The PR template and changelog remain in place

**Known limits.**

- The owner graph is a reviewed model, not compiler enforcement. Private rounding, a shared stock
  directory, a hash helper located in records, and shared dictionary/literal contracts remain visible
  seams. They are not repaired by this documentation change. Readability and owner count do not prove
  product scope or artistic validity; future independent responsibilities need the human scope review

- Hook enforcement is installed only in the adopted hardening worktree. The main checkout still has
  the preserved, untracked supplied checker and no active hook path. Integrating the branch must
  reconcile those files and install the tracked hooks there; no remote setting has changed
- Native hook tests ran on Apple Git 2.39.3. Direct protocol regression cases cover newer Git's
  symbolic-reference rows, including detached-HEAD transitions; native execution on newer Git is
  not yet verified. Hooks cover new local commit objects; exact range review still covers reachable
  history. Numeric detection covers documented literal fields, while other numbers, copying,
  causal Fixes and human exception authority remain author/reviewer obligations

- Local passing results are not GitHub Actions results. Ubuntu jobs, Windows installation commands,
  signed/unsigned remote PR behavior and required checks have not yet been exercised. The DCO workflow
  cannot protect its own initial adoption; that needs explicit review before it becomes trusted policy
- A bundle pins Python and dependency versions and constrains artifact hashes. It does not make
  OS/CPU-specific wheels or native decoders identical. Both local installations used Pillow 12.3.0
  with libjpeg-turbo 3.1.4.1; NumPy was 2.4.6 on Python 3.11 and 2.5.3 on Python 3.14, as selected by
  the lock's markers. JPEG fixture drift must be investigated, never hidden by invented tolerances
- Ordinary `uvx asrai==<version>` does not consume the repository lock. `doctor --lock` records drift;
  automatic strict refusal and per-run complete environment stamps remain planned. Install bundles
  are local/CI artifacts until attached to a release
- Agreement bands and surface selection still need measured evidence or an explicit, sourced human
  decision. Synthetic estimator tests do not establish art-direction validity
- `measure` refuses above 12 Mpx; 16-bit color PNGs are measured at 8-bit precision, while 16-bit grey
  is rescaled. A 4K capture fits; 8K does not
- A heavy vignette can bend shaded-mass direction into the observer band; a vignette can also dim a
  border emitter below the global proposal floor. The eight brightest blobs and at most sixteen
  subjects are measured, not every possible source or object
- The absolute emitter floor depends on the transfer function; its basis is reported, not corrected.
  Bright paint is proposed as a possible emitter and a bright painted band can supply the highlight
- Spill depends on the neighborhood: a real lamp by a lit floor and dark wall can read negative.
  Spill and receivers are both considered, and an unmeasurable neighborhood remains unknown
- Cast-shadow evidence needs known subject pixels (a mask or file alpha), cannot separate cast from
  form shadow inside one box, and cannot judge a flat subject. A baked checkerboard is not alpha;
  request the original asset instead of interpreting the preview as the asset
- Precedent retrieval, recipes, previews/apply, ingest/promotion, pairwise bootstrap and external
  rendering remain unbuilt. Blender and Inkscape are not installed in the verified local environment

**Waiting on a human.**

- Review and integrate this local branch, reconcile the main checkout's untracked checker, install
  its hooks there, then activate and verify the remote gates and release path
- Validate or explicitly adopt/replace the lighting policy and surface selection with a recorded basis
- Review `docs/spec.md` and the artist brief
- Name native industry-language owners for `ko`, `ja` and `zh-Hans` and review/restamp their README
  translations; the shipped locale translations also remain unconfirmed
- Decide `observer.mode` default and embedding egress (`spec.md` §10)
- Confirm external-tool versions on team machines before implementing their adapters

**Standing facts.**

- Inputs are immutable; output files are new; corpus records and prior checkpoint entries are
  append-only. Dated reviews remain historical. All prior checkpoint and review bytes are preserved
- Spec §1 retains the three intended readers and `surfaces.v1` retains its measurement/evidence/
  observer distinction. Tests show implementation behavior, not artistic approval
- The runbook owns hierarchy and procedures; the docs index routes to the current sources. Scratch
  stays outside tracked documentation, under the already permitted ignored names

---

## 2026-09-16 · verified at `ea6ae95` · Codex

The revision above is the inspected hardening base; acceptance includes this entry's commit-policy
changes in `codex/oss-hardening`. The commit containing this entry identifies those changes.

**State.**

- phase: 1 (core and transports) and 1b (surface pass) remain complete; phase 2 is not implemented
- last_acceptance_passed: 61 tests on CPython 3.11.9 and 3.14.7, macOS 14.6.1 arm64. Real temporary Git
  histories accept/reject new commits, root commits, message-only and staged amendments, owner-changing
  renames, merges and linked worktrees; missing/shallow revisions and malformed trailers fail. Direct
  symbolic-reference protocol cases pass. Package, corpus and fixture-byte checks pass unchanged.
  Links: 0 broken. Translation stamps: 0 current, 3 stale, 0 broken (advisory). A fresh wheel install
  passes CLI, actual stdio MCP, stock/locale/skill loading and input preservation on CPython 3.14.7.
  The prior hardening entry retains the same runtime's cross-version wheel and negative-hash evidence
- in_progress: local hardening and commit-policy work is ready for integration; remote CI execution,
  DCO bootstrap and required-check activation remain unverified
- next_slice: integrate the branch and local hook adoption, land the reviewed DCO workflow/checker on
  the remote default branch, exercise signed and unsigned PR cases, then require
  `Checks (Python 3.11)`, `Checks (Python 3.14)` and `DCO`. A release needs its successful run's exact
  install bundle attached. Phase 2 follows separately: recipes, adapters, alpha policy, recipe hashes,
  preview/apply/diff (`spec.md` §8)
- next_command: the landing checks in `runbook.md` §1 and commit range validation in §7
- working_tree: `codex/oss-hardening` contains the adopted tools. Git's worktree-specific config is
  enabled and `core.hooksPath=tools/hooks` is set only here. Main's tracked and untracked file bytes
  are unchanged; no merge, remote branch, release or repository setting was published

**What landed.**

- Asrai-native Owners and conditional trailers replace the supplied Unity policy. Failed Git lookups
  remain errors; disposable histories replace foreign commit ids. `commit-msg` validates structure,
  and the prepared reference transaction checks the actual first-parent diff before a branch moves.
  Existing subject policy is propagated through conventions, runbook and contribution guidance
- The original hardening commit `e51d61b` was reworded as `ea6ae95` through the installed hooks. Its
  tree stayed exactly `0840ce03d81e90438158c5f5be3459502fd1b32e`. Its message now names every owner;
  inherited history was not rewritten. The policy rationale records the supplied files' actual byte
  provenance without inventing a source revision for untracked files
- Runbook §1 continues to own judgment authority: explicit responsible human decisions,
  human-maintained documents, derived specs, then executable code/tests. A conflicting implementation
  is defective. Spec, conventions, contribution guidance and the docs index route through that rule
- Operative spec, skill, lighting comments and shipped surfaces mark unsupported alignment and
  suspicion claims as unverified policy. Existing cutoffs and selected surfaces are not newly approved
  magnitudes. Numeric behavior, fixture images and expected fixture bytes remain unchanged
- Fixture tests enforce byte equality using the generator's shared serialization. The wheel checker
  derives an install bundle from `uv.lock`, with hashes, Python version, source and environment
  evidence; installed CLI and MCP operate away from the editable checkout. Runbook §9 covers setup
- CI runs locked checks on Python 3.11 and 3.14 and uploads verified install bundles. DCO remains a
  trusted-default-branch workflow: proposed commits are data and the fixed pre-adoption history is
  exempt. Local schema hooks are not a remote gate. The PR template and changelog remain in place

**Known limits.**

- Hook enforcement is installed only in the adopted hardening worktree. The main checkout still has
  the preserved, untracked supplied checker and no active hook path. Integrating the branch must
  reconcile those files and install the tracked hooks there; no remote setting has changed
- Native hook tests ran on Apple Git 2.39.3. Direct protocol regression cases cover newer Git's
  symbolic-reference rows, including detached-HEAD transitions; native execution on newer Git is
  not yet verified. Hooks cover new local commit objects; exact range review still covers reachable
  history. Numeric detection covers documented literal fields, while other numbers, copying,
  causal Fixes and human exception authority remain author/reviewer obligations

- Local passing results are not GitHub Actions results. Ubuntu jobs, Windows installation commands,
  signed/unsigned remote PR behavior and required checks have not yet been exercised. The DCO workflow
  cannot protect its own initial adoption; that needs explicit review before it becomes trusted policy
- A bundle pins Python and dependency versions and constrains artifact hashes. It does not make
  OS/CPU-specific wheels or native decoders identical. Both local installations used Pillow 12.3.0
  with libjpeg-turbo 3.1.4.1; NumPy was 2.4.6 on Python 3.11 and 2.5.3 on Python 3.14, as selected by
  the lock's markers. JPEG fixture drift must be investigated, never hidden by invented tolerances
- Ordinary `uvx asrai==<version>` does not consume the repository lock. `doctor --lock` records drift;
  automatic strict refusal and per-run complete environment stamps remain planned. Install bundles
  are local/CI artifacts until attached to a release
- Agreement bands and surface selection still need measured evidence or an explicit, sourced human
  decision. Synthetic estimator tests do not establish art-direction validity
- `measure` refuses above 12 Mpx; 16-bit color PNGs are measured at 8-bit precision, while 16-bit grey
  is rescaled. A 4K capture fits; 8K does not
- A heavy vignette can bend shaded-mass direction into the observer band; a vignette can also dim a
  border emitter below the global proposal floor. The eight brightest blobs and at most sixteen
  subjects are measured, not every possible source or object
- The absolute emitter floor depends on the transfer function; its basis is reported, not corrected.
  Bright paint is proposed as a possible emitter and a bright painted band can supply the highlight
- Spill depends on the neighborhood: a real lamp by a lit floor and dark wall can read negative.
  Spill and receivers are both considered, and an unmeasurable neighborhood remains unknown
- Cast-shadow evidence needs known subject pixels (a mask or file alpha), cannot separate cast from
  form shadow inside one box, and cannot judge a flat subject. A baked checkerboard is not alpha;
  request the original asset instead of interpreting the preview as the asset
- Precedent retrieval, recipes, previews/apply, ingest/promotion, pairwise bootstrap and external
  rendering remain unbuilt. Blender and Inkscape are not installed in the verified local environment

**Waiting on a human.**

- Review and integrate this local branch, reconcile the main checkout's untracked checker, install
  its hooks there, then activate and verify the remote gates and release path
- Validate or explicitly adopt/replace the lighting policy and surface selection with a recorded basis
- Review `docs/spec.md` and the artist brief
- Name native industry-language owners for `ko`, `ja` and `zh-Hans` and review/restamp their README
  translations; the shipped locale translations also remain unconfirmed
- Decide `observer.mode` default and embedding egress (`spec.md` §10)
- Confirm external-tool versions on team machines before implementing their adapters

**Standing facts.**

- Inputs are immutable; output files are new; corpus records and prior checkpoint entries are
  append-only. Dated reviews remain historical. All prior checkpoint and review bytes are preserved
- Spec §1 retains the three intended readers and `surfaces.v1` retains its measurement/evidence/
  observer distinction. Tests show implementation behavior, not artistic approval
- The runbook owns hierarchy and procedures; the docs index routes to the current sources. Scratch
  stays outside tracked documentation, under the already permitted ignored names

---

## 2026-09-16 · verified at `149656a` · Codex

The revision above is the inspected base; acceptance below includes this entry's hardening changes
in `codex/oss-hardening`. The commit containing this entry identifies those changes.

**State.**

- phase: 1 (core and transports) and 1b (surface pass) remain complete; phase 2 is not implemented
- last_acceptance_passed: 59 tests on CPython 3.11.9 and 3.14.7, macOS 14.6.1 arm64. The same committed
  fixture images and expected JSON pass actual UTF-8 byte comparison on both environments. Links:
  0 broken. Translation stamps: valid, with README translations becoming stale when this source edit
  is committed; staleness remains advisory. Fresh wheel installs on both Python versions pass bundled
  stock hashes, locale and skill loading, CLI measurement, real stdio MCP measurement and input-byte
  preservation. An altered wheel hash is refused; an editable source leak and a serialized fixture-byte
  mismatch are detected. DCO accepts signed new commits and rejects unsigned, body-only, malformed,
  missing-history and shallow-history cases. Both workflows pass actionlint 1.7.12 locally
- in_progress: local implementation complete; remote CI execution, DCO bootstrap and required-check
  activation remain unverified
- next_slice: land the reviewed DCO workflow/checker on the remote default branch, exercise signed and
  unsigned PR cases, then require `Checks (Python 3.11)`, `Checks (Python 3.14)` and `DCO`. A release
  needs its successful run's exact install bundle attached. Phase 2 follows separately: recipes,
  adapters, alpha policy, recipe hashes, preview/apply/diff (`spec.md` §8)
- next_command: `uv sync --locked`, then the landing checks in `runbook.md` §1
- working_tree: `codex/oss-hardening` is based on `149656a`; the original `main` checkout is unchanged.
  No remote branch, release or repository setting was changed by this slice

**What landed.**

- Runbook §1 owns judgment authority: explicit responsible human decisions, human-maintained
  documents, derived specs, then executable code/tests. A conflicting implementation is defective.
  Spec, conventions, contribution guidance and the docs index route through that rule. A filename,
  AI authorship or a passing test does not establish human adoption
- Operative spec, skill, lighting comments and shipped surfaces stop presenting the unsupported
  hand-drawn alignment and suspicion claims as evidence. Existing agreement cutoffs and the selected
  surfaces remain unverified policy, not newly approved magnitudes. Numeric behavior is unchanged;
  the stock manifest is refreshed. Old reviews are preserved; the dated authority/release rationale
  records this decision and supersedes the historical index's stale checkpoint-writing description
- Fixture tests now enforce the byte-equality contract through the generator's shared serialization.
  No fixture image or expected output changed. Documentation states the tested decoder/toolchain
  boundary rather than promising equality on arbitrary machines
- `tools/check_wheel.py` builds a wheel, exports hashed runtime requirements from `uv.lock`, adds the
  wheel hash and Python version, and installs into an isolated environment for CLI/MCP/data checks.
  The generated bundle includes platform/decoder, source revision and dirty-state evidence; it is not
  a second maintained lockfile. Runbook §9 covers end-user installation, registration and rollback
- CI runs locked checks on Python 3.11 and 3.14 and uploads each job's verified install bundle. DCO is
  a separate, trusted-default-branch `pull_request_target` workflow: PR commits are fetched as data,
  never checked out or executed there. The fixed pre-adoption history is exempt; commit dates cannot
  grant an exemption. A PR template and hand-written `CHANGELOG.md` complete the initial gate

**Known limits.**

- Local passing results are not GitHub Actions results. Ubuntu jobs, Windows installation commands,
  signed/unsigned remote PR behavior and required checks have not yet been exercised. The DCO workflow
  cannot protect its own initial adoption; that needs explicit review before it becomes trusted policy
- A bundle pins Python and dependency versions and constrains artifact hashes. It does not make
  OS/CPU-specific wheels or native decoders identical. Both local installations used Pillow 12.3.0
  with libjpeg-turbo 3.1.4.1; NumPy was 2.4.6 on Python 3.11 and 2.5.3 on Python 3.14, as selected by
  the lock's markers. JPEG fixture drift must be investigated, never hidden by invented tolerances
- Ordinary `uvx asrai==<version>` does not consume the repository lock. `doctor --lock` records drift;
  automatic strict refusal and per-run complete environment stamps remain planned. Install bundles
  are local/CI artifacts until attached to a release
- Agreement bands and surface selection still need measured evidence or an explicit, sourced human
  decision. Synthetic estimator tests do not establish art-direction validity
- `measure` refuses above 12 Mpx; 16-bit color PNGs are measured at 8-bit precision, while 16-bit grey
  is rescaled. A 4K capture fits; 8K does not
- A heavy vignette can bend shaded-mass direction into the observer band; a vignette can also dim a
  border emitter below the global proposal floor. The eight brightest blobs and at most sixteen
  subjects are measured, not every possible source or object
- The absolute emitter floor depends on the transfer function; its basis is reported, not corrected.
  Bright paint is proposed as a possible emitter and a bright painted band can supply the highlight
- Spill depends on the neighborhood: a real lamp by a lit floor and dark wall can read negative.
  Spill and receivers are both considered, and an unmeasurable neighborhood remains unknown
- Cast-shadow evidence needs known subject pixels (a mask or file alpha), cannot separate cast from
  form shadow inside one box, and cannot judge a flat subject. A baked checkerboard is not alpha;
  request the original asset instead of interpreting the preview as the asset
- Precedent retrieval, recipes, previews/apply, ingest/promotion, pairwise bootstrap and external
  rendering remain unbuilt. Blender and Inkscape are not installed in the verified local environment

**Waiting on a human.**

- Review and integrate this local branch, then activate and verify the remote gates and release path
- Validate or explicitly adopt/replace the lighting policy and surface selection with a recorded basis
- Review `docs/spec.md` and the artist brief
- Name native industry-language owners for `ko`, `ja` and `zh-Hans` and review/restamp their README
  translations; the shipped locale translations also remain unconfirmed
- Decide `observer.mode` default and embedding egress (`spec.md` §10)
- Confirm external-tool versions on team machines before implementing their adapters

**Standing facts.**

- Inputs are immutable; output files are new; corpus records and prior checkpoint entries are
  append-only. Dated reviews remain historical. All prior checkpoint and review bytes are preserved
- Spec §1 retains the three intended readers and `surfaces.v1` retains its measurement/evidence/
  observer distinction. Tests show implementation behavior, not artistic approval
- The runbook owns hierarchy and procedures; the docs index routes to the current sources. Scratch
  stays outside tracked documentation, under the already permitted ignored names

---

## 2026-09-15 · verified at `75ad625` · Shelby Yoon

**State.**

- phase: 1 (core and transports) done, fixtures committed; 1b surface pass (`surfaces.v1`,
  `light_ledger`) done
- last_acceptance_passed: 58 tests on 3.14 (vocab search/get/locales, lint rules, light_ledger direction/
  emitters/key fit/form/answers/depth/modes/noise floor/mirror/capture/malformed/a light nothing answers
  to/a shadow on the wrong side/production perturbations/subject masks, surfaces map onto vocabulary and
  skill, measure determinism incl. 16-bit grey, record validation incl. layer rules, doctor lock/drift,
  MCP tools in-process and over stdio and inside their token budget, malformed-input refusal at both trust
  boundaries, six measure fixtures byte-equal, corpus validators inside pytest, every registered number
  matching its claim in every file that states it — `surfaces.v1.json` now among them); `check_links`
  0 broken; `check_translations` 3 current, 0 stale
- in_progress: nothing
- next_slice: phase 2 — recipes, tool adapters, alpha policy, recipe hashes, preview/apply/diff
  (`spec.md` §8). The CI gate: discovery done and all six of its questions answered; `.github/` is still
  unwritten — the pull-request template, the DCO check and `CHANGELOG.md` are the next round
- next_command: `uv run pytest`
- working_tree: `main` carries phase 1 (tag v0.1.0), AGENTS.md, the surface pass and the documentation
  rounds; 31 commits ahead of `origin/main`, nothing pushed. Phase 2 starts in a separate git worktree,
  because this checkout is shared with another session

**What landed.**

- **Two commits this entry owes.** `853e11b` made this file append-only and `1ecfc08` refused links
  that climb above the repository root. Both landed after the entry below was verified and neither got
  an entry: the append rule was broken by the commit after the one that wrote it. This entry is the
  correction, and nothing below it is changed
- **The three open gate questions are decided** (below). `docs/i18n/README.md` gained an owner table,
  `tools/check_translations.py` says staleness never fails by decision, and `CONTRIBUTING.md` and the
  runbook carry the sign-off
- **A forensic pass over all thirty commits** — the spec-perturbation probe run backwards: the message
  as the spec, the diff as the footprint, `git log -S` for the commit that planted each defect a later
  one fixed. Kept as an ignored experiment record, `docs/experiments/2026-09-15-boundary-forensics/`,
  never tracked; its numbers are in the decision below and nowhere else in the tree. What it changed
  here: runbook §7.6, `claims.json` anchoring 20 and 60 in `surfaces.v1.json`, and the known limit on
  unsourced numbers
- `.gitignore` covers `docs/experiments/`; runbook §3 and `AGENTS.md` name it beside the other scratch
  names. A copy of DeliveryKnight's `spec-perturbation` skill sits in the ignored `.claude/skills/`

**Decided today.**

- **A stale translation never blocks a merge.** A language is accepted with a named owner who reads it
  natively and answers for its staleness; none of `ko`, `ja`, `zh-Hans` has one yet and the table says
  so. The gate reports; a person holds
- **DCO.** Every commit from today carries `Signed-off-by` (`git commit -s`); no CLA; nothing
  retroactive — the thirty commits before it carry none
- **The changelog is hand-written**, not generated from commit messages. The file lands with the
  pull-request template round; until then no document names it
- **Each commit message names every owner its diff touches** (runbook §7.6). Basis, measured on this
  history — 28 authored commits, 31 defects a later commit said it found: defects planted did not track
  how far a commit went beyond its message (Spearman +0.15 against unstated owners, +0.04 with
  `91a4bc7` set aside) and did track size (+0.49 against files touched). Twenty of the 31 sat inside
  the intent the message stated. Across all 31, what found them was reading documents against code
  (11) and a registered number or a checker (8) — never a scope rule. The exception is cargo:
  `91a4bc7` carried 1,941 lines its message never named — three reviews, the playbook, the README and
  three tool scripts — and the five defects in them lived 11 to 27 commits, the longest in the history,
  because a reviewer reads what the message points at. The wall catches a worker leaving scope; this
  history's leaks were planted inside scope in the largest commits, so the rule that follows is the wall
  run backwards

**Known limits.**

- the byte-equal fixture gate is decoder-bound, and `flat.jpg` is the exposed one: perturbing its decode
  by ±1 on 0.1% of subpixels moves 2 of its 78 committed numbers (1% moves 10), landing on percentiles,
  which jump a whole quantisation step. Arithmetic is not the risk — the tightest of the 304 rounded
  values sits 9.8e-07 from a rounding boundary against float noise near 1e-16 — but PNG decoding is
  exact by definition and JPEG's is not, and `pillow>=12,<13` lets the bundled decoder move. A
  dependency patch release can turn a green change red under a message blaming the author
- `measure` refuses above 12 Mpx (~4 GB peak at ~320 B/px): a 4K capture fits, 8K does not
- 16-bit colour PNGs are measured at 8-bit precision; 16-bit grey is rescaled correctly
- a heavy vignette (0.55) bends a sprite's shaded mass by about 20 deg, out of the band the measurement
  settles and into the one the observer is asked. Light ones (0.15) cost under 9 deg
- a vignette also dims an emitter near the frame border below the proposal floor, which is global
  (0.6 x the 99th percentile): a neon sign at the edge of a graded screenshot is not proposed at all
- at most the eight brightest blobs are proposed and at most sixteen subjects measured; a frame with a
  dozen neon signs is read through its eight strongest
- the absolute emitter floor (`EMITTER_MIN_Y` 0.30 linear) is the one constant in the pass that a
  transfer function moves. On the pixel-art night reference it is the binding one and the relative floor
  sits at 0.298, so the two nearly tie; a darker frame would be chosen by an absolute level. Reported as
  `emitter_floor.basis` rather than corrected
- **four** numbers have no recorded basis: `DISAGREE_DEG = 60`, the assertion that hand-drawn scenes
  hold their key to roughly 10 deg, why the surface list is these ten
  (`review/2026-09-15-art-direction-rationale.md` §6), and — found by the forensic pass after that review
  was written — "suspicion starts near 18 deg (cosine 0.95)", stated in a `light.py` comment and in
  `surfaces.v1.json`'s `thresholds`, used by no code
- `surfaces.v1.json`'s `thresholds` is 1,582 characters of prose inside shipped data carrying eight
  numbers; nothing in the code reads the field, and `claims.json` sees only the two it now anchors there
  (20 and 60). The other six are held by nothing

**Waiting on a human.**

- the four unsourced numbers above: measure them, or demote each to a named choice with a date
- name an owner for each of `ko`, `ja` and `zh-Hans`, and confirm the three README translations against
  each language's industry wording
- write `.github/`: the pull-request template, the DCO check, and `CHANGELOG.md`
- review `docs/spec.md` and the artist brief
- decide `observer.mode` default and embedding egress (`spec.md` §10)
- confirm Blender/Inkscape versions on team machines (none installed on the dev machine)
- `light_ledger` proposes emitters from luminance alone: bright paint is proposed too, by design (the
  emissive question rejects it); the highlight of a subject with a bright painted band is that band
- spill reads the neighbourhood, so a real lamp mounted on a dark wall beside a lit floor can read
  negative; it is one of two tests (the other is receivers) and both must be empty before a light is
  called one the frame does not answer to
- `cast_shadow` measures where a subject's shaded mass sits against its lit side, which needs no emitter
  and judges a lone sprite; inside one box it cannot separate cast from form shadow, it is read only on
  a file with alpha (which is what says which pixels are the subject), and a subject too flat for either
  mass to carry a direction is `unknown`, never yes
- a flattened preview of a transparent sprite (the checkerboard baked into the pixels) is not the asset:
  `measure` reports `alpha_present` false and `light_ledger` proposes the checkerboard as emitters. Ask
  for the PNG with its alpha

**Standing facts.**

- design lens: `spec.md` §1 carries the three readers a feature must serve (no art training, an artist,
  an art director) and `surfaces.v1` carries `decided_by` per surface (measurement 2, evidence 4,
  observer 4), so coverage is read from the data rather than argued in prose
- repo docs: every tracked directory carries a README (`src/asrai`, `data`, `data/skill`, `data/stock`,
  `data/stock/examples`, `data/stock/locales`, `tests`, `tests/fixtures`, `tools`, `docs`, `docs/review`,
  `docs/i18n`), plus `CONTRIBUTING.md`, `docs/runbook.md` and a repository map in the root README.
  Mermaid carries the four structural diagrams so they diff as text. `docs/README.md` holds the
  authority order
- scratch never tracked: `*.scratch.md`, `scratch/`, `docs/experiments/`, `.claude/skills/`

---

## 2026-09-15 · verified at `a6b0537` · Shelby Yoon

**State.**

- phase: 1 (core and transports) done, fixtures committed; 1b surface pass (`surfaces.v1`,
  `light_ledger`) done
- last_acceptance_passed: 58 tests on 3.14, and the declared floor 3.11 was run today and passes
  (vocab search/get/locales, lint rules, light_ledger direction/emitters/key fit/form/answers/depth/
  modes/noise floor/mirror/capture/malformed/a light nothing answers to/a shadow on the wrong side/
  production perturbations/subject masks, surfaces map onto vocabulary and skill, measure determinism
  incl. 16-bit grey, record validation incl. layer rules, doctor lock/drift, MCP tools in-process and
  over stdio and inside their token budget, malformed-input refusal at both trust boundaries, six
  measure fixtures byte-equal, corpus validators inside pytest); `validate_stock` 21,675 checks;
  `review_locales` no defects
- in_progress: nothing
- next_slice: phase 2 — recipes, tool adapters, alpha policy, recipe hashes, preview/apply/diff
  (`spec.md` §8). The CI gate is a separate track, still at discovery
- next_command: `uv run pytest`
- working_tree: `main` carries phase 1 (tag v0.1.0), AGENTS.md, the surface pass and the documentation
  rounds. Phase 2 starts in a separate git worktree, because this checkout is shared with another session

**What landed.**

- **Translations exist.** `docs/i18n/{ko,ja,zh-Hans}/README.md`, each stamped on line 1 with the commit
  it was translated from; `tools/check_translations.py` reports drift with the intervening commit
  subjects and fails only on a stamp that is missing, malformed, or points at a source that does not
  exist or may never be translated. Staleness is reported, not enforced. The contract (`spec.md`,
  `conventions.md`, `SKILL.md`) and `review/` are never translated: a translated contract is a second
  source of truth. Numbers are the one place a translation is not free — the claims test finds mirrors
  from the English row and requires the same numeral, so **no translator edits `claims.json`**. All three
  are LLM-drafted and unconfirmed, flagged the way the locale bundles are
- **The link checker became real.** This file used to claim a link checker named in the CONTRIBUTING
  checklist; neither the script nor the checklist line existed. `tools/check_links.py` now does, and
  both `check_*` scripts are in the checklist. Neither runs inside `pytest`: what they check is a fact
  about this repository, not behaviour of the package a user installs
- **Two dated reviews**, because a rationale in a status file is a rationale that rots:
  `review/2026-09-15-ci-gate-discovery.md` and `review/2026-09-15-art-direction-rationale.md`. The
  surface pass's eight sources and the estimator noise floor moved into the second one
- **This file's write policy changed** to the one at the top, and `docs/runbook.md` was written so that
  an agent asked for a tour of this repository reaches the right answer without inferring it
- **Fixture provenance is recorded.** All six are generated by `tools/make_fixtures.py` and contain no
  third-party content; `tests/fixtures/README.md` now says so per image, and `CONTRIBUTING.md` requires
  it of any image a contribution adds

**Decided today.**

- **A rationale carries a stamp**: the date, the revision it was verified at, and the author. New
  reviews carry it inline; `review/README.md` carries it for the ones written before the rule, where it
  is recoverable from git
- **No ad-hoc status documents.** An agent working here does not create a plan, a summary, a progress
  note or a second checkpoint as a tracked file. Scratch goes outside the repository, or under a name
  `.gitignore` already covers (`*.scratch.md`, `scratch/`). The reason is the CI gate: a reviewer and a
  machine cannot tell an agent's working note from a documentation contribution, and every review meets
  one
- **A contributed image records where it came from and under what licence.** No reason was found not to,
  and the six fixtures cost nothing because they are synthetic
- **A held pull request is a state this project wants**, because holding is reversible and closing is
  not — the same argument as `unknown` being a hold in the data model
- **No second-approver gate yet.** At one author, `CODEOWNERS` would encode a bottleneck rather than a
  control; the project is early enough that being found matters more

**Known limits.**

- the byte-equal fixture gate is decoder-bound, and `flat.jpg` is the exposed one: perturbing its decode
  by ±1 on 0.1% of subpixels moves 2 of its 78 committed numbers (1% moves 10), landing on percentiles,
  which jump a whole quantisation step. Arithmetic is not the risk — the tightest of the 304 rounded
  values sits 9.8e-07 from a rounding boundary against float noise near 1e-16 — but PNG decoding is
  exact by definition and JPEG's is not, and `pillow>=12,<13` lets the bundled decoder move. A
  dependency patch release can turn a green change red under a message blaming the author
- `measure` refuses above 12 Mpx (~4 GB peak at ~320 B/px): a 4K capture fits, 8K does not
- 16-bit colour PNGs are measured at 8-bit precision; 16-bit grey is rescaled correctly
- a heavy vignette (0.55) bends a sprite's shaded mass by about 20 deg, out of the band the measurement
  settles and into the one the observer is asked. Light ones (0.15) cost under 9 deg
- a vignette also dims an emitter near the frame border below the proposal floor, which is global
  (0.6 x the 99th percentile): a neon sign at the edge of a graded screenshot is not proposed at all
- at most the eight brightest blobs are proposed and at most sixteen subjects measured; a frame with a
  dozen neon signs is read through its eight strongest
- the absolute emitter floor (`EMITTER_MIN_Y` 0.30 linear) is the one constant in the pass that a
  transfer function moves. On the pixel-art night reference it is the binding one and the relative floor
  sits at 0.298, so the two nearly tie; a darker frame would be chosen by an absolute level. Reported as
  `emitter_floor.basis` rather than corrected
- three art claims have no recorded basis at all: `DISAGREE_DEG = 60`, the assertion that hand-drawn
  scenes hold their key to roughly 10 deg, and why the surface list is these ten
  (`review/2026-09-15-art-direction-rationale.md` §6)

**Waiting on a human.**

- three CI-gate questions are still open: whether a stale translation blocks a merge, DCO or nothing,
  and whether the changelog is generated or hand-written
  (`review/2026-09-15-ci-gate-discovery.md` §8; the other three were answered above)
- the three unsourced art claims above: measure them, or demote them to a named choice with a date
- confirm the ko, ja and zh-Hans README translations against each language's industry wording
- review `docs/spec.md` and the artist brief
- decide `observer.mode` default and embedding egress (`spec.md` §10)
- confirm Blender/Inkscape versions on team machines (none installed on the dev machine)
- `light_ledger` proposes emitters from luminance alone: bright paint is proposed too, by design (the
  emissive question rejects it); the highlight of a subject with a bright painted band is that band
- spill reads the neighbourhood, so a real lamp mounted on a dark wall beside a lit floor can read
  negative; it is one of two tests (the other is receivers) and both must be empty before a light is
  called one the frame does not answer to
- `cast_shadow` measures where a subject's shaded mass sits against its lit side, which needs no emitter
  and judges a lone sprite; inside one box it cannot separate cast from form shadow, it is read only on
  a file with alpha (which is what says which pixels are the subject), and a subject too flat for either
  mass to carry a direction is `unknown`, never yes
- a flattened preview of a transparent sprite (the checkerboard baked into the pixels) is not the asset:
  `measure` reports `alpha_present` false and `light_ledger` proposes the checkerboard as emitters. Ask
  for the PNG with its alpha

**Standing facts.**

- design lens: `spec.md` §1 carries the three readers a feature must serve (no art training, an artist,
  an art director) and `surfaces.v1` carries `decided_by` per surface (measurement 2, evidence 4,
  observer 4), so coverage is read from the data rather than argued in prose
- repo docs: every tracked directory carries a README (`src/asrai`, `data`, `data/skill`, `data/stock`,
  `data/stock/examples`, `data/stock/locales`, `tests`, `tests/fixtures`, `tools`, `docs`, `docs/review`,
  `docs/i18n`), plus `CONTRIBUTING.md`, `docs/runbook.md` and a repository map in the root README.
  Mermaid carries the four structural diagrams so they diff as text. `docs/README.md` holds the
  authority order

---

## 2026-09-14 · verified at `cdf7802` · Shelby Yoon

**Audit — every README and doc read against the code and the schemas.**

- fixed, silent: a `capture.json` row without a usable `screen_bbox` was skipped without a word (four
  declared, one measured, no warning), and rows past the sixteen-subject cap were dropped the same way.
  Phase one now returns `capture` with declared, measured and every skipped row with its reason
- fixed, silent: an emitter answered `unknown` was treated as a rejection, so on one decoy scene naming
  e1 a lamp read fail while "I cannot tell" read pass and dropped the row entirely. `unknown` is a hold:
  it keeps a row as `unclassified` and holds `asset_cohesion` at warn. `paint` still rejects, because
  that is a judgment. The sibling verdict `unknown` became `unreadable`
- fixed, leaked at a boundary: `subjects[].mask` was reachable from neither the CLI (`--subject` took a
  bbox only) nor the MCP description, two commits after it shipped. The CLI form is now
  `ID=X,Y,W,H[,depth][@mask.png]` and the tool description names `mask`
- fixed, leaked at a boundary: `lint` requires nine conditional context keys (`baseline_ref`,
  `image_ref`/`grid_ref` + `resolution`, `viewBox`, `timebase.fps` + `clock`, `fov_axis` + `projection`,
  `shader_model`, and `metric`/`sequence` on the change). None was named in `spec.md`, `SKILL.md` or the
  tool schema, so they were discoverable only by failing. `SKILL.md` now carries the table and a test
  derives the key list from `vocab.py`, so it cannot go stale
- fixed, drifted: "twelve locale bundles" in three files against eleven; per-file test counts in
  `tests/README` summing to 36 against a suite of 51; `spec.md` §6 listing six tools against seven.
  `tests/claims.json` now registers the numbers with what computes each and the wording that carries it
- fixed, unchecked: `manifest.sha256.json` had drifted on `validation_report.json` with nothing to catch
  it; a test now compares every digest
- moved out of the contract: the embedding price table (`spec.md` §10) and the pre-implementation
  playbook (repository root) are dated reviews. `AGENTS.md` now holds the asrai section `spec.md` §12
  reserves instead of unrelated web-research notes
- English is canonical everywhere except `review/`, whose never-edited rule outranks it. The two READMEs
  inside the wheel were Korean, including the one asking eleven language communities for translations;
  both are English now

**MCP surface, decided.** The eight-tool cap was never a host limit and had no measurement behind it, so
the bound is now bytes. The `tools/list` reply as compact JSON was 3,620 bytes — about 850 tokens at
4.25 bytes per token, o200k_base — under a hard cap of 1,200 tokens and warned above 1,000 by
`tests/test_asrai.py`. It measured 4,108 bytes (968 tokens) before the descriptions were cut,
`light_ledger`'s alone 38.5% of it; what left the descriptions is in `SKILL.md`, which is read once. The
`vocab_get` overload survives on the same budget (`docs/conventions.md` §1a, structural notes).

**Colour space, answered, with no input field added.**

- every rank-based measurement is invariant to a monotone transfer by construction: bright side, shaded
  mass and key fit are percentile centroids, and the emitter relative floor is a percentile. Measured:
  8 emitters x 3 references x {shipped, gamma 2.2, gamma 1/2.2}, masks pinned, and the rank share of
  each spill ring was identical to two decimals while the luminance difference swung 10-20x
- the difference form still held its sign on all 18 real rows; it flipped only when the file's tonal
  range was destroyed (sRGB read as linear, then JPEG), which `SPILL_MIN_Y` refuses. A mid-rank form was
  tried and rejected: it reads 1.00 on the bloomed synthetic where the difference form correctly reads
  `lights_nothing`, because both ring forms include subjects and not only ground
- `SPILL_MIN_Y` verified against the night reference: all 8 emitters measurable (p50 Y 0.015, gains
  +0.013..+0.075), so the guard does not silence dark genres

**Perturbations run — synthetic disc scene, both alpha and bbox subjects.**

- injected: URP bloom, vignette (0.1..0.7), sRGB-as-linear both ways, JPEG q60, film grain, matte-line
  fringing, atlas extrude writing opaque padding, and the stacks a real hand-over combines
- held: `bright_side` (under 1 deg across every perturbation and stack), `contour_fit` (under 4 deg, and
  r2 reports the silhouette that is not one form), bloom at every radius and gain (it widens the emitter
  mask symmetrically, so the spill sign survives), atlas padding (a phantom emitter, correctly proposed
  and rejectable; the silhouette box grows by the padding)
- moved, and fixed: a vignette of a tenth fabricated a shaded mass on a bbox subject (alpha now
  required); a vignette over 0.4 and a crushed export made spill unmeasurable and the axis read pass (an
  unchecked light now holds it at warn); sRGB-as-linear plus JPEG flipped the spill sign positive around
  a decal (both rings must now clear the bottom 3% of the 8-bit range); the ordinal emitter ids rebound
  under a strong vignette, so a filled sheet answered about other blobs (the form is stamped)

**Where the sources went.** The surface pass's eight published sources and the estimator noise floor
were part of this snapshot until 2026-09-15, when they moved to
`review/2026-09-15-art-direction-rationale.md`. A citation is not a status.
