# citation-standard 技能说明

## 一、背景与问题

### 1.1 现有 prompt 的引用格式缺陷

原prompt定义了科研报告的三部分输出格式，其中第二部分（逐条结论）要求每条结论标注出处及位置。其给出的位置格式示例包括：

- `§4.1 节 "Main Results"`
- `第5页第3段`
- `Abstract`
- `Introduction 末段`

这些格式存在以下模糊性，导致不同 case 输出的位置标注格式不一致：

| 问题 | 示例 | 歧义来源 |
|------|------|---------|
| 段落计数无规则 | `第5页第3段` | 从何处开始计为"第1段"？是否跳过标题、图表标题、脚注？ |
| 中英文混用 | `§4.1 节`, `第5页第3段` | 半边符号半边中文，不同模型输出风格不一 |
| 粒度过粗 | `Abstract` | Abstract 有多个段落，仅标 Abstract 无法定位具体位置 |
| 自由文本描述 | `the part about limitations` | 完全无法标准化，每个模型输出的描述词都不同 |
| 无多位置分隔规范 | `§3.2节和§4.1节` | "和"、"与"、"、" 随意使用，难以被程序解析 |

---

## 二、新增文件清单

在 `openclaw/skills/citation-standard/` 下新建 3 个文件：

```
openclaw/skills/citation-standard/
├── SKILL.md                        # 主技能文件（67 行）
├── references/
│   └── cps-spec.md                 # 完整规范（143 行）
└── scripts/
    └── validate.py                 # CPS 合规检查脚本（244 行）
```

### 2.1 SKILL.md — 主技能文件

**路径：** `openclaw/skills/citation-standard/SKILL.md`

定义 Citation Position Standard (CPS) 的核心规则：

- **句法模板：** `[Tag] scope::elementID`
- **封闭词汇表：**
  - scope：`§N.M`、`pN§N.M`、`Abstract`、`Introduction`、`Conclusion`、`Methods`、`Results`、`Discussion`、`RelatedWork`
  - element：`¶`（段落）、`T`（表格）、`F`（图表）、`Eq`（公式）、`FN`（脚注）
- **段落计数规则：** 从所属结构单元起始处计数，跳过标题/图表标题/公式/脚注，页边界处按起始页计
- **分隔符规范：** 同论文多位置用 `; `，不同论文用 ` / `
- **输出前自检清单：** 6 条逐项核查规则

### 2.2 references/cps-spec.md — 完整规范文档

**路径：** `openclaw/skills/citation-standard/references/cps-spec.md`

包含 SKILL.md 中不适合放但需要查证的详细内容：

- **EBNF 形式文法** — 位置字符串的严格语法定义
- **逐类位置计数细则** — 按 scope 类型分别说明段落计数方法（编号节/页码/命名区域）
- **特殊元素规则** — 表格、图表、公式、脚注的编号引用规则
- **边界情况处理** — 节从页中间开始、跨段落内容、无编号节的论文、PDF 无页码等
- **旧格式 vs CPS 对照表** — 8 种常见场景的迁移对照

### 2.3 scripts/validate.py — 合规检查脚本

**路径：** `openclaw/skills/citation-standard/scripts/validate.py`

Python 命令行工具，读取报告文件并逐条检查 CPS 合规性：

```
用法：
  python validate.py <report.md>    # 检查报告文件
  python validate.py --stdin         # 从标准输入读取
  python validate.py --help          # 显示帮助
```

**检查项：**
1. 第二部分每条结论的每个 `[A]~[F]` 标签是否后跟位置标注
2. 位置标注是否符合 `scope::elementID` 语法
3. scope 是否来自封闭词汇表
4. element 类型是否来自封闭集合 `{¶, T, F, Eq, FN}`
5. 多位置分隔符是否使用 `; `（同论文）和 ` / `（异论文）
6. 第三部分是否完整列出 A~F 全部六篇论文

已用测试报告验证：脚本能正确区分合规引用（如 `§4.1::¶2`、`Abstract::¶2`、`Results::¶末`）和违规引用（如 `T2` 缺 scope、`the part about limitations` 自由文本、空位置）。

---

## 三、CPS 格式速览

### 3.1 核心句法

```
[Tag] scope::elementID
```

### 3.2 完整示例

```
出处：[A] §4.1::¶2; §4.1::T2 / [B] §3.2::¶1 / [D] Abstract::¶2
出处：[A] §2.3::¶3 / [C] p7§5.1::¶1; p7§5.1::F4 / [E] Results::¶末
出处：[B] §5::¶末 / [D] §4.2::¶2; §6.1::¶1 / [F] Discussion::¶2
```

### 3.3 与原格式的差异

| 维度 | prompt.md 原格式 | CPS 格式 |
|------|-----------------|---------|
| 段落引用 | `第5页第3段`（计数规则未定义） | `p5§3.2::¶1`（计数规则明确：从 scope 起始计） |
| 区域引用 | `Abstract`（无段落粒度） | `Abstract::¶2`（必须标注段落） |
| 表格引用 | `Table 2` | `§4.1::T2`（强制附带所在节） |
| 同论文多位置 | `§3.2 节和 §4.1 节` | `§3.2::¶2; §4.1::T2`（`; ` 分隔，每个位置重复完整 scope） |
| 同 scope 多段落 | `§3.2::¶2; ¶3` | `§3.2::¶2; §3.2::¶3` |
| 异论文 | `[A]...，[B]...` | `[A]... / [B]...`（` / ` 分隔） |
| 引言末段 | `Introduction 末段` | `Introduction::¶末` |
| 语法约束 | 无（自由文本） | EBNF 文法 + 封闭词汇表 |

---

## 四、集成方式

### 注册为技能（利用 OpenClaw 内置技能系统）

在 `~/.openclaw/openclaw.json` 的 `skills.entries` 中添加条目，Agent 即可按需加载引用格式规范：

```jsonc
"citation-standard": {
  "enabled": true
}
```

这是 OpenClaw 框架原生的技能发现机制（`skills.entries` 为系统配置项），无需额外依赖。

---
