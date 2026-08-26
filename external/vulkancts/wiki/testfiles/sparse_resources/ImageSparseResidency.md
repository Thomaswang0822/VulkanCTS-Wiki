## Overview

**Core question:** Do sparse image binds make resident image data visible to compute shaders and readback while unbound blocks follow the device's nonresident residency contract?

- `vktSparseResourcesImageSparseResidency.cpp` implements both sparse image residency roots and the regular root's mutable-format branch.
- The regular root covers 2D, 2D-array, cube, cube-array, and 3D images. The device-group root covers the same five image types and supplies device-group sparse-bind metadata.
- The test binds alternating sparse blocks, writes coordinate-derived values with compute shaders, copies image planes back, and checks the results. When `residencyNonResidentStrict` is enabled, unbound blocks must read as zero.
- The regular root also tests compatible mutable-format image views by writing separate image portions through two views and comparing the copied portions with generated references.

## Background Knowledge

- Sparse image residency lets an image exist with only selected memory regions bound. Operations that touch an unbound region therefore have device-defined behavior unless the device advertises strict nonresident residency.
- A sparse image can have separate memory requirements for image blocks, mip tails, and metadata. Multi-planar images also expose planes whose compatible storage formats can differ from the image's external format.
- A mutable-format image can use views with compatible formats. The view format controls the storage-image access used for a write, while the image and view format compatibility rules constrain which combinations are legal.

## Registration Hierarchy

```text
sparse_resources.image_sparse_residency
├── 2d
├── 2d_array
├── cube
├── cube_array
├── 3d
└── mutable

sparse_resources.device_group_image_sparse_residency
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

The tree shows only direct children. Beneath the image-type groups, registration expands through format identifiers and image-size leaves. The mutable group expands through image type and compatible image/view format triples.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Root | `image_sparse_residency`, `device_group_image_sparse_residency` | Selects regular sparse binds or device-group sparse-bind metadata. | [`createImageSparseResidencyTests`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2149) |
| Image type | `2d`, `2d_array`, `cube`, `cube_array`, `3d` | Selects image dimensionality and layer or depth interpretation. | [`createImageSparseResidencyTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2029-L2045) |
| Regular image size | `512_256_1`, `1024_128_1`, `11_137_1` for `2d`; `512_256_6`, `1024_128_8`, `11_137_3` for `2d_array`; `256_256_1`, `128_128_1`, `137_137_1` for `cube`; `256_256_6`, `128_128_8`, `137_137_3` for `cube_array`; `512_256_16`, `1024_128_8`, `11_137_3` for `3d` | Varies sparse block counts, image extent, array layers, or 3D depth. | [`createImageSparseResidencyTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2030-L2045) |
| Format | Formats from `getSparseResidencyTestFormats`; applicable regular non-device-group cases also include `VK_FORMAT_A8_UNORM_KHR` | Selects channel class, plane layout, storage compatibility, and format-specific feature checks. | [`ImageSparseResidencyCase::checkSupport`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L276-L336) |
| Mutable image size | `512_256_1` for `2d`, `512_512_2` for `2d_array`, `512_512_3` for `3d` | Fixes the image extent while the format triple varies. | [`createImageSparseResidencyTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2091) |

## Behavior Parameters

The primary behavioral axis is the direct child under the registered root. The regular root has six values; the device-group root has five because the mutable branch is excluded when `useDeviceGroup` is true.

### `2d`, `2d_array`, `cube`, `cube_array`, and `3d` | sparse residency by image type

Each image-type group creates cases for its registered formats and supported sizes. The case creates a sparse storage image, binds every other sparse block in resident mip levels, and uses the image type's coordinate mapping for shader writes and readback validation. Cube and cube-array cases use cube-compatible layer arrangements; array and 3D cases preserve their respective layer or depth interpretation.

### `mutable` | sparse mutable-format image views

The regular-only mutable group creates compatible triples of image, first-view, and second-view formats, with all three formats distinct. It allocates only the left half of the image, writes the upper and lower portions through separate storage-image views, copies both portions out, and compares each portion with a generated integer or floating-point reference image.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.sparse_resources.device_group_image_sparse_residency.2d.r32ui.512_256_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `device_group_image_sparse_residency` | Selects the device-group sparse-bind path. The shader itself is shared with regular image residency; the host bind additionally carries `VkDeviceGroupBindSparseInfo`. |
| `2d.r32ui.512_256_1` | Selects a single-plane 2D unsigned-integer storage image with a 512×256×1 shader grid. `r32ui` makes the image variable a `uimage2D` and the stored payload a `uvec4`. |
| `local_size = 128, 1, 1` | `computeWorkGroupSize()` caps the generated workgroup at 128 invocations. The dispatch dimensions are rounded up from the 512×256×1 shader extent. |

#### Purpose

The compute shader writes a coordinate-derived unsigned value to every in-range texel of the sparse image. Host-side readback then checks the alternating resident sparse blocks against the same coordinate pattern and, when strict nonresident residency is advertised, checks unbound blocks for zero.

#### Structural Design

| Phase | Shader operation | Test signal |
|------|------------------|-------------|
| Invocation grid | `gl_GlobalInvocationID` supplies x/y/z coordinates | One invocation maps to one candidate texel. |
| Bounds guards | Three nested comparisons retain only x < 512, y < 256, z < 1 | Rounded-up dispatches cannot write outside the selected image extent. |
| Coordinate mapping | `ivec2(gl_GlobalInvocationID.x, gl_GlobalInvocationID.y)` | The 2D image ignores the z coordinate for addressing. |
| Payload construction | x, y, and z are converted to signed integers, reduced modulo 127, then converted to `uint`; alpha is 1 | Host validation can identify which resident texel or channel failed. |
| Image store | `imageStore(u_image, coord, payload)` | The resulting image is copied to a host-visible buffer after the shader-to-transfer barrier. |

#### Shader Code

```glsl
#version 440

/// The generated workgroup is 128×1×1 for the 512×256×1 r32ui case. The host dispatches enough groups to cover the image.
layout (local_size_x = 128, local_size_y = 1, local_size_z = 1) in;

/// Binding 0, set 0 is the host-created sparse image view. The r32ui qualifier selects unsigned 32-bit storage-image
/// format compatibility, and writeonly matches the shader's sole image operation.
layout (binding = 0, r32ui) writeonly uniform highp uimage2D u_image;

void main (void)
{
    /// The host rounds dispatch dimensions up to whole workgroups. These guards preserve the exact 512×256×1 image extent.
    if( gl_GlobalInvocationID.x < 512 )
    if( gl_GlobalInvocationID.y < 256 )
    if( gl_GlobalInvocationID.z < 1 )
    {
        /// The 2D coordinate uses x and y. Each channel records a deterministic coordinate component modulo 127;
        /// alpha is the constant one used by the generated unsigned-integer payload.
        imageStore(u_image, ivec2(gl_GlobalInvocationID.x,gl_GlobalInvocationID.y), uvec4(
            int(gl_GlobalInvocationID.x) % 127,
            int(gl_GlobalInvocationID.y) % 127,
            int(gl_GlobalInvocationID.z) % 127,
            1));
    }
}
```

#### Additional Info

- The selected device-group case uses one generated `comp0` module because `r32ui` has one image plane; the device-group distinction is in sparse binding and submission metadata, not shader text.
- The source selects SPIR-V 1.3 explicitly through `ShaderBuildOptions(..., SPIRV_VERSION_1_3, FLAG_ALLOW_SCALAR_OFFSETS)`.
- The host binds alternating image blocks, transitions the image to `GENERAL`, waits on the sparse-bind semaphore at the compute stage, and transitions the written image to `TRANSFER_SRC_OPTIMAL` before readback.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Image type | Changes the generated image type and coordinate constructor: `image2D`/`ivec2` for 2D, `image2DArray`/`ivec3` for 2D-array, `imageCube`/`ivec3` for cube, `imageCubeArray`/`ivec3` for cube-array, or `image3D`/`ivec3` for 3D. | [`getShaderImageType` and `getCoordStr`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L466-L565), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L103-L120) |
| Format and plane count | Selects signedness, image data type, format qualifier, channel ordering, and one generated `comp<plane>` shader per plane. R64 cases add explicit 64-bit arithmetic/image extensions; A8 cases add formatted-image-load support and omit the format qualifier. | [`ImageSparseResidencyCase::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L175-L272) |
| Image size | Changes the literal bounds and shader grid; `getShaderGridSize()` maps array layers, cube faces, or 3D depth into the z dispatch dimension. | [`getShaderGridSize`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L120-L155), [`createImageSparseResidencyTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2029-L2076) |
| Regular versus device-group root | Does not change the generated shader. It changes sparse bind submission by attaching `VkDeviceGroupBindSparseInfo` in the device-group instance. | [`ImageSparseResidencyInstance::iterate`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L632-L652) |
| Mutable branch | Uses a separate `comp` shader with two storage-image bindings, constant format-dependent colors, and a y-half branch selecting `image0` or `image1`; it is registered only for the regular root. | [`ImageMutableSparseTest::initPrograms`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1342-L1420), [`createImageSparseResidencyTestsCommon`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2135) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 65
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 128 1 1
               OpSource GLSL 440
               OpName %main "main"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
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
         %32 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_32 = OpTypePointer UniformConstant %32
    %u_image = OpVariable %_ptr_UniformConstant_32 UniformConstant
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
    %int_127 = OpConstant %int 127
     %v4uint = OpTypeVector %uint 4
   %uint_128 = OpConstant %uint 128
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_128 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
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
         %35 = OpLoad %32 %u_image
         %36 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %37 = OpLoad %uint %36
         %39 = OpBitcast %int %37
         %40 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %41 = OpLoad %uint %40
         %42 = OpBitcast %int %41
         %44 = OpCompositeConstruct %v2int %39 %42
         %45 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %46 = OpLoad %uint %45
         %47 = OpBitcast %int %46
         %49 = OpSMod %int %47 %int_127
         %50 = OpBitcast %uint %49
         %51 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %52 = OpLoad %uint %51
         %53 = OpBitcast %int %52
         %54 = OpSMod %int %53 %int_127
         %55 = OpBitcast %uint %54
         %56 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_2
         %57 = OpLoad %uint %56
         %58 = OpBitcast %int %57
         %59 = OpSMod %int %58 %int_127
         %60 = OpBitcast %uint %59
         %62 = OpCompositeConstruct %v4uint %50 %55 %60 %uint_1
               OpImageWrite %35 %44 %62
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

- The instance creates a logical device with both sparse-binding and compute queues. It checks image limits, sparse support for the selected image type, storage-image support, and format-specific R64 or A8 requirements before execution.
- It creates the sparse image, queries sparse memory requirements, and binds alternating image blocks. It binds mip tails and metadata when required. Device-group cases attach `VkDeviceGroupBindSparseInfo` to the sparse bind.
- After the sparse bind completes, the test transitions the image for shader access, dispatches the generated compute shader for each plane, then copies each plane to host-visible memory.
- Resident blocks must contain coordinate-derived channel values. Integer channels use exact comparisons; fixed-point and floating-point channels use format-aware tolerances. If `residencyNonResidentStrict` is true, nonresident blocks must contain zeroes within the same channel rules.
- Mutable cases copy the two written portions and compare them with `tcu::intThresholdCompare` for integer formats or `tcu::floatThresholdCompare` with a `0.01` threshold for floating-point formats.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d`, `2d_array`, `cube`, `cube_array`, or `3d` | Sparse image binding, compute image stores, image-plane readback, or format-aware validation does not preserve the expected values. |
| `mutable` | Sparse mutable-format image creation, view-based writes, copyback, or integer/floating-point reference comparison does not preserve the two written portions. |
| Any device-group image-type value | Device-group sparse-bind metadata or peer-memory handling fails in addition to the regular residency path. |

### Cause Analysis

#### Sparse residency data or strict nonresident results

**Possible failure symptoms:** A resident block differs from its coordinate-derived reference, or a nonresident block is nonzero when strict nonresident residency requires zero.

**Possible implementation causes:** The sparse bind may cover the wrong subresource, offset, extent, layer, mip tail, or metadata region. The compute image store, image layout transition, sparse queue synchronization, or copyback path may also expose the wrong data. The exact failing layer requires the test log and source-level investigation.

#### Mutable-format view writes and comparisons

**Possible failure symptoms:** Either copied image portion fails its integer comparison or exceeds the floating-point threshold against the reference generated for its view format.

**Possible implementation causes:** The image and view format combination may be handled incorrectly, one view may address the wrong portion, or sparse memory coverage may not match the view access. Source inspection grounds these as the relevant mechanisms; the precise defect location requires the failing format triple and test log.

#### Device-group sparse binding

**Possible failure symptoms:** A device-group case fails the same resident-data checks as a regular case, with the failure limited to device-group execution or peer-memory arrangements.

**Possible implementation causes:** The device-group bind metadata may select the wrong resource or memory device, or peer-memory features may not support the requested mapping. The failing device indices and sparse-bind trace are needed to distinguish these cases.

## Case Pruning

### Requirement-based pruning

Cases are skipped when image limits, sparse residency support for the image type, storage-image support, queue requirements, memory types, sparse address-space limits, or sparse image-format properties are unavailable. Device-group cases additionally require suitable peer-memory features. R64 formats require `VK_EXT_shader_image_atomic_int64` with both shader-image and sparse-image 64-bit atomic support. `VK_FORMAT_A8_UNORM_KHR` requires `VK_KHR_maintenance5` and storage writes without a format where that branch is applicable. Mutable cases require sparse and mutable image-format properties for the image and its views.

### Design-based pruning

The regular matrix adds `mutable` only to the non-device-group root because the mutable implementation does not support device-group mode. Mutable cases retain only triples in which all three formats differ and the image format is compatible with both view formats. The regular image matrix uses one registered set of sizes per image type, while format alignment checks remove sizes that cannot represent a selected format, including certain odd-sized YCbCr cases.

## Key Takeaways

- The test deliberately leaves alternating sparse blocks unbound, so resident data and strict nonresident behavior are checked separately.
- Image type changes the layer, face, or depth mapping used by both sparse binds and validation; it is the page's main behavioral axis.
- Multi-planar formats use per-plane storage-compatible operations and readback checks.
- Mutable-format coverage tests two view-driven writes into separate image portions and compares each portion in the view's format.
- Device-group coverage reuses the residency matrix but adds device-group sparse-bind metadata and omits mutable-format cases.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createImageSparseResidencyTests` and `createDeviceGroupImageSparseResidencyTests` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2149) | Registers the two category-qualified roots. |
| `createImageSparseResidencyTestsCommon` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2025-L2137) | Defines image types, sizes, formats, and the regular-only mutable branch. |
| `ImageSparseResidencyCase::checkSupport` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L276-L337) | Defines image, format, and feature support gates. |
| `ImageSparseResidencyInstance::iterate` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L365-L1205) | Creates resources, binds sparse memory, dispatches shaders, copies planes, and validates resident and nonresident data. |
| `ImageMutableSparseTestInstance::verifyImage` | [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1508-L1575) | Compares copied mutable-view portions with generated references. |
| Sparse image helpers | [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L43-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) | Supplies image-type, plane, format, and sparse-support helpers. |
