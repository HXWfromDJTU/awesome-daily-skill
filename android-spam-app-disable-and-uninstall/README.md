# android-spam-app-disable-and-uninstall

这是一个面向普通家庭场景的安卓手机清理 Skill。它适合用来帮父母检查手机里反复出现的“清理大师”“免费 Wi-Fi”“红包赚钱”“手机加速”“弹窗广告”等垃圾软件。

它的重点不是一键删除，而是：

1. 通过 ADB 列出非系统 App。
2. 标出每个 App 的安装来源。
3. 高亮来路不明、浏览器下载、文件管理器安装、第三方市场安装的 App。
4. 先把“未来安装入口”列成带序号的清单，让用户确认禁用哪些安装权限。
5. 对浏览器、应用商店、文件管理器、快应用这类入口，默认只禁用 APK 安装权限，不引导删除 App 本体。
6. 再处理家人明确确认不要的垃圾 App。
7. 只有在用户选择“完成清理”时，才引导关闭 USB 调试、无线调试和开发者选项；如果用户要继续删除垃圾 App，就保持 ADB 可用。

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

- 父母的安卓手机。
- 一台电脑。
- 官方 ADB 工具，也就是 Android SDK Platform-Tools。
- 手机和电脑连接同一个 Wi-Fi，或用 USB 数据线连接。

官方 ADB 下载页：

https://developer.android.com/tools/releases/platform-tools

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

禁用安装入口后，不要默认提示用户马上关闭 USB 调试、无线调试和开发者选项。应先让用户选择：

```text
选项 A：好的，我已完成我的工作，现在就去关闭无线调试、USB 调试和开发者选项，然后重启手机。
选项 B：好的，继续进入删除垃圾应用。
```

内置脚本：

- `scripts/collect_android_inventory.py`：只读盘点，不会删除、停用或修改手机里的任何 App。
- `scripts/block_install_routes.py`：默认 dry-run，只列出将关闭的安装入口；用户确认后加 `--apply`，才会执行 `adb shell appops set <包名> REQUEST_INSTALL_PACKAGES ignore`。支持 `--select 1,3,5` 只禁用用户确认的编号。
