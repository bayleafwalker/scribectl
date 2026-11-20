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

An optional `heard:` prefix names who or where an event reaches without
taking part — the café hearing a horn across the water, a presenter receiving
a bulletin's news second-hand:

    - actors: Tavi | loc: Landing | heard: Café | The Tavi's horn sounds.

Sets that declare `knowledge: scoped` (worlds overheard through partial
sources) treat the timeline as world truth that no narrator holds whole: an
event reaches a pack only through its actors, its location or its `heard:`
list, and an event naming none of them reaches nobody.

A wrong entry is corrected by appending, never by editing. A bullet with a
`supersedes:` prefix drops bullets written before it: `B1.C3.S1950` drops every
one at that position, `pre#3` only the third bullet written at `pre` (counted
in file order, across headings). Its own fact, if it has one, stands at its own
heading:

    - supersedes: B1.C3.S1950 | actors: Café customers | loc: Café | They talk about the bus.

The superseded lines stay in the file as history.

A position may carry a sub-position after a dot, for a moment finer than the
heading's unit: `S1812.40` sorts after `S1812` and before `S1813`. Listening
sets read it as a second (18:12:40), where two positions must hear one sound
at the same moment.

`render_standing` writes what replay leaves standing (positions and bullets,
no prose, corrections applied): the oracle a canon reviewer reads, so the
reviewer applies nothing the timeline's prose says that the voicer never saw.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .vault import Vault, Note

POS = re.compile(r"^(pre|B(\d+)\.C(\d+)\.S(\d+)(?:\.(\d+))?)$", re.IGNORECASE)


@dataclass
class Event:
    pos: tuple[int, ...]  # sort key; pre-history sorts before everything
    pos_label: str
    actors: list[str]
    location: str | None
    fact: str
    heard: list[str] = field(default_factory=list)  # reached without taking part


def _pos_key(label: str) -> tuple[int, ...] | None:
    """(book, chapter, scene[, sub]). A sub-position makes a longer tuple, which
    sorts after its scene and before the next; a card's 3-tuple position is
    still strictly after everything earlier in its scene's unit."""
    m = POS.match(label.strip())
    if not m:
        return None
    if m.group(1).lower() == "pre":
        return (-1, -1, -1)
    key = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
    return key + (int(m.group(5)),) if m.group(5) else key


def _names(p: str) -> list[str]:
    return [a.strip() for a in p.split(":", 1)[1].split(",") if a.strip()]


def _parse_bullet(text: str) -> tuple[list[str], str | None, str, list[str], str | None]:
    actors: list[str] = []
    heard: list[str] = []
    loc: str | None = None
    supersedes: str | None = None
    parts = [p.strip() for p in text.split("|")]
    fact_parts = []
    for p in parts:
        low = p.lower()
        if low.startswith("actors:"):
            actors = _names(p)
        elif low.startswith("heard:"):
            heard = _names(p)
        elif low.startswith("loc:"):
            loc = p.split(":", 1)[1].strip()
        elif low.startswith("supersedes:"):
            supersedes = p.split(":", 1)[1].strip()
        else:
            fact_parts.append(p)
    return actors, loc, " | ".join(fact_parts).strip(), heard, supersedes


SUPERSEDES = re.compile(r"^(?P<pos>[^#\s]+)(?:#(?P<n>[1-9]\d*))?$")


def _replay(note: Note) -> tuple[list[Event], list[str]]:
    """Bullets in file order, applying each `supersedes:` as it is reached.
    Returns the standing events and the `supersedes:` values that corrected
    nothing (malformed, or no such bullet written before them)."""
    standing: list[tuple[tuple[int, ...], int, Event]] = []
    dangling: list[str] = []
    written: dict[tuple[int, ...], int] = {}  # bullets per position so far
    current_label: str | None = None
    current_key: tuple[int, ...] | None = None
    for line in note.body.splitlines():
        if line.startswith("## "):
            label = line[3:].strip()
            key = _pos_key(label)
            current_label, current_key = (label, key) if key else (None, None)
        elif line.strip().startswith("- ") and current_key is not None:
            actors, loc, fact, heard, sup = _parse_bullet(line.strip()[2:])
            if sup is not None:
                m = SUPERSEDES.match(sup)
                target = _pos_key(m["pos"]) if m else None
                nth = int(m["n"]) if m and m["n"] else None
                if target in written and (nth is None or nth <= written[target]):
                    standing = [(k, n, e) for k, n, e in standing
                                if not (k == target and nth in (None, n))]
                else:
                    dangling.append(sup)
            written[current_key] = written.get(current_key, 0) + 1
            if fact or sup is None:
                standing.append((current_key, written[current_key],
                                 Event(current_key, current_label, actors, loc, fact, heard)))
    return [e for _, _, e in standing], dangling


def load_events(note: Note) -> list[Event]:
    """The standing events, in file order, with superseded bullets dropped."""
    return _replay(note)[0]


def dangling_supersedes(note: Note) -> list[str]:
    """`supersedes:` values that correct nothing. A typo there leaves the wrong
    entry standing, so doctor surfaces it."""
    return _replay(note)[1]


def render_standing(note: Note) -> str:
    """The standing timeline: every event replay keeps, by position, one
    heading per position (a corrected position's bullets gather under it)."""
    out: list[str] = []
    pos = None
    for e in sorted(load_events(note), key=lambda e: e.pos):
        if e.pos != pos:
            pos = e.pos
            out += ["", f"## {e.pos_label}"]
        routing = [f"actors: {', '.join(e.actors)}" if e.actors else "",
                   f"loc: {e.location}" if e.location else "",
                   f"heard: {', '.join(e.heard)}" if e.heard else ""]
        out.append("- " + " | ".join([r for r in routing if r] + [e.fact]))
    return "\n".join(out).strip() + "\n"


def prior_relevant(vault: Vault, before: tuple[int, ...],
                   actors: set[str], location: str | None,
                   scoped: bool = False) -> list[Event]:
    """Events strictly before `before` touching any actor in scope or the location.

    Unscoped (the default), an event naming no actors is global and always
    relevant. Scoped, nothing is global: the pack holds only what reached its
    actors or location — the knowledge boundary of one source."""
    tl = vault.one("timeline")
    if not tl:
        return []
    out = []
    for e in load_events(tl):
        if e.pos >= before:
            continue
        hit = bool((set(e.actors) | set(e.heard)) & actors) or (
            location and (e.location == location or location in e.heard))
        if hit or (not e.actors and not scoped):  # unscoped: actor-less = global
            out.append(e)
    return sorted(out, key=lambda e: e.pos)
