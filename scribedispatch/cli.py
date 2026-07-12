"""scribe-dispatch — plan and run the automatic agentic mode.

`plan` prints what would fire and why (including why not); `run` executes it:
freeze pack → render skill → runner → land artifact with the sha receipt.
`watch` repeats `run` on an interval, but only when the vault has been quiet
for the settle window — livesync delivers notes as bursts of file writes, and
a half-synced note must never dispatch. No retries-with-feedback anywhere —
a bad draft is information for the writer, not fuel for the coordinator
(docs/DISPATCH.md).
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
import time
from pathlib import Path

import yaml

from . import DispatchError
from . import engine, landing, skills
from .policy import Dispatch, plan as plan_dispatches
from .runner import make_runner
from .vaultio import (contract_for, find_note, load_contracts, pack_for_sha,
                      read_note, verify_pack)


def _read(path: Path, missing: str) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else missing


def execute(d: Dispatch, state: dict, contracts: dict, runner) -> Path:
    model = runner.model
    proj = state["project"]
    root = Path(proj["root"])
    if d.skill == "body_fill":
        contract = contract_for(contracts, root, d.card)
        pack_path = engine.freeze_pack(d.card, proj["name"])
        sha = verify_pack(pack_path)
        prompt = skills.render(
            "body_fill",
            card_name=d.card,
            card_text=find_note(root, d.card).read_text(encoding="utf-8"),
            contract_text=contract["_text"],
            pack_path=str(pack_path),
            pack_text=pack_path.read_text(encoding="utf-8"),
        )
        out = runner.generate("body_fill", prompt)
        return landing.land_draft(root, d.card, contract, out, sha, runner.name, model)

    # review_canon / review_voice
    draft_path = find_note(root, d.draft)
    meta, _ = read_note(draft_path)
    sha = str(meta.get("pack_sha") or "") or None
    pack_path = pack_for_sha(Path(proj["paths"]["pack_output"]), sha) if sha else None
    if sha and pack_path:
        verify_pack(pack_path)
    pack_text = (pack_path.read_text(encoding="utf-8") if pack_path
                 else "(no frozen pack recorded for this draft — review against the oracle alone)")
    common = dict(card_name=d.card, draft_name=d.draft,
                  draft_text=draft_path.read_text(encoding="utf-8"))
    if d.kind == "canon":
        prompt = skills.render("review_canon", pack_path=str(pack_path or "none"),
                               pack_text=pack_text,
                               timeline_text=_read(Path(proj["paths"]["timeline"]),
                                                   "(no timeline)"), **common)
    elif d.kind == "mechanics":
        # The pack briefs the in-scope mechanic nodes — it IS the rulebook.
        prompt = skills.render("review_mechanics", pack_path=str(pack_path or "none"),
                               pack_text=pack_text, **common)
    else:
        prompt = skills.render("review_voice",
                               voice_canon_text=_read(Path(proj["paths"]["voice_canon"]),
                                                      "(no voice canon)"), **common)
    out = runner.generate(d.skill, prompt)
    return landing.land_review(root, d.card, d.kind, d.draft, out, sha, runner.name, model)


def last_change(root: Path) -> float:
    """Newest mtime under the project root, directories included — a deletion
    only shows on its parent dir."""
    return max((p.stat().st_mtime for p in itertools.chain([root], root.rglob("*"))
                if p.is_file() or p.is_dir()), default=0.0)


def _run_once(args, runners: "RunnerPool", chatty: bool = True) -> None:
    """One dispatch pass. The follow-up iteration exists only so reviews fire
    on drafts this pass just landed — never a second fill, never iteration."""
    first = True
    while True:
        state = engine.status(args.project)
        contracts = load_contracts(Path(state["project"]["root"]))
        dispatches, notes = plan_dispatches(state, contracts, only_card=args.card)
        if first:
            if chatty:
                for note in notes:
                    print(f"  - {note}")
        else:
            dispatches = [d for d in dispatches if d.skill.startswith("review_")]
        if not dispatches:
            if first and chatty:
                print("nothing to dispatch")
            return
        filled = False
        for d in dispatches:
            runner = runners.for_skill(d.skill)
            print(f"dispatching {d.skill} for {d.card} [{runner.name}] — {d.reason}")
            path = execute(d, state, contracts, runner)
            print(f"  landed {path}")
            filled = filled or d.skill == "body_fill"
        if not filled:
            return
        first = False


def _watch(args, runners: "RunnerPool") -> int:
    """Poll-and-pass loop. A tick where the vault changed inside the settle
    window dispatches nothing — wait out the livesync burst and let the next
    tick look again. Errors are not survived: a dead watch is visible, a watch
    that silently skips failures is not. `--ticks 1` is the systemd-timer /
    cron shape (one debounced pass, exit 0 either way)."""
    root = Path(engine.status(args.project)["project"]["root"])
    tick = 0
    while args.ticks is None or tick < args.ticks:
        if tick:
            time.sleep(args.interval)
        tick += 1
        quiet = time.time() - last_change(root)
        if quiet < args.settle:
            print(f"[watch] vault changed {quiet:.0f}s ago (settle {args.settle:.0f}s) — "
                  "waiting for livesync to finish")
            continue
        _run_once(args, runners, chatty=False)
    return 0


def _config() -> dict:
    p = Path.home() / ".config" / "scribectl" / "dispatch.yaml"
    if p.is_file():
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return cfg if isinstance(cfg, dict) else {}
    return {}


class RunnerPool:
    """Per-skill runner routing (backlog item 1076). Backend choice stays
    machine policy: an explicit --runner (or env) pins one backend for the
    whole pass — that's how the bake-off harness forces a model — otherwise
    the config's `skills:` map routes each skill (frontier reviews + local
    fills, say) and the top-level keys are the fallback."""

    def __init__(self, args, cfg: dict):
        self._cli_runner = args.runner or os.environ.get("SCRIBE_DISPATCH_RUNNER")
        self._cli_model = args.model or os.environ.get("SCRIBE_DISPATCH_MODEL")
        self._cli_base = args.base_url or os.environ.get("SCRIBE_DISPATCH_BASE_URL")
        self._fake_dir = args.fake_dir or os.environ.get("SCRIBE_DISPATCH_FAKE_DIR")
        self._cfg = cfg
        self._skills = cfg.get("skills") if isinstance(cfg.get("skills"), dict) else {}
        self._cache: dict[tuple, object] = {}

    def route(self, skill: str) -> tuple[str | None, str | None, str | None]:
        per = self._skills.get(skill) if isinstance(self._skills.get(skill), dict) else {}
        if self._cli_runner:
            per = {}  # explicit invocation overrides the routing map entirely
        name = (self._cli_runner or per.get("runner")
                or self._cfg.get("runner") or "claude")
        model = self._cli_model or per.get("model") or self._cfg.get("model")
        base_url = self._cli_base or per.get("base_url") or self._cfg.get("base_url")
        return name, model, base_url

    def for_skill(self, skill: str):
        key = self.route(skill)
        if key not in self._cache:
            name, model, base_url = key
            self._cache[key] = make_runner(name, model=model, base_url=base_url,
                                           fake_dir=self._fake_dir)
        return self._cache[key]

    def describe(self, skill: str) -> str:
        name, model, _ = self.route(skill)
        return f"{name}:{model}" if model else name


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="scribe-dispatch",
                                 description="automatic agentic mode: fire fill + reviews from derived state")
    ap.add_argument("command", choices=["plan", "run", "watch"])
    ap.add_argument("-p", "--project")
    ap.add_argument("--card", help="restrict to one card")
    ap.add_argument("--runner", help="claude | openai | fake (default: config, env, then claude)")
    ap.add_argument("--model")
    ap.add_argument("--base-url", help="openai runner endpoint, e.g. http://127.0.0.1:8080")
    ap.add_argument("--fake-dir", help="fake runner canned-responses directory")
    ap.add_argument("--interval", type=float, default=60.0,
                    help="watch: seconds between polls (default: 60)")
    ap.add_argument("--settle", type=float, default=30.0,
                    help="watch: dispatch only after the vault has been quiet this long "
                         "(livesync debounce; default: 30)")
    ap.add_argument("--ticks", type=int,
                    help="watch: exit after N polls (timer/cron single-shot: --ticks 1)")
    args = ap.parse_args(argv)

    runners = RunnerPool(args, _config())

    try:
        if args.command == "plan":
            state = engine.status(args.project)
            contracts = load_contracts(Path(state["project"]["root"]))
            dispatches, notes = plan_dispatches(state, contracts, only_card=args.card)
            for note in notes:
                print(f"  - {note}")
            for d in dispatches:
                extra = f" (draft: {d.draft})" if d.draft else ""
                print(f"would dispatch {d.skill} for {d.card}{extra} "
                      f"[{runners.describe(d.skill)}] — {d.reason}")
            if any(d.skill == "body_fill" for d in dispatches):
                print("(reviews for landed fills fire in the same run)")
            if not dispatches:
                print("nothing to dispatch")
            return 0
        if args.command == "watch":
            return _watch(args, runners)
        _run_once(args, runners)
        return 0
    except DispatchError as e:
        print(f"scribe-dispatch: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
