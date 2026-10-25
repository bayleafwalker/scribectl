# Cheap model breadth and selective editorial judgment

Status: **operator-requested implementation experiment**, 2026-10-25.
Extends [SC-K01/SC-K02](2026-10-18-kaos-roadmap.md) and the ratified
[writing design](../DESIGN.md). Companion: Agentops
[AE-08](https://github.com/bayleafwalker/agentops/blob/main/docs/plans/agentops/2026-10-25-evidence-guided-agent-workflows.md).
No automatic canon change, live vault migration or new agent dispatcher follows.

## Intended result

On one real, authorized writing project, test whether several inexpensive
**genuinely different** proposals followed by selective higher-quality
editorial synthesis produce work the writer prefers over direct premium-model
generation. Include time spent rejecting drafts and repairing them; more
words are not progress.

Existing Scribectl frozen source packs, provenance, proposal mining and human
ratification are the input and acceptance boundary. Agents may draft, rank,
summarize and criticize; the writer alone records canon/ratification. Do not
route rejected claims into the Obsidian vault as accepted facts.

## SC-C1 — freeze the creative comparison

- Choose one project and 3–5 bounded prompts representing contrasting jobs:
  structure, idea generation, revision, voice consistency, and fact/canon
  conflict. Obtain the exact allowed public/private data scope before
  selecting a remote API. Frozen canonical source/reference packs must be
  digest-bound. Reserve a truly held-out passage or criteria for review.
- Compare (a) direct established premium-model draft, (b) one cheap draft and
  premium revision, and (c) two or three **role-differentiated** cheap drafts
  synthesized/reviewed by the same premium editorial model. Optionally
  compare a qualified local generative model; do not pretend a decision-only
  model can write narrative prose.
- Use the existing provider-native runners and selected API/subscription
  routes. Record requested and actual provider/model, profile revision,
  instruction digest, source pack digest, exact generated artifacts, quota
  behavior, actual cost or unknown, elapsed time and any repair rounds.

**Acceptance:** all variants are generated from the same declared source
revision, blind reading order, unchanged locked canon, no additional
permissions and a replayable artifact inventory. Missing/rejected variants
stay in the denominator.

## SC-C2 — rank, review, and preserve actual taste

A deterministic checker rejects schema violations, forbidden canon mutation
and missing citations before an LLM judge can comment. Cheap structured
classifiers may flag contradictions or rubric misses but cannot ratify
fictional facts or replace author preference. A stronger reviewer may
identify tension and alternatives; a blind human preference and actually
accepted revision are the useful result.

Measure selection frequency, independent voice/canon criteria, factual
corrections, useful divergence (not paraphrased duplicates), reviewer time,
rework time, accepted outcome and cost **including rejected material**. Keep
an explicit no-change option. A human may deliberately keep a surprising
variant even when a model score dislikes it.

**Acceptance:** one preserved selected artifact, one rejected example with
reason, one canonical decision/receipt by the authorized writer, and one
negative test in which a candidate attempts to edit accepted canon. No
synthetic scorer success is called a human aesthetic win.

## SC-C3 — resumption, learning and stopping

Restart the writing session under another model/harness using only the frozen
pack, draft refs, author decisions and latest accepted canon, not the original
conversation. Preserve discarded candidates as reviewable evidence, but do not
automatically teach a future model that a fluent prior draft is canon.
Optional read-only summary/metadata may be exported through a versioned
source-linked observation for a later writing companion.

Stop expansion if multiple cheap passes increase editing time, produce
mostly redundant candidates, or create repeated canon mistakes. Report
mixed/unknown costs and the human preference evidence. A positive result
changes only Scribectl's native writing workflow configuration; it does
not change Vuoro model routing, Sprintctl acceptance or Workspace review.

**Validation/rollback:** run against a copied fixture vault; compare pack and
ratification hashes before/after; inject model failure, provider denial and
interrupted sync; restore previous native dispatch mode while preserving
proposals and original evidence. Live vault/canon operations stay under their
existing human authority. Bind these packets to SC-K01/02 served items
before execution; these labels are not new work identities.
