# 安全与密钥

## 目标

- 代码可以开源
- 密钥不出本地
- 不把你的个人历史（submitted_papers / recommendations / logs）推到仓库

## SwiftScholar Key

支持两种方式（推荐第一种）：

1) 本地文件（不会进 git）：
- `~/.config/swiftscholar/api_key.txt`

2) 环境变量：
- `SWIFTSCHOLAR_API_KEY`

## Notion（可选）

仅当你想同步到 Notion：
- `NOTION_API_KEY`
- `NOTION_PAPERS_DB_ID`

## .gitignore 建议

本仓库已经忽略：
- `skills/hf-daily-papers/recommendations/`
- `submitted_papers.md`
- `*.log`, `.env*`

你也可以按自己的习惯增强忽略规则。
