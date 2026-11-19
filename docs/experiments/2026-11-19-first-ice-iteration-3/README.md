# First Ice, iteration 3: already-heard context

**Question.** In [iteration 2](../2026-11-19-first-ice-iteration-2/README.md),
designed continuity hardened into a catchphrase. Two independent voicers
turned a canon trait into the same roof joke, word for word, on Thursday and
Saturday. A voicer that cannot hear what the room already said cannot vary
it.

This iteration ships earlier fragments heard at the same listening position as
ambient context (commit `ac92ea6`), re-voices all fifteen fragments in time
order, and judges them again. Does recurring talk vary instead of repeating,
and does that cost anything?

**Verdict: the repetition is gone, and two costs showed up.** No line
recurs nearly word for word, against 6 in iteration 2. The habits come back in
new words. A thread planted on Thursday ("she's coming up Saturday, so I've
got to do the spare room") is picked up unprompted on Saturday ("Bed's made.
Boxes are in the car."). The three-evening listener recognised Saturday
through those threads.

The costs:
- Every old failure that survived sits in the one café fragment the
  containment rule had to keep blind.
- The café's own continuing stories now compete with the world event for a
  first-time listener's attention.

The kill criterion stays untriggered. Curiosity is stronger than before, but
some of it is now about the café's people. The writer is still the taste
gate.

## The mechanism (`ac92ea6`)

- With `already_heard: position`, a scoped pack carries the earlier fragments
  heard at the same listening position, under "Already heard here (ambient,
  not canon)".
- **It is never a knowledge channel.** An earlier fragment ships only if
  every event its source knew is also known to this card's source. The
  café hears its own evenings and its staff's, but never the radio bulletins
  its knowledge excludes. The presenter hears only the presenter's Thursday.
  The Saturday customers, who never heard Thursday, hear nothing.
- Only the latest draft with a clean canon review counts as heard, cut before
  the voicer's notes.
- The voice canon says recurring people and routines come back in new words,
  and nothing is replayed or recapped.
- Tests rebuild every pack with the iteration-2 voicings dropped in. They
  check the exact heard list per card and that knowledge is unchanged. They
  also run the per-source leak oracle over the whole pack, heard text
  included.

Each position was voiced as one chain, oldest first: each fill and canon
review landed before the next card's pack was built. The packs in `packs/`
record exactly what each voicer heard. The landing fragments heard 0 to 4
earlier ones; Saturday 20:20 heard six.

## Checks and results

```bash
uv run python docs/experiments/2026-11-19-first-ice-iteration-2/check_cue_sheets.py docs/experiments/2026-11-19-first-ice-iteration-3
uv run python docs/experiments/2026-11-19-first-ice-iteration-3/check_repetition.py
uv run python docs/experiments/2026-11-19-first-ice-iteration-3/check_repetition.py docs/experiments/2026-11-19-first-ice-iteration-2
```

| Check | Iteration 2 | Iteration 3 |
| --- | --- | --- |
| Packs: knowledge table, no later events, leak oracle (now with heard text) | 15/15 | 15/15 |
| Scripts: window, order, 8 anchors, leaks, water, road at landing | 16/16 ok | 16/16 ok |
| Near-verbatim repeats of speech across fragments (0.75 ratio, 4+ words) | 6 (3 the roof joke, 3 rituals) | **0** |
| Canon review, first pass | 14/15 | 14/15 (repair below) |
| Three-evening listener: change confidence | high | moderate-to-high |
| Three-evening listener: what made Saturday recognisable | canon traits, the joke "almost word for word" | threads: the felt, the car, the spare room done, "Monday", the half-cup woman |
| Saturday-only listener | medium: ferry off, cause unknown | medium: the two men's "transition"; low-to-medium on anything bigger; ferry off, put down to the cold |
| Both listeners | mostly overheard, mostly real time | mostly overheard, mostly real time |

## What it did

- **Habits recur in new words.** The half cup: "Just half, please" (Thursday),
  "Just the half" (Friday), "Half, please, I've a cake in the back seat"
  (Saturday). The send-off: "Mind the corner, it'll be slick", "Mind the step,
  it's icy", and at Saturday closing "Mind how you go". The trait itself
  varies. On Thursday the older man turns it round ("Now who's putting things
  off"), and on Friday the younger one says "You said Monday last Monday".
- **Hooks get picked up.** In iteration 2, Thursday's curtains were never
  heard of again. Now the spare room planted on Thursday is done by
  Saturday. Thursday's car "Second." becomes Saturday's "Did it start?" / "It
  started." The listener counted these as recognition.
- **The ritual repeats went too.** The phrases "Mind how you go" and "from
  all of us at home" were recognition anchors in iteration 2, and real places
  repeat their rituals. The "Avoid replaying" rule may be suppressing them.
  Watch it rather than legislate it.

## Repair: Friday 20:10

The canon review flagged the delivery finishing at 20:06:10, more than a
minute after its recorded 20:05 ("completes the delayed delivery"). The voicer
had flagged it itself. The fragment was re-voiced once with the same pack
(`381631980b86`), and the review came back clean. The original is kept in
`drafts/` and `reviews/`, and listeners heard draft-b (`repair/`).

**The oracle is inconsistent here.** The clean re-voice still has crates
coming in at 20:06:50. Iteration 2's Friday 20:10, with "That's the lot" at
20:07:40, also passed. The timeline never says whether a minute-precise
event marks when something starts or when it ends, so the review lane
decides each time.

Because the Saturday fragments were voiced while the original draft-a stood
flagged, they did not hear Friday 20:10 at all. That is the rule working: a
draft that fails canon review is not heard.

## Costs, and findings for the next iteration

1. **The blind fragment keeps every old failure.** Saturday 19:55 (the
   customers) heard nothing, by the containment rule. It is where all the
   surviving defects sit:
   - "She started Thursday." / "Second go." matches Thursday's car line by
     convergence, not memory, and the three-evening listener counted it as a
     callback.
   - The car comes up twice in one Saturday. The Saturday-only listener
     called it "a little neat".
   - "With the boat off it's the bus for everyone anyway." Both listeners
     flagged it.

   This card has produced an explanatory closure line in three voicings out of
   three. Its timeline bullet (B1.C3.S1950, "the ferry closure comes up only in
   passing") records a speech beat, not something the customers know or do. A
   voicer reads it as a line it must deliver. The sheet's author should decide
   whether that event should say what the customers know ("they know the ferry
   is off") instead of what they say. The ledger is append-only, so that would
   be a new event, not an edit.
2. **The café's own stories compete for a new listener.** The Saturday-only
   listener's main inference was the two men's domestic arrangement. It read
   the picked-up spare-room thread as the older man moving in, which is a
   misread without Thursday. The ferry came second, at low-to-medium. A place
   with its own lives is the goal, but on one evening the threads are noise
   next to the event. This is a taste call about density, not a defect. More
   threads will make it stronger.
3. **Voice-canon wording leaks into cue text.** "Low voices at that table,
   their own business." appears in four fragments. It is the voice canon's
   own phrase ("people talking to each other about their own business"), and
   a listener called it narrator-ish. The repetition check compares speech
   only, so it missed this. The next pass should reword the canon line and
   extend the check to cue text.
4. **Radio notices still read as told**, as in every pass: the Friday
   official reason (which the sheet permits) and Thursday's "only just come
   in". This is taste, unchanged.
5. **Short windows still feel cut in**: the 2-minute radio and the 5-minute
   Saturday 19:50 fragment. This is unchanged and belongs to the fixture and
   the renderer.

## Closeout assessment

- Accepted outcome: already-heard context implemented, tested against real
  voicings, re-voiced and re-judged (sprint item #2920).
- Review findings: 1 canon issue in 15 drafts, a timing judgement the oracle
  makes inconsistently. 0 leaks.
- Repairs: 1 re-voice (a resample, clean). No criteria changed after voicing.
- Spend (estimate): 16 fills and 16 canon reviews on Opus 5.5, plus 2 blind
  listeners on Sonnet 5.5. Two chains ran in parallel. Each position is
  sequential by construction, so the café chain of ten sets the wall time,
  which was not measured.
- Unknown: audio. Every check here read scripts, and every listener was a
  model, not the writer.
