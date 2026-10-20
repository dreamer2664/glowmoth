# BRIEF — audio-feel (SOLO: piper)
**Lane:** `src/feel/` · **Branch:** `agent/piper/audio-feel` · **Size:** M (floor 6h)

## Deliverable

1. **Audio spine** (`src/feel/audio.luau`): event-driven cues — lantern low (the
   half-second before it dies is its own sound), moth swarm, wind rising, grove
   saved. Spec sheet in `evidence/p1-audio-spec.md`: every cue, trigger, priority.
2. **Game feel** (`src/feel/juice.luau`): camera (storm shake budget in ms),
   lantern glow pulse, footstep timing table (yes, the table is required — but it
   ships in P2, not hour 3 of P1).
3. **VFX timing** (`src/feel/vfx.luau`): light fades, moth trails, death-of-light
   moment (this is the game's emotional beat — treat it like one).
4. `evidence/`: cue spec + measured timing table + a `feel-budget.md` (frame ms
   budgets for camera/vfx, stated numbers rook can check).

## Definition of done
- [ ] modules + specs exist, static checks green
- [ ] feel-budget.md has real numbers
- [ ] `bash tools/ship.sh audio-feel` green

## Scope boundaries
- in: `src/feel/`
- out: mechanics (tinker owns), copy (marlowe owns)

## Hard constraints
Audio without numbers is vibes: every cue needs trigger + priority. The
death-of-light moment ships once, fully — not half-polished twice.
