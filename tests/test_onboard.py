#!/usr/bin/env python3
"""test_onboard.py — the entry battery is one command and produces receipts."""
import os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def main():
    t0 = time.time()
    repo = tempfile.mkdtemp(prefix="agency-ob-")
    for p in ("agents", "board/tasks", "board/heartbeats", "board/votes", "jobs", "tests"):
        os.makedirs(os.path.join(repo, p), exist_ok=True)
    # a trivial test file so a full T4 could run; we use --quick in one path
    open(os.path.join(repo, "tests", "run_all.py"), "w").write("print('ok')\n")
    try:
        e = {**os.environ, "AGENCY_DIR": repo, "AGENCY_NO_PUSH": "1", "AGENCY_AGENT": "fledge"}
        def run(*args, expect=0):
            r = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, env=e)
            if expect != "any":
                assert r.returncode == expect, f"{args} -> {r.returncode}\n{r.stdout}\n{r.stderr}"
            return r

        run("init", "--name", "fledge", "--caps", "python")
        r = run("onboard", "--quick")
        assert "T1 ✅" in r.stdout and "T5 ✅" in r.stdout
        assert "fledge — entry tests passed" in r.stdout
        assert "Epoch 2026-10-20.3" in r.stdout
        assert os.path.exists(os.path.join(repo, "evidence", "T1-T5.txt"))
        report = open(os.path.join(repo, "evidence", "T1-T5.txt")).read()
        assert "T1 PASS" in report and "T5 PASS" in report

        # full battery (runs the suite we placed)
        r = run("onboard")
        assert "T4 ✅" in r.stdout

        # stub generator
        r = run("stub", "--name", "fledge", "--job", "jobs/t-x")
        assert "COMMISSION STUB" in r.stdout and "onboard" in r.stdout

        # epoch drift detection
        p = os.path.join(repo, "agents", "fledge.json")
        s = open(p).read().replace("2026-10-20.3", "2026-10-01.9")
        open(p, "w").write(s)
        r = run("epoch", expect="any")
        assert "STALE" in r.stdout and "fledge" in r.stdout

        print(f"7 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
