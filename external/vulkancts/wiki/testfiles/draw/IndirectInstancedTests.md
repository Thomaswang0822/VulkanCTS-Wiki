## Overview

**Core question:** Do indirect draw records apply instance count, first instance, and first vertex consistently across each supported recording path?

`IndirectInstancedTests` validates indirect graphics draws when each command also controls instancing. The test writes `VkDrawIndirectCommand` records into an indirect buffer, submits one, two, four, or sixteen records with `vkCmdDrawIndirect`, and checks that vertex input, `instanceCount`, `firstInstance`, and `firstVertex` produce the expected 128x128 image. The same implementation runs through render-pass and, where supported, dynamic-rendering command-buffer arrangements.

The source is [`vktDrawIndirectInstancedTests.cpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp), with its public factory declared in [`vktDrawIndirectInstancedTests.hpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.hpp).

## Background Knowledge

An indirect draw moves the draw parameters from the command call into a device-visible array of `VkDrawIndirectCommand` structures. Each record supplies `vertexCount`, `instanceCount`, `firstVertex`, and `firstInstance`; `drawCount` is the number of records consumed and `stride` is the byte distance between records. This test fixes the stride to `sizeof(VkDrawIndirectCommand)` and changes `drawCount` through registration.

Instancing repeats the vertex sequence for each instance. The instance-rate color binding is indexed using the instance number, including the `firstInstance` offset. Thus, a correct implementation must combine indirect parameter fetch with both instance repetition and nonzero first-instance addressing.

The command-buffer path is also part of the contract. In a render-pass case, the primary command buffer begins a render pass, binds the pipeline and vertex buffers, issues the indirect draw, and ends the pass. In dynamic-rendering cases, drawing is recorded either directly in the primary buffer or in a secondary buffer executed by the primary. A complete secondary path begins and ends dynamic rendering in the secondary; a partial secondary path inherits rendering state while the primary owns the rendering scope.

## Registration Hierarchy

```text
draw.renderpass.indirect_instanced
├── 1
├── 2
├── 4
└── 16

draw.dynamic_rendering.primary_cmd_buff.indirect_instanced
├── 1
├── 2
├── 4
└── 16

draw.dynamic_rendering.partial_secondary_cmd_buff.indirect_instanced
├── 1
├── 2
├── 4
└── 16

draw.dynamic_rendering.complete_secondary_cmd_buff.indirect_instanced
├── 1
├── 2
├── 4
└── 16
```

Outside VulkanSC, the same group is present under the three dynamic-rendering branches shown above.

The dynamic-rendering registration is not emitted for `nested_partial_secondary_cmd_buff` or `nested_complete_secondary_cmd_buff`: the dispatcher passes `nestedSecondaryCmdBuffer` to the group and guards this family with `!groupParams->nestedSecondaryCmdBuffer`. In VulkanSC, the source excludes the secondary/dynamic-rendering recording code with `#ifndef CTS_USES_VULKANSC`; the VulkanSC mustpass contains the render-pass family only.

## Parameter Dimensions and Observed Values

The registered leaf name is the number of indirect command records consumed by one `vkCmdDrawIndirect` call.

| Leaf | `drawCount` | What it adds |
|---|---:|---|
| `1` | 1 | Baseline indirect instanced draw. |
| `2` | 2 | Two records with different `firstVertex` offsets. |
| `4` | 4 | Four-record multi-draw indirect sequence. |
| `16` | 16 | Larger multi-draw sequence and indirect-count-limit coverage. |

Within every leaf, `iterate()` runs these values:

| Internal dimension | Values | Effect |
|---|---|---|
| `instanceCount` | `0`, `1`, `2`, `4`, `20` | Number of instances for every indirect record. |
| `firstInstance` | `1`, `3`, `4`, `20` | Starting instance index used by instance-rate input and the reference shader. |
| Grid | `8x8` | Number of lower-left triangles used to build the position data. |
| Target | `128x128`, `VK_FORMAT_R8G8B8A8_UNORM` | Color image compared after submission. |

For a selected pair, the implementation computes `vertexCount = m_vertexPosition.size() / drawCount`. It creates one command per record:

```text
vertexCount   = generated position count / drawCount
instanceCount = selected internal instanceCount
firstVertex   = vertexCount * record index
firstInstance = selected internal firstInstance
```

The records are contiguous in the indirect buffer and are consumed with `drawCount` and `sizeof(VkDrawIndirectCommand)`. The `firstVertex` values partition the generated position array so that every record addresses its own segment.

## Behavior Parameters

The primary behavioral axis is the registered indirect-record count. The leaves select how many records a single indirect draw consumes; internal instance values then exercise the interaction between those records and instance-rate input.

### `1`: one indirect record

This is the baseline indirect instanced path and isolates command fetch from multi-record sequencing.

### `2`: two indirect records

This path checks record stepping and distinct `firstVertex` offsets while retaining the same instance behavior.

### `4`: four indirect records

This path extends record sequencing and makes ordering or stride errors more visible.

### `16`: sixteen indirect records

This path exercises the largest registered record count and its corresponding indirect-count limit.

## Shader Analysis

The generated shaders pass position and instance-rate color from vertex input to the fragment output. The page's primary behavioral axis is indirect record consumption rather than shader control flow; a representative shader walkthrough is therefore not expanded here.

### Resource Setup and Command Recording

`DrawIndirectInstancedInstance` creates a pipeline layout, color target image and view, command pool, command buffers, render pass/framebuffer when render-pass mode is selected, and a graphics pipeline. The pipeline has two vertex bindings:

- Binding 0 contains `tcu::Vec4` positions at `VK_VERTEX_INPUT_RATE_VERTEX`.
- Binding 1 contains `tcu::Vec4` colors at `VK_VERTEX_INPUT_RATE_INSTANCE`.

`prepareVertexData()` generates the 8x8 triangle grid and instance colors. The horizontal coordinates are scaled by `1 / instanceCount` so multiple instances tile horizontally. For `instanceCount = 0`, the implementation still creates the minimum safe color allocation, while the draw itself has no instances.

`initPrograms()` generates GLSL 430 stages. The vertex shader assigns `gl_Position = in_position` and forwards `in_color`; the fragment shader writes the forwarded color to location 0. The CPU reference mirrors this with `TestVertShader` and `TestFragShader`. `TestVertShader` calls `rr::readVertexAttribFloat` with the selected `firstInstance`, making the reference's instance-rate lookup use the same absolute starting index as the Vulkan draw.

Before drawing, `preRenderCommands()` transitions the color image to `GENERAL`, clears it, and inserts a transfer-write to color-attachment read/write barrier. `draw()` binds the pipeline and both vertex buffers, then issues:

```cpp
m_vk.cmdDrawIndirect(cmdBuffer, indirectBuffer->object(), 0,
                     drawCount, sizeof(vk::VkDrawIndirectCommand));
```

For a secondary path, the secondary command buffer is begun with rendering inheritance information. If it completely contains dynamic rendering, it begins and ends rendering itself; otherwise the primary begins the rendering scope, executes the secondary, and ends the scope. The primary is then submitted and the command pool is reset where required by the VulkanSC execution model.

### Support and Feature Requirements

Every leaf requires `DEVICE_CORE_FEATURE_DRAW_INDIRECT_FIRST_INSTANCE`, because all internal command records use a nonzero `firstInstance`.

For `drawCount > 1`, `checkSupport()` requires `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT` and rejects devices whose `maxDrawIndirectCount` is smaller than the requested count. Dynamic-rendering groups additionally require `VK_KHR_dynamic_rendering`.

The dispatcher, not the test case, controls the rendering-mode matrix. The family is omitted from nested secondary dynamic-rendering branches, and the implementation's compile-time guard omits non-render-pass paths for VulkanSC. These are registration and build boundaries, not runtime failures.

## Runtime Execution and Result Checking

The test records the selected indirect command, submits the rendering work, waits for completion, reads the color target, and compares it with the reference renderer using the source tolerance.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `1` | Basic indirect command fetch, instance addressing, or rendering. |
| `2` | Record stepping, ordering, or `firstVertex` handling in addition to the baseline path. |
| `4` | Multi-record sequencing, stride, or indirect-count handling. |
| `16` | Large record-range, address, or maximum indirect-count handling. |

### Cause Analysis

#### Indirect record consumption

**Possible failure symptoms:** The rendered image differs from the CPU reference for one or more record-count leaves.

**Possible implementation causes:** Incorrect indirect-buffer address, record stride, command ordering, or draw-parameter interpretation.

#### Instance addressing and rendering

**Possible failure symptoms:** Only selected instance counts or first-instance values produce incorrect placement or color.

**Possible implementation causes:** Instance-rate vertex input, `firstInstance` handling, shader execution, rasterization, or image readback.

## Case Pruning

### Requirement-based pruning

The implementation requires indirect first-instance support; multi-record leaves additionally require multi-draw indirect support and a sufficient `maxDrawIndirectCount`. Dynamic-rendering branches require dynamic rendering support.

### Design-based pruning

Nested secondary-command-buffer branches and VulkanSC non-render-pass paths are omitted by dispatcher or build guards. These are registration/build boundaries, not runtime failure results.

## Key Takeaways

- Numeric leaves select the number of indirect command records consumed by one draw.
- Every leaf also exercises instance count and nonzero first-instance addressing.
- A mismatch must be localized across indirect fetch, instance-rate input, command-buffer inheritance, rendering, and readback.

### Runtime Execution Details

After waiting for the queue, the test reads the color target into a `tcu::TextureLevel`. It creates a CPU reference at the same dimensions, clears it to opaque black, and renders the generated primitive list with `rr::Renderer::drawInstanced(command, instanceCount)`. The reference vertex shader uses the selected `firstInstance`; the fragment shader passes through the color.

The result is checked with [`tcu::fuzzyCompare`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L430-L440), using threshold `0.05`. The result description records the internal instance count and first-instance index. A failed comparison marks the test `QP_TEST_RESULT_FAIL`; passing every internal pair returns `QP_TEST_RESULT_PASS`.

The comparison is intentionally end-to-end. A failure may indicate an incorrect indirect-buffer address or stride, a wrong `drawCount`, record ordering or `firstVertex` handling, incorrect instance repetition or first-instance offset, vertex-input-rate state, command-buffer inheritance, rendering transitions, shader execution, rasterization, or image readback. The source does not expose a separate GPU-side parameter checksum, so the internal pair and command-buffer variant are the primary localization dimensions.

### Additional Failure Mapping
|---|---|
| Leaf `1` | Basic `VkDrawIndirectCommand` fetch, `instanceCount`, `firstInstance`, instance-rate attribute lookup, or ordinary rendering. |
| Leaf `2` | Incorrect record stride/addressing, record order, or `firstVertex` offset in addition to the baseline behavior. |
| Leaf `4` | Multi-draw indirect feature path, four-record fetch, or command sequencing. |
| Leaf `16` | Larger indirect command sequence, `maxDrawIndirectCount` handling, or buffer range/address calculation. |
| Only one internal `instanceCount` | Instance repetition, zero-instance handling, or geometry scaling. |
| Only one internal `firstInstance` | Absolute instance-index calculation or instance-rate buffer fetch. |
| Only secondary/dynamic-rendering modes | Command-buffer inheritance, rendering scope, `vkCmdExecuteCommands`, or dynamic-rendering state. |
| All modes | Pipeline vertex input, indirect buffer visibility, shader, attachment transition, rasterization, or readback. |

### Registration and Mustpass Evidence

The exact identifiers are present in the source's `drawCountTests` table:

```cpp
drawCountTests[] = {{1, "1"}, {2, "2"}, {4, "4"}, {16, "16"}};
```

The default Vulkan mustpass lists the four render-pass leaves and the same leaves under `primary_cmd_buff`, `partial_secondary_cmd_buff`, and `complete_secondary_cmd_buff`. The VulkanSC default lists only the four render-pass leaves:

- [`vk-default draw.txt`](../../../mustpass/main/vk-default/draw.txt#L793-L796): dynamic complete-secondary examples.
- [`vk-default draw.txt`](../../../mustpass/main/vk-default/draw.txt#L3327-L3330): dynamic partial-secondary examples.
- [`vk-default draw.txt`](../../../mustpass/main/vk-default/draw.txt#L6126-L6129): dynamic primary examples.
- [`vk-default draw.txt`](../../../mustpass/main/vk-default/draw.txt#L18613-L18616): render-pass examples.
- [`vksc-default draw.txt`](../../../mustpass/main/vksc-default/draw.txt#L959-L962): VulkanSC render-pass examples.

### Runtime Execution Details

The execution details above describe resource setup, command recording, readback, and failure interpretation for the indirect-instanced family.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Test declaration | [`vktDrawIndirectInstancedTests.hpp`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.hpp#L27-L40) |
| Instance setup and pipeline | [`DrawIndirectInstancedInstance::DrawIndirectInstancedInstance`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L169-L290) |
| Internal loops and indirect records | [`DrawIndirectInstancedInstance::iterate`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L292-L333) |
| Render-pass and dynamic-rendering recording | [`iterate`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L335-L401) |
| Reference and comparison | [`iterate`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L404-L443) |
| Vertex-data generation | [`prepareVertexData`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L446-L471) |
| Resource transitions and draw | [`preRenderCommands` / `draw`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L473-L504) |
| Secondary inheritance | [`beginSecondaryCmdBuffer`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L506-L544) |
| Support checks and shaders | [`DrawIndirectInstancedCase`](../../../modules/vulkan/draw/vktDrawIndirectInstancedTests.cpp#L546-L603) |
| Dispatcher registration | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L100) |
| Vulkan draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc) |
| Vertex-processing context | [`vertexpostproc.adoc`](../../../../vulkan-docs/src/chapters/vertexpostproc.adoc) |

### Preservation Note

The obsolete page [`vktDrawIndirectInstancedTests.md`](vktDrawIndirectInstancedTests.md) remains in place and is not modified. The registration group and leaf names remain exactly `indirect_instanced`, `1`, `2`, `4`, and `16`.
