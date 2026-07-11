# scribectl — design note

**Status:** ratified 2026-07-10. Supersedes nothing; generalizes
`fertile-flames-pipeline/` from one hardcoded project to all writing.

## What this is

scribectl is the contract runner for writing projects that live in the real
Obsidian vault at `/media/Creative/`. The vault is the world database and
writing cockpit; scribectl is the engine that assembles context packs, derives
state, and keeps ledgers honest; LLM agents fill, review, and refactor; the
human stays the canon ratifier and taste gate.

`fertile-flames-pipeline/` proved the shape at 400 lines against a fixture. The
job now is to point the same machinery at the real vault without breaking its
invariants.

## The integration decision

Three options existed for connecting the pipeline to `/media/Creative/`:

1. **Obsidian plugin.** Rejected. The engine's core invariant — read-only over
   the vault, derived state, frozen hashed packs — wants to live in a CLI that
   agents can also invoke. A TypeScript rewrite inside the app process
   duplicates the parser and assembler, couples the engine to Obsidian's
   release cycle, and puts state-bearing logic in the one place it can't be
   contact-tested from a shell.
2. **Semi-manual write-out of select artifacts** to this repo. Rejected harder.
   Two copies of canon that drift silently is *the* failure mode this system
   exists to kill. Any workflow with a "remember to copy it back" step is a
   canon-rot machine with extra ceremony.
3. **External CLI operating directly on the real vault.** Chosen. Obsidian
   stays a dumb renderer and editor. scribectl reads the vault in place, writes
   only its designated outputs, and never needs Obsidian to be running.

## Vault contract

Projects live under a works subtree; legacy concept notes stay where they are:

```
/media/Creative/
  30 Creative/
    <existing concept notes>          ← legacy; untouched; become SOURCES
    Works/
      Fertile Flames/
        world/  structure/  body/  control/  reviews/
      Sunstolen/
        ...
```

**Legacy notes are ore, not canon.** `Fertile Flames Saga.md`, `Sunstolen
Narrative Materials.md`, and the rest of the flat `30 Creative/` corpus are
never migrated, rewritten, or given frontmatter contracts. A canon node in
`world/canon/` cites `[[Fertile Flames Saga]]` and extracts ratified facts from
it; the ratification log is the receipt. `scribectl adopt <note>` can wrap a
legacy note as a canon-node *stub with open questions* — a discover-mode
output, never final canon (no auto-canon-from-prose; that rule carries over
unchanged).

Each project root holds one note with `type: scribe-project` frontmatter — the
project's config and the discovery marker. The registry therefore lives in the
vault itself: visible in Obsidian, synced by livesync, no side-channel config
file to fall out of date. See ARCHITECTURE.md for the field spec.

## The livesync constraint

The vault syncs via CouchDB (obsidian-livesync). External file writes race
with sync when the same note is open on another device. The engine's existing
write discipline is accidentally the correct answer, so it becomes a hard rule:

- **Create files** (packs, drafts, reviews, generated dashboards) — safe.
- **Append to ledgers** (timeline, ratification log) — safe if single-writer.
- **Never rewrite a note that is also edited by hand.** No exceptions.

The one collision surface is the ratification log. Rule: it is appended by
`scribectl ratify` only, never edited in Obsidian. If that proves unlivable,
flip it — Obsidian-only — but pick one writer and keep it.

## Plugin roles — ergonomics only, never state

| Plugin | State | Role |
| --- | --- | --- |
| QuickAdd (enabled) | none | Instantiate the artifact templates into a project subtree from inside Obsidian. Replaces copy-by-hand. |
| Longform (installed, disabled) | compile config only | Enable per-project to compile `body/drafts/` into a manuscript. Read/compile concern; cannot corrupt canon. |
| LanguageTool (installed, disabled) | none | Enable during manual rework passes. Irrelevant to the pipeline. |
| livesync (enabled) | sync | The constraint above. Not a pipeline component. |
| Dataview | — | **Not installed; stays that way.** Derived status (draft exists? clean review landed? accepted in ledger?) is `project.py`'s job. DataviewJS replicating it means two implementations of the state machine. |

Status projection in Obsidian is instead a **generated note**: `scribectl
status --write` emits `control/Status.md` — a dashboard Obsidian merely
renders. It is a cache, clearly marked generated, regenerated on every run,
read back by nothing. This is consistent with "status is derived, not stored"
because nothing downstream consumes it; it exists for eyeballs.

## Generalizing beyond fiction

The artifact shapes map cleanly beyond prose fiction:

| Fiction | Gamedev (exists) | Non-fiction (future) |
| --- | --- | --- |
| scene card | output card (`kind`: scene, spoken_fic, blog_post, research_note, generated) | section card |
| canon node | canon node + **mechanic node** (rulings are facts) | claims / sources ledger |
| timeline (chronology oracle) | identical (`pre` = myth-time; B.C.S = content sequence) | argument-dependency / event chronology |
| voice canon | voice canon (registers per kind, inline) | voice canon (identical) |
| review reports, ratification | identical, + mechanics reviews | identical |

The abstraction that makes this real: **pluggable template sets** — each set
is a directory of artifact contracts plus a `set.yaml` manifest declaring the
card type, the fact-bearing node types, the pull spec (which frontmatter
fields the assembler gathers), and what `init` instantiates. The engine reads
the shape as data; there are no per-set subclasses.

**Discipline, kept and paid:** the fiction set stayed the only one until
Fertile Flames survived a full fill → review → ratify loop in the real vault
(Phase C, closed 2026-07-11). The second set, `gamedev`, was then built for a
real second project — Runosong, a rhythm-driven survival RPG whose literary
tie-ins (spoken fics, devlog posts, research digests, auto-generated outputs
grown from a `base` node) share one canon with its game-mechanics rulings.
The same rule still holds for a third set: shapes are earned by projects,
not predicted.

Two gamedev-specific decisions worth stating:

- **Mechanics are canon.** A `mechanic_node` carries ratified design rulings
  in the same "Ratified facts" section a lore node uses, ratifies through the
  same ledger, and ships into packs identically — a fic where magic works
  differently than the game is canon rot in both directions. Tuning numbers
  stay in a never-shipped "Tuning knobs" section: prose dramatizes rulings,
  not knobs.
- **Unpositioned cards see the whole timeline.** Sequenced tie-ins carry
  book/chapter/scene and see strictly-prior events, as fiction does; a blog
  post or research digest carries no position and everything recorded is
  prior. The actor/location relevance filter still applies.

## Carried over unchanged from fertile-flames

- Status is derived, not stored.
- The timeline is a first-class canon artifact.
- Review *firing* automatic, review *consumption* manual.
- No autonomous chapter iteration, no auto-canon-from-prose, no writers-room
  multi-agent, no empty stub farms.
- The engine never calls an LLM. Agents are dispatched outside it (see
  ARCHITECTURE.md, "The agent boundary").
