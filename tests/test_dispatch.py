"""Contact tests for the automatic agentic mode (docs/DISPATCH.md).

Fake runner, disposable fixture copy, zero network. Write discipline under
test throughout: dispatch lands NEW files in designated dirs only, stamps
pack-sha receipts, refuses overwrites, and a completed loop dispatches
nothing on the next pass.
"""
import hashlib
from pathlib import Path

import pytest

from scribedispatch.cli import main
from scribedispatch.landing import parse_verdict
from scribedispatch.vaultio import verify_pack
from scribedispatch import DispatchError

FILL_RESPONSE = """\
# A Routine That Lies

The queue for the ash-census had wrapped twice around the Lower Ashmarket
by the time the sirens tested themselves.

## Introduced candidates
- "The ash-census is conducted quarterly" — new civic procedure

## Uncertainties
- none
"""

CANON_RESPONSE = """\
verdict: clean

## Findings
- none

## Introduced candidates seen in draft
- "The ash-census is conducted quarterly" — appears in neither timeline nor pack
"""

VOICE_RESPONSE = """\
verdict: issues

## Findings
- "sirens tested themselves" — personification the voice canon forbids

## Strongest passage
- "wrapped twice around the Lower Ashmarket" — concrete, civic, unhurried.
"""

MECHANICS_RESPONSE = """\
verdict: issues

## Findings
- "she counts to four and the meadow answers" — Polymetric Difficulty rules
  the world pulse is 5/4

## Introduced candidates seen in draft
- "Resting the empty beats is itself part of the cast" → [[Freeform Casting Evaluation]]
"""


@pytest.fixture
def fakes(tmp_path) -> Path:
    d = tmp_path / "fake-responses"
    d.mkdir()
    (d / "body_fill.md").write_text(FILL_RESPONSE, encoding="utf-8")
    (d / "review_canon.md").write_text(CANON_RESPONSE, encoding="utf-8")
    (d / "review_voice.md").write_text(VOICE_RESPONSE, encoding="utf-8")
    (d / "review_mechanics.md").write_text(MECHANICS_RESPONSE, encoding="utf-8")
    return d


@pytest.fixture
def run(monkeypatch, capsys, scratch_root, fakes):
    monkeypatch.setenv("SCRIBECTL_VAULT", str(scratch_root))
    monkeypatch.setenv("SCRIBE_DISPATCH_FAKE_DIR", str(fakes))

    def _run(*argv):
        code = main([*argv, "--runner", "fake"])
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run


def unblock(project: Path) -> None:
    (project / "world/canon/Lower Ashmarket.md").write_text(
        "---\ntype: canon_node\n---\n\n# Lower Ashmarket\n\n## Ratified facts\n"
        "- The Ashmarket sits below the terrace line.\n", encoding="utf-8")


def snapshot(project: Path, exclude: tuple[str, ...]) -> dict[str, str]:
    return {str(p.relative_to(project)): hashlib.md5(p.read_bytes()).hexdigest()
            for p in project.rglob("*") if p.is_file()
            and not any(str(p.relative_to(project)).startswith(e) for e in exclude)}


def test_blocked_card_dispatches_nothing(run):
    code, out, _ = run("plan")
    assert code == 0
    assert "blocked" in out and "nothing to dispatch" in out


def test_full_loop_fill_then_reviews_then_quiet(run, scratch_project):
    unblock(scratch_project)
    before = snapshot(scratch_project,
                      exclude=("body/drafts", "reviews", "control/context-packs"))

    code, out, _ = run("plan")
    assert code == 0 and "would dispatch body_fill for Scene 01-01" in out

    code, out, _ = run("run")
    assert code == 0

    # The draft landed at the contract's output_target with the sha receipt.
    draft = scratch_project / "body/drafts/ch01-sc01-draft-a.md"
    text = draft.read_text(encoding="utf-8")
    assert "type: draft" in text and 'card: "[[Scene 01-01]]"' in text
    packs = list((scratch_project / "control/context-packs").glob("*-context.md"))
    assert len(packs) == 1
    sha = verify_pack(packs[0])
    assert f"pack_sha: {sha}" in text
    assert "ash-census" in text

    # Reviews fired in the same run, one per lane, verdicts parsed.
    canon = scratch_project / "reviews/canon/ch01-sc01-draft-a — canon review.md"
    voice = scratch_project / "reviews/voice/ch01-sc01-draft-a — voice review.md"
    assert "verdict: clean" in canon.read_text(encoding="utf-8")
    assert "verdict: issues" in voice.read_text(encoding="utf-8")
    assert f"pack_sha: {sha}" in canon.read_text(encoding="utf-8")

    # A completed loop goes quiet: idempotent second pass.
    code, out, _ = run("run")
    assert code == 0
    assert "nothing to dispatch" in out and "fully reviewed" in out

    # Nothing outside the designated dirs moved.
    after = snapshot(scratch_project,
                     exclude=("body/drafts", "reviews", "control/context-packs"))
    assert after == before


def test_ready_card_without_contract_is_skipped(run, scratch_project):
    unblock(scratch_project)
    (scratch_project / "control/contracts/fill-scene-01-01.md").unlink()
    code, out, _ = run("run")
    assert code == 0
    assert "no body_fill contract" in out and "nothing to dispatch" in out
    assert not any((scratch_project / "body/drafts").glob("*.md"))


def test_scaffolded_card_awaiting_scope_dispatches_nothing(run, scratch_project):
    """A `new card` scaffold (all scope fields blank placeholders) must be
    skipped, not filled — the whole point of the awaiting_scope guard."""
    (scratch_project / "structure/scenes/Scene 08-01.md").write_text(
        "---\ntype: scene_card\nbook: 0\nchapter: 0\nscene: 0\n"
        'pov: "[[ ]]"\nlocation: "[[ ]]"\n'
        'characters:\n  - "[[ ]]"\ncanon_scope:\n  - "[[ ]]"\n'
        "mode: body_fill\ntarget_words: 1000\n---\n\n# Scene 8.1\n",
        encoding="utf-8")
    (scratch_project / "control/contracts/fill-scene-08-01.md").write_text(
        "---\ntype: contract\ncontract_id: fill-scene-08-01\n"
        'target: "[[Scene 08-01]]"\nmode: body_fill\n---\n\n# Contract\n',
        encoding="utf-8")
    code, out, _ = run("plan", "--card", "Scene 08-01")
    assert code == 0
    assert "scaffolded but unauthored" in out
    assert "would dispatch" not in out
    code, out, _ = run("run", "--card", "Scene 08-01")
    assert code == 0
    assert not any((scratch_project / "body/drafts").glob("*.md"))


def test_manual_draft_still_gets_reviews(run, scratch_project):
    """Reviews fire on drafts, not on paperwork — a hand-landed draft with no
    pack receipt is reviewed against the oracle alone."""
    unblock(scratch_project)
    (scratch_project / "body/drafts/hand-draft.md").write_text(
        "---\ntype: draft\nscene: \"[[Scene 01-01]]\"\n---\n\nHand-written prose.\n",
        encoding="utf-8")
    code, out, _ = run("run")
    assert code == 0
    assert (scratch_project / "reviews/canon/hand-draft — canon review.md").is_file()
    assert (scratch_project / "reviews/voice/hand-draft — voice review.md").is_file()
    # No fill fired: the card already has a draft.
    assert not (scratch_project / "body/drafts/ch01-sc01-draft-a.md").exists()


def test_refuses_to_overwrite_existing_draft(run, scratch_project):
    """If the contract's output_target already exists but doesn't link the
    card (say, a stray file), landing refuses rather than clobbers."""
    unblock(scratch_project)
    target = scratch_project / "body/drafts/ch01-sc01-draft-a.md"
    target.write_text("a human wrote this\n", encoding="utf-8")
    code, _, err = run("run")
    assert code == 2
    assert "refusing to overwrite" in err
    assert target.read_text(encoding="utf-8") == "a human wrote this\n"


def test_verdict_defaults_to_issues(fakes):
    verdict, rest = parse_verdict("no verdict line here\n\n## Findings\n- none\n")
    assert verdict == "issues"
    assert "no verdict line here" in rest


def test_watch_single_tick_runs_full_pass(run, scratch_project):
    """`watch --ticks 1` is the timer/cron shape: one debounced pass."""
    unblock(scratch_project)
    code, out, _ = run("watch", "--ticks", "1", "--settle", "0")
    assert code == 0
    assert (scratch_project / "body/drafts/ch01-sc01-draft-a.md").is_file()
    assert (scratch_project / "reviews/canon/ch01-sc01-draft-a — canon review.md").is_file()
    assert (scratch_project / "reviews/voice/ch01-sc01-draft-a — voice review.md").is_file()


def test_watch_debounces_livesync_bursts(run, scratch_project):
    """A vault that changed inside the settle window never dispatches — a
    half-synced note is not derived state."""
    unblock(scratch_project)  # fresh write: the vault is mid-burst by definition
    code, out, _ = run("watch", "--ticks", "1", "--settle", "3600")
    assert code == 0
    assert "waiting for livesync" in out
    assert not any((scratch_project / "body/drafts").glob("*.md"))


def test_watch_second_tick_goes_quiet(run, scratch_project):
    """Tick 2 re-plans against the completed loop and dispatches nothing —
    watching adds repetition, never iteration."""
    unblock(scratch_project)
    code, out, _ = run("watch", "--ticks", "2", "--interval", "0", "--settle", "0")
    assert code == 0
    assert len(list((scratch_project / "body/drafts").glob("*.md"))) == 1
    assert out.count("dispatching body_fill") == 1


def test_tampered_pack_fails_verification(run, scratch_project, tmp_path):
    unblock(scratch_project)
    code, _, _ = run("run")
    assert code == 0
    pack = next((scratch_project / "control/context-packs").glob("*-context.md"))
    pack.write_text(pack.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
    with pytest.raises(DispatchError, match="does not match its pack-sha"):
        verify_pack(pack)


# -- gamedev set: kind-parameterized cards + the mechanics lane ---------------

@pytest.fixture
def run_gamedev(monkeypatch, capsys, scratch_runosong, fakes):
    monkeypatch.setenv("SCRIBECTL_VAULT", str(scratch_runosong))
    monkeypatch.setenv("SCRIBE_DISPATCH_FAKE_DIR", str(fakes))

    def _run(*argv):
        code = main([*argv, "--runner", "fake"])
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return _run


def test_gamedev_full_loop_fills_kind_and_fires_mechanics(run_gamedev, scratch_runosong):
    project = scratch_runosong / "Works" / "Runosong"

    code, out, _ = run_gamedev("plan")
    assert code == 0
    # The spoken_fic card fills; the blog card is blocked on unresolved scope.
    assert "would dispatch body_fill for Episode 1-01" in out
    assert "Why Our World Beats in Five: blocked" in out

    code, out, _ = run_gamedev("run")
    assert code == 0
    draft = project / "body/drafts/ep01-01-draft-a.md"
    assert 'card: "[[Episode 1-01]]"' in draft.read_text(encoding="utf-8")

    # All three gamedev lanes fired on the landed draft.
    for kind in ("canon", "voice", "mechanics"):
        report = project / f"reviews/{kind}/ep01-01-draft-a — {kind} review.md"
        assert report.is_file(), kind
    mech = (project / "reviews/mechanics/ep01-01-draft-a — mechanics review.md").read_text(encoding="utf-8")
    assert "verdict: issues" in mech and "kind: mechanics" in mech
    assert "Polymetric Difficulty" in mech

    code, out, _ = run_gamedev("run")
    assert code == 0
    assert "nothing to dispatch" in out and "fully reviewed" in out


def test_gamedev_hand_draft_gets_mechanics_lane_by_default(run_gamedev, scratch_runosong):
    """No contract, hand-landed draft: the gamedev set's default lanes still
    include mechanics — a fic where magic works differently than the game is
    canon rot in both directions."""
    project = scratch_runosong / "Works" / "Runosong"
    (project / "control/contracts/fill-episode-1-01.md").unlink()
    (project / "body/drafts/hand-episode.md").write_text(
        '---\ntype: draft\ncard: "[[Episode 1-01]]"\n---\n\nHand-written episode.\n',
        encoding="utf-8")
    code, _, _ = run_gamedev("run")
    assert code == 0
    for kind in ("canon", "voice", "mechanics"):
        assert (project / f"reviews/{kind}/hand-episode — {kind} review.md").is_file(), kind


def test_skip_unreachable_skips_fill_but_reviews_still_fire(monkeypatch, capsys,
                                                           scratch_root, scratch_project, fakes):
    """--skip-unreachable is the systemd-timer policy (item 1091): a down local
    writer skips the fills routed to it — no crash — while reviews on the
    frontier still land. A stopped writer is a state, not breakage."""
    from scribedispatch import cli, runner as runner_mod

    monkeypatch.setenv("SCRIBECTL_VAULT", str(scratch_root))
    monkeypatch.setenv("SCRIBE_DISPATCH_FAKE_DIR", str(fakes))
    monkeypatch.setattr(cli, "_config", lambda: {
        "runner": "claude",
        "skills": {"body_fill": {"runner": "openai",
                                 "base_url": "http://127.0.0.1:8080",
                                 "model": "local-writer"}}})

    class DownWriter(runner_mod.FakeRunner):
        name = "openai"
        def reachable(self):
            return False

    def routed(name, model=None, base_url=None, fake_dir=None):
        cls = DownWriter if name == "openai" else runner_mod.FakeRunner
        return cls(fake_dir or str(fakes))

    monkeypatch.setattr(cli, "make_runner", routed)
    unblock(scratch_project)  # Scene 01-01 -> ready_for_fill (fill routes to the down writer)

    # A second card that already has a hand-draft, so a review lane has
    # something to fire on in the same pass the fill is skipped.
    (scratch_project / "structure/scenes/Scene 01-02.md").write_text(
        "---\ntype: scene_card\nbook: 1\nchapter: 1\nscene: 2\n"
        'pov: "[[Mara Vey]]"\nlocation: "[[The Volcanic City-State]]"\n'
        'characters:\n  - "[[Mara Vey]]"\ncanon_scope:\n  - "[[The Mist]]"\n'
        "mode: body_fill\ntarget_words: 1000\n---\n\n# Scene 1.2\n", encoding="utf-8")
    (scratch_project / "body/drafts/Scene 01-02 hand.md").write_text(
        "---\ntype: draft\nscene: \"[[Scene 01-02]]\"\n---\n\nHand prose.\n", encoding="utf-8")

    code = cli.main(["run", "--skip-unreachable"])
    out = capsys.readouterr().out
    assert code == 0
    assert "skipping body_fill for Scene 01-01" in out and "unreachable" in out
    assert not (scratch_project / "body/drafts/ch01-sc01-draft-a.md").exists()
    # Reviews (fake, reachable) fired on the hand-draft despite the down writer.
    assert (scratch_project / "reviews/canon/Scene 01-02 hand — canon review.md").is_file()
    assert (scratch_project / "reviews/voice/Scene 01-02 hand — voice review.md").is_file()


def test_down_writer_without_skip_flag_crashes_loudly(monkeypatch, capsys,
                                                      scratch_root, scratch_project, fakes):
    """Without --skip-unreachable the pass fails loudly on a real generate
    error — a dead watch is visible; the flag is what makes it degrade."""
    from scribedispatch import cli, runner as runner_mod

    monkeypatch.setenv("SCRIBECTL_VAULT", str(scratch_root))
    monkeypatch.setenv("SCRIBE_DISPATCH_FAKE_DIR", str(fakes))
    monkeypatch.setattr(cli, "_config", lambda: {"runner": "claude"})

    class DeadRunner(runner_mod.FakeRunner):
        name = "openai"
        def reachable(self):
            return False
        def generate(self, skill, prompt):
            from scribedispatch import DispatchError
            raise DispatchError("endpoint refused connection")

    monkeypatch.setattr(cli, "make_runner",
                        lambda *a, **k: DeadRunner(k.get("fake_dir") or str(fakes)))
    unblock(scratch_project)
    code = cli.main(["run"])  # no --skip-unreachable
    assert code == 2


def test_per_skill_routing_splits_fill_and_reviews(monkeypatch, capsys,
                                                   scratch_root, scratch_project, fakes):
    """dispatch.yaml `skills:` map (backlog item 1076): fills route to the
    local writer, reviews fall back to the frontier default — and an explicit
    --runner still pins one backend for the whole pass."""
    from scribedispatch import cli, runner as runner_mod

    monkeypatch.setenv("SCRIBECTL_VAULT", str(scratch_root))
    monkeypatch.setenv("SCRIBE_DISPATCH_FAKE_DIR", str(fakes))
    monkeypatch.setattr(cli, "_config", lambda: {
        "runner": "claude",
        "skills": {"body_fill": {"runner": "openai",
                                 "base_url": "http://127.0.0.1:8080",
                                 "model": "local-writer"}}})
    made = []

    def recording(name, model=None, base_url=None, fake_dir=None):
        made.append((name, model, base_url))
        return runner_mod.FakeRunner(fake_dir or str(fakes))

    monkeypatch.setattr(cli, "make_runner", recording)
    unblock(scratch_project)

    code = cli.main(["plan"])
    out = capsys.readouterr().out
    assert code == 0
    assert "would dispatch body_fill for Scene 01-01 [openai:local-writer]" in out

    # Explicit --runner overrides the map: one backend for the whole pass.
    code = cli.main(["plan", "--runner", "fake"])
    out = capsys.readouterr().out
    assert code == 0
    assert "would dispatch body_fill for Scene 01-01 [fake]" in out

    code = cli.main(["run"])
    out = capsys.readouterr().out
    assert code == 0
    assert ("openai", "local-writer", "http://127.0.0.1:8080") in made
    assert ("claude", None, None) in made  # reviews fell back to the default
    assert (scratch_project / "body/drafts/ch01-sc01-draft-a.md").is_file()
