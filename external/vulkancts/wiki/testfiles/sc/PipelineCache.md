## Overview

**Core question:** Does Vulkan SC reject pipeline-cache data whose vendor or device identity is incorrect?

- This page covers `vktPipelineCacheSCTests.cpp`, which registers `sc.pipeline_cache` with the leaves `incorrect_vendor_id` and `incorrect_device_id`.
- Each leaf seeds a non-empty safety-critical pipeline cache, mutates one identity field in its header, and supplies the bytes as initial cache data during SC device creation.
- The expected oracle is `VK_ERROR_INVALID_PIPELINE_CACHE_DATA`; direct `vkCreatePipelineCache` is checked only if device creation unexpectedly accepts the data.
- Graphics, compute, and GLSL code exist to seed the cache, but no command buffer is submitted and no shader output is read. The tested behavior is cache-data input validation.

## Background Knowledge

- A Vulkan pipeline cache stores implementation-generated data that can be supplied again as initial data. Safety-critical Vulkan adds a defined cache-data path and resource reservation requirements around device creation.
- A cache header's vendor and device identity associate the data with the implementation that produced it. This test deliberately changes one identity field so the implementation must reject the bytes instead of treating them as valid initial data.
- A subprocess-aware CTS case can use a parent invocation to create reserved resources and a subprocess invocation to exercise the actual check. That division matters here because the parent seeds the cache, while the subprocess mutates and offers its bytes to SC device creation.

## Registration Hierarchy

```text
sc.pipeline_cache
├── incorrect_vendor_id
└── incorrect_device_id
```

The family factory registers exactly these two leaves with `addFunctionCaseWithPrograms()` ([family registration](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L365-L382)); the `sc` category wiring places the family below the safety-critical root ([category wiring](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L65)). The default mustpass contains both executable paths at [sc.txt#L148-L149](../../../mustpass/main/vksc-default/sc.txt#L148-L149).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| identity field mutation | `incorrect_vendor_id`, `incorrect_device_id` | Selects which safety-critical cache-header identity field is replaced before ingestion. | [mutation switch](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L235-L258) |
| mutated vendor ID | `uint32_t(VK_VENDOR_ID_MAX_ENUM)` | Supplies an intentionally invalid/implausible vendor identity while preserving the other copied bytes. | [vendor mutation](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L235-L247) |
| mutated device ID | `0xFFFFFFFF` | Supplies an intentionally invalid/implausible device identity while preserving the other copied bytes. | [device mutation](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L247-L258) |
| cache-ingestion path | SC device creation; direct `vkCreatePipelineCache` fallback | The primary path validates initial data while creating the SC device; direct cache creation runs only after unexpected primary acceptance. | [device result check](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L315-L333), [fallback](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L335-L360) |

There are no registered dimensions for cache magic, header version, UUID, size, flags, arbitrary corruption, or a valid alternate identity. Their absence is scope, not implicit coverage ([factory loop](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L365-L382)).

## Behavior Parameters

The primary behavioral axis is the identity field selected for mutation. Both values use the same seeded cache and the same expected rejection; only the corrupted identity field differs.

### `incorrect_vendor_id` — mutate the vendor identity

The subprocess changes `headerVersionOne.vendorID` to `uint32_t(VK_VENDOR_ID_MAX_ENUM)` in the copied cache data. All other copied bytes remain unchanged. The implementation must reject this initial data with `VK_ERROR_INVALID_PIPELINE_CACHE_DATA` ([copy and mutation](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L235-L258)).

### `incorrect_device_id` — mutate the device identity

The subprocess changes `headerVersionOne.deviceID` to `0xFFFFFFFF` in the copied cache data. This isolates device identity handling from the vendor mutation; the required result is the same invalid-cache-data error ([copy and mutation](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L235-L258)).

## Shader Analysis

This page has no shader component. The implementation uses shaders only to create pipeline objects; no command buffer executes them and no shader output is checked. The oracle is the pipeline-cache result.

## Runtime Execution and Result Checking

- In the parent invocation, the test creates a custom instance and uses the current physical device. It creates vertex/fragment shader modules, a graphics pipeline with offline identifier `PCST_GRAPHICS`, and a compute pipeline with offline identifier `PCST_COMPUTE`. Neither pipeline is submitted or executed; successful creation seeds a non-empty resource/package cache ([parent setup](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L103-L115), [graphics construction](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L120-L192), [compute construction](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L194-L232)).
- In the subprocess, the test copies the resource-interface cache returned by `ResourceInterface::getCacheDataSize()` and `getCacheData()`, records `initialDataSize`, and changes exactly one header identity field ([copy and mutation](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L235-L258)).
- It builds `VkPipelineCacheCreateInfo` with `VK_PIPELINE_CACHE_CREATE_READ_ONLY_BIT | VK_PIPELINE_CACHE_CREATE_USE_APPLICATION_STORAGE_BIT`, the copied byte size, and the mutated byte buffer. That structure is attached to `VkDeviceObjectReservationCreateInfo`, whose reservation counts cover layouts, render pass, pipelines, and caches; the reservation chain is linked through `VkPhysicalDeviceVulkanSC10Features` into `VkDeviceCreateInfo` ([device reservation setup](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L260-L313)).
- `instance.createUncheckedDevice()` is the primary oracle. Each leaf requires `VK_ERROR_INVALID_PIPELINE_CACHE_DATA`; any other result changes the status to `Fail`, and any error returns immediately ([first result check](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L315-L333)).
- Only after unexpected `VK_SUCCESS` does the test resolve `vkCreatePipelineCache` and `vkDestroyPipelineCache` with `vkGetDeviceProcAddr` and offer the same cache-create structure directly. That fallback must also return `VK_ERROR_INVALID_PIPELINE_CACHE_DATA`; a successfully created cache is destroyed ([fallback](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L335-L360)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `incorrect_vendor_id` | Vendor identity validation accepted the mutation, or the rejection was translated to another result. |
| `incorrect_device_id` | Device identity validation accepted the mutation, or the rejection was translated to another result. |

A failure before the result assertion can instead indicate cache-resource acquisition, cache-header interpretation, SC reservation-chain construction, or device setup; the source does not localize such errors to a shader or parser routine.

### Cause Analysis

#### Cache identity validation and result reporting

**Possible failure symptoms:** The selected mutation produces `VK_SUCCESS` or an error other than `VK_ERROR_INVALID_PIPELINE_CACHE_DATA`. If device creation unexpectedly accepts the bytes but direct `vkCreatePipelineCache` rejects them, the two ingestion paths disagree.

**Possible implementation causes:** The implementation may compare vendor or device identity incorrectly, accept cache data associated with a different implementation, or map the validation failure to the wrong `VkResult`. The test does not expose the internal header-comparison routine, so further implementation inspection is needed to localize the cause.

#### Cache seeding, reservation, or setup failures

**Possible failure symptoms:** The case fails before reaching the intended cache-data result check, for example while obtaining resource-interface data, constructing the reserved SC device, or creating the seed pipelines.

**Possible implementation causes:** The source evidence supports investigating cache byte availability and format, the explicit reservation counts and `pNext` chain, and device creation. It does not support blaming the setup shaders, because their output is never executed ([device reservation setup](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L260-L333)).

## Case Pruning

### Requirement-based pruning

- `createPipelineCacheTests()` contains no feature, limit, format, or support predicate; both leaves are registered unconditionally ([factory loop](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L365-L382)).
- Resource-interface failures, seed-pipeline failures, device-creation failures, and other framework errors can prevent a leaf from reaching its result assertion. These are execution/setup failures, not parameter-based pruning.

### Design-based pruning

- The family intentionally covers only vendor-ID and device-ID mutations. Cache magic, header version, UUID, size, flags, arbitrary corruption, and valid alternate identities are not generated.
- The test uses one seeded graphics pipeline and one seeded compute pipeline, fixed offline identifiers, and one mutation per leaf. Other pipeline states and cache contents are outside this registered family.

## Key Takeaways

- `pipeline_cache` tests rejection of identity-mismatched safety-critical cache data, not rendering, compute output, or shader correctness.
- `incorrect_vendor_id` and `incorrect_device_id` isolate two header identity fields and both require `VK_ERROR_INVALID_PIPELINE_CACHE_DATA`.
- The parent process seeds a non-empty cache; the subprocess performs the mutation and primary SC device-creation check.
- Direct `vkCreatePipelineCache` is only a fallback after unexpected device-creation acceptance, not a second normally executed oracle.
- A setup failure does not by itself identify cache identity validation as the cause; use the failure stage and the distinctions in `## Failure Meaning`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| SC category wiring | [vktSafetyCriticalTests.cpp#L45-L65](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L65) | Places `pipeline_cache` below `sc`. |
| Shader callback | [vktPipelineCacheSCTests.cpp#L61-L101](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L61-L101) | Defines setup-only GLSL programs. |
| Parent cache seeding | [vktPipelineCacheSCTests.cpp#L103-L232](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L103-L232) | Creates graphics and compute pipelines without execution. |
| Cache mutation | [vktPipelineCacheSCTests.cpp#L235-L258](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L235-L258) | Defines exact vendor/device replacements. |
| SC ingestion and oracle | [vktPipelineCacheSCTests.cpp#L260-L333](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L260-L333) | Defines the reservation chain and primary result check. |
| Direct fallback | [vktPipelineCacheSCTests.cpp#L335-L360](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L335-L360) | Defines the secondary result check and cleanup. |
| Family registration | [vktPipelineCacheSCTests.cpp#L365-L382](../../../modules/vulkan/sc/vktPipelineCacheSCTests.cpp#L365-L382) | Defines exact group and leaf names. |
| Default mustpass | [sc.txt#L148-L149](../../../mustpass/main/vksc-default/sc.txt#L148-L149) | Confirms both default executable paths. |
