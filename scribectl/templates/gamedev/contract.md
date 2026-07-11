---
type: contract
contract_id: <verb-target-nn>
target: "[[ ]]"
mode: <body_fill|audio_script|blog_draft|research_digest|auto_generate|review_canon|review_voice|review_mechanics|review_beta|refactor>
agent_profile: <prose_drafter|audio_drafter|post_drafter|researcher|canon_reviewer|voice_reviewer|mechanics_reviewer|beta_reader|refactorer>
context_strategy: canon_slice
output_target: "/body/drafts/<...>.md"
review_after:        # reports FIRE automatically; CONSUMPTION stays manual
  - canon_check
  - voice_check
  - mechanics_check
---

# Contract

## Task
<What the agent does. One paragraph. For auto_generate: grow the output from
the card's `base` node's ratified facts — the pack is the whole input, the
card's beats are the whole brief; publication-bound outputs still cross the
human taste gate before they ship anywhere.>

## Scope
Use only the supplied context pack and the target note. Invent minor sensory
texture freely. Any new proper noun, world fact, or implied game ruling goes
in an "Introduced candidates" section — never asserted as settled.

## Output
- The artifact (draft prose, audio script, post, digest, or review report).
- Introduced candidates (proper nouns / facts / implied rulings this pass).
- Uncertainties.
