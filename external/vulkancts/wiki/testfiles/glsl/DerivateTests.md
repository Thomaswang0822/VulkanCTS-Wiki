## Overview

**Core question:** Do fragment-shader derivative operations produce the expected spatial differences across expression, precision, render-target, and texture variants?

- `vktShaderRenderDerivateTests.cpp` implements and registers the `glsl.derivate` test family. It creates cases for the standard, fine, coarse, and subgroup forms of `dFdx` and `dFdy`, plus the corresponding `fwidth` forms.
- The cases draw a two-triangle quad, read the color image, decode the derivative value from each pixel, and compare it with a host-computed reference.
- Non-subgroup functions cover constant expressions, linear expressions in several control-flow contexts, framebuffer configurations, and textures. Subgroup functions use the framebuffer configurations and explicit quad broadcasts.
- This page explains the registered hierarchy, the generated matrix, shader behavior, host-side checking, and the limits of what a failure identifies.

## Background Knowledge

- Fragment derivatives estimate how a fragment value changes across neighboring fragments in a 2x2 fragment quad. `dFdx` uses the horizontal direction, `dFdy` the vertical direction, and `fwidth` combines the absolute x and y derivatives.
- Fine and coarse derivatives may select different implementation grouping rules. The test therefore checks them against the same analytically derived ramp where the source and render target make that comparison meaningful.
- A subgroup quad operation lets a shader explicitly obtain values from the four invocations in a quad. The subgroup variants use those broadcasts to form horizontal or vertical differences rather than calling the built-in derivative function.
- Interpolation and reduced-precision arithmetic can change the representable result. The verifier uses tolerances and a second interval-based check for precision and flush-to-zero effects instead of requiring every pixel to match a single float exactly.

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

`ShaderDerivateTests::init()` iterates the eleven `DerivateFunc` values and adds one direct test family for each value. The deeper generated leaves are described below rather than expanded in this parseable hierarchy.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Derivative function | `dfdx`, `dfdxfine`, `dfdxcoarse`, `dfdxsubgroup`, `dfdy`, `dfdyfine`, `dfdycoarse`, `dfdysubgroup`, `fwidth`, `fwidthfine`, `fwidthcoarse` | Selects the derivative operation or the explicit subgroup implementation and the host reference formula. | [`DerivateFunc`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L77-L94), [`getDerivateFuncCaseName()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L138-L168) |
| Data type | `float`, `vec2`, `vec3`, `vec4` | Selects the number of derivative components written to the output. | [`ShaderDerivateTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2056-L2060) |
| Precision | `lowp`, `mediump`, `highp` | Changes the GLSL precision used by the derivative expression and the allowed error. | [`ShaderDerivateTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2075-L2087) |
| Linear source context | `linear`, `in_function`, `static_if`, `static_loop`, `static_switch`, `uniform_if`, `uniform_loop`, `uniform_switch`, `dynamic_if`, `dynamic_loop`, `dynamic_switch`, `output_store`, `private_store`, and, outside Vulkan SC, `linear_vec8` | Places the derivative expression in direct code, a function, control flow, a stored output, a private variable, or an eight-component long vector. | [`s_linearDerivateCases[]`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1690-L1961) |
| Framebuffer configuration | `fbo`, `fbo_msaa2`, `fbo_msaa4`, `fbo_float` | Selects an UNORM or float-backed render target and one, two, or four samples. | [`s_fboConfigs[]`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2020-L2030) |
| Texture configuration | `basic`, `msaa4`, `float` | Selects the texture ramp and its sample count or float surface. Non-subgroup functions only. | [`s_textureConfigs[]`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2032-L2041), [`init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2140-L2174) |
| Render surface | `GL_RGBA8` for ordinary cases, `GL_RGBA32UI` for `fbo_float` and `float` configurations | Encodes the calculated derivative into the image that the host reads back. | [`TriangleDerivateCaseInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L711-L715) |

The active generated matrix is also recorded in both mustpass profiles: `vk-default` contains 1,674 `glsl.derivate` leaves, while `vksc-default` contains 1,656. The 18-leaf difference is the non-Vulkan-SC `linear_vec8` configuration: it contributes two leaves, `vec4_highp` and `vec4_mediump`, for each of the three `dFdx*`, three `dFdy*`, and three `fwidth*` non-subgroup functions. The `lowp` leaf is skipped by the linear-case rule. The exact spans are [`vk-default/glsl.txt#L5280-L6953`](../../../mustpass/main/vk-default/glsl.txt#L5280-L6953) and [`vksc-default/glsl.txt#L4379-L6034`](../../../mustpass/main/vksc-default/glsl.txt#L4379-L6034).

## Behavior Parameters

The primary behavioral axis is the derivative function. The source maps each registered name to a GLSL spelling and chooses the corresponding verification path.

### `dfdx`, `dfdxfine`, and `dfdxcoarse`: horizontal derivatives

These functions measure the x-direction change of the interpolated or sampled ramp. Linear and texture cases divide the value range by the image width, then apply the component scale. The fine and coarse forms retain the same source ramp but exercise their distinct GLSL operation names. [`isDfdxFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L170-L174) selects this branch.

### `dfdy`, `dfdyfine`, and `dfdycoarse`: vertical derivatives

These functions use the y direction. The reference divides the value range by the image height and applies the y component scale. The source classifies these values through [`isDfdyFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L176-L180).

### `dfdxsubgroup`: explicit horizontal quad difference

The shader broadcasts the left and right members of a subgroup quad and returns `right - left`. The framebuffer matrix still varies data type, precision, surface, and sample count, but constant, linear-context, and texture groups are not generated for subgroup functions. [`dFdxSubgroupSource`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1963-L1989) supplies the source.

### `dfdysubgroup`: explicit vertical quad difference

The shader broadcasts the top and bottom members of a subgroup quad and returns `bottom - top`. It uses the same framebuffer-only generation rule as `dfdxsubgroup`. [`dFdySubgroupSource`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1991-L2018) supplies the source.

### `fwidth`, `fwidthfine`, and `fwidthcoarse`: combined width derivatives

These functions use `abs(dx) + abs(dy)` as the expected result. The source selects this formula with [`isFwidthFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L182-L185). They receive the non-subgroup constant, linear, framebuffer, and texture families.

## Shader Analysis

The implementation builds GLSL strings from templates. One representative linear shader is the direct `linear` case: it receives an interpolated `v_coord`, evaluates `${FUNC}(v_coord)`, applies a uniform scale and bias, and writes the result to the color output. The control-flow variants keep that derivative expression but move it into a function, static or uniform control flow, non-uniform control flow, or a value stored through an output or private variable. The source template is visible at [`s_linearDerivateCases[]`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1690-L1961).

The subgroup cases are a separate source shape. `dFdxSubgroup` chooses horizontal members with `subgroupQuadBroadcast()`, while `dFdySubgroup` chooses vertical members. Both then feed the result through the same scale, bias, and color-output path. These are explicit quad-difference shaders, not reconstructions of the implementation's built-in derivative operation.

No generated SPIR-V artifact is published in this page. The source strings are specialized during case construction with the selected function, data type, precision, output type, and surface configuration.

## Runtime Execution and Result Checking

- The case creates a `99 x 133` render target, renders the two triangles that form the test quad, obtains the result image, and creates an error mask. [`TriangleDerivateCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L763-L811) calls the case-specific `verify()` implementation.
- Constant cases use a zero derivative reference. Linear cases derive the expected x or y slope from `coordMax - coordMin`; `fwidth` cases add the absolute x and y slopes. Texture cases use their generated texture ramp and ignore the one-pixel border when checking the interior.
- `readDerivate()` removes the output bias and scale before comparison. The verifier checks only the active components for `float` through `vec4`; inactive output components do not affect the result.
- The first comparison uses precision- and surface-dependent thresholds. If a linear or texture derivative fails that comparison, the implementation retries with interval bounds that model interpolation precision and flush-to-zero behavior. [`reverifyConstantDerivateWithFlushRelaxations()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L455-L593) implements that fallback.
- A failing pixel is recorded in the error mask. The instance logs the rendered image and mask and returns a test failure; a case that satisfies the selected comparison returns pass.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `dfdx`, `dfdxfine`, or `dfdxcoarse` | Incorrect horizontal derivative grouping or value, interpolation/precision handling, or render-target integration. |
| `dfdy`, `dfdyfine`, or `dfdycoarse` | Incorrect vertical derivative grouping or value, interpolation/precision handling, or render-target integration. |
| `dfdxsubgroup` | Incorrect subgroup quad selection, broadcast, or horizontal difference, or subgroup-to-fragment integration. |
| `dfdysubgroup` | Incorrect subgroup quad selection, broadcast, or vertical difference, or subgroup-to-fragment integration. |
| `fwidth`, `fwidthfine`, or `fwidthcoarse` | Incorrect combination of x and y derivative magnitudes, precision handling, or render-target integration. |
| Any registered function | Shader compilation, feature support, draw/setup, image readback, or host verification can fail before the function-specific comparison completes. |

### Cause Analysis

#### Derivative value or grouping failures

**Possible failure symptoms:** The decoded image differs from the expected horizontal, vertical, or combined derivative outside the allowed threshold. The error mask identifies the affected pixels, and texture tests can report failures only in the checked interior.

**Possible implementation causes:** The fragment derivative operation may form neighborhoods or coarse groups differently from the assumptions exercised by the case, or the compiler may lower the expression incorrectly. The source and oracle do not isolate a particular driver stage.

#### Explicit subgroup quad failures

**Possible failure symptoms:** `dfdxsubgroup` or `dfdysubgroup` produces a value different from the difference between the selected quad members.

**Possible implementation causes:** The implementation may expose incompatible subgroup quad ordering, mishandle `subgroupQuadBroadcast()`, or integrate subgroup results incorrectly in the fragment stage. The check does not by itself distinguish those possibilities.

#### Precision and render-target failures

**Possible failure symptoms:** Failures cluster in `lowp` or `mediump` cases, UNORM surfaces, float surfaces, multisample configurations, or pixels near texture edges. A value can pass the relaxed interval check even when it misses the single nominal reference.

**Possible implementation causes:** Interpolation precision, arithmetic precision, conversion into the selected color format, multisample evaluation, or image readback can change the decoded value. Source inspection is needed to localize a failure beyond these observable conditions.

#### Setup, support, or readback failures

**Possible failure symptoms:** The case is reported unsupported before execution, shader or graphics setup rejects the case, image acquisition fails, or the host cannot obtain the expected render result.

**Possible implementation causes:** The device may lack the required subgroup, ballot, demote, or long-vector capability, or the graphics and readback path may reject or corrupt the case. A support rejection is a skip, not evidence of a derivative arithmetic failure.

## Case Pruning

### Requirement-based pruning

- `ShaderRenderCase::checkSupport()` runs before the derivative-specific checks. Dynamic-control-flow cases and subgroup functions require fragment-stage quad operations, subgroup size at least 4, and subgroup ballot support. [`TriangleDerivateCase::checkSupport()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L857-L876)
- `output_store` and `private_store` require `VK_EXT_shader_demote_to_helper_invocation`; their shaders demote some fragments to helper invocations. [`LinearDerivateCase::checkSupport()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1173-L1179)
- `linear_vec8` requires the long-vector feature and is unavailable in Vulkan SC because its registration is inside `#ifndef CTS_USES_VULKANSC`. [`linear_vec8`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1942-L1960)

### Design-based pruning

- Constant, linear-context, and texture groups are omitted for `dfdxsubgroup` and `dfdysubgroup` because those functions use dedicated subgroup source and are generated through the framebuffer loop only.
- `lowp` is omitted from non-basic linear cases and from UNORM framebuffer or texture configurations because the source notes that those render paths do not produce usable low-precision bits. Float-backed configurations retain `lowp`.
- `linear_vec8` is generated only for `vec4`; the shader creates an eight-component long vector and combines its two four-component halves before writing the result.

## Key Takeaways

- The test family changes derivative behavior through the registered function, while source context, precision, surface, sampling, and vector width provide the surrounding matrix.
- Subgroup derivative names are implemented with explicit quad broadcasts and are not generated through the ordinary linear and texture paths.
- The host oracle checks decoded image values with tolerances and a flush-to-zero relaxation, so a failure means the result escaped the comparison contract rather than simply differing bit-for-bit.
- Vulkan SC and the default profile intentionally differ by the `linear_vec8` family. The mustpass counts record that compile-time partition.

## Source Reference Appendix

| Entry point | Link |
|---|---|
| GLSL category registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1255) |
| Public factory declaration and factory definition | [`vktShaderRenderDerivateTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.hpp#L31-L37), [`createDerivateTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L2183-L2186) |
| Function enumeration and names | [`DerivateFunc`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L77-L168) |
| Generated registration matrix | [`ShaderDerivateTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1680-L2178) |
| Linear shader templates and compile-time exclusion | [`s_linearDerivateCases[]`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1690-L1961) |
| Explicit subgroup shader templates | [`dFdxSubgroupSource`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1963-L2018) |
| Support checks | [`TriangleDerivateCase::checkSupport()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L857-L876), [`LinearDerivateCase::checkSupport()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L1173-L1185) |
| Image verification and fallback interval checks | [`verifyConstantDerivate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L390-L435), [`reverifyConstantDerivateWithFlushRelaxations()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L455-L593) |
| Runtime render and result handling | [`TriangleDerivateCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRenderDerivateTests.cpp#L763-L811) |
| Default-profile coverage | [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L5280-L6953) |
| Vulkan SC coverage | [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L4379-L6034) |
