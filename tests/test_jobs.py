#!/usr/bin/env python3
"""test_jobs.py — job folders: claim files, double-claim refusal, checkpoints."""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def fresh_repo():
    d = tempfile.mkdtemp(prefix="agency-jobs-")
    for p in ("agents", "board/tasks", "board/heartbeats", "board/votes", "jobs"):
        os.makedirs(os.path.join(d, p), exist_ok=True)
    os.makedirs(os.path.join(d, "jobs", "t-1-blend"), exist_ok=True)
    open(os.path.join(d, "jobs", "t-1-blend", "BRIEF.md"), "w").write("# brief\n")
    open(os.path.join(d, "jobs", "t-1-blend", "PHASES.md"), "w").write("| phase | min_hours |\n")
    open(os.path.join(d, "jobs", "t-1-blend", "HANDOFF.md"), "w").write("# handoff\n")
    return d

def run(repo, *args, expect=0, agent="nova"):
    e = {**os.environ, "AGENCY_DIR": repo, "AGENCY_NO_PUSH": "1", "AGENCY_AGENT": agent}
    r = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, env=e)
    if expect != "any":
        assert r.returncode == expect, f"{args} -> {r.returncode}\n{r.stdout}\n{r.stderr}"
    return r

def main():
    t0 = time.time()
    repo = fresh_repo()
    try:
        run(repo, "init", "--name", "nova")
        run(repo, "init", "--name", "rex")
        # backdate both to FULL age (30h): this file tests job mechanics, not lifecycle
        from datetime import datetime, timezone, timedelta
        full = (datetime.now(timezone.utc) - timedelta(hours=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for n in ("nova", "rex"):
            p = os.path.join(repo, "agents", f"{n}.json")
            d = json.load(open(p))
            d["joined_ts"] = full
            json.dump(d, open(p, "w"))

        r = run(repo, "jobs", "list")
        assert "t-1-blend" in r.stdout

        r = run(repo, "jobs", "claim", "t-1-blend", "--hours", "8")
        assert "claimed t-1-blend" in r.stdout
        claim = json.load(open(os.path.join(repo, "jobs", "t-1-blend", "CLAIM.nova.json")))
        assert claim["agent"] == "nova" and claim["lease_hours"] == 8

        r = run(repo, "jobs", "claim", "t-1-blend", agent="rex", expect="any")
        assert r.returncode != 0, "second agent must not steal a live claim"

        run(repo, "jobs", "heartbeat", "t-1-blend", "--note", "P1 close @abc", agent="nova")
        hb = open(os.path.join(repo, "jobs", "t-1-blend", "HANDOFF.md")).read()
        assert "P1 close @abc" in hb

        run(repo, "jobs", "release", "t-1-blend", "--note", "blocked on render", agent="nova")
        st = json.load(open(os.path.join(repo, "jobs", "t-1-blend", "STATUS.json")))
        assert st["status"] == "released" and st["owner"] is None

        # after release + expiry, rex can take it
        p = os.path.join(repo, "jobs", "t-1-blend", "CLAIM.nova.json")
        c = json.load(open(p))
        c["lease_expires"] = "2020-01-01T00:00:00Z"
        json.dump(c, open(p, "w"))
        r = run(repo, "jobs", "claim", "t-1-blend", agent="rex", expect="any")
        assert r.returncode == 0, f"expired claim must not block: {r.stderr}"

        print(f"5 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
