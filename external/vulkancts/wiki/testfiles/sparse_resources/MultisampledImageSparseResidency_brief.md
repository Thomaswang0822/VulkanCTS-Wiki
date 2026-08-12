# Understanding Brief: MultisampledImageSparseResidency

## One-Sentence Test Purpose

This test checks whether a partially resident multisampled 2D storage image returns the expected sample-count value from bound tiles and zero from the unbound row when strict nonresident residency is required.

## Background Knowledge

### Sparse image residency and strict nonresident behavior

A sparse image can be created before all of its image-tile memory is bound. This test binds the image tiles except for the lowest row. With `residencyNonResidentStrict`, shader accesses to that unbound region must behave as nonresident accesses and return zero after the shader applies the residency result.

### Multisampled storage images

The image is a 2D `image2DMS` with one mip level, one array layer, and 2, 4, 8, or 16 samples. The compute shader addresses one pixel and sample 0 at each invocation. The sample count is written into the image, then loaded through `sparseImageLoadARB`; the shader uses `sparseTexelsResidentARB` to replace a nonresident value with zero.

## One Concrete Example

For a `VK_FORMAT_R32G32B32A32_SFLOAT` case with `samples_4`, the generated shader is conceptually:

```glsl
// Conceptual reconstruction of the generated source.
layout(set = 0, binding = 0, rgba32f) uniform image2DMS u_msImage;
layout(set = 0, binding = 1, r32ui) writeonly uniform uimage2D u_resultImage;

void main() {
    ivec2 p = ivec2(gl_GlobalInvocationID.xy);
    vec4 color;
    imageStore(u_msImage, p, 0, vec4(4));
    int code = sparseImageLoadARB(u_msImage, p, 0, color);
    if (!sparseTexelsResidentARB(code))
        color = vec4(0);
    imageStore(u_resultImage, p, uvec4(color));
}
```

The shader uses the format prefix required by the selected format: no prefix for floating-point formats, `u` for unsigned integer formats, and `i` for signed integer formats.

## End-to-End Test Flow

```text
[host] select one format, one sample count, and the fixed 256x512x1 image size
[host] require sparse binding, 2D sparse residency, the sample-count feature, strict nonresident behavior, storage-image multisampling, and shader resource residency
[host] create sparse and compute queues, create the sparse multisampled image, and query its sparse granularity
[host] bind every sparse tile except the lowest row and signal a semaphore
[host] wait for the sparse bind to complete
[host] create an R32_UINT result image, a host-visible result buffer, descriptors, and the compute pipeline
[device] clear the result image to ones, write the sample count to sample 0, and load the sparse image value
[device] replace the loaded value with zero when the sparse residency status reports a nonresident texel
[device] write the value to the result image
[host] copy the result image to the host-visible buffer and inspect all elements
[host] pass only when the bound region contains the sample count and the unbound lowest row contains zero
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test builds one compute GLSL source string per format and sample-count case. It enables `GL_ARB_sparse_texture2`, declares the selected multisampled storage-image format, and declares an `r32ui` result image. The selected sample count is embedded in the `imageStore` value.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Sparse multisampled image | yes | selected sparse image tiles only | shader reads and writes sample 0 | no | Its missing lowest tile row supplies the nonresident region. |
| R32_UINT result image | yes | yes | shader writes | copied to buffer | Stores the shader's residency-adjusted value. |
| Host-visible result buffer | yes | yes | transfer writes | yes | Supplies the host-side pass/fail data. |
| Descriptor set and compute pipeline | yes | n/a | binds both storage images | no | Connects the generated shader to the resources. |

## What Is Checked

The host reads one `uint32_t` per image element. Elements in the bound portion must equal the selected sample count. Elements after the bound portion, which represent the lowest unbound row in the linear result check, must equal zero. Any mismatch fails the test.

## Behavior Parameter Identification

> **Behavior parameter:** image format and sample-count test case
>
> **Candidate values:** 11 formats (`rgba32f`, `rgba16f`, `r32f`, `rgba32ui`, `rgba16ui`, `rgba8ui`, `r32ui`, `rgba32i`, `rgba16i`, `rgba8i`, `r32i`) crossed with `samples_2`, `samples_4`, `samples_8`, and `samples_16`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Any format with `samples_2`, `samples_4`, `samples_8`, or `samples_16` | Sparse multisampled image creation or binding, sample-count support, storage-image access, sparse shader load, synchronization, result copyback, or host validation does not produce the expected values. |
| Floating-point format value | Format-specific storage-image or conversion behavior may affect the value written to the `r32ui` result image. |
| Unsigned or signed integer format value | Format-specific shader type selection, storage-image access, or conversion to the unsigned result image may be incorrect. |

Primary source: [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L1-L43)
