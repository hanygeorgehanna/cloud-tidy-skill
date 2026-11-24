# Cloud Tidy Skill

## Name
cloud-tidy

## Description
Help a user tidy a messy cloud folder (for example a Google Drive export)
by reporting the largest, duplicate, and forgotten files, and suggesting
what to archive or review. Read-only: never delete, move, or rename files.

Use this skill when a user says their Drive, cloud storage, or a folder
is full, messy, duplicated, or hard to search, or when they want to free
space, stop paying for extra storage, or feel less overwhelmed by digital
clutter.

## How it works
1. Ask the user which folder to scan. If they name a cloud service,
   ask them to download / export that folder first, or point the scan
   at a local copy. Do not ask for cloud passwords or API keys.
2. Run the local script (Python 3.9+, standard library only):
   ```bash
   python3 tidy.py /path/to/folder --top 20 --days 365 --report tidy-report.md
   ```
   Use `--days 180` if the user wants a shorter "forgotten" window,
   and `--top 10` for a shorter list.
3. Read the report and summarise it in plain language:
   - total files and total size
   - the largest files, with sizes
   - duplicate groups and how much space the extra copies waste
   - forgotten files (not modified in the chosen number of days)
   - empty folders
4. Suggest a concrete next step, in this order: archive what is still
   needed, review duplicates and keep one copy, then delete only what
   the user confirms. Present the list and wait for the user's choice
   before doing anything else.

## Safety rules
- **Never delete, move, or rename anything.** This skill only reports.
- **Never upload files.** The scan runs locally; file contents are
  never sent to a server. Only file names, sizes, and dates appear
  in the report.
- **Do not hash or open very large files unnecessarily.** The script
  skips hashing files over 200 MB and reports them by size instead.
- If a file cannot be read, skip it and say so in the report.
- If the user asks you to delete something, list the exact files
  first and get an explicit confirmation for each one before any
  deletion, in a separate step outside this skill.

## Example
User: "My Drive is full and I keep paying for more storage."
Assistant: asks for the exported folder, runs
`python3 tidy.py ~/Downloads/drive-export --top 20 --days 365`,
then says: "You have 1,240 files totalling 18.4 GB. The largest file
is a 2.1 GB video. There are 14 duplicate groups wasting about
3.2 GB. 210 files have not been modified in a year. Here is the
list — shall we archive the old videos first, or review the
duplicates?"
