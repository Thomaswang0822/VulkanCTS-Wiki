## Overview

**Core question:** For every valid combination of `VkBufferCreateFlags`, `VkBufferUsageFlags`, and external memory handle types, does the implementation advertise at least one compatible memory type? When `VK_KHR_maintenance4` is supported, is the reported memory size also bounded by the aligned buffer size?

- Covers the `buffer_memory_requirements` test family inside the `api` test category, registered by [createBufferMemoryRequirementsTests()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L977).
- Source file: [`vktApiBufferMemoryRequirementsTests.cpp`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1); helper flag utilities in [`vktApiBufferMemoryRequirementsTestsUtils.hpp`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTestsUtils.hpp#L1).
- For each generated configuration the test creates a buffer, queries its memory requirements through `vkGetBufferMemoryRequirements` (`method1`) or `vkGetBufferMemoryRequirements2` (`method2`), and verifies the returned `VkMemoryRequirements`.
- Two verification modes are exercised: a non-zero `memoryTypeBits` check (default leaves) and a `size <= align(bufferSize, alignment)` check (`size_req_*` leaves, non-VKSC only, requires `VK_KHR_maintenance4`).
- The matrix is generated from valid `VkBufferCreateFlags` combinations after applying VUID-00918 and VUID-None-01888 constraints, crossed with usage-flag categories, external-memory configurations, and the two query methods.

## Background Knowledge

- `vkGetBufferMemoryRequirements` (Vulkan 1.0) and `vkGetBufferMemoryRequirements2` (from `VK_KHR_get_memory_requirements2`, Vulkan 1.1) are the two host-side entry points that return a `VkMemoryRequirements` for a given `VkBuffer`. The second form accepts a `pNext` chain so callers can attach structures such as `VkMemoryDedicatedRequirements`.
- `VkMemoryRequirements` reports `size` (bound the implementation will require), `alignment` (minimum binding offset), and `memoryTypeBits` (bitmask of memory type indices that the buffer can be bound to). A zero `memoryTypeBits` means the implementation advertises no compatible memory type for the queried buffer.
- `VK_KHR_maintenance4` (Vulkan 1.3) constrains buffer memory requirements so that `reqs.size` must not exceed `align(bufferSize, reqs.alignment)` for a buffer created with `size = bufferSize`. The `size_req_*` leaves verify this bound by repeatedly querying buffers whose `size` is grown as `(1ull << N) + 1`.
- `VK_BUFFER_CREATE_SPARSE_BINDING_BIT`, `VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT`, and `VK_BUFFER_CREATE_SPARSE_ALIASED_BIT` select sparse-resource behavior. VUID-00918 makes `sparse_residency` and `sparse_aliased` imply `sparse_binding`, so test combinations always co-set the binding bit when either of the others is present.
- `VK_BUFFER_CREATE_PROTECTED_BIT` selects protected memory. VUID-None-01888 forbids combining protected with any sparse bit, so the test matrix generates protected and sparse branches as mutually exclusive `VkBufferCreateFlags` combinations.
- `VkExternalMemoryBufferCreateInfo` is chained into `VkBufferCreateInfo::pNext` to declare which external memory handle types the buffer must be compatible with. The `ext_mem_flags_included` intermediate node chains this structure; `ext_mem_flags_excluded` does not.

## Registration Hierarchy

```text
api.buffer_memory_requirements
├── create_no_flags
├── create_protected
├── create_sparse_binding
├── create_sparse_binding_sparse_aliased
├── create_sparse_binding_sparse_residency
└── create_sparse_binding_sparse_residency_sparse_aliased
```

[vktApiTests.cpp#L127](../../../modules/vulkan/api/vktApiTests.cpp#L127) adds the `buffer_memory_requirements` test family to the `api` test category. The six `create_*` intermediate nodes are produced by iterating all valid combinations of `AvailableBufferCreateBits` after [`updateBufferCreateFlags()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L193) enforces the VUID constraints.

Beneath each `create_*` intermediate node the tree is uniform: two `ext_mem_flags_*` nodes, each with `method1` and `method2`, each with ten test case leaves: five non-prefixed `*_usage_bits` leaves and five `size_req_*_usage_bits` leaves. The full set of registered leaves for each `create_*` value is enumerated under `## Parameter Dimensions and Observed Values`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Create flags | `create_no_flags`, `create_protected`, `create_sparse_binding`, `create_sparse_binding_sparse_aliased`, `create_sparse_binding_sparse_residency`, `create_sparse_binding_sparse_residency_sparse_aliased` | Which `VkBufferCreateFlags` combination is used when creating the buffer; selects baseline, protected, or sparse memory behavior | [`AvailableBufferCreateBits`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L119), [`updateBufferCreateFlags()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L193) |
| External memory handle configuration | `ext_mem_flags_excluded`, `ext_mem_flags_included` | Whether `VkExternalMemoryBufferCreateInfo` is chained into `VkBufferCreateInfo::pNext` | [`TestConfig::incExtMemTypeFlags`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L92), iterate chain at [L873-L876](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L873-L876) |
| Query method | `method1`, `method2` | Whether memory requirements are obtained through `vkGetBufferMemoryRequirements` or `vkGetBufferMemoryRequirements2` | [`TestConfig::useMethod2`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L89), dispatch at [L831-L832](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L831-L832) |
| Usage fate bits | `transfer_usage_bits`, `storage_usage_bits`, `other_usage_bits`, `acc_struct_usage_bits`, `video_usage_bits` | Which category of `VkBufferUsageFlagBits` is expanded into `VkBufferCreateInfo::usage`; each fate expands to multiple `VkBufferUsageFlagBits` (see `AvailableBufferUsageBits`) | [`AvailableBufferFateBits`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L73), [`AvailableBufferUsageBits`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L129) |
| Verification mode | non-prefixed leaves, `size_req_*` leaves | Whether the leaf checks non-zero `memoryTypeBits`, or instead checks `reqs.size <= align(bufferSize, reqs.alignment)` over an iterated size range (non-VKSC only) | iterate body at [L888-L961](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L888-L961) |

For each `create_*` intermediate node the registered leaf set is the cross product of `ext_mem_flags_excluded` × `ext_mem_flags_included`, `method1` × `method2`, and the ten leaves `transfer_usage_bits`, `storage_usage_bits`, `other_usage_bits`, `acc_struct_usage_bits`, `video_usage_bits` plus their `size_req_*` variants. The full mustpass listing for the test family contains 240 test case leaves (6 × 2 × 2 × 10), starting at [`dEQP-VK.api.buffer_memory_requirements.create_no_flags.ext_mem_flags_excluded.method1.acc_struct_usage_bits`](../../../mustpass/main/vk-default/api.txt).

## Behavior Parameters

The primary behavioral axis is the `create_*` intermediate node. Each value selects a distinct `VkBufferCreateFlags` combination, which changes what kind of buffer is created, which feature gates must be satisfied, and which memory model the implementation must report against. The other registered dimensions (`ext_mem_flags_*`, `method1`/`method2`, fate bits, and `size_req_*` versus non-prefixed leaves) expand coverage across query path and usage category rather than changing the kind of buffer under test.

### create_no_flags — baseline buffer with no create flags

Creates a buffer with `VkBufferCreateFlags = 0`. This is the baseline case: no protected memory, no sparse behavior, no special memory model. The test verifies that the implementation still reports at least one compatible memory type for the chosen usage flags, and (for `size_req_*` leaves) that the reported size is bounded by `VK_KHR_maintenance4`. Available on all platforms including VKSC.

### create_protected — buffer with the protected create flag

Creates a buffer with `VK_BUFFER_CREATE_PROTECTED_BIT`. Requires the protected memory feature. The test instantiates a separate protected device via [`createProtectedDevice()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L794) (with `VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT` and `VkPhysicalDeviceProtectedMemoryFeatures::protectedMemory = VK_TRUE`) and queries memory requirements against that device. Available on all platforms; [`checkSupport()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L424-L430) enforces the protected memory feature gate.

### create_sparse_binding — buffer with sparse binding flag (non-VKSC only)

Creates a buffer with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT`. Requires the `sparseBinding` feature. The buffer is not fully resident by default and the implementation must advertise memory types compatible with sparse binding. Available only on non-VKSC builds because `AvailableBufferCreateBits` excludes sparse bits under `CTS_USES_VULKANSC`.

### create_sparse_binding_sparse_aliased — buffer with sparse binding and aliased flags (non-VKSC only)

Creates a buffer with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT | VK_BUFFER_CREATE_SPARSE_ALIASED_BIT`. Per VUID-00918, `sparse_aliased` implies `sparse_binding`, so the test generator always co-sets the binding bit. Requires `sparseBinding` and `sparseResidencyAliased` features.

### create_sparse_binding_sparse_residency — buffer with sparse binding and residency flags (non-VKSC only)

Creates a buffer with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT | VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT`. Per VUID-00918, `sparse_residency` implies `sparse_binding`, so the test generator always co-sets the binding bit. Requires `sparseBinding` and `sparseResidencyBuffer` features.

### create_sparse_binding_sparse_residency_sparse_aliased — buffer with all sparse flags (non-VKSC only)

Creates a buffer with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT | VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT | VK_BUFFER_CREATE_SPARSE_ALIASED_BIT`. Both VUID-00918 implications apply. Requires `sparseBinding`, `sparseResidencyBuffer`, and `sparseResidencyAliased` features.

### Verification mode — non-prefixed leaves versus `size_req_*` leaves

Within each `create_*` × `ext_mem_flags_*` × `method*` × `*_usage_bits` combination the test family registers two leaf variants that differ in what is checked:

- **Non-prefixed leaf** (`<fate>_usage_bits`) verifies only that `memoryTypeBits != 0` after a single buffer creation and query at `size = 4096`.
- **`size_req_*` leaf** (`size_req_<fate>_usage_bits`) iterates `createInfo.size = (1ull << N) + 1` while the value remains below `VkPhysicalDeviceMaintenance4PropertiesKHR::maxBufferSize`, queries memory requirements for each size, and verifies `reqs.size <= align(createInfo.size, reqs.alignment)`. The loop stops early on `vk::OutOfMemoryError`.

The `size_req_*` leaves exist only on non-VKSC builds because `VK_KHR_maintenance4` is not exposed there. They do not re-check `memoryTypeBits`; the two leaf variants are disjoint verification modes.

## Shader Analysis

No shader is involved in this test family. The test exercises host-side buffer creation and memory requirement queries, then validates the returned `VkMemoryRequirements` on the host. No `### Representative Shader Walkthrough` subsection is needed.

## Runtime Execution and Result Checking

The instance entry point is [`BufferMemoryRequirementsInstance::iterate()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L827), which executes the following host-side flow:

- Selects the query method pointer (`getBufferMemoryRequirements` or `getBufferMemoryRequirements2`) based on `TestConfig::useMethod2`.
- If `createBits` contains `VK_BUFFER_CREATE_PROTECTED_BIT`, creates a dedicated protected device via [`createProtectedDevice()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L794) and uses it for the rest of the iteration; otherwise uses the context's default device.
- Iterates the pre-resolved usage-flag combinations produced by [`checkSupport()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L373) and, for each, iterates the pre-resolved external-memory-handle-type combinations.
- For each `(createBits, usageFlags, extMemHandleFlags)` triple:
  - Builds the `pNext` chain: chains `VkVideoProfileListInfoKHR` when video usage bits are present (non-VKSC), then chains `VkExternalMemoryBufferCreateInfo` when `incExtMemTypeFlags` is true.
  - Constructs `VkBufferCreateInfo` with `size = 4096`, `sharingMode = VK_SHARING_MODE_EXCLUSIVE`, the queue family index, the resolved create flags, and the resolved usage flags.
  - Branches on `testSizeRequirements`:
    - **Default path** (`testSizeRequirements = false`, all VKSC leaves and the non-prefixed non-VKSC leaves): creates the buffer, queries memory requirements through the selected method, and increments `passCount` if `memoryTypeBits != 0`; otherwise records the failing triple.
    - **Size-requirements path** (`testSizeRequirements = true`, the `size_req_*` non-VKSC leaves): queries `VkPhysicalDeviceMaintenance4PropertiesKHR::maxBufferSize`, then iterates `N` from 0 while `(1ull << N) + 1 < maxBufferSize`. For each size, it creates the buffer, queries memory requirements, and verifies `reqs.size <= deAlign64(createInfo.size, reqs.alignment)`. The loop breaks on `vk::OutOfMemoryError` and resets the watchdog between iterations.
- If any sub-configuration failed, [`logFailedSubtests()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L622) emits the failing `VkBufferCreateFlags`, `VkBufferUsageFlags`, and `VkExternalMemoryHandleTypeFlags` triples to the test log, and the case returns `TestStatus::fail` with the failing count.
- Otherwise the case returns `TestStatus::pass` with the passing count.

The `method2` query path also chains `VkMemoryDedicatedRequirements` into `VkMemoryRequirements2::pNext`, although the test does not assert on `prefersDedicatedAllocation` or `requiresDedicatedAllocation`; the chained structure only exercises the pNext-handling code path of `vkGetBufferMemoryRequirements2`.

## Failure Meaning

### Failure Cause Mapping

For the primary behavioral axis (`create_*`):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `create_no_flags` | `memoryTypeBits` reporting failure for a baseline buffer; the implementation advertises no compatible memory type for the requested usage flags |
| `create_protected` | `memoryTypeBits` reporting failure for a protected buffer (no protected-memory type advertised), or protected device creation fails before the query is reached |
| `create_sparse_binding` | `memoryTypeBits` reporting failure for a sparse-binding buffer; sparse-backed memory type not advertised |
| `create_sparse_binding_sparse_aliased` | `memoryTypeBits` reporting failure for a sparse-binding + aliased buffer |
| `create_sparse_binding_sparse_residency` | `memoryTypeBits` reporting failure for a sparse-binding + residency buffer |
| `create_sparse_binding_sparse_residency_sparse_aliased` | `memoryTypeBits` reporting failure for a buffer with all three sparse flags |

For the verification-mode axis (orthogonal to `create_*`):

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| non-prefixed `*_usage_bits` leaf | `memoryTypeBits` returned as 0 for a valid buffer configuration |
| `size_req_*` leaf | Reported `reqs.size` exceeds `align(bufferSize, reqs.alignment)` for at least one iterated size, violating the `VK_KHR_maintenance4` bound |

### Cause Analysis

#### memoryTypeBits reporting failure

**Possible failure symptoms:** the test case returns `TestStatus::fail` with a non-zero failing sub-configuration count. The test log section emitted by `logFailedSubtests()` lists the `VkBufferCreateFlags`, `VkBufferUsageFlags`, and `VkExternalMemoryHandleTypeFlags` triples that produced `memoryTypeBits == 0`. The pass count for the case is reduced accordingly.

**Possible implementation causes:** for baseline buffers (`create_no_flags`), the implementation's `vkGetBufferMemoryRequirements*` returned a `memoryTypeBits` value with no bits set, meaning no `VkMemoryType` in `VkPhysicalDeviceMemoryProperties` was flagged as compatible with the buffer's usage flags. For protected buffers (`create_protected`), the implementation did not advertise any memory type with the `VK_MEMORY_PROPERTY_PROTECTED_BIT` set, or the protected device was created without exposing such a type. For sparse buffers, the implementation did not advertise a memory type compatible with the sparse create flags. Whether the implementation is genuinely non-conformant or the test requested an unsupported configuration that should have been pruned at `checkSupport` time requires source-level investigation against the specific failing triple.

#### Protected device creation failure

**Possible failure symptoms:** the case terminates before any `memoryTypeBits` check is performed, typically with an exception from `vkCreateDevice` raised through `createProtectedDevice()`. The test log does not contain a `Failed subtests` section because the iteration did not reach the failing-subtest recording path.

**Possible implementation causes:** the implementation's protected queue family or protected memory feature advertisement is inconsistent with what `VkPhysicalDeviceProtectedMemoryFeatures::protectedMemory` reported during `checkSupport`, or device creation with `VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT` is rejected by the driver. Source-level investigation is needed to confirm whether the failure is a driver-side inconsistency or a test-side assumption mismatch.

#### Size requirement over-report

**Possible failure symptoms:** a `size_req_*` leaf returns `TestStatus::fail` with a non-zero failing count, and `logFailedSubtests()` records the `VkBufferCreateFlags`/`VkBufferUsageFlags`/`VkExternalMemoryHandleTypeFlags` triple that produced `reqs.size > align(bufferSize, reqs.alignment)`. The failure is observed only on implementations that advertise `VK_KHR_maintenance4`.

**Possible implementation causes:** the implementation's `vkGetBufferMemoryRequirements*` returned a `size` value that exceeds the bound guaranteed by `VK_KHR_maintenance4` for a buffer of the requested `size`. Possible reasons include the driver adding internal alignment padding beyond what the maintenance4 bound permits, or returning a `size` derived from a larger internal allocator granularity. Confirming whether the reported `size` is actually non-conformant requires comparing the reported `size`, `alignment`, and the requested `bufferSize` against the spec language of `VK_KHR_maintenance4`.

## Case Pruning

### Requirement-based pruning

[`MemoryRequirementsTest::checkSupport()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L373) gates each registered case before execution:

- `VK_KHR_get_physical_device_properties2` is required for every case ([L379](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L379)).
- `VK_KHR_get_memory_requirements2` is required when `useMethod2 = true` ([L381-L382](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L381-L382)).
- `VK_KHR_maintenance4` is required when `testSizeRequirements = true` ([L615-L619](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L615-L619)).
- `sparseBinding` is required for any `create_*` value containing `VK_BUFFER_CREATE_SPARSE_BINDING_BIT` ([L405-L409](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L405-L409)).
- `sparseResidencyBuffer` is required for any `create_*` value containing `VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT` ([L410-L416](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L410-L416)).
- `sparseResidencyAliased` is required for any `create_*` value containing `VK_BUFFER_CREATE_SPARSE_ALIASED_BIT` ([L417-L423](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L417-L423)).
- The protected memory feature is required for `create_protected` ([L424-L430](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L424-L430)).
- `VK_KHR_acceleration_structure` is required for usage bits containing acceleration-structure or shader-binding-table usage ([L462-L476](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L462-L476)).
- `VK_EXT_buffer_device_address` (or core support) is required for `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` ([L478-L488](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L478-L488)).
- `VK_KHR_video_queue` and either `VK_KHR_video_decode_h264` or `VK_KHR_video_encode_h264` (plus a queue family exposing the matching codec operation) are required for video usage bits ([L491-L563](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L491-L563)).

`checkSupport` prunes by removing unsupported usage-flag combinations from the instance input list; if all combinations for a case are removed, the case throws `NotSupportedError` and is reported as skipped rather than failed.

### Design-based pruning

[`updateBufferCreateFlags()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L193) prunes the `create_*` matrix during test registration:

- **VUID-00918 enforcement:** any combination containing `sparse_residency` or `sparse_aliased` has `sparse_binding` co-set automatically ([L205-L209](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L205-L209)). This is why registered names such as `create_sparse_binding_sparse_residency` always include the `sparse_binding` token.
- **VUID-None-01888 enforcement:** any combination that mixes `protected` with a sparse bit has the sparse bits removed, and the resulting empty combination is dropped from the matrix ([L211-L226](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L211-L226)). This is why no `create_protected_sparse_*` intermediate node exists.
- **Redundant zero-bit removal:** because `VkBufferCreateFlagBits(0)` ("no_flags") is a valid entry in `AvailableBufferCreateBits`, the combiner can produce sets that contain both the zero bit and a real bit. The post-processor strips the zero bit from any set with more than one entry ([L230-L238](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L230-L238)) so the resulting `VkBufferCreateFlags` value is unambiguous.
- **Duplicate removal:** after the above transformations, duplicate flag sets are removed ([L241-L245](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L241-L245)).
- **VKSC build exclusion:** sparse create bits, video usage bits, and the `size_req_*` verification mode are excluded entirely under `CTS_USES_VULKANSC` via `#ifndef CTS_USES_VULKANSC` guards ([L122-L126](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L122-L126), [L140-L151](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L140-L151), [L1032-L1036](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1032-L1036)). On VKSC the matrix collapses to two `create_*` values (`create_no_flags`, `create_protected`) and five non-`size_req` leaves per `(ext_mem_flags_*, method*)` combination.

The `BufferFateBits` combiner is disabled in [`createBufferMemoryRequirementsTests()`](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L1002-L1018); fate bits are iterated individually rather than as a cartesian product. The disabled `#if 0` block in source records the conscious choice to avoid combinatorial explosion.

## Key Takeaways

- The test family's central guarantee is that `vkGetBufferMemoryRequirements*` returns a non-zero `memoryTypeBits` for every valid `(create flags, usage flags, external memory handle types)` triple, after VUID-driven pruning has removed combinations the spec forbids.
- The `create_*` intermediate node is the primary behavioral axis: each value selects a different `VkBufferCreateFlags` family (baseline, protected, or one of four sparse combinations) and triggers distinct feature gates and, for protected, a dedicated device.
- The `size_req_*` leaves add a second, disjoint verification mode grounded in `VK_KHR_maintenance4`: they check that `reqs.size` does not exceed `align(bufferSize, reqs.alignment)` across an iterated size range, and do not re-check `memoryTypeBits`.
- `updateBufferCreateFlags()` enforces VUID-00918 and VUID-None-01888 at registration time, which is why the registered `create_*` names already reflect the implied `sparse_binding` bit and why no protected-plus-sparse combination appears in mustpass.
- See `## Failure Meaning` for how to interpret a failure: a non-zero `memoryTypeBits` failure points at memory-type advertisement for the relevant buffer class, while a `size_req_*` failure points at `VK_KHR_maintenance4` size-bound violation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [createBufferMemoryRequirementsTests()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L977) | Builds the `buffer_memory_requirements` tree from the pruned `create_*`, `ext_mem_flags_*`, `method*`, and fate-bit cross product |
| Parent registration | [vktApiTests.cpp#L127](../../../modules/vulkan/api/vktApiTests.cpp#L127) | Adds the test family to the `api` test category |
| VUID-driven create-flag pruning | [updateBufferCreateFlags()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L193) | Enforces VUID-00918 and VUID-None-01888, removes redundant zero bit, removes duplicates |
| Available create / fate / usage / ext-mem bit tables | [L119-L174](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L119-L174) | Source of registered `create_*` names and usage-flag category mappings |
| Test case configuration | [TestConfig](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L87) | Carries `useMethod2`, `createBits`, `fateBits`, `incExtMemTypeFlags`, `testSizeRequirements` |
| Test case class | [MemoryRequirementsTest](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L276) | `TestCase` subclass; `checkSupport()` performs feature gating and builds instance inputs |
| Instance class | [BufferMemoryRequirementsInstance](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L248) | `TestInstance` subclass whose `iterate()` runs the host-side flow |
| Iteration body | [BufferMemoryRequirementsInstance::iterate()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L827) | Creates the buffer(s), queries memory requirements, applies the `memoryTypeBits` and `size_req` checks, records failing triples |
| Query method dispatch | [getBufferMemoryRequirements()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L711) / [getBufferMemoryRequirements2()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L683) | Wraps the two Vulkan entry points; `method2` chains `VkMemoryDedicatedRequirements` |
| Protected device setup | [createProtectedDevice()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L794) | Creates a separate device with `VK_DEVICE_QUEUE_CREATE_PROTECTED_BIT` for `create_protected` cases |
| Failed-subtest logging | [logFailedSubtests()](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L622) | Emits the failing `VkBufferCreateFlags`/`VkBufferUsageFlags`/`VkExternalMemoryHandleTypeFlags` triples |
| External-memory chain helper | [chainVkStructure&lt;VkExternalMemoryBufferCreateInfo&gt;](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L718) | Builds the `VkExternalMemoryBufferCreateInfo` pNext entry used when `incExtMemTypeFlags` is true |
| Video profile chain helper | [chainVkStructure&lt;VkVideoProfileListInfoKHR&gt;](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.cpp#L731) | Builds the `VkVideoProfileListInfoKHR` pNext entry used for video usage bits (non-VKSC) |
| Header | [vktApiBufferMemoryRequirementsTests.hpp](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTests.hpp#L1) | Public entry point declaration |
| Bit-set utility | [vktApiBufferMemoryRequirementsTestsUtils.hpp](../../../modules/vulkan/api/vktApiBufferMemoryRequirementsTestsUtils.hpp#L1) | `BitsSet` template used to enumerate and filter flag combinations |
| Mustpass listing | [api.txt](../../../mustpass/main/vk-default/api.txt) | 240 registered leaves under `dEQP-VK.api.buffer_memory_requirements.*` |
