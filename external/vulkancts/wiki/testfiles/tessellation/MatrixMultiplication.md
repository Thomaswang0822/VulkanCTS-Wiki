## Overview

**Core question:** Does a tessellation control shader compute a matrix product correctly while preserving values copied before the product overwrites a patch output?

- [`vktTessellationMatrixMultiplicationTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L1) implements the two test case leaves under `tessellation.matrix_multiplication`.
- Both leaves execute the same `mat4 * mat4` expression in the tessellation control shader. `tesc_1` checks the product; `tesc_2` checks the original first column copied before the product overwrites the output matrix.
- The shaders turn four comparison results into RGBA. The host passes a case only when all 16 pixels in a 4 by 4 image are opaque white.

## Background Knowledge

For the shared concepts tessellation pipeline stages and patch interfaces, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- **GLSL matrix order.** A GLSL `mat4` consists of four column vectors, and a scalar-list constructor fills one column at a time. `m * x` is an ordered matrix product rather than component-wise multiplication. Reversing the operands or reading the constructor as rows gives a different result.
- **Patch outputs and interface locations.** A tessellation control shader can produce values shared by the whole patch. Later graphics stages receive matching inputs by location. A `mat4` consumes four consecutive locations because shader interfaces assign a matrix as an array of column vectors. See [Shader Input and Output Interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces) and [Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-locations).

## Registration Hierarchy

```text
tessellation.matrix_multiplication
├── tesc_1
└── tesc_2
```

[`createTessellationMatrixMultiplicationTests()`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L368-L375) registers the two leaves. [`createChildren()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L64-L81) attaches the family under `tessellation`. The [Vulkan](../../../mustpass/main/vk-default/tessellation.txt#L235-L236) and [Vulkan SC](../../../mustpass/main/vksc-default/tessellation.txt#L235-L236) default mustpass lists include both executable paths.

## Parameter Dimensions and Observed Values

| Dimension | Registered or fixed values | Meaning in this test | Evidence |
|-----------|----------------------------|----------------------|----------|
| Test case leaf | `tesc_1`, `tesc_2` | Selects whether validation observes the matrix product or a pre-product copy of its first input column. | [registration](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L368-L375) |
| Matrix operands | two fixed `mat4` constants | Keeps the numerical product deterministic and gives every expected component a source-controlled value. | [shader generation](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L228-L322) |
| Comparison tolerance | strict absolute error less than `0.01` | Converts each expected matrix or vector component to a Boolean result in the fragment shader. | [`tesc_1` comparison](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L273-L291), [`tesc_2` comparison](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L347-L357) |
| Tessellation configuration | quads, clockwise order, fractional-odd spacing; all levels `1.0` | Produces a minimal quad-domain draw whose evaluation positions cover the color attachment. | [control and evaluation generation](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L253-L270) |
| Render target | 4 by 4 `VK_FORMAT_R8G8B8A8_UNORM` | Stores one four-channel comparison result at each pixel. | [runtime constants](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L75-L78) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. It changes which value must survive tessellation-control execution and reach fragment validation.

### `tesc_1` — validate the matrix product

The control shader assigns the fixed input matrix to patch output `x`, computes `x = m * x`, and exports the resulting four columns at locations 0 through 3. The evaluation shader forwards the complete matrix. The fragment shader checks all 16 components against the precomputed product.

### `tesc_2` — preserve a value copied before multiplication

The control shader copies `x` to local `temp`, executes the same `x = m * x` assignment, and exports `temp[0]` as a separate patch output at location 5. The evaluation and fragment stages consume only this copied column. This leaf checks that the later output-matrix write does not replace or corrupt the value captured in `temp`.

The source comments describe the intended regression shape: a failing implementation passed when `x` ceased to be an output or when the multiplication line was removed, even though the observable value was `temp` rather than the updated `x` ([generated `tesc_2` comments](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L301-L324)).

## Shader Analysis

The tessellation control stage contains the operation shared by both leaves. The representative `tesc_1` walkthrough exposes the matrix product directly; the variation summary covers the preservation path in `tesc_2`. The shader was reconstructed from the exact `MatrixMultiplicationTestCase::initPrograms()` branch, then compiled, validated, and disassembled with the shader-analyzer/shader-disassembler CCVDO workflow.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.matrix_multiplication.tesc_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `tesc_1` | Sends the multiplied `mat4` through the patch interface for complete 16-component validation. |
| fixed matrices | Exercises one deterministic, non-identity product with mixed positive and negative coefficients. |
| tessellation levels `1.0` | Keeps generated geometry minimal while providing fragments that carry the comparison result. |

#### Purpose

This control shader performs the tested `mat4 * mat4` operation and writes the product as a per-patch output. It also supplies the levels needed to execute the following quad-domain evaluation stage.

#### Structural Design

| Phase | Operation | Observable effect |
|-------|-----------|-------------------|
| Initialize | Store the fixed four-column matrix in patch output `x`. | Supplies the right operand and output object. |
| Multiply | Evaluate `m * x` and overwrite `x`. | Produces the value checked by the fragment shader. |
| Enable tessellation | Write `1.0` to both inner and all four outer levels. | Generates a quad-domain result that carries `x` to rasterization. |

#### Shader Code

```glsl
#version 450
/// One invocation writes one control point and the per-patch outputs.
layout(vertices = 1) out;

/// A mat4 occupies locations 0 through 3; the evaluation shader consumes the same patch value.
layout(location = 0) patch out mat4 x;

void main()
{
    /// GLSL fills the matrix one column at a time.
    x = mat4(
        0.53455, 0.47307, 0.34935, 0.28717,
        0.67195, 0.59992, 0.48213, 0.43678,
        0.76376, 0.6772, 0.55361, 0.5165,
        0.77996, 0.68862, 0.56187, 0.52611
    );

    const mat4 m = mat4(
        vec4( -1.0, 3.0,-3.0, 1.0),
        vec4(  3.0,-6.0, 3.0, 0.0),
        vec4( -3.0, 3.0, 0.0, 0.0),
        vec4(  1.0, 0.0, 0.0, 0.0)
    );

    /// Perform the ordered matrix product and make it the patch value observed by later stages.
    x = m * x;

    /// Level 1.0 is enough to run the evaluation and fragment validation path.
    gl_TessLevelInner[0u] = 1.;
    gl_TessLevelInner[1u] = 1.;
    gl_TessLevelOuter[0u] = 1.;
    gl_TessLevelOuter[1u] = 1.;
    gl_TessLevelOuter[2u] = 1.;
    gl_TessLevelOuter[3u] = 1.;
}
```

#### Additional Info

- The expected product, written by columns, is `(0.12378, -0.18672, -0.18444, 0.53455)`, `(0.11820, -0.13728, -0.21609, 0.67195)`, `(0.12351, -0.11109, -0.25968, 0.76376)`, and `(0.12640, -0.10623, -0.27402, 0.77996)`.
- The evaluation shader forwards `x` unchanged and derives `gl_Position` from `gl_TessCoord.xy`. The fragment shader compares each column with strict absolute error less than `0.01`.
- No explicit shader build target overrides `SourceCollections`, so the walkthrough uses the CTS baseline SPIR-V 1.0 target.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Test case leaf | `tesc_2` adds `patch out vec4 col0` at location 5, saves `mat4 temp = x` before the product, and writes `col0 = temp[0]` afterward. | [`tesc_2` control shader](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L293-L332) |
| Evaluation interface | `tesc_1` forwards the complete matrix from location 0; `tesc_2` forwards only the preserved vector from location 5 to fragment location 0. | [evaluation branches](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L261-L271), [second branch](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L334-L345) |
| Fragment oracle | `tesc_1` checks four product columns; `tesc_2` checks the four components of the original first column. | [fragment branches](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L273-L291), [second branch](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L347-L357) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tesc`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 66
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationControl %main "main" %x %gl_TessLevelInner %gl_TessLevelOuter
               OpExecutionMode %main OutputVertices 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %x "x"
               OpName %gl_TessLevelInner "gl_TessLevelInner"
               OpName %gl_TessLevelOuter "gl_TessLevelOuter"
               OpDecorate %x Patch
               OpDecorate %x Location 0
               OpDecorate %gl_TessLevelInner BuiltIn TessLevelInner
               OpDecorate %gl_TessLevelInner Patch
               OpDecorate %gl_TessLevelOuter BuiltIn TessLevelOuter
               OpDecorate %gl_TessLevelOuter Patch
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%mat4v4float = OpTypeMatrix %v4float 4
%_ptr_Output_mat4v4float = OpTypePointer Output %mat4v4float
          %x = OpVariable %_ptr_Output_mat4v4float Output
%float_0_534550011 = OpConstant %float 0.534550011
%float_0_473069996 = OpConstant %float 0.473069996
%float_0_349350005 = OpConstant %float 0.349350005
%float_0_287169993 = OpConstant %float 0.287169993
         %15 = OpConstantComposite %v4float %float_0_534550011 %float_0_473069996 %float_0_349350005 %float_0_287169993
%float_0_671949983 = OpConstant %float 0.671949983
%float_0_599919975 = OpConstant %float 0.599919975
%float_0_482129991 = OpConstant %float 0.482129991
%float_0_436780006 = OpConstant %float 0.436780006
         %20 = OpConstantComposite %v4float %float_0_671949983 %float_0_599919975 %float_0_482129991 %float_0_436780006
%float_0_763759971 = OpConstant %float 0.763759971
%float_0_677200019 = OpConstant %float 0.677200019
%float_0_553610027 = OpConstant %float 0.553610027
%float_0_516499996 = OpConstant %float 0.516499996
         %25 = OpConstantComposite %v4float %float_0_763759971 %float_0_677200019 %float_0_553610027 %float_0_516499996
%float_0_779959977 = OpConstant %float 0.779959977
%float_0_688619971 = OpConstant %float 0.688619971
%float_0_561869979 = OpConstant %float 0.561869979
%float_0_526109993 = OpConstant %float 0.526109993
         %30 = OpConstantComposite %v4float %float_0_779959977 %float_0_688619971 %float_0_561869979 %float_0_526109993
         %31 = OpConstantComposite %mat4v4float %15 %20 %25 %30
   %float_n1 = OpConstant %float -1
    %float_3 = OpConstant %float 3
   %float_n3 = OpConstant %float -3
    %float_1 = OpConstant %float 1
         %36 = OpConstantComposite %v4float %float_n1 %float_3 %float_n3 %float_1
   %float_n6 = OpConstant %float -6
    %float_0 = OpConstant %float 0
         %39 = OpConstantComposite %v4float %float_3 %float_n6 %float_3 %float_0
         %40 = OpConstantComposite %v4float %float_n3 %float_3 %float_0 %float_0
         %41 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_0
         %42 = OpConstantComposite %mat4v4float %36 %39 %40 %41
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_float_uint_2 = OpTypeArray %float %uint_2
%_ptr_Output__arr_float_uint_2 = OpTypePointer Output %_arr_float_uint_2
%gl_TessLevelInner = OpVariable %_ptr_Output__arr_float_uint_2 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Output_float = OpTypePointer Output %float
      %int_1 = OpConstant %int 1
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Output__arr_float_uint_4 = OpTypePointer Output %_arr_float_uint_4
%gl_TessLevelOuter = OpVariable %_ptr_Output__arr_float_uint_4 Output
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %x %31
         %43 = OpLoad %mat4v4float %x
         %44 = OpMatrixTimesMatrix %mat4v4float %42 %43
               OpStore %x %44
         %53 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_0
               OpStore %53 %float_1
         %55 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_1
               OpStore %55 %float_1
         %60 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_0
               OpStore %60 %float_1
         %61 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_1
               OpStore %61 %float_1
         %63 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_2
               OpStore %63 %float_1
         %65 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_3
               OpStore %65 %float_1
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` requires the `tessellationShader` device feature before program execution.
- The host creates one 4 by 4 `VK_FORMAT_R8G8B8A8_UNORM` image for color-attachment and transfer-source use, plus one 64-byte host-visible transfer-destination buffer.
- The monolithic graphics pipeline uses patch-list input and the generated vertex, tessellation-control, tessellation-evaluation, and fragment modules. No vertex attributes, descriptor sets, or buffer-backed shader inputs are needed.
- The command buffer clears the image to transparent black, binds the pipeline, and calls `vkCmdDraw()` with four vertices. The evaluation shader maps quad-domain coordinates into clip space so the resulting fragments cover the small target.
- Each fragment writes four Boolean comparison results as RGBA. A passing comparison becomes `1.0`; any failed column or component makes at least one channel zero.
- After rendering, an image barrier makes color writes available to the transfer operation. The command buffer copies the image to the output buffer and the host waits for queue completion.
- The host scans all 16 pixels. It requires exact `(1.0, 1.0, 1.0, 1.0)` after UNORM decoding and fails at the first other value ([runtime and oracle](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L153-L188)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `tesc_1` | Incorrect `mat4 * mat4` evaluation, incorrect transport of the four-column patch matrix across tessellation evaluation and fragment interfaces, or a shared render/copy/readback failure. |
| `tesc_2` | The original first column copied to `temp` was corrupted or replaced after the later matrix multiplication, its location-5 patch transport was incorrect, or a shared render/copy/readback failure. |

### Cause Analysis

#### Matrix product evaluation or transport

**Possible failure symptoms:** `tesc_1` produces one or more pixels with a zero red, green, blue, or alpha channel. A channel identifies the matrix column whose four component comparisons did not all pass; the host reports only the overall non-white pixel failure.

**Possible implementation causes:** Shader compilation or execution may evaluate `m * x` with incorrect operand order, column interpretation, arithmetic, or result assignment. The same symptom can come from losing or mismatching one of the four consecutive patch-interface locations as the matrix passes through tessellation evaluation to fragment shading.

#### Pre-product value preservation or vector transport

**Possible failure symptoms:** `tesc_2` produces a non-white pixel even though its fragment shader expects only the original first column. A failure specific to `tesc_2` points to behavior introduced by saving `temp`, overwriting output `x`, or transporting `col0` at location 5.

**Possible implementation causes:** Compiler lowering may alias or reuse the saved local matrix value incorrectly when the later multiplication writes `x`. The control-to-evaluation patch interface or evaluation-to-fragment interface may instead corrupt or mismatch the location-5 vector. The image alone cannot distinguish value-lifetime failure from interface transport failure.

#### Rendering, copy, or host readback

**Possible failure symptoms:** Both leaves may return non-white pixels without a pattern tied to product columns or preserved-vector components. Broad black or partially written output can implicate the shared path.

**Possible implementation causes:** Pipeline execution, tessellation-generated coverage, fragment output, color-attachment writes, the color-to-transfer barrier, image-to-buffer copy, or host-visible memory access may fail to deliver the shader's comparison result to the scan. Source-level investigation of the failed image and command execution is needed to narrow this shared symptom.

## Case Pruning

### Requirement-based pruning

- Every leaf requires the `tessellationShader` feature through [`checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L210-L213). A device without it reports the case as unsupported before execution.
- The family needs no optional matrix feature, geometry shader, descriptor-backed storage, special image format support, or portability-subset tessellation mode.

### Design-based pruning

- Registration contains exactly two hand-authored leaves. The source does not generate a cross-product of operand values, matrix sizes, primitive modes, or tolerances.
- Both leaves keep the same multiplication. One observes the product and the other observes a value whose lifetime spans the output write; other matrix columns and alternate write orders are outside this focused regression shape.
- The source places the preserved vector at location 5 and leaves location 4 unused. It does not register a packed-location counterpart or explain an additional behavior associated with the gap.

## Key Takeaways

- `tesc_1` validates every component of one fixed `mat4 * mat4` result with a `0.01` shader-side tolerance.
- `tesc_2` validates the first input column copied before the same product overwrites a patch output, which tests live-value preservation around that write.
- Both shaders reduce their checks to an RGBA image, and the host requires all channels of all 16 pixels to equal one.
- See `## Failure Meaning` to separate product, preservation/interface, and shared rendering or readback causes.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestType` | [`vktTessellationMatrixMultiplicationTests.cpp#L47-L51`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L47-L51) | Defines the two behavior values. |
| Runtime setup and oracle | [`MatrixMultiplicationTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L64-L188) | Creates resources, draws, copies, and checks every pixel. |
| Support check | [`MatrixMultiplicationTestCase::checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L210-L213) | Requires tessellation shader support. |
| Shader generation | [`MatrixMultiplicationTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L215-L364) | Emits both matrix-control paths and their evaluation and fragment oracles. |
| Family registration | [`createTessellationMatrixMultiplicationTests()`](../../../modules/vulkan/tessellation/vktTessellationMatrixMultiplicationTests.cpp#L368-L375) | Registers `matrix_multiplication.tesc_1` and `tesc_2`. |
| Category attachment | [`createChildren()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L64-L81) | Places the family under `tessellation`. |
| Vulkan default mustpass | [`tessellation.txt#L235-L236`](../../../mustpass/main/vk-default/tessellation.txt#L235-L236) | Confirms both Vulkan executable paths. |
| Vulkan SC default mustpass | [`tessellation.txt#L235-L236`](../../../mustpass/main/vksc-default/tessellation.txt#L235-L236) | Confirms both Vulkan SC executable paths. |
| Tessellation stage model | [`tessellation.adoc#tessellation`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation) | Defines control, tessellator, and evaluation stage sequencing. |
| Shader interface matching | [`interfaces.adoc#interfaces-iointerfaces`](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces) | Defines matching between consecutive graphics-stage interfaces. |
| Matrix location assignment | [`interfaces.adoc#interfaces-iointerfaces-locations`](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-locations) | Defines consecutive location consumption by matrix columns. |
