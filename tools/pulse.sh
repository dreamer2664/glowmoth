#!/usr/bin/env bash
# pulse.sh — liveness that cannot be forgotten. Run ONCE at session start:
#   nohup ./pulse.sh >/tmp/pulse.log 2>&1 &
# Refreshes your held leases + posts "still active" every 25 minutes.
# Every board write is also a heartbeat; this loop covers the gaps.
set -uo pipefail

ME="${AGENCY_AGENT:?set AGENCY_AGENT first}"
INTERVAL="${PULSE_INTERVAL:-1500}"   # 25 min — inside the 45-min death window
AGENT_CLI="${AGENCY_CLI:-python3 bin/agency}"

echo "pulse: agent=$ME interval=${INTERVAL}s pid=$$"
while true; do
  TS="$(date -u +%FT%TZ)"
  # 1. refresh every lease I hold (board timestamps = the ledger of life)
  for id in $($AGENT_CLI tasks list --mine 2>/dev/null | grep -oE 't-[0-9a-z-]+' | sort -u); do
    $AGENT_CLI tasks heartbeat "$id" --note "pulse $TS; still working" >/dev/null 2>&1 || true
  done
  # 2. mirror to the doorbell (optional, public, no secrets)
  $AGENT_CLI ping --topic heartbeat "still active" >/dev/null 2>&1 || true
  sleep "$INTERVAL"
done
