# Understanding Brief: pipeline.blend_operation_advanced

## One-Sentence Test Purpose

This test checks whether `VK_EXT_blend_operation_advanced` applies advanced blend operations, overlap declarations, premultiplication state, independent attachment state, and coherent consecutive operations to the color attachments that the pipeline renders.

## Background Knowledge

### Advanced color blending

A color attachment starts with a destination color. A fragment shader supplies a source color, and the pipeline's blend state combines them before the attachment stores the result. `VK_EXT_blend_operation_advanced` adds blend operations such as `VK_BLEND_OP_MULTIPLY_EXT`, HSL modes, and Porter-Duff-style operations. The extension also adds `VkPipelineColorBlendAdvancedStateCreateInfoEXT`, which declares source and destination premultiplication plus the overlap mode. See [advanced blending in the Vulkan specification](../../../../vulkan-docs/src/chapters/framebuffer.adoc#advanced-blending).

Why it matters here:
- The fragment shader supplies test colors, but fixed-function color blending performs the behavior under test.
- Premultiplication and overlap declarations alter the reference calculation and can restrict supported cases.

### Coherent and independent attachment behavior

An implementation may support different advanced operations per color attachment only when its advanced-blend properties allow independent blending. Coherent operations concern two advanced blends that use the same attachment in sequence. The extension feature and property contracts are described in [the feature chapter](../../../../vulkan-docs/src/chapters/features.adoc#features-blendOperationAdvanced) and [the limits chapter](../../../../vulkan-docs/src/chapters/limits.adoc#limits-blendOperationAdvanced).

## One Concrete Example

A representative `ops` leaf uses `VK_BLEND_OP_MULTIPLY_EXT`, one `R16G16B16A16_SFLOAT` attachment, `VK_BLEND_OVERLAP_UNCORRELATED_EXT`, and premultiplied source and destination colors. The test clears the 32 by 32 attachment, draws rectangles with fixed source colors, then reads the image. [`calculateFinalColor`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1394) computes the matching reference color for each rectangle and the host compares it with the rendered pixel.

## End-to-End Test Flow

```text
[host] choose a registered ops, independent, or coherent case and check extension support and advertised properties
[host] create the color image or images, render pass, framebuffer, vertex buffer, pipeline layout, and graphics pipeline
[host] attach VkPipelineColorBlendAdvancedStateCreateInfoEXT to color-blend state and record the selected blend operation per attachment
[host] record image transitions and one draw, or two draw passes for coherent cases
[device] execute the vertex and fragment programs, then apply the selected fixed-function advanced blend operation to each color attachment
[host] submit and wait, read color attachments, reconstruct expected pixels, and threshold-compare expected and actual images
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`BlendOperationAdvancedTest::initPrograms()` emits a small vertex program and a fragment program. The fragment program receives a `Vec4` push constant and writes it as the source color. It does not implement blend equations; [`buildPipeline`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L998) puts those equations in `VkPipelineColorBlendAttachmentState` and the advanced-state `pNext` structure.

The registration function randomly selects operation values for the `independent` and `coherent` test cases from a deterministic group-name seed. It generates the case matrix in [`createBlendOperationAdvancedTests`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2237).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read | no | Holds the rectangle geometry. |
| Push constant `Vec4` | yes | yes | read | no | Supplies the fragment source color for each draw. |
| Color image or images | yes | yes | read and written | yes | Supplies destination colors and exposes blend results. |
| Render pass and framebuffer | yes | yes | used | no | Bind each color image as a color attachment. |
| Graphics pipeline | yes | yes | used | no | Carries advanced blend operation, overlap, and premultiplication state. |

## What Is Checked

The host creates a software reference image from the same source and destination colors. For generic cases it checks each attachment independently. For coherent cases it applies the first selected operation to the first draw's source and destination, then applies the second operation to that intermediate color. `tcu::floatThresholdCompare` compares each readback image with the reference using a `0.01` threshold for `R16G16B16A16_SFLOAT`; `R8G8B8A8_UNORM` uses the wider source-defined thresholds.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node
>
> **Candidate values:** `ops`, `independent`, `coherent`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ops` | Advanced operation equation, overlap handling, premultiplication conversion, or color-format result error. |
| `independent` | Per-attachment advanced blend state selection or multi-attachment result-routing error. |
| `coherent` | Consecutive-operation ordering, attachment load/store behavior, coherent-operation feature handling, or intervening-barrier error. |

## Important Variations and Special Cases

- `ops` varies attachment count over 1, 2, 4, 8, and 16; each generic case tests both `R16G16B16A16_SFLOAT` and `R8G8B8A8_UNORM`. Extra RGB blend operations run only with `VK_BLEND_OVERLAP_UNCORRELATED_EXT` because the source records that overlap modes do not affect them.
- `independent` uses 2, 4, 8, or 16 attachments, premultiplied colors, and uncorrelated overlap. Each attachment can receive a different selected operation.
- `coherent` uses one attachment and two selected operations. The `false` coherent flag inserts a color-attachment memory barrier between render passes; the `true` flag exercises the coherent-operation configuration.
- Support checks skip cases when the device lacks `VK_EXT_blend_operation_advanced`, an operation outside the required baseline set, enough color attachments, correlated overlap, independent blending, non-premultiplied colors, or `advancedBlendCoherentOperations`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration matrix | [`createBlendOperationAdvancedTests`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2237) | Creates `ops`, `independent`, and `coherent` leaves. |
| Pipeline state | [`buildPipeline`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L998) | Configures blend attachments and advanced state. |
| Support checks | [`checkSupport`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1523) | Gates leaves against extension features and properties. |
| Generic oracle | [`verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1394) | Builds and compares per-attachment references. |
| Coherent oracle | [`BlendOperationAdvancedTestCoherentInstance::verifyTestResult`](../../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L2089) | Applies the two operations in order before image comparison. |

## Questions / Risk Points for User Audit

- Is the distinction between fixed-function blending and shader source-color production clear?
- Does the `coherent` explanation make the two-pass ordering and barrier variant clear?
- Do the three intermediate nodes provide useful failure localization without overstating it?

## Conversion Notes for Final Wiki Rewrite

The final page should retain the brief's fixed-function blending prerequisite, one representative operation case, the runtime timeline, the resource roles, and the complete `### Failure Cause Mapping` table. It should replace teaching detail with concise source and specification evidence, and add Cause Analysis plus registration and mustpass accounting.
