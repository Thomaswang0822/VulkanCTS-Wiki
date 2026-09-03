## Overview

**Core question:** Does the EXT mesh pipeline deliver every generated interface variable with the declared ownership, type, width, dimension, location, and interpolation behavior?

- `vktMeshShaderInOutTestsEXT.cpp` implements the `mesh_shader.ext.in_out` test family.
- Each feature group builds a source-backed list of interface descriptors, then creates 40 deterministic shuffled permutations. Each permutation has `mesh_only` and `task_mesh` test case leaves.
- The mesh shader emits four vertices and two triangles. The fragment shader checks the received interface values and writes blue only when every generated check passes.
- The page explains the registration matrix, support gates, generated shader interfaces, host/device flow, reference comparison, pruning, and failure interpretation.

## Background Knowledge

- A mesh shader's user-defined outputs form the interface consumed by the fragment shader. Matching includes the declared type, location occupancy, and the `perprimitiveEXT` qualifier. Interpolation qualifiers affect delivery semantics rather than ordinary interface matching; legal vertex-owned floating-point values may be interpolated, while primitive-owned and integer values use flat delivery.
- Interface locations contribute to mesh output limits. A scalar or ordinary vector uses one location. A 64-bit three- or four-component vector uses two. Vulkan also counts built-in and user-defined mesh outputs against `maxMeshOutputComponents`, so the implementation reserves four glslang-generated built-ins.

## Registration Hierarchy

```text
mesh_shader.ext.in_out
├── 32_bits_only
├── with_i64
├── with_f64
├── all_but_16_bits
├── with_i16
├── with_f16
└── all_types
```

The source registers `in_out` under the EXT mesh-shader test category. Each feature-group child contains `permutation_0` through `permutation_39`, and every permutation contains the executable leaves `mesh_only` and `task_mesh`. The complete leaf coverage is listed in [vk-default mesh-shader mustpass](../../../mustpass/main/vk-default/mesh-shader.txt#L1370).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Feature group | `32_bits_only`, `with_i64`, `with_f64`, `all_but_16_bits`, `with_i16`, `with_f16`, `all_types` | Selects which 16- and 64-bit types enter the generated interface list | [feature-group table](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1601-L1615) |
| Owner | `VERTEX`, `PRIMITIVE` | Chooses per-vertex or per-primitive transport and its source array size | [owner and array helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L76-L80) |
| Data type | `FLOAT`, `INTEGER` | Selects floating-point or integer GLSL declarations and checks | [type helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L82-L86) |
| Bit width | `B64`, `B32`, `B16` | Selects 64-, 32-, or 16-bit interface types. 8-bit variables are not generated | [width definition](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L88-L94) |
| Data dimension | `SCALAR`, `VEC2`, `VEC3`, `VEC4` | Changes scalar/vector declarations and component-wise checks | [dimension definition](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L96-L102) |
| Interpolation | `NORMAL`, `FLAT` | Controls interpolated versus flat declaration where legal | [interpolation definition](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L104-L108) |
| Variable index | `0`, `1` | Gives two independent variables for each otherwise identical descriptor | [`kVarsPerType`](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L116-L137) |
| Permutation | `permutation_0` through `permutation_39` | Changes declaration order, location assignment, and the retained prefix | [permutation loop](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1667-L1694) |
| Execution path | `mesh_only`, `task_mesh` | Selects direct buffer reads or task payload transfer before mesh output | [leaf construction](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1696-L1716) |
| Counts and dimensions | task count `1,1,1`; mesh count `1,1,1`; image `8 x 8` | Fixes one draw and the reference image extent | [parameter construction](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1704-L1713) |

The source iterates the Cartesian product of owner, data type, bit width, dimension, and interpolation, then removes unsupported combinations before adding two indexed variables for each legal descriptor. It does not register the full product of variable lists. A single seeded RNG generates 40 shuffled permutations, and each retained prefix stops before the 16-location budget would be exceeded.

## Behavior Parameters

The primary behavioral axis is the feature group. It determines the set of interface types that the shaders must declare and move through the pipeline. `mesh_only` and `task_mesh` are execution-path leaves that exercise the same interface list through different producer paths.

### `32_bits_only`: baseline 32-bit interfaces

This group enables neither 64-bit nor 16-bit types. It covers the legal 32-bit floating-point and integer combinations, subject to ownership and interpolation rules.

### `with_i64`: add 64-bit integers

This group adds 64-bit integer variables to the baseline. Integers remain flat, so the group tests wide integer declarations and transfer rather than integer interpolation.

### `with_f64`: add 64-bit floating point

This group adds 64-bit floating-point variables. Normally interpolated 64-bit floating-point variables are excluded by the source because that combination is not legal for this test's interface.

### `all_but_16_bits`: combine both 64-bit classes

This group enables both 64-bit integer and floating-point variables while leaving out 16-bit types. It checks the combined wide-type location and interface behavior.

### `with_i16`: add 16-bit integers

This group enables 16-bit integer variables and checks their storage and interface path. Integer variables use flat interpolation.

### `with_f16`: add 16-bit floating point

This group enables 16-bit floating-point variables. Both the shader feature and input/output 16-bit storage feature gate the cases.

### `all_types`: enable all four optional type flags

This group enables 64-bit integer, 64-bit floating-point, 16-bit integer, and 16-bit floating-point variables. The same legal-combination filters and 16-location trim still apply.

## Shader Analysis

The generated shader path is the behavior under test. The following walkthrough uses an exact registered leaf and shows the shared mesh and fragment stages. The task stage is described as the optional path because it changes transport, not the final interface checks.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.ext.in_out.32_bits_only.permutation_0.mesh_only
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `32_bits_only` | The generated variable list contains only legal 32-bit float and integer descriptors |
| `permutation_0.mesh_only` | The deterministic shuffled list is used directly by the mesh shader, without a task payload stage |
| Four vertices and two triangles | The mesh output provides four vertex entries and two primitive entries for the generated checks |

#### Purpose

This shader path checks that explicitly located mesh outputs arrive in the fragment shader with the expected values. It accepts the range produced by valid vertex interpolation and requires exact primitive values selected by `gl_PrimitiveID`.

#### Structural Design

| Stage or data path | Operation | Observable consequence |
|--------------------|-----------|------------------------|
| Storage buffers | Provide `pvd` and `ppd` source arrays | The mesh shader has known values for every selected descriptor |
| Mesh shader | Calls `SetMeshOutputsEXT(4, 2)`, writes positions, indices, primitive IDs, and interface outputs | Two triangles cover the 8 x 8 target |
| Fragment shader | Checks each location-qualified input and combines the booleans | One failed variable makes the pixel black |
| Host | Copies the color image and compares with blue | The case passes only when the generated interface checks succeed |

#### Shader Code

##### Mesh shader

```glsl
#version 450
#extension GL_EXT_mesh_shader : enable
#extension GL_EXT_shader_explicit_arithmetic_types : enable

layout (local_size_x=1) in;
layout (max_primitives=2, max_vertices=4) out;
layout (triangles) out;

/// The generated user-defined outputs occupy sequential locations. Each declaration is emitted from an IfaceVar descriptor.
layout (location=0) out float vert_f32d1_inter_0[];
layout (location=1) flat out int vert_i32d1_flat_0[];

out gl_MeshPerVertexEXT {
   vec4 gl_Position;
} gl_MeshVerticesEXT[];
out perprimitiveEXT gl_MeshPerPrimitiveEXT {
  int gl_PrimitiveID;
} gl_MeshPrimitivesEXT[];

/// Binding 0 supplies per-vertex source data. Binding 1 supplies per-primitive source data.
layout(set=0, binding=0, std430) readonly buffer PerVertexBlock {
    float vert_f32d1_inter_0[4];
    int vert_i32d1_flat_0[4];
} pvd;
layout(set=0, binding=1, std430) readonly buffer PerPrimitiveBlock {
    int prim_i32d1_flat_0[2];
} ppd;

/// The source generator creates four positions and two triangle index values here.

void main ()
{
    SetMeshOutputsEXT(4, 2);
    for (uint i = 0u; i < 4u; ++i)
        gl_MeshVerticesEXT[i].gl_Position = positions[i];
    gl_PrimitiveTriangleIndicesEXT[0] = indices[0];
    gl_PrimitiveTriangleIndicesEXT[1] = indices[1];
    gl_MeshPrimitivesEXT[0].gl_PrimitiveID = 0;
    gl_MeshPrimitivesEXT[1].gl_PrimitiveID = 1;
    for (uint i = 0u; i < 4u; ++i) {
        vert_f32d1_inter_0[i] = float(pvd.vert_f32d1_inter_0[i]);
        vert_i32d1_flat_0[i] = int(pvd.vert_i32d1_flat_0[i]);
    }
}
```

##### Fragment shader

```glsl
#version 450
#extension GL_EXT_mesh_shader : enable
#extension GL_EXT_shader_explicit_arithmetic_types : enable

/// The fragment inputs match the mesh output locations and qualifiers.
layout (location=0) in float vert_f32d1_inter_0;
layout (location=1) flat in int vert_i32d1_flat_0;
layout (location=0) out vec4 outColor;

/// The full generated shader declares all selected source arrays. These two entries illustrate the check shape.
layout(set=0, binding=0, std430) readonly buffer PerVertexBlock {
    float vert_f32d1_inter_0[4];
    int vert_i32d1_flat_0[4];
} pvd;

void main ()
{
    bool good_vert_f32d1_inter_0 = (vert_f32d1_inter_0 <= max(max(max(pvd.vert_f32d1_inter_0[0], pvd.vert_f32d1_inter_0[1]), pvd.vert_f32d1_inter_0[2]), pvd.vert_f32d1_inter_0[3])) && (vert_f32d1_inter_0 >= min(min(min(pvd.vert_f32d1_inter_0[0], pvd.vert_f32d1_inter_0[1]), pvd.vert_f32d1_inter_0[2]), pvd.vert_f32d1_inter_0[3]));
    bool good_vert_i32d1_flat_0 = (vert_i32d1_flat_0 == pvd.vert_i32d1_flat_0[0]);
    if (good_vert_f32d1_inter_0 && good_vert_i32d1_flat_0)
        outColor = vec4(0.0, 0.0, 1.0, 1.0);
    else
        outColor = vec4(0.0, 0.0, 0.0, 1.0);
}
```

The code above is a compact reconstruction of the generator's structure, not a replacement for the generated artifact. The actual source emits every selected declaration and check from the shuffled list. It also emits both source buffers in the fragment shader and uses the complete owner-specific check expression.

#### Additional Info

- The source-generated mesh and fragment programs use `getMinMeshEXTBuildOptions`, which requests SPIR-V 1.4. The page's compact GLSL is a reconstruction of the generator, not a complete generated artifact, and the page does not include hand-written or hand-edited SPIR-V.
- The task variant copies every selected array entry from bindings into `taskPayloadSharedEXT`, then calls `EmitMeshTasksEXT(1, 1, 1)`. The mesh shader reads `td` instead of `pvd` and `ppd` for that path.
- The source buffers store plain 32-bit `float` and `int` members. Generated assignments convert them to the selected interface type, which lets the same deterministic source values exercise 16-, 32-, and 64-bit declarations.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Owner | Vertex variables use four-element arrays and interpolation-aware range checks; primitive variables use two-element arrays, `perprimitiveEXT`, and `gl_PrimitiveID` selection | [owner checks and declarations](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L205-L290) |
| Data type and interpolation | Integers are flat; primitive variables are flat; legal floating-point vertex variables may use normal interpolation | [registration filters](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1637-L1665) |
| Bit width and dimension | GLSL type names and conversion casts change; 64-bit vec3/vec4 declarations consume two locations | [GLSL type and location helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L171-L213) |
| Feature group | The optional-width variables included in the generated source change with the group flags | [feature filtering](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1637-L1650) |
| Permutation | The declaration order and retained location prefix change, while the same order is shared by `mesh_only` and `task_mesh` | [shuffle and trim](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1667-L1703) |

#### SPIR-V

##### Fragment SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: frag
- Target SPIRV version: spirv1.4

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 80
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %pvd %vert_f32d1_inter_0 %vert_i32d1_flat_0 %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_mesh_shader"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types"
               OpName %main "main"
               OpName %maxValue "maxValue"
               OpName %PerVertexBlock "PerVertexBlock"
               OpMemberName %PerVertexBlock 0 "vert_f32d1_inter_0"
               OpMemberName %PerVertexBlock 1 "vert_i32d1_flat_0"
               OpName %pvd "pvd"
               OpName %minValue "minValue"
               OpName %good_vert_f32d1_inter_0 "good_vert_f32d1_inter_0"
               OpName %vert_f32d1_inter_0 "vert_f32d1_inter_0"
               OpName %good_vert_i32d1_flat_0 "good_vert_i32d1_flat_0"
               OpName %vert_i32d1_flat_0 "vert_i32d1_flat_0"
               OpName %outColor "outColor"
               OpDecorate %_arr_float_uint_4 ArrayStride 4
               OpDecorate %_arr_int_uint_4 ArrayStride 4
               OpDecorate %PerVertexBlock Block
               OpMemberDecorate %PerVertexBlock 0 NonWritable
               OpMemberDecorate %PerVertexBlock 0 Offset 0
               OpMemberDecorate %PerVertexBlock 1 NonWritable
               OpMemberDecorate %PerVertexBlock 1 Offset 16
               OpDecorate %pvd NonWritable
               OpDecorate %pvd Binding 0
               OpDecorate %pvd DescriptorSet 0
               OpDecorate %vert_f32d1_inter_0 Location 0
               OpDecorate %vert_i32d1_flat_0 Flat
               OpDecorate %vert_i32d1_flat_0 Location 1
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
        %int = OpTypeInt 32 1
%_arr_int_uint_4 = OpTypeArray %int %uint_4
%PerVertexBlock = OpTypeStruct %_arr_float_uint_4 %_arr_int_uint_4
%_ptr_StorageBuffer_PerVertexBlock = OpTypePointer StorageBuffer %PerVertexBlock
        %pvd = OpVariable %_ptr_StorageBuffer_PerVertexBlock StorageBuffer
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
%_ptr_Input_float = OpTypePointer Input %float
%vert_f32d1_inter_0 = OpVariable %_ptr_Input_float Input
%_ptr_Input_int = OpTypePointer Input %int
%vert_i32d1_flat_0 = OpVariable %_ptr_Input_int Input
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %77 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
         %79 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
   %maxValue = OpVariable %_ptr_Function_float Function
   %minValue = OpVariable %_ptr_Function_float Function
%good_vert_f32d1_inter_0 = OpVariable %_ptr_Function_bool Function
%good_vert_i32d1_flat_0 = OpVariable %_ptr_Function_bool Function
         %19 = OpAccessChain %_ptr_StorageBuffer_float %pvd %int_0 %int_0
         %20 = OpLoad %float %19
         %22 = OpAccessChain %_ptr_StorageBuffer_float %pvd %int_0 %int_1
         %23 = OpLoad %float %22
         %24 = OpExtInst %float %1 FMax %20 %23
         %26 = OpAccessChain %_ptr_StorageBuffer_float %pvd %int_0 %int_2
         %27 = OpLoad %float %26
         %28 = OpExtInst %float %1 FMax %24 %27
         %30 = OpAccessChain %_ptr_StorageBuffer_float %pvd %int_0 %int_3
         %31 = OpLoad %float %30
         %32 = OpExtInst %float %1 FMax %28 %31
               OpStore %maxValue %32
         %34 = OpAccessChain %_ptr_StorageBuffer_float %pvd %int_0 %int_0
         %35 = OpLoad %float %34
         %36 = OpAccessChain %_ptr_StorageBuffer_float %pvd %int_0 %int_1
         %37 = OpLoad %float %36
         %38 = OpExtInst %float %1 FMin %35 %37
         %39 = OpAccessChain %_ptr_StorageBuffer_float %pvd %int_0 %int_2
         %40 = OpLoad %float %39
         %41 = OpExtInst %float %1 FMin %38 %40
         %42 = OpAccessChain %_ptr_StorageBuffer_float %pvd %int_0 %int_3
         %43 = OpLoad %float %42
         %44 = OpExtInst %float %1 FMin %41 %43
               OpStore %minValue %44
         %50 = OpLoad %float %vert_f32d1_inter_0
         %51 = OpLoad %float %maxValue
         %52 = OpFOrdLessThanEqual %bool %50 %51
               OpSelectionMerge %54 None
               OpBranchConditional %52 %53 %54
         %53 = OpLabel
         %55 = OpLoad %float %vert_f32d1_inter_0
         %56 = OpLoad %float %minValue
         %57 = OpFOrdGreaterThanEqual %bool %55 %56
               OpBranch %54
         %54 = OpLabel
         %58 = OpPhi %bool %52 %5 %57 %53
               OpStore %good_vert_f32d1_inter_0 %58
         %62 = OpLoad %int %vert_i32d1_flat_0
         %64 = OpAccessChain %_ptr_StorageBuffer_int %pvd %int_1 %int_0
         %65 = OpLoad %int %64
         %66 = OpIEqual %bool %62 %65
               OpStore %good_vert_i32d1_flat_0 %66
         %67 = OpLoad %bool %good_vert_f32d1_inter_0
         %68 = OpLoad %bool %good_vert_i32d1_flat_0
         %69 = OpLogicalAnd %bool %67 %68
               OpSelectionMerge %71 None
               OpBranchConditional %69 %70 %78
         %70 = OpLabel
               OpStore %outColor %77
               OpBranch %71
         %78 = OpLabel
               OpStore %outColor %79
               OpBranch %71
         %71 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `InterfaceVariablesInstance::iterate` creates an 8 x 8 `VK_FORMAT_R8G8B8A8_UNORM` color image and a host-visible verification buffer sized to hold the image.
- It creates two host-visible storage buffers, copies `PerVertexData` and `PerPrimitiveData` into them, flushes both allocations, and binds them at set 0 bindings 0 and 1. The descriptor stages include fragment and mesh, plus task when the binary collection contains `task`.
- The graphics pipeline uses the generated task shader when present, the generated mesh shader, and the generated fragment shader. It draws with `cmdDrawMeshTasksEXT(1, 1, 1)`. A task case uses that command count to launch one task workgroup, which emits one mesh workgroup.
- The command buffer transitions the color image from color-attachment output to transfer source, copies it to the verification buffer, and inserts a transfer-to-host barrier before submission and wait.
- The host builds an 8 x 8 blue reference level and compares the copied image with `tcu::floatThresholdCompare` at `0.005` per component. It invalidates the verification-buffer allocation before reading it; a mismatch calls `TCU_FAIL`, and an equal image returns `Pass`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `32_bits_only` | Basic 32-bit float/int interface declaration, location matching, interpolation, mesh-to-fragment transfer, or generated check failure |
| `with_i64` | 64-bit integer interface support, conversion, location use, or transfer failure in addition to the 32-bit baseline |
| `with_f64` | 64-bit floating-point interface support, conversion, interpolation restriction, location use, or transfer failure |
| `all_but_16_bits` | Combined 64-bit integer and floating-point interface behavior or location accounting failure |
| `with_i16` | 16-bit integer interface support, storage feature, conversion, or transfer failure |
| `with_f16` | 16-bit floating-point interface support, storage feature, conversion, or transfer failure |
| `all_types` | Combined 16-bit and 64-bit type coverage, feature interaction, location accounting, or interface transfer failure |

### Cause Analysis

#### Generated interface or location mismatch

**Possible failure symptoms:** The fragment shader writes black pixels because one or more generated values fail their checks. Pipeline creation or shader compilation can also reject incompatible interface declarations.

**Possible implementation causes:** The mesh output and fragment input may disagree in type, location, component occupancy, interpolation decoration, or `perprimitiveEXT` use. The implementation's location trim should keep the generated list within 16 locations, while Vulkan's mesh output component limit still constrains the total output interface.

#### Incorrect vertex interpolation handling

**Possible failure symptoms:** A `NORMAL` vertex variable fails although the value lies within the expected source range, or a value appears outside that range and turns the output black.

**Possible implementation causes:** The device or shader toolchain may mishandle interpolation of the declared floating-point type. The generated check intentionally uses component-wise min/max bounds rather than requiring one source vertex's exact value.

#### Incorrect primitive or integer delivery

**Possible failure symptoms:** A flat integer, or a primitive-owned variable selected by `gl_PrimitiveID`, does not equal its expected source entry and the image becomes black.

**Possible implementation causes:** Flat delivery, primitive ownership, primitive ID assignment, or the generated array indexing may not agree across mesh and fragment stages. The source treats integer variables and primitive variables as flat by construction.

#### Optional-width feature or conversion failure

**Possible failure symptoms:** A group requiring 16- or 64-bit values is reported unsupported, fails shader compilation, or produces black output after execution.

**Possible implementation causes:** The required numeric feature, `shaderFloat16`, `storageInputOutput16`, type conversion, or interface representation may be unavailable or incorrect. The source support checks distinguish unsupported prerequisites from a rendered value mismatch.

#### Task-to-mesh payload failure

**Possible failure symptoms:** `task_mesh` fails while the corresponding `mesh_only` permutation passes, or task shader creation and execution reports an error.

**Possible implementation causes:** The task shader may copy a selected value incorrectly into `taskPayloadSharedEXT`, use a mismatched payload layout, or fail to launch the mesh workgroup with `EmitMeshTasksEXT`. This cause is specific to the task path and does not apply to `mesh_only`.

## Case Pruning

### Requirement-based pruning

- `checkSupport` requires `VK_EXT_mesh_shader` and mesh-shader support through `checkTaskMeshShaderSupportEXT`; task-shader support is additionally required for `task_mesh`. It then requires `shaderFloat64`, `shaderInt64`, or `shaderInt16` for the corresponding group flags. A floating-point 16-bit group requires `shaderFloat16`, and either 16-bit group requires `storageInputOutput16`.
- Four glslang built-ins plus 16 maximum locations are budgeted as `(4 + 16) * 4` components. `checkSupport` calls `TCU_FAIL` if `maxMeshOutputComponents` is lower; this is a precondition failure, not a skipped or trimmed case.
- Feature-group flags remove 64-bit and 16-bit descriptors when the group does not request them.
- The registration loop removes integer `NORMAL`, primitive-owned `NORMAL`, and 64-bit floating-point `NORMAL` descriptors.
- The source defines only 64-, 32-, and 16-bit widths because 8-bit input/output interface variables are unavailable.
- Runtime support gates skip cases when the EXT mesh features, optional numeric features, or 16-bit input/output storage are unavailable.

### Design-based pruning

- The implementation samples 40 seeded pseudorandom permutations instead of registering every ordering of the eligible variables.
- Each shuffled vector is truncated before adding a variable would exceed 16 locations. 64-bit vec3 and vec4 values consume two locations.
- Each retained permutation creates exactly two leaves, `mesh_only` and `task_mesh`, using the same variable order so only the transport path differs.

## Key Takeaways

- `mesh_shader.ext.in_out` tests a generated interface, not one fixed variable declaration.
- The feature group controls optional type coverage; owner, type, width, dimension, interpolation, index, permutation, and execution path control the generated cases.
- The mesh shader writes known values and the fragment shader turns interface correctness into blue pixels. Black pixels mean at least one generated value check failed.
- The task path adds payload transport before the same mesh-to-fragment interface check.
- Support gates and location trimming are part of the test design, so unsupported or over-budget combinations are pruned before execution.

## Source Reference Appendix

- [EXT interface-variable implementation](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp)
- [Interface variable declarations and checks](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L76-L291)
- [Feature-gated support](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L590-L630)
- [Generated program sources](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L632-L924)
- [Runtime execution and image comparison](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L986-L1593)
- [Registration and permutation construction](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597-L1724)
- [EXT mesh support and build options](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L148)
- [Vulkan shader interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces)
- [Vulkan interpolation decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-interpolation-decorations)
- [Vulkan EXT mesh properties](../../../../vulkan-docs/src/chapters/limits.adoc#limits-maxMeshOutputComponents)
- [Vulkan mesh output accounting](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-output)
- [Exact vk-default EXT in_out coverage](../../../mustpass/main/vk-default/mesh-shader.txt#L1370-L1929)
