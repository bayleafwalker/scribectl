---
doc_id: scribectl.state-protocols
status: draft
supersedes: null
---

# Stateful protocol boundaries

This document identifies the stateful contracts that sit underneath scribectl's trust rules. It does not amend `DESIGN.md`, `ARCHITECTURE.md`, `DISPATCH.md`, or `RATIFICATION.md`; those remain the intent sources.

## Authority map

| State | Authority | Projection or evidence |
|---|---|---|
| Canon facts | Human-authored nodes plus accepted ratification receipts | `canon_status` and context packs |
| Candidate verdict | Writer checkbox in the ratification inbox | Sweep receipts and target-node facts |
| Card readiness | Vault artifacts and links | Derived project/card status |
| Draft/review completion | New files in designated output directories | Dispatch planning |
| Generation provenance | Frozen pack content and `pack_sha` | Draft/review frontmatter |
| Sprint execution | Shared sprintctl state | Rendered sprint snapshot |

Derived status is never more authoritative than the artifacts and receipts it reads.

## Artifact landing

The dispatcher may create drafts, reviews, and frozen packs in designated paths. It must never overwrite a pre-existing artifact. Success is observed when a complete file exists with deterministic frontmatter and the expected pack receipt.

Current `_write_new` behavior checks `path.exists()` and then calls `write_text()`. This rejects sequential overwrite attempts but leaves a check-then-write race between independent processes. Concurrent never-overwrite remains unverified until landing uses an exclusive-create or atomic reservation protocol and tests establish it.

An interrupted call after file creation but before response has an unknown outcome. Recovery is read-and-reconcile from the intended path and receipt, never blind regeneration over an existing file.

## Context-pack receipt

`build_pack` derives a minimal pack from current canon, card scope, voice guidance, timeline, and exclusions. The embedded SHA identifies the generated body. A draft or review receipt is valid only if it matches the exact frozen pack supplied to the runner.

Pack generation is deterministic only within its documented inputs. Generated dates, input ordering, or source mutation must not be ignored when claiming stable hashes.

## Mining

Mining reads review reports and fact proposals, then queues pending inbox candidates. A `via [[artifact]]` marker in the inbox or ledger is the idempotency proof. Re-running mining over stable inputs should append nothing.

Mining never supplies a verdict. Confidence and conflict signals only order the newly mined batch.

## Ratification sweep

The writer's checkbox is the only verdict. Sweep may transform target nodes, append ledger receipts, and remove resolved inbox candidates. These are multiple filesystem effects rather than one filesystem transaction.

A crash or competing sweep can produce partial effects unless the CLI detects and reconciles receipts and target facts. Verification must exercise interruption between each durable write and distinguish safe replay from manual reconciliation. No automated path may infer acceptance from a review verdict or confidence field.

## Safety properties

- Existing human-authored files are never overwritten by dispatch.
- Every landed generated artifact identifies its runner and governing pack receipt.
- Mining is idempotent by source-artifact marker.
- Pending, deferred, rejected, and accepted candidates remain distinguishable.
- Only an explicit accepted checkbox can promote a fact and append an accepted receipt.
- Derived status is reproducible from the same vault snapshot.

## Liveness

- No multi-process fairness guarantee is made.
- Ambient watch progresses only while the vault is settled and the process is healthy.
- Writer action is required for ratification; pending candidates may remain pending indefinitely by design.

## Verification

Reusable contexts live in `verification/contexts/`. Run them only against copied fixture vaults. A result must name the fixture revision, pack/content hashes, changed paths, fault points, and evidence classification.
