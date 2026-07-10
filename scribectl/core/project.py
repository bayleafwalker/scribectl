"""State projection (kctl-shaped, read-only).

The doc proposed three parallel mutable frontmatter enums (status / draft_status
/ canon_level), with "ratified" living in two of them. That is hand-maintained
mutable state — the exact thing append-only models exist to refuse, and a status
field you flip by hand will lie the moment you're mid-flow.

So status is *derived*, not stored. A note's real state is a function of the
vault: does a draft file link back to the scene, did a clean canon review land,
is the node listed as Accepted in the ratification ledger. This module is the
projection. Nothing here writes.
"""
from __future__ import annotations

from .vault import Vault, Note


def _ledger_accepted(vault: Vault) -> set[str]:
    led = vault.one("ratification_log")
    if not led:
        return set()
    accepted: set[str] = set()
    capture = False
    for line in led.body.splitlines():
        s = line.strip()
        if s.startswith("### "):
            capture = s[4:].strip().lower() == "accepted"
        elif capture:
            accepted.update(line.strip("[] ") for line in __import__("re").findall(r"\[\[([^\]|]+)", line))
    return accepted


def canon_status(vault: Vault, note: Note, accepted: set[str]) -> str:
    facts = note.section("Ratified facts")
    has_facts = bool(facts and "_(none" not in facts and facts.strip())
    if note.name in accepted:
        return "ratified"
    if has_facts:
        return "seeded"
    return "stub"


def _drafts_for(vault: Vault, scene_name: str) -> list[Note]:
    return [n for n in vault.notes.values()
            if n.type == "draft" and scene_name in n.links()]


def scene_status(vault: Vault, note: Note) -> str:
    drafts = _drafts_for(vault, note.name)
    scope = note.links("canon_scope") + note.links("location") + note.links("characters")
    unresolved = [l for l in scope if vault.resolve(l) is None]
    reviews = [n for n in vault.notes.values()
               if n.type == "review_report" and note.name in n.links()]
    if not drafts:
        return "ready_for_fill" if not unresolved else "blocked_unresolved_scope"
    if reviews:
        return "reviewed"
    return "has_draft"


def project(vault: Vault) -> list[tuple[str, str, str]]:
    """Return (type, name, derived_status) rows for the legible artifact types."""
    accepted = _ledger_accepted(vault)
    rows: list[tuple[str, str, str]] = []
    for n in sorted(vault.notes.values(), key=lambda x: (x.type, x.name)):
        if n.type == "canon_node":
            rows.append((n.type, n.name, canon_status(vault, n, accepted)))
        elif n.type == "scene_card":
            rows.append((n.type, n.name, scene_status(vault, n)))
    return rows
