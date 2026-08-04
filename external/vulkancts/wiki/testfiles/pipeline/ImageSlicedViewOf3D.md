## Overview

**Core question:** Does a sliced 3D storage-image view expose exactly the requested parent-image slices at the requested mip level?

- [`vktPipelineImageSlicedViewOf3DTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L71-L1223) implements the `pipeline` test category's `sliced_view_of_3d_image` test family.
- It uses `VK_EXT_image_sliced_view_of_3d` to restrict a `VK_IMAGE_VIEW_TYPE_3D` view to a Z offset and slice count, then tests storage-image reads and writes in compute and fragment pipelines.
- The four intermediate nodes vary simple one-slice views, full-depth views, deterministic pseudorandom ranges, and nonzero mip levels. The monolithic mustpass contains 156 leaves: 16 `basic`, 8 `full_slice`, 100 `random`, and 32 `mip_level`.
- This page explains the parameters, generated shaders, host execution, exact comparisons, and what a failure can localize.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A `VkImageViewSlicedCreateInfoEXT` chained to image-view creation supplies a Z `sliceOffset` and `sliceCount`. In a storage-image shader, view coordinate Z 0 accesses the parent image at `sliceOffset`; the accessible Z range ends at `sliceCount - 1`. The view covers exactly one mip level. See [the Vulkan resource rules](../../../../vulkan-docs/src/chapters/resources.adoc#_vk_image_view_sliced_create_info_ext).
- `VK_REMAINING_3D_SLICES_EXT` selects all slices after the offset. The effective count depends on the depth of the selected mip level, not on the base-level depth.
- The `imageSlicedViewOf3D` feature authorizes use of such a view through a `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE` descriptor. Other descriptor types ignore the slicing create info, which explains why the optional sampling path checks ordinary full-level sampling separately. See [the feature description](../../../../vulkan-docs/src/chapters/features.adoc#_vk_physical_device_image_sliced_view_of_3d_features_ext) and [the descriptor-specific rule](../../../../vulkan-docs/src/chapters/resources.adoc#_vk_image_view_sliced_create_info_ext).

## Registration Hierarchy

```text
pipeline.monolithic.sliced_view_of_3d_image
├── basic
├── full_slice
├── random
└── mip_level
```

[`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L202-L209) registers this test family only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`. Its factory registers the four intermediate nodes and their leaves in [`createImageSlicedViewOf3DTests()`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L978-L1223). The relevant mustpass scope is [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Operation | `load`, `store` | Chooses whether the sliced view is the shader input or output. | [`TestType`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L67-L70), [shader generation](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L289-L313) |
| Shader stage | `comp`, `frag` | Runs the same storage-image operation through a compute dispatch or an instanced full-screen draw. | [stage registration](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L983-L987), [pipeline execution](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L559-L610) |
| Intermediate node | `basic`, `full_slice`, `random`, `mip_level` | Selects the range and mip-level population. | [factory](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1013-L1221) |
| Parent depth and offset | `basic`: depth 2, offsets 0/1; `full_slice`: depth 4, offset 0; `random`: depths 10 through 32; `mip_level`: base depth 8 | Places the selected view range in the parent image. | [basic/full registration](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1013-L1073), [random/mip registration](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1075-L1221) |
| Slice range | explicit count or `VK_REMAINING_3D_SLICES_EXT` | Defines the view depth. The parameter helper derives the actual count for the sentinel. | [`TestParams::getActualRange`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L129-L146) |
| Mip level | base level for the first three nodes; levels 0 through 3 in `mip_level` | Changes the effective parent-image depth and the coordinate extent. | [mip registration](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1146-L1218) |
| Sampling follow-up | absent or `_with_sampling` in `basic` and `full_slice` | Adds a full-level combined-sampler comparison after the storage-image operation. | [sampling registration](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L994-L998), [sampling execution](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L613-L739) |

The deterministic random generator starts from seed `1667817299u`. For each operation-stage combination, it attempts five depth selections and five offset/range cases per selected depth, then removes duplicate `(depth, offset, range)` tuples before registering leaves. The current mustpass contains 25 `random` leaves for each of the four operation-stage combinations; duplicate depth selections mean a combination can contain fewer than five distinct depths. The `mip_level` node generates two distinct offset/range cases at each of the four levels.

## Behavior Parameters

The primary behavior parameter is the operation: `load` and `store` reverse the data path across the sliced storage-image view. The intermediate nodes, stage, and range dimensions exercise that operation under different view shapes.

### load: Read through the sliced view

The host copies reference pixels into the selected region of the full 3D image. The shader reads `slicedImage` and writes the pixels into a reduced-depth auxiliary image. The host copies that auxiliary image to a verification buffer and compares it with the original reference buffer. [`SlicedViewLoadTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L742-L857) implements this direction.

### store: Write through the sliced view

The host fills the reduced-depth auxiliary image from the reference buffer. The shader reads that image and writes into `slicedImage`. The host copies the selected region from the full 3D image to a verification buffer and compares it with the reference buffer. [`SlicedViewStoreTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L859-L972) implements this direction.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.sliced_view_of_3d_image.basic.load.comp.offset_1
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `basic.load` | The full image has depth 2; the test reads one selected slice through the view. |
| `comp` | A compute dispatch runs one workgroup for the view's only slice. |
| `offset_1` | View Z coordinate 0 must access parent-image slice 1. |

#### Purpose

This generated compute shader reads pixels from a one-slice storage-image view and copies them to an equally sized auxiliary image. It also converts a wrong reported view depth into zeros, making `imageSize(slicedImage).z` part of the observable result.

#### Structural Design

| Phase | Shader action | Observable consequence |
|---|---|---|
| Coordinate formation | Combines the local XY invocation ID with `gl_WorkGroupID.x` as Z. | Each invocation addresses one pixel in the sliced view. |
| View query and load | Reads `imageSize(slicedImage)` and `imageLoad(slicedImage, coords)`. | Exercises the sliced storage-image descriptor's depth and address translation. |
| Guarded store | Stores the loaded color only when the reported Z size is 1. | A wrong effective range produces zero pixels in the result. |

#### Shader Code

```glsl
#version 460
/// One 8x8 workgroup covers the single selected slice in this representative case.
layout (local_size_x=8, local_size_y=8, local_size_z=1) in;
/// Binding 0 is the sliced `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE` view.
layout (rgba8ui, set=0, binding=0) uniform uimage3D slicedImage;
/// Binding 1 receives the value read through the sliced view.
layout (rgba8ui, set=0, binding=1) uniform uimage3D auxiliarImage;
void main (void) {
    /// Z is relative to the view, so Z 0 must map to parent slice 1.
    const ivec3 coords = ivec3(ivec2(gl_LocalInvocationID.xy), int(gl_WorkGroupID.x));
    const ivec3 size = imageSize(slicedImage);
    const uvec4 badColor = uvec4(0, 0, 0, 0);
    const uvec4 goodColor = imageLoad(slicedImage, coords);
    const uvec4 storedColor = ((size.z == 1) ? goodColor : badColor);
    imageStore(auxiliarImage, coords, storedColor);
}
```

#### Additional Info

- [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L283-L357) derives this shader from `TestParams`; `offset` configures the image view rather than appearing in the shader source.
- Fragment cases use the same main operation. Their vertex shader supplies an instance-derived Z coordinate and the graphics path draws one full-screen triangle per selected slice.
- `store` swaps `slicedImage` and `auxiliarImage` in the generated `imageLoad` and `imageStore` expressions.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Operation | `load` reads `slicedImage` and writes `auxiliarImage`; `store` reverses those roles. | [operation selection](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L289-L313) |
| Stage | `comp` derives coordinates from local and workgroup IDs; `frag` derives them from fragment coordinates and an instance-provided Z input. | [stage generation](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L315-L357) |
| Effective range | The generated depth literal in the `imageSize` guard changes with `getActualRange()`. | [range helper](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L129-L146), [guard generation](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L307-L313) |

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
; Bound: 60
; Schema: 0
               OpCapability Shader
               OpCapability ImageQuery
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_LocalInvocationID %gl_WorkGroupID
               OpExecutionMode %main LocalSize 8 8 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %coords "coords"
               OpName %gl_LocalInvocationID "gl_LocalInvocationID"
               OpName %gl_WorkGroupID "gl_WorkGroupID"
               OpName %size "size"
               OpName %slicedImage "slicedImage"
               OpName %goodColor "goodColor"
               OpName %storedColor "storedColor"
               OpName %auxiliarImage "auxiliarImage"
               OpDecorate %gl_LocalInvocationID BuiltIn LocalInvocationId
               OpDecorate %gl_WorkGroupID BuiltIn WorkgroupId
               OpDecorate %slicedImage Binding 0
               OpDecorate %slicedImage DescriptorSet 0
               OpDecorate %auxiliarImage Binding 1
               OpDecorate %auxiliarImage DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v3int = OpTypeVector %int 3
%_ptr_Function_v3int = OpTypePointer Function %v3int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_LocalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
%gl_WorkGroupID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
         %29 = OpTypeImage %uint 3D 0 0 0 2 Rgba8ui
%_ptr_UniformConstant_29 = OpTypePointer UniformConstant %29
%slicedImage = OpVariable %_ptr_UniformConstant_29 UniformConstant
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
     %uint_2 = OpConstant %uint 2
%_ptr_Function_int = OpTypePointer Function %int
      %int_1 = OpConstant %int 1
       %bool = OpTypeBool
         %49 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
     %v4bool = OpTypeVector %bool 4
%auxiliarImage = OpVariable %_ptr_UniformConstant_29 UniformConstant
     %uint_8 = OpConstant %uint 8
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_8 %uint_8 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
     %coords = OpVariable %_ptr_Function_v3int Function
       %size = OpVariable %_ptr_Function_v3int Function
  %goodColor = OpVariable %_ptr_Function_v4uint Function
%storedColor = OpVariable %_ptr_Function_v4uint Function
         %15 = OpLoad %v3uint %gl_LocalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %18 = OpBitcast %v2int %16
         %22 = OpAccessChain %_ptr_Input_uint %gl_WorkGroupID %uint_0
         %23 = OpLoad %uint %22
         %24 = OpBitcast %int %23
         %25 = OpCompositeExtract %int %18 0
         %26 = OpCompositeExtract %int %18 1
         %27 = OpCompositeConstruct %v3int %25 %26 %24
               OpStore %coords %27
         %32 = OpLoad %29 %slicedImage
         %33 = OpImageQuerySize %v3int %32
               OpStore %size %33
         %37 = OpLoad %29 %slicedImage
         %38 = OpLoad %v3int %coords
         %39 = OpImageRead %v4uint %37 %38
               OpStore %goodColor %39
         %43 = OpAccessChain %_ptr_Function_int %size %uint_2
         %44 = OpLoad %int %43
         %47 = OpIEqual %bool %44 %int_1
         %48 = OpLoad %v4uint %goodColor
         %51 = OpCompositeConstruct %v4bool %47 %47 %47 %47
         %52 = OpSelect %v4uint %51 %48 %49
               OpStore %storedColor %52
         %54 = OpLoad %29 %auxiliarImage
         %55 = OpLoad %v3int %coords
         %56 = OpLoad %v4uint %storedColor
               OpImageWrite %54 %55 %56
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each case requires `VK_EXT_image_sliced_view_of_3d`; fragment cases also require `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS`. [`checkSupport`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L273-L280) performs these checks.
- The load and store instances allocate the full image, a reduced-depth auxiliary image, a filled reference buffer, and a verification buffer. They clear the full image and use barriers to move copy data into shader access and shader results into transfer and host access. See [load setup](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L742-L828) and [store setup](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L859-L925).
- `make3DImageView` receives the offset and requested range through its sliced-view argument. The descriptor layout binds both views as `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE`; the runtime chooses a graphics draw or compute dispatch based on the stage. [View construction](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L804-L818), [descriptor setup](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L532-L568), and [stage dispatch](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L570-L610) establish that path.
- After queue completion, the host invalidates the readback allocation and compares reference and result with `tcu::intThresholdCompare` using a zero `UVec4` threshold. The optional sampling run reads the complete selected level via a combined sampler, copies both sampled and direct parent-image data, and makes the same exact comparison. [Load comparison](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L835-L857), [store comparison](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L950-L972), and [sampling check](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L613-L739) show the checks.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `load` | The sliced storage-image view may expose the wrong parent-image slices, mip level, or effective depth when shaders read it. |
| `store` | Writes through the sliced storage-image view may land in the wrong parent-image slices or mip level, or may not update the selected region. |
| Either family | Descriptor, image-layout, synchronization, copyback, or host-comparison handling may prevent the expected data from reaching the comparison. |

### Cause Analysis

#### Sliced storage-image address or extent handling

**Possible failure symptoms:** A `load` result differs from the reference buffer, or the shader writes zero because `imageSize(slicedImage).z` differs from the effective range. The symptom can appear for one offset, remaining-slice range, or mip level while simpler cases pass.

**Possible implementation causes:** The Vulkan contract maps view-relative Z 0 to `sliceOffset` and makes `sliceCount` the accessible depth for storage-image access. An implementation can therefore fail by applying the offset or count incorrectly, by using base-level rather than selected-mip depth for a remaining range, or by reporting an incorrect storage-image extent. Source-level investigation is needed to distinguish descriptor-view construction, shader compiler lowering, and device image-address handling.

#### Sliced storage-image write handling

**Possible failure symptoms:** A `store` result differs only in the selected parent-image region, or the copied region remains clear while the source auxiliary image contains the expected values.

**Possible implementation causes:** The store path uses the same sliced-view coordinate translation as load but writes into the parent image. Incorrect view-relative Z translation, mip selection, or storage-image write routing can place data in a different slice or leave the selected region unchanged. The test's final image cannot by itself distinguish those mechanisms.

#### Data-transfer and result-visibility path

**Possible failure symptoms:** Either operation fails exact comparison, including across many offsets and stages, even if the shader-side operation is correct. Optional sampling can also fail independently after a successful storage-image comparison.

**Possible implementation causes:** The CTS explicitly transitions images, inserts shader-to-transfer and transfer-to-host barriers, submits, waits, invalidates host allocations, and then compares. A fault in descriptor binding, layout transition, barrier visibility, copy, or host memory invalidation could produce the same observed mismatch. The source provides the operation sequence, but the failing output alone does not isolate a particular layer.

## Case Pruning

### Requirement-based pruning

The test case skips when `VK_EXT_image_sliced_view_of_3d` is unavailable. Fragment leaves also skip without `DEVICE_CORE_FEATURE_FRAGMENT_STORES_AND_ATOMICS`. The parameter constructor rejects an offset outside the selected mip depth and rejects explicit ranges that extend beyond that depth; these mirror the view-validity constraints. See [support checks](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L273-L280), [parameter assertions](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L97-L122), and [Vulkan valid usage](../../../../vulkan-docs/src/chapters/resources.adoc#_vk_image_view_sliced_create_info_ext).

### Design-based pruning

`basic` fixes the range to one and covers each slice in a depth-2 image. `full_slice` fixes offset 0 and covers depth 4. The random and mip generators retain distinct tuples, preventing duplicate leaves. Sampling appears only in `basic` and `full_slice`, where the compact populations add an ordinary sampled-view comparison without multiplying the large random and mip matrices.

## Key Takeaways

- The test family verifies both storage-image reads and writes through views whose Z coordinates are relative to a selected parent-image slice range.
- The shader's `imageSize` guard makes the effective slice count observable, including when `VK_REMAINING_3D_SLICES_EXT` depends on the selected mip level.
- Compute and fragment leaves use different invocation generation but exercise the same storage-image view semantics.
- Exact host comparison checks the selected region; optional sampling separately confirms the full selected level through a descriptor type for which slicing is ignored.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Parameter and range helpers | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L71-L188) | Converts ranges and mip levels into actual slice extents. |
| Feature gate and generated shaders | [`SlicedViewTestCase::checkSupport` and `initPrograms`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L273-L378) | Defines requirements and shader-visible behavior. |
| Descriptor and pipeline execution | [`SlicedViewTestInstance::runPipeline`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L532-L610) | Binds storage images and executes the selected stage. |
| Optional sampling verification | [`SlicedViewTestInstance::runSamplingPipeline`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L613-L739) | Shows the separate combined-sampler check. |
| Load and store lifecycles | [`SlicedViewLoadTestInstance::iterate` and `SlicedViewStoreTestInstance::iterate`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L742-L972) | Shows initialization, synchronization, readback, and exact comparison. |
| Test-family registration | [`createImageSlicedViewOf3DTests`](../../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L978-L1223) | Registers the intermediate nodes and test case leaves. |
| Parent registration | [`createChildren`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L202-L209) | Restricts the family to monolithic construction. |
| Vulkan view contract | [`VkImageViewSlicedCreateInfoEXT`](../../../../vulkan-docs/src/chapters/resources.adoc#_vk_image_view_sliced_create_info_ext) | Defines slice offsets, counts, mip restriction, and descriptor behavior. |
