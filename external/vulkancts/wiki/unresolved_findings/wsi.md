# WSI category：待实现维护者确认的 Source-Level Findings

> 本文从 [WSI audit summary](wsi_audit_summary.md) 抽取 7 项未解决发现，供 Vulkan CTS 实现维护者逐项评估。它们不表示 wiki 审计未完成，也不等同于已经确认的 Vulkan 实现缺陷。共同点是：现有 C++ 测试实现、测试意图与 Vulkan 规范边界之间存在需要源码维护者判断的风险、不一致或覆盖缺口。审计阶段没有修改 Vulkan CTS C++ 源码、mustpass、规范文件或驱动实现。
>
> 本文只记录当前观察和需要确认的问题，不替维护者决定这些问题是否应修复，也不直接把任何失败归因于 Vulkan 实现或驱动。对应 Level-3 页面已经修正文档表述，使其反映当前实际行为。

## 处理建议

建议把每项作为独立的源码调查或 issue：先确认测试对象的生命周期、API 调用前置条件、错误结果传播和实际控制流，再决定是否修改测试实现。若确认需要修复，应补充能证明修复有效的回归场景，并重新检查相关 mustpass 覆盖。

这 7 项可以分成三类：

- **可能违反 API 使用前置条件：** `ColorSpaceTests` 的 image readback、`DisplayTests` 的无效 display-mode 参数和未确认的 identity transform。
- **可能遗漏错误或使检查不可达：** `PresentIdWaitTests` 的错误诊断、`Maintenance1Tests` 的 aggregate present result、`DisplayControlTests` 的 ownership gate 和 counter 检查。
- **需要确认测试意图与当前实现是否一致：** 某些问题可能是直接的源码缺陷，也可能是测试只想覆盖较窄的可观察行为。最终结论应由源码维护者结合运行环境和规范作出。

## 1. `ColorSpaceTests`：present 后读取尚未重新 acquire 的 swapchain image

**对应页面：** [ColorSpaceTests.md](../testfiles/wsi/ColorSpaceTests.md)

### 背景：surface color space 测试在比较什么

Vulkan 的 `VkSurfaceFormatKHR` 将一个图像格式和一个 `VkColorSpaceKHR` 配对。`colorspace_compare` 测试固定一个图像格式，例如 `VK_FORMAT_B8G8R8A8_UNORM`，然后为该格式支持的多个 color space 分别创建 swapchain。每个 swapchain 都绘制同一份三角形内容，present 一张图像，再读取一个固定像素，最后要求不同 color space 得到的原始像素值完全相同。

这个测试意图比较的是 **swapchain image 中的原始值**，不是显示器或 compositor 最终显示出来的颜色。正常情况下，读取某张 swapchain image 前必须先通过 `vkAcquireNextImageKHR` 取得它的使用权。

### 观察到的代码路径

在 [`colorspaceCompareTest`](../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L425-L563) 中，测试先 acquire image，提交绘制并调用 `vkQueuePresentKHR`。随后，对刚刚 present 的同一个 `swapchainImages[imageNdx]` 直接调用 `getPixel`：

```cpp
vkQueuePresentKHR(..., &swapchainImages[imageNdx], ...);

getPixel(..., &swapchainImages[imageNdx]);
```

代码在比较下一个 color space 时也沿用同一模式。它没有在 present 后重新调用 `vkAcquireNextImageKHR`。

### 为什么需要确认

WSI 规范规定，queue present 会释放对 presentable image 的 acquisition；在再次使用该 image 前，应用必须重新 acquire。当前代码在 present 后直接把 image 当作可读资源使用，触及了 Vulkan 的 image ownership / acquisition 前置条件。

因此，`getPixel` 返回相同或不同的值，都不能直接支持一个有效的 conformance 结论：

- 如果比较通过，不代表不同 color space 的行为已经被正确验证，因为读取动作本身不符合使用规则。
- 如果比较失败，也不能可靠地归因于实现改变了原始像素值，因为问题可能来自未重新 acquire 的访问。

这不是简单的“缺少一条检查”。它可能要求维护者重新设计测试流程，例如在合法重新 acquire 后再进行 readback，并确认 readback 所需的 layout、同步和 image 生命周期仍然正确。

### 需要维护者确认的问题

1. `getPixel` 的实现是否包含某种 CTS 内部同步或隐含的 image 使用约定，能否改变上述判断？
2. 如果不能，测试应在 present 后如何重新 acquire，才能继续比较同一张或等价的 swapchain image？
3. 重新 acquire 后，比较的对象是否仍然符合原测试意图，尤其是在 present 可能选择不同 image 的情况下？
4. 修复后是否需要分别覆盖六种注册格式和多个 color space，而不是只验证一个代表 case？

相关证据：[`colorspaceCompareTest`](../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L438-L545)，[Vulkan presentable-image reacquisition rule](../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7419-L7426)。

## 2. `PresentIdWaitTests`：version 2 wait 失败诊断仍然使用错误的 API 名称

**对应页面：** [PresentIdWaitTests.md](../testfiles/wsi/PresentIdWaitTests.md)

### 背景：version 1 和 version 2 的 wait 不是同一个入口点

present-ID 测试为每次 presentation 关联一个 ID，随后可以等待某个 ID 对应的 presentation 达到规范定义的状态。该 category 同时覆盖两套扩展接口：

- version 1 使用 `vkWaitForPresentKHR`；
- version 2 使用 `vkWaitForPresent2KHR`，并通过 `VkPresentWait2InfoKHR` 传入参数。

两者有相近的测试目的，但入口点、参数结构和部分 valid-usage 条件不同。读者如果只看到“wait 测试失败”，必须先知道实际执行的是哪一个版本。

### 观察到的代码路径

公共 runner 根据 `m_ver` 选择实际调用：

- `m_ver == 1` 时调用 `vkd.waitForPresentKHR`；
- 其他情况调用 `vkd.waitForPresent2KHR`。

但是在两条错误处理路径中，消息都写成了 `vkWaitForPresentKHR`，包括 timeout 结果不符合预期、等待时长超出测试范围以及普通 wait 失败的消息。具体见 [`wait` 执行循环](../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L633-L675)。

### 为什么需要确认

这不会改变 Vulkan API 的实际调用，但会污染测试日志和失败诊断。version 2 case 失败时，维护者或驱动开发者可能误以为失败发生在 version 1 入口点，进而：

- 追错扩展或 feature；
- 误读 valid-usage 条件；
- 在大量自动化日志中错误聚合失败；
- 对应错误的规范章节或实现路径。

它属于源码层面的诊断缺陷，修复方向看起来可能只是按 `m_ver` 选择消息文本，但仍需要确认所有分支和测试报告格式不会依赖现有字符串。

### 需要维护者确认的问题

1. 是否应在 version 2 分支使用 `vkWaitForPresent2KHR` 的诊断文本？
2. timeout-duration 日志是否也应根据版本选择 API 名称，或进一步统一为“present wait operation”？
3. 是否有脚本、测试基础设施或 issue triage 流程依赖当前错误字符串？

相关证据：[`wait` 执行循环](../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp#L633-L675)，[version 1 wait 规则](../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8206-L8265)，[version 2 wait 规则](../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8342-L8404)。

## 3. `Maintenance1Tests`：release_images 路径没有验证 aggregate present result

**对应页面：** [Maintenance1Tests.md](../testfiles/wsi/Maintenance1Tests.md)

### 背景：`vkQueuePresentKHR` 有两个相关的结果

`VkPresentInfoKHR` 中可以通过 `pResults` 为每个 swapchain 提供单独结果；`vkQueuePresentKHR` 自身也返回一个 aggregate result。单 swapchain 场景下两者通常相关，但它们不是同一个字段，测试不能仅凭其中一个就声称已经检查了另一个。

`release_images` 测试的核心是反复 acquire、提交、present，并在适当时机调用 `vkReleaseSwapchainImagesKHR`，验证旧 swapchain 或共享 present 模式下图像释放和再次 acquire 的生命周期。

### 观察到的代码路径

在 [`release_images` 的 present 循环](../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2475-L2551) 中：

1. `vkQueuePresentKHR` 的返回值保存到 `aggregateResult`；
2. `pResults` 中的单 swapchain result 保存到 `result`；
3. 如果任一结果是 `VK_ERROR_OUT_OF_DATE_KHR`，代码进入 swapchain recreate 分支；
4. 否则只执行两次 `VK_CHECK_WSI(result)`。

也就是说，正常分支没有检查 `aggregateResult`。如果 aggregate result 表示错误，而 `pResults[0]` 没有反映同一个错误，测试可能继续运行并最终报告成功。

### 为什么需要确认

这可能造成错误遗漏，尤其是该测试还会进行 image release、swapchain recreation 和资源回收。一个未被捕获的 aggregate present failure 可能在后续阶段表现为完全不同的错误，也可能被资源清理路径掩盖。

但需要维护者确认几个事实后才能决定修复方式：

- 对于当前只提交一个 swapchain 的调用，规范和各实现是否保证 aggregate result 与 `pResults[0]` 一致？
- `VK_CHECK_WSI(result)` 的宏是否包含某种额外处理，使得重复检查并非纯粹的疏漏？
- `VK_ERROR_OUT_OF_DATE_KHR` 等特殊结果是否应继续由 aggregate result 和 per-swapchain result 共同决定 recreate 行为？

### 需要维护者确认的问题

1. 正常分支是否应显式检查 `aggregateResult`？
2. 如果单 swapchain 时两种结果规范上必然一致，是否仍应保留检查以防止测试代码未来扩展到多 swapchain？
3. 修复后应增加哪种注入或回归场景，才能证明 aggregate 错误不会被遗漏？

相关证据：[`release_images` present/release loop](../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2475-L2551)，[present result 规则](../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7290-L7345)。

## 4. `DisplayControlTests`：platform ownership gate 使三个测试家族不可达

**对应页面：** [DisplayControlTests.md](../testfiles/wsi/DisplayControlTests.md)

### 背景：为什么 display-control 测试需要特殊平台

`VK_EXT_display_control` 的测试不是普通 window-system WSI 测试。它面向物理 display、surface counter、display power 和 display event 等功能，要求测试直接拥有可用的 display，而不是让 X11、Wayland、Android 或其他窗口系统先占用它。

测试启动时需要：

- `VK_KHR_swapchain`；
- `VK_EXT_display_control`；
- 可用的物理 display；
- 一个不会被当前 window system 访问的 display。

因此源码使用 `platform.hasDisplay(wsiType)` 检查 display ownership。

### 观察到的代码路径

[`createTestDevice`](../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L96-L143) 遍历所有 WSI 类型：只要有一个 `platform.hasDisplay(wsiType)` 返回 true，就把 `displayAvailable` 设为 false，随后抛出 `NotSupportedError`。

当前 Linux、Android、macOS 和 Windows 平台实现都至少对一个 WSI 类型返回 true。例如 Linux 的 `hasDisplay` 实现见 [`tcuLnxVulkanPlatform.cpp`](../../../../framework/platform/lnx/tcuLnxVulkanPlatform.cpp#L509-L539)。这意味着 `createTestDevice` 在这些常见平台上会把相关 case 直接筛掉。

受影响的三个注册家族是：

- `swapchain_counter`；
- `display_power_control`；
- `register_display_event`。

只有 `register_device_event` 的路径不经过这个 device/display 枚举 gate，能够继续到自己的测试逻辑。

### 为什么需要确认

从测试名称和扩展功能看，前三个家族应该验证具体的 counter、power 或 display event 行为；但当前平台 gate 可能让它们在进入这些操作前就变成 `NotSupported`。这样会造成两种可能：

1. gate 的条件写反或过于宽泛，导致本应在 direct-display 环境执行的测试被跳过；
2. 测试设计本来就只允许一种尚未覆盖的特殊平台状态，而当前仓库没有对应实现。

在未确认平台语义前，不能直接断言“测试永远不可达”，也不能单凭大量 `NotSupported` 把它归因于 driver 缺陷。需要维护者确认 `hasDisplay` 的约定究竟表示“系统拥有 display”还是“display 已被 window system 占用”，以及这个测试希望寻找哪一种状态。

### 需要维护者确认的问题

1. `platform.hasDisplay()` 在这里的语义是否与 `displayAvailable` 变量的使用一致？
2. direct-display 测试应该通过什么平台配置或 backend 才能执行？
3. gate 是否应该只检查当前测试选定的 WSI 类型，而不是遍历所有类型？
4. 如果这些家族确实无法在当前平台执行，是否应调整 registration、skip message 或 mustpass 预期？

相关证据：[`createTestDevice`](../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L96-L143)，Linux `hasDisplay` 实现（同上），[display-control specification](../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L1450-L1475)。

## 5. `DisplayControlTests`：surface counter 检查位于已结束的 frame loop 之后

**对应页面：** [DisplayControlTests.md](../testfiles/wsi/DisplayControlTests.md)

### 背景：surface counter 想验证什么

`VK_EXT_display_control` 的 `VK_SURFACE_COUNTER_VBLANK_EXT` counter 用来表示与显示刷新相关的计数。测试希望渲染并 present 一定数量的 frame，再读取 counter，检查它落在“已经提交的 frame 数量减去可能仍在队列中的 swapchain image 数量”和“总 frame 数量”之间。

这个范围检查的意图是允许 presentation engine 落后于 queue submission，同时仍检查 counter 不会明显越界。

### 观察到的代码路径

在 [`SwapchainCounterTestInstance::render`](../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L730-L760) 中，counter query 被放在：

```cpp
if (m_frameNdx >= m_frameCount)
{
    getSwapchainCounterEXT(...);
    ...
}
```

但是 `iterate()` 每次调用 `render()` 后才递增 `m_frameNdx`，并且当它达到 `m_frameCount` 时直接结束测试。也就是说，最后一次 `render()` 看到的仍是 `m_frameNdx == m_frameCount - 1`；counter query 在正常路径上不会被执行。

### 为什么需要确认

这使测试名称所暗示的 counter validation 与实际执行不一致。测试可能报告通过，但没有真正读取或检查 counter。即使修正了上一条 ownership gate，这条独立的控制流问题仍会使 counter oracle 不可达。

需要注意，不能仅凭代码中的注释判断这是 bug。维护者还应确认：

- `m_frameCount` 是否有特殊值或其他路径会使 `render()` 再执行一次；
- `iterate()` 的 incomplete/pass 状态是否可能在框架层重新进入一次；
- 该 query 是否原本应放在最后一次 render 内，还是应移到 `iterate()` 的终止逻辑中。

### 需要维护者确认的问题

1. counter query 是否确实应该在最后一个 frame present 后执行？
2. 期望的 counter 范围是否仍然适用于实际的 display refresh 和 queue/presentation 延迟？
3. 修复后如何在没有稳定物理 display 的 CI 中建立可重复的回归验证？

相关证据：[`render`](../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L730-L760)，[`iterate`](../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L762-L803)。

## 6. `DisplayTests`：用违反 valid usage 的参数验证 display mode 创建失败

**对应页面：** [DisplayTests.md](../testfiles/wsi/DisplayTests.md)

### 背景：display mode 创建的正常检查

Display mode 描述物理 display 的可用模式，例如可见区域大小和刷新率。测试先枚举已有 mode，选择第一个作为合法样本，然后调用 `vkCreateDisplayModeKHR` 创建一个相同参数的新 mode，最后确认内置 mode 列表数量没有异常变化。

在此之前，测试还执行三个 negative call，分别把：

- `refreshRate` 设为 `0`；
- `visibleRegion.width` 设为 `0`；
- `visibleRegion.height` 设为 `0`。

每次都要求返回 `VK_ERROR_INITIALIZATION_FAILED`。

### 观察到的代码路径

完整流程见 [`testCreateDisplayModeKHR`](../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1226-L1330)。它确实把这三个零值送入 Vulkan API，并把返回结果作为测试 oracle。

### 为什么需要确认

Vulkan 规范对 `VkDisplayModeParametersKHR` 明确要求 visible region 的 width、height 和 refresh rate 都必须大于零。这意味着这些调用违反 valid usage，不是一个可以安全用来测试实现“应返回什么运行时错误”的普通 negative test。

因此：

- 实现返回 `VK_ERROR_INITIALIZATION_FAILED`，只能说明它对这次 invalid call 做了某种处理，不能作为完整的 conformance 证据；
- 实现没有返回预期错误，也不能直接证明实现违反了 Vulkan conformance，因为调用方已经先违反了前置条件；
- validation layer 报告 valid-usage 错误、直接终止调用，或不同实现表现不同，都可能是合理的观察结果。

这并不影响同一测试中基于已枚举合法 mode 的创建、handle 检查和 builtin mode 数量稳定性检查。问题只集中在三个零值 negative calls 的 oracle。

### 需要维护者确认的问题

1. 这三个调用的原始测试意图是什么：验证 invalid input 的错误映射，还是验证实现不会创建零参数 mode？
2. 如果要测试错误处理，是否有不违反 valid usage、但规范明确要求返回错误的输入方式？
3. 这三个 negative calls 是否应移除、改为 validation-only 场景，或改用符合规范的边界输入？
4. 是否需要把合法 mode 的 conformance checks 与 invalid-input robustness checks 分成不同测试？

相关证据：[`testCreateDisplayModeKHR`](../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1263-L1327)，[VkDisplayModeParametersKHR valid usage](../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L1930-L1955)。

## 7. `DisplayTests`：创建 display surface 前未检查 identity transform 支持

**对应页面：** [DisplayTests.md](../testfiles/wsi/DisplayTests.md)

### 背景：display surface 创建需要匹配 plane 能力

display surface 创建时，`VkDisplaySurfaceCreateInfoKHR` 会指定 display mode、plane、alpha mode、transform 和 image extent。测试选择：

- 一个 full-display plane；
- `VK_DISPLAY_PLANE_ALPHA_OPAQUE_BIT_KHR`；
- `VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR`；
- 由 plane capability 得到的最小 destination extent。

其中 alpha 和 extent 可以从已查询的 plane capabilities 推导，但 transform 是否允许，属于 display 的 `supportedTransforms` 能力集合。

### 观察到的代码路径

在 [`testDisplaySurface`](../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1494-L1688) 中，源码检查了 full-display extent 和 opaque alpha 支持，然后无条件把 transform 写成 `VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR`，调用 `vkCreateDisplayPlaneSurfaceKHR`。它没有检查对应 display properties 的 `supportedTransforms` 是否包含 identity bit。

### 为什么需要确认

如果某个 display 不支持 identity transform，这个 create call 就可能违反 `VkDisplaySurfaceCreateInfoKHR` 的 valid usage。此时：

- create 失败可能只是调用方传入了不被支持的 transform，不能作为实现缺陷证据；
- create 成功也可能暴露实现对 invalid input 的宽松处理，不能直接说明测试建立了有效的 conformance 结论；
- 当前测试把返回值不是 `VK_SUCCESS` 直接作为 failure，可能把测试前置条件缺失误报成实现失败。

如果平台恰好所有 display 都支持 identity transform，这条路径在实际环境中可能不暴露，但源码仍然没有把这个前置条件显式化。

### 需要维护者确认的问题

1. 测试是否应在创建前检查 `supportedTransforms` 并跳过不支持 identity 的 display/plane？
2. 如果测试目标就是 identity transform surface，是否应把 transform support 作为明确的 test prerequisite，而不是隐式假设？
3. 若测试希望覆盖非 identity transform，是否应按能力枚举选择合法 transform 并分别验证？
4. 针对不支持 identity 的 display，预期是 skip、选择另一 transform，还是保留 negative test？

相关证据：[`testDisplaySurface`](../../modules/vulkan/wsi/vktWsiDisplayTests.cpp#L1494-L1688)，[VkDisplaySurfaceCreateInfoKHR valid usage](../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2275-L2334)。

## 关联材料

- [WSI audit summary](wsi_audit_summary.md)
- [WSI category 页面](../categories/wsi.md)
- [Vulkan CTS WSI 源码目录](../../modules/vulkan/wsi/)
- [draw unresolved findings 文档（结构参考）](draw_unresolved_findings.md)
