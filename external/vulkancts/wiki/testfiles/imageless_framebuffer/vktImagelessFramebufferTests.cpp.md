# vktImagelessFramebufferTests.cpp

## Overview

This file implements the entire `imageless_framebuffer` test category, verifying the `VK_KHR_imageless_framebuffer` extension. The extension allows framebuffers to be created without specifying image views at framebuffer creation time; instead, image views are provided at render pass begin time via `VkRenderPassAttachmentBeginInfo`.

The file serves as both the **registration file** and the **implementation file** for the category. It defines a single `BaseTestCase` class with six test-type variants, each dispatched to a dedicated `TestInstance` subclass.

## Source Code

- [vktImagelessFramebufferTests.cpp](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp)
- [vktImagelessFramebufferTests.hpp](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.hpp)

## Other Inspected Related Files

- [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1383) -- root registration: `addRootChild("imageless_framebuffer", ...)`

## Registration Hierarchy

```text
imageless_framebuffer
├── color
├── depth_stencil
├── color_resolve
├── depth_stencil_resolve
├── multisubpass
└── different_attachments
```

The `createTests` function ([vktImagelessFramebufferTests.cpp#L3027-L3041](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L3027-L3041)) creates a `TestCaseGroup` named after the `name` parameter and adds six children. Each child is a single `BaseTestCase` leaf (not a subgroup), constructed by helper functions that specify the test type and format parameters:

| Child name | Helper function | Group name line |
|---|---|---|
| `color` | `imagelessColorTests` | [L2962](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2962) |
| `depth_stencil` | `imagelessDepthStencilTests` | [L2974](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2974) |
| `color_resolve` | `imagelessColorResolveTests` | [L2986](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2986) |
| `depth_stencil_resolve` | `imagelessDepthStencilResolveTests` | [L2998](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2998) |
| `multisubpass` | `imagelessMultisubpass` | [L3010](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L3010) |
| `different_attachments` | `imagelessDifferentAttachments` | [L3022](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L3022) |

## Test Families

### color -- Color-only imageless framebuffer

Renders a single-subpass, single-sample color attachment using an imageless framebuffer. The framebuffer is created with `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT` ([L699](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L699)), and image views are supplied at `beginRenderPass` via `VkRenderPassAttachmentBeginInfo` ([L1273-L1278](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1273-L1278)).

Dispatched to `ColorImagelessTestInstance` ([L2932-L2933](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2932-L2933)).

Parameters: `TEST_TYPE_COLOR`, color format `VK_FORMAT_R8G8B8A8_UNORM`, depth/stencil format `VK_FORMAT_UNDEFINED`.

### depth_stencil -- Color plus depth/stencil imageless framebuffer

Extends the color test by adding a combined depth/stencil attachment (`VK_FORMAT_D24_UNORM_S8_UINT`). Verifies that color, depth, and stencil aspects all render correctly through the imageless framebuffer path.

Dispatched to `DepthImagelessTestInstance` ([L2935-L2936](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2935-L2936)), which inherits from `ColorImagelessTestInstance`.

Parameters: `TEST_TYPE_DEPTH_STENCIL`, color format `VK_FORMAT_R8G8B8A8_UNORM`, depth/stencil format `VK_FORMAT_D24_UNORM_S8_UINT`.

### color_resolve -- Multisample color with resolve attachment

Uses a 4x multisampled color attachment with a resolve attachment. After rendering, verifies both the resolved image and each individual sample of the multisampled image using a demultisample shader pass.

Dispatched to `ColorResolveImagelessTestInstance` ([L2938-L2939](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2938-L2939)).

Parameters: `TEST_TYPE_COLOR_RESOLVE`, color format `VK_FORMAT_R8G8B8A8_UNORM`, depth/stencil format `VK_FORMAT_UNDEFINED`, sample count `VK_SAMPLE_COUNT_4_BIT` ([L1692](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1692)).

### depth_stencil_resolve -- Multisample depth/stencil with resolve

Combines multisampled color, depth, and stencil attachments with resolve attachments. Verifies resolved color, resolved depth, resolved stencil, and per-sample values of the multisampled images. Uses `VK_KHR_depth_stencil_resolve` with `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` for both depth and stencil resolve modes ([L342-L343](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L342-L343)).

Dispatched to `DepthResolveImagelessTestInstance` ([L2941-L2942](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2941-L2942)).

Parameters: `TEST_TYPE_DEPTH_STENCIL_RESOLVE`, color format `VK_FORMAT_R8G8B8A8_UNORM`, depth/stencil format `VK_FORMAT_D24_UNORM_S8_UINT`, sample count 4 ([L1982-L1983](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1982-L1983)).

### multisubpass -- Multi-subpass with input attachment

Uses a render pass with two subpasses. Subpass 0 renders to a color attachment; subpass 1 reads that attachment as an input attachment and renders to a second color attachment. Both subpasses share the same imageless framebuffer.

Dispatched to `MultisubpassTestInstance` ([L2944-L2945](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2944-L2945)).

Parameters: `TEST_TYPE_MULTISUBPASS`, color format `VK_FORMAT_R8G8B8A8_UNORM`, depth/stencil format `VK_FORMAT_UNDEFINED`.

### different_attachments -- Different image views across render passes

Creates an imageless framebuffer with a single attachment slot, then uses it in two separate render passes with different image views bound via `VkRenderPassAttachmentBeginInfo`. Verifies that each render pass correctly renders to its own image view.

Dispatched to `DifferentAttachmentsTestInstance` ([L2947-L2948](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2947-L2948)).

Parameters: `TEST_TYPE_DIFFERENT_ATTACHMENTS`, color format `VK_FORMAT_R8G8B8A8_UNORM`, depth/stencil format `VK_FORMAT_UNDEFINED`.

## Parameter Dimensions and Observed Values

| Parameter | Values | Source |
|---|---|---|
| `TestType testType` | `TEST_TYPE_COLOR`, `TEST_TYPE_DEPTH_STENCIL`, `TEST_TYPE_COLOR_RESOLVE`, `TEST_TYPE_DEPTH_STENCIL_RESOLVE`, `TEST_TYPE_MULTISUBPASS`, `TEST_TYPE_DIFFERENT_ATTACHMENTS` | [L60-L69](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L60-L69) |
| `VkFormat colorFormat` | `VK_FORMAT_R8G8B8A8_UNORM` (all tests) | [L2957](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2957) |
| `VkFormat dsFormat` | `VK_FORMAT_D24_UNORM_S8_UINT` (depth/stencil tests) or `VK_FORMAT_UNDEFINED` (color-only tests) | [L2958](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2958), [L2970](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2970) |
| Render extent | 32x32 (all tests) | [L956](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L956) |
| Sample count | 1 (non-resolve tests) or 4 (resolve tests) | [L1444](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1444), [L1692](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1692) |

## Support / Feature Requirements

| Requirement | Applicable tests | Source |
|---|---|---|
| `VK_KHR_imageless_framebuffer` device extension | All tests | [L955](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L955) |
| `imagelessFramebuffer` feature bit must be `VK_TRUE` | All tests | [L966-L967](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L966-L967) |
| `limits.standardSampleLocations` must be `VK_TRUE` | `color_resolve`, `depth_stencil_resolve` | [L2717-L2721](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2717-L2721) |
| `VK_KHR_depth_stencil_resolve` device extension | `depth_stencil_resolve` | [L1838](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1838) |
| Image format properties must support required usage flags and extent | All tests (checked per format) | [L845-L868](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L845-L868) |

## Verification Methods

All tests use **procedural reference image comparison** as the primary verification method:

1. **Reference image generation**: Each `TestInstance` subclass implements `generateReferenceImage()` which produces a `tcu::TextureLevel` with the expected pixel values based on the vertex geometry and test type.

2. **Pixel comparison via `tcu::intThresholdCompare`**: The `verifyBufferInternal()` method ([L1114-L1133](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1114-L1133)) first performs a fast `deMemCmp`. If the result differs from the reference, it falls back to `tcu::intThresholdCompare` with a threshold of `tcu::UVec4(1)`, allowing a tolerance of 1 in each unsigned integer channel.

3. **Depth/stencil conversion**: For depth and stencil aspects, the raw buffer data is converted to a color-compatible format before comparison:
   - Depth: `convertDepthToColor()` ([L883-L901](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L883-L901)) maps depth values to grayscale.
   - Stencil: `convertStencilToColor()` ([L903-L922](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L903-L922)) maps stencil values to grayscale.

4. **Per-sample verification** (resolve tests only): For multisampled resolve tests, each individual sample is extracted from the multisampled image using a demultisample shader pass (`readOneSampleFromMultisampleImage()`, [L972-L1024](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L972-L1024)) and compared against a per-sample reference image.

## Test Principles Observed

- **Imageless framebuffer creation**: All framebuffers are created with `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT` and `pAttachments = nullptr` in `VkFramebufferCreateInfo` ([L696-L708](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L696-L708)). Attachment image info is provided via `VkFramebufferAttachmentsCreateInfo` in the `pNext` chain.
- **Deferred image view binding**: Image views are supplied at `beginRenderPass` time via `VkRenderPassAttachmentBeginInfo` rather than at framebuffer creation.
- **Attachment image info consistency**: `VkFramebufferAttachmentImageInfo` structs specify the usage, extent, and format constraints that the actual image views must satisfy.
- **Coverage of attachment types**: The six test types systematically cover color-only, depth/stencil, color resolve, depth/stencil resolve, multi-subpass (input attachment), and different-attachments-per-render-pass scenarios.

## Notes / Uncertainties

- The test plan file (`apitests.adoc`) does not contain a dedicated section for `imageless_framebuffer`, so all claims are derived solely from source code inspection.
- All tests use a fixed render extent of 32x32 pixels; no parameterization over image sizes is present in the inspected code.
- The `TestType` enum has a `TEST_TYPE_LAST` sentinel ([L68](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L68)) that is not used as a test type.
- The `checkSupport` method in `BaseTestCase` ([L2715-L2722](../../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2715-L2722)) only checks `standardSampleLocations` for resolve tests; the `VK_KHR_imageless_framebuffer` extension and feature bit checks happen inside the `TestInstance` constructors rather than in `checkSupport`.
