## Overview

**Core question:** Can Vulkan images remain in `VK_IMAGE_LAYOUT_GENERAL` while the selected transfer, shader synchronization, attachment-local read, or multisample attachment path produces the expected result?

- [`vktImageGeneralLayoutTests.cpp`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L47-L2435) implements the `image.general_layout` test family.
- Every family retains its exercised images in `GENERAL` for the relevant operations. The tests then establish the dependencies needed for the next access, copy an observable result to host-visible memory, and compare it with generated reference data.
- The source combines four distinct behaviors: ASTC compressed-image transfer and sampling, synchronization2 memory-barrier coverage, input-attachment reads through render passes or dynamic rendering, and multisample color-attachment arrangements.

## Background Knowledge

For the shared concepts image layouts and synchronization, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **A general layout does not synchronize access.** `VK_IMAGE_LAYOUT_GENERAL` permits the image uses selected by these tests, but it does not order operations or make writes visible. An image or memory barrier can retain `GENERAL` as both layouts while supplying the required execution and memory dependency.
- **Input attachments read rendering-local images.** A fragment shader can read an attachment as a `subpassInput`. This test also uses a sampled image as an alternative first-pass read. The dynamic-rendering cases use `VK_KHR_dynamic_rendering_local_read` to associate the rendering attachments with input-attachment indices.

## Registration Hierarchy

```text
image.general_layout
├── astc_sample
├── memory_barrier
├── input_attachment
└── msaa
```

[`createImageGeneralLayoutTests()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2304-L2435) registers the four families. `memory_barrier` and the ASTC host-copy leaves are absent when `CTS_USES_VULKANSC` is defined. Each family has a separate parameter matrix described below.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `astc_sample`, `memory_barrier`, `input_attachment`, `msaa` | Selects the image-use property under test. | [Registration](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2304-L2435) |
| ASTC transfer form | `copy_into_image`, `copy_from_image`, `host_copy_into_image`, `host_copy_from_image`, `sample_alias` | Chooses the operation between two sampling passes, or the mutable ASTC alias-view path. The host-copy forms are not VulkanSC leaves. | [ASTC leaves](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2310-L2329) |
| Barrier shader stage | `compute`, `fragment` | Selects the producer and consumer execution path. | [Stage matrix](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2333-L2341) |
| Barrier ordering | `write_read`, `read_write` | Selects whether the first shader writes the image or reads the uploaded value before the synchronization2 barrier. | [Ordering matrix](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2354-L2374) |
| Barrier access pair | `shader_read_write`, `sampled_read_storage_write`, `storage_read_storage_write` | Supplies the `VkAccessFlags2` values used for the selected read and write accesses. | [Access matrix](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2343-L2352) |
| Input read form | `input_attachment`, `sampled` | Selects `subpassLoad` or `texture` in the first fragment shader. | [Input matrix](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2390-L2416) |
| Input dependency form | `execution`, `memory`, `image` | Selects no explicit barrier, a same-layout memory barrier, or a same-layout image barrier between the two passes. | [Barrier matrix](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2380-L2388) |
| Input rendering form | `render_pass`, `dynamic_rendering` | Selects two subpasses or two dynamic-rendering instances. | [Rendering matrix](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2401-L2411) |
| MSAA arrangement | `same`, `different` | Selects whether the initial multisample and single-sample targets are reused as the final multi-attachment render targets or whether separate images are resolved afterward. | [MSAA matrix](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2418-L2433) |
| MSAA attachment count | `4`, `8`, `16` | Selects the number of color attachments written by the final graphics pipeline. | [MSAA leaves](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2424-L2429) |

All families use a 128 by 128, one-layer image extent. ASTC uses `VK_FORMAT_ASTC_8x8_UNORM_BLOCK` for the sampled view and `R8G8B8A8_UNORM` output. The barrier family uses `R32_SFLOAT`; input-attachment and MSAA families use `R8G8B8A8_UNORM`. MSAA targets use four samples for the multisampled images.

## Behavior Parameters

The test family is the primary behavioral axis. Its values change the image mechanism being tested, while the deeper path components select variants of that mechanism.

### `astc_sample` - compressed-image transfer and sampling

The ASTC family samples an `ASTC_8x8_UNORM_BLOCK` image into an RGBA8 color attachment while the sampled image remains in `GENERAL`. The standard copy leaves replace or read the compressed blocks between sampling passes. `host_copy_into_image` and `host_copy_from_image` use `VK_EXT_host_image_copy`; `sample_alias` creates an ASTC sRGB image with mutable-format and block-texel-view-compatible flags, then views it as ASTC UNORM.

The source generates deterministic ASTC LDR blocks and decompresses them to form the sampling reference. It compares sampled output with a tolerance of `0.04`; copy-out leaves additionally compare the compressed byte stream directly.

### `memory_barrier` - shader producer and consumer dependency

The memory-barrier family tests a synchronization2 memory barrier between two accesses to an `R32_SFLOAT` image in `GENERAL`. The stage parameter selects compute dispatches or graphics draws. The access-pair parameter selects storage-image reads and writes, or sampled reads with storage writes.

For `write_read`, the first shader stores `x + y`, then the second shader reads it. For `read_write`, the first shader reads the uploaded random value, then the second stores `x + y`. The test copies the image and, for the fragment path, the framebuffer result to host-visible buffers. The expected results distinguish the producer/consumer order.

### `input_attachment` - two-pass attachment-local read

The input-attachment family initializes the first RGBA8 image from a random buffer. The first fragment pass reads it as either an input attachment or a sampled image and writes half the value to the second image. The second pass reads the second image as an input attachment, writes `1.0 - value` to the first image, and leaves the final result in `GENERAL` for copyback.

The dependency form selects an execution-only path, an explicit memory barrier, or an explicit same-layout image barrier. The rendering form selects a two-subpass render pass or two dynamic-rendering instances with local-read attachment-index configuration.

### `msaa` - many color attachments with four-sample targets

The MSAA family renders an interpolated coordinate color to alternating four-sample and one-sample attachments. The `same` arrangement uses those images directly in a later render pass with many color attachments. The `different` arrangement uses separate targets for that pass, then resolves the additional four-sample images to single-sample images.

The generated second fragment shader declares one output per selected attachment count and writes the same coordinate color to each. The host reads every observed single-sample attachment and checks the coordinate pattern.

## Shader Analysis

The walkthrough uses the write shader from `dEQP-VK.image.general_layout.memory_barrier.compute.write_read.storage_read_storage_write`. This leaf isolates the producer side of the synchronization2 dependency: a compute invocation stores the value that the following compute read must observe.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.general_layout.memory_barrier.compute.write_read.storage_read_storage_write
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `compute` | The source uses a local-size-one compute write pipeline and dispatches 128 by 128 workgroups. |
| `write_read` | This shader is the producer. The following compute shader must read its result after a synchronization2 memory barrier. |
| `storage_read_storage_write` | The consumer uses `imageLoad` through the storage-image descriptor; the barrier uses storage-read and storage-write access masks. |

#### Purpose

The shader writes a deterministic scalar value to each `R32_SFLOAT` texel. The test later verifies that the consumer and the transfer copyback observe `x + y` for every texel.

#### Structural Design

| Phase | Shader action | Test significance |
|-------|---------------|-------------------|
| Address | Reads `gl_GlobalInvocationID.xy`. | Maps each local-size-one workgroup to one image texel. |
| Value | Computes `coord.x + coord.y` and splats it to `vec4`. | Supplies a host-derivable reference value. |
| Store | Writes the value through the `r32f image2D` at binding 0. | Produces the data that the synchronization2 barrier must make available to the consumer. |

#### Shader Code

```glsl
#version 450
layout (local_size_x = 1, local_size_y = 1) in;
/// Binding 0 is the `R32_SFLOAT` storage image. The write pass stores one value per invocation.
layout (binding = 0, r32f) uniform image2D storageImage;
void main()
{
    /// The host dispatches 128 by 128 workgroups, so this names one image texel.
    ivec2 coord = ivec2(gl_GlobalInvocationID.xy);
    vec4 color = vec4(coord.x + coord.y);
    imageStore(storageImage, coord, color);
}
```

#### Additional Info

- [`MemoryBarrierCase::initPrograms()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1131-L1140) emits this shader text, except for the wiki-authored `///` comments.
- The host binds the image as a storage image at binding 0, retains its descriptor layout as `GENERAL`, and records a compute-to-compute `VkMemoryBarrier2` before dispatching the generated read shader ([execution](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L842-L970)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Barrier stage | `fragment` uses a fullscreen vertex/fragment pair; `compute` uses `gl_GlobalInvocationID` and dispatches. | [Generated programs](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1091-L1165) |
| Read access pair | The generated reader uses `imageLoad` for `storage_read_storage_write`, or `texture` through binding 1 for the other two access-pair names. | [Read-program branch](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1113-L1158) |
| Ordering | `read_write` binds the generated read pipeline first and the write pipeline second. | [Pipeline selection](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L937-L989) |

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
; Bound: 39
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %coord "coord"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %color "color"
               OpName %storageImage "storageImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %storageImage Binding 0
               OpDecorate %storageImage DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
     %uint_0 = OpConstant %uint 0
%_ptr_Function_int = OpTypePointer Function %int
     %uint_1 = OpConstant %uint 1
         %32 = OpTypeImage %float 2D 0 0 0 2 R32f
%_ptr_UniformConstant_32 = OpTypePointer UniformConstant %32
%storageImage = OpVariable %_ptr_UniformConstant_32 UniformConstant
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %coord = OpVariable %_ptr_Function_v2int Function
      %color = OpVariable %_ptr_Function_v4float Function
         %15 = OpLoad %v3uint %gl_GlobalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %17 = OpBitcast %v2int %16
               OpStore %coord %17
         %24 = OpAccessChain %_ptr_Function_int %coord %uint_0
         %25 = OpLoad %int %24
         %27 = OpAccessChain %_ptr_Function_int %coord %uint_1
         %28 = OpLoad %int %27
         %29 = OpIAdd %int %25 %28
         %30 = OpConvertSToF %float %29
         %31 = OpCompositeConstruct %v4float %30 %30 %30 %30
               OpStore %color %31
         %35 = OpLoad %32 %storageImage
         %36 = OpLoad %v2int %coord
         %37 = OpLoad %v4float %color
               OpImageWrite %35 %36 %37
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **ASTC:** The host creates a 128 by 128 compressed image, host-visible source and copy buffers, an RGBA8 color attachment, a combined image sampler, and a fullscreen graphics pipeline. It first uploads generated blocks, samples the image, optionally performs the selected copy operation, samples again, and copies the color attachment to a host-visible buffer. The host compares decoded reference pixels with a `0.04` tolerance and directly compares compressed bytes for copy-out variants ([execution and checks](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L239-L599)).
- **Memory barrier:** The host uploads deterministic random floats to an `R32_SFLOAT` image and creates storage-image, sampled-image, and storage-buffer descriptors. It records the initial transfer-to-shader barrier, the selected producer and consumer shader operations, a synchronization2 barrier carrying the selected access masks, and transfer readback. It compares every float with `1e-6` ([execution and checks](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L690-L1063)).
- **Input attachment:** The host copies random RGBA8 bytes into the first image, prepares two image views and a descriptor set, and records either a two-subpass render pass or two dynamic-rendering operations. The first pass divides the source by two; the second subtracts the result from one. It copies the first image back and compares every byte with `255 - input / 2`, allowing one unit ([execution and checks](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1197-L1719)).
- **MSAA:** The host creates alternating four-sample and single-sample RGBA8 images. It renders coordinate colors, transitions them for the later attachment use, and either reads the single-sample images directly or resolves separate four-sample images. It reads the final single-sample images into host-visible buffers and checks each attachment's red, green, blue, and alpha channels ([execution and checks](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1812-L2237)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `astc_sample` | ASTC image use in `GENERAL`, compressed transfer or host-image-copy handling, mutable alias view setup, fragment sampling, or decoded-output comparison. |
| `memory_barrier` | synchronization2 stage/access dependency, storage versus sampled image access, compute or fragment execution path, or transfer readback after shader work. |
| `input_attachment` | Attachment-local read semantics, selected execution/memory/image barrier path, sampled versus input-attachment descriptor path, render-pass setup, or dynamic-rendering local-read setup. |
| `msaa` | General-layout color attachment use, four-sample rendering, selected attachment routing, resolve handling for `different`, or per-attachment readback comparison. |

### Cause Analysis

#### ASTC image access, transfer, or sampling

**Possible failure symptoms:** A sampled RGBA8 channel differs from the CTS ASTC decompression reference by more than `0.04`, or a copy-from-image leaf reports unequal compressed bytes. The log identifies the differing pixel/channel or compressed byte.

**Possible implementation causes:** The source exercises transfer and sampling operations with the compressed image in `GENERAL`. A failure can arise in ASTC block transfer, host image copy, mutable alias view interpretation, descriptor sampling, or the dependency that makes a preceding transfer or host copy visible to the fragment shader. The case's result cannot isolate a particular component without comparing the corresponding copy and alias leaves.

#### Synchronization2 access dependency or shader image access

**Possible failure symptoms:** A copied image texel differs from `x + y`, or the consumer output differs from `x + y` for `write_read` or from the uploaded random value for `read_write`. The log reports the failing index and float values.

**Possible implementation causes:** The selected leaf changes shader stage, ordering, and access masks. Source-level triage should compare the paired stage and access leaves to distinguish storage/sampled access from a stage/access dependency that failed to make the producer result available and visible to the consumer. The test also covers the shader-to-transfer dependency before image copyback.

#### Attachment-local read or rendering dependency

**Possible failure symptoms:** A copied output byte differs from `255 - input / 2` by more than one. The source logs the expected and observed values for the failing comparison.

**Possible implementation causes:** A failure may involve the selected first-pass descriptor form, the attachment input mapping, the transition between the two render operations, or the final attachment-to-transfer dependency. Comparing `input_attachment` with `sampled`, and `render_pass` with `dynamic_rendering`, narrows the affected access and rendering setup. The `memory` and `image` leaves specifically exercise same-layout synchronization forms.

#### Multisample attachment routing or resolve

**Possible failure symptoms:** Any observed attachment contains a red or green coordinate value outside the tolerance, or a blue/alpha channel differs from zero/255. The log reports the attachment index, pixel index, expected color, and actual color.

**Possible implementation causes:** The failure can involve four-sample color writes, the large color-attachment pipeline configuration, attachment routing, or the explicit resolve path used by `different`. Comparing `same` with `different` separates the direct reused-attachment path from the separate-image and resolve path. The source-level result does not identify a particular sample, so further investigation must inspect the selected attachment configuration.

## Case Pruning

- `memory_barrier` is registered only outside VulkanSC because the source encloses its registration in `#ifndef CTS_USES_VULKANSC`.
- ASTC host-copy leaves are also outside VulkanSC and require `VK_EXT_host_image_copy`. All ASTC leaves require `VK_EXT_astc_decode_mode`, `textureCompressionASTC_LDR`, and sampled-image support for `VK_FORMAT_ASTC_8x8_UNORM_BLOCK` ([support check](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L617-L635)).
- Input-attachment leaves require `VK_KHR_synchronization2`. `dynamic_rendering` leaves additionally require `VK_KHR_dynamic_rendering` and `VK_KHR_dynamic_rendering_local_read` ([support check](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1737-L1745)).
- Each MSAA leaf requires `maxColorAttachments` to meet its selected count. The source registers `4`, `8`, and `16`, then rejects unsupported counts in `checkSupport()` ([support check](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2255-L2259)).

## Key Takeaways

- `GENERAL` provides the common layout condition for the tested image uses. Barriers still establish the ordering and visibility that dependent operations require.
- The four test families cover different correctness properties, so their pass criteria and failure triage differ: decoded ASTC output, float visibility, transformed attachment bytes, and multisample coordinate output.
- The registration matrix varies transfer form, stage/access dependency, attachment read/rendering form, and attachment arrangement without changing the central layout condition.

## Source Reference Appendix

| Topic | Source reference |
|-------|------------------|
| ASTC setup, operations, validation, and support gates | [`AstcSampleTestInstance::iterate()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L239-L599), [`AstcSampleCase::checkSupport()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L617-L635) |
| Generated ASTC and memory-barrier programs | [`AstcSampleCase::initPrograms()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L642-L665), [`MemoryBarrierCase::initPrograms()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1091-L1165) |
| Memory-barrier resource setup, synchronization, and comparisons | [`MemoryBarrierTestInstance::iterate()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L690-L1063) |
| Input-attachment execution, generated programs, and support gates | [`InputAttachmentTestInstance::iterate()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1197-L1719), [`InputAttachmentCase`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1721-L1791) |
| MSAA setup, validation, generated programs, and support gate | [`MsaaTestInstance::iterate()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L1812-L2237), [`MsaaCase`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2239-L2300) |
| Registration | [`createImageGeneralLayoutTests()`](../../../modules/vulkan/image/vktImageGeneralLayoutTests.cpp#L2304-L2435) |
| Vulkan layout and synchronization semantics | [`resources.adoc`](../../../../vulkan-docs/src/chapters/resources.adoc), [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) |
| Copy, render-pass, and dynamic local-read semantics | [`copies.adoc`](../../../../vulkan-docs/src/chapters/copies.adoc), [`renderpass.adoc`](../../../../vulkan-docs/src/chapters/renderpass.adoc) |
