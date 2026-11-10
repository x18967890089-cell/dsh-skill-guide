# dsh-skill-guide

[![ci](https://github.com/x18967890089-cell/dsh-skill-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/x18967890089-cell/dsh-skill-guide/actions/workflows/ci.yml)

给 [DeepSeek Harness](https://github.com/deepseek-ai)（下称 DSH）写技能的最小说明书：一个 `SKILL.md` 放在哪、frontmatter 怎么写、description 为什么决定它会不会被用上。

> A minimal, field-tested guide to authoring DSH skills: where `SKILL.md` lives, which frontmatter keys matter, and why the description is the whole ballgame.

本仓库里的每个结论都来自真实跑过的技能目录（`~/.dsh/skills/`），不是从文档里抄的字段表。

---

## 技能是什么

一个技能就是**一个目录 + 一个 `SKILL.md`**。模型在会话里能看到技能目录（名字 + description），判断当前任务匹配时用 `skill` 工具加载正文，然后按正文里的步骤做事。

```
~/.dsh/skills/
├── my-skill/
│   ├── SKILL.md          # 必须，正文 + frontmatter
│   ├── scripts/probe.sh  # 可选，正文里引用
│   └── references/api.md # 可选，长资料放这里，正文按需读
└── another-skill/
    └── SKILL.md
```

三条硬事实：

1. **目录名就是技能名**（`my-skill/` → `my-skill`），`skill` 工具按这个名字加载，写错一个字就加载不到。
2. **只有 `SKILL.md` 是必读的**。脚本、参考文档都是正文按需引用，不会被自动注入上下文——这正好是技能比「一次性塞进提示词」强的地方。
3. **不装、不编译、不重启**。目录在，下一次会话的技能目录里就有它。

## `SKILL.md` 长什么样

```markdown
---
name: my-skill
description: "Use when the user wants X: does Y and Z. Not for W."
version: 1.0.0
---

# 正文标题

正文就是给模型看的操作手册：步骤、命令、判据、失败怎么退。
```

真实例子（本机 `~/.dsh/skills/impeccable/SKILL.md` 的头部，只截前几行）：

```yaml
---
name: impeccable
description: "Use when the user wants to design, redesign, shape, critique, audit, polish … Not for backend-only or non-UI tasks."
version: 4.8.0
user-invocable: true
license: Apache 2.0
---
```

### frontmatter 字段

| 字段 | 必填 | 作用 |
|---|---|---|
| `name` | 是 | 技能名，与目录名保持一致；`skill` 工具按它加载 |
| `description` | 是 | **决定技能会不会被用上**，见下一节 |
| `version` | 否 | 自己维护的版本号，改动大时递增 |
| `user-invocable` | 否 | 是否允许用户直接点名调用 |
| `license` | 否 | 分发时的许可证标注 |

没列的字段不会被解读，写上去只是给人看。

## description 才是技能的开关

技能目录里只有 `name` + `description` 会被常驻展示。模型靠这两行判断「这个任务该不该加载它」。所以 description 不是介绍文案，是**路由规则**，三句话写完：

1. **什么时候用**：动作 + 对象，用用户会说的词（中文任务就写中文关键词）。
2. **它能交付什么**：一句话说清产出，避免模型以为它只是参考资料。
3. **什么时候别用**（可选但强烈建议）：写清边界，减少误加载。

反例（加载率极低）：

```yaml
description: "一个很有用的技能"
```

正例：

```yaml
description: "Use when a PHP site behind nginx+php-fpm must be deployed over plain FTP and the client keeps failing on 421/Transfer channel can't be opened: slot preflight, per-file byte verification, retry ladder. Not for SFTP or rsync targets."
```

## 正文怎么写

按「模型读一遍就能照做」的标准写，四段够用：

```markdown
## 前置条件
需要什么、检查什么（一条命令能验证的最好）

## 步骤
1. 具体命令，参数用占位符（TARGET / PORT / PATH）
2. 每步的期望输出

## 判据
怎么算跑通（退出码、字节数、HTTP 状态、日志里的那句话）

## 失败与回滚
哪一步失败说明什么；怎么退回去
```

三条经验：

- **写你验证过的命令**，别写「大致如此」。一次真实执行的输出贴进去，比十句描述有用。
- **占位符化**：`TARGET`、`PORT`、`WORKDIR`，别把一次性路径写死。
- **长资料外置**：API 清单、字段表放 `references/`，正文只写「需要时读 `references/x.md`」，避免正文几千行把上下文吃光。

## 最小可用技能

完整可运行版本见 [`examples/hello-skill/SKILL.md`](examples/hello-skill/SKILL.md)：十行，演示 frontmatter + 判据 + 失败处理；一个更接近实战的版本见 [`examples/http-probe/SKILL.md`](examples/http-probe/SKILL.md)。

安装：把目录整个复制到 `~/.dsh/skills/` 下即可。

```bash
cp -r examples/hello-skill ~/.dsh/skills/
ls ~/.dsh/skills/hello-skill/SKILL.md
```

Windows（PowerShell）：

```powershell
Copy-Item -Recurse .\examples\hello-skill "$env:USERPROFILE\.dsh\skills\"
```

## 什么时候不该写成技能

- **一次性的操作**：技能是为「下次还会遇到」准备的，只做一次的事写进日志就够。
- **纯资料**：没有步骤、只有知识点的东西，写成笔记或 `references/` 更好。
- **需要模型自己判断分寸的事**：技能里写死「必须执行 X」会把判断力也写死，留判据比留命令更重要。

## 自动沉淀出来的技能

DSH 的记忆系统会把跑通过的多步流程自动落成技能，目录名形如 `mem-skill-<片段>-<哈希>`，正文开头通常带一段「本技能由某次真实工作沉淀，附带程序仅供参考」的提示：

```
~/.dsh/skills/mem-skill-winscp-ftp-php-24de499db599/SKILL.md
```

这类技能可以直接用，但建议**跑通一次后再自己重写一遍**：机器沉淀的步骤保留，描述换成你的说法，边界补上你踩过的坑。

## 已知限制

- 本仓库只覆盖 `SKILL.md` 这一种形态；插件自带的技能、内置技能不在讨论范围。
- frontmatter 用 YAML，但只按上面五个字段读取；复杂结构（数组、嵌套）没有对应语义。
- 技能正文是**给模型读的**，不是给脚本解析的：不要指望它能被程序当成配置。

## 怎么验（本仓库自带的检查）

`tools/check-skills.py` 把上面所有能机器判的规则都判一遍：

```bash
python tools/check-skills.py
# ok: 2 skill(s), every link resolves
```

它检查五件事：`examples/*/SKILL.md` 有 frontmatter 块、frontmatter 是 `key: value` 形态、`name` 与 `description` 都非空、`name` 等于目录名（DSH 就是这么加载的）、README 里所有相对链接指向真实存在的文件。

CI（`.github/workflows/ci.yml`）除了跑它，还有一个**反向对照**：把 `name` 改坏再跑，检查脚本必须失败——只证明"合法的能过"不够，还得证明"坏的过不去"。

## 许可证

MIT
