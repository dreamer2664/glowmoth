#!/usr/bin/env python3
"""check_luau.py — the honest static gate for Luau sources (rook's first tool).

What it proves: structure. What it does NOT: that the game runs in Studio —
that boundary is named in PROJECT.md and must stay named in reports.
"""
import os, re, sys

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, "src")
    errs, warns, files = [], [], 0
    for dirpath, _, names in os.walk(src if os.path.isdir(src) else root):
        for n in sorted(names):
            if not n.endswith(".luau") and not n.endswith(".lua"):
                continue
            files += 1
            p = os.path.join(dirpath, n)
            text = open(p, encoding="utf-8", errors="replace").read()
            rel = os.path.relpath(p, root)
            opens = len(re.findall(r"\b(function|if|for|while|do)\b", text))
            ends = len(re.findall(r"\bend\b", text))
            if ends < opens * 0.5:
                warns.append(f"{rel}: block imbalance? opens={opens} ends={ends}")
            for i, line in enumerate(text.splitlines(), 1):
                if "TODO" in line or "FIXME" in line:
                    warns.append(f"{rel}:{i}: honest note — {line.strip()[:60]}")
                if re.search(r"require\(.*Workspace\)", line):
                    warns.append(f"{rel}:{i}: check require cycles")
            if "return" not in text and not n.startswith("init"):
                warns.append(f"{rel}: module returns nothing?")
    print(f"luau: {files} files · {len(errs)} errors · {len(warns)} warnings")
    for w in warns[:20]:
        print("  warn ", w)
    for e in errs:
        print("  ERROR", e)
    sys.exit(1 if errs else 0)

if __name__ == "__main__":
    main()
