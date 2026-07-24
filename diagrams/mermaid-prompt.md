# Task: 生成 VK-GL-CTS Skills 关系 Mind Map（Mermaid）

直接生成一个 Mermaid 图表（无需使用任何外部 skill 或工具）。将 Mermaid 代码写入 `diagrams/vkcts-skills-mindmap.mmd` 文件。

## 背景

VK-GL-CTS 项目在 `.agents/skills/` 下有一组 wiki 文档 skills。本图展示这些 skills 之间的**使用先后顺序**、**master/helper 关系**，以及每个 skill 的 **helper files** 和 **helper skills** 的作用。

## 范围限制（重要）

**包含以下 skills：**

主 workflow skills（4 个）：

1. `wiki-rewriter`
2. `wiki-auditor`
3. `translate-doc`
4. `wiki-publisher`

helper skills（2 个，均为 `wiki-rewriter` 的 helper）：

5. `shader-analyzer`
6. `shader-disassembler`

**不要包含以下 skills：** `wiki-analyzer`、`vkcts-wiki-sync`。不要画中央标题节点。

## helper skill 关系说明

- `shader-analyzer` 是 `wiki-rewriter` 的 helper skill：在改写 shader-heavy 页面时，`wiki-rewriter` 调用 `shader-analyzer` 来重构并讲解代表性 shader case。
- `shader-disassembler` 是 `shader-analyzer` 的 helper skill：`shader-analyzer` 调用 `shader-disassembler` 把重构的 GLSL/HLSL 编译、验证、反汇编为 SPIR-V assembly。
- 形成调用链：`wiki-rewriter` → `shader-analyzer` → `shader-disassembler`。

## 语言规则

- 整体使用**中文叙述**。
- 技术概念保留英文，参照以下原则（源自 `translate-doc` 的 terminology 规则）：
  - skill 名称保留英文：`wiki-rewriter`、`wiki-auditor`、`translate-doc`、`wiki-publisher`、`shader-analyzer`、`shader-disassembler`
  - 保留英文的技术词：`workflow`、`source-navigation`、`explanation-first`、`canonical wiki`、`review workflow`、`translation workflow`、`publishing orchestrator`、`Level-2`、`Level-3`、`contract`、`gateway`、`template`、`terminology policy`、`validation checklist`、`registration tree`、`identifier`、`language gate`、`AI-pattern`、`directness`、`category-index`、`link-worker`、`section`、`list`、`table`、`code block`、`tree`、`blob URL`、`GitLab Wiki`、`canonical`、`helper`、`professor model`、`target-reader`、`meaningful-defect`、`truth`、`exposition`、`generated-artifact`、`worker result contract`、`summary`、`shader-heavy`、`shader case`、`GLSL`、`HLSL`、`SPIR-V`、`assembly`、`representative`、`walkthrough`
  - 文件名保留英文原样，如 `review-protocol.md`、`terminology.zh.md`、`output-template.md`、`shader-utility-index.md`、`workflow-notes.md`
  - 普通解释性文字翻译成中文

## 图表类型与布局

使用 `flowchart TD`（自上而下方向）。

由于 Mermaid 的自动布局无法像 Draw.io 那样精确控制坐标，采用以下策略实现清晰的层次结构：

### 节点分层（利用不可见的层级推算）

```
第一层: wiki-rewriter → wiki-auditor → translate-doc → wiki-publisher   （主流程，实线箭头）
第二层: 各 skill 下方的 helper files 节点                                  （黄色，虚线连接到对应 skill）
第三层: shader-analyzer、shader-disassembler                               （红色，虚线连接）
第四层: enWorkers、zhWorkers                                                （灰色，虚线连接到对应 helper files）
```

### 节点 ID 与内容

**第一层 — 4 个主 skill（各用不同颜色）：**

| 节点 ID | 显示内容 | 颜色 class |
|---------|----------|-----------|
| rewriter | `1. wiki-rewriter<br/>主 workflow<br/>把 source-navigation 页面改写为<br/>explanation-first 的英文 canonical wiki` | blue |
| auditor | `2. wiki-auditor<br/>主 review workflow<br/>审查技术正确性与解释充分性，<br/>就地修正已确认的缺陷` | green |
| translate | `3. translate-doc<br/>主 translation workflow<br/>把稳定的英文 canonical 页面翻译为<br/>受保护、结构对齐的中文页面` | orange |
| publisher | `4. wiki-publisher<br/>publishing orchestrator<br/>分发类别翻译、校验结构、转换链接、<br/>并完成发布导航` | purple |

**第二层 — 4 个 helper files 节点（黄色）：**

**重要：不要在节点内写 "<skill name> helper files" 之类的标题，直接以文件列表开头。**

| 节点 ID | 显示内容 |
|---------|----------|
| rwHelpers | `• rewrite-outline-template.md — 类别范围与分批<br/>• level3-template.md — Level-3 页面 contract<br/>• level2-template.md — 类别 gateway contract<br/>• understanding-brief-template.md — 改写前的学习模型<br/>• terminology-policy.md — 层级术语规则<br/>• validation-checklist.md — 完成校验项<br/>• pilot-examples.md — 已接受的风格示例` |
| auditHelpers | `• review-protocol.md<br/>　target-reader 与 professor model<br/>　meaningful-defect 阈值<br/>　truth 与 exposition 审查工作表<br/>　generated-artifact 编辑边界<br/>　worker result contract<br/>　以页面为中心的类别 summary 格式<br/><br/>同时复用 rewriter 的页面 templates、<br/>terminology policy 与 validation checklist` |
| trHelpers | `• terminology.zh.md — 中文术语与保护规则<br/>• level2-template.zh.md — 固定的 Level-2 中文结构<br/>• level3-template.zh.md — 固定的 Level-3 标题与翻译规则<br/>• .skillfish.json — skill 来源元数据<br/><br/>共同保证 identifier、链接、代码、<br/>registration tree 与结构对齐` |
| pubHelpers | `• worker-dispatch-templates.md — Level-2、Level-3 与 link-worker 的固定分配<br/>• verify_translation_structure.py — 逐 section 比对 list、table、code block 与 tree<br/>• convert_markdown_links.py — 把 canonical 本地链接映射为 GitLab Wiki 与 blob URL<br/><br/>这些 helper 在翻译之后、category-index<br/>收尾之前运行` |

**第三层 — 2 个 helper skill 节点（红色）：**

| 节点 ID | 显示内容 |
|---------|----------|
| shaderAnalyzer | `shader-analyzer<br/>helper skill（wiki-rewriter 调用）<br/>重构并讲解代表性 shader case，<br/>产出 Representative Shader Walkthrough` |
| shaderDisassembler | `shader-disassembler<br/>helper skill（shader-analyzer 调用）<br/>把重构的 GLSL/HLSL 编译、验证、<br/>反汇编为 SPIR-V assembly` |

**第四层 — 2 个 language gate 节点（灰色）：**

| 节点 ID | 显示内容 |
|---------|----------|
| enWorkers | `强制英文 language gate<br/>humanizer → stop-slop<br/>先做自然度审查，再做 directness / 残留 AI-pattern 清理` |
| zhWorkers | `强制中文 language gate<br/>shuorenhua → humanizer-zh<br/>先做技术中文自然度审查，再做残留 AI-pattern 清理` |

## 连接线规则

**主流程（实线粗箭头）：**

水平连接第一层的 4 个 skill，表示使用顺序：

```
rewriter --> auditor --> translate --> publisher
```

**helper skill 调用链（虚线箭头）：**

```
rewriter -.->|shader-heavy 页面时调用| shaderAnalyzer
shaderAnalyzer -.->|委托 SPIR-V 生成| shaderDisassembler
```

**拥有/调用关系（虚线箭头）：**

每个 skill 向下连接到对应的 helper files 节点：

```
rewriter -.->|拥有 contract| rwHelpers
auditor -.->|拥有 review protocol| auditHelpers
translate -.->|拥有翻译规则| trHelpers
publisher -.->|拥有发布工具| pubHelpers
```

**language gate 连接（虚线箭头）：**

**注意：** enWorkers 和 zhWorkers 都向上指向各自列正上方的**黄色 helper files 节点**（enWorkers → rwHelpers，zhWorkers → trHelpers），不指向 helper skill 节点。

```
enWorkers -.->|技术起草后运行| rwHelpers
zhWorkers -.->|翻译后运行| trHelpers
```

## 样式定义（classDef）

在 Mermaid 代码末尾使用 `classDef` 定义颜色：

```mermaid
classDef blue fill:#dae8fc,stroke:#6c8ebf
classDef green fill:#d5e8d4,stroke:#82b366
classDef orange fill:#ffe6cc,stroke:#d79b00
classDef purple fill:#e1d5e7,stroke:#9673a6
classDef yellow fill:#fff2cc,stroke:#d6b656
classDef red fill:#f8cecc,stroke:#b85450
classDef gray fill:#f5f5f5,stroke:#666666
```

然后用 `class` 语句分配：

```mermaid
class rewriter blue
class auditor green
class translate orange
class publisher purple
class rwHelpers,auditHelpers,trHelpers,pubHelpers yellow
class shaderAnalyzer,shaderDisassembler red
class enWorkers,zhWorkers gray
```

## 图例

由于 Mermaid flowchart 没有原生图例功能，在图表底部添加一个图例节点（使用不可见或中性样式），用文字说明颜色含义：

```
legend["图例<br/>🟨 helper files / contract（各 skill 拥有的参考文件）<br/>🟥 helper skill（被其它 skill 调用的子 skill）<br/>⬜ language quality gate（强制语言质量审查）<br/>━━ 实线 = 主流程顺序　- - 虚线 = 拥有 / 调用关系"]
```

给 legend 节点应用中性样式（无填充或白色填充），并用 `linkStyle` 隐藏连接到它的箭头（如果有的话），或干脆不连接它。

## Mermaid 语法注意事项

- 节点文本中的换行用 `<br/>`（Mermaid 支持 HTML 标签）。
- 节点文本中的特殊字符（如 `()`、`[]`、`{}`、`|`）需要用引号包裹节点定义，例如：`rewriter["1. wiki-rewriter<br/>..."]`。
- 虚线箭头用 `-.->`，带标签的虚线箭头用 `-.->|标签|`。
- 实线箭头用 `-->`。
- 全角空格 `　` 用于缩进子项。
- 节点 ID 用英文驼峰，显示内容用中文+英文混合。
- 文件开头写 `flowchart TD`。

## 输出要求

**所有输出文件必须写到 `diagrams/` 目录下，不要写到 project root。**

1. 将 Mermaid 代码写入 `diagrams/vkcts-skills-mindmap.mmd`。
2. 确认文件以 `flowchart TD` 开头。
3. 确认所有节点、连接线、classDef 和 class 语句都完整。
4. 确认 project root 下没有残留的副本。
