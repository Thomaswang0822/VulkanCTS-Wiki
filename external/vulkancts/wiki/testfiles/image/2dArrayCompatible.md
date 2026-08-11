## Overview

**Core question:** Can a 3D image created with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` preserve a copied depth slice when that slice is sampled through the selected legal image-view interpretation?

- [`vktImage2dArrayCompatibleTests.cpp`](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L44-L524) implements the `image.2d_array_compatible` family. It creates a 3D `VK_FORMAT_R8G8B8A8_UNORM` image with the maintenance9 2D-array-compatible create flag.
- Each case uploads random non-NaN RGBA8 data to one depth slice, copies that slice to another depth slice of the same image, samples the destination through either a 3D view or, outside Vulkan SC, a 2D view, and makes both the copied texels and sampled values observable to the host.
- The three layer configurations place the source and destination slices at the beginning, middle, and near the end of images with different depths. Linear and optimal tiling are both registered.
- This page describes the registered matrix, the two view interpretations, command sequence, and the two result comparisons.

## Background Knowledge

For the shared concepts image views, subresources, copies, layouts, and synchronization, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **A 3D image uses its depth coordinate to address slices.** A transfer region can select a single depth slice with a depth-one extent and a nonzero `imageOffset.z`. A 3D sampled view instead receives a normalized third texture coordinate.
- **An image view controls shader interpretation of the underlying image.** The 3D path binds a `sampler3D` view of the image; the non-Vulkan-SC 2D path binds a `sampler2D` view whose subresource range selects the destination slice. The view type therefore changes the shader coordinate shape without changing the stored destination data.
- **Layout transitions and barriers have separate purposes.** The transfer-to-shader barrier here changes the destination slice to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` and makes the copy write available to the compute shader. The later shader-to-transfer barrier makes that slice available for copyback.

## Registration Hierarchy

```text
image.2d_array_compatible
├── 0_1_8
├── 3_7_16
└── 3_4_5
```

[`createImage2dArrayCompatibleTests()`](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L464-L524) registers the three layer-configuration groups. Each contains `linear` and `optimal`, and each tiling contains `3d`; non-Vulkan-SC builds also register `2d`. [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) adds this family to `image`.

The Vulkan default mustpass inventory contains all twelve leaves, while the Vulkan SC inventory contains the six `3d` leaves: [`vk-default`](../../../mustpass/main/vk-default/image/2d-array-compatible.txt) and [`vksc-default`](../../../mustpass/main/vksc-default/image/2d-array-compatible.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Layer configuration group | `0_1_8`, `3_7_16`, `3_4_5` | Selects the source slice, destination slice, and 3D image depth. The corresponding triples are `(first, second, total) = (0, 1, 8)`, `(3, 7, 16)`, and `(3, 4, 5)`. | [Layer matrix and registration](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L468-L520) |
| Tiling | `linear`, `optimal` | Selects `VK_IMAGE_TILING_LINEAR` or `VK_IMAGE_TILING_OPTIMAL` for the otherwise fixed image configuration. | [Tiling matrix](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L480-L487) |
| Image-view leaf | `2d`, `3d` | Selects the shader-visible view. `2d` is omitted under `CTS_USES_VULKANSC`; `3d` is registered in both build forms. | [View-type matrix](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L489-L498) |
| Image configuration | `VK_IMAGE_TYPE_3D`, `VK_FORMAT_R8G8B8A8_UNORM`, 32 x 32 x `totalLayers`, one mip, one sample | Keeps format, width, height, mip count, and samples fixed so the cases isolate depth-slice and view compatibility. | [Image create info](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L121-L152) |
| Image create flags | `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT`; additionally `VK_IMAGE_CREATE_2D_VIEW_COMPATIBLE_BIT_EXT` for `2d` outside Vulkan SC | Requests maintenance9 2D-array compatibility for every image and the extension-specific 2D-view compatibility needed by the `2d` path. | [Create-flag selection](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L126-L130) |
| Image usage | `TRANSFER_SRC`, `TRANSFER_DST`, `SAMPLED` | Supports upload, intra-image copy, destination readback, and sampled observation. | [Usage flags](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L132-L149) |

## Behavior Parameters

The primary behavioral axis is the **image-view leaf**. Both leaves perform the same upload, slice-to-slice copy, and host comparisons; they differ in the image view and coordinate type used to observe the copied destination slice. The layer configuration and tiling axes place that behavior in distinct slice positions and image layouts.

### `2d`: sample the selected depth slice as a 2D view

Outside Vulkan SC, this leaf adds `VK_IMAGE_CREATE_2D_VIEW_COMPATIBLE_BIT_EXT` and creates a `VK_IMAGE_VIEW_TYPE_2D` view over the destination slice only. The compute shader uses `sampler2D` and normalized `(x, y)` coordinates, so the selected view range, rather than a shader depth coordinate, identifies the copied slice. The case requires `VK_EXT_image_2d_view_of_3d` and its `sampler2DViewOf3D` feature.

### `3d`: sample the destination through the 3D view

This leaf creates a `VK_IMAGE_VIEW_TYPE_3D` view beginning at the image's only array layer. The compute shader uses `sampler3D` and supplies the destination slice as normalized `z = secondLayer / totalLayers`. It is available in both Vulkan and Vulkan SC builds and transitions all depth slices for the 3D view before making the sampled destination slice shader-readable.

## Shader Analysis

[`ArrayCompatibleTestCase::initPrograms()`](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L431-L460) generates one compute shader per view-type leaf. The following reconstructed `3d` shader is for `dEQP-VK.image.2d_array_compatible.0_1_8.linear.3d`; its `z` coordinate selects destination slice 1 of the eight-slice image. The GLSL and SPIR-V were generated and validated with `glslangValidator --target-env vulkan1.0` and `spirv-dis`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.2d_array_compatible.0_1_8.linear.3d
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `0_1_8` | The host uploads slice 0, copies it to slice 1, and creates an eight-slice 3D image. |
| `linear` | The image uses `VK_IMAGE_TILING_LINEAR`. |
| `3d` | Binding 0 is a 3D sampled view, and the shader selects slice 1 with normalized `z = 1 / 8`. |

#### Purpose

Each invocation samples one texel of the copied destination slice and stores the returned RGBA value in a storage buffer. This creates a second observation path in addition to the destination-slice copyback.

#### Structural Design

| Shader element | Action | Test significance |
|----------------|--------|-------------------|
| `gl_GlobalInvocationID.xy` | Names one of the 32 x 32 texels dispatched by the host. | Makes one sampled result available for every copied texel. |
| `inputImage` | Samples the bound 3D view at normalized `x`, `y`, and the fixed destination-slice `z`. | Tests 3D-view access to the copied depth slice. |
| `data.color` | Stores the sampled `vec4` at row-major index `y * 32 + x`. | Lets the host compare the sampled result with the uploaded byte data. |

#### Shader Code

```glsl
#version 450

/// The host dispatches one invocation for every texel in the 32 x 32 destination slice.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the `VK_IMAGE_VIEW_TYPE_3D` sampled view of the image.
layout (set = 0, binding = 0) uniform sampler3D inputImage;
/// Binding 1 receives one sampled RGBA value for every invocation.
layout (set = 0, binding = 1) buffer outputBuffer {
    vec4 color[];
} data;

void main() {
    /// The selected destination slice is 1 of the 8 depth slices in this representative leaf.
    vec3 pixelCoords = vec3(gl_GlobalInvocationID.xy / vec2(32.0f, 32.0f), 1.0f / 8.0f);
    uint index = gl_GlobalInvocationID.y * 32 + gl_GlobalInvocationID.x;
    data.color[index] = texture(inputImage, pixelCoords);
}
```

#### Additional Info

- The source emits the same structure, without the wiki-authored `///` comments. For the `3d` leaf it declares `sampler3D` and substitutes `secondLayer / totalLayers` in the third coordinate; [the generator](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L433-L459) supplies those values.
- The `2d` leaf instead declares `sampler2D`, constructs only normalized `(x, y)` coordinates, and relies on its single-slice 2D view range to select the destination slice.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this representative shader | Evidence |
|---------------------|----------------------------------------------------------|----------|
| Image-view leaf | `2d` changes `sampler3D` to `sampler2D` and removes the third coordinate. `3d` retains the 3D declaration and uses `secondLayer / totalLayers`. | [View-dependent generated GLSL](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L437-L456) |
| Layer configuration | The `3d` leaf changes only the generated third coordinate: `1 / 8`, `7 / 16`, or `4 / 5`. | [Layer parameters](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L468-L478), [coordinate construction](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L446-L450) |
| Tiling | No GLSL text changes; tiling changes image creation and the deterministic random-data seed. | [Image create info](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L132-L149), [data generation](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L188-L190) |

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
; Bound: 57
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %pixelCoords "pixelCoords"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %index "index"
               OpName %outputBuffer "outputBuffer"
               OpMemberName %outputBuffer 0 "color"
               OpName %data "data"
               OpName %inputImage "inputImage"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_v4float ArrayStride 16
               OpDecorate %outputBuffer BufferBlock
               OpMemberDecorate %outputBuffer 0 Offset 0
               OpDecorate %data Binding 1
               OpDecorate %data DescriptorSet 0
               OpDecorate %inputImage Binding 0
               OpDecorate %inputImage DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
    %v2float = OpTypeVector %float 2
   %float_32 = OpConstant %float 32
         %20 = OpConstantComposite %v2float %float_32 %float_32
%float_0_125 = OpConstant %float 0.125
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_1 = OpConstant %uint 1
%_ptr_Input_uint = OpTypePointer Input %uint
    %uint_32 = OpConstant %uint 32
     %uint_0 = OpConstant %uint 0
    %v4float = OpTypeVector %float 4
%_runtimearr_v4float = OpTypeRuntimeArray %v4float
%outputBuffer = OpTypeStruct %_runtimearr_v4float
%_ptr_Uniform_outputBuffer = OpTypePointer Uniform %outputBuffer
       %data = OpVariable %_ptr_Uniform_outputBuffer Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
         %46 = OpTypeImage %float 3D 0 0 0 1 Unknown
         %47 = OpTypeSampledImage %46
%_ptr_UniformConstant_47 = OpTypePointer UniformConstant %47
 %inputImage = OpVariable %_ptr_UniformConstant_47 UniformConstant
    %float_0 = OpConstant %float 0
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%pixelCoords = OpVariable %_ptr_Function_v3float Function
      %index = OpVariable %_ptr_Function_uint Function
         %15 = OpLoad %v3uint %gl_GlobalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %18 = OpConvertUToF %v2float %16
         %21 = OpFDiv %v2float %18 %20
         %23 = OpCompositeExtract %float %21 0
         %24 = OpCompositeExtract %float %21 1
         %25 = OpCompositeConstruct %v3float %23 %24 %float_0_125
               OpStore %pixelCoords %25
         %30 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %31 = OpLoad %uint %30
         %33 = OpIMul %uint %31 %uint_32
         %35 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %36 = OpLoad %uint %35
         %37 = OpIAdd %uint %33 %36
               OpStore %index %37
         %45 = OpLoad %uint %index
         %50 = OpLoad %47 %inputImage
         %51 = OpLoad %v3float %pixelCoords
         %53 = OpImageSampleExplicitLod %v4float %50 %51 Lod %float_0
         %55 = OpAccessChain %_ptr_Uniform_v4float %data %int_0 %45
               OpStore %55 %53
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test allocates host-visible source and destination buffers of one 32 x 32 RGBA8 slice and a host-visible storage buffer for 1,024 `vec4` shader results. It fills the source buffer with random non-NaN values, using a tiling-derived seed, and flushes the upload allocation. [Buffer setup and initialization](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L174-L195)
- It creates the selected sampled image view, a nearest-filter sampler, and a compute descriptor set containing that combined image sampler and the storage buffer. [View, descriptors, and pipeline](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L154-L262)
- The command buffer transitions the source slice to transfer-destination layout, copies the source buffer to `firstLayer`, transitions that source and the initially undefined `secondLayer` for transfer, then uses `vkCmdCopyImage` to copy one 32 x 32 x 1 region from the first slice to the second. The helper transitions every unused slice separately so the full 3D image can be used by the 3D-view path. [Upload and image copy](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L264-L302)
- For `3d`, all slices first transition to shader-read-only layout; for both leaves, the destination slice receives a transfer-write-to-shader-read barrier and transition to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`. The test dispatches 32 by 32 by 1 compute workgroups. [Shader-read transition and dispatch](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L303-L321)
- It transitions the destination slice from shader-read-only to transfer-source layout, copies that slice to the destination buffer, and records a host-read barrier for that copyback buffer. After queue completion, it performs two comparisons. [Copyback and host barrier](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L322-L354)
- First, `memcmp` requires the copied destination-buffer bytes to equal the original source-buffer bytes exactly. On a mismatch, the source logs each different byte and reference/result images, then returns `fail`. Second, the test multiplies each float component from the storage buffer by 256 and requires it to be within `1.0` of the matching source byte. If all checks succeed, the case returns `pass`. [Result checks](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L355-L384)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | 2D-view creation or selected-slice mapping for the compatible 3D image, `sampler2D` read behavior, copy/transition sequencing, or either host comparison. |
| `3d` | 3D-view depth-coordinate mapping, full-image layout preparation, copy/transition sequencing, `sampler3D` read behavior, or either host comparison. |

Both leaves also vary the registered source/destination/depth triple and tiling. A failure isolated to one of those values can additionally indicate the corresponding slice placement or format-and-tiling support path.

### Cause Analysis

#### Compatible-view interpretation, copy, or sampled observation

**Possible failure symptoms:** The byte comparison reports a source/destination mismatch, the sampled-value comparison returns `fail`, or both do. A `2d`-only failure distinguishes the selected 2D-view path from the shared transfer path. A `3d`-only failure distinguishes the 3D view, its normalized depth coordinate, or the all-slice layout preparation. A failure in both leaves can arise before view-specific sampling, but the two host checks do not by themselves locate the first incorrect operation.

**Possible implementation causes:** The source gives the source and destination slices distinct roles: it uploads to `firstLayer`, copies to `secondLayer`, then observes `secondLayer` by image copyback and shader sampling. Incorrect depth-slice addressing in `vkCmdCopyBufferToImage` or `vkCmdCopyImage`, incorrect 2D-view subresource selection, incorrect 3D-view/depth-coordinate interpretation, or missing transfer-to-shader or shader-to-transfer visibility can therefore change an observed value. A `2d` case additionally depends on the extension feature and the extension create flag; a `3d` case depends on the view being valid after all image slices are prepared for the 3D sampled view. The source comparison establishes the symptom; identifying a particular implementation stage requires the recorded validation output and implementation investigation.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_KHR_maintenance9`. Before executing, the source queries format properties for the fixed RGBA8 3D image, selected tiling, transfer-and-sampled usage, and `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT`; unsupported combinations throw `NotSupportedError`. [Support check](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L407-L420)
- Outside Vulkan SC, the `2d` leaf also requires `VK_EXT_image_2d_view_of_3d` and `sampler2DViewOf3D`. [2D-view support check](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L421-L428)
- Under `CTS_USES_VULKANSC`, the factory does not register `2d`; the default Vulkan SC mustpass list consequently contains only `3d` leaves. [Conditional registration](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L489-L498), [Vulkan SC inventory](../../../mustpass/main/vksc-default/image/2d-array-compatible.txt)

### Design-based pruning

- The factory fixes the format, 32 x 32 dimensions, one mip level, one sample, usage flags, and one-slice copy extent. It tests compatible depth-slice access rather than filtering, format conversion, mipmapping, multisampling, or multi-slice copies. [Fixed image and copy configuration](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L121-L149), [copy regions](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L273-L300)
- The three layer triples deliberately cover a source at layer 0, a source and destination in the middle of a deeper image, and adjacent high-numbered slices in a shallow five-slice image. The matrix does not enumerate every legal pair because each leaf uses the same observation and comparison mechanism. [Registered layer triples](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L468-L478)

## Key Takeaways

- Each leaf proves the same data survives an upload to one 3D depth slice, an intra-image copy to a second slice, and two independent observations of that destination: exact transfer copyback and shader sampling.
- `2d` and `3d` isolate two compatible ways to sample the destination slice. The former uses a single-slice 2D view when the extension feature is available; the latter supplies the slice as a normalized 3D texture coordinate.
- The layer triples exercise slice selection away from a single trivial position, while linear and optimal tiling exercise the fixed image contract through both registered tiling forms.
- A failure is an observed data mismatch; the two comparisons and the differing view leaves narrow the affected path but do not alone assign a defect to a specific implementation stage.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters and layer helpers | [Definitions and transitions](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L44-L110) | Defines the source/destination/depth parameters and the per-slice layout-transition helpers. |
| Image, view, resource, and command setup | [`ArrayCompatibleTestInstance::iterate()`](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L112-L385) | Creates the compatible 3D image, performs transfers and dispatch, and decides pass or fail. |
| Support checks | [`ArrayCompatibleTestCase::checkSupport()`](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L407-L429) | Requires maintenance9, verifies the requested image format configuration, and gates the 2D view path. |
| Generated compute shader | [`ArrayCompatibleTestCase::initPrograms()`](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L431-L460) | Selects the `sampler2D` or `sampler3D` shader declaration and coordinate construction. |
| Case registration | [`createImage2dArrayCompatibleTests()`](../../../modules/vulkan/image/vktImage2dArrayCompatibleTests.cpp#L464-L524) | Registers the exact layer, tiling, and view-type matrix. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) | Places `2d_array_compatible` in the `image` category. |
| Mustpass inventories | [`vk-default`](../../../mustpass/main/vk-default/image/2d-array-compatible.txt) and [`vksc-default`](../../../mustpass/main/vksc-default/image/2d-array-compatible.txt) | Confirm the default Vulkan and Vulkan SC leaf sets. |
