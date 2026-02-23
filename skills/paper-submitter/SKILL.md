# SwiftScholar Paper Submitter (OpenClaw Skill)

Submit an arXiv paper (usually found via Hugging Face Papers) to SwiftScholar (aipaper.cc) for AI reading.

Features:
- Submit by arXiv ID (e.g. `2602.13515`)
- Maintains a local `submitted_papers.md` log (optional)
- Optional Notion sync (via env vars)

## Quick Use (chat)

- "Submit 2602.13515 for reading"
- "Submit https://huggingface.co/papers/2602.13515"
- "List submitted papers"

## CLI

```bash
cd skills/paper-submitter

# Submit by arXiv/HF paper id
python3 submitter.py 2602.13515

# List history
python3 submitter.py --list

# Save SwiftScholar API key (writes to ~/.config/swiftscholar/api_key.txt)
python3 submitter.py --save-key YOUR_SWIFTSCHOLAR_API_KEY
```

## Auth (no secrets in repo)

SwiftScholar API key is required. Provide it via:
- `~/.config/swiftscholar/api_key.txt` (created by `--save-key`), or
- env var `SWIFTSCHOLAR_API_KEY`

Optional Notion sync (only if you want it):
- `NOTION_API_KEY`
- `NOTION_PAPERS_DB_ID`

## Security

- Do NOT commit any API keys.
- Prefer env vars or local config files outside the repo.
