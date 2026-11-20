# First Ice, iteration 6: one oracle for reviewer and voicer, one moment per shared sound, the delivery made concrete

**Question.** [Iteration 5](../2026-11-19-first-ice-iteration-5/README.md)
left seven findings and two questions for the sheet's author. This iteration
answers the questions, acts on the findings that have a fix, and re-voices
both chains from scratch:

- Every rule the canon reviewer applies must reach the voicer. The clock rule
  had been in the timeline preamble only, and it cost five failures.
- "A full room for a Saturday" was a new kind of cue commentary: what is usual.
- One sound heard from both positions landed on two seconds: the Thursday horn
  at 18:12:40 at the landing and 18:12:50 at the café.
- The three-evening listener read Thursday's "beans tomorrow" against
  Friday's delivery and called it an inconsistency.

**Verdict: four of the five criteria are met. The fifth missed by one card,
and a new failure mode surfaced.**

- The horn is one sound: [18:12:40] at both positions.
- The delivery holds together. Thursday runs short of cream and cuts
  yesterday's bread; Friday's crates bring bread, milk, tins and coffee. The
  three-evening listener connected the two on its own ("Then no cream with
  the pie", setting up the Friday delivery) and reported no inconsistency.
- No cue commentary and no repeated speech.
- The Saturday-only listener guessed right at low confidence ("the ferry
  may not be running and a bus has replaced it"). It would tune in again to
  hear the landing "to learn whether the ferry runs".

The canon reviewer now quotes the voicer's own clock rule from the pack when
it flags a lead-in. One lead-in still got through, in 20 voicings, and was
clean on resample. That misses criterion 1 as written.

The new failure mode: **a candidate nobody had ruled on became precedent.**
The first landing chain was canon-clean 5/5, but its first fragment heard a
faint car door up on the road. The reviewer queued "the road can be heard from
the landing" as a candidate. Before anyone ruled on it, each later landing
fragment cited the one before and added passing traffic. The road rule had
held for four iterations. I ruled against the candidate and re-voiced the
landing chain.

## Author calls

The two questions iteration 5 left open, answered before voicing:

- **Should a first-time listener be able to name the change? No.** Naming it
  on Saturday alone would take a told line, which the series rejects, or new
  events written to serve the listener. The Saturday-only listener is judged
  instead on whether its curiosity points at the right absence. In iteration
  5 it did: it wanted the landing "for ferry sounds". Its confidence stays a
  signal, not a criterion.
- **How legible should the shortage be? Unsaid in speech, concrete in
  objects.** The Thursday voicer wrote "the beans, then, tomorrow" because the
  sheet never said what the delivery carries; its own notes say "the pack
  doesn't say what the delivery was supposed to contain". Friday's voicer
  invented different goods. What a delivery brings is now ratified canon, so
  what Thursday goes without and what Friday unpacks are the same goods, and
  nobody has to say why.

**Acceptance criteria**, set before voicing (sprint item #2923):

1. no lead-in timing finding, and every card clean within one resample with
   no repair;
2. SYNC passes: the horn at [18:12:40] in both Thu 1815 Café and Thu 1820
   Landing;
3. cue commentary 0 by the lexicon, and no listener calls a cue line
   narration;
4. Thursday's and Friday's delivery goods come from the ratified list, and
   the three-evening listener reports no delivery inconsistency;
5. iteration 5's gains hold: café 19:40 Friday against Saturday at or below
   43% / 0.39, no invented names, the leak oracle passes, and Saturday is not
   heard as a replay.

## What changed

| Finding | Fix |
| --- | --- |
| The reviewer applied a rule the voicer never saw | Engine: the canon reviewer reads the standing timeline, `scribectl timeline` (what replay keeps, corrections applied, prose dropped), instead of the file. Rules about how events are voiced now reach the reviewer only through the pack, which is what the voicer reads. Superseded lines no longer reach it either (`c6676c6`). |
| One shared sound, two moments | Engine: a timeline position may carry a sub-position after a dot (`B1.C1.S1812.40`), sorting inside its unit; listening sets read it as a second. Fixture: a supersede gives the horn its own moment at 18:12:40 and starts the boarding at 18:14. Voice canon: a time with seconds is that second wherever it is heard. Check: `SYNC` flags a pinned pack event inside the window with no cue on its second (`c6676c6`, `275c2ac`). |
| "What is usual" as cue commentary | Voice canon (fixture and template): the commentary bullet names what is usual or unusual for the place or the night. The lexicon catches usual/unusual, "as always", "as ever" and "for once" (`275c2ac`). |
| Delivery goods invented per fragment | Café staff: a delivery comes in crates of bread, milk and cream, coffee and tinned goods, ratified from iteration 5's review candidates; Thursday's beans were rejected as one fragment's prop (`275c2ac`). |
| Road traffic at the landing (found this iteration) | Landing: the inlet road is out of earshot, no traffic and no car doors. The candidates saying otherwise were rejected. `SYNC` now compares only seconds pinned on the card's own evening (`dc1f9f0`). |

Findings left alone, with reasons:

- **Landing opening convergence:** a bed phrase. Watch it rather than act on
  it.
- **Radio notices read as told:** a notice is told by nature, and the timeline
  records the operator's official explanation. The wording ("Their reason: …")
  is the voicer's; no rule change.
- **The café's 19:30–19:40 window is crowded:** the bus and its passengers are
  the sheet's events in that window. Thinning it would be a sheet change made
  for pacing, so it is left for the author to weigh against the listeners'
  comments.

## How it was voiced

Two chains, one per listening position, oldest first, in fresh vaults copied
from the fixture. A card that failed canon review was resampled at once,
before the next card was built, as in iteration 5. Each resample built the
same pack as its first attempt.

- **Café chain:** 9/10 clean on the first pass. Friday 20:10 needed one
  resample. Its delivery was first heard at 20:05:00, on its recorded time.
  The finding was that coffee and tins arrived in a cardboard box, while the
  newly ratified fact says a delivery "comes in crates". The fact is read
  literally, packaging included.
- **First landing chain:** 5/5 clean on the first pass, Thursday 18:45
  included (two failures in iteration 5). Four of the five fragments put the
  road within earshot, though:
  - Thursday 18:15 heard "a car door, faint, somewhere up there";
  - Thursday 19:15 added a passing car, citing it;
  - Friday and Saturday 18:20 followed.

  Three of the voicers asked in their notes whether the road should be heard,
  and the reviewers queued the matching candidates. The chain is kept in
  `first-landing-chain/` and was never heard.
- **Landing chain, re-voiced** after the road ruling: 3/5 clean on the first
  pass, and both failures were clean on resample.
  - Thursday 18:15: a passenger says the ramp has "gone icy" at 18:14. That
    puts part of the closure's cause before the slush, and the reviewer cited
    the pack's "Nothing causal" constraint.
  - Thursday 18:45: water is "a little thick in the slap" at 18:35:30,
    before the slush begins at 18:37. The reviewer quoted the voice canon's
    clock rule from the pack: "Nothing of it is heard earlier, not even its
    approach."

Failed first attempts are in `resampled/`. There was no repair: every final
draft is a chain draft.

## Checks and results

```bash
uv run python docs/experiments/2026-11-19-first-ice-iteration-2/check_cue_sheets.py docs/experiments/2026-11-20-first-ice-iteration-6
uv run python docs/experiments/2026-11-19-first-ice-iteration-3/check_repetition.py docs/experiments/2026-11-20-first-ice-iteration-6
```

| Check | Iteration 4 | Iteration 5 | Iteration 6 |
| --- | --- | --- | --- |
| Packs: leak oracle | 22/22 | 16/16 | 20/20, first landing chain included |
| Scripts heard: window, order, anchors, leaks, water, road, names, new names, **sync** | 15/15 as recorded | 15/15 | 15/15. Thursday 18:45's `ramp` anchor flag is "beneath the ramp" naming the place at 18:41:20; the attempt starts at 18:43:00. A heuristic false positive. The first landing chain flags `ROAD@LANDING` 4/5. |
| Pinned second shared by both positions | not checked | horn 18:12:40 vs 18:12:50 | **[18:12:40] at both** |
| Lead-in timing findings | 2 | 3, plus 1 repeat | 1 in 20 voicings |
| Near-verbatim speech repeats | 11, all rituals | 1, a ritual | 0 |
| Cue commentary | 0 | 1 | 0, with the wider lexicon |
| Cue clauses shared by 3+ fragments | 29 | 24 | 22 |
| Structural echo, café 19:40 Fri vs Sat (shared timestamps / cue text) | 65% / 0.56 | 35% / 0.29 | **30% / 0.23** |
| Structural echo, landing 18:20 Fri vs Sat | 20% / 0.25 | 15% / 0.38 | 8% / 0.21 |
| Canon review, first pass | 12/15 | 12/15 | 12/15 in the final record, 17/20 across all voicings |
| Three-evening listener | high; Saturday "a replay with small variations" | high; "the pull is gentle"; shortage not tied to the delivery | **high**. Saturday "did pull me in". The cream shortage is tied to Friday's delivery. The bus arrival "repeats almost beat for beat". |
| Saturday-only listener | low-to-medium | low, "I can't say what has changed" | **low, and right**: ferry not running, bus instead. It would return to the landing "to learn whether the ferry runs". |

## What held

- **One oracle.** Every canon finding cites the timeline's events or a rule
  that is in the voicer's pack. There are no preamble conventions any more,
  and the reviewer never saw a superseded line. The one lead-in finding
  quotes the pack's own clock rule back to the draft.
- **One moment per shared sound.** The supersede moved the horn and the
  boarding without editing a line, and both positions put the horn on its
  second.
- **The shortage reads through objects.** Nobody explains it:
  - Thursday: "one and a half of cream", "Then no cream with the pie",
    "Yesterday's will do for toast";
  - Friday: "Bread on top?", "Milk in the fridge first";
  - Saturday: "Milk's fine till Monday".

  The listener linked them, and nothing was told.
- **Echo keeps falling.** Café 19:40 is at 30% / 0.23 and the landing at
  8% / 0.21. The landing's opening clause still converges, though: Friday
  and Saturday 18:10 both begin "Wind off the water, cold". It is a bed
  phrase, still watched.

## What did not, and findings for the next iteration

1. **A candidate nobody has ruled on becomes precedent.** "Already heard"
   ships earlier clean fragments as the listener's memory, and voicers read
   them as evidence of what the place sounds like. A canon-clean fragment can
   still carry a candidate the writer has not ruled on, and the next fragment
   builds on it. One structural fix is a candidate: an earlier fragment ships
   as already heard only once its review's candidates are ruled. The writer's
   taste gate would then come before the precedent, not after.
2. **"Already heard" can hide the room's own history.** The filter drops any
   earlier fragment whose source knew more, and the café staff never heard the
   horn. So Thursday 19:35 heard no earlier café fragment and repeated the
   Thursday 18:15 dedication: Sirkka, for her sister. "Her sister" is also the
   canon's own example in the Evening programme node, so both voicers reached
   for it. Two separate fixes: vary or drop the example, and decide whether
   the radio's past dedications belong to the room rather than to a source.
3. **A ratified fact is read to the letter.** "Comes in crates" made
   packaging canon, and a cardboard box failed review. Ratify the goods, not
   their packing, when only the goods matter.
4. **A recurring event's onset now converges.** The clock rule puts the first
   sound on the recorded minute. Friday's and Saturday's buses then step
   through the same three beats: engine at 19:35:00, brakes at :15, doors at
   :30. The listener heard it "almost beat for beat" and took it as routine,
   not replay: "the bus is now a normal sound". Watch it. A bus does arrive
   the same way every night.
5. **"What is usual" moved into speech.** "Full house." (a regular, Friday)
   was named as a line for the listener. It is overheard speech, not cue
   text, so the rule does not reach it, and it reads as natural. Watch it.
6. **Lead-ins are rarer, not gone.** There was one in 20 voicings. A related
   failure appeared too: a passenger's "gone icy" foreshadows the cause.
   Both are clean on resample, and the reviewer catches both from the pack.
7. **Unchanged:** radio notices are heard as told (accepted, see above). The
   Saturday radio at 19:50 is "a man talking", which two iterations of
   listeners have noticed.

## Closeout assessment

- Accepted outcome: two author calls made, four iteration 5 findings
  implemented, one new finding fixed by ratification, both chains voiced
  and re-judged (sprint item #2923).
  - Criteria 2–5 are met.
  - Criterion 1 missed by one lead-in finding. Every card was clean within
    one resample, with no repair.
- Review findings:
  - first-pass canon failures: 1 literal-fact mismatch, 1 causal
    foreshadowing and 1 lead-in;
  - the check caught the road precedent across 4 fragments, and the
    reviewer only queued it as candidates.
- Repairs: 3 resamples, all clean. The landing chain was re-voiced once
  after the road ruling.
- Spend (estimate): 23 fills and 23 canon reviews on Opus 5.5, plus 2 blind
  listeners on Sonnet 5.5. Wall time was not measured.
- Unknown: audio. Every check read scripts, and every listener was a model,
  not the writer.
