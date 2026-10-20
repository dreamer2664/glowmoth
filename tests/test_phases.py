#!/usr/bin/env python3
"""test_phases.py — the 8h rule is mechanical: floors, evidence, gate."""
import json, os, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def fresh_repo():
    d = tempfile.mkdtemp(prefix="agency-ph-")
    for p in ("agents", "board/tasks", "board/heartbeats", "board/votes", "jobs"):
        os.makedirs(os.path.join(d, p), exist_ok=True)
    jd = os.path.join(d, "jobs", "t-big")
    os.makedirs(jd)
    open(os.path.join(jd, "BRIEF.md"), "w").write("# big job\n")
    open(os.path.join(jd, "PHASES.md"), "w").write(
        "| phase | deliverable | required evidence | min_hours |\n"
        "|---|---|---|---|\n"
        "| P1 | concept | `evidence/p1.txt` | 2.0 |\n"
        "| P2 | build | `evidence/p2.txt` | 3.0 |\n")
    open(os.path.join(jd, "HANDOFF.md"), "w").write("# handoff\n")
    os.makedirs(os.path.join(jd, "evidence"))
    return d

def run(repo, *args, expect=0, agent="nova"):
    e = {**os.environ, "AGENCY_DIR": repo, "AGENCY_NO_PUSH": "1", "AGENCY_AGENT": agent}
    r = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, env=e)
    if expect != "any":
        assert r.returncode == expect, f"{args} -> {r.returncode}\n{r.stdout}\n{r.stderr}"
    return r

def backdate_start(repo, jid, phase, hours_ago):
    """Rewrite the start ts of a phase so floors can be tested without waiting."""
    p = os.path.join(repo, "jobs", jid, "PHASELOG.jsonl")
    lines = [json.loads(l) for l in open(p) if l.strip()]
    for e in lines:
        if e.get("phase") == phase and e.get("action") == "start":
            t = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
            e["ts"] = t.strftime("%Y-%m-%dT%H:%M:%SZ")
    open(p, "w").write("".join(json.dumps(e, sort_keys=True) + "\n" for e in lines))

def main():
    t0 = time.time()
    repo = fresh_repo()
    try:
        run(repo, "init", "--name", "nova")
        # full-age agent (this is not a lifecycle test)
        p = os.path.join(repo, "agents", "nova.json")
        d = json.load(open(p))
        d["joined_ts"] = "2026-10-10T00:00:00Z"
        json.dump(d, open(p, "w"))

        run(repo, "jobs", "phase", "t-big", "start", "P1")
        # close before floor → refused
        r = run(repo, "jobs", "phase", "t-big", "close", "P1", expect="any")
        assert r.returncode != 0 and "floor" in r.stderr, r.stderr

        # backdate 2.1h; close without evidence → refused
        backdate_start(repo, "t-big", "P1", 2.1)
        r = run(repo, "jobs", "phase", "t-big", "close", "P1", expect="any")
        assert r.returncode != 0 and "evidence missing" in r.stderr, r.stderr

        # write evidence; close → ok
        open(os.path.join(repo, "jobs", "t-big", "evidence", "p1.txt"), "w").write("ok\n")
        r = run(repo, "jobs", "phase", "t-big", "close", "P1")
        assert "closed after" in r.stdout

        # gate is red until P2 is done
        r = run(repo, "jobs", "gate", "t-big", expect="any")
        assert r.returncode == 1 and "P2" in r.stdout

        # P2 full cycle with backdating
        run(repo, "jobs", "phase", "t-big", "start", "P2")
        backdate_start(repo, "t-big", "P2", 3.2)
        open(os.path.join(repo, "jobs", "t-big", "evidence", "p2.txt"), "w").write("ok\n")
        with open(os.path.join(repo, "jobs", "t-big", "HANDOFF.md"), "a") as f:
            f.write("2026-10-20T10:00:00Z · nova · phase P1 close · done\n"
                    "2026-10-20T11:00:00Z · nova · phase P2 close · done\n")
        run(repo, "jobs", "phase", "t-big", "close", "P2")

        # gate green
        r = run(repo, "jobs", "gate", "t-big", expect="any")
        assert r.returncode == 0, r.stdout
        assert "GREEN" in r.stdout

        # phases listing shows both closed
        r = run(repo, "jobs", "phases", "t-big", expect="any")
        assert "CLOSED" in r.stdout and "GREEN" in r.stdout

        print(f"7 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
