## Overview

**Core question:** Does the implementation reconverge divergent subgroups as required by `VK_KHR_shader_subgroup_uniform_control_flow`?

- This page covers the `subgroups.subgroup_uniform_control_flow` test family, registered by [`createSubgroupUniformControlFlowTests()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L206-L451).
- The C++ code creates `cts_amber::AmberTestCase` instances for GLSL programs loaded from `external/vulkancts/data/vulkan/amber/subgroup_uniform_control_flow/`; it does not provide a page-local shader builder.
- Compute cases vary `large` or `small` workgroups, `full` or `partial` final subgroups, and subgroup-size-control `control` or non-control routes. The separate `discard` family uses a fragment shader.
- The cases exercise reconvergence after branches, loops, early exits, switches, atomics, subgroup votes, nested control flow, and fragment discard. The default mustpass includes the full compute forms and `discard`; all `*partial*` paths are excluded by Issue 4372.

## Background Knowledge

For the shared concepts subgroup identity and active invocations, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- `VK_KHR_shader_subgroup_uniform_control_flow` provides stronger guarantees that a divergent subgroup reconverges in the same manner as invocation groups. The shader requests this behavior with the `SubgroupUniformControlFlowKHR` execution mode, which requires the corresponding feature and supported stage ([extension description](../../../../vulkan-docs/src/appendices/VK_KHR_shader_subgroup_uniform_control_flow.adoc#L21-L34), [SPIR-V environment requirement](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L2742-L2752)).
- The full compute scripts launch 256 local invocations for `large` and 128 for `small`. The corresponding partial scripts launch 238 and 119, respectively, intending to leave the final subgroup not fully populated. This page uses `full` and `partial` as registered test conditions, not as hierarchy terms.

## Registration Hierarchy

```text
subgroups.subgroup_uniform_control_flow
├── large_full
├── large_full_control
├── small_full
├── small_full_control
└── discard
```

C++ registration also adds `large_partial`, `large_partial_control`, `small_partial`, and `small_partial_control`. The default mustpass selection excludes their paths through `dEQP-VK.subgroups.subgroup_uniform_control_flow.*partial*` in [`test-issues.txt`](../../../mustpass/main/src/test-issues.txt#L23-L24), so those source-registered families do not appear in this mustpass-backed hierarchy.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Workgroup size | `large`, `small` | Selects the large or small compute workgroup. Large cases require at least 256 compute workgroup invocations. | [`checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L162-L172), [`createSubgroupUniformControlFlowTests()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L236-L345) |
| Final subgroup occupancy | `full`, `partial` | Full scripts launch 256 (`large`) or 128 (`small`) local invocations; partial scripts use 238 or 119 to exercise a not-fully-populated final subgroup. The source registers both forms. | [`full representative`](../../../data/vulkan/amber/subgroup_uniform_control_flow/large/subgroup_reconverge00.amber#L3-L8), [`partial representative`](../../../data/vulkan/amber/subgroup_uniform_control_flow/large/subgroup_reconverge_partial00.amber#L3-L8) |
| Subgroup-size-control route | non-control, `control` | Control cases require `VK_EXT_subgroup_size_control`, `computeFullSubgroups`, and `subgroupSizeControl`; their Amber pipelines request `FULLY_POPULATED on`. Non-control cases are selected only when `computeFullSubgroups` is not supported. | [`checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L104-L159), [`large_control` pipeline](../../../data/vulkan/amber/subgroup_uniform_control_flow/large_control/subgroup_reconverge00.amber#L60-L81) |
| Reconvergence case | `subgroup_reconverge00` through `subgroup_reconverge20`, with matching `small_` and `_partial` names | Selects the divergent control-flow form loaded from the matching Amber file. | [`large` case registration](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L243-L283), [`small` case registration](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L348-L388) |
| Fragment special case | `subgroup_reconverge_discard00` | Selects the fragment-stage discard program rather than a compute program. | [`discard` registration](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L444-L449) |

The default `subgroups.txt` contains 85 paths for this family: 84 full compute paths and one discard path. It contains no partial paths because of the `*partial*` exclusion. The exact representative path is [`dEQP-VK.subgroups.subgroup_uniform_control_flow.large_full.subgroup_reconverge00`](../../../mustpass/main/vk-default/subgroups.txt#L47724).

## Behavior Parameters

The primary behavioral axis is the reconvergence case. The other dimensions select the workgroup occupancy and feature route in which that control-flow form runs.

### `subgroup_reconverge00` through `subgroup_reconverge20` | divergent control-flow forms

These test case leaves cover distinct ways for invocations to diverge and later reach subgroup operations: `if` and `else`, `do while`, `while` with `break`, volatile conditions, early `return`, loop `break` and `continue`, atomics, divergent `switch`, nested switches, unequal loop counts, subgroup votes, nested returns, and deep nesting. The corresponding Amber file supplies the exact shader for each leaf.

### `large` and `small` | compute workgroup size

The same reconvergence forms run with large and small compute workgroups. A large case uses the `large` Amber directory and must pass the 256-invocation limit check. A small case uses the `small` directory.

### `full` and `partial` | final subgroup occupancy

Full and partial cases use parallel Amber basenames in the same size-specific directories. The full scripts launch 256 (`large`) or 128 (`small`) local invocations; partial scripts launch 238 or 119, intending to leave the final subgroup not fully populated. Source registration includes these cases, but the default mustpass excludes all paths containing `partial` through Issue 4372.

### `control` and non-control | subgroup-size-control route

Control cases use `VK_EXT_subgroup_size_control`, require `computeFullSubgroups` and `subgroupSizeControl` through `addTestsForAmberFiles<true>`, and set `FULLY_POPULATED on` for both Amber compute pipelines. Non-control compute cases require that `computeFullSubgroups` not be supported, because the source selects the complementary test route. Both routes also require `VK_KHR_shader_subgroup_uniform_control_flow`.

### `discard` | fragment discard

`discard` contains the separate `subgroup_reconverge_discard00` fragment case. It is registered with `small_workgroups` true, subgroup-size control disabled, and the fragment stage. It is not one of the compute reconvergence forms.

## Shader Analysis

The representative case is Amber-backed. `addTestsForAmberFiles()` builds the resource path `vulkan/amber/subgroup_uniform_control_flow/large/subgroup_reconverge00.amber`, and `AmberTestCase::parse()` obtains the script from the CTS archive. The walkthrough below reconstructs the exact `test` compute shader from that one Amber script. It does not stand in for the other 20 compute control-flow forms or the fragment `discard` script; those are separate executable Amber artifacts. The representative script's `fill` shader creates the expected marker buffer and is described in `Additional Info` and the runtime section.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.subgroup_uniform_control_flow.large_full.subgroup_reconverge00
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `large_full` | Uses the `large` Amber directory and the full-subgroup compute family. |
| `subgroup_reconverge00` | Selects the Amber case whose main shader uses an outer parity branch, an invocation-0 branch, and `subgroupElect()`. |
| `TARGET_ENV spv1.3` | Selects SPIR-V 1.3 in the Amber script and the corresponding CTS shader-build target. |
| `layout(local_size_x = 128, local_size_y = 2, local_size_z = 1)` | Launches 256 local invocations for the large workgroup. |

#### Purpose

The shader performs divergent updates inside a subgroup-uniform-control-flow entry point and then uses `subgroupElect()` to write one marker per active invocation index. The expected buffer is an independently generated active/elected mask: an active subgroup writes one `1` and zeros for its other active invocations, while indices for a subgroup that skips the outer branch remain at the initial value `4`.

#### Structural Design

```mermaid
flowchart TD
    A[Compute subgroup-local index] --> B{a[a subgroup ID] is even?}
    B -->|no| E[Leave b at its initial value]
    B -->|yes| C{Subgroup invocation ID is zero?}
    C -->|yes| D[Add 4 to c at idx]
    C -->|no| F[Increment c at idx]
    D --> G[subgroupElect selects one invocation]
    F --> G
    G --> H[Write elected marker to b at idx]
    E --> I[End]
    H --> I
```

#### Shader Code

```glsl
#version 450 core
#extension GL_KHR_shader_subgroup_basic : enable
#extension GL_KHR_shader_subgroup_ballot : enable
#extension GL_EXT_subgroup_uniform_control_flow : enable
layout(local_size_x = 128, local_size_y = 2, local_size_z = 1) in;

/// Binding 0 is a coherent storage buffer containing one parity selector per subgroup.
layout(set=0, binding=0) coherent buffer A { uint a[]; } a;
/// Binding 1 is a coherent storage buffer receiving the elected-invocation marker.
layout(set=0, binding=1) coherent buffer B { uint b[]; } b;
/// Binding 2 is a coherent storage buffer updated by the two divergent invocation paths.
layout(set=0, binding=2) coherent buffer C { uint c[]; } c;
/// Binding 3 is declared by the Amber test pipeline but is not accessed by this shader.
layout(set=0, binding=3) coherent buffer D { uint d[]; } d;

/// The execution mode supplies the subgroup-uniform-control-flow guarantee tested by this case.
void main()
[[subgroup_uniform_control_flow]]
{
  /// Map a subgroup and its local invocation to the storage-buffer index used by Amber.
  uint idx = gl_SubgroupID * gl_SubgroupSize + gl_SubgroupInvocationID;
  /// Only subgroups whose selector is even enter the divergent region.
  if (a.a[gl_SubgroupID] % 2 == 0) {
    /// One invocation follows the add path; all other invocations increment their element.
    if (gl_SubgroupInvocationID == 0) {
      c.c[idx] += 4;
    } else {
      c.c[idx]++;
    }
    /// Exactly one elected invocation stores 1; other invocations store 0.
    b.b[idx] = subgroupElect() ? 1 : 0;
  }
}
```

#### Additional Info

- The representative Amber script also defines a `fill` compute shader. For an even selector it writes `1` at the invocation elected by that shader execution and `0` at the other active indices; for an odd selector it writes `4`.
- `a` is initialized with the series 0 through 255, while `b` and `c` start filled with 4. `d` is filled with 0 and remains unused by the shown `test` shader.
- The `test` shader uses the exact source from [`subgroup_reconverge00.amber`](../../../data/vulkan/amber/subgroup_uniform_control_flow/large/subgroup_reconverge00.amber#L1-L28); the `///` comments are wiki annotations.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `large` versus `small` | Selects Amber subdirectories and corresponding workgroup-size metadata; the control-flow form remains the same family of reconvergence cases. | [`createSubgroupUniformControlFlowTests()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L236-L345) |
| `full` versus `partial` | Selects full or partial Amber basenames and directories, changing final subgroup occupancy while retaining the reconvergence case shape. | [`partial` registration](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L289-L336) |
| `control` versus non-control | Selects the `large_control` or `large` Amber directory and the matching support requirements. | [`control` registration](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L233-L287) |
| `subgroup_reconverge01` through `subgroup_reconverge20` | Replaces the branch body with the corresponding Amber control-flow form, including loops, exits, switches, atomics, votes, or nesting. | [`large` reconvergence case list](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L243-L283) |

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
; Bound: 73
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpExtension "SPV_KHR_subgroup_uniform_control_flow"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_SubgroupID %gl_SubgroupSize %gl_SubgroupInvocationID
               OpExecutionMode %main SubgroupUniformControlFlowKHR
               OpExecutionMode %main LocalSize 128 2 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_subgroup_uniform_control_flow"
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %idx "idx"
               OpName %gl_SubgroupID "gl_SubgroupID"
               OpName %gl_SubgroupSize "gl_SubgroupSize"
               OpName %gl_SubgroupInvocationID "gl_SubgroupInvocationID"
               OpName %A "A"
               OpMemberName %A 0 "a"
               OpName %a "a"
               OpName %C "C"
               OpMemberName %C 0 "c"
               OpName %c "c"
               OpName %B "B"
               OpMemberName %B 0 "b"
               OpName %b "b"
               OpName %D "D"
               OpMemberName %D 0 "d"
               OpName %d "d"
               OpDecorate %gl_SubgroupID BuiltIn SubgroupId
               OpDecorate %gl_SubgroupSize RelaxedPrecision
               OpDecorate %gl_SubgroupSize BuiltIn SubgroupSize
               OpDecorate %13 RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID RelaxedPrecision
               OpDecorate %gl_SubgroupInvocationID BuiltIn SubgroupLocalInvocationId
               OpDecorate %16 RelaxedPrecision
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpDecorate %A Block
               OpMemberDecorate %A 0 Coherent
               OpMemberDecorate %A 0 Offset 0
               OpDecorate %a Coherent
               OpDecorate %a Binding 0
               OpDecorate %a DescriptorSet 0
               OpDecorate %35 RelaxedPrecision
               OpDecorate %_runtimearr_uint_0 ArrayStride 4
               OpDecorate %C Block
               OpMemberDecorate %C 0 Coherent
               OpMemberDecorate %C 0 Offset 0
               OpDecorate %c Coherent
               OpDecorate %c Binding 2
               OpDecorate %c DescriptorSet 0
               OpDecorate %_runtimearr_uint_1 ArrayStride 4
               OpDecorate %B Block
               OpMemberDecorate %B 0 Coherent
               OpMemberDecorate %B 0 Offset 0
               OpDecorate %b Coherent
               OpDecorate %b Binding 1
               OpDecorate %b DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
               OpDecorate %_runtimearr_uint_2 ArrayStride 4
               OpDecorate %D Block
               OpMemberDecorate %D 0 Coherent
               OpMemberDecorate %D 0 Offset 0
               OpDecorate %d Coherent
               OpDecorate %d Binding 3
               OpDecorate %d DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_SubgroupID = OpVariable %_ptr_Input_uint Input
%gl_SubgroupSize = OpVariable %_ptr_Input_uint Input
%gl_SubgroupInvocationID = OpVariable %_ptr_Input_uint Input
%_runtimearr_uint = OpTypeRuntimeArray %uint
          %A = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer_A = OpTypePointer StorageBuffer %A
          %a = OpVariable %_ptr_StorageBuffer_A StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
     %uint_2 = OpConstant %uint 2
     %uint_0 = OpConstant %uint 0
       %bool = OpTypeBool
%_runtimearr_uint_0 = OpTypeRuntimeArray %uint
          %C = OpTypeStruct %_runtimearr_uint_0
%_ptr_StorageBuffer_C = OpTypePointer StorageBuffer %C
          %c = OpVariable %_ptr_StorageBuffer_C StorageBuffer
     %uint_4 = OpConstant %uint 4
      %int_1 = OpConstant %int 1
%_runtimearr_uint_1 = OpTypeRuntimeArray %uint
          %B = OpTypeStruct %_runtimearr_uint_1
%_ptr_StorageBuffer_B = OpTypePointer StorageBuffer %B
          %b = OpVariable %_ptr_StorageBuffer_B StorageBuffer
     %uint_3 = OpConstant %uint 3
     %v3uint = OpTypeVector %uint 3
   %uint_128 = OpConstant %uint 128
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_128 %uint_2 %uint_1
%_runtimearr_uint_2 = OpTypeRuntimeArray %uint
          %D = OpTypeStruct %_runtimearr_uint_2
%_ptr_StorageBuffer_D = OpTypePointer StorageBuffer %D
          %d = OpVariable %_ptr_StorageBuffer_D StorageBuffer
       %main = OpFunction %void None %3
          %5 = OpLabel
        %idx = OpVariable %_ptr_Function_uint Function
         %11 = OpLoad %uint %gl_SubgroupID
         %13 = OpLoad %uint %gl_SubgroupSize
         %14 = OpIMul %uint %11 %13
         %16 = OpLoad %uint %gl_SubgroupInvocationID
         %17 = OpIAdd %uint %14 %16
               OpStore %idx %17
         %24 = OpLoad %uint %gl_SubgroupID
         %26 = OpAccessChain %_ptr_StorageBuffer_uint %a %int_0 %24
         %27 = OpLoad %uint %26
         %29 = OpUMod %uint %27 %uint_2
         %32 = OpIEqual %bool %29 %uint_0
               OpSelectionMerge %34 None
               OpBranchConditional %32 %33 %34
         %33 = OpLabel
         %35 = OpLoad %uint %gl_SubgroupInvocationID
         %36 = OpIEqual %bool %35 %uint_0
               OpSelectionMerge %38 None
               OpBranchConditional %36 %37 %49
         %37 = OpLabel
         %43 = OpLoad %uint %idx
         %45 = OpAccessChain %_ptr_StorageBuffer_uint %c %int_0 %43
         %46 = OpLoad %uint %45
         %47 = OpIAdd %uint %46 %uint_4
         %48 = OpAccessChain %_ptr_StorageBuffer_uint %c %int_0 %43
               OpStore %48 %47
               OpBranch %38
         %49 = OpLabel
         %50 = OpLoad %uint %idx
         %51 = OpAccessChain %_ptr_StorageBuffer_uint %c %int_0 %50
         %52 = OpLoad %uint %51
         %54 = OpIAdd %uint %52 %int_1
               OpStore %51 %54
               OpBranch %38
         %38 = OpLabel
         %59 = OpLoad %uint %idx
         %61 = OpGroupNonUniformElect %bool %uint_3
         %62 = OpSelect %int %61 %int_1 %int_0
         %63 = OpBitcast %uint %62
         %64 = OpAccessChain %_ptr_StorageBuffer_uint %b %int_0 %59
               OpStore %64 %63
               OpBranch %34
         %34 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `addTestsForAmberFiles()` constructs the filename from the data directory, subdirectory, and basename, then creates `SubgroupUniformControlFlowTestCase`, a subclass of `cts_amber::AmberTestCase`.
- `AmberTestCase::parse()` loads and parses the script during delayed initialization. `AmberTestCase::initPrograms()` maps each Amber GLSL compute shader to `glu::ComputeSource` and uses the script's `spv1.3` target as `vk::SPIRV_VERSION_1_3`.
- Amber creates `fill_pipe` with buffers `a`, `c`, and `compare`. `RUN fill_pipe 1 1 1` writes the expected `compare` data.
- Amber creates `test_pipe` with buffers `a`, `b`, `c`, and `d`. `RUN test_pipe 1 1 1` runs the representative shader once.
- The script first sanity-checks the fill result at index 0 with `EXPECT compare IDX 0 EQ 1 0 0 0`, then checks the test shader's entire `b` buffer with `EXPECT b EQ_BUFFER compare`. Buffers `c` and `d` support the control-flow forms but are not directly compared by this representative script, so a pass proves the post-control-flow election marker rather than every intermediate side effect.
- The separate discard script renders an `expect` integer attachment without discard and a `compare` attachment with the subgroup-uniform-control-flow fragment shader, then requires `EXPECT compare EQ_BUFFER expect`. Its `out1` and `out2` attachments steer shader writes but are not part of the final comparison.
- `AmberTestInstance::iterate()` executes the recipe, logs an Amber error if execution fails, and returns CTS `Pass` for Amber success or `Fail` otherwise.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroup_reconverge00` through `subgroup_reconverge20` | Incorrect subgroup reconvergence or compiler/control-flow lowering for the selected branch, loop, early-exit, switch, atomic, vote, or nested-control-flow form. |
| `large` or `small` | Incorrect handling of the corresponding compute workgroup size or its subgroup indexing. |
| `full` or `partial` | Incorrect handling of final subgroup occupancy. Partial values are source-registered but excluded from default mustpass by Issue 4372. |
| `control` or non-control | Incorrect feature or subgroup-size-control variant selection, including execution with the wrong `computeFullSubgroups` support route. |
| `subgroup_reconverge_discard00` | Incorrect fragment-stage subgroup behavior when invocations discard. |

### Cause Analysis

#### Reconvergence control-flow forms

**Possible failure symptoms:** The post-control-flow election-marker comparison fails for a branch, loop, early exit, switch, atomic-assisted, subgroup-vote, or nested-control-flow case. In the representative case, `b` differs from `compare`, or the independent fill shader fails its `compare` sanity check. Intermediate `c` and `d` side effects are not themselves the oracle.

**Possible implementation causes:** The implementation may lower the selected divergent construct without preserving the execution-mode reconvergence guarantee, or the compiler may generate control flow that changes which invocations reach `subgroupElect()`. The exact cause depends on the selected Amber shader and needs source-level investigation for a failing form.

#### Workgroup size and subgroup indexing

**Possible failure symptoms:** A compute case fails only for `large` or `small`, or expected entries do not line up with the `gl_SubgroupID * gl_SubgroupSize + gl_SubgroupInvocationID` indexing used by the shaders.

**Possible implementation causes:** The implementation may execute the registered local size incorrectly, expose inconsistent subgroup built-ins, or mishandle indexing at the chosen workgroup shape. A failing result does not by itself identify hardware, driver, compiler, or host code as the cause.

#### Final subgroup occupancy

**Possible failure symptoms:** A full or partial variant produces a mismatch in its Amber expectation after the same reconvergence form runs. The default mustpass does not exercise partial paths because Issue 4372 excludes them.

**Possible implementation causes:** The implementation may form or schedule the final subgroup contrary to the selected occupancy condition. For a partial-case failure, source-level investigation is needed because the default mustpass exclusion removes that result from the normal conformance selection.

#### Feature and subgroup-size-control route

**Possible failure symptoms:** A control or non-control case is reported unsupported, or its execution produces a result mismatch under the selected feature route.

**Possible implementation causes:** The implementation may advertise `computeFullSubgroups` inconsistently with the selected route, fail the required extension or operation support check, or apply a different subgroup-size-control behavior than the test expects. The source checks these support conditions before Amber execution.

#### Fragment discard

**Possible failure symptoms:** `subgroup_reconverge_discard00` produces a `compare` integer attachment different from the separately rendered `expect` attachment. The tested shader reports `-1` if election changes across the discard region or if an elected out-of-bounds invocation would discard; the reference expects `1` in bounds and `-1` outside.

**Possible implementation causes:** The fragment implementation or shader lowering may handle active-lane participation and reconvergence differently from the behavior required by the Amber case. Source-level investigation is needed to identify the failing stage or operation.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_shader_subgroup_uniform_control_flow` and a stage with subgroup operations supported.
- Control variants require `VK_EXT_subgroup_size_control`, `computeFullSubgroups`, and `subgroupSizeControl`. The source uses `addRequirement()` for the latter two when adding control cases.
- The source checks that the required subgroup operation mask is supported. Vote cases `subgroup_reconverge18`, `subgroup_reconverge19`, and their corresponding variants require the vote operation in addition to basic operations.
- Large compute cases require at least 256 invocations per compute workgroup.

### Design-based pruning

- The source registers the same 21 reconvergence forms across the large or small, full or partial, and control or non-control compute families. This separates occupancy and feature conditions from control-flow behavior.
- The source also registers four partial compute families, but [`test-issues.txt`](../../../mustpass/main/src/test-issues.txt#L23-L24) excludes every path containing `partial` from the default mustpass. The cases remain in source registration and can matter to targeted runs; they are not default mustpass evidence.
- The `discard` family is a separate fragment-stage design, not another compute-size variant.

## Key Takeaways

- This page tests reconvergence behavior through Amber-loaded shaders, not through a C++ `initPrograms` builder specific to this family.
- The primary behavioral choices are the 21 reconvergence forms. Workgroup size, final subgroup occupancy, and subgroup-size-control route define the conditions around each form.
- Source registration and mustpass selection differ: partial families are registered in C++, but the default mustpass excludes all `*partial*` paths.
- The representative shader makes the execution mode visible in SPIR-V as `SubgroupUniformControlFlowKHR` and checks the elected invocation marker against Amber-generated expected data.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createSubgroupUniformControlFlowTests()` | [`large`, `small`, partial, and discard registration](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L206-L451) | Defines the direct families, exact case leaves, stage, occupancy, and subgroup-size-control parameters. |
| `SubgroupUniformControlFlowTestCase::checkSupport()` | [`checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L99-L172) | Applies extension, operation, subgroup-size-control, and large-workgroup checks. |
| `addTestsForAmberFiles()` | [`addTestsForAmberFiles()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L175-L201) | Constructs the Amber resource filename and the Amber-backed test case. |
| `AmberTestCase::parse()` and `initPrograms()` | [`parse()` and `initPrograms()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L475) | Parses the script and maps its GLSL shader metadata to CTS shader sources and the requested SPIR-V target. |
| `AmberTestInstance::iterate()` | [`iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Executes the Amber recipe and maps Amber success or failure to CTS status. |
| Representative Amber program | [`subgroup_reconverge00.amber`](../../../data/vulkan/amber/subgroup_uniform_control_flow/large/subgroup_reconverge00.amber#L1-L76) | Defines the exact `fill` and `test` shaders, resources, pipelines, runs, and expectations. |
| Default mustpass selection | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L47723-L47742) | Lists the selected discard and large full paths, including the representative case. |
| Partial-case exclusion | [`test-issues.txt`](../../../mustpass/main/src/test-issues.txt#L23-L24) | Excludes all default mustpass paths containing `partial`. |
| Dispatcher registration | [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L45) and [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L77-L81) | Includes and attaches this test family only for non-VulkanSC builds. |
| Vulkan uniform-control-flow semantics | [`VK_KHR_shader_subgroup_uniform_control_flow`](../../../../vulkan-docs/src/appendices/VK_KHR_shader_subgroup_uniform_control_flow.adoc#L21-L34) and [`spirvenv.adoc`](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L2742-L2752) | Grounds the reconvergence guarantee and execution-mode prerequisites. |
