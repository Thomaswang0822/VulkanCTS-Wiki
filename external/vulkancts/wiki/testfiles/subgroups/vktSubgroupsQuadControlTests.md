# vktSubgroupsQuadControlTests.cpp

## Overview

[`vktSubgroupsQuadControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L1) documents the [`subgroups.shader_quad_control`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L807) branch. It covers `VK_KHR_shader_quad_control` draw tests.

## Role

Implementation file that registers tests under the verified group name [`shader_quad_control`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L807).

## Source Code

- Primary source: [`vktSubgroupsQuadControlTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L1)

## Registration Hierarchy

```text
subgroups.shader_quad_control
├── quad_derivatives
├── require_full_quads
├── divergent_condition
└── terminated_invocation
```

## Test Families

### quad_derivatives

Registered direct child of `shader_quad_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### require_full_quads

Registered direct child of `shader_quad_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### divergent_condition

Registered direct child of `shader_quad_control`; generated leaves and parameter matrices are summarized from the source registration loops.
### terminated_invocation

Registered direct child of `shader_quad_control`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- test mode selected from four direct child cases, observed in [`createSubgroupsQuadControlTests()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L807-L820).
- The four modes map to `quad_derivatives`, `require_full_quads`, `divergent_condition`, and `terminated_invocation` test cases in the registration function.

## Support / Feature Requirements

Requires `VK_KHR_shader_quad_control`; terminated-invocation mode also requires `VK_KHR_shader_terminate_invocation`, with support checks in [`DrawWithQuadControlTestCase::checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L621-L645).

## Verification Methods

The draw test returns pass when `isResultCorrect()` accepts the output image/buffer access, evidenced by result-checking code in [`isResultCorrect()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L569-L576) and the test iteration path that calls it in [`DrawWithQuadControlTestInstance::iterate()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L331-L336).

## Test Principles Observed

- This file registers four direct child draw tests for `VK_KHR_shader_quad_control` behavior.
- The implementation is draw-oriented; it is not a shared compute/mesh/ray-tracing subgroup-helper matrix like many operation files in this category.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.shader_quad_control`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`; [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L8-L12) gives only general API-test-plan context for this category.
