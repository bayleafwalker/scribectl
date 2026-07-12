# scribe-dispatch watch — systemd user units (item 1091)

Ambient dispatch on the workstation: the writer writes, fills and reviews
land, no terminal held open. A `systemd --user` timer fires one debounced
`scribe-dispatch watch --ticks 1` pass on an interval — the single-shot shape
watch was built for (docs/DISPATCH.md; GUIDE.md "Ambient — watch mode").

## Files

| file | installs to | what |
|------|-------------|------|
| `scribe-dispatch-watch.service` | `~/.config/systemd/user/` | oneshot; one settle-gated pass |
| `scribe-dispatch-watch.timer` | `~/.config/systemd/user/` | fires the service every few minutes |
| `watch.env` | `~/.config/scribectl/` | `WATCH_PROJECT` (required) + optional `SCRIBECTL_VAULT` |

Prerequisite: `scribectl`/`scribe-dispatch` on PATH at `~/.local/bin`
(`uv tool install --editable /projects/dev/scribectl`; the unit calls the
absolute path). Run `scribectl doctor` first — it checks exactly the legs this
timer stands on, including whether the routed runners are up.

## Install

```
cp scribe-dispatch-watch.{service,timer} ~/.config/systemd/user/
cp watch.env ~/.config/scribectl/            # then edit WATCH_PROJECT
systemctl --user daemon-reload
systemctl --user enable --now scribe-dispatch-watch.timer
```

Watch it: `systemctl --user list-timers scribe-dispatch-watch.timer`,
`journalctl --user -u scribe-dispatch-watch.service -f`. One pass by hand:
`systemctl --user start scribe-dispatch-watch.service`.

## The writer-down policy (the decision baked in here)

The unit runs with **`--skip-unreachable`**: when a dispatch's routed runner
is down, that dispatch is skipped with a note instead of crashing the pass.
Concretely — with fills routed to the local vllm-writer and reviews to the
frontier, **a stopped vllm-writer skips the fills and still fires the
reviews.** A stopped writer is a state, not breakage; ambient dispatch should
degrade, not fail. The unit therefore has **no dependency on
`vllm-writer.service`** — the writer starts the model when they want fills
landing.

### Auto-start the writer instead?

If you would rather the timer keep the writer up whenever it is active, add a
drop-in (don't edit the shipped unit):

```
systemctl --user edit scribe-dispatch-watch.service
```

```ini
[Unit]
Wants=vllm-writer.service
After=vllm-writer.service
```

Tradeoff, eyes open: this holds the 24 GB writing model resident for as long
as the timer is enabled, and `vllm-writer` `Conflicts=vllm-devstral` — so
auto-start here evicts the code model. That is why the default is
hands-off. With the drop-in, `--skip-unreachable` becomes a belt-and-braces
guard for the cold-start window rather than the normal path.
