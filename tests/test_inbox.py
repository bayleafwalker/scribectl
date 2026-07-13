"""Verdict inbox: parsing, the pure sweep transforms, and candidate mining.

The contract under test: checkbox marks map to verdicts, provenance rides
along verbatim, malformed candidates surface as problems instead of vanishing,
the node/inbox rewrites touch nothing beyond their sanctioned span, and mined
candidates land pending with a via-link that makes mining idempotent.
"""
from pathlib import Path

import pytest

from scribectl.core.inbox import (append_bullets, mine, mine_proposal, mine_report,
                                  parse_inbox, receipt, remove_candidates)
from scribectl.core.vault import Note, Vault

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


# -- candidate mining (docs/RATIFICATION.md, build item 2) --------------------

REPORT_BODY = """\
# canon review — Scene 01-01

## Findings
- none

## Introduced candidates seen in draft
- "The ash-census is conducted quarterly" — appears in neither timeline nor pack
- "Curfew keys are cut in pairs" → [[Mara Vey]] — implied by the clerk scene
- "<new fact, worded as a checkable claim>" → [[<the canon node it belongs in>]]
- none
"""


def _report(name="ch01-sc01-draft-a — canon review", body=REPORT_BODY, **meta):
    m = {"type": "review_report", "kind": "canon",
         "draft": "[[ch01-sc01-draft-a]]", "pack_sha": "d21f2dd064bd", **meta}
    return Note(path=Path(f"reviews/canon/{name}.md"), meta=m, body=body)


PROV = ("(from [[ch01-sc01-draft-a]], pack d21f2dd064bd, "
        "via [[ch01-sc01-draft-a — canon review]])")


def test_mine_report_lifts_candidates_pending():
    blocks = mine_report(_report())
    # `- none` and the template placeholder never become candidates.
    assert blocks == [
        f'- [ ] "The ash-census is conducted quarterly"\n      {PROV}',
        f'- [ ] "Curfew keys are cut in pairs" → [[Mara Vey]]\n      {PROV}',
    ]
    # The routed block round-trips through the inbox grammar; the unrouted one
    # surfaces as a problem every sweep until the writer routes it.
    cands, problems = parse_inbox("\n".join(blocks) + "\n")
    assert [c.verdict for c in cands] == ["pending"]
    assert cands[0].fact == "Curfew keys are cut in pairs"
    assert cands[0].target == "Mara Vey"
    assert cands[0].provenance == PROV
    assert len(problems) == 1 and "no `→ [[target]]`" in problems[0][1]


def test_mine_report_without_candidates_section():
    voice = _report(body="## Findings\n- none\n\n## Strongest passage\n- x\n")
    assert mine_report(voice) == []
    sparse = _report(body="## Introduced candidates seen in draft\n- none\n")
    assert mine_report(sparse) == []


def test_mine_report_provenance_omits_what_is_missing():
    bare = _report(body='## Introduced candidates seen in draft\n- "A fact"\n')
    bare.meta.pop("draft"), bare.meta.update(pack_sha="none")
    assert mine_report(bare) == [
        '- [ ] "A fact"\n      (via [[ch01-sc01-draft-a — canon review]])']


def test_mine_skips_reports_already_linked():
    vault = Vault(root=Path("."), notes={"r": _report()})
    blocks, names = mine(vault, "", "")
    assert names == ["ch01-sc01-draft-a — canon review"] and len(blocks) == 2
    # Wikilinked from the inbox (still queued) or the ledger (swept): skipped.
    inboxed = "- [ ] \"x\"\n      via [[ch01-sc01-draft-a — canon review]]\n"
    assert mine(vault, inboxed, "") == ([], [])
    ledgered = '### Accepted\n- "x" → [[Y]] (via [[ch01-sc01-draft-a — canon review]])\n'
    assert mine(vault, "", ledgered) == ([], [])


# -- fact-proposal mining (docs/RATIFICATION.md, build item 3) ----------------

PROPOSAL_BODY = """\
# Fact proposal — Ilmi ← Design Seed

## Candidate facts
- "Ilmi learned the beat digging ditches to work songs"
      quote: "learns the beat digging ditches to work songs"
      confidence: high
      conflicts: none
- "Cast feedback is diegetic music, never a UI popup" → [[Freeform Casting Evaluation]]
      confidence: high
- "<candidate fact — a checkable claim>"
      quote: "<the supporting span>"
- none
"""


def _proposal(name="Ilmi — Design Seed — 2026-07-12", body=PROPOSAL_BODY, **meta):
    m = {"type": "fact_proposal", "target": "[[Ilmi]]", "source": "[[Design Seed]]",
         "mining_pack_sha": "abaeea6dc3ac", **meta}
    return Note(path=Path(f"control/proposals/{name}.md"), meta=m, body=body)


PPROV = ("(from [[Design Seed]], mining pack abaeea6dc3ac, "
         "via [[Ilmi — Design Seed — 2026-07-12]])")


def test_mine_proposal_routes_to_target_and_honors_overrides():
    blocks = mine_proposal(_proposal())
    # `- none` and the template placeholder never become candidates; the
    # indented quote/confidence/conflicts lines stay in the proposal.
    assert blocks == [
        f'- [ ] "Ilmi learned the beat digging ditches to work songs" → [[Ilmi]]\n      {PPROV}',
        f'- [ ] "Cast feedback is diegetic music, never a UI popup" → [[Freeform Casting Evaluation]]\n      {PPROV}',
    ]
    # Round-trips through the inbox grammar as pending, provenance intact.
    cands, problems = parse_inbox("\n".join(blocks) + "\n")
    assert [c.verdict for c in cands] == ["pending", "pending"]
    assert cands[0].target == "Ilmi"          # defaulted to the proposal's target
    assert cands[1].target == "Freeform Casting Evaluation"  # explicit override kept
    assert cands[0].provenance == PPROV and problems == []


def test_mine_proposal_without_candidates_or_provenance():
    assert mine_proposal(_proposal(body="## Notes\n- nothing here\n")) == []
    # Missing sha and source drop out of provenance, leaving just the via-link.
    bare = _proposal(body='## Candidate facts\n- "A fact"\n')
    bare.meta.pop("source"), bare.meta.update(mining_pack_sha="none")
    assert mine_proposal(bare) == [
        '- [ ] "A fact" → [[Ilmi]]\n      (via [[Ilmi — Design Seed — 2026-07-12]])']


def test_mine_covers_reports_and_proposals_and_stays_idempotent():
    vault = Vault(root=Path("."), notes={"r": _report(), "p": _proposal()})
    blocks, names = mine(vault, "", "")
    assert set(names) == {"ch01-sc01-draft-a — canon review",
                          "Ilmi — Design Seed — 2026-07-12"}
    assert len(blocks) == 4  # 2 from the report, 2 from the proposal
    # A proposal wikilinked from the ledger (swept) is skipped, same as a report.
    ledgered = '### Accepted\n- "x" → [[Ilmi]] (via [[Ilmi — Design Seed — 2026-07-12]])\n'
    _, names2 = mine(vault, "", ledgered)
    assert names2 == ["ch01-sc01-draft-a — canon review"]


def test_mine_skips_reconciled_siblings():
    """A proposal folded into a merge (named in its `reconciles:`) never
    reaches the inbox itself — its candidates ride the merge proposal
    (docs/RATIFICATION.md, build item 4)."""
    merge = _proposal(name="Ilmi — reconciliation — 2026-07-13",
                      body='## Candidate facts\n- "The merged fact"\n',
                      reconciles=["[[Ilmi — Design Seed — 2026-07-12]]"])
    vault = Vault(root=Path("."), notes={"p": _proposal(), "m": merge})
    blocks, names = mine(vault, "", "")
    assert names == ["Ilmi — reconciliation — 2026-07-13"]
    assert len(blocks) == 1 and '"The merged fact"' in blocks[0]
