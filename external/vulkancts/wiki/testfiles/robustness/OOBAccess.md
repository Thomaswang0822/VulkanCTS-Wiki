## Overview

**Core question:** Do out-of-bounds texel-buffer and storage-image accesses obey the enabled robustness contract?

- This page covers the `robustness.oob_access` test family implemented and registered by [`vktRobustnessOOBAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1-L1064).
- Compute shaders perform out-of-bounds reads or writes against texel-buffer views and storage images.
- `robust_on` cases check defined zero-read or unchanged-resource outcomes where the selected robustness feature provides them. `robust_off` storage-image cases require successful execution but do not assert an out-of-bounds value.

## Background Knowledge

For the shared model of bounded resource access, robustness contracts, and shader/host responsibilities, see [Robustness Background Knowledge](../../categories/robustness.md#background-knowledge).

- **A texel-buffer view** exposes a bounded range of a larger buffer. An index can therefore be outside the view while still addressing bytes inside the backing allocation, which helps detect implementations that incorrectly use allocation bounds instead of view bounds.
- **Storage images** are addressed by coordinates. A coordinate at or beyond the selected extent is outside the image even though the shader and dispatch remain otherwise valid.

## Registration Hierarchy

```text
robustness.oob_access
├── robust_on
└── robust_off
```

The factory creates both direct children, while the generated test case leaves carry the resource, access, format, size, and robustness-level choices ([`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L1058)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Robustness mode | `robust_on`, `robust_off` | Selects whether defined robust behavior is requested; `robust_off` is generated only for storage images. | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L973-L1054) |
| Access distance | `off_by_one`, `off` | Uses the first invalid element/coordinate or a farther invalid location. | [`OOBAccessType`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L54-L58), [index calculation](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L349) |
| Resource kind | `texel_buffer_uniform`, `texel_buffer_storage`, storage image | Changes the descriptor and resource bounds being exercised. Uniform texel-buffer writes are not generated. | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L982-L1024) |
| Direction | `read`, `write` | Reads expose the returned value; writes test whether valid resource contents remain unchanged. | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L990-L1051) |
| Format | `VK_FORMAT_R32_UINT`, `VK_FORMAT_R64_UINT` | Exercises 32-bit and 64-bit unsigned texels. | [format loops](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L995-L996), [image format loop](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1030-L1033) |
| Texel-buffer robustness level | `rba`, `rba2` | Selects core robust buffer access or `VK_EXT_robustness2`; explicit result comparison is performed for `rba2`. | [robustness loop](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L999-L1002), [buffer verification](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L540) |
| Texel-buffer backing size | `256`, `1024`, `4096` bytes | Varies allocation size while the tested access remains outside the view. | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L997-L998) |
| Storage-image extent | `16x16`, `64x64`, `128x128` | Varies image bounds and therefore the invalid coordinate. | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L1034-L1050) |

## Behavior Parameters

The primary behavioral axis is the direct robustness-mode component below `robustness.oob_access`.

### `robust_on` — verify defined robust outcomes

These cases request robust access. Texel-buffer cases cover reads and supported writes at `rba` and `rba2` levels; storage-image cases use `VK_EXT_image_robustness`. The checks that have explicit source-level outcomes require out-of-bounds reads to return zero and writes to leave the initialized resource unchanged ([buffer verification](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L538), [image verification](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L926-L948)).

### `robust_off` — exercise unprotected storage-image access

These cases are generated only for storage images. They execute the same out-of-bounds access shapes without enabling robust image access, but the host does not compare a returned value or unchanged image; successful completion is the asserted result in the inspected code ([`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L922-L948)).

## Shader Analysis

The source generates one compute shader per case. The walkthrough below uses a robust storage-texel-buffer read because it exposes the central device-side operation and a result that the host checks. Nearby cases change the resource declaration, operation, integer width, or coordinate shape without adding control flow.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.robustness.oob_access.robust_on.rba2_texel_buffer_storage_r32_uint_read_off_by_one_1024
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `robust_on`, `rba2` | Enables `robustBufferAccess2`, whose out-of-bounds texel-buffer read result is checked for zero. |
| `texel_buffer_storage`, `r32_uint`, `read` | Uses a storage texel-buffer view with 32-bit unsigned texels and copies the loaded component to a storage buffer for host inspection. |
| `off_by_one`, `1024` | The 1024-byte allocation has a 512-byte view, so the first invalid `R32_UINT` index is 128. |

#### Purpose

This shader reads the first texel outside a storage texel-buffer view and writes the returned component to a host-visible result buffer. The host checks that `robustBufferAccess2` makes every result byte zero.

#### Structural Design

| Shader step | Operation | Observable role |
|-------------|-----------|-----------------|
| Receive invalid index | Read `pc.index` from the push constant | Selects texel 128, immediately beyond the 128-texel view. |
| Perform tested access | Call `imageLoad(texelBuffer, pc.index)` | Issues the out-of-bounds storage texel-buffer read. |
| Export result | Store `.x` in `outBuffer.outputData` | Makes the robust read value available to the host check. |

#### Shader Code

```glsl
#version 450
/// Binding 0 is the bounded storage texel-buffer view under test.
layout(set = 0, binding = 0, r32ui) uniform uimageBuffer texelBuffer;
/// Binding 1 receives the value returned by the out-of-bounds read.
layout(set = 0, binding = 1, std430) buffer OutputBuffer {
    uint outputData;
} outBuffer;
/// The host supplies the first invalid texel index for this case.
layout(push_constant) uniform PushConstants {
    int index;
} pc;
layout(local_size_x = 1) in;

void main (void)
{
    /// Perform the tested storage texel-buffer access, then expose its first component.
    uint value = imageLoad(texelBuffer, pc.index).x;
    outBuffer.outputData = value;
}
```

#### Additional Info

- The generator requests SPIR-V 1.0 for this 32-bit case; only 64-bit formats select SPIR-V 1.3 ([`OOBBufferTestCase::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L236-L305)).
- The host derives index 128 from a 512-byte view and a four-byte texel, while the backing allocation remains 1024 bytes ([index calculation](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L349)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Resource kind | Uniform texel-buffer reads use `utextureBuffer` and `texelFetch`; storage-image cases use `uimage2D` and an `ivec2` coordinate. | [buffer generator](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L236-L305), [image generator](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L630-L695) |
| Direction | Write cases replace the output buffer with an input buffer and call `imageStore`; uniform texel-buffer writes are not generated. | [buffer generator](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L278-L304), [case generation](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L990-L1024) |
| Format | `R64_UINT` adds the required 64-bit extensions, changes shader scalar and image types, and targets SPIR-V 1.3. | [format-dependent shader generation](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L238-L304) |
| Access distance and resource size | These choices change the host-supplied push constant but not the shader structure. | [index calculation](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L349) |
| Robustness mode or level | Robustness changes device features and host-side checking; it does not add a shader branch. | [capability setup](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L207-L234), [buffer verification](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L540) |

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
; Bound: 34
; Schema: 0
               OpCapability Shader
               OpCapability ImageBuffer
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %value "value"
               OpName %texelBuffer "texelBuffer"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "index"
               OpName %pc "pc"
               OpName %OutputBuffer "OutputBuffer"
               OpMemberName %OutputBuffer 0 "outputData"
               OpName %outBuffer "outBuffer"
               OpDecorate %texelBuffer Binding 0
               OpDecorate %texelBuffer DescriptorSet 0
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpDecorate %OutputBuffer BufferBlock
               OpMemberDecorate %OutputBuffer 0 Offset 0
               OpDecorate %outBuffer Binding 1
               OpDecorate %outBuffer DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
          %9 = OpTypeImage %uint Buffer 0 0 0 2 R32ui
%_ptr_UniformConstant_9 = OpTypePointer UniformConstant %9
%texelBuffer = OpVariable %_ptr_UniformConstant_9 UniformConstant
        %int = OpTypeInt 32 1
%PushConstants = OpTypeStruct %int
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
         %pc = OpVariable %_ptr_PushConstant_PushConstants PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
     %v4uint = OpTypeVector %uint 4
     %uint_0 = OpConstant %uint 0
%OutputBuffer = OpTypeStruct %uint
%_ptr_Uniform_OutputBuffer = OpTypePointer Uniform %OutputBuffer
  %outBuffer = OpVariable %_ptr_Uniform_OutputBuffer Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %value = OpVariable %_ptr_Function_uint Function
         %12 = OpLoad %9 %texelBuffer
         %19 = OpAccessChain %_ptr_PushConstant_int %pc %int_0
         %20 = OpLoad %int %19
         %22 = OpImageRead %v4uint %12 %20
         %24 = OpCompositeExtract %uint %22 0
               OpStore %value %24
         %28 = OpLoad %uint %value
         %30 = OpAccessChain %_ptr_Uniform_uint %outBuffer %int_0
               OpStore %30 %28
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- For texel buffers, the host fills backing memory with a nonzero pattern and initializes the read/write result buffer to `0xFF`. It creates a bounded texel-buffer view, pushes the selected invalid index, and dispatches one compute workgroup ([buffer setup and dispatch](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L489)).
- For `rba2` reads, every byte of the result must be zero. For `rba2` writes, the entire backing buffer must match its original reference data. Other inspected texel-buffer cases pass after successful execution ([buffer verification](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L517-L540)).
- For storage images, the host initializes the image through a buffer copy, dispatches with an invalid coordinate, and copies written images back for comparison ([image setup and dispatch](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L784-L924)).
- Robust image reads must return all-zero bytes, and robust image writes must preserve the initialized image. Non-robust image cases do not assert the accessed value ([image verification](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L926-L948)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `robust_on` | The enabled robustness path returned nonzero data for a checked out-of-bounds read, modified valid resource contents during a checked out-of-bounds write, or failed to execute the supported case. |
| `robust_off` | The unprotected storage-image case failed to execute successfully; the test does not diagnose a particular returned value. |

### Cause Analysis

#### Robustness contract violation

**Possible failure symptoms:** An `rba2` texel-buffer or robust storage-image read contains a nonzero byte, or a checked out-of-bounds write changes the initialized backing data.

**Possible implementation causes:** Bounds may be evaluated against the wrong resource range, or the enabled robustness behavior may not be applied to the generated storage operation. For a texel-buffer view, using backing-allocation bounds instead of view bounds can make an invalid view index reach valid allocation memory.

#### Access execution failure

**Possible failure symptoms:** Submission, execution, synchronization, or result retrieval fails before the case reaches its expected pass condition; this is the only asserted failure class for `robust_off`.

**Possible implementation causes:** Source-level investigation is needed to distinguish descriptor, format-operation, shader-lowering, command-execution, or device-loss causes from the reported test result.

## Case Pruning

### Requirement-based pruning

- Portability-subset devices must expose `robustBufferAccess` for robust texel-buffer cases. `rba2` requires `VK_EXT_robustness2` and `robustBufferAccess2` ([buffer support checks](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L162-L188)).
- Texel-buffer formats must support the selected uniform or storage usage, and the view must not exceed `maxTexelBufferElements` ([buffer format checks](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L190-L204)).
- Robust image cases require `VK_EXT_image_robustness`; storage-image format and image-format properties must support the selected usage ([image support checks](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L578-L605)).
- `VK_FORMAT_R64_UINT` cases require the inspected 64-bit shader and atomic capabilities ([common support checks](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L145-L160)).

### Design-based pruning

- Texel-buffer cases are omitted from `robust_off`.
- Uniform texel-buffer writes are omitted because uniform texel buffers are read-only in this test design.
- The matrix uses three representative backing sizes or image extents and two invalid-access distances rather than enumerating every possible bound and offset.

## Key Takeaways

- The matrix distinguishes an access just outside the resource from one farther outside it, including texel-buffer indices that can remain inside the backing allocation while outside the view.
- Explicit value checking is limited to source paths with a defined asserted outcome: zero reads and unchanged data for `rba2` texel buffers and robust storage images.
- `robust_off` does not establish a returned-value contract; it only requires the generated storage-image case to complete successfully.
- See `## Failure Meaning` for how checked data mismatches differ from general execution failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Factory and parameter matrix | [`createOOBAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L965-L1058) | Registers `robust_on`, `robust_off`, and their generated leaves. |
| Texel-buffer support and programs | [`OOBBufferTestCase`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L162-L305) | Defines requirements, capabilities, and generated compute shaders. |
| Texel-buffer execution and checks | [`OOBBufferTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L341-L540) | Builds the bounded view, dispatches, and validates checked robust outcomes. |
| Storage-image support and programs | [`OOBImageTestCase`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L578-L695) | Defines image requirements and generated compute shaders. |
| Storage-image execution and checks | [`OOBImageTestInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessOOBAccessTests.cpp#L755-L948) | Initializes, dispatches, copies back, and validates robust outcomes. |
| Category registration | [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L96-L97) | Adds `oob_access` to the `robustness` test category. |
| Default mustpass coverage | [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13755-L13874) | Lists generated `oob_access` test paths. |
