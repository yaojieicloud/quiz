# Git 协作规范

> 本项目代码托管于 GitHub: https://github.com/yaojieicloud/quiz
> AI 助手（Hernes Agent）可代为操作 Git 推送，但需遵循本规范。

## AI 代操作前提

AI 助手通过 `hermes-agent` 的 `github-repo-management` 技能管理本仓库。
**推送前必须向用户确认**，严禁未经同意自动 commit / push / branch。

## GitHub Desktop 用户 → AI 代推送

本机 GitHub Desktop 已配置 credential helper，AI 代推送时直接复用，无需额外鉴权：

```bash
cd C:/Users/Yaojie/Documents/GitHub/quiz
# credential helper 自动从 GitHub Desktop 取 token
git add .
git commit -m "fix: ..."
git push origin main
```

> **注意**：若 AI 直接调用 `git push` 失败（而非通过 skill），通常是 credential 未被 git 正确读取。
> 解决方式：确保在 quiz 仓库目录下执行，并确认 `git config --global credential.helper` 已设置为 GitHub Desktop 的 helper。

## AI 代操作标准流程

1. **确认改动范围** — 向用户展示 `git diff`，说明要提交什么
2. **请求确认** — 明确告知「即将 commit + push 到 main」，得到同意后才执行
3. **执行** — 在 `C:/Users/Yaojie/Documents/GitHub/quiz` 目录下执行 git 命令
4. **验证** — 推送后检查 GitHub 仓库确认提交已到

## 禁止行为

- ❌ 未经用户确认的 `git push --force`
- ❌ 在非 quiz 目录下执行会影响本仓库的操作
- ❌ 提交 `data/`、`*.db`、`.venv/` 等已被 `.gitignore` 的文件

## 协作流程与本项目的关系

本项目使用 **it-workflow** 流程（需求 → 设计 → 任务 → 开发 → 文档同步 → 验收），
Git 操作是「文档同步 / 代码提交」环节的执行手段，不是独立的开发步骤。
详见 `docs/init/project-structure.md` 和 `docs/PROGRESS.md`。

## 参考

- GitHub 仓库：https://github.com/yaojieicloud/quiz
- `it-workflow` 技能（Hermes Agent 内置）：需求管理 / 任务拆解 / 协作流程
- `github-repo-management` 技能（Hermes Agent 内置）：clone / PR / issues / releases
