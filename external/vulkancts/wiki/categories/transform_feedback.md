## Overview

The `transform_feedback` test category collects tests that check transform-feedback capture, its buffer layout and counters, and its interaction with primitive generation, pipeline state, and query results.

## Background Knowledge

- **Transform feedback** captures outputs from the last pre-rasterization shader stage into application-provided buffers. Buffer number, byte offset, and stride determine where each captured output is written; the layout cases and simple capture cases depend on this relationship.
- **Primitive assembly and generated primitives** determine what a draw produces before rasterization. This is needed to interpret both primitive-restart capture results and primitives-generated query counts.
- **Vulkan query results** are stored asynchronously in query pools and can be read by the host or copied to a buffer. Query reset, result width, availability, and synchronization affect how the query-oriented pages interpret a result.

## Category Structure

```text
transform_feedback
├── fuzz
├── primitive_restart
├── primitives_generated_query
├── simple
├── simple_fast_gpl
└── simple_optimized_gpl
```

The `simple`, `simple_fast_gpl`, and `simple_optimized_gpl` test families share one implementation-oriented Level-3 page because they exercise the same generated matrix under different graphics-pipeline construction modes.

## How the Families Fit Together

The families observe different parts of the same transform-feedback data path:

- **when** capture is laid out across scalar, aggregate, or multiple-buffer outputs, `fuzz` checks the generated interface-block layout and captured values;
- **when** indexed primitive assembly changes because of restart state or topology state, `primitive_restart` checks the captured positions and capture counter;
- **when** the question is how many primitives the pipeline generated, `primitives_generated_query` checks query-pool results and their interaction with transform-feedback queries;
- **when** the capture operation itself is varied, the `simple` family checks basic output capture, resume, streams, built-in outputs, indirect consumers, synchronization, and graphics-pipeline-library construction paths.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `simple`, `simple_fast_gpl`, `simple_optimized_gpl` | [Simple](../testfiles/transform_feedback/Simple.md) | Shared generated capture matrix, pipeline construction variants, resume, streams, indirect draws, built-in outputs, and host-side validation. |
| `fuzz` | [FuzzLayout](../testfiles/transform_feedback/FuzzLayout.md) | Deterministic and seeded-random interface-block layouts, recursive aggregate packing, and captured-value validation. |
| `primitive_restart` | [PrimitiveRestart](../testfiles/transform_feedback/PrimitiveRestart.md) | Static and dynamic primitive-restart/topology state and its observable transform-feedback output. |
| `primitives_generated_query` | [PrimitivesGeneratedQuery](../testfiles/transform_feedback/PrimitivesGeneratedQuery.md) | Host-read and device-copy query results, reset/readback variants, query ordering, stream selection, and concurrent query cases. |

## Category Notes

The preserved `vkt*.md` files are the original source-navigation pages. The shortened CamelCase pages above are the rewritten English documents; the dispatcher itself is represented by this category gateway rather than by an additional technical Level-3 page.
