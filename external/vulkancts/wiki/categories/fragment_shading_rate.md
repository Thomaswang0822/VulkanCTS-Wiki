## Overview

The `fragment_shading_rate` test category checks that Vulkan uses the requested fragment shading rate across render-pass, dynamic-rendering, attachment, basic, miscellaneous, and pixel-consistency cases.

## Background Knowledge

- **Fragment shading rate.** A fragment shading rate controls the pixel area covered by one fragment invocation, such as `1x1`, `2x2`, or `4x4` pixels.
- **Shading-rate attachment.** A shading-rate attachment supplies per-region rate information through an image. Attachment setup, image layout, and queue ownership affect whether the rate reaches the rendering operation.
- **Dynamic and static state.** A rate may come from pipeline state or a dynamic command. The category compares those state sources and also checks dynamic rendering and secondary-command-buffer paths.

## Category Structure

```text
fragment_shading_rate
├── renderpass2
└── dynamic_rendering
```

The implementation places `basic`, `attachment_rate`, `pixel_consistency`, and `misc` beneath these rendering-path roots. Vulkan SC excludes the dynamic-rendering branch.

## How the Families Fit Together

- `basic` tests dynamic and static shading-rate state across a broad rendering matrix.
- `attachment_rate` tests how shading-rate attachment data is created, transferred, bound, and consumed.
- `pixel_consistency` checks that pixels within one selected fragment-sized region remain consistent.
- `misc` covers limits, reported-rate lists, attachment transitions, no-fragment-shader behavior, out-of-bounds attachment access, and maintenance cases.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `basic` | [Basic.md](../testfiles/fragment_shading_rate/Basic.md) | Dynamic/static state, rate matrix, shader behavior, and result checks |
| `attachment_rate` | [AttachmentRate.md](../testfiles/fragment_shading_rate/AttachmentRate.md) | Shading-rate attachment setup, queue/resource paths, and validation |
| `pixel_consistency` | [PixelConsistency.md](../testfiles/fragment_shading_rate/PixelConsistency.md) | `rate_1x1` through `rate_4x4` region consistency |
| `misc` | [Misc.md](../testfiles/fragment_shading_rate/Misc.md) | Limits, rate lists, out-of-bounds access, and special rendering behavior |

## Category Notes

The default Vulkan mustpass contains 110,363 leaves. Each Level-3 page records its own complete ownership boundary for the relevant rendering-path subtree.
