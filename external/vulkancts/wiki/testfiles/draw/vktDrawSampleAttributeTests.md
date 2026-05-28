# Sample Attribute Tests (Implicit Sample Shading)

## Overview

Tests for implicit sample shading triggered by the use of sample interpolation attributes in fragment shaders. Verifies that declaring or using `gl_SampleID`, `gl_SamplePosition`, or the `sample` decoration on a fragment input variable correctly enables per-sample fragment shader invocations at a rate equivalent to `minSampleShading = 1.0`, even when `sampleShadingEnable` is set to `VK_FALSE` in the pipeline.

## Role

Validates that the Vulkan specification requirement for implicit sample shading is correctly implemented: when a fragment shader statically uses `gl_SampleID` or `gl_SamplePosition`, or dynamically uses a `sample`-decorated input variable, the implementation must invoke the fragment shader once per sample per fragment. This is tested by using an atomic counter in a storage buffer to count fragment shader invocations and verifying that the count is at least `sampleCount * width * height` (i.e., one invocation per sample per pixel).

## Source Code

- [vktDrawSampleAttributeTests.cpp](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp)

## Registration Hierarchy

```text
draw.renderpass.implicit_sample_shading
├── sample_decoration_dynamic_use
├── sample_id_static_use
└── sample_position_static_use
```

## Test Families

### sample_decoration_dynamic_use — Sample decoration on fragment input triggers implicit sample shading

The vertex shader outputs a `verify` value via a `sample`-decorated fragment input variable. The fragment shader reads this per-sample input and uses `atomicAdd` with `uint(ceil(verify))` to count invocations. Because the `sample` decoration is used on the input, the implementation must invoke the fragment shader per-sample. The pipeline has `sampleShadingEnable = VK_FALSE` and `minSampleShading = 0.0`, so sample shading is triggered solely by the `sample` decoration. Uses `VK_SAMPLE_COUNT_4_BIT` on a 4x4 framebuffer, expecting at least 64 invocations.

### sample_id_static_use — Declaring gl_SampleID triggers implicit sample shading

The fragment shader contains a bare reference to `gl_SampleID` (the built-in is declared but its value is not consumed in any computation). This static use of `gl_SampleID` is sufficient to trigger per-sample invocation. The invocation counter uses a constant `1` per invocation. Uses `VK_SAMPLE_COUNT_4_BIT` on a 4x4 framebuffer, expecting at least 64 invocations.

### sample_position_static_use — Declaring gl_SamplePosition triggers implicit sample shading

The fragment shader contains a bare reference to `gl_SamplePosition` (the built-in is declared but its value is not consumed). This static use of `gl_SamplePosition` triggers per-sample invocation. The invocation counter uses a constant `1` per invocation. Uses `VK_SAMPLE_COUNT_4_BIT` on a 4x4 framebuffer, expecting at least 64 invocations.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Trigger mechanism | SAMPLE_DECORATION_DYNAMIC_USE, SAMPLE_ID_STATIC_USE, SAMPLE_POSITION_STATIC_USE | The fragment shader feature that triggers implicit sample shading (defined at [vktDrawSampleAttributeTests.cpp#L59-L64](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L59-L64)) |
| Sample count | VK_SAMPLE_COUNT_4_BIT | Fixed at 4 samples per pixel |
| Framebuffer size | 4x4 | Fixed small size for counter-based verification |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| `fragmentStoresAndAtomics` feature | Always | [vktDrawSampleAttributeTests.cpp#L121](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L121) |
| `sampleRateShading` feature | Always (all three trigger types require it) | [vktDrawSampleAttributeTests.cpp#L123-L124](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L123-L124) |
| `VK_KHR_dynamic_rendering` | When using dynamic rendering variant | [vktDrawSampleAttributeTests.cpp#L119-L120](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L119-L120) |

## Verification Methods

- **Atomic counter comparison**: A storage buffer with a single `uint32_t` counter is bound to the fragment shader. Each invocation performs `atomicAdd(buf.invocationCount, one)` where `one` is either `1` (for `sample_id_static_use` and `sample_position_static_use`) or `uint(ceil(verify))` (for `sample_decoration_dynamic_use`). After rendering, the counter value is read back and compared against the expected minimum of `sampleCount * width * height` (4 * 4 * 4 = 64). The test passes if `result >= expectedCounter`. The check is at [vktDrawSampleAttributeTests.cpp#L484-L489](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L484-L489).

## Notes

- The pipeline explicitly sets `sampleShadingEnable = VK_FALSE` and `minSampleShading = 0.0` at [vktDrawSampleAttributeTests.cpp#L348-L351](../../../modules/vulkan/draw/vktDrawSampleAttributeTests.cpp#L348-L351), ensuring that sample shading is triggered only by the shader's use of sample-related built-ins or decorations, not by explicit pipeline configuration.
- The `sample_decoration_dynamic_use` test uses a vertex shader that outputs a `verify` value in the range [0.75, 1.0], which when passed through `ceil()` yields 1.0, making the counter increment equivalent to the other tests.
- The framebuffer is intentionally small (4x4) because the test uses atomic counter comparison rather than image comparison, making a large framebuffer unnecessary.
- The color attachment format is `VK_FORMAT_R8G8B8A8_UNORM` with `VK_SAMPLE_COUNT_4_BIT`, but the color output is not verified; only the atomic counter is checked.
