"""
qpad.md 质量检查工具。
当前检查项：字数（中文字符，不含代码块）。

用法：
  python desk/check.py handoff/foo.qpad.md
  python desk/check.py handoff/foo.qpad.md --target 7500-8500
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from formula import parse_front_matter

_CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
_CJK = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")


def count_chinese(body: str) -> int:
    """剥离代码块后统计中文字符数。"""
    text = _CODE_BLOCK.sub("", body)
    return len(_CJK.findall(text))


def parse_target(s: str) -> tuple[int, int]:
    """解析 'MIN-MAX' 或单个数字，返回 (min, max)。"""
    s = s.strip()
    if "-" in s:
        parts = s.split("-", 1)
        return int(parts[0]), int(parts[1])
    n = int(s)
    return n, n


def main() -> int:
    parser = argparse.ArgumentParser(description="qpad.md 字数检查")
    parser.add_argument("src", help=".qpad.md 文件路径")
    parser.add_argument("--target", help="目标字数范围，格式 MIN-MAX 或单个数字")
    args = parser.parse_args()

    src = Path(args.src)
    if not src.is_file():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 1

    text = src.read_text(encoding="utf-8")
    _, body = parse_front_matter(text)
    count = count_chinese(body)

    if args.target:
        lo, hi = parse_target(args.target)
        if count < lo:
            print(f"✗ 字数: {count}  目标: {lo}–{hi}（差 {lo - count} 字）")
            return 1
        elif count > hi:
            print(f"⚠ 字数: {count}  目标: {lo}–{hi}（超出 {count - hi} 字）")
            return 0
        else:
            print(f"✓ 字数: {count}  目标: {lo}–{hi}")
            return 0
    else:
        print(f"字数: {count}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
