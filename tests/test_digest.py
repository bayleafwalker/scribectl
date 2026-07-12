"""The next-actions digest (#1085): a pure projection like project.py."""
from scribectl.core.digest import build_digest, render_digest
from scribectl.core.vault import Vault
from scribectl.templateset import load_set

FICTION = load_set("fiction")


def _digest(root, inbox="", ledger=""):
    return build_digest(Vault.load(root), FICTION, inbox, ledger)


def test_empty_digest_renders_quiet():
    from scribectl.core.digest import Digest
    d = Digest()
    assert d.empty
    assert "Nothing waiting" in render_digest(d, "Anything")


def test_fixture_surfaces_blocked_card(fixture_root):
    """The bare fixture: Scene 01-01 blocked on scope, nothing else waiting."""
    d = _digest(fixture_root)
    assert ("Scene 01-01", "[[Lower Ashmarket]]") in d.blocked
    text = render_digest(d, "Fertile Flames")
    assert "Scene 01-01 — blocked: resolve [[Lower Ashmarket]]" in text


def test_unmined_review_report_shows_mine_action(scratch_project):
    """A landed review report with introduced candidates, not yet queued into
    the inbox, is a `ratify --mine` action."""
    (scratch_project / "reviews/canon/ch01-sc01-draft-a — canon review.md").write_text(
        "---\ntype: review_report\nkind: canon\n"
        'target: "[[Scene 01-01]]"\ndraft: "[[ch01-sc01-draft-a]]"\n'
        "verdict: clean\npack_sha: abc123abc123\n---\n\n"
        "## Introduced candidates seen in draft\n"
        '- "The ash-census is quarterly" → [[The Mist]]\n', encoding="utf-8")
    d = _digest(scratch_project)
    assert d.unmined_reports == 1 and d.unmined_candidates == 1
    assert "ratify --mine" in render_digest(d, "Fertile Flames")


def test_ready_card_split_by_contract(scratch_project):
    """A ready card with a body_fill contract is dispatchable; one without
    needs a contract — the digest says which."""
    (scratch_project / "world/canon/Lower Ashmarket.md").write_text(
        "---\ntype: canon_node\n---\n\n# Lower Ashmarket\n\n## Ratified facts\n"
        "- Below the terrace line.\n", encoding="utf-8")
    # A second ready card with NO contract.
    (scratch_project / "structure/scenes/Scene 02-02.md").write_text(
        "---\ntype: scene_card\nbook: 1\nchapter: 2\nscene: 2\n"
        'pov: "[[Mara Vey]]"\nlocation: "[[The Volcanic City-State]]"\n'
        'characters:\n  - "[[Mara Vey]]"\ncanon_scope:\n  - "[[The Mist]]"\n'
        "mode: body_fill\ntarget_words: 1000\n---\n\n# Scene 2.2\n", encoding="utf-8")
    d = _digest(scratch_project)
    assert "Scene 01-01" in d.ready            # the fixture contract targets it
    assert "Scene 02-02" in d.ready_no_contract
    text = render_digest(d, "Fertile Flames")
    assert "Scene 01-01 — has a contract" in text
    assert "Scene 02-02 — ready but no body_fill contract" in text


def test_awaiting_scope_scaffold_is_author_action(scratch_project):
    (scratch_project / "structure/scenes/Scene 09-09.md").write_text(
        "---\ntype: scene_card\nbook: 0\nchapter: 0\nscene: 0\n"
        'pov: "[[ ]]"\nlocation: "[[ ]]"\n'
        'characters:\n  - "[[ ]]"\ncanon_scope:\n  - "[[ ]]"\n'
        "mode: body_fill\ntarget_words: 1000\n---\n\n# Scene 9.9\n", encoding="utf-8")
    d = _digest(scratch_project)
    assert "Scene 09-09" in d.awaiting_scope
    assert "fill or remove the `[[ ]]` scope placeholders" in render_digest(d, "x")


def test_rework_lists_issues_review_on_newest_draft(scratch_project):
    (scratch_project / "body/drafts/ch01-sc01-draft-a.md").write_text(
        '---\ntype: draft\ncard: "[[Scene 01-01]]"\n---\n\nProse.\n', encoding="utf-8")
    (scratch_project / "reviews/voice/ch01-sc01-draft-a — voice review.md").write_text(
        "---\ntype: review_report\nkind: voice\n"
        'target: "[[Scene 01-01]]"\ndraft: "[[ch01-sc01-draft-a]]"\n'
        "verdict: issues\n---\n\n## Findings\n- personification\n", encoding="utf-8")
    d = _digest(scratch_project)
    assert ("Scene 01-01", "voice", "ch01-sc01-draft-a") in d.rework


def test_clean_review_is_not_rework(scratch_project):
    (scratch_project / "body/drafts/ch01-sc01-draft-a.md").write_text(
        '---\ntype: draft\ncard: "[[Scene 01-01]]"\n---\n\nProse.\n', encoding="utf-8")
    (scratch_project / "reviews/canon/ch01-sc01-draft-a — canon review.md").write_text(
        "---\ntype: review_report\nkind: canon\n"
        'target: "[[Scene 01-01]]"\ndraft: "[[ch01-sc01-draft-a]]"\n'
        "verdict: clean\n---\n\n## Findings\n- none\n", encoding="utf-8")
    assert _digest(scratch_project).rework == []


def test_inbox_pending_and_unrouted_counts():
    inbox = (
        "---\ntype: ratification_inbox\n---\n\n# Inbox\n\n"
        '- [ ] "routed fact" → [[The Mist]]\n      (from [[d]])\n'
        '- [ ] "unrouted fact"\n      (from [[d]])\n'
        '- [x] "already decided" → [[The Mist]]\n      (from [[d]])\n'
    )
    # No vault needed for the inbox math; use an empty fixture read.
    from scribectl.core.digest import Digest
    from scribectl.core.inbox import parse_inbox
    candidates, problems = parse_inbox(inbox)
    pending = sum(1 for c in candidates if c.verdict == "pending")
    unrouted = sum(1 for _, m in problems if "target" in m)
    assert pending == 1 and unrouted == 1
