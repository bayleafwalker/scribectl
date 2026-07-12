"""Artifact landing — the dispatcher's ONLY writes, and their whole discipline.

New files only (never overwrite: a human may have reworked what's there), in
exactly the designated dirs (`body/drafts/`, `reviews/<kind>/`). The
frontmatter is stamped here, deterministically — type, links, pack_sha,
runner, model, date — the agent supplies only the body. A review verdict the
agent failed to state parses as `issues`: fail toward the writer looking.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from . import DispatchError


def _strip_frontmatter(body: str) -> str:
    """Agents are told not to emit frontmatter; if one does anyway, it does
    not get to stamp its own metadata."""
    if body.startswith("---\n"):
        end = body.find("\n---", 4)
        if end != -1:
            return body[end + 4:].lstrip("\n")
    return body


def _write_new(path: Path, text: str) -> Path:
    if path.exists():
        raise DispatchError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def land_draft(root: Path, card: str, contract: dict, body: str,
               pack_sha: str, runner: str, model: str | None) -> Path:
    rel = str(contract.get("output_target") or f"body/drafts/{card} draft (dispatch).md").lstrip("/")
    fm = "\n".join([
        "---",
        "type: draft",
        f'card: "[[{card}]]"',
        f"pack_sha: {pack_sha}",
        "agent: body_fill",
        f"runner: {runner}",
        f"model: {model or 'default'}",
        f"generated: {date.today().isoformat()}",
        "---",
        "", "",
    ])
    return _write_new(root / rel, fm + _strip_frontmatter(body).strip() + "\n")


def parse_verdict(body: str) -> tuple[str, str]:
    """(verdict, rest-of-body). Missing/malformed verdict → issues."""
    lines = body.strip().splitlines()
    if lines and lines[0].strip().lower() in ("verdict: clean", "verdict: issues"):
        return lines[0].split(":", 1)[1].strip().lower(), "\n".join(lines[1:]).lstrip("\n")
    return "issues", body.strip()


def land_review(root: Path, card: str, kind: str, draft: str, body: str,
                pack_sha: str | None, runner: str, model: str | None) -> Path:
    verdict, rest = parse_verdict(_strip_frontmatter(body))
    fm = "\n".join([
        "---",
        "type: review_report",
        f"kind: {kind}",
        f'target: "[[{card}]]"',
        f'draft: "[[{draft}]]"',
        f"pack_sha: {pack_sha or 'none'}",
        f"verdict: {verdict}",
        f"agent: review_{kind}",
        f"runner: {runner}",
        f"model: {model or 'default'}",
        f"generated: {date.today().isoformat()}",
        "---",
        "", "",
    ])
    path = root / "reviews" / kind / f"{draft} — {kind} review.md"
    return _write_new(path, fm + rest.strip() + "\n")
