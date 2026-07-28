## Overview

**Core question:** For every core Vulkan format the implementation advertises as supporting uniform or storage texel buffer usage, can `vkCreateBufferView` succeed when the buffer is bound through both suballocated and dedicated-allocation memory?

[`vktApiBufferViewCreateTests.cpp`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L1) implements the `buffer_view.create` test family. The family is registered as the `create` child of the `buffer_view` group at [`createBufferViewTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L78-L84), which the `api` test category mounts via [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L106).

- The family sweeps every core Vulkan format from `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST` and asks the implementation to create a `VkBufferView` for each format that the device reports as supporting the corresponding texel buffer feature.
- Two intermediate nodes split the family by memory binding strategy: `suballocation` exercises the standard `vkAllocateMemory` plus `vkBindBufferMemory` path, and `dedicated_alloc` exercises the `VK_KHR_dedicated_allocation` path with `VkMemoryDedicatedAllocateInfo` in the `pNext` chain.
- Each allocation kind nests a `uniform` and a `storage` intermediate node, selecting `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` or `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` and the matching `VK_FORMAT_FEATURE_*_TEXEL_BUFFER_BIT` flag.
- Each test case leaf is named after a Vulkan format (for example, `r8_unorm`). The mustpass file lists 736 test case leaves under this family.

## Background Knowledge

- **Texel buffer view.** A `VkBufferView` reinterprets a region of a `VkBuffer` as a one-dimensional array of texels in a specific `VkFormat`. The buffer must have been created with `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` (read-only access from a `uniformBuffer` descriptor) or `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` (read-write access from a `storageBuffer` descriptor). The chosen `VkFormat` must support the matching `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT` or `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT` buffer feature, as reported by `vkGetPhysicalDeviceFormatProperties`.
- **Suballocation versus dedicated allocation.** Suballocation binds a buffer to a region of a larger `VkDeviceMemory` allocation queried through `vkGetBufferMemoryRequirements` and bound with `vkBindBufferMemory`. Dedicated allocation, introduced by `VK_KHR_dedicated_allocation` and promoted to Vulkan 1.1, binds a buffer to a `VkDeviceMemory` whose `VkMemoryDedicatedAllocateInfo` pNext pins it to that single resource. For non-external resources, the Vulkan spec requires `VkMemoryDedicatedRequirements::requiresDedicatedAllocation` to be `VK_FALSE`; the test asserts this invariant before allocating.

## Registration Hierarchy

```text
api.buffer_view.create
├── suballocation
└── dedicated_alloc
```

The `suballocation` and `dedicated_alloc` intermediate nodes each contain `uniform` and `storage` intermediate nodes, which in turn contain one test case leaf per core Vulkan format. Deeper levels are listed in `## Parameter Dimensions and Observed Values` and `## Behavior Parameters` rather than in this tree, per the Level-3 hierarchy contract.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Allocation kind | `suballocation`, `dedicated_alloc` | Selects the `IBufferAllocator` subclass and the Vulkan memory binding API path exercised for the buffer that backs the view. | [`AllocationKind`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L46-L52), registered at [`vktApiBufferViewCreateTests.cpp#L404-L408`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L404-L408) |
| Usage type | `uniform`, `storage` | Sets `VkBufferUsageFlags` to `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` or `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` and gates the matching `VK_FORMAT_FEATURE_*_TEXEL_BUFFER_BIT` requirement. | [`usage` and `feature` arrays](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L393-L396) |
| Format | `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST - 1` | Each value becomes a test case leaf and is passed as `VkBufferViewCreateInfo::format`. Covers all core Vulkan 1.0 formats, including color, compressed, depth-stencil, and packed formats; unsupported combinations are skipped by `checkSupport()`. | [format loop](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L415) |
| Buffer view range (primary view) | `VK_WHOLE_SIZE` | The primary `VkBufferView` is created with `range = VK_WHOLE_SIZE`, exercising the implementation's whole-buffer view path. | [`range` constant](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L392) |
| Buffer view range (complete view) | explicit buffer size, `3 * 5 * 7 * 64` bytes | A second `VkBufferView` is created with an explicit `range` equal to the buffer size, exercising the explicit-range path. | [`completeBufferViewCreateInfo`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L362-L372) |
| Buffer offset | `0` | Both views use `offset = 0`, avoiding any `minTexelBufferOffsetAlignment` constraint. | [`BufferViewCaseParameters`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L56-L64) |
| Buffer size | `3 * 5 * 7 * 64` bytes (6720 bytes) | A non-power-of-two size chosen so the test does not rely on alignment assumptions baked into common buffer sizes. | [`iterate()`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L323) |

## Behavior Parameters

The primary behavioral axis is the allocation kind intermediate node (`suballocation` versus `dedicated_alloc`). It selects which `IBufferAllocator` subclass runs and therefore which Vulkan memory binding API path is exercised. The `uniform` and `storage` intermediate nodes are a secondary axis: they change `VkBufferUsageFlags` and the required `VkFormatFeatureFlags` but do not change the overall test flow. Format leaves are a coverage sweep, not a behavioral axis, and are skipped per-format when the implementation does not report the matching feature.

### `suballocation` — buffer view creation over a suballocated buffer

The test creates the buffer with `vkCreateBuffer`, queries its memory requirements with `vkGetBufferMemoryRequirements`, allocates a `VkDeviceMemory` with `vkAllocateMemory` using the first set bit of `memoryTypeBits`, and binds the buffer with `vkBindBufferMemory`. This is the standard Vulkan 1.0 memory binding path. The test then creates two `VkBufferView` objects against this buffer: one with `range = VK_WHOLE_SIZE` and one with the explicit buffer size.

### `dedicated_alloc` — buffer view creation over a dedicated allocation

The test creates the buffer with `vkCreateBuffer`, queries its memory requirements with `vkGetBufferMemoryRequirements2` using a `VkMemoryDedicatedRequirements` pNext, and requires the implementation to report `requiresDedicatedAllocation == VK_FALSE` for this non-external buffer. The test then allocates a `VkDeviceMemory` with `vkAllocateMemory` using a `VkMemoryDedicatedAllocateInfo` pNext that pins the allocation to this buffer, and binds the buffer with `vkBindBufferMemory`. This path exercises the `VK_KHR_dedicated_allocation` extension semantics that Vulkan 1.1 promoted to core. The same two `VkBufferView` objects are created as in the suballocation case.

## Shader Analysis

No shader is involved in this test family. The test exercises only host-side Vulkan object creation and memory binding APIs; no pipeline, descriptor, or shader execution is part of the tested behavior. No representative shader walkthrough is needed.

## Runtime Execution and Result Checking

[`BufferViewTestCase::checkSupport()`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L120-L133) runs before the test instance is created:

- It calls `vkGetPhysicalDeviceFormatProperties` for the case's `VkFormat` and throws `NotSupportedError` if `properties.bufferFeatures` does not contain the required `VK_FORMAT_FEATURE_*_TEXEL_BUFFER_BIT` flag. This skips the case rather than failing it.
- For `dedicated_alloc` cases, it throws `NotSupportedError` if the device does not support `VK_KHR_dedicated_allocation`.

[`BufferViewTestInstance::iterate()`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L319-L386) executes the per-case host-side flow:

- Allocates a buffer of `3 * 5 * 7 * 64` bytes through the `IBufferAllocator` selected by `bufferAllocationKind`. The suballocation and dedicated-allocation allocators each perform their own `vkCreateBuffer`, memory requirements query, memory allocation, and `vkBindBufferMemory` steps, with internal pass/fail checks at each stage.
- Creates the primary `VkBufferView` with `offset = 0` and `range = VK_WHOLE_SIZE`. A thrown `vk::Error` is caught and converted to a `tcu::TestStatus::fail` result.
- Creates a second "complete" `VkBufferView` with `offset = 0` and `range` equal to the explicit buffer size. The same failure conversion applies.

Pass condition: both `vkCreateBufferView` calls return without throwing, after the allocator has reported success for buffer creation, memory allocation, and memory binding. The instance then returns `tcu::TestStatus::pass("BufferView test")`. Any earlier failure short-circuits the flow and returns `tcu::TestStatus::fail` with a message identifying which step failed.

The allocator's internal checks are part of the pass condition:

- `vkCreateBuffer` must not throw.
- `vkGetBufferMemoryRequirements` (suballocation) or `vkGetBufferMemoryRequirements2` (dedicated allocation) must report a `size` at least as large as the requested buffer size.
- `vkAllocateMemory` must succeed and return `VK_SUCCESS`.
- `vkBindBufferMemory` must return `VK_SUCCESS`.
- For dedicated allocation, `VkMemoryDedicatedRequirements::requiresDedicatedAllocation` must be `VK_FALSE`, and `memoryTypeBits` must be non-zero.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `suballocation` | Buffer creation failure; memory requirements size mismatch; suballocation memory allocation or binding failure; buffer view creation failure |
| `dedicated_alloc` | Buffer creation failure; dedicated allocation requirement violation; dedicated allocation memory type bits invalid; dedicated allocation memory allocation or binding failure; memory requirements size mismatch; buffer view creation failure |

Both allocation kinds also share format-support checks performed in `checkSupport()`, but a skipped case is reported as `NotSupported` rather than as a failure, so format-support rejection is a pruning mechanism, not a failure cause.

### Cause Analysis

#### Buffer creation failure

**Possible failure symptoms:** The test fails immediately during `vkCreateBuffer`, before any memory allocation or view creation, with a message identifying the caught `vk::Error` code.

**Possible implementation causes:** `VkBufferCreateInfo` does not carry a `VkFormat` field, so the rejection is not format-related. The source does not narrow the cause further; source-level investigation of the returned error code is needed to determine whether the rejection stems from an invalid usage flag combination, an oversized `size`, host resource exhaustion, or another implementation-specific condition.

#### Memory requirements size mismatch

**Possible failure symptoms:** The allocator returns `tcu::TestStatus::fail` with a "memory size smaller than the buffer's size" message after `vkGetBufferMemoryRequirements` (suballocation) or `vkGetBufferMemoryRequirements2` (dedicated allocation).

**Possible implementation causes:** The Vulkan spec requires `VkMemoryRequirements::size` for a buffer to be at least as large as the buffer's `size`. A reported `size` smaller than the requested 6720 bytes violates the spec. The dedicated-allocation allocator queries requirements twice; the second query at [`vktApiBufferViewCreateTests.cpp#L276`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L276) exists to obtain the proper size requirement before allocation and is checked again at [`vktApiBufferViewCreateTests.cpp#L278-L284`](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L278-L284).

#### Suballocation memory allocation or binding failure

**Possible failure symptoms:** The suballocation allocator returns `tcu::TestStatus::fail` with an "Alloc memory failed" message (after `vkAllocateMemory` throws) or a "Bind buffer memory failed" message (after `vkBindBufferMemory` returns a non-success result).

**Possible implementation causes:** `vkAllocateMemory` may fail because no memory type in the implementation's `memoryTypeBits` is host-visible or allocatable for this buffer usage, or because the device is out of memory. `vkBindBufferMemory` may fail if the implementation rejects the chosen memory type for the buffer's usage flags. Both would indicate inconsistencies in the implementation's memory type reporting or binding logic; the source does not distinguish further.

#### Dedicated allocation requirement violation

**Possible failure symptoms:** The dedicated-allocation allocator returns `tcu::TestStatus::fail` with the message "Nonexternal objects cannot require dedicated allocation." after `vkGetBufferMemoryRequirements2` returns `requiresDedicatedAllocation == VK_TRUE`.

**Possible implementation causes:** Per the Vulkan spec, `VkMemoryDedicatedRequirements::requiresDedicatedAllocation` must be `VK_FALSE` for non-external resources. A `VK_TRUE` value for a buffer that was not created with an external-memory handle type violates the spec. The test enforces this invariant before allocating, so the failure points directly at the implementation's `vkGetBufferMemoryRequirements2` reporting.

#### Dedicated allocation memory type bits invalid

**Possible failure symptoms:** The dedicated-allocation allocator returns `tcu::TestStatus::fail` with the message "memoryTypeBits is 0" after `vkGetBufferMemoryRequirements2`.

**Possible implementation causes:** The Vulkan spec requires the implementation to report at least one compatible memory type for a valid buffer. A zero `memoryTypeBits` value violates this requirement. The source then computes the memory type index with `deCtz32(memoryTypeBits)`, which would be undefined behavior on a zero value, so the test guards against this before continuing.

#### Dedicated allocation memory allocation or binding failure

**Possible failure symptoms:** The dedicated-allocation allocator returns `tcu::TestStatus::fail` with an "Unable to allocate N bytes of memory" message (after `vkAllocateMemory` returns a non-success result) or a "Bind buffer memory failed" message (after `vkBindBufferMemory` returns a non-success result).

**Possible implementation causes:** `vkAllocateMemory` with a `VkMemoryDedicatedAllocateInfo` pNext may fail if the implementation does not correctly handle the dedicated-allocation pNext for buffers, or if no compatible memory type is available for the chosen `heapTypeIndex`. `vkBindBufferMemory` may fail if the implementation rejects binding a dedicated-allocated memory object to the buffer. Both point to driver-side handling of the `VK_KHR_dedicated_allocation` extension; the source does not distinguish further.

#### Buffer view creation failure

**Possible failure symptoms:** The test fails during either `vkCreateBufferView` call with a "Buffer View creation failed" message that includes the caught `vk::Error` code. The primary view (with `range = VK_WHOLE_SIZE`) and the "complete" view (with explicit buffer size range) produce the same symptom.

**Possible implementation causes:** `vkCreateBufferView` rejected the request despite `checkSupport()` verifying that the format reports the required `VK_FORMAT_FEATURE_*_TEXEL_BUFFER_BIT` feature. Per the Vulkan spec, `vkCreateBufferView` requires the format to support the matching texel buffer feature for the buffer's usage; if the implementation's `vkCreateBufferView` rejects a combination that `vkGetPhysicalDeviceFormatProperties` reported as supported, that is a driver inconsistency between format property reporting and buffer view creation logic. The test uses `offset = 0` and either `VK_WHOLE_SIZE` or the explicit buffer size as `range`, so a `minTexelBufferOffsetAlignment` or range-bound violation is unlikely to be the cause. Source-level investigation of the returned error code is needed if a non-format-related cause is suspected.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` queries `vkGetPhysicalDeviceFormatProperties` and throws `NotSupportedError` when the format's `bufferFeatures` does not contain the required `VK_FORMAT_FEATURE_UNIFORM_TEXEL_BUFFER_BIT` (for `uniform` cases) or `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT` (for `storage` cases). Such cases are skipped, not failed, on implementations that do not advertise the feature.
- `dedicated_alloc` cases throw `NotSupportedError` if the device does not support `VK_KHR_dedicated_allocation`. Suballocation cases have no such gate.

### Design-based pruning

- The format loop iterates only over core Vulkan 1.0 formats, from `VK_FORMAT_UNDEFINED + 1` through `VK_CORE_FORMAT_LAST - 1`, where `VK_CORE_FORMAT_LAST` is defined as `VK_FORMAT_ASTC_12x12_SRGB_BLOCK + 1`. Extension-defined formats such as `VK_FORMAT_G8B8G8R8_422_UNORM` and the `PVRTC` family are excluded.
- The test uses a single fixed buffer size (`3 * 5 * 7 * 64` bytes) and `offset = 0` for both views, avoiding alignment-driven variations. The "complete" view duplicates the primary view's setup with an explicit range instead of `VK_WHOLE_SIZE`, so the matrix does not sweep different offsets or ranges.
- The test stops at `vkCreateBufferView` creation and does not bind the view to a descriptor or run any shader against it. Descriptor-binding and shader-observable behavior for buffer views is exercised by the sibling `buffer_view.access` family, not by this family.

## Key Takeaways

- The family verifies only that `vkCreateBufferView` succeeds for every supported core Vulkan format, under both suballocated and dedicated-allocation memory bindings. It does not exercise shader-side reads or writes through the view.
- The allocation kind intermediate node is the primary behavioral axis; it switches the entire memory binding code path, including the `VK_KHR_dedicated_allocation` pNext chain and the `requiresDedicatedAllocation == VK_FALSE` spec invariant.
- The dedicated-allocation path enforces two spec invariants that the suballocation path does not: `requiresDedicatedAllocation` must be `VK_FALSE` for non-external buffers, and `memoryTypeBits` must be non-zero. Violations are reported as failures, not skips.
- The `uniform`/`storage` intermediate nodes change `VkBufferUsageFlags` and the required format feature, but the test flow itself is identical between them.
- A failure of `vkCreateBufferView` after `checkSupport()` has passed indicates a driver inconsistency between `vkGetPhysicalDeviceFormatProperties` reporting and `vkCreateBufferView` enforcement; see `## Failure Meaning` for the case-by-case analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `AllocationKind` enum | [vktApiBufferViewCreateTests.cpp#L46-L52](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L46-L52) | Defines the suballocation/dedicated_alloc dispatch dimension. |
| `BufferViewCaseParameters` struct | [vktApiBufferViewCreateTests.cpp#L56-L64](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L56-L64) | Carries per-case format, offset, range, usage, feature flag, and allocation kind. |
| `BufferViewTestCase::checkSupport()` | [vktApiBufferViewCreateTests.cpp#L120-L133](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L120-L133) | Requirement-based pruning: format feature check and `VK_KHR_dedicated_allocation` gate. |
| `BufferSuballocation::createTestBuffer()` | [vktApiBufferViewCreateTests.cpp#L139-L201](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L139-L201) | Suballocation memory binding path with internal pass/fail checks. |
| `BufferDedicatedAllocation::createTestBuffer()` | [vktApiBufferViewCreateTests.cpp#L203-L317](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L203-L317) | Dedicated-allocation memory binding path, including the `requiresDedicatedAllocation == VK_FALSE` and `memoryTypeBits != 0` spec invariants. |
| `BufferViewTestInstance::iterate()` | [vktApiBufferViewCreateTests.cpp#L319-L386](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L319-L386) | Main test flow: allocator dispatch, primary view creation, "complete" view creation, pass/fail decision. |
| `createBufferViewCreateTests()` | [vktApiBufferViewCreateTests.cpp#L390-L444](../../../modules/vulkan/api/vktApiBufferViewCreateTests.cpp#L390-L444) | Family registration: builds the `suballocation` and `dedicated_alloc` intermediate nodes, the `uniform` and `storage` intermediate nodes, and one test case leaf per core Vulkan format. |
| Parent registration | [vktApiTests.cpp#L78-L84](../../../modules/vulkan/api/vktApiTests.cpp#L78-L84) | `createBufferViewTests()` mounts `create` and the sibling `access` family under `buffer_view`; `createApiTests()` at [vktApiTests.cpp#L106](../../../modules/vulkan/api/vktApiTests.cpp#L106) mounts `buffer_view` under `api`. |
