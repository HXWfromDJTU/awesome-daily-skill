#!/usr/bin/env python3
"""Block Android APK installation routes through ADB appops.

Default mode is dry-run. Pass --apply only after user confirmation.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass


KNOWN_INSTALL_ROUTE_PACKAGES = {
    "com.huawei.appmarket": "Huawei AppGallery",
    "com.huawei.browser": "Huawei Browser",
    "com.huawei.fastapp": "Huawei Quick App",
    "com.huawei.fastappengine": "Huawei Quick App Engine",
    "com.hihonor.appmarket": "Honor App Market",
    "com.hihonor.fastapp": "Honor Quick App",
    "com.hihonor.fastappengine": "Honor Quick App Engine",
    "com.xiaomi.market": "Xiaomi App Store",
    "com.android.browser": "System Browser",
    "com.android.chrome": "Chrome Browser",
    "com.mi.globalbrowser": "Mi Browser",
    "com.miui.hybrid": "Xiaomi Quick App",
    "com.miui.hybrid.accessory": "Xiaomi Quick App Accessory",
    "com.heytap.market": "HeyTap Market",
    "com.oppo.market": "OPPO Market",
    "com.heytap.browser": "HeyTap Browser",
    "com.nearme.instant.platform": "OPPO Quick App Platform",
    "com.heytap.quickgame": "HeyTap Quick Game",
    "com.bbk.appstore": "vivo App Store",
    "com.vivo.browser": "vivo Browser",
    "com.vivo.hybrid": "vivo Quick App",
    "com.vivo.quickapp": "vivo Quick App",
    "com.tencent.android.qqdownloader": "Tencent MyApp",
    "com.baidu.appsearch": "Baidu App Search",
    "com.baidu.searchbox": "Baidu Search",
    "com.qihoo.appstore": "360 App Store",
    "com.wandoujia.phoenix2": "Wandoujia",
}

KEYWORD_HINTS = (
    "market",
    "appstore",
    "browser",
    "download",
    "downloader",
    "filemanager",
    "fileexplorer",
    "quickapp",
    "fastapp",
    "hybrid",
    "gamecenter",
)

NEVER_TOUCH_PACKAGES = {
    "com.tencent.mm",  # WeChat
    "com.eg.android.AlipayGphone",  # Alipay
}


@dataclass
class RoutePackage:
    index: int
    package: str
    reason: str
    before: str = ""
    after: str = ""
    status: str = "planned"


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


def parse_devices(output: str) -> list[tuple[str, str]]:
    devices: list[tuple[str, str]] = []
    for line in output.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices


def parse_package_list(output: str) -> set[str]:
    packages: set[str] = set()
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            packages.add(line.removeprefix("package:").strip())
    return packages


def package_requests_install_permission(adb_path: str, package: str) -> bool:
    code, out, _ = shell(adb_path, "dumpsys", "package", package, timeout=30)
    if code != 0:
        return False
    return "android.permission.REQUEST_INSTALL_PACKAGES" in out


def discover_route_packages(adb_path: str, all_packages: set[str], extra_packages: list[str]) -> list[RoutePackage]:
    routes: dict[str, str] = {}
    for package, reason in KNOWN_INSTALL_ROUTE_PACKAGES.items():
        if package in all_packages:
            routes[package] = reason

    for package in all_packages:
        lower = package.lower()
        if package in NEVER_TOUCH_PACKAGES:
            continue
        if any(hint in lower for hint in KEYWORD_HINTS) and package_requests_install_permission(adb_path, package):
            routes.setdefault(package, "package name matches install-route keyword")

    for package in extra_packages:
        if package in all_packages:
            routes.setdefault(package, "user-specified package")
        else:
            routes.setdefault(package, "user-specified package, not found in package list")

    return [
        RoutePackage(index=index, package=package, reason=reason)
        for index, (package, reason) in enumerate(sorted(routes.items()), start=1)
    ]


def print_table(routes: list[RoutePackage]) -> None:
    headers = ["No.", "Package", "Reason", "Before", "After/Status"]
    rows = [
        [
            str(route.index),
            route.package,
            route.reason,
            route.before or "-",
            route.after or route.status,
        ]
        for route in routes
    ]
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    print("| " + " | ".join(headers[index].ljust(widths[index]) for index in range(len(headers))) + " |")
    print("| " + " | ".join("-" * widths[index] for index in range(len(headers))) + " |")
    for row in rows:
        print("| " + " | ".join(row[index].ljust(widths[index]) for index in range(len(headers))) + " |")


def parse_selection(selection: str, max_index: int) -> set[int]:
    selected: set[int] = set()
    if not selection:
        return selected
    normalized = selection.replace("，", ",").replace("、", ",").replace(" ", "")
    for part in normalized.split(","):
        if not part:
            continue
        if "-" in part:
            start_raw, end_raw = part.split("-", 1)
            start = int(start_raw)
            end = int(end_raw)
            if start > end:
                start, end = end, start
            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))
    invalid = sorted(index for index in selected if index < 1 or index > max_index)
    if invalid:
        raise ValueError(f"Selection out of range: {', '.join(map(str, invalid))}")
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run or apply REQUEST_INSTALL_PACKAGES ignore for install-route packages.")
    parser.add_argument("--adb", default="adb", help="Path to adb executable. Defaults to adb on PATH.")
    parser.add_argument("--apply", action="store_true", help="Apply appops changes. Without this flag, only prints the plan.")
    parser.add_argument("--package", action="append", default=[], help="Additional package to include. Can be repeated.")
    parser.add_argument("--select", default="", help="Apply only selected dry-run item numbers, for example 1,3,5 or 1-4. Defaults to all.")
    args = parser.parse_args()

    code, out, err = adb(args.adb, "devices", "-l")
    if code != 0:
        print(f"ADB failed: {err or out}", file=sys.stderr)
        return code or 1
    devices = parse_devices(out)
    if len(devices) != 1 or devices[0][1] != "device":
        print("Expected exactly one authorized Android device.", file=sys.stderr)
        print(out, file=sys.stderr)
        return 2

    code, all_out, all_err = shell(args.adb, "pm", "list", "packages", timeout=60)
    if code != 0:
        print(f"Failed to list packages: {all_err or all_out}", file=sys.stderr)
        return code or 1

    routes = discover_route_packages(args.adb, parse_package_list(all_out), args.package)
    if not routes:
        print("No install-route packages discovered.")
        return 0

    if args.select:
        try:
            selected = parse_selection(args.select, len(routes))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        routes = [route for route in routes if route.index in selected]

    print("# Install Route Permission Plan")
    print(f"\nMode: {'APPLY' if args.apply else 'DRY RUN'}")
    print("\nThis only changes the APK installation permission appop. It does not uninstall apps.\n")

    for route in routes:
        get_code, get_out, get_err = shell(args.adb, "appops", "get", route.package, "REQUEST_INSTALL_PACKAGES")
        route.before = get_out or get_err or f"appops get exited {get_code}"
        if args.apply:
            set_code, set_out, set_err = shell(args.adb, "appops", "set", route.package, "REQUEST_INSTALL_PACKAGES", "ignore")
            if set_code == 0:
                verify_code, verify_out, verify_err = shell(args.adb, "appops", "get", route.package, "REQUEST_INSTALL_PACKAGES")
                route.after = verify_out or verify_err or f"verify exited {verify_code}"
                route.status = "applied"
            else:
                route.status = f"failed: {set_err or set_out or set_code}"
        else:
            route.status = f"adb shell appops set {route.package} REQUEST_INSTALL_PACKAGES ignore"

    print_table(routes)

    if not args.apply:
        print("\nAsk the user to reply with one of these:")
        print("- 确认禁用全部")
        print("- 确认禁用 1,3,5")
        print("\nAfter the user confirms all items, run:")
        print("\n```bash")
        print("python3 scripts/block_install_routes.py --apply")
        print("```")
        print("\nAfter the user confirms selected item numbers, run:")
        print("\n```bash")
        print("python3 scripts/block_install_routes.py --apply --select 1,3,5")
        print("```")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
