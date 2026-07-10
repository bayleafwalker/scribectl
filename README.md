# scribectl

A contract runner for writing projects that live in the Obsidian vault at
`/media/Creative/`. The vault is the world database and writing cockpit;
scribectl assembles context packs, derives state, and keeps ledgers honest;
LLM agents fill, review, and refactor; you stay the canon ratifier and taste
gate.

The dangerous failure mode is not bad prose — it is quiet canon rot.
Everything here exists to make canon legible and to keep prose from silently
amending it.

## Layout

```
docs/DESIGN.md            why it's shaped this way: the vault-integration
                          decision, the livesync write rules, plugin roles,
                          the fiction→non-fiction generalization
docs/ARCHITECTURE.md      what gets built: package layout, ProjectConfig,
                          CLI surface, invariants, the agent boundary
PLAN.md                   the order to build it in (phases A–E)
scribectl/                the package: core/ (vault, timeline, contextpack,
                          project), config.py (discovery), cli.py, templates/
fixtures/fertile-flames/  the volcanic city-state test vault; its root note is
                          the scribe-project config spec
tests/                    contact tests — every core change runs here before
                          it touches the real vault
fertile-flames-pipeline/  the retired Phase-0 substrate (docs only; parity
                          with ff.py demonstrated 2026-07-10)
```

## The shape, in one breath

```
scribe-project note (in-vault config) → scribectl pack → frozen, hashed
context pack → body_fill agent drafts → you rework → review_canon /
review_voice fire automatically, you consume manually → scribectl ratify
```

Status is derived, never stored. Ledgers are append-only. The engine never
calls an LLM and never rewrites a note you edit by hand. Legacy notes in
`30 Creative/` are sources to cite, not canon to migrate.

## Status

Design ratified 2026-07-10. Phase A (extraction) landed the same day: the
package, discovery, and the full CLI surface (`projects`, `status [--write]`,
`pack`, `ratify`, `adopt`, `init`) are test-driven green against the fixture,
and the ff.py parity gate passed (identical status output, identical pack
sha). Next: Phase B — land Fertile Flames in the real vault at
`/media/Creative` via `scribectl init` + `adopt`.

## Run it

```
uv venv && uv pip install -e . --python .venv/bin/python
SCRIBECTL_VAULT=$PWD/fixtures .venv/bin/scribectl status
.venv/bin/python -m pytest -q          # 51 contact tests
```
