## Overview

**Core question:** Can a compute shader select different sampled-image descriptors for different invocations and still produce the expected per-index result, and can a render pass sample a descriptor array whose allocated count is smaller than its declared size?

- This page covers the five direct `descriptor_indexing` test cases registered by [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L791-L820).
- The four `misc_common_nonuniform_index_arraysize_*` cases use three runtime-sized sampled-image arrays, `nonuniformEXT` descriptor selection, and one storage buffer for results. Their matrix varies the array size, `8` or `64`, and the sample coordinate, `0` or `mid`.
- The fifth case, `misc_variable_count`, renders with a `sampler2D` array binding that declares eight descriptors but allocates and writes only two, combining `descriptorBindingVariableDescriptorCount` with `descriptorBindingPartiallyBound`.
- The page explains the registration hierarchy, feature and limit gates, shader sources, image and descriptor setup, result checking, pruning, and failure meaning.

## Background Knowledge

- A sampled-image descriptor array contains separate image descriptors that shader code can select with an array index. Vulkan requires the appropriate descriptor-indexing feature when that index is a non-uniform integer expression. The [`shaderSampledImageArrayNonUniformIndexing` specification entry](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderSampledImageArrayNonUniformIndexing) defines this feature for sampler and sampled-image arrays.
- A runtime-sized shader array does not provide an unrestricted descriptor range. The selected element must exist in the bound descriptor binding, and `runtimeDescriptorArray` must be enabled. The [`runtimeDescriptorArray` specification entry](../../../../vulkan-docs/src/chapters/features.adoc#features-runtimeDescriptorArray) describes that capability, while the [descriptor array interface rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-resources) define the binding and array-element requirements.
- Non-uniform indexing allows different invocations to select different descriptors. Implementations that do not natively support this access may execute a dynamic instruction more than once to access the required descriptors, as described by [`shaderSampledImageArrayNonUniformIndexingNative`](../../../../vulkan-docs/src/chapters/limits.adoc#limits-shaderSampledImageArrayNonUniformIndexingNative). The test therefore checks the values produced by each invocation rather than assuming one hardware instruction per invocation.
- A descriptor set layout can declare a large array binding while allocation provides fewer actual descriptors. The [`descriptorBindingVariableDescriptorCount` specification entry](../../../../vulkan-docs/src/chapters/features.adoc#features-descriptorBindingVariableDescriptorCount) defines that capability, which `VkDescriptorSetVariableDescriptorCountAllocateInfo` uses to pass the actual per-binding count at `VkAllocateDescriptorSets` time.
- A variable-count array binding is normally combined with the [`descriptorBindingPartiallyBound` specification entry](../../../../vulkan-docs/src/chapters/features.adoc#features-descriptorBindingPartiallyBound): only the elements that shader code actually reads must hold valid writes, and unwritten elements inside the declared extent are permitted.

## Registration Hierarchy

`createDescriptorIndexingMiscTests` receives the already-created `descriptor_indexing` test category group and appends the five test cases directly. It does not create an intermediate test family or nested `TestCaseGroup`. The registration loop adds the four `misc_common_nonuniform_index_arraysize_*` cases, and a final `addChild` adds `misc_variable_count` ([`MiscVariableCountTestCase`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L819)).

```text
descriptor_indexing
├── misc_common_nonuniform_index_arraysize_8_at_0
├── misc_common_nonuniform_index_arraysize_8_at_mid
├── misc_common_nonuniform_index_arraysize_64_at_0
├── misc_common_nonuniform_index_arraysize_64_at_mid
└── misc_variable_count
```

All five paths appear in the default [`descriptor-indexing.txt`](../../../mustpass/main/vk-default/descriptor-indexing.txt#L24-L28) mustpass list, with the four `misc_common_nonuniform_index_arraysize_*` paths at lines 24-27 and `misc_variable_count` at line 28. The caller invokes the misc registration after registering `non_uniform_atomics` ([`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4938-L4942)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Array size | `8`, `64` | Sets the number of descriptors in each sampled-image array, the compute `local_size_x`, and the number of output elements. | [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L802-L817) and [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L131-L165) |
| Sample coordinate | `0`, `mid` | Selects `{ Vec2(0.0f, 0.0f), "0" }` or `{ Vec2(0.5f, 0.5f), "mid" }` for all three image samples. | [`testCoords`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L795-L800) |
| Sampled-image arrays | `Tex0[]`, `Tex1[]`, `Tex2[]` | Keeps the indexed descriptor class fixed while making the three input values independent. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L146-L149) |
| Image format | `VK_FORMAT_R32G32B32A32_UINT` | Makes each sampled value a `uvec4` and permits exact integer comparison. | [`TestParams`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L66-L71) and [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L806-L810) |
| Image extent | `numElementsPerArray` by `numElementsPerArray` | Gives the `8` and `64` cases square images with a coordinate that can select the corner or midpoint texel. | [`iterate`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L300-L311) |
| Descriptor sets | Sets `0`, `1`, `2`, and `3` | Sets `0` through `2` hold one sampled-image array each. Set `3` holds the output storage buffer and one sampler. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L146-L150) and descriptor layout setup ([`iterate`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L388-L417)) |
| Declared versus allocated array count | `misc_variable_count` only: declared `8`, allocated `2` | Decouples the layout capacity of the `sampler2D` array binding from the descriptor count that allocation and writes actually provide. | [`MiscVariableCountTestInstance::iterate`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L607-L636) |

## Behavior Parameters

The primary behavioral axis is the registered case name. For the four `misc_common_nonuniform_index_arraysize_*` cases the values combine the sampled-image array length with the coordinate used by the shader and CPU reference. `misc_variable_count` is a single fixed-parameter graphics case.

### `misc_common_nonuniform_index_arraysize_8_at_0`: eight descriptors, corner sample

Each of the three arrays contains eight sampled-image descriptors. One eight-invocation workgroup uses `gl_GlobalInvocationID.x` values `0` through `7` to select matching elements. Both shader and CPU reference sample at `(0.0, 0.0)`.

### `misc_common_nonuniform_index_arraysize_8_at_mid`: eight descriptors, midpoint sample

This case keeps the eight-element descriptor arrays and changes the sample coordinate to `(0.5, 0.5)`. It checks that the same non-uniform descriptor selection works when the sampled texel is taken from the image midpoint.

### `misc_common_nonuniform_index_arraysize_64_at_0`: 64 descriptors, corner sample

Each array contains 64 sampled-image descriptors, and the workgroup has 64 invocations. The shader selects indices `0` through `63` and samples `(0.0, 0.0)`. The three arrays consume `3 * 64 = 192` sampled-image descriptors.

### `misc_common_nonuniform_index_arraysize_64_at_mid`: 64 descriptors, midpoint sample

This case combines the larger descriptor arrays with the midpoint coordinate. It exercises the same expression and result rule as the other cases across 64 distinct per-invocation descriptor selections.

### `misc_variable_count`: variable-count partially bound sampler array

This case uses one descriptor set whose layout pairs a single UBO binding with an eight-element `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER` array binding carrying `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT | VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT` ([layout setup](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L620-L626)). Allocation passes `VkDescriptorSetVariableDescriptorCountAllocateInfo` with count `2`, so the set really holds only two combined image samplers ([allocate info](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L628-L636)), and only those two elements receive 1x1 texture writes ([descriptor writes](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L660-L667)). A four-vertex full-screen draw samples `tex[0]` and `tex[1]` and multiplies them: yellow `(255,255,0,255)` times cyan `(0,255,255,255)` gives green `(0,255,0,255)`, and every pixel of the 16x16 render must equal that value ([pixel check](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L719-L732)). The shader never touches elements 2-7, so the case passes only if the implementation honors the reduced allocation and partial-write state instead of faulting or reading garbage through the declared eight-element extent.

## Shader Analysis

The four `misc_common_nonuniform_index_arraysize_*` cases share one generated compute shader. The first walkthrough below uses `dEQP-VK.descriptor_indexing.misc_common_nonuniform_index_arraysize_8_at_mid`; the `64` cases change the local size and resource counts, while the shader dataflow remains the same. `misc_variable_count` contributes its own fixed vertex and fragment shaders, covered by the second walkthrough.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.descriptor_indexing.misc_common_nonuniform_index_arraysize_8_at_mid
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `numElementsPerArray = 8` | Emits `layout(local_size_x = 8) in` and creates eight descriptors in each of the three sampled-image arrays. |
| `coordinate = Vec2(0.5f, 0.5f)` | Emits `vec2(0.5,0.5)` in each `textureLod` call and makes the `mid` test case. |
| `format = VK_FORMAT_R32G32B32A32_UINT` | Makes each sample an exact `uvec4` value. |

#### Purpose

The shader tests non-uniform indexing of three sampled-image descriptor arrays. Each invocation selects the same index in all three arrays, computes `a * b + c`, and stores the result at that index.

#### Structural Design

| Shader phase | Operation | Tested consequence |
|---|---|---|
| Invocation index | Read `gl_GlobalInvocationID.x` into `index`. | Different invocations select different descriptor elements. |
| Three descriptor reads | Apply `nonuniformEXT` to `Tex0[index]`, `Tex1[index]`, and `Tex2[index]` before sampling. | Each sampled-image array uses the descriptor-indexing path. |
| Integer combine | Compute `a * b + c`. | The three independently initialized image values remain distinguishable in the output. |
| Result write | Store to `data[index]`. | The host can compare one result for every array element. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_nonuniform_qualifier : require

/// One workgroup covers the complete eight-element descriptor array in this representative case.
layout(local_size_x = 8) in;

/// Sets 0, 1, and 2 each contain a runtime-sized array of sampled-image descriptors. The index is marked non-uniform at use sites below.
layout(set = 0, binding = 0) uniform utexture2D Tex0[];
layout(set = 1, binding = 0) uniform utexture2D Tex1[];
layout(set = 2, binding = 0) uniform utexture2D Tex2[];
/// Set 3 receives the host-visible result buffer and the sampler shared by all image arrays.
layout(set = 3, binding = 0) writeonly buffer SSBO { uvec4 data[]; };
layout(set = 3, binding = 1) uniform sampler Samp;

void main()
{
    /// The global invocation ID is the descriptor-array index and output element.
    uint index = gl_GlobalInvocationID.x;
    /// nonuniformEXT applies to the sampled-image object formed from the selected image and shared sampler.
    uvec4 a = textureLod(nonuniformEXT(usampler2D(Tex0[index], Samp)), vec2(0.5,0.5), 0.0);
    uvec4 b = textureLod(nonuniformEXT(usampler2D(Tex1[index], Samp)), vec2(0.5,0.5), 0.0);
    uvec4 c = textureLod(nonuniformEXT(usampler2D(Tex2[index], Samp)), vec2(0.5,0.5), 0.0);
    /// The host reference evaluates the same component-wise unsigned-integer expression.
    data[index] = a * b + c;
}
```

#### Additional Info

- `Tex0`, `Tex1`, and `Tex2` are three separate `VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE` array bindings. `Samp` is one `VK_DESCRIPTOR_TYPE_SAMPLER`, not an element of those arrays ([descriptor layouts](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L392-L417)).
- The source generator emits `#extension GL_EXT_nonuniform_qualifier : require` and uses `textureLod` with an explicit level of `0.0` ([`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L139-L164)).
- The source constructs the coordinate string from `m_params.coordinate.x()` for both components. The registered coordinates currently have equal components, so `0` and `mid` still emit the intended `(0,0)` and `(0.5,0.5)` values ([`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L133-L135), [`testCoords`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L795-L800)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Array size | Changes `local_size_x` from `8` to `64`; declarations and arithmetic stay unchanged. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L131-L145) |
| Sample coordinate | Changes the literal passed to all three `textureLod` calls from `vec2(0.0,0.0)` to `vec2(0.5,0.5)`. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L133-L135) and [`testCoords`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L795-L800) |
| Descriptor index | Remains `gl_GlobalInvocationID.x` in every case, but ranges over eight or 64 invocations. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L152-L161) and dispatch ([`iterate`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L523-L525)) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 79
; Schema: 0
               OpCapability Shader
               OpCapability ShaderNonUniform
               OpCapability RuntimeDescriptorArray
               OpExtension "SPV_EXT_descriptor_indexing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 8 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_nonuniform_qualifier"
               OpName %main "main"
               OpName %index "index"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %a "a"
               OpName %Tex0 "Tex0"
               OpName %Samp "Samp"
               OpName %b "b"
               OpName %Tex1 "Tex1"
               OpName %c "c"
               OpName %Tex2 "Tex2"
               OpName %SSBO "SSBO"
               OpMemberName %SSBO 0 "data"
               OpName %_ ""
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %Tex0 Binding 0
               OpDecorate %Tex0 DescriptorSet 0
               OpDecorate %Samp Binding 1
               OpDecorate %Samp DescriptorSet 3
               OpDecorate %33 NonUniform
               OpDecorate %Tex1 Binding 0
               OpDecorate %Tex1 DescriptorSet 1
               OpDecorate %49 NonUniform
               OpDecorate %Tex2 Binding 0
               OpDecorate %Tex2 DescriptorSet 2
               OpDecorate %60 NonUniform
               OpDecorate %_runtimearr_v4uint ArrayStride 16
               OpDecorate %SSBO BufferBlock
               OpMemberDecorate %SSBO 0 NonReadable
               OpMemberDecorate %SSBO 0 Offset 0
               OpDecorate %_ NonReadable
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 3
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
         %19 = OpTypeImage %uint 2D 0 0 0 1 Unknown
%_runtimearr_19 = OpTypeRuntimeArray %19
%_ptr_UniformConstant__runtimearr_19 = OpTypePointer UniformConstant %_runtimearr_19
       %Tex0 = OpVariable %_ptr_UniformConstant__runtimearr_19 UniformConstant
%_ptr_UniformConstant_19 = OpTypePointer UniformConstant %19
         %27 = OpTypeSampler
%_ptr_UniformConstant_27 = OpTypePointer UniformConstant %27
       %Samp = OpVariable %_ptr_UniformConstant_27 UniformConstant
         %31 = OpTypeSampledImage %19
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
  %float_0_5 = OpConstant %float 0.5
         %37 = OpConstantComposite %v2float %float_0_5 %float_0_5
    %float_0 = OpConstant %float 0
%_runtimearr_19_0 = OpTypeRuntimeArray %19
%_ptr_UniformConstant__runtimearr_19_0 = OpTypePointer UniformConstant %_runtimearr_19_0
       %Tex1 = OpVariable %_ptr_UniformConstant__runtimearr_19_0 UniformConstant
%_runtimearr_19_1 = OpTypeRuntimeArray %19
%_ptr_UniformConstant__runtimearr_19_1 = OpTypePointer UniformConstant %_runtimearr_19_1
       %Tex2 = OpVariable %_ptr_UniformConstant__runtimearr_19_1 UniformConstant
%_runtimearr_v4uint = OpTypeRuntimeArray %v4uint
       %SSBO = OpTypeStruct %_runtimearr_v4uint
%_ptr_Uniform_SSBO = OpTypePointer Uniform %SSBO
          %_ = OpVariable %_ptr_Uniform_SSBO Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_v4uint = OpTypePointer Uniform %v4uint
     %uint_8 = OpConstant %uint 8
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_8 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_uint Function
          %a = OpVariable %_ptr_Function_v4uint Function
          %b = OpVariable %_ptr_Function_v4uint Function
          %c = OpVariable %_ptr_Function_v4uint Function
         %14 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %15 = OpLoad %uint %14
               OpStore %index %15
         %23 = OpLoad %uint %index
         %25 = OpAccessChain %_ptr_UniformConstant_19 %Tex0 %23
         %26 = OpLoad %19 %25
         %30 = OpLoad %27 %Samp
         %32 = OpSampledImage %31 %26 %30
         %33 = OpCopyObject %31 %32
         %39 = OpImageSampleExplicitLod %v4uint %33 %37 Lod %float_0
               OpStore %a %39
         %44 = OpLoad %uint %index
         %45 = OpAccessChain %_ptr_UniformConstant_19 %Tex1 %44
         %46 = OpLoad %19 %45
         %47 = OpLoad %27 %Samp
         %48 = OpSampledImage %31 %46 %47
         %49 = OpCopyObject %31 %48
         %50 = OpImageSampleExplicitLod %v4uint %49 %37 Lod %float_0
               OpStore %b %50
         %55 = OpLoad %uint %index
         %56 = OpAccessChain %_ptr_UniformConstant_19 %Tex2 %55
         %57 = OpLoad %19 %56
         %58 = OpLoad %27 %Samp
         %59 = OpSampledImage %31 %57 %58
         %60 = OpCopyObject %31 %59
         %61 = OpImageSampleExplicitLod %v4uint %60 %37 Lod %float_0
               OpStore %c %61
         %68 = OpLoad %uint %index
         %69 = OpLoad %v4uint %a
         %70 = OpLoad %v4uint %b
         %71 = OpIMul %v4uint %69 %70
         %72 = OpLoad %v4uint %c
         %73 = OpIAdd %v4uint %71 %72
         %75 = OpAccessChain %_ptr_Uniform_v4uint %_ %int_0 %68
               OpStore %75 %73
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.descriptor_indexing.misc_variable_count
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `tex[8]` array declaration | The fragment shader declares eight `sampler2D` descriptors even though the set is allocated with only two. |
| Allocated descriptor count `2` | `VkDescriptorSetVariableDescriptorCountAllocateInfo` reduces the binding to two combined image samplers, and only those two are written. |
| Texture colors yellow and cyan | The fragment product `texture(tex[0], uv) * texture(tex[1], uv)` must equal green `(0,255,0,255)` at every pixel. |

#### Purpose

The two fixed shaders render one full-screen quadrilateral whose fragment stage multiplies the two written elements of a variable-count, partially bound `sampler2D` array. The shaders never reference elements 2 through 7, so the draw must succeed and produce the expected color even though the declared array extent is larger than the allocated and written descriptor range.

#### Structural Design

| Shader phase | Operation | Tested consequence |
|---|---|---|
| Vertex position | Derive `pos` from `gl_VertexIndex` bits and map it to clip space. | Four `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` vertices cover the whole 16x16 render area without a vertex buffer. |
| Vertex output | Write `uv = pos` to location 0. | Every fragment samples both textures at a coordinate inside the 1x1 texels. |
| Fragment descriptor reads | Load array elements 0 and 1 through constant access chains and sample each. | Only the two written descriptors are referenced despite the declared eight-element extent. |
| Fragment combine | Multiply the two sampled RGBA colors. | The result is green only when the yellow and cyan descriptors are correctly bound and sampled. |
| Fragment output | Write `color` to the color attachment. | The host reads back the render and compares every pixel against `(0,255,0,255)`. |

#### Shader Code

##### Vertex shader

```glsl
#version 450
layout(location = 0) out vec2 uv;
void main() {
    vec2 pos = vec2(float(gl_VertexIndex & 1), float((gl_VertexIndex >> 1) & 1));
    gl_Position = vec4(pos * 2.0f - 1.0f, 0.0f, 1.0f);
    uv = pos;
}
```

##### Fragment shader

```glsl
#version 450
layout(location = 0) in vec2 uv;
layout(location = 0) out vec4 color;
layout(set = 0, binding = 1) uniform sampler2D tex[8];
void main() {
    color = texture(tex[0], uv) * texture(tex[1], uv);
}
```

#### Additional Info

- The fragment shader declares the complete fixed array `sampler2D tex[8]`; the variable descriptor count is applied only on the host side through `VkDescriptorSetVariableDescriptorCountAllocateInfo`, so the shader interface is unchanged ([initPrograms](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L766-L787), [allocate info](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L628-L636)).
- Both indices are compile-time constants, so the SPIR-V uses two `OpAccessChain` instructions with `%int_0` and `%int_1`; no non-uniform or runtime-indexing capability is needed by these shaders.
- The layout also declares a `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` binding that neither shader declares or reads; only the array binding at set 0, binding 1 is part of the shader interface ([layout setup](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L622-L625)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Descriptor count | Fixed: the declared `tex[8]` interface is unchanged while allocation provides two descriptors; there is no registered variation. | [`iterate`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L607-L608) |
| Sampled elements | Fixed: constant indices `tex[0]` and `tex[1]` compile to two constant-indexed access chains. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L778-L786) |
| Vertex generation | Fixed: positions come from `gl_VertexIndex` for all four strip vertices. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L768-L776) |

#### SPIR-V

##### Vertex shader

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
; Bound: 45
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %gl_VertexIndex %_ %uv
               OpSource GLSL 450
               OpName %main "main"
               OpName %pos "pos"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %uv "uv"
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %uv Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_1 = OpConstant %int 1
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
      %int_0 = OpConstant %int 0
    %float_2 = OpConstant %float 2
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_ptr_Output_v2float = OpTypePointer Output %v2float
         %uv = OpVariable %_ptr_Output_v2float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
        %pos = OpVariable %_ptr_Function_v2float Function
         %13 = OpLoad %int %gl_VertexIndex
         %15 = OpBitwiseAnd %int %13 %int_1
         %16 = OpConvertSToF %float %15
         %17 = OpLoad %int %gl_VertexIndex
         %18 = OpShiftRightArithmetic %int %17 %int_1
         %19 = OpBitwiseAnd %int %18 %int_1
         %20 = OpConvertSToF %float %19
         %21 = OpCompositeConstruct %v2float %16 %20
               OpStore %pos %21
         %30 = OpLoad %v2float %pos
         %32 = OpVectorTimesScalar %v2float %30 %float_2
         %34 = OpCompositeConstruct %v2float %float_1 %float_1
         %35 = OpFSub %v2float %32 %34
         %37 = OpCompositeExtract %float %35 0
         %38 = OpCompositeExtract %float %35 1
         %39 = OpCompositeConstruct %v4float %37 %38 %float_0 %float_1
         %41 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %41 %39
         %44 = OpLoad %v2float %pos
               OpStore %uv %44
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment shader

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
; Bound: 33
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %color %uv
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %color "color"
               OpName %tex "tex"
               OpName %uv "uv"
               OpDecorate %color Location 0
               OpDecorate %tex Binding 1
               OpDecorate %tex DescriptorSet 0
               OpDecorate %uv Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %color = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %11 = OpTypeSampledImage %10
       %uint = OpTypeInt 32 0
     %uint_8 = OpConstant %uint 8
%_arr_11_uint_8 = OpTypeArray %11 %uint_8
%_ptr_UniformConstant__arr_11_uint_8 = OpTypePointer UniformConstant %_arr_11_uint_8
        %tex = OpVariable %_ptr_UniformConstant__arr_11_uint_8 UniformConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
         %uv = OpVariable %_ptr_Input_v2float Input
      %int_1 = OpConstant %int 1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %20 = OpAccessChain %_ptr_UniformConstant_11 %tex %int_0
         %21 = OpLoad %11 %20
         %25 = OpLoad %v2float %uv
         %26 = OpImageSampleImplicitLod %v4float %21 %25
         %28 = OpAccessChain %_ptr_UniformConstant_11 %tex %int_1
         %29 = OpLoad %11 %28
         %30 = OpLoad %v2float %uv
         %31 = OpImageSampleImplicitLod %v4float %29 %30
         %32 = OpFMul %v4float %26 %31
               OpStore %color %32
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `iterate()` creates `3 * numElementsPerArray` 2D optimal-tiled images. Each image has format `VK_FORMAT_R32G32B32A32_UINT`, sampled and transfer-destination usage, and extent `numElementsPerArray` by `numElementsPerArray` ([image setup](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L300-L335)).
- The host creates one host-visible color buffer per image. `populateColorBuffer()` fills every texel with a grayscale value whose red component is offset by the linear element index, then flushes the allocation ([initialization](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L338-L350), [`populateColorBuffer`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L245-L269)).
- The implementation creates one image view per image, one nearest-filter sampler, three descriptor-set layouts with `numElementsPerArray` sampled-image descriptors each, and a fourth set with the output storage buffer and sampler ([image views and sampler](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L368-L386), [descriptor layouts and pool](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L388-L424)).
- It copies each host color buffer into its corresponding image, binds the four descriptor sets, and dispatches one workgroup. The dispatch therefore runs `8` or `64` compute invocations, matching the selected array size ([initialization copies](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L491-L513), [bind and dispatch](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L523-L525)).
- A host-write to shader-write barrier protects the initially filled output buffer. A shader-write to host-read barrier follows the dispatch. The host then waits for submission completion and invalidates the output allocation ([barriers and wait](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L515-L539)).
- The CPU reference samples the corresponding initialized color buffers at the selected coordinate and computes the same component-wise expression, `total[elemIdx] = total[elemIdx] * color` for the second array followed by addition of the third array. It compares every `UVec4` result with `deMemCmp` ([reference calculation](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L541-L571), [comparison](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L573-L582)).
- The case returns `TestStatus::fail("Fail")` on the first mismatch and `TestStatus::pass("Pass")` only after all output elements match.
- In `misc_variable_count`, `iterate()` first builds a pool holding one UBO and eight combined image sampler slots, then a layout whose binding 1 combines `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT` and `VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT` ([pool and layout](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L614-L626)). The set is allocated with a variable-count of `2` and receives two `writeArray` image writes only ([allocation and writes](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L628-L667)).
- Two 1x1 textures are filled from one host buffer holding yellow `(255,255,0,255)` and cyan `(0,255,255,255)` through buffer-to-image copies, then a four-vertex draw renders into a 16x16 `VK_FORMAT_R8G8B8A8_UNORM` attachment ([texture data and copies](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L638-L701), [render](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L703-L708)).
- The rendered image is copied back to a host buffer, the submission is waited on and the allocation invalidated, and every pixel must equal `(0,255,0,255)`; the first mismatch logs its coordinates and fails the case ([readback and check](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L710-L732)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `misc_common_nonuniform_index_arraysize_8_at_0` | Incorrect non-uniform sampled-image descriptor selection, image initialization or transfer, compute result, synchronization, or CPU reference at `(0.0, 0.0)`. |
| `misc_common_nonuniform_index_arraysize_8_at_mid` | Incorrect non-uniform sampled-image descriptor selection, image initialization or transfer, compute result, synchronization, or CPU reference at `(0.5, 0.5)`. |
| `misc_common_nonuniform_index_arraysize_64_at_0` | Incorrect handling of the larger 192-descriptor sampled-image set, non-uniform selection, image initialization or transfer, compute result, synchronization, or CPU reference at `(0.0, 0.0)`. |
| `misc_common_nonuniform_index_arraysize_64_at_mid` | Incorrect handling of the larger 192-descriptor sampled-image set, non-uniform selection, image initialization or transfer, compute result, synchronization, or CPU reference at `(0.5, 0.5)`. |
| `misc_variable_count` | Incorrect variable-count allocation or partially-bound state tracking for the eight-element array reduced to two descriptors, descriptor writes, texture transfer, graphics pipeline execution, or render readback producing pixels other than `(0,255,0,255)`. |

### Cause Analysis

#### Per-invocation descriptor selection

**Possible failure symptoms:** One or more output elements differs from the CPU value because an invocation read the wrong element of `Tex0[]`, `Tex1[]`, or `Tex2[]`, or because the three reads did not use the same `index`.

**Possible implementation causes:** The shader uses `gl_GlobalInvocationID.x` as a non-uniform index and emits `NonUniform` decorations on the sampled-image objects in the generated SPIR-V. A failure can indicate incorrect compiler lowering or descriptor-array access behavior. The available source and specification evidence does not identify a particular implementation component, so further source-level investigation is needed for a concrete attribution.

#### Image transfer and sampling

**Possible failure symptoms:** All or some components of the output differ from the reference at the selected coordinate, even when descriptor indices appear correct.

**Possible implementation causes:** The test copies host-filled buffers into images before sampling and uses `VK_IMAGE_LAYOUT_GENERAL` with transfer-destination and sampled usage. A mismatch can involve image initialization, layout or transfer handling, integer sampling, sampler behavior, or coordinate calculation. The test alone does not distinguish those causes.

#### Compute result and host visibility

**Possible failure symptoms:** The output buffer contains stale values, incomplete writes, or arithmetic different from `a * b + c`. The initial `0xFF` fill can remain visible where a shader write did not reach the expected element.

**Possible implementation causes:** The command buffer places a host-write to shader-write barrier before dispatch and a shader-write to host-read barrier after dispatch, then waits and invalidates the allocation. A failure can indicate compute execution, output-buffer access, barrier, queue completion, invalidation, or host-reference behavior. More specific attribution requires investigation of the failing case and implementation.

#### Variable-count partially bound array access

**Possible failure symptoms:** `misc_variable_count` fails with pixels different from `(0,255,0,255)`, or the implementation faults, hangs, or reports device lost while recording or submitting the draw that samples the reduced array binding.

**Possible implementation causes:** The layout declares an eight-element combined image sampler array while allocation provides two descriptors and only elements 0 and 1 are written. A defect can involve honoring `VkDescriptorSetVariableDescriptorCountAllocateInfo`, tracking the `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT` and `VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT` binding flags, or resolving the constant-indexed `tex[0]` and `tex[1]` accesses at draw time. The test itself cannot separate descriptor-model defects from ordinary rendering defects without further investigation.

## Case Pruning

### Requirement-based pruning

- The case requires `VK_EXT_descriptor_indexing`, `runtimeDescriptorArray`, and `shaderSampledImageArrayNonUniformIndexing`. Missing functionality produces `NotSupported`, not a failed result ([support checks](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L100-L112)).
- The implementation rejects a parameter set when `3 * numElementsPerArray` exceeds `maxPerStageDescriptorSampledImages` ([descriptor-count check](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L113-L118)). The 64-element cases therefore need room for 192 sampled-image descriptors.
- The implementation queries support for `VK_FORMAT_R32G32B32A32_UINT` as a 2D optimal-tiled image with transfer-destination and sampled usage. `VK_ERROR_FORMAT_NOT_SUPPORTED` produces `NotSupported` ([format check](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L120-L128)).
- `misc_variable_count` requires `VK_EXT_descriptor_indexing` plus the `descriptorBindingPartiallyBound` and `descriptorBindingVariableDescriptorCount` features. Either feature missing produces `NotSupported` ([support check](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L754-L764)).

### Design-based pruning

- The registration loop intentionally keeps only two array sizes, `8u` and `64u`, and two equal-component coordinates, `0` and `mid` ([registration loop](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L795-L817)).
- The test fixes the format, descriptor count of three arrays, sampler configuration, explicit LOD `0.0`, and one-workgroup dispatch. Those dimensions are part of the common non-uniform sampled-image check rather than independent registered cases.

## Key Takeaways

- The five direct category-root cases cover two mechanisms: four cases test one non-uniform sampled-image dataflow with two array sizes and two image coordinates, and `misc_variable_count` tests a variable-count partially bound sampler array in a render pass.
- `gl_GlobalInvocationID.x` selects one descriptor from each of three sampled-image arrays for each invocation. `nonuniformEXT` marks those sampled-image selections as non-uniform.
- The output contract is exact in both directions: for every array index, the compute shader must write the component-wise value `Tex0[index] * Tex1[index] + Tex2[index]` at the selected coordinate, and `misc_variable_count` must render `(0,255,0,255)` everywhere from a two-descriptor allocation under an eight-element declared array.
- A skipped case means the implementation lacks a required feature, limit, or image-format usage. A failed case means the executed output did not match the CPU reference or expected pixel color; see `## Failure Meaning` for the possible mechanisms.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDescriptorIndexingMiscTests` | [`vktDescriptorIndexingMiscTests.cpp#L791-L820`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L791-L820) | Registers the four loop-generated cases and the final `misc_variable_count` case. |
| `CommonNonUniformDescriptorIndexTestCase::checkSupport` | [`vktDescriptorIndexingMiscTests.cpp#L100-L128`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L100-L128) | Applies extension, feature, descriptor-limit, and format gates. |
| `CommonNonUniformDescriptorIndexTestCase::initPrograms` | [`vktDescriptorIndexingMiscTests.cpp#L131-L165`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L131-L165) | Generates the compute GLSL source. |
| `CommonNonUniformDescriptorIndexTestInstance::iterate` resource setup | [`vktDescriptorIndexingMiscTests.cpp#L292-L489`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L292-L489) | Creates images, host buffers, views, sampler, descriptor sets, and pipeline. |
| `CommonNonUniformDescriptorIndexTestInstance::iterate` dispatch | [`vktDescriptorIndexingMiscTests.cpp#L491-L539`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L491-L539) | Copies image data, applies barriers, dispatches, waits, and invalidates output. |
| `CommonNonUniformDescriptorIndexTestInstance::iterate` verification | [`vktDescriptorIndexingMiscTests.cpp#L541-L582`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L541-L582) | Builds the CPU reference and compares every output element. |
| `MiscVariableCountTestCase::checkSupport` | [`vktDescriptorIndexingMiscTests.cpp#L754-L764`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L754-L764) | Requires the partially-bound and variable-count descriptor-binding features. |
| `MiscVariableCountTestCase::initPrograms` | [`vktDescriptorIndexingMiscTests.cpp#L766-L787`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L766-L787) | Supplies the fixed full-screen vertex shader and two-texture multiply fragment shader. |
| `MiscVariableCountTestInstance::iterate` | [`vktDescriptorIndexingMiscTests.cpp#L598-L735`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L598-L735) | Allocates the variable-count set, renders, reads back, and checks every pixel. |
| Misc caller | [`vktDescriptorSetsIndexingTests.cpp#L4938-L4942`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4938-L4942) | Places misc registration in the category construction path. |
| Default mustpass entries | [`descriptor-indexing.txt#L24-L28`](../../../mustpass/main/vk-default/descriptor-indexing.txt#L24-L28) | Confirms the five exact executable paths. |
| Sampled-image non-uniform feature | [`features.adoc#features-shaderSampledImageArrayNonUniformIndexing`](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderSampledImageArrayNonUniformIndexing) | Defines the required feature for non-uniform sampler and sampled-image arrays. |
| Runtime descriptor array feature | [`features.adoc#features-runtimeDescriptorArray`](../../../../vulkan-docs/src/chapters/features.adoc#features-runtimeDescriptorArray) | Defines support for runtime-sized descriptor arrays. |
| Descriptor array interface rules | [`interfaces.adoc#interfaces-resources`](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-resources) | Defines descriptor binding and array-element requirements. |
| Native non-uniform indexing property | [`limits.adoc#limits-shaderSampledImageArrayNonUniformIndexingNative`](../../../../vulkan-docs/src/chapters/limits.adoc#limits-shaderSampledImageArrayNonUniformIndexingNative) | Explains the implementation-dependent native execution property. |
