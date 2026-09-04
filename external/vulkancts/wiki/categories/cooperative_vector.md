## Overview

The `cooperative_vector` category covers cooperative-vector arithmetic, matrix operations, training operations, and host/device matrix conversions. Its six direct families are implemented by separate child groups, while the dispatcher page documents routing only.

## Background Knowledge

- **Cooperative-vector properties:** The implementation advertises supported component types, sizes, and interpretations. Generated cases use these properties to decide which operations can execute.
- **Matrix interpretation and layout:** Component interpretation and layout describe how logical matrix values are represented. Conversion tests check that values remain usable when either representation changes.
- **Execution stages:** Generated operations can target compute, graphics, mesh, or ray-tracing stages when the selected device features support those stages.

## Category Structure

```text
cooperative_vector
├── basic
├── longvec
├── matmul
├── training
├── layoutconvert
└── typeconvert
```

The `basic`, `longvec`, `matmul`, and `training` families are documented together on [Basic](../testfiles/cooperative_vector/Basic.md). The conversion families are documented together on [Matrix](../testfiles/cooperative_vector/Matrix.md). The category root and its registration-only dispatcher are described here rather than on a separate Level-3 page.

## How the Families Fit Together

- Read [Basic](../testfiles/cooperative_vector/Basic.md) for vector operations, long-vector spelling, matrix multiplication, and training accumulation.
- Read [Matrix](../testfiles/cooperative_vector/Matrix.md) for host/device layout conversion and component-type conversion.
- The category root and six direct factory routes are recorded in `Category Structure`. Executable behavior belongs to [Basic](../testfiles/cooperative_vector/Basic.md) and [Matrix](../testfiles/cooperative_vector/Matrix.md).

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `basic`, `longvec`, `matmul`, and `training` | [Basic](../testfiles/cooperative_vector/Basic.md) | Generated operations, stages, storage paths, support gates, result checks, pruning, and failure mapping. |
| `layoutconvert` and `typeconvert` | [Matrix](../testfiles/cooperative_vector/Matrix.md) | Host/device matrix conversion, supported interpretations, quantization, and failure meaning. |

## Category Notes

The Level-3 filenames are shortened CamelCase names: `CooperativeVector`, `Basic`, and `Matrix`. They omit the `vkt` prefix and trailing `Tests` suffix.
