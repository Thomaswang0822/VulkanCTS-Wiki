# Understanding Brief: StencilExport

## One-Sentence Test Purpose

This test checks whether `VK_EXT_shader_stencil_export` lets a fragment shader replace the stencil reference and makes a later subpass expose the resulting checkerboard through stencil comparison.

## Background Knowledge

`FragStencilRefEXT` is a fragment-shader output built-in. A shader that writes it declares `StencilRefReplacingEXT`; Vulkan then uses the value as the stencil reference for the covered samples. Only the low-order bits that fit the stencil attachment participate in the test.

Stencil comparison controls fragment coverage. A later draw with `VK_COMPARE_OP_EQUAL` and reference zero therefore produces color only where the first draw stored zero. This lets a color image reveal the stencil pattern without copying stencil data to the host.

`VK_AMD_shader_early_and_late_fragment_tests` permits fragment tests before and after fragment-shader execution. Its stencil-reference modes tell early testing how the shader-produced reference relates to the API reference, while late testing uses the produced reference.

## One Concrete Example

For `pipeline.monolithic.shader_stencil_export.s8_uint.op_replace`, the first full-screen draw calculates `(floor(x) / 16 + floor(y) / 16) % 2` and writes zero or one to `gl_FragStencilRefARB`. Its replace operation stores that reference in an `S8_UINT` stencil attachment. A second full-screen draw compares each stencil value with zero and writes blue only for matching squares. CTS copies the color image to a host-visible buffer and compares it with a matching blue-and-clear checkerboard.

## End-to-End Test Flow

```text
[host] select construction type, stencil format, and ordinary or early-and-late leaf
[host] check shader-stencil-export, format, construction, and optional AMD feature support
[host] create stencil and color attachments, a two-subpass render pass, pipelines, framebuffer, command buffer, and readback buffer
[device] first subpass draws a full-screen primitive whose fragment shader exports a zero-or-one stencil reference
[device] second subpass compares stencil with zero and writes blue only for matching fragments
[device] copy the color attachment to the host-visible buffer and wait for completion
[host] compare the copied color image with the generated checkerboard reference
```

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Created/configured by host? | Used by device? | Read by host? | Why it matters |
|---|---:|---:|---:|---|
| Stencil image and view | yes | depth/stencil attachment in both subpasses | no | Stores the shader-exported references. |
| RGBA color image and view | yes | color attachment in the second subpass | copied to buffer | Converts the stencil comparison into observable blue pixels. |
| Vertex shader | yes | both draws | no | Emits a full-screen rectangle from `gl_VertexIndex`. |
| Ordinary fragment shader | yes | first draw for `op_replace` | no | Exports the checkerboard reference through `gl_FragStencilRefARB`. |
| SPIR-V fragment shaders | yes | first draw for `op_replace_early_and_late` | no | Add `EarlyAndLateFragmentTestsAMD` and one stencil-reference relation mode. |
| Color fragment shader | yes | second draw | no | Writes constant blue when stencil comparison retains coverage. |
| Host-visible color buffer and reference image | yes | transfer destination | yes | Provide the final comparison oracle. |

## What Is Checked

The ordinary leaf checks shader-produced stencil references with `VK_STENCIL_OP_REPLACE`. The early-and-late leaf repeats the same observable checkerboard for six SPIR-V execution modes: `StencilRefGreaterFrontAMD`, `StencilRefLessFrontAMD`, `StencilRefGreaterBackAMD`, `StencilRefLessBackAMD`, `StencilRefUnchangedFrontAMD`, and `StencilRefUnchangedBackAMD`. The host uses `floatThresholdCompare` with a `Vec4(0.02f)` threshold against a generated 16-pixel-square reference.

## Important Variations and Special Cases

- The intermediate-node axis is the stencil attachment format: `s8_uint`, `d24_unorm_s8_uint`, and `d32_sfloat_s8_uint`.
- Each format contains `op_replace`; non-Vulkan-SC builds also register `op_replace_early_and_late`.
- The early-and-late leaf requires `VK_AMD_shader_early_and_late_fragment_tests` and its `shaderEarlyAndLateFragmentTests` feature.
- Default Vulkan mustpass roots each contain six leaves for `monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_linked_spirv`, `shader_object_linked_binary`, `shader_object_unlinked_spirv`, and `shader_object_unlinked_binary`. Vulkan SC registers the three ordinary `monolithic` leaves only.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `s8_uint` | Shader stencil-reference export, replace operation, stencil comparison, or stencil-only attachment handling is incorrect. |
| `d24_unorm_s8_uint` | Shader stencil-reference export or the stencil aspect of a combined depth/stencil attachment is incorrect. |
| `d32_sfloat_s8_uint` | Shader stencil-reference export or the stencil aspect of a combined depth/stencil attachment is incorrect. |

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Program generation | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L98-L218) | Builds ordinary GLSL and early-and-late SPIR-V shaders. |
| Render pass and pipeline state | [`makeTestRenderPass` and `preparePipelineWrapper`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L231-L418) | Defines two subpasses, their dependency, and stencil states. |
| Execution and comparison | [`testStencilExportReplace`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L443-L596) | Draws, reads the color image, and compares it with the reference. |
| Support and registration | [`checkSupport` and `createStencilExportTests`](../../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L598-L651) | Defines requirements, formats, and leaves. |
| Stencil-reference contract | [Fragment stencil reference](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-fragstencilref) | Defines `FragStencilRefEXT`, its execution mode, and bit-width handling. |
| Fragment-operation ordering | [Fragment Operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops) | Defines placement of fragment tests and stencil reference replacement. |

## Questions / Risk Points for User Audit

- The final color comparison observes the whole two-subpass path, so it identifies an operation shape rather than one exclusive implementation stage.
- The ordinary and AMD leaves use different shader artifact sources but share the same color oracle.

## Conversion Notes for Final Wiki Rewrite

Use the three direct format intermediate nodes as the behavior axis. Copy the failure-cause mapping unchanged into the final page. Keep the shader analysis focused on the one ordinary GLSL shader and explain that the AMD variants are embedded SPIR-V source rather than reconstructing six near-identical assemblies.
