## Overview

**Core question:** Does sampling through each tested image view expose the selected channels, mip levels, and array layers for its view type and format?

- [`vktPipelineImageViewTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L1) implements the `pipeline.*.image_view` test family.
- The source builds image views over initialized sampled images, samples them through graphics and compute work, and validates the output against format-aware software lookups.
- The two intermediate nodes under each view-type and format path test component remapping and subresource selection.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- An image view supplies the type and format used to interpret an image, a `VkComponentMapping`, and a `VkImageSubresourceRange`. The range selects the mipmap levels and array layers that the view exposes. [Image Views](../../../../vulkan-docs/src/chapters/resources.adoc#L5788-L5809) defines these fields.
- A sampled-image shader accesses the view rather than the whole image. The suite uses nearest filtering and nearest mipmap selection, so its reference lookup can isolate view selection instead of filtering quality.
- `VK_REMAINING_MIP_LEVELS` and `VK_REMAINING_ARRAY_LAYERS` make a view range extend from the given base value to the available end of the image.

## Registration Hierarchy

```text
pipeline.monolithic.image_view
└── view_type
```

[`createImageViewTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L760-L1000) builds the same hierarchy for monolithic and `shader_object_unlinked_spirv` construction variants. The direct `view_type` intermediate node contains the seven view-type groups; each then contains `format`, a concrete format, and the two property nodes documented below. The main Vulkan mustpass list contains 27,708 `pipeline.monolithic.image_view` leaves and 27,708 `pipeline.shader_object_unlinked_spirv.image_view` leaves. The Vulkan SC monolithic list contains 26,736 leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| View type | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array` | Selects the image-view type, matching GLSL sampler type, image extent, layer count, coordinate components, and type-specific range cases. | [`imageViewTypes`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L762-L772), [`getGlslSamplerType()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L318-L363) |
| Format | Uncompressed, packed, floating-point, integer, ETC2, EAC, ASTC 2D, and BC5 formats; ASTC 3D formats for `3d` outside Vulkan SC | Selects texture data interpretation and lookup precision. | [format arrays](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L774-L938) |
| Intermediate node | `component_swizzle`, `subresource_range` | Selects the image-view property under test. | [factory assembly](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L940-L1000) |
| Component mapping | Four cyclic RGBA mappings: `r_g_b_a`, `g_b_a_r`, `b_a_r_g`, `a_r_g_b` | Remaps sampled color components in the image view. | [`getComponentMappingPermutations()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L658-L700) |
| Subresource range | Type-specific base mip level, mip count, base array layer, layer count, and `VK_REMAINING_*` combinations | Limits the visible subresources and drives explicit-LOD cases. | [`createSubresourceRangeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L425-L655) |
| Execution path | ordinary leaf and `_compute` counterpart | Samples the same view through graphics or compute execution. | [range leaf helper](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L444-L458), [swizzle leaf helper](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L741-L753) |

## Behavior Parameters

The primary behavioral axis is the intermediate node below each concrete view-type and format path. View type and format establish the object shape and data representation; the selected intermediate node decides whether the leaf checks component remapping or subresource visibility.

### `component_swizzle`: component remapping

This intermediate node creates a view over the complete valid range and changes only the four-component mapping. The source rotates the identity RGBA mapping four times. The generated shader samples the matching sampler type and applies a scale and bias that the host has remapped with the same mapping, so a channel-selection error changes the observed values.

### `subresource_range`: visible mip levels and array layers

This intermediate node retains identity component mapping and changes the view range. Cases select bounded mip ranges, bounded array-layer ranges, combinations of both, and `VK_REMAINING_MIP_LEVELS` or `VK_REMAINING_ARRAY_LAYERS`. Some leaves call `textureLod()` with LOD 4.0. The other generated shaders call `texture()`: the fragment path uses implicit level-of-detail selection, while the compute path has no explicit LOD operand. The software reference uses LOD 0.0 for those no-explicit-LOD cases. The registered combinations differ by view type because arrays, cube faces, and 3D images have different legal layer models.

## Shader Analysis

`ImageViewTest::initPrograms()` generates the shader source for each leaf. It chooses a sampler type from the `VkImageViewType`: `sampler1D`, `sampler1DArray`, `sampler2D`, `sampler2DArray`, `sampler3D`, `samplerCube`, or `samplerCubeArray`, with `i` or `u` prefixes for signed or unsigned integer formats. The graphics path passes the mosaic texture coordinates from vertex to fragment shader; the compute path interpolates that mosaic from a storage-buffer vertex list.

Both paths execute either `texture(texSampler, coordinates)` or `textureLod(texSampler, coordinates, samplerLod)`, then apply the generated scale and bias. That sample instruction is central to the tested property, but a fixed representative GLSL or SPIR-V listing would not represent the matrix because sampler declaration, coordinate arity, LOD form, format class, and graphics/compute path vary by leaf. This page records the generated forms from source rather than presenting an artificial single-case disassembly.

## Runtime Execution and Result Checking

- The test case packages the selected view type, format, mapping, range, sampler LOD, and execution mode into `ImageSamplingInstanceParams`. It fixes nearest minification, magnification, and mipmap filtering, clamp-to-edge addressing, and a `maxLod` derived from the view's `levelCount`.
- `ImageSamplingInstance::setup()` creates the sampled source image, initializes a test texture for all available mip levels and layers, uploads it, and creates `VkImageViewCreateInfo` with the selected `viewType`, `format`, `components`, and `subresourceRange`. It binds the view with a sampler as a combined image sampler.
- The graphics path writes sampled colors to a color-attachment output image. The compute path writes them to a storage output image. `iterate()` records setup work, submits the command buffer, and waits for completion before validation.
- `verifyImage()` uses `ReferenceRenderer` to reproduce the texture coordinates, resolves the selected source-image range, computes the nearest-filter lookup bounds and precision threshold for the chosen format, and validates the output image with `tcu::isLookupResultValid`. All four result components are checked for this family; the shared validator's reduced component mask applies only to sampler reduction-mode cases, which these tests do not create. The validator also includes an sRGB tolerance adjustment.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `component_swizzle` | Image-view component remapping, format interpretation, sampler-type selection, or the graphics/compute sampling path returns channels different from the selected `VkComponentMapping`. |
| `subresource_range` | Image-view mip-level or array-layer selection, `VK_REMAINING_MIP_LEVELS` or `VK_REMAINING_ARRAY_LAYERS` resolution, explicit-LOD sampling, or range-derived LOD clamping selects data outside the view. |

### Cause Analysis

#### Component mapping or format interpretation

**Possible failure symptoms:** Only `component_swizzle` leaves fail, often for one channel rotation, format class, or execution path. The observed sampled colors differ from the remapped reference values.

**Possible implementation causes:** The implementation may apply `VkComponentMapping` in the wrong component order, mishandle the selected view format, bind an incompatible sampler type, or execute the graphics and compute sampling paths differently. The image-view contract assigns component remapping to `VkImageViewCreateInfo::components`; source-level investigation is needed to distinguish sampling hardware from output or readback handling.

#### Mip-level or array-layer range selection

**Possible failure symptoms:** Only `subresource_range` leaves fail, especially explicit-LOD cases, a nonzero base mip level, a nonzero base array layer, or a remaining-range suffix.

**Possible implementation causes:** The implementation may resolve base/count fields or `VK_REMAINING_*` values incorrectly, expose subresources outside the view, clamp explicit LOD to the wrong interval, or select cube faces or array layers with the wrong unit. The specification defines `subresourceRange` as the set of accessible mipmap levels and array layers; the final output alone cannot separate view selection from shader sampling or transfer-readback faults.

#### View-type-specific image setup

**Possible failure symptoms:** Failures cluster by `1d`, array, `3d`, cube, or cube-array view type, while other types pass.

**Possible implementation causes:** The implementation may create an incompatible image type, extent, layer count, cube-compatible image, coordinate interpretation, or sampler declaration for the selected view type. The CTS setup derives those properties from the view type, so source-level investigation should compare image creation, view creation, descriptor binding, and the affected execution path.

## Case Pruning

### Requirement-based pruning

- Each leaf calls `checkSupportImageSamplingInstance()` for the derived image and sampling parameters. Graphics leaves require the selected pipeline-construction path; compute leaves require the corresponding shader-object construction path.
- ASTC 3D leaves occur only outside Vulkan SC and call `checkSupportAstcFormat()`. `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5` outside Vulkan SC.
- The source stops adding compressed formats for `1d` and `1d_array`, and it adds ASTC 3D formats only to `3d`.

### Design-based pruning

- The four cyclic component mappings provide a bounded channel-order matrix instead of all possible `VkComponentMapping` values.
- Each property leaf has one graphics and one `_compute` path, allowing the suite to compare execution models without multiplying the view-property matrix further.
- Subresource-range cases target boundaries and representative combinations: nonzero base values, fixed counts, cube face groups, and remaining-range constants. They do not enumerate every valid range.

## Key Takeaways

- An image view controls both how a shader interprets texels and which mip levels and array layers it can access.
- `component_swizzle` isolates `VkComponentMapping`; `subresource_range` isolates the view's visible subresources and LOD boundaries.
- The suite samples one view matrix through graphics and compute paths, then uses a format-aware software lookup oracle rather than a raw pixel equality check.
- View type changes resource shape, coordinates, and sampler declaration, so type-specific range combinations are part of the intended coverage.

## Source Reference Appendix

| Entry point or contract | Link | Why it matters |
|-------------------------|------|----------------|
| Test parameters, program generation, and support checks | [`ImageViewTest`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L60-L315) | Defines selected parameters, generated graphics/compute source, and requirements. |
| Type helpers and range registration | [`getGlslSamplerType()` through `createSubresourceRangeTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L318-L655) | Defines sampler choice, image shape, and type-specific subresource cases. |
| Component mappings and family registration | [`getComponentMappingPermutations()` through `createImageViewTests()`](../../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L658-L1000) | Defines swizzle leaves, view types, formats, and hierarchy assembly. |
| Pipeline-category registration | [`createPipelineTests()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L100-L125) | Registers the family only for monolithic and shader-object-unlinked-SPIR-V variants. |
| Shared image setup and image-view creation | [`ImageSamplingInstance::setup()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L455-L560) | Creates images, uploads data, and creates the tested view. |
| Submission and result validation | [`ImageSamplingInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1029-L1039) and [`verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1640-L1704) | Waits for execution and performs the reference lookup validation. |
| Vulkan image-view contract | [`Image Views`](../../../../vulkan-docs/src/chapters/resources.adoc#L5733-L5859) | Defines image-view creation and the tested fields. |
