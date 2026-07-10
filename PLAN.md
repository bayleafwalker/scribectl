# scribectl — build plan

This is the repo-level plan: generalizing `fertile-flames-pipeline/` into
scribectl and landing it in the real vault. The original slice plan lives at
`fertile-flames-pipeline/PLAN.md`; its Phase 1 (the vertical slice) is
deliberately re-hosted here as Phase C — it now runs in the real vault, not
the fixture.

Design rationale: `docs/DESIGN.md`. Target shape: `docs/ARCHITECTURE.md`.

## Phase A — extraction (mechanical; do first) — DONE 2026-07-10

All six items landed, plus the Phase-D `status --write` dashboard and the
`init`/`ratify`/`adopt` commands (test-driven, 51 tests). Parity gate passed:
identical `status` bytes, identical pack sha `b1aa50b69a16`; ff.py retired.

1. Package skeleton: `pyproject.toml`, `scribectl/`, `tests/`, `fixtures/`.
2. Move `fertile-flames-pipeline/pipeline/*` → `scribectl/core/`, replacing
   hardcoded path assumptions with `ProjectConfig` parameters. **No behavior
   changes ride along.**
3. Move `fertile-flames-pipeline/vault/` → `fixtures/fertile-flames/` and drop
   a `scribe-project` note at its root (the fixture doubles as the config-note
   spec test).
4. Move `templates/` → `scribectl/templates/fiction/`.
5. `config.py` (discovery) + `cli.py` (`projects`, `status`, `pack`).
6. Tests: `status` derives the expected fixture states; `pack` is sha-stable.
   Parity gate: same output as `ff.py` before it, then retire
   `fertile-flames-pipeline/` as a live tool (keep it until parity is shown).

## Phase B — land in the real vault

1. `scribectl init "Fertile Flames"` → `/media/Creative/30 Creative/Works/`.
2. Write the scribe-project note; list the legacy saga notes under `sources:`.
3. `scribectl adopt` the two or three legacy notes that carry the most load
   (e.g. `Fertile Flames Saga.md`) into canon-node *stubs with open
   questions*. Ratify facts out of them by hand — the log is the receipt.
4. Confirm livesync behaves with engine-created files (packs, stubs) while
   another device has the vault open. This is a test, not an assumption.

## Phase C — the vertical slice, for real

The fertile-flames Phase 1, run where it counts:

1. Resolve the deliberately-open scope link; `status` flips the scene to
   `ready_for_fill`.
2. `scribectl pack` → feed pack + card to `body_fill`. Rework the draft by
   hand into `body/drafts/`.
3. Fire `review_canon` (timeline oracle) and `review_voice` (exemplars);
   reports land under `reviews/`. Consume them manually.
4. `scribectl ratify` the invention verdicts.

If state holds through that loop **in the synced vault** and the prose sounds
like you, the architecture is real. If it doesn't, no orchestration saves it.

## Phase D — conveniences (only after C holds)

- `scribectl status --write` → generated `control/Status.md` dashboard.
- QuickAdd capture configs for instantiating templates from inside Obsidian.
- Enable Longform for the project; compile `body/drafts/` to manuscript.
- Wire `body_fill` / `review_canon` / `review_voice` / `refactor` into the
  `.agents/skills/` dispatch pattern (coordinator never authors).

## Phase E — second project, second shape

Only when a real non-fiction project exists: the `essay/` template set
(section cards, claims/sources ledger, argument-dependency oracle) and its
pull spec. Sunstolen as the second *fiction* project is the cheaper next
stress test of multi-project discovery and can precede this.

## Deliberately NOT built

Everything on the fertile-flames list still holds (no status enums, no stub
farms, no autonomous iteration, no auto-canon-from-prose, no writers-room).
Added at the scribectl level:

- **No Obsidian plugin.** The engine lives in a CLI agents can invoke;
  Obsidian renders.
- **No Dataview.** Derived state has one implementation: `project.py`.
- **No copy-out workflows.** One vault; the engine reads it in place.
- **No LLM client in the engine.** Dispatch is the skills layer's job.
- **No second template set on spec.** Shapes are earned by projects, not
  predicted.
