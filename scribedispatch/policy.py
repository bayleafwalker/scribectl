"""The dispatch policy — pure derivation over `status --json` output.

Fill fires on ready_for_fill (only with an authored contract: contracts are
intent, and the coordinator never authors one). Reviews fire for whichever
lanes a card's newest draft is still missing. Everything else — reworking
drafts, consuming reviews, ratifying — is the writer's, and nothing here
schedules or stores anything.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .vaultio import contract_for

DEFAULT_REVIEW_KINDS = ("canon", "voice")
# The variant tag landing stamps into a draft's name (#1100). Policy reads it
# back to plan per-variant reviews — the dispatcher parsing its own naming
# convention, never engine state.
VARIANT_TAG = re.compile(r" \(v(\d+)\)$")
# Gamedev tie-ins get the mechanics lane by default: a fic where magic works
# differently than the game is canon rot in both directions.
SET_REVIEW_KINDS = {"gamedev": ("canon", "voice", "mechanics")}
_REVIEW_ALIASES = {"canon_check": "canon", "voice_check": "voice",
                   "mechanics_check": "mechanics",
                   "canon": "canon", "voice": "voice", "mechanics": "mechanics"}


@dataclass
class Dispatch:
    skill: str                # body_fill | review_canon | review_voice
    card: str
    reason: str
    draft: str | None = None  # reviews: the draft under review
    kind: str | None = None   # reviews: canon | voice
    variant: int | None = None  # fills: 1-based variant index (#1100 breadth)
    variants_total: int | None = None


def variant_count(contract: dict | None) -> int:
    """The contract's `variants:` — breadth is authored intent, like the
    contract itself. Anything unparsable or < 1 means one plain fill."""
    try:
        return max(1, int((contract or {}).get("variants") or 1))
    except (TypeError, ValueError):
        return 1


def _variant_set(drafts: list[str]) -> list[str]:
    """The drafts reviews should target. Normally just the newest draft; when
    the newest carries a variant tag, its whole sibling set — every variant
    gets its own lanes, because the reviews are the information the writer's
    pick runs on (#1100). A later untagged draft (the writer's rework of the
    pick) ends the set: reviews return to newest-only."""
    newest = drafts[-1]
    m = VARIANT_TAG.search(newest)
    if not m:
        return [newest]
    base = newest[:m.start()]
    return [d for d in drafts
            if (dm := VARIANT_TAG.search(d)) and d[:dm.start()] == base]


def review_kinds(contract: dict | None,
                 default: tuple[str, ...] = DEFAULT_REVIEW_KINDS) -> tuple[str, ...]:
    """The contract's review_after decides the lanes; a card whose draft
    arrived without a contract still gets the set's default lanes — reviews
    fire on drafts, not on paperwork."""
    if not contract or not contract.get("review_after"):
        return default
    kinds = [_REVIEW_ALIASES[k] for k in contract["review_after"] if k in _REVIEW_ALIASES]
    return tuple(dict.fromkeys(kinds)) or default


def plan(state: dict, contracts: dict[str, dict],
         only_card: str | None = None) -> tuple[list[Dispatch], list[str]]:
    """(dispatches, notes) — notes explain every card NOT dispatched."""
    root = Path(state["project"]["root"])
    card_type = state["project"]["card_type"]
    default_kinds = SET_REVIEW_KINDS.get(state["project"].get("template_set", ""),
                                         DEFAULT_REVIEW_KINDS)
    dispatches: list[Dispatch] = []
    notes: list[str] = []
    for row in state["rows"]:
        if row["type"] != card_type or (only_card and row["name"] != only_card):
            continue
        card, s = row["name"], row["status"]
        contract = contract_for(contracts, root, card)
        if s == "blocked_unresolved_scope":
            notes.append(f"{card}: blocked ({row['detail']}) — resolve scope first")
        elif s == "awaiting_scope":
            notes.append(f"{card}: scaffolded but unauthored (scope placeholders "
                         "unfilled) — author the card first")
        elif s == "ready_for_fill":
            if contract is None or contract.get("mode") != "body_fill":
                notes.append(f"{card}: ready_for_fill but no body_fill contract — "
                             "skipped (contracts are authored intent)")
            else:
                n = variant_count(contract)
                if n == 1:
                    dispatches.append(Dispatch("body_fill", card, "ready_for_fill with contract"))
                else:
                    # Breadth, not iteration (#1100): N independent fills of
                    # the same frozen pack. No fill sees another; the writer
                    # picks. A card with any draft variant is has_draft, so
                    # a partially landed set never refires.
                    dispatches += [Dispatch("body_fill", card,
                                            f"ready_for_fill with contract (variant {i}/{n})",
                                            variant=i, variants_total=n)
                                   for i in range(1, n + 1)]
        elif s in ("has_draft", "reviewed"):
            targets = _variant_set(row["drafts"])
            kinds = review_kinds(contract, default_kinds)
            if len(targets) == 1:
                present = {r["kind"] for r in row["reviews"]}
                for kind in kinds:
                    if kind not in present:
                        dispatches.append(Dispatch(f"review_{kind}", card,
                                                   f"draft lacks {kind} review",
                                                   draft=targets[0], kind=kind))
                if all(k in present for k in kinds):
                    notes.append(f"{card}: fully reviewed — the rest is the writer's")
            else:
                # Per-variant lanes: the reviews are the information the
                # writer's pick runs on. Each review reads only its own
                # variant — no agent judges another agent's draft.
                outstanding = False
                for draft in targets:
                    present = {r["kind"] for r in row["reviews"] if r["draft"] == draft}
                    for kind in kinds:
                        if kind not in present:
                            outstanding = True
                            dispatches.append(Dispatch(f"review_{kind}", card,
                                                       f"variant lacks {kind} review",
                                                       draft=draft, kind=kind))
                if not outstanding:
                    notes.append(f"{card}: all {len(targets)} variants fully "
                                 "reviewed — the writer picks")
    return dispatches, notes
