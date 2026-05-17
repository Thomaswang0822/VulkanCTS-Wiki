# imageless_framebuffer

## Overview

The `imageless_framebuffer` category tests the `VK_KHR_imageless_framebuffer` extension, which decouples framebuffer creation from specific image view binding. Framebuffers are created with `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT`, specifying only attachment format and usage constraints via `VkFramebufferAttachmentImageInfo`. Actual image views are provided at render pass begin time through `VkRenderPassAttachmentBeginInfo`.

This category is compact, consisting of a single source file that implements both registration and test logic for six leaf tests covering the major attachment scenarios.

## Registration Entry Point

The category is registered in [vktTestPackage.cpp#L1383](../../modules/vulkan/vktTestPackage.cpp#L1383):

```cpp
addRootChild("imageless_framebuffer", m_caseListFilter, imageless::createTests);
```

The `createTests` function is defined in [vktImagelessFramebufferTests.cpp#L3027-L3041](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L3027-L3041).

## Subgroup Structure

The category has a flat structure with six leaf tests directly under the root group:

```text
imageless_framebuffer
├── color
├── depth_stencil
├── color_resolve
├── depth_stencil_resolve
├── multisubpass
└── different_attachments
```

| Group name | Description |
|---|---|
| `color` | Single-sample color-only imageless framebuffer |
| `depth_stencil` | Color plus combined depth/stencil imageless framebuffer |
| `color_resolve` | 4x multisampled color with resolve attachment |
| `depth_stencil_resolve` | 4x multisampled color, depth, and stencil with resolve attachments |
| `multisubpass` | Two-subpass render pass with input attachment between subpasses |
| `different_attachments` | Same framebuffer used with different image views in separate render passes |

## File Inventory

| File | Role |
|---|---|
| [vktImagelessFramebufferTests.cpp](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp) | Registration and implementation (all tests) |
| [vktImagelessFramebufferTests.hpp](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.hpp) | Header declaring `imageless::createTests` |

## Cross-File Recurring Test Families or Themes

All six tests share a common `BaseTestCase` / `ColorImagelessTestInstance` base class hierarchy and follow the same pattern:

1. Create an imageless framebuffer with `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT`
2. Create image views for the attachments
3. Begin a render pass with `VkRenderPassAttachmentBeginInfo` supplying the image views
4. Render geometry
5. Copy attachment contents to host-visible buffers
6. Compare against procedurally generated reference images

The variation across tests is in the attachment configuration (color-only, depth/stencil, resolve, multi-subpass, different views per render pass).

## Cross-File Recurring Parameter Dimensions

| Parameter | Values |
|---|---|
| `TestType` | 6 enum values covering the attachment scenarios |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` (all tests) |
| Depth/stencil format | `VK_FORMAT_D24_UNORM_S8_UINT` (depth/stencil tests) or `VK_FORMAT_UNDEFINED` |
| Render extent | 32x32 (all tests) |
| Sample count | 1 (non-resolve tests) or 4 (resolve tests) |

## Cross-File Recurring Support Requirements or Feature Gates

| Requirement | Applicable tests |
|---|---|
| `VK_KHR_imageless_framebuffer` extension + `imagelessFramebuffer` feature | All tests |
| `limits.standardSampleLocations == VK_TRUE` | `color_resolve`, `depth_stencil_resolve` |
| `VK_KHR_depth_stencil_resolve` extension | `depth_stencil_resolve` |
| Image format properties support for required usage and extent | All tests (per format) |

## Cross-File Recurring Verification Methods

All tests use **procedural reference image comparison** via `tcu::intThresholdCompare` with a threshold of `tcu::UVec4(1)`. Depth and stencil aspects are converted to a color-compatible format before comparison. Resolve tests additionally verify per-sample values using a demultisample shader pass.

## Links to Level-3 Docs

- [vktImagelessFramebufferTests.cpp](../testfiles/imageless_framebuffer/vktImagelessFramebufferTests.cpp.md)

## Notes on Scope / Uncertainty

- The test plan (`apitests.adoc`) does not contain a dedicated section for this category; all documentation is derived from source code inspection.
- The `VK_KHR_imageless_framebuffer` extension and feature bit checks are performed inside `TestInstance` constructors rather than in `BaseTestCase::checkSupport()`, which only checks `standardSampleLocations` for resolve tests.
