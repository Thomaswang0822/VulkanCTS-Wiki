# vktShaderHelperInvocationsTests.cpp

## Overview

Tests for helper invocation behavior in fragment shaders. Verifies that helper invocations (fragment shader invocations that do not contribute to the final output but are spawned for derivative computations) correctly read data from various sources (SSBO, device address, UBO, image, texture) and that output variables behave correctly for helper invocations.

## Role

Combined registration and implementation file. Contains the `addShaderHelperInvocationsTests()` function that builds the flat test case hierarchy, as well as the `HelperInvocationsTestCase` / `HelperInvocationsTestInstance` test classes with full rendering infrastructure.

## Source Code

- [vktShaderHelperInvocationsTests.cpp](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L1-L639) (full file)
- Test instance class: [HelperInvocationsTestInstance](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L70-L93)
- Test case class: [HelperInvocationsTestCase](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L510-L523)
- Registration function: [addShaderHelperInvocationsTests()](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L615-L630)
- Entry point: [createShaderHelperInvocationsTests()](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L634-L637)

## Registration Hierarchy

```text
glsl.helper_invocations
├── load_from_ssbo
├── load_from_address
├── load_from_ubo
├── load_from_image
├── load_from_texture
└── output_variables
```

## Test Families

| Family | Class | Description |
|--------|-------|-------------|
| HelperInvocationsTestCase | [HelperInvocationsTestCase](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L510-L523) | Test case that checks support and creates test instance |
| HelperInvocationsTestInstance | [HelperInvocationsTestInstance](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L70-L93) | Test instance that performs two-draw rendering and validates results |

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| TestType | LOAD_SSBO, LOAD_ADDRESS, LOAD_UBO, LOAD_IMAGE, LOAD_TEXTURE, OUTPUT_VARIABLES (6 types) |

## Support/Feature Requirements

| Feature | Condition |
|---------|-----------|
| VK_KHR_buffer_device_address | Required only for `load_from_address` (TestType::LOAD_ADDRESS) |

## Verification Methods

Two-draw rendering approach:
1. A render pass with two subpasses is used. The first subpass writes data that the second subpass reads
2. Helper invocations are spawned by rendering overlapping triangles that create derivative-dependent fragments
3. The fragment shader reads data from the configured source (SSBO, device address, UBO, image, or texture) and writes the result to an output attachment
4. For `output_variables`, the test verifies that helper invocations do not corrupt output variable values
5. Pass/fail is determined by counting fragments with the expected color value (`m_expectedColor = 63` by default) after reading back the color attachment

## Notes

- The test uses a two-subpass render pass to ensure helper invocations are active during the second subpass
- Each TestType configures different resource types: `LOAD_SSBO` uses storage buffers, `LOAD_ADDRESS` uses buffer device addresses, `LOAD_UBO` uses uniform buffers, `LOAD_IMAGE` uses storage images, `LOAD_TEXTURE` uses combined image samplers, `OUTPUT_VARIABLES` tests output variable behavior
- The `LOAD_ADDRESS` test type sets `m_usingDeviceAddress = true` and `m_usingDescriptorSet = false`, requiring `VK_KHR_buffer_device_address`
