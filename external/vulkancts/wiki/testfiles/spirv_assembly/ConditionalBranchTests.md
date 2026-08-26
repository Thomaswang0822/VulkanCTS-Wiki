## Overview

**Core question:** Does `OpBranchConditional` execute the one named target correctly when its true and false label operands are both the same label?

- This page documents the `conditional_branch` test family implemented by [`vktSpvAsmConditionalBranchTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L47-L238) in the `spirv_assembly` test category.
- Each test case emits an `OpBranchConditional` whose condition is a literal `%true` or `%false`, while both label operands name `%live`. The `%live` block writes its invocation index to a storage buffer. A separately authored `%dead` block would instead write `2863311530` (`0xAAAAAAAA`).
- The source creates two compute test case leaves and ten graphics test case leaves. The graphics helper installs the same test function into the fragment, geometry, tessellation-control, tessellation-evaluation, and vertex paths.
- The page traces one exact compute assembly variant, then explains the host-side oracle and the limits of failure localization.

## Background Knowledge

- `OpBranchConditional` has a condition operand followed by true-label and false-label operands. The SPIR-V grammar defines all three as ID references, so the instruction can name the same label twice. See the [`OpBranchConditional` grammar entry](../../../../spirv-headers/src/include/spirv/1.0/spirv.core.grammar.json).
- `OpSelectionMerge` identifies the merge block for a structured selection. The following branch instruction transfers control to the selected successor; the merge declaration does not make an unreferenced block execute. See the [`OpSelectionMerge` grammar entry](../../../../spirv-headers/src/include/spirv/1.0/spirv.core.grammar.json).
- A storage buffer gives the shader a host-visible result channel. This test writes one 32-bit value per index and compares the complete buffer with a host-provided reference.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.conditional_branch
├── same_labels_false
└── same_labels_true

spirv_assembly.instruction.graphics.conditional_branch
├── same_labels_false_frag
├── same_labels_false_geom
├── same_labels_false_tessc
├── same_labels_false_tesse
├── same_labels_false_vert
├── same_labels_true_frag
├── same_labels_true_geom
├── same_labels_true_tessc
├── same_labels_true_tesse
└── same_labels_true_vert
```

[`createInstructionTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21311-L21547) adds the compute and graphics instruction branches. This implementation creates each `conditional_branch` test family through [`createConditionalBranchComputeGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L222-L229) and [`createConditionalBranchGraphicsGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L231-L238). The current default Vulkan mustpass list contains 2 compute and 10 graphics executable leaves, as shown in [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L1315-L1316) and [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L23019-L23028).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Literal condition | `true`, `false` | Selects `%true` or `%false` for `OpBranchConditional`; neither value changes the named successor because both operands are `%live`. | [`conditions` and compute specialization](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L47-L125) |
| Execution surface | `compute`; graphics `frag`, `geom`, `tessc`, `tesse`, `vert` | Compute dispatches one invocation per output index. Graphics injects the same loop and selection into one tested graphics stage at a time. | [compute builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L49-L126), [graphics builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L128-L217) |
| Output index range | `0` through `127` | The live block writes each index back to its matching storage-buffer element. The sentinel makes an unintended `%dead` execution observable. | [buffer initialization and dispatch size](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L52-L57), [live/dead stores](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L103-L115) |
| Graphics storage features | `vertexPipelineStoresAndAtomics`, `fragmentStoresAndAtomics` | The graphics specification requests these core features before asking the utility to construct the stage cases. | [feature requests](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L140-L145) |

## Behavior Parameters

The behavioral axis is the **test case leaf**. Every leaf checks the same-label control-flow property, while its name fixes the literal condition and, for graphics, the stage that executes the injected code.

### same_labels_false: compute false condition

The compute shader uses `%false` in `OpBranchConditional %false %live %live`. Since both successors are `%live`, invocation `i` must write `i`, not the sentinel, to output element `i`.

### same_labels_true: compute true condition

This leaf changes only the literal condition to `%true`. It must produce the same `0` through `127` output sequence as `same_labels_false` because the two successor operands remain `%live`.

### same_labels_false_frag: fragment false condition

The fragment-stage variant injects the false-condition same-label selection inside the utility-generated graphics test function. Its storage-buffer writes must preserve the sequential reference values.

### same_labels_false_geom: geometry false condition

The geometry-stage variant executes the same false-condition selection and indexed storage-buffer writes in the generated geometry path.

### same_labels_false_tessc: tessellation-control false condition

The tessellation-control variant places the false-condition selection in the generated tessellation-control path and checks the same indexed output signal.

### same_labels_false_tesse: tessellation-evaluation false condition

The tessellation-evaluation variant places the false-condition selection in the generated tessellation-evaluation path and checks the same indexed output signal.

### same_labels_false_vert: vertex false condition

The vertex-stage variant places the false-condition selection in the generated vertex path and checks the same indexed output signal.

### same_labels_true_frag: fragment true condition

The fragment-stage true variant differs from `same_labels_false_frag` only in the literal condition. Both branch operands still name `%live`.

### same_labels_true_geom: geometry true condition

The geometry-stage true variant checks the same-label rule in the generated geometry path with `%true` as the condition.

### same_labels_true_tessc: tessellation-control true condition

The tessellation-control true variant checks the same-label rule in the generated tessellation-control path with `%true` as the condition.

### same_labels_true_tesse: tessellation-evaluation true condition

The tessellation-evaluation true variant checks the same-label rule in the generated tessellation-evaluation path with `%true` as the condition.

### same_labels_true_vert: vertex true condition

The vertex-stage true variant checks the same-label rule in the generated vertex path with `%true` as the condition.

## Shader Analysis

The selected compute case is the smallest exact case: one `GLCompute` entry point, 128 one-invocation workgroups, one storage buffer, and the literal `%true`. The `same_labels_false` variant substitutes `%false`; the graphics variants reuse the same selection fragment inside a utility-generated stage function.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.conditional_branch.same_labels_true
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `GLCompute`, `LocalSize 1 1 1` | Each workgroup has one invocation; the host launches 128 workgroups. |
| Set `0`, binding `0`, `Uniform` `BufferBlock` | A 128-element `uint` buffer stores the result for each global invocation ID. |
| `%true` | The first operand of `OpBranchConditional`. |
| `%live`, `%live` | Both label operands name the live store block. |
| `%uint_unused = 2863311530` | The unreferenced `%dead` block would store this value if execution incorrectly reached it. |

#### Purpose

The shader loads `gl_GlobalInvocationID.x` as `i`, declares `%merge` as the selection merge block, then executes `OpBranchConditional %true %live %live`. The only named successor is `%live`, which stores `i` to `dataOutput[0][i]`. The host expects the complete sequence `0` through `127`; a sentinel value or any other mismatch fails the case.

#### Structural Design

```mermaid
flowchart TD
    A[GLCompute invocation i] --> B[Load GlobalInvocationID.x]
    B --> C[OpSelectionMerge %merge None]
    C --> D[OpBranchConditional %true %live %live]
    D --> E[%live: dataOutput[i] = i]
    E --> F[%merge: return]
    G[%dead: dataOutput[i] = 0xAAAAAAAA] -. has no branch target .-> F
```

#### Shader Code

This representative case does not use GLSL or HLSL. CTS supplies the shader module directly as SPIR-V assembly. The selected module contains `compute` stage entry point `main`; the source template or Amber artifact cited by this walkthrough is the authoritative shader source. The complete validated assembly is presented in the final `SPIR-V` subsection.

#### Additional Info

- `%gl_GlobalInvocationID` is an `Input` variable with the `BuiltIn GlobalInvocationId`; its x component supplies `i`.
- `%dataOutput` is the `Uniform` `%Output` object at descriptor set `0`, binding `0`, holding the 128-element result array.
- `%i` is a `Function` `uint` variable that keeps the loaded invocation index across the selection.
- `%live` is the label named by both branch-target operands and performs the expected indexed write; `%dead` is not named by this branch and contains the sentinel write that makes an incorrect transfer visible.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Literal condition | `same_labels_false` changes only `OpBranchConditional %true %live %live` to `OpBranchConditional %false %live %live`; its expected buffer remains `0` through `127`. | [`conditions` and compute specialization](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L47-L125) |
| Graphics stage and condition | The graphics builder uses the same `%true`/`%false` specialization in the generated `%test_code` function. That function loops from `0` to `127`, executes the same-label selection per index, and is installed into one graphics stage by [`createTestsForAllStages`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L171-L217). | [graphics builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L128-L217) |
| Graphics loop scaffolding | The graphics fragment text also has an outer loop condition, `OpBranchConditional %lt %write %merge`, with distinct targets. That loop branch is control scaffolding; the test focus is the nested `OpBranchConditional %${condition} %live %live`. | [nested branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L180-L205) |

#### SPIR-V

- Status: assembled, validated, and disassembled
- Source: CTS-authored SPIR-V assembly from this walkthrough
- Entry point(s): `GLCompute` (`main`)
- Stage: `GLCompute`
- Target SPIRV version: `spv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos SPIR-V Tools Assembler; 0
; Bound: 32
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %2 "main" %gl_GlobalInvocationID
               OpExecutionMode %2 LocalSize 1 1 1
               OpSource GLSL 430
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_arr_uint_uint_128 ArrayStride 4
               OpMemberDecorate %_struct_5 0 Offset 0
               OpDecorate %_struct_5 BufferBlock
               OpDecorate %6 DescriptorSet 0
               OpDecorate %6 Binding 0
       %void = OpTypeVoid
          %8 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
       %bool = OpTypeBool
       %true = OpConstantTrue %bool
      %false = OpConstantFalse %bool
   %uint_128 = OpConstant %uint 128
%_arr_uint_uint_128 = OpTypeArray %uint %uint_128
  %_struct_5 = OpTypeStruct %_arr_uint_uint_128
%_ptr_Uniform__struct_5 = OpTypePointer Uniform %_struct_5
          %6 = OpVariable %_ptr_Uniform__struct_5 Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%uint_2863311530 = OpConstant %uint 2863311530
          %2 = OpFunction %void None %8
         %22 = OpLabel
         %23 = OpVariable %_ptr_Function_uint Function
         %24 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %25 = OpLoad %uint %24
               OpStore %23 %25
         %26 = OpLoad %uint %23
               OpSelectionMerge %27 None
               OpBranchConditional %true %28 %28
         %28 = OpLabel
         %29 = OpAccessChain %_ptr_Uniform_uint %6 %uint_0 %26
               OpStore %29 %26
               OpBranch %27
         %30 = OpLabel
         %31 = OpAccessChain %_ptr_Uniform_uint %6 %uint_0 %26
               OpStore %31 %uint_2863311530
               OpBranch %27
         %27 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The compute builder fills a 128-element host reference buffer with `0` through `127`, specializes the assembly once for each literal condition, sets `numWorkGroups` to `(128, 1, 1)`, and gives the reference buffer to `SpvAsmComputeShaderCase` as its expected output. See [`addComputeSameLabelsTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L49-L125).
- With `LocalSize 1 1 1`, each compute workgroup writes one index. The live block writes the loaded global ID to the matching storage-buffer element. The compute case passes only when the framework's output comparison matches the original sequential reference.
- The graphics builder creates the same sequential expected data, exposes it as a storage-buffer output resource, requests vertex and fragment storage-write features, and gives the generated fragments and resources to [`createTestsForAllStages`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L128-L217). That helper creates the stage-specific leaves listed above.
- The branch-specific graphics oracle is the storage-buffer content, not the default colors. `addGraphicsSameLabelsTest` initializes `defaultColors` and supplies them as both input and expected image colors; the [common graphics utility](../../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L4558-L4589) separately spot-checks those four rendered corners before comparing the registered 128-element storage-buffer output resource at [lines 136 through 146](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L136-L146) and [lines 4719 through 4784](../../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L4719-L4784).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `same_labels_false` | Compute handling of a same-label `OpBranchConditional`, or its storage-buffer result path. |
| `same_labels_true` | Compute handling of a same-label `OpBranchConditional`, or its storage-buffer result path. |
| `same_labels_false_frag` | Fragment-stage same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_false_geom` | Geometry-stage same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_false_tessc` | Tessellation-control same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_false_tesse` | Tessellation-evaluation same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_false_vert` | Vertex-stage same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_true_frag` | Fragment-stage same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_true_geom` | Geometry-stage same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_true_tessc` | Tessellation-control same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_true_tesse` | Tessellation-evaluation same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |
| `same_labels_true_vert` | Vertex-stage same-label branch handling, graphics storage-buffer writes, the default-image check, or shared graphics test setup. |

A matching failure pattern cannot by itself distinguish the branch operation from the shared buffer, image, pipeline, and framework paths. The cause names classify the operation shape; source-level investigation of the generated module, pipeline creation, image check, storage-buffer comparison, and comparison result is needed to localize a defect.

### Cause Analysis

#### Same-label branch target handling

**Possible failure symptoms:** One or more output elements differ from their index. A visible `2863311530` value directly matches the sentinel emitted in `%dead`, while another unexpected value shows that the output did not match the host reference.

**Possible implementation causes:** A compiler or execution implementation may mishandle `OpBranchConditional` when its true-label and false-label operands resolve to the same block, for example by altering the successor during control-flow processing or by executing code that the instruction does not name. The source and the successful SPIR-V validation gate establish the exact instruction shape; they do not identify a failing implementation layer.

#### Storage-buffer output path

**Possible failure symptoms:** A compute or graphics leaf reports a mismatch even though the branch's selected `%live` block conceptually performs the expected indexed write. Storage-buffer failures can affect a subset of indices or the whole 128-element reference sequence; a graphics leaf can instead fail the utility's separate default-image corner check.

**Possible implementation causes:** The storage-output path includes descriptor binding, storage-buffer addressing, shader writes, execution completion, copyback, and comparison framework behavior. Graphics also renders and spot-checks the default image before checking the output resource. Neither oracle can isolate its result path from the branch operation. Inspect the generated module and the relevant CTS utility code before attributing a failure to descriptor handling, image rendering, or synchronization.

#### Graphics stage integration

**Possible failure symptoms:** Only leaves with one stage suffix fail, such as `same_labels_true_geom`, while compute and other graphics stage leaves pass. A failure that spans all graphics suffixes can instead come from shared graphics setup or the shared output resource.

**Possible implementation causes:** The source injects the selection fragment into utility-generated graphics test code, so a stage-specific failure can involve that stage's generated assembly or execution path. The graphics builder also requests `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`; support, pipeline construction, and stage-specific storage writes remain part of the result path. The current source does not provide a finer per-stage oracle, so further source and runtime evidence is needed to localize the defect.

## Case Pruning

### Requirement-based pruning

No requirement-based pruning is applied.

### Design-based pruning

The source has no generated value matrix to prune. It iterates the two exact literals in `conditions[]`, producing two compute leaves and then asks the graphics utility to create five stage suffixes for each literal. The current default Vulkan mustpass inventory retains all 12 leaves. VulkanSC mustpass also lists the same 12 paths in [`spirv-assembly.txt`](../../../mustpass/main/vksc-default/spirv-assembly.txt#L874-L875) and [`spirv-assembly.txt`](../../../mustpass/main/vksc-default/spirv-assembly.txt#L8976-L8985).

## Key Takeaways

- The test family exercises an exact SPIR-V edge case: both successor operands of `OpBranchConditional` name `%live`.
- `%true` and `%false` are separate test case leaf values, but they must produce the same indexed buffer because the branch target is identical.
- The `%dead` sentinel block makes an unintended control transfer observable through the normal output oracle.
- Compute gives the smallest direct execution path. Graphics repeats the same control-flow property across five shader stages, with storage-buffer comparison as the common signal.
- A failed image of output data identifies a same-label branch or output-path problem class, not a unique driver, compiler, or hardware fault location.

## Source Reference Appendix

| Topic | Source reference | Why it matters |
|-------|------------------|----------------|
| Literal conditions and compute assembly template | [`addComputeSameLabelsTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L47-L126) | Defines the exact representative assembly, 128-element reference data, specialization, dispatch size, and compute case leaves. |
| Graphics fragments and feature requests | [`addGraphicsSameLabelsTest`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L128-L218) | Shows the storage output resource, requested features, nested same-label branch, and all-stages utility call. |
| Family registration | [`createConditionalBranchComputeGroup` and `createConditionalBranchGraphicsGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp#L222-L238) | Creates the compute and graphics `conditional_branch` test families. |
| Parent instruction registration | [`createInstructionTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21398-L21405) and [`graphicsTests`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21497-L21504) | Places both families under `spirv_assembly.instruction`. |
| SPIR-V operand grammar | [`spirv.core.grammar.json`](../../../../spirv-headers/src/include/spirv/1.0/spirv.core.grammar.json) | Defines the operands of `OpSelectionMerge` and `OpBranchConditional`. |
| Default Vulkan mustpass leaves | [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L1315-L1316) and [`spirv-assembly.txt`](../../../mustpass/main/vk-default/spirv-assembly.txt#L23019-L23028) | Records the current 2 compute and 10 graphics paths. |
