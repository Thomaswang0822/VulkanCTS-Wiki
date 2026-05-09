# [vktApiDescriptorSetTests.cpp](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1)

## Overview

[`vktApiDescriptorSetTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.descriptor_set` subtree. It registers three direct children under `descriptor_set`, covering descriptor-set-layout lifetime after pipeline-layout creation, empty descriptor-set-layout creation, and descriptor-set-layout binding-order behavior.

## Role of File

Implementation-heavy test file for the `api.descriptor_set` subgroup. The public entry point is [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664-L672).

## Source Code

- Primary source: [vktApiDescriptorSetTests.cpp](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L1)
- Header: [vktApiDescriptorSetTests.hpp](../../../modules/vulkan/api/vktApiDescriptorSetTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L100-L140)

## Registration Hierarchy

```text
api.descriptor_set
├── descriptor_set_layout_lifetime
├── descriptor_set_layout
└── descriptor_set_layout_binding
```

The confirmed Level-3 root is `api.descriptor_set`, created by [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664-L672) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L120-L120). The exact direct children confirmed from the registration function are `descriptor_set_layout_lifetime`, `descriptor_set_layout`, and `descriptor_set_layout_binding`. The default Vulkan mustpass entries under this subtree are `descriptor_set_layout_lifetime.compute`, `descriptor_set_layout_lifetime.graphics`, `descriptor_set_layout.empty_set.normal`, `descriptor_set_layout.empty_set.push_descriptor`, `descriptor_set_layout_binding.update_subsequent_binding`, and `descriptor_set_layout_binding.layout_binding_order`, as seen in [`api.txt`](../../../mustpass/main/vk-default/api.txt).

## Test Families

### descriptor_set_layout_lifetime — Descriptor-set-layout lifetime after pipeline-layout creation

Covers the `descriptor_set_layout_lifetime` direct child registered by [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L668-L668). This subgroup contains the `graphics` and `compute` cases described in the legacy page. Those cases verify that a descriptor set layout can be used to create a pipeline layout, destroyed afterward, and still permit successful pipeline creation and execution.

### descriptor_set_layout — Empty descriptor-set-layout creation

Covers the `descriptor_set_layout` direct child registered by [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L669-L669). Its registered child `empty_set` is created by [`createDescriptorSetLayoutTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L655-L661), which delegates to [`createEmptyDescriptorSetLayoutTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L620-L635). The resulting leaf cases are `normal`, which uses zero create flags, and `push_descriptor`, which uses `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` and is omitted for Vulkan SC by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L628-L633).

### descriptor_set_layout_binding — Descriptor-set-layout binding-order behavior

Covers the `descriptor_set_layout_binding` direct child registered by [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L670-L670). [`createDescriptorSetLayoutBindingOrderingTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L637-L653) registers `update_subsequent_binding` through [`addFunctionCaseWithPrograms()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L642-L643) and conditionally adds the Amber-based `layout_binding_order` case from the `api/descriptor_set/descriptor_set_layout_binding` data directory in [`vktApiDescriptorSetTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L645-L650).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct child subgroup | `descriptor_set_layout_lifetime`, `descriptor_set_layout`, `descriptor_set_layout_binding` from [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L666-L670) |
| Lifetime pipeline type | `graphics`, `compute` as documented in the registered `descriptor_set_layout_lifetime` subtree and reflected by mustpass entries in [`api.txt`](../../../mustpass/main/vk-default/api.txt) |
| Empty-layout case | `normal`, `push_descriptor` from [`createEmptyDescriptorSetLayoutTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L623-L633) |
| Layout flags | `0` and `VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` in [`vktApiDescriptorSetTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L626-L632) |
| Binding-order case | `update_subsequent_binding`, `layout_binding_order` from [`createDescriptorSetLayoutBindingOrderingTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L641-L649) |
| Amber test data directory | `api/descriptor_set/descriptor_set_layout_binding` in [`vktApiDescriptorSetTests.cpp`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L645-L649) |

## Support / Feature Requirements

- `push_descriptor` is excluded from Vulkan SC by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L628-L633), matching the note that `VK_KHR_push_descriptor` is not part of the Vulkan SC test set.
- `layout_binding_order` is likewise omitted for Vulkan SC by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L645-L650).
- The legacy page notes that the graphics lifetime path requires a renderable color-attachment format, but that specific support helper is not confirmed from the inspected registration excerpt and is therefore left as an observed legacy note rather than a stronger source-backed claim.

## Verification Methods

- Lifetime tests create a pipeline layout using a descriptor set layout, destroy the descriptor set layout, then create and execute the pipeline to verify the lifetime sequence succeeds, as summarized by the legacy page and associated with the `descriptor_set_layout_lifetime` subgroup registered by [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L668-L668).
- Empty-layout tests create empty descriptor set layouts and pass when creation succeeds without error; the relevant registrations come from [`createEmptyDescriptorSetLayoutTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L620-L635).
- Binding-order verification uses the functional `update_subsequent_binding` program path plus the Amber-based `layout_binding_order` case registered in [`createDescriptorSetLayoutBindingOrderingTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L637-L653).

## Test Principles Observed

- Validate deferred-lifetime behavior for descriptor set layouts after they have already contributed to pipeline-layout creation.
- Exercise empty descriptor set layouts as a legal edge-case configuration.
- Combine ordinary programmatic API tests with an Amber-based declarative binding-order test in the same Level-3 subtree.

## Notes / Uncertainties

- This normalization confirms the canonical Level-3 root as `api.descriptor_set`, replacing the legacy split between `Registration Path` and `Test Hierarchy` sections.
- The direct children used in the canonical hierarchy are strictly the registered immediate children of [`createDescriptorSetTests()`](../../../modules/vulkan/api/vktApiDescriptorSetTests.cpp#L664-L672): `descriptor_set_layout_lifetime`, `descriptor_set_layout`, and `descriptor_set_layout_binding`.
- Deeper descendants such as `graphics`, `compute`, `empty_set`, `normal`, `push_descriptor`, `update_subsequent_binding`, and `layout_binding_order` are intentionally described in prose rather than expanded in the parseable hierarchy, per the normalization contract.
