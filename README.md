# Quillen（奎琳）

**奎琳**是面向文档与演示的**文书型小助理**：把重复排版、格式转换和「从想法到可交付稿」的流程固化在仓库里，用脚本和约定减少手工折腾。

## 目录结构

| 路径 | 说明 |
|------|------|
| `environment.yml` | Conda 环境定义（`quillen`：Python、pandoc、pypandoc、pyyaml） |
| `inbox/` | 创作简报槽：`*.idea.md` 文件（格式见 `inbox/IDEA.md`）；`example/` 存放示例简报 |
| `handoff/` | 交接层：`PAD.md`（案笺格式说明）、`templates/`、`examples/` |
| `agent/` | 工作流定义：`new-idea.md`、`idea2doc.md`、`idea2auto.md` |
| `desk/` | 办公桌，存放工具脚本，详见 `desk/DESK.md` |
| `outbox/` | 本地输出目录（`.gitignore` 已忽略） |
| `.github/workflows/` | CI 工作流（`compose-auto`、`sync-inbox`） |

## 环境准备

```bash
conda env create -f environment.yml   # 首次
conda activate quillen
```

---

## 整体流程

```
用户 idea
    │
    ▼  agent/new-idea.md（对话引导 → 确认结构）
    │
    ▼
inbox/*.idea.md          ← 创作简报（结构、字数、素材、禁区）
    │
    ▼  agent/idea2doc.md 或 agent/idea2auto.md
    │
    ▼
handoff/*.qpad.md        ← 案笺草稿（带 YAML 前言的 Markdown 正文）
    │
    ├── 本地 ──▶ outbox/*.docx
    │
    └── 远端 ──▶ push 至远端 GitHub 仓库，由 CI 触发排版并推送产物
```

- **`.idea.md`**：用自然语言描述文档意图，包含结构大纲、字数约束、素材与禁区（格式见 `inbox/IDEA.md`）
- **`.qpad.md`**：带 YAML 前言区的 Markdown 正文，是排版程序的直接输入（格式见 `handoff/PAD.md`）

---

## 使用方式

核心入口是 `agent/new-idea.md`，它负责在对话中引导用户从一句话想法走到确认好的创作简报，再自动落稿。任何能执行 Markdown 工作流的 AI 工具都可以触发它；下面以 **Claude Code** 为例。

### 以 Claude Code 为例

**第一步：配置 Skill**

在用户配置目录下创建 Skill 文件：

```
~/.claude/skills/quillen/SKILL.md
```

写入以下内容（将 `/path/to/Quillen` 替换为本仓库实际绝对路径）：

```markdown
---
name: quillen
description: 奎琳文书工作流：自然语言描述触发创作引导，.idea.md 路径直接落稿
argument-hint: [主题描述 | path/to/file.idea.md]
version: 1.0.0
---

根据 `$ARGUMENTS` 的形式，路由到对应的奎琳工作流：

- 若 `$ARGUMENTS` 是以 `.idea.md` 结尾的文件路径：读取并执行 `/path/to/Quillen/agent/idea2doc.md`，以 `$ARGUMENTS` 作为输入
- 否则（自然语言描述或空）：读取并执行 `/path/to/Quillen/agent/new-idea.md`，以 `$ARGUMENTS` 作为输入
```

**第二步：触发工作流**

在 Claude Code 中输入主题描述，奎琳会先对话引导确认结构，再自动落稿：

```
/quillen 论述詹姆斯的历史地位已经超过了乔丹
```

已有 `.idea.md` 时可跳过引导直接落稿：

```
/quillen inbox/your-doc.idea.md
```

---

## TODO

- [ ] **目录处理**：自动生成带超链接的文档目录，支持插入位置配置
- [ ] **图片及说明**：图片嵌入、自动编号（图 1、图 2…）、题注样式
- [ ] **PPT 支持**：`.idea.md` → 演示文稿大纲，输出 PPTX

---

名称 **Quillen / 奎琳** 取自 quill（羽毛笔），如有重名纯属巧合。
