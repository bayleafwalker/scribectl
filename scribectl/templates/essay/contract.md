---
type: contract
contract_id: <verb-target-nn>
target: "[[ ]]"
mode: <body_fill|review_canon|review_voice|review_beta|refactor>
agent_profile: <prose_drafter|canon_reviewer|voice_reviewer|beta_reader|refactorer>
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
Use only the supplied context pack and the target note. The pack's "Source
material" section is raw ore — draw on it freely, but write its claims as the
author's working notes, never as settled fact. Any claim worth settling goes
in an "Introduced candidates" section — never asserted as ratified.

## Output
- The artifact (draft essay, revision, or review report).
- Introduced candidates (positions / claims worth ratifying from this pass).
- Uncertainties.
