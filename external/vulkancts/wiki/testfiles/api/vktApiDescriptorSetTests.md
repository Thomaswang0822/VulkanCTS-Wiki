# [vktApiDescriptorSetTests.cpp](../../../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1)

## Overview

Tests descriptor set layout lifetime semantics, empty descriptor set layout creation, and descriptor set layout binding ordering. Validates that descriptor set layouts can be destroyed after being used to create pipeline layouts and that the resulting pipelines remain valid.

## Role of File

Implementation-heavy. Contains test logic for descriptor set layout lifetime, empty layout creation, and binding ordering verification. The public entry point [createDescriptorSetTests()](../../../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664) assembles the test tree.

## Source Code

- Source: [vktApiDescriptorSetTests.cpp](../../../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1)
- Header: [vktApiDescriptorSetTests.hpp](../../../../../modules/vulkan/api/vktApiDescriptorSetTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L120) adds `descriptor_set` group to `api`

## Registration Path

```
api
 +-- descriptor_set
      +-- descriptor_set_layout_lifetime
      |    +-- graphics
      |    +-- compute
      +-- descriptor_set_layout
      |    +-- empty_set
      |         +-- normal
      |         +-- push_descriptor    (non-VKSC only)
      +-- descriptor_set_layout_binding
           +-- update_subsequent_binding
           +-- layout_binding_order    (non-VKSC only, Amber test)
```

## Test Hierarchy

```
descriptor_set
 +-- descriptor_set_layout_lifetime
 |    +-- graphics              -- descriptor set layout destroyed before graphics pipeline creation
 |    +-- compute               -- descriptor set layout destroyed before compute pipeline creation
 +-- descriptor_set_layout
 |    +-- empty_set
 |         +-- normal           -- create empty descriptor set layout with no flags
 |         +-- push_descriptor  -- create empty push descriptor set layout (non-VKSC only)
 +-- descriptor_set_layout_binding
      +-- update_subsequent_binding  -- verify subsequent binding update with remaining elements
      +-- layout_binding_order       -- Amber test for binding order (non-VKSC only)
```

## Test Families

### descriptor_set_layout_lifetime

Tests that a descriptor set layout used to create a pipeline layout can be destroyed before the pipeline is created, and the pipeline remains functional. The graphics variant creates a vertex-only pipeline with rasterizer discard enabled. The compute variant creates a compute pipeline that writes to a storage buffer. Both verify the pipeline can be used to submit and complete work successfully.

### descriptor_set_layout / empty_set

Tests creation of empty descriptor set layouts (zero bindings). The `normal` test uses no create flags. The `push_descriptor` test uses `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` (non-VKSC only). Implemented by [emptyDescriptorSetLayoutTest()](../../../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L620).

### descriptor_set_layout_binding

Tests descriptor set layout binding ordering. The `update_subsequent_binding` test verifies that updating a subsequent binding does not affect prior bindings. The `layout_binding_order` test is an Amber-based test that verifies binding order correctness (non-VKSC only).

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Pipeline Type | graphics, compute |
| Layout Flags | 0, VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR |
| Binding Test | update_subsequent_binding, layout_binding_order |

## Support / Feature Requirements

- `VK_KHR_push_descriptor` required for `push_descriptor` test (non-VKSC only)
- Graphics tests require a renderable color attachment format ([getRenderTargetFormat()](../../../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp) in related pipeline tests)

## Verification Methods

- Lifetime tests: Create pipeline layout with descriptor set layout, destroy layout, create pipeline, submit command buffer, verify completion succeeds
- Empty set tests: Create empty descriptor set layout and verify no errors occur
- Binding ordering: Use compute shader to write descriptor data to storage buffer and verify correct values are read back

## Test Principles Observed

- Lifetime tests validate Vulkan's deferred destruction semantics for descriptor set layouts
- Empty descriptor set layouts are a valid edge case per the Vulkan specification
- Amber test integration for declarative test specification

## Notes / Uncertainties

- The group name is `descriptor_set` as confirmed in [createDescriptorSetTests()](../../../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L666)
- The lifetime tests create the pipeline layout first, then destroy the descriptor set layout, then create the pipeline -- this is the key sequence being tested
- The Amber test data directory is `api/descriptor_set/descriptor_set_layout_binding` ([L646](../../../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L646))
