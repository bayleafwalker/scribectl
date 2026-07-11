"""Vault parsing layer.

A Note is a markdown file with YAML frontmatter and `## `-delimited sections.
The Vault loads every note and resolves [[wikilink]] -> Note by file stem.

Deliberately dumb about folders: type lives in frontmatter, navigation is by
links. Folders are storage, not taxonomy.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

WIKILINK = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]")
SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Note:
    path: Path
    meta: dict
    body: str

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def type(self) -> str:
        return self.meta.get("type", "untyped")

    def section(self, title: str) -> str | None:
        """Return the body text under a `## title` heading, or None."""
        matches = list(SECTION.finditer(self.body))
        for i, m in enumerate(matches):
            if m.group(1).strip().lower() == title.strip().lower():
                start = m.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(self.body)
                return self.body[start:end].strip()
        return None

    def section_titles(self) -> list[str]:
        return [m.group(1).strip() for m in SECTION.finditer(self.body)]

    def links(self, field_or_section: str | None = None) -> list[str]:
        """Wikilink targets. Scans the whole note, or a frontmatter list, or a section."""
        # allow_unicode: escaped dumps would break [[links]] with non-ASCII
        # names (Väki) before the regex ever sees them.
        if field_or_section is None:
            text = yaml.safe_dump(self.meta, allow_unicode=True) + "\n" + self.body
        elif field_or_section in self.meta:
            text = yaml.safe_dump(self.meta[field_or_section], allow_unicode=True)
        else:
            text = self.section(field_or_section) or ""
        # Blank targets ([[ ]] template placeholders) are not links.
        return [t for t in WIKILINK.findall(text) if t.strip()]


def _parse(path: Path) -> Note:
    raw = path.read_text(encoding="utf-8")
    meta: dict = {}
    body = raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            meta = yaml.safe_load(raw[3:end]) or {}
            body = raw[end + 4 :].lstrip("\n")
    return Note(path=path, meta=meta, body=body)


@dataclass
class Vault:
    root: Path
    notes: dict[str, Note] = field(default_factory=dict)  # keyed by stem

    @classmethod
    def load(cls, root: str | Path) -> "Vault":
        root = Path(root)
        v = cls(root=root)
        for p in sorted(root.rglob("*.md")):
            note = _parse(p)
            v.notes[p.stem] = note
        return v

    def resolve(self, link: str) -> Note | None:
        return self.notes.get(link.strip())

    def by_type(self, t: str) -> list[Note]:
        return [n for n in self.notes.values() if n.type == t]

    def one(self, t: str) -> Note | None:
        hits = self.by_type(t)
        return hits[0] if hits else None
