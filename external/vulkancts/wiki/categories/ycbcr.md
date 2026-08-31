## Overview

The `ycbcr` test category collects tests that check Vulkan YCbCr image formats, plane access, sampling conversion, transfers, and related image metadata behavior.

## Background Knowledge

- **Multi-planar images and compatible plane formats.** A multi-planar image stores luma and chroma in separate planes. Vulkan can expose an individual plane through its compatible single-plane format, which lets tests reason about plane layout, sampling, and storage access without treating the image as an ordinary packed texel format.
- **Sampler YCbCr conversion.** A `VkSamplerYcbcrConversion` defines how a sampler interprets a multi-planar image: chroma locations and reconstruction, range and color model, and component mapping. The sampled result is a converted color, while plane-view and transfer tests can inspect the underlying plane representation instead.
- **Disjoint image memory.** With `VK_IMAGE_CREATE_DISJOINT_BIT`, each plane can be bound separately. This changes memory binding and plane-aspect operations, but it does not turn the planes into independent test categories; the logical image and its format still define their relationship.
- **Image subresource layouts and dependencies.** A subresource layout reports how an image plane is arranged in memory. Image layout transitions and transfer or shader-access dependencies determine when writes can be consumed by later operations. These concepts are shared by the plane-layout, copy, storage-write, and shader-backed families.

## Category Structure

```text
ycbcr
├── format
├── filtering
├── plane_view
├── query
├── conversion
├── copy
├── single_plane_copy
├── copy_dimensions
├── storage_image_write
├── subresource_offset
└── misc
```

The registration-only dispatcher [`populateTestGroup()`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44-L58) creates these direct test families. The dispatcher itself is folded into this Level-2 gateway rather than represented by a separate rewritten implementation page.

## How the Families Fit Together

The families test different ways a Vulkan implementation exposes or uses YCbCr images:

- **Format and filtering:** `format` samples the supported format matrix through sampler conversion, while `filtering` focuses on chroma reconstruction and its nearest or linear filter choice.
- **Views and queries:** `plane_view` checks plane-compatible views and aliases, while `query` checks shader image metadata such as extent and mip-level count.
- **Conversion and transfers:** `conversion` checks sampled color conversion and reconstruction. `copy`, `single_plane_copy`, and `copy_dimensions` check byte-preserving image transfers across plane, tiling, and dimension variants.
- **Storage and layout:** `storage_image_write` writes plane-compatible storage images from compute. `subresource_offset` checks per-plane linear-image offsets. `misc` currently covers the relaxed-precision sampling case.

Together, the families cover both the logical sampled-color view of YCbCr and the underlying plane, memory, and transfer behavior.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `format` | [Format.md](../testfiles/ycbcr/Format.md) | Format matrix, image setup, shader sampling, software-reference comparison, and support pruning. |
| `filtering` | [Filtering.md](../testfiles/ycbcr/Filtering.md) | Chroma-filter variants, graphics and compute sampling paths, bounds checking, and failure meaning. |
| `plane_view` | [View.md](../testfiles/ycbcr/View.md) | Plane-compatible image views, disjoint memory aliases, shader access, and comparison rules. |
| `query` | [ImageQuery.md](../testfiles/ycbcr/ImageQuery.md) | `size_lod` and `levels` image queries across supported shader stages and image variants. |
| `conversion` | [Conversion.md](../testfiles/ycbcr/Conversion.md) | Color models, ranges, chroma reconstruction, sampler arrays, shader sampling, and precision bounds. |
| `copy`, `single_plane_copy`, `copy_dimensions` | [Copy.md](../testfiles/ycbcr/Copy.md) | Per-plane image copies, fixed single-plane directions, large dimensions, and byte-level checking. |
| `storage_image_write` | [StorageImageWrite.md](../testfiles/ycbcr/StorageImageWrite.md) | Joint and disjoint plane storage writes from compute and readback validation. |
| `subresource_offset` | [ImageOffset.md](../testfiles/ycbcr/ImageOffset.md) | Separate plane bindings and the required zero subresource offsets for linear disjoint images. |
| `misc.relaxed_precision` | [Misc.md](../testfiles/ycbcr/Misc.md) | CTS-authored SPIR-V relaxed-precision sampling and its result check. |

## Category Notes

- The exact generated case inventory depends on device format features, image usage support, extensions, shader-executor stage support, and device limits. The registration tree above identifies the direct families; each Level-3 page documents its deeper generated cases.
- The `copy`, `single_plane_copy`, and `copy_dimensions` families share one implementation file and one rewritten page because they exercise related image-copy mechanisms while varying the workload and stress dimension.
- The top-level dispatcher also routes the category's support helpers and shared image utilities; those helpers are evidence for the family pages, not additional user-facing test families.
