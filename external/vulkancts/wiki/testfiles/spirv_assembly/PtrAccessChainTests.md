## Overview

**Core question:** Does the implementation compute `OpPtrAccessChain` addressing on a workgroup pointer using the natural stride of the pointed-to type, ignoring any non-standard `ArrayStride` decoration placed on the pointer type itself?

- This page covers the `spirv_assembly.instruction.compute.ptr_access_chain` test family registered by [`createPtrAccessChainGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73-L78) in [`vktSpvAsmPtrAccessChainTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp).
- The C++ source is a pure Amber dispatcher. It registers two case leaves, `workgroup` and `workgroup_bad_stride`, and attaches the same feature requirements and SPIR-V 1.4 build options to each. All shader text, host buffers, dispatch, and result probing live in the matching `.amber` files under [`spirv_assembly/instruction/compute/ptr_access_chain/`](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/).
- Both cases drive `OpPtrAccessChain` over a 17-element workgroup `uint` array. The `workgroup` case decorates the workgroup `uint` pointer type with a correct `ArrayStride 4`. The `workgroup_bad_stride` case decorates the same pointer type with `ArrayStride 8`, a value that does not match the `uint` element size and is not a legal place for the decoration to take effect.
- The page explains the dispatcher, the shared shader/buffer/probe pattern, the feature gates, and what a failing result points to.

## Background Knowledge

- **`OpPtrAccessChain`.** SPIR-V's `OpPtrAccessChain` walks a pointer by a runtime element index, producing a new pointer to `base[index]`. The byte offset it adds is `index * sizeof(pointed-to type)`. The stride comes from the pointed-to type's natural layout, not from any decoration on the pointer type. This differs from `OpAccessChain`, which only walks compile-time-constant structure-member or array-index paths and cannot take a runtime-variable element offset on a plain pointer.
- **`ArrayStride` decoration.** `ArrayStride` is a layout decoration that the SPIR-V spec defines for array types (and structure members holding an array). It tells consumers how many bytes one array element occupies. Decorating a *pointer* type with `ArrayStride` is non-standard: the spec does not define a meaning for it there, so a conformant consumer must ignore the decoration when computing `OpPtrAccessChain` offsets and fall back to the pointed-to type's natural size.
- **`VK_KHR_workgroup_memory_explicit_layout` and `VariablePointers`.** The shader declares the `WorkgroupMemoryExplicitLayoutKHR` capability so a `Workgroup` variable can use an explicit `OpTypeArray` layout, and the `VariablePointers` capability so a `Workgroup` pointer can be passed as a function parameter and dereferenced after a `OpPtrAccessChain`. Both are required for the test shader to be legal.

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
| Stride correctness | `workgroup`, `workgroup_bad_stride` | Selects whether the `OpDecorate %_ptr_Workgroup_uint ArrayStride N` line uses the correct value `4` (matching `uint` size) or the incorrect value `8`. The pointer-type decoration should not affect `OpPtrAccessChain` addressing in either case. | [case array](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L49-L52) |
| SPIR-V target | `SPIRV_VERSION_1_4` | Both cases build with SPIR-V 1.4 and `supports_VK_KHR_spirv_1_4`. | [asmOptions](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L40-L41) |
| Required features | `VariablePointerFeatures.variablePointers`, `VK_KHR_workgroup_memory_explicit_layout` | Both cases advertise the same feature and extension requirements to the framework. | [addRequirement calls](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L59-L60) |

## Behavior Parameters

The primary behavioral axis is the stride-correctness leaf: the two test case leaves each probe one value of the pointer-type `ArrayStride` decoration. The shader body, buffers, dispatch, and probe are identical between the two cases, so the only thing that changes is whether the decoration is correct or deliberately wrong.

### `workgroup`: correct `ArrayStride` decoration

The shader decorates `%_ptr_Workgroup_uint` with `ArrayStride 4`, matching the 4-byte size of `uint`. This is the baseline case: the decoration happens to agree with the natural element stride, so a consumer that honors it and a consumer that ignores it both produce the same addressing. The case exists to confirm the surrounding `OpPtrAccessChain` plumbing works end-to-end before the bad-stride variant tests the ignore-the-decoration rule.

### `workgroup_bad_stride`: incorrect `ArrayStride` decoration

The shader decorates `%_ptr_Workgroup_uint` with `ArrayStride 8`, double the real `uint` size. Because `ArrayStride` is not defined for pointer types, a conformant consumer must ignore the decoration and compute `OpPtrAccessChain` offsets using the pointed-to `uint` type's natural 4-byte stride. The case shares its buffers, dispatch, and probe with the baseline, so it produces the same expected output `1 2 3 ... 15 0` when the implementation ignores the bad decoration.

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
- **Decorations.** `%_runtimearr_uint ArrayStride 4` and `%_arr_uint_uint_17 ArrayStride 4` are the legal array-stride decorations: they describe the storage-buffer runtime array and the workgroup fixed-size array, both of which hold 4-byte `uint` elements. `OpDecorate %_ptr_Workgroup_uint ArrayStride 4` is the test-focus line, a stride decoration placed on a *pointer* type, where the spec does not define it. The `workgroup_bad_stride` case changes this single line to `ArrayStride 8` and nothing else.
- **Descriptor bindings.** Three `StorageBuffer` variables wrap the same `%_struct_3` block (a runtime array of `uint`). `%22` is descriptor set `0` binding `0` (input `A`), `%23` is set `0` binding `1` (input `B`), and `%24` is set `0` binding `2` (output `C`). All three use `OpDecorate %_struct_3 Block` with `OpMemberDecorate %_struct_3 0 Offset 0`.
- **Built-in and workgroup variables.** `%gl_LocalInvocationID` is the `Input` `v3uint` built-in `LocalInvocationId`. `%20` is the `Workgroup` variable holding the 17-element `uint` array; it is the storage that `OpPtrAccessChain` later walks.
- **`get_data` helper function.** Function `%25` takes a `%_ptr_Workgroup_uint` parameter `%26` and returns `uint`. Its body is `%28 = OpPtrAccessChain %_ptr_Workgroup_uint %26 %uint_1` followed by `%29 = OpLoad %uint %28` and `OpReturnValue %29`. In other words, it returns `d[1]`, the element one past the pointer argument. This is the only `OpPtrAccessChain` in the shader and the focus of the test.
- **`main` body.** Invocation `i = gl_LocalInvocationID.x` (`%33`) loads `A[i]` and `B[i]`, multiplies them, and stores the product into `data[i]` via `%39 = OpAccessChain %_ptr_Workgroup_uint %20 %33`. Invocation `0` additionally stores `0` into `data[16]` via `%42`. `OpControlBarrier %uint_2 %uint_1 %uint_264` then issues a workgroup-scope, AcquireRelease barrier (execution scope `Workgroup`, memory scope `Device`, semantics `264 = AcquireRelease | CrossWorkgroupMemory`) so every `data[i]` write is visible before any read. Each invocation then calls `get_data(&data[i])`, passing the pointer `%39` it just stored through, and writes the returned `data[i+1]` into `C[i]`.
- **Pass/fail logic.** With `A[i]=i` and `B[i]=1`, `data[i]=i` for `i=0..15` and `data[16]=0`. `get_data(&data[i])` returns `data[i+1]`, so `C[i] = i+1` for `i=0..14` and `C[15] = data[16] = 0`. The Amber probe `probe ssbo int 0:2 0 == 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0` reads 16 `int` values from SSBO `0:2` starting at byte offset `0` and requires them to equal `1, 2, ..., 15, 0` in order. The case passes only when all 16 entries match.

#### Parameter Variation Summary

The `workgroup_bad_stride` case shares the entire shader body, descriptor layout, workgroup array, control barrier, and probe with the `workgroup` case. The only difference is the single decoration line:

```text
OpDecorate %_ptr_Workgroup_uint ArrayStride 8   ; workgroup_bad_stride only
```

Because `ArrayStride` is not defined for pointer types, the implementation must ignore this decoration and continue to use the `uint` element's natural 4-byte stride for `OpPtrAccessChain`. The amber header comment for `workgroup_bad_stride.amber` records this intent: the incorrect decoration should be ignored, and the case should give the same results as `ArrayStride == 4`. The expected probe output is therefore identical to the baseline: `1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0`.

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
| `workgroup` (correct `ArrayStride 4`) | Wrong `OpPtrAccessChain` addressing on a workgroup pointer, wrong control-barrier visibility, or wrong `OpAccessChain` indexing into the storage buffers or workgroup array. |
| `workgroup_bad_stride` (incorrect `ArrayStride 8`) | Implementation honored the non-standard `ArrayStride 8` decoration on the pointer type instead of ignoring it, so `OpPtrAccessChain` advanced by 8 bytes per element instead of 4 and read the wrong workgroup slots. |
| Both cases share the same plumbing | A failure common to both cases points to the shared `OpPtrAccessChain`/`VariablePointers`/`WorkgroupMemoryExplicitLayoutKHR` path rather than the stride decoration itself. |

### Cause Analysis

#### Wrong `OpPtrAccessChain` addressing on a workgroup pointer

**Possible failure symptoms:** The `probe ssbo int 0:2 0 == 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0` clause fails. The mismatched entries are shifted or scrambled relative to the expected `1, 2, ..., 15, 0` pattern; for example, `C[i]` reads `data[i+2]` or reads from an unrelated workgroup slot because the pointer advanced by the wrong number of bytes.

**Possible implementation causes:** `OpPtrAccessChain %_ptr_Workgroup_uint %26 %uint_1` must add `1 * sizeof(uint) = 4` bytes to the base pointer `%26`. A driver that miscompiles `OpPtrAccessChain` for `Workgroup` storage would produce a wrong pointer, for example by reusing an `OpAccessChain` code path that does not honor a runtime element index, or by applying a wrong element size. The `VariablePointers` capability is what permits a `Workgroup` pointer to be passed to a function and dereferenced after the access chain; if the driver lowers that capability incorrectly, the pointer may be truncated or reinterpreted. Source-level investigation of the driver's `OpPtrAccessChain` lowering for `Workgroup` storage is needed to pin the exact cause when the failure is reproducible.

#### Honoring the non-standard pointer-type `ArrayStride` decoration

**Possible failure symptoms:** Only `workgroup_bad_stride` fails while `workgroup` passes. The probe sees a pattern consistent with an 8-byte element stride: because `data[i] = i` occupies bytes `4*i .. 4*i+3`, advancing by 8 bytes per element would make `get_data(&data[i])` read `data[i+2]` instead of `data[i+1]`. The observed `C` would then be `2 3 4 5 6 7 8 9 10 11 12 13 14 15 <garbage> <garbage>` rather than `1 2 ... 15 0`, with the last two entries reading beyond the sentinel into uninitialized workgroup memory.

**Possible implementation causes:** The SPIR-V spec defines `ArrayStride` only for array types and struct members holding arrays, not for pointer types. A consumer that treats `OpDecorate %_ptr_Workgroup_uint ArrayStride N` as authoritative and uses `N` as the element stride for `OpPtrAccessChain` would advance by `8` bytes instead of `4`, producing this shifted read pattern. The fix is to ignore `ArrayStride` on pointer types and use the pointed-to type's natural size. The amber header comment for `workgroup_bad_stride.amber` states this expectation.

#### Wrong control-barrier visibility

**Possible failure symptoms:** The probe fails non-deterministically or sees stale `-1` values in some entries, because some invocations read `data[i+1]` before the partner invocation wrote it.

**Possible implementation causes:** `OpControlBarrier %uint_2 %uint_1 %uint_264` uses `Workgroup` execution scope, `Device` memory scope, and `AcquireRelease | CrossWorkgroupMemory` semantics. If the driver lowers the barrier with the wrong scope or drops the `AcquireRelease` semantics, the `data[i]` writes may not be visible to other invocations when `get_data` runs. This would be a memory-model lowering bug in the driver, not an `OpPtrAccessChain` bug. Source-level investigation of the driver's control-barrier lowering is needed when this pattern appears.

## Case Pruning

### Requirement-based pruning

Both cases advertise the same requirements through [`addRequirement`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L59-L60) and the amber `[require]` section:

- `VariablePointerFeatures.variablePointers`: needed so a `Workgroup` pointer can be a function parameter and be dereferenced after `OpPtrAccessChain`.
- `VK_KHR_workgroup_memory_explicit_layout`: needed so the `Workgroup` variable can use an explicit `OpTypeArray` layout with `WorkgroupMemoryExplicitLayoutKHR`.
- SPIR-V 1.4 with `supports_VK_KHR_spirv_1_4`: set through [`asmOptions`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L40-L41); the shader uses SPIR-V 1.4 features such as `OpPtrAccessChain` on non-physical pointers.

The whole `ptr_access_chain` test family is non-VulkanSC only. The entire `createTests` body is guarded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L37-L68), so on VulkanSC builds the group registers no cases.

### Design-based pruning

No design-based pruning is applied. Only the two stride-correctness leaves are registered, and both are required to make the ignore-the-decoration rule testable: the `workgroup` case establishes the baseline addressing, and the `workgroup_bad_stride` case probes the same addressing under a deliberately wrong decoration. No other stride values or memory classes are exercised in this family.

## Key Takeaways

- The `ptr_access_chain` test family is a pure Amber dispatcher: the C++ source registers two case leaves and their feature requirements, and each case's SPIR-V, buffers, dispatch, and probe live in a matching `.amber` file.
- Both cases run the same compute shader over a 17-element workgroup `uint` array; the only difference is the single `OpDecorate %_ptr_Workgroup_uint ArrayStride N` line, which is `4` in `workgroup` and `8` in `workgroup_bad_stride`.
- The test focus is `%28 = OpPtrAccessChain %_ptr_Workgroup_uint %26 %uint_1` inside the `get_data` helper. A conformant implementation must compute the offset using the pointed-to `uint` type's natural 4-byte stride and ignore any `ArrayStride` decoration placed on the pointer type itself.
- Both cases expect the same probe output `1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0`. The `workgroup_bad_stride` case passes only when the implementation ignores the bad `ArrayStride 8` decoration and addresses the workgroup array exactly as in the baseline.
- See `## Failure Meaning` for the failure interpretation: a `workgroup_bad_stride`-only failure points to the implementation honoring the non-standard pointer-type decoration, while a failure common to both cases points to shared `OpPtrAccessChain` or control-barrier lowering.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createPtrAccessChainGroup` factory | [vktSpvAsmPtrAccessChainTests.cpp#L73-L78](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L73-L78) | Defines the `ptr_access_chain` test family and routes it to `createTests`. |
| `createTests` body | [vktSpvAsmPtrAccessChainTests.cpp#L35-L69](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L35-L69) | Registers the two Amber cases, attaches feature/extension requirements, and sets SPIR-V 1.4 build options. |
| Case array | [vktSpvAsmPtrAccessChainTests.cpp#L49-L52](../../../modules/vulkan/spirv_assembly/vktSpvAsmPtrAccessChainTests.cpp#L49-L52) | Lists the `workgroup` and `workgroup_bad_stride` basenames and their descriptions. |
| Representative Amber script | [workgroup.amber](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup.amber) | Baseline case carrying the embedded SPIR-V assembly, host buffers, dispatch, and probe analyzed in this page. |
| Bad-stride Amber script | [workgroup_bad_stride.amber](../../../data/vulkan/amber/spirv_assembly/instruction/compute/ptr_access_chain/workgroup_bad_stride.amber) | Identical to the baseline except for the single `OpDecorate %_ptr_Workgroup_uint ArrayStride 8` line. |
| Mustpass entry range | [spirv-assembly.txt#L9963-L9964](../../../mustpass/main/vk-default/spirv-assembly.txt#L9963-L9964) | Mirrors the two registered `dEQP-VK.spirv_assembly.instruction.compute.ptr_access_chain.*` case paths. |
