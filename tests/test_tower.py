#!/usr/bin/env python3
"""test_tower.py — liveness verdicts and zombie detection at fixed clocks."""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def fresh_repo():
    d = tempfile.mkdtemp(prefix="agency-tower-")
    for p in ("agents", "board/tasks", "board/heartbeats", "board/votes", "jobs"):
        os.makedirs(os.path.join(d, p), exist_ok=True)
    return d

def run(repo, *args, agent="nova", expect=0):
    e = {**os.environ, "AGENCY_DIR": repo, "AGENCY_NO_PUSH": "1", "AGENCY_AGENT": agent}
    r = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, env=e)
    if expect != "any":
        assert r.returncode == expect, f"{args} -> {r.returncode}\n{r.stdout}\n{r.stderr}"
    return r

def main():
    t0 = time.time()
    repo = fresh_repo()
    try:
        # three agents last seen at different ages relative to fixed 'now'
        now = "2026-10-20T12:00:00Z"
        for name, seen in (("alive1", "2026-10-20T11:50:00Z"),
                           ("stale1", "2026-10-20T11:25:00Z"),
                           ("dead1",  "2026-10-20T10:00:00Z")):
            os.makedirs(os.path.join(repo, "agents"), exist_ok=True)
            json.dump({"name": name, "role": "worker", "kind": "ai",
                       "last_seen": seen, "joined_ts": seen, "epoch": "x"},
                      open(os.path.join(repo, "agents", f"{name}.json"), "w"))

        # dead1 holds a claimed task → zombie lease
        json.dump({"id": "t-z", "title": "zombie", "status": "claimed", "owner": "dead1",
                   "lease": {"agent": "dead1", "since": "2026-10-20T10:00:00Z",
                             "expires": "2026-10-20T11:00:00Z", "checkpoint": ""},
                   "history": []},
                  open(os.path.join(repo, "board", "tasks", "t-z.json"), "w"))

        r = run(repo, "tower", "--json", "--now", now, expect="any")
        d = json.loads(r.stdout)
        assert d["verdicts"] == {"ALIVE": 1, "STALE": 1, "DEAD": 1, "COLD": 0}, d["verdicts"]
        assert d["zombie_leases"] == ["dead1"]
        assert r.returncode == 1, "tower must exit 1 when zombies exist"

        r = run(repo, "tower", "--now", now, expect="any")
        assert r.returncode == 1  # zombies present
        assert "1 alive · 1 stale · 1 dead" in r.stdout
        assert "ZOMBIE" in r.stdout and "t-z" in r.stdout

        # sweep --apply clears the zombie
        run(repo, "sweep", "--apply", agent="alive1", expect="any")
        r = run(repo, "tower", "--json", "--now", now, expect="any")
        d = json.loads(r.stdout)
        assert d["zombie_leases"] == []
        assert r.returncode == 0

        print(f"5 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
