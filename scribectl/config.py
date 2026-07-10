"""Vault roots + project discovery.

A project is a directory containing a note with `type: scribe-project`
frontmatter. The note is both the config and the discovery marker: the
registry lives in the vault itself, syncs with it, and cannot drift from the
project it describes. All paths in the frontmatter are relative to the note's
directory. The body of the note is the human's; only the frontmatter is read.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .core.vault import _parse

DEFAULT_VAULT = Path("/media/Creative")
DEFAULT_ROOTS = {
    "world": "world",
    "structure": "structure",
    "body": "body",
    "control": "control",
    "reviews": "reviews",
}
DEFAULTS = {
    "template_set": "fiction",
    "voice_canon": "world/language/Prose Voice Canon.md",
    "timeline": "control/timeline/Timeline.md",
    "ratification_log": "control/ratification/Ratification Log.md",
    "pack_output": "control/context-packs",
}


@dataclass
class ProjectConfig:
    name: str
    note_path: Path
    template_set: str
    roots: dict[str, Path]
    voice_canon: Path
    timeline: Path
    ratification_log: Path
    pack_output: Path
    sources: list[str] = field(default_factory=list)

    @property
    def root(self) -> Path:
        return self.note_path.parent

    @classmethod
    def from_note(cls, path: str | Path) -> "ProjectConfig":
        path = Path(path)
        note = _parse(path)
        if note.type != "scribe-project":
            raise ValueError(f"{path} is not a scribe-project note (type: {note.type})")
        meta = note.meta
        base = path.parent
        roots = {k: base / meta.get("roots", {}).get(k, v) for k, v in DEFAULT_ROOTS.items()}
        return cls(
            name=meta.get("name", path.stem),
            note_path=path,
            template_set=meta.get("template_set", DEFAULTS["template_set"]),
            roots=roots,
            voice_canon=base / meta.get("voice_canon", DEFAULTS["voice_canon"]),
            timeline=base / meta.get("timeline", DEFAULTS["timeline"]),
            ratification_log=base / meta.get("ratification_log", DEFAULTS["ratification_log"]),
            pack_output=base / meta.get("pack_output", DEFAULTS["pack_output"]),
            sources=[str(s) for s in meta.get("sources") or []],
        )


def vault_roots() -> list[Path]:
    """Configured vault roots: $SCRIBECTL_VAULT (os.pathsep-separated),
    then ~/.config/scribectl/vaults (one path per line), then the default."""
    env = os.environ.get("SCRIBECTL_VAULT")
    if env:
        return [Path(p) for p in env.split(os.pathsep) if p]
    cfg = Path.home() / ".config" / "scribectl" / "vaults"
    if cfg.is_file():
        lines = [l.strip() for l in cfg.read_text(encoding="utf-8").splitlines()]
        roots = [Path(l) for l in lines if l and not l.startswith("#")]
        if roots:
            return roots
    return [DEFAULT_VAULT]


def discover_projects(roots: list[Path] | None = None) -> list[ProjectConfig]:
    roots = roots if roots is not None else vault_roots()
    found: list[ProjectConfig] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.md")):
            try:
                note = _parse(p)
            except Exception:
                continue  # unreadable / non-UTF8 strays never block discovery
            if note.type == "scribe-project" and p.parent not in seen:
                seen.add(p.parent)
                found.append(ProjectConfig.from_note(p))
    return sorted(found, key=lambda c: c.name)
