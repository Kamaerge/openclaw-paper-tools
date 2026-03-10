#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw nano-pdf Paper Analyzer - 使用 OpenClaw Agent 的 nano-pdf 功能精读论文
"""

import os
import sys
import re
import json
import tempfile
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path


def download_arxiv_pdf(arxiv_id):
    """下载 arXiv 论文 PDF"""
    print(f"📥 下载 arXiv PDF: {arxiv_id}")
    
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # 使用临时目录
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"arxiv_{arxiv_id}.pdf")
    
    try:
        req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            with open(pdf_path, 'wb') as f:
                f.write(r.read())
        
        # 验证文件大小
        file_size = os.path.getsize(pdf_path)
        if file_size < 10000:  # 小于 10KB 可能不是有效 PDF
            print(f"⚠️ PDF 文件太小 ({file_size} bytes)，可能下载失败")
            return None
        
        print(f"✅ 已下载 PDF ({file_size / 1024:.1f} KB) 到 {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None


def analyze_paper_with_nanopdf(arxiv_id, pdf_path, title):
    """使用 OpenClaw Agent nano-pdf 分析论文"""
    print(f"🤖 调用 OpenClaw Agent nano-pdf 分析论文...")
    
    # 构造 prompt，让 Agent 使用 nano-pdf 工具
    # 明确要求完整分析，避免缓存响应
    prompt = f"""【新的分析任务】

请使用 nano-pdf 工具详细分析这篇 arXiv 论文（ID: {arxiv_id}，标题: {title}）。

⚠️ 重要：即使你之前见过这篇论文，也请重新提供完整的深度分析，不要引用之前的对话。

请提供以下分析：
1. **核心贡献**: 论文的主要创新点是什么？
2. **技术方法**: 使用了哪些主要技术方法？
3. **实验亮点**: 有什么令人印象深刻的实验结果或基准？
4. **相关工作**: 与哪些已有工作相关？
5. **局限性**: 论文有哪些潜在的局限或不足？

请用简洁的中文总结（200-300字）。"""
    
    try:
        openclaw_bin = os.environ.get('OPENCLAW_BIN', 'openclaw')
        
        # 使用临时文件传递 PDF 路径和 prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            # nano-pdf 工具调用格式：分析一个本地 PDF 文件
            f.write(f"""分析这个 PDF 文件：{pdf_path}

{prompt}""")
            prompt_file = f.name
        
        try:
            # 调用 openclaw agent，让它使用 nano-pdf 工具
            # 为每次分析创建唯一的 session（包含时间戳），完全避免缓存
            import time
            timestamp = int(time.time())
            session_id = f"paper-{arxiv_id}-{timestamp}"
            cmd = f'{openclaw_bin} agent --local --session-id "{session_id}" --message "@{prompt_file}" --json --thinking medium'
            
            print(f"📝 执行命令: {cmd}")
            print(f"🔑 Session ID: {session_id}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时（PDF 分析可能较慢）
                shell=True
            )
            
            if result.returncode != 0:
                print(f"❌ OpenClaw 调用失败 (exit code {result.returncode})")
                print(f"stderr: {result.stderr[:500]}")
                return None
            
            # 解析 JSON 输出
            try:
                output = json.loads(result.stdout)
                
                # OpenClaw 返回 payloads 列表
                if isinstance(output, dict) and 'payloads' in output:
                    payloads = output.get('payloads', [])
                    # 提取文本内容，跳过 PDF 读取错误的消息
                    analysis_text = []
                    for payload in payloads:
                        if isinstance(payload, dict):
                            text = payload.get('text', '')
                            if text and '二进制格式' not in text and 'PDF 文件' not in text:
                                analysis_text.append(text.strip())
                    
                    if analysis_text:
                        analysis = '\n\n'.join(analysis_text)
                        print(f"\n✅ 分析完成:\n{analysis[:1500]}...")
                        return analysis
                
                # 尝试其他格式
                analysis = output.get('response') or output.get('message') or output.get('result')
                if analysis:
                    print(f"\n✅ 分析完成:\n{analysis}")
                    return analysis
                    
                print(f"⚠️ 无法提取分析内容: {str(output)[:200]}")
                return None
            except json.JSONDecodeError:
                # 可能不是 JSON 格式，直接返回 stdout
                if result.stdout.strip():
                    print(f"\n✅ 分析完成:\n{result.stdout[:1000]}")
                    return result.stdout
                else:
                    print(f"❌ 无响应")
                    return None
        
        finally:
            # 清理临时文件
            try:
                os.unlink(prompt_file)
            except:
                pass
    
    except subprocess.TimeoutExpired:
        print(f"❌ 分析超时 (10分钟)")
        return None
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None


def fetch_arxiv_metadata(arxiv_id):
    """获取 arXiv 论文元数据"""
    print(f"📄 获取论文元数据: {arxiv_id}")
    
    arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
    
    try:
        req = urllib.request.Request(arxiv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
        
        # 提取标题
        title_match = re.search(r'<meta name="citation_title" content="([^"]+)"', html)
        title = title_match.group(1) if title_match else f"arXiv:{arxiv_id}"
        
        # 提取摘要
        abstract_match = re.search(r'<blockquote class="abstract mathjax"[^>]*>.*?<span class="descriptor">Abstract:</span>\s*(.+?)</blockquote>', html, re.DOTALL)
        abstract = ""
        if abstract_match:
            abstract = re.sub(r'<[^>]+>', '', abstract_match.group(1)).strip()
            abstract = re.sub(r'\s+', ' ', abstract)
        
        return {
            'arxiv_id': arxiv_id,
            'title': title,
            'abstract': abstract[:500],
            'arxiv_url': arxiv_url,
            'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        }
        
    except Exception as e:
        print(f"❌ 获取元数据失败: {e}")
        return None


def infer_tags_from_analysis(analysis, title):
    """从分析结果和标题推断标签"""
    text = f"{title} {analysis}".lower()
    tags = []
    
    tag_keywords = {
        'world model': ['world model', 'world modeling'],
        'diffusion': ['diffusion', 'ddpm', 'ddim'],
        'video generation': ['video generation', 'video synthesis', 'temporal'],
        'efficient inference': ['efficient', 'acceleration', 'fast inference', 'optimization'],
        'llm': ['large language model', 'llm', 'gpt', 'transformer language'],
        'quantization': ['quantization', 'int8', 'int4', 'low-bit'],
        'sparse attention': ['sparse attention', 'sparse transformer'],
        'multimodal': ['multimodal', 'vision-language', 'clip'],
        'robotics': ['robot', 'manipulation', 'embodied'],
        'generation': ['generation', 'generative', 'synthesis'],
    }
    
    for tag, keywords in tag_keywords.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    
    return tags[:5]


def split_text_into_blocks(text, max_length=2000):
    """将长文本分割成多个 Notion 块（Notion 每个块有长度限制）"""
    blocks = []
    
    # 首先按照换行符分割段落
    paragraphs = text.split('\n')
    current_block = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # 检查当前块加上新段落是否超过限制
        test_text = current_block + ('\n' if current_block else '') + para
        
        if len(test_text) > max_length:
            # 当前块已满，保存它
            if current_block:
                blocks.append(current_block)
            current_block = para
        else:
            # 添加到当前块
            current_block = test_text
    
    # 保存最后一个块
    if current_block:
        blocks.append(current_block)
    
    return blocks


def create_paragraph_blocks(text_blocks):
    """从文本块列表创建 Notion paragraph 块"""
    blocks = []
    for text in text_blocks:
        if text.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })
    return blocks


def save_to_notion(arxiv_id, metadata, analysis, tags, notion_api_key, notion_db_id):
    """保存完整分析结果到 Notion"""
    print(f"💾 保存到 Notion...")
    
    properties = {
        "Name": {"title": [{"text": {"content": metadata['title'][:2000]}}]},
        "arXiv": {"rich_text": [{"text": {"content": arxiv_id}}]},
        "Link": {"url": metadata['arxiv_url']}
    }
    
    if tags:
        properties["Tags"] = {"multi_select": [{"name": t} for t in tags]}
    
    # 构造页面内容：摘要 + AI 分析
    children = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📄 摘要"}}]
            }
        }
    ]
    
    # 添加摘要段落（可能很长）
    abstract_blocks = split_text_into_blocks(metadata['abstract'], max_length=2000)
    children.extend(create_paragraph_blocks(abstract_blocks))
    
    children.append({
        "object": "block",
        "type": "divider",
        "divider": {}
    })
    
    children.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "🤖 AI 精读分析"}}]
        }
    })
    
    # 添加分析段落（可能很长，需要分割）
    analysis_text = analysis if isinstance(analysis, str) else str(analysis)
    analysis_blocks = split_text_into_blocks(analysis_text, max_length=2000)
    children.extend(create_paragraph_blocks(analysis_blocks))
    
    children.append({
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": [{"type": "text", "text": {"content": "🔗 链接"}}]
        }
    })
    
    children.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": "📖 PDF: "}},
                {"type": "text", "text": {"content": metadata['pdf_url'], "link": {"url": metadata['pdf_url']}}}
            ]
        }
    })
    
    payload = {
        "parent": {"database_id": notion_db_id},
        "properties": properties,
        "children": children
    }
    
    try:
        import urllib.request as ur
        notion_req = ur.Request(
            "https://api.notion.com/v1/pages",
            data=json.dumps(payload).encode(),
            headers={
                'Authorization': f'Bearer {notion_api_key}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
        )
        
        with ur.urlopen(notion_req, timeout=30) as r:
            page_result = json.loads(r.read().decode())
            if 'id' in page_result:
                page_url = f"https://notion.so/{page_result['id'].replace('-', '')}"
                print(f"✅ 已同步到 Notion: {page_url}")
                return page_url
            else:
                print(f"⚠️ Notion 同步失败: {page_result.get('message', '未知错误')}")
                return None
    except ur.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        print(f"❌ Notion API 错误 {e.code}: {error_body[:500]}")
        return None
    except Exception as e:
        print(f"❌ Notion 同步异常: {e}")
        return None


def send_analysis_to_feishu(arxiv_id, metadata, analysis, tags, openclaw_channel, openclaw_target):
    """将分析结果发送到飞书群组"""
    print(f"📤 发送分析结果到飞书群组...")
    
    # 构造消息内容（精简版，飞书消息有长度限制）
    tags_text = f"🏷️ {', '.join(tags)}" if tags else ""
    
    message = f"""📄 论文精读 - {metadata['title'][:80]}

📌 arXiv: {arxiv_id}
{tags_text}

🤖 AI 精读分析:

{analysis[:1500]}{'...' if len(analysis) > 1500 else ''}

🔗 完整信息:
• arXiv: {metadata['arxiv_url']}
• PDF: {metadata['pdf_url']}

---
(由 OpenClaw nano-pdf 自动分析)
"""
    
    try:
        import tempfile
        openclaw_bin = os.environ.get('OPENCLAW_BIN', 'openclaw')
        
        # DEBUG: 打印消息前100个字符
        print(f"📝 准备发送消息 (长度: {len(message)} 字符)")
        print(f"   消息预览: {message[:100]}...")
        
        # 将消息写入临时文件，避免 PowerShell 参数传递问题
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(message)
            msg_file = f.name
        
        try:
            # 使用临时文件而不是直接传递参数
            ps_script = f"""
$msgFile = '{msg_file}'
$msg = Get-Content -Path $msgFile -Raw -Encoding UTF8
& '{openclaw_bin}' message send --channel '{openclaw_channel}' --target '{openclaw_target}' --message $msg --silent
"""
            
            # 使用 PowerShell 执行命令
            result = subprocess.run(
                ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ 已发送到飞书群组")
                return True
            else:
                print(f"⚠️ 飞书发送失败 (exit code: {result.returncode})")
                if result.stderr:
                    print(f"   stderr: {result.stderr[:300]}")
                if result.stdout:
                    print(f"   stdout: {result.stdout[:300]}")
                return False
        finally:
            # 清理临时文件
            try:
                os.unlink(msg_file)
            except:
                pass
    
    except Exception as e:
        print(f"❌ 飞书发送异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_analysis_to_markdown(arxiv_id, metadata, analysis, tags, output_dir='./analysis_results'):
    """将分析结果保存为本地 Markdown 文件"""
    import os
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])[:50]
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    filename = f"{arxiv_id}_{safe_title}.md"
    filepath = os.path.join(output_dir, filename)
    
    # 构造 Markdown 内容
    markdown_content = f"""# {metadata['title']}

**arXiv**: [{arxiv_id}]({metadata['arxiv_url']})  
**PDF**: [Download]({metadata['pdf_url']})  
**Tags**: {', '.join(tags) if tags else 'N/A'}  
**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📄 摘要

{metadata['abstract']}

---

## 🤖 AI 精读分析 (OpenClaw nano-pdf)

{analysis}

---

## 🔗 相关链接

- [arXiv 页面]({metadata['arxiv_url']})
- [PDF 下载]({metadata['pdf_url']})
- [Notion 页面](待同步)

---

*本分析由 OpenClaw Agent nano-pdf 自动生成*
"""
    
    # 写入文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"💾 分析结果已保存到: {filepath}")
        return filepath
    except Exception as e:
        print(f"⚠️ 保存本地文件失败: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("""用法:
    python3 analyze_with_nanopdf.py 2602.23152
    
环境变量:
    NOTION_API_KEY          (可选) Notion API Key
    NOTION_PAPERS_DB_ID     (可选) Notion 数据库 ID
    OPENCLAW_BIN            (可选) OpenClaw 二进制路径，默认 'openclaw'
""")
        sys.exit(1)
    
    arxiv_id = sys.argv[1]
    
    if not re.match(r'^\d{4}\.\d+$', arxiv_id):
        print("❌ 无效的 arXiv ID 格式，应为 YYYY.NNNNN")
        sys.exit(1)
    
    # 获取论文元数据
    metadata = fetch_arxiv_metadata(arxiv_id)
    if not metadata:
        print("❌ 获取元数据失败")
        sys.exit(1)
    
    print(f"\n📄 {metadata['title']}")
    
    # 下载 PDF
    pdf_path = download_arxiv_pdf(arxiv_id)
    if not pdf_path:
        print("❌ 下载 PDF 失败")
        sys.exit(1)
    
    # 使用 nano-pdf 分析
    analysis = analyze_paper_with_nanopdf(arxiv_id, pdf_path, metadata['title'])
    if not analysis:
        print("❌ 分析失败")
        # 清理 PDF
        try:
            os.unlink(pdf_path)
        except:
            pass
        sys.exit(1)
    
    # 推断标签
    tags = infer_tags_from_analysis(analysis, metadata['title'])
    
    # 保存分析结果到本地 Markdown 文件
    local_file = save_analysis_to_markdown(arxiv_id, metadata, analysis, tags)
    
    # 优先发送到飞书群组
    feishu_channel = os.environ.get('OPENCLAW_CHANNEL', 'feishu')
    feishu_target = os.environ.get('OPENCLAW_TARGET')
    
    if feishu_target:
        send_analysis_to_feishu(arxiv_id, metadata, analysis, tags, feishu_channel, feishu_target)
    else:
        print("\n💡 提示: 设置 OPENCLAW_CHANNEL 和 OPENCLAW_TARGET 可发送到飞书群组")
    
    # 可选：保存到 Notion（如果环境变量已设置）
    notion_key = os.environ.get('NOTION_API_KEY')
    notion_db = os.environ.get('NOTION_PAPERS_DB_ID')
    enable_notion = os.environ.get('ENABLE_NOTION_SYNC', '0') == '1'
    
    if notion_key and notion_db and enable_notion:
        save_to_notion(arxiv_id, metadata, analysis, tags, notion_key, notion_db)
    elif notion_key and notion_db:
        print("\n💡 提示: 设置 ENABLE_NOTION_SYNC=1 可同步到 Notion")
    
    # 清理 PDF
    try:
        os.unlink(pdf_path)
    except:
        pass
    
    print("\n✅ 完成!")


if __name__ == '__main__':
    main()
