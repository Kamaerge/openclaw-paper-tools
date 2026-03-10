# OpenClaw Paper Tools

<h1 align="center">OpenClaw 论文工具</h1>

<p align="center">
  <b>自动发现 → 个性化筛选 → AI 深度分析 → 飞书实时推送</b>
</p>

论文工作流自动化工具，把"发现论文 → 筛选 → 推送 → 一键精读"串起来。

## 核心特性

- 🌐 **多源论文聚合**：整合 HuggingFace Papers + arXiv + Papers with Code（~80 篇/天）
- 🔄 **智能去重**：自动追踪已推送论文，避免重复（30 天滚动缓存）
- 🎯 **个性化筛选**：按关键词筛选，完全可定制（支持单词边界匹配）
- 🤖 **OpenClaw nano-pdf 分析**：AI 驱动的论文深度分析（5 个维度：核心贡献、技术方法、实验亮点、相关工作、局限性）
- 📚 **Top5 精读**：每日自动深度分析前 5 篇最相关论文（可配置）
- 📱 **飞书群组推送**：每天 08:00 自动发送论文列表和分析结果
- 💾 **本地存档**：所有分析结果保存为 Markdown，便于查阅和搜索
- 🎛️ **一键注册**：一条命令配置每日定时任务（Windows 计划任务）

## 工作流

```
多源聚合 (~80篇)
 ├─ HuggingFace Papers (最近7天)
 ├─ arXiv (cs.CV/AI/LG/CL)
 └─ Papers with Code
    ↓
① 智能去重 + 关键词筛选
    ↓
② 飞书推送论文列表
    ↓
③ nano-pdf 分析 (Top5)
    ↓
④ 飞书推送分析结果 + 本地存档
    ↓
⑤ 标记已推送（避免重复）
```

## 快速开始（5 分钟）

### 前置要求

- Windows 10+ 或 macOS
- OpenClaw 已安装并配置 Feishu
- Python 3.8+

### Step 1: 单次测试

```powershell
cd skills/hf-daily-papers

# 设置飞书群组 ID（从 OpenClaw 配置获取）
$env:OPENCLAW_TARGET = 'oc_c10dddb79f789d945e7d2317d5014d08'
$env:AUTO_SUBMIT_TOPN = '5'  # Top5 精读
$env:USE_MULTI_SOURCE = '1'  # 多源聚合

# 运行工作流
.\run_and_send.ps1
```

您将在飞书群组看到：
1. 📰 多源聚合的论文列表（标注来源）
2. 🤖 前 5 篇论文的深度分析（如已启用）

### Step 2: 配置您的兴趣领域

```powershell
# 根据您的研究方向自定义兴趣领域（Top5 精读 + 多源聚合）
.\register_task.ps1 `
  -FeishuTarget 'oc_c10dddb79f789d945e7d2317d5014d08' `
  -GenKeywords 'agent,benchmark,multimodal,reasoning' `
  -EffKeywords 'efficient,optimization,compression' `
  -UseNanoPdfAnalyzer `
  -UseMultiSource `
  -AutoSubmitTopN 5
```

### Step 3: 验证和测试

```powershell
# 查看已注册的任务
schtasks /Query /TN "*HF*"

# 立即运行任务（测试）
schtasks /Run /TN "OpenClaw-HF-Daily-Papers-Feishu"
```

---

## 配置参数说明

| 参数 | 说明 | 默认值 / 示例 |
|------|------|------|
| `-FeishuTarget` | 飞书群组 ID（必需） | `oc_c10...` |
| `-GenKeywords` | 主要关注领域关键词 | `agent,benchmark,multimodal` |
| `-EffKeywords` | 次要关注领域关键词 | `efficient,optimization` |
| `-UseNanoPdfAnalyzer` | 启用 nano-pdf 深度分析 | 默认开启 |
| `-UseMultiSource` | 启用多源聚合 | 默认开启 |
| `-AutoSubmitTopN` | 自动分析前 N 篇论文 | 默认 `5` |
| `-Time` | 每日执行时间 | 默认 `08:00` |
| `-Time` | 每日执行时间 | `08:00`（默认） |

详见 [USAGE_GUIDE.md](USAGE_GUIDE.md)。

---

## 常见配置示例

### 计算机视觉 + 优化

```powershell
.\register_task.ps1 -FeishuTarget 'oc_xxx' `
  -GenKeywords 'vision,object detection,3D reconstruction' `
  -EffKeywords 'optimization,efficient inference,acceleration' `
  -UseNanoPdfAnalyzer -AutoSubmitTopN 1
```

### 大模型 + 微调

```powershell
.\register_task.ps1 -FeishuTarget 'oc_xxx' `
  -GenKeywords 'LLM,language model,GPT,transformer' `
  -EffKeywords 'quantization,distillation,LoRA,fine-tuning' `
  -UseNanoPdfAnalyzer -AutoSubmitTopN 1
```

### 强化学习 + 机器人

```powershell
.\register_task.ps1 -FeishuTarget 'oc_xxx' `
  -GenKeywords 'reinforcement learning,robot,control,manipulation' `
  -EffKeywords 'sample efficiency,meta-learning,transfer learning' `
  -UseNanoPdfAnalyzer -AutoSubmitTopN 1
```

---

## 文件结构

```
openclaw-paper-tools/
├── README.md                          # [您在这里] 快速开始
├── USAGE_GUIDE.md                     # 详细配置和常见问题
├── LICENSE                            # MIT License
├── skills/
│   ├── hf-daily-papers/               # 论文爬取和推送
│   │   ├── generator.py              # 爬取HF Papers并按关键词筛选
│   │   ├── run_and_send.ps1          # 主工作流（Windows）
│   │   ├── register_task.ps1         # 注册定时任务
│   │   ├── run_and_send.sh           # 主工作流（macOS/Linux）
│   │   ├── script.sh                 # LaunchAgent 幼虫脚本
│   │   ├── SKILL.md                  # OpenClaw Skill 描述
│   │   └── recommendations/          # 每日推荐列表（生成的）
│   │
│   └── paper-submitter/               # 论文分析和存档
│       ├── analyze_with_nanopdf.py   # OpenClaw nano-pdf 深度分析
│       ├── script.sh                 # LaunchAgent 辅助脚本
│       ├── SKILL.md                  # Skill 描述
│       └── analysis_results/         # 分析结果存档（Markdown）
│
├── launchd/                           # macOS 定时任务配置
│   └── ai.openclaw.hf-daily-papers.plist
│
└── docs/                              # 技术文档
    ├── README.md                      # 架构设计文档
    ├── technical.md                   # 技术细节
    ├── security.md                    # 安全性说明
    └── launchagent.md                 # macOS LaunchAgent 说明
```

---

## 工作原理

### 单次执行流程

1. **生成论文列表**：`generator.py` 爬取 HF Papers，按关键词筛选
2. **推送到飞书**：发送论文排行榜到飞书群组
3. **自动分析（可选）**：如果 `AUTO_SUBMIT_TOPN > 0`，使用 nano-pdf 分析前 N 篇
4. **存档**：分析结果保存为 Markdown，本地存档

### 每日定时执行

`register_task.ps1` 在 Windows 中注册计划任务，每天 08:00 自动执行上述流程。

---

## 环境变量

所有配置都通过环境变量传递（无密钥存储）：

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENCLAW_TARGET` | 飞书群组 ID | `oc_c10...` |
| `OPENCLAW_CHANNEL` | 推送渠道 | `feishu` |
| `HF_DAILY_GEN_KEYWORDS` | 生成类论文关键词 | `diffusion,video` |
| `HF_DAILY_EFF_KEYWORDS` | 效率类论文关键词 | `quantization,sparse` |
| `HF_DAILY_INTERESTS` | 显示的分类名称 | `Generation,Efficient` |
| `AUTO_SUBMIT_TOPN` | 自动分析数量 | `1` |
| `USE_NANOPDF_ANALYZER` | 启用 nano-pdf 分析 | `1` |

---

## 故障排除

### 问题：飞书没有收到消息

**检查**：
1. `OPENCLAW_TARGET` 是否正确（`oc_...`）
2. 确认 OpenClaw 已启动：`openclaw status`
3. 测试消息连接：`openclaw message send --channel feishu --target <ID> --message "Test"`

### 问题：论文分析结果很短

**原因**：OpenClaw Agent 首次分析时长，之后每个新 session 生成独立分析。

**解决**：使用新的兴趣关键词测试，会自动创建新的分析。

### 问题：每天没有自动推送

**检查**：
1. 任务是否注册：`schtasks /Query /TN "*HF*"`
2. 任务是否启用：`schtasks /Query /TN "OpenClaw-HF-Daily-Papers-Feishu" /V`
3. 查看任务历史：事件查看器 → 计划任务

---

## 更新配置

如果要修改兴趣领域或执行时间：

```powershell
# 1. 删除旧任务
schtasks /Delete /TN "OpenClaw-HF-Daily-Papers-Feishu" /F

# 2. 使用新参数重新注册
.\register_task.ps1 -FeishuTarget 'oc_xxx' -GenKeywords '...' ...
```

---

## MIT License

可自由使用和修改，保留原作权信息即可。
