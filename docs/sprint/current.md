SPRINT: 2026-S01-forge-core-overture  [active]
Goal:   Extract fertile-flames pipeline into the scribectl package and land Fertile Flames in the real vault (PLAN.md phases A-B, C as gate)
Dates:  2026-07-10 to 2026-07-24
ID:     401
Items:  17 total — 16 done, 0 active, 1 pending, 0 blocked

--- Track: engine ---
  health: 4 items — 4 done (100%), 0 active, 0 pending, 0 blocked (0%)
  [done    ] #1052  Extract pipeline/* into scribectl/core parameterized by ProjectConfig (no behavior changes)  (assignee: -)
  [done    ] #1053  Move fixture vault to fixtures/fertile-flames with a scribe-project note at its root  (assignee: -)
  [done    ] #1054  Implement config.py: discovery of type: scribe-project notes across vault roots  (assignee: -)
  [done    ] #1055  Contact tests: derived status matches fixture expectations; pack output sha-stable  (assignee: -)

--- Track: cli ---
  health: 4 items — 4 done (100%), 0 active, 0 pending, 0 blocked (0%)
  [done    ] #1056  Implement cli.py: projects, status, pack with -p/--project inference  (assignee: -)
  [done    ] #1057  Implement init: instantiate a Works/ subtree from the fiction template set + write the scribe-project note  (assignee: -)
  [done    ] #1058  Implement ratify (append-only ledger writer) and adopt (canon-node stub from legacy note)  (assignee: -)
  [done    ] #1069  Phase D: verdict inbox + ratify --sweep (parse control/ratification/Inbox.md checkboxes; execute fact append + receipt + inbox clear per verdict)  (assignee: claude-fable)

--- Track: vault ---
  health: 3 items — 3 done (100%), 0 active, 0 pending, 0 blocked (0%)
  [done    ] #1059  Land Fertile Flames in /media/Creative via scribectl init; list legacy saga notes under sources:  (assignee: -)
  [done    ] #1060  Adopt 2-3 load-bearing legacy notes as canon-node stubs; hand-ratify facts into the log  (assignee: -)
  [done    ] #1061  Livesync concurrency test: engine-created files while the vault is open on another device  (assignee: -)

--- Track: slice ---
  health: 1 items — 1 done (100%), 0 active, 0 pending, 0 blocked (0%)
  [done    ] #1062  Run the vertical slice in the synced vault: pack -> body_fill -> rework -> reviews -> ratify  (assignee: -)

--- Track: dispatch ---
  health: 5 items — 4 done (80%), 0 active, 1 pending, 0 blocked (0%)
  [done    ] #1070  Phase F.1: scribectl status --json — project header + rows + per-card drafts/reviews-by-lane (engine CLI as the dispatcher API)  (assignee: -)
  [done    ] #1071  Phase F.2: .agents/skills prompt contracts: body_fill, review_canon, review_voice (string.Template markdown; parsed output shape)  (assignee: -)
  [done    ] #1072  Phase F.3: scribedispatch package: policy + runner abstraction (claude CLI / openai-compat / fake) + sha-verified landing; scribe-dispatch plan|run  (assignee: -)
  [done    ] #1073  Phase F.4: contact tests: fake-runner end-to-end on disposable fixture vault; idempotent second pass; designated-dirs-only writes  (assignee: -)
  [pending ] #1074  Phase F.5: live smoke (operator-gated): claude backend fills Scene 01-01 in a scratch vault; reviews fire; writer judges the voice  (assignee: -)

Rendered: 2026-07-12T08:04:35Z
