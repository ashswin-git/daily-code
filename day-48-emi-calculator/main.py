#!/usr/bin/env python3
"""EMI Calculator: monthly installment, total interest and amortization."""
import argparse
import sys


def emi(principal, annual_rate, months):
    """Return monthly EMI for a reducing-balance loan."""
    r = annual_rate / 12 / 100
    if r == 0:
        return principal / months
    f = (1 + r) ** months
    return principal * r * f / (f - 1)


def schedule(principal, annual_rate, months):
    r = annual_rate / 12 / 100
    e = emi(principal, annual_rate, months)
    bal = principal
    for m in range(1, months + 1):
        interest = bal * r
        princ = e - interest
        bal = max(bal - princ, 0)
        yield m, interest, princ, bal


def main():
    p = argparse.ArgumentParser(description="EMI Calculator")
    p.add_argument("principal", type=float, help="loan amount")
    p.add_argument("rate", type=float, help="annual interest rate in percent")
    p.add_argument("tenure", type=float, help="loan tenure")
    p.add_argument("--years", action="store_true", help="tenure is in years (default: months)")
    p.add_argument("--table", action="store_true", help="print amortization table")
    a = p.parse_args()
    months = int(round(a.tenure * 12 if a.years else a.tenure))
    if a.principal <= 0 or a.rate < 0 or months <= 0:
        sys.exit("Error: principal and tenure must be positive, rate non-negative.")
    e = emi(a.principal, a.rate, months)
    total = e * months
    print(f"Monthly EMI    : {e:,.2f}")
    print(f"Total interest : {total - a.principal:,.2f}")
    print(f"Total payment  : {total:,.2f}")
    if a.table:
        print(f"\n{'Month':>5} {'Interest':>12} {'Principal':>12} {'Balance':>14}")
        for m, i, pr, b in schedule(a.principal, a.rate, months):
            print(f"{m:>5} {i:>12,.2f} {pr:>12,.2f} {b:>14,.2f}")


if __name__ == "__main__":
    main()
