# BRIEF — story-ui (SOLO: marlowe)
**Lane:** `src/story/` · **Branch:** `agent/marlowe/story-ui` · **Size:** M (floor 6h)

## Deliverable

1. **Quest chain** (`src/story/quests.luau`): a 3-act, 6-step first-run chain that
   teaches the pillars without a tutorial screen (the moths teach by behavior).
2. **Progression + save** (`src/story/save.luau`): species discovered, lantern
   colors, keeper rank. Deterministic round-trip: save → load → save must hash equal.
3. **The codex** (`src/story/codex.luau`): 6 moth species with 2-line entries each
   (voice: marlowe, warm). Plus all user-facing strings in `src/story/strings.luau`.
4. `evidence/`: save round-trip hash proof + the full codex text + a strings audit
   (every UI surface covered — list which surfaces).

## Definition of done
- [ ] modules exist, static checks green
- [ ] save round-trip hash proof in `evidence/`
- [ ] `bash tools/ship.sh story-ui` green

## Scope boundaries
- in: `src/story/`, UI copy
- out: UI layout/animation (feel/piper pairs on that at integration), core mechanics

## Hard constraints
No lorem ipsum. Every string final-quality. Story that needs a screen to make
sense is wrong — the world teaches.
