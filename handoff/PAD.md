# Quillen Handoff（案笺）格式说明 v1

**Handoff** 是「写作 / Agent」与 **desk** 脚本之间的**交接层**：人用 Markdown 写可读正文，用 **YAML 前言区**写机器可消费的元数据；路径上归 **`handoff/`**（规范、模板、示例），执行脚本仍在 **`desk/`**。

## 文件与命名

| 约定 | 说明 |
|------|------|
| 扩展名 | 使用 **`.md`** 或 **`.qpad.md`**（后者一眼可辨「走奎琳案笺」）。 |
| 编码 | **UTF-8**。 |
| 正文 | 标准 Markdown；数学公式与 `desk/formula.py` 一致：**`$...$`** 行内、**`$$...$$`** 块级。 |

## YAML 前言区（可选但推荐）

置于文件开头，由一行 **`---`** 开始、下一行 **`---`** 结束（闭合行单独成段），内容为 **YAML**。

### `quillen_pad`（核心）

```yaml
quillen_pad:
  version: 1           # 案笺格式版本，递增；desk 可据此做兼容判断
  kind: memo           # memo | report | slide（预留）
  title: "文档标题"
  lang: zh-CN
```

- **`version`**：本仓库当前契约为 **1**；破坏性变更时递增。
- **`kind`**：文档种类，供未来不同 desk 管线路由；未知值时脚本可忽略或告警（以具体脚本为准）。

### `template`（可选）

**`handoff/templates/`** 下某套命名模板的逻辑名。desk 按约定解析其中的文件（当前：`reference.docx`）。

```yaml
template: default   # → handoff/templates/default/reference.docx
```

### 与正文的关系

- 前言区不得替代正文：叙事、公式、列表均在 **`---` 闭合之后**。
- 公式列表统计（`formula.py` 终端输出）仅扫描**正文**，避免前言区误匹配。

## 命名模板

- **`handoff/templates/<name>/`**：一套模板目录；前言区 **`template:`** 引用逻辑名，desk 按约定文件名解析。

| 文件名 | 用途 |
|--------|------|
| `reference.docx` | pandoc `--reference-doc`，控制 Word 输出样式 |

## 示例稿

试跑与对照见 **`handoff/examples/`**（含带 YAML 前言的 `*.qpad.md` 与纯 `*.md`）。

## 流水线位置

```text
handoff/（规范 + templates + examples） → desk/（脚本） → outbox/（生成物）
```

---

*修改时间：2026-04-12*
