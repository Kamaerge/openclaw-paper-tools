#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Source Paper Fetcher
整合多个论文来源：HuggingFace Papers, arXiv, Papers with Code
"""

import os
import re
import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# Proxy setting
_proxy = os.environ.get('HF_DAILY_PAPERS_PROXY')
if _proxy:
    os.environ['HTTP_PROXY'] = _proxy
    os.environ['HTTPS_PROXY'] = _proxy


def load_submitted_papers(cache_file='submitted_papers.json'):
    """加载已推送论文记录"""
    if not os.path.exists(cache_file):
        return {}
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载已推送记录失败: {e}")
        return {}


def save_submitted_papers(submitted, cache_file='submitted_papers.json'):
    """保存已推送论文记录"""
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(submitted, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 保存已推送记录失败: {e}")


def clean_old_records(submitted, days=30):
    """清理超过指定天数的旧记录"""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    cleaned = {k: v for k, v in submitted.items() if v.get('date', '') > cutoff}
    removed = len(submitted) - len(cleaned)
    if removed > 0:
        print(f"🧹 清理了 {removed} 条超过 {days} 天的旧记录")
    return cleaned


def fetch_huggingface_papers(days=7, max_papers=50):
    """获取 HuggingFace Papers（扩展到最近N天）"""
    print(f"📥 获取 HuggingFace Papers (最近 {days} 天)...")
    
    try:
        req = urllib.request.Request("https://huggingface.co/papers", 
                                    headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode()
        
        # 提取论文 ID
        paper_ids = list(set(re.findall(r'href="/papers/([0-9]+\.[0-9]+)"', html)))[:max_papers]
        
        papers = []
        for i, pid in enumerate(paper_ids):
            try:
                url = f"https://huggingface.co/api/papers/{pid}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read().decode())
                    
                    # 检查日期
                    pub_date_str = data.get('publishedAt', '')
                    if pub_date_str:
                        pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                        if (datetime.now() - pub_date).days > days:
                            continue
                    
                    papers.append({
                        'pid': pid,
                        'title': data.get('title', 'N/A'),
                        'upvotes': data.get('upvotes', 0),
                        'summary': data.get('summary', '')[:500].lower(),
                        'source': 'HuggingFace',
                        'url': f"https://huggingface.co/papers/{pid}"
                    })
            except Exception as e:
                continue
            
            if (i+1) % 10 == 0:
                print(f"  HF: 已处理 {i+1}/{len(paper_ids)}...")
        
        print(f"✅ HuggingFace: 获取到 {len(papers)} 篇论文")
        return papers
    
    except Exception as e:
        print(f"❌ HuggingFace 获取失败: {e}")
        return []


def fetch_arxiv_recent(categories=None, max_results=30):
    """获取 arXiv 最新提交的论文
    
    默认分类针对 AR/眼动追踪/时间预测领域：
    - cs.CV: 计算机视觉（AR、眼动跟踪）
    - cs.HC: 人机交互（AR应用、眼动界面）
    - cs.RO: 机器人学（AR、眼动在机器人中的应用）
    - cs.LG: 机器学习（时间序列预测）
    - stat.ML: 统计机器学习（时间序列、预测）
    """
    if categories is None:
        categories = ['cs.CV', 'cs.HC', 'cs.RO', 'cs.LG', 'stat.ML']
    
    print(f"📥 获取 arXiv 最新论文 (分类: {', '.join(categories)})...")
    
    try:
        import xml.etree.ElementTree as ET
        
        papers = []
        for category in categories:
            try:
                # 使用 arXiv API
                url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req, timeout=30) as r:
                    xml_data = r.read().decode('utf-8')
                
                root = ET.fromstring(xml_data)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    try:
                        arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                        title = entry.find('atom:title', ns).text.strip()
                        summary = entry.find('atom:summary', ns).text.strip()[:500]
                        
                        # 提取版本号后的 ID (例如 2602.12345v1 -> 2602.12345)
                        arxiv_id = re.sub(r'v\d+$', '', arxiv_id)
                        
                        papers.append({
                            'pid': arxiv_id,
                            'title': title,
                            'upvotes': 0,  # arXiv 没有 upvotes，可以后续补充引用数
                            'summary': summary.lower(),
                            'source': f'arXiv ({category})',
                            'url': f"https://arxiv.org/abs/{arxiv_id}"
                        })
                    except Exception as e:
                        continue
                
                print(f"  arXiv {category}: 获取到 {len([p for p in papers if category in p['source']])} 篇")
            
            except Exception as e:
                print(f"❌ arXiv {category} 获取失败: {e}")
                continue
        
        print(f"✅ arXiv: 总共获取到 {len(papers)} 篇论文")
        return papers
    
    except Exception as e:
        print(f"❌ arXiv 获取失败: {e}")
        return []


def fetch_paperswithcode_trending():
    """获取 Papers with Code 热门论文"""
    print(f"📥 获取 Papers with Code 热门论文...")
    
    try:
        # Papers with Code 有一个公开的 API
        url = "https://paperswithcode.com/api/v1/papers/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        
        papers = []
        for item in data.get('results', [])[:30]:
            try:
                # 提取 arXiv ID
                arxiv_url = item.get('arxiv_id', '')
                if not arxiv_url:
                    arxiv_url = item.get('url_abs', '')
                
                arxiv_id = None
                if arxiv_url:
                    match = re.search(r'(\d{4}\.\d{4,5})', arxiv_url)
                    if match:
                        arxiv_id = match.group(1)
                
                if not arxiv_id:
                    continue
                
                papers.append({
                    'pid': arxiv_id,
                    'title': item.get('title', 'N/A'),
                    'upvotes': 0,
                    'summary': item.get('abstract', '')[:500].lower() if item.get('abstract') else '',
                    'source': 'Papers with Code',
                    'url': f"https://arxiv.org/abs/{arxiv_id}"
                })
            except Exception as e:
                continue
        
        print(f"✅ Papers with Code: 获取到 {len(papers)} 篇论文")
        return papers
    
    except Exception as e:
        print(f"❌ Papers with Code 获取失败: {e}")
        return []


def fetch_all_sources():
    """从所有来源获取论文
    
    arXiv 使用针对 AR/眼动追踪/时间预测的分类：
    - cs.CV: 计算机视觉（AR、眼动追踪）
    - cs.HC: 人机交互（AR应用、眼动界面）
    - cs.RO: 机器人学（AR、眼动在机器人中的应用）
    - cs.LG: 机器学习（时间序列预测）
    - stat.ML: 统计机器学习（时间序列、预测）
    """
    all_papers = []
    
    # 1. HuggingFace Papers (扩展到7天)
    all_papers.extend(fetch_huggingface_papers(days=7, max_papers=50))
    
    # 2. arXiv 最新论文 - 使用领域特定的分类
    all_papers.extend(fetch_arxiv_recent(
        categories=['cs.CV', 'cs.HC', 'cs.RO', 'cs.LG', 'stat.ML'],
        max_results=20
    ))
    
    # 3. Papers with Code
    all_papers.extend(fetch_paperswithcode_trending())
    
    return all_papers


def deduplicate_papers(papers, submitted_cache):
    """去重：移除已推送的论文"""
    before_count = len(papers)
    
    # 按 pid 去重（同一论文可能出现在多个来源）
    seen_pids = {}
    for paper in papers:
        pid = paper['pid']
        if pid not in seen_pids:
            seen_pids[pid] = paper
        else:
            # 保留 upvotes 更高的版本
            if paper.get('upvotes', 0) > seen_pids[pid].get('upvotes', 0):
                seen_pids[pid] = paper
    
    papers = list(seen_pids.values())
    
    # 移除已推送的论文
    new_papers = [p for p in papers if p['pid'] not in submitted_cache]
    
    removed = before_count - len(new_papers)
    print(f"🔄 去重: 移除了 {removed} 篇已推送或重复的论文")
    
    return new_papers


def mark_as_submitted(paper_ids, cache_file='submitted_papers.json'):
    """标记论文为已推送"""
    submitted = load_submitted_papers(cache_file)
    
    for pid in paper_ids:
        submitted[pid] = {
            'date': datetime.now().isoformat(),
            'title': ''  # 可以选择存储标题
        }
    
    save_submitted_papers(submitted, cache_file)


if __name__ == '__main__':
    # 测试获取
    papers = fetch_all_sources()
    print(f"\n📊 总计获取: {len(papers)} 篇论文")
    
    # 去重
    cache_file = 'submitted_papers.json'
    submitted = load_submitted_papers(cache_file)
    submitted = clean_old_records(submitted, days=30)
    
    new_papers = deduplicate_papers(papers, submitted)
    print(f"📊 去重后: {len(new_papers)} 篇新论文")
