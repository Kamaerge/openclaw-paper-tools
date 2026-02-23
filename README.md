<h1 align="center">OpenClaw Paper Tools</h1>

<p align="center">
  每天刷论文很爽，但每天刷 <b>论文列表</b> 很累。
</p>

这是一个「论文工作流自动化」的小工具，帮你把“发现论文 → 筛选 → 推送 → 一键精读”串起来：

- 🧠 **HF Daily Papers**：自动抓取 Hugging Face Papers 热榜，按 *Generation* / *Efficient* 分类输出
- 🚀 **SwiftScholar Submitter**：看到好论文，一句话提交到 SwiftScholar（aipaper.cc）生成 AI 精读
- ⏰ **08:00 定时推送（macOS LaunchAgent）**：每天早上把论文列表直接发到 Telegram
- 🧩 **可对话定制**：附带可上手 prompt，直接跟你自己的 OpenClaw 聊着聊着就把 skill “长”出来（按你的口味改关键词、改推送渠道、改格式）

## 你是不是也有这些痛点

- 😵‍💫 *“我只想看生成 / 高效化方向，结果每天被一堆无关论文淹没”*
- 🕳️ *“收藏夹堆到爆炸，真正精读的永远是明天”*
- 🤯 *“好不容易看到一篇对的，还要复制链接、找工具、粘贴、提交……”*
- 🧱 *“定时任务最烦：PATH、代理、环境变量、日志，一堆坑”*

这个工具只想帮你把一件事做顺：

- ✅ **每天 8 点把“你真正关心的论文”送到你手上**
- ✅ **看到值得精读的，直接一句话提交**


## ⚡️ Code Is Cheap, Show Me The Prompt！

仅通过对话构建自己的 paper 阅读 workflow！🧠⚡️
（下面的 prompt 可以直接丢进 OpenClaw，让它给你生成/改造这两个 skill）

### Prompt: build HF Daily Papers skill (with daily push)

```text
Create an OpenClaw skill named "hf-daily-papers".

Requirements:
- Fetch https://huggingface.co/papers, extract up to 30 paper ids.
- For each id, call https://huggingface.co/api/papers/<id> and collect title + upvotes + summary.
- Filter into two sections:
  - Generation (diffusion/video/image/generative)
  - Efficient (attention/sparse/quant/memory/optimization)
- Write a markdown report to:
  skills/hf-daily-papers/recommendations/YYYY-MM-DD.md
- Support an optional HF_DAILY_PAPERS_PROXY env var.
- Provide:
  - python generator.py (core logic)
  - script.sh (shell wrapper)
  - run_and_send.sh: generate + send a compact list to Telegram using:
    openclaw message send --channel telegram --target $TELEGRAM_TARGET --message "$MSG"
- Provide a macOS LaunchAgent template plist that runs run_and_send.sh everyday at 08:00.
  - The plist must set PATH to include /opt/homebrew/bin
  - The plist must accept TELEGRAM_TARGET and optional HF_DAILY_PAPERS_PROXY via EnvironmentVariables.
- Avoid any secrets in code or docs.

Keep it simple, readable, and production-friendly.
```

### Prompt: build SwiftScholar submitter skill

```text
Create an OpenClaw skill named "paper-submitter".

Requirements:
- Input: arXiv id (e.g. 2602.13515) or a Hugging Face paper link.
- Resolve to an arXiv URL and submit it to SwiftScholar via HTTPS.
- Read SwiftScholar API key from ~/.config/swiftscholar/api_key.txt or SWIFTSCHOLAR_API_KEY env.
- Optional Notion sync using NOTION_API_KEY + NOTION_PAPERS_DB_ID.
- Maintain a local markdown log submitted_papers.md (but do not include real history in the repo).
- Avoid any secrets in code or docs.

Keep it safe and boring (security first).
```

---

## 30 秒上手（本地跑一遍）

### 1) 生成今天的 HF 论文清单

```bash
cd skills/hf-daily-papers
python3 generator.py
```

### 2) 一句话提交精读

```bash
cd skills/paper-submitter
python3 submitter.py 2602.13515
```

---

## 配置（不公开密钥，放心）

- 🔐 本仓库 **不会** 存任何 key / token
- 🧼 提交记录、推荐列表、日志默认都被 `.gitignore` 忽略

你只需要在本地配置：

- SwiftScholar：`SWIFTSCHOLAR_API_KEY` 或 `~/.config/swiftscholar/api_key.txt`
- （可选）Notion：`NOTION_API_KEY` + `NOTION_PAPERS_DB_ID`
- （可选）代理：`HF_DAILY_PAPERS_PROXY`

详细写在：[docs/security.md](docs/security.md)

---

## 定时推送（macOS 08:00）

- 模板：[launchd/ai.openclaw.hf-daily-papers.plist](launchd/ai.openclaw.hf-daily-papers.plist)
- 说明：[docs/launchagent.md](docs/launchagent.md)

---

更多技术细节在 docs：

- [docs/README.md](docs/README.md)
