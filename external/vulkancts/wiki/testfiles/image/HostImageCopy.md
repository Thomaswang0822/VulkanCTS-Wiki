## Overview

**Core question:** Does `VK_EXT_host_image_copy` correctly transition eligible image layouts and copy image data between host memory and images, including host image-to-image copies, while preserving the result through direct readback or later graphics/compute use?

- [`vktImageHostImageCopyTests.cpp`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp) implements `image.host_image_copy`, a non-VulkanSC image-category family.
- The suite combines a large draw/dispatch observation matrix with targeted large-image, array, layout, capture/replay, extension-property, performance-query, memory-layout, depth/stencil, and broad simple round-trip paths.
- Host-side operations include `vkTransitionImageLayoutEXT`, `vkCopyMemoryToImageEXT`, `vkCopyImageToMemoryEXT`, and `vkCopyImageToImageEXT`. Some cases use queue transfer commands as a comparison path or to read the final device-observed result.
- The main matrix generates vertex, fragment, and compute shaders. Several targeted paths perform no shader execution; `depth_stencil` has its own graphics programs.

## Background Knowledge

For the shared concepts subresources, copies, layouts, and synchronization, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Host image copies.** `VK_EXT_host_image_copy` supplies host-side layout transitions and copies between host memory and image subresources, plus host image-to-image copies. A region identifies its subresource, offset, and extent; memory-image regions also carry a host pointer and optional row/image strides. The extension's `VK_HOST_IMAGE_COPY_MEMCPY_EXT` flag selects the memcpy-style variants exercised by specific leaves.
- **Layout and format eligibility.** `VkPhysicalDeviceHostImageCopyPropertiesEXT` reports allowed source and destination layouts. The operational cases require the selected layouts, `hostImageCopy` feature, compatible image configuration, and `VK_FORMAT_FEATURE_2_HOST_IMAGE_TRANSFER_BIT_EXT` for the chosen tiling. Host-copy images use `VK_IMAGE_USAGE_HOST_TRANSFER_BIT_EXT` where needed.
- **Device observation.** A host copy becomes observable in the main matrix by sampling the copied image in a fullscreen fragment shader or in a local-size-one compute shader. The resulting output image is copied to host-visible memory for comparison.
- **Format-aware validation.** Ordinary color paths can compare bytes or pixels. Compressed sampled inputs are checked through the sampled output. Depth/stencil paths copy aspects independently and use rendering to validate both attachment behavior and preserved values; selected packed formats mask unused bits before comparison.

## Registration Hierarchy

```text
image.host_image_copy
├── draw_r8g8b8a8_unorm_r8g8b8a8_unorm
├── draw_r8g8_unorm_r8g8_unorm
├── draw_r32g32b32a32_sfloat_r32g32b32a32_sfloat
├── draw_r8_unorm_r8_unorm
├── draw_r32g32_sfloat_r32g32_sfloat
├── draw_r16_unorm_r16_unorm
├── draw_r16_unorm_d16_unorm
├── draw_r32_sfloat_d32_sfloat
├── draw_r8g8b8a8_unorm_bc7_unorm_block
├── draw_r8g8b8a8_unorm_etc2_r8g8b8a8_unorm_block
├── draw_r8g8b8a8_unorm_astc_4x4_unorm_block
├── dispatch_r10x6_unorm_pack16_r10x6_unorm_pack16
├── dispatch_r8g8b8a8_unorm_r8g8b8a8_unorm
├── dispatch_r8g8b8a8_uint_r8g8b8a8_unorm
├── large_images
├── array
├── linear
├── optimal
├── drm_format_modifier
├── capture_replay
├── properties
├── query
├── identical_memory_layout
├── depth_stencil
└── simple
```

[`createImageHostImageCopyTests()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L5008-L5013) creates the `host_image_copy` group and delegates its contents to [`testGenerator()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4353-L5005). The image category adds it only outside VulkanSC ([guarded parent registration](../../../modules/vulkan/image/vktImageTests.cpp#L49-L51), [child addition](../../../modules/vulkan/image/vktImageTests.cpp#L92-L94)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct family | Main draw/dispatch matrix; `large_images`; `array`; `linear`, `optimal`, `drm_format_modifier`; `capture_replay`; `properties`; `query`; `identical_memory_layout`; `depth_stencil`; `simple` | Selects the assertion and validation mechanism. | [Factory structure](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4353-L5005) |
| Main observer | `draw`, `dispatch` | Samples copied input into an output image through graphics or compute. | [Format/command pairs](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4391-L4411) |
| Main transition/copy route | `host_transition_host_copy`, `host_transition`, `barrier_transition_host_copy`; `memory_to_image`, `image_to_memory`, `memcpy` | Selects host versus barrier layout transition, host operation direction, and memcpy flag. The non-host-copy `host_transition` route does not register `memcpy`. | [Route arrays and skip](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4355-L4380), [skip](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4490-L4494) |
| Main image layouts | Source/destination `general_general`, `transfer_src_transfer_dst`; seven intermediate layouts | Changes the host-copy-eligible and device-observation layouts under test. | [Layout arrays](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4429-L4452) |
| Main tiling and coverage | `linear`, `optimal`; mip/region/padding `0_1_0`, `1_1_0`, `4_1_0`, `0_4_4`, `0_16_64`; sizes `16x16`, `32x28`, `53x61` | Changes copy addressing, mip level, number of regions, padding, and extent. | [Tiling, size, and region arrays](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4382-L4389), [#L4419-L4427](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4419-L4427), [#L4454-L4464](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4454-L4464) |
| Main format/observer pairs | Draw: RGBA8, RG8, RGBA32F, R8, RG32F, R16, D16/R16, D32/R32F, BC7/RGBA8, ETC2/RGBA8, ASTC/RGBA8. Dispatch: R10X6, RGBA8/RGBA8, RGBA8/RGBA8_UINT. | Changes the copied sampled representation and the output representation. | [Format table](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4397-L4410) |
| Large images | Seven input/output pairs, `128²`, `512²`, `4096²`, host memory-to-image or image-to-memory | Isolates larger optimal-tiled host-copy coverage with draw observation. | [Large-image registration](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4598-L4662) |
| Array path | Five formats; linear/optimal; six layer-offset tuples; five offset/extent configurations; remaining-layer and legal cube variants | Changes layer range, source/destination layer offset, dimensional addressing, and cube compatibility. | [Array registration](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4665-L4764) |
| Layout/image-to-image path | Linear, optimal, DRM modifier; image-to-image, memcpy, or preinitialized; 17 layouts; four shapes; offsets `0`, `64`; six formats | Covers host image-to-image operations and preinitialized-memory scenarios across curated layout pairs. | [Registration](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4767-L4889) |
| Query/memory formats | Ten mixed color, depth/stencil, and block-compressed formats; linear/optimal | Drives property/performance and identical-layout checks. | [Query formats and loops](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4903-L4943) |
| Simple path | `formats::nonPlanarFormats`; linear/optimal; `general_general` or `transfer_src_transfer_dst`; fixed 2D/3D shapes | Broad direct round-trip coverage, excluding 3D configurations that require YCbCr conversion. | [Simple registration](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4962-L5005) |

## Behavior Parameters

The primary behavioral axis is the **registered direct family**. It changes the property observed and often the entire oracle, while deeper path components choose coverage variants of that behavior.

### Main draw/dispatch matrix: copied image observed by shaders

The main matrix first establishes the selected source/destination layout route and performs the selected host or queue copy. It then samples the copied image into an output image using either a fullscreen draw or a compute dispatch. It reads that output to host memory and compares expected sampled data. This validates that copied data survives the copy route and is correctly consumed by the chosen shader pipeline.

### `large_images`: main host-copy path at larger extents

These leaves fix host transition, host copy, optimal tiling, one region, no padding, draw observation, and `GENERAL` layouts. They vary selected input/output format pairs, host copy direction, and 128-, 512-, or 4096-pixel square images.

### `array`: layer ranges and host image-to-image copies

This path host-copies generated data into a source image, transitions it for host image-to-image copy, relocates the selected range to a destination image, and copies the destination range to host memory. The layer tuple may use different source and destination base layers; legal cases also test `VK_REMAINING_ARRAY_LAYERS` and cube-compatible images.

### Tiling/image-to-image/preinitialized paths: layout and allocation scenarios

The three top-level tiling paths cover host image-to-image copy, its memcpy-flag form, and preinitialized-image handling. They vary eligible source/destination layouts, extent/layer shape, image memory offset, and format. DRM modifier leaves additionally choose a supported modifier through format-property discovery.

### `capture_replay`: descriptor-heap capture/replay allocation path

This single `heap` leaf uses the preinitialized/image-to-image machinery with descriptor-heap capture/replay image and allocation flags, then verifies copied bytes.

### `properties` and `query`: extension reporting contracts

`properties` reads `VkPhysicalDeviceHostImageCopyPropertiesEXT` and validates layout-list/UUID requirements. `query` chains `VkHostImageCopyDevicePerformanceQueryEXT` into image-format-property queries and checks mandated relationships involving identical layout, optimal device access, compressed formats, and advertised sampled/host-transfer support.

### `identical_memory_layout`: paired allocation layout

These leaves create paired images that differ by `VK_IMAGE_USAGE_HOST_TRANSFER_BIT_EXT`, upload equivalent data, copy their bound image memory to verification buffers, and compare the bytes. The assertion is limited to the advertised identical-memory-layout behavior for this paired configuration.

### `depth_stencil` and `simple`: direct broad-format validation

`depth_stencil` host-copies depth and stencil aspects independently, uses the image as a depth/stencil attachment, copies a color observation to host memory, and checks color, depth, and stencil expectations. `simple` uploads to one image via host copy, uses host image-to-image copy to create a third image, copies all relevant images to host memory, and applies format-specific comparison rules.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.host_image_copy.draw_r8g8b8a8_unorm_r8g8b8a8_unorm.host_transition_host_copy.memory_to_image.general_general.general.optimal.0_1_0.16x16
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `draw_r8g8b8a8_unorm_r8g8b8a8_unorm` | Uses the graphics observer with RGBA8 UNORM output and sampled images. |
| `host_transition_host_copy.memory_to_image` | Transitions on the host and populates the sampled image from host memory with `vkCopyMemoryToImageEXT`. |
| `general_general.general.optimal` | Uses `GENERAL` for the selected source, destination, and intermediate layouts, with optimal tiling for the sampled image. |
| `0_1_0.16x16` | Selects mip level 0, one copy region, no host-memory padding, and a 16-by-16 image. |

#### Purpose

The fragment shader makes the host-populated image observable by sampling it and writing the value to an RGBA8 color attachment. The fixed vertex shader supplies fullscreen coverage and texture coordinates for that observation.

#### Structural Design

| Stage or operation | Interface and action | Role in the check |
|--------------------|----------------------|-------------------|
| Host copy | One unpadded mip-0 region is copied from host memory into the 16-by-16 optimal-tiled sampled image. | Establishes the data whose device-side visibility is tested. |
| Vertex shader | Derives location-0 `texCoord` and `gl_Position` from `gl_VertexIndex`; a four-vertex triangle strip covers the attachment. | Supplies normalized coordinates without a vertex buffer. |
| Fragment shader | Reads set 0, binding 0 as `sampler2D` and writes location 0 as `vec4`. | Samples the host-copy result and exposes it in the output image. |
| Readback | The color-attachment write is made available to transfer, then copied to a host-visible buffer. | Supplies the pixels used by the result comparison. |

#### Shader Code

##### Fragment Shader

```glsl
#version 450
/// Writes the sampled host-copy result to the 16x16 RGBA8 color attachment.
layout (location=0) out vec4 out_color;
/// Receives the fullscreen texture coordinate generated from gl_VertexIndex by the vertex stage.
layout (location=0) in vec2 texCoord;
/// Combined sampler for the mip-0 VK_FORMAT_R8G8B8A8_UNORM image populated by vkCopyMemoryToImageEXT.
layout (set=0, binding=0) uniform sampler2D combinedSampler;
void main()
{
    /// Make the host-populated image observable through the configured nearest-filtered sampling path.
    out_color = texture(combinedSampler, texCoord);
}
```

##### Vertex Shader

```glsl
#version 450
/// Carries a corner coordinate to the fragment shader at location 0.
layout (location=0) out vec2 texCoord;
void main()
{
    /// Decode the four vertex indices into the corners of a fullscreen triangle strip.
    texCoord = vec2(gl_VertexIndex & 1u, (gl_VertexIndex >> 1u) & 1u);    gl_Position = vec4(texCoord * 2.0f - 1.0f, 0.0f, 1.0f);
}
```

#### Additional Info

- The vertex stage stays fixed across the main matrix. It matters here because its four `gl_VertexIndex` values provide both fullscreen triangle-strip positions and the fragment shader's sampling coordinates ([pipeline topology](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L719-L722), [shader generator](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1347-L1360)).
- After drawing, the runtime barriers the color attachment for transfer read, copies the observed pixels to a host-visible buffer, and invalidates that buffer before comparison ([observer and readback](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L965-L1049)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Observer command | `dispatch` replaces the graphics observer with a local-size-one compute shader that reads the sampler and stores through a binding-1 storage image. | [Compute generation](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1379-L1405) |
| Sampled format class | A depth/stencil sampled format changes the fragment expression to replicate only the sampled red component into the output's red channel and write zero to the other components. | [Fragment branch](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1362-L1377) |
| Compute output format | The RGBA8 UINT dispatch pair changes the storage image to `uimage2D` and converts normalized samples to integer values by multiplying by 255; other dispatch pairs use `image2D` and store the sampled `vec4` directly. | [Compute output branch](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1380-L1403) |
| Copy route, layouts, tiling, mip/regions/padding, and extent | These dimensions change host/runtime setup and the data presented to the observer, but do not specialize the generated vertex or fragment source. | [Registration parameters](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4353-L4464), [case construction](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4561-L4581) |

#### SPIR-V

##### Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 20
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %out_color %texCoord
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %out_color "out_color"
               OpName %combinedSampler "combinedSampler"
               OpName %texCoord "texCoord"
               OpDecorate %out_color Location 0
               OpDecorate %combinedSampler Binding 0
               OpDecorate %combinedSampler DescriptorSet 0
               OpDecorate %texCoord Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %11 = OpTypeSampledImage %10
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
%combinedSampler = OpVariable %_ptr_UniformConstant_11 UniformConstant
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
   %texCoord = OpVariable %_ptr_Input_v2float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpLoad %11 %combinedSampler
         %18 = OpLoad %v2float %texCoord
         %19 = OpImageSampleImplicitLod %v4float %14 %18
               OpStore %out_color %19
               OpReturn
               OpFunctionEnd
```

</details>

##### Vertex Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 43
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %texCoord %gl_VertexIndex %_
               OpSource GLSL 450
               OpName %main "main"
               OpName %texCoord "texCoord"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpDecorate %texCoord Location 0
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Output_v2float = OpTypePointer Output %v2float
   %texCoord = OpVariable %_ptr_Output_v2float Output
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
    %v4float = OpTypeVector %float 4
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
    %float_2 = OpConstant %float 2
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %int %gl_VertexIndex
         %15 = OpBitcast %uint %13
         %17 = OpBitwiseAnd %uint %15 %uint_1
         %18 = OpConvertUToF %float %17
         %19 = OpLoad %int %gl_VertexIndex
         %20 = OpShiftRightArithmetic %int %19 %uint_1
         %21 = OpBitcast %uint %20
         %22 = OpBitwiseAnd %uint %21 %uint_1
         %23 = OpConvertUToF %float %22
         %24 = OpCompositeConstruct %v2float %18 %23
               OpStore %texCoord %24
         %31 = OpLoad %v2float %texCoord
         %33 = OpVectorTimesScalar %v2float %31 %float_2
         %35 = OpCompositeConstruct %v2float %float_1 %float_1
         %36 = OpFSub %v2float %33 %35
         %38 = OpCompositeExtract %float %36 0
         %39 = OpCompositeExtract %float %36 1
         %40 = OpCompositeConstruct %v4float %38 %39 %float_0 %float_1
         %42 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %42 %40
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Main matrix

[`HostImageCopyTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L391-L1201) performs the following sequence.

1. It derives the selected mip extent, creates generated input bytes, creates sampled/output images and views, and configures image usage from the action and intermediate layout. Sparse variants allocate and bind sparse images; ordinary variants use `ImageWithMemory` ([setup](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L410-L524)).
2. For a host transition, it calls `vkTransitionImageLayoutEXT`. For a host memory-to-image route, it creates one or more `VkMemoryToImageCopyEXT` regions and calls `vkCopyMemoryToImageEXT`; for the comparison route it records `vkCmdCopyBufferToImage`. The memcpy path copies through the selected host-memory flag and a second image ([copy routing](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L767-L947)).
3. It transitions/configures the output image, records the selected draw or compute observer, and barriers the output image for transfer read. It copies output pixels into a host-visible buffer, waits for queue completion, and invalidates the allocation ([observer and readback](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L952-L1049)).
4. For image-to-memory action leaves it calls `vkCopyImageToMemoryEXT`; otherwise it uses the observer-buffer data. It compares transformed expected values or bytes, accommodating selected packed-format bit behavior, and fails on mismatch ([comparison](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1063-L1201)).

### Targeted paths

- **Preinitialized/image-to-image:** Generates host allocation data, performs selected host transitions and optional host image-to-image copy, then either copies image data to host with the extension or queue-copies it to a buffer for verification. It compares all bytes ([runtime](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1488-L1739)).
- **Properties/query:** `properties` obtains property-list storage in two calls and validates required entries/UUID. `query` reads performance-query fields from image-format-property queries and checks its specified relationships ([properties/query runtime](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1924-L2180)).
- **Identical layout:** Paired images are populated with equivalent data, their bound memory is copied to buffers, and every byte is compared ([runtime](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2414-L2584)).
- **Depth/stencil:** The host copies separate depth/stencil aspects, renders against the image, then verifies the read-back color buffer plus expected depth/stencil values with depth-format-aware tolerance ([runtime and checks](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2801-L3210)).
- **Array/simple:** Array leaves perform host memory-to-image, host image-to-image, and host image-to-memory operations across selected subresource layers. Simple leaves compare host upload and host image-to-image results for the selected nonplanar format, with separate depth/stencil and packed-format handling ([array](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L3246-L3434), [simple](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L3927-L4220)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Main draw/dispatch matrix | Host transition, selected host-copy direction/flag, region/mip addressing, allowed-layout processing, copy visibility, or shader sampling/storage observation. |
| `large_images` | A main-matrix host-copy defect that appears at the registered larger extent, including allocation or region-size handling. |
| `array` | Incorrect layer range, source/destination layer offset, remaining-array-layer, cube-compatible, or layer-copy addressing behavior. |
| Tiling/image-to-image/preinitialized | Incorrect selected layout, DRM modifier path, image allocation offset, host image-to-image operation, or byte preservation. |
| `capture_replay` | Descriptor-heap capture/replay image allocation or its host image-to-image path is incorrect. |
| `properties` / `query` | Inconsistent returned host-copy layout lists, UUID, feature support, or performance-query relationships. |
| `identical_memory_layout` | Paired images with and without host-transfer use do not meet the reported identical-memory-layout behavior. |
| `depth_stencil` / `simple` | Incorrect aspect selection, special-format representation, direct host copy, image-to-image copy, or value comparison. |

### Cause Analysis

#### Host-copy eligibility and addressing

**Possible failure symptoms:** Cases skip unexpectedly, or failures cluster by tiling, source/destination layout, mip level, regions, padding, or array layer configuration.

**Possible implementation causes:** The case checks returned layout lists and tiling-specific `HOST_IMAGE_TRANSFER` format support before execution. A fault in reported support, layout transition, or interpretation of the selected subresource, extent, host strides, mip, padding, or layers can prevent a valid route or copy data to the wrong location. The source’s final mismatch status does not isolate the individual region that introduced an incorrect value.

#### Graphics/compute observation versus the direct copy

**Possible failure symptoms:** Main draw/dispatch leaves fail while direct simple or array round trips pass, or failures divide by draw versus dispatch.

**Possible implementation causes:** The main path includes descriptor/view setup, sampling, output attachment/storage-image writes, barriers, and output readback after the host operation. A failure can lie in that observer path rather than in the host copy alone. Conversely, a shared failure across observer and direct-copy paths strengthens the evidence for a transition/copy or format-representation problem.

#### Properties and memory-layout claims

**Possible failure symptoms:** `properties`, `query`, or `identical_memory_layout` fails without a data-round-trip mismatch.

**Possible implementation causes:** These leaves directly test consistency of driver-reported structures or paired allocation bytes. They do not execute the main shader observation matrix, so their failure points to an extension-reporting or allocation-layout contract rather than a fragment/compute output mismatch.

## Case Pruning

### Requirement-based pruning

- Operational paths require `VK_EXT_host_image_copy`; the main, preinitialized/image-to-image, array, and simple support methods also query `VkPhysicalDeviceHostImageCopyFeaturesEXT` and skip when `hostImageCopy` is not true. The main matrix additionally requires the selected source/destination/intermediate layouts, matching image-format properties, mip capacity, and tiling-specific host-image-transfer format support ([main support](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1224-L1345)).
- Main leaves additionally require `VK_KHR_dynamic_rendering` only for their selected dynamic-rendering configuration and sparse binding only for sparse variants ([main support](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1231-L1237)).
- Preinitialized/image-to-image leaves require extensions selected by their configuration: DRM format modifier, swapchain for present layouts, maintenance2 or separate-depth-stencil-layouts, synchronization2, attachment-feedback-loop layout, and descriptor heap for capture/replay. They also require a supported DRM modifier when applicable, selected layout-list membership, image-format support, and array-layer capacity ([support](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1783-L1910)).
- Dedicated `depth_stencil` leaves require host transfer, transfer source/destination, and depth/stencil attachment format features for the selected optimal-tiled format ([support](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2753-L2787)). Depth/stencil formats in `identical_memory_layout` are skipped on compute-only configurations because that path uses graphics-capable queue commands to populate them ([queue gate](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2495-L2513)).
- The entire group is absent in VulkanSC because the parent image dispatcher conditionally includes its header and child only outside `CTS_USES_VULKANSC` ([parent guard](../../../modules/vulkan/image/vktImageTests.cpp#L49-L51), [#L92-L94](../../../modules/vulkan/image/vktImageTests.cpp#L92-L94)).

### Design-based pruning

- Main-matrix registration excludes the `memcpy` action when its transition/copy mode selects a queue copy, because that combination duplicates the non-memcpy memory-to-image route ([registration skip](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4490-L4494)).
- It excludes depth/stencil intermediate layouts for color formats and color-attachment intermediate layout for non-color formats. Sparse compressed-input variants are not registered ([layout and sparse pruning](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4500-L4532)).
- Later-added restricted formats retain only selected layout/intermediate/mip/region combinations. Dynamic rendering and sparse selection are alternated rather than forming an exhaustive cross product ([restriction logic](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4515-L4569)).
- Array leaves exclude remaining-layer copies with depth greater than one and cube-compatible variants unless the total layer count is six and the selected extent is square ([array pruning](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4724-L4736)).
- Layout/image-to-image leaves do not form every differing source/destination layout pair: they retain equal pairs and pairs where at least one layout is `GENERAL`, `TRANSFER_SRC_OPTIMAL`, or `TRANSFER_DST_OPTIMAL` ([curated pairs](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4851-L4863)).
- `simple` iterates nonplanar formats but excludes 3D cases for formats requiring YCbCr conversion ([simple pruning](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4974-L4988)).

## Key Takeaways

- `image.host_image_copy` is a multi-oracle test family: it checks operational host copies, device-observed host-copy results, extension property/reporting contracts, paired memory-layout behavior, and format/aspect special cases.
- The main draw/dispatch matrix does not test only a copy call; it observes copied image data through a graphics or compute consumer and verifies the resulting output.
- Array, preinitialized/image-to-image, simple, and depth/stencil paths directly exercise combinations that the main observer matrix does not represent.
- A supported configuration requires more than the extension name: the source checks the feature bit, selected source/destination layouts, image and format support, and configuration-specific extensions.
- The family is registered only outside VulkanSC.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Helpers and main parameters | [`generateData()`, feature helper, and parameter model](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L118-L297) | Defines test bytes, format-feature support, and main-matrix configuration. |
| Main runtime | [`HostImageCopyTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L391-L1201) | Executes the main host/queue routes, observer, and comparison. |
| Main support and shaders | [`HostImageCopyTestCase`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1204-L1407) | Checks feature/layout support and generates shaders. |
| Preinitialized/image-to-image runtime | [`PreinitializedTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1488-L1739) | Covers allocation data, host image-to-image copies, memcpy, and readback. |
| Preinitialized support | [`PreinitializedTestCase::checkSupport()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1783-L1910) | Defines configuration-dependent extension, layout, format, and layer gates. |
| Properties and query | [`PropertiesTestInstance` and `QueryTestInstance`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L1924-L2180) | Validates returned extension properties and performance-query relationships. |
| Identical memory layout | [`IdenticalMemoryLayoutTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2414-L2584) | Compares paired allocation byte layouts. |
| Depth/stencil | [`DepthStencilHostImageCopyInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L2860-L3210) | Defines aspect-specific copies, rendering, and expected-value checks. |
| Array | [`HostImageArrayCopyTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L3246-L3434) | Defines layered host memory/image/image copy flow. |
| Simple | [`SimpleHostImageCopyTestInstance::iterate()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L3927-L4220) | Defines broad direct round-trip and special-format validation. |
| Registration | [`testGenerator()`](../../../modules/vulkan/image/vktImageHostImageCopyTests.cpp#L4353-L5005) | Defines hierarchy, axes, and design pruning. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L49-L100) | Places the family in `image` and shows the VulkanSC guard. |
