# android-spam-app-disable-and-uninstall

这是一个面向普通家庭场景的安卓手机清理 Skill。它适合用来帮老人家检查手机里反复出现的“清理大师”“免费 Wi-Fi”“红包赚钱”“手机加速”“弹窗广告”等垃圾软件。

它的重点不是一键删除，而是：

1. 通过 ADB 列出 App；需要完整复核时，也列出系统/重要类 App。
2. 标出每个 App 的安装来源。
3. 高亮来路不明、浏览器下载、文件管理器安装、第三方市场安装的 App。
4. 先把“未来安装入口”列成带序号的清单，让用户确认禁用哪些安装权限。
5. 对浏览器、应用商店、文件管理器、快应用这类入口，默认只禁用 APK 安装权限，不引导删除 App 本体。
6. 再处理家人明确确认不要的垃圾 App。
7. 清理过程中保持 ADB 调试可用，全部结束后再关闭 USB 调试、无线调试和开发者选项。

## 适用 Agent

Codex 可以使用这个 Skill。其他任意支持 Skill / 自定义工作流 / 从 GitHub 仓库安装能力的 Agent 也可以使用，比如 Workbuddy、Qclaw、Claude、马维斯等。

## 推荐安装方式

这个 Skill 在仓库中的目录地址：

```text
https://github.com/HXWfromDJTU/awesome-daily-skill/tree/main/android-spam-app-disable-and-uninstall
```

直接对 Agent 说：

```text
请从 GitHub 仓库 https://github.com/HXWfromDJTU/awesome-daily-skill 安装 android-spam-app-disable-and-uninstall 这个 Skill。
安装后，使用这个 Skill 帮我清理爸妈安卓手机里的垃圾软件。
```

如果 Agent 需要文件路径：

```text
Skill 目录：android-spam-app-disable-and-uninstall
正式内容文件：SKILL.md
```

## 需要提前准备

- 老人家的安卓手机。
- 一台电脑。
- 官方 ADB 工具，也就是 Android SDK Platform-Tools。Agent 可以自动识别当前系统并下载对应版本。
- 手机和电脑连接同一个 Wi-Fi，或用 USB 数据线连接。

官方 ADB 下载页：

https://developer.android.com/tools/releases/platform-tools

Agent 自动下载时会先识别系统：

| 当前系统 | 下载包 |
|---|---|
| macOS | `platform-tools-latest-darwin.zip` |
| Windows | `platform-tools-latest-windows.zip` |
| Linux | `platform-tools-latest-linux.zip` |

默认下载到 `~/.codex/tools/android-platform-tools/`，不修改系统 PATH。

## 重要提醒

这个 Skill 包含删除、停用和关闭安装入口命令，但不会要求 Agent 自动执行。Agent 必须先给出清单、命令和影响说明，得到用户确认后再执行。

对安装入口的默认交互是：

```text
1. com.android.browser - 系统浏览器不能安装 APK
2. com.android.chrome - Chrome 不能安装 APK
3. com.android.filemanager - 文件管理器不能安装 APK

你可以回复：
- 确认禁用全部
- 确认禁用 1,3,5
```

这里的“禁用”指禁用 APK 安装权限，也就是执行 `REQUEST_INSTALL_PACKAGES ignore`，不是删除浏览器、应用商店或文件管理器本体。

对 App 删除复核的默认交互是完整列举，而不是替用户省略“看起来安全”的 App。微信、支付宝、输入法、运营商、银行/保险、地图等也可以列出来，但要标在 `重要/谨慎` 分组里，并说明默认保留、确认不用才处理。

完整复核可让 Agent 使用：

```bash
python3 scripts/collect_android_inventory.py --include-system
```

如果清单太长，可以分页，但必须说明总数、当前批次，并保持全局编号：

```bash
python3 scripts/collect_android_inventory.py --include-system --page-size 40 --page 1
python3 scripts/collect_android_inventory.py --include-system --page-size 40 --page 2
```

用户选择 `选项 B` 或要求“全部列出来”时，Agent 必须重新执行全量清单查询，不能只展示前面提到过的候选 App，也不能把少量候选称为“第一轮复核表”。如果分页，需要把每一批都列完，或者用户明确说“只看当前这批就够了”，再让用户选删除编号。

默认交互是：

```text
继续删除前，我重新查询了手机上的全量应用清单。
共查询到 103 个 App/包。下面是全部应用。

| 编号 | 分组 | App 名称 | 安装来源 | 安装时间 | 包名 | 删除建议 |
|---|---|---|---|---|---|---|
| 1 | 重点复核 | LED 跑马灯 | vivo 应用商店 | 2026-06-18 10:20 | com.devfire.ledbanner | 非必要工具，确认不用后可删 |
| 2 | 重要/谨慎 | 输入法 | vivo 应用商店 | 2025-10-03 12:30 | com.sohu.inputmethod.sogou.vivo | 可能影响打字，默认保留，确认不用才处理 |

你可以回复：请删除 1、2
```

不建议、也不默认接受“全部删除”。用户第一次用编号选择后，Agent 还必须把选中的 App 序号、名称、包名、安装来源、安装时间和将执行的命令再复述一遍，等用户二次确认后才允许删除。

如果 ADB 没有读到 App 显示名，Agent 直接写 `未读取到，以包名为准`，不要让普通用户再去手机设置里核对并手动输入名称。二次确认时用户回复：

```text
确认删除
```

即可开始执行删除命令。

内置脚本：

- `scripts/ensure_adb.py`：识别当前系统，缺少 ADB 时从 Google 官方地址下载对应版本的 Platform-Tools，并用 `adb version` 验证。
- `scripts/collect_android_inventory.py`：只读盘点，会尽量列出 App 分组、显示名、安装来源、安装时间、更新时间、包名和建议，不会删除、停用或修改手机里的任何 App。加 `--include-system` 时会把系统/重要类 App 也放进复核表；加 `--page-size` 和 `--page` 可以分页展示全量清单。
- `scripts/block_install_routes.py`：默认 dry-run，只列出将关闭的安装入口；用户确认后加 `--apply`，才会执行 `adb shell appops set <包名> REQUEST_INSTALL_PACKAGES ignore`。支持 `--select 1,3,5` 只禁用用户确认的编号。
