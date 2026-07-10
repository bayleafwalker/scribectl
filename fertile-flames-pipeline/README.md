# fertile-flames-pipeline — RETIRED (extracted into scribectl)

This directory was the Phase-0 substrate: a fiction production system with
canon control, proven at ~400 lines against a fixture vault. On 2026-07-10 the
parity gate passed (identical `status` output; identical pack sha
`b1aa50b69a16`) and it was retired as a live tool. Only the historical plan
remains here.

Where everything went:

```
pipeline/vault.py timeline.py contextpack.py project.py
                     → scribectl/core/        (unchanged behavior)
templates/           → scribectl/templates/fiction/
vault/               → fixtures/fertile-flames/  (now carries a scribe-project
                                                  note — the config spec test)
ff.py status / pack  → scribectl status / scribectl pack
```

Run the slice via the package now:

```
uv pip install -e .              # from the repo root
SCRIBECTL_VAULT=$PWD/fixtures scribectl status
SCRIBECTL_VAULT=$PWD/fixtures scribectl pack "Scene 01-01"
```

`PLAN.md` in this directory is the original Phase-0/1 build plan, kept as the
design record. The repo-level `PLAN.md` supersedes it.
