# BRIEF — core-loop (PAIR: lumen + tinker)
**Lane:** `src/core/` · **Branch:** `agent/pair/core-loop` · **Size:** L (floor 8h)

## Deliverable (the contract)

One playable co-op slice of GLOWMOTH, headlessly verifiable:

1. **Procedural grove generator** (`src/core/grove.luau`): seeded (`Random.new(seed)`),
   deterministic per seed, produces a walkable grove: trees, glades, moth nests,
   light sources. `tools/`-callable: dump the scene graph of seed N to JSON.
2. **The lantern system** (`src/core/lantern.luau`): light = health/heat/compass.
   Fuel drains, refills at nests, merges when keepers are near, dies at zero with
   a logged death event. Deterministic given a tick log.
3. **Moth pathing** (`src/core/moths.luau`): 2 species minimum, follow light,
   flee wind, return to nests. No orphan instances on despawn (tinker's edge case).
4. **Co-op loop**: 2-player join → 3-grove run → storm finale → save the light.
   Replication-safe state machine (`src/core/loop.luau`).
5. `evidence/`: seed dump of 5 groves + determinism re-run hashes + a tick-log
   replay that produces identical state.

## Definition of done

- [ ] all five modules exist, `tools/check_luau.py` green, `tests/run_all.py` green
- [ ] 5 seed dumps + 2 identical determinism runs in `evidence/`
- [ ] HANDOFF shows both names' checkpoints at every phase (pair handshake)
- [ ] `bash tools/ship.sh core-loop` green · "Studio play: NOT YET — named boundary"

## Scope boundaries
- in: `src/core/`, `evidence/` for the above
- out: audio/feel (piper), story/UI (marlowe), map art beyond geometry+light

## Hard constraints
Deterministic seeds. 60 fps target stated with measured scene budgets (rook will
check numbers). Pillars first: if a feature serves no pillar, cut it and log why.
