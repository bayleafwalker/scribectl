---
type: mechanic_node
domain: core-loop
importance: core
ties_to:
  - "[[Väki]]"
  - "[[Syntysanat]]"
  - "[[Runolaulu]]"
---

# Freeform Casting Evaluation

## One-line function
Parse what the player actually performed — meter, known anchors, rests — and
have the world respond to the literal utterance, not the intent.

## Ratified facts
- Casting is utterance evaluation, not chart evaluation: the game parses the
  performed song and the väki respond to exactly that.
- Evaluation is constrained improvisation on a three-layer grammar: (1) does
  the line scan in the meter, (2) which known syntysanat fragments and
  väki-names anchor it, (3) everything between anchors is free and judged
  rhythmically, not semantically.
- Notes quantize to the 5/4 world pulse with judgment windows; there is no
  unquantized tempo inference.
- Falling silent and re-entering on a phrase boundary decays the effect
  toward uncast but gives no offense; breaking meter mid-phrase, or forcing
  wrong syllables to hold the beat, is what curdles a cast.
- Guidance UI is the character's memory of the verse made visible:
  fragmentary knowledge renders as fragmentary notation, and full mastery
  fades the lane entirely.

## Tuning knobs
- Judgment window widths per difficulty; decay rate of an abandoned cast;
  how many kerto repeats before the väki's attention wanders.

## Open questions
- Does the parser detect composite-pattern play vs. true limb independence
  and score them differently?

## Design utility
One rule — the väki respond to what you actually sang — generates every
failure mode without a punishment system, and makes listening a mechanic:
what enemies sing is parseable by the same grammar.
