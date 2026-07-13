"""The next-actions digest — 'where the next ten minutes go' (#1085).

Pure projection, like project.py: a function of the vault plus the inbox and
ledger text, computing what is waiting on the writer. Nothing here writes; the
CLI prints it and (optionally) pins it atop Status.md.

The sections mirror the loop's decision points in dependency order — author,
fill, rework, ratify, mine — so the digest reads top-to-bottom as the order to
act. Everything is derived; a card the writer finished simply stops appearing.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .inbox import mine, parse_inbox
from .project import card_status, ledger_accepted, canon_status, _drafts_for, unresolved_scope
from .vault import Note, Vault, WIKILINK


@dataclass
class Digest:
    ready: list[str] = field(default_factory=list)              # ready_for_fill, has contract
    ready_no_contract: list[str] = field(default_factory=list)  # ready_for_fill, needs a contract
    awaiting_scope: list[str] = field(default_factory=list)     # new-card scaffolds to author
    blocked: list[tuple[str, str]] = field(default_factory=list)  # (card, missing detail)
    rework: list[tuple[str, str, str]] = field(default_factory=list)  # (card, kind, draft) verdict=issues
    pending_inbox: int = 0
    unrouted_inbox: int = 0
    unmined_reports: int = 0
    unmined_candidates: int = 0
    ratified_empty: list[str] = field(default_factory=list)
    open_proposals: int = 0

    @property
    def empty(self) -> bool:
        return not any((self.ready, self.ready_no_contract, self.awaiting_scope,
                        self.blocked, self.rework, self.pending_inbox,
                        self.unrouted_inbox, self.unmined_reports,
                        self.ratified_empty, self.open_proposals))


def _card_title(note: Note) -> str:
    for line in note.body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return note.name


def _body_fill_contract_targets(vault: Vault) -> set[str]:
    """Names a body_fill contract points its `target` at — either a card's
    note name or its H1 title (contracts link whichever). Contract notes are
    ordinary markdown under the root, so the loaded vault already holds them."""
    targets: set[str] = set()
    for c in vault.by_type("contract"):
        if str(c.meta.get("mode", "")) == "body_fill":
            targets.update(c.links("target"))
    return targets


def _newest_draft(vault: Vault, card: str) -> str | None:
    drafts = sorted(d.name for d in _drafts_for(vault, card))
    return drafts[-1] if drafts else None


def build_digest(vault: Vault, ts, inbox_text: str, ledger_text: str) -> Digest:
    d = Digest()
    accepted = ledger_accepted(vault)
    carded = _body_fill_contract_targets(vault)

    for n in sorted(vault.notes.values(), key=lambda x: (x.type, x.name)):
        if n.type in ts.node_types:
            if canon_status(vault, n, accepted) == "ratified_empty":
                d.ratified_empty.append(n.name)
        elif n.type == ts.card_type:
            s = card_status(vault, n, ts.fill_fields)
            if s == "ready_for_fill":
                has_contract = n.name in carded or _card_title(n) in carded
                (d.ready if has_contract else d.ready_no_contract).append(n.name)
            elif s == "awaiting_scope":
                d.awaiting_scope.append(n.name)
            elif s == "blocked_unresolved_scope":
                missing = unresolved_scope(vault, n, ts.fill_fields)
                d.blocked.append((n.name, ", ".join(f"[[{m}]]" for m in missing)))
            elif s in ("has_draft", "reviewed"):
                newest = _newest_draft(vault, n.name)
                for r in vault.by_type("review_report"):
                    if (n.name in r.links() and newest and newest in r.links("draft")
                            and str(r.meta.get("verdict", "")).lower() == "issues"):
                        d.rework.append((n.name, str(r.meta.get("kind", "?")), newest))

    candidates, problems = parse_inbox(inbox_text)
    d.pending_inbox = sum(1 for c in candidates if c.verdict == "pending")
    # Arrowless candidates parse as problems ('no → [[target]]'): queued but
    # unrouted, and every sweep nags until the writer points them at a node.
    d.unrouted_inbox = sum(1 for _, msg in problems if "target" in msg)

    blocks, names = mine(vault, inbox_text, ledger_text)
    d.unmined_reports = len(names)
    d.unmined_candidates = len(blocks)

    # Open proposals (fact_proposal notes, docs/RATIFICATION.md build items 3–4):
    # one wikilinked from the ledger is swept, one folded into a merge is
    # reconciled; both drop out, leaving only the proposals still awaiting the
    # writer. The section renders only when some exist — no fabrication.
    in_ledger = {t.strip() for t in WIKILINK.findall(ledger_text) if t.strip()}
    reconciled = {s.strip() for p in vault.by_type("fact_proposal")
                  for s in p.links("reconciles")}
    d.open_proposals = sum(1 for p in vault.by_type("fact_proposal")
                           if p.name not in in_ledger and p.name not in reconciled)
    return d


def render_digest(d: Digest, project_name: str) -> str:
    """Human-facing markdown. Only non-empty sections render; a quiet project
    says so. Also the block pinned atop Status.md, so the two never diverge."""
    out = [f"# Next — {project_name}", ""]
    if d.empty:
        out += ["Nothing waiting — write. "
                "(No ready cards, no rework, an empty inbox, nothing to mine.)", ""]
        return "\n".join(out)

    def section(title: str, lines: list[str]) -> None:
        if lines:
            out.append(f"## {title}")
            out.extend(lines)
            out.append("")

    section("Author the card", [f"- {c} — scaffold: fill or remove the `[[ ]]` scope "
                                f"placeholders (then it's ready to fill)" for c in d.awaiting_scope]
            + [f"- {c} — blocked: resolve {missing}" for c, missing in d.blocked])
    section("Ready to fill",
            [f"- {c} — has a contract → `scribe-dispatch run`" for c in d.ready]
            + [f"- {c} — ready but no body_fill contract → `scribectl new card` "
               f"(or author one)" for c in d.ready_no_contract])
    section("Rework — a review flagged issues",
            [f"- {card} ({kind}) — draft {draft}" for card, kind, draft in d.rework])

    ratify_lines = []
    if d.pending_inbox:
        ratify_lines.append(f"- {d.pending_inbox} undecided candidate"
                            f"{'s' if d.pending_inbox != 1 else ''} in the inbox — "
                            "tick verdicts, then `scribectl ratify --sweep`")
    if d.unrouted_inbox:
        ratify_lines.append(f"- {d.unrouted_inbox} unrouted (no `→ [[target]]`) — "
                            "point each at a node")
    section("Ratify — the inbox", ratify_lines)

    if d.unmined_reports:
        section("Mine", [f"- {d.unmined_candidates} candidate"
                        f"{'s' if d.unmined_candidates != 1 else ''} in "
                        f"{d.unmined_reports} un-mined report"
                        f"{'s' if d.unmined_reports != 1 else ''}/proposal → `scribectl ratify --mine`"])
    section("Governance",
            [f"- {n} — ledger-accepted but the node carries no ratified facts "
             f"(ratified_empty)" for n in d.ratified_empty])
    if d.open_proposals:
        section("Proposals", [f"- {d.open_proposals} open fact proposal"
                             f"{'s' if d.open_proposals != 1 else ''} awaiting review"])
    return "\n".join(out)
