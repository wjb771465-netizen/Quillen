"""
仓库路径工具。
"""
from __future__ import annotations

import io
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_ROOT = REPO_ROOT / "handoff" / "templates"


def resolve_reference_doc(template_name: str) -> Path:
    """
    将模板逻辑名解析为 reference.docx 的绝对路径。
    文件不存在时抛出 FileNotFoundError。
    """
    ref = TEMPLATES_ROOT / template_name / "reference.docx"
    if not ref.is_file():
        raise FileNotFoundError(f"模板 reference.docx 不存在: {ref}")
    return ref


def patch_list_indent(docx_path: Path) -> None:
    """
    修复 reference.docx 中 List Paragraph 样式导致的双重缩进问题。

    问题根源：
    1. Normal 样式有 firstLine="200"（中文首行缩进），List Paragraph 继承它；
       pandoc 自己加 w:hanging 时不会覆盖 firstLine，导致首行多缩进。
    2. List Paragraph 样式自带 numPr（numId 引用），pandoc 还会再加自己的
       numPr，两个列表编号定义叠加产生额外左缩进。

    修复：去掉样式里的 numPr；显式设 firstLine="0" 覆盖 Normal 的继承。
    原地覆写文件，仅执行一次即可。
    """
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    def _tag(name: str) -> str:
        return f"{{{W}}}{name}"

    buf = io.BytesIO()
    with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "word/styles.xml":
                data = _patch_styles_xml(data, W, _tag)
            zout.writestr(info, data)

    docx_path.write_bytes(buf.getvalue())


def apply_layout(out_docx: Path, layout: dict) -> None:
    """
    对输出 docx 后处理，按 layout 强制写入段落缩进。

    支持的 layout 键（单位 twips，567≈1cm）：
      list_left    — 项目符号/数字列表左缩进
      list_hanging — 悬挂缩进（符号占位宽）
    """
    list_left = layout.get("list_left")
    list_hanging = layout.get("list_hanging")
    if list_left is None and list_hanging is None:
        return

    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    def _tag(name: str) -> str:
        return f"{{{W}}}{name}"

    buf = io.BytesIO()
    with zipfile.ZipFile(out_docx, "r") as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "word/document.xml":
                data = _patch_document_list_indent(data, _tag, list_left, list_hanging)
            elif info.filename == "word/numbering.xml":
                data = _patch_numbering_indent(data, _tag, list_left, list_hanging)
            zout.writestr(info, data)

    out_docx.write_bytes(buf.getvalue())


def _patch_numbering_indent(
    data: bytes,
    _tag,
    list_left: int | None,
    list_hanging: int | None,
) -> bytes:
    """按 list_left/list_hanging 重写 numbering.xml 中每个 abstractNum 每层的 w:ind。
    level n 的 left = list_left + n * list_left（每层递增一个缩进单位）。
    """
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ET.register_namespace("w", W)
    for event, elem in ET.iterparse(io.BytesIO(data), events=["start-ns"]):
        ET.register_namespace(elem[0], elem[1])

    root = ET.fromstring(data)
    step = list_left if list_left else 0
    hang = list_hanging if list_hanging is not None else 0

    for abstract in root.iter(_tag("abstractNum")):
        for lvl in abstract.findall(_tag("lvl")):
            ilvl = int(lvl.get(_tag("ilvl"), 0))
            pPr = lvl.find(_tag("pPr"))
            if pPr is None:
                pPr = ET.SubElement(lvl, _tag("pPr"))
            ind = pPr.find(_tag("ind"))
            if ind is None:
                ind = ET.SubElement(pPr, _tag("ind"))
            left = step * (ilvl + 1)
            ind.set(_tag("left"), str(left))
            ind.set(_tag("hanging"), str(hang))
            for attr in (_tag("firstLine"), _tag("firstLineChars")):
                ind.attrib.pop(attr, None)

    return ET.tostring(root, encoding="unicode", xml_declaration=False).encode("utf-8")


def _patch_document_list_indent(
    data: bytes,
    _tag,
    list_left: int | None,
    list_hanging: int | None,
) -> bytes:
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ET.register_namespace("w", W)
    for event, elem in ET.iterparse(io.BytesIO(data), events=["start-ns"]):
        ET.register_namespace(elem[0], elem[1])

    root = ET.fromstring(data)
    for p in root.iter(_tag("p")):
        pPr = p.find(_tag("pPr"))
        if pPr is None or pPr.find(_tag("numPr")) is None:
            continue
        ind = pPr.find(_tag("ind"))
        if ind is None:
            ind = ET.SubElement(pPr, _tag("ind"))
        if list_left is not None:
            ind.set(_tag("left"), str(list_left))
        if list_hanging is not None:
            ind.set(_tag("hanging"), str(list_hanging))
        # hanging 和 firstLine 互斥，清掉 firstLine
        for attr in (_tag("firstLine"), _tag("firstLineChars")):
            ind.attrib.pop(attr, None)

    return ET.tostring(root, encoding="unicode", xml_declaration=False).encode("utf-8")


def _patch_styles_xml(data: bytes, W: str, _tag) -> bytes:
    ET.register_namespace("w", W)
    for event, elem in ET.iterparse(io.BytesIO(data), events=["start-ns"]):
        ET.register_namespace(elem[0], elem[1])

    root = ET.fromstring(data)
    for style in root.findall(_tag("style")):
        name_el = style.find(_tag("name"))
        if name_el is None or name_el.get(_tag("val")) != "List Paragraph":
            continue
        pPr = style.find(_tag("pPr"))
        if pPr is None:
            continue
        # 去掉样式自带的 numPr，避免与 pandoc 生成的 numPr 叠加
        num_pr = pPr.find(_tag("numPr"))
        if num_pr is not None:
            pPr.remove(num_pr)
        # 覆盖继承自 Normal 的 firstLine 缩进，保留其他 ind 属性不动
        ind = pPr.find(_tag("ind"))
        if ind is None:
            ind = ET.SubElement(pPr, _tag("ind"))
        ind.set(_tag("firstLine"), "0")
        ind.set(_tag("firstLineChars"), "0")

    return ET.tostring(root, encoding="unicode", xml_declaration=False).encode("utf-8")
