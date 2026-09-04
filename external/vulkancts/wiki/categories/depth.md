## Overview

The `depth` category covers rasterization depth behavior exercised by eight Amber-backed cases. The cases vary fragment depth clamping, out-of-range depth, early fragment tests, depth bias, and unrestricted depth range.

## Background Knowledge

- **Viewport depth mapping:** Rasterized depth is transformed into the viewport depth range before depth testing and storage.
- **Depth clamp:** Clamping limits values that would otherwise lie outside the supported depth range.
- **Unrestricted depth range:** The unrestricted-range behavior changes which out-of-range depth values may be represented.
- **Depth bias:** Bias changes the rasterized depth value before the test observes the resulting depth behavior.
- **Amber recipes:** Amber files define the render setup, shaders, expected color, and expected depth observations. The CTS wrapper registers the cases and supplies shared support checks.

## Category Structure

```text
depth
├── fs_clamp
├── out_of_range
├── ez_fs_clamp
├── bias_fs_clamp
├── bias_outside_range
├── bias_outside_range_fs_clamp
├── out_of_range_unrestricted
└── bias_outside_range_fs_clamp_unrestricted
```

All eight direct cases are documented together on [Amber](../testfiles/depth/Amber.md) because they share the same implementation and Amber execution boundary.

## How the Families Fit Together

- The clamp cases observe ordinary fragment-depth clamping, including the early-fragment-test variant.
- The out-of-range cases exercise depth values outside the ordinary viewport range, with and without unrestricted depth range.
- The bias cases add rasterization depth bias and then observe whether the biased value is clamped or remains outside the viewport range.
- The Amber recipes define expected color and depth results; the wrapper controls registration and common support requirements.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| All eight direct `depth` cases | [Amber](../testfiles/depth/Amber.md) | Registration, Amber recipe mapping, depth operation parameters, support requirements, execution flow, and failure meaning. |

## Category Notes

The category has one implementation-bearing Level-3 page. `Amber.md` is the shortened CamelCase name derived from `vktAmberDepthTests.cpp`.
