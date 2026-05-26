# vktTransformFeedbackSimpleTests.cpp

## Overview

[`vktTransformFeedbackSimpleTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L1) provides the implementation used by the three top-level simple transform-feedback groups: `simple`, `simple_fast_gpl`, and `simple_optimized_gpl`. The category root registers the same factory three times with different GPL (graphics pipeline library) construction modes in [`constructionTypes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L40-L49), and this file maps those construction modes to the three registered group names in [`groupNameSuffix`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7264-L7276).

The MUSTPASS file confirms these are separate sibling roots, not descendants of `simple`: [`simple`](../../../mustpass/main/vk-default/transform-feedback.txt#L110039) has 7894 `dEQP-VK.transform_feedback.simple.` entries, while [`simple_fast_gpl`](../../../mustpass/main/vk-default/transform-feedback.txt#L117933) and [`simple_optimized_gpl`](../../../mustpass/main/vk-default/transform-feedback.txt#L125819) have 7886 entries each.

## Role

Implementation file. It creates three top-level category children through a construction-type-dependent group name and then fills each group with generated transform-feedback test cases.

## Source Code

- Primary source: [`vktTransformFeedbackSimpleTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L1)
- Root registration caller: [`vktTransformFeedbackTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L40-L49)
- MUSTPASS evidence: [`transform-feedback.txt`](../../../mustpass/main/vk-default/transform-feedback.txt#L110039)

## Registration Hierarchy

```text
transform_feedback
├── simple
├── simple_fast_gpl
└── simple_optimized_gpl
```

The hierarchy above intentionally documents the three direct category children registered through this source file. It does not expand all generated leaf cases under those roots because the source file has no additional registered subgroup files at that depth; the leaf matrices are described in `## Test Families` and are backed by source loops and MUSTPASS counts.

## Test Families

### simple — Monolithic pipeline construction

The `simple` group is produced when [`createTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L40-L49) passes `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` to [`createTransformFeedbackSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7264-L7276). The empty suffix in [`groupNameSuffix`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7267-L7274) makes the registered group name `simple`. MUSTPASS entries beginning at [`transform-feedback.txt#L110039`](../../../mustpass/main/vk-default/transform-feedback.txt#L110039) confirm the `dEQP-VK.transform_feedback.simple.` prefix.

The monolithic group includes the same broad generator families as the GPL variants plus source-observed cases that are emitted only for monolithic construction. The monolithic-only guards add device-address-command variants for the seven basic test types when `partCount == 2` and `bufferSize == 256` in [`createTransformFeedbackSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6511-L6518), plus the shader-object rebind case in [`createTransformFeedbackSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6977-L6984). Together these source-observed monolithic-only registrations account for why this root has 7894 observed MUSTPASS entries while each GPL sibling has 7886.

### simple_fast_gpl — Fast linked graphics pipeline library construction

The `simple_fast_gpl` group is produced when the root dispatcher passes `PIPELINE_CONSTRUCTION_TYPE_FAST_LINKED_LIBRARY` in [`constructionTypes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L42-L46). The suffix map appends `_fast_gpl` in [`groupNameSuffix`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7267-L7274). MUSTPASS entries beginning at [`transform-feedback.txt#L117933`](../../../mustpass/main/vk-default/transform-feedback.txt#L117933) confirm the `dEQP-VK.transform_feedback.simple_fast_gpl.` prefix.

### simple_optimized_gpl — Link-time optimized graphics pipeline library construction

The `simple_optimized_gpl` group is produced when the root dispatcher passes `PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY` in [`constructionTypes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L42-L46). The suffix map appends `_optimized_gpl` in [`groupNameSuffix`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7267-L7274). MUSTPASS entries beginning at [`transform-feedback.txt#L125819`](../../../mustpass/main/vk-default/transform-feedback.txt#L125819) confirm the `dEQP-VK.transform_feedback.simple_optimized_gpl.` prefix.

### basic_* / resume_* — Basic capture and resume

The basic matrix combines test types such as `basic`, `resume`, point size, clip/cull distance, and draw-outside with buffer counts `{1,2,4,8}` and buffer sizes `{256,512,128*1024}` in [`createTransformFeedbackSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6455-L6529). Cases are emitted by [`addTransformFeedbackTestCaseVariants()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6430-L6452), which may add `_ptsz` variants when point-size alternatives are generated.

### draw_indirect_* — Draw-indirect and counter-buffer variants

Draw-indirect variants combine multiview, counter offset, counter-buffer offset, and vertex strides from explicit arrays and loops in [`createTransformFeedbackSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6558-L6626).

### query_* / multiquery_* — Transform-feedback query cases

Query cases vary stream ids, vertex counts, query width, copy/get/reset behavior, and topology in the loops around [`usedStreamId[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6681-L6691) and multi-query stream handling in [`createTransformFeedbackStreamsSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7105-L7153).

### streams_* / multistreams_* — Geometry-stream capture

Stream cases use nonzero stream ids and test point size, clip/cull distance, multistream capture, same-location output, and single-raster cases in [`createTransformFeedbackStreamsSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7004-L7239).

### holes_* / max_output_components_* — Layout holes and output component limits

Holes cases skip components in transform-feedback buffers, and max-output-components cases write many vertex outputs using `TEST_TYPE_MAX_OUTPUT_COMPONENTS` in [`createTransformFeedbackStreamsSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7196-L7225).

## Parameter Dimensions

| Dimension | Evidence |
|---|---|
| Pipeline construction | The root dispatcher iterates monolithic, fast linked library, and link-time optimized library values in [`constructionTypes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackTests.cpp#L42-L46). |
| Registered group suffix | [`groupNameSuffix`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7267-L7274) maps construction type to `simple`, `simple_fast_gpl`, or `simple_optimized_gpl`. |
| Buffer count and size | [`bufferCounts[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6457-L6459) and [`bufferSizes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6457-L6459) define `{1,2,4,8}` and `{256,512,128*1024}`. |
| Test type | [`testTypes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6460-L6465) begins the basic/resume/point-size/clip/cull/draw-outside matrix. |
| Point-size variants | [`addTransformFeedbackTestCaseVariants()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6430-L6452) emits base and `_ptsz` cases when applicable. |
| Stream and query dimensions | Stream/query loops are visible in [`createTransformFeedbackSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L6681-L6691) and [`createTransformFeedbackStreamsSimpleTests()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L7105-L7153). |

## Support / Feature Requirements

[`TransformFeedbackTestCase::checkSupport()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L4597-L4724) requires `VK_KHR_get_physical_device_properties2`, pipeline-construction requirements, `VK_EXT_transform_feedback`, the `transformFeedback` feature, and conditional gates such as `VK_KHR_maintenance5`, multiview, `transformFeedbackDraw`, `VK_KHR_draw_indirect_count`, `VK_KHR_device_address_commands`, geometry/tessellation shader core features, large points, host query reset, max output components, and `VK_EXT_shader_object`.

## Verification Methods

Verification is primarily buffer- and image-based. Several instances call [`verifyTransformFeedbackBuffer()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L1125-L1233) after readback, winding checks use [`verifyVertexDataWithWinding()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L1688-L1779), draw-indirect paths use [`verifyImage()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackSimpleTests.cpp#L2656-L2870), and query paths compare written/generated counters.

## Test Principles Observed

- Large matrices are generated from explicit arrays and nested loops rather than hand-written cases.
- `simple_fast_gpl` and `simple_optimized_gpl` are sibling top-level roots, not descendants of `simple`.
- The two GPL roots are observed as twins in the inspected MUSTPASS file: each has 7886 entries, while the monolithic `simple` root has 7894 entries.

## Notes / Uncertainties

- The Registration Hierarchy tree lists the direct category children registered through this implementation file. Generated leaf case names are intentionally summarized in prose and parameter tables to avoid conflating sibling roots or duplicating thousands of generated leaves in the hierarchy tree.
