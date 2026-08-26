## Overview

**Core question:** Do the shader clock builtins return non-decreasing values when read twice in one shader invocation?

- [`vktShaderClockTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L20-L24) implements `glsl.shader_clock` for `VK_KHR_shader_clock`.
- Each leaf generates GLSL that reads one clock builtin twice, writes `1` only when the second reading is smaller than the first, and expects zero from all 32 shader-executor invocations.
- The registered matrix combines three shader stages with four clock operations, for 12 leaves. This page describes source-defined registration, support checks, shader generation, and result checking; it does not report execution on this host.

## Background Knowledge

- **Shader clock scopes.** A subgroup clock measures a clock associated with the shader subgroup, while a device clock uses a device-wide clock. The test treats both as ordering sources and does not require a particular timestamp value.
- **Unsigned multiword values.** The 64-bit forms return `uint64_t`. The `2x32` forms return a `uvec2` containing two words, so their comparison must treat `.y` as the high word and `.x` as the low word.
- **Shader-executor stages.** The shared shader-executor framework can place the same generated operation in different shader stages and selects the corresponding stage-specific executor. The clock page therefore compares stage variants through one common host-side result path.

## Registration Hierarchy

```text
glsl.shader_clock
├── vertex
├── fragment
└── compute
```

`addShaderClockTests()` creates the three stage groups and adds all four operation entries to each group ([registration loop](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L250)). The stage names are `vertex`, `fragment`, and `compute`; this file registers no tessellation, geometry, mesh, or task group. The GLSL package attaches the factory through [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1279).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Shader stage | `vertex`, `fragment`, `compute` | Selects where the clock reads execute and which shared executor implementation runs. | [stage table and registration](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L250), [`generateSources()` and `createExecutor()`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L4198-L4259) |
| Clock operation | `clockARB`, `clock2x32ARB`, `clockRealtimeEXT`, `clockRealtime2x32EXT` | Selects clock scope, GLSL builtin, return representation, and extension. | [operation table](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L68-L85) |
| Clock scope | Subgroup or Device | Selects the `shaderSubgroupClock` or `shaderDeviceClock` feature check. | [support selection](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L159-L167) |
| Return representation | 64-bit `uint64_t` or two-word `uvec2` | Selects the comparison form and whether `shaderInt64` is required. | [source selection](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L175-L203) |
| Invocation count | `32` | Gives every leaf one output slot per shader-executor invocation. | [`NUM_ELEMENTS` and `iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L63-L66), [execution](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L103-L118) |

The operation table is applied independently to every stage, producing `3 × 4 = 12` registered leaves ([registration loop](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L250)).

## Behavior Parameters

The primary behavioral axis is the clock operation. Its values change the clock scope, builtin, return representation, extension requirements, and comparison emitted into the shader.

### `clockARB` — subgroup 64-bit clock

This case reads the subgroup clock builtin `clockARB()` twice as `uint64_t` values. It uses the 64-bit comparison and enables `GL_ARB_shader_clock`; the 64-bit operation also requires `GL_ARB_gpu_shader_int64` in the generated shader ([operation table and source construction](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L68-L85), [64-bit source](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L175-L185)).

### `clock2x32ARB` — subgroup two-word clock

This case reads `clock2x32ARB()` twice as `uvec2` values and compares the high word first, then the low word when the high words are equal. It uses the subgroup clock scope and `GL_ARB_shader_clock`, but does not take the 64-bit shader-integer branch ([32-bit-pair source](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L186-L194)).

### `clockRealtimeEXT` — device 64-bit clock

This case reads the device realtime clock builtin `clockRealtimeEXT()` twice as `uint64_t` values. It uses the 64-bit comparison, requires `GL_EXT_shader_realtime_clock`, and selects the device-clock feature check ([device extension and 64-bit source](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L175-L203)).

### `clockRealtime2x32EXT` — device two-word clock

This case reads `clockRealtime2x32EXT()` twice as `uvec2` values and uses the same unsigned lexicographic comparison as `clock2x32ARB`. It selects the device clock scope and requires `GL_EXT_shader_realtime_clock` ([device extension and pair comparison](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L186-L203)).

Each operation is registered once under each of the three stage groups. The stage changes execution placement, while the operation changes the clock behavior being checked.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.shader_clock.compute.clockRealtime2x32EXT
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | Selects the single-stage compute executor, whose generated wrapper exposes the exact storage-buffer result path without fixed-function graphics stages. |
| `clockRealtime2x32EXT` | Selects the device-scope clock, its two-word `uvec2` return form, `GL_EXT_shader_realtime_clock`, and the nontrivial high-word-first comparison branch. |
| `32` invocations | `iterate()` requests 32 results; the compute executor dispatches 32 one-invocation workgroups and writes one `uvec2` record per workgroup. |

#### Purpose

This shader checks that two consecutive device-scope realtime-clock reads do not move backwards. It emits `out0.x = 1` only when the unsigned 64-bit value encoded as `{ low = .x, high = .y }` decreases.

#### Structural Design

| Phase | Exact behavior |
|---|---|
| Address result | Flatten `gl_WorkGroupID` using `gl_NumWorkGroups`; with the host's `(32, 1, 1)` dispatch, the index is `0` through `31`. |
| Sample clock | Call `clockRealtime2x32EXT()` twice, yielding `time1` and `time2` as two-word unsigned values. |
| Compare | Test `time1.y > time2.y`, then compare `.x` only when the high words are equal. |
| Record | Initialize `out0` to zero, set only `out0.x` on a backwards reading, and store the full `uvec2` to output binding 1. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_long_vector : enable
#extension GL_EXT_shader_realtime_clock : require

/// One local invocation per workgroup; the host dispatches 32 workgroups for the 32 result elements.
layout(local_size_x = 1) in;

struct Outputs
{
    highp uvec2 out0;
};

/// Set 0, binding 1 is the host-visible std430 output SSBO. Each invocation writes one uvec2;
/// .x is the failure flag and .y remains zero.
layout(set = 0, binding = 1, std430) buffer OutBuffer
{
    Outputs outputs[];
};

void main (void)
{
    /// Flatten the dispatched workgroup coordinates to select this invocation's output record.
    uint invocationNdx = gl_NumWorkGroups.x*gl_NumWorkGroups.y*gl_WorkGroupID.z
                       + gl_NumWorkGroups.x*gl_WorkGroupID.y + gl_WorkGroupID.x;
    highp uvec2 out0;

    /// Read the device-scope realtime clock twice and record failure only if the unsigned 64-bit
    /// value represented by high word .y and low word .x moves backwards.
    uvec2 time1 = clockRealtime2x32EXT();
    uvec2 time2 = clockRealtime2x32EXT();
    out0  = uvec2(0, 0);
    if (time1.y > time2.y || (time1.y == time2.y && time1.x > time2.x)){
        out0.x = 1;
    }

    /// Publish the complete two-word result to the element read back for this invocation.
    outputs[invocationNdx].out0 = out0;
}
```

#### Additional Info

- `ShaderClockCase::initShaderSpec()` contributes the clock extension, operation fragment, and sole `highp uvec2 out0`; `ComputeShaderExecutor::generateComputeShader()` supplies the version, compute layout, `Outputs`/`OutBuffer` declarations, index calculation, and final store ([case fragment](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L170-L212), [compute wrapper](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3061-L3122), [shared buffer printers](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L2034-L2130)).
- There is no shader-visible input resource because this case declares no `ShaderSpec::inputs`. The only shader-visible host resource is the output SSBO at set 0, binding 1; its 32 `uvec2` records occupy 256 bytes under the generated std430 layout ([buffer declarations](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L2034-L2068), [host allocation and dispatch](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L2252-L2299), [execution](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3219-L3299)).
- The case supplies no explicit `ShaderBuildOptions`, so the source-collection baseline target is SPIR-V 1.0 ([default `ShaderSpec`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.hpp#L64-L85), [`getBaselineSpirvVersion()`](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Shader stage | `fragment` moves the operation into a fragment shader fed by a passthrough vertex shader; `vertex` moves it into the vertex shader and passes `out0` through a fixed fragment shader. The operation fragment itself is unchanged. | [stage registration](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L250), [stage source selection](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L1756-L1765), [fragment source selection](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L1834-L1844), [`generateSources()`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L4198-L4231) |
| Clock operation | `clockRealtimeEXT` adds 64-bit integer support and uses `uint64_t` plus a direct comparison; subgroup variants replace the realtime extension with `GL_ARB_shader_clock`, and `clockARB` also uses the 64-bit branch. The `2x32` variants retain the high-word/low-word comparison. | [operation table and generated branches](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L170-L212), [registration](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L250) |
| Invocation count | The shader source is unchanged, while the host's `numValues` controls output-buffer length and compute dispatch count; this test fixes that value at 32. | [`NUM_ELEMENTS` and `iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L63-L66), [execution request](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L103-L118), [compute dispatch](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L3219-L3299) |

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
; Bound: 80
; Schema: 0
               OpCapability Shader
               OpCapability ShaderClockKHR
               OpExtension "SPV_KHR_shader_clock"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_NumWorkGroups %gl_WorkGroupID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_long_vector"
               OpSourceExtension "GL_EXT_shader_realtime_clock"
               OpName %main "main"
               OpName %invocationNdx "invocationNdx"
               OpName %gl_NumWorkGroups "gl_NumWorkGroups"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %time1 "time1"
               OpName %time2 "time2"
               OpName %out0 "out0"
               OpName %Outputs "Outputs"
               OpMemberName %Outputs 0 "out0"
               OpName %OutBuffer "OutBuffer"
               OpMemberName %OutBuffer 0 "outputs"
               OpName %_ ""
               OpDecorate %gl_NumWorkGroups BuiltIn NumWorkgroups
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpMemberDecorate %Outputs 0 Offset 0
               OpDecorate %_runtimearr_Outputs ArrayStride 8
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
     %v2uint = OpTypeVector %uint 2
%_ptr_Function_v2uint = OpTypePointer Function %v2uint
         %41 = OpConstantComposite %v2uint %uint_0 %uint_0
       %bool = OpTypeBool
    %Outputs = OpTypeStruct %v2uint
%_runtimearr_Outputs = OpTypeRuntimeArray %Outputs
  %OutBuffer = OpTypeStruct %_runtimearr_Outputs
%_ptr_Uniform_OutBuffer = OpTypePointer Uniform %OutBuffer
          %_ = OpVariable %_ptr_Uniform_OutBuffer Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v2uint = OpTypePointer Uniform %v2uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%invocationNdx = OpVariable %_ptr_Function_uint Function
      %time1 = OpVariable %_ptr_Function_v2uint Function
      %time2 = OpVariable %_ptr_Function_v2uint Function
       %out0 = OpVariable %_ptr_Function_v2uint Function
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
         %37 = OpReadClockKHR %v2uint %uint_1
               OpStore %time1 %37
         %39 = OpReadClockKHR %v2uint %uint_1
               OpStore %time2 %39
               OpStore %out0 %41
         %43 = OpAccessChain %_ptr_Function_uint %time1 %uint_1
         %44 = OpLoad %uint %43
         %45 = OpAccessChain %_ptr_Function_uint %time2 %uint_1
         %46 = OpLoad %uint %45
         %47 = OpUGreaterThan %bool %44 %46
         %48 = OpLogicalNot %bool %47
               OpSelectionMerge %50 None
               OpBranchConditional %48 %49 %50
         %49 = OpLabel
         %51 = OpAccessChain %_ptr_Function_uint %time1 %uint_1
         %52 = OpLoad %uint %51
         %53 = OpAccessChain %_ptr_Function_uint %time2 %uint_1
         %54 = OpLoad %uint %53
         %55 = OpIEqual %bool %52 %54
               OpSelectionMerge %57 None
               OpBranchConditional %55 %56 %57
         %56 = OpLabel
         %58 = OpAccessChain %_ptr_Function_uint %time1 %uint_0
         %59 = OpLoad %uint %58
         %60 = OpAccessChain %_ptr_Function_uint %time2 %uint_0
         %61 = OpLoad %uint %60
         %62 = OpUGreaterThan %bool %59 %61
               OpBranch %57
         %57 = OpLabel
         %63 = OpPhi %bool %55 %49 %62 %56
               OpBranch %50
         %50 = OpLabel
         %64 = OpPhi %bool %47 %5 %63 %57
               OpSelectionMerge %66 None
               OpBranchConditional %64 %65 %66
         %65 = OpLabel
         %67 = OpAccessChain %_ptr_Function_uint %out0 %uint_0
               OpStore %67 %uint_1
               OpBranch %66
         %66 = OpLabel
         %75 = OpLoad %uint %invocationNdx
         %76 = OpLoad %v2uint %out0
         %78 = OpAccessChain %_ptr_Uniform_v2uint %_ %int_0 %75 %int_0
               OpStore %78 %76
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Before execution, `checkSupport()` requires `VK_KHR_shader_clock`. It additionally requires the core `shaderInt64` feature for the two 64-bit operations and checks `shaderSubgroupClock` or `shaderDeviceClock` according to the operation scope ([support checks](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L152-L167)).
- `iterate()` allocates 32 `uint64_t` host result slots and initializes every slot to `0xcdcdcdcd`. It passes pointers to the shared shader executor, which executes the selected stage and writes the shader output back ([iteration](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L103-L118)).
- The shader uses `out0.x` as the failure flag. A zero-initialized `out0` therefore represents a non-decreasing pair, while `out0.x = 1` records that the first reading was greater than the second ([output initialization and comparison](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L175-L194)).
- `validateOutput()` passes only when every host slot equals zero. Any nonzero slot causes `iterate()` to return `Result comparison failed`; all-zero output returns `Pass` ([validation](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L114-L125)).

This is an ordering check, not a timestamp-value oracle. The implementation does not require a clock value to be nonzero, does not compare it with a CPU timestamp, does not require a minimum elapsed interval, and accepts equal consecutive readings because only a strict backwards comparison writes the failure value.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `clockARB` | A decreasing subgroup 64-bit clock comparison, or a failure in the generated 64-bit shader and shared execution/output path. |
| `clock2x32ARB` | A decreasing subgroup two-word comparison, incorrect high/low word handling, or a failure in the generated pair-valued shader and shared execution/output path. |
| `clockRealtimeEXT` | A decreasing device 64-bit clock comparison, or a failure in the generated 64-bit shader and shared execution/output path. |
| `clockRealtime2x32EXT` | A decreasing device two-word comparison, incorrect high/low word handling, or a failure in the generated pair-valued shader and shared execution/output path. |

A missing extension or feature follows the support path in `## Case Pruning` and is reported as not supported rather than as evidence that the ordering check failed.

### Cause Analysis

#### Clock ordering failure

**Possible failure symptoms:** One or more invocations return a nonzero output slot, and the case reports `Result comparison failed`. The shader's failure flag means that its generated comparison observed `time1 > time2`.

**Possible implementation causes:** The selected clock implementation or shader execution may have produced a backwards pair of readings, or the compiler may have mishandled the clock builtin or comparison. The host result alone does not distinguish clock semantics, generated GLSL/SPIR-V handling, or execution behavior; source-level and device-level investigation is needed.

#### Two-word comparison failure

**Possible failure symptoms:** A `clock2x32ARB` or `clockRealtime2x32EXT` case reports a nonzero output even when the underlying clock values may be ordered. The affected branch is the lexicographic comparison of `.y` and `.x`.

**Possible implementation causes:** The generated shader, compiler, or execution path may have mishandled the high-word-first comparison, equality condition, or unsigned interpretation. The source establishes the intended comparison, but the host check cannot identify which stage of translation or execution caused a mismatch.

#### Shared shader-executor or result-path failure

**Possible failure symptoms:** A stage or operation reports nonzero output, unchanged sentinel values, or a broad pattern of comparison failures across otherwise unrelated leaves.

**Possible implementation causes:** Generated shader compilation, selected-stage executor setup, pipeline execution, output transport, or host-side result comparison may be involved. The final all-zero scan does not isolate one of these layers, so further source-level tracing is required.

## Case Pruning

### Requirement-based pruning

`ShaderClockCase::checkSupport()` applies the following runtime requirements before execution:

| Requirement | Applies to | Behavior when unavailable |
|---|---|---|
| `VK_KHR_shader_clock` device functionality | All leaves | The case is not supported. |
| `shaderInt64` core feature | `clockARB`, `clockRealtimeEXT` | The case is not supported. |
| `shaderSubgroupClock` feature | `clockARB`, `clock2x32ARB` | The case throws `NotSupportedError`. |
| `shaderDeviceClock` feature | `clockRealtimeEXT`, `clockRealtime2x32EXT` | The case throws `NotSupportedError`. |

The extension requirement is unconditional. The integer feature is conditional on the 64-bit operation, and the clock feature is selected from the operation's `DEVICE` or `SUBGROUP` scope ([support implementation](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L152-L167)). These checks affect support status at runtime; they do not remove the registered leaves from the three-by-four hierarchy.

### Design-based pruning

- The source registers exactly the three shader stages supported by this test group: `vertex`, `fragment`, and `compute` ([stage table](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L239)).
- It registers exactly four operations: two subgroup operations and two device operations, with one 64-bit and one two-word representation in each scope ([operation table](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L227-L230)).
- It does not create separate leaves for clock values, elapsed intervals, invocation-to-invocation comparisons, or other shader stages. Those are outside the source-defined test design.

## Key Takeaways

- `glsl.shader_clock` checks that two reads of one selected clock builtin are non-decreasing within each invocation.
- The matrix contains 12 leaves: four operation forms under each of `vertex`, `fragment`, and `compute`.
- The two-word operations compare `.y` as the high word and `.x` as the low word; the 64-bit operations use a direct `uint64_t` comparison.
- Every invocation must return zero. A nonzero result means the generated comparison observed a backwards ordering or that some shader-executor/output path did not produce the expected value.
- Equal consecutive reads pass, and the test does not assert an absolute timestamp or CPU/device clock relationship.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test instance and validation | [`ShaderClockTestInstance`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L94-L127) | Allocates 32 outputs, invokes the executor, and accepts only all-zero results. |
| Case support and shader specification | [`ShaderClockCase`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L130-L221) | Defines support checks, generated operation source, extensions, and the `out0` output. |
| Operation and stage registration | [`addShaderClockTests()`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L250) | Defines the three stage groups and four operation leaves per stage. |
| Public factory | [`createShaderClockTests()`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L255-L258) | Creates the `shader_clock` group. |
| Public factory declaration | [`vktShaderClockTests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.hpp#L30-L38) | Declares the shader-clock test factory. |
| GLSL package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1279) | Attaches the factory below the GLSL package. |
| Shared source generation and executor selection | [`generateSources()` and `createExecutor()`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L4198-L4259) | Wraps the operation in stage-specific shader-executor generation and execution. |
