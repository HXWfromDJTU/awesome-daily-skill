---
name: "android-spam-app-disable-and-uninstall"
description: "Use when helping a non-technical user clean a parent's Android phone via ADB: list installed apps, identify installer sources, group important and suspicious apps without hiding them, ask for confirmation, close APK installation permissions on browsers/app stores/file managers/quick apps, and only then handle clearly unwanted apps. Also usable by Codex or any other Agent that supports Skills."
---

# Android Spam App Disable And Uninstall

Help a non-technical user clean junk apps from a parent's Android phone with ADB. Keep the tone simple and family-friendly, list apps transparently, and always provide concrete commands for actions.

This Skill can be used by Codex or any other Agent that supports Skills, custom workflows, or GitHub-based Skill installation, such as Workbuddy, Qclaw, Claude, or Mavis-style agents.

## Safety Rules

- Do not root the phone.
- Do not flash firmware.
- Do not factory reset.
- Do not wipe photos, contacts, messages, WeChat data, or gallery data.
- Do not automatically delete, disable, hide, or change any app.
- Do not delete or disable phone, SMS, settings, launcher, system services, gallery, file manager, keyboard, WeChat, Alipay, banking, medical insurance, social security, or anti-fraud apps unless the user explicitly confirms after a risk explanation.
- Before uninstalling, disabling, hiding, or closing install routes, show the package names, exact commands, expected impact, and recovery commands.
- For app stores, browsers, file managers, downloaders, and quick-app services, do not present the app itself as a deletion target just because it can install APK files. First recommend only disabling its APK installation permission with `REQUEST_INSTALL_PACKAGES ignore`.
- In Chinese user-facing replies, call this action `禁用安装权限` or `禁止安装 APK`, not `删除`. If the user says `确认禁用`, interpret it as disabling APK installation permission unless they explicitly mention app-package disabling.
- For install-route packages, always show a numbered list and accept simple confirmations: `确认禁用全部` or `确认禁用 1,3,5`. Do not ask the user to separately fill `确认删除 / 确认停用 / 确认保留` for the install-route step.
- For junk-app deletion candidates, always show a numbered table before asking the user to choose. The table must prioritize the app's UI display name, then installer source, install time, package name, and the deletion recommendation.
- Do not omit apps from the review table just because they look important, common, official, financial, map-related, carrier-related, keyboard-related, or installed from an official app store. List them and put them in an `重要/谨慎` or `普通复核` group with a conservative recommendation instead of making the decision for the user.
- When the user chooses `选项 B`, says `继续删除垃圾应用`, or asks to list all apps, run a fresh full inventory with `scripts/collect_android_inventory.py --include-system`. Do not reuse earlier candidate lists, memory, screenshots, or only the apps mentioned by the user.
- In a full deletion review, report the total number of app rows found. If you paginate because the table is long, keep global numbering, show page status, and continue pages until every app has been shown or the user explicitly says a subset is enough.
- Do not accept `全部删除`, `全删`, or similar blanket deletion requests for app deletion. Explain that app deletion is riskier than closing install permissions, and ask the user to choose explicit item numbers such as `请删除 1、2、4`.
- Never delete apps immediately after the user's first numbered selection. First repeat the selected apps by number, UI name when available, package, command, and impact, then ask for a second confirmation. If the UI name is unavailable, write `未读取到，以包名为准`; do not ask the user to manually look up and retype the name. Execute only after the user replies `确认删除`.

## Bundled Resources

- Use `scripts/ensure_adb.py` to detect the Agent's current OS and install the matching official Android SDK Platform-Tools package when `adb` is missing.
- Use `scripts/collect_android_inventory.py` to collect a read-only inventory when Python is available. It prints numbered apps with group, app name, installer, install time, update time, package, and suggestion when the device exposes that metadata. Use `--include-system` when the user wants a complete review table that also includes important/system-looking apps. Use `--page-size <n> --page <n>` only for pagination; this keeps global numbering and prints the total row count.
- Use `scripts/block_install_routes.py` to generate or apply ADB commands that set install-route packages to `REQUEST_INSTALL_PACKAGES ignore`.
- Read `references/adb-command-reference.md` when you need exact command templates for uninstalling, disabling, restoring, appops, and verification.
- Read `references/vendor-package-candidates.md` when you need common package candidates for domestic Android vendors and third-party app stores.

`ensure_adb.py` only downloads official Platform-Tools into a user-scoped directory and does not modify PATH. `collect_android_inventory.py` is read-only. `block_install_routes.py` is dry-run by default and only modifies the phone when the user confirms and you pass `--apply`.

## Workflow

### 1. Ensure ADB For The Current System

Do not assume the user is on macOS. First detect the Agent runtime OS and use the matching official Google Platform-Tools package.

When Python is available, prefer:

```bash
python3 scripts/ensure_adb.py --dry-run
python3 scripts/ensure_adb.py
```

The script chooses:

| Agent OS | Official package |
|---|---|
| macOS / Darwin | `platform-tools-latest-darwin.zip` |
| Windows | `platform-tools-latest-windows.zip` |
| Linux | `platform-tools-latest-linux.zip` |

Rules:

- Download only from `https://dl.google.com/android/repository/`.
- Install into a user-scoped directory, by default `~/.codex/tools/android-platform-tools/`.
- Do not modify the user's system `PATH`.
- Verify with `adb version`.
- Use the resulting explicit `adb` path in later commands when needed.

If Python is unavailable, detect the OS manually before choosing the download URL:

```bash
uname -s
```

On Windows PowerShell:

```powershell
$PSVersionTable.OS
```

### 2. Confirm ADB Connection

Explain that this step only checks whether the computer can see the phone.

Run:

```bash
adb devices -l
```

If the device is `unauthorized`, tell the user to unlock the phone and tap "Allow debugging". If it is `offline`, ask the user to reconnect USB or reopen wireless debugging. If multiple devices are connected, stop and ask the user to keep only the target phone connected.

Collect model information:

```bash
adb shell getprop ro.product.manufacturer
adb shell getprop ro.product.brand
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.incremental
```

### 3. Collect App Inventory

Prefer the bundled script when Python is available:

```bash
python3 scripts/collect_android_inventory.py
```

For a complete review where the user does not want the Agent to hide important-looking apps, use:

```bash
python3 scripts/collect_android_inventory.py --include-system
```

This may produce a longer table. It is still read-only.

If the full table is too long for one response, paginate explicitly:

```bash
python3 scripts/collect_android_inventory.py --include-system --page-size 40 --page 1
python3 scripts/collect_android_inventory.py --include-system --page-size 40 --page 2
```

The Agent must say the total app count and page range from the script output. Do not call a partial page a complete review.

If Python is unavailable, run the core commands manually:

```bash
adb shell pm list packages -i
adb shell pm list packages -3 -i
adb shell pm list packages -d
adb shell pm list packages
```

For a specific package, inspect install source:

```bash
adb shell cmd package get-install-source <package>
```

If unsupported, fall back to:

```bash
adb shell dumpsys package <package> | grep installer
```

On Windows PowerShell, replace `grep` with `findstr`.

### 4. Classify Apps For The User

Present plain-language tables. You may split the result into groups, but keep one stable numbering sequence across all groups if the user may select items by number.

| Group | App clue | Package | Installer source | Recommendation |
|---|---|---|---|---|
| 重点复核 | cleaner / booster / free Wi-Fi / red packet / pop-up ads | package | unknown, browser, file manager, downloader, or third-party store | Confirm whether parent needs it; likely removable if unused |
| 安装入口 | browsers / app stores / file managers / quick apps | package | system or official source | First disable APK install permission, do not delete the app body by default |
| 重要/谨慎 | WeChat / Alipay / banking / insurance / maps / keyboard / carrier / phone / SMS / settings | package | any source | List it, but mark deletion as high-risk and default keep |
| 普通复核 | shopping / video / tools / official-store apps | package | official store or known source | Ask whether parent actually uses it |

Do not write user-facing text like:

```text
没有把微信、支付宝、输入法、运营商、银行/保险、地图、电话短信设置类放进删除候选。
```

Instead, list those apps in the table under `重要/谨慎` with a clear reason and recommendation. The Agent should inform, not decide silently.

Flag an app as suspicious when:

- The installer is empty, unknown, browser, file manager, downloader, chat app, third-party market, or APK sideload route.
- The name or package looks like cleaner, booster, Wi-Fi cracking/free Wi-Fi, red packet, earning money, short drama ads, quick game, quick app, or popup ads.
- It was supposedly deleted from the launcher but still appears as installed for user 0.

If the installer is the official app store, do not automatically trust it. Ask whether the parent actually needs the app.

### 5. Prepare The Install-Route Confirmation List

After the read-only inventory, prioritize future install routes before discussing app deletion. Present install-route packages as a numbered list.

Use this Chinese shape for ordinary users:

```text
建议先禁用这些 App 的“安装 APK 权限”。这不会删除 App，只是不让它们继续安装 APK。

1. com.android.browser - 系统浏览器不能安装 APK
2. com.android.chrome - Chrome 不能安装 APK
3. com.android.filemanager - 文件管理器不能安装 APK

你可以回复：
- 确认禁用全部
- 确认禁用 1,3,5
```

Rules for this step:

- `确认禁用全部` means run install-permission blocking for all numbered install-route packages.
- `确认禁用 1,3,5` means run install-permission blocking only for those item numbers.
- Do not mix this step with deletion, app-package disabling, hiding, or keep lists.
- If the parent is unsure, do not change that package.
- After this step, you may separately ask about clearly unwanted junk apps, but still require explicit confirmation before deletion or app-package disabling.

### 6. Close Future Install Routes With Agent Commands

Do not primarily tell the user to tap through phone settings. Let the Agent close install routes through ADB when possible.

First generate a dry-run plan:

```bash
python3 scripts/block_install_routes.py
```

Show the user the packages and commands it plans to run. Explain that this does not delete apps; it only blocks those apps from installing APK files.

If the user replies `确认禁用全部`, apply all numbered install-route packages:

```bash
python3 scripts/block_install_routes.py --apply
```

If the user replies with item numbers, for example `确认禁用 1,3,5`, apply only those numbers:

```bash
python3 scripts/block_install_routes.py --apply --select 1,3,5
```

For one-off manual command generation, use:

```bash
adb shell appops get <package> REQUEST_INSTALL_PACKAGES
adb shell appops set <package> REQUEST_INSTALL_PACKAGES ignore
```

Then verify:

```bash
adb shell appops get <package> REQUEST_INSTALL_PACKAGES
```

Expected result should include `ignore`.

Do not uninstall app stores, browsers, file managers, downloaders, or quick-app services only because they are install routes. Only after install permission is blocked, and only if the user explicitly says the parent does not need the app itself, consider app-package disabling:

```bash
adb shell am force-stop <package>
adb shell pm disable-user --user 0 <package>
```

If disable fails and the user explicitly confirms the risk, use current-user uninstall only as a last resort:

```bash
adb shell pm uninstall --user 0 <package>
```

If ADB cannot reliably change a vendor setting, provide a manual route as a fallback only:

- Settings > Apps > Special app access > Install unknown apps > turn off all unnecessary apps.
- Settings > App store > Settings > Auto update / Auto download > off.
- Settings > Browser > Download / Security settings > turn off APK auto install.
- Settings > Quick apps > Manage > disable service when available.

### 7. Present Full App Review As Numbered Tables

Only enter this step after install routes have been reviewed, or when the user explicitly asks to continue deleting junk apps.

When entering this step, first run a fresh complete inventory:

```bash
python3 scripts/collect_android_inventory.py --include-system
```

If the output is too long, use paginated full inventory:

```bash
python3 scripts/collect_android_inventory.py --include-system --page-size 40 --page 1
```

Rules for full review:

- Do not reuse the earlier candidate list from install-route review or a previous user message.
- Do not show only `重点复核` or only apps you already suspected.
- Do not title a partial hand-picked list as `第一轮复核表`.
- If paginated, title it as `全量应用清单第 1 批 / 共 N 批` and keep global numbers from the script.
- Show `共查询到 N 个 App/包` before the table.
- Do not invite deletion choices until all pages have been shown, unless the user explicitly says they only want to choose from the current page.

Do not show deletion candidates as a plain bullet list of package names. Do not hide important-looking apps. For ordinary users, package names are only supporting details. Always show numbered tables in Chinese:

```text
继续删除前，我重新查询了手机上的全量应用清单。
共查询到 103 个 App/包。下面是全量应用清单第 1 批 / 共 3 批（编号 1-40）。
这里不是让你全部删除，而是让你看清楚每个 App 的来源和建议。

| 编号 | 分组 | App 名称 | 安装来源 | 安装时间 | 包名 | 删除建议 |
|---|---|---|---|---|---|---|
| 1 | 重点复核 | LED 跑马灯 | com.bbk.appstore / vivo 应用商店 | 2026-06-18 10:20 | com.devfire.ledbanner | 非必要工具，问过机主不用后可删 |
| 2 | 重点复核 | 第三方天气 | unknown / 未读取到 | 2026-05-02 08:11 | com.zdbq.ljtq.ljweather | 非系统天气，若不用可删 |
| 3 | 重要/谨慎 | 微信 | com.tencent.mm / 安装来源见清单 | 2025-12-01 09:10 | com.tencent.mm | 常用通讯 App，默认保留；确认不用才处理 |
| 4 | 重要/谨慎 | 输入法 | com.bbk.appstore / vivo 应用商店 | 2025-10-03 12:30 | com.sohu.inputmethod.sogou.vivo | 可能影响打字，默认保留；确认不用才处理 |
| 5 | 普通复核 | 短视频 App | com.bbk.appstore / vivo 应用商店 | 2026-06-20 21:03 | com.kaixinkan.ugc.video.atom | 如果家人不用，可考虑删除 |

我会继续列出下一批，等全量清单都列完后，再让你选择要删除的编号。
```

After every page has been shown, ask for deletion choices:

```text
全量清单已经列完。你可以回复：请删除 1、2、4
不建议回复：全部删除
```

If the full table fits in one response:

```text
继续删除前，我重新查询了手机上的全量应用清单。
共查询到 103 个 App/包。下面是全部应用。

| 编号 | 分组 | App 名称 | 安装来源 | 安装时间 | 包名 | 删除建议 |
|---|---|---|---|---|---|---|
| 1 | 重点复核 | LED 跑马灯 | com.bbk.appstore / vivo 应用商店 | 2026-06-18 10:20 | com.devfire.ledbanner | 非必要工具，问过机主不用后可删 |
| 2 | 重点复核 | 第三方天气 | unknown / 未读取到 | 2026-05-02 08:11 | com.zdbq.ljtq.ljweather | 非系统天气，若不用可删 |
| 3 | 重要/谨慎 | 微信 | com.tencent.mm / 安装来源见清单 | 2025-12-01 09:10 | com.tencent.mm | 常用通讯 App，默认保留；确认不用才处理 |
| 4 | 重要/谨慎 | 输入法 | com.bbk.appstore / vivo 应用商店 | 2025-10-03 12:30 | com.sohu.inputmethod.sogou.vivo | 可能影响打字，默认保留；确认不用才处理 |
| 5 | 普通复核 | 短视频 App | com.bbk.appstore / vivo 应用商店 | 2026-06-20 21:03 | com.kaixinkan.ugc.video.atom | 如果家人不用，可考虑删除 |

你可以回复：请删除 1、2、4
不建议回复：全部删除
```

Table rules:

- `编号`: stable item number for this deletion-candidate round.
- `分组`: use `重点复核`, `安装入口`, `重要/谨慎`, or `普通复核`.
- `App 名称`: put the app's UI display name first. If ADB cannot read it, write `未读取到，以包名为准`. Do not require the user to open phone settings and retype the visible name just because ADB did not expose it.
- `安装来源`: show the raw installer package and a plain-language explanation when known, for example `com.bbk.appstore / vivo 应用商店`, `com.android.browser / 浏览器下载`, or `unknown / 未读取到`.
- `安装时间`: use `firstInstallTime` from `dumpsys package` when available. If unavailable, write `未读取到`.
- `包名`: show the package name, but do not make it the first thing ordinary users see.
- `删除建议`: use plain language such as `建议问爸妈`, `确认不用可删`, `不建议删除`, or `高风险广告类，建议删除前再确认`.

Selection rules:

- Accept `请删除 1、2、4`, `删除 1,2,4`, or similar explicit number selections.
- If the user says `全部删除`, `全删`, or gives no numbers, do not continue. Reply that app deletion should not be done in bulk and ask for explicit item numbers.
- If a selected app name is unavailable, still continue to the second-confirmation list using the original number, package name, installer source, install time, and deletion command.
- If the user selects an `重要/谨慎` item, do not refuse or silently remove it from the selection. Include a stronger risk note in the second-confirmation list, then let the user decide with `确认删除`.

### 8. Second Confirm And Delete Confirmed Apps

After the user gives deletion numbers, do not execute commands yet. First produce a second-confirmation message:

```text
我还不会马上删除。请你二次确认是否删除下面这几个 App：

1. 编号 6 - Netflix 相关 App
   App 名称：未读取到，以包名为准
   包名：com.netflixgc.app
   安装来源：com.android.packageinstaller / APK 安装器
   安装时间：未读取到
   将执行：adb uninstall com.netflixgc.app

2. 编号 8 - vivo 浏览器小说组件
   App 名称：未读取到，以包名为准
   包名：com.vivo.browser.novel.widget
   安装来源：com.bbk.appstore / vivo 应用商店
   安装时间：未读取到
   将执行：adb uninstall com.vivo.browser.novel.widget

如果确认删除，请回复：确认删除
如果不确定，请回复：先不删
```

If the user selected an `重要/谨慎` item, keep it in the confirmation list and add a risk note:

```text
3. 编号 4 - 输入法
   包名：com.sohu.inputmethod.sogou.vivo
   安装来源：com.bbk.appstore / vivo 应用商店
   安装时间：2025-10-03 12:30
   风险提醒：删除后可能影响打字。确认家人不用这个输入法后再删。
   将执行：adb uninstall com.sohu.inputmethod.sogou.vivo

如果确认删除，请回复：确认删除
如果不确定，请回复：先不删
```

If app names are available, include them directly:

```text
我还不会马上删除。请你二次确认是否删除下面这几个 App：

1. 编号 1 - LED 跑马灯
   包名：com.devfire.ledbanner
   安装来源：com.bbk.appstore / vivo 应用商店
   安装时间：2026-06-18 10:20
   将执行：adb uninstall com.devfire.ledbanner

2. 编号 3 - 临时邮箱
   包名：com.temporary.email.pro
   安装来源：com.android.browser / 浏览器下载
   安装时间：2026-06-20 21:03
   将执行：adb uninstall com.temporary.email.pro

如果确认删除，请回复：确认删除
如果不确定，请回复：先不删
```

Only after the second confirmation, execute deletion commands.

Use the command patterns in `references/adb-command-reference.md`.

For ordinary user-installed apps:

```bash
adb uninstall <package>
```

For preinstalled apps that should be removed only from the current user:

```bash
adb shell pm uninstall --user 0 <package>
```

For temporary disabling:

```bash
adb shell pm disable-user --user 0 <package>
```

Always include recovery commands:

```bash
adb shell cmd package install-existing --user 0 <package>
adb shell pm enable <package>
```

After every action, verify:

```bash
adb shell pm list packages --user 0 | grep <package>
```

On Windows PowerShell:

```powershell
adb shell pm list packages --user 0 | findstr <package>
```

### 9. Ask Whether To Continue Or Finish

Do not tell the user to close wireless debugging, USB debugging, or Developer options immediately after closing install routes if there are still possible ADB cleanup steps. Closing debugging ends the Agent's ability to continue uninstalling or disabling unwanted apps.

After an install-route step, summarize what was changed and present these choices in Chinese:

```text
选项 A：好的，我已完成我的工作，现在就去关闭无线调试、USB 调试和开发者选项，然后重启手机。
选项 B：好的，继续进入删除垃圾应用。
```

If the user chooses option A, or clearly says the cleanup is finished, then tell the user to close:

- Wireless debugging.
- USB debugging.
- Developer options.

Then ask the user to reboot the phone once.

If the user chooses option B, keep ADB available and continue with confirmed junk-app deletion or app-package disabling. Do not mention closing debugging again until there are no remaining ADB actions or the user chooses to finish.

When the user chooses option B, go to the full app review step and run:

```bash
python3 scripts/collect_android_inventory.py --include-system
```

Do not answer option B with only a curated short candidate table.

End with a concise summary:

- Apps removed.
- Apps disabled.
- Apps removed for current user.
- Install routes closed.
- Manual settings still needing review.
- Apps intentionally kept.
- Recovery commands for each changed package.
