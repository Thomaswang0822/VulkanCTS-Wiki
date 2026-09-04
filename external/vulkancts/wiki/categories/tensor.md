## Overview

The `tensor` category covers Vulkan tensor creation, memory requirements, copying, shader access, dimension queries, array access, boolean operations, and graphics-pipeline integration.

## Background Knowledge

- **Tensor descriptors:** A tensor is described by an element format, rank, dimensions, tiling, and, for linear storage, byte strides.
- **Tensor views and access:** Shader declarations and tensor operations must agree with the view's element type and rank, and each coordinate must be inside its dimension.
- **Linear and optimal tiling:** Linear tensors can expose packed or explicitly padded strides. Optimal tensors use an implementation-defined layout.
- **Tensor memory flow:** Copy, shader-access, and rendering tests exercise tensor resources together with buffers or images. Synchronization and host invalidation make device writes visible before comparison.

## Category Structure

```text
tensor
├── creation_and_requirements
├── copies
├── basic_access
├── dimension_query
├── array_access
├── graphics_pipeline
└── boolean
```

Each direct subgroup has one implementation-bearing Level-3 page. The `basic_access` page uses `BasicShaderAccess` to distinguish it from other Basic-style names.

## How the Families Fit Together

- Read [CreateRequirements](../testfiles/tensor/CreateRequirements.md) for tensor creation and memory-requirement queries.
- Read [Copies](../testfiles/tensor/Copies.md) for tensor-to-tensor transfers. Read [BasicShaderAccess](../testfiles/tensor/BasicShaderAccess.md) or [ArrayAccess](../testfiles/tensor/ArrayAccess.md) for shader reads and writes.
- Read [DimensionQuery](../testfiles/tensor/DimensionQuery.md) and [Bool](../testfiles/tensor/Bool.md) for dimension queries and boolean tensor operations.
- Read [GraphicsPipeline](../testfiles/tensor/GraphicsPipeline.md) for vertex and fragment tensor access and rendered-image validation.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `creation_and_requirements` | [CreateRequirements](../testfiles/tensor/CreateRequirements.md) | Tensor descriptions, supported formats and tilings, creation, and memory-requirement checks. |
| `copies` | [Copies](../testfiles/tensor/Copies.md) | Tensor copy directions, compatible formats, layouts, synchronization, and data comparison. |
| `basic_access` | [BasicShaderAccess](../testfiles/tensor/BasicShaderAccess.md) | Compute shader tensor reads and writes, rank and stride variants, staging, DMA, and failure mapping. |
| `dimension_query` | [DimensionQuery](../testfiles/tensor/DimensionQuery.md) | Shader-side dimension queries across registered ranks, shapes, formats, and tilings. |
| `array_access` | [ArrayAccess](../testfiles/tensor/ArrayAccess.md) | Tensor-array reads and writes, indexing, and result checks. |
| `graphics_pipeline` | [GraphicsPipeline](../testfiles/tensor/GraphicsPipeline.md) | Vertex and fragment tensor access, image-shape variants, rendering flow, and pixel validation. |
| `boolean` | [Bool](../testfiles/tensor/Bool.md) | Boolean tensor operations and shader and host-side comparisons. |

## Category Notes

The Level-3 names are `CreateRequirements`, `Copies`, `BasicShaderAccess`, `DimensionQuery`, `ArrayAccess`, `GraphicsPipeline`, and `Bool`. They use shortened CamelCase names derived from the implementation stems.
