"""The listening set: a small place overheard through partial sources.

What must hold: the timeline is world truth that no narrator holds whole. A
fragment's pack carries one source's knowledge at one moment — what it took
part in, was told, or could perceive — and never the rest. What happened, who
learned it, and what the listener could observe stay three different things.
The fixture is event sheet 001, "First Ice"; its cards project Thursday only.
"""
import pathlib
import re

import pytest

from scribectl.cli import main
from scribectl.core.contextpack import build_pack
from scribectl.core.vault import Vault
from scribectl.templateset import load_set

THURSDAY = ["Thu 1815 Café", "Thu 1820 Landing", "Thu 1845 Landing", "Thu 1915 Café",
            "Thu 1915 Landing", "Thu 1922 Radio", "Thu 1935 Café staff"]

BASELINE_STATUS = """\
type          name                status
------------------------------------------
canon_node    Café                ratified
canon_node    Café customers      ratified
canon_node    Café staff          ratified
canon_node    Ferry operator      ratified
canon_node    Inlet road          ratified
canon_node    Landing             ratified
canon_node    Leena               ratified
canon_node    Local radio         ratified
canon_node    Radio presenter     ratified
canon_node    Replacement bus     ratified
canon_node    Supplier            ratified
canon_node    Tavi                ratified
fragment_card Thu 1815 Café       ready_for_fill
fragment_card Thu 1820 Landing    ready_for_fill
fragment_card Thu 1845 Landing    ready_for_fill
fragment_card Thu 1915 Café       ready_for_fill
fragment_card Thu 1915 Landing    ready_for_fill
fragment_card Thu 1922 Radio      ready_for_fill
fragment_card Thu 1935 Café staff ready_for_fill
"""

# Which timeline events reach each Thursday source (by position label). This
# is the event sheet's knowledge-boundary table, made checkable.
KNOWS = {
    "Thu 1820 Landing": ["S1700", "S1812", "S1812"],
    "Thu 1845 Landing": ["S1700", "S1812", "S1812", "S1837", "S1843"],
    "Thu 1915 Landing": ["S1700", "S1812", "S1812", "S1837", "S1843", "S1912"],
    "Thu 1815 Café": ["S1700", "S1812"],        # the horn carries; the ramp does not
    "Thu 1915 Café": ["S1700", "S1812", "S1912"],
    "Thu 1922 Radio": ["S1700", "S1920"],       # the bulletin, and nothing behind it
    "Thu 1935 Café staff": ["S1700", "S1930"],  # the delivery is late, not why
}

# Words that would mean world truth leaked past a source's boundary — in the
# card as much as in the timeline section: a card is a leak vector too.
FORBIDDEN = {
    "Thu 1922 Radio": r"slush|ramp|\bice\b|Leena|expected delivery|supplies|closure|winter|inspect",
    "Thu 1935 Café staff": r"slush|ramp|\bice\b|cancel|bulletin|closure|winter",
    "Thu 1815 Café": r"slush|ramp|cancel|bulletin|expected delivery",
    "Thu 1915 Café": r"slush|ramp|cancel|bulletin|expected delivery",
    "Thu 1820 Landing": r"slush|cancel|bulletin|expected delivery",
    "Thu 1845 Landing": r"cancel|bulletin|expected delivery|reports",
    "Thu 1915 Landing": r"cancel|bulletin|expected delivery|reports",
}


@pytest.fixture
def lp_vault(listening_root):
    return Vault.load(listening_root)


@pytest.fixture
def listening():
    return load_set("listening")


@pytest.fixture
def run(monkeypatch, capsys):
    def _run(*argv, vault=None):
        if vault is not None:
            monkeypatch.setenv("SCRIBECTL_VAULT", str(vault))
        code = main(list(argv))
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run


def _known(md: str) -> str:
    return md.split("## Known to this source (timeline, scoped)", 1)[1].split("\n## ", 1)[0]


def test_listening_set_is_the_only_scoped_one(listening):
    assert listening.card_type == "fragment_card"
    assert listening.knowledge == "scoped"
    assert listening.position_fields == ("sheet", "evening", "clock")
    for other in ("fiction", "gamedev", "essay"):
        assert load_set(other).knowledge == "open"


def test_status_baseline(run, listening_root):
    code, out, _ = run("status", "-p", "Listening Post", vault=listening_root.parent)
    assert code == 0
    assert out == BASELINE_STATUS


@pytest.mark.parametrize("card", THURSDAY)
def test_pack_holds_exactly_what_reached_the_source(lp_vault, listening, card):
    known = _known(build_pack(lp_vault, card, listening).markdown)
    assert re.findall(r"B1\.C1\.(S\d{4})", known) == KNOWS[card]


@pytest.mark.parametrize("card", THURSDAY)
def test_no_world_truth_leaks_past_the_boundary(lp_vault, listening, card):
    md = build_pack(lp_vault, card, listening).markdown
    assert "B1.C2" not in md and "B1.C3" not in md     # Thursday cannot know Friday
    leak = re.search(FORBIDDEN[card], md, re.IGNORECASE)
    assert leak is None, f"{card} pack leaks {leak.group(0)!r}"


def test_radio_pack_matches_golden(lp_vault, listening):
    """Byte-stable modulo the run date (and so the sha, which hashes it)."""
    generated = build_pack(lp_vault, "Thu 1922 Radio", listening).markdown
    golden = (pathlib.Path(__file__).parent / "golden" / "Thu-1922-Radio-context.md").read_text(
        encoding="utf-8")

    def normalize(text: str) -> str:
        text = re.sub(r"`pack-sha: [0-9a-f]+`", "`pack-sha: X`", text)
        return re.sub(r"_Generated \d{4}-\d{2}-\d{2}", "_Generated DATE", text)

    assert normalize(generated) == normalize(golden)


def test_init_listening_layout_is_manifest_driven(run, tmp_path):
    code, _, _ = run("init", "Harbour", "--set", "listening",
                     "--under", str(tmp_path / "Works"), vault=tmp_path)
    assert code == 0
    root = tmp_path / "Works" / "Harbour"
    for rel in ["world/canon", "world/World Seed.md", "world/language/Prose Voice Canon.md",
                "structure/fragments", "body/drafts", "control/timeline/Timeline.md",
                "control/ratification/Ratification Log.md", "control/context-packs"]:
        assert (root / rel).exists(), rel
    assert "template_set: listening" in (root / "Harbour.md").read_text(encoding="utf-8")
    code, _, _ = run("status", "-p", "Harbour", vault=tmp_path)
    assert code == 0
