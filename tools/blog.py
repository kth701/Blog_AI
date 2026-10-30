"""
blog.py - 참고 자료 기반 블로그 포스트 작성 및 마크다운 저장 커스텀 도구
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _load_reference_content(references: str) -> str:
    """
    참고 자료가 파일 경로인 경우 해당 파일의 내용을 읽어오고,
    일반 텍스트인 경우 그대로 반환합니다.
    """
    if os.path.exists(references) and os.path.isfile(references):
        try:
            with open(references, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            return f"[파일 읽기 오류 ({references}): {e}]"
    return references.strip()


def _extract_references_urls(content: str) -> List[str]:
    """텍스트 내 포함된 URL 목록을 추출합니다."""
    url_pattern = r"https?://[^\s)\]>]+"
    return sorted(list(set(re.findall(url_pattern, content))))


def create_blog_post(
    topic: str,
    references: str,
    output_path: str = "draft.md",
    image_path: str = "image.jpg",
    categories: Optional[List[str]] = None,
    description: Optional[str] = None,
    body_markdown: Optional[str] = None,
) -> Dict[str, Any]:
    """
    참고 자료를 기반으로 구조화된 블로그 포스트를 작성하고 마크다운(.md) 파일로 저장합니다.

    Args:
        topic (str): 블로그 포스트 제목 또는 핵심 주제
        references (str): 참고 자료 텍스트 또는 참고 자료 파일 경로(예: search.md)
        output_path (str): 저장할 마크다운 파일 경로 (기본값: "draft.md")
        image_path (str): 블로그 대표 이미지 경로 (기본값: "image.jpg")
        categories (Optional[List[str]]): 포스트 카테고리 목록
        description (Optional[str]): 포스트 요약 설명 (생략 시 자동 생성)
        body_markdown (Optional[str]): 직접 구성한 본문 마크다운 (지정 시 해당 본문 사용)

    Returns:
        Dict[str, Any]: 실행 결과 상태, 저장 경로, 글자 수, 메타데이터 등
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    ref_body = _load_reference_content(references)

    if not categories:
        categories = ["AI", "Google", "NotebookLM", "Tech"]

    if not description:
        cleaned_first_line = ref_body.replace("#", "").strip().split("\n")[0]
        description = (
            cleaned_first_line[:120] + "..."
            if len(cleaned_first_line) > 120
            else cleaned_first_line
        )
        if not description:
            description = f"{topic}에 대한 핵심 요약과 상세 분석 아티클입니다."

    categories_yaml = "[" + ", ".join([f'"{c}"' for c in categories]) + "]"

    urls = _extract_references_urls(ref_body)
    ref_links_md = ""
    if urls:
        ref_links_md = "\n".join([f"- <{url}>" for url in urls])

    if body_markdown:
        main_content = body_markdown.strip()
    else:
        main_content = f"""## 1. 도입

혹시 새로운 분야를 공부하거나 리서치를 시작할 때, **"어떤 자료부터 찾아서 읽어야 할지 막막했던 경험"**이 있으신가요?
오늘 살펴볼 **{topic}**은 바로 그 고민에 대한 명쾌한 해답을 제시합니다.

---

## 2. 핵심 요약

바쁜 독자분들을 위해 가장 중요한 핵심 포인트 3가지를 먼저 정리해 드립니다.

1. **전문가·주요 기관의 사전 큐레이션**: 직접 문서를 모을 필요 없이 검증된 고품질 소스를 즉시 탐색할 수 있습니다.
2. **멀티모달 AI 분석 도구의 즉각적인 활용**: AI 오디오 오버뷰(팟캐스트), 인터랙티브 마인드맵, 출처 기반 질의응답이 사전 준비되어 있습니다.
3. **안전한 탐색과 지식 공유 생태계 확장**: 읽기 전용 환경에서 원문 훼손 걱정 없이 학습하고 공개 노트북 생태계와 연결됩니다.

---

## 3. 상세 설명

{ref_body}

---

## 4. 마무리

지금까지 **{topic}**의 핵심 기능과 활용 가치를 살펴보았습니다.
단순히 문서를 읽는 것을 넘어 검증된 지식과 대화하는 새로운 패러다임이 앞으로 우리의 학습과 리서치 방식을 어떻게 변화시킬지 기대됩니다.

---

## 참고 자료 (References)

{ref_links_md if ref_links_md else "- 수집된 원본 자료 및 검색 결과 기반 작성"}"""

    markdown_content = f"""---
title: "{topic}"
date: "{today_str}"
categories: {categories_yaml}
image: "{image_path}"
description: "{description}"
---

{main_content}
"""

    target_file = Path(output_path)
    target_file.parent.mkdir(parents=True, exist_ok=True)

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return {
        "status": "success",
        "tool": "blog",
        "output_path": str(target_file.resolve()),
        "relative_path": output_path,
        "title": topic,
        "date": today_str,
        "categories": categories,
        "char_count": len(markdown_content),
        "message": f"블로그 포스트 초안이 '{output_path}'에 성공적으로 저장되었습니다.",
    }
