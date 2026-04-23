# [vktApiBufferViewCreateTests.cpp](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L390)

## Overview

[`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L390) is one half of the adjacent `api/buffer_view` subtree that appears immediately after `api/buffer` in the API registration order through [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L106). The local group name in this file is `create`, and it focuses on buffer-view object construction over many Vulkan formats, two usage intents (uniform texel vs storage texel), and two buffer memory-allocation styles (suballocation vs dedicated allocation).

This file is included because it is directly adjacent and coherent with the requested early memory-object slice, and because `buffer_view` registration is split into two concrete implementation files by [`createBufferViewTests()`](../../modules/vulkan/api/vktApiTests.cpp#L78).

## Role of File

Implementation-heavy test file for the `api/buffer_view/create` subgroup.

## Source Code

- Primary source: [`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L1)
- Declaration: [`vktApiBufferViewCreateTests.hpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.hpp)
- Parent `buffer_view` aggregator registration: [`createBufferViewTests()`](../../modules/vulkan/api/vktApiTests.cpp#L78)
- Parent category registration: [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L106)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
└── api
    └── createTests(testCtx, "api")
        └── createApiTests(apiTests)
            └── createTestGroup(testCtx, "buffer_view", createBufferViewTests)
                └── createBufferViewTests(bufferViewTests)
                    ├── createBufferViewCreateTests(testCtx)
                    │   └── create
                    │       ├── suballocation
                    │       │   ├── uniform
                    │       │   │   └── <format cases>
                    │       │   └── storage
                    │       │       └── <format cases>
                    │       └── dedicated_alloc
                    │           ├── uniform
                    │           │   └── <format cases>
                    │           └── storage
                    │               └── <format cases>
                    └── createBufferViewAccessTests(testCtx)
                        └── access (documented in separate file)
```

Evidence:

- `buffer_view` subgroup insertion in [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L106)
- split registration into create/access in [`createBufferViewTests()`](../../modules/vulkan/api/vktApiTests.cpp#L82)
- `create` hierarchy assembly in [`createBufferViewCreateTests()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L390)

## Test Hierarchy

Visible hierarchy from [`createBufferViewCreateTests()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L390):

```text
api
└── buffer_view
    └── create
        ├── suballocation
        │   ├── uniform
        │   │   └── <one test per VkFormat in (VK_FORMAT_UNDEFINED+1 .. VK_CORE_FORMAT_LAST-1)>
        │   └── storage
        │       └── <same format sweep>
        └── dedicated_alloc
            ├── uniform
            │   └── <same format sweep>
            └── storage
                └── <same format sweep>
```

Observed construction details:

- allocation-style groups are pre-created as `suballocation` and `dedicated_alloc` in [`bufferViewAllocationGroupTests`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L404)
- usage groups are `uniform` and `storage`, driven by parallel arrays [`usage[]`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L393), [`feature[]`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L395), and [`usageName[]`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L397)
- the format sweep iterates from `VK_FORMAT_UNDEFINED + 1` up to `VK_CORE_FORMAT_LAST - 1` in [`createBufferViewCreateTests()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L415), creating one [`BufferViewTestCase`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L105) per format per usage per allocation kind

## Test Families

### 1. Buffer-view creation over format × usage × allocation-kind matrix

The central family is defined by [`BufferViewCaseParameters`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L56) and instantiated in [`createBufferViewCreateTests()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L423).

Per-case fixed parameters observed in registration:

- `offset = 0` ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L425))
- `range = VK_WHOLE_SIZE` ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L392))
- `usage` is either `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` or `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L393))
- required format feature is matched to usage (`UNIFORM_TEXEL_BUFFER_BIT` or `STORAGE_TEXEL_BUFFER_BIT`) ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L395))
- allocation kind is either suballocated or dedicated ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L429))

### 2. Suballocation buffer allocator path

When `bufferAllocationKind` is suballocation, [`BufferSuballocation::createTestBuffer()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L139) is used.

Observed behavior:

- creates a buffer with exclusive sharing and requested usage ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L146))
- queries memory requirements via [`getBufferMemoryRequirements()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L166)
- validates requirement size is not smaller than requested size in subprocess contexts and generally in this helper's check branch ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L172))
- allocates memory from the first supported memory type bit using `deCtz32(memoryTypeBits)` ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L185))
- binds memory with [`bindBufferMemory()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L197)

### 3. Dedicated-allocation buffer allocator path

When `bufferAllocationKind` is dedicated, [`BufferDedicatedAllocation::createTestBuffer()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L203) is used.

Observed behavior:

- queries dedicated requirements through [`VkMemoryDedicatedRequirements`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L213) chained into [`VkMemoryRequirements2`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L219), fetched by [`getBufferMemoryRequirements2()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L251)
- fails if `requiresDedicatedAllocation == VK_TRUE` for this non-external scenario ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L253))
- requires nonzero `memoryTypeBits` ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L271))
- allocates memory with [`VkMemoryDedicatedAllocateInfo`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L290) and binds with [`bindBufferMemory()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L313)

### 4. Buffer-view construction checks per case

Each instantiated case executes [`BufferViewTestInstance::iterate()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L319), which performs two related buffer-view creations:

1. creates a view using the case's configured `offset` and `range` ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L340))
2. creates a second "complete view size" variant with `range = size` where `size` is fixed to `3*5*7*64` bytes ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L323), [`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L364))

Both view creations use exception handling around [`createBufferView()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L352) / [`createBufferView()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L376), and the case passes if both succeed ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L385)).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Allocation kinds | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` in [`AllocationKind`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L46) |
| Usage variants | `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` and `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` in [`usage[]`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L393) |
| Required format feature per usage | `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT` and `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT` in [`feature[]`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L395) |
| Usage subgroup names | `uniform`, `storage` in [`usageName[]`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L397) |
| Format sweep | integer cast over `VkFormat` from `VK_FORMAT_UNDEFINED + 1` to `VK_CORE_FORMAT_LAST - 1` in [`createBufferViewCreateTests()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L415) |
| Registered offset/range | `offset = 0`, `range = VK_WHOLE_SIZE` in [`BufferViewCaseParameters`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L423) |
| Internal iterate buffer size | constant `3 * 5 * 7 * 64` in [`BufferViewTestInstance::iterate()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L323) |

## Support / Feature Requirements

Observed gates:

- per-case format support is required through [`BufferViewTestCase::checkSupport()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L120), which verifies `properties.bufferFeatures & requiredFeatures`
- dedicated-allocation cases additionally require `VK_KHR_dedicated_allocation` in the same support function ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L128))

No explicit Vulkan-SC preprocessor exclusions were observed in this file's registration loop; behavior differences would come from shared framework/runtime support checks rather than branch removal in this source.

## Verification Methods

Observed pass/fail criteria:

- allocation helper paths fail on buffer creation/memory allocation/binding exceptions or failures with explicit messages ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L161), [`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L192), [`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L197), [`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L306), [`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L313))
- the per-case iterate path fails if either of the two [`createBufferView()`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L352) attempts throws, and passes otherwise ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L385))
- no texel readback/functional shader access is performed in this file; it is object-construction validation only

## Test Principles Observed

- this file frames buffer-view creation as a broad compatibility matrix across core format space, two texel-buffer usages, and two memory-allocation styles
- support checks are kept strict and local: unsupported format-feature combinations are rejected before execution
- dedicated-allocation behavior is checked as a first-class variation, not as an incidental side path
- a second full-range view creation in each test case provides an additional construction sanity check beyond the nominal registered range

## Notes / Uncertainties

- The file computes `formatName` and allocates a `formatGroup` inside the format loop, but in the inspected code path the actual added child is directly attached to `usageGroup` ([`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L417), [`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L418), [`vktApiBufferViewCreateTests.cpp`](../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L432)). This appears to leave `formatGroup` unused; this document records that observation without inferring author intent.
- Because the format loop spans up to `VK_CORE_FORMAT_LAST`, exact generated case count depends on the enum extent in the active headers and is not restated here.
- Functional buffer-view access/contents validation is intentionally outside this file and belongs to [`vktApiBufferViewAccessTests.cpp`](../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1).
