## Overview

**Core question:** Does a cube image view read the six intended array layers when its `baseArrayLayer` is nonzero and not aligned to a six-layer cube boundary?

- [`vktImageMisalignedCubeTests.cpp`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L59-L406) implements the `image.misaligned_cube` test family in the `image` test category.
- Each test creates one cube-compatible 2D image, then creates two six-layer `VK_IMAGE_VIEW_TYPE_CUBE` views of that image. The first view begins at layer 0. The second begins at `numLayers - 6`, which is 1 through 5 for the registered cases.
- The host writes a distinct grayscale value into every image layer. A one-invocation compute shader reads all six face indices from both cube views into a host-visible storage buffer.
- The host compares all twelve returned colors against the layer values expected for the two view ranges. The page covers the resource mapping, shader reads, and exact comparison that make a nonzero base layer observable.

## Background Knowledge

For the shared concepts image views and subresources, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Cube-compatible image views.** `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` permits cube and cube-array image views of an image. A cube view exposes six consecutive array layers as its faces. `baseArrayLayer` selects the first accessible layer, and the face order from that layer is +X, -X, +Y, -Y, +Z, -Z. [The image-view rules](../../../../vulkan-docs/src/chapters/resources.adoc#L4156-L4158) and [cube-face mapping](../../../../vulkan-docs/src/chapters/resources.adoc#L6885-L6912) define those relationships.
- **Storage images and `imageLoad`.** A compute shader can bind a typed storage image and fetch a texel with `imageLoad`. For `imageCube`, the third integer coordinate selects one of the view's six faces. The shader in this family uses that coordinate only to identify a face; it does not sample a direction or filter texels.

## Registration Hierarchy

```text
image.misaligned_cube
├── 7
├── 8
├── 9
├── 10
└── 11
```

[`createMisalignedCubeTests()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L405) registers these five test case leaves. [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L99) adds `misaligned_cube` to the `image` test category. The Vulkan and Vulkan SC default mustpass inventories each contain the same five leaves: [`vk-default`](../../../mustpass/main/vk-default/image/misaligned-cube.txt) and [`vksc-default`](../../../mustpass/main/vksc-default/image/misaligned-cube.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf / image layer count | `7`, `8`, `9`, `10`, `11` | Selects the image's array-layer count and therefore the second view's base layer: 1, 2, 3, 4, or 5. | [Size array and registration](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L384-L405) |
| Image shape | 16 x 16 2D faces, one mip, one sample | Fixes the face extent while the test changes only layer placement. | [`makeImageCreateInfo()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L59-L81) |
| Image format | `VK_FORMAT_R8G8B8A8_UNORM` | Provides the `rgba8` storage-image qualifier and quantized per-layer grayscale values. | [Fixed format and assertion](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L146-L163), [factory](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L402) |
| Cube view | View 0: base layer 0, six layers; view 1: base layer `numLayers - 6`, six layers | Binds an aligned reference view and a nonzero-base view of the same image. Their ranges may overlap. | [View ranges and creation](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L156-L180) |
| Layer data | `vec4(16 * layer / 255, 16 * layer / 255, 16 * layer / 255, 1)` | Encodes each physical array layer with a value that identifies it during readback. | [Initialization loop](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L245-L260) |

## Behavior Parameters

The primary behavioral axis is the **test case leaf / image layer count**. It changes the nonzero `baseArrayLayer` of the second cube view while preserving the same six-face load-and-compare procedure.

### `7`: Second cube starts at layer 1

The second view covers physical layers 1 through 6. Its base layer is displaced by one from layer 0, so every face read must map through the nonzero view base.

### `8`: Second cube starts at layer 2

The second view covers layers 2 through 7. This moves the same six-face interpretation two layers into the image.

### `9`: Second cube starts at layer 3

The second view covers layers 3 through 8. The two cube views overlap in three physical layers, which allows the test to compare distinct view-relative face indices that refer to shared storage.

### `10`: Second cube starts at layer 4

The second view covers layers 4 through 9. It still has six valid layers although its base is not a multiple of six.

### `11`: Second cube starts at layer 5

The second view covers layers 5 through 10. This is the greatest nonzero base layer in the registered matrix.

## Shader Analysis

[`MisalignedCubeTest::initPrograms()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L332-L377) generates one fixed compute-shader structure for every registered leaf. The `7` case is representative because it uses the first nonzero base layer. The layer count changes the second bound view, not the shader text.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.misaligned_cube.7
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `7` | Creates seven array layers, so the second cube view starts at physical layer 1. |
| View 0 | Binds layers 0 through 5 as `u_cubeImage0`. |
| View 1 | Binds layers 1 through 6 as `u_cubeImage1`. |
| `rgba8` | Matches the fixed `VK_FORMAT_R8G8B8A8_UNORM` image and supplies floating-point `vec4` load results. |

#### Purpose

The shader loads texel `(1, 1)` from face indices 0 through 5 of each cube view. It writes the twelve results to an SSBO, so the host can determine the physical layer selected by each view-relative face index.

#### Structural Design

| Shader element | Action | Tested property |
|----------------|--------|-----------------|
| `u_cubeImage0` | Reads six face indices from the view that begins at physical layer 0. | Establishes the aligned reference mapping. |
| `u_cubeImage1` | Reads the same six face indices from the view that begins at physical layer 1. | Exercises nonzero, non-six-aligned `baseArrayLayer` mapping. |
| `sb_out` | Stores the twelve loaded `vec4` values in fixed member order. | Makes every face mapping visible to host comparison. |

#### Shader Code

```glsl
#version 440

/// The test runs one compute invocation because every requested coordinate is fixed.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the cube view over physical layers 0 through 5.
layout (binding = 0, rgba8) readonly uniform highp imageCube u_cubeImage0;
/// Binding 1 is the cube view over physical layers 1 through 6 in the selected `7` case.
layout (binding = 1, rgba8) readonly uniform highp imageCube u_cubeImage1;
/// Binding 2 holds one result for every face of both views.
layout (binding = 2) writeonly buffer Output
{
    vec4 cube0_color0;
    vec4 cube0_color1;
    vec4 cube0_color2;
    vec4 cube0_color3;
    vec4 cube0_color4;
    vec4 cube0_color5;
    vec4 cube1_color0;
    vec4 cube1_color1;
    vec4 cube1_color2;
    vec4 cube1_color3;
    vec4 cube1_color4;
    vec4 cube1_color5;
} sb_out;

void main (void)
{
    /// The third coordinate selects a face index relative to each cube view.
    sb_out.cube0_color0 = imageLoad(u_cubeImage0, ivec3(1, 1, 0));
    sb_out.cube0_color1 = imageLoad(u_cubeImage0, ivec3(1, 1, 1));
    sb_out.cube0_color2 = imageLoad(u_cubeImage0, ivec3(1, 1, 2));
    sb_out.cube0_color3 = imageLoad(u_cubeImage0, ivec3(1, 1, 3));
    sb_out.cube0_color4 = imageLoad(u_cubeImage0, ivec3(1, 1, 4));
    sb_out.cube0_color5 = imageLoad(u_cubeImage0, ivec3(1, 1, 5));
    sb_out.cube1_color0 = imageLoad(u_cubeImage1, ivec3(1, 1, 0));
    sb_out.cube1_color1 = imageLoad(u_cubeImage1, ivec3(1, 1, 1));
    sb_out.cube1_color2 = imageLoad(u_cubeImage1, ivec3(1, 1, 2));
    sb_out.cube1_color3 = imageLoad(u_cubeImage1, ivec3(1, 1, 3));
    sb_out.cube1_color4 = imageLoad(u_cubeImage1, ivec3(1, 1, 4));
    sb_out.cube1_color5 = imageLoad(u_cubeImage1, ivec3(1, 1, 5));
}
```

#### Additional Info

- The shader text uses the format qualifier returned for the fixed `VK_FORMAT_R8G8B8A8_UNORM` format. It binds both views as readonly storage images and the output as a writeonly storage buffer.
- The generator adds this source without explicit shader build options. The reconstructed shader therefore uses the CTS baseline SPIR-V target, `spirv1.0`.
- The `8` through `11` leaves retain this shader. They change only the host-created layer count and the subresource range bound at binding 1.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Test case leaf / image layer count | No GLSL text changes. The host changes the `imageView1` subresource range from base layer 1 through 5. | [Second-view base calculation](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L156-L180), [shader generator](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L332-L377) |
| Cube view binding | No declaration changes. Descriptor bindings 0 and 1 receive distinct cube views of the same image. | [Descriptor updates](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L182-L234) |

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
; Bound: 76
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 440
               OpName %main "main"
               OpName %Output "Output"
               OpMemberName %Output 0 "cube0_color0"
               OpMemberName %Output 1 "cube0_color1"
               OpMemberName %Output 2 "cube0_color2"
               OpMemberName %Output 3 "cube0_color3"
               OpMemberName %Output 4 "cube0_color4"
               OpMemberName %Output 5 "cube0_color5"
               OpMemberName %Output 6 "cube1_color0"
               OpMemberName %Output 7 "cube1_color1"
               OpMemberName %Output 8 "cube1_color2"
               OpMemberName %Output 9 "cube1_color3"
               OpMemberName %Output 10 "cube1_color4"
               OpMemberName %Output 11 "cube1_color5"
               OpName %sb_out "sb_out"
               OpName %u_cubeImage0 "u_cubeImage0"
               OpName %u_cubeImage1 "u_cubeImage1"
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpMemberDecorate %Output 1 NonReadable
               OpMemberDecorate %Output 1 Offset 16
               OpMemberDecorate %Output 2 NonReadable
               OpMemberDecorate %Output 2 Offset 32
               OpMemberDecorate %Output 3 NonReadable
               OpMemberDecorate %Output 3 Offset 48
               OpMemberDecorate %Output 4 NonReadable
               OpMemberDecorate %Output 4 Offset 64
               OpMemberDecorate %Output 5 NonReadable
               OpMemberDecorate %Output 5 Offset 80
               OpMemberDecorate %Output 6 NonReadable
               OpMemberDecorate %Output 6 Offset 96
               OpMemberDecorate %Output 7 NonReadable
               OpMemberDecorate %Output 7 Offset 112
               OpMemberDecorate %Output 8 NonReadable
               OpMemberDecorate %Output 8 Offset 128
               OpMemberDecorate %Output 9 NonReadable
               OpMemberDecorate %Output 9 Offset 144
               OpMemberDecorate %Output 10 NonReadable
               OpMemberDecorate %Output 10 Offset 160
               OpMemberDecorate %Output 11 NonReadable
               OpMemberDecorate %Output 11 Offset 176
               OpDecorate %sb_out NonReadable
               OpDecorate %sb_out Binding 2
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %u_cubeImage0 NonWritable
               OpDecorate %u_cubeImage0 Binding 0
               OpDecorate %u_cubeImage0 DescriptorSet 0
               OpDecorate %u_cubeImage1 NonWritable
               OpDecorate %u_cubeImage1 Binding 1
               OpDecorate %u_cubeImage1 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
     %Output = OpTypeStruct %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float %v4float
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
         %13 = OpTypeImage %float Cube 0 0 0 2 Rgba8
%_ptr_UniformConstant_13 = OpTypePointer UniformConstant %13
%u_cubeImage0 = OpVariable %_ptr_UniformConstant_13 UniformConstant
      %v3int = OpTypeVector %int 3
      %int_1 = OpConstant %int 1
         %19 = OpConstantComposite %v3int %int_1 %int_1 %int_0
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
         %24 = OpConstantComposite %v3int %int_1 %int_1 %int_1
      %int_2 = OpConstant %int 2
         %29 = OpConstantComposite %v3int %int_1 %int_1 %int_2
      %int_3 = OpConstant %int 3
         %34 = OpConstantComposite %v3int %int_1 %int_1 %int_3
      %int_4 = OpConstant %int 4
         %39 = OpConstantComposite %v3int %int_1 %int_1 %int_4
      %int_5 = OpConstant %int 5
         %44 = OpConstantComposite %v3int %int_1 %int_1 %int_5
      %int_6 = OpConstant %int 6
%u_cubeImage1 = OpVariable %_ptr_UniformConstant_13 UniformConstant
      %int_7 = OpConstant %int 7
      %int_8 = OpConstant %int 8
      %int_9 = OpConstant %int 9
     %int_10 = OpConstant %int 10
     %int_11 = OpConstant %int 11
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpLoad %13 %u_cubeImage0
         %20 = OpImageRead %v4float %16 %19
         %22 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_0
               OpStore %22 %20
         %23 = OpLoad %13 %u_cubeImage0
         %25 = OpImageRead %v4float %23 %24
         %26 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_1
               OpStore %26 %25
         %28 = OpLoad %13 %u_cubeImage0
         %30 = OpImageRead %v4float %28 %29
         %31 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_2
               OpStore %31 %30
         %33 = OpLoad %13 %u_cubeImage0
         %35 = OpImageRead %v4float %33 %34
         %36 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_3
               OpStore %36 %35
         %38 = OpLoad %13 %u_cubeImage0
         %40 = OpImageRead %v4float %38 %39
         %41 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_4
               OpStore %41 %40
         %43 = OpLoad %13 %u_cubeImage0
         %45 = OpImageRead %v4float %43 %44
         %46 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_5
               OpStore %46 %45
         %49 = OpLoad %13 %u_cubeImage1
         %50 = OpImageRead %v4float %49 %19
         %51 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_6
               OpStore %51 %50
         %53 = OpLoad %13 %u_cubeImage1
         %54 = OpImageRead %v4float %53 %24
         %55 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_7
               OpStore %55 %54
         %57 = OpLoad %13 %u_cubeImage1
         %58 = OpImageRead %v4float %57 %29
         %59 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_8
               OpStore %59 %58
         %61 = OpLoad %13 %u_cubeImage1
         %62 = OpImageRead %v4float %61 %34
         %63 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_9
               OpStore %63 %62
         %65 = OpLoad %13 %u_cubeImage1
         %66 = OpImageRead %v4float %65 %39
         %67 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_10
               OpStore %67 %66
         %69 = OpLoad %13 %u_cubeImage1
         %70 = OpImageRead %v4float %69 %44
         %71 = OpAccessChain %_ptr_Uniform_v4float %sb_out %int_11
               OpStore %71 %70
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates a cube-compatible, optimal-tiled 16 x 16 image with `VK_IMAGE_USAGE_STORAGE_BIT`, `VK_IMAGE_USAGE_SAMPLED_BIT`, `VK_IMAGE_USAGE_TRANSFER_SRC_BIT`, and `VK_IMAGE_USAGE_TRANSFER_DST_BIT`. It creates one six-layer cube view at layer 0 and another at `numLayers - 6`. [Image and view setup](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L156-L180) binds both views as storage-image descriptors.
- Before dispatch, the command buffer transitions all image layers from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`. It fills one host-visible buffer region per layer with the layer's grayscale value and copies each region into its matching image layer. A second barrier makes the transfer writes visible to compute shader reads in `VK_IMAGE_LAYOUT_GENERAL`. [Initialization and transition sequence](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L211-L263)
- The test dispatches one workgroup, then uses a shader-write-to-host-read buffer barrier. After queue completion, it invalidates the host-visible output allocation. [Dispatch, synchronization, and wait](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L265-L274)
- The host expects view 0 face `i` to contain the color for physical layer `i`, and view 1 face `i` to contain the color for physical layer `numLayers - 6 + i`. It compares every RGBA component of all twelve `vec4` values with epsilon `1 / (2 * 256)`. A mismatch returns `fail`; otherwise the case returns `pass`. [Both comparison loops](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L276-L307)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `7`, `8`, `9`, `10`, or `11` | Nonzero cube-view base-layer mapping, face-index interpretation, image-view descriptor access, layer initialization and transfer visibility, storage-buffer readback, or host color comparison. |

### Cause Analysis

#### Cube-view layer mapping or observed result path

**Possible failure symptoms:** One or more of the twelve returned colors differs from its expected layer color. A mismatch only in the second six results identifies the nonzero-base cube view as the differing observation path. A mismatch only at a face index identifies a wrong mapping for that view-relative face or a bad value from the corresponding physical layer.

**Possible implementation causes:** The source binds two six-layer cube views of the same image and gives every physical layer a unique color. An incorrect `baseArrayLayer` offset, cube-face mapping, descriptor view interpretation, `imageLoad` result, transfer-to-shader visibility dependency, shader-to-host buffer visibility dependency, or readback comparison can produce the observed mismatch. The source comparison does not isolate which stage first produced a wrong value, so diagnosis of a specific failure requires inspecting the returned twelve values and the execution log.

## Case Pruning

### Requirement-based pruning

- The source has no runtime support callback and does not generate feature-gated branches. Every registered case uses the fixed cube-compatible image configuration and the fixed `VK_FORMAT_R8G8B8A8_UNORM` format.
- Image-view validity still requires each six-layer range to fit within the created image. The source chooses the second base as `numLayers - 6`, so `baseArrayLayer + layerCount` equals `numLayers`. [View construction](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L156-L180) and [view-range validity rule](../../../../vulkan-docs/src/chapters/resources.adoc#L6136-L6165) establish that boundary.

### Design-based pruning

- The factory registers only `7` through `11` layers. Those counts produce second-view base layers 1 through 5, so every leaf tests a nonzero base layer that is not aligned to a six-layer boundary. [Registered size array](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L384-L387)
- The test fixes the face extent, format, mip count, sample count, and a six-layer view count. It isolates cube-view base-layer interpretation rather than format conversion, sampling, mip selection, or cube-array length.
- Although the instance assertion accepts layer counts from 6 through 16, the factory intentionally chooses only five nonzero-base cases. A six-layer image would make the second view start at 0 and would not exercise the target behavior.

## Key Takeaways

- Each leaf compares two cube views of one image. The aligned view is a reference, while the second view proves the mapping from a nonzero `baseArrayLayer` to six view-relative cube faces.
- Unique per-layer grayscale values make a wrong physical-layer selection observable without rendering or directional cube-map sampling.
- The registered layer counts select second-view base layers 1 through 5, then validate all six faces with one compute dispatch and twelve host comparisons.
- A failure reports an observed color mismatch. The returned face values distinguish the view and face that diverged, but source-level investigation must locate the first failing operation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Cube image creation | [`makeImageCreateInfo()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L59-L81) | Defines the cube-compatible 2D image, usage flags, tiling, and single-mip configuration. |
| Per-layer upload helper | [`fillBuffer()` and `makeBufferImageCopy()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L84-L117) | Writes the host-side color pattern and describes each layer copy. |
| Instance execution and comparison | [`MisalignedCubeTestInstance::iterate()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L146-L308) | Creates both views, uploads layer values, dispatches compute, synchronizes readback, and decides pass or fail. |
| Generated compute shader | [`MisalignedCubeTest::initPrograms()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L332-L377) | Generates the two cube-image declarations and the twelve `imageLoad` operations. |
| Case registration | [`createMisalignedCubeTests()`](../../../modules/vulkan/image/vktImageMisalignedCubeTests.cpp#L391-L405) | Registers the five exact layer-count leaves. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L99) | Places `misaligned_cube` in the `image` test category. |
| Vulkan cube-view rules | [`resources.adoc`](../../../../vulkan-docs/src/chapters/resources.adoc#L6885-L6912) | Defines `baseArrayLayer`, layer count, cube face order, and six-layer cube mapping. |
| Mustpass inventories | [`vk-default`](../../../mustpass/main/vk-default/image/misaligned-cube.txt) and [`vksc-default`](../../../mustpass/main/vksc-default/image/misaligned-cube.txt) | Confirm the five default Vulkan and Vulkan SC leaves. |
