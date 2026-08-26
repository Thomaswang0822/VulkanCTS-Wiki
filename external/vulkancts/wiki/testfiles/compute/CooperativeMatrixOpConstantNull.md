## Overview

**Core question:** When a SPIR-V module declares an `OpConstantNull` cooperative matrix for one of the four operands (A, B, C) or for the result R, does the implementation honor the null cooperative-matrix value when it replaces a loaded operand/accumulator or the generated result, and do the stored matrices satisfy the checks implemented for the chosen target slot?

- [vktComputeCooperativeMatrixOpConstantNullTests.cpp](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1) is a delegated registration source under [compute.pipeline.cooperative_matrix](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6475-L6507). It registers one leaf per matrix target slot: `null_a`, `null_b`, `null_c`, and `null_r`.
- The file synthesizes SPIR-V 1.3 compute modules keyed by component-type tuple and scope; M, K, and N are specialization constants, so configurations that differ only in dimensions share a module. For the selected target slot the module substitutes `OpConstantNull` for the loaded or produced matrix and stores all four matrices to host-visible storage buffers.
- The test enumerates all viable configurations that the implementation accepts through `vkGetPhysicalDeviceCooperativeMatrixPropertiesKHR`, runs each one, and counts per-configuration mismatches against the target-specific expectation.
- `cooperative_matrix` is registered only under non-VulkanSC builds, so this subtree is non-VulkanSC.

## Background Knowledge

- **Cooperative matrix operands and result.** A cooperative matrix multiplication produces R from operands A, B, and an accumulator C using `R = A * B + C` (`OpCooperativeMatrixMulAddKHR`). A and B carry the operand roles `gl_MatrixUseA` and `gl_MatrixUseB`; C and R carry the accumulator role `gl_MatrixUseAccumulator`. Each matrix has a scope (`gl_ScopeSubgroup` here), a component type, and dimensions (M, K for A; K, N for B; M, N for C and R).
- **`OpConstantNull` value identity.** The SPIR-V spec defines `OpConstantNull` as producing the null value of its result type. For a cooperative matrix type the null value is the matrix whose every element is zero. Storing such a matrix to a storage buffer therefore writes zeros to every element. The test treats a stored matrix as null exactly when every element reads back as zero [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L694-L698](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L694-L698).
- **Subgroup scope.** The static configuration generator and the dynamic enumerator both require `scope == VK_SCOPE_SUBGROUP_KHR` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L95-L99](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L95-L99). All `OpConstantNull` cases therefore operate on subgroup-scoped cooperative matrices.
- **Null propagation in this test.** Replacing one operand with the null matrix propagates through the multiplication. With A null the product is null and the accumulator C is the result. With B null the product is null and the result equals C. With C null the result equals `A * B`. With R selected, the shader takes the null-result branch and does not execute the multiply-add branch. The test encodes these four propagation rules as its four leaves.

## Registration Hierarchy

```text
compute.pipeline.cooperative_matrix.op_constant_null
├── null_a
├── null_b
├── null_c
└── null_r
```

The `op_constant_null` subtree is registered by `createCooperativeMatrixOpConstantNullTests()` under the `cooperative_matrix` group [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866). It is delegated from the parent registration in [vktComputeCooperativeMatrixTests.cpp#L6485](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6485). The same four leaves appear under `compute.shader_object_spirv.cooperative_matrix.op_constant_null` and `compute.shader_object_binary.cooperative_matrix.op_constant_null` because the `compute` dispatcher replays `createChildren()` under every pipeline-construction root [vktComputeTests.cpp#L48-L64](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64), [vktComputeTests.cpp#L68-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85). Mustpass confirms all four leaves under all three pipeline-construction roots [compute.txt#L15770-L15773](../../../mustpass/main/vk-default/compute.txt#L15770-L15773), [compute.txt#L36055-L36058](../../../mustpass/main/vk-default/compute.txt#L36055-L36058), [compute.txt#L56327-L56330](../../../mustpass/main/vk-default/compute.txt#L56327-L56330).

## Parameter Dimensions and Observed Values

The full per-configuration matrix is built by intersecting a static enumeration with the implementation-reported dynamic configurations. The static enumeration iterates four component-type slots, three sizes (8, 16, 32), and applies four structural rules [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1243-L1304](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1243-L1304). The dynamic list comes from `vkGetPhysicalDeviceCooperativeMatrixPropertiesKHR` and is filtered through `isPossibleConfiguration()` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1218-L1233](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1218-L1233). Each viable configuration is logged with its component types, scope, and (M, N, K) tuple [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1384-L1392](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1384-L1392).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Target matrix slot | `null_a`, `null_b`, `null_c`, `null_r` | Selects which matrix operand or result the shader replaces with `OpConstantNull`; the other slots use loaded or multiplied values. | [registration table](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1850-L1855), [verifyResult branches](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1685-L1738) |
| Pipeline construction type | `pipeline`, `shader_object_spirv`, `shader_object_binary` | Inherited from the `compute` dispatcher; replayed for every pipeline-construction root. | [compute dispatcher](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L85), [case params](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1860-L1863) |
| Cooperative-matrix component types | `float16`, `float32`, `float64`, `sint8/16/32/64`, `uint8/16/32/64`, `bfloat16`, `float8_e4m3`, `float8_e5m2` (A/B must not be float32 or float64; float inputs require float accumulation; int inputs require int accumulation) | Determines the matrix type and the SPIR-V `OpConstantNull` instance emitted; the runtime omits configs whose types are not supported. | [PossibleTypes](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L70-L88), [static rules](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1249-L1304) |
| Cooperative-matrix sizes | `8`, `16`, `32` for M, N, K (multiples of 4 only) | Determines the matrix shape; sizes that are not multiples of 4 are pruned in the static enumeration. | [PossibleSizes and size rule](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1247-L1303) |
| Cooperative-matrix scope | `subgroup` only | The implementation-reported property must report `VK_SCOPE_SUBGROUP_KHR`; workgroup scope is not exercised here. | [scope filter](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L95-L99) |
| Per-component feature gates | `storageBuffer16BitAccess` + `shaderFloat16`; `shaderInt8` + `storageBuffer8BitAccess`; `shaderFloat8` + `shaderFloat8CooperativeMatrix`; `shaderBFloat16Type` + `shaderBFloat16CooperativeMatrix` | Required when the viable set contains 16-bit, 8-bit integer, float8, or bfloat16 components; failure to throw `NotSupportedError` keeps the case out of the run. | [checkSupport feature gates](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1178-L1215) |
| Pipeline-construction feature gate | `VK_EXT_shader_object` when construction type is shader-object | Required for shader-object SPIR-V or shader-object binary roots. | [checkSupport shader-object gate](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1170-L1174) |

## Behavior Parameters

The primary behavioral axis is the **target matrix slot**. The four leaves map one-to-one onto the four SPIR-V matrix roles in a cooperative-matrix multiplication. Each leaf changes which null-value branch is selected and which branch of `verifyResult()` runs. Only `null_b` and `null_c` compare R with a reference; `null_a` checks A and B's nullness but does not compare R, and `null_r` checks only R's nullness.

### null_a — Null operand A

`null_a` is registered with `Matrices::A` in the static name table [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1851](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1851). The shader declares an `OpConstantNull` of matrix type A and selects it through a push constant when the requested matrix equals `MAT_A` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L852](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L852), [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L960-L981](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L960-L981). Verification requires matrix A to be null and matrix B to be non-null [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1687-L1698](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1687-L1698). Although mathematically `A * B + C` should equal C when A is null, this branch does **not** call `cmp(C, R)`; therefore the leaf directly validates only A's and B's nullness, not R's value or C's value.

### null_b — Null operand B

`null_b` uses `Matrices::B` and the corresponding `OpConstantNull` of matrix type B [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1852](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1852), [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L857](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L857). The push-constant switch selects the null branch in `loadMatB_def` when the requested matrix equals `MAT_B` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L983-L1004](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L983-L1004). Verification requires matrix A to be non-null and matrix B to be null, and compares the stored R against the loaded C buffer [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1700-L1716](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1700-L1716). With B null, the multiplication is the zero product, leaving R equal to C; the leaf exercises the path that propagates null through the multiplication on the B side.

### null_c — Null accumulator C

`null_c` uses `Matrices::C` and the corresponding `OpConstantNull` of matrix type C [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1853](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1853), [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L862](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L862). The push-constant switch selects the null branch in `loadMatC_def` when the requested matrix equals `MAT_C` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1006-L1027](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1006-L1027). Verification requires matrix C to be null and compares the stored R against the host-side `A * B` reference [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1718-L1729](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1718-L1729). With C null, the multiplication contributes only `A * B`, so R must equal the product of the loaded A and B buffers computed in host code.

### null_r — Null result R

`null_r` uses `Matrices::R` and the corresponding `OpConstantNull` of the result matrix type [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1854](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1854), [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L866-L870](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L866-L870). The push-constant switch selects the null branch in `genMatR_def` when the requested matrix equals `MAT_R` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1029-L1053](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1029-L1053). Verification only checks that the stored R reads back as null [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1731-L1738](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1731-L1738). When R is selected, control takes the null branch and bypasses `OpCooperativeMatrixMulAddKHR`; the leaf checks that this null matrix survives `OpCooperativeMatrixStoreKHR`. It does not validate A, B, or C.

## Shader Analysis

The shader is generated as a SPIR-V 1.3 assembly string by `CoopMtxOpConstantNullCase::initPrograms()`, which feeds static configurations to `genShaderCode()`, deduplicates modules by the name derived from component types and scope, and registers each module with `SpirVAsmBuildOptions` for SPIR-V 1.3 plus `kScalarBlockLayout` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1352-L1382](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1352-L1382). The template declares one `OpConstantNull` per matrix type (A, B, C, and conditionally R), three `OpCooperativeMatrixLoadKHR` calls, each guarded by a push-constant branch that either loads from an SSBO or selects the null constant, and one `OpCooperativeMatrixMulAddKHR` call inside `genMatR_def` that is replaced with the null R when `MAT_R` is requested [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L779-L1054](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L779-L1054). The push constant is a five-`uint` struct whose first slot is the requested matrix and the next four slots are the `MAT_A`, `MAT_B`, `MAT_C`, `MAT_R` discriminators [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L170-L177](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L170-L177), [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L874-L878](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L874-L878). One walkthrough is used because a single representative module covers all four leaves; the only per-leaf variation is which `OpConstantNull` is selected by the push-constant switch.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.compute.pipeline.cooperative_matrix.op_constant_null.null_b
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `null_b` | The push constant selects matrix B, so `loadMatB_def` returns the B-type `OpConstantNull` instead of loading binding 1. |
| A and C operands | A and C are loaded normally from bindings 0 and 2 and participate in `OpCooperativeMatrixMulAddKHR`. |
| Result storage | The module stores R, C, B, and A to bindings 3, 2, 1, and 0, exposing the selected null operand and resulting matrix. |

#### Purpose

This walkthrough isolates the shader behavior exercised by the selected representative case.

#### Structural Design

1. `main` calls `loadMatA_def`, `loadMatB_def`, and `loadMatC_def`, then calls `genMatR_def` and stores R, C, B, and A to bindings 3, 2, 1, and 0.
2. Each loader compares push-constant member 0 (`REQUESTED_MATRIX`) with its matrix discriminator. For this `null_b` execution, the B comparison selects `%matB_null`; A and C are loaded with `OpCooperativeMatrixLoadKHR`.
3. `genMatR_def` compares the request with `MAT_R`. Because this case requests B, it executes `OpCooperativeMatrixMulAddKHR` with the loaded A, null B, and loaded C, then returns the result.
4. The complete module below is the mechanically specialized CTS template. Its `OpConstantNull` declarations and four store instructions are therefore the evidence for the generated artifact under audit.

#### Shader Code

This CTS case is generated directly as SPIR-V assembly and does not use GLSL or HLSL source. The complete generated assembly remains only in the final SPIR-V subsection.

#### Additional Info

- `CoopMtxOpConstantNullCase::initPrograms()` specializes the CTS assembly template for SPIR-V 1.3 and scalar block layout; the selected push-constant discriminator determines which cooperative matrix uses `OpConstantNull`.
- The same module contains null constants for A, B, C, and R, while the registered leaf controls which one replaces a load or generated result.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Selected null matrix | `null_a`, `null_b`, and `null_c` select the corresponding operand loader's `OpConstantNull`; `null_r` selects the null result after the multiply-add branch. | [push-constant selection in `genShaderCode()`](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L779-L1054) |
| Registered leaf | The four leaves keep the same generated module shape and vary which A, B, C, or R discriminator is requested at execution. | [case registration](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1352-L1382) |

#### SPIR-V

- Status: generated and validated
- Source: CTS `genShaderCode(conf)` SPIR-V assembly template, mechanically specialized for the configuration above
- Stage: `comp`
- Target SPIRV version: `spirv1.3`

The template was specialized mechanically, assembled with `spirv-as --target-env spv1.3`, validated with `spirv-val --target-env spv1.3`, and disassembled with `spirv-dis`. The `spirv-dis` output below is preserved unchanged.

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 150
; Schema: 0
               OpCapability Shader
               OpCapability VulkanMemoryModel
               OpCapability CooperativeMatrixKHR
               OpExtension "SPV_KHR_cooperative_matrix"
               OpExtension "SPV_KHR_vulkan_memory_model"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical Vulkan
               OpEntryPoint GLCompute %2 "main"
               OpExecutionMode %2 LocalSize 1 1 1
               OpDecorate %3 SpecId 1
               OpDecorate %4 SpecId 2
               OpDecorate %5 SpecId 3
               OpDecorate %_struct_6 Block
               OpMemberDecorate %_struct_6 0 Offset 0
               OpMemberDecorate %_struct_6 1 Offset 4
               OpMemberDecorate %_struct_6 2 Offset 8
               OpMemberDecorate %_struct_6 3 Offset 12
               OpMemberDecorate %_struct_6 4 Offset 16
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %_struct_8 Block
               OpMemberDecorate %_struct_8 0 Offset 0
               OpDecorate %9 Binding 0
               OpDecorate %9 DescriptorSet 0
               OpDecorate %_runtimearr_uint_0 ArrayStride 4
               OpDecorate %_struct_11 Block
               OpMemberDecorate %_struct_11 0 Offset 0
               OpDecorate %12 Binding 1
               OpDecorate %12 DescriptorSet 0
               OpDecorate %_runtimearr_uint_1 ArrayStride 4
               OpDecorate %_struct_14 Block
               OpMemberDecorate %_struct_14 0 Offset 0
               OpDecorate %15 Binding 2
               OpDecorate %15 DescriptorSet 0
               OpDecorate %_runtimearr_uint_2 ArrayStride 4
               OpDecorate %_struct_17 Block
               OpMemberDecorate %_struct_17 0 Offset 0
               OpDecorate %18 Binding 3
               OpDecorate %18 DescriptorSet 0
               OpDecorate %19 SpecId 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
         %22 = OpTypeFunction %void
       %bool = OpTypeBool
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
     %uint_3 = OpConstant %uint 3
     %uint_5 = OpConstant %uint 5
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
      %int_4 = OpConstant %int 4
          %3 = OpSpecConstant %int 1
          %4 = OpSpecConstant %int 1
          %5 = OpSpecConstant %int 1
         %36 = OpTypeCooperativeMatrixKHR %uint %uint_3 %3 %4 %uint_0
         %37 = OpConstantNull %36
%_ptr_Function_36 = OpTypePointer Function %36
         %39 = OpTypeFunction %void %_ptr_Function_36
         %40 = OpTypeCooperativeMatrixKHR %uint %uint_3 %4 %5 %uint_1
         %41 = OpConstantNull %40
%_ptr_Function_40 = OpTypePointer Function %40
         %43 = OpTypeFunction %void %_ptr_Function_40
         %44 = OpTypeCooperativeMatrixKHR %uint %uint_3 %3 %5 %uint_2
         %45 = OpConstantNull %44
%_ptr_Function_44 = OpTypePointer Function %44
         %47 = OpTypeFunction %void %_ptr_Function_44
         %48 = OpTypeFunction %44
  %_struct_6 = OpTypeStruct %uint %uint %uint %uint %uint
%_ptr_PushConstant__struct_6 = OpTypePointer PushConstant %_struct_6
         %50 = OpVariable %_ptr_PushConstant__struct_6 PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
%_runtimearr_uint = OpTypeRuntimeArray %uint
  %_struct_8 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer__struct_8 = OpTypePointer StorageBuffer %_struct_8
          %9 = OpVariable %_ptr_StorageBuffer__struct_8 StorageBuffer
         %53 = OpSpecConstantOp %uint IAdd %4 %uint_0
         %54 = OpSpecConstantOp %uint IAdd %4 %uint_0
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
 %_struct_11 = OpTypeStruct %_runtimearr_uint_0
%_ptr_StorageBuffer__struct_11 = OpTypePointer StorageBuffer %_struct_11
         %12 = OpVariable %_ptr_StorageBuffer__struct_11 StorageBuffer
         %56 = OpSpecConstantOp %uint IAdd %5 %uint_0
         %57 = OpSpecConstantOp %uint IAdd %5 %uint_0
%_runtimearr_uint_1 = OpTypeRuntimeArray %uint
 %_struct_14 = OpTypeStruct %_runtimearr_uint_1
%_ptr_StorageBuffer__struct_14 = OpTypePointer StorageBuffer %_struct_14
         %15 = OpVariable %_ptr_StorageBuffer__struct_14 StorageBuffer
         %59 = OpSpecConstantOp %uint IAdd %5 %uint_0
         %60 = OpSpecConstantOp %uint IAdd %5 %uint_0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%_ptr_StorageBuffer_uint_0 = OpTypePointer StorageBuffer %uint
%_ptr_StorageBuffer_uint_1 = OpTypePointer StorageBuffer %uint
%_ptr_StorageBuffer_uint_2 = OpTypePointer StorageBuffer %uint
%_ptr_Private_36 = OpTypePointer Private %36
         %66 = OpVariable %_ptr_Private_36 Private
%_ptr_Private_40 = OpTypePointer Private %40
         %68 = OpVariable %_ptr_Private_40 Private
%_ptr_Private_44 = OpTypePointer Private %44
         %70 = OpVariable %_ptr_Private_44 Private
%_ptr_Private_44_0 = OpTypePointer Private %44
         %72 = OpVariable %_ptr_Private_44_0 Private
%_runtimearr_uint_2 = OpTypeRuntimeArray %uint
 %_struct_17 = OpTypeStruct %_runtimearr_uint_2
%_ptr_StorageBuffer__struct_17 = OpTypePointer StorageBuffer %_struct_17
         %18 = OpVariable %_ptr_StorageBuffer__struct_17 StorageBuffer
         %74 = OpSpecConstantOp %uint IAdd %5 %uint_0
         %19 = OpSpecConstant %uint 1
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpSpecConstantComposite %v3uint %19 %uint_1 %uint_1
          %2 = OpFunction %void None %22
         %76 = OpLabel
         %77 = OpVariable %_ptr_Function_36 Function
         %78 = OpVariable %_ptr_Function_40 Function
         %79 = OpVariable %_ptr_Function_44 Function
         %80 = OpFunctionCall %void %81 %77
         %82 = OpLoad %36 %77
               OpStore %66 %82
         %83 = OpFunctionCall %void %84 %78
         %85 = OpLoad %40 %78
               OpStore %68 %85
         %86 = OpFunctionCall %void %87 %79
         %88 = OpLoad %44 %79
               OpStore %70 %88
         %89 = OpFunctionCall %44 %90
               OpStore %72 %89
         %91 = OpLoad %44 %72
         %92 = OpAccessChain %_ptr_StorageBuffer_uint_2 %18 %int_0 %uint_0
               OpCooperativeMatrixStoreKHR %92 %91 %int_0 %74 MakePointerAvailable|NonPrivatePointer %uint_5
         %93 = OpLoad %44 %70
         %94 = OpAccessChain %_ptr_StorageBuffer_uint_1 %15 %int_0 %uint_0
               OpCooperativeMatrixStoreKHR %94 %93 %int_0 %60 MakePointerAvailable|NonPrivatePointer %uint_5
         %95 = OpLoad %40 %68
         %96 = OpAccessChain %_ptr_StorageBuffer_uint_0 %12 %int_0 %uint_0
               OpCooperativeMatrixStoreKHR %96 %95 %int_0 %57 MakePointerAvailable|NonPrivatePointer %uint_5
         %97 = OpLoad %36 %66
         %98 = OpAccessChain %_ptr_StorageBuffer_uint %9 %int_0 %uint_0
               OpCooperativeMatrixStoreKHR %98 %97 %int_0 %54 MakePointerAvailable|NonPrivatePointer %uint_5
               OpReturn
               OpFunctionEnd
         %81 = OpFunction %void None %39
         %99 = OpFunctionParameter %_ptr_Function_36
        %100 = OpLabel
        %101 = OpAccessChain %_ptr_PushConstant_uint %50 %int_0
        %102 = OpLoad %uint %101
        %103 = OpAccessChain %_ptr_PushConstant_uint %50 %int_1
        %104 = OpLoad %uint %103
        %105 = OpIEqual %bool %102 %104
               OpSelectionMerge %106 None
               OpBranchConditional %105 %107 %108
        %107 = OpLabel
               OpStore %99 %37
               OpBranch %106
        %108 = OpLabel
        %109 = OpAccessChain %_ptr_StorageBuffer_uint %9 %int_0 %uint_0
        %110 = OpCooperativeMatrixLoadKHR %36 %109 %int_0 %54 MakePointerVisible|NonPrivatePointer %uint_5
               OpStore %99 %110
               OpBranch %106
        %106 = OpLabel
               OpReturn
               OpFunctionEnd
         %84 = OpFunction %void None %43
        %111 = OpFunctionParameter %_ptr_Function_40
        %112 = OpLabel
        %113 = OpAccessChain %_ptr_PushConstant_uint %50 %int_0
        %114 = OpLoad %uint %113
        %115 = OpAccessChain %_ptr_PushConstant_uint %50 %int_2
        %116 = OpLoad %uint %115
        %117 = OpIEqual %bool %114 %116
               OpSelectionMerge %118 None
               OpBranchConditional %117 %119 %120
        %119 = OpLabel
               OpStore %111 %41
               OpBranch %118
        %120 = OpLabel
        %121 = OpAccessChain %_ptr_StorageBuffer_uint_0 %12 %int_0 %uint_0
        %122 = OpCooperativeMatrixLoadKHR %40 %121 %int_0 %57 MakePointerVisible|NonPrivatePointer %uint_5
               OpStore %111 %122
               OpBranch %118
        %118 = OpLabel
               OpReturn
               OpFunctionEnd
         %87 = OpFunction %void None %47
        %123 = OpFunctionParameter %_ptr_Function_44
        %124 = OpLabel
        %125 = OpAccessChain %_ptr_PushConstant_uint %50 %int_0
        %126 = OpLoad %uint %125
        %127 = OpAccessChain %_ptr_PushConstant_uint %50 %int_3
        %128 = OpLoad %uint %127
        %129 = OpIEqual %bool %126 %128
               OpSelectionMerge %130 None
               OpBranchConditional %129 %131 %132
        %131 = OpLabel
               OpStore %123 %45
               OpBranch %130
        %132 = OpLabel
        %133 = OpAccessChain %_ptr_StorageBuffer_uint_1 %15 %int_0 %uint_0
        %134 = OpCooperativeMatrixLoadKHR %44 %133 %int_0 %60 MakePointerVisible|NonPrivatePointer %uint_5
               OpStore %123 %134
               OpBranch %130
        %130 = OpLabel
               OpReturn
               OpFunctionEnd
         %90 = OpFunction %44 None %48
        %135 = OpLabel
        %136 = OpVariable %_ptr_Function_44 Function
        %137 = OpAccessChain %_ptr_PushConstant_uint %50 %int_0
        %138 = OpLoad %uint %137
        %139 = OpAccessChain %_ptr_PushConstant_uint %50 %int_4
        %140 = OpLoad %uint %139
        %141 = OpIEqual %bool %138 %140
               OpSelectionMerge %142 None
               OpBranchConditional %141 %143 %144
        %143 = OpLabel
               OpStore %136 %45
               OpBranch %142
        %144 = OpLabel
        %145 = OpLoad %36 %66
        %146 = OpLoad %40 %68
        %147 = OpLoad %44 %70
        %148 = OpCooperativeMatrixMulAddKHR %44 %145 %146 %147
               OpStore %136 %148
               OpBranch %142
        %142 = OpLabel
        %149 = OpLoad %44 %136
               OpReturnValue %149
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Configuration enumeration.** For each invocation of `iterate()` the host selects one viable configuration from the intersection of the static enumeration and the implementation-reported dynamic configurations [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1765-L1784](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1765-L1784). The active configuration is logged as `Configuration: <N> A=<type> B=<type> C=<type> R=<type> Scope=Subgroup M=<M> K=<K> N=<N>` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1384-L1392](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1384-L1392). The host iterates `m_iteration` through every viable configuration across multiple `iterate()` calls.
- **Buffer setup.** Four `BufferWithMemory` SSBOs are created for A, B, C, and R, sized to `M * K`, `K * N`, `M * N`, and `M * N` elements respectively [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1454-L1496](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1454-L1496). A descriptor set with four storage-buffer bindings exposes them to the compute pipeline.
- **Pipeline setup.** The host compiles the generated SPIR-V with `SPIRV_VERSION_1_3` and `kScalarBlockLayout` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1355-L1358](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1355-L1358). The pipeline is constructed with the requested `ComputePipelineConstructionType`, so the same generated SPIR-V runs under `pipeline`, `shader_object_spirv`, and `shader_object_binary`. The pipeline receives a `VkSpecializationInfo` with `(subgroupSize, M, K, N)` and a five-`uint` push-constant range [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1500-L1532](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1500-L1532).
- **Input data.** A, C, and R are filled with pseudo-random values drawn from the per-component-type `ValueGenerator` set; B is filled with all 1.0 values to make the host-side reference predictable [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1547-L1586](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1547-L1586). The host then submits the command buffer with one `cmdDispatch(3, 1, 1)` and waits for completion [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1590-L1598](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1590-L1598).
- **Two identical target executions per configuration.** `iterate()` dispatches twice with `m_params.matrix` encoded in the push constant both times and verifies each result [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1765-L1818](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1765-L1818). The log labels the first run `normal multiplication` and the second `OpConstantNull`, but the inputs and selected target are the same; the first run is not a non-null baseline. A configuration contributes at most one to `m_failCount` even if both executions fail.
- **Result checking.** `verifyResult()` checks the stored matrices against the target-specific expectation: `null_a` requires A to be null and B to be non-null without comparing R; `null_b` requires A to be non-null and B to be null, then compares R against C; `null_c` requires C to be null and compares R against the host-computed `A * B`; `null_r` requires R to be null [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1656-L1762](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1656-L1762). Element-wise comparison uses `fabs(ref - y) < 1e-6f` and counts mismatches [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1669-L1682](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1669-L1682).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `null_a` | The shader stored a non-null matrix at binding 0, or B read back as null. This verifier branch does not compare R against C. |
| `null_b` | The shader stored a non-null matrix at binding 1, or A was also null, or R did not equal C because the implementation mishandled a null B operand. |
| `null_c` | The shader stored a non-null matrix at binding 2, or R did not equal the host-computed `A * B` because the implementation mishandled a null C accumulator. |
| `null_r` | The shader stored a non-null matrix at binding 3, indicating that the null result was not preserved through `OpCooperativeMatrixStoreKHR`. |

All four leaves share the same shader module and dispatch path; a single configuration's failure is reported as `M from N` with the count of failing viable configurations [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1830-L1839](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1830-L1839).

### Cause Analysis

#### Wrong matrix reads back as non-null

**Possible failure symptoms:** For `null_a`, `null_b`, `null_c`, or `null_r`, the corresponding storage buffer reads back as a matrix with at least one non-zero element. The host reports `"Matrix X must be null"` or `"Matrix X must not be null"` and increments the failure count [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1685-L1738](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1685-L1738).

**Possible implementation causes:** The SPIR-V validator or driver may have replaced `OpConstantNull` of a cooperative-matrix type with a default-constructed matrix that does not satisfy the all-zeros contract; the implementation may have folded the push-constant switch incorrectly and selected the wrong branch; the implementation may have optimized away the null assignment when the matrix is unused after the switch; or the host may have read back a stale allocation when an `invalidateAlloc` was missed. Source-level investigation is needed to determine which path was taken.

#### Wrong reference comparison

**Possible failure symptoms:** For `null_b`, the stored R does not match the loaded C matrix element-wise. For `null_c`, the stored R does not match the host-computed `A * B` reference element-wise. The host logs `Mismatch in <count> from <total> cells` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1754-L1760](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1754-L1760).

**Possible implementation causes:** The implementation may have used the loaded (non-null) matrix instead of the null constant at the multiply operand; the `OpCooperativeMatrixMulAddKHR` lowering may have skipped the null operand, leaving the product indeterminate; the storage-buffer readback may have returned stale data because `invalidateAlloc` was not invoked before the per-matrix read [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1394-L1426](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1394-L1426). Source-level investigation is needed to distinguish a shader-side defect from a host-side readback defect.

#### Pipeline construction mode unsupported

**Possible failure symptoms:** `checkSupport()` throws `NotSupportedError` when the pipeline construction type requires `VK_EXT_shader_object` and the implementation does not expose it [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1170-L1174](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1170-L1174). The leaf is skipped entirely.

**Possible implementation causes:** This is not a conformance failure: the registered leaf remains in the mustpass list but is reported as unsupported/skipped for that construction type, so its test body does not execute.

## Case Pruning

### Requirement-based pruning

- Each case requires `VkPhysicalDeviceCooperativeMatrixFeaturesKHR::cooperativeMatrix` and at least one viable configuration; otherwise `checkSupport()` throws `NotSupportedError` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1154-L1168](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1154-L1168).
- Pipeline construction type `shader_object_spirv` and `shader_object_binary` require `VK_EXT_shader_object` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1170-L1174](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1170-L1174).
- Viable configurations that contain 16-bit components require `storageBuffer16BitAccess` and `shaderFloat16` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1178-L1185](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1178-L1185).
- Viable configurations that contain 8-bit integer components require `shaderInt8` and `storageBuffer8BitAccess` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1187-L1194](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1187-L1194).
- Viable configurations that contain float8 components require `shaderFloat8`, `shaderFloat8CooperativeMatrix`, and `storageBuffer8BitAccess` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1196-L1206](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1196-L1206).
- Viable configurations that contain bfloat16 components require `shaderBFloat16Type` and `shaderBFloat16CooperativeMatrix` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1208-L1215](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1208-L1215).
- The dynamic configuration list is restricted to configurations whose component types are in `PossibleTypes` and whose scope is `VK_SCOPE_SUBGROUP_KHR` [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L95-L99](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L95-L99), [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1218-L1233](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1218-L1233).

### Design-based pruning

- The static enumeration forbids A and B with `float32` or `float64` component types because those types cannot appear as cooperative-matrix operands [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1249-L1255](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1249-L1255).
- The static enumeration requires A and B to share the float-or-int classification, and requires the accumulator C to match A and B's classification [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1265-L1286](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1265-L1286).
- The static enumeration keeps only matrix dimensions that are multiples of 4 [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1287-L1289](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1287-L1289).
- Only configurations that appear in both the static enumeration and the dynamic implementation report are considered viable, so the iteration never enters a configuration the implementation cannot run [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1328-L1337](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1328-L1337).

## Key Takeaways

- The four leaves correspond to the four matrix operand and result slots in a cooperative-matrix multiplication: `null_a` replaces the A operand, `null_b` replaces the B operand, `null_c` replaces the accumulator C, and `null_r` replaces the result R.
- The shader module is identical for all four leaves; the only difference is the value of the `REQUESTED_MATRIX` push-constant slot that drives the SPIR-V `OpSelectionMerge` branches.
- The null propagation rule is direct: with A or B null the multiplication contributes zero from the product and the result equals C; with C null the result equals `A * B`; with R selected the multiply-add branch is bypassed and a null result is stored.
- `cooperative_matrix` is non-VulkanSC only, so this subtree is absent from `compute_sc.txt`.
- The host's `Executor::getMatrix()` reads all four matrices back, so a null property of the target slot is directly observable on the host side.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Delegated factory | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1847-L1866) | Registers the four leaves under `op_constant_null` from the parent `cooperative_matrix` group. |
| Parent delegation call site | [vktComputeCooperativeMatrixTests.cpp#L6485](../../../modules/vulkan/compute/vktComputeCooperativeMatrixTests.cpp#L6485) | Wires the delegated factory into `createCooperativeMatrixTests`. |
| Category dispatcher | [vktComputeTests.cpp#L48-L64](../../../modules/vulkan/compute/vktComputeTests.cpp#L48-L64), [vktComputeTests.cpp#L68-L85](../../../modules/vulkan/compute/vktComputeTests.cpp#L68-L85) | Replays `createChildren()` under each pipeline-construction root, so the four leaves appear three times in mustpass. |
| Support checks | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1154-L1216](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1154-L1216) | API feature, viable-configuration count, shader-object, 16-bit, 8-bit int, float8, bfloat16 gating. |
| Configuration generators | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1218-L1311](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1218-L1311) | Dynamic and static cooperative-matrix property enumeration. |
| Configuration intersection | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1320-L1350](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1320-L1350) | Retains only configurations present in both lists. |
| SPIR-V assembly generation | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L715-L1140](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L715-L1140) | Builds the SPIR-V 1.3 template with `OpConstantNull` declarations per matrix type. |
| Shader registration | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1352-L1382](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1352-L1382) | Adds SPIR-V sources and SPIR-V 1.3 build options. |
| Buffer and pipeline setup | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1428-L1538](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1428-L1538) | Allocates four SSBOs, descriptor set, push-constant range, and specialization constants. |
| Dispatch and submission | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1540-L1599](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1540-L1599) | Fills buffers, dispatches, and waits for completion. |
| Verification logic | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1656-L1762](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1656-L1762) | Target-specific null checks and per-element comparison against host-side reference. |
| Per-iteration driver | [vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1765-L1843](../../../modules/vulkan/compute/vktComputeCooperativeMatrixOpConstantNullTests.cpp#L1765-L1843) | Iterates viable configurations, logs outcomes, accumulates failure count. |
| Mustpass coverage | [compute.txt#L15770-L15773](../../../mustpass/main/vk-default/compute.txt#L15770-L15773), [compute.txt#L36055-L36058](../../../mustpass/main/vk-default/compute.txt#L36055-L36058), [compute.txt#L56327-L56330](../../../mustpass/main/vk-default/compute.txt#L56327-L56330) | Confirms all four leaves under all three pipeline-construction roots. |
