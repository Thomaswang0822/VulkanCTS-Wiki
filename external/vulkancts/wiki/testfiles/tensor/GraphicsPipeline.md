## Overview

**Core question:** Does tensor access remain correct when vertex and fragment shader stages drive rendered pixels?

- This page covers the `tensor.graphics_pipeline` family and its four registered image-shape cases.
- The vertex shader reads rectangle coordinates from a rank-2 tensor; the fragment shader reads values from a rank-3 tensor and writes the rendered result.
- The page explains the shape matrix, generated shader behavior, resource and synchronization flow, result checking, pruning, and failure meaning.

## Background Knowledge

### Tensor views and coordinates

A tensor view exposes a multidimensional tensor to a shader. `tensorReadARM` receives one integer coordinate per tensor dimension, and the coordinates are checked against the tensor dimensions. This test uses a rank-2 `R32_SINT` tensor for vertex positions and a rank-3 `R8_UINT` tensor for fragment values.

The vertex tensor uses `gl_VertexIndex` with coordinate 0 or 1 for x and y. The fragment tensor uses `coord_y`, `coord_x`, and `0`, so its first two dimensions follow image height and width. The shader tensor declaration and the bound view must agree on element type, rank, and shape ([tensor operation validation](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors-operation-validation)).

### Dynamic rendering and attachment layouts

Dynamic rendering supplies the color attachment through `VkRenderingInfo`. The image uses `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` during rendering and is then copied to a host-visible buffer. The layout transition, rendering commands, copy, submission, and wait form one ordered GPU sequence.

## Registration Hierarchy

The test is registered under the tensor category with one graphics-pipeline group and four image-shape leaves:

```text
tensor
└── graphics_pipeline
```

The executable test names are:

- `dEQP-VK.tensor.graphics_pipeline.600x600`
- `dEQP-VK.tensor.graphics_pipeline.1280x720`
- `dEQP-VK.tensor.graphics_pipeline.567x891`
- `dEQP-VK.tensor.graphics_pipeline.891x567`

All four leaves use the same shader logic and rectangle definitions. The registered image shape is the behavior parameter: it changes the image extent, fragment-tensor shape, vertex-shader specialization constants, viewport, scissor, render area, copy extent, and host-side pixel scan.

## Behavior Parameters

### `600x600`

The square case creates a 600 by 600 `VK_FORMAT_R8G8B8A8_UINT` color image, a rank-3 fragment tensor with dimensions `{600, 600, 1}`, and a rank-2 vertex tensor with dimensions `{12, 2}`.

### `1280x720`

The wide case creates a 1280 by 720 color image. The fragment tensor dimensions are `{720, 1280, 1}`, while the vertex tensor remains `{12, 2}`. The selected width and height are also passed to the vertex shader through specialization constants 0 and 1.

### `567x891`

The tall case creates a 567 by 891 color image. The fragment tensor dimensions are `{891, 567, 1}`, while the vertex tensor remains `{12, 2}`. This exercises portrait image coordinates through the image extent, viewport, `gl_FragCoord`, tensor indexing, and readback scan.

### `891x567`

The inverse-aspect-ratio case creates an 891 by 567 color image. The fragment tensor dimensions are `{567, 891, 1}`, while the vertex tensor remains `{12, 2}`. This exercises landscape image coordinates with the same shader and rectangle data.

For every leaf, the 12 vertex-tensor rows contain two triangles for each of two rectangles: `{50, 40, 200, 200}` and `{350, 340, 200, 200}`. The image dimensions vary; the rectangle definitions and shader behavior do not.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tensor.graphics_pipeline.600x600
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `600x600` image shape | Selects the square image extent and the fragment tensor shape `{600, 600, 1}`. |
| `VK_FORMAT_R8_UINT` fragment tensor | Supplies one unsigned byte for each fragment coordinate. |
| `VK_FORMAT_R32_SINT` vertex tensor | Supplies the 12 two-component rectangle vertices. |

#### Purpose

This case checks tensor reads in both graphics shader stages and compares the rendered image with the expected clear and tensor-derived colors.

#### Structural Design

| Stage | Tensor operation | Observable result |
|-------|------------------|-------------------|
| Vertex | Read x and y from the rank-2 vertex tensor using `gl_VertexIndex`. | Two rectangles are positioned in the selected image extent. |
| Fragment | Read one value from the rank-3 tensor using `{coord_y, coord_x, 0}`. | Interior pixels receive the tensor-derived green value. |
| Host | Copy the image to a host-visible buffer and scan every pixel. | A mismatch reports its coordinate and actual and expected RGBA values. |

#### Shader Code

##### Vertex shader

```glsl
layout(set=0, binding=1) uniform readonly tensorARM<int32_t, 2> tensor;
layout (constant_id = 0) const uint32_t imageShapeWidth = 0;
layout (constant_id = 1) const uint32_t imageShapeHeight = 0;
void main() {
    int32_t pos_x, pos_y;
    tensorReadARM(tensor, uint[]
        (gl_VertexIndex, 0), pos_x);
    tensorReadARM(tensor, uint[]
        (gl_VertexIndex, 1), pos_y);
    const vec2 position = vec2(pos_x, pos_y);
    const vec2 clip_space_pos = position * (2.0 / vec2(imageShapeWidth, imageShapeHeight)) - 1.0;
    gl_Position = vec4(clip_space_pos, 0.0, 1.0);
}
```

##### Fragment shader

```glsl
layout(location = 0) out vec4 outColor;
layout(set=0, binding=0) uniform readonly tensorARM<uint8_t, 3> tensor;
void main() {
    const uint coord_x = uint(gl_FragCoord.x);
    const uint coord_y = uint(gl_FragCoord.y);
    uint8_t tensorValue = uint8_t(0);
    tensorReadARM(tensor, uint[]
        (coord_y, coord_x, 0), tensorValue);
    outColor = vec4(0.0, tensorValue, 0.0, 255.0);
}
```

The following simplified source excerpt shows the tensor access and coordinate mapping documented above. The exact generated programs are assembled by [initPrograms](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L130-L175).

#### Additional Info

- The vertex stage receives image width and height through specialization constants.
- The fragment stage has no specialization constants.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Image shape | Changes image extent, fragment tensor dimensions, and vertex specialization constants. | [graphics pipeline source](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L177-L195) |
| Tensor format | Changes the tensor element declaration while preserving the read coordinates. | [shader generation](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L130-L175) |

#### SPIR-V

##### Vertex shader

- Status: generated and validated
- Source: CTS vertex program generated from the GLSL above
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 71
; Schema: 0
               OpCapability Shader
               OpCapability TensorsARM
               OpExtension "SPV_ARM_tensors"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %gl_VertexIndex %_
               OpSource GLSL 450
               OpSourceExtension "GL_ARM_tensors"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpName %main "main"
               OpName %tensor "tensor"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpDecorate %tensor NonWritable
               OpDecorate %tensor Binding 1
               OpDecorate %tensor DescriptorSet 0
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
       %void = OpTypeVoid
       %uint = OpTypeInt 32 0
        %int = OpTypeInt 32 1
     %uint_2 = OpConstant %uint 2
         %23 = OpTypeTensorARM %int %uint_2
       %tensor = OpVariable %_ptr_UniformConstant_23 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
         %26 = OpLoad %23 %tensor
         %33 = OpCompositeConstruct %_arr_uint_uint_2 %30 %uint_0
         %36 = OpTensorReadARM %int %26 %33
         %37 = OpLoad %23 %tensor
         %41 = OpCompositeConstruct %_arr_uint_uint_2 %39 %uint_1
         %43 = OpTensorReadARM %int %37 %41
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment shader

- Status: generated and validated
- Source: CTS fragment program generated from the GLSL above
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 44
; Schema: 0
               OpCapability Shader
               OpCapability Int8
               OpCapability TensorsARM
               OpExtension "SPV_ARM_tensors"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_ARM_tensors"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpName %main "main"
               OpName %tensor "tensor"
               OpName %gl_FragCoord "gl_FragCoord"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %tensor NonWritable
               OpDecorate %tensor Binding 0
               OpDecorate %tensor DescriptorSet 0
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
       %uint = OpTypeInt 32 0
      %uchar = OpTypeInt 8 0
     %uint_3 = OpConstant %uint 3
         %28 = OpTypeTensorARM %uchar %uint_3
       %tensor = OpVariable %_ptr_UniformConstant_28 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
         %31 = OpLoad %28 %tensor
         %35 = OpCompositeConstruct %_arr_uint_uint_3 %32 %33 %uint_0
         %36 = OpTensorReadARM %uchar %31 %35
               OpStore %outColor %43
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Generated or loaded program artifacts

The pipeline uses dynamic rendering, `VK_FORMAT_R8G8B8A8_UINT`, triangle-list input assembly, and a 12-vertex draw. The host creates shader modules from the generated vertex and fragment programs and builds one graphics pipeline for the selected image shape.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Fragment tensor | yes | set 0, binding 0 | fragment shader reads | no | Supplies one byte per image coordinate. |
| Vertex tensor | yes | set 0, binding 1 | vertex shader reads | no | Supplies rectangle triangle coordinates. |
| Tensor views | yes | through tensor descriptors | shader tensor operations use them | no | Carry tensor format, rank, shape, and resource identity. |
| Color image | yes | dynamic color attachment | color output writes it | copied to buffer | Receives clear and rendered pixels. |
| Image buffer backing | yes | copy destination | transfer writes it | yes | Host-visible readback for the pixel scan. |
| Descriptor set and pipeline | yes | bound for the draw | device consumes state | no | Expose both tensor bindings to their stages. |

`uploadToTensor()` either copies directly into host-visible tensor memory and flushes it, or uses a staging buffer, an aliasing buffer bound to the tensor allocation, a transfer copy, a transfer-to-memory-read barrier, and a waited submission ([uploadToTensor](../../../framework/vulkan/vkTensorUtil.cpp#L41-L101)).

### End-to-end flow

```text
[host] choose one registered image shape
[host] create and fill the rank-3 fragment tensor and rank-2 vertex tensor
[host] create tensor views, the uint image, descriptor set, shader modules, and graphics pipeline
[host] transition the image from UNDEFINED to COLOR_ATTACHMENT_OPTIMAL
[host] begin dynamic rendering and bind the pipeline and both tensor descriptors
[device] vertex shader reads rectangle coordinates from the rank-2 tensor
[device] fragment shader reads one uint8 value from the rank-3 tensor for each fragment
[device] store tensor-derived green pixels inside triangles and preserve cleared red pixels elsewhere
[host] end rendering, copy the color image to its buffer, submit, and wait
[host] invalidate the allocation and compare every pixel with the expected value
[host] return pass or a coordinate-specific comparison failure
```

The host uploads the tensors before the draw. It records the image transition, dynamic-rendering begin, pipeline and descriptor binding, 12-vertex draw, rendering end, and image-to-buffer copy in order. Submission and wait complete the GPU work before the host invalidates the readback allocation.

### What is checked

- A pixel inside either rectangle must be `(0, fragmentTensorData[y * width + x], 0, 255)`.
- A pixel outside both rectangles must be `(255, 0, 0, 255)`.
- The host invalidates the image readback allocation and checks every pixel. The first mismatch names its coordinate, actual RGBA value, and expected RGBA value ([pixel scan](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L447-L500)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `600x600` | Tensor reads or descriptor binding fail for a square image; vertex coordinate conversion, dynamic rendering, or pixel validation is incorrect. |
| `1280x720` | Width and height specialization or non-square image coordinate handling is incorrect; fragment tensor indexing or render setup may be wrong. |
| `567x891` | Portrait image dimensions are mapped incorrectly between image extent, tensor dimensions, viewport, and `gl_FragCoord`. |
| `891x567` | Landscape image dimensions are mapped incorrectly between image extent, tensor dimensions, viewport, and `gl_FragCoord`. |

### Cause Analysis

#### Shared setup and image-shape mapping

**Possible failure symptoms:** A failure is common to all four image-shape leaves, or the rendered region is displaced, transposed, or has an incorrect green channel.

**Possible implementation causes:** A common failure points first to tensor setup or access, including a tensor declaration/view mismatch, incorrect descriptor binding, missing stage capability, or upload/synchronization error. A shape-specific failure points to image extent, specialization constants, viewport, `gl_FragCoord`, tensor dimensions, or copy extent mapping. The source does not identify a more specific driver or hardware layer without further investigation.

## Case Pruning

### Requirement-based pruning

Before the test is run, `checkSupport()` prunes unsupported environments. It requires the tensor extension and the tensor capabilities needed by this test: the supported tensor rank and formats, tensor access in shader stages, and access from both vertex and fragment stages ([checkSupport](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L97-L128)). A missing required capability causes the case to be reported as unsupported rather than producing a misleading rendering comparison failure.

### Design-based pruning

The implementation keeps the four image-shape cases as generated leaves of the single `graphics_pipeline` family. It does not create separate registration groups for image width, height, tensor rank, or rectangle data; those values are behavior parameters of each leaf.

## Key Takeaways

- Is the distinction between the rank-2 vertex tensor and rank-3 fragment tensor clear?
- Is the relationship between `gl_FragCoord`, `{height, width, 1}`, and the host scan clear?
- Does the timeline show tensor upload and render-to-readback synchronization?
- Is the failure mapping specific enough to separate aspect-ratio errors from shared tensor-access failures?

## Source Reference Appendix