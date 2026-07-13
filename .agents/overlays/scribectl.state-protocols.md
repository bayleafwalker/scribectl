# scribectl state-protocol overlay

## Trust rules

Protocol verification must preserve these boundaries:

- agents never ratify;
- no operation rewrites a human-authored note;
- drafts and reviews cite the frozen pack they consumed;
- reviews inform but never trigger agent-on-agent repair loops;
- status is derived from artifacts and ledgers rather than mutable status fields;
- `/media/Creative` is production and is excluded from automated verification.

## Closed subjects

| Subject | State owner | Default depth | Primary anchors |
|---|---|---:|---|
| Context-pack receipt | Frozen file plus content SHA | 1 | `scribectl.core.contextpack:build_pack`, pack CLI |
| Derived project state | Vault artifacts and ratification ledger | 1 | `scribectl.core.project` |
| Draft/review landing | New artifact path | 2 | `scribedispatch.landing:_write_new`, `land_draft`, `land_review` |
| Mining idempotency | Inbox/ledger `via [[artifact]]` markers | 1 | `scribectl.core.inbox:mine` |
| Ratification sweep | Inbox verdicts, target nodes, ledger receipts | 2 | inbox transforms and ratify CLI writes |
| Ambient dispatch | Derived state plus artifact existence | 2 | `scribedispatch` plan/run/watch |

## Required scenarios

- Two independent dispatch processes attempt to land the same draft or review.
- Crash after artifact creation but before the caller observes success.
- Frozen pack SHA matches the exact pack body consumed by the runner.
- Repeated plan/run/watch passes over stable artifacts dispatch nothing.
- Repeated mining adds no duplicate candidate blocks.
- Sweep interruption between target-node, ledger, and inbox writes is detectable and recoverable.
- Two sweep processes cannot silently ratify or drop the same candidate twice.
- Unknown or malformed review verdict fails toward `issues`.

## Current concurrency risk

Artifact landing uses an existence check followed by a normal file write. That protects sequential runs but is not an exclusive-create primitive across processes. Until verified or repaired, do not classify concurrent never-overwrite as established.

Use copied fixture vaults only. Hash the pristine fixture before and after each scenario and report every changed path.
