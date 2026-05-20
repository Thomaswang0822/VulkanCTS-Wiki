# compute

## Overview

The [`compute`](../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85) category documents Vulkan compute dispatch and compute-shader behavior. The Vulkan API test plan states that compute dispatch tests validate call parameters and verify that workgroup counts and invocation IDs reach shader invocations ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L676-L681)). The inspected source covers baseline compute execution, large buffer indexing, device groups, cooperative matrices, indirect dispatch, shader built-ins, zero-initialized workgroup memory, and explicit workgroup-memory layout.

## Registration Entry Point

The category is rooted in [`createTests()`](../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85). [`createChildren()`](../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64) registers the child groups under each construction-type root:

```text
compute
├── pipeline
│   ├── basic
│   ├── 64b_indexing
│   ├── device_group
│   ├── cooperative_matrix (non-VulkanSC only)
│   ├── indirect_dispatch
│   ├── builtin_var
│   ├── zero_initialize_workgroup_memory
│   └── workgroup_memory_explicit_layout (non-VulkanSC only)
├── shader_object_spirv (non-VulkanSC only)
│   └── same child factories as pipeline, subject to each file's shader-object exclusions
└── shader_object_binary (non-VulkanSC only)
    └── same child factories as pipeline, subject to each file's shader-object exclusions
```

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktComputeTests.cpp`](../../modules/vulkan/compute/vktComputeTests.cpp#L1) | Registration | Root dispatcher for `pipeline`, `shader_object_spirv`, and `shader_object_binary` |
| [`vktComputeBasicComputeShaderTests.cpp`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1) | Implementation | Registers `basic`, `64b_indexing`, and `device_group` |
| [`vktComputeCooperativeMatrixTests.cpp`](../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L1) | Implementation | Registers `cooperative_matrix` children and includes 64-bit cooperative-matrix indexing |
| [`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1) | Nested implementation with registration | Adds `op_constant_null` and its `null_a`/`null_b`/`null_c`/`null_r` children under `cooperative_matrix` |
| [`vktComputeIndirectComputeDispatchTests.cpp`](../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L1) | Implementation | Registers indirect dispatch upload and compute-generated command-buffer paths |
| [`vktComputeShaderBuiltinVarTests.cpp`](../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L1) | Implementation | Registers compute built-in variable cases |
| [`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1) | Implementation | Registers `VK_KHR_zero_initialize_workgroup_memory` coverage |
| [`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1) | Implementation | Registers `VK_KHR_workgroup_memory_explicit_layout` coverage |
| [`vktComputeTestsUtil.cpp`](../../modules/vulkan/compute/vktComputeTestsUtil.cpp#L1) | Helper | Utility file; no observed direct test registration |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktComputeBasicComputeShaderTests.cpp`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1) | [`vktComputeBasicComputeShaderTests.md`](../testfiles/compute/vktComputeBasicComputeShaderTests.md) |
| [`vktComputeCooperativeMatrixTests.cpp`](../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L1) | [`vktComputeCooperativeMatrixTests.md`](../testfiles/compute/vktComputeCooperativeMatrixTests.md) |
| [`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1) | [`vktComputeCooperativeMatrixOpConstantNullTests.md`](../testfiles/compute/vktComputeCooperativeMatrixOpConstantNullTests.md) |
| [`vktComputeIndirectComputeDispatchTests.cpp`](../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L1) | [`vktComputeIndirectComputeDispatchTests.md`](../testfiles/compute/vktComputeIndirectComputeDispatchTests.md) |
| [`vktComputeShaderBuiltinVarTests.cpp`](../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L1) | [`vktComputeShaderBuiltinVarTests.md`](../testfiles/compute/vktComputeShaderBuiltinVarTests.md) |
| [`vktComputeTests.cpp`](../../modules/vulkan/compute/vktComputeTests.cpp#L1) | [`vktComputeTests.md`](../testfiles/compute/vktComputeTests.md) |
| [`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1) | [`vktComputeWorkgroupMemoryExplicitLayoutTests.md`](../testfiles/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.md) |
| [`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1) | [`vktComputeZeroInitializeWorkgroupMemoryTests.md`](../testfiles/compute/vktComputeZeroInitializeWorkgroupMemoryTests.md) |

## Subgroup Structure and Major Themes

- [`basic`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L5986-L6234): basic compute execution, buffer and image side effects, barriers, shared variables, empty workgroups, maximum local sizes, compute-only queues, replicated composites, Amber regressions, undefined values, and dispatch sequencing.
- [`64b_indexing`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6237-L6265): large SSBO indexing and untyped-pointer coverage.
- [`device_group`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6268-L6284): device-group dispatch base and device-index shader behavior.
- [`cooperative_matrix`](../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6475-L6507): NV/KHR cooperative-matrix operation matrices, null constants, and non-VulkanSC large-index cooperative-matrix cases.
- [`indirect_dispatch`](../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L839-L920): uploaded and compute-generated indirect dispatch command buffers with offsets, empty commands, multi-dispatch, compute-only queues, and device-address commands.
- [`builtin_var`](../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L650-L679): compute built-ins for workgroup counts, IDs, sizes, global IDs, local IDs, and local invocation index.
- [`zero_initialize_workgroup_memory`](../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1382-L1423): zero initialization across types, composites, maximum workgroup dimensions, specialization sizes, repeated pipeline creation, and Amber shared-memory blocks.
- [`workgroup_memory_explicit_layout`](../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1289-L1323): explicit workgroup-memory layout aliasing, zeroing, padding, size, copy-memory, and zero-initialize-extension interactions.

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Pipeline construction mode | Root `pipeline`, `shader_object_spirv`, and `shader_object_binary` groups select the compute pipeline construction type ([`vktComputeTests.cpp`](../../modules/vulkan/compute/vktComputeTests.cpp#L70-L76)) |
| Workgroup/local sizes | Basic tests use explicit local/work sizes, including empty axes and multi-group vectors ([`vktComputeBasicComputeShaderTests.cpp`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6000-L6124)) |
| Buffer size, offset, and indexing width | Basic and cooperative-matrix files include bounds checks, large buffers, and 64-bit indexing cases ([`vktComputeBasicComputeShaderTests.cpp`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L6241-L6262), [`vktComputeCooperativeMatrixTests.cpp`](../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6487-L6505)) |
| Indirect command source and offset | Indirect dispatch tests vary uploaded/generated command buffers, offsets, empty commands, and multi-command buffers ([`vktComputeIndirectComputeDispatchTests.cpp`](../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L842-L918)) |
| Numeric type and storage/layout | Zero-initialize and explicit-layout files derive feature gates from scalar/vector/matrix and storage layout case data ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L346-L387), [`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L100-L140)) |
| Cooperative matrix dimensions | Cooperative-matrix generation varies use type, scope, test type, subgroup-size mode, component type, storage class, layout, and address method ([`vktComputeCooperativeMatrixTests.cpp`](../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5760-L6013)) |

## Recurring Support Requirements

Observed recurring gates include shader-object requirements for shader-object construction paths, `VK_KHR_device_group` and `VK_KHR_maintenance5` for device-group dispatch, `VK_EXT_robustness2` for robust bounds checks, `VK_EXT_shader_64bit_indexing`/`shader64BitIndexing` for large indexing, `VK_KHR_shader_untyped_pointers`, `VK_KHR_device_address_commands` for indirect command buffers, cooperative-matrix feature families, `VK_KHR_zero_initialize_workgroup_memory`, `VK_KHR_workgroup_memory_explicit_layout`, `VK_KHR_spirv_1_4`, variable pointers, buffer device address, and shader numeric-width features such as float16, float64, int8, int16, int64, bfloat16, and float8 ([`vktComputeBasicComputeShaderTests.cpp`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1311-L1333), [`vktComputeIndirectComputeDispatchTests.cpp`](../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L661-L686), [`vktComputeCooperativeMatrixTests.cpp`](../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L739-L786), [`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L329-L389), [`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L141)).

## Recurring Verification Methods

Verification commonly uses shader-written buffers or images compared against expected host-side values. Examples include built-in-variable result-buffer comparison ([`vktComputeShaderBuiltinVarTests.cpp`](../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L600-L632)), generated shaders that map `gl_NumWorkGroups`, `gl_WorkGroupSize`, and `gl_GlobalInvocationID` to buffer elements ([`vktComputeBasicComputeShaderTests.cpp`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L1693-L1705)), compute-generated indirect command buffers followed by a compute-to-indirect barrier ([`vktComputeIndirectComputeDispatchTests.cpp`](../../modules/vulkan/compute/vktComputeIndirectComputeDispatchTests.cpp#L751-L829)), and pre-execution limit/feature checks for workgroup and shared-memory sizes ([`vktComputeBasicComputeShaderTests.cpp`](../../modules/vulkan/compute/vktComputeBasicComputeShaderTests.cpp#L4817-L4831), [`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1153-L1159)).

## Relationship to the Test Plan

The inspected test-plan compute section says compute tests validate dispatch call parameters and verify workgroup and invocation IDs in shaders ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L676-L681)). The source files implement that theme directly in `builtin_var`, indirect dispatch, and many buffer/image side-effect cases. The plan also notes that compute-specific shader features such as shared memory are assumed to be covered by SPIR-V tests ([`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L681-L681)); the compute category nevertheless includes extension-specific workgroup-memory behavior where the inspected Vulkan CTS source registers it.

## Notes / Uncertainties

- The `pipeline` hierarchy is fully expanded to the registered top-level compute children. Shader-object roots reuse the same child factories, but several Amber-based or extension-heavy branches are conditionally absent as documented in Level-3 pages.
- `vktComputeCooperativeMatrixOpConstantNullTests.cpp` is a delegated nested registration source under `cooperative_matrix`; it has a Level-3 page because it registers the `op_constant_null` subtree even though it is not a root-level included branch.
