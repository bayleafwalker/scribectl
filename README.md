# scribectl

[![tests](https://github.com/bayleafwalker/scribectl/actions/workflows/test.yml/badge.svg)](https://github.com/bayleafwalker/scribectl/actions/workflows/test.yml)

A contract runner for writing projects that live in an Obsidian vault. The
vault is the world database and writing cockpit; scribectl assembles frozen
context packs, derives project state, and keeps ledgers honest; LLM agents
fill, review, and propose; **you stay the canon ratifier and taste gate**.

The dangerous failure mode is not bad prose — it is quiet canon rot.
Everything here exists to make canon legible and to keep prose from silently
amending it.

## The shape, in one breath

```
scribe-project note (in-vault config) → scribectl pack → frozen, hashed
context pack → body_fill agent drafts → you rework → review_canon /
review_voice fire automatically, you consume manually → candidates land in a
ratification inbox → you tick checkboxes → scribectl ratify --sweep
```

Status is derived, never stored. Ledgers are append-only. The engine never
calls an LLM and never rewrites a note you edit by hand — agents draft into
new files, reviews inform without acting, and nothing becomes canon unless
you tick it.

## Trust rules, enforced by the machine

- **No auto-ratify, anywhere.** Agents propose; the inbox is where you
  decide; `ratify --sweep` executes your verdicts and nothing else.
- **Nothing rewrites a human-authored note.** Engine and agents create new
  files in designated places and append to ledgers.
- **Every draft carries its receipt.** Drafts cite the frozen pack (by sha)
  they were written against; ratified facts cite the draft and pack they came
  from. "Why does the canon say this?" always has an answer.
- **Reviews fire automatically, you consume them manually.** A red review
  never blocks and never triggers an agent rewrite. No agent-on-agent loops.

## Try it

The repo ships two fixture vaults, so nothing touches a real vault:

```
uv venv && uv pip install -e . --python .venv/bin/python
SCRIBECTL_VAULT=$PWD/fixtures .venv/bin/scribectl status
SCRIBECTL_VAULT=$PWD/fixtures .venv/bin/scribectl next
.venv/bin/python -m pytest -q          # the contact-test suite
```

For a real install, `uv tool install --editable .` puts `scribectl` and
`scribe-dispatch` on PATH, and `scribectl doctor` health-checks the device.
The vault root defaults to `/media/Creative`; set `SCRIBECTL_VAULT` to yours.
Start a project inside it with `scribectl init "<name>" --set fiction`
(or `--set gamedev`), then read [docs/GUIDE.md](docs/GUIDE.md) — the writer's
guide is the front door.

Dispatch (the agent layer) is optional and pluggable: the default runner
shells out to the `claude` CLI, and a `dispatch.yaml` can route per-skill to
any OpenAI-compatible endpoint (e.g. a local vllm writer — see
`ops/vllm-writer/`).

## Layout

```
docs/GUIDE.md             the writer's guide: surfaces (Obsidian / console /
                          VS Code / ambient watch) and session recipes
docs/DESIGN.md            why it's shaped this way: the vault-integration
                          decision, the livesync write rules, plugin roles
docs/ARCHITECTURE.md      what gets built: package layout, ProjectConfig,
                          CLI surface, invariants, the agent boundary
docs/DISPATCH.md          the agent layer: skills, runners, policy, watch mode
docs/RATIFICATION.md      the verdict inbox, mining packs, propose/reconcile
PLAN.md                   the order it was built in (phases A–G)
scribectl/                the engine: core/ (vault, timeline, contextpack,
                          miningpack, inbox, project), cli.py, templates/
                          (fiction, gamedev set.yaml manifests)
scribedispatch/           the dispatcher: policy, runners, landing, watch
.agents/skills/           prompt/session contracts agents work under
ops/                      per-surface packaging: Obsidian QuickAdd, VS Code
                          tasks, systemd watch units, local vllm writer
fixtures/fertile-flames/  the volcanic city-state test vault (fiction set)
fixtures/runosong/        the rhythm-game test vault (gamedev set: canon +
                          mechanic nodes, kind-parameterized output cards)
tests/                    contact tests — every core change runs here before
                          it touches a real vault
```

## Status

A personal tool, built in the open and driven daily against real writing
projects. The full loop is live: init → capture ore → propose/reconcile
(agent-mined candidates) → fill/review dispatch → verdict inbox →
`ratify --sweep`, with ambient watch mode and per-skill local/frontier model
routing. Deliberately not built: Obsidian plugins, Dataview, auto-ratify, and
any LLM client inside the engine — see the docs for why.

No stability promises yet; the vault formats and CLI surface may shift as
real projects earn changes. Issues and questions are welcome; large PRs are
best preceded by an issue, since the design docs are ratified and changes
that re-litigate them won't land.

## License

[MIT](LICENSE)
