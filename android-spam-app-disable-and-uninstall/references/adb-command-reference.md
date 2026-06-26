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
python3 scripts/collect_android_inventory.py --include-system
python3 scripts/collect_android_inventory.py --include-system --page-size 40 --page 1
```

The helper is read-only. The default command prints third-party apps. `--include-system` prints a broader table that also includes system/important-looking apps so the Agent does not silently omit WeChat, Alipay, keyboards, carrier apps, banking/insurance apps, maps, phone, SMS, settings, and similar packages. `--page-size` and `--page` may be used only for pagination; the script keeps global numbering and prints the total row count.

When the user chooses `选项 B`, says `继续删除垃圾应用`, or asks to list all apps, run a fresh full query:

```bash
python3 scripts/collect_android_inventory.py --include-system
```

Do not answer from a previous short candidate list. Do not show only the known suspicious apps. If the table is too long, paginate and report every page until the complete list has been shown or the user explicitly says the current subset is enough.

## Deletion Candidate Confirmation

Before deleting any app, show a numbered review table from the fresh full inventory. Do not hide important-looking apps; put them in a conservative group instead.

```text
继续删除前，我重新查询了手机上的全量应用清单。
共查询到 103 个 App/包。下面是全量应用清单第 1 批 / 共 3 批（编号 1-40）。

| 编号 | 分组 | App 名称 | 安装来源 | 安装时间 | 包名 | 删除建议 |
|---|---|---|---|---|---|---|
| 1 | 重点复核 | LED 跑马灯 | com.bbk.appstore / vivo 应用商店 | 2026-06-18 10:20 | com.devfire.ledbanner | 非必要工具，确认不用后可删 |
| 2 | 重要/谨慎 | 输入法 | com.bbk.appstore / vivo 应用商店 | 2025-10-03 12:30 | com.sohu.inputmethod.sogou.vivo | 可能影响打字，默认保留，确认不用才处理 |
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

1. 编号 1 - LED 跑马灯
   包名：com.devfire.ledbanner
   安装来源：com.bbk.appstore / vivo 应用商店
   安装时间：2026-06-18 10:20
   将执行：adb uninstall com.devfire.ledbanner

如果确认删除，请回复：确认删除
```

If ADB cannot read the UI display name, do not block on manual name lookup. Keep the original selected number and package details:

```text
1. 编号 8 - App 名称未读取到，以包名为准
   包名：com.vivo.browser.novel.widget
   安装来源：com.bbk.appstore / vivo 应用商店
   安装时间：未读取到
   将执行：adb uninstall com.vivo.browser.novel.widget

如果确认删除，请回复：确认删除
```

For an important/cautious item, do not drop it from the user's selection and do not ask the user to manually retype app names. Keep it selected but add a risk note in the same second confirmation:

```text
2. 编号 2 - 输入法
   包名：com.sohu.inputmethod.sogou.vivo
   安装来源：com.bbk.appstore / vivo 应用商店
   安装时间：2025-10-03 12:30
   风险提醒：删除后可能影响打字。确认家人不用这个输入法后再删。
   将执行：adb uninstall com.sohu.inputmethod.sogou.vivo

如果确认删除，请回复：确认删除
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
