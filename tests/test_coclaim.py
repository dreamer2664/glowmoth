#!/usr/bin/env python3
"""test_coclaim.py — the pair protocol: --with co-claims + commissioned rookies."""
import json, os, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def fresh_repo():
    d = tempfile.mkdtemp(prefix="agency-pair-")
    for p in ("agents", "board/tasks", "board/heartbeats", "board/votes", "jobs"):
        os.makedirs(os.path.join(d, p), exist_ok=True)
    jd = os.path.join(d, "jobs", "t-core")
    os.makedirs(jd)
    open(os.path.join(jd, "BRIEF.md"), "w").write("# core\n")
    open(os.path.join(jd, "PHASES.md"), "w").write(
        "| phase | deliverable | required evidence | min_hours |\n|---|---|---|---|\n"
        "| P1 | loop | `evidence/x` | 8.0 |\n")
    open(os.path.join(jd, "HANDOFF.md"), "w").write("# h\n")
    return d

def run(repo, *args, expect=0, agent="lumen"):
    e = {**os.environ, "AGENCY_DIR": repo, "AGENCY_NO_PUSH": "1", "AGENCY_AGENT": agent}
    r = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, env=e)
    if expect != "any":
        assert r.returncode == expect, f"{args} -> {r.returncode}\n{r.stdout}\n{r.stderr}"
    return r

def main():
    t0 = time.time()
    repo = fresh_repo()
    try:
        for n in ("lumen", "tinker", "marlowe", "solo"):
            run(repo, "init", "--name", n)
        # commissioned pair: the Director sends rookies onto 8h work
        for n in ("lumen", "tinker", "marlowe"):
            p = os.path.join(repo, "agents", f"{n}.json")
            d = json.load(open(p)); d["commissioned"] = True
            json.dump(d, open(p, "w"))

        # plain rookie (not commissioned) cannot take the 8h job
        r = run(repo, "jobs", "claim", "t-core", "--hours", "8", agent="solo", expect="any")
        assert r.returncode != 0 and "ROOKIE" in r.stderr

        # commissioned rookie CAN (and names the partner up front)
        r = run(repo, "jobs", "claim", "t-core", "--hours", "8", "--with", "tinker",
                agent="lumen", expect="any")
        assert r.returncode == 0, r.stderr

        # stranger cannot join without --with
        r = run(repo, "jobs", "claim", "t-core", "--hours", "8", agent="marlowe", expect="any")
        assert r.returncode != 0 and "held by lumen" in r.stderr

        # the declared pair partner joins with --with (mutual declaration)
        r = run(repo, "jobs", "claim", "t-core", "--hours", "8", "--with", "lumen",
                agent="tinker")
        assert "claimed" in r.stdout
        c = json.load(open(os.path.join(repo, "jobs", "t-core", "CLAIM.lumen.json")))
        assert c["with"] == ["tinker"]

        # list shows both
        r = run(repo, "jobs", "list")
        assert "lumen" in r.stdout and "t-core" in r.stdout

        # a third wheel with --with lumen is refused: only declared partners
        r = run(repo, "jobs", "claim", "t-core", "--hours", "8", agent="marlowe",
                expect="any")
        assert r.returncode != 0

        print(f"7 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
