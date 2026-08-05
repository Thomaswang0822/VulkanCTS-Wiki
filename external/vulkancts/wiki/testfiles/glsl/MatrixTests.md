## Overview

`vktShaderRenderMatrixTests.cpp` implements `glsl.matrix`, a shader-render family for GLSL ES matrix operators and built-in functions. Each case generates a GLSL ES 3.10 vertex or fragment shader, renders its result, and compares that image with a host-side evaluator. `createMatrixTests()` creates the `matrix` group, and the GLSL package adds it below `glsl` ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2326-L2559), [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1265)).

The family covers arithmetic, component-wise multiplication, `outerProduct`, `transpose`, `determinant`, `inverse`, unary operators, increment/decrement, and compound assignment. Its registration code selects only operand shapes that GLSL permits.

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

`ShaderMatrixTests::init()` defines these nineteen operation groups in its `ops[]` table ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2347-L2394)). The first nine groups create an input-source subgroup. For `add`, `sub`, `mul`, and `div`, those subgroups are `const`, `uniform`, and `dynamic`. `matrixcompmult`, `outerproduct`, `transpose`, `determinant`, and `inverse` create only `dynamic`. The remaining unary and assignment groups put dynamic leaves directly below their operation group ([`#L2401-L2438`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2401-L2438)).

## Generated Case Dimensions

| Dimension | Values |
|---|---|
| Matrix types | `mat2`, `mat2x3`, `mat2x4`, `mat3x2`, `mat3`, `mat3x4`, `mat4x2`, `mat4x3`, `mat4` |
| Precision | `mediump`, `highp` |
| Shader stage | `vertex`, `fragment` |
| Extended input source | `const`, `uniform`, `dynamic` for add, subtract, multiply, and divide |
| Reduced input source | `dynamic` for the other groups that expose an input-source subgroup |

The registration loop crosses the applicable dimensions and appends `_vertex` or `_fragment` to each leaf name ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2410-L2463), [`#L2491-L2547`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2491-L2547)). Names begin with precision and the first operand type, such as `highp_mat3_float_vertex` for a matrix-scalar case.

## Operation Families

### Arithmetic and component-wise operations

- **`add`, `sub`, and `div`** generate matrix-scalar and same-shape matrix-matrix cases. The matrix-matrix form tests GLSL's component-wise operator semantics.
- **`mul`** adds the valid multiplication forms: matrix-scalar, matrix-vector, vector-matrix, and arithmetic matrix-matrix cases. The registration enters only the arithmetic branch ([`isOperationArithmeticMatrixMatrix()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L561-L564)); although `OP_MUL` also satisfies the component-wise predicate, the `if/else if` chain means no component-wise `mul` cases are generated.
- **`matrixcompmult`** tests `matrixCompMult(a, b)` with two matrices of the same shape.

For arithmetic matrix multiplication, the second matrix has row count equal to the first matrix's column count and column count from two through four. This permits every valid result width ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2465-L2515)). `div` uses a uniform scalar second operand, avoiding dynamically varying divisors ([`#L2454-L2462`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2454-L2462)).

### Matrix built-ins

- **`outerproduct`** tests `outerProduct(vecRows, vecCols)`. The generated vector sizes follow the current matrix shape.
- **`transpose`** accepts every matrix shape and produces the corresponding rows-by-columns-swapped type.
- **`determinant`** and **`inverse`** run only on square matrices.

The result of `determinant` is a scalar. The other built-ins return a matrix, including a differently shaped matrix for `transpose` ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2517-L2535), [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2001-L2017)). The instance setup adjusts inverse inputs and uses a smaller grid (64 instead of the default 90) for vertex-stage inverse cases so the test avoids singular or uninformative matrices ([`ShaderMatrixInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1701-L1728)).

### Unary and mutation operators

`unary_addition` and `negation` run on every matrix type. The increment and decrement groups test both prefix and postfix forms:

- `pre_increment`, `pre_decrement`
- `post_increment`, `post_decrement`

Mutation cases copy the operand into a temporary, apply the operator, and reduce both the expression result and the temporary's final value. This distinguishes prefix from postfix behavior while also checking the side effect ([`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2197-L2262)).

### Compound assignment

`add_assign`, `sub_assign`, and `div_assign` apply to all matrix shapes. `mul_assign` applies only to square matrices because `a *= b` requires a result that can be assigned back to `a`. Assignment cases initialize a result from the first matrix and emit the compound assignment against the second matrix ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2538-L2547), [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2207-L2249)).

## Operand and Input Rules

The operation predicates enforce the legal operand categories ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L551-L605)):

| Operand category | Operations |
|---|---|
| Matrix-scalar | `add`, `sub`, `mul`, `div` |
| Matrix-vector and vector-matrix | `mul` |
| Arithmetic matrix-matrix | `mul` |
| Same-shape component-wise matrix-matrix | `add`, `sub`, `mul`, `div`, `matrixcompmult` |
| Vector-vector | `outerproduct` |
| Unary, any matrix shape | `transpose`, unary plus/minus, increment/decrement |
| Unary, square only | `determinant`, `inverse` |
| Assignment, any matrix shape | add, subtract, divide assignment |
| Assignment, square only | multiply assignment |

A generated case does not use two dynamic matrix-like inputs. When its first input is dynamic, the registration code changes the second matrix or vector to uniform. Shader setup asserts the same constraint ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2491-L2521), [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1980-L1993)).

## Shader Data Flow

The generated shaders begin with `#version 310 es`. Constant operands become GLSL constructors; uniform operands are declared in `std140` uniform blocks; dynamic inputs come from vertex attributes. A fragment-stage dynamic input passes through a vertex-to-fragment varying. Matrix attributes consume the locations required by their column vectors ([`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2048-L2111)).

The shader converts every scalar, vector, or matrix result into an RGB value with `genGLSLMatToVec3Reduction()`. This gives the common image-comparison path a `vec4` color regardless of the original result type ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2255-L2323)). `ShaderMatrixInstance::setupUniforms()` supplies uniform scalars, vectors, and matrices, while its attribute setup supplies dynamic matrix data ([`ShaderMatrixInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1765-L1775), [`#L1870-L1905`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1870-L1905)).

## Reference Evaluation and Pass Criteria

`ShaderMatrixCase` installs a `MatrixShaderEvaluator` selected for the operation and input modes. `Evaluator` template specializations independently calculate the expected matrix operation, including the built-ins and mutation semantics ([`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1133-L1405), [`#L1642-L1652`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1642-L1652)).

The shared `ShaderRenderCase` harness renders the generated programs, evaluates the reference image, and compares the images. These cases therefore test execution results, not only whether the shader compiler accepts a matrix expression ([`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [`#L2692-L2730`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2730)).

The file defines no matrix-specific `checkSupport()` override. It relies on the shader-render framework's support and compilation path ([`ShaderMatrixCase`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1934-L1974)).

## Failure Triage

A failing path identifies the operation, input source, precision, operand shape, and shader stage. Use that information to narrow investigation:

- Failures limited to `dynamic` can involve attributes, interpolation, or varyings; `uniform` failures can involve UBO declarations or host upload.
- A rectangular-matrix failure in `mul`, `outerproduct`, or `transpose` often points to row/column type construction.
- `inverse` or `determinant` failures only involve square shapes and may involve numerical handling.
- Prefix/postfix failures can indicate that the expression result or the mutated temporary was evaluated incorrectly.
- `mul_assign` should appear only for square matrix types; an unexpected rectangular leaf indicates a registration error.

## Source Reference Appendix

- Operation table and generated-case loops: [`ShaderMatrixTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2347-L2551)
- Operand-category predicates: [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L551-L605)
- Evaluators: [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1133-L1405)
- Case and instance implementation: [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1686-L2323)
- Package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1265)
- Shared rendering and comparison: [`vktShaderRender.cpp`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [`#L2692-L2730`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2730)
