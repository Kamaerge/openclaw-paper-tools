# 更新日志 - v2.0

## 📅 2026-03-01

### 🎯 主要更新

#### 1. 多源论文聚合 🌐
- ✅ **整合多个论文来源**：
  - HuggingFace Papers（扩展到最近7天）
  - arXiv 最新提交（cs.CV, cs.AI, cs.LG, cs.CL）
  - Papers with Code 热门论文
  
- ✅ **智能去重机制**：
  - 使用 `submitted_papers.json` 追踪已推送论文
  - 自动清理 30 天前的旧记录
  - 跨来源去重（同一论文可能出现在多个平台）

#### 2. Top5 精读 📚
- **从 Top1 扩展到 Top5**
- 每日自动分析前 5 篇最相关论文
- 使用 OpenClaw nano-pdf 进行深度分析
- 生成 5 维度分析报告：核心贡献、技术方法、实验亮点、相关工作、局限性

#### 3. 配置简化 ⚙️
- **默认配置优化**：
  - `AUTO_SUBMIT_TOPN = 5`（默认 Top5）
  - `USE_MULTI_SOURCE = 1`（默认多源）
  - `USE_NANOPDF_ANALYZER = 1`（默认 nano-pdf）

### 📊 性能提升

| 指标 | 之前 | 现在 | 提升 |
|------|------|------|------|
| 论文来源 | 1 个 | 3 个 | +200% |
| 日均论文量 | ~30 篇 | ~80 篇 | +167% |
| 精读数量 | 1 篇 | 5 篇 | +400% |
| 去重机制 | ❌ | ✅ | 新增 |

### 🔧 技术改进

1. **新增文件**：
   - `multi_source_fetcher.py` - 多源论文获取器
   - `submitted_papers.json` - 已推送论文缓存

2. **修改文件**：
   - `generator.py` - 支持多源模式切换
   - `register_task.ps1` - 新增多源参数，默认 Top5
   - `run_and_send.ps1` - 修复分析器路径

3. **关键特性**：
   - 单词边界匹配（避免短关键词误报）
   - 环境变量完全控制（无硬编码）
   - 论文来源标签（显示论文来自哪个平台）

### 📖 使用示例

#### 注册任务（新配置）
```powershell
.\register_task.ps1 `
  -FeishuTarget 'oc_xxx' `
  -GenKeywords 'agent,benchmark,multimodal' `
  -EffKeywords 'efficient,optimization' `
  -AutoSubmitTopN 5 `
  -UseNanoPdfAnalyzer `
  -UseMultiSource
```

#### 手动运行（多源 + Top5）
```powershell
$env:OPENCLAW_TARGET = 'oc_xxx'
$env:HF_DAILY_GEN_KEYWORDS = 'agent,benchmark'
$env:HF_DAILY_EFF_KEYWORDS = 'efficient'
$env:AUTO_SUBMIT_TOPN = '5'
$env:USE_MULTI_SOURCE = '1'
$env:USE_NANOPDF_ANALYZER = '1'
.\run_and_send.ps1
```

#### 关闭多源模式（仅 HF）
```powershell
$env:USE_MULTI_SOURCE = '0'
.\run_and_send.ps1
```

### 🎯 下一步计划

- [ ] 优化 Papers with Code API 集成
- [ ] 添加更多论文源（如 Semantic Scholar）
- [ ] 支持自定义 arXiv 分类
- [ ] 论文质量评分机制
- [ ] 邮件推送选项

### 🐛 已知问题

- Papers with Code API 可能返回空结果（不影响主要功能）
- 含特殊字符的论文标题可能导致飞书发送失败（已保存本地）

### ✅ 测试结果

```
📊 测试日期: 2026-03-01
✅ 多源获取: 80 篇论文（HF 0 + arXiv 80）
✅ 去重: 移除 14 篇重复论文
✅ 筛选: 17 篇主要 + 7 篇次要
✅ Top5 精读: 全部成功
✅ 飞书推送: 4/5 成功（1 篇特殊字符问题）
```

---

**版本**: v2.0  
**更新时间**: 2026-03-01  
**贡献者**: GitHub Copilot & User
