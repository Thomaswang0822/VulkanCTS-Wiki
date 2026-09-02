## Overview

The `drm_format_modifiers` test category checks image modifier discovery, DRM-modifier image creation, external-memory binding, export/import, and pixel preservation.

## Background Knowledge

- **DRM format modifier.** A DRM modifier describes how an image's pixels are laid out in memory. Vulkan queries supported modifiers and uses the selected modifier when creating or importing an image.
- **Per-plane layout.** A multi-plane modifier image can expose a separate offset and pitch for each plane. Explicit-modifier creation must reproduce those plane layouts consistently.
- **External memory.** Export/import cases pass image memory through opaque file descriptors or dma-buf handles, then verify that the imported image retains the intended contents.

## Category Structure

```text
drm_format_modifiers
├── list_modifiers
├── list_modifiers_fmt_features2
├── list_modifiers_consistency
├── create_list_modifiers
├── create_list_modifiers_fmt_features2
├── bound_to_dma_buf
├── create_explicit_modifier
├── create_explicit_modifier_fmt_features2
├── export_import
├── export_import_fmt_features2
├── export_import_with_suballoc
└── export_import_fmt_features2_with_suballoc
```

All twelve direct families are implemented and registered by `vktModifiersTests.cpp`.

## How the Families Fit Together

- The list families query modifier metadata through legacy and `VK_KHR_format_feature_flags2` structures, while the consistency family compares the two query paths.
- The create families use queried modifier lists or explicit per-plane layouts to construct images.
- `bound_to_dma_buf` checks dma-buf binding and export. The export/import families check opaque-FD round trips, including suballocation variants.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| All twelve DRM modifier families | [Modifiers.md](../testfiles/drm_format_modifiers/Modifiers.md) | Modifier metadata, image creation, external memory, suballocation, and pixel verification |

## Category Notes

The default Vulkan mustpass contains 1,572 leaves. Each direct family iterates over 131 `formats::basicColorFormats` format leaves; modifier values are queried at runtime rather than selected from a fixed list.
