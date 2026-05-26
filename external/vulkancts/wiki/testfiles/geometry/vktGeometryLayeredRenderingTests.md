# vktGeometryLayeredRenderingTests.cpp

## Overview

[`vktGeometryLayeredRenderingTests.cpp`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1) implements layered geometry-shader rendering tests. In the inspected code, the file exercises directing geometry output to default or selected layers, writing to all layers, varying content by layer, using one invocation per layer or multiple layers per invocation, verifying fragment-stage [`gl_Layer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1191), performing layered readback checks, and testing a secondary-command-buffer path.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryLayeredRenderingTests.cpp`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1)
- Shared context/framework conventions: [`vkt::TestCase`](../../../modules/vulkan/vktTestCase.hpp#L277), [`tcu::TestStatus`](../../../../../framework/common/tcuTestCase.hpp#L253)

## Registration Hierarchy

This file contributes the `layered` subgroup returned by [`createLayeredRenderingTests()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1996), which is attached under geometry by [`createChildren()`](../../../modules/vulkan/geometry/vktGeometryTests.cpp#L47). The inspected factory implementation registers five direct child groups by view type at [`getShortImageViewTypeName()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2041), then adds concrete size groups and test cases beneath each view-type group at [`viewTypeGroup`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2052) and [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2059).

```text
geometry.layered
├── 1d_array
├── 2d_array
├── cube
├── cube_array
└── 3d
```

## Test Families

### 1d_array — 1D-array layered rendering cases

The [`1d_array`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2041) subgroup is created from [`VK_IMAGE_VIEW_TYPE_1D_ARRAY`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2028). Under that direct child, the factory creates two size groups — [`64_1_4`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2046) and [`12_1_6`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2046) — then registers the full layered behavior set defined by [`testTypes[]`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2000).

### 2d_array — 2D-array layered rendering cases

The [`2d_array`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2041) subgroup is created from [`VK_IMAGE_VIEW_TYPE_2D_ARRAY`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2030). It likewise contains two size groups — [`64_64_4`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2046) and [`12_36_6`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2046) — and each size group receives the same layered test-name set from [`testTypes[]`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2000).

### cube — Cube layered rendering cases

The [`cube`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2041) subgroup is created from [`VK_IMAGE_VIEW_TYPE_CUBE`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2032). The factory builds size groups [`64_64_6`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2046) and [`36_36_6`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2046), then registers the layered behavior families beneath each one.

### cube_array — Cube-array layered rendering cases

The [`cube_array`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2041) subgroup is created from [`VK_IMAGE_VIEW_TYPE_CUBE_ARRAY`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2034). Its two direct size groups are [`64_64_12`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2046) and [`36_36_12`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2046), after which the same behavior family names are registered from [`testTypes[]`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2000).

### 3d — 3D layered rendering cases

The [`3d`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2041) subgroup is created from [`VK_IMAGE_VIEW_TYPE_3D`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2036). Its two direct size groups are [`64_64_8`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2048) and [`12_36_6`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2048), and the full test-name set is registered under each one via [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2059).

Across all five direct children, the concrete per-size behavior set comes from [`testTypes[]`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2000):
- [`render_to_default_layer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2005)
- [`render_to_one`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2007)
- [`render_to_all`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2009)
- [`render_different_content`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2011)
- [`fragment_layer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2013)
- [`invocation_per_layer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2015)
- [`multiple_layers_per_invocation`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2017)
- [`readback`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2019)
- [`secondary_cmd_buffer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2021)
- [`secondary_cmd_buffer_inherit_framebuffer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2067) for the secondary-command-buffer mode only

Semantically, those registered names correspond to the following behavior families implemented by [`TestType`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L62):
- default-layer and single-layer targeting
- all-layer rendering
- different content per layer
- fragment-stage `gl_Layer` verification
- one invocation per layer and multiple layers per invocation
- layered readback validation
- secondary command buffer execution

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Test behavior | [`TestType`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L62) and registered names in [`testTypes[]`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2000) |
| Image-view type | [`VK_IMAGE_VIEW_TYPE_1D_ARRAY`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2028), [`VK_IMAGE_VIEW_TYPE_2D_ARRAY`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2030), [`VK_IMAGE_VIEW_TYPE_CUBE`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2032), [`VK_IMAGE_VIEW_TYPE_CUBE_ARRAY`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2034), [`VK_IMAGE_VIEW_TYPE_3D`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2036) |
| Image extent | [`VkExtent3D size`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L78) values in [`imageParams`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2026) |
| Number of layers | [`numLayers`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L79) from [`imageParams`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2026), with 3D depth used instead for 3D subgroup-name synthesis at [`viewTypeGroupName`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2048) |
| Size-group names | Generated from width / height / depth-or-layer-count at [`viewTypeGroupName`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2045) |
| Framebuffer inheritance flag | [`inheritFramebuffer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L86), toggled for the extra secondary-command-buffer case at [`params.inheritFramebuffer = true`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2066) |
| Layer target | Middle layer via [`getTargetLayer()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L107) or per-invocation/per-loop layer selection in the generated geometry code |
| Verification mode for readback | color / depth / stencil paths in [`verifyLayerContent()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L727) |

## Support / Feature Requirements

Explicit support checking is implemented in [`checkSupport()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1965). The inspected function shows requirements coupled to:
- core geometry-shader support via [`context.requireDeviceCoreFeature(DEVICE_CORE_FEATURE_GEOMETRY_SHADER)`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1967)
- 3D image-view cases, which require [`VK_KHR_maintenance1`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1971) and reject portability-subset implementations without [`imageView2DOn3DImage`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1975)
- secondary-command-buffer cases requiring [`DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1985)
- Vulkan SC secondary-command-buffer framebuffer restrictions in [`secondaryCommandBufferNullOrImagelessFramebuffer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1988)

The layered readback execution path separately checks depth/stencil image format properties at runtime via [`checkImageFormatProperties()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1367) before creating the depth/stencil image.

## Verification Methods

This file contains extensive file-local verification code.

### Layer-content verification helpers

- [`verifyImageSingleColoredRow()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L451) checks a filled bar against a target color with thresholds and an error mask
- [`verifyImageMultipleBars()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L524) checks multiple x-axis regions against expected values
- [`verifyEmptyImage()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L660) ensures a layer remains background-colored

### Per-layer semantic verification

[`verifyLayerContent()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L687) selects the expected rule by [`TestType`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L694), including:
- empty-vs-populated layer checks for default and single-layer cases
- per-layer color validation for all-layer and invocation-per-layer cases
- width-varying bar checks for different-content cases
- [`gl_Layer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L722)-derived fragment colors for layer-id cases
- multi-bar color, depth, and stencil validation for layered-readback cases
- blended expected colors for secondary-command-buffer cases

### Whole-result verification

[`verifyResults()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L817) wraps the per-layer checks by creating a uniform layer-access abstraction through [`LayeredImageAccess`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L395) and iterating through all layers and slices.

## Test Principles Observed

- **Layer semantics are validated explicitly**: tests do not stop at successful rendering; they check exact per-layer content in CPU-side validators
- **Geometry and fragment cooperation is tested**: the file includes both geometry-side [`gl_Layer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L943) assignment and fragment-side [`gl_Layer`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1191) consumption
- **Image-view diversity matters**: the file is structured around 1D-array, 2D-array, cube, cube-array, and 3D view handling rather than a single image shape
- **Readback paths are part of coverage**: layered-readback tests verify not only color but also depth and stencil representations via [`convertDepthToColorBufferAccess()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L633) and [`convertStencilToColorBufferAccess()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L646)

## Notes / Uncertainties

- The direct child names in `## Registration Hierarchy` are confirmed from [`getShortImageViewTypeName()`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2041); deeper generated size groups and per-case registrations are described in prose rather than in the parseable tree.
- The documented semantic families correspond to registered test names through [`testTypes[]`](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L2000), but the page does not expand every generated size-group subtree as a separate parseable hierarchy because the canonical contract limits the tree to one level below the Level-3 root.
