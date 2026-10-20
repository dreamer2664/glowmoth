#!/usr/bin/env python3
"""test_ship_e2e.py — ship.sh end-to-end: gate → squash → push → readback;
   and fail-closed when the job gate is red."""
import os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(HERE, "..")
SHIP = os.path.join(REPO_ROOT, "tools", "ship.sh")

def sh(cmd, cwd, env, expect=0):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env=env)
    if expect != "any":
        assert r.returncode == expect, f"{cmd} -> {r.returncode}\n{r.stdout}\n{r.stderr}"
    return r

def main():
    t0 = time.time()
    base = tempfile.mkdtemp(prefix="agency-ship-")
    origin, work = os.path.join(base, "origin"), os.path.join(base, "work")
    try:
        sh(f"git init --bare -q {origin}", base, os.environ)
        os.makedirs(work)
        env = {**os.environ, "AGENCY_AGENT": "nova",
               "GIT_AUTHOR_NAME": "nova", "GIT_AUTHOR_EMAIL": "nova@a",
               "GIT_COMMITTER_NAME": "nova", "GIT_COMMITTER_EMAIL": "nova@a"}
        sh("git init -q -b main .", work, env)
        sh(f"git remote add origin {origin}", work, env)
        # never inherit a polluted AGENCY_DIR — the CLI must gate THIS scratch repo
        env["AGENCY_DIR"] = work

        # the machine inside the scratch repo (ship.sh calls it)
        os.makedirs(os.path.join(work, "bin"))
        shutil.copy(os.path.join(REPO_ROOT, "bin", "agency"), os.path.join(work, "bin", "agency"))
        os.makedirs(os.path.join(work, "tests"))
        open(os.path.join(work, "tests", "test_ok.py"), "w").write("assert 1 + 1 == 2\n")
        open(os.path.join(work, "SHIP_GATE.md"), "w").write("$ python3 tests/test_ok.py\n")

        # job with a quick floor + required evidence
        jd = os.path.join(work, "jobs", "t-e2e")
        os.makedirs(os.path.join(jd, "evidence"))
        open(os.path.join(jd, "BRIEF.md"), "w").write("# e2e\n")
        open(os.path.join(jd, "PHASES.md"), "w").write(
            "| phase | deliverable | required evidence | min_hours |\n|---|---|---|---|\n"
            "| P1 | thing | `evidence/p1.txt` | 0.0 |\n")
        open(os.path.join(jd, "evidence", "p1.txt"), "w").write("receipt\n")
        open(os.path.join(jd, "HANDOFF.md"), "w").write(
            "2026-10-20T10:00:00Z · nova · phase P1 start · working\n"
            "2026-10-20T10:30:00Z · nova · phase P1 close · 0.5h · done thing\n")
        open(os.path.join(jd, "PHASELOG.jsonl"), "w").write(
            '{"ts":"2026-10-20T10:00:00Z","by":"nova","phase":"P1","action":"start","note":""}\n'
            '{"ts":"2026-10-20T10:30:00Z","by":"nova","phase":"P1","action":"close","note":"done","elapsed_h":0.5}\n')

        os.makedirs(os.path.join(work, "agents"))
        open(os.path.join(work, "agents", "nova.json"), "w").write(
            '{"name":"nova","role":"worker","kind":"ai","joined_ts":"2026-10-10T00:00:00Z",'
            '"last_seen":"2026-10-20T10:00:00Z","epoch":"2026-10-20.3"}')

        sh("git add -A && git commit -qm init && git push -q origin main", work, env)
        sh("git checkout -qb agent/nova/t-e2e && echo work >> f.txt && git add f.txt "
           "&& git commit -qm work", work, env)

        r = sh("bash " + SHIP + " t-e2e", work, env)
        assert "SHIPPED: t-e2e" in r.stdout, r.stdout + r.stderr
        log = sh("git -C " + origin + " log main --oneline -5", base, env).stdout
        assert "ship(nova)" in log, log

        # second scenario: gate red → fail closed
        sh("git checkout -q main && git checkout -qb agent/nova/t-e2e2", work, env)
        os.remove(os.path.join(jd, "evidence", "p1.txt"))
        sh("echo more >> f.txt && git add -A && git commit -qm work2", work, env)
        r = sh("bash " + SHIP + " t-e2e", work, env, expect="any")
        assert r.returncode != 0 and "SHIP REFUSED" in (r.stdout + r.stderr)
        assert "evidence" in (r.stdout + r.stderr)

        print(f"5 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(base, ignore_errors=True)

if __name__ == "__main__":
    main()
