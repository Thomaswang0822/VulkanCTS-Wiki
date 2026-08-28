# subgroups category：待实现维护者确认的 Source-Level Findings

> 本文从 `subgroups` category 的源码审计结果中抽取 2 项未解决发现，供 Vulkan CTS 实现维护者逐项评估。它们不表示 wiki 审计未完成，也不等同于已经确认的 Vulkan 实现缺陷。当前观察集中在测试 oracle 覆盖边界，以及 support-gating 与生成 shader artifact 之间的一致性。
>
> 文档审计没有修改 Vulkan CTS C++ 源码、生成 shader、Amber artifact、mustpass 或 Vulkan 规范。对应 Level-3 页面已经记录当前可观察行为和限制；在排除测试侧问题前，不应仅凭这些测试结果把失败归因于驱动。

## 处理建议

建议把每项作为独立的源码调查或 issue。先确认测试意图、完整执行路径和规范前置条件，再决定是否修改测试实现。若确认需要修复，应添加能够区分修复前后行为的回归场景，并重新检查受影响的 mustpass 覆盖。

这 2 项分别属于：

- **测试 oracle 覆盖限制：** `Shuffle` 某些 selector/source 组合可能没有任何有效的 exchange comparison。
- **feature/capability gate 与生成 artifact 不一致：** `UniformDescriptorIndexing` 过度要求 descriptor-class non-uniform-indexing feature，同时遗漏部分 dynamic-indexing feature 检查。

## 1. `Shuffle`：某些运行没有有效的 exchange comparison

**对应页面：** [Shuffle.md](../testfiles/subgroups/Shuffle.md)

**对应源码：** [`vktSubgroupsShuffleTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L227-L336)

### 背景：测试如何验证 source invocation

`Shuffle` 为每个 invocation 计算一个 source index，并将 subgroup built-in 返回的值与独立计算得到的 `data1[source]` 比较。shader 只有在计算出的 source invocation 同时处于范围内且在 ballot mask 中处于 active 状态时，才执行值比较；无法验证的 source 会直接写入成功标记 `1`。

这种 guard 对 inactive 或 out-of-range source 是有意的保护，但它也意味着：如果某次运行中所有 invocation 的 source 都无法验证，那么该次运行不会执行任何有效的 exchange comparison。

### 观察到的代码路径

页面的 runtime section 已记录这一边界：当计算出的 source invocation 全部 out of range 或 inactive 时，shader 只写入 `1` marker，不会执行 checked exchange comparison。页面还给出了一个具体例子：某些 `_constant_requiredsubgroupsize` 的 XOR、up 和 down case 在 subgroup size 小于字面量 selector `5` 时，所有预期 source 都会 out of range。

源码中的代表性逻辑位于 [`getNonClusteredTestSource()` 和 `getClusteredTestSource()`](../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L227-L336)：生成的 shader 通过 ballot 和范围判断决定是否比较；否则将结果设为成功。运行路径和 required-subgroup-size sweep 位于 [`test()`](../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L524-L595)。

### 为什么需要确认

这种运行仍可能通过 host callback，因为 host 看到的所有 marker 都是 `1`。因此，测试结果在这些参数组合中只能说明“没有观察到可验证的 mismatch”，不能证明 subgroup exchange operation 返回了正确的 source value。

这属于 oracle coverage limitation，不自动证明 `Shuffle` 实现错误，也不意味着所有 selector 组合都缺少有效比较。需要维护者确认测试设计是否有意接受不可验证运行，或者是否应约束 selector、subgroup-size 组合，确保每个代表性 case 至少执行一次有效 comparison。

### 需要维护者确认的问题

1. 对每个 operation、argument form 和 required subgroup size，是否应保证至少一个 invocation 的 source 同时 active 且在范围内？
2. `_constant_requiredsubgroupsize` 的 XOR、up 和 down case 是否应避开所有 source 都 out of range 的 subgroup-size 组合，或将这类组合标为不可验证？
3. 如果测试目标是覆盖 operation 的 source-selection 语义，是否应额外记录 checked-comparison 计数，并在计数为零时让 case 失败或显式报告？
4. 当 source 的 data value 偶然相同时，是否需要使用更强的输入构造或额外标记，降低错误 source 选择被掩盖的概率？
5. 修复或调整 oracle 后，能否为不同 operation、stage family 和 required-size sweep 增加至少一个有效 comparison 的回归检查？

相关证据：[`getNonClusteredTestSource()` / `getClusteredTestSource()`](../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L227-L336)，[`test()`](../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L524-L595)，[`checkComputeOrMesh()`](../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663)，以及页面中的 [runtime execution and result checking](../testfiles/subgroups/Shuffle.md#runtime-execution-and-result-checking) 说明。

## 2. `UniformDescriptorIndexing`：support-gating 与生成 shader artifact 不一致

**对应页面：** [UniformDescriptorIndexing.md](../testfiles/subgroups/UniformDescriptorIndexing.md)

**对应源码：** [`vktSubgroupsUniformDescriptorIndexingTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L625-L773)

### 背景：测试实际使用哪一种 descriptor indexing

该测试通过 `subgroupBroadcastFirst()` 和 peeling loop，使同一 subgroup 内当前访问的 descriptor index 保持 uniform；不同 subgroup 可以选择不同的 descriptor。生成的 fragment shader 开启 `GL_EXT_nonuniform_qualifier`，但实际 descriptor access 不使用 `nonuniformEXT(i)`。

因此，需要区分：

- runtime descriptor array 这一共同前置条件；
- dynamically uniform descriptor access 所需的 capability/feature；
- 真正使用 non-uniform descriptor index 时才需要的 descriptor-class non-uniform-indexing feature；
- 生成 artifact 声明的 dynamic-indexing capability 及其对应 feature。

### 观察到的代码路径

[`UniformDescriptorIndexingTestCase::checkSupport()`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L625-L684) 在确认 `runtimeDescriptorArray` 后，根据 descriptor type 要求对应的 `shader*ArrayNonUniformIndexing` feature，例如 storage buffer、uniform buffer、texel buffer、input attachment、sampler、sampled image、combined image sampler 和 storage image 的 non-uniform-indexing feature。

但生成 shader 的模板在 [`initPrograms()`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L686-L774) 中只通过 subgroup broadcast 和 peeling loop 访问 descriptor，并没有给 descriptor index 添加 `NonUniform` decoration，也没有声明 descriptor-class `...NonUniformIndexing` capability。另一方面，storage texel buffer、uniform texel buffer 和 input attachment 的生成 artifact 分别声明了 `StorageTexelBufferArrayDynamicIndexing`、`UniformTexelBufferArrayDynamicIndexing` 和 `InputAttachmentArrayDynamicIndexing`，而当前 `checkSupport()` 没有查询对应的 dynamic-indexing feature。

### 为什么需要确认

当前 gate 可能同时产生两类问题：

- **过度筛选：** descriptor access 实际保持 subgroup-uniform，但缺少 descriptor-class non-uniform-indexing feature 的设备会被跳过，即使 shader 可能能够合法执行。
- **检查不足：** 某些 artifact 声明了 dynamic-indexing capability，但对应 dynamic-indexing feature 没有在 `checkSupport()` 中明确检查；如果该 capability 需要 feature 支持，测试可能在不满足前置条件的设备上继续构建或执行。

这看起来像 support-gating defect，但最终结论仍需维护者结合 SPIR-V capability/feature 对应关系、CTS device feature enable 路径和实际 shader compilation 行为确认。文档不应把它直接定性为 Vulkan 实现或驱动缺陷。

### 需要维护者确认的问题

1. 这些生成 artifact 的 descriptor access 是否确实属于 dynamically uniform indexing，而不是 descriptor-class non-uniform indexing？
2. 九类 descriptor family 是否都应移除对应的 non-uniform-indexing gate，还是某些资源类型仍有额外的 Vulkan/ SPIR-V 前置条件？
3. storage-texel-buffer、uniform-texel-buffer 和 input-attachment artifact 所需的 dynamic-indexing feature 是否应加入 `checkSupport()`？
4. CTS 的 device feature enable 路径是否会隐式补齐这些 capability 所需的 features，还是必须在该 test case 中明确检查并启用？
5. 能否增加一个按 descriptor type 对照生成 SPIR-V capability/decorations 与 support gate 的回归测试，避免 gate 和 artifact 再次分离？

相关证据：[`checkSupport()`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L625-L684)，[`initPrograms()`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L686-L774)，页面中的 [runtime execution and result checking](../testfiles/subgroups/UniformDescriptorIndexing.md#runtime-execution-and-result-checking)，以及 Vulkan 的 [descriptor resource indexing rules](../../../vulkan-docs/src/chapters/interfaces.adoc#L1358-L1405) 和 [descriptor-indexing features](../../../vulkan-docs/src/chapters/features.adoc#L2004-L2077)。

## 关联材料

- [`subgroups` audit summary](subgroups_audit_summary.md)
- [`subgroups` category 页面](../categories/subgroups.md)
- [Vulkan CTS subgroups 源码目录](../../modules/vulkan/subgroups/)
