## Overview

**Core question:** Do transfer-capable queue families report the image-transfer granularities checked by the maintenance11 test?

- [`vktApiMaintenance11Tests.cpp`](../../../modules/vulkan/api/vktApiMaintenance11Tests.cpp#L62-L118) implements `api.maintenance11.queue_properties`.
- It queries queue-family properties, then checks minimum and optimal image-transfer granularity for families explicitly advertising `VK_QUEUE_TRANSFER_BIT`.
- This is a host-side property test, not a copy-command or throughput test.

## Background Knowledge

- Queue-family transfer granularity describes image-region constraints or preferred transfer granularity. Minimum and optimal granularities are different properties; a preferred granularity is not a measurement of transfer speed.
- Extension property structures are attached through `pNext` to a base query structure so one query can populate both.

## Registration Hierarchy

```text
api.maintenance11
└── queue_properties
```

[`createMaintenance11Tests()`](../../../modules/vulkan/api/vktApiMaintenance11Tests.cpp#L145-L152) registers the single leaf. The [API dispatcher](../../../modules/vulkan/api/vktApiTests.cpp#L142-L148) excludes it from Vulkan SC.

## Behavior Parameters

There is one fixed test case, without a generated parameter matrix. `queue_properties` iterates all returned queue families but validates only those whose `queueFlags` contain `VK_QUEUE_TRANSFER_BIT`.

## Shader Analysis

No shader, pipeline, draw, dispatch, or transfer command is involved. The test queries properties and evaluates them on the host.

## Runtime Execution and Result Checking

- Query the queue-family count with `vkGetPhysicalDeviceQueueFamilyProperties2`.
- Allocate a base-property structure and `VkQueueFamilyOptimalImageTransferGranularityPropertiesKHR` for each family. Initialize optimal granularity to `(1337, 1337, 1337)` before chaining and querying the structures.
- Skip families without an explicit transfer bit.
- Require `minImageTransferGranularity` to equal `(1, 1, 1)`.
- Require optimal granularity to be either `(0, 0, 0)` or positive powers of two in all three dimensions. Mixed zero/nonzero dimensions fail.
- Return failure at the first invalid family; otherwise return pass. See [the query and checks](../../../modules/vulkan/api/vktApiMaintenance11Tests.cpp#L70-L117).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `queue_properties`: minimum granularity | A transfer-capable family reports a minimum other than `(1, 1, 1)`. |
| `queue_properties`: optimal granularity | The optimal-property chain was not populated, or the dimensions are neither all zero nor all positive powers of two. |

### Cause Analysis

#### Invalid minimum or optimal property

**Possible failure symptoms:** The case reports a queue-family granularity error. An untouched optimal sentinel also fails the power-of-two check.

**Possible implementation causes:** The implementation may expose stale queue-family limits or mishandle the extension structure in the output chain. This test does not issue image copies, so its failure does not directly demonstrate incorrect transfer execution or performance. The minimum-granularity diagnostic prints the family index where a granularity value would normally be expected; inspect the queried properties rather than interpreting that number as an extent.

## Case Pruning

### Requirement-based pruning

The [support callback](../../../modules/vulkan/api/vktApiMaintenance11Tests.cpp#L132-L135) requires `VK_KHR_maintenance11`. Unsupported functionality produces a skip.

### Design-based pruning

Only families with `VK_QUEUE_TRANSFER_BIT` are checked. The implementation does not infer eligibility solely from graphics or compute flags. Vulkan SC does not register this family.

## Key Takeaways

- One query-only leaf checks two distinct granularity properties.
- The optimal check accepts all-zero dimensions or three positive powers of two.
- A pass establishes the implemented property checks, not image-copy correctness or throughput.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Property query and validation | [Maintenance11QueuePropsTestInstance](../../../modules/vulkan/api/vktApiMaintenance11Tests.cpp#L62-L118) | Defines sentinel initialization, queue selection, and failure predicates. |
| Support and registration | [case and factory](../../../modules/vulkan/api/vktApiMaintenance11Tests.cpp#L121-L151) | Requires the extension and registers `queue_properties`. |
| Mustpass | [api.txt](../../../mustpass/main/vk-default/api.txt) | Contains `dEQP-VK.api.maintenance11.queue_properties`. |
