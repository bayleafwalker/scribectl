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
fertile-flames-pipeline/  the proven substrate — one project, one fixture,
                          ~400 lines. scribectl is its generalization; it
                          stays runnable until parity is demonstrated.
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

Design ratified 2026-07-10; Phase A (extraction) not yet started. Run the
existing slice via `fertile-flames-pipeline/ff.py` (`status`, `pack`).
