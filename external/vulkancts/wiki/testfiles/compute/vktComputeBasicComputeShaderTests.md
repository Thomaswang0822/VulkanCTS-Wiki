# vktComputeBasicComputeShaderTests.cpp

## Overview

[`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5986-L6285) registers the `basic`, `64b_indexing`, and `device_group` compute branches. The file covers dispatch dimensions, storage-buffer reads/writes, shared memory and image operations, compute-only queues, large buffer indexing, untyped pointers, and device-group dispatch behavior.

## Role

Implementation file with multiple directly registered compute subgroups.

## Source Code

- Primary source: [`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1)
- Factory declarations: [`vktComputeBasicComputeShaderTests.hpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.hpp#L37-L42)

## Registration Hierarchy

```text
compute.pipeline.basic
├── empty_shader
├── concurrent_compute
├── empty_workgroup_x
├── empty_workgroup_y
├── empty_workgroup_z
├── empty_workgroup_all
├── max_local_size_x
├── max_local_size_y
├── max_local_size_z
├── ubo_to_ssbo_single_invocation
├── ubo_to_ssbo_single_group
├── ubo_to_ssbo_multiple_invocations
├── ubo_to_ssbo_multiple_groups
├── copy_ssbo_single_invocation
├── copy_ssbo_multiple_invocations
├── copy_ssbo_multiple_groups
├── copy_ssbo_bounds
├── ssbo_rw_single_invocation
├── ssbo_rw_multiple_groups
├── ssbo_unsized_arr_single_invocation
├── ssbo_unsized_arr_multiple_groups
├── write_multiple_arr_single_invocation
├── write_multiple_arr_multiple_groups
├── write_multiple_unsized_arr_single_invocation
├── write_multiple_unsized_arr_multiple_groups
├── read_unbound_ssbo
├── ssbo_local_barrier_single_invocation
├── ssbo_local_barrier_single_group
├── ssbo_local_barrier_multiple_groups
├── ssbo_cmd_barrier_single
├── ssbo_cmd_barrier_multiple
├── shared_var_single_invocation
├── shared_var_single_group
├── shared_var_multiple_invocations
├── shared_var_multiple_groups
├── shared_atomic_op_single_invocation
├── shared_atomic_op_single_group
├── shared_atomic_op_multiple_invocations
├── shared_atomic_op_multiple_groups
├── copy_image_to_ssbo_small
├── copy_image_to_ssbo_large
├── copy_ssbo_to_image_small
├── copy_ssbo_to_image_large
├── image_atomic_op_local_size_1
├── image_atomic_op_local_size_8
├── image_barrier_single
├── image_barrier_multiple
├── secondary_compute_only_queue
├── replicated_composites_vector_value (non-VulkanSC only)
├── replicated_composites_matrix_value (non-VulkanSC only)
├── replicated_composites_array_value (non-VulkanSC only)
├── replicated_composites_array_array_value (non-VulkanSC only)
├── replicated_composites_struct_value (non-VulkanSC only)
├── replicated_composites_struct_struct_value (non-VulkanSC only)
├── replicated_composites_coopmat_value (non-VulkanSC only)
├── replicated_composites_vector_constant (non-VulkanSC only)
├── replicated_composites_matrix_constant (non-VulkanSC only)
├── replicated_composites_array_constant (non-VulkanSC only)
├── replicated_composites_array_array_constant (non-VulkanSC only)
├── replicated_composites_struct_constant (non-VulkanSC only)
├── replicated_composites_struct_struct_constant (non-VulkanSC only)
├── replicated_composites_coopmat_constant (non-VulkanSC only)
├── replicated_composites_vector_specconstant (non-VulkanSC only)
├── replicated_composites_matrix_specconstant (non-VulkanSC only)
├── replicated_composites_array_specconstant (non-VulkanSC only)
├── replicated_composites_array_array_specconstant (non-VulkanSC only)
├── replicated_composites_struct_specconstant (non-VulkanSC only)
├── replicated_composites_struct_struct_specconstant (non-VulkanSC only)
├── replicated_composites_coopmat_specconstant (non-VulkanSC only)
├── write_ssbo_array (pipeline only, non-VulkanSC only)
├── atomic_barrier_sum_small (pipeline only, non-VulkanSC only)
├── vec2_nclamp_nan_component (pipeline only, non-VulkanSC only)
├── branch_past_barrier (pipeline only, non-VulkanSC only)
├── float64_isnan_isinf (pipeline only, non-VulkanSC only)
├── float16_isnan_isinf (pipeline only, non-VulkanSC only)
├── webgl_spirv_loop (pipeline only, non-VulkanSC only)
├── pk_immediate (pipeline only, non-VulkanSC only)
├── pkadd_immediate (pipeline only, non-VulkanSC only)
├── undefined_values
└── indirect_after_base_dispatch
```

## Test Families

### basic — Core compute shader behavior

The `basic` group is created in [`createBasicComputeShaderTests()`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5986-L5995). Direct children cover empty shaders/workgroups, maximum local sizes, buffer-to-buffer copies, SSBO read/write forms, local and command barriers, shared variables, image copies, image atomics, image barriers, compute-only queue use, replicated composites, Amber regression cases, undefined values, and an indirect-after-base-dispatch sequence ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5992-L6233)).

### 64b_indexing — Large storage-buffer indexing

The same file registers a separate `64b_indexing` group with large-buffer SSBO copy cases and an `untyped_pointers` case ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6237-L6265)).

### device_group — Device-group compute dispatch

The separate `device_group` group registers `dispatch_base`, a non-VulkanSC `dispatch_base_maintenance5`, and `device_index` cases ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6268-L6284)).

## Parameter Dimensions

| Dimension | Evidence |
|---|---|
| Local and work sizes | Explicit `tcu::IVec3`/`tcu::UVec3` values in the `basic` registrations ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6000-L6124)) |
| Buffer sizes and bounds modes | SSBO/UBO cases pass element counts and `doBoundsCheck` flags ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6026-L6053)) |
| Composite type and instantiation mode | Replicated-composite names are generated for vector, matrix, array, nested array, struct, nested struct, and cooperative matrix over `value`, `constant`, and `specconstant` ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6154-L6180)) |
| Device-group modes | `dispatch_base`, `dispatch_base_maintenance5`, and `device_index` use explicit sizes and base offsets ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6273-L6282)) |

## Support / Feature Requirements

Common support checks call shader-object requirements for shader-object construction variants, for example in SSBO and image tests ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1687-L1691), [`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2647-L2651)). Large indexing requires `shader64BitIndexing` when the buffer exceeds the 32-bit element threshold, and bounds cases require `VK_EXT_robustness2` plus `robustBufferAccess2` ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1311-L1333)). Untyped pointers require `VK_KHR_shader_untyped_pointers` and `VK_EXT_shader_64bit_indexing` ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1857-L1862)). Device-group dispatch requires `VK_KHR_device_group`, with `VK_KHR_maintenance5` for the maintenance5 variant ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L3330-L3337)). Replicated composites require `shaderReplicatedComposites`, and cooperative-matrix replicated composites also check cooperative matrix support ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5380-L5398)).

## Verification Methods

Observed verification methods include generated GLSL that uses `gl_NumWorkGroups`, `gl_WorkGroupSize`, and `gl_GlobalInvocationID` to map invocations to buffer elements ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1693-L1705)), shader-side SSBO writes to multiple outputs ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1999-L2010)), explicit SSBO barrier shader programs ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2397-L2407)), and image atomic shaders with coherent image storage ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L2653-L2665)). The maximum-workgroup-size test compares reported per-axis limits against `maxComputeWorkGroupInvocations` and storage-buffer capacity before execution ([`vktComputeBasicComputeShaderTests.cpp`](../../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4817-L4831)).

## Test Principles Observed

- The file exercises compute dispatch effects through combinations of local size, workgroup count, and buffer/image side effects, matching the compute test-plan focus on dispatch parameters ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L679)).
- The same implementation is reused under the root pipeline-construction variants through the dispatcher ([`vktComputeTests.cpp`](../../../modules/vulkan/compute/vktComputeTests.cpp#L52-L54)).

## Notes / Uncertainties

- The parseable hierarchy tree expands the `compute.pipeline.basic` root. The file also registers sibling `64b_indexing` and `device_group` groups; they are documented in prose because the Level-3 contract allows only one canonical tree per page.
