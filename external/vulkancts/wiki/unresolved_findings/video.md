# video category：待实现维护者确认的 Source-Level Finding

> 本文从 [video audit summary](../internal_doc/video_audit_summary.md) 抽取 1 项未解决发现，供 Vulkan CTS 实现维护者单独评估。它不表示 wiki 审计未完成，也不等同于已经确认的 Vulkan 实现缺陷。当前观察集中在 H.264/H.265 encode 路径：输入加载阶段可以把实际处理帧数限制到 clip 可用帧数，但资源创建、编码和验证仍按 test definition 的 GOP 帧数运行。
>
> 本文只记录当前源码行为、潜在影响和需要确认的问题，不替维护者决定测试是否需要修改，也不把相关失败直接归因于 Vulkan 实现或驱动。审计阶段没有修改 Vulkan CTS C++ 源码、mustpass、输入 clip 或规范文件。

## 处理建议

建议把该项作为独立的源码调查或 issue：先逐个核对当前注册的 H.264/H.265 encode definition 所需帧数与对应 clip 的可用帧数，确认现有 mustpass 是否能够触发数量不一致；再决定应当在输入加载时拒绝帧数不足的 clip，还是让后续资源、编码和验证路径统一使用实际加载帧数。若需要修改，应为“clip 帧数少于 GOP 定义”增加回归覆盖，并重新检查 layered/separated source image 以及普通/intra-refresh 路径。

## 1. `Encode`：输入加载可以缩短帧数，但编码与验证仍使用 GOP 定义数量

**对应页面：** [Encode.md](../testfiles/video/Encode.md)

**对应源码：** [`vktVideoEncodeTests.cpp`](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L1997-L2035)

### 背景：测试需要多少帧

每个 H.264/H.265 encode definition 给出：

- `gops`：执行多少个 GOP；
- `encodePattern`：每个 GOP 包含多少个 picture；
- input clip：这些 picture 的原始 YUV 数据来源。

实例初始化时直接把 definition 转成：

```cpp
m_gopCount      = m_testDefinition->gopCount();
m_gopFrameCount = m_testDefinition->gopFrameCount();
```

因此 definition 所需的总帧数为：

```text
m_gopCount * m_gopFrameCount
```

普通 I/P case 通常只需要一两帧，量化图 case 需要两三帧，`i_p_b_13` 则使用两个 14-picture GOP。对应定义见 [`g_EncodeTests`](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L432-L1088)。当前 clip metadata 分别报告 24 帧或 15 帧，见 [`ClipInfo`](../../modules/vulkan/video/vktVideoClipInfo.cpp#L553-L587)。

### 观察到的代码路径

输入加载阶段先取得 clip 的可用帧数，然后取二者的较小值：

```cpp
uint32_t availableFrames = m_testDefinition->getClipTotalFrames();

uint32_t framesToProcess =
    std::min(m_gopCount * m_gopFrameCount, availableFrames);

for (uint32_t i = 0; i < framesToProcess; ++i)
    m_inVector.push_back(...);
```

对应 [`loadVideoFrames()`](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2730-L2797)。这意味着当 definition 需要的帧数超过 clip 可用帧数时，`m_inVector` 只保存实际可用的 prefix。

但其他阶段没有统一使用 `framesToProcess`：

1. `prepareInputImages()` 在加载 clip 之前，按 `m_gopCount * m_gopFrameCount` 创建 source images、layers 和 views，见 [`prepareInputImages()`](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2691-L2727)。
2. `encodeFrames()` 仍按 `m_gopCount` 和 `m_gopFrameCount` 嵌套循环并调用 `encodeFrame(...)`，见 [`encodeFrames()`](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2941-L2979)。
3. `verifyEncodedBitstream()` 再次把期望验证数设为 `m_gopCount * m_gopFrameCount`，并按该数量读取 decoded frames 和 `m_inVector[NALIdx]`，见 [`verifyEncodedBitstream()`](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L3394-L3504)。

intra-refresh 路径有一项局部调整：`loadVideoFrames()` 会先执行

```cpp
m_gopFrameCount = std::min(m_gopFrameCount, availableFrames);
```

但该调整发生在 `prepareInputImages()`、DPB 和 session-parameter setup 之后。源码自己的 `FIXME` 也说明这里仍涉及 test definition 的 DPB slot 使用问题，见 [`loadVideoFrames()`](../../modules/vulkan/video/vktVideoEncodeTests.cpp#L2745-L2755)。

### 一个最小例子

假设某个 definition 要求两个 14-picture GOP，但输入 clip 只有 24 帧：

```text
定义需要：2 * 14 = 28 帧
实际加载：min(28, 24) = 24 帧
编码循环：仍按 28 次运行
验证循环：仍期望 28 个 decoded frames
参考输入：m_inVector 只有 24 项
```

如果该组合可以进入执行路径，后四次编码或验证就不再有对应的已加载输入帧。潜在结果包括访问不存在的 input vector 元素、期待 bitstream 中不存在的 frame、报告 internal CTS error，或使失败位置无法代表被测实现的 encode 行为。

### 当前覆盖是否已经触发

静态阅读可以确认这条不一致路径存在，但不能仅凭它断言当前 mustpass 已经触发：

- 常用 H.264/H.265 clips 分别有 24 帧或 15 帧；
- 多数 definitions 所需帧数明显低于可用帧数；
- `i_p_b_13` 需要 28 帧，却使用 24-frame clips，因此最值得首先核对其完整运行路径以及是否有其他约束、资源行为或当前测试数据掩盖了数量不一致；
- intra-refresh 会在加载阶段调整 `m_gopFrameCount`，但调整时序仍需结合此前已经创建的资源确认。

所以当前证据足以提出 source-level finding，却不足以在不运行和不追踪全部对象索引的情况下决定唯一修复方案。

### 为什么需要维护者确认

这个问题首先指向 CTS 测试自身的 frame-count bookkeeping，而不是已经确认的 Vulkan 实现缺陷：

- 若测试访问了未加载的输入帧，相关 crash、internal error 或错误比较不能直接归因于 encoder；
- 若当前所有实际执行 case 都由其他不变量保证 clip 足够长，则问题可能只是潜在的防御性缺口；
- 单独把验证数量改为实际加载数，可能掩盖“测试资源或 bitstream 本应覆盖完整 GOP”的意图；
- 单独缩短 `m_gopFrameCount`，又可能改变 reference pattern、DPB slot、session parameter 和 source-image allocation 的既有关系。

因此，需要先确认测试意图和所有当前 definition 的实际触发条件，再选择一致的 frame-count contract。

### 需要维护者确认的问题

1. 当前所有注册的 H.264/H.265 definitions 中，哪些满足 `gopCount * gopFrameCount > clip.totalFrames`？
2. `i_p_b_13` 的两个 14-picture GOP 与 24-frame clip 是有意设计，还是 clip metadata、GOP count 或 pattern 配置不一致？
3. clip 不足时，CTS 应当：
   - 在 setup 阶段报告 internal error；
   - 只编码实际可用帧；
   - 还是为后续 GOP 重用或循环使用输入帧？
4. 若只编码实际帧数，source-image allocation、DPB references、bitstream queries、decoder expected count 和 PSNR input vector 应如何统一？
5. intra-refresh 对 `m_gopFrameCount` 的调整是否应提前到资源和 session setup 之前？
6. 是否需要分别增加 layered/separated source、普通/intra-refresh、resolution-change 和 `i_p_b_13` 的回归场景？
7. 修复后是否需要重新检查对应 mustpass case 的帧数、pass message 和 failure classification？

### 建议调查与处置

1. 在每个 definition 实例化后记录 `gopCount`、`gopFrameCount`、`clip.totalFrames` 和最终 `m_inVector.size()`。
2. 优先运行 H.264/H.265 的 `i_p_b_13` 四种 source/layout variants，并开启 ASan/UBSan 和 CTS video 日志。
3. 在 `encodeFrames()` 和 `verifyEncodedBitstream()` 前加入临时断言，确认所需 frame index 小于 source images、views 和 `m_inVector` 的实际数量。
4. 明确一个唯一的 frame-count contract，并让资源创建、输入上传、编码循环、decoder expected count 和 PSNR 比较共同使用它。
5. 在源码修复或确认不变量之前，不把由 frame shortage 引起的 internal error、missing decoded frame 或越界行为解释为 driver/hardware encode failure。

## 关联材料

- [video category 页面](../categories/video.md)
- [Encode.md](../testfiles/video/Encode.md)
- [Vulkan CTS video 源码目录](../../modules/vulkan/video/)
