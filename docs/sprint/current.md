SPRINT: 2026-S01-forge-core-overture  [active]
Goal:   Extract fertile-flames pipeline into the scribectl package and land Fertile Flames in the real vault (PLAN.md phases A-B, C as gate)
Dates:  2026-07-10 to 2026-07-24
ID:     401
Items:  12 total — 1 done, 0 active, 11 pending, 0 blocked

--- Track: engine ---
  health: 4 items — 0 done (0%), 0 active, 4 pending, 0 blocked (0%)
  [pending ] #1052  Extract pipeline/* into scribectl/core parameterized by ProjectConfig (no behavior changes)  (assignee: -)
  [pending ] #1053  Move fixture vault to fixtures/fertile-flames with a scribe-project note at its root  (assignee: -)
  [pending ] #1054  Implement config.py: discovery of type: scribe-project notes across vault roots  (assignee: -)
  [pending ] #1055  Contact tests: derived status matches fixture expectations; pack output sha-stable  (assignee: -)

--- Track: cli ---
  health: 4 items — 1 done (25%), 0 active, 3 pending, 0 blocked (0%)
  [pending ] #1056  Implement cli.py: projects, status, pack with -p/--project inference  (assignee: -)
  [pending ] #1057  Implement init: instantiate a Works/ subtree from the fiction template set + write the scribe-project note  (assignee: -)
  [pending ] #1058  Implement ratify (append-only ledger writer) and adopt (canon-node stub from legacy note)  (assignee: -)
  [done    ] #1069  Phase D: verdict inbox + ratify --sweep (parse control/ratification/Inbox.md checkboxes; execute fact append + receipt + inbox clear per verdict)  (assignee: claude-fable)

--- Track: vault ---
  health: 3 items — 0 done (0%), 0 active, 3 pending, 0 blocked (0%)
  [pending ] #1059  Land Fertile Flames in /media/Creative via scribectl init; list legacy saga notes under sources:  (assignee: -)
  [pending ] #1060  Adopt 2-3 load-bearing legacy notes as canon-node stubs; hand-ratify facts into the log  (assignee: -)
  [pending ] #1061  Livesync concurrency test: engine-created files while the vault is open on another device  (assignee: -)

--- Track: slice ---
  health: 1 items — 0 done (0%), 0 active, 1 pending, 0 blocked (0%)
  [pending ] #1062  Run the vertical slice in the synced vault: pack -> body_fill -> rework -> reviews -> ratify  (assignee: -)

Rendered: 2026-07-11T19:32:24Z
