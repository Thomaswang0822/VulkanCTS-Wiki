## Overview

**Core question:** Does memory allocated with `VK_MEMORY_ALLOCATE_ZERO_INITIALIZE_BIT_EXT` expose zero contents through every tested buffer and image access path?

- [`vktMemoryZeroInitializeDeviceMemoryTests.cpp`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp) implements the `memory.zero_initialize_device_memory` test family.
- `clear_buffer` checks zeroed buffer bytes across compatible memory types and usage flags.
- `image_transition` checks zeroed color and depth/stencil image contents after transition from `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT` through transfer, compute, fragment, and render-pass paths.

## Background Knowledge

For the shared concepts memory types, heaps, and resource compatibility, host-visible and non-coherent memory, and memory dependencies, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- `VK_EXT_zero_initialize_device_memory` adds an allocation flag that requests zeroed device-memory contents. The tested resource must still be bound to that allocation and read through a legal access path. [Feature definition](../../../../vulkan-docs/src/chapters/features.adoc#L6380-L6386)
- An image created in `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT` must transition to the layout needed by the selected read path. The source transitions the complete image subresource range before access. [Image layout transition validity](../../../../vulkan-docs/src/chapters/commonvalidity/image_layout_transition_common.adoc#L170-L180)
- A format without an alpha channel produces an alpha value of one when sampled into a four-component shader value. The image reference accounts for that rule rather than expecting four zero components for every format.

## Registration Hierarchy

```text
memory.zero_initialize_device_memory
├── clear_buffer
└── image_transition
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `clear_buffer`, `image_transition` | Selects byte comparison for a buffer or image observation after the zero-initialized layout. | [`createClearedAllocationControlTests`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1252-L1395) |
| Buffer usage | `transfer_dst`, `uniform_texel_buffer`, `storage_texel_buffer`, `uniform_buffer`, `storage_buffer`, `index_buffer`, `vertex_buffer`, `indirect_buffer` | Changes the usage constraints on the buffer whose memory begins at zero. | [Buffer registration](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1258-L1290) |
| Buffer size | `1`, `4`, `4096`, `4194304` | Covers single-byte, word-sized, page-scale, and large allocations. | [Buffer size cases](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1258-L1258) |
| Host visibility | default leaf, `_host_visible` leaf | Selects direct host inspection or a device-to-host copy before comparison. | [`clearBufferAllocation`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L136-L221) |
| Image format | color formats including `r8_unorm`, integer/float formats, and `bc1_rgba_unorm_block`; depth/stencil formats | Changes representation, shader value type, and support checks. | [Image format registration](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1299-L1389) |
| Image read path | `xfer`, `comp`, `frag`, depth/stencil rendering | Selects transfer copy, compute read, fragment read, or depth/stencil attachment observation. | [`ImageTransitionCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L445-L528) |
| Mip extent | `1x1`, `4x4`, `53x92`, `512x512` | Changes the observed image region and dispatch/draw size. | [Mip sizes](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1292-L1297) |
| Mip selection | `first_mip`, `second_mip` | Reads the only mip or mip level 1 of a two-level image. | [`ImageTransitionParams`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L224-L281) |

## Behavior Parameters

The test family is the primary behavioral axis. The `image_transition` read path is a secondary axis because it changes how zero contents become observable.

### clear_buffer: zeroed buffer allocation

The test allocates each compatible memory type with `VK_MEMORY_ALLOCATE_ZERO_INITIALIZE_BIT_EXT`, binds it to a buffer, and compares all bytes with zero. Host-visible variants inspect the tested allocation directly. Other variants copy to a host-visible buffer first.

### image_transition: zeroed image allocation

The test creates an image in `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT`, binds zero-initialized memory, transitions the full image, and observes the selected mip through one of four paths.

### image_transition.xfer: transfer readback

The command buffer transitions the image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`, copies the selected mip to a host-visible buffer, and compares the copied texels with a zero reference. Compressed formats are excluded from this path.

### image_transition.comp: compute image read

A compute shader reads each texel from a sampled or storage image and writes a four-component value to a storage buffer. The host compares that buffer with the expected zero texture.

### image_transition.frag: fragment image read

A full-screen triangle invokes a fragment shader for each pixel. The fragment shader reads the image and writes each value to the same storage-buffer result layout used by compute cases.

### image_transition.depth_stencil: attachment behavior

A separate render-pass path transitions the zero-initialized depth/stencil image to attachment layout, draws a blue triangle, copies the color attachment, and compares it with the expected blue result. This exposes an incorrect initial depth/stencil state through the depth/stencil tests rather than by reading raw attachment bytes.

## Shader Analysis

One compute walkthrough represents shader-based image observation. Fragment cases use the same image-read and SSBO-write idea with fragment coordinates; transfer and buffer cases do not use shaders.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory.zero_initialize_device_memory.image_transition.r8_unorm_sampled_shader_comp_4x4_first_mip
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `r8_unorm` | Uses a normalized one-channel image, so the shader reads `vec4` values and the reference expects zero RGB with default alpha one. |
| `sampled_shader_comp` | Reads through `sampler2D` in a compute shader and writes results to an SSBO. |
| `4x4_first_mip` | Uses a one-level 4x4 image and one workgroup per row. |

#### Purpose

The shader turns every texel observed from the zero-initialized image into host-readable storage-buffer data. Any nonzero source component appears in the final exact comparison.

#### Structural Design

| Phase | Shader action |
|-------|---------------|
| Work distribution | Each workgroup handles one row; local invocations divide columns. |
| Bounds check | Invocations outside the 4x4 extent do not read or write. |
| Image observation | `texelFetch` reads the selected texel at mip level 0. |
| Result recording | The shader writes one `vec4` per pixel to `ssbo.pixels`. |

#### Shader Code

```glsl
#version 460
layout (local_size_x=64, local_size_y=1, local_size_z=1) in;
/// Binding 0 is the sampled R8_UNORM image backed by the zero-initialized allocation.
layout (set=0, binding=0) uniform sampler2D res;
/// Binding 1 stores one vec4 result per pixel for host comparison.
layout (set=0, binding=1) buffer OutBlock { vec4 pixels[]; } ssbo;
void main(void) {
    // One row per WG.
    const uint width = 4;
    const uint height = 4;
    const uint wgSize = gl_WorkGroupSize.x;
    const uint pixelsPerInv = (width + (wgSize - 1u)) / wgSize;
    for (uint i = 0; i < pixelsPerInv; ++i) {
        const uint col = i * wgSize + gl_LocalInvocationIndex;
        const uint row = gl_WorkGroupID.x;
        if (col < width && row < height) {
            vec4 color = texelFetch(res, ivec2(col, row), 0);
            const uint outIndex = row * width + col;
            ssbo.pixels[outIndex] = color;
        }
    }
}
```

#### Additional Info

- [`ImageTransitionTest::iterate`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L738-L816) dispatches one workgroup for each image row and invalidates the result allocation before host comparison.
- The source uses the default `SourceCollections` build options, so the baseline target is SPIR-V 1.0.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Sampled versus storage | Selects `sampler2D`/`texelFetch` or `image2D`/`imageLoad`, including the storage image format qualifier. | [`ImageTransitionCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L455-L474) |
| Channel class | Selects `vec4`, `ivec4`, or `uvec4` resources and SSBO values. | [`ImageTransitionCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L455-L468) |
| Extent | Replaces generated width/height constants and changes dispatch row count. | [`ImageTransitionCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L476-L497) |
| Fragment stage | Uses fragment coordinates and a full-screen vertex shader instead of workgroup indexing. | [`ImageTransitionCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L499-L524) |

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
; Bound: 77
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationIndex %gl_WorkGroupID
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %i "i"
               OpName %col "col"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %row "row"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %color "color"
               OpName %res "res"
               OpName %outIndex "outIndex"
               OpName %OutBlock "OutBlock"
               OpMemberName %OutBlock 0 "pixels"
               OpName %ssbo "ssbo"
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %res Binding 0
               OpDecorate %res DescriptorSet 0
               OpDecorate %_runtimearr_v4float ArrayStride 16
               OpDecorate %OutBlock BufferBlock
               OpMemberDecorate %OutBlock 0 Offset 0
               OpDecorate %ssbo Binding 1
               OpDecorate %ssbo DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
       %bool = OpTypeBool
    %uint_64 = OpConstant %uint 64
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_4 = OpConstant %uint 4
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %45 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %46 = OpTypeSampledImage %45
%_ptr_UniformConstant_46 = OpTypePointer UniformConstant %46
        %res = OpVariable %_ptr_UniformConstant_46 UniformConstant
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
      %int_0 = OpConstant %int 0
%_runtimearr_v4float = OpTypeRuntimeArray %v4float
   %OutBlock = OpTypeStruct %_runtimearr_v4float
%_ptr_Uniform_OutBlock = OpTypePointer Uniform %OutBlock
       %ssbo = OpVariable %_ptr_Uniform_OutBlock Uniform
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
      %int_1 = OpConstant %int 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_uint Function
        %col = OpVariable %_ptr_Function_uint Function
        %row = OpVariable %_ptr_Function_uint Function
      %color = OpVariable %_ptr_Function_v4float Function
   %outIndex = OpVariable %_ptr_Function_uint Function
               OpStore %i %uint_0
               OpBranch %10
         %10 = OpLabel
               OpLoopMerge %12 %13 None
               OpBranch %14
         %14 = OpLabel
         %15 = OpLoad %uint %i
         %18 = OpULessThan %bool %15 %uint_1
               OpBranchConditional %18 %11 %12
         %11 = OpLabel
         %20 = OpLoad %uint %i
         %22 = OpIMul %uint %20 %uint_64
         %25 = OpLoad %uint %gl_LocalInvocationIndex
         %26 = OpIAdd %uint %22 %25
               OpStore %col %26
         %31 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %32 = OpLoad %uint %31
               OpStore %row %32
         %33 = OpLoad %uint %col
         %35 = OpULessThan %bool %33 %uint_4
         %36 = OpLoad %uint %row
         %37 = OpULessThan %bool %36 %uint_4
         %38 = OpLogicalAnd %bool %35 %37
               OpSelectionMerge %40 None
               OpBranchConditional %38 %39 %40
         %39 = OpLabel
         %49 = OpLoad %46 %res
         %50 = OpLoad %uint %col
         %52 = OpBitcast %int %50
         %53 = OpLoad %uint %row
         %54 = OpBitcast %int %53
         %56 = OpCompositeConstruct %v2int %52 %54
         %58 = OpImage %45 %49
         %59 = OpImageFetch %v4float %58 %56 Lod %int_0
               OpStore %color %59
         %61 = OpLoad %uint %row
         %62 = OpIMul %uint %61 %uint_4
         %63 = OpLoad %uint %col
         %64 = OpIAdd %uint %62 %63
               OpStore %outIndex %64
         %69 = OpLoad %uint %outIndex
         %70 = OpLoad %v4float %color
         %72 = OpAccessChain %_ptr_Uniform_v4float %ssbo %int_0 %69
               OpStore %72 %70
               OpBranch %40
         %40 = OpLabel
               OpBranch %13
         %13 = OpLabel
         %73 = OpLoad %uint %i
         %75 = OpIAdd %uint %73 %int_1
               OpStore %i %75
               OpBranch %10
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [`allocateZeroInitMemory`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L113-L133) adds the zero-initialize flag for every tested allocation.
- `clear_buffer` iterates all compatible memory types except protected and unsupported AMD device-coherent types. It copies non-host-visible buffer contents to a host-visible destination, invalidates the destination allocation, and runs `memcmp` against zero bytes.
- Color image cases transition the complete image from `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT`. Transfer cases copy the selected mip. Shader cases bind the image at descriptor binding 0 and the result buffer at binding 1, then dispatch or draw before host comparison.
- Integer outputs use `intThresholdCompare`; floating-point and normalized outputs use `floatThresholdCompare`. Both use zero thresholds. The reference includes an alpha value of one when the observed format has no alpha channel.
- Depth/stencil cases render after transition and compare the copied color attachment against an exact blue reference image.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `clear_buffer` | The zero-initialize allocation flag, buffer binding, memory-type selection, copy path, or host readback exposes nonzero contents. |
| `image_transition` | The zero-initialized image contents, initial-layout transition, image read path, descriptor/resource access, or readback comparison is incorrect. |
| `image_transition.comp` | Compute image access or storage-buffer result production does not preserve the expected zero values. |
| `image_transition.frag` | Fragment image access or rasterization/readback result production does not preserve the expected zero values. |
| `image_transition.xfer` | The image-to-buffer transfer path or its layout transition exposes unexpected contents. |
| `image_transition.depth_stencil` | The depth/stencil transition or render-pass path produces an unexpected validation image. |

### Cause Analysis

#### Buffer contents are not zero

**Possible failure symptoms:** `memcmp` finds a nonzero byte in a directly mapped allocation or copied readback buffer for at least one tested memory type.

**Possible implementation causes:** The implementation may not apply the zero-initialize allocation flag to the selected memory type, or the binding/copy path may expose contents other than the allocation's initial state. The source logs the failing memory type, which provides the first distinction for investigation.

#### Color image observation is not zero

**Possible failure symptoms:** Transfer, compute, or fragment output differs from the zero reference for one or more pixels or components.

**Possible implementation causes:** The zero-initialized image state, transition from `VK_IMAGE_LAYOUT_ZERO_INITIALIZED_EXT`, descriptor image access, or copy/readback path may be incorrect. A failure isolated to one read path should be investigated against that path's barrier, layout, and resource access rather than assumed to originate in allocation.

#### Compute or fragment result production fails

**Possible failure symptoms:** The SSBO contains unexpected values even though another image read path for the same format and extent passes.

**Possible implementation causes:** Descriptor interpretation, sampled/storage image reads, shader execution, or shader-write visibility to the host may be incorrect. The stage-specific case and exact generated shader distinguish compute from fragment behavior.

#### Depth/stencil render validation fails

**Possible failure symptoms:** The copied color attachment differs from the exact blue reference after the depth/stencil image is transitioned and used for drawing.

**Possible implementation causes:** The zero-initialized depth/stencil contents or their transition to attachment use may affect depth/stencil testing incorrectly. Render-pass, draw, or copyback behavior can also produce the symptom; the observed color image alone does not locate the fault without source-level investigation.

## Case Pruning

### Requirement-based pruning

- The entire test family requires `VK_EXT_zero_initialize_device_memory` and is not registered for Vulkan SC.
- Resource cases skip unsupported formats, usages, extents, mip counts, and compatible memory-type combinations.
- Protected and AMD device-coherent memory types are excluded by source policy because the needed extension setup is not enabled for them.
- Depth/stencil cases require format support for attachment usage.

### Design-based pruning

- Transfer image reads exclude compressed formats because the implementation does not calculate compressed block copies for this path.
- Three-channel color formats are excluded from storage image cases.
- `xfer` pairs only with transfer-source usage. `comp` and `frag` pair only with sampled or storage usage.
- One compute walkthrough represents the common shader observation mechanism; fragment differences are summarized rather than duplicating the same image-to-SSBO logic.

## Key Takeaways

- The test observes zero-initialized allocations through resource behavior, not by assuming allocation success proves zero contents.
- Buffer cases separate direct host inspection from copied readback for non-host-visible memory.
- Image cases cover transfer and two shader stages, plus a separate depth/stencil attachment path.
- A stage-specific failure identifies the observation path that failed but does not by itself prove the allocation, transition, shader, or readback layer is responsible.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Allocation helper | [`allocateZeroInitMemory`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L113-L133) | Adds the flag under test. |
| Buffer path | [`clearBufferAllocation`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L136-L221) | Implements memory-type iteration and byte comparison. |
| Shader builder | [`ImageTransitionCase::initPrograms`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L445-L528) | Generates all color-image shader variants. |
| Color image path | [`ImageTransitionTest::iterate`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L530-L884) | Implements transitions, transfer/shader reads, and comparison. |
| Depth/stencil path | [`DepthFormatTest::iterate`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1031-L1246) | Implements attachment validation. |
| Registration | [`createClearedAllocationControlTests`](../../../modules/vulkan/memory/vktMemoryZeroInitializeDeviceMemoryTests.cpp#L1252-L1395) | Defines family hierarchy and case matrix. |
| Mustpass coverage | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt) | Lists selected `dEQP-VK.memory.zero_initialize_device_memory.*` cases. |
