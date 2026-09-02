## Overview

**Core question:** Can a compute shader select different sampled-image descriptors for different invocations and still produce the expected per-index result?

- This page covers the four direct `descriptor_indexing` test cases registered by [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612).
- The cases use three runtime-sized sampled-image arrays, `nonuniformEXT` descriptor selection, and one storage buffer for results.
- The matrix varies the array size, `8` or `64`, and the sample coordinate, `0` or `mid`.
- The page explains the registration hierarchy, feature and limit gates, generated compute shader, image and descriptor setup, CPU reference calculation, pruning, and failure meaning.

## Background Knowledge

- A sampled-image descriptor array contains separate image descriptors that shader code can select with an array index. Vulkan requires the appropriate descriptor-indexing feature when that index is a non-uniform integer expression. The [`shaderSampledImageArrayNonUniformIndexing` specification entry](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderSampledImageArrayNonUniformIndexing) defines this feature for sampler and sampled-image arrays.
- A runtime-sized shader array does not provide an unrestricted descriptor range. The selected element must exist in the bound descriptor binding, and `runtimeDescriptorArray` must be enabled. The [`runtimeDescriptorArray` specification entry](../../../../vulkan-docs/src/chapters/features.adoc#features-runtimeDescriptorArray) describes that capability, while the [descriptor array interface rules](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-resources) define the binding and array-element requirements.
- Non-uniform indexing allows different invocations to select different descriptors. Implementations that do not natively support this access may execute a dynamic instruction more than once to access the required descriptors, as described by [`shaderSampledImageArrayNonUniformIndexingNative`](../../../../vulkan-docs/src/chapters/limits.adoc#limits-shaderSampledImageArrayNonUniformIndexingNative). The test therefore checks the values produced by each invocation rather than assuming one hardware instruction per invocation.

## Registration Hierarchy

`createDescriptorIndexingMiscTests` receives the already-created `descriptor_indexing` test category group and appends the four test cases directly. It does not create an intermediate test family or nested `TestCaseGroup`.

```text
descriptor_indexing
├── misc_common_nonuniform_index_arraysize_8_at_0
├── misc_common_nonuniform_index_arraysize_8_at_mid
├── misc_common_nonuniform_index_arraysize_64_at_0
└── misc_common_nonuniform_index_arraysize_64_at_mid
```

The four paths also appear in the default [`descriptor-indexing.txt`](../../../mustpass/main/vk-default/descriptor-indexing.txt#L24-L27) mustpass list. The caller invokes the misc registration after registering `non_uniform_atomics` ([`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4920-L4923)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Array size | `8`, `64` | Sets the number of descriptors in each sampled-image array, the compute `local_size_x`, and the number of output elements. | [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L598-L611) and [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L131-L165) |
| Sample coordinate | `0`, `mid` | Selects `{ Vec2(0.0f, 0.0f), "0" }` or `{ Vec2(0.5f, 0.5f), "mid" }` for all three image samples. | [`testCoords`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L591-L596) |
| Sampled-image arrays | `Tex0[]`, `Tex1[]`, `Tex2[]` | Keeps the indexed descriptor class fixed while making the three input values independent. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L146-L149) |
| Image format | `VK_FORMAT_R32G32B32A32_UINT` | Makes each sampled value a `uvec4` and permits exact integer comparison. | [`TestParams`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L66-L71) and [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L602-L605) |
| Image extent | `numElementsPerArray` by `numElementsPerArray` | Gives the `8` and `64` cases square images with a coordinate that can select the corner or midpoint texel. | [`iterate`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L300-L311) |
| Descriptor sets | Sets `0`, `1`, `2`, and `3` | Sets `0` through `2` hold one sampled-image array each. Set `3` holds the output storage buffer and one sampler. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L146-L150) and descriptor layout setup ([`iterate`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L388-L417)) |

## Behavior Parameters

The primary behavioral axis is the registered case name. Its values combine the sampled-image array length with the coordinate used by the shader and CPU reference.

### `misc_common_nonuniform_index_arraysize_8_at_0`: eight descriptors, corner sample

Each of the three arrays contains eight sampled-image descriptors. One eight-invocation workgroup uses `gl_GlobalInvocationID.x` values `0` through `7` to select matching elements. Both shader and CPU reference sample at `(0.0, 0.0)`.

### `misc_common_nonuniform_index_arraysize_8_at_mid`: eight descriptors, midpoint sample

This case keeps the eight-element descriptor arrays and changes the sample coordinate to `(0.5, 0.5)`. It checks that the same non-uniform descriptor selection works when the sampled texel is taken from the image midpoint.

### `misc_common_nonuniform_index_arraysize_64_at_0`: 64 descriptors, corner sample

Each array contains 64 sampled-image descriptors, and the workgroup has 64 invocations. The shader selects indices `0` through `63` and samples `(0.0, 0.0)`. The three arrays consume `3 * 64 = 192` sampled-image descriptors.

### `misc_common_nonuniform_index_arraysize_64_at_mid`: 64 descriptors, midpoint sample

This case combines the larger descriptor arrays with the midpoint coordinate. It exercises the same expression and result rule as the other cases across 64 distinct per-invocation descriptor selections.

## Shader Analysis

The cases share one generated compute shader. The representative walkthrough below uses `dEQP-VK.descriptor_indexing.misc_common_nonuniform_index_arraysize_8_at_mid`; the `64` cases change the local size and resource counts, while the shader dataflow remains the same.

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
- The source constructs the coordinate string from `m_params.coordinate.x()` for both components. The registered coordinates currently have equal components, so `0` and `mid` still emit the intended `(0,0)` and `(0.5,0.5)` values ([`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L133-L135), [`testCoords`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L591-L596)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Array size | Changes `local_size_x` from `8` to `64`; declarations and arithmetic stay unchanged. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L131-L145) |
| Sample coordinate | Changes the literal passed to all three `textureLod` calls from `vec2(0.0,0.0)` to `vec2(0.5,0.5)`. | [`initPrograms`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L133-L135) and [`testCoords`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L591-L596) |
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

## Runtime Execution and Result Checking

- `iterate()` creates `3 * numElementsPerArray` 2D optimal-tiled images. Each image has format `VK_FORMAT_R32G32B32A32_UINT`, sampled and transfer-destination usage, and extent `numElementsPerArray` by `numElementsPerArray` ([image setup](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L300-L335)).
- The host creates one host-visible color buffer per image. `populateColorBuffer()` fills every texel with a grayscale value whose red component is offset by the linear element index, then flushes the allocation ([initialization](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L338-L350), [`populateColorBuffer`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L245-L269)).
- The implementation creates one image view per image, one nearest-filter sampler, three descriptor-set layouts with `numElementsPerArray` sampled-image descriptors each, and a fourth set with the output storage buffer and sampler ([image views and sampler](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L368-L386), [descriptor layouts and pool](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L388-L424)).
- It copies each host color buffer into its corresponding image, binds the four descriptor sets, and dispatches one workgroup. The dispatch therefore runs `8` or `64` compute invocations, matching the selected array size ([initialization copies](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L491-L513), [bind and dispatch](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L523-L525)).
- A host-write to shader-write barrier protects the initially filled output buffer. A shader-write to host-read barrier follows the dispatch. The host then waits for submission completion and invalidates the output allocation ([barriers and wait](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L515-L539)).
- The CPU reference samples the corresponding initialized color buffers at the selected coordinate and computes the same component-wise expression, `total[elemIdx] = total[elemIdx] * color` for the second array followed by addition of the third array. It compares every `UVec4` result with `deMemCmp` ([reference calculation](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L541-L571), [comparison](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L573-L582)).
- The case returns `TestStatus::fail("Fail")` on the first mismatch and `TestStatus::pass("Pass")` only after all output elements match.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `misc_common_nonuniform_index_arraysize_8_at_0` | Incorrect non-uniform sampled-image descriptor selection, image initialization or transfer, compute result, synchronization, or CPU reference at `(0.0, 0.0)`. |
| `misc_common_nonuniform_index_arraysize_8_at_mid` | Incorrect non-uniform sampled-image descriptor selection, image initialization or transfer, compute result, synchronization, or CPU reference at `(0.5, 0.5)`. |
| `misc_common_nonuniform_index_arraysize_64_at_0` | Incorrect handling of the larger 192-descriptor sampled-image set, non-uniform selection, image initialization or transfer, compute result, synchronization, or CPU reference at `(0.0, 0.0)`. |
| `misc_common_nonuniform_index_arraysize_64_at_mid` | Incorrect handling of the larger 192-descriptor sampled-image set, non-uniform selection, image initialization or transfer, compute result, synchronization, or CPU reference at `(0.5, 0.5)`. |

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

## Case Pruning

### Requirement-based pruning

- The case requires `VK_EXT_descriptor_indexing`, `runtimeDescriptorArray`, and `shaderSampledImageArrayNonUniformIndexing`. Missing functionality produces `NotSupported`, not a failed result ([support checks](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L100-L112)).
- The implementation rejects a parameter set when `3 * numElementsPerArray` exceeds `maxPerStageDescriptorSampledImages` ([descriptor-count check](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L113-L118)). The 64-element cases therefore need room for 192 sampled-image descriptors.
- The implementation queries support for `VK_FORMAT_R32G32B32A32_UINT` as a 2D optimal-tiled image with transfer-destination and sampled usage. `VK_ERROR_FORMAT_NOT_SUPPORTED` produces `NotSupported` ([format check](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L120-L128)).

### Design-based pruning

- The registration loop intentionally keeps only two array sizes, `8u` and `64u`, and two equal-component coordinates, `0` and `mid` ([registration loop](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L591-L611)).
- The test fixes the format, descriptor count of three arrays, sampler configuration, explicit LOD `0.0`, and one-workgroup dispatch. Those dimensions are part of the common non-uniform sampled-image check rather than independent registered cases.

## Key Takeaways

- The four direct category-root cases test one descriptor-indexing dataflow with two array sizes and two image coordinates.
- `gl_GlobalInvocationID.x` selects one descriptor from each of three sampled-image arrays for each invocation. `nonuniformEXT` marks those sampled-image selections as non-uniform.
- The output contract is exact: for every array index, the shader must write the component-wise value `Tex0[index] * Tex1[index] + Tex2[index]` at the selected coordinate.
- A skipped case means the implementation lacks a required feature, limit, or image-format usage. A failed case means the executed output did not match the CPU reference; see `## Failure Meaning` for the possible mechanisms.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDescriptorIndexingMiscTests` | [`vktDescriptorIndexingMiscTests.cpp#L587-L612`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612) | Registers the four direct category-root test cases. |
| `CommonNonUniformDescriptorIndexTestCase::checkSupport` | [`vktDescriptorIndexingMiscTests.cpp#L100-L128`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L100-L128) | Applies extension, feature, descriptor-limit, and format gates. |
| `CommonNonUniformDescriptorIndexTestCase::initPrograms` | [`vktDescriptorIndexingMiscTests.cpp#L131-L165`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L131-L165) | Generates the compute GLSL source. |
| `CommonNonUniformDescriptorIndexTestInstance::iterate` resource setup | [`vktDescriptorIndexingMiscTests.cpp#L292-L489`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L292-L489) | Creates images, host buffers, views, sampler, descriptor sets, and pipeline. |
| `CommonNonUniformDescriptorIndexTestInstance::iterate` dispatch | [`vktDescriptorIndexingMiscTests.cpp#L491-L539`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L491-L539) | Copies image data, applies barriers, dispatches, waits, and invalidates output. |
| `CommonNonUniformDescriptorIndexTestInstance::iterate` verification | [`vktDescriptorIndexingMiscTests.cpp#L541-L582`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L541-L582) | Builds the CPU reference and compares every output element. |
| Misc caller | [`vktDescriptorSetsIndexingTests.cpp#L4920-L4923`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4920-L4923) | Places misc registration in the category construction path. |
| Default mustpass entries | [`descriptor-indexing.txt#L24-L27`](../../../mustpass/main/vk-default/descriptor-indexing.txt#L24-L27) | Confirms the four exact executable paths. |
| Sampled-image non-uniform feature | [`features.adoc#features-shaderSampledImageArrayNonUniformIndexing`](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderSampledImageArrayNonUniformIndexing) | Defines the required feature for non-uniform sampler and sampled-image arrays. |
| Runtime descriptor array feature | [`features.adoc#features-runtimeDescriptorArray`](../../../../vulkan-docs/src/chapters/features.adoc#features-runtimeDescriptorArray) | Defines support for runtime-sized descriptor arrays. |
| Descriptor array interface rules | [`interfaces.adoc#interfaces-resources`](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-resources) | Defines descriptor binding and array-element requirements. |
| Native non-uniform indexing property | [`limits.adoc#limits-shaderSampledImageArrayNonUniformIndexingNative`](../../../../vulkan-docs/src/chapters/limits.adoc#limits-shaderSampledImageArrayNonUniformIndexingNative) | Explains the implementation-dependent native execution property. |
