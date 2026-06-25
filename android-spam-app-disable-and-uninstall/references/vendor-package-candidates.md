# Vendor Package Candidates

These are candidates, not guaranteed package names. Always check that a package exists before generating a command.

## Search Commands

Mac / Linux:

```bash
adb shell pm list packages | grep -Ei "market|appstore|store|browser|file|installer|quick|fast|game|assistant|download"
adb shell pm list packages | grep -Ei "qqdownloader|appsearch|wandoujia|qihoo|baidu|sogou"
```

Windows PowerShell:

```powershell
adb shell pm list packages | findstr /i "market appstore store browser file installer quick fast game assistant download"
adb shell pm list packages | findstr /i "qqdownloader appsearch wandoujia qihoo baidu sogou"
```

## Domestic Vendor Candidates

| Vendor / System | Route | Package candidates |
|---|---|---|
| Huawei / HarmonyOS | AppGallery | `com.huawei.appmarket` |
| Huawei / HarmonyOS | Quick apps | `com.huawei.fastapp`, `com.huawei.fastappengine` |
| Huawei / HarmonyOS | Browser | `com.huawei.browser` |
| Honor / MagicOS | App market | `com.hihonor.appmarket` |
| Honor / MagicOS | Quick apps | `com.hihonor.fastapp`, `com.hihonor.fastappengine` |
| Xiaomi / Redmi / HyperOS / MIUI | App store | `com.xiaomi.market` |
| Xiaomi / Redmi / HyperOS / MIUI | Quick app / hybrid service | `com.miui.hybrid`, `com.miui.hybrid.accessory` |
| Xiaomi / Redmi / HyperOS / MIUI | Browser | `com.android.browser`, `com.mi.globalbrowser` |
| OPPO / OnePlus / realme | App market | `com.heytap.market`, `com.oppo.market` |
| OPPO / OnePlus / realme | Game center | `com.nearme.gamecenter`, `com.heytap.game` |
| OPPO / OnePlus / realme | Browser | `com.heytap.browser`, `com.android.browser` |
| OPPO / OnePlus / realme | Quick apps | `com.nearme.instant.platform`, `com.heytap.quickgame` |
| vivo / iQOO | App store | `com.bbk.appstore` |
| vivo / iQOO | Game center | `com.vivo.game`, `com.vivo.gamecenter` |
| vivo / iQOO | Browser | `com.vivo.browser` |
| vivo / iQOO | Quick apps | `com.vivo.hybrid`, `com.vivo.quickapp` |
| Meizu | App store / services | Search for `meizu`, `mstore`, `flyme` |
| Lenovo / Moto China | App store / services | Search for `lenovo`, `moto`, `leos` |
| ZTE / nubia | App store / services | Search for `zte`, `nubia`, `market`, `store` |

## Third-Party App Stores

| App store | Package candidates |
|---|---|
| Tencent MyApp | `com.tencent.android.qqdownloader` |
| Baidu Mobile Assistant / search download route | `com.baidu.appsearch`, `com.baidu.searchbox` |
| 360 Mobile Assistant | `com.qihoo.appstore` |
| Wandoujia | `com.wandoujia.phoenix2` |
| Sogou search / download route | Search for `sogou` |

## Example Vendor Commands

Huawei / HarmonyOS:

```bash
adb shell pm list packages | grep -E "com.huawei.appmarket|com.huawei.fastapp|com.huawei.fastappengine|com.huawei.browser"
adb shell am force-stop com.huawei.appmarket
adb shell appops set com.huawei.browser REQUEST_INSTALL_PACKAGES ignore
adb shell pm disable-user --user 0 com.huawei.appmarket
adb shell pm disable-user --user 0 com.huawei.fastapp
```

Honor / MagicOS:

```bash
adb shell pm list packages | grep -E "com.hihonor.appmarket|com.hihonor.fastapp|com.hihonor.fastappengine"
adb shell am force-stop com.hihonor.appmarket
adb shell pm disable-user --user 0 com.hihonor.appmarket
adb shell pm disable-user --user 0 com.hihonor.fastapp
```

Xiaomi / Redmi / HyperOS / MIUI:

```bash
adb shell pm list packages | grep -E "com.xiaomi.market|com.miui.hybrid|com.miui.hybrid.accessory|com.android.browser|com.mi.globalbrowser"
adb shell am force-stop com.xiaomi.market
adb shell appops set com.android.browser REQUEST_INSTALL_PACKAGES ignore
adb shell pm disable-user --user 0 com.xiaomi.market
adb shell pm disable-user --user 0 com.miui.hybrid
```

OPPO / OnePlus / realme:

```bash
adb shell pm list packages | grep -E "com.heytap.market|com.oppo.market|com.nearme.instant.platform|com.heytap.browser|com.android.browser"
adb shell am force-stop com.heytap.market
adb shell appops set com.heytap.browser REQUEST_INSTALL_PACKAGES ignore
adb shell pm disable-user --user 0 com.heytap.market
adb shell pm disable-user --user 0 com.nearme.instant.platform
```

vivo / iQOO:

```bash
adb shell pm list packages | grep -E "com.bbk.appstore|com.vivo.browser|com.vivo.hybrid|com.vivo.quickapp"
adb shell am force-stop com.bbk.appstore
adb shell appops set com.vivo.browser REQUEST_INSTALL_PACKAGES ignore
adb shell pm disable-user --user 0 com.bbk.appstore
adb shell pm disable-user --user 0 com.vivo.hybrid
```
