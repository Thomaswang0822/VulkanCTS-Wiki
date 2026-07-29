## Overview

**Core question:** does the implementation report a valid `vkGetDeviceMemoryCommitment` value for lazily allocated memory (never exceeding the relevant upper bound), both when checked against a bound transient image's memory requirements and when checked against the size of each unbound allocation?

- Source file: [vktApiGetMemoryCommitment.cpp](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L1) in the `api` source directory.
- Test category `api`, test family `get_memory_commitment`, registered under `dEQP-VK.api.get_memory_commitment`.
- Two test case leaves: `memory_commitment` exercises a transient color attachment image bound to lazily allocated memory and queries commitment before and after a render pass; `memory_commitment_allocate_only` queries commitment on unbound lazy allocations of randomized sizes.
- The implementation registers the family root; [createMemoryCommitmentTests()](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L479-L496) creates the `get_memory_commitment` group and adds both leaves directly.
- The page covers a host-side memory-query test. Shaders exist in `memory_commitment` only to drive rendering work against the transient image; they are not the behavior under test.

## Background Knowledge

- `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` marks a memory type whose backing store is not fully committed at allocation time. The implementation may commit physical memory lazily as the bound resource is used, and may decommit memory when the resource is no longer needed. This property is typically associated with transient attachments on tile-based renderers.
- `vkGetDeviceMemoryCommitment(device, memory, pCommittedMemoryInBytes)` queries the bytes of backing memory currently committed for a `VkDeviceMemory` object allocated from a lazy memory type. Per the Vulkan specification, the returned value must be less than or equal to the size of the allocation; it may be zero if no memory has been committed yet.
- `VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT` allows an image to be used as a transient attachment. Such images are typically backed by lazy memory when available; their contents are undefined outside the render pass that operates on them.

## Registration Hierarchy

```text
api.get_memory_commitment
├── memory_commitment
└── memory_commitment_allocate_only
```

The test family has no intermediate nodes; [createMemoryCommitmentTests()](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L479-L496) registers both test case leaves directly under `get_memory_commitment`. The parent dispatcher attaches `get_memory_commitment` to the `api` test category unconditionally at [vktApiTests.cpp#L115](../../../modules/vulkan/api/vktApiTests.cpp#L115), with no VulkanSC guard.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `memory_commitment`, `memory_commitment_allocate_only` | Each leaf tests the commitment query against a different upper bound: image memory requirements size for bound memory, or allocation size for unbound memory. | [createMemoryCommitmentTests()](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L479-L496) |
| Image format | `VK_FORMAT_R32_UINT` | Fixed format for the transient color attachment in `memory_commitment`. | [L147](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L147) |
| Image extent | `256x256` | Fixed extent for the transient image; also defines `pixelDataSize` used by the commitment check. | [L148](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L148) |
| Image usage | `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT \| VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT` | Required to make the image a transient color attachment compatible with lazy memory. | [L153](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L153) |
| Memory property | `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` | Selects lazy memory types for both allocation and the commitment query. | [L115](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L115), [L369](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L369) |
| Random allocation sizes | 10 per memory type, 1 to 1000 bytes | Randomized upper-bound inputs for the `memory_commitment_allocate_only` leaf. | [L371](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L371), [L381](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L381) |

The `MemoryCommitmentCaseParams` struct carries `bufferSize = 2048` and `elementOffset = 0` ([L481-L484](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L481-L484)), but only `bufferViewSize = 256` is consumed (as the render extent at [L87](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L87)). The other two fields are vestigial in this implementation.

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf tests a different upper bound for the commitment query.

### `memory_commitment`: commitment upper bound for memory bound to a transient image

The leaf creates a `256x256` `VK_FORMAT_R32_UINT` transient color attachment image, binds lazily allocated memory, builds a graphics pipeline, and queries `vkGetDeviceMemoryCommitment` before and after a render pass that performs a clear attachment operation. The check, [isDeviceMemoryCommitmentOk()](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L447-L477), verifies that for at least one lazy memory type, a fresh `pixelDataSize`-byte allocation reports commitment less than or equal to the bound image's `memoryRequirements.size`.

### `memory_commitment_allocate_only`: commitment upper bound for unbound lazy allocations

The leaf allocates lazy memory of 10 randomized sizes (1 to 1000 bytes) per supported lazy memory type and queries `vkGetDeviceMemoryCommitment` immediately, without binding the memory to any resource. The check verifies that the reported commitment does not exceed the allocation size; a non-zero commitment before binding is logged as a warning but does not fail the test.

## Shader Analysis

Shader code is not part of the tested behavior. The `memory_commitment` leaf builds a graphics pipeline with simple vertex and fragment shaders ([initPrograms()](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L410-L428)) solely to issue rendering work against the transient color attachment; the shader logic itself is not under test. The `memory_commitment_allocate_only` leaf creates no pipeline at all. No representative shader walkthrough is provided.

## Runtime Execution and Result Checking

`memory_commitment` ([MemoryCommitmentTestInstance::iterate()](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L113-L332)):

- Throws `NotSupportedError` if no memory type supports `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` ([L139-L140](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L139-L140)).
- Creates a `256x256` `VK_FORMAT_R32_UINT` image with `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT` and `VK_IMAGE_TILING_OPTIMAL` ([L142-L158](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L142-L158)).
- Allocates and binds lazy memory to the image ([L160-L164](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L160-L164)).
- Creates image view, render pass, framebuffer, descriptor set layout, pipeline layout, shader modules, and graphics pipeline ([L166-L264](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L166-L264)).
- Calls `isDeviceMemoryCommitmentOk(memoryRequirements)` before rendering ([L267](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L267)).
- Records a command buffer that transitions the image to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, begins the render pass, binds the pipeline, calls `cmdClearAttachments`, ends the render pass ([L290-L319](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L290-L319)).
- Submits and waits on the universal queue ([L322-L323](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L322-L323)).
- Calls `isDeviceMemoryCommitmentOk(memoryRequirements)` again after rendering ([L326](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L326)).
- Passes if both calls returned `true`; otherwise fails.

`memory_commitment_allocate_only` ([MemoryCommitmentAllocateOnlyTestInstance::iterate()](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L362-L408)):

- Throws `NotSupportedError` if no memory type supports `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` ([L375-L376](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L375-L376)).
- Generates 10 random allocation sizes in the range 1 to 1000 bytes using `rand() % 1000 + 1` ([L379-L382](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L379-L382)). The test does not seed the RNG deterministically.
- For each lazy memory type, for each of the 10 sizes: allocates `VkDeviceMemory`, queries `vkGetDeviceMemoryCommitment`, logs a warning if commitment is non-zero, and returns `fail` if commitment exceeds the allocation size ([L384-L406](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L384-L406)).
- Passes if no allocation reported commitment greater than its size.

Final pass/fail for both leaves: each leaf returns `tcu::TestStatus::pass("Pass")` only if every checked condition holds; otherwise it returns `tcu::TestStatus::fail("Fail")`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `memory_commitment` | Commitment reported by `vkGetDeviceMemoryCommitment` exceeds the bound image's `memoryRequirements.size` for every lazy memory type. |
| `memory_commitment_allocate_only` | Commitment reported by `vkGetDeviceMemoryCommitment` exceeds the allocation size for some lazy memory type and randomized size. |

### Cause Analysis

#### Commitment exceeds the upper bound

**Possible failure symptoms:** the case returns `tcu::TestStatus::fail("Fail")`. `memory_commitment` fails when [isDeviceMemoryCommitmentOk()](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L447-L477) returns `false` because no lazy memory type reports commitment less than or equal to `memoryRequirements.size`. `memory_commitment_allocate_only` fails when the comparison at [L403-L404](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L403-L404) trips for some size and memory type. Neither leaf logs a per-cause message identifying which memory type or size triggered the failure.

**Possible implementation causes:** per the Vulkan specification, `vkGetDeviceMemoryCommitment` must return a value less than or equal to the size of the allocation. A value exceeding the allocation size, or exceeding the bound resource's memory requirements size in the bound case, indicates the implementation is reporting more committed memory than the allocation can hold. This points to driver-side accounting for lazy memory types: the reported commitment value is computed incorrectly, or the lazy-allocation path is not backing the memory lazily and reports a fixed inflated size. The test symptom alone does not identify which lazy memory type or which internal counter is wrong; source-level investigation of the driver's lazy-memory commitment reporting is needed to pinpoint the cause.

The `memory_commitment_allocate_only` leaf logs `Warning: Memory commitment not null before binding.` ([L398-L402](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L398-L402)) when a freshly allocated, unbound `VkDeviceMemory` reports non-zero commitment. This warning does not cause a failure: the Vulkan specification permits `vkGetDeviceMemoryCommitment` to return any value between zero and the allocation size, including before the memory is bound to a resource. A non-zero value before binding is unusual for a lazy memory type but not a spec violation.

## Case Pruning

### Requirement-based pruning

- Both test case leaves require at least one memory type that supports `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT`. Implementations without such a memory type skip the entire test family with `NotSupportedError` ([L139-L140](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L139-L140), [L375-L376](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L375-L376)). This is common on desktop GPUs that do not expose lazy memory types.
- The parent dispatcher registers the test family unconditionally for both Vulkan and VulkanSC builds; it does not guard `createMemoryCommitmentTests` with `#ifndef CTS_USES_VULKANSC` ([vktApiTests.cpp#L115](../../../modules/vulkan/api/vktApiTests.cpp#L115)).

### Design-based pruning

- `memory_commitment` uses a fixed image configuration (`256x256`, `VK_FORMAT_R32_UINT`, color attachment with transient usage). The test does not parameterize over format, extent, mip count, sample count, or attachment type; varying those would test the same commitment-query property against different resource shapes, which is out of scope for this family.
- `memory_commitment_allocate_only` uses 10 randomized allocation sizes per lazy memory type rather than an exhaustive size matrix. The randomized subset is sufficient because the tested property is the upper bound, not a size-dependent behavior.
- The `MemoryCommitmentCaseParams` fields `bufferSize` and `elementOffset` are not consumed by the test logic; only `bufferViewSize` is used as the render extent. These vestigial fields are not pruned by the implementation but have no behavioral effect.

## Key Takeaways

- The test family verifies the upper-bound contract of `vkGetDeviceMemoryCommitment` for lazily allocated memory: the reported commitment must not exceed the allocation size, and (in the bound case) must not exceed the bound resource's memory requirements size.
- `memory_commitment` checks commitment of a fresh lazy allocation against a bound transient image's `memoryRequirements.size` (with a render pass driving work on the image); `memory_commitment_allocate_only` checks commitment against each unbound allocation's own size. The two leaves cover the same upper-bound invariant with different upper bounds.
- A non-zero commitment before binding is logged as a warning but does not fail the test, because the Vulkan specification permits that behavior for lazy memory types.
- Both leaves skip on implementations without `VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT` memory types, which is common on desktop GPUs.
- See `## Failure Meaning` for why a failure points to driver-side lazy-memory accounting and why the test cannot identify the specific memory type or counter at fault.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createMemoryCommitmentTests()` | [vktApiGetMemoryCommitment.cpp#L479-L496](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L479-L496) | Public entry point that creates the `get_memory_commitment` test family and registers both test case leaves. |
| `MemoryCommitmentTestInstance::iterate()` | [vktApiGetMemoryCommitment.cpp#L113-L332](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L113-L332) | Implementation of the `memory_commitment` leaf: image creation, binding, pipeline build, render pass, and commitment checks. |
| `MemoryCommitmentAllocateOnlyTestInstance::iterate()` | [vktApiGetMemoryCommitment.cpp#L362-L408](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L362-L408) | Implementation of the `memory_commitment_allocate_only` leaf: randomized allocation loop and commitment upper-bound check. |
| `isDeviceMemoryCommitmentOk()` | [vktApiGetMemoryCommitment.cpp#L447-L477](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L447-L477) | Helper used by `memory_commitment` that allocates a fresh lazy memory object and checks commitment against `memoryRequirements.size`. |
| `initPrograms()` | [vktApiGetMemoryCommitment.cpp#L410-L428](../../../modules/vulkan/api/vktApiGetMemoryCommitment.cpp#L410-L428) | Generates the vertex and fragment shaders used by `memory_commitment`'s graphics pipeline. |
| Parent registration | [vktApiTests.cpp#L115](../../../modules/vulkan/api/vktApiTests.cpp#L115) | Adds `get_memory_commitment` to the `api` test category, unconditionally for Vulkan and VulkanSC. |
| Header | [vktApiGetMemoryCommitment.hpp](../../../modules/vulkan/api/vktApiGetMemoryCommitment.hpp#L1) | Declares `createMemoryCommitmentTests` for the parent dispatcher. |
