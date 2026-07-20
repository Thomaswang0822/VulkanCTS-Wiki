## Overview

**Core question:** Do the acceleration-structure and ray-tracing-pipeline property limits reported by the implementation fall within the Vulkan spec's required minimum and maximum ranges?

- [vktRayTracingLimitsTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp) registers and implements the `limits` test family under the `ray_tracing_pipeline` test category.
- The family has two test case leaves: `accel_struct_props` and `ray_tracing_props`. Each leaf queries ray-tracing-related property structs through `makeRayTracingProperties` and asserts each reported field against a hard-coded spec-required bound.
- `accel_struct_props` validates eight fields of `VkPhysicalDeviceAccelerationStructurePropertiesKHR`. `ray_tracing_props` validates eight fields of `VkPhysicalDeviceRayTracingPipelinePropertiesKHR`. The two leaves are otherwise identical in mechanism: a random iteration count, a fresh property fetch each iteration, a per-field range check, and a fail on the first out-of-range field.
- The page explains the registered hierarchy, the behavioral axis formed by the two property families, the per-field bounds checked, and what a failure of each leaf points at.

## Background Knowledge

- **Ray tracing property structs.** `VK_KHR_acceleration_structure` introduces `VkPhysicalDeviceAccelerationStructurePropertiesKHR`, and `VK_KHR_ray_tracing_pipeline` introduces `VkPhysicalDeviceRayTracingPipelinePropertiesKHR`. Both are queried through `vkGetPhysicalDeviceProperties2` with the corresponding `pNext` chain entry. The Vulkan spec sets required minimum (and in some cases maximum) values for each reported field.
- **`makeRayTracingProperties`.** The CTS helper at [vkRayTracingUtil.cpp#L5045-L5049](../../../framework/vulkan/vkRayTracingUtil.cpp#L5045-L5049) returns a `RayTracingProperties` wrapper whose constructor fetches each property struct through a separate `vkGetPhysicalDeviceProperties2` call with that struct chained via `pNext` ([RayTracingPropertiesKHR constructor](../../../framework/vulkan/vkRayTracingUtil.cpp#L5037-L5043)). Each getter on the wrapper returns one field from those structs.
- **Spec-required bounds.** The test encodes the spec's required lower or upper bound for each property as a constant and compares the reported value against it. A reported value outside that bound is a conformance failure independent of any actual ray tracing work.

## Registration Hierarchy

```text
ray_tracing_pipeline.limits
├── accel_struct_props
└── ray_tracing_props
```

The two direct children are registered by [createLimitsTests](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L277-L285). Each child is one `RayTracingLimitsTest` instance parameterized by a `PropertyType` value. The dispatcher at [vktRayTracingTests.cpp#L101](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L101) adds the `limits` group as a child of the `ray_tracing_pipeline` test category. Both leaves appear in the mustpass at [ray-tracing-pipeline.txt#L12609-L12610](../../../mustpass/main/vk-default/ray-tracing-pipeline.txt#L12609-L12610).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Property family (test case leaf) | `accel_struct_props`, `ray_tracing_props` | Selects which property struct's fields are validated. This is the primary behavioral axis. | [createLimitsTests](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L281-L282) |
| Iteration count | random integer in `[1, 20]` | Each iteration re-fetches the property structs and re-runs every field check, so a single test case exercises the query path repeatedly. | [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L107) |
| Random seed | `1234` (fixed) | The `de::Random` instance is constructed with seed `1234`, so the iteration count sequence is deterministic across runs. | [RayTracingLimitsTestInstance constructor](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L92-L97) |

## Behavior Parameters

The primary behavioral axis is the property family, which is the test case leaf. The two leaves each validate a different property struct's fields against spec-required bounds.

### accel_struct_props — acceleration-structure property bounds

Validates eight fields of `VkPhysicalDeviceAccelerationStructurePropertiesKHR` retrieved through the `RayTracingProperties` wrapper. The bounds checked are:

- `maxGeometryCount` in `[2^24 - 1, UINT32_MAX]`
- `maxInstanceCount` in `[2^24 - 1, UINT32_MAX]`
- `maxPrimitiveCount` in `[2^29 - 1, UINT32_MAX]`
- `maxPerStageDescriptorAccelerationStructures >= 16`
- `maxPerStageDescriptorUpdateAfterBindAccelerationStructures >= 500000`
- `maxDescriptorSetAccelerationStructures >= 16`
- `maxDescriptorSetUpdateAfterBindAccelerationStructures >= 500000`
- `minAccelerationStructureScratchOffsetAlignment <= 256`

A failure of any one field returns `TestStatus::fail` with a message naming that field. Requires `VK_KHR_acceleration_structure` ([checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L71-L78)).

### ray_tracing_props — ray-tracing-pipeline property bounds

Validates eight fields of `VkPhysicalDeviceRayTracingPipelinePropertiesKHR`. The bounds checked are:

- `shaderGroupHandleSize == 32`
- `maxRayRecursionDepth >= 1`
- `maxShaderGroupStride >= 4096`
- `shaderGroupBaseAlignment <= 64`
- `shaderGroupHandleCaptureReplaySize <= 64`
- `maxRayDispatchInvocationCount >= 2^30`
- `shaderGroupHandleAlignment <= 32`
- `maxRayHitAttributeSize >= 32`

A failure of any one field returns `TestStatus::fail` with a message naming that field. Requires `VK_KHR_ray_tracing_pipeline` ([checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L71-L78)).

## Shader Analysis

Shader code is not part of the tested behavior. The test never builds a pipeline, dispatches rays, or loads a shader. It only queries device property structs on the host and compares the reported fields against spec-required bounds. No representative shader walkthrough is needed.

## Runtime Execution and Result Checking

- **Property fetch.** Each iteration calls `makeRayTracingProperties(vki, physicalDevice)`, which constructs a `RayTracingPropertiesKHR` that fetches `VkPhysicalDeviceAccelerationStructurePropertiesKHR` and `VkPhysicalDeviceRayTracingPipelinePropertiesKHR` through separate `vkGetPhysicalDeviceProperties2` calls, each chaining one struct via `pNext` ([iterate](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L103-L113)).
- **Per-field range check.** Depending on `m_propType`, the iteration walks the relevant block of range checks. Each check reads one getter, compares it against a hard-coded constant, and returns `TestStatus::fail` with a field-specific message on the first violation ([accel_struct block](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L115-L195), [ray_tracing block](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L197-L264)).
- **Iteration loop.** A `de::Random(1234)` instance picks a random iteration count in `[1, 20]`. The property fetch and all field checks run again on every iteration. The loop returns pass only if every iteration completes without a range violation ([iterate loop](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L107-L265)).
- **Pass condition.** `TestStatus::pass("Pass")` is returned after the iteration loop completes without an early fail ([final return](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L267)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `accel_struct_props` | One of the eight `VkPhysicalDeviceAccelerationStructurePropertiesKHR` fields is reported outside the spec-required bound. |
| `ray_tracing_props` | One of the eight `VkPhysicalDeviceRayTracingPipelinePropertiesKHR` fields is reported outside the spec-required bound. |

Both leaves share the property-fetch helper and the per-iteration loop. A failure message naming a field that does not belong to the failing leaf's struct would point at the wrapper or the test's own field mapping rather than a driver property report.

### Cause Analysis

#### Property reported outside spec-required bound

**Possible failure symptoms:** The failing leaf's `TestStatus::fail` message names one specific property field (for example, "Property maxGeometryCount is not within supported limits"). The test returns fail on the first violated field, so only one field is named even if multiple fields are out of range.

**Possible implementation causes:** The Vulkan spec fixes required minimum or maximum values for each field this test checks. A failure means the implementation reported a value outside that required range through `vkGetPhysicalDeviceProperties2`. Grounded investigation should confirm the bound the test encodes matches the current `VK_KHR_acceleration_structure` or `VK_KHR_ray_tracing_pipeline` specification chapter, then check whether the driver's property report matches what the implementation actually enforces. A driver that reports a stricter value than the spec requires but still accepts work beyond that stricter value would have a reporting bug rather than a functional bug. A value that violates the spec minimum (for example, `maxRayRecursionDepth == 0`) would mean the implementation does not conform to the extension's property contract. Source-level investigation of the driver's property query path is needed to confirm which field is wrong and why.

## Case Pruning

### Requirement-based pruning

- `accel_struct_props` requires `VK_KHR_acceleration_structure` device functionality; `ray_tracing_props` requires `VK_KHR_ray_tracing_pipeline` device functionality. Each leaf's `checkSupport` calls `context.requireDeviceFunctionality` for its own extension and skips the case if the extension is absent ([checkSupport](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L71-L78)).

### Design-based pruning

- No parameter matrix is generated. The two leaves are a fixed set with no generated variants. The random iteration count only affects how many times the same property fetch and range-check sequence runs; it does not vary what is being tested.
- The test does not exercise actual acceleration-structure builds, ray tracing pipelines, or ray dispatches. It only checks reported property values, so no resource, format, or limit requirements beyond the two KHR extensions apply.

## Key Takeaways

- The `limits` test family verifies that reported `VkPhysicalDeviceAccelerationStructurePropertiesKHR` and `VkPhysicalDeviceRayTracingPipelinePropertiesKHR` fields fall within the spec-required bounds. It is a pure property-query test with no shader, pipeline, or ray dispatch work.
- The primary behavioral axis is the property family. `accel_struct_props` validates eight acceleration-structure property fields; `ray_tracing_props` validates eight ray-tracing-pipeline property fields. Both leaves use the same fetch-and-range-check mechanism.
- A failure names one specific field and means the implementation reported a value outside the spec-required range for that field. See `## Failure Meaning` for the per-cause analysis.
- The random iteration count and fixed seed only affect how many times the same check sequence runs; they do not change what is being tested.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `PropertyType` enum | [vktRayTracingLimitsTests.cpp#L42-L46](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L42-L46) | Selects which property struct's fields are validated |
| `RayTracingLimitsTest::checkSupport` | [vktRayTracingLimitsTests.cpp#L71-L78](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L71-L78) | Per-leaf KHR extension requirement gate |
| `RayTracingLimitsTestInstance::iterate` | [vktRayTracingLimitsTests.cpp#L103-L268](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L103-L268) | Property fetch, per-field range checks, and pass/fail condition |
| accel_struct range checks | [vktRayTracingLimitsTests.cpp#L115-L195](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L115-L195) | The eight `VkPhysicalDeviceAccelerationStructurePropertiesKHR` field bounds |
| ray_tracing range checks | [vktRayTracingLimitsTests.cpp#L197-L264](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L197-L264) | The eight `VkPhysicalDeviceRayTracingPipelinePropertiesKHR` field bounds |
| `createLimitsTests` | [vktRayTracingLimitsTests.cpp#L277-L285](../../../modules/vulkan/ray_tracing/vktRayTracingLimitsTests.cpp#L277-L285) | Registration of the `limits` group and its two leaves |
| Category dispatcher | [vktRayTracingTests.cpp#L101](../../../modules/vulkan/ray_tracing/vktRayTracingTests.cpp#L101) | `createLimitsTests` is added to the `ray_tracing_pipeline` test category |
| `makeRayTracingProperties` | [vkRayTracingUtil.cpp#L5045-L5049](../../../framework/vulkan/vkRayTracingUtil.cpp#L5045-L5049) | Wrapper that fetches both ray-tracing property structs in its constructor |
| Mustpass evidence | [ray-tracing-pipeline.txt#L12609-L12610](../../../mustpass/main/vk-default/ray-tracing-pipeline.txt#L12609-L12610) | Both `limits.*` leaves listed in the default ray-tracing-pipeline mustpass |
