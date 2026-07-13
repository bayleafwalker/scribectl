# AGENTS.md — scribectl

Agent entry point. Read this fully before touching anything.

## What this repo is

scribectl: a contract runner for writing projects living in the Obsidian vault
at `/media/Creative/`. Generalization of `fertile-flames-pipeline/` (the proven
~400-line substrate, still the runnable tool until parity). Read
`docs/DESIGN.md` (why), `docs/ARCHITECTURE.md` (what), `PLAN.md` (order)
before implementing anything — the design is ratified; don't re-litigate it in
code.

## Sprint workflow (sprintctl, remote mode)

Execution state lives in the **shared homelab postgres**, tenant-scoped by
`repo_id: scribectl` (`.sprintctl/backend.json`). Same wiring as
homelab-analytics.

| Var | Value | Source |
|-----|-------|--------|
| `SPRINTCTL_BACKEND` | `remote` | `.envrc` |
| `SPRINTCTL_URL` | credentialed postgres URL | `.env.sprintctl.local` (gitignored) |
| `AUDITCTL_DB` / `AUDITCTL_ARTIFACTS_ROOT` | repo-local / `/projects/dev` | `.envrc` |

**Load:** `direnv allow` or `source .envrc` from repo root, once per shell —
never hand-prefix env onto individual commands. If `SPRINTCTL_URL` is missing,
copy `.env.sprintctl.local` from homelab-analytics or inject the secret; the
`.envrc` fails fast on purpose.

**If `sprintctl` is missing or stale** (private tool, not on PyPI):

```bash
uv tool install --force --reinstall /projects/dev/sprintctl --python python3
```

**Validate before use:** `sprintctl usage --context --json` must show the
scribectl sprint, not another repo's. Remote mode means claims are shared
state — TTL discipline matters (`--ttl` ≥ 2× expected duration, heartbeat at
half-TTL).

### Session entry

1. `sprintctl sprint show` / `sprintctl item list --sprint-id <id>`
2. `sprintctl claim list-sprint --sprint-id <id>` — respect existing claims
3. Claim before non-trivial work: `sprintctl claim create --item-id <id> --actor <you> --json`; keep the `claim_token`
4. Record decisions as item notes (`--type decision`) as you go
5. Close with the token: `sprintctl item status --id <id> --status done --claim-id <cid> --claim-token <tok>`
6. Before stopping: release or hand off claims, leave `claim-handoff` notes,
   `sprintctl render > docs/sprint/current.md`

## Sprint naming

`YYYY-SNN-<anchor>-<focus>-<phase>` per the sprintctl-bootstrap-template
vocabulary (hearth/forge/harbor…, workflow/core/docs…, overture/build/weave…).
Current: `2026-S01-forge-core-overture`. Backlog sprint:
`2026-S00-cairn-backlog` (kind=backlog) — pull Phase D/E items from it only
after the Phase C slice holds.

## Tracks

| Track | Scope |
|-------|-------|
| `engine` | `scribectl/core/` extraction, ProjectConfig, discovery, tests |
| `cli` | command surface (`projects/status/pack/init/ratify/adopt`) |
| `vault` | landing projects in `/media/Creative/`, livesync verification |
| `slice` | the Phase C vertical slice — the sprint's acceptance gate |
| `expansion` | (backlog) second project, second template set |
| `dispatch` | automatic agentic mode: `scribedispatch/`, `.agents/skills/`, runners (see `docs/DISPATCH.md`) |

## Claim policy

- Claim per item before implementation; shaping/notes need no claim.
- One item per claim; don't batch claims.
- The `slice` item is operator-driven (taste gate) — agents assist, never
  close it autonomously.

## Review policy

- Targeted tests gate `done`: `pytest <touched tests> -x --tb=short` green
  before any done transition on `engine`/`cli` items.
- Parity gate: `fertile-flames-pipeline/` is retired only after item 1055
  (contact tests) demonstrates identical status/pack output.
- Commit at the smallest reviewable scope; never commit with failing tests.

## Stateful protocol verification

- Routing and hooks are declared in `scribectl.dispatch.json`; closed subjects and escalation rules live in `.agents/overlays/scribectl.state-protocols.md`.
- Use the shared `verify-state-protocols` skill for artifact landing, pack receipts, mining idempotency, ratification sweep recovery, or concurrent filesystem writers.
- `survey` and `reconcile` are read-only. `verify` may add tests and model artifacts; `repair` requires separate product-change authorization.
- Run fault and concurrency scenarios only against copied fixture vaults. `/media/Creative/` remains production.
- The writer's checkbox remains the only ratification verdict. Verification and automation never set or infer acceptance.

## Artifact paths

| Artifact | Path |
|----------|------|
| Sprint snapshot | `docs/sprint/current.md` (rendered, committed) |
| Sprint archive | `docs/sprint/archive/` |
| Knowledge entries | `docs/knowledge/` (promote only real decisions/lessons) |
| Design docs | `docs/DESIGN.md`, `docs/ARCHITECTURE.md`, `PLAN.md` |

## Source-of-truth order

1. sprintctl (remote db) — execution state, claims, item status
2. `docs/DESIGN.md` / `docs/ARCHITECTURE.md` — ratified design
3. `PLAN.md` — sequencing
4. `docs/sprint/current.md` — rendered snapshot (may lag the db; regenerate,
   don't hand-edit)

## What NOT to do

- **Never write to `/media/Creative/` from this repo's tooling until Phase B
  items are claimed and active.** The real vault is production.
- No LLM client in the engine package, ever (ARCHITECTURE.md invariant 5).
  Runners live in `scribedispatch/`, which talks to the engine only through
  the `scribectl` CLI and never ratifies, edits, or iterates (docs/DISPATCH.md).
- No status enums in vault frontmatter; status is derived (`project.py`).
- Don't edit `docs/sprint/current.md` by hand — it's `sprintctl render` output.
- Don't start Phase D/E backlog items while Phase C is unproven.
- Don't run `sprintctl init` — no such command; don't create a local sqlite db
  here — this repo is locked to remote mode by `.sprintctl/backend.json`.
