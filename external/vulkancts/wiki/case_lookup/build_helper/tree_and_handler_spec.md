# Registration Hierarchy Tree 与 Build Helper Contract

## 1. 目标与核心分工

本文件规定 case-lookup builder 如何把 Wiki Level-3 页面的
`## Registration Hierarchy` 转换成 prefix-to-page ownership mapping，以及什么时候允许
category-specific build helper 介入。

核心分工如下：

```text
Wiki Registration Hierarchy
    → primary ownership evidence
    → exact prefix-to-page candidate mappings

mustpass full case paths
    → executable universe and coverage validation
    → construction-variant discovery when explicitly required

category-specific build helper
    → explicit namespace projection or generated-family expansion only

validated mappings
    → SQLite build output
```

Builder 不应先为每个 mustpass leaf 生成完整的 `case → page` 表，再从这些 leaves
反推 shortest prefix。页面 tree 已经声明了 ownership boundary；mustpass 的职责是验证
真实 executable universe 是否完全落在这些 boundary 内。

## 2. 术语

- **Concrete root**：页面真正拥有的 category-qualified registration prefix，不带
  `dEQP-VK.`。例如 `memory_model.shared` 或
  `api.copy_and_blit.core`。
- **Direct child**：concrete root 下的直属 registration component。标准 tree 只展开
  一层 direct children。
- **Exact evidence**：由 concrete root 和 direct children 直接形成的真实 registration
  prefix。它是普通 category 的主要 DB mapping 来源。
- **Ownership tree set**：一个页面在一个 `text` snippet 中声明的一个或多个
  `concrete root` 及其 direct children。
- **Construction variant**：mustpass 中改变构建方式、但不改变页面行为 ownership 的
  namespace variant，例如 pipeline 的 monolithic、pipeline library、fast-linked library
  和 shader-object 变体。
- **Generated family expansion**：source 注册逻辑从一个稳定 family 规则生成多个真实
  registration component，例如 sample-count、offset、format 或变量后缀展开。
- **Category-specific projection**：build-time helper 根据已确认的 construction variant
  或 generated-family 规则，把 canonical page evidence 投影到真实 mustpass namespace。
- **Explicit alias**：为未覆盖 registration path 人工指定页面的历史 workaround。它
  不是正式 ownership evidence，也不是正式 DB build 允许的输入；出现 alias 表明 page
  tree 或 category-specific projection 尚未修复完整。
- **Generic anchor fallback**：根据孤立 component 名称或其下划线截短形式猜测 owner 的
  迁移诊断机制。它不是正式 DB mapping 生成机制。

## 3. 标准页面 contract

普通 Level-3 页面应满足以下条件：

1. `## Registration Hierarchy` 下使用一个 `text` fenced code block 表达页面的
   ownership tree set。
2. tree root 必须是 category-qualified path，但不带 `dEQP-VK.`，例如 `memory_model`
   或 `memory_model.shared`。
3. 一个 snippet 可以包含多个独立 trees。每棵 tree 必须以 root 开始，随后为该 root
   的直属 children；相邻 trees 之间至少使用一行空行分隔。
4. tree 只展开 root 的直属子节点；子节点使用 `├── name` / `└── name`，不得嵌套更深层级。
5. 如果 source 或 mustpass 会生成多个真实 direct children，页面应列出所有可确定的
   registration children。不要用 `<type>`、`<count>`、`{value}` 或省略号代替真实
   components。
6. 如果一个 generated family 的完整成员集合规模合理且可以由稳定、source-backed
   规则确定，页面应在 tree 中列出完整成员集合，并在 tree 后的 prose 或参数表中解释
   生成规则。不能只列出几个 representative children 后要求 generic builder 猜出其余
   成员。对于规模很大的规则化矩阵，可以列出一个真实存在的 canonical representative
   child，并在括号和 prose 中明确指出变量位置；这种写法必须配套显式、source-backed
   category helper，不能依赖 generic anchor。例：

   ```text
   └── indirect_compute_dispatch_offsets_0_0 (last two entries are memOffset and dispatchOffset)
   ```
7. 给读者看的括号说明可以存在，但不改变 ownership semantics。包含
   `registration only` 的 child 只供文档说明，builder 必须跳过它，不得把它变成 mapping。
   括号说明中的匹配是 containment match，而不是只接受完整固定字符串。
8. 同一 snippet 中的所有 trees 必须属于当前 category。root 不得重复；同一 root 下的
   child 不得重复；不得同时出现 ancestor root 和 descendant root。
9. tree 中不得出现带 `dEQP-VK.` 的 root、placeholder、`...`、变量模板或 `# comment`。
   root 必须是裸的 category-qualified path；direct child 必须是合法 registration
   component。读者解释应放在 tree 外的 prose 中。
10. 普通 category 的每个页面只能有一个 `text` snippet。一个页面覆盖多个 family 时，
    使用同一 snippet 中的多个 ownership trees。
11. `synchronization` / `synchronization2` 是当前页面级例外：共享页面可以包含两个
    category 的 roots，但每个 category 的 tree 仍必须列出其完整、可验证的 direct-child
    ownership set。只属于一个 category 的页面仍使用一个 snippet。
12. `vkt*.md`、`*_brief.md`、`internal_doc/` 不参与 ownership evidence。

推荐写法：

```text
memory_model.message_passing
├── core11
├── ext
└── permuted_index

memory_model.write_after_read
├── core11
└── ext

memory_model.transitive
├── coherent
└── noncoherent

memory_model.padding

memory_model.shared
```

generated family 的推荐写法：

```text
rasterization
├── fill_rules
├── fill_rules_multisample_2_bit
├── fill_rules_multisample_4_bit
├── fill_rules_multisample_8_bit
└── fill_rules_multisample_16_bit
```

tree 后的 prose 可以说明这些 children 来自同一 source family 和 sample-count loop，
但不能把 placeholder 放进 tree。

shared category 的推荐写法：

```text
synchronization2.internally_synchronized_queues
├── android_bind_sparse_wsi
├── headless_small2_wsi
├── small2_small2
└── xcb_wsi_bind_sparse
```

不推荐的写法：

- 只列出几个 representative children，却没有完整列表或显式 generated-family helper；
- 使用 `<type>`、`<memOffset>`、`{value}` 或 `...` 代替真实 tree component；
- 把 `dEQP-VK.` 写进 tree root；
- 使用 nested tree 或自然语言代替 direct-child 列表；
- 把 `registration only` child 当作普通 ownership child；
- 依赖 generic anchor fallback 代替修正页面 tree。

## 4. Build 处理框架

### 4.1 Exact evidence

Builder 首先读取所有可索引 Level-3 页面，解析其 ownership trees，并把每个 root 或
root + direct child 转换成 exact registration prefix。

例如：

```text
pipeline.monolithic.multisample
├── sampled_image
└── storage_image
```

产生：

```text
dEQP-VK.pipeline.monolithic.multisample.sampled_image → Multisample
dEQP-VK.pipeline.monolithic.multisample.storage_image → Multisample
```

如果 root 没有普通 child，则 root 本身是 mapping boundary。

页面间出现同一 exact prefix 的不同 owner 时，builder 必须直接失败并报告冲突。不能
依靠 mustpass 顺序、页面名排序或首次出现顺序消除冲突。

### 4.2 Category-specific projection

Exact evidence 不能覆盖真实 mustpass namespace 时，只允许使用明确、可测试、build-time
only 的 category-specific projection。projection 必须由 source、mustpass 和页面 prose
共同支持，并且只能生成真实存在于当前 mustpass universe 的 prefix。

允许的主要类别包括：

- **Construction variants**：将页面的 canonical behavior tree 投影到实际出现的
  construction namespaces。最终 DB 保存真实 registration prefix，不保存 canonical alias。
- **Generated families**：将页面 tree 中的稳定 representative root 或 canonical real
  member 按 source-backed 规则展开为真实 registration components。规则应明确写在
  helper 中，不应由通用字符串截断推断。规模合理的 family 仍应优先在 tree 中列全；
  大型规则化矩阵才使用 canonical real member 加显式 helper。
- **Shared category namespaces**：例如 synchronization2 使用 synchronization 页面
  目录，但必须按真实 `synchronization2.*` roots 过滤和验证。

projection 不得改变页面 owner，不得把未知 path 静默归入最近页面，也不得在 runtime
lookup 中执行。所有 projection 结果都必须继续接受 mustpass coverage validation。

### 4.3 Mustpass coverage validation

Builder 逐个读取配置的 mustpass files，验证每个真实 executable leaf 都能匹配：

1. exact evidence；或
2. 已确认的 category-specific projection。

除此之外的 alias 或 anchor 命中只能用于生成诊断，不能让正式 DB build 通过。

mustpass 是 coverage 和真实 namespace 的检查依据，不是重新推导页面 ownership 的主要
输入。builder 不应 materialize 全量 leaf-to-owner mapping，也不应从全量 leaves 反向构造
Trie 来恢复页面已经声明的 prefix boundary。

## 5. Fallback 分类与失败策略

正式 DB build 的目标是让所有 case 都落入前两类：

```text
Exact evidence
    → 正常路径

Category-specific projection
    → 明确的 construction variant、generated family 或 shared namespace 规则

Explicit alias
    → hard fail
    → 指引修复 page tree 或 category-specific projection

Generic anchor fallback
    → 仅生成诊断
    → 正式 DB build hard fail

Ambiguous anchor
    → hard fail

Completely unknown path
    → hard fail
```

### 5.1 Explicit alias

已有 alias 表示历史页面 evidence 与真实 registration namespace 之间存在尚未修复的
差异。正式 build 遇到 alias 覆盖需求时必须 hard fail，并报告完整 path、alias、目标
page 和相关 category。修复方式只能是：

- 补全或修正 page tree；或
- 对确属稳定 namespace 规则的情况增加 source-backed category-specific projection。

修复后必须删除对应 alias。正式配置中的长期目标是 alias 数量为零；不能因为 alias
能够猜中 owner，就认为 ownership 已经正确。

### 5.2 Generic anchor fallback

generic anchor 只能帮助诊断问题，例如提示：

```text
真实 path 没有 exact evidence，但 component anchor 指向 Page X
```

它不能把这种猜测写入正式 DB。发现 generic anchor 命中时，builder 应报告真实 path、
候选 anchor、目标 page 和建议修复方向，然后 hard fail：

- 补完整 page tree；
- 添加已确认的 category-specific generated-family rule；或
- 修正错误或不完整的 ownership evidence。

### 5.3 Ambiguous anchor

同一个最佳 anchor 指向多个 page 时，无法确定 owner。builder 必须 hard fail，并列出：

- 完整 mustpass path；
- 候选 anchor；
- 所有候选 page。

不能任意选择一个 page。

### 5.4 Completely unknown path

一个 mustpass leaf 如果没有 exact evidence、合法 projection 或明确的迁移诊断结果，
说明页面 tree、category helper 或 source/mustpass 之间存在未解决的不一致。builder 必须
hard fail，并报告该 path，帮助返回 Wiki 修正，而不是跳过或生成模糊 mapping。

## 6. `synchronization` / `synchronization2`

两个 category 共享 `external/vulkancts/wiki/testfiles/synchronization/` 页面目录，但
拥有独立的 mustpass universe。

- 页面检索可以读取共享目录；
- hierarchy root 必须保留真实 category 前缀；
- 构建 `synchronization` 时只接受 `synchronization.*` ownership；
- 构建 `synchronization2` 时只接受 `synchronization2.*` ownership；
- shared page 中的两个 category tree 必须分别通过 exact evidence 或明确 projection
  覆盖各自 mustpass；
- 不能用另一个 category 的同名 family 作为 owner fallback。

如果 `synchronization2` 的 generated family 只有少数 representative children 出现在
当前 tree，优先扩充页面 tree 列出所有真实 children；只有当 source-backed namespace
转换确实属于稳定 category 规则时，才加入 helper projection。

## 7. Builder 职责边界

Builder 应负责：

1. 从页面 hierarchy 生成 exact ownership evidence；
2. 检查页面间 duplicate、ancestor/descendant 和 owner conflict；
3. 应用明确的 category-specific projection；
4. 从 mustpass 读取真实 executable leaves 并验证全覆盖；
5. 对 ambiguous 和 unknown ownership hard fail；
6. 生成并原子写入 category DB 和 final DB；
7. 记录足以定位 Wiki tree 或 helper 问题的诊断信息。

Builder 不应负责：

- 在 runtime 做 suffix fallback、alias 或分类推断；
- 用 LLM/agent 隐式判断 ownership；
- 静默跳过无法解析的 hierarchy 或 mustpass leaf；
- 用 generic anchor fallback 长期掩盖页面 tree 缺陷；
- 把明显可以通过页面标准化表达的规则永久固化成 alias；
- 为了追求 build 通过而修改 validator 规则。

## 8. 处理优先级

当 build 暴露 unmapped 或 fallback path 时，按以下顺序处理：

1. 检查 page tree 是否遗漏了真实 root 或 direct child；
2. 检查页面是否用 representative placeholder 代替了必须列出的真实 members；
3. 检查是否存在合法、稳定且 source-backed 的 construction variant 或 generated-family
   规则；
4. 将该规则实现为 `build_helper/` 中显式、可测试的 projection；
5. 删除所有可被 exact evidence 或 projection 替代的 explicit alias；
6. 将 generic anchor 命中作为诊断并 hard fail；
7. 对 ambiguous 和 completely unknown path 始终 hard fail。

## 9. 迁移与验证流程

对每个 category：

1. 读取并验证所有页面 hierarchy；
2. 生成 exact evidence，报告 duplicate/conflict；
3. 根据 source、mustpass 和页面 prose 确认是否需要 projection；
4. 运行 category-specific build helper；
5. 对所有 mustpass leaves 做 full coverage validation；
6. 修复 page tree 缺陷，不用 generic fallback 静默绕过；
7. 对每个 helper 增加 unit test 和实际 category build test；
8. 重建 category DB 并检查 mapping、owner、manifest metadata；
9. 运行 lookup full coverage、deterministic rebuild 和 final merge 验证。

只有在 exact evidence、必要 projection、full coverage、deterministic rebuild、单元测试
和 smoke/integration checks 全部通过后，category 才能纳入 final DB。

## 10. 当前设计结论

- `Registration Hierarchy` 是 ownership 的 primary evidence。
- mustpass 是 executable universe、variant discovery 和 coverage validation 的依据。
- 普通 category 只应依赖 exact evidence；无 exact 命中应暴露页面或数据问题。
- construction variants、generated families 和 shared namespace 是允许的显式 projection
  类别，但必须放在 `build_helper/` 并有 source-backed 规则。
- explicit aliases 只用于解释历史问题；正式 build 遇到 alias 需求必须 hard fail。
- generic anchor fallback 只生成诊断；正式 build 必须 hard fail。
- ambiguous anchor 和 completely unknown path 必须 hard fail。
- validator 规则不因 builder 方便而放宽；无法放进 tree 的变量展开应通过合法 representative
  component 加页面 prose 和显式 helper 表达。