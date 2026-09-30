#!/usr/bin/env python3
"""Replay real console request shapes against the firmware's resolver logic.

Mirrors resolve() / resolve_by_bare_name() in PS5_Server_Pico.ino. Run from
this directory:  python3 tools/test_resolve.py

This is a check on the *path logic only*. It does not exercise HTTP, TLS, DNS
or the radio, so it cannot tell you the firmware works on a board - see the
caveat in POOPICKER.md.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# ../../ is this repo's root; the sketch is a sibling of embedded/.
HEADER = os.path.join(HERE, "..", "..", "PS5-Server-Pico",
                      "PS5_Server_Pico", "payloads.h")

# Must match RELAPSE_SITE / the order[] array in PS5_Server_Pico.ino.
RELAPSE_SITE = "relapse"
ORDER = [
    RELAPSE_SITE, RELAPSE_SITE, "p2jb", "poopsploit", "luasauce",
    RELAPSE_SITE + "-dev", "relapse-dev", "p2jb-dev", "poopsploit-dev",
    "luasaucedev",
]


def load_keys():
    if not os.path.exists(HEADER):
        sys.exit(f"payloads.h not found at {HEADER}\n"
                 f"run tools/mkpages.py to generate it")
    with open(HEADER) as f:
        return set(re.findall(r'\{ "([^"]+)",', f.read()))


def resolve(path, keys):
    clean = path.split("?")[0].split("#")[0].lower()
    parts = [s for s in clean.split("/") if s and s not in (".", "..")][:10]
    if not parts:
        return "poopicker/index.html" if "poopicker/index.html" in keys else None

    for i in range(len(parts)):
        cand = "/".join(parts[i:])
        if cand in keys:
            return cand
        if cand + "/index.html" in keys:
            return cand + "/index.html"

    leaf = parts[-1]
    if leaf and "/" not in leaf:
        for root in ORDER:
            if f"{root}/{leaf}" in keys:
                return f"{root}/{leaf}"
    return None


def pageish(path):
    """A missing .js or .css must 404, never the index - it would be served as
    script and fail with a confusing parse error."""
    return True if "." not in path else path.endswith((".html", ".htm"))


CASES = [
    # the index, and the root the User's Guide redirect lands on
    ("/poopicker/index.html", "poopicker/index.html"),
    ("/", "poopicker/index.html"),
    # relapse, reached by following an index link
    ("/relapse/", "relapse/index.html"),
    ("/relapse/index.html", "relapse/index.html"),
    ("/relapse/main.js?v=6", "relapse/main.js"),
    ("/relapse/rop.js", "relapse/rop.js"),
    ("/relapse/syscalls.js", "relapse/syscalls.js"),
    ("/relapse/firmware.js?v=4", "relapse/firmware.js"),
    ("/relapse/payloads.js?v=1", "relapse/payloads.js"),
    # the guide prefix: same assets, unknown mount point
    ("/document/en/ps5/main.js", "relapse/main.js"),
    ("/document/en/ps5/rop.js", "relapse/rop.js"),
    ("/document/en/ps5/syscalls.js", "relapse/syscalls.js"),
    # a real subdirectory must win over prefix stripping
    ("/p2jb/p2jb.html?go=1&auto=1&payload=1", "p2jb/p2jb.html"),
    ("/poopsploit/poopsploit/poops.html?go=1&payload=1",
     "poopsploit/poopsploit/poops.html"),
    ("/poopsploit/poopsploit/rop.js", "poopsploit/poopsploit/rop.js"),
    ("/luasauce/psfree/psfree.js", "luasauce/psfree/psfree.js"),
    # devkit roots still resolve when asked for directly
    ("/relapse-dev/main.js", "relapse-dev/main.js"),
    # traversal is stripped, not resolved
    ("/../../etc/passwd", None),
]


def main():
    keys = load_keys()
    print(f"{len(keys)} mirrored files\n")

    failed = 0
    for path, want in CASES:
        got = resolve(path, keys)
        if got is None and want is None:
            ok, got = True, "None"
        else:
            ok = got == want
        failed += not ok
        mark = "ok  " if ok else "FAIL"
        print(f"  {mark} {path:<48} -> {got}")

    # page-shaped misses fall back to the index; script-shaped misses 404
    print()
    for path, want in [("/relapse/nope.html", "poopicker/index.html"),
                       ("/relapse/nope.js", None)]:
        got = resolve(path, keys) or ("poopicker/index.html" if pageish(path)
                                      else None)
        ok = got == want
        failed += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {path:<48} -> {got}")

    total = len(CASES) + 2
    print(f"\n{total - failed}/{total} pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
