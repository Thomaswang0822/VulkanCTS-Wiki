# vktPipelineVertexInputSRGBTests.cpp

## Overview

[`vktPipelineVertexInputSRGBTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L1) implements the [`srgb_vertex_formats`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L455) nested subgroup under the `vertex_input` group of the pipeline category. It verifies that sRGB vertex attribute data is properly linearized when consumed by the vertex shader, testing each component (R/G/B/A) per sRGB format with both strict and non-strict validation modes.

## Role

Implementation file. Nested subgroup under [`vktPipelineVertexInputTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1).

## Source Code

- Primary source: [`vktPipelineVertexInputSRGBTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L1)
- Header: [`vktPipelineVertexInputSRGBTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.vertex_input.srgb_vertex_formats
├── r8_srgb
├── r8g8_srgb
├── r8g8b8_srgb
├── b8g8r8_srgb
├── r8g8b8a8_srgb
└── b8g8r8a8_srgb
```

## Test Families

### r8_srgb — R8_SRGB format linearization

Tests sRGB-to-linear conversion for the R channel of VK_FORMAT_R8_SRGB. Contains `r` (non-strict, tolerates missing linearization with QUALITY_WARNING) and `r_strict` (fails if linearization does not occur, requires VK_KHR_maintenance10).

### r8g8_srgb — R8G8_SRGB format linearization

Tests sRGB-to-linear conversion for the R and G channels of VK_FORMAT_R8G8_SRGB. Each channel has non-strict and strict variants.

### r8g8b8_srgb — R8G8B8_SRGB format linearization

Tests sRGB-to-linear conversion for the R, G, and B channels of VK_FORMAT_R8G8B8_SRGB. Each channel has non-strict and strict variants.

### b8g8r8_srgb — B8G8R8_SRGB format linearization

Tests sRGB-to-linear conversion for the R, G, and B channels of VK_FORMAT_B8G8R8_SRGB. Each channel has non-strict and strict variants.

### r8g8b8a8_srgb — R8G8B8A8_SRGB format linearization

Tests sRGB-to-linear conversion for the R, G, B, and A channels of VK_FORMAT_R8G8B8A8_SRGB. Each channel has non-strict and strict variants.

### b8g8r8a8_srgb — B8G8R8A8_SRGB format linearization

Tests sRGB-to-linear conversion for the R, G, B, and A channels of VK_FORMAT_B8G8R8A8_SRGB. Each channel has non-strict and strict variants.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| VkFormat | [`kTestedFormats[]`](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L444) | 6 sRGB formats: R8_SRGB, R8G8_SRGB, R8G8B8_SRGB, B8G8R8_SRGB, R8G8B8A8_SRGB, B8G8R8A8_SRGB |
| Component | Loop | {0, 1, 2, 3} (R=0, G=1, B=2, A=3); skipped if >= format channel count |
| Strict mode | Loop | `false` (non-strict), `true` (strict, requires maintenance10) |
| PipelineConstructionType | Factory parameter | Monolithic, fast-linked library, or shader object |

**SRGBVertexInputParams struct** at [line 71](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L71).

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT` | `checkSupport` | [171](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L171) |
| `VK_KHR_maintenance10` (strict mode only) | `checkSupport` | [165](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L165) |
| Pipeline construction requirements | `checkSupport` | [162](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L162) |

## Verification Methods

**Rendered coverage comparison** ([line 269](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L269)):

The vertex shader uses the tested sRGB component value as the Y coordinate of a quad. If the GPU properly linearizes sRGB vertex data, a stored sRGB value of ~0.5 (which is ~0.214 in linear space) will produce a Y coordinate of ~0.214, covering approximately the top 21% of the framebuffer. If linearization does NOT occur, the raw 0.5 value is used directly, covering the top 50%.

**Two-run strategy** ([line 386](../../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L386)):
- **Run 0 (strict)**: Vertex buffer contains sRGB-encoded values. If the GPU linearizes on read, the result matches the expected coverage. Uses `tcu::floatThresholdCompare` with zero threshold against a reference image.
- **Run 1 (non-strict fallback)**: If Run 0 fails and strict mode is off, the test retries with pre-linearized values (no sRGB encoding). If this passes, the test returns `QUALITY_WARNING` ("sRGB vertex coordinates are not linearized").

## Test Principles Observed

- **Coverage-based verification**: Uses framebuffer coverage (quad position) rather than direct color comparison to detect sRGB linearization
- **Two-tier validation**: Strict mode fails on missing linearization; non-strict mode issues a quality warning, acknowledging that some implementations may not support sRGB vertex format linearization
- **Per-component isolation**: Each component is tested independently to ensure linearization is applied per-channel

## Notes / Uncertainties

- The test acknowledges that sRGB vertex format linearization is not universally supported by all implementations
- `VK_KHR_maintenance10` formalizes the requirement for sRGB vertex format linearization
