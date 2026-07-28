## Overview

**Core question:** Are Vulkan memory requirements invariant: must the same resource create info always report the same `size`, `alignment`, and `memoryTypeBits`, and must the per-resource, pNext-chaining, and per-createInfo query paths agree with each other and with their dedicated-allocation counterparts?

- Covers the `invariance` test family inside the `api` test category, registered by [createMemoryRequirementInvarianceTests()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L760).
- Source file: [`vktApiMemoryRequirementInvarianceTests.cpp`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L1); header: [`vktApiMemoryRequirementInvarianceTests.hpp`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.hpp#L1).
- Three test case leaves exercise three distinct invariance properties: allocation-order invariance of `size` (`random`), alignment matching across identically-created resources plus cross-method consistency of `VkMemoryRequirements` and size monotonicity (`memory_requirements_matching`), and matching of `VkMemoryDedicatedRequirements` between the per-resource and per-createInfo query paths (`memory_dedicated_requirements_matching`).
- All checks are host-side; no shader, queue submission, or device-side execution is involved.
- The page explains each invariance property, the runtime flow that exercises it, and what a failure implies.

## Background Knowledge

- `vkGetBufferMemoryRequirements` / `vkGetImageMemoryRequirements` (Vulkan 1.0) return a `VkMemoryRequirements` for an already-created `VkBuffer` / `VkImage`. The reported `size`, `alignment`, and `memoryTypeBits` describe how the resource must be bound to device memory.
- `vkGetBufferMemoryRequirements2` / `vkGetImageMemoryRequirements2` (from `VK_KHR_get_memory_requirements2`, Vulkan 1.1) are the pNext-chaining equivalents. They let the caller attach extension structures such as `VkMemoryDedicatedRequirements` to the query.
- `vkGetDeviceBufferMemoryRequirements` / `vkGetDeviceImageMemoryRequirements` (from `VK_KHR_maintenance4`, Vulkan 1.3) take a `VkBufferCreateInfo` / `VkImageCreateInfo` directly, without first creating the resource. Per the maintenance4 specification, the returned requirements must match what `vkGet*MemoryRequirements2` would report for a resource created with the same create info.
- `VkMemoryDedicatedRequirements` (from `VK_KHR_dedicated_allocation`, Vulkan 1.1) is chained into `VkMemoryRequirements2::pNext` and reports `prefersDedicatedAllocation` and `requiresDedicatedAllocation`, telling the caller whether a dedicated `VkDeviceMemory` allocation is recommended or required for the resource.
- The Vulkan specification treats `VkMemoryRequirements` as a property of the resource's create info and the implementation's memory layout, not of the surrounding allocation history. A larger requested extent (for an image) or size (for a buffer) with otherwise-identical create-info fields must not produce a smaller reported `size`.

## Registration Hierarchy

```text
api.invariance
├── random
├── memory_requirements_matching
└── memory_dedicated_requirements_matching
```

[vktApiTests.cpp#L122](../../../modules/vulkan/api/vktApiTests.cpp#L122) adds the `invariance` test family to the `api` test category. The three test case leaves are added directly under the family by [createMemoryRequirementInvarianceTests()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L760-L770); there are no intermediate nodes. The function name embeds `MemoryRequirementInvariance`, but the registered group name is `invariance`, so the mustpass identifier is `dEQP-VK.api.invariance.*` rather than `dEQP-VK.api.memory_requirement_invariance.*`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values / observed range | Meaning in this test | Evidence |
|-----------|------------------------------------|----------------------|----------|
| Test case leaf | `random`, `memory_requirements_matching`, `memory_dedicated_requirements_matching` | Selects which invariance property is exercised; each leaf maps to a distinct `TestType` value | [createMemoryRequirementInvarianceTests()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L760-L770) |
| Internal test type | `TT_BASIC_INVARIANCE`, `TT_REQUIREMENTS_MATCHING`, `TT_DEDICATED_REQUIREMENTS` | Enum dispatched in `createInstance()` to select the `TestInstance` subclass | [TestType enum](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L46-L51), [createInstance()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L746-L752) |
| Resource type (`random` only) | `buffer`, `image` | Randomly chosen per allocation slot inside `random`; the matching leaves fix both a buffer and an image | [InvarianceInstance::iterate()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L362-L367) |
| Buffer size (`random` only) | 7 to 1030 bytes | `(deRandom_getUint32() % 1024) + 7`; chosen to provoke alignment edge cases | [BufferAllocator ctor](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L105) |
| Buffer usage (`random` only) | one of 9 `VkBufferUsageFlagBits` shifted by random index 0..8 | `1 << (deRandom_getUint32() % 9)`; exercises each usage bit independently | [BufferAllocator ctor](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L107) |
| Image format (`random` only) | runtime-discovered subset of `formats::allFormats` | Filtered by supported linear/optimal tiling and by available extensions (`VK_KHR_sampler_ycbcr_conversion`, `VK_EXT_ycbcr_2plane_444_formats`, `VK_IMG_format_pvrtc`, `VK_KHR_maintenance5`) | [format scan loop](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L285-L318) |
| Image tiling (`random` only) | `VK_IMAGE_TILING_LINEAR`, `VK_IMAGE_TILING_OPTIMAL` | Randomly chosen when at least one linear-tiled format is supported | [ImageAllocator ctor](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L178) |
| Memory type (`random` only) | one of 11 legal `MemoryRequirement` combinations | Random index into the device-supported subset of `legalMemoryTypes`, covering `Any`, `HostVisible`, `Local`, `LazilyAllocated`, `Protected`, and combinations | [legalMemoryTypes array](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L54-L66), [heap matching loop](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L323-L334) |
| Allocation mode (`random` only) | suballocated, dedicated | Randomly chosen when `VK_KHR_dedicated_allocation` is supported | [BufferAllocator ctor](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L103), [ImageAllocator ctor](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L176) |
| Test cycles (`random` only) | 1000 (non-VKSC), 100 (VKSC) | Number of resource slots created, deallocated, and re-allocated in shuffled order | [testCycles definition](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L40-L44) |
| Matching-leaf object counts | 5 of each (`VkImage`, `VkBuffer`) | Number of identically-created objects used to verify alignment matching and size monotonicity | [AlignmentMatchingInstance::iterate()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L456) |
| Matching-leaf base extents / sizes | image `32×31×1`, buffer `1023` bytes | Fixed base dimensions used by the alignment and monotonicity loops | [AlignmentMatchingInstance::iterate()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L459-L460) |
| Random seed (`random` only) | `0x600613` | Fixed seed so the same configuration set is exercised across runs and platforms | [createInstance()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L751) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf verifies a distinct invariance property and dispatches to a different `TestInstance` via [InvarianceCase::createInstance()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L746-L752). The two `*_matching` leaves share the same `AlignmentMatchingInstance` class but differ in the `TestType` value passed to it; the `random` leaf uses a separate `InvarianceInstance`.

### random: allocation-order invariance

For 1000 randomly-generated buffer and image configurations (100 under VKSC), the leaf records the `size` reported by `vkGetBufferMemoryRequirements` / `vkGetImageMemoryRequirements` for a reference allocation order, then deallocates every resource, re-allocates them in a shuffled order, and re-queries `size`. The two `size` values for the same configuration must be identical. The property under test is that the implementation's memory-requirement query is independent of when the resource is created relative to other live allocations and of the order in which resources are created.

### memory_requirements_matching: alignment, cross-method, and monotonicity consistency

The leaf creates a fixed `VkBuffer` (1023 bytes, `TRANSFER_DST` usage) and `VkImage` (`R8G8B8A8_UNORM`, `32×31×1`, optimal tiling, `TRANSFER_SRC` usage) plus five additional objects of each kind built from identical create infos. It then verifies three properties:

- Alignments reported for all objects created with the same create info must match.
- `vkGetDeviceBufferMemoryRequirements` / `vkGetDeviceImageMemoryRequirements` must report the same `size`, `alignment`, and `memoryTypeBits` as `vkGetBufferMemoryRequirements2` / `vkGetImageMemoryRequirements2`.
- For resources created with otherwise-identical parameters, a larger requested extent or buffer size must not produce a smaller reported `size`.

### memory_dedicated_requirements_matching: dedicated-allocation requirements consistency

Reuses the same `AlignmentMatchingInstance` machinery as `memory_requirements_matching` with `TestType = TT_DEDICATED_REQUIREMENTS`. In addition to the alignment, cross-method, and monotonicity checks, it chains `VkMemoryDedicatedRequirements` into both `vkGet*MemoryRequirements2` (against the created resource) and `vkGetDevice*MemoryRequirements` (against the create info), and verifies that `prefersDedicatedAllocation` and `requiresDedicatedAllocation` match across the two query paths.

## Shader Analysis

No shader is involved in this test family. All memory-requirement queries are host-side Vulkan entry points, and all validation is performed on the host. No `### Representative Shader Walkthrough` subsection is needed.

## Runtime Execution and Result Checking

### random leaf

The instance [`InvarianceInstance`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L244) executes the following host-side flow:

- Initializes a `deRandom` state with the fixed seed `0x600613`.
- Probes device extension availability (`VK_KHR_dedicated_allocation`, `VK_KHR_sampler_ycbcr_conversion`, `VK_EXT_ycbcr_2plane_444_formats`, `VK_IMG_format_pvrtc`, `VK_KHR_maintenance5`) and the physical-device memory properties.
- Builds two supported-format lists by iterating `formats::allFormats` and probing `vkGetPhysicalDeviceImageFormatProperties` for both `VK_IMAGE_TILING_LINEAR` and `VK_IMAGE_TILING_OPTIMAL`, dropping formats whose required extension is not enabled.
- Builds a supported-memory-type list by matching the 11 `legalMemoryTypes` entries against the device's `VkMemoryType` property flags.
- For each of `testCycles` slots, randomly picks `BufferAllocator` or `ImageAllocator` and constructs the allocator. The allocator constructor records the random `size`, usage, format, tiling, and memory type internally without creating the resource yet.
- Reference pass: allocates each resource, queries its `size` via `vkGetBufferMemoryRequirements` / `vkGetImageMemoryRequirements`, stores the value in `refSizes[i]`, then deallocates the resource. Resources that throw `tcu::NotSupportedError` are marked `supported[i] = false` and skipped for the rest of the test.
- Builds a permutation of `[0, testCycles)` by swapping random pairs.
- Shuffled pass: re-allocates every supported resource in the shuffled order.
- Verification pass: re-queries `size` for each supported resource in the shuffled order and compares against `refSizes[i]`. A mismatch sets `success = false` and logs `Object <i> size mismatch (<val> != <ref>)`.
- Tears down all live resources. The case passes if no mismatch was observed, and fails with `One or more allocation is not invariant` otherwise.

If every allocation was unsupported, the case throws `NotSupportedError` and is reported as skipped rather than failed.

### memory_requirements_matching and memory_dedicated_requirements_matching leaves

The instance [`AlignmentMatchingInstance`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L435) executes the following host-side flow:

- Creates one base `VkImage` (`32×31×1`, `R8G8B8A8_UNORM`, optimal tiling) and one base `VkBuffer` (1023 bytes, `TRANSFER_DST`), then queries their `VkMemoryRequirements` via `vkGetImageMemoryRequirements` / `vkGetBufferMemoryRequirements`.
- Creates five additional `VkImage` objects and five additional `VkBuffer` objects from the same create infos, queries each one's requirements, and verifies that the `alignment` field matches the base object's `alignment`. A mismatch logs an `Alignments for all VkImage/VkBuffer objects created with the same create infos should match` message.
- When `VK_KHR_get_memory_requirements2` is supported (non-VKSC): queries `vkGet*MemoryRequirements2` against the created resource and `vkGetDevice*MemoryRequirements` against the create info. Verifies that `size`, `alignment`, and `memoryTypeBits` are identical across the two paths. A mismatch logs a `vkGetDevice*MemoryRequirements and vkGet*MemoryRequirements2 report different memory requirements` message.
- When `m_testType == TT_DEDICATED_REQUIREMENTS`: chains `VkMemoryDedicatedRequirements` into both query paths and verifies that `prefersDedicatedAllocation` and `requiresDedicatedAllocation` match between `vkGet*MemoryRequirements2` and `vkGetDevice*MemoryRequirements`. A mismatch logs the corresponding `VkMemoryDedicatedRequirements ... doesn't match ...` message.
- For the size-monotonicity check: creates five additional `VkImage` objects whose extent grows as `width + (idx % 2) * idx, height + idx` and five additional `VkBuffer` objects whose size grows as `1023 + idx`. Queries each one's `size` and verifies that the base `size` is never greater than the grown `size`. A mismatch logs a `Size memory requirement for VkImage/VkBuffer should never be greater than ...` message.
- The case passes if no mismatch was observed, and fails otherwise.

The source log strings for the monotonicity check contain a typo (`requiremen` instead of `requirement`) and an incorrect reference to `VkImageCreateInfo` in the buffer branch; both are test-side log-message defects and do not affect what is checked.

## Failure Meaning

### Failure Cause Mapping

For the primary behavioral axis (test case leaf):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `random` | Allocation-order invariance violation: same create info reported different `size` between the reference and shuffled allocation passes |
| `memory_requirements_matching` | Alignment mismatch across identically-created resources; or cross-method `VkMemoryRequirements` mismatch between `vkGetDevice*MemoryRequirements` and `vkGet*MemoryRequirements2`; or size-monotonicity violation where a larger resource reported a smaller `size` |
| `memory_dedicated_requirements_matching` | Any of the `memory_requirements_matching` causes, plus mismatch of `VkMemoryDedicatedRequirements::prefersDedicatedAllocation` or `requiresDedicatedAllocation` between the per-resource and per-createInfo query paths |

### Cause Analysis

#### Allocation-order invariance violation

**Possible failure symptoms:** the `random` leaf returns `TestStatus::fail` with the message `One or more allocation is not invariant`. The test log contains one or more `Object <i> size mismatch (<val> != <ref>)` lines naming the resource slot that produced a different `size` in the shuffled pass than in the reference pass.

**Possible implementation causes:** the implementation's `vkGetBufferMemoryRequirements` / `vkGetImageMemoryRequirements` returned a `size` value that depends on allocator state, on the set of currently live allocations, or on the order in which queries are issued, rather than being a deterministic function of the resource's create info. The Vulkan specification requires `VkMemoryRequirements::size` to be a property of the create info and the implementation's memory layout, not of the surrounding allocation history. Whether the divergence comes from a suballocator that reports different padding based on heap occupancy, or from a driver query path that consults live-resource state, requires source-level investigation against the specific failing slot's create info and the surrounding shuffle pattern.

#### Alignment mismatch across identically-created resources

**Possible failure symptoms:** the `memory_requirements_matching` or `memory_dedicated_requirements_matching` leaf fails with the log message `Alignments for all VkImage objects created with the same create infos should match` or the corresponding `VkBuffer` variant.

**Possible implementation causes:** the implementation's `vkGet*MemoryRequirements` returned different `alignment` values for two resources created from identical `VkBufferCreateInfo` / `VkImageCreateInfo`. The Vulkan specification requires `VkMemoryRequirements` to be a pure function of the create info and the implementation's memory layout. A driver that derives alignment from an internal allocator slot rather than from the create info would produce this symptom. Source-level investigation is needed to identify which pair of objects diverged, since the source does not log per-object alignment values.

#### Cross-method requirements mismatch

**Possible failure symptoms:** the `memory_requirements_matching` or `memory_dedicated_requirements_matching` leaf fails with a log message reporting that `vkGetDeviceBufferMemoryRequirements` / `vkGetDeviceImageMemoryRequirements` and `vkGetBufferMemoryRequirements2` / `vkGetImageMemoryRequirements2` returned different memory requirements.

**Possible implementation causes:** the implementation's per-createInfo query (`vkGetDevice*MemoryRequirements`, `VK_KHR_maintenance4`) and per-resource query (`vkGet*MemoryRequirements2`) returned `VkMemoryRequirements` fields that disagree on `size`, `alignment`, or `memoryTypeBits`. Per the `VK_KHR_maintenance4` specification, the per-createInfo query must return identical requirements to those that would be returned by the per-resource query for a resource created with the same create info. A driver that implements the two query paths through different code paths and lets them drift is the most plausible cause. Confirming which field diverged requires source-level inspection of the logged requirements; the source emits a fixed mismatch message and does not log the differing field values.

#### Dedicated-allocation requirements mismatch

**Possible failure symptoms:** the `memory_dedicated_requirements_matching` leaf fails with a log message reporting that `VkMemoryDedicatedRequirements` returned by `vkGetBufferMemoryRequirements2` / `vkGetImageMemoryRequirements2` does not match the one returned by `vkGetDeviceBufferMemoryRequirements` / `vkGetDeviceImageMemoryRequirements`.

**Possible implementation causes:** the implementation's `vkGet*MemoryRequirements2` (chained against the created resource) and `vkGetDevice*MemoryRequirements` (chained against the create info) returned `VkMemoryDedicatedRequirements` whose `prefersDedicatedAllocation` or `requiresDedicatedAllocation` flags disagree. Per `VK_KHR_dedicated_allocation`, the dedicated-allocation preference and requirement are properties of the resource's create info and the implementation's allocation strategy, not of whether the resource has been created yet. Source-level investigation is needed to determine which flag diverged and in which direction; the source emits a fixed mismatch message and does not log the per-field values.

#### Size-monotonicity violation

**Possible failure symptoms:** the `memory_requirements_matching` or `memory_dedicated_requirements_matching` leaf fails with a log message reporting that the size memory requirement for a `VkImage` / `VkBuffer` was greater than that of another resource created with a greater extent or size when all other creation parameters were identical.

**Possible implementation causes:** the implementation reported a smaller `size` for a resource with a larger requested extent (image) or larger requested size (buffer), even though all other create-info fields were identical. The Vulkan specification requires `VkMemoryRequirements::size` to be non-decreasing in the requested extent or size when other creation parameters are fixed. A driver that rounds sizes through a non-monotonic internal allocator would produce this symptom. Source-level investigation is needed to identify which `idx` value in the monotonicity loop triggered the violation; the source does not log per-idx sizes.

## Case Pruning

### Requirement-based pruning

[`InvarianceCase::checkSupport()`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L754-L758) gates the two matching leaves at registration time:

- `VK_KHR_maintenance4` is required for `memory_requirements_matching` and `memory_dedicated_requirements_matching` ([L756-L757](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L756-L757)). The `random` leaf has no feature gate at `checkSupport` time.

The `random` leaf probes device functionality at runtime inside [`InvarianceInstance::iterate()`](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L264), but does not skip the case based on these probes; they only adjust which formats and allocation modes are exercised:

- `VK_KHR_dedicated_allocation` controls whether `BufferAllocator` / `ImageAllocator` may pick the dedicated-allocation path ([L272](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L272), [L103](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L103), [L176](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L176)).
- `VK_KHR_sampler_ycbcr_conversion` gates YCbCr format support ([L273](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L273), [L287-L288](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L287-L288)).
- `VK_EXT_ycbcr_2plane_444_formats` gates the corresponding extension formats ([L274](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L274), [L290-L291](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L290-L291)).
- `VK_IMG_format_pvrtc` gates PVRTC format support ([L275](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L275), [L293-L294](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L293-L294)).
- `VK_KHR_maintenance5` gates `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` (non-VKSC only, [L277-L302](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L277-L302)).
- `VK_KHR_get_memory_requirements2` gates the cross-method query path in `AlignmentMatchingInstance::iterate()` ([L528](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L528)). When the extension is absent, the cross-method and dedicated-requirements portions are silently skipped rather than failing.

The `random` leaf also probes each candidate image format against `vkGetPhysicalDeviceImageFormatProperties` for both linear and optimal tiling; formats that return non-`VK_SUCCESS` are dropped from the per-tiling supported-format list rather than failing the case ([L307-L317](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L307-L317)). Individual resource allocations that throw `tcu::NotSupportedError` are marked `supported[i] = false` and excluded from the invariance check ([L382-L385](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L382-L385)); if every allocation was unsupported, the case throws `NotSupportedError` and is reported as skipped ([L388-L389](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L388-L389)).

### Design-based pruning

- **PVRTC1 power-of-2 dimensions:** when the randomly chosen format is a PVRTC1 format, the image allocator overrides the random extent with `1 << (random % 4 + 1)` for both width and height, satisfying VUID-VkImageCreateInfo-format-09583 and VUID-VkImageCreateInfo-format-09584 ([L185-L189](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L185-L189)).
- **YCbCr 420/422 width/height alignment:** for `*_420*` or `*_422*` YCbCr formats, the width is aligned to a multiple of 2; for `*_420*` formats, the height is also aligned to a multiple of 2 ([L193-L198](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L193-L198)).
- **Random seed fixed:** the `random` leaf uses seed `0x600613` so the same configuration set is exercised across runs and platforms ([L751](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L751)).
- **Test cycles reduced on VKSC:** the `random` leaf allocates 1000 resources per run on non-VKSC builds and 100 on VKSC builds to keep VKSC memory pressure bounded ([L40-L44](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L40-L44)).
- **VKSC exclusion of the cross-method block:** the entire `VK_KHR_get_memory_requirements2` query path is wrapped in `#ifndef CTS_USES_VULKANSC` ([L530-L678](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L530-L678)), so on VKSC the two matching leaves exercise only alignment matching and size monotonicity, never cross-method or dedicated-requirements consistency.

## Key Takeaways

- The `invariance` test family verifies three distinct invariance properties of Vulkan memory-requirement queries: allocation-order invariance of `size` (`random`), alignment matching across identically-created resources plus cross-method and monotonicity consistency (`memory_requirements_matching`), and dedicated-allocation requirements matching between the per-resource and per-createInfo query paths (`memory_dedicated_requirements_matching`).
- All three properties are host-side: no shader, queue submission, or device-side execution is involved. The test exercises the `vkGet*MemoryRequirements`, `vkGet*MemoryRequirements2`, and `vkGetDevice*MemoryRequirements` entry points and the `VkMemoryDedicatedRequirements` pNext chain.
- The `random` leaf uses a fixed seed (`0x600613`) and a constrained random matrix (11 legal memory type combinations, 9 single-bit buffer usage flags, supported image formats only, optional dedicated allocation) to exercise the same invariance surface deterministically across runs and platforms.
- The two `*_matching` leaves are gated by `VK_KHR_maintenance4` at `checkSupport` time because `vkGetDevice*MemoryRequirements` is the maintenance4 entry point that the cross-method consistency check compares against.
- See `## Failure Meaning` for how to interpret a failure: each symptom maps to a specific invariance property violation, and confirming which field diverged requires source-level investigation because the source log strings do not name the differing field values.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [createMemoryRequirementInvarianceTests()](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L760-L770) | Builds the `invariance` tree with the three test case leaves |
| Parent registration | [vktApiTests.cpp#L122](../../../modules/vulkan/api/vktApiTests.cpp#L122) | Adds the `invariance` test family to the `api` test category |
| Header declaration | [vktApiMemoryRequirementInvarianceTests.hpp](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.hpp#L1) | Public entry point declaration |
| Test case class | [InvarianceCase](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L727-L758) | `TestCase` subclass; `createInstance()` dispatches by `TestType`, `checkSupport()` enforces `VK_KHR_maintenance4` |
| TestType enum | [TestType](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L46-L51) | Internal enum: `TT_BASIC_INVARIANCE`, `TT_REQUIREMENTS_MATCHING`, `TT_DEDICATED_REQUIREMENTS` |
| Random-leaf instance | [InvarianceInstance](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L244-L433) | Allocates and re-allocates 1000 resources in shuffled order; compares `size` across passes |
| Matching-leaf instance | [AlignmentMatchingInstance](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L435-L725) | Alignment matching, cross-method query comparison, dedicated-requirements comparison, size monotonicity |
| Buffer allocator | [BufferAllocator](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L82-L150) | Random buffer create-info generator and allocator used by `random` |
| Image allocator | [ImageAllocator](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L152-L242) | Random image create-info generator and allocator used by `random`; contains PVRTC1 and YCbCr extent alignment |
| Legal memory type combinations | [legalMemoryTypes array](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L54-L66) | 11 `MemoryRequirement` combinations the `random` leaf draws from |
| Test cycles constant | [testCycles definition](../../../modules/vulkan/api/vktApiMemoryRequirementInvarianceTests.cpp#L40-L44) | 1000 on non-VKSC, 100 on VKSC |
| Mustpass listing | [api.txt](../../../mustpass/main/vk-default/api.txt) | Three registered leaves under `dEQP-VK.api.invariance.*` |
