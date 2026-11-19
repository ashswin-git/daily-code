#!/usr/bin/env python3
"""To-Do CLI: a tiny task manager that stores tasks in a JSON file."""

import argparse
import json
import os
import sys
from datetime import datetime

DB = os.environ.get("TODO_FILE", "todos.json")


def load():
    if not os.path.exists(DB):
        return []
    with open(DB, encoding="utf-8") as f:
        return json.load(f)


def save(items):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def find(items, tid):
    for t in items:
        if t["id"] == tid:
            return t
    sys.exit(f"No task with id {tid}")


def cmd_add(a):
    items = load()
    tid = max((t["id"] for t in items), default=0) + 1
    items.append({"id": tid, "text": " ".join(a.text), "done": False,
                  "created": datetime.now().isoformat(timespec="seconds")})
    save(items)
    print(f"Added #{tid}")


def cmd_list(a):
    items = load()
    if not a.all:
        items = [t for t in items if not t["done"]]
    if not items:
        print("Nothing to do!")
    for t in items:
        print(f"[{'x' if t['done'] else ' '}] {t['id']:>3}  {t['text']}")


def cmd_done(a):
    items = load()
    find(items, a.id)["done"] = True
    save(items)
    print(f"Completed #{a.id}")


def cmd_remove(a):
    items = load()
    find(items, a.id)
    save([t for t in items if t["id"] != a.id])
    print(f"Removed #{a.id}")


def cmd_clear(a):
    save([t for t in load() if not t["done"]])
    print("Cleared completed tasks")


def main():
    p = argparse.ArgumentParser(description="Simple To-Do CLI")
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("add"); x.add_argument("text", nargs="+"); x.set_defaults(f=cmd_add)
    x = s.add_parser("list"); x.add_argument("-a", "--all", action="store_true"); x.set_defaults(f=cmd_list)
    x = s.add_parser("done"); x.add_argument("id", type=int); x.set_defaults(f=cmd_done)
    x = s.add_parser("remove"); x.add_argument("id", type=int); x.set_defaults(f=cmd_remove)
    x = s.add_parser("clear"); x.set_defaults(f=cmd_clear)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
