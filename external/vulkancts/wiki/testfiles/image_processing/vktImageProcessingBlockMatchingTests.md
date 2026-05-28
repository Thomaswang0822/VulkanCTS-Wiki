# vktImageProcessingBlockMatchingTests.cpp

## Overview

This file implements the `block_matching` test group for the `image_processing` category. It validates the `VK_QCOM_image_processing` block matching operations (`textureBlockMatchSADQCOM` and `textureBlockMatchSSDQCOM`) across both graphics and compute pipelines. The file contains all test class definitions, shader generation, descriptor setup, command buffer construction, and result verification logic.

This is an **implementation file** that both registers and implements its test cases. It is the largest file in the category and covers the core functional testing of block matching image operations.

**Source:** [vktImageProcessingBlockMatchingTests.cpp](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp)

## Registration Hierarchy

```text
image_processing.graphics.monolithic.block_matching
├── sad
└── ssd
```

## Registration Details

### `createImageProcessingBlockMatchingGraphicsTests()` (line 2259)

Delegates to `createImageProcessingBlockMatchingCommonTests()` with `testCompute = false`. Called from the registration file for each pipeline construction type.

Exported via [vktImageProcessingBlockMatchingTests.hpp](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.hpp#L39).

### `createImageProcessingBlockMatchingComputeTests()` (line 2265)

Delegates to `createImageProcessingBlockMatchingCommonTests()` with `testCompute = true`. Called from the registration file once for the `compute` group.

Exported via [vktImageProcessingBlockMatchingTests.hpp](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.hpp#L41).

### `createImageProcessingBlockMatchingCommonTests()` (line 1881)

The shared registration function that builds the `block_matching` group. It creates sub-groups for each image processing operation (`sad`, `ssd`), and within each operation, creates test sub-groups that differ between graphics and compute paths.

**Key branching logic** (line 2005):
- If `!testCompute && pipelineConstructionType == MONOLITHIC`: creates the full graphics test suite (basic, block_sizes, address_modes, reduction_modes, tiling, swizzles, layouts, shader_stages, descriptors)
- If `testCompute`: creates basic tests plus compute-only self tests
- If `!testCompute && pipelineConstructionType != MONOLITHIC`: creates only basic tests (the extended graphics sub-groups are only generated for monolithic pipelines)

## Test Families

### sad (Sum of Absolute Differences)

Tests the `IMAGE_PROC_OP_BLOCK_MATCH_SAD` operation, which maps to the GLSL `textureBlockMatchSADQCOM()` function. Computes the sum of absolute differences between corresponding texels in a target block and a reference block.

**Registered formats** (from [`getOpSupportedFormats()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408)): `VK_FORMAT_R8_UNORM`, `VK_FORMAT_R8G8_UNORM`, `VK_FORMAT_R8G8B8_UNORM`, `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_A8B8G8R8_UNORM_PACK32`, and `VK_FORMAT_A2B10G10R10_UNORM_PACK32`; per-device format support is checked at runtime.

### ssd (Sum of Squared Differences)

Tests the `IMAGE_PROC_OP_BLOCK_MATCH_SSD` operation, which maps to the GLSL `textureBlockMatchSSDQCOM()` function. Computes the sum of squared differences between corresponding texels.

**Registered formats** (from [`getOpSupportedFormats()`](../../../modules/vulkan/image_processing/vktImageProcessingTestsUtil.cpp#L408)): `VK_FORMAT_R8_UNORM`, `VK_FORMAT_R8G8_UNORM`, `VK_FORMAT_R8G8B8_UNORM`, `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_A8B8G8R8_UNORM_PACK32`, and `VK_FORMAT_A2B10G10R10_UNORM_PACK32`; per-device format support is checked at runtime.

## Test Sub-groups

### basic

**Both graphics and compute paths.** Tests block matching with default parameters across the registered block-matching format list, subject to per-device support checks. Each test case is parameterized by:

| Parameter | Values | Line |
|---|---|---|
| Format | Formats returned by `getOpSupportedFormats()` | [L1962](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1962) |
| Match type | `same` (matching blocks) / `diff` (different blocks) | [L1967](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1967) |
| Random reference | `true` / `false` | [L1969](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1969) |
| Constant difference | `true` / `false` (skipped when match=true) | [L1971](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1971) |

**Test name pattern:** `{format}_{same|diff}[_random][_constdiff]`

Default parameters (from `getCommonTestParams()`, line 1657):
- Image size: 64x64
- Block size: 32x32
- Target/reference coordinates: (0,0)
- Tiling: `VK_IMAGE_TILING_OPTIMAL`
- Layout: `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`
- Address mode: `VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE`
- Reduction mode: `SAMPLER_REDUCTION_MODE_NONE`
- Components: identity mapping

For compute tests, `stageMask` is set to `VK_SHADER_STAGE_COMPUTE_BIT` at [L1990](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1990).

### block_sizes (graphics only, monolithic only)

Tests various block size configurations with non-zero target/reference coordinates. Defined by `getBlockSizeTestParams()` at [L1817](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1817).

| Parameter Set | targetCoord | referenceCoord | blockSize |
|---|---|---|---|
| params0 | (32,32) | (0,0) | (32,32) |
| params1 | (0,0) | (16,16) | (32,32) |
| params2 | (0,0) | (0,0) | (1,1) |
| params3 | (0,0) | (0,0) | (64,64) |
| params4 | (0,0) | (63,0) | (1,64) |

### address_modes (graphics only, monolithic only)

Tests sampler address modes with out-of-bounds block coordinates. Defined by `getSamplerAddressModeTestParams()` at [L1699](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1699).

| Address Mode | Test Scenarios |
|---|---|
| `VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE` | Center target with oversized block; smaller target image; target coord at image corner |
| `VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_BORDER` | Same three scenarios |

**Test name pattern:** `{addrModeName}_params{N}_{format}`

### reduction_modes (graphics only, monolithic only)

Tests combinations of reference and target sampler reduction modes. Defined by `getSamplerReductionModeTestParams()` at [L1743](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1743).

| Reference Reduction Mode | Target Reduction Modes Tested |
|---|---|
| `SAMPLER_REDUCTION_MODE_WEIGHTED_AVG` | NONE, WEIGHTED_AVG, MIN, MAX |
| `SAMPLER_REDUCTION_MODE_MIN` | NONE, WEIGHTED_AVG, MIN, MAX |
| `SAMPLER_REDUCTION_MODE_MAX` | NONE, WEIGHTED_AVG, MIN, MAX |

**Test name pattern:** `{reductionModeName}_params{N}_{format}`

### tiling (graphics only, monolithic only)

Tests combinations of target and reference image tiling. Defined by `getTilingTestParams()` at [L1766](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1766).

| Reference Tiling | Target Tiling Variants |
|---|---|
| `VK_IMAGE_TILING_OPTIMAL` | LINEAR only (OPTIMAL+OPTIMAL covered by basic) |
| `VK_IMAGE_TILING_LINEAR` | OPTIMAL, LINEAR |

**Test name pattern:** `{tilingName}_params{N}_{format}`

### swizzles (graphics only, monolithic only)

Tests non-identity component mapping (swizzle) for the reference image. Defined at [L2124](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2124).

| Swizzle Name | Component Mapping |
|---|---|
| `bgra` | B, G, R, A |
| `g01a` | G, ZERO, ONE, A |
| `rbg1` | R, B, IDENTITY, ONE |

### layouts (graphics only, monolithic only)

Tests combinations of target and reference image layouts. Defined by `getLayoutTestParams()` at [L1791](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1791).

| Reference Layout | Target Layout Variants |
|---|---|
| `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` | GENERAL only (RDONLY+RDONLY covered by basic) |
| `VK_IMAGE_LAYOUT_GENERAL` | SHADER_READ_ONLY_OPTIMAL, GENERAL |

**Test name pattern:** `{layoutName}_params{N}_{format}`

### shader_stages (graphics only, monolithic only)

Tests block matching operations in shader stages other than fragment. Defined at [L2173](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2173).

| Stage | Test Name |
|---|---|
| `VK_SHADER_STAGE_VERTEX_BIT` | `vertex` |

### descriptors (graphics only, monolithic only)

Tests descriptor-related features, specifically update-after-bind descriptors. Defined at [L2193](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2193).

| Feature | Variants |
|---|---|
| `updateAfterBind` | `same` / `diff` x `random` / non-random |

**Test name pattern:** `updateAfterBind_{same|diff}[_random]`

### self (compute only)

Tests block matching where the target and reference are different regions of the **same image**. Defined at [L2224](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L2224).

Uses `ImageProcessingBlockMatchSelfTest` class ([L1467](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1467)) and its instance class `ImageProcessingBlockMatchSelfTestInstance` ([L1487](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1487)).

| Parameter | Values |
|---|---|
| Match type | `same` / `diff` |
| Random reference | `true` / `false` |

**Test name pattern:** `{same|diff}[_random]`

Default self-test parameters:
- Target coordinate: (0,0)
- Reference coordinate: (32,32)
- Both target and reference use the same image (single descriptor binding)

## Support / Feature Requirements

### Common (base class `ImageProcessingBlockMatchTest::checkSupport()`, line 141)

| Requirement | Line | Detail |
|---|---|---|
| `VK_QCOM_image_processing` | Inherited from `ImageProcessingTest` | Device extension |
| `textureBlockMatch` | [L112-L114](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L112-L114) | Required by the shared image-processing base support check for SAD/SSD operations |
| Vulkan 1.3+ or `VK_KHR_format_feature_flags2` | [L97-L99](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L97-L99) | `VK_KHR_format_feature_flags2` is required below Vulkan 1.3 |
| `VK_EXT_descriptor_indexing` and `descriptorBindingSampledImageUpdateAfterBind` | [L163-L168](../../../modules/vulkan/image_processing/vktImageProcessingBase.cpp#L163-L168) | Required only for descriptor tests where `updateAfterBind` is enabled |
| Block size within limits | [L160-L162](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L160) | `blockSize <= maxBlockMatchRegion` from `VkPhysicalDeviceImageProcessingPropertiesQCOM` |
| `VK_FORMAT_FEATURE_2_BLOCK_MATCHING_BIT_QCOM` | [L172-L177](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L172) | Required for both target and reference image formats (optimal or linear tiling as appropriate) |
| Target image format support | [L198-L213](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L198) | `vkGetPhysicalDeviceImageFormatProperties` must succeed with `VK_IMAGE_USAGE_SAMPLE_BLOCK_MATCH_BIT_QCOM` |
| Reference image format support | [L181-L195](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L181) | Same as target |

### Graphics-specific (line 240)

| Requirement | Line | Detail |
|---|---|---|
| Color attachment format support | [L253](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L253) | Output format must support `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` |
| Output image format properties | [L258-L270](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L258) | `vkGetPhysicalDeviceImageFormatProperties` must succeed with color attachment usage |
| Pipeline construction requirements | [L272](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L272) | `checkPipelineConstructionRequirements()` for fast-linked-lib or shader-object pipelines |

### Compute-specific (line 1157)

| Requirement | Line | Detail |
|---|---|---|
| Storage image format support | [L1171](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1171) | Output format must support `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT` |
| Output image format properties | [L1176-L1188](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1176) | `vkGetPhysicalDeviceImageFormatProperties` must succeed with storage usage |
| Compute workgroup count | [L1190-L1192](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L1190) | Output image dimensions must fit within `maxComputeWorkGroupCount` limits |

## Verification Method

All block matching tests follow the same verification approach:

1. **CPU reference computation**: `buildStandardResult()` at [L741](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L741) computes the expected block matching error on the CPU using `ImageProcessingResult::getBlockMatchingResult()`.
2. **GPU result retrieval**: The shader writes the block matching error to a storage buffer (`sbOut.outError`) and a color output (green for match, red for mismatch).
3. **Error threshold calculation**: `calculateErrorThreshold()` at [L82](../../../modules/vulkan/image_processing/vktImageProcessingBlockMatchingTests.cpp#L82) computes a per-component tolerance accounting for quantization error and floating-point precision.
4. **Comparison**: `verifyResult()` (inherited from `ImageProcessingTestInstance`) compares the GPU error vector against the CPU reference with the calculated threshold, and also performs a pixel-level comparison of the output image.

The error threshold formula (line 82-102):
- For components with >= 8 bits: `quantizationErr + floatErr`, where `floatErr = (FP16_EPS * numElements) + safetyNet`
- For components with < 8 bits: `floatErr` only (clamped to 1.0 in `populateColorBuffer`)

## Key Data Structures

### `BlockMatchingTestParams` (line 67)

| Field | Type | Description |
|---|---|---|
| `targetImageParams` | `TestImageParams` | Target image configuration (type, size, format, tiling, layout, components, address mode, reduction mode) |
| `targetCoord` | `UVec2` | Target block start coordinate |
| `referenceCoord` | `UVec2` | Reference block start coordinate |
| `blockSize` | `UVec2` | Block dimensions for matching |

### `TestPushConstants` (line 75)

| Field | Type | Description |
|---|---|---|
| `targetCoord` | `UVec2` | Pushed to shader as target block origin |
| `referenceCoord` | `UVec2` | Pushed to shader as reference block origin |
| `blockSize` | `UVec2` | Pushed to shader as block dimensions |

## Shader Generation

### Graphics shaders (line 318)

- **Vertex shader**: If `stageMask` includes `VK_SHADER_STAGE_VERTEX_BIT`, the block matching operation is performed in the vertex shader; otherwise, a pass-through vertex shader is used.
- **Fragment shader**: If `stageMask` includes `VK_SHADER_STAGE_FRAGMENT_BIT`, the block matching operation is performed in the fragment shader; otherwise, a pass-through fragment shader is used.
- Both shaders use GLSL 450 with `GL_QCOM_image_processing` extension.
- Descriptor bindings: target texture (0), reference texture (1), target sampler (2), reference sampler (3), output error SSBO (4).

### Compute shaders (line 1195)

- Single compute shader with `local_size_x = 1, local_size_y = 1, local_size_z = 1`.
- Same descriptor bindings as graphics, plus output storage image (binding 5).
- Dispatches one workgroup per output pixel.

## Dependencies

| Include | Role |
|---|---|
| `vktImageProcessingBase.hpp` | Base classes (`ImageProcessingTest`, `ImageProcessingTestInstance`), `TestParams`, `TestImageParams` |
| `vktImageProcessingTestsUtil.hpp` | `ImageProcOp` enum, `ImageProcessingResult`, `DescriptorSetLayoutExtBuilder`, image/view creation helpers |
| `vkBufferWithMemory.hpp` | Buffer allocation wrapper |
| `vkImageWithMemory.hpp` | Image allocation wrapper |
| `vkPipelineConstructionUtil.hpp` | `PipelineConstructionType` enum and `checkPipelineConstructionRequirements()` |
| `vkComputePipelineConstructionUtil.hpp` | Compute pipeline creation helpers |
| `tcuImageCompare.hpp` | Image comparison utilities |
| `tcuRGBA.hpp` | RGBA color constants |
