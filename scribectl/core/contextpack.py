"""Context-pack assembler — the engineering center of the whole system.

Given a card (the template set's fillable unit — a scene, an episode, a blog
post), assemble the *minimal* relevant canon bundle for a fill: the spine, the
card, the in-scope fact-bearing nodes (ratified facts only), the voice canon,
prior relevant timeline events, and hard exclusions. Whole-vault context
produces confident contradiction soup; this is the thing that keeps fills
consistent.

Which frontmatter fields are pulled, and which note types count as the card
and as fact-bearing nodes, comes from the project's TemplateSet — this module
stays shape-agnostic and never reads the manifests itself.

Dual identity, resolved explicitly:
  - regenerate to fill   (it's an impl-cache: rebuild fresh per draft)
  - freeze to audit      (the emitted file + content hash is the provenance
                          record of exactly what a given draft saw)
  - never hand-edit      (edit the canon, not the pack)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date

from .vault import Vault, Note
from .timeline import prior_relevant
from .project import canon_status, ledger_accepted


@dataclass
class ContextPack:
    card: str
    markdown: str
    sha: str
    warnings: list[str]


def _node_brief(note: Note) -> str:
    """A fact-bearing node contributes its one-line function + ratified facts only.
    Open questions / story utility are authoring scaffolding, not canon — excluded."""
    fn = note.section("One-line function")
    facts = note.section("Ratified facts")
    out = [f"### {note.name}"]
    if fn:
        out.append(fn.strip())
    out.append("**Ratified facts**")
    out.append(facts.strip() if facts else "_(none ratified yet — node is a stub)_")
    return "\n".join(out)


def build_pack(vault: Vault, card_name: str, ts) -> ContextPack:
    """ts is a TemplateSet (or anything with its shape attributes)."""
    card = vault.resolve(card_name)
    if card is None or card.type != ts.card_type:
        raise ValueError(f"No {ts.card_type} named {card_name!r}")

    m = card.meta
    if any(f in m for f in ts.position_fields):
        pos = tuple(int(m.get(f, 0)) for f in ts.position_fields)
    else:
        # A card that carries no position (a blog post, a research digest)
        # sits after everything: the whole timeline is prior and relevant.
        pos = (2**31,) * (len(ts.position_fields) or 3)

    # Resolve everything in scope by link.
    scope_links = list(dict.fromkeys(
        l for f in ts.scope_fields for l in card.links(f)
    ))
    nodes = [vault.resolve(l) for l in scope_links]
    nodes = [n for n in nodes if n is not None]
    missing = [l for l in scope_links if vault.resolve(l) is None]

    # Advisory only — packing is never gated, but the author should know when
    # in-scope facts ship without a ledger receipt behind them.
    accepted = ledger_accepted(vault)
    warnings: list[str] = []
    for n in nodes:
        if n.type not in ts.node_types:
            continue
        s = canon_status(vault, n, accepted)
        if s == "stub":
            warnings.append(f"[[{n.name}]] is a stub — it ships no facts")
        elif s == "seeded":
            warnings.append(f"[[{n.name}]] is seeded, not ratified — its facts ship without a ledger receipt")
        elif s == "ratified_empty":
            warnings.append(f"[[{n.name}]] is ledger-accepted but carries no facts — paste them into the node")

    actors = {a for f in ts.actor_fields for a in card.links(f)}
    location = ((card.links(ts.location_field) or [None])[0]
                if ts.location_field else None)

    events = prior_relevant(vault, pos, actors, location)

    seed = vault.one("world_seed")
    voice = vault.one("voice_canon")

    parts: list[str] = []
    parts.append(f"# Context Pack — {card_name}")
    parts.append(f"_Generated {date.today().isoformat()} · regenerate to fill, freeze to audit, never hand-edit._\n")

    if seed:
        spine = seed.section("Core premise") or ""
        cons = seed.section("Hard constraints") or ""
        parts.append("## World spine\n" + spine.strip() + ("\n\n**Hard constraints**\n" + cons.strip() if cons else ""))

    parts.append(f"## {ts.card_heading}\n" + card.body.strip())

    if nodes:
        parts.append("## Canon in scope\n" + "\n\n".join(_node_brief(n) for n in nodes))
    if missing:
        parts.append("## ⚠ Unresolved scope links\n"
                     + "\n".join(f"- [[{l}]] — referenced but no note exists" for l in missing))

    if events:
        lines = [f"- {e.pos_label} · {', '.join(e.actors) or 'global'} · {e.fact}" for e in events]
        parts.append("## Prior relevant events (timeline)\n" + "\n".join(lines))
    else:
        parts.append("## Prior relevant events (timeline)\n_(none recorded before this scene)_")

    if voice:
        pref = voice.section("Preferred") or ""
        avoid = voice.section("Avoid") or ""
        ex = voice.section("Exemplars") or ""
        block = "**Preferred**\n" + pref.strip() + "\n\n**Avoid**\n" + avoid.strip()
        if ex:
            block += "\n\n**Exemplars (cadence target)**\n" + ex.strip()
        parts.append("## Voice canon\n" + block)

    dont = card.section("Do not")
    if dont:
        parts.append("## Hard exclusions\n" + dont.strip())

    md = "\n\n".join(parts).strip() + "\n"
    sha = hashlib.sha256(md.encode("utf-8")).hexdigest()[:12]
    md = md.replace("_Generated", f"`pack-sha: {sha}`\n\n_Generated", 1)
    return ContextPack(card=card_name, markdown=md, sha=sha, warnings=warnings)
