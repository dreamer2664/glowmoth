# PHASES — core-loop

| phase | deliverable | required evidence | min_hours |
|---|---|---|---|
| P1 | grove generator + 5 seed dumps | `evidence/p1-seeds/` (5 JSON dumps) | 2.0 |
| P2 | lantern + moths + tick replay | `evidence/p2-replay/tick-log.txt`, `evidence/p2-replay/state-hash.txt` | 2.5 |
| P3 | co-op loop + replication state machine | `evidence/p3-loop.md` (state diagram + event list) | 2.0 |
| P4 | determinism + QC cycle | `evidence/p4-determinism.txt` (2 runs, identical hashes), `evidence/p4-SELF_REVIEW.md` (≥1 real defect-fix cycle) | 1.5 |

**Total floor: 8.0 h.** Pair handshake: both lumen and tinker checkpoint each phase
within 15 minutes of each other.
