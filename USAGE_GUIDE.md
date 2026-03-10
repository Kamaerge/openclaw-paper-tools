# 详细使用指南

完整的配置、高级用法和故障排除指南。快速开始见 [README.md](README.md)。

---

## 目录

1. [安装和初始化](#安装和初始化)
2. [配置关键词](#配置关键词)
3. [注册定时任务](#注册定时任务)
4. [验证和测试](#验证和测试)
5. [常见配置预设](#常见配置预设)
6. [故障排除](#故障排除)
7. [进阶用法](#进阶用法)

---

## 安装和初始化

### Windows

#### 1. 安装 OpenClaw

```powershell
npm install -g openclaw
openclaw status  # 验证安装
```

#### 2. 配置 Feishu 频道

```powershell
# 如果尚未配置，运行
openclaw plugins list
openclaw plugins enable feishu

# 获取您的飞书群组 ID（从 OpenClaw 配置或应用中获取）
# 格式通常为 oc_xxxxx...
```

#### 3. 验证 Python 环境

```powershell
python --version    # 需要 3.8+
pip install urllib3 json  # 基本库（通常已有）
```

#### 4. 克隆或下载本项目

```powershell
git clone https://github.com/your-repo/openclaw-paper-tools.git
cd openclaw-paper-tools
```

### macOS / Linux

需要 Bash + Python 3.8+。参考 [docs/launchagent.md](docs/launchagent.md)。

---

## 配置关键词

### 什么是关键词？

关键词用于匹配论文的标题和摘要。系统会检查每篇论文是否包含您指定的任何关键词。

- ✅ 好例子：`eye tracking`, `gaze stabilization`, `temporal prediction`
- ✅ 好例子：`LLM`, `GPU`, `quantization`
- ❌ 差例子：`learning`, `model`, `paper`（太通用）

### 关键词匹配规则

- **不分大小写**：`Eye Tracking` = `eye tracking`
- **空格和符号**：单个关键词内的空格被保留（`eye tracking` 是一个关键词）
- **逻辑**：只要论文标题或摘要包含**至少一个**您指定的关键词，就会被筛选出来
- **顺序无关**：`eye tracking` 和 `tracking eye` 都能匹配同一篇论文

### 推荐关键词列表

#### 计算机视觉（Vision）

```
vision,computer vision,image,video,object detection,segmentation,
3D,reconstruction,tracking,optical flow,pose estimation,depth estimation,
neural radiance field,NeRF,gaussian splatting
```

#### 生成模型（Generation）

```
generation,generative,diffusion,DDPM,DDIM,flow matching,
text-to-image,image-to-image,video generation,synthesis,
GAN,VAE,autoencoder,transformer
```

#### 大语言模型和 NLP

```
LLM,language model,ChatGPT,GPT,BERT,T5,LLAMA,
transformer,attention,RLHF,fine-tuning,prompt,in-context learning
```

#### 高效化和优化（Efficiency）

```
efficient,optimization,quantization,int8,int4,pruning,
sparse,compression,distillation,knowledge distillation,
acceleration,fast inference,lightweight,mobile
```

#### 多模态（Multimodal）

```
multimodal,vision-language,CLIP,VLM,visual question answering,
image caption,cross-modal,fusion,alignment
```

#### 强化学习和机器人（RL + Robotics）

```
reinforcement learning,RL,policy,reward,MDP,
robot,robotics,manipulation,control,embodied AI,simulation
```

#### 时间序列和预测（Temporal）

```
temporal,time series,forecasting,prediction,sequence,
LSTM,RNN,GRU,transformer time series,motion prediction,
trajectory prediction,action prediction
```

---

## 注册定时任务

### 基础用法

```powershell
cd skills/hf-daily-papers

.\register_task.ps1 `
  -FeishuTarget 'oc_c10dddb79f789d945e7d2317d5014d08' `
  -GenKeywords 'YOUR_KEYWORDS_HERE' `
  -EffKeywords 'YOUR_KEYWORDS_HERE' `
  -UseNanoPdfAnalyzer `
  -AutoSubmitTopN 1
```

### 完整的可选参数

```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -TaskName 'MyPaperTask' `
  -Time '09:00' `
  -OpenclawChannel 'feishu' `
  -OpenclawBin 'openclaw' `
  -PythonBin 'python' `
  -GenKeywords '...' `
  -EffKeywords '...' `
  -InterestDomains 'Category1,Category2' `
  -AutoSubmitTopN 1 `
  -UseNanoPdfAnalyzer
```

### 参数详解

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `-FeishuTarget` | ✅ | 无 | 飞书群组 ID（格式：`oc_...`） |
| `-TaskName` | ❌ | `'OpenClaw-HF-Daily-Papers-Feishu'` | Windows 计划任务的名称 |
| `-Time` | ❌ | `'08:00'` | 每日执行时间（HH:MM） |
| `-OpenclawChannel` | ❌ | `'feishu'` | 推送渠道（通常是 feishu） |
| `-GenKeywords` | ❌ | 空 | 第一类论文关键词（逗号分隔） |
| `-EffKeywords` | ❌ | 空 | 第二类论文关键词（逗号分隔） |
| `-InterestDomains` | ❌ | `'generation,efficient'` | 显示标签（在飞书消息中显示） |
| `-AutoSubmitTopN` | ❌ | `0` | 自动分析前 N 篇论文（0=禁用） |
| `-UseNanoPdfAnalyzer` | ❌ | 无 | 启用 nano-pdf 深度分析 |

---

## 验证和测试

### Step 1: 单次手动运行

```powershell
cd skills/hf-daily-papers

$env:OPENCLAW_TARGET = 'oc_xxx'
$env:HF_DAILY_GEN_KEYWORDS = 'YOUR_KEYWORDS'
$env:HF_DAILY_EFF_KEYWORDS = 'YOUR_KEYWORDS'
$env:AUTO_SUBMIT_TOPN = '1'
$env:USE_NANOPDF_ANALYZER = '1'

.\run_and_send.ps1
```

观察输出和飞书群组：
- 论文列表应该专注于您的兴趣领域
- 分析结果应该在 2-3 分钟内出现

### Step 2: 检查任务注册

```powershell
# 列出任务
schtasks /Query /TN "*HF*"

# 详细信息
schtasks /Query /TN "OpenClaw-HF-Daily-Papers-Feishu" /V

# 查看下次运行时间
schtasks /Query /TN "OpenClaw-HF-Daily-Papers-Feishu" /NextRunTime
```

### Step 3: 测试定时执行

```powershell
# 立即运行任务（不等待时间表）
schtasks /Run /TN "OpenClaw-HF-Daily-Papers-Feishu"

# 监控执行（需要管理员）
Get-Job | Select-Object Name, State
```

### Step 4: 检查日志

Windows 事件查看器：
- **路径**：事件查看器 → Windows 日志 → 系统
- **搜索**：`OpenClaw-HF-Daily-Papers-Feishu`
- **查看**：任务执行成功/失败

---

## 常见配置预设

### 配置 1: AR 眼动追踪 + 时序预测

```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_c10dddb79f789d945e7d2317d5014d08' `
  -GenKeywords 'AR,augmented reality,eye tracking,gaze stabilization,pupil tracking,head-mounted display' `
  -EffKeywords 'temporal prediction,trajectory prediction,motion forecasting,sequence prediction,LSTM,RNN' `
  -InterestDomains 'AR/Gaze,Temporal Prediction' `
  -UseNanoPdfAnalyzer `
  -AutoSubmitTopN 1
```

### 配置 2: 计算机视觉 + 优化

```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -GenKeywords 'vision,object detection,segmentation,3D reconstruction,tracking,pose estimation' `
  -EffKeywords 'optimization,efficient inference,pruning,quantization,acceleration' `
  -InterestDomains 'Vision,Efficiency' `
  -UseNanoPdfAnalyzer `
  -AutoSubmitTopN 1
```

### 配置 3: 大模型 + 微调

```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -GenKeywords 'LLM,language model,ChatGPT,GPT,LLAMA,transformer' `
  -EffKeywords 'quantization,distillation,LoRA,fine-tuning,compression,int8' `
  -InterestDomains 'LLM,Fine-tuning' `
  -UseNanoPdfAnalyzer `
  -AutoSubmitTopN 1
```

### 配置 4: 强化学习 + 机器人

```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -GenKeywords 'reinforcement learning,robot,manipulation,control,embodied AI' `
  -EffKeywords 'sample efficiency,meta-learning,transfer learning,imitation' `
  -InterestDomains 'RL,Robotics' `
  -UseNanoPdfAnalyzer `
  -AutoSubmitTopN 1
```

---

## 故障排除

### 问题 1: "Missing runner script"

**原因**：`run_and_send.ps1` 未找到

**解决**：
```powershell
# 确保在正确目录
cd d:\Project\openclaw-paper-tools\skills\hf-daily-papers

# 或者提供完整路径
$runnerPath = 'D:\Project\openclaw-paper-tools\skills\hf-daily-papers\run_and_send.ps1'
```

### 问题 2: 飞书没有收到任何消息

**检查清单**：
```powershell
# 1. 检查 OpenClaw 是否运行
openclaw status

# 2. 验证 Feishu 配置
openclaw config get feishu

# 3. 测试消息发送
openclaw message send --channel feishu --target oc_xxx --message "Test Message"

# 4. 检查您的飞书 ID 是否正确
# 应该是 oc_ 开头的长字符串
```

### 问题 3: 论文列表为空

**原因**：关键词过于严格，没有论文匹配

**解决**：
```powershell
# 临时调试：使用更通用的关键词
$env:HF_DAILY_GEN_KEYWORDS = 'learning,model'
.\run_and_send.ps1

# 查看生成的 Markdown 文件
Get-Content recommendations\2026-03-01.md
```

### 问题 4: 任务未自动执行

**检查**：
```powershell
# 1. 验证任务是否存在
schtasks /Query /TN "*HF*"

# 2. 检查任务是否启用
schtasks /Query /TN "OpenClaw-HF-Daily-Papers-Feishu" /V | Select-String "Status"

# 3. 查看最后运行时间和结果
schtasks /Query /TN "OpenClaw-HF-Daily-Papers-Feishu" /V | Select-String "Last Result"
```

**可能原因**：
- 计算机在计划的时间未开机
- Windows 更新导致计划任务被禁用
- 用户账户权限不足

**重新注册**：
```powershell
# 删除旧任务
schtasks /Delete /TN "OpenClaw-HF-Daily-Papers-Feishu" /F

# 重新注册
.\register_task.ps1 -FeishuTarget 'oc_xxx' ...
```

### 问题 5: 分析结果很短或重复

**原因**：OpenClaw Agent 会缓存之前见过的论文，重复查询时返回简短响应

**解决**：
- 使用不同的关键词组合，让每天的论文不同
- 或等待 OpenClaw 更新缓存策略
- nano-pdf 已优化：每次使用唯一 session 来避免缓存

---

## 进阶用法

### 自定义推送内容

编辑 `skills/hf-daily-papers/run_and_send.ps1` 中的消息模板：

```powershell
# 大约第 150-160 行
$msg = @"
🎯 HF Daily Papers ($dateStr)
...
"@
```

### 禁用某一类论文

```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -GenKeywords 'your-keywords' `
  -EffKeywords '' `  # 空字符串表示禁用
  -UseNanoPdfAnalyzer
```

### 修改执行时间

```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -Time '09:30' `
  -UseNanoPdfAnalyzer
```

### 使用代理（可选）

```powershell
$env:HF_DAILY_PAPERS_PROXY = 'http://127.0.0.1:7897'
.\run_and_send.ps1
```

### 禁用自动分析，只推送列表

```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -AutoSubmitTopN 0  # 不自动分析
  # 不需要 -UseNanoPdfAnalyzer
```

---

## 更新和维护

### 更新兴趣关键词

```powershell
# 1. 删除旧任务
schtasks /Delete /TN "OpenClaw-HF-Daily-Papers-Feishu" /F

# 2. 重新注册（使用新的关键词）
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -GenKeywords 'NEW_KEYWORDS' `
  ...
```

### 查看历史推荐

所有日期的论文列表都保存在：

```
skills/hf-daily-papers/recommendations/YYYY-MM-DD.md
```

### 查看分析结果存档

所有分析的结果都保存为 Markdown：

```
skills/paper-submitter/analysis_results/ARXIV_ID_TITLE.md
```

---

## FAQ

**Q: 可以只推送列表，不自动分析吗？**  
A: 可以，设置 `-AutoSubmitTopN 0`

**Q: 可以改变推送渠道（比如 Telegram、Slack）吗？**  
A: 可以，修改 `-OpenclawChannel` 参数（需要 OpenClaw 支持该渠道）

**Q: 分析结果去哪了？**  
A: 飞书群组消息 + 本地 Markdown 存档（`skills/paper-submitter/analysis_results/`）

**Q: 如何自定义分析的 5 个维度？**  
A: 编辑 `skills/paper-submitter/analyze_with_nanopdf.py` 的 prompt

**Q: 支持多个飞书群组吗？**  
A: 可以注册多个任务，使用不同的 `-TaskName` 和 `-FeishuTarget`

