import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _packet(name: str) -> dict:
    return json.loads((ROOT / "verification/contexts" / name).read_text(encoding="utf-8"))


def test_concurrent_landing_context_targets_exclusive_create():
    packet = _packet("concurrent-artifact-landing.json")

    assert packet["depth"] == 2
    assert packet["consistency"]["object"] == "exclusive-artifact-creation"
    assert "simultaneous-create" in packet["faults"]


def test_ratification_context_preserves_human_verdict_boundary():
    packet = _packet("ratification-sweep-recovery.json")

    assert "only-accepted-checkbox-promotes-fact" in packet["invariants"]
    assert "concurrent-sweep-same-candidate" in packet["faults"]


def test_protocol_document_records_current_landing_race_without_weakening_trust_rules():
    protocol = (ROOT / "docs/STATE_PROTOCOLS.md").read_text(encoding="utf-8")

    assert "check-then-write race" in protocol
    assert "writer's checkbox is the only verdict" in protocol
    assert "No automated path may infer acceptance" in protocol
