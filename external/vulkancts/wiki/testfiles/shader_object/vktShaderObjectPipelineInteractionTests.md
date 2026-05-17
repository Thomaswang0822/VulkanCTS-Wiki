# [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1)

## Overview

[`vktShaderObjectPipelineInteractionTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1) implements the `shader_object/pipeline_interaction` branch. The branch registers ten pipeline/shader-object sequencing cases and eight stage-binding cases under the verified group name `pipeline_interaction` at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1506-L1552). The sequencing enum covers shader-object-only, pipeline-only, pipeline/shader-object interleaving, render-pass pipeline plus shader-object, and compute interactions at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L45-L57). Verification copies rendered output to host-visible buffers, checks quadrant colors according to draw count, and checks compute output buffer values for compute-interaction cases at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L740-L777) and [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L780-L817).

## Role of File

Implementation-heavy test file for the root-level `pipeline_interaction` branch.

## Source Code

- Primary source: [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L56)
- Shared utility include: [vktShaderObjectCreateUtil.hpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Hierarchy

```text
shader_object.pipeline_interaction
├── shader_object
├── max_pipeline
├── max_pipeline_shader_object_max_pipeline
├── shader_object_max_pipeline_shader_object
├── min_pipeline_shader_object
├── shader_object_min_pipeline
├── render_pass_pipeline_shader_object
├── render_pass_pipeline_shader_object_after_begin
├── compute_shader_object_min_pipeline
├── shader_object_compute_pipeline
├── vert
├── vert_tess
├── vert_geom
├── vert_frag
├── vert_tess_geom
├── vert_tess_frag
├── vert_geom_frag
└── vert_tess_geom_frag
```

The displayed branch name is verified from `TestCaseGroup(testCtx, "pipeline_interaction")` at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1506-L1508). The root file registers this branch directly at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L56).

## Test Families

### shader_object — Pipeline and shader-object sequencing

`tests[]` maps the ten `TestType` values to case names: `shader_object`, `max_pipeline`, `max_pipeline_shader_object_max_pipeline`, `shader_object_max_pipeline_shader_object`, `min_pipeline_shader_object`, `shader_object_min_pipeline`, `render_pass_pipeline_shader_object`, `render_pass_pipeline_shader_object_after_begin`, `compute_shader_object_min_pipeline`, and `shader_object_compute_pipeline` at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1510-L1533). The enum itself shows the covered ordering categories: shader objects, maximum pipelines, minimum pipelines, render-pass pipelines, and compute combinations at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L45-L57). The draw count expected by image verification is selected from `TestType` in `getDrawCount()` at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L102-L128).

### vert — Stage-binding subsets

`shaderBindTests[]` registers eight stage-presence combinations: `vert`, `vert_tess`, `vert_geom`, `vert_frag`, `vert_tess_geom`, `vert_tess_frag`, `vert_geom_frag`, and `vert_tess_geom_frag` over vertex, tessellation, geometry, and fragment stages at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1535-L1549). These cases use `StageTestParams` booleans defined at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L64-L70).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Pipeline interaction type | Ten `TestType` enum values at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L45-L57) and registered names at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1514-L1525) |
| Expected draw count | `getDrawCount()` returns 1, 2, or 3 depending on the selected `TestType` at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L102-L128) |
| Stage-binding booleans | `vertShader`, `tessShader`, `geomShader`, `fragShader` in `StageTestParams` at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L64-L70) |
| Stage-binding names | `vert`, `vert_tess`, `vert_geom`, `vert_frag`, `vert_tess_geom`, `vert_tess_frag`, `vert_geom_frag`, `vert_tess_geom_frag` at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1539-L1544) |

## Support / Feature Requirements

- Primary sequencing cases require `VK_EXT_shader_object`, tessellation shader support, and geometry shader support at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L954-L960).
- Stage-binding cases require `VK_EXT_shader_object`; tessellation and geometry features are required only when the selected `StageTestParams` use those stages at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1324-L1333).
- Registration itself is unconditional once the root adds the branch factory at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L56).

## Verification Methods

- Pipeline-interaction cases copy the rendered image into a host-visible buffer, call `verifyImage()`, and fail if the expected draw-count-dependent image regions are missing at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L740-L761).
- `verifyImage()` expects red in the upper-left quadrant for draw count greater than zero, green in the upper-right quadrant for draw count greater than one, and blue in the lower-left quadrant for draw count greater than two at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L780-L817).
- Compute-interaction cases additionally invalidate and read a storage buffer and fail unless indices `0..3` contain their own index values at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L763-L777).
- Stage-binding cases copy image output and fail if `verifyImage()` fails, then check per-stage storage-buffer values: vertex writes `1`, tessellation writes `2`, and geometry writes `3` when those stages are selected at [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1240-L1263).

## Test Principles Observed

- Exercise switching boundaries between shader objects and graphics/compute pipelines.
- Separate full sequencing tests from smaller stage-binding subset tests.
- Verify both visual effects and shader-stage side effects through host-visible output buffers.

## Notes / Uncertainties

- This page describes the pass/fail checks visible in inspected `iterate()` and helper ranges. It does not enumerate every command-buffer setup path inside the long bodies.
