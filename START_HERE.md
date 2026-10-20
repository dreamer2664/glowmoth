# START_HERE.md — GLOWMOTH crew entry
<!-- EPOCH: 2026-10-20.3 · the LAW lives at dreamer2664/agency — this file is the project door -->

You are one of five keepers building **Glowmoth: Lantern Woods** (the game:
`PROJECT.md`; the crew and your persona: `TEAM.md`). The law of the Agency —
leases, evidence, no questions, the lifecycle clock, the red lines — lives at
**[dreamer2664/agency/START_HERE.md](https://github.com/dreamer2664/agency/blob/main/START_HERE.md)**.
Read it once. It wins every conflict.

## Arm yourself (3 minutes)

```bash
set -a; . ~/.private/<yourname>.env; set +a     # your stamped kit (Director-delivered)
export AGENCY_AGENT=<yourname>
git clone https://github.com/dreamer2664/glowmoth && cd glowmoth
git config user.name <yourname> && git config user.email <yourname>@glowmoth.local
python3 bin/agency init --name <yourname> --caps "<your lane>" --force   # roster is pre-seeded; --force stamps your arrival
bash tools/bootstrap.sh                          # 90s: sandbox capability profile
```

## Onboard (one command — the entry battery)

```bash
python3 bin/agency onboard
```

Then send your flare on **newentriescode** (exact line the command prints), and —
this project's rule — say hi on **`theagency`** in plain English (`TEAM.md` §the wire):

```
<yourname> - I just arrived and passed the entry tests. Claiming <job> now.
```

## Take your job (it's already cut for you)

| you | job | how |
|---|---|---|
| lumen | `jobs/core-loop/` | `jobs claim core-loop --hours 8 --with tinker` (pair branch: `agent/pair/core-loop`) |
| tinker | `jobs/core-loop/` | `jobs claim core-loop --hours 8 --with lumen` |
| marlowe | `jobs/story-ui/` | `jobs claim story-ui --hours 8` |
| piper | `jobs/audio-feel/` | `jobs claim audio-feel --hours 8` |
| rook | `jobs/qa-tools/` | `jobs claim qa-tools --hours 8` |

Then: read your `BRIEF.md` + `PHASES.md` → branch (created for you) →
`jobs phase <id> start P1` → build → checkpoint in `HANDOFF.md` →
`jobs phase <id> close P1` (floors + evidence enforced) → `bash tools/ship.sh <id>`.

## While you work

- **Pulse:** `nohup bash tools/pulse.sh >/tmp/pulse.log 2>&1 &` — and every push
  gets a plain-English line on `theagency`.
- **Assumptions** go in `HANDOFF.md` (`assumed: …`). Questions are protocol
  violations. Blockers are statements, then you take other work.
- **Studio boundary:** verify everything you can headlessly; name what awaits
  Roblox Studio play (PROJECT.md §honest boundary).
- **48h:** the clock says AGING → `bash tools/handoff.sh <job-id> planned-rotation`
  → a fresh keeper resumes from `RELAY.md` in five minutes.

*The forest outlives the keeper. Leave receipts.*
