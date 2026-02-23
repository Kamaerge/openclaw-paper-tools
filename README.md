# OpenClaw Paper Tools

Automate your daily paper workflow:

- **HF Daily Papers**: fetch + filter trending Hugging Face Papers into *Generation* and *Efficient* buckets.
- **SwiftScholar Submitter**: submit an arXiv paper to SwiftScholar (aipaper.cc) for AI deep reading.

Designed to be:
- **Fast** (single command / single chat message)
- **Automatable** (macOS LaunchAgent at 08:00)
- **Safe** (**no keys in repo**; everything uses env vars / local config files)

---

## Demo

### 1) Get today's HF paper list

```bash
cd skills/hf-daily-papers
python3 generator.py

# output: skills/hf-daily-papers/recommendations/YYYY-MM-DD.md
```

### 2) Submit a paper for AI reading

```bash
cd skills/paper-submitter
python3 submitter.py 2602.13515

# output: a SwiftScholar paper URL
```

---

## Install

Prereqs:
- macOS or Linux
- Python 3
- OpenClaw installed and logged in for your target channel (Telegram / etc.)

Optional PDF support:

```bash
pip3 install fpdf
```

---

## Configuration (No Secrets Committed)

### SwiftScholar API key

Use either:

1) Save it locally (recommended):

```bash
cd skills/paper-submitter
python3 submitter.py --save-key YOUR_SWIFTSCHOLAR_API_KEY
```

2) Or set env var:

```bash
export SWIFTSCHOLAR_API_KEY="YOUR_SWIFTSCHOLAR_API_KEY"
```

### (Optional) Notion sync

If you want every submission to also create a row in a Notion database:

```bash
export NOTION_API_KEY="ntn_xxx"
export NOTION_PAPERS_DB_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### (Optional) Proxy

If your network needs a proxy to access Hugging Face:

```bash
export HF_DAILY_PAPERS_PROXY="http://127.0.0.1:7897"
```

---

## Automate: macOS LaunchAgent (08:00 every day)

This repo ships a template:
- `launchd/ai.openclaw.hf-daily-papers.plist`

Steps:

1) Copy it to `~/Library/LaunchAgents/` and edit:
- the absolute path to `run_and_send.sh`
- `TELEGRAM_TARGET`

2) Load it:

```bash
UID=$(id -u)
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/ai.openclaw.hf-daily-papers.plist
launchctl enable gui/$UID/ai.openclaw.hf-daily-papers
```

3) Test immediately:

```bash
launchctl kickstart -k gui/$(id -u)/ai.openclaw.hf-daily-papers
```

Logs (as configured in the template):
- `/tmp/ai.openclaw.hf-daily-papers.out.log`
- `/tmp/ai.openclaw.hf-daily-papers.err.log`

---

## What This Actually Does

### HF Daily Papers

- Scrapes `https://huggingface.co/papers` for recent paper IDs
- Fetches metadata via `https://huggingface.co/api/papers/<id>`
- Filters into two lists with simple keyword rules
- Writes `recommendations/YYYY-MM-DD.md` (+ optional PDF)

### SwiftScholar Submitter

- Gets title/arXiv id from the HF paper page
- Calls SwiftScholar API (`/api/tools/paper_submit_url`)
- Prints a paper URL you can open in your browser
- Optionally appends a row to `submitted_papers.md`
- Optionally syncs to Notion

---

## Code Is Cheap, Show Me The Prompt

If you already run OpenClaw, you can build these as skills by *just chatting*.

### Prompt: build HF Daily Papers skill

Copy/paste this into an OpenClaw chat:

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

## License

MIT (see `LICENSE`).
