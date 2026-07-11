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


# -- ratify --sweep -----------------------------------------------------------

SWEEP_INBOX = """\
---
type: ratification_inbox
---

# Ratification Inbox

- [x] "Ash-line ledgers track heat debts by family." → [[The Volcanic City-State]]
      (from [[Scene 01-01 — draft 1]], pack 0123abcdef01)
- [-] "A royal bloodline rules the rim." → [[The Volcanic City-State]]
- [>] "Gate-warden guild controls the curfew keys." → [[Mara Vey]]
- [ ] "The Mist sings in Bay Nine." → [[The Mist]]
"""


@pytest.fixture
def inbox(scratch_project) -> Path:
    path = scratch_project / "control/ratification/Inbox.md"
    path.write_text(SWEEP_INBOX, encoding="utf-8")
    return path


def test_sweep_executes_verdicts(run, scratch_root, scratch_project, inbox):
    node = scratch_project / "world/canon/The Volcanic City-State.md"
    log = scratch_project / "control/ratification/Ratification Log.md"
    node_before, log_before = node.read_text(encoding="utf-8"), log.read_text(encoding="utf-8")

    code, out, err = run("ratify", "--sweep", vault=scratch_root)
    assert code == 0 and err == ""

    # Accepted fact landed at the tail of Ratified facts; nothing else moved.
    node_after = node.read_text(encoding="utf-8")
    assert "- Class maps loosely to altitude: rim is power, lower terraces are labor.\n- Ash-line ledgers track heat debts by family.\n\n## Open questions" in node_after
    assert node_after.startswith(node_before.split("## Ratified facts")[0])
    assert node_after.endswith(node_before.split("labor.")[1])

    # Receipts: verdict wording + route + provenance, writer typed none of it.
    tail = log.read_text(encoding="utf-8")[len(log_before):]
    assert log.read_text(encoding="utf-8").startswith(log_before)  # append-only
    assert '"Ash-line ledgers track heat debts by family." → promoted to [[The Volcanic City-State]] (from [[Scene 01-01 — draft 1]], pack 0123abcdef01)' in tail
    assert "### Rejected\n- \"A royal bloodline rules the rim.\"" in tail
    assert "### Deferred\n- \"Gate-warden guild controls the curfew keys.\"" in tail

    # Decided candidates cleared; the undecided one keeps its place.
    left = inbox.read_text(encoding="utf-8")
    assert "Bay Nine" in left and "Ash-line" not in left and "# Ratification Inbox" in left

    # The two halves of ratification moved together: fact + receipt = ratified.
    _, out, _ = run("status", vault=scratch_root)
    assert "canon_node   The Volcanic City-State ratified" in out


def test_sweep_dry_run_writes_nothing(run, scratch_root, scratch_project, inbox):
    snapshot = {p: p.read_text(encoding="utf-8")
                for p in scratch_project.rglob("*.md")}
    code, out, _ = run("ratify", "--sweep", "--dry-run", vault=scratch_root)
    assert code == 0
    assert "dry run" in out and "Ash-line" in out and "would clear 3" in out
    assert snapshot == {p: p.read_text(encoding="utf-8")
                        for p in scratch_project.rglob("*.md")}


def test_sweep_unresolved_target_stays_in_inbox(run, scratch_root, scratch_project, inbox):
    inbox.write_text(SWEEP_INBOX.replace("[[Mara Vey]]", "[[No Such Node]]").replace(
        "- [>] \"Gate-warden guild", "- [x] \"Gate-warden guild"), encoding="utf-8")
    code, _, err = run("ratify", "--sweep", vault=scratch_root)
    assert code == 0
    assert "No Such Node" in err and "stays in the inbox" in err
    left = inbox.read_text(encoding="utf-8")
    assert "Gate-warden" in left and "Ash-line" not in left  # valid ones still swept


def test_sweep_accept_targets_nodes_only(run, scratch_root, scratch_project, inbox):
    inbox.write_text('- [x] "fact" → [[Scene 01-01]]\n', encoding="utf-8")
    code, _, err = run("ratify", "--sweep", vault=scratch_root)
    assert code == 0
    assert "scene_card" in err and "fact-bearing" in err
    assert "[[Scene 01-01]]" in inbox.read_text(encoding="utf-8")


def test_sweep_into_adopted_stub_retires_placeholder(run, scratch_root, scratch_project, inbox):
    (scratch_root / "Legacy.md").write_text("# Legacy\n\nOre.\n", encoding="utf-8")
    run("adopt", "Legacy", vault=scratch_root)
    inbox.write_text('- [x] "Extracted, ratified wording." → [[Legacy]]\n', encoding="utf-8")
    code, _, _ = run("ratify", "--sweep", vault=scratch_root)
    assert code == 0
    stub = (scratch_project / "world/canon/Legacy.md").read_text(encoding="utf-8")
    assert "_(none" not in stub and "- Extracted, ratified wording." in stub
    _, out, _ = run("status", vault=scratch_root)
    assert "canon_node   Legacy                  ratified" in out


def test_sweep_nothing_ticked(run, scratch_root, inbox):
    inbox.write_text('- [ ] "still thinking" → [[The Mist]]\n', encoding="utf-8")
    code, out, _ = run("ratify", "--sweep", vault=scratch_root)
    assert code == 0
    assert "nothing to sweep" in out and "1 pending" in out


def test_sweep_requires_inbox(run, scratch_root):
    code, _, err = run("ratify", "--sweep", vault=scratch_root)
    assert code != 0
    assert "no inbox" in err


def test_sweep_rejects_flag_mixing(run, scratch_root, inbox):
    code, _, err = run("ratify", "--sweep", "--accept", "x", vault=scratch_root)
    assert code != 0 and "inbox" in err
    code, _, err = run("ratify", "--dry-run", "--accept", "x", vault=scratch_root)
    assert code != 0 and "--sweep" in err


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
        "control/ratification/Ratification Log.md", "control/ratification/Inbox.md",
        "control/context-packs",
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
