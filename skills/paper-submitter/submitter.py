#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper Submitter - 提交论文到 SwiftScholar (aipaper.cc)

功能:
- 提交 Hugging Face 论文到 SwiftScholar 进行 AI 精读
- 自动维护提交记录 (submitted_papers.md)
- 支持查询历史提交

使用方法:
    # 提交论文
    python3 submitter.py 2601.22954
    
    # 查询历史
    python3 submitter.py --list
    
    # 保存 API Key
    python3 submitter.py --save-key YOUR_API_KEY
"""

import os
import sys
import re
import json
import urllib.request
from datetime import datetime

# 配置
BASE_URL = "https://www.swiftscholar.net"
API_BASE = f"{BASE_URL}/api/tools"
CONFIG_FILE = os.path.expanduser("~/.config/swiftscholar/api_key.txt")

# 记录文件
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SUBMISSIONS_LOG = os.path.join(SCRIPT_DIR, "submitted_papers.md")

def get_api_key():
    """获取 API Key"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            key = f.read().strip()
            if key:
                return key
    
    key = os.environ.get('SWIFTSCHOLAR_API_KEY')
    if key:
        return key
    
    return None

def save_api_key(key):
    """保存 API Key"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        f.write(key)
    print(f"✅ API Key 已保存到: {CONFIG_FILE}")

def get_paper_info(hf_id):
    """获取 HF 论文信息"""
    print(f"📥 获取论文信息: {hf_id}")
    
    try:
        url = f"https://huggingface.co/papers/{hf_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode()
            
            title_match = re.search(r'<title>(.+?)</title>', html)
            title = title_match.group(1).replace(' - Hugging Face', '').strip() if title_match else ''
            
            arxiv_match = re.search(r'arxiv:(\d{4}\.\d+)', html)
            arxiv_id = arxiv_match.group(1) if arxiv_match else hf_id
            
            return {
                'hf_id': hf_id,
                'title': title,
                'arxiv_id': arxiv_id,
                'arxiv_url': f'https://arxiv.org/abs/{arxiv_id}'
            }
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return None

def load_submissions():
    """加载历史提交记录"""
    if not os.path.exists(SUBMISSIONS_LOG):
        return []
    
    try:
        with open(SUBMISSIONS_LOG, 'r') as f:
            content = f.read()
            papers = []
            lines = content.split('\n')
            for line in lines[3:]:  # 跳过表头
                if line.strip().startswith('|') and 'swiftscholar' in line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        hf_id = parts[1].strip()
                        title = parts[2].strip()
                        swiftscholar_url = parts[3].strip()
                        date = parts[4].strip()
                        papers.append({
                            'hf_id': hf_id,
                            'title': title,
                            'swiftscholar_url': swiftscholar_url,
                            'date': date
                        })
            return papers
    except Exception as e:
        print(f"⚠️ 读取历史记录失败: {e}")
        return []

def save_submission(paper_info, swiftscholar_url):
    """保存提交记录到 markdown 和 Notion"""
    date = datetime.now().strftime('%Y-%m-%d %H:%M')

    title_short = paper_info['title'][:58] + ".." if len(paper_info['title']) > 60 else paper_info['title']
    new_entry = f"| {paper_info['hf_id']} | {title_short} | {swiftscholar_url} | {date} |"

    if not os.path.exists(SUBMISSIONS_LOG):
        header = f"""# 已提交论文记录

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 提交记录

| ID | 标题 | 精读链接 | 提交时间 |
|----|------|----------|----------|
"""
        with open(SUBMISSIONS_LOG, 'w') as f:
            f.write(header + new_entry + '\n')
    else:
        with open(SUBMISSIONS_LOG, 'r') as f:
            content = f.read()

        content = re.sub(
            r'\*\*最后更新\*\*: \d{4}-\d{2}-\d{2} \d{2}:\d{2}',
            f'**最后更新**: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            content
        )

        lines = content.split('\n')
        insert_idx = 4
        lines.insert(insert_idx, new_entry)

        with open(SUBMISSIONS_LOG, 'w') as f:
            f.write('\n'.join(lines))

    print(f"\n📝 已记录到: {SUBMISSIONS_LOG}")

    # ========== Notion 集成 ==========
    add_to_notion(paper_info, swiftscholar_url, date)


def add_to_notion(paper_info, swiftscholar_url, date):
    """添加到 Notion 数据库 (自动执行)"""
    notion_key = os.environ.get('NOTION_API_KEY')
    if not notion_key:
        print("\n⚠️ 未配置 NOTION_API_KEY，跳过 Notion 同步")
        return

    # Notion 数据库 ID (从环境变量读取)
    notion_db_id = os.environ.get('NOTION_PAPERS_DB_ID')
    if not notion_db_id:
        print("\n⚠️ 未配置 NOTION_PAPERS_DB_ID，跳过 Notion 同步")
        return

    # 构建属性
    properties = {
        "Name": {"title": [{"text": {"content": paper_info['title'][:2000]}}]},
        "Date": {"date": {"start": date.split()[0]}},
        "arXiv": {"rich_text": [{"text": {"content": paper_info['arxiv_id']}}]},
        "Link": {"url": swiftscholar_url}
    }

    # 提取标签 (简化处理: 从标题推断)
    tags = infer_tags(paper_info['title'])
    if tags:
        properties["Tags"] = {"multi_select": [{"name": t} for t in tags]}

    payload = {
        "parent": {"database_id": notion_db_id},
        "properties": properties
    }

    try:
        import urllib.request
        notion_req = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=json.dumps(payload).encode(),
            headers={
                'Authorization': f'Bearer {notion_key}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
        )

        with urllib.request.urlopen(notion_req, timeout=10) as r:
            result = json.loads(r.read().decode())
            if 'id' in result:
                print(f"✅ 已同步到 Notion: https://notion.so/{result['id'].replace('-', '')}")
            else:
                print(f"\n⚠️ Notion 同步失败: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"\n⚠️ Notion 同步异常: {e}")


def infer_tags(title):
    """从标题推断论文标签"""
    title_lower = title.lower()
    tags = []

    tag_keywords = {
        'speculative decoding': ['speculative decoding', 'eagle', 'draft'],
        'efficient inference': ['efficient', 'acceleration', 'optimization', 'quantization'],
        'video generation': ['video', 'diffusion', 'temporal'],
        'llm inference': ['llm', 'language model', 'inference'],
        'robotics': ['robot', 'manipulation', 'control'],
        'vla': ['vla', 'vision-language-action'],
        'parallelization': ['parallel', 'distributed'],
        'memory optimization': ['memory', 'kv cache', 'cache'],
        'sparse attention': ['sparse', 'attention'],
    }

    for tag, keywords in tag_keywords.items():
        if any(kw in title_lower for kw in keywords):
            tags.append(tag)

    return tags[:5]  # 最多5个标签

def list_submissions():
    """列出所有历史提交"""
    papers = load_submissions()
    
    if not papers:
        print("📭 暂无提交记录")
        return
    
    print(f"\n📚 历史提交记录 ({len(papers)} 篇):\n")
    print("-" * 80)
    
    for i, paper in enumerate(papers, 1):
        title = paper['title'][:50] + "..." if len(paper['title']) > 50 else paper['title']
        print(f"{i}. [{paper['hf_id']}] {title}")
        print(f"   📄 {paper['swiftscholar_url']}")
        print(f"   📅 {paper['date']}")
        print()
    
    print("-" * 80)
    print(f"\n📄 完整记录: {SUBMISSIONS_LOG}")

def submit_paper(arxiv_url, api_key):
    """提交论文到 SwiftScholar"""
    print(f"📤 提交论文: {arxiv_url}")
    
    endpoint = f"{API_BASE}/paper_submit_url"
    
    data = json.dumps({
        "url": arxiv_url,
        "force": False
    }).encode()
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        req = urllib.request.Request(endpoint, data=data, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read().decode())
            
            if result.get('ok'):
                paper_id = result.get('data', {}).get('id') or arxiv_url.split('/')[-1]
                print(f"✅ 提交成功!")
                return f"{BASE_URL}/paper/{paper_id}"
            else:
                print(f"⚠️ 提交结果: {result}")
                return f"{BASE_URL}/paper/{arxiv_url.split('/')[-1]}"
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ API 错误 ({e.code}): {error_body[:300]}")
        return None

def main():
    api_key = None
    hf_id = None
    list_mode = False
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == '--api-key' and i < len(sys.argv):
            api_key = sys.argv[i + 1]
        elif arg == '--save-key' and i < len(sys.argv):
            save_api_key(sys.argv[i + 1])
            sys.exit(0)
        elif arg == '--list' or arg == '-l':
            list_mode = True
        elif arg.startswith('-'):
            continue
        else:
            hf_id = arg
    
    if list_mode:
        list_submissions()
        sys.exit(0)
    
    if not hf_id:
        print("""❌ 用法:
    
    # 提交论文
    python3 submitter.py 2601.22954
    
    # 查询历史提交
    python3 submitter.py --list
    
    # 保存 API Key
    python3 submitter.py --save-key YOUR_API_KEY
""")
        sys.exit(1)
    
    if not re.match(r'^\d{4}\.\d+$', hf_id):
        print("❌ 无效的论文编号格式，应为 YYYY.NNNNN")
        sys.exit(1)
    
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        print("""
⚠️ 需要 API Key！

获取方式:
1. 打开 https://www.swiftscholar.net/swagger
2. 点击页面顶部的 "Authorize" 按钮
3. 复制显示的 API Key

使用方法:
   python3 submitter.py 2601.22954 --api-key YOUR_API_KEY
   
   或保存到配置文件:
   python3 submitter.py --save-key YOUR_API_KEY
""")
        sys.exit(1)
    
    print("✅ 已加载 API Key")
    
    paper_info = get_paper_info(hf_id)
    if not paper_info:
        print("❌ 无法获取论文信息")
        sys.exit(1)
    
    print(f"\n📄 论文信息:")
    print(f"   ID: {paper_info['hf_id']}")
    title_display = paper_info['title'][:50] + "..." if len(paper_info['title']) > 50 else paper_info['title']
    print(f"   标题: {title_display}")
    
    result_url = submit_paper(paper_info['arxiv_url'], api_key)
    
    if result_url:
        print(f"\n✅ 完成!")
        print(f"🔗 {result_url}")
        save_submission(paper_info, result_url)
    else:
        print(f"\n⚠️ 提交失败")

if __name__ == '__main__':
    main()
