#!/usr/bin/env python3
"""Crawl the exploit sites into a local mirror for embedding in firmware.

Only the assets the chains actually load are pulled: the HTML entry point plus
the scripts and stylesheets it pulls in. The multi-hundred-megabyte bulk in the
original host mirror is firmware images and patch payloads, which are not needed
to *run* a chain - the .elf payloads are fetched by the console's own loader
after the jailbreak succeeds, not by the host.

Everything lands under sites/<host>/<path> preserving the URL path exactly, so
the firmware's prefix-stripping resolver sees the same layout the console
browses under (e.g. /P2JB/p2jb.html, /luasauce/main.js).
"""

import os
import sys
import re
import urllib.parse
import urllib.request
import collections
import hashlib

MIRROR_HOST = "soniciso1.github.io"
BASE = f"https://{MIRROR_HOST}"

# Seed paths. Each is a site root; the crawl stays inside it.
SEEDS = [
    "/poopicker/",
    "/P2JB/",
    "/P2JB-dev/",
    "/poopsploit/",
    "/poopsploit-dev/",
    "/relapse/",
    "/relapse-dev/",
    "/luasauce/",
    "/luasaucedev/",
]

# Extensions worth mirroring. Anything else (images the pages do not reference,
# stray directories) is skipped to keep the flash image small.
EXT_OK = {
    ".html", ".htm", ".php", ".js", ".mjs", ".css", ".json", ".xml", ".txt",
    ".wasm", ".appcache", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot",
}

# Binary payloads are deliberately NOT fetched: they are only used after a
# successful jailbreak, and they are large.
SKIP_EXT = {".elf", ".bin", ".prx", ".sprx", ".self", ".zip", ".pkg", ".iso"}

# Images on these pages are decoration (a 2 MB cat gif, mostly). None of them
# participate in a chain, so anything over this is dropped to keep the built
# image inside the Pico 2 W's 4 MB.
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"}
IMG_MAX = 64 * 1024

REF_RE = re.compile(
    r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)

UA = "Mozilla/5.0 (PS5; poopicker-mirror)"


def fetch(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get_content_type()


def textish(ct, url):
    if ct and any(k in ct for k in ("html", "javascript", "json", "css", "text")):
        return True
    path = urllib.parse.urlparse(url).path.lower()
    return os.path.splitext(path)[1] in {".html", ".htm", ".php", ".js", ".mjs", ".css"}


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "sites"
    os.makedirs(root, exist_ok=True)

    queue = collections.deque()
    for s in SEEDS:
        p = s if s.endswith("/") else s + "/"
        queue.append((BASE + p, p + "index.html"))

    seen = set()
    saved = {}
    total = 0

    while queue:
        url, path = queue.popleft()
        if url in seen:
            continue
        seen.add(url)

        ext = os.path.splitext(path.lower())[1]
        if ext in SKIP_EXT:
            continue

        try:
            body, ct = fetch(url)
        except Exception as e:
            print(f"  FAIL {path}: {e}", file=sys.stderr)
            continue

        if ext in IMG_EXT and len(body) > IMG_MAX:
            print(f"  {len(body):>9,}  {path}  (skipped: decorative image)")
            continue

        out = os.path.join(root, path.lstrip("/"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(body)
        total += len(body)
        saved[path] = len(body)
        print(f"  {len(body):>9,}  {path}")

        if not textish(ct, url):
            continue

        try:
            txt = body.decode("utf-8", "replace")
        except Exception:
            continue

        for ref in REF_RE.findall(txt):
            ref = ref.strip()
            if not ref or ref.startswith(("data:", "#", "mailto:", "javascript:")):
                continue
            if ref.startswith("//"):
                ref = "https:" + ref
            nxt = urllib.parse.urljoin(url, ref)
            pu = urllib.parse.urlparse(nxt)
            if pu.scheme not in ("http", "https"):
                continue
            # Stay on the mirror host, and stay inside the seed's subtree so a
            # cross-site link cannot drag the whole Pages site in.
            if pu.netloc != MIRROR_HOST:
                continue
            npath = pu.path
            if os.path.splitext(npath.lower())[1] not in EXT_OK:
                continue
            if npath not in SEEDS and not any(
                    npath.startswith(s) for s in SEEDS):
                continue
            if npath.endswith("/"):
                npath += "index.html"
            queue.append((BASE + npath, npath))

    print(f"\n{len(saved)} files, {total:,} bytes raw")
    h = hashlib.sha256()
    for p in sorted(saved):
        h.update(p.encode())
    print(f"tree sha256: {h.hexdigest()[:16]}")


if __name__ == "__main__":
    main()
