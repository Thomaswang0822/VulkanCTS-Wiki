# vktComputeZeroInitializeWorkgroupMemoryTests.cpp

## Overview

[`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1382-L1423) registers `zero_initialize_workgroup_memory`, a set of tests for `VK_KHR_zero_initialize_workgroup_memory`. It covers maximum workgroup memory, scalar/vector/matrix types, composite structures, maximum workgroup counts per dimension, specialization-constant workgroup sizes, repeated pipeline construction, and non-shader-object Amber shared-memory block cases.

## Role

Implementation file.

## Source Code

- Primary source: [`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1)
- Factory declaration: [`vktComputeZeroInitializeWorkgroupMemoryTests.hpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.hpp#L38-L39)

## Registration Hierarchy

```text
compute.pipeline.zero_initialize_workgroup_memory
├── max_workgroup_memory
├── types
├── composites
├── max_workgroups
├── specialize_workgroup
├── repeat_pipeline
└── shared_memory_blocks (pipeline only, non-VulkanSC only)
```

## Test Families

### max_workgroup_memory — Maximum workgroup memory initialization

The `max_workgroup_memory` group is registered and populated by `AddMaxWorkgroupMemoryTests()` ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1387-L1391)).

### types — Scalar/vector/matrix type coverage

`types` is populated by `AddTypeTests()` ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1393-L1395)); support checks show coverage includes float16/float64, int8/int16/int64, and corresponding vector/matrix type names when features are present ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L346-L387)).

### composites — Composite type coverage

`composites` is populated by `AddCompositeTests()` ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1397-L1399)); feature needs are encoded in bit flags for float16, float64, int8, int16, and int64 ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L552-L567)).

### max_workgroups — Axis-wise maximum workgroup counts

The `max_workgroups` group registers `x`, `y`, and `z` cases ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L995-L1000), [`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1401-L1403)).

### specialize_workgroup — Specialization-constant workgroup sizes

`specialize_workgroup` is registered through `AddSpecializeWorkgroupTests()` and rejects workgroup sizes above `maxComputeWorkGroupInvocations` ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1405-L1407), [`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1051-L1061)).

### repeat_pipeline — Repeated pipeline construction

`repeat_pipeline` is added by `AddRepeatedPipelineTests()` ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1409-L1411)) and uses the same extension gate as other generated tests ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1154-L1158)).

### shared_memory_blocks — Amber shared-memory-block cases

In non-VulkanSC, non-shader-object modes, Amber cases are registered for workgroup sizes such as `workgroup_size_128`, `workgroup_size_8x8x2`, and other permutations ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1360-L1375), [`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1413-L1419)).

## Parameter Dimensions

| Dimension | Evidence |
|---|---|
| Type family | Type checks distinguish float16, float64, int8, int16, and int64 scalar/vector/matrix names ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L346-L387)) |
| Composite feature flags | Composite cases encode feature requirements in bit flags inspected during `CompositeTest::checkSupport()` ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L552-L567)) |
| Workgroup dimensions | `max_workgroups` registers `x`, `y`, and `z` cases ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L995-L1000)) |
| Amber workgroup sizes | Shared-memory block Amber tests enumerate seven workgroup-size names ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1366-L1375)) |

## Support / Feature Requirements

Most cases require `VK_KHR_zero_initialize_workgroup_memory` and shader-object requirements when applicable ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L204-L208)). Type and composite tests additionally check `shaderFloat16`, `shaderFloat64`, `shaderInt8`, `shaderInt16`, and `shaderInt64` as required by the case data ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L329-L389), [`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L535-L568)). Specialization workgroup tests also check device workgroup invocation limits ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1057-L1061)).

## Verification Methods

The file uses generated tests and Amber tests that read zero-initialized workgroup memory under different type and layout patterns. The visible source establishes pass/fail gating through feature checks and generated case construction; detailed shader comparison code is distributed in the generated program bodies and Amber files referenced from the registration helpers ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1360-L1375)).

## Test Principles Observed

- The category isolates zero-initialization behavior by varying type, composite layout, workgroup size, and repeated pipeline setup while using a common extension gate.
- Shader-object modes exclude Amber-only shared-memory-block tests because the source comments that Amber cannot use shader objects ([`vktComputeZeroInitializeWorkgroupMemoryTests.cpp`](../../../modules/vulkan/compute/vktComputeZeroInitializeWorkgroupMemoryTests.cpp#L1413-L1416)).

## Notes / Uncertainties

- This page documents direct child groups; many deeper generated cases are created by helper functions and are summarized at family granularity.
