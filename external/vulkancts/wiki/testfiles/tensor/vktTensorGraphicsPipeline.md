# tensor.graphics_pipeline

## Overview

Tests that verify tensor access from within a Vulkan **graphics pipeline**, exercising both the vertex and fragment shader stages. The test creates two tensors -- one consumed by the vertex shader to define rectangle geometry and one consumed by the fragment shader to supply per-pixel colour data -- renders into an image, and validates the output pixel-by-pixel against expected values.

## Role of file

[vktTensorGraphicsPipeline.cpp](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp) registers the `graphics_pipeline` subgroup under `dEQP-VK.tensor`. It defines a single test case class ([`TensorGraphicsPipelineAccessTestCase`](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L83-L179)) and its corresponding instance ([`TensorGraphicsPipelineAccessTestInstance`](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L67-L81)), then enumerates four image-dimension variants via [`addGraphicsPipelineAccessTest`](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L503-L509). The factory function [`createGraphicsPipelineTests`](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L513-L521) creates the `TestCaseGroup` named `"graphics_pipeline"`.

## Source code link

[vktTensorGraphicsPipeline.cpp](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp)

[vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp) -- shared tensor test utilities (`TensorParameters`, `formatSupportTensorFlags`, `deviceSupportsShaderTensorAccess`, `deviceSupportsShaderStagesTensorAccess`, `getTensorPhysicalDeviceProperties`, etc.)

## Registration Hierarchy

```text
tensor.graphics_pipeline
├── 600x600
├── 1280x720
├── 567x891
└── 891x567
```

The four children are added in the order shown at [addGraphicsPipelineAccessTest](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L503-L509). Each child name is `"<width>x<height>"` constructed from the `VkExtent2D` parameter at the [TestCase constructor](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L87).

## Test Families

### 600x600

Registered at [line 505](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L505). Uses a square image extent of 600 by 600 pixels.

### 1280x720

Registered at [line 506](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L506). Uses a landscape-oriented 1280 by 720 image extent.

### 567x891

Registered at [line 507](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L507). Uses a portrait-oriented 567 by 891 image extent.

### 891x567

Registered at [line 508](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L508). Uses a landscape-oriented 891 by 567 image extent.

All four families share the same test logic; only the image dimensions differ.

## Parameter dimensions

Each test variant is parameterised by a single `VkExtent2D` value representing the render-target image dimensions ([m_imageShape](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L80)). This parameter controls:

- The shape of the **fragment tensor** (3-D: `{height, width, 1}`, format `VK_FORMAT_R8_UINT`) -- see [lines 191-194](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L191-L194).
- The shape of the **render-target image** (`VK_FORMAT_R8G8B8A8_UINT`) -- see [lines 253-255](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L253-L255).
- The viewport and scissor rectangles -- see [lines 340-342](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L340-L342).
- The specialization constants passed to the vertex shader (`imageShapeWidth`, `imageShapeHeight`) -- see [lines 316-325](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L316-L325).

The **vertex tensor** shape is fixed regardless of image dimensions: `{12, 2}` (i.e. 12 vertices x 2 coordinates, format `VK_FORMAT_R32_SINT`), derived from 2 rectangles x 6 vertices/rectangle x 2 dimensions -- see [lines 211-212](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L211-L212).

## Support / feature requirements

The [`checkSupport`](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L97-L128) method enforces the following requirements:

| Requirement | Source | Detail |
|---|---|---|
| `VK_ARM_tensors` device extension | [line 99](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L99) | `context.requireDeviceFunctionality("VK_ARM_tensors")` |
| Max tensor dimension count >= 3 | [line 101](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L101-L104) | The fragment tensor is 3-D, so the implementation must support at least 3 dimensions |
| `VK_FORMAT_R8_UINT` supports `VK_TENSOR_TILING_LINEAR_ARM` with `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` | [lines 106-110](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L106-L110) | Required for the fragment-shader tensor |
| `VK_FORMAT_R32_SINT` supports `VK_TENSOR_TILING_LINEAR_ARM` with `VK_FORMAT_FEATURE_2_TENSOR_SHADER_BIT_ARM` | [lines 112-116](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L112-L116) | Required for the vertex-shader tensor |
| Device supports shader tensor access | [lines 118-121](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L118-L121) | `deviceSupportsShaderTensorAccess(context)` from [vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L113) |
| Device supports shader tensor access in both fragment and vertex stages | [lines 123-127](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L123-L127) | `deviceSupportsShaderStagesTensorAccess(context, VK_SHADER_STAGE_FRAGMENT_BIT \| VK_SHADER_STAGE_VERTEX_BIT)` from [vktTensorTestsUtil.hpp](../../../modules/vulkan/tensor/vktTensorTestsUtil.hpp#L114) |

## Verification methods

The [`iterate`](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L181-L501) method performs pixel-level verification after rendering:

1. **Render**: Two rectangles (at offsets `{50,40}` and `{350,340}`, each 200x200 pixels) are drawn using dynamic rendering. The vertex shader reads rectangle corner positions from the vertex tensor; the fragment shader reads per-pixel values from the fragment tensor and writes them as the green channel of the output colour -- see [fragment shader](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L156-L174).

2. **Readback**: The colour attachment is copied to a host-visible buffer via [`copyImageToBuffer`](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L440-L441) and the allocation is invalidated for host access at [line 448](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L448).

3. **Pixel comparison** ([lines 452-498](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L452-L498)):
   - For pixels **inside** a rendered rectangle: the expected colour is `(0, fragmentTensorData[y*width+x], 0, 255)` -- i.e. the green channel must match the corresponding element of the fragment tensor, and R, B, A must be 0, 0, 255 respectively ([lines 472-473](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L472-L473)).
   - For pixels **outside** all rectangles: the expected colour is `(255, 0, 0, 255)`. The source code sets the clear value to `{{1.0f, 0.0f, 0.0f, 1.0f}}` ([line 420](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L420)), which for a `VK_FORMAT_R8G8B8A8_UINT` attachment reinterprets the float bits as uint32 (producing out-of-range values per the Vulkan spec); the test assumes implementation-specific clamping to `(255, 0, 0, 255)` ([lines 486-487](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L486-L487)).
   - Any mismatch causes an immediate `TestStatus::fail` with a diagnostic message containing the pixel coordinate and actual vs. expected RGBA values.

## Test principles

The test validates end-to-end tensor integration in a graphics pipeline by:

1. **Vertex-shader tensor read**: The vertex shader uses `tensorReadARM` to read per-vertex x/y positions from a 2-D `tensorARM<int32_t, 2>` descriptor (binding 1). Vertex positions define two screen-space rectangles rendered as triangle lists ([vertex shader](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L132-L154)).

2. **Fragment-shader tensor read**: The fragment shader uses `tensorReadARM` to read a per-pixel `uint8_t` value from a 3-D `tensorARM<uint8_t, 3>` descriptor (binding 0). The value is written to the green channel of the output colour ([fragment shader](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L156-L174)).

3. **Specialization constants**: The vertex shader receives image dimensions via specialization constants (`constant_id` 0 and 1) to compute clip-space positions from the integer tensor coordinates ([lines 140-143](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L140-L143)).

4. **Descriptor binding**: Two `VK_DESCRIPTOR_TYPE_TENSOR_ARM` bindings are used -- binding 0 for the fragment tensor, binding 1 for the vertex tensor ([lines 258-260](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L258-L260)).

5. **Dynamic rendering**: The test uses `vkCmdBeginRendering`/`vkCmdEndRendering` (no render pass object) with `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` ([lines 414-437](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L414-L437)).

6. **Data flow integrity**: By comparing rendered pixel values against the known tensor contents, the test confirms that tensor data traverses the full pipeline (host upload -> GPU tensor memory -> shader read -> framebuffer write -> host readback) without corruption.

## Notes / uncertainties

- The inside-rectangle check at [line 462](../../../modules/vulkan/tensor/vktTensorGraphicsPipeline.cpp#L462) uses `rectangle.extent.width` for both the x and y boundary comparisons. This appears to be a bug -- the y comparison should use `rectangle.extent.height` instead. As a consequence, the two rectangles (both 200x200) happen to produce correct results because `width == height`, but non-square rectangles would be checked incorrectly. This is observed in the inspected file and may affect future test variants.
- The fragment tensor is 3-D with a trailing dimension of 1 (`{height, width, 1}`). The `checkSupport` requires `maxTensorDimensionCount >= 3`, which is consistent with this shape.
- The test uses `VK_TENSOR_TILING_LINEAR_ARM` exclusively; optimal tiling is not exercised.
- The vertex tensor format `VK_FORMAT_R32_SINT` and fragment tensor format `VK_FORMAT_R8_UINT` are the only formats tested in this file. Other tensor formats are covered by sibling test files.
