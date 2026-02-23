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

## Environment Variables

- `HF_DAILY_PAPERS_PROXY` (optional): HTTP(S) proxy URL, e.g. `http://127.0.0.1:7897`

## Notes

- This skill scrapes `https://huggingface.co/papers` to collect up to 30 recent paper IDs,
  then fetches details via `https://huggingface.co/api/papers/<id>`.
