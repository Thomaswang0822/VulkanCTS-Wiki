## Overview

**Core question:** Do dynamically set depth bounds and stencil parameters (compare mask, write mask, reference) take effect and override static pipeline state, for both classic vertex pipelines and mesh shader pipelines?

- [vktDynamicStateDSTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1) implements the `ds_state` test family of the `dynamic_state` test category.
- It registers five behavior groups under the `ds_state` test family: `depth_bounds_1`, `depth_bounds_2`, `stencil_params_basic_1`, `stencil_params_basic_2`, and `stencil_params_advanced`. Each group has a `_mesh` sibling on non-VulkanSC builds that reruns the same logic through a mesh shader pipeline.
- The tests drive `vkCmdSetDepthBounds`, `vkCmdSetStencilCompareMask`, `vkCmdSetStencilWriteMask`, and `vkCmdSetStencilReference` through the shared [`DepthStencilBaseCase`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L62) harness (and [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) for `depth_bounds_2`).
- Each case draws simple geometry, builds a software reference frame that encodes the expected depth-bounds or stencil outcome, and compares the rendered color attachment with a fuzzy image threshold.
- The page explains what each behavior group verifies, how runtime execution and result checking work, and what a failure points to.

## Background Knowledge

- **Dynamic depth bounds test.** The depth bounds test discards fragments whose post-polygon-expansion depth value falls outside a `[min, max]` range. When the bounds test is enabled in the pipeline but the bounds themselves are dynamic, the command-buffer value set by `vkCmdSetDepthBounds` overrides whatever range the pipeline was created with. The test relies on the `DEVICE_CORE_FEATURE_DEPTH_BOUNDS` feature.
- **Dynamic stencil parameters.** Stencil testing compares the stencil reference value against the existing stencil buffer value, masked by a compare mask, and writes are controlled by a write mask. With `VK_DYNAMIC_STATE_STENCIL_COMPARE_MASK`, `VK_DYNAMIC_STATE_STENCIL_WRITE_MASK`, and `VK_DYNAMIC_STATE_STENCIL_REFERENCE` set dynamic, the command-buffer values govern these per-draw rather than the static pipeline state.
- **Pipeline construction type subgroup.** Every behavior group below is registered as a direct child of one of the construction-type subgroups (`monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_unlinked_spirv`, `shader_object_unlinked_binary`, `shader_object_linked_spirv`, `shader_object_linked_binary`) created by the registration-only dispatcher. The construction type is passed in from the parent and is not a behavioral axis of this page.

## Registration Hierarchy

```text
dynamic_state.monolithic.ds_state
├── depth_bounds_1
├── depth_bounds_2
├── stencil_params_basic_1
├── stencil_params_basic_2
└── stencil_params_advanced
```

Each leaf above also has a `_mesh` sibling on non-VulkanSC builds, registered in the same `init()` loop. The mesh variants are siblings of their classic counterparts, not nested under them. The same `ds_state` subtree appears under every construction-type subgroup. The registration root shown here is the full category-qualified path for the `monolithic` subgroup; replace `monolithic` with the other subgroup names for the parallel subtrees.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader type | classic vertex, mesh | Runs the same depth/stencil logic through a vertex+fragment pipeline and a mesh+fragment pipeline. The mesh variant requires `VK_EXT_mesh_shader` and is excluded on VulkanSC. | [init() loop](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1281) |
| Depth bounds range | `[0.5f, 0.75f]` (parametric), `[0.3f, 0.9f]` (pre-filled) | The dynamic range passed to `vkCmdSetDepthBounds`. The parametric case draws geometry at known depths; the pre-filled case loads varying depth values into the depth buffer first. | [DepthBoundsParamTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L549), [DepthBoundsTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L830) |
| Stencil write mask | `0x0D`, `0x06`, `0x0E` | Controls which stencil bits the first draw of a stencil case writes. The basic cases use `0x0D` and `0x06`; the advanced case uses `0x0E`. | [init() registrations](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1310-L1319) |
| Stencil compare mask | `0x06`, `0x02`, `0xFF` | Masks the reference-versus-buffer comparison on the second draw. | [init() registrations](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1310-L1319) |
| Stencil reference | `0x05`, `0x0E`, `0x0F` | The reference value compared against the masked stencil buffer on the second draw. | [init() registrations](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1310-L1319) |
| Depth/stencil attachment format | `VK_FORMAT_D24_UNORM_S8_UINT` or `VK_FORMAT_D32_SFLOAT_S8_UINT` | Selected at runtime based on format support for the cases using `DepthStencilBaseCase`. | [format selection](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L139-L157) |
| Pre-filled depth format (`depth_bounds_2`) | `VK_FORMAT_D16_UNORM` | Separate depth-only image used by `DepthBoundsTestInstance` for the pre-filled depth gradient. | [DepthBoundsTestInstance ctor](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L662) |
| Render dimensions | 128x128 | Fixed framebuffer size for all cases. | [WIDTH/HEIGHT](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L89-L92) |

## Behavior Parameters

The primary behavioral axis is the behavior group: each group of test case leaves tests a distinct dynamic-state property. The mesh variants repeat the same logic through a different pipeline and do not form a separate axis.

### depth_bounds_1: Depth bounds (parametric)

Draws three quads at known depths through two pipelines. Pipeline 1 (depth test `ALWAYS`, depth write enabled, bounds test disabled) draws two green quads: the left half at depth `0.375f` and the right half at depth `0.625f`, writing those values into the depth buffer. Pipeline 2 (bounds test enabled, depth test disabled) then draws a blue full-screen quad at depth `1.0f`. With `vkCmdSetDepthBounds(0.5f, 0.75f)` set on the command buffer, the blue quad's bounds test reads the depth buffer: on the left half the stored depth `0.375f` is below `0.5f` so blue fails and green remains; on the right half the stored depth `0.625f` is inside the range so blue passes and overwrites green. The reference frame expects green on the left half and blue on the right half. See [`DepthBoundsParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L504).

### depth_bounds_2: Depth bounds (pre-filled)

Pre-fills a `VK_FORMAT_D16_UNORM` depth buffer with a computed depth gradient using `vkCmdCopyBufferToImage`, then draws a single full-screen green quad with depth bounds enabled and `vkCmdSetDepthBounds(0.3f, 0.9f)`. Only pixels whose pre-filled depth falls inside the bounds range pass the bounds test and render green; the rest stay at the clear color (white). This case uses a separate `VK_FORMAT_D16_UNORM` depth image and the [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) base rather than `DepthStencilBaseCase`. See [`DepthBoundsTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L630).

### stencil_params_basic_1: Stencil parameters (basic, config 1)

Two draws with two pipelines. The first draw uses stencil op `REPLACE` with compare `ALWAYS`, dynamic write mask `0x0D`, and dynamic reference `0x0F`, writing `0x0F & 0x0D = 0x0D` into the stencil buffer over the green quad. The second draw uses compare `EQUAL` with dynamic compare mask `0x06` and dynamic reference `0x05`. The compare checks `(buffer & mask) == (ref & mask)`: `(0x0D & 0x06) = 0x04` equals `(0x05 & 0x06) = 0x04`, so the compare passes and the blue quad renders over the whole framebuffer. Registered only on non-VulkanSC builds.

### stencil_params_basic_2: Stencil parameters (basic, config 2)

Same two-draw structure as `stencil_params_basic_1`, but with write mask `0x06` and compare mask `0x02`. The first draw writes `0x0F & 0x06 = 0x06` into the stencil buffer. The second draw compares `(0x06 & 0x02) = 0x02` against `(0x05 & 0x02) = 0x00`; they are not equal, so the compare fails and the blue quad is discarded, leaving the first draw's green. Registered only on non-VulkanSC builds. The two basic configs together cover both a passing and a failing stencil compare outcome from the same two-draw pattern.

### stencil_params_advanced: Stencil parameters (advanced)

Two draws with two pipelines. The first draw (pipeline 1, compare `ALWAYS`) writes the green center rectangle (vertices spanning `-0.5..0.5`) with dynamic write mask `0x0E` and dynamic reference `0x0F`, storing `0x0F & 0x0E = 0x0E` in the stencil buffer inside the rectangle. The second draw (pipeline 2, compare `NOT_EQUAL`) draws the blue full-screen quad with dynamic reference `0x0E`. Inside the center rectangle the stencil buffer holds `0x0E`; `NOT_EQUAL` with reference `0x0E` fails there, so the blue quad is discarded and green remains. Outside the rectangle the stencil buffer is still `0`, so `NOT_EQUAL` passes and blue renders. This case is registered on all build targets, including VulkanSC.

## Shader Analysis

The shaders are not part of the tested behavior. All depth/stencil cases share the same `VertexFetch.vert` / `VertexFetch.frag` (classic) and `VertexFetch.mesh` (mesh) shaders, which only pass through position and color attributes. The depth bounds and stencil logic is entirely in fixed-function pipeline state and the dynamic `vkCmdSet*` calls. No shader walkthrough is included because the shader content does not vary across behavior groups and does not influence the pass/fail outcome.

## Runtime Execution and Result Checking

All cases follow the same host-side flow through the shared base harness:

- The host selects a depth/stencil attachment format at runtime, falling back from `VK_FORMAT_D24_UNORM_S8_UINT` to `VK_FORMAT_D32_SFLOAT_S8_UINT` based on `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` support. If neither is supported the case throws `NotSupportedError`.
- The host creates a color attachment (`VK_FORMAT_R8G8B8A8_UNORM`) and a depth/stencil image, builds one or two graphics pipelines with the relevant static depth/stencil state (bounds test enabled, or stencil test enabled with static op states), and marks the bounds, compare mask, write mask, and reference as dynamic.
- The `depth_bounds_2` case additionally creates a `VK_FORMAT_D16_UNORM` depth image, fills a staging buffer with a computed depth gradient, and copies it into the depth image before the render pass.
- Inside the render pass, the test records the dynamic state commands (`setDynamicDepthStencilState` for bounds, or the per-draw stencil parameter sets), binds pipelines, and issues the draws.
- After submission, the host reads back the color attachment and builds a software reference frame encoding the expected color pattern.
- Pass/fail is decided by [`tcu::fuzzyCompare()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L619) with threshold `0.05f` comparing the rendered frame against the reference.

| Resource | Created/configured by host | Bound to GPU | Device access | Host readback | Role |
|----------|-----------------------------|--------------|---------------|---------------|------|
| Color attachment image | Yes | Color attachment | Written by fragment output | Yes, via `readSurface` | Captures the rendered result for comparison. |
| Depth/stencil image | Yes | Depth/stencil attachment | Read/written by depth/stencil tests | No (inferred from color) | Holds depth and stencil values tested by fixed-function state. |
| Pre-filled depth image (`depth_bounds_2`) | Yes, via `cmdCopyBufferToImage` | Depth attachment | Read by depth bounds test | No | Provides known per-pixel depth values for the bounds range check. |
| Vertex buffer / mesh descriptor | Yes | Vertex buffer or storage buffer | Read by vertex or mesh shader | No | Provides geometry positions and colors. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `depth_bounds_1` / `depth_bounds_1_mesh` | Dynamic depth bounds not applied, or applied with the wrong range. |
| `depth_bounds_2` / `depth_bounds_2_mesh` | Dynamic depth bounds not applied against pre-filled depth values, or pre-fill not visible to the bounds test. |
| `stencil_params_basic_1` / `stencil_params_basic_2` (and mesh variants) | Dynamic stencil compare mask, write mask, or reference not applied correctly across the two draws. |
| `stencil_params_advanced` / `stencil_params_advanced_mesh` | Dynamic stencil state not changed correctly between two draws with `NOT_EQUAL`. |

### Cause Analysis

#### Dynamic depth bounds not applied, or applied with the wrong range

**Possible failure symptoms:** The fuzzy image comparison fails because the rendered color pattern does not match the reference. For `depth_bounds_1`, geometry that should pass the bounds test is discarded (wrong color in the in-bounds region) or out-of-bounds geometry passes (wrong color outside). For `depth_bounds_2`, the green region does not correspond to pixels whose pre-filled depth falls inside `[0.3f, 0.9f]`.

**Possible implementation causes:** The pipeline enables the depth bounds test but the implementation ignores or misapplies the range set by `vkCmdSetDepthBounds`. A mismatch between the static pipeline bounds (which are present but should be overridden) and the dynamic values would also produce this symptom. For `depth_bounds_1`, the depth compare op (`ALWAYS` on pipeline 1, `NEVER` on pipeline 2) and depth write interact with the bounds test, so a depth-write or depth-compare defect can mimic a bounds defect.

#### Dynamic depth bounds not applied against pre-filled depth values, or pre-fill not visible

**Possible failure symptoms:** Specific to `depth_bounds_2`: the rendered green region is wrong relative to the pre-filled depth gradient.

**Possible implementation causes:** The `cmdCopyBufferToImage` into the `VK_FORMAT_D16_UNORM` depth image, the subsequent layout transition to `VK_IMAGE_LAYOUT_DEPTH_STENCIL_READ_ONLY_OPTIMAL`, or the memory barrier between the transfer and the depth bounds test may not correctly publish the written depth values. Source-level investigation is needed to distinguish a depth-bounds logic bug from a pre-fill visibility bug.

#### Dynamic stencil compare mask, write mask, or reference not applied correctly across two draws

**Possible failure symptoms:** For `stencil_params_basic_1`, the framebuffer is not uniformly blue (the compare should pass everywhere). For `stencil_params_basic_2`, the framebuffer is not uniformly green (the compare should fail everywhere, leaving the first draw). A partial or inverted pattern indicates the dynamic mask or reference was not the value set on the command buffer.

**Possible implementation causes:** The implementation may apply the static pipeline stencil mask or reference instead of the dynamic one, or may not update the dynamic stencil state between the two draws within the same command buffer. Because the two basic configs are designed to produce opposite pass/fail outcomes from the same pattern, a failure on both configs points to a general dynamic stencil parameter bug, while a failure on only one points to mask-specific handling.

#### Dynamic stencil state not changed correctly between two draws with `NOT_EQUAL`

**Possible failure symptoms:** The center rectangle is not green or the outer region is not blue, meaning the `NOT_EQUAL` comparison used the wrong reference or write mask on the second draw.

**Possible implementation causes:** The dynamic write mask `0x0E` on the first draw or the dynamic reference `0x0E` on the second draw was not applied, so the stencil buffer contents at the second draw did not match what the `NOT_EQUAL` test expects.

## Case Pruning

### Requirement-based pruning

- `depth_bounds_1` and `depth_bounds_2` (classic and mesh) require the `DEVICE_CORE_FEATURE_DEPTH_BOUNDS` core feature, checked by [`checkDepthBoundsSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1246).
- All `_mesh` variants require `VK_EXT_mesh_shader`, checked by [`checkMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1045). On VulkanSC builds the mesh variants are compile-time excluded.
- `stencil_params_basic_1` and `stencil_params_basic_2` are registered only on non-VulkanSC builds (guarded by `#ifndef CTS_USES_VULKANSC` at [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1309-L1316)).
- Every case checks pipeline construction requirements through [`checkPipelineConstructionRequirements`](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1082) in the case-level support method.
- If no supported depth/stencil attachment format is found, the case throws `NotSupportedError`.

### Design-based pruning

- There is no generated matrix of stencil parameter values. The two basic configs are hand-chosen to produce one passing and one failing compare outcome from the same two-draw pattern.
- The advanced case uses a fixed pair of draws with `NOT_EQUAL`; no other compare ops are registered as separate leaves.

## Key Takeaways

- The `ds_state` test family verifies that dynamic depth bounds and stencil parameters override static pipeline state, using fuzzy image comparison against a software reference frame.
- `depth_bounds_1` draws geometry at known depths; `depth_bounds_2` pre-fills the depth buffer to test the bounds range against arbitrary per-pixel depth values.
- The two `stencil_params_basic` configs are deliberately paired: config 1 should pass the compare and config 2 should fail, covering both outcomes from the same mechanism.
- `stencil_params_advanced` verifies that dynamic stencil state can be changed between two draws in the same command buffer.
- See `## Failure Meaning` for what a failing result implies for each behavior group.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [vktDynamicStateDSTests.cpp#L1274-L1321](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1274-L1321) | Registers all behavior groups and their mesh variants in the `init()` loop. |
| Shared base harness | [DepthStencilBaseCase](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L62) | Provides resource setup, render pass, dynamic state helpers, and the `iterate()` override point. |
| DepthBoundsParamTestInstance | [vktDynamicStateDSTests.cpp#L504-L628](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L504-L628) | Implements `depth_bounds_1`. |
| DepthBoundsTestInstance | [vktDynamicStateDSTests.cpp#L630-L891](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L630-L891) | Implements `depth_bounds_2` with a pre-filled depth buffer. |
| StencilParamsBasicTestInstance | [vktDynamicStateDSTests.cpp#L893-L1039](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L893-L1039) | Implements `stencil_params_basic_1` and `stencil_params_basic_2`. |
| StencilParamsAdvancedTestInstance | [vktDynamicStateDSTests.cpp#L1109-L1244](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1109-L1244) | Implements `stencil_params_advanced`. |
| Support checks | [vktDynamicStateDSTests.cpp#L1246-L1257](../../../modules/vulkan/dynamic_state/vktDynamicStateDSTests.cpp#L1246-L1257) | Depth bounds and mesh shader feature checks. |
| Shared base class | [DynamicStateBaseClass](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) | Base class used by `DepthBoundsTestInstance` and the mesh descriptor path. |
| Test case utilities | [vktDynamicStateTestCaseUtil.hpp](../../../modules/vulkan/dynamic_state/vktDynamicStateTestCaseUtil.hpp#L1) | Instance factory and shader map helpers. |
