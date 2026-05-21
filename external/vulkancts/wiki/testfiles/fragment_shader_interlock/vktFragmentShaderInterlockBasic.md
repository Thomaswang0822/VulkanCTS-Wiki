# vktFragmentShaderInterlockBasic.cpp

This page documents the `basic` branch of the Vulkan CTS `fragment_shader_interlock` category.

## Overview

[`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L1) implements the `basic` subgroup for `VK_EXT_fragment_shader_interlock`. The branch generates cases across discard behavior, resource type, interlock mode, sample count, sample-shading state, and framebuffer dimensions at [`createBasicTests()`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L777-L864).

## Role of File

- Implementation-heavy registered subgroup file.
- The file constructs `TestCaseGroup(testCtx, "basic")` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L777-L779).
- Each leaf case is an `FSITestCase` added under the generated dimension groups at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L823-L862).

## Registration Hierarchy

```text
fragment_shader_interlock.basic
├── nodiscard
└── discard
```

## Test Families

### nodiscard — Interlock without discard paths

`nodiscard` cases are created from `killCases[]` with value `0` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L797-L800). Under this child, the generator creates resource, interlock, sample-count, sample-shading, and dimension descendants.

### discard — Interlock with discard paths

`discard` cases are created from the same `killCases[]` table with value `1` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L797-L800). The fragment shader discards selected odd coordinates before and during the interlock and can discard again after ending the interlock at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L296-L330).

## Parameter Dimensions

| Dimension | Observed values |
|---|---|
| Resource target | `image`, `ssbo` from `resCases[]` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L792-L795) |
| Interlock mode | `pixel_ordered`, `pixel_unordered`, `sample_ordered`, `sample_unordered`, plus non-Vulkan SC `shading_rate_ordered` and `shading_rate_unordered` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L812-L821) |
| Sample count | `1xaa`, `4xaa` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L802-L805) |
| Sample shading | `no_sample_shading`, `sample_shading`, with `sample_shading` skipped when the sample count is 1 at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L807-L810) and [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L849-L850) |
| Dimensions | `8x8` through `1024x1024` from `dimCases[]` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L787-L790) |

## Support / Feature Requirements

`FSITestCase::checkSupport()` requires `VK_EXT_fragment_shader_interlock` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L154-L157). It then checks feature bits according to the selected interlock mode: sample interlock requires `fragmentShaderSampleInterlock`, pixel interlock requires `fragmentShaderPixelInterlock`, and non-Vulkan SC shading-rate interlock requires `fragmentShaderShadingRateInterlock` plus fragment-shading-rate support for fragment shader interlock at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L158-L181). Sample-interlock or sample-shading cases require the core `sampleRateShading` feature at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L184-L185).

## Verification Methods

The generated fragment shader performs a read/modify/write inside `beginInvocationInterlockARB()` and `endInvocationInterlockARB()` at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L249-L327). Ordered modes verify that previous primitive bits are present before setting the current mask, while unordered modes OR the mask directly at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L314-L319). After rendering, the test copies the image or buffer to a host-visible buffer and requires each copied word to equal `expectedValue`, except odd discarded entries which must remain zero at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L735-L772).

## Test Principles

The cases exercise interlock layout qualifiers emitted from the selected mode at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L225-L247), resource read/write paths for images and SSBOs at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L305-L325), and coordinate transformations for sample and shading-rate interlock modes at [`vktFragmentShaderInterlockBasic.cpp`](../../../modules/vulkan/fragment_shader_interlock/vktFragmentShaderInterlockBasic.cpp#L269-L281).

## Notes / Uncertainties

The shading-rate interlock modes are excluded from Vulkan SC builds by preprocessor guards in the registration table and support checks.
