# vktSpvAsmComputeShaderDerivativesTests

## Overview

Tests for SPIR-V derivative operations in compute-like shaders (compute, mesh, and task shaders). Verifies derivative value correctness, index verification, quad operations (broadcast/swap), and LOD sampling/querying using the [`VK_KHR_compute_shader_derivatives`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2831-L2834) extension.

## Role

Implementation file

## Source

- [vktSpvAsmComputeShaderDerivativesTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3730)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.compute_shader_derivatives
├── compute
├── mesh
└── task
```

## Test Families

### compute — Compute shader derivative tests

Tests derivative operations in GLCompute shaders. Each sub-group exercises [`derivative_value`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3743-L3886), [`verify_ndx`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3888-L3954), [`quad_op`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3956-L4029), and [`lod_op`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L4031-L4173) test categories with linear and quads derivative features across multiple data types (float32, vec2_float32, vec3_float32, vec4_float32).

Observed in [`createComputeShaderDerivativesTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3730-L4176) at [vktSpvAsmComputeShaderDerivativesTests.cpp#L3730-L4176](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3730-L4176).

### mesh — Mesh shader derivative tests

Tests derivative operations in mesh shaders. Same test structure as compute but uses mesh shader entry points. Requires [`VK_EXT_mesh_shader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2850-L2859) and [`meshAndTaskShaderDerivatives`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2853-L2857) property support.

Observed in [`ShaderType::MESH`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2567-L2678) handling at [vktSpvAsmComputeShaderDerivativesTests.cpp#L3735](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3735).

### task — Task shader derivative tests

Tests derivative operations in task shaders. Same test structure as compute but uses task shader entry points. Requires [`VK_EXT_mesh_shader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2850-L2859) with both [`meshShader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2861-L2873) and [`taskShader`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2868-L2874) features, plus [`meshAndTaskShaderDerivatives`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2853-L2857) property support.

Observed in [`ShaderType::TASK`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2689-L2817) handling at [vktSpvAsmComputeShaderDerivativesTests.cpp#L3735](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3735).

Each shader type group contains these direct children:

- **derivative_value** — Tests proper derivative values (OpDPdx, OpDPdy, OpDPdxFine, OpDPdyFine, OpDPdxCoarse, OpDPdyCoarse) with linear and quads features across data types and workgroup configurations
- **verify_ndx** — Tests proper invocation indices in compute-like shaders using subgroup operations, with linear and quads features
- **quad_op** — Tests quad subgroup operations (OpGroupNonUniformQuadBroadcast, OpGroupNonUniformQuadSwap) with broadcast and swap variants across data types
- **lod_op** — Tests LOD operations: sample (OpImageSampleExplicitLod) and query (OpImageQueryLod) with linear and quads features across mip levels

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| ShaderType | `compute`, `mesh`, `task` | Shader stage under test |
| TestType | `DERIVATIVE_VALUE`, `VERIFY_NDX`, `QUAD_OPERATIONS`, `LOD_SAMPLE`, `LOD_QUERY` | Category of derivative test |
| DerivativeVariant | `normal`, `fine`, `coarse` | Derivative precision variant (for [`derivative_value`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3743-L3886)) |
| DataType | `float32`, `vec2_float32`, `vec3_float32`, `vec4_float32` | Data type for derivative computation |
| DerivativeFeature | `linear`, `quads` | Derivative group execution mode (DerivativeGroupLinearKHR / DerivativeGroupQuadsKHR) |
| QuadOp | `broadcast`, `swap` | Quad operation type (for [`quad_op`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3956-L4029)) |
| quadNdx | 0-3 (broadcast), 0-2 (swap) | Quad index parameter |
| numWorkgroup | Various (16_1_1, 4_4_1, 128_1_1, 32_4_1) | Workgroup dimensions |
| mipLvl | 0-1 | Mip level for LOD tests |
| useLocalInvocationIndex | bool | Whether to use LocalInvocationIndex (quads variant) |

## Support Requirements

- **VK_KHR_compute_shader_derivatives** extension (all tests) — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2834](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2834)
- **computeDerivativeGroupLinear** feature — required when `DerivativeFeature::LINEAR` — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2841](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2841)
- **computeDerivativeGroupQuads** feature — required when `DerivativeFeature::QUADS` — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2846](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2846)
- **VK_EXT_mesh_shader** extension — required for `mesh` and `task` shader types — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2859](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2859)
- **meshAndTaskShaderDerivatives** property — required for mesh/task shaders — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2856](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2856)
- **meshShader** feature — required for `mesh` shader type — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2865](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2865)
- **taskShader** feature — required for `task` shader type — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2873](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2873)
- **Vulkan 1.1+** with **VK_SUBGROUP_FEATURE_BASIC_BIT** — required for [`verify_ndx`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3888-L3954) and [`quad_op`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3956-L4029) tests — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2881-L2887](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2881-L2887)
- **VK_SUBGROUP_FEATURE_QUAD_BIT** — required for [`quad_op`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3956-L4029) tests — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2891](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2891)
- SPIR-V 1.4 for mesh/task shaders, SPIR-V 1.3 for fragment shaders — [vktSpvAsmComputeShaderDerivativesTests.cpp#L3704-L3714](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3704-L3714)
- Non-VulkanSC only (observed in task description)

## Verification Methods

- **Derivative value tests**: Output buffer values are compared against expected derivative values computed on the CPU side, using a float comparison threshold ([`compareFloats`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L73-L77) with 0.01 threshold at [vktSpvAsmComputeShaderDerivativesTests.cpp#L73](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L73))
- **Verify NDX tests**: Invocation indices are verified by writing index values to output buffer and comparing against expected sequential values
- **Quad operation tests**: Output buffer values are verified against expected broadcast/swap results based on quad indices
- **LOD tests**: Sampled/query results are compared against expected values based on mip level configuration

## Notes

- This test group is non-VulkanSC only
- The [`meshAndTaskShaderDerivatives`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2853-L2857) property check is a runtime property query, not just a feature enable
- Workgroup X dimension must be a multiple of subgroupSize for [`verify_ndx`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L3888-L3954) tests (VUID-VkPipelineShaderStageCreateInfo-flags-02759) — [vktSpvAsmComputeShaderDerivativesTests.cpp#L2900-L2906](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderDerivativesTests.cpp#L2900-L2906)
