# VK-GL-CTS Wiki 中文术语参考

本文件记录 redesigned wiki 翻译时的术语选择和保留规则。英文注册路径、文件名、符号名、inline code 和 code block 始终保持原样。

## 层级术语

| English | 中文 | 说明 |
|---------|------|------|
| test category | 测试类别 | Level-2 路径组件，例如 `memory_model` |
| test family | 测试子族 | Level-3 页面范围或路径组件，例如 `shared`、`padding` |
| intermediate node | 中间节点 | 测试子族下面的中间路径组件，例如 `16bit`、`arrays_of_arrays` |
| node | 节点 | 仅用于 `intermediate node` 语境；不要用来指测试类别或测试子族 |
| test case | 单个测试 | 可执行的单个测试 |
| test case leaf | 单个测试 | 最终可执行的单个测试，例如 `3` 或 `test` |
| registered path | 注册路径 | 精确路径名保持英文原样 |
| registration hierarchy | 注册层级 | 固定章节标题 |
| registration only | 仅注册 | 树形结构注释中使用，例如 `(仅注册)` |
| delegated test family | 委托实现的测试子族 | 由当前文件注册、由其他文件实现的测试子族 |
| pure registration-only file | 仅包含注册逻辑的文件 | 不创建普通 Level-3 页面 |
| implementation-bearing source file | 包含实现逻辑的源文件 | Level-3 页面关注其实现逻辑 |

## 文档结构术语

| English | 中文 |
|---------|------|
| Level-2 page | Level-2 页面 |
| Level-3 page | Level-3 页面 |
| category page | 类别页面 |
| source evidence | 源码证据 |
| implementation evidence | 实现证据 |
| parameter dimension | 参数维度 |
| observed value | 可确认的取值 |
| support requirement | 支持条件 |
| feature requirement | feature 要求 |
| runtime execution | runtime 执行逻辑 |
| result checking | 结果检查 |
| case pruning | 用例裁剪 |
| key takeaway | 要点 |
| source reference appendix | 源码参考附录 |

## 常见 Vulkan / CTS 技术词

通常保留英文：

- Vulkan, Vulkan CTS, Vulkan SC, CTS, dEQP, mustpass, SPIR-V, GLSL, HLSL
- shader, Compute Shader, Vertex Shader, Fragment Shader
- GPU, CPU
- device, queue, pipeline, descriptor, descriptor set, render pass, framebuffer
- image, buffer, sampler, command buffer, query pool, subpass
- feature, extension, format, layout, tiling
- subgroup, workgroup, invocation

说明：`subgroup` 和 `workgroup` 是 Vulkan/GLSL 技术术语时保留英文；不要把 `subgroup` 用作文档层级术语。

## Shader 讲解翻译原则

- `shader-analyzer` 生成的 `///` 注释是 wiki 解释性内容，应翻译成中文。
- 翻译 `///` 注释时，保留注释标记、缩进、inline code、GLSL/Vulkan 符号、枚举、变量名、resource 名和注册路径。
- 不要把某个测试类别中的角色名或概念固化为全局术语；按上下文决定普通词是否翻译、技术词是否保留英文。
- 如果某个英文技术词在 Vulkan/GLSL 读者中更常用，保留英文并用自然中文解释其作用。

固定 SPIR-V 小节标签：

| English | 中文 |
|---------|------|
| Status | 状态 |
| generated and validated | 已生成并验证 |
| failed | 失败 |
| skipped | 已跳过 |
| Source | 来源 |
| reconstructed GLSL from this walkthrough | 本讲解中的重构 GLSL |
| Stage | 阶段 |
| Target SPIRV version | 目标 SPIRV 版本 |
| Click to expand SPIRV asm code | 点击展开 SPIRV asm 代码 |

## 单复数保留规则

当英文单复数区别会影响技术范围时，中文输出也要保留这个区别。

- 如果术语保留英文，保留英文原文中的单数或复数形式，例如 `race instance` / `race instances`。
- 如果术语翻译成中文且复数含义重要，使用自然的中文范围标记，例如 `多个`、`一组`、`一系列`、`这些`、`若干`、`集合`，或根据上下文改写。
- 不要机械标记每一个英文复数；只在复数会影响范围、行为或理解时使用本规则。

示例：

| English source | 中文处理 |
|----------------|----------|
| skipped race instances | 被跳过的 race instances |
| that race instance | 该 race instance |
| generated tests | 一组生成测试 / 生成出的多个测试 |
| parameter combinations | 多个参数组合 / 一组参数组合 |

## 保护规则

不要翻译：

- inline code 中的内容；
- fenced code block 中的代码 token 和源生成注释；
- 文件名、目录名、URL、markdown link target path；
- 函数名、类名、变量名、宏名、枚举名、结构体名；
- 注册路径和测试用例名称；
- ASCII tree 中的注册路径组件。

可以翻译：

- 普通解释性 prose；
- markdown link 的可见文本；
- heading 文本；
- ASCII tree 中括号内的说明性注释，例如 `(registration only)` → `(仅注册)`。
