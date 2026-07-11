# Ratification, iterated — and agent-filled canon nodes

**Status:** proposal, 2026-07-11. Grounded in the first real-vault Phase C run
(Fertile Flames, scene `What Aune Brings Back`). Nothing here is implemented
except the fixes listed at the end; everything else is design for Phase D.

## What the run taught about ratification

The ledger model is right. The *decision* — this invention becomes canon, this
one doesn't, this one waits — is the single point where the writer's taste
enters the system, and making it a dated, append-only receipt is what keeps a
growing canon from silently rotting. None of what follows weakens that. The
goal is the opposite: reduce the mechanics around the verdict to near zero so
the verdict is the only thing the writer actually does.

The mechanics, as experienced from the writer's chair:

1. **Ratification is two disconnected hand-steps.** Paste the fact into the
   node's `## Ratified facts`, then append the receipt with `ratify --accept`.
   Nothing checks they agree; the run produced a `ratified_empty` state to at
   least *detect* the drift, but detection is not the fix.
2. **The unit of thought is a fact routed to a node; the unit of the tool is a
   free-text ledger line.** The writer mentally says "*the splice* → Crusade
   node, keep"; the tool wants a hand-composed sentence with wikilinks in it.
3. **Candidates are already structured, then get flattened.** Review reports
   end with an `## Introduced candidates seen in draft` list. Today the writer
   re-types each candidate into a shell flag — with shell quoting, which is
   hostile to exactly the person this tool serves. A writer in Obsidian should
   never meet an escaped apostrophe.
4. **Batching fights granularity.** The run accepted six inventions in one
   ledger line ("the trench practice bundle") because per-fact CLI calls were
   tedious. That trades away per-fact addressability — a later reject of *one*
   of those six has no receipt to point at. Cheap mechanics should make
   one-fact-one-receipt the path of least resistance.
5. **Provenance is manual.** The draft knows its `pack_sha`; the receipt should
   cite draft and pack without the writer typing either.

## The verdict inbox

One new writer-facing surface, lives in the vault, edited in Obsidian:

```
control/ratification/Inbox.md        type: ratification_inbox
```

Anything that proposes canon appends *structured candidates* to the inbox —
review reports, agent proposals (below), or the writer jotting one down
mid-draft. One candidate per line, checkbox syntax the writer already knows:

```markdown
- [ ] "the splice — trench term for rejoining the cadence" → [[Crusade narratives across fictional worlds]]
      (from [[What Aune Brings Back — draft 1]], pack 01318d2d1470)
- [ ] "Bay Nine ≈ forty throats" → [[Crusade narratives across fictional worlds]]
      (from [[What Aune Brings Back — draft 1]], pack 01318d2d1470)
```

The writer's entire job: tick `[x]` to accept, `[-]` to reject, leave `[ ]` to
defer, optionally rewrite the fact text in place (the rewrite *is* the
ratified wording — taste applied at the moment of decision). Then:

```
scribectl ratify --sweep
```

does everything mechanical in one motion, per accepted candidate:

- append the fact bullet to the target node's `## Ratified facts`
- append the receipt to the ledger, carrying source draft + pack sha verbatim
- move the candidate out of the inbox into the ledger's dated block
  (rejected/deferred candidates get their receipts the same way)

`--accept/--reject/--defer` flags stay for scripting and agents; the inbox is
the human path. Nothing is ever ratified that the writer didn't tick.

**The write-discipline question, faced squarely.** `--sweep` appends to a
canon node, and the standing rule is "nothing rewrites a note a human edits."
Position: the rule's purpose is that no *machine judgment* lands in canon.
A sweep write is the writer's own verdict executed — append-only, into exactly
one section, receipt-logged, and byte-traceable to a checkbox the writer
ticked. That is the same trust class as a ledger append. For the conservative
setting, `--sweep --dry-run` emits ready-to-paste blocks per node and the
paste stays manual; the default should be the real write, because the two-step
disconnect is the top observed failure mode.

## Agent-filled canon nodes

The motivating case sits in the vault right now: `Fertile Flames Saga` is a
deliberately deferred stub over ~35k words of scratchpad ore. Mining it by
hand is a full session of drudgery that produces *candidates* — which is
exactly the half of ratification that should never have been manual.

### The propose stage

Agents never touch `world/canon/`. They get a new quarantined output:

```
control/proposals/<node> — <source> — <date>.md     type: fact_proposal
```

A proposal note is structured ore-refinement: target node, source note, and a
list of candidate facts, each with a supporting quote, a confidence, and — the
part that makes agents genuinely useful — a `conflicts:` line naming any
existing ratified fact or timeline event the candidate rubs against.

```
scribectl propose --into "Fertile Flames Saga" --source "Fertile Flames Saga"
```

builds a **mining pack** (the extraction analog of the context pack, same
freeze-and-hash discipline): the source text, the target node's open
questions, every already-ratified fact in the project, and the world seed's
hard constraints. That scope is what keeps an independent agent honest — it
proposes against existing canon instead of beside it, and its conflicts lines
are pre-computed review work, not hallucinated authority.

### Independence and parallelism

Proposal files are one-per-agent-run, append-never, so N agents can mine N
sources concurrently with zero write contention — which also makes the flow
livesync-safe (files only, no shared mutable state, same property the Phase B
concurrency test verified). A reconciler agent can then read sibling proposals
targeting the same node and emit a merge proposal that flags overlaps and
contradictions *between agents* before the writer ever looks. The writer's
surface never changes: candidates land in the inbox, verdicts are checkboxes,
`ratify --sweep` executes them, and the receipt chain reads
`source → mining pack sha → proposal → verdict → node fact → context pack sha → draft`.

Lower-stakes node scaffolding — `One-line function`, `Open questions`,
`Story utility` — is authoring aid, not canon (packs ship only the facts
section plus the function line). Proposals may suggest these too; sweep
applies them under the same checkbox rule.

### Derived state, extended

- `fact_proposal` notes get status rows: `open` / `swept`.
- A stub node with open proposals reads `stub (3 candidates pending)` — the
  status table now tells the writer where the next ten minutes go, which the
  Phase C run showed is the real function of `status`.
- A scene blocked on a stub node points at the proposal queue instead of a
  dead end.

### What stays forbidden

- No auto-ratify, ever. An agent's confidence is input, not verdict.
- Agents write only under `control/proposals/` (and the inbox, via sweep of
  proposal candidates). `world/`, `structure/`, `body/` remain human-plus-fill
  territory.
- A proposal is not citable. Packs ship ratified facts only; an unswept
  proposal has exactly the standing of the ore it was mined from.

## Already fixed (this commit series)

The Phase C run's mechanical findings, closed in code: sha-suffixed frozen
packs (regeneration can no longer destroy a draft's audit trail), status
detail naming the unresolved links behind `blocked_unresolved_scope`,
`ratified_empty` divergence detection, pack-time warnings when in-scope nodes
ship facts without receipts, same-day ledger blocks deduplicated, blank
`[[ ]]` placeholders no longer parse as links, and the timeline template no
longer seeds a phantom event into every pack.

## Build order (proposed Phase D slice)

1. `ratify --sweep` + inbox parsing — kills the two-step disconnect and the
   shell-quoting wall; smallest change with the largest writer payoff.
2. Review-report template gains machine-parsable candidate lines that
   `--sweep` can lift into the inbox (or reports write to the inbox directly).
3. Mining packs + `propose` + `fact_proposal` status rows.
4. Reconciler pass, only once ≥2 sources are actually being mined.
