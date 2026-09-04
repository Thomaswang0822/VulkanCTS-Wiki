## Overview

**Core question:** Do the `basic`, `longvec`, `matmul`, and `training` test families produce the expected vector or matrix values across their generated cooperative-vector operations?

- [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp) implements the `basic`, `longvec`, `matmul`, and `training` families. The category dispatcher calls the shared factory once with `false` for `basic`, once with `true` for `longvec`, and calls separate factories for `matmul` and `training` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L37-L50).
- The `basic` and `longvec` factory combines an operation, input and output component types, vector component counts, storage class, and shader stage. The `matmul` and `training` factories add matrix layouts, activation modes, result-address modes, and their own operation/size tables. Each factory prunes combinations that do not match the operation or the selected execution path [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3909-L4172) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4185-L4670) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4671-L4904).

- Each case generates GLSL, runs the operation in a compute, graphics, mesh, tessellation, or ray-tracing stage, and compares the output buffer with a CPU reference.
- `basic` enables `GL_NV_cooperative_vector` and uses `coopvecNV<T, N>` where appropriate. `longvec` enables `GL_EXT_long_vector` and uses `vector<T, N>`. `matmul` and `training` use the NV cooperative-vector matrix operations and training-layout paths [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L512-L640) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4185-L4904).

## Background Knowledge

- A cooperative vector is a shader vector type intended for small neural-network workloads. The NV extension leaves supported component combinations implementation-dependent, so the test checks advertised `VkCooperativeVectorPropertiesNV` entries before it runs a case.
- The EXT long-vector path uses the `vector<T, N>` GLSL type. It has its own feature and maximum-component checks. It shares the basic operation matrix with `basic`, but it does not share the NV cooperative-vector extension path.
- Each invocation owns one logical input and output vector. The host pads vector storage to 16-byte boundaries, while workgroup cases use shader-local shared arrays and synchronization barriers.

## Registration Hierarchy

```text
cooperative_vector
├── basic
├── longvec
├── matmul
└── training
```

The four direct children above come from the two calls to `createCooperativeVectorBasicTests` and the calls to `createCooperativeVectorMatrixMulTests` and `createCooperativeVectorTrainingTests` [vktCooperativeVectorTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L37-L50). `basic` and `longvec` share the vector-operation factory, while `matmul` and `training` are separate generated families implemented in the same source file [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4185-L4190) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4671-L4685). Each family expands below its direct child into operation, type, storage, component-count, layout, activation, and stage paths; these generated axes are described in the tables below rather than expanded in the parseable tree.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `basic`, `longvec`, `matmul`, `training` | Selects the vector-operation path, NV matrix-multiply path, or NV training path. | [category child factories](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L41-L49) |
| Operation | `basic`/`longvec`: `length`, `constant`, `convert`, `composite`, `composite_rvalue`, `vector_extract`, `add`, `sub`, `mul`, `div`, `negate`, `vectortimesscalar`, `exp`, `log`, `tanh`, `atan`, `min`, `max`, `clamp`, `step`, `fma`, `func`, `and`, `or`, `xor`, `not`, `shl`, `shr`, `composite_array`; `matmul`: `matrixmul`, `matrixmuladd`, `matrixmuladdtranspose`, `matrixmul3`, `matrixmul2addmul2`, `matrixmul2add`, `matrixmultrainingbias`; `training`: `reducesum`, `outerproduct` | Selects the generated vector expression, matrix operation, or training operation under test. | [basic operation cases](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3920-L3950), [matmul operation cases](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4197-L4205), [training operation cases](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4682-L4685) |
| Component type pair | `float16_float16`, `uint8_uint8`, `uint8_uint32`, `uint32_uint8`, `sint8_sint8`, `sint8_sint32`, `sint32_sint8`, `float16_uint8`, `float16_sint8`, `float16_uint32`, `float16_sint32`, `uint8_float16`, `sint8_float16`, `uint32_float16`, `sint32_float16`, `float16_float32`, `float32_float16`, `float32_float32` | Selects input and output representation. Conversion uses unlike types; most other basic cases require matching types. | [dtCases](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3952-L3971) |
| Vector size | `components1`, `components2`, `components3`, `components4`, `components5`, `components6`, `components7`, `components8`, `components9`, `components31`, `components65`, `components1024` | Sets the input and output component count and therefore the padded buffer stride and generated vector type. | [sizeCases](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3973-L3980) |
| Storage class | `buffer`, `workgroup`, `buffer_varptr`, `workgroup_varptr`, `physical_buffer` | Selects direct SSBO access, shared workgroup staging, variable-pointer access, or buffer-reference addresses. | [scCases](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3982-L3988) |
| Shader stage | `compute`, `raygen`, `isect`, `ahit`, `chit`, `miss`, `callable`, `vertex`, `fragment`, `geometry`, `tessctrl`, `tesseval`, `task`, `mesh` | Selects the pipeline and the formula that maps an invocation to its vector slot. | [stageCases](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3990-L4005) |
| Storage, layout, activation, and stage | Factory-specific combinations, including `buffer`, `workgroup`, `physical_buffer`, `trainingOptimal`, activation names, and the registered shader stages | Selects resource transport, matrix interpretation, post-operation activation, result addressing, and pipeline stage. | [matmul matrix](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4279-L4336), [training matrix](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4722-L4759) |

The `vk-default` mustpass file contains 6,554 paths for each of `basic` and `longvec`, 25,282 `matmul` paths, and 15,008 `training` paths. Its entries show the generated path order, for example `dEQP-VK.cooperative_vector.basic.add.float16_float16.buffer.components1.compute`, `dEQP-VK.cooperative_vector.matmul.64b_indexing.muladd_ahit71x2`, and `dEQP-VK.cooperative_vector.training.64b_indexing.outerproduct_ahit71x2` [cooperative-vector.txt](../../../mustpass/main/vk-default/cooperative-vector.txt).

## Behavior Parameters

The primary behavioral axis is the test family. `basic` and `longvec` change the shader type system and extension feature, while `matmul` and `training` exercise NV cooperative-vector matrix operations and training layouts. Operation, type, size, storage, layout, activation, result addressing, and stage remain important generated axes within each family.

### basic: NV cooperative-vector operations

`basic` enables `GL_NV_cooperative_vector`. For ordinary basic operations, the generated shader uses `coopvecNV<T, N>` and calls `coopVecLoadNV` and `coopVecStoreNV` when vectors move between storage buffers and shader variables. The host accepts an NV case only when the device advertises cooperative-vector properties covering the selected input and output types [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L317-L327) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L406-L482).

The operation leaves cover vector length, constants, conversions, construction and extraction, arithmetic, elementary functions, FMA, function parameters, and integer bit operations. The host computes the matching scalar or vector reference and checks the stored result component by component.

### longvec: EXT long-vector operations

`longvec` enables `GL_EXT_long_vector` and generates `vector<T, N>` declarations. It loads and stores a complete long vector through the buffer element expression, with `std140` layout for the generated vector buffer blocks [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L579-L640).

The factory reuses the same operation, type, size, storage, and stage tables. Its support check uses `longVector` and `maxVectorComponents` instead of the NV cooperative-vector feature and maximum component property [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L329-L339). The source marks this mode as limited to the basic operation matrix.

### matmul: NV cooperative-vector matrix operations

`matmul` is a separate direct family created by `createCooperativeVectorMatrixMulTests`. It generates matrix multiply, multiply-add, transpose, chained multiply, and training-bias forms from the `ttCases` table. The matrix input, interpretation, output type, matrix layout, activation, storage class, invocation stage, and control-flow or offset modes are all selected by the generated case. The source prunes unsupported layout/type combinations, limits expensive activation and storage variants, and keeps the training-bias form on `trainingOptimal` layouts [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4185-L4205) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4379-L4555).

### training: NV cooperative-vector training operations

`training` is a separate direct family created by `createCooperativeVectorTrainingTests`. It covers `reducesum` and `outerproduct` with FP16 or FP32 data, training-optimal matrix layout, buffer or address-based storage, result-address modes, control-flow modes, and the generated shader stages. The outer-product path fixes its input type to FP16, while the reduction and outer-product size tables use different shape interpretations [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4671-L4759) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4762-L4853).

## Shader Analysis

The source builds shader strings in `CooperativeVectorTestCase::initPrograms`. The representative walkthrough below uses the exact registered `basic` add case and its compute-stage shape. The SPIR-V artifact comes from the local `glslangValidator`, `spirv-val`, and `spirv-dis` workflow with target `spirv1.4`; the compact reconstruction keeps the relevant extension, bindings, vector loads, add, and store.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.cooperative_vector.basic.add.float16_float16.buffer.components1.compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `basic` | Uses `GL_NV_cooperative_vector` and `coopvecNV` operations. |
| `add` | Generates a vector addition and checks the sum against the host reference. |
| `float16_float16` | Reads and writes FP16 components without a conversion between input and output types. |
| `buffer` | Uses storage-buffer bindings for both inputs and the output. |
| `components1` | Gives each invocation a one-component vector. |
| `compute` | Uses a compute shader with an 8 by 8 local size in the representative reconstruction. |

#### Purpose

This shader checks that an NV cooperative vector can load two FP16 values, add them, and store the result at the invocation's output slot.

#### Structural Design

| Phase | Shader action | Test meaning |
|-------|---------------|--------------|
| 1 | Read `gl_LocalInvocationIndex` | Select the invocation's input and output slot. |
| 2 | Load `a` from binding 0 and `b` from binding 1 | Exercise cooperative-vector buffer loads. |
| 3 | Evaluate `o = a + b` | Exercise the selected vector operation. |
| 4 | Store `o` to binding 3 | Produce the value that the host checks. |

#### Shader Code

Reconstructed GLSL for this registered path:

```glsl
#version 460 core
#pragma use_vulkan_memory_model
#extension GL_KHR_shader_subgroup_basic : enable
#extension GL_KHR_memory_scope_semantics : enable
#extension GL_EXT_nonuniform_qualifier : enable
#extension GL_EXT_shader_explicit_arithmetic_types : enable
#extension GL_EXT_buffer_reference : enable
#extension GL_NV_cooperative_vector : enable
layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;
/// Binding 0 supplies the first FP16 vector for each invocation.
layout(set = 0, binding = 0) readonly buffer InputA { float16_t x[]; } inputA;
/// Binding 1 supplies the second FP16 vector for each invocation.
layout(set = 0, binding = 1) readonly buffer InputB { float16_t x[]; } inputB;
/// Binding 3 receives the vector result for host-side comparison.
layout(set = 0, binding = 3) coherent buffer Output { float16_t x[]; } outputO;
coopvecNV<float16_t, 1> a;
coopvecNV<float16_t, 1> b;
coopvecNV<float16_t, 1> o;
void main()
{
    uint i = gl_LocalInvocationIndex;
    /// Each one-component vector occupies one FP16 element in this simplified case.
    coopVecLoadNV(a, inputA.x, i * 2);
    coopVecLoadNV(b, inputB.x, i * 2);
    o = a + b;
    coopVecStoreNV(o, outputO.x, i * 2);
}
```

#### Additional Info

- `initPrograms` adds the source-controlled `ShaderBuildOptions` with SPIR-V 1.4 for the test shader [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1593-L1616).
- The complete CTS generator also emits stage-specific declarations, padded offsets, specialization constants, and optional workgroup or physical-buffer paths. The representative code shows the direct compute-buffer branch, not every generated branch.
- The generated source uses byte offsets for NV cooperative-vector loads and stores. The host allocates padded vectors and supplies the matching byte-stride values [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L676-L693).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test family | `longvec` replaces `coopvecNV<T, N>` with `vector<T, N>`, enables `GL_EXT_long_vector`, and uses complete vector element loads and stores. | [vector type and extension selection](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L512-L525) [longvec declarations](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L579-L640) |
| Operation | The body selects `length`, conversion, construction, arithmetic, elementary functions, function calls, or bitwise and shift expressions. | [operation generation](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1186-L1295) |
| Component type pair | GLSL component types and permitted operation set change with the input and output pair. Integer cases omit floating-point functions; floating-point cases omit bitwise and shift operations. | [type pruning](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4055-L4130) |
| Vector size | `K`, `N`, vector declarations, padded element counts, and load/store offsets change with `components1` through `components1024`. | [size constants and padding](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L676-L693) |
| Storage class | Buffer cases use SSBO members; workgroup cases copy through shared arrays and barriers; physical-buffer cases use buffer references and a device-address parameter buffer. | [resource declarations](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L652-L710) [load and store paths](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L890-L920) |
| Shader stage | Invocation indexing changes to built-ins for compute, graphics, tessellation, mesh, and ray-tracing stages. | [stage index generation](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L717-L756) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 61
; Schema: 0
               OpCapability Shader
               OpCapability Float16
               OpCapability StorageBuffer16BitAccess
               OpCapability VulkanMemoryModel
               OpCapability CooperativeVectorNV
               OpExtension "SPV_KHR_vulkan_memory_model"
               OpExtension "SPV_NV_cooperative_vector"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical Vulkan
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationIndex %inputA %a %inputB %outputO
               OpExecutionMode %main LocalSize 8 8 1
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpSourceExtension "GL_NV_cooperative_vector"
               OpName %main "main"
               OpName %i "i"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %tempArg "tempArg"
               OpName %InputA "InputA"
               OpMemberName %InputA 0 "x"
               OpName %inputA "inputA"
               OpName %a "a"
               OpName %tempArg_0 "tempArg"
               OpName %InputB "InputB"
               OpMemberName %InputB 0 "x"
               OpName %inputB "inputB"
               OpName %b "b"
               OpName %o "o"
               OpName %Output "Output"
               OpMemberName %Output 0 "x"
               OpName %outputO "outputO"
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %_runtimearr_half ArrayStride 2
               OpDecorate %InputA Block
               OpMemberDecorate %InputA 0 NonWritable
               OpMemberDecorate %InputA 0 Offset 0
               OpDecorate %inputA NonWritable
               OpDecorate %inputA Binding 0
               OpDecorate %inputA DescriptorSet 0
               OpDecorate %_runtimearr_half_0 ArrayStride 2
               OpDecorate %InputB Block
               OpMemberDecorate %InputB 0 NonWritable
               OpMemberDecorate %InputB 0 Offset 0
               OpDecorate %inputB NonWritable
               OpDecorate %inputB Binding 1
               OpDecorate %inputB DescriptorSet 0
               OpDecorate %_runtimearr_half_1 ArrayStride 2
               OpDecorate %Output Block
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %outputO Binding 3
               OpDecorate %outputO DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
       %half = OpTypeFloat 16
     %uint_1 = OpConstant %uint 1
         %14 = OpTypeVectorIdEXT %half %uint_1
%_ptr_Function_14 = OpTypePointer Function %14
%_runtimearr_half = OpTypeRuntimeArray %half
     %InputA = OpTypeStruct %_runtimearr_half
%_ptr_StorageBuffer_InputA = OpTypePointer StorageBuffer %InputA
     %inputA = OpVariable %_ptr_StorageBuffer_InputA StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer__runtimearr_half = OpTypePointer StorageBuffer %_runtimearr_half
     %uint_2 = OpConstant %uint 2
%_ptr_Private_14 = OpTypePointer Private %14
          %a = OpVariable %_ptr_Private_14 Private
%_runtimearr_half_0 = OpTypeRuntimeArray %half
     %InputB = OpTypeStruct %_runtimearr_half_0
%_ptr_StorageBuffer_InputB = OpTypePointer StorageBuffer %InputB
     %inputB = OpVariable %_ptr_StorageBuffer_InputB StorageBuffer
%_ptr_StorageBuffer__runtimearr_half_0 = OpTypePointer StorageBuffer %_runtimearr_half_0
%_runtimearr_half_1 = OpTypeRuntimeArray %half
     %Output = OpTypeStruct %_runtimearr_half_1
%_ptr_StorageBuffer_Output = OpTypePointer StorageBuffer %Output
    %outputO = OpVariable %_ptr_StorageBuffer_Output StorageBuffer
     %uint_5 = OpConstant %uint 5
%_ptr_StorageBuffer__runtimearr_half_1 = OpTypePointer StorageBuffer %_runtimearr_half_1
     %v3uint = OpTypeVector %uint 3
     %uint_8 = OpConstant %uint 8
     %gl_WorkGroupSize = OpConstantComposite %v3uint %uint_8 %uint_8 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_uint Function
    %tempArg = OpVariable %_ptr_Function_14 Function
  %tempArg_0 = OpVariable %_ptr_Function_14 Function
          %b = OpVariable %_ptr_Function_14 Function
          %o = OpVariable %_ptr_Function_14 Function
         %11 = OpLoad %uint %gl_LocalInvocationIndex
               OpStore %i %11
         %24 = OpAccessChain %_ptr_StorageBuffer__runtimearr_half %inputA %int_0
         %25 = OpLoad %uint %i
         %27 = OpIMul %uint %25 %uint_2
         %28 = OpCooperativeVectorLoadNV %14 %24 %27 None
               OpStore %tempArg %28
         %31 = OpLoad %14 %tempArg
               OpStore %a %31
         %38 = OpAccessChain %_ptr_StorageBuffer__runtimearr_half_0 %inputB %int_0
         %39 = OpLoad %uint %i
         %40 = OpIMul %uint %39 %uint_2
         %41 = OpCooperativeVectorLoadNV %14 %38 %40 None
               OpStore %tempArg_0 %41
         %43 = OpLoad %14 %tempArg_0
               OpStore %b %43
         %45 = OpLoad %14 %a
         %46 = OpLoad %14 %b
         %47 = OpFAdd %14 %45 %46
               OpStore %o %47
         %48 = OpLoad %14 %o
         %55 = OpAccessChain %_ptr_StorageBuffer__runtimearr_half_1 %outputO %int_0
         %56 = OpLoad %uint %i
         %57 = OpIMul %uint %56 %uint_2
               OpCooperativeVectorStoreNV %55 %57 %48 MakePointerAvailable|NonPrivatePointer %uint_5
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The instance derives `N` and `K` from the case, rounds vector storage to 16-byte boundaries, and allocates host-visible storage buffers for input A, input B, input C, and output. The physical-buffer variant also allocates a buffer containing the four device addresses [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1834-L2041).
- The host initializes the buffers with deterministic random data from seed `1234`. It builds a descriptor set with storage-buffer bindings 0 through 3, or passes the address buffer at binding 4 for `physical_buffer` [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1805-L1810) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2084-L2105).
- The test submits a compute, graphics, mesh, tessellation, or ray-tracing pipeline. Specialization data supplies the local dimensions and generated offsets [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2175-L2202).
- Workgroup storage uses a barrier before the shader reads shared input and another before it stores the output. Direct storage paths use the selected vector load and store form [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L890-L920) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1535-L1566).
- After completion, the host reads each output vector. Integer cases use exact comparisons after truncation. Floating-point cases use exact comparisons where appropriate and source-defined relative-error checks for division and elementary functions [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2990-L3071).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Incorrect `VK_NV_cooperative_vector` type or operation lowering, unsupported advertised type combination accepted by the test, vector load/store addressing or padding error, stage or storage-class transport error, or host reference mismatch. |
| `longvec` | Incorrect `GL_EXT_long_vector` type or operation lowering, long-vector load/store or std140 layout error, stage or storage-class transport error, or host reference mismatch. |
| `matmul` | Incorrect cooperative-vector matrix operation lowering, matrix interpretation or layout handling, activation or transpose handling, matrix addressing, stage/storage transport, or host reference mismatch. |
| `training` | Incorrect training operation lowering, training-optimal layout handling, reduction or outer-product addressing, result-address/control-flow handling, stage/storage transport, or host reference mismatch. |

### Cause Analysis

#### NV cooperative-vector operation or support matching

**Possible failure symptoms:** A `basic` case produces output components different from the operation's CPU reference, or the shader cannot use the selected advertised type combination.

**Possible implementation causes:** The failure can come from lowering an NV cooperative-vector operation or from a mismatch between the advertised `VkCooperativeVectorPropertiesNV` combination and shader behavior. The test's support check and the specification's property model provide the evidence boundary; source inspection cannot identify a particular driver or hardware defect.

#### EXT long-vector operation or layout

**Possible failure symptoms:** A `longvec` case stores a value that differs from the CPU reference, or the output is displaced when the vector has multiple components.

**Possible implementation causes:** The implementation may lower the `vector<T, N>` operation incorrectly or apply a different layout or element stride from the generated `std140` buffer declaration. The page does not assign the cause to a particular implementation layer without a failing case trace.

#### Vector transport and invocation indexing

**Possible failure symptoms:** The arithmetic value is correct for one slot but wrong for other invocations, or only workgroup, variable-pointer, physical-buffer, or non-compute cases fail.

**Possible implementation causes:** The symptom points to one of the source-controlled transport paths, such as 16-byte padding, shared-memory staging and barriers, device-address indirection, or the stage-specific global invocation index. A host-side reference mismatch remains possible because the host computes the expected slot and value from the same case definition.

#### Host reference comparison

**Possible failure symptoms:** The test reports a component mismatch, including a mismatch only for conversion, integer truncation, elementary-function tolerance, or floating-point quantization cases.

- **Possible implementation causes:** The shader result, host conversion path, or comparison tolerance may disagree. The FP8 retry described in the generic result-checking code is matrix-specific and is not part of the `basic`/`longvec` operation matrix [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3138-L3440) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3920-L3950).

## Case Pruning

### Requirement-based pruning

- All cases require Vulkan 1.1 and buffer device address support. `basic` requires `cooperativeVector`, a supported component count, and advertised support for the selected input and output types. `longvec` requires `longVector` and its maximum component count [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L310-L339) [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L406-L482).
- Variable-pointer storage requires `variablePointers`. Ray-tracing stages require acceleration structures and ray-tracing pipeline support. Mesh and task stages require the corresponding mesh shader features. FP16 cases require shader float16 support [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L341-L390).
- Integer cases remove floating-point functions and FMA. Floating-point cases remove bitwise and shift operations. `convert` removes equal-type pairs, while other non-matrix basic operations remove unequal-type pairs [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4055-L4130).

### Design-based pruning

- Workgroup and workgroup-variable-pointer storage run only in compute because the generated shared arrays depend on compute local invocation IDs.
- Non-compute integer cases retain reduced component counts, and non-compute cases generally keep `components31`; the source keeps `components65` for selected signed integer coverage.
- `components1024` is removed from workgroup storage because the shared arrays would use too much memory. `length` with `components1024` is also removed because it overflows some types.
- Physical-buffer and buffer-variable-pointer basic cases run only at `components31` to keep the matrix bounded; workgroup-variable-pointer cases are not covered by this particular size restriction. The resulting mustpass list records the pruned set rather than the full Cartesian product [vktCooperativeVectorBasicTests.cpp](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L4029-L4069).

## Key Takeaways

- `basic` and `longvec` validate the same basic operation matrix through different GLSL vector types and feature gates.
- The generated path tests more than the arithmetic expression. Padding, storage class, device addresses, invocation indexing, and stage-specific pipeline setup all affect the value that reaches the host comparison.
- The source prunes unsupported and intentionally expensive combinations, so the registered mustpass entries are the authoritative executed set.
- A failure in `basic` points first to the NV cooperative-vector path; a failure in `longvec` points first to the EXT long-vector path. Both families can also expose shared transport or host-reference problems described in `## Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Category dispatcher | [vktCooperativeVectorTests.cpp#L37-L58](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorTests.cpp#L37-L58) | Registers `basic` and `longvec` as direct children. |
| Factory and operation matrix | [createCooperativeVectorBasicTests#L3909-L4172](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L3909-L4172) | Defines names, generated dimensions, and basic-family pruning. |
| Support and property checks | [CooperativeVectorTestCase::checkSupport#L310-L483](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L310-L483) | Enforces feature, limit, and advertised combination requirements. |
| Type and extension generation | [makeVecType and initPrograms#L512-L640](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L512-L640) | Distinguishes `coopvecNV` from `vector` and emits declarations. |
| Operation emission | [operation switch#L1186-L1295](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1186-L1295) | Emits the selected basic operation. |
| Runtime resources | [iterate setup#L1796-L2352](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L1796-L2352) | Allocates, initializes, binds, and specializes resources. |
| Result checks | [iterate checking#L2990-L3440](../../../modules/vulkan/cooperative_vector/vktCooperativeVectorBasicTests.cpp#L2990-L3440) | Computes references and applies source-defined comparison rules. |
| Current Vulkan semantics | [shader cooperative vectors](../../../../vulkan-docs/src/chapters/shaders.adoc#_cooperative_vectors) | Defines cooperative-vector purpose, supported combinations, and matrix-related interfaces. |
| Mustpass registration | [cooperative-vector.txt](../../../mustpass/main/vk-default/cooperative-vector.txt) | Lists the registered `basic` and `longvec` executable paths. |
