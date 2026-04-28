# Maintenance7 Query Tests

Tests for maintenance7-specific timestamp query wrapping behavior under `query_pool`. This page documents the `maintenance7` Level-3 group registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:50) and implemented in [`vktQueryMaintenance7Tests.cpp`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp).

## Source

- [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- [`vktQueryMaintenance7Tests.cpp`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp)
- [`vktQueryMaintenance7Tests.hpp`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.hpp)

## Registration

| Item | Value |
|------|-------|
| Top-level parent | `query_pool` via [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:59) |
| Level-3 group name | `maintenance7` via [`createQueryMaintenance7Tests()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:228) |
| Child registration | [`queryPoolTests->addChild(createQueryMaintenance7Tests(testCtx))`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:50) |
| Group population | [`createQueryMaintenance7Tests()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:228) |
| Vulkan SC split | Registered only when `CTS_USES_VULKANSC` is not defined because both the parent add-child call and the whole implementation are guarded by [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:48) and [`vktQueryMaintenance7Tests.cpp:34`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:34) |

## Summary

The `maintenance7` group is a compact two-case timestamp-query suite that verifies how 32-bit query results relate to corresponding 64-bit results when `VK_KHR_maintenance7` is available. Both cases record a single timestamp query, read it back as both 32-bit and 64-bit values, and then check whether the implementation follows the wrapping rule mandated when maintenance7 is enabled or the pre-maintenance7 behavior permitted when it is not enabled.

## Test Hierarchy

```text
query_pool
└── maintenance7
    ├── query_32b_wrap_required
    └── query_32b_wrap_notrequired
```

The two leaf registrations are the only children added in [`createQueryMaintenance7Tests()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:234).

## Registered Families

### `query_32b_wrap_required`

This case is created by [`new Maintenance7QueryFeatureTestCase(testCtx, "query_32b_wrap_required", true)`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:234).

Its `maint7Enabled` parameter is `true`, which means:

- the device-capability setup requests [`VkPhysicalDeviceMaintenance7FeaturesKHR`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:215);
- runtime support checking requires the `maintenance7` feature bit to be enabled in [`Maintenance7QueryFeatureTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:189);
- verification expects the 32-bit result to equal the low 32 bits of the 64-bit result in [`Maintenance7QueryInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:142).

### `query_32b_wrap_notrequired`

This case is created by [`new Maintenance7QueryFeatureTestCase(testCtx, "query_32b_wrap_notrequired", false)`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:235).

Its `maint7Enabled` parameter is `false`, which means:

- the extension is still required, but the maintenance7 feature itself is not requested in [`initDeviceCapabilities()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:210);
- verification allows either low-32-bit wrapping behavior or saturated `0xFFFFFFFF` behavior when the 64-bit value exceeds 32 bits, as implemented in [`Maintenance7QueryInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:157).

## Parameter Dimensions

This file has a deliberately small matrix.

| Dimension | Values | Source |
|-----------|--------|--------|
| Maintenance7 feature enablement | `true`, `false` | The two constructor calls in [`createQueryMaintenance7Tests()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:234) |
| Query type | Fixed: `VK_QUERY_TYPE_TIMESTAMP` | [`VkQueryPoolCreateInfo`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:97) |
| Query count | Fixed: `1` | [`VkQueryPoolCreateInfo`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:102) |
| Pipeline stage written | Fixed: `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT` | [`cmdWriteTimestamp()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:113) |

Unlike the broader `query_pool` files, this page documents only a feature toggle and does not generate deeper subgroup matrices.

## Support Requirements

Support is checked in [`Maintenance7QueryFeatureTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:185).

| Requirement | Needed for | Source |
|------------|------------|--------|
| `VK_KHR_maintenance7` device functionality | Both cases | [`Maintenance7QueryFeatureTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:187) |
| `maintenance7` feature bit | `query_32b_wrap_required` only | [`Maintenance7QueryFeatureTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:189) |
| Universal queue family supports timestamps (`timestampValidBits > 0`) | Both cases | [`Maintenance7QueryFeatureTestCase::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:194) |
| Queue-family `timestampValidBits` in range `36..64` | Both cases during instance setup | [`checkValidBits()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:70) |

### Timestamp valid-bit handling

The implementation further constrains the queue-family timestamp width through these constants:

| Constant | Value | Source |
|----------|-------|--------|
| `MIN_TIMESTAMP_VALID_BITS` | `36` | [`vktQueryMaintenance7Tests.cpp:39`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:39) |
| `MAX_TIMESTAMP_VALID_BITS` | `64` | [`vktQueryMaintenance7Tests.cpp:40`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:40) |

[`checkTimestampsSupported()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:58) reads `timestampValidBits` from the universal queue family, validates that range, and derives a timestamp mask through [`timestampMaskFromValidBits()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:81).

Although the mask is stored in [`m_timestampMask`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:45), the current verification path does not explicitly apply it when comparing results; the test instead compares the 32-bit and 64-bit return values directly.

## Verification Methods

### Command recording

The instance constructor immediately records the timestamp workload in [`Maintenance7QueryInstance::Maintenance7QueryInstance()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:51) by calling [`recordComands()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:87).

That helper performs the following steps:

1. Validate queue timestamp support and valid-bit range.
2. Create a one-slot timestamp query pool.
3. Allocate a transient command pool and one primary command buffer.
4. Record [`cmdResetQueryPool()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:112) and one [`cmdWriteTimestamp()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:113) at top-of-pipe.

### Result retrieval

[`Maintenance7QueryInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:121) submits the recorded command buffer, waits for completion, and then retrieves the same query twice:

| Readback width | API flags | Destination |
|----------------|-----------|-------------|
| 32-bit | `VK_QUERY_RESULT_WAIT_BIT` | `uint32_t tsGet32Bits` |
| 64-bit | `VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT` | `uint64_t tsGet64Bits` |

The two [`vkGetQueryPoolResults()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:135) calls are issued in [`vktQueryMaintenance7Tests.cpp:135`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:135) and [`vktQueryMaintenance7Tests.cpp:137`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:137).

### Pass / fail rules

The comparison rules are split by feature enablement.

#### Maintenance7 enabled: wrapping required

For `query_32b_wrap_required`, the test passes only when:

```text
(tsGet64Bits & 0xFFFFFFFF) == tsGet32Bits
```

This rule is enforced in [`Maintenance7QueryInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:142). Any other relationship fails the case and logs an explanatory message.

#### Maintenance7 not enabled: wrapping not required

For `query_32b_wrap_notrequired`, the test accepts either of two behaviors in [`Maintenance7QueryInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:157):

| Accepted behavior | Condition |
|-------------------|-----------|
| Low-32-bit wrapping | `(tsGet64Bits & 0xFFFFFFFF) == tsGet32Bits` |
| Saturation to max 32-bit value | `tsGet64Bits > 0xFFFFFFFF` and `tsGet32Bits == 0xFFFFFFFF` |

If neither condition is true, the case fails.

## Notes

- The group is extension-specific and intentionally small: it checks one behavioral rule with and without feature enablement rather than creating a larger timestamp-query matrix.
- Both leaf nodes are implemented with the same [`Maintenance7QueryInstance`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:42); only the `maint7Enabled` flag changes support setup and verification criteria.
- The exact registered subgroup names are `query_32b_wrap_required` and `query_32b_wrap_notrequired`; the latter is not spelled `not_required` in the source and should not be normalized.
- The implementation function name is spelled [`recordComands()`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp:87) in the source, and this page preserves source references exactly.
- This page documents only the Level-3 file represented by [`vktQueryMaintenance7Tests.cpp`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp).
