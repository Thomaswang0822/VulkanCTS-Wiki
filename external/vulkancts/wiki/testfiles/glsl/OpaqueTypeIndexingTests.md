## Overview

**Core question:** Do shaders select the correct opaque resource when an array index comes from a literal, a constant expression, a uniform, or a dynamically uniform shader input?

- [`vktOpaqueTypeIndexingTests.cpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L150-L2048) implements `glsl.opaque_type_indexing` for combined image samplers, uniform-buffer block instances, storage-buffer block instances, and storage-buffer-backed atomic counters.
- The generator applies four index-expression forms across six shader stages. Sampler test case leaves use vertex, fragment, and compute stages; block and atomic-counter leaves use all six stages.
- Each test runs through the shared shader-executor framework. The host checks sampled texels, block values, or atomic results rather than treating successful compilation and execution as sufficient.
- The Vulkan default mustpass list contains 372 test case leaves: 276 sampler leaves and 24 leaves in each of the four other test families ([mustpass range](../../../mustpass/main/vk-default/glsl.txt#L10489-L10860)).

## Background Knowledge

- Opaque GLSL types represent resources whose contents cannot be copied into ordinary shader variables. The shader accesses them through operations such as texture sampling or by selecting an interface-block instance.
- Vulkan descriptor arrays contain multiple descriptors at one binding. An index selects one descriptor for a shader access. Runtime indexing of sampled-image, uniform-buffer, and storage-buffer descriptor arrays has separate device feature bits.
- A dynamically uniform expression has the same value for the relevant shader invocations even though the compiler cannot treat it as a compile-time constant. This permits resource selection without allowing different invocations to diverge onto unrelated descriptors.
- An atomic add updates one counter indivisibly and returns its previous value. Concurrent increments can arrive in any order, so a correct oracle must accept the legal orderings rather than expect one invocation order.

## Registration Hierarchy

```text
glsl.opaque_type_indexing
├── sampler
├── ubo
├── ssbo
├── ssbo_storage_buffer_decoration
└── atomic_counter
```

`createOpaqueTypeIndexingTests()` returns the `opaque_type_indexing` group, and the Vulkan test package places that group directly under `glsl` ([factory](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2045-L2048), [package registration](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1277)). The registration loop creates the five test families shown above ([family generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1918-L2041)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `sampler`, `ubo`, `ssbo`, `ssbo_storage_buffer_decoration`, `atomic_counter` | Selects the opaque resource form, descriptor layout, shader operation, and host oracle. | [Family registration](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1944-L2040) |
| Index expression | `const_literal`, `const_expression`, `uniform`, `dynamically_uniform` | Changes where the resource index comes from and whether the host must provide an index buffer or shader input. | [Index table](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1920-L1931) |
| Shader stage | `vertex`, `fragment`, `geometry`, `tess_ctrl`, `tess_eval`, `compute` | Moves the same resource-selection logic through different shader-executor paths. Sampler leaves use only vertex, fragment, and compute. | [Stage table and sampler filter](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1933-L1942), [sampler stage filter](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1982-L1992) |
| Sampler type | 23 float, shadow, signed-integer, and unsigned-integer sampler types | Changes image dimensionality, coordinate shape, image format, filtering, and output type. | [Sampler type table](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1946-L1970), [type mapping](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L289-L401) |
| Sampler workload | 8 samplers, 4 lookups, 64 invocations | Each lookup selects one of eight one-texel images, and every invocation must produce an accepted value. | [Sampler constants](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L636-L644) |
| Block workload | 4 block instances, 4 reads, 32 invocations | Each read selects one separately backed `uint` block instance. | [Block constants](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1138-L1146) |
| Atomic workload | 4 counters, 4 operations, 32 observed invocations | Each operation selects one counter, increments it, and returns the old counter value. | [Atomic constants](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1511-L1519) |
| Extra resource set | Descriptor set 1 | Keeps tested resources separate from the shader executor's input and output buffers in set 0. | [Set definition](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.hpp#L87-L91) |

The sampler path has the form `sampler/<index expression>/<shader stage>/<sampler type>`. The other test families use flat test case leaf names of the form `<index expression>_<shader stage>` ([sampler generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1972-L2003), [block and atomic generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2007-L2038)).

The source seeds each test's pseudo-random indices and values from its parameters. Repeated runs of the same test case leaf therefore use the same generated selections and resource contents ([sampler generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1070-L1083), [block generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1441-L1457), [atomic generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1837-L1845)).

## Behavior Parameters

The primary behavioral axis is the test family. It determines which opaque resource the shader selects and which independent result check the host applies. The four index-expression values then exercise different compiler and descriptor-indexing paths within that behavior.

### `sampler`: select and sample a combined image sampler

The shader declares an array of eight combined image samplers and performs four texture lookups. Each array element refers to a separate one-texel image, so selecting the wrong descriptor changes the sampled value. The 23 sampler types cover float, shadow, signed-integer, and unsigned-integer outputs across 1D, 1D-array, 2D, cube, 2D-array, and 3D image forms ([shader construction](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1070-L1128), [runtime resources](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L679-L889)).

### `ubo`: read an indexed uniform-block instance

The shader declares four uniform-block instances, each containing one `highp uint`, and emits four indexed reads. The host backs the descriptor array with four separate uniform buffers and compares every returned value with the selected buffer's seeded value ([shader construction](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1441-L1505), [execution and check](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1186-L1365)).

### `ssbo`: read an indexed storage-block instance

This test uses the same four-read structure as `ubo`, but the generated declaration is `readonly buffer` and the descriptors are storage buffers. The comparison remains exact because each selected block contains one host-generated `uint` ([interface selection](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1446-L1471), [descriptor selection](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1198-L1201)).

### `ssbo_storage_buffer_decoration`: use the storage-buffer storage-class build path

This family repeats the `ssbo` behavior while setting `FLAG_USE_STORAGE_BUFFER_STORAGE_CLASS` in the shader build options. The runtime also requires `VK_KHR_storage_buffer_storage_class`. Data generation, descriptors, execution, and result checking otherwise use the storage-block path ([case registration](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2033-L2037), [extension check](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1217-L1221), [build flag](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1507-L1508)).

### `atomic_counter`: atomically increment an indexed counter

The shader declares four `uint` counters in one storage buffer and performs four `atomicAdd(counter[index], 1)` operations. The host checks the final counter values and the old values returned by the atomic operations. This family tests indexed storage access together with stage-specific atomic execution ([shader construction](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1837-L1893), [execution and oracle](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1545-L1798)).

The index-expression values change the generated shader as follows:

| Index-expression value | Generated selection mechanism |
|------------------------|-------------------------------|
| `const_literal` | Places the selected integer directly inside each subscript. |
| `const_expression` | Declares `const highp int indexBase = 1` and uses `indexBase + offset`. |
| `uniform` | Reads each index from a `std140` uniform block in descriptor set 1. |
| `dynamically_uniform` | Reads each index from a shader-executor input. The host repeats one selected value across every invocation for that operation. |

All forms except `const_literal` request `GL_EXT_gpu_shader5`. The `uniform` and `dynamically_uniform` paths also run the appropriate dynamic descriptor-array indexing feature check ([sampler generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1086-L1123), [block generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1459-L1501), [atomic generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1851-L1888), [feature checks](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L249-L275)).

## Shader Analysis

The representative shader uses a block test because it exposes the tested descriptor-array access without texture-coordinate setup or concurrent atomic ordering. Nearby `uniform`, `dynamically_uniform`, SSBO, sampler, and atomic variants change the index source or operation as summarized after the code.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.opaque_type_indexing.ubo.const_literal_compute
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `ubo` | Declares an array of four uniform-block instances in descriptor set 1, binding 0. |
| `const_literal` | Places the source-generated indices `3`, `2`, `3`, and `0` directly in the four subscripts. |
| `compute` | Runs 32 one-invocation workgroups and writes four `uint` results per invocation. |

#### Purpose

This shader checks that literal indexing selects the correct uniform-buffer descriptor for four reads and that every compute invocation returns the selected block values.

#### Structural Design

| Shader element | Role |
|----------------|------|
| `block[4]` | Descriptor array under test. Each element contains one host-seeded `uint`. |
| Four literal reads | Select block elements 3, 2, 3, and 0. Repeating index 3 also checks repeated access to one descriptor. |
| `outputs[]` | Shader-executor storage buffer that carries the four selected values to the host. |
| `invocationNdx` | Maps each one-invocation workgroup to one output record. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_long_vector : enable

/// Descriptor set 1 contains the tested array of four uniform-buffer descriptors.
layout(set = 1, binding = 0) uniform Block
{
    highp uint value;
} block[4];

layout(local_size_x = 1) in;

struct Outputs
{
    highp uint result0;
    highp uint result1;
    highp uint result2;
    highp uint result3;
};

/// Descriptor set 0 is shader-executor plumbing for host-visible results.
layout(set = 0, binding = 1, std430) buffer OutBuffer
{
    Outputs outputs[];
};

void main (void)
{
    uint invocationNdx = gl_NumWorkGroups.x*gl_NumWorkGroups.y*gl_WorkGroupID.z
                       + gl_NumWorkGroups.x*gl_WorkGroupID.y + gl_WorkGroupID.x;
    highp uint result0;
    highp uint result1;
    highp uint result2;
    highp uint result3;

    /// These literals come from the deterministic generator for this exact case.
    result0 = block[3].value;
    result1 = block[2].value;
    result2 = block[3].value;
    result3 = block[0].value;

    outputs[invocationNdx].result0 = result0;
    outputs[invocationNdx].result1 = result1;
    outputs[invocationNdx].result2 = result2;
    outputs[invocationNdx].result3 = result3;
}
```

#### Additional Info

- `BlockArrayIndexingCase::createShaderSpec()` supplies the block declaration, output symbols, and four tested reads. `ComputeShaderExecutor::generateComputeShader()` supplies the GLSL version, local-size declaration, invocation index, set 0 output block, and `main()` wrapper ([case generator](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1441-L1508), [compute wrapper](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3061-L3121), [buffer I/O generation](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L2034-L2130)).
- The deterministic seed for shader type `compute`, block type `uniform`, and index form `const_literal` produces indices `3`, `2`, `3`, and `0`. The host values are also deterministic, but the shader source does not contain them ([seed and value generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1441-L1457)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Index expression | `const_expression` replaces literals with `indexBase + offset`; `uniform` reads indices from a set 1 uniform block; `dynamically_uniform` reads them from set 0 shader-executor inputs. | [Index generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1459-L1501) |
| Resource family | `ssbo` changes `uniform` to `readonly buffer`; sampler leaves replace the reads with `texture()` calls; atomic leaves use `atomicAdd()` on a counter array. | [Block declaration](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1446-L1471), [sampler calls](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1110-L1123), [atomic calls](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1877-L1888) |
| Shader stage | The shared shader executor wraps the same `ShaderSpec` for vertex, fragment, geometry, tessellation-control, tessellation-evaluation, or compute execution. | [Source generation dispatch](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L174-L184), [registered stages](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1933-L1942) |
| Storage-buffer decoration | `ssbo_storage_buffer_decoration` adds `FLAG_USE_STORAGE_BUFFER_STORAGE_CLASS` during shader compilation. | [Build option](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1507-L1508) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 75
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_long_vector"
               OpName %main "main"
               OpName %invocationNdx "invocationNdx"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %result0 "result0"
               OpName %Block "Block"
               OpMemberName %Block 0 "value"
               OpName %block "block"
               OpName %result1 "result1"
               OpName %result2 "result2"
               OpName %result3 "result3"
               OpName %Outputs "Outputs"
               OpMemberName %Outputs 0 "result0"
               OpMemberName %Outputs 1 "result1"
               OpMemberName %Outputs 2 "result2"
               OpMemberName %Outputs 3 "result3"
               OpName %OutBuffer "OutBuffer"
               OpMemberName %OutBuffer 0 "outputs"
               OpName %_ ""
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %Block Block
               OpMemberDecorate %Block 0 Offset 0
               OpDecorate %block Binding 0
               OpDecorate %block DescriptorSet 1
               OpMemberDecorate %Outputs 0 Offset 0
               OpMemberDecorate %Outputs 1 Offset 4
               OpMemberDecorate %Outputs 2 Offset 8
               OpMemberDecorate %Outputs 3 Offset 12
               OpDecorate %_runtimearr_Outputs ArrayStride 16
               OpDecorate %OutBuffer BufferBlock
               OpMemberDecorate %OutBuffer 0 Offset 0
               OpDecorate %_ Binding 1
               OpDecorate %_ DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
      %Block = OpTypeStruct %uint
     %uint_4 = OpConstant %uint 4
%_arr_Block_uint_4 = OpTypeArray %Block %uint_4
%_ptr_Uniform__arr_Block_uint_4 = OpTypePointer Uniform %_arr_Block_uint_4
      %block = OpVariable %_ptr_Uniform__arr_Block_uint_4 Uniform
        %int = OpTypeInt 32 1
      %int_3 = OpConstant %int 3
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
      %int_2 = OpConstant %int 2
    %Outputs = OpTypeStruct %uint %uint %uint %uint
%_runtimearr_Outputs = OpTypeRuntimeArray %Outputs
  %OutBuffer = OpTypeStruct %_runtimearr_Outputs
%_ptr_Uniform_OutBuffer = OpTypePointer Uniform %OutBuffer
          %_ = OpVariable %_ptr_Uniform_OutBuffer Uniform
      %int_1 = OpConstant %int 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%invocationNdx = OpVariable %_ptr_Function_uint Function
    %result0 = OpVariable %_ptr_Function_uint Function
    %result1 = OpVariable %_ptr_Function_uint Function
    %result2 = OpVariable %_ptr_Function_uint Function
    %result3 = OpVariable %_ptr_Function_uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %15 = OpLoad %uint %14
         %17 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_1
         %18 = OpLoad %uint %17
         %19 = OpIMul %uint %15 %18
         %22 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_2
         %23 = OpLoad %uint %22
         %24 = OpIMul %uint %19 %23
         %25 = OpAccessChain %_ptr_Input_uint %gl_NumWorkGroups %uint_0
         %26 = OpLoad %uint %25
         %27 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_1
         %28 = OpLoad %uint %27
         %29 = OpIMul %uint %26 %28
         %30 = OpIAdd %uint %24 %29
         %31 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %32 = OpLoad %uint %31
         %33 = OpIAdd %uint %30 %32
               OpStore %invocationNdx %33
         %44 = OpAccessChain %_ptr_Uniform_uint %block %int_3 %int_0
         %45 = OpLoad %uint %44
               OpStore %result0 %45
         %48 = OpAccessChain %_ptr_Uniform_uint %block %int_2 %int_0
         %49 = OpLoad %uint %48
               OpStore %result1 %49
         %51 = OpAccessChain %_ptr_Uniform_uint %block %int_3 %int_0
         %52 = OpLoad %uint %51
               OpStore %result2 %52
         %54 = OpAccessChain %_ptr_Uniform_uint %block %int_0 %int_0
         %55 = OpLoad %uint %54
               OpStore %result3 %55
         %61 = OpLoad %uint %invocationNdx
         %62 = OpLoad %uint %result0
         %63 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %61 %int_0
               OpStore %63 %62
         %64 = OpLoad %uint %invocationNdx
         %66 = OpLoad %uint %result1
         %67 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %64 %int_1
               OpStore %67 %66
         %68 = OpLoad %uint %invocationNdx
         %69 = OpLoad %uint %result2
         %70 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %68 %int_2
               OpStore %70 %69
         %71 = OpLoad %uint %invocationNdx
         %72 = OpLoad %uint %result3
         %73 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %71 %int_3
               OpStore %73 %72
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Every test first creates the extra descriptor-set layout and resources required by its family, then asks `createExecutor()` for the selected shader stage. The executor runs the generated `ShaderSpec` and copies its declared outputs into host arrays.
- Sampler tests create eight one-texel images and matching samplers. They execute 64 invocations and collect four lookup streams. Shadow results use reference compare sampling with tolerance `0.005`; non-shadow float vectors use a per-component threshold of `1/256`; signed and unsigned integer vectors require exact equality. The checker also requires each lookup to remain consistent across invocations where the reference is invocation-independent ([setup and execution](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L679-L889), [sampler checks](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L891-L1000)).
- Block tests create four separate one-`uint` buffers, write and flush one seeded value into each, and optionally create a uniform index buffer. After 32 invocations, the host compares all four output streams with `m_inValues[m_readIndices[readNdx]]` using exact `uint` equality ([resource setup](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1186-L1337), [comparison](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1339-L1365)).
- Atomic-counter tests zero and flush a four-counter storage buffer, optionally upload uniform indices, and run 32 observed invocations. The host invalidates the counter buffer, checks that every selected counter reached at least the expected number of increments, and requires an untouched counter to remain zero. It then checks that each returned old value lies below the final value of its counter and that no observed old value is duplicated for that counter ([setup and execution](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1545-L1704), [atomic checks](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1706-L1798)).

A pass means every host-observed result satisfies the family-specific oracle. It does not mean only that the shader compiled, the pipeline ran, or the descriptor set was accepted.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sampler` | Wrong combined-image-sampler descriptor selection, texture lookup lowering, image/view setup, or typed sample result |
| `ubo` | Wrong uniform-buffer descriptor selection, block-array access, or returned block value |
| `ssbo` | Wrong storage-buffer descriptor selection, storage-block access, or returned block value |
| `ssbo_storage_buffer_decoration` | Wrong storage-buffer storage-class compilation path in addition to the ordinary SSBO causes |
| `atomic_counter` | Wrong indexed counter selection, atomic increment, returned old value, stage-specific atomic execution, or memory visibility |

A failure limited to `uniform` or `dynamically_uniform` can point to runtime index transport or dynamic descriptor-array indexing. A failure limited to one shader stage can point to that stage's shader-executor wrapper or resource-operation lowering.

### Cause Analysis

#### Sampler selection or lookup failure

**Possible failure symptoms:** The log reports an incorrect lookup value, an inconsistent value across invocations, or both. Float and shadow mismatches exceed their stated tolerances; integer sampler mismatches differ exactly.

**Possible implementation causes:** The implementation may select the wrong descriptor, lower a sampler-array subscript incorrectly, sample with the wrong dimensional or shadow form, or return the wrong typed value. A failure confined to one sampler type can narrow the investigation to that image, coordinate, comparison, or result-type path.

#### Uniform or storage block selection failure

**Possible failure symptoms:** One of the four output streams contains a `uint` different from the seeded value in the selected buffer. The log identifies the invocation and read number.

**Possible implementation causes:** The implementation may select the wrong descriptor, lower the interface-block instance array incorrectly, or use the wrong descriptor/storage-class path. Comparing `ubo`, `ssbo`, and `ssbo_storage_buffer_decoration` with the same index form and stage separates resource-class handling from the common indexing expression.

#### Index-source failure

**Possible failure symptoms:** Literal cases pass while `const_expression`, `uniform`, or `dynamically_uniform` cases fail for several resource families. Failures may follow one index-expression token across otherwise different test families.

**Possible implementation causes:** The compiler may fold the constant expression incorrectly, the runtime uniform block may be read from the wrong binding or layout, or shader-executor inputs may reach the tested stage incorrectly. For runtime index forms, descriptor-array dynamic indexing can also be lowered incorrectly even when the feature is advertised.

#### Atomic counter failure

**Possible failure symptoms:** A selected counter finishes below its expected minimum, an unselected counter changes, a returned old value lies outside its counter's final range, or two observed operations return the same old value for one counter.

**Possible implementation causes:** The implementation may select the wrong counter, lose atomic increments, return an incorrect pre-increment value, execute storage atomics incorrectly in one stage, or expose stale counter memory to the host. The oracle permits valid concurrent orderings, so it does not require one fixed order of old values.

#### Shared execution or readback failure

**Possible failure symptoms:** Unrelated sampler, block, and atomic leaves fail broadly, return unchanged data, or fail before their family-specific comparisons.

**Possible implementation causes:** Shader compilation, pipeline creation, descriptor binding, executor input/output buffers, submission, or host memory flush and invalidation may be involved. The family-specific log and stage clustering are needed before assigning the defect to one layer.

## Case Pruning

### Requirement-based pruning

Registered test case leaves can return `NotSupported` before their main comparison:

- Every leaf checks support for its selected shader stage through `checkSupportShader()` ([common support check](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L174-L211)).
- `uniform` and `dynamically_uniform` leaves require the matching device feature: `shaderSampledImageArrayDynamicIndexing`, `shaderUniformBufferArrayDynamicIndexing`, or `shaderStorageBufferArrayDynamicIndexing`. Literal and constant-expression leaves skip this dynamic-indexing gate ([descriptor feature checks](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L249-L275)).
- `sampler1DShadow` and `sampler1DArrayShadow` leaves require `VK_FORMAT_D16_UNORM` support for a 1D image with sampled-image usage ([format check](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1042-L1062)).
- `BlockArrayIndexingCase::checkSupport()` compares a source-calculated storage-buffer descriptor requirement with `maxPerStageDescriptorStorageBuffers`. The source applies this check to both UBO and SSBO block cases and adds two descriptors for compute execution ([limit check](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1407-L1433)).
- `ssbo_storage_buffer_decoration` requires `VK_KHR_storage_buffer_storage_class` ([extension check](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1217-L1221)).
- Atomic-counter leaves require `vertexPipelineStoresAndAtomics` in vertex, geometry, and tessellation stages, or `fragmentStoresAndAtomics` in the fragment stage. Compute adds no corresponding optional-feature check ([atomic stage checks](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1555-L1578)).

These checks do not remove names from the registered hierarchy. They classify a test case leaf as unsupported on a device that lacks a required capability.

### Design-based pruning

The registration code intentionally limits the matrix before creating test case leaves:

- Sampler test case leaves exist only for vertex, fragment, and compute. The generator still creates empty geometry and tessellation intermediate groups under each sampler index-expression group because it adds the stage group before applying the Vulkan CTS 1.0.2 stage filter ([sampler stage generation](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1982-L1992)).
- Block and atomic test families use all six registered stages and all four index-expression values ([block and atomic matrix](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L2020-L2038)).
- Sampler coverage stops at the 23 listed combined sampler types. The table contains no separate-image, separate-sampler, multisample, buffer, or external sampler forms ([sampler table](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1946-L1970)).
- Block tests use one separate buffer per descriptor-array element. The source explicitly leaves offsets within one buffer as possible future coverage, so this family does not vary buffer offsets or pack all elements into one allocation ([block resource setup](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1206-L1208)).

## Key Takeaways

- `glsl.opaque_type_indexing` executes each opaque-array indexing form and checks the selected resource's contents.
- The five test families supply distinct oracles: texture reference sampling, exact block-value comparison, and concurrent atomic-result validation.
- Literal, constant-expression, uniform, and dynamically uniform subscripts select the same kinds of generated indices through different shader and descriptor paths.
- The registration matrix has 372 test case leaves. Sampler coverage is deliberately limited to three stages, while block and atomic coverage uses six.
- Requirement-based `NotSupported` results are separate from design exclusions. See `Failure Meaning` for how failures cluster by resource family, index source, and shader stage.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Public factory declaration | [`vktOpaqueTypeIndexingTests.hpp`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.hpp#L23-L36) | Declares the test-family factory. |
| Common case and support logic | [`OpaqueTypeIndexingCase` and `checkSupported()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L150-L276) | Defines index-expression values, stage support, and descriptor dynamic-indexing gates. |
| Sampler type and format helpers | [`getTextureType()` through sampler helpers](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L289-L504) | Maps GLSL sampler types to image forms, coordinates, outputs, and formats. |
| Sampler execution and oracle | [`SamplerIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L679-L1000) | Creates images and descriptors, executes lookups, and checks sampled values. |
| Sampler shader generator | [`SamplerIndexingCase`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1002-L1128) | Generates the sampler array, index source, texture calls, and outputs. |
| Block execution and oracle | [`BlockArrayIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1138-L1365) | Creates UBO or SSBO descriptor arrays and checks every returned value. |
| Block support and shader generator | [`BlockArrayIndexingCase`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1368-L1508) | Defines the descriptor-limit check, interface declaration, indexed reads, and storage-class build flag. |
| Atomic execution and oracle | [`AtomicCounterIndexingCaseInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1511-L1798) | Runs indexed atomic adds and validates final counters plus returned old values. |
| Atomic shader generator | [`AtomicCounterIndexingCase`](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1801-L1894) | Generates the counter array and four indexed `atomicAdd` calls. |
| Family matrix and factory | [`OpaqueTypeIndexingTests::init()` and factory](../../../modules/vulkan/shaderexecutor/vktOpaqueTypeIndexingTests.cpp#L1896-L2048) | Defines all registered families, dimensions, stage exclusions, names, and the public entry point. |
| Shader-executor wrapper | [`BufferIoExecutor` and `ComputeShaderExecutor`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L2034-L2130), [`compute generation and execution`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3061-L3187) | Supplies stage wrappers, set 0 input/output resources, dispatch, and readback infrastructure. |
| GLSL package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1277) | Places `opaque_type_indexing` directly below `glsl`. |
| Vulkan default mustpass coverage | [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L10489-L10860) | Lists all 372 concrete test case leaves. |
