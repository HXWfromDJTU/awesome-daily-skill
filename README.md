# awesome-daily-skill

面向日常生活场景的 Agent Skills 集合。

这里的 Skill 不只给 Codex 使用。任意支持 Skill / 自定义工作流 / 仓库安装能力的 Agent 都可以使用，比如 Workbuddy、Qclaw、Claude、马维斯等。只要它能读取仓库里的 `SKILL.md` 和配套文件，就可以按同一套流程执行。

## Skills

| Skill | 用途 |
|---|---|
| [`android-spam-app-disable-and-uninstall`](./android-spam-app-disable-and-uninstall/) | 帮父母清理安卓手机里的垃圾软件，列出安装来源，优先禁用 APK 安装权限，再处理确认不要的 App |

## 推荐安装方式

不要让普通用户手动复制文件。直接对你正在使用的 Agent 说：

```text
请从 GitHub 仓库 https://github.com/HXWfromDJTU/awesome-daily-skill 安装 android-spam-app-disable-and-uninstall 这个 Skill。
安装后，使用这个 Skill 帮我清理爸妈安卓手机里的垃圾软件。
```

如果 Agent 需要更明确的路径，可以补一句：

```text
Skill 目录是 android-spam-app-disable-and-uninstall，正式内容文件是 SKILL.md。
```

## 安全原则

- 先列清单，再确认，再执行。
- 不 root、不刷机、不恢复出厂设置。
- 不自动删除任何 App。
- 对微信、支付宝、银行、医保、社保、反诈、输入法、电话、短信、相册、系统桌面、系统设置等重要 App 默认保留。
- 对卸载、停用、禁用 APK 安装权限等动作，必须先展示命令和影响，再让用户确认。
