## Overview

[`vktShaderRenderLimitTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L48-L261) implements the `glsl.limits` test subtree. It generates graphics shaders that nearly fill the vertex-output/fragment-input component budget, renders a quad, and accepts the case only when every tested fragment produces green. The sole registered family is `near_max.fragment_input`; it contains 15 cases generated from the component-count seeds 64, 128, and 256.

The component count used in a case is not a count of only user varyings. The implementation explicitly accounts for the four components of `gl_Position`: it generates user-defined interface data from `m_inputComponents - 4`, while its vertex-output limit check adds four back. This makes each leaf a near-threshold interface test rather than a claim that the shader declares exactly `components_N` user components.

## Registration and Coverage

[`createGlslTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1269) attaches `createLimitTests()` to the GLSL group. The GLSL root is attached in both the Vulkan and Vulkan SC package initializers at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1345-L1354) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1413-L1422). There is no file-local `CTS_USES_VULKANSC` exclusion around `createLimitTests()`.

## Registration Hierarchy

```text
glsl.limits
└── near_max
```

[`createLimitTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L241-L261) creates the three nodes above. Its two nested loops add five leaves below each seed:

| Seed | Registered `components_N` leaves | Count |
|---|---|---:|
| 64 | `components_59` through `components_63` | 5 |
| 128 | `components_123` through `components_127` | 5 |
| 256 | `components_251` through `components_255` | 5 |
| **Total** | Three seeds × five offsets | **15** |

The exact 15-leaf set appears in both mustpass profiles: [Vulkan default, lines 8015–8029](../../../mustpass/main/vk-default/glsl.txt#L8015-L8029) and [Vulkan SC default, lines 7096–7110](../../../mustpass/main/vksc-default/glsl.txt#L7096-L7110). The profiles differ only in the `dEQP-VK` versus `dEQP-VKSC` prefix for this subtree.

## Test Behavior

### Generated interface

[`FragmentInputComponentCase::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L131-L210) specializes one vertex and one fragment GLSL 450 template per leaf.

1. The vertex shader takes `a_position` at location 0, assigns it to `gl_Position`, and declares `o_color<location>` outputs.
2. The fragment shader declares matching `i_color<location>` inputs and `o_color` at location 0.
3. For each user location, the vertex shader writes a constructor whose components equal that location number; the fragment shader compares its matching input against the same constructor.
4. The fragment shader writes `(0, 1, 0, 1)` when every comparison passes, otherwise `(1, 0, 0, 1)`.

The number of emitted user locations is `ceil((m_inputComponents - 4) / 4)`. All locations before the final one are `vec4`; the final declaration is selected as `float`, `vec2`, `vec3`, or `vec4` by the remaining component count. Location numbers begin at zero, and each generated output/input pair uses the same explicit location.

For example, the source comment explains that a nominal 128-component case has 124 user-declared output components in addition to `gl_Position` ([lines 156–171](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L156-L171)). The test's component accounting and the literal final-type switch are the authoritative definition of the stress shape.

### Draw and result path

[`FragmentInputComponentCaseInstance::setupDefaultInputs()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L98-L104) installs six `vec4` positions as a `VK_FORMAT_R32G32B32A32_SFLOAT` vertex attribute at location 0. [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L66-L96) records an indexed render with 12 indices and four triangles, copies the result image, and compares it with a solid opaque-green reference image.

The shader comparisons test matching interface values at the fragment stage. The host oracle then uses `tcu::pixelThresholdCompare()` with per-channel threshold `tcu::RGBA(2, 2, 2, 2)`. Therefore a pass establishes that the rendered output matches green within that threshold; it does not separately report which varying location first mismatched.

## Support and Skip Conditions

[`FragmentInputComponentCase::createInstance()`](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L212-L237) reads physical-device limits and throws `NotSupportedError` instead of executing when either condition fails:

| Checked property | Executed-case requirement |
|---|---|
| `maxFragmentInputComponents` | `m_inputComponents <= maxFragmentInputComponents` |
| `maxVertexOutputComponents` | `m_inputComponents + 4 <= maxVertexOutputComponents` |

The second condition reserves the four `gl_Position` components in the vertex-output accounting. The inspected file contains no separate extension requirement, feature-bit gate, or `checkSupport()` override. A limit shortfall is therefore a not-supported outcome, not an image-comparison failure.

## Failure Cause Mapping

| Observable result | Evidence-backed interpretation |
|---|---|
| `NotSupportedError` before rendering | The requested count exceeds `maxFragmentInputComponents`, or the requested count plus the `gl_Position` allowance exceeds `maxVertexOutputComponents`. |
| Result image differs from green | At least one fragment shader interface comparison produced an error count, or another compiled/rendered-result path made the final image differ from the green reference. The image oracle alone does not localize the mismatch to a specific varying location or pipeline stage. |
| Shader or pipeline creation fails | The generated near-limit graphics interface was not accepted by the implementation; this is distinct from a completed render whose pixels fail the green comparison. |

## Source Evidence

- [Implementation and generator](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.cpp#L48-L261)
- [Public factory declaration](../../../modules/vulkan/shaderrender/vktShaderRenderLimitTests.hpp#L29-L37)
- [GLSL-parent registration](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1269)
- [Vulkan package root registration](../../../modules/vulkan/vktTestPackage.cpp#L1345-L1354)
- [Vulkan SC package root registration](../../../modules/vulkan/vktTestPackage.cpp#L1413-L1422)
- [Vulkan default mustpass leaves](../../../mustpass/main/vk-default/glsl.txt#L8015-L8029)
- [Vulkan SC default mustpass leaves](../../../mustpass/main/vksc-default/glsl.txt#L7096-L7110)

## Scope Notes

- This page documents generated GLSL source. There is no hand-authored per-leaf shader file or inline SPIR-V assembly artifact to reproduce.
- `near_max` is the only direct child of `limits`, and `fragment_input` is its only child in the local factory. No additional limit-test family is implied by the broader `glsl` package.
- The 64, 128, and 256 values are generator seeds, not assertions that every device exposes those exact limits. The actual device limits determine whether an individual generated case runs.
