## Overview

**Core question:** When `vkCmdSetBlendConstants` sets the constant color used by `VK_BLEND_FACTOR_CONSTANT_COLOR` and `VK_BLEND_FACTOR_CONSTANT_ALPHA` blend factors, does the rendered output match the blend formula evaluated with those dynamic constants?

- [vktDynamicStateCBTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L1) implements the `cb_state` test family of the `dynamic_state` test category.
- Both leaves draw a full-screen green quad onto a white background with blending enabled. The blend factors reference the dynamic blend constants, which are set to `(0.33, 0.1, 0.66, 0.5)` during command-buffer recording. The test passes when the rendered image matches a software reference frame computed from the blend formula with those constants.
- Two leaves cover the vertex-shader pipeline and the mesh-shader pipeline; the mesh-shader leaf is excluded on Vulkan SC builds.
- Both leaves share one instance class, [`BlendConstantsTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L49), and the shared [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) harness.

## Background Knowledge

- **Dynamic blend constants.** Vulkan allows blend factors `VK_BLEND_FACTOR_CONSTANT_COLOR` and `VK_BLEND_FACTOR_CONSTANT_ALPHA` to reference four constant values supplied through `vkCmdSetBlendConstants`. When a pipeline declares those factors, the draw is invalid unless the constants have been set (and not subsequently invalidated) before recording the draw. The constants are a dynamic state, so they are not baked into the pipeline object and can change between draws.
- **Blend formula.** For each color attachment, the fixed-function blend unit computes the blended result from source (fragment) and destination (attachment) values. The standard add operation evaluates `result = source * sourceBlendFactor + destination * destinationBlendFactor`, per channel, then clamps to the representable range. A green source blended over a white destination with constant-dependent factors therefore produces a channel value that depends directly on the dynamic constants.

## Registration Hierarchy

```text
dynamic_state.monolithic.cb_state
├── blend_constants
└── blend_constants_mesh    (non-VulkanSC only)
```

The test family is registered once per pipeline construction type by the category dispatcher. The `blend_constants_mesh` leaf is compiled out on Vulkan SC builds ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L222-L245)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader type | Vertex+Fragment, Mesh+Fragment | Selects the `blend_constants` versus `blend_constants_mesh` leaf. The mesh path replaces the vertex-shader draw with `vkCmdDrawMeshTasksEXT`, otherwise the blend setup and validation are identical. | [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L229-L244) |
| Pipeline construction type | Passed from the parent group | Selects monolithic, pipeline-library, fast-linked-library, or one of the shader-object construction types. Does not change the tested blend property. | [DynamicStateCBTests constructor](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L210-L216) |
| Blend constants | `(0.33f, 0.1f, 0.66f, 0.5f)` | The dynamic RGBA values set through `vkCmdSetBlendConstants`. They feed the `CONSTANT_COLOR` and `CONSTANT_ALPHA` destination blend factors. | [setDynamicBlendState](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L132) |
| Topology | `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` | The four green vertices form a full-screen quad. | [constructor](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L57-L62) |
| Render dimensions | 128x128 | Fixed framebuffer size from the shared base class. | [DynamicStateBaseClass](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L88-L92) |

## Behavior Parameters

The primary behavioral axis is the shader type, which selects between the vertex-shader and mesh-shader pipelines. Both leaves exercise the same dynamic-blend-constants property; the axis exists to confirm the property holds under both pipeline shapes.

### `blend_constants`: dynamic blend constants, vertex-shader pipeline

The leaf builds a vertex+fragment pipeline and records the blend constants via [`setDynamicBlendState(0.33f, 0.1f, 0.66f, 0.5f)`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L132) before drawing the full-screen quad with a standard vertex-buffer draw. The rendered color attachment must match the reference frame derived from the blend formula with those constants.

### `blend_constants_mesh`: dynamic blend constants, mesh-shader pipeline

The mesh-shader variant replaces the vertex shader with a taskless mesh shader and the vertex draw with [`vkCmdDrawMeshTasksEXT`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L143). The blend pipeline setup, dynamic constants, and reference comparison are identical to the vertex-shader leaf. The leaf requires `VK_EXT_mesh_shader` and is excluded on Vulkan SC builds ([checkMeshShaderSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L202-L205)).

## Shader Analysis

The shaders support the test rather than implement the tested property. The vertex shader (`VertexFetch.vert`) passes position and color through; the fragment shader (`VertexFetch.frag`) outputs the interpolated color. The mesh shader (`VertexFetch.mesh`) emits the same full-screen quad primitives the vertex path would have produced. The tested behavior is whether the fixed-function blend unit applied the dynamic constants, which is a host-side readback question, not a shader question.

No representative shader walkthrough is included. The shaders only feed a known source color into the blend unit, and the property under test is decided by the blend stage and the host-side comparison.

## Runtime Execution and Result Checking

- Both leaves check only pipeline construction requirements. The mesh-shader leaf additionally requires `VK_EXT_mesh_shader` through [`checkMeshShaderSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L202-L205).
- The constructor fills the vertex buffer with four green `PositionColorVertex` entries forming a triangle strip covering the full 128x128 framebuffer ([constructor](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L57-L64)).
- [`initPipeline()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L67-L115) configures the color-blend attachment with blending enabled. The RGB channels use `VK_BLEND_FACTOR_SRC_ALPHA` as the source factor and `VK_BLEND_FACTOR_CONSTANT_COLOR` as the destination factor; the alpha channel uses `VK_BLEND_FACTOR_SRC_ALPHA` as the source factor and `VK_BLEND_FACTOR_CONSTANT_ALPHA` as the destination factor; both operations are `VK_BLEND_OP_ADD` ([attachmentState](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L78-L80)).
- [`iterate()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L117-L198) clears the color target to white `(1, 1, 1, 1)`, binds the pipeline, records the dynamic viewport, rasterization, depth/stencil, and blend states (the blend constants set to `(0.33f, 0.1f, 0.66f, 0.5f)`), and submits the draw. The mesh path binds the descriptor set, pushes a vertex offset, and calls `vkCmdDrawMeshTasksEXT`; the vertex path binds the vertex buffer and calls `vkCmdDraw`.
- Validation builds a software reference frame. The full-screen quad region is filled with the expected blended color `(0.33, 1.0, 0.66, 1.0)`, derived from the blend formula with a green source, white destination, and the dynamic constants. The rendered color attachment is read back and compared against the reference with [`tcu::fuzzyCompare()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L190-L191) at threshold `0.05f`. A match passes; otherwise the case fails with "Image verification failed".

### Blended color derivation

The blend unit evaluates, per channel, `result = source * srcFactor + destination * dstFactor`, then clamps to `[0, 1]`:

| Channel | Formula | Unclamped value | Clamped value |
|---------|---------|-----------------|---------------|
| R | `0 * 1 + 1 * 0.33` | 0.33 | 0.33 |
| G | `1 * 1 + 1 * 0.10` | 1.10 | 1.0 |
| B | `0 * 1 + 1 * 0.66` | 0.66 | 0.66 |
| A | `1 * 1 + 1 * 0.50` | 1.50 | 1.0 |

The green channel exceeds 1.0 and the alpha channel exceeds 1.0, so both clamp. The reference frame uses `(0.33, 1.0, 0.66, 1.0)`, matching the clamped result.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `blend_constants` | The implementation ignored or mishandled the dynamic blend constants in the vertex-shader pipeline, or the blend unit did not apply the configured constant-dependent factors. |
| `blend_constants_mesh` | The same dynamic-blend-constants defect surfaced through the mesh-shader pipeline, or the mesh-shader path diverged from the vertex path in a way that changed the source color feeding the blend unit. |
| Both leaves | Shared infrastructure: the clear color, vertex data, pipeline blend setup, or reference frame was wrong, or the blend constants were not set before the draw. |

### Cause Analysis

#### Dynamic blend constants not applied

**Possible failure symptoms:** The rendered image differs from the reference frame beyond the `0.05f` fuzzy threshold, so `tcu::fuzzyCompare()` reports a mismatch.

**Possible implementation causes:** The implementation may have ignored the constants set through `vkCmdSetBlendConstants`, used stale or zeroed constants, or failed to wire the `CONSTANT_COLOR` and `CONSTANT_ALPHA` factors to the dynamic constant values. The Vulkan specification requires that the blend constants set by the command be the values used by those factors, so using any other value is a specification violation. Whether the defect is in the dynamic-state tracking, the blend factor evaluation, or the command-buffer recording path requires source-level investigation of the failing implementation.

#### Mesh path diverges from vertex path

**Possible failure symptoms:** Only `blend_constants_mesh` fails while `blend_constants` passes, indicating the mesh-shader pipeline produced a different source color or geometry than the vertex-shader pipeline.

**Possible implementation causes:** The mesh shader may have emitted vertices with different positions or colors, or the mesh draw may not have covered the full framebuffer, leaving some pixels at the clear color. The vertex path and mesh path share the same blend setup and constants, so an isolated mesh failure points at the mesh-shader geometry or per-vertex data rather than the blend constants themselves. Source-level inspection of the mesh shader output is needed to confirm.

#### Shared setup defect

**Possible failure symptoms:** Both leaves fail identically, or the failure pattern is independent of the dynamic constants.

**Possible implementation causes:** The clear color was not white, the vertex data was not green, the blend attachment was misconfigured, or the reference frame did not match the configured blend formula. Because both leaves share the same instance class and base harness, a failure that is constant across the axis points at the shared setup rather than the mesh-versus-vertex difference.

## Case Pruning

### Requirement-based pruning

- `blend_constants` checks only pipeline construction requirements; no additional device features or extensions are required.
- `blend_constants_mesh` additionally requires `VK_EXT_mesh_shader` and is compiled out entirely on Vulkan SC builds through the `CTS_USES_VULKANSC` guard ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L236-L244)).

### Design-based pruning

- The file tests exactly one blend configuration with one set of constants. It does not enumerate other blend factors, blend operations, or constant values; those belong to dedicated blend tests outside this category.
- The shader-type axis is limited to the vertex and mesh pipelines. There is no tessellation, geometry, or compute variant in this file.

## Key Takeaways

- The tested property is that `vkCmdSetBlendConstants` supplies the values used by the `CONSTANT_COLOR` and `CONSTANT_ALPHA` blend factors. A passing result means the rendered image matched the reference frame computed from the blend formula with the dynamic constants.
- Both the green and alpha channels clamp above 1.0, so the reference frame uses the clamped color `(0.33, 1.0, 0.66, 1.0)` rather than the raw formula output.
- The vertex and mesh leaves exist for pipeline parity; a leaf-isolated failure suggests a mesh-path divergence, while a shared failure suggests a dynamic-blend-constants or shared-setup defect.
- Validation uses fuzzy image comparison at threshold `0.05f`, not exact pixel equality, so minor implementation-dependent rasterization differences within that tolerance still pass.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration | [`DynamicStateCBTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L222-L245) | Registers the `blend_constants` and `blend_constants_mesh` leaves. |
| Test instance | [`BlendConstantsTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L49-L199) | Geometry, pipeline blend setup, dynamic-state recording, draw, and reference comparison. |
| Blend setup | [attachmentState](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L78-L80) | The `SRC_ALPHA` / `CONSTANT_COLOR` / `CONSTANT_ALPHA` factor configuration that the test exercises. |
| Dynamic constants | [`setDynamicBlendState()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L132) | Records `vkCmdSetBlendConstants` with `(0.33, 0.1, 0.66, 0.5)`. |
| Mesh-shader support | [`checkMeshShaderSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateCBTests.cpp#L202-L205) | Requires `VK_EXT_mesh_shader` for the mesh leaf. |
| Shared base | [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) | Resource setup, render pass, dynamic-state helpers, and submit flow shared by both leaves. |
