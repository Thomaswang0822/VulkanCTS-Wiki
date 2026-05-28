# vktDrawShaderInvocationTests.cpp

## Overview

[`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L1) implements the [`shader_invocation`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L109) topic group of the draw category. It tests helper-invocation behavior in fragment shaders using the `VK_EXT_shader_demote_to_helper_invocation` extension and its Vulkan 1.6 core promotion, including interaction with the Vulkan memory model.

## Role

Implementation file. Amber-test-based; delegates test logic to `.amber` files under `draw/shader_invocation/`.

## Source Code

- Primary source: [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L1)
- Header: [`vktDrawShaderInvocationTests.hpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.hpp#L1)

## Registration Hierarchy

```text
draw.renderpass.shader_invocation
├── helper_invocation
├── helper_invocation_volatile
└── helper_invocation_volatile_mem_model
```

Source: [`createShaderInvocationTests()`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L109). This group is only added under the renderpass variant root, gated by `!CTS_USES_VULKANSC` and `!useDynamicRendering` in [`createChildren()`](../../../modules/vulkan/draw/vktDrawTests.cpp#L106).

## Test Families

### helper_invocation — EXT demote-to-helper-invocation test

Amber test using `OpIsHelperInvocationEXT` from `VK_EXT_shader_demote_to_helper_invocation`. Requires subgroup quad operations and the EXT extension. Defined in `draw/shader_invocation/helper_invocation.amber`.

### helper_invocation_volatile — Core SPIR-V 1.6 helper invocation test

Amber test using the core `OpIsHelperInvocationEXT` with volatile semantics (SPIR-V 1.6). Requires subgroup quad operations and `shaderDemoteToHelperInvocation` feature. Defined in `draw/shader_invocation/helper_invocation_volatile.amber`.

### helper_invocation_volatile_mem_model — Helper invocation with Vulkan memory model

Amber test combining helper-invocation volatile semantics with the Vulkan memory model. Requires subgroup quad operations, `shaderDemoteToHelperInvocation`, and `vulkanMemoryModel` feature. Defined in `draw/shader_invocation/helper_invocation_volatile_mem_model.amber`.

## Parameter Dimensions

| Dimension | Values | Notes |
|---|---|---|
| Test type | EXT, CORE, CORE_MEM_MODEL | Determines support requirements and amber file |

## Support / Feature Requirements

| Requirement | Applicable Tests | Source |
|---|---|---|
| `VK_SUBGROUP_FEATURE_QUAD_BIT` | All | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L49) |
| `shaderDemoteToHelperInvocation` | All | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L52) |
| `VK_EXT_shader_demote_to_helper_invocation` | `helper_invocation` (EXT) | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L56) |
| SPIR-V 1.6 | `helper_invocation_volatile` (CORE), `helper_invocation_volatile_mem_model` | Checked automatically by the framework |
| `vulkanMemoryModel` | `helper_invocation_volatile_mem_model` | [`checkSupport()`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L62) |

## Verification Methods

Amber-based verification. Each `.amber` file defines its own pass/fail criteria internally.

## Notes

- Renderpass-only: this group is not added to `dynamic_rendering` variant roots because amber tests do not support dynamic rendering.
- VK only: gated by `#ifndef CTS_USES_VULKANSC`.
