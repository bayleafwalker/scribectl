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
docs/GUIDE.md             the writer's guide: surfaces (Obsidian / console /
                          VS Code / ambient watch), session recipes, and
                          what's real today vs. backlogged
docs/DESIGN.md            why it's shaped this way: the vault-integration
                          decision, the livesync write rules, plugin roles,
                          the fiction→non-fiction generalization
docs/ARCHITECTURE.md      what gets built: package layout, ProjectConfig,
                          CLI surface, invariants, the agent boundary
PLAN.md                   the order to build it in (phases A–E)
scribectl/                the package: core/ (vault, timeline, contextpack,
                          project), config.py (discovery), templateset.py
                          (set.yaml manifests), cli.py, templates/ (fiction,
                          gamedev)
fixtures/fertile-flames/  the volcanic city-state test vault; its root note is
                          the scribe-project config spec
fixtures/runosong/        the rhythm-game test vault: the gamedev set's canon
                          + mechanic nodes and kind-parameterized output cards
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

Design ratified 2026-07-10. Phases A–C landed 2026-07-10/11: extraction, the
real-vault landing, and the full fill → review → ratify loop in the synced
vault. Phase E landed 2026-07-11: template sets became data (`set.yaml`
manifests) and the second set, `gamedev`, exists for Runosong — game canon
and mechanics rulings feeding literary tie-ins (scenes, spoken fics, blog
posts, research notes, auto-generated outputs), proven against
`fixtures/runosong/` with fiction output byte-identical. Ratification UX
(verdict inbox, `ratify --sweep`) is the open design track — see
docs/RATIFICATION.md.

## Run it

```
uv venv && uv pip install -e . --python .venv/bin/python
SCRIBECTL_VAULT=$PWD/fixtures .venv/bin/scribectl status
.venv/bin/python -m pytest -q          # 70 contact tests
```
