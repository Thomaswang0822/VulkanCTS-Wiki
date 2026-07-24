# Understanding Brief: `memory.requirements`

## One-Sentence Test Purpose

This test checks whether Vulkan memory-requirement queries return legal, internally consistent results for buffers, images, dedicated allocations, multiplane images, memory-property flags, and create-info queries.

## Background Knowledge

### Memory requirements

A Vulkan memory-requirement query returns allocation size, alignment, and a bitmask of compatible physical-device memory types. A result must describe legal memory usable by the queried resource. The queried size and alignment constrain later memory binding. [Device memory properties](../../../../vulkan-docs/src/chapters/memory.adoc#L494-L553)

### Object and create-info queries

Object-based queries inspect an already created buffer or image. Requirements2 and maintenance4 create-info queries expose comparable data before object creation or through extended output structures.

## One Concrete Example

A buffer requirement case creates a buffer with one selected usage, queries its requirements, and checks that `memoryTypeBits` is nonzero and valid, alignment is a power of two, and the result remains consistent across the selected size and usage comparisons.

## End-to-End Test Flow

```text
[host] select a registered requirement-query family and resource configuration
[host] check required features and format support
[host] create a buffer or image when the family uses object-based queries
[host] issue the selected requirements query and capture its output structures
[host] validate legality, resource-specific restrictions, and consistency relations
[host] compare equivalent object and create-info results when applicable
[host] report pass, Not Supported, or failure
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

No shaders participate.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Buffers | yes | no | no | query result only | Exercise buffer requirements and create-info equivalence. |
| Images | yes | no | no | query result only | Exercise tiling, format, sparse, and multiplane requirements. |
| Requirements output structures | yes | no | no | host-only | Carry size, alignment, compatible memory types, dedicated, plane, and sparse data. |

## What Is Checked

- Query results have nonzero, valid `memoryTypeBits` and power-of-two alignment.
- Buffer and image results obey resource-specific constraints and consistency relations.
- Extended and dedicated-allocation paths expose legal requirements data.
- Multiplane queries report per-plane information for supported configurations.
- Create-info results match equivalent object-based results where the source compares them.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `core`, `extended`, `dedicated_allocation`, `multiplane_image`, `memory_property_flags`, `create_info`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `core` | Invalid or inconsistent requirements from original buffer, image, or sparse-image query APIs. |
| `extended` | Invalid or inconsistent Requirements2 query results. |
| `dedicated_allocation` | Invalid dedicated-allocation requirement flags or incompatible extended requirements data. |
| `multiplane_image` | Incorrect per-plane requirements or plane-aspect handling. |
| `memory_property_flags` | Physical-device memory types report unsupported or unrecognized property-flag combinations. |
| `create_info` | Create-info query results differ from equivalent object-based queries or violate maintenance4 relations. |

## Important Variations and Special Cases

- `core` covers original buffer, image, and non-Vulkan-SC sparse query paths.
- `extended` requires `VK_KHR_get_memory_requirements2`; dedicated allocation also requires `VK_KHR_dedicated_allocation`.
- `multiplane_image` requires Requirements2 and sampler YCbCr conversion.
- `create_info` is excluded under Vulkan SC and requires `VK_KHR_maintenance4`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Buffer requirement cases | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L125-L685) | Builds and validates core, extended, dedicated, and create-info buffer cases. |
| Image requirement cases | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L861-L1571) | Builds and validates image variants. |
| Multiplane cases | [`vktMemoryRequirementsTests.cpp`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1964-L2109) | Builds per-plane requirement tests. |
| Family registration | [`createRequirementsTests`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L2110-L2131) | Defines the registered top-level families. |

## Questions / Risk Points for User Audit

- Does the six-family behavior axis make the API boundaries clear?
- Are query consistency claims kept tied to their corresponding source comparisons?

## Conversion Notes for Final Wiki Rewrite

- Use test family as the primary behavioral axis.
- Copy the Failure Cause Mapping table unchanged into the final page.
- State that no shader participates.
