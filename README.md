# Quillen（奎琳）

**奎琳**是面向文档与演示的**文书型小助理**：把重复排版、格式转换和「从想法到可交付稿」的流程固化在仓库里，用脚本和约定减少手工折腾。

## 目录结构

| 路径 | 说明 |
|------|------|
| `environment.yml` | Conda 环境定义（`quillen`：Python、pandoc、pypandoc、pyyaml） |
| `inbox/` | 创作简报槽：`*.idea.md` 文件（格式见 `inbox/IDEA.md`）；`example/` 存放示例简报 |
| `handoff/` | 交接层：`PAD.md`（案笺格式说明）、`*.auto.qpad.md`（CI 触发槽）、`templates/`、`examples/` |
| `desk/` | 办公桌，存放工具脚本:详见 `desk/DESK.md` |
| `desk/tests/` | 单元测试 |
| `outbox/` | 本地输出目录（`.gitignore` 已忽略） |
| `.claude/commands/` | Claude Code 自定义命令；`idea2doc.md` 为完整 idea→docx 工作流 |
| `.github/workflows/` | CI 工作流（`compose-auto`、`sync-inbox`） |

## 环境准备

```bash
conda env create -f environment.yml   # 首次
conda activate quillen
```

---

## 整体流程

```
inbox/*.idea.md   →   handoff/*.qpad.md   →   outbox/*.docx
   （创作简报）          （案笺草稿）            （交付文档）
```

- **`.idea.md`**：用自然语言描述文档意图，包含结构大纲、字数约束、素材与禁区（格式见 `inbox/IDEA.md`）
- **`.qpad.md`**：带 YAML 前言区的 Markdown 正文，是排版程序的直接输入（格式见 `handoff/PAD.md`）
- **`.docx`**：最终交付文件，输出至 `outbox/`

---

## 模式一：idea → docx（工作流模式）

在 Claude Code 中准备好 `*.idea.md` 后，执行命令，由 Agent 自动完成从创作简报到交付文档的全流程，含草稿生成、字数质检与格式输出。

**前置条件**：Claude Code 打开 `Quillen/` 目录。

```
/idea2doc inbox/你的简报.idea.md
```

示例简报见 `inbox/example/`。

---

## 模式二：qpad → docx（本地手动模式）

直接编写或修改 `.qpad.md`，本地运行 `compose.py` 生成文档。

```bash
conda run -n quillen python desk/compose.py handoff/foo.qpad.md
# 输出到 outbox/foo.docx
```

指定输出目录：

```bash
conda run -n quillen python desk/compose.py handoff/foo.qpad.md -o /tmp/out
```

字数质检（可选）：

```bash
conda run -n quillen python desk/check.py handoff/foo.qpad.md --target 7500-8500
```

### .qpad.md 前言区字段

```yaml
---
quillen_pad:
  version: 1
  kind: report        # memo | report
  title: "标题"
  lang: zh-CN
template: report      # 逻辑名 → handoff/templates/report/reference.docx
layout:
  list_left: 0        # 列表左缩进（twips，567≈1cm）
  list_hanging: 0     # 符号悬挂量
---
```

`template` 省略时走无样式的默认 pandoc 输出；`layout` 省略时不做后处理。

### 添加模板

```bash
cp 源文件.docx handoff/templates/mytemplate/reference.docx
```

前言区写 `template: mytemplate`。

---

## 模式三：远端 CI（待开发）

push 触发 GitHub Actions 自动生成，输出推送至独立仓库。

---

## 测试

```bash
conda activate quillen
python -m unittest discover -s desk/tests -v
```

---

名称 **Quillen / 奎琳** 取自 quill（羽毛笔），如有重名纯属巧合。
