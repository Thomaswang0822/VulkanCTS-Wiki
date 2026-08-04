## Overview

**Core question:** Does `VK_EXT_blend_operation_advanced` produce the expected advanced-blend results when the CTS changes the operation, overlap declaration, premultiplication state, attachment count, and coherent-operation setting?

[`vktPipelineBlendOperationAdvancedTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1) implements the `pipeline.blend_operation_advanced` test family. The family renders fixed geometry to color attachments and checks the images against host-built reference images. Its three direct children are intermediate nodes: `ops` changes the advanced operation matrix, `independent` assigns operations per attachment, and `coherent` applies two operations to one attachment in sequence.

The test requires `VK_EXT_blend_operation_advanced`. [`checkSupport`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1523) also checks the relevant advertised properties and feature before an affected test case runs.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- Advanced blending combines a fragment source color with the destination color already held by a color attachment. `VkPipelineColorBlendAdvancedStateCreateInfoEXT` declares source and destination premultiplication plus the overlap mode. The [advanced-blending specification](../../../../vulkan-docs/src/chapters/framebuffer.adoc#advanced-blending) defines this pipeline behavior.
- An implementation advertises limits and optional capabilities such as `advancedBlendMaxColorAttachments`, correlated overlap, independent blending, and non-premultiplied color support through `VkPhysicalDeviceBlendOperationAdvancedPropertiesEXT`. [Feature support](../../../../vulkan-docs/src/chapters/features.adoc#features-blendOperationAdvanced) and [limits](../../../../vulkan-docs/src/chapters/limits.adoc#limits-blendOperationAdvanced) define the associated contracts.
- Coherent advanced blending concerns consecutive operations on the same color attachment. The `coherent` intermediate node makes two render passes target one image and uses the selected coherent-operation setting to choose whether it inserts an intervening color-attachment barrier.

## Registration Hierarchy

`createBlendOperationAdvancedTests()` registers the family for each pipeline-construction type. This tree shows the monolithic construction root used for path validation; the source also receives the other construction types through the pipeline test registration path.

```text
pipeline.monolithic.blend_operation_advanced
├── ops
├── independent
└── coherent
```

The `vk-default` mustpass files contain 4,652 matching `blend_operation_advanced` leaves for each construction root: `monolithic/monolithic.txt`, `pipeline-library.txt`, `fast-linked-library.txt`, `shader-object-linked-spirv.txt`, `shader-object-linked-binary.txt`, `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`, and `shader-object-unlinked-binary.txt`. These files cover the corresponding `pipeline.monolithic`, `pipeline.pipeline_library`, `pipeline.fast_linked_library`, and shader-object construction roots.

## Parameter Dimensions and Observed Values

| Parameter | Source evidence | Observed values and effect |
|-----------|-----------------|----------------------------|
| Intermediate node | [`createBlendOperationAdvancedTests`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2237) | `ops`, `independent`, and `coherent` select the test shape. |
| Advanced operation | `blendOps[]` in the registration function | Core advanced operations plus additional RGB operations such as `VK_BLEND_OP_PLUS_EXT`, `VK_BLEND_OP_MINUS_EXT`, `VK_BLEND_OP_CONTRAST_EXT`, and channel operations. |
| Color-attachment count | `colorAttachmentCounts[]` | `ops`: 1, 2, 4, 8, 16. `independent`: 2, 4, 8, 16. `coherent`: 1. |
| Overlap | registration loops and parameter construction | `VK_BLEND_OVERLAP_UNCORRELATED_EXT`, `VK_BLEND_OVERLAP_DISJOINT_EXT`, and `VK_BLEND_OVERLAP_CONJOINT_EXT`; additional RGB operations use uncorrelated overlap only. |
| Premultiplication | `premultiplyModes[]` | Source and destination independently select premultiplied or non-premultiplied state for `ops`; `independent` and `coherent` use premultiplied colors. |
| Format | registration function | `VK_FORMAT_R16G16B16A16_SFLOAT` and `VK_FORMAT_R8G8B8A8_UNORM`. |
| Coherent flag | `coherentOps[]` | `false` records a color-attachment barrier between passes; `true` exercises coherent advanced blending. |
| Pipeline construction | caller parameter | The family is instantiated under monolithic, pipeline-library, fast-linked-library, and shader-object construction roots represented by mustpass files. |

## Behavior Parameters

The primary behavioral axis is the intermediate node directly below `pipeline.<construction>.blend_operation_advanced`.

### `ops`: Operation, overlap, premultiplication, and format matrix

`ops` uses the same selected operation for every attachment in a case. It varies attachment count, overlap, source and destination premultiplication, operation, and both test formats. It excludes correlated-overlap variants for additional RGB operations because the registration source records that those operations are not affected by overlap modes.

### `independent`: Per-attachment operation selection

`independent` renders to 2, 4, 8, or 16 attachments. Registration selects an operation for each attachment from a deterministic random sequence, uses uncorrelated overlap and premultiplied colors, then verifies every attachment against its own reference image.

### `coherent`: Two advanced operations on one attachment

`coherent` selects two operations and renders twice to one attachment. The first render pass clears the image; the second loads it. The non-coherent variant records a color-attachment barrier between passes, while the coherent variant tests the extension feature path without that barrier.

## Shader Analysis

The shaders do not implement advanced blend arithmetic. [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1605) emits a vertex shader for the rectangles and a fragment shader that writes a pushed `Vec4` source color. [`buildPipeline`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L998) binds the selected `VkBlendOp` and `VkPipelineColorBlendAdvancedStateCreateInfoEXT`, so fixed-function pipeline state performs the behavior under test. A shader walkthrough would therefore obscure the relevant implementation boundary.

## Runtime Execution and Result Checking

1. The test case checks `VK_EXT_blend_operation_advanced`, queries `VkPhysicalDeviceBlendOperationAdvancedPropertiesEXT`, and rejects unsupported operations, attachment counts, overlap modes, independent blending, or non-premultiplied colors. It separately checks `advancedBlendCoherentOperations` for coherent cases.
2. The generic instance creates a host-populated vertex buffer, one color image per attachment, image views, a render pass, framebuffer, pipeline layout with a fragment `Vec4` push constant, and a graphics pipeline. It transitions every color image to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` before drawing.
3. [`buildPipeline`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L998) creates one `VkPipelineColorBlendAttachmentState` per attachment with blending enabled, `VK_BLEND_FACTOR_ONE` factors, the case's advanced `VkBlendOp` for color and alpha, and an RGBA write mask. It chains `VkPipelineColorBlendAdvancedStateCreateInfoEXT` into the color-blend state.
4. The generic path records one render pass. Before each draw, it uses `vkCmdClearAttachments` over the draw's one-pixel scissor to install that sample's destination color in every attachment, then pushes the corresponding source color and draws. After submission and waiting, [`verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1394) reconstructs reference images with `calculateFinalColor`, skips ill-formed or non-normal expected colors, and calls `tcu::floatThresholdCompare` per attachment. `R16G16B16A16_SFLOAT` uses `0.01` per component; `R8G8B8A8_UNORM` uses `0.15, 0.15, 0.15, 0.13`.
5. The coherent path creates one color image and two render passes. The first clears, the second loads the same image. It records the first draw, conditionally places a color-attachment memory barrier, records the second draw, then submits and waits. [`BlendOperationAdvancedTestCoherentInstance::verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2089) applies the two selected operations in the same order to build one reference image before comparison. Its `R16G16B16A16_SFLOAT` threshold is `0.01` per component, while its `R8G8B8A8_UNORM` threshold is `0.13` per component.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ops` | Advanced operation equation, overlap handling, premultiplication conversion, or color-format result error. |
| `independent` | Per-attachment advanced blend state selection or multi-attachment result-routing error. |
| `coherent` | Consecutive-operation ordering, attachment load/store behavior, coherent-operation feature handling, or intervening-barrier error. |

### Cause Analysis

#### Advanced operation, overlap, premultiplication, or format errors

**Possible failure symptoms:** `ops` leaves show image mismatches for one operation, one overlap declaration, one premultiplication combination, or one format. The same mismatch may appear across several attachment counts because those cases use the same operation for each attachment.

**Possible implementation causes:** The color-blend implementation may apply an advanced equation incorrectly, interpret `blendOverlap` incorrectly, or convert non-premultiplied colors incorrectly. A format conversion or quantization defect can also surface only in `VK_FORMAT_R8G8B8A8_UNORM`, whose checker uses a wider threshold. The image result alone does not isolate pipeline state setup from fixed-function blend execution, so source-level and driver investigation is needed to distinguish them.

#### Per-attachment state selection or result-routing errors

**Possible failure symptoms:** `independent` leaves fail while matching `ops` leaves pass, or only selected attachments in a multi-attachment result mismatch.

**Possible implementation causes:** The implementation may apply one attachment's `VkBlendOp` to another attachment, fail to retain per-attachment advanced state, or route writes and readback results to the wrong attachment. The generic oracle compares each attachment separately, which localizes the symptom to attachment-specific handling but cannot identify the internal pipeline-state stage that lost the mapping.

#### Consecutive-operation ordering, load/store, coherent feature, or barrier errors

**Possible failure symptoms:** `coherent` leaves fail while generic leaves using related operations pass, or failures separate the `coherent=true` and `coherent=false` variants.

**Possible implementation causes:** The second pass may not read the first pass's stored attachment value, may execute the selected operations in the wrong order, or may mishandle the coherent-operation feature path. In the non-coherent variant, failure can also arise from the color-attachment barrier or its access and stage masks. Because the final pixel combines both operations, one image mismatch cannot isolate the first draw from the second draw or the synchronization transition.

## Case Pruning

### Requirement-based pruning

[`checkSupport`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1523) skips a case when:

- `VK_EXT_blend_operation_advanced` is unavailable.
- `advancedBlendAllOperations` is false and the selected operation is outside the extension's required baseline operations.
- The case needs more attachments than `advancedBlendMaxColorAttachments`.
- A correlated overlap mode needs `advancedBlendCorrelatedOverlap`.
- An independent multi-attachment case needs `advancedBlendIndependentBlend`.
- A non-premultiplied source or destination needs its corresponding advertised property.
- A coherent case with `coherentOperations=true` needs `advancedBlendCoherentOperations`.

### Design-based pruning

- Additional RGB blend operations run only with `VK_BLEND_OVERLAP_UNCORRELATED_EXT` because the registration source states that overlap does not affect them.
- `independent` fixes both colors as premultiplied and uses uncorrelated overlap to focus on per-attachment state.
- `coherent` fixes attachment count to one and uses exactly two selected operations so the reference can model their sequence on one image.
- The oracle skips colors whose expected result is ill-formed or non-normal rather than treating undefined reference arithmetic as a conformance result.

## Key Takeaways

- This test family validates fixed-function advanced color blending, not shader arithmetic.
- `ops`, `independent`, and `coherent` are intermediate nodes that separate equation matrices, per-attachment state, and two-pass sequencing.
- The host reference model drives pass/fail by comparing readback images, with format-specific thresholds and explicit skipping of ill-formed expected colors.
- Support pruning follows the extension's advertised operation, attachment-count, overlap, independent-blend, premultiplication, and coherent-operation capabilities.

## Source Reference Appendix

| Topic | Source reference |
|-------|------------------|
| Family registration and matrix | [`createBlendOperationAdvancedTests`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2237) |
| Advanced pipeline state | [`BlendOperationAdvancedTestInstance::buildPipeline`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L998) |
| Generic runtime and oracle | [`iterate`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1363), [`verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1394) |
| Support requirements | [`BlendOperationAdvancedTest::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1523) |
| Coherent runtime and oracle | [`BlendOperationAdvancedTestCoherentInstance::prepareCommandBuffer`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1903), [`verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2089) |
| Legacy navigation page preserved | [`vktPipelineBlendOperationAdvancedTests.md`](vktPipelineBlendOperationAdvancedTests.md) |
| Vulkan semantics | [advanced blending](../../../../vulkan-docs/src/chapters/framebuffer.adoc#advanced-blending), [blend-operation-advanced features](../../../../vulkan-docs/src/chapters/features.adoc#features-blendOperationAdvanced), [blend-operation-advanced limits](../../../../vulkan-docs/src/chapters/limits.adoc#limits-blendOperationAdvanced) |
