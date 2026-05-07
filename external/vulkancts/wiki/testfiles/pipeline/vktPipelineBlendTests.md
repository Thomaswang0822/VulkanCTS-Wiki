# vktPipelineBlendTests.cpp

## Overview

[`vktPipelineBlendTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1) implements the [`blend`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2727) topic group of the pipeline category. It verifies color blending operations across a wide range of formats, blend factors, and blend ops, including clamping behavior, dynamic color write masks, dual-source blending, and dynamic rendering local read remapping.

## Role

Implementation file. Also dispatches to [`vktPipelineDualBlendTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1) for multi-attachment dual-source blend tests.

## Source Code

- Primary source: [`vktPipelineBlendTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1)
- Header: [`vktPipelineBlendTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.hpp#L1)
- Shared blend support: [`vktPipelineBlendTestsCommon.cpp`](../../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.cpp#L1)
- Nested subgroup: [`vktPipelineDualBlendTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1)
- Shared helpers: [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1)

## Registration Path

This file contributes the subgroup returned by [`createBlendTests()`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2713), which is attached under each variant root by [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1) in the pipeline category root.

**Variant coverage**: All variants.

## Test Hierarchy

```text
blend
├── format                                (genFormatTests only)
│   └── <format_name>
│       └── states
│           └── <blend_state_set_name>   (100 random blend states per format)
├── clamp                                 (always generated)
│   └── <clamp_format_name>              (6 formats)
├── dynamic_mask                          (genFormatTests only)
│   └── format
│       └── e5b9g9r9_ufloat_pack32
│           └── states
│               ├── mask_0_no_blend
│               ├── mask_0_alpha_blend
│               ├── mask_rgb_no_blend
│               ├── mask_rgb_alpha_blend
│               ├── mask_a_no_blend
│               ├── mask_a_alpha_blend
│               ├── mask_rgba_no_blend
│               └── mask_rgba_alpha_blend
├── dual_source                           (genFormatTests only)
│   ├── format
│   │   └── <format_name>
│   │       ├── output_variable
│   │       │   └── states
│   │       │       └── <dual_source_blend_state_name>
│   │       └── output_array
│   │           └── states
│   │               └── <dual_source_blend_state_name>
│   └── multi_attachments                 (delegated to vktPipelineDualBlendTests.cpp, non-VulkanSC)
├── dynamic_dual_disable                  (non-VulkanSC, genFormatTests only)
│   ├── att_count_1
│   ├── att_count_1_plus_1
│   ├── att_count_2
│   ├── att_count_2_plus_1
│   ├── att_count_8
│   └── att_count_8_plus_1
└── drlr_remap                            (non-VulkanSC, genFormatTests only)
    └── locations_1_0[_we_<YY|YN|NY>][_dyn_blend][_dyn_we]
```

Source: [`createBlendTests()`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2713).

## Test Families

### 1. format/states

Core blend tests. For each blendable format, generates 100 random `VkPipelineColorBlendAttachmentState` combinations (src/dst color/alpha blend factors x blend ops x color write masks) using [`BlendStateUniqueRandomIterator`](../../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.cpp#L1) (seed 123). Verifies blending results against a software reference renderer.

### 2. clamp

Tests that blend factor clamping to [0,1] (unorm) or [-1,1] (snorm) is correctly applied before blend operations. Uses out-of-range quad colors and blend constants to exercise clamping.

### 3. dynamic_mask

Tests `VK_FORMAT_E5B9G9R9_UFLOAT_PACK32` with `VK_DYNAMIC_STATE_COLOR_WRITE_MASK_EXT`, verifying the spec rule that RGB mask bits must be all-or-none for this format. Uses [`DynamicMaskBlendTest`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1) which overrides color write masks dynamically.

### 4. dual_source

Dual-source blending tests. Iterates blend states that use SRC1 (secondary) blend factors. Tests both `output_variable` (single fragment output) and `output_array` (array output) shader patterns. Includes multi-attachment dual-source tests from [`vktPipelineDualBlendTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1).

### 5. dynamic_dual_disable

Tests dynamically disabling dual-source blending via `VK_EXT_extended_dynamic_state3` (colorBlendEnable, colorBlendEquation, colorWriteMask). Varies attachment count (1, 2, 8) with optional extra attachment.

### 6. drlr_remap

Tests `VK_KHR_dynamic_rendering_local_read` color attachment remapping with swapped location indices. Varies write enables, dynamic blend, and dynamic write enables.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| Color format | [`getBlendFormats()`](../../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.cpp#L42) | ~38 formats (UNORM, SNORM, SFLOAT, USCALED, packed, etc.) |
| Blend states | `BlendStateUniqueRandomIterator` (seed 123, 100 states) | Random cross-product of srcColorBlendFactor x dstColorBlendFactor x colorBlendOp x srcAlphaBlendFactor x dstAlphaBlendFactor x alphaBlendOp |
| Color write masks | `BlendTest::s_colorWriteMasks` | 4 masks (one per quad) |
| Clamp formats | [`clampFormats[]`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2831) | 6 formats (R8G8B8A8_UNORM/SNORM, B8G8R8A8_UNORM/SNORM, R16G16B16A16_UNORM/SNORM) |
| Dynamic mask patterns | [`ColorMaskTestCase[]`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2899) | 4 mask patterns (0, RGB, A, RGBA) x 2 blend states |
| Dual-source shader output | [`shaderOutputTypes[]`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2721) | `output_variable`, `output_array` |
| Attachment count (dynamic_dual_disable) | Loop | 1, 2, 8 |
| Extra attachment (dynamic_dual_disable) | Loop | `false`, `true` |
| Write enables (drlr_remap) | `weCases` | {true,true}, {true,false}, {false,true} |
| Dynamic blend / dynamic WE (drlr_remap) | Loops | `false`/`true` x `false`/`true` |

## Support / Feature Requirements

| Requirement | Where | Line |
|---|---|---|
| Format must support blending (`isSupportedBlendFormat`) | `BlendTest::checkSupport` | [394](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L394) |
| Pipeline construction requirements | `BlendTest::checkSupport` | [396](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L396) |
| `VK_KHR_portability_subset` / `constantAlphaColorBlendFactors` (non-VulkanSC) | `BlendTest::checkSupport` | [399](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L399) |
| `dualSrcBlend` device feature | `DualSourceBlendTest::checkSupport` | [493](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L493) |
| `extendedDynamicState3ColorBlendEnable`, `extendedDynamicState3ColorBlendEquation`, `extendedDynamicState3ColorWriteMask` | `DynamicDualBlendDisableCase::checkSupport` | [1977](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1977) |
| `dynamicRenderingLocalRead` | `RemapCase::checkSupport` | [2385](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2385) |
| `colorWriteEnable` (when dynamic write enables) | `RemapCase::checkSupport` | [2398](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2398) |

## Verification Methods

### format/states and dynamic_mask families

[`BlendTestInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L929) uses [`ReferenceRenderer`](../../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1) to render a reference with matching blend state. Reads back color attachment via `readColorAttachment()`. Primary comparison uses `tcu::floatThresholdCompare` with format-dependent threshold. For sub-8-bit and expandable formats, falls back to wider precision comparisons if the primary comparison fails.

### clamp family

[`ClampTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1580) reads back color attachment and compares with `tcu::floatThresholdCompare` (threshold computed from format precision).

### dynamic_dual_disable family

[`DynamicDualBlendDisableInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2029) reads back each color attachment and verifies pixel values match expected colors using `tcu::floatThresholdCompare`.

### drlr_remap family

[`RemapInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L2437) reads back color attachments after rendering with remapped locations and verifies expected colors using `tcu::floatThresholdCompare`.

## Test Principles Observed

- **Randomized blend-state coverage**: Uses seeded random iterator over the full blend-state space rather than exhaustive enumeration, balancing coverage against test count
- **Format-dependent precision**: Verification thresholds adapt to format bit depth, with fallback comparisons for borderline formats
- **Clamping orthogonality**: Clamping behavior is tested separately from core blending, with out-of-range inputs that exercise the clamping path
- **Dynamic state interaction**: Multiple families test the interaction between dynamic blend state and static pipeline state

## Notes / Uncertainties

- `genFormatTests` flag controls which sub-groups are generated per variant: only `shader_object_unlinked_spirv` gets format tests among shader object types
- `dynamic_dual_disable` and `drlr_remap` are guarded by `#ifndef CTS_USES_VULKANSC`
- The `clamp` group is always generated regardless of variant
