## Overview

[`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L1-L529) implements the `glsl.return` ShaderRenderCase-based test group. [`createReturnTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L523-L526) creates the `return` group, which is registered below the GLSL package in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1268).

The page covers GLSL `return` statements in helper functions and `main()`, returns between output writes, returns inside finite loops, and a return from a loop whose increment is supplied by a zero-valued uniform. Every behavior is tested in both vertex and fragment stages. The shader writes coordinate-derived colors, and the shared render harness compares the result with a CPU evaluator.

## Registration Hierarchy

The public factory is declared in [`vktShaderRenderReturnTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.hpp#L27-L35). The implementation and all shader generators are in the single primary source file. It uses the shared [`ShaderRenderCase`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L577-L632) rendering infrastructure; there is no separate per-case shader file.

```text
glsl.return
├── single_return_vertex
├── single_return_fragment
├── conditional_return_always_vertex
├── conditional_return_always_fragment
├── conditional_return_never_vertex
├── conditional_return_never_fragment
├── conditional_return_dynamic_vertex
├── conditional_return_dynamic_fragment
├── double_return_vertex
├── double_return_fragment
├── last_statement_in_main_vertex
├── last_statement_in_main_fragment
├── output_write_in_func_always_vertex
├── output_write_in_func_always_fragment
├── output_write_in_func_never_vertex
├── output_write_in_func_never_fragment
├── output_write_in_func_dynamic_vertex
├── output_write_in_func_dynamic_fragment
├── output_write_always_vertex
├── output_write_always_fragment
├── output_write_never_vertex
├── output_write_never_fragment
├── output_write_dynamic_vertex
├── output_write_dynamic_fragment
├── return_in_static_loop_always_vertex
├── return_in_static_loop_always_fragment
├── return_in_static_loop_never_vertex
├── return_in_static_loop_never_fragment
├── return_in_static_loop_dynamic_vertex
├── return_in_static_loop_dynamic_fragment
├── return_in_dynamic_loop_always_vertex
├── return_in_dynamic_loop_always_fragment
├── return_in_dynamic_loop_never_vertex
├── return_in_dynamic_loop_never_fragment
├── return_in_dynamic_loop_dynamic_vertex
├── return_in_dynamic_loop_dynamic_fragment
├── return_in_infinite_loop_vertex
└── return_in_infinite_loop_fragment
```

`ShaderReturnTests::init()` registers the direct leaves at [`vktShaderRenderReturnTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L344-L519). The default Vulkan and Vulkan SC mustpass lists each contain 38 normalized `glsl.return` leaves: [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt) and [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt).

## Test families

### Single, conditional, and repeated returns

- `single_return_vertex` and `single_return_fragment` call `getColor()`, whose only return produces `coords.xyz`. The vertex case reads `a_coords`; the fragment case reads the pass-through `v_coords` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L346-L375)).
- `conditional_return_<mode>_<stage>` is generated for the three modes `always`, `never`, and `dynamic` ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L377-L387)). The helper returns `coords.xyz` when the condition is true and `coords.wzy` otherwise ([generator](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L139-L187)). The conditions are respectively `true`, `false`, and `coords.x + coords.y >= 0.0`.
- `double_return_vertex` and `double_return_fragment` place two unconditional returns in `getColor()`. The first returns `coords.xyz`; the second `coords.wzy` is unreachable ([source](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L390-L421)).
- `last_statement_in_main_<stage>` writes `coords.xyz` and then executes `return;` as the final statement in `main()` ([source](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L423-L447)).

### Returns between output writes

`output_write_<mode>_<stage>` and `output_write_in_func_<mode>_<stage>` cover the same sequence in `main()` or in `myfunc()`. The shader first writes `coords.xyz`, conditionally returns, and otherwise overwrites the output with `coords.wzy` ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L449-L463); [generator](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L189-L249)). Thus an early return preserves the first write, while a fall-through path is observable through the second write.

### Returns inside finite loops

`return_in_static_loop_<mode>_<stage>` and `return_in_dynamic_loop_<mode>_<stage>` are generated for all three return modes and both stages ([registration](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L465-L479)). `getCoords()` starts with the coordinate vector and executes a loop with:

- static bound: literal `1`;
- dynamic bound: uniform `ui_one`.

Inside the loop, the selected condition returns the current coordinates. If it is false, the shader applies `coords = coords.wzyx` and eventually returns the resulting vector after the loop ([generator](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L251-L306)). The finite-loop cases use `ReturnTestUniformSetup(UI_ONE)`.

### Return from a zero-increment loop

`return_in_infinite_loop_vertex` and `return_in_infinite_loop_fragment` declare `ui_zero` and use `for (int i = 1; i < 10; i += ui_zero)`. The loop body immediately returns the input coordinates, so with the uniform value zero the implementation must still terminate through the return rather than hang. The fallback `coords.wzyx` return is unreachable in the executed configuration ([source](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L481-L518)). These cases use `ReturnTestUniformSetup(UI_ZERO)`.

## Parameter dimensions

| Dimension | Values / effect |
|---|---|
| Return mode | `always`, `never`, `dynamic`; names come from [`getReturnModeName()`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L308-L322). |
| Shader stage | `vertex` or `fragment`; generated names receive the corresponding suffix. |
| Return location | Helper function, `main()`, output-write sequence, finite loop, or zero-increment loop. |
| Output-write placement | Directly in `main()` or inside `myfunc()`. |
| Loop bound | Literal `1` or uniform `ui_one`. |
| Loop increment | Uniform `ui_zero` for the zero-increment cases. |
| Coordinate input | Vertex shaders use high-precision `a_coords` at location 1; fragment shaders use interpolated mediump `v_coords` at location 0. |

The `ShaderReturnCase` wrapper installs the selected source in the tested stage and supplies a pass-through shader for the other stage ([constructor](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L79-L116)). `ReturnTestUniformSetup` binds one integer uniform at binding 0; the shared [`useUniform()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L965) path supplies `UI_ZERO` as 0 and `UI_ONE` as 1.

## Shader generation and expected behavior

All generated programs use `#version 310 es`. Vertex variants write `gl_Position` and a color varying; fragment variants write the color output directly. The return conditions are inserted into templates by the three builders ([conditional](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L139-L187), [output-write](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L189-L249), and [loop](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L251-L306)).

The CPU reference functions define the observable result:

| Evaluator | Reference RGB |
|---|---|
| `evalReturnAlways()` | `coords.xyz` |
| `evalReturnNever()` | `coords.wzy` |
| `evalReturnDynamic()` | `coords.xyz` when `coords.x + coords.y >= 0.0`, otherwise `coords.wzy` |

These functions are selected by [`getEvalFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderReturnTests.cpp#L49-L77), matching the condition used in shader generation. Alpha is supplied by the shader-side `vec4(..., 1.0)` output construction.

## Support requirements and execution

No return-specific `checkSupport()` override or extension requirement is present in the inspected source. Cases use the common ShaderRender path. Uniform-backed cases require the shared uniform-buffer/render infrastructure, but do not introduce a return-family feature gate.

At execution, [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) renders the generated programs, copies the result image, computes a vertex- or fragment-stage reference using the selected evaluator, and compares the images with `compareImages(resImage, refImage, 0.2f)`. The comparison uses the shared fuzzy image-comparison path ([instance setup](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L658-L683); [comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

A passing case establishes that the rendered color matches the expected return-path behavior within the harness threshold. A failing image does not by itself distinguish return-statement lowering from shader compilation/linking, stage-interface passing, interpolation/rasterization, or another shared render-harness issue.

## Coverage summary

| Family | Leaves |
|---|---:|
| Single return | 2 |
| Conditional helper return | 3 modes × 2 stages = 6 |
| Double return | 2 |
| Final return in `main()` | 2 |
| Output write / return / output write | 2 placements × 3 modes × 2 stages = 12 |
| Return in finite loop | 2 loop bounds × 3 modes × 2 stages = 12 |
| Return in zero-increment loop | 2 |
| **Total** | **38** |

## Notes and limitations

- The page documents runtime-generated GLSL; there are no standalone per-leaf shader files.
- The “infinite loop” cases are intentionally safe because the loop body returns before a second iteration can occur. Their purpose is to exercise return control flow in a loop with a zero increment, not to run an unbounded shader loop to completion.
- The observed mustpass entries confirm 38 leaves for both Vulkan and Vulkan SC, but mustpass membership is not a substitute for running the tests on a device.
- An image mismatch is an observable failure of the complete generated-shader/render/reference path and should not be interpreted as proof of one isolated compiler or runtime defect.
