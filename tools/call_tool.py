"""
tools/call_tool.py - tools 패키지 내부용 도구 실행 디스패처
"""

from typing import Any, Dict
from tools.blog import create_blog_post
from tools.publish import publish_blog_post

TOOL_REGISTRY = {
    "blog": create_blog_post,
    "publish": publish_blog_post,
}


def call_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    지정된 도구 이름(tool_name)에 해당하는 커스텀 도구를 실행합니다.

    Args:
        tool_name (str): 실행할 도구 이름 (예: "blog", "publish")
        **kwargs: 도구 함수에 전달할 매개변수

    Returns:
        Dict[str, Any]: 도구 실행 결과 딕셔너리
    """
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(
            f"지원되지 않는 도구입니다: '{tool_name}'. 가능한 도구 목록: {list(TOOL_REGISTRY.keys())}"
        )

    tool_func = TOOL_REGISTRY[tool_name]
    return tool_func(**kwargs)
