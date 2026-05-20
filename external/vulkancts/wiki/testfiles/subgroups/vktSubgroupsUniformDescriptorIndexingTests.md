# vktSubgroupsUniformDescriptorIndexingTests.cpp

## Overview

[`vktSubgroupsUniformDescriptorIndexingTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L1) documents the [`subgroups.uniform_descriptor_indexing`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L827) branch. It covers uniform descriptor indexing for several descriptor types.

## Role

Implementation file that registers tests under the verified group name [`uniform_descriptor_indexing`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L827).

## Source Code

- Primary source: [`vktSubgroupsUniformDescriptorIndexingTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L1)

## Registration Hierarchy

```text
subgroups.uniform_descriptor_indexing
├── storage_buffer
├── storage_texel_buffer
├── uniform_texel_buffer
├── storage_image
├── sampler
├── sampled_image
├── combined_image_sampler
├── uniform_buffer
└── input_attachment
```

## Test Families

### storage_buffer

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.
### storage_texel_buffer

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.
### uniform_texel_buffer

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.
### storage_image

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.
### sampler

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.
### sampled_image

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.
### combined_image_sampler

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.
### uniform_buffer

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.
### input_attachment

Registered direct child of `uniform_descriptor_indexing`; generated leaves and parameter matrices are summarized from the source registration loops.

## Parameter Dimensions

- descriptor type from the `caseList` table, observed in [`createSubgroupsUniformDescriptorIndexingTests()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L827-L831).
- Each descriptor type is registered as one child `UniformDescriptorIndexingTestCase`; descriptor-specific setup is handled by the local implementation rather than by the shared operation-family subgroup helper matrix.

## Support / Feature Requirements

Requires subgroup size greater than one, fragment-stage subgroup support, runtime descriptor arrays, and descriptor-type-specific non-uniform indexing features, with support code in [`UniformDescriptorIndexingTestCase::checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L625-L684).

## Verification Methods

The image result is classified by colors; the test passes only when non-background groups are within the expected descriptor-count range, evidenced by result verification in [`UniformDescriptorIndexingTestCaseTestInstance::iterate()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L353-L378).

## Test Principles Observed

- The file registers descriptor-type children from a local `caseList` loop.
- The implementation is fragment/descriptor-indexing oriented; it is not a compute/mesh/ray-tracing subgroup-operation matrix like many other files in this category.

## Notes / Uncertainties

- The hierarchy tree intentionally lists only direct children of `subgroups.uniform_descriptor_indexing`. Deeper generated leaf names are summarized rather than expanded.
- Claims are limited to inspected source under `external/vulkancts/modules/vulkan/subgroups/`; [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L8-L12) gives only general API-test-plan context for this category.
