---
dimension: docs_quality
weight: 100
threshold:
  pass: 100
  warn: 80

metrics:
  - name: markdownlint_pass
    command: npm run lint:md 2>&1
    hard_gate: true
    tier: fast

  - name: agents_entry_exists
    command: test -f AGENTS.md && echo "AGENTS.md present"
    pattern: "AGENTS.md present"
    hard_gate: true
    tier: fast

  - name: fitness_rulebook_exists
    command: test -f docs/fitness/README.md && echo "fitness rulebook present"
    pattern: "fitness rulebook present"
    hard_gate: false
    tier: fast

  - name: readme_structure_exists
    command: grep -c '^## ' README.md | awk '{print "level2_sections:", $1}'
    pattern: "level2_sections: ([1-9][0-9]*|[1-9])"
    hard_gate: false
    tier: fast

  - name: routa_reference_exists
    command: grep -n 'Routa' README.md >/dev/null && echo "Routa referenced"
    pattern: "Routa referenced"
    hard_gate: false
    tier: fast
---

# 文档质量证据

> 这是文档仓库的最小 Fitness 维度。它先验证写作入口与 Markdown 质量，再逐步扩展到更细的文档约束。

## 当前目标

- 用 `markdownlint` 把最基础的格式问题收敛成 Hard Gate。
- 确保 `AGENTS.md` 与 `docs/fitness/README.md` 这两个入口文件存在。
- 确保文章本身仍然保持有效结构，并且包含 Routa 实践引用。

## 后续可扩展方向

- 链接检查
- 中英文术语一致性检查
- Frontmatter 示例与正文描述的一致性检查
- 引用来源完整性检查
