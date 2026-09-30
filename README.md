# poopicker-pico

An offline PS5 exploit host that runs entirely on a **Raspberry Pi Pico 2 W**.

The Pico raises its own WiFi access point and answers **every** DNS query with
its own IP. There is no router, no PC, and no internet at any point in the
chain: the console joins the AP, opens the User's Guide, and lands on the
index.

Built on two things:

* **[soniciso1/poopicker](https://github.com/soniciso1/poopicker)** — the site
  mirror and its exploit chains. Only the assets the chains actually load are
  carried; the multi-hundred-MB bulk in the desktop host is firmware images and
  patch payloads, which are not needed to *run* a chain.
* **[stooged/PS5-Server-Pico](https://github.com/stooged/PS5-Server-Pico)** — the
  Pico-side server (AP mode, wildcard DNS, HTTPS, LittleFS, admin UI), which had
  a 3.xx/4.xx IPv6 chain swapped out for the poopicker mirror.

## Layout

    PS5-Server-Pico/           upstream layout, kept as-is
    └── PS5_Server_Pico/       the firmware sketch (arduino-pico core)
    embedded/                  mirror crawler, payload generator, resolver test

## Which chain

Configured for **relapse, retail** — **FW 12.71 – 13.60** (retail and testkit,
target ID `0x82`). A devkit needs the `-dev` sites.

| firmware | chain | time to jailbreak |
| --- | --- | --- |
| 7.00 – 12.00 | poopsploit | seconds |
| 12.02 – 12.70 | p2jb | ~1 hour (the leak alone runs that long) |
| 12.71 – 13.60 | relapse | fast |

The index carries the full firmware table, so the right chain can be picked from
the page itself. Sending a console the wrong chain fails to jailbreak and does
not harm it.

## Build

Needs [arduino-cli](https://arduino.github.io/arduino-cli/) and the
[arduino-pico](https://github.com/earlephilhower/arduino-pico) core.

    arduino-cli core install rp2040:rp2040
    arduino-cli compile \
      -b rp2040:rp2040:rpipico2w:flash=4194304_131072 \
      --export-binaries PS5-Server-Pico/PS5_Server_Pico

The 4 MB board with a 128 KB LittleFS partition is required — the payload table
alone is ~724 KB of `.rodata`. Current build: **963 KB of 4096 KB flash (24%)**,
75 KB of 524 KB RAM.

To flash: hold **BOOT** while plugging the board in, then drop
`PS5-Server-Pico/PS5_Server_Pico/build/rp2040.rp2040.rpipico2w/PS5_Server_Pico.ino.uf2`
onto the `RPI-RP2` volume.

Then, with the console: join `PS5_WEB_AP` and open the User's Guide. Admin UI at
`http://10.1.1.1/admin.html` (upload, file manager, config, reboot).

## Refreshing the mirror

The embedded copy goes stale the moment an exploit site is updated:

    cd embedded
    python3 tools/fetch_sites.py sites
    python3 tools/mkpages.py sites ../PS5-Server-Pico/PS5_Server_Pico/payloads.h

    # then recompile

`fetch_sites.py` skips images over 64 KB — those are decoration (there is a 2 MB
cat gif) and none of them take part in a chain. `.elf` / `.bin` are skipped
entirely: they are only used after a successful jailbreak, and the board has a
LittleFS uploader for those instead.

`payloads.h` is committed so a fresh clone builds without re-crawling.

## Tests

    python3 embedded/tools/test_resolve.py

Replays real console request shapes against the firmware's resolver logic —
guide prefixes, query strings, subdirectories, path traversal — 20 cases.

Both run in CI on every push and PR.

## Releases

Tag a `v*` and the release workflow builds, publishes the UF2 as a **draft**
release, and attaches [SLSA Level 3](https://slsa.dev) provenance:

    git tag v0.1.0 && git push origin v0.1.0

Provenance is signed with GitHub's OIDC key — no long-lived signing key to leak
or rotate — and lets someone confirm the UF2 in a release came from this repo at
that tag, which matters more than usual when the artifact decides which exploit
runs on a console.

It attests to the *build*, not to the chain working on hardware. Draft releases
are deliberate: review the notes before publishing.

## Caveat

**This has been compiled and its path routing tested, but it has not been
flashed to a board or run against a real PS5.** Nothing here substitutes for
confirming it on hardware. Two things to check first:

* **Timing.** The chains are timing-sensitive and `poopsploit` is a UAF race
  that completes in seconds. Serving from a microcontroller over WiFi adds
  jitter the desktop host never had. If a chain stalls where it used to work,
  suspect jitter before the payload.
* **Flash pressure.** 24% used, but the mirror is the whole cost centre. There is
  room for the ~900 KB `luasauce` variants again; a second large chain is not.

## Credits

* `soniciso1/poopicker` — chains, mirror, index.
* `stooged/PS5-Server-Pico` — Pico server foundation (MIT).
* `earlephilhower/arduino-pico` — the core.
* `zecoxao` — `luasauce` / `luasaucedev`, carried verbatim with original credits.
