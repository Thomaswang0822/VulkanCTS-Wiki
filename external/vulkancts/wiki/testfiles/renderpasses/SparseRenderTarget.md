## Overview

**Core question:** Can the implementation render into a sparse-resident 2D color image, store it, and read the result back with the correct pixel values for each supported color format?

- This page covers the `sparserendertarget` test family implemented in [vktRenderPassSparseRenderTargetTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp). The family is created by [`createRenderPassSparseRenderTargetTests()`](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L867-L871) and attached under the `suballocation` subgroup for each rendering variant ([attachment in vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8579-L8580)).
- Each supported color format becomes one test case leaf. The host binds a fully resident sparse color image, renders a solid color quad into it through a render pass or dynamic rendering instance, copies the result to a host-visible buffer, and compares it against a host-computed reference.
- The point of the test is that the sparse residency and memory binding path must produce a color target that behaves like a normal (non-sparse) color attachment for rendering and readback. If sparse binding, the sparse queue semaphore, or the format conversion is wrong, the read-back pixels will not match the reference.
- The family runs only for the monolithic pipeline construction type. Graphics pipeline library variants are not registered for this family ([gating condition](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8580)).
- The same test family is registered under `renderpass1`, `renderpass2`, and each `dynamic_rendering.*` subgroup, so the same 50 formats are exercised through legacy render passes, render pass 2, and dynamic rendering.

## Background Knowledge

- **Sparse residency.** An image created with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT` and `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` does not have to be bound to one contiguous memory allocation. Instead it has a prescribed block layout, and rectangular regions of the image are bound to specific memory offsets. The `sparseResidencyImage2D` feature advertises support for 2D, single-sampled images of this kind ([sparsemem.adoc](../../../../vulkan-docs/src/chapters/sparsemem.adoc)).
- **Fully resident sparse image.** This test binds every sparse block of the color image before rendering. There are no unbound (non-resident) regions during the draw, so the test does not exercise non-resident access behavior. The point is that the residency and binding machinery, the sparse queue binding, and the format handling must not corrupt the rendered result.
- **Sparse queue binding with a semaphore.** Sparse memory bindings are queued through `VkQueueBindSparse` and synchronized against graphics work with a semaphore. The test signals a bind semaphore from the sparse binding operation and waits on it before the draw command buffer runs, so the color attachment memory is guaranteed resident before rendering begins.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.sparserendertarget
├── a2b10g10r10_uint_pack32
├── a2b10g10r10_unorm_pack32
├── a2r10g10b10_unorm_pack32
├── a8_unorm
├── a8b8g8r8_sint_pack32
├── a8b8g8r8_snorm_pack32
├── a8b8g8r8_srgb_pack32
├── a8b8g8r8_uint_pack32
├── a8b8g8r8_unorm_pack32
├── b8g8r8a8_srgb
├── b8g8r8a8_unorm
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r16_sfloat
├── r16_sint
├── r16_snorm
├── r16_uint
├── r16_unorm
├── r16g16_sfloat
├── r16g16_sint
├── r16g16_snorm
├── r16g16_uint
├── r16g16_unorm
├── r16g16b16a16_sfloat
├── r16g16b16a16_sint
├── r16g16b16a16_snorm
├── r16g16b16a16_uint
├── r16g16b16a16_unorm
├── r32_sfloat
├── r32_sint
├── r32_uint
├── r32g32_sfloat
├── r32g32_sint
├── r32g32_uint
├── r32g32b32a32_sfloat
├── r32g32b32a32_sint
├── r32g32b32a32_uint
├── r5g6b5_unorm_pack16
├── r8_sint
├── r8_snorm
├── r8_uint
├── r8_unorm
├── r8g8_sint
├── r8g8_snorm
├── r8g8_uint
├── r8g8_unorm
├── r8g8b8a8_sint
├── r8g8b8a8_snorm
├── r8g8b8a8_srgb
├── r8g8b8a8_uint
└── r8g8b8a8_unorm
```

The tree uses the `renderpass1` variant as one concrete parseable hierarchy. The same 50 test case leaves are registered under `renderpasses.renderpass2.suballocation.sparserendertarget` and under each `renderpasses.dynamic_rendering.{primary_cmd_buff,complete_secondary_cmd_buff,partial_secondary_cmd_buff}.suballocation.sparserendertarget` path. The family is added inside the monolithic-pipeline block only ([gating](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8580)), so graphics pipeline library variants are absent from mustpass. Each test case leaf is registered by [`initTests()`](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L795-L863), which lowercases the `VK_FORMAT_` enum to form the test name ([formatToName](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L750-L758)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Color format | 50 formats spanning UNORM, SNORM, UINT, SINT, SRGB, SFLOAT, and packed representations | The format is the only parameter that changes what is rendered and how the result is validated. Different channel classes (unsigned integer, signed integer, fixed point, floating point) drive both the shader output value and the host comparison method. | [format list](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L797-L848), [mustpass](../../../mustpass/main/vk-default/renderpasses.txt#L47144-L47193) |
| Rendering type | `renderpass1`, `renderpass2`, `dynamic_rendering` | Selects the render pass or dynamic rendering path. The same draw, copy, and comparison run through each. | [createRenderPass dispatch](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L216-L232) |
| Render size | `32 x 32` | Fixed for every case. The framebuffer and readback buffer are always this size. | [width/height](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L413-L414) |
| Pipeline construction | monolithic only | The family is gated to `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`, so graphics pipeline library variants are not registered. | [attachment gating](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8580) |

## Behavior Parameters

The primary behavioral axis is the format test case leaf. Each leaf renders the same full-screen quad but with a fragment output and reference value chosen for that format's channel class. The rendering type, render size, and pipeline construction are configuration, not behavior: they change which code path executes but not what property is being tested.

The fragment shader has three shapes, selected at shader build time from the format's channel class ([Programs::init](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L682-L748)):

- unsigned integer formats write `uvec4(1 << (bits.x - 1), 1 << (bits.y - 2), 1 << (bits.z - 3), 0xffffffff)`;
- signed integer formats write `ivec4(1 << (bits.x - 2), 1 << (bits.y - 3), 1 << (bits.z - 4), 0xffffffff)`;
- fixed-point and floating-point formats write `vec4(0.5, 0.25, 0.125, 1.0)`.

The host reference is computed with the same channel-class logic, with an SRGB conversion applied for sRGB formats. Because the value and the comparison rule are both derived from the channel class, the behavioral grouping below is by channel class rather than by individual format.

### Unsigned integer formats

Formats such as `r8_uint`, `r8g8b8a8_uint`, `a8b8g8r8_uint_pack32`, `a2b10g10r10_uint_pack32`, `r16_uint`, `r16g16_uint`, `r16g16b16a16_uint`, `r32_uint`, `r32g32_uint`, and `r32g32b32a32_uint` write a per-channel bit pattern into `uvec4` output. The host compares the read-back image against the same pattern with `tcu::intThresholdCompare` using a zero threshold, so any bit difference fails ([unsigned integer branch](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L591-L604)).

### Signed integer formats

Formats such as `r8_sint`, `r8g8b8a8_sint`, `a8b8g8r8_sint_pack32`, `r16_sint`, `r16g16_sint`, `r16g16b16a16_sint`, `r32_sint`, `r32g32_sint`, and `r32g32b32a32_sint` write the signed counterpart of the unsigned pattern into `ivec4` output. The host compares with `tcu::intThresholdCompare` using a zero threshold ([signed integer branch](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L606-L619)).

### Fixed-point formats

UNORM, SNORM, and SRGB formats write `vec4(0.5, 0.25, 0.125, 1.0)`. The host reference scales the format's representable maximum per channel, applies an SRGB encode for sRGB formats, and compares with `tcu::floatThresholdCompare` using a threshold of four times the minimum representable difference for the format ([fixed-point branch](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L621-L648)).

### Floating-point formats

`r16_sfloat`, `r16g16_sfloat`, `r16g16b16a16_sfloat`, `r32_sfloat`, `r32g32_sfloat`, and `r32g32b32a32_sfloat` write `vec4(0.5, 0.25, 0.125, 1.0)`. The host compares with `tcu::floatUlpThresholdCompare` using a threshold of 64 ULP scaled to the format's mantissa width, which tolerates precision loss when a 32-bit float constant is stored to a narrower float format ([floating-point branch](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L650-L673)).

## Shader Analysis

The shader is a tool that paints the sparse color target with a known value. It is not the behavior under test; the behavior under test is whether the sparse-resident attachment survives rendering, storage, and readback intact. No representative shader walkthrough is included for that reason. The notable shader facts are:

- The vertex shader emits a full-screen triangle pair from `gl_VertexIndex` with no vertex input, so the test needs no vertex buffers ([vertex shader](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L692-L702)).
- The fragment shader output type (`uvec4`, `ivec4`, or `vec4`) and the literal values it writes are chosen at build time from the format's bit depth and channel class ([fragment shader generation](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L704-L744)).
- The pipeline has no descriptor bindings, no vertex input state, and no tessellation, geometry, or depth state. The only variable is the fragment output type and the format carried into the color attachment ([pipeline creation](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L272-L328)).

## Runtime Execution and Result Checking

Every case follows the same host-side shape: build the sparse color image and its memory, build the framebuffer and pipeline, record one draw, copy the image back, and compare.

- The host creates a 2D sparse-resident color image with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, and optimal tiling ([createSparseImageAndMemory](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L77-L112)). The helper `allocateAndBindSparseImage` binds every sparse block before the draw, so the image is fully resident during rendering.
- A bind semaphore is signaled from the sparse binding operation and passed to the draw submission as a wait semaphore, so the universal queue does not start the draw until the sparse memory binding is complete ([constructor](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L410-L438), [submit](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L480-L482)).
- For `renderpass1` and `renderpass2`, the host records `vkCmdBeginRenderPass`, binds the graphics pipeline, draws six vertices (two triangles covering the framebuffer), ends the render pass, and copies the image to a host-visible buffer ([iterateInternal](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L455-L485)).
- For dynamic rendering, the host issues an image memory barrier into `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, then either records the draw inline or through a secondary command buffer, depending on the `SharedGroupParams` variant, and ends rendering before the copy ([iterateInternalDynamicRendering](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L487-L576)).
- After the copy, the host invalidates the mapped buffer and compares the read-back pixels against a host-computed reference using the channel-class-specific comparator ([verify](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L578-L680)). Results are collected through `tcu::ResultCollector`, and the case passes only if every pixel is within tolerance.
- The attachment load op is `VK_ATTACHMENT_LOAD_OP_DONT_CARE` and the initial layout is `VK_IMAGE_LAYOUT_UNDEFINED`, so the test only checks the drawn output and is not sensitive to prior attachment contents ([attachment description](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L165-L179)).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| Sparse-resident color image | Yes | Sparse memory blocks bound through `VkQueueBindSparse` | Written as color attachment, read as copy source | No (copied first) | The render target whose sparse residency, binding, and format handling are under test. |
| Color image view | Yes | Framebuffer or dynamic rendering attachment | Used by the pipeline | No | Selects the color aspect of the sparse image as the attachment. |
| Host-visible destination buffer | Yes | Bound to device memory | Written by `vkCmdCopyImageToBuffer` | Yes | Holds the read-back pixels the host compares. |
| Bind semaphore | Yes | Waited by the draw submission | Synchronizes sparse binding against graphics | No | Guarantees the color image is fully resident before rendering. |
| Graphics pipeline | Yes | Bound before the draw | Executes the vertex and fragment shaders | No | Paints the known per-channel-class value into the attachment. |

## Failure Meaning

### Failure Cause Mapping

Because the behavior axis is the format leaf, every failure maps to the same combined check: the sparse-resident color image must render, store, and read back the per-channel-class value within tolerance.

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any unsigned integer format | Sparse binding, store, copyback, or integer attachment write produced a bit difference. |
| Any signed integer format | Sparse binding, store, copyback, or signed integer attachment write produced a bit difference. |
| Any fixed-point (UNORM, SNORM, SRGB) format | Sparse binding, store, copyback, or normalized-attachment conversion produced a value outside the 4x minimum-difference threshold; sRGB encode may be wrong for SRGB cases. |
| Any floating-point format | Sparse binding, store, copyback, or float attachment rounding produced a value outside the 64-ULP threshold. |
| Any format (common cause) | Sparse residency or binding path, the bind semaphore synchronization, the image-to-buffer copy, or the host comparison produced wrong data independent of the format. |

### Cause Analysis

#### Sparse residency or binding path corrupted the color target

**Possible failure symptoms:** The read-back image differs from the host reference across all or part of the framebuffer, for one or more formats, regardless of channel class. The error may look like stale, zeroed, or partially written pixels rather than a clean format-conversion error.

**Possible implementation causes:** The test binds every sparse block of the color image before the draw and waits on the bind semaphore before the graphics submission runs ([constructor](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L410-L438), [submit](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L480-L482)). A driver that does not make the sparse binding visible to the universal queue at the semaphore wait, that mis-handles the sparse image block layout returned by `vkGetImageSparseMemoryRequirements`, or that loses a residency binding during the store or copy, can produce this symptom. The Vulkan specification ties sparse residency to the `sparseResidencyImage2D` feature and the sparse image format properties ([sparsemem.adoc](../../../../vulkan-docs/src/chapters/sparsemem.adoc)), so a mismatch between advertised sparse format support and actual rendering behavior is one concrete failure source.

#### Color attachment store or image-to-buffer copy lost data

**Possible failure symptoms:** The drawn region is correct for some pixels but wrong for others, or the whole image is shifted, tiled, or partially cleared. The error pattern may track the sparse block granularity rather than the framebuffer rectangle.

**Possible implementation causes:** The attachment uses `VK_ATTACHMENT_STORE_OP_STORE` and a final layout of `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, then `copyImageToBuffer` transfers the result ([attachment description](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L165-L179), [copy](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L476)). A driver that does not correctly store a sparse-resident attachment to its bound memory, or whose `vkCmdCopyImageToBuffer` reads sparse image blocks in the wrong order or with the wrong layout transition, can produce this symptom. Source-level investigation is needed to separate a store-side bug from a copy-side bug.

#### Format conversion or comparison threshold exceeded

**Possible failure symptoms:** A single format, or a small group of formats sharing a channel class, fails while others pass. Integer formats fail by a single bit; fixed-point formats fail by more than four times the minimum representable difference; floating-point formats fail by more than 64 ULP.

**Possible implementation causes:** The host reference is computed from the same bit depth and channel class used to generate the shader output, with an SRGB encode applied for sRGB formats and a scaled threshold for fixed-point and float formats ([verify](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L578-L680)). A driver that rounds, clamps, or encodes a format differently from the host reference (for example, wrong sRGB curve, wrong normalized range for SNORM, or excess rounding when narrowing a 32-bit float to a 16-bit float) can fail a specific format without failing the sparse path. The 64-ULP float threshold is deliberately loose to absorb legitimate narrowing precision, so a float failure usually points to a real conversion defect rather than tolerance.

## Case Pruning

### Requirement-based pruning

- The case requires the `sparseResidencyImage2D` feature; without it the case raises `NotSupportedError` rather than failing ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L774-L776)).
- `VK_FORMAT_A8_UNORM_KHR` additionally requires `VK_KHR_maintenance5` ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L763-L766)).
- `renderpass2` cases require `VK_KHR_create_renderpass2`, and dynamic rendering cases require `VK_KHR_dynamic_rendering` ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L768-L772)).
- Each format must be queryable as a sparse image format with color-attachment and transfer-source usage; if `vkGetPhysicalDeviceImageFormatProperties` returns `VK_ERROR_FORMAT_NOT_SUPPORTED` or the sparse image format properties list is empty, the case is unsupported ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L778-L792)).

### Design-based pruning

- The family is gated to the monolithic pipeline construction type, so graphics pipeline library variants are not registered ([attachment gating](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8571-L8580)).
- The render size is fixed at `32 x 32` for every case; larger or smaller sizes are not part of the registered matrix.
- Depth, stencil, and compressed formats are not in the format list. The family covers color formats that support sparse residency with optimal tiling only ([format list](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L797-L848)).

## Key Takeaways

- The `sparserendertarget` family proves that a fully resident sparse 2D color image behaves like a normal color attachment across 50 color formats and three rendering paths.
- The format is the only behavior-changing parameter; it drives the shader output value, the host reference, and the comparison method through the channel-class logic.
- The bind semaphore guarantees the sparse memory binding is complete before the draw, so a failure usually points to residency, binding, store, copy, or format-conversion behavior rather than timing.
- The comparison thresholds are deliberately tight for integers (zero) and loose for floats (64 ULP), so the failure type tells you whether the defect is a bit corruption or a conversion rounding issue.
- See `## Failure Meaning` for the failure interpretation: a failing result means the sparse residency or binding path, the store or copy, or the format conversion did not satisfy the per-channel-class validation rule.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Family factory | [createRenderPassSparseRenderTargetTests](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L867-L871) | Creates the `sparserendertarget` test family and runs `initTests`. |
| Test case registration | [initTests](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L795-L863) | Registers one leaf per supported format, named by lowercasing the `VK_FORMAT_` enum. |
| Format list | [formats array](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L797-L848) | The 50 color formats exercised by the family. |
| Sparse image and memory binding | [createSparseImageAndMemory](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L77-L112) | Creates the sparse-resident color image and binds its memory through the helper. |
| Render pass construction | [createRenderPass](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L152-L232) | Builds the legacy, render pass 2, or dynamic rendering render pass from the format and rendering type. |
| Pipeline construction | [createRenderPipeline](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L272-L328) | Builds the graphics pipeline with the generated vertex and fragment shaders. |
| Shader generation | [Programs::init](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L682-L748) | Emits the full-screen vertex shader and the channel-class-specific fragment shader. |
| Support checks | [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L760-L793) | Enforces `sparseResidencyImage2D`, extension, and sparse format support requirements. |
| Runtime execution and submit | [iterateInternal](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L455-L485), [iterateInternalDynamicRendering](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L487-L576) | Records the draw, handles the bind semaphore, and submits the command buffer. |
| Result comparison | [verify](../../../modules/vulkan/renderpass/vktRenderPassSparseRenderTargetTests.cpp#L578-L680) | Computes the per-channel-class reference and runs the threshold comparison. |
| Family attachment | [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8579-L8580) | Attaches the family under `suballocation` inside the monolithic-pipeline block. |
| Mustpass entry | [renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt#L47144-L47193) | The 50 `renderpass1` leaves; the same leaves repeat under `renderpass2` and each `dynamic_rendering.*` subgroup. |
