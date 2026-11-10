---
name: hello-skill
description: "Use when the user asks to verify that a skill directory is installed and loadable: prints its own path, name and a one-line self check. Not for real work, it is the minimal reference example."
version: 1.0.0
---

# hello-skill

最小可用的 DSH 技能：证明「目录 + `SKILL.md`」就足够，顺便验证技能确实被加载了。

## 前置条件

技能目录在 `~/.dsh/skills/hello-skill/` 下，`skill` 工具能按名字 `hello-skill` 加载到这份正文。

## 步骤

1. 打印本文件绝对路径与目标行：

```bash
ls -l ~/.dsh/skills/hello-skill/SKILL.md
head -n 3 ~/.dsh/skills/hello-skill/SKILL.md
```

2. Windows：

```powershell
Get-Item "$env:USERPROFILE\.dsh\skills\hello-skill\SKILL.md" | Select-Object FullName,Length
Get-Content "$env:USERPROFILE\.dsh\skills\hello-skill\SKILL.md" -TotalCount 3
```

3. 报告加载结果，并说明「下一步做什么真正的工作」。

## 判据

- 文件存在，且前三行是 frontmatter 的 `---`、`name:`、`description:`。
- 你能读到这段文字本身——就说明 `skill hello-skill` 加载成功。
- 没有任何脚本报错。

## 失败与回滚

| 现象 | 原因 | 处理 |
|---|---|---|
| `skill` 找不到这个技能 | 目录名或 `name` 拼错 | 两者必须完全一致，改好后开新会话 |
| 读到正文但模型没主动加载 | description 太笼统 | 把「什么时候用」写具体，加用户会说的关键词 |
| 只读到一部分 | 正文过长被截断 | 长资料挪到 `references/`，正文只留步骤与判据 |
