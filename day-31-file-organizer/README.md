# Day 31 — File Organizer

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Tidy a messy folder (like Downloads) by moving files into subfolders by type, extension, or modified month/year. It always shows a preview first and only moves files when you add `--apply`. Every applied batch is logged so you can undo it. Standard library only.

## Features

- Group by `type` (Images, Videos, Audio, Documents, Code, Archives...), `ext`, `month` or `year`
- Preview by default with file counts and sizes per folder; `--apply` moves; `--undo` reverts
- Never overwrites: name clashes become `name (1).ext`
- Filter by extension (`-o pdf -o jpg`), skip hidden files unless `--hidden`
- Custom folder name for unknown types (`--other Misc`); `--list-types` shows categories

## Run

```bash
cd day-31-file-organizer
python3 main.py --help
```

No install needed (Python 3.8+).

## Usage

```bash
python3 main.py ~/Downloads              # preview, grouped by type
python3 main.py ~/Downloads --apply      # move files
python3 main.py ~/Downloads --undo       # put everything back
python3 main.py ~/Pictures -b month      # 2026-10/, 2026-09/ ...
python3 main.py . -b ext -o pdf -o csv   # only PDFs and CSVs, into PDF/ and CSV/
```

## Example

```
$ python3 main.py ~/Downloads

Documents/  (2 files, 1.2 MB)
  notes.txt
  report.pdf

Images/  (2 files, 3.4 MB)
  a.jpg  -> a (1).jpg
  b.PNG

Preview only: 4 files would move. Add --apply to do it.
```

## Requirements

Python 3.8+ only. No third-party packages, no API keys.
