# drm_format_modifiers：待实现维护者确认的 Source-Level Finding

> 本文从 `drm_format_modifiers` category 的 audit summary 中抽取 1 项 unresolved finding，供 Vulkan CTS 实现维护者单独评估。它不表示 wiki 审计未完成，也不等同于已经确认的 Vulkan 实现缺陷。当前观察集中在 suballocation 测试的结果检查独立性和资源绑定路径。审计阶段没有修改 Vulkan CTS C++ 源码、mustpass、format list 或 Vulkan 规范文件。
>
> 对应 Level-3 页面已经记录当前可观察行为。本文只记录源码观察、影响范围和需要确认的问题，不替维护者决定测试是否需要修改，也不把任何失败直接归因于 Vulkan 实现或驱动。

## 处理建议

建议把该项目作为独立的源码调查或 issue：确认两个 suballocated image 的 copyback 是否应由独立的 host buffer 和独立的 comparison accessor 验证，并检查相关 image layout、allocation offset 与 queried properties 是否都来自对应的 source/destination image。若确认需要修复，应分别覆盖普通 suballocation、flags2 suballocation、不同 modifier、不同 format 以及全量 modifier 被跳过的 NotSupported 路径。

## `export_import_with_suballoc`：两个 image 的结果检查可能不独立

**对应页面：** [Modifiers.md](../testfiles/drm_format_modifiers/Modifiers.md)

**对应源码：** [`vktModifiersTests.cpp`](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1109-L1597)

### 观察到的代码路径

suballocation 测试把两个 DRM-modifier image 放入同一个 exportable allocation，并将第二个 image 绑定到经过 alignment 的 offset。随后它把两个 image 分别 copy 到 `outputBuffer` 和 `outputSubBuffer`。但是，当前 checking code 构造两个 `ConstPixelBufferAccess` 时都使用 `outputBuffer`，而不是分别使用两个 readback buffer：

- 两个 image 的 import、binding 和 copyback 路径见 [`exportImportMemoryExplicitModifiersWithSuballocationCase`](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1109-L1529)；
- 两个 result accessor 都从 `outputBuffer` 构造的代码位于同一函数的 checking 区域（见上述 source range）。

此外，审计还观察到 source 查询 `subDstProperties` 时使用了 `dstImage`，并且 `outSubImage` 在 output allocation 中绑定到 offset zero。这些对象对应关系需要维护者结合完整 helper 和 Vulkan external-memory binding 语义确认。

### 为什么需要确认

如果第二个 comparison accessor 实际读取的是第一个 output buffer，那么第二个 image 的 copyback 结果没有被独立观察。这样即使第一个 image 的结果正确，第二个 image 的错误也可能无法被该 oracle 区分；测试仍可能通过，但不能证明两个 suballocated image 都保留了预期内容。

这条发现目前不直接断言实现或驱动错误，因为需要确认：

- `outputBuffer` 与 `outputSubBuffer` 是否存在包装层别名或特殊映射；
- 两个 accessor 是否确实分别对应两个 copyback destination；
- `subDstProperties` 的来源是否是有意复用，还是应当读取 `subDstImage` 的 properties；
- `outSubImage` 的 zero offset 是否符合该 allocation 与 image binding 的完整构造。

### 需要维护者确认的问题

1. 两个 `ConstPixelBufferAccess` 是否应分别由 `outputBuffer` 和 `outputSubBuffer` 构造？
2. `subDstProperties` 是否应从 `subDstImage` 查询，而不是从 `dstImage` 查询？
3. `outSubImage` 绑定到 output allocation offset zero 是否与该 image 的 allocation size、alignment 和 memory requirements 一致？
4. 修复后是否需要同时回归 `export_import_with_suballoc` 和 `export_import_fmt_features2_with_suballoc` 的所有 131-format / runtime-modifier 组合？
5. 当所有 modifier 都被 dedicated-allocation 或其他 support 条件排除时，`NotSupportedError` 路径是否仍应保持当前语义？

### 建议调查与处置

1. 对照 `outputBuffer`、`outputSubBuffer`、`dstImage`、`subDstImage` 和 `outSubImage` 的完整声明、allocation、binding、copy region 与 accessor 构造，建立逐对象映射。
2. 开启 Vulkan validation，分别运行两个 suballocation family 的代表 format 和多个 modifier，确认是否报告 image memory requirements、binding offset、external-memory 或 copyback 相关错误。
3. 构造一个只破坏第二个 suballocated image 的回归场景，确认当前 oracle 是否能够失败；如果不能，修正第二个 output accessor 或相关 result path。
4. 修复后重新验证 131 个 format leaves、legacy/flags2 两条路径、modifier 全部 unsupported 的 pruning，以及 `git diff --check`。

相关证据：[`exportImportMemoryExplicitModifiersWithSuballocationCase`](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1109-L1597)，[DRM modifier properties](../../../vulkan-docs/src/chapters/formats.adoc#VkDrmFormatModifierPropertiesEXT)，[explicit modifier image creation](../../../vulkan-docs/src/chapters/resources.adoc#VkImageDrmFormatModifierExplicitCreateInfoEXT)。

## 关联材料

- [drm_format_modifiers audit summary](../internal_doc/drm_format_modifiers_audit_summary.md)
- [drm_format_modifiers category 页面](../categories/drm_format_modifiers.md)
- [DRM format modifier Level-3 页面](../testfiles/drm_format_modifiers/Modifiers.md)
- [Vulkan CTS modifier source](../../modules/vulkan/modifiers/vktModifiersTests.cpp#L1109-L1597)
