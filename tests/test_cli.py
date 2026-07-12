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


def test_status_json_carries_project_header_and_card_artifacts(run, scratch_root, scratch_project):
    """The dispatcher's whole view of a project (docs/DISPATCH.md): paths it
    may read, rows it acts on, per-card drafts and reviews-by-kind."""
    import json

    (scratch_project / "body/drafts/Scene 01-01 draft v1.md").write_text(
        "---\ntype: draft\nscene: \"[[Scene 01-01]]\"\n---\n\nProse here.\n",
        encoding="utf-8")
    (scratch_project / "reviews/canon/Scene 01-01 canon review.md").write_text(
        "---\ntype: review_report\nkind: canon\ntarget: \"[[Scene 01-01]]\"\n"
        "draft: \"[[Scene 01-01 draft v1]]\"\nverdict: clean\n---\n\n# canon review\n",
        encoding="utf-8")
    code, out, _ = run("status", "--json", vault=scratch_root)
    assert code == 0
    data = json.loads(out)
    assert data["project"]["name"] == "Fertile Flames"
    assert data["project"]["card_type"] == "scene_card"
    assert Path(data["project"]["paths"]["voice_canon"]).is_file()
    assert Path(data["project"]["paths"]["timeline"]).is_file()
    card = next(r for r in data["rows"] if r["type"] == "scene_card")
    assert card["status"] == "reviewed"
    assert card["drafts"] == ["Scene 01-01 draft v1"]
    assert card["reviews"] == [{"name": "Scene 01-01 canon review",
                                "kind": "canon",
                                "draft": "Scene 01-01 draft v1"}]
    # Node rows stay lean: no artifact keys.
    node = next(r for r in data["rows"] if r["type"] == "canon_node")
    assert "drafts" not in node


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
    code, _, err = run("ratify", "--mine", "--accept", "x", vault=scratch_root)
    assert code != 0 and "--mine" in err


# -- ratify --mine ------------------------------------------------------------

CANON_REVIEW = """\
---
type: review_report
kind: canon
target: "[[Scene 01-01]]"
draft: "[[Scene 01-01 — draft 1]]"
pack_sha: 0123abcdef01
verdict: clean
---

## Findings
- none

## Introduced candidates seen in draft
- "Ash-line ledgers are audited at solstice" → [[The Volcanic City-State]]
- "The clerk's alibi stamp" — appears in neither timeline nor pack
"""


@pytest.fixture
def landed_review(scratch_project) -> Path:
    path = scratch_project / "reviews/canon/Scene 01-01 — draft 1 — canon review.md"
    path.write_text(CANON_REVIEW, encoding="utf-8")
    return path


def test_mine_queues_pending_and_creates_inbox(run, scratch_root, scratch_project, landed_review):
    code, out, err = run("ratify", "--mine", vault=scratch_root)
    assert code == 0 and err == ""
    assert "queued 2 candidates from 1 review report" in out
    # The inbox was created from the set's template, candidates land pending
    # with full provenance; nothing is ever mined as decided.
    text = (scratch_project / "control/ratification/Inbox.md").read_text(encoding="utf-8")
    assert "# Ratification Inbox" in text
    assert ('- [ ] "Ash-line ledgers are audited at solstice" → [[The Volcanic City-State]]\n'
            "      (from [[Scene 01-01 — draft 1]], pack 0123abcdef01, "
            "via [[Scene 01-01 — draft 1 — canon review]])") in text
    assert '- [ ] "The clerk\'s alibi stamp"' in text
    assert "- [x]" not in text.split("```")[-1]

    # Idempotent: the via-link marks the report mined.
    code, out, _ = run("ratify", "--mine", vault=scratch_root)
    assert code == 0 and "nothing to mine" in out


def test_mine_dry_run_writes_nothing(run, scratch_root, scratch_project, landed_review):
    code, out, _ = run("ratify", "--mine", "--dry-run", vault=scratch_root)
    assert code == 0
    assert "dry run" in out and "Ash-line ledgers are audited" in out
    assert not (scratch_project / "control/ratification/Inbox.md").exists()


def test_sweep_mines_before_executing(run, scratch_root, scratch_project, inbox, landed_review):
    code, out, err = run("ratify", "--sweep", vault=scratch_root)
    assert code == 0
    assert "queued 2 candidates" in out and "cleared 3 candidates" in out
    text = inbox.read_text(encoding="utf-8")
    # Decided candidates swept out, freshly mined ones sit pending.
    assert "Ash-line ledgers track heat debts" not in text
    assert '- [ ] "Ash-line ledgers are audited at solstice"' in text
    # The unrouted mined candidate nags from stderr until the writer routes it.
    assert "no `→ [[target]]`" in err

    # Ticking a mined candidate ratifies it with provenance carried verbatim.
    inbox.write_text(text.replace('- [ ] "Ash-line ledgers are audited at solstice"',
                                  '- [x] "Ash-line ledgers are audited at solstice"'),
                     encoding="utf-8")
    code, _, _ = run("ratify", "--sweep", vault=scratch_root)
    assert code == 0
    log = (scratch_project / "control/ratification/Ratification Log.md").read_text(encoding="utf-8")
    assert ('"Ash-line ledgers are audited at solstice" → promoted to '
            "[[The Volcanic City-State]] (from [[Scene 01-01 — draft 1]], "
            "pack 0123abcdef01, via [[Scene 01-01 — draft 1 — canon review]])") in log
    # The ledger's via-link keeps the report mined-once forever.
    code, out, _ = run("ratify", "--mine", vault=scratch_root)
    assert "nothing to mine" in out


# -- propose ------------------------------------------------------------------

def test_propose_freezes_pack_and_scaffolds_proposal(run, scratch_runosong):
    code, out, err = run("propose", "--into", "Ilmi", "--source", "Design Seed",
                         vault=scratch_runosong)
    assert code == 0 and err == ""
    proj = scratch_runosong / "Works" / "Runosong"
    packs = list((proj / "control/mining-packs").glob("*mining.md"))
    props = list((proj / "control/proposals").glob("*.md"))
    assert len(packs) == 1 and len(props) == 1
    ptext = props[0].read_text(encoding="utf-8")
    assert "type: fact_proposal" in ptext
    assert 'target: "[[Ilmi]]"' in ptext and 'source: "[[Design Seed]]"' in ptext
    assert "## Candidate facts" in ptext
    # The proposal cites the frozen pack's sha — the provenance chain's first link.
    sha = packs[0].stem.split("-")[-2]  # <node>-<source>-<sha>-mining
    assert f"mining_pack_sha: {sha}" in ptext
    assert "mining-pack-sha:" in packs[0].read_text(encoding="utf-8")
    assert "read the mining pack" in out


def test_propose_refuses_duplicate_and_bad_args(run, scratch_runosong):
    assert run("propose", "--into", "Ilmi", "--source", "Design Seed",
               vault=scratch_runosong)[0] == 0
    # Same node + source + day → same proposal path, refused (never clobbered).
    code, _, err = run("propose", "--into", "Ilmi", "--source", "Design Seed",
                       vault=scratch_runosong)
    assert code != 0 and "exist" in err.lower()
    # A card is not a fact-bearing node; a missing source has no ore.
    assert run("propose", "--into", "Episode 1-01", "--source", "Design Seed",
               vault=scratch_runosong)[0] != 0
    assert run("propose", "--into", "Ilmi", "--source", "Nope",
               vault=scratch_runosong)[0] != 0


def test_propose_candidates_ride_the_mine_path(run, scratch_runosong):
    proj = scratch_runosong / "Works" / "Runosong"
    assert run("propose", "--into", "Ilmi", "--source", "Design Seed",
               vault=scratch_runosong)[0] == 0
    prop = next(iter((proj / "control/proposals").glob("*.md")))
    head = prop.read_text(encoding="utf-8").split("## Candidate facts")[0]
    prop.write_text(head + '## Candidate facts\n'
                    '- "Ilmi dug ditches to work songs before any magic"\n'
                    '      confidence: high\n', encoding="utf-8")
    code, out, _ = run("ratify", "--mine", vault=scratch_runosong)
    assert code == 0 and "1 candidate from 1 fact proposal" in out
    inbox = (proj / "control/ratification/Inbox.md").read_text(encoding="utf-8")
    assert '- [ ] "Ilmi dug ditches to work songs before any magic" → [[Ilmi]]' in inbox
    assert "via [[" in inbox and "mining pack" in inbox
    # Status now shows the proposal open and the node with a pending candidate.
    _, sout, _ = run("status", vault=scratch_runosong)
    assert "fact_proposal" in sout and "open" in sout
    assert "candidate pending" in sout


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
        "control/context-packs", "AGENTS.md",
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


def test_init_drops_agent_guidance(run, scratch_root):
    """init drops AGENTS.md at the project root — the house rules any console
    agent opened inside the vault should read (#1089)."""
    run("init", "Sunstolen", "--under", str(scratch_root / "Works"), vault=scratch_root)
    guide = (scratch_root / "Works" / "Sunstolen" / "AGENTS.md").read_text(encoding="utf-8")
    assert "Never ratify" in guide
    assert "Candidates ride the inbox" in guide
    assert "Designated dirs only" in guide
    assert "Cite the pack sha" in guide
    # AGENTS.md is plain guidance, not a fact-bearing note — status ignores it.
    code, out, _ = run("status", "-p", "Sunstolen", vault=scratch_root)
    assert code == 0 and "AGENTS" not in out


def test_init_gamedev_agent_guidance_names_mechanics(run, scratch_root):
    """The gamedev guidance is set-specific: it names mechanic nodes and the
    mechanics review lane the fiction set doesn't have."""
    run("init", "Runosong2", "--set", "gamedev",
        "--under", str(scratch_root / "Works"), vault=scratch_root)
    guide = (scratch_root / "Works" / "Runosong2" / "AGENTS.md").read_text(encoding="utf-8")
    assert "mechanic_node" in guide
    assert "reviews/canon|voice|mechanics|beta/" in guide


# -- doctor -----------------------------------------------------------------

@pytest.fixture
def doctor_env(monkeypatch, tmp_path):
    """Deterministic doctor surroundings: fake HOME (no real dispatch config),
    commands 'installed', no dispatch env pins leaking from the real shell."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr("scribectl.doctor.shutil.which", lambda cmd: f"/fake/bin/{cmd}")
    for var in ("SCRIBE_DISPATCH_RUNNER", "SCRIBE_DISPATCH_MODEL", "SCRIBE_DISPATCH_BASE_URL"):
        monkeypatch.delenv(var, raising=False)
    return home


def test_doctor_healthy_on_fixture(run, fixture_root, doctor_env):
    code, out, _ = run("doctor", vault=fixture_root)
    assert code == 0
    assert "scribectl on PATH" in out and "scribe-dispatch on PATH" in out
    assert "vault root" in out and "$SCRIBECTL_VAULT" in out
    assert 'project "Fertile Flames"' in out
    assert "designated dirs present" in out
    assert "routes to claude" in out          # no dispatch config in fake HOME
    assert "runner claude" in out
    assert "doctor: healthy" in out


def test_doctor_missing_vault_root_fails(run, tmp_path, doctor_env):
    code, out, _ = run("doctor", vault=tmp_path / "nope")
    assert code == 1
    assert "FAIL" in out and "does not exist" in out
    assert "problems found" in out


def test_doctor_reports_openai_route_down_as_warn(run, fixture_root, doctor_env):
    cfg = doctor_env / ".config" / "scribectl"
    cfg.mkdir(parents=True)
    (cfg / "dispatch.yaml").write_text(
        "runner: claude\n"
        "skills:\n"
        "  body_fill:\n"
        "    runner: openai\n"
        "    base_url: http://127.0.0.1:9\n"
        "    model: local-writer\n",
        encoding="utf-8")
    code, out, _ = run("doctor", vault=fixture_root)
    assert code == 0  # a down local writer is a state, not breakage
    assert "runner openai (body_fill)" in out
    assert "down" in out and "vllm-writer" in out
    # reviews still route to claude and group onto one line
    assert "review_canon" in out and "runner claude" in out


def test_doctor_warns_when_commands_off_path(run, fixture_root, doctor_env, monkeypatch):
    monkeypatch.setattr("scribectl.doctor.shutil.which", lambda cmd: None)
    code, out, _ = run("doctor", vault=fixture_root)
    assert code == 1  # claude CLI missing FAILs (default runner unusable)
    assert "scribectl not on PATH" in out and "uv tool install" in out
    assert "claude CLI not on PATH" in out


# -- new card ---------------------------------------------------------------

def test_new_card_scaffolds_card_and_contract(run, scratch_root, scratch_project):
    code, out, _ = run("new", "card", "Scene 07-01", "-p", "Fertile Flames",
                       vault=scratch_root)
    assert code == 0
    card = scratch_project / "structure/scenes/Scene 07-01.md"
    contract = scratch_project / "control/contracts/fill-scene-07-01.md"
    assert card.is_file() and contract.is_file()
    assert "created" in out and "awaiting_scope" in out

    ctext = contract.read_text(encoding="utf-8")
    assert 'target: "[[Scene 07-01]]"' in ctext
    assert "mode: body_fill" in ctext
    assert "contract_id: fill-scene-07-01" in ctext
    assert "output_target: \"/body/drafts/scene-07-01-draft-a.md\"" in ctext
    # The Task/Scope/Output prose is left for the writer — intent stays human.
    assert "## Task" in ctext

    # The card's H1 is its name; the scaffold parks at awaiting_scope.
    assert "# Scene 07-01" in card.read_text(encoding="utf-8")
    code, sout, _ = run("status", "-p", "Fertile Flames", vault=scratch_root)
    assert "Scene 07-01" in sout and "awaiting_scope" in sout


def test_new_card_refuses_to_overwrite(run, scratch_root):
    run("new", "card", "Scene 07-02", "-p", "Fertile Flames", vault=scratch_root)
    code, _, err = run("new", "card", "Scene 07-02", "-p", "Fertile Flames",
                       vault=scratch_root)
    assert code != 0
    assert "overwrite" in err.lower()


def test_new_card_gamedev_uses_output_card_and_cards_dir(run, scratch_runosong):
    code, out, _ = run("new", "card", "Episode 2-01", "-p", "Runosong",
                       vault=scratch_runosong)
    assert code == 0
    proj = scratch_runosong / "Works" / "Runosong"
    card = proj / "structure/cards/Episode 2-01.md"
    assert card.is_file()
    assert "type: output_card" in card.read_text(encoding="utf-8")
    assert (proj / "control/contracts/fill-episode-2-01.md").is_file()


def test_new_card_rejects_slashy_name(run, scratch_root):
    code, _, err = run("new", "card", "bad/name", "-p", "Fertile Flames",
                       vault=scratch_root)
    assert code != 0
    assert "name" in err.lower()


# -- capture ----------------------------------------------------------------

def test_capture_from_file_lands_source_and_registers(run, tmp_path, scratch_root, scratch_project):
    from datetime import date

    transcript = tmp_path / "dialogue.txt"
    transcript.write_text("A: what's the world?\nB: volcanic, terraced.\n", encoding="utf-8")
    note = scratch_project / "Fertile Flames.md"
    body_before = note.read_text(encoding="utf-8").split("\n---\n", 1)[1]

    code, out, err = run("capture", "Ashfall Session", "-p", "Fertile Flames",
                         "--from", str(transcript), vault=scratch_root)
    assert code == 0 and err == ""

    stem = f"{date.today().isoformat()} Ashfall Session"
    src = scratch_project / "sources" / f"{stem}.md"
    assert src.is_file()
    text = src.read_text(encoding="utf-8")
    assert "type: source" in text and "kind: dialogue" in text
    assert "# Ashfall Session" in text
    assert "B: volcanic, terraced." in text          # transcript verbatim

    # Registered under sources:, and the human body is byte-for-byte untouched.
    after = note.read_text(encoding="utf-8")
    assert f'- "[[{stem}]]"' in after
    assert '- "[[Fertile Flames Saga]]"' in after     # prior source kept
    assert after.split("\n---\n", 1)[1] == body_before
    assert f"registered [[{stem}]]" in out

    # The source note is not a project, card, or node — discovery is unchanged.
    code, sout, _ = run("status", "-p", "Fertile Flames", vault=scratch_root)
    assert code == 0 and "source" not in sout


def test_capture_from_stdin(run, monkeypatch, scratch_root, scratch_project):
    import io
    from datetime import date

    monkeypatch.setattr("sys.stdin", io.StringIO("piped ore\n"))
    code, out, _ = run("capture", "Piped Note", "-p", "Fertile Flames", vault=scratch_root)
    assert code == 0
    src = scratch_project / "sources" / f"{date.today().isoformat()} Piped Note.md"
    assert src.is_file() and "piped ore" in src.read_text(encoding="utf-8")
    assert 'origin: "stdin"' in src.read_text(encoding="utf-8")


def test_capture_into_empty_sources_builds_block(run, scratch_root, tmp_path):
    """A freshly init'd project carries `sources: []`; capture converts it to a
    block list without disturbing any other frontmatter key."""
    from datetime import date

    run("init", "Sunstolen", "--under", str(scratch_root / "Works"), vault=scratch_root)
    transcript = tmp_path / "seed.md"
    transcript.write_text("first ore for a new world\n", encoding="utf-8")
    code, _, _ = run("capture", "Origin Chat", "-p", "Sunstolen",
                     "--from", str(transcript), vault=scratch_root)
    assert code == 0
    note = (scratch_root / "Works" / "Sunstolen" / "Sunstolen.md").read_text(encoding="utf-8")
    stem = f"{date.today().isoformat()} Origin Chat"
    assert "sources: []" not in note
    assert f'sources:\n  - "[[{stem}]]"' in note
    # Other keys survive the surgical rewrite.
    assert "type: scribe-project" in note and "pack_output:" in note


def test_capture_refuses_overwrite(run, tmp_path, scratch_root):
    transcript = tmp_path / "t.md"
    transcript.write_text("ore\n", encoding="utf-8")
    assert run("capture", "Dup", "-p", "Fertile Flames",
               "--from", str(transcript), vault=scratch_root)[0] == 0
    code, _, err = run("capture", "Dup", "-p", "Fertile Flames",
                       "--from", str(transcript), vault=scratch_root)
    assert code != 0 and "overwrite" in err.lower()


def test_capture_empty_input_errors(run, tmp_path, scratch_root, scratch_project):
    empty = tmp_path / "empty.md"
    empty.write_text("   \n", encoding="utf-8")
    code, _, err = run("capture", "Nothing", "-p", "Fertile Flames",
                       "--from", str(empty), vault=scratch_root)
    assert code != 0 and "empty" in err.lower()
    assert not (scratch_project / "sources").exists()


def test_capture_rejects_slashy_title(run, tmp_path, scratch_root):
    transcript = tmp_path / "t.md"
    transcript.write_text("ore\n", encoding="utf-8")
    code, _, err = run("capture", "bad/title", "-p", "Fertile Flames",
                       "--from", str(transcript), vault=scratch_root)
    assert code != 0 and "title" in err.lower()


# -- next -------------------------------------------------------------------

def test_next_prints_digest(run, fixture_root):
    code, out, _ = run("next", "-p", "Fertile Flames", vault=fixture_root.parent)
    assert code == 0
    assert "# Next — Fertile Flames" in out
    # The bare fixture: Scene 01-01 blocked on scope.
    assert "blocked: resolve [[Lower Ashmarket]]" in out


def test_next_lists_ready_card_with_contract(run, runosong_root):
    code, out, _ = run("next", "-p", "Runosong", vault=runosong_root.parent)
    assert code == 0
    # The gamedev fixture: one ready card carrying a contract.
    assert "Episode 1-01 — has a contract" in out


def test_next_write_pins_digest_atop_status(run, scratch_root, scratch_project):
    code, out, _ = run("next", "--write", vault=scratch_root)
    assert code == 0
    dash = (scratch_project / "control" / "Status.md").read_text(encoding="utf-8")
    # Digest leads; the derived-state table follows the horizontal rule.
    assert dash.index("# Next —") < dash.index("# Status —")
    assert "| type | name | status | detail |" in dash
    assert "Scene 01-01" in dash


def test_status_write_still_leads_with_digest(run, scratch_root, scratch_project):
    """status --write and next --write produce the same Status.md — the digest
    is pinned atop the table either way, so the two never diverge."""
    run("status", "--write", vault=scratch_root)
    dash = (scratch_project / "control" / "Status.md").read_text(encoding="utf-8")
    assert "# Next —" in dash and "# Status —" in dash
    assert dash.index("# Next —") < dash.index("# Status —")
    # Still a pure cache: the derived rows the console prints are unchanged.
    code, out, _ = run("status", vault=scratch_root)
    assert out == BASELINE_STATUS
