# QuickAdd capture buttons — in-Obsidian surface (item 1088)

Four in-vault buttons so the writer never meets a terminal for the everyday
captures: jot a candidate into the inbox, spin up a canon or mechanic node, and
scaffold a card + its dispatch contract. Built on the
[QuickAdd](https://github.com/chhoumann/quickadd) community plugin.

These are conveniences over the same loop the CLI drives — they do not add
powers. Nothing here can ratify, and the card scaffold delegates to the tested
`scribectl` command rather than re-implementing it (see "native vs. delegated").

## Files

| file | what |
|------|------|
| `quickadd-choices.json` | the four choices' exact settings, as data |
| `templates/canon-node.qa.md` | Template body for a new `canon_node` |
| `templates/mechanic-node.qa.md` | Template body for a new `mechanic_node` (gamedev) |
| `scripts/new-card.js` | QuickAdd user script: bridges the "card + contract" button to `scribectl new card` |

Copy the `templates/` and `scripts/` files somewhere inside your vault (they
must be vault-resident for QuickAdd to reach them); the paths in
`quickadd-choices.json` assume you keep them at `ops/obsidian/quickadd/…`, so
adjust if you put them elsewhere.

## Prerequisites

- The **QuickAdd** plugin, installed and enabled.
- For the card + contract button only: `scribectl` reachable from Obsidian's
  environment. Obsidian's `PATH` frequently omits `~/.local/bin`, so put the
  absolute path (`which scribectl`) into the script's `scribectl path` option.

## Install

1. Copy `templates/` and `scripts/` into the vault.
2. In QuickAdd → Manage Macros / Choices, create the four choices below (import
   `quickadd-choices.json` if your QuickAdd version accepts it; otherwise
   recreate them from the tables — the settings are identical).
3. Add each choice to the QuickAdd command palette / a ribbon button.

### 1. Jot inbox candidate — Capture

| setting | value |
|---------|-------|
| Type | Capture |
| Capture to | `control/ratification/Inbox.md` |
| Format enabled | yes |
| Format | `- [ ] "{{VALUE:fact}}" → [[{{VALUE:target node}}]]\n` |

Native. Appends one pending, routed candidate. The next `scribectl ratify
--sweep` still executes nothing you haven't ticked — this only queues.

### 2. New canon node — Template

| setting | value |
|---------|-------|
| Type | Template |
| Template path | `…/templates/canon-node.qa.md` |
| Folder | `world/canon` |
| File name format | `{{VALUE:name}}` |

Native. Fill in `domain`/`importance` and the ratified-facts placeholder; an
empty node reads as a stub in `scribectl status`, which is correct.

### 3. New mechanic node — Template (gamedev set)

Same as canon node, with template `…/templates/mechanic-node.qa.md` and folder
`world/mechanics`.

### 4. New card + contract — Macro → user script

| setting | value |
|---------|-------|
| Type | Macro |
| Command | User Script → `…/scripts/new-card.js` |
| Script option `scribectl path` | absolute path from `which scribectl` |
| Script option `Project directory` | the project root, e.g. `…/Works/Fertile Flames` |

Prompts for a card name and runs `scribectl new card <name>` in the project
directory. The engine scaffolds the card and its `body_fill` contract and parks
the card at `awaiting_scope`; the QuickAdd Notice echoes the command's output.

## Native vs. delegated (the design call)

Inbox jots and node creation are pure file writes with no engine invariants
riding on them, so they are **native QuickAdd** — no shell, no drift. The card +
contract scaffold is different: the slug wiring and the `awaiting_scope` guard
are tested engine behavior with exactly one implementation
(`scribectl/cli.py`). Re-coding that in a QuickAdd script would fork canon
machinery into an untested copy, so this button **delegates to the CLI**. The
writer still only presses a button; the shell runs under the hood.

## Honest caveat

There is no Obsidian in this repo's test loop, so these configs are **not
machine-verified** the way the CLI is — the four surfaces above are documented
and structurally checked (valid JSON, referenced files present), not run. The
tested source of truth for everything they do is `scribectl` itself. If a
button misbehaves, fall back to the equivalent command:

| button | equivalent command |
|--------|--------------------|
| Jot inbox candidate | edit `control/ratification/Inbox.md` (add a `- [ ]` line) |
| New canon / mechanic node | `scribectl adopt` for legacy ore, or author the note |
| New card + contract | `scribectl new card "<name>"` |
