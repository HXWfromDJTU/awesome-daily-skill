---
name: "android-spam-app-disable-and-uninstall"
description: "Use when helping a non-technical user clean a parent's Android phone via ADB: list non-system apps, identify installer sources, flag suspicious app installers, ask for confirmation, close APK installation permissions on browsers/app stores/file managers/quick apps, and only then handle clearly unwanted apps. Also usable by Codex or any other Agent that supports Skills."
---

# Android Spam App Disable And Uninstall

Help a non-technical user clean junk apps from a parent's Android phone with ADB. Keep the tone simple and family-friendly, but always provide concrete commands for actions.

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

## Bundled Resources

- Use `scripts/ensure_adb.py` to detect the Agent's current OS and install the matching official Android SDK Platform-Tools package when `adb` is missing.
- Use `scripts/collect_android_inventory.py` to collect a read-only inventory when Python is available.
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

If Python is unavailable, run the core commands manually:

```bash
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

Present a plain-language table:

| Suggestion | App clue | Package | Installer source | Why |
|---|---|---|---|---|
| Keep | WeChat / Alipay / banking | package | official store or known source | Parent likely needs it |
| Ask parent | Maps / shopping / video | package | official store | May be useful |
| High-risk removable | cleaner / booster / free Wi-Fi / red packet / pop-up ads | package | unknown, browser, file manager, downloader, or third-party store | Common adware pattern |
| Do not touch yet | keyboard / phone / SMS / system settings | package | system or protected source | Could affect normal phone use |

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

### 6. Generate Commands For Confirmed Junk Apps

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

### 7. Close Future Install Routes With Agent Commands

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

### 8. Ask Whether To Continue Or Finish

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

End with a concise summary:

- Apps removed.
- Apps disabled.
- Apps removed for current user.
- Install routes closed.
- Manual settings still needing review.
- Apps intentionally kept.
- Recovery commands for each changed package.
