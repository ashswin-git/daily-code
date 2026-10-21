#!/usr/bin/env python3
"""Day 23 - IP Address Checker.

Validate IPv4/IPv6 addresses and CIDR networks offline: version, type
(private, public, loopback, reserved...), reverse DNS name, binary/integer
forms, and network details. Optional --me / --geo use the free ipapi.co
endpoint (no API key) to show your public IP and rough location.

Standard library only.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
import urllib.request

GEO_URL = "https://ipapi.co/{ip}json/"


DOC_NETS = [ipaddress.ip_network(n) for n in
            ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32")]


def classify(ip: ipaddress._BaseAddress) -> str:
    """Return the most specific human label for an address."""
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped:
        ip = mapped
    if any(ip.version == n.version and ip in n for n in DOC_NETS):
        return "documentation (example-only)"
    if ip.version == 4 and ip in ipaddress.ip_network("100.64.0.0/10"):
        return "carrier-grade NAT"
    checks = [
        ("is_unspecified", "unspecified"),
        ("is_loopback", "loopback"),
        ("is_link_local", "link-local"),
        ("is_multicast", "multicast"),
        ("is_private", "private"),
        ("is_reserved", "reserved"),
        ("is_global", "public"),
    ]
    for attr, label in checks:
        if getattr(ip, attr, False):
            return label
    return "special-use"


def ip_details(ip: ipaddress._BaseAddress, rdns: bool) -> dict:
    info = {
        "input": str(ip),
        "valid": True,
        "kind": "address",
        "version": ip.version,
        "type": classify(ip),
        "compressed": ip.compressed,
        "exploded": ip.exploded,
        "integer": int(ip),
        "reverse_pointer": ip.reverse_pointer,
    }
    if ip.version == 4:
        info["binary"] = ".".join(f"{int(o):08b}" for o in str(ip).split("."))
        first = int(str(ip).split(".")[0])
        info["class"] = ("A" if first < 128 else "B" if first < 192 else
                         "C" if first < 224 else "D (multicast)" if first < 240 else "E (reserved)")
    else:
        mapped = ip.ipv4_mapped
        if mapped:
            info["ipv4_mapped"] = str(mapped)
    if rdns:
        try:
            socket.setdefaulttimeout(2)
            info["hostname"] = socket.gethostbyaddr(str(ip))[0]
        except (OSError, socket.herror):
            info["hostname"] = "(no PTR record)"
    return info


def net_details(net: ipaddress._BaseNetwork) -> dict:
    hosts = net.num_addresses
    if net.version == 4 and net.prefixlen < 31:
        hosts -= 2
    info = {
        "input": str(net),
        "valid": True,
        "kind": "network",
        "version": net.version,
        "type": classify(net.network_address),
        "network": str(net.network_address),
        "prefix": net.prefixlen,
        "netmask": str(net.netmask),
        "addresses": net.num_addresses,
        "usable_hosts": hosts,
    }
    if net.version == 4:
        info["broadcast"] = str(net.broadcast_address)
        info["wildcard"] = str(net.hostmask)
    if net.num_addresses >= 2:
        first = net.network_address + (1 if net.version == 4 and net.prefixlen < 31 else 0)
        last = net.broadcast_address - (1 if net.version == 4 and net.prefixlen < 31 else 0)
        info["host_range"] = f"{first} - {last}"
    return info


def check(text: str, rdns: bool) -> dict:
    raw = text.strip()
    try:
        if "/" in raw:
            return net_details(ipaddress.ip_network(raw, strict=False))
        return ip_details(ipaddress.ip_address(raw), rdns)
    except ValueError as exc:
        return {"input": raw, "valid": False, "error": str(exc)}


def fetch_geo(ip: str = "") -> dict:
    url = GEO_URL.format(ip=f"{ip}/" if ip else "")
    req = urllib.request.Request(url, headers={"User-Agent": "day-23-ip-checker"})
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.load(resp)
    except Exception as exc:  # network errors, rate limits, bad JSON
        return {"error": f"lookup failed: {exc}"}
    if data.get("error"):
        return {"error": data.get("reason", "lookup failed")}
    keep = ("ip", "city", "region", "country_name", "org", "asn", "timezone")
    return {k: data.get(k) for k in keep if data.get(k)}


def print_text(info: dict) -> None:
    if not info["valid"]:
        print(f"[INVALID] {info['input']}\n          x {info['error']}")
        return
    print(f"[VALID  ] {info['input']}  (IPv{info['version']} {info['kind']}, {info['type']})")
    for key, val in info.items():
        if key in ("input", "valid", "kind", "version", "type") or val is None:
            continue
        if key == "geo":
            for gk, gv in val.items():
                print(f"          {('geo ' + gk):<16} {gv}")
            continue
        print(f"          {key:<16} {val}")


def main() -> int:
    p = argparse.ArgumentParser(description="Check and explain IPv4/IPv6 addresses and CIDR networks.")
    p.add_argument("items", nargs="*", help="IP addresses or CIDR ranges, e.g. 8.8.8.8 192.168.1.0/24")
    p.add_argument("-f", "--file", help="read one IP/CIDR per line from a file")
    p.add_argument("--rdns", action="store_true", help="look up reverse DNS hostname")
    p.add_argument("--geo", action="store_true", help="add location/ISP for public IPs (free ipapi.co)")
    p.add_argument("--me", action="store_true", help="show your own public IP and location")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = p.parse_args()

    if args.me:
        geo = fetch_geo()
        print(json.dumps(geo, indent=2) if args.json else
              "\n".join(f"{k:<14} {v}" for k, v in geo.items()))
        return 1 if "error" in geo else 0

    items = list(args.items)
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            items += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    if not items and not sys.stdin.isatty():
        items = [ln.strip() for ln in sys.stdin if ln.strip()]
    if not items:
        try:
            items = [input("Enter an IP or CIDR: ")]
        except (EOFError, KeyboardInterrupt):
            return 1

    results = []
    for item in items:
        info = check(item, args.rdns)
        if args.geo and info.get("valid") and info["kind"] == "address" and info["type"] == "public":
            info["geo"] = fetch_geo(info["input"])
        results.append(info)

    if args.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        for info in results:
            print_text(info)
        ok = sum(r["valid"] for r in results)
        print(f"\n{ok}/{len(results)} valid")
    return 0 if all(r["valid"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
