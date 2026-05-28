# vktShaderRenderMatrixTests.cpp

## Overview

[`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1) implements the `glsl.matrix` ShaderRenderCase-based tests. The GLSL category registers this file's factory with `sr::createMatrixTests(testCtx)` under the `glsl` root in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1265), and the factory returns a `ShaderMatrixTests` group named `matrix` in [`createMatrixTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2556-L2559).

The file covers matrix arithmetic operators, component-wise multiplication, `outerProduct`, `transpose`, `inverse`, `determinant`, unary operators, increment/decrement operators, and compound assignments through the `ops[]` registration table in [`ShaderMatrixTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2347-L2394). Generated cases combine operation-specific input groups, matrix data types, `mediump` / `highp` precision, and vertex / fragment shader execution in the registration loops at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2416-L2551).

## Role

Registration and implementation-heavy test file. The source declares `ShaderMatrixTests` as a `tcu::TestCaseGroup` named `matrix` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2326-L2340), registers all direct operation children in [`ShaderMatrixTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2347-L2551), and implements each generated case with `ShaderMatrixCase` and `ShaderMatrixInstance` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1686-L1776) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1934-L1974).

## Source Code

- Primary source: [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1)
- Public factory declaration: [`vktShaderRenderMatrixTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.hpp#L23-L35)
- GLSL category registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1215-L1265)
- Root package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1345-L1353) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1413-L1422)

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

### add — Matrix addition

The `add` operation maps to `OP_ADD` and is registered with input-type subgroups because its `ops[]` entry sets `extendedInputTypeCases=true` and `createInputTypeGroup=true` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2355-L2358). It generates `const`, `uniform`, and `dynamic` input groups from `extendedInputTypes[]` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2401-L2408). For each matrix type and precision, the registration loop adds matrix-scalar cases and same-dimension component-wise matrix-matrix cases at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2454-L2463) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2506-L2515). Reference evaluation computes `in0 + in1` and reduces the result to `vec3` at [`Evaluator<OP_ADD>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1133-L1145).

### sub — Matrix subtraction

The `sub` operation maps to `OP_SUB` and has the same input-type grouping as `add` through the `ops[]` entry at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2358-L2359). Its generated cases are matrix-scalar plus same-dimension matrix-matrix because `isOperationMatrixScalar()` includes `OP_SUB` and `isOperationComponentwiseMatrixMatrix()` includes `OP_SUB` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L551-L569). Reference evaluation computes `in0 - in1` at [`Evaluator<OP_SUB>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1148-L1160).

### mul — Matrix multiplication

The `mul` operation maps to `OP_MUL` and uses `const`, `uniform`, and `dynamic` input groups from its `ops[]` entry at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2360-L2361). Unlike `add` and `sub`, multiplication is classified as matrix-scalar, matrix-vector / vector-matrix, arithmetic matrix-matrix, and component-wise matrix-matrix by the operation predicates at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L551-L569). The registration loop emits matrix-vector and vector-matrix cases using vector sizes derived from matrix column and row counts at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2465-L2489), and emits arithmetic matrix-matrix cases for `otherCols` values 2 through 4 at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2491-L2505). Reference evaluation computes `in0 * in1` at [`Evaluator<OP_MUL>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1163-L1175).

### div — Matrix division

The `div` operation maps to `OP_DIV` and uses the extended input-type groups from [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2362-L2363). It is classified as matrix-scalar plus same-dimension component-wise matrix-matrix by the operation predicates at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L551-L569). For matrix-scalar division, the scalar input is forced to `INPUTTYPE_UNIFORM`; for component-wise matrix division, the second matrix is also forced to uniform when the first input is dynamic, avoiding two dynamic matrix inputs in the same case at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2454-L2458) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2506-L2515). Reference evaluation computes `in0 / in1` at [`Evaluator<OP_DIV>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1178-L1190).

### matrixcompmult — `matrixCompMult()`

The `matrixcompmult` operation maps to `OP_COMP_MUL`, creates an input-type subgroup, but uses only the reduced `dynamic` input list because `extendedInputTypeCases=false` in the `ops[]` table at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2364-L2365). It generates same-dimension matrix-matrix cases through the component-wise branch at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2506-L2515). Reference evaluation calls `matrixCompMult(in0, in1)` at [`Evaluator<OP_COMP_MUL>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1193-L1205).

### outerproduct — `outerProduct()`

The `outerproduct` operation maps to `OP_OUTER_PRODUCT`, creates a `dynamic` input-type subgroup, and is recognized as a vector-vector operation by `isOperationVectorVector()` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L571-L574). The registration loop derives vector sizes from the current matrix type's row and column counts and forces the second vector to uniform when the first vector is dynamic at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2517-L2526). The shader result type is the matrix formed from the second vector size as columns and the first vector size as rows at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2001-L2004), and reference evaluation calls `outerProduct(in0, in1)` at [`Evaluator<OP_OUTER_PRODUCT>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1208-L1220).

### transpose — `transpose()`

The `transpose` operation maps to `OP_TRANSPOSE`, creates a `dynamic` input-type subgroup, and is accepted for any matrix type by `isOperationUnaryAnyMatrix()` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2368-L2369) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L576-L580). The generated shader computes a result type with rows and columns swapped at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2005-L2009), and reference evaluation calls `transpose(in0)` at [`Evaluator<OP_TRANSPOSE>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1223-L1233).

### determinant — `determinant()`

The `determinant` operation maps to `OP_DETERMINANT`, creates a `dynamic` input-type subgroup, and is restricted to square matrices by the `isOperationUnarySymmetricMatrix(op) && numCols == numRows` registration guard at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2368-L2373) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2529-L2535). The generated shader sets the result type to `float` at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2014-L2017), and reference evaluation broadcasts `determinant(in0)` into the RGB vector at [`Evaluator<OP_DETERMINANT>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1249-L1259).

### inverse — `inverse()`

The `inverse` operation maps to `OP_INVERSE`, creates a `dynamic` input-type subgroup, and is restricted to square matrices by the same unary symmetric registration guard used by `determinant` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2370-L2373) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2529-L2535). The `ShaderMatrixInstance` constructor uses a larger grid for vertex inverse cases and adjusts attribute transforms to avoid singular or problematic inputs at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1701-L1728). Reference evaluation calls `inverse(in0)` at [`Evaluator<OP_INVERSE>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1236-L1246).

### unary_addition — Unary plus

The `unary_addition` operation maps to `OP_UNARY_PLUS`, does not create an input-type subgroup, and therefore registers direct leaf cases below `glsl.matrix.unary_addition` using only dynamic input at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2374-L2375) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2432-L2438). It applies to every matrix type through `isOperationUnaryAnyMatrix()` and the unary registration branch at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L576-L580) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2529-L2535). Reference evaluation returns the input value unchanged at [`Evaluator<OP_UNARY_PLUS>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1262-L1272).

### negation — Unary minus

The `negation` operation maps to `OP_NEGATION`, registers direct dynamic-input leaves without an input-type subgroup at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2376-L2377) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2432-L2438), and applies to every matrix type through the unary-any predicate at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L576-L580). Reference evaluation negates the matrix with `negate(in0)` at [`Evaluator<OP_NEGATION>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1275-L1285).

### pre_increment — Prefix increment

The `pre_increment` operation maps to `OP_PRE_INCREMENT`, registers direct dynamic-input leaves at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2378-L2379), and is classified as a value-modifying unary operation by `isOperationValueModifying()` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L587-L590). The generated shader copies the input into `tmpValue`, applies the prefix operator to that temporary, and outputs both `res` and the modified temporary for value-modification checks at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2197-L2262). Reference evaluation sums two reductions of `increment(in0)` at [`Evaluator<OP_PRE_INCREMENT>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1288-L1300).

### pre_decrement — Prefix decrement

The `pre_decrement` operation maps to `OP_PRE_DECREMENT`, registers direct dynamic-input leaves at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2380-L2381), and uses the same value-modifying shader-generation path as prefix increment at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2197-L2262). Reference evaluation sums two reductions of `decrement(in0)` at [`Evaluator<OP_PRE_DECREMENT>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1303-L1315).

### post_increment — Postfix increment

The `post_increment` operation maps to `OP_POST_INCREMENT`, registers direct dynamic-input leaves at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2382-L2383), and generates a postfix operator expression through `OPERATIONTYPE_UNARY_POSTFIX_OPERATOR` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L466-L469) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2230-L2233). Reference evaluation combines the original input reduction and the incremented input reduction at [`Evaluator<OP_POST_INCREMENT>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1318-L1330).

### post_decrement — Postfix decrement

The `post_decrement` operation maps to `OP_POST_DECREMENT`, registers direct dynamic-input leaves at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2384-L2385), and uses the postfix operator shader-generation branch at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2230-L2233). Reference evaluation combines the original input reduction and the decremented input reduction at [`Evaluator<OP_POST_DECREMENT>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1333-L1345).

### add_assign — Compound addition assignment

The `add_assign` operation maps to `OP_ADD_INTO`, registers direct dynamic-input leaves without an input-type subgroup at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2386-L2387), and applies to every matrix type through `isOperationAssignmentAnyMatrix()` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L592-L600). Assignment cases initialize `res` from the first operand and then emit the compound operator statement at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2207-L2249). Reference evaluation computes `in0 + in1` at [`Evaluator<OP_ADD_INTO>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1348-L1360).

### sub_assign — Compound subtraction assignment

The `sub_assign` operation maps to `OP_SUBTRACT_FROM`, registers direct dynamic-input leaves at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2388-L2389), and applies to every matrix type through `isOperationAssignmentAnyMatrix()` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L597-L600). Reference evaluation computes `in0 - in1` at [`Evaluator<OP_SUBTRACT_FROM>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1363-L1375).

### mul_assign — Compound multiplication assignment

The `mul_assign` operation maps to `OP_MULTIPLY_INTO`, registers direct dynamic-input leaves at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2390-L2391), but is restricted to square matrices because `isOperationAssignmentSymmetricMatrix()` only returns true for `OP_MULTIPLY_INTO` and the registration guard also requires `numCols == numRows` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L602-L605) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2538-L2547). Reference evaluation computes `in0 * in1` at [`Evaluator<OP_MULTIPLY_INTO>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1378-L1390).

### div_assign — Compound division assignment

The `div_assign` operation maps to `OP_DIVIDE_INTO`, registers direct dynamic-input leaves at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2392-L2393), and applies to every matrix type through `isOperationAssignmentAnyMatrix()` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L597-L600). As with other assignment operations, a dynamic first input causes the second matrix input to be uniform in the assignment branch at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2538-L2547). Reference evaluation computes `in0 / in1` at [`Evaluator<OP_DIVIDE_INTO>`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1393-L1405).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Operation children | Nineteen operation names are registered by `ops[]`: `add`, `sub`, `mul`, `div`, `matrixcompmult`, `outerproduct`, `transpose`, `determinant`, `inverse`, `unary_addition`, `negation`, `pre_increment`, `pre_decrement`, `post_increment`, `post_decrement`, `add_assign`, `sub_assign`, `mul_assign`, and `div_assign` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2355-L2394). |
| Operation enum values | `MatrixOp` contains `OP_ADD` through `OP_DIVIDE_INTO`, with `OP_LAST` as the terminator at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L323-L345). |
| Input source groups | `add`, `sub`, `mul`, and `div` use `const`, `uniform`, and `dynamic`; operation families with input-type groups but `extendedInputTypeCases=false` use only `dynamic`; operations with `createInputTypeGroup=false` register dynamic cases directly under the operation group at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2355-L2408) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2416-L2438). |
| Matrix types | `mat2`, `mat2x3`, `mat2x4`, `mat3x2`, `mat3`, `mat3x4`, `mat4x2`, `mat4x3`, and `mat4` are generated from `matrixTypes[]` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2410-L2412). |
| Precision | `mediump` and `highp` are generated from `precisions[]` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2414-L2451). |
| Shader stage | Every generated leaf is duplicated as `_vertex` and `_fragment` when each `ShaderMatrixCase` is added at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2459-L2462), [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2472-L2488), [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2498-L2503), [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2511-L2526), [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2531-L2535), and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2543-L2546). |
| Operand families | Matrix-scalar applies to add/sub/mul/div; matrix-vector and arithmetic matrix-matrix apply only to multiplication; component-wise matrix-matrix applies to add/sub/mul/div and `matrixCompMult`; vector-vector applies to `outerProduct`; unary-any applies to transpose/unary plus/negation/increment/decrement; unary-square applies to inverse/determinant; assignment-any applies to add/sub/div assignment; assignment-square applies to multiply assignment at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L551-L605). |
| Dynamic-input pairing rule | The generated cases avoid two dynamic matrix inputs: matrix-matrix, component-wise, vector-vector, and assignment branches use a uniform second input when the first input is dynamic at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2491-L2521) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2538-L2547); shader setup asserts that only one dynamic matrix input is allowed at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1980-L1993). |
| Result reduction | Shader output reduces scalar, vector, and matrix results into RGB through `genGLSLMatToVec3Reduction()` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2255-L2262) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2271-L2323). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| GLSL category availability | The `glsl` root is registered for Vulkan and Vulkan SC package initialization at [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1345-L1353) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1413-L1422). |
| No file-local feature gate observed | `ShaderMatrixCase` does not define a file-local `checkSupport()` override in the inspected source; support behavior is inherited from the `ShaderRenderCase` / `ShaderRenderCaseInstance` framework while this file supplies generated GLSL, uniforms, and attributes at [`ShaderMatrixCase`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1934-L1974) and [`ShaderMatrixInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1686-L1776). |
| Shader language version | Generated shaders start with `#version 310 es` at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2048-L2054). |
| Uniform inputs | Uniform operands are emitted as `layout(std140, set = 0, binding = ...) uniform buffer...` declarations at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2106-L2111), and `ShaderMatrixInstance::setupUniforms()` fills scalar, vector, and matrix uniform buffers at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1870-L1905). |
| Dynamic matrix attributes | Dynamic matrix inputs use vertex attributes selected with `useAttribute(4u + inNdx, getAttributeType(in.dataType))` at [`ShaderMatrixInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1765-L1775), and GLSL declarations account for matrix attribute locations and passthrough varyings at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2071-L2089). |

## Verification Methods

- Each `ShaderMatrixCase` constructs a `MatrixShaderEvaluator` selected by `getEvalFunc(in0, in1, op)` at [`ShaderMatrixCase::ShaderMatrixCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1953-L1963). The evaluator invokes the operation-specific function for the current input modes at [`MatrixShaderEvaluator::evaluate()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1642-L1652).
- Operation-specific reference paths are template specializations of `Evaluator`, covering arithmetic operators, `matrixCompMult`, `outerProduct`, `transpose`, `inverse`, `determinant`, unary operators, increment/decrement, and compound assignments at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1133-L1405).
- The generated shader computes `res` using the corresponding GLSL operator or built-in function, then writes a `vec4` color based on `genGLSLMatToVec3Reduction()`; value-modifying cases add a second reduction of the mutated temporary to verify both the returned value and side effect at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2186-L2262).
- Dynamic inputs are sourced through attributes and varyings, uniform inputs through uniform buffers, and constant inputs through literal GLSL constructors at [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2061-L2167); the reference evaluator reads matching constant or dynamic data through `getInputValue` specializations at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L634-L828).
- The rendered image comparison itself is performed by the shared `ShaderRenderCase` framework; this file provides the GLSL output color and analytic evaluator rather than implementing a separate pixel-comparison loop, as shown by inheritance from `ShaderRenderCase` and `ShaderRenderCaseInstance` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1686-L1704) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1934-L1957).

## Test Principles

- The direct hierarchy is operation-centric: each direct child under `glsl.matrix` comes from one `ops[]` table entry, and deeper cases are generated by input-type, matrix-type, precision, operand-shape, and shader-stage loops at [`ShaderMatrixTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2347-L2551).
- The source uses operation predicates to avoid claiming a single operand matrix for every operation: multiplication has matrix-vector and matrix-matrix forms, component-wise matrix operations are restricted to same-dimension operands, `outerProduct` is vector-vector, and inverse/determinant/multiply-assignment are square-matrix-only paths at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L551-L605) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2465-L2547).
- Test data is adjusted per operation family to keep reference images meaningful and avoid problematic inverse/division inputs, including operation-selected matrix transforms in `ShaderMatrixInstance` and uniform second operands for selected dynamic-input cases at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1701-L1763) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2454-L2547).
- The generated-case pattern follows the operation/input/precision/type/stage naming structure visible in the source registration loops and leaf-name construction for the inspected matrix group.

## Notes

- The previous broad statement that all matrix operations are parameterized across `const`, `uniform`, and `dynamic` inputs was narrowed: only `add`, `sub`, `mul`, and `div` set `extendedInputTypeCases=true`; the remaining operation families use dynamic input, with or without an explicit `dynamic` subgroup depending on `createInputTypeGroup` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2355-L2408).
- The previous operand summary was narrowed: `add`, `sub`, and `div` do not generate matrix-vector or arithmetic matrix-matrix cases; those branches are selected only for `OP_MUL` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L556-L564) and [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2465-L2505).
- Square-matrix restrictions apply to `inverse`, `determinant`, and `mul_assign`; the inspected code does not apply that restriction to `transpose`, unary plus, negation, increment/decrement, `add_assign`, `sub_assign`, or `div_assign` at [`vktShaderRenderMatrixTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2529-L2547).
