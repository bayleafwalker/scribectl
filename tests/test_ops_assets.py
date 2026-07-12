"""Structural checks for the shipped editor/Obsidian surfaces (#1088, #1090).

There is no Obsidian or VS Code in this repo's test loop, so these assets can't
be run here the way the CLI is. What is machine-checkable — the configs are
well-formed, they reference files that actually exist, and the JS parses — is
checked; the behavioral truth lives in `scribectl` itself (see each README).
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
QUICKADD = REPO / "ops" / "obsidian" / "quickadd"
VSCODE = REPO / "ops" / "vscode"


# -- 1088 QuickAdd ----------------------------------------------------------

def test_quickadd_choices_is_valid_json_with_four_choices():
    data = json.loads((QUICKADD / "quickadd-choices.json").read_text(encoding="utf-8"))
    names = [c["name"] for c in data["choices"]]
    assert names == ["Jot inbox candidate", "New canon node",
                     "New mechanic node", "New card + contract"]


def test_quickadd_choices_reference_existing_files():
    data = json.loads((QUICKADD / "quickadd-choices.json").read_text(encoding="utf-8"))
    for c in data["choices"]:
        for key in ("templatePath", "userScript"):
            if key in c:
                assert (REPO / c[key]).is_file(), f"{c['name']}: missing {c[key]}"


def test_quickadd_node_templates_carry_type_and_name_slot():
    canon = (QUICKADD / "templates" / "canon-node.qa.md").read_text(encoding="utf-8")
    assert "type: canon_node" in canon and "# {{VALUE:name}}" in canon
    mech = (QUICKADD / "templates" / "mechanic-node.qa.md").read_text(encoding="utf-8")
    assert "type: mechanic_node" in mech and "# {{VALUE:name}}" in mech


def test_quickadd_card_script_delegates_not_reimplements():
    """The card button must bridge to the tested CLI, never fork the scaffold."""
    js = (QUICKADD / "scripts" / "new-card.js").read_text(encoding="utf-8")
    assert 'module.exports' in js
    assert '"new", "card"' in js and "execFile" in js
    # A re-implementation would wire the contract itself (output_target,
    # contract_id) — the bridge must not; it shells out for exactly that reason.
    assert "output_target" not in js and "contract_id" not in js


@pytest.mark.skipif(shutil.which("node") is None, reason="node not available")
def test_quickadd_card_script_parses():
    js = QUICKADD / "scripts" / "new-card.js"
    r = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
