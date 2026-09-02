## Overview

The `fragment_shader_interlock` test category collects cases that check ordered fragment access to overlapping pixel, sample, and shading-rate regions.

## Background Knowledge

- **Fragment shader interlock.** An interlock region orders fragment invocations that access the same rasterization region, allowing a shader to perform a read-modify-write without losing a conflicting update.
- **Interlock scopes.** Pixel-ordered, sample-ordered, and shading-rate-ordered regions define different sets of fragments that must be serialized.
- **Discard and sample shading.** Discard removes a fragment's normal output, while sample shading changes fragment invocation frequency. Both affect the writes observed by the interlock checks.

## Category Structure

```text
fragment_shader_interlock
└── basic
```

The `basic` test family contains image and SSBO cases with discard and nodiscard variants.

## How the Families Fit Together

The category has one implementation-bearing family. It varies interlock scope, destination resource, discard behavior, sample count, sample shading, and render dimensions within that family.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `basic` | [Basic.md](../testfiles/fragment_shader_interlock/Basic.md) | Interlock scopes, image/SSBO read-modify-write, discard and sample variants, and result checking |

## Category Notes

The dispatcher page is registration-only. The implementation page owns the generated matrix and its Vulkan execution semantics. The default Vulkan mustpass contains 576 leaves.
