## Overview

The `dynamic_state` test category collects tests that check Vulkan's dynamic state mechanism, which allows certain pipeline state to be set dynamically at command buffer recording time rather than being baked into the pipeline object.

## Background Knowledge

- **Dynamic state.** Vulkan lets the application set certain pipeline state dynamically via `vkCmdSet*` commands recorded into the command buffer, instead of fixing it at pipeline creation time. A pipeline created with a dynamic state enabled does not use the corresponding static value from `VkGraphicsPipelineCreateInfo`; instead, the most recent dynamic command recorded before a draw supplies the value. This category verifies that dynamic state commands correctly override static pipeline state, that state persists across pipeline binds, and that dynamic state does not interfere with compute or transfer operations.
- **Pipeline construction type subgroups.** The dispatcher `createTests()` in [`vktDynamicStateTests.cpp`](../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L108) creates seven pipeline-construction-type subgroups: `monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_unlinked_spirv`, `shader_object_unlinked_binary`, `shader_object_linked_spirv`, and `shader_object_linked_binary`. Each subgroup attaches the same set of implementation files as direct children through `createChildren()`, so the same test families appear under each construction type. The `compute_transfer` family is an exception: it is registered only under `monolithic` and `shader_object_unlinked_spirv`.
- **Shared `DynamicStateBaseClass` harness.** Every implementation file in this category inherits from `DynamicStateBaseClass`, which provides the common resource setup, render-pass recording, software reference rasterization, and image comparison logic. Each test family overrides `setDynamicStates()` to issue the specific `vkCmdSet*` commands it tests, and overrides the reference rendering to apply the same state. `vktDynamicStateTestCaseUtil.hpp` provides the `InstanceFactory` template that instantiates the correct test instance per pipeline construction type.

## Category Structure

```text
dynamic_state
├── monolithic
├── pipeline_library
├── fast_linked_library
├── shader_object_unlinked_spirv
├── shader_object_unlinked_binary
├── shader_object_linked_spirv
└── shader_object_linked_binary
```

Each construction-type subgroup holds the same ten direct test families: `vp_state`, `rs_state`, `cb_state`, `ds_state`, `general_state`, `inheritance`, `image`, `discard`, `line_width`, and `compute_transfer`. The `compute_transfer` family appears only under `monolithic` and `shader_object_unlinked_spirv`; it is absent from the other five construction types because the dispatcher conditionally attaches it ([dispatcher guard](../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L63-L66)). The `image` family name refers to image-manipulation commands (clear, blit, copy, resolve), not image-related dynamic state. The registration-only dispatcher `vktDynamicStateTests.cpp` has no Level-3 page; its facts are folded into this Level-2 page.

## How the Families Fit Together

The families share one theme: each verifies that a specific set of dynamic state commands produces correct rendering or does not corrupt other state. They differ in which dynamic states they target.

- **Viewport and rasterization** families (`vp_state`, `rs_state`) test geometric dynamic state: viewport/scissor transforms and depth bias or line width. The test compares rendered geometry against a software reference that applies the same dynamic values.
- **Color and depth/stencil** families (`cb_state`, `ds_state`) test per-fragment dynamic state: blend constants and stencil parameters or depth bounds. The test checks that the dynamic values override the static pipeline configuration.
- **General state** (`general_state`) tests state switching, reordering, persistence across pipeline binds, and the static-mask-zero edge case, catching interaction bugs that single-state families would miss.
- **Inheritance** (`inheritance`) tests whether secondary command buffers correctly inherit viewport/scissor state from the primary under `VK_NV_inherited_viewport_scissor`, including nested command buffer variants.
- **Side-effect isolation** families (`image`, `compute_transfer`) verify that image-manipulation or compute/transfer commands recorded between dynamic state setup and a draw do not corrupt the dynamic state.
- **Edge-case families** (`discard`, `line_width`) cover discard-rectangle extension behavior and line-width dynamic state.

## Level-3 Pages Navigation

| Registered test family | Level-3 page | What to read there |
|------------------------|--------------|--------------------|
| `vp_state` | [VP](../testfiles/dynamic_state/VP.md) | Dynamic viewport/scissor with multi-viewport routing |
| `rs_state` | [RS](../testfiles/dynamic_state/RS.md) | Dynamic depth bias and line width |
| `cb_state` | [CB](../testfiles/dynamic_state/CB.md) | Dynamic blend constants |
| `ds_state` | [DS](../testfiles/dynamic_state/DS.md) | Dynamic depth bounds, stencil compare/write mask, stencil reference |
| `general_state` | [General](../testfiles/dynamic_state/General.md) | State switching, reordering, persistence, static-mask-zero, double static bind |
| `inheritance` | [Inheritance](../testfiles/dynamic_state/Inheritance.md) | `VK_NV_inherited_viewport_scissor` secondary command buffer inheritance |
| `image` | [Clear](../testfiles/dynamic_state/Clear.md) | Image-manipulation commands do not corrupt dynamic blend constants |
| `discard` | [Discard](../testfiles/dynamic_state/Discard.md) | GLSL `discard` interaction with dynamic state |
| `line_width` | [LineWidth](../testfiles/dynamic_state/LineWidth.md) | Dynamic line width with draw-order interaction |
| `compute_transfer` | [Compute](../testfiles/dynamic_state/Compute.md) | Compute/transfer commands do not corrupt dynamic state |

## Category Notes

- The `compute_transfer` family is registered only under `monolithic` and `shader_object_unlinked_spirv`; it is absent from the other five construction types ([dispatcher guard](../../modules/vulkan/dynamic_state/vktDynamicStateTests.cpp#L63-L66)).
- The `general_state` family omits the `double_static_bind` group for shader-object construction types.
- Mesh-shader variants (`_mesh` suffix) are registered for several families but are excluded from VulkanSC builds under `CTS_USES_VULKANSC` guards.
- The `vktDynamicStateBaseClass.cpp`/`.hpp` shared base and `vktDynamicStateTestCaseUtil.hpp` instance-factory template have no Level-3 pages; Level-3 pages reference them as supporting evidence.
