# Day 30 — File Renamer

Part of the [100-day lightweight Python series](https://github.com/ashswin-git/daily-code).

**Difficulty:** Easy

Bulk-rename files in a folder with find/replace, regex, case changes, prefixes, suffixes, numbering and date stamps. It always shows a preview first and only renames when you add `--apply`. Each applied batch is saved so you can undo it. Standard library only.

## Features

- Find/replace plain text (`-f old -r new`) or regex (`-x pattern -r new`)
- Case styles: `lower`, `upper`, `title`, `snake`, `kebab`, `camel`
- Add a prefix or suffix, a running number (`-n prefix|suffix`, `--start`, `--pad`) or the file's modified date (`-d`)
- Change or lowercase the extension (`--ext png`, `--lower-ext`)
- Pick files by extension (`-o jpg -o png`) or name regex (`-m`), sort numbering by name, date or size
- Preview by default; `--apply` renames; `--undo` reverts the last batch
- Skips anything that would collide or overwrite an existing file
- Safe two-step rename, so swapping names never clobbers a file

## Run

```bash
cd day-30-file-renamer
python3 main.py --help
```

No install needed (Python 3.8+).

## Usage

```bash
python3 main.py ~/Pictures -o jpg -c kebab --lower-ext -n prefix   # preview
python3 main.py ~/Pictures -o jpg -c kebab --lower-ext -n prefix --apply
python3 main.py ~/Pictures --undo
python3 main.py . -f "IMG_" -r "trip_"
python3 main.py . -x "\s+" -r "_" --strip
python3 main.py ~/Downloads -d -s mtime -o pdf
```

## Example

```
$ python3 main.py /tmp/demo -o jpg -c kebab --lower-ext -n prefix --apply

  2 file(s) matched, 2 to rename

  another_pic.jpg       ->  001_another-pic.jpg
  My Holiday Photo.JPG  ->  002_my-holiday-photo.jpg

  Renamed 2 file(s). Undo with: python3 main.py /tmp/demo --undo
```

## Requirements

- Python 3.8+
- No third-party packages

> Tip: the undo log is saved as `.renamer-undo.json` in the folder and only covers the most recent `--apply`.
