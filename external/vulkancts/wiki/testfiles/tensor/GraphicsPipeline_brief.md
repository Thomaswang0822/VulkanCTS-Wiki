# Understanding Brief: tensor.graphics_pipeline

## One-Sentence Test Purpose

This test checks whether Vulkan tensor reads work in both vertex and fragment shader stages when tensor-backed data drives rectangle geometry and rendered pixel values.

## Background Knowledge

### Tensor views and coordinates

A tensor view exposes a multidimensional tensor to a shader. `tensorReadARM` receives one integer coordinate per tensor dimension, and the coordinates are checked against the tensor dimensions. This test uses a rank-2 `R32_SINT` tensor for vertex positions and a rank-3 `R8_UINT` tensor for fragment values.

Why it matters here:
- The vertex tensor uses `gl_VertexIndex` with coordinate 0 or 1 for x and y.
- The fragment tensor uses `coord_y`, `coord_x`, and `0`, so its first two dimensions follow image height and width.
- The shader tensor declaration and the bound view must agree on element type, rank, and shape ([tensor operation validation](../../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors-operation-validation)).

### Dynamic rendering and attachment layouts

Dynamic rendering supplies the color attachment through `VkRenderingInfo`. The image must use `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` during rendering, then the test copies it to a host-visible buffer. The layout transition, rendering commands, copy, submission, and wait form one ordered GPU sequence.

## One Concrete Example

For `dEQP-VK.tensor.graphics_pipeline.600x600`, the host creates a 600 by 600 `VK_FORMAT_R8G8B8A8_UINT` color image, a rank-3 fragment tensor with dimensions `{600, 600, 1}`, and a rank-2 vertex tensor with dimensions `{12, 2}`. The 12 rows contain two triangles for each of two rectangles: `{50, 40, 200, 200}` and `{350, 340, 200, 200}`.

The vertex shader reads each row's x and y values and converts pixel coordinates to clip space. The fragment shader converts `gl_FragCoord.xy` to integer tensor coordinates, reads the green value, and writes `(0, value, 0, 255)`. Pixels outside both rectangles retain the clear color `(255, 0, 0, 255)`.

## End-to-End Test Flow

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

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` supplies vertex and fragment GLSL strings. The vertex program has specialization constants 0 and 1 for image width and height. The host maps them to the selected image shape. The fragment program has no specialization constants.

The pipeline uses dynamic rendering, `VK_FORMAT_R8G8B8A8_UINT`, triangle-list input assembly, and a 12-vertex draw.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Fragment tensor | yes | set 0, binding 0 | fragment shader reads | no | Supplies one byte per image coordinate. |
| Vertex tensor | yes | set 0, binding 1 | vertex shader reads | no | Supplies rectangle triangle coordinates. |
| Tensor views | yes | through tensor descriptors | shader tensor operations use them | no | Carry tensor format, rank, shape, and resource identity. |
| Color image | yes | dynamic color attachment | color output writes it | copied to buffer | Receives clear and rendered pixels. |
| Image buffer backing | yes | copy destination | transfer writes it | yes | Host-visible readback for the pixel scan. |
| Descriptor set and pipeline | yes | bound for the draw | device consumes state | no | Expose both tensor bindings to their stages. |

`uploadToTensor()` either copies directly into host-visible tensor memory and flushes it, or uses a staging buffer, an aliasing buffer bound to the tensor allocation, a transfer copy, a transfer-to-memory-read barrier, and a waited submission ([uploadToTensor](../../../vulkan/framework/vulkan/vkTensorUtil.cpp#L41-L101)).

## What Is Checked

- A pixel inside either rectangle must be `(0, fragmentTensorData[y * width + x], 0, 255)`.
- A pixel outside both rectangles must be `(255, 0, 0, 255)`.
- The host invalidates the image readback allocation and checks every pixel. The first mismatch names its coordinate, actual RGBA value, and expected RGBA value ([pixel scan](../../../vulkancts/modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L447-L500)).

## Behavior Parameter Identification

> **Behavior parameter:** registered image-shape test case
>
> **Candidate values:** `600x600`, `1280x720`, `567x891`, `891x567`

The image shape is the primary behavioral axis because it changes the image extent, fragment tensor shape, vertex specialization constants, viewport, scissor, render area, copy extent, and host scan.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `600x600` | Tensor reads or descriptor binding fail for a square image; vertex coordinate conversion, dynamic rendering, or pixel validation is incorrect. |
| `1280x720` | Width and height specialization or non-square image coordinate handling is incorrect; fragment tensor indexing or render setup may be wrong. |
| `567x891` | Portrait image dimensions are mapped incorrectly between image extent, tensor dimensions, viewport, and `gl_FragCoord`. |
| `891x567` | Landscape image dimensions are mapped incorrectly between image extent, tensor dimensions, viewport, and `gl_FragCoord`. |

## Important Variations and Special Cases

The four leaves keep the same shader logic and rectangle definitions. They vary the image dimensions; the fragment tensor becomes `{height, width, 1}` and the vertex tensor remains `{12, 2}`. The test covers square, wide, tall, and inverse-aspect-ratio images.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and test-case names | [createGraphicsPipelineTests](../../../vulkancts/modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L503-L509) | Defines all four executable leaves. |
| Category registration | [tensor root](../../../vulkancts/modules/vulkan/tensor/vktTensorTests.cpp#L37-L49) | Adds `graphics_pipeline` under `tensor`. |
| Support gates | [checkSupport](../../../vulkancts/modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L97-L128) | Requires extension, rank, formats, tensor access, and both stages. |
| Shader generation | [initPrograms](../../../vulkancts/modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L130-L175) | Defines tensor declarations, coordinates, specialization constants, and outputs. |
| Tensor and image setup | [resource setup](../../../vulkancts/modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L189-L255) | Shows ranks, dimensions, formats, usages, and initialized data. |
| Descriptors and pipeline | [descriptor and pipeline setup](../../../vulkancts/modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L257-L390) | Binds tensor views and builds dynamic rendering state. |
| Render and synchronization | [command recording](../../../vulkancts/modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L392-L445) | Transitions, renders, copies, submits, and waits. |
| Tensor coordinate semantics | [coordinate validation](../../../vulkan-docs/src/chapters/VK_ARM_tensors/tensorops.adoc#tensors-coordinate-validation) | Defines coordinate bounds for tensor reads. |

## Questions / Risk Points for User Audit

- Is the distinction between the rank-2 vertex tensor and rank-3 fragment tensor clear?
- Is the relationship between `gl_FragCoord`, `{height, width, 1}`, and the host scan clear?
- Does the timeline show tensor upload and render-to-readback synchronization?
- Is the failure mapping specific enough to separate aspect-ratio errors from shared tensor-access failures?

## Conversion Notes for Final Wiki Page

- Keep the four image-shape leaves as the primary behavior subsections.
- Retain the resource table and host/device timeline in shorter form.
- Use the 600x600 case for one two-stage shader walkthrough.
- Copy the `### Failure Cause Mapping` table directly into `## Failure Meaning`; write `### Cause Analysis` fresh.
- Include generated SPIR-V for both shown stages.
