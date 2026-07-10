---
type: contract
contract_id: <verb-target-nn>
target: "[[ ]]"
mode: <body_fill|fill_lore|review_canon|review_voice|review_beta|refactor>
agent_profile: <prose_drafter|lore_filler|canon_reviewer|voice_reviewer|beta_reader|refactorer>
context_strategy: canon_slice
output_target: "/body/drafts/<...>.md"
review_after:        # reports FIRE automatically; CONSUMPTION stays manual
  - canon_check
  - voice_check
---

# Contract

## Task
<What the agent does. One paragraph.>

## Scope
Use only the supplied context pack and the target note. Invent minor sensory
texture freely. Any new proper noun or world fact goes in an
"Introduced candidates" section — never asserted as settled.

## Output
- The artifact (draft prose, lore expansion, or review report).
- Introduced candidates (proper nouns / facts invented this pass).
- Uncertainties.
