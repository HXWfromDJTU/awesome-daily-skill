---
name: "android-spam-app-disable-and-uninstall"
description: "Use when helping a non-technical user clean a parent's Android phone via ADB: list non-system apps, identify installer sources, flag suspicious app installers, ask for confirmation, then uninstall, disable, hide app stores, or close APK installation routes with explicit ADB commands. Also usable by Codex or any other Agent that supports Skills."
---

# Android Spam App Disable And Uninstall

Help a non-technical user clean junk apps from a parent's Android phone with ADB. Keep the tone simple and family-friendly, but always provide concrete commands for actions.

This Skill can be used by Codex or any other Agent that supports Skills, custom workflows, or GitHub-based Skill installation, such as Workbuddy, Qclaw, Claude, or Mavis-style agents.

## Safety Rules

- Do not root the phone.
- Do not flash firmware.
- Do not factory reset.
- Do not wipe photos, contacts, messages, WeChat data, or gallery data.
- Do not automatically delete any app.
- Do not delete or disable phone, SMS, settings, launcher, system services, gallery, file manager, keyboard, WeChat, Alipay, banking, medical insurance, social security, or anti-fraud apps unless the user explicitly confirms after a risk explanation.
- Before uninstalling, disabling, hiding, or closing install routes, show the package names, exact commands, expected impact, and recovery commands.
- For app stores, browsers, file managers, downloaders, and quick-app services, first close install permissions when possible. Disable or current-user-uninstall only after the user confirms that the parent does not need to install apps independently.

## Bundled Resources

- Use `scripts/collect_android_inventory.py` to collect a read-only inventory when Python is available.
- Use `scripts/block_install_routes.py` to generate or apply ADB commands that set install-route packages to `REQUEST_INSTALL_PACKAGES ignore`.
- Read `references/adb-command-reference.md` when you need exact command templates for uninstalling, disabling, restoring, appops, and verification.
- Read `references/vendor-package-candidates.md` when you need common package candidates for domestic Android vendors and third-party app stores.

`collect_android_inventory.py` is read-only. `block_install_routes.py` is dry-run by default and only modifies the phone when the user confirms and you pass `--apply`.

## Workflow

### 1. Confirm ADB Connection

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

### 2. Collect App Inventory

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

### 3. Classify Apps For The User

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

### 4. Prepare A Confirmation List

Pause before making changes. Ask the user to reply in this shape:

```text
确认删除：
1. App name - package

确认停用 / 隐藏：
1. App store or quick-app service - package

确认保留：
1. App name - package
```

If the parent is unsure, keep the app.

### 5. Generate Commands For Confirmed Apps

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

### 6. Close Future Install Routes With Agent Commands

Do not primarily tell the user to tap through phone settings. Let the Agent close install routes through ADB when possible.

First generate a dry-run plan:

```bash
python3 scripts/block_install_routes.py
```

Show the user the packages and commands it plans to run. Explain that this does not delete apps; it only blocks those apps from installing APK files.

After the user confirms, apply it:

```bash
python3 scripts/block_install_routes.py --apply
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

Only after the install permission is blocked, handle confirmed unwanted app stores or quick-app services:

```bash
adb shell am force-stop <package>
adb shell pm disable-user --user 0 <package>
```

If disable fails and the user confirms, use current-user uninstall:

```bash
adb shell pm uninstall --user 0 <package>
```

If ADB cannot reliably change a vendor setting, provide a manual route as a fallback only:

- Settings > Apps > Special app access > Install unknown apps > turn off all unnecessary apps.
- Settings > App store > Settings > Auto update / Auto download > off.
- Settings > Browser > Download / Security settings > turn off APK auto install.
- Settings > Quick apps > Manage > disable service when available.

### 7. Finish Safely

Tell the user to close:

- Wireless debugging.
- USB debugging.
- Developer options.

Then ask the user to reboot the phone once.

End with a concise summary:

- Apps removed.
- Apps disabled.
- Apps removed for current user.
- Install routes closed.
- Manual settings still needing review.
- Apps intentionally kept.
- Recovery commands for each changed package.
