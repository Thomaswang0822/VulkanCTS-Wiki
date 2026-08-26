## Overview

**Core question:** Does synchronization2 preserve image contents when an image barrier keeps the same layout, and does it track later layout changes recorded on alternating universal and compute queues?

- This page covers the synchronization2-only `layout_transition` test family implemented in [`vktSynchronizationImageLayoutTransitionTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp).
- `no_op` checks the rule that equal old and new layouts are ignored and the image contents remain intact, even when both values are `VK_IMAGE_LAYOUT_UNDEFINED`.
- `compute_transition` and `compute_transition_storage` record successive layout changes on an exclusive compute queue and the universal queue, clear a four-sample image, and verify every sample through a compute shader.
- The legacy `synchronization` test category does not register this family.

## Background Knowledge

For the shared concept synchronization scopes, see [Background Knowledge](../../categories/synchronization2.md#background-knowledge) of the `synchronization2` page.

- An image memory barrier names an old layout and a new layout for an image subresource range. If the values differ, the barrier defines a layout transition. If the queue-family indices and layouts are equal, Vulkan ignores the layouts and preserves the contents regardless of the values or the image's current layout. This rule is why an `UNDEFINED`/`UNDEFINED` barrier does not permit content loss here.
- An image created with `VK_SHARING_MODE_EXCLUSIVE` can be accessed by one queue family at a time. The compute cases do not encode queue-family ownership transfers: `makeImageMemoryBarrier2()` leaves both queue-family indices at `VK_QUEUE_FAMILY_IGNORED`. They do not rely on contents produced before a queue-family change; the universal queue clears the image after the alternating layout-only submissions.
- A multisample image stores a value for each sample of each pixel. `sampler2DMS` with `texelFetch` and `image2DMS` with `imageLoad` both accept an explicit sample index, which lets one compute invocation copy one pixel/sample value to the readback buffer.

## Registration Hierarchy

```text
synchronization2.layout_transition
├── compute_transition
├── compute_transition_storage
└── no_op
```

The source factory registers these three direct test case leaves in [`createImageLayoutTransitionTests()`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L744-L757). The synchronization2 dispatcher adds the family only on its synchronization2 branch in [`createTestsInternal()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L144), and the [default mustpass file](../../../mustpass/main/vk-default/synchronization2.txt#L32027-L32029) contains all three paths.

## Parameter Dimensions and Observed Values

The source registers three fixed scenarios rather than generating a larger matrix.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Scenario | `no_op`, `compute_transition`, `compute_transition_storage` | Selects same-layout preservation, multisample sampled-image readback, or multisample storage-image readback | [factory](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L744-L757) |
| Image extent | 64x64 for `no_op`; 8x8 for both compute cases | Matches the graphics framebuffer or the compute shader's local X/Y size | [graphics constants](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L55-L79), [compute parameters](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L385-L420) |
| Sample count | `VK_SAMPLE_COUNT_1_BIT` for `no_op`; `VK_SAMPLE_COUNT_4_BIT` for both compute cases | The graphics case checks one color per pixel; the compute cases check four values per pixel | [graphics image creation](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L59-L79), [compute parameters](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L389-L402) |
| Image format | `VK_FORMAT_R8G8B8A8_UNORM` | Fixes the attachment and compute-image format in all three cases | [graphics format](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L55-L79), [compute format](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L399-L419) |
| Compute read mode | `sampler2DMS` / `texelFetch`; `image2DMS` / `imageLoad` | Selects sampled-image or storage-image access and the final readable layout | [compute shader generation](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L491-L517), [descriptor setup](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L522-L613) |

## Behavior Parameters

The primary behavioral axis is the layout transition scenario. Its values correspond to the three direct test case leaves but describe the property each leaf checks.

### `no-op undefined transition`: preserve contents when layouts are ignored

`no_op` draws an alpha-blended yellow quad, inserts a `VkImageMemoryBarrier2` with both layouts set to `VK_IMAGE_LAYOUT_UNDEFINED`, and draws the same quad again. Because the helper leaves both queue-family indices at `VK_QUEUE_FAMILY_IGNORED`, the indices and layouts compare equal. Vulkan therefore ignores the layout values and requires the image contents to survive for the second blend.

### `cross-queue sampled read`: carry layout state to a multisample sampler read

`compute_transition` records `UNDEFINED` to `COLOR_ATTACHMENT_OPTIMAL` on the universal queue, then `COLOR_ATTACHMENT_OPTIMAL` to `TRANSFER_DST_OPTIMAL` on the exclusive compute queue. After both submissions finish, the universal queue clears the image blue, transitions it to `SHADER_READ_ONLY_OPTIMAL`, and dispatches a compute shader that copies every sample through `sampler2DMS` and `texelFetch`.

### `cross-queue storage-image read`: carry layout state to a multisample storage read

`compute_transition_storage` uses the same three-submission sequence. It creates the image with `VK_IMAGE_USAGE_STORAGE_BIT`, transitions the cleared image to `VK_IMAGE_LAYOUT_GENERAL`, binds a storage-image descriptor, and reads every sample through `image2DMS` and `imageLoad`. This separate leaf also applies the storage format and four-sample support check.

## Shader Analysis

One walkthrough is enough because the sampled and storage compute shaders differ only in the image declaration and read instruction. The graphics shaders in `no_op` provide a full-screen position and a fixed fragment color; their shader logic does not perform the synchronization check.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.synchronization2.layout_transition.compute_transition
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute_transition` | Uses the sampled-image branch of `ComputeLayoutTransitionCase::initPrograms()` |
| 8x8 extent and four samples | Produces a single 8x8x4 local workgroup, one invocation per pixel/sample tuple |
| `sampler2DMS` | Reads the blue multisample image in `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` |

#### Purpose

The shader exposes the image contents after the alternating-queue layout sequence. Each invocation reads one sample and writes it unchanged to a host-visible storage buffer.

#### Structural Design

| Shader phase | Operation | Observable result |
|--------------|-----------|-------------------|
| Select | Read `x`, `y`, and sample `s` from `gl_LocalInvocationID` | Covers all 8x8x4 pixel/sample tuples |
| Index | Compute `4 * 8 * y + 4 * x + s` | Assigns each tuple a unique output element |
| Copy | `texelFetch(inImage, ivec2(x, y), int(s))` | Reads one multisample value |
| Record | Store the `vec4` in `outBuffer.color[idx]` | Makes the value available to the host check |

#### Shader Code

```glsl
#version 460
layout (local_size_x=8, local_size_y=8, local_size_z=4) in;
/// Binding 0 is the four-sample 8x8 image after its blue clear and transition to SHADER_READ_ONLY_OPTIMAL.
layout (set=0, binding=0) uniform sampler2DMS inImage;
/// Binding 1 stores one vec4 for each (x, y, sample) tuple so the host can check all 256 values.
layout (set=0, binding=1, std430) buffer OutBlock { vec4 color[]; } outBuffer;
void main (void) {
    const uint width = gl_WorkGroupSize.x;
    const uint height = gl_WorkGroupSize.y;
    const uint samples = gl_WorkGroupSize.z;
    const uint x = gl_LocalInvocationID.x;
    const uint y = gl_LocalInvocationID.y;
    const uint s = gl_LocalInvocationID.z;
    const uint idx = samples * width * y + samples * x + s;
    /// Read the invocation's selected sample and preserve it unchanged for host comparison.
    const vec4 color = texelFetch(inImage, ivec2(x, y), int(s));
    outBuffer.color[idx] = color;
}
```

#### Additional Info

- The source inserts this shader without explicit `ShaderBuildOptions`, so the CTS baseline target is SPIR-V 1.0.
- `height` is part of the generated source even though the indexing expression does not reference it.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Compute read mode | `compute_transition_storage` changes binding 0 to `layout(..., rgba8) uniform image2DMS`, replaces `texelFetch` with `imageLoad`, and leaves the output indexing unchanged | [shader branch](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L491-L517) |
| Scenario | `no_op` uses fixed vertex and fragment shaders instead of the compute shader; the fragment shader outputs `vec4(1.0, 1.0, 0.0, 0.4)` | [graphics shader generation](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L355-L373) |

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
; Bound: 65
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationID
               OpExecutionMode %main LocalSize 8 8 4
               OpSource GLSL 460
               OpName %main "main"
               OpName %x "x"
               OpName %gl_LocalInvocationID "gl_LocalInvocationID"
               OpName %y "y"
               OpName %s "s"
               OpName %idx "idx"
               OpName %color "color"
               OpName %inImage "inImage"
               OpName %OutBlock "OutBlock"
               OpMemberName %OutBlock 0 "color"
               OpName %outBuffer "outBuffer"
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %inImage Binding 0
               OpDecorate %inImage DescriptorSet 0
               OpDecorate %_runtimearr_v4float ArrayStride 16
               OpDecorate %OutBlock BufferBlock
               OpMemberDecorate %OutBlock 0 Offset 0
               OpDecorate %outBuffer Binding 1
               OpDecorate %outBuffer DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
    %uint_32 = OpConstant %uint 32
     %uint_4 = OpConstant %uint 4
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %38 = OpTypeImage %float 2D 0 0 1 1 Unknown
         %39 = OpTypeSampledImage %38
%_ptr_UniformConstant_39 = OpTypePointer UniformConstant %39
    %inImage = OpVariable %_ptr_UniformConstant_39 UniformConstant
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_runtimearr_v4float = OpTypeRuntimeArray %v4float
   %OutBlock = OpTypeStruct %_runtimearr_v4float
%_ptr_Uniform_OutBlock = OpTypePointer Uniform %OutBlock
  %outBuffer = OpVariable %_ptr_Uniform_OutBlock Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
     %uint_8 = OpConstant %uint 8
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_8 %uint_8 %uint_4
       %main = OpFunction %void None %3
          %5 = OpLabel
          %x = OpVariable %_ptr_Function_uint Function
          %y = OpVariable %_ptr_Function_uint Function
          %s = OpVariable %_ptr_Function_uint Function
        %idx = OpVariable %_ptr_Function_uint Function
      %color = OpVariable %_ptr_Function_v4float Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_0
         %15 = OpLoad %uint %14
               OpStore %x %15
         %18 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_1
         %19 = OpLoad %uint %18
               OpStore %y %19
         %22 = OpAccessChain %_ptr_Input_uint %gl_LocalInvocationID %uint_2
         %23 = OpLoad %uint %22
               OpStore %s %23
         %26 = OpLoad %uint %y
         %27 = OpIMul %uint %uint_32 %26
         %29 = OpLoad %uint %x
         %30 = OpIMul %uint %uint_4 %29
         %31 = OpIAdd %uint %27 %30
         %32 = OpLoad %uint %s
         %33 = OpIAdd %uint %31 %32
               OpStore %idx %33
         %42 = OpLoad %39 %inImage
         %43 = OpLoad %uint %x
         %45 = OpBitcast %int %43
         %46 = OpLoad %uint %y
         %47 = OpBitcast %int %46
         %49 = OpCompositeConstruct %v2int %45 %47
         %50 = OpLoad %uint %s
         %51 = OpBitcast %int %50
         %52 = OpImage %38 %42
         %53 = OpImageFetch %v4float %52 %49 Sample %51
               OpStore %color %53
         %59 = OpLoad %uint %idx
         %60 = OpLoad %v4float %color
         %62 = OpAccessChain %_ptr_Uniform_v4float %outBuffer %int_0 %59
               OpStore %62 %60
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `no_op` creates a 64x64 single-sample color image, clears it to transparent black, and transitions it to `COLOR_ATTACHMENT_OPTIMAL`. One command buffer draws the full-screen quad, records the synchronization2 barrier with equal `UNDEFINED` layouts, draws again, and copies the image to a host-visible buffer. The host constructs the expected blended color as `((2 - 0.4) * 0.4, (2 - 0.4) * 0.4, 0, 0.4)` and compares every pixel with a `0.01` component threshold.
- Each compute case creates an 8x8 four-sample image and an output storage buffer containing 8x8x4 `vec4` elements. Descriptor binding 0 selects a combined image sampler or a storage image; binding 1 exposes the output buffer.
- The first compute-case submission records `UNDEFINED` to `COLOR_ATTACHMENT_OPTIMAL` on the universal queue and waits for completion. The second records `COLOR_ATTACHMENT_OPTIMAL` to `TRANSFER_DST_OPTIMAL` on the exclusive compute queue and waits again.
- The third submission returns to the universal queue. It clears the image to `(0, 0, 1, 1)`, records a transfer-write to compute-read barrier while changing to `SHADER_READ_ONLY_OPTIMAL` or `GENERAL`, dispatches one workgroup, and records a compute-write to host-read memory barrier.
- After the third submission completes, the host invalidates the output allocation and compares all 256 `VK_FORMAT_R32G32B32A32_SFLOAT` values with exact blue using a zero threshold. Any mismatch fails the case.

## Failure Meaning

### Failure Cause Mapping

| If this value fails | Possible failure cause(s) |
|---|---|
| `no-op undefined transition` | Incorrect preservation of image contents or execution dependency handling for an `UNDEFINED`/`UNDEFINED` synchronization2 barrier |
| `cross-queue sampled read` | Incorrect queue-family/layout transition, multisample sampling, or shader-read visibility |
| `cross-queue storage-image read` | Incorrect queue-family/layout transition, multisample storage-image access, or format support handling |

### Cause Analysis

#### Equal-layout barrier preservation

**Possible failure symptoms:** `no_op` produces pixels outside the `0.01` threshold after the second blended draw, often showing that the first draw's color did not survive the equal-layout barrier.

**Possible implementation causes:** the synchronization2 image-barrier path may treat `VK_IMAGE_LAYOUT_UNDEFINED` as permission to discard contents without first applying the equal-layout rule. The Vulkan specification states that equal queue-family indices and equal old/new layouts make the layout values ignored and preserve the image contents. The implementation may also fail to enforce the color-attachment write-to-read dependency encoded by the barrier.

#### Alternating-queue layout state and sampled read

**Possible failure symptoms:** one or more of the 256 sampled-image output elements differs from exact blue after `compute_transition`, or the required layout sequence cannot execute successfully.

**Possible implementation causes:** the implementation may lose or misapply the image's layout state between the separately completed universal and exclusive-compute submissions. In the final submission, it may fail to make the transfer clear visible to the compute shader or mishandle a four-sample `sampler2DMS` fetch. Because the case does not encode queue-family ownership transfers and overwrites the image after returning to the universal queue, the check does not require preservation of pre-clear image contents across queue families.

#### Storage-image layout, access, and support handling

**Possible failure symptoms:** `compute_transition_storage` reports unsupported-format handling incorrectly, fails during setup, or returns at least one non-blue value from `imageLoad`.

**Possible implementation causes:** the implementation may report incompatible image format properties, mishandle the transition to `VK_IMAGE_LAYOUT_GENERAL`, fail to make the transfer clear visible to storage-image reads, or lower the multisample `imageLoad` path incorrectly. The source checks the complete storage image usage combination and four-sample support before execution, so a reported unsupported combination should prune the case instead of producing a comparison failure.

## Case Pruning

### Requirement-based pruning

- Every leaf calls `requireDeviceFunctionality("VK_KHR_synchronization2")`; implementations without synchronization2 support skip the case.
- Both compute leaves call `getComputeQueue()`, which requires an exclusive compute queue. If none exists, the CTS reports the case as unsupported.
- `compute_transition_storage` calls `vkGetPhysicalDeviceImageFormatProperties` for the exact format, optimal tiling, storage/color-attachment/transfer-destination usage, and then checks `VK_SAMPLE_COUNT_4_BIT`. An unsupported format or sample count skips only this leaf.

### Design-based pruning

- The factory intentionally registers only the fixed `no_op`, sampled compute, and storage compute scenarios. Extent, format, sample count, and queue sequence are not generated dimensions.
- The dispatcher registers `layout_transition` only for synchronization2. There is no legacy `synchronization.layout_transition` leaf to test.
- Ordinary builds call the core `vkCmdPipelineBarrier2` entry point, while Vulkan SC builds call `vkCmdPipelineBarrier2KHR`. This compile-time choice does not create additional registered cases.

## Key Takeaways

- `no_op` targets the equal-layout exception directly: equal queue-family indices and equal old/new layouts require content preservation even when both layouts are `UNDEFINED`.
- The compute leaves test layout-state handling across separately completed submissions on alternating queue families. They do not encode queue-family ownership transfers or depend on earlier image contents after the queue changes.
- One compute invocation checks each pixel/sample pair, so the exact-blue comparison covers all four samples of every 8x8 pixel.
- The sampled and storage leaves share the same queue sequence but exercise different descriptor types, read instructions, final layouts, and support gates.
- See `Failure Meaning` for the evidence-backed interpretation of comparison or setup failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Equal-layout preservation rule | [Vulkan synchronization specification](../../../../vulkan-docs/src/chapters/synchronization.adoc#L7510-L7521) | Defines when image-barrier layouts are ignored and contents are preserved |
| Exclusive sharing semantics | [Vulkan resource specification](../../../../vulkan-docs/src/chapters/resources.adoc#L11479-L11517) | Defines ownership and content behavior for exclusive resources used by different queue families |
| Image-barrier helper defaults | [`makeImageMemoryBarrier2()` declaration](../../../framework/vulkan/vkBarrierUtil.hpp#L61-L68) | Confirms that omitted queue-family indices become `VK_QUEUE_FAMILY_IGNORED` |
| `no_op` runtime and comparison | [`SynchronizationImageLayoutTransitionTestInstance::iterate()`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L170-L337) | Defines the two draws, equal-layout barrier, copyback, and threshold check |
| Graphics shader generation and support | [`SynchronizationImageLayoutTransitionTest`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L339-L383) | Defines the fixed shaders and synchronization2 requirement |
| Compute parameters, support, and shader | [`ComputeLayoutTransitionCase`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L385-L517) | Defines image values, the storage support gate, and both compute shader branches |
| Compute runtime and comparison | [`ComputeLayoutTransitionInstance::iterate()`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L520-L739) | Defines descriptors, submissions, barriers, dispatch, and exact-blue check |
| Exclusive compute queue requirement | [`DefaultDevice::getComputeQueue()`](../../../modules/vulkan/vktTestCase.cpp#L966-L971) | Shows that the requested compute queue must come from an exclusive compute family |
| Registration | [`createImageLayoutTransitionTests()`](../../../modules/vulkan/synchronization/vktSynchronizationImageLayoutTransitionTests.cpp#L744-L757) | Defines the exact test family and leaves |
| Category dispatch | [`createTestsInternal()`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L144) | Confirms synchronization2-only ownership of the family |
| Default mustpass coverage | [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt#L32027-L32029) | Lists all three executable paths |
