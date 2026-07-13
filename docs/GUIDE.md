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
the mechanical passes for you — that is watch mode below, packaged as the
systemd timer (#1091). In-Obsidian buttons for "new card + contract", "new
canon/mechanic node", and "jot an inbox candidate" ship as QuickAdd configs in
`ops/obsidian/quickadd/` (#1088) — install them and the writer never meets a
shell for the everyday captures.

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
  are enforced by the engine, not by the agent's manners. `scribectl init`
  drops an `AGENTS.md` at the project root — the standing house rules the
  agent finds in the vault (never ratify, candidates via the inbox, cite pack
  shas, designated dirs only), authored per template set (#1089).

This is where governance sessions live: mine, sweep, route unrouted
candidates, retire stubs.

### VS Code (or any editor) + running backends

Open the vault folder — it is just Markdown — with integrated terminals
running `scribe-dispatch watch` and an agent session. You write in the
editor; fills and reviews land beside you; the inbox is a file you edit.
A workspace + tasks template (one-keystroke status/next/pack/plan/run/sweep/
watch) ships in `ops/vscode/` (#1090) — copy the `.code-workspace` into a
project or drop `tasks.json` in `.vscode/`. There is no editor extension and
won't be: the CLI is the whole API, on purpose.

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

1. `scribectl next` — the next-actions digest: exactly where the next ten
   minutes go, in the order to act. Cards to author (scaffolds and
   scope-blocked), cards ready to fill (and whether they have a contract),
   drafts a review flagged for rework, undecided and unrouted inbox
   candidates, review reports waiting to be mined. A quiet project says
   "Nothing waiting — write." `scribectl next --write` also pins the digest
   atop `control/Status.md` (which then leads with it, table below).
2. Start watch (or an agent console) if you want fills landing while you
   work; skip it for a pure prose day.
3. Write.

`scribectl status` is still the full derived-state table (every node and
card); `next` is the filtered, ordered "what's waiting on me" view over the
same state.

### Start a new project

```
scribectl init "Sunstolen"                    # fiction set
scribectl init "Runosong" --set gamedev       # game canon + literary tie-ins
```

You get the subtree (world/structure/body/control/reviews), the
scribe-project config note, an empty timeline, ledger, and inbox, and an
`AGENTS.md` of house rules for any console agent opened inside the vault
(#1089). Feed it source ore with `scribectl capture` (below); legacy notes
already in the vault go under `sources:` in the config note's frontmatter.

### Feed it raw material

Two moves:

- `scribectl adopt "<legacy note>"` wraps an existing vault note as a canon
  *stub with open questions* — the note itself is never touched; facts get
  ratified out of it through the ledger.
- `scribectl capture "<title>"` pipes a raw design dialogue or brainstorm
  transcript into a dated `type: source` note under the project's `sources/`
  dir and registers its wikilink under the project note's `sources:` — raw ore
  survives without depending on discipline (the Runosong design dialogue was
  never saved; only its distillate did). Read it from stdin
  (`scribectl capture "Ashfall Session" < talk.md`) or `--from FILE`; `--kind`
  tags it (dialogue|brainstorm|transcript|notes). The transcript lands
  verbatim and the project note's body is never touched — only its `sources:`
  list grows.

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

Node-side (#1092):

```
scribectl propose --into "Fertile Flames Saga" --source "Fertile Flames Saga"
```

freezes a **mining pack** (the extraction analog of the context pack: the
source ore, the target node's open questions and already-ratified facts, every
other ratified fact in the project, and the world seed's hard constraints —
sha-stamped, never hand-edited) and scaffolds a quarantined `fact_proposal`
under `control/proposals/`. An agent reads the pack and fills in candidate
facts — each with a quote, a confidence, and a `conflicts:` line naming what it
rubs against. Then `scribectl ratify --mine` lifts those candidates into the
same inbox as review candidates (routed to the node, provenance carried
verbatim: `from source, mining pack sha, via proposal`), where your checkbox is
still the only verdict. Agents never touch `world/canon/` — an unswept proposal
has exactly the standing of the ore it was mined from, and no context pack cites
it. Status advertises the queue: a stub node reads `stub (3 candidates pending)`
and the proposal itself rows as `open` until its facts are swept. Proposal files
are one-per-run and append-never, so N agents can mine N sources with zero write
contention.

When ≥2 open proposals from distinct sources target the same node (#1093):

```
scribectl reconcile --into "Fertile Flames Saga"
```

freezes a **reconciliation pack** — the same node frame, plus every sibling
proposal's candidate set laid side by side — and scaffolds one merge proposal
whose `reconciles:` names the siblings. An agent dedupes the overlaps and flags
where the agents disagree *before you ever look*; the merged candidates ride
the same `ratify --mine` path, and the reconciled siblings retire from every
queue (status rows them `reconciled (folded into [[merge]])`). Fewer than two
sources and the command refuses — nothing to reconcile until independent
miners can actually disagree.

### Brainstorm / ideation

Brainstorm anywhere — an agent chat, a walk, a note. The system's job is to
catch the output, not host the muse. On foot: paste the transcript as a
source note (see above), jot keeper-ideas straight into the inbox as `[ ]`
candidates routed to a node. With an agent: the `brainstorm` skill (#1094,
`.agents/skills/brainstorm.md`, summarized in the vault's `AGENTS.md`) makes
the session end in a fixed exit protocol — capture the transcript verbatim
(`--kind brainstorm`), `propose` against it, distill keeper ideas into the
quarantined proposal's candidates (quote / confidence / conflicts), then
`ratify --mine` queues them as pending inbox lines. Ideation inside the loop,
never inside the canon: verdicts stay yours, and a session whose every idea
you reject still succeeded — the ore survived and the receipts say why.

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
| "what do I do next" | `scribectl next` (digest, also atop Status.md) | — (#1085 done) |
| new card ready for dispatch | `scribectl new card <name>` | — (#1086 done) |
| raw transcripts preserved | `scribectl capture "<title>"` (dated + registered) | — (#1087 done) |
| trigger captures from inside Obsidian | QuickAdd buttons (`ops/obsidian/`) | — (#1088 done) |
| agent-in-vault house rules | `AGENTS.md` dropped by `init` | — (#1089 done) |
| VS Code one-keystroke tasks | workspace + tasks (`ops/vscode/`) | — (#1090 done) |
| dispatch without a terminal open | `enable --now scribe-dispatch-watch.timer` | — (#1091 done) |
| bulk-mine legacy ore into candidates | `scribectl propose --into <node> --source <ore>` → agent fills → `ratify --mine` | — (#1092 done) |
| merge parallel mines of one node | `scribectl reconcile --into <node>` → agent merges → `ratify --mine` | — (#1093 done) |
| ideation captured into the loop | brainstorm skill exit protocol (capture → propose → mine) | — (#1094 done) |
| local/no-cost model fills | claude runner only | #1075/#1076 vllm + routing |
| dispatch in the real vault | engine only | after 1074 verdict → #1080 |
