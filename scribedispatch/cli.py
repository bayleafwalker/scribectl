"""scribe-dispatch — plan and run the automatic agentic mode.

`plan` prints what would fire and why (including why not); `run` executes it:
freeze pack → render skill → runner → land artifact with the sha receipt.
Single pass, no daemon, no retries-with-feedback — a bad draft is information
for the writer, not fuel for the coordinator (docs/DISPATCH.md).
"""
from __future__ import annotations

import argparse
import os
import sys
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


def execute(d: Dispatch, state: dict, contracts: dict, runner, model: str | None) -> Path:
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
    else:
        prompt = skills.render("review_voice",
                               voice_canon_text=_read(Path(proj["paths"]["voice_canon"]),
                                                      "(no voice canon)"), **common)
    out = runner.generate(d.skill, prompt)
    return landing.land_review(root, d.card, d.kind, d.draft, out, sha, runner.name, model)


def _config() -> dict:
    p = Path.home() / ".config" / "scribectl" / "dispatch.yaml"
    if p.is_file():
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return cfg if isinstance(cfg, dict) else {}
    return {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="scribe-dispatch",
                                 description="automatic agentic mode: fire fill + reviews from derived state")
    ap.add_argument("command", choices=["plan", "run"])
    ap.add_argument("-p", "--project")
    ap.add_argument("--card", help="restrict to one card")
    ap.add_argument("--runner", help="claude | openai | fake (default: config, env, then claude)")
    ap.add_argument("--model")
    ap.add_argument("--base-url", help="openai runner endpoint, e.g. http://127.0.0.1:8080")
    ap.add_argument("--fake-dir", help="fake runner canned-responses directory")
    args = ap.parse_args(argv)

    cfg = _config()
    runner_name = (args.runner or os.environ.get("SCRIBE_DISPATCH_RUNNER")
                   or cfg.get("runner") or "claude")
    model = args.model or os.environ.get("SCRIBE_DISPATCH_MODEL") or cfg.get("model")
    base_url = args.base_url or os.environ.get("SCRIBE_DISPATCH_BASE_URL") or cfg.get("base_url")

    try:
        runner = None
        first = True
        while True:
            state = engine.status(args.project)
            contracts = load_contracts(Path(state["project"]["root"]))
            dispatches, notes = plan_dispatches(state, contracts, only_card=args.card)
            if first:
                for note in notes:
                    print(f"  - {note}")
            else:
                # The follow-up pass exists only so reviews fire on drafts
                # this run just landed — never a second fill, never iteration.
                dispatches = [d for d in dispatches if d.skill.startswith("review_")]
            if args.command == "plan":
                for d in dispatches:
                    extra = f" (draft: {d.draft})" if d.draft else ""
                    print(f"would dispatch {d.skill} for {d.card}{extra} — {d.reason}")
                if any(d.skill == "body_fill" for d in dispatches):
                    print("(reviews for landed fills fire in the same run)")
                if not dispatches:
                    print("nothing to dispatch")
                return 0
            if not dispatches:
                if first:
                    print("nothing to dispatch")
                return 0
            if runner is None:
                runner = make_runner(runner_name, model=model, base_url=base_url,
                                     fake_dir=args.fake_dir or os.environ.get("SCRIBE_DISPATCH_FAKE_DIR"))
            filled = False
            for d in dispatches:
                print(f"dispatching {d.skill} for {d.card} [{runner.name}] — {d.reason}")
                path = execute(d, state, contracts, runner, model)
                print(f"  landed {path}")
                filled = filled or d.skill == "body_fill"
            if not filled:
                return 0
            first = False
    except DispatchError as e:
        print(f"scribe-dispatch: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
