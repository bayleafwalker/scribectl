"""The essay template set: standalone nonfiction drafted from captured ore.

What must hold (the kotona dogfood findings, mechanized): the card scaffold
carries no fiction fields, `pull.ore` ships captured source notes into the
pack verbatim instead of briefing them as empty fact stubs, unresolved and
placeholder ore links gate the card exactly like scope links, and the
fiction/gamedev sets keep shipping byte-identical packs (their golden tests
are the other half of this file).
"""
from datetime import date
from pathlib import Path

import pytest

from scribectl.cli import main
from scribectl.core.contextpack import build_pack
from scribectl.core.vault import Vault
from scribectl.templateset import load_set


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
def essay():
    return load_set("essay")


@pytest.fixture
def essay_project(run, tmp_path) -> Path:
    code, _, _ = run("init", "Kotona", "--set", "essay",
                     "--under", str(tmp_path / "Works"), vault=tmp_path)
    assert code == 0
    return tmp_path / "Works" / "Kotona"


ORE_BODY = """\
Sweep of the backlog tooling gap.

## The numbers
831 items, seven doc refs. The tool was never in the loop.

Desire paths say the convention failed, not the writers.
"""


def _capture_ore(run, essay_project, tmp_path) -> str:
    """Land ORE_BODY through the real capture path; return its link target."""
    f = tmp_path / "ref-research.md"
    f.write_text(ORE_BODY, encoding="utf-8")
    code, _, _ = run("capture", "Ref research", "-p", "Kotona",
                     "--kind", "notes", "--from", str(f))
    assert code == 0
    return f"{date.today().isoformat()} Ref research"


def _author_card(essay_project: Path, name: str, sources: list[str],
                 canon_scope: list[str]) -> None:
    src = "\n".join(f'  - "[[{s}]]"' for s in sources) or "  []"
    scope = "\n".join(f'  - "[[{s}]]"' for s in canon_scope) or "  []"
    (essay_project / "structure/essays" / f"{name}.md").write_text(
        f"""---
type: essay_card
kind: essay
distribution: publication
sources:
{src}
canon_scope:
{scope}
mode: body_fill
target_words: 800
---

# {name}

## Brief
Why the backlog reference convention failed.

## Required beats
- The tool was never in the loop.

## Exit state
Reader stops blaming writers for missing refs.

## Tone target
Dry, specific.

## Do not
- No private infrastructure details.
""", encoding="utf-8")


# -- the set itself -----------------------------------------------------------

def test_essay_set_shape(essay):
    assert essay.card_type == "essay_card"
    assert essay.node_types == ("canon_node",)
    assert essay.ore_fields == ("sources",)
    assert essay.fill_fields == ("canon_scope", "sources")
    assert essay.position_fields == ()
    # The ore rule is this set's; the existing shapes are untouched by it.
    assert load_set("fiction").ore_fields == ()
    assert load_set("gamedev").ore_fields == ()


def test_init_essay_layout_is_manifest_driven(run, tmp_path, essay_project):
    for rel in [
        "world/canon", "world/Site Seed.md",
        "world/language/Prose Voice Canon.md", "structure/essays", "sources",
        "body/drafts", "control/timeline/Timeline.md",
        "control/ratification/Ratification Log.md", "control/context-packs",
        "reviews/canon", "reviews/voice", "reviews/beta", "AGENTS.md",
    ]:
        assert (essay_project / rel).exists(), rel
    assert "template_set: essay" in (essay_project / "Kotona.md").read_text(encoding="utf-8")
    code, _, _ = run("status", "-p", "Kotona", vault=tmp_path)
    assert code == 0


# -- derived state: ore links gate the card like scope links -------------------

def _card_row(out: str, name: str) -> str:
    return next(l for l in out.splitlines() if name in l)


def test_fresh_scaffold_awaits_scope(run, tmp_path, essay_project):
    code, out, _ = run("new", "card", "The Ref Nobody Adds", "-p", "Kotona", vault=tmp_path)
    assert code == 0
    assert (essay_project / "structure/essays/The Ref Nobody Adds.md").exists()
    assert (essay_project / "control/contracts/fill-the-ref-nobody-adds.md").exists()
    _, out, _ = run("status", "-p", "Kotona", vault=tmp_path)
    assert "awaiting_scope" in _card_row(out, "The Ref Nobody Adds")


def test_unresolved_source_blocks_fill(run, tmp_path, essay_project):
    _author_card(essay_project, "The Ref Nobody Adds", ["Missing Research"], [])
    _, out, _ = run("status", "-p", "Kotona", vault=tmp_path)
    row = _card_row(out, "The Ref Nobody Adds")
    assert "blocked_unresolved_scope" in row and "[[Missing Research]]" in row


def test_captured_source_readies_card(run, tmp_path, essay_project):
    ore = _capture_ore(run, essay_project, tmp_path)
    _author_card(essay_project, "The Ref Nobody Adds", [ore], [])
    _, out, _ = run("status", "-p", "Kotona", vault=tmp_path)
    assert "ready_for_fill" in _card_row(out, "The Ref Nobody Adds")


# -- the pack: ore ships verbatim ----------------------------------------------

def test_pack_ships_ore_verbatim(run, tmp_path, essay_project, essay):
    ore = _capture_ore(run, essay_project, tmp_path)
    (essay_project / "world/canon/Desire Paths.md").write_text(
        """---
type: canon_node
domain: position
importance: core
---

# Desire Paths

## One-line function
The lens: worn ground is data, not disobedience.

## Ratified facts
- A convention nobody follows indicts the convention.

## Open questions
- none

## Essay utility
Private scaffolding that must never ship.
""", encoding="utf-8")
    _author_card(essay_project, "The Ref Nobody Adds", [ore], ["Desire Paths"])

    pack = build_pack(Vault.load(essay_project), "The Ref Nobody Adds", essay)
    md = pack.markdown
    assert "## Essay card" in md
    # Ore ships whole — subheadings and all — and is labelled unratified.
    assert "## Source material (raw ore — unratified)" in md
    assert f"### {ore}" in md
    assert "831 items, seven doc refs" in md
    assert "## The numbers" in md
    # It briefs nowhere as an empty fact stub, and draws no canon warnings.
    assert "node is a stub" not in md
    assert not any(ore in w for w in pack.warnings)
    # Canon discipline is unchanged beside the ore: facts ship, scaffolding doesn't.
    assert "worn ground is data" in md
    assert "convention nobody follows indicts" in md
    assert "Essay utility" not in md and "Private scaffolding" not in md
    assert "## Hard exclusions" in md and "No private infrastructure details" in md


def test_pack_cli_freezes_essay_pack(run, tmp_path, essay_project):
    ore = _capture_ore(run, essay_project, tmp_path)
    _author_card(essay_project, "The Ref Nobody Adds", [ore], [])
    code, out, _ = run("pack", "The Ref Nobody Adds", "-p", "Kotona", vault=tmp_path)
    assert code == 0
    packs = list((essay_project / "control/context-packs").glob("*.md"))
    assert len(packs) == 1
    assert "831 items" in packs[0].read_text(encoding="utf-8")


def test_missing_ore_link_ships_as_unresolved(run, tmp_path, essay_project, essay):
    _author_card(essay_project, "The Ref Nobody Adds", ["Missing Research"], [])
    md = build_pack(Vault.load(essay_project), "The Ref Nobody Adds", essay).markdown
    assert "[[Missing Research]] — referenced but no note exists" in md
