## Overview

**Core question:** Do Vulkan pipelines deliver shader defaults or API-supplied specialization values to the intended graphics or compute stage, including uses that affect expressions, composites, built-ins, and local size?

[`vktPipelineSpecConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L147-L2994) implements the `spec_constant` test family. Most cases generate GLSL for a selected shader stage, optionally attach `VkSpecializationInfo` during pipeline creation, write observed values to a storage buffer, then compare raw bytes with the case's expected values. The compute-only `unaligned_spec_constant` and `same_id` cases instead use hand-authored SPIR-V and dedicated result checks.

[SpecConstant_brief.md](SpecConstant_brief.md) gives a compact failure-oriented map. This page records registration, generated-program, runtime, and coverage evidence.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Specialization map.** `VkSpecializationInfo` maps SPIR-V constant IDs to byte ranges in `pData`; `VkSpecializationMapEntry` supplies the ID, offset, and size. Map-entry IDs must be unique, offsets and sizes must stay within the data buffer, and an entry for an ID unused by the shader has no effect ([specialization constants](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9505-L9599)).
- **Pipeline-time value.** Vulkan supplies a specialization constant when it creates the pipeline. A shader declaration with no replacement data retains its declared default; a matching map entry changes that value for that pipeline ([pipeline-time semantics](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9505-L9543)).
- **Selected shader stage.** Graphics tests need supporting stages to make a valid pipeline, but only the selected vertex, fragment, tessellation-control, tessellation-evaluation, or geometry stage includes the generated specialization declarations. Compute executes its selected shader in one workgroup.

## Registration Hierarchy

```text
pipeline.monolithic.spec_constant
├── graphics
└── compute
```

`graphics` has five intermediate stage nodes: `vertex`, `fragment`, `tess_control`, `tess_eval`, and `geometry`. Each stage registers `default_value`, `basic`, `builtin`, `expression`, and `composite`. `compute` has those same mechanisms plus `local_size`, `unaligned_spec_constant`, and `same_id`. The source registers `compute` only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` ([registration](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2932-L2994)).

The default mustpass split has five non-monolithic construction lists: `fast-linked-library.txt`, `pipeline-library.txt`, `shader-object-linked-binary.txt`, `shader-object-linked-spirv.txt`, and `shader-object-unlinked-binary.txt`. Each lists 1,170 `spec_constant` leaves, all graphics: 234 leaves for each graphics stage. `monolithic/monolithic.txt` lists 1,413 leaves: those 1,170 graphics leaves plus 243 compute leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Pipeline construction | `monolithic` plus five non-monolithic construction modes for graphics; compute only under `monolithic` | Determines which constructions register the family; it does not change the underlying specialization mechanism. | [registration guard](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2955-L2962) |
| Shader stage | `vertex`, `fragment`, `tess_control`, `tess_eval`, `geometry`, `compute` | In normal cases, the selected stage receives generated declarations and writes results; the two dedicated cases are compute-only hand-authored programs. | [stage table](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2944-L2951), [program generation](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L355-L513) |
| Data representation | `bool`, 8/16/32/64-bit signed and unsigned integers, `float16_t`, `float`, `double`; vectors, matrices, arrays, and structures | Separates scalar byte mapping from composite construction and layout behavior. | [default and basic definitions](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L875-L1515), [composite registration](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2965-L2969) |
| Data packing | generic-stride data or tightly packed `_packed` variants | Changes successive `VkSpecializationMapEntry` offsets without changing expected shader values. | [`Specialization`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L272-L301) |
| Feature requirements | tessellation, geometry, 64-bit, 16-bit, and 8-bit scalar support; graphics SSBO store/atomic support | A case runs only when its stage and type requirements are available. | [support checks](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L832-L860) |

## Behavior Parameters

The primary behavior axis is the registered test mechanism. Stage and representation select where and with which type the mechanism runs.

### `default_value`: retain declared shader constants

These leaves declare constants but omit replacement data. The shader stores the declared values, testing that pipeline creation leaves them intact.

### `basic`: replace scalar values through map entries

These leaves supply selected scalar values through `VkSpecializationInfo`. Generic-stride and `_packed` variants distinguish entry-offset handling from scalar conversion and storage.

### `builtin`: specialize a built-in constant

The `default` case checks the minimum observable `gl_MaxImageUnits` behavior. `specialized` provides `12` and checks that the stage reads that replacement ([built-in cases](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1714-L1748)).

### `expression`: consume constants in compile-time expressions

These leaves use specialized values in constant expressions, array sizes, array-size expressions, and array operations. They test use sites rather than a direct one-value write ([expression cases](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1751-L1900)).

### `composite`: construct composite specialized values

These leaves cover vector, matrix, array, and structure values. They check component ordering and byte layout by writing selected members to the output SSBO.

### `local_size`: specialize compute workgroup dimensions

Compute-only leaves specialize one or more of `local_size_x_id`, `local_size_y_id`, and `local_size_z_id`. The shader writes `gl_WorkGroupSize` and an atomic invocation count; for `xyz`, the expected dimensions are `(3, 5, 7)` and the count is 105 ([definitions](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1593-L1711)).

### `unaligned_spec_constant`: consume an unaligned hand-authored SPIR-V value

This compute-only leaf uses its own initialization and execution functions rather than the generated GLSL path. It targets an unaligned specialization-data layout ([registration](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2974-L2981)).

### `same_id`: assign one ID to constants of different types

This compute-only leaf gives three distinct SPIR-V specialization constants of type `float`, `int`, and `uint` the same `SpecId` of 0. One four-byte map entry must specialize all three by interpreting the same bytes according to each constant's type. The shader also derives its output index from the specialized integer values, then the dedicated runner checks all three stored values ([SPIR-V declarations](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2756-L2793), [specialization and result check](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2822-L2924)).

## Shader Analysis

The inventory identifies `dEQP-VK.pipeline.shader_object_linked_binary.spec_constant.graphics.fragment.basic.bool` as the representative case: it exercises the generated GLSL path while keeping the selected stage and value representation easy to audit. The fragment shader below is reconstructed from the `basic.bool` `CaseDefinition`; its SPIR-V was generated with `glslangValidator --target-env spirv1.3 -V`, validated with `spirv-val --target-env vulkan1.1`, and disassembled with `spirv-dis`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.shader_object_linked_binary.spec_constant.graphics.fragment.basic.bool
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `shader_object_linked_binary` | Selects one of the non-monolithic graphics construction roots. The generated shader logic and specialization map are shared with the other construction variants; the construction path changes how the shader object/pipeline is built. |
| `graphics.fragment` | Makes the fragment stage the selected stage. Supporting vertex and fragment pipeline setup is still generated as required, but only the selected fragment program receives the specialization declarations, SSBO, and case code. |
| `basic.bool` | Declares four boolean specialization constants with IDs 1–4 and supplies four-byte API values `true`, `false`, `false`, and `true`. |
| `std430` output SSBO | Makes each host-checked boolean occupy a four-byte output slot at offsets 0, 4, 8, and 12, allowing `verifyValues` to compare the specialized results as raw bytes. |

#### Purpose

This shader checks that API-supplied specialization values replace the four declared boolean defaults in the selected fragment stage. It writes each specialized value to a storage buffer while producing a constant yellow fragment output so the SSBO, rather than rendered color, is the behavioral oracle.

#### Structural Design

| Phase | Shader operation | Validation signal |
|-------|------------------|-------------------|
| Declaration | Declare `sc0`–`sc3` with `SpecId` 1–4 and expose `Output.r0`–`r3` at set 0, binding 0. | Pipeline specialization has four IDs and one byte-comparable result buffer. |
| Observation | Store `sc0`–`sc3` into the four SSBO members. | The selected values become host-visible at offsets 0, 4, 8, and 12. |
| Graphics completion | Store yellow into `fragColor`. | The triangle executes the selected fragment stage; color is incidental to the specialization result check. |

#### Shader Code

```glsl
#version 450
layout(location = 0) out highp vec4 fragColor;
/// The selected fragment stage receives four distinct specialization IDs. Their declarations retain the defaults until pipeline creation supplies replacement data.
layout(constant_id = 1) const bool sc0 = true;
layout(constant_id = 2) const bool sc1 = false;
layout(constant_id = 3) const bool sc2 = true;
layout(constant_id = 4) const bool sc3 = false;
/// Binding 0 is the host-visible result SSBO. In std430, these scalar boolean members are represented in four-byte slots for the comparison below.
layout (set = 0, binding = 0, std430) writeonly buffer Output {
    bool r0;
    bool r1;
    bool r2;
    bool r3;
} sb_out;
void main (void)
{
    /// Copy the pipeline-specialized values into independently checked output slots.
    sb_out.r0 = sc0;
    sb_out.r1 = sc1;
    sb_out.r2 = sc2;
    sb_out.r3 = sc3;
    /// The graphics path needs a valid color result, but specialization correctness is checked through sb_out.
    fragColor = vec4(1.0, 1.0, 0.0, 1.0);
}
```

#### Additional Info

- `initPrograms` always creates the graphics support stages, but the `useSpecConst` guard is true only when `m_stage == VK_SHADER_STAGE_FRAGMENT_BIT`; therefore the vertex shader does not declare or write these constants ([`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L355-L419)).
- The host supplies four-byte values for all four IDs, attaches the resulting `VkSpecializationInfo` to the fragment state, draws one triangle, makes shader writes visible to the host, and checks the expected boolean bytes with `verifyValues` ([`basic` definitions](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1074-L1095), [graphics execution](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L730-L779), [verification](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L810-L829)).
- The same `basic.bool` shader shape is reused across the five non-monolithic graphics construction lists; the representative path differs in construction mode, not in generated specialization logic.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Selected shader stage | Vertex, fragment, tessellation-control, tessellation-evaluation, and geometry cases insert the declarations, SSBO, and case code only into the selected stage; supporting stages retain their fixed pipeline plumbing. | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L355-L519) |
| Test mechanism | `default_value` omits replacement entries and observes declared defaults; `basic` supplies map entries; `builtin`, `expression`, and `composite` replace the case declarations and main-body logic with their respective use sites. | [`createSpecConstantTests`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2963-L2969) |
| Representation | `basic` changes the declaration and output member type across bool, integer, and floating-point definitions; feature-gated 8/16/64-bit types add the corresponding GLSL extensions. | [`basic` definitions and feature flags](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1074-L1109), [extension selection](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L370-L380) |
| Data packing | `_packed` variants keep the generated shader values and output logic but advance map-entry offsets by each value's size instead of `sizeof(GenericValue)`. | [`Specialization`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L272-L300) |
| Construction type | Monolithic and the five non-monolithic graphics roots reuse the generated source while attaching specialization information through their respective pipeline/shader-object construction paths. | [`createSpecConstantTests`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2955-L2991) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 38
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %fragColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %Output "Output"
               OpMemberName %Output 0 "r0"
               OpMemberName %Output 1 "r1"
               OpMemberName %Output 2 "r2"
               OpMemberName %Output 3 "r3"
               OpName %sb_out "sb_out"
               OpName %sc0 "sc0"
               OpName %sc1 "sc1"
               OpName %sc2 "sc2"
               OpName %sc3 "sc3"
               OpName %fragColor "fragColor"
               OpDecorate %Output Block
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpMemberDecorate %Output 1 NonReadable
               OpMemberDecorate %Output 1 Offset 4
               OpMemberDecorate %Output 2 NonReadable
               OpMemberDecorate %Output 2 Offset 8
               OpMemberDecorate %Output 3 NonReadable
               OpMemberDecorate %Output 3 Offset 12
               OpDecorate %sb_out NonReadable
               OpDecorate %sb_out Binding 0
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %sc0 SpecId 1
               OpDecorate %sc1 SpecId 2
               OpDecorate %sc2 SpecId 3
               OpDecorate %sc3 SpecId 4
               OpDecorate %fragColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %Output = OpTypeStruct %uint %uint %uint %uint
%_ptr_StorageBuffer_Output = OpTypePointer StorageBuffer %Output
     %sb_out = OpVariable %_ptr_StorageBuffer_Output StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
       %bool = OpTypeBool
        %sc0 = OpSpecConstantTrue %bool
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
      %int_1 = OpConstant %int 1
        %sc1 = OpSpecConstantFalse %bool
      %int_2 = OpConstant %int 2
        %sc2 = OpSpecConstantTrue %bool
      %int_3 = OpConstant %int 3
        %sc3 = OpSpecConstantFalse %bool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %fragColor = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
         %37 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpSelect %uint %sc0 %uint_1 %uint_0
         %18 = OpAccessChain %_ptr_StorageBuffer_uint %sb_out %int_0
               OpStore %18 %16
         %21 = OpSelect %uint %sc1 %uint_1 %uint_0
         %22 = OpAccessChain %_ptr_StorageBuffer_uint %sb_out %int_1
               OpStore %22 %21
         %25 = OpSelect %uint %sc2 %uint_1 %uint_0
         %26 = OpAccessChain %_ptr_StorageBuffer_uint %sb_out %int_2
               OpStore %26 %25
         %29 = OpSelect %uint %sc3 %uint_1 %uint_0
         %30 = OpAccessChain %_ptr_StorageBuffer_uint %sb_out %int_3
               OpStore %30 %29
               OpStore %fragColor %37
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking
- The source builds a `Specialization` object from each case's declarations. It reserves generic storage, copies supplied bytes, adds an entry for each nonzero-size or forced-use constant, and advances offsets by either the value size or `sizeof(GenericValue)` for non-packed data ([builder](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L272-L301)).
- The compute path creates a host-visible SSBO and descriptor set, attaches specialization information to `ComputePipelineWrapper` when entries exist, dispatches `(1, 1, 1)`, barriers shader writes to host reads, waits, invalidates the allocation, and calls `verifyValues` ([compute path](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L552-L630)).
- The graphics path creates a color attachment, a triangle vertex buffer, and a host-visible SSBO. It attaches specialization information to the pre-rasterization or fragment state, draws one triangle, barriers graphics shader writes to host reads, waits, invalidates, and calls the same verifier ([graphics path](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L665-L830)).
- `verifyValues` compares every `OffsetValue` byte range at its declared output offset. On a mismatch, it logs expected and actual values in decimal when possible and hexadecimal bytes in all cases ([verifier](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L206-L238)).
- The two hand-authored SPIR-V cases bypass these generated-case runners. `unaligned_spec_constant` reconstructs expected words from the map-entry byte ranges and compares five output words; `same_id` checks a selected output record's float, integer, and unsigned-integer fields ([unaligned check](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2655-L2693), [same-ID check](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2907-L2927)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `default_value` | Pipeline creation incorrectly replaces a declaration that has no supplied value, or the selected stage does not preserve its default. |
| `basic` | Map-entry ID, byte offset, byte size, or packed-data handling supplies the wrong scalar value. |
| `builtin` | Built-in specialization constant handling fails for the default or replacement path. |
| `expression` | A specialized value is wrong when consumed by a constant expression, array declaration, or array operation. |
| `composite` | Composite member layout, element mapping, or reconstructed composite value is wrong. |
| `local_size` | The local-size IDs do not specialize `gl_WorkGroupSize` or workgroup execution as expected. |
| `unaligned_spec_constant` | The implementation mishandles the unaligned byte range used by the hand-authored SPIR-V case. |
| `same_id` | The same constant ID does not produce the expected value in each declared use. |

### Cause Analysis

#### Default-value preservation

**Possible failure symptoms:** The SSBO contains a value different from the declaration's default when the case provides no replacement data.

**Possible implementation causes:** Pipeline creation may attach or interpret specialization data when `pSpecializationInfo` should be absent. The selected-stage program may also lower its declared specialization constant incorrectly. Source-level investigation is needed to distinguish those paths from a shared SSBO write or readback fault.

#### Scalar mapping and data layout

**Possible failure symptoms:** `basic` cases fail at one or more expected byte offsets. A failure limited to `_packed` variants points more narrowly to map-entry offset progression.

**Possible implementation causes:** A map entry can select the wrong ID, byte range, or scalar representation. Vulkan requires each entry size to match the declared constant size, while the CTS builder deliberately changes only entry placement between packed and generic-stride variants ([map-entry rules](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9561-L9597), [CTS builder](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L272-L301)).

#### Built-in and expression use

**Possible failure symptoms:** Direct scalar cases pass but `builtin` or `expression` leaves write an unexpected result, array length, or expression value.

**Possible implementation causes:** The pipeline may substitute the constant but lower its use in a built-in declaration, constant expression, or array declaration incorrectly. The output cannot by itself distinguish compiler lowering from the generated shader's storage write path.

#### Composite reconstruction

**Possible failure symptoms:** A vector, matrix, array, or structure member differs at its checked SSBO offset while simpler scalar leaves pass.

**Possible implementation causes:** The implementation may map composite members in the wrong order or reconstruct their layout incorrectly during specialization. The source-level result check observes selected bytes, so investigation should compare the failing composite's declarations, expected offsets, and generated output code.

#### Compute execution shape

**Possible failure symptoms:** `local_size` writes the wrong `gl_WorkGroupSize` component or checksum, while other compute scalar results may pass.

**Possible implementation causes:** The implementation may not apply a local-size ID to the execution mode or may execute the wrong number of invocations. The source initializes a shared counter, uses barriers, and writes the dimensions and count after the atomic increment, so a mismatch can also require investigation of that generated compute path ([local-size code](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1598-L1613)).

#### Special layout cases

**Possible failure symptoms:** Only `unaligned_spec_constant` or `same_id` fails; its dedicated output buffer reports unexpected values.

**Possible implementation causes:** The unaligned case can expose incorrect byte-range handling. The same-ID case can expose failure to apply one `SpecId` entry to distinct specialization constants, including constants of different types, or incorrect per-type interpretation of the shared bytes. These cases use dedicated program/runner paths, so source-level investigation should first separate their specialization setup from their dispatch and readback logic.

#### Shared execution or observation path

**Possible failure symptoms:** Failures span unrelated mechanisms, types, and stages, or a mismatch appears in both graphics and compute leaves.

**Possible implementation causes:** Shared program compilation, pipeline creation, descriptor binding, shader-write visibility, host invalidation, or `verifyValues` input can affect many mechanisms. The common host code barriers shader writes before host reads and performs raw-byte comparison, but an observed mismatch alone does not isolate the fault to specialization ([compute synchronization](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L608-L629), [graphics synchronization](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L810-L829)).

## Case Pruning

### Requirement-based pruning

- The `compute` intermediate node is not registered for non-monolithic pipeline construction types ([registration condition](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2955-L2962)).
- Tessellation and geometry stage cases require their corresponding features. 64-bit, 16-bit, and 8-bit types require their declared arithmetic and storage features; graphics-stage SSBO writes require the appropriate store/atomic feature ([support checks](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L832-L860)).

### Design-based pruning

- The source samples representative scalar types and selected composite shapes rather than every GLSL type or member arrangement.
- It emits paired generic-stride and packed variants for cases where entry placement matters, instead of combining every representation with every stage/type mechanism.
- `local_size` covers the seven nonempty subsets `x`, `y`, `z`, `xy`, `xz`, `yz`, and `xyz`, rather than every numeric workgroup size.
- `unaligned_spec_constant` and `same_id` remain compute-only dedicated cases because they target special SPIR-V/data-layout behavior.

## Key Takeaways

- `spec_constant` makes graphics and compute specialization results observable through host-visible storage buffers. Generated cases compare expected byte ranges with `verifyValues`; the two hand-authored compute cases use dedicated checks.
- The five non-monolithic split mustpass lists cover the same 1,170 graphics leaves. Monolithic construction adds 243 compute leaves, including local-size and dedicated special-layout cases.
- `_packed` leaves change map-entry placement, while the default, basic, built-in, expression, composite, local-size, unaligned, and same-ID mechanisms change what specialization must accomplish.
- A failing byte comparison proves an observable disagreement. It can narrow diagnosis by mechanism and variant, but it does not alone identify whether specialization, generated shader use, execution, synchronization, or readback caused the disagreement.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Case structures and byte verifier | [`SpecConstant`, `OffsetValue`, and `verifyValues`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L147-L252) | Defines declarations, expected output ranges, and host comparison. |
| Specialization-data builder | [`Specialization`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L254-L301) | Builds `VkSpecializationInfo` and map-entry offsets. |
| Generated shader source | [`generateSpecConstantCode`, `generateSSBOCode`, and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L330-L513) | Inserts case code into the selected shader stage. |
| Compute runtime | [`ComputeTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L552-L630) | Dispatches and reads the compute SSBO. |
| Graphics runtime | [`GraphicsTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L665-L830) | Draws and reads the graphics SSBO. |
| Local-size cases | [`createWorkGroupSizeTests`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1593-L1711) | Defines local-size IDs and expected workgroup count. |
| Registered family | [`createSpecConstantTests`](../../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L2932-L2994) | Creates stages, test mechanisms, and the monolithic compute boundary. |
| Default mustpass scope | [`external/vulkancts/mustpass/main/vk-default/pipeline/`](../../../mustpass/main/vk-default/pipeline/) | Contains the five graphics-only split lists and `monolithic/monolithic.txt`. |
| Vulkan contract | [specialization constants and map entries](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9505-L9599) | Defines pipeline-time constants, map fields, and entry validity requirements. |
