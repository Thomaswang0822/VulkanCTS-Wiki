## Overview

[`vktShaderClockTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L20-L24) implements `glsl.shader_clock`, the GLSL shader-executor group for `VK_KHR_shader_clock`. Each leaf emits GLSL that reads one clock builtin twice in the same invocation. The shader records a failure only if the first reading is greater than the second, and the host accepts the case only when all invocations report no failure.

The factory is added to the GLSL package by [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1279). This page documents source-defined registration and checking behavior; it does not report execution on this host.

## Source Code

- Implementation and factory: [`vktShaderClockTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L63-L261)
- Public factory declaration: [`vktShaderClockTests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.hpp#L30-L38)
- GLSL-package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1279)
- Shared shader-executor source generation and executor selection: [`generateSources()` and `createExecutor()`](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L4198-L4259)

## Registration Hierarchy

```text
glsl.shader_clock
├── vertex
├── fragment
└── compute
```

`addShaderClockTests()` explicitly creates the three stage groups and adds every entry of its four-item operation table to each one, for 12 registered leaves ([registration loop](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L250)). The stage names are `vertex`, `fragment`, and `compute`; no tessellation, geometry, mesh, or task group is registered by this file.

## Test Families

The operation name is both the test-case name and the GLSL builtin called by the generated shader ([operation table](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L80-L85), [shader construction](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L170-L211)).

| Leaf name | Clock scope | Returned representation | Generated GLSL extension |
|---|---|---|---|
| `clockARB` | Subgroup | 64-bit `uint64_t` | `GL_ARB_shader_clock` enabled |
| `clock2x32ARB` | Subgroup | two-word `uvec2` | `GL_ARB_shader_clock` enabled |
| `clockRealtimeEXT` | Device | 64-bit `uint64_t` | `GL_EXT_shader_realtime_clock` required |
| `clockRealtime2x32EXT` | Device | two-word `uvec2` | `GL_EXT_shader_realtime_clock` required |

The operation-table mapping is defined at [`vktShaderClockTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L68-L85) and used during registration at [lines 227–246](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L227-L246). `BIT_64` shaders additionally require `GL_ARB_gpu_shader_int64`; the two 32-bit-word operations do not ([extension and source selection](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L175-L203)).

Each leaf runs 32 shader-executor invocations. The host allocates one 64-bit result slot per invocation, although the shader output itself is declared as the high-precision unsigned vector `out0` ([element count and output setup](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L63-L66), [`iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L103-L112), [output declaration](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L205-L212)).

## Support / Feature Requirements

| Requirement | Applies to | Behavior when unavailable |
|---|---|---|
| `VK_KHR_shader_clock` device functionality | All leaves | The case is not supported. |
| `shaderInt64` core feature | `clockARB`, `clockRealtimeEXT` | The case is not supported. |
| `shaderSubgroupClock` feature | `clockARB`, `clock2x32ARB` | The case throws `NotSupportedError`. |
| `shaderDeviceClock` feature | `clockRealtimeEXT`, `clockRealtime2x32EXT` | The case throws `NotSupportedError`. |

[`ShaderClockCase::checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L152-L167) performs these checks before execution. The extension is unconditional; the integer feature is conditional on the 64-bit operation; and the clock feature is selected from the operation's `DEVICE` or `SUBGROUP` scope. These are runtime support outcomes, not registration-time removal of the leaf.

## Verification Methods

1. The case initializes 32 host result slots to `0xcdcdcdcd`, passes pointers to the shared shader executor, and validates the resulting vector after execution ([`ShaderClockTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L103-L118)).
2. A 64-bit shader reads the selected builtin into `time1` and `time2`, initializes `out0` to zero, and writes `out0.x = 1` when `time1 > time2` ([64-bit source](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L175-L185)).
3. A two-word shader performs the equivalent unsigned lexicographic comparison: `.y` is compared as the high word, then `.x` as the low word when the high words are equal ([32-bit-pair source](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L186-L194)).
4. `validateOutput()` passes only if every host slot equals zero; any shader invocation that records `1` produces `Result comparison failed` ([validation](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L121-L125)).

This is a non-decreasing-pair check, not a timestamp-value oracle. The implementation does not require a clock value to be nonzero, does not compare it with a CPU timestamp, and accepts equal consecutive reads because only a strict backwards comparison writes the failure value.

## Failure Meaning

A failing executed leaf establishes that at least one invocation observed the generated clock comparison as decreasing, or that the shader-executor/output path did not produce the expected zero result. It does not, by itself, isolate the defect to a particular driver component: generated GLSL/SPIR-V handling, the selected shader stage, clock implementation, pipeline execution, result transport, or host-side comparison can contribute to the observed failure.

A missing extension or feature follows the support path above and is reported as not supported rather than as evidence that the clock ordering check failed.

## Test Principles

- Coverage is a deliberately compact `3 × 4` matrix: three shader stages paired with two scopes and two result representations ([matrix construction](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L223-L250)).
- Each operation uses the same generated source shape for every registered stage; the shared shader-executor infrastructure chooses the stage-specific executor ([source generation](../../../modules/vulkan/shaderexecutor/vktShaderClockTests.cpp#L147-L150), [shared dispatch](../../../modules/vulkan/shaderexecutor/vktShaderExecutor.cpp#L4198-L4259)).
- The check concerns ordering between two reads within one invocation only. It neither compares readings between invocations nor imposes a minimum elapsed interval.
- Support gating is operation-specific, while the set of registered shader stages is fixed by the local stage table.
