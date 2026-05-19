# vktTransformFeedbackFuzzLayoutTests.cpp

## Overview

[`vktTransformFeedbackFuzzLayoutTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L1) registers the [`fuzz`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L364-L365) group for transform-feedback interface-block layout coverage.

## Role

Implementation file.

## Source Code

- Primary source: [`vktTransformFeedbackFuzzLayoutTests.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L1)
- Related inspected files:
  - [`vktTransformFeedbackFuzzLayoutCase.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1)
  - [`vktTransformFeedbackRandomLayoutCase.cpp`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackRandomLayoutCase.cpp#L1)

## Registration Hierarchy

```text
transform_feedback.fuzz
├── 2_level_array
├── 2_level_struct_array
├── 3_level_array
├── instance_array_basic_type
├── multi_basic_types
├── multi_nested_struct
├── random_geometry
├── random_vertex
├── single_basic_array
├── single_basic_type
├── single_nested_struct
├── single_nested_struct_array
├── single_struct
├── single_struct_array
└── various_buffers
```

## Test Families

### single_* / multi_* — Structured interface layouts

The deterministic groups cover single basic types, arrays, structs, nested structs, multi-basic layouts, multi-nested layouts, and varying XFB buffers using direct `TestCaseGroup` construction in [`InterfaceBlockTests::init()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L397-L672).

### random_vertex / random_geometry — Randomized layout combinations

The random groups create 50 or 100 cases per feature set for scalar/vector/basic/array/struct/member-order combinations in [`createRandomCaseGroup()` calls](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L674-L738).

## Parameter Dimensions

Parameters include GLSL data type from [`basicTypes[]`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutTests.cpp#L374-L384), precision flags, array nesting, struct nesting, instance arrays, XFB buffer assignments, test stage (vertex or geometry), random feature flags, and case counts.

## Support / Feature Requirements

[`InterfaceBlockCaseInstance`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1710-L1764) requires the `transformFeedback` feature, sufficient transform-feedback buffers/data size, sufficient vertex or geometry output components, geometry shader support for geometry-stage cases, and shaderFloat64 for double-precision layouts.

## Verification Methods

The instance records transform feedback into a host-visible buffer, invalidates it, and calls [`validateValues()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1853-L1858); scalar/matrix details are checked in [`validateValue()`](../../../modules/vulkan/transform_feedback/vktTransformFeedbackFuzzLayoutCase.cpp#L1863-L1870).

## Test Principles Observed
- Interface layout coverage is split between deterministic structural cases and randomized feature combinations.
- Vertex and geometry stages are tested separately for many layout shapes.

## Notes / Uncertainties

- This page documents source-observed registration and verification behavior. The hierarchy tree lists the complete direct children of the documented registered group; generated cases inside those children are summarized in prose.
