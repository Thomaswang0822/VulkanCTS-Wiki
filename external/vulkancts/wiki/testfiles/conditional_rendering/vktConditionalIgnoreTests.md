# vktConditionalIgnoreTests.cpp

## Overview

This file registers the `conditional_ignore` group for commands that are expected to execute even while conditional rendering is active. It includes clear operations built from shared condition data plus general command, graphics-bind, and ray-tracing cases with normal and inverted condition variants.

## Role and Source

| Item | Evidence |
|---|---|
| Source file | [vktConditionalIgnoreTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp) |
| Registered group and children | [vktConditionalIgnoreTests.cpp registration](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L2310-L2436) |
| Shared condition-data table | [vktConditionalRenderingTestUtil.hpp](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) |
| Shared capability helper | [checkConditionalRenderingCapabilities()](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L58) |

## Registration Hierarchy

```text
conditional_rendering.conditional_ignore
├── bind_descriptor_sets
├── bind_descriptor_sets_inverted
├── bind_index_buffer
├── bind_index_buffer_inverted
├── bind_pipeline
├── bind_pipeline_inverted
├── bind_shaders
├── bind_shaders_inverted
├── bind_vertex_buffers
├── bind_vertex_buffers_inverted
├── blit_image
├── blit_image_inverted
├── clear_color_condition_host_memory_expect_execution
├── clear_color_condition_host_memory_expect_execution_inverted
├── clear_color_condition_host_memory_expect_noop
├── clear_color_condition_host_memory_expect_noop_inverted
├── clear_color_condition_host_memory_inherited_expect_execution
├── clear_color_condition_host_memory_inherited_expect_execution_inverted
├── clear_color_condition_host_memory_inherited_expect_noop
├── clear_color_condition_host_memory_inherited_expect_noop_inverted
├── clear_color_condition_host_memory_nested_buffer_expect_execution
├── clear_color_condition_host_memory_nested_buffer_expect_execution_inverted
├── clear_color_condition_host_memory_nested_buffer_expect_noop
├── clear_color_condition_host_memory_nested_buffer_expect_noop_inverted
├── clear_color_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── clear_color_condition_host_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── clear_color_condition_host_memory_nested_buffer_nested_inherited_expect_noop
├── clear_color_condition_host_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── clear_color_condition_host_memory_nested_inherited_expect_execution
├── clear_color_condition_host_memory_nested_inherited_expect_execution_inverted
├── clear_color_condition_host_memory_nested_inherited_expect_noop
├── clear_color_condition_host_memory_nested_inherited_expect_noop_inverted
├── clear_color_condition_host_memory_secondary_buffer_expect_execution
├── clear_color_condition_host_memory_secondary_buffer_expect_execution_inverted
├── clear_color_condition_host_memory_secondary_buffer_expect_noop
├── clear_color_condition_host_memory_secondary_buffer_expect_noop_inverted
├── clear_color_condition_host_memory_secondary_buffer_inherited_expect_execution
├── clear_color_condition_host_memory_secondary_buffer_inherited_expect_execution_inverted
├── clear_color_condition_host_memory_secondary_buffer_inherited_expect_noop
├── clear_color_condition_host_memory_secondary_buffer_inherited_expect_noop_inverted
├── clear_color_condition_local_memory_expect_execution
├── clear_color_condition_local_memory_expect_execution_inverted
├── clear_color_condition_local_memory_expect_noop
├── clear_color_condition_local_memory_expect_noop_inverted
├── clear_color_condition_local_memory_inherited_expect_execution
├── clear_color_condition_local_memory_inherited_expect_execution_inverted
├── clear_color_condition_local_memory_inherited_expect_noop
├── clear_color_condition_local_memory_inherited_expect_noop_inverted
├── clear_color_condition_local_memory_nested_buffer_expect_execution
├── clear_color_condition_local_memory_nested_buffer_expect_execution_inverted
├── clear_color_condition_local_memory_nested_buffer_expect_noop
├── clear_color_condition_local_memory_nested_buffer_expect_noop_inverted
├── clear_color_condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── clear_color_condition_local_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── clear_color_condition_local_memory_nested_buffer_nested_inherited_expect_noop
├── clear_color_condition_local_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── clear_color_condition_local_memory_nested_inherited_expect_execution
├── clear_color_condition_local_memory_nested_inherited_expect_execution_inverted
├── clear_color_condition_local_memory_nested_inherited_expect_noop
├── clear_color_condition_local_memory_nested_inherited_expect_noop_inverted
├── clear_color_condition_local_memory_secondary_buffer_expect_execution
├── clear_color_condition_local_memory_secondary_buffer_expect_execution_inverted
├── clear_color_condition_local_memory_secondary_buffer_expect_noop
├── clear_color_condition_local_memory_secondary_buffer_expect_noop_inverted
├── clear_color_condition_local_memory_secondary_buffer_inherited_expect_execution
├── clear_color_condition_local_memory_secondary_buffer_inherited_expect_execution_inverted
├── clear_color_condition_local_memory_secondary_buffer_inherited_expect_noop
├── clear_color_condition_local_memory_secondary_buffer_inherited_expect_noop_inverted
├── clear_color_image
├── clear_color_image_inverted
├── clear_color_no_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── clear_color_no_condition_host_memory_secondary_buffer_inherited_expect_execution
├── clear_color_no_condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── clear_color_no_condition_local_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_condition_host_memory_expect_execution
├── clear_depth_condition_host_memory_expect_execution_inverted
├── clear_depth_condition_host_memory_expect_noop
├── clear_depth_condition_host_memory_expect_noop_inverted
├── clear_depth_condition_host_memory_inherited_expect_execution
├── clear_depth_condition_host_memory_inherited_expect_execution_inverted
├── clear_depth_condition_host_memory_inherited_expect_noop
├── clear_depth_condition_host_memory_inherited_expect_noop_inverted
├── clear_depth_condition_host_memory_nested_buffer_expect_execution
├── clear_depth_condition_host_memory_nested_buffer_expect_execution_inverted
├── clear_depth_condition_host_memory_nested_buffer_expect_noop
├── clear_depth_condition_host_memory_nested_buffer_expect_noop_inverted
├── clear_depth_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── clear_depth_condition_host_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── clear_depth_condition_host_memory_nested_buffer_nested_inherited_expect_noop
├── clear_depth_condition_host_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── clear_depth_condition_host_memory_nested_inherited_expect_execution
├── clear_depth_condition_host_memory_nested_inherited_expect_execution_inverted
├── clear_depth_condition_host_memory_nested_inherited_expect_noop
├── clear_depth_condition_host_memory_nested_inherited_expect_noop_inverted
├── clear_depth_condition_host_memory_secondary_buffer_expect_execution
├── clear_depth_condition_host_memory_secondary_buffer_expect_execution_inverted
├── clear_depth_condition_host_memory_secondary_buffer_expect_noop
├── clear_depth_condition_host_memory_secondary_buffer_expect_noop_inverted
├── clear_depth_condition_host_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_condition_host_memory_secondary_buffer_inherited_expect_execution_inverted
├── clear_depth_condition_host_memory_secondary_buffer_inherited_expect_noop
├── clear_depth_condition_host_memory_secondary_buffer_inherited_expect_noop_inverted
├── clear_depth_condition_local_memory_expect_execution
├── clear_depth_condition_local_memory_expect_execution_inverted
├── clear_depth_condition_local_memory_expect_noop
├── clear_depth_condition_local_memory_expect_noop_inverted
├── clear_depth_condition_local_memory_inherited_expect_execution
├── clear_depth_condition_local_memory_inherited_expect_execution_inverted
├── clear_depth_condition_local_memory_inherited_expect_noop
├── clear_depth_condition_local_memory_inherited_expect_noop_inverted
├── clear_depth_condition_local_memory_nested_buffer_expect_execution
├── clear_depth_condition_local_memory_nested_buffer_expect_execution_inverted
├── clear_depth_condition_local_memory_nested_buffer_expect_noop
├── clear_depth_condition_local_memory_nested_buffer_expect_noop_inverted
├── clear_depth_condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── clear_depth_condition_local_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── clear_depth_condition_local_memory_nested_buffer_nested_inherited_expect_noop
├── clear_depth_condition_local_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── clear_depth_condition_local_memory_nested_inherited_expect_execution
├── clear_depth_condition_local_memory_nested_inherited_expect_execution_inverted
├── clear_depth_condition_local_memory_nested_inherited_expect_noop
├── clear_depth_condition_local_memory_nested_inherited_expect_noop_inverted
├── clear_depth_condition_local_memory_secondary_buffer_expect_execution
├── clear_depth_condition_local_memory_secondary_buffer_expect_execution_inverted
├── clear_depth_condition_local_memory_secondary_buffer_expect_noop
├── clear_depth_condition_local_memory_secondary_buffer_expect_noop_inverted
├── clear_depth_condition_local_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_condition_local_memory_secondary_buffer_inherited_expect_execution_inverted
├── clear_depth_condition_local_memory_secondary_buffer_inherited_expect_noop
├── clear_depth_condition_local_memory_secondary_buffer_inherited_expect_noop_inverted
├── clear_depth_no_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── clear_depth_no_condition_host_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_no_condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── clear_depth_no_condition_local_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_stencil_image
├── clear_depth_stencil_image_inverted
├── copy_buffer
├── copy_buffer_inverted
├── copy_buffer_to_image
├── copy_buffer_to_image_inverted
├── copy_image
├── copy_image_inverted
├── copy_image_to_buffer
├── copy_image_to_buffer_inverted
├── fill_buffer
├── fill_buffer_inverted
├── push_constant
├── push_constant_inverted
├── resolve_image
├── resolve_image_inverted
├── trace_rays
├── trace_rays_indirect
├── trace_rays_indirect2
├── trace_rays_indirect2_inverted
├── trace_rays_indirect_inverted
├── trace_rays_inverted
├── update_buffer
└── update_buffer_inverted
```

## Test Families

### Direct registered children

Direct children include generated `clear_color_*` and `clear_depth_*` leaves from the shared condition table, paired non-inverted/inverted general command leaves, graphics bind leaves, and ray-tracing leaves.

## Parameter Dimensions

The shared condition rows drive clear-color and clear-depth leaf names. The general command loop varies an `inverted` boolean and appends `_inverted` names for the second pass. Graphics-bind cases vary descriptor-set, index-buffer, pipeline, shader-object, and vertex-buffer binding operations. Ray-tracing cases vary direct, indirect, and indirect2 trace commands.

## Support / Feature Requirements

Clear ignore cases require `VK_EXT_conditional_rendering` and check inherited conditional rendering when requested. General command tests require `VK_EXT_conditional_rendering`; shader-object binding additionally requires `VK_EXT_shader_object`; ray-tracing cases require `VK_KHR_ray_tracing_pipeline`, with indirect2 requiring `VK_KHR_ray_tracing_maintenance1`.

## Verification Methods

Verification is case-specific: image and buffer results are compared against references with zero-threshold color comparisons or depth/stencil threshold comparison, and graphics-bind output is compared against the expected color buffer.

## Test Principles

The implementation varies whether the conditional-rendering predicate should execute or suppress work, then verifies externally visible image, buffer, or transform-feedback results rather than relying only on successful command submission.

## Notes and Uncertainties

The hierarchy tree lists only one direct level below `conditional_rendering.conditional_ignore` as required by the wiki registration contract. Deeper generated leaves are described in prose because they are registered below those direct children.
