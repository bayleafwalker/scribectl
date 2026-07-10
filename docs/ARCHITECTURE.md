# scribectl — application architecture

Companion to DESIGN.md. This is what gets built; PLAN.md is the order.

## Package layout

```
scribectl/
  pyproject.toml
  scribectl/
    core/
      vault.py         note / frontmatter / wikilink / section parsing
      timeline.py      append-only chronology — the oracle review_canon checks
      contextpack.py   the assembler: minimal canon slice per card   ← center
      project.py       derived state (status computed, never stored)
    config.py          vault roots + project discovery (scribe-project notes)
    cli.py             the command surface
    templates/
      fiction/         the eight artifact contracts (moved from ff)
      <essay/ etc. — NOT until a second project demands it>
  fixtures/
    fertile-flames/    the volcanic city-state vault, moved from
                       fertile-flames-pipeline/vault/ — the test fixture
  tests/               contact tests: status + pack green against the fixture
```

The four core modules are extracted from `fertile-flames-pipeline/pipeline/`
as-is, with one change: every hardcoded path assumption becomes a parameter on
`ProjectConfig`. No behavior changes ride along with the extraction.

## ProjectConfig — the one new concept

Each project root contains a note whose frontmatter is the config and whose
existence is the discovery marker:

```markdown
---
type: scribe-project
name: Fertile Flames
template_set: fiction
roots:
  world: world
  structure: structure
  body: body
  control: control
  reviews: reviews
voice_canon: world/language/Prose Voice Canon.md
timeline: control/timeline/Timeline.md
ratification_log: control/ratification/Ratification Log.md
pack_output: control/context-packs
sources:                  # legacy vault notes the assembler may cite as
  - "[[Fertile Flames Saga]]"        # UNRATIFIED source material
---

Freeform project notes below the fence — scribectl reads only the frontmatter.
```

Discovery: `config.py` scans configured vault roots (default
`/media/Creative`, overridable via `SCRIBECTL_VAULT` / `~/.config/scribectl/`)
for `type: scribe-project` notes. All paths in the frontmatter are relative to
the note's directory. The body of the note is the human's; the engine never
touches it.

Why a vault note and not a TOML file in this repo: the registry syncs with the
vault via livesync, is visible in Obsidian, and cannot drift from the project
it describes because it lives inside it.

## CLI surface

```
scribectl projects                     list discovered projects
scribectl init <name> [--set fiction]  instantiate a project subtree under
                                       Works/ from a template set; writes the
                                       scribe-project note
scribectl status  [-p PROJECT]         derived state of every node + card
scribectl status --write               also emit control/Status.md (generated
                                       dashboard; a cache, read back by nothing)
scribectl pack <card> [-p PROJECT]     assemble + freeze a hashed context pack
scribectl ratify  [-p PROJECT]         append accepted/rejected/deferred
                                       inventions to the ratification log
                                       (sole writer of that file — see DESIGN)
scribectl adopt <legacy-note>          wrap a vault note as a canon-node STUB
                                       with open questions (discover-mode
                                       output, never final canon)
```

`-p/--project` may be omitted when the argument (a card name, a path) resolves
to exactly one project, or when cwd is inside a project subtree.

## Core invariants (enforced, not documented-and-hoped)

1. **Read-only over the vault** except designated outputs: `pack_output/`,
   `control/Status.md`, ledger appends via `ratify`, stubs via `adopt`/`init`.
   `core/` takes the vault as data; only `cli.py` holds write paths.
2. **Status is derived, never stored.** No status enums in frontmatter,
   anywhere, including the generated dashboard's inputs.
3. **Packs are frozen and hashed.** A pack's sha is the reproducibility
   receipt; agents consume the frozen file, never live vault state.
4. **Ledgers are append-only.** Timeline and ratification log grow; they do
   not get rewritten. This is also the livesync safety property.
5. **The engine never calls an LLM.** No API client in this package, ever.

## The agent boundary

Dispatch lives outside the engine, in the `.agents/skills/` pattern:

```
skill            consumes                        emits into vault
body_fill        frozen pack + scene card        body/drafts/<draft>.md
review_canon     draft + timeline                reviews/canon/<report>.md
review_voice     draft + voice canon exemplars   reviews/voice/<report>.md
refactor         one paragraph + its constraints edited draft (new file)
```

The coordinator never authors. scribectl can *detect* that a review landed
(derived state) without ever having requested one — that separation is what
keeps "review firing automatic, consumption manual" enforceable, and keeps the
engine testable with zero network.

Skills receive a pack *path*, not pack contents, so the sha in the emitted
artifact's frontmatter can be verified against what was actually consumed.

## Template sets

A template set = a directory of artifact contracts + a pull-spec vocabulary
the assembler understands. `fiction/` ships the existing eight contracts with
pull spec `actors` / `locations` / `scope` (what contextpack.py already
resolves). A future `essay/` set would declare `sources` / `claims`. The
assembler reads the card's frontmatter keys and pulls accordingly; template
sets are data plus a small pull-spec registration, not subclasses.

## Testing

The fixture vault moves to `fixtures/fertile-flames/` and the existing contact
tests become real tests: `status` derives the expected states, `pack` produces
a byte-stable (sha-stable) pack. Every core change runs against the fixture
before it touches the real vault. `fertile-flames-pipeline/` itself is retired
once parity is demonstrated — same commands, same output, new package.
