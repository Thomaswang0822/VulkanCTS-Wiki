# Fragment Shading Rate

This page summarizes the Vulkan CTS `fragment_shading_rate` category, which verifies `VK_KHR_fragment_shading_rate` behavior across render-pass and dynamic-rendering paths, pipeline construction types, attachment-driven rates, primitive/pipeline rate interactions, pixel consistency, and selected edge cases.

## Registration Entry Point

The category root is created by [`FragmentShadingRate::createTests()`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L629-L650). It unconditionally registers `renderpass2` and conditionally registers `dynamic_rendering` outside Vulkan SC builds at [`vktFragmentShadingRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L634-L648).

## Subgroup Structure

```text
fragment_shading_rate
├── renderpass2
└── dynamic_rendering (non-VulkanSC only)
```

## File Inventory

| File | Role | Wiki page |
|---|---|---|
| [`vktFragmentShadingRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L1) | Root dispatcher plus property/misc tests | [`vktFragmentShadingRateTests.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRateTests.md) |
| [`vktFragmentShadingRateBasic.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L1) | Large generated basic-family contributor | [`vktFragmentShadingRateBasic.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRateBasic.md) |
| [`vktAttachmentRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L1) | Registered `attachment_rate` branch | [`vktAttachmentRateTests.cpp`](../testfiles/fragment_shading_rate/vktAttachmentRateTests.md) |
| [`vktFragmentShadingRatePixelConsistency.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L1) | Registered `pixel_consistency` branch | [`vktFragmentShadingRatePixelConsistency.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.md) |
| [`vktFragmentShadingRateMiscTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1) | Additional tests under `misc` | [`vktFragmentShadingRateMiscTests.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRateMiscTests.md) |
| [`vktFragmentShadingRateGroupParams.hpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateGroupParams.hpp#L34-L50) | Shared parameter structure | Header-only helper; no Level-3 page |
| [`CMakeLists.txt`](../../modules/vulkan/fragment_shading_rate/CMakeLists.txt#L1) | Build inventory | Build metadata |

## Cross-File Test Themes

The category combines a high-level rendering/pipeline permutation tree with several implementation contributors:

- [`vktFragmentShadingRateBasic.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRateBasic.md) contributes the broad matrix of basic, sample-mask, depth/stencil, layered, multiview, interlock, sample-location, multipass, and maintenance families through [`createBasicTests()`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L3594-L4085).
- [`vktAttachmentRateTests.cpp`](../testfiles/fragment_shading_rate/vktAttachmentRateTests.md) contributes the `attachment_rate` branch for attachment setup modes, shading-rate attachment formats, and fragment sizes at [`vktAttachmentRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2539-L2753).
- [`vktFragmentShadingRatePixelConsistency.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.md) contributes `pixel_consistency` only for the renderpass2 monolithic path, as selected by the parent dispatcher at [`vktFragmentShadingRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L550-L556).
- [`vktFragmentShadingRateMiscTests.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRateMiscTests.md) contributes edge cases under `misc`, with different children depending on dynamic-rendering mode at [`vktFragmentShadingRateMiscTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L1497-L1530).

## Cross-File Parameter Dimensions

Recurring dimensions include rendering path (`renderpass2` versus non-SC `dynamic_rendering`), command-buffer containment mode for dynamic rendering, pipeline construction type, dynamic versus static shading-rate state, attachment usage, shader-written primitive rate, combiner operations, framebuffer extent, sample count, shader stage path, attachment setup mode, attachment format, and reported fragment size. The top-level and pipeline dimensions are visible in [`vktFragmentShadingRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L559-L650), the shared-parameter fields are defined in [`vktFragmentShadingRateGroupParams.hpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateGroupParams.hpp#L34-L50), and the large basic/attachment/pixel value tables are in their respective Level-3 pages.

The mustpass file confirms generated paths beginning with `dynamic_rendering.complete_secondary_cmd_buff...` at [`fragment-shading-rate.txt`](../../mustpass/main/vk-default/fragment-shading-rate.txt#L1-L24), matching the dynamic-rendering command-buffer subtree in the registration source.

## Cross-File Support Requirements and Feature Gates

The common baseline is `VK_KHR_fragment_shading_rate`, required by category-level checks and implementation cases. Specific cases add support requirements for `pipelineFragmentShadingRate`, `primitiveFragmentShadingRate`, `attachmentFragmentShadingRate`, dynamic rendering, imageless framebuffers, format/rate support, robustness/image-robustness behavior, maintenance extensions, and feature-specific interactions such as interlock or custom sample locations. Examples include property-test support at [`vktFragmentShadingRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L509-L512), attachment-rate support checks at [`vktAttachmentRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2336-L2391), pixel-consistency support checks at [`vktFragmentShadingRatePixelConsistency.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L160-L184), and misc support helpers at [`vktFragmentShadingRateMiscTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L83-L108).

## Cross-File Verification Methods

Verification is branch-specific:

| Pattern | Evidence |
|---|---|
| Property/list validation | `testLimits()` and `testShadingRates()` return fail on invalid property or rate-list relationships at [`vktFragmentShadingRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateTests.cpp#L280-L425) |
| Rendered color/depth/stencil readback | Basic cases scan copied results, simulated expected rate masks, depth/stencil values, layer/multiview routing, and per-fragment consistency at [`vktFragmentShadingRateBasic.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateBasic.cpp#L2641-L2920) |
| Attachment-rate behavior | Attachment-rate tests prepare shading-rate attachments via registered setup modes and validate resulting fragment-rate behavior; setup/rate axes are registered at [`vktAttachmentRateTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktAttachmentRateTests.cpp#L2539-L2673) |
| Pixel consistency | Pixel-consistency tests scan copied pixels and require consistent values within fragment-sized regions, with explicit boundary handling at [`vktFragmentShadingRatePixelConsistency.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.cpp#L359-L425) |
| Misc depth comparison | One misc path uses `tcu::dsThresholdCompare` against generated expected depth values at [`vktFragmentShadingRateMiscTests.cpp`](../../modules/vulkan/fragment_shading_rate/vktFragmentShadingRateMiscTests.cpp#L719-L736) |

## Level-3 Pages

- [`vktFragmentShadingRateTests.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRateTests.md)
- [`vktFragmentShadingRateBasic.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRateBasic.md)
- [`vktAttachmentRateTests.cpp`](../testfiles/fragment_shading_rate/vktAttachmentRateTests.md)
- [`vktFragmentShadingRatePixelConsistency.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRatePixelConsistency.md)
- [`vktFragmentShadingRateMiscTests.cpp`](../testfiles/fragment_shading_rate/vktFragmentShadingRateMiscTests.md)

## Notes / Scope

No direct test-plan match was used. The documented Vulkan SC conditionality follows the inspected source guards: root `dynamic_rendering`, pipeline-library construction permutations, mesh shader paths, and several named families are non-Vulkan SC only.
