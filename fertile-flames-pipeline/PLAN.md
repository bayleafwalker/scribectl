# Build plan

## Phase 0 — substrate (done; this repo)

The load-bearing machinery and a runnable fixture. Built and contact-tested:

- Eight artifact templates (`templates/`) — the reusable contracts.
- Vault parser, timeline parser, **context-pack assembler**, **state projection**.
- `ff status` and `ff pack` run green against the fixture; pack pulls spine,
  ratified-facts-only canon, prior timeline events, voice, exclusions, flags
  unresolved scope, and freezes a sha.

Two design decisions baked in here that depart from the spec doc, on purpose:

1. **Status is derived, not stored.** No `status` / `draft_status` /
   `canon_level` enums to hand-flip and forget. `project.py` computes state from
   the vault (draft exists? clean review landed? listed Accepted in the ledger?).
   A status field you maintain by hand lies the moment you're mid-flow.
2. **The timeline is a first-class canon artifact.** `review_canon` was told to
   catch timeline bugs with no timeline to check. The assembler now pulls prior
   events by actor/location, so chronology — the axis prose actually drifts on —
   has an oracle.

## Phase 1 — the vertical slice (do this next, by hand)

Prove canon survives one fill. Do not build more tooling first.

1. Create `Lower Ashmarket` as a canon node (it's the deliberately-unresolved
   scope link — `ff status` will flip Scene 01-01 to `ready_for_fill`).
2. `ff pack "Scene 01-01"` → feed pack + card to a `body_fill` agent.
3. Rework the draft yourself. Save under `body/drafts/` with `type: draft` and a
   `[[Scene 01-01]]` link so the projection sees it.
4. Run `review_canon` against the timeline, `review_voice` against the exemplars.
   Emit reports under `reviews/`.
5. Append accepted/rejected/deferred inventions to the ratification log.

If state holds through that loop and the prose sounds like you, the architecture
is real. If it doesn't, no orchestration saves it.

## Phase 2 — mode discipline

- `refactor`: paragraph-scoped only, never "make better." Preserve beats + facts.
- `discover` / `scaffold`: emit stub nodes with Open questions, not final canon.
- Keep review *firing* automatic but review *consumption* manual — auto-consumed
  reports become an auto-advancing loop, and you're back at resolution-aftertaste.

## Phase 3 — scale

- Dataview projections in Obsidian mirroring `ff status` (folders stay dumb).
- Wire the modes to your `.agents/skills/` dispatch pattern: assembler as the
  context step, fill/review/refactor as delegated skills, coordinator never
  authoring. Same plan/build/review shape, vault as the work surface.

## Deliberately NOT built

- **No status enums** — derived instead (see Phase 0).
- **No empty stub farm.** Templates + a minimal runnable fixture, not 40 hollow
  notes that simulate progress.
- **No autonomous chapter iteration** — converges on smooth generic prose.
- **No auto-canon-from-prose** — schema drift in a cloak.
- **No writers-room multi-agent.** One model invents, another agrees, a third
  launders the agreement into a worse fact.

This machine can manufacture the *feeling* of a novel — large, consistent,
unread. Its honest job is deleting the consistency drudgery so your taste carries
the load. The seed, the structure calls, the ratification gate, and the
is-this-good judgment stay yours.
