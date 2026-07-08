# <cpp source code filename>

## 概览

**核心问题：** <此源码文件验证的行为。>

## 背景知识

<阅读本页需要先了解的概念。>

## 注册层级

```text
<test category>
└── <test family>
    └── <intermediate node or case leaf>
```

固定树形注释：

- `(registration only)` → `(仅注册)`

## 参数维度与可确认取值

| 维度 | 注册值 | 在此测试中的含义 | 证据 |
|------|--------|------------------|------|
| <parameter> | `<registered value>` | <含义> | <source link> |

## 行为参数

<最直接影响测试行为的注册参数及其取值，逐一举例说明。>

## Shader 分析

固定标题映射：

| English heading | 中文标题 |
|-----------------|----------|
| `## Shader Analysis` | `## Shader 分析` |
| `### Representative Shader Walkthrough 1` | `### 代表性 shader 讲解 1` |
| `### Representative Shader Walkthrough 2` | `### 代表性 shader 讲解 2` |
| `### Representative Shader Walkthrough 3` | `### 代表性 shader 讲解 3` |
| `#### Parameter Values Chosen` | `#### 所选参数值` |
| `#### Purpose` | `#### 目的` |
| `#### Structural Design` | `#### 结构设计` |
| `#### Shader Code` | `#### Shader 代码` |
| `#### Additional Info` | `#### 补充信息` |
| `#### Parameter Variation Summary` | `#### 参数变化总结` |
| `#### SPIR-V` | `#### SPIR-V` |

保留与翻译规则：

- `Representative Shader Walkthrough N` 的编号必须保留，翻译为 `代表性 shader 讲解 N`；不要改成无编号标题或“补充 shader 讲解”。
- `Structural Design` 内的 `mermaid`、`drawio`、`text` 等 fenced diagram block 保持原文不变；只翻译 block 外的说明文字和表格 prose。
- `Shader Code` 内的 `glsl` code block 必须保留代码 token、缩进和源生成的 `//` 注释。
- `Shader Code` 内 wiki 添加的 `///` 解释性注释应翻译成中文，同时保留 `///` 标记、缩进、inline code、标识符和技术术语。
- `Parameter Variation Summary` 的表格结构保留；翻译解释性 cell prose，但保留 inline code、路径、符号和源码链接目标。
- `SPIR-V` 小节中的 `llvm` code block 是 `spirv-dis` 原始输出，必须完整保留原文；只翻译 code block 外的固定字段标签和 `<summary>` 文本。

### 代表性 shader 讲解 1

#### 所选参数值

代表性路径：

```text
<registered.test.path>
```

| 参数选择 | 在此代表性用例中的含义 |
|----------|------------------------|
| `<value>` | <含义> |

#### 目的

<此 shader 变体要验证的同步、可见性或数据访问性质。>

#### 结构设计

<资源、坐标、同步协议和结果检查结构。>

#### Shader 代码

此路径对应的重构 GLSL：

```glsl
<reconstructed shader>
```

#### 补充信息

<该 shader 的关键语义说明。>

#### 参数变化总结

| 参数维度 | 相对此 shader 的 GLSL 层面变化 | 证据 |
|----------|--------------------------------|------|
| <dimension> | <variation> | <source link> |

### 代表性 shader 讲解 2

<仅在英文页面包含 `### Representative Shader Walkthrough 2` 时使用。>

### 代表性 shader 讲解 3

<仅在英文页面包含 `### Representative Shader Walkthrough 3` 时使用。>

## runtime 执行逻辑与结果检查

<命令缓冲、资源初始化、提交方式和结果判定。>

## 失败含义

### 失败原因映射

<行为参数取值到可能失败原因的映射表。>

### 原因分析

<逐一分析每个失败原因：具体可能出现什么问题，以及实现中什么可能导致该问题。>

## 用例裁剪

<不支持组合、特性要求和能力检查。>

## 要点总结

- <关键结论。>

## 源码参考附录

| 入口点 | 链接 | 重要性 |
|--------|------|--------|
| <function or file> | <source link> | <why it matters> |
