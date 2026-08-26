## Overview

**Core question:** Do GLSL ES 3.10 structure construction, access, transfer, assignment, comparison, and `std140` uniform-buffer reads produce the expected rendered color in both the vertex and fragment stages?

- This page covers the `glsl.struct` family implemented by [`vktShaderRenderStructTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L38-L2120).
- The family separates structures created in shader-local storage from structures uploaded by the host and read through uniform blocks.
- Every source pattern has a vertex and a fragment leaf. The implementation registers 26 local patterns and 14 uniform patterns, for 80 executable leaves.
- The tests are not compile-only checks. Each shader reduces selected structure members or comparison results to a color, and the shared shader-render harness compares the rendered image with a CPU-generated reference.

## Background Knowledge

- A GLSL structure groups named members that can include scalars, vectors, arrays, or other structures. The tested source patterns combine member selection with construction, whole-structure copies, function calls, array indexing, loops, and equality operators.
- `local` describes where the tested structure value lives. Local cases still use small uniform blocks for integer indices, loop bounds, and constants so that selected expressions are supplied at run time rather than folded entirely from literals.
- Uniform cases declare the tested structure in `layout(std140, set = 0, binding = ...) uniform` blocks. Their C++ setup callbacks use explicitly padded mirror types for layouts such as scalar arrays, nested structures, and arrays of structures.
- Vertex and fragment variants use different observable paths. A vertex variant computes `v_color`, which the pass-through fragment shader writes to the attachment. A fragment variant receives interpolated `v_coords` from the pass-through vertex shader and computes `o_color` directly.
- The CPU reference follows the selected stage: vertex results are evaluated at grid vertices and interpolated over the quads, while fragment results are evaluated at pixel centers.

## Registration Hierarchy

```text
glsl.struct
├── local
└── uniform
```

[`createStructTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L2088-L2120) creates the `struct` root, and `ShaderStructTests::init()` adds the `local` and `uniform` groups. The GLSL package attaches that root below `glsl` in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1269).

`LOCAL_STRUCT_CASE` and `UNIFORM_STRUCT_CASE` each append `_vertex` and `_fragment` to a source-pattern name and register both leaves. [`createStructCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L64-L118) then places the generated GLSL in the selected stage and supplies the other stage's pass-through shader.

The Vulkan and Vulkan SC default mustpass files each list the same 80 suffixes: 52 local leaves followed by 28 uniform leaves ([Vulkan range](../../../mustpass/main/vk-default/glsl.txt#L14833-L14912), [Vulkan SC range](../../../mustpass/main/vksc-default/glsl.txt#L13771-L13850)).

## Parameter Dimensions and Observed Values

| Dimension | Registered or supplied values | Meaning in this test | Evidence |
|-----------|-------------------------------|----------------------|----------|
| Structure storage group | `local`, `uniform` | Selects shader-local structure values or host-uploaded structures in `std140` uniform blocks. | [Root groups](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L120-L134), [uniform group](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1204-L1218) |
| Tested shader stage | `vertex`, `fragment` | Places the same structure source pattern in either stage; the other stage passes coordinates or color through. | [Stage specialization](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L64-L118) |
| Local source patterns | 26 names | Covers construction, nesting, arrays, function parameters and returns, assignment, loops, and comparisons. | [`LocalStructTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L134-L1202) |
| Uniform source patterns | 14 names | Covers layout-sensitive reads, nested and array access, fixed and dynamic loops, and comparisons. | [`UniformStructTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1218-L2086) |
| Index form | Literal or uniform-backed `ui_zero`, `ui_one`, `ui_two` | Selects structure-array elements and array members through static or run-time expressions. | [Local array cases](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L206-L475), [uniform array cases](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1329-L1656) |
| Loop bound form | Literal `2` or `3`; uniform-backed `ui_two` or `ui_three` | Distinguishes fixed loop bounds from values supplied through uniform buffers. | [Local loop cases](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L799-L1047), [uniform loop cases](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1657-L1961) |
| Nested array shape | `S[2]`, each `S` containing `T[3]`, each `T` containing `vec2[2]` | Exercises repeated member selection and array indexing at three levels. | [Local nested-array source](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L324-L475), [uniform nested-array source](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1506-L1656) |
| Result oracle | Stage-specific CPU evaluator and rendered RGBA image | Converts structure behavior into a visible color and compares it with an independently generated reference image. | [Shared iteration and comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805) |

The two registration macros make the total `26 x 2 + 14 x 2 = 80` leaves. The group name is a semantic dimension, not a claim that local cases contain no uniforms: local structures are local, while several controlling values are deliberately descriptor-backed uniforms.

## Behavior Parameters

The primary behavior parameter is the structure operation represented by each source-pattern name. Storage group, indexing form, loop-bound form, and shader stage refine that behavior.

### Construction, nesting, and indexed access

Both groups include these eight names:

- `basic` and `nested`
- `array_member` and `array_member_dynamic_index`
- `struct_array` and `struct_array_dynamic_index`
- `nested_struct_array` and `nested_struct_array_dynamic_index`

`basic` uses scalar, vector, and integer members. `nested` places `T` inside `S`. The array-member pair indexes an array declared inside a structure, the structure-array pair indexes `S[3]`, and the nested pair traverses the `S[2] -> T[3] -> vec2[2]` shape. The `_dynamic_index` forms substitute uniform-backed selectors for literal subscripts ([local access patterns](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L155-L475), [uniform access patterns](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1240-L1656)).

### Function transfer and whole-structure assignment

These behaviors exist only in `local`:

- `parameter`, `parameter_nested`
- `return`, `return_nested`
- `conditional_assignment`, `loop_assignment`, `dynamic_loop_assignment`
- `nested_conditional_assignment`, `nested_loop_assignment`, `nested_dynamic_loop_assignment`

The parameter cases pass an `S` value into `myFunc()`. The return cases construct and return `S` from `myFunc()`. Assignment cases replace either a complete `S` or a nested structure member in a conditional or loop. Dynamic-loop forms obtain the loop bound from a uniform ([function cases](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L477-L599), [assignment cases](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L601-L797)).

### Iteration over arrays of structures

Both groups register:

- `loop_struct_array`, `dynamic_loop_struct_array`
- `loop_nested_struct_array`, `dynamic_loop_nested_struct_array`

The simple cases iterate over `S[3]` and assemble reversed scalar members plus an integer accumulation. The nested cases use two loops to accumulate members from the nested `S`/`T` array shape. Fixed forms use literal bounds; dynamic forms use `ui_two` and `ui_three` ([local loops](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L799-L1047), [uniform loops](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1657-L1961)).

### Whole-structure equality and inequality

The local group has `basic_equal`, `basic_not_equal`, `nested_equal`, and `nested_not_equal`. Each shader constructs several related values and writes the outcomes of `==` or `!=` into RGB channels. The nested pair moves one compared vector and integer into an inner `T` ([local comparisons](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1049-L1201)).

The uniform group has `equal` and `not_equal`. It compares three uploaded `S` values and one shader-constructed `S`, again encoding Boolean outcomes as color channels ([uniform comparisons](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1963-L2085)).

### `std140` uniform-buffer structure reads

Every `uniform` pattern uploads a C++ representation with `addUniform()`. The basic and nested cases place explicit padding around members where required by their intended mirror layout. Array-member cases wrap scalar array elements in padded records, structure-array cases pad each `S`, and nested-array cases mirror `T[3]` and `S[2]` with vector-sized fields and trailing padding ([basic and nested setup](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1240-L1327), [array setup](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1329-L1504), [nested setup](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1506-L1656)).

These leaves observe the combined host-layout, descriptor-upload, shader-access, and rendering path. They do not inspect member offsets directly.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.struct.uniform.nested_struct_array_dynamic_index_fragment
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| Structure storage group = `uniform` | The tested `S[2]` object is prepared by the host and read from a uniform buffer rather than constructed in shader-local storage. |
| Source pattern = `nested_struct_array_dynamic_index` | Selects the deepest registered access shape: `S[2]`, containing `T[3]`, containing `vec2[2]`, with subscripts expressed through uniform-backed integer arithmetic. |
| Tested shader stage = `fragment` | `createStructCase()` installs the generated template as the fragment shader, maps `${DST}` to `o_color`, and leaves `${ASSIGN_POS}` empty. |
| Dynamic selectors = `ui_zero = 0`, `ui_one = 1`, `ui_two = 2` | Three separate uniform buffers drive otherwise in-range accesses to both structure arrays and member arrays. |

#### Purpose

This case verifies that a fragment shader can read the host-populated nested `S[2] -> T[3] -> vec2[2]` uniform layout through dynamically computed indices and combine the selected members into the expected RGBA color.

#### Structural Design

| Shader-visible element or phase | Exact role in this case |
|---------------------------------|-------------------------|
| `v_coords`, location 0 | Input from the fixed pass-through vertex shader. The selected uniform case does not use its value; all tested payload data comes from uniform buffers. |
| Bindings 0, 1, and 2 | Separate uniform buffers contain integer selectors `0`, `1`, and `2`. |
| Binding 3 | Contains two host-populated `S` values. Each `S` has three `T` members, and each `T` has two `vec2` array elements. |
| Four result expressions | Traverse the nested values with selector arithmetic such as `ui_one - 1`, `ui_two - 2`, and `ui_two - ui_one`; preserved source comments state the intended arithmetic. |
| Image oracle | The shader produces `(constCoords.z, constCoords.x, constCoords.w, 1.0)`. The CPU evaluator independently selects `constCoords.zxw`, and the shared harness compares the rendered image with that reference. |

#### Shader Code

```glsl
#version 310 es
layout(location = 0) in mediump vec4 v_coords;
layout(location = 0) out mediump vec4 o_color;
/// Bindings 0-2 are host-created std140 uniform buffers containing the dynamic selectors 0, 1, and 2.
layout (std140, set = 0, binding = 0) uniform buffer0 { int ui_zero; };
layout (std140, set = 0, binding = 1) uniform buffer1 { int ui_one; };
layout (std140, set = 0, binding = 2) uniform buffer2 { int ui_two; };

struct T {
    mediump float    a;
    mediump vec2    b[2];
};
struct S {
    mediump float    a;
    T                b[3];
    int                c;
};
/// Binding 3 is a host-created uniform buffer containing two S values. The host mirror explicitly pads each
/// scalar before vector-aligned data and stores each vec2 array element in a tcu::Vec4-sized slot.
layout (set = 0, binding = 3) uniform buffer3 { S s[2]; };

void main (void)
{
    /// Traverse S[2] -> T[3] -> vec2[2] with uniform-backed index expressions, then encode selected values as RGBA.
    mediump float r = (s[0].b[ui_one].b[ui_one-1].x + s[ui_one].b[ui_two].b[ui_zero+1].y) * s[0].b[0].a; // (z + z) * 0.5
    mediump float g = s[ui_two-1].b[ui_two-2].b[ui_zero].y * s[0].b[ui_two].a * s[ui_one].b[2].a; // x * 0.25 * 4
    mediump float b = (s[ui_zero].b[ui_one+1].b[1].y + s[0].b[ui_one*ui_one].b[0].y + s[ui_one].a) * s[0].b[ui_two-ui_one].a; // (w + w + w) * 0.333
    mediump float a = float(s[ui_zero].c) + s[ui_one-ui_zero].b[ui_two].a - s[ui_zero+ui_one].b[ui_two-ui_one].a; // 0 + 4.0 - 3.0
    o_color = vec4(r, g, b, a);

}
```

#### Additional Info

- [`UNIFORM_STRUCT_CASE`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1220-L1238) registers both stage suffixes; the selected macro invocation and its setup/evaluator are in [`UniformStructTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1577-L1656). `createStructCase()` then supplies the fixed vertex shader that forwards `a_coords` to `v_coords` for this fragment leaf ([stage specialization](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L64-L118)).
- The host mirror uses explicit padding arrays around scalar fields and `tcu::Vec4 b[2]` for the shader's `vec2 b[2]`; binding 3 uploads exactly `2 * sizeof(S)` bytes, while bindings 0-2 are populated through `useUniform()` ([resource setup](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1609-L1655), [selector values](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L966)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Tested shader stage | The vertex sibling substitutes `a_coords`/`v_color`, declares vertex attributes, and assigns `gl_Position`; this fragment case substitutes `v_coords`/`o_color` and emits no position assignment. | [`createStructCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L64-L118) |
| Index form | `nested_struct_array` replaces all selector expressions and bindings 0-2 with literal subscripts, while retaining the same nested structure payload at binding 0. | [Literal case](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1506-L1575), [dynamic case](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1577-L1656) |
| Structure storage group | The local sibling constructs `S s[2]` in `main()` and uses only the three selector buffers; this uniform case reads host-populated `S s[2]` from binding 3. | [Local dynamic case](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L399-L475), [uniform dynamic case](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1577-L1656) |
| Source pattern | Other registered patterns change the member shape and may introduce structure construction, function transfer, whole-structure assignment, loops, or comparisons; this invocation is the nested dynamic-read path. | [Local registrations](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L134-L1202), [uniform registrations](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1218-L2086) |

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
; Bound: 147
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %o_color %v_coords
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpName %main "main"
               OpName %r "r"
               OpName %T "T"
               OpMemberName %T 0 "a"
               OpMemberName %T 1 "b"
               OpName %S "S"
               OpMemberName %S 0 "a"
               OpMemberName %S 1 "b"
               OpMemberName %S 2 "c"
               OpName %buffer3 "buffer3"
               OpMemberName %buffer3 0 "s"
               OpName %_ ""
               OpName %buffer1 "buffer1"
               OpMemberName %buffer1 0 "ui_one"
               OpName %__0 ""
               OpName %buffer2 "buffer2"
               OpMemberName %buffer2 0 "ui_two"
               OpName %__1 ""
               OpName %buffer0 "buffer0"
               OpMemberName %buffer0 0 "ui_zero"
               OpName %__2 ""
               OpName %g "g"
               OpName %b "b"
               OpName %a "a"
               OpName %o_color "o_color"
               OpName %v_coords "v_coords"
               OpDecorate %r RelaxedPrecision
               OpDecorate %_arr_v2float_uint_2 ArrayStride 16
               OpMemberDecorate %T 0 RelaxedPrecision
               OpMemberDecorate %T 0 Offset 0
               OpMemberDecorate %T 1 RelaxedPrecision
               OpMemberDecorate %T 1 Offset 16
               OpDecorate %_arr_T_uint_3 ArrayStride 48
               OpMemberDecorate %S 0 RelaxedPrecision
               OpMemberDecorate %S 0 Offset 0
               OpMemberDecorate %S 1 Offset 16
               OpMemberDecorate %S 2 RelaxedPrecision
               OpMemberDecorate %S 2 Offset 160
               OpDecorate %_arr_S_uint_2 ArrayStride 176
               OpDecorate %buffer3 Block
               OpMemberDecorate %buffer3 0 Offset 0
               OpDecorate %_ Binding 3
               OpDecorate %_ DescriptorSet 0
               OpDecorate %buffer1 Block
               OpMemberDecorate %buffer1 0 RelaxedPrecision
               OpMemberDecorate %buffer1 0 Offset 0
               OpDecorate %__0 Binding 1
               OpDecorate %__0 DescriptorSet 0
               OpDecorate %29 RelaxedPrecision
               OpDecorate %31 RelaxedPrecision
               OpDecorate %32 RelaxedPrecision
               OpDecorate %36 RelaxedPrecision
               OpDecorate %38 RelaxedPrecision
               OpDecorate %buffer2 Block
               OpMemberDecorate %buffer2 0 RelaxedPrecision
               OpMemberDecorate %buffer2 0 Offset 0
               OpDecorate %__1 Binding 2
               OpDecorate %__1 DescriptorSet 0
               OpDecorate %43 RelaxedPrecision
               OpDecorate %buffer0 Block
               OpMemberDecorate %buffer0 0 RelaxedPrecision
               OpMemberDecorate %buffer0 0 Offset 0
               OpDecorate %__2 Binding 0
               OpDecorate %__2 DescriptorSet 0
               OpDecorate %48 RelaxedPrecision
               OpDecorate %49 RelaxedPrecision
               OpDecorate %52 RelaxedPrecision
               OpDecorate %53 RelaxedPrecision
               OpDecorate %55 RelaxedPrecision
               OpDecorate %56 RelaxedPrecision
               OpDecorate %g RelaxedPrecision
               OpDecorate %59 RelaxedPrecision
               OpDecorate %60 RelaxedPrecision
               OpDecorate %62 RelaxedPrecision
               OpDecorate %64 RelaxedPrecision
               OpDecorate %66 RelaxedPrecision
               OpDecorate %68 RelaxedPrecision
               OpDecorate %70 RelaxedPrecision
               OpDecorate %72 RelaxedPrecision
               OpDecorate %73 RelaxedPrecision
               OpDecorate %75 RelaxedPrecision
               OpDecorate %77 RelaxedPrecision
               OpDecorate %78 RelaxedPrecision
               OpDecorate %b RelaxedPrecision
               OpDecorate %81 RelaxedPrecision
               OpDecorate %83 RelaxedPrecision
               OpDecorate %84 RelaxedPrecision
               OpDecorate %86 RelaxedPrecision
               OpDecorate %88 RelaxedPrecision
               OpDecorate %90 RelaxedPrecision
               OpDecorate %91 RelaxedPrecision
               OpDecorate %93 RelaxedPrecision
               OpDecorate %94 RelaxedPrecision
               OpDecorate %96 RelaxedPrecision
               OpDecorate %98 RelaxedPrecision
               OpDecorate %99 RelaxedPrecision
               OpDecorate %101 RelaxedPrecision
               OpDecorate %103 RelaxedPrecision
               OpDecorate %104 RelaxedPrecision
               OpDecorate %106 RelaxedPrecision
               OpDecorate %107 RelaxedPrecision
               OpDecorate %a RelaxedPrecision
               OpDecorate %110 RelaxedPrecision
               OpDecorate %112 RelaxedPrecision
               OpDecorate %113 RelaxedPrecision
               OpDecorate %115 RelaxedPrecision
               OpDecorate %117 RelaxedPrecision
               OpDecorate %118 RelaxedPrecision
               OpDecorate %120 RelaxedPrecision
               OpDecorate %122 RelaxedPrecision
               OpDecorate %123 RelaxedPrecision
               OpDecorate %125 RelaxedPrecision
               OpDecorate %127 RelaxedPrecision
               OpDecorate %128 RelaxedPrecision
               OpDecorate %130 RelaxedPrecision
               OpDecorate %132 RelaxedPrecision
               OpDecorate %133 RelaxedPrecision
               OpDecorate %135 RelaxedPrecision
               OpDecorate %136 RelaxedPrecision
               OpDecorate %o_color RelaxedPrecision
               OpDecorate %o_color Location 0
               OpDecorate %140 RelaxedPrecision
               OpDecorate %141 RelaxedPrecision
               OpDecorate %142 RelaxedPrecision
               OpDecorate %143 RelaxedPrecision
               OpDecorate %144 RelaxedPrecision
               OpDecorate %v_coords RelaxedPrecision
               OpDecorate %v_coords Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %v2float = OpTypeVector %float 2
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_v2float_uint_2 = OpTypeArray %v2float %uint_2
          %T = OpTypeStruct %float %_arr_v2float_uint_2
     %uint_3 = OpConstant %uint 3
%_arr_T_uint_3 = OpTypeArray %T %uint_3
        %int = OpTypeInt 32 1
          %S = OpTypeStruct %float %_arr_T_uint_3 %int
%_arr_S_uint_2 = OpTypeArray %S %uint_2
    %buffer3 = OpTypeStruct %_arr_S_uint_2
%_ptr_Uniform_buffer3 = OpTypePointer Uniform %buffer3
          %_ = OpVariable %_ptr_Uniform_buffer3 Uniform
      %int_0 = OpConstant %int 0
      %int_1 = OpConstant %int 1
    %buffer1 = OpTypeStruct %int
%_ptr_Uniform_buffer1 = OpTypePointer Uniform %buffer1
        %__0 = OpVariable %_ptr_Uniform_buffer1 Uniform
%_ptr_Uniform_int = OpTypePointer Uniform %int
     %uint_0 = OpConstant %uint 0
%_ptr_Uniform_float = OpTypePointer Uniform %float
    %buffer2 = OpTypeStruct %int
%_ptr_Uniform_buffer2 = OpTypePointer Uniform %buffer2
        %__1 = OpVariable %_ptr_Uniform_buffer2 Uniform
    %buffer0 = OpTypeStruct %int
%_ptr_Uniform_buffer0 = OpTypePointer Uniform %buffer0
        %__2 = OpVariable %_ptr_Uniform_buffer0 Uniform
     %uint_1 = OpConstant %uint 1
      %int_2 = OpConstant %int 2
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %v_coords = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
          %r = OpVariable %_ptr_Function_float Function
          %g = OpVariable %_ptr_Function_float Function
          %b = OpVariable %_ptr_Function_float Function
          %a = OpVariable %_ptr_Function_float Function
         %28 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %29 = OpLoad %int %28
         %30 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %31 = OpLoad %int %30
         %32 = OpISub %int %31 %int_1
         %35 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %int_0 %int_1 %29 %int_1 %32 %uint_0
         %36 = OpLoad %float %35
         %37 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %38 = OpLoad %int %37
         %42 = OpAccessChain %_ptr_Uniform_int %__1 %int_0
         %43 = OpLoad %int %42
         %47 = OpAccessChain %_ptr_Uniform_int %__2 %int_0
         %48 = OpLoad %int %47
         %49 = OpIAdd %int %48 %int_1
         %51 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %38 %int_1 %43 %int_1 %49 %uint_1
         %52 = OpLoad %float %51
         %53 = OpFAdd %float %36 %52
         %54 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %int_0 %int_1 %int_0 %int_0
         %55 = OpLoad %float %54
         %56 = OpFMul %float %53 %55
               OpStore %r %56
         %58 = OpAccessChain %_ptr_Uniform_int %__1 %int_0
         %59 = OpLoad %int %58
         %60 = OpISub %int %59 %int_1
         %61 = OpAccessChain %_ptr_Uniform_int %__1 %int_0
         %62 = OpLoad %int %61
         %64 = OpISub %int %62 %int_2
         %65 = OpAccessChain %_ptr_Uniform_int %__2 %int_0
         %66 = OpLoad %int %65
         %67 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %60 %int_1 %64 %int_1 %66 %uint_1
         %68 = OpLoad %float %67
         %69 = OpAccessChain %_ptr_Uniform_int %__1 %int_0
         %70 = OpLoad %int %69
         %71 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %int_0 %int_1 %70 %int_0
         %72 = OpLoad %float %71
         %73 = OpFMul %float %68 %72
         %74 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %75 = OpLoad %int %74
         %76 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %75 %int_1 %int_2 %int_0
         %77 = OpLoad %float %76
         %78 = OpFMul %float %73 %77
               OpStore %g %78
         %80 = OpAccessChain %_ptr_Uniform_int %__2 %int_0
         %81 = OpLoad %int %80
         %82 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %83 = OpLoad %int %82
         %84 = OpIAdd %int %83 %int_1
         %85 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %81 %int_1 %84 %int_1 %int_1 %uint_1
         %86 = OpLoad %float %85
         %87 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %88 = OpLoad %int %87
         %89 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %90 = OpLoad %int %89
         %91 = OpIMul %int %88 %90
         %92 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %int_0 %int_1 %91 %int_1 %int_0 %uint_1
         %93 = OpLoad %float %92
         %94 = OpFAdd %float %86 %93
         %95 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
         %96 = OpLoad %int %95
         %97 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %96 %int_0
         %98 = OpLoad %float %97
         %99 = OpFAdd %float %94 %98
        %100 = OpAccessChain %_ptr_Uniform_int %__1 %int_0
        %101 = OpLoad %int %100
        %102 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
        %103 = OpLoad %int %102
        %104 = OpISub %int %101 %103
        %105 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %int_0 %int_1 %104 %int_0
        %106 = OpLoad %float %105
        %107 = OpFMul %float %99 %106
               OpStore %b %107
        %109 = OpAccessChain %_ptr_Uniform_int %__2 %int_0
        %110 = OpLoad %int %109
        %111 = OpAccessChain %_ptr_Uniform_int %_ %int_0 %110 %int_2
        %112 = OpLoad %int %111
        %113 = OpConvertSToF %float %112
        %114 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
        %115 = OpLoad %int %114
        %116 = OpAccessChain %_ptr_Uniform_int %__2 %int_0
        %117 = OpLoad %int %116
        %118 = OpISub %int %115 %117
        %119 = OpAccessChain %_ptr_Uniform_int %__1 %int_0
        %120 = OpLoad %int %119
        %121 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %118 %int_1 %120 %int_0
        %122 = OpLoad %float %121
        %123 = OpFAdd %float %113 %122
        %124 = OpAccessChain %_ptr_Uniform_int %__2 %int_0
        %125 = OpLoad %int %124
        %126 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
        %127 = OpLoad %int %126
        %128 = OpIAdd %int %125 %127
        %129 = OpAccessChain %_ptr_Uniform_int %__1 %int_0
        %130 = OpLoad %int %129
        %131 = OpAccessChain %_ptr_Uniform_int %__0 %int_0
        %132 = OpLoad %int %131
        %133 = OpISub %int %130 %132
        %134 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %128 %int_1 %133 %int_0
        %135 = OpLoad %float %134
        %136 = OpFSub %float %123 %135
               OpStore %a %136
        %140 = OpLoad %float %r
        %141 = OpLoad %float %g
        %142 = OpLoad %float %b
        %143 = OpLoad %float %a
        %144 = OpCompositeConstruct %v4float %140 %141 %142 %143
               OpStore %o_color %144
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each leaf is a `ShaderStructCase`, a thin `ShaderRenderCase` wrapper carrying the selected-stage flag, generated vertex and fragment source, CPU evaluator, and uniform-setup callback ([case wrapper](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L38-L58)).
- `ShaderRenderCase::initPrograms()` compiles the generated pair as `vert` and `frag`, and `createInstance()` transfers the evaluator and setup callback to `ShaderRenderCaseInstance` ([program and instance creation](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L607-L633)).
- The setup callback binds predefined scalar values through `useUniform()`. Uniform-structure cases additionally upload explicitly prepared bytes through `addUniform()`; both paths create uniform-buffer descriptor bindings ([descriptor data setup](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L823-L865), [predefined values](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L977)).
- `iterate()` initializes resources, creates a quad grid, renders the generated shader pair, and copies the result image for host access ([iteration](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L800), [image copyback](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2580-L2600)).
- For a vertex leaf, the harness evaluates expected colors at grid vertices and interpolates them over each triangle. For a fragment leaf, it evaluates expected colors at pixel centers ([vertex reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2690), [fragment reference](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2692-L2719)).
- The harness compares result and reference images with `compareImages(..., 0.2f)`. The active shared comparison mode determines whether that value is a fuzzy threshold or whether the pixel-threshold path uses one integer unit per RGBA channel. Success reports `Result image matches reference`; failure reports `Image mismatch` ([comparison and status](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L799-L805), [comparison implementation](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2721-L2730)).

The runtime checker observes the final image. It does not read back a structure, report a member offset, or identify the compiler instruction that produced a wrong value.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` or `nested` | Structure construction or member selection, nested access, selected-stage execution, or the shared render/reference path. |
| Static access passes but `_dynamic_index` fails | Uniform selector delivery, dynamic subscript lowering, member/element addressing, or the shared path. |
| `parameter` or `return` | Structure argument transfer, return-value handling, whole-value copies, or the shared path. |
| Conditional or loop assignment | Whole-structure or nested-member assignment under control flow, loop execution, uniform loop bounds, or the shared path. |
| Fixed loop passes but dynamic loop fails | Uniform loop-bound delivery or dynamic-loop handling, in addition to the same structure-array operations. |
| Local comparison | Whole-structure `==`/`!=`, recursive nested comparison for nested leaves, Boolean-to-color encoding, or the shared path. |
| Uniform access or comparison | Host mirror layout, descriptor upload/binding, `std140` shader addressing, the selected structure operation, or the shared path. |
| Vertex sibling only | Generated vertex execution, color varying output/interpolation, or vertex-reference construction, in addition to the named operation. |
| Fragment sibling only | Coordinate varying input/interpolation, generated fragment execution, or fragment-reference construction, in addition to the named operation. |

### Cause Analysis

#### Structure operation or control-flow handling

**Possible failure symptoms:** A local access, function, assignment, loop, or comparison leaf returns `Image mismatch`, often while a simpler sibling passes.

**Possible implementation causes:** The generated GLSL may have been compiled or executed incorrectly for construction, nested member access, whole-structure copying, function transfer, assignment, indexing, loop execution, or comparison. A sibling can narrow the source pattern—for example, static versus dynamic indexing—but the image oracle cannot identify a compiler pass or Vulkan stage by itself.

#### Uniform layout, upload, or addressing

**Possible failure symptoms:** Uniform leaves fail while corresponding local access shapes pass, or failures concentrate on arrays and nested structures with explicit host padding.

**Possible implementation causes:** The complete tested path includes the C++ mirror bytes, buffer creation and flush, descriptor binding, `std140` addressing, and shader member access. The source patterns make layout-sensitive failures visible, but they do not query offsets or distinguish host setup from shader lowering. Source-level inspection of the failing leaf and captured data is required.

#### Stage handoff or common rendering path

**Possible failure symptoms:** Many unrelated leaves fail in only one stage, or both storage groups show similarly placed image differences.

**Possible implementation causes:** The pass-through shader, vertex-to-fragment interpolation, rasterization, image copyback, CPU reference generation, or image comparison can differ from the expected path. The final `Image mismatch` status does not prove that the named structure operation alone is faulty.

## Case Pruning

### Requirement-based pruning

The structure implementation defines no family-specific `checkSupport()` override, extension gate, feature test, format query, or device-limit filter. Registration unconditionally creates both stage leaves for every macro invocation. The cases therefore rely on the common GLSL ES 3.10 shader-render and uniform-buffer path; any broader package or framework requirement is outside the family-specific source ([case type and registration](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L38-L153), [root registration](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L2088-L2120)).

### Design-based pruning

- Function parameter/return and conditional/whole-structure assignment patterns are local-only. The uniform group focuses on reads, indexing, loops, and comparisons of descriptor-backed structure values.
- Literal and dynamic variants are paired for array-member, structure-array, nested-array, and loop behavior. `basic`, `nested`, and comparison names do not add an index-form axis where no such access is central to the source pattern.
- Nested-array coverage fixes one deep shape, `S[2] -> T[3] -> vec2[2]`, rather than enumerating every array length, nesting depth, or member type.
- Comparison coverage uses four local names to distinguish basic versus nested and equality versus inequality. Uniform coverage keeps only `equal` and `not_equal` for its uploaded basic `S` values.
- Every retained source pattern has both shader stages. The generator does not prune one stage based on the operation or storage group.

These are generator design choices that define the 80-leaf matrix; they are not runtime skips.

## Key Takeaways

- `glsl.struct` contains 80 image-checked leaves: 26 local and 14 uniform source patterns, each emitted for vertex and fragment execution.
- Local coverage includes structure construction, nested and array access, function transfer, whole-structure and nested assignment, loops, and comparisons.
- Uniform coverage combines those read-oriented operations with explicitly prepared `std140` host mirror data and descriptor-backed upload.
- Static/dynamic and vertex/fragment siblings help narrow a failure, but the final oracle remains a rendered-image comparison across the complete shader-render path.
- The family has no structure-specific feature pruning. Its exclusions are deliberate limits of the generated source-pattern matrix.
- An image mismatch proves that the complete tested path did not produce the evaluator's expected color; see `Failure Meaning` for the causes that result can and cannot distinguish.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Structure case wrapper | [`ShaderStructCase`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L38-L58) | Connects generated sources, selected stage, evaluator, and uniform setup to the shared render case. |
| Stage specialization | [`createStructCase()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L64-L118) | Defines the GLSL ES version, pass-through shaders, and `${HEADER}`, `${COORDS}`, `${DST}`, and `${ASSIGN_POS}` substitutions. |
| Local registration and cases | [`LocalStructTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L134-L1202) | Registers the 26 local source patterns and their 52 stage leaves. |
| Uniform registration and cases | [`UniformStructTests::init()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L1218-L2086) | Registers the 14 uniform source patterns, padded mirror data, and their 28 stage leaves. |
| Structure-family factory | [`ShaderStructTests` and `createStructTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.cpp#L2088-L2120) | Creates `struct` and attaches its `local` and `uniform` children. |
| Public factory declaration | [`vktShaderRenderStructTests.hpp`](../../../modules/vulkan/shaderrender/vktShaderRenderStructTests.hpp#L22-L35) | Exposes `createStructTests()` to the GLSL package. |
| GLSL package registration | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1269) | Places the family below `glsl`. |
| Shared shader program and instance creation | [`ShaderRenderCase`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L575-L633) | Compiles the generated shader pair and creates the runtime instance. |
| Shared uniform setup | [`addUniform()` and `useUniform()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L823-L865), [`useUniform()` values](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L945-L977) | Defines descriptor-backed data upload and predefined scalar controls. |
| Shared execution and oracle | [`ShaderRenderCaseInstance::iterate()`](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L773-L805), [reference and comparison](../../../modules/vulkan/shaderrender/vktShaderRender.cpp#L2603-L2730) | Renders, computes the stage-specific reference image, compares images, and returns pass or fail. |
| Vulkan default mustpass coverage | [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L14833-L14912) | Lists all 80 `dEQP-VK.glsl.struct` leaves. |
| Vulkan SC default mustpass coverage | [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L13771-L13850) | Lists the same 80 suffixes under `dEQP-VKSC.glsl.struct`. |
