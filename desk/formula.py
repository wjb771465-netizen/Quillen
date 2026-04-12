"""
将含 LaTeX 数学的 Markdown 转为 Word（.docx），并列出识别到的公式片段。
依赖：系统由 conda 提供 pandoc；Python 侧 pypandoc。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 块级公式 $$ ... $$
_DISPLAY = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
# 行内 $ ... $（不与 $$ 混淆）
_INLINE = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.DOTALL)


def _display_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in _DISPLAY.finditer(text)]


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    spans = sorted(spans)
    out = [spans[0]]
    for a, b in spans[1:]:
        la, lb = out[-1]
        if a <= lb:
            out[-1] = (la, max(lb, b))
        else:
            out.append((a, b))
    return out


def _gaps(text: str, occupied: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not occupied:
        return [(0, len(text))]
    occ = _merge_spans(occupied)
    gaps = []
    pos = 0
    for a, b in occ:
        if pos < a:
            gaps.append((pos, a))
        pos = max(pos, b)
    if pos < len(text):
        gaps.append((pos, len(text)))
    return gaps


def _body_after_yaml_front_matter(text: str) -> str:
    """若存在标准 YAML 前言区（首行 --- … 闭合 ---），返回其后正文；否则返回全文。"""
    s = text.lstrip("\ufeff")
    lines = s.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    i = 1
    while i < len(lines):
        if lines[i].strip() == "---":
            return "".join(lines[i + 1 :])
        i += 1
    return text


def _source_stem(path: Path) -> str:
    n = path.name
    if n.lower().endswith(".qpad.md"):
        return n[: -len(".qpad.md")]
    return path.stem


def list_math_in_markdown(text: str) -> list[tuple[str, str]]:
    """
    返回 (kind, latex_body)：
    kind 为 'display' 或 'inline'；latex_body 为不含定界符的公式文本（首尾 strip）。
    顺序为文中出现顺序。
    """
    display_matches = list(_DISPLAY.finditer(text))
    occupied = [(m.start(), m.end()) for m in display_matches]
    found: list[tuple[int, str, str]] = []
    for m in display_matches:
        found.append((m.start(), "display", m.group(1).strip()))
    for ga, gb in _gaps(text, occupied):
        chunk = text[ga:gb]
        offset = ga
        for m in _INLINE.finditer(chunk):
            found.append((offset + m.start(), "inline", m.group(1).strip()))
    found.sort(key=lambda x: x[0])
    return [(k, body) for _, k, body in found]


def md_to_docx(src_md: Path, out_docx: Path) -> None:
    import pypandoc

    out_docx.parent.mkdir(parents=True, exist_ok=True)
    text = src_md.read_text(encoding="utf-8")
    pypandoc.convert_text(
        text,
        "docx",
        format="md",
        outputfile=str(out_docx),
        extra_args=["--standalone"],
    )


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    default_outbox = root / "outbox"

    p = argparse.ArgumentParser(description="Markdown（含 LaTeX 公式）→ DOCX，并列出公式。")
    p.add_argument("input_md", type=Path, help="输入 .md 文件路径")
    p.add_argument(
        "-o",
        "--outbox",
        type=Path,
        default=default_outbox,
        help=f"输出目录（默认: {default_outbox}）",
    )
    args = p.parse_args(argv)

    src = args.input_md
    if not src.is_file():
        print(f"找不到文件: {src}", file=sys.stderr)
        return 1
    suf = src.name.lower()
    if not (suf.endswith(".md") or suf.endswith(".qpad.md")):
        print("期望输入扩展名为 .md 或 .qpad.md", file=sys.stderr)
        return 1

    text = src.read_text(encoding="utf-8")
    math_items = list_math_in_markdown(_body_after_yaml_front_matter(text))
    print(f"共识别 {len(math_items)} 处公式（$ 行内 / $$ 块级）：")
    for i, (kind, body) in enumerate(math_items, 1):
        label = "块级" if kind == "display" else "行内"
        preview = body.replace("\n", " ")
        if len(preview) > 120:
            preview = preview[:117] + "..."
        print(f"  [{i}] {label}: {preview}")

    out_docx = args.outbox / f"{_source_stem(src)}.docx"
    md_to_docx(src, out_docx)
    print(f"已写入: {out_docx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
