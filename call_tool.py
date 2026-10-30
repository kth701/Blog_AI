"""
call_tool.py - 도구 이름과 인자를 받아 커스텀 도구를 호출/실행하는 디스패처 스크립트
"""

import argparse
import json
from typing import Any, Dict

from tools.blog import create_blog_post
from tools.publish import publish_blog_post

# 지원하는 도구 레지스트리 매핑
TOOL_REGISTRY = {
    "blog": create_blog_post,
    "publish": publish_blog_post,
}


def call_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    지정된 도구 이름(tool_name)에 해당하는 커스텀 도구를 실행합니다.
    """
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(
            f"지원되지 않는 도구입니다: '{tool_name}'. 지원 목록: {list(TOOL_REGISTRY.keys())}"
        )

    tool_func = TOOL_REGISTRY[tool_name]
    return tool_func(**kwargs)


def _cli_entrypoint():
    parser = argparse.ArgumentParser(
        description="커스텀 도구(Custom Tool) 실행 디스패처"
    )
    parser.add_argument(
        "tool",
        nargs="?",
        default="blog",
        choices=list(TOOL_REGISTRY.keys()),
        help="실행할 도구 이름 (blog 또는 publish)",
    )
    parser.add_argument("--topic", type=str, help="블로그 주제 또는 제목")
    parser.add_argument(
        "--references",
        type=str,
        help="참고 자료 텍스트 또는 파일 경로 (예: search.md)",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        type=str,
        default="draft.md",
        help="저장할 마크다운 파일 경로 (기본값: draft.md)",
    )
    parser.add_argument(
        "--image",
        dest="image_path",
        type=str,
        default="image.jpg",
        help="이미지 경로 (기본값: image.jpg)",
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        default=None,
        help="카테고리 목록 (공백으로 구분)",
    )
    parser.add_argument(
        "--source-md",
        dest="source_md",
        type=str,
        default="post.md",
        help="[publish 전용] 변환할 마크다운 파일 (기본값: post.md)",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="posts/notebooklm-featured-notebooks",
        help="[publish 전용] 포스트 디렉터리 (기본값: posts/notebooklm-featured-notebooks)",
    )

    args = parser.parse_args()

    if args.tool == "publish":
        result = call_tool(
            tool_name="publish",
            source_md=args.source_md,
            directory=args.directory,
        )
    else:
        if not args.topic or not args.references:
            print("💡 [안내] 별도의 옵션이 전달되지 않아 기본 샘플로 blog 도구를 실행합니다.")
            sample_topic = "Quarto와 GitHub Pages를 활용한 블로그 자동화"
            sample_ref = (
                "Quarto는 마크다운 문서를 정적 블로그나 웹사이트로 손쉽게 변환해 주는 도구입니다.\n"
                "GitHub Pages를 이용해 웹상에 무료로 간편하게 호스팅할 수 있습니다.\n"
                "공식 문서: https://quarto.org"
            )
            result = call_tool(
                tool_name="blog",
                topic=sample_topic,
                references=sample_ref,
                output_path=args.output_path,
                image_path=args.image_path,
                categories=args.categories or ["Automation", "Quarto"],
            )
        else:
            result = call_tool(
                tool_name=args.tool,
                topic=args.topic,
                references=args.references,
                output_path=args.output_path,
                image_path=args.image_path,
                categories=args.categories,
            )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _cli_entrypoint()
