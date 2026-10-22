#!/usr/bin/env python3
"""Day 24 - Port Checker.

Check whether TCP ports are open on a host. Supports single ports, lists,
ranges, a "common" preset, concurrent scanning, and JSON output.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor

COMMON = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns", 80: "http",
    110: "pop3", 143: "imap", 443: "https", 465: "smtps", 587: "submission",
    993: "imaps", 995: "pop3s", 1433: "mssql", 3000: "dev-server",
    3306: "mysql", 3389: "rdp", 5000: "flask", 5432: "postgres",
    5900: "vnc", 6379: "redis", 8000: "http-alt", 8080: "http-proxy",
    8443: "https-alt", 9000: "php-fpm", 27017: "mongodb",
}


def service_name(port: int) -> str:
    if port in COMMON:
        return COMMON[port]
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "-"


def parse_ports(spec: str) -> list[int]:
    """Parse '22,80,8000-8005' or 'common' into a sorted unique port list."""
    if spec.strip().lower() == "common":
        return sorted(COMMON)
    ports: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = (int(x) for x in part.split("-", 1))
            if a > b:
                a, b = b, a
            ports.update(range(a, b + 1))
        else:
            ports.add(int(part))
    bad = [p for p in ports if not 1 <= p <= 65535]
    if bad:
        raise ValueError(f"port out of range 1-65535: {bad[0]}")
    if not ports:
        raise ValueError("no ports given")
    return sorted(ports)


def check_port(host: str, port: int, timeout: float) -> dict:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            state = "open"
    except socket.timeout:
        state = "filtered"
    except ConnectionRefusedError:
        state = "closed"
    except OSError as exc:
        state = "error" if exc.errno not in (111, 10061) else "closed"
    ms = round((time.perf_counter() - start) * 1000, 1)
    return {"port": port, "service": service_name(port), "state": state, "ms": ms}


def scan(host: str, ports: list[int], timeout: float, workers: int) -> list[dict]:
    with ThreadPoolExecutor(max_workers=max(1, min(workers, len(ports)))) as pool:
        results = list(pool.map(lambda p: check_port(host, p, timeout), ports))
    return sorted(results, key=lambda r: r["port"])


ICON = {"open": "OPEN    ", "closed": "closed  ", "filtered": "filtered", "error": "error   "}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check which TCP ports are open on a host.")
    ap.add_argument("host", nargs="?", help="hostname or IP (prompted if missing)")
    ap.add_argument("-p", "--ports", default="common",
                    help="ports: '80', '22,80,443', '8000-8010' or 'common' (default)")
    ap.add_argument("-t", "--timeout", type=float, default=1.0, help="seconds per port (default 1)")
    ap.add_argument("-w", "--workers", type=int, default=100, help="parallel checks (default 100)")
    ap.add_argument("--open", action="store_true", help="only show open ports")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = ap.parse_args(argv)

    host = args.host or input("Host: ").strip()
    if not host:
        print("No host given.", file=sys.stderr)
        return 2
    try:
        ports = parse_ports(args.ports)
        ip = socket.gethostbyname(host)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except socket.gaierror:
        print(f"Error: cannot resolve host '{host}'", file=sys.stderr)
        return 2

    t0 = time.perf_counter()
    results = scan(ip, ports, args.timeout, args.workers)
    elapsed = round(time.perf_counter() - t0, 2)
    open_ports = [r for r in results if r["state"] == "open"]
    shown = open_ports if args.open else results

    if args.json:
        print(json.dumps({"host": host, "ip": ip, "scanned": len(ports),
                          "open": len(open_ports), "seconds": elapsed,
                          "results": shown}, indent=2))
    else:
        print(f"Host {host} ({ip}) - {len(ports)} port(s) in {elapsed}s\n")
        print(f"{'PORT':>6}  {'STATE':<8}  {'TIME':>8}  SERVICE")
        for r in shown:
            print(f"{r['port']:>6}  {ICON[r['state']]}  {r['ms']:>6}ms  {r['service']}")
        print(f"\n{len(open_ports)} open / {len(ports)} scanned")
    return 0 if open_ports else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
