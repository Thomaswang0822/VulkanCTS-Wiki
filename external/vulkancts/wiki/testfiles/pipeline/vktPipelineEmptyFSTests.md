# vktPipelineEmptyFSTests.cpp

## Overview

[`vktPipelineEmptyFSTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L1) implements the [`empty_fs`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L802) topic group. It verifies pipeline behavior with empty fragment shaders, testing that pipelines with no fragment shader or an empty fragment shader work correctly for depth-only and stencil-only rendering.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineEmptyFSTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L1)
- Header: [`vktPipelineEmptyFSTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.hpp#L1)

## Registration Path

[`createEmptyFSTests()`](../../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L800) returns the `empty_fs` group, attached under each variant root by `createChildren()`.

**Variant coverage**: All variants.

## Test Hierarchy

```text
empty_fs
└── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| EmptyFSTest | Verifies pipeline behavior with empty or missing fragment shader |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Fragment shader presence | Enum | No fragment shader, empty fragment shader |
| Depth/stencil attachment | Enum | Depth-only, stencil-only, depth+stencil |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| Standard pipeline support | Basic pipeline feature support |

## Verification Methods

- **Depth/stencil verification**: Render without fragment shader, verify depth/stencil buffer contains expected values
- **No color output verification**: Verify that no color output is produced when fragment shader is absent

## Notes

- Empty fragment shader tests are important for depth-only and shadow map rendering passes
