SPRINT: 2026-S00-cairn-backlog  [planned]
Goal:   Backlog cairn: Phase D/E/F items waiting for their gates
ID:     403
Items:  20 total — 11 done, 0 active, 9 pending, 0 blocked

--- Track: dispatch ---
  health: 10 items — 7 done (70%), 0 active, 3 pending, 0 blocked (0%)
  [done    ] #1075  Local writer backend: vllm-writer.service + writer.env on the RTX 3090 (reuse vllm-devstral pattern); model bake-off (Mistral Small 24B / Gemma 3 27B / writing finetunes) judged via review_voice against the Prose Voice Canon  (assignee: -)
  [done    ] #1076  Per-skill runner routing in dispatch.yaml (e.g. frontier reviews + local fills) — after two real backends exist  (assignee: -)
  [pending ] #1077  codex CLI backend for scribedispatch (runner abstraction already vendor-neutral) — when codex is installed  (assignee: -)
  [done    ] #1078  Watch mode: scribe-dispatch watch or systemd timer; livesync debounce so half-synced notes never dispatch  (assignee: -)
  [done    ] #1079  Candidate mining: parse 'Introduced candidates' from landed review reports into the ratification Inbox as pending candidates (RATIFICATION.md reconciler track)  (assignee: -)
  [done    ] #1080  Real-vault enablement: scribe-dispatch against Fertile Flames in /media/Creative — only after F.4 tests and the F.5 smoke both hold (operator-gated)  (assignee: -)
  [done    ] #1081  Gamedev set dispatch: kind-parameterized output cards + reviews/mechanics lane for Runosong fixture, then live project  (assignee: -)
  [pending ] #1082  refactor skill: paragraph-level, constraints in, new file out (never edits in place)  (assignee: -)
  [done    ] #1083  agentops integration: scribectl.dispatch.json manifest + cockpit visibility for dispatch runs (observability only)  (assignee: -)
  [pending ] #1094  brainstorm skill: ideation session contract — quarantined output under control/proposals/, candidates ride the mine/propose path into the inbox; never canon, never cited by packs  (assignee: -)

--- Track: surfaces ---
  health: 8 items — 4 done (50%), 0 active, 4 pending, 0 blocked (0%)
  [done    ] #1084  Install story: uv tool install puts scribectl + scribe-dispatch on PATH on both devices; scribectl doctor checks vault root, project discovery, designated write dirs, runner auth — the writer never types .venv/bin/  (assignee: -)
  [done    ] #1085  scribectl next: writer-facing next-actions digest (ready cards, unconsumed reviews, undecided inbox candidates, unrouted/mined candidates, open proposals), printed and embedded atop Status.md — 'where the next ten minutes go' as a first-class surface  (assignee: -)
  [done    ] #1086  scribectl new card <name>: scaffold a scene/output card + its dispatch contract in one motion (contract authoring is intent; one command, no hand-copied frontmatter) — unblocks 'everything ready_for_fill has a contract'  (assignee: -)
  [pending ] #1087  scribectl capture: paste/pipe a raw design dialogue or brainstorm transcript into a dated source note under the project + sources: registration — raw ore is never lost again (the Runosong raw-dialogue gap, generalized)  (assignee: -)
  [pending ] #1088  QuickAdd capture configs (Phase D bullet): new card+contract, new canon/mechanic node, jot an inbox candidate — in-Obsidian buttons; the writer never meets a shell  (assignee: -)
  [pending ] #1089  Vault-side agent guidance: init drops an agents note (engine rules for any console agent opened inside the vault — never ratify, candidates via inbox, cite pack shas, designated dirs only); template per set  (assignee: -)
  [pending ] #1090  VS Code surface: workspace + tasks.json template (status/pack/plan/run/sweep/watch tasks) shipped in docs — editor-agnostic console surface, explicitly no extension  (assignee: -)
  [done    ] #1091  systemd user units: scribe-dispatch-watch.timer (--ticks 1 single-shot pattern) + env file — ambient dispatch on the workstation; writer writes, fills land  (assignee: -)

--- Track: engine ---
  health: 2 items — 0 done (0%), 0 active, 2 pending, 0 blocked (0%)
  [pending ] #1092  Mining packs + scribectl propose + fact_proposal status rows (RATIFICATION.md build item 3): freeze-and-hash extraction packs; agents mine legacy ore into quarantined proposals; candidates land in the inbox  (assignee: -)
  [pending ] #1093  Reconciler pass (RATIFICATION.md build item 4): read sibling proposals targeting the same node, emit a merge proposal flagging overlaps/contradictions — gated on >=2 sources actually being mined  (assignee: -)

Rendered: 2026-07-12T19:29:17Z
