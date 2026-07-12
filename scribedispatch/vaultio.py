"""Read-side vault helpers + pack verification for the dispatcher.

Reading is unrestricted (the vault is data); every WRITE lives in landing.py.
Frontmatter parsing here is deliberately local and minimal — the dispatcher's
contract with the engine is the CLI, not engine internals.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

from . import DispatchError

WIKILINK = re.compile(r"\[\[([^\]|]+)")


def read_note(path: Path) -> tuple[dict, str]:
    """(frontmatter dict, body) — tolerant: no fence means empty meta."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            meta = yaml.safe_load(text[4:end]) or {}
            return (meta if isinstance(meta, dict) else {}), text[end + 4:].lstrip("\n")
    return {}, text


def wikilinks(value) -> list[str]:
    return [m.strip() for m in WIKILINK.findall(str(value or ""))]


def find_note(root: Path, name: str) -> Path:
    hits = sorted(root.rglob(f"{name}.md"))
    if not hits:
        raise DispatchError(f"no note named {name!r} under {root}")
    return hits[0]


def note_title(path: Path) -> str:
    _, body = read_note(path)
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def load_contracts(root: Path) -> dict[str, dict]:
    """Contract notes keyed by every name their `target` link might mean —
    the note name or the card's H1 title (fixture contracts link the title).
    Values: the contract's frontmatter plus its raw text under `_text`."""
    out: dict[str, dict] = {}
    contracts_dir = root / "control" / "contracts"
    for p in sorted(contracts_dir.glob("*.md")) if contracts_dir.is_dir() else []:
        meta, _ = read_note(p)
        if meta.get("type") != "contract":
            continue
        meta["_text"] = p.read_text(encoding="utf-8")
        for target in wikilinks(meta.get("target")):
            out[target] = meta
    return out


def contract_for(contracts: dict[str, dict], root: Path, card: str) -> dict | None:
    if card in contracts:
        return contracts[card]
    try:
        return contracts.get(note_title(find_note(root, card)))
    except DispatchError:
        return None


def verify_pack(path: Path) -> str:
    """Return the pack's sha after re-deriving it from the content — the
    receipt an agent artifact cites must be the bytes the agent actually got."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"`pack-sha: ([0-9a-f]{12})`", text)
    if not m:
        raise DispatchError(f"{path}: no pack-sha line — not a frozen pack")
    sha = m.group(1)
    stripped = text.replace(f"`pack-sha: {sha}`\n\n", "", 1)
    if hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:12] != sha:
        raise DispatchError(f"{path}: content does not match its pack-sha {sha}")
    return sha


def pack_for_sha(pack_output: Path, sha: str) -> Path | None:
    hits = sorted(pack_output.glob(f"*-{sha}-context.md")) if pack_output.is_dir() else []
    return hits[0] if hits else None
