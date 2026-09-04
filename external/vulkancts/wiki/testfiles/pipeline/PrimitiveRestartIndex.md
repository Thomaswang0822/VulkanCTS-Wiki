## Overview

**Core question:** Does Vulkan honor custom primitive-restart indices across indexed draw forms, topologies, index widths, dynamic state, and secondary-command execution?

- [`vktPipelinePrimitiveRestartIndexTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L421-L507) implements the `pipeline.*.primitive_restart_index` family.
- The family is registered for monolithic, graphics-pipeline-library, fast-linked-library, and unlinked-SPIR-V shader-object construction roots.
- It varies the reserved restart value, primitive topology, index width, direct or indirect draw form, dynamic primitive-restart state, conditional rendering, and secondary-command execution.
- The test renders a 4×8 target whose colored blocks expose whether the implementation compares the custom restart value correctly and preserves the expected assembly boundaries.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A primitive restart value ends the current indexed primitive and starts assembly of the next primitive. The reserved value depends on the selected index type unless a custom restart index is supplied.
- The restart comparison occurs before `vertexOffset` is added to an index. This distinction matters when a test deliberately uses `0` or `1` as the custom restart value while the visible geometry uses offset vertex data.
- Indexed, indirect, and indirect-count draws all consume indexed draw parameters, but they transport those parameters through different command paths. Secondary-command cases additionally record the draw in a secondary command buffer before executing it from a primary command buffer.

## Registration Hierarchy

```text
pipeline.monolithic.primitive_restart_index
├── point_list
├── line_list
├── line_strip
├── triangle_list
├── triangle_strip
├── triangle_fan
├── line_list_with_adjacency
├── line_strip_with_adjacency
├── triangle_list_with_adjacency
├── triangle_strip_with_adjacency
├── patch_list
├── secondary_cmd
└── conditional_rendering
```

The dispatcher adds this family below `pipeline.monolithic`, `pipeline.pipeline_library`, `pipeline.fast_linked_library`, and `pipeline.shader_object_unlinked_spirv`; it does not add it below linked or binary shader-object roots. The topology, `secondary_cmd`, and `conditional_rendering` children are created by [`createPrimitiveRestartIndexTests()`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1174-L1285). The monolithic mustpass file contains 810 leaves for the family, and the same family is present in the three other supported construction roots.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction type | `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`, `PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY`, `PIPELINE_CONSTRUCTION_TYPE_FAST_LINKED_LIBRARY`, `PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_UNLINKED_SPIRV` | Selects how the graphics pipeline or shader objects are constructed while keeping the restart-index behavior under test. | [dispatcher](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L95-L103), [family insertion](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L219-L220) |
| Primitive topology | `POINT_LIST`, `LINE_LIST`, `LINE_STRIP`, `TRIANGLE_LIST`, `TRIANGLE_STRIP`, `TRIANGLE_FAN`, `LINE_LIST_WITH_ADJACENCY`, `LINE_STRIP_WITH_ADJACENCY`, `TRIANGLE_LIST_WITH_ADJACENCY`, `TRIANGLE_STRIP_WITH_ADJACENCY`, `PATCH_LIST` | Changes how many indices form a primitive and therefore where a restart boundary can discard incomplete assembly. | [`getTopologies()`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1075-L1100) |
| Index type | `VK_INDEX_TYPE_UINT32`, `VK_INDEX_TYPE_UINT16`, `VK_INDEX_TYPE_UINT8` | Changes index encoding and the width of the custom restart value. | [`getIndexTypes()`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1102-L1114) |
| Custom restart index | `zero`, `one`, `penultimate`, `max` | Chooses whether the restart value collides with low ordinary indices, the penultimate geometry index, or the maximum value for the selected width. | [`getRestartIndices()`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1116-L1128) |
| Draw call | `draw_indexed`, `draw_indexed_indirect`, `draw_indexed_indirect_count` | Selects direct indexed execution or one of the indirect parameter-buffer paths. | [`getDrawCalls()`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1160-L1169) |
| Dynamic restart state | no suffix, `_dyn_prim_restart` | Selects whether `VK_DYNAMIC_STATE_PRIMITIVE_RESTART_ENABLE` is set dynamically instead of relying only on pipeline state. | [`createPrimitiveRestartIndexTests()`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1193-L1216) |
| Secondary and conditional execution | `secondary_cmd`; `conditional_rendering` with optional `_secondary_cmd` | Moves the draw into a secondary command buffer or gates it with `VK_EXT_conditional_rendering`. | [`secondary_cmd` registration](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1225-L1251), [`conditional_rendering` registration](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1253-L1283) |

For each construction root, the topology matrix contributes `11 × 3 × 4 × 3 × 2 = 792` leaves. `secondary_cmd` contributes six leaves and `conditional_rendering` contributes twelve, for 810 leaves in the monolithic mustpass file.

## Behavior Parameters

The primary behavioral axis is the registered intermediate group below `primitive_restart_index`. The topology branches exercise custom restart values in ordinary indexed draws; the two additional branches exercise command transport and execution-state interactions.

### Topology branches: custom restart across primitive assembly rules

Each topology branch combines three index widths, four custom restart values, three draw forms, and static or dynamic primitive-restart state. The generated index stream is arranged so that the custom restart value should prevent the final visible portion of a row from becoming a primitive. The test compares the rendered blocks against the expected colors, exposing implementations that treat the restart value as an ordinary index or add `vertexOffset` before comparing it.

Adjacency topologies include the extra adjacency vertices in their assembly pattern. `patch_list` uses pass-through tessellation stages and requires tessellation support; adjacency branches require a geometry shader.

### `secondary_cmd`: restart state in secondary command execution

This branch fixes the topology to `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP`, the index type to `VK_INDEX_TYPE_UINT16`, and the custom restart value to `one`. It varies the direct, indirect, and indirect-count draw forms and whether primitive-restart enable is dynamic, then records the indexed draw in a secondary command buffer. The result checks that the restart state and indexed parameters survive secondary-command execution.

### `conditional_rendering`: restart state with conditional execution

This branch uses a triangle strip with `VK_INDEX_TYPE_UINT32` and custom restart value `zero`. It varies direct, indirect, and indirect-count draws, dynamic restart enable, and optional secondary-command execution while a zero conditional-rendering value disables rendering. The expected cleared image checks that conditional rendering suppresses the entire draw without turning the restart value into visible geometry.

## Shader Analysis

The shaders are pass-through fixtures rather than the property under test, so this page does not require a representative shader walkthrough. The vertex shader forwards the generated position and point size, and the fragment shader writes the push-constant color. Patch-list cases add pass-through tessellation-control and tessellation-evaluation shaders; adjacency cases require a geometry stage for topology support. The tested behavior is fixed-function primitive assembly and command execution, not shader computation. [`RestartIndexCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L509-L580)

## Runtime Execution and Result Checking

- The test creates a 4×8 `VK_FORMAT_R8G8B8A8_UNORM` color target and generates rows of vertices whose primitives cover the target's colored blocks.
- It encodes the selected custom restart value into `uint8`, `uint16`, or `uint32` index data. For low restart values, it uses padding vertices and a separate manual offset so the restart comparison can be distinguished from vertex-offset application.
- Direct cases issue `vkCmdDrawIndexed`. Indirect cases create a parameter buffer with no-op commands around the selected indexed draw; indirect-count cases additionally use a count buffer and require `VK_KHR_draw_indirect_count`.
- When dynamic restart is selected, the command buffer sets `VK_DYNAMIC_STATE_PRIMITIVE_RESTART_ENABLE`. Conditional cases bind a zero-valued conditional-rendering buffer, and secondary cases execute the recorded draw through a primary command buffer.
- The command buffer transitions the color image, binds the selected pipeline construction, index and vertex buffers, push constants, and draw state, then copies the result to host-visible memory after queue completion.
- The result comparison checks the expected colored blocks. A mismatch indicates that the restart boundary, topology assembly, index-width handling, command transport, or conditional state did not match the CTS contract.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Topology branches | Custom restart comparison, index-width handling, `vertexOffset` ordering, or primitive assembly is incorrect for the selected topology. |
| `secondary_cmd` | Restart state or indexed draw parameters are not preserved when the draw is recorded and executed through a secondary command buffer. |
| `conditional_rendering` | Conditional execution does not suppress the indexed draw correctly, or restart state interacts incorrectly with direct, indirect, or secondary execution. |

### Cause Analysis

#### Restart comparison or vertex-offset ordering is incorrect

**Possible failure symptoms:** The final block contains unexpected geometry, or a low custom restart value causes a crash, extra coverage, or a missing primitive.

**Possible implementation causes:** The implementation may add `vertexOffset` before comparing the index with the custom restart value, interpret the restart value with the wrong width, or fail to discard incomplete primitive assembly at the boundary. The test deliberately uses `zero` and `one` to make these ordering errors visible. [Indexed drawing](../../../../vulkan-docs/src/chapters/drawing.adoc#L1238-L1268)

#### Topology-specific primitive assembly is incorrect

**Possible failure symptoms:** Only adjacency, patch, strip, fan, or another topology family produces wrong colored blocks while simpler topologies pass.

**Possible implementation causes:** The implementation may use the wrong primitive vertex count, mishandle adjacency vertices, apply list-restart rules to the wrong topology, or assemble a patch after a restart when the incomplete patch should be discarded. The exact failing topology and support path are needed for driver-level diagnosis.

#### Indirect or secondary command transport loses restart state

**Possible failure symptoms:** Direct draws pass but indirect, indirect-count, or secondary-command variants produce extra or missing geometry.

**Possible implementation causes:** The implementation may read the wrong indexed-draw parameters, fail to preserve the dynamic restart enable state across command execution, or mishandle the index-buffer binding when a secondary command is executed by a primary command buffer.

#### Conditional execution does not suppress the draw

**Possible failure symptoms:** A conditional-rendering case writes colored blocks even though its condition value disables rendering, or only one command form ignores the condition.

**Possible implementation causes:** The implementation may evaluate the condition incorrectly, apply conditional rendering only to direct draws, or fail to preserve the condition across secondary-command execution. A failure can also expose a command-buffer state transition problem rather than a primitive-restart arithmetic error.

## Case Pruning

### Requirement-based pruning

- Every case requires the selected pipeline construction type to satisfy `checkPipelineConstructionRequirements`.
- Custom restart cases require `VK_EXT_primitive_restart_index` unless the source is built with `AVOID_CUSTOM_RESTART_INDEX`.
- `uint8` index cases require the `indexTypeUint8` feature.
- Dynamic restart cases require `extendedDynamicState2`.
- List-topology restart cases require `primitiveTopologyListRestart`; patch-list restart cases require `primitiveTopologyPatchListRestart` and the core tessellation-shader feature.
- Adjacency topologies require the core geometry-shader feature.
- Indirect-count cases require `VK_KHR_draw_indirect_count`; conditional cases require `VK_EXT_conditional_rendering`.
- The source adds this family only outside `CTS_USES_VULKANSC`, so it is absent from Vulkan SC registration.

### Design-based pruning

- The ordinary matrix uses 11 topologies, three index widths, four custom restart values, three draw forms, and two restart-state modes. This gives broad coverage while keeping each topology's cases structurally comparable.
- `secondary_cmd` fixes a representative triangle-strip configuration and varies command transport and dynamic state instead of multiplying the full topology matrix.
- `conditional_rendering` uses a triangle strip and a zero condition value to isolate whole-draw suppression; it adds optional secondary execution because that is a separate command-recording risk.
- The two device-address draw forms are present in the enum but commented out by `getDrawCalls()`, so they are not part of the current registered matrix.

## Key Takeaways

- The family tests custom restart-index comparison before vertex-offset application, not shader arithmetic.
- The ordinary matrix combines topology, index width, restart value, draw form, and dynamic state; the expected image makes incorrect assembly visible.
- `secondary_cmd` and `conditional_rendering` extend the same restart behavior into command-buffer and whole-draw execution paths.
- Support checks intentionally separate index-width, topology, shader-stage, indirect-count, conditional-rendering, and pipeline-construction requirements.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter and support model | [`Params`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L119-L211) and [`RestartIndexCase::checkSupport`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L456-L507) | Defines the restart values, topology-specific requirements, and feature gates |
| Shader fixtures | [`RestartIndexCase::initPrograms`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L509-L580) | Shows the pass-through graphics and optional tessellation shaders |
| Index and indirect buffers | [`makeIndexBuffer`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L582-L628) and [`makeIndirectBuffer`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L631-L657) | Encodes index widths and indirect draw parameters |
| Runtime execution | [`RestartIndexInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L659-L1071) | Records the draw paths, state, image transitions, and readback |
| Topology and matrix registration | [`createPrimitiveRestartIndexTests`](../../../modules/vulkan/pipeline/vktPipelinePrimitiveRestartIndexTests.cpp#L1174-L1285) | Defines the topology matrix and the secondary/conditional branches |
| Category dispatcher | [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L95-L220) | Places the family below the supported pipeline-construction roots |
