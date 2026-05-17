# Vertex Attribute Divisor Tests

## Overview

Tests for the vertex attribute divisor functionality provided by `VK_EXT_vertex_attribute_divisor` and `VK_KHR_vertex_attribute_divisor`, verifying that instanced vertex attributes are correctly fetched according to the specified divisor value. The tests cover multiple draw command variants, pipeline configuration modes (static, dynamic vertex input, shader objects), and both zero and non-zero first-instance values.

## Role

Validates that when a vertex input binding uses `VK_VERTEX_INPUT_RATE_INSTANCE` with a divisor value, vertex attribute data is advanced once every N instances (where N is the divisor). A divisor of 0 means all instances share the same attribute value (index 0). Tests ensure that the divisor is correctly applied across different draw functions (direct, indexed, indirect, multi-draw), different pipeline construction methods, and different first-instance offsets. Reference rendering is performed using a software rasterizer and compared against the GPU output.

## Source Code

- [vktDrawVertexAttribDivisorTests.cpp](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.vertex_attribute_divisor
├── ext
└── khr
```

## Test Families

### ext — Tests using VK_EXT_vertex_attribute_divisor

Tests that exercise the `VK_EXT_vertex_attribute_divisor` extension. The extension provides the `vertexAttributeInstanceRateDivisor` feature (for non-zero divisors) and the `vertexAttributeInstanceRateZeroDivisor` feature (for divisor == 0). The sub-structure is:

- **static_pipeline** — Pipeline with static vertex input state (divisor set at pipeline creation time via `VkVertexInputBindingDivisorDescription` at [vktDrawVertexAttribDivisorTests.cpp#L366-L371](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L366-L371))
- **dynamic_pipeline** — Pipeline with `VK_EXT_vertex_input_dynamic_state`, setting vertex input state dynamically via `vkCmdSetVertexInputEXT` at draw time ([vktDrawVertexAttribDivisorTests.cpp#L831-L858](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L831-L858))
- **shader_objects** — Uses `VK_EXT_shader_object` instead of a traditional graphics pipeline ([vktDrawVertexAttribDivisorTests.cpp#L379-L419](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L379-L419)). Only available with dynamic rendering.

Each pipeline type contains draw function groups:
- **draw** — `vkCmdDraw`
- **draw_indexed** — `vkCmdDrawIndexed`
- **draw_indirect** — `vkCmdDrawIndirect`
- **draw_indexed_indirect** — `vkCmdDrawIndexedIndirect`
- **draw_multi_ext** — `vkCmdDrawMultiEXT` (requires `VK_EXT_multi_draw`)
- **draw_multi_indexed_ext** — `vkCmdDrawMultiIndexedEXT` (requires `VK_EXT_multi_draw`)
- **draw_indirect_byte_count** — `vkCmdDrawIndirectByteCountEXT` (requires `VK_EXT_transform_feedback`, not available on VulkanSC)
- **draw_indirect_count** — `vkCmdDrawIndirectCount` (requires `VK_KHR_draw_indirect_count`)
- **draw_indexed_indirect_count** — `vkCmdDrawIndexedIndirectCount` (requires `VK_KHR_draw_indirect_count`)

Each draw function group contains first-instance groups:
- **zero** — `firstInstance = 0`
- **non_zero** — `firstInstance` values of 1, 3, 4, 20 (requires `supportsNonZeroFirstInstance` property and `drawIndirectFirstInstance` feature for indirect draws)

Each first-instance group contains leaf tests for divisor values: **0**, **1**, **2**, **16**.

### khr — Tests using VK_KHR_vertex_attribute_divisor

Identical structure to the `ext` family but requires `VK_KHR_vertex_attribute_divisor` instead. The KHR extension is the promoted version of the EXT extension with the same functionality. The same feature requirements (`vertexAttributeInstanceRateDivisor`, `vertexAttributeInstanceRateZeroDivisor`) and property checks (`supportsNonZeroFirstInstance`) apply.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Extension | EXT, KHR | Which vertex attribute divisor extension to require (defined at [vktDrawVertexAttribDivisorTests.cpp#L48-L52](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L48-L52)) |
| Pipeline type | STATIC_PIPELINE, DYNAMIC_PIPELINE, SHADER_OBJECTS | How the graphics pipeline is constructed (defined at [vktDrawVertexAttribDivisorTests.cpp#L54-L58](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L54-L58)) |
| Draw function | DRAW, DRAW_INDEXED, DRAW_INDIRECT, DRAW_INDEXED_INDIRECT, DRAW_MULTI_EXT, DRAW_MULTI_INDEXED_EXT, DRAW_INDIRECT_BYTE_COUNT_EXT, DRAW_INDIRECT_COUNT, DRAW_INDEXED_INDIRECT_COUNT | The Vulkan draw command used (defined at [vktDrawVertexAttribDivisorTests.cpp#L61-L76](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L61-L76)) |
| First instance | zero (0), non_zero (1, 3, 4, 20) | Whether the first instance index is zero or non-zero |
| Attribute divisor | 0, 1, 2, 16 | The instance rate divisor value for the instanced vertex binding |
| Instance count | 0, 1, 2, 4, 20 | Number of instances drawn per iteration (defined at [vktDrawVertexAttribDivisorTests.cpp#L483](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L483)) |

## Support Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `VK_EXT_vertex_attribute_divisor` | When extension is EXT | [vktDrawVertexAttribDivisorTests.cpp#L979](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L979) |
| `VK_KHR_vertex_attribute_divisor` | When extension is KHR | [vktDrawVertexAttribDivisorTests.cpp#L988](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L988) |
| `vertexAttributeInstanceRateDivisor` feature | When divisor == 1 | [vktDrawVertexAttribDivisorTests.cpp#L1001-L1002](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1001-L1002) |
| `vertexAttributeInstanceRateZeroDivisor` feature | When divisor == 0 | [vktDrawVertexAttribDivisorTests.cpp#L1003-L1004](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1003-L1004) |
| `supportsNonZeroFirstInstance` property | When firstInstance is non-zero | [vktDrawVertexAttribDivisorTests.cpp#L982-L984](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L982-L984) |
| `drawIndirectFirstInstance` feature | When firstInstance is non-zero and draw is indirect | [vktDrawVertexAttribDivisorTests.cpp#L996-L999](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L996-L999) |
| `VK_EXT_vertex_input_dynamic_state` | When pipeline type is DYNAMIC_PIPELINE | [vktDrawVertexAttribDivisorTests.cpp#L1006-L1007](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1006-L1007) |
| `VK_EXT_shader_object` | When pipeline type is SHADER_OBJECTS | [vktDrawVertexAttribDivisorTests.cpp#L1008-L1009](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1008-L1009) |
| `VK_EXT_multi_draw` | When draw function is DRAW_MULTI_EXT or DRAW_MULTI_INDEXED_EXT | [vktDrawVertexAttribDivisorTests.cpp#L1011-L1012](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1011-L1012) |
| `VK_KHR_draw_indirect_count` | When draw function is indirect count type | [vktDrawVertexAttribDivisorTests.cpp#L1013-L1014](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1013-L1014) |
| `VK_EXT_transform_feedback` + `transformFeedbackDraw` | When draw function is DRAW_INDIRECT_BYTE_COUNT_EXT | [vktDrawVertexAttribDivisorTests.cpp#L1017-L1026](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1017-L1026) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawVertexAttribDivisorTests.cpp#L1029-L1030](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1029-L1030) |

## Verification Methods

- **Fuzzy image comparison against software reference renderer**: For each combination of instance count and first instance index, a reference image is rendered using the rr (reference renderer) software rasterizer with `TestVertShader` and `TestFragShader` at [vktDrawVertexAttribDivisorTests.cpp#L160-L226](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L160-L226). The reference renderer applies the same vertex attribute divisor logic (with divisor 0 mapped to INT_MAX for the reference). The GPU output is compared against the reference using `tcu::fuzzyCompare` with a threshold of 0.05 at [vktDrawVertexAttribDivisorTests.cpp#L688-L689](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L688-L689). The test iterates over multiple instance counts (0, 1, 2, 4, 20) and first-instance values, failing if any combination produces a mismatch.

## Notes

- The framebuffer size is 128x128 with an 8x8 quad grid (defined at [vktDrawVertexAttribDivisorTests.cpp#L248-L250](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L248-L250)).
- The `shader_objects` pipeline type is only available when using dynamic rendering, because shader objects inherently use dynamic rendering. This filter is applied at [vktDrawVertexAttribDivisorTests.cpp#L1155-L1156](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1155-L1156).
- The vertex shader uses push constants to pass `firstInstance` and `instanceCount`, which are used to compute per-instance position offsets and color adjustments at [vktDrawVertexAttribDivisorTests.cpp#L1035-L1054](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L1035-L1054).
- The reference renderer treats a divisor of 0 as INT_MAX (all instances share attribute index 0), since the rr renderer does not natively support divisor 0 semantics. This is handled at [vktDrawVertexAttribDivisorTests.cpp#L658-L659](../../../modules/vulkan/draw/vktDrawVertexAttribDivisorTests.cpp#L658-L659).
- The `non_zero` first-instance tests iterate over multiple first-instance values (1, 3, 4, 20) rather than a single value, providing broader coverage of the first-instance offset interaction with attribute divisors.
- For dynamic pipeline and shader object modes, vertex input state is set at draw time using `vkCmdSetVertexInputEXT` with `VkVertexInputBindingDescription2EXT` and `VkVertexInputAttributeDescription2EXT` structures that include the divisor value.
