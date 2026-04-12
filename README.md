# Quillen（奎琳）

**奎琳**是面向文档与演示的**文书型小助理**：帮你把材料收好、格式对齐、交付物就位——本仓库就是她用的「工作台」：把重复排版、格式转换和「从想法到可交付稿」的流程**固化在仓库里**，用脚本和约定减少手工折腾；后续可逐步接入更强的工作流（例如 Agent），但始终**以需求为驱动**。

## 动机

- **网页对话式 AI**写大纲、公式很方便，但产物往往不能直接进 **Word / PPT**（例如 LaTeX 公式、版式不一致）。
- **奎琳**希望在仓库中沉淀**可重复执行**的步骤：先有可版本控制的中间稿（如 Markdown），再由本仓库工具生成面向办公软件的输出，并控制「空话报告」类低价值内容（通过模板、校验与流程迭代，而非单次提示词）。

当前第一个落地能力是：**含 LaTeX 数学公式的 Markdown → Word（`.docx`）**，并能在终端**列出识别到的公式片段**，便于核对。

## 目录结构（现状与展望）

| 路径 | 说明 |
|------|------|
| `environment.yml` | Conda 环境定义（环境名 `quillen`：Python、pandoc、`pypandoc`）。 |
| `handoff/` | **交接层**（案头待办）：`PAD.md`（案笺说明）、`templates/`（命名导出模板）、`examples/` 样例稿；稿怎么写、模板放哪，与 desk 的契约与输入示例均在此。 |
| `desk/` | **办公桌**：日常工具脚本，真正「动手」转换的地方；当前核心为 `formula.py`。 |
| `desk/tests/` | 与 `desk` 配套的单元测试。 |
| `outbox/` | **成品筐**：默认输出目录（生成的 `.docx` 建议不入库，见 `.gitignore`）。 |

**展望（非承诺）**：在 `desk/` 或后续子包中扩展更多「稿 → 版式」管线（如幻灯片、模板化章节、质量检查）；输入侧可继续以「AI 产出 `idea.md` / 结构化大纲」为起点，输出侧由脚本统一落地。

## 环境准备

1. 安装 [Miniconda](https://docs.conda.io/) 或 Anaconda（已安装可跳过）。
2. 在本仓库根目录创建并激活环境：

```bash
conda env create -f environment.yml   # 首次
conda activate quillen
```

3. 确认 Pandoc 可用（由 conda 提供）：

```bash
pandoc -v
```

## 现有功能：公式 Markdown → Word

**脚本**：`desk/formula.py`

**作用**：

- 读取输入 **`.md`**（UTF-8）。
- 按常见 Pandoc/Markdown 习惯识别数学片段：**`$$...$$`** 为块级公式，**`$...$`** 为行内公式（块级区域内的内容不参与行内匹配）。
- 在终端打印识别到的公式条数与简短预览。
- 调用 **Pandoc**（经 `pypandoc`）将全文转为 **`.docx`**，公式在 Word 中一般为可编辑的公式对象（取决于 Pandoc 版本与内容）。

**基本用法**（在仓库根目录执行）：

```bash
conda activate quillen
python desk/formula.py handoff/examples/posture_reward.md
```

**指定输出目录**：

```bash
python desk/formula.py path/to/笔记.md -o /tmp/quillen-out
```

## 测试

```bash
conda activate quillen
python -m unittest discover -s desk/tests -v
```

## 限制与说明

- 公式定界目前仅支持 **`$` / `$$`**；`\(...\)`、`\[...\]` 等写法可能不会被当前识别逻辑列出（转换仍可能由 Pandoc 处理，以实测为准）。
- 行内公式若含未转义的 `$`，可能被切分错误，需以预览列表核对。
- `outbox/*.docx` 已默认被 `.gitignore` 忽略；若需分享成品，请单独导出或使用发布流程。

---

名称 **Quillen / 奎琳** 取自 quill（羽毛笔），如有重名纯属巧合。
