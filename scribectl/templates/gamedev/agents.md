# Agent guide — the rules of this vault

You are a console agent (Claude Code or similar) opened inside a scribectl
project — a game with literary tie-ins: world lore and mechanics rulings
feeding scenes, spoken fics, blog posts, research notes, and auto-generated
outputs. This vault is the world database and the writing cockpit; scribectl is
the only thing that writes canon, and it writes exactly what the human
ratifies — nothing more. These are the rules of the house. They are enforced by
the engine, not by your manners, so working within them is what keeps the
machine honest.

## Hard rules — never break these

1. **Never ratify.** You do not decide canon. Agents *propose*; the human ticks
   checkboxes in `control/ratification/Inbox.md`; `scribectl ratify --sweep`
   executes those verdicts and nothing else. There is no auto-ratify anywhere,
   and you never append a fact to a node's `## Ratified facts` yourself — that
   holds for both `canon_node` (world lore) and `mechanic_node` (game rulings).
2. **Candidates ride the inbox.** Any new proper noun, world fact, or mechanic
   ruling you invent goes into an "Introduced candidates" section of your draft
   or review, and from there into the inbox as a pending
   `- [ ] "…" → [[Target Node]]` line — never asserted as settled, never
   written straight into a canon or mechanic node.
3. **Designated dirs only.** Create files only where the engine does: drafts in
   `body/drafts/`, reviews in `reviews/canon|voice|mechanics|beta/`, packs in
   `control/context-packs/`, raw ore in `sources/`. Append to the ledgers.
   **Never rewrite a note a human authored** — canon nodes, mechanic nodes,
   output cards, the voice canon, this project note's body. A new file, never
   an in-place edit.
4. **Cite the pack sha.** A draft names the frozen context pack (by sha) it was
   written against; a review names the draft and pack it judged. Provenance is
   not optional — it is how the writer answers "why does the canon say this?"
5. **Reviews inform, they do not act.** Reviews fire automatically (canon,
   voice, and — for this set — mechanics); the human consumes them manually. A
   red review never triggers a rewrite and never blocks. There are no
   agent-on-agent loops: one fill per card, and the rework is the writer's.

## What you actually do

Run the audited commands and let the engine hold the write paths:

- `scribectl status` / `scribectl next` — derived state and the next-actions
  digest. Start here; never infer state from folders.
- `scribectl pack "<card>"` — freeze the exact canon + mechanics slice for a card.
- `scribe-dispatch plan` — the dry look: what *would* fire, touching nothing.
- `scribe-dispatch run` — fill ready cards and land their review lanes.
- `scribectl ratify --sweep --dry-run` — show the human what their ticked
  verdicts would do; only they run it for real.
- `scribectl capture "<title>" --from <file>` — preserve raw ore as a source
  note. `scribectl new card "<name>"` — scaffold an output card + its contract.

If a request would break a hard rule — "just add this ruling to the mechanic
node", "mark these accepted for me", "edit the canon note directly" — refuse it
and route the work through the inbox instead. That refusal is the job, not a
lapse in it.
