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

A representative ordinary leaf is:

```text
image.load_store.with_format.2d.r8g8b8a8_unorm
```

It uses a 64 x 64 2D texture from `s_textures`; the precise shader text is generated at runtime. The following is a faithful structural rendering of the generator's normal 2D branch, not a checked-in shader artifact:

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(binding = 0, rgba8) readonly uniform image2D u_image0;
layout(binding = 1, rgba8) writeonly uniform image2D u_image1;

void main(void)
{
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    imageStore(u_image1, pos, imageLoad(u_image0, ivec2(63 - pos.x, pos.y)));
}
```

The generator derives image type and coordinates from the selected shape and format. In this leaf, the nonuniform XOR-based reference pattern makes a wrong source coordinate observable: the host flips the reference horizontally, then compares it with the destination. [Declarations](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1447-L1507), [2D branch](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1558-L1577), [reference pattern](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L352-L406), [verification](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1763-L1781)

Relevant generator variations are:

- Array, cube, and 3D forms use the appropriate `int`, `ivec2`, or `ivec3` coordinate form; `_single_layer` binds a per-layer non-array view. [Generator](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1447-L1455), [views](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1870-L1897)
- Formatless groups omit the relevant layout qualifier and require `GL_EXT_shader_image_load_formatted` in the generated GLSL. [Generator](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1481-L1484)
- Uniform texel-buffer sources use `textureBuffer` and `texelFetch`; three-component source formats expand the fetched channels into three stores. [Generator](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1493-L1538)

## Runtime Execution and Result Checking

1. The ordinary load/store constructor generates the reference and places it in a host-visible helper buffer. [Setup](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1726-L1761)
2. Image paths transition the source to transfer destination, copy the reference into it, transition it to `GENERAL`, execute the shader, then transition/copy the result to the helper buffer. Buffer paths use a shader-write-to-host-read barrier. [Image setup](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1939-L1987), [copy helpers](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L447-L539)
3. Ordinary loads flip the reference before comparison. Reinterpretation reference generation removes invalid floating-point representations and the SNORM `-128` representation before a differently interpreted read. [Reference safeguards](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L294-L337), [normal verifier](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1763-L1781)
4. `comparePixelBuffers()` applies format-aware acceptance: exact integer comparison, a representable-value threshold for fixed-point formats, and a mantissa-scaled one-ULP threshold for floating-point formats. [Comparison helper](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L184-L280)

## Failure Meaning

| Failing family | Investigation focus |
|---|---|
| `store` | Storage image/texel-buffer write, generated coordinate or value, descriptor view/offset, and result copyback. |
| `load_store` | Source upload and read, destination write, formatless declaration support, mirrored coordinate, and host reference transformation. |
| `format_reinterpret` | Mutable image creation, compatible view creation/access, byte interpretation, and reinterpretation reference safeguards. |
| `extend_operands_spirv1p4` | SPIR-V image-operand validation/lowering, integer width or signedness, relaxed-precision masking, and integer readback. |
| `nontemporal_operand` | `Nontemporal` on `OpImageWrite`, integer image operation, and the shared transfer/readback executor. It is not evidence of a performance regression. |
| `device_scope_access` | Device-scope availability/visibility, producer-to-consumer execution dependency, and, for `comp_draw`, fragment output/attachment readback. |
| `load_store_lod` | AMD explicit-LOD operation, level-specific coordinates/subresources, per-level transfers, and result-buffer offsets. |

## Case Pruning

| Area | CTS condition |
|---|---|
| Ordinary image and buffer access | Requires storage-image or storage-texel-buffer support for the selected format/tiling. Formatless read or write also requires the corresponding without-format feature; Vulkan SC uses its core feature checks. [Store checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L584-L657), [load/store checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1286-L1442) |
| Shapes and special formats | Cube arrays require the cube-array feature. `A8_UNORM_KHR` and `A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5` outside Vulkan SC. [Load/store checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1286-L1323) |
| Extend and nontemporal operands | Requires `VK_KHR_spirv_1_4`, storage-image and transfer support, and `shaderInt64` when applicable. Non-SC nontemporal cases additionally require Vulkan 1.3. [Checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L2723-L2777) |
| Device scope | Requires Vulkan 1.1, `vulkanMemoryModel`, `vulkanMemoryModelDeviceScope`, and equivalent API version at least 1.2. `comp_draw` also skips compute-only execution and checks color-attachment/transfer-source image support. [Checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3189-L3227) |
| AMD LOD | Requires `VK_AMD_shader_image_load_store_lod`; buffer views are excluded and formatted write images must have a SPIR-V format. [Checks](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1303-L1304), [factory](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3665-L3728) |

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
