# vktComputeWorkgroupMemoryExplicitLayoutTests.cpp

## Overview

[`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1289-L1323) registers `workgroup_memory_explicit_layout`, covering `VK_KHR_workgroup_memory_explicit_layout` behavior for aliasing, manual zeroing, padding, shared-memory size, copy-memory Amber tests, and interaction with zero-initialize-workgroup-memory extension tests.

## Role

Implementation file.

## Source Code

- Primary source: [`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1)
- Factory declaration: [`vktComputeWorkgroupMemoryExplicitLayoutTests.hpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.hpp#L38-L39)

## Registration Hierarchy

```text
compute.pipeline.workgroup_memory_explicit_layout
├── alias
├── zero
├── padding
├── size
├── copy_memory (pipeline only)
└── zero_ext (pipeline only)
```

## Test Families

### alias — Aliasing between workgroup-memory blocks and types

`alias` is registered first and populated by `AddAliasTests()` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1294-L1297)). Its support path derives required scalar layout and numeric-type features from case data ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L408-L421)).

### zero — Manual zero initialization across blocks

`zero` is populated by `AddZeroTests()` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1299-L1302)) and checks required element/field types before running ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L738-L750)).

### padding — Padding and scalar-layout-sensitive cases

`padding` is populated by `AddPaddingTests()` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1304-L1306)); support derives type requirements from every case type and whether scalar layout is needed ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1004-L1015)).

### size — Shared-memory size limits

`size` is populated by `AddSizeTests()` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1308-L1310)) and rejects cases larger than `maxComputeSharedMemorySize` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1153-L1159)).

### copy_memory — Amber copy-memory cases

For non-shader-object modes, `copy_memory` registers `basic`, `two_invocations`, and `variable_pointers`; `variable_pointers` requires variable pointers and descriptor indexing ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1256-L1268), [`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1316)).

### zero_ext — Zero-initialize extension interaction

For non-shader-object modes, `zero_ext` adds Amber cases `block`, `other_block`, and `block_with_offset` that also require zero-initialize-workgroup-memory support through `CreateAmberTestCase()` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1271-L1284), [`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1318-L1320)).

## Parameter Dimensions

| Dimension | Evidence |
|---|---|
| Layout features | Common support checks include base explicit layout, SPIR-V 1.4, scalar block layout, 8-bit access, and 16-bit access as case data requires ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L141)) |
| Numeric types | Case support checks track int8, int16, int64, float16, and float64 needs ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L106-L139)) |
| Memory-size limits | `size` compares requested shared-memory size with `maxComputeSharedMemorySize` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1153-L1159)) |
| Pipeline construction | `copy_memory` and `zero_ext` are only registered when the construction type is not a shader-object mode ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321)) |

## Support / Feature Requirements

The central support helper requires `VK_KHR_workgroup_memory_explicit_layout`, `VK_KHR_spirv_1_4`, and shader-object requirements when applicable ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L77-L82)). It conditionally requires scalar block layout, int8/int16 explicit layout access, shader int/float widths, and float64 based on `CheckSupportParams` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L100-L140)). `copy_memory.variable_pointers` adds `VariablePointerFeatures.variablePointers` and `VK_EXT_descriptor_indexing` requirements ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1263-L1268)).

## Verification Methods

The generated C++ tests exercise aliasing, zeroing, padding, and size behavior through compute shaders created from case definitions, while Amber cases load external `.amber` scripts via `CreateAmberTestCase()` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1232-L1251)). The size test also performs a pre-execution device-limit check against `maxComputeSharedMemorySize` ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1153-L1159)).

## Test Principles Observed

- The file centralizes feature gating in `checkSupportWithParams()` and lets each family derive its required layout/type features from case data.
- Shader-object construction excludes Amber-based children because those helper paths are only added outside shader-object modes ([`vktComputeWorkgroupMemoryExplicitLayoutTests.cpp`](../../../modules/vulkan/compute/vktComputeWorkgroupMemoryExplicitLayoutTests.cpp#L1312-L1321)).

## Notes / Uncertainties

- The tree lists direct family groups; generated descendants under `alias`, `zero`, `padding`, and `size` are summarized because their names are produced by helper loops.
