"""Derived-state projection: status is a function of the vault, never stored."""
from pathlib import Path

from scribectl.core.project import project
from scribectl.core.vault import Vault


def rows_dict(vault_path):
    return {name: status for _, name, status in project(Vault.load(vault_path))}


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


def test_rejected_section_does_not_promote(scratch_project):
    log = scratch_project / "control/ratification/Ratification Log.md"
    log.write_text(
        log.read_text(encoding="utf-8")
        + "\n## 2026-07-10\n\n### Rejected\n"
        '- "royal bloodline" (source draft) → would touch [[Mara Vey]] — conflicts.\n',
        encoding="utf-8",
    )
    assert rows_dict(scratch_project)["Mara Vey"] == "seeded"
