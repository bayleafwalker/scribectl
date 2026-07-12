# scribectl — automatic agentic mode (dispatch)

Companion to ARCHITECTURE.md ("The agent boundary") and RATIFICATION.md. This
is the design for the layer that *runs* the agents; the engine stays LLM-free
(invariant 5) and this document does not amend that.

## What "automatic" means here — and what it never means

The loop the design already sanctions is: fill fires when a card is ready,
reviews fire when a draft lands, and *consumption stays manual*. Automatic
agentic mode is exactly that and nothing more, made into a runnable process:

```
scribectl status --json          derived state says what is dispatchable
        │
scribe-dispatch plan/run         the coordinator: picks skills, runs agents,
        │                        lands artifacts — never authors, never decides
        ▼
body/drafts/, reviews/canon|voice/    artifacts with pack_sha receipts
        ▼
you: rework drafts, consume reviews, tick the inbox, scribectl ratify
```

Hard lines, inherited, not new:

- **Never ratifies.** No writes to the ledger, the inbox verdicts, or any
  `## Ratified facts` section. The taste gate is the writer.
- **Never edits.** Artifacts are new files in designated output dirs
  (`body/drafts/`, `reviews/<lane>/`). A human-touched file is never rewritten.
- **Never iterates on itself.** One dispatch per card per state; a landed
  draft is the human's to rework. "No autonomous iteration" still holds — the
  automation is in the *firing*, not in agent-on-agent loops.
- **Consumes frozen packs only.** Skills get a pack *path*; the landed
  artifact's `pack_sha` frontmatter is verified against the file actually read.

## Placement

```
scribedispatch/          sibling package in this repo (second wheel package,
  policy.py              console script scribe-dispatch); talks to the engine
  runner.py              ONLY through the scribectl CLI (subprocess), so the
  landing.py             engine's read/write contract is also the dispatcher's
  cli.py
.agents/skills/          the prompt contracts (body_fill.md, review_canon.md,
                         review_voice.md, review_mechanics.md) — data,
                         versioned with the repo
```

Why a sibling package and not `scribectl/`: invariant 5 ("no LLM client in the
engine, ever") is load-bearing for testability and for trust in the write
paths. Why the CLI as the API and not imports: the CLI is the audited surface
— every pack the dispatcher feeds an agent was frozen by the same command a
human would run, and the dispatcher can be replaced without touching core.

## The policy (v1)

Derived state is the only trigger; nothing is stored, nothing is scheduled.

| card state              | action |
|-------------------------|--------|
| `blocked_unresolved_scope` | nothing (report it) |
| `ready_for_fill`        | freeze pack (`scribectl pack`), run `body_fill`, land draft at the contract's `output_target` |
| `has_draft`             | run each review in the contract's `review_after` whose report is missing for that draft |
| `reviewed`              | fill any *missing* review lane; otherwise nothing — the rest is the writer's |

The per-card contract note (`control/contracts/`, `type: contract`) is the
dispatch spec: `mode`, `agent_profile`, `output_target`, `review_after`. A
`ready_for_fill` card without a contract is skipped with a warning — writing
contracts is authoring intent, and the coordinator never authors.

Idempotency is artifact existence, not state: a draft at `output_target`
means fill is done (even if a human replaced its content); a review report
naming that draft + lane means that review fired. Re-running `run` after a
completed pass dispatches nothing.

## Runners

One abstraction, `Runner.generate(prompt) -> text`, three backends:

| runner   | what it is | when |
|----------|-----------|------|
| `claude` | `claude -p` headless subprocess (installed, authenticated) | default; frontier quality for reviews and fills |
| `openai` | OpenAI-compatible chat endpoint via stdlib urllib — vLLM on the RTX 3090 (`~/.config/vllm/` service pattern, port 8080) | local writer model; no per-token cost, private |
| `fake`   | canned responses from a directory | contact tests; zero network |

Backend choice is machine policy, not vault content: `--runner`/`--model`/
`--base-url` flags, env (`SCRIBE_DISPATCH_RUNNER`…), then
`~/.config/scribectl/dispatch.yaml`. Per-skill routing landed 2026-07-12
(item 1076, once two backends were real): a `skills:` map in dispatch.yaml
routes each skill (frontier reviews + local fills is the shipped shape) with
the top-level keys as fallback; an explicit `--runner` pins one backend for
the whole pass. `codex` joins as a fourth backend if/when the CLI is
installed — the abstraction is the contract, not the vendor.

The local track reuses the proven `vllm-devstral.service` pattern (user unit +
env file, AWQ 4-bit, 24 GB budget) with a *writing* model — Devstral is a code
model (`ops/vllm-writer/`). The candidate bake-off (Mistral Small 24B, Gemma 3
27B, Cydonia as the writing finetune) was judged the only way that matters —
`review_voice` reports against the Prose Voice Canon, read by the writer —
and Gemma 3 27B won on 2026-07-12: the only draft whose administrative
physical detail carried the horror. (Cydonia was disqualified diagnostically:
its AWQ quant's chat-template serving path is broken; the weights write fine
through a hand-templated raw completion.)

## Skill contracts

`.agents/skills/<name>.md` — `string.Template` markdown ($vars, so prose
braces stay safe). Each states the task, the scope rule (invented proper
nouns go under "Introduced candidates", never asserted), and the exact output
shape the dispatcher parses:

| skill          | consumes                             | emits |
|----------------|--------------------------------------|-------|
| `body_fill`    | frozen pack + card + contract        | `body/drafts/<output_target>` — `type: draft`, links card, `pack_sha` |
| `review_canon` | draft + timeline + pack              | `reviews/canon/<draft>-canon-review.md` — `type: review_report`, `kind: canon` |
| `review_voice` | draft + voice canon + pack           | `reviews/voice/<draft>-voice-review.md` — `type: review_report`, `kind: voice` |
| `review_mechanics` | draft + pack (the mechanic-node briefs are the rulebook) | `reviews/mechanics/<draft>-mechanics-review.md` — `type: review_report`, `kind: mechanics` |

Review lanes default per template set (`policy.SET_REVIEW_KINDS`): fiction
gets canon + voice, gamedev adds mechanics — a fic where magic works
differently than the game is canon rot in both directions. A contract's
`review_after` narrows or reorders the lanes; `body_fill` is kind-blind (the
card's `kind` names the form — scene, spoken fic, blog post — and the skill
contract tells the agent to honor it).

The dispatcher writes the frontmatter itself (deterministic: type, kind,
links, `pack_sha`, `agent`, `model`, `generated`); the agent supplies only the
body. A review's `verdict:` line is parsed from the agent output and defaults
to `issues` when unparsable — fail toward the writer looking, never away.
`refactor` (paragraph-level, new file out) is deferred until the loop earns it.

## Testing

Contact tests, same doctrine as the engine: copy `fixtures/fertile-flames` to
a tmp vault, run the dispatcher with the `fake` runner end-to-end —
`ready_for_fill` → fill lands → `has_draft` → reviews land → `reviewed`;
second run dispatches nothing; nothing outside `body/drafts/`, `reviews/`,
`control/context-packs/` moved (md5 against pristine). The live smoke (claude
backend, Scene 01-01, disposable vault) is operator-reviewed like the Phase C
slice: if the draft doesn't sound like the voice canon, the loop doesn't earn
the real vault.

## Deliberately NOT built (v1)

- ~~**No watch daemon.**~~ Landed 2026-07-12: `scribe-dispatch watch` polls
  every `--interval` (60s) and passes only when the vault has been quiet for
  `--settle` (30s) — livesync delivers notes as bursts of file writes, and a
  half-synced note must never dispatch. `--ticks 1` is the systemd-timer /
  cron single shot (one debounced pass, exit 0 either way). Errors are not
  survived: a dead watch is visible, one that silently skips failures is not.
  The hard lines hold — watching adds repetition, never iteration.
- **No candidate mining by the dispatcher.** Reviews list "Introduced
  candidates"; the *engine's* `scribectl ratify --mine` lifts them into the
  ratification Inbox as pending candidates (RATIFICATION.md build item 2,
  landed 2026-07-12). The dispatcher itself still never touches the inbox.
- ~~**No real-vault dispatch** until the fixture loop and the live smoke both
  hold.~~ Gate lifted 2026-07-12: the F.5 smoke draft passed the operator's
  voice verdict (canon + voice lanes clean), and the first real-vault
  plan/run pass came back a clean no-op — the Phase C card reads as fully
  reviewed, so idempotency held on production ground. `/media/Creative` is
  still production: machine policy lives in `~/.config/scribectl/dispatch.yaml`
  (runner: claude), and every hard line above applies with no fixture net.
- **No agent-on-agent loops, no retries-with-feedback.** A bad draft is
  information for the writer, not fuel for the coordinator.
- ~~**No actionq/cockpit integration yet.**~~ Landed 2026-07-12, once dispatch
  proved out: `scribectl.dispatch.json` (repo root; staged copy in
  `agentops/templates/dispatch/examples/`) registers the repo at adoption
  level `observable` — the cockpit's `/cockpit/api/dispatch-manifests` serves
  it, all actionq action classes are `enabled: false`, and the manifest's
  own out_of_scope lines restate the hard lines. Observability, not a
  dependency: actionq never drives fills or reviews.
