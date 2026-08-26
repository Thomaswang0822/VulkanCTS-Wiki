## Overview

**Core question:** Do static, uniform-driven, and loop-driven GLSL indexing forms produce the same rendered result for arrays, vectors, and matrix columns?

- This page covers the `glsl.indexing` test family implemented by [`vktShaderRenderIndexingTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L45-L1360).
- The family contains five intermediate nodes: `varying_array`, `uniform_array`, `tmp_array`, `vector_subscript`, and `matrix_subscript`.
- Each case generates a GLSL ES 3.10 vertex/fragment pair. The selected indexing forms write weighted values and read them back into a color.
- The shared shader-render harness draws a quad, evaluates the expected color in software, and compares the rendered and reference images.
- Type, access form, and shader stage expand the family to 760 registered leaves. The family determines which storage and indexing mechanism each leaf exercises.

## Background Knowledge

- A GLSL subscript can use a literal, such as `arr[2]`, or an integer expression whose value arrives at run time. A compiler may lower those forms differently even when both select the same element.
- A GLSL matrix subscript selects a column. The selected value is therefore a vector whose length equals the matrix row count. This matters for the rectangular matrix cases.
- Vertex outputs become fragment inputs through the graphics pipeline. An array declared across that interface tests both element selection and cross-stage data transport.
- A loop can make the index variable while keeping the trip count constant, or it can obtain the trip count from a uniform. The generated shaders test both forms.

## Registration Hierarchy

```text
glsl.indexing
├── varying_array
├── uniform_array
├── tmp_array
├── vector_subscript
└── matrix_subscript
```

[`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1263) adds `createIndexingTests()` directly below `glsl`. The factory returns the `indexing` group, and `ShaderIndexingTests::init()` creates the five intermediate nodes shown above ([factory and registration](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1184-L1360)). The Vulkan default mustpass list contains all 760 generated leaves ([mustpass range](../../../mustpass/main/vk-default/glsl.txt#L7183-L7942)).

## Parameter Dimensions and Observed Values

| Test family | Data types or shapes | Write access values | Read access values | Stage placement | Registered leaves |
|-------------|----------------------|---------------------|--------------------|-----------------|-------------------|
| `varying_array` | `float`, `vec2`, `vec3`, `vec4` | `static`, `dynamic`, `static_loop`, `dynamic_loop` in the vertex shader | The same four values in the fragment shader | Fixed cross-stage path | 64 |
| `uniform_array` | `float`, `vec2`, `vec3`, `vec4` | Uniform-buffer initialization on the host | `static`, `dynamic`, `static_loop`, `dynamic_loop` | `vertex`, `fragment` | 32 |
| `tmp_array` | `float`, `vec2`, `vec3`, `vec4` | `static`, `dynamic`, `static_loop`, `dynamic_loop`, `const` | The four non-`const` array access values | `vertex`, `fragment` | 160 |
| `vector_subscript` | `vec2`, `vec3`, `vec4` | `direct`, `component`, `static_subscript`, `dynamic_subscript`, `static_loop_subscript`, `dynamic_loop_subscript` | The same six values | `vertex`, `fragment` | 216 |
| `matrix_subscript` | `mat2`, `mat2x3`, `mat2x4`, `mat3x2`, `mat3`, `mat3x4`, `mat4x2`, `mat4x3`, `mat4` | `static`, `dynamic`, `static_loop`, `dynamic_loop` | The same four values | `vertex`, `fragment` | 288 |

The registration loops define these cross-products and leaf counts ([family generation](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1192-L1353)). Most leaves follow this naming form:

```text
<type>_<write_access>_write_<read_access>_read_<shader_stage>
```

`varying_array` omits the stage suffix because the write always occurs in the vertex shader and the read always occurs in the fragment shader. `uniform_array` uses `<type>_<read_access>_read_<shader_stage>` because host initialization replaces the shader write ([array leaf naming](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1202-L1274)).

Dynamic subscripts use integer uniforms `ui_zero`, `ui_one`, `ui_two`, and `ui_three`. Dynamic loops use the uniform matching the element or column count, up to `ui_four`. `IndexingTestUniformSetup` assigns the values and descriptor bindings ([uniform names and setup](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L156-L246)).

## Behavior Parameters

The primary behavioral axis is the test family. It selects the storage location and the kind of GLSL object being indexed. Access mode, type, and stage then vary that mechanism within the selected family.

### `varying_array`: cross-stage array indexing

The vertex shader writes four weighted values to an output array. The fragment shader reads and sums all four elements. Write and read access forms vary independently, so a leaf can combine a static vertex write with a dynamic-loop fragment read, or any other registered pair ([shader construction](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L280-L405)). This family checks array indexing together with transport of the whole array across the vertex-to-fragment interface.

### `uniform_array`: uniform-buffer array reads

The host places four weighted values in `u_arr[4]` at binding 5. The selected shader stage reads the array with one of the four non-`const` access forms and sums its elements ([uniform-array builder](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L408-L519)). A vertex-stage leaf passes the computed color to the fragment shader. A fragment-stage leaf passes coordinates through the vertex shader and performs the uniform-array read in the fragment shader.

### `tmp_array`: local array writes and reads

The selected stage declares a function-local array, writes weighted values with one access form, then reads them with another ([temporary-array builder](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L522-L702)). The `const` write form uses literal constructors. It allocates 40 elements and fills the unused entries so the compiler has a large local array with four relevant constant values ([constant write and array sizing](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L582-L599), [size selection](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L668-L678)).

### `vector_subscript`: vector component access

The shader writes weighted vector components and reduces the vector to a scalar sum. `direct` uses a whole-vector expression or `dot()`, `component` names `.x`, `.y`, `.z`, and `.w`, and the four subscript forms use literals, uniforms, or loops ([vector write and read paths](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L733-L921)). The generator emits only the component uniforms that exist for the selected vector length.

### `matrix_subscript`: matrix column access

The shader builds a matrix one column at a time from rotated coordinate vectors, then sums the columns. The four access forms vary independently for writing and reading ([matrix builder](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L997-L1166)). Nine square and rectangular shapes vary column count and column-vector length. Shape-specific software evaluators reproduce the weighted column sums ([matrix evaluators](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L926-L995)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.indexing.matrix_subscript.mat3x4_dynamic_loop_write_dynamic_read_fragment
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `matrix_subscript` | Exercises indexing of matrix columns rather than array elements or vector components. |
| `mat3x4` | Uses three columns whose selected values are four-component vectors, covering a rectangular matrix shape. |
| `dynamic_loop_write` | Writes columns through loop variable `i`; uniform `ui_three` supplies the three-column loop bound. |
| `dynamic_read` | Reads columns through the independently supplied selectors `ui_zero`, `ui_one`, and `ui_two`. |
| `fragment` | Places the matrix construction and reduction in the fragment shader; the vertex shader only forwards `a_coords` as `v_coords`. |

#### Purpose

This case verifies that a fragment shader can populate all columns of a rectangular `mat3x4` through a uniform-bounded indexed loop, then recover the same columns through uniform-driven dynamic subscripts and produce the expected weighted coordinate sum.

#### Structural Design

| Phase | Shader-visible operation | Result |
|-------|--------------------------|--------|
| Input transport | Read interpolated `v_coords` from location 0 | Initial four-component coordinate vector |
| Dynamic-loop write | For `i` from zero to `ui_three - 1`, assign `tmp[i]`, then rotate `coords.yzwx` and multiply by `0.5` | Three `mat3x4` columns weighted by `1.0`, `0.5`, and `0.25` |
| Dynamic read | Accumulate `tmp[ui_zero]`, `tmp[ui_one]`, and `tmp[ui_two]` | Sum of all three four-component columns |
| Output | Store the sum in location-0 `o_color` | Rendered value compared with `evalSubscriptMat3x4()` |

#### Shader Code

```glsl
#version 310 es
layout(location = 0) out mediump vec4 o_color;
layout(location = 0) in mediump vec4 v_coords;
/// Dynamic reads select the three mat3x4 columns through host-provided integer uniforms.
layout(std140, binding = 0) uniform something0 { mediump int ui_zero; };
layout(std140, binding = 1) uniform something1 { mediump int ui_one; };
layout(std140, binding = 2) uniform something2 { mediump int ui_two; };
/// The dynamic write loop uses the matrix column count (3) supplied at binding 3.
layout(std140, binding = 3) uniform something3 { mediump int ui_three; };

void main()
{
    mediump vec4 coords = v_coords;
    mediump mat3x4 tmp;
    /// Write each column through a loop index, rotating and halving the source coordinates after each write.
    for (int i = 0; i < ui_three; i++)
    {
        tmp[i] = vec4(coords);
        coords = coords.yzwx * 0.5;
    }
    /// Read the same three columns through independent uniform-driven subscripts and sum their vec4 values.
    mediump vec4 res = vec4(0.0);
    res += tmp[ui_zero];
    res += tmp[ui_one];
    res += tmp[ui_two];
    o_color = vec4(res);
}
```

#### Additional Info

- `IndexingTestUniformSetup::setup()` supplies bindings 0 through 4 with integer values zero through four; this exact shader consumes bindings 0, 1, 2, and 3 ([uniform setup](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L203-L209)).
- The omitted vertex shader is fixed transport boilerplate for this fragment-stage case: it writes `gl_Position = a_position` and forwards `a_coords` to `v_coords` ([matrix builder](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1011-L1027), [fragment-stage handoff](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1137-L1141)).
- `ShaderRenderCase::initPrograms()` uses default `ShaderBuildOptions` because this case does not install explicit per-stage options, so the walkthrough targets the baseline SPIR-V 1.0 environment ([program registration](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L625)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Matrix shape | Changes the matrix type, column vector width, number of generated column operations, dynamic-loop-bound uniform, and output padding for two- or three-row results. | [matrix dimensions and specialization](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1006-L1009), [template parameters and padding](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1146-L1162) |
| Write access | Replaces the uniform-bounded loop with literal-column assignments, uniform-selected assignments, or a literal-bounded loop. | [matrix write branches](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1053-L1096) |
| Read access | Replaces the three uniform-selected reads with literal-column reads, a literal-bounded loop, or a uniform-bounded loop. | [matrix read branches](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1098-L1130) |
| Shader stage | Moves the tested matrix logic between vertex and fragment source; the other stage carries either the computed color or the source coordinates across location 0. | [stage interface selection](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1018-L1027), [stage-specific output](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1132-L1141) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 77
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %v_coords %o_color
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpName %main "main"
               OpName %coords "coords"
               OpName %v_coords "v_coords"
               OpName %i "i"
               OpName %something3 "something3"
               OpMemberName %something3 0 "ui_three"
               OpName %_ ""
               OpName %tmp "tmp"
               OpName %res "res"
               OpName %something0 "something0"
               OpMemberName %something0 0 "ui_zero"
               OpName %__0 ""
               OpName %something1 "something1"
               OpMemberName %something1 0 "ui_one"
               OpName %__1 ""
               OpName %something2 "something2"
               OpMemberName %something2 0 "ui_two"
               OpName %__2 ""
               OpName %o_color "o_color"
               OpDecorate %coords RelaxedPrecision
               OpDecorate %v_coords RelaxedPrecision
               OpDecorate %v_coords Location 0
               OpDecorate %12 RelaxedPrecision
               OpDecorate %i RelaxedPrecision
               OpDecorate %22 RelaxedPrecision
               OpDecorate %something3 Block
               OpMemberDecorate %something3 0 RelaxedPrecision
               OpMemberDecorate %something3 0 Offset 0
               OpDecorate %_ Binding 3
               OpDecorate %_ DescriptorSet 0
               OpDecorate %28 RelaxedPrecision
               OpDecorate %tmp RelaxedPrecision
               OpDecorate %34 RelaxedPrecision
               OpDecorate %35 RelaxedPrecision
               OpDecorate %37 RelaxedPrecision
               OpDecorate %38 RelaxedPrecision
               OpDecorate %40 RelaxedPrecision
               OpDecorate %41 RelaxedPrecision
               OpDecorate %43 RelaxedPrecision
               OpDecorate %res RelaxedPrecision
               OpDecorate %something0 Block
               OpMemberDecorate %something0 0 RelaxedPrecision
               OpMemberDecorate %something0 0 Offset 0
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %51 RelaxedPrecision
               OpDecorate %53 RelaxedPrecision
               OpDecorate %54 RelaxedPrecision
               OpDecorate %55 RelaxedPrecision
               OpDecorate %something1 Block
               OpMemberDecorate %something1 0 RelaxedPrecision
               OpMemberDecorate %something1 0 Offset 0
               OpDecorate %__1 Binding 1
               OpDecorate %__1 DescriptorSet 0
               OpDecorate %60 RelaxedPrecision
               OpDecorate %62 RelaxedPrecision
               OpDecorate %63 RelaxedPrecision
               OpDecorate %64 RelaxedPrecision
               OpDecorate %something2 Block
               OpMemberDecorate %something2 0 RelaxedPrecision
               OpMemberDecorate %something2 0 Offset 0
               OpDecorate %__2 Binding 2
               OpDecorate %__2 DescriptorSet 0
               OpDecorate %69 RelaxedPrecision
               OpDecorate %71 RelaxedPrecision
               OpDecorate %72 RelaxedPrecision
               OpDecorate %73 RelaxedPrecision
               OpDecorate %o_color RelaxedPrecision
               OpDecorate %o_color Location 0
               OpDecorate %76 RelaxedPrecision
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %v_coords = OpVariable %_ptr_Input_v4float Input
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
 %something3 = OpTypeStruct %int
%_ptr_Uniform_something3 = OpTypePointer Uniform %something3
          %_ = OpVariable %_ptr_Uniform_something3 Uniform
%_ptr_Uniform_int = OpTypePointer Uniform %int
       %bool = OpTypeBool
%mat3v4float = OpTypeMatrix %v4float 3
%_ptr_Function_mat3v4float = OpTypePointer Function %mat3v4float
  %float_0_5 = OpConstant %float 0.5
      %int_1 = OpConstant %int 1
    %float_0 = OpConstant %float 0
         %46 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_0
 %something0 = OpTypeStruct %int
%_ptr_Uniform_something0 = OpTypePointer Uniform %something0
        %__0 = OpVariable %_ptr_Uniform_something0 Uniform
 %something1 = OpTypeStruct %int
%_ptr_Uniform_something1 = OpTypePointer Uniform %something1
        %__1 = OpVariable %_ptr_Uniform_something1 Uniform
 %something2 = OpTypeStruct %int
%_ptr_Uniform_something2 = OpTypePointer Uniform %something2
        %__2 = OpVariable %_ptr_Uniform_something2 Uniform
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
     %coords = OpVariable %_ptr_Function_v4float Function
          %i = OpVariable %_ptr_Function_int Function
        %tmp = OpVariable %_ptr_Function_mat3v4float Function
        %res = OpVariable %_ptr_Function_v4float Function
         %12 = OpLoad %v4float %v_coords
               OpStore %coords %12
               OpStore %i %int_0
               OpBranch %17
         %17 = OpLabel
               OpLoopMerge %19 %20 None
               OpBranch %21
         %21 = OpLabel
         %22 = OpLoad %int %i
         %27 = OpAccessChain %_ptr_Uniform_int %_ %int_0
         %28 = OpLoad %int %27
         %30 = OpSLessThan %bool %22 %28
               OpBranchConditional %30 %18 %19
         %18 = OpLabel
         %34 = OpLoad %int %i
         %35 = OpLoad %v4float %coords
         %36 = OpAccessChain %_ptr_Function_v4float %tmp %34
               OpStore %36 %35
         %37 = OpLoad %v4float %coords
         %38 = OpVectorShuffle %v4float %37 %37 1 2 3 0
         %40 = OpVectorTimesScalar %v4float %38 %float_0_5
               OpStore %coords %40
               OpBranch %20
         %20 = OpLabel
         %41 = OpLoad %int %i
         %43 = OpIAdd %int %41 %int_1
               OpStore %i %43
               OpBranch %17
         %19 = OpLabel
               OpStore %res %46
         %50 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %51 = OpLoad %int %50
         %52 = OpAccessChain %_ptr_Function_v4float %tmp %51
         %53 = OpLoad %v4float %52
         %54 = OpLoad %v4float %res
         %55 = OpFAdd %v4float %54 %53
               OpStore %res %55
         %59 = OpAccessChain %_ptr_Uniform_int %__1 %int_0
         %60 = OpLoad %int %59
         %61 = OpAccessChain %_ptr_Function_v4float %tmp %60
         %62 = OpLoad %v4float %61
         %63 = OpLoad %v4float %res
         %64 = OpFAdd %v4float %63 %62
               OpStore %res %64
         %68 = OpAccessChain %_ptr_Uniform_int %__2 %int_0
         %69 = OpLoad %int %68
         %70 = OpAccessChain %_ptr_Function_v4float %tmp %69
         %71 = OpLoad %v4float %70
         %72 = OpLoad %v4float %res
         %73 = OpFAdd %v4float %72 %71
               OpStore %res %73
         %76 = OpLoad %v4float %res
               OpStore %o_color %76
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `ShaderIndexingCase` gives the shared `ShaderRenderCase` the generated sources, the selected software evaluator, stage placement, and `IndexingTestUniformSetup` ([case wrapper](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L249-L272)).
- The uniform setup supplies integer selectors at bindings 0 through 4. For `uniform_array`, it also uploads four `Vec4` slots at binding 5. Those slots contain the selected scalar or vector coordinates scaled by `1.0`, `0.5`, `0.25`, and `0.125` ([uniform setup](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L203-L246)).
- The shared case registers the vertex and fragment GLSL sources and creates a `ShaderRenderCaseInstance` ([program and instance creation](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L632)).
- `iterate()` creates a quad grid, renders it, computes a vertex-stage or fragment-stage software reference according to the case, and compares the two images with error threshold `0.2f` ([iteration](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805)).
- Fragment references reset the evaluation context for each pixel, run the selected evaluator, and write its color to the reference image ([fragment reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2718)). The default comparison uses `tcu::fuzzyCompare()`; the alternate path uses `tcu::pixelThresholdCompare()` ([comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

A passing leaf means the generated access forms produced a rendered image accepted against the independently computed reference. If execution reaches the final comparison and the images differ, the case returns `Image mismatch`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `varying_array` | Incorrect array indexing on either stage or incorrect transport of array elements across the stage interface |
| `uniform_array` | Incorrect uniform-buffer array layout, descriptor access, or indexed read |
| `tmp_array` | Incorrect function-local array write/read indexing or incorrect handling of the `const` write form |
| `vector_subscript` | Incorrect vector component selection, subscript lowering, or vector-length handling |
| `matrix_subscript` | Incorrect matrix-column selection, column-vector handling, or rectangular-matrix lowering |

Failures grouped by `dynamic`, loop, or shader-stage suffix can narrow the cause to uniform-driven selection, loop-controlled access, or stage-specific compilation and execution. Broad failures across unrelated families can instead indicate a problem in shared shader compilation, rendering, uniform setup, reference generation, or image comparison.

### Cause Analysis

#### Cross-stage varying-array failure

**Possible failure symptoms:** One or more `varying_array` leaves render colors that disagree with the weighted coordinate sum. Failures may cluster by the vertex write form, fragment read form, or a particular scalar/vector element type.

**Possible implementation causes:** The generated vertex or fragment indexing may select the wrong element, or the array interface may transport the wrong element values. If only one access suffix fails, source-level investigation should start with that generated form rather than assume the interface itself is at fault.

#### Uniform-array access failure

**Possible failure symptoms:** `uniform_array` leaves fail while equivalent coordinate-based array leaves pass. The mismatch may follow one read form, one data type, or one shader stage.

**Possible implementation causes:** Binding 5 data may be interpreted with the wrong uniform-array layout or component width, or a dynamic or loop-based read may select the wrong slot. The source uses four `Vec4` host slots for the `std140` array, so descriptor contents, generated access, and shader lowering are distinct points to inspect.

#### Temporary-array access failure

**Possible failure symptoms:** `tmp_array` failures follow a write form, read form, or shader stage. A failure limited to `const_write` leaves distinguishes the 40-element literal-initialization path from the ordinary four-element coordinate path.

**Possible implementation causes:** The compiler may mishandle local-array storage, indexed assignment, indexed accumulation, or optimization of the constant-filled array. A mismatch does not by itself identify which write or read operation was wrong; the two access tokens in the leaf name identify the smallest source variants to compare.

#### Vector component access failure

**Possible failure symptoms:** `vector_subscript` produces the wrong scalar sum for one vector width or access pair. Failures limited to `component`, `dynamic_subscript`, or a loop suffix separate those forms from the whole-vector `direct` result.

**Possible implementation causes:** Component naming or subscript lowering may select the wrong lane, a dynamic selector may use the wrong uniform, or loop handling may process too few or too many lanes. Width-specific failures can point to the conditional generation for `vec2`, `vec3`, or `vec4`.

#### Matrix column access failure

**Possible failure symptoms:** `matrix_subscript` renders a vector sum that differs from the shape-specific evaluator. Failures may group by column count, row count, write/read access form, or shader stage.

**Possible implementation causes:** Matrix indexing may select the wrong column, preserve the wrong column-vector width, or lower a rectangular shape incorrectly. Dynamic-loop failures can also come from using the wrong column-count uniform. Comparing square and rectangular leaves with the same access pair helps separate shape handling from the access syntax.

#### Shared execution or comparison failure

**Possible failure symptoms:** Many unrelated families return compile errors, unchanged output, or broad image mismatches that do not follow a storage type or access form.

**Possible implementation causes:** Shared shader compilation, descriptor setup, draw execution, reference-image generation, or result comparison may be involved. The page's source does not identify one layer from a broad symptom alone; logs and source-level tracing are needed before assigning the defect.

## Case Pruning

### Requirement-based pruning

`ShaderIndexingCase` has no indexing-specific `checkSupport()` override, feature query, extension gate, format check, or limit check. The family therefore does not remove registered leaves according to optional implementation capabilities. Shader compilation and the common shader-render setup still apply, but they do not prune this family's registration matrix ([case definition](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L249-L272)).

### Design-based pruning

The generator intentionally limits the matrix before it creates leaves:

- `const` is a temporary-array write mode only. Varying-array writes, all array reads, and matrix accesses stop before `INDEXACCESS_CONST` ([array registration loops](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1202-L1274), [matrix registration loops](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1325-L1346)).
- `uniform_array` has no shader write parameter because the host supplies the array contents at binding 5.
- `varying_array` fixes stage placement to a vertex write and fragment read, so it has no `vertex` or `fragment` suffix dimension.
- Vector cases use `vec2`, `vec3`, and `vec4`. They omit scalar `float` because the family tests vector component and subscript forms.
- Matrix cases use the nine two-to-four-column, two-to-four-row float matrix shapes and the four non-`const` access forms.
- Stage-selectable families generate only vertex and fragment variants because this shader-render family is built around a graphics quad and its two generated shader stages.

These exclusions define the intended test design. They are different from runtime `NotSupported` decisions.

## Key Takeaways

- `glsl.indexing` compares equivalent element-selection forms across cross-stage arrays, uniform arrays, local arrays, vector components, and matrix columns.
- The five test families are the primary behavior choices. Access syntax, data shape, and stage placement refine each choice.
- Weighted writes make the expected result deterministic. Software evaluators compute the same array, vector, or shape-specific matrix sum without reusing the generated GLSL.
- The registration matrix contains 760 leaves and deliberately reserves `const` for temporary-array writes.
- A failure path is identified by the family plus its write, read, type, and stage tokens. See `Failure Meaning` for symptom-based diagnosis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Access enums and names | [`IndexAccessType` and `VectorAccessType`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L45-L90) | Defines the exact access tokens used in generated leaf names. |
| Array reference evaluators | [`getArrayCoordsEvalFunc()` and `getArrayUniformEvalFunc()`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L92-L154) | Computes the expected `1.875` weighted sum. |
| Uniform setup | [`IndexingTestUniformSetup`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L186-L246) | Supplies dynamic selectors and uniform-array data. |
| Case wrapper | [`ShaderIndexingCase`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L249-L272) | Connects generated shaders and evaluators to the shared render harness. |
| Varying-array builder | [`createVaryingArrayCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L280-L405) | Generates cross-stage array writes and reads. |
| Uniform-array builder | [`createUniformArrayCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L408-L519) | Generates binding 5 reads in either shader stage. |
| Temporary-array builder | [`createTmpArrayCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L522-L702) | Generates local-array writes, reads, and the `const` form. |
| Vector builder and evaluator | [`vector_subscript` implementation](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L707-L921) | Covers whole-vector, component, subscript, and loop forms. |
| Matrix builder and evaluator | [`matrix_subscript` implementation](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L926-L1166) | Covers column indexing for all registered matrix shapes. |
| Family registration | [`ShaderIndexingTests::init()` and factory](../../../modules/vulkan/shaderrender/vktShaderRenderIndexingTests.cpp#L1184-L1360) | Defines the hierarchy and every generated leaf. |
| GLSL package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1263) | Places `indexing` directly below `glsl`. |
| Shared execution and comparison | [`ShaderRenderCase`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L632), [`iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), and [`compareImages()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730) | Compiles the shaders, renders the quad, computes the reference, and reports the image result. |
| Vulkan default mustpass coverage | [`glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L7183-L7942) | Lists all 760 concrete `dEQP-VK.glsl.indexing.*` leaves. |
