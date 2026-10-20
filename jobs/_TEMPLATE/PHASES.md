# PHASES — t-YYYYMMDD-<slug>

<!-- Gates, not wishes. `ship` enforces both columns. -->
<!-- min_hours: elapsed since the phase-start checkpoint in HANDOFF.md -->
<!-- Early finisher rule: close before min_hours ⇒ upgrade evidence, don't stop -->

| phase | deliverable | required evidence (file names) | min_hours |
|---|---|---|---|
| P1 | <concept/plan> | `evidence/P1-<plan>.md` | 1.5 |
| P2 | <build/draft> | `evidence/P2-<draft>.*` + honest notes | 2.5 |
| P3 | <full output> | `evidence/P3-<manifest>.sha256` + decode/test log | 2.0 |
| P4 | QC loop | `evidence/P4-SELF_REVIEW.md` — ≥1 real defect-fix-reinspection cycle | 2.0 |

**Total floor: 8.0 h** — a phase's clock starts at its `phase start` line in
`HANDOFF.md` and ends at its `phase close` line. Both must carry UTC timestamps and
SHAs. Found zero defects in P4? You did not look hard enough — log what you checked.
