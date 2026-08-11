# Understanding Brief: image.qualifiers / vktImageQualifiersTests.cpp

## One-Sentence Test Purpose

This test checks whether GLSL `coherent`, `volatile`, and `restrict` qualifiers on storage-image and texel-buffer declarations compile and execute with the memory-access behavior expected by the Vulkan CTS cases.

## Background Knowledge

### Shader memory qualifiers and synchronization

A qualifier decorates a shader resource declaration; it does not create a host-side Vulkan memory barrier. The Vulkan specification says that accesses through a `Coherent` variable make available writes to the same buffer, buffer view, or image view visible, but still requires an explicit memory dependency to order writes to different locations. The compute shader in this test therefore uses both `memoryBarrier()` and `barrier()` between its write and cross-invocation read phases.

`volatile` constrains an implementation's freedom to reuse a previously loaded value. The CTS case applies it to the same storage-image declaration used for `imageStore` and `imageLoad`; the final image comparison checks the resulting computation rather than inspecting compiler decisions directly.

`restrict` is an aliasing promise on a resource declaration. Its test path differs from the other two: `vktImageQualifiersTests.cpp` delegates each image-type case to the load/store implementation, which creates a `LoadStoreTest` with `FLAG_RESTRICT_IMAGES`. That generator places `restrict` on its read and write image declarations.

Why this matters here:

- `coherent` does not replace the shader barriers that make the workgroup exchange well defined.
- `volatile` and `coherent` share the local generated compute-shader path, but express different declaration semantics.
- `restrict` has a separate delegated implementation and a different registered matrix.

## One Concrete Example

Consider `dEQP-VK.image.qualifiers.coherent.2d.r32ui`.

1. The generated compute shader declares an `r32ui coherent uniform uimage2D` at binding `0`.
2. Each invocation stores `gx ^ gy` at its own image coordinate.
3. `memoryBarrier()` orders the invocation's memory operations and `barrier()` synchronizes the workgroup.
4. Each invocation loads four offset coordinates within its own workgroup, wrapping offsets modulo the local workgroup dimensions, and sums their `.x` components.
5. A second `memoryBarrier()` plus `barrier()` separates that read phase from the final store of the sum.
6. The host copies the output to a host-visible buffer and compares it with a CPU-generated reference image.

The representative path uses an 8×8×1 local size because the source clamps its 8×8×2 base size to the image grid. The full test also varies image type, dimensions, and scalar format.

## End-to-End Test Flow

```text
1. [host] register qualifier, image-type, and format cases
2. [host] generate GLSL for `coherent` or `volatile`, or delegate `restrict`
3. [host] create a storage image plus host-visible copyback buffer, or a storage texel buffer
4. [host] bind the resource, record image-layout/access barriers when an image is used, and dispatch compute work
5. [device] write each invocation's coordinate-derived value
6. [device] synchronize the workgroup, read four peer locations, and store the sum
7. [host] transition/copy image output when needed, invalidate the readback allocation, and compare it with the reference
```

## Generated Test Artifacts and Bound Resources

| Resource or artifact | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| Generated `coherent`/`volatile` compute shader | Yes | Yes, as the compute pipeline's shader module | Executes stores and loads | No | Places the selected qualifier on `u_image`. |
| Storage image and image view | Yes, except for buffer cases | Yes, storage-image descriptor at binding `0` | Written and read by the shader | Indirectly, after image-to-buffer copy | Covers dimensional images and layers/faces. |
| Storage texel buffer and buffer view | Yes, for `buffer` cases | Yes, storage-texel-buffer descriptor at binding `0` | Written and read by the shader | Yes | Covers buffer-image declaration behavior. |
| Host-visible copyback buffer | Yes | Transfer destination | Receives copied image output, when applicable | Yes | Supplies data to the CPU comparison. |
| CPU reference image | Yes, CPU-only | No | No | Yes | Recomputes the four-offset sum expected from the first write phase. |

## What Is Checked

- For `coherent` and `volatile`, the host compares every output layer, slice, or cube face with the reference. Integer formats require exact equality; floating-point formats use a `0.01` threshold.
- For `restrict`, the delegated `LoadStoreTest` performs its own load/store result verification for the selected image type.
- A mismatch produces `Image comparison failed` in the local qualifier implementation.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `coherent`, `volatile`, `restrict`

The test family is the primary behavioral axis: it selects the declaration semantic and, for `restrict`, the delegated load/store implementation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `coherent` | Incorrect handling of the `coherent` declaration together with the shader barriers used for the workgroup read-after-write exchange. |
| `volatile` | Incorrect handling of the `volatile` declaration or of the same synchronized image-access sequence used by the generated case. |
| `restrict` | Incorrect lowering or execution of `restrict`-qualified read/write image declarations in the delegated load/store path. |

## Important Variations and Special Cases

- `coherent` and `volatile` register eight image types: `1d`, `1d_array`, `2d`, `2d_array`, `3d`, `cube`, `cube_array`, and `buffer`. Each has `r32f`, `r32ui`, and `r32i` leaves.
- `restrict` registers one case per image type and delegates to `createImageQualifierRestrictCase`; it uses `VK_FORMAT_R32G32B32A32_UINT`, not the three-format matrix.
- `cube_array` requires `DEVICE_CORE_FEATURE_IMAGE_CUBE_ARRAY` in the local qualifier test path.
- The source uses GLSL 4.40 for the locally generated `coherent` and `volatile` shaders. The delegated restrict generator sets explicit SPIR-V 1.3 build options.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Qualifier registration and matrix | [createImageQualifiersTests](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L695-L769) | Builds the three test families, image types, formats, and delegated restrict cases. |
| Generated `coherent` and `volatile` shader | [MemoryQualifierTestCase::initPrograms](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L241-L305) | Shows the qualifier declaration, two barrier phases, and image access sequence. |
| Host dispatch and comparison | [MemoryQualifierInstanceBase::iterate](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L352-L419) | Creates the pipeline, dispatches, reads back, and returns the pass/fail result. |
| CPU reference calculation | [generateReferenceImage](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L421-L463) | Reproduces the expected four-offset sum. |
| Image resource path | [MemoryQualifierInstanceImage](../../../modules/vulkan/image/vktImageQualifiersTests.cpp#L491-L603) | Creates the storage image, performs layout/access barriers, and copies it to the readback buffer. |
| Restrict generator | [createImageQualifierRestrictCase](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L3760-L3769) | Delegates to `LoadStoreTest` with `FLAG_RESTRICT_IMAGES`. |
| Restrict declaration emission | [LoadStoreTest::makePrograms](../../../modules/vulkan/image/vktImageLoadStoreTests.cpp#L1444-L1507) | Emits `restrict` on the generated readonly and writeonly image declarations. |
| Vulkan shader memory rules | [Shaders](../../../../vulkan-docs/src/chapters/shaders.adoc#L2291-L2340) | Defines the relevant availability, visibility, barrier, and `Coherent` rules. |

## Questions / Risk Points for User Audit

- [x] The behavioral-axis conclusion distinguishes the three registered test families.
- [x] The `restrict` path is documented as delegated rather than described as the local compute-sum implementation.
- [x] The `coherent` explanation says that explicit barriers remain part of the test.
- [x] The representative walkthrough should use `coherent.2d.r32ui`, because its resource type, integer result, and local dimensions can be reconstructed exactly.
- [x] The `volatile` description remains limited to what this output-comparison test establishes; it does not claim to inspect an optimizer or cache implementation.

## Conversion Notes for Final Wiki Rewrite

- Keep the qualifier family as the final page's behavior parameter and copy the failure-cause table unchanged.
- Distill the background to qualifier semantics, barrier scope, and the delegated restrict path.
- Keep one `coherent.2d.r32ui` walkthrough because it exercises the local GLSL generator; explain `volatile` as a declaration-only variation of that generator.
- Describe the `restrict` shader path from its separate load/store builder without inventing a local shader walkthrough for it.
