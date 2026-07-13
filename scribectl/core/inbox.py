"""Verdict inbox: parsing and pure sweep transforms.

The inbox (`control/ratification/Inbox.md`, `type: ratification_inbox`) is the
one writer-facing ratification surface: everything that proposes canon appends
structured candidates, the writer renders verdicts as checkboxes in Obsidian —
no shell, no quoting — and `scribectl ratify --sweep` executes them.

Candidate grammar, one per list item, indented lines are provenance carried
into the receipt verbatim:

    - [x] "the fact, worded as it should read in canon" → [[Target Node]]
          (from [[Draft note]], pack 0123abcdef01)

Marks: `[x]` accept, `[-]` reject, `[>]` defer (receipt, cleared), `[ ]`
undecided (stays in the inbox, no receipt — deferral is a verdict the writer
marks, not a side effect of sweeping). Fenced code blocks are skipped so
templates and notes can show example candidates without them being swept.

This module parses and computes new file contents; the CLI owns every write.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .vault import WIKILINK

CANDIDATE = re.compile(r"^- \[( |x|X|>|-)\]\s*(\S.*)$")
ARROW = re.compile(r"\s*(?:→|->)\s*")
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”')

VERDICTS = {"x": "accept", "-": "reject", ">": "defer", " ": "pending"}

# Review reports quarantine inventions under this heading (exact tail wording
# varies by template set, so match on the prefix).
CANDIDATE_SECTION = "introduced candidates"
# Fact proposals (docs/RATIFICATION.md, "The propose stage") list agent-mined
# candidates under this heading; all route to the proposal's target node.
PROPOSAL_SECTION = "candidate facts"


@dataclass(frozen=True)
class Candidate:
    verdict: str          # accept | reject | defer | pending
    fact: str             # ratified wording, surrounding quotes stripped
    target: str           # wikilink target the fact routes to
    provenance: str       # continuation lines verbatim ("" if none)
    lines: tuple[int, int]  # [start, end) line span in the inbox file


@dataclass(frozen=True)
class Mined:
    """One inbox-grammar candidate block plus the ordering signals its source
    artifact stated (#1104). The signals order the freshly mined batch for the
    writer's attention — conflicts-flagged first, then confidence descending —
    and do nothing else: they never ride into the inbox text, never touch
    candidates already queued, and never carry a verdict. An agent's confidence
    is input, not verdict (docs/RATIFICATION.md, "What stays forbidden")."""
    block: str
    conflicts: bool = False      # the proposal named a fact this rubs against
    confidence: str | None = None  # high | medium | low, else None

# Indented detail line under a proposal candidate; only these two keys matter
# to ordering — the quote (and everything else) is proposal-local noise here.
DETAIL = re.compile(r"^[ \t]+(confidence|conflicts):\s*(.+?)\s*$")

_CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}


def _stated_confidence(value: str | None) -> str | None:
    v = (value or "").strip().lower()
    return v if v in _CONFIDENCE_RANK else None


def _stated_conflict(value: str | None) -> bool:
    v = (value or "").strip().lower()
    # `<` marks an uninstantiated template placeholder, same as in bullets.
    return bool(v) and not v.rstrip(".").startswith("none") and "<" not in v


def _mine_key(m: Mined) -> tuple[bool, int]:
    return (not m.conflicts,
            _CONFIDENCE_RANK.get(m.confidence, len(_CONFIDENCE_RANK)))


def _strip_quotes(s: str) -> str:
    s = s.strip()
    for a, b in (('"', '"'), ("“", "”")):
        if len(s) > 1 and s.startswith(a) and s.endswith(b):
            return s[1:-1].strip()
    return s


def parse_inbox(text: str) -> tuple[list[Candidate], list[tuple[int, str]]]:
    """All candidates in file order, plus (lineno, message) for lines that
    carry a checkbox but don't parse — those must stay visible, never be
    silently dropped."""
    lines = text.splitlines()
    candidates: list[Candidate] = []
    problems: list[tuple[int, str]] = []
    fenced = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            fenced = not fenced
            i += 1
            continue
        m = None if fenced else CANDIDATE.match(line)
        if not m:
            i += 1
            continue
        start, rest = i, m.group(2)
        i += 1
        prov: list[str] = []
        while i < len(lines) and lines[i].strip() and lines[i][0] in " \t" \
                and not CANDIDATE.match(lines[i]):
            prov.append(lines[i].strip())
            i += 1
        parts = ARROW.split(rest)
        targets = [t for t in WIKILINK.findall(parts[-1]) if t.strip()] if len(parts) > 1 else []
        if not targets:
            problems.append((start + 1, f"no `→ [[target]]` in candidate: {rest!r}"))
            continue
        fact = _strip_quotes(" → ".join(parts[:-1]))
        candidates.append(Candidate(
            verdict=VERDICTS[m.group(1).lower()],
            fact=fact,
            target=targets[0].strip(),
            provenance=" ".join(prov),
            lines=(start, i),
        ))
    return candidates, problems


def _quoted_span(s: str) -> str | None:
    m = QUOTED.search(s)
    return (m.group(1) or m.group(2)).strip() if m else None


def _report_provenance(note) -> str:
    """The provenance line every mined candidate carries. The `via [[report]]`
    link doubles as the mined-already marker: sweep copies provenance into the
    receipt verbatim, so the marker outlives the candidate in inbox or ledger."""
    bits = []
    draft = next(iter(note.links("draft")), "")
    if draft:
        bits.append(f"from [[{draft}]]")
    sha = str(note.meta.get("pack_sha") or "")
    if sha and sha != "none":
        bits.append(f"pack {sha}")
    bits.append(f"via [[{note.name}]]")
    return "(" + ", ".join(bits) + ")"


def mine_report(note) -> list[Mined]:
    """Inbox-grammar candidate blocks lifted from one review report's
    `## Introduced candidates …` section (docs/RATIFICATION.md, build item 2).

    Every candidate lands pending — mining queues, only the writer decides.
    A bullet the reviewer routed (`→ [[node]]`) keeps its suggested route; an
    unrouted bullet is queued without an arrow, which every later sweep flags
    as a problem until the writer routes it — fail toward the writer looking.
    Reports state no confidence or conflicts, so their candidates sort after
    any proposal candidate that does (#1104).
    """
    title = next((t for t in note.section_titles()
                  if t.lower().startswith(CANDIDATE_SECTION)), None)
    if title is None:
        return []
    prov = _report_provenance(note)
    blocks: list[Mined] = []
    for line in (note.section(title) or "").splitlines():
        if not line.startswith("- "):
            continue
        text = line[2:].strip()
        # Skip empties, `- none`, and uninstantiated template placeholders.
        if not text or text.rstrip(".").lower() == "none" or "<" in text:
            continue
        parts = ARROW.split(text)
        targets = [t for t in WIKILINK.findall(parts[-1]) if t.strip()] if len(parts) > 1 else []
        if targets:
            lead = " → ".join(parts[:-1])
            fact = _quoted_span(lead) or _strip_quotes(lead)
            blocks.append(Mined(f'- [ ] "{fact}" → [[{targets[0].strip()}]]\n      {prov}'))
        else:
            fact = _quoted_span(text) or text
            blocks.append(Mined(f'- [ ] "{fact}"\n      {prov}'))
    return blocks


def _proposal_provenance(note) -> str:
    """The provenance line a mined proposal candidate carries. Same shape as a
    report's, so the receipt chain reads uniformly: source ore, the frozen
    mining pack sha, and the `via [[proposal]]` mined-already marker."""
    bits = []
    source = next(iter(note.links("source")), "")
    if source:
        bits.append(f"from [[{source}]]")
    sha = str(note.meta.get("mining_pack_sha") or "")
    if sha and sha != "none":
        bits.append(f"mining pack {sha}")
    bits.append(f"via [[{note.name}]]")
    return "(" + ", ".join(bits) + ")"


def mine_proposal(note) -> list[Mined]:
    """Inbox-grammar candidate blocks lifted from one fact proposal's
    `## Candidate facts` section (docs/RATIFICATION.md, build item 3).

    A proposal targets one node, so a candidate with no arrow of its own routes
    to the proposal's `target`; a candidate that names its own `→ [[node]]`
    keeps it (agents sometimes spot a fact that belongs elsewhere). Everything
    lands pending — the proposal is agent output, only the writer decides. The
    indented quote/confidence/conflicts lines stay in the proposal (the
    via-link points the writer back to them); they never ride into the inbox —
    but confidence and conflicts do key the mined batch's ordering (#1104)."""
    title = next((t for t in note.section_titles()
                  if t.lower().startswith(PROPOSAL_SECTION)), None)
    if title is None:
        return []
    prov = _proposal_provenance(note)
    default_target = next(iter(note.links("target")), "")
    rows: list[dict] = []
    current: dict | None = None
    for line in (note.section(title) or "").splitlines():
        if not line.startswith("- "):
            # A detail line belongs to the candidate above it; details under a
            # skipped bullet (placeholder, `- none`) attach to nothing.
            d = DETAIL.match(line)
            if d and current is not None:
                current[d.group(1)] = d.group(2)
            continue
        current = None
        text = line[2:].strip()
        if not text or text.rstrip(".").lower() == "none" or "<" in text:
            continue
        parts = ARROW.split(text)
        targets = [t for t in WIKILINK.findall(parts[-1]) if t.strip()] if len(parts) > 1 else []
        if targets:
            lead = " → ".join(parts[:-1])
            fact = _quoted_span(lead) or _strip_quotes(lead)
            block = f'- [ ] "{fact}" → [[{targets[0].strip()}]]\n      {prov}'
        elif default_target:
            fact = _quoted_span(text) or _strip_quotes(text)
            block = f'- [ ] "{fact}" → [[{default_target}]]\n      {prov}'
        else:
            fact = _quoted_span(text) or _strip_quotes(text)
            block = f'- [ ] "{fact}"\n      {prov}'
        current = {"block": block}
        rows.append(current)
    return [Mined(block=r["block"],
                  conflicts=_stated_conflict(r.get("conflicts")),
                  confidence=_stated_confidence(r.get("confidence")))
            for r in rows]


def mine(vault, inbox_text: str, ledger_text: str) -> tuple[list[str], list[str]]:
    """(candidate blocks to append to the inbox, names of artifacts mined).

    Both review reports and fact proposals propose canon; each is mined by its
    own extractor into the same pending inbox grammar. An artifact already
    wikilinked from the inbox or the ledger was mined before and is skipped —
    idempotency by artifact content, nothing stored. A proposal folded into a
    merge (named in some proposal's `reconciles:`) is skipped too: its
    candidates ride the merge proposal, never the sibling.

    The fresh batch is ordered for the writer's attention (#1104):
    conflicts-flagged first, then confidence descending, ties in artifact
    order (stable sort). Ordering is presentation only — it applies to the
    newly mined blocks alone (the caller appends; candidates already sitting
    in the inbox are never reordered under the writer's cursor), and the
    checkbox stays the sole verdict."""
    seen = {t.strip() for text in (inbox_text, ledger_text)
            for t in WIKILINK.findall(text) if t.strip()}
    for p in vault.by_type("fact_proposal"):
        seen.update(s.strip() for s in p.links("reconciles"))
    mined: list[Mined] = []
    names: list[str] = []
    for artifact_type, extract in (("review_report", mine_report),
                                   ("fact_proposal", mine_proposal)):
        for a in sorted(vault.by_type(artifact_type), key=lambda n: n.name):
            if a.name in seen:
                continue
            got = extract(a)
            if got:
                mined += got
                names.append(a.name)
    return [m.block for m in sorted(mined, key=_mine_key)], names


def receipt(c: Candidate) -> str:
    """Ledger entry text: the verdict wording, the route, and the provenance
    carried verbatim — the writer types none of it."""
    prov = f" {c.provenance}" if c.provenance else ""
    route = "→ promoted to" if c.verdict == "accept" else "→"
    return f'"{c.fact}" {route} [[{c.target}]]{prov}'


def append_bullets(text: str, section: str, bullets: list[str]) -> str:
    """Raw note text with bullets appended at the tail of `## section`.

    Every byte outside the section survives untouched (frontmatter included —
    this operates on the file, not the parsed body). Stub placeholders
    (`_(none …)_`) are dropped: their one job ends with the first real fact,
    and leaving one behind would make status read the node as a stub forever.
    """
    matches = list(HEADING.finditer(text))
    for i, m in enumerate(matches):
        if m.group(1).strip().lower() == section.lower():
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            seg = text[start:end].splitlines()
            seg = [l for l in seg if not l.strip().startswith("_(none")]
            while seg and not seg[-1].strip():
                seg.pop()
            if not seg or seg[0].strip():  # keep the newline after the heading
                seg.insert(0, "")
            seg += [f"- {b}" for b in bullets]
            tail = "\n\n" if end < len(text) else "\n"
            return text[:start] + "\n".join(seg) + tail + text[end:]
    raise ValueError(f"no `## {section}` section")


def remove_candidates(text: str, swept: list[Candidate]) -> str:
    """Inbox text with the swept candidates' line spans removed; everything
    else — header, pending candidates, the writer's own notes — is preserved
    byte-for-byte."""
    drop = {n for c in swept for n in range(*c.lines)}
    lines = [l for n, l in enumerate(text.splitlines()) if n not in drop]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
