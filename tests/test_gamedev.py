"""The gamedev template set: second project, second shape (PLAN Phase E).

What must hold: two fact-bearing node types (lore + mechanics) derive status
through the same machinery, the kind-parameterized output card packs the same
minimal slice, unpositioned cards see the whole timeline, and `init --set
gamedev` instantiates the manifest's layout — all without moving a byte of
fiction output (the fiction golden test is the other half of this file).
"""
import re
from pathlib import Path

import pytest

from scribectl.cli import main
from scribectl.core.contextpack import build_pack
from scribectl.core.vault import Vault
from scribectl.templateset import list_sets, load_set

BASELINE_STATUS = """\
type          name                        status
--------------------------------------------------
canon_node    Ilmi                        seeded
canon_node    Runolaulu                   seeded
canon_node    Syntysanat                  ratified
canon_node    The Ditch Meadow            stub
canon_node    Väki                        seeded
mechanic_node Freeform Casting Evaluation ratified
mechanic_node Polymetric Difficulty       seeded
output_card   Episode 1-01                ready_for_fill
output_card   Why Our World Beats in Five blocked_unresolved_scope  (missing: [[Latency Anchoring]])
"""


@pytest.fixture
def run(monkeypatch, capsys):
    def _run(*argv, vault=None):
        if vault is not None:
            monkeypatch.setenv("SCRIBECTL_VAULT", str(vault))
        code = main(list(argv))
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run


@pytest.fixture
def rs_vault(runosong_root):
    return Vault.load(runosong_root)


# -- the set itself -----------------------------------------------------------

def test_all_sets_discoverable():
    assert list_sets() == ["essay", "fiction", "gamedev"]
    gd = load_set("gamedev")
    assert gd.card_type == "output_card"
    assert gd.node_types == ("canon_node", "mechanic_node")


def test_load_unknown_set_names_available():
    with pytest.raises(ValueError, match="essay, fiction, gamedev"):
        load_set("zine")


# -- derived state ------------------------------------------------------------

def test_gamedev_baseline_status(run, runosong_root):
    """Mechanic nodes ratify through the same ledger; unicode links (Väki)
    resolve; the unpositioned blog card blocks on its missing mechanics link."""
    code, out, _ = run("status", "-p", "Runosong", vault=runosong_root.parent)
    assert code == 0
    assert out == BASELINE_STATUS


def test_output_card_draft_review_chain(run, scratch_runosong):
    proj = scratch_runosong / "Works" / "Runosong"
    (proj / "body/drafts/Episode 1-01 draft v1.md").write_text(
        '---\ntype: draft\ncard: "[[Episode 1-01]]"\n---\n\nSpoken prose here.\n',
        encoding="utf-8",
    )
    _, out, _ = run("status", vault=scratch_runosong)
    assert "Episode 1-01                has_draft" in out

    (proj / "reviews/mechanics/Episode 1-01 mechanics review.md").write_text(
        '---\ntype: review_report\nkind: mechanics\ntarget: "[[Episode 1-01]]"\n'
        "verdict: clean\n---\n\n# mechanics review\n",
        encoding="utf-8",
    )
    _, out, _ = run("status", vault=scratch_runosong)
    assert "Episode 1-01                reviewed" in out


# -- the pack -----------------------------------------------------------------

def test_pack_ships_mechanics_beside_lore(rs_vault, gamedev):
    md = build_pack(rs_vault, "Episode 1-01", gamedev).markdown
    assert "## Output card" in md
    # Lore and mechanic nodes brief identically: rulings are facts.
    assert "Väki respond to what was actually sung" in md
    assert "utterance evaluation, not chart evaluation" in md
    # Scaffolding never ships, for either node type.
    assert "Tuning knobs" not in md and "Judgment window widths" not in md
    assert "Story utility" not in md and "Design utility" not in md
    # Out-of-scope events stay out (minimal slice, unchanged).
    assert "Louhi" not in md


def test_positioned_card_gates_timeline(rs_vault, gamedev):
    """Episode 1.1.1 must not see the B1.C1.S1 event (strictly-before rule)."""
    md = build_pack(rs_vault, "Episode 1-01", gamedev).markdown
    assert "charred page of tulen synty" in md          # pre event ships
    assert "answers a work song" not in md              # its own moment does not


def test_unpositioned_card_sees_whole_timeline(rs_vault, gamedev):
    """A blog post carries no position: everything recorded is prior."""
    md = build_pack(rs_vault, "Why Our World Beats in Five", gamedev).markdown
    assert "answers a work song" in md
    assert "[[Latency Anchoring]] — referenced but no note exists" in md
    # auto_generate base node's rulings are in the pack the agent grows from.
    assert "polymetric against it" in md


def test_pack_warns_on_unreceipted_mechanics(rs_vault, gamedev):
    warnings = build_pack(rs_vault, "Why Our World Beats in Five", gamedev).warnings
    assert any("Polymetric Difficulty" in w and "seeded" in w for w in warnings)


def test_gamedev_pack_matches_golden(rs_vault, gamedev):
    golden = (Path(__file__).parent / "golden" / "Episode-1-01-context.md").read_text(
        encoding="utf-8"
    )
    generated = build_pack(rs_vault, "Episode 1-01", gamedev).markdown

    def normalize(text: str) -> str:
        text = re.sub(r"`pack-sha: [0-9a-f]{12}`", "`pack-sha: XXX`", text)
        return re.sub(r"_Generated \d{4}-\d{2}-\d{2}", "_Generated DATE", text)

    assert normalize(generated) == normalize(golden)


def test_pack_rejects_wrong_card_type(rs_vault, gamedev, vault, fiction):
    with pytest.raises(ValueError, match="output_card"):
        build_pack(rs_vault, "Väki", gamedev)  # exists, but not the card type
    with pytest.raises(ValueError, match="scene_card"):
        build_pack(vault, "Episode 1-01", fiction)  # wrong vault, wrong shape


# -- init ---------------------------------------------------------------------

def test_init_gamedev_layout_is_manifest_driven(run, tmp_path):
    code, _, _ = run("init", "Kantele", "--set", "gamedev",
                     "--under", str(tmp_path / "Works"), vault=tmp_path)
    assert code == 0
    root = tmp_path / "Works" / "Kantele"
    for rel in [
        "world/canon", "world/mechanics", "world/Design Seed.md",
        "world/language/Prose Voice Canon.md", "structure/cards", "body/drafts",
        "control/timeline/Timeline.md", "control/ratification/Ratification Log.md",
        "control/context-packs", "reviews/canon", "reviews/voice",
        "reviews/mechanics", "reviews/beta",
    ]:
        assert (root / rel).exists(), rel
    text = (root / "Kantele.md").read_text(encoding="utf-8")
    assert "template_set: gamedev" in text
    code, _, _ = run("status", "-p", "Kantele", vault=tmp_path)
    assert code == 0
