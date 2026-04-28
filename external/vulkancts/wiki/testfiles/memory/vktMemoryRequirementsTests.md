# Memory Requirements Tests

Buffer and image memory requirements validation tests. Verifies that `VkMemoryRequirements` returned by various query APIs are consistent, valid, and conform to Vulkan specification constraints.

## Source

- [vktMemoryRequirementsTests.cpp](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp)

## Registration

- **Group name:** `requirements`
- **Registration function:** [`createRequirementsTests()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L2110)
- **Parent group:** `memory`

## Test Hierarchy

```
requirements
├── core
│   ├── buffer
│   │   ├── regular
│   │   ├── sparse                    (Vulkan 1.0 only)
│   │   ├── sparse_residency          (Vulkan 1.0 only)
│   │   ├── sparse_aliased            (Vulkan 1.0 only)
│   │   └── sparse_residency_aliased  (Vulkan 1.0 only)
│   └── image
│       ├── regular_tiling_linear
│       ├── regular_tiling_optimal
│       ├── transient_tiling_linear
│       ├── transient_tiling_optimal
│       ├── sparse_tiling_linear        (Vulkan 1.0 only)
│       ├── sparse_tiling_optimal       (Vulkan 1.0 only)
│       ├── sparse_residency_tiling_optimal   (Vulkan 1.0 only)
│       ├── sparse_aliased_tiling_optimal     (Vulkan 1.0 only)
│       └── sparse_residency_aliased_tiling_optimal (Vulkan 1.0 only)
├── extended
│   ├── buffer (same sub-cases as core)
│   └── image (same sub-cases as core)
├── dedicated_allocation
│   ├── buffer (same sub-cases as core)
│   └── image (same sub-cases as core)
├── multiplane_image
│   ├── regular_optimal
│   ├── regular_linear
│   ├── transient_optimal
│   ├── transient_linear
│   ├── sparse_optimal
│   ├── sparse_residency_optimal
│   ├── sparse_aliased_optimal
│   └── sparse_residency_aliased_optimal
├── memory_property_flags
│   └── check_all
└── create_info                        (Vulkan 1.0 only)
    ├── buffer (same sub-cases as core)
    ├── image (same sub-cases as core)
    └── multiplane_image (same sub-cases as multiplane_image)
```

## Test Families

### core

Tests memory requirements using the original Vulkan 1.0 core APIs:
- **Buffer:** [`vkGetBufferMemoryRequirements()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L429)
- **Image:** [`vkGetImageMemoryRequirements()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L887)
- **Sparse images:** [`vkGetImageSparseMemoryRequirements()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L891)

### extended

Same test logic as `core`, but uses `VK_KHR_get_memory_requirements2` extension APIs:
- **Buffer:** [`vkGetBufferMemoryRequirements2()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L545-L549)
- **Image:** [`vkGetImageMemoryRequirements2()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1437)

### dedicated_allocation

Extends `extended` tests to also validate `VkMemoryDedicatedRequirements` chained output, checking `prefersDedicatedAllocation` and `requiresDedicatedAllocation` fields. Requires `VK_KHR_dedicated_allocation`.

Key verification: regular (non-shared) objects must **not** require dedicated allocations ([vktMemoryRequirementsTests.cpp:641-643](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L641), [vktMemoryRequirementsTests.cpp:1504-1505](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1504)).

### multiplane_image

Tests per-plane memory requirements for multi-planar (YCbCr) image formats using `VK_KHR_sampler_ycbcr_conversion` and `VK_KHR_get_memory_requirements2`. Iterates over `formats::planarFormats` and queries requirements for each plane aspect via `VkImagePlaneMemoryRequirementsInfo` ([vktMemoryRequirementsTests.cpp:1873-1880](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1873)).

### memory_property_flags

Validates that all memory types reported by `vkGetPhysicalDeviceMemoryProperties()` match known `VkMemoryPropertyFlagBits` combinations ([vktMemoryRequirementsTests.cpp:2013-2080](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L2013)).

### create_info (Vulkan 1.0 only)

Tests `VK_KHR_maintenance4` create-info-based memory requirement queries:
- **Buffer:** [`vkGetDeviceBufferMemoryRequirements()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L125) — queries requirements without creating a buffer object
- **Image:** [`vkGetDeviceImageMemoryRequirements()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L164) — queries without creating an image
- **Sparse:** [`vkGetDeviceImageSparseMemoryRequirements()`](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L180)

Verifies results match equivalent object-based queries ([vktMemoryRequirementsTests.cpp:713-726](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L713), [vktMemoryRequirementsTests.cpp:1571-1639](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1571)).

## Parameter Dimensions

### Buffer tests

| Dimension | Values |
|-----------|--------|
| Create flags | 0, `SPARSE_BINDING_BIT`, `SPARSE_BINDING_BIT|SPARSE_RESIDENCY_BIT`, `SPARSE_BINDING_BIT|SPARSE_ALIASED_BIT`, all three combined |
| Usage flags | Each individual `VK_BUFFER_USAGE_*` bit from `TRANSFER_SRC_BIT` to `INDIRECT_BUFFER_BIT` |
| Size | 1KB, 8KB, 64KB, 1MB |

### Image tests (core/extended/dedicated_allocation)

| Dimension | Values |
|-----------|--------|
| Create flags | 0, `CUBE_COMPATIBLE_BIT`, sparse combinations |
| Tiling | `VK_IMAGE_TILING_LINEAR`, `VK_IMAGE_TILING_OPTIMAL` |
| Transient | With/without `VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT` |
| Image type | `VK_IMAGE_TYPE_1D`, `VK_IMAGE_TYPE_2D`, `VK_IMAGE_TYPE_3D` |
| Format | All formats from `formats::allFormats` matching color or depth/stencil aspect |
| Usage | Each individual `VK_IMAGE_USAGE_*` bit |
| Samples | 1, 2, 4, 8, 16 |

### Multiplane image tests

| Dimension | Values |
|-----------|--------|
| Create flags | `MUTABLE_FORMAT_BIT`, `CUBE_COMPATIBLE_BIT`, `ALIAS_BIT`, `DISJOINT_BIT`, `EXTENDED_USAGE_BIT`, `SAMPLE_LOCATIONS_COMPATIBLE_DEPTH_BIT_EXT`, `PROTECTED_BIT`, and various extension flags |
| Tiling | `VK_IMAGE_TILING_OPTIMAL`, `VK_IMAGE_TILING_LINEAR` |
| Transient | With/without |
| Sparse | Regular, sparse, sparse+residency, sparse+aliased, sparse+residency+aliased |
| Formats | `formats::planarFormats` |

## Support Requirements

| Feature/Extension | Required by |
|-------------------|-------------|
| Sparse binding feature | All sparse buffer/image test cases |
| Sparse residency buffer feature | Buffer tests with `SPARSE_RESIDENCY_BIT` |
| Sparse residency aliased feature | Tests with `SPARSE_ALIASED_BIT` |
| Sparse residency image 2D/3D | Image tests with `SPARSE_RESIDENCY_BIT` |
| `VK_KHR_get_memory_requirements2` | extended, multiplane_image, create_info groups |
| `VK_KHR_dedicated_allocation` | dedicated_allocation group |
| `VK_KHR_sampler_ycbcr_conversion` | multiplane_image group |
| `VK_KHR_maintenance4` | create_info group |
| `VK_EXT_texture_compression_astc_3d` | ASTC 3D format cases ([vktMemoryRequirementsTests.cpp:1164](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1164)) |

## Verification Methods

### Buffer verification ([vktMemoryRequirementsTests.cpp:437-502](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L437))

- `memoryTypeBits` must have at least one bit set
- All bits must reference valid memory type indices
- Alignment must be a power of two
- At least one memory type must include `VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT`
- Non-sparse buffers require `HOST_VISIBLE_BIT | HOST_COHERENT_BIT`
- Memory types must not include `LAZILY_ALLOCATED_BIT`
- Alignment respects device limits for uniform/storage/texel buffers
- `memoryTypeBits` for specific usage must be a superset of all-usage-combined bits
- For same create/usage flags, `memoryTypeBits` and `alignment` must be identical across different sizes

### Image verification ([vktMemoryRequirementsTests.cpp:895-952](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L895))

- Same basic checks as buffer (valid bits, power-of-two alignment, device local)
- `LAZILY_ALLOCATED_BIT` only allowed for transient attachment images
- Linear-tiling images require `HOST_VISIBLE_BIT | HOST_COHERENT_BIT`
- For sparse images, `imageMipTailSize` must be aligned with sparse block size
- `memoryTypeBits` must be consistent across configurations with same tiling/transient/sparse flags

### Multiplane verification ([vktMemoryRequirementsTests.cpp:1888-1948](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L1888))

- Per-plane alignment must be power of two
- Sparse `imageMipTailSize` aligned with sparse block size
- Linear-tiling requires `HOST_VISIBLE_BIT` (unless protected)
- `LAZILY_ALLOCATED_BIT` only for transient attachments

### Create-info verification ([vktMemoryRequirementsTests.cpp:706-727](../../../modules/vulkan/memory/vktMemoryRequirementsTests.cpp#L706))

- Results from create-info queries must match object-based queries (alignment, memoryTypeBits, size)
- Smaller objects must not require larger memory sizes

## Test Principles

The tests systematically iterate over parameter combinations for buffers and images, querying memory requirements and validating them against Vulkan spec constraints. The design ensures:

1. **API consistency:** Different query APIs (core vs. KHR2 vs. create-info) return consistent results
2. **Size independence:** Memory type bits and alignment do not change with buffer/image size
3. **Usage subset property:** Memory types for a specific usage are a subset of all-usage-combined types
4. **Dedicated allocation hints:** `prefersDedicatedAllocation` is a valid bool32; `requiresDedicatedAllocation` is always false for regular objects
