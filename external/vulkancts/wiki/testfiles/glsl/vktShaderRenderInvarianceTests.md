# vktShaderRenderInvarianceTests.cpp

## Overview

[`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1) implements two GLSL render-test roots: `glsl.invariance` for the `invariant` qualifier and `glsl.precise` for the `precise` qualifier. The roots are registered under the `glsl` package by [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1260-L1267), and the file's factories construct `invariance` and `precise` groups at [`createShaderInvarianceTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1130) and [`createShaderPreciseTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1132-L1140).

Both roots use [`InvarianceTest`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L90-L103), which stores two vertex shaders and one fragment shader for a render comparison. Each case draws the same generated triangle set twice; the first pass uses shader `vertex1` with a red uniform contribution and the second pass uses shader `vertex2` with a green uniform contribution, then verification fails if any red channel remains in the final image at [`InvarianceTestInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L270-L301) and [`InvarianceTestInstance::checkImage()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L304-L342).

## Role

Registration and implementation file. The header declares the two factories at [`vktShaderRenderInvarianceTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.hpp#L30-L35). [`createShaderInvarianceTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1130) calls [`addBasicTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L372-L915) with `"invariant"`; [`createShaderPreciseTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1132-L1140) calls the same basic generator with `"precise"` and adds the `extended_instructions` subgroup through [`addExtendedInstructionsTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L917-L1121).

## Source Code

- Primary source: [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1)
- Header: [`vktShaderRenderInvarianceTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.hpp#L1)
- GLSL package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1267)

## Registration Hierarchy

```text
glsl.invariance
├── highp
├── lowp
└── mediump
```

```text
glsl.precise
├── extended_instructions
├── highp
├── lowp
└── mediump
```

## Test Families

### highp, lowp, mediump — Basic invariant/precise render cases

[`addBasicTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L372-L915) iterates the `precisions[]` table and creates one direct child group per precision name: `highp`, `mediump`, and `lowp` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L370) and [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L400-L405).

Each precision group contains `gl_position` and `user_defined` subgroups, created from `varGroup[]` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L407-L415). For `gl_position`, the decorated assignment target is `gl_Position`; for `user_defined`, the file decorates `gl_Position` and a location-1 `v_value` output, then assigns `gl_Position = v_value` after computing the decorated value at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L376-L382).

Within each variable subgroup, the basic generator registers four `common_subexpression_*` cases, three `subexpression_precision_*` cases, and five `loop_*` cases. The common-subexpression cases are registered explicitly as `common_subexpression_0` through `common_subexpression_3` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L441-L596). The cross-precision subexpression loop registers `subexpression_precision_lowp`, `subexpression_precision_mediump`, and `subexpression_precision_highp` by iterating `glu::PRECISION_LOWP` through `glu::PRECISION_LAST` for the unrelated output precision at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L599-L681). The loop cases `loop_0` through `loop_4` are registered at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L684-L911).

The basic cases are shared by both roots, but the decoration string differs: `glsl.invariance` generates `invariant` shaders and `glsl.precise` generates `precise` shaders through their factory calls at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1139).

### extended_instructions — Precise extended-instruction cases

The `extended_instructions` direct child exists only in the `precise` root because [`createShaderPreciseTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1132-L1140) calls [`addExtendedInstructionsTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L917-L1121). That helper creates the subgroup at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L934-L935) and adds it to the main group at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1119-L1120).

For every tested value precision from `precisions[]` and every unrelated-output precision from `glu::PRECISION_LOWP` through `glu::PRECISION_LAST`, the helper registers cases named `smoothstep_<precision>_<unrelatedPrec>`, `mix_<precision>_<unrelatedPrec>`, `dot_<precision>_<unrelatedPrec>`, `cross_<precision>_<unrelatedPrec>`, and `distance_<precision>_<unrelatedPrec>` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L937-L1117).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Root decoration | `invariant` for `glsl.invariance`; `precise` for `glsl.precise` from the factory calls at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1139) |
| Direct precision groups | `highp`, `mediump`, and `lowp` from `precisions[]` and the group construction loop at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L405) |
| Literal and loop parameters by precision | `highValue`, `invHighValue`, `mediumValue`, `lowValue`, `invlowValue`, loop counts, normalization constants, and multipliers are listed per precision in `precisions[]` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L370) |
| Decorated target form | `gl_position` and `user_defined` variable groups from `varGroup[]` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L407-L415), with declarations and assignments selected by `vertDeclaration`, `assignment0`, `assignment1`, and `fragDeclaration` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L376-L382) |
| Basic generated case names | `common_subexpression_0..3`, `subexpression_precision_lowp/mediump/highp`, and `loop_0..4`, registered at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L441-L911) |
| Extended-instruction operations | `smoothstep`, `mix`, `dot`, `cross`, and `distance`, registered only under `glsl.precise.extended_instructions` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L953-L1116) |
| Render geometry and size | The test uses `m_renderSize = 256`, `numTriangles = 72`, and generates narrow and normal triangle patterns at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L105-L112) and [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L163-L187) |
| Per-pass uniform color | Pass 0 writes red and pass 1 writes green into two uniform buffers at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L189-L241) |

## Support / Feature Requirements

The file does not define a per-case `checkSupport()` override for [`InvarianceTest`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L90-L103). During iteration it selects the first available depth/stencil attachment format from `VK_FORMAT_D32_SFLOAT`, `VK_FORMAT_D24_UNORM_S8_UINT`, and `VK_FORMAT_X8_D24_UNORM_PACK32`, failing the test if none reports `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` in optimal tiling features at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L244-L263).

No additional feature or extension gate was observed in the inspected file. The page therefore should not claim optional-feature requirements for the whole group beyond this runtime depth-format availability check.

## Verification Methods

- [`InvarianceTest::initPrograms()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L123-L128) compiles two vertex shader variants named `vertex1` and `vertex2` plus a fragment shader for each case.
- [`InvarianceTestInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L156-L301) generates 72 narrow and 72 normal triangles, creates two uniform buffers with red and green colors, registers two draw objects using the two vertex shaders, draws them into one render target, and then calls `checkImage()`.
- The fragment shaders combine the pass color with a blue component derived from `v_unrelated`; the basic fragment template is at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L384-L398), while the extended-instruction fragment template is at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L917-L932).
- Verification is not a `tcu::pixelThresholdCompare()` between two saved images. Instead, the two passes are drawn sequentially to the same target; [`checkImage()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L304-L342) scans every pixel in the 256x256 image and fails if any pixel has a nonzero red channel, reporting that fragments from the first render pass remain.
- The pass criterion is therefore absence of red-channel evidence from the first pass after the second pass is rendered, as logged by the messages around [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L272-L299) and the red-channel scan at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L314-L326).

## Test Principles

- The same implementation class is reused for both `invariant` and `precise` roots; the decoration text is injected into GLSL source templates by [`formatGLSL()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L83-L88) and `FormatArgumentList` values assembled in [`addBasicTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L411-L438) and [`addExtendedInstructionsTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L943-L951).
- The basic generator varies both the decorated result target and an unrelated output calculation so that one shader includes computations involving `v_unrelated` while the paired shader generally assigns that output to zero, as seen in `common_subexpression_0` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L447-L478) and the cross-precision subexpression case at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L618-L680).
- Loop cases exercise decorated-value calculations inside or across loops with precision-specific iteration counts and normalization literals from `precisions[]` at [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L684-L911).
- Extended-instruction cases narrow the `precise` coverage to five observed GLSL built-ins (`smoothstep`, `mix`, `dot`, `cross`, and `distance`) and use cross-precision unrelated outputs, rather than covering every built-in operation.

## Notes / Uncertainties

- The current source includes `lowp` as a direct precision group for both roots; any description that lists only `mediump` and `highp` is stale relative to [`precisions[]`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L370).
- No separate source file was observed for these registered roots; the inspected implementation and registration evidence is in [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L90-L1140), with package attachment in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1260-L1267).
