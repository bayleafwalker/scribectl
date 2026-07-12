# vllm-writer — local writing backend on the RTX 3090 (item 1075)

The `openai` runner's local endpoint (DISPATCH.md "Runners"): a vLLM
OpenAI-compatible server on `127.0.0.1:8080`, reusing the proven
`vllm-devstral` pattern (user unit + env file, AWQ 4-bit, 24 GB budget) with
a *writing* model — Devstral is a code model.

## Files

| file | installs to | what |
|------|-------------|------|
| `vllm-writer.service` | `~/.config/systemd/user/` | user unit; `Conflicts=vllm-devstral.service` (one model at a time) |
| `writer.env` | `~/.config/vllm/` | `WRITER_MODEL` + tuning knobs; installed copy carries the real HF token |
| `vllm-writer-run` | `~/.local/bin/` | docker launcher (model comes from env, no tool-call parser) |
| `bakeoff-writer.sh` | run from repo | the bake-off harness (below) |

## Bake-off

```
ops/vllm-writer/bakeoff-writer.sh          # all three candidates
ops/vllm-writer/bakeoff-writer.sh <model>  # one specific model
```

Per candidate (all AWQ 4-bit, verified on HF 2026-07-12 — Mistral Small 3.2
24B, Gemma 3 27B, Cydonia v4.3 as the writing finetune): serve the model,
fill Scene 01-01 in a disposable fixture-vault copy via the `openai` runner,
fire canon+voice reviews via the `claude` runner, collect draft + reports +
logs under `bakeoff-results/<stamp>/<model>/`.

The judging is the only part that isn't mechanical and it is not this
script's: **read the drafts against the Prose Voice Canon** and set the
winner as `WRITER_MODEL` in `~/.config/vllm/writer.env`. Cold starts
download ~15 GB per model into the shared HF cache.

## Steady state (after the bake-off)

```
systemctl --user start vllm-writer     # or enable, or a timer
scribe-dispatch run --runner openai --base-url http://127.0.0.1:8080
```

Per-skill routing (frontier reviews + local fills in one pass) is backlog
item 1076 and unblocks once this backend is real.
