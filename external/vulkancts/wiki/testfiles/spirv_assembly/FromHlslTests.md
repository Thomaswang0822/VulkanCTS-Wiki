## Overview

**Core question:** does the implementation correctly honor an HLSL `cbuffer` `packoffset` that places a scalar member inside the stride of a preceding array, when `VK_EXT_scalar_block_layout` is enabled?

- Source file: [`vktSpvAsmFromHlslTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp).
- Registered path: `spirv_assembly.instruction.compute.hlsl_cases.cbuffer_packing`.
- The single registered case `cbuffer_packing` covers an HLSL packing corner case the source comments identify as not expressible in GLSL: an `int foo[2]` array with `ArrayStride 16` is followed by `int bar` placed at `packoffset(c1.y)`, i.e. byte offset 20, which falls inside the stride of `foo[1]`.
- The compute shader reads `bar` from the uniform buffer and writes it to a storage buffer; the host then checks the readback value.
- The page covers the registered path, the HLSL and SPIR-V representation, the host-side setup, and what a failure would mean.

## Background Knowledge

- HLSL `cbuffer` blocks allow explicit member placement through `packoffset(cN.M)` annotations, where `cN` selects a 16-byte constant register and `.M` selects a 4-byte slot within that register. A `packoffset(c1.y)` therefore means byte offset `16 + 4 = 20` from the start of the block. GLSL has no equivalent syntax: it cannot place a member inside the stride of a preceding array member.
- `VK_EXT_scalar_block_layout` relaxes Vulkan's uniform buffer layout rules so that each member is aligned only to its scalar type. With this extension, an `int` member at byte offset 20 inside an `int[2]` array of stride 16 is a legal layout, because offset 20 is 4-byte aligned and does not conflict at scalar granularity.
- An HLSL `RWStructuredBuffer<int>` lowers to a Vulkan storage buffer with a runtime-sized `int` array at offset 0.

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.hlsl_cases
└── cbuffer_packing
```

The page covers only the `cbuffer_packing` test case leaf under the `hlsl_cases` test family. The `instruction` and `compute` ancestors are registered by [`vktSpvAsmInstructionTests.cpp`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21426); this page does not expand them.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test type enum | `TT_CBUFFER_PACKING` | Only enum value defined in this file; selects the HLSL `cbuffer` packing shader and the matching host-side buffer setup. | [`TestType`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L46-L48), [`createHlslComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L228-L235) |

## Behavior Parameters

This page covers a single fixed test case leaf, `cbuffer_packing`. The shader source, host-side buffers, descriptor bindings, dispatch dimensions, and pass condition are all fixed by `TT_CBUFFER_PACKING`, so there is no behavioral axis to subdivide.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.spirv_assembly.instruction.compute.hlsl_cases.cbuffer_packing
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `TT_CBUFFER_PACKING` | Selects the only HLSL shader in this file: a compute shader that reads `bar` from a `cbuffer` and writes it to a `RWStructuredBuffer<int>`. |
| HLSL source registered through `dst.hlslSources.add("comp")` | The shader is genuine HLSL, compiled by the CTS HLSL frontend with `FLAG_ALLOW_SCALAR_OFFSETS` so the resulting SPIR-V is validated under `VK_EXT_scalar_block_layout` ([build options](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L77-L79)). |
| `vk::SPIRV_VERSION_1_0` target | Matches the SPIR-V environment used by CTS for this case. |

#### Purpose

The shader reads `bar` from the `cbIn` cbuffer and writes that value to `result[0]`. The interesting property is not the read or write itself, but the offset that `bar` occupies inside the cbuffer: byte 20, which sits inside the stride of `foo[1]`. The test passes only if the implementation honors that scalar-block-layout offset end to end.

#### Structural Design

| Phase | What happens | Why it matters for the tested property |
|-------|--------------|----------------------------------------|
| cbuffer declaration | `foo[2]` has `ArrayStride 16`; `bar` is placed at `packoffset(c1.y)`, i.e. byte offset 20. | The overlap with `foo[1]`'s stride is the tested property. |
| `result` declaration | `RWStructuredBuffer<int> result : register(u1)` lowers to a storage buffer bound at descriptor set 0, binding 1. | Provides a host-visible sink for the value read from `bar`. |
| Entry point | `[numthreads(1, 1, 1)] void main(...)` runs a single compute invocation. | One invocation is enough because the shader only copies one scalar. |
| Body | `result[0] = bar;` loads `bar` from the uniform buffer and stores it to the storage buffer. | The copy is the only behavior the host checks. |

#### Source Code

Reconstructed HLSL from [`Programs::init()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L59-L79); `///` lines are wiki annotations, while the remaining shader text is the CTS source:

```hlsl
/// cbuffer cbIn is the uniform buffer at descriptor set 0, binding 0. `foo` starts at byte 0 with
/// ArrayStride 16; `bar` lands at byte 20, inside the stride of `foo[1]`.
cbuffer cbIn
{
  int foo[2] : packoffset(c0);
  int bar    : packoffset(c1.y);
};
/// `result` is the storage buffer at descriptor set 0, binding 1; the shader writes index 0 only.
RWStructuredBuffer<int> result : register(u1);
[numthreads(1, 1, 1)]
void main(uint3 dispatchThreadID : SV_DispatchThreadID)
{
  result[0] = bar;
}
```

- `dispatchThreadID` is unused; it stays because it appears in the original HLSL.

#### Additional Info

- CTS compiles the HLSL with `vk::ShaderBuildOptions::FLAG_ALLOW_SCALAR_OFFSETS`, which sets `SpirvValidatorOptions::kScalarBlockLayout` so CTS validates the SPIR-V under `VK_EXT_scalar_block_layout` ([build options](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L77-L79), [flag mapping](../../../framework/vulkan/vkShaderProgram.hpp#L80-L83)).
- The C++ comment in `Programs::init()` notes that the case is "a packing corner case that GLSL shaders cannot exhibit" because `bar` ends up "effectively 'within' the end of the foo array" ([source comment](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L61-L64)).
- The disassembled SPIR-V below shows `OpMemberDecorate %cbIn 1 Offset 20` next to `OpDecorate %_arr_int_uint_2 ArrayStride 16`, which is the SPIR-V-level encoding of the overlap.

#### Parameter Variation Summary

There are no shader-level parameter variants for this test family. The only registered path is `spirv_assembly.instruction.compute.hlsl_cases.cbuffer_packing`; all values above are fixed by the single registered case.

#### SPIR-V

- Status: generated and validated
- Source: reconstructed HLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 40
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource HLSL 500
               OpName %main "main"
               OpName %result "result"
               OpMemberName %result 0 "@data"
               OpName %result_0 "result"
               OpName %cbIn "cbIn"
               OpMemberName %cbIn 0 "foo"
               OpMemberName %cbIn 1 "bar"
               OpName %_ ""
               OpDecorate %_runtimearr_int ArrayStride 4
               OpDecorate %result BufferBlock
               OpMemberDecorate %result 0 Offset 0
               OpDecorate %result_0 Binding 1
               OpDecorate %result_0 DescriptorSet 0
               OpDecorate %_arr_int_uint_2 ArrayStride 16
               OpDecorate %cbIn Block
               OpMemberDecorate %cbIn 0 Offset 0
               OpMemberDecorate %cbIn 1 Offset 20
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
%_runtimearr_int = OpTypeRuntimeArray %int
     %result = OpTypeStruct %_runtimearr_int
%_ptr_Uniform_result = OpTypePointer Uniform %result
   %result_0 = OpVariable %_ptr_Uniform_result Uniform
      %int_0 = OpConstant %int 0
     %uint_2 = OpConstant %uint 2
%_arr_int_uint_2 = OpTypeArray %int %uint_2
       %cbIn = OpTypeStruct %_arr_int_uint_2 %int
%_ptr_Uniform_cbIn = OpTypePointer Uniform %cbIn
          %_ = OpVariable %_ptr_Uniform_cbIn Uniform
      %int_1 = OpConstant %int 1
%_ptr_Uniform_int = OpTypePointer Uniform %int
       %main = OpFunction %void None %3
          %5 = OpLabel
         %37 = OpAccessChain %_ptr_Uniform_int %_ %int_1
         %38 = OpLoad %int %37
         %39 = OpAccessChain %_ptr_Uniform_int %result_0 %int_0 %int_0
               OpStore %39 %38
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

[`HlslTest::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L98-L219) drives the runtime:

- Host allocates a 32-byte host-visible uniform buffer (binding 0) and zeroes it. The host writes the test value `5` at index 5, i.e. byte offset 20, where `bar` lives ([input buffer setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L105-L122)).
- Host allocates a 4-byte host-visible storage buffer (binding 1) for `result` ([output buffer setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L125-L132)).
- Host builds a descriptor set with the input uniform buffer at binding 0 and the output storage buffer at binding 1, matching the HLSL `register(u1)` and the implicit cbuffer binding ([descriptor update](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L151-L160)).
- Host records a compute pipeline bind, descriptor set bind, host-to-device barrier, `cmdDispatch(1, 1, 1)`, and a device-to-host barrier ([command recording](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L195-L208)).
- After `submitCommandsAndWait`, host invalidates the output allocation and reads the first `int` ([readback](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L213-L218)).
- Pass condition: the readback value equals `testValue` (`5`). Any other value, including `0`, fails.

## Failure Meaning

### Failure Cause Mapping

This is a single fixed test case, so the cause is direct: a failure means the implementation did not return the byte at offset 20 of the uniform buffer when the shader loaded `bar`. The most likely failure points are SPIR-V offset decoration handling and uniform buffer reads under scalar block layout; less likely ones are descriptor binding, barrier, or storage buffer write visibility, since the test exercises only the most basic forms of those.

### Cause Analysis

#### SPIR-V offset decoration handling

**Possible failure symptoms:** the readback value is not `5`. Common alternatives are `0` (the buffer was zeroed and the implementation read uninitialized or padding memory), the value of `foo[0]`, or the value of `foo[1]` at offset 16.

**Possible implementation causes:** the shader compiler or driver does not honor `OpMemberDecorate %cbIn 1 Offset 20` under scalar block layout. A likely form is rewriting the cbuffer to a std140-style layout, which would push `bar` to offset 32 (after `foo[2]`) and read zero. A driver that rejects the SPIR-V would surface as a pipeline-creation or shader-module error before readback. Confirming a specific driver or compiler path needs source-level investigation.

#### Uniform buffer read at scalar-block-layout offset

**Possible failure symptoms:** the readback value is not `5`, but the SPIR-V offset decorations are correct.

**Possible implementation causes:** the driver's uniform buffer load path applies an alignment or stride rule that differs from the SPIR-V `Offset` decoration when scalar block layout is enabled, so the load targets a different byte. This would be a uniform-buffer memory-layout bug rather than a shader-compiler bug; claiming a specific cause needs source-level investigation.

#### Descriptor binding and storage write visibility

**Possible failure symptoms:** the readback value is not `5`, but a correct load of `bar` would have produced `5`.

**Possible implementation causes:** the descriptor set did not bind the input uniform buffer at binding 0 or the output storage buffer at binding 1, or the device-to-host barrier did not make the shader write visible to the host read. The CTS code uses the standard helpers and a single shader write followed by a single barrier, so a failure here would point to driver-side descriptor or barrier handling rather than the test itself.

## Case Pruning

### Requirement-based pruning

- The test calls `context.requireDeviceFunctionality("VK_EXT_scalar_block_layout")` in [`checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L221-L224). Devices without the extension cannot run the case at all, because the `packoffset(c1.y)` overlap inside `foo[1]`'s stride is only legal under scalar block layout.

### Design-based pruning

- The file defines only `TT_CBUFFER_PACKING` and registers only the `cbuffer_packing` leaf ([`createHlslComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L228-L235)). There is no parameter matrix to prune: the single case is the entire test family.

## Key Takeaways

- The test exercises an HLSL `cbuffer` overlap that GLSL cannot express: `bar` at `packoffset(c1.y)` lands at byte 20, inside the stride of `foo[1]`.
- The overlap is only legal under `VK_EXT_scalar_block_layout`, which the test requires through `checkSupport()` and the `FLAG_ALLOW_SCALAR_OFFSETS` build option.
- The pass condition is a single `int` equality check on a 4-byte readback; any value other than `5` means the implementation read from the wrong offset or wrote to the wrong sink.
- See `## Failure Meaning` for the offset-handling, uniform-buffer-read, and descriptor-binding failure points.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `Programs::init()` | [`vktSpvAsmFromHlslTests.cpp#L59-L79`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L59-L79) | Adds the HLSL compute source with `FLAG_ALLOW_SCALAR_OFFSETS`. |
| `HlslTest::iterate()` | [`vktSpvAsmFromHlslTests.cpp#L98-L219`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L98-L219) | Allocates buffers, builds descriptors, dispatches, reads back, and checks the value. |
| `checkSupport()` | [`vktSpvAsmFromHlslTests.cpp#L221-L224`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L221-L224) | Requires `VK_EXT_scalar_block_layout`. |
| `createHlslComputeGroup()` | [`vktSpvAsmFromHlslTests.cpp#L228-L235`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L228-L235) | Registers the `hlsl_cases` test family and the `cbuffer_packing` leaf. |
| `TestType` enum | [`vktSpvAsmFromHlslTests.cpp#L46-L48`](../../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp#L46-L48) | Defines the only `TT_CBUFFER_PACKING` value used by this file. |
| Parent registration | [`vktSpvAsmInstructionTests.cpp#L21426`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21426) | Adds `createHlslComputeGroup()` under `instruction.compute`. |
