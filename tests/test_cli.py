"""CLI surface: projects, status, pack, ratify, adopt, init.

Write discipline under test throughout: the engine only creates files in
designated outputs and appends to ledgers; it never rewrites a note.
"""
from pathlib import Path

import pytest

from scribectl.cli import main

BASELINE_STATUS = """\
type         name                    status
---------------------------------------------
canon_node   Mara Vey                seeded
canon_node   The Mist                ratified
canon_node   The Volcanic City-State seeded
scene_card   Scene 01-01             blocked_unresolved_scope  (missing: [[Lower Ashmarket]])
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


# -- projects ---------------------------------------------------------------

def test_projects_lists_discovered(run, fixture_root):
    code, out, _ = run("projects", vault=fixture_root.parent)
    assert code == 0
    assert "Fertile Flames" in out
    assert "fiction" in out
    assert str(fixture_root) in out
    # The second fixture project rides the second template set.
    assert "Runosong" in out and "gamedev" in out


def test_projects_none_found(run, tmp_path):
    code, out, _ = run("projects", vault=tmp_path)
    assert code == 0
    assert "no projects" in out.lower()


# -- status -----------------------------------------------------------------

def test_status_matches_ff_baseline(run, fixture_root):
    """The parity gate: same rows, same formatting as ff.py status."""
    code, out, _ = run("status", "-p", "Fertile Flames", vault=fixture_root.parent)
    assert code == 0
    assert out == BASELINE_STATUS


def test_status_infers_single_project(run, fixture_root):
    # Scoped to the project dir itself: fixtures/ now holds two projects.
    code, out, _ = run("status", vault=fixture_root)
    assert code == 0
    assert out == BASELINE_STATUS


def test_status_ambiguous_across_projects_demands_p(run, fixture_root):
    code, _, err = run("status", vault=fixture_root.parent)
    assert code != 0
    assert "ambiguous" in err and "Runosong" in err


def test_status_unknown_project(run, fixture_root):
    code, _, err = run("status", "-p", "Nope", vault=fixture_root.parent)
    assert code != 0
    assert "Nope" in err


def test_status_write_emits_dashboard(run, scratch_root, scratch_project):
    code, _, _ = run("status", "--write", vault=scratch_root)
    assert code == 0
    dash = scratch_project / "control" / "Status.md"
    text = dash.read_text(encoding="utf-8")
    assert "generated" in text.lower()
    assert "Scene 01-01" in text and "blocked_unresolved_scope" in text
    # The dashboard is a cache read back by nothing: derived rows unchanged.
    code, out, _ = run("status", vault=scratch_root)
    assert out == BASELINE_STATUS


# -- pack -------------------------------------------------------------------

def test_pack_writes_frozen_pack(run, scratch_root, scratch_project):
    code, out, _ = run("pack", "Scene 01-01", vault=scratch_root)
    assert code == 0
    packs = list((scratch_project / "control/context-packs").glob("Scene-01-01-*-context.md"))
    assert len(packs) == 1
    text = packs[0].read_text(encoding="utf-8")
    assert text.startswith("# Context Pack — Scene 01-01")
    sha = text.split("`pack-sha: ")[1][:12]
    # The sha is the filename: a later regeneration can never clobber this freeze.
    assert packs[0].name == f"Scene-01-01-{sha}-context.md"
    assert sha in out and str(packs[0]) in out


def test_pack_freeze_survives_regeneration(run, scratch_root, scratch_project):
    """Regenerating after canon changes must add a pack, not overwrite the audit copy."""
    run("pack", "Scene 01-01", vault=scratch_root)
    _, out, _ = run("pack", "Scene 01-01", vault=scratch_root)
    assert "unchanged" in out  # identical content: same freeze, no rewrite
    node = scratch_project / "world/canon/The Mist.md"
    node.write_text(node.read_text(encoding="utf-8").replace(
        "- The Mist is not weather", "- The Mist hums at dawn.\n- The Mist is not weather"
    ), encoding="utf-8")
    code, _, _ = run("pack", "Scene 01-01", vault=scratch_root)
    assert code == 0
    packs = list((scratch_project / "control/context-packs").glob("Scene-01-01-*-context.md"))
    assert len(packs) == 2


def test_pack_warns_on_unratified_scope(run, scratch_root):
    _, _, err = run("pack", "Scene 01-01", vault=scratch_root)
    assert "The Volcanic City-State" in err and "seeded" in err
    assert "The Mist" not in err  # ratified nodes are not warned about


def test_pack_unknown_card(run, scratch_root):
    code, _, err = run("pack", "Scene 99-99", vault=scratch_root)
    assert code != 0
    assert "Scene 99-99" in err


# -- ratify -----------------------------------------------------------------

def test_ratify_appends_only_and_promotes(run, scratch_root, scratch_project):
    log = scratch_project / "control/ratification/Ratification Log.md"
    before = log.read_text(encoding="utf-8")
    code, _, _ = run(
        "ratify",
        "--accept", '"ash-line ledgers" → promoted to [[The Volcanic City-State]] — load-bearing.',
        "--reject", '"royal bloodline" (source draft v1) — contradicts the civic frame.',
        "--defer", '"gate-warden guild" (source draft v1) — depends on B2 politics.',
        vault=scratch_root,
    )
    assert code == 0
    after = log.read_text(encoding="utf-8")
    assert after.startswith(before)  # append-only: prior bytes untouched
    tail = after[len(before):]
    assert "### Accepted" in tail and "### Rejected" in tail and "### Deferred" in tail
    assert "ash-line ledgers" in tail

    _, out, _ = run("status", vault=scratch_root)
    assert "canon_node   The Volcanic City-State ratified" in out


def test_ratify_same_day_reuses_date_heading(run, scratch_root, scratch_project):
    from datetime import date

    log = scratch_project / "control/ratification/Ratification Log.md"
    run("ratify", "--accept", "first entry", vault=scratch_root)
    run("ratify", "--defer", "second entry", vault=scratch_root)
    text = log.read_text(encoding="utf-8")
    assert text.count(f"## {date.today().isoformat()}") == 1
    assert "first entry" in text and "second entry" in text


def test_ratify_requires_at_least_one_entry(run, scratch_root, scratch_project):
    log = scratch_project / "control/ratification/Ratification Log.md"
    before = log.read_text(encoding="utf-8")
    code, _, err = run("ratify", vault=scratch_root)
    assert code != 0
    assert log.read_text(encoding="utf-8") == before


# -- adopt ------------------------------------------------------------------

def test_adopt_wraps_legacy_note_as_stub(run, scratch_root, scratch_project):
    legacy_dir = scratch_root / "30 Creative"
    legacy_dir.mkdir()
    (legacy_dir / "Fertile Flames Saga.md").write_text(
        "# Fertile Flames Saga\n\nOld freewriting. Ore, not canon.\n", encoding="utf-8"
    )
    code, out, _ = run("adopt", "Fertile Flames Saga", vault=scratch_root)
    assert code == 0
    stub = scratch_project / "world/canon/Fertile Flames Saga.md"
    assert stub.exists()
    text = stub.read_text(encoding="utf-8")
    assert "type: canon_node" in text
    assert "[[Fertile Flames Saga]]" in text
    assert "## Open questions" in text
    # The legacy note itself is never touched.
    assert "Ore, not canon" in (legacy_dir / "Fertile Flames Saga.md").read_text(encoding="utf-8")
    # Discover-mode output: it reads as a stub, never final canon.
    _, out, _ = run("status", vault=scratch_root)
    assert "canon_node   Fertile Flames Saga     stub" in out


def test_adopt_refuses_to_overwrite(run, scratch_root, scratch_project):
    legacy = scratch_root / "Legacy.md"
    legacy.write_text("# Legacy\n", encoding="utf-8")
    assert run("adopt", "Legacy", vault=scratch_root)[0] == 0
    code, _, err = run("adopt", "Legacy", vault=scratch_root)
    assert code != 0
    assert "exist" in err.lower()


def test_adopt_missing_note(run, scratch_root):
    code, _, err = run("adopt", "No Such Note", vault=scratch_root)
    assert code != 0


# -- init -------------------------------------------------------------------

def test_init_instantiates_project(run, scratch_root):
    code, out, _ = run("init", "Sunstolen", "--under", str(scratch_root / "Works"),
                       vault=scratch_root)
    assert code == 0
    root = scratch_root / "Works" / "Sunstolen"
    assert (root / "Sunstolen.md").exists()
    for rel in [
        "world/canon", "world/language/Prose Voice Canon.md", "world/World Seed.md",
        "structure/scenes", "body/drafts", "control/timeline/Timeline.md",
        "control/ratification/Ratification Log.md", "control/context-packs",
        "reviews/canon", "reviews/voice", "reviews/beta",
    ]:
        assert (root / rel).exists(), rel

    # Discovery now sees both projects; the new one is empty but legible.
    _, out, _ = run("projects", vault=scratch_root)
    assert "Fertile Flames" in out and "Sunstolen" in out
    code, _, _ = run("status", "-p", "Sunstolen", vault=scratch_root)
    assert code == 0


def test_init_refuses_existing_project(run, scratch_root):
    code, _, err = run("init", "Fertile Flames", "--under", str(scratch_root / "Works"),
                       vault=scratch_root)
    assert code != 0
    assert "exist" in err.lower()


def test_init_unknown_template_set(run, scratch_root):
    code, _, err = run("init", "Essayish", "--set", "essay",
                       "--under", str(scratch_root / "Works"), vault=scratch_root)
    assert code != 0
