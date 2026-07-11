"""Template sets: the pluggable shape of a project.

A template set is a directory under scribectl/templates/ holding artifact
contracts (markdown) plus one `set.yaml` manifest declaring the shape the
engine needs to know: which note type is "the card" (the fillable unit),
which node types carry ratified facts, which frontmatter fields the
assembler pulls, and what `init` instantiates. Sets are data plus this
small registration — never subclasses (ARCHITECTURE.md, "Template sets").

core/ never reads this module; the CLI resolves a project's set and passes
the shape into the assembler and the status projection as plain parameters.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

TEMPLATES = Path(__file__).parent / "templates"
MANIFEST = "set.yaml"


@dataclass(frozen=True)
class TemplateSet:
    name: str
    card_type: str                    # the fillable unit: scene_card, output_card
    card_heading: str                 # pack section heading for the card body
    node_types: tuple[str, ...]       # fact-bearing nodes the assembler briefs
    scope_fields: tuple[str, ...]     # link fields resolved into canon-in-scope
    actor_fields: tuple[str, ...]     # link fields contributing timeline actors
    location_field: str | None
    position_fields: tuple[str, ...]  # frontmatter ints ordering the card;
                                      # a card carrying none sees the whole timeline
    init_dirs: tuple[str, ...]
    init_files: dict[str, str]        # template file in the set → project-relative dest

    @property
    def dir(self) -> Path:
        return TEMPLATES / self.name


def list_sets() -> list[str]:
    return sorted(p.name for p in TEMPLATES.iterdir()
                  if p.is_dir() and (p / MANIFEST).is_file())


def load_set(name: str) -> TemplateSet:
    path = TEMPLATES / name / MANIFEST
    if not path.is_file():
        raise ValueError(
            f"unknown template set {name!r} (available: {', '.join(list_sets()) or 'none'})")
    m = yaml.safe_load(path.read_text(encoding="utf-8"))
    pull = m.get("pull", {})
    return TemplateSet(
        name=name,
        card_type=m["card_type"],
        card_heading=m["card_heading"],
        node_types=tuple(m.get("node_types", ["canon_node"])),
        scope_fields=tuple(pull.get("scope", [])),
        actor_fields=tuple(pull.get("actors", [])),
        location_field=pull.get("location"),
        position_fields=tuple(m.get("position", [])),
        init_dirs=tuple(m.get("init", {}).get("dirs", [])),
        init_files=dict(m.get("init", {}).get("files", {})),
    )
