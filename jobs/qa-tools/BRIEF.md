# BRIEF — qa-tools (SOLO: rook)
**Lane:** `tools/`, `tests/` · **Branch:** `agent/rook/qa-tools` · **Size:** M (floor 6h)

## Deliverable

1. **The gauntlet** (`tools/verify_grove.py`): given a seed dump JSON, check —
   walkability graph connectivity, light-source count bounds, nest reachability,
   instance budget. Exit non-zero with precise reasons. This is what every other
   lane will be graded by: make it strict and fair.
2. **Determinism harness** (`tools/rerun.py`): runs the same seed twice, hashes
   state, reports equality. Wire it into `SHIP_GATE.md`.
3. **The QC timer** (`tools/qc_timer.py`): given a PHASES.md, reports phases at
   risk of floor-violation or evidence-missing — the crew's early-warning.
4. `evidence/`: the gauntlet run against lumen's P1 seed dumps (or fixtures of
   your own if they aren't there yet — state which), plus `gauntlet-self-test.md`
   (prove it catches 3 seeded defects you planted).

## Definition of done
- [ ] three tools run, `tools/check_luau.py` green
- [ ] gauntlet self-test catches all 3 planted defects
- [ ] `bash tools/ship.sh qa-tools` green

## Scope boundaries
- in: `tools/`, `tests/`
- out: fixing others' bugs — file to `bugs/INBOX.md`, they triage

## Hard constraints
The gauntlet never lies for convenience. A check that can't fail is deleted.
Report the Studio boundary honestly in every tool's docstring.
