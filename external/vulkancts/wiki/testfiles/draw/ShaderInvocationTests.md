## Overview

**Core question:** Does Vulkan preserve the identity and behavior of helper fragment invocations when a fragment is demoted, including subgroup quad operations, volatile helper-invocation queries, atomics, and the Vulkan memory model?

This page documents [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L40-L112). The implementation registers three Amber test cases under `shader_invocation`; the Amber scripts perform the graphics workload, verification compute dispatch, and final buffer comparison. The family is render-pass-only and is omitted from Vulkan SC builds because the dispatcher excludes Amber tests there.

## Background Knowledge

- A helper invocation is a fragment invocation retained for derivative, quad, or related shader operations but excluded from normal side effects such as framebuffer writes. `demote`/`OpDemoteToHelperInvocation` changes an invocation's status without terminating shader execution.
- `helperInvocationEXT()` is the extension function spelling used by the first case. The two `TARGET_ENV spv1.6` cases use the GLSL built-in `gl_HelperInvocation`; this does not imply a core replacement for `OpIsHelperInvocationEXT`, which the C++ support check explicitly says was not promoted to core.
- Subgroup quad broadcasts read values from the four lanes of a 2x2 fragment quad. The scripts deliberately query the quad before and after demotion so helper lanes must contribute the specified helper value (`8.0`) rather than their ordinary rounded input.
- The fragment shader also performs an atomic add after the first demotion. The compute verification shader accepts only combinations of color masks and atomic values that are consistent with the allowed initial helper status and subsequent demotions.
- The Amber runner creates the render target, graphics and compute pipelines, submits the draw and verification work, and evaluates the script's `EXPECT` command. The C++ file supplies registration and support callbacks; it does not implement a separate host-side image algorithm.

## Registration Hierarchy

```text
draw.renderpass.shader_invocation
├── helper_invocation
├── helper_invocation_volatile
└── helper_invocation_volatile_mem_model
```

`shader_invocation` is the exact group name passed to [`createTestGroup`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L109-L112). The three exact child names and their Amber files are the entries in the `cases` array at [`createTests`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L81-L104). The parent dispatcher adds this group only when `!useDynamicRendering`, and only outside `CTS_USES_VULKANSC`, at [`createChildren`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117). Thus the full standard path is `draw.renderpass.shader_invocation.<case>`.

## Parameter Dimensions and Observed Values

| Case | Amber file | Shader spelling / environment | Additional support gate |
|---|---|---|---|
| `helper_invocation` | [`helper_invocation.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber) | `helperInvocationEXT()`; `TARGET_ENV spv1.3` | `VK_EXT_shader_demote_to_helper_invocation` |
| `helper_invocation_volatile` | [`helper_invocation_volatile.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile.amber) | `gl_HelperInvocation`; `TARGET_ENV spv1.6` | SPIR-V 1.6 availability is checked by the framework |
| `helper_invocation_volatile_mem_model` | [`helper_invocation_volatile_mem_model.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile_mem_model.amber) | `gl_HelperInvocation`; `TARGET_ENV spv1.6`; `#pragma use_vulkan_memory_model` | `vulkanMemoryModel` (and framework SPIR-V 1.6 checking) |

All three cases require subgroup quad operations and the `shaderDemoteToHelperInvocation` feature. The exact checks and unsupported messages are in [`checkSupport`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L47-L63). Unsupported requirements raise `NotSupportedError`; they are not test failures.

## Behavior Parameters

The primary behavioral axis is the registered case and its shader environment.

### `helper_invocation`: extension spelling

Uses `helperInvocationEXT()` with the extension environment.

### `helper_invocation_volatile`: SPIR-V 1.6-targeted volatile query

Uses `gl_HelperInvocation` with SPIR-V 1.6.

### `helper_invocation_volatile_mem_model`: Vulkan memory model

Adds the Vulkan memory model pragma to the volatile helper-invocation path.

## Shader Analysis

The Amber scripts contain the representative fragment and verification compute shaders. Their helper-invocation, quad-operation, demotion, and atomic behavior is summarized below and linked in the source appendix.

### Workload and shader behavior

Each Amber script uses the same 2x2 `R32G32B32A32_SFLOAT` framebuffer, a four-element float `alpha_keys` buffer (`0.75`, `2.25`, `3.25`, `3.75`), and a four-element uint `atomics` buffer initialized to zero. The fragment shader maps `gl_FragCoord` to one buffer element and computes three quad masks:

1. `mask0` is built before the conditional demotion.
2. Lanes whose `fract(alpha_value) < 0.5` execute `demote`.
3. `mask1` is built after that demotion, then the invocation performs `atomicAdd(atomics[linear_coord], 101u)`.
4. The invocation for `linear_coord == 3`, or one whose atomic result exceeds 1000, is demoted.
5. `mask2` is built after the second demotion, and the fragment writes `vec4(1.0, mask0, mask1, mask2)`.

The extension case uses `helperInvocationEXT()` in [`helper_invocation.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber#L16-L74). The volatile case uses `gl_HelperInvocation` and SPIR-V 1.6 in [`helper_invocation_volatile.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile.amber#L16-L74). The memory-model case has the same logical workload but adds `#pragma use_vulkan_memory_model` in [`helper_invocation_volatile_mem_model.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile_mem_model.amber#L16-L76).

## Runtime Execution and Result Checking

```text
create shader_invocation group
  -> create one Amber test case per caseDef entry
  -> run a 2x2 graphics draw
  -> run verification compute shader
  -> enumerate allowed helper-status/mask/atomic combinations
  -> write results[0] = all-ones only for a matching combination
  -> EXPECT results EQ_BUFFER ref_buffer
```

The verification compute shader loads the first pixel and the three remaining framebuffer pixels, reconstructs all 16 possible initial helper-status combinations, derives the expected `mask0`, `mask1`, `mask2`, and atomic values, and marks `results[0]` as `(1,1,1,1)` when the observed values match one allowed combination. The remaining result elements are the captured pixels. `ref_buffer` is sixteen float ones, so [`EXPECT results EQ_BUFFER ref_buffer`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber#L179-L193) requires every result element to equal one. The corresponding final checks are present in the volatile and memory-model scripts at their respective `EXPECT` lines.

A failure means the observed helper status, quad broadcast result, demotion behavior, atomic side effect, memory-model behavior, or Amber resource/submission path did not satisfy any allowed combination. It does not by itself identify whether the fault is shader compilation, subgroup execution, demotion lowering, atomic visibility, or image/buffer handling.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible implementation cause(s) |
|---|---|
| `helper_invocation` | Extension demotion, helper query, subgroup quad behavior, or Amber validation. |
| `helper_invocation_volatile` | SPIR-V 1.6 helper query, volatile behavior, demotion, or validation. |
| `helper_invocation_volatile_mem_model` | Vulkan memory model, atomic visibility, helper behavior, or validation. |

### Cause Analysis

#### Helper invocation and demotion

**Possible failure symptoms:** The observed masks, atomic values, or result buffer do not match an allowed helper-status combination.

**Possible implementation causes:** Shader compilation, demotion lowering, subgroup execution, atomic visibility, memory model behavior, or Amber resource handling.

## Case Pruning

### Requirement-based pruning

- Missing `VK_SUBGROUP_FEATURE_QUAD_BIT` causes `NotSupportedError` for every case.
- Missing `shaderDemoteToHelperInvocation` causes `NotSupportedError` for every case.
- Missing `VK_EXT_shader_demote_to_helper_invocation` affects only `helper_invocation`.
- Missing `vulkanMemoryModel` affects only `helper_invocation_volatile_mem_model`.
- The `CORE` and `CORE_MEM_MODEL` test types depend on SPIR-V 1.6; the source explicitly notes that this requirement is checked automatically. The source also states that `OpIsHelperInvocationEXT` was not promoted to core.

### Design-based pruning

- The family is not registered below dynamic-rendering roots because the parent calls it only when `useDynamicRendering` is false. It is also excluded under `CTS_USES_VULKANSC`.

## Key Takeaways

- The exact family is `draw.renderpass.shader_invocation` with three Amber leaves: `helper_invocation`, `helper_invocation_volatile`, and `helper_invocation_volatile_mem_model`.
- All cases exercise a 2x2 fragment quad, two demotion points, subgroup quad broadcasts, and atomic side effects.
- The first case uses `helperInvocationEXT()`; the latter two use `gl_HelperInvocation` in SPIR-V 1.6-targeted shaders, with the third enabling the Vulkan memory model. None documents a core replacement for `OpIsHelperInvocationEXT`.
- Amber's verification compute shader accepts the complete set of allowed helper-status outcomes and requires an all-ones result buffer.
- Support rejection is distinct from a failing `EXPECT` comparison.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Test type enum and support callbacks | [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L40-L79) |
| Exact case names, Amber directory, and callback binding | [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L81-L105) |
| Group creation | [`vktDrawShaderInvocationTests.cpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.cpp#L109-L112) |
| Public declaration | [`vktDrawShaderInvocationTests.hpp`](../../../modules/vulkan/draw/vktDrawShaderInvocationTests.hpp#L27-L39) |
| Render-pass/Vulkan-SC registration gate | [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L120) |
| Extension shader and verification | [`helper_invocation.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation.amber) |
| SPIR-V 1.6 volatile shader and verification | [`helper_invocation_volatile.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile.amber) |
| Vulkan memory-model shader and verification | [`helper_invocation_volatile_mem_model.amber`](../../../data/vulkan/amber/draw/shader_invocation/helper_invocation_volatile_mem_model.amber) |
