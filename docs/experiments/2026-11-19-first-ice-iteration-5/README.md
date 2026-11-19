# First Ice, iteration 5: a correctable timeline, recurring events heard afresh, regular requesters

**Question.** [Iteration 4](../2026-11-19-first-ice-iteration-4/README.md)
left three findings to act on:

- The closure line only shrank. Its timeline entry, B1.C3.S1950, recorded a
  speech beat (the closure "comes up only in passing"), and an append-only
  timeline could not take it back.
- Saturday 19:40 was rebuilt on Friday 19:40's frame (65% shared cue
  timestamps, cue text 0.56), and the listener heard "a replay with small
  variations".
- The naming rule removed invented names, and the dedications lost their
  texture with them.

Do the fixes hold, and what do they cost?

**Acceptance criteria**, set before voicing (sprint item #2922):

- café 19:40, Friday against Saturday, at or below the no-heard-context
  baseline of iteration 2 (43% shared timestamps, cue text 0.39);
- no invented names;
- every canon review clean within one resample per card;
- Saturday not heard as a replay.

**Verdict: the three fixes hold, and three of the four criteria are met.**

- The closure line is gone. The closure shows only in what the regulars do
  ("so it'll be the bus Monday, then"), and neither listener flagged it.
- Saturday 19:40 echo fell to 35% / 0.29, below the no-heard baseline. The
  three-evening listener heard Saturday as the same place with differences it
  noticed on its own ("the room was fuller", "the bus Monday"), not as a
  replay.
- Requester names are back, with no invented ones, and listeners followed
  them across evenings ("Ossi again").

Canon review missed its criterion. Friday 20:10 failed both attempts the way
it failed twice in iteration 4: the delivery is heard arriving seconds before
its time. The cause turned out to be an asymmetry between oracle and voicer.
The reviewer applies a timing rule that the voicer never sees. Fixing it
mid-iteration took one repair (below), and that asymmetry is this iteration's
main lesson.

## What changed

| Finding | Fix |
| --- | --- |
| Closure line, from a speech beat in the timeline | Engine: a timeline bullet that starts `supersedes: <position>` (or `<position>#<n>`) drops the earlier bullets there. The old line stays as history, and doctor warns about a supersedes that corrects nothing (`d3786bc`). Fixture: S1950 is corrected to "Customers, who know the ferry is off, make ordinary plans around the bus.", which keeps what they know and drops the direction (`a82a232`). |
| Saturday rebuilt on Friday's frame | Voice canon (fixture and template): something that happens again on another evening is heard afresh. Its recorded time holds, but what the ear catches around it belongs to this evening, and an earlier fragment is never a frame to re-dress (`a82a232`). |
| Naming rule costs texture | Evening programme: dedications come mostly from five regular listeners, read out by first name. Whoever a dedication is for goes by what they are to the sender (`a82a232`). |
| Invented names, checked only against canon people | Cue-sheet check: `NEW` flags a capitalised name mid-sentence that the pack never mentions. Run back over iteration 4, it finds seven invented names in six heard scripts, all voiced before the naming rule (`a82a232`). |
| The reviewer's timing rule is invisible to the voicer (found this iteration) | Voice canon (fixture and template): the first sound of an event, its approach included, comes at its recorded time and not before (`8461e1d`). |

## How it was voiced

As before, there were two chains, one per listening position, oldest first.
One thing changed in the protocol. A card that failed canon review was
resampled at once, before the next card was built, so later cards heard the
clean version. Iteration 4 did this in a second pass over the downstream
cards. Each resample built the same pack as its first attempt.

- **Landing chain:** 5/5 clean. Thursday 18:45 needed one resample: the
  ramp's latch and chain ran from 18:42:45, before the attempt at 18:43.
- **Café chain:** 9/10 clean.
  - Friday 18:30 radio needed one resample: the presenter added "by road",
    a detail the announcement never gave.
  - Friday 20:10 failed both attempts. The van is heard at 20:04:10, then the
    engine at 20:04:50, both before the delivery at 20:05.

The failed attempts are in `resampled/`. The second Friday 20:10 attempt stays
in `drafts/` and was never heard.

**Why Friday 20:10 keeps failing.** The timeline preamble says a heading's
clock is "when the event begins or is first perceived". The canon reviewer
reads the raw timeline, preamble included. The voicer's pack holds only the
scoped events and the voice canon's "Events sit at their recorded times", so
it hears an approach before the knock at the door. The preamble cannot simply
ship in packs: it summarises the whole event sheet, which would leak. So
across two iterations, five failures came from one rule that only the
reviewer could see:

- Friday 20:10, twice in iteration 4 and twice here;
- Thursday 18:45, here.

The voice canon now states the rule. Friday 20:10 was then re-voiced once
against it (`repair/`, pack `70368fe03e2a`). The engine is first heard at
20:05:00, and the review is clean. The other fourteen fragments predate the
amendment.

The Saturday fragments did not hear Friday 20:10, as in iteration 4, because
it was still flagged when they were voiced.

## Checks and results

```bash
uv run python docs/experiments/2026-11-19-first-ice-iteration-2/check_cue_sheets.py docs/experiments/2026-11-19-first-ice-iteration-5
uv run python docs/experiments/2026-11-19-first-ice-iteration-3/check_repetition.py docs/experiments/2026-11-19-first-ice-iteration-5
```

| Check | Iteration 2 | Iteration 3 | Iteration 4 | Iteration 5 |
| --- | --- | --- | --- | --- |
| Packs: leak oracle | 15/15 | 15/15 | 22/22 | 16/16, repair included |
| Scripts heard: window, order, anchors, leaks, water, road, names, **new names** | 16/16 | 16/16 | 15/15 as recorded; 9/15 under today's check (6 flag `NEW`, all voiced before the naming rule) | 15/15. The repair's `crate` anchor flag is the café's own crate at 20:01:10, a heuristic false positive. The unheard Friday attempt flags LEAK "ice" (road ice). |
| Near-verbatim speech repeats | 6 | 0 | 11, all rituals | 1, a ritual ("back to the music"). Shorter rituals recur below the four-word threshold ("Watch the bend"). |
| Cue commentary | 0 | 4 | 0 | 1: "A full room for a Saturday", flagged by both listeners. The lexicon gained "for a \<weekday\>" today; the earlier records score the same. |
| Cue clauses shared by 3+ fragments | 20 | 35 | 29 | 24 |
| Structural echo, café 19:40 Fri vs Sat (shared timestamps / cue text) | 43% / 0.39 | 23% / 0.50 | 65% / 0.56 | **35% / 0.29** |
| Structural echo, landing 18:20 Fri vs Sat | 17% / 0.25 | 31% / 0.23 | 20% / 0.25 | 15% / 0.38 |
| Canon review, first pass | 14/15 | 14/15 | 12/15 | 12/15 |
| Three-evening listener | high | moderate-to-high | high, full chain. Saturday "a pleasant coda more than a hook" and "a replay with small variations". | **high** on the ferry-to-bus change. Saturday "clearly the same place", "wasn't flat, but the pull is gentle". No replay. The supply shortage is no longer connected to the delivery. |
| Saturday-only listener | medium | medium on the two men, low-to-medium on more | low-to-medium: ferry off is "the best candidate" | **low**: "I can't say what has changed". It would tune in again "to listen to the landing for ferry sounds. I never heard a ferry". |

## What held

- **The correction works.** The superseded line stays in the timeline.
  Packs built after it no longer carry the stage direction (fixture test
  `test_superseded_entry_never_reaches_a_pack`). The canon reviewer read the
  raw timeline, both lines and the preamble, and judged both affected Saturday
  fragments clean. The customers now talk about the bus as a fact of the week:
  "so it'll be the bus Monday, then", "What's the sheet say for the morning
  one?".
- **Saturday is its own evening.** Echo is below what independent voicers
  produced with no heard context. The bus is still at 19:35, as canon says,
  and the frame around it is new. The listener's differences were its own:
  a fuller room, no ferry, the men's Monday bus.
- **Names recur by design.** Seven of the ten café fragments name one
  requester each. Voicers rotated through the pool using what they had
  heard; one fill note reads "earlier fragments already used Sirkka, Pentti
  and Raili". Listeners tracked the recurrences ("Ossi again", "Ossi's Friday
  dedication to a neighbour"). The Saturday-only listener wants to know "who
  Marjatta … and the shovel are". No invented name and no collision.
- **Repetition and convergence keep falling.** There is one four-word repeat,
  a ritual, and shared cue clauses are down to 24.

## What did not, and findings for the next iteration

1. **Every rule the reviewer applies must be in the voicer's pack.** The
   clock convention sat only in the timeline preamble, and it cost five
   failures over two iterations. It is now in the voice canon, but only one
   fragment was voiced under it. The next full re-voice is the test. A
   structural check is a candidate: list what `review_canon` reads that
   `body_fill` does not.
2. **A new kind of commentary.** "A full room for a Saturday" compares the
   room with what is usual. That is interpretation, and both listeners called
   it narration. The voice canon's commentary bullet names who-minds-what and
   who-reacts. "What is usual" belongs there too. The lexicon now catches the
   phrase.
3. **First-time inference keeps falling: low.** With the closure line gone,
   the Saturday-only listener can't name the change. It is curious about an
   absence, though: it wants the landing "for ferry sounds". That is the place
   not explaining itself, which is the goal. Whether a first-time listener
   should be able to name the change is the sheet author's call.
4. **Unsaid knowledge costs causal links.** Thursday's shortage now shows only
   in what the staff do ("soup without it", "Four left. Keep them back"). The
   three-evening listener heard "a pulla count and 'beans tomorrow'" and did
   not tie it to Friday's delivery, which iteration 4's listener reconstructed.
   Expected, and again a call on how legible the shortage should be.
5. **The landing opening converges.** Friday and Saturday 18:20 open on the
   same clause ("Wind off the water, cold, steady from the open side."), and
   landing cue text rose to 0.38. Shared timestamps stay low (15%). It is a
   bed phrase, so watch it rather than act on it.
6. **Shared sounds across positions are not synchronised.** The landing hears
   Thursday's horn at 18:12:40 and the café at 18:12:50, and the three-evening
   listener noticed. Nothing checks the second-level sync of one sound heard
   from two positions. That is a candidate check.
7. **Unchanged:** radio notices read as told (the Friday notice's "Their
   reason: …"). The café's 19:30–19:40 window still feels crowded to both
   listeners: the bus, arrivals and small events all land in ten minutes.

## Closeout assessment

- Accepted outcome: three iteration-4 findings implemented, re-voiced and
  re-judged, plus one new finding (the oracle asymmetry) fixed and repaired
  (sprint item #2922). Three of four acceptance criteria are met. The
  canon-review criterion is met only after the criteria-driven repair.
- Review findings:
  - first-pass canon issues: 2 lead-in timings and 1 detail beyond the
    announcement;
  - 1 repeat of the lead-in timing;
  - 1 cue-commentary phrase, caught by the listeners and missed by the
    lexicon.
- Repairs: 3 resamples, two of them clean, then 1 criteria-driven repair,
  which was clean.
- Spend (estimate): 19 fills and 19 canon reviews on Opus 5.5, plus 2 blind
  listeners on Sonnet 5.5. Wall time was not measured.
- Unknown: audio. Every check read scripts, and every listener was a model,
  not the writer.
