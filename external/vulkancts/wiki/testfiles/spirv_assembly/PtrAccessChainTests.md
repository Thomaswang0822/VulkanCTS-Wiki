## Overview

**Core question:** Do the two Amber workgroup-pointer scripts produce their common neighbor-read result when the `OpPtrAccessChain` base-pointer type carries `ArrayStride 4` or `ArrayStride 8`?

- This page covers the `spirv_assembly.instruction.compute.ptr_access_chain` test family registered by [`createPtrAccessChainGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73-L78) in [`vktSpvAsmPtrAccessChainTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp).
- The C++ source is a pure Amber dispatcher. It registers two case leaves, `workgroup` and `workgroup_bad_stride`, and attaches the same feature requirements and SPIR-V 1.4 build options to each. All shader text, host buffers, dispatch, and result probing live in the matching `.amber` files under [`spirv_assembly/instruction/compute/ptr_access_chain/`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/).
- Both cases drive `OpPtrAccessChain` over a 17-element workgroup `uint` array. `workgroup` decorates the workgroup `uint` pointer type with `ArrayStride 4`; `workgroup_bad_stride` changes that decoration to `ArrayStride 8`. The scripts retain the same dispatch and output probe.
- The page explains the dispatcher, the shared shader/buffer/probe pattern, the feature gates, and what a failing result points to.

## Background Knowledge

- **`OpPtrAccessChain`.** This instruction adds its `Element` operand, interpreted as a signed element count, to the base pointer before walking any remaining `Indexes` as `OpAccessChain` would. For an object that requires explicit layout, SPIR-V specifies that the stride comes from an `ArrayStride` decoration on the base pointer's type; otherwise the implementation calculates the element address or location. The instruction can form a variable pointer, which is why this shader needs `VariablePointers` for its `Workgroup` pointer path.
- **`ArrayStride` on the base pointer type.** The scripts decorate `%_ptr_Workgroup_uint`, the type of the pointer passed as the `OpPtrAccessChain` base, with `ArrayStride`. The `workgroup` script uses `4`; `workgroup_bad_stride` changes that one operand to `8` but keeps the same result probe. The latter script explicitly says that its added incorrect decoration should be ignored. That comment is the Amber case's intended oracle, not a normative rule that `ArrayStride` is generally ignored: the SPIR-V 1.4 [`OpPtrAccessChain` rule](https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html#OpPtrAccessChain) uses the Base type's `ArrayStride` for explicitly laid-out objects, and [`SPV_KHR_workgroup_memory_explicit_layout`](https://github.khronos.org/SPIRV-Registry/extensions/KHR/SPV_KHR_workgroup_memory_explicit_layout.html) applies that rule to explicitly laid-out Workgroup objects. This page therefore distinguishes the script expectation from the applicable specification semantics and does not generalize either beyond this test's exact pointer shape.
- **Workgroup memory and synchronization.** `Workgroup` storage is shared by the invocations of one workgroup. An `OpControlBarrier` is therefore needed between the stores that initialize the shared array and the cross-invocation loads that read the next element.
- **Feature gates.** `WorkgroupMemoryExplicitLayoutKHR` enables the workgroup explicit-layout path used with this module's `ArrayStride`-decorated pointer type. `VariablePointers` permits the workgroup pointer to be passed to `get_data` and used as the `OpPtrAccessChain` base.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.ptr_access_chain
├── workgroup
└── workgroup_bad_stride
```

Both children are direct test case leaves of the `ptr_access_chain` test family; there are no intermediate nodes. The full registration is mirrored at [spirv-assembly.txt#L9963-L9964](../../../mustpass/main/vk-default/spirv-assembly.txt#L9963-L9964).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pointer `ArrayStride` | `workgroup`, `workgroup_bad_stride` | Selects whether `OpDecorate %_ptr_Workgroup_uint ArrayStride N` uses `4` or `8`. The scripts deliberately retain the same output probe, so this is the only semantic input variation. | [case array](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L49-L52) |
| SPIR-V target | `SPIRV_VERSION_1_4` | Both cases build with SPIR-V 1.4 and `supports_VK_KHR_spirv_1_4`. | [asmOptions](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L40-L41) |
| Required features | `VariablePointerFeatures.variablePointers`, `VK_KHR_workgroup_memory_explicit_layout` | Both cases advertise the same feature and extension requirements to the framework. | [addRequirement calls](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L59-L60) |

## Behavior Parameters

The primary behavioral axis is the pointer-type `ArrayStride` value. The shader body, buffers, dispatch, and probe are identical between the two cases; only the decoration changes from `4` to `8`.

### `workgroup`: correct `ArrayStride` decoration

The shader decorates `%_ptr_Workgroup_uint` with `ArrayStride 4`, which matches the four-byte `uint` representation used by the script. This is the baseline for the common Amber setup: it establishes that the shared `OpPtrAccessChain`, pointer parameter, workgroup data, and probe path can produce the expected neighbor sequence.

### `workgroup_bad_stride`: incorrect `ArrayStride` decoration

The shader decorates `%_ptr_Workgroup_uint` with `ArrayStride 8`, double the representation size used by the script. The Amber header records the test author's expectation that this added decoration is ignored, so this leaf retains the baseline probe `1 2 3 ... 15 0`. It is a focused regression case for that documented CTS expectation, not a general survey of all pointer-layout rules; under the applicable SPIR-V rule, an explicitly laid-out Workgroup `OpPtrAccessChain` uses the Base type's stride.

## Shader Analysis

Both Amber scripts embed the same compute shader; the only difference is the single `OpDecorate %_ptr_Workgroup_uint ArrayStride N` line. The representative walkthrough uses the `workgroup` case because its decoration matches the natural `uint` stride and exposes the addressing logic most cleanly. The `workgroup_bad_stride` case is covered by the Parameter Variation Summary at the end of the walkthrough.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
spirv_assembly.instruction.compute.ptr_access_chain.workgroup
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `workgroup` | Correct `ArrayStride 4` on `%_ptr_Workgroup_uint`, matching the `uint` element size. |
| `LocalSize 16 1 1` | One workgroup of 16 invocations, indexed `0..15` via `gl_LocalInvocationID.x`. |
| Input `A` (binding 0) | `0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15`, so `A[i] = i`. |
| Input `B` (binding 1) | All ones, so `A[i] * B[i] = i`. |
| Output `C` (binding 2) | Pre-filled with `-1` to make unmodified slots visible. |
| Workgroup array `data[17]` | Slots `0..15` hold `A[i]*B[i]`; slot `16` is set to `0` by invocation `0`. |
| `get_data(d)` | Returns `d[1]` via `OpPtrAccessChain`, so `get_data(&data[i]) = data[i+1]`. |
| Probe | `probe ssbo int 0:2 0 == 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0`. |

#### Purpose

This shader runs a 16-invocation workgroup that fills a shared `data[17]` array with `A[i]*B[i]`, sets a sentinel `0` at `data[16]`, synchronizes with a workgroup control barrier, and then writes `get_data(&data[i]) = data[i+1]` into `C[i]` for each invocation. The pass condition is that `C` reads back as `1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0`; each invocation observed its neighbor's value through an `OpPtrAccessChain`-derived pointer.

#### Structural Design

```mermaid
flowchart TD
    A[Host: A, B, C SSBOs<br/>A = 0..15, B = all 1, C = all -1] --> B[Bind SSBOs as<br/>set 0 binding 0/1/2]
    B --> C[Dispatch 1 1 1<br/>= 16 invocations]
    C --> D[i = gl_LocalInvocationID.x]
    D --> E[data[i] = A[i] * B[i] = i]
    E --> F{i == 0?}
    F -- yes --> G[data[16] = 0]
    F -- no --> H[OpControlBarrier<br/>Workgroup scope, AcquireRelease]
    G --> H
    H --> I[p = &data[i] via OpAccessChain]
    I --> J[r = get_data p]
    J --> K[C[i] = r]
    K --> L[Host: probe C ==<br/>1 2 3 ... 15 0]
```

#### Source Code

The SPIR-V assembly below is the literal contents of `workgroup.amber` between `[compute shader spirv]` and `[test]`. It is test data, not reconstructed source, so it is shown verbatim.

```llvm
               OpCapability Shader
               OpCapability VariablePointers
			   OpCapability WorkgroupMemoryExplicitLayoutKHR
               OpExtension "SPV_KHR_storage_buffer_storage_class"
               OpExtension "SPV_KHR_variable_pointers"
			   OpExtension "SPV_KHR_workgroup_memory_explicit_layout"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %30 "main" %gl_LocalInvocationID %20 %22 %23 %24
               OpExecutionMode %30 LocalSize 16 1 1
               OpSource OpenCL_C 120
               OpDecorate %_runtimearr_uint ArrayStride 4
               OpMemberDecorate %_struct_3 0 Offset 0
               OpDecorate %_struct_3 Block
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %22 DescriptorSet 0
               OpDecorate %22 Binding 0
               OpDecorate %23 DescriptorSet 0
               OpDecorate %23 Binding 1
               OpDecorate %24 DescriptorSet 0
               OpDecorate %24 Binding 2
               OpDecorate %_arr_uint_uint_17 ArrayStride 4
               OpDecorate %_ptr_Workgroup_uint ArrayStride 4
       %uint = OpTypeInt 32 0
%_runtimearr_uint = OpTypeRuntimeArray %uint
  %_struct_3 = OpTypeStruct %_runtimearr_uint
%_ptr_StorageBuffer__struct_3 = OpTypePointer StorageBuffer %_struct_3
%_ptr_Workgroup_uint = OpTypePointer Workgroup %uint
          %6 = OpTypeFunction %uint %_ptr_Workgroup_uint
       %void = OpTypeVoid
          %8 = OpTypeFunction %void
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%_ptr_Input_uint = OpTypePointer Input %uint
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
    %uint_17 = OpConstant %uint 17
%_arr_uint_uint_17 = OpTypeArray %uint %uint_17
%_ptr_Workgroup__arr_uint_uint_17 = OpTypePointer Workgroup %_arr_uint_uint_17
       %bool = OpTypeBool
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
     %uint_0 = OpConstant %uint 0
    %uint_16 = OpConstant %uint 16
   %uint_264 = OpConstant %uint 264
         %20 = OpVariable %_ptr_Workgroup__arr_uint_uint_17 Workgroup
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
         %22 = OpVariable %_ptr_StorageBuffer__struct_3 StorageBuffer
         %23 = OpVariable %_ptr_StorageBuffer__struct_3 StorageBuffer
         %24 = OpVariable %_ptr_StorageBuffer__struct_3 StorageBuffer
         %25 = OpFunction %uint Pure %6
         %26 = OpFunctionParameter %_ptr_Workgroup_uint
         %27 = OpLabel
         %28 = OpPtrAccessChain %_ptr_Workgroup_uint %26 %uint_1
         %29 = OpLoad %uint %28
               OpReturnValue %29
               OpFunctionEnd
         %30 = OpFunction %void None %8
         %31 = OpLabel
         %32 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %33 = OpLoad %uint %32
         %34 = OpAccessChain %_ptr_StorageBuffer_uint %22 %uint_0 %33
         %35 = OpLoad %uint %34
         %36 = OpAccessChain %_ptr_StorageBuffer_uint %23 %uint_0 %33
         %37 = OpLoad %uint %36
         %38 = OpIMul %uint %37 %35
         %39 = OpAccessChain %_ptr_Workgroup_uint %20 %33
               OpStore %39 %38
         %40 = OpIEqual %bool %33 %uint_0
               OpSelectionMerge %43 None
               OpBranchConditional %40 %41 %43
         %41 = OpLabel
         %42 = OpAccessChain %_ptr_Workgroup_uint %20 %uint_16
               OpStore %42 %uint_0
               OpBranch %43
         %43 = OpLabel
               OpControlBarrier %uint_2 %uint_1 %uint_264
         %44 = OpFunctionCall %uint %25 %39
         %45 = OpAccessChain %_ptr_StorageBuffer_uint %24 %uint_0 %33
               OpStore %45 %44
               OpReturn
               OpFunctionEnd
```

#### Additional Info

- **Capabilities and entry point.** The shader declares `Shader`, `VariablePointers`, and `WorkgroupMemoryExplicitLayoutKHR`, matched by the `SPV_KHR_variable_pointers` and `SPV_KHR_workgroup_memory_explicit_layout` extensions. The entry point is `%30 "main"` with `OpExecutionMode %30 LocalSize 16 1 1`, so one workgroup runs 16 invocations. `OpSource OpenCL_C 120` records that clspv compiled the shader from OpenCL C, as the amber header comment explains.
- **Decorations.** `%_runtimearr_uint ArrayStride 4` and `%_arr_uint_uint_17 ArrayStride 4` describe the runtime and fixed-size `uint` arrays. `OpDecorate %_ptr_Workgroup_uint ArrayStride 4` is the test-focus line on the `OpPtrAccessChain` base-pointer type. `workgroup_bad_stride` changes only this line to `ArrayStride 8`.
- **Descriptor bindings.** Three `StorageBuffer` variables wrap the same `%_struct_3` block (a runtime array of `uint`). `%22` is descriptor set `0` binding `0` (input `A`), `%23` is set `0` binding `1` (input `B`), and `%24` is set `0` binding `2` (output `C`). All three use `OpDecorate %_struct_3 Block` with `OpMemberDecorate %_struct_3 0 Offset 0`.
- **Built-in and workgroup variables.** `%gl_LocalInvocationID` is the `Input` `v3uint` built-in `LocalInvocationId`. `%20` is the `Workgroup` variable holding the 17-element `uint` array; it is the storage that `OpPtrAccessChain` later walks.
- **`get_data` helper function.** Function `%25` takes a `%_ptr_Workgroup_uint` parameter `%26` and returns `uint`. Its body is `%28 = OpPtrAccessChain %_ptr_Workgroup_uint %26 %uint_1` followed by `%29 = OpLoad %uint %28` and `OpReturnValue %29`. In other words, it returns `d[1]`, the element one past the pointer argument. This is the only `OpPtrAccessChain` in the shader and the focus of the test.
- **`main` body.** Invocation `i = gl_LocalInvocationID.x` (`%33`) loads `A[i]` and `B[i]`, multiplies them, and stores the product into `data[i]` via `%39 = OpAccessChain %_ptr_Workgroup_uint %20 %33`. Invocation `0` additionally stores `0` into `data[16]` via `%42`. `OpControlBarrier %uint_2 %uint_1 %uint_264` has `Workgroup` execution scope, `Device` memory scope, and `AcquireRelease | WorkgroupMemory` semantics (`264 = 8 + 256`), synchronizing the shared-array initialization before the reads. Each invocation then passes `%39` to `get_data` and writes the loaded result to `C[i]`.
- **Pass/fail logic.** With `A[i]=i` and `B[i]=1`, `data[i]=i` for `i=0..15` and `data[16]=0`. `get_data(&data[i])` returns `data[i+1]`, so `C[i] = i+1` for `i=0..14` and `C[15] = data[16] = 0`. The Amber probe `probe ssbo int 0:2 0 == 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0` reads 16 `int` values from SSBO `0:2` starting at byte offset `0` and requires them to equal `1, 2, ..., 15, 0` in order. The case passes only when all 16 entries match.

#### Parameter Variation Summary

The `workgroup_bad_stride` case shares the entire shader body, descriptor layout, workgroup array, control barrier, and probe with the `workgroup` case. The only difference is the single decoration line:

```text
OpDecorate %_ptr_Workgroup_uint ArrayStride 8   ; workgroup_bad_stride only
```

The header comment in `workgroup_bad_stride.amber` records the intended comparison: its added `ArrayStride 8` should be ignored and should give the same results as `ArrayStride == 4`. Accordingly, its expected probe output is identical to the baseline: `1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0`. That is the CTS-script expectation being exercised here, not proof that the decoration is normatively ignored; the applicable SPIR-V 1.4 plus workgroup-explicit-layout rule says the Base type's stride is used for explicitly laid-out Workgroup objects.

## Runtime Execution and Result Checking

- The Amber framework, not CTS host code, owns the runtime. Each `.amber` file declares the `A`, `B`, and `C` SSBOs, the compute pipeline, the descriptor-set bindings, and the dispatch dimensions.
- The compute pipeline attaches the embedded SPIR-V compute shader and binds `A` to set `0` binding `0`, `B` to set `0` binding `1`, and `C` to set `0` binding `2`. The `[require]` section lists `VK_KHR_workgroup_memory_explicit_layout` and `VariablePointerFeatures.variablePointers`, which CTS also advertises through `addRequirement` calls in the dispatcher.
- The dispatch is `compute 1 1 1`, producing one workgroup of 16 invocations. Each invocation fills `data[i]`, invocation `0` sets the `data[16]` sentinel, the workgroup barrier synchronizes the writes, and each invocation reads `data[i+1]` through `OpPtrAccessChain` and stores it into `C[i]`.
- After the dispatch, the Amber `probe ssbo int 0:2 0 == 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0` clause reads back the first 16 `int` values from `C` and compares them in order against the expected sequence. The case passes only when all 16 entries match.
- There is no host-side aggregation: each case is independent and reports its own pass/fail status.

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| `A` buffer | Amber host, prefilled `0..15` | Descriptor set `0` binding `0` | Read by compute shader | No | Provides `A[i] = i`, the multiplicand. |
| `B` buffer | Amber host, prefilled all `1` | Descriptor set `0` binding `1` | Read by compute shader | No | Provides `B[i] = 1`, so `A[i]*B[i] = i`. |
| `C` buffer | Amber host, prefilled all `-1` | Descriptor set `0` binding `2` | Written by compute shader | Yes, via `probe` | Receives `data[i+1]` per invocation; checked entry-by-entry. |
| `data[17]` workgroup variable | Device-side `OpVariable %20 Workgroup` | Workgroup storage | Read and written by compute shader | No | Holds `A[i]*B[i]` plus the `data[16]=0` sentinel; walked by `OpPtrAccessChain`. |
| Compute pipeline | Amber host | Pipeline state | Executes SPIR-V compute shader | No | Runs the embedded SPIR-V assembly. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `workgroup` (`ArrayStride 4`) | A fault in the common `OpPtrAccessChain`/variable-pointer path, workgroup initialization and synchronization, or surrounding buffer accesses. |
| `workgroup_bad_stride` (`ArrayStride 8`) | Any common-path cause above, or behavior that differs from the Amber script's documented expectation that the added `ArrayStride 8` decoration is ignored. |

### Cause Analysis

#### Wrong `OpPtrAccessChain` addressing on a workgroup pointer

**Possible failure symptoms:** The probe differs from `1, 2, ..., 15, 0`. A shifted, repeated, or otherwise wrong neighbor value can show that the pointer passed to `get_data` did not reach the intended next element, but the probe alone does not identify which lowering step was wrong.

**Possible implementation causes:** `%28 = OpPtrAccessChain %_ptr_Workgroup_uint %26 %uint_1` is the focused operation. A defect in element-address calculation, in the transfer of `%39` through the `get_data` parameter, or in the later load can change the returned value. The `VariablePointers` capability permits this `Workgroup` pointer path. The scripts' single final probe cannot distinguish these causes, so a reproducible failure needs inspection of the generated or driver-level code before assigning a location.

#### Different handling of `ArrayStride 8` from the Amber-script expectation

**Possible failure symptoms:** `workgroup_bad_stride` fails while `workgroup` passes. That comparison isolates the one changed decoration, although the final probe does not establish a unique address computation or rule that caused the difference.

**Possible implementation causes:** The `workgroup_bad_stride.amber` header says that its added decoration should be ignored and should give the `ArrayStride == 4` result. An implementation that produces a different result may be handling the `OpPtrAccessChain` base type, its explicit-layout requirements, or related pointer lowering differently from that CTS expectation. Because the applicable SPIR-V rule uses the Base type's `ArrayStride` for explicitly laid-out Workgroup objects, this leaf's result should be reported as a mismatch with the Amber expectation rather than as proof of a universal "ignored stride" rule. The test alone does not establish which semantic or lowering detail explains a mismatch.

#### Wrong control-barrier visibility

**Possible failure symptoms:** The probe can fail intermittently, especially at the last neighbor read if invocation `15` observes `data[16]` before invocation `0` initializes its sentinel. The original CTS fix for this family added the barrier because that race could produce a wrong final array element.

**Possible implementation causes:** `OpControlBarrier %uint_2 %uint_1 %uint_264` has `Workgroup` execution scope, `Device` memory scope, and `AcquireRelease | WorkgroupMemory` semantics. If the implementation fails to apply those synchronization requirements to the shared-array accesses, one invocation can load before another invocation's store becomes available. This is a synchronization path separate from pointer arithmetic; the observed output alone cannot prove the responsible layer.

## Case Pruning

### Requirement-based pruning

Both cases advertise the same requirements through [`addRequirement`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L59-L60) and the amber `[require]` section:

- `VariablePointerFeatures.variablePointers`: needed so a `Workgroup` pointer can be a function parameter and be dereferenced after `OpPtrAccessChain`.
- `VK_KHR_workgroup_memory_explicit_layout`: required by both Amber scripts for the workgroup explicit-layout path and its `WorkgroupMemoryExplicitLayoutKHR` capability.
- SPIR-V 1.4 with `supports_VK_KHR_spirv_1_4`: selected through [`asmOptions`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L40-L41) for both Amber cases.

The whole `ptr_access_chain` test family is non-VulkanSC only. The entire `createTests` body is guarded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L37-L68), so on VulkanSC builds the group registers no cases.

### Design-based pruning

No design-based pruning is applied. The two registered leaves form a baseline and one changed-decoration comparison. No other stride values or memory classes are exercised in this family. A former `workgroup_no_stride` leaf was removed when updated SPIR-V validation required the stride decoration; fixing that module would have duplicated `workgroup` (see the source history for the test-family change).

## Key Takeaways

- The `ptr_access_chain` test family is a pure Amber dispatcher: the C++ source registers two case leaves and their feature requirements, and each case's SPIR-V, buffers, dispatch, and probe live in a matching `.amber` file.
- Both cases run the same compute shader over a 17-element workgroup `uint` array; the only source difference is `OpDecorate %_ptr_Workgroup_uint ArrayStride N`, which is `4` in `workgroup` and `8` in `workgroup_bad_stride`.
- The focused instruction is `%28 = OpPtrAccessChain %_ptr_Workgroup_uint %26 %uint_1` inside `get_data`. The `VariablePointers` and explicit-workgroup-layout gates make that path available to the test.
- Both cases expect `1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0`. The bad-stride script documents that its added `ArrayStride 8` should be ignored, so its identical probe makes that expectation observable.
- A bad-stride-only failure identifies a difference from the scripts' one-decoration comparison; a failure in both leaves may instead involve their shared pointer, workgroup, synchronization, or buffer path. The final probe does not localize the defect further.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createPtrAccessChainGroup` factory | [vktSpvAsmPtrAccessChainTests.cpp#L73-L78](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73-L78) | Defines the `ptr_access_chain` test family and routes it to `createTests`. |
| `createTests` body | [vktSpvAsmPtrAccessChainTests.cpp#L35-L69](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L35-L69) | Registers the two Amber cases, attaches feature/extension requirements, and sets SPIR-V 1.4 build options. |
| Case array | [vktSpvAsmPtrAccessChainTests.cpp#L49-L52](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L49-L52) | Lists the `workgroup` and `workgroup_bad_stride` basenames and their descriptions. |
| Representative Amber script | [workgroup.amber](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup.amber) | Baseline case carrying the embedded SPIR-V assembly, host buffers, dispatch, and probe analyzed in this page. |
| Bad-stride Amber script | [workgroup_bad_stride.amber](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup_bad_stride.amber) | Identical to the baseline except for the single `OpDecorate %_ptr_Workgroup_uint ArrayStride 8` line. |
| Mustpass entry range | [spirv-assembly.txt#L9963-L9964](../../../mustpass/main/vk-default/spirv-assembly.txt#L9963-L9964) | Mirrors the two registered `dEQP-VK.spirv_assembly.instruction.compute.ptr_access_chain.*` case paths. |
