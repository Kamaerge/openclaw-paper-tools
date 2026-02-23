# 技术细节

## HF Daily Papers 是怎么拿数据的

1. 抓取 Hugging Face Papers 首页：
- `https://huggingface.co/papers`

2. 从 HTML 里提取 paper id（形如 `YYYY.NNNNN`），最多取 30 个。

3. 逐个调用 HF 的 API 拿结构化信息：
- `https://huggingface.co/api/papers/<id>`
- 字段主要用：`title`, `summary`, `upvotes`

4. 关键词筛选

- Generation（生成方向）关键词示例：
  - diffusion, video, image, gan, generation, generative, synthesis, text-to
- Efficient（高效方向）关键词示例：
  - efficient, attention, quant, sparse, compress, memory, compute, optimization

5. 输出

- Markdown：`skills/hf-daily-papers/recommendations/YYYY-MM-DD.md`
- 可选 PDF：`python3 generator.py --pdf`（需要 `fpdf`）

## SwiftScholar Submitter 是怎么提交的

1. 输入：arXiv id（或 HF paper 链接）

2. 解析出 arXiv URL：
- `https://arxiv.org/abs/<id>`

3. 调 SwiftScholar API：
- `POST https://www.swiftscholar.net/api/tools/paper_submit_url`
- header：`Authorization: Bearer <SWIFTSCHOLAR_API_KEY>`

4. 返回 SwiftScholar paper 页面 URL。

5. 可选 Notion 同步
- 如果设置了 `NOTION_API_KEY` + `NOTION_PAPERS_DB_ID`，会自动创建数据库条目。

## 代理

如果你需要代理访问 Hugging Face：

- 设置 `HF_DAILY_PAPERS_PROXY`，例如：
  - `export HF_DAILY_PAPERS_PROXY="http://127.0.0.1:7897"`

该值会被用于 `HTTP_PROXY/HTTPS_PROXY`。
