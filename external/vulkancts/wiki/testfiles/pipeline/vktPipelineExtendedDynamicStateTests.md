# vktPipelineExtendedDynamicStateTests.cpp

## Overview

[`vktPipelineExtendedDynamicStateTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L1) implements the [`extended_dynamic_state`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6978) topic group. It verifies VK_EXT_extended_dynamic_state and VK_EXT_extended_dynamic_state3 functionality, testing dynamically set pipeline state including cull mode, front face, rasterization, logic op, color blend, depth bounds, depth test, stencil test, vertex input, and many more dynamic state parameters.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineExtendedDynamicStateTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L1)
- Header: [`vktPipelineExtendedDynamicStateTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.extended_dynamic_state
├── cmd_buffer_start
├── before_draw
├── between_pipelines
├── after_pipelines
├── before_good_static
├── two_draws_dynamic
├── two_draws_static
├── three_draws_dynamic
├── mesh_shader
└── misc
```

Source: [`createExtendedDynamicStateTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6977). Variant coverage: Not extra shader-object. Skipped by extra shader-object variants.

## Test Families

### cmd_buffer_start — Dynamic state set at command buffer start

Tests where the dynamic state is set at the beginning of the command buffer, before any pipeline is bound. Each test case within this group exercises a specific EDS1 or EDS3 dynamic state parameter (cull mode, front face, rasterizer discard, logic op, color blend, depth bias, depth bounds, depth test, stencil test, vertex input, patch control points, etc.) with the state set via `vkCmdSet*` at command buffer start time.

### before_draw — Dynamic state set before draw call

Tests where the dynamic state is set just before the draw call. Same EDS1/EDS3 state coverage as `cmd_buffer_start`, but the `vkCmdSet*` calls are issued immediately before `vkCmdDraw`.

### between_pipelines — Dynamic state set between pipeline binds

Tests where the dynamic state is set after a pipeline with static states has been bound and before a pipeline with dynamic states has been bound. Skipped for shader object construction type.

### after_pipelines — Dynamic state set after pipeline binds

Tests where the dynamic state is set after both a static-state pipeline and a second dynamic-state pipeline have been bound. Skipped for shader object construction type.

### before_good_static — Dynamic state set before a good static pipeline

Tests where the dynamic state is set after a dynamic pipeline has been bound and before a second static-state pipeline with the correct values has been bound.

### two_draws_dynamic — Two draws with dynamic state

Binds a bad static pipeline and draws, followed by binding a correct dynamic pipeline and drawing again.

### two_draws_static — Two draws with static state

Binds a bad dynamic pipeline and draws, followed by binding a correct static pipeline and drawing again.

### three_draws_dynamic — Three draws with dynamic state

Extended sequence of three draws exercising dynamic state transitions.

### mesh_shader — Mesh shader dynamic state tests

Contains the same ordering subgroups (`cmd_buffer_start`, `before_draw`, etc.) but with mesh shaders instead of vertex shaders. Each test case exercises EDS1/EDS3 dynamic state parameters with mesh shader pipelines. Non-VulkanSC only.

### misc — Miscellaneous extended dynamic state tests

Implements edge-case and interaction tests for extended dynamic state that don't fit in the main ordering groups. Includes `sample_shading_dynamic_sample_count` and `dynamic_sample_shading_static_*_dynamic_*` test cases. Documented separately in [`vktPipelineExtendedDynamicStateMiscTests.md`](vktPipelineExtendedDynamicStateMiscTests.md).

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Non-extra-shader-object variant types |
| Dynamic state type | Enum | All EDS1 and EDS3 states |
| State ordering | Enum | Static-first, dynamic-first |
| VK_EXT_extended_dynamic_state | Extension | Required for EDS1 tests |
| VK_EXT_extended_dynamic_state3 | Extension | Required for EDS3 tests |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_extended_dynamic_state` | Required for EDS1 tests |
| `VK_EXT_extended_dynamic_state3` | Required for EDS3 tests |
| `VK_KHR_maintenance10` | Required for some maintenance10-related tests |
| Various feature gates | Per-test depending on state type |

## Verification Methods

- **Rendering comparison**: Set state dynamically, render, compare against expected output
- **State ordering test**: Verify that dynamic state overrides static state correctly
- **Feature gate check**: Verify that unsupported dynamic states are properly rejected

## Notes

- This is one of the largest test files in the pipeline category
- EDS3 tests are conditionally registered based on extension support
- The file uses a custom `TestGroupWithClean` class for resource cleanup
