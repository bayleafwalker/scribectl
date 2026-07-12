"""Mining-pack assembler — the extraction analog of the context pack.

Where `contextpack` freezes the minimal canon slice a *fill* reads, this freezes
the minimal slice a *mining* run reads: the source ore to extract facts from,
the target node's open questions (the fill targets), every fact already ratified
in the project (so an agent proposes against existing canon instead of beside
it), and the world seed's hard constraints. That scope is what keeps an
independent mining agent honest — it can see what is already true and what the
node still needs, so its candidates arrive routed and conflict-checked rather
than hallucinated (docs/RATIFICATION.md, "The propose stage").

Same identity as the context pack: regenerate to mine, freeze-and-hash to audit,
never hand-edit. The emitted sha chains provenance
`source → mining pack sha → proposal → verdict → node fact`.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date

from .vault import Vault, Note


@dataclass
class MiningPack:
    node: str
    source: str
    markdown: str
    sha: str
    warnings: list[str]


def _ratified(note: Note) -> str | None:
    """A node's ratified facts, or None if it ships none (stub / seeded-empty)."""
    facts = note.section("Ratified facts")
    if not facts or not facts.strip() or "_(none" in facts:
        return None
    return facts.strip()


def build_mining_pack(vault: Vault, node_name: str, source_name: str, ts) -> MiningPack:
    """ts is a TemplateSet (or anything with its shape attributes).

    The node must be a fact-bearing type (that is where mined facts can ever
    land); the source is any note whose body is the ore to mine."""
    node = vault.resolve(node_name)
    if node is None or node.type not in ts.node_types:
        raise ValueError(
            f"No fact-bearing node named {node_name!r} "
            f"(node types: {', '.join(ts.node_types)})")
    source = vault.resolve(source_name)
    if source is None:
        raise ValueError(f"No note named {source_name!r} to mine")

    warnings: list[str] = []
    if not source.body.strip():
        warnings.append(f"[[{source_name}]] has no body to mine")

    parts: list[str] = []
    parts.append(f"# Mining Pack — {node_name} ← {source_name}")
    parts.append(f"_Generated {date.today().isoformat()} · extract candidate facts "
                 "from the source into a fact proposal · never canon until ratified._\n")

    seed = vault.one("world_seed")
    if seed:
        cons = seed.section("Hard constraints") or ""
        if cons.strip():
            parts.append("## World spine — hard constraints\n" + cons.strip())

    fn = node.section("One-line function")
    oq = node.section("Open questions")
    here = _ratified(node)
    block = [f"## Target node — {node_name}"]
    if fn and fn.strip():
        block.append(fn.strip())
    block.append("**Already ratified here (do not re-propose)**")
    block.append(here if here else "_(none — this node is a stub)_")
    block.append("**Open questions (fill targets)**")
    block.append(oq.strip() if oq and oq.strip() else "_(none recorded)_")
    parts.append("\n".join(block))

    # Every other node's ratified facts: propose against existing canon, not
    # beside it. The target's own facts are shown above, so skip it here.
    others = []
    for n in sorted(vault.notes.values(), key=lambda x: x.name):
        if n.type not in ts.node_types or n.name == node_name:
            continue
        facts = _ratified(n)
        if facts:
            others.append(f"### {n.name}\n{facts}")
    if others:
        parts.append("## Existing canon across the project (propose against, not beside)\n"
                     + "\n\n".join(others))

    parts.append(f"## Source ore — {source_name}\n" + source.body.strip())

    md = "\n\n".join(parts).strip() + "\n"
    sha = hashlib.sha256(md.encode("utf-8")).hexdigest()[:12]
    md = md.replace("_Generated", f"`mining-pack-sha: {sha}`\n\n_Generated", 1)
    return MiningPack(node=node_name, source=source_name, markdown=md, sha=sha, warnings=warnings)
