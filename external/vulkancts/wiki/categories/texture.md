## Overview

The `texture` test category collects tests that check sampled-image lookup, image-format conversion, texel addressing, mip selection, multisample access, and related sampler behavior.

The category combines generated C++ matrices with focused Amber recipes. Its pages explain the contract each family observes rather than mirroring the source-file layout.

## Background Knowledge

- **Image views and sampled access.** A Vulkan image view selects an image subresource range and format interpretation. A sampler then controls filtering, address modes, mip selection, comparison, and optional anisotropy for sampled-image instructions.
- **Coordinates, footprints, and LOD.** Normalized coordinates identify positions relative to an image extent. Derivatives or explicit gradients define a texture footprint, which determines minification, magnification, and mip-level selection. Explicit LOD and texel-fetch instructions bypass parts of that implicit calculation.
- **Format conversion.** The view format defines how stored bits become shader-visible components. This includes normalized conversion, sRGB transfer, packed-field extraction, compressed-block decoding, and component swizzling.
- **Precision-aware verification.** Vulkan permits bounded implementation precision in coordinate interpolation, LOD, filtering, and format conversion. Many texture tests therefore accept a set or interval of legal results instead of comparing against one ideal floating-point value.
- **Sparse and ordinary backing.** Some families run the same logical image operation with ordinary memory or fully resident sparse bindings. The operation under test stays the same while resource creation, binding, and upload paths differ.

## Category Structure

```text
texture
├── filtering
├── mipmap
├── explicit_lod
├── shadow
├── filtering_anisotropy
├── compressed
├── compressed_3D
├── swizzle
├── conversion
├── subgroup_lod
├── texel_buffer
├── multisample
└── texel_offset
```

`compressed` and `compressed_3D` share one Level-3 page because the same implementation owns both direct families. The registration-only texture dispatcher is represented here rather than receiving a separate Level-3 page.

## How the Families Fit Together

The families isolate different points in the path from stored image data to a shader-visible result.

- **Lookup and level selection:** `filtering`, `mipmap`, `explicit_lod`, `shadow`, `filtering_anisotropy`, `subgroup_lod`, and `texel_offset` vary coordinates, footprints, sampler state, comparison, or explicit level controls.
- **Stored representation:** `compressed`, `compressed_3D`, `conversion`, and `texel_buffer` check how encoded bits or formatted elements become shader values.
- **View interpretation:** `swizzle` checks component selection and shader-side coordinate rearrangement.
- **Per-sample access:** `multisample` addresses individual storage-image samples and applies atomics or out-of-range sample operands.

Together, the pages cover resource interpretation, coordinate and LOD rules, sampler behavior, and the verification paths that decide whether each observed result is permitted.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `filtering` | [Filtering](../testfiles/texture/Filtering.md) | Normalized and unnormalized 2D, cube, array, and 3D sampling across filters, address modes, formats, and coordinate spans. |
| `mipmap` | [Mipmap](../testfiles/texture/Mipmap.md) | Implicit and explicit mip selection, LOD clamps, view level ranges, image-view minimum LOD, and gather behavior. |
| `explicit_lod` | [FilteringExplicitLod](../testfiles/texture/FilteringExplicitLod.md) | `textureLod` and `textureGrad` with interval-based filtering verification. |
| `shadow` | [Shadow](../testfiles/texture/Shadow.md) | Depth-comparison sampling, PCF result ranges, cube handling, sparse variants, and border texel replacement. |
| `filtering_anisotropy` | [FilteringAnisotropy](../testfiles/texture/FilteringAnisotropy.md) | Anisotropic versus isotropic output across single-level and mipmapped graphics or compute cases. |
| `compressed`, `compressed_3D` | [CompressedFormat](../testfiles/texture/CompressedFormat.md) | ETC2/EAC, ASTC, and BC block decoding for 2D or 3D images, including sparse and ASTC special cases. |
| `swizzle` | [Swizzle](../testfiles/texture/Swizzle.md) | Image-view component mapping and shader-side coordinate swizzles. |
| `conversion` | [Conversion](../testfiles/texture/Conversion.md) | UFLOAT storage conversion and SNORM endpoint behavior under direct or linear-filtered sampling. |
| `subgroup_lod` | [SubgroupLod](../testfiles/texture/SubgroupLod.md) | Vertex-stage `texelFetch`, `textureGrad`, and `textureLod` selection using mip-colored Amber images. |
| `texel_buffer` | [TexelBuffer](../testfiles/texture/TexelBuffer.md) | sRGB, packed-format, and SNORM conversion through uniform texel-buffer views. |
| `multisample` | [Multisample](../testfiles/texture/Multisample.md) | Per-sample storage-image atomics and mixed valid/out-of-range sample writes. |
| `texel_offset` | [TexelOffset](../testfiles/texture/TexelOffset.md) | Constant one-texel offsets with nearest sampling and a four-direction result mask. |

## Category Notes

- The current `filtering` implementation does not register sparse leaves, although related texture families do exercise sparse backing.
- `subgroup_lod` is a historical registration name; its shaders vary LOD inputs between vertex invocations but do not use subgroup operations.
- `multisample` documents unresolved source-level defects found during reconstruction. Those findings do not authorize source changes in this documentation workflow.
