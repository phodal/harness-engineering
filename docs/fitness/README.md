# Fitness Function Rulebook

> 这个仓库是文档仓库，因此最小自举目标不是“跑通应用”，而是让文章本身具备可检查、可阻断、可继续演进的约束。

## Quick Start

```bash
# 仅查看会执行什么
python3 docs/fitness/scripts/fitness.py --dry-run

# 实际执行最小规则
python3 docs/fitness/scripts/fitness.py

# 如果已经安装 Node 依赖，也可以直接跑 markdownlint
npm run lint:md
```

## Flow

```text
1. AGENTS.md                  → 文章仓库入口
2. docs/fitness/README.md     → 规则手册
3. docs/fitness/*.md          → frontmatter 规则文件
4. docs/fitness/scripts/fitness.py
5. markdownlint / shell checks
```

## Scope

- 当前仓库的第一目标是约束 `README.md` 这篇长文。
- 基础 Hard Gate 先只覆盖 Markdown 质量与仓库入口完整性。
- 后续可以继续扩展到链接校验、术语一致性、引用完整性等维度。

## Hard Gates

| Gate | 命令 | 阈值 |
| --- | --- | --- |
| markdownlint_pass | `npm run lint:md` | 0 errors |
| agents_entry_exists | `test -f AGENTS.md` | present |

## Core Principle

- 规则必须在仓库中。
- 规则必须既能被人阅读，也能被脚本执行。
- 对文档仓库来说，`markdownlint` 是最小门禁，Fitness 是统一解释层。
