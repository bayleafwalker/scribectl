"""Verdict inbox: parsing and the pure sweep transforms.

The contract under test: checkbox marks map to verdicts, provenance rides
along verbatim, malformed candidates surface as problems instead of vanishing,
and the node/inbox rewrites touch nothing beyond their sanctioned span.
"""
import pytest

from scribectl.core.inbox import append_bullets, parse_inbox, receipt, remove_candidates

INBOX = """\
---
type: ratification_inbox
---

# Ratification Inbox

Grammar example, invisible to the sweep:

```
- [x] "fenced example" → [[Nowhere]]
```

- [x] "the splice — trench term for rejoining the cadence" → [[Crusade]]
      (from [[What Aune Brings Back — draft 1]], pack 01318d2d1470)
- [-] "a royal bloodline rules the rim" → [[The Volcanic City-State]]
- [>] "gate-warden guild" -> [[Mara Vey]]
      (from [[Scene 01-01 — draft 1]], pack aaaabbbbcccc)
- [ ] "Bay Nine ≈ forty throats" → [[Crusade]]
- [x] no target link at all
"""


def test_parse_marks_targets_provenance():
    cands, problems = parse_inbox(INBOX)
    assert [c.verdict for c in cands] == ["accept", "reject", "defer", "pending"]
    assert cands[0].fact == "the splice — trench term for rejoining the cadence"
    assert cands[0].target == "Crusade"
    assert cands[0].provenance == "(from [[What Aune Brings Back — draft 1]], pack 01318d2d1470)"
    assert cands[1].provenance == ""
    # ASCII arrow accepted; provenance may follow either arrow form.
    assert cands[2].target == "Mara Vey"
    # The fenced example never becomes a candidate.
    assert all(c.target != "Nowhere" for c in cands)
    # A ticked line with no target is a problem, never a silent drop.
    assert len(problems) == 1 and "no `→ [[target]]`" in problems[0][1]


def test_parse_unquoted_fact_and_blank_target():
    cands, problems = parse_inbox("- [x] plain wording → [[Node]]\n- [x] \"x\" → [[ ]]\n")
    assert cands[0].fact == "plain wording"
    assert len(problems) == 1  # [[ ]] placeholders are not links


def test_receipt_carries_route_and_provenance():
    cands, _ = parse_inbox(INBOX)
    assert receipt(cands[0]) == ('"the splice — trench term for rejoining the cadence" '
                                 "→ promoted to [[Crusade]] "
                                 "(from [[What Aune Brings Back — draft 1]], pack 01318d2d1470)")
    assert receipt(cands[1]) == '"a royal bloodline rules the rim" → [[The Volcanic City-State]]'


NODE = """\
---
type: canon_node
---

# The Mist

## One-line function
Pressure from outside.

## Ratified facts
- The Mist is not weather.

## Open questions
- What does it want?
"""


def test_append_bullets_touches_only_the_section():
    out = append_bullets(NODE, "Ratified facts", ["It hums at dawn."])
    assert "- The Mist is not weather.\n- It hums at dawn.\n\n## Open questions" in out
    # Every byte outside the section survives, frontmatter included.
    head, _, _ = NODE.partition("## Ratified facts")
    assert out.startswith(head)
    assert out.endswith("## Open questions\n- What does it want?\n")


def test_append_bullets_retires_stub_placeholder():
    stub = NODE.replace("- The Mist is not weather.",
                        "_(none ratified yet — node is a stub)_")
    out = append_bullets(stub, "Ratified facts", ["First fact."])
    assert "_(none" not in out
    assert "## Ratified facts\n- First fact.\n\n## Open questions" in out


def test_append_bullets_section_at_eof_and_missing():
    tail = "# N\n\n## Ratified facts\n- Old.\n"
    assert append_bullets(tail, "Ratified facts", ["New."]).endswith("- Old.\n- New.\n")
    with pytest.raises(ValueError, match="Ratified facts"):
        append_bullets("# N\n\n## Other\n", "Ratified facts", ["x"])


def test_remove_candidates_preserves_the_rest():
    cands, _ = parse_inbox(INBOX)
    swept = [c for c in cands if c.verdict != "pending"]
    out = remove_candidates(INBOX, swept)
    remaining, problems = parse_inbox(out)
    assert [c.fact for c in remaining] == ["Bay Nine ≈ forty throats"]
    assert len(problems) == 1  # the malformed line is not ours to delete
    assert "# Ratification Inbox" in out and "fenced example" in out
