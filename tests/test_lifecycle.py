#!/usr/bin/env python3
"""test_lifecycle.py — ROOKIE/AGING/RETIRED claim gating is mechanical."""
import json, os, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def fresh_repo():
    d = tempfile.mkdtemp(prefix="agency-lc-")
    for p in ("agents", "board/tasks", "board/heartbeats", "board/votes", "jobs"):
        os.makedirs(os.path.join(d, p), exist_ok=True)
    jd = os.path.join(d, "jobs", "t-big")
    os.makedirs(jd)
    open(os.path.join(jd, "BRIEF.md"), "w").write("# big\n")
    open(os.path.join(jd, "PHASES.md"), "w").write(
        "| phase | deliverable | required evidence | min_hours |\n|---|---|---|---|\n"
        "| P1 | all of it | `evidence/x` | 8.0 |\n")
    open(os.path.join(jd, "HANDOFF.md"), "w").write("# h\n")
    return d

def run(repo, *args, expect=0, agent="nova"):
    e = {**os.environ, "AGENCY_DIR": repo, "AGENCY_NO_PUSH": "1", "AGENCY_AGENT": agent}
    r = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, env=e)
    if expect != "any":
        assert r.returncode == expect, f"{args} -> {r.returncode}\n{r.stdout}\n{r.stderr}"
    return r

def set_age(repo, name, hours_ago):
    p = os.path.join(repo, "agents", f"{name}.json")
    d = json.load(open(p))
    d["joined_ts"] = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump(d, open(p, "w"))

def main():
    t0 = time.time()
    repo = fresh_repo()
    try:
        for n in ("nova", "rex", "ada", "boss"):
            run(repo, "init", "--name", n)
        # boss is a lead — exempt
        p = os.path.join(repo, "agents", "boss.json")
        d = json.load(open(p)); d["role"] = "lead"; json.dump(d, open(p, "w"))

        # ROOKIE (1h old): small task OK, big job refused
        set_age(repo, "nova", 1)
        run(repo, "tasks", "new", "--title", "small", "--id", "t-s")
        run(repo, "tasks", "claim", "t-s", "--hours", "2", agent="nova")
        r = run(repo, "jobs", "claim", "t-big", agent="nova", expect="any")
        assert r.returncode != 0 and "ROOKIE" in r.stderr, r.stderr

        # ROOKIE also refused a >4h task
        run(repo, "tasks", "new", "--title", "bigish", "--id", "t-b")
        r = run(repo, "tasks", "claim", "t-b", "--hours", "5", agent="nova", expect="any")
        assert r.returncode != 0 and "ROOKIE" in r.stderr

        # FULL (30h old): the big job is allowed
        set_age(repo, "rex", 30)
        run(repo, "jobs", "claim", "t-big", "--hours", "8", agent="rex")

        # AGING (50h old): no new claims at all
        set_age(repo, "ada", 50)
        run(repo, "tasks", "new", "--title", "x", "--id", "t-x")
        r = run(repo, "tasks", "claim", "t-x", agent="ada", expect="any")
        assert r.returncode != 0 and "AGING" in r.stderr

        # RETIRED (70h): refused even small claims
        set_age(repo, "nova", 70)
        run(repo, "tasks", "new", "--title", "y", "--id", "t-y")
        r = run(repo, "tasks", "claim", "t-y", "--hours", "1", agent="nova", expect="any")
        assert r.returncode != 0 and "RETIRED" in r.stderr

        # lead skips the ROOKIE size cap …
        set_age(repo, "boss", 1)
        r = run(repo, "tasks", "claim", "t-b", "--hours", "5", agent="boss")
        assert "claimed" in r.stdout
        # … but the clock binds leads too — degradation spares nobody
        run(repo, "tasks", "release", "t-b", agent="boss")
        set_age(repo, "boss", 70)
        r = run(repo, "tasks", "claim", "t-b", "--hours", "1", agent="boss", expect="any")
        assert r.returncode != 0 and "RETIRED" in r.stderr

        print(f"7 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
