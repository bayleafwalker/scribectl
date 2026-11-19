# First Ice, Thursday: the first voicing pass

**Question.** Event sheet 001 ("First Ice") went into scribectl as a
deterministic fixture. Each fragment was written only from its source's
scoped knowledge. Does Thursday sound like a place where something happened,
or like a radio drama explaining a story?

**Verdict: a place.** Two blind listeners heard none of the canon, cards or
event sheet. Both took it as overheard rather than explained. Both inferred
the actual causal chain from ordinary traces, and both said they would come
back. The first-proof gate passes for Thursday. The kill criterion belongs to
Saturday and is still untested. The writer is still the taste gate:
everything here is evidence for that decision, not the decision itself.

## Setup

- Fixture: `fixtures/listening-post/` holds three evenings of world truth and
  seven Thursday fragment cards (landing ×3, café ×2, the radio heard in the
  café, café staff).
- Engine: the `listening` set, `knowledge: scoped`. A pack holds only what
  reached its source before its clock: events it took part in, events at it
  when it is a place, and events it `heard:`. Scoped packs print where and
  what, never who else knew.
- Voicing: `scribe-dispatch run --runner claude --model claude-opus-5-5`. Each
  fill saw its card, its contract and its frozen pack, nothing else. Every
  draft carries its `pack_sha`, and all seven packs are in `packs/`.
- Review: `review_canon` on each landed draft. It is the only lane that sees
  the whole timeline, which makes it the omniscient oracle.

## Checks and results

| Check | Result |
| --- | --- |
| Pack scoping vs the sheet's knowledge table (`tests/test_listening.py`) | 7/7 exact |
| Leak oracle over packs (per-source forbidden terms, no Friday events) | 7/7 clean, after the five repairs below |
| Leak oracle over voiced scripts | 7/7 clean |
| Length vs card target | all within 4 s (45–88 s) |
| Canon review | 6 clean, 1 issue (phantom engine) |
| Blind listener, both positions | medium-high: slush → last ferry cancelled → café rationing |
| Blind listener, café only | medium: ferry stopped → supplies cut off |

## What the fragments did well

- **The ferry is recognisable before its absence matters.** The 18:10 landing
  fragment carries the whole arrival: an engine coming and going with the
  gusts, one horn, the ramp, passengers off and on, departure. The café gets
  a single faint horn under the piano.
- **The incident stays physical and unexplained.** At 18:45 the slush arrives
  as texture, and Leena's ramp attempt is all sound: a crunch, a rock, "Hm."
- **The bulletin is mundane.** "A notice from the ferry operator, just in …
  Right. Back to the music." Nobody in the café reacts, and the café-only
  listener found that silence interesting in itself.
- **The late delivery is noticed only by a careful listener.** "Take the
  rolls off the board. Do the soup with toast." / "Toast we've got." Nobody
  says why.

## Defects found, and what was done

1. **Phantom engine (correctness).** At [0:43] of 19:35 café staff: "Very far
   off … something on the water, a low engine note". The timeline has nothing
   on the water then. The canon review caught it, and both blind listeners
   took it as possible evidence that the ferry was still running. That is the
   failure the sheet warns about: improvised, contradictory evidence. The
   voicer read "the ferry is heard only distantly here" as permission for
   ambient maybe-ferry sounds.
   *Repair:* the criteria were strengthened, not the draft hand-edited. The
   World Seed now says a sound from the water is evidence, and the café node
   says "*when the ferry comes*, she is heard only distantly". The original
   draft and review are kept in `drafts/` and `reviews/`. See
   [Repair check](#repair-check).
2. **Leaks found while building the fixture (before any voicing).** The pack
   oracle found five: three static node facts ("Leena reports conditions" →
   primes a phone call at the landing; the café's supply route reaching the
   presenter; the road being "usable in winter"), the voice canon's own bad
   example ("ice cracking like gunshots" put *ice* into every pack), and pack
   lines listing co-actors (the presenter learned that Leena felt the cold).
   Reading the cards found a sixth. The radio card said "say nothing about
   ice, the season, replacement transport", handing the hidden truth to the
   writer it hides it from. **Cards and static facts are leak vectors too:**
   attach each fact to whoever knows it, and phrase exclusions from the
   source's knowledge, never by naming what it lacks.

## Open, for the writer's taste gate

- **The radio repeats the notice** ("That's tonight's final crossing,
  cancelled."). Both listeners heard the repeat as aimed at them. It is a
  real radio habit, so this is taste, not canon, and it was left unlegislated.
- **"No hot chocolate till it's here" / "I'll tell them if they ask"** lean
  slightly explanatory for one listener each.
- **Introduced candidates** waiting for the inbox: the Lehtinens'
  dedication, chalkboard menu, rolls and milk in the late delivery, two staff,
  the landing's metal ramp and plank decking. None of them is causal except
  "rolls and milk", which the voicer flagged itself.

## What independent voicing cannot hold (next design question)

- **Shared ambient state drifts at the seams.** The radio's running order
  (an accordion at 19:15, a guitar ending at 19:20, another accordion),
  the presenter becoming "a man's voice" only at 19:35, and "end of the
  month" turning up in two independent fragments. None of it is canon and none
  of it is per-fragment. Options: voice each position's evening as one
  sequence, or ship the previous fragment at the same position as
  already-heard context. Ratifying a playlist would be the wrong tool.
- **Time is compressed.** Every voicer squeezed a 10-minute window into 45–90
  seconds, so the evening plays as a montage, not an evening. The Listening
  Room would want events at true clock offsets over a continuous bed. That is
  a renderer question, and it decides what a "fragment" should be.
- **Bulletin timing.** The radio's voicer noticed that the 19:20 bulletin
  cancels a 19:12 crossing that has already not happened. It reads as
  realistic institutional lateness, which suits the sheet, but the sheet's
  author should know it is load-bearing.

## Repair check

The café-staff card was re-voiced once against the strengthened criteria, in
a fresh copy of the fixture (`repair/`, pack `9783fb67b02b`). The canon review
is clean, there is nothing on the water, and the oracle finds no leaks. The
shortage got quieter: "Leave the crates where they were. Room for them when
it comes."

It also over-corrected. The first wording ("a vessel, vehicle or voice the
pack does not put there is a new event … boats, horns and engines are not
[free]") led the voicer to drop ordinary road traffic, reasoning that a
passing car is an engine. Road traffic is canonically audible at the café.
The rule was narrowed to what the defect was about: *a sound from the water*
appears only if the pack puts it there, while room texture and passing road
traffic stay free. **The narrowed wording has not been re-voiced yet.**

## Closeout assessment

- Accepted outcome: the fixture, scoped packs and Thursday voicing (sprint
  item #2917).
- Review findings: 1 canon issue in 7 drafts; 6 leaks found by the oracle or
  by reading, all before voicing.
- Repairs: 5 fixture/engine repairs before voicing; 1 criterion strengthened
  after (verified by one re-voice, then narrowed, and the narrowing is unverified).
- Spend (estimate): 7 fills + 7 canon reviews on Opus 5.5, 2 blind listeners
  on Sonnet 5.5, and one re-voice (fill + review).
- Unknown: how this sounds as audio. Every check here read scripts.
