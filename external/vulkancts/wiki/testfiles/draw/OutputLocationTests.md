## Overview

**Core question:** Do fragment output locations route each Amber-produced value to the intended color attachment across the registered array and shuffle cases?

`output_location` is a render-pass-only draw-test group for fragment output locations. Its registration code creates two Amber-backed families: `array`, which covers output arrays across attachment formats, precision qualifiers, and output types, and `shuffle`, which covers the `inputs-outputs` and `inputs-outputs-mod` location-mapping cases. The C++ wrapper registers the cases and attaches one portability-subset support check; the rendering and expected-result details live in the Amber data named by the wrapper.

## Background Knowledge

Fragment output locations map shader outputs to color attachment locations. Output arrays and shuffled locations exercise the correspondence between shader declarations and framebuffer attachments.

## Registration Hierarchy

The complete path is:

```text
draw.renderpass.output_location
├── array
└── shuffle
```

`createOutputLocationTests()` creates the `output_location` group through `createTestGroup()` ([source](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L127-L131)). The draw dispatcher adds that group only while building the render-pass branch and only when `CTS_USES_VULKANSC` is not defined and `useDynamicRendering` is false ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117)). Therefore this page describes neither a Vulkan SC registration nor a dynamic-rendering variant.

The public entry point is declared in [`vktDrawOutputLocationTests.hpp`](../../../modules/vulkan/draw/vktDrawOutputLocationTests.hpp#L27-L40), and the wrapper implementation is [`vktDrawOutputLocationTests.cpp`](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L25-L135).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning |
|---|---|---|
| Family | `array`, `shuffle` | Selects output-array or output-location-shuffle coverage. |
| Array cases | 28 exact Amber identifiers | Vary format, precision, and explicit output type. |
| Shuffle cases | `inputs-outputs`, `inputs-outputs-mod` | Vary output-location mapping scripts. |

## Behavior Parameters

The primary behavioral axis is the registered family and its exact Amber case. The wrapper preserves those identifiers and delegates shader behavior and expected results to Amber.

### `array`: output-array declarations

The 28 cases vary attachment format, precision, and output type.

### `shuffle`: output-location mapping

The two cases exercise the corresponding location-shuffle Amber scripts.

## Shader Analysis

Shader declarations and expected output values are defined in the referenced Amber scripts. The C++ wrapper does not generate a representative shader body, so this page does not infer one.

## Runtime Execution and Result Checking

The wrapper uses the Amber data directory `draw/output_location/array` and registers 28 case names. Each name becomes both the test-case identifier and the `.amber` filename passed to `createAmberTestCase()` ([registration](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L56-L100)). The names encode the attachment format, precision, and, where present, an explicit output type:

| Format encoded by case name | Precision | Registered cases |
|---|---|---|
| `b10g11r11-ufloat-pack32` | `highp` | `b10g11r11-ufloat-pack32-highp`, `b10g11r11-ufloat-pack32-highp-output-float`, `b10g11r11-ufloat-pack32-highp-output-vec2` |
| `b10g11r11-ufloat-pack32` | `mediump` | `b10g11r11-ufloat-pack32-mediump`, `b10g11r11-ufloat-pack32-mediump-output-float`, `b10g11r11-ufloat-pack32-mediump-output-vec2` |
| `b8g8r8a8-unorm` | `highp` | `b8g8r8a8-unorm-highp`, `b8g8r8a8-unorm-highp-output-vec2`, `b8g8r8a8-unorm-highp-output-vec3` |
| `b8g8r8a8-unorm` | `mediump` | `b8g8r8a8-unorm-mediump`, `b8g8r8a8-unorm-mediump-output-vec2`, `b8g8r8a8-unorm-mediump-output-vec3` |
| `r16g16-sfloat` | `highp` | `r16g16-sfloat-highp`, `r16g16-sfloat-highp-output-float` |
| `r16g16-sfloat` | `mediump` | `r16g16-sfloat-mediump`, `r16g16-sfloat-mediump-output-float` |
| `r32g32b32a32-sfloat` | `highp` | `r32g32b32a32-sfloat-highp`, `r32g32b32a32-sfloat-highp-output-vec2`, `r32g32b32a32-sfloat-highp-output-vec3` |
| `r32g32b32a32-sfloat` | `mediump` | `r32g32b32a32-sfloat-mediump`, `r32g32b32a32-sfloat-mediump-output-vec2`, `r32g32b32a32-sfloat-mediump-output-vec3` |
| `r32-sfloat` | `highp` | `r32-sfloat-highp` |
| `r32-sfloat` | `mediump` | `r32-sfloat-mediump` |
| `r8g8-uint` | `highp` | `r8g8-uint-highp`, `r8g8-uint-highp-output-uint` |
| `r8g8-uint` | `mediump` | `r8g8-uint-mediump`, `r8g8-uint-mediump-output-uint` |

The source supplies names rather than a C++ parameter object or generated case matrix. Consequently, the exact output declarations, draw commands, and expected pixels must be read from the corresponding Amber scripts; they should not be inferred from the filename alone.

### `shuffle` family

The wrapper uses `draw/output_location/shuffle` and registers exactly two Amber cases ([source](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L103-L118)):

| Case | Registered Amber file |
|---|---|
| `inputs-outputs` | `inputs-outputs.amber` |
| `inputs-outputs-mod` | `inputs-outputs-mod.amber` |

The family is intended by its registration name to exercise output-location shuffling. The C++ wrapper itself does not describe the shader interface or expected image; those details belong to the Amber inputs.

### End-to-end registration flow

1. The draw root creates a `renderpass` branch and several dynamic-rendering branches with `GroupParams` ([root setup](../../../modules/vulkan/draw/vktDrawTests.cpp#L126-L199)).
2. `createChildren()` reaches `createOutputLocationTests(testCtx)` only inside the non-VulkanSC block and the `!useDynamicRendering` condition ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117)).
3. `createOutputLocationTests()` calls `createTestGroup(testCtx, "output_location", createTests)` ([wrapper](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L127-L131)).
4. `createTests()` creates `array` and `shuffle`, then calls `cts_amber::createAmberTestCase()` with the exact case name, data directory, and `<case>.amber` filename ([array](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L56-L100), [shuffle](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L103-L118)).
5. Every `array` case receives `checkSupport`; `shuffle` cases do not ([support assignment](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L92-L99), [shuffle loop](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L110-L117)). Amber owns execution and comparison after the wrapper has registered the test case.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible implementation cause(s) |
|---|---|
| `array` case | Output declaration, format conversion, precision, Amber pipeline setup, or attachment mapping. |
| `shuffle` case | Location mapping, shader interface, Amber execution, or attachment validation. |

### Cause Analysis

#### Shader interface and attachment mapping

**Possible failure symptoms:** An Amber expected result comparison fails for one case family or format.

**Possible implementation causes:** Shader output declaration, location assignment, format conversion, pipeline interface, or attachment handling.

## Case Pruning

### Requirement-based pruning

Array cases can be skipped by the portability-subset and alignment gate in the wrapper.

### Design-based pruning

The dispatcher excludes the group for VulkanSC and dynamic-rendering paths.

### Support and pruning behavior

There are two independent registration gates:

- **Vulkan SC:** `createTests()` is compiled out under `CTS_USES_VULKANSC`; the fallback only marks the group parameter unused ([guard](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L51-L54), [fallback](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L120-L122)).
- **Dynamic rendering:** the dispatcher does not add this group when `useDynamicRendering` is true ([dispatcher](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L117)). This is a registration limitation of the Amber group, not a per-case runtime failure.

For `array` cases, `checkSupport()` raises `NotSupportedError` when all of the following hold: `VK_KHR_portability_subset` is supported, `minVertexInputBindingStrideAlignment == 4`, and the case name contains `r8g8` or `inputs-outputs-mod` ([checkSupport](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L40-L48)). Because the callback is attached only in the `array` loop, the `inputs-outputs-mod` condition is present in the shared callback but is not applied to the `shuffle` case by this wrapper. The `shuffle` family has no support callback in this file.

A `NotSupportedError` from this callback means the case was pruned for the declared portability-subset stride constraint; it is not a rendering failure. Other Amber execution or image-comparison failures indicate a failure in the behavior encoded by the relevant Amber script or in the implementation path exercised by it.

### Mustpass cross-check

The default Vulkan draw mustpass lists the registered path under `draw.renderpass.output_location`, including the `array` and `shuffle` cases ([`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28946-L28975)). The mustpass names are the compatibility-sensitive identifiers; they should remain exactly as registered in the C++ arrays.

### Source evidence

- [`vktDrawOutputLocationTests.cpp`](../../../modules/vulkan/draw/vktDrawOutputLocationTests.cpp#L40-L131): support callback, family groups, exact case arrays, Amber registration, and public group creation.
- [`vktDrawOutputLocationTests.hpp`](../../../modules/vulkan/draw/vktDrawOutputLocationTests.hpp#L27-L40): public declaration.
- [`vktDrawTests.cpp`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L121): dispatcher and render-pass/dynamic-rendering gating.
- [`draw.txt`](../../../mustpass/main/vk-default/draw.txt#L28946-L28975): default mustpass registration evidence.

## Key Takeaways

- The exact hierarchy is `draw.renderpass.output_location.{array,shuffle}`.
- `array` contains 28 Amber cases; `shuffle` contains `inputs-outputs` and `inputs-outputs-mod`.

## Source Reference Appendix

The wrapper, dispatcher, Amber data, and mustpass references cited above form the source reference map for this registration-only family.
- The group is excluded from Vulkan SC and is not registered in dynamic-rendering branches.
- The portability-subset callback applies to every `array` case and can prune matching names under the stated stride condition; the wrapper does not attach it to `shuffle`.
- The C++ file is a registration and support-policy wrapper. Shader behavior and expected results are defined by the Amber data files named by each case.
