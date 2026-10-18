#!/usr/bin/env python3
"""Day 20 - Fake Data Generator.

Generate realistic-looking fake records (people, users, orders...) for testing,
demos and seeding. Standard library only, fully offline.

Examples:
    python3 main.py                          # 5 people as a table
    python3 main.py -n 3 -f name,email,city
    python3 main.py --preset user -n 10 --format json
    python3 main.py --preset order -n 100 --format csv -o orders.csv
    python3 main.py --seed 42 -n 2           # reproducible output
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import random
import string
import sys
import uuid
from datetime import date, datetime, timedelta

FIRST = ["Aarav", "Diya", "Rohan", "Ananya", "Kabir", "Meera", "Vivaan", "Isha",
         "Liam", "Emma", "Noah", "Olivia", "Mateo", "Sofia", "Yuki", "Hana",
         "Omar", "Layla", "Leo", "Zara", "Arjun", "Priya", "Ethan", "Mia"]
LAST = ["Sharma", "Patel", "Verma", "Iyer", "Khan", "Singh", "Gupta", "Reddy",
        "Smith", "Johnson", "Garcia", "Silva", "Tanaka", "Kim", "Müller",
        "Rossi", "Brown", "Nguyen", "Lopez", "Das", "Mehta", "Nair"]
CITIES = [("Mumbai", "India"), ("Delhi", "India"), ("Bengaluru", "India"),
          ("Pune", "India"), ("Kolkata", "India"), ("London", "UK"),
          ("New York", "USA"), ("Austin", "USA"), ("Toronto", "Canada"),
          ("Berlin", "Germany"), ("Tokyo", "Japan"), ("Sydney", "Australia"),
          ("Dubai", "UAE"), ("Singapore", "Singapore"), ("Lisbon", "Portugal")]
STREETS = ["MG Road", "Park Street", "Lake View", "Main Street", "Oak Avenue",
           "Station Road", "Hill Road", "Market Lane", "Sunset Blvd", "River Walk"]
DOMAINS = ["example.com", "mail.test", "demo.dev", "sample.org", "inbox.test"]
COMPANIES = ["Nimbus", "Bluefin", "Quantica", "Pixelworks", "Greenleaf",
             "Ironclad", "Skyline", "Brightpath", "Corelabs", "Zenith"]
SUFFIX = ["Labs", "Tech", "Systems", "Solutions", "Studio", "Inc", "Pvt Ltd"]
JOBS = ["Software Engineer", "Designer", "Data Analyst", "Product Manager",
        "Teacher", "Accountant", "Marketing Lead", "DevOps Engineer",
        "Content Writer", "Sales Executive", "Doctor", "Student"]
PRODUCTS = ["Wireless Mouse", "USB-C Cable", "Notebook", "Water Bottle",
            "Headphones", "Desk Lamp", "Backpack", "Phone Stand", "Keyboard",
            "Coffee Mug", "Smartwatch", "Power Bank"]
STATUS = ["pending", "paid", "shipped", "delivered", "cancelled"]
WORDS = ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua").split()


class Fake:
    """Field generators. Each person-ish record shares one identity."""

    def __init__(self, rng: random.Random):
        self.r = rng
        self._ctx: dict = {}

    def new_record(self) -> None:
        first, last = self.r.choice(FIRST), self.r.choice(LAST)
        self._ctx = {"first": first, "last": last}

    # identity ------------------------------------------------------------
    def id(self): return str(uuid.UUID(int=self.r.getrandbits(128), version=4))
    def first_name(self): return self._ctx["first"]
    def last_name(self): return self._ctx["last"]
    def name(self): return f"{self._ctx['first']} {self._ctx['last']}"

    def username(self):
        base = f"{self._ctx['first']}{self.r.choice(['', '.', '_'])}{self._ctx['last']}"
        base = base.lower().replace("ü", "u")
        return f"{base}{self.r.randint(1, 999)}"

    def email(self):
        local = f"{self._ctx['first']}.{self._ctx['last']}".lower().replace("ü", "u")
        return f"{local}{self.r.randint(1, 99)}@{self.r.choice(DOMAINS)}"

    def phone(self):
        return f"+91 {self.r.choice('6789')}{self.r.randint(0, 9999):04d} {self.r.randint(0, 99999):05d}"

    def age(self): return self.r.randint(18, 75)

    def birthdate(self):
        days = self.r.randint(18 * 365, 75 * 365)
        return (date.today() - timedelta(days=days)).isoformat()

    def gender(self): return self.r.choice(["female", "male", "non-binary"])
    def job(self): return self.r.choice(JOBS)
    def company(self): return f"{self.r.choice(COMPANIES)} {self.r.choice(SUFFIX)}"

    # location ------------------------------------------------------------
    def city(self):
        self._ctx.setdefault("place", self.r.choice(CITIES))
        return self._ctx["place"][0]

    def country(self):
        self._ctx.setdefault("place", self.r.choice(CITIES))
        return self._ctx["place"][1]

    def address(self): return f"{self.r.randint(1, 250)}, {self.r.choice(STREETS)}"
    def zipcode(self): return f"{self.r.randint(100000, 999999)}"

    # web / misc ----------------------------------------------------------
    def password(self):
        pool = string.ascii_letters + string.digits + "!@#$%"
        return "".join(self.r.choice(pool) for _ in range(12))

    def ip(self): return ".".join(str(self.r.randint(1, 254)) for _ in range(4))
    def url(self): return f"https://{self.r.choice(COMPANIES).lower()}.{self.r.choice(['io', 'dev', 'com'])}"
    def color(self): return f"#{self.r.randint(0, 0xFFFFFF):06x}"
    def bool(self): return self.r.random() < 0.5
    def sentence(self): return " ".join(self.r.choices(WORDS, k=self.r.randint(5, 10))).capitalize() + "."

    def created_at(self):
        delta = timedelta(seconds=self.r.randint(0, 365 * 24 * 3600))
        return (datetime.now().replace(microsecond=0) - delta).isoformat(sep=" ")

    # commerce ------------------------------------------------------------
    def product(self): return self.r.choice(PRODUCTS)
    def quantity(self): return self.r.randint(1, 5)
    def price(self): return round(self.r.uniform(99, 4999), 2)
    def status(self): return self.r.choice(STATUS)
    def order_id(self): return f"ORD-{self.r.randint(100000, 999999)}"


FIELDS = [m for m in dir(Fake) if not m.startswith("_") and m != "new_record"]
PRESETS = {
    "person": ["name", "email", "phone", "age", "city", "country"],
    "user": ["id", "username", "email", "password", "ip", "created_at"],
    "employee": ["name", "job", "company", "email", "city"],
    "address": ["name", "address", "city", "zipcode", "country"],
    "order": ["order_id", "name", "product", "quantity", "price", "status", "created_at"],
}


def generate(fields: list[str], count: int, rng: random.Random) -> list[dict]:
    fake = Fake(rng)
    rows = []
    for _ in range(count):
        fake.new_record()
        rows.append({f: getattr(fake, f)() for f in fields})
    return rows


def to_table(rows: list[dict]) -> str:
    if not rows:
        return "(no rows)"
    cols = list(rows[0])
    cells = [[str(r[c]) for c in cols] for r in rows]
    widths = [max(len(c), *(len(row[i]) for row in cells)) for i, c in enumerate(cols)]
    line = "  ".join(c.ljust(w) for c, w in zip(cols, widths))
    sep = "  ".join("-" * w for w in widths)
    body = ["  ".join(v.ljust(w) for v, w in zip(row, widths)) for row in cells]
    return "\n".join([line, sep, *body])


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    if rows:
        w = csv.DictWriter(buf, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate fake test data (offline, stdlib only).")
    p.add_argument("-n", "--count", type=int, default=5, help="number of records (default 5)")
    p.add_argument("-p", "--preset", choices=sorted(PRESETS), default="person",
                   help="field preset (default person)")
    p.add_argument("-f", "--fields", help="comma-separated fields (overrides --preset)")
    p.add_argument("--format", choices=["table", "json", "csv", "jsonl"], default="table")
    p.add_argument("-o", "--output", help="write to file instead of stdout")
    p.add_argument("--seed", type=int, help="seed for reproducible data")
    p.add_argument("--list", action="store_true", help="list fields and presets")
    a = p.parse_args(argv)

    if a.list:
        print("Fields:  " + ", ".join(FIELDS))
        for name, flds in sorted(PRESETS.items()):
            print(f"{name:<9}{', '.join(flds)}")
        return 0

    if a.count < 1 or a.count > 100_000:
        p.error("--count must be between 1 and 100000")

    fields = [f.strip() for f in a.fields.split(",")] if a.fields else PRESETS[a.preset]
    bad = [f for f in fields if f not in FIELDS]
    if bad:
        p.error(f"unknown field(s): {', '.join(bad)} (see --list)")

    rows = generate(fields, a.count, random.Random(a.seed))
    if a.format == "json":
        out = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
    elif a.format == "jsonl":
        out = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    elif a.format == "csv":
        out = to_csv(rows)
    else:
        out = to_table(rows) + "\n"

    if a.output:
        with open(a.output, "w", encoding="utf-8", newline="") as fh:
            fh.write(out)
        print(f"Wrote {len(rows)} {a.preset if not a.fields else 'custom'} record(s) to {a.output}")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
