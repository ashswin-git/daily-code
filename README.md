# daily-code

100 days of small, self-contained Python projects.

Each day lives in its own folder under this monorepo. Original standalone repos may still exist for history; this repo is the consolidated home going forward.

## Days

| Day | Folder | Description |
|-----|--------|-------------|
| 1 | [day-01-random-password-generator](./day-01-random-password-generator/) | CLI random password generator (`secrets`) |
| 2 | [day-02-username-generator](./day-02-username-generator/) | CLI adjective/noun username generator |
| 3 | [day-03-qr-code-generator](./day-03-qr-code-generator/) | CLI QR code generator (terminal / SVG / PNG via `segno`) |
| 4 | [day-04-unit-converter](./day-04-unit-converter/) | CLI length / mass / temperature / volume converter |
| 5 | [day-05-tip-calculator](./day-05-tip-calculator/) | CLI tip calculator with split and currency |
| 6 | [day-06-bmi-calculator](./day-06-bmi-calculator/) | CLI BMI calculator (metric / imperial, WHO categories) |
| 7 | [day-07-age-calculator](./day-07-age-calculator/) | CLI exact age + next birthday countdown |
| 8 | [day-08-dice-roller](./day-08-dice-roller/) | CLI tabletop dice roller (`2d6+3`, keep highest, advantage) |
| 9 | [day-09-url-shortener](./day-09-url-shortener/) | CLI URL shortener + link expander (TinyURL / is.gd, no API key) |
| 10 | [day-10-word-counter](./day-10-word-counter/) | CLI word counter with reading time + top-words chart |
| 11 | [day-11-character-counter](./day-11-character-counter/) | CLI character counter by type + frequency chart |
| 12 | [day-12-text-case-converter](./day-12-text-case-converter/) | CLI text case converter (snake, camel, title, kebab and more) |

## Progress

Track series milestones, difficulty counts, and completed day folders in [`ACHIEVEMENTS.md`](./ACHIEVEMENTS.md).

**Currently done:**

- [day-01-random-password-generator](./day-01-random-password-generator/)
- [day-02-username-generator](./day-02-username-generator/)
- [day-03-qr-code-generator](./day-03-qr-code-generator/)
- [day-04-unit-converter](./day-04-unit-converter/)
- [day-05-tip-calculator](./day-05-tip-calculator/)
- [day-06-bmi-calculator](./day-06-bmi-calculator/)
- [day-07-age-calculator](./day-07-age-calculator/)
- [day-08-dice-roller](./day-08-dice-roller/)
- [day-09-url-shortener](./day-09-url-shortener/)
- [day-10-word-counter](./day-10-word-counter/)
- [day-11-character-counter](./day-11-character-counter/)
- [day-12-text-case-converter](./day-12-text-case-converter/)

Regenerate the achievements doc after adding a day:

```bash
python3 scripts/update_achievements.py
```

## Quick start

```bash
git clone https://github.com/ashswin-git/daily-code.git
cd daily-code/day-01-random-password-generator
python3 main.py --help
```

Python 3.10+, standard library only unless a day says otherwise.

## Posts

Short daily notes live under [`posts/`](./posts/).

## License

MIT unless a day folder says otherwise.
