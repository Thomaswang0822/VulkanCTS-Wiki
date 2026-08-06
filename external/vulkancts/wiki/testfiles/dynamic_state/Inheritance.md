## Overview

**Core question:** When a secondary command buffer enables viewport/scissor inheritance, does it correctly receive viewport and scissor state from the primary command buffer, an earlier secondary command buffer, or a nested secondary command buffer, instead of using its own static or stale state?

- [vktDynamicStateInheritanceTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1) implements the `inheritance` test family of the `dynamic_state` test category.
- The file tests the `VK_NV_inherited_viewport_scissor` extension. A geometry-shader pipeline draws colored rectangles through several command-buffer arrangements, selecting per-rectangle viewports and scissors. Each case asks whether the inherited viewport/scissor state is the one the test intended, not the one the secondary buffer was originally built with.
- The `primary_with_count`, `secondary_with_count`, and `nested_with_count` cases exercise the same inheritance with the `VK_EXT_extended_dynamic_state` viewport/scissor-with-count commands. The `nested` and `nested_with_count` cases also require `VK_EXT_nested_command_buffer`.
- The host produces an independent CPU reference image and compares it against the device result with exact per-pixel equality.

## Background Knowledge

- **Primary and secondary command buffers.** A primary command buffer can be submitted directly to a queue. A secondary command buffer cannot be submitted directly; it is recorded once and executed inside a primary command buffer through `vkCmdExecuteCommands`. Secondary buffers are often used to record reusable drawing work.
- **Inherited viewport/scissor state.** Normally a secondary command buffer recorded with `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` must set its own dynamic viewport and scissor state before drawing. `VK_NV_inherited_viewport_scissor` adds a struct, `VkCommandBufferInheritanceViewportScissorInfoNV`, that lets a secondary buffer inherit viewport/scissor state from the primary buffer that executes it, or from an earlier secondary buffer executed before it in the same primary buffer.
- **Viewport transform and depth.** A viewport maps normalized device coordinates to window coordinates, including a depth range remap. Because this test enables depth testing, an incorrect viewport (especially its `minDepth`/`maxDepth`) changes the depth values written, which changes which fragments pass the depth test and which color reaches the framebuffer.

## Registration Hierarchy

```text
dynamic_state.monolithic.inheritance
├── baseline
├── primary (non-VulkanSC only)
├── secondary (non-VulkanSC only)
├── nested (non-VulkanSC only)
├── split (non-VulkanSC only)
├── primary_with_count (non-VulkanSC only)
├── secondary_with_count (non-VulkanSC only)
└── nested_with_count (non-VulkanSC only)
```

The test family is registered once per pipeline construction type by the category dispatcher. `baseline` is available on Vulkan SC builds; every other leaf is conditionally compiled out under `CTS_USES_VULKANSC` ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1207-L1230)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Inheritance mode | 8 values from the [`InheritanceMode`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L84-L99) enum | The primary behavioral axis: selects where viewport/scissor state comes from and whether count is dynamic. | [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1207-L1230) |
| Test geometry | 8 configurations from [`makeGeometry()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1023-L1084) | Varies viewport count (2 or 3), scissor rectangles, viewport dimensions, and depth ranges so that a wrong viewport or scissor produces a visibly different image. | [makeGeometry](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1023-L1084) |
| Pipeline construction type | Passed from the parent group | Selects monolithic, pipeline-library, or shader-object construction. Shader-object construction uses `vkCmdSetViewportWithCount`/`vkCmdSetScissorWithCount` in place of the fixed-count commands. | [startRenderCmds](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L549-L874) |
| Framebuffer dimensions | 256x128 (`kWidth`, `kHeight`) | A power of two to avoid rounding error in the CPU reference. | [constants](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L52-L54) |
| Color format | `VK_FORMAT_B8G8R8A8_UNORM` | Universally supported framebuffer format. | [kFormat](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L59) |

The leaf runs all 8 geometry configurations in a single test case. A `failBits` bitmask records which configurations failed, so a partial mismatch names the failing indices in the failure message.

## Behavior Parameters

The primary behavioral axis is the inheritance mode. Each value changes where the secondary command buffer's viewport/scissor state is expected to come from, and therefore changes what a correct implementation must do.

### `baseline`: inheritance disabled

The `VK_NV_inherited_viewport_scissor` struct is not attached. The secondary command buffer sets its own viewport/scissor state directly with the non-dynamic-count commands. This case is the control: it verifies the rest of the pipeline, geometry, and reference rasterizer agree before any inheritance is introduced ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1210)).

### `primary`: inherit from the primary command buffer

The secondary buffer attaches the `VkCommandBufferInheritanceViewportScissorInfoNV` struct. The viewport/scissor state is set in the primary command buffer before `vkCmdExecuteCommands`. The drawing secondary buffer records no viewport/scissor state of its own; it must use the inherited values ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1213)).

### `secondary`: inherit from an earlier secondary command buffer

Two secondary buffers are executed in sequence inside the primary buffer. The first sets the viewport/scissor state; the drawing buffer inherits that state through the extension struct. This tests inheritance across a secondary-to-secondary boundary ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1215)).

### `nested`: inherit from a nested secondary command buffer

The setting and drawing secondary buffers are themselves executed from a third secondary buffer through `vkCmdExecuteCommands`, and that outer buffer is executed by the primary. Requires `VK_EXT_nested_command_buffer` with the `nestedCommandBuffer` and `nestedCommandBufferRendering` features ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1217)).

### `split`: inherit part from primary, part from secondary

The viewport/scissor array is divided. The first viewport/scissor is set in an early secondary buffer; the remaining viewports/scissors are set in the primary buffer. The drawing buffer inherits the combined state. This tests that the extension correctly merges state from two different sources ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1219)).

### `primary_with_count`: inherit from primary, dynamic count

Same as `primary`, but the viewport/scissor count is dynamic. The state is set with `vkCmdSetViewportWithCount`/`vkCmdSetScissorWithCount` from `VK_EXT_extended_dynamic_state`, and the pipeline is built with a dynamic viewport/scissor count. Requires `VK_EXT_extended_dynamic_state` ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1221)).

### `secondary_with_count`: inherit from earlier secondary, dynamic count

Same as `secondary`, but using the with-count commands. Requires `VK_EXT_extended_dynamic_state` ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1224)).

### `nested_with_count`: inherit from nested secondary, dynamic count

Same as `nested`, but using the with-count commands. `checkSupport()` gates it on `VK_EXT_nested_command_buffer`; it also uses `VK_EXT_extended_dynamic_state` viewport/scissor-with-count commands ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1160-L1183), [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1227)).

## Shader Analysis

The shaders support the test rather than implement the tested property. The vertex shader passes rectangle parameters through; the geometry shader expands each point into a triangle-strip rectangle and selects the viewport index through `gl_ViewportIndex`; the fragment shader writes the passed-through color ([shaders](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L196-L267)).

No representative shader walkthrough is included. Reconstructing the shader would explain rectangle expansion, but it would not explain why inherited viewport/scissor state should differ from locally recorded state. The useful shader fact is that `gl_ViewportIndex` selects which inherited viewport and scissor applies to each rectangle.

## Runtime Execution and Result Checking

- `checkSupport()` requires `VK_NV_inherited_viewport_scissor` for all leaves, `VK_EXT_extended_dynamic_state` for `primary_with_count` and `secondary_with_count`, and `VK_EXT_nested_command_buffer` plus its `nestedCommandBuffer` and `nestedCommandBufferRendering` features for the nested leaves. It also checks pipeline construction requirements ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1160-L1183)).
- The constructor creates a color image, a depth image (format chosen at runtime from a list of supported depth attachment formats), and matching views, then builds a render pass and framebuffer. The pipeline array is indexed by static viewport/scissor count, with index 0 reserved for the dynamic-count case ([constructor setup](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L183-L538)).
- For every geometry configuration, `startRenderCmds()` records the state-setting secondary buffer, the drawing secondary buffer, and the primary buffer. The drawing buffer attaches the `VkCommandBufferInheritanceViewportScissorInfoNV` struct when inheritance is enabled. For `primary` and `primary_with_count`, the primary records the correct viewport/scissor state that the drawing secondary must inherit. For every other mode, the primary deliberately records **bogus** viewport/scissor state so that a passing result proves the correct state came from inheritance (or, for `baseline`, from the secondary's own direct setting) rather than coincidentally matching ([startRenderCmds](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L549-L937)).
- `rasterizeExpectedResults()` runs an independent software rasterizer on the host: it applies viewport transform, scissor clamping, a depth test (`VK_COMPARE_OP_LESS`), and color assignment for each rectangle, producing the expected image ([rasterizeExpectedResults](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L938-L1021)).
- The pass/fail check compares the device image to the CPU reference pixel by pixel. The R, G, and B channels must match exactly; alpha is unused. The power-of-two framebuffer and separated depth values mean fuzzy matching is unnecessary ([comparison](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1110-L1119)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `baseline` | The pipeline, geometry, or CPU reference is wrong, or non-inherited viewport/scissor state is not applied. A `baseline` failure undermines the other modes because it shares the same harness. |
| `primary` | Viewport/scissor state set in the primary command buffer is not inherited by the secondary buffer that attached the inheritance struct. |
| `secondary` | Viewport/scissor state set in an earlier secondary buffer is not inherited by a later secondary buffer. |
| `nested` | Inheritance does not cross a secondary-to-secondary boundary inside a nested secondary buffer, or nested command buffer execution is mishandled. |
| `split` | The implementation fails to merge viewport/scissor state from two sources into one coherent array. |
| `primary_with_count`, `secondary_with_count`, or `nested_with_count` | The with-count variant of inheritance is not applied, or the dynamic-count pipeline does not consume inherited state correctly. |
| All modes | Shared infrastructure: the depth format search picked an unsupported format, or the geometry-shader viewport selection is wrong. (For the six modes that inject bogus viewport/scissor state, a failure to override that bogus state is an additional shared cause.) |

### Cause Analysis

#### Inherited state not applied or overridden by bogus state

**Possible failure symptoms:** The device image differs from the CPU reference in regions that depend on a viewport's position, size, depth range, or scissor rectangle.

**Possible implementation causes:** The implementation may ignore the `VkCommandBufferInheritanceViewportScissorInfoNV` struct, apply stale state left over in the secondary buffer, or fail to override the deliberately bogus viewport/scissor state the primary buffer records. Because the test injects bogus state and then expects inheritance to replace it, a match between the device image and the bogus-state image points directly at missed inheritance. Whether the defect lives in the driver's command-buffer recording or in the hardware viewport/scissor unit cannot be determined from the image alone; source-level investigation against the `VK_NV_inherited_viewport_scissor` specification is needed.

#### Wrong depth values from an incorrect viewport

**Possible failure symptoms:** The color pattern is right in position but wrong in which rectangle is visible, because depth ordering changed.

**Possible implementation causes:** A viewport with the wrong `minDepth`/`maxDepth` remaps depth incorrectly. Fragments that should fail the depth test then pass, or vice versa, so a different rectangle wins the overlapping pixels. The CPU reference applies the intended depth range; a mismatch isolates the failure to the depth component of the inherited viewport.

#### Dynamic-count pipeline does not consume inherited state

**Possible failure symptoms:** Only the with-count leaves fail while their fixed-count counterparts pass.

**Possible implementation causes:** The dynamic-count pipeline (static viewport count 0) may not be wired to receive inherited viewport/scissor state, or the with-count set commands may not populate the inherited state array. Comparing a with-count leaf against its fixed-count sibling narrows the failure to the count-handling path.

## Case Pruning

### Requirement-based pruning

- All leaves require `VK_NV_inherited_viewport_scissor`.
- The with-count leaves that set state through the `VK_EXT_extended_dynamic_state` commands (`primary_with_count` and `secondary_with_count`) require that extension; `nested_with_count` relies on the same commands but `checkSupport()` gates it only on `VK_EXT_nested_command_buffer` ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1160-L1183)).
- The nested leaves require `VK_EXT_nested_command_buffer` with the `nestedCommandBuffer` and `nestedCommandBufferRendering` features enabled.
- The depth attachment format is selected at runtime from `VK_FORMAT_X8_D24_UNORM_PACK32`, `VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT`, and `VK_FORMAT_D32_SFLOAT_S8_UINT`; if none is supported the test cannot run ([depth format search](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L374-L406)).
- The geometry shader writes `gl_ViewportIndex`, which implicitly requires the `multiViewport` feature.

### Design-based pruning

- Only `baseline` is registered on Vulkan SC builds. All inheritance modes are conditionally compiled out under `CTS_USES_VULKANSC` because the relevant extensions and nested command buffer support are not part of Vulkan SC.
- The eight geometry configurations are fixed across all leaves rather than parameterized, so they are not exposed as separate test cases.

## Key Takeaways

- The inheritance mode is the behavioral axis. The with-count variants test the same property through `VK_EXT_extended_dynamic_state`, and the nested variants test it through `VK_EXT_nested_command_buffer`.
- Deliberately recording bogus viewport/scissor state in the primary buffer makes the test meaningful: a passing result proves inheritance replaced the bogus state, rather than that the buffers happened to agree.
- The depth test makes viewport depth-range errors observable. An inherited viewport with the wrong `minDepth`/`maxDepth` changes which rectangle wins overlapping pixels, so a depth-ordering mismatch is a viewport-inheritance symptom.
- An exact CPU reference comparison, rather than fuzzy matching, is valid here because the framebuffer is a power of two and the depth values are separated.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration | [`DynamicStateInheritanceTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1207-L1230) | Registers the eight inheritance-mode leaves and the Vulkan SC guard. |
| Support checks | [`InheritanceTestCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1160-L1183) | Extension and feature requirements per mode. |
| Command recording | [`InheritanceTestInstance::startRenderCmds()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L549-L937) | Records the state-setting, drawing, nested, and primary buffers, including bogus-state injection. |
| CPU reference | [`rasterizeExpectedResults()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L938-L1021) | Independent software rasterizer used for comparison. |
| Geometry generation | [`makeGeometry()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1023-L1084) | The eight fixed geometry configurations. |
| Comparison and fail tracking | [`iterate()`](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L1086-L1142) | Exact per-pixel check and per-geometry `failBits`. |
| Shaders | [vert/geom/frag](../../../modules/vulkan/dynamic_state/vktDynamicStateInheritanceTests.cpp#L196-L267) | Pass-through vertex, rectangle-expanding geometry shader with `gl_ViewportIndex`, pass-through fragment. |
