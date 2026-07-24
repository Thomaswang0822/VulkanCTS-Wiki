## Overview

**Core question:** Do Vulkan memory-requirement query APIs report legal and mutually consistent allocation requirements for the tested buffers and images?

- This page covers [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp), which implements `memory.requirements`.
- The family compares original, Requirements2, dedicated-allocation, multiplane, memory-property-flag, and create-info query behavior.
- The tests are host-side query and validation paths. They do not allocate memory for GPU work or execute shaders.

## Background Knowledge

For the shared concept memory types, heaps, and resource compatibility, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- Requirements2 queries return the same core requirements through extensible structures and can expose additional data such as `VkMemoryDedicatedRequirements` or per-plane image requirements.
- Create-info queries obtain requirements from resource-create parameters instead of an already-created object. The tests compare them with equivalent object queries where the APIs define comparable results.

## Registration Hierarchy

```text
memory.requirements
├── core
├── extended
├── dedicated_allocation
├── multiplane_image
├── memory_property_flags
└── create_info
```

`create_info` is not registered for Vulkan SC. The other direct test families select a query API or a requirements property to validate.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `core`, `extended`, `dedicated_allocation`, `multiplane_image`, `memory_property_flags`, `create_info` | Selects the query interface or requirements property under test. | [`createRequirementsTests`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L2110-L2131) |
| Buffer size | `1KiB`, `8KiB`, `64KiB`, `1MiB` | Checks size-dependent buffer requirements and consistency relations. | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L125-L685) |
| Buffer usage and flags | individual usages and regular/sparse variants | Changes the resource requirement being queried. | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L330-L685) |
| Image configuration | format, 1D/2D/3D type, sample count, usage, tiling, transient, sparse, cube-compatible variants | Changes the image requirement and feature gate. | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L861-L1571) |
| Plane aspect | planar format aspects | Selects a plane requirement in `multiplane_image`. | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1964-L2109) |

## Behavior Parameters

The test family is the primary behavioral axis. Each value changes the query contract or the part of the result being checked.

### core: original object-based requirement queries

This family uses the original buffer and image requirement APIs, plus sparse-image queries outside Vulkan SC. It checks basic result legality and resource-specific constraints.

### extended: Requirements2 object queries

This family repeats relevant buffer and image coverage through `vkGetBufferMemoryRequirements2` and `vkGetImageMemoryRequirements2`. It requires `VK_KHR_get_memory_requirements2` where the functionality is not core.

### dedicated_allocation: dedicated requirement flags

This family chains `VkMemoryDedicatedRequirements` into Requirements2 output. It checks that `prefersDedicatedAllocation` is a valid `VkBool32` and that the test objects do not unexpectedly require dedicated allocation.

### multiplane_image: per-plane image requirements

This family queries supported planar formats and aspects. It adds `VkImagePlaneMemoryRequirementsInfo` for disjoint images and checks the returned plane requirements.

### memory_property_flags: reported physical-memory properties

This single `check_all` area compares every physical-device memory type's `propertyFlags` with the source's recognized combinations, including extension-specific combinations where enabled.

### create_info: pre-creation requirement queries

This family uses maintenance4 create-info query APIs for buffers, images, sparse images, and applicable multiplane cases. It compares results with equivalent object-query data and checks selected size relations.

## Shader Analysis

No shader code participates in this test. The test constructs resource descriptions, calls requirements APIs, and validates returned host-side structures.

## Runtime Execution and Result Checking

- Core and extended buffer paths query requirements, require nonzero valid `memoryTypeBits`, power-of-two alignment, and check buffer-specific restrictions such as compatible memory properties and offset-limit alignment. [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L125-L685)
- Image paths filter unsupported configurations, query requirements, and check image-specific restrictions. Linear tiling requires a host-visible/coherent compatible type; lazily allocated memory is limited to transient attachments. [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L861-L1571)
- The source compares requirement consistency across selected buffer sizes and usages, and across supported image configurations with the same relevant configuration class.
- Multiplane paths query plane requirements only for supported planar configurations. Create-info paths compare their returned requirements with equivalent created-object queries. [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1964-L2131)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `core` | Invalid or inconsistent requirements from original buffer, image, or sparse-image query APIs. |
| `extended` | Invalid or inconsistent Requirements2 query results. |
| `dedicated_allocation` | Invalid dedicated-allocation requirement flags or incompatible extended requirements data. |
| `multiplane_image` | Incorrect per-plane requirements or plane-aspect handling. |
| `memory_property_flags` | Physical-device memory types report unsupported or unrecognized property-flag combinations. |
| `create_info` | Create-info query results differ from equivalent object-based queries or violate maintenance4 relations. |

### Cause Analysis

#### Basic or extended requirement failure

**Possible failure symptoms:** A query returns zero or invalid `memoryTypeBits`, non-power-of-two alignment, or a result that violates a checked buffer or image restriction.

**Possible implementation causes:** The implementation may report incompatible memory types, alignment, or resource requirements incorrectly. The source derives each assertion from the queried resource configuration; investigation should start with the failing API and exact resource-create parameters.

#### Dedicated-allocation or multiplane failure

**Possible failure symptoms:** Dedicated flags are not legal values, an ordinary test object unexpectedly requires dedicated allocation, or a plane requirement differs from the expected legal configuration.

**Possible implementation causes:** The extended requirements chain or planar-image aspect handling may be incorrect. The CTS source selects only supported format/configuration paths, so an unexpected result warrants source-level investigation of the corresponding Requirements2 output chain.

#### Memory-property-flag failure

**Possible failure symptoms:** A physical-device memory type reports a property-flag combination outside the recognized list.

**Possible implementation causes:** The implementation's memory-property report may be inconsistent with the extension and core flag combinations supported by this CTS version. Source-level investigation is needed to determine whether the report or the platform feature exposure is at fault.

#### Create-info equivalence failure

**Possible failure symptoms:** A create-info query differs from its equivalent object query in checked size, alignment, compatible-memory mask, or sparse-image fields.

**Possible implementation causes:** The maintenance4 query path may compute requirements differently from object creation. The source provides matched configurations for comparison, so the failing pair is the appropriate starting point for implementation investigation.

## Case Pruning

### Requirement-based pruning

- `extended` requires `VK_KHR_get_memory_requirements2`.
- `dedicated_allocation` also requires `VK_KHR_dedicated_allocation`.
- `multiplane_image` requires Requirements2 and `VK_KHR_sampler_ycbcr_conversion`.
- `create_info` requires `VK_KHR_maintenance4` and is excluded in Vulkan SC.
- Sparse, format, sample-count, and planar configurations skip when their required feature or queried support is absent.

### Design-based pruning

- Invalid linear+sparse image combinations are not registered for multiplane paths.
- Image variants are limited to configurations that the source can compare consistently; unsupported format combinations do not become false failures.
- Depth/stencil formats reset the image consistency baseline where their requirements cannot be compared with prior color-format cases.

## Key Takeaways

- The category checks requirements as a contract between resource creation and legal memory allocation, not as a data-transfer test.
- The six families cover original APIs, extensible APIs, specialized output data, physical-memory flags, and pre-creation queries.
- Consistency comparisons are central: equivalent query paths and related resource configurations must not report incompatible results.
- Feature and format pruning prevents unsupported resource shapes from being reported as failures.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Buffer requirements | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L125-L685) | Defines original, extended, dedicated, and create-info buffer coverage. |
| Image requirements | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L861-L1571) | Defines image legality and consistency checks. |
| Multiplane requirements | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1964-L2109) | Defines planar image and per-plane query coverage. |
| Top-level registration | [`createRequirementsTests`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L2110-L2131) | Registers the six direct test families. |
| Mustpass coverage | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt) | Contains registered `dEQP-VK.memory.requirements.*` paths. |
