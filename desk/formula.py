"""
Markdown 数学公式识别与 md→docx 转换库。
依赖：系统由 conda 提供 pandoc；Python 侧 pypandoc、pyyaml。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

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
    if n.lower().endswith(".auto.qpad.md"):
        return n[: -len(".auto.qpad.md")]
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


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """
    解析 YAML 前言区，返回 (meta, body)。
    无前言时 meta 为空字典，body 为全文。
    """
    import yaml

    s = text.lstrip("\ufeff")
    lines = s.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    i = 1
    while i < len(lines):
        if lines[i].strip() == "---":
            meta = yaml.safe_load("".join(lines[1:i])) or {}
            return meta, "".join(lines[i + 1 :])
        i += 1
    return {}, text


def md_to_docx(src_md: Path, out_docx: Path, reference_doc: Path | None = None) -> None:
    import pypandoc

    out_docx.parent.mkdir(parents=True, exist_ok=True)
    text = src_md.read_text(encoding="utf-8")
    extra_args = ["--standalone"]
    if reference_doc is not None:
        extra_args.append(f"--reference-doc={reference_doc}")
    pypandoc.convert_text(
        text,
        "docx",
        format="md",
        outputfile=str(out_docx),
        extra_args=extra_args,
    )
