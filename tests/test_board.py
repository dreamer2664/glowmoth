#!/usr/bin/env python3
"""test_board.py — identity, claims, leases, sweep."""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "..", "bin", "agency")

def fresh_repo():
    d = tempfile.mkdtemp(prefix="agency-test-")
    os.makedirs(os.path.join(d, "agents"), exist_ok=True)
    os.makedirs(os.path.join(d, "board", "tasks"), exist_ok=True)
    os.makedirs(os.path.join(d, "board", "heartbeats"), exist_ok=True)
    os.makedirs(os.path.join(d, "board", "votes"), exist_ok=True)
    os.makedirs(os.path.join(d, "jobs"), exist_ok=True)
    return d

def run(repo, *args, expect=0, env=None):
    e = {**os.environ, "AGENCY_DIR": repo, "AGENCY_NO_PUSH": "1",
         "AGENCY_AGENT": env.pop("AGENT", "nova") if env else "nova"}
    if env:
        e.update(env)
    r = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True, env=e)
    if expect == "any":
        return r
    assert r.returncode == expect, f"{args} -> rc={r.returncode}\n{r.stdout}\n{r.stderr}"
    return r

def main():
    t0 = time.time()
    repo = fresh_repo()
    try:
        # register two agents
        run(repo, "init", "--name", "nova", "--caps", "python")
        run(repo, "init", "--name", "rex", "--caps", "blender")
        assert os.path.exists(os.path.join(repo, "agents", "nova.json"))
        r = run(repo, "whoami", env={"AGENT": "nova"})
        assert "nova" in r.stdout

        # create + claim a task
        r = run(repo, "tasks", "new", "--title", "demo card", "--id", "t-demo")
        r = run(repo, "tasks", "claim", "t-demo", "--hours", "4", env={"AGENT": "nova"})
        assert "claimed t-demo" in r.stdout
        t = json.load(open(os.path.join(repo, "board", "tasks", "t-demo.json")))
        assert t["status"] == "claimed" and t["owner"] == "nova" and t["lease"]

        # second agent cannot take it
        r = run(repo, "tasks", "claim", "t-demo", env={"AGENT": "rex"}, expect="any")
        assert r.returncode != 0, "double-claim must fail"

        # heartbeat renews lease + writes append-only heartbeat
        run(repo, "tasks", "heartbeat", "t-demo", "--note", "done X @abc; next Y",
            env={"AGENT": "nova"})
        hb = open(os.path.join(repo, "board", "heartbeats", "nova.jsonl")).read()
        assert "done X @abc" in hb

        # sweep with clock far in the future: lease expires
        r = run(repo, "sweep", expect="any",
                env={"AGENT": "rex"})
        # force expiry by rewriting the lease, then sweep --apply
        p = os.path.join(repo, "board", "tasks", "t-demo.json")
        d = json.load(open(p))
        d["lease"]["expires"] = "2020-01-01T00:00:00Z"
        json.dump(d, open(p, "w"))
        r = run(repo, "sweep", "--apply", expect="any", env={"AGENT": "rex"})
        assert "SWEPT t-demo" in r.stdout
        t = json.load(open(p))
        assert t["status"] == "open" and t["owner"] is None

        # release flow
        run(repo, "tasks", "claim", "t-demo", env={"AGENT": "rex"})
        run(repo, "tasks", "release", "t-demo", env={"AGENT": "rex"})
        t = json.load(open(p))
        assert t["status"] == "open"

        print(f"6 assertions ok ({time.time()-t0:.1f}s)", file=sys.stderr)
    finally:
        shutil.rmtree(repo, ignore_errors=True)

if __name__ == "__main__":
    main()
