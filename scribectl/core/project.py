"""State projection (kctl-shaped, read-only).

The doc proposed three parallel mutable frontmatter enums (status / draft_status
/ canon_level), with "ratified" living in two of them. That is hand-maintained
mutable state — the exact thing append-only models exist to refuse, and a status
field you flip by hand will lie the moment you're mid-flow.

So status is *derived*, not stored. A note's real state is a function of the
vault: does a draft file link back to the card, did a clean review land, is the
node listed as Accepted in the ratification ledger. This module is the
projection. Nothing here writes.

Which note types are cards and which are fact-bearing nodes comes from the
project's TemplateSet; the derivation logic is identical across sets.
"""
from __future__ import annotations

from .vault import Vault, Note


def ledger_accepted(vault: Vault) -> set[str]:
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
        # Ledger says Accepted but the node carries no facts: the two halves of
        # ratification (paste the fact, append the receipt) have diverged.
        return "ratified" if has_facts else "ratified_empty"
    if has_facts:
        return "seeded"
    return "stub"


def _drafts_for(vault: Vault, card_name: str) -> list[Note]:
    return [n for n in vault.notes.values()
            if n.type == "draft" and card_name in n.links()]


def unresolved_scope(vault: Vault, note: Note, scope_fields) -> list[str]:
    scope = [l for f in scope_fields for l in note.links(f)]
    return [l for l in dict.fromkeys(scope) if vault.resolve(l) is None]


def card_status(vault: Vault, note: Note, scope_fields) -> str:
    drafts = _drafts_for(vault, note.name)
    reviews = [n for n in vault.notes.values()
               if n.type == "review_report" and note.name in n.links()]
    if not drafts:
        return "ready_for_fill" if not unresolved_scope(vault, note, scope_fields) else "blocked_unresolved_scope"
    if reviews:
        return "reviewed"
    return "has_draft"


def project(vault: Vault, ts) -> list[tuple[str, str, str, str]]:
    """Return (type, name, derived_status, detail) rows for the template set's
    legible artifact types. detail says *why* for the states that need acting
    on: which scope links are unresolved, or that a ledger-accepted node
    carries no facts."""
    accepted = ledger_accepted(vault)
    rows: list[tuple[str, str, str, str]] = []
    for n in sorted(vault.notes.values(), key=lambda x: (x.type, x.name)):
        if n.type in ts.node_types:
            s = canon_status(vault, n, accepted)
            detail = "ledger-accepted but no ratified facts in node" if s == "ratified_empty" else ""
            rows.append((n.type, n.name, s, detail))
        elif n.type == ts.card_type:
            s = card_status(vault, n, ts.scope_fields)
            missing = unresolved_scope(vault, n, ts.scope_fields) if s == "blocked_unresolved_scope" else []
            detail = "missing: " + ", ".join(f"[[{l}]]" for l in missing) if missing else ""
            rows.append((n.type, n.name, s, detail))
    return rows
