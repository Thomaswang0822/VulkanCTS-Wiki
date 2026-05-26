# Shader Derivate Function Tests

## Overview

[`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1) registers and implements the `glsl.derivate` ShaderRenderCase-based group. The group covers fragment-shader derivative functions named by `DerivateFunc`, including `dFdx`, `dFdxFine`, `dFdxCoarse`, `dFdxSubgroup`, `dFdy`, `dFdyFine`, `dFdyCoarse`, `dFdySubgroup`, `fwidth`, `fwidthFine`, and `fwidthCoarse` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L77-L94) and [`getDerivateFuncName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L106-L136).

The file builds derivative cases around rendered image verification: it renders a two-triangle quad, reads back the result image, and calls a family-specific `verify()` implementation before returning pass or fail at [`TriangleDerivateCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L763-L811).

## Role

Registration and implementation file. The Vulkan package attaches this file's factory under the `glsl` category with `glslTests->addChild(sr::createDerivateTests(testCtx))` at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1255). The factory returns `ShaderDerivateTests`, whose constructor names the group `derivate` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1656-L1657) and whose `init()` method generates the direct function children at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2043-L2178).

## Source Code

- Primary source: [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1)
- Public factory declaration: [`vktShaderRenderDerivateTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.hpp#L23-L37)
- GLSL category registration site: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1255)
- Shared ShaderRender base declarations: [`vktShaderRender.hpp`](../../../modules/vulkan/shaderrender/vktShaderRender.hpp#L22-L44)

## Registration Hierarchy

```text
glsl.derivate
├── dfdx
├── dfdxfine
├── dfdxcoarse
├── dfdxsubgroup
├── dfdy
├── dfdyfine
├── dfdycoarse
├── dfdysubgroup
├── fwidth
├── fwidthfine
└── fwidthcoarse
```

## Test Families

### dfdx — Standard x-derivative cases

The `dfdx` child name is produced by [`getDerivateFuncCaseName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L138-L149), and the function group is created for every `DerivateFunc` enumerant in [`ShaderDerivateTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2043-L2048). Because `dfdx` is not a subgroup function, it receives the `constant` group, every generated linear-context group, the FBO groups, and the `texture` group through the non-subgroup branches at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2050-L2175).

### dfdxfine — Fine x-derivative cases

`dfdxfine` follows the same non-subgroup generation path as `dfdx`, with the shader spelling selected as `dFdxFine` by [`getDerivateFuncName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L110-L115). The implementation therefore combines constant-argument checks, generated linear contexts, FBO variants, and texture variants for this function at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2050-L2175).

### dfdxcoarse — Coarse x-derivative cases

`dfdxcoarse` is generated from `DERIVATE_DFDXCOARSE`, maps to shader text `dFdxCoarse`, and is classified as an x-derivative by `isDfdxFunc()` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L114-L115) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L170-L174). Its verification uses x-neighbor reference scaling in `LinearDerivateCaseInstance::verify()` and `TextureDerivateCaseInstance::verify()` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1078-L1091) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1408-L1420).

### dfdxsubgroup — Manual subgroup x-derivative cases

`dfdxsubgroup` is one of the two functions for which `isSubgroupFunc()` returns true at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L187-L190). The non-subgroup-only `constant`, linear-context, and `texture` branches are skipped for it, while the FBO loop still creates `fbo`, `fbo_msaa2`, `fbo_msaa4`, and `fbo_float` using `dFdxSubgroupSource` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2066-L2138) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2140-L2175). The subgroup shader uses `GL_KHR_shader_subgroup_quad`, `GL_KHR_shader_subgroup_ballot`, and `subgroupQuadBroadcast()` to compute `right - left` inside a quad at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1963-L1989).

### dfdy — Standard y-derivative cases

`dfdy` is generated as a non-subgroup function and receives the same family structure as `dfdx` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2050-L2175). The verification path classifies it with `isDfdyFunc()` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L176-L180), uses framebuffer height rather than width for the primary reference denominator, and applies y-neighbor component scaling at [`LinearDerivateCaseInstance::verify()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1078-L1091).

### dfdyfine — Fine y-derivative cases

`dfdyfine` maps to shader text `dFdyFine` at [`getDerivateFuncName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L118-L123). Its generated cases use the same non-subgroup family matrix as `dfdy`, including constant, linear-context, FBO, and texture groups at [`ShaderDerivateTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2050-L2175).

### dfdycoarse — Coarse y-derivative cases

`dfdycoarse` maps to `dFdyCoarse` and is treated as a y-derivative by `isDfdyFunc()` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L122-L123) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L176-L180). Linear and texture verification compute `reference` from the value range divided by image height and then multiply by the y component scale at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1078-L1091) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1408-L1420).

### dfdysubgroup — Manual subgroup y-derivative cases

`dfdysubgroup` is the y-direction subgroup function in `isSubgroupFunc()` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L187-L190). It skips constant, linear-context, and texture groups and uses the FBO matrix with `dFdySubgroupSource` selected in the FBO loop at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2111-L2117). The subgroup shader computes `bottom - top` with `subgroupQuadBroadcast()` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1991-L2018).

### fwidth — Standard width-derivative cases

`fwidth` is a non-subgroup function, so it receives constant, linear-context, FBO, and texture families at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2050-L2175). Its linear and texture verification paths compute the expected value as `abs(dx) + abs(dy)` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1142-L1156) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1467-L1481).

### fwidthfine — Fine width-derivative cases

`fwidthfine` maps to shader text `fwidthFine` at [`getDerivateFuncName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L126-L131). It uses the same non-subgroup case generation as `fwidth` at [`ShaderDerivateTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2050-L2175).

### fwidthcoarse — Coarse width-derivative cases

`fwidthcoarse` maps to shader text `fwidthCoarse` at [`getDerivateFuncName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L126-L131). Like the other `fwidth` family members, it uses `isFwidthFunc()` to select the `abs(dx) + abs(dy)` verification branch at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L182-L185), [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1142-L1156), and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1467-L1481).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Derivative function root | Eleven `DerivateFunc` values are enumerated at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L77-L94), named for registration at [`getDerivateFuncCaseName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L138-L168), and iterated by `funcNdx < DERIVATE_LAST` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2043-L2048). |
| Data type | Generated cases iterate vector sizes 1 through 4 and map them to `float`, `vec2`, `vec3`, and `vec4` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2056-L2060), [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2075-L2081), [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2119-L2124), and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2152-L2158). |
| Precision | Linear, FBO, and texture loops iterate `glu::PRECISION_LOWP`, `glu::PRECISION_MEDIUMP`, and `glu::PRECISION_HIGHP` through `precNdx < glu::PRECISION_LAST` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2077-L2082), [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2121-L2128), and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2154-L2162). Constant cases set high precision only at [`ConstantDerivateCase::ConstantDerivateCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L954-L963). |
| Low-precision skip rules | Non-basic linear contexts skip `lowp` when `caseNdx != 0`, because the default framebuffer path does not produce usable lowp bits, at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2086-L2087). FBO and texture cases skip `lowp` for non-float FBO surfaces at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2127-L2128) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2161-L2162). |
| Linear source contexts | `s_linearDerivateCases[]` includes `linear`, `in_function`, `static_if`, `static_loop`, `static_switch`, `uniform_if`, `uniform_loop`, `uniform_switch`, `dynamic_if`, `dynamic_loop`, `dynamic_switch`, `output_store`, `private_store`, and, outside Vulkan SC builds, `linear_vec8` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1682-L1961). |
| FBO configurations | `s_fboConfigs[]` registers `fbo`, `fbo_msaa2`, `fbo_msaa4`, and `fbo_float` with sample counts `0`, `2`, `4`, and `0`, respectively, at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2020-L2030). `getVkSampleCount()` maps those counts to `VK_SAMPLE_COUNT_1_BIT`, `VK_SAMPLE_COUNT_2_BIT`, and `VK_SAMPLE_COUNT_4_BIT` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L688-L701). |
| Texture configurations | `s_textureConfigs[]` registers `basic`, `msaa4`, and `float` texture branches at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2032-L2041). Texture cases are generated only for non-subgroup functions at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2140-L2175). |
| Render size and surface format | `TriangleDerivateCaseInstance` uses `VIEWPORT_WIDTH` and `VIEWPORT_HEIGHT`, and maps `SURFACETYPE_FLOAT_FBO` to `GL_RGBA32UI` while other cases use `GL_RGBA8` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L711-L715). |
| Value ranges | Linear cases choose precision-dependent `coordMin` and `coordMax` values at [`LinearDerivateCase::LinearDerivateCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1220-L1239). Texture cases choose precision-dependent texture value ranges at [`TextureDerivateCase::TextureDerivateCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1519-L1538). |
| Long-vector branch | `linear_vec8` is compiled only when `CTS_USES_VULKANSC` is not defined, is generated only for `vec4`, and uses `GL_EXT_long_vector` shader text at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1942-L1960) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2089-L2091). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Shared ShaderRender support | Every `TriangleDerivateCase` calls `ShaderRenderCase::checkSupport(context)` before derivative-specific checks at [`TriangleDerivateCase::checkSupport()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L857-L860). |
| Dynamic-control-flow and subgroup-function cases | If a case is in non-uniform control flow or is a subgroup function, `TriangleDerivateCase::checkSupport()` requires fragment-stage quad operations, subgroup size at least 4, and `VK_SUBGROUP_FEATURE_BALLOT_BIT` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L861-L876). |
| Shader text using `gl_SubgroupInvocationID` | `LinearDerivateCase::createInstance()` repeats checks for fragment-stage quad operations and subgroup size at least 4 when the fragment template contains `gl_SubgroupInvocationID` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1270-L1281). |
| Demote cases | `output_store` and `private_store` set `demoteToHelperInvocation = true` in `s_linearDerivateCases[]` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1908-L1941); that flag requires `VK_EXT_shader_demote_to_helper_invocation` in `LinearDerivateCase::checkSupport()` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1173-L1179). |
| Long-vector cases | Outside Vulkan SC builds, `LinearDerivateCase::checkSupport()` requires the `longVector` feature when the generated `linear_vec8` case sets `m_longVec` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1180-L1185). |
| Subgroup shader extensions | The manual subgroup sources require `GL_KHR_shader_subgroup_quad` and `GL_KHR_shader_subgroup_ballot` in the generated fragment shaders at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1963-L1967) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1991-L1995). |

## Verification Methods

- `TriangleDerivateCaseInstance::iterate()` renders two triangles, obtains the result image, creates an error mask, calls the case's `verify()` method, logs the rendered image and failure mask when needed, and returns pass or image-comparison failure at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L763-L811).
- `verifyConstantDerivate()` decodes each pixel with `readDerivate()`, compares active components against `reference` within `threshold`, ignores inactive components through `getDerivateMask()`, optionally skips odd rows for demote-to-helper-invocation cases, and marks failed pixels in the error mask at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L390-L435).
- Constant cases expect a zero derivative reference and use the surface threshold divided by derivative scale at [`ConstantDerivateCaseInstance::verify()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L932-L940).
- Linear `dFdx*` and `dFdy*` cases compute a reference from `coordMax - coordMin` divided by result width or height, apply component direction scale, and first try `verifyConstantDerivate()`; if that fails, they recompute per-pixel legal ranges with interval arithmetic in `reverifyConstantDerivateWithFlushRelaxations()` at [`LinearDerivateCaseInstance::verify()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1071-L1138) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L455-L593).
- Linear `fwidth*` cases compute `abs(dx) + abs(dy)` and compare through `verifyConstantDerivate()` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1140-L1157).
- Texture verification ignores one-pixel image edges, compares only the interior subregion, and uses the same direct-compare-plus-interval-relaxation structure for `dFdx*` and `dFdy*` at [`TextureDerivateCaseInstance::verify()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1390-L1465). Texture `fwidth*` cases use `abs(dx) + abs(dy)` for the generated texture value ramp at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1467-L1481).
- Thresholds include precision-dependent derivative error from `getDerivateThreshold()` and per-surface thresholds from `getSurfaceThreshold()`; UNORM FBO surfaces allow `1/255`, while float FBO surfaces use zero surface threshold at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L345-L359) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L722-L733).

## Test Principles

- The direct registration hierarchy is function-oriented: `ShaderDerivateTests::init()` creates one group per `DerivateFunc` and adds it as a direct child of `glsl.derivate` at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2043-L2048) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2177-L2178).
- Non-subgroup functions exercise a broader matrix than subgroup functions: constant derivatives and texture derivatives are guarded by `!isSubgroupFunc(function)`, while the FBO matrix is generated for every function at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2050-L2175).
- The implementation separates source-expression coverage from render-target coverage: `s_linearDerivateCases[]` changes how the derivative operand is computed in shader control flow, while `s_fboConfigs[]` changes surface type and sample count at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1682-L1961) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2020-L2030).
- Verification is image-based and tolerance-aware, not a strict byte comparison: decoded derivative values are compared against references and thresholds, with interval-based relaxation for values affected by interpolation precision and flush-to-zero behavior at [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L390-L435) and [`vktShaderRenderDerivateTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L455-L593).

## Notes / Uncertainties

- The inspected source proves a generated registration matrix under `glsl.derivate`; this page does not infer additional generated case counts beyond the visible loops and guards in [`ShaderDerivateTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1680-L2179).
- The source uses the spelling `Derivate` in type and function names, while the GLSL concepts and shader functions are derivative operations.
