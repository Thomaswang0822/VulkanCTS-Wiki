# vktPipelineExtendedDynamicStateMiscTests.cpp

## Overview

[`vktPipelineExtendedDynamicStateMiscTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L1) implements the [`misc`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L798) subgroup under `extended_dynamic_state`. It verifies miscellaneous extended dynamic state behaviors that don't fit in the main EDS test file, including edge cases and interaction tests.

## Role

Implementation file. Nested subgroup registered under `extended_dynamic_state`.

## Source Code

- Primary source: [`vktPipelineExtendedDynamicStateMiscTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L1)
- Header: [`vktPipelineExtendedDynamicStateMiscTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.extended_dynamic_state.misc
├── sample_shading_dynamic_sample_count
├── dynamic_sample_shading_static_1_dynamic_2
├── dynamic_sample_shading_static_1_dynamic_4
├── dynamic_sample_shading_static_1_dynamic_8
├── dynamic_sample_shading_static_1_dynamic_16
├── dynamic_sample_shading_static_2_dynamic_4
├── dynamic_sample_shading_static_2_dynamic_8
├── dynamic_sample_shading_static_2_dynamic_16
├── dynamic_sample_shading_static_4_dynamic_8
├── dynamic_sample_shading_static_4_dynamic_16
└── dynamic_sample_shading_static_8_dynamic_16
```

Source: [`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795). Variant coverage: Not extra shader-object, VK only.

## Test Families

### sample_shading_dynamic_sample_count — Sample shading with dynamic sample count

Verifies that sample shading works correctly when the sample count is set dynamically via `vkCmdSetRasterizationSamplesEXT`. Tests that the actual number of fragment shader invocations matches the dynamically set sample count when sample shading is enabled.

### dynamic_sample_shading_static_*_dynamic_* — Dynamic sample shading with mixed static/dynamic counts

Verifies dynamic sample shading behavior when the static pipeline sample count differs from the dynamically set sample count. Each test case specifies a pair of static and dynamic sample counts (e.g., static 1 / dynamic 2, static 4 / dynamic 16). The dynamic count is always greater than the static value. These tests verify that the dynamic sample count correctly overrides the static pipeline state for sample shading calculations. Non-VulkanSC only, non-shader-object only.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Non-extra-shader-object variant types |
| Static sample count | Loop | 1, 2, 4, 8 |
| Dynamic sample count | Loop | 2, 4, 8, 16 (always greater than static) |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_extended_dynamic_state` | Required for EDS1 misc tests |
| `VK_EXT_extended_dynamic_state3` | Required for EDS3 misc tests |

## Verification Methods

- **Rendering comparison**: Set state dynamically, render, compare against expected output
- **Edge case verification**: Verify edge cases in dynamic state interaction

## Notes

- This file provides the `misc` subgroup nested under `extended_dynamic_state`
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
