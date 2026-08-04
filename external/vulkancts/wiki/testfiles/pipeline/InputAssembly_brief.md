# Understanding Brief: Input assembly

## One-Sentence Test Purpose

This test checks whether Vulkan assembles primitives from the selected topology and index type, honors primitive restart, and preserves restart state when indexed and non-indexed draws are mixed.

## Background Knowledge

### Primitive assembly and restart

`VkPipelineInputAssemblyStateCreateInfo::topology` determines how fetched vertices become points, lines, triangles, adjacency primitives, or patches. With indexed drawing, `primitiveRestartEnable` treats the index value reserved for the bound index type as a boundary: incomplete assembly is discarded and the next index starts a new primitive. The Vulkan specification describes this state and the restrictions on list topologies in [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L49-L89).

Why it matters here:
- The topology tests change the assembly rule while keeping the vertex shader simple.
- The restart tests place reserved index values at controlled primitive boundaries, then compare the resulting image with a reference renderer.

## One Concrete Example

A restart case can draw a strip with a sequence equivalent to `A, B, C, RESTART, D, E, F`. The first strip is assembled from `A, B, C`; the restart value prevents the following indices from joining that strip, so `D, E, F` starts a new one. The CTS uses this idea with generated indexed vertex data and several restart placements, rather than relying on a single hand-written triangle.

## End-to-End Test Flow

```text
[host] select a topology, index type, restart mode, or mixed-draw parameters
[host] generate vertex and index data, including reserved restart indices where required
[host] generate a pass-through vertex/fragment shader pair and create the graphics pipeline
[host] bind vertex/index buffers and issue indexed, non-indexed, or second-pass draws
[device] assemble primitives and render vertex colors into a color attachment
[host] copy the image to host-visible memory and compare it with a software reference or expected quadrant colors
[host] report pass or image mismatch
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The ordinary topology and restart cases generate a vertex shader that forwards position and color, plus a fragment shader that writes the forwarded color. The shaders expose the fixed-function input-assembly result; they do not implement topology or restart.
- The `restart_mix` cases generate the same pass-through pair with GLSL version 460 and can make primitive topology dynamic.
- Graphics pipeline state sets `VkPipelineInputAssemblyStateCreateInfo::topology` and, for restart cases, enables primitive restart. Dynamic-topology variants set the final topology with `vkCmdSetPrimitiveTopology`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read | no | Supplies positions and colors for assembled primitives. |
| Index buffer | yes, indexed cases | yes | read | no | Supplies UINT16, UINT32, or UINT8 indices and restart values. |
| Color image and readback buffer | yes | render target and copy destination | color written, then copied | yes | Carries the observable assembly result to the host. |

## What Is Checked

- `primitive_topology` and `primitive_restart` render a color image and compare it with `ReferenceRenderer` using an integer threshold of `UVec4(2, 2, 2, 2)` and position deviation `IVec3(1, 1, 0)`.
- `restart_mix` clears expected quadrants and compares the readback image with `tcu::floatThresholdCompare` at a zero threshold.
- Amber `restart_disabled_*` cases are executed by the Amber runner; their purpose is to show that an index equal to the restart value is ordinary index data when restart is disabled.

## Behavior Parameter Identification

> **Behavior parameter:** test family and restart mode
>
> **Candidate values:** `primitive_topology`, `primitive_restart` with `NORMAL`, `NONE`, `ALL`, `DIVIDE`, or `SECOND_PASS`, `restart_mix`, and monolithic-only `restart_disabled_*`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primitive_topology` | Incorrect topology selection, index-width handling, vertex fetch, primitive assembly, rasterization, or image comparison path. |
| `primitive_restart.NORMAL` | The enabled restart boundary is ignored or applied at the wrong primitive boundary. |
| `primitive_restart.NONE` | A restart boundary is introduced even though this enabled-restart test supplies no restart index. |
| `primitive_restart.ALL` | Restart handling is incorrect when restart indices are inserted throughout the generated primitive stream. |
| `primitive_restart.DIVIDE` | The split draw path or restart boundary produces different geometry from the expected divided primitives. |
| `primitive_restart.SECOND_PASS` | Restart handling or state retained across the second draw pass is incorrect. |
| `restart_mix` | Primitive-restart state leaks into or is lost across indexed/non-indexed draws, topology changes, or a large non-indexed draw. |
| `restart_disabled_*` | A disabled restart state is treated as enabled, or the Amber setup/expected result is wrong. |

## Important Variations and Special Cases

- `primitive_topology` registers 10 standard topologies for each of `index_type_uint16`, `index_type_uint32`, and `index_type_uint8`.
- `primitive_restart` uses 11 topology values for ordinary restart modes, while `DIVIDE` and `SECOND_PASS` use six list topologies. `POINT_LIST` is omitted for `ALL`.
- List and patch restart cases require `VK_EXT_primitive_topology_list_restart` and the matching feature bits. Adjacency and patch cases also require geometry or tessellation shader support.
- The `restart_mix` matrix has four booleans. `largeNonIndexedDraw` is valid only with `triangleList=true`.
- `primitive_restart` and `restart_mix` are inside `#ifndef CTS_USES_VULKANSC`; the `restart_disabled_*` Amber cases are monolithic-only.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Common support, data creation, and shader generation | [`InputAssemblyTest::checkSupport()` and `initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L242-L320) | Defines feature gates and the pass-through shader pair. |
| Topology registration | [`createPrimitiveTopologyTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1703-L1731) | Registers the three index-type branches and ten topology leaves. |
| Restart setup and support | [`PrimitiveRestartTest` constructor and `checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L702-L784) | Defines restart modes, index placement, and list-restart requirements. |
| Mixed indexed/non-indexed registration | [`createPrimitiveRestartTests()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L2186-L2336) | Defines restart leaves, Amber cases, and the `restart_mix` matrix. |
| Mixed draw execution and check | [`PrimitiveRestartMixCase::checkSupport()` and `PrimitiveRestartMixTest::iterate()`](../../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1799-L2184) | Shows dynamic topology, draw ordering, expected quadrants, and exact comparison. |
| Specification semantics | [Input assembly and primitive restart](../../../../vulkan-docs/src/chapters/drawing.adoc#L49-L89) | Defines topology, restart index values, and list-topology restrictions. |

## Questions / Risk Points for User Audit

- Does the split between `primitive_restart` modes and `restart_mix` make the state-retention checks clear?
- Is the distinction between unsupported cases and Vulkan SC compile-time exclusion clear?
- Should the final page include a concrete topology example beyond the short restart sequence?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's Background Knowledge to the primitive-assembly and restart concepts only.
- Use the test family as the primary behavior axis and copy the Failure Cause Mapping table directly into the final page.
- The pass-through shaders are not the tested behavior, so the final page should state that shader walkthroughs are not applicable instead of inventing a SPIR-V walkthrough.
- Keep the runtime section focused on generated buffers, draw ordering, reference rendering, and readback comparison.
