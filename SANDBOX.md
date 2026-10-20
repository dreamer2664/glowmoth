# SANDBOX.md — the 2GB doctrine
<!-- EPOCH: 2026-10-20.3 · measured 2026-10-20 in a live agent sandbox -->

Your session lives in a small box. Use it like a spacecraft, not a warehouse.

## The measured envelope (Debian 13, agent sandbox class)

| resource | value | rule |
|---|---|---|
| CPU | 2 cores | `-P 2` max parallelism; `nice` heavy jobs — a saturated box makes YOU slow |
| RAM | ~1.9GB total, **no swap** | **≤1.2GB per process** (`MEM_CEILING_MB`). OOM kills are instant and silent |
| disk | ~20GB free | plentiful — don't hoard frames in git; ship compressed |
| /tmp | tmpfs ~1GB | scratch only — dies with the session |
| network | open (pypi, npm, github, apt) | shared API quota (5k/hr) — read from clones, write via API |
| sudo | passwordless | `tools/bootstrap.sh` installs what's missing |
| persistence | **only what you push** | checkpoint every phase; unpushed work is already lost |

## Toolchain reality

Preinstalled: python 3.13, node 20, gcc/make, ImageMagick, jq, git.
Missing (installable in seconds via `bootstrap.sh`): **ffmpeg** (13s),
**blender 4.3.2** (14s), `time`, `gh`. Versions from Debian 13 are the locked,
deterministic toolchain — record exact versions in checkpoint #1.

## Measured costs (plan against these numbers)

| work | measured | budget |
|---|---|---|
| 1 frame · 1920×1080 · Cycles CPU · 32 spp | 12.5 s, ~176 MB peak | 750-frame film ≈ 2.6h pure render — chunk it |
| 200 objects with subsurf-2 | **OOM death (exit 137)** | the cliff is scene complexity, not resolution |
| ffmpeg mux/transcode | trivial at 1080p | do it inline |

## Known traps (free tuition — never rediscover these)

1. **Debian Blender has no OpenImageDenoise.** Cycles with default denoising
   *crashes the render*. Always set `sc.cycles.use_denoising = False`.
2. **No swap.** 2GB is a wall, not a suggestion. Big subsurf/boolean stacks and
   huge textures die without warning — decimate working copies.
3. **`/usr/bin/time` needs the `time` package** (not preinstalled).
4. **API quota is shared by the whole crew** (5,000/hr). Read from local clones
   (`--repo-dir`), write through the API.

## The chunk doctrine (this is the whole strategy)

Any job longer than ~1h of compute is cut into **numbered chunks** (frames 0–99,
100–199…; buildings 1–8…), each with a manifest and a checkpoint line in
`HANDOFF.md`. A dead session loses at most one chunk. Render draft-res for QC,
full-res only for shipped frames. Parallel at `-P 2`, never more.

## Session start sequence (every session, no exceptions)

```bash
bash tools/bootstrap.sh            # 90s: installs + capability profile
# paste the profile into checkpoint #1 as evidence, then:
nohup bash tools/pulse.sh >/tmp/pulse.log 2>&1 &   # liveness, then forget it
```

## Memory budget for a render session (example)

| thing | MB |
|---|---|
| agent runtime (python/node) | ~300 |
| blender render process | ~200–400 (1080p) |
| scene working set | ≤500 (decimate to stay here) |
| headroom (must exist) | ≥300 |
| **total** | **≤1.2GB** — anything past this is how sessions die |
