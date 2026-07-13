"""The mining-pack assembler (#1092): the extraction analog of the context pack.

The contract under test: a mining pack freezes exactly the slice an independent
agent needs to propose facts *against* canon rather than beside it — hard
constraints, the target node's own facts and open questions, every other
ratified fact in the project, and the source ore — hashed for audit, stable
across regenerations, and refusing a non-node target or a missing source.
"""
import hashlib
from pathlib import Path

import pytest

from scribectl.core.miningpack import build_mining_pack, build_reconciliation_pack
from scribectl.core.vault import Note, Vault


def test_pack_pulls_the_extraction_slice(vault, fiction):
    mp = build_mining_pack(vault, "Mara Vey", "World Seed", fiction)
    md = mp.markdown
    # World seed hard constraints frame the mining.
    assert "## World spine — hard constraints" in md
    assert "administratively real" in md
    # The target node: its function, its already-ratified facts (do not
    # re-propose), and its open questions (the fill targets).
    assert "## Target node — Mara Vey" in md
    assert "Works the lower terraces" in md
    assert "**Open questions (fill targets)**" in md
    assert "What does she want" in md
    # Every *other* node's ratified facts — propose against them, not beside.
    assert "## Existing canon across the project" in md
    assert "### The Mist" in md and "The Mist is not weather" in md
    assert "### The Volcanic City-State" in md
    # The target is shown once (under 'Target node'), never duplicated below.
    assert "### Mara Vey" not in md
    # The source ore, verbatim body.
    assert "## Source ore — World Seed" in md
    assert "A fortified volcanic city-state" in md


def test_pack_is_sha_stable_and_self_certifying(vault, fiction):
    a = build_mining_pack(vault, "Mara Vey", "World Seed", fiction)
    b = build_mining_pack(vault, "Mara Vey", "World Seed", fiction)
    assert a.markdown == b.markdown and a.sha == b.sha
    stripped = a.markdown.replace(f"`mining-pack-sha: {a.sha}`\n\n", "", 1)
    assert hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:12] == a.sha


def test_stub_target_says_so(vault, fiction):
    """A stub node (the motivating case) mines with an empty 'already ratified'
    block — the whole point is to fill it."""
    # The Volcanic City-State is seeded; build a stub in-memory to be explicit.
    stub = Note(path=Path("world/canon/Empty Node.md"),
                meta={"type": "canon_node"},
                body="## One-line function\nTBD\n\n## Ratified facts\n"
                     "_(none ratified yet — node is a stub)_\n\n## Open questions\n- everything\n")
    src = Note(path=Path("sources/Ore.md"), meta={"type": "source"}, body="Raw ore text.\n")
    seed = vault.notes["World Seed"]
    v = Vault(root=Path("."), notes={"Empty Node": stub, "Ore": src, "World Seed": seed})
    md = build_mining_pack(v, "Empty Node", "Ore", fiction).markdown
    assert "_(none — this node is a stub)_" in md
    assert "Raw ore text." in md


def test_rejects_non_node_target_and_missing_source(vault, fiction):
    with pytest.raises(ValueError, match="fact-bearing node"):
        build_mining_pack(vault, "Scene 01-01", "World Seed", fiction)  # a card, not a node
    with pytest.raises(ValueError, match="No note named"):
        build_mining_pack(vault, "Mara Vey", "No Such Ore", fiction)


# -- reconciliation packs (docs/RATIFICATION.md, build item 4) -----------------

def _sibling(name, source, cands, sha="aaa111aaa111"):
    return Note(path=Path(f"control/proposals/{name}.md"),
                meta={"type": "fact_proposal", "target": "[[Mara Vey]]",
                      "source": f"[[{source}]]", "mining_pack_sha": sha},
                body=f"## Candidate facts\n{cands}")


def test_reconciliation_pack_lays_siblings_side_by_side(vault, fiction):
    b = _sibling("Mara Vey — B", "Ore B",
                 '<!-- scaffold guidance for the miner -->\n- "Fact from B"\n', sha="bbb222bbb222")
    a = _sibling("Mara Vey — A", "Ore A", "")
    rp = build_reconciliation_pack(vault, "Mara Vey", [b, a], fiction)
    md = rp.markdown
    # The same frame a mining pack gives: constraints + the target node.
    assert "## World spine — hard constraints" in md
    assert "## Target node — Mara Vey" in md
    # One section per sibling, name-sorted regardless of call order, each
    # heading carrying the sibling's source and frozen mining-pack sha.
    ha = md.index("## Proposal [[Mara Vey — A]] — source [[Ore A]], mining pack aaa111aaa111")
    hb = md.index("## Proposal [[Mara Vey — B]] — source [[Ore B]], mining pack bbb222bbb222")
    assert ha < hb
    assert '- "Fact from B"' in md
    # Empty candidate sets say so; scaffold comments are the miner's, not the
    # reconciler's, and never ride into the pack.
    assert "_(no candidates)_" in md
    assert "<!--" not in md
    assert rp.source == "reconciliation"


def test_reconciliation_pack_is_sha_stable_and_rejects_non_node(vault, fiction):
    sibs = [_sibling("Mara Vey — A", "Ore A", '- "A fact"\n')]
    a = build_reconciliation_pack(vault, "Mara Vey", sibs, fiction)
    b = build_reconciliation_pack(vault, "Mara Vey", sibs, fiction)
    assert a.markdown == b.markdown and a.sha == b.sha
    stripped = a.markdown.replace(f"`reconciliation-pack-sha: {a.sha}`\n\n", "", 1)
    assert hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:12] == a.sha
    with pytest.raises(ValueError, match="fact-bearing node"):
        build_reconciliation_pack(vault, "Scene 01-01", sibs, fiction)  # a card


def test_empty_source_warns():
    from scribectl.templateset import load_set
    node = Note(path=Path("world/canon/N.md"), meta={"type": "canon_node"},
                body="## Ratified facts\n- a\n")
    empty = Note(path=Path("sources/E.md"), meta={"type": "source"}, body="   \n")
    v = Vault(root=Path("."), notes={"N": node, "E": empty})
    mp = build_mining_pack(v, "N", "E", load_set("fiction"))
    assert any("no body to mine" in w for w in mp.warnings)
