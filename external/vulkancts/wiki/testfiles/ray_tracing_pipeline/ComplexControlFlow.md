## Overview

**Core question:** Does a ray tracing pipeline preserve GLSL control-flow semantics (conditionals, switches, loops, nested loops, function calls) when a shader-call instruction is embedded inside that control flow, so the call runs the right number of times on the right payload?

- [vktRayTracingComplexControlFlowTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp) implements and registers the `complexcontrolflow` test family under the `ray_tracing_pipeline` test category.
- Ten test case groups, one per control-flow construct (`if`, `loop`, `switch`, `loop_double_call`, `loop_double_call_sparse`, `nested_loop`, `nested_loop_loop_before`, `nested_loop_loop_after`, `function_call`, `nested_function_call`), each crossed with three shader-call ops (`execute_callable`, `trace_ray`, `report_intersection`) and a per-op set of stages.
- The core idea wraps `executeCallableEXT`, `traceRayEXT`, or `reportIntersectionEXT` inside a nontrivial control-flow block. The shader-call mutates a payload; the host mirrors the same control flow in C++ and compares every written image layer.
- A 3D `r32ui` storage image of size `4 x 4 x 16` carries 16 observable signals per launch: the accumulator at Z = 0, push constants at Z = 1..6, the launch id at Z = 7, and per-iteration or per-branch payload values at Z = 8..15.
- The page explains what each control-flow construct tests, walks through the `if.execute_callable.rgen` shader, and maps each construct's failure to its likely cause.

## Background Knowledge

- **Ray tracing shader-call instructions.** `executeCallableEXT(sbtIndex, location)` runs a callable shader that shares data with the caller through `callableDataEXT` and `callableDataInEXT` variables at the same `location`. `traceRayEXT(...)` runs the traversal pipeline and shares data through `rayPayloadEXT` and `rayPayloadInEXT`. `reportIntersectionEXT(t, hitKind)` is only legal inside an intersection shader and declares a candidate hit. Each instruction suspends the caller, runs another stage, and resumes the caller with side effects visible through the shared storage.
- **Payload-indexed result image.** The callee writes its result to Z = `(payload.x % 8) + 8` with value `payload.y`, then increments `payload.y`. The caller addresses payloads with distinct `.x` values so multiple calls per launch land in distinct Z layers.
- **Push-constant-driven control flow.** Six `uint32_t` push constants (`a`, `b`, `c`, `d`, `hitOfs`, `miss`) drive every branch condition, loop bound, and mask. The rgen echoes them to Z = 1..6 so the host can confirm they arrived intact.
- **`fixed` flag.** `testOp == TEST_OP_REPORT_INTERSECTION` sets `fixed = true`, which suppresses the post-call `v0++` / `v1++` increment in both the shader and the host expected-value formula. The other two ops leave `fixed = false` and the increment applies on both sides.
- **Recursion depth.** When `trace_ray` runs from a stage other than `rgen`, the pipeline sets `maxRayRecursionDepth(2)` so the rgen's initial trace plus the inner trace issued from the tested stage both fit within the limit.

## Registration Hierarchy

```text
ray_tracing_pipeline.complexcontrolflow
├── function_call
├── if
├── loop
├── loop_double_call
├── loop_double_call_sparse
├── nested_function_call
├── nested_loop
├── nested_loop_loop_after
├── nested_loop_loop_before
└── switch
```

Each direct child is an intermediate node that owns three `testOp` subgroups (`execute_callable`, `trace_ray`, `report_intersection`), and each `testOp` owns a per-op set of stage leaves. The full leaf path is `complexcontrolflow.<testType>.<testOp>.<stage>`, with 80 leaves total across the ten test case groups.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| `testType` | `if`, `loop`, `switch`, `loop_double_call`, `loop_double_call_sparse`, `nested_loop`, `nested_loop_loop_before`, `nested_loop_loop_after`, `function_call`, `nested_function_call` | Selects the GLSL control-flow construct that wraps the shader call. This is the primary behavioral axis. | [testTypes array](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1831-L1842) |
| `testOp` | `execute_callable`, `trace_ray`, `report_intersection` | Selects the shader-call instruction placed inside the control flow. | [testOps array](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1822-L1826) |
| `stage` | `rgen`, `chit`, `miss`, `sect`, `call` | Selects the stage that contains the control-flow block. Per-op applicability filters the cross product. | [testStages array](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1812-L1816) |
| Launch size | fixed `4 x 4 x 1` | 16 rays per case, enough to exercise varying `id` values across the grid. | [width/height](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1861-L1862) |
| Result image | fixed `4 x 4 x 16`, `r32ui` | 16 Z-layers carry the per-launch observable signals. | [runTest image setup](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L609-L622) |
| Push constants | per-`testType` values | Drive branch conditions, loop bounds, and masks for each construct. | [getPushConstants](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L476-L550) |

## Behavior Parameters

The primary behavioral axis is `testType`, the registered intermediate node that selects the GLSL control-flow construct wrapped around the shader call. Each value exercises a distinct control-flow property; the shader-call instruction (`testOp`) and containing stage are secondary axes that vary the kind of call and its placement.

### if — conditional branch around a shader call

An `if/else` picks which of two payloads (`v0` at location 0, or `v1` at location 1) the shader call receives. The condition `(p.a & id) != 0` varies across the 4x4 launch grid, so both branches run in the same case. The host mirrors the same `if/else` to compute expected Z = 0 and Z = 8 values. This is the simplest construct and the basis for the representative walkthrough.

### loop — single shader call per iteration with accumulator

A `for (uint x = 0; x < p.a; x++)` loop runs the shader call once per iteration with `v0 = uvec2(x, (p.c & id) + x)`. Each iteration writes to Z = `((x % 8) + 8)` and accumulates `result += v0.y + v1.y + v3.y`. The host mirrors the loop to compute the per-iteration Z layers and the accumulator. This case exercises iteration count correctness and per-iteration payload addressing.

### switch — multi-case selection around a shader call

A `switch (p.a & id)` with cases 0 through 3 plus `default` selects which of `v0`, `v1`, `v2`, `v3` receives `(p.c & id)` while the other three receive `p.b`. Each case also issues a shader call on a distinct payload. The host mirrors the switch to compute the expected `result = v0 + v1 + v2 + v3` and the per-case Z = 8 write. This case exercises case selection and the absence of fall-through.

### loop_double_call — two shader calls per iteration

A `for` loop issues two shader calls per iteration, one on `v0 = uvec2(2*x + 0, (p.c & id) + x)` and one on `v1 = uvec2(2*x + 1, (p.d & id) + x + 1)`. The two calls write to distinct Z layers within the same iteration. This case exercises call ordering and per-call payload isolation when multiple calls share a loop body.

### loop_double_call_sparse — sparse two-call loop with iteration filter

Same as `loop_double_call` but the loop body is guarded by `if ((x & p.b) != 0)`, so only a sparse subset of iterations run the calls. The host mirrors the same filter. This case exercises correct evaluation of the sparse filter and correct skip behavior for excluded iterations.

### nested_loop — doubly-nested loop with index-based filter

A `for (y) for (x)` loop computes `n = x + y * p.a` and guards the call with `if ((n & p.d) != 0)`. The payload is `v0 = uvec2(n, (p.c & id) + n)`. This case exercises nested loop bounds, the `n` index computation, and the inner filter.

### nested_loop_loop_before — accumulator loop followed by shader-call loop

Two sequential loops: the first accumulates `(x + y)` subject to a filter, the second runs the shader call subject to a different filter. This case exercises correct state isolation between the two loops and correct ordering of the accumulator before the call loop.

### nested_loop_loop_after — shader-call loop followed by accumulator loop

Same as `nested_loop_loop_before` but with the shader-call loop first and the accumulator loop second. This case exercises that the after-loop does not perturb the call loop's writes, and that the accumulator runs correctly after the call loop returns.

### function_call — shader call inside a function

A user-defined function `f1()` initializes a local array, issues the shader call, then accumulates the array. The main shader calls `f1()` and adds its return value to `v0.y + v1.y + v3.y`. This case exercises that the shader call runs correctly inside a function scope and that the function's local state is preserved across the call.

### nested_function_call — shader call inside a nested function call stack

A function `f1()` calls `f0()` from inside its own body, and `f0()` issues the shader call. Both functions initialize and accumulate local arrays. This case exercises callable-data side-effect preservation across a nested call stack and correct return to the caller's state after the inner call returns.

## Shader Analysis

The shaders are inline GLSL strings emitted by `initPrograms` with `vk::SPIRV_VERSION_1_4` build options
[vktRayTracingComplexControlFlowTests.cpp#L1233-L1235](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1233-L1235).
A shared `calleeMainPart` body writes the per-payload Z layer and the launch-id echo, then increments `payload.y`
[vktRayTracingComplexControlFlowTests.cpp#L1236-L1241](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1236-L1241).
A `shaderCallInstruction` template substitutes `executeCallableEXT`, `traceRayEXT`, or `reportIntersectionEXT` for the `$` payload-index placeholder
[vktRayTracingComplexControlFlowTests.cpp#L1243-L1251](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1243-L1251).
Per-`testType` `opInMain` blocks wrap that instruction in the tested control flow
[vktRayTracingComplexControlFlowTests.cpp#L1283-L1502](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1283-L1502).

One walkthrough covers the `if.execute_callable.rgen` case because the `if/else` is the most fundamental control-flow construct and cleanly exposes branch-direction payload selection. The same rgen shell drives every `testType`; only the `opInMain` block changes. The shared callable shader is the same across every `execute_callable` case.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
ray_tracing_pipeline.complexcontrolflow.if.execute_callable.rgen
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `if` | The control-flow block is an `if/else` that selects payload `v0` (location 0) or `v1` (location 1) for the callable. |
| `execute_callable` | The shader-call instruction is `executeCallableEXT(0, location)`, which runs the callable at SBT index 0 with the payload at the given location. |
| `rgen` | The control flow lives in the raygen shader. No inner `traceRayEXT` recursion is needed, so `maxRayRecursionDepth` stays at the default. |
| Push constants | `p = {41, 10000, 0x0F, 0xF0, 1, 1}` so `(p.a & id)` varies across the 4x4 grid and both branches run. |

#### Purpose

This case checks that the `if/else` branch direction controls which payload the callable receives, and that the callable's post-call increment lands on the correct `v0.y` or `v1.y`. If the compiler flips the branch, swaps the payload indices, or drops the increment, the host comparison fails on Z = 0 (the accumulator) or Z = 8 (the per-branch payload write).

#### Structural Design

| Step | Stage | Action | Payload effect |
|------|-------|--------|----------------|
| 1 | rgen | Compute `id`, set `v2 = v3 = (0, p.b)` | v2.y = v3.y = p.b |
| 2 | rgen | If `(p.a & id) != 0`: set `v0 = (0, p.c & id)`, `v1 = (0, (p.d & id) + 1)`, call `executeCallableEXT(0, 0)` | callable reads v0, writes Z = 8, increments v0.y |
| 3 | rgen | Else: set `v0 = (0, p.d & id)`, `v1 = (0, (p.c & id) + 1)`, call `executeCallableEXT(0, 1)` | callable reads v1, writes Z = 8, increments v1.y |
| 4 | callable | Write `inValue.y` to Z = `(inValue.x % 8) + 8`, write `id` to Z = 7, increment `inValue.y` | Z = 7 = id, Z = 8 = pre-increment value |
| 5 | rgen | Compute `result = v0.y + v1.y + v2.y + v3.y` (post-increment values) | result includes the incremented v0.y or v1.y |
| 6 | rgen | Write `result` to Z = 0, push constants to Z = 1..6 | host compares all 7 layers |

#### Shader Code

Reconstructed rgen (the tested control-flow block is the `if/else`):

```glsl
#version 460 core
#extension GL_EXT_nonuniform_qualifier : enable
#extension GL_EXT_ray_tracing : require

/// Storage image: 16 Z-layers carry per-launch observable signals.
layout(set = 0, binding = 0, r32ui) uniform uimage3D resultImage;
/// Top-level AS: bound but unused by execute_callable cases (no traceRayEXT in rgen).
layout(set = 0, binding = 1) uniform accelerationStructureEXT as;

/// Push constants drive every branch, loop bound, and mask in the tested control flow.
layout(push_constant) uniform TestParams
{
    uint a;
    uint b;
    uint c;
    uint d;
    uint hitOfs;
    uint miss;
} p;

/// Four callable-data slots; the if/else picks which one the callable receives.
layout(location = 0) callableDataEXT uvec2 v0;
layout(location = 1) callableDataEXT uvec2 v1;
layout(location = 2) callableDataEXT uvec2 v2;
layout(location = 3) callableDataEXT uvec2 v3;

void main()
{
  uint result = 0;
  /// Linear launch id used as the per-pixel discriminator for branch conditions.
  uint id = uint(gl_LaunchIDEXT.x + gl_LaunchSizeEXT.x * gl_LaunchIDEXT.y);
  v2 = v3 = uvec2(0, p.b);

  /// The tested control flow: an if/else that selects payload v0 or v1 for the callable.
  if ((p.a & id) != 0)
      { v0 = uvec2(0, p.c & id); v1 = uvec2(0, (p.d & id) + 1);executeCallableEXT(0, 0); }
  else
      { v0 = uvec2(0, p.d & id); v1 = uvec2(0, (p.c & id) + 1);executeCallableEXT(0, 1); }

  /// After the callable returns, v0.y or v1.y has been incremented by the callee.
  result = v0.y + v1.y + v2.y + v3.y;
  /// Z = 0: the per-launch accumulator (the primary pass/fail signal).
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, 0), uvec4(result, 0, 0, 1));
  /// Z = 1..6: push constants echoed verbatim so the host can confirm they arrived.
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, 1), uvec4(p.a, 0, 0, 1));
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, 2), uvec4(p.b, 0, 0, 1));
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, 3), uvec4(p.c, 0, 0, 1));
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, 4), uvec4(p.d, 0, 0, 1));
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, 5), uvec4(p.hitOfs, 0, 0, 1));
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, 6), uvec4(p.miss, 0, 0, 1));
}
```

Reconstructed callable shader (`cal0`, shared by every `execute_callable` case):

```glsl
#version 460 core
#extension GL_EXT_nonuniform_qualifier : enable
#extension GL_EXT_ray_tracing : require

layout(set = 0, binding = 0, r32ui) uniform uimage3D resultImage;
/// inValue is the callableData slot the caller passed by location.
layout(location = 0) callableDataInEXT uvec2 inValue;

void main()
{
  /// Z = (inValue.x % 8) + 8: per-payload layer addressing.
  uint z = (inValue.x % 8) + 8;
  uint v = inValue.y;
  uint n = gl_LaunchIDEXT.x + gl_LaunchSizeEXT.x * gl_LaunchIDEXT.y;
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, z), uvec4(v, 0, 0, 1));
  /// Z = 7: launch id echo, confirms the callee ran with the right coordinates.
  imageStore(resultImage, ivec3(gl_LaunchIDEXT.x, gl_LaunchIDEXT.y, 7), uvec4(n, 0, 0, 1));
  /// Post-call increment: the caller observes v0.y++ or v1.y++ after the call returns.
  inValue.y++;
}
```

#### Additional Info

- The rgen traces no rays. The `as` binding is present because the descriptor set layout is shared across all cases, but `execute_callable` cases never call `traceRayEXT` from rgen.
- The disassembled rgen below shows `OpSelectionMerge` and `OpBranchConditional` implementing the `if/else`, with one `OpExecuteCallableKHR` in each branch. The merge block reads `v0.y` and `v1.y` after both branches converge, so the post-call increment is visible to the accumulator.
- The callable shader is the same across all `testType` values for `execute_callable`. Only the rgen `opInMain` block changes between cases.

#### Parameter Variation Summary

| Parameter dimension | GLSL-level variation from this walkthrough | Evidence |
|---------------------|--------------------------------------------|----------|
| `testType` | Swaps the `opInMain` block: `if/else` becomes `for`, `switch`, nested `for`, or a function body. The rgen shell, push constants, and image layout stay the same. | [opInMain switch](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1283-L1502) |
| `testOp` | Swaps `executeCallableEXT(0, $)` for `traceRayEXT(..., $)` or `reportIntersectionEXT(1.0f, 0u)`. The payload declaration changes from `callableDataEXT` to `rayPayloadEXT` or `hitAttributeEXT`. | [shaderCallInstruction](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1243-L1251) |
| `stage` | Moves the `opInMain` block from rgen into chit, miss, sect, or an outer callable. Non-rgen stages use `getCommonRayGenerationShader()` for the rgen and add a second SBT hit/miss group for nested `trace_ray`. | [stage switch](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1525-L1738) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `rgen`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 173
; Schema: 0
               OpCapability RayTracingKHR
               OpExtension "SPV_KHR_ray_tracing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint RayGenerationKHR %main "main" %gl_LaunchIDEXT %gl_LaunchSizeEXT %v2 %v3 %p %v0 %v1 %resultImage %as
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_nonuniform_qualifier"
               OpSourceExtension "GL_EXT_ray_tracing"
               OpName %main "main"
               OpName %result "result"
               OpName %id "id"
               OpName %gl_LaunchIDEXT "gl_LaunchIDEXT"
               OpName %gl_LaunchSizeEXT "gl_LaunchSizeEXT"
               OpName %v2 "v2"
               OpName %v3 "v3"
               OpName %TestParams "TestParams"
               OpMemberName %TestParams 0 "a"
               OpMemberName %TestParams 1 "b"
               OpMemberName %TestParams 2 "c"
               OpMemberName %TestParams 3 "d"
               OpMemberName %TestParams 4 "hitOfs"
               OpMemberName %TestParams 5 "miss"
               OpName %p "p"
               OpName %v0 "v0"
               OpName %v1 "v1"
               OpName %resultImage "resultImage"
               OpName %as "as"
               OpDecorate %gl_LaunchIDEXT BuiltIn LaunchIdKHR
               OpDecorate %gl_LaunchSizeEXT BuiltIn LaunchSizeKHR
               OpDecorate %TestParams Block
               OpMemberDecorate %TestParams 0 Offset 0
               OpMemberDecorate %TestParams 1 Offset 4
               OpMemberDecorate %TestParams 2 Offset 8
               OpMemberDecorate %TestParams 3 Offset 12
               OpMemberDecorate %TestParams 4 Offset 16
               OpMemberDecorate %TestParams 5 Offset 20
               OpDecorate %resultImage Binding 0
               OpDecorate %resultImage DescriptorSet 0
               OpDecorate %as Binding 1
               OpDecorate %as DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LaunchIDEXT = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LaunchSizeEXT = OpVariable %_ptr_Input_v3uint Input
     %uint_1 = OpConstant %uint 1
     %v2uint = OpTypeVector %uint 2
%_ptr_CallableDataKHR_v2uint = OpTypePointer CallableDataKHR %v2uint
         %v2 = OpVariable %_ptr_CallableDataKHR_v2uint CallableDataKHR
         %v3 = OpVariable %_ptr_CallableDataKHR_v2uint CallableDataKHR
 %TestParams = OpTypeStruct %uint %uint %uint %uint %uint %uint
%_ptr_PushConstant_TestParams = OpTypePointer PushConstant %TestParams
          %p = OpVariable %_ptr_PushConstant_TestParams PushConstant
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
      %int_0 = OpConstant %int 0
       %bool = OpTypeBool
         %v0 = OpVariable %_ptr_CallableDataKHR_v2uint CallableDataKHR
      %int_2 = OpConstant %int 2
         %v1 = OpVariable %_ptr_CallableDataKHR_v2uint CallableDataKHR
      %int_3 = OpConstant %int 3
%_ptr_CallableDataKHR_uint = OpTypePointer CallableDataKHR %uint
         %86 = OpTypeImage %uint 3D 0 0 0 2 R32ui
%_ptr_UniformConstant_86 = OpTypePointer UniformConstant %86
%resultImage = OpVariable %_ptr_UniformConstant_86 UniformConstant
      %v3int = OpTypeVector %int 3
     %v4uint = OpTypeVector %uint 4
      %int_4 = OpConstant %int 4
      %int_5 = OpConstant %int 5
      %int_6 = OpConstant %int 6
        %170 = OpTypeAccelerationStructureKHR
%_ptr_UniformConstant_170 = OpTypePointer UniformConstant %170
         %as = OpVariable %_ptr_UniformConstant_170 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
     %result = OpVariable %_ptr_Function_uint Function
         %id = OpVariable %_ptr_Function_uint Function
               OpStore %result %uint_0
         %15 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %16 = OpLoad %uint %15
         %18 = OpAccessChain %_ptr_Input_uint %gl_LaunchSizeEXT %uint_0
         %19 = OpLoad %uint %18
         %21 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %22 = OpLoad %uint %21
         %23 = OpIMul %uint %19 %22
         %24 = OpIAdd %uint %16 %23
               OpStore %id %24
         %35 = OpAccessChain %_ptr_PushConstant_uint %p %int_1
         %36 = OpLoad %uint %35
         %37 = OpCompositeConstruct %v2uint %uint_0 %36
               OpStore %v3 %37
               OpStore %v2 %37
         %39 = OpAccessChain %_ptr_PushConstant_uint %p %int_0
         %40 = OpLoad %uint %39
         %41 = OpLoad %uint %id
         %42 = OpBitwiseAnd %uint %40 %41
         %44 = OpINotEqual %bool %42 %uint_0
               OpSelectionMerge %46 None
               OpBranchConditional %44 %45 %62
         %45 = OpLabel
         %49 = OpAccessChain %_ptr_PushConstant_uint %p %int_2
         %50 = OpLoad %uint %49
         %51 = OpLoad %uint %id
         %52 = OpBitwiseAnd %uint %50 %51
         %53 = OpCompositeConstruct %v2uint %uint_0 %52
               OpStore %v0 %53
         %56 = OpAccessChain %_ptr_PushConstant_uint %p %int_3
         %57 = OpLoad %uint %56
         %58 = OpLoad %uint %id
         %59 = OpBitwiseAnd %uint %57 %58
         %60 = OpIAdd %uint %59 %uint_1
         %61 = OpCompositeConstruct %v2uint %uint_0 %60
               OpStore %v1 %61
               OpExecuteCallableKHR %uint_0 %v0
               OpBranch %46
         %62 = OpLabel
         %63 = OpAccessChain %_ptr_PushConstant_uint %p %int_3
         %64 = OpLoad %uint %63
         %65 = OpLoad %uint %id
         %66 = OpBitwiseAnd %uint %64 %65
         %67 = OpCompositeConstruct %v2uint %uint_0 %66
               OpStore %v0 %67
         %68 = OpAccessChain %_ptr_PushConstant_uint %p %int_2
         %69 = OpLoad %uint %68
         %70 = OpLoad %uint %id
         %71 = OpBitwiseAnd %uint %69 %70
         %72 = OpIAdd %uint %71 %uint_1
         %73 = OpCompositeConstruct %v2uint %uint_0 %72
               OpStore %v1 %73
               OpExecuteCallableKHR %uint_0 %v1
               OpBranch %46
         %46 = OpLabel
         %75 = OpAccessChain %_ptr_CallableDataKHR_uint %v0 %uint_1
         %76 = OpLoad %uint %75
         %77 = OpAccessChain %_ptr_CallableDataKHR_uint %v1 %uint_1
         %78 = OpLoad %uint %77
         %79 = OpIAdd %uint %76 %78
         %80 = OpAccessChain %_ptr_CallableDataKHR_uint %v2 %uint_1
         %81 = OpLoad %uint %80
         %82 = OpIAdd %uint %79 %81
         %83 = OpAccessChain %_ptr_CallableDataKHR_uint %v3 %uint_1
         %84 = OpLoad %uint %83
         %85 = OpIAdd %uint %82 %84
               OpStore %result %85
         %89 = OpLoad %86 %resultImage
         %90 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
         %91 = OpLoad %uint %90
         %92 = OpBitcast %int %91
         %93 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
         %94 = OpLoad %uint %93
         %95 = OpBitcast %int %94
         %97 = OpCompositeConstruct %v3int %92 %95 %int_0
         %98 = OpLoad %uint %result
        %100 = OpCompositeConstruct %v4uint %98 %uint_0 %uint_0 %uint_1
               OpImageWrite %89 %97 %100 ZeroExtend
        %101 = OpLoad %86 %resultImage
        %102 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
        %103 = OpLoad %uint %102
        %104 = OpBitcast %int %103
        %105 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
        %106 = OpLoad %uint %105
        %107 = OpBitcast %int %106
        %108 = OpCompositeConstruct %v3int %104 %107 %int_1
        %109 = OpAccessChain %_ptr_PushConstant_uint %p %int_0
        %110 = OpLoad %uint %109
        %111 = OpCompositeConstruct %v4uint %110 %uint_0 %uint_0 %uint_1
               OpImageWrite %101 %108 %111 ZeroExtend
        %112 = OpLoad %86 %resultImage
        %113 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
        %114 = OpLoad %uint %113
        %115 = OpBitcast %int %114
        %116 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
        %117 = OpLoad %uint %116
        %118 = OpBitcast %int %117
        %119 = OpCompositeConstruct %v3int %115 %118 %int_2
        %120 = OpAccessChain %_ptr_PushConstant_uint %p %int_1
        %121 = OpLoad %uint %120
        %122 = OpCompositeConstruct %v4uint %121 %uint_0 %uint_0 %uint_1
               OpImageWrite %112 %119 %122 ZeroExtend
        %123 = OpLoad %86 %resultImage
        %124 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
        %125 = OpLoad %uint %124
        %126 = OpBitcast %int %125
        %127 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
        %128 = OpLoad %uint %127
        %129 = OpBitcast %int %128
        %130 = OpCompositeConstruct %v3int %126 %129 %int_3
        %131 = OpAccessChain %_ptr_PushConstant_uint %p %int_2
        %132 = OpLoad %uint %131
        %133 = OpCompositeConstruct %v4uint %132 %uint_0 %uint_0 %uint_1
               OpImageWrite %123 %130 %133 ZeroExtend
        %134 = OpLoad %86 %resultImage
        %135 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
        %136 = OpLoad %uint %135
        %137 = OpBitcast %int %136
        %138 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
        %139 = OpLoad %uint %138
        %140 = OpBitcast %int %139
        %142 = OpCompositeConstruct %v3int %137 %140 %int_4
        %143 = OpAccessChain %_ptr_PushConstant_uint %p %int_3
        %144 = OpLoad %uint %143
        %145 = OpCompositeConstruct %v4uint %144 %uint_0 %uint_0 %uint_1
               OpImageWrite %134 %142 %145 ZeroExtend
        %146 = OpLoad %86 %resultImage
        %147 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
        %148 = OpLoad %uint %147
        %149 = OpBitcast %int %148
        %150 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
        %151 = OpLoad %uint %150
        %152 = OpBitcast %int %151
        %154 = OpCompositeConstruct %v3int %149 %152 %int_5
        %155 = OpAccessChain %_ptr_PushConstant_uint %p %int_4
        %156 = OpLoad %uint %155
        %157 = OpCompositeConstruct %v4uint %156 %uint_0 %uint_0 %uint_1
               OpImageWrite %146 %154 %157 ZeroExtend
        %158 = OpLoad %86 %resultImage
        %159 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_0
        %160 = OpLoad %uint %159
        %161 = OpBitcast %int %160
        %162 = OpAccessChain %_ptr_Input_uint %gl_LaunchIDEXT %uint_1
        %163 = OpLoad %uint %162
        %164 = OpBitcast %int %163
        %166 = OpCompositeConstruct %v3int %161 %164 %int_6
        %167 = OpAccessChain %_ptr_PushConstant_uint %p %int_5
        %168 = OpLoad %uint %167
        %169 = OpCompositeConstruct %v4uint %168 %uint_0 %uint_0 %uint_1
               OpImageWrite %158 %166 %169 ZeroExtend
               OpReturn
               OpFunctionEnd
```

</details>## Runtime Execution and Result Checking

- **Resource setup.** The host builds one bottom-level AS containing a single AABB geometry. The AABB sits at `z = -1.0f` for hit stages and `z = +1.0f` for the miss stage, so a ray traced straight down `-Z` hits for `chit`, `ahit`, `sect`, and `call` cases, and misses for `miss` cases. A one-instance TLAS wraps the BLAS
  [initBottomAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L439-L461),
  [initTopAccelerationStructure](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L417-L437).
- **Pipeline and SBT.** The pipeline has up to four shader groups: raygen, miss, hit, and callable. The `trace_ray` cases add a second hit group and miss group (`miss2`, `ahit2`, `chit2`, `sect2`) so the inner trace resolves to a different callee. SBTs are built per group with `shaderGroupHandleSize` stride
  [makePipeline](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L342-L396),
  [createShaderBindingTable](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L398-L415).
- **Image clear and barriers.** The 16-layer `r32ui` storage image is cleared to `DEFAULT_CLEAR_VALUE` (999999) in transfer-dst layout, then barriered to `GENERAL` with shader read+write access before the trace
  [runTest barriers](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L629-L664).
- **Push constants.** Six `uint32_t` push constants are pushed once before the trace with `ALL_RAY_TRACING_STAGES` flags, so every shader stage sees the same `p.a` through `p.miss` values
  [cmdPushConstants](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L650-L651).
- **Trace.** `cmdTraceRays` runs a `4 x 4 x 1` launch
  [cmdTraceRays](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L686-L687).
- **Copyback.** A shader-write to transfer-read memory barrier follows the trace, then `cmdCopyImageToBuffer` copies the 16-layer image to a host-visible buffer, and a transfer-write to host-read barrier precedes `submitCommandsAndWait`. The host invalidates the mapped range before reading
  [copyback](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L689-L702).
- **Reference comparison.** `getExpectedValues` builds a 256-element reference vector by mirroring the same `testType` switch in C++. It fills Z = 0 with the per-testType `result` formula, Z = 1..6 with the push constants, Z = 7 with the launch id, and Z = 8..15 with the per-iteration or per-branch payload values. The `iterate` function compares `bufferPtr[pos] != expected[pos]` for every `(z, y, x)` and counts failures
  [getExpectedValues](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L707-L1075),
  [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1077-L1129).
- **Pass/fail.** The instance returns pass iff `failures == 0`; otherwise it returns fail with the failure count. On failure, the host logs a per-Z-layer dump of the actual and expected values for debugging
  [iterate log](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1096-L1123).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `if` | Branch direction mismatch: shader-call ran on the wrong payload, or the post-call increment landed on the wrong `v0` / `v1`, or the `result` sum used the wrong branch's values. |
| `loop` | Loop iteration count or accumulation mismatch: the shader-call ran the wrong number of times, or `result` did not accumulate per-iteration `v0.y + v1.y + v3.y` correctly. |
| `switch` | Case selection or fall-through mismatch: the wrong case body ran for a given `p.a & id`, or the `default` path executed when a defined case should have. |
| `loop_double_call` | Two shader calls per iteration executed in the wrong order, on the wrong payloads, or with wrong per-call `v0` / `v1` values; accumulation diverged. |
| `loop_double_call_sparse` | Sparse iteration filter `(x & p.b) != 0` was evaluated incorrectly, so calls ran on excluded iterations or were skipped on included ones. |
| `nested_loop` | Nested loop bounds or the `n = x + y * p.a` index computation diverged, so the shader-call ran at the wrong `n` or with the wrong `v0`. |
| `nested_loop_loop_before` | The pre-loop accumulator ran the wrong number of iterations or the second loop reused stale state from the first; ordering between the two loops was not preserved. |
| `nested_loop_loop_after` | Same as above but with the inner trace loop first and the accumulator second; the after-loop must not perturb the trace-loop's writes. |
| `function_call` | The `f1()` function did not run the shader-call in its own scope, or its local array initialization and accumulation diverged from the host formula. |
| `nested_function_call` | `f0()` called from `f1()` did not preserve callable-data side effects, or the nested call stack did not return to the correct caller state. |
| (all `testOp` values for a given `testType`) | If failure appears across all three `testOp` values for one `testType`, the cause is the control-flow construct itself, not the specific shader-call instruction. |
| (all `testType` values for one `testOp`/`stage`) | If failure appears across all `testType` values for one `testOp`, the cause is the shader-call instruction or its stage binding, not the control-flow construct. |

### Cause Analysis

#### Branch direction mismatch

**Possible failure symptoms:** For `if`, Z = 0 (the accumulator) differs from the host mirror on launches where the branch direction was flipped. Z = 8 may also differ because the wrong payload was sent to the callable, so the callee wrote the wrong `v.y` value.

**Possible implementation causes:** The SPIR-V uses `OpBranchConditional` on the `(p.a & id) != 0` result. A failure here points to the shader compiler lowering the `if/else` incorrectly, or the runtime mis-evaluating the bitwise-and condition. The host mirrors the same `if/else` in C++ with the same push constants, so a wrong branch direction surfaces as a per-launch mismatch on Z = 0 and Z = 8. Source-level investigation is needed to confirm whether the compiler or the runtime is at fault; the test itself cannot distinguish them.

#### Loop iteration count or accumulation divergence

**Possible failure symptoms:** For `loop`, Z = 0 (the accumulator) diverges because the loop ran the wrong number of iterations or the per-iteration accumulation was wrong. Z = 8..15 may show missing or extra per-iteration writes if the loop count is off, or wrong `v0.y` values if the per-iteration payload was computed incorrectly.

**Possible implementation causes:** The loop bound is `p.a` (a push constant), and the per-iteration payload is `v0 = uvec2(x, (p.c & id) + x)`. A failure here suggests the shader compiler mis-lowered the loop control flow, or the runtime did not preserve the loop counter across the shader-call suspension. The shader-call suspends the caller inside the loop body; on resume, the loop counter and accumulator must be intact.

#### Sparse filter mis-evaluation

**Possible failure symptoms:** For `loop_double_call_sparse`, Z = 8..15 shows writes on iterations where `(x & p.b) != 0` should have excluded them, or missing writes on iterations that should have been included. Z = 0 diverges because the accumulator included or excluded the wrong iterations.

**Possible implementation causes:** The filter is a bitwise-and inside the loop body. A failure here points to the shader compiler mis-evaluating the filter, or the runtime not respecting the filter when scheduling the shader-call. The host mirrors the same filter in C++, so any divergence surfaces as a per-iteration mismatch.

#### Nested loop index computation divergence

**Possible failure symptoms:** For `nested_loop`, Z = 8..15 shows writes at wrong `n` values, or Z = 0 diverges because the accumulator used wrong `n`-indexed `v0.y` values. The `n = x + y * p.a` computation must match between shader and host.

**Possible implementation causes:** The nested loop computes `n` from two loop counters and a push constant. A failure here suggests the shader compiler mis-lowered the nested loop, or the runtime did not preserve both loop counters across the shader-call suspension. The `(n & p.d) != 0` inner filter adds another evaluation point that could diverge.

#### Function-call scope or callable-data preservation

**Possible failure symptoms:** For `function_call` and `nested_function_call`, Z = 0 diverges because the function's return value was wrong, or Z = 8 shows the wrong `v0.y` because the callable-data side effect did not propagate back through the function call stack. For `nested_function_call`, the inner `f0()` call's side effects must be visible to `f1()` after `f0()` returns.

**Possible implementation causes:** The shader-call runs inside a user-defined function. A failure here points to the shader compiler not preserving callable-data storage across the function call boundary, or the runtime not resuming the correct caller state after the callable returns. The nested case adds a second function-call boundary that could lose side effects.

#### Shared image-clear, SBT, or copyback error

**Possible failure symptoms:** A failure that appears across multiple unrelated `testType` or `testOp` cases, or pixels that read back `DEFAULT_CLEAR_VALUE` (999999) instead of any expected value, point to shared infrastructure rather than a specific control-flow construct.

**Possible implementation causes:** The image is cleared to 999999 before the trace and barriered to `GENERAL`. If the clear or barrier did not take effect, the rgen `imageStore` could write over stale data or be invisible to the copy. If `copyImageToBuffer` or the host invalidation missed a layer, the host would read stale or uninitialized memory. These causes are not specific to control flow and would be investigated by checking the barriers and copy region rather than the shader.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline` device functionality, with the `rayTracingPipeline` and `accelerationStructure` feature bits enabled
  [checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1159-L1176).
- The `accelerationStructure` feature is checked as a hard `TestError` rather than `NotSupportedError` because `VK_KHR_ray_tracing_pipeline` depends on it.
- For `trace_ray` cases where the stage is not `rgen`, the pipeline requires `maxRayRecursionDepth >= 2` to allow the rgen's initial trace plus the inner trace issued from the tested stage. Devices with `maxRayRecursionDepth < 2` skip those cases with `NotSupportedError`
  [maxRayRecursionDepth check](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1181-L1186).

### Design-based pruning

- The `report_intersection` op is registered only for the `sect` stage, because `reportIntersectionEXT` is only legal inside an intersection shader. The registration loop skips all other stage combinations for this op via the `applicableInStages` mask `I`
  [testOps array](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1822-L1826).
- The `execute_callable` op is registered for `rgen`, `chit`, `miss`, and `call` (mask `R | C | M | L`). The `call` stage case uses a two-level callable invocation: rgen calls an outer callable (SBT index 1), which calls the inner callable (SBT index 0) from inside the tested control flow.
- The `trace_ray` op is registered for `rgen`, `chit`, and `miss` (mask `R | C | M`). It is not registered for `sect` because `traceRayEXT` from an intersection shader would conflict with the ongoing traversal, and not for `call` because callable shaders cannot trace rays without a recursion depth increase that the test does not exercise.
- Push constants are chosen per `testType` to exercise the relevant branches of each construct. For example, `TEST_TYPE_IF` uses `p.a = 32 | 8 | 1 = 41` so the `(p.a & id)` condition varies across the 4x4 grid, while `TEST_TYPE_LOOP_DOUBLE_CALL_SPARSE` uses `p.a = 16` and `p.b = 5` so the sparse filter `(x & p.b) != 0` excludes roughly half the iterations
  [getPushConstants](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L476-L550).

## Key Takeaways

- The same rgen shell, callable shader, and result-image layout drive every case. Only the `opInMain` block changes between `testType` values, so each case isolates one control-flow construct.
- The `if/else` walkthrough shows the core mechanism: a branch selects which payload the shader call receives, and the host mirrors the same branch to compute the expected accumulator and per-branch Z-layer writes.
- The `fixed` flag distinguishes `report_intersection` from the other two ops: the any-hit callee for `report_intersection` does not increment `inValue.y`, while the callable and miss callees for the other two ops do.
- Failure analysis is by construct: `if` points to branch direction, `loop` to iteration count and accumulation, `switch` to case selection, sparse variants to filter evaluation, nested loops to index computation, and function-call variants to callable-data preservation across function boundaries.
- A failure across all three `testOp` values for one `testType` implicates the control-flow construct; a failure across all `testType` values for one `testOp` implicates the shader-call instruction or its stage binding.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType` and `TestOp` enums | [vktRayTracingComplexControlFlowTests.cpp#L61-L80](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L61-L80) | Defines the ten `testType` and three `testOp` values. |
| `CaseDef` struct | [vktRayTracingComplexControlFlowTests.cpp#L91-L98](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L91-L98) | Carries `testType`, `testOp`, `stage`, and launch dimensions. |
| `getPushConstants` | [vktRayTracingComplexControlFlowTests.cpp#L476-L550](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L476-L550) | Per-`testType` push-constant values that drive branches and loops. |
| `getExpectedValues` | [vktRayTracingComplexControlFlowTests.cpp#L707-L1075](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L707-L1075) | Host-side reference image computation; the source of truth for pass/fail. |
| `initPrograms` GLSL emission | [vktRayTracingComplexControlFlowTests.cpp#L1233-L1788](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1233-L1788) | Generator for every case's shader set; basis for the walkthrough reconstruction. |
| `calleeMainPart` and `shaderCallInstruction` | [vktRayTracingComplexControlFlowTests.cpp#L1236-L1251](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1236-L1251) | Shared callee body and the per-`testOp` shader-call instruction template. |
| `opInMain` per-`testType` switch | [vktRayTracingComplexControlFlowTests.cpp#L1283-L1502](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1283-L1502) | The tested control-flow blocks; source of the `if/else` walkthrough. |
| Pass-through ahit/chit/miss/sect | [vktRayTracingComplexControlFlowTests.cpp#L1189-L1231](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1189-L1231) | No-op stages used when the tested stage is elsewhere. |
| `runTest` host flow | [vktRayTracingComplexControlFlowTests.cpp#L552-L705](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L552-L705) | Image clear, AS build, trace, copyback, host invalidation. |
| `iterate` pass/fail decision | [vktRayTracingComplexControlFlowTests.cpp#L1077-L1129](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1077-L1129) | Element-wise zero-threshold comparison and failure logging. |
| `checkSupport` feature gates | [vktRayTracingComplexControlFlowTests.cpp#L1159-L1187](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1159-L1187) | Requires the two KHR feature bits and `maxRayRecursionDepth >= 2` for nested trace cases. |
| Registration loop | [vktRayTracingComplexControlFlowTests.cpp#L1797-L1884](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1797-L1884) | Builds the `complexcontrolflow.<testType>.<testOp>.<stage>` tree with per-op stage filtering. |
