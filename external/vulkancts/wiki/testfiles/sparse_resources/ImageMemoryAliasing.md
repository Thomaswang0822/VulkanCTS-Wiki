## Overview

**Core question:** Can two sparse images alias the same resident image blocks while one image supplies input data and the other receives shader output?

- [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1-L22) implements the regular `sparse_resources.image_sparse_memory_aliasing` family and the device-group `sparse_resources.device_group_image_sparse_memory_aliasing` family.
- Both families cover 2D, 2D-array, cube, cube-array, and 3D images. The device-group family uses the same image-type matrix with device-group sparse-bind and submission metadata.
- Each case creates a read image and a write image. The images share the sparse residency-block memory binds, while their mip-tail allocations remain separate where the implementation requires it.
- The test copies reference data into the read image, dispatches compute shaders through the aliased write image, copies the read image back, and checks both the shader-written regions and the preserved reference regions.

## Background Knowledge

- Sparse binding lets an image reserve virtual address space while the application supplies memory for individual image blocks, mip tails, and metadata regions.
- Memory aliasing makes two resources refer to the same physical allocation. Writes through one resource can therefore be observed through another resource when the bindings and synchronization are correct.
- A sparse image can expose separate residency blocks and mip-tail requirements. This test aliases the ordinary residency blocks but tracks the read and write mip tails separately.
- Multi-planar formats may need plane-compatible storage-image views and copy regions. Cube and array images represent their layers through the image subresource layout; 3D images use depth instead.

## Registration Hierarchy

```text
sparse_resources.image_sparse_memory_aliasing
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

The source registers the same five direct children under `sparse_resources.device_group_image_sparse_memory_aliasing`. Beneath each image-type group, registration expands through supported formats and the image sizes listed by the source.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `image_sparse_memory_aliasing`, `device_group_image_sparse_memory_aliasing` | Selects regular sparse binding or device-group sparse-bind and submission behavior. | [`createImageMemoryAliasingTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1094-L1104) |
| Image type | `2d`, `2d_array`, `cube`, `cube_array`, `3d` | Selects image dimensionality and layer or depth interpretation. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1060) |
| Image sizes | Four source-defined sizes per image type (for example, `512x256x1` for 2D, `512x256x6` for 2D-array, `256x256x1` for cube, and `256x256x16` for 3D) | Varies sparse-block counts, array layers, or 3D depth. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1054) |
| Format | Values from `getTestFormats(imageType)` | Changes channel representation, plane layout, alignment, and storage-image requirements. | [`getTestFormats`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) |
| Device-group mode | `false` or `true` | Adds device-group information to sparse binds and submissions; it does not add image-type children. | [`createImageMemoryAliasingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1091) |

The generator skips an image size when its dimensions fail the selected format's alignment requirements. This matters for formats, such as some YCbCr formats, whose valid image extents impose additional constraints. [`createImageMemoryAliasingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1064-L1084)

## Behavior Parameters

The primary behavior choice is the registered image type. Format and extent select the concrete sparse image configuration within each family.

### `2d` : two-dimensional sparse image aliasing

The case creates two `VK_IMAGE_TYPE_2D` images with sparse binding, sparse residency, and sparse aliasing enabled. Both images use the same regular image-residency binds. The source registers four extents for each supported format. [`ImageMemoryAliasingInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L217-L245)

### `2d_array` : two-dimensional array image aliasing

The third extent component represents array layers. Copy regions and shader views use `getNumLayers()`, so validation covers every layer in the selected array configuration. [`ImageMemoryAliasingInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L223-L224), [`copyImageToBuffer`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L531-L540)

### `cube` : cube image aliasing

The source adds `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` for cube images. The shared layer mapping handles the six cube faces while the two images continue to share their regular sparse residency binds. [`ImageMemoryAliasingInstance`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L234-L235)

### `cube_array` : cube-array image aliasing

Cube-array cases use cube-compatible creation and the shared array-layer handling. The same aliasing and readback checks apply to every selected face and array layer.

### `3d` : three-dimensional sparse image aliasing

The third extent component represents depth. The compute dispatch derives its grid from `getShaderGridSize()` and rejects configurations that exceed the device's workgroup limits before issuing `cmdDispatch`. [`ImageMemoryAliasingInstance::dispatchShader`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L734-L759)

## Shader Analysis

The representative shader is the generated compute program for [`dEQP-VK.sparse_resources.image_sparse_memory_aliasing.2d.r32ui.512_256_1`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1038-L1084). `ImageSparseMemoryAliasingCase::initPrograms` emits one program for each plane and mip level; this single-plane, level-0 `R32_UINT` instance exposes the core aliasing write and its bounds guards. The program is generated from GLSL 4.40 and uses the default CTS source-collection target, SPIR-V 1.0.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.sparse_resources.image_sparse_memory_aliasing.2d.r32ui.512_256_1
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `2d` | Selects `VK_IMAGE_TYPE_2D`, `image2D`, a two-component integer coordinate, and one depth slice. |
| `r32ui` | Selects the unsigned integer `r32ui` storage-image qualifier, `uimage2D`, `uvec4` store data, and exact integer verification. |
| `512_256_1` | Selects a 512 x 256 x 1 level-0 grid. The generator derives a 128 x 1 x 1 local size and dispatches enough groups to cover the grid. |
| level 0, plane 0 | Selects the first generated program (`comp0_0`) with no multi-planar divisor adjustment and the full 512 x 256 extent. |

#### Purpose

Each in-range compute invocation writes a deterministic `uvec4` value to the write image. The host binds that image as the aliased write view while the read image is later copied back, so the shader store is the observable payload of the sparse-image aliasing test.

#### Structural Design

| Phase | Generated operation | Why it matters |
|---|---|---|
| Bounds | Compare `gl_GlobalInvocationID.x/y/z` with `512/256/1`. | Extra invocations from the dispatch do not write outside the selected image extent. |
| Linear index | Compute `logicalX + 512 * logicalY + 131072 * logicalZ`. | Gives every logical texel a deterministic value independent of execution order. |
| Value construction | Use `index % 127` for RGB and `1` for alpha. | Produces a format-compatible unsigned payload that the host can predict exactly. |
| Aliased store | `imageStore(u_image, ivec2(gl_GlobalInvocationID.xy), ...)`. | Writes the storage image whose physical residency blocks are shared with the read image. |

#### Shader Code

```glsl
#version 440

/// One invocation addresses one logical texel in the selected 512 x 256 x 1 level-0 image.
layout (local_size_x = 128, local_size_y = 1, local_size_z = 1) in;
/// Binding 0 is the write-side storage image. The host binds the corresponding sparse image view here;
/// its ordinary residency blocks alias the read image's blocks, while mip-tail allocations stay separate.
layout (binding = 0, r32ui) writeonly uniform highp uimage2D u_image;

void main (void)
{
    /// The nested guards match the generated plane extent and make the dispatch safe when rounded up to workgroups.
    if( gl_GlobalInvocationID.x < 512 )
    if( gl_GlobalInvocationID.y < 256 )
    if( gl_GlobalInvocationID.z < 1 )
    {
        /// For this single-plane case the logical coordinates equal the invocation coordinates.
        int logicalX = int(gl_GlobalInvocationID.x) * 1;
        int logicalY = int(gl_GlobalInvocationID.y) * 1;
        /// Flatten x/y/z using the full level-0 grid dimensions; the modulus keeps the payload bounded.
        int index = logicalX + 512 * logicalY + 512 * 256 * int(gl_GlobalInvocationID.z);
        /// The uvec4 type and r32ui qualifier are selected from VK_FORMAT_R32_UINT by the source helpers.
        imageStore(u_image, ivec2(gl_GlobalInvocationID.x,gl_GlobalInvocationID.y), uvec4(index % 127, index % 127, index % 127, 1));
    }
}
```

#### Additional Info

- The generator names this module `comp0_0`; other mip levels and planes receive separate modules with their own derived grid, local size, coordinate type, and format data type ([`initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L932-L1022)).
- The selected case uses `glu::GLSL_VERSION_440`; no explicit `vk::ShaderBuildOptions` target is supplied, so the source-collection baseline is SPIR-V 1.0 ([GLSL version selection](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1080-L1084)).
- The shader writes only the ordinary residency-block region that is later checked against `index % 127`; host verification separately compares mip-tail bytes against the original reference data ([verification](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L772-L929)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Image type | Changes `image2D` and `ivec2` to array, cube, cube-array, or 3D image types and changes the coordinate's z/layer interpretation. | [`getCoordStr`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L68-L91), [`getShaderGridSize`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L120-L155) |
| Format | Changes the storage-image qualifier, image object type signedness/width, store data type, and host comparison class. Multi-planar formats additionally select a plane-compatible view and divide x/y plane extents. | [`initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L943-L980), [`getShaderImageType`/`getShaderImageDataType`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L466-L602), [`verify`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L856-L907) |
| Image extent | Changes the literal bounds, flattening strides, derived plane extent, local workgroup sizes, and dispatch grid. | [`initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L975-L1017), [`dispatchShader`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L734-L759) |
| Mip level | Generates a separate `comp<plane>_<mip>` module with mip-shrunk grid dimensions and a corresponding image view/dispatch. | [`initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L975-L1021) |
| Device-group mode | Reuses the same shader text; the variation is in sparse-bind and submission device metadata rather than shader declarations or control flow. | [`createImageSparseMemoryAliasingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1104), [`bindSparseImages`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L347-L492) |

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
; Bound: 83
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 128 1 1
               OpSource GLSL 440
               OpName %main "main"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %logicalX "logicalX"
               OpName %logicalY "logicalY"
               OpName %index "index"
               OpName %u_image "u_image"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_image NonReadable
               OpDecorate %u_image Binding 0
               OpDecorate %u_image DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
   %uint_512 = OpConstant %uint 512
       %bool = OpTypeBool
     %uint_1 = OpConstant %uint 1
   %uint_256 = OpConstant %uint 256
     %uint_2 = OpConstant %uint 2
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_1 = OpConstant %int 1
    %int_512 = OpConstant %int 512
 %int_131072 = OpConstant %int 131072
         %57 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_57 = OpTypePointer UniformConstant %57
    %u_image = OpVariable %_ptr_UniformConstant_57 UniformConstant
      %v2int = OpTypeVector %int 2
    %int_127 = OpConstant %int 127
     %v4uint = OpTypeVector %uint 4
   %uint_128 = OpConstant %uint 128
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_128 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
   %logicalX = OpVariable %_ptr_Function_int Function
   %logicalY = OpVariable %_ptr_Function_int Function
      %index = OpVariable %_ptr_Function_int Function
         %12 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %13 = OpLoad %uint %12
         %16 = OpULessThan %bool %13 %uint_512
               OpSelectionMerge %18 None
               OpBranchConditional %16 %17 %18
         %17 = OpLabel
         %20 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %21 = OpLoad %uint %20
         %23 = OpULessThan %bool %21 %uint_256
               OpSelectionMerge %25 None
               OpBranchConditional %23 %24 %25
         %24 = OpLabel
         %27 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %28 = OpLoad %uint %27
         %29 = OpULessThan %bool %28 %uint_1
               OpSelectionMerge %31 None
               OpBranchConditional %29 %30 %31
         %30 = OpLabel
         %35 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %36 = OpLoad %uint %35
         %37 = OpBitcast %int %36
         %39 = OpIMul %int %37 %int_1
               OpStore %logicalX %39
         %41 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %42 = OpLoad %uint %41
         %43 = OpBitcast %int %42
         %44 = OpIMul %int %43 %int_1
               OpStore %logicalY %44
         %46 = OpLoad %int %logicalX
         %48 = OpLoad %int %logicalY
         %49 = OpIMul %int %int_512 %48
         %50 = OpIAdd %int %46 %49
         %52 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %53 = OpLoad %uint %52
         %54 = OpBitcast %int %53
         %55 = OpIMul %int %int_131072 %54
         %56 = OpIAdd %int %50 %55
               OpStore %index %56
         %60 = OpLoad %57 %u_image
         %61 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %62 = OpLoad %uint %61
         %63 = OpBitcast %int %62
         %64 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %65 = OpLoad %uint %64
         %66 = OpBitcast %int %65
         %68 = OpCompositeConstruct %v2int %63 %66
         %69 = OpLoad %int %index
         %71 = OpSMod %int %69 %int_127
         %72 = OpBitcast %uint %71
         %73 = OpLoad %int %index
         %74 = OpSMod %int %73 %int_127
         %75 = OpBitcast %uint %74
         %76 = OpLoad %int %index
         %77 = OpSMod %int %76 %int_127
         %78 = OpBitcast %uint %77
         %80 = OpCompositeConstruct %v4uint %72 %75 %78 %uint_1
               OpImageWrite %60 %68 %80
               OpBranch %31
         %31 = OpLabel
               OpBranch %25
         %25 = OpLabel
               OpBranch %18
         %18 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` requires aliased sparse residency, a supported image size and image type, and the relevant sparse image format properties. R64 formats additionally require `VK_EXT_shader_image_atomic_int64`, `shaderImageInt64Atomics`, and `sparseImageInt64Atomics`. [`ImageMemoryAliasingCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L125-L154)
- The instance checks storage-image support, storage-compatible plane formats, `sparseAddressSpaceSize`, memory-type compatibility, and peer-memory capabilities for cross-device cases. [`ImageMemoryAliasingInstance::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L247-L340)
- It creates the read and write images with `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, `VK_IMAGE_CREATE_SPARSE_ALIASED_BIT`, and `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`. Cube-compatible images also receive the cube-compatible flag.
- The sparse bind gives both images identical regular residency binds. The instance keeps the mip-tail memory for the read and write images separate, then submits the bind with the required device-group metadata when `useDeviceGroup` is enabled. [`bindSparseImages`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L347-L492)
- A deterministic input buffer is copied into the read image. Compute dispatches write the aliased write image, after which the read image is copied back to a host-visible buffer. [`ImageMemoryAliasingInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L564-L759)
- The host checks shader-written sparse blocks against generated values and checks the remaining mip-tail or reference data against the original input. [`ImageMemoryAliasingInstance::verify`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L772-L929)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `2d` | Incorrect sparse aliasing, image layout transition, shader store, or transfer handling for a 2D image. |
| `2d_array` | Incorrect array-layer addressing or sparse binding for one or more layers. |
| `cube` | Incorrect cube-compatible setup, face mapping, sparse binding, or readback. |
| `cube_array` | Incorrect cube-face or array-layer mapping in the aliased access path. |
| `3d` | Incorrect depth handling, dispatch grid, sparse binding, or 3D image copy. |
| Any format | Unsupported storage-image or plane format handling, incorrect format-aware comparison, or an R64 feature mismatch. |
| Any device-group case | The regular path or its device-group bind, peer-memory selection, or device-targeted submission fails. |

### Cause Analysis

#### Shared residency binds do not alias as expected

**Possible failure symptoms:** Shader-written values are missing from the readback, or the returned data still contains the input pattern in blocks that the shader should have overwritten.

**Possible implementation causes:** The two images may not receive identical regular sparse binds, the implementation may resolve an alias to different physical memory, or a sparse bind may use the wrong offset, extent, aspect, or mip level. The failing format and sparse-bind record are needed to isolate the mapping error.

#### Synchronization or layout transition error

**Possible failure symptoms:** Results vary between runs, or the copied image contains stale data even though both images report compatible bindings.

**Possible implementation causes:** The sparse bind signal, image barriers, compute dispatch, or image-to-buffer copy may execute out of order. The source explicitly sequences these operations; the failing synchronization point requires investigation with the test log and command trace.

#### Mip-tail or plane data is corrupted

**Possible failure symptoms:** Shader-written blocks compare correctly, but mip-tail bytes or one plane differs from the original reference.

**Possible implementation causes:** The implementation may apply the shared residency binds to a mip-tail region that should use its own allocation, calculate plane offsets incorrectly, or mishandle a storage-compatible plane format during copyback.

#### Device-group targeting error

**Possible failure symptoms:** A failure occurs only under `device_group_image_sparse_memory_aliasing` or only for a particular physical-device pair.

**Possible implementation causes:** The sparse-bind device indices, peer-memory mapping, or command submission target may not match the selected resource and memory devices. The failing device pair and bind metadata are needed for attribution.

## Case Pruning

### Requirement-based pruning

Cases are skipped when the selected extent exceeds image limits, the image type lacks sparse support, the format lacks the required sparse properties, or storage-image support is unavailable. The runtime also checks sparse address-space size, compatible memory types, and peer-memory copy or generic-destination features for cross-device cases. R64 formats require the extension and both 64-bit shader-image atomic features described above. [`checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L125-L154), [`checkSparseSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L247-L340)

### Design-based pruning

The registration keeps one image-type matrix for regular and device-group roots and passes `useDeviceGroup` into the common builder. Format-alignment checks remove invalid extents, while device-group mode changes bind and submission metadata rather than the direct-child hierarchy. [`createImageMemoryAliasingTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1104)

## Key Takeaways

- The defining check is physical-memory aliasing: both images share regular sparse image binds, then one image is written through compute while the other is read back.
- Mip tails remain separately managed where the source requires distinct read and write allocations, so the test checks aliasing without conflating it with tail binding.
- The same contract runs across 2D, array, cube, cube-array, and 3D image layouts, with format and extent filters removing unsupported combinations.
- Device-group cases reuse the image matrix and add device-targeted sparse binding and submission coverage.
- A passing case requires both the aliased shader-written blocks and the preserved reference data to survive the full bind, dispatch, and copy sequence.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test registration | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L1033-L1104) | Defines regular and device-group roots, image types, extents, and format filtering. |
| `ImageMemoryAliasingCase::checkSupport` | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L125-L154) | Defines feature and format requirements, including R64 atomic support. |
| Image and sparse-bind setup | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L217-L492) | Creates both images and establishes their shared residency and separate tail binds. |
| Copy and dispatch flow | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L531-L759) | Copies input data, dispatches the write shader, and copies the aliased image back. |
| Result verification | [`vktSparseResourcesImageMemoryAliasing.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageMemoryAliasing.cpp#L772-L1022) | Generates expected values and compares integer, fixed-point, and floating-point results. |
| Shared image helpers | [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L73-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) | Supplies image-type, format, plane, and sparse-support behavior shared by the family. |
| Sparse image semantics | [Vulkan sparse memory](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L497-L536) | Background for sparse image requirements, bindings, and image aspects. |

