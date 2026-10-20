# PROJECT.md — GLOWMOTH: Lantern Woods
<!-- project brief · law lives in dreamer2664/agency (link, never copy) · EPOCH 2026-10-20.3 -->

## The game (30 seconds)

**Glowmoth** is a co-op Roblox experience for 2–4 players: you are a
**lantern-keeper** — you carry the last light through an endless procedural night
forest, guiding lost moths home to their groves before your lantern dies. Light is
health, heat, currency, and compass. The forest is dark on purpose.

## Pillars (every decision answers to these)

1. **Glow > darkness.** Light is the verb. Everything the player does is about
   making, keeping, sharing, or spending light.
2. **Together > alone.** Co-op is the default: lanterns merge, moths follow two
   keepers farther than one, a downed keeper can be revived with shared flame.
3. **Wonder > grind.** No currency treadmills. Sessions of 8–12 minutes that end
   with a story worth retelling.

## Specs (the contract's numbers)

| thing | spec |
|---|---|
| platform | Roblox · Luau · code-built environments (seeded generation, `Random.new(seed)`) |
| players | 2–4 co-op, public sessions |
| session loop | 8–12 min: grove → grove, escalating wind/darkness, boss-weather finale |
| launch content | one biome (Lantern Woods) + procedural grove variety · 6 moth species |
| feel | 60 fps on mid hardware · no hard fail states — losing is beautiful (the light goes out; the moths remember) |
| persistence | simple save: species discovered, lantern colors, keeper rank |

## The honest boundary (Riveter's lesson — "headless ≠ engine")

Agents can build and statically verify everything in this repo (Luau, generation
logic, validators). **Roblox Studio play-testing is a named boundary**: any report
must say explicitly what was verified headlessly vs. what awaits Studio play.
"Runs in Studio" is a claim a human or a Studio-equipped agent must back.

## Lanes

| lane | who | what lives there |
|---|---|---|
| `src/core/` | lumen + tinker (PAIR) | generation, light mechanics, replication, game loop |
| `src/story/` | marlowe | quests, progression, saves, UI copy |
| `src/feel/` | piper | audio, VFX polish, game feel, camera |
| `tools/`, `tests/` | rook | validators, QC gauntlet, evidence tooling |
| `assets/` | everyone | named outputs only, manifest in `assets/INDEX.md` |

Work on your own branch (`agent/<you>/<job-id>`; the pair shares
`agent/pair/<job-id>`). Never edit another lane without a `groupchatcode` collision
call first.
