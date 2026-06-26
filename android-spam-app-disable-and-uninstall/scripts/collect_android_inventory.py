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

PROTECTED_EXACT_PACKAGES = {
    "com.android.contacts": "重要：联系人",
    "com.android.dialer": "重要：电话",
    "com.android.incallui": "重要：通话界面",
    "com.android.launcher": "重要：桌面",
    "com.android.mms": "重要：短信",
    "com.android.phone": "重要：电话服务",
    "com.android.providers.contacts": "重要：联系人存储",
    "com.android.settings": "重要：系统设置",
    "com.android.systemui": "重要：系统界面",
    "com.eg.android.AlipayGphone": "重要：支付宝",
    "com.tencent.mm": "重要：微信",
    "com.unionpay.tsmservice": "重要：银联",
}

PROTECTED_PACKAGE_HINTS = (
    "10010",
    "10086",
    "189",
    "alipay",
    "bank",
    "bankcomm",
    "bocom",
    "ccb",
    "chinamobile",
    "cmbc",
    "cmb",
    "cmbchina",
    "contacts",
    "ctclient",
    "dialer",
    "gallery",
    "icbc",
    "ime",
    "input",
    "insurance",
    "keyboard",
    "launcher",
    "map",
    "mms",
    "phone",
    "settings",
    "sms",
    "sinovatech",
    "telecom",
    "telephony",
    "unionpay",
    "unicom",
    "wechat",
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
    installer: str = ""
    app_name: str = ""
    first_install_time: str = ""
    last_update_time: str = ""
    group: str = ""
    suggestion: str = ""


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


def clean_metadata_value(value: str) -> str:
    value = value.strip().strip("'\"")
    if value in {"", "null", "None"} or value.startswith("null "):
        return ""
    return value


def parse_dumpsys_field(output: str, field_name: str) -> str:
    prefix = f"{field_name}="
    for line in output.splitlines():
        line = line.strip()
        if prefix not in line:
            continue
        value = line.split(prefix, 1)[1].strip()
        for trailer in (" icon=", " banner=", " description=", " enabled=", " flags="):
            value = value.split(trailer, 1)[0].strip()
        return clean_metadata_value(value)
    return ""


def parse_app_name(output: str) -> str:
    for field_name in ("nonLocalizedLabel", "label"):
        value = parse_dumpsys_field(output, field_name)
        if value and not value.startswith("0x"):
            return value
    return ""


def fill_package_metadata(adb_path: str, pkg: PackageInfo) -> None:
    code, out, _ = shell(adb_path, "dumpsys", "package", pkg.package, timeout=30)
    if code != 0 or not out:
        return
    pkg.app_name = parse_app_name(out)
    pkg.first_install_time = parse_dumpsys_field(out, "firstInstallTime")
    pkg.last_update_time = parse_dumpsys_field(out, "lastUpdateTime")
    if not pkg.installer:
        pkg.installer = parse_dumpsys_field(out, "installerPackageName")


def package_has_hint(package: str, hints: tuple[str, ...]) -> bool:
    package_l = package.lower()
    return any(hint in package_l for hint in hints)


def classify(package: str, installer: str) -> tuple[str, str]:
    package_l = package.lower()
    installer_l = installer.lower()
    if package in PROTECTED_EXACT_PACKAGES:
        return "重要/谨慎", f"{PROTECTED_EXACT_PACKAGES[package]}，默认保留；若确实不用，也必须二次确认"
    if package_has_hint(package, PROTECTED_PACKAGE_HINTS):
        return "重要/谨慎", "像通信、支付、银行保险、地图、输入法、桌面或设置类；默认保留，确认不用才处理"
    if package in VENDOR_CANDIDATES.values():
        return "安装入口", "先禁用安装 APK 权限，不建议直接删除 App 本体"
    if installer in OFFICIAL_INSTALLERS:
        return "普通复核", "官方应用商店安装，也要确认家人是否真的需要"
    if not installer:
        return "重点复核", "安装来源未知或未读取到，建议确认用途"
    if any(hint in installer_l for hint in SUSPICIOUS_INSTALLER_HINTS):
        return "重点复核", "来自浏览器、文件管理器、下载器或第三方安装入口"
    if any(hint in package_l for hint in SUSPICIOUS_PACKAGE_HINTS):
        return "重点复核", "包名像清理、加速、广告、快应用、游戏或 Wi-Fi 类"
    return "普通复核", "请和家人确认是否还需要"


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
    parser.add_argument("--include-system", action="store_true", help="Include system packages in the review table.")
    parser.add_argument("--no-deep-source", action="store_true", help="Do not call get-install-source for each app.")
    parser.add_argument("--no-metadata", action="store_true", help="Do not call dumpsys package for app name and install time.")
    parser.add_argument("--page-size", type=int, default=0, help="Rows per page. Defaults to 0, which prints all rows.")
    parser.add_argument("--page", type=int, default=1, help="Page number when --page-size is used.")
    args = parser.parse_args()
    if args.page_size < 0:
        print("--page-size must be 0 or greater", file=sys.stderr)
        return 2
    if args.page < 1:
        print("--page must be 1 or greater", file=sys.stderr)
        return 2

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

    package_list_args = ["pm", "list", "packages", "-i"] if args.include_system else ["pm", "list", "packages", "-3", "-i"]
    code, packages_out, packages_err = shell(args.adb, *package_list_args, timeout=60)
    if code != 0:
        package_scope = "all packages" if args.include_system else "third-party packages"
        print(f"\nFailed to list {package_scope}: {packages_err or packages_out}", file=sys.stderr)
        return code or 1

    packages = parse_packages_with_installers(packages_out)
    if not args.no_deep_source:
        for pkg in packages:
            code, source_out, _ = shell(args.adb, "cmd", "package", "get-install-source", pkg.package, timeout=15)
            source = parse_install_source(source_out) if code == 0 else ""
            if source:
                pkg.installer = source

    if not args.no_metadata:
        for pkg in packages:
            fill_package_metadata(args.adb, pkg)

    for pkg in packages:
        pkg.group, pkg.suggestion = classify(pkg.package, pkg.installer)

    sorted_packages = sorted(packages, key=lambda item: (item.group, item.suggestion, item.package))
    indexed_packages = list(enumerate(sorted_packages, start=1))
    total_rows = len(indexed_packages)
    if args.page_size and total_rows:
        total_pages = (total_rows + args.page_size - 1) // args.page_size
        if args.page > total_pages:
            print(f"--page is out of range. Total pages: {total_pages}", file=sys.stderr)
            return 2
        start_index = (args.page - 1) * args.page_size
        end_index = min(start_index + args.page_size, total_rows)
        indexed_packages = indexed_packages[start_index:end_index]
    else:
        total_pages = 1 if total_rows else 0
        start_index = 0
        end_index = total_rows

    section_title = "All Packages" if args.include_system else "Third-Party Packages"
    print(f"\n## {section_title}\n")
    package_scope = "all installed packages" if args.include_system else "third-party packages only"
    print(f"- Package scope: {package_scope}")
    print(f"- Package rows found: {total_rows}")
    if args.page_size and total_rows:
        print(f"- Page: {args.page}/{total_pages}, rows {start_index + 1}-{end_index} of {total_rows}")
        if args.page < total_pages:
            print(f"- Next page command: `python3 scripts/collect_android_inventory.py {'--include-system ' if args.include_system else ''}--page-size {args.page_size} --page {args.page + 1}`")
    print()

    rows = [["No.", "Group", "App name", "Installer", "First install", "Last update", "Package", "Suggestion"]]
    for index, pkg in indexed_packages:
        rows.append([
            str(index),
            pkg.group,
            pkg.app_name or "未读取到，以包名为准",
            pkg.installer or "未读取到",
            pkg.first_install_time or "未读取到",
            pkg.last_update_time or "未读取到",
            pkg.package,
            pkg.suggestion,
        ])
    empty_message = "No packages found." if args.include_system else "No third-party packages found."
    print(markdown_table(rows) if len(rows) > 1 else empty_message)

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
