# vktPipelineEmptyFSTests.cpp

## Overview

[`vktPipelineEmptyFSTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L1) implements the [`empty_fs`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L802) topic group. It verifies pipeline behavior with empty fragment shaders, testing that pipelines with no fragment shader or an empty fragment shader work correctly for depth-only and stencil-only rendering.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineEmptyFSTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L1)
- Header: [`vktPipelineEmptyFSTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.empty_fs
├── vert_no_fs
├── vert_empty_fs
├── tess_no_fs
├── tess_empty_fs
├── geom_no_fs
├── geom_empty_fs
├── primitive_discard
└── masked_samples
```

## Test Families

### vert_no_fs — Vertex pipeline with no fragment shader

Verifies that a pipeline with a vertex shader stage but no fragment shader works correctly for depth-only rendering. The pipeline processes vertices but produces no color output.

### vert_empty_fs — Vertex pipeline with empty fragment shader

Verifies that a pipeline with a vertex shader stage and an empty fragment shader (no outputs) works correctly for depth-only rendering.

### tess_no_fs — Tessellation pipeline with no fragment shader

Verifies that a pipeline with tessellation evaluation stage but no fragment shader works correctly for depth-only rendering. Requires `tessellationShader`.

### tess_empty_fs — Tessellation pipeline with empty fragment shader

Verifies that a pipeline with tessellation evaluation stage and an empty fragment shader works correctly for depth-only rendering. Requires `tessellationShader`.

### geom_no_fs — Geometry pipeline with no fragment shader

Verifies that a pipeline with a geometry shader stage but no fragment shader works correctly for depth-only rendering. Requires `geometryShader`.

### geom_empty_fs — Geometry pipeline with empty fragment shader

Verifies that a pipeline with a geometry shader stage and an empty fragment shader works correctly for depth-only rendering. Requires `geometryShader`.

### primitive_discard — Primitive discard with no fragment shader

Verifies that primitives can be discarded in a pipeline without a fragment shader, testing depth/stencil behavior when primitives are discarded.

### masked_samples — Masked samples with no fragment shader

Verifies that sample masking works correctly in a pipeline without a fragment shader.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Fragment shader presence | Enum | No fragment shader, empty fragment shader |
| Depth/stencil attachment | Enum | Depth-only, stencil-only, depth+stencil |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| `tessellationShader` | Required for `tess_no_fs` and `tess_empty_fs` |
| `geometryShader` | Required for `geom_no_fs` and `geom_empty_fs` |
| Standard pipeline support | Basic pipeline feature support |

## Verification Methods

- **Depth/stencil verification**: Render without fragment shader, verify depth/stencil buffer contains expected values
- **No color output verification**: Verify that no color output is produced when fragment shader is absent

## Notes

- Empty fragment shader tests are important for depth-only and shadow map rendering passes
