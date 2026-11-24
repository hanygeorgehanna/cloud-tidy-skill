# Cloud Tidy Skill

A simple, open-source skill that helps you tidy a messy cloud folder —
safely, locally, and without deleting anything.

Your Drive or cloud storage is full, you keep paying for more space,
and you cannot find the files you need. Cloud Tidy scans a folder
(for example a downloaded Google Drive export) and reports:

- the **largest files**
- **duplicate files** and how much space the extra copies waste
- **forgotten files** not modified in a year (or any period you choose)
- **empty folders**

Then it suggests what to archive or review. It never deletes, moves,
or renames anything — the decision is always yours.

## Why this helps wellbeing

Digital clutter is stressful: a full drive, extra storage bills, and
files you cannot find. A short, honest report makes the mess visible
and small enough to act on, instead of overwhelming. Everything runs
on your own computer, so your files are never uploaded anywhere.

## How to use

You need Python 3.9 or newer. No extra packages are needed.

```bash
python3 tidy.py /path/to/folder
python3 tidy.py /path/to/folder --top 10 --days 180
python3 tidy.py /path/to/folder --report tidy-report.md
```

Example output:

```
# Cloud Tidy report
Folder: /home/user/Downloads/drive-export
Files scanned: 1240  |  Total size: 18.4 GB

## Largest files (top 20)
- 2.1 GB  .../videos/family-trip.mp4
...
## Duplicate files
Extra copies waste about 3.2 GB in total.
...
## Forgotten files (not modified in 365 days)
Count: 210  |  Total size: 6.8 GB
...
```

If you use an AI agent, give it `SKILL.md` as well: it tells the
agent when to use this skill, how to run the scan, and the safety
rules (read-only, no uploads, no automatic deletion).

## Safety

- **Read-only.** `tidy.py` only reads file names, sizes, and dates.
  It never deletes, moves, or renames files.
- **Local only.** No file contents leave your computer.
- **Large files.** Files over 200 MB are not hashed; they are
  reported by size only.

## Files

- `tidy.py` — the scanner. Standard library only.
- `SKILL.md` — instructions for an AI agent using this skill.
- `README.md` — this file.

## Status

This is a new, small project created on 25 November 2026. It has
no users, stars, or contributors yet. It is published as open
source under the MIT License so anyone can use it, suggest changes,
or contribute.

## Contributing

Issues and pull requests are welcome. Good first contributions:
a new report rule (for example, files by type), a shorter summary
format, or a translation of the report headings. Please keep
changes small, keep the tool read-only, and test `tidy.py` on a
sample folder before submitting.

## License

MIT — see `LICENSE`.
