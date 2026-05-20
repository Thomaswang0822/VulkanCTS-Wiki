# vktComputeCooperativeMatrixOpConstantNullTests.cpp

## Overview

[`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866) is a delegated cooperative-matrix registration unit. It adds the `op_constant_null` subgroup under `compute.pipeline.cooperative_matrix` and registers one case for each tested cooperative-matrix operand/result selection: `null_a`, `null_b`, `null_c`, and `null_r`.

## Role

Nested implementation file with registered tests delegated from the cooperative-matrix parent.

## Source Code

- Primary source: [`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1)
- Parent registration source: [`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6471-L6486)

## Registration Hierarchy

```text
compute.pipeline.cooperative_matrix.op_constant_null
├── null_a
├── null_b
├── null_c
└── null_r
```

## Test Families

### null_a — Null matrix A

The `null_a` child is generated from the static matrix/name table and stores `Matrices::A` in the case parameters ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1850-L1863)). Verification expects matrix A to be null and matrix B to remain non-null for this target ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1685-L1699)).

### null_b — Null matrix B

The `null_b` child is generated from the same table with `Matrices::B` ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1850-L1863)). Verification expects matrix A to remain non-null, matrix B to be null, and result R to match C for the selected multiplication path ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1700-L1716)).

### null_c — Null matrix C

The `null_c` child targets the accumulator C matrix ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1850-L1863)). Verification checks that C is null and compares R against the host-side `A * B` reference ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1718-L1729)).

### null_r — Null result matrix R

The `null_r` child targets the result matrix ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1850-L1863)). Verification checks that R is null after the selected execution path ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1731-L1738)).

## Parameter Dimensions

| Dimension | Evidence |
|---|---|
| Target matrix | The registration table enumerates A, B, C, and R targets with `null_a`, `null_b`, `null_c`, and `null_r` names ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1850-L1855)) |
| Pipeline construction type | The parent passes the active compute pipeline construction type into the delegated registration function and each case stores it in `Params` ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6471-L6485), [`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1860-L1863)) |
| Cooperative-matrix configurations | Static configuration generation combines possible component types and `8`, `16`, and `32` M/N/K sizes, then filters invalid operand, type-compatibility, and size combinations ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1243-L1304)) |
| Dynamic viability | Runtime configuration discovery queries `vkGetPhysicalDeviceCooperativeMatrixPropertiesKHR` and retains configurations accepted by `isPossibleConfiguration()` ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1218-L1233)) |

## Support / Feature Requirements

Each case requires cooperative matrix support and at least one viable configuration; otherwise `checkSupport()` throws `NotSupportedError` ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1154-L1168)). Shader-object construction modes additionally require `VK_EXT_shader_object` ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1170-L1174)). Feature checks are also derived from the viable component types, including 16-bit storage/float16, int8, float8, and bfloat16 cooperative-matrix support where present ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1176-L1215)).

## Verification Methods

The source generates SPIR-V assembly containing `OpConstantNull` cooperative-matrix values for A, B, C, and R matrix types ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L851-L868)). During execution, each viable configuration is logged, the selected target matrix is executed, and `verifyResult()` compares observed matrices with target-specific expectations or host-side references; mismatches are counted and reported ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1656-L1762), [`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1765-L1818)).

## Test Principles Observed

- The file isolates null-constant behavior from the broader cooperative-matrix generator by registering one direct child per matrix target ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866)).
- The test avoids claiming full static coverage by intersecting generated/static configurations with runtime-viable configurations before execution ([`vktComputeCooperativeMatrixOpConstantNullTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1328-L1337)).

## Notes / Uncertainties

- This source does not have its own public header in the compute directory; the parent declares the delegated registration function with `extern` before calling it ([`vktComputeCooperativeMatrixTests.cpp`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6471-L6485)).
