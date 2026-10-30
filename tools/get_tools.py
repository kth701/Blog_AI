"""
get_tools.py - 커스텀 도구 명세(Tool Definition / Schema) 반환 모듈
"""

import json
from typing import Any, Dict, List


def get_tools() -> List[Dict[str, Any]]:
    """
    에이전트 또는 시스템에서 호출 가능한 커스텀 도구 정의(Schema) 목록을 반환합니다.
    """
    tools: List[Dict[str, Any]] = [
        {
            "name": "blog",
            "description": "참고 자료(텍스트 또는 search.md 파일)를 기반으로 구조화된 마크다운 블로그 포스트(draft.md)를 작성하고 저장합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "블로그 포스트의 주제 또는 제목",
                    },
                    "references": {
                        "type": "string",
                        "description": "참고 자료 내용(텍스트) 또는 참고 자료 파일 경로(예: search.md)",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "저장할 마크다운 파일 경로 (기본값: 'draft.md')",
                        "default": "draft.md",
                    },
                    "image_path": {
                        "type": "string",
                        "description": "포스트에 첨부할 이미지 경로 (기본값: 'image.jpg')",
                        "default": "image.jpg",
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "블로그 카테고리 태그 목록",
                    },
                    "description": {
                        "type": "string",
                        "description": "포스트 요약 설명",
                    },
                },
                "required": ["topic", "references"],
            },
        },
        {
            "name": "publish",
            "description": "작성된 블로그 포스트(post.md 또는 draft.md)와 이미지를 지정된 디렉터리에 배치하고 Quarto HTML(DIRECTORY/index.html)로 변환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_md": {
                        "type": "string",
                        "description": "변환할 원본 마크다운 파일 경로 (기본값: 'post.md')",
                        "default": "post.md",
                    },
                    "directory": {
                        "type": "string",
                        "description": "포스트가 저장될 디렉터리 경로 (기본값: 'posts/notebooklm-featured-notebooks')",
                        "default": "posts/notebooklm-featured-notebooks",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "GitHub Pages 배포용 루트 출력 폴더 (기본값: 'docs')",
                        "default": "docs",
                    },
                },
                "required": [],
            },
        },
    ]
    return tools


if __name__ == "__main__":
    tool_list = get_tools()
    print("=== 등록된 커스텀 도구 목록 (총 {}개) ===".format(len(tool_list)))
    print(json.dumps(tool_list, indent=2, ensure_ascii=False))
