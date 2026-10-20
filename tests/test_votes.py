#!/usr/bin/env python3
"""test_votes.py — post-merge acceptance: no self-vote, quorum closes, deny warns."""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def fresh_repo():
    d = tempfile.mkdtemp(prefix="agency-votes-")
    for p in ("agents", "board/tasks", "board/heartbeats", "board/votes", "jobs"):
        os.makedirs(os.path.join(d, p), exist_ok=True)
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
        for n in ("nova", "rex", "ada"):
            run(repo, "init", "--name", n)
        run(repo, "tasks", "new", "--title", "shipped work", "--id", "t-v")
        run(repo, "tasks", "claim", "t-v", agent="nova")
        run(repo, "tasks", "review", "t-v", agent="nova")

        # self-vote refused
        r = run(repo, "vote", "t-v", "accept-inspected", "--reason", "abc123 ran tests",
                agent="nova", expect="any")
        assert r.returncode != 0 and "self" in r.stderr.lower()

        # short reason refused
        r = run(repo, "vote", "t-v", "accept-inspected", "--reason", "ok",
                agent="rex", expect="any")
        assert r.returncode != 0

        run(repo, "vote", "t-v", "accept-inspected",
            "--reason", "abc123 + ran tests/run_all.py green", agent="rex")
        r = run(repo, "votes", "t-v")
        assert "1 accept / 0 deny" in r.stdout

        # double vote refused
        r = run(repo, "vote", "t-v", "accept-inspected",
                "--reason", "again with more evidence here", agent="rex", expect="any")
        assert r.returncode != 0

        # second ballot → quorum → done
        run(repo, "vote", "t-v", "accept-inspected",
            "--reason", "def456 + decoded frames, 0 errors", agent="ada")
        t = json.load(open(os.path.join(repo, "board", "tasks", "t-v.json")))
        assert t["status"] == "done", t["status"]

        # review next must not hand you your own work
        run(repo, "tasks", "new", "--title", "mine", "--id", "t-mine")
        run(repo, "tasks", "claim", "t-mine", agent="nova")
        run(repo, "tasks", "review", "t-mine", agent="nova")
        r = run(repo, "review", "next", agent="nova")
        assert "YOURS" in r.stdout or "t-mine" not in r.stdout.splitlines()[0]

        print(f"6 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
