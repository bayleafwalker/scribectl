"""Timeline: an append-only canon artifact recording who-knew/did-what-when.

This is the oracle review_canon checks against. Without it, a reviewer can only
verify facts in isolation, never facts in sequence — and sequence (a dead
brother speaking, a secret known before it was learned) is the axis prose
actually drifts on.

Events are parsed from a single Timeline note. Each event is one `- ` bullet
under a `## ` story-position heading of the form `B<book>.C<chapter>.S<scene>`
(or `pre` for founding-era / backstory). Format per bullet:

    - actors: Mara Vey, Inspector Kalen | loc: Lower Ashmarket | fact text here

`actors:` and `loc:` are optional prefixes; everything after the last `|` is the
fact. Append new events; never edit or reorder existing ones.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .vault import Vault, Note

POS = re.compile(r"^(pre|B(\d+)\.C(\d+)\.S(\d+))$", re.IGNORECASE)


@dataclass
class Event:
    pos: tuple[int, int, int]  # sort key; pre-history sorts before everything
    pos_label: str
    actors: list[str]
    location: str | None
    fact: str


def _pos_key(label: str) -> tuple[int, int, int] | None:
    m = POS.match(label.strip())
    if not m:
        return None
    if m.group(1).lower() == "pre":
        return (-1, -1, -1)
    return (int(m.group(2)), int(m.group(3)), int(m.group(4)))


def _parse_bullet(text: str) -> tuple[list[str], str | None, str]:
    actors: list[str] = []
    loc: str | None = None
    parts = [p.strip() for p in text.split("|")]
    fact_parts = []
    for p in parts:
        low = p.lower()
        if low.startswith("actors:"):
            actors = [a.strip() for a in p.split(":", 1)[1].split(",") if a.strip()]
        elif low.startswith("loc:"):
            loc = p.split(":", 1)[1].strip()
        else:
            fact_parts.append(p)
    return actors, loc, " | ".join(fact_parts).strip()


def load_events(note: Note) -> list[Event]:
    events: list[Event] = []
    current_label: str | None = None
    current_key: tuple[int, int, int] | None = None
    for line in note.body.splitlines():
        if line.startswith("## "):
            label = line[3:].strip()
            key = _pos_key(label)
            current_label, current_key = (label, key) if key else (None, None)
        elif line.strip().startswith("- ") and current_key is not None:
            actors, loc, fact = _parse_bullet(line.strip()[2:])
            events.append(Event(current_key, current_label, actors, loc, fact))
    return events


def prior_relevant(vault: Vault, before: tuple[int, int, int],
                   actors: set[str], location: str | None) -> list[Event]:
    """Events strictly before `before` touching any actor in scope or the location."""
    tl = vault.one("timeline")
    if not tl:
        return []
    out = []
    for e in load_events(tl):
        if e.pos >= before:
            continue
        hit = bool(set(e.actors) & actors) or (location and e.location == location)
        if hit or not e.actors:  # global events (no actors) always relevant
            out.append(e)
    return sorted(out, key=lambda e: e.pos)
