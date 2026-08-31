# protected_memory category：待实现维护者确认的 Source-Level Finding

> 本文从 [protected_memory audit summary](../internal_doc/protected_memory_audit_summary.md) 抽取 1 项未解决发现，供 Vulkan CTS 实现维护者单独评估。它不表示 wiki 审计未完成，也不等同于已经确认的 Vulkan 实现缺陷。问题集中在当前 C++ 测试实现传入 `vkCmdCopyBuffer` 的 source buffer usage 与 Vulkan valid usage 要求之间的疑似不一致。审计阶段没有修改 Vulkan CTS C++ 源码、mustpass 或规范文件。
>
> 本文只记录当前观察、影响范围和需要确认的问题，不替维护者决定测试是否应修改，也不把任何失败直接归因于 Vulkan 实现或驱动。对应 Level-3 页面已经记录当前实现行为，并将该项目标记为 unresolved。

## 处理建议

建议把该项目作为独立的源码调查或 issue：先确认普通 buffer-copy 路径与 `VK_KHR_device_address_commands` 路径的实际测试意图、资源 usage 构造和不同构建条件，再决定是修正测试 source buffer 的 usage、调整测试操作，还是确认当前调用在目标扩展语义下有额外前置条件。若确认需要修复，应补充覆盖普通和 device-address copy 路径的回归场景，并重新检查相关 mustpass 覆盖。

## 1. `FillUpdateCopyBuffer`：copy source buffer 缺少 `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`

**对应页面：** [FillUpdateCopyBuffer.md](../testfiles/protected_memory/FillUpdateCopyBuffer.md)

### 背景：`vkCmdCopyBuffer` 对 source buffer 的要求

`vkCmdCopyBuffer` 从 source buffer 读取数据并写入 destination buffer。source buffer 必须声明 `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`，destination buffer 必须声明 `VK_BUFFER_USAGE_TRANSFER_DST_BIT`。这是 command valid usage 的前置条件，不是测试运行时可以随意忽略的资源配置细节。

该测试的 `copy` 家族还包括受保护的 buffer memory copy 路径。普通路径和 device-address 路径都需要分别确认 source、destination 资源 usage 与实际 copy 命令的要求是否匹配。

### 观察到的代码路径

在 [`FillUpdateCopyBufferTestInstance::iterate`](../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L140-L179) 中，测试构造 usage：

```cpp
vk::VkBufferUsageFlags srcUsage =
    vk::VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT | vk::VK_BUFFER_USAGE_TRANSFER_DST_BIT;

vk::VkBufferUsageFlags dstUsage = srcUsage | vk::VK_BUFFER_USAGE_TRANSFER_DST_BIT;
```

随后测试把 `srcBuffer` 创建为 `dstUsage`，把 `dstBuffer` 创建为 `srcUsage`。因此，普通 `copy` 路径中的 source buffer 实际包含 `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` 和 `VK_BUFFER_USAGE_TRANSFER_DST_BIT`，但没有 `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`：

- source buffer：由 `dstUsage` 创建，但没有 transfer-source usage；
- destination buffer：由 `srcUsage` 创建，也没有新增 transfer-destination usage，因为该 bit 已经包含在 `srcUsage` 中。

普通 buffer copy 随后把这两个对象作为 source 和 destination 传给 `vkCmdCopyBuffer`，见 [`copy` command path](../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L237-L289)。Vulkan valid usage 对应于 [`copy_buffer_common.adoc`](../../../vulkan-docs/src/chapters/commonvalidity/copy_buffer_common.adoc#L23-L25) 和 [`vkCmdCopyBuffer` specification text](../../../vulkan-docs/src/chapters/copies.adoc#L123-L131)。

在 device-address 分支中，测试使用 `vkCmdCopyMemoryKHR` 和两个 `VkDeviceAddressRangeKHR`，而不是 `vkCmdCopyBuffer`。该路径的 source/destination address ranges 仍来自同一对 buffer allocation，维护者需要单独确认 `VK_KHR_device_address_commands` 对 source memory 和 destination memory 的要求，以及当前 usage 构造是否足够。

### 为什么需要确认

如果普通 copy 路径确实要求 source buffer 带有 `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`，当前测试就可能在执行一个违反 valid usage 的 `vkCmdCopyBuffer` 调用。这样会削弱该测试作为 protected buffer copy conformance 检查的有效性：

- 如果实现接受调用并通过，不能据此证明 protected buffer copy 行为满足规范，因为调用方已经没有满足 source usage 前置条件。
- 如果实现拒绝调用、触发 validation error 或报告其他错误，也不能直接归因于 protected-memory 实现缺陷，问题可能来自 CTS 自身的 resource declaration。
- 如果测试在某些实现上继续运行，结果差异可能来自实现对 invalid usage 的处理，而不是被测的 protected copy 语义。

该观察目前只证明源码中的 usage 构造与普通 `vkCmdCopyBuffer` 的 valid-usage 条件存在疑似不一致。它还不能单凭静态阅读确定所有构建条件、包装层或 device-address 路径是否提供了额外保证，因此应由实现维护者确认后再决定处置。

### 需要维护者确认的问题

1. 普通 `copy` 路径是否应把 `VK_BUFFER_USAGE_TRANSFER_SRC_BIT` 加到 `srcBuffer` 的 usage 中，并保持 `dstBuffer` 的 transfer-destination usage？
2. `srcUsage` 与 `dstUsage` 的命名和实际绑定对象是否写反，是否存在测试原本想覆盖但没有覆盖的 source/destination usage 组合？
3. device-address 分支的 `vkCmdCopyMemoryKHR` 是否有独立的 usage 或 memory-access 前置条件，当前 allocation 是否满足这些条件？
4. 该问题是否在 `primary`、`secondary`、float/integer/unsigned 三种类型，以及 static/random cases 中具有相同影响？
5. 修复后是否需要为普通 `vkCmdCopyBuffer` 和 `vkCmdCopyMemoryKHR` 分别增加回归验证，并重新确认 protected submission 与 buffer-validator 结果？

### 建议调查与处置

1. 对照当前 Vulkan headers、`VK_KHR_device_address_commands` 规范文本和 validation layer 行为，确认普通 `vkCmdCopyBuffer` source usage 的适用条件。
2. 运行普通 protected `copy` cases，并开启 Vulkan validation，记录是否报告 `VK_BUFFER_USAGE_TRANSFER_SRC_BIT` 相关 valid-usage 错误。
3. 分别检查 `primary`、`secondary`、`static`、`random` 和三种 typed-buffer 分支，确认问题不是某一个 registration branch 的局部构造错误。
4. 如果确认 source usage 缺失，修正测试资源构造后重新生成或检查 mustpass 覆盖，确保普通和 device-address copy paths 都有有效回归。
5. 在源码修复前，不把该测试的 copy 失败直接解释为 protected-memory driver 或 hardware failure。

相关证据：[`FillUpdateCopyBufferTestInstance::iterate`](../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L140-L179)，[`copy` command path](../../modules/vulkan/protected_memory/vktProtectedMemFillUpdateCopyBufferTests.cpp#L237-L289)，[`copy_buffer_common.adoc`](../../../vulkan-docs/src/chapters/commonvalidity/copy_buffer_common.adoc#L23-L25)，[`vkCmdCopyBuffer` specification text](../../../vulkan-docs/src/chapters/copies.adoc#L123-L131)，以及 [FillUpdateCopyBuffer.md](../testfiles/protected_memory/FillUpdateCopyBuffer.md)。

## 关联材料

- [protected_memory audit summary](../internal_doc/protected_memory_audit_summary.md)
- [protected_memory category 页面](../categories/protected_memory.md)
- [Vulkan CTS protected_memory 源码目录](../../modules/vulkan/protected_memory/)
- [Vulkan protected memory specification](../../../vulkan-docs/src/chapters/memory.adoc#L5564-L5654)
