#!/usr/bin/env python3
"""run_all.py — run every tests/test_*.py; exit 1 if any fails."""
import glob, os, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
fails = 0
for f in sorted(glob.glob(os.path.join(here, "test_*.py"))):
    r = subprocess.run([sys.executable, f], capture_output=True, text=True)
    name = os.path.basename(f)
    if r.returncode == 0:
        print(f"PASS  {name}  ({r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''})")
    else:
        fails += 1
        print(f"FAIL  {name}")
        print((r.stdout + r.stderr)[-2000:])
print(f"\n{len(glob.glob(os.path.join(here, 'test_*.py'))) - fails} passed · {fails} failed")
sys.exit(1 if fails else 0)
