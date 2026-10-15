#!/usr/bin/env python3
"""Day 17 - UUID Generator.

Generate UUIDs (v1, v3, v4, v5, v7) in several formats, and inspect any UUID
to see its version, variant, and embedded timestamp. Standard library only.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import uuid
from datetime import datetime, timezone

NAMESPACES = {
    "dns": uuid.NAMESPACE_DNS,
    "url": uuid.NAMESPACE_URL,
    "oid": uuid.NAMESPACE_OID,
    "x500": uuid.NAMESPACE_X500,
}

# Offset between the UUID epoch (1582-10-15) and the Unix epoch, in 100 ns ticks.
GREGORIAN_OFFSET = 0x01B21DD213814000


def uuid7() -> uuid.UUID:
    """Time-ordered UUID v7 (RFC 9562): 48-bit Unix ms timestamp + random bits."""
    ms = time.time_ns() // 1_000_000
    rand = int.from_bytes(os.urandom(10), "big")
    value = (ms & ((1 << 48) - 1)) << 80
    value |= 0x7 << 76                       # version 7
    value |= ((rand >> 68) & 0xFFF) << 64    # rand_a (12 bits)
    value |= 0b10 << 62                      # RFC 4122 variant
    value |= rand & ((1 << 62) - 1)
    return uuid.UUID(int=value)


def resolve_namespace(name: str) -> uuid.UUID:
    if name.lower() in NAMESPACES:
        return NAMESPACES[name.lower()]
    try:
        return uuid.UUID(name)
    except ValueError:
        sys.exit(f"error: namespace must be dns/url/oid/x500 or a UUID, got {name!r}")


def make_uuid(version: int, namespace: str | None, name: str | None) -> uuid.UUID:
    if version in (3, 5):
        if not name:
            sys.exit(f"error: v{version} needs --name (and optionally --namespace)")
        ns = resolve_namespace(namespace or "dns")
        return uuid.uuid3(ns, name) if version == 3 else uuid.uuid5(ns, name)
    if version == 1:
        return uuid.uuid1()
    if version == 7:
        return uuid7()
    return uuid.uuid4()


def fmt(u: uuid.UUID, style: str, upper: bool) -> str:
    text = {
        "standard": str(u),
        "hex": u.hex,
        "braces": "{" + str(u) + "}",
        "urn": u.urn,
        "int": str(u.int),
    }[style]
    return text.upper() if upper and style != "int" else text


def describe_variant(u: uuid.UUID) -> str:
    return {
        uuid.RESERVED_NCS: "NCS (reserved)",
        uuid.RFC_4122: "RFC 4122 / 9562",
        uuid.RESERVED_MICROSOFT: "Microsoft (reserved)",
        uuid.RESERVED_FUTURE: "future (reserved)",
    }.get(u.variant, str(u.variant))


def timestamp_of(u: uuid.UUID) -> datetime | None:
    if u.variant != uuid.RFC_4122:
        return None
    if u.version == 1:
        seconds = (u.time - GREGORIAN_OFFSET) / 10_000_000
    elif u.version == 7:
        seconds = (u.int >> 80) / 1000
    else:
        return None
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def inspect(text: str) -> int:
    try:
        u = uuid.UUID(text.strip())
    except ValueError:
        print(f"invalid: {text.strip()!r} is not a UUID")
        return 1
    print(f"uuid:     {u}")
    print("valid:    yes")
    print(f"version:  {u.version if u.variant == uuid.RFC_4122 else 'n/a'}")
    print(f"variant:  {describe_variant(u)}")
    print(f"hex:      {u.hex}")
    print(f"int:      {u.int}")
    ts = timestamp_of(u)
    if ts:
        print(f"created:  {ts.isoformat(timespec='milliseconds')}")
    if u == uuid.UUID(int=0):
        print("note:     this is the nil UUID")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate and inspect UUIDs.")
    sub = p.add_subparsers(dest="cmd")

    g = sub.add_parser("gen", aliases=["g"], help="generate UUIDs (default)")
    g.add_argument("-v", "--version", type=int, choices=[1, 3, 4, 5, 7], default=4)
    g.add_argument("-n", "--count", type=int, default=1, help="how many to make")
    g.add_argument("-f", "--format", dest="style", default="standard",
                   choices=["standard", "hex", "braces", "urn", "int"])
    g.add_argument("-u", "--upper", action="store_true", help="uppercase output")
    g.add_argument("--namespace", help="v3/v5 namespace: dns, url, oid, x500 or a UUID")
    g.add_argument("--name", help="v3/v5 name to hash, e.g. example.com")

    i = sub.add_parser("inspect", aliases=["i"], help="validate and explain UUIDs")
    i.add_argument("uuids", nargs="*", help="UUIDs to inspect (or pipe via stdin)")
    return p


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0].startswith("-") and argv[0] not in ("-h", "--help"):
        argv = ["gen", *argv]
    args = build_parser().parse_args(argv)

    if args.cmd in ("inspect", "i"):
        items = args.uuids or [line for line in sys.stdin.read().split() if line]
        if not items:
            print("error: give at least one UUID", file=sys.stderr)
            return 2
        status = 0
        for n, item in enumerate(items):
            if n:
                print()
            status |= inspect(item)
        return status

    if args.count < 1:
        sys.exit("error: --count must be at least 1")
    if args.version in (3, 5) and args.count > 1:
        print("note: v3/v5 are deterministic, so every copy is identical", file=sys.stderr)
    for _ in range(args.count):
        print(fmt(make_uuid(args.version, args.namespace, args.name), args.style, args.upper))
    return 0


if __name__ == "__main__":
    sys.exit(main())
