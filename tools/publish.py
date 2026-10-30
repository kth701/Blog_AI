"""
publish.py - 마크다운 블로그 포스트(post.md / draft.md)를 Quarto 프로젝트 구조에 배치하고
HTML(DIRECTORY/index.html)로 변환하는 퍼블리싱 도구
"""

import html
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _parse_frontmatter(md_text: str) -> Tuple[Dict[str, Any], str]:
    """YAML 프론트매터와 마크다운 본문을 분리합니다."""
    meta: Dict[str, Any] = {
        "title": "Blog Post",
        "date": "",
        "categories": [],
        "image": "",
        "description": "",
    }
    body = md_text
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md_text, re.DOTALL)
    if fm_match:
        fm_raw, body = fm_match.group(1), fm_match.group(2)
        for line in fm_raw.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key == "categories":
                    cats = re.findall(r'"([^"]+)"|\'([^\']+)\'|([^,\[\]\s]+)', val)
                    meta["categories"] = [
                        next( group for group in c if group ) for c in cats if any(c)
                    ]
                else:
                    meta[key] = val
    return meta, body


def _markdown_to_html_body(md_body: str) -> Tuple[str, List[Tuple[str, str, int]]]:
    """
    마크다운 본문을 깔끔한 Quarto 스타일 HTML 본문과 목차(TOC) 리스트로 변환합니다.
    """
    lines = md_body.splitlines()
    html_lines: List[str] = []
    toc: List[Tuple[str, str, int]] = []
    in_list = False

    def format_inline(text: str) -> str:
        # 이미지 변환: ![alt](src)
        text = re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)",
            r'<figure class="figure my-4"><img src="\2" alt="\1" class="figure-img img-fluid rounded shadow-sm"><figcaption class="figure-caption text-center mt-2">\1</figcaption></figure>',
            text,
        )
        # 꺾쇠 링크: <https://...>
        text = re.sub(
            r"<(https?://[^>]+)>",
            r'<a href="\1" target="_blank" rel="noopener">\1</a>',
            text,
        )
        # 일반 링크: [text](url)
        text = re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+)\)",
            r'<a href="\2" target="_blank" rel="noopener">\1</a>',
            text,
        )
        # 굵게: **text**
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        # 기울임: *text*
        text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
        # 인라인 코드: `code`
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        return text

    sec_idx = 0
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        if line == "---":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append('<hr class="my-4">')
            continue

        # 헤딩 처리
        h_match = re.match(r"^(#{2,3})\s+(.+)$", line)
        if h_match:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            level = len(h_match.group(1))
            title_text = h_match.group(2).strip()
            sec_idx += 1
            anchor_id = f"section-{sec_idx}"
            toc.append((anchor_id, title_text, level))
            html_lines.append(
                f'<h{level} id="{anchor_id}" class="anchored mt-4 mb-3">{format_inline(title_text)}</h{level}>'
            )
            continue

        # 리스트 처리 (- 또는 1.)
        li_match = re.match(r"^(?:[-*]|\d+\.)\s+(.+)$", line)
        if li_match:
            if not in_list:
                html_lines.append('<ul class="list-group-flush ps-3 mb-3">')
                in_list = True
            html_lines.append(f'<li class="mb-2">{format_inline(li_match.group(1))}</li>')
            continue

        # 일반 문단 또는 이미지 단독 줄
        if in_list:
            html_lines.append("</ul>")
            in_list = False

        if line.startswith("!["):
            html_lines.append(format_inline(line))
        else:
            html_lines.append(f"<p>{format_inline(line)}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines), toc


def _build_quarto_html(meta: Dict[str, Any], body_html: str, toc: List[Tuple[str, str, int]]) -> str:
    """Quarto Cosmo 테마 스타일의 반응형 HTML 문서를 생성합니다."""
    title = html.escape(meta.get("title", "Blog Post"))
    date = html.escape(meta.get("date", ""))
    desc = html.escape(meta.get("description", ""))
    categories = meta.get("categories", [])

    badges_html = " ".join(
        [
            f'<span class="badge bg-primary bg-opacity-10 text-primary border border-primary-subtle me-1">{html.escape(c)}</span>'
            for c in categories
        ]
    )

    toc_items = []
    for anchor_id, sec_title, level in toc:
        indent_cls = "ms-3 small" if level == 3 else "fw-semibold"
        toc_items.append(
            f'<li class="nav-item {indent_cls}"><a class="nav-link py-1 text-secondary" href="#{anchor_id}">{html.escape(sec_title)}</a></li>'
        )
    toc_html = "\n".join(toc_items)

    return f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="ko" xml:lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes" />
  <meta name="dcterms.date" content="{date}" />
  <meta name="description" content="{desc}" />
  <title>{title} – Antigravity AI Tech Blog</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif;
      line-height: 1.75;
      color: #212529;
      background-color: #ffffff;
    }}
    .quarto-title-banner {{
      background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
      color: #ffffff;
      padding: 3.5rem 0 2.5rem 0;
      margin-bottom: 2.5rem;
    }}
    .quarto-title-banner .description {{
      color: rgba(255, 255, 255, 0.85);
      font-size: 1.1rem;
    }}
    main.content h2 {{
      border-bottom: 2px solid #eef2f6;
      padding-bottom: 0.5rem;
      color: #1e293b;
      font-weight: 700;
    }}
    main.content h3 {{
      color: #334155;
      font-weight: 600;
    }}
    figure img {{
      max-width: 100%;
      height: auto;
      border-radius: 12px;
    }}
    .toc-sidebar {{
      position: sticky;
      top: 2rem;
      border-left: 2px solid #e2e8f0;
      padding-left: 1rem;
    }}
    .toc-sidebar .nav-link:hover {{
      color: #2563eb !important;
    }}
    code {{
      background-color: #f1f5f9;
      padding: 0.2em 0.4em;
      border-radius: 4px;
      color: #0f172a;
    }}
  </style>
</head>
<body>
  <!-- Navbar -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <a class="navbar-brand fw-bold" href="../index.html">Antigravity AI Tech Blog</a>
    </div>
  </nav>

  <!-- Title Banner -->
  <header class="quarto-title-banner">
    <div class="container">
      <div class="mb-2">{badges_html}</div>
      <h1 class="title display-6 fw-bold mb-3">{title}</h1>
      <p class="description mb-3">{desc}</p>
      <div class="small text-white-50">작성일: {date}</div>
    </div>
  </header>

  <!-- Main Content & TOC -->
  <div class="container mb-5">
    <div class="row">
      <main class="content col-lg-9 pe-lg-5">
        {body_html}
      </main>
      <aside class="col-lg-3 d-none d-lg-block">
        <nav class="toc-sidebar">
          <h6 class="text-uppercase text-muted fw-bold small mb-2">목차 (On this page)</h6>
          <ul class="nav flex-column">
            {toc_html}
          </ul>
        </nav>
      </aside>
    </div>
  </div>

  <footer class="border-top py-4 mt-5 bg-light text-center text-muted small">
    <div class="container">
      Powered by Quarto &amp; Antigravity Blog Automation Pipeline
    </div>
  </footer>
</body>
</html>
"""


def publish_blog_post(
    source_md: str = "post.md",
    directory: str = "posts/notebooklm-featured-notebooks",
    output_dir: str = "docs",
) -> Dict[str, Any]:
    """
    작성된 마크다운 포스트(post.md 또는 draft.md)와 이미지를 지정된 DIRECTORY에 배치하고
    Quarto HTML(DIRECTORY/index.html)로 변환합니다.
    """
    src_path = Path(source_md)
    if not src_path.exists():
        raise FileNotFoundError(f"원본 마크다운 파일을 찾을 수 없습니다: {source_md}")

    md_text = src_path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(md_text)

    # 1. 대상 포스트 디렉터리(DIRECTORY) 생성 및 에셋 복사
    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)

    # index.qmd 및 원본 복사
    (target_dir / "index.qmd").write_text(md_text, encoding="utf-8")
    if src_path.resolve() != (target_dir / src_path.name).resolve():
        shutil.copy2(src_path, target_dir / src_path.name)

    # 본문에 참조된 이미지 파일 복사
    referenced_images = set(re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md_text))
    if meta.get("image"):
        referenced_images.add(meta["image"])

    copied_images: List[str] = []
    for img_name in referenced_images:
        img_src = Path(img_name)
        if img_src.exists() and img_src.is_file():
            dst_img = target_dir / img_src.name
            if img_src.resolve() != dst_img.resolve():
                shutil.copy2(img_src, dst_img)
            copied_images.append(img_src.name)

    # 2. Quarto CLI 설치 여부 확인 후 렌더링 수행
    quarto_bin = shutil.which("quarto")
    render_method = "builtin-quarto-renderer"

    if quarto_bin:
        try:
            subprocess.run(
                [quarto_bin, "render", str(target_dir / "index.qmd")],
                check=True,
                capture_output=True,
                text=True,
            )
            render_method = "quarto-cli"
        except Exception:
            render_method = "builtin-quarto-renderer"

    # HTML 파일 생성 (DIRECTORY/index.html)
    body_html, toc = _markdown_to_html_body(body)
    full_html = _build_quarto_html(meta, body_html, toc)

    index_html_path = target_dir / "index.html"
    index_html_path.write_text(full_html, encoding="utf-8")

    # 3. GitHub Pages 배포용 docs/ 폴더 동기화
    docs_root = Path(output_dir)
    docs_post_dir = docs_root / directory
    docs_post_dir.mkdir(parents=True, exist_ok=True)
    (docs_post_dir / "index.html").write_text(full_html, encoding="utf-8")
    for img_name in copied_images:
        shutil.copy2(target_dir / img_name, docs_post_dir / img_name)

    # 메인 블로그 인덱스(docs/index.html) 생성
    thumb_src = f"{directory}/{meta.get('image', 'blog_image_001.png')}"
    main_index_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Antigravity AI Tech Blog</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <nav class="navbar navbar-dark bg-dark mb-4">
    <div class="container">
      <a class="navbar-brand fw-bold" href="index.html">Antigravity AI Tech Blog</a>
    </div>
  </nav>
  <div class="container py-4">
    <h1 class="fw-bold mb-2">Antigravity AI Tech Blog</h1>
    <p class="text-muted mb-4">AI 기반 자료 수집부터 블로그 글 작성, Quarto 퍼블리싱까지 자동화된 기술 블로그입니다.</p>
    <div class="card shadow-sm border-0 overflow-hidden mb-4">
      <div class="row g-0 align-items-center">
        <div class="col-md-4">
          <img src="{thumb_src}" class="img-fluid rounded-start" alt="{html.escape(meta.get('title', ''))}">
        </div>
        <div class="col-md-8">
          <div class="card-body p-4">
            <div class="small text-muted mb-2">{html.escape(meta.get('date', ''))}</div>
            <h3 class="card-title h4 fw-bold">
              <a href="{directory}/index.html" class="text-decoration-none text-dark stretched-link">{html.escape(meta.get('title', ''))}</a>
            </h3>
            <p class="card-text text-secondary mt-2">{html.escape(meta.get('description', ''))}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""
    (docs_root / "index.html").write_text(main_index_html, encoding="utf-8")

    return {
        "status": "success",
        "tool": "publish",
        "render_method": render_method,
        "post_html": str(index_html_path.resolve()),
        "docs_post_html": str((docs_post_dir / "index.html").resolve()),
        "docs_index_html": str((docs_root / "index.html").resolve()),
        "copied_images": copied_images,
        "message": f"'{source_md}'가 '{directory}/index.html' 및 '{output_dir}/{directory}/index.html'로 성공적으로 변환되었습니다.",
    }

