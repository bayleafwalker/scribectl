---
name: verify
description: Drive scribectl end-to-end against a disposable copy of the fixture vault.
---

# Verifying scribectl changes

The surface is the CLI (`project.scripts` → `scribectl.cli:main`). No install
needed:

```bash
run(){ python -c "import sys; from scribectl.cli import main; sys.exit(main(sys.argv[1:]))" "$@"; }
```

Point it at a throwaway vault — never at `/media/Creative` (production):

```bash
mkdir -p "$SCRATCH/vault/Works"
cp -r fixtures/fertile-flames "$SCRATCH/vault/Works/Fertile Flames"
export SCRIBECTL_VAULT="$SCRATCH/vault"
```

Flows worth driving: `status` (baseline vs. after mutations), `pack` twice
(freeze + `unchanged`), `ratify --sweep --dry-run` then `--sweep` then re-sweep
(idempotency), `init X --under "$SCRATCH/vault/Works"` then a command against
the fresh project. Gamedev-set flows: copy `fixtures/runosong` instead.

Gotchas: two projects in one vault root make bare commands ambiguous — pass
`-p`. Warnings go to stderr; keep it separate from stdout when capturing.
`md5sum` against the pristine `fixtures/` copy is the cheapest
"nothing-else-moved" check.
