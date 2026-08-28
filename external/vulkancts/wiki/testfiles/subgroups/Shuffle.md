## Overview

**Core question:** Does each subgroup data-exchange operation return the value from the invocation selected by its exact source-index rule and argument form?

- This page covers the `subgroups.shuffle` test family implemented by [`vktSubgroupsShuffleTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L1).
- Six operation families are tested: absolute shuffle, XOR shuffle, shuffle up, shuffle down, rotate, and clustered rotate.
- A second behavior axis checks selectors supplied per invocation, supplied once at runtime for the subgroup, or embedded as a constant.
- The same shader-side comparison is run through graphics, compute, framebuffer, ray-tracing, and mesh stage harnesses where supported.
- Each checked invocation writes `1` for a correct value and `0` for a mismatch. The host requires every result to be `1`.

## Background Knowledge

For the shared concepts subgroup identity, active invocations, ballots, masks, collective result shapes, and clustered partitions, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- A selector is nonuniform when it may differ per invocation. A dynamically uniform selector is loaded at runtime but has one value for all invocations. A constant selector is embedded in the generated shader.
- Rotate differs from shuffle up and down because its source index wraps modulo the subgroup size. Clustered rotate applies that wraparound separately inside consecutive power-of-two clusters.

## Registration Hierarchy

```text
subgroups.shuffle
├── graphics
├── compute
├── framebuffer
├── ray_tracing
└── mesh
```

The final two direct children are not present in Vulkan SC builds. Vulkan SC also excludes rotate operations.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Stage family | `graphics`, `compute`, `framebuffer`, `ray_tracing`, `mesh` | Chooses the common execution harness and shader stages that carry the same operation check. | [`createSubgroupsShuffleTests()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L661-L860) |
| Operation family | `subgroupshuffle`, `subgroupshufflexor`, `subgroupshuffleup`, `subgroupshuffledown`, `subgrouprotate`, `subgroupclusteredrotate` | Changes the source-invocation rule under test. | [`OpType` and operation-name mapping](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L41-L110) |
| Argument form | no suffix, `_dynamically_uniform`, `_constant` | Selects a per-invocation runtime operand, one runtime operand shared by the subgroup, or literal `5`. | [`argCases`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L687-L697) |
| Data format | Scalar and vector Boolean, signed integer, unsigned integer, floating-point, 8-bit, 16-bit, 32-bit, 64-bit, and long-vector forms where available | Checks that subgroup exchange preserves values across supported scalar widths and vector shapes. | [`getAllFormats()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1878-L1912) |
| Required subgroup size | default or `_requiredsubgroupsize` for compute and mesh | Repeats the operation at each supported power-of-two subgroup size. | [`test()` required-size loop](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L541-L595) |
| Framebuffer stage | `vertex`, `tess_control`, `tess_eval`, `geometry` | Runs the check without shader storage buffers and returns the marker through framebuffer output. | [`fbStages` and framebuffer registration](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L673-L678) |
| Mesh stage | `mesh`, `task` | Selects which mesh-pipeline stage executes the subgroup operation. | [`meshStages`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L680-L684) |

The operation and argument dimensions do not form a full Cartesian product. `subgroupshuffle` uses only the dynamic form. XOR, up, and down use all three forms. Rotate and clustered rotate use dynamically uniform and constant forms, but not dynamic forms.

## Behavior Parameters

The primary behavioral axis is the operation family because it changes how the expected source invocation is calculated.

### `shuffle`: absolute source invocation

`subgroupShuffle(value, id_in)` reads from invocation `id_in`. The test supplies a separate dynamic selector for each invocation and compares the returned value with `data1[id_in]` when that source is active and in range.

### `xor`: XOR-relative source invocation

`subgroupShuffleXor(value, id_in)` reads from `gl_SubgroupInvocationID ^ id_in`. This forms XOR-based exchange patterns whose distance depends on the selector bits.

### `up`: source at a lower invocation index

`subgroupShuffleUp(value, id_in)` uses `gl_SubgroupInvocationID - id_in`. Unsigned underflow produces an out-of-range index, so the ballot and range guard excludes that result from comparison.

### `down`: source at a higher invocation index

`subgroupShuffleDown(value, id_in)` uses `gl_SubgroupInvocationID + id_in`. Sources beyond `gl_SubgroupSize` are excluded from comparison.

### `rotate`: subgroup-wide wraparound

`subgroupRotate(value, id_in)` uses `(gl_SubgroupInvocationID + id_in) & (gl_SubgroupSize - 1)`. Vulkan subgroup size is a power of two, so this masks the sum to the subgroup-wide wrapped source index.

### `clustered_rotate`: cluster-local wraparound

`subgroupClusteredRotate(value, id_in, cluster_size)` rotates independently inside each consecutive power-of-two cluster. The shader loops from cluster size `1` through `gl_SubgroupSize`; a switch keeps each cluster-size operand constant at pipeline creation time. The expected index wraps the low cluster bits and preserves the invocation's cluster prefix.

The secondary behavioral axis is the argument form. It changes operand uniformity and the resource path used to obtain the selector.

### `dynamic`: per-invocation selector

Each invocation loads `data2[gl_SubgroupInvocationID]` and masks it by `gl_SubgroupSize - 1`. Graphics, compute, ray-tracing, and mesh cases read the selector from a std430 SSBO; framebuffer cases use a UBO array because that path avoids shader storage buffers. This form is used by shuffle, XOR, up, and down.

### `dynamically_uniform`: one runtime selector

Every invocation loads `data2[0]` from a std140 UBO. XOR, up, and down reduce it with `% 32`. Rotate and clustered rotate mask it with `gl_SubgroupSize * 2 - 1` before the operation applies wraparound.

### `constant`: literal selector

The generated shader uses literal `5` as the operation operand. XOR, up, down, rotate, and clustered rotate include this form. The common resource setup still binds the selector input, but the operation expression does not read it.

## Shader Analysis

One compute shader is enough to show the generated resource declarations, selector loading, subgroup operation, independent expected-index calculation, active-source guard, and result marker. Clustered rotate adds a cluster-size loop, which is described in the behavior and variation sections rather than repeated as a second walkthrough.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.shuffle.compute.subgroupshufflexor_uint_dynamically_uniform
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Uses the compute branch of `initStdPrograms()` and writes one SSBO result per global invocation. |
| `subgroupshufflexor` | Selects the source invocation by XOR of the current subgroup invocation ID and `id_in`. |
| `uint` | Exchanges one 32-bit unsigned scalar per invocation. |
| `dynamically_uniform` | All invocations load the runtime selector from `data2[0]` in a UBO. |
| default subgroup size | Runs with the implementation-selected subgroup size rather than the required-size sweep. |

#### Purpose

This shader checks that `subgroupShuffleXor` returns the `uint` value from the active invocation selected by a dynamically uniform XOR mask.

#### Structural Design

| Phase | Shader action | Observable result |
|-------|---------------|-------------------|
| Address output | Flatten `gl_GlobalInvocationID` to `offset`. | Each global invocation owns one result element. |
| Select source | Load `id_in = data2[0] % 32` and compute `id = gl_SubgroupInvocationID ^ id_in`. | The operation and reference calculation use the same selector through independent mechanisms. |
| Exchange value | Call `subgroupShuffleXor` on the current invocation's `data1` value. | `op` contains the implementation result. |
| Guard and compare | Check that `id` is in range and active, then compare `op` with `data1[id]`. | A checked match writes `1`; a checked mismatch writes `0`; an unverifiable source writes `1`. |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_shuffle: enable
#extension GL_KHR_shader_subgroup_ballot: enable

/// The host specializes all three local-size dimensions. The global invocation index selects one result slot.
layout (local_size_x_id = 0, local_size_y_id = 1, local_size_z_id = 2) in;

/// Binding 0 is a std430 result SSBO with one uint pass marker per global invocation.
layout(set = 0, binding = 0, std430) buffer Buffer1
{
  uint result[];
};

/// Binding 1 is a read-only std430 SSBO. Element n is the value contributed by subgroup invocation n.
layout(set = 0, binding = 1, std430) readonly buffer Buffer2
{
  uint data1[];
};

/// Binding 2 is a std140 UBO. This dynamically uniform case reads only data2[0].
layout(set = 0, binding = 2, std140) uniform Buffer3
{
  uint data2[];
};

void main (void)
{
  uvec3 globalSize = gl_NumWorkGroups * gl_WorkGroupSize;
  highp uint offset = globalSize.x * ((globalSize.y * gl_GlobalInvocationID.z) + gl_GlobalInvocationID.y) + gl_GlobalInvocationID.x;
  uint tempRes;

  /// All invocations read the same runtime selector, then XOR it with their own subgroup invocation ID.
  uint temp_res;
  uvec4 mask = subgroupBallot(true);
  uint id_in = data2[0] % 32;
  uint op = subgroupShuffleXor(data1[gl_SubgroupInvocationID], id_in);
  uint id = gl_SubgroupInvocationID ^ id_in;

  /// Compare only when the computed source invocation is in range and active.
  if ((id < gl_SubgroupSize) && subgroupBallotBitExtract(mask, id))
  {
    temp_res = (op == data1[id]) ? 1 : 0;
  }
  else
  {
    temp_res = 1; // Invocation we read from was inactive, so we can't verify results!
  }
  tempRes = temp_res;
  result[offset] = tempRes;
}
```

#### Additional Info

- The exact case is registered in the Vulkan default subgroup mustpass list at [`subgroups.txt#L39667`](../../../mustpass/main/vk-default/subgroups.txt#L39667).
- `initPrograms()` selects SPIR-V 1.3 for this compute case and delegates final compute-shader assembly to `initStdPrograms()`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation family | Replaces the built-in call and expected source-index formula. Clustered rotate also adds a cluster-size loop and switch. | [`getNonClusteredTestSource()` and `getClusteredTestSource()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L227-L336) |
| Argument form | Replaces `data2[0] % 32` with a per-invocation SSBO load, a rotate-specific mask, or literal `5`; declarations switch between SSBO and UBO. | [`getPerStageHeadDeclarations()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L143-L182) |
| Data format | Replaces the `uint` type of `data1` and `op`, and may add an extended-type or long-vector extension. | [`getAdditionalExtensionForFormat()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1848-L1875) |
| Stage family | Wraps the same test body in stage-specific entry-point code and changes result transport. Mesh and ray tracing require SPIR-V 1.4. | [`initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L362-L379) |
| Required subgroup size | Keeps the shader logic but runs it with each supported required subgroup size. | [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L541-L595) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 105
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformBallot
               OpCapability GroupNonUniformShuffle
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_GlobalInvocationID %gl_SubgroupInvocationID %gl_SubgroupSize
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpSourceExtension "GL_KHR_shader_subgroup_shuffle"
               OpName %main "main"
               OpName %globalSize "globalSize"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %offset "offset"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %mask "mask"
               OpName %id_in "id_in"
               OpName %Buffer3 "Buffer3"
               OpMemberName %Buffer3 0 "data2"
               OpName %_ ""
               OpName %op "op"
               OpName %Buffer2 "Buffer2"
               OpMemberName %Buffer2 0 "data1"
               OpName %__0 ""
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %id "id"
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpName %temp_res "temp_res"
               OpName %tempRes "tempRes"
               OpName %Buffer1 "Buffer1"
               OpMemberName %Buffer1 0 "result"
               OpName %__1 ""
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %13 SpecId 0
               OpDecorate %14 SpecId 1
               OpDecorate %15 SpecId 2
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_arr_uint_uint_1 ArrayStride 16
               OpDecorate %Buffer3 Block
               OpMemberDecorate %Buffer3 0 Offset 0
               OpDecorate %_ Binding 2
               OpDecorate %_ DescriptorSet 0
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %Buffer2 Block
               OpMemberDecorate %Buffer2 0 NonWritable
               OpMemberDecorate %Buffer2 0 Offset 0
               OpDecorate %__0 NonWritable
               OpDecorate %__0 Binding 1
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %64 RelaxedPrecision
               OpDecorate %71 RelaxedPrecision
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %76 RelaxedPrecision
               OpDecorate %_runtimearr_uint_0 ArrayStride 4
               OpDecorate %Buffer1 Block
               OpMemberDecorate %Buffer1 0 Offset 0
               OpDecorate %__1 Binding 0
               OpDecorate %__1 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_NumWorkGroups = OpVariable %_ptr_Input_v3uint Input
         %13 = OpSpecConstant %uint 1
         %14 = OpSpecConstant %uint 1
         %15 = OpSpecConstant %uint 1
%gl_WorkGroupSize = OpSpecConstantComposite %v3uint %13 %14 %15
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_2 = OpConstant %uint 2
%_ptr_Input_uint = OpTypePointer Input %uint
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
       %bool = OpTypeBool
       %true = OpConstantTrue %bool
     %uint_3 = OpConstant %uint 3
%_arr_uint_uint_1 = OpTypeArray %uint %uint_1
    %Buffer3 = OpTypeStruct %_arr_uint_uint_1
%_ptr_Uniform_Buffer3 = OpTypePointer Uniform %Buffer3
          %_ = OpVariable %_ptr_Uniform_Buffer3 Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
    %uint_32 = OpConstant %uint 32
%_runtimearr_uint = OpTypeRuntimeArray %uint
    %Buffer2 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_Buffer2 = OpTypePointer StorageBuffer %Buffer2
        %__0 = OpVariable %_ptr_StorageBuffer_Buffer2 StorageBuffer
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
      %int_1 = OpConstant %int 1
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
    %Buffer1 = OpTypeStruct %_runtimearr_uint_0
%_ptr_StorageBuffer_Buffer1 = OpTypePointer StorageBuffer %Buffer1
        %__1 = OpVariable %_ptr_StorageBuffer_Buffer1 StorageBuffer
       %main = OpFunction %void None %3
          %5 = OpLabel
 %globalSize = OpVariable %_ptr_Function_v3uint Function
     %offset = OpVariable %_ptr_Function_uint Function
       %mask = OpVariable %_ptr_Function_v4uint Function
      %id_in = OpVariable %_ptr_Function_uint Function
         %op = OpVariable %_ptr_Function_uint Function
         %id = OpVariable %_ptr_Function_uint Function
   %temp_res = OpVariable %_ptr_Function_uint Function
    %tempRes = OpVariable %_ptr_Function_uint Function
         %12 = OpLoad %v3uint %gl_NumWorkGroups
         %17 = OpIMul %v3uint %12 %gl_WorkGroupSize
               OpStore %globalSize %17
         %21 = OpAccessChain %_ptr_Function_uint %globalSize %uint_0
         %22 = OpLoad %uint %21
         %24 = OpAccessChain %_ptr_Function_uint %globalSize %uint_1
         %25 = OpLoad %uint %24
         %29 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %30 = OpLoad %uint %29
         %31 = OpIMul %uint %25 %30
         %32 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %33 = OpLoad %uint %32
         %34 = OpIAdd %uint %31 %33
         %35 = OpIMul %uint %22 %34
         %36 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %37 = OpLoad %uint %36
         %38 = OpIAdd %uint %35 %37
               OpStore %offset %38
         %45 = OpGroupNonUniformBallot %v4uint %uint_3 %true
               OpStore %mask %45
         %54 = OpAccessChain %_ptr_Uniform_uint %_ %int_0 %int_0
         %55 = OpLoad %uint %54
         %57 = OpUMod %uint %55 %uint_32
               OpStore %id_in %57
         %64 = OpLoad %uint %gl_SubgroupInvocationID
         %66 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0 %64
         %67 = OpLoad %uint %66
         %68 = OpLoad %uint %id_in
         %69 = OpGroupNonUniformShuffleXor %uint %uint_3 %67 %68
               OpStore %op %69
         %71 = OpLoad %uint %gl_SubgroupInvocationID
         %72 = OpLoad %uint %id_in
         %73 = OpBitwiseXor %uint %71 %72
               OpStore %id %73
         %74 = OpLoad %uint %id
         %76 = OpLoad %uint %gl_SubgroupSize
         %77 = OpULessThan %bool %74 %76
               OpSelectionMerge %79 None
               OpBranchConditional %77 %78 %79
         %78 = OpLabel
         %80 = OpLoad %v4uint %mask
         %81 = OpLoad %uint %id
         %82 = OpGroupNonUniformBallotBitExtract %bool %uint_3 %80 %81
               OpBranch %79
         %79 = OpLabel
         %83 = OpPhi %bool %77 %5 %82 %78
               OpSelectionMerge %85 None
               OpBranchConditional %83 %84 %95
         %84 = OpLabel
         %87 = OpLoad %uint %op
         %88 = OpLoad %uint %id
         %89 = OpAccessChain %_ptr_StorageBuffer_uint %__0 %int_0 %88
         %90 = OpLoad %uint %89
         %91 = OpIEqual %bool %87 %90
         %93 = OpSelect %int %91 %int_1 %int_0
         %94 = OpBitcast %uint %93
               OpStore %temp_res %94
               OpBranch %85
         %95 = OpLabel
               OpStore %temp_res %uint_1
               OpBranch %85
         %85 = OpLabel
         %97 = OpLoad %uint %temp_res
               OpStore %tempRes %97
        %102 = OpLoad %uint %offset
        %103 = OpLoad %uint %tempRes
        %104 = OpAccessChain %_ptr_StorageBuffer_uint %__1 %int_0 %102
               OpStore %104 %103
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `supportedCheck()` requires general subgroup support, the operation-specific shuffle, shuffle-relative, rotate, or clustered-rotate capability, support for the selected data format, and support for the chosen shader stage.
- The host initializes `data1` and `data2` with deterministic pseudorandom data. Dynamic argument cases allocate one selector per maximum supported subgroup invocation. Other argument cases allocate one selector element.
- Compute and mesh paths dispatch through their common helpers. Graphics and ray-tracing paths use all supported stages from their stage family. Framebuffer cases use UBO inputs and return the pass marker through framebuffer output.
- The shader computes the expected source invocation separately from the subgroup built-in. It compares values only when that source invocation is both in range and active according to the ballot mask.
- The value oracle cannot distinguish a wrong source invocation that happens to contain the same value as the expected source. A run in which every computed source is out of range or inactive also records only `1` markers and therefore makes no checked exchange comparison; for example, `_constant_requiredsubgroupsize` XOR, up, and down runs at power-of-two subgroup sizes below the literal selector `5` make every expected source out of range.
- Clustered rotate combines the result for every power-of-two cluster size. A mismatch in any cluster size leaves the final marker at `0`.
- Compute and mesh `_requiredsubgroupsize` cases run once for every supported power-of-two subgroup size from `minSubgroupSize` through `maxSubgroupSize`.
- The common host callbacks scan the complete result range and return failure on the first value that is not `1`. Required-size sweeps stop at the first failed size and log that size.

## Failure Meaning

### Failure Cause Mapping

Operation-family axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `shuffle` | Incorrect absolute invocation selection or lowering of `subgroupShuffle`. |
| `xor` | Incorrect XOR-relative source selection or lowering of `subgroupShuffleXor`. |
| `up` | Incorrect subtraction-based source selection, boundary handling, or lowering of `subgroupShuffleUp`. |
| `down` | Incorrect addition-based source selection, boundary handling, or lowering of `subgroupShuffleDown`. |
| `rotate` | Incorrect modulo-subgroup wraparound or lowering of `subgroupRotate`. |
| `clustered_rotate` | Incorrect cluster partitioning, cluster-local wraparound, cluster-size handling, or lowering of `subgroupClusteredRotate`. |

Argument-form axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dynamic` | Incorrect handling of a per-invocation nonuniform selector or its selector-buffer load path. |
| `dynamically_uniform` | Incorrect handling of a runtime but subgroup-uniform selector or its UBO load path. |
| `constant` | Incorrect handling or optimization of the literal selector operand. |

Failures across all values can also come from shared stage plumbing, input initialization, descriptor access, result writes, synchronization, or host readback. The operation and argument patterns help separate those shared failures from operation-specific or operand-form-specific failures.

### Cause Analysis

#### Incorrect source invocation selection

**Possible failure symptoms:** One operation family writes `0` when the subgroup result differs from `data1` at the independently calculated absolute, XOR, lower, higher, or wrapped source index. Up and down failures may concentrate near subgroup boundaries.

**Possible implementation causes:** The shader compiler or subgroup implementation may lower the operation with the wrong index rule, apply a signed or unsigned boundary rule incorrectly, or fail to preserve the source lane's value. Vulkan defines shuffle as reading from another subgroup invocation, relative shuffle as shifting up or down, and rotate as modulo-subgroup selection.

#### Incorrect clustered rotate behavior

**Possible failure symptoms:** `clustered_rotate` fails for one or more cluster sizes while ordinary rotate passes, or values cross a cluster boundary instead of wrapping within that cluster.

**Possible implementation causes:** The implementation may ignore the cluster-size operand, derive the wrong cluster prefix, wrap across the whole subgroup, or mishandle one of the compile-time power-of-two cluster sizes. Vulkan defines clustered rotate as rotate within consecutive power-of-two partitions.

#### Incorrect argument-form handling

**Possible failure symptoms:** Dynamic cases fail while dynamically uniform and constant cases pass, or one runtime-uniform or constant suffix fails across several operation families.

**Possible implementation causes:** Descriptor loads, nonuniform operand propagation, dynamically uniform analysis, or constant folding may provide a selector different from the source-defined value. A compiler transformation may also treat a nonuniform selector as uniform or incorrectly specialize a constant selector.

#### Shared execution or readback failure

**Possible failure symptoms:** Unrelated operation and argument values fail in the same stage family, all output elements remain wrong, or only a framebuffer, ray-tracing, graphics, compute, or mesh path fails.

**Possible implementation causes:** Stage-specific shader plumbing, descriptor access, output writes, command synchronization, framebuffer transfer, or host cache invalidation may corrupt or hide the pass markers. The CTS source uses separate common harnesses for these paths, so a stage-wide pattern calls for investigation below the operation-specific logic.

## Case Pruning

### Requirement-based pruning

- Shuffle and XOR require `VK_SUBGROUP_FEATURE_SHUFFLE_BIT`. Up and down require `VK_SUBGROUP_FEATURE_SHUFFLE_RELATIVE_BIT`.
- Rotate requires `shaderSubgroupRotate`; clustered rotate requires `shaderSubgroupRotateClustered`. Both require extension specification version 2 or later when supplied by `VK_KHR_shader_subgroup_rotate`.
- The selected data format and shader stage must support subgroup operations. Narrow framebuffer formats also require matching 8-bit or 16-bit UBO storage support.
- Required-subgroup-size cases require `VK_EXT_subgroup_size_control`, `subgroupSizeControl`, `computeFullSubgroups`, and support for the selected stage in `requiredSubgroupSizeStages`.
- Ray-tracing cases require `VK_KHR_ray_tracing_pipeline`. Mesh cases require `VK_EXT_mesh_shader`, vertex-pipeline stores and atomics, and `taskShader` for task-stage cases.

### Design-based pruning

- `shuffle` omits dynamically uniform and constant forms because its selector is tested as the direct per-invocation source index.
- Rotate and clustered rotate omit the dynamic form. Their registered selectors are dynamically uniform or constant.
- Clustered rotate tests only power-of-two cluster sizes from `1` through the subgroup size, matching the operation's cluster requirements.
- Ray tracing uses a smaller representative format list than the other stage families.
- Vulkan SC omits rotate, clustered rotate, ray tracing, mesh, and non-SC long-vector additions.

## Key Takeaways

- The operation family is the main behavior axis: each value has a distinct source-invocation formula.
- Argument form is a second behavior axis that separates per-invocation selectors, one runtime subgroup-uniform selector, and literal operands.
- The shader does not judge values read from inactive or out-of-range sources. Its ballot and range guard limits validation to defined, observable exchanges.
- Rotate wraps across the subgroup. Clustered rotate wraps inside each tested cluster and never treats whole-subgroup rotate as a substitute.
- A failure marker comes from an exact value comparison, while patterns across operations, operand forms, and stage families help locate the affected mechanism. See `## Failure Meaning` for that mapping.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Operation and argument definitions | [`OpType`, `ArgType`, and `CaseDefinition`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L41-L72) | Defines both behavior axes and per-case support flags. |
| Operation names and extensions | [`getOpTypeName()` and `getExtensionForOpType()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L89-L141) | Maps families to GLSL built-ins and required extensions. |
| Per-stage resources | [`getPerStageHeadDeclarations()` and framebuffer declarations](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L143-L225) | Defines result, value, and selector interfaces. |
| Shader test bodies | [`getNonClusteredTestSource()` and `getClusteredTestSource()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L227-L336) | Generates operation calls, expected indices, guards, comparisons, and cluster loops. |
| Shader builders and SPIR-V targets | [`initFrameBufferPrograms()` and `initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L350-L379) | Connects generated bodies to common stage builders. |
| Support checks | [`supportedCheck()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L381-L483) | Applies feature, format, stage, and subgroup-size gates. |
| Runtime routing | [`noSSBOtest()` and `test()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L485-L654) | Creates inputs, selects harnesses, and performs required-size sweeps. |
| Registration matrix | [`createSubgroupsShuffleTests()`](../../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L661-L860) | Generates the five direct stage families and their leaves. |
| Common compute builder | [`initStdPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434) | Wraps the test body and writes one result per global invocation. |
| Input initialization | [`initializeMemory()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2293-L2407) | Supplies deterministic input data and flushes host writes. |
| Result callbacks | [`check()` and `checkComputeOrMesh()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Requires every host-visible marker to equal `1`. |
| Representative registration | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L39667) | Confirms the exact walkthrough path. |
| Subgroup operation semantics | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3447-L3567) | Defines exchange, relative shuffle, rotate, and cluster concepts. |
| Advertised subgroup capabilities | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L1428-L1480) | Defines the subgroup feature bits used by support checks. |
