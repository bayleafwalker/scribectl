"""scribectl doctor — writer-facing environment health check (#1084).

Read-only: probes, never repairs. Checks the four legs a writing session
stands on — commands on PATH, vault roots, per-project designated dirs and
ledgers, and the dispatch runners' reachability (including "is vllm-writer
up", now that fills route to the local endpoint). The one network call is a
GET /v1/models against openai-routed endpoints; no prompt ever leaves this
module — health is not inference, so the no-LLM-client invariant holds
(ARCHITECTURE.md invariant 5).

Route resolution mirrors scribedispatch.cli.RunnerPool deliberately without
importing it: the engine package never imports the dispatch package; the
shared truth is the config file format.
"""
from __future__ import annotations

import json
import os
import shutil
import urllib.request
from pathlib import Path

import yaml

from .config import ProjectConfig, discover_projects, vault_roots
from .templateset import load_set

# Every skill the dispatcher can fire; grouped by resolved route for probing.
DISPATCH_SKILLS = ("body_fill", "review_canon", "review_voice", "review_mechanics")

INSTALL_HINT = "uv tool install --editable <path-to-scribectl-repo>"


class Report:
    """Collect (level, message) lines; FAIL is the only level that flips the
    exit code — warn means a session works but something will bite later."""

    def __init__(self):
        self.lines: list[tuple[str, str]] = []

    def ok(self, msg: str):
        self.lines.append(("ok", msg))

    def warn(self, msg: str):
        self.lines.append(("warn", msg))

    def fail(self, msg: str):
        self.lines.append(("FAIL", msg))

    @property
    def failed(self) -> bool:
        return any(lvl == "FAIL" for lvl, _ in self.lines)


def _root_source() -> str:
    if os.environ.get("SCRIBECTL_VAULT"):
        return "$SCRIBECTL_VAULT"
    cfg = Path.home() / ".config" / "scribectl" / "vaults"
    return str(cfg) if cfg.is_file() else "built-in default"


def _check_path(r: Report) -> None:
    for cmd in ("scribectl", "scribe-dispatch"):
        hit = shutil.which(cmd)
        if hit:
            r.ok(f"{cmd} on PATH: {hit}")
        else:
            r.warn(f"{cmd} not on PATH — install with `{INSTALL_HINT}` "
                   "so nobody types .venv/bin/ again")


def _check_vault(r: Report) -> list[Path]:
    roots = vault_roots()
    src = _root_source()
    live: list[Path] = []
    for root in roots:
        if root.is_dir():
            r.ok(f"vault root {root} ({src})")
            live.append(root)
        else:
            r.fail(f"vault root {root} does not exist ({src})")
    return live


def _check_project(r: Report, cfg: ProjectConfig) -> None:
    try:
        load_set(cfg.template_set)
    except ValueError as e:
        r.fail(f'project "{cfg.name}": {e}')
        return
    r.ok(f'project "{cfg.name}" ({cfg.template_set}) at {cfg.root}')
    if not os.access(cfg.root, os.W_OK):
        r.fail(f'  "{cfg.name}": project root not writable')
        return
    missing_dirs = [k for k, d in cfg.roots.items() if not d.is_dir()]
    if missing_dirs:
        r.warn(f'  "{cfg.name}": missing designated dirs: ' + ", ".join(missing_dirs))
    else:
        r.ok(f'  "{cfg.name}": designated dirs present '
             f'({", ".join(cfg.roots)}; pack output {cfg.pack_output.name}/)')
    if not cfg.ratification_log.is_file():
        r.warn(f'  "{cfg.name}": no ratification log at {cfg.ratification_log} '
               "— ratify will fail until it exists (init creates it)")
    if not cfg.ratification_inbox.is_file():
        r.ok(f'  "{cfg.name}": no inbox yet (created on first mine)')
    for label, p in (("voice canon", cfg.voice_canon), ("timeline", cfg.timeline)):
        if not p.is_file():
            r.warn(f'  "{cfg.name}": no {label} at {p} — reviews run degraded')
    contracts = cfg.root / "control" / "contracts"
    if not (contracts.is_dir() and any(contracts.glob("*.md"))):
        r.warn(f'  "{cfg.name}": no contracts under control/contracts/ — '
               "nothing is dispatchable (scribectl new card scaffolds one)")


def _dispatch_config() -> tuple[Path, dict | None]:
    p = Path.home() / ".config" / "scribectl" / "dispatch.yaml"
    if not p.is_file():
        return p, None
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return p, cfg if isinstance(cfg, dict) else {}


def _route(cfg: dict, skill: str) -> tuple[str, str | None, str | None]:
    """(runner, model, base_url) — same precedence as RunnerPool.route:
    env pin beats the per-skill map beats the top-level keys beats claude."""
    skills = cfg.get("skills") if isinstance(cfg.get("skills"), dict) else {}
    per = skills.get(skill) if isinstance(skills.get(skill), dict) else {}
    env_runner = os.environ.get("SCRIBE_DISPATCH_RUNNER")
    if env_runner:
        per = {}
    name = env_runner or per.get("runner") or cfg.get("runner") or "claude"
    model = os.environ.get("SCRIBE_DISPATCH_MODEL") or per.get("model") or cfg.get("model")
    base = os.environ.get("SCRIBE_DISPATCH_BASE_URL") or per.get("base_url") or cfg.get("base_url")
    return name, model, base


def _probe_openai(base_url: str, timeout: float = 3.0) -> tuple[bool, str]:
    url = base_url.rstrip("/") + "/v1/models"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        served = ", ".join(m.get("id", "?") for m in data.get("data", []))
        return True, served or "no models listed"
    except Exception as e:  # any failure mode reads the same to the writer
        return False, str(e)


def _check_runners(r: Report) -> None:
    path, cfg = _dispatch_config()
    if cfg is None:
        r.ok(f"no dispatch config at {path} — every skill routes to claude")
        cfg = {}
    else:
        r.ok(f"dispatch config {path}")
    by_route: dict[tuple[str, str | None, str | None], list[str]] = {}
    for skill in DISPATCH_SKILLS:
        by_route.setdefault(_route(cfg, skill), []).append(skill)
    for (name, model, base), skills in by_route.items():
        label = ", ".join(skills)
        if name == "claude":
            hit = shutil.which("claude")
            if hit:
                r.ok(f"runner claude ({label}): CLI at {hit} — auth not probed, "
                     "a failed dispatch will say so loudly")
            else:
                r.fail(f"runner claude ({label}): claude CLI not on PATH")
        elif name == "openai":
            if not base:
                r.fail(f"runner openai ({label}): no base_url configured")
                continue
            up, detail = _probe_openai(base)
            if up:
                r.ok(f"runner openai ({label}): {base} up, serving {detail}")
            else:
                r.warn(f"runner openai ({label}): {base} down ({detail}) — "
                       "these skills fail until the endpoint starts "
                       "(systemctl --user start vllm-writer)")
        elif name == "fake":
            r.ok(f"runner fake ({label}): canned responses, nothing to probe")
        else:
            r.warn(f"runner {name!r} ({label}): unknown to doctor "
                   f"(model {model or 'default'})")


def run_doctor() -> int:
    r = Report()
    _check_path(r)
    live_roots = _check_vault(r)
    projects = discover_projects(live_roots) if live_roots else []
    if live_roots and not projects:
        r.warn("no projects found — scribectl init <name> starts one")
    for p in projects:
        _check_project(r, p)
    _check_runners(r)
    width = max(len(lvl) for lvl, _ in r.lines)
    for lvl, msg in r.lines:
        print(f"{lvl:<{width}}  {msg}")
    if r.failed:
        print("\ndoctor: problems found (FAIL lines above)")
        return 1
    print("\ndoctor: healthy" + (" (warnings above)" if any(
        lvl == "warn" for lvl, _ in r.lines) else ""))
    return 0
