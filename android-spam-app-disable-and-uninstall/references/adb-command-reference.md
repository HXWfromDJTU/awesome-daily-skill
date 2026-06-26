# ADB Command Reference

Use these commands only after confirming the target phone and package names. Show the impact and recovery command before changing anything.

## Ensure ADB

First identify the Agent runtime OS. Do not assume macOS.

Preferred helper:

```bash
python3 scripts/ensure_adb.py --dry-run
python3 scripts/ensure_adb.py
```

Manual OS checks:

```bash
uname -s
```

Windows PowerShell:

```powershell
$PSVersionTable.OS
```

Official Google Platform-Tools packages:

| OS | URL |
|---|---|
| macOS / Darwin | `https://dl.google.com/android/repository/platform-tools-latest-darwin.zip` |
| Windows | `https://dl.google.com/android/repository/platform-tools-latest-windows.zip` |
| Linux | `https://dl.google.com/android/repository/platform-tools-latest-linux.zip` |

Install into a user-scoped directory such as `~/.codex/tools/android-platform-tools/`. Do not modify PATH automatically. Verify with:

```bash
adb version
```

## Connection

```bash
adb devices -l
adb shell getprop ro.product.manufacturer
adb shell getprop ro.product.brand
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.incremental
```

## Inventory

```bash
adb shell pm list packages -3 -i
adb shell pm list packages -d
adb shell pm list packages
adb shell cmd package get-install-source <package>
adb shell dumpsys package <package> | grep installer
adb shell dumpsys package <package> | grep firstInstallTime
adb shell dumpsys package <package> | grep lastUpdateTime
```

Windows PowerShell:

```powershell
adb shell dumpsys package <package> | findstr installer
adb shell dumpsys package <package> | findstr firstInstallTime
adb shell dumpsys package <package> | findstr lastUpdateTime
```

Preferred helper:

```bash
python3 scripts/collect_android_inventory.py
```

The helper is read-only and prints third-party apps with numbered rows, app name when available, installer, install time, update time, package, and suggestion.

## Deletion Candidate Confirmation

Before deleting any app, show a numbered table:

```text
| 编号 | App 名称 | 安装来源 | 安装时间 | 包名 | 删除建议 |
|---|---|---|---|---|---|
| 1 | LED 跑马灯 | com.bbk.appstore / vivo 应用商店 | 2026-06-18 10:20 | com.devfire.ledbanner | 非必要工具，确认不用后可删 |
```

Ask the user to choose explicit numbers:

```text
请删除 1、2、4
```

Do not accept blanket deletion requests such as:

```text
全部删除
全删
```

After the user chooses numbers, do not execute yet. Repeat the selected apps and commands, then ask for a second confirmation:

```text
我还不会马上删除。请你二次确认是否删除下面这几个 App：

1. LED 跑马灯
   包名：com.devfire.ledbanner
   安装来源：com.bbk.appstore / vivo 应用商店
   安装时间：2026-06-18 10:20
   将执行：adb uninstall com.devfire.ledbanner

如果确认删除以上 1 个 App，请回复：确认删除以上 1 个 App
```

## Unknown APK Install Permission

This should be done by the Agent with ADB where possible. Do not make the user manually tap settings unless the ADB command fails or the vendor blocks appops changes.

For browsers, app stores, file managers, downloaders, and quick-app services, do not recommend deleting the app itself just because it is an install route. First disable only APK installation permission.

Check:

```bash
adb shell appops get <package> REQUEST_INSTALL_PACKAGES
```

Block:

```bash
adb shell appops set <package> REQUEST_INSTALL_PACKAGES ignore
```

Restore default:

```bash
adb shell appops set <package> REQUEST_INSTALL_PACKAGES default
```

Batch helper:

```bash
python3 scripts/block_install_routes.py
python3 scripts/block_install_routes.py --apply
python3 scripts/block_install_routes.py --apply --select 1,3,5
```

The first command is a dry run and prints numbered install-route packages. The second command applies `REQUEST_INSTALL_PACKAGES ignore` to all discovered install-route packages. The third command applies only selected item numbers.

User-facing confirmation wording:

```text
确认禁用全部
确认禁用 1,3,5
```

In this context, `禁用` means disabling APK installation permission, not uninstalling or disabling the app package.

If the command is unsupported or ineffective, provide manual settings:

- Settings > Apps > Special app access > Install unknown apps.
- Settings > Security > More security settings > Install unknown apps.

## Stop, Disable, Hide, Or Remove

Force stop only:

```bash
adb shell am force-stop <package>
```

Disable for current user:

```bash
adb shell pm disable-user --user 0 <package>
```

Current-user uninstall:

```bash
adb shell pm uninstall --user 0 <package>
```

Current-user uninstall while keeping data:

```bash
adb shell pm uninstall -k --user 0 <package>
```

Ordinary user app uninstall:

```bash
adb uninstall <package>
```

## Recovery

Restore a package removed only from current user:

```bash
adb shell cmd package install-existing --user 0 <package>
```

Re-enable a disabled package:

```bash
adb shell pm enable <package>
```

Restore install permission default:

```bash
adb shell appops set <package> REQUEST_INSTALL_PACKAGES default
```

## Verification

Check package still installed for current user:

```bash
adb shell pm list packages --user 0 | grep <package>
```

Windows PowerShell:

```powershell
adb shell pm list packages --user 0 | findstr <package>
```

Check disabled packages:

```bash
adb shell pm list packages -d | grep <package>
```

Windows PowerShell:

```powershell
adb shell pm list packages -d | findstr <package>
```

## Third-Party App Store Examples

Only run commands for packages that were found on the phone.

For app stores that are install routes, first block APK installation permission:

```bash
adb shell appops set com.tencent.android.qqdownloader REQUEST_INSTALL_PACKAGES ignore
adb shell appops set com.baidu.appsearch REQUEST_INSTALL_PACKAGES ignore
adb shell appops set com.qihoo.appstore REQUEST_INSTALL_PACKAGES ignore
adb shell appops set com.wandoujia.phoenix2 REQUEST_INSTALL_PACKAGES ignore
```

Only uninstall a third-party app store if the user explicitly confirms that the parent does not need that app itself:

```bash
adb uninstall com.tencent.android.qqdownloader
adb uninstall com.baidu.appsearch
adb uninstall com.qihoo.appstore
adb uninstall com.wandoujia.phoenix2
```

If ordinary uninstall fails:

```bash
adb shell pm uninstall --user 0 <third-party-store-package>
```
