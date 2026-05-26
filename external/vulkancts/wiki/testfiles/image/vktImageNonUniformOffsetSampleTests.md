# vktImageNonUniformOffsetSampleTests ([source](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp))

## Overview

Tests that verify non-uniform offset values can be used with GLSL texture*Offset functions. The tests use pseudorandomly generated offset values obtained from a uniform buffer, varying per shader invocation, to validate that implementations correctly handle non-constant offset arguments. Tests cover vertex, fragment, and compute shader stages with various texture sampling functions.

## Role of File

Implementation file that registers the `non_uniform_offset_sample` test group and provides complete test implementations. Contains test case class, test instance class, and the factory function that populates the test hierarchy.

## Source Code

- Implementation: [vktImageNonUniformOffsetSampleTests.cpp](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp)
- Header: [vktImageNonUniformOffsetSampleTests.hpp](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.hpp)

## Registration Hierarchy

```text
image.non_uniform_offset_sample
├── texture_offset
├── texel_fetch_offset
├── texture_lod_offset
├── texture_proj_offset
└── texture_proj_lod_offset
```

Evidence:
- `non_uniform_offset_sample` group created by [`createImageNonUniformOffsetSampleTests()`](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L714-L767)
- Function groups added at lines 742-744 with names like `{prefix}_offset`
- Test stages and multi-mip variants generated at lines 747-761

## Test Families

### texture_offset — Basic texture sampling with non-uniform offset

Tests `textureOffset` GLSL function. Uses base texture coordinates (top-left texel center) while offsets select which texel to actually sample. Validates that the sampler correctly applies non-constant offsets.

### texel_fetch_offset — Texel fetch with non-uniform offset

Tests `texelFetchOffset` GLSL function. Uses integer texel coordinates with explicit LOD, while offsets select which texel to fetch. Requires LOD argument availability.

### texture_lod_offset — Explicit LOD texture sampling with non-uniform offset

Tests `textureLodOffset` GLSL function. Uses explicit LOD value with offset selection. Requires LOD argument availability.

### texture_proj_offset — Projective texture sampling with non-uniform offset

Tests `textureProjOffset` GLSL function. Uses projective coordinates (3-component) where the third component serves as a divisor. The offset selects which texel to sample from the projected result.

### texture_proj_lod_offset — Projective texture sampling with explicit LOD and non-uniform offset

Tests `textureProjLodOffset` GLSL function. Combines projective coordinates, explicit LOD, and non-uniform offset selection. Most complex sampling variant.

### Per-function variants

Each function group generates:
- **Shader stages**: vert (vertex shader), frag (fragment shader), and comp (compute shader) when the sampling
  function has an explicit LOD argument. Compute variants are skipped for implicit-LOD functions because compute
  shaders do not provide derivatives without `GL_KHR_compute_shader_derivatives`.
- **Mip levels**: single_mip (1 mip level) or multi_mip (4 mip levels, LOD-based functions only)

The current source therefore excludes compute-stage `texture_offset.single_mip_comp` and
`texture_proj_offset.single_mip_comp`; this matches their removal from
[`non-uniform-offset-sample.txt`](../../../mustpass/main/vk-default/image/non-uniform-offset-sample.txt).

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Framebuffer/Texture Size | 3x3 pixels | [line 135-138](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L135-138) |
| Image Format | VK_FORMAT_R8G8B8A8_UNORM | [line 312](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L312) |
| Mip Levels | 1 (single_mip) or 4 (multi_mip) | [line 313-314](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L313-314) |
| Texture Usage | VK_IMAGE_USAGE_SAMPLED_BIT, VK_IMAGE_USAGE_TRANSFER_DST_BIT | [line 317](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L317) |
| Sample Count | VK_SAMPLE_COUNT_1_BIT | [line 332](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L332) |
| Offset Range | 0-2 in each coordinate (x, y) | [line 459-464](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L459-464) |
| Texture Colors | R/G from pixel position, B=0.5, A=1.0 | [line 356-365](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L356-365) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_maintenance8 | All tests | [line 168](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L168) |
| GL_EXT_texture_offset_non_const | GLSL extension for non-constant offsets | [lines 240, 265, 278](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L240) |

## Verification Methods

### Framebuffer comparison

Tests verify results by copying the framebuffer (or storage image for compute) to host-visible memory and comparing against a reference image:

- **Reference generation**: For each pixel position (x, y), the reference color is the texture pixel at `offset[x, y]` where offset is the shuffled offset array at that pixel index [lines 686-694](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L686-694)
- **Result comparison**: Uses `tcu::floatThresholdCompare` with RGB threshold of 0.005 (between 1/255 and 2/255) at [lines 701-706](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L701-706)

### Test logic

1. Create 3x3 texture with known gradient colors
2. Generate offsets (0,0) through (2,2), then shuffle pseudorandomly
3. Store offsets in uniform buffer
4. For each pixel, read offset from buffer at varying index and apply to texture*Offset call
5. Compare framebuffer result against expected (texture sampled at shuffled offset position)

## Test Principles Observed

- **Non-uniform offset validation**: Offsets obtained from uniform buffer at indices that vary per invocation ensure they cannot be hoisted to constants by the compiler
- **Stage-specific offset variation**:
  - Compute: Offset varies by `gl_LocalInvocationIndex` (each invocation different)
  - Vertex: Offset varies by vertex/primitive coordinates (each primitive different)
  - Fragment: Offset varies by `gl_FragCoord` (each fragment different)
- **Shader variation**: Tests all three shader stages where texture sampling can occur
- **Mip level coverage**: Single-mip and multi-mip variants test LOD handling with non-uniform offsets
- **Offset range**: Uses offsets 0-2 which fall within mandatory `minTexelOffset`/`maxTexelOffset` range (-8 to 7), avoiding additional feature requirements
- **SPIR-V validation**: Uses `FLAG_ALLOW_NON_CONST_OFFSETS` build option to allow non-constant offsets in SPIR-V [line 192](../../../modules/vulkan/image/vktImageNonUniformOffsetSampleTests.cpp#L192)

## Notes / Uncertainties

- The file requires VK_KHR_maintenance8 which enables non-uniform offsets in GLSL via `GL_EXT_texture_offset_non_const`
- Offsets are shuffled rather than truly random to ensure consistent but unpredictable test coverage
- Graphics tests use different primitive topologies: triangle strip for fragment stage, triangle list for vertex stage
- Compute tests use 1x1x1 dispatch with local size matching framebuffer dimensions
- The reference texture uses (R, G) derived from pixel position divided by (extent-1), producing values in [0, 1] range
- Clear color is black (0, 0, 0, 1) which differs from all possible texture colors to detect missing writes
