# [vktApiDescriptorSetTests.cpp](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1)

## Overview

Tests Vulkan descriptor set layout lifetime semantics, empty descriptor set layout creation, and descriptor set layout binding ordering. Verifies that descriptor set layouts can be destroyed after being used to create pipeline layouts and pipelines, and that descriptor updates spanning multiple bindings work correctly.

## Role of File

Implementation-heavy. Contains all test logic, shader source generation, and the registration function [createDescriptorSetTests()](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664). Delegates to sub-group creation functions.

## Source Code

- Implementation: [vktApiDescriptorSetTests.cpp](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1)
- Header: [vktApiDescriptorSetTests.hpp](../../modules/vulkan/api/vktApiDescriptorSetTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../modules/vulkan/api/vktApiTests.cpp#L120)

## Registration Path

```
api
  +-- descriptor_set
```

## Test Hierarchy

```
descriptor_set
  +-- descriptor_set_layout_lifetime
  |     +-- graphics
  |     +-- compute
  +-- descriptor_set_layout
  |     +-- empty_set
  |           +-- normal
  |           +-- push_descriptor              [non-SC]
  +-- descriptor_set_layout_binding
        +-- update_subsequent_binding
        +-- layout_binding_order               [non-SC, Amber]
```

## Test Families

### Descriptor Set Layout Lifetime

[descriptorSetLayoutLifetimeGraphicsTest()](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L69) creates a pipeline layout from a descriptor set layout, destroys the layout (via Unique going out of scope in [createPipelineLayoutDestroyDescriptorSetLayout()](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L50)), then creates a graphics pipeline and executes a draw. Verifies that the pipeline remains valid after the layout object is destroyed.

[descriptorSetLayoutLifetimeComputeTest()](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L228) does the same for a compute pipeline, dispatching a compute shader after the descriptor set layout used to create the pipeline layout has been destroyed.

Both tests are registered at [line 610](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L610) and [line 614](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L614) via addFunctionCaseWithPrograms.

### Empty Descriptor Set Layout

[emptyDescriptorSetLayoutTest()](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L308) creates a descriptor set layout with zero bindings. The normal variant uses no create flags; the push_descriptor variant uses VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR (non-SC, requires VK_KHR_push_descriptor). Registered at [line 626](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L626) and [line 631](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L631).

### Descriptor Set Layout Binding Ordering

[descriptorSetLayoutBindingOrderingTest()](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L334) tests that when a VkWriteDescriptorSet with dstBinding=0 and descriptorCount=3 spans two bindings (binding 0 with 2 descriptors and binding 1 with 1 descriptor), the update correctly fills both bindings. Uses a compute shader that reads from both bindings and writes results to a storage buffer. Verifies that all three descriptor values are correctly read. Registered at [line 642](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L642).

The layout_binding_order Amber test at [line 647](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L647) provides additional coverage for binding ordering via the Amber framework (non-SC).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Pipeline type | Graphics, Compute |
| Descriptor set layout create flags | 0, VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR |
| Binding count | 0, 3 |
| Descriptor types | VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER |
| Binding array sizes | 1, 2 |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_push_descriptor | empty_set push_descriptor variant |

## Verification Methods

- **Pass-by-default**: The lifetime tests pass if the pipeline creation, command buffer recording, and submission succeed without errors ([line 225](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L225), [line 305](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L305))
- **Buffer content comparison**: The binding ordering test reads back a storage buffer and verifies that result values match expected values (5, 5, 5) at [line 552](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L552)
- **API success validation**: empty_set tests verify VK_SUCCESS from vkCreateDescriptorSetLayout

## Test Principles Observed

- Object lifetime: core focus is verifying that descriptor set layouts can be destroyed after their information has been consumed by pipeline layout and pipeline creation
- Cross-binding updates: the binding ordering test validates a specific spec requirement about descriptor updates spanning multiple bindings
- Amber integration: uses Amber test framework for additional declarative test coverage

## Notes / Uncertainties

- The lifetime tests use a rasterizer-discard graphics pipeline (rasterizerDiscardEnable=VK_TRUE at [line 114](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L114)), so no actual rendering output is verified
- The compute lifetime test uses a no-op compute shader (empty main at [line 573](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L573)), so only successful execution is checked, not output correctness
- The Amber test data directory is "api/descriptor_set/descriptor_set_layout_binding" at [line 646](../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L646)
