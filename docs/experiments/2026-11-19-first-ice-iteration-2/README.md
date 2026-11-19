# First Ice, iteration 2: real time, standing conditions, designed continuity

**Question.** The [Fri/Sat record](../2026-11-19-first-ice-fri-sat/README.md)
passed the kill criterion weakly and left five findings:

- standing conditions were missing;
- recognition across evenings was accidental;
- the bulletin timing was noticed;
- every fragment compressed ten minutes into one;
- the road-traffic wording had not been re-voiced.

All five were fixed in the fixture (commit `eb2f4b7`), and all fifteen
fragments were re-voiced. Does it still sound like a place, and does
recognition now come from canon?

**Verdict: yes on both, with one new failure.** Both blind listeners said
"mostly overhearing" and "mostly time passing". The three-evening listener
recognised Saturday through things that are now canon: the corner-table
regulars, the woman's half cup, the accordion and guitar programme, and the
closing routine. It said "Nothing felt inert". The Saturday-only listener
would tune in again. It inferred the ferry is off, but it could no longer
say why. That matches what the Saturday sources know.

The new failure is that designed continuity hardened into a catchphrase:
the regulars' roof joke recurs nearly word for word.

The kill criterion stays untriggered. The writer is still the taste gate.

## What changed in the fixture

| Finding | Fix (in `eb2f4b7`) |
| --- | --- |
| Standing conditions | Appended "the cold holds" events at Fri and Sat 17:00. They are `heard:` by the landing, the café and its customers. Events record change, so persistence is now recorded as an event too. |
| Designed continuity | New `Café regulars` and `Evening programme` nodes. The presenter's voice, two evening staff and the radio shelf were added to existing nodes. All of it was promoted from texture that Thursday invented and listeners recognised. |
| Bulletin timing | The sheet's 19:20 is kept, because absence at 19:12 comes before the news. The radio card lets the presenter say the notice has only just come in. |
| Time compression | A fragment is now a clock-stamped cue sheet over its real window `[window_from, clock)`, with events at their recorded times. Four windows were trimmed to end at the pack cut-off. |
| Road traffic | The World Seed rule ("where the listening position can hear the road") is unchanged. This pass is its first re-voice. |

## Checks and results

`check_cue_sheets.py` re-runs every script check below from this record:

```bash
.venv/bin/python docs/experiments/2026-11-19-first-ice-iteration-2/check_cue_sheets.py
```

| Check | Result |
| --- | --- |
| Pack scoping vs knowledge table, no later events (`tests/test_listening.py`) | 15/15 |
| Leak oracle over the 15 scripts and the repair | 16/16 clean |
| Every cue inside its window, in order | 16/16 |
| Anchors at recorded times (horn 18:12, slush 18:37, ramp 18:43, bulletin 19:20, bus 19:35, crates, lock) | 8/8 |
| Sound cues from the water outside the 18:12 approach | none |
| Road traffic at the landing | none in 5/5 landing fragments. Café fragments keep it. **Road rule verified.** |
| Cold audible on Fri/Sat | 6/8. Absent in Fri radio (5 min) and Sat 19:30 café. Last pass the café voicers left it out. |
| Regulars or programme audible | every café fragment |
| Cue spacing | 18–58 s, with the landing the sparsest |
| Canon review | 14/15 clean. 1 issue, repaired (below). |
| Blind listener, three evenings | high on the change. Saturday recognised through canon. Mild pull, "nothing felt inert". Mostly real time. |
| Blind listener, Saturday only | medium: ferry off, cause unknown. Would tune in again. Mostly real time. |

## Repair: Saturday 19:55

The canon review flagged `"You'll want to look at the timetable, then. Not go
by what it was."`: it implies the customers knew of a timetable revision. The
only revision in the timeline is the operator's notice at the landing, and it
never reaches them. The voicer had already listed the line as an introduced
candidate, and the card already forbade it ("They know only what they have
seen, read or been told"). So no criterion was missing. The oracle caught it
as designed. The fragment was re-voiced once with the same pack
(`341a3a8e8213`) in a fresh copy of the fixture, and the review is clean
(`repair/`). The original draft and review are kept in `drafts/` and
`reviews/`. This was a resample, not a criteria change. Listeners heard
draft-b.

The re-voice also replaced the line both earlier listeners had flagged ("with
the ferry off it's the long way round anyway"). The closure now comes up as the
older man's own worry: "Not with the ferry off, it'll be full of everybody."
The Saturday-only listener still marked it as slightly for them, and
inference from Saturday dropped from medium-high to medium. Nothing on
Saturday now gives the cause in words. That is correct scoping, not a loss:
the customers were never told why. A listener who wants the reason has to go
to the landing.

## What carried it

- **Recognition is canon now.** Every café fragment carries the regulars or
  the programme, and most carry both. The recurring pieces are the corner
  table, the woman's "just half" and "Mind how you go", and the record
  rotation with its dedications. The accidental "Aino" is gone, and no
  listener needed it.
- **Real time reads as time.** Both listeners heard the windows run at their
  own speed. Each picked out the gaps at the landing and the café's closing
  routine (chairs up, radio clicked off, the dishwasher) as the best of it.
- **The bulletin is no longer an inconsistency.** It was flagged twice before.
  This time the three-evening listener placed the 19:20 notice in sequence
  without remark.
- **The causal chain is still inferred, not told.** For Thursday the
  three-evening listener reconstructed the ramp, the cancellation, the kitchen
  "working round it" and the delivery coming the long road. Its evidence was
  "No." under Leena's breath and "Long, but all right".

## New findings for the next iteration

1. **A trait becomes a catchphrase.** The regulars node names a trait (he
   puts jobs off, the younger one needles him) and contains no dialogue. Two
   independent voicers still turned it into the same lines: Thursday 18:05
   and Saturday 19:30 both have "It's not weather for a roof." / "It wasn't
   [weather] in August either." The joke also appears in all three Saturday
   café fragments. The three-evening listener counted it as recognition,
   "almost word for word". The Saturday-only listener heard "the same joke
   comes back three times" as designed. Designed continuity fixed *what*
   recurs, but independent voicing cannot vary *how* it recurs.
2. **Same cause, smaller symptom: dangling hooks.** Thursday's "she wants the
   curtains back Saturday" never returns on Saturday. A voicer can plant a hook
   but cannot pick one up.

   For both: the Thursday record's option is now the leading candidate. Ship
   the previous fragment at the same position as already-heard context, so a
   voicer knows what the room has said and can vary it or pick it up. It would
   be ambient, not canon, and it should not enter the knowledge scope.
3. **Short windows feel cut in.** The 2-minute radio window (19:20–19:22)
   reads as an insert. Saturday 19:30–19:40 holds the bus, the passengers and a
   dedication, and one listener found it slightly busy. The events are canon.
   Window length is a fixture choice, and the renderer's continuous bed between
   fragments decides the rest.
4. **Radio notices still read as told.** Both notices were flagged: Friday's
   official reason, which the sheet permits, and Thursday's "That's as it
   came." This is taste, unchanged from before.
5. **Cosmetic:** speaker labels drift between YOUNGER MAN/OLDER MAN and
   FRIEND for the same pair. A label convention on the regulars node would fix
   it. Not urgent.

## Closeout assessment

- Accepted outcome: all five Fri/Sat findings implemented, re-voiced and
  re-judged (sprint item #2919).
- Review findings: 1 canon issue in 15 drafts, caught by the oracle and
  flagged by the voicer itself. 0 leaks. 0 rule over-reaches. The road rule is
  verified.
- Repairs: 1 re-voice (a resample, clean). No criteria changed after voicing.
- Spend (estimate): 16 fills and 16 canon reviews on Opus 5.5, plus 2 blind
  listeners on Sonnet 5.5. Voicing ran as three parallel batches. Wall time
  was not measured.
- Unknown: audio. Every check here read scripts, and every listener was a
  model, not the writer.
