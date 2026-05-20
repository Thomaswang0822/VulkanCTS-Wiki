# vktSubgroupsTests.cpp

## Overview

[`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L25-L47) is the top-level dispatcher for the `subgroups` category. It includes the registering subgroup headers and attaches each verified child group in [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L55-L82).

## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L1)

## Registration Hierarchy

```text
subgroups
├── builtin_var
├── builtin_mask_var
├── basic
├── vote
├── ballot
├── ballot_broadcast
├── ballot_other
├── arithmetic
├── clustered
├── partitioned
├── shuffle
├── quad
├── shape
├── ballot_mask
├── multiple_dispatches
├── size_control
├── subgroup_uniform_control_flow
├── uniform_descriptor_indexing
└── shader_quad_control
```

## Test Families

### builtin_var

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### builtin_mask_var

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### basic

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### vote

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### ballot

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### ballot_broadcast

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### ballot_other

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### arithmetic

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### clustered

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### partitioned

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### shuffle

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### quad

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### shape

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### ballot_mask

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### multiple_dispatches

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### size_control

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### subgroup_uniform_control_flow

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### uniform_descriptor_indexing

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.
### shader_quad_control

Registered direct child of `subgroups` from [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80). See the matching Level-3 page for operation families and parameter matrices.

## Parameter Dimensions

The dispatcher itself has no data matrix. It delegates all operation, format, shader-stage, subgroup-size-control, descriptor-type, and Amber-file parameters to child implementation files registered in [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L59-L80).

## Support / Feature Requirements

No support checks are implemented in this dispatcher. Child implementation files check subgroup support, operation feature bits, stage availability, and extension requirements. Non-VulkanSC-only child registrations are guarded by `#ifndef CTS_USES_VULKANSC` in the include and registration sections of [`vktSubgroupsTests.cpp`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L45) and [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L68-L81).

## Verification Methods

No result validation is implemented in this dispatcher; verification is delegated to child implementation files and shared helpers such as [`makeComputeTest()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L4116-L4123), [`makeVertexFrameBufferTest()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L3243-L3249), and related result-callback helpers.

## Test Principles Observed

- The root file separates category registration from implementation.
- Displayed group names are defined by child `TestCaseGroup` construction, not by factory-symbol names.
- VulkanSC guards remove partitioned, uniform-control-flow, uniform-descriptor-indexing, and quad-control branches and non-SC shader-stage branches where guarded in children.

## Notes / Uncertainties

- This page documents source-observed registration only. Leaf-level generated cases are summarized in child pages.
- [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L8-L12) provides general API test-plan context but no inspected category-specific subgroup plan.
