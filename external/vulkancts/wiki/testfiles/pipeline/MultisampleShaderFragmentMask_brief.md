# Understanding Brief: Multisample shader fragment mask

## One-Sentence Test Purpose

This test checks whether `VK_AMD_shader_fragment_mask` returns the fragment selected for each sample of a compressed multisampled color surface.

## Background Knowledge

### Fragment masks and fragment fetches

A compressed multisampled color surface can store color fragments more compactly than one independent value per sample. `VK_AMD_shader_fragment_mask` exposes a lookup table for that representation. [`fragmentMaskFetchAMD`](../../../../vulkan-docs/src/appendices/VK_AMD_shader_fragment_mask.adoc#L21-L38) returns one `uint`; each four-bit field gives the fragment index for a sample. A shader passes that index to `fragmentFetchAMD` to obtain the corresponding color fragment.

Why it matters here:
- The test derives the fragment index for every sample from the mask, then compares the resulting colors with ordinary `texelFetch` results.
- The comparison tests the extension's mapping, not a fixed physical compression layout.

### Multisampled attachments

The graphics pipeline supplies multisample state through `VkPipelineMultisampleStateCreateInfo` when rasterization is enabled, and the attachment sample count must match `rasterizationSamples` in this test's ordinary render-pass configuration. See [multisample pipeline state](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2188-L2201) and the [attachment compatibility rule](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3016-L3020).

## One Concrete Example

A representative leaf is `dEQP-VK.pipeline.monolithic.multisample.shader_fragment_mask.samples_4.image_2d.r32_uint`. The test draws colored geometry into a 32-by-32 four-sample `R32_UINT` image. A compute workgroup handles one pixel, with four local invocations. Invocation `sampleNdx` extracts bits `4 * sampleNdx` through `4 * sampleNdx + 3` from the mask, fetches the indexed fragment, and writes its first component to the matching storage-buffer slot. A second dispatch writes the ordinary `texelFetch` value for the same pixel and sample. The host requires exact equality.

## End-to-End Test Flow

```text
[host] select sample count, source form, integer or UNORM format, and pipeline construction type
[host] require VK_AMD_shader_fragment_mask and the relevant sample-count limits
[host] allocate a multisampled color image, vertex buffer, and host-visible result buffer
[device] draw the colored geometry into the multisampled image
[device] read the image with fragment-mask operations, either in a compute dispatch or a second render-pass subpass
[host] invalidate and copy the fragment-mask result, clear the result buffer, and run the ordinary texel-fetch reference path
[host] compare each layer and sample exactly; any mismatched texel fails the case
```

For `subpass_input`, the test performs the draw and fragment-mask read in two dependent subpasses. For `image_2d` and `image_2d_array`, it draws first and uses a compute shader for both result paths.

## Behavior Parameter Identification

The primary behavioral axis is the direct intermediate node below `pipeline.monolithic.multisample.shader_fragment_mask`: `samples_2`, `samples_4`, `samples_8`, or `samples_16`. Each value changes the mask-field count and the multisampled attachment configuration. Source form and color format exercise access and type variants within each sample-count behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `samples_2` | Incorrect two-sample fragment-mask decoding or fragment fetch, or a shared render, image-access, synchronization, or comparison defect. |
| `samples_4` | Incorrect four-sample fragment-mask decoding or fragment fetch, or a shared render, image-access, synchronization, or comparison defect. |
| `samples_8` | Incorrect eight-sample fragment-mask decoding or fragment fetch, or a shared render, image-access, synchronization, or comparison defect. |
| `samples_16` | Incorrect sixteen-sample fragment-mask decoding or fragment fetch, or a shared render, image-access, synchronization, or comparison defect. |

The final comparison localizes an error to the tested path but cannot by itself distinguish image creation, rasterization, extension instruction lowering, memory visibility, or host comparison.

## Open Questions and Risks

The test covers the extension only when the implementation exposes `VK_AMD_shader_fragment_mask`; unsupported implementations skip rather than fail the case. Shader-object construction types omit `subpass_input` because input attachments cannot be used with dynamic rendering.
