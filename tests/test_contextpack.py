"""The assembler: minimal canon slice, frozen and hashed."""
import hashlib
import re

import pytest

from scribectl.core.contextpack import build_pack


def test_pack_is_sha_stable(vault, fiction):
    a = build_pack(vault, "Scene 01-01", fiction)
    b = build_pack(vault, "Scene 01-01", fiction)
    assert a.markdown == b.markdown
    assert a.sha == b.sha


def test_sha_is_receipt_for_content(vault, fiction):
    """The embedded pack-sha must equal the hash of the pack minus the sha line."""
    pack = build_pack(vault, "Scene 01-01", fiction)
    stripped = pack.markdown.replace(f"`pack-sha: {pack.sha}`\n\n", "", 1)
    assert hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:12] == pack.sha
    assert f"`pack-sha: {pack.sha}`" in pack.markdown


def test_pack_pulls_the_minimal_slice(vault, fiction):
    md = build_pack(vault, "Scene 01-01", fiction).markdown
    assert "## World spine" in md
    assert "## Scene card" in md
    assert "## Canon in scope" in md
    assert "## Prior relevant events (timeline)" in md
    assert "## Voice canon" in md
    assert "## Hard exclusions" in md
    # Ratified facts ship; authoring scaffolding never does.
    assert "The Mist is not weather" in md
    assert "What does the Mist want" not in md  # Open questions excluded
    assert "Story utility" not in md


def test_pack_flags_unresolved_scope(vault, fiction):
    md = build_pack(vault, "Scene 01-01", fiction).markdown
    assert "## ⚠ Unresolved scope links" in md
    assert "[[Lower Ashmarket]] — referenced but no note exists" in md


def test_pack_includes_prior_timeline_events(vault, fiction):
    md = build_pack(vault, "Scene 01-01", fiction).markdown
    assert "ration ledger" in md
    assert "officially recorded as contained" in md


def test_pack_rejects_unknown_scene(vault, fiction):
    with pytest.raises(ValueError):
        build_pack(vault, "Scene 99-99", fiction)
    with pytest.raises(ValueError):
        build_pack(vault, "The Mist", fiction)  # exists, but not a scene_card


def test_pack_matches_golden(vault, fixture_root, fiction):
    """Byte parity with the ff.py baseline, modulo the run date (and therefore
    the sha, which hashes the dated content)."""
    import pathlib

    golden = (pathlib.Path(__file__).parent / "golden" / "Scene-01-01-context.md").read_text(
        encoding="utf-8"
    )
    generated = build_pack(vault, "Scene 01-01", fiction).markdown

    def normalize(text: str) -> str:
        text = re.sub(r"`pack-sha: [0-9a-f]{12}`", "`pack-sha: XXX`", text)
        return re.sub(r"_Generated \d{4}-\d{2}-\d{2}", "_Generated DATE", text)

    assert normalize(generated) == normalize(golden)
