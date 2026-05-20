# Shader Indexing Tests

## Overview

Tests for GLSL array, vector, and matrix indexing operations in vertex and fragment shaders. Verifies correct behavior when accessing array elements, vector components, and matrix columns using various indexing methods including static indices, dynamic (variable) indices, and loop-based indices.

## Role

Both registration and implementation. The `ShaderIndexingTests` class (derived from `tcu::TestCaseGroup`) serves as the test group registrar and populates all child test cases in its `init()` method. Individual test cases are created via factory functions (`createVaryingArrayCase`, `createUniformArrayCase`, `createTmpArrayCase`, `createVectorSubscriptCase`, `createMatrixSubscriptCase`) that return `ShaderIndexingCase` instances.

## Source Code

[../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1-L1363)

## Registration Hierarchy

```text
glsl.indexing
├── varying_array
├── uniform_array
├── tmp_array
├── vector_subscript
└── matrix_subscript
```

## Test Families

- **VaryingArrayCase** - Tests indexing into varying arrays. Vertex shader writes to array elements using one access type, fragment shader reads using another. Parameterized by data type and vertex/fragment index access combinations.
- **UniformArrayCase** - Tests indexing into uniform arrays. Fragment or vertex shader reads array elements using various access types. Parameterized by data type, read access type, and shader stage.
- **TmpArrayCase** - Tests indexing into temporary (local) arrays. Both write and read access types are parameterized, along with data type and shader stage. Includes const index access.
- **VectorSubscriptCase** - Tests subscript-based indexing into vector components. Parameterized by vector type, write/read access types (direct, component, static/dynamic/loop subscript), and shader stage.
- **MatrixSubscriptCase** - Tests subscript-based indexing into matrix columns. Parameterized by matrix type, write/read access types, and shader stage.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| DataType (arrays) | float, vec2, vec3, vec4 | Element type for varying/uniform/tmp arrays |
| DataType (vector) | vec2, vec3, vec4 | Vector type for subscript tests |
| DataType (matrix) | mat2, mat2x3, mat2x4, mat3x2, mat3, mat3x4, mat4x2, mat4x3, mat4 | Matrix type for subscript tests |
| IndexAccessType | static, dynamic, static_loop, dynamic_loop, const | How the array index is computed (const only for tmp arrays) |
| VectorAccessType | direct, component, static_subscript, dynamic_subscript, static_loop_subscript, dynamic_loop_subscript | How vector component access is performed |
| ShaderType | vertex, fragment | Which shader stage performs the indexing |

### IndexAccessType Details

- **static**: Index is a compile-time constant
- **dynamic**: Index is computed from a varying/uniform value at runtime
- **static_loop**: Index is the loop counter in a compile-time bounded loop
- **dynamic_loop**: Index is the loop counter in a runtime-bounded loop
- **const**: Index is a const-qualified variable (tmp arrays only)

### VectorAccessType Details

- **direct**: Direct swizzle access (e.g., `v.x`)
- **component**: Component-level access (e.g., `v[0]`)
- **static_subscript**: Subscript with compile-time constant index
- **dynamic_subscript**: Subscript with runtime-computed index
- **static_loop_subscript**: Subscript with loop counter in compile-time bounded loop
- **dynamic_loop_subscript**: Subscript with loop counter in runtime-bounded loop

## Support/Feature Requirements

No additional requirements beyond core Vulkan.

## Verification Methods

- **ShaderRenderCase reference comparison**: Each test case uses a `ShaderEvaluator` function to compute the expected output color. For varying arrays, the evaluator scales the input coordinates by 1.875. For uniform arrays, the evaluator scales the const coordinates by 1.875. The rendered image is compared against the reference image produced by the evaluator.

## Notes

- Varying array tests combine vertex write access and fragment read access, producing a matrix of access type pairs (4x4 = 16 combinations per data type, excluding const access).
- Uniform array tests only parameterize read access (since the uniform data is written by the host), and additionally parameterize by shader stage.
- Tmp array tests include the `const` index access type for both write and read, yielding 5x4 = 20 combinations per data type and shader stage.
- Matrix subscript tests use the 9 non-square and square float matrix types (mat2 through mat4, including non-square variants).
