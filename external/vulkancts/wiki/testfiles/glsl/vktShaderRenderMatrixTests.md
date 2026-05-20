# Shader Matrix Tests

## Overview

Tests GLSL matrix arithmetic operations and built-in matrix functions. Covers binary operations (add, subtract, multiply, divide), component-wise multiplication, `outerProduct`, `transpose`, `determinant`, `inverse`, unary operations (negation, increment, decrement), and compound assignment operations. Tests are parameterized across all float matrix types (mat2 through mat4x4), precision qualifiers, input sources (constant, uniform, dynamic), and shader stages.

## Role

Both registration and implementation. The `ShaderMatrixTests` class (line 2326) serves as the `TestCaseGroup` that registers the `glsl.matrix` hierarchy, and the same source file contains the `ShaderMatrixCase` class (line 1934) and all evaluation logic.

Source: [vktShaderRenderMatrixTests.cpp](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp)

## Registration Hierarchy

```text
glsl.matrix
├── add
├── sub
├── mul
├── div
├── matrixcompmult
├── outerproduct
├── transpose
├── determinant
├── inverse
├── unary_addition
├── negation
├── pre_increment
├── pre_decrement
├── post_increment
├── post_decrement
├── add_assign
├── sub_assign
├── mul_assign
└── div_assign
```

## Test Families

- **ShaderMatrixCase** (line 1934): Single test family for all matrix operations. Each case is parameterized by two `ShaderInput` descriptors (input0 and input1), a `MatrixOp` operation, and the shader stage. The `setupShader` method (line 1974) generates GLSL source code tailored to the specific operation and input types. Evaluation is performed by `MatrixShaderEvaluator` which delegates to operation-specific template specializations in the `MatrixCaseUtils` namespace.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| MatrixOp | 19 operations (enum at line 323) | Matrix operation under test |
| InputType | `const`, `uniform`, `dynamic` | How matrix data is provided to the shader |
| MatrixType | mat2, mat2x3, mat2x4, mat3x2, mat3, mat3x4, mat4x2, mat4x3, mat4 | Matrix dimensions (line 2410) |
| Precision | `mediump`, `highp` | Precision qualifier (line 2414) |
| Shader stage | `vertex`, `fragment` | Shader stage under test |
| Operand combinations | mat-scalar, mat-vec, vec-mat, mat-mat | Determined by operation type via helper predicates (lines 553-604) |

**MatrixOp values** (line 323): `OP_ADD`, `OP_SUB`, `OP_MUL`, `OP_DIV`, `OP_COMP_MUL`, `OP_OUTER_PRODUCT`, `OP_TRANSPOSE`, `OP_INVERSE`, `OP_DETERMINANT`, `OP_UNARY_PLUS`, `OP_NEGATION`, `OP_PRE_INCREMENT`, `OP_PRE_DECREMENT`, `OP_POST_INCREMENT`, `OP_POST_DECREMENT`, `OP_ADD_INTO`, `OP_SUBTRACT_FROM`, `OP_MULTIPLY_INTO`, `OP_DIVIDE_INTO`.

**Operand applicability**:
- Arithmetic binary (add/sub/mul/div): mat-scalar, mat-vec, vec-mat, mat-mat
- Component-wise (matrixcompmult): mat-mat (same dimensions)
- Outer product: vec-vec
- Transpose/determinant/inverse/unary/assignment: single mat input
- Unary symmetric-only (inverse/determinant): square matrices only

## Support/Feature Requirements

None beyond core Vulkan. All tests use standard GLSL 310 es features.

## Verification Methods

ShaderRenderCase-based reference comparison. The `MatrixShaderEvaluator` (used in `ShaderMatrixCase` constructor at line 1956) computes reference results analytically using `tcu::Matrix` utilities. Operation-specific evaluation is performed by template specializations of the `Evaluator` struct (e.g., `Evaluator<OP_ADD>` at line 1134, `Evaluator<OP_TRANSPOSE>` at line 1224). The rendered output color (a vec3 reduction of the matrix result) is compared against the reference with appropriate floating-point tolerance.

## Notes

- Binary arithmetic operations (add, sub, mul, div) test three input types: constant, uniform, and dynamic. Other operations use only dynamic input (lines 2401-2408).
- Unary and assignment operations that require symmetric (square) matrices (inverse, determinant) are restricted to mat2, mat3, mat4 via `isOperationUnarySymmetricMatrix` and `isOperationAssignmentSymmetricMatrix` predicates (lines 2529, 2538).
- Division operations use uniform input for the divisor to avoid division by zero (line 2457).
- The `outerproduct` operation takes two vector inputs rather than matrix inputs (line 2517-2526).
