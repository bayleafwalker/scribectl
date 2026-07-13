---
type: ratification_inbox
---

# Ratification Inbox

Everything that proposes canon queues candidates here; the verdict is a
checkbox. Rewrite the fact text in place before ticking if you want — the
rewrite is the ratified wording. Then run `scribectl ratify --sweep`:

- `[x]` accept — fact lands in the node, receipt in the ledger
- `[-]` reject — receipt in the ledger
- `[>]` defer — receipt in the ledger, cleared from this inbox
- `[ ]` undecided — stays here, untouched

Candidate grammar (this fenced example is invisible to the sweep):

```
- [ ] "the claim, worded as it should read settled" → [[Target Node]]
      (from [[Draft note]], pack 0123abcdef01)
```
