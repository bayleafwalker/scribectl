# Shell Commands one-motion actions — in-Obsidian surface (item 1102)

Three buttons so a governance pass never leaves Obsidian: tick your inbox
checkboxes, press **Sweep verdicts**, glance at the regenerated dashboard.
Built on the [Shell Commands](https://github.com/Taitava/obsidian-shellcommands)
community plugin.

This is DESIGN.md's "dumb button" doctrine made literal: the plugin holds
**zero state and zero script code of ours** — each button is one line of
configuration that invokes the same tested `scribectl` command you would type.
Nothing here parses output, nothing decides, and nothing can ratify: `ratify
--sweep` executes only the checkboxes you already ticked. (That is also why
these are Shell Commands entries rather than QuickAdd macros: a macro needs a
vault-resident user script — code of ours — where Shell Commands is pure
config.)

Desktop only: mobile Obsidian has no shell. On a phone, the inbox is still a
note and your checkboxes still queue — the next sweep from any desktop or the
watch timer's project sees them.

## Prerequisites

- The **Shell Commands** plugin, installed and enabled.
- `scribectl` on PATH per the install story (item 1084): `uv tool install`
  and a green `scribectl doctor`. Obsidian's own `PATH` frequently omits
  `~/.local/bin`, so either add it in the plugin's *Environments* settings
  (PATH augmentation) or use the absolute path from `which scribectl` in the
  commands below — same caveat as the QuickAdd card button (`../quickadd/`).

## The three commands

Create each in Shell Commands → *New shell command*, paste the command, set
the output settings listed, then assign it a command-palette entry or ribbon
icon (the plugin does both).

Every command is prefixed `SCRIBECTL_VAULT={{vault_path}}` —
`{{vault_path}}` is a Shell Commands built-in variable, so the button acts
on **the vault you pressed it in**, whatever the device's global config
says (vault discovery is env → `~/.config/scribectl/vaults` → the default;
it never looks at the working directory). With one project in the vault
that is the whole story; with several, add `-p "<project>"` or duplicate
the button per project.

### 1. Sweep verdicts

```
SCRIBECTL_VAULT={{vault_path}} scribectl ratify --sweep
```

| setting | value |
|---------|-------|
| Output → stdout | Notification balloon |
| Output → stderr | Notification balloon |

Executes exactly the checkboxes you ticked — accepted facts into their
nodes, receipts into the ledger, swept candidates out of the inbox. An
untouched `- [ ]` stays put. The balloon echoes the engine's own report.

### 2. Refresh dashboard

```
SCRIBECTL_VAULT={{vault_path}} scribectl status --write
```

| setting | value |
|---------|-------|
| Output → stdout | Ignore (the note is the output) |
| Output → stderr | Notification balloon |

Regenerates `control/Status.md`, the generated-note dashboard Obsidian
merely renders (DESIGN.md, "Status projection"). Press it with the pinned
note already open — the refresh appears in place.

### 3. What's next

```
SCRIBECTL_VAULT={{vault_path}} scribectl next --write
```

| setting | value |
|---------|-------|
| Output → stdout | Notification balloon |
| Output → stderr | Notification balloon |

The next-actions digest — where the next ten minutes go — as a balloon, and
pinned atop `control/Status.md` by `--write` for reading at leisure.

## Honest caveat

As with the QuickAdd configs, there is no Obsidian in this repo's test loop:
these settings are documented and reviewed, not machine-verified. The tested
source of truth is `scribectl` itself, and every button has a trivial
fallback — the identical command in any terminal. If a balloon ever shows a
`scribectl: error:` line, run the same command in a terminal where `doctor`
is green before suspecting the engine.

| button | equivalent command |
|--------|--------------------|
| Sweep verdicts | `scribectl ratify --sweep` |
| Refresh dashboard | `scribectl status --write` |
| What's next | `scribectl next --write` |
