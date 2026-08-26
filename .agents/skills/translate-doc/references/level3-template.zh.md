本文件给出 redesigned Level-3 中文页的固定输出结构。具体中文术语和固定措辞以
[`terminology.zh.md`](terminology.zh.md) 为准；最终结构以
`.agents/skills/wiki-publisher/scripts/verify_translation_structure.py` 为唯一机械 authority。

每个标题前必须恰好有一个空行（文件第一行标题除外），不得添加顶层 `#` 标题。

## 概览

**核心问题：** <此源码文件验证的核心行为。>

<用高信息密度的中文概括 page scope、测试目的和读者将在本页得到的内容。>

## 背景知识

<阅读本页需要先了解的最少前置概念。若 English source 使用 canonical no-prerequisite sentence，则使用
`本页不需要额外的前置概念。`。>

## 注册层级

逐字保留 English source 中完整的单个 `text` fence 及其 tree set；只允许把 trailing
`(registration only)` 注释翻译成 `(仅注册)`。不得添加 `dEQP-VK.`、嵌套层级、placeholder、`...` 或额外 prose。

```text
<category-qualified root copied from English source>
├── <direct child>
└── <direct child (仅注册)>
```

## 参数维度与可确认取值

<仅当 English source 包含此 optional section 时保留。>

| 维度 | 注册值 | 在此测试中的含义 | 证据 |
|------|--------|------------------|------|
| <parameter> | `<registered value>` | <含义> | <source link> |

## 行为参数

<最直接影响测试行为的注册参数及其取值；保留 English source 的 H3 行为值结构。>

## Shader 分析

若 English source 没有 walkthrough，翻译其 source-reviewed no-walkthrough justification，不创建 H3/H4。
若有 walkthrough，数量、编号和固定 subsection 必须与 English source 一一对应。

### 代表性 shader 讲解 1

#### 所选参数值

代表性路径：

```text
dEQP-VK.<完整可执行 registration path>
```

| 参数选择 | 在此代表性用例中的含义 |
|----------|------------------------|
| `<value>` | <含义> |

#### 目的

<一到两句说明此 shader 变体要验证的性质。>

#### 结构设计

此小节必须使用 Markdown table、Mermaid block 或 Markdown list，不能只写 plain prose。例如：

| 阶段 | 作用 |
|------|------|
| <phase> | <role> |

#### Shader 代码

保留 English source 的 `glsl` / `hlsl` fence、代码 token、缩进和 source-generated `//` 注释。翻译
wiki-authored `///` 注释中的说明性 prose，同时保留标识符和技术术语。

```glsl
<reconstructed shader copied from English source, with only permitted comment translation>
```

多 shader walkthrough 必须保留 English source 在 `#### Shader Code` 下的 H5 数量、顺序和 stage identity：

##### <Primary Stage> Shader

```glsl
<primary shader>
```

##### <Secondary Stage> Shader

```glsl
<secondary shader>
```

Direct-SPIR-V stage 保留对应 H5 和“不使用 GLSL/HLSL”的说明，不补造 source fence。

#### 补充信息

此小节允许为空。非空时只使用 Markdown list items，不写 plain paragraph，也不人为限制 bullet 数量。

- <high-value exact-case fact>

#### 参数变化总结

| 参数维度 | 相对此 shader 的 shader 层面变化 | 证据 |
|----------|--------------------------------|------|
| <dimension> | <variation> | <Markdown source link> |

每个数据行的 `证据` cell 都必须包含 Markdown source link。

#### SPIR-V

完整保留 English source 的 artifact 数量、stage H5、metadata、`<details>` wrapper、summary 和 `llvm` assembly。只按
`terminology.zh.md` 翻译固定 metadata labels 和 summary；assembly 必须逐字不变。

单 artifact 形状：

- 状态：已生成并验证
- 来源：本讲解中的重构 GLSL
- 阶段：`<stage>`
- 目标 SPIRV 版本：`spirv1.X`

<details>
<summary>点击展开 SPIRV asm 代码</summary>

```llvm
; SPIR-V
; Version: 1.X
<full unmodified spirv-dis output>
```

</details>

多 artifact 时，保留与 English source `Shader Code` stages 对齐的 H5：

##### <Primary Stage> SPIR-V

<该 stage 的完整 metadata + details + llvm artifact>

##### <Secondary Stage> SPIR-V

<该 stage 的完整 metadata + details + llvm artifact>

### 代表性 shader 讲解 2

<仅在 English source 包含 `### Representative Shader Walkthrough 2` 时使用，并重复完整固定 H4 结构。>

### 代表性 shader 讲解 3

<仅在 English source 包含 `### Representative Shader Walkthrough 3` 时使用，并重复完整固定 H4 结构。>

## runtime 执行逻辑与结果检查

<命令缓冲、资源初始化、提交方式和结果判定；保留 English source 的 list/table/code structure。>

## 失败含义

### 失败原因映射

<保留 English source 的行为参数到失败原因映射结构。>

### 原因分析

#### <原因名称>

**可能的失败表现：** <测试检查会观察到的表现。>

**可能的实现原因：** <有 evidence 的可能实现原因，或明确需要源码级调查。>

每个 `####` 原因小节都必须包含以上两个固定 lead-in。

## 用例裁剪

### 基于要求的裁剪

<硬件、API、feature、format、stage、scope 或 device-limit support gates。>

### 基于设计的裁剪

<冗余、无意义、超出测试设计或特殊 family 固定维度的组合。>

## 要点总结

- <page-specific 关键结论。>

## 源码参考附录

| 入口点 | 链接 | 重要性 |
|--------|------|--------|
| <function or file> | <source link> | <why it matters> |
