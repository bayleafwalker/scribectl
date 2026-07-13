# Scribectl semantic verification and concurrency hardening

## Full-worker prompt baseline

Use this prompt from the root of `bayleafwalker/scribectl`. It is grounded in
`main` at commit `279aae91c2025cdbace0b9745dbc97bc7f040b7e` (2026-07-13).
Re-inspect the repository before acting; later commits override factual details
here, but not the stated product laws unless a ratified design document says so.

---

You are the primary implementation and verification worker for Scribectl. Your
task is to establish an independent semantic-verification layer for the system,
then use it to expose and minimally harden unsafe state transitions and
concurrent histories. Deliver executable models, stateful tests, deterministic
concurrency/crash tests, model documentation, and the smallest production
changes needed to make the accepted model true.

This is not a request for a general testing brainstorm. Work repo-first, produce
the artifacts, run them, and leave a reviewable, green change set.

## 1. Mission and success condition

Scribectl already has a strong product philosophy and a passing contact-test
suite. The missing layer is independent verification of its stateful and
concurrent semantics. Today, many guarantees are true only when one process and
one device act at a time. Make the actual consistency boundary explicit and
tested.

The completed change must answer, in executable form:

1. What are the authoritative entities, identities, states, commands, and
   derived projections in Scribectl?
2. Which invariants are product laws, which are implementation conveniences,
   and which are merely current behavior?
3. What consistency guarantee applies to each write surface?
4. What may happen when two workers plan or mutate the same vault concurrently?
5. What may happen when a process crashes at every durable-write boundary?
6. What does Livesync replication guarantee, and what remains a single-writer
   operational constraint?
7. Can one declarative test-context packet drive the reference model,
   stateful tests, deterministic schedules, history checkers, and bounded TLC
   configurations without copying the scenario into five subtly different
   fixtures?

Success means the repository contains a small semantic model that is plainly
independent of the production implementation, a reproducible PlusCal/TLA+
model-checking path, Hypothesis state machines, deterministic multi-worker and
crash tests, and a traceability map from product law to model property to test.

## 2. Repository protocol: do this before editing

Read in full:

- `AGENTS.md`
- `docs/DESIGN.md`
- `docs/ARCHITECTURE.md`
- `docs/DISPATCH.md`
- `docs/RATIFICATION.md`
- `PLAN.md`
- `scribectl/core/{vault,project,contextpack,miningpack,inbox,timeline}.py`
- `scribectl/cli.py`
- `scribedispatch/{policy,cli,landing,engine,vaultio}.py`
- all current tests, especially `tests/test_cli.py`, `tests/test_project.py`,
  `tests/test_dispatch.py`, and `tests/test_inbox.py`

Follow `AGENTS.md` exactly. Validate the remote sprint context before edits and
claim the assigned item. If sprint credentials are unavailable, do not create a
local Sprintctl database and do not pretend a claim exists; report the blocker
after completing read-only analysis.

Record the inspected commit, current test count, and baseline command output in
the final handoff. At the baseline above, the suite is 175 passing tests.

Do not push, open a PR, or mutate the real `/media/Creative` vault unless the
operator separately authorizes it. All concurrency and fault work runs against
disposable fixture copies.

## 3. Non-negotiable product laws

Treat these as axioms unless a ratified design document explicitly changes
them:

1. The writer is the canon ratifier and taste gate. No agent, dispatcher,
   confidence score, consensus, or retry loop may substitute for the writer's
   verdict.
2. No automatic ratification.
3. The engine never calls an LLM. Runner integrations stay in
   `scribedispatch/`.
4. The coordinator never authors intent. It consumes authored contracts and
   frozen inputs, then lands new artifacts.
5. Agents never rewrite human-touched drafts, canon nodes, cards, contracts, or
   verdicts.
6. Status is derived, never hand-maintained in vault frontmatter.
7. Context, mining, and reconciliation packs are frozen, immutable receipts.
   Agents consume the bytes identified by the receipt, not a later live-vault
   reconstruction.
8. The timeline and ratification log are append-only semantic artifacts.
9. Reviews inform but do not act. No agent-on-agent feedback or autonomous
   rewrite loop.
10. Independent variant generation is allowed only when each variant has an
    explicit identity and remains a quarantined choice for the writer. Do not
    model “one draft per card forever” as a product law.
11. Quarantined proposals and unratified source ore are not canon and must not
    silently enter fill context.
12. A cache such as `control/Status.md` is disposable and must never become an
    input to authoritative state.

Do not “solve” concurrency by weakening these laws.

## 4. Current implementation hazards to verify, not blindly assume

The following are evidence-backed review hypotheses. Reproduce them with a
model or deterministic test before choosing a production fix.

| Surface | Current pattern | History to test |
| --- | --- | --- |
| Draft/review landing | `_write_new` performs `exists()` then `write_text()` | Two workers can both pass the check, both spend tokens, and race to truncate/write the same path. |
| Pack freezing | content-addressed name, but check-then-write and immediate visibility | A second worker may treat a just-created but incomplete file as frozen, or two writers may race. |
| Dispatch planning | derived plan with no claim/reservation | Two watches can plan the same fill/review from the same snapshot. |
| Inbox mining | read inbox and ledger, derive additions, rewrite the full inbox | Concurrent miners or a miner plus a human edit can cause a lost update; identical work can duplicate after ambiguous failure. |
| Ratification sweep | rewrite node(s), append ledger, then rewrite inbox | Crash or concurrency can create a partial/torn logical transaction, duplicate effects, or lost edits. |
| Source capture | create source, then rewrite the project note's `sources:` block | Crash leaves an orphan; concurrent captures can lose a registration. |
| New card/init/propose/reconcile/adopt | multi-file check-then-create sequences | Crash leaves partial scaffolds; concurrent equal names can overwrite or conflict. |
| Vault loading | files are read one by one; note identity is keyed by basename/stem | A pack/status can be a fractured read; duplicate stems silently shadow one another. |
| Card/review projection | card becomes `reviewed` when any review exists; policy collects review kinds across all drafts and selects a draft lexicographically | Reviews for an old or different variant can make a newer draft appear complete. |
| Proposal projection | a sibling is `reconciled` as soon as a merge scaffold links it | A worker crash before merged candidates exist can hide still-unswept work. |
| Watch settling | mtime debounce only | Quiet time is not mutual exclusion, a claim, or an atomic snapshot barrier. |
| Livesync | asynchronous replication of files | Local locks cannot provide cross-device linearizability; simultaneous mutable-file writers need an explicit policy or a different data shape. |

Also inspect and characterize:

- path containment for contract `output_target` values;
- stable candidate/fact identity and whether one proposal-level `via` link can
  accurately represent several independently decided candidates;
- the distinction between direct human-authored facts and machine-applied
  sweep facts;
- the intended authority relationship among a node's `## Ratified facts`, the
  writer's checkbox, and the ratification receipt;
- retry behavior after an indeterminate runner completion or process kill;
- orphaned but immutable files versus lost authoritative intent.

Do not turn every hypothesis into a broad rewrite. Rank by violation of a
product law, irreversible loss, audit failure, duplicate expensive work, and
operator recoverability.

## 5. Use consistency terminology precisely

Use Jepsen-style language as a vocabulary and history discipline, not as a
reason to introduce a Clojure cluster harness into this small Python tool.

Define these terms in the repository documentation and use them consistently:

- **operation**: one logical client request such as `sweep`, `mine`,
  `freeze-pack`, `claim-fill`, or `land-review`;
- **invocation/completion**: operation start and its `ok`, definite `fail`, or
  indeterminate `info` completion;
- **history**: the concurrent sequence of operation events;
- **safety property**: the set of histories the system must never admit;
- **linearization point**: the single conceptual instant at which a
  single-object operation takes effect;
- **linearizability**: use for one logical object or per-key operation that must
  appear atomic and preserve real-time order;
- **strict serializability**: use for a multi-object logical transaction that
  must be equivalent to one real-time-compatible serial order;
- **eventual convergence**: use for replicated immutable artifacts when
  temporary replica divergence is accepted but all delivered updates must
  converge;
- **indeterminate outcome**: the client cannot know whether an effect committed;
  retries must be safe;
- **lost update/lost write**, **fractured read**, **torn transaction**,
  **stale read**, and **duplicate effect**: name concrete observed phenomena;
- **nemesis**: a deliberate fault injector such as worker kill, write pause,
  replica lag, or concurrent human mutation—not an ordinary test client.

Do not claim SQL isolation levels for a filesystem tree. State the abstract
object and legal histories first, then name the closest consistency property.

## 6. Required semantic model

Create a repository-native semantic model document before changing production
behavior. It must be concise enough to review but complete enough to serve as
the independent oracle for tests.

### 6.1 Artifact classes

At minimum distinguish:

1. **Immutable content-addressed receipts**: context packs, mining packs,
   reconciliation packs.
2. **Create-once generated artifacts**: drafts, review reports, proposals, raw
   captured sources, and future variants.
3. **Human-authored mutable intent**: project note, card, contract, canon node,
   inbox verdict marks.
4. **Append-only semantic records**: timeline and ratification receipts.
5. **Generated projections/caches**: status dashboard and digests.
6. **Coordination records**, if added: claims, reservations, transaction
   journals, recovery markers. Declare whether they are authoritative,
   ephemeral, host-local, or replicated.

For each class document identity, mutability, allowed writers, source of truth,
visibility/commit rule, retry rule, conflict behavior, and recovery rule.

### 6.2 Logical identities

Define stable identities independently of display filenames. Cover:

- project/vault identity;
- artifact identity versus Obsidian wikilink/display name;
- card identity;
- draft/variant identity and revision ordering;
- review identity: draft revision + lane, not merely card + lane;
- context/mining pack identity and input read-set revision;
- candidate/fact/verdict/receipt identity;
- dispatch work key, including variant when intentional;
- operation/transaction identity for crash-safe retries.

Explicitly reject silent basename collisions. If duplicate note stems remain a
product restriction, validate and fail closed; do not let dictionary insertion
order decide authority.

### 6.3 State and actions

Define a pure abstract state separate from Markdown parsing. It should include
only semantics needed to decide properties, for example:

- artifacts and their immutable revisions/digests;
- authored cards and contracts;
- drafts and reviews keyed by the input revision they consume;
- candidates, writer verdicts, node facts, receipts, and provenance;
- proposal/reconciliation reachability;
- frozen pack read sets;
- in-flight claims and operation journals;
- worker phase and crash state.

Define command preconditions, effects, failure/indeterminate outcomes, and
observations for at least:

- author/edit card or contract;
- freeze pack;
- claim, generate, validate, land, release/expire;
- mine report/proposal candidates;
- mark a writer verdict;
- sweep and recover sweep;
- capture/register source;
- scaffold/fill/reconcile proposal;
- load/project status;
- crash/restart;
- replica delivery or conflict, if modeled.

Treat LLM output as opaque nondeterministic bytes. The semantic model is about
authorization, state, provenance, and concurrency—not prose quality.

### 6.4 Derived projections

Specify pure functions for:

- canonical/audited node state;
- card state;
- active or selected draft/variant;
- missing review lanes for that exact draft revision;
- proposal and per-candidate state;
- dispatchable work set;
- candidate reachability and next-action counts.

The model must force a decision on these ambiguities instead of inheriting the
current code accidentally:

1. Does direct human text in `## Ratified facts` become canon immediately,
   become “seeded but usable,” or require a receipt? Distinguish direct human
   authorship from a machine-applied sweep fact.
2. What makes a draft active when variants and manual rework coexist?
3. When exactly are sibling proposals considered reconciled?
4. Is status allowed to be stale, or must each returned result correspond to
   one self-consistent snapshot?

Document the chosen answer, compatibility impact, and migration/rollback path.

## 7. Consistency contract by surface

Create a table in `docs/semantics/` or an equivalent ratified location. Begin
from this target and change it only with a written rationale:

| Abstract surface | Recommended contract | Notes |
| --- | --- | --- |
| Immutable pack publication | Linearizable create-if-absent per content key plus atomic visibility | Same key + same bytes is idempotent; same key + different bytes is corruption/conflict. |
| Draft/review/proposal landing | Linearizable reservation/put-if-absent per work key | Intentional variants use distinct variant/work identities. Existing human artifacts are never overwritten. |
| Dispatch work acquisition | Linearizable claim per work key, with owner token and bounded recovery/expiry | Do not hold a global lock during an LLM call. Revalidate inputs before commit. |
| Pack assembly/read projection | One validated read snapshot or explicit abort/retry on change | A frozen pack must never combine mutually inconsistent file generations without detection. |
| Inbox mining | Convergent, idempotent candidate insertion with no lost writer edits | Stable candidate identity is preferable to full-file blind rewrite. |
| Ratification sweep | One recoverable logical transaction; locally strict-serializable with a declared commit point | After crash/recovery, a machine-applied fact, receipt, and inbox disposition agree exactly once. |
| Capture + project registration | Atomic or recoverable batch; retry-safe | Orphan detection and repair are acceptable if automatic and lossless. |
| Generated status cache | Atomic replace; no authority | Readers may see old or new complete bytes, never partial bytes. |
| Same-host multiple workers | Hard guarantee | Use process-safe primitives, not only `threading.Lock`. |
| Cross-device Livesync writers | Explicitly bounded guarantee | Prefer immutable per-operation artifacts or a declared single-writer rule. A host-local lock is not a distributed lock wearing a fake moustache. |

The simplest acceptable implementation is preferred. A coarse vault-scoped
critical section for short mutations plus per-work claims for long generation
is more appropriate than inventing a distributed control plane. Do not add
Redis, etcd, PostgreSQL, or a second authoritative database without model
evidence that the file-native design cannot meet the agreed scope.

## 8. Stable invariant catalogue

Assign stable IDs (`SEM-*`) and use them in model names, test packet properties,
test names, and the traceability matrix. Include at least:

- `SEM-001 NoAutoRatify`: only an explicit writer verdict authorizes a
  machine-applied canon fact.
- `SEM-002 NoHumanOverwrite`: generated operations never replace an existing
  human-owned artifact.
- `SEM-003 PackIntegrity`: a published pack is complete, hash-valid, immutable,
  and tied to its actual read set.
- `SEM-004 CandidateConservation`: every proposed candidate is pending,
  explicitly decided, or losslessly represented by a live reconciliation;
  never merely hidden by a scaffold or crash.
- `SEM-005 SweepCorrespondence`: each machine-applied accepted fact has exactly
  one accepted verdict and receipt with matching identity/provenance; rejected
  and deferred candidates never enter node facts.
- `SEM-006 SweepRecoverability`: an interrupted sweep either has no logical
  effect or deterministically completes/reconciles on recovery; retry does not
  duplicate effects.
- `SEM-007 WorkExclusion`: at most one worker owns a non-variant work key at a
  time, and only the token owner may commit.
- `SEM-008 RevisionExactReview`: review completeness is computed per exact
  draft revision and lane.
- `SEM-009 DerivedStateSoundness`: projections equal the abstract reference
  model for the observed snapshot.
- `SEM-010 AtomicVisibility`: readers never consume a partially published
  generated artifact.
- `SEM-011 PathContainment`: every engine/dispatcher write remains in its
  designated project subtree.
- `SEM-012 IdentityUnambiguous`: artifact resolution never silently selects one
  of several identities.
- `SEM-013 Quarantine`: unratified proposal/source content never appears as
  settled canon in a fill pack.
- `SEM-014 RecoveryVisibility`: abandoned claims, journals, or orphan batches
  are detectable and have a documented safe recovery path.

Do not force every invariant into TLC. Map each to the cheapest independent
verification layer that can falsify it.

## 9. Test-context packets: one scenario, several adapters

Create a versioned, declarative `test_context_packet` schema. Do not confuse it
with Scribectl's runtime `context_pack` artifact. A test-context packet
describes an initial semantic world, actors, logical operations, controlled
interleaving/faults, and required properties.

The packet must be able to feed:

1. the pure Python reference model;
2. fixture materialization into a temporary vault;
3. a Hypothesis state-machine seed or rule configuration;
4. a deterministic concurrency/crash schedule;
5. a Jepsen-style history and domain checker;
6. constants/initialization for generic TLC models where applicable;
7. generated traceability/documentation summaries.

Do not generate a fresh TLA+ algorithm per packet. Write a small number of
generic specifications and map packet constants/configurations into them.

A starting shape:

```yaml
schema: scribectl.test-context/v1
id: ratification.two-sweepers.same-candidate
title: Two sweepers race on one accepted candidate
scope: same_host
template_set: fiction

initial:
  cards: []
  nodes:
    - id: node:mara
      facts: []
  candidates:
    - id: candidate:c1
      target: node:mara
      fact: The gate opens at dawn.
      verdict: accepted_by_writer
      provenance: proposal:p1
  artifacts:
    - ratification_inbox
    - ratification_log

actors:
  - id: worker:a
    role: sweeper
  - id: worker:b
    role: sweeper

operations:
  - id: op:a
    process: worker:a
    function: sweep
    args: {candidate_ids: [candidate:c1]}
  - id: op:b
    process: worker:b
    function: sweep
    args: {candidate_ids: [candidate:c1]}

schedule:
  kind: named_interleaving
  name: both_read_before_either_commit

faults: []

properties:
  - SEM-005
  - SEM-006
  - SEM-007

expected:
  terminal:
    fact_count: 1
    receipt_count: 1
    candidate_state: swept
  allowed_completions:
    - [ok, fail_already_applied]
    - [fail_already_applied, ok]

adapters:
  reference: true
  stateful: true
  concurrency: true
  history: true
  tla_model: ratification
```

Schema requirements:

- stable semantic IDs, not only filenames;
- explicit actor/process identity;
- operation identity and arguments;
- initial and terminal semantic state;
- named yield points/interleavings rather than sleeps;
- crash/partition/edit fault descriptions;
- property IDs and allowed versus forbidden outcomes;
- an escape hatch to name a small adapter-specific fixture builder, without
  smuggling the whole scenario back into Python;
- schema validation tests and useful error messages;
- deterministic packet-to-fixture and packet-to-history expansion;
- packets remain small data documents, not a new workflow language.

Create a traceability test which fails if a mandatory packet names an unknown
property or an enabled adapter has no implementation.

## 10. Mandatory scenario packets

Implement at least the P0 packet set below. P1 may be completed in the same
change if it remains reviewable; otherwise document a concrete follow-up with
the semantic property already assigned.

### P0 — must execute in CI

1. `dispatch.two-fills.same-work-key`: two workers plan the same ready card and
   output target.
2. `dispatch.two-reviews.same-draft-lane`: two workers review one exact draft
   revision and lane.
3. `ratification.two-sweepers.same-candidate`: both read the same checked inbox
   state before either commits.
4. `ratification.crash-after-fact-before-receipt`: kill/restart at the first
   multi-file boundary.
5. `ratification.crash-after-receipt-before-inbox-disposition`: outcome is
   indeterminate to the first client; recovery/retry remains exact-once.
6. `inbox.mine-versus-mine-disjoint-artifacts`: neither candidate batch is
   lost.
7. `inbox.mine-versus-human-edit-or-sweep`: writer marks/notes are not lost and
   no decided candidate is resurrected.
8. `pack.reader-versus-publication`: no reader accepts partial bytes.
9. `pack.snapshot-changes-during-read`: either the pack corresponds to one
   validated read set or creation aborts/retries visibly.
10. `projection.new-draft-old-reviews`: old lanes do not review a new or
    selected variant by osmosis.
11. `reconcile.crash-after-scaffold`: sibling candidates remain reachable until
    a valid reconciliation actually carries them.
12. `identity.duplicate-note-stems`: discovery/resolution fails closed with a
    precise diagnostic.

### P1 — strongly recommended

13. two captures update `sources:` concurrently;
14. card creation crashes between card and contract;
15. proposal creation crashes between pack and proposal;
16. intentional variant fills share a pack but have distinct work and artifact
    identities;
17. a stale claim expires or is explicitly recovered, while a live claim cannot
    be stolen;
18. malicious or mistaken `output_target` path traversal is rejected;
19. same-host worker plus simulated Livesync delivery modifies a read-set file;
20. two replicas create immutable, differently named artifacts during a
    partition and converge without loss;
21. two replicas mutate the same inbox/ledger under the declared cross-device
    policy and fail closed or surface a conflict—never silently claim
    linearizability.

## 11. PlusCal/TLA+ deliverables

Use PlusCal where the algorithmic steps and worker program counters matter;
translate to TLA+ and check with TLC. Do not attempt to formalize Markdown,
YAML parsing, prose, or the complete application.

Create at least two bounded executable models:

### 11.1 Ratification protocol

Model:

- two workers;
- at least two candidates and two target nodes;
- writer verdict as pre-existing authorization, never generated by a worker;
- inbox membership/disposition;
- node effects;
- receipt effects;
- operation identity/journal or the chosen recovery mechanism;
- lock/token ownership;
- crash at each instruction boundary;
- restart/recovery and retry;
- an external observer if intermediate visibility matters.

Check `TypeOK`, `SEM-001`, `SEM-004`, `SEM-005`, `SEM-006`, and the relevant
exclusion/visibility properties. Identify the intended linearization point.

### 11.2 Dispatch claim and landing protocol

Model:

- two workers and at least two work keys;
- same-key and disjoint-key schedules;
- claim token, optional lease/expiry, generation outside the short critical
  section, input revision validation, atomic landing, release/recovery;
- crash before/after generation and before/after landing;
- an intentional variant key distinct from accidental duplicate work;
- review key includes exact draft revision and lane.

Check `TypeOK`, `SEM-002`, `SEM-003`, `SEM-007`, `SEM-008`, `SEM-010`, and
`SEM-014` as applicable.

### 11.3 Prove the checker is not decorative

Provide an unsafe/legacy model configuration or deliberately weakened action
whose TLC run is expected to produce a counterexample for at least:

- duplicate or torn sweep effects; and
- duplicate same-key dispatch/landing.

The normal safe configurations must pass. The known-bad configuration must be
run through a wrapper that expects the named invariant violation; CI should
fail if the bad model unexpectedly appears safe or if the safe model violates
an invariant.

Keep state spaces reviewable: small finite constants, symmetry where helpful,
no unbounded strings/timestamps, and documented fairness assumptions. Add
liveness only after safety is stable; candidate/work recoverability is more
valuable than ornamental temporal formulas.

Use the official `tla2tools.jar` command-line tools with a pinned version and
checksum, Java 11+, and reproducible commands for PlusCal translation and TLC.
Do not commit a large binary JAR unless repository policy explicitly prefers
vendoring. Record tool versions and use deterministic, conservative worker
settings in CI.

## 12. Hypothesis stateful testing

Add Hypothesis as a development dependency, not a runtime dependency. Build a
`RuleBasedStateMachine` around a pure reference model and a disposable vault
adapter.

The reference model must not call `card_status`, `proposal_status`, `mine`, or
the production parser to decide expected outcomes. Shared parsers may only be
used at the final serialization boundary if the independent logical state is
still the oracle.

Rules should generate short but meaningful sequences such as:

- add/edit/remove node/card/contract/source;
- create draft variant;
- add review for a specific draft/lane;
- propose/mine/mark/sweep/recover;
- reconcile before and after candidates exist;
- freeze/tamper/reload pack;
- crash and restart at named phases;
- introduce an allowed or forbidden duplicate identity;
- advance an injected logical clock for claim expiry.

After rules, compare the production projection to the reference model and
check invariant IDs. Preserve Hypothesis shrinking: do not hide all actions
inside one opaque mega-rule. Persist a minimal regression packet for each real
counterexample found.

Do not use random sleeps or probabilistic race loops in the required CI path.

## 13. Deterministic concurrency, crash, and history testing

Implement a small test seam for named yield/fail points around durable
boundaries. It may be dependency injection, a filesystem adapter, or a
test-only hook; it must not make production behavior depend on test globals.

Required boundaries include, as relevant to the chosen protocol:

- after observation/read-set capture;
- after existence/CAS check;
- after claim/reservation;
- after temporary file is complete but before publication;
- after first node effect;
- after receipt effect;
- before inbox disposition;
- after publication but before client acknowledgement;
- before claim release;
- during source registration or reconciliation activation.

Use `threading.Barrier` only for in-process behavior and multiprocessing or
real CLI subprocesses for process-level guarantees. A Python GIL is not a
filesystem transaction. Kill subprocesses at named fail points to create true
indeterminate outcomes and then run documented recovery.

Emit a compact Jepsen-style JSON history for concurrency tests with at least:

```json
{
  "process": "worker-a",
  "type": "invoke|ok|fail|info",
  "f": "sweep",
  "op_id": "op-a",
  "value": {},
  "time_ns": 0
}
```

Write domain checkers for:

- exact-once candidate effect/receipt correspondence;
- candidate conservation;
- per-key claim exclusion and commit authority;
- no pre-existing artifact overwrite;
- pack integrity and snapshot provenance;
- review-to-draft revision correspondence;
- path containment;
- recovery from `info` outcomes.

For a simple put-if-absent or claim object, a linearizability checker is useful.
For ratification, use the explicit abstract transaction model rather than
mislabeling a custom business invariant as generic register linearizability.

Include synthetic invalid histories to prove each checker detects the anomaly
it names.

## 14. Minimal implementation direction

Model first, then implement the smallest mechanism that satisfies the accepted
same-host contract. The preferred starting architecture is:

1. **Central filesystem primitives** used by both `scribectl/cli.py` and
   `scribedispatch/landing.py`:
   - exclusive create (`O_CREAT | O_EXCL`) for create-once artifacts;
   - write-temp-in-same-directory, flush/fsync, atomic rename, and directory
     sync for generated replacements;
   - compare-and-swap or expected-digest replace under the vault mutation lock;
   - path containment validation;
   - explicit “existing same bytes” versus “existing different bytes” results.
2. **A short, process-safe vault mutation lock** for local shared mutable files.
   Do not hold it while an LLM runs.
3. **Per-work claims/reservations** for fills and reviews. Claim briefly,
   generate outside the lock, then revalidate the claim token and input
   revisions before atomically landing.
4. **Stable operation/candidate identity and recoverable sweep**. Prefer a
   durable operation journal or immutable event record with idempotent replay
   over trying to make several unrelated file rewrites magically atomic.
5. **Validated pack snapshot**. Capture the exact file read set and versions or
   hashes; before publication, verify it has not changed. Abort/retry rather
   than freeze a fractured pack.
6. **Explicit projection semantics** for active drafts, review lanes, proposal
   reconciliation, and duplicate identities.

The implementation may choose a different mechanism if the model and ADR show
why it is simpler or safer. Reject these shortcuts:

- an in-memory lock as the only protection;
- `exists()` followed by ordinary `write_text()`;
- holding a coarse lock across a model call;
- using mtime settle as a correctness barrier;
- last-writer-wins on the inbox, project note, node, or ledger;
- a host-local lock presented as a cross-device guarantee;
- hiding a failed reconciliation or partial sweep from status;
- adding a database merely because transactions are familiar.

For cross-device writers, choose and document one of two honest contracts:

- **recommended v1:** mutable canon/inbox/ledger operations have one active
  writer device; immutable create-once artifacts converge through Livesync and
  conflicts fail visibly; or
- immutable per-operation events plus a deterministic projection that can
  merge concurrent replica updates without loss.

Do not build the second option unless the requirement is real and the model
shows it remains compatible with Obsidian and the current product laws.

## 15. Required repository artifacts

Use repo conventions, but the final change should contain equivalents of:

```text
docs/semantics/domain-model.md
docs/semantics/consistency-contract.md
docs/semantics/test-context-packets.md
docs/semantics/traceability.md
docs/adr/<concurrency-and-recovery-decision>.md

models/tla/Ratification.tla
models/tla/RatificationSafe.cfg
models/tla/RatificationUnsafe.cfg
models/tla/DispatchClaims.tla
models/tla/DispatchClaimsSafe.cfg
models/tla/DispatchClaimsUnsafe.cfg
models/tla/README.md

tests/context_packets/<schema or loader>
tests/context_packets/scenarios/*.yaml
tests/stateful/test_semantic_state_machine.py
tests/concurrency/test_dispatch_protocol.py
tests/concurrency/test_ratification_protocol.py
tests/history/test_history_checkers.py
tests/support/<reference model, scheduler, history recorder>

scripts/check-models
```

Do not create empty architecture theatre. Every document must link to executable
artifacts; every executable property must link back to a documented invariant.

If a production abstraction is needed, keep it narrow and place it where the
existing engine/dispatcher boundary remains obvious. `core/` should continue to
be a pure read/derivation layer unless a ratified architecture change explicitly
says otherwise.

## 16. Execution order

Work in these stages and commit/review at the smallest coherent boundary:

### Stage A — characterize and decide

1. Re-run the baseline suite.
2. Write the semantic inventory and invariant IDs.
3. Add deterministic legacy race/crash characterizations or synthetic bad
   histories; do not leave the main suite red.
4. Write the consistency ADR, including local versus cross-device scope,
   linearization points, recovery behavior, compatibility, and rollback.

### Stage B — executable abstract models

5. Implement the pure Python reference model and packet loader/schema.
6. Implement the two PlusCal/TLA+ protocols, safe and expected-unsafe configs.
7. Add traceability checks and model-check scripts.

### Stage C — stateful and concrete tests

8. Implement Hypothesis state machines against disposable vaults.
9. Implement deterministic process/thread interleavings, crash injection, and
   history checkers for the P0 packets.
10. Confirm the tests can detect the characterized legacy anomalies.

### Stage D — minimal hardening

11. Add atomic filesystem primitives, claims, validation, and recovery only as
    demanded by failed properties.
12. Re-run every layer after each production change.
13. Update public design/architecture docs where behavior or guarantees changed.
14. Render the Sprintctl snapshot and produce a concise handoff.

Do not begin with a sweeping storage rewrite and retrofit a model afterward.

## 17. Acceptance gates

The task is not complete until all applicable gates pass:

1. Existing behavior tests remain green; intentional behavior changes have an
   explicit semantic decision and regression test.
2. All P0 context packets validate and run through their enabled adapters.
3. Safe TLC configurations complete without invariant violations.
4. Expected-unsafe TLC configurations produce the named counterexamples.
5. Hypothesis stateful tests run with deterministic CI settings and retain
   shrinking.
6. Concurrency tests use controlled interleavings, not timing luck.
7. Crash tests produce and recover from at least one `info` outcome on sweep
   and dispatch landing.
8. Synthetic bad histories are rejected by the appropriate checkers.
9. Two same-key workers cannot both commit a non-variant artifact.
10. Disjoint-key workers can still make progress; safety must not collapse into
    one lock held across model generation.
11. A machine-applied sweep fact cannot remain permanently without its matching
    authorized verdict/receipt, and retry cannot duplicate it.
12. An uncompleted reconciliation cannot make original candidates disappear
    from every writer-facing surface.
13. Reviews are exact to draft revision and lane.
14. Published files are atomically visible and path-contained.
15. The cross-device Livesync contract is explicit and tested or clearly marked
    as a manual integration boundary; no unsupported distributed guarantee is
    implied.
16. Recovery and rollback instructions are executable and do not require
    deleting unknown files by hand.
17. `git diff --check` passes and the worktree contains no unrelated changes.

Add the exact repository commands to the model README and CI. At minimum the
handoff should report equivalents of:

```bash
uv sync --dev
uv run pytest -q
./scripts/check-models
git diff --check
```

If stress or two-replica Livesync tests are too slow or environment-dependent
for normal CI, mark them explicitly and provide a reproducible local command.
The deterministic P0 core stays in CI.

## 18. Rollback and compatibility

The ADR and handoff must cover:

- how to disable or revert new worker coordination without losing committed
  artifacts;
- how stale claims are inspected and safely recovered;
- how incomplete sweep journals are replayed or abandoned with evidence;
- whether old Scribectl versions tolerate any new frontmatter fields or
  control directories;
- whether candidate/operation IDs require migration and how existing fixtures
  are interpreted;
- why rollback cannot resurrect a swept candidate or drop a receipt;
- how to restore from a disposable fixture snapshot during tests.

Prefer additive, backward-readable formats. Do not add an “unsafe legacy mode”
to production merely to make rollback easy; reverting code is safer than a
switch that re-enables known data-loss histories.

## 19. Final handoff format

Return:

1. **Outcome:** what semantic contract is now executable.
2. **Decisions:** canon authority, active draft identity, work key, same-host
   guarantee, cross-device boundary, sweep commit/recovery rule.
3. **Counterexamples found:** minimal histories and the property each violated.
4. **Implementation:** production changes, deliberately deferred changes, and
   why.
5. **Verification:** exact commands and results for pytest, Hypothesis,
   concurrency/crash packets, TLC safe/unsafe configs, and diff checks.
6. **Traceability:** invariant → model → packet/test → code path.
7. **Recovery/rollback:** operator commands and remaining risks.
8. **Files changed:** grouped by model, tests, production, and docs.

Do not report “thread-safe,” “atomic,” “idempotent,” “linearizable,” or
“strict-serializable” without naming the object, scope, failure assumptions,
and test/model that supports the claim.

## 20. Primary references

Use primary sources for terminology and tooling:

- Jepsen, consistency as legal histories and safety properties:
  <https://jepsen.io/consistency>
- Jepsen consistency-model map:
  <https://jepsen.io/consistency/models>
- Jepsen linearizability:
  <https://jepsen.io/consistency/models/linearizable>
- Jepsen strict/strong serializability:
  <https://jepsen.io/consistency/models/strong-serializable>
- Jepsen anomaly/phenomena catalogue:
  <https://jepsen.io/consistency/phenomena>
- Leslie Lamport's PlusCal tutorial:
  <https://lamport.azurewebsites.net/tla/tutorial/intro.html>
- Official TLA+ command-line tools:
  <https://github.com/tlaplus/tlaplus/blob/master/USE.md>
- Hypothesis stateful testing:
  <https://hypothesis.readthedocs.io/en/latest/stateful.html>

The repository's ratified design remains authoritative over generic advice.
The references give us precise tools for testing that design, not permission to
replace it with a distributed-systems hobby project.

