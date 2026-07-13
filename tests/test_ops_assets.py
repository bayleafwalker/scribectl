"""Structural checks for the shipped editor/Obsidian surfaces (#1088, #1090)
and the brainstorm session contract (#1094).

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


# -- 1090 VS Code -----------------------------------------------------------

EXPECTED_TASKS = {
    "scribectl: next", "scribectl: status", "scribectl: doctor",
    "scribectl: pack card", "scribe-dispatch: plan", "scribe-dispatch: run",
    "scribectl: sweep (dry-run)", "scribe-dispatch: watch",
}


def _labels(tasks_block: dict) -> set[str]:
    return {t["label"] for t in tasks_block["tasks"]}


def test_vscode_tasks_json_is_valid_and_complete():
    data = json.loads((VSCODE / "tasks.json").read_text(encoding="utf-8"))
    assert data["version"] == "2.0.0"
    assert _labels(data) == EXPECTED_TASKS


def test_vscode_workspace_embeds_the_same_tasks():
    """The workspace file and tasks.json must not drift — one loop, two ways in."""
    ws = json.loads((VSCODE / "scribectl.code-workspace").read_text(encoding="utf-8"))
    assert _labels(ws["tasks"]) == EXPECTED_TASKS
    assert ws["folders"] == [{"path": "."}]


def test_vscode_sweep_task_is_dry_run_only():
    """Ratification is a human keystroke: no shipped task executes a real sweep."""
    for path in ("tasks.json", "scribectl.code-workspace"):
        raw = (VSCODE / path).read_text(encoding="utf-8")
        data = json.loads(raw)
        tasks = data["tasks"] if path.endswith(".json") else data["tasks"]["tasks"]
        sweeps = [t for t in tasks if "sweep" in t["label"]]
        assert sweeps and all("--dry-run" in t["args"] for t in sweeps)


# -- 1094 brainstorm skill ----------------------------------------------------

SKILLS = REPO / ".agents" / "skills"
TEMPLATES = REPO / "scribectl" / "templates"

# The exit protocol's command spine — the contract and both vault guides must
# name every step, or a session's output falls out of the loop.
EXIT_PROTOCOL = ["--kind brainstorm", "scribectl propose",
                 "control/proposals/", "ratify --mine"]


def test_brainstorm_contract_names_the_full_exit_protocol():
    text = (SKILLS / "brainstorm.md").read_text(encoding="utf-8")
    for step in EXIT_PROTOCOL:
        assert step in text, f"brainstorm.md misses exit-protocol step: {step}"
    # The verdict never belongs to the session agent.
    assert "checkbox" in text and "writer" in text


def test_brainstorm_contract_is_not_a_dispatch_prompt():
    """No dispatch pass fires a brainstorm — the contract must carry no
    string.Template placeholders a render() would demand values for."""
    from string import Template

    text = (SKILLS / "brainstorm.md").read_text(encoding="utf-8")
    assert Template(text).get_identifiers() == []


def test_vault_agent_guides_carry_the_brainstorm_protocol():
    for ts in ("fiction", "gamedev"):
        text = (TEMPLATES / ts / "agents.md").read_text(encoding="utf-8")
        assert "## Brainstorm sessions" in text, f"{ts}/agents.md misses the section"
        for step in EXIT_PROTOCOL:
            assert step in text, f"{ts}/agents.md misses exit-protocol step: {step}"
