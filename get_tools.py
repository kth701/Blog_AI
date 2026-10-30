"""
get_tools.py - 최상위 진입점 스크립트
"""

import json
from tools.get_tools import get_tools

if __name__ == "__main__":
    tools = get_tools()
    print("=== [커스텀 도구 목록] ===")
    print(json.dumps(tools, indent=2, ensure_ascii=False))

