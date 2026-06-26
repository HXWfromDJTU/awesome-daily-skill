# ADB Command Reference

Use these commands only after confirming the target phone and package names. Show the impact and recovery command before changing anything.

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
```

Windows PowerShell:

```powershell
adb shell dumpsys package <package> | findstr installer
```

## Unknown APK Install Permission

This should be done by the Agent with ADB where possible. Do not make the user manually tap settings unless the ADB command fails or the vendor blocks appops changes.

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
```

The first command is a dry run. The second command applies `REQUEST_INSTALL_PACKAGES ignore` to discovered install-route packages.

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
