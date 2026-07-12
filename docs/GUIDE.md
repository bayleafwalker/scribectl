# scribectl — the writer's guide

This is the user-facing document: how to actually write with this thing.
The engineering rationale lives in DESIGN.md / ARCHITECTURE.md / DISPATCH.md /
RATIFICATION.md; nothing here amends those. Where a workflow below is not
built yet, it says so and names the backlog item.

## What it does for you

You write in Obsidian. scribectl keeps the world legible: it knows which
scenes are ready to draft, freezes exactly the right slice of canon into a
context pack, lets agents draft and review against that pack, and reduces
canon governance to ticking checkboxes in a note. You never lose an
invention, never wonder which facts a draft was written against, and never
watch your canon rot quietly while you were busy writing.

## The trust rules, in writer terms

These are enforced by the machine, not promised by prose:

- **Nothing becomes canon unless you tick it.** Agents propose; the
  ratification inbox is where you decide; `ratify --sweep` executes your
  verdicts and nothing else. There is no auto-ratify anywhere.
- **Nothing rewrites a note you edit by hand.** Engine and agents create new
  files in designated places (drafts, reviews, packs) and append to ledgers.
  Your prose is yours.
- **Every draft carries its receipt.** A draft names the frozen pack (by sha)
  it was written against; a ratified fact's receipt names the draft and pack
  it came from. You can always answer "why does the canon say this?"
- **Reviews fire automatically; you consume them manually.** A red canon
  review never blocks you and never triggers an agent rewrite. It is
  information for your next rework pass, nothing more.
- **A bad draft is information, not fuel.** There are no agent-on-agent
  loops. One fill per card; the rework is yours.

## Setup, per device

One command:

```
uv tool install --editable /projects/dev/scribectl
```

That puts `scribectl` and `scribe-dispatch` on PATH (`~/.local/bin`);
`--editable` means a `git pull` in the repo updates the tools in place, no
reinstall. Then health-check the device:

```
scribectl doctor
```

Doctor checks commands on PATH, vault roots (default `/media/Creative`;
`SCRIBECTL_VAULT` overrides — the fixtures use this), each project's
designated dirs and ledgers, and every dispatch route's runner — including
whether vllm-writer is up, now that fills route to it. `FAIL` lines flip the
exit code; warnings don't. Doctor only probes, never repairs.

Dispatch defaults to the `claude` runner (the authenticated `claude` CLI);
`--runner/--model/--base-url`, env, or `~/.config/scribectl/dispatch.yaml`
change that per machine — the per-skill `skills:` map in that file is what
routes fills to the local writer and reviews to the frontier.

**Where dispatch runs:** everywhere, including the real vault — the
live-smoke voice gate (1074) passed and real-vault dispatch was enabled
(1080) on 2026-07-12. Idempotency held on production: a plan/run against
fully-reviewed cards is a clean no-op.

## Pick your surface

The vault is the primary interface. Obsidian renders it; consoles act on it;
every decision you make happens in a note, not a flag. The surfaces below
are arrangements of the same loop — use whichever fits the session, switch
freely mid-project.

### Obsidian only

Write. `control/Status.md` (regenerate with `status --write`) is your
dashboard; reviews land as notes; candidates queue in
`control/ratification/Inbox.md` and you verdict them with checkboxes:

```markdown
- [x] accept — becomes canon on the next sweep
- [-] reject — receipted as rejected
- [>] defer  — receipted as deferred, leaves the inbox
- [ ] untouched — stays put; a sweep never flushes what you haven't judged
```

Rewriting the fact text before ticking is encouraged: the rewrite *is* the
ratified wording. For this surface to be fully hands-off something must run
the mechanical passes for you — that is watch mode below, and the planned
systemd timer (#1091). In-Obsidian buttons for "new card", "new node", "jot
a candidate" are the QuickAdd configs, planned as #1088.

### Obsidian + a console beside it

The workhorse arrangement: vault on one screen, terminal on the other. Two
modes of console:

- **Raw ctl.** You run `scribectl status` / `pack` / `ratify --sweep` and
  `scribe-dispatch plan|run` yourself. `plan` is the dry look — it prints
  what *would* fire and touches nothing.
- **An agent driving the ctl.** Open a Claude (or other CLI agent) session
  and say things like "sweep the inbox and tell me what's still unrouted" or
  "pack everything ready and run fills, then summarize the reviews." The
  agent runs the same audited commands; the trust rules hold because they
  are enforced by the engine, not by the agent's manners. A standing
  guidance note the agent finds in the vault (rules of the house, per
  project) is planned as #1089.

This is where governance sessions live: mine, sweep, route unrouted
candidates, retire stubs.

### VS Code (or any editor) + running backends

Open the vault folder — it is just Markdown — with integrated terminals
running `scribe-dispatch watch` and an agent session. You write in the
editor; fills and reviews land beside you; the inbox is a file you edit.
A workspace/tasks template (one-keystroke status/pack/sweep/watch) is
planned as #1090. There will be no editor extension: the CLI is the whole
API, on purpose.

### Ambient — watch mode

```
scribe-dispatch watch -p "Fertile Flames"        # poll loop
scribe-dispatch watch --ticks 1                  # single shot, for timers
```

Watch polls every `--interval` (60s) and only acts once the vault has been
mtime-quiet for `--settle` (30s), so a half-synced note never dispatches.
It repeats, never iterates: a finished card is never re-drafted. It stops
loudly on error — a dead watch is visible, a silently skipping one is not.

Fully ambient, no terminal held open — packaged systemd user units
(`ops/scribe-dispatch/`, its README has the install):

```
cp ops/scribe-dispatch/scribe-dispatch-watch.{service,timer} ~/.config/systemd/user/
cp ops/scribe-dispatch/watch.env ~/.config/scribectl/     # set WATCH_PROJECT
systemctl --user enable --now scribe-dispatch-watch.timer
```

The timer fires one `--ticks 1 --skip-unreachable` pass every few minutes.
`--skip-unreachable` is the policy decision baked in: **a stopped vllm-writer
skips the fills routed to it and still fires the reviews on the frontier** —
a down writer is a state, not breakage, so the unit does *not* auto-start the
model. (The README shows the drop-in for those who'd rather it did, and the
resource tradeoff — the 24 GB writer evicts the code model.) With the timer
enabled, the writing day collapses to: write, glance at Status.md, tick the
inbox.

## Sessions

### Start a writing session

1. `scribectl status --write` — the dashboard tells you where the next ten
   minutes go: what's blocked and on which link, what's ready, what has
   unconsumed reviews, whether the inbox holds undecided candidates.
2. Start watch (or an agent console) if you want fills landing while you
   work; skip it for a pure prose day.
3. Write.

A single `scribectl next` that prints exactly the "next ten minutes" list —
and pins it atop Status.md — is planned as #1085.

### Start a new project

```
scribectl init "Sunstolen"                    # fiction set
scribectl init "Runosong" --set gamedev       # game canon + literary tie-ins
```

You get the subtree (world/structure/body/control/reviews), the
scribe-project config note, an empty timeline, ledger, and inbox. List any
legacy notes that should count as source ore under `sources:` in the config
note's frontmatter.

### Feed it raw material

Two moves, today:

- `scribectl adopt "<legacy note>"` wraps an existing vault note as a canon
  *stub with open questions* — the note itself is never touched; facts get
  ratified out of it through the ledger.
- Paste raw ore (a design dialogue, a brainstorm transcript) into a note
  yourself, then list it under `sources:`. Do this *at the time* — the
  Runosong design dialogue was never saved and only its distillate survives.
  `scribectl capture` (pipe a transcript in, get a dated, registered source
  note out) is planned as #1087 so this stops depending on discipline.

### Bulk fill — turning ore into candidates and cards into drafts

Card-side: every `ready_for_fill` card with a contract gets packed and
drafted by `scribe-dispatch run`; landed drafts get their review lanes
(canon + voice; gamedev adds mechanics) filled automatically. Scaffold the
pair in one motion:

```
scribectl new card "Scene 02-01"                 # fiction: card + contract
scribectl new card "Episode 2-01" -p Runosong    # gamedev: output card + contract
```

You get the card (in the set's card dir) and its `body_fill` dispatch
contract (in `control/contracts/`, targeting the card, `output_target`
pre-wired). The card lands with its `[[ ]]` scope placeholders intact, so it
derives a new **`awaiting_scope`** state — dispatch skips it, and ambient
watch will *not* fill an empty scaffold. Author the card in Obsidian (fill or
delete the placeholders); the first real scope link flips it to
`ready_for_fill` (or `blocked_unresolved_scope` if a link doesn't resolve
yet). Writing the contract's Task/Scope/Output prose stays yours — the
ceremony is automated, the intent isn't.

Node-side, designed but not built (#1092, #1093): `scribectl propose` will
mine a legacy source through a frozen mining pack into quarantined proposal
notes — candidate facts with quotes, confidence, and conflict flags —
feeding the same inbox. N agents can mine N sources in parallel; a
reconciler flags where they disagree before you ever look. Until then,
mining the 35k-word saga stub is a manual session.

### Brainstorm / ideation

Brainstorm anywhere — an agent chat, a walk, a note. The system's job is to
catch the output, not host the muse. Today: paste the transcript as a source
note (see above), jot keeper-ideas straight into the inbox as `[ ]`
candidates routed to a node. Planned: a `brainstorm` skill (#1094) whose
sessions land as quarantined proposal notes that ride the mining path into
the inbox — ideation inside the loop, never inside the canon.

### Review and ratify — the governance pass

After drafts and reviews have landed:

```
scribectl ratify --sweep [--dry-run]
```

One motion: mines new review candidates into the inbox, executes every
verdict you've ticked (fact into the node, receipt into the ledger, inbox
line cleared), and nags about problems — unrouted candidates queue arrowless
until you point them at a node. Read reviews in Obsidian, rework the draft,
tick the inbox, sweep, done. `--dry-run` prints ready-to-paste blocks if you
want the conservative path. Per-fact flags (`--accept/--reject/--defer`)
exist for scripting; if you are typing an escaped apostrophe, use the inbox.

## Real today vs. planned

| you want | today | planned |
| --- | --- | --- |
| commands on PATH, env health check | `uv tool install` once; `scribectl doctor` | — (#1084 done) |
| "what do I do next" | read Status.md | #1085 `scribectl next` |
| new card ready for dispatch | `scribectl new card <name>` | — (#1086 done) |
| raw transcripts preserved | paste + `sources:` by discipline | #1087 `capture` |
| trigger workflows from inside Obsidian | inbox checkboxes only | #1088 QuickAdd |
| agent-in-vault house rules | repo docs only | #1089 guidance note |
| VS Code one-keystroke tasks | type the commands | #1090 workspace template |
| dispatch without a terminal open | `enable --now scribe-dispatch-watch.timer` | — (#1091 done) |
| bulk-mine legacy ore | manual session | #1092/#1093 propose + reconciler |
| ideation captured into the loop | inbox jots | #1094 brainstorm skill |
| local/no-cost model fills | claude runner only | #1075/#1076 vllm + routing |
| dispatch in the real vault | engine only | after 1074 verdict → #1080 |
