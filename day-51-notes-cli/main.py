#!/usr/bin/env python3
"""Notes CLI - tiny note taker backed by a JSON file."""
import argparse
import json
import os
import sys
from datetime import datetime

FILE = os.environ.get("NOTES_FILE", "notes.json")


def load():
    if not os.path.exists(FILE):
        return []
    with open(FILE, encoding="utf-8") as f:
        return json.load(f)


def save(notes):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def find(notes, nid):
    for n in notes:
        if n["id"] == nid:
            return n
    sys.exit(f"No note with id {nid}")


def main():
    p = argparse.ArgumentParser(description="Notes CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="add a note"); a.add_argument("text", nargs="+")
    sub.add_parser("list", help="list notes")
    v = sub.add_parser("view", help="show a note"); v.add_argument("id", type=int)
    e = sub.add_parser("edit", help="edit a note"); e.add_argument("id", type=int); e.add_argument("text", nargs="+")
    s = sub.add_parser("search", help="search notes"); s.add_argument("query")
    d = sub.add_parser("delete", help="delete a note"); d.add_argument("id", type=int)
    args = p.parse_args()

    notes = load()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if args.cmd == "add":
        nid = max((n["id"] for n in notes), default=0) + 1
        notes.append({"id": nid, "text": " ".join(args.text), "created": now})
        save(notes); print(f"Added note {nid}")
    elif args.cmd == "list":
        if not notes: print("No notes yet.")
        for n in notes:
            print(f"{n['id']:>3}  {n['created']}  {n['text'][:60]}")
    elif args.cmd == "view":
        n = find(notes, args.id)
        print(f"#{n['id']} ({n['created']})\n{n['text']}")
    elif args.cmd == "edit":
        n = find(notes, args.id); n["text"] = " ".join(args.text)
        save(notes); print(f"Updated note {args.id}")
    elif args.cmd == "search":
        hits = [n for n in notes if args.query.lower() in n["text"].lower()]
        for n in hits: print(f"{n['id']:>3}  {n['text'][:60]}")
        if not hits: print("No matches.")
    elif args.cmd == "delete":
        find(notes, args.id)
        save([n for n in notes if n["id"] != args.id]); print(f"Deleted note {args.id}")


if __name__ == "__main__":
    main()
