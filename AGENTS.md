# Harness Engineering 文章仓库

## Project Overview

- `README.md` 是文章正文，也是当前仓库的单一事实来源。
- `docs/fitness/` 存放文档仓库的最小 Fitness 规则与执行器。

## Writing Standards

- 优先保持文章结构稳定，不要无意改动章节编号与主叙事顺序。
- 新增内容应尽量落在已有章节中，除非明确需要新增章节。
- 文档仓库的变更以可读性和可执行性为目标，不写只用于展示、无法运行的“样例工程”。

## Fitness Function

在提交前，优先执行：

```bash
python3 -m pip install -r docs/fitness/requirements.txt
npm run fitness:dry-run
```

如果已经安装 Node 依赖，再执行：

```bash
npm run lint:md
npm run fitness
```

## Git Discipline

- 保持 baby-step 提交，一次只处理一个清晰问题。
- 这个仓库主要是文档与规则仓库，避免把无关的实验性脚本一起提交。
