"""
Markdown（含 LaTeX 公式）→ DOCX 统一入口。

读取 .md / .qpad.md 的 YAML 前言区：
- template: <逻辑名>  → handoff/templates/<逻辑名>/reference.docx
无 template 字段时，走无样式的默认 pandoc 输出。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from formula import _source_stem, list_math_in_markdown, md_to_docx, parse_front_matter
from utils import REPO_ROOT, apply_layout, resolve_reference_doc

_DEFAULT_OUTBOX = REPO_ROOT / "outbox"


def compose(src: Path, outbox: Path) -> Path:
    text = src.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)

    template_name: str | None = meta.get("template")
    reference_doc = resolve_reference_doc(template_name) if template_name else None

    math_items = list_math_in_markdown(body)
    print(f"共识别 {len(math_items)} 处公式（$ 行内 / $$ 块级）：")
    for i, (kind, latex) in enumerate(math_items, 1):
        label = "块级" if kind == "display" else "行内"
        preview = latex.replace("\n", " ")
        if len(preview) > 120:
            preview = preview[:117] + "..."
        print(f"  [{i}] {label}: {preview}")

    out_docx = outbox / f"{_source_stem(src)}.docx"
    md_to_docx(src, out_docx, reference_doc)
    layout = meta.get("layout", {})
    if layout:
        apply_layout(out_docx, layout)
    if reference_doc:
        print(f"模板: {reference_doc}")
    print(f"已写入: {out_docx}")
    return out_docx


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Markdown（含 LaTeX 公式）→ DOCX")
    p.add_argument("input_md", type=Path, help="输入 .md 或 .qpad.md 文件路径")
    p.add_argument("-o", "--outbox", type=Path, default=_DEFAULT_OUTBOX,
                   help=f"输出目录（默认: {_DEFAULT_OUTBOX}）")
    args = p.parse_args(argv)

    src = args.input_md
    if not src.is_file():
        print(f"找不到文件: {src}", file=sys.stderr)
        return 1
    if not (src.name.lower().endswith(".md") or src.name.lower().endswith(".qpad.md")):
        print("期望输入扩展名为 .md 或 .qpad.md", file=sys.stderr)
        return 1

    compose(src, args.outbox)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
