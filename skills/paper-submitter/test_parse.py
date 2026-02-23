import re

def load_submissions():
    """加载历史提交记录"""
    SUBMISSIONS_LOG = "submitted_papers.md"
    
    if not os.path.exists(SUBMISSIONS_LOG):
        return []
    
    try:
        with open(SUBMISSIONS_LOG, 'r') as f:
            content = f.read()
            papers = []
            # 解析 markdown 表格
            lines = content.split('\n')
            for line in lines[3:]:  # 跳过表头
                if line.strip().startswith('|') and 'arxiv.org' in line:
                    parts = line.split('|')
                    print(f"Parts: {parts}")
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

papers = load_submissions()
print(f"\n找到 {len(papers)} 篇论文:\n")
for i, p in enumerate(papers, 1):
    print(f"{i}. [{p['hf_id']}] {p['title'][:40]}...")
