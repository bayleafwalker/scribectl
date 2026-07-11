---
type: output_card
kind: <scene|spoken_fic|blog_post|research_note|generated>
mode: <body_fill|audio_script|blog_draft|research_digest|auto_generate>
distribution: <personal|publication>
# Sequenced kinds (scenes, fic episodes) carry a position and see only
# timeline events before it. Unsequenced kinds (blog_post, research_note,
# generated) DELETE these three lines and see the whole timeline.
book: 0
chapter: 0
scene: 0
pov: "[[ ]]"          # optional for non-narrative kinds
location: "[[ ]]"     # optional for non-narrative kinds
characters:
  - "[[ ]]"
canon_scope:
  - "[[ ]]"
mechanics_scope:      # the mechanic nodes this output must stay true to
  - "[[ ]]"
base: "[[ ]]"         # auto_generate only: the node the output grows from
target_words: 1000    # or target_minutes for spoken kinds
---

# <title>

## Brief
<What this output is, for whom, and where it lands (session prep, feed, blog,
audio). One paragraph.>

## Required beats
- <beat — for narrative kinds, story beats; for posts/notes, points that must land>
- <beat>

## Exit state
<What must be true, or understood by the audience, when this output ends.
review_canon checks narrative exit states against the timeline.>

## Tone target
<One line. The voice canon carries the register; this carries the mood.>

## Do not
- <hard exclusion — ships into the pack verbatim>
