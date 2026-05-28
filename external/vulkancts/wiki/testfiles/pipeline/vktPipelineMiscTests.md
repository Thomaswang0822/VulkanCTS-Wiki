# vktPipelineMiscTests.cpp

## Overview

[`vktPipelineMiscTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L1) implements the [`misc`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L2545) topic group. It verifies miscellaneous pipeline behaviors that don't fit into other topic groups, including implicit primitive ID passthrough, pipeline layout binding, descriptor binding with backwards/holes, identically defined layouts, no-rendering pipelines, and pipeline layout host allocation callbacks.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineMiscTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L1)
- Header: [`vktPipelineMiscTestsTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineMiscTests.hpp#L1)

## Registration Hierarchy

```text
pipeline.monolithic.misc
├── position_to_ssbo (monolithic only, amber)
├── primitive_id_from_tess (monolithic only, amber)
├── layer_read_from_frag (monolithic only, amber)
├── implicit_primitive_id
├── implicit_primitive_id_with_tessellation
├── array_of_structs_interface
├── descriptor_bind_test_backwards
├── descriptor_bind_test_holes
├── descriptor_bind_test_backwards_holes
├── identically_defined_layout (monolithic only)
├── no_rendering (non-VulkanSC only)
├── no_rendering_unused_attachment (non-VulkanSC only)
└── color_write_mask_none
```

## Test Families

### position_to_ssbo — Amber position-to-SSBO test

Amber test that writes vertex position to a storage buffer. Monolithic-only, requires `vertexPipelineStoresAndAtomics`.

### primitive_id_from_tess — Amber primitive ID from tessellation

Amber test verifying `gl_PrimitiveID` passthrough from tessellation. Monolithic-only, requires `tessellationShader` and `geometryShader`.

### layer_read_from_frag — Amber layer read from fragment shader

Amber test reading `gl_Layer` from a fragment shader without prior geometry shader writes. Monolithic-only, requires `geometryShader`.

### implicit_primitive_id — Implicit primitive ID passthrough

Verifies that `gl_PrimitiveID` is implicitly available in the fragment shader without being explicitly passed through geometry or tessellation stages.

### implicit_primitive_id_with_tessellation — Implicit primitive ID with tessellation

Verifies that `gl_PrimitiveID` is implicitly available in the fragment shader when a tessellation stage is present. Requires `tessellationShader`.

### array_of_structs_interface — Array of structs interface

Verifies pipeline behavior with array-of-structs shader interfaces between stages.

### descriptor_bind_test_backwards — Descriptor binding with backwards bindings

Verifies that pipeline layout creation works with descriptor bindings specified in reverse order.

### descriptor_bind_test_holes — Descriptor binding with holes

Verifies that pipeline layout creation works with descriptor bindings that have gaps (holes) in the binding numbers.

### descriptor_bind_test_backwards_holes — Descriptor binding with backwards and holes

Verifies that pipeline layout creation works with descriptor bindings that are both in reverse order and have gaps.

### identically_defined_layout — Identically defined pipeline layout

Verifies that identically defined pipeline layouts work correctly. Monolithic-only, guarded by `VK_KHR_maintenance4`.

### no_rendering — Pipeline with no rendering

Verifies pipeline creation and execution without any rendering (no color attachments). Non-VulkanSC only, not available for shader-object variants.

### no_rendering_unused_attachment — Pipeline with unused attachment

Verifies pipeline creation and execution with an unused attachment. Non-VulkanSC only, not available for shader-object variants.

### color_write_mask_none — Color write mask none

Verifies pipeline behavior when color write mask is set to none for all color attachments.

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | All variant types |
| Descriptor binding config | Enum | Backwards, holes, backwards+holes |
| Rendering mode | Enum | No rendering, unused attachment |

## Support / Feature Requirements

| Requirement | Context |
|---|---|
| `tessellationShader` | Required for implicit primitive ID tests |
| `geometryShader` | Required for some pipeline layout tests |
| `vertexPipelineStoresAndAtomics` | Required for `position_to_ssbo` amber test |

## Verification Methods

- **Rendering verification**: Render with miscellaneous pipeline configurations, verify correct output
- **Layout compatibility verification**: Verify that pipeline layouts with backwards bindings and holes work correctly
- **Allocation callback verification**: Verify that host allocation callbacks are correctly invoked

## Notes

- The `identically_defined_layout` test is conditionally registered (monolithic only)
- Amber tests (`position_to_ssbo`, `primitive_id_from_tess`, `layer_read_from_frag`) are monolithic-only
- This is a catch-all group for pipeline tests that don't fit other topic categories
