## Overview

**Core question:** can the implementation create buffers across the usage-flag, create-flag, and size matrix, report memory requirements at least as large as the requested size, and bind the resulting memory correctly?

- Source file covered: [`vktApiBufferTests.cpp`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L1).
- Test category: `api`. Test family: `buffer`. Intermediate nodes: `suballocation`, `dedicated_alloc`, `basic`, `invalid_buffer_features`.
- Core test idea: drive `vkCreateBuffer`, `vkAllocateMemory`, and memory binding across a generated matrix of buffer usage and create flags; probe large buffer sizes through `basic`; and verify through `invalid_buffer_features` that depth/stencil formats do not advertise buffer features.
- The remaining sections cover the four intermediate nodes, what each one changes, what is checked, and what a failure of each one means.

## Background Knowledge

- **Suballocation versus dedicated allocation.** Vulkan allows one `VkDeviceMemory` object to back multiple resources (suballocation) or to be dedicated to a single resource through `VkMemoryDedicatedAllocateInfo` (introduced by `VK_KHR_dedicated_allocation`). The two paths query memory requirements through different APIs (`vkGetBufferMemoryRequirements` versus `vkGetBufferMemoryRequirements2` with `VkMemoryDedicatedRequirements`), so the test family exercises both.
- **Sparse buffer binding.** A buffer created with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT` (optionally combined with residency and aliased bits) cannot be bound with `vkBindBufferMemory`; binding must go through `vkQueueBindSparse` with a `VkSparseBufferMemoryBindInfo` structure. The test branches on the sparse flags when choosing the bind path.
- **`VkMemoryRequirements` versus requested size.** The implementation reports a `size` field in `VkMemoryRequirements` that must be at least as large as the buffer's creation size. Reporting a smaller size is a conformance failure and is checked in the test loop.
- **`maxBufferSize` from `VK_KHR_maintenance4`.** This property is a hard cap on legal buffer creation size. Sizes above `maxBufferSize` are not legal usage, so the test treats `VK_ERROR_OUT_OF_HOST_MEMORY` and `VK_ERROR_OUT_OF_DEVICE_MEMORY` as acceptable outcomes for `ULLONG_MAX` requests.
- **`bufferFeatures` for depth/stencil formats.** The Vulkan spec restricts which format features a depth/stencil format may advertise. A non-zero `bufferFeatures` value for such a format is invalid; the test family queries `vkGetPhysicalDeviceFormatProperties` and asserts the field is zero.

## Registration Hierarchy

```text
api.buffer
├── suballocation
├── dedicated_alloc
├── basic
└── invalid_buffer_features
```

The `buffer` test family is registered by [`createBufferTests()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L748) and attached to the `api` test category by [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L101). The four intermediate nodes are added at [`vktApiBufferTests.cpp#L753`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L753) (`suballocation`), [`vktApiBufferTests.cpp#L759`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L759) (`dedicated_alloc`), [`vktApiBufferTests.cpp#L765`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L765) (`basic`), and [`vktApiBufferTests.cpp#L782`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L782) (`invalid_buffer_features`).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Allocation kind | `suballocation`, `dedicated_alloc` | Selects `BufferTestInstance` versus `DedicatedAllocationBufferTestInstance` and which requirements API is queried. | [`AllocationKind`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L49) |
| Buffer usage flags | non-empty combinations of `transfer_src`, `transfer_dst`, `uniform_texel`, `storage_texel`, `uniform`, `storage`, `index`, `vertex`, `indirect` | Each leaf combines one or more `VkBufferUsageFlagBits`. Generated recursively so every non-empty subset appears once. | [`createBufferUsageCases()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L589) |
| Buffer create flags | `zero`, `binding`, `binding_residency`, `binding_aliased`, `binding_residency_aliased` (suballocation only); `zero` only (dedicated_alloc) | Sparse create-flag combinations exercise the `vkQueueBindSparse` path. Dedicated allocation excludes sparse flags by design. | [`vktApiBufferTests.cpp#L616-L625`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L616-L625) |
| Sharing mode | `VK_SHARING_MODE_EXCLUSIVE` | Fixed across all generated cases; no concurrent-mode variants exist. | [`BufferCaseParameters`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L85) |
| Test sizes (create-and-alloc cases) | `1`, `1181`, `15991`, `16384`, `~0ull` | Each size drives one `bufferCreateAndAllocTest` iteration. The `~0ull` value is excluded on Vulkan SC. | [`BufferTestInstance::iterate()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L369) |
| Large buffer size parameter | `maxBufferSize` (for `max_size`, `max_size_sparse`), `UINT64_MAX` (for `size_max_uint64`) | Drives the `basic` intermediate node; each leaf uses one value. | [`vktApiBufferTests.cpp#L768-L775`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L768-L775) |
| Depth/stencil formats | `d16_unorm`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat`, `d32_sfloat_s8_uint`, `s8_uint`, `x8_d24_unorm_pack32` | One leaf per format under `invalid_buffer_features`. | [`vktApiBufferTests.cpp#L785`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L785) |

The full matrix produces 3076 registered test case leaves: 2555 under `suballocation` (511 non-empty usage combinations × 5 create-flag sets), 511 under `dedicated_alloc` (511 × 1), 3 under `basic`, and 7 under `invalid_buffer_features`.

## Behavior Parameters

The primary behavioral axis is the intermediate node. Each value of the axis changes what is being tested: the allocation strategy, the requirements-query API, the bind path, or the property being asserted.

### suballocation — Buffer creation with one allocation per buffer

Tests `vkCreateBuffer` followed by `vkGetBufferMemoryRequirements`, `vkAllocateMemory`, and binding for every non-empty usage-flag combination paired with every supported sparse create-flag combination. Binding uses `vkBindBufferMemory` for non-sparse flags and `vkQueueBindSparse` with a `VkSparseBufferMemoryBindInfo` structure for sparse flags. The test instance is [`BufferTestInstance`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L92), and its main loop is [`BufferTestInstance::bufferCreateAndAllocTest()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L185). Sparse cases are gated by [`BuffersTestCase::checkSupport()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L135), which throws `NotSupportedError` when `sparseBinding`, `sparseResidencyBuffer`, or `sparseResidencyAliased` is missing.

### dedicated_alloc — Buffer creation with a dedicated allocation

Tests `vkCreateBuffer` followed by `vkGetBufferMemoryRequirements2` (with `VkMemoryDedicatedRequirements` chained), `vkAllocateMemory` with a chained `VkMemoryDedicatedAllocateInfo`, and `vkBindBufferMemory`. The test instance is [`DedicatedAllocationBufferTestInstance`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L105). Two additional checks apply only on this path: a non-external buffer must not report `requiresDedicatedAllocation == VK_TRUE` ([`vktApiBufferTests.cpp#L437-L442`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L437-L442)), and `memoryTypeBits` must not be zero ([`vktApiBufferTests.cpp#L444-L445`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L444-L445)). Sparse create flags are excluded by design ([`vktApiBufferTests.cpp#L628-L629`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L628-L629)). Support is gated by [`DedicatedAllocationBuffersTestCase::checkSupport()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L175), which requires `VK_KHR_dedicated_allocation`.

### basic — Large buffer size boundary tests

Tests `vkCreateBuffer` at three boundary sizes: `maxBufferSize` ([`max_size`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L768)), `maxBufferSize` with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT` ([`max_size_sparse`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L771)), and `UINT64_MAX` ([`size_max_uint64`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L774)). The implementation function is [`testLargeBuffer()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L680). Successful creation is validated by checking that the reported memory requirements size is at least as large as the requested buffer size; `VK_ERROR_OUT_OF_HOST_MEMORY` and `VK_ERROR_OUT_OF_DEVICE_MEMORY` are accepted as legal rejections. Any other error is a failure. All three leaves are excluded on Vulkan SC.

### invalid_buffer_features — Depth/stencil format feature advertisement check

Tests that the implementation does not advertise buffer features for any depth/stencil format. One leaf is registered per format in `formats::depthAndStencilFormats`, and the implementation function is [`testDepthStencilBufferFeatures()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L658). The check queries `vkGetPhysicalDeviceFormatProperties` and asserts `bufferFeatures == 0`.

## Shader Analysis

No shader is involved in this test family. All test logic runs on the host through Vulkan buffer, memory, sparse binding, and format-property API calls. No `### Representative Shader Walkthrough` subsection is therefore created.

## Runtime Execution and Result Checking

### suballocation and dedicated_alloc

For each registered usage and create-flag combination, [`BufferTestInstance::iterate()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L369) iterates over the test size array `{1, 1181, 15991, 16384, ~0ull}` and calls `bufferCreateAndAllocTest(size)` for each value.

For each size, the host:

1. Creates a 1-byte probe buffer with the same flags to discover the supported memory type bits.
2. Computes a clamped maximum buffer size from the memory heap size and platform memory limits, halves it, and aligns it to `memReqs.alignment` ([`vktApiBufferTests.cpp#L232-L238`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L232-L238)).
3. Clamps the requested size to that maximum and aligns it.
4. Enters a shrink-and-retry loop driven by `shrinkBits = 4`. On each iteration:
   - calls `vkCreateBuffer` with the current size; on failure, shrinks and retries, failing only if the size reaches alignment or zero ([`vktApiBufferTests.cpp#L243-L265`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L243-L265));
   - calls `vkGetBufferMemoryRequirements` (or `vkGetBufferMemoryRequirements2` on the dedicated path) and checks `memReqs.size >= size`; if smaller, the case fails immediately with `"Required memory size ... smaller than the buffer's size"` ([`vktApiBufferTests.cpp#L273-L280`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L273-L280));
   - calls `vkAllocateMemory` with `memReqs.size`; on failure, shrinks and retries.
5. Binds the memory. Non-sparse cases use `vkBindBufferMemory` ([`vktApiBufferTests.cpp#L359-L360`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L359-L360)). Sparse cases build a `VkSparseBufferMemoryBindInfo`, queue a `vkQueueBindSparse` call, and wait on a fence ([`vktApiBufferTests.cpp#L317-L358`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L317-L358)).

The dedicated path performs two additional checks before the loop: `requiresDedicatedAllocation` must be `VK_FALSE` for the non-external buffer, and `memoryTypeBits` must not be zero. The pass condition is that every test size reaches a successful bind.

### basic

For each leaf, [`testLargeBuffer()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L680) resolves the requested size (substituting `maxBufferSize` from `VkPhysicalDeviceMaintenance4Properties` when `useMaxBufferSize` is set), clamps sparse cases to `limits.sparseAddressSpaceSize`, calls `vkCreateBuffer`, and applies the following pass/fail rules:

- On `VK_SUCCESS`: reads `vkGetBufferMemoryRequirements` and passes only if `memoryRequirements.size >= params.bufferSize` ([`vktApiBufferTests.cpp#L711-L720`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L711-L720)).
- On `VK_ERROR_OUT_OF_DEVICE_MEMORY` or `VK_ERROR_OUT_OF_HOST_MEMORY`: passes, because these are legal rejections of an oversized request ([`vktApiBufferTests.cpp#L722-L724`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L722-L724)).
- On any other result: fails ([`vktApiBufferTests.cpp#L726`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L726)).

### invalid_buffer_features

For each registered format, [`testDepthStencilBufferFeatures()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L658) calls `vkGetPhysicalDeviceFormatProperties` and passes when `bufferFeatures == 0x0`; any non-zero value fails the case ([`vktApiBufferTests.cpp#L666-L669`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L666-L669)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `suballocation` | Memory requirement size smaller than requested size; `vkCreateBuffer` returns unexpected failure; `vkAllocateMemory` returns unexpected failure; `vkBindBufferMemory` or `vkQueueBindSparse` fails |
| `dedicated_alloc` | Non-external buffer reports `requiresDedicatedAllocation == VK_TRUE`; `memoryTypeBits == 0`; memory requirement size smaller than requested size; `vkCreateBuffer` returns unexpected failure; `vkAllocateMemory` returns unexpected failure; `vkBindBufferMemory` fails |
| `basic` | `vkCreateBuffer` returns an error other than the allowed out-of-memory errors; reported memory requirement size is smaller than the requested buffer size |
| `invalid_buffer_features` | Driver advertises a non-zero `bufferFeatures` value for a depth/stencil format |

### Cause Analysis

#### Memory requirement size smaller than requested size

**Possible failure symptoms:** the case returns a fail status with the message `"Required memory size (<N>) bytes smaller than the buffer's size (<M>) bytes!"` on the suballocation or dedicated path, or returns a plain fail status on the `basic` path after `vkCreateBuffer` succeeds.

**Possible implementation causes:** the driver reports a `VkMemoryRequirements::size` value that is smaller than the size passed to `vkCreateBuffer`. The Vulkan spec requires the reported size to be at least the buffer's creation size; reporting a smaller value indicates a bug in the driver's memory-requirements computation for the tested combination of usage flags, create flags, and size. The dedicated path uses `vkGetBufferMemoryRequirements2` and would surface the same defect through that API.

#### Buffer or memory allocation failure

**Possible failure symptoms:** the case returns a fail status with `"Buffer creation failed! (<result>)"` or `"Unable to allocate <N> bytes of memory"`, after the shrink-and-retry loop has reduced the size down to the alignment.

**Possible implementation causes:** `vkCreateBuffer` returns a `VkResult` other than `VK_SUCCESS` for a buffer configuration that the implementation should accept, or `vkAllocateMemory` returns a non-success result for an allocation sized to the implementation's own reported memory requirements. A consistent failure across all shrink iterations, on configurations that match advertised features and limits, points to a driver-side defect in buffer or memory object creation.

#### Bind failure

**Possible failure symptoms:** the case returns `"Bind buffer memory failed! (requested memory size: <N>)"` on the non-sparse path, or `"Bind sparse buffer memory failed! (requested memory size: <N>)"` on the sparse path.

**Possible implementation causes:** `vkBindBufferMemory` rejects a valid buffer-memory pair, or `vkQueueBindSparse` rejects a sparse bind whose resource offset, size, and memory arguments were derived from the implementation's reported memory requirements. For sparse cases, the failure may also indicate that the sparse binding path does not honour the reported `VkSparseBufferMemoryBindInfo` layout.

#### Dedicated allocation requirement violation

**Possible failure symptoms:** the case returns `"Nonexternal objects cannot require dedicated allocation."` or `"memoryTypeBits is 0"` on the dedicated path before the create-and-alloc loop runs.

**Possible implementation causes:** the driver populates `VkMemoryDedicatedRequirements::requiresDedicatedAllocation` with `VK_TRUE` for a buffer that is not backed by an external handle, which the spec disallows for non-external objects. Reporting `memoryTypeBits == 0` indicates the driver returned no usable memory type for the buffer, which is not a legal response for a buffer created against advertised features.

#### Large buffer creation returns unexpected error

**Possible failure symptoms:** the `basic.size_max_uint64` leaf returns a fail status because `vkCreateBuffer` returned a `VkResult` other than `VK_SUCCESS`, `VK_ERROR_OUT_OF_HOST_MEMORY`, or `VK_ERROR_OUT_OF_DEVICE_MEMORY`. The `basic.max_size` and `basic.max_size_sparse` leaves can also fail here when `vkCreateBuffer` rejects a `maxBufferSize` request with an unexpected error.

**Possible implementation causes:** the driver rejects a buffer size that is legal under `VK_KHR_maintenance4` `maxBufferSize` with an error code outside the spec-allowed set, or returns a validation error instead of an out-of-memory result for `UINT64_MAX` requests. Source-level investigation is needed to confirm whether a specific `VkResult` falls inside or outside the spec-allowed set for a given size and flag combination.

#### Invalid buffer feature advertisement

**Possible failure symptoms:** the `invalid_buffer_features` leaf for a depth/stencil format returns a fail status with no diagnostic string.

**Possible implementation causes:** `vkGetPhysicalDeviceFormatProperties` reports a non-zero `bufferFeatures` field for a depth/stencil format. The Vulkan spec does not allow buffer features to be advertised for depth/stencil formats, so any non-zero bit indicates a driver bug in format feature reporting.

## Case Pruning

### Requirement-based pruning

- `dedicated_alloc` is gated by [`DedicatedAllocationBuffersTestCase::checkSupport()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L175), which throws `NotSupportedError` when `VK_KHR_dedicated_allocation` is not supported.
- Sparse create-flag cases under `suballocation` are gated by [`BuffersTestCase::checkSupport()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L135): `VK_BUFFER_CREATE_SPARSE_BINDING_BIT` requires `sparseBinding`, `VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT` requires `sparseResidencyBuffer`, and `VK_BUFFER_CREATE_SPARSE_ALIASED_BIT` requires `sparseResidencyAliased`.
- `basic.max_size` and `basic.max_size_sparse` require `VK_KHR_maintenance4` through [`checkMaintenance4Support()`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L731) because they read `VkPhysicalDeviceMaintenance4Properties::maxBufferSize`.
- `basic.size_max_uint64` is skipped when `VK_KHR_maintenance4` is supported and `params.bufferSize > maxBufferSize`, because requesting a buffer larger than `maxBufferSize` is not legal usage ([`vktApiBufferTests.cpp#L735-L737`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L735-L737)).

### Design-based pruning

- All `basic` leaves are excluded on Vulkan SC through `#ifndef CTS_USES_VULKANSC` ([`vktApiBufferTests.cpp#L766`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L766)).
- Sparse create-flag combinations are excluded on Vulkan SC through `#ifndef CTS_USES_VULKANSC` ([`vktApiBufferTests.cpp#L618-L624`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L618-L624)).
- The `~0ull` test size in `BufferTestInstance::iterate()` is excluded on Vulkan SC ([`vktApiBufferTests.cpp#L373-L375`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L373-L375)).
- `dedicated_alloc` excludes sparse create flags by limiting the loop to a single `zero` create-flag entry ([`vktApiBufferTests.cpp#L628-L629`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L628-L629)).
- `sharingMode` is fixed to `VK_SHARING_MODE_EXCLUSIVE` for every generated case; no concurrent-mode variants exist in the matrix.
- Usage-flag combinations are restricted to non-empty subsets; the zero-usage case is not generated ([`vktApiBufferTests.cpp#L613`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L613)).
- `basic` leaves use `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` only; the usage-flag matrix does not apply to the large-buffer path.

## Key Takeaways

- The `buffer` test family proves that the implementation can create and bind buffers across the full usage-flag and create-flag matrix, with memory requirements that are at least as large as the requested size.
- `suballocation` and `dedicated_alloc` overlap on the usage-flag matrix but differ in requirements-query API, bind path, and the additional `requiresDedicatedAllocation` and `memoryTypeBits` checks; sparse create flags appear only on the suballocation path.
- `basic` probes boundary sizes: `maxBufferSize` must be accepted, `UINT64_MAX` may legally fail with `VK_ERROR_OUT_OF_HOST_MEMORY` or `VK_ERROR_OUT_OF_DEVICE_MEMORY`, and any other error is a conformance failure.
- `invalid_buffer_features` covers a spec-mandated property with seven leaves: depth/stencil formats must not advertise any buffer feature bit.
- See `## Failure Meaning` for the per-cause failure analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createBufferTests()` | [`vktApiBufferTests.cpp#L748`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L748) | Top-level registration for the `buffer` test family; adds the four intermediate nodes. |
| `createBufferUsageCases()` | [`vktApiBufferTests.cpp#L589`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L589) | Recursive generator for non-empty usage-flag combinations and per-usage `create` subgroups. |
| `BufferTestInstance::iterate()` | [`vktApiBufferTests.cpp#L369`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L369) | Test size loop for `suballocation` and `dedicated_alloc` instances. |
| `BufferTestInstance::bufferCreateAndAllocTest()` | [`vktApiBufferTests.cpp#L185`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L185) | Suballocation create-and-alloc loop, memory-requirement check, and bind path selection. |
| `DedicatedAllocationBufferTestInstance::bufferCreateAndAllocTest()` | [`vktApiBufferTests.cpp#L389`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L389) | Dedicated-allocation create-and-alloc loop, `VkMemoryDedicatedRequirements` check, and `VkMemoryDedicatedAllocateInfo` usage. |
| `BuffersTestCase::checkSupport()` | [`vktApiBufferTests.cpp#L135`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L135) | Sparse feature gating for `suballocation`. |
| `DedicatedAllocationBuffersTestCase::checkSupport()` | [`vktApiBufferTests.cpp#L175`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L175) | `VK_KHR_dedicated_allocation` gating for `dedicated_alloc`. |
| `testLargeBuffer()` | [`vktApiBufferTests.cpp#L680`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L680) | `basic` test instance function; applies the pass/fail rules for `max_size`, `max_size_sparse`, and `size_max_uint64`. |
| `checkMaintenance4Support()` | [`vktApiBufferTests.cpp#L731`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L731) | `VK_KHR_maintenance4` gating and `maxBufferSize` legality check for `basic`. |
| `testDepthStencilBufferFeatures()` | [`vktApiBufferTests.cpp#L658`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L658) | `invalid_buffer_features` test instance function; queries `vkGetPhysicalDeviceFormatProperties` and asserts `bufferFeatures == 0`. |
| `AllocationKind` enum | [`vktApiBufferTests.cpp#L49`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L49) | Defines the `ALLOCATION_KIND_SUBALLOCATED` and `ALLOCATION_KIND_DEDICATED` values used by `createBufferUsageCases()`. |
| `BufferCaseParameters` struct | [`vktApiBufferTests.cpp#L85`](../../../modules/vulkan/api/vktApiBufferTests.cpp#L85) | Per-case parameter bundle: usage flags, create flags, and sharing mode. |
| Parent registration | [`vktApiTests.cpp#L101`](../../../modules/vulkan/api/vktApiTests.cpp#L101) | `apiTests->addChild(createBufferTests(testCtx))` attaches the `buffer` family to the `api` test category. |
