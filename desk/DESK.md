# desk/ 脚本说明

## compose.py — 统一入口（CLI）

```bash
python desk/compose.py <file.qpad.md> [-o <outbox>]
```

读取 `.md` / `.qpad.md`，完成完整的「稿 → docx」流水线：

1. 解析 YAML 前言区，取 `template` 和 `layout` 字段
2. 按 `template` 逻辑名找 `handoff/templates/<name>/reference.docx`
3. 打印识别到的公式（行内 / 块级）
4. 调用 pandoc 生成 docx（有模板则传 `--reference-doc`）
5. 若前言区有 `layout`，对输出 docx 做后处理（修正列表缩进）
6. 写入 `outbox/<stem>.docx`

---

## formula.py — 核心库（不直接运行）

供 `compose.py` 导入，不暴露 CLI。

| 函数 | 作用 |
|------|------|
| `parse_front_matter(text)` | 分离 YAML 前言区，返回 `(meta, body)` |
| `list_math_in_markdown(text)` | 扫描正文中的 `$...$` / `$$...$$`，返回 `(kind, latex)` 列表 |
| `md_to_docx(src, out, reference_doc)` | 调用 pandoc 转换，可选传入 reference doc 路径 |

---

## utils.py — 路径与后处理工具

| 常量 / 函数 | 作用 |
|-------------|------|
| `REPO_ROOT` | 仓库根目录绝对路径 |
| `TEMPLATES_ROOT` | `handoff/templates/` 绝对路径 |
| `resolve_reference_doc(name)` | 逻辑名 → `reference.docx` 路径，不存在则报错 |
| `apply_layout(out_docx, layout)` | 后处理输出 docx：按 `layout` 重写 `numbering.xml` 和段落级 `w:ind`，修正 pandoc 叠加缩进问题 |
| `patch_list_indent(docx_path)` | 修复 reference.docx 中 `List Paragraph` 样式的 `numPr` 和 `firstLine` 继承问题，对模板文件一次性执行 |
