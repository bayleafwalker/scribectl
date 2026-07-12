# VS Code surface — workspace + tasks (item 1090)

The vault is just Markdown; open it in any editor and write. This is the VS
Code arrangement of the loop: one-keystroke `status` / `pack` / `plan` / `run`
/ `sweep` / `watch`, an integrated terminal beside the prose, the inbox a file
you edit. **There is no extension and there will not be one** — the CLI is the
whole API, on purpose. These are two small config files, nothing more.

## Files

| file | what |
|------|------|
| `scribectl.code-workspace` | a workspace that opens the project folder and carries all the tasks in one file |
| `tasks.json` | the same tasks, for dropping into a project's `.vscode/tasks.json` |

They are equivalent — use whichever fits. A parity test keeps their task lists
identical, so neither drifts from the other.

## Install

Pick one:

- **Workspace file (self-contained):** copy `scribectl.code-workspace` into a
  project root (e.g. `…/Works/Fertile Flames/`), then *File → Open Workspace
  from File…*. The folder path is `.`, so the workspace root is the project
  root — every task runs there and `scribectl` infers the project from the cwd,
  no `-p` needed.
- **tasks.json:** copy `tasks.json` into `<project>/.vscode/tasks.json`. Same
  result when the project folder is your workspace root.

Prerequisite: `scribectl` and `scribe-dispatch` on PATH (`uv tool install
--editable /projects/dev/scribectl`). Run **scribectl: doctor** first — it
checks exactly the legs these tasks stand on. If VS Code's terminal can't find
the commands, its `PATH` is missing `~/.local/bin`; fix your shell profile or
set `terminal.integrated.env.linux` in the workspace `settings`.

## The tasks

Run them from *Terminal → Run Task…*, or bind keys. **scribectl: next** is the
default build task (**Ctrl+Shift+B**).

| task | command | notes |
|------|---------|-------|
| scribectl: next | `scribectl next` | default build — where the next ten minutes go |
| scribectl: status | `scribectl status` | full derived-state table |
| scribectl: doctor | `scribectl doctor` | environment health |
| scribectl: pack card | `scribectl pack "<card>"` | prompts for the card name |
| scribe-dispatch: plan | `scribe-dispatch plan` | dry look; touches nothing |
| scribe-dispatch: run | `scribe-dispatch run --skip-unreachable` | fills + review lanes; a down writer skips fills, reviews still fire |
| scribectl: sweep (dry-run) | `scribectl ratify --sweep --dry-run` | shows what your ticked verdicts would ratify; writes nothing |
| scribe-dispatch: watch | `scribe-dispatch watch --skip-unreachable` | ambient poll loop in a dedicated panel; Ctrl+C to stop |

The two write-capable dispatch tasks carry `--skip-unreachable` so a stopped
`vllm-writer` degrades (skips the local fills) instead of crashing the run —
the same policy the systemd timer bakes in (see `ops/scribe-dispatch/`). Sweep
is shipped dry-run only; run the real `ratify --sweep` in the terminal once you
have read what it would do — ratification is a human keystroke, not a task
button.

## A note on cwd inference

Every task sets `cwd` to `${workspaceFolder}` and passes no `-p`, so it acts on
whichever project your workspace root sits inside. If you open the whole vault
(many projects) rather than one project folder, add `-p "<name>"` to the task
args, or open the single project folder instead.
