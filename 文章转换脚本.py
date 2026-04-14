# -*- coding: utf-8 -*-
"""
文章转换脚本：将 剧情/ 文件夹中的 .md 文件，
自动转换为 index.html 所需的 chapters JS 数组格式。
同时检查 配图/ 文件夹中的配图是否存在。

用法：python 文章转换脚本.py
"""

import os
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ========== 配置 ==========
STORY_DIR = r"E:\Opencode\科幻小说\剧情"
IMAGE_DIR = r"E:\Opencode\科幻小说\配图"
HTML_FILE = r"E:\Opencode\科幻小说\index.html"

# 配图文件名映射（按集数）
IMAGE_MAP = {
    "EP01-01": "ep01-01.jpg",
    "EP01-02": "ep01-02.jpg",
}

# .md 文件名解析：EP01-01_标题.md 或 EP01-02_标题.md
CHAPTER_PATTERN = re.compile(r"^(EP\d{2}-\d{2})_(.+)\.md$")

# ========== 工具函数 ==========

def escape_html(text):
    """简单 HTML 转义"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def parse_md(content):
    """
    将简单 Markdown 转为 HTML（单行字符串，\\n 作为换行标记）。
    """
    lines = content.split("\n")
    html_parts = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # 代码块
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            html_parts.append("&lt;code&gt;" + escape_html(stripped) + "&lt;/code&gt;")
            continue

        # 分割线
        if re.match(r"^-{3,}$", stripped):
            html_parts.append("<hr>")
            continue

        # 标题（# 标题）
        m = re.match(r"^# (.+)$", stripped)
        if m:
            html_parts.append("<h1>" + m.group(1) + "</h1>")
            continue

        # 元信息行
        if re.match(r"^\*\*【", stripped):
            text = re.sub(r"\*\*(【[^】]+】)\*\*", r"<b>\1</b>", stripped)
            html_parts.append('<p class="meta">' + text + '</p><hr>')
            continue

        # 引用块
        if stripped.startswith(">"):
            inner = stripped.lstrip("> ").strip()
            inner = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", inner)
            html_parts.append("<p><em>" + inner + "</em></p>")
            continue

        # 强调和转义
        line_html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", stripped)
        line_html = escape_html(line_html)
        line_html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", line_html)

        if line_html:
            html_parts.append("<p>" + line_html + "</p>")

    # JSON 字符串值不能包含未转义的换行，用 \\n 连接
    return "\\n".join(html_parts)


def slug_from_filename(filename):
    m = CHAPTER_PATTERN.match(filename)
    if m:
        return m.group(1)
    return None


def title_from_filename(filename):
    m = CHAPTER_PATTERN.match(filename)
    if m:
        num = m.group(1)
        title = m.group(2).replace("_", "：")
        return num + "：" + title
    return filename


# ========== 主流程 ==========

def main():
    print("=" * 40)
    print("文章转换脚本 - 科幻小说阅读器")
    print("=" * 40)

    # 1. 构建章节数据
    print("\n[1] Scan articles...")
    files = sorted(os.listdir(STORY_DIR))
    chapters = []

    for fname in files:
        slug = slug_from_filename(fname)
        if not slug:
            print("  [SKIP]", fname)
            continue

        md_path = os.path.join(STORY_DIR, fname)
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # 转换 md 为 HTML（已转义换行）
        body_html = parse_md(md_content)

        # 配图路径
        img_name = IMAGE_MAP.get(slug, slug.lower() + ".jpg")
        img_path = "配图/" + img_name

        full_img_path = os.path.join(IMAGE_DIR, img_name)
        if not os.path.exists(full_img_path):
            print("  [WARN] Image missing:", img_path)

        chapter = {
            "title": title_from_filename(fname),
            "image": img_path,
            "text": body_html,
        }
        chapters.append(chapter)
        print("  [OK]", fname, "->", img_path)

    if not chapters:
        print("Error: no chapters found!")
        return

    # 2. 注入 HTML
    print("\n[2] Update index.html...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    chapters_json = json.dumps(chapters, ensure_ascii=False, indent=4)

    # 替换 var chapters = [...] 块
    pattern = r'(var chapters = \[)[\s\S]*?(\];)'
    replacement = r'var chapters = ' + chapters_json

    new_html = re.sub(pattern, replacement, html, count=1)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("\nDone! Total", len(chapters), "chapters")
    print("Run: python verify.py to check output")


if __name__ == "__main__":
    main()
