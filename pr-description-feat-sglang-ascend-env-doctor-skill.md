* [new branch]      feat/sglang-ascend-env-doctor-skill -> feat/sglang-ascend-env-doctor-skill

Introduce a low-cost Ascend environment doctor for SGLang startup diagnostics, with structured reports and no default real-weight download. Group it under sglang/ namespace for future SGLang-related skills and update marketplace plus README links.

Made-with: Cursor

## 变更描述

新增并完善 `sglang/sglang-ascend-env-doctor`，用于在不默认下载真实大模型权重的前提下，低成本诊断 SGLang 在 Ascend NPU 上的可拉起性与可调用性。

### 变更类型
- [x] 新增 Skill
- [x] 更新现有 Skill
- [x] 修复问题
- [ ] 其他（请说明）

### 涉及的 Skill
Skill 名称：`sglang-ascend-env-doctor`

### 变更内容摘要
将 SGLang 诊断能力以独立 Skill 形式落地并归档到 `sglang/` 命名空间；新增最小拉起后 `curl` 验证、失败场景依赖版本采集与日志驱动根因分析，输出结构化 Markdown/JSON 报告与可追溯日志。

---

## 检查清单

提交 PR 前，请确认以下检查项已完成：

### SKILL.md 格式检查
- [x] `name` 字段与目录名完全匹配
- [x] `description` 字段不少于 20 个字符
- [x] frontmatter 格式正确（以 `---` 开头和结尾）
- [x] 包含 `description` 字段用于 Agent 匹配
- [x] 正文中无 `[TODO]` 或 `[TODO:xxx]` 占位符

### 内容完整性检查
- [x] 内部链接可正常访问（如 `references/xxx.md`）
- [x] 代码块已标注语言（如 ```bash、```python）
- [x] 表格格式正确（如有）

### 仓库更新检查
- [x] 已添加到 `.claude-plugin/marketplace.json`
- [x] 已更新 `README.md` 中的 Skill 列表（如适用）

---

## 测试说明

### 本地验证
运行以下命令进行本地验证：

```bash
# 验证所有 Skill 文件
python3 scripts/validate_skills.py

# 检查 frontmatter
find . -name "SKILL.md" -exec head -5 {} \; -print

# 检查 name 字段是否匹配目录名
find . -name "SKILL.md" | while read f; do
  dir=$(dirname "$f")
  name=$(grep "^name:" "$f" | cut -d: -f2 | tr -d ' ')
  echo "$dir -> name: $name"
done
```

### 本地测试截图

#### 1. 验证脚本测试结果

截图路径：
- `/home/d00883276/sglang_skill_dev/sglang-ascend-env-doctor-output-test/case4-curl-realmodel-20260315-114948/reports/screenshot-validate-skills.png`

```text
已执行 `python3 scripts/validate_skills.py`，结果通过（Errors: 0, Warnings: 0）。
```

#### 2. Skill 功能测试（如适用）

- [ ] 已在 AI Agent 中测试 Skill 触发（需人工在目标 Agent 会话中补测触发行为）
- [x] 已验证 Skill 内容正确加载

**测试截图：**

截图路径：
- `/home/d00883276/sglang_skill_dev/sglang-ascend-env-doctor-output-test/case4-curl-realmodel-20260315-114948/reports/screenshot-case4-curl-success.png`

关键证据路径：
- 报告：`/home/d00883276/sglang_skill_dev/sglang-ascend-env-doctor-output-test/case4-curl-realmodel-20260315-114948/reports/latest-env-doctor-report.md`
- `curl` 证据：`/home/d00883276/sglang_skill_dev/sglang-ascend-env-doctor-output-test/case4-curl-realmodel-20260315-114948/logs/20260315-114951-minimal-launch-curl.json`
- 失败场景分析报告：`/home/d00883276/sglang_skill_dev/sglang-ascend-env-doctor-output-test/case5-failure-analysis-20260315-123318/reports/latest-env-doctor-report.md`

### CI 检查
提交 PR 后将自动运行以下检查：
1. **Validate SKILL.md files** - 验证所有 SKILL.md 文件格式
2. **Check frontmatter** - 检查 frontmatter 完整性
3. **Verify skill names** - 验证 name 字段与目录名匹配
4. **Check for broken internal links** - 检查内部链接是否损坏

---

## 其他说明

### 关联 Issue
Fixes #

### 截图（如适用）
- 已补充本地验证截图与功能测试截图路径；如 PR 平台要求直接粘贴图片，可由提交者在 PR 页面上传上述截图文件。
