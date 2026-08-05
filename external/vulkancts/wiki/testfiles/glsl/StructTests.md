## Overview

`vktShaderRenderStructTests.cpp` implements the `glsl.struct` shader-render family. It tests GLSL ES 3.10 structures in two storage domains:

- `local`: structures created and manipulated in shader-local storage.
- `uniform`: structures read from `std140` uniform blocks.

Every semantic case is emitted twice: once with the tested code in the vertex shader and once with it in the fragment shader. The other shader is a small pass-through stage. Consequently, the family contains **80 leaves**: 26 local cases × 2 stages and 14 uniform cases × 2 stages.

The tests validate observable shader output, rather than merely compilation. A case writes a color assembled from selected structure members; the shared shader-render framework independently evaluates the expected color on the CPU and compares the rendered and reference images.

## Registration Hierarchy

```text
glsl.struct
├── local
└── uniform
```

[`ShaderStructTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L2108-L2113) adds `LocalStructTests` and `UniformStructTests`. The GLSL package registers the resulting group as `glsl.struct` in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1269).

`local` expands 26 base cases and `uniform` expands 14; each base case has `_vertex` and `_fragment` leaves.

`LOCAL_STRUCT_CASE` and `UNIFORM_STRUCT_CASE` each register `<name>_vertex` and `<name>_fragment` children. [`createStructCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L64-L118) specializes the generated shader source for the selected stage, supplying `a_coords` and `v_color` for a vertex case or `v_coords` and `o_color` for a fragment case.

## Test Matrix

| Dimension | Values | Notes |
|---|---|---|
| Structure storage | `local`, `uniform` | Local shader values versus values supplied through uniform buffers. |
| Tested shader stage | `vertex`, `fragment` | Every base case has one variant per stage. |
| Local base cases | 26 | Construction, nesting, array access, functions, assignments, loops, and comparisons. |
| Uniform base cases | 14 | `std140` layout, nested/array access, loops, and comparisons. |
| Dynamic selectors | `ui_zero` through `ui_three` as applicable | Used as array indices, loop bounds, or comparison inputs. |
| Mustpass coverage | 80 leaves each in `vk-default` and `vksc-default` | All registered stage variants occur in both lists. |

The local registration is defined by [`LOCAL_STRUCT_CASE`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L136-L153) and its invocations through [`LocalStructTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L155-L1201). The uniform equivalents are [`UNIFORM_STRUCT_CASE`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1220-L1238) and [`UniformStructTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1240-L2085).

## `local`: Shader-Local Structures

The local family constructs structures inside the selected shader and checks that member selection, whole-structure operations, and array accesses produce the expected color.

### Construction, nesting, and arrays

- `basic` constructs `S` containing a `float`, `vec3`, and `int`, then writes a vector member after construction.
- `nested` places `T` inside `S` and selects fields at both nesting levels.
- `array_member` and `array_member_dynamic_index` access a `float b[3]` structure member with literal and uniform-derived indices.
- `struct_array` and `struct_array_dynamic_index` access elements of `S[3]` using literal and uniform-derived indices.
- `nested_struct_array` and `nested_struct_array_dynamic_index` traverse `S[2]`, whose members contain `T[3]`, whose members contain `vec2[2]`.

These cases cover both direct member syntax and combinations of member selection with array indexing. See [`basic`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L155-L174), [`nested`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L176-L204), and the array cases through [`nested_struct_array_dynamic_index`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L206-L475).

### Functions and assignment

Only the local family tests passing and returning structures through functions:

- `parameter`, `parameter_nested`
- `return`, `return_nested`

The assignment cases exercise whole-structure and nested-member updates in control flow:

- `conditional_assignment`, `loop_assignment`, `dynamic_loop_assignment`
- `nested_conditional_assignment`, `nested_loop_assignment`, `nested_dynamic_loop_assignment`

The dynamic forms source an integer control value from a uniform. The function cases are implemented at [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L477-L599); the assignment cases follow at [`#L601-L797`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L601-L797).

### Loops and equality

`loop_struct_array`, `loop_nested_struct_array`, `dynamic_loop_struct_array`, and `dynamic_loop_nested_struct_array` accumulate values while iterating over arrays of structures. Fixed-loop variants use literal bounds; dynamic variants use uniform bounds. [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L799-L1047)

`basic_equal`, `basic_not_equal`, `nested_equal`, and `nested_not_equal` check `==` and `!=` on structures with scalar/vector/integer members and on nested structures. Their evaluator callbacks encode the expected Boolean results in output channels. [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1049-L1201)

## `uniform`: `std140` Uniform-Block Structures

The uniform family declares structures in `layout(std140, set = 0, binding = …) uniform` blocks. Its setup callback uploads C++ mirror data using `ShaderRenderCaseInstance::addUniform()`, so these cases test shader reads together with the expected uniform-buffer layout.

### Layout-sensitive structure shapes

`basic` and `nested` read the same broad shapes used by the local family. The host-side mirrors include explicit padding where necessary to match `std140` placement. [`basic`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1240-L1275) [`nested`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1277-L1327)

The remaining access shapes are:

- `array_member`, `array_member_dynamic_index`
- `struct_array`, `struct_array_dynamic_index`
- `nested_struct_array`, `nested_struct_array_dynamic_index`

These use literal and uniform-driven indices to read arrays inside a uniform structure, arrays of uniform structures, and nested arrays. The nested case again has the `S[2] → T[3] → vec2[2]` shape, with padded host-side representations. [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1329-L1655)

### Loop and comparison cases

The four loop cases have the same fixed/dynamic and simple/nested axes as the local family:

- `loop_struct_array`, `loop_nested_struct_array`
- `dynamic_loop_struct_array`, `dynamic_loop_nested_struct_array`

They iterate over values read from uniform buffers. [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1657-L1961)

`equal` and `not_equal` compare uploaded `S` instances and an `S` constructed in GLSL. Unlike the local group, the uniform group does not split these into basic and nested comparison names. [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1963-L2085)

## Execution and Result Checking

Each leaf is a `ShaderStructCase`, a small wrapper around the shared [`ShaderRenderCase`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L575-L633). It supplies stage-specialized GLSL source, an evaluator callback, and a uniform-setup callback. [`ShaderStructCase`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L38-L58)

At execution time, `ShaderRenderCaseInstance::iterate()`:

1. renders the generated vertex/fragment pair;
2. computes a software reference with the vertex or fragment evaluator for the selected stage; and
3. compares reference and rendered images.

The shared implementation is at [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L806), with reference evaluation at [`#L2603-L2719`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2719) and image comparison at [`#L2721-L2730`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730).

For local cases, the reference normally derives the color from interpolated coordinates. For uniform cases, setup callbacks populate data from constant coordinates, and the reference consequently derives from those constant values. Integer uniforms are installed with `useUniform()`; descriptor-backed uniform data is installed with `addUniform()`. [`ShaderRenderCaseInstance::useUniform()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L977) [`ShaderRenderCaseInstance::addUniform()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L858-L865)

## Interpreting Failures

A failure is a rendered-image mismatch against the case evaluator. It demonstrates that the complete tested path did not produce the expected observable color; it does not by itself identify one faulty compiler pass or Vulkan component.

| Failing area | Likely paths implicated |
|---|---|
| Local construction/nesting | Structure construction, member access, nested selection, or selected-stage execution. |
| Dynamic indexing | Uniform delivery, dynamic index handling, array/member addressing, or selected-stage execution. |
| Function/assignment cases | Structure parameter/return handling, copies, conditional or loop assignment. |
| Uniform cases | GLSL uniform access, `std140` placement, descriptor upload/binding, host-side padding, or selected-stage execution. |
| Equality cases | Structure comparison semantics, component comparison, or Boolean-to-color encoding. |
| Vertex-only failures | Vertex execution or forwarding through the stage interface, in addition to the tested structure operation. |
| Fragment-only failures | Fragment-stage execution or coordinate forwarding, in addition to the tested structure operation. |

The file has no structure-specific `checkSupport()` override or feature gate. Cases rely on the common ShaderRender GLSL ES 3.10 compilation, descriptor, pipeline, and rendering path. [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L38-L2120)

## Source Reference Appendix

- Structure case wrapper and stage specialization: [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L38-L118)
- Local registration and test generation: [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L120-L1201)
- Uniform registration and test generation: [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1204-L2085)
- Root `glsl.struct` registration: [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L2088-L2113)
- Public factory declaration: [`vktShaderRenderStructTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.hpp#L22-L35)
- Shared ShaderRender execution: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L575-L633), [`#L773-L806`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L806)
- GLSL-category registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1269)
- Vulkan default mustpass entries: [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt)
- Vulkan SC default mustpass entries: [`glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt)
