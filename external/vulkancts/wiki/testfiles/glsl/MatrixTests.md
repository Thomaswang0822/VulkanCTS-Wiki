## Overview

**Core question:** Do vertex and fragment shaders evaluate GLSL ES matrix operators and matrix built-in functions with the correct values, result shapes, and side effects?

- `vktShaderRenderMatrixTests.cpp` implements the `glsl.matrix` test family and registers nineteen operation-specific intermediate nodes.
- Each test case generates a GLSL ES 3.10 shader for one operation, operand form, input source, matrix type, precision, and shader stage.
- The shader reduces its scalar, vector, or matrix result to a color. The host evaluates the same operation independently and compares the rendered image with the reference image.
- The generated matrix excludes operand shapes that the GLSL operation cannot accept and avoids input combinations that would obscure the intended check.

## Background Knowledge

- A GLSL matrix type `matC` or `matCxR` has `C` columns and `R` rows. Matrix and vector operand dimensions must agree for algebraic multiplication, while component-wise operations require matching matrix shapes.
- The `*` operator performs algebraic multiplication for matrix-vector, vector-matrix, and matrix-matrix operands. `matrixCompMult()` multiplies corresponding components instead.
- Prefix and postfix increment or decrement produce different expression values even though both modify the operand. A test must observe the expression result and the value left in the operand to distinguish them.

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

`createMatrixTests()` creates the `matrix` test family, and the GLSL package registers it below `glsl`. `ShaderMatrixTests::init()` creates the nineteen operation intermediate nodes shown above ([package registration](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1265), [matrix registration](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2326-L2425)).

The first nine intermediate nodes contain input-source intermediate nodes. `add`, `sub`, `mul`, and `div` use `const`, `uniform`, and `dynamic`; `matrixcompmult`, `outerproduct`, `transpose`, `determinant`, and `inverse` use only `dynamic`. The unary, increment/decrement, and assignment intermediate nodes contain their generated test case leaves directly ([input-source registration](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2396-L2438)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Operation intermediate node | `add`, `sub`, `mul`, `div`, `matrixcompmult`, `outerproduct`, `transpose`, `determinant`, `inverse`, `unary_addition`, `negation`, `pre_increment`, `pre_decrement`, `post_increment`, `post_decrement`, `add_assign`, `sub_assign`, `mul_assign`, `div_assign` | Selects the GLSL expression and is the primary behavioral axis. | [`ops[]`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2347-L2394) |
| Input-source intermediate node | `const`, `uniform`, `dynamic`, with availability determined by the operation | Chooses whether the first operand comes from shader source, a uniform buffer, or interpolated/vertex input data. | [input-source lists](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2396-L2438) |
| First matrix type | `mat2`, `mat2x3`, `mat2x4`, `mat3x2`, `mat3`, `mat3x4`, `mat4x2`, `mat4x3`, `mat4` | Covers every two-, three-, and four-column float matrix with two through four rows. | [`matrixTypes[]`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2410-L2412) |
| Precision | `mediump`, `highp` | Applies the selected precision qualifier to operands and the generated result. | [`precisions[]`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2414-L2452) |
| Shader stage | `vertex`, `fragment` | Places the tested expression in the vertex or fragment shader. The other stage passes through position, color, or dynamic inputs. | [test case generation](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2454-L2547) |
| Operand form | Matrix-scalar, matrix-vector, vector-matrix, matrix-matrix, vector-vector, or unary matrix, as allowed by the operation | Changes the overload, result type, and dimensional compatibility being tested. | [operand predicates](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L545-L605) |
| Arithmetic matrix result width | Two, three, or four columns for the second matrix in `mul` | Exercises every valid result width while matching the inner multiplication dimension. | [matrix-matrix generation](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2491-L2504) |

Test case leaf names encode precision, operand types, and stage. For example, `highp_mat3_float_vertex` selects a high-precision `mat3` first operand, a scalar second operand, and a vertex-stage expression. The Vulkan and Vulkan SC default mustpass lists each contain 1,764 `glsl.matrix` leaves across all nineteen operation intermediate nodes ([Vulkan mustpass range](../../../mustpass/main/vk-default/glsl.txt#L8725-L10488), [Vulkan SC mustpass range](../../../mustpass/main/vksc-default/glsl.txt#L7804-L9567)).

## Behavior Parameters

The primary behavioral axis is the operation intermediate node. Each value changes the GLSL expression, legal operands, or state change that the test checks.

### `add`: matrix addition

Tests `+` with a matrix and scalar and with two same-shape matrices. The shader and evaluator both reduce the component-wise sum to RGB.

### `sub`: matrix subtraction

Tests `-` with a matrix and scalar and with two same-shape matrices. Operand order remains significant in every generated expression.

### `mul`: scalar and algebraic multiplication

Tests matrix-scalar, matrix-vector, vector-matrix, and dimensionally valid matrix-matrix `*`. Matrix-matrix generation chooses second matrices whose row count equals the first matrix's column count and varies the result width from two through four ([multiplication generation](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2454-L2505)).

### `div`: component-wise division

Tests matrix-scalar and same-shape matrix-matrix `/`. Registration places the scalar in a uniform buffer for every matrix-scalar division case. Dynamic matrix-matrix cases also make the second matrix uniform ([division and binary input generation](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2454-L2462), [second-matrix rule](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2506-L2515)).

### `matrixcompmult`: component-wise multiplication built-in

Tests `matrixCompMult(a, b)` with two matrices of the same shape. This intermediate node checks explicit component-wise multiplication rather than the algebraic matrix behavior of `*`.

### `outerproduct`: vector outer product

Tests `outerProduct(a, b)` with vector lengths derived from the current matrix's row and column counts. The result has the current generated matrix shape ([outer-product generation](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2517-L2527)).

### `transpose`: row and column exchange

Tests `transpose(a)` for every generated matrix type. The result type swaps the source matrix's row and column counts ([result-type selection](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1995-L2017)).

### `determinant`: square-matrix scalar result

Tests `determinant(a)` only for `mat2`, `mat3`, and `mat4`. The generated result is a float, which the shader copies into all three reference color channels.

### `inverse`: square-matrix inverse

Tests `inverse(a)` only for square matrices. The instance adjusts dynamic input transforms to avoid singular or uninformative matrices and uses a 64-cell grid for vertex-stage inverse cases instead of the default 90-cell vertex grid ([inverse input setup](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1701-L1728)).

### `unary_addition`: unary plus

Tests `+a` on every matrix shape. The operation preserves the matrix value, so the color reduction should match the unmodified input.

### `negation`: unary minus

Tests `-a` on every matrix shape. The evaluator negates each matrix component before applying the same color reduction used by the shader.

### `pre_increment`: modified value as expression result

Copies the input to `tmpValue`, evaluates `++tmpValue`, and reduces both the expression result and the final `tmpValue`. Both reductions use the incremented value.

### `pre_decrement`: modified value as expression result

Copies the input to `tmpValue`, evaluates `--tmpValue`, and reduces both the expression result and the final `tmpValue`. Both reductions use the decremented value.

### `post_increment`: original value as expression result

Copies the input to `tmpValue`, evaluates `tmpValue++`, and adds the reduction of the original expression result to the reduction of the incremented `tmpValue`.

### `post_decrement`: original value as expression result

Copies the input to `tmpValue`, evaluates `tmpValue--`, and adds the reduction of the original expression result to the reduction of the decremented `tmpValue` ([mutation shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2197-L2262), [mutation evaluators](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1288-L1346)).

### `add_assign`: compound addition

Initializes `res` from the first matrix, applies `res += second`, and reduces the assigned matrix. All nine matrix shapes are legal.

### `sub_assign`: compound subtraction

Initializes `res` from the first matrix, applies `res -= second`, and reduces the assigned matrix. All nine matrix shapes are legal.

### `mul_assign`: assignable multiplication result

Initializes `res` from the first matrix and applies `res *= second`. Registration limits this operation to square matrices because the multiplication result must have the same type as `res`.

### `div_assign`: compound division

Initializes `res` from the first matrix, applies `res /= second`, and reduces the assigned matrix. All nine matrix shapes are legal ([assignment shader generation](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2207-L2249), [assignment case generation](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2538-L2547)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.matrix.add.const.highp_mat2_float_vertex
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `add` | Selects the binary `+` operator; with two matrix-like operands, the generated result keeps the first operand's `mat2` shape. |
| `const`, `highp_mat2`, `float`, `vertex` | The first operand is the generated constant `mat2`, the second operand is a dynamic highp scalar attribute, and evaluation plus reduction occur in the vertex shader. |

#### Purpose

This case checks GLSL matrix-plus-scalar semantics for a high-precision 2-by-2 matrix in the vertex stage. The rendered color exposes the generated matrix result, allowing the host-side evaluator to compare the expression's values rather than only checking compilation.

#### Structural Design

| Phase | Generated behavior |
|-------|--------------------|
| Inputs | `a_position` supplies the pass-through vertex position; `a_coords` supplies the dynamic scalar; `in0` is the source-backed constant matrix. |
| Operation | `res = in0 + a_coords` applies scalar addition component-wise to both columns of the `mat2`. |
| Observation | `genGLSLMatToVec3Reduction()` maps `res[0][0]`, `res[1][0]`, and the sum `res[0][1] + res[1][1]` into RGB, with alpha `1.0`. |
| Handoff | The vertex shader writes `v_color`; the fixed fragment stage copies that varying to `dEQP_FragColor`. |

#### Shader Code

```glsl
#version 310 es
layout(location = 0) in highp vec4 a_position;
layout(location = 0) out mediump vec4 v_color;
layout(location = 1) in highp float a_coords;
const highp mat2 in0 = mat2(-0.1, 1.0, -0.2, 0.0);

void main (void)
{
    /// The selected vertex case evaluates the generated matrix-plus-scalar expression.
    gl_Position = a_position;
    highp mat2 res = in0 + a_coords;
    /// The mat2 reduction follows genGLSLMatToVec3Reduction(): column-major indexing is intentional.
    v_color = vec4(res[0][0], res[1][0], res[0][1]+res[1][1], 1.0);
}
```

#### Additional Info

- The primary generator is `ShaderMatrixCase::setupShader()` in `vktShaderRenderMatrixTests.cpp`; `ShaderMatrixTests::init()` registers this exact leaf as the `add`/`const`/`mat2`/`highp`/`float`/`vertex` specialization ([shader builder](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1934-L1974), [leaf registration](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2416-L2462)).
- The constant values are the first entry of `s_constInMat2x2`: `-0.1, 1.0, -0.2, 0.0`; `writeMatrixConstructor<2, 2>()` emits them column-major ([constant data and constructor](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L73-L93), [constructor emission](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1604-L1623)).
- The scalar is dynamic because `init()` creates `scalarIn` as `INPUTTYPE_DYNAMIC` for `add` matrix-scalar cases; the instance binds that input as the `a_coords` attribute ([matrix-scalar registration](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2454-L2462), [dynamic attribute setup](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1765-L1775)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Operation | `add` emits `res = operationValue0 + operationValue1`; other binary operations change the operator or function and may change legal operand forms. | [operation emission](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2186-L2249) |
| Input source | For the first operand, `const` emits a typed constructor, while `uniform` emits a `std140` block and `dynamic` emits a matrix attribute; this selected case's scalar is dynamic and therefore uses `a_coords`. | [input declarations](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2061-L2166) |
| Matrix type | Changing `mat2` changes the result declaration and selects a different shape-specific RGB reduction. | [matrix type registration](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2410-L2412), [reduction](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2271-L2323) |
| Precision and stage | `mediump` changes emitted qualifiers; `fragment` moves the operation to the fragment shader and passes dynamic inputs through vertex outputs, while `vertex` writes `v_color`. | [stage and precision setup](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1974-L2059), [stage handoff](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2177-L2184) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 54
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %a_position %a_coords %v_color
               OpSource ESSL 310
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %a_position "a_position"
               OpName %res "res"
               OpName %a_coords "a_coords"
               OpName %v_color "v_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %a_position Location 0
               OpDecorate %a_coords Location 1
               OpDecorate %v_color RelaxedPrecision
               OpDecorate %v_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
 %a_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %v2float = OpTypeVector %float 2
%mat2v2float = OpTypeMatrix %v2float 2
%_ptr_Function_mat2v2float = OpTypePointer Function %mat2v2float
%float_n0_100000001 = OpConstant %float -0.100000001
    %float_1 = OpConstant %float 1
         %24 = OpConstantComposite %v2float %float_n0_100000001 %float_1
%float_n0_200000003 = OpConstant %float -0.200000003
    %float_0 = OpConstant %float 0
         %27 = OpConstantComposite %v2float %float_n0_200000003 %float_0
         %28 = OpConstantComposite %mat2v2float %24 %27
%_ptr_Input_float = OpTypePointer Input %float
   %a_coords = OpVariable %_ptr_Input_float Input
    %v_color = OpVariable %_ptr_Output_v4float Output
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Function_float = OpTypePointer Function %float
      %int_1 = OpConstant %int 1
     %uint_1 = OpConstant %uint 1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %res = OpVariable %_ptr_Function_mat2v2float Function
         %15 = OpLoad %v4float %a_position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
         %31 = OpLoad %float %a_coords
         %32 = OpCompositeConstruct %v2float %31 %31
         %33 = OpCompositeExtract %v2float %28 0
         %34 = OpFAdd %v2float %33 %32
         %35 = OpCompositeExtract %v2float %28 1
         %36 = OpFAdd %v2float %35 %32
         %37 = OpCompositeConstruct %mat2v2float %34 %36
               OpStore %res %37
         %42 = OpAccessChain %_ptr_Function_float %res %int_0 %uint_0
         %43 = OpLoad %float %42
         %45 = OpAccessChain %_ptr_Function_float %res %int_1 %uint_0
         %46 = OpLoad %float %45
         %48 = OpAccessChain %_ptr_Function_float %res %int_0 %uint_1
         %49 = OpLoad %float %48
         %50 = OpAccessChain %_ptr_Function_float %res %int_1 %uint_1
         %51 = OpLoad %float %50
         %52 = OpFAdd %float %49 %51
         %53 = OpCompositeConstruct %v4float %43 %46 %52 %float_1
               OpStore %v_color %53
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `ShaderMatrixCase` selects an evaluator from the operation and operand data types, generates the vertex and fragment sources, and creates a `ShaderMatrixInstance` with the same input modes and operation ([case construction](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1934-L1972), [evaluator selection](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1408-L1587)).
- Instance setup exposes dynamic matrices as vertex attributes and uploads uniform scalars, vectors, or matrices to uniform buffers. Matrix uniforms occupy a padded 4-by-4 host value whose used columns contain the selected matrix ([attribute setup](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1701-L1775), [uniform setup](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1782-L1930)).
- The shared shader-render harness builds a quad grid, renders a 128-by-128 RGBA8 image, copies the color image back to host-visible memory, and computes a reference image ([render and reference flow](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [image copyback](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2585-L2600)).
- For vertex cases, the host evaluator computes a color at each grid vertex and interpolates those colors across the same triangles. For fragment cases, it evaluates the expected color at each pixel center ([vertex reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2689), [fragment reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2719)).
- The matrix instance uses the non-fuzzy comparison path. Each rendered RGBA8 channel may differ from the reference by at most one integer value. A match returns `Result image matches reference`; any larger difference returns `Image mismatch` ([instance comparison mode](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L686-L711), [comparison and status](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L799-L805), [pixel threshold](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

A compile, link, setup, or execution error also fails the test before the final image match. The family does not check only whether the compiler accepts the expression; successful cases must produce the expected rendered values.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `add` | Matrix expression semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `sub` | Matrix expression semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `mul` | Matrix expression semantics; operand shape and result-type handling; input transport or stage handoff; result reduction, rendering, or comparison |
| `div` | Matrix expression semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `matrixcompmult` | Built-in function behavior; input transport or stage handoff; result reduction, rendering, or comparison |
| `outerproduct` | Built-in function behavior; operand shape and result-type handling; input transport or stage handoff; result reduction, rendering, or comparison |
| `transpose` | Built-in function behavior; operand shape and result-type handling; input transport or stage handoff; result reduction, rendering, or comparison |
| `determinant` | Built-in function behavior; scalar result handling; input transport or stage handoff; result reduction, rendering, or comparison |
| `inverse` | Built-in function behavior; input transport or stage handoff; result reduction, rendering, or comparison |
| `unary_addition` | Matrix expression semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `negation` | Matrix expression semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `pre_increment` | Mutation and assignment semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `pre_decrement` | Mutation and assignment semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `post_increment` | Mutation and assignment semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `post_decrement` | Mutation and assignment semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `add_assign` | Mutation and assignment semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `sub_assign` | Mutation and assignment semantics; input transport or stage handoff; result reduction, rendering, or comparison |
| `mul_assign` | Mutation and assignment semantics; operand shape and result-type handling; input transport or stage handoff; result reduction, rendering, or comparison |
| `div_assign` | Mutation and assignment semantics; input transport or stage handoff; result reduction, rendering, or comparison |

### Cause Analysis

#### Matrix expression semantics

**Possible failure symptoms:** A valid arithmetic or unary shader may fail compilation, or the rendered color may disagree with the evaluator for specific operators, precisions, matrix shapes, or stages.

**Possible implementation causes:** The GLSL compiler may select or lower a valid matrix overload incorrectly, or shader execution may apply the wrong component-wise or algebraic operation. The affected operand form identifies which overload needs source-level investigation.

#### Operand shape and result-type handling

**Possible failure symptoms:** Failures may cluster on rectangular multiplication, vector-matrix direction, `outerProduct`, `transpose`, or square-only `mul_assign`, while related scalar or square cases pass.

**Possible implementation causes:** The compiler may derive the wrong row or column dimension, construct the wrong result type, or map matrix columns to locations incorrectly. The CTS generator derives these types from both operands and reduces the resulting type with a shape-specific formula, so either shader compilation or a wrong image can expose the error.

#### Built-in function behavior

**Possible failure symptoms:** `matrixcompmult`, `outerproduct`, `transpose`, `determinant`, or `inverse` may compile but produce an image mismatch for particular shapes or precisions.

**Possible implementation causes:** The implementation may lower the selected built-in with incorrect component order, arithmetic, shape, or precision behavior. `determinant` and `inverse` failures need numerical investigation against the generated inputs before assigning a cause to a single layer.

#### Scalar result handling

**Possible failure symptoms:** `determinant` may fail while matrix-returning built-ins on the same square shapes pass, with the mismatch repeated across the red, green, and blue channels.

**Possible implementation causes:** The determinant operation or conversion of its float result into the three color channels may be wrong. The evaluator writes the same scalar into all three channels, which separates this path from matrix-specific reduction formulas.

#### Mutation and assignment semantics

**Possible failure symptoms:** Prefix and postfix cases may disagree with each other, or compound assignments may render the wrong updated matrix despite the corresponding pure arithmetic operation passing.

**Possible implementation causes:** The compiler may return the wrong pre-mutation or post-mutation expression value, omit the side effect, apply it more than once, or mishandle an in-place compound assignment. The mutation color contains reductions of both `res` and `tmpValue`, while assignment cases reduce the modified `res`.

#### Input transport or stage handoff

**Possible failure symptoms:** Failures may occur only under `const`, `uniform`, or `dynamic`, or only in fragment cases that receive dynamic values through varyings.

**Possible implementation causes:** The implementation or test setup may mishandle a constant constructor, `std140` uniform data, matrix vertex attributes, attribute locations, or vertex-to-fragment interpolation. Comparing input-source and stage siblings can isolate the failing path without assuming whether compilation, descriptor setup, or interpolation is responsible.

#### Result reduction, rendering, or comparison

**Possible failure symptoms:** Many unrelated operations may produce similarly placed image mismatches, or values near channel quantization boundaries may exceed the one-unit RGBA8 threshold.

**Possible implementation causes:** A shared result-reduction expression, stage color handoff, rasterization path, image copyback, host reference calculation, or threshold comparison may be responsible. Source-level investigation should compare the logged result and reference images before attributing a broad failure to matrix arithmetic.

## Case Pruning

### Requirement-based pruning

The family has no matrix-specific `checkSupport()` override and performs no feature, format, or device-limit pruning in its registration loop. It relies on the common shader-render framework and the baseline GLSL ES 3.10 shader path ([`ShaderMatrixCase`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1934-L1974)).

### Design-based pruning

- `determinant` and `inverse` use only square matrices. `mul_assign` also uses only square matrices because its result must remain assignable to the first operand.
- The generator emits only operand categories accepted by each operation. Algebraic matrix multiplication matches inner dimensions and varies the result width; same-shape component-wise forms use identical matrix types.
- `add`, `sub`, `mul`, and `div` cover `const`, `uniform`, and `dynamic` first operands. Other operations use `dynamic` only, which removes repeated source-mode coverage from those intermediate nodes.
- The generator does not combine two dynamic matrix-like operands in one binary case. If the first matrix or vector is dynamic, registration makes the second matrix or vector uniform ([binary input constraints](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2491-L2521), [shader assertion](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1980-L1993)).
- Although `OP_MUL` satisfies the component-wise predicate, its arithmetic matrix-matrix branch comes first in an `if`/`else if` chain. The `mul` intermediate node therefore contains algebraic matrix-matrix leaves, while `matrixcompmult` owns explicit component-wise multiplication ([operation predicates](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L561-L569), [generation branch](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2491-L2515)).

These exclusions define the generated matrix. They do not indicate runtime skips on a supported device.

## Key Takeaways

- The nineteen operation intermediate nodes are the primary behavior choices. They cover arithmetic operators, matrix built-ins, unary mutation, and compound assignment.
- Operand and result dimensions come from operation-specific rules. Rectangular matrices appear wherever the operation permits them, while determinant, inverse, and multiply assignment remain square-only.
- Every shader converts its result to color, and mutation cases include both the expression result and final operand value in that color.
- The host evaluates the operation independently, follows stage-appropriate interpolation, and requires the rendered RGBA8 image to stay within one integer value per channel.
- Input-source and stage siblings help separate expression failures from uniform upload, vertex attribute, varying, and common rendering paths. See `Failure Meaning` for the corresponding failure analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Operation model and operand predicates | [`MatrixOp` and predicate helpers](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L297-L605) | Defines the nineteen operations, their expression kinds, and legal operand categories. |
| Independent evaluators | [`Evaluator` specializations and selector](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1126-L1587) | Computes host-side expected values for arithmetic, built-ins, mutations, and assignments. |
| Matrix instance setup | [`ShaderMatrixInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1681-L1930) | Configures dynamic attributes, inverse inputs, grid size, and uniform data. |
| Shader generation | [`ShaderMatrixCase::setupShader()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L1932-L2269) | Builds declarations, result types, expressions, stage handoffs, and final colors. |
| Result reduction | [`genGLSLMatToVec3Reduction()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2271-L2323) | Maps each scalar, vector, or matrix result type to RGB. |
| Test case registration | [`ShaderMatrixTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderMatrixTests.cpp#L2326-L2551) | Creates operation and input-source intermediate nodes and all valid test case leaves. |
| GLSL package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1265) | Registers `matrix` under the `glsl` test category. |
| Shared rendering and comparison | [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [reference and comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2730) | Renders, computes the stage-specific reference image, and decides pass or fail. |
| Default matrix mustpass coverage | [Vulkan](../../../mustpass/main/vk-default/glsl.txt#L8725-L10488), [Vulkan SC](../../../mustpass/main/vksc-default/glsl.txt#L7804-L9567) | Confirms the registered leaves included in both default configurations. |
