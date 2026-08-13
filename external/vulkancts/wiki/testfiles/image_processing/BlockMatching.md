## Overview

**Core question:** Do Vulkan graphics and compute paths produce correct SAD/SSD block-match results across the image and pipeline states registered by CTS?

- This page covers the `image_processing.graphics.*.block_matching` and `image_processing.compute.block_matching` test family implemented by [`vktImageProcessingBlockMatchingTests.cpp`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L104-L2268).
- The family exercises `textureBlockMatchSADQCOM` and `textureBlockMatchSSDQCOM` with host-generated target/reference image data, generated shaders, and a CPU-built reference result.
- Graphics cases write a red/green result image through a draw; compute cases write the result through an output storage image. Both paths also return the block-match metric through a storage buffer.

## Background Knowledge

- A block-match operation compares corresponding texels in a rectangular target block and reference block. SAD sums absolute channel differences; SSD sums their squares. The returned metric is separate from the diagnostic result image used by these tests.
- A Vulkan image view supplies the format and component mapping seen by shader image operations, while a sampler supplies address and reduction behavior. Those view/sampler states can change the values consumed by block matching even when the underlying image data is unchanged.
- A Vulkan descriptor set binds shader-visible resources to numbered bindings. The test's block-match image descriptors, samplers, metric buffer, and compute output image must agree with the generated shader interface.

## Registration Hierarchy

```text
image_processing.graphics.monolithic.block_matching
├── sad
└── ssd
```

The same `block_matching` test family is also registered below `graphics.fast_lib`, `graphics.shader_objects`, and `compute`. The category dispatcher selects the graphics construction type and compute path in [`createChildren()`](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L78); the common factory creates the `sad` and `ssd` operation families in [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1881-L1898).

## Parameter Dimensions and Observed Values

The registered scope is a matrix. The table lists the dimensions that change the resources, shader stage, execution path, or expected-result calculation; unsupported cases may be pruned before execution.

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Operation family | `sad`, `ssd` | Selects the QCOM built-in and the host metric calculation. | [`imageProcessingOps[]`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1887-L1898), [`getImageProcGLSLStr()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L250-L255) |
| Graphics construction | `monolithic`, `fast_lib`, `shader_objects` | Selects the graphics pipeline-construction path. | [`constructionTypes[]`](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L50-L63) |
| Basic formats | `r8_unorm`, `r8g8_unorm`, `r8g8b8_unorm`, `r8g8b8a8_unorm`, `a8b8g8r8_unorm_pack32`, `a2b10g10r10_unorm_pack32` | Changes image storage, component widths, and the tolerance calculation. | [`getOpSupportedFormats()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408-L435) |
| Basic match mode | `same`, `diff` | Controls whether the target block is copied from the reference block or generated independently. | [`basic` registration](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1958-L2001) |
| Basic data variation | optional `_random`, optional `_constdiff` | Selects random versus uniform generated values; `_constdiff` adds a constant difference for applicable `diff` cases. | [`populateColorBuffer()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L523-L605) |
| Default geometry | 2D `64x64` images, coordinates `(0,0)`, block size `32x32` | Defines the baseline target/reference regions. | [`getCommonTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1657-L1695) |
| Graphics-only variation groups | `block_sizes`, `address_modes`, `reduction_modes`, `tiling`, `swizzles`, `layouts`, `shader_stages`, `descriptors` | Isolates block geometry, sampler state, image state, component mapping, stage, or descriptor update behavior. | [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2004-L2217) |
| Compute-only variation | `self` with `same`, `diff`, optional `_random` | Compares two non-overlapping regions of one image using the compute path. | [`self` registration](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2221-L2248) |

## Behavior Parameters

The primary behavioral axis is the operation and the execution/variation group. `sad` and `ssd` change the value being computed; the remaining groups change the conditions under which that operation must remain correct.

### `sad` — sum of absolute differences

The generated shader calls `textureBlockMatchSADQCOM`. The CPU reference accumulates absolute differences over the selected target and reference blocks. A `same` case should therefore produce a zero metric when the compared values remain equal after the selected view/sampler interpretation ([operation mapping](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L250-L255); [reference construction](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L741-L773)).

### `ssd` — sum of squared differences

The generated shader calls `textureBlockMatchSSDQCOM`. The CPU reference squares the per-channel differences before accumulation. This changes the magnitude of the expected metric and its error tolerance, while the resource and execution structure remains shared with `sad` ([operation selection](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L747-L768)).

### Graphics condition groups

- `basic` covers the default image setup for all three graphics construction types and both operations.
- `block_sizes` changes coordinates and block extents, including `1x1`, `64x64`, and `1x64` cases.
- `address_modes` uses `clamp_to_edge` and `clamp_to_border` with oversized blocks, a smaller target image, and an out-of-range target coordinate.
- `reduction_modes` combines three reference reductions (`weighted_average`, `min`, `max`) with target reduction values from `NONE` through `MAX`.
- `tiling` combines linear and optimal target/reference images while avoiding the optimal/optimal combination already covered by `basic`.
- `swizzles` applies `bgra`, `g01a`, or `rbg1` component mappings to the reference view.
- `layouts` combines `rdonly_optimal` and `general` layouts while avoiding the read-only/read-only combination already covered by `basic`.
- `shader_stages` adds a `vertex` case; fragment-stage execution is already represented by `basic`.
- `descriptors` enables update-after-bind and varies `same`/`diff` plus random/non-random data.

The exact generator tables and case names are in [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1900-L2217), with coordinate/size generators in [`getBlockSizeTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1817-L1877), [`getSamplerAddressModeTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1699-L1741), [`getSamplerReductionModeTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1743-L1764), [`getTilingTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1766-L1789), and [`getLayoutTestParams()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1791-L1815).

### Compute condition groups

Compute `basic` uses a compute shader with the same operation and baseline matrix. `self` binds one image as both target and reference and compares `(0,0)` with `(32,32)`; the implementation deliberately avoids overlapping regions ([self setup](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2221-L2248)).

## Shader Analysis

The family uses generated GLSL in both graphics and compute paths. A full representative walkthrough is not included in this rewrite because the required shader-analyzer and shader-disassembler round trip was not completed for an exact case; the source-grounded shader shape is summarized here.

- The shared generated preamble requires `GL_QCOM_image_processing`, binds target/reference block-match images at bindings 0 and 1, samplers at bindings 2 and 3, a `vec4` metric storage buffer at binding 4, and push constants for the two coordinates and block size ([preamble](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L275-L293)).
- The generated operation call passes the two combined `sampler2D` objects, the target and reference coordinates, and the block size. It writes the returned metric and chooses green for an all-zero metric or red otherwise ([operation body](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L295-L315)).
- Graphics cases normally execute this body in the fragment shader and draw a full-screen rectangle. `shader_stages.vertex` moves it to the vertex shader ([graphics generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L318-L368); [draw path](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L923-L958)).
- Compute cases use one invocation per output pixel, call the same generated operation body, and store the diagnostic color in a storage image at binding 5 ([compute generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1195-L1218); [dispatch path](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1291-L1304)).

## Runtime Execution and Result Checking

- [host] The shared support path requires `VK_QCOM_image_processing`, and below Vulkan 1.3 also requires `VK_KHR_format_feature_flags2` ([base support](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L92-L100)). For SAD/SSD it requires `textureBlockMatch` and `VK_FORMAT_FEATURE_2_BLOCK_MATCHING_BIT_QCOM` for the selected sampled-image tiling ([operation support](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L102-L123)).
- [host] The block-match support path checks the target format feature, both target/reference image usages, and the device's `maxBlockMatchRegion` against the generated block size ([block-match support](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L141-L213)). Graphics additionally checks color-attachment output support and pipeline-construction requirements ([graphics support](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L240-L272)); compute checks storage-image output support and workgroup-count limits ([compute support](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1157-L1193)).
- [host] The instance fills host-visible color buffers, creates target/reference images and views, creates samplers, writes descriptors, and copies the buffers into the images. `same` cases copy the reference region into the target; `diff` cases generate a separate target region ([buffer generation](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L523-L605); [descriptor setup](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L460-L521)).
- [device] Graphics submits a draw through the selected pipeline construction; compute dispatches over the output extent. Both paths write one `vec4` metric to a storage buffer and a diagnostic result image ([shared command path](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L642-L738)).
- [host] The test reads back the output image and metric, computes the CPU reference with [`buildStandardResult()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L741-L773), then calls [`verifyResult()`](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L237-L272). The image comparison uses an exact zero threshold; the metric comparison uses `calculateErrorThreshold()`, which scales floating-point and format quantization allowances by block element count and component width ([threshold](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L82-L102)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `sad` | SAD built-in execution, input setup, or SAD reference calculation mismatch. |
| `ssd` | SSD built-in execution, input setup, or SSD reference calculation mismatch. |
| `basic` | Baseline image, descriptor, shader, output-transfer, or comparison failure. |
| `block_sizes` | Block coordinate, extent, or boundary handling failure. |
| `address_modes` | Address handling for out-of-range coordinates or blocks. |
| `reduction_modes` | Interaction between target and reference reduction modes. |
| `tiling` | Linear/optimal image-tiling handling. |
| `swizzles` | Reference-view component mapping or metric interpretation. |
| `layouts` | Target/reference image-layout handling. |
| `shader_stages` | Block matching in the vertex stage rather than the baseline fragment stage. |
| `descriptors` | Update-after-bind descriptor update or consumption. |
| `self` | Two non-overlapping regions of one image and the single-image descriptor path. |

### Cause Analysis

#### Operation or input-data mismatch

**Possible failure symptoms:** The returned metric exceeds the calculated tolerance, or the diagnostic image differs from the CPU result image.

**Possible implementation causes:** The selected QCOM operation may be executed incorrectly, or the device path may interpret image data, coordinates, component mapping, or format values differently from the host reference. The test does not isolate those causes further.

#### Resource-state or variant-handling mismatch

**Possible failure symptoms:** A resource-state or specialized group fails while the corresponding baseline group passes.

**Possible implementation causes:** The implementation may mishandle the selected image tiling/layout, sampler address/reduction state, component swizzle, shader stage, or descriptor update. Source-level investigation is needed to distinguish API-state handling from the block-matching operation.

#### Output or copyback mismatch

**Possible failure symptoms:** The metric is within tolerance but the exact output-image comparison fails, or the host reads back an unexpected metric.

**Possible implementation causes:** The output image write, layout transition, image-to-buffer copy, storage-buffer visibility, or host readback path may be incorrect. The test reports the mismatch but does not localize the responsible stage.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the required extension, feature, format feature, image usage, output usage, descriptor feature, pipeline construction capability, device limit, or compute workgroup-count limit is unavailable. Relevant gates include [`ImageProcessingTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L92-L168), block-match checks ([`ImageProcessingBlockMatchTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L141-L213)), graphics checks ([`ImageProcessingBlockMatchGraphicsTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L240-L272)), and compute checks ([`ImageProcessingBlockMatchComputeTest::checkSupport()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1157-L1193)).

### Design-based pruning

- Extended graphics groups are intentionally generated only for monolithic pipelines. `fast_lib` and `shader_objects` cover `basic`; compute covers `basic` and `self` ([branch](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2004-L2251)).
- `constdiff` is not generated for `same` cases because a matching case cannot simultaneously apply an intentional constant difference ([basic generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1967-L1975)).
- The both-optimal tiling and both-read-only-optimal layout combinations are omitted from their extended groups because `basic` already covers them ([tiling generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1766-L1789); [layout generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1791-L1815)).
- The compute `self` generator fixes two non-overlapping regions and does not generate overlapping cases because the implementation does not support them ([self generator](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2221-L2248)).

## Key Takeaways

- `sad` and `ssd` share the resource and execution framework but test different block-match metrics.
- The family validates both the returned metric and a diagnostic output image, so a passing case requires agreement in two observable results.
- The large graphics matrix is monolithic-only by design; the alternative pipeline-construction paths and compute path focus on their baseline or self-specific coverage.
- Runtime support checks prune unsupported cases before execution; a skipped case is not a failed block-match result.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Category dispatch | [`vktImageProcessingTests.cpp#createChildren()`](../../../modules/vulkan/image_processing/vktImageProcessingTests.cpp#L43-L78) | Selects graphics construction branches, API, and compute. |
| Common registration | [`createImageProcessingBlockMatchingCommonTests()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1881-L2257) | Registers operation families and all variation groups. |
| Operation mapping and formats | [`vktImageProcessingTestsUtil.cpp`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L250-L255), [`getOpSupportedFormats()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408-L435) | Maps `sad`/`ssd` to GLSL built-ins and supplies candidate formats. |
| Generated graphics source | [`initPrograms()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L275-L369) | Builds vertex and fragment GLSL for graphics cases. |
| Generated compute source | [`ImageProcessingBlockMatchComputeTest::initPrograms()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1195-L1218) | Builds the compute shader and output-image path. |
| Host reference and tolerance | [`buildStandardResult()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L741-L773), [`calculateErrorThreshold()`](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L82-L102) | Produces the CPU metric and accepted error threshold. |
| Final comparison | [`verifyResult()`](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L237-L272) | Compares the output image exactly and the metric within tolerance. |
| Mustpass inventory | [`image-processing.txt`](../../../mustpass/main/vk-default/image-processing.txt) | Records the category's current executable case scope. |
