#!/usr/bin/env python3
"""test_watch.py — the watch finds problems at a fixed clock."""
import json, os, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def fresh_repo():
    d = tempfile.mkdtemp(prefix="agency-w-")
    for p in ("agents", "board/tasks", "board/heartbeats", "board/votes", "jobs"):
        os.makedirs(os.path.join(d, p), exist_ok=True)
    return d

def run(repo, *args, expect=0, agent="watchdog"):
    e = {**os.environ, "AGENCY_DIR": repo, "AGENCY_NO_PUSH": "1", "AGENCY_AGENT": agent}
    r = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, env=e)
    if expect != "any":
        assert r.returncode == expect, f"{args} -> {r.returncode}\n{r.stdout}\n{r.stderr}"
    return r

def main():
    t0 = time.time()
    repo = fresh_repo()
    now = "2026-10-20T12:00:00Z"
    try:
        # agent mid-lifecycle holding an expired task lease
        json.dump({"name": "ghost", "role": "worker", "kind": "ai",
                   "joined_ts": "2026-10-18T12:00:00Z", "last_seen": "2026-10-20T10:00:00Z",
                   "epoch": "x"},
                  open(os.path.join(repo, "agents", "ghost.json"), "w"))
        json.dump({"id": "t-z", "title": "zombie", "status": "claimed", "owner": "ghost",
                   "lease": {"agent": "ghost", "since": "2026-10-20T09:00:00Z",
                             "expires": "2026-10-20T10:00:00Z", "checkpoint": ""},
                   "updated_ts": "2026-10-20T09:00:00Z", "history": []},
                  open(os.path.join(repo, "board", "tasks", "t-z.json"), "w"))

        # a review card starving for 60h with no ballots
        json.dump({"id": "t-r", "title": "shipped, unverified", "status": "review",
                   "owner": "ghost", "lease": None,
                   "created_ts": "2026-10-18T00:00:00Z", "updated_ts": "2026-10-18T00:00:00Z",
                   "history": []},
                  open(os.path.join(repo, "board", "tasks", "t-r.json"), "w"))

        # an AGING agent holding a live job
        json.dump({"name": "oldster", "role": "worker", "kind": "ai",
                   "joined_ts": "2026-10-18T12:00:00Z", "last_seen": "2026-10-20T11:50:00Z",
                   "epoch": "x"},
                  open(os.path.join(repo, "agents", "oldster.json"), "w"))
        jd = os.path.join(repo, "jobs", "t-j")
        os.makedirs(jd)
        json.dump({"agent": "oldster", "ts": "2026-10-20T11:00:00Z",
                   "lease_expires": "2026-10-20T23:00:00Z", "epoch": "x"},
                  open(os.path.join(jd, "CLAIM.oldster.json"), "w"))

        r = run(repo, "watch", "--now", now, expect="any")
        out = r.stdout
        assert r.returncode == 1
        assert "SWEEP" in out and "t-z" in out
        assert "UNVERIFIED" in out and "t-r" in out
        assert "ROTATE" in out and "oldster" in out
        assert "CLOCK" in out and "AGING" in out

        # quiet repo → exit 0
        repo2 = fresh_repo()
        r = run(repo2, "watch", "--now", now, expect="any")
        assert r.returncode == 0 and "all quiet" in r.stdout

        print(f"6 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
