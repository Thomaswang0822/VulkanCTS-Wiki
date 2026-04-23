# [vktApiBufferTests.cpp](../../modules/vulkan/api/vktApiBufferTests.cpp#L748)

## Overview

[`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L748) implements the foundational `api/buffer` subtree registered immediately after [`createObjectManagementTests()`](../../modules/vulkan/api/vktApiTests.cpp#L101) and before the separate `buffer_view` aggregator added by [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L106). The file is implementation-heavy: it covers buffer creation plus memory allocation/binding across many usage-flag combinations, compares suballocated versus dedicated memory paths, probes very large-buffer behavior, and checks that depth/stencil formats do not incorrectly advertise buffer-format support.

Within the requested memory-object slice, this file is coherent on its own because it documents raw buffer object creation/binding. It does not include buffer-view tests, but it directly precedes that adjacent subtree in the API registration order.

## Role of File

Implementation-heavy test file for the `api/buffer` subgroup.

## Source Code

- Primary source: [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L1)
- Declaration: [`vktApiBufferTests.hpp`](../../modules/vulkan/api/vktApiBufferTests.hpp)
- Parent-category registration: [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L102)

## Registration Path

```text
TestPackage::init / TestPackageSC::init
└── api
    └── createTests(testCtx, "api")
        └── createApiTests(apiTests)
            └── createBufferTests(testCtx)
                └── buffer
                    ├── suballocation
                    │   └── recursive usage-flag combination tree
                    │       └── create
                    │           └── sparse/non-sparse creation variants
                    ├── dedicated_alloc
                    │   └── recursive usage-flag combination tree
                    │       └── create
                    │           └── non-sparse creation variant
                    ├── basic
                    │   ├── max_size                    (not in Vulkan SC)
                    │   ├── max_size_sparse             (not in Vulkan SC)
                    │   └── size_max_uint64            (not in Vulkan SC)
                    └── invalid_buffer_features
                        └── one case per depth/stencil format
```

Evidence:

- package-level `api` attachment in [`TestPackage::init()`](../../modules/vulkan/vktTestPackage.cpp#L1349) and [`TestPackageSC::init()`](../../modules/vulkan/vktTestPackage.cpp#L1417)
- parent attachment in [`createApiTests()`](../../modules/vulkan/api/vktApiTests.cpp#L102)
- subgroup construction in [`createBufferTests()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L748)
- recursive usage-tree expansion in [`createBufferUsageCases()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L588)

## Test Hierarchy

The dominant structure is the recursively generated usage-flag tree created by [`createBufferUsageCases()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L588):

```text
api
└── buffer
    ├── suballocation
    │   └── <usage-flag combination tree>
    │       └── create
    │           ├── zero
    │           ├── binding                         (not in Vulkan SC)
    │           ├── binding_residency              (not in Vulkan SC)
    │           ├── binding_aliased                (not in Vulkan SC)
    │           └── binding_residency_aliased      (not in Vulkan SC)
    ├── dedicated_alloc
    │   └── <usage-flag combination tree>
    │       └── create
    │           └── zero
    ├── basic
    │   ├── max_size                               (not in Vulkan SC)
    │   ├── max_size_sparse                        (not in Vulkan SC)
    │   └── size_max_uint64                        (not in Vulkan SC)
    └── invalid_buffer_features
        └── <depth/stencil format name>
```

Observed hierarchy mechanics:

- each recursive level adds one more usage-bit subgroup name using [`getBufferUsageFlagsName()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L542) and [`createBufferUsageCases()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L602)
- once a nonzero accumulated usage mask exists, the helper adds a `create` subgroup containing one test case per allowed buffer-create-flag variant ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L613), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L631))
- dedicated allocation explicitly suppresses sparse variants by limiting `numBufferCreateFlags` to `1` when `allocationKind == ALLOCATION_KIND_DEDICATED` ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L627))

## Test Families

### 1. Buffer creation + allocation + binding across usage combinations

The main family is parameterized by [`BufferCaseParameters`](../../modules/vulkan/api/vktApiBufferTests.cpp#L85) and exercised by [`BufferTestInstance::iterate()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L369) for suballocated memory and [`DedicatedAllocationBufferTestInstance::bufferCreateAndAllocTest()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L389) for dedicated memory.

Observed behavior in the common suballocated path:

- each test runs the same create/allocate/bind sequence for multiple target sizes `1`, `1181`, `15991`, `16384`, plus `~0ull` outside Vulkan SC ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L371))
- [`BufferTestInstance::bufferCreateAndAllocTest()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L185) first creates a minimal buffer to query supported memory types and requirements, then derives a clamped maximum test size from the chosen heap plus platform memory limits ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L206), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L232))
- if creation or allocation fails, the helper repeatedly shrinks the requested size by shifting right four bits until success or a terminal too-small condition ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L244), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L284))
- once memory exists, the test binds it either through [`queueBindSparse()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L353) for sparse buffers or [`bindBufferMemory()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L359) for regular ones
- the pass condition is successful binding for all tested sizes ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L366), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L386))

### 2. Dedicated-allocation buffer creation path

The `dedicated_alloc` branch reuses the same recursive usage-combination hierarchy but swaps in [`DedicatedAllocationBuffersTestCase`](../../modules/vulkan/api/vktApiBufferTests.cpp#L154), whose instances call [`DedicatedAllocationBufferTestInstance::bufferCreateAndAllocTest()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L389).

Observed behavior:

- the dedicated path queries [`VkMemoryDedicatedRequirements`](../../modules/vulkan/api/vktApiBufferTests.cpp#L400) via [`getBufferMemoryRequirements2()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L435)
- it explicitly fails if a non-external buffer reports `requiresDedicatedAllocation == VK_TRUE`, treating that as invalid for this tested scenario ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L437))
- it allocates memory with [`VkMemoryDedicatedAllocateInfo`](../../modules/vulkan/api/vktApiBufferTests.cpp#L504) chained into [`VkMemoryAllocateInfo`](../../modules/vulkan/api/vktApiBufferTests.cpp#L511)
- like the suballocated path, it shrinks oversized requests until buffer creation and memory allocation succeed, then requires [`bindBufferMemory()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L536) to succeed
- dedicated allocation registration excludes sparse create-flag combinations by construction ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L627))

### 3. Usage-flag combination generation

A major principle of this file is exhaustive combination generation over a fixed set of nine buffer usage bits listed in [`bufferUsageModes`](../../modules/vulkan/api/vktApiBufferTests.cpp#L592):

- `TRANSFER_SRC`
- `TRANSFER_DST`
- `UNIFORM_TEXEL_BUFFER`
- `STORAGE_TEXEL_BUFFER`
- `UNIFORM_BUFFER`
- `STORAGE_BUFFER`
- `INDEX_BUFFER`
- `VERTEX_BUFFER`
- `INDIRECT_BUFFER`

Observed generation details:

- [`createBufferUsageCases()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L588) recursively walks all combinations by OR-ing one additional usage bit at a time ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L602), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L608))
- leaf tests are instantiated only when the accumulated mask is nonzero ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L613))
- for suballocated buffers, each usage-mask leaf is crossed with up to five create-flag modes: `0`, `SPARSE_BINDING`, `SPARSE_BINDING|SPARSE_RESIDENCY`, `SPARSE_BINDING|SPARSE_ALIASED`, and `SPARSE_BINDING|SPARSE_RESIDENCY|SPARSE_ALIASED` outside Vulkan SC ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L616))

### 4. Large-buffer boundary tests

The `basic` branch registers three non-Vulkan-SC function cases through [`addFunctionCase()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L768) to [`addFunctionCase()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L774), all backed by [`testLargeBuffer()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L680).

Observed behavior:

- `max_size` requests `maxBufferSize` from maintenance4 when `useMaxBufferSize == true` ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L690))
- `max_size_sparse` does the same but with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT`, additionally clamping to `sparseAddressSpaceSize` if needed ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L694))
- `size_max_uint64` requests `std::numeric_limits<uint64_t>::max()` and accepts either successful creation with adequate memory requirements or one of the explicitly allowed out-of-memory errors ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L711), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L723))
- support gating is handled by [`checkMaintenance4Support()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L731), which requires `VK_KHR_maintenance4` when needed and rejects above-`maxBufferSize` requests on implementations that expose maintenance4 ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L733), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L735))

### 5. Invalid depth/stencil buffer-format exposure checks

The `invalid_buffer_features` branch uses [`testDepthStencilBufferFeatures()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L658) for every format in [`formats::depthAndStencilFormats`](../../modules/vulkan/api/vktApiBufferTests.cpp#L785).

Observed behavior:

- for each depth/stencil format, the test queries [`VkFormatProperties`](../../modules/vulkan/api/vktApiBufferTests.cpp#L663)
- it passes only when `bufferFeatures == 0x0` ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L666))
- if any depth/stencil format advertises nonzero buffer features, the test fails ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L669))

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Allocation kinds | `ALLOCATION_KIND_SUBALLOCATED`, `ALLOCATION_KIND_DEDICATED` in [`AllocationKind`](../../modules/vulkan/api/vktApiBufferTests.cpp#L49) |
| Buffer usage bits considered by the recursive tree | nine flags listed in [`bufferUsageModes`](../../modules/vulkan/api/vktApiBufferTests.cpp#L592) |
| Sharing mode in generated create tests | always `VK_SHARING_MODE_EXCLUSIVE` in generated [`BufferCaseParameters`](../../modules/vulkan/api/vktApiBufferTests.cpp#L635) |
| Suballocated create-flag variants | `0`, `SPARSE_BINDING`, `SPARSE_BINDING|SPARSE_RESIDENCY`, `SPARSE_BINDING|SPARSE_ALIASED`, `SPARSE_BINDING|SPARSE_RESIDENCY|SPARSE_ALIASED` in [`bufferCreateFlags`](../../modules/vulkan/api/vktApiBufferTests.cpp#L616) |
| Dedicated create-flag variants | only `0`, because sparse variants are disabled for dedicated allocation at [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L627) |
| Iterated buffer sizes in the main create/bind tests | `1`, `1181`, `15991`, `16384`, and `~0ull` outside Vulkan SC in [`testSizes`](../../modules/vulkan/api/vktApiBufferTests.cpp#L371) |
| Shrink policy for oversized requests | right shift by `4` bits per retry in both main allocation helpers ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L224), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L450)) |
| Large-buffer parameters | `bufferSize`, `useMaxBufferSize`, `flags` in [`LargeBufferParameters`](../../modules/vulkan/api/vktApiBufferTests.cpp#L672) |
| Large-buffer registered cases | `max_size`, `max_size_sparse`, `size_max_uint64` in [`createBufferTests()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L768) |
| Invalid-buffer-feature cases | one per depth/stencil format from [`formats::depthAndStencilFormats`](../../modules/vulkan/api/vktApiBufferTests.cpp#L785) |

## Support / Feature Requirements

Observed support gates:

- sparse binding/residency/aliased create modes require the corresponding core features through [`BuffersTestCase::checkSupport()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L135)
- dedicated allocation cases require device functionality `VK_KHR_dedicated_allocation` through [`DedicatedAllocationBuffersTestCase::checkSupport()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L175)
- maintenance4-specific large-buffer cases are gated by [`checkMaintenance4Support()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L731)
- Vulkan SC builds exclude sparse create-flag variants, the `~0ull` large size in the regular size loop, and all `basic` large-buffer cases through preprocessor guards ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L373), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L618), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L766))

## Verification Methods

Observed pass/fail logic:

- the main create/bind families pass when buffer creation, memory allocation, and final binding succeed for every tested size ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L380), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L386), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L539))
- both allocation helpers explicitly fail if reported memory requirement size is smaller than the chosen buffer size ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L273), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L491))
- large-buffer tests pass either on successful creation with `memoryRequirements.size >= requestedSize` or on allowed OOM errors ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L717), [`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L723))
- invalid-buffer-feature tests pass only when queried `bufferFeatures` is exactly zero for depth/stencil formats ([`vktApiBufferTests.cpp`](../../modules/vulkan/api/vktApiBufferTests.cpp#L666))

## Test Principles Observed

- this file treats buffer validation as a combinatorial API-contract problem: usage-mask combinations, create-flag combinations, memory-allocation style, and size regime are crossed systematically
- the main create/bind tests are intentionally resilient to platform memory pressure, shrinking requests until a realistic allocation path is found rather than assuming fixed heap availability
- dedicated allocation is treated as a distinct API path with its own requirement-query mechanism, rather than as a trivial variant of ordinary allocation
- very large buffer requests are validated contractually rather than performance-wise: success is accepted, but certain OOM results are also considered correct outcomes

## Notes / Uncertainties

- The recursive tree produces many usage combinations, but this document stops at the meaningful generator level rather than enumerating every generated subgroup path.
- The file does not verify buffer contents; it verifies creation, memory requirements, allocation, and binding behavior. Content-level access is delegated to adjacent tests such as the separate `buffer_view` subtree.
- [`getPlatformMemoryLimits()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L57) and [`getMaxBufferSize()`](../../modules/vulkan/api/vktApiBufferTests.cpp#L66) clearly influence the chosen upper test sizes, but the exact runtime values depend on the executing platform and are therefore not knowable from static inspection alone.
