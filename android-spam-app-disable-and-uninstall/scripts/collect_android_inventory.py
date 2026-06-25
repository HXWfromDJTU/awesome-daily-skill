#!/usr/bin/env python3
"""Collect a read-only Android app inventory through ADB."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime


OFFICIAL_INSTALLERS = {
    "com.huawei.appmarket",
    "com.hihonor.appmarket",
    "com.xiaomi.market",
    "com.heytap.market",
    "com.oppo.market",
    "com.bbk.appstore",
}

SUSPICIOUS_INSTALLER_HINTS = (
    "browser",
    "file",
    "download",
    "qqdownloader",
    "appsearch",
    "wandoujia",
    "qihoo",
    "baidu",
    "sogou",
)

SUSPICIOUS_PACKAGE_HINTS = (
    "clean",
    "cleaner",
    "boost",
    "speed",
    "wifi",
    "redpacket",
    "hongbao",
    "ad",
    "ads",
    "quick",
    "fastapp",
    "game",
)

VENDOR_CANDIDATES = {
    "Huawei app market": "com.huawei.appmarket",
    "Huawei quick app": "com.huawei.fastapp",
    "Huawei quick app engine": "com.huawei.fastappengine",
    "Huawei browser": "com.huawei.browser",
    "Honor app market": "com.hihonor.appmarket",
    "Honor quick app": "com.hihonor.fastapp",
    "Honor quick app engine": "com.hihonor.fastappengine",
    "Xiaomi app store": "com.xiaomi.market",
    "Xiaomi hybrid quick app": "com.miui.hybrid",
    "Xiaomi hybrid accessory": "com.miui.hybrid.accessory",
    "Android browser": "com.android.browser",
    "Mi browser": "com.mi.globalbrowser",
    "HeyTap market": "com.heytap.market",
    "OPPO market": "com.oppo.market",
    "OPPO instant platform": "com.nearme.instant.platform",
    "HeyTap browser": "com.heytap.browser",
    "vivo app store": "com.bbk.appstore",
    "vivo browser": "com.vivo.browser",
    "vivo hybrid": "com.vivo.hybrid",
    "vivo quick app": "com.vivo.quickapp",
    "Tencent MyApp": "com.tencent.android.qqdownloader",
    "Baidu app search": "com.baidu.appsearch",
    "360 app store": "com.qihoo.appstore",
    "Wandoujia": "com.wandoujia.phoenix2",
}


@dataclass
class PackageInfo:
    package: str
    installer: str
    suggestion: str


def run_command(args: list[str], timeout: int = 20) -> tuple[int, str, str]:
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


def adb(adb_path: str, *args: str, timeout: int = 20) -> tuple[int, str, str]:
    return run_command([adb_path, *args], timeout=timeout)


def shell(adb_path: str, *args: str, timeout: int = 20) -> tuple[int, str, str]:
    return adb(adb_path, "shell", *args, timeout=timeout)


def parse_devices(output: str) -> list[tuple[str, str, str]]:
    devices: list[tuple[str, str, str]] = []
    for line in output.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=2)
        if len(parts) >= 2:
            devices.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
    return devices


def parse_packages_with_installers(output: str) -> list[PackageInfo]:
    packages: list[PackageInfo] = []
    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("package:"):
            continue
        raw = line.removeprefix("package:")
        package = raw
        installer = ""
        if " installer=" in raw:
            package, installer = raw.split(" installer=", 1)
        packages.append(PackageInfo(package=package.strip(), installer=installer.strip(), suggestion=""))
    return packages


def parse_install_source(output: str) -> str:
    for key in ("installerPackageName", "initiatingPackageName", "originatingPackageName"):
        match = re.search(rf"{key}=([^\s]+)", output)
        if match and match.group(1) not in {"null", "None"}:
            return match.group(1)
    stripped = output.strip()
    return stripped if stripped and "\n" not in stripped else ""


def classify(package: str, installer: str) -> str:
    package_l = package.lower()
    installer_l = installer.lower()
    if installer in OFFICIAL_INSTALLERS:
        return "ask: official store installed, confirm whether parent needs it"
    if not installer:
        return "review: installer unknown or empty"
    if any(hint in installer_l for hint in SUSPICIOUS_INSTALLER_HINTS):
        return "high-risk: installed by browser/file/downloader/third-party route"
    if any(hint in package_l for hint in SUSPICIOUS_PACKAGE_HINTS):
        return "review: package name looks like cleaner/booster/ad/quick-app"
    return "ask: confirm with parent"


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
    lines = []
    header = rows[0]
    lines.append("| " + " | ".join(str(header[i]).ljust(widths[i]) for i in range(len(header))) + " |")
    lines.append("| " + " | ".join("-" * widths[i] for i in range(len(header))) + " |")
    for row in rows[1:]:
        lines.append("| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(row))) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a read-only Android app inventory via ADB.")
    parser.add_argument("--adb", default="adb", help="Path to adb executable. Defaults to adb on PATH.")
    parser.add_argument("--no-deep-source", action="store_true", help="Do not call get-install-source for each app.")
    args = parser.parse_args()

    code, out, err = adb(args.adb, "devices", "-l")
    if code != 0:
        print(f"ADB failed: {err or out}", file=sys.stderr)
        return code or 1

    devices = parse_devices(out)
    print(f"# Android App Inventory\n")
    print(f"- Generated at: {datetime.now().isoformat(timespec='seconds')}")
    print(f"- ADB command: `{args.adb}`\n")

    if len(devices) != 1 or devices[0][1] != "device":
        print("## Device Check\n")
        print("Expected exactly one authorized device.\n")
        print("```text")
        print(out)
        print("```")
        return 2

    print("## Device\n")
    props = [
        ("manufacturer", "ro.product.manufacturer"),
        ("brand", "ro.product.brand"),
        ("model", "ro.product.model"),
        ("android", "ro.build.version.release"),
        ("build", "ro.build.version.incremental"),
    ]
    for label, prop in props:
        _, value, _ = shell(args.adb, "getprop", prop)
        print(f"- {label}: {value or 'unknown'}")

    code, packages_out, packages_err = shell(args.adb, "pm", "list", "packages", "-3", "-i", timeout=60)
    if code != 0:
        print(f"\nFailed to list third-party packages: {packages_err or packages_out}", file=sys.stderr)
        return code or 1

    packages = parse_packages_with_installers(packages_out)
    if not args.no_deep_source:
        for pkg in packages:
            code, source_out, _ = shell(args.adb, "cmd", "package", "get-install-source", pkg.package, timeout=15)
            source = parse_install_source(source_out) if code == 0 else ""
            if source:
                pkg.installer = source

    for pkg in packages:
        pkg.suggestion = classify(pkg.package, pkg.installer)

    print("\n## Third-Party Packages\n")
    rows = [["Suggestion", "Package", "Installer"]]
    for pkg in sorted(packages, key=lambda item: (item.suggestion, item.package)):
        rows.append([pkg.suggestion, pkg.package, pkg.installer or "(unknown)"])
    print(markdown_table(rows) if len(rows) > 1 else "No third-party packages found.")

    code, all_packages_out, _ = shell(args.adb, "pm", "list", "packages", timeout=60)
    all_packages = {line.removeprefix("package:").strip() for line in all_packages_out.splitlines() if line.startswith("package:")}

    print("\n## Candidate Install Routes Found\n")
    candidate_rows = [["Route", "Package", "Suggested next check"]]
    for label, package in sorted(VENDOR_CANDIDATES.items()):
        if package in all_packages:
            candidate_rows.append([label, package, f"adb shell appops get {package} REQUEST_INSTALL_PACKAGES"])
    print(markdown_table(candidate_rows) if len(candidate_rows) > 1 else "No known candidate install routes found.")

    print("\n## Reminder\n")
    print("This script is read-only. Do not remove or disable apps until the parent confirms the final list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
