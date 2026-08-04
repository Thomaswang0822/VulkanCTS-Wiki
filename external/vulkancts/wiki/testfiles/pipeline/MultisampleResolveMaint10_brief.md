# Understanding Brief: MultisampleResolveMaint10

## One-Sentence Test Purpose

This test checks whether Vulkan resolves four-sample color, depth, and stencil images correctly through command, render-pass, and dynamic-rendering paths introduced or extended by `VK_KHR_maintenance10`.

## Background Knowledge

A multisample image stores several values for one pixel. A resolve produces one value by selecting a sample or combining the samples with a resolve mode such as average, minimum, or maximum. Color integer formats use sample zero in this family, while floating-point and normalized color formats use average.

`VK_KHR_maintenance10` adds resolve-mode and depth/stencil support to `vkCmdResolveImage2`, and it allows an implementation to expose control over the transfer-function handling of sRGB resolves. The same resolve concept also appears in render-pass and dynamic-rendering attachment state. A resolve region maps a source rectangle and layer range to a destination rectangle and layer range; `VK_REMAINING_ARRAY_LAYERS` tests the special layer-count value rather than a fixed count.

Depth and stencil are separate aspects of a depth/stencil format. Their supported resolve modes come from `VkPhysicalDeviceDepthStencilResolveProperties`. Stencil values in this test come from shader stencil export, so the stencil path also depends on `VK_EXT_shader_stencil_export`.

## One Concrete Example

A representative command leaf is `pipeline.monolithic.m10_resolve.resolve_cmd.r8g8b8a8_unorm.color.average.region.no_flags`. CTS creates a 16 by 16 four-sample source image, fills each sample with deterministic random data, and resolves the top-left quadrant into the bottom-right quadrant of a single-sample image. The host applies the same coordinate mapping and averages the four source samples for every destination pixel covered by the region. After the command completes, CTS copies the destination image to a host-visible buffer and compares it with that reference.

## End-to-End Test Flow

```text
[host] select construction type, resolve method, format, aspect, mode, area, and sRGB flags
[host] check maintenance10, method-specific, depth/stencil, format, layer, and pipeline requirements
[host] create a 4-sample source image, a single-sample destination image, views, buffers, descriptors, and graphics pipeline
[device] render deterministic per-sample color, depth, or stencil values
[device] resolve the selected full or regional image ranges with the selected method and mode
[device] copy resolved aspects to verification buffers and signal host visibility
[host] generate the matching reference, compare every layer, and return pass or failure
```

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Created/configured by host? | Used by device? | Read by host? | Why it matters |
|---|---:|---:|---:|---|
| Four-sample source image and view | yes | color or depth/stencil attachment | no, except through resolve | Holds distinct deterministic values for each sample. |
| Single-sample destination image and view | yes | resolve destination and transfer source | copied to buffers | Contains the result whose resolve semantics are checked. |
| `PixelValuesBlock` storage buffer | yes | fragment shader input | no | Supplies per-pixel, per-sample values to the shader. |
| Generated vertex and fragment shaders | yes | graphics draw | no | Write the selected color, depth, and stencil aspects. |
| `VkResolveImageInfo2` and `VkResolveImageModeInfoKHR` | yes | command resolve | no | Carry regions, resolve modes, and sRGB transfer flags. |
| Color, depth, and stencil verification buffers | yes | transfer destinations | yes | Provide host-readable copies for comparison. |
| Host-generated reference textures | yes | no | yes | Model region mapping and the selected resolve operation. |

## What Is Checked

The host reference leaves pixels outside the selected regions at zero. For covered pixels it uses sample zero for integer color and the selected depth or stencil mode. For floating-point and normalized color, it averages four samples and handles sRGB transfer behavior according to the selected flag and the device's `resolveSrgbFormatAppliesTransferFunction` property. Integer color and stencil results require exact comparison. Floating-point color uses a format-derived threshold, and depth uses a format-specific depth threshold.

## Important Variations and Special Cases

- `resolve_cmd` exercises `vkCmdResolveImage2` and all eight area forms, including 3D destination slices and multi-region mappings. It is the only method with sub-area and 3D cases.
- `render_pass_resolve` and `dynamic_render_resolve` use only sRGB formats and full-image or layered areas. The render-pass family is omitted for shader-object construction.
- Color uses `average` for floating-point or normalized formats and `sample_zero` for integer formats. Depth supports all four registered modes when the device advertises them. Stencil excludes `average` during registration.
- Layered cases require Vulkan 1.2 and `shaderOutputLayer`. The 3D destination case uses one destination slice and is restricted to command resolve.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `resolve_cmd` | `vkCmdResolveImage2` region, mode, aspect, layout, or sRGB control is mishandled; source or destination image state may also be wrong. |
| `render_pass_resolve` | Render-pass attachment resolve state or its integration with maintenance10 mode and sRGB control is mishandled. |
| `dynamic_render_resolve` | Dynamic-rendering resolve attachment state or its integration with maintenance10 mode and sRGB control is mishandled. |

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter definitions and image setup | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L51-L226) | Defines sample count, extents, image types, aspects, and usages. |
| Support checks and generated shaders | [`checkSupport` and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L273-L418) | Shows feature requirements and shader inputs. |
| Region mapping and deterministic samples | [`resolveRegions` and sample generation](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L577-L755) | Defines the expected source-to-destination mappings. |
| Resolve command and transfer flags | [`VkResolveImageInfo2` construction](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1117-L1203) | Shows command resolve mode and sRGB flag wiring. |
| Reference generation and comparisons | [`reference generation and checks`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1284-L1579) | Defines pass and failure conditions. |
| Registration | [`createMultisampleResolveMaint10Tests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1586-L1810) | Builds the `m10_resolve` matrix and prunes combinations. |
| Vulkan maintenance10 feature contract | [Maintenance10 feature description](../../../../vulkan-docs/src/chapters/features.adoc#features-maintenance10) | Describes the feature's resolve additions and sRGB control. |
| Command resolve semantics | [Resolve image commands](../../../../vulkan-docs/src/chapters/copies.adoc#vkCmdResolveImage2) | Defines `VkResolveImageInfo2`, resolve modes, regions, and aspects. |

## Questions / Risk Points for User Audit

- Does the distinction between command, render-pass, and dynamic-rendering resolve remain clear?
- Is the host reference model clear about region mapping and sRGB transfer handling?
- Should the final page include any additional format names beyond the registered format classes?

## Conversion Notes for Final Wiki Rewrite

Keep the final page focused on the three direct intermediate nodes under `m10_resolve`. Preserve the complete failure table under `## Failure Meaning`, then add source-grounded cause analysis. Move the teaching example into the overview or runtime section only if it helps explain the region mapping.
