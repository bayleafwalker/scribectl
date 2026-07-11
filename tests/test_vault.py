"""Contact tests for the vault parsing layer against the fertile-flames fixture."""
from pathlib import Path

from scribectl.core.vault import Note, Vault, _parse


def test_frontmatter_parsed(vault):
    card = vault.resolve("Scene 01-01")
    assert card.type == "scene_card"
    assert card.meta["book"] == 1
    assert card.meta["pov"] == "[[Mara Vey]]"


def test_note_without_frontmatter(tmp_path):
    p = tmp_path / "Plain.md"
    p.write_text("just prose, no fence\n", encoding="utf-8")
    n = _parse(p)
    assert n.meta == {}
    assert n.type == "untyped"
    assert n.body.startswith("just prose")


def test_section_extraction_case_insensitive(vault):
    card = vault.resolve("Scene 01-01")
    assert "Mist alarm" in card.section("required beats")
    assert card.section("No Such Section") is None


def test_section_titles(vault):
    card = vault.resolve("Scene 01-01")
    assert card.section_titles() == [
        "Entry state", "Required beats", "Exit state", "Tone target", "Do not",
    ]


def test_links_from_frontmatter_field(vault):
    card = vault.resolve("Scene 01-01")
    assert card.links("canon_scope") == [
        "The Volcanic City-State", "The Mist", "Lower Ashmarket",
    ]
    assert card.links("characters") == ["Mara Vey"]


def test_links_whole_note_includes_meta_and_body(vault):
    mist = vault.resolve("The Mist")
    assert "The Volcanic City-State" in mist.links()


def test_links_alias_form(tmp_path):
    p = tmp_path / "Aliased.md"
    p.write_text("See [[Real Target|the display text]].\n", encoding="utf-8")
    assert _parse(p).links() == ["Real Target"]


def test_blank_placeholder_links_ignored(tmp_path):
    p = tmp_path / "Templated.md"
    p.write_text('---\npov: "[[ ]]"\n---\n\nBody with [[ ]] and [[Real]].\n', encoding="utf-8")
    n = _parse(p)
    assert n.links() == ["Real"]
    assert n.links("pov") == []


def test_by_type_and_one(vault):
    assert {n.name for n in vault.by_type("canon_node")} == {
        "Mara Vey", "The Mist", "The Volcanic City-State",
    }
    assert vault.one("world_seed").name == "World Seed"
    assert vault.one("no_such_type") is None


def test_resolve_missing_link(vault):
    assert vault.resolve("Lower Ashmarket") is None
