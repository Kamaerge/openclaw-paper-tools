# macOS LaunchAgent 定时（08:00）

仓库自带模板：`launchd/ai.openclaw.hf-daily-papers.plist`

## 你需要改的地方

- `ProgramArguments` 里的 `run_and_send.sh` 绝对路径
- `TELEGRAM_TARGET`
- （可选）`OPENCLAW_BIN`（默认 `openclaw`，建议填绝对路径）
- （可选）`HF_DAILY_PAPERS_PROXY`

## 安装

1. 复制并编辑：

```bash
cp launchd/ai.openclaw.hf-daily-papers.plist ~/Library/LaunchAgents/
$EDITOR ~/Library/LaunchAgents/ai.openclaw.hf-daily-papers.plist
```

2. 加载：

```bash
UID=$(id -u)
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/ai.openclaw.hf-daily-papers.plist
launchctl enable gui/$UID/ai.openclaw.hf-daily-papers
```

3. 立刻测试一次：

```bash
launchctl kickstart -k gui/$(id -u)/ai.openclaw.hf-daily-papers
```

## 日志

模板默认写到：
- `/tmp/ai.openclaw.hf-daily-papers.out.log`
- `/tmp/ai.openclaw.hf-daily-papers.err.log`

如果你希望写到仓库目录，也可以改 plist。
