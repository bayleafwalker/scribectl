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
   — DONE 2026-07-10; `projects` discovers it.
2. Write the scribe-project note; list the legacy saga notes under `sources:`.
   — DONE 2026-07-10: `[[Fertile Flames Saga]]` (dossier over the ~35k-word
   scratchpad original) and `[[Crusade narratives across fictional worlds]]`
   (the four FF vignettes). Other vault mentions are index links, not ore.
3. `scribectl adopt` the two or three legacy notes that carry the most load
   (e.g. `Fertile Flames Saga.md`) into canon-node *stubs with open
   questions*. Ratify facts out of them by hand — the log is the receipt.
   — ADOPTED 2026-07-10 (both sources → `world/canon/` stubs, sources
   untouched; `status --write` dashboard emitted). Ratifying facts is the
   author's move and stays open.
4. Confirm livesync behaves with engine-created files (packs, stubs) while
   another device has the vault open. This is a test, not an assumption.
   — DONE 2026-07-11: initial push landed all 8 project files byte-identical
   on the second device; with both Obsidians open, `status --write` + a
   `ratify --defer` receipt append propagated in ~80s, sha-identical, zero
   conflict artifacts, and the deferred entry flipped no stub state. Empty
   scaffold dirs don't sync (livesync syncs files) — harmless. Untested:
   deliberately simultaneous appends to the same ledger from both devices.

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

- Ratification, iterated (`docs/RATIFICATION.md`): verdict inbox +
  `ratify --sweep` — DONE 2026-07-11; review-candidate mining into the inbox
  (`ratify --mine`, swept-first by `--sweep`) — DONE 2026-07-12;
  mining packs / `propose`, reconciler still open.
- `scribectl status --write` → generated `control/Status.md` dashboard.
- QuickAdd capture configs for instantiating templates from inside Obsidian.
- Enable Longform for the project; compile `body/drafts/` to manuscript.
- Wire `body_fill` / `review_canon` / `review_voice` / `refactor` into the
  `.agents/skills/` dispatch pattern (coordinator never authors).

## Phase E — second project, second shape — LANDED 2026-07-11 (as gamedev, not essay)

The real second project arrived as a game, not an essay: Runosong (the
Kalevala rhythm-game design dialogue), whose literary tie-ins share one canon
with its game-mechanics rulings. Landed: `templateset.py` + per-set `set.yaml`
manifests (fiction's shape became data; init, the pull spec, and derived
status are manifest-driven), the `gamedev/` set (canon + mechanic nodes,
kind-parameterized output cards spanning scenes / spoken fics / blog posts /
research notes / auto-generated outputs), the `fixtures/runosong/` vault, and
contact tests incl. a second golden pack — fiction output byte-identical
throughout. The `essay/` set remains unbuilt until a real non-fiction project
demands it. Next real-vault step when wanted: `scribectl init Runosong --set
gamedev` + adopt the design dialogue as a source.

## Phase F — automatic agentic mode (dispatch)

Design: `docs/DISPATCH.md`. The Phase D bullet "wire body_fill / review_canon /
review_voice into the `.agents/skills/` dispatch pattern" grown into a
runnable coordinator, with the engine untouched (invariant 5 holds).

1. `scribectl status --json` — machine-readable derived state: project header
   (root, config paths) + rows + per-card drafts/reviews-by-lane. The engine
   CLI is the dispatcher's whole API.
2. `.agents/skills/` prompt contracts: `body_fill`, `review_canon`,
   `review_voice` (string.Template markdown; output shape the dispatcher parses).
3. `scribedispatch/` sibling package — policy (fill on `ready_for_fill`,
   missing reviews on `has_draft`/`reviewed`, never ratify/edit/iterate),
   runner abstraction (`claude` CLI / `openai`-compatible local vLLM / `fake`),
   sha-verified artifact landing; `scribe-dispatch plan|run`.
4. Contact tests: fake-runner end-to-end against a disposable fixture copy;
   idempotent second pass; nothing outside designated dirs moves.
5. Live smoke (operator-gated, like the Phase C slice): claude backend fills
   Scene 01-01 in a scratch vault; reviews fire; the writer judges the voice.
6. Backlog beyond the slice: local writer model on the 3090
   (`vllm-writer.service` + bake-off), per-skill routing, codex backend,
   real-vault enablement, agentops dispatch manifest.
   Landed 2026-07-12: candidate mining into the inbox (`ratify --mine`,
   engine-side — see RATIFICATION.md); watch mode (`scribe-dispatch watch`,
   livesync settle debounce, `--ticks 1` for timers); gamedev set dispatch
   (kind-blind fill + per-set review lanes incl. `review_mechanics`, proven
   on the runosong fixture — the live project still needs `init`).

## Phase G — writing surfaces (writer UX)

Design intent: docs/GUIDE.md (the user-facing doc). The loop works; this
phase makes it *inhabitable* from every chair the writer actually sits in —
Obsidian alone, Obsidian + console (raw ctl or an agent driving it), VS Code
with backends in integrated terminals, or fully ambient under watch. The
judgments carried from the Phase C/F session notes: the vault is the primary
UI and every decision surface is a note; the writer never meets shell
quoting; one-motion beats two-step (the two-step disconnect was the top
observed failure mode); status's real function is "where the next ten
minutes go"; raw ore must be captured at the moment it exists.

Backlog (sprint 403), in rough value order:

1. #1084 install story + `scribectl doctor` — PATH on both devices, env
   health check. Prereq for every other surface.
2. #1085 `scribectl next` — the next-actions digest, printed and pinned
   atop Status.md.
3. #1086 `scribectl new card` — card + dispatch contract in one motion
   (contract authoring stays human; the ceremony doesn't).
4. #1087 `scribectl capture` — transcripts/dialogues into dated, registered
   source notes (the Runosong raw-dialogue loss, generalized away).
5. #1092/#1093 mining packs + `propose` + reconciler (RATIFICATION.md items
   3–4) — bulk ore refinement feeding the inbox; the reconciler stays gated
   on ≥2 mined sources.
6. #1094 `brainstorm` skill — ideation sessions land as quarantined
   proposals riding the mine path; never canon, never cited.
7. #1088 QuickAdd configs, #1089 vault-side agent guidance note,
   #1090 VS Code workspace/tasks template, #1091 systemd watch units —
   the per-surface packaging; each is small once 1–4 exist.

Still no Obsidian plugin, no editor extension, no Dataview: surfaces are
generated notes, checkboxes, and the CLI — the pieces that can't drift from
the engine.

## Deliberately NOT built

Added at the scribectl level:

- **No Obsidian plugin.** The engine lives in a CLI agents can invoke;
  Obsidian renders.
- **No Dataview.** Derived state has one implementation: `project.py`.
- **No copy-out workflows.** One vault; the engine reads it in place.
- **No LLM client in the engine.** Dispatch is the skills layer's job.
- **No second template set on spec.** Shapes are earned by projects, not
  predicted.

## Mining the edges — assessed 2026-07-13

The not-built lists (above, the fertile-flames original, DISPATCH.md,
RATIFICATION.md) are two different kinds of line. **Constitutive bans**
protect the system's identity and never lift: no auto-ratify, no LLM client
in the engine, no editable copy-out, no second implementation of derived
state, no auto-canon-from-prose, no consensus-laundering multi-agent.
**Evidence gates** lift when a real project earns them — three of
DISPATCH.md's five items were struck through and landed this way, and the
gamedev set lifted "no second template set on spec" identically.

The recipe that has now mined banned space three times (propose, reconcile,
brainstorm) without crossing a constitutive line: **quarantine the output,
keep agents independent and parallel — never conversational — and route
every verdict through the writer's checkbox.** See the DESIGN.md addendum
for the render-out/copy-out and generated-view clarifications that fall out.

Filed on that recipe (cairn 403), in rough value order:

1. #1100 variant fills — breadth without iteration: N independent fills of
   one card from the same frozen pack, writer picks. Mines "no autonomous
   chapter iteration" and "no writers-room" (dispatch track).
2. #1101 watch invokes `ratify --mine` — ambient candidate flow; the
   dispatcher still never parses a report or touches the inbox (dispatch
   track; the invoke-vs-do line gets decided in DISPATCH.md). — DONE
   2026-07-13: lifted as *invoke, don't do*; watch fires the engine's
   `ratify --mine` after a pass lands reviews, `--no-mine` opts out
   (DISPATCH.md carries the redrawn line).
3. #1102 Shell Commands / QuickAdd macros invoking scribectl — one-motion
   sweep and status from inside Obsidian; the plugin is a dumb button under
   DESIGN.md's ergonomics-only doctrine (surfaces track).
4. #1103 beta pack — the render-out lane: one-way sha-stamped manuscript
   render for beta readers, read back by nothing; coordinates with Longform
   #1065 (engine track).
5. #1104 inbox ordering — verdict ergonomics: conflicts-first /
   by-confidence presentation; threshold-accept is auto-ratify in a hat and
   stays refused (engine track). — DONE 2026-07-13: `ratify --mine` orders
   each fresh batch, queued candidates never move, signals stay in the
   proposal (RATIFICATION.md "What stays forbidden").

Judged not worth mining: engine-side LLM anything (every tempting case has a
skills-layer answer — e.g. an agent skill *proposing* `scope:` links if pack
bloat ever gets real), status enums and stub farms (derived state and
adopt-from-real-ore won outright), and the essay set (already correctly
gated as #1068).
