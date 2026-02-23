<h1 align="center">OpenClaw Paper Tools</h1>

<p align="center">
  每天刷论文很爽，但每天刷 <b>论文列表</b> 很累。
</p>

这个仓库给你一套「论文工作流自动化」的小工具：

- 🧠 **HF Daily Papers**：自动抓取 Hugging Face Papers 热榜，按 *Generation* / *Efficient* 分类输出
- 🚀 **SwiftScholar Submitter**：看到好论文，一句话提交到 SwiftScholar（aipaper.cc）生成 AI 精读
- ⏰ **08:00 定时推送**（macOS LaunchAgent）：每天早上把论文列表直接发到 Telegram

---

## 你是不是也有这些痛点

- 😵‍💫 *“我只想看生成 / 高效化方向，结果每天被一堆无关论文淹没”*
- 🕳️ *“收藏夹堆到爆炸，真正精读的永远是明天”*
- 🤯 *“好不容易看到一篇对的，还要复制链接、找工具、粘贴、提交……”*
- 🧱 *“定时任务最烦：PATH、代理、环境变量、日志，一堆坑”*

这套工具的目标就一句话：

- ✅ **每天 8 点把“你真正关心的论文”送到你手上**
- ✅ **看到值得精读的，直接一句话提交**

---

## Code Is Cheap, Show Me The Prompt

If you already run OpenClaw, you can build these as skills by *just chatting*.

### Prompt: build HF Daily Papers skill

```text
Create an OpenClaw skill named "hf-daily-papers".

Requirements:
- Fetch https://huggingface.co/papers, extract up to 30 paper ids.
- For each id, call https://huggingface.co/api/papers/<id> and collect title + upvotes + summary.
- Filter into two sections: Generation (diffusion/video/image/generative) and Efficient (attention/sparse/quant/memory/optimization).
- Write a markdown report to skills/hf-daily-papers/recommendations/YYYY-MM-DD.md.
- Support an optional HF_DAILY_PAPERS_PROXY env var.
- Add a CLI entrypoint script.sh and a python generator.py.

Keep it simple, readable, and avoid any secrets.
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

Keep it safe: no keys in code or docs.
```

---

## 30 秒上手（本地跑一遍）

### 1) 生成今天的 HF 论文清单

```bash
cd skills/hf-daily-papers
python3 generator.py

# output: skills/hf-daily-papers/recommendations/YYYY-MM-DD.md
```

### 2) 一句话提交精读

```bash
cd skills/paper-submitter
python3 submitter.py 2602.13515

# output: SwiftScholar paper URL
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

你可以用 LaunchAgent 每天 08:00 自动把列表发到 Telegram。

- 模板：[launchd/ai.openclaw.hf-daily-papers.plist](launchd/ai.openclaw.hf-daily-papers.plist)
- 说明：[docs/launchagent.md](docs/launchagent.md)

---

更多技术细节在 docs：

- [docs/README.md](docs/README.md)
