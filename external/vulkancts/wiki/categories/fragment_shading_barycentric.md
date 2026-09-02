## Overview

The `fragment_shading_barycentric` test category checks barycentric fragment inputs for per-vertex data and interpolation weights across topology, provoking-vertex, interpolation, data-type, shader-stage, sample, and pipeline-construction variants.

## Background Knowledge

- **Barycentric coordinates.** A fragment inside a triangle can be described by three weights whose sum is one. Applying them to known vertex values reconstructs an interpolated value.
- **Provoking vertex.** Flat-qualified data comes from a selected provoking vertex, while interpolated data depends on the fragment position and all relevant vertices.
- **Pipeline construction.** Monolithic and graphics-pipeline-library paths assemble the same graphics behavior through different pipeline objects.

## Category Structure

```text
fragment_shading_barycentric
├── data
├── weights
├── pipeline_library
└── fast_linked_library
```

The pipeline-library roots contain their own `data` and `weights` branches; the default root contains the monolithic equivalents.

## How the Families Fit Together

- `data` checks barycentric access to known per-vertex values.
- `weights` checks the barycentric weights themselves through a reference rendering.
- `pipeline_library` and `fast_linked_library` repeat these behaviors with alternate graphics-pipeline construction.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `data`, `weights`, and pipeline-library variants | [Tests.md](../testfiles/fragment_shading_barycentric/Tests.md) | Barycentric data and weight semantics, stage/topology variation, support, and image verification |

## Category Notes

The default Vulkan mustpass contains 20,991 leaves. The category page keeps only category-level relationships; the complete parameter matrix and shader behavior are documented on the Level-3 page.
