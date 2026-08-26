# texture category：待实现维护者确认的 Source-Level Findings

> 本文从 [texture audit summary](texture_audit_summary.md) 抽取 5 项未解决发现，供 Vulkan CTS 实现维护者逐项评估。它们不表示 wiki 审计未完成，也不等同于已经确认的 Vulkan 实现缺陷。共同点是：当前 C++ 或 Amber 测试实现、测试意图和 Vulkan 规范前置条件之间存在风险、不一致或覆盖缺口，需要源码维护者结合实际运行结果作出判断。
>
> 文档审计没有修改 C++、Amber、mustpass 或 Vulkan 规范。对应 Level-3 页面已经改为描述当前可观察行为，并提醒读者不要在排除测试侧问题前把失败归因于驱动。

## 处理建议

建议把每项作为独立的源码调查或 issue。先确认相关 feature 是否真正启用、测试 oracle 是否与执行序列一致、运行路径是否到达预期检查，再决定是否修改测试。若确认需要修复，应添加能够区分修复前后行为的回归场景，并重新检查受影响的 mustpass 路径。

这 5 项可按问题性质分为三类：

- **设备 feature 或 capability gate 不完整：** `Mipmap` 的 gather custom device、`TexelBuffer` 的 BGRA SNORM support requirement。
- **软件 reference 或 Amber oracle 与实际数据路径不一致：** `Shadow` 的浮点 depth clamp、`Multisample` 的 R64 expected value。
- **测试执行了没有满足规范前置条件的访问：** `Multisample` 的 invalid sample index writes。

## 1. `Mipmap`：gather custom device 未注册 `robustImageAccess2`

**对应页面：** [Mipmap.md](../testfiles/texture/Mipmap.md)

### 背景：`min_lod_gather` 想验证什么

`texture.mipmap.min_lod_gather` 创建三层 mip image，并通过 `VK_EXT_image_view_min_lod` 设置 image-view minimum LOD。`minlod_0_1` 的整数 minimum LOD 仍是 0，因此 base level gather 有定义；`minlod_1_1` 的整数 minimum LOD 是 1，shader 却仍从 base level 执行 `textureGather`。

后一个 case 依赖 `robustImageAccess2`。按测试注释和页面当前解释，低于 image-view minimum LOD 的 gather 应返回零，而不是 level 0 或 level 1 的颜色。

### 观察到的代码路径

[`TextureGatherMinLodTest::checkSupport()`](../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L2809-L2828) 查询 robustness2 features，并在 `robustImageAccess2` 不受支持时跳过测试。`minlod_1_1` 还通过 `getRequiredCapabilitiesId()` 选择 custom device。

但该 custom device 的 [`initDeviceCapabilities()`](../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L2728-L2745) 注册的是：

```cpp
caps.addFeature(&VkPhysicalDeviceRobustness2FeaturesEXT::robustBufferAccess2);
caps.addFeature(&VkPhysicalDeviceFeatures::robustBufferAccess);
```

这里没有注册 `VkPhysicalDeviceRobustness2FeaturesEXT::robustImageAccess2`。测试的 support check 因而证明 physical device 支持该 feature，却没有从这个函数看出 custom logical device 会启用它。

### 为什么需要确认

若 custom device 最终没有启用 `robustImageAccess2`，shader 不能依赖 robustness2 规定的 image out-of-bounds 返回值。此时 `minlod_1_1` 的非零结果或其他异常不能直接作为实现不符合 image-view minimum LOD 规则的证据。

仍需维护者确认 custom-device builder 是否在其他公共路径中自动复制或启用 `robustImageAccess2`。如果没有，这是一处 capability declaration 与测试 oracle 不匹配的问题；如果有隐式启用路径，当前注册方式至少不够清楚，容易在设备创建逻辑变化后失效。

### 需要维护者确认的问题

1. `TextureGatherMinLodTest` 的 custom device 最终是否启用了 `robustImageAccess2`？
2. `initDeviceCapabilities()` 是否应把 `robustBufferAccess2` 改为或补充为 `robustImageAccess2`？
3. `minlod_0_1` 使用默认 device 时，是否还应显式检查并启用 `minLod` feature？
4. 能否增加一个启动时断言或 device-feature 回读，证明运行 oracle 所依赖的 feature 已启用？

相关证据：[`TextureGatherMinLodTest` capability 和 support 路径](../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L2713-L2828)，[`min_lod_gather` 注册](../../modules/vulkan/texture/vktTextureMipmapTests.cpp#L4188-L4195)。

## 2. `Shadow`：浮点 depth 软件 reference 假设 upload 会 clamp

**对应页面：** [Shadow.md](../testfiles/texture/Shadow.md)

### 背景：浮点 depth 数据如何进入比较 oracle

`texture.shadow` 的部分 case 使用浮点 depth format。测试生成的 gradient 可以包含 `[0,1]` 之外的值。device 侧通过 shadow sampler 读取 texture 并执行 Dref comparison，host 侧则用 CTS software sampler 构造允许结果。

要让两边可比较，software reference 必须使用与 Vulkan image 中实际存储数据相同的值。这里的关键问题不是 Dref 对 UNORM format 的 clamp，而是上传到浮点 depth image 的 texel 本身是否会被 clamp。

### 观察到的代码路径

[`verifyTexCompareResult()`](../../modules/vulkan/texture/vktTextureShadowTests.cpp#L155-L191) 对浮点 depth texture 复制一份 software source，然后调用 `clampFloatingPointTexture()`。旁边的注释说明它假定 texture upload 会把浮点 depth 数据限制到 `[0,1]`，所以 software copy 也要做相同处理。

Vulkan upload 路径却没有显示这种数值转换：

- [`TestTexture::write()`](../../modules/vulkan/pipeline/vktPipelineImageUtil.cpp#L923-L967) 以相同 format 把 source texel 复制到 staging memory；
- Vulkan 的 [depth/stencil aspect copy 规则](../../../vulkan-docs/src/chapters/copies.adoc#L903-L947) 把 `VK_FORMAT_D32_SFLOAT` depth aspect 作为同一 `VK_FORMAT_D32_SFLOAT` texel block 复制。

在已检查的路径中，没有找到把浮点 depth texel clamp 到 `[0,1]` 的 upload-time conversion。

### 为什么需要确认

如果 device image 保留 `[0,1]` 外的 `D32_SFLOAT` 值，而 software reference 把这些值先 clamp，二者从验证开始就不是同一份 texture。某些 compare operation、过滤区域或 mip level 可能因此产生 false failure，也可能使真正的采样问题被错误 reference 掩盖。

这条发现仍保留为未解决项，因为需要维护者确认完整 upload helper、format decode 和 shadow sampling 规则中是否还有未追踪到的 clamp。还应确认这段注释是否从 OpenGL 测试移植而来，并误把 GL texture upload 语义带入 Vulkan 路径。

### 需要维护者确认的问题

1. Vulkan 路径中是否存在任何明确规则或 helper，会在 `D32_SFLOAT` buffer-to-image copy 或后续读取前 clamp depth texel？
2. 如果没有，software reference 是否应直接使用未 clamp 的浮点 source？
3. 当前参数矩阵中哪些 case 实际采样到了 `[0,1]` 外的浮点 depth 值？
4. 能否添加一个专门包含负值和大于 1 值的最小 case，用来验证 device image 与 software reference 的实际约定？

相关证据：[`verifyTexCompareResult()`](../../modules/vulkan/texture/vktTextureShadowTests.cpp#L155-L191)，[`TestTexture::write()`](../../modules/vulkan/pipeline/vktPipelineImageUtil.cpp#L923-L967)，[Vulkan buffer-image depth aspect copy](../../../vulkan-docs/src/chapters/copies.adoc#L903-L947)。

## 3. `TexelBuffer`：BGRA SNORM case 查询了 SINT format capability

**对应页面：** [TexelBuffer.md](../testfiles/texture/TexelBuffer.md)

### 背景：uniform texel buffer 的 format gate

Uniform texel buffer 只能使用在 `bufferFeatures` 中声明了 `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT` 的 format。`texture.texel_buffer.uniform.snorm` 因此会在运行 Amber recipe 前查询非 mandatory format 的能力；不支持的 format 应报告 `NotSupported`，而不是进入测试后失败。

`b8g8r8a8-snorm` 的实际测试对象是 `B8G8R8A8_SNORM` buffer view。shader 通过 `samplerBuffer` 读取 SNORM 数据，并检查 signed-normalized conversion 和 component order。

### 观察到的代码路径

[`createUniformTexelBufferTests()`](../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L120-L158) 的 case table 写成：

```cpp
{"b8g8r8a8-snorm", false, VK_FORMAT_B8G8R8A8_SINT},
```

随后这一个 `format` 被加入 `BufferRequirement`。[`AmberTestCase::checkSupport()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L270-L282) 对它调用 `getPhysicalDeviceFormatProperties()` 并检查 `bufferFeatures`。

但对应的 [`b8g8r8a8-snorm.amber`](../../data/vulkan/amber/texture/texel_buffer/uniform/snorm/b8g8r8a8-snorm.amber#L29-L50) 明确创建：

```text
BUFFER texel_buffer DATA_TYPE B8G8R8A8_SNORM DATA
```

support gate 查询的是 SINT，实际 buffer view 使用的是 SNORM。

### 为什么需要确认

`VK_FORMAT_B8G8R8A8_SINT` 和 `VK_FORMAT_B8G8R8A8_SNORM` 的 `bufferFeatures` 不必相同。当前代码可能产生两种错误：

- SINT 支持 uniform texel buffer、SNORM 不支持时，case 通过 gate 后在 Amber 资源创建阶段失败；
- SNORM 支持、SINT 不支持时，本可执行的 SNORM case 被错误跳过。

测试名称、recipe 和同一表中其他 SNORM entries 都指向 SNORM，因此这很像一处 format 常量笔误；正式修复前仍应由维护者确认是否有特殊设计理由。

### 需要维护者确认的问题

1. 该 table entry 是否应改为 `VK_FORMAT_B8G8R8A8_SNORM`？
2. Amber engine 是否还会独立检查实际 SNORM buffer-view format，从而只影响 skip 行为而不会产生非法创建？
3. 是否应增加 table-to-recipe 一致性检查，避免 test name、support format 和 Amber `DATA_TYPE` 再次分离？
4. 修复后能否在 SINT 与 SNORM capability 不同的实现或 mock feature table 上验证 accept/skip 行为？

相关证据：[`b8g8r8a8-snorm` registration](../../modules/vulkan/texture/vktTextureTexelBufferTests.cpp#L127-L155)，[`AmberTestCase::checkSupport()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L270-L282)，[`b8g8r8a8-snorm.amber`](../../data/vulkan/amber/texture/texel_buffer/uniform/snorm/b8g8r8a8-snorm.amber#L29-L50)，[`VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT`](../../../vulkan-docs/src/chapters/formats.adoc#L2359-L2371)。

## 4. `Multisample`：R64 atomic oracle 的高位常量与操作序列不一致

**对应页面：** [Multisample.md](../testfiles/texture/Multisample.md)

### 背景：R64 atomic case 如何构造结果

`texture.multisample.atomic` 对四样本 R64 storage image 依次执行 initialization、atomic add、OR、XOR 和 AND。每个 invocation 还会访问 workgroup 内的镜像 partner location，因此同一个 texel 会收到自身 invocation 和 partner invocation 的操作。

R32 和 R64 scripts 都在 shader 内读取最终 image value，并将其与一条 expected expression 比较。最终 framebuffer 全绿才算通过。

### 观察到的代码路径

在 [`storage_image_r64i.amber`](../../data/vulkan/amber/texture/multisample/atomic/storage_image_r64i.amber#L37-L85) 和 [`storage_image_r64ui.amber`](../../data/vulkan/amber/texture/multisample/atomic/storage_image_r64ui.amber#L26-L74) 中：

1. OR 阶段由一对 invocation 对同一 texel 设置 bit 63 和 bit 62，高 byte 先成为 `0xc0`；
2. XOR 阶段再分别应用 `0x0a00000000000000` 和 `0x0600000000000000`；
3. 因此高 byte 是 `0xc0 ^ 0x0a ^ 0x06 = 0xcc`；
4. verification expression 却只把低位 sum 与 `0x0a00000000000000` 做 OR。

脚本注释本身也写着 XOR 后的 byte 应为 `0xc`。但当前 oracle 的对应 byte 是 `0xa`，与注释和实际 atomic sequence 都不一致。

### 为什么需要确认

如果上述 paired-invocation 推导正确，R64 case 会把符合操作序列的实现结果判为失败。反过来，如果维护者认为 expected `0x0a...` 才是测试意图，就需要调整前面的 OR/XOR operations 或 partner access，而不是只改说明。

还应确认并发 atomic ordering 不会改变这个结论。这里的 OR 和 XOR 分阶段执行，阶段之间有 image memory barrier 和 workgroup barrier；同一阶段内这些位运算对目标 bit 的结果与调用顺序无关，所以当前差异不像普通竞态造成的不确定值。

### 需要维护者确认的问题

1. R64 expected expression 的高位常量是否应为 `0xcc00000000000000`？
2. signed 和 unsigned 两个 R64 scripts 是否应同步修复？
3. 是否需要让 R64 oracle 的结构与已工作的 R32 scripts 保持一致，避免以后只修改一组 mask？
4. 能否把 expected value 的每一阶段计算拆成 shader-side named constants，或增加 host-side/reference 测试，降低手写十六进制常量出错的风险？

相关证据：[`storage_image_r64i.amber`](../../data/vulkan/amber/texture/multisample/atomic/storage_image_r64i.amber#L37-L85)，[`storage_image_r64ui.amber`](../../data/vulkan/amber/texture/multisample/atomic/storage_image_r64ui.amber#L26-L74)，[R64 case registration](../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L38-L99)。

## 5. `Multisample`：invalid sample index writes 未启用 robust image access

**对应页面：** [Multisample.md](../testfiles/texture/Multisample.md)

### 背景：invalid sample index case 依赖什么规范保证

`texture.multisample.invalid_sample_index` 创建 2、4、8、16、32 或 64 samples 的 multisample storage image。shader 对 sample operand `-256` 到 `255` 逐一执行 `imageStore`。有效 sample 写入预定颜色，无效 sample 写入白色。之后 shader 只读取有效 samples，并要求它们仍保留预定颜色。

测试注释把目标写成“无效 sample number 的写入应被丢弃”。这正是 robust image access 对越界 storage-image write 提供的行为：越界写入不修改任何 memory。

### 观察到的代码路径

以 [`sample_count_4.amber`](../../data/vulkan/amber/texture/multisample/invalidsampleindex/sample_count_4.amber#L17-L89) 为例，recipe 只声明：

```text
DEVICE_FEATURE shaderStorageImageMultisample
```

C++ registration 同样只加入 `Features.shaderStorageImageMultisample`，见 [`createInvalidSampleIndexTests()`](../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L105-L144)。它没有请求 `robustImageAccess` 或 `robustImageAccess2`。

CTS 默认 device setup 还会主动关闭 image robustness，见 [`vkDeviceFeatures.cpp`](../../framework/vulkan/vkDeviceFeatures.cpp#L210-L234)。Vulkan 的 [Shader Out-of-Bounds Memory Access](../../../vulkan-docs/src/chapters/shaders.adoc#L1871-L1921) 要求应用在没有 bounds checking 时不得执行越界访问；[Robust Image Access](../../../vulkan-docs/src/chapters/shaders.adoc#L2171-L2186) 和 [Robust Image Access 2](../../../vulkan-docs/src/chapters/shaders.adoc#L2203-L2235) 才规定越界 storage-image write 不修改 memory。

### 为什么需要确认

在未启用 robust image access 的设备上，这些越界 `imageStore` 不具备测试所依赖的 discard 保证。有效 samples 最后保持原值，只能说明该次执行碰巧没有破坏它们，不能建立稳定的 conformance oracle；如果有效 sample 被改变，也不能直接归因于 driver 不符合 robust image 规则，因为测试没有启用该规则。

需要维护者决定测试目标究竟是 robust image behavior，还是一种非规范化的实现压力测试。如果目标是 conformance，前置 feature、device 创建和 skip 条件必须与 oracle 对齐。

### 需要维护者确认的问题

1. 这些 cases 应依赖 `robustImageAccess` 还是 `robustImageAccess2`？
2. registration 是否应检查 feature support，并通过 custom device 明确启用相应 feature？
3. 如果测试只关心越界 write 不破坏有效 samples，robust image access 1 的保证是否已经足够？
4. 是否应保留一个不启用 robustness 的版本作为非 conformance stress test，并避免对其结果作规范性判断？
5. 修复后能否加入 feature 回读或启动断言，证明 shader 执行时 robustness 确实生效？

相关证据：[`createInvalidSampleIndexTests()`](../../modules/vulkan/texture/vktTextureMultisampleTests.cpp#L105-L144)，[`sample_count_4.amber`](../../data/vulkan/amber/texture/multisample/invalidsampleindex/sample_count_4.amber#L17-L89)，[默认 robustness 设置](../../framework/vulkan/vkDeviceFeatures.cpp#L210-L234)，[Vulkan shader 越界访问规则](../../../vulkan-docs/src/chapters/shaders.adoc#L1871-L1921)，[robust image access 行为](../../../vulkan-docs/src/chapters/shaders.adoc#L2171-L2235)。

## 关联材料

- [Texture audit summary](texture_audit_summary.md)
- [Texture category 页面](../categories/texture.md)
- [Vulkan CTS texture 源码目录](../../modules/vulkan/texture/)
