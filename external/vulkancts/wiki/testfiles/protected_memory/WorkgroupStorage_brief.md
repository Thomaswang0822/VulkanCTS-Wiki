# Understanding Brief: protected workgroup storage

## One-Sentence Test Purpose

This test checks whether a protected compute shader can use GLSL `shared` workgroup storage to pass image data from one invocation to another and produce the expected protected image result.

## Background Knowledge

### Workgroup shared storage

A compute workgroup is the set of invocations launched together by one local workgroup. A GLSL `shared` variable is allocated once for that workgroup, rather than once per invocation, so invocations can exchange values through it. A barrier provides the control-flow and memory ordering needed before an invocation reads a value written by another invocation.

Why it matters here:
- The generated shader assigns each invocation an image-derived index into one `shared vec4` array.
- The array size is part of the shader's workgroup-storage footprint, while the protected images are separate host-created Vulkan resources.

### Protected execution and device limits

The test submits its compute work on a protected queue and creates the source and destination images with protected memory. Vulkan exposes `maxComputeSharedMemorySize` as the maximum total storage available to Workgroup variables in a compute shader, and `maxComputeWorkGroupInvocations` limits the number of invocations in one local workgroup.

Why it matters here:
- The test skips a size when the declared `sharedData` array would exceed the device's shared-memory limit.
- It also skips a case when the generated image dimensions would require too many local invocations.

## One Concrete Example

For `dEQP-VK.protected_memory.workgroupstorage.memsize_1`, the generator chooses a 1x1 local workgroup and emits a one-element array. The only invocation loads the source texel into `sharedData[0]`, reaches `barrier()`, reads `sharedData[(0 + 1) % 1]`, and stores that value in the destination image.

The example is reconstructed from the generated string; the test source does not store a standalone shader file.

```glsl
#version 450
layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(set = 0, binding = 0, rgba8) writeonly uniform highp image2D u_resultImage;
layout(set = 0, binding = 1, rgba8) readonly uniform highp image2D u_srcImage;
shared vec4 sharedData[1];

void main() {
    int gx = int(gl_GlobalInvocationID.x);
    int gy = int(gl_GlobalInvocationID.y);
    int s = 1;
    int idx0 = gy * 1 + gx;
    int idx1 = (idx0 + 1) % s;
    vec4 color = imageLoad(u_srcImage, ivec2(gx, gy));
    if (idx0 < s)
        sharedData[idx0] = color;
    barrier();
    vec4 outColor = sharedData[idx1];
    imageStore(u_resultImage, ivec2(gx, gy), outColor);
}
```

## End-to-End Test Flow

```text
[host] choose one shared-memory size and derive a power-of-two image grid whose area is at least that size
[host] fill an unprotected RGBA8 reference texture with deterministic random color tiles
[host] upload the texture to an unprotected image and copy it to a protected source image
[host] create a cleared protected destination image, storage-image descriptors, a compute pipeline, and a protected command pool
[host] submit one protected compute dispatch with one local workgroup
[device] each invocation loads one source texel, conditionally writes shared workgroup storage, waits at barrier(), then reads the next shared element and stores it
[host] calculate the same cyclic permutation in the reference texture
[host] sample four deterministic reference coordinates and ask the protected image validator to compare the destination image
[host] report pass when validation succeeds, or fail with "Result validation failed"
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The `comp` program is generated inline by `WorkgroupStorageTestCase::initPrograms()`. Its local workgroup dimensions and `sharedData` array length come from `Params`.
- `Params` starts with a 1x1 image and alternately doubles width and height until `imageWidth * imageHeight >= sharedMemorySize`. The registered sizes therefore select both the shared-memory declaration and the invocation grid.
- The reference calculation uses the same linear indexing and cyclic successor rule as the shader.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Protected source image | yes | yes, storage image at binding 1 | read | sampled by validator through the protected path | Supplies the source texels copied into workgroup storage |
| Protected destination image | yes | yes, storage image at binding 0 | written | sampled by the image validator | Carries the shader's cyclically shifted output |
| `sharedData` | no, shader-local | no descriptor binding | read and written by compute invocations | no | Tests Workgroup storage and the barrier between write and read |
| Unprotected staging/reference image | yes | yes during upload/copy | read by transfer commands | not as final output | Makes deterministic host-generated texture data available to the protected source image |

## What Is Checked

- The host creates a deterministic RGBA8 reference texture using `deInt32Hash(sharedMemorySize)` as the random seed.
- `calculateRef()` maps each pixel into a `sharedMemorySize`-element array and replaces each pixel with the next element modulo the selected size.
- `validateResult()` chooses four deterministic normalized coordinates, samples the reference texture with nearest filtering, and passes those coordinates and values to `ImageValidator`.
- The validator compares the protected destination image at those coordinates with a per-component threshold of `0.1`. A mismatch or validator submission failure returns `false`, which becomes `Result validation failed`.

## Behavior Parameter Identification

> **Behavior parameter:** shared-memory size
>
> **Candidate values:** `1`, `4`, `5`, `60`, `101`, `503`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `1` | Incorrect Workgroup storage declaration or access, barrier handling, protected image binding, or result validation for the 1x1 case |
| `4` | Incorrect Workgroup storage sizing, 2x2 invocation indexing, barrier handling, protected image binding, or result validation |
| `5` | Incorrect non-square grid handling or cyclic indexing when the 2x4 grid has more invocations than shared elements |
| `60` | Incorrect larger shared-memory declaration, 8x8 grid handling, protected dispatch, or result validation |
| `101` | Incorrect 16x8 grid handling, shared-memory sizing, protected dispatch, or result validation |
| `503` | Incorrect 32x16 grid handling, shared-memory sizing, protected dispatch, or result validation |
| Any value | A failure in protected resource creation, transfer synchronization, descriptor setup, queue submission, or the shared `ImageValidator` path |

## Important Variations and Special Cases

- The six values are deliberately not all powers of two. For `5`, `60`, `101`, and `503`, the image area is rounded up by alternating width and height doublings, so some invocations have `idx0 >= s` and do not write `sharedData`; the cyclic read still uses an in-range index modulo `s`.
- `sharedMemorySize` counts `vec4` elements in the GLSL declaration. The support check accounts for `4 * 4` bytes per element before dispatch.
- The protected-memory support gate requires Vulkan 1.1, the protected-memory feature, and a protected queue. The workgroup test does not request pipeline protected access or YCbCr conversion.
- The host-side validator uses a protected helper storage buffer and a separate unprotected reference uniform buffer. These are validator implementation details, not additional workgroup-storage variants.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter construction and generated compute shader | [`Params` and `WorkgroupStorageTestCase::initPrograms()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L58-L168) | Defines image dimensions, `sharedData`, indexing, barrier, and image bindings |
| Protected support gate | [`WorkgroupStorageTestCase::checkSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L120-L124) and [`checkProtectedContextSupport()`](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127) | Defines required API, feature, and queue support |
| Limit checks and protected resources | [`WorkgroupStorageTestInstance::iterate()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L194-L325) | Defines limits, images, descriptors, dispatch, and protected submission |
| Reference permutation and result check | [`calculateRef()` and `validateResult()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L328-L365) | Defines expected output and final status |
| Registered values | [`createWorkgroupStorageTests()`](../../../modules/vulkan/protected_memory/vktProtectedMemWorkgroupStorageTests.cpp#L370-L383) | Registers `workgroupstorage.memsize_1`, `4`, `5`, `60`, `101`, and `503` |
| Image validation | [`ImageValidator::validateImage()`](../../../modules/vulkan/protected_memory/vktProtectedMemImageValidator.cpp#L117-L263) | Compares four samples in a protected compute validation pass |
| Mustpass coverage | [`protected-memory.txt`](../../../mustpass/main/vk-default/protected-memory.txt#L5995-L6000) and [`Vulkan SC mustpass`](../../../mustpass/main/vksc-default/protected-memory.txt#L4803-L4808) | Confirms Vulkan and Vulkan SC registration paths |
| Workgroup model | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L2419-L2429) | Defines local workgroups, shared variables, and barriers |
| Shared-memory limit | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L499-L503) | Defines `maxComputeSharedMemorySize` for Workgroup/shared storage |

## Questions / Risk Points for User Audit

- Is the distinction between shader-local `sharedData` and host-created protected images clear?
- Is the non-square image-grid behavior clear for sizes whose area exceeds the shared-memory element count?
- Does the mapping table distinguish implementation causes that are source-grounded from symptoms observed only through the validator?
- Should the final page show one representative shader only, with the remaining sizes summarized as parameter variations?

## Conversion Notes for Final Wiki Rewrite

- Use `sharedMemorySize` as the primary behavioral axis and retain all six exact values in the parameter table and behavior subsections.
- Distill the workgroup and protected-resource concepts into short Background Knowledge bullets; keep the concrete `memsize_1` example as the single shader walkthrough.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write fresh cause analysis for shared-memory/barrier behavior, grid/indexing behavior, protected execution/resources, and validation.
- Keep the full source mapping only as a focused Source Reference Appendix. The final page should explain the execution and result check before listing source entry points.
