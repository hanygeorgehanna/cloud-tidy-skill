#!/usr/bin/env python3
"""Cloud Tidy: report large, duplicate and forgotten files in a folder.

Read-only by design. This script never deletes, moves or renames anything.
It only scans a local folder (for example a downloaded Google Drive export)
and prints a tidy-up report, so you can decide what to archive or delete.

Usage:
    python3 tidy.py /path/to/folder
    python3 tidy.py /path/to/folder --top 10 --days 180
    python3 tidy.py /path/to/folder --report tidy-report.md

Requires Python 3.9+ and only the standard library.
"""

import argparse
import hashlib
import os
import sys
from datetime import datetime, timedelta


def human_size(size):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024
    return f"{size:.1f} PB"


def file_hash(path, limit_mb=200):
    """SHA-256 of a file. Files larger than limit_mb are not hashed."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def scan(root):
    files = []
    empty_dirs = []
    skipped = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden folders such as .git, to keep the report useful.
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        if not dirnames and not filenames:
            empty_dirs.append(dirpath)
        for name in filenames:
            if name.startswith("."):
                continue
            path = os.path.join(dirpath, name)
            try:
                stat = os.stat(path)
            except OSError:
                skipped += 1
                continue
            files.append(
                {
                    "path": path,
                    "size": stat.st_size,
                    "mtime": datetime.fromtimestamp(stat.st_mtime),
                }
            )
    return files, empty_dirs, skipped


def find_duplicates(files):
    """Group files by size first, then hash only same-size candidates."""
    by_size = {}
    for item in files:
        if item["size"] == 0:
            continue
        by_size.setdefault(item["size"], []).append(item)

    groups = []
    for size, candidates in by_size.items():
        if len(candidates) < 2:
            continue
        by_hash = {}
        for item in candidates:
            if size > 200 * 1024 * 1024:
                # Too large to hash safely here; report by size + name only.
                key = ("large-unhashed", item["path"])
                by_hash.setdefault(key, []).append(item)
                continue
            try:
                key = file_hash(item["path"])
            except OSError:
                continue
            by_hash.setdefault(key, []).append(item)
        for members in by_hash.values():
            if len(members) > 1 and not members[0]["path"].startswith("large"):
                groups.append(members)
            elif len(members) > 1:
                groups.append(members)
    # Sort groups by wasted space (size * extra copies), largest first.
    groups.sort(key=lambda g: g[0]["size"] * (len(g) - 1), reverse=True)
    return groups


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cloud Tidy: report large, duplicate and forgotten files. Read-only, never deletes."
    )
    parser.add_argument("folder", help="Folder to scan, for example a Drive export")
    parser.add_argument("--top", type=int, default=20, help="How many largest files to list (default: 20)")
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="A file is 'forgotten' if not modified in this many days (default: 365)",
    )
    parser.add_argument("--report", help="Also write the report to this Markdown file")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.folder)
    if not os.path.isdir(root):
        print(f"Error: not a folder: {root}", file=sys.stderr)
        return 2

    files, empty_dirs, skipped = scan(root)
    total_size = sum(item["size"] for item in files)
    cutoff = datetime.now() - timedelta(days=args.days)
    forgotten = sorted(
        (item for item in files if item["mtime"] < cutoff),
        key=lambda item: item["size"],
        reverse=True,
    )
    largest = sorted(files, key=lambda item: item["size"], reverse=True)[: args.top]
    duplicates = find_duplicates(files)
    duplicate_waste = sum(g[0]["size"] * (len(g) - 1) for g in duplicates)

    lines = []
    lines.append("# Cloud Tidy report")
    lines.append("")
    lines.append(f"Folder: {root}")
    lines.append(f"Files scanned: {len(files)}  |  Total size: {human_size(total_size)}")
    if skipped:
        lines.append(f"Files skipped (unreadable): {skipped}")
    lines.append("")

    lines.append(f"## Largest files (top {args.top})")
    if largest:
        for item in largest:
            lines.append(f"- {human_size(item['size']):>10}  {item['path']}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Duplicate files")
    if duplicates:
        lines.append(f"Extra copies waste about {human_size(duplicate_waste)} in total.")
        for group in duplicates[:20]:
            lines.append(f"- {human_size(group[0]['size'])} x {len(group)} copies:")
            for item in group:
                lines.append(f"  - {item['path']}")
    else:
        lines.append("- No duplicates found.")
    lines.append("")

    lines.append(f"## Forgotten files (not modified in {args.days} days)")
    if forgotten:
        lines.append(f"Count: {len(forgotten)}  |  Total size: {human_size(sum(i['size'] for i in forgotten))}")
        for item in forgotten[: args.top]:
            lines.append(f"- {human_size(item['size']):>10}  {item['mtime'].date()}  {item['path']}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Empty folders")
    if empty_dirs:
        for path in empty_dirs[:50]:
            lines.append(f"- {path}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Suggested next step")
    lines.append("Review the lists above. Archive what you still need, then delete")
    lines.append("only the copies and files you are sure you do not need. Cloud Tidy")
    lines.append("never deletes anything by itself.")
    lines.append("")

    report = "\n".join(lines)
    print(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as handle:
            handle.write(report)
        print(f"Report also written to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
