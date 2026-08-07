# draw category：待实现维护者确认的 Source-Level Findings

> 本文从 audit summary report (已删除) 抽取 5 项未解决发现，供 CTS 实现维护者单独评估。它们不表示 wiki 审计未完成，也不等同于已经确认的 Vulkan 实现缺陷；共同点是：现有 C++ 或 Amber 测试实现、测试意图与规范边界之间存在需要源码维护者判断的风险、覆盖缺口或不一致。审计阶段没有修改 C++、Amber、mustpass 或规范文件。

## 处理建议

建议把每项作为独立的源码调查/issue：先复现或建立最小回归用例，确认 CTS 框架中相关对象的实际生命周期、dispatch table 所属 device、Amber 图像内容与规范定义域；只有在确认行为不符合测试意图或规范后，才修改测试源码并添加覆盖该修复的回归场景。wiki 页面已描述当前可观察行为，但不应把下述项目表述为已经定性的 driver conformance failure。

## 1. `AhbExternalFormatResolveTests`：显式析构后的资源生命周期

**对应页面：** [AhbExternalFormatResolveTests.md](../testfiles/draw/AhbExternalFormatResolveTests.md)

### 观察到的代码路径

在非 input-attachment 的 direct-read 路径中，测试需要先释放仍引用 Android Hardware Buffer（AHB）的 Vulkan image，才能将 AHB 锁定为 `CPU_READ`。为此，它对普通数据成员 `m_resources` 直接调用显式析构：

```cpp
m_resources.~DrawResources();
```

随后代码锁定 AHB、复制或解压其内容、解锁 AHB，并继续使用局部 `cpuTexture` 完成结果验证。可直接查看 [显式析构与 CPU readback 路径](../../modules/vulkan/draw/vktDrawAhbExternalFormatResolveTests.cpp#L195-L245)。

### 为什么需要确认

显式调用成员对象的析构函数本身不重建该对象。测试实例之后按正常 C++ 生命周期销毁时，`m_resources` 仍是一个成员，编译器生成的析构过程通常还会再次析构它。这里是否安全取决于 `DrawResources` 的具体析构语义、成员的实际所有权关系，以及该显式析构是否被后续代码或框架保证为可重入/幂等；仅凭当前调用点无法安全地把它定性为确定的 double-destruction bug。

若资源析构不是幂等的，风险包括二次释放 Vulkan handle、访问已释放的 allocation，或只在特定 AHB format/direct-read path 上出现不稳定行为。反过来，如果 `DrawResources` 的内部成员全部采用能够安全空析构的包装类型，也可能只是非常规但可运行的写法。

### 建议调查与处置

1. 检查 `DrawResources` 的定义和析构链，确认显式析构后其成员是否会在测试实例最终析构时再次释放同一资源。
2. 用 ASan/UBSan、Vulkan validation 或针对 direct-read AHB path 的压力运行验证是否存在二次销毁或 use-after-free。
3. 若需要提前释放 image，优先评估以 `reset()`、受控 optional/指针所有权，或单独的明确 cleanup API 表达“提前释放”的设计，避免显式析构仍存活的普通成员。
4. 修复后应回归 RAW10、RAW12、RAW16 与非 raw 格式，以及 input-attachment 和 direct-read 两类结果路径。

## 2. `ConcurrentTests`：compute device 的 dispatch interface 被用于 draw device

**对应页面：** [ConcurrentTests.md](../testfiles/draw/ConcurrentTests.md)

### 观察到的代码路径

测试先创建 custom compute device，随后以该 `computeDevice` 构造 `vk::DeviceDriver`，并把它绑定为局部 `vk::DeviceInterface`：

- [创建 `computeDevice` 和 `DeviceDriver`](../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L210-L232)

后续 draw 路径却使用这个 `vk` interface 对 `drawDevice` 创建 fence、提交 `drawQueue`，并以 `drawDevice` 等待该 fence：

- [draw fence 创建、两个 queue submit 与 fence wait](../../modules/vulkan/draw/vktDrawConcurrentTests.cpp#L397-L437)

计算 workload 修改 storage buffer，图形 workload 写入独立 color target；两次提交没有 semaphore wait/signal，因此它们不是 producer-consumer 同步测试。问题集中在 device-level function dispatch 与对象所属 device 是否匹配，而不是两项 workload 之间缺少同步。

### 为什么需要确认

Vulkan device-level function pointer 是通过特定 logical device 的 `vkGetDeviceProcAddr` 语义取得的；它应只用于该 device 或其 child objects。若 `computeDevice` 与 `drawDevice` 确实不同，用由前者建立的 `DeviceDriver` 调用后者的 queue/fence 操作违反了这一 ownership 边界，可能在 loader、ICD 或不同硬件/多 device 配置下产生未定义或失败行为。

不过，需先确认该测试的上下文是否在所有实际执行配置中保证两个 handle 相同，或 `DeviceDriver` 的包装层是否有额外的保证。即使常见配置里它们恰好相同，这种代码结构仍会掩盖测试真正要验证的“独立并发 workload”语义。

### 建议调查与处置

1. 明确记录 `computeDevice` 与 `drawDevice` 在各目标配置中是否可以不同；在可区分的设备配置运行该 case。
2. 为每个 logical device 使用与该 device 对应的 `DeviceDriver` / `DeviceInterface`；`drawFence`、`drawQueue` submit 和 draw fence wait 应走 draw-device interface。
3. 保留计算与绘制的独立验证，但将该修复与任何跨 queue 同步断言区分开；当前 source 没有跨 workload 的资源依赖。
4. 修复后增加能覆盖不同 device-dispatch ownership 的测试配置或断言，避免“同一 device 恰好掩盖错误”。

## 3. `DepthBiasTests`：Amber 验证 oracle 不能区分预期绿色与未写入的 opaque black

**对应页面：** [DepthBiasTests.md](../testfiles/draw/DepthBiasTests.md)

### 观察到的代码路径

以 `depth_bias_triangle_list_fill.amber` 为例，两个图像先清为 opaque black，之后 compute verifier 读取 `resultImage`。若像素满足 `color.r == 0.0 && color.a == 1.0`，它就在 `verifyImage` 写绿色；否则写红色。最后要求整个 `verifyImage` 都为绿色：

- [清屏、两个 draw、compute verifier 与全图 EXPECT](../../data/vulkan/amber/draw/depth_bias/depth_bias_triangle_list_fill.amber#L138-L179)

### 为什么需要确认

这个判据只观察 red 和 alpha。预期成功的绿色像素具有 `r == 0, a == 1`，但没有被任何 draw 写到、仍保持 clear color 的 opaque black 像素也同样具有 `r == 0, a == 1`。二者都会被 verifier 写成绿色，因此最终全绿并不能证明每个预期被覆盖的位置真的发生了正确的绿色绘制。

这更准确地说是 **oracle coverage limitation**：它允许某一类“预期绿色区域未被写入，仍为 clear color”的错误逃逸。它不自动证明所有 depth-bias case 都错误，也不意味着结果必然存在 false pass；但它削弱了该 verifier 对覆盖、颜色分量或特定 rasterization failure 的区分能力。

### 建议调查与处置

1. 对照每个 Amber case 的期望区域，确认测试意图究竟是“全部像素 red=0 且 alpha=1”，还是“指定区域必须为某个精确颜色、其余区域必须保持 clear color”。
2. 若意图包含对绘制覆盖的验证，改用能区分 green 和 black 的完整 `RGBA` 比较，或至少同时检查 green 分量/预期覆盖 mask。
3. 将 depth-bias 的深度行为验证与颜色覆盖验证分开：前者可检查 depth/stencil 或专用 reference，后者使用明确的 color mask。
4. 修复 oracle 后，增加一个刻意不绘制或错误裁剪的负向变体，验证它确实会从绿色变为红色并失败。

## 4. `InvertedDepthRangesTests`：fixed-point depth 在规范未定义域上的饱和 reference

**对应页面：** [InvertedDepthRangesTests.md](../testfiles/draw/InvertedDepthRangesTests.md)

### 观察到的代码路径

reference 生成器对 depth attachment 使用 `VK_FORMAT_D16_UNORM_S8_UINT`，插值顶点 depth 后，先将值夹到 `[0,1]`，再映射到 `minDepth`/`maxDepth`，最后在启用 depth clamp 时夹到该 viewport 的 depth range：

- [reference image 的 depth 计算、`[0,1]` clamp 与写入](../../modules/vulkan/draw/vktDrawInvertedDepthRangesTests.cpp#L363-L457)

但是 Vulkan 规范在 `VK_EXT_depth_range_unrestricted` 存在且 attachment 是 fixed-point format 时说明：若 depth-clamping/range-adjustment 后 fragment depth 不在 `[0,1]`，该 depth 在后续步骤中是 undefined：

- [Vulkan spec：depth clamping/range adjustment 与 fixed-point undefined domain](../../../vulkan-docs/src/chapters/fragops.adoc#L1859-L1903)

### 为什么需要确认

当前 reference 将 source 计算得到的值转换为可存入 D16_UNORM 的饱和值，并将其用于逐像素 depth comparison。对于规范已声明为 undefined 的 outside-range fixed-point fragment depth，任何 driver 的不同表现都不能可靠地作为 conformance failure 或 pass 的依据；reference 给出一个确定的饱和值，并不让该域重新变成规范定义的行为。

颜色观察仍可能有价值，且处于规范定义域内的 depth case 仍可作为 conformance test。局限只针对“在 fixed-point attachment 上，经过相关 depth 变换后进入 `[0,1]` 外”的 depth-only 断言。需要由维护者判断该测试数据是否实际覆盖这一域，以及预期的覆盖边界应如何编码。

### 建议调查与处置

1. 枚举参数组合，确认哪些 `minDepth`、`maxDepth`、depth-bias、depth-clamp 状态和像素实际得到 outside-`[0,1]` 的 fixed-point depth。
2. 对这些组合，选择其一：限制输入/attachment 使 depth 留在定义域；改用适合 unrestricted-depth 语义的 floating-point attachment；或明确跳过 depth-only comparison，只保留有定义的观察。
3. 将 reference 中“为 host image 生成可表示值”的计算与“规范允许用作 conformance oracle 的值”分离，避免饱和实现细节被误认为 spec expectation。
4. 为定义域内与定义域外的 case 分别添加说明和回归，确保后续改动不会重新把 undefined-domain comparison 当作稳定 oracle。

## 5. `NegativeViewportHeightTests`：zero-height root 没有选择 zero-height 分支

**对应页面：** [NegativeViewportHeightTests.md](../testfiles/draw/NegativeViewportHeightTests.md)

### 观察到的代码路径

`createNegativeViewportHeightTests()` 与 `createZeroViewportHeightTests()` 都构造：

```cpp
SubGroupParams subGroupParams{false, groupParams};
```

随后分别用不同 root 名称注册 group：

- [两个 factory 的参数与 root 名称](../../modules/vulkan/draw/vktDrawNegativeViewportHeightTests.cpp#L1002-L1014)

因此，尽管 `zero_viewport_height` root 的注释和页面意图是测试 zero-height viewport，它传入的布尔值与 negative-height root 完全相同。根据该页审计时追踪到的 `SubGroupParams` 分支选择，这会让 zero-height root 走 negative-height 配置，而不是预期的 zero-height 分支。

### 为什么需要确认

mustpass hierarchy 仍然有独立的 `negative_viewport_height` 与 `zero_viewport_height` 名称，且二者可各自展开相同的 front-face/cull-mode leaves；但测试名称、页面说明和实际 parameter selection 可能没有对应到不同的运行行为。结果是：zero-height root 可能只是 duplicate coverage，真正的 zero-height 行为未被执行或未被验证。

这里最重要的是确认 `SubGroupParams` 的布尔字段语义以及 `populateTestGroup` 对它的使用。若字段确实是 zero-height selector，则这很可能是直接的 source/intent mismatch；若还有其他路径覆写它，则需要据完整控制流重新判断。

### 建议调查与处置

1. 从 `SubGroupParams` 定义一路跟踪到 `populateTestGroup` 和 viewport construction，确认该布尔值是否就是 zero-height selector。
2. 将 negative-height 与 zero-height root 的实际 `VkViewport::height`、front-face/cull setup、reference image 与 pass/fail 条件打印或以测试日志验证。
3. 若 zero-height root 本应选择另一分支，改为正确的参数值，并确认全部八个 front-face/cull leaves 的 expected output 与规范语义一致。
4. 增加回归断言，确保两个 root 不会只因名称不同而运行同一配置；也应复核 negative-height 与 zero-height 的 mustpass 覆盖是否仍与修复后的行为匹配。

## 关联材料

- [draw category 页面](../categories/draw.md)
- [Vulkan CTS draw 源码目录](../../modules/vulkan/draw/)
