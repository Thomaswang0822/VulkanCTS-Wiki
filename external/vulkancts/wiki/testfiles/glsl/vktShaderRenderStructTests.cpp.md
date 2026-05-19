# Shader Struct Tests

## Overview

Tests GLSL struct declaration, initialization, member access, nested structs, struct arrays, and struct usage as function parameters and return values. Covers both local struct variables (declared and initialized within shader code) and uniform struct variables (provided via std140 uniform buffers). Validates correct struct layout, member access patterns, dynamic indexing of array members, and interaction with control flow constructs (conditional assignment, loop assignment).

## Role

Both registration and implementation. The `ShaderStructTests` class (line 2088) serves as the `TestCaseGroup` that registers the `glsl.struct` hierarchy, and the same source file contains the `ShaderStructCase` class (line 38), `LocalStructTests` (line 120), and `UniformStructTests` (line 1204).

Source: [vktShaderRenderStructTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp)

## Registration Hierarchy

```text
glsl.struct
├── local
└── uniform
```

## Test Families

- **ShaderStructCase** (line 38): Single test family for all struct tests. Extends `ShaderRenderCase` and is constructed with an evaluation function, a uniform setup function, and vertex/fragment shader source strings. The `createStructCase` helper (line 64) uses `tcu::StringTemplate` to specialize shader source templates based on the shader stage.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Struct scope | `local`, `uniform` | Whether the struct is a local variable or a uniform buffer member |
| Struct complexity | basic, nested, deeply_nested | Struct with simple members, nested struct members, or arrays of nested structs |
| Control flow | conditional, loop, dynamic_loop | Struct assignment within if-else, static loop, or dynamic loop |
| Shader stage | `vertex`, `fragment` | Shader stage under test (each case is instantiated for both) |

**Local struct test cases** (defined via `LOCAL_STRUCT_CASE` macro at line 136):
- `basic`: Simple struct with float, vec3, and int members
- `nested`: Struct containing another struct as a member
- `array_member`: Struct with a fixed-size array member
- `array_member_dynamic_index`: Array member accessed with dynamic (uniform) index
- `struct_array`: Array of structs
- `struct_array_dynamic_index`: Array of structs with dynamic indexing
- `nested_struct_array`: Array of structs containing nested struct arrays
- `nested_struct_array_dynamic_index`: Same with dynamic indexing
- `parameter`: Struct passed as function parameter
- `parameter_nested`: Nested struct passed as function parameter
- `return`: Struct returned from a function
- `return_nested`: Nested struct returned from a function
- `conditional_assignment`: Struct reassigned conditionally
- `loop_assignment`: Struct reassigned in a static loop
- `dynamic_loop_assignment`: Struct reassigned in a dynamic loop
- `nested_conditional_assignment`: Nested struct member reassigned conditionally
- `nested_loop_assignment`: Nested struct member reassigned in a loop

**Uniform struct test cases** (defined via `UNIFORM_STRUCT_CASE` macro at line 1220):
- `basic`, `nested`, `array_member`, `array_member_dynamic_index`, `struct_array`, `struct_array_dynamic_index`, `nested_struct_array`, `nested_struct_array_dynamic_index`: Mirror the local cases but with struct data provided via std140 uniform buffers

## Support/Feature Requirements

None beyond core Vulkan. All tests use standard GLSL 310 es features with std140 layout uniform buffers.

## Verification Methods

ShaderRenderCase-based reference comparison using custom evaluation and uniform setup functions. Each test case defines:
- An `eval` function that computes the expected output color from `ShaderEvalContext` (e.g., `c.color.xyz() = c.coords.swizzle(0, 1, 2)`)
- A `setUniforms` function that configures the uniform buffer data, including proper std140 padding for struct layout

For uniform struct tests, the uniform setup functions manually construct C++ structs with the correct std140 padding (e.g., `_padding` fields) and upload them via `instance.addUniform()` with `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER`.

## Notes

- Each test case is instantiated for both vertex and fragment shader stages (suffixed `_vertex` and `_fragment`).
- The `LOCAL_STRUCT_CASE` and `UNIFORM_STRUCT_CASE` macros (lines 136, 1220) generate both the uniform setup and evaluation functions using local struct definitions, ensuring type safety and reducing boilerplate.
- Uniform struct tests require careful std140 layout alignment. The C++ uniform setup code includes explicit padding fields to match the GLSL std140 layout rules (e.g., `float _padding1[3]` after a `float` member to align `vec3` to 16-byte boundaries).
- Dynamic indexing tests use integer uniforms (`ui_zero`, `ui_one`, `ui_two`) as array indices to test runtime indexing of struct array members.
