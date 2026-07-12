"""Skill prompt rendering: `.agents/skills/<name>.md` are string.Template
markdown ($vars — prose braces stay safe; a missing variable fails loud).
Override the directory with $SCRIBE_SKILLS_DIR (the default resolves relative
to this repo checkout — editable installs are the supported mode for now).
"""
from __future__ import annotations

import os
from pathlib import Path
from string import Template

from . import DispatchError


def skills_dir() -> Path:
    env = os.environ.get("SCRIBE_SKILLS_DIR")
    d = Path(env) if env else Path(__file__).resolve().parents[1] / ".agents" / "skills"
    if not d.is_dir():
        raise DispatchError(f"skills directory not found: {d} (set SCRIBE_SKILLS_DIR)")
    return d


def render(skill: str, **vars: str) -> str:
    path = skills_dir() / f"{skill}.md"
    if not path.is_file():
        raise DispatchError(f"no skill contract at {path}")
    try:
        return Template(path.read_text(encoding="utf-8")).substitute(vars)
    except KeyError as e:
        raise DispatchError(f"{path.name}: unfilled template variable ${e.args[0]}") from e
