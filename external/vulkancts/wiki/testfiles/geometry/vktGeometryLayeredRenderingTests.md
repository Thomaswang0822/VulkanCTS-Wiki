# vktGeometryLayeredRenderingTests.cpp

## Overview

[`vktGeometryLayeredRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1) implements layered geometry-shader rendering tests. In the inspected code, the file exercises directing geometry output to default or selected layers, writing to all layers, varying content by layer, using one invocation per layer or multiple layers per invocation, verifying fragment-stage [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1191), performing layered readback checks, and testing a secondary-command-buffer path.

## Role

Implementation file.

## Source Code

- Primary source: [`vktGeometryLayeredRenderingTests.cpp`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1)
- Shared context/framework conventions: [`vkt::TestCase`](../../modules/vulkan/vktTestCase.hpp:277), [`tcu::TestStatus`](../../../framework/common/tcuTestCase.hpp:253)

## Registration Path

This file defines layered behavior through the [`TestType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:62) model and generates programs/tests from [`initPrograms()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:850) and [`test()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1223). The geometry category attaches the layered subgroup through [`createLayeredRenderingTests()`](../../modules/vulkan/geometry/vktGeometryTests.cpp:47). The actual factory body was not included in the inspected snippet set, so the documented hierarchy below is derived from the observed [`TestType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:62) cases and verification code.

## Test Hierarchy

Observed subgroup themes from [`TestType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:62):

```text
layered
├── default-layer rendering
├── single-layer rendering
├── all-layers rendering
├── different-content-per-layer
├── layer-id verification
├── invocation-per-layer
├── multiple-layers-per-invocation
├── layered-readback
└── secondary-command-buffer path
```

This is a semantic hierarchy derived from the inspected enum and program-generation branches, not a verbatim registration tree dump.

## Test Families

### 1. Default-layer and single-layer targeting

[`TEST_TYPE_DEFAULT_LAYER`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:64) emits geometry without assigning [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:920), while [`TEST_TYPE_SINGLE_LAYER`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:65) explicitly targets the middle layer computed by [`getTargetLayer()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:107) and written in the geometry program at [`gl_Layer = targetLayer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:943).

### 2. All-layer rendering

[`TEST_TYPE_ALL_LAYERS`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:66) iterates over all layers and assigns a per-layer color chosen from [`s_colors`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:89), emitted in the geometry shader loop at [`layerNdx`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:965).

### 3. Different content per layer

[`TEST_TYPE_DIFFERENT_CONTENT`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:67) draws layer-specific bar widths by looping over both [`layerNdx`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1021) and [`colNdx`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1022), yielding progressively wider coverage for later layers.

### 4. Fragment-stage layer-id verification

[`TEST_TYPE_LAYER_ID`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:68) writes all layers from the geometry shader and then colors fragments according to fragment-stage [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1191). Verification expects the fragment code and the CPU-side checker to stay in sync, as called out in [`verifyLayerContent()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:721).

### 5. Invocation distribution across layers

[`TEST_TYPE_INVOCATION_PER_LAYER`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:69) uses [`layout(points, invocations = numLayers)`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:892), then maps [`gl_InvocationID`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1040) directly to [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1044).

[`TEST_TYPE_MULTIPLE_LAYERS_PER_INVOCATION`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:70) instead makes each invocation write to two target layers, [`layerA`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1070) and [`layerB`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1071).

### 6. Layered readback

[`TEST_TYPE_LAYERED_READBACK`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:71) uses an input uniform block [`uInput.pass`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:886) and per-pass depth/color behavior in the generated geometry shader at [`posZ`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1114). CPU-side validation distinguishes color, depth, and stencil readback in [`verifyLayerContent()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:727).

### 7. Secondary command buffer path

[`TEST_TYPE_SECONDARY_CMD_BUFFER`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:72) combines layered rendering with image load/store in the fragment shader using a bound [`storageImage`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1182) and blends [`vert_color`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1209) with the existing layer content.

## Parameter Dimensions

| Parameter | Observed values / source |
|---|---|
| Test behavior | [`TestType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:62) |
| Image-view type | [`VkImageViewType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:77), with handling for 1D-array, 2D-array, cube, cube-array, and 3D in [`getImageType()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:121) and fragment-image-type selection at [`imageViewString`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1154) |
| Image extent | [`VkExtent3D size`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:78) |
| Number of layers | [`numLayers`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:79) and derived layer count for 3D views at [`numLayers`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:870) |
| Framebuffer inheritance flag | [`inheritFramebuffer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:86) |
| Layer target | Middle layer via [`getTargetLayer()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:107) or per-invocation/per-loop layer selection in the generated geometry code |
| Verification mode for readback | color / depth / stencil paths in [`verifyLayerContent()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:727) |

## Support / Feature Requirements

The inspected snippets show several capability-dependent paths, but the dedicated support-check function was not included in the inspected range. Evidence from the file still shows requirements coupled to:
- layered image/view compatibility via [`checkImageFormatProperties()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:161)
- cube and 3D compatibility handling in [`isCubeImageViewType()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:156) and image-create flags in [`test()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1244)
- invocation-count-dependent shader generation for per-layer invocation modes in [`initPrograms()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:890)

Because the explicit `checkSupport()` function was not part of the inspected snippet set, this document avoids making stronger claims about exact feature gates beyond what is directly visible.

## Verification Methods

This file contains extensive file-local verification code.

### Layer-content verification helpers

- [`verifyImageSingleColoredRow()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:451) checks a filled bar against a target color with thresholds and an error mask
- [`verifyImageMultipleBars()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:524) checks multiple x-axis regions against expected values
- [`verifyEmptyImage()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:660) ensures a layer remains background-colored

### Per-layer semantic verification

[`verifyLayerContent()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:687) selects the expected rule by [`TestType`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:694), including:
- empty-vs-populated layer checks for default/single-layer cases
- per-layer color validation for all-layer and invocation-per-layer cases
- width-varying bar checks for different-content cases
- [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:722)-derived fragment colors for layer-id cases
- multi-bar color/depth/stencil validation for layered-readback cases
- blended expected colors for secondary-command-buffer cases

### Whole-result verification

[`verifyResults()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:817) wraps the per-layer checks by creating a uniform layer-access abstraction through [`LayeredImageAccess`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:395) and iterating through all layers/slices.

## Test Principles Observed

- **Layer semantics are validated explicitly**: tests do not stop at successful rendering; they check exact per-layer content in CPU-side validators
- **Geometry and fragment cooperation is tested**: the category includes both geometry-side [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:943) assignment and fragment-side [`gl_Layer`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:1191) consumption
- **Image-view diversity matters**: the file is structured around 1D/2D/cube/3D view handling rather than a single image shape
- **Readback paths are part of coverage**: layered-readback tests verify not only color but also depth and stencil representations via [`convertDepthToColorBufferAccess()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:633) and [`convertStencilToColorBufferAccess()`](../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp:646)

## Notes / Uncertainties

- The exact user-visible case names are not reconstructed here because the factory function that registers the individual layered cases was not part of the inspected snippet set.
- The documented family structure is therefore evidence-backed at the semantic/test-type level rather than as a complete emitted case-name list.
