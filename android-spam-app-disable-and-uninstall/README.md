# android-spam-app-disable-and-uninstall

这是一个面向普通家庭场景的安卓手机清理 Skill。它适合用来帮父母检查手机里反复出现的“清理大师”“免费 Wi-Fi”“红包赚钱”“手机加速”“弹窗广告”等垃圾软件。

它的重点不是一键删除，而是：

1. 通过 ADB 列出非系统 App。
2. 标出每个 App 的安装来源。
3. 高亮来路不明、浏览器下载、文件管理器安装、第三方市场安装的 App。
4. 让用户和家人确认哪些要删、哪些要留。
5. 再执行删除、当前用户移除、停用，或通过 ADB 直接关闭安装入口。
6. 收尾时关闭 USB 调试、无线调试和开发者选项。

## 适用 Agent

Codex 可以使用这个 Skill。其他任意支持 Skill / 自定义工作流 / 从 GitHub 仓库安装能力的 Agent 也可以使用，比如 Workbuddy、Qclaw、Claude、马维斯等。

## 推荐安装方式

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

内置脚本：

- `scripts/collect_android_inventory.py`：只读盘点，不会删除、停用或修改手机里的任何 App。
- `scripts/block_install_routes.py`：默认 dry-run，只列出将关闭的安装入口；用户确认后加 `--apply`，才会执行 `adb shell appops set <包名> REQUEST_INSTALL_PACKAGES ignore`。
