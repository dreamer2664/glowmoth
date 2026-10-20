#!/usr/bin/env bash
# ship.sh — a worker merges its own work. Merge authority follows the gate.
# Ship is a command, not a permission. Tier-law files are rejected here.
#
# usage: ./ship.sh <job-or-task-id> [--remote-only]
# env:   AGENCY_AGENT=<you>  (required)
#        GITHUB_TOKEN (for push + ledger)
set -euo pipefail

ID="${1:?usage: ship.sh <job-or-task-id>}"
ME="${AGENCY_AGENT:?set AGENCY_AGENT first}"
REPO_DIR="$(git rev-parse --show-toplevel)"
cd "$REPO_DIR"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
TODAY="$(date -u +%Y-%m-%dT%H:%MZ)"

fail() { echo "SHIP REFUSED: $*" >&2; exit 1; }

# ---- 0. identity & branch discipline -------------------------------------
case "$BRANCH" in
  agent/"$ME"/*) ;;
  main|master) fail "you are on $BRANCH — ship from agent/$ME/<id>" ;;
  *) fail "branch '$BRANCH' does not match agent/$ME/<id>" ;;
esac

# ---- 1. fail-closed preconditions ---------------------------------------
# tier-law files must never ride a worker ship
if git diff --name-only origin/main...HEAD | grep -qE \
  '^(START_HERE\.md|ORDERS\.md|SHIP_GATE\.md|bin/|\.github/)'; then
  fail "this diff touches tier-law files (START_HERE/ORDERS/SHIP_GATE/bin/.github) — needs 2 pre-merge votes + Director"
fi

# secrets sweep: no NEW token-looking strings in ADDED lines only (R3).
# (context lines may legally carry the Director-stamped kit in START_HERE.md;
#  the gate watches what YOU add, not what already lives on main)
if git diff origin/main...HEAD | grep -E '^\+' | grep -qE 'github_pat_[A-Za-z0-9_]{20,}|CHATCODE_TOKEN=[^P ].{10,}|GITHUB_TOKEN=[^P ].{10,}'; then
  fail "possible secret in added lines (R3) — inspect before shipping"
fi

[ -f SHIP_GATE.md ] || fail "no SHIP_GATE.md in this repo — the repo owner must define the gate first"

# phase gates for jobs: THE GATE is mechanical (bin/agency jobs gate)
JOB_DIR="$(ls -d jobs/"$ID" 2>/dev/null || true)"
if [ -n "$JOB_DIR" ]; then
  python3 bin/agency jobs gate "$ID" || fail "job gate red for $ID (see above: floors, evidence, checkpoints)"
fi

# ---- 2. THE GATE: run exactly what SHIP_GATE.md lists ---------------------
echo "== ship gate: running SHIP_GATE.md =="
# SHIP_GATE.md format: lines starting with '$ ' are commands; run them in order.
grep '^\$ ' SHIP_GATE.md | sed 's/^\$ //' | while read -r cmd; do
  echo "+ $cmd"
  eval "$cmd" || fail "gate command failed: $cmd"
done
echo "== gate green =="

# ---- 3. merge, push, VERIFY REMOTE (R6: a 200 is not a push) -------------
git fetch origin main
git rebase origin/main
MAIN_SHA_BEFORE="$(git rev-parse origin/main)"
git checkout main && git pull --ff-only origin main
git merge --squash "$BRANCH" && git commit -m "ship($ME): $ID from $BRANCH"
git push origin main
MAIN_SHA_AFTER="$(git rev-parse origin/main)"
git fetch origin main
[ "$(git rev-parse origin/main)" = "$MAIN_SHA_AFTER" ] || fail "remote readback mismatch — the push did not stick"

# ---- 4. receipts: ledger + job folder + acceptance request ----------------
if [ -d ../storagecode ]; then
  ROW="| $(date -u +%F) | $ME | $(basename "$REPO_DIR") | $BRANCH @${MAIN_SHA_AFTER:0:12} | ship($ID): gate green, squash-merged | 2 post-merge accept-inspected ballots (48h) |"
  printf '%s\n' "$ROW" >> ../storagecode/PUSHES.md
  ( cd ../storagecode && git add PUSHES.md && git commit -m "ledger: $ME shipped $ID" && git push )
fi

if [ -n "$JOB_DIR" ]; then
  {
    echo "$(date -u +%FT%TZ) · $ME · phase close · shipped @${MAIN_SHA_AFTER:0:12} · next: request 2 accept-inspected ballots · blocker: —"
    echo "acceptance: PENDING (2 non-owner ballots, 48h window, deny→revert)"
  } >> "$JOB_DIR/HANDOFF.md"
  git add "$JOB_DIR" && git commit -m "handoff: $ID shipped @${MAIN_SHA_AFTER:0:12}" && git push origin main || true
fi

# formalcode is automatic (record.yml) — do not announce the push yourself.
# Ask for ballots (statement, not a question):
if command -v python3 >/dev/null; then
  python3 bin/agency ping --topic jobs \
    "$ME: $ID shipped @${MAIN_SHA_AFTER:0:12}; gate green; 2 accept-inspected ballots needed (48h)" \
    || true
fi

echo "SHIPPED: $ID @${MAIN_SHA_AFTER:0:12} — acceptance pending (post-merge, 2 ballots)"
