## Overview

**Core question:** Does `VK_KHR_maintenance10` produce the expected single-sample color, depth, or stencil result when a four-sample image is resolved through command, render-pass, or dynamic-rendering operations?

[`vktPipelineMultisampleResolveMaint10Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1) implements the `m10_resolve` test family below `multisample`. It renders deterministic per-sample values, resolves selected image regions, copies the resolved image to host-visible buffers, and compares every checked layer with a host-generated reference.

The split pipeline mustpass files register 2,916 leaves for this family: 1,000 each in `monolithic` and `fast-linked-library`, plus 916 in `shader-object-unlinked-spirv`. The command intermediate node accounts for 832 leaves in each construction root. The render-pass intermediate node has 84 leaves in the first two roots and is absent from the shader-object root; dynamic rendering has 84 leaves in every registered root.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Multisample resolve.** A multisample image retains several samples per pixel; resolve writes one value to a single-sample image. The relevant [command-resolve rules](../../../../vulkan-docs/src/chapters/copies.adoc#vkCmdResolveImage2) define source and destination image regions, while `VkResolveImageModeInfoKHR` selects the resolve mode for non-stencil and stencil values.
- **Maintenance10 extensions.** The [maintenance10 feature](../../../../vulkan-docs/src/chapters/features.adoc#features-maintenance10) adds command-resolve modes and depth/stencil support, and permits control of sRGB transfer-function behavior. The command rules require `average` for non-integer color and `sample_zero` for integer color when a resolve-mode structure is present.
- **Aspect-specific output.** Color, depth, and stencil use separate image aspects. The source checks device-advertised depth and stencil resolve modes before running an applicable case, then reads each selected aspect back independently.

## Registration Hierarchy

```text
pipeline.monolithic.multisample.m10_resolve
├── resolve_cmd
├── render_pass_resolve
└── dynamic_render_resolve
```

[`createMultisampleResolveMaint10Tests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1586-L1810) creates these direct intermediate nodes. [`createMultisampleTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7787-L7791) registers the family only for monolithic, fast-linked-library, and shader-object-unlinked-SPIR-V construction, and excludes the fragment-shading-rate root. `render_pass_resolve` is pruned for shader-object construction.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Resolve intermediate node | `resolve_cmd`, `render_pass_resolve`, `dynamic_render_resolve` | Selects the API mechanism that performs the resolve. | [method registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1591-L1597) |
| Format class | UNORM, UINT, SINT, SFLOAT, sRGB, depth, stencil, and combined depth/stencil entries | Determines output representation, legal aspects, reference calculation, and comparison tolerance. | [format list](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1599-L1660) |
| Resolve aspect | `color`, `depth`, `stencil`, `depth_stencil` | Selects the attachment usage, shader output, resolve properties, copyback buffer, and reference path. | [aspect registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1662-L1671) |
| Resolve mode | `average`, `sample_zero`, `min`, `max` | Selects the host operation used to calculate the expected value for the selected aspect. | [mode registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1673-L1682) |
| Resolve area | `full`, `full_multilayer`, `full_multilayer_rem`, `full_multilayer_rem_single`, `full_3d`, `region`, `regions_multilayer`, `regions_multilayer_rem` | Selects full, layered, 3D, or subregion source-to-destination mapping. | [area registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1684-L1697) |
| sRGB flags | `no_flags`, `enable_transfer`, `skip_transfer` | Selects default behavior or the maintenance10 transfer-function override for applicable sRGB average resolves. | [flag registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1699-L1707) |
| Construction type | `monolithic`, `fast_linked_library`, `shader_object_unlinked_spirv` | Selects a supported pipeline-construction implementation; shader objects omit render-pass cases. | [dispatcher condition](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7787-L7791) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node below `m10_resolve`. Each value selects a different mechanism that must produce the same class of resolved data for its legal parameter combinations.

### resolve_cmd: command-buffer image resolve

This intermediate node records `vkCmdResolveImage2` with one or more `VkImageResolve2` regions and a chained `VkResolveImageModeInfoKHR`. It covers the complete area matrix, including 3D destination slices and subregions. The source uses transfer layouts and explicit barriers before resolving, then copies the destination image to verification buffers.

### render_pass_resolve: render-pass attachment resolve

This intermediate node resolves the multisample attachment through render-pass attachment state. It restricts the matrix to sRGB formats and area forms that fit this path. Shader-object construction cannot use this render-pass path, so registration omits it for that construction type.

### dynamic_render_resolve: dynamic-rendering attachment resolve

This intermediate node supplies the resolve through dynamic-rendering attachment state. It uses the same sRGB-focused scope as the render-pass path, but it remains registered for shader-object construction. The checked result is still a copied single-sample image compared with the host reference.

## Shader Analysis

The source generates a simple vertex shader and a parameterized fragment shader. The vertex shader draws a full-screen triangle and assigns `gl_Layer` for multilayer cases. The fragment shader reads `PixelData` from a storage buffer using `gl_FragCoord`, `gl_Layer`, and `gl_SampleID`, then writes typed color output, `gl_FragDepth`, or `gl_FragStencilRefARB` according to the selected aspects. The test targets resolve and attachment behavior; it does not compare alternative shader algorithms or embed a fixed shader artifact.

## Runtime Execution and Result Checking

- The host checks `VK_KHR_maintenance10`, the method-specific extension, pipeline-construction support, image format support, and depth/stencil resolve properties. Layered paths require Vulkan 1.2 plus `shaderOutputLayer`; sRGB transfer flags require the device property `resolveSrgbFormatSupportsTransferFunctionControl`.
- CTS creates a four-sample 2D source image and a single-sample destination image. A `full_3d` case changes the destination to a 3D image. It fills a host-visible storage buffer with deterministic random per-sample `PixelData`, flushes it, and draws into the multisample attachment.
- The selected area builds one or more `ResolveRegion` mappings. Full-area cases may use explicit layer counts or `VK_REMAINING_ARRAY_LAYERS`; regional command cases move quadrants within or across layers.
- For `resolve_cmd`, CTS transitions the images, builds `VkImageResolve2` entries, chains `VkResolveImageModeInfoKHR`, and calls `vkCmdResolveImage2`. The render-pass and dynamic-rendering paths resolve through their attachment configuration.
- CTS transitions the resolved image to transfer source, copies color, depth, and stencil aspects to separate verification buffers, waits for submission completion, and invalidates host allocations.
- The host reference maps each destination pixel through the first matching resolve region. It selects sample zero, minimum, maximum, or an average as appropriate. It compares integer color and stencil exactly, floating-point color with a format-derived threshold, and depth with a format-specific threshold.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `resolve_cmd` | `vkCmdResolveImage2` region, mode, aspect, layout, or sRGB control is mishandled; source or destination image state may also be wrong. |
| `render_pass_resolve` | Render-pass attachment resolve state or its integration with maintenance10 mode and sRGB control is mishandled. |
| `dynamic_render_resolve` | Dynamic-rendering resolve attachment state or its integration with maintenance10 mode and sRGB control is mishandled. |

### Cause Analysis

#### Command resolve state or region mapping

**Possible failure symptoms:** `resolve_cmd` leaves show mismatches in covered pixels, layers, or moved quadrants, while pixels outside a selected region should retain the zero reference. A mismatch can be limited to `full_3d`, `VK_REMAINING_ARRAY_LAYERS`, or one aspect.

**Possible implementation causes:** The implementation may apply `VkImageResolve2` offsets, extents, base layers, layer counts, image layouts, or resolve modes incorrectly. The final image also includes multisample attachment writes, barriers, the command resolve, copyback, and host comparison, so one mismatch does not identify an exclusive failing stage.

#### Attachment resolve integration

**Possible failure symptoms:** `render_pass_resolve` or `dynamic_render_resolve` differs from the reference for an sRGB leaf, or only one attachment-based mechanism fails while command resolve passes.

**Possible implementation causes:** Render-pass or dynamic-rendering attachment resolve configuration may select the wrong resolve image, mode, aspect, or layout. The source-generated data and final copyback remain shared dependencies, so the result localizes the operation shape rather than proving that attachment resolve alone caused the error.

#### sRGB transfer-function or numerical result

**Possible failure symptoms:** A mismatch is confined to `enable_transfer` or `skip_transfer`, or it occurs only for averaged sRGB or floating-point color. Exact integer color and stencil cases can pass while tolerant color cases fail.

**Possible implementation causes:** The implementation may ignore the maintenance10 transfer flags, use the wrong default from `resolveSrgbFormatAppliesTransferFunction`, convert at the wrong point in averaging, or produce a value beyond the format-derived tolerance. The [resolve rules](../../../../vulkan-docs/src/chapters/copies.adoc#vkCmdResolveImage2) permit implementation-defined numerical precision for calculations over multiple samples, which is why CTS uses format-aware thresholds.

## Case Pruning

### Requirement-based pruning

The source reports not supported when `VK_KHR_maintenance10`, the method-specific extension, format support, sample count, or required depth/stencil resolve modes are unavailable. Depth/stencil cases require `VK_KHR_depth_stencil_resolve`; stencil cases also require `VK_EXT_shader_stencil_export`. A selected sRGB transfer flag requires `resolveSrgbFormatSupportsTransferFunctionControl`. Layered cases require Vulkan 1.2 and `shaderOutputLayer`.

### Design-based pruning

The registration loop rejects aspect and format pairs that do not match, such as color resolve for a depth/stencil format. Integer color retains only `sample_zero`, while floating-point and normalized color retains `average`. Stencil excludes `average`. `full_3d`, `region`, and multi-region areas only apply to `resolve_cmd`; render-pass and dynamic-rendering paths retain sRGB formats because they concentrate on the new transfer flags. `render_pass_resolve` is omitted for shader-object construction.

## Key Takeaways

- `m10_resolve` compares resolved image data with a host model that includes region routing, aspect semantics, resolve mode, and sRGB transfer handling.
- `resolve_cmd` covers the broadest geometry matrix; render-pass and dynamic-rendering paths focus on sRGB transfer-flag behavior.
- The final readback exposes incorrect results, but the shared draw, synchronization, resolve, copyback, and reference path limit fault localization. See [Failure Meaning](#failure-meaning) for operation-shape-specific causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L51-L226) | Defines image shape, sample count, aspects, and image uses. |
| Support checks | [`Maint10ResolveCase::checkSupport`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L273-L390) | Checks extension, property, format, layered-rendering, and resolve-mode requirements. |
| Shader generation | [`Maint10ResolveCase::initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L392-L418) | Generates per-sample color, depth, and stencil writes. |
| Execution and readback | [`Maint10ResolveInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L535-L1581) | Creates resources, resolves images, generates references, and compares results. |
| Matrix registration | [`createMultisampleResolveMaint10Tests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1586-L1810) | Creates methods, formats, aspects, modes, areas, and sRGB flags. |
| Parent registration | [`createMultisampleTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7787-L7791) | Limits supported construction types and fragment-shading-rate use. |
| Maintenance10 contract | [Maintenance10 feature](../../../../vulkan-docs/src/chapters/features.adoc#features-maintenance10) | Defines the feature's resolve additions. |
| Resolve command contract | [Resolve image commands](../../../../vulkan-docs/src/chapters/copies.adoc#vkCmdResolveImage2) | Defines `VkResolveImageInfo2`, modes, aspects, sRGB control, and valid usage. |
