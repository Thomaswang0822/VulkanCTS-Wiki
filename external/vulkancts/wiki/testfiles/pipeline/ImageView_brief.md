# Understanding Brief: pipeline image view tests

## One-Sentence Test Purpose

This test checks whether Vulkan sampling through an image view honors the view's type, format interpretation, component mapping, and selected mip-level and array-layer range.

## Background Knowledge

### An image view selects an interpretation and subresources

`VkImageViewCreateInfo` supplies a `viewType`, a format used to interpret texel blocks, a `VkComponentMapping`, and a `VkImageSubresourceRange`. The range selects the mipmap levels and array layers accessible through the view. The Vulkan specification defines these fields in [Image Views](../../../../vulkan-docs/src/chapters/resources.adoc#L5788-L5809).

Why it matters here:
- The suite constructs views over initialized color images while varying each of those selection properties.
- A sampling instruction must only see the subresources and remapped components selected by the view.

### Sampling a selected mip level

The suite uses nearest filtering and nearest mipmap selection. A `textureLod()` case supplies an explicit LOD, while other cases use ordinary texture sampling. The expected lookup constrains the reference LOD to the sampler's `minLod` and `maxLod`, which the test sets from the view range.

## One Concrete Example

Consider `dEQP-VK.pipeline.monolithic.image_view.view_type.2d_array.format.r8g8b8a8_unorm.subresource_range.lod_mip_levels`.

The case initializes a six-layer 2D-array image with mip levels, creates a view whose range starts at level zero and exposes three levels, and samples at LOD 4.0. It uses a `sampler2DArray`, dispatches or draws a texture-coordinate mosaic, and compares the observed sample values with a software lookup constrained by the selected range. The same registered leaf with the `_compute` suffix exercises the compute path.

## End-to-End Test Flow

```text
[host] register view-type, format, component-swizzle, and subresource-range leaves
[host] initialize a texture image and upload every source mip level and array layer
[host] create VkImageView with the tested viewType, format, components, and subresourceRange
[host] bind the view and nearest-filtering sampler to graphics or compute work
[device] sample the view with texture() or textureLod() and write results to the output image
[host] wait for completion, reconstruct the coordinate mosaic, and validate each sampled lookup
[host] report pass only when all observed samples fall within format-aware precision bounds
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `ImageViewTest::initPrograms()` generates GLSL for the chosen view type. It selects `sampler1D`, `sampler2DArray`, `samplerCube`, or another matching sampler type and selects the coordinate components for that type.
- Graphics cases generate a pass-through vertex shader and a fragment shader. Compute cases generate a one-workgroup-pixel compute shader that interpolates the same test mosaic from a storage-buffer vertex list.
- The shader multiplies the sampled result by a scale and adds a bias. The test applies the same component mapping to those values, so component-swizzle cases retain a format-aware expected result.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Source image and allocation | yes | yes | initialized by transfer; sampled by shader | indirectly | Contains the generated texture data for every tested mip level and layer. |
| `VkImageView` | yes | yes | read through combined image-sampler descriptor | no | Carries the tested type, format, component mapping, and subresource range. |
| Sampler | yes | yes | read during sampling | no | Uses nearest filtering, clamp-to-edge addressing, and range-derived LOD bounds. |
| Graphics color attachment or compute storage image | yes | yes | written by fragment or compute shader | yes | Captures observed sampling results for validation. |
| Vertex buffer or storage buffer | yes | yes | read by graphics vertex fetch or compute interpolation | no | Defines the texture-coordinate mosaic. |

## What Is Checked

- `ImageSamplingInstance::verifyImage()` reconstructs the coordinate mosaic with `ReferenceRenderer`, resolves the selected subresource range, and checks each lookup with `tcu::isLookupResultValid`.
- The oracle uses the selected image format, nearest-filter precision, mipmap-precision bounds, the component mapping, and extra sRGB tolerance where needed. It does not seek to measure filtering accuracy.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node beneath `pipeline.*.image_view.view_type.<view_type>.format.<format>`
>
> **Candidate values:** `component_swizzle`, `subresource_range`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `component_swizzle` | Image-view component remapping, format interpretation, sampler-type selection, or the graphics/compute sampling path returns channels different from the selected `VkComponentMapping`. |
| `subresource_range` | Image-view mip-level or array-layer selection, `VK_REMAINING_MIP_LEVELS` or `VK_REMAINING_ARRAY_LAYERS` resolution, explicit-LOD sampling, or range-derived LOD clamping selects data outside the view. |

## Important Variations and Special Cases

- The root covers `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, and `cube_array` view types. Array and cube cases use different layer counts and cube cases use six-layer face units.
- Each supported format group has four cyclic RGBA component mappings and both graphics and `_compute` leaves.
- Subresource-range leaf inventories depend on view type. Array-capable views vary mip and layer bounds together; 3D views omit array-range combinations; several cases use `VK_REMAINING_MIP_LEVELS` or `VK_REMAINING_ARRAY_LAYERS`.
- The source adds ASTC 3D formats only for `VK_IMAGE_VIEW_TYPE_3D` outside Vulkan SC, and checks ASTC support. Two maintenance5 formats require `VK_KHR_maintenance5` outside Vulkan SC.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test parameters, support checks, and generated programs | [`ImageViewTest`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L60-L315) | Defines the view parameters, graphics/compute programs, and support gates. |
| Subresource-range matrix | [`createSubresourceRangeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L425-L655) | Defines type-specific mip/layer configurations and `_compute` counterparts. |
| Component-swizzle matrix | [`getComponentMappingPermutations()` and `createComponentSwizzleTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L658-L756) | Defines four cyclic mappings and paired graphics/compute leaves. |
| Family registration | [`createImageViewTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L760-L1000) | Defines view types, format inventory, and hierarchy assembly. |
| Shared image setup and view creation | [`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L455-L560) | Uploads texture data and creates the tested `VkImageView`. |
| Submission and lookup oracle | [`iterate()` and `verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1029-L1039) and [`verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1640-L1704) | Defines completion and format-aware reference validation. |
| Vulkan image-view contract | [`Image Views`](../../../../vulkan-docs/src/chapters/resources.adoc#L5733-L5859) | Defines creation and the selected view type, format, component mapping, and subresource range. |

## Questions / Risk Points for User Audit

- The source uses one implementation for graphics and compute leaves. A graphics leaf requires its selected pipeline construction type, while a compute leaf checks the related shader-object construction requirements.
- The generated shaders perform the property under test by sampling the image view. The final page therefore describes the generated sampling form but does not embed a representative GLSL or SPIR-V listing, because it varies with view type, format class, LOD, and execution path.

## Conversion Notes for Final Wiki Rewrite

Keep the intermediate-node failure table verbatim. The final page should identify `component_swizzle` and `subresource_range` as the behavioral axis, explain graphics and compute execution in one lifecycle, and separate view-type and format coverage from the two properties checked.
