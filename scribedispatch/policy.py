"""The dispatch policy — pure derivation over `status --json` output.

Fill fires on ready_for_fill (only with an authored contract: contracts are
intent, and the coordinator never authors one). Reviews fire for whichever
lanes a card's newest draft is still missing. Everything else — reworking
drafts, consuming reviews, ratifying — is the writer's, and nothing here
schedules or stores anything.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .vaultio import contract_for

DEFAULT_REVIEW_KINDS = ("canon", "voice")
_REVIEW_ALIASES = {"canon_check": "canon", "voice_check": "voice",
                   "canon": "canon", "voice": "voice"}


@dataclass
class Dispatch:
    skill: str                # body_fill | review_canon | review_voice
    card: str
    reason: str
    draft: str | None = None  # reviews: the draft under review
    kind: str | None = None   # reviews: canon | voice


def review_kinds(contract: dict | None) -> tuple[str, ...]:
    """The contract's review_after decides the lanes; a card whose draft
    arrived without a contract still gets the default pair — reviews fire on
    drafts, not on paperwork."""
    if not contract or not contract.get("review_after"):
        return DEFAULT_REVIEW_KINDS
    kinds = [_REVIEW_ALIASES[k] for k in contract["review_after"] if k in _REVIEW_ALIASES]
    return tuple(dict.fromkeys(kinds)) or DEFAULT_REVIEW_KINDS


def plan(state: dict, contracts: dict[str, dict],
         only_card: str | None = None) -> tuple[list[Dispatch], list[str]]:
    """(dispatches, notes) — notes explain every card NOT dispatched."""
    root = Path(state["project"]["root"])
    card_type = state["project"]["card_type"]
    dispatches: list[Dispatch] = []
    notes: list[str] = []
    for row in state["rows"]:
        if row["type"] != card_type or (only_card and row["name"] != only_card):
            continue
        card, s = row["name"], row["status"]
        contract = contract_for(contracts, root, card)
        if s == "blocked_unresolved_scope":
            notes.append(f"{card}: blocked ({row['detail']}) — resolve scope first")
        elif s == "ready_for_fill":
            if contract is None or contract.get("mode") != "body_fill":
                notes.append(f"{card}: ready_for_fill but no body_fill contract — "
                             "skipped (contracts are authored intent)")
            else:
                dispatches.append(Dispatch("body_fill", card, "ready_for_fill with contract"))
        elif s in ("has_draft", "reviewed"):
            present = {r["kind"] for r in row["reviews"]}
            draft = row["drafts"][-1]
            for kind in review_kinds(contract):
                if kind not in present:
                    dispatches.append(Dispatch(f"review_{kind}", card,
                                               f"draft lacks {kind} review",
                                               draft=draft, kind=kind))
            if all(k in present for k in review_kinds(contract)):
                notes.append(f"{card}: fully reviewed — the rest is the writer's")
    return dispatches, notes
