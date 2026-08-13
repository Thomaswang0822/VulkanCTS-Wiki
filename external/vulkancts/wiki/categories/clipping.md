## Overview

The `clipping` test category collects tests that check fixed clip-volume behavior, depth clamp and explicit depth clip control, large-point and wide-line clipping, shader-defined clip and cull distances, clip-distance complementarity, and a cull-distance half-space corner case.

## Background Knowledge

- Vulkan clips primitives against a fixed clip volume defined by the viewport and depth range. Primitives fully inside are rendered; primitives fully outside are discarded; intersecting primitives are cut so only the inside portion remains. The depth range establishes near and far clip planes.
- When `depthClampEnable` is set in pipeline state, fragments whose depth falls outside the depth range are clamped to the nearest bound instead of being clipped away. `VK_EXT_depth_clip_enable` allows decoupling depth clamp from depth clipping so that clamping and clipping can be controlled independently.
- Shaders can declare `gl_ClipDistance[]` and `gl_CullDistance[]` arrays as `gl_PerVertex` built-ins. Each component defines a half-space: a negative value places the vertex outside that half-space. If all vertices of a primitive are negative for the same clip-distance component, the primitive is clipped. If all vertices are negative for the same cull-distance component, the primitive is culled entirely.

## Category Structure

```text
clipping
├── clip_volume
├── user_defined
├── complementarity
└── misc
```

All four families are registered from one implementation file and covered by a single Level-3 page. `clip_volume` contains `inside`, `outside`, `depth_clamp`, `depth_clip`, and `clipped` (large points, wide lines) sub-groups. `user_defined` contains `clip_distance`, `clip_cull_distance`, each with a `_dynamic_index` variant, expanded across vertex, tessellation, geometry, and combined shader-stage groups. `complementarity` registers cases `1` through `8`. `misc` registers one case.

## How the Families Fit Together

The category separates fixed-function clip behavior from shader-defined clip behavior:

- **`clip_volume`** tests the fixed clip volume with pipeline-controlled depth clamp and explicit depth clip. It also covers large-point and wide-line clipping edge cases.
- **`user_defined`** tests shader-written `gl_ClipDistance[]` and `gl_CullDistance[]` across clip/cull count combinations, indexing modes, shader stages, and optional fragment-shader readback.
- **`complementarity`** verifies that two primitive sets with opposite clip-distance signs together cover the framebuffer exactly once through blending.
- **`misc`** verifies that a triangle where no single cull-distance half-space is negative for all vertices is drawn, not culled.

The first family validates the fixed-function pipeline; the remaining three validate shader-defined distance behavior and its interaction with the clipper.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `clip_volume` (inside, outside, depth_clamp, depth_clip, clipped) | [ClippingTests.md](../testfiles/clipping/ClippingTests.md) | Fixed clip-volume behavior, depth clamp/clip pipeline state, topology matrix, large-point and wide-line clipping. |
| `user_defined` (clip_distance, clip_cull_distance, dynamic indexing, fragment read) | [ClippingTests.md](../testfiles/clipping/ClippingTests.md) | Generated shader shape for `gl_ClipDistance[]` and `gl_CullDistance[]`, stage combinations, clip/cull count matrix, indexing mode, and fragment-shader readback. |
| `complementarity` (cases 1–8) | [ClippingTests.md](../testfiles/clipping/ClippingTests.md) | Blended clip-distance complementarity test and gray-pixel verification. |
| `misc` (negative_and_non_negative_cull_distance) | [ClippingTests.md](../testfiles/clipping/ClippingTests.md) | Cull-distance half-space corner case where no single half-space is negative for all vertices. |
