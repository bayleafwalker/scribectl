SPRINT: 2026-S00-cairn-backlog  [planned]
Goal:   Backlog cairn: Phase D/E/F items waiting for their gates
ID:     403
Items:  30 total — 23 done, 0 active, 7 pending, 0 blocked

--- Track: dispatch ---
  health: 13 items — 10 done (76%), 0 active, 3 pending, 0 blocked (0%)
  [done    ] #1075  Local writer backend: vllm-writer.service + writer.env on the RTX 3090 (reuse vllm-devstral pattern); model bake-off (Mistral Small 24B / Gemma 3 27B / writing finetunes) judged via review_voice against the Prose Voice Canon  (assignee: -)
  [done    ] #1076  Per-skill runner routing in dispatch.yaml (e.g. frontier reviews + local fills) — after two real backends exist  (assignee: -)
  [pending ] #1077  codex CLI backend for scribedispatch (runner abstraction already vendor-neutral) — when codex is installed  (assignee: -)
  [done    ] #1078  Watch mode: scribe-dispatch watch or systemd timer; livesync debounce so half-synced notes never dispatch  (assignee: -)
  [done    ] #1079  Candidate mining: parse 'Introduced candidates' from landed review reports into the ratification Inbox as pending candidates (RATIFICATION.md reconciler track)  (assignee: -)
  [done    ] #1080  Real-vault enablement: scribe-dispatch against Fertile Flames in /media/Creative — only after F.4 tests and the F.5 smoke both hold (operator-gated)  (assignee: -)
  [done    ] #1081  Gamedev set dispatch: kind-parameterized output cards + reviews/mechanics lane for Runosong fixture, then live project  (assignee: -)
  [pending ] #1082  refactor skill: paragraph-level, constraints in, new file out (never edits in place)  (assignee: -)
  [done    ] #1083  agentops integration: scribectl.dispatch.json manifest + cockpit visibility for dispatch runs (observability only)  (assignee: -)
  [done    ] #1094  brainstorm skill: ideation session contract — quarantined output under control/proposals/, candidates ride the mine/propose path into the inbox; never canon, never cited by packs  (assignee: -)
  [pending ] #1097  First routed real fill: card+contract in a live project, vllm-writer up, dispatch lands a local fill + frontier reviews end-to-end (operator-gated: writer authors and judges)  (assignee: -)
  [done    ] #1100  Variant fills: fill a card N ways in one pass (per-variant runner/temperature routes from the routing map), land as draft variants, writer picks — independence + human verdict, never agent-on-agent iteration (the bake-off pattern as a dispatch policy knob)  (assignee: -)
  [done    ] #1101  Ambient candidate flow: watch invokes engine ratify --mine after reviews land — dispatcher still never parses reports or touches the inbox (engine CLI is its API); decide and document the invoke-vs-do line in DISPATCH.md  (assignee: -)

--- Track: surfaces ---
  health: 10 items — 9 done (90%), 0 active, 1 pending, 0 blocked (0%)
  [done    ] #1084  Install story: uv tool install puts scribectl + scribe-dispatch on PATH on both devices; scribectl doctor checks vault root, project discovery, designated write dirs, runner auth — the writer never types .venv/bin/  (assignee: -)
  [done    ] #1085  scribectl next: writer-facing next-actions digest (ready cards, unconsumed reviews, undecided inbox candidates, unrouted/mined candidates, open proposals), printed and embedded atop Status.md — 'where the next ten minutes go' as a first-class surface  (assignee: -)
  [done    ] #1086  scribectl new card <name>: scaffold a scene/output card + its dispatch contract in one motion (contract authoring is intent; one command, no hand-copied frontmatter) — unblocks 'everything ready_for_fill has a contract'  (assignee: -)
  [done    ] #1087  scribectl capture: paste/pipe a raw design dialogue or brainstorm transcript into a dated source note under the project + sources: registration — raw ore is never lost again (the Runosong raw-dialogue gap, generalized)  (assignee: -)
  [done    ] #1088  QuickAdd capture configs (Phase D bullet): new card+contract, new canon/mechanic node, jot an inbox candidate — in-Obsidian buttons; the writer never meets a shell  (assignee: -)
  [done    ] #1089  Vault-side agent guidance: init drops an agents note (engine rules for any console agent opened inside the vault — never ratify, candidates via inbox, cite pack shas, designated dirs only); template per set  (assignee: -)
  [done    ] #1090  VS Code surface: workspace + tasks.json template (status/pack/plan/run/sweep/watch tasks) shipped in docs — editor-agnostic console surface, explicitly no extension  (assignee: -)
  [done    ] #1091  systemd user units: scribe-dispatch-watch.timer (--ticks 1 single-shot pattern) + env file — ambient dispatch on the workstation; writer writes, fills land  (assignee: -)
  [pending ] #1098  AGENTS.md backfill for pre-1089 projects: safe refresh path (init --refresh or documented copy) so live Fertile Flames + Runosong get the vault agent-guidance note  (assignee: -)
  [done    ] #1102  In-Obsidian one-motion actions: Shell Commands / QuickAdd macros invoking scribectl (sweep, status --write, next) — ergonomics-only plugin roster extension per DESIGN.md, zero state in the plugin, desktop device only  (assignee: -)

--- Track: engine ---
  health: 4 items — 3 done (75%), 0 active, 1 pending, 0 blocked (0%)
  [done    ] #1092  Mining packs + scribectl propose + fact_proposal status rows (RATIFICATION.md build item 3): freeze-and-hash extraction packs; agents mine legacy ore into quarantined proposals; candidates land in the inbox  (assignee: -)
  [done    ] #1093  Reconciler pass (RATIFICATION.md build item 4): read sibling proposals targeting the same node, emit a merge proposal flagging overlaps/contradictions — gated on >=2 sources actually being mined  (assignee: -)
  [pending ] #1103  Beta pack: one-way sha-stamped manuscript render for beta readers (compile body/drafts + front matter, regenerable, read back by nothing) — the render-out lane, distinct from banned copy-out; coordinate with Longform (#1065)  (assignee: -)
  [done    ] #1104  Inbox verdict ergonomics: order/group candidates conflicts-first and by confidence at mine time — presentation only, the checkbox stays the sole verdict; threshold-accept refused by design (auto-ratify in a hat)  (assignee: -)

--- Track: repo ---
  health: 1 items — 1 done (100%), 0 active, 0 pending, 0 blocked (0%)
  [done    ] #1095  GitHub Actions CI: uv-based pytest workflow on push/PR + README badge — the public repo runs its own test suite  (assignee: -)

--- Track: vault ---
  health: 2 items — 0 done (0%), 0 active, 2 pending, 0 blocked (0%)
  [pending ] #1096  Runosong ore mining: writer authors/adopts target nodes, then propose from runolaulu-design-dialogue + agent fill + mine into inbox — first real-vault use of 1092/1093 (operator-gated: writer routes and sweeps)  (assignee: -)
  [pending ] #1099  Livesync ledger torture test: deliberately simultaneous appends to the same ratification ledger from both devices; document observed conflict behavior (operator-gated: needs both devices)  (assignee: -)

Rendered: 2026-07-13T11:57:37Z

========================================================================

SPRINT: 2026-S00-cairn-backlog  [planned]
Goal:   Backlog: PLAN.md phases D-E — conveniences and second project/template set. Pull from here only after the Phase C slice holds.
ID:     402
Items:  6 total — 3 done, 0 active, 3 pending, 0 blocked

--- Track: cli ---
  health: 1 items — 1 done (100%), 0 active, 0 pending, 0 blocked (0%)
  [done    ] #1063  status --write: emit generated control/Status.md dashboard  (assignee: -)

--- Track: vault ---
  health: 2 items — 1 done (50%), 0 active, 1 pending, 0 blocked (0%)
  [done    ] #1064  QuickAdd capture configs for instantiating artifact templates from inside Obsidian  (assignee: -)
  [pending ] #1065  Enable Longform for Fertile Flames; compile body/drafts to manuscript  (assignee: -)

--- Track: agents ---
  health: 1 items — 1 done (100%), 0 active, 0 pending, 0 blocked (0%)
  [done    ] #1066  Wire body_fill/review_canon/review_voice/refactor into .agents/skills dispatch  (assignee: -)

--- Track: expansion ---
  health: 2 items — 0 done (0%), 0 active, 2 pending, 0 blocked (0%)
  [pending ] #1067  Second fiction project: Sunstolen via scribectl init — stress multi-project discovery  (assignee: -)
  [pending ] #1068  essay/ template set + sources/claims pull spec  (assignee: -)

Rendered: 2026-07-13T11:57:38Z
