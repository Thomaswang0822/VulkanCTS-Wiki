## Overview

**Core question:** Does `OpTerminateInvocation` end a fragment invocation so that post-termination operations do not execute and the terminated invocation contributes no fragment output or subgroup participation?

- This page covers the `spirv_assembly.instruction.terminate_invocation` test family registered by [`createTerminateInvocationGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L110-L168) in [`vktSpvAsmTerminateInvocationTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp).
- All 15 registered test case leaves are Amber-dispatched cases. The C++ file registers each case name, its SPIR-V version, and its feature requirements through `cts_amber::createAmberTestCase`; the SPIR-V assembly, host buffers, descriptor bindings, draw calls, and `EXPECT` checks live in the matching `.amber` files under `external/vulkancts/data/vulkan/amber/spirv_assembly/instruction/terminate_invocation/`.
- Each case exercises one category of post-terminate side effect that must be suppressed: output writes, SSBO stores/atomics, image stores/atomics, null or out-of-bounds pointer accesses, an `OpTerminateInvocation` inside a loop, or subgroup ballot/vote participation.
- The page explains the shared shader pattern, the per-case side-effect variations, the Amber reference-pipeline comparison, and what a failing result points to.

## Background Knowledge

- **`OpTerminateInvocation` (SPV_KHR_terminate_invocation).** This SPIR-V instruction terminates the current shader invocation. The [Vulkan shader-termination rules](../../../../vulkan-docs/src/chapters/shaders.adoc#L1843-L1867) state that a terminated invocation has finished executing instructions. For a fragment invocation, the [fragment-operation rules](../../../../vulkan-docs/src/chapters/fragops.adoc#L850-L861) set its covered samples' coverage-mask bits to zero. The test therefore distinguishes work that follows termination and must not execute from an output store that precedes termination but is still discarded with the terminated fragment.
- **Amber test framework.** Each `.amber` file is a self-contained recipe that declares shaders, host buffers, images, pipelines, draw calls, and `EXPECT` checks. CTS loads the file through `cts_amber::createAmberTestCase` and runs the recipe on the device; the C++ side never sees shader source. The output, loop, and subgroup scripts use a reference pipeline with a plain GLSL fragment shader, while the SSBO, image, and pointer scripts use literal expected data or an expected buffer.
- **Subgroup vote and ballot (SPV_KHR_subgroup_vote).** Two cases use SPIR-V 1.3 subgroup operations. `OpGroupNonUniformAll` (vote) and `OpGroupNonUniformBallot` (ballot) compute a per-subgroup result across the invocations that are still active at the call site. Terminated invocations must not contribute to that result, otherwise the vote/ballot value observed by surviving invocations would be wrong.

## Registration Hierarchy

```text
spirv_assembly.instruction.terminate_invocation
└── terminate
```

The `terminate` intermediate node holds all 15 test case leaves listed in `## Behavior Parameters`. The `terminate` group is wrapped by [`addTestsForAmberFiles`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L77-L104), which is excluded from Vulkan SC by a `#ifndef CTS_USES_VULKANSC` guard. A 16th Amber file, `ssbo_atomic_before_terminate.amber`, exists in the data directory but is not registered by the C++ dispatcher.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Side-effect category | output write, SSBO store/atomic, image store/atomic, null/oob pointer access, loop, subgroup | Selects which kind of post-terminate operation must be suppressed. The category determines the shader body, descriptor bindings, and feature requirements. | [case list](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L132-L162) |
| SPIR-V version | 1.0 for ordinary cases, 1.3 for subgroup cases | `spv1p3 = true` selects `VK_API_VERSION_1_1` and `SPIRV_VERSION_1_3`; otherwise Vulkan 1.0 / SPIR-V 1.0. | [version selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L86-L88) |
| Requirement bundle | `Stores`, `VarPtr`, `Vote`, `Ballot` (or none) | Per-case requirement vectors attached after the shared `VK_KHR_shader_terminate_invocation` extension. `Stores` adds `Features.fragmentStoresAndAtomics`; `VarPtr` adds `VariablePointerFeatures.variablePointersStorageBuffer` and `Features.fragmentStoresAndAtomics`; `Vote`/`Ballot` add the matching subgroup operation and stage support. | [requirement vectors](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L117-L130) |

## Behavior Parameters

The primary behavioral axis is the side-effect category, because it determines the operation shape, feature gate, and oracle. All cases use `combined == int(gl_FragCoord.z)` to select termination, but the output, loop, and subgroup scripts compare a reference framebuffer while storage and pointer scripts compare their mutated targets against literal data or an expected buffer.

### Output write cases: `no_output_write`, `no_output_write_before_terminate`

The fragment shader writes to its color output in two placements. `no_output_write` places `OpStore %out_data %int_1` after the terminate branch, so terminated invocations must not execute it. `no_output_write_before_terminate` places the store before the branch; the store executes, but its fragment still terminates and therefore contributes no covered sample. Both cases compare against a GLSL reference that writes `1` when `x` or `y` is odd and `0` otherwise. No extra feature beyond `VK_KHR_shader_terminate_invocation` is required.

### SSBO store/atomic cases: `no_ssbo_store`, `no_ssbo_atomic`, `ssbo_store_before_terminate`

The fragment shader binds a runtime-array storage buffer at descriptor set 0 binding 0 and writes to it after the terminate branch. `no_ssbo_store` performs `OpStore` to `a[idx]`; `no_ssbo_atomic` performs an atomic on the same location; `ssbo_store_before_terminate` performs the store on the terminating branch before `OpTerminateInvocation`, expecting the store to commit. All three carry the `Stores` requirement (`Features.fragmentStoresAndAtomics`). The expected buffer is a fixed 8×8 pattern derived from the per-pixel `x` coordinate, with zeros at positions where termination should have suppressed the store.

### Image store/atomic cases: `no_image_store`, `no_image_atomic`

The fragment shader binds a storage image and writes to it after the terminate branch. `no_image_store` performs `OpImageWrite`; `no_image_atomic` performs an atomic on the image. Both carry the `Stores` requirement. The expected image follows the same positional pattern as the SSBO cases.

### Null and out-of-bounds pointer cases: `no_null_pointer_load`, `no_null_pointer_store`, `no_out_of_bounds_load`, `no_out_of_bounds_store`, `no_out_of_bounds_atomic`

The fragment shader binds two storage buffers (`a` at binding 0, `b` at binding 1) and selects an invalid pointer for the invocations that terminate. The null-pointer cases select `OpConstantNull %ptr_int_ssbo`; the out-of-bounds cases select a pointer one element past the runtime array. Each script creates or selects the pointer before the terminate branch, then dereferences it after the merge through `OpCopyMemory` or an atomic. A correct implementation must not execute that dereference for terminated invocations. All five cases carry the `VarPtr` requirement (`VariablePointerFeatures.variablePointersStorageBuffer` plus `Features.fragmentStoresAndAtomics`).

### Control flow case: `terminate_loop`

The fragment shader wraps `OpTerminateInvocation` inside a `for` loop built with `OpLoopMerge`/`OpBranchConditional`. The loop body executes `OpTerminateInvocation` unconditionally on the first iteration when the terminate condition holds, so a correct implementation exits the loop and the shader without reaching the post-merge `OpStore %out_data %int_1`. No extra feature is required.

### Subgroup participation cases: `subgroup_ballot`, `subgroup_vote`

The fragment shader uses SPIR-V 1.3 subgroup operations. `subgroup_vote` calls `OpGroupNonUniformAll` with subgroup scope 3; `subgroup_ballot` calls `OpGroupNonUniformBallot`. The terminate condition is computed first, then `OpTerminateInvocation` ends the matching invocations, and the subgroup operation runs after the merge block. Terminated invocations must not contribute to the vote or ballot, so the result seen by surviving invocations must reflect only non-terminated lanes. The expected framebuffer matches the output-write reference. `subgroup_vote` requires `SubgroupSupportedOperations.vote` and `SubgroupSupportedStages.fragment`; `subgroup_ballot` requires `SubgroupSupportedOperations.ballot` and `SubgroupSupportedStages.fragment`. Both cases build with SPIR-V 1.3 / Vulkan 1.1.

## Shader Analysis

All 15 Amber scripts share the same vertex shader and the same fragment-shader skeleton; they differ only in what operation follows the `OpTerminateInvocation` branch and which descriptors, capabilities, and SPIR-V version are declared. The representative walkthrough uses the `no_output_write` case, which has the smallest feature set (only `VK_KHR_shader_terminate_invocation`) and exposes the shared trigger condition, terminate branch, and pass/fail logic most cleanly.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
spirv_assembly.instruction.terminate_invocation.terminate.no_output_write
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `no_output_write` | Plain output-write case; no extra feature beyond `VK_KHR_shader_terminate_invocation`. |
| Framebuffer 8×8 | Two triangles cover the full framebuffer; `gl_FragCoord.x`/`y` range over 0..7. |
| `in_data = 0` | Vertex `in_data_buf` is filled with zeros, so `combined = (x & 1) + (y & 1)`. |
| `gl_FragCoord.z = 0` | Vertex `position.z = 0`, so the terminate condition `combined == int(gl_FragCoord.z)` is true exactly when both `x` and `y` are even. |
| Reference shader | GLSL `expect_fs` writes `(x_is_odd || y_is_odd) ? 1 : 0`, the value the tested shader must produce if post-terminate `OpStore %out_data %int_1` is suppressed for even-even pixels. |

#### Purpose

This shader terminates the fragment invocations covering pixels where both `x` and `y` are even, then attempts `OpStore %out_data %int_1` after the merge block. The pass condition is that the framebuffer matches the GLSL reference, which writes `1` only for pixels where at least one coordinate is odd. If `OpTerminateInvocation` fails to suppress the post-terminate store, the even-even pixels would receive `1` instead of the initial `0`, and the `EXPECT out_data EQ_BUFFER expect_frame` check would fail.

#### Structural Design

```mermaid
flowchart TD
    A[Vertex shader: pass position<br/>and in_data=0] --> B[Fragment shader: load FragCoord]
    B --> C[combined = (x AND 1) + (y AND 1) + in_data]
    C --> D{combined == int(FragCoord.z)?}
    D -- yes --> E[OpTerminateInvocation<br/>invocation ends]
    D -- no --> F[OpStore out_data, 1]
    E -. suppressed .- F
    F --> G[Frame buffer compare<br/>EXPECT out_data EQ_BUFFER expect_frame]
```

#### Shader Resources

| Resource | Binding | Role in this case |
|----------|---------|-------------------|
| `%frag_coord` | BuiltIn `FragCoord` | Input; provides `x`, `y`, `z` used for the trigger condition. |
| `%in_data` | `Location 0`, `Flat` | Per-vertex integer input; constant `0` from `in_data_buf`. |
| `%out_data` | `Location 0` | Output color attachment (`out_data` image, 8×8, int32). The post-terminate `OpStore` targets this variable. |
| `expect_frame` | reference pipeline color attachment | 8×8 int32 image filled by the GLSL `expect_fs` shader; compared against `out_data` after both pipelines draw. |

#### Source Code

The SPIR-V assembly below is the literal contents of `no_output_write.amber` between `SHADER fragment fs SPIRV-ASM` and `END`. It is test data, not reconstructed source, so it is shown verbatim. The leading `;`-prefixed lines are SPIR-V assembly comments showing the original GLSL intent.

```llvm
;#version 450
;
;layout(location = 0) in flat int in_data;
;layout(location = 0) out int out_data;
;void main() {
;  int x_coord = int(gl_FragCoord.x);
;  int y_coord = int(gl_FragCoord.y);
;  int combined = (x_coord & 0x1) + (y_coord & 0x1) + in_data;
;  if (combined == int(gl_FragCoord.z))
;    terminateInvocation;
;
;  out_data = 1;
;}
OpCapability Shader
OpExtension "SPV_KHR_terminate_invocation"
OpMemoryModel Logical GLSL450
OpEntryPoint Fragment %main "main" %frag_coord %in_data %out_data
OpExecutionMode %main OriginUpperLeft
OpDecorate %frag_coord BuiltIn FragCoord
OpDecorate %in_data Location 0
OpDecorate %in_data Flat
OpDecorate %out_data Location 0
%void = OpTypeVoid
%bool = OpTypeBool
%int = OpTypeInt 32 1
%int_1 = OpConstant %int 1
%float = OpTypeFloat 32
%float4 = OpTypeVector %float 4
%ptr_int_input = OpTypePointer Input %int
%ptr_int_output = OpTypePointer Output %int
%ptr_float4_input = OpTypePointer Input %float4
%frag_coord = OpVariable %ptr_float4_input Input
%in_data = OpVariable %ptr_int_input Input
%out_data = OpVariable %ptr_int_output Output
%void_fn = OpTypeFunction %void
%main = OpFunction %void None %void_fn
%entry = OpLabel
%coord = OpLoad %float4 %frag_coord
%x_coord = OpCompositeExtract %float %coord 0
%y_coord = OpCompositeExtract %float %coord 1
%z_coord = OpCompositeExtract %float %coord 2
%x = OpConvertFToS %int %x_coord
%y = OpConvertFToS %int %y_coord
%z = OpConvertFToS %int %z_coord
%x_and_1 = OpBitwiseAnd %int %x %int_1
%y_and_1 = OpBitwiseAnd %int %y %int_1
%add = OpIAdd %int %x_and_1 %y_and_1
%ld_in_data = OpLoad %int %in_data
%combined = OpIAdd %int %add %ld_in_data
%cmp = OpIEqual %bool %combined %z
OpSelectionMerge %exit None
OpBranchConditional %cmp %then %exit
%then = OpLabel
OpTerminateInvocation
%exit = OpLabel
OpStore %out_data %int_1
OpReturn
OpFunctionEnd
```

The fragment shader declares the `Shader` capability and the `SPV_KHR_terminate_invocation` extension, with `OriginUpperLeft` placement. `%frag_coord` is decorated `BuiltIn FragCoord`; `%in_data` is `Location 0` and `Flat`; `%out_data` is `Location 0` and is the only color attachment. The entry point loads `FragCoord`, extracts `x`, `y`, `z`, converts them to signed integers, computes `combined = (x & 1) + (y & 1) + in_data`, and compares against `int(gl_FragCoord.z)`. The `OpSelectionMerge %exit None` / `OpBranchConditional %cmp %then %exit` pair forms the terminate branch: when the condition is true, control reaches `%then`, which contains only `OpTerminateInvocation`. Surviving invocations fall through to `%exit`, where `OpStore %out_data %int_1` writes the value compared against the reference framebuffer.

## Runtime Execution and Result Checking

Each Amber script starts with `position_buf`, six vertices that form two triangles over an 8 x 8 framebuffer, and `in_data_buf`, six zero values. The tested pipeline `gpipe` attaches the SPIR-V vertex shader `vs` and fragment shader `fs`.

1. `no_output_write`, `no_output_write_before_terminate`, `terminate_loop`, `subgroup_ballot`, and `subgroup_vote` also create `expect_pipe` with a passthrough vertex shader and a GLSL reference fragment shader. They run `expect_pipe` first and then `gpipe`, followed by `EXPECT out_data EQ_BUFFER expect_frame`.
2. SSBO, image, and pointer scripts bind their case-specific resources to `gpipe`, run only that pipeline, and compare the changed target with literal `EXPECT` rows or an `expect_buf`. The image cases use indexed `EXPECT a_buf` rows rather than a reference pipeline.
3. `ssbo_store_before_terminate` uses its precomputed `expect_buf` to confirm that the SSBO store, which precedes termination, remains visible even though a preceding fragment-output store does not.

The C++ dispatcher attaches `VK_KHR_shader_terminate_invocation` to every case and adds the per-case requirement vector (`Stores`, `VarPtr`, `Vote`, or `Ballot`) before registering the Amber test. SPIR-V 1.3 build options are applied to `subgroup_ballot` and `subgroup_vote`; all other cases build with SPIR-V 1.0.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `no_output_write` | A post-terminate output store executed, or termination did not remove the terminated fragment's coverage. |
| `no_output_write_before_terminate` | A pre-terminate output store from a terminated fragment remained visible; fragment termination did not remove that fragment's coverage. |
| `no_ssbo_store`, `no_ssbo_atomic` | Post-terminate SSBO store or atomic not suppressed; the write reaches the storage buffer. |
| `ssbo_store_before_terminate` | Pre-terminate SSBO store not committed; termination discards stores that should have happened. |
| `no_image_store`, `no_image_atomic` | Post-terminate image store or atomic not suppressed; the write reaches the storage image. |
| `no_null_pointer_load`, `no_null_pointer_store` | Post-terminate null-pointer dereference executed; the implementation accesses an invalid pointer that the termination should have skipped. |
| `no_out_of_bounds_load`, `no_out_of_bounds_store`, `no_out_of_bounds_atomic` | Post-terminate out-of-bounds pointer access executed; the implementation accesses memory outside the buffer bounds. |
| `terminate_loop` | `OpTerminateInvocation` inside a loop body does not end the invocation; control continues past the loop merge and reaches the post-merge store. |
| `subgroup_ballot`, `subgroup_vote` | Terminated invocations still contribute to the subgroup ballot or vote; the per-subgroup result no longer reflects only surviving lanes. |

### Cause Analysis

#### Post-termination work or fragment output remains visible

**Possible failure symptoms:** `no_output_write` can show `1` at even-even pixels, where the terminated fragment should leave the cleared output unchanged. `no_output_write_before_terminate` can show the same symptom even though its output store precedes termination. SSBO or storage-image cases can contain values written by operations after `OpTerminateInvocation`.

**Possible implementation causes:** The compiler can lower `OpTerminateInvocation` to a control-flow exit that leaves post-merge work reachable, or it can schedule a post-termination store or atomic before the termination condition. For the output-write-before-terminate case, a fragment-operation implementation can retain output from a fragment whose coverage should have been removed. The final comparison cannot separate the compiler, fragment-output, and attachment paths without a runtime trace.

#### Pre-terminate store not committed

**Possible failure symptoms:** For `ssbo_store_before_terminate`, the SSBO location that should have received the store before `OpTerminateInvocation` retains its initial zero value. The `EXPECT a_buf EQ_BUFFER expect_buf` comparison fails at the terminated positions.

**Possible implementation causes:** The implementation treats `OpTerminateInvocation` as rolling back all stores in the same invocation, including those that lexically precede the terminate instruction, or the compiler reorders the store to after the terminate instruction where it is then suppressed.

#### Invalid pointer dereference executed

**Possible failure symptoms:** For null-pointer and out-of-bounds cases, the test could fail by device loss, a crash, a validation-layer error, or, if the dereference happens to read a defined value, a mismatched `EXPECT a_buf EQ_BUFFER expect_buf`. The exact symptom depends on whether the implementation traps invalid pointer accesses or silently returns undefined data.

**Possible implementation causes:** The shader compiler fails to recognize that the pointer dereference is post-dominated by the terminate branch and emits the load/store/atomic unconditionally, or it hoists the dereference above the terminate check. For null pointers, the `OpSelect %ptr_int_ssbo %cmp %nullptr %b_ptr` pattern may be lowered to a direct dereference of the selected pointer without preserving the domination relationship.

#### Subgroup operation includes terminated invocations

**Possible failure symptoms:** For `subgroup_vote` and `subgroup_ballot`, the surviving invocations observe a vote or ballot result that includes contributions from terminated lanes. The output framebuffer disagrees with the GLSL reference at positions where the subgroup result differs.

**Possible implementation causes:** The subgroup lowering may record all lanes that entered the shader, including lanes that later terminate, instead of masking them out of the vote/ballot computation. Because these cases use the SPIR-V 1.3 / subgroup-operation path, the failure is consistent with an error in that path, but the final framebuffer comparison does not distinguish it from shared termination lowering or fragment-output handling.

## Case Pruning

### Requirement-based pruning

- `VK_KHR_shader_terminate_invocation` is required for every case; implementations without the extension skip the entire `terminate` group.
- `Features.fragmentStoresAndAtomics` is required for the SSBO, image, and pointer cases (`Stores` and `VarPtr` bundles). Implementations without fragment stores and atomics skip those cases.
- `VariablePointerFeatures.variablePointersStorageBuffer` is required for the null-pointer and out-of-bounds cases (`VarPtr` bundle). Implementations without variable pointers skip those cases.
- `SubgroupSupportedOperations.vote` plus `SubgroupSupportedStages.fragment` gate `subgroup_vote`; `SubgroupSupportedOperations.ballot` plus `SubgroupSupportedStages.fragment` gate `subgroup_ballot`. Implementations without subgroup vote or ballot support in the fragment stage skip those cases.
- The whole group is wrapped in `#ifndef CTS_USES_VULKANSC`, so Vulkan SC builds skip every case.

### Design-based pruning

- The 16th Amber file `ssbo_atomic_before_terminate.amber` exists in the data directory but is intentionally not registered. The dispatcher registers `ssbo_store_before_terminate` only; the atomic-before-terminate variant is omitted from the CTS run.
- Subgroup cases are pinned to SPIR-V 1.3 / Vulkan 1.1 because `OpGroupNonUniformAll` and `OpGroupNonUniformBallot` require subgroup support that is part of the Vulkan 1.1 core feature set. All other cases stay on SPIR-V 1.0 / Vulkan 1.0 to keep the baseline minimal.

## Key Takeaways

- The test family checks both effects of fragment termination: post-termination work must not execute, and a terminated fragment must not contribute its stored output to the attachment.
- The 15 cases share a termination predicate, but their operation shapes, feature requirements, and result oracles differ between output, storage, pointer, loop, and subgroup coverage.
- `no_output_write_before_terminate` shows that a color-output store before termination still disappears with the fragment, while `ssbo_store_before_terminate` shows that a preceding SSBO store remains visible.
- Null-pointer and out-of-bounds cases rely on termination to make an invalid pointer unreachable; a failure here can manifest as device loss or a validation error rather than a quiet value mismatch.
- Subgroup cases require SPIR-V 1.3 and check that terminated invocations do not contribute to vote or ballot results observed by surviving lanes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createTerminateInvocationGroup` | [vktSpvAsmTerminateInvocationTests.cpp#L110-L168](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L110-L168) | Top-level group constructor; registers the `terminate` intermediate node and all 15 case leaves. |
| `addTestsForAmberFiles` | [vktSpvAsmTerminateInvocationTests.cpp#L77-L104](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L77-L104) | Amber dispatcher; attaches `VK_KHR_shader_terminate_invocation`, the per-case requirement vector, and the SPIR-V version to each `cts_amber::createAmberTestCase`. |
| Case list | [vktSpvAsmTerminateInvocationTests.cpp#L132-L162](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L132-L162) | The 15 registered case basenames with their `spv1p3` flag and requirement bundle. |
| Requirement vectors | [vktSpvAsmTerminateInvocationTests.cpp#L117-L130](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L117-L130) | Definitions of `Stores`, `VarPtr`, `Vote`, and `Ballot` requirement vectors. |
| Amber data directory | [terminate_invocation/](../../../data/vulkan/amber/spirv_assembly/instruction/terminate_invocation/) | The 16 `.amber` files (15 registered) containing the SPIR-V assembly, buffers, pipelines, and `EXPECT` checks. |
| Representative Amber script | [no_output_write.amber](../../../data/vulkan/amber/spirv_assembly/instruction/terminate_invocation/no_output_write.amber) | Source of the walkthrough fragment shader and the reference-pipeline comparison. |
