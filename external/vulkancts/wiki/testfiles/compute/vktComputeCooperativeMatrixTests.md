# vktComputeCooperativeMatrixTests.cpp

## Overview

[`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6475-L6507) registers `cooperative_matrix`. It creates cooperative-matrix test branches for NV and KHR matrix use modes, delegates `op_constant_null` registration to [`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866), and adds non-VulkanSC 64-bit indexing cooperative-matrix cases.

## Role

Implementation file that also delegates one registered subgroup to a companion source file.

## Source Code

- Primary source: [`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L1)
- Companion source: [`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1)
- Factory declaration: [`vktComputeCooperativeMatrixTests.hpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.hpp#L37-L38)

## Registration Hierarchy

```text
compute.pipeline.cooperative_matrix
├── nv
├── khr_a
├── khr_b
├── khr_c
├── khr_r
├── op_constant_null
└── 64b_indexing (non-VulkanSC only)
```

## Test Families

### nv — NV cooperative-matrix use mode

The NV branch is produced by `createCooperativeMatrixTestsInternal(..., UT_NV)` ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6478-L6481)). Its internal generator names the branch with `getUseType(useType)` and builds scope/type/storage/layout descendants ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5523-L5528), [`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5760-L6021)).

### khr_a — KHR matrix A use mode

The KHR-A branch is registered by the root factory ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6480-L6482)) and participates in the same nested generator, with some matrix-multiply tests skipped to avoid redundant copies when use type is A or B ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5821-L5825)).

### khr_b — KHR matrix B use mode

The KHR-B branch is registered alongside KHR-A ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6481-L6483)) and follows the same type/storage/scope generation rules.

### khr_c — KHR matrix C use mode

The KHR-C branch is registered by [`createCooperativeMatrixTests()`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6482-L6484). The generator skips most non-cross tests for matrix C ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5813-L5819)).

### khr_r — KHR result matrix use mode

The `khr_r` result branch is registered by the root factory and uniquely hosts accumulator conversion/transpose tests that are not repeated across A/B/C ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6483-L6484), [`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5927-L5933)).

### op_constant_null — Null cooperative-matrix constants

The companion source adds `op_constant_null` with `null_a`, `null_b`, `null_c`, and `null_r` cases ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866)); that delegated registration subtree is documented separately in [`vktComputeCooperativeMatrixOpConstantNullTests.md`](vktComputeCooperativeMatrixOpConstantNullTests.md).

### 64b_indexing — Large cooperative-matrix buffer indexing

In non-VulkanSC builds, `64b_indexing` registers row-major and tensor-layout cases with normal, medium, and large offsets ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6487-L6505)).

## Parameter Dimensions

| Dimension | Evidence |
|---|---|
| Use type | Root branches are `UT_NV`, `UT_KHR_A`, `UT_KHR_B`, `UT_KHR_C`, and `UT_KHR_Result` ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6480-L6484)) |
| Scope, test type, subgroup-size mode | Nested loops over scope cases, test-type cases, and subgroup-size cases create direct descendants inside each use mode ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5760-L5781)) |
| Component type and storage class | Loops create component-type, storage-class, row/column, and address-method combinations with filtering rules ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5783-L6013)) |
| Conversion and multicomponent tests | Additional `convert`, `convert_sat`, and `multicomponent` groups are generated for applicable KHR branches ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6025-L6179)) |
| 64-bit indexing offsets | 64-bit cases use 2 GiB buffers with small, 1 GiB, and 5 GiB offsets for row-major and tensor layout ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6492-L6504)) |

## Support / Feature Requirements

Cooperative-matrix cases require Vulkan 1.1, either KHR or NV cooperative matrix support depending on use type, Vulkan memory model, variable pointers for variable-pointer storage classes, buffer device address for physical storage buffers, and shader float16 when float16 component types are used ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L739-L782)). Additional gates cover cooperative-matrix combinations, shader-object requirements, bfloat16 cooperative matrix features, and float8 cooperative matrix features ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L994-L1025)). 64-bit cooperative-matrix indexing requires `shader64BitIndexing` ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6232-L6237)).

## Verification Methods

The file constructs `CaseDef` records for generated cooperative-matrix shader cases and filters unsupported or redundant combinations before creating `CooperativeMatrixTestCase` instances ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5797-L6013)). The generator varies operation type, scope, component type, storage class, layout, address method, subgroup sizing, and workgroup/subgroup dimensions, which lets shader execution validate the selected cooperative-matrix operation under those conditions.

## Test Principles Observed

- The registration is evidence-driven by actual `TestCaseGroup` names, not by factory-symbol names; `getUseType(useType)` determines the direct use-mode group name ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5504-L5521)).
- The file prunes invalid or redundant cases through explicit conditionals rather than claiming full Cartesian coverage ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L5803-L5977)).

## Notes / Uncertainties

- The direct `nv`, `khr_a`, `khr_b`, `khr_c`, and `khr_r` names are validated through registration-path validation; the helper function that maps `UseType` to string is outside the extracted line range but is used at group construction.
