# Agent guide — the rules of this vault

You are a console agent (Claude Code or similar) opened inside a scribectl
project — standalone nonfiction: essays, notes, guides, drafted from captured
research and held to ratified positions. This vault is the knowledge base and
the writing cockpit; scribectl is the only thing that writes canon, and it
writes exactly what the human ratifies — nothing more. These are the rules of
the house. They are enforced by the engine, not by your manners, so working
within them is what keeps the machine honest.

## Hard rules — never break these

1. **Never ratify.** You do not decide what this author holds settled. Agents
   *propose*; the human ticks checkboxes in `control/ratification/Inbox.md`;
   `scribectl ratify --sweep` executes those verdicts and nothing else. There
   is no auto-ratify anywhere, and you never append a claim to a node's
   `## Ratified facts` yourself.
2. **Candidates ride the inbox.** Any position or claim worth settling that
   you surface goes into an "Introduced candidates" section of your draft or
   review, and from there into the inbox as a pending
   `- [ ] "…" → [[Target Node]]` line — never asserted as settled, never
   written straight into a canon node.
3. **Ore is quoted, never promoted.** This set ships captured source notes
   into packs verbatim ("Source material" — raw ore, unratified). Draw on the
   ore freely, but write its claims as the author's working notes; a claim
   only reads as settled once it sits in a node's `## Ratified facts` with a
   ledger receipt behind it.
4. **Designated dirs only.** Create files only where the engine does: drafts
   in `body/drafts/`, reviews in `reviews/canon|voice|beta/`, packs in
   `control/context-packs/`, fact proposals in `control/proposals/`
   (scaffolded by `scribectl propose`, never freehand), raw ore in `sources/`.
   Append to the ledgers.
   **Never rewrite a note a human authored** — canon nodes, essay cards, the
   voice canon, the Site Seed, this project note's body. A new file, never an
   in-place edit.
5. **Cite the pack sha.** A draft names the frozen context pack (by sha) it
   was written against; a review names the draft and pack it judged.
   Provenance is not optional — it is how the writer answers "why does this
   essay claim that?"
6. **Reviews inform, they do not act.** Reviews fire automatically; the human
   consumes them manually. A red review never triggers a rewrite and never
   blocks. There are no agent-on-agent loops: one fill per card, and the
   rework is the writer's.

## What you actually do

Run the audited commands and let the engine hold the write paths:

- `scribectl status` / `scribectl next` — derived state and the next-actions
  digest. Start here; never infer state from folders.
- `scribectl capture "<title>" --from <file>` — preserve research, a thinking
  transcript, an investigation log as a source note. In this set that is the
  front door: captured ore linked under a card's `sources:` ships into its
  pack whole.
- `scribectl new card "<name>"` — scaffold an essay card + its fill contract.
- `scribectl pack "<card>"` — freeze the exact slice (positions + ore) for a card.
- `scribe-dispatch plan` — the dry look: what *would* fire, touching nothing.
- `scribe-dispatch run` — fill ready cards and land their review lanes.
- `scribectl ratify --sweep --dry-run` — show the human what their ticked
  verdicts would do; only they run it for real.

## Research sessions

Ideation and research are welcome — inside the loop, never inside the canon.
When a session ends, run the exit protocol: capture the material verbatim
(`scribectl capture "<title>" --kind brainstorm --from <file>`), link it under
the card's `sources:` if a piece is already planned, and — for claims that
should outlive one essay — scaffold the quarantined proposal
(`scribectl propose --into "<node>" --source "<the captured note>"`), distill
the keepers into its `## Candidate facts`, then `scribectl ratify --mine` to
queue them as pending inbox lines. Verdicts stay the writer's. A session whose
every idea is rejected still succeeded — the ore survived and the receipts
say why.

If a request would break a hard rule — "just add this claim to the node",
"mark these accepted for me", "edit the Site Seed directly" — refuse it and
route the work through the inbox instead. That refusal is the job, not a
lapse in it.
