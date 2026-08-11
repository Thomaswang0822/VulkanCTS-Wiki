## Overview

**Core question:** Does GLSL `imageSize()` report the dimensions that Vulkan exposes through each storage-image or storage-texel-buffer view?

- This page covers [`vktImageSizeTests.cpp`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L57-L611), which implements the `image.image_size` test family registered by the image category.
- Each case binds one `VK_FORMAT_R32G32B32A32_SFLOAT` storage image or storage texel buffer, runs a one-invocation compute shader, and writes the result of `imageSize()` to an SSBO.
- The family varies image kind, access qualifier, and extent. It also tests a 2D view of a 3D image when that view type is available.
- The host compares the returned `ivec3` against an expectation derived from the constructed texture shape, including the special layer reporting rules for arrays and cube arrays.

## Background Knowledge

For the shared concept image/view/format interpretation, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- A storage image is a shader-visible image resource declared with an image type such as `image2D`; a storage texel buffer uses the corresponding buffer image type. `imageSize()` queries the resource shape rather than reading a texel.
- The dimensionality of an image type determines the integer vector returned by `imageSize()`. Array image types include a layer count, while cube-array queries report a count of cubes rather than a count of cube faces.
- An image view determines the shader-visible interpretation of an image. A 2D view of a 3D image exposes the selected slice as a two-dimensional resource.

## Registration Hierarchy

```text
image.image_size
├── 1d
├── 1d_array
├── 2d
├── 2d_array
├── 3d
├── cube
├── cube_array
└── buffer
```

[`createImageSizeTests()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L558-L611) creates these eight direct subgroups. The image category registers the family through [`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Image kind | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array`, `buffer` | Selects resource construction, shader image type, and the shape that `imageSize()` must return. | [image-type array](../../../modules/vulkan/image/vktImageSizeTests.cpp#L560-L563), [texture construction](../../../modules/vulkan/image/vktImageSizeTests.cpp#L57-L88) |
| Access qualifiers | `readonly`, `writeonly`, `readonly_writeonly` | Changes the qualifiers on the shader image declaration while keeping the size query and result comparison unchanged. | [flag definitions and shader declaration](../../../modules/vulkan/image/vktImageSizeTests.cpp#L170-L177), [shader generation](../../../modules/vulkan/image/vktImageSizeTests.cpp#L236-L270), [generated flags](../../../modules/vulkan/image/vktImageSizeTests.cpp#L573-L577) |
| Base extent | `32x32x32`, `12x34x56`, `1x1x1`, `7x1x1` | Provides regular, asymmetric, minimal, and thin dimensions. `getTexture()` maps these values to the dimensions and layer counts valid for each image kind. | [base extents](../../../modules/vulkan/image/vktImageSizeTests.cpp#L565-L571), [mapping rules](../../../modules/vulkan/image/vktImageSizeTests.cpp#L57-L88) |
| 2D view of 3D | normal 3D view; `2d_view` 3D variant | Changes the shader-facing image type from 3D to 2D and therefore removes the returned Z component. This variant exists only for the `3d` subgroup. | [shader image-type choice](../../../modules/vulkan/image/vktImageSizeTests.cpp#L236-L267), [case generation condition](../../../modules/vulkan/image/vktImageSizeTests.cpp#L588-L606) |
| Format | `VK_FORMAT_R32G32B32A32_SFLOAT` | Supplies the storage-image format qualifier and the texel-buffer view format used by every generated case. | [format selection](../../../modules/vulkan/image/vktImageSizeTests.cpp#L579-L606) |

## Behavior Parameters

The primary behavioral axis is the registered image kind. It changes the resource seen by the shader and the dimensional interpretation that the expected-result helper applies.

### 1d: One-dimensional storage image

The case queries the width of a 1D storage image. The expected result is `ivec3(width, 0, 0)`, because the generated shader pads the scalar `imageSize()` result to the SSBO's three-component output. [The expectation branch](../../../modules/vulkan/image/vktImageSizeTests.cpp#L142-L167) and [shader assignment](../../../modules/vulkan/image/vktImageSizeTests.cpp#L259-L267) use the same interpretation.

### 1d_array: Width and layer count

A 1D array has a one-dimensional layer size plus an array-layer count. The test expects `ivec3(width, layers, 0)`; `getTexture()` obtains the layer count from the Y component of the selected base extent. [Texture construction](../../../modules/vulkan/image/vktImageSizeTests.cpp#L62-L73) and [expected values](../../../modules/vulkan/image/vktImageSizeTests.cpp#L148-L159) define that relationship.

### 2d: Width and height

A 2D image produces two size components. The test pads that `ivec2` result to `ivec3(width, height, 0)` before writing the SSBO. [The 2D texture rule](../../../modules/vulkan/image/vktImageSizeTests.cpp#L69-L70) and [generated assignment](../../../modules/vulkan/image/vktImageSizeTests.cpp#L261-L266) show the two-component path.

### 2d_array: Width, height, and layer count

A 2D array reports width, height, and the array-layer count. The test constructs a one-layer-deep image extent and sets the texture layer count from the selected base Z component, then expects that three-component size. [Construction](../../../modules/vulkan/image/vktImageSizeTests.cpp#L72-L73) and [expected values](../../../modules/vulkan/image/vktImageSizeTests.cpp#L153-L159) establish the result.

### 3d: Width, height, and depth

The normal 3D cases expect the full 3D texture size. The `2d_view` variants instead declare a 2D shader image type and expect `ivec3(width, height, 0)`, which checks that the view's visible dimensionality controls the query. [The special expectation](../../../modules/vulkan/image/vktImageSizeTests.cpp#L153-L159) and [view-dependent shader type](../../../modules/vulkan/image/vktImageSizeTests.cpp#L236-L267) cover both paths.

### cube: Square face extent

A cube image is created with a square face extent and six layers. Its query returns the face width and height, padded to `ivec3(width, height, 0)`; the six faces do not appear as the Z result. [Cube construction](../../../modules/vulkan/image/vktImageSizeTests.cpp#L75-L76) and [expected values](../../../modules/vulkan/image/vktImageSizeTests.cpp#L148-L151) define the rule.

### cube_array: Square face extent and cube count

A cube array is created with twelve array layers, or two cubes of six faces each. The expected helper divides the layer count by six, so the query must return the number of cubes rather than the number of faces. [Cube-array construction](../../../modules/vulkan/image/vktImageSizeTests.cpp#L78-L79) and [cube-count calculation](../../../modules/vulkan/image/vktImageSizeTests.cpp#L161-L162) provide the evidence.

### buffer: Storage texel-buffer element count

The buffer subgroup uses a storage texel buffer instead of a `VkImage`. It queries its one-dimensional size and expects `ivec3(width, 0, 0)`; its instance class creates a buffer view with the selected format. [Buffer selection](../../../modules/vulkan/image/vktImageSizeTests.cpp#L478-L546) and [instance choice](../../../modules/vulkan/image/vktImageSizeTests.cpp#L548-L554) distinguish this path from image-backed cases.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.image_size.1d.readonly_32
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `1d` | Selects a storage image whose query result is one scalar width. |
| `readonly` | Adds `readonly` to the storage-image declaration generated by the case. |
| `32` | Selects the `32x32x32` base extent; the 1D texture mapping uses its X component as the width. |

#### Purpose

This representative compute shader checks the one-dimensional `imageSize()` path. It queries the bound `image1D`, expands the scalar result to the test's `ivec3` output representation, and writes that value to the result SSBO.

#### Structural Design

| Phase | Shader action | Test role |
|-------|---------------|-----------|
| Resource declaration | Declares a `rgba32f` readonly `image1D` at binding 0 and a write-only SSBO at binding 1. | Matches the storage image and host-visible result buffer bound by the test. |
| Query | Calls `imageSize(u_image)`. | Obtains the one-dimensional width under test. |
| Normalization and output | Builds `ivec3(width, 0, 0)` and stores it in `sb_out.size`. | Gives the host one uniform three-component representation to compare. |

#### Shader Code

```glsl
#version 440

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the readonly `VK_FORMAT_R32G32B32A32_SFLOAT` 1D storage image.
layout (binding = 0, rgba32f) readonly uniform highp image1D u_image;
/// Binding 1 receives the normalized three-component query result.
layout (binding = 1) writeonly buffer Output {
    ivec3 size;
} sb_out;

void main (void)
{
    /// `imageSize(image1D)` yields one component; the test pads Y and Z with zero.
    sb_out.size = ivec3(imageSize(u_image), 0, 0);
}
```

#### Additional Info

- [`SizeTest::initPrograms()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L236-L270) generates this source shape. It selects `image1D` for the 1D kind and appends `readonly` from the selected flag.
- Other image kinds change the generated image type and the conversion to `ivec3`; the test still uses one compute invocation and the same output-buffer layout.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Image kind | Changes the image type and selects scalar, two-component, or three-component `imageSize()` assignment logic. The 3D 2D-view path uses the 2D form. | [shader generator](../../../modules/vulkan/image/vktImageSizeTests.cpp#L236-L270) |
| Access qualifier | Adds `readonly`, `writeonly`, or both tokens to the storage-image declaration. | [qualifier construction](../../../modules/vulkan/image/vktImageSizeTests.cpp#L243-L254) |
| Base extent | Does not alter shader text; it changes the bound resource size that the query must report. | [case generation](../../../modules/vulkan/image/vktImageSizeTests.cpp#L565-L606) |

#### SPIR-V

- Status: reconstructed from the generated GLSL; not independently validated in this audit
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 25
; Schema: 0
               OpCapability Shader
               OpCapability Image1D
               OpCapability ImageQuery
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 440
               OpName %main "main"
               OpName %Output "Output"
               OpMemberName %Output 0 "size"
               OpName %sb_out "sb_out"
               OpName %u_image "u_image"
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpDecorate %sb_out NonReadable
               OpDecorate %sb_out Binding 1
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %u_image NonWritable
               OpDecorate %u_image Binding 0
               OpDecorate %u_image DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v3int = OpTypeVector %int 3
     %Output = OpTypeStruct %v3int
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
      %int_0 = OpConstant %int 0
      %float = OpTypeFloat 32
         %13 = OpTypeImage %float 1D 0 0 0 2 Rgba32f
%_ptr_UniformConstant_13 = OpTypePointer UniformConstant %13
    %u_image = OpVariable %_ptr_UniformConstant_13 UniformConstant
%_ptr_Uniform_v3int = OpTypePointer Uniform %v3int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpLoad %13 %u_image
         %17 = OpImageQuerySize %int %16
         %18 = OpCompositeConstruct %v3int %17 %int_0 %int_0
         %20 = OpAccessChain %_ptr_Uniform_v3int %sb_out %int_0
               OpStore %20 %18
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The test allocates a host-visible 12-byte result buffer for the shader's `ivec3` output. [Result-buffer setup](../../../modules/vulkan/image/vktImageSizeTests.cpp#L312-L329) fixes that size at three 32-bit components.
- Image-backed cases create an optimal-tiled storage image and an image view. The image contents remain uninitialized because the shader only queries its dimensions. Buffer cases create a storage texel buffer and `VkBufferView` instead. [Image setup](../../../modules/vulkan/image/vktImageSizeTests.cpp#L410-L429) and [buffer setup](../../../modules/vulkan/image/vktImageSizeTests.cpp#L501-L516) define the two resource paths.
- Before dispatch, image-backed cases transition the image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_GENERAL`. The command buffer binds the compute pipeline and descriptor set, dispatches exactly `(1, 1, 1)`, and inserts a shader-write-to-host-read barrier for the result buffer. [Command recording](../../../modules/vulkan/image/vktImageSizeTests.cpp#L331-L372) and [image transition](../../../modules/vulkan/image/vktImageSizeTests.cpp#L463-L476) show the synchronization.
- After the queue completes, the host invalidates the result allocation, reads three integers, computes the expected `ivec3`, and fails the case if the vectors differ. [Readback and comparison](../../../modules/vulkan/image/vktImageSizeTests.cpp#L374-L387) make the pass condition explicit.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `1d` or `buffer` | The query can report an incorrect one-dimensional element count, or the scalar-to-`ivec3` normalization can be wrong. |
| `1d_array`, `2d`, or `cube` | The query can report incorrect width or height, or the two-component result can be padded incorrectly. |
| `2d_array` or normal `3d` | The query can report an incorrect layer count or depth in the third component. |
| `3d` with `2d_view` | The implementation can expose a 3D interpretation instead of the 2D view interpretation. |
| `cube_array` | The query can report face layers rather than the number of cubes. |

### Cause Analysis

#### Query dimensionality or output normalization

**Possible failure symptoms:** the host readback differs from the expected `ivec3`; for one- and two-dimensional resources, this includes a nonzero padded component or an incorrect width or height.

**Possible implementation causes:** a shader compiler can lower `imageSize()` with the wrong result dimensionality, or the execution path can write the queried components incorrectly to the SSBO. The source isolates this outcome by normalizing every shader result to `ivec3` before the host comparison. [Generated assignments](../../../modules/vulkan/image/vktImageSizeTests.cpp#L259-L267) and [comparison](../../../modules/vulkan/image/vktImageSizeTests.cpp#L374-L387) support this diagnosis.

#### Array, depth, and cube-array interpretation

**Possible failure symptoms:** the X and Y components match while Z differs for an array, 3D, or cube-array case. A cube-array mismatch appears when the result reflects twelve faces rather than two cubes for the constructed resource.

**Possible implementation causes:** the query can use an incorrect array-layer or depth interpretation, or fail to convert cube-array face layers to cube count. The expected-result helper explicitly separates these cases, including division by six for cube arrays. [Expected-result branches](../../../modules/vulkan/image/vktImageSizeTests.cpp#L131-L167) ground the distinctions.

#### 2D view of 3D interpretation

**Possible failure symptoms:** a `2d_view` case returns a nonzero Z component or a result inconsistent with the selected 2D view's width and height.

**Possible implementation causes:** the image-view or shader-interface path can retain the underlying 3D interpretation when the shader queries the 2D view. The test uses a 2D shader image type for this variant and expects a zero Z component. [View-dependent type and assignment](../../../modules/vulkan/image/vktImageSizeTests.cpp#L236-L267) and [view-specific expected result](../../../modules/vulkan/image/vktImageSizeTests.cpp#L153-L159) establish that expectation.

## Case Pruning

### Requirement-based pruning

- `cube_array` requires the core `imageCubeArray` feature. [Support check](../../../modules/vulkan/image/vktImageSizeTests.cpp#L210-L216) requests it before the case runs.
- For image-backed cases, the test queries `getPhysicalDeviceImageFormatProperties()` with the constructed storage-image create information and reports unsupported format usage as a skip. [Format support check](../../../modules/vulkan/image/vktImageSizeTests.cpp#L217-L230) provides the gate.
- A 2D view of a 3D image requires `VK_EXT_image_2d_view_of_3d`. [Extension requirement](../../../modules/vulkan/image/vktImageSizeTests.cpp#L232-L233) enforces that condition.

### Design-based pruning

- The 2D-view branch is generated only for the `3d` subgroup; it does not describe the other image kinds. [Generation condition](../../../modules/vulkan/image/vktImageSizeTests.cpp#L588-L606) removes those meaningless combinations.
- Vulkan SC builds omit all 2D-view variants because the source excludes them when `CTS_USES_VULKANSC` is defined. [Vulkan SC guard](../../../modules/vulkan/image/vktImageSizeTests.cpp#L594-L598) implements this build-time pruning.

## Key Takeaways

- The family reduces each `imageSize()` result to a common `ivec3` representation, then checks it with one host readback comparison.
- Image kind is the central behavioral parameter: it controls whether the test checks width, height, layers, depth, cube count, or texel-buffer element count.
- The 3D 2D-view cases verify view-visible dimensionality, and cube-array cases verify cube count rather than face-layer count.
- Access qualifiers and several extents broaden coverage without changing the core query-and-compare mechanism.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Texture construction and expected size | [`getTexture()` and `getExpectedImageSizeResult()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L57-L168) | Defines the resource shape and the expected query result for every image kind. |
| Support and generated shader | [`SizeTest::checkSupport()` and `SizeTest::initPrograms()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L210-L270) | Defines feature and format gates plus the generated GLSL. |
| Execution and comparison | [`SizeTestInstance::iterate()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L312-L387) | Records the dispatch, synchronizes the result buffer, and applies the pass/fail comparison. |
| Image and buffer resource paths | [instance implementations](../../../modules/vulkan/image/vktImageSizeTests.cpp#L389-L546) | Shows the distinct descriptors and resources used for images and texel buffers. |
| Case matrix registration | [`createImageSizeTests()`](../../../modules/vulkan/image/vktImageSizeTests.cpp#L558-L611) | Registers all image-kind groups and generates qualifier, extent, and 2D-view cases. |
| Category registration | [`vktImageTests.cpp`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L100) | Adds `image_size` to the image category. |
| Default SPIR-V target | [`getBaselineSpirvVersion()`](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052) | Supplies SPIR-V 1.0 when this shader source does not provide explicit build options. |
