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

import re

from .inbox import mine_proposal, parse_inbox
from .vault import Vault, Note, WIKILINK

BLANK_LINK = re.compile(r"\[\[\s*\]\]")


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


def ledger_links(vault: Vault) -> set[str]:
    """Every wikilink target in the ratification log. A proposal named here has
    reached a verdict (its `via [[proposal]]` marker rode a receipt into the
    ledger), which is exactly what 'swept' means."""
    led = vault.one("ratification_log")
    if not led:
        return set()
    return {t.strip() for t in WIKILINK.findall(led.body) if t.strip()}


def reconciled_into(vault: Vault) -> dict[str, str]:
    """Map each proposal folded into a merge proposal → the merge that claims
    it. A merge proposal (docs/RATIFICATION.md build item 4) declares
    `reconciles: [[A]], [[B]]`; those siblings retire from the open queue, their
    candidates now the merge's to carry forward."""
    out: dict[str, str] = {}
    for p in vault.by_type("fact_proposal"):
        for sib in p.links("reconciles"):
            out[sib] = p.name
    return out


def proposal_status(note: Note, linked_in_ledger: set[str],
                    reconciled: dict[str, str] | set[str] = frozenset()) -> str:
    """A fact_proposal is `swept` once its candidates have receipts (wikilinked
    from the ledger), `reconciled` once folded into a merge proposal, else
    `open` — still awaiting the writer (docs/RATIFICATION.md, "Derived state")."""
    if note.name in linked_in_ledger:
        return "swept"
    if note.name in reconciled:
        return "reconciled"
    return "open"


def open_proposal_candidates(vault: Vault, node_name: str, linked_in_ledger: set[str],
                             reconciled: dict[str, str] | set[str] = frozenset()) -> int:
    """Candidate facts sitting in open (unswept) proposals that *route* to this
    node — the 'N candidates pending' a stub advertises so status points the
    writer at the proposal queue instead of a dead end. Counting follows each
    candidate's actual route, so a candidate that overrides its proposal's
    target lands against the node it truly names."""
    total = 0
    for p in vault.by_type("fact_proposal"):
        if proposal_status(p, linked_in_ledger, reconciled) != "open":
            continue
        blocks = mine_proposal(p)
        if not blocks:
            continue
        cands, _ = parse_inbox("\n".join(blocks) + "\n")
        total += sum(1 for c in cands if c.target == node_name)
    return total


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


def placeholder_scope(vault: Vault, note: Note, scope_fields) -> bool:
    """A pristine `new card` scaffold: still carries a blank `[[ ]]` scope
    placeholder AND has no authored scope link anywhere. Without this guard a
    fresh scaffold derives ready_for_fill (blank links are dropped by links())
    and ambient watch would fill an empty card the moment `new card` returns.

    The guard is deliberately narrow — the first real scope link the writer
    adds means the card is authored, and any placeholders still sitting in
    *other* fields go back to meaning 'no link here' (a deliberately-blank
    location on an otherwise-filled card stays ready_for_fill)."""
    has_placeholder = any(BLANK_LINK.search(str(note.meta[f]))
                          for f in scope_fields if f in note.meta)
    has_real_link = any(note.links(f) for f in scope_fields if f in note.meta)
    return has_placeholder and not has_real_link


def card_status(vault: Vault, note: Note, scope_fields) -> str:
    drafts = _drafts_for(vault, note.name)
    reviews = [n for n in vault.notes.values()
               if n.type == "review_report" and note.name in n.links()]
    if not drafts:
        if placeholder_scope(vault, note, scope_fields):
            return "awaiting_scope"
        return "ready_for_fill" if not unresolved_scope(vault, note, scope_fields) else "blocked_unresolved_scope"
    if reviews:
        return "reviewed"
    return "has_draft"


def card_artifacts(vault: Vault, card_name: str) -> dict:
    """Drafts linking back to the card, and review reports by kind (with the
    draft each one reviewed). This is the dispatch layer's what-still-fires
    question, answered here so derived state keeps one implementation."""
    reviews = [n for n in vault.notes.values()
               if n.type == "review_report" and card_name in n.links()]
    return {
        "drafts": sorted(d.name for d in _drafts_for(vault, card_name)),
        "reviews": sorted(({"name": r.name,
                            "kind": str(r.meta.get("kind", "")),
                            "draft": next(iter(r.links("draft")), "")}
                           for r in reviews), key=lambda r: r["name"]),
    }


def project(vault: Vault, ts) -> list[tuple[str, str, str, str]]:
    """Return (type, name, derived_status, detail) rows for the template set's
    legible artifact types. detail says *why* for the states that need acting
    on: which scope links are unresolved, that a ledger-accepted node carries no
    facts, or that a node has proposal candidates waiting in the queue."""
    accepted = ledger_accepted(vault)
    in_ledger = ledger_links(vault)
    reconciled = reconciled_into(vault)
    rows: list[tuple[str, str, str, str]] = []
    for n in sorted(vault.notes.values(), key=lambda x: (x.type, x.name)):
        if n.type in ts.node_types:
            s = canon_status(vault, n, accepted)
            detail = "ledger-accepted but no ratified facts in node" if s == "ratified_empty" else ""
            pending = open_proposal_candidates(vault, n.name, in_ledger, reconciled)
            if pending:
                note = f"{pending} candidate{'s' if pending != 1 else ''} pending"
                detail = f"{detail}; {note}" if detail else note
            rows.append((n.type, n.name, s, detail))
        elif n.type == "fact_proposal":
            s = proposal_status(n, in_ledger, reconciled)
            target = next(iter(n.links("target")), "")
            if s == "open":
                k = len(mine_proposal(n))
                detail = f"{k} candidate{'s' if k != 1 else ''} → [[{target}]]" if target else ""
            elif s == "reconciled":
                detail = f"folded into [[{reconciled[n.name]}]]"
            else:
                detail = ""
            rows.append((n.type, n.name, s, detail))
        elif n.type == ts.card_type:
            s = card_status(vault, n, ts.scope_fields)
            missing = unresolved_scope(vault, n, ts.scope_fields) if s == "blocked_unresolved_scope" else []
            detail = "missing: " + ", ".join(f"[[{l}]]" for l in missing) if missing else ""
            if s == "awaiting_scope":
                detail = "scope placeholders ([[ ]]) unfilled — author the card"
            rows.append((n.type, n.name, s, detail))
    return rows
