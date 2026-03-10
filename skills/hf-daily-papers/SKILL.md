# HF Daily Papers (OpenClaw Skill)

Generate a daily list of trending papers from Hugging Face Papers, filtered into:
- Generation (diffusion / video / image / generative)
- Efficient (attention / sparse / quant / memory / optimization)

Outputs:
- Markdown: `skills/hf-daily-papers/recommendations/YYYY-MM-DD.md`
- (Optional) PDF: `skills/hf-daily-papers/recommendations/YYYY-MM-DD.pdf`

## Quick Use (chat)

- "Generate today's HF papers"
- "HF daily papers"
- "Generate HF daily papers and send me the list"

## CLI

```bash
cd skills/hf-daily-papers
python3 generator.py

# PDF (requires `fpdf`)
python3 generator.py --pdf
```

## Push to Feishu (Windows)

```powershell
cd skills/hf-daily-papers

# one-off run (requires OPENCLAW has feishu channel configured)
$env:FEISHU_TARGET = "your-feishu-chat-id"
$env:HF_DAILY_INTERESTS = "generation,efficient"   # 可选: generation / efficient
$env:AUTO_SUBMIT_TOPN = "1"                         # 可选: 自动提交TopN到SwiftScholar
$env:NOTION_API_KEY = "your-notion-api-key"        # 可选: 启用后 submitter 自动写入 Notion
$env:NOTION_PAPERS_DB_ID = "your-notion-db-id"     # 可选
pwsh -File .\run_and_send.ps1

# register daily scheduled task at 08:00
pwsh -File .\register_task.ps1 -FeishuTarget "your-feishu-chat-id"

# register with interests + auto submit + notion sync
pwsh -File .\register_task.ps1 `
    -FeishuTarget "your-feishu-chat-id" `
    -InterestDomains "generation,efficient" `
    -AutoSubmitTopN 1 `
    -NotionApiKey "your-notion-api-key" `
    -NotionPapersDbId "your-notion-db-id"
```

Task name defaults to `OpenClaw-HF-Daily-Papers-Feishu`.

## Environment Variables

- `HF_DAILY_PAPERS_PROXY` (optional): HTTP(S) proxy URL, e.g. `http://127.0.0.1:7897`
- `FEISHU_TARGET` (required for Feishu push): chat target id for OpenClaw feishu channel
- `OPENCLAW_CHANNEL` (optional): defaults to `feishu` in run-and-send scripts
- `OPENCLAW_TARGET` (optional): overrides `FEISHU_TARGET`
- `HF_DAILY_GEN_KEYWORDS` (optional): 覆盖 Generation 关键词，逗号分隔
- `HF_DAILY_EFF_KEYWORDS` (optional): 覆盖 Efficient 关键词，逗号分隔
- `HF_DAILY_INTERESTS` (optional): 仅推送指定领域，`generation` / `efficient` / 两者
- `AUTO_SUBMIT_TOPN` (optional): 推送后自动提交 TopN 论文到 `paper-submitter`
- `SUBMITTER_SCRIPT` (optional): 自定义 submitter.py 路径
- `NOTION_API_KEY` / `NOTION_PAPERS_DB_ID` (optional): 自动精读后写入 Notion

## Notes

- This skill scrapes `https://huggingface.co/papers` to collect up to 30 recent paper IDs,
  then fetches details via `https://huggingface.co/api/papers/<id>`.
