## Overview

**Core question:** Do Vulkan storage-image and texel-buffer operations produce the expected texel data when the CTS changes format declaration, resource view, SPIR-V image operand, memory-model scope, or explicit mip level?

## Background Knowledge

For the shared concepts image/view/format interpretation and synchronization, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

The Vulkan [resource-descriptor](https://docs.vulkan.org/spec/latest/chapters/descriptorsets.html) and [image](https://docs.vulkan.org/spec/latest/chapters/resources.html) chapters define the API context. The CTS source, rather than this background, defines exactly which legal combinations are registered and when a case is skipped.

- **Storage-image declaration versus view format.** A GLSL storage-image declaration can include a format layout qualifier or omit it. The latter path is tested only when the matching storage-read-without-format or storage-write-without-format support is present. An image view exposes the access format used by the shader; the underlying image is separately created with its storage format.
- **Reinterpretation is not conversion.** The reinterpretation family creates storage using one format and accesses it through a different compatible view format. Its compatibility predicate accepts identical formats or equal-size, non-alpha-only pairs; the factory further excludes identical pairs. Thus this family checks byte-preserving compatible-view access, not numeric conversion.
- **Visibility is distinct from execution order.** The device-scope shaders emit image-memory barriers with `MakeAvailable` or `MakeVisible` at device scope. A command-buffer pipeline barrier orders the producer and consumer stages. The [synchronization chapter](https://docs.vulkan.org/spec/latest/chapters/synchronization.html) provides the API background; the source deliberately exercises both mechanisms.

## Registration Hierarchy

[`vktImageLoadStoreTests.cpp`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp) implements seven direct `image` families:

```text
image
├── store
├── load_store
├── format_reinterpret
├── extend_operands_spirv1p4
├── nontemporal_operand
├── device_scope_access
└── load_store_lod
```

[`createChildren()`](../../../modules/vulkan/image/vktImageTests.cpp#L61-L99) adds the families below `image`; their factories are in [`vktImageLoadStoreTests.cpp#L3408-L3975`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3408-L3975). `nontemporal_operand` is not registered in Vulkan SC builds.

## Parameter Dimensions and Observed Values

| Dimension | Registered values or rule | Source evidence |
|---|---|---|
| Direct family | `store`, `load_store`, `format_reinterpret`, `extend_operands_spirv1p4`, `nontemporal_operand`, `device_scope_access`, `load_store_lod` | [Factories](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3408-L3975) |
| Ordinary shapes | `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array`, `buffer` | [`s_textures`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2973-L2982) |
| Ordinary formats | Selected float, integer, normalized, sRGB, packed, alpha, and three-component formats | [`s_formats`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2995-L3096) |
| Tiling | optimal (no suffix) and linear (`_linear`) | [`s_tilings`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3098-L3113) |
| Ordinary declaration groups | `store`: `with_format`, `without_format`; `load_store`: those groups plus `without_any_format` | [Store factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3408-L3508), [load/store factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3511-L3663) |
| Layer and buffer variants | Formatted eligible layered leaves add `_single_layer`; buffer leaves add `_minalign`; selected load sources add `_uniform` | [Factories](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3447-L3463), [load/store buffer branches](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3554-L3619) |
| Reinterpretation pair | Distinct `imageFormat_format` pair accepted by `formatsAreCompatible()` | [Predicate](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L440-L445), [factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3730-L3758) |
| Extension operands | `read`/`write`, matched or permitted mismatched signedness, normal or eligible relaxed precision | [Factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3819-L3893) |
| Device-scope consumer | `comp_comp`, `comp_draw`; draw excludes 3D | [Factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3921-L3975) |
| AMD LOD | `with_format` and `without_format`, optimal-tiled non-buffer shapes, six mip levels | [Factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3665-L3728) |

Depth-only ordinary leaves are intentionally formatless, optimal-tiled, and limited to 2D or 2D-array shapes. The formatted branch is disabled because the source does not substitute a different SPIR-V image format for a depth format. [Source](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3467-L3498), [load/store equivalent](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3621-L3650)

## Behavior Parameters

### `store`

Each invocation writes a storage-image texel or storage texel-buffer element. The normal reference uses a coordinate-derived pattern; `_constant` leaves use the representable middle value. The result is read back and compared with the generated reference. [Reference generation](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L352-L412), [store generator](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L659-L861)

### `load_store`

The host initializes a source resource with a reference pattern. The shader loads from horizontally mirrored x and writes to the same invocation's destination coordinate; the verifier horizontally flips the reference before comparing. `with_format` declares both images, `without_format` declares only the destination, and `without_any_format` declares neither. [Generator](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1444-L1614), [verification](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1726-L1781)

### `format_reinterpret`

This uses the ordinary load/store executor with distinct access and storage formats. Both images receive `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` when those formats differ, while descriptor views use the access format. [Image creation](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1818-L1850), [view creation](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1852-L1899)

### `extend_operands_spirv1p4`

These 8 x 8 integer tests generate SPIR-V assembly, not GLSL. `SignExtend` is selected for signed tested formats and `ZeroExtend` for unsigned formats. The operand is emitted on `OpImageRead` for `read` leaves and on `OpImageWrite` for `write` leaves. Relaxed-precision results are compared after retaining only each component's low 16 bits. [SPIR-V generator](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2779-L2966), [result check](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2622-L2669)

### `nontemporal_operand`

This reuses the integer SPIR-V executor for 8 x 8 images, changes the generated module to SPIR-V 1.6, and emits `Nontemporal` on `OpImageWrite`. It checks returned image values, not cache behavior or performance. [Generator branch](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2900-L2907), [factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3895-L3919)

### `device_scope_access`

The producer compute shader mirrors source data into the other image and then emits a device-scope make-available barrier. After a command-buffer execution dependency, the consumer emits a device-scope make-visible barrier. `comp_comp` copies the data back with compute; `comp_draw` loads it in a fragment shader and writes a color attachment. [Generated barriers](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1462-L1517), [store-side barrier](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1600-L1604), [execution](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3247-L3404)

### `load_store_lod`

This AMD-extension family emits `imageLoadLodAMD` and `imageStoreLodAMD` for every one of six mip levels. Each level's mirror expression uses that level's width, and validation reports the first failed level independently. [LOD generator](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1540-L1589), [per-level verifier](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2133-L2162)

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.load_store.with_format.2d.r8g8b8a8_unorm
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `load_store` | The compute shader reads a source image and writes the transformed value to a destination image. |
| `with_format.2d.r8g8b8a8_unorm` | Both storage-image declarations carry the `rgba8` qualifier; the 2D texture is 64 x 64 and the normalized four-channel format makes the mirrored transfer directly comparable. |
| Optimal-tiled 2D image, one layer | Each invocation handles one `(x, y)` texel with a one-to-one destination coordinate. |

#### Purpose

This shader copies the source image into the destination while mirroring the source coordinate horizontally. The host-side verifier applies the same horizontal flip to its reference image, so a wrong image binding, coordinate, or storage-image operation becomes observable.

#### Structural Design

| Phase | Shader operation | Observable contract |
|-------|------------------|----------------------|
| Invocation mapping | `gl_GlobalInvocationID.xy` → `pos` | One local-size-1 invocation addresses one destination texel. |
| Source lookup | `imageLoad(u_image0, ivec2(63 - pos.x, pos.y))` | The x coordinate is reflected across the 64-wide image; y is unchanged. |
| Destination write | `imageStore(u_image1, pos, ...)` | The loaded normalized RGBA value is written at the unmirrored destination coordinate. |

#### Shader Code

```glsl
#version 450

/// One invocation covers one destination texel because the generated workgroup is 1 x 1 x 1.
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
/// Source storage image at descriptor binding 0; `rgba8` is the selected with-format qualifier.
layout (binding = 0, rgba8) readonly uniform image2D u_image0;
/// Destination storage image at descriptor binding 1 with the same shader-visible format.
layout (binding = 1, rgba8) writeonly uniform image2D u_image1;

void main (void)
{
    /// The invocation ID supplies the destination coordinate in the 64 x 64 2D image.
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    /// Read the horizontally mirrored source texel and store it at the destination coordinate.
    imageStore(u_image1, pos, imageLoad(u_image0, ivec2(63-pos.x, pos.y)));
}
```

#### Additional Info

- `makePrograms()` selects `SPIRV_VERSION_1_3` explicitly for this generated compute shader ([shader build options and declarations](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1444-L1507)).
- The host initializes the source image with the generated reference, transitions it to `GENERAL`, dispatches the compute shader, and copies the destination back before comparison; `LoadStoreTestInstance::verifyResult()` flips the reference horizontally for this load/store family ([image execution](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1939-L1987), [verification](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1726-L1781)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Image shape | 1D, array, cube, and 3D cases change the image type and coordinate dimensionality; the selected 2D case uses `ivec2` and preserves y. | [`s_textures` and dimension branches](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1447-L1455) |
| Format declaration | `without_format` omits the image format qualifier and requires the formatted-load extension path; `with_format` emits the selected qualifier for reads and writes. | [`LoadStoreTest::makePrograms()`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1452-L1507) |
| Access mode | Buffer and uniform-texel-buffer sources replace `imageLoad` with `texelFetch`; the selected image path retains `imageLoad`/`imageStore`. | [`makePrograms()` buffer and image branches](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1493-L1556) |
| Synchronization family | Device-scope producer/consumer variants add memory-model headers and acquire/release visibility barriers around the same image dataflow. | [`makePrograms()` device-scope branches](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1462-L1479) and [barriers](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1513-L1517) |
| Explicit LOD | `load_store_lod` emits `imageLoadLodAMD`/`imageStoreLodAMD` once for each mip level; the selected ordinary leaf uses implicit-level storage-image operations. | [LOD branches](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1540-L1568) |

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
; Bound: 39
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %pos "pos"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %u_image1 "u_image1"
               OpName %u_image0 "u_image0"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %u_image1 NonReadable
               OpDecorate %u_image1 Binding 1
               OpDecorate %u_image1 DescriptorSet 0
               OpDecorate %u_image0 NonWritable
               OpDecorate %u_image0 Binding 0
               OpDecorate %u_image0 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
      %v2int = OpTypeVector %int 2
%_ptr_Function_v2int = OpTypePointer Function %v2int
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
      %float = OpTypeFloat 32
         %19 = OpTypeImage %float 2D 0 0 0 2 Rgba8
%_ptr_UniformConstant_19 = OpTypePointer UniformConstant %19
   %u_image1 = OpVariable %_ptr_UniformConstant_19 UniformConstant
   %u_image0 = OpVariable %_ptr_UniformConstant_19 UniformConstant
     %int_63 = OpConstant %int 63
     %uint_0 = OpConstant %uint 0
%_ptr_Function_int = OpTypePointer Function %int
     %uint_1 = OpConstant %uint 1
    %v4float = OpTypeVector %float 4
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
        %pos = OpVariable %_ptr_Function_v2int Function
         %15 = OpLoad %v3uint %gl_GlobalInvocationID
         %16 = OpVectorShuffle %v2uint %15 %15 0 1
         %17 = OpBitcast %v2int %16
               OpStore %pos %17
         %22 = OpLoad %19 %u_image1
         %23 = OpLoad %v2int %pos
         %25 = OpLoad %19 %u_image0
         %29 = OpAccessChain %_ptr_Function_int %pos %uint_0
         %30 = OpLoad %int %29
         %31 = OpISub %int %int_63 %30
         %33 = OpAccessChain %_ptr_Function_int %pos %uint_1
         %34 = OpLoad %int %33
         %35 = OpCompositeConstruct %v2int %31 %34
         %37 = OpImageRead %v4float %25 %35
               OpImageWrite %22 %23 %37
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. The ordinary load/store constructor generates the reference and places it in a host-visible helper buffer. [Setup](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1726-L1761)
2. Image paths transition the source to transfer destination, copy the reference into it, transition it to `GENERAL`, execute the shader, then transition/copy the result to the helper buffer. Buffer paths use a shader-write-to-host-read barrier. [Image setup](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1939-L1987), [copy helpers](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L447-L539)
3. Ordinary loads flip the reference before comparison. Reinterpretation reference generation removes invalid floating-point representations and the SNORM `-128` representation before a differently interpreted read. [Reference safeguards](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L294-L337), [normal verifier](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1763-L1781)
4. `comparePixelBuffers()` applies format-aware acceptance: exact integer comparison, a representable-value threshold for fixed-point formats, and a mantissa-scaled one-ULP threshold for floating-point formats. [Comparison helper](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L184-L280)

## Failure Meaning

### Failure Cause Mapping

| Failing family | Investigation focus |
|---|---|
| `store` | Storage image/texel-buffer write, generated coordinate or value, descriptor view/offset, and result copyback. |
| `load_store` | Source upload and read, destination write, formatless declaration support, mirrored coordinate, and host reference transformation. |
| `format_reinterpret` | Mutable image creation, compatible view creation/access, byte interpretation, and reinterpretation reference safeguards. |
| `extend_operands_spirv1p4` | SPIR-V image-operand validation/lowering, integer width or signedness, relaxed-precision masking, and integer readback. |
| `nontemporal_operand` | `Nontemporal` on `OpImageWrite`, integer image operation, and the shared transfer/readback executor. It is not evidence of a performance regression. |
| `device_scope_access` | Device-scope availability/visibility, producer-to-consumer execution dependency, and, for `comp_draw`, fragment output/attachment readback. |
| `load_store_lod` | AMD explicit-LOD operation, level-specific coordinates/subresources, per-level transfers, and result-buffer offsets. |

### Cause Analysis

#### Family-specific execution or validation path

**Possible failure symptoms:** The selected family fails during shader or resource setup, execution, transfer readback, or its family-specific result comparison.

**Possible implementation causes:** The applicable stages are the ones identified for that family in the mapping above; the source references in the behavior and runtime sections define the generated operation, synchronization path, and result check used to distinguish them.

## Case Pruning

### Requirement-based pruning

| Area | CTS condition |
|---|---|
| Ordinary image and buffer access | Requires storage-image or storage-texel-buffer support for the selected format/tiling. Formatless read or write also requires the corresponding without-format feature; Vulkan SC uses its core feature checks. [Store checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L584-L657), [load/store checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1286-L1442) |
| Shapes and special formats | Cube arrays require the cube-array feature. `A8_UNORM_KHR` and `A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5` outside Vulkan SC. [Load/store checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1286-L1323) |
| Extend and nontemporal operands | Requires `VK_KHR_spirv_1_4`, storage-image and transfer support, and `shaderInt64` when applicable. Non-SC nontemporal cases additionally require Vulkan 1.3. [Checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2723-L2777) |
| Device scope | Requires Vulkan 1.1, `vulkanMemoryModel`, `vulkanMemoryModelDeviceScope`, and equivalent API version at least 1.2. `comp_draw` also skips compute-only execution and checks color-attachment/transfer-source image support. [Checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3189-L3227) |
| AMD LOD | Requires `VK_AMD_shader_image_load_store_lod`; buffer views are excluded and formatted write images must have a SPIR-V format. [Checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1303-L1304), [factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3665-L3728) |

### Design-based pruning

Additional design pruning: formatted ordinary leaves are created only for formats with a SPIR-V image-format spelling; unsigned extension-operand formats omit `mismatched_sign`; relaxed precision is registered only when the selected read format is eligible; and `comp_draw` excludes 3D. [Factories](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3540-L3559), [operand pruning](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3851-L3881), [device-scope pruning](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3942-L3949)

## Key Takeaways

- The shared ordinary path makes a nontrivial mirrored transfer observable through format-aware host comparison; it is not a constant-value smoke test.
- Format declaration mode, view reinterpretation, texel-buffer alignment, and uniform texel-buffer sources use the same core dataflow while stressing distinct descriptor and capability paths.
- The SPIR-V operand families validate functional image results for `SignExtend`, `ZeroExtend`, and `Nontemporal`; the nontemporal family does not benchmark cache behavior.
- Device-scope coverage combines shader availability and visibility semantics with command-buffer execution order, then checks the same image-derived data through compute or graphics consumption.
- The AMD family validates explicit per-mip image operations and reports failures at the individual mip level.

### Mustpass Evidence

The default mustpass lists contain leaves for all seven direct families. The counts below are line counts of `dEQP-VK.image.<family>.` entries in this checkout's `mustpass/main` tree, not a count of all dynamically registered leaves.

| Family | Default mustpass list | Listed leaves |
|---|---|---:|
| `store` | [`store.txt`](../../../mustpass/main/vk-default/image/store.txt) | 3012 |
| `load_store` | [`load-store.txt`](../../../mustpass/main/vk-default/image/load-store.txt) | 3446 |
| `format_reinterpret` | [`format-reinterpret.txt`](../../../mustpass/main/vk-default/image/format-reinterpret.txt) | 5944 |
| `extend_operands_spirv1p4` | [`extend-operands-spirv1p4.txt`](../../../mustpass/main/vk-default/image/extend-operands-spirv1p4.txt) | 81 |
| `nontemporal_operand` | [`nontemporal-operand.txt`](../../../mustpass/main/vk-default/image/nontemporal-operand.txt) | 21 |
| `device_scope_access` | [`device-scope-access.txt`](../../../mustpass/main/vk-default/image/device-scope-access.txt) | 390 |
| `load_store_lod` | [`load-store-lod.txt`](../../../mustpass/main/vk-default/image/load-store-lod.txt) | 702 |

## Source Reference Appendix

| Entry point | Why it matters |
|---|---|
| [`generateReferenceImage()` and `comparePixelBuffers()`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L184-L445) | Defines the data oracle, reinterpretation safeguards, and comparison policy. |
| [`StoreTest`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L541-L861) | Defines ordinary store support and shader generation. |
| [`LoadStoreTest`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1224-L1689) | Defines ordinary load/store support, declarations, mirrored access, device-scope GLSL, and AMD LOD GLSL. |
| [`LoadStoreTestInstance` and image variants](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1726-L2422) | Sets up resources, uploads, dispatches, copies, and verifies ordinary and LOD results. |
| [`ImageExtendOperandTest`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2671-L2971) | Generates operand SPIR-V and verifies integer results. |
| [`ImageDeviceScopeAccessTest`](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3126-L3406) | Implements device-scope support checks and two-stage execution. |
| [Registration factories](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3408-L3975) | Defines the seven direct test roots and their case matrices. |
