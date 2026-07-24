# Task: 生成 VK-GL-CTS Skills 关系 Mind Map（Draw.io）

请使用 global skill `drawio-skill`（位于 `~/.agents/skills/drawio-skill/`），生成一个 `.drawio` 文件并导出 PNG 和 SVG。

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

**不要包含以下 skills：** `wiki-analyzer`、`vkcts-wiki-sync`。也不要包含 `drawio-skill` 自身。不要画中央标题节点。

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

## 布局策略（严格网格，避免箭头混乱）

画布约 1800×1100。采用网格布局：

```
第一行 (y≈100):  [rewriter]  [auditor]  [translate]  [publisher]     ← 4 个主 skill，各用不同颜色
第二行 (y≈330):  [rwHelpers] [auditHelpers] [trHelpers] [pubHelpers]  ← 4 个黄色 helper files 框
第三行 (y≈600):  [shaderAnalyzer] [shaderDisassembler]                ← 2 个红色 helper skill 框
第四行 (y≈820):  [enWorkers]               [zhWorkers]                 ← 2 个灰色 language gate 框
                                                                  [图例]
```

**注意：** enWorkers 和 zhWorkers 都向上指向各自列正上方的**黄色 helper files 框**（enWorkers → rwHelpers，zhWorkers → trHelpers），不指向 helper skill 框。
```

- 第一行 4 个框等宽（320px），水平间距均匀（左起 x=70, 480, 890, 1300）。
- 第二行 4 个框与第一行**列对齐**（相同 x 坐标），宽度相同。
- 第三行 2 个 helper skill 框放在第 1 列和第 2 列位置（x=70, 480），用红色系。
- 第四行 2 个 language gate 框分别与第 1 列和第 3 列对齐。
- 图例放在右下角（第 4 列位置）。
- 所有坐标对齐到 10 的倍数。

## 连接线规则

**主流程（实线粗箭头，strokeWidth=2，endArrow=block）：**

水平连接第一行的 4 个 skill，表示使用顺序：

```
wiki-rewriter → wiki-auditor → translate-doc → wiki-publisher
```

使用 `exitX=1;exitY=0.5;entryX=0;entryY=0.5`（从右侧中点到左侧中点），确保水平直线不交叉。

**helper skill 调用链（虚线箭头，dashed=1，endArrow=open）：**

- `wiki-rewriter` → `shader-analyzer`：`wiki-rewriter` 从底部出发，`shader-analyzer` 从顶部进入。由于不在同一列，需要用带 waypoint 的折线或让 `shader-analyzer` 位于 `wiki-rewriter` 正下方偏移位置。标签：`shader-heavy 页面时调用`。
- `shader-analyzer` → `shader-disassembler`：水平虚线箭头。标签：`委托 SPIR-V 生成`。

**拥有/调用关系（虚线箭头，dashed=1，endArrow=open）：**

- 每个 skill 向下连接到正下方的 helper files 框：`exitX=0.5;exitY=1;entryX=0.5;entryY=0`（垂直直线）。
- 每个 language gate 框向上连接到对应列的 helper files 框：`exitX=0.5;exitY=0;entryX=0.5;entryY=1`。
- 所有虚线箭头加 `labelBackgroundColor=#ffffff` 使标签可读。

**连接线标签（中文）：**

| 连接线 | 标签 |
|--------|------|
| rewriter → rwHelpers | 拥有 contract |
| auditor → auditHelpers | 拥有 review protocol |
| translate → trHelpers | 拥有翻译规则 |
| publisher → pubHelpers | 拥有发布工具 |
| rewriter → shaderAnalyzer | shader-heavy 页面时调用 |
| shaderAnalyzer → shaderDisassembler | 委托 SPIR-V 生成 |
| enWorkers → rwHelpers | 技术起草后运行 |
| zhWorkers → trHelpers | 翻译后运行 |

## 各节点内容

### 第一行：4 个主 skill（fontSize=14，各用不同颜色）

**1. wiki-rewriter**（蓝色 `#dae8fc` / `#6c8ebf`）
```
1. wiki-rewriter
主 workflow
把 source-navigation 页面改写为
explanation-first 的英文 canonical wiki
```

**2. wiki-auditor**（绿色 `#d5e8d4` / `#82b366`）
```
2. wiki-auditor
主 review workflow
审查技术正确性与解释充分性，
就地修正已确认的缺陷
```

**3. translate-doc**（橙色 `#ffe6cc` / `#d79b00`）
```
3. translate-doc
主 translation workflow
把稳定的英文 canonical 页面翻译为
受保护、结构对齐的中文页面
```

**4. wiki-publisher**（紫色 `#e1d5e7` / `#9673a6`）
```
4. wiki-publisher
publishing orchestrator
分发类别翻译、校验结构、转换链接、
并完成发布导航
```

### 第二行：4 个 helper files 框（黄色 `#fff2cc` / `#d6b656`，fontSize=12，align=left，verticalAlign=top）

**重要：不要在框内写 "<skill name> helper files" 之类的标题，直接以文件列表开头。**

**wiki-rewriter 下方：**
```
• rewrite-outline-template.md — 类别范围与分批
• level3-template.md — Level-3 页面 contract
• level2-template.md — 类别 gateway contract
• understanding-brief-template.md — 改写前的学习模型
• terminology-policy.md — 层级术语规则
• validation-checklist.md — 完成校验项
• pilot-examples.md — 已接受的风格示例
```

**wiki-auditor 下方：**
```
• review-protocol.md
    target-reader 与 professor model
    meaningful-defect 阈值
    truth 与 exposition 审查工作表
    generated-artifact 编辑边界
    worker result contract
    以页面为中心的类别 summary 格式

同时复用 rewriter 的页面 templates、
terminology policy 与 validation checklist
```

**translate-doc 下方：**
```
• terminology.zh.md — 中文术语与保护规则
• level2-template.zh.md — 固定的 Level-2 中文结构
• level3-template.zh.md — 固定的 Level-3 标题与翻译规则
• .skillfish.json — skill 来源元数据

共同保证 identifier、链接、代码、
registration tree 与结构对齐
```

**wiki-publisher 下方：**
```
• worker-dispatch-templates.md — Level-2、Level-3 与 link-worker 的固定分配
• verify_translation_structure.py — 逐 section 比对 list、table、code block 与 tree
• convert_markdown_links.py — 把 canonical 本地链接映射为 GitLab Wiki 与 blob URL

这些 helper 在翻译之后、category-index
收尾之前运行
```

### 第三行：2 个 helper skill 框（红色 `#f8cecc` / `#b85450`，fontSize=13）

**第 1 列：shader-analyzer**
```
shader-analyzer
helper skill（wiki-rewriter 调用）
重构并讲解代表性 shader case，
产出 Representative Shader Walkthrough
```

**第 2 列：shader-disassembler**
```
shader-disassembler
helper skill（shader-analyzer 调用）
把重构的 GLSL/HLSL 编译、验证、
反汇编为 SPIR-V assembly
```

### 第四行：2 个 language gate 框（灰色 `#f5f5f5` / `#666666`，fontSize=12）

**第 1 列（英文 gate）：**
```
强制英文 language gate
humanizer → stop-slop
先做自然度审查，再做 directness / 残留 AI-pattern 清理
```

**第 3 列（中文 gate）：**
```
强制中文 language gate
shuorenhua → humanizer-zh
先做技术中文自然度审查，再做残留 AI-pattern 清理
```

### 图例（右下角，无填充，strokeColor=#666666）

解释**复用的**颜色块（第一行各 skill 颜色不同，不列入图例）：

```
图例
[黄] helper files / contract（各 skill 拥有的参考文件）
[红] helper skill（被其它 skill 调用的子 skill）
[灰] language quality gate（强制语言质量审查）
[白] 实线箭头 = 主流程顺序；虚线箭头 = 拥有 / 调用关系
```

图例使用容器（parent=legend），子元素坐标相对于容器。每行间距约 40px。

## XML 技术要求

- 使用标准 `<mxfile><diagram><mxGraphModel><root>` 结构。
- `id="0"` 和 `id="1"` 为必需的根 cell。
- 所有 `value` 属性中的换行用 `&#xa;`，不要用字面 `\n`。
- 所有 `value` 属性中的 `&` 必须转义为 `&`（`&#xa;` 中的 `&` 不需要再转义）。
- 不要在 `value` 中使用 HTML 标签（如 `<b>`、`<br>`），因为会导致 XML 解析失败。
- 每条 edge 必须包含 `<mxGeometry relative="1" as="geometry"/>` 子元素。
- 所有 edge 使用 `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;`。

## 输出要求

**所有输出文件必须写到 `diagrams/` 目录下，不要写到 project root。**

1. 将 `.drawio` 文件写到 `diagrams/vkcts-skills-mindmap.drawio`。
2. 用 `xmllint --noout` 验证 XML 合法性。
3. 用 draw.io CLI 导出 PNG 和 SVG：
   ```bash
   drawio -x -f png --width 1800 -o diagrams/vkcts-skills-mindmap.png diagrams/vkcts-skills-mindmap.drawio
   drawio -x -f svg --width 1800 -o diagrams/vkcts-skills-mindmap.svg diagrams/vkcts-skills-mindmap.drawio
   ```
4. 如果 `repair_png.py` 脚本可用，对 PNG 运行修复。
5. 确认 `diagrams/` 目录下三个文件都已生成，且 project root 下没有残留的副本。
