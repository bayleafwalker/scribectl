"""The engine boundary: scribectl CLI subprocesses, nothing else.

Every pack the dispatcher feeds an agent was frozen by the same command a
human would run; the dispatcher never imports engine internals, so the
engine's read/write contract is also the dispatcher's.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from . import DispatchError


def _run(args: list[str]) -> str:
    proc = subprocess.run([sys.executable, "-m", "scribectl.cli", *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise DispatchError(f"scribectl {' '.join(args)} failed: {detail}")
    return proc.stdout


def status(project: str | None = None) -> dict:
    return json.loads(_run(["status", "--json"] + (["-p", project] if project else [])))


def mine(project: str | None = None) -> str:
    """Invoke the engine's `ratify --mine`: queue candidates from landed
    review artifacts into the ratification inbox as pending. Invoke, don't
    do (#1101, docs/DISPATCH.md): the dispatcher never parses report content
    and never writes the inbox itself — it fires the same idempotent command
    the writer would type (the via-link marker makes a second mine a no-op)."""
    return _run(["ratify", "--mine"] + (["-p", project] if project else []))


def freeze_pack(card: str, project: str | None = None) -> Path:
    """Freeze (or find already-frozen) the card's pack; return its path."""
    out = _run(["pack", card] + (["-p", project] if project else []))
    for line in out.splitlines():
        for prefix in ("wrote ", "unchanged "):
            if line.startswith(prefix) and "  (sha " in line:
                return Path(line[len(prefix):line.rindex("  (sha ")])
    raise DispatchError(f"could not locate pack path in scribectl output:\n{out}")
