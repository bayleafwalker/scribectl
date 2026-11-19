# First Ice, iteration 4: unsaid knowledge, plain cues, a clock convention

**Question.** [Iteration 3](../2026-11-19-first-ice-iteration-3/README.md)
removed verbatim repetition with already-heard context, and left these
findings:

- the Saturday customers state the closure outright, in three voicings out of
  three;
- the voice canon's own wording turns up as cue commentary ("their own
  business");
- cue wording converges, with clauses shared by 3+ fragments rising from 20
  to 35;
- rituals vanished along with the catchphrases;
- the canon review judges minute-stamped events inconsistently.

Commit `540ab92` acts on all five. Mid-iteration a sixth finding appeared, and
commit `50bffc9` acts on it: voicers gave invented people a canon actor's
name. Do the fixes hold, and what do they cost?

**Verdict: the cue-level and oracle fixes hold. The closure line only shrank.
Saturday is now recognisable but closer to a coda.**

- Cue commentary fell to 0.
- Rituals came back as the only repeats.
- The clock convention made the canon review consistent.
- The new naming rule closed a collision that only the leak oracle had
  caught.
- The closure line is now a tucked-in clause ("with the boat off"), because
  its timeline entry still asks for it.

The three-evening listener reconstructed the whole chain at high confidence
and recognised Saturday through the regulars and their rituals. It found
Saturday "a pleasant coda more than a hook", and Friday's bus scene replayed.
It was right: Saturday 19:40 is built on Friday 19:40's skeleton, a new
failure of already-heard context.
The Saturday-only listener could not clearly name a change.

The kill criterion is not triggered: recognition is clear, but voluntary
curiosity is milder than in iteration 3. The writer is still the taste gate.

## What changed

| Finding | Fix |
| --- | --- |
| Closure stated outright | Voice canon: what everyone present knows stays unsaid or half-said, and shows in what people do about it. (`540ab92`) |
| Canon wording as cue commentary | The canon line no longer offers the phrase. Commentary is named as an anti-pattern: a cue is what the ear receives. (`540ab92`) |
| Converging cue wording | "The bed recurs; its wording does not have to." (`540ab92`) |
| Rituals lost | Greetings, sign-offs and the radio's set phrases are exempt from "do not replay". (`540ab92`) |
| Minute-stamp semantics | Timeline preamble (fixture and template): a heading's clock is when an event begins or is first perceived. The canon review reads the preamble. (`540ab92`) |
| Invented names colliding with canon (found this iteration) | World Seed: people and boats are named only as the pack names them. Oracle: a canon person or vessel named in a script whose pack does not name them is flagged. (`50bffc9`) |

## How it was voiced

As in iteration 3, there were two chains, one per listening position, oldest
first.

- **Landing chain:** 5/5 clean.
- **Café chain, first pass:** 3 of 10 failed canon review (`first-chain/`).
  - Thursday 18:15: "your Leena" with a cast.
  - Thursday 19:15: the car "played up this morning", before the cold begins
    at 17:00.
  - Friday 20:10: crates come in from 20:04, before the delivery's 20:05.

Failed drafts are never heard, so no later café fragment heard Thursday's
café. That would have confounded the continuity and cue-wording comparison.
So the three failed fragments were re-voiced once, along with the three clean
downstream café fragments whose heard sets change (Friday 19:40, Saturday
19:40, Saturday 20:20). The four whose packs cannot change were kept:
Thursday radio, Thursday staff, Friday radio and the customers. All four
rebuild to the same pack sha.

Five of the six came back clean. Friday 20:10 failed again for the same
reason: the van is heard turning in at 20:03:20.

That draft also named a radio dedication "for Leena, from the lads at the
yard". It was the second collision with the canon landing worker, and the
leak oracle caught it where the canon review had not. The naming rule
followed. Friday 20:10 was then re-voiced once against the strengthened
criteria (`repair/`, pack `077004bdc068`): the van arrives at 20:05:00,
nobody is named, and the review is clean.

The Saturday fragments did not hear Friday 20:10, because it was still
flagged when they were voiced. Fourteen fragments predate the naming rule.

## Checks and results

```bash
uv run python docs/experiments/2026-11-19-first-ice-iteration-2/check_cue_sheets.py docs/experiments/2026-11-19-first-ice-iteration-4
uv run python docs/experiments/2026-11-19-first-ice-iteration-3/check_repetition.py docs/experiments/2026-11-19-first-ice-iteration-4
```

| Check | Iteration 2 | Iteration 3 | Iteration 4 |
| --- | --- | --- | --- |
| Packs: leak oracle (with heard text from iteration 3) | 15/15 | 15/15 | 22/22, first chain and repair included |
| Scripts heard: window, order, anchors, leaks, water, road, **names** | 16/16 | 16/16 | 15/15. The superseded Friday draft flags LEAK and NAME Leena, and the first-chain Thursday draft flags NAME. |
| Near-verbatim speech repeats | 6 (3 joke, 3 ritual) | 0 | 11, **all rituals**: "back to the music" and "mind how you go". No conversational line repeats. |
| Cue commentary | 0 | 4 | **0** |
| Cue clauses shared by 3+ fragments | 20 | 35 | 29 |
| Structural echo, café 19:40 Fri vs Sat (shared timestamps / cue text) | 43% / 0.39 | 23% / 0.50 | **65% / 0.56** |
| Canon review, first pass | 14/15 | 14/15 | 12/15 |
| Three-evening listener | high. Saturday recognised through canon traits. | moderate-to-high. Saturday recognised through threads. | **high**, full chain including the supply shortage and delivery. Saturday recognised through the regulars and rituals ("Half it is", "Go steady"). "A pleasant coda more than a hook." |
| Saturday-only listener | medium: ferry off, cause unknown | medium: the two men's "transition"; low-to-medium on anything bigger | **low-to-medium**: ferry off is "the best candidate" |

## What held

- **Commentary is gone,** and the narrator-ish phrases no listener asked for
  went with it.
- **Rituals carry recognition again.** The presenter's "back to the music"
  recurs, and the three-evening listener picked out "Half, thanks / Half it
  is" and "Go steady". Its wording comes straight from the Evening programme
  node ("then it is back to the music"). For a radio sign-off that is the
  point of designed continuity. But canon wording becomes script wherever a
  phrase is quotable, as "their own business" showed.
- **The oracle is consistent now.** Two Friday 20:10 voicings were flagged for
  the same reason under the same rule, and the third, which honours it, passed.
  The convention also made the review stricter. Thursday 19:15's "played up
  this morning" is timeline-true (the cold begins at 17:00), and it is the
  kind of catch that iteration 3's reviewer let through.
- **Names.** Earlier passes had harmless convergences on invented names (two
  "Aino" dedications in the Fri/Sat pass). Here two invented names landed on a
  real actor. The rule fixes that, and the oracle checks it on every script
  regardless of the per-card forbidden lists.

## What did not, and findings for the next iteration

1. **The closure line is shrunk, not gone.** "Bus there and back, with the
   boat off." is half-said, but it is still the line both listeners flag. The
   voicer's own note says why: the pack says the closure "comes up only in
   passing", so it delivers it. That is timeline entry B1.C3.S1950, which
   records a speech beat rather than what the customers know. The timeline is
   append-only, so a voicer-side rule cannot remove it, and a new event cannot
   retract it either.

   The options are the sheet author's call:
   - leave it;
   - or give the timeline an append-only way to supersede an entry (a later
     bullet that names the one it replaces). That fits the ledger model, but
     it is an engine feature, not a fixture edit.
2. **The naming rule costs texture.** The Saturday-only listener wanted to
   hear "the radio dedications again (Marjatta, Sirkka)". Those names
   predate the rule, which will now remove them. Candidate: ratify a small
   pool of dedication names on the Evening programme node. That would give
   safe names that recur by design, with no collisions and no accidental
   "Aino"/"Aili"/"Aune" drift (the three-evening listener caught "Aili" vs
   "Aune").
3. **Saturday is rebuilt on Friday's skeleton. This is the main new
   failure.** The 19:35 bus is canon on both evenings. Saturday 19:40 heard
   Friday 19:40 and reused its frame: the same cue timestamps to the second
   (19:34:50, 19:35:00, 19:35:30, 19:35:45, 19:36:00 … 19:39:50) and the same
   sequence of events. The cue wording is only lightly paraphrased ("The front
   window hums faintly with it" / "buzzes faintly"). Only the speech is new.
   The listener heard "a replay with small variations".

   The speech check and the cue-clause check both missed it, so
   `check_repetition.py` now measures structural echo between fragments that
   share a window on different evenings:

   | Café 19:40, Fri vs Sat | Iter. 2 | Iter. 3 | Iter. 4 |
   | --- | --- | --- | --- |
   | Shared timestamps | 43% | 23% | 65% |
   | Cue-text similarity | 0.39 | 0.50 | 0.56 |

   The canon bus pulls even independent voicers onto the same round seconds,
   hence iteration 2's 43%. The landing pairs show no echo (0.05–0.25).
   Already-heard context is what makes a voicer template on the previous
   evening. The voice canon asks habits to recur in new words, but it says
   nothing about recurring events or about a fragment's shape. It should, if
   Saturday is to be more than a coda. Alternatively the pack could ship
   earlier fragments from *other* windows only.
4. **First-time inference keeps falling** as explanation is removed: medium,
   then low-to-medium, then low-to-medium. A place that doesn't explain itself
   is the goal, so this is expected. It does mean the Saturday landing is now
   carrying the evidence almost alone, with two walkers and slush.
5. **Shared cue wording is down but not back to baseline** (29 against 20).
   Already-heard context still homogenises how the bed is described.
6. **Unchanged:** radio notices read as told, and short windows feel cut in.

## Closeout assessment

- Accepted outcome: five iteration-3 findings and one new finding
  implemented, re-voiced and re-judged (sprint item #2921).
- Review findings: 3 canon issues in the first café pass (a name collision, a
  pre-onset cold reference, an early delivery), 1 repeat of the delivery
  issue, and 1 name collision caught only by the leak oracle.
- Repairs: 6 chain re-voices (resamples, so heard sets stay coherent), then 1
  criteria-driven repair after the naming rule, which was clean.
- Spend (estimate): 22 fills and 22 canon reviews on Opus 5.5, plus 2 blind
  listeners on Sonnet 5.5. Wall time was not measured.
- Unknown: audio. Every check read scripts, and every listener was a model,
  not the writer.
