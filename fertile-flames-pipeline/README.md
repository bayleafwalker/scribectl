# fertile-flames-pipeline

A fiction production system with canon control. Obsidian is the world database
and writing cockpit; this repo is the contract runner; LLMs fill, review, and
refactor; you stay the canon ratifier and taste gate.

The dangerous failure mode is not bad prose — it is quiet canon rot. Everything
here exists to make canon legible and to keep prose from silently amending it.

## Layout

```
pipeline/        the engine (read-only over the vault, except pack output)
  vault.py       note / frontmatter / wikilink / section parsing
  timeline.py    append-only chronology — the oracle review_canon checks
  contextpack.py the assembler: minimal canon slice per scene card  ← center
  project.py     derived state (status is computed, never stored)
templates/       the eight artifact contracts — copy into the vault to instantiate
vault/           Obsidian vault. The volcanic city-state is the TEST FIXTURE,
                 not content I authored for you — skeletal, yours to fill.
ff.py            CLI: the vertical slice runs through here
```

## Run the slice

```
python3 ff.py status              # derived state of every node + scene
python3 ff.py pack "Scene 01-01"  # assemble + freeze a context pack
```

`pack` writes a hashed, frozen pack to `vault/control/context-packs/`. Feed it
plus the scene card to your `body_fill` agent. Rework the draft by hand. Then
request `review_canon` (checks the timeline) and `review_voice` (checks the
exemplars). Route invented facts through the ratification log.

## Two symmetric modes, one interface

```
manual:     scene card → you draft → canon/voice/beta review → refactor → ratify
llm-assist: scene card → pack → llm draft → you rework → review → ratify
```

The scene card + context pack + review loop is the product. The lore bible is
a byproduct.
