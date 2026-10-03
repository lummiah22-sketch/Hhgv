#!/usr/bin/env python3
"""Clean a project.zip archive by removing duplicate and generated files.

This keeps the real project code while deleting obvious junk such as:
- __pycache__ folders
- compiled .pyc files
- .db files
- .bak / .backup files
- duplicate project backups such as backend_backup_giftcard

Usage:
    python clean_project_zip.py path/to/project.zip
    python clean_project_zip.py

By default it cleans `project.zip` in the current directory.
"""

from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path


def is_unwanted(name: str) -> bool:
    lower = name.replace("\\", "/").lower()

    if not lower or lower.startswith("/"):
        return True

    # Common junk / generated folders
    if "__pycache__" in lower:
        return True
    if lower.endswith(".pyc"):
        return True
    if lower.endswith(".pyo"):
        return True

    # Database / local runtime files
    if lower.endswith(".db"):
        return True
    if lower.endswith(".sqlite3"):
        return True

    # Backup / duplicate project artifacts
    if "backend_backup_giftcard" in lower:
        return True
    if lower.endswith(".bak"):
        return True
    if ".backup" in lower:
        return True
    if "backup-support" in lower:
        return True
    if "backup5" in lower:
        return True

    # Keep the real app code. Ignore generated OS junk if present.
    if lower.startswith("__macosx/"):
        return True

    return False


def clean_zip_file(zip_path: Path) -> Path:
    zip_path = zip_path.resolve()
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as src:
        names = src.namelist()
        kept = []
        for name in names:
            if not is_unwanted(name):
                kept.append(name)

    if len(kept) == len(zipfile.ZipFile(zip_path).namelist()):
        return zip_path

    backup = zip_path.with_suffix(zip_path.suffix + ".bak")
    if backup.exists():
        backup.unlink()
    os.replace(zip_path, backup)

    with zipfile.ZipFile(backup, "r") as src, zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            if is_unwanted(info.filename):
                continue
            data = src.read(info.filename)
            dst.writestr(info, data)

    return zip_path


def main() -> int:
    if len(sys.argv) > 1:
        targets = [Path(arg) for arg in sys.argv[1:]]
    else:
        targets = [Path("project.zip")]

    for target in targets:
        try:
            cleaned = clean_zip_file(target)
            print(f"Cleaned: {cleaned}")
        except Exception as exc:  # pragma: no cover
            print(f"ERROR: {target}: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
