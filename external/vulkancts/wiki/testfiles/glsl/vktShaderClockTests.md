# vktShaderClockTests.cpp

## Overview

Tests for the VK_KHR_shader_clock extension. Verifies that the `OpReadClockKHR` SPIR-V instruction returns valid, monotonically increasing clock values for both subgroup-level and device-level clocks, in 32-bit and 64-bit variants.

## Role

Combined registration and implementation file. Contains the `addShaderClockTests()` function that builds the test hierarchy, as well as the `ShaderClockCase` / `ShaderClockTestInstance` test classes.

## Source Code

- [vktShaderClockTests.cpp](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L1-L261) (full file)
- Test instance class: [ShaderClockTestInstance](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L94-L128)
- Test case class: [ShaderClockCase](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L130-L221)
- Registration function: [addShaderClockTests()](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L251)
- Entry point: [createShaderClockTests()](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L255-L258)

## Registration Hierarchy

```text
glsl.shader_clock
├── vertex
├── fragment
└── compute
```

Each stage group contains 4 test cases:
- `clockARB` (subgroup clock, 64-bit)
- `clock2x32ARB` (subgroup clock, 2x32-bit)
- `clockRealtimeEXT` (device clock, 64-bit)
- `clockRealtime2x32EXT` (device clock, 2x32-bit)

## Test Families

| Family | Class | Description |
|--------|-------|-------------|
| ShaderClockCase | [ShaderClockCase](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L130-L221) | Test case that configures shader spec and checks support |
| ShaderClockTestInstance | [ShaderClockTestInstance](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L94-L128) | Test instance that executes shader and validates output |

## Parameter Dimensions

| Dimension | Values |
|-----------|--------|
| clockType | SUBGROUP, DEVICE |
| bitType | BIT_32, BIT_64 |
| ShaderType | vertex, fragment, compute |

## Support/Feature Requirements

| Feature | Condition |
|---------|-----------|
| VK_KHR_shader_clock | Always required |
| DEVICE_CORE_FEATURE_SHADER_INT64 | Required for BIT_64 tests |
| shaderSubgroupClock | Required for SUBGROUP (clockARB/clock2x32ARB) tests |
| shaderDeviceClock | Required for DEVICE (clockRealtimeEXT/clockRealtime2x32EXT) tests |

## Verification Methods

Smoke test approach:
1. Shader reads clock value twice in sequence (`time1`, `time2`)
2. If `time1 > time2` (clock went backwards), shader writes `1` to output; otherwise writes `0`
3. CPU validates all output elements are `0` (i.e., clock is non-zero and monotonically increasing)
4. For 64-bit: direct `uint64_t` comparison; for 2x32-bit: lexicographic comparison of `uvec2` pairs (high word first, then low word)

## Notes

- The test uses `NUM_ELEMENTS = 32` invocations per test
- GLSL extensions used: `GL_ARB_shader_clock` for subgroup clocks, `GL_EXT_shader_realtime_clock` for device clocks, `GL_ARB_gpu_shader_int64` for 64-bit integer support
- The validation is intentionally lightweight (smoke test) since clock values are non-deterministic; the test only checks monotonicity, not specific values
