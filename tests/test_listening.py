"""The listening set: a small place overheard through partial sources.

What must hold: the timeline is world truth that no narrator holds whole. A
fragment's pack carries one source's knowledge at one moment — what it took
part in, was told, or could perceive — and never the rest. What happened, who
learned it, and what the listener could observe stay three different things.
The fixture is event sheet 001, "First Ice"; its cards project all three
evenings from two listening positions.
"""
import pathlib
import re
import shutil

import pytest

from scribectl.cli import main
from scribectl.core.contextpack import build_pack
from scribectl.core.vault import Vault
from scribectl.templateset import load_set

CARDS = ["Thu 1815 Café", "Thu 1820 Landing", "Thu 1845 Landing", "Thu 1915 Café",
         "Thu 1915 Landing", "Thu 1922 Radio", "Thu 1935 Café staff",
         "Fri 1820 Landing", "Fri 1830 Radio", "Fri 1940 Café", "Fri 2010 Café",
         "Sat 1820 Landing", "Sat 1940 Café", "Sat 1955 Café customers", "Sat 2020 Café"]

BASELINE_STATUS = """\
type          name                    status
----------------------------------------------
canon_node    Café                    ratified
canon_node    Café customers          ratified
canon_node    Café regulars           ratified
canon_node    Café staff              ratified
canon_node    Evening programme       ratified
canon_node    Ferry operator          ratified
canon_node    Inlet road              ratified
canon_node    Landing                 ratified
canon_node    Leena                   ratified
canon_node    Local radio             ratified
canon_node    Radio presenter         ratified
canon_node    Replacement bus         ratified
canon_node    Supplier                ratified
canon_node    Tavi                    ratified
fragment_card Fri 1820 Landing        ready_for_fill
fragment_card Fri 1830 Radio          ready_for_fill
fragment_card Fri 1940 Café           ready_for_fill
fragment_card Fri 2010 Café           ready_for_fill
fragment_card Sat 1820 Landing        ready_for_fill
fragment_card Sat 1940 Café           ready_for_fill
fragment_card Sat 1955 Café customers ready_for_fill
fragment_card Sat 2020 Café           ready_for_fill
fragment_card Thu 1815 Café           ready_for_fill
fragment_card Thu 1820 Landing        ready_for_fill
fragment_card Thu 1845 Landing        ready_for_fill
fragment_card Thu 1915 Café           ready_for_fill
fragment_card Thu 1915 Landing        ready_for_fill
fragment_card Thu 1922 Radio          ready_for_fill
fragment_card Thu 1935 Café staff     ready_for_fill
"""

# Which timeline events reach each source (by position label). This is the
# event sheet's knowledge-boundary table, made checkable.
_THU_LANDING = ["C1.S1700", "C1.S1812", "C1.S1812", "C1.S1837", "C1.S1843", "C1.S1912"]
# C2.S1700 / C3.S1700 are standing conditions: the cold holds.
_FRI_LANDING = _THU_LANDING + ["C2.S0830", "C2.S1530", "C2.S1700", "C2.S1812", "C2.S1812"]
_FRI_CAFE = ["C1.S1700", "C1.S1812", "C1.S1912", "C1.S1930",
             "C2.S1530", "C2.S1700", "C2.S1812", "C2.S1935"]
_SAT_CAFE = _FRI_CAFE + ["C2.S2005", "C3.S1700", "C3.S1812", "C3.S1935"]
KNOWS = {
    "Thu 1820 Landing": _THU_LANDING[:3],
    "Thu 1845 Landing": _THU_LANDING[:5],
    "Thu 1915 Landing": _THU_LANDING,
    "Thu 1815 Café": ["C1.S1700", "C1.S1812"],        # the horn carries; the ramp does not
    "Thu 1915 Café": ["C1.S1700", "C1.S1812", "C1.S1912"],
    "Thu 1922 Radio": ["C1.S1700", "C1.S1920"],       # the bulletin, and nothing behind it
    "Thu 1935 Café staff": ["C1.S1700", "C1.S1930"],  # the delivery is late, not why
    "Fri 1820 Landing": _FRI_LANDING,                 # the notice, not the decision behind it
    "Fri 1830 Radio": ["C1.S1700", "C1.S1920", "C2.S1215", "C2.S1700"],  # now the official explanation
    "Fri 1940 Café": _FRI_CAFE,
    "Fri 2010 Café": _FRI_CAFE + ["C2.S2005"],
    "Sat 1820 Landing": _FRI_LANDING + ["C3.S1700", "C3.S1740", "C3.S1812", "C3.S1812"],
    "Sat 1940 Café": _SAT_CAFE,
    "Sat 1955 Café customers": ["C2.S1700", "C3.S1700", "C3.S1950"],  # felt the cold; never heard Thursday
    "Sat 2020 Café": _SAT_CAFE + ["C3.S1950", "C3.S2015"],
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
    "Fri 1820 Landing": r"cancel|bulletin|expected delivery|official explanation|closure|crates",
    "Fri 1830 Radio": r"slush|inspect|Leena|expected delivery|supplies|crates|is posted|Ice at the ramp|19:35",
    "Fri 1940 Café": r"slush|ramp|\bice\b|inspect|cancel|bulletin|official explanation|Leena|closure",
    "Fri 2010 Café": r"slush|ramp|\bice\b|inspect|cancel|bulletin|official explanation|Leena|closure",
    "Sat 1820 Landing": r"cancel|bulletin|expected delivery|official explanation|closure|crates",
    "Sat 1940 Café": r"slush|ramp|\bice\b|inspect|cancel|bulletin|official explanation|Leena|updated notice",
    "Sat 1955 Café customers": r"slush|ramp|\bice\b|cancel|bulletin|expected delivery|delayed delivery|crates|inspect|official|her horn|Leena",
    "Sat 2020 Café": r"slush|ramp|\bice\b|inspect|cancel|bulletin|official explanation|Leena|updated notice",
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


@pytest.mark.parametrize("card", CARDS)
def test_pack_holds_exactly_what_reached_the_source(lp_vault, listening, card):
    known = _known(build_pack(lp_vault, card, listening).markdown)
    assert re.findall(r"B1\.(C\d\.S\d{4})", known) == KNOWS[card]


@pytest.mark.parametrize("card", CARDS)
def test_no_world_truth_leaks_past_the_boundary(lp_vault, listening, card):
    md = build_pack(lp_vault, card, listening).markdown
    meta = lp_vault.resolve(card).meta
    here = (int(meta["evening"]), int(meta["clock"]))
    for c, t in re.findall(r"B1\.C(\d)\.S(\d{4})", md):   # nothing from later
        assert (int(c), int(t)) < here, f"{card} sees C{c}.S{t}"
    leak = re.search(FORBIDDEN[card], md, re.IGNORECASE)
    assert leak is None, f"{card} pack leaks {leak.group(0)!r}"


@pytest.mark.parametrize("card", CARDS)
def test_fragment_is_a_real_time_window(lp_vault, card):
    """A fragment is real time over [window_from, clock): the card states that
    window, and the pack (cut at clock) covers everything inside it."""
    note = lp_vault.resolve(card)
    frm, clock = int(note.meta["window_from"]), int(note.meta["clock"])
    assert frm < clock
    hm = lambda n: f"{n // 100:02d}:{n % 100:02d}"
    assert f"{hm(frm)}–{hm(clock)}" in note.section("Observation")


# Already heard: earlier fragments at the same listening position ship as
# ambient context so recurring talk can vary. They must never become a
# knowledge channel. Exercised on the real iteration-2 voicings: a fragment is
# heard only when everything its source knew is known to this card's source,
# and only through a draft whose canon review is clean.
LISTENING_FIXTURE = pathlib.Path(__file__).parents[1] / "fixtures" / "listening-post"
VOICED = pathlib.Path(__file__).parents[1] / "docs" / "experiments" / "2026-11-19-first-ice-iteration-2"
_CAFE_THU = ["Thu 1815 Café", "Thu 1915 Café", "Thu 1935 Café staff"]
_LANDING_THU = ["Thu 1820 Landing", "Thu 1845 Landing", "Thu 1915 Landing"]
HEARD = {
    "Thu 1815 Café": [],
    "Thu 1820 Landing": [],
    "Thu 1845 Landing": _LANDING_THU[:1],
    "Thu 1915 Café": _CAFE_THU[:1],
    "Thu 1915 Landing": _LANDING_THU[:2],
    "Thu 1922 Radio": [],                  # the café heard the horn; the presenter did not
    "Thu 1935 Café staff": [],             # the radio carried the bulletin; the staff did not take it in
    "Fri 1820 Landing": _LANDING_THU,
    "Fri 1830 Radio": ["Thu 1922 Radio"],  # the presenter's own Thursday, nothing of the room
    "Fri 1940 Café": _CAFE_THU,            # the café hears its staff, never the bulletins
    "Fri 2010 Café": _CAFE_THU + ["Fri 1940 Café"],
    "Sat 1820 Landing": _LANDING_THU + ["Fri 1820 Landing"],
    "Sat 1940 Café": _CAFE_THU + ["Fri 1940 Café", "Fri 2010 Café"],
    "Sat 1955 Café customers": [],         # they never heard Thursday
    "Sat 2020 Café": _CAFE_THU + ["Fri 1940 Café", "Fri 2010 Café", "Sat 1940 Café"],
    # ... and not Sat 1955: its only draft-a failed canon review
}


@pytest.fixture(scope="module")
def voiced_vault(tmp_path_factory):
    root = tmp_path_factory.mktemp("voiced") / "listening-post"
    shutil.copytree(LISTENING_FIXTURE, root)
    for sub, dest in (("drafts", "body/drafts"), ("reviews", "reviews/canon")):
        for f in (VOICED / sub).glob("*.md"):
            shutil.copy(f, root / dest / f.name)
    return Vault.load(root)


def _heard(md: str) -> str:
    return md.split("## Already heard here (ambient, not canon)", 1)[1].split("\n## ", 1)[0]


@pytest.mark.parametrize("card", CARDS)
def test_unvoiced_fixture_has_heard_nothing(lp_vault, listening, card):
    assert _heard(build_pack(lp_vault, card, listening).markdown).strip().endswith(
        "_(nothing heard here before)_")


@pytest.mark.parametrize("card", CARDS)
def test_already_heard_never_widens_what_a_source_knows(voiced_vault, listening, card):
    md = build_pack(voiced_vault, card, listening).markdown
    heard = _heard(md)
    assert re.findall(r"^### (.+)$", heard, re.M) == HEARD[card]
    assert "Introduced candidates" not in heard and "Uncertainties" not in heard
    assert _known(md) == _known(build_pack(Vault.load(LISTENING_FIXTURE), card, listening).markdown)
    leak = re.search(FORBIDDEN[card], md, re.IGNORECASE)   # the whole pack, heard text included
    assert leak is None, f"{card} pack leaks {leak.group(0)!r} through what it heard"


@pytest.mark.parametrize("card", ["Sat 1955 Café customers", "Sat 2020 Café"])
def test_superseded_entry_never_reaches_a_pack(lp_vault, listening, card):
    # B1.C3.S1950 once told voicers the closure "comes up only in passing";
    # its correction keeps what the customers know and drops the direction.
    known = _known(build_pack(lp_vault, card, listening).markdown)
    assert "comes up only in passing" not in known
    assert "Customers, who know the ferry is off, make ordinary plans around the bus." in known


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
