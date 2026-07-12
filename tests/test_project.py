"""Derived-state projection: status is a function of the vault, never stored."""
from pathlib import Path

from scribectl.core.project import project
from scribectl.core.vault import Vault
from scribectl.templateset import load_set

FICTION = load_set("fiction")


def rows_dict(vault_path):
    return {name: status for _, name, status, _ in project(Vault.load(vault_path), FICTION)}


def test_fixture_baseline_states(fixture_root):
    assert rows_dict(fixture_root) == {
        "Mara Vey": "seeded",
        "The Mist": "ratified",
        "The Volcanic City-State": "seeded",
        "Scene 01-01": "blocked_unresolved_scope",
    }


def test_scene_unblocks_when_scope_resolves(scratch_project):
    (scratch_project / "world/canon/Lower Ashmarket.md").write_text(
        "---\ntype: canon_node\n---\n\n# Lower Ashmarket\n\n"
        "## One-line function\nThe crowded market district.\n\n"
        "## Ratified facts\n- Sits below the ash line.\n",
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["Scene 01-01"] == "ready_for_fill"
    assert rows_dict(scratch_project)["Lower Ashmarket"] == "seeded"


def test_scene_with_draft_then_review(scratch_project):
    (scratch_project / "body/drafts/Scene 01-01 draft v1.md").write_text(
        "---\ntype: draft\nscene: \"[[Scene 01-01]]\"\n---\n\nProse here.\n",
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["Scene 01-01"] == "has_draft"

    (scratch_project / "reviews/canon/Scene 01-01 canon review.md").write_text(
        "---\ntype: review_report\nkind: canon\ntarget: \"[[Scene 01-01]]\"\n"
        "verdict: clean\n---\n\n# canon review\n",
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["Scene 01-01"] == "reviewed"


def test_ratification_promotes_canon_node(scratch_project):
    log = scratch_project / "control/ratification/Ratification Log.md"
    log.write_text(
        log.read_text(encoding="utf-8")
        + "\n## 2026-07-10\n\n### Accepted\n"
        '- "ash-line ledgers" → promoted to [[The Volcanic City-State]] — test.\n',
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["The Volcanic City-State"] == "ratified"


def test_ledger_accept_without_facts_reads_ratified_empty(scratch_project):
    """The two halves of ratification diverging (receipt without paste) is surfaced."""
    (scratch_project / "world/canon/Gate-Warden Guild.md").write_text(
        "---\ntype: canon_node\n---\n\n# Gate-Warden Guild\n\n"
        "## Ratified facts\n_(none ratified yet — node is a stub)_\n",
        encoding="utf-8",
    )
    log = scratch_project / "control/ratification/Ratification Log.md"
    log.write_text(
        log.read_text(encoding="utf-8")
        + "\n## 2026-07-10\n\n### Accepted\n"
        '- "wardens keep the seals" → promoted to [[Gate-Warden Guild]] — test.\n',
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["Gate-Warden Guild"] == "ratified_empty"


def test_blocked_scene_detail_names_missing_links(scratch_project):
    rows = {name: detail for _, name, _, detail in project(Vault.load(scratch_project), FICTION)}
    assert rows["Scene 01-01"] == "missing: [[Lower Ashmarket]]"


def test_blank_placeholder_links_do_not_block(scratch_project):
    """`[[ ]]` template placeholders are not scope links."""
    card = scratch_project / "structure/scenes/Scene 01-02.md"
    card.write_text(
        "---\ntype: scene_card\nbook: 1\nchapter: 1\nscene: 2\n"
        'pov: "[[Mara Vey]]"\nlocation: "[[ ]]"\n'
        'characters:\n  - "[[Mara Vey]]"\ncanon_scope:\n  - "[[The Mist]]"\n---\n\n'
        "# Scene 1.2\n\n## Entry state\nx\n",
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["Scene 01-02"] == "ready_for_fill"


def test_pristine_scaffold_is_awaiting_scope(scratch_project):
    """A `new card` scaffold — every scope field a blank placeholder — must
    NOT derive ready_for_fill, or ambient watch would fill an empty card."""
    card = scratch_project / "structure/scenes/Scene 09-09.md"
    card.write_text(
        "---\ntype: scene_card\nbook: 0\nchapter: 0\nscene: 0\n"
        'pov: "[[ ]]"\nlocation: "[[ ]]"\n'
        'characters:\n  - "[[ ]]"\ncanon_scope:\n  - "[[ ]]"\n'
        "mode: body_fill\ntarget_words: 1000\n---\n\n"
        "# Scene 9.9\n\n## Entry state\n<Where things stand.>\n",
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["Scene 09-09"] == "awaiting_scope"


def test_one_real_scope_link_leaves_awaiting_scope(scratch_project):
    """The first authored scope link means the card is being written; a blank
    placeholder still sitting in another field is back to 'no link here'."""
    card = scratch_project / "structure/scenes/Scene 09-10.md"
    card.write_text(
        "---\ntype: scene_card\nbook: 1\nchapter: 9\nscene: 10\n"
        'pov: "[[ ]]"\nlocation: "[[ ]]"\n'
        'characters:\n  - "[[ ]]"\ncanon_scope:\n  - "[[The Mist]]"\n'
        "mode: body_fill\ntarget_words: 1000\n---\n\n# Scene 9.10\n",
        encoding="utf-8",
    )
    # The Mist resolves; every other scope field is a blank placeholder →
    # authored, not a scaffold, and nothing unresolved → ready_for_fill.
    assert rows_dict(scratch_project)["Scene 09-10"] == "ready_for_fill"


def test_rejected_section_does_not_promote(scratch_project):
    log = scratch_project / "control/ratification/Ratification Log.md"
    log.write_text(
        log.read_text(encoding="utf-8")
        + "\n## 2026-07-10\n\n### Rejected\n"
        '- "royal bloodline" (source draft) → would touch [[Mara Vey]] — conflicts.\n',
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["Mara Vey"] == "seeded"
