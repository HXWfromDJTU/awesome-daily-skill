#!/usr/bin/env python3
"""Install Android SDK Platform-Tools for the current OS if adb is missing.

The script downloads only from Google's official dl.google.com Android
repository, installs into a user-scoped directory, and does not modify PATH.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path


DOWNLOADS = {
    "Darwin": (
        "platform-tools-latest-darwin.zip",
        "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip",
        "platform-tools/adb",
    ),
    "Windows": (
        "platform-tools-latest-windows.zip",
        "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
        "platform-tools/adb.exe",
    ),
    "Linux": (
        "platform-tools-latest-linux.zip",
        "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
        "platform-tools/adb",
    ),
}


def default_install_dir() -> Path:
    return Path.home() / ".codex" / "tools" / "android-platform-tools"


def run(args: list[str], timeout: int = 20) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", f"Command not found: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"Command timed out: {' '.join(args)}"
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def existing_adb(explicit_adb: str | None) -> Path | None:
    if explicit_adb:
        adb = Path(explicit_adb).expanduser()
        return adb if adb.exists() else None
    found = shutil.which("adb")
    return Path(found) if found else None


def safe_extract(zip_path: Path, install_dir: Path) -> None:
    install_dir.mkdir(parents=True, exist_ok=True)
    install_root = install_dir.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = install_dir / member.filename
            resolved = target.resolve()
            try:
                resolved.relative_to(install_root)
            except ValueError:
                raise RuntimeError(f"Unsafe zip member path: {member.filename}")
        archive.extractall(install_dir)


def chmod_executable(path: Path) -> None:
    if os.name == "nt":
        return
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure adb exists for the current operating system.")
    parser.add_argument("--install-dir", default=str(default_install_dir()), help="User-scoped install directory.")
    parser.add_argument("--adb", default="", help="Explicit adb path to verify before downloading.")
    parser.add_argument("--force", action="store_true", help="Download even if adb is already available.")
    parser.add_argument("--dry-run", action="store_true", help="Print detected OS, URL, and target path without downloading.")
    args = parser.parse_args()

    system = platform.system()
    if system not in DOWNLOADS:
        print(f"Unsupported OS: {system}", file=sys.stderr)
        print("Supported OS values: Darwin, Windows, Linux", file=sys.stderr)
        return 2

    zip_name, url, adb_relative = DOWNLOADS[system]
    install_dir = Path(args.install_dir).expanduser()
    target_adb = install_dir / adb_relative

    detected = existing_adb(args.adb or None)
    if detected and not args.force:
        code, out, err = run([str(detected), "version"])
        if code == 0:
            print(f"OS: {system}")
            print(f"ADB already available: {detected}")
            print(out)
            return 0
        print(f"Existing adb failed, will download official platform-tools: {err or out}", file=sys.stderr)

    print(f"OS: {system}")
    print(f"Download URL: {url}")
    print(f"Install dir: {install_dir}")
    print(f"ADB path: {target_adb}")
    print("PATH will not be modified.")

    if args.dry_run:
        return 0

    zip_path = install_dir / zip_name
    install_dir.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, zip_path)
    safe_extract(zip_path, install_dir)
    if not target_adb.exists():
        print(f"ADB not found after extraction: {target_adb}", file=sys.stderr)
        return 1
    chmod_executable(target_adb)

    code, out, err = run([str(target_adb), "version"])
    if code != 0:
        print(f"Downloaded adb failed verification: {err or out}", file=sys.stderr)
        return code or 1
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
