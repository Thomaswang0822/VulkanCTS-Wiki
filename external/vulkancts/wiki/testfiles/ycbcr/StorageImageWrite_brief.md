# Understanding Brief: YCbCr storage image writes

## One-Sentence Test Purpose

This test checks whether Vulkan can write the planes of a YCbCr image through compute storage-image views and preserve the expected channel values when the image is copied back to host memory.

## Background Knowledge

### Multi-planar images and plane-compatible views

A multi-planar image stores its channels in separate image planes. A disjoint image gives each plane its own memory binding, while a joint image binds the image as one allocation. Vulkan exposes a plane through `VK_IMAGE_ASPECT_PLANE_0_BIT`, `VK_IMAGE_ASPECT_PLANE_1_BIT`, or `VK_IMAGE_ASPECT_PLANE_2_BIT`. A plane can be viewed through a compatible single-plane format when the formats have the required block extent and size relationship. The test uses that relationship to make each plane writable as a storage image. See [plane-compatible formats](../../../../vulkan-docs/src/chapters/formats.adoc#formats-compatible-planes) and [multi-planar image aspects](../../../../vulkan-docs/src/chapters/formats.adoc#formats-multiplanar-image-aspect).

Why it matters here:
- A chroma-subsampled plane can have a smaller extent than the luma plane, so the shader bounds and dispatch count are plane-specific.
- Disjoint and joint cases use different image, memory, and transfer capabilities, even though both exercise the same write pattern.

### Compute storage-image access

A storage-image descriptor associates an image view with shader image operations. Compute shaders run in workgroups, and `gl_GlobalInvocationID` gives each invocation its global three-dimensional coordinate. The shader writes one texel for each coordinate inside the selected plane extent. Storage-image stores require the view to support `VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT`, and the image subresource must be in `VK_IMAGE_LAYOUT_GENERAL` while the shader accesses it. See [storage images](../../../../vulkan-docs/src/chapters/descriptors.adoc#descriptors-storageimage) and [compute shaders](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-compute).

Why it matters here:
- The test creates one compute pipeline and one storage-image descriptor for each plane.
- The host inserts barriers before the dispatch, before the image-to-buffer copy, and before host readback.

## One Concrete Example

Consider `dEQP-VK.ycbcr.storage_image_write.r10x6_unorm_pack16.512_512_1.joint`. This is a single-plane 10-bit UNORM format whose compatible writable view is `VK_FORMAT_R16_UNORM`. The generated compute shader uses a 128 by 1 by 1 local workgroup and writes the x-coordinate pattern below. The source is reconstructed from `initPrograms()` for this representative case; the production generator emits one equivalent shader for every plane.

```glsl
#version 440
layout (local_size_x = 128, local_size_y = 1, local_size_z = 1) in;
layout (binding = 0, r16) writeonly uniform highp image2D u_image;
void main (void)
{
    if( gl_GlobalInvocationID.x < 512 )
    if( gl_GlobalInvocationID.y < 512 )
    if( gl_GlobalInvocationID.z < 1 )
    {
        imageStore(u_image, ivec2( gl_GlobalInvocationID.x, gl_GlobalInvocationID.y ), vec4(float(int(gl_GlobalInvocationID.x) % 127) / 127.0, 0, 0, 0));
    }
}
```

The full generated walkthrough and validated SPIR-V appear in [StorageImageWrite](StorageImageWrite.md).

## End-to-End Test Flow

```text
[host] choose a registered format, image size, and joint or disjoint case
[host] check image-format, storage-image, plane, and required extension support
[host] create a 2D optimal-tiled image with transfer-source and storage usage
[host] allocate and bind one image allocation, or one allocation per plane for a disjoint image
[host] generate one compute shader and pipeline for each plane
[host] create a plane image view, bind it to a storage-image descriptor, and transition it to GENERAL
[host] dispatch enough workgroups to cover that plane
[device] each invocation computes a coordinate-derived value and stores one texel
[host] transition each plane to TRANSFER_SRC_OPTIMAL and copy all planes into one host-visible buffer
[host] wait for completion, invalidate the allocation, and expose each plane at its computed buffer offset
[host] decode each channel from the copied planes and compare it with the coordinate-derived reference
[host] report Passed if every checked channel value meets its integer or floating-point comparison rule
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` emits `comp0`, `comp1`, and `comp2` as needed for the format's plane count. The shader image type is `image2D`, `iimage2D`, or `uimage2D` according to the channel class. The image data type is `vec4`, `ivec4`, or `uvec4`. The image format qualifier comes from the plane-compatible format, such as `r8`, `r16`, `rgba8`, or `rgba16`. The local size is computed from that plane's extent and is capped by 128 total invocations.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| YCbCr `VkImage` | yes | yes | written through storage views | copied to buffer | The image under test, with one or more planes |
| Plane `VkImageView` | yes | indirectly through descriptor | written | no | Selects one plane and its compatible writable format |
| Storage-image descriptor | yes | yes | provides the image to the compute shader | no | Binding 0 is the shader's `u_image` |
| Per-plane compute shader and pipeline | yes | yes | executes the write | no | Uses global invocation coordinates as the pattern source |
| Host-visible output `VkBuffer` | yes | yes | transfer destination only | yes | Receives packed plane data for checking |
| Disjoint image allocations | yes, only for disjoint cases | yes | image backing memory | no | Each plane receives its own binding |

The plane views are GPU resources. `gl_GlobalInvocationID` and the coordinate-derived values are shader inputs and temporaries, not host-created resources.

## What Is Checked

- The host computes a reference for every present channel. Channel 0 uses `x % 127`, channel 1 uses `y % 127`, channel 2 uses `z % 127`, and channel 3 uses `1`.
- Integer channels require an exact match after the copied plane data is decoded.
- Fixed-point and floating-point channels use an absolute error limit of `1e-5`, with the format's fixed-point error added for fixed-point channels.
- The check runs on the host after the transfer completes. The first mismatch returns `Failed`; completing all channel and plane loops returns `Passed`.

## Behavior Parameter Identification

> **Behavior parameter:** joint/disjoint image binding mode
>
> **Candidate values:** `joint`, `disjoint`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `joint` | Whole-image storage-image support, compatible view creation, image layout transition, compute storage write, image-to-buffer copy, or channel decoding is incorrect. |
| `disjoint` | Disjoint plane support, per-plane memory binding, plane-compatible storage-image support, plane view access, layout transition, copy, or channel decoding is incorrect. |

## Important Variations and Special Cases

- The generator covers the YCbCr format range from `VK_YCBCR_FORMAT_FIRST` through the format immediately before `VK_YCBCR_FORMAT_LAST`, plus the four 2-plane 444 EXT formats from `VK_FORMAT_G8_B8R8_2PLANE_444_UNORM_EXT` through `VK_FORMAT_G16_B16R16_2PLANE_444_UNORM_EXT`.
- The candidate sizes are `{512,512,1}`, `{1024,128,1}`, and `{66,32,1}`. The generator skips a size when either dimension is not aligned to `getImageSizeAlignment(format)`.
- A disjoint case uses `VK_IMAGE_CREATE_DISJOINT_BIT | VK_IMAGE_CREATE_EXTENDED_USAGE_BIT`. If the plane's writable format differs from the image format, the image also gets `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT`.
- For multi-planar disjoint images, the copy uses plane views. The support check therefore checks storage-image support for each plane-compatible format as well as disjoint support for the original format.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test-case construction | [populateStorageImageWriteFormatGroup()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L884-L934) | Defines formats, sizes, and `joint`/`disjoint` leaves |
| Support checks | [checkSupport()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L89-L215) | Defines extension and format-feature gates |
| Shader generation | [initPrograms()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L802-L881) | Emits one plane-specific compute shader |
| Image setup and dispatch | [testStorageImageWrite()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L240-L405) | Creates views, descriptors, barriers, pipelines, and dispatches |
| Copyback and comparison | [testStorageImageWrite()](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L407-L585) | Copies planes and applies the channel checks |
| Plane extents and sizes | [getPlaneExtent()](../../../framework/vulkan/vkImageUtil.cpp#L2568-L2577) and [getPlaneSizeInBytes()](../../../framework/vulkan/vkImageUtil.cpp#L2548-L2556) | Defines subsampled extents and buffer packing |
| Storage-image semantics | [Storage Image](../../../../vulkan-docs/src/chapters/descriptors.adoc#descriptors-storageimage) | Defines storage-image descriptors, stores, features, and GENERAL layout |
| Plane compatibility | [Compatible Formats of Planes](../../../../vulkan-docs/src/chapters/formats.adoc#formats-compatible-planes) | Defines compatible single-plane view formats |

## Questions / Risk Points for User Audit

- Does the joint/disjoint distinction make clear which resource and support checks differ?
- Is the relationship between a plane extent, local workgroup size, and dispatch count clear?
- Are the host-visible readback buffer and per-plane offsets clear enough to explain the final comparison?
- Is the distinction between the reconstructed representative shader and the generated per-plane shader clear?
- Should the page call out any device-specific format-support skip messages in more detail?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page's `## Background Knowledge` limited to multi-planar plane selection, compatible views, and compute storage-image access.
- Use the `joint`/`disjoint` image binding mode as the primary behavior axis and copy this mapping table into `## Failure Meaning`.
- Turn the concrete `r10x6_unorm_pack16` case into one exact shader walkthrough. Keep the format and size matrix in `## Parameter Dimensions and Observed Values`.
- Move the host timeline, resource table, and comparison rules into `## Runtime Execution and Result Checking`.
- Write fresh cause analysis for whole-image support and per-plane disjoint support rather than copying this brief's teaching text.
- Leave source-navigation details in the final source appendix.
