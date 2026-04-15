# Quillen（奎琳）

**奎琳**是面向文档与演示的**文书型小助理**：把重复排版、格式转换和「从想法到可交付稿」的流程固化在仓库里，用脚本和约定减少手工折腾。

## 目录结构

| 路径 | 说明 |
|------|------|
| `environment.yml` | Conda 环境定义（`quillen`：Python、pandoc、pypandoc、pyyaml） |
| `handoff/` | 交接层：`PAD.md`（案笺格式说明）、`templates/`（命名模板目录）、`examples/`（示例稿） |
| `desk/` | 工具脚本：`compose.py`（入口）、`formula.py`（库）、`utils.py`（路径与后处理）；详见 `desk/DESK.md` |
| `desk/tests/` | 单元测试 |
| `inbox/` | 自动化投稿槽：`*.auto.qpad.md` 文件变动触发 CI 流水线 |
| `outbox/` | 本地输出目录（`.gitignore` 已忽略） |
| `.github/workflows/` | CI 工作流（`compose-auto`、`sync-inbox`） |

## 环境准备

```bash
conda env create -f environment.yml   # 首次
conda activate quillen
```

---

## 模式一：本地转换

适合开发调试、临时转换。

```bash
conda activate quillen
python desk/compose.py handoff/examples/handoff-sample.qpad.md
# 输出到 outbox/handoff-sample.docx
```

指定输出目录：

```bash
python desk/compose.py path/to/稿件.qpad.md -o /tmp/out
```

### 前言区字段

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

将已有 `.docx` 复制到 `handoff/templates/<name>/reference.docx` 即可：

```bash
cp 源文件.docx handoff/templates/mytemplate/reference.docx
```

前言区写 `template: mytemplate`。

---

## 模式二：自动流水线（auto 分支）

适合在 Windows 网页端用 Claude Code 写稿、自动生成 docx 到独立仓库。

### 流程

```
编辑 inbox/*.auto.qpad.md
  → push 到 auto 分支
  → GitHub Actions 运行 compose.py
  → docx 推送到 Quillen-out/wjb/
```

### 投稿槽

`inbox/` 下以 `.auto.qpad.md` 结尾的文件为固定槽位，直接编辑内容即可触发。输出文件名取自文件名去掉 `.auto.qpad.md` 后缀。

### 自动同步

`sync-inbox` workflow 每周一 02:00 UTC 自动将 `main` 合并进 `auto` 分支，保持 desk 脚本最新。

---

## 测试

```bash
conda activate quillen
python -m unittest discover -s desk/tests -v
```

---

名称 **Quillen / 奎琳** 取自 quill（羽毛笔），如有重名纯属巧合。
