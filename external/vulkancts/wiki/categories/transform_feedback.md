# transform_feedback

## Overview

The [`transform_feedback`](../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L36-L55) category documents Vulkan transform-feedback tests. Inspected files cover simple transform-feedback capture and replay patterns, graphics-pipeline-library construction variants, interface-block layout fuzzing, primitives-generated-query interactions, and primitive-restart behavior.

## Registration Entry Point

The category is rooted in [`createTests()`](../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L36-L55):

```text
transform_feedback
├── fuzz
├── primitive_restart
├── primitives_generated_query
├── simple
├── simple_fast_gpl
└── simple_optimized_gpl
```

## File Inventory

| File | Role | Notes |
|---|---|---|
| [`vktTransformFeedbackTests.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L1) | Registration | Top-level dispatcher |
| [`vktTransformFeedbackSimpleTests.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L1) | Implementation | Simple, fast GPL (graphics pipeline library), and optimized-GPL transform-feedback matrices |
| [`vktTransformFeedbackFuzzLayoutTests.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L1) | Implementation | Interface-block layout group registration |
| [`vktTransformFeedbackFuzzLayoutCase.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1) | Helper/implementation support | Fuzz-layout execution, support, and validation logic |
| [`vktTransformFeedbackRandomLayoutCase.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackRandomLayoutCase.cpp#L1) | Helper | Random layout case construction support |
| [`vktPrimitivesGeneratedQueryTests.cpp`](../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1) | Implementation | Primitives generated query and transform-feedback query interactions |
| [`vktTransformFeedbackPrimitiveRestartTests.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L1) | Implementation | Primitive restart and dynamic topology/restart matrix |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktPrimitivesGeneratedQueryTests.cpp`](../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L1) | [`vktPrimitivesGeneratedQueryTests.md`](../testfiles/transform_feedback/vktPrimitivesGeneratedQueryTests.md) |
| [`vktTransformFeedbackFuzzLayoutTests.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L1) | [`vktTransformFeedbackFuzzLayoutTests.md`](../testfiles/transform_feedback/vktTransformFeedbackFuzzLayoutTests.md) |
| [`vktTransformFeedbackPrimitiveRestartTests.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L1) | [`vktTransformFeedbackPrimitiveRestartTests.md`](../testfiles/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.md) |
| [`vktTransformFeedbackSimpleTests.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L1) | [`vktTransformFeedbackSimpleTests.md`](../testfiles/transform_feedback/vktTransformFeedbackSimpleTests.md) |
| [`vktTransformFeedbackTests.cpp`](../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L1) | [`vktTransformFeedbackTests.md`](../testfiles/transform_feedback/vktTransformFeedbackTests.md) |

## Subgroup Structure and Major Themes

- [`simple`](../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7264-L7276), [`simple_fast_gpl`](../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7267-L7274), and [`simple_optimized_gpl`](../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7267-L7274) use the same generator under different pipeline construction modes.
- [`fuzz`](../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L364-L365) covers deterministic and randomized transform-feedback interface-block layout cases.
- [`primitives_generated_query`](../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L3062-L3065) checks primitives-generated-query results, optionally cross-checking transform-feedback query counters.
- [`primitive_restart`](../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L426-L440) covers static/dynamic primitive restart and topology combinations.

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Pipeline construction | Monolithic, fast linked library, link-time optimized library in [`constructionTypes[]`](../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L42-L46) |
| Buffer count and size | `{1,2,4,8}` buffers and `{256,512,128*1024}` sizes in [`createTransformFeedbackSimpleTests()`](../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6457-L6501) |
| Stream id | Stream ids such as `{0,1,3,6,14}` in simple and stream cases |
| Query dimensions | read/reset/result type, query count, command-buffer case, query order, outside draws, and availability bit in [`testGenerator()`](../../modules/vulkan/transform_feedback/vktPrimitivesGeneratedQueryTests.cpp#L2801-L2953) |
| Interface layout | GLSL data type, precision, arrays, structs, nested structs, instance arrays, buffers, and vertex/geometry stage in [`InterfaceBlockTests::init()`](../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L372-L740) |
| Dynamic state | Dynamic primitive restart and dynamic primitive topology in [`createTransformFeedbackPrimitiveRestartTests()`](../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L432-L438) |

## Recurring Support Requirements

The central requirement is `VK_EXT_transform_feedback`, checked in [`TransformFeedbackTestCase::checkSupport()`](../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L4597-L4607), [`PrimitiveRestartCase::checkSupport()`](../../modules/vulkan/transform_feedback/vktTransformFeedbackPrimitiveRestartTests.cpp#L90-L99), and primitives-generated-query support paths. Other observed gates include `VK_KHR_get_physical_device_properties2`, `VK_EXT_primitives_generated_query`, `VK_EXT_host_query_reset`, `VK_EXT_color_write_enable`, `VK_EXT_extended_dynamic_state`, `VK_EXT_extended_dynamic_state2`, `VK_KHR_maintenance5`, `VK_KHR_draw_indirect_count`, `VK_KHR_device_address_commands`, `VK_EXT_shader_object`, geometry/tessellation shader core features, large points, shaderFloat64, multiview, pipeline statistics, inherited queries, and transform-feedback property limits.

## Recurring Verification Methods

Observed verification methods include transform-feedback buffer readback and byte/value validation, query-pool get/copy counter comparison, image comparison for draw-indirect rendering, interface-layout value validation through [`validateValues()`](../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1853-L1858), and primitive-restart counter/position validation after transform-feedback capture.


## Notes / Uncertainties

- The simple transform-feedback groups generate thousands of leaf cases from source loops. Their Level-3 page documents the three sibling top-level roots (`simple`, `simple_fast_gpl`, and `simple_optimized_gpl`) and summarizes generated leaf matrices in prose instead of duplicating every leaf case in the hierarchy tree.
