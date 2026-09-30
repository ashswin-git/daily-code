#!/usr/bin/env python3
"""Scan day-* folders and regenerate ACHIEVEMENTS.md (progress + checklist).

Preserves the GitHub profile achievements section by rewriting the whole file
from a known template so the doc stays consistent.

Usage (from repo root):
  python3 scripts/update_achievements.py
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOTAL_DAYS = 100
MILESTONES = (10, 25, 50, 75, 100)


def day_num(name: str) -> int:
    m = re.match(r"day-(\d+)", name)
    if not m:
        raise ValueError(f"not a day folder: {name}")
    return int(m.group(1))


def parse_difficulty(folder: Path) -> str:
    """Read Difficulty from README if present; else default Easy for this series."""
    readme = folder / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            low = line.lower()
            if "difficulty" not in low:
                continue
            if "medium" in low:
                return "Medium"
            if "hard" in low:
                return "Hard"
            if "easy" in low:
                return "Easy"
    return "Easy"


def display_title(folder: Path) -> str:
    readme = folder / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return folder.name


def discover_days() -> list[dict]:
    days = []
    for p in ROOT.iterdir():
        if not p.is_dir() or not p.name.startswith("day-"):
            continue
        try:
            n = day_num(p.name)
        except ValueError:
            continue
        days.append(
            {
                "num": n,
                "folder": p.name,
                "display": display_title(p),
                "difficulty": parse_difficulty(p),
            }
        )
    days.sort(key=lambda d: d["num"])
    return days


def streak_from_day_one(nums: set[int]) -> int:
    streak = 0
    for i in range(1, TOTAL_DAYS + 1):
        if i in nums:
            streak += 1
        else:
            break
    return streak


def render(days: list[dict]) -> str:
    done = len(days)
    nums = {d["num"] for d in days}
    streak = streak_from_day_one(nums)
    easy = sum(1 for d in days if d["difficulty"] == "Easy")
    medium = sum(1 for d in days if d["difficulty"] == "Medium")
    hard = sum(1 for d in days if d["difficulty"] == "Hard")
    today = date.today().isoformat()

    milestone_lines = "\n".join(
        f"- [{'x' if done >= m else ' '}] Day {m}" for m in MILESTONES
    )
    checklist = "\n".join(
        f"- [x] [{d['folder']}/](./{d['folder']}/) — {d['display']} ({d['difficulty']})"
        for d in days
    )
    remaining = TOTAL_DAYS - done
    next_day = done + 1

    return f"""# Achievements

Progress tracker for the **100-day** lightweight Python series in this monorepo.

> Last regenerated: {today} (Asia/Kolkata calendar date on the box).  
> Tip: run `python3 scripts/update_achievements.py` after adding a new `day-*` folder.

## Series progress

| Metric | Value |
|--------|-------|
| **Days done** | **{done} / {TOTAL_DAYS}** |
| **Current streak** | **{streak}** consecutive day folders from Day 1 |
| **Easy** | {easy} |
| **Medium** | {medium} |
| **Hard** | {hard} |

### Milestones

{milestone_lines}

### Completed day folders

{checklist}

_{remaining} days remaining (day-{next_day:02d} … day-{TOTAL_DAYS:02d})._

---

## GitHub profile achievements

GitHub shows optional **profile achievements** (badges) for certain account activity.  
GitHub does **not** publish a stable official API or full criteria catalog; thresholds below are **community-observed** and may change.  
**Do not treat anything here as earned unless it is verified** (public profile achievements tab or equivalent).

Public profile check for [`ashswin-git`](https://github.com/ashswin-git?tab=achievements) (scraped / viewed, not via achievements API — none exists):

| Achievement | Typical unlock (community-reported) | Helps this 100-day series? | Status |
|-------------|--------------------------------------|----------------------------|--------|
| **Pull Shark** | Merged PRs you authored (often cited: base ~2, then higher tiers e.g. 16 / 128 / 1024) | **Yes** — if each day (or batch) is opened as a PR and merged | **Unknown / not verified as claimed** (GraphQL: 0 merged PRs visible for this account at check time) |
| **Pair Extraordinaire** | Co-authored commits (`Co-authored-by:` trailer) on merged PRs (tiers often cited ~1 / 10 / 24 / 48) | **Maybe** — only if pairing with a real collaborator on day PRs | **Unknown / not claimed** |
| **Galaxy Brain** | Answers in GitHub Discussions marked accepted (tiers often cited ~2 / 8 / 16 / 32) | **No** — not a natural side effect of daily coding alone | **Unknown / not claimed** |
| **YOLO** | Merge a PR without waiting for / without a review | **Yes (optional)** — solo day PRs self-merged without review | **Unknown / not claimed** |
| **Quickdraw** | Close an issue or PR within ~5 minutes of opening | **Incidental** — possible if issues/PRs are closed quickly; not the series goal | **Verified on public profile** |
| **Starstruck** | Stars on a repo you own (often cited: base ~16, then 128 / 512 / 4096) | **Indirect** — useful day projects may attract stars over time | **Unknown / not claimed** (`daily-code` had 0 stars at check time; other repos not exhaustively checked) |
| **Arctic Code Vault Contributor** | Code included in GitHub’s **2020** Arctic Code Vault snapshot | **No** — historical / not earnable via new 2026 work | **Unknown / not claimed** (cannot be newly earned) |
| **Public Sponsor** | Sponsor someone via GitHub Sponsors | **No** — unrelated to daily commits | **Unknown / not claimed** |
| **Mars 2020 Contributor** | Historical contribution to Mars 2020 mission repos | **No** — unobtainable | **Unknown / not claimed** (historical) |

### How this series can help (naturally)

- **Daily commits** on `day-*` folders build a visible contribution graph (not itself a badge).
- **Opening and merging PRs** per day (or per batch) is the clean path toward **Pull Shark**, and optionally **YOLO** if self-merged without review.
- **Pair programming** with proper `Co-authored-by:` trailers on merged PRs is the path toward **Pair Extraordinaire**.
- **Galaxy Brain**, **Starstruck**, **Sponsor**, and vault/mission badges are outside the core daily-code loop.

> Status policy: only **Quickdraw** is marked verified above because it appears on the public achievements tab. Everything else stays **unknown / not claimed** until re-verified.
"""


def main() -> None:
    days = discover_days()
    out = ROOT / "ACHIEVEMENTS.md"
    out.write_text(render(days), encoding="utf-8")
    print(f"Updated {out.relative_to(ROOT)} — {len(days)}/{TOTAL_DAYS} days")


if __name__ == "__main__":
    main()
