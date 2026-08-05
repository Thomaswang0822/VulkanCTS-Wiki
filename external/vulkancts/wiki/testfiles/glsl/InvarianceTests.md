## Overview

[`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L90-L128) implements the GLSL ShaderRender tests for the `invariant` and `precise` qualifiers. The GLSL package attaches the two factories as `glsl.invariance` and `glsl.precise` in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1267). Both roots construct [`InvarianceTest`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L90-L103) cases containing two vertex-shader variants and one fragment shader.

The test deliberately renders the same geometry twice into one 256x256 target. The first draw uses the first vertex shader and a red uniform color; the second uses the second vertex shader and a green uniform color. A nonzero red channel means that fragments from the first pass remain visible, so the case fails with `Detected variance between two invariant values` at [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L270-L301). The test is therefore a sequential-overdraw oracle for position invariance; it is not a saved-image-to-saved-image comparison.

## Role

Registration and implementation file. [`createShaderInvarianceTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1130) creates the `invariance` group and calls [`addBasicTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L372-L915) with the `invariant` decoration. [`createShaderPreciseTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1132-L1140) creates the `precise` group, adds the same basic matrix with `precise`, and adds `extended_instructions` through [`addExtendedInstructionsTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L917-L1121). The header declares the factories in [`vktShaderRenderInvarianceTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.hpp#L30-L35).

## Source Code

- Primary implementation: [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1-L1144)
- Public factory declarations: [`vktShaderRenderInvarianceTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.hpp#L1-L38)
- GLSL package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1267)

## Registration Hierarchy

```text
glsl.invariance
├── highp
├── lowp
└── mediump

glsl.precise
├── extended_instructions
├── highp
├── lowp
└── mediump
```

The `highp`, `lowp`, and `mediump` groups each contain `gl_position` and `user_defined`. Each of those variable groups contains the four `common_subexpression_*` cases, three `subexpression_precision_*` cases, and five `loop_*` cases. `extended_instructions` is present only below `precise`.

## Test Families

### Basic matrix — `gl_position` and `user_defined`

[`addBasicTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L372-L415) iterates the three entries in `precisions[]`: `highp`, `mediump`, and `lowp` ([`precision table`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L370)). For each precision it creates the two variable groups `gl_position` and `user_defined` ([`varGroup[]`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L407-L415)). The `gl_position` form decorates `gl_Position`. The `user_defined` form decorates both `gl_Position` and a location-1 `highp out vec4 v_value`, then assigns `gl_Position = v_value`; the matching fragment input is emitted by the template arguments at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L376-L398).

Each variable group registers:

- `common_subexpression_0` through `_3` ([`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L441-L596)), where the first shader performs arithmetic shared with `v_unrelated` and the second removes that unrelated calculation while retaining the decorated result calculation.
- `subexpression_precision_lowp`, `_mediump`, and `_highp` ([`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L599-L681)). The input/result calculation uses the selected precision while the unrelated output uses each of the three precision values. The source selects different multipliers and normalization expressions when the lower of the two precisions is `lowp`.
- `loop_0` through `loop_4` ([`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L684-L911)). These cases place multiplication, conditional assignment, accumulation, or two related loop calculations around the decorated value. Iteration counts and normalization literals come from the selected precision record.

The basic matrix has `3 × 2 × (4 + 3 + 5) = 72` leaves under each root. The `invariant` and `precise` roots use the same generated shapes; only the injected GLSL decoration differs.

### Extended instructions — `precise` only

[`addExtendedInstructionsTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L917-L1121) creates the direct child `extended_instructions` and loops over three precisions for the calculation under test and three precisions for `v_unrelated` ([`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L934-L951)). For each of the 9 precision pairs it registers five operations: `smoothstep`, `mix`, `dot`, `cross`, and `distance` ([`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L953-L1116).

Each pair contrasts a shader in which the selected built-in also contributes to an unrelated output with a shader that writes zero to that output, while the decorated calculation remains. This is targeted coverage of these five built-ins, not a claim about all GLSL extended instructions. The subgroup contains `3 × 3 × 5 = 45` leaves; combined with the 72 basic leaves, `glsl.precise` contains 117 leaves.

## Parameter Dimensions

| Dimension | Values / implementation evidence |
|---|---|
| Root decoration | `invariant` for `glsl.invariance`, `precise` for `glsl.precise` ([factory calls](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1140)) |
| Basic precision | `highp`, `mediump`, `lowp` ([`precisions[]`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L370)) |
| Decorated target | `gl_Position` or `gl_Position` plus user-defined `v_value` ([declarations](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L376-L382)) |
| Basic case families | Four common-subexpression, three cross-precision-subexpression, and five loop cases ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L441-L911)) |
| Extended operation | `smoothstep`, `mix`, `dot`, `cross`, `distance` ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L953-L1116)) |
| Extended precision pair | Calculation precision × unrelated-output precision: `highp`, `mediump`, `lowp` × the same three values ([loops](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L937-L951)) |
| Precision literals | High: `1.0e20` / `1.0e-20`; medium: `1.0e4` / `1.0e-4`; low: `0.9` / `1.1`, with additional values in the table ([`PrecisionCase`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L370)) |
| Loop parameters | High `14` iterations, medium `13`, low `6`; partial iterations are `11`, `11`, and `2` respectively ([`precisions[]`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L364-L370)) |
| Geometry | 72 narrow triangles and 72 normal triangles, generated with deterministic seed `123` ([geometry generation](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L163-L187)) |
| Render target | 256 × 256; the first available depth format among `D32_SFLOAT`, `D24_UNORM_S8_UINT`, and `X8_D24_UNORM_PACK32` ([render setup](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L244-L268)) |

## Support / Feature Requirements

No file-local `checkSupport()` or explicit extension/feature requirement is defined for these cases. At runtime, [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L244-L262) queries the three candidate depth formats and requires one whose optimal-tiling properties include `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`. If none is available, the implementation returns a test failure rather than a per-case `NotSupportedError`.

The package registration for these two roots is unconditional in the inspected `vktTestPackage.cpp` path; the nearby `CTS_USES_VULKANSC` guard applies to other GLSL groups, not to `createShaderInvarianceTests()` or `createShaderPreciseTests()` ([`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1267)). The `vksc-default` mustpass file consequently contains both roots.

## Runtime and Verification

1. [`initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L123-L128) adds the generated `vertex1`, `vertex2`, and `fragment` GLSL sources to the source collection.
2. [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L156-L187) creates the deterministic geometry: 72 narrow triangles, followed by 72 normal triangles. It creates two host-visible uniform buffers, writes red to pass 0 and green to pass 1, flushes each allocation, and binds each buffer through its own descriptor set ([`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L189-L241)).
3. Two draw objects are registered with the same fragment shader and the two vertex shader binaries ([`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L270-L289)). They render sequentially into the same color target; the source logs the first primitive as `red - purple` because the blue component is derived from `v_unrelated`, and the second as green.
4. [`checkImage()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L304-L342) visits every pixel in the 256×256 image and treats any nonzero integer red channel as an error. On failure it emits the result and an error mask; on success it logs `No variance found.`

The fragment template writes `vec4(ucolor.u_color.r, ucolor.u_color.g, blue, ucolor.u_color.a)`, with `blue` computed from the unrelated varying ([`basicFragmentShader`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L384-L398)). Thus the oracle specifically observes stale first-pass fragments through red-channel presence. It does not independently compare the two vertex outputs, and it does not establish that every unrelated varying value is preserved.

## Failure Cause Mapping

| Observable result | Evidence-backed interpretation |
|---|---|
| No available candidate depth format | The runtime prerequisite in [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L244-L262) was not met; this implementation reports a failure. |
| Shader compilation or pipeline/draw setup fails | The generated GLSL, interface, resource setup, or graphics execution path was rejected; the source does not isolate which stage caused the failure. |
| Any nonzero red pixel | A fragment from the first red draw remained visible after the green draw, which the case reports as variance. The oracle cannot by itself localize the cause to interpolation, arithmetic, qualifier handling, or another graphics component. |
| No red pixels | The tested two-pass rendering path produced the expected overwrite observation for this generated case. It is not proof of a general invariance guarantee beyond the exercised inputs and shader pair. |

## Test Principles

- `invariant` and `precise` are tested through the same render harness and generated shader families. The `precise` root is additionally used for the five explicit extended-instruction families; source comments state that `precise` also makes invariance guarantees ([`createShaderPreciseTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1132-L1138)).
- The paired vertex shaders preserve the decorated position calculation while changing or removing calculations that feed `v_unrelated`. This targets optimizer/reassociation interactions without using a cross-case host comparison.
- `gl_position` and `user_defined` are separate construction paths. The latter tests propagation through a decorated user output and a fragment input before the final position assignment.
- The render oracle is intentionally strict on red-channel absence but does not threshold or compare all channels. Background and green pixels are accepted as long as their integer red component is zero.

## Coverage Reconciliation

The source generator yields 72 leaves for `glsl.invariance` and 72 basic leaves plus 45 extended-instruction leaves for `glsl.precise`, for 189 leaves across both roots. The normalized leaf sets in [`vk-default` invariance entries](../../../mustpass/main/vk-default/glsl.txt#L7943-L8014), [`vk-default` precise entries](../../../mustpass/main/vk-default/glsl.txt#L14491-L14607), [`vksc-default` invariance entries](../../../mustpass/main/vksc-default/glsl.txt#L7024-L7095), and [`vksc-default` precise entries](../../../mustpass/main/vksc-default/glsl.txt#L13570-L13686) match those source-derived counts: each profile contains 72 `invariance` leaves and 117 `precise` leaves. The profile prefixes differ (`dEQP-VK` versus `dEQP-VKSC`); the suffix hierarchy is the same.

## Notes / Uncertainties
- The page documents generated GLSL templates and their registration, not a single verbatim shader source: literal values and precision substitutions are specialized per leaf by `formatGLSL()` ([`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L83-L88)).
- The implementation checks depth-format availability during test iteration and returns `fail` if no candidate is supported; no separate optional-feature skip path was observed in this file.
- The test's red-channel oracle is an observability boundary. A passing case shows that the second draw covered all pixels that the first draw covered without residual red; it does not independently identify the mechanism that made the two decorated computations invariant.
