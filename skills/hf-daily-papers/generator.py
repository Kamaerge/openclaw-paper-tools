#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HF Daily Papers Generator
生成 Markdown 和 PDF 格式的论文推荐报告
支持多来源：HuggingFace, arXiv, Papers with Code
"""

import os
import re
import urllib.request
import json
from datetime import datetime

# Optional proxy: set `HF_DAILY_PAPERS_PROXY` (e.g. http://127.0.0.1:7897) if you need it.
_proxy = os.environ.get('HF_DAILY_PAPERS_PROXY')
if _proxy:
    os.environ['HTTP_PROXY'] = _proxy
    os.environ['HTTPS_PROXY'] = _proxy

# 多源模式开关
USE_MULTI_SOURCE = os.environ.get('USE_MULTI_SOURCE', '1') == '1'


def parse_keywords(env_name, defaults):
    """从环境变量读取关键词（逗号分隔），未设置则使用默认值"""
    raw = os.environ.get(env_name, '').strip()
    if not raw:
        return defaults

    keywords = [part.strip().lower() for part in raw.split(',') if part.strip()]
    return keywords if keywords else defaults

def fetch_papers():
    """获取论文（支持多源模式）"""
    if USE_MULTI_SOURCE:
        return fetch_papers_multi_source()
    else:
        return fetch_papers_huggingface_only()


def fetch_papers_multi_source():
    """多源模式：从 HF + arXiv + PwC 获取论文并去重"""
    print("📥 多源模式：获取论文...")
    
    try:
        from multi_source_fetcher import (
            fetch_all_sources, 
            load_submitted_papers, 
            clean_old_records,
            deduplicate_papers
        )
        
        # 获取所有来源的论文
        all_papers = fetch_all_sources()
        
        # 加载已推送记录并清理旧记录
        cache_file = os.path.join(os.path.dirname(__file__), 'submitted_papers.json')
        submitted = load_submitted_papers(cache_file)
        submitted = clean_old_records(submitted, days=30)
        
        # 去重
        new_papers = deduplicate_papers(all_papers, submitted)
        
        # 按 upvotes 排序（HF 论文有 upvotes，arXiv 为 0）
        new_papers.sort(key=lambda x: (x.get('upvotes', 0), x.get('title', '')), reverse=True)
        
        return new_papers
    
    except Exception as e:
        print(f"❌ 多源获取失败，回退到单源模式: {e}")
        return fetch_papers_huggingface_only()


def fetch_papers_huggingface_only():
    """单源模式：仅从 HuggingFace Papers 获取"""
    print("📥 获取 HF Daily Papers...")
    
    # 获取页面
    req = urllib.request.Request("https://huggingface.co/papers", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode()
    
    # 提取论文 ID
    paper_ids = list(set(re.findall(r'href="/papers/([0-9]+\.[0-9]+)"', html)))[:30]
    
    # 获取论文详情
    papers = []
    for i, pid in enumerate(paper_ids):
        try:
            url = f"https://huggingface.co/api/papers/{pid}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                papers.append({
                    'pid': pid,
                    'title': data.get('title', 'N/A')[:100],
                    'upvotes': data.get('upvotes', 0),
                    'summary': data.get('summary', '')[:500].lower(),
                    'source': 'HuggingFace',
                    'url': f"https://huggingface.co/papers/{pid}"
                })
        except Exception as e:
            continue
        
        if (i+1) % 10 == 0:
            print(f"  已处理 {i+1}/{len(paper_ids)}...")
    
    # 按 upvotes 排序
    papers.sort(key=lambda x: x['upvotes'], reverse=True)
    return papers

def filter_papers(papers):
    """筛选论文"""
    # 针对特定领域的关键词：AR/VR、人机交互、时间序列、眼动追踪
    gen_kw = parse_keywords('HF_DAILY_GEN_KEYWORDS', 
                            ['ar', 'vr', 'augmented reality', 'virtual reality', 
                             'interaction', 'human-computer', 'eye tracking', 'gaze', 'gaze tracking'])
    eff_kw = parse_keywords('HF_DAILY_EFF_KEYWORDS', 
                            ['temporal', 'time series', 'trajectory', 'sequence',
                             'gaze', 'fixation', 'attention', 'eye movement'])
    
    print(f"🔍 Primary Keywords: {gen_kw if gen_kw else '(未设置)'}")
    print(f"🔍 Secondary Keywords: {eff_kw if eff_kw else '(未设置)'}")
    
    def keyword_match(text, keyword):
        """使用单词边界匹配关键词，避免短词误报"""
        # 对于短关键词（<=2字符），使用完整词匹配
        if len(keyword) <= 2:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            return bool(re.search(pattern, text, re.IGNORECASE))
        else:
            # 长关键词（包含多词短语）使用子串匹配
            # 对于 'augmented reality', 'eye tracking' 等多词短语，支持部分匹配
            return keyword.lower() in text.lower()
    
    gen_papers = [p for p in papers if any(keyword_match(p['title'].lower(), kw) or keyword_match(p['summary'], kw) for kw in gen_kw)]
    eff_papers = [p for p in papers if any(keyword_match(p['title'].lower(), kw) or keyword_match(p['summary'], kw) for kw in eff_kw)]
    
    return gen_papers, eff_papers

def generate_markdown(gen_papers, eff_papers, output_dir, timestamp):
    """生成 Markdown 文件"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    md_file = os.path.join(output_dir, f"{date_str}.md")
    
    # 收集所有论文 ID（用于标记为已推送）
    all_paper_ids = [p['pid'] for p in gen_papers] + [p['pid'] for p in eff_papers]
    
    md_content = f"""# Hugging Face Daily Papers 推荐

**生成时间**: {timestamp}
**论文来源**: {'多源聚合 (HF + arXiv + PwC)' if USE_MULTI_SOURCE else 'HuggingFace Papers'}

---

## 📌 主要关注领域 ({len(gen_papers)} 篇)

"""
    
    for i, p in enumerate(gen_papers[:15], 1):
        source_tag = f" `{p.get('source', 'HF')}`" if USE_MULTI_SOURCE else ""
        md_content += f"""### [{p['pid']}]({p.get('url', f"https://huggingface.co/papers/{p['pid']}")}) - {p['title']}{source_tag}

**Upvotes**: {p['upvotes']}

"""
    
    md_content += f"""

## 📎 次要关注领域 ({len(eff_papers)} 篇)

"""
    
    for i, p in enumerate(eff_papers[:15], 1):
        source_tag = f" `{p.get('source', 'HF')}`" if USE_MULTI_SOURCE else ""
        md_content += f"""### [{p['pid']}]({p.get('url', f"https://huggingface.co/papers/{p['pid']}")}) - {p['title']}{source_tag}

**Upvotes**: {p['upvotes']}

"""
    
    md_content += """---
*Generated by OpenClaw HF Daily Papers Skill*
"""
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ Markdown: {md_file}")
    
    # 如果是多源模式，标记为已推送
    if USE_MULTI_SOURCE and all_paper_ids:
        try:
            from multi_source_fetcher import mark_as_submitted
            cache_file = os.path.join(os.path.dirname(__file__), 'submitted_papers.json')
            mark_as_submitted(all_paper_ids, cache_file)
            print(f"✅ 已标记 {len(all_paper_ids)} 篇论文为已推送")
        except Exception as e:
            print(f"⚠️ 标记已推送失败: {e}")
    
    return md_file

def generate_pdf(gen_papers, eff_papers, output_dir, timestamp):
    """生成 PDF 文件"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    pdf_file = os.path.join(output_dir, f"{date_str}.pdf")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 标题
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, 'Hugging Face Daily Papers', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, 'Recommendation Report', ln=True, align='C')
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Generated: {timestamp}', ln=True)
    pdf.ln(5)
    
    # 主要关注领域
    pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(230, 240, 255)
    pdf.cell(0, 10, f'Primary Focus ({len(gen_papers)} papers)', ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font('Arial', '', 9)
    
    for i, p in enumerate(gen_papers[:15], 1):
        pdf.set_font('Arial', 'B', 9)
        title = re.sub(r'[^\x00-\x7F]+', '', p['title'])[:70]
        pdf.cell(0, 6, f"{i}. [{p['pid']}] {title}", ln=True)
        pdf.set_font('Arial', 'I', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"   Upvotes: {p['upvotes']}", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
    
    pdf.ln(5)
    
    # 次要关注领域
    pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(240, 250, 230)
    pdf.cell(0, 10, f'Secondary Focus ({len(eff_papers)} papers)', ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font('Arial', '', 9)
    
    for i, p in enumerate(eff_papers[:15], 1):
        pdf.set_font('Arial', 'B', 9)
        title = re.sub(r'[^\x00-\x7F]+', '', p['title'])[:70]
        pdf.cell(0, 6, f"{i}. [{p['pid']}] {title}", ln=True)
        pdf.set_font('Arial', 'I', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"   Upvotes: {p['upvotes']}", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
    
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, 'Generated by OpenClaw HF Daily Papers Skill', align='C')
    
    pdf.output(pdf_file)
    print(f"✅ PDF: {pdf_file}")
    return pdf_file

def main():
    import sys
    
    generate_pdf_flag = '--pdf' in sys.argv
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output_dir = os.path.dirname(os.path.abspath(__file__)) + "/recommendations"
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取并筛选论文
    papers = fetch_papers()
    gen_papers, eff_papers = filter_papers(papers)
    
    print(f"\n📊 Total: {len(papers)} papers | Generation: {len(gen_papers)} | Efficient: {len(eff_papers)}")
    
    # 生成 Markdown
    generate_markdown(gen_papers, eff_papers, output_dir, timestamp)
    
    # 生成 PDF（如果需要）
    if generate_pdf_flag:
        try:
            from fpdf import FPDF
            generate_pdf(gen_papers, eff_papers, output_dir, timestamp)
        except ImportError:
            print("⚠️ fpdf not installed. Run: pip3 install fpdf")

if __name__ == '__main__':
    main()
