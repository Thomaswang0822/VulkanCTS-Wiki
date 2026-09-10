## Overview

**Core question:** Do single-layer image views retain correct size queries and texel access when the shader's arrayed image type disagrees with the view type?

- The `binding_model.image_array_m11` test family covers the maintenance11 single-layer descriptor aliasing behavior implemented in `vktBindingImageArrayMaintenance11Tests.cpp`.
- CTS creates the image with `VK_IMAGE_CREATE_ALIAS_SINGLE_LAYER_DESCRIPTOR_BIT_KHR`, exposes one selected layer through a view, and deliberately chooses the opposite arrayed/non-arrayed shader declaration. It tests explicit-LOD sampling, storage-image loads, and storage-image stores. [Image setup](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L436-L457); [shader type selection](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L307).
- Each case checks the queried dimensions before accessing texels, then compares image-format pixels with expanded shader vectors on the host. The query and data-access checks share the same final comparison rather than separate result flags. [Shader guard](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L350-L401); [comparison](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L711-L769).

## Background Knowledge

- An image view describes which mip levels and array layers a descriptor exposes. A view's base array layer selects a layer in the underlying image; an array coordinate in a shader addresses a layer relative to that view. An arrayed view can expose just one layer.
- An arrayed image type such as `image2DArray` is one image resource with a layer coordinate. It is not a descriptor array such as an array of separate image variables. The mismatch here concerns the image type's arrayedness.
- Sampled-image coordinates are normalized spatial coordinates; an explicit LOD selects the mip level. Storage-image loads and stores use integer texel coordinates. CTS therefore needs different coordinate and size-query expressions for these access modes. [Coordinate and operation generation](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L309-L377).

## Registration Hierarchy

```text
binding_model
└── image_array_m11
```

The [parent registration](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L62-L75) adds this family only outside `CTS_USES_VULKANSC`. Its [factory](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L776-L890) registers format and view-type intermediate nodes, then executable leaves. The [Vulkan mustpass list](../../../mustpass/main/vk-default/binding-model.txt#L48435-L49514) contains 1,080 unique cases for this family; the [Vulkan SC binding-model list](../../../mustpass/main/vksc-default/binding-model.txt) contains none.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| 8-bit format | `r8_unorm`, `r8_uint`, `r8_sint`, `r8g8_unorm`, `r8g8_uint`, `r8g8_sint`, `r8g8b8a8_unorm`, `r8g8b8a8_uint`, `r8g8b8a8_sint` | One, two, or four channels; normalized versus unsigned/signed integer access. | [Formats](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L780-L789) |
| 16-bit format | `r16_unorm`, `r16_uint`, `r16_sint`, `r16g16_unorm`, `r16g16_uint`, `r16g16_sint`, `r16g16b16a16_unorm`, `r16g16b16a16_uint`, `r16g16b16a16_sint` | The same channel/type combinations at a higher image precision. | [Formats](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L790-L798) |
| 32-bit format | `r32_sfloat`, `r32_uint`, `r32_sint`, `r32g32_sfloat`, `r32g32_uint`, `r32g32_sint`, `r32g32b32a32_sfloat`, `r32g32b32a32_uint`, `r32g32b32a32_sint` | Floating point replaces UNORM; integer variants remain. | [Formats](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L799-L807) |
| View type | `view_type_1d`, `view_type_1d_array`, `view_type_2d`, `view_type_2d_array` | Determines spatial dimensionality and the direction of the arrayedness mismatch. Only dimension-matched image/view pairs are generated. | [View matrix](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L810-L851) |
| Sampled leaf | `sampler_lod_00`, `sampler_lod_01`, `sampler_lod_02`, `sampler_lod_10`, `sampler_lod_11`, `sampler_lod_12` | The two final digits concatenate base layer and LOD, in that order. For example, `sampler_lod_12` means layer 1 and LOD 2. | [Leaf construction](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L853-L879) |
| Storage leaf | `storage_img_0_load`, `storage_img_0_store`, `storage_img_1_load`, `storage_img_1_store` | Selects base layer 0 or 1 and transfer direction; storage cases use LOD 0. | [Leaf construction](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L853-L879) |
| Tested mip extent | 1D: `4096 × 1 × 1`; 2D: `64 × 64 × 1` | Fixed queried/processed size. Creation width, and 2D height, are multiplied by `1 << lod`, so the selected mip keeps this extent. | [Extent helpers](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L140-L172) |
| Image and view ranges | Image: `layer + 1` layers and `lod + 1` mip levels; view: one layer starting at `layer`, all created mips | Separates underlying-image layer count from the single layer visible through the descriptor. | [Count helpers](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L155-L177); [View range](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L436-L457) |

Every format/view pair has the same ten leaves. Registration and mustpass agree on the full matrix: 27 formats, four view types, and ten leaves per pair.

## Behavior Parameters

The primary behavioral axis is the registered view type: it determines which side of the descriptor interface is arrayed. The operation leaves then vary the access instruction without changing that mismatch rule.

### view_type_1d — arrayed shader, non-arrayed 1D view

The shader declares a `sampler1DArray` or `image1DArray` variant while the host binds a non-arrayed 1D view. Its size query must yield width and a single visible layer; integer coordinates include layer zero. The generator pads the query to `uvec3` for comparison with the fixed 1D extent. [Type and coordinate branches](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L322); [Query expansion](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L350-L377).

### view_type_1d_array — non-arrayed shader, single-layer 1D array view

The host exposes one layer through a 1D array view, but the shader uses the non-arrayed 1D type. Coordinates carry only a column, and the size query has only a width component. Selecting base layer 1 still refers to that selected layer even though the shader has no layer coordinate. [Generator](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L377); [Selected view layer](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L454-L457).

### view_type_2d — arrayed shader, non-arrayed 2D view

The shader uses a 2D array type over a non-arrayed 2D view. Its size query must produce width, height, and one layer. The shader maps its linear invocation index to a row and column, then accesses relative array layer zero. [Generator](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L401).

### view_type_2d_array — non-arrayed shader, single-layer 2D array view

The host binds a single-layer 2D array view to a non-arrayed shader type. The shader queries width and height, pads depth to one, and accesses with two spatial coordinates. This reverses the arrayedness relationship exercised by `view_type_2d`. [Generator](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L401).

Across these values, `sampler_lod_*` uses `textureSize` and `textureLod`; `storage_img_*_load` uses `imageSize` and `imageLoad`; `storage_img_*_store` uses `imageSize` and `imageStore`. For sampled array types, the generated normalization expression also transforms the layer component: relative layer zero becomes 0.5 when the queried layer count is one. The walkthrough below uses integer-coordinate storage access; the sampling cases retain that distinct expression. [Work and coordinates](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L309-L348).

## Shader Analysis

The representative uses storage-image loading with an arrayed shader type and a non-arrayed view. It exposes the size guard, relative layer coordinate, and host-visible payload in one compute shader; the variation table covers sampling, stores, and the reverse mismatch.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.image_array_m11.r32_uint.view_type_2d.storage_img_1_load
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `r32_uint` | Unsigned integer image access with `r32ui`; the buffer stores `uvec4` values. |
| `view_type_2d` | Non-arrayed host view paired with `uimage2DArray` in the shader. |
| `storage_img_1_load` | Read mip 0 from underlying layer 1 through relative array coordinate zero. |

#### Purpose

Check that the mismatched descriptor reports `64 × 64 × 1` and supplies the selected layer's integer texels. The host compares the expanded shader results with the uploaded pixel data.

#### Structural Design

| Shader expression | Role in the check |
|-------------------|-------------------|
| `imageSize(img)` | Query the descriptor as an arrayed image, including the visible layer count. |
| `sizeOK && globalInvocationIndex < pixelCount` | Permit payload writes only for the expected dimensions and an in-range invocation. |
| `ivec3(invCol, invRow, 0)` | Turn a linear index into a texel coordinate in the view's sole layer. |
| `imageLoad` into `ssbo.values` | Preserve the read result for host comparison, including default missing-channel values. |

#### Shader Code

```glsl
#version 460
/// The host dispatches 64 workgroups, covering the 4096 texels.
layout (local_size_x=64, local_size_y=1, local_size_z=1) in;
/// Binding 0: R32_UINT storage image, non-arrayed 2D view of base layer 1.
/// The shader deliberately declares an arrayed image type.
layout (set=0, binding=0, r32ui) uniform uimage2DArray img;
/// Binding 1: host-readable storage buffer with 4096 expanded uvec4 results.
layout (set=0, binding=1) buffer BufferBlock { uvec4 values[]; } ssbo;
void main (void) {
    /// A wrong descriptor size suppresses the payload write; there is no fail flag.
    const uvec3 imageSize = uvec3(uvec3(imageSize(img)));
    const bool sizeOK = (imageSize == uvec3(64, 64, 1));
    const uint pixelCount = imageSize.x * imageSize.y;
    const uint globalInvocationIndex = gl_WorkGroupID.x * gl_WorkGroupSize.x + gl_LocalInvocationIndex;
    if (sizeOK && globalInvocationIndex < pixelCount) {
        const uint invRow = globalInvocationIndex / imageSize.x;
        const uint invCol = globalInvocationIndex % imageSize.x;
        /// Layer zero is relative to the view, whose underlying base layer is one.
        const ivec3 coords = ivec3(invCol, invRow, 0);
        /// The generator emits this expression even for storage-image operations.
        const vec3 normCoords = ((vec3(coords) + vec3(0.5)) / vec3(imageSize));
        ssbo.values[globalInvocationIndex] = imageLoad(img, coords);
    }
}
```

#### Additional Info

- The source reconstructs this program in [ImageArrayCase::initPrograms](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L401). There are no source-generated shader comments in this builder; `///` comments above are wiki annotations.
- Although the image has two underlying layers, the view exposes only layer 1. The array-size check expects one visible layer, not the underlying image's layer count. [Image/view creation](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L436-L457).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| View type | Array views remove the shader `Array` suffix and the layer coordinate; 1D changes coordinate and size-query component counts. | [Type and coordinates](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L377) |
| Access leaf | Stores reverse the SSBO/image data direction. Sampling switches to a sampler, uses normalized coordinates, and inserts the chosen explicit LOD into query and access. | [Access generation](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L291-L377) |
| Format | Signed integer formats use `i`-prefixed image/sampler types and `ivec4`; unsigned use `u` and `uvec4`; UNORM/SFLOAT use unprefixed types and `vec4`. Storage declarations carry the format qualifier. | [Qualifier mapping](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L51-L93); [Prefix selection](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L307) |
| Base layer | No emitted shader change: the host view selects the underlying layer while the shader uses the same relative coordinate. | [View range](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L454-L457) |

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
; Bound: 95
; Schema: 0
               OpCapability Shader
               OpCapability ImageQuery
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_WorkGroupID %gl_LocalInvocationIndex
               OpExecutionMode %main LocalSize 64 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %imageSize "imageSize"
               OpName %img "img"
               OpName %sizeOK "sizeOK"
               OpName %pixelCount "pixelCount"
               OpName %globalInvocationIndex "globalInvocationIndex"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %gl_LocalInvocationIndex "gl_LocalInvocationIndex"
               OpName %invRow "invRow"
               OpName %invCol "invCol"
               OpName %coords "coords"
               OpName %normCoords "normCoords"
               OpName %BufferBlock "BufferBlock"
               OpMemberName %BufferBlock 0 "values"
               OpName %ssbo "ssbo"
               OpDecorate %img Binding 0
               OpDecorate %img DescriptorSet 0
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %gl_LocalInvocationIndex BuiltIn LocalInvocationIndex
               OpDecorate %_runtimearr_v4uint ArrayStride 16
               OpDecorate %BufferBlock BufferBlock
               OpMemberDecorate %BufferBlock 0 Offset 0
               OpDecorate %ssbo Binding 1
               OpDecorate %ssbo DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Function_v3uint = OpTypePointer Function %v3uint
         %10 = OpTypeImage %uint 2D 0 1 0 2 R32ui
%_ptr_UniformConstant_10 = OpTypePointer UniformConstant %10
        %img = OpVariable %_ptr_UniformConstant_10 UniformConstant
        %int = OpTypeInt 32 1
      %v3int = OpTypeVector %int 3
       %bool = OpTypeBool
%_ptr_Function_bool = OpTypePointer Function %bool
    %uint_64 = OpConstant %uint 64
     %uint_1 = OpConstant %uint 1
         %24 = OpConstantComposite %v3uint %uint_64 %uint_64 %uint_1
     %v3bool = OpTypeVector %bool 3
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
%gl_LocalInvocationIndex = OpVariable %_ptr_Input_uint Input
%_ptr_Function_v3int = OpTypePointer Function %v3int
      %int_0 = OpConstant %int 0
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
  %float_0_5 = OpConstant %float 0.5
         %78 = OpConstantComposite %v3float %float_0_5 %float_0_5 %float_0_5
     %v4uint = OpTypeVector %uint 4
%_runtimearr_v4uint = OpTypeRuntimeArray %v4uint
%BufferBlock = OpTypeStruct %_runtimearr_v4uint
%_ptr_Uniform_BufferBlock = OpTypePointer Uniform %BufferBlock
       %ssbo = OpVariable %_ptr_Uniform_BufferBlock Uniform
%_ptr_Uniform_v4uint = OpTypePointer Uniform %v4uint
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_64 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
  %imageSize = OpVariable %_ptr_Function_v3uint Function
     %sizeOK = OpVariable %_ptr_Function_bool Function
 %pixelCount = OpVariable %_ptr_Function_uint Function
%globalInvocationIndex = OpVariable %_ptr_Function_uint Function
     %invRow = OpVariable %_ptr_Function_uint Function
     %invCol = OpVariable %_ptr_Function_uint Function
     %coords = OpVariable %_ptr_Function_v3int Function
 %normCoords = OpVariable %_ptr_Function_v3float Function
         %13 = OpLoad %10 %img
         %16 = OpImageQuerySize %v3int %13
         %17 = OpBitcast %v3uint %16
               OpStore %imageSize %17
         %21 = OpLoad %v3uint %imageSize
         %26 = OpIEqual %v3bool %21 %24
         %27 = OpAll %bool %26
               OpStore %sizeOK %27
         %31 = OpAccessChain %_ptr_Function_uint %imageSize %uint_0
         %32 = OpLoad %uint %31
         %33 = OpAccessChain %_ptr_Function_uint %imageSize %uint_1
         %34 = OpLoad %uint %33
         %35 = OpIMul %uint %32 %34
               OpStore %pixelCount %35
         %40 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %41 = OpLoad %uint %40
         %42 = OpIMul %uint %41 %uint_64
         %44 = OpLoad %uint %gl_LocalInvocationIndex
         %45 = OpIAdd %uint %42 %44
               OpStore %globalInvocationIndex %45
         %46 = OpLoad %bool %sizeOK
         %47 = OpLoad %uint %globalInvocationIndex
         %48 = OpLoad %uint %pixelCount
         %49 = OpULessThan %bool %47 %48
         %50 = OpLogicalAnd %bool %46 %49
               OpSelectionMerge %52 None
               OpBranchConditional %50 %51 %52
         %51 = OpLabel
         %54 = OpLoad %uint %globalInvocationIndex
         %55 = OpAccessChain %_ptr_Function_uint %imageSize %uint_0
         %56 = OpLoad %uint %55
         %57 = OpUDiv %uint %54 %56
               OpStore %invRow %57
         %59 = OpLoad %uint %globalInvocationIndex
         %60 = OpAccessChain %_ptr_Function_uint %imageSize %uint_0
         %61 = OpLoad %uint %60
         %62 = OpUMod %uint %59 %61
               OpStore %invCol %62
         %65 = OpLoad %uint %invCol
         %66 = OpBitcast %int %65
         %67 = OpLoad %uint %invRow
         %68 = OpBitcast %int %67
         %70 = OpCompositeConstruct %v3int %66 %68 %int_0
               OpStore %coords %70
         %75 = OpLoad %v3int %coords
         %76 = OpConvertSToF %v3float %75
         %79 = OpFAdd %v3float %76 %78
         %80 = OpLoad %v3uint %imageSize
         %81 = OpConvertUToF %v3float %80
         %82 = OpFDiv %v3float %79 %81
               OpStore %normCoords %82
         %88 = OpLoad %uint %globalInvocationIndex
         %89 = OpLoad %10 %img
         %90 = OpLoad %v3int %coords
         %91 = OpImageRead %v4uint %89 %90
         %93 = OpAccessChain %_ptr_Uniform_v4uint %ssbo %int_0 %88
               OpStore %93 %91
               OpBranch %52
         %52 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- CTS creates one optimally tiled, single-sample image and a single-layer view. Binding 0 holds either a combined image sampler or a storage image; binding 1 holds the expanded-vector storage buffer. Sampling uses nearest minification, magnification, and mip selection, repeat addressing, and a maximum LOD equal to the case's LOD. [Resources](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L436-L519); [Descriptor setup](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L592-L622).
- Two data representations connect host and shader: tightly packed pixels in the selected image format and four-component, 32-bit vectors in the storage buffer. CTS generates deterministic random values within each format's integer range or within `[0,1]` for floating-point access. Missing RGB channels use zero and missing alpha uses one. For stores, the vector buffer is input; for loads and sampling, the packed pixel buffer is input. CTS flushes the uploaded host allocation. [Value generators](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L404-L427); [Input preparation](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L521-L590).
- For loads and sampling, CTS transitions the selected view range from undefined to transfer-destination layout, copies the packed pixels into the selected mip and base layer, then makes transfer writes visible to compute shader reads. Sampling uses shader-read-only layout; storage access uses general layout. Store cases transition from undefined to general layout for shader writes without uploading image pixels. [Layout choice](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L184-L194); [Pre-dispatch synchronization](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L627-L661).
- One dispatch covers 4,096 texels with 64 workgroups of 64 invocations. Storage stores then transition the image for transfer reads and copy the selected mip/layer to the packed pixel buffer. A memory barrier exposes shader/transfer writes to host reads; CTS submits, waits, and invalidates the output allocation before reading it. [Dispatch and readback](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L662-L709).
- The host compares the packed-pixel texture with a texture view of the vector buffer. It treats the uploaded side as reference and the downloaded side as result. Signed and unsigned integer comparisons require exact equality in all four channels. Floating comparisons allow one UNORM quantization unit, `1 / (2^bits - 1)`, per present channel, or `0.0000002` for SFLOAT channels; absent channels have zero tolerance. The implementation uses these thresholds for both reads and writes, even though its comment motivates tolerance through stores. [Comparison implementation](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L711-L761).
- A failed comparison logs `Ints`, `Uints`, or `Floats` and reports `Unexpected results in output buffer; check log for details --`; otherwise CTS returns `Pass`. No separate host result identifies a size-query failure. [Final result](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L742-L769).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `view_type_1d` | Arrayed shader interpretation of a non-arrayed view; selected-subresource or value-transfer errors. |
| `view_type_1d_array` | Non-arrayed shader interpretation of an arrayed view; selected-subresource or value-transfer errors. |
| `view_type_2d` | Arrayed shader interpretation of a non-arrayed view; selected-subresource or value-transfer errors. |
| `view_type_2d_array` | Non-arrayed shader interpretation of an arrayed view; selected-subresource or value-transfer errors. |

### Cause Analysis

#### Arrayed shader interpretation of a non-arrayed view

**Possible failure symptoms:** A dimension or layer-count query that differs from the expected extent suppresses all payload accesses. Incorrect addressing can instead produce incorrect texels. Both paths reach the same host comparison failure; the log alone does not distinguish them. [Size guard and access](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L350-L401).

**Possible implementation causes:** Descriptor interpretation or shader image-operation handling may fail to treat the non-arrayed view as the shader's single-layer array. Check the queried components and relative layer-zero access before attributing the mismatch to format conversion. The source establishes these investigation points, not a unique driver or hardware cause.

#### Non-arrayed shader interpretation of an arrayed view

**Possible failure symptoms:** The size query may report the wrong spatial extent, or the result may contain values from the wrong texels. A view at base layer 1 can expose addressing mistakes even though the shader has no explicit layer component. The test reports the same output-buffer mismatch. [View selection](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L454-L457); [Comparison](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L742-L769).

**Possible implementation causes:** Descriptor interpretation or image-operation lowering may mishandle the removal of the array dimension while retaining the selected base layer. These are source-derived candidates; confirming one requires inspection of the failing implementation.

#### Selected-subresource or value-transfer errors

**Possible failure symptoms:** Sampling failures can depend on the selected LOD; storage failures can differ between loads and stores. Incorrect channel values, missing-channel defaults, or deviations beyond the format-dependent threshold fail the host comparison. [Access choice](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L328-L348); [Thresholds](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L723-L761).

**Possible implementation causes:** Investigate mip/base-layer selection, typed image access and conversion, descriptor binding, and the transfer/compute/host visibility path that produces the comparison inputs. CTS does not instrument these stages separately, so a mismatch cannot establish a specific implementation defect. [Setup and synchronization](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L592-L709).

The size guard is not a deterministic failure marker. For read cases, the zero-initialized CPU `vecBytes` vector is not uploaded to the output allocation; store cases do not initialize the destination image before shader execution. A failed size check therefore leaves an unwritten output rather than a defined sentinel. The comparison can expose the failure, but the page does not claim a guaranteed zero result or a dedicated size-error diagnosis. [Input initialization](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L532-L590); [Store transition](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L628-L638).

## Case Pruning

### Requirement-based pruning

- `checkSupport` requires `VK_KHR_maintenance11`. It queries image-format support for the selected format, image type, optimal tiling, and sampled/storage plus transfer usage. `VK_ERROR_FORMAT_NOT_SUPPORTED` skips the case; another non-success result fails it. [Support check](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L231-L247).
- The case skips if the creation extent exceeds the returned `maxExtent`, or `layer + 1` exceeds `maxArrayLayers`. This matters for higher sampled LODs because CTS enlarges the base image to keep the tested mip extent fixed. [Limit checks](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L249-L267).
- These are the explicit local checks. The format-support query passes image-create flags `0`, while image creation later sets `VK_IMAGE_CREATE_ALIAS_SINGLE_LAYER_DESCRIPTOR_BIT_KHR`. The local support function does not separately test `maxMipLevels` or a storage-image extended-format feature. Do not read the format query as a check of the exact flagged image-creation configuration. [Query arguments](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L239-L241); [Creation flags](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L436-L447).
- The parent excludes the family from Vulkan SC registration with `#ifndef CTS_USES_VULKANSC`; this is a build-time boundary, not a runtime skip. [Registration guard](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L62-L75).

### Design-based pruning

- Only 1D and 2D image/view pairs with matching spatial dimensionality are registered. There are no 3D, cube, multisample, or depth/stencil cases in this family. [Registered formats and types](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L780-L846).
- Storage-image cases keep LOD zero. Sampling cases never set `store`; each base layer instead gets LODs 0, 1, and 2. [Generator exclusions](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L853-L864).
- Every view exposes one layer and every shader deliberately disagrees with the view's arrayedness. The family does not include a matched-type control case, a multi-visible-layer view, or nonzero relative array coordinates for storage access. [Mismatch selection](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L277-L288); [Coordinates](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L309-L326); [View range](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L454-L457).

## Key Takeaways

- A view's arrayedness and the shader image type's arrayedness deliberately disagree in both directions; the descriptor still exposes one selected layer.
- Base layer and LOD are separate parameters. In `sampler_lod_12`, layer 1 and mip 2 select the subresource while the tested mip size stays fixed.
- The shader uses the queried size to guard data access, and the host checks the resulting payload. The output-buffer failure does not by itself identify a query, addressing, conversion, or visibility defect; see `Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent `createChildren` | [Registration](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L62-L75) | Family routing and Vulkan SC exclusion. |
| `createImageArrayMaintenance11Tests` | [Factory](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L776-L890) | Complete matrix, pruning, and exact leaf spelling. |
| `TestParams` | [Parameter helpers](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L95-L194) | Seed, usage, extents, counts, and shader layouts. |
| `ImageArrayCase::checkSupport` | [Support gates](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L231-L267) | Extension requirement, format query, and explicit limits. |
| `ImageArrayCase::initPrograms` | [Shader builder](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L270-L402) | Mismatched types, query components, coordinates, and access instructions. |
| `ImageArrayInstance::iterate` | [Runtime](../../../modules/vulkan/binding_model/vktBindingImageArrayMaintenance11Tests.cpp#L430-L769) | Image flag, upload/copyback, synchronization, thresholds, and failure result. |
| Default shader target | [Baseline SPIR-V](../../../framework/vulkan/vkPrograms.cpp#L1049-L1052) | Builder has no explicit build options; walkthrough uses baseline SPIR-V 1.0. |
| Mustpass coverage | [Vulkan cases](../../../mustpass/main/vk-default/binding-model.txt#L48435-L49514); [SC list](../../../mustpass/main/vksc-default/binding-model.txt) | Enumerated Vulkan coverage and absent SC family. |
