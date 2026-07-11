"""Project discovery: scribe-project notes are both config and registry."""
from pathlib import Path

import pytest

from scribectl.config import ProjectConfig, discover_projects, vault_roots


def test_fixture_note_is_the_config_spec(fixture_root):
    cfg = ProjectConfig.from_note(fixture_root / "Fertile Flames.md")
    assert cfg.name == "Fertile Flames"
    assert cfg.template_set == "fiction"
    assert cfg.root == fixture_root
    # All paths resolve relative to the note's directory.
    assert cfg.roots["world"] == fixture_root / "world"
    assert cfg.voice_canon == fixture_root / "world/language/Prose Voice Canon.md"
    assert cfg.timeline == fixture_root / "control/timeline/Timeline.md"
    assert cfg.ratification_log == fixture_root / "control/ratification/Ratification Log.md"
    assert cfg.pack_output == fixture_root / "control/context-packs"
    assert cfg.sources == ["[[Fertile Flames Saga]]"]
    for p in [cfg.voice_canon, cfg.timeline, cfg.ratification_log, cfg.pack_output]:
        assert p.exists(), p


def test_discover_finds_projects_under_a_root(fixture_root):
    projects = discover_projects([fixture_root.parent])
    assert [p.name for p in projects] == ["Fertile Flames", "Runosong"]
    assert [p.template_set for p in projects] == ["fiction", "gamedev"]


def test_discover_multiple_projects_sorted(scratch_root):
    other = scratch_root / "Works" / "Sunstolen"
    other.mkdir(parents=True)
    (other / "Sunstolen.md").write_text(
        "---\ntype: scribe-project\nname: Sunstolen\ntemplate_set: fiction\n---\n",
        encoding="utf-8",
    )
    projects = discover_projects([scratch_root])
    assert [p.name for p in projects] == ["Fertile Flames", "Sunstolen"]


def test_discover_ignores_non_project_notes(scratch_root):
    (scratch_root / "Random Note.md").write_text("---\ntype: essay\n---\nhi\n", encoding="utf-8")
    projects = discover_projects([scratch_root])
    assert [p.name for p in projects] == ["Fertile Flames"]


def test_non_project_note_rejected_by_from_note(fixture_root):
    with pytest.raises(ValueError):
        ProjectConfig.from_note(fixture_root / "world" / "World Seed.md")


def test_config_defaults_fill_missing_fields(tmp_path):
    note = tmp_path / "Bare.md"
    note.write_text("---\ntype: scribe-project\nname: Bare\n---\n", encoding="utf-8")
    cfg = ProjectConfig.from_note(note)
    assert cfg.template_set == "fiction"
    assert cfg.roots["world"] == tmp_path / "world"
    assert cfg.pack_output == tmp_path / "control/context-packs"
    assert cfg.sources == []


def test_vault_roots_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("SCRIBECTL_VAULT", str(tmp_path))
    assert vault_roots() == [tmp_path]


def test_vault_roots_env_multiple(monkeypatch, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    monkeypatch.setenv("SCRIBECTL_VAULT", f"{a}:{b}")
    assert vault_roots() == [a, b]


def test_vault_roots_default(monkeypatch):
    monkeypatch.delenv("SCRIBECTL_VAULT", raising=False)
    monkeypatch.setenv("HOME", "/nonexistent-home")
    assert vault_roots() == [Path("/media/Creative")]
