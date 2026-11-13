#!/usr/bin/env python3
"""Currency Converter: live rates from the free open.er-api.com (no API key)."""

import json
import sys
import urllib.request

API = "https://open.er-api.com/v6/latest/{}"


def fetch_rates(base: str) -> dict:
    with urllib.request.urlopen(API.format(base.upper()), timeout=10) as r:
        data = json.load(r)
    if data.get("result") != "success":
        raise ValueError(f"Unknown currency: {base}")
    return data["rates"]


def convert(amount: float, src: str, dst: str) -> float:
    rates = fetch_rates(src)
    dst = dst.upper()
    if dst not in rates:
        raise ValueError(f"Unknown currency: {dst}")
    return amount * rates[dst]


def main() -> None:
    try:
        if len(sys.argv) == 4:
            amount, src, dst = float(sys.argv[1]), sys.argv[2], sys.argv[3]
        else:
            amount = float(input("Amount: "))
            src = input("From (e.g. USD): ")
            dst = input("To (e.g. INR): ")
        result = convert(amount, src, dst)
        print(f"{amount:,.2f} {src.upper()} = {result:,.2f} {dst.upper()}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
