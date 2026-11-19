# First Ice, Friday and Saturday: the kill criterion

**Question.** The event sheet's kill criterion: *if the third evening
produces neither recognition nor voluntary curiosity, the additional world
machinery has not yet earned its place.* Thursday already passed the
first-proof gate ([record](../2026-11-19-first-ice-thursday/README.md)). Do
Friday and Saturday hold up?

**Verdict: not killed, with a mild pull.** One listener heard all three
evenings and found Saturday recognisably the same place. What it noticed on
its own was the empty landing, and that turned its attention back toward the
landing and Thursday's arrival, which is the turn the sheet asked for. In its
words, "a mild pull, not a strong one … calm but not flat". A second
listener heard Saturday only, never Thursday. It inferred from ordinary
traces that the ferry is off because of ice, at medium-high confidence, and
would tune in again.

The machinery has earned a next step, not a victory. Two caveats below weaken
the result. The writer is still the taste gate.

## Setup

Same pipeline as Thursday: `listening` set, scoped packs, `scribe-dispatch
run --runner claude --model claude-opus-5-5`, and a `review_canon` on each
landed draft. There are eight new cards. Friday: the landing at the old
crossing time; the radio, which now has the official explanation; the café
as the replacement bus comes in; the café as the delayed delivery arrives by
road. Saturday: the landing at the old crossing time; the café as the bus
comes in; customers at a table; the café closing. The Saturday customers hold
only what is said at their own table, so they are a source that never heard
Thursday.

Before voicing, the pack oracle caught one more timeline leak. Friday's and
Saturday's 18:12 bullets were `heard: Café` but also carried landing-only
detail ("Ice at the ramp", "slush remains"). Both were split like Thursday's
arrival: the café hears the missing engine and horn, and the landing keeps
the ice.

## Checks and results

| Check | Result |
| --- | --- |
| Pack scoping vs knowledge table, all 15 cards | 15/15 exact |
| No pack sees a later event (generic check) | 15/15 |
| Leak oracle over packs | 15/15 clean |
| Leak oracle over the 8 new scripts | 8/8 clean |
| Sounds from the water in Fri/Sat scripts | none |
| Length vs card target | all within 3 s (47–90 s) |
| Canon review | 8/8 clean |
| Blind listener, three evenings | high: ferry stopped, bus replaced it; Saturday recognised; mild pull to the landing |
| Blind listener, Saturday only | medium-high: ferry off because of ice; would tune in again |

## What carried it

- **The landing remembers.** At Saturday 18:10 a paper edge on the notice
  board ticks against its tape twice, and slush packs and loosens at the
  ramp. One walker crosses the planks and goes. Nothing is read aloud.
- **The change becomes routine without anyone explaining it.** "Road all
  right?" / "Long way round. It's fine." (Friday's delivery). "Same as last
  night." (a Saturday bus passenger). "Every bend on that road, I swear."
  (Friday).
- **The café closes like any night.** Chairs up, radio off, the fridge hum,
  a key turned and tried.

## Caveats

1. **Some recognition was accidental.** Two independent voicers both invented
   a radio dedication to "Aino" (Friday 19:30, Saturday 19:30). The
   three-evening listener named it as something it recognised. Earlier,
   "end of the month" turned up in two Thursday fragments. Recognition across
   evenings is currently partly model convergence, not designed continuity.
2. **Saturday's inference for a new listener leaned on the one tidy line.**
   Both listeners flagged "with the ferry off it's the long way round anyway"
   as handed to them, and it is the Saturday-only listener's clearest
   evidence. The card allowed the closure to "come up once, in passing", and
   it did, but phrased as an explanation.

## Explaining moments, for the taste gate

- Friday radio: "The Tavi's closed. There's early ice at the landing …" is
  the official explanation, which the sheet permits the presenter on Friday.
  The gloss after it, "So that's the bus, not the boat, for now.", is extra
  and reads as being for the listener.
- Thursday radio's repeated notice (flagged again).
- Saturday customers' "with the ferry off …" (both listeners), and milder
  ones: "It was on time today", "I wrote it down somewhere".

## Findings for the next iteration

- **The narrowed water rule held, then over-reached on the road.** The café
  fragments got their road traffic back, and nothing came off the water
  anywhere. But both landing fragments added a car on the road, which the
  landing's audible list does not include, and both voicers flagged it
  themselves. The World Seed now says road traffic is free *where the
  listening position can hear the road*. **That qualification has not been
  re-voiced.**
- **Standing conditions are not represented.** The timeline records the cold
  spell's onset on Thursday at 17:00 and nothing after it, so Friday's and
  Saturday's café voicers were unsure the cold had lasted and left cold cues
  out. Events say what changed, not what persists. Candidate fix: a
  standing-conditions bullet at the start of each evening, or a state section
  on the weather node.
- **Continuity needs a designed home.** Recurring texture (the radio's
  dedications and notices, regulars, the presenter's voice) should be canon a
  listener can learn to recognise, perhaps a "regulars" node and the radio
  programme's recurring segments, so recognition stops depending on the model
  repeating itself.
- **The bulletin timing is noticed.** For the second time a listener pointed
  out that the 19:20 bulletin cancels a crossing that already didn't happen
  at 19:12. It is realistic, but the sheet's author should decide whether it
  is wanted.
- **Time compression still applies.** Fifteen fragments of about a minute
  each stand for three evenings. The curiosity measured here is curiosity
  about a montage.

## Closeout assessment

- Accepted outcome: Friday and Saturday voiced; kill criterion tested and
  passed weakly (sprint item #2918).
- Review findings: 0 canon issues in 8 drafts; 1 timeline leak caught by the
  oracle before voicing; 1 rule over-reach found in the scripts.
- Repairs: timeline split (pre-voicing), road-traffic qualification
  (post-voicing, unverified).
- Spend (estimate): 8 fills + 8 canon reviews on Opus 5.5, 2 blind listeners
  on Sonnet 5.5.
- Unknown: audio. Every check here read scripts, and every listener was a
  model, not the writer.
