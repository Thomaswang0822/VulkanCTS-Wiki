## Overview

**Core question:** Do Vulkan draw commands expose the correct base vertex, base instance, and draw index to the vertex shader?

- This page covers the implementation in [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L25-L62), registered below `draw.renderpass.shader_draw_parameters`.
- The test keeps the graphics pipeline and `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` fixed while changing direct, indexed, indirect, instanced, first-instance, and multi-draw command parameters.
- The vertex shader uses `gl_BaseVertexARB`, `gl_BaseInstanceARB`, and `gl_DrawIDARB` to select vertex data, instance offsets, and per-draw colors. The resulting color image is compared with a host-built reference image.

## Background Knowledge

- `gl_BaseVertexARB` is the signed vertex offset applied by an indexed draw; it is zero for non-indexed draws. The shader can combine it with `gl_VertexIndex` to recover the index within the intended vertex data.
- `gl_BaseInstanceARB` is the first-instance value for a draw. Subtracting it from `gl_InstanceIndex` gives a zero-based instance slot even when the command starts at a nonzero instance.
- `gl_DrawIDARB` identifies the current draw within a multi-draw indirect command. It is distinct from the instance index and is meaningful here only because the command is indirect and has multiple records.
- A triangle strip consumes four consecutive vertices for the test's rectangle. The source deliberately places valid and junk records at different buffer indices so incorrect built-in values change the rendered image.

## Registration Hierarchy

```text
draw.renderpass.shader_draw_parameters
├── base_vertex
├── base_vertex_only
├── base_instance
├── base_instance_only
└── draw_index
```

The `base_vertex_only` and `base_instance_only` test families are registered only when secondary command-buffer recording is disabled. The source's dispatcher creates this test category through `ShaderDrawParametersTests` in [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L389-L465).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `base_vertex`, `base_vertex_only`, `base_instance`, `base_instance_only`, `draw_index` | Selects which shader draw parameter is checked and whether the check is isolated. | [`ShaderDrawParametersTests::init`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L467-L538) |
| Command form | `draw`, `draw_indexed`, `draw_indirect`, `draw_indexed_indirect` | Moves command parameters between direct API arguments, index data, and indirect records. | [`addDrawCase`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L357-L387) |
| Instancing | absent or `_instanced` | Uses one instance or `MAX_INSTANCE_COUNT` (3) instances and exercises base-instance addressing. | [`DrawTest::draw`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L281-L355) |
| First instance | absent or `_first_instance` | Uses nonzero `firstInstance` values in indirect commands. | [`DrawTest::draw`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L301-L328) |
| Multi-draw | absent or `draw_index`'s three-record indirect call | Uses `MAX_INDIRECT_DRAW_COUNT` (3) records so `gl_DrawIDARB` selects three draw positions and colors. | [`DrawTest::draw`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L301-L348) |
| Topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` | Keeps primitive assembly constant while shader-visible draw parameters vary. | [`FlagsTestSpec`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L45-L62) |

## Behavior Parameters

The primary behavioral axis is the registered test family. Each family uses the same draw harness but asks a different question about shader-visible command state.

### `base_vertex`: combined base-vertex behavior

The four leaves `draw`, `draw_indexed`, `draw_indirect`, and `draw_indexed_indirect` compare non-indexed zero behavior with indexed `vertexOffset` behavior. The shader tests `(gl_VertexIndex - gl_BaseVertexARB)` against the reference index and colors only the intended vertices with the selected instance color.

### `base_vertex_only`: isolated base-vertex behavior

This family uses `VertexFetchShaderDrawParametersBaseVert.vert` and removes the instance-offset part of the combined shader. It retains the same four command forms and is restricted to primary command buffers to avoid repeating the same isolation check in secondary paths.

### `base_instance`: combined base-instance behavior

The six leaves are `draw`, `draw_indexed`, `draw_indirect`, `draw_indirect_first_instance`, `draw_indexed_indirect`, and `draw_indexed_indirect_first_instance`. The shader computes `gl_InstanceIndex - gl_BaseInstanceARB`; nonzero `firstInstance` values therefore test that both built-ins describe the same command invocation.

### `base_instance_only`: isolated base-instance behavior

This family uses `VertexFetchShaderDrawParametersBaseInst.vert` and keeps the expected vertex reference anchored at index 2. It covers the same six command forms as `base_instance`, again only for primary command buffers.

### `draw_index`: multi-draw draw-index behavior

The four leaves are `draw`, `draw_instanced`, `draw_indexed`, and `draw_indexed_instanced`. Every leaf is indirect and multi-draw: three records are submitted in one `vkCmdDrawIndirect` or `vkCmdDrawIndexedIndirect` call. `VertexFetchShaderDrawParametersDrawIndex.vert` uses `gl_DrawIDARB` to select a per-draw offset and color, while instance addressing remains independent.

## Shader Analysis

All four vertex shaders require `GL_ARB_shader_draw_parameters` and share position, color, and reference-index inputs. The fragment stage is the pass-through `vulkan/draw/VertexFetch.frag`. The shader is not checking a host-visible scalar; it encodes built-in correctness into rectangle position and color, making a wrong built-in visible in the attachment image.

### Representative Shader Walkthrough 1

`VertexFetchShaderDrawParameters.vert` is the representative combined path. It computes the zero-based instance slot from `gl_InstanceIndex - gl_BaseInstanceARB`, uses `gl_VertexIndex - gl_BaseVertexARB` to recognize the intended four-vertex rectangle, and requires `gl_DrawIDARB == 0` for the first indirect draw. Matching vertices receive the instance color; all other vertices receive red. [`VertexFetchShaderDrawParameters.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParameters.vert)

The isolated shaders retain the same built-in expressions but remove the unrelated dimension: `VertexFetchShaderDrawParametersBaseVert.vert` focuses on base vertex, and `VertexFetchShaderDrawParametersBaseInst.vert` focuses on base instance. `VertexFetchShaderDrawParametersDrawIndex.vert` adds `perDraw[gl_DrawIDARB]` and selects `colors[gl_DrawIDARB]` for the three indirect records. [`VertexFetchShaderDrawParametersDrawIndex.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParametersDrawIndex.vert)

The host reference mirrors the shader's visible effects with three instance offsets, three draw offsets, and four colors in [`DrawTest::drawReferenceImage`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L225-L255). The generated GLSL is compiled by the CTS shader program setup; no shader-side storage-buffer result is used.

## Runtime Execution and Result Checking

- The instance creates vertex data containing four valid rectangle vertices separated by junk data. Indexed cases additionally create a `VK_INDEX_TYPE_UINT32` index buffer; indirect cases create a host-visible indirect buffer with room for three command records.
- Direct commands use `vkCmdDraw` or `vkCmdDrawIndexed`. Indirect commands populate `VkDrawIndirectCommand` or `VkDrawIndexedIndirectCommand` with the selected offsets, instance count, and optional nonzero `firstInstance`, then issue one indirect call with `drawCount` equal to one or three.
- Depending on shared draw parameters, the command is recorded through a legacy render pass, dynamic rendering, or a secondary command buffer path. The test submits the primary command buffer and waits for completion.
- The color target is read back and compared with the 0.05 threshold in [`DrawTest::iterate`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L257-L279). A mismatch returns `Rendered image is incorrect`; otherwise the case passes with `OK`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `base_vertex` | Incorrect `gl_BaseVertexARB` exposure or indexed vertex-offset handling, vertex fetch, command recording, or image comparison path. |
| `base_vertex_only` | Incorrect isolated base-vertex built-in exposure, indexed/non-indexed command handling, or shader/pipeline setup. |
| `base_instance` | Incorrect `gl_BaseInstanceARB` exposure, instance-index calculation, `firstInstance` handling, or command execution. |
| `base_instance_only` | Incorrect isolated base-instance exposure or instanced command handling. |
| `draw_index` | Incorrect `gl_DrawIDARB` exposure or multi-draw indirect record selection, including interaction with indexed or instanced execution. |

### Cause Analysis

#### Shader-visible base vertex

**Possible failure symptoms:** The intended rectangle is missing or the attachment contains red output when an indexed command uses a nonzero vertex offset.

**Possible implementation causes:** The implementation may expose the wrong base vertex to the vertex shader or apply `vertexOffset` incorrectly when fetching indexed vertices. The exact fault location requires source-level investigation; the image alone does not distinguish shader lowering, command interpretation, and vertex fetch.

#### Shader-visible base instance and first instance

**Possible failure symptoms:** Instanced rectangles appear at the wrong offsets or with the wrong colors, especially in `_first_instance` leaves.

**Possible implementation causes:** The implementation may report an incorrect `gl_BaseInstanceARB`, mishandle `firstInstance` in an indirect record, or compute instance indexing inconsistently. The feature gate requires `drawIndirectFirstInstance` for the nonzero indirect cases.

#### Shader-visible draw index and multi-draw records

**Possible failure symptoms:** The three rectangles overlap, use the wrong colors, or appear at the wrong per-draw offsets in `draw_index`.

**Possible implementation causes:** The implementation may fail to advance indirect records correctly, report the wrong draw index, or mishandle the interaction between multi-draw execution and indexed/instanced commands. The test requires multi-draw indirect support before execution.

#### Shared rendering and image validation

**Possible failure symptoms:** Broad image differences occur across otherwise unrelated families or recording modes.

**Possible implementation causes:** The mismatch may be in pipeline setup, attachment rendering, command-buffer inheritance, image readback, or the host reference comparison. Investigation is needed before attributing such a failure to a shader built-in.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_shader_draw_parameters`; on Vulkan 1.1 and later the optional `shaderDrawParameters` feature must be enabled.
- Dynamic-rendering variants require `VK_KHR_dynamic_rendering`.
- `TEST_FLAG_MULTIDRAW` requires `DEVICE_CORE_FEATURE_MULTI_DRAW_INDIRECT`.
- `TEST_FLAG_FIRST_INSTANCE` requires `DEVICE_CORE_FEATURE_DRAW_INDIRECT_FIRST_INSTANCE`.
- The isolated families are not registered when `useSecondaryCmdBuffer` is enabled; this is intentional duplication control rather than a device-support failure.

### Design-based pruning

- `base_vertex` and `base_vertex_only` use four command forms; `base_instance` and `base_instance_only` add the two `_first_instance` forms because nonzero first-instance behavior is their additional axis.
- `draw_index` always uses indirect multi-draw and therefore has only four combinations of indexed and instanced execution.
- The topology is fixed to `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`; topology variation is outside this test family's purpose.
- Buffer padding and junk records are deliberate: they prevent a zero-based or accidentally contiguous fetch from passing by coincidence.

## Key Takeaways

- The test validates shader-visible command state through rendered geometry and color rather than through a separate scalar result buffer.
- Indexed and non-indexed paths distinguish base-vertex behavior; instanced and `_first_instance` paths distinguish base-instance behavior; three-record indirect calls distinguish draw-index behavior.
- The same implementation-bearing test family covers direct, indexed, indirect, and indexed-indirect forms, while isolated families reduce ambiguity when diagnosing a failure.
- A failing image comparison identifies a mismatch in the complete draw path. See `## Failure Meaning` before assigning the failure to a particular built-in.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `ShaderDrawParametersTests::init` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L467-L538) | Registers the exact test families, shader files, flags, and leaves. |
| `addDrawCase` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L357-L387) | Builds exact leaf identifiers from command flags. |
| `DrawTest::draw` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L281-L355) | Writes direct and indirect command parameters and issues draw calls. |
| `drawReferenceImage` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L225-L255) | Defines expected instance/draw offsets and colors. |
| `DrawTest::iterate` | [`vktDrawShaderDrawParametersTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderDrawParametersTests.cpp#L257-L279) | Submits, reads back, and compares the rendered image. |
| Combined shader | [`VertexFetchShaderDrawParameters.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParameters.vert) | Exercises all three shader draw-parameter built-ins. |
| Isolated shaders | [`VertexFetchShaderDrawParametersBaseVert.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParametersBaseVert.vert), [`VertexFetchShaderDrawParametersBaseInst.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParametersBaseInst.vert) | Separate base-vertex and base-instance checks. |
| Draw-index shader | [`VertexFetchShaderDrawParametersDrawIndex.vert`](../../../data/vulkan/draw/VertexFetchShaderDrawParametersDrawIndex.vert) | Uses draw ID to select per-draw offsets and colors. |
| Mustpass registration | [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28999-L29022) | Confirms the `draw.renderpass.shader_draw_parameters` hierarchy and leaves. |
| Vulkan feature requirements | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L1795-L1805) | Defines the relevant shader-draw-parameter and draw-command feature context. |
| Vulkan draw semantics | [`drawing.adoc`](../../../../vulkan-docs/src/chapters/drawing.adoc#L1540-L1580) | Defines direct and indirect draw parameter behavior. |
