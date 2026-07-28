## Overview

**Core question:** For every core Vulkan format, does the implementation's `VkFormatProperties3` (reported through `VK_KHR_format_feature_flags2`) contain at least the feature bits that CTS derives as required for that format?

- Covers the `api.format_feature_flags2` test family implemented in [`vktApiFormatPropertiesExtendedKHRtests.cpp`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L1) and attached to the `api` test category by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L125-L125) inside `#ifndef CTS_USES_VULKANSC`.
- The family registers one test case leaf per core Vulkan format: 184 leaves total, named as the lowercase format name with the `VK_FORMAT_` prefix stripped, e.g. `r4g4_unorm_pack8` and `x8_d24_unorm_pack32` [`createTestCases()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L73-L80), [api.txt](../../../mustpass/main/vk-default/api.txt#L271425-L271608).
- Each leaf reads the implementation-reported `VkFormatProperties3` for its format, computes the CTS-required `VkFormatProperties3`, and verifies the reported flags are a superset of the required flags for `bufferFeatures`, `linearTilingFeatures`, and `optimalTilingFeatures` [`test()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L59-L70).
- The family is host-side property validation only: it queries physical-device format properties and compares bit masks on the host. No pipeline, dispatch, draw, shader, or device-side resource is involved.
- Passing means every required feature bit for the leaf's format is present in the corresponding reported feature set. Each leaf produces its own pass/fail result.

## Background Knowledge

- `VK_KHR_format_feature_flags2` exposes format feature flags as 64-bit `VkFlags64` values through the `VkFormatProperties3` structure, chained into `VkFormatProperties2::pNext` and queried via `vkGetPhysicalDeviceFormatProperties2`. The extension was promoted to Vulkan 1.3 core. The `VkFormatProperties3` fields `linearTilingFeatures`, `optimalTilingFeatures`, and `bufferFeatures` use the `VK_FORMAT_FEATURE_2_*` bit names, which are a wider 64-bit superset of the legacy 32-bit `VkFormatFeatureFlagBits` values exposed by `vkGetPhysicalDeviceFormatProperties`.
- `vkGetPhysicalDeviceFormatProperties` (Vulkan 1.0) returns the same per-format capability information in 32-bit `VkFormatProperties` fields. CTS uses this legacy query as the baseline for computing the required `VkFormatProperties3` bits, then augments that baseline with spec-derived implications to obtain the CTS-required feature mask that the implementation's `VkFormatProperties3` must be a superset of.
- `VK_KHR_get_physical_device_properties2` provides the `vkGetPhysicalDeviceFormatProperties2` entry point used to chain `VkFormatProperties3` into the query. The CTS support gate refers to it by name even when the implementation exposes the entry point through Vulkan 1.1+ core promotion.
- The `VkFormatProperties3` feature sets describe capability per resource shape: `bufferFeatures` applies to buffer views and texel buffers, `linearTilingFeatures` to linear-tiled images, and `optimalTilingFeatures` to optimal-tiled images. Each set is validated independently per format.

## Registration Hierarchy

```text
api.format_feature_flags2
```

The test family is created by [`createFormatPropertiesExtendedKHRTests()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93), which installs a callback that registers leaf cases directly through `addFunctionCase()` in [`createTestCases()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L73-L80). The family has no intermediate nodes: every child of `format_feature_flags2` is a test case leaf named after one core Vulkan format. The 184 leaves are listed in the canonical mustpass from [`api.txt#L271425`](../../../mustpass/main/vk-default/api.txt#L271425) through [`api.txt#L271608`](../../../mustpass/main/vk-default/api.txt#L271608); the alphabetically first leaf is `a1r5g5b5_unorm_pack16` and the last is `x8_d24_unorm_pack32`. The full leaf range is described in `## Parameter Dimensions and Observed Values` rather than enumerated in the tree.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | 184 leaves, one per core Vulkan format from `VK_FORMAT_R4G4_UNORM_PACK8` up to but not including `VK_CORE_FORMAT_LAST` | Selects which Vulkan core format's `VkFormatProperties3` is validated. Every leaf runs the identical superset check; only the input format and the CTS-derived required bits differ. | [`createTestCases()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L73-L80), [api.txt](../../../mustpass/main/vk-default/api.txt#L271425-L271608) |
| Leaf name derivation | Lowercase `getFormatName(format)` with the leading `VK_FORMAT_` (10 characters) stripped | Each leaf is named after its format, e.g. `r4g4_unorm_pack8`, `b8g8r8a8_unorm`, `d32_sfloat_s8_uint`, `bc1_rgb_unorm_block`, `astc_4x4_srgb_block`. | [`createTestCases()` name derivation](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L78-L78) |
| Feature set checked | `bufferFeatures`, `linearTilingFeatures`, `optimalTilingFeatures` | Each leaf validates all three feature sets of `VkFormatProperties3` in a fixed order. The three sets are independent: a failure in one does not short-circuit the others within the same leaf. | [`test()` feature-set loop](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L64-L68) |
| Reported-flags source | Implementation-reported `VkFormatProperties3` returned by `Context::getFormatProperties()` via `vkGetPhysicalDeviceFormatProperties2` with `VkFormatProperties3` chained through `pNext` | The values being checked. The support gate guarantees `VK_KHR_format_feature_flags2` is present, so the chained-struct path is taken. | [`vktTestCase.cpp getFormatProperties()`](../../../modules/vulkan/vktTestCase.cpp#L1671-L1688) |
| Required-flags source | CTS-derived `VkFormatProperties3` returned by `Context::getRequiredFormatProperties()` | Built from the legacy `VkFormatProperties` plus spec-derived implications: depth formats with `SAMPLED_IMAGE_BIT` also require `SAMPLED_IMAGE_DEPTH_COMPARISON_BIT`; extended storage formats with `shaderStorageImageReadWithoutFormat` / `shaderStorageImageWriteWithoutFormat` require the corresponding `STORAGE_READ_WITHOUT_FORMAT_BIT` / `STORAGE_WRITE_WITHOUT_FORMAT_BIT`; non-SPIR-V-compatible formats exposing `*_WITHOUT_FORMAT` storage bits must also expose `STORAGE_IMAGE_BIT` or `STORAGE_TEXEL_BUFFER_BIT`. | [`vktTestCase.cpp getRequiredFormatProperties()`](../../../modules/vulkan/vktTestCase.cpp#L1616-L1669) |
| Required extensions | `VK_KHR_format_feature_flags2`, `VK_KHR_get_physical_device_properties2` | Both are checked in `checkSupport()` before the leaf runs. Either being absent causes the leaf to be skipped. | [`checkSupport()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L39-L44) |

## Behavior Parameters

The primary behavioral axis is the test case leaf: each leaf selects one core Vulkan format and runs the same three-feature-set superset check against the implementation's `VkFormatProperties3`. Because every leaf applies the identical validation rule, leaves vary only in which required feature bits the CTS-side `getRequiredFormatProperties` derives for that format's category.

The behavior splits into the following format-category-driven required-bit implications. The check itself does not branch on these categories; they describe which required bits get added on top of the legacy `VkFormatProperties` baseline before the superset comparison.

### Standard color and packed formats: basic superset check

For typical color and packed formats (for example `r8g8b8a8_unorm`, `b8g8r8a8_srgb`, `r4g4_unorm_pack8`, `a1r5g5b5_unorm_pack16`), `getRequiredFormatProperties` returns the legacy `VkFormatProperties` bits reinterpreted as `VK_FORMAT_FEATURE_2_*` bits. The leaf checks that the implementation's reported `VkFormatProperties3` for each of the three feature sets is a superset of those legacy-derived bits.

### Depth/stencil formats: additional `SAMPLED_IMAGE_DEPTH_COMPARISON_BIT` requirement

For depth/stencil formats (for example `d16_unorm`, `d32_sfloat`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint`), `getRequiredFormatProperties` adds `VK_FORMAT_FEATURE_2_SAMPLED_IMAGE_DEPTH_COMPARISON_BIT_KHR` to `linearTilingFeatures` and `optimalTilingFeatures` whenever the legacy query reported `VK_FORMAT_FEATURE_2_SAMPLED_IMAGE_BIT_KHR` for that tiling. The leaf therefore requires the implementation to also report the depth-comparison bit on top of the basic sampled-image bit for these formats [`vktTestCase.cpp#L1663-L1666`](../../../modules/vulkan/vktTestCase.cpp#L1663-L1666).

### Extended storage formats: `*_WITHOUT_FORMAT` storage bit requirements

For extended storage formats when the device exposes `shaderStorageImageReadWithoutFormat` or `shaderStorageImageWriteWithoutFormat`, `getRequiredFormatProperties` adds `VK_FORMAT_FEATURE_2_STORAGE_READ_WITHOUT_FORMAT_BIT_KHR` and/or `VK_FORMAT_FEATURE_2_STORAGE_WRITE_WITHOUT_FORMAT_BIT_KHR` to the linear and optimal tiling features whenever the format already exposes `STORAGE_IMAGE_BIT`. The leaf therefore requires the implementation to also report the corresponding without-format storage bit for these formats and tilings [`vktTestCase.cpp#L1629-L1642`](../../../modules/vulkan/vktTestCase.cpp#L1629-L1642).

### Non-SPIR-V-compatible formats: storage image and texel buffer implication

For formats that are not in the SPIR-V compatibility table, `getRequiredFormatProperties` adds `VK_FORMAT_FEATURE_2_STORAGE_IMAGE_BIT_KHR` (for linear and optimal tiling) and `VK_FORMAT_FEATURE_2_STORAGE_TEXEL_BUFFER_BIT_KHR` (for buffer features) when the implementation already exposes `STORAGE_READ_WITHOUT_FORMAT_BIT` or `STORAGE_WRITE_WITHOUT_FORMAT_BIT` for that path. The leaf therefore requires the implementation to also report the underlying storage image or texel buffer bit whenever it reports a without-format storage bit for a non-SPIR-V-compatible format [`vktTestCase.cpp#L1645-L1662`](../../../modules/vulkan/vktTestCase.cpp#L1645-L1662).

## Shader Analysis

No shader is involved in this test family. Every leaf performs host-side physical-device format-property queries and bit-mask comparisons; no pipeline, dispatch, draw, descriptor, or device-side resource is used.

## Runtime Execution and Result Checking

Each leaf runs the same host-side sequence inside [`test()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L59-L70):

1. Acquire the implementation-reported `VkFormatProperties3` for the leaf's format via [`Context::getFormatProperties()`](../../../modules/vulkan/vktTestCase.cpp#L1671-L1688). Because the support gate already required `VK_KHR_format_feature_flags2`, the implementation's chained-struct query is used: `VkFormatProperties3` is chained into `VkFormatProperties2::pNext` and populated by `vkGetPhysicalDeviceFormatProperties2`.
2. Acquire the CTS-required `VkFormatProperties3` for the same format via [`Context::getRequiredFormatProperties()`](../../../modules/vulkan/vktTestCase.cpp#L1616-L1669). This call issues the legacy `vkGetPhysicalDeviceFormatProperties` query, reinterprets the 32-bit feature flags as 64-bit `VK_FORMAT_FEATURE_2_*` bits, and applies the spec-derived implications described in `## Behavior Parameters`.
3. Validate `bufferFeatures`, `linearTilingFeatures`, and `optimalTilingFeatures` in that fixed order through [`checkFlags()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57). Each call computes `(reportedFlags & requestedFlags)`, compares the result to `requestedFlags`, and on mismatch computes the missing mask as `andMask ^ requestedFlags`.
4. On any mismatch, format a failure message as `"<setName>: missing flags 0x<16-hex-digits>"` where `<setName>` is `"Buffer features"`, `"Linear tiling features"`, or `"Optimal tiling features"`, then call `TCU_FAIL(msg.str())` to terminate the leaf with a failed status and that message [`checkFlags()` diagnostic](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L51-L55).
5. Return `tcu::TestStatus::pass("Pass")` when all three feature-set checks succeed [pass return](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L70-L70).

The three checks within one leaf are independent in the sense that each computes its own missing mask, but `TCU_FAIL` aborts on the first failing set, so only the first failing feature set's missing mask appears in the diagnostic for that leaf.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Standard color and packed formats | Implementation's `VkFormatProperties3` for the format is missing one or more `VK_FORMAT_FEATURE_2_*` bits that the legacy `VkFormatProperties` query reported for that format. |
| Depth/stencil formats | Implementation reports `SAMPLED_IMAGE_BIT` for the format's tiling but does not report `SAMPLED_IMAGE_DEPTH_COMPARISON_BIT` for the same tiling. |
| Extended storage formats | Implementation exposes `STORAGE_IMAGE_BIT` for the format's tiling and the device exposes `shaderStorageImageReadWithoutFormat` or `shaderStorageImageWriteWithoutFormat`, but the implementation does not report the corresponding `STORAGE_READ_WITHOUT_FORMAT_BIT` or `STORAGE_WRITE_WITHOUT_FORMAT_BIT` for that tiling. |
| Non-SPIR-V-compatible formats | Implementation exposes `STORAGE_READ_WITHOUT_FORMAT_BIT` or `STORAGE_WRITE_WITHOUT_FORMAT_BIT` for a non-SPIR-V-compatible format without also exposing the underlying `STORAGE_IMAGE_BIT` (tiling) or `STORAGE_TEXEL_BUFFER_BIT` (buffer) bit. |
| Any leaf | A common infrastructure cause: the implementation advertises `VK_KHR_format_feature_flags2` but does not populate the chained `VkFormatProperties3` struct on `vkGetPhysicalDeviceFormatProperties2`. |

All leaves share the same superset-check mechanism in [`checkFlags()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57); the difference across the rows above is which required bit is missing, not how the missing bits are detected. The reported missing mask in the diagnostic identifies the affected feature set (`Buffer features`, `Linear tiling features`, or `Optimal tiling features`) and the exact missing `VK_FORMAT_FEATURE_2_*` bits.

### Cause Analysis

#### Reported `VkFormatProperties3` is missing a legacy-derived feature bit

**Possible failure symptoms:** [`checkFlags()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57) computes a non-zero `missingBits` for one of the three feature sets and the leaf terminates with a `TCU_FAIL` message of the form `"<setName>: missing flags 0x<16-hex-digits>"`. The reported missing mask corresponds to bits that exist in the legacy `VkFormatProperties` for the same format but are absent from the implementation's `VkFormatProperties3`.

**Possible implementation causes:** the implementation's `VkFormatProperties3` reporting path diverges from its legacy `VkFormatProperties` reporting path for the same format. The Vulkan spec requires the 64-bit `VkFormatProperties3` feature bits to be a superset of the corresponding 32-bit `VkFormatProperties` bits, so any bit present in the legacy query but absent from the extended query is non-conformant. The most plausible driver-side cause is that the format capability table backing the `*2` query path is incomplete or maps the format to a different feature set than the table backing the legacy query. Source-level investigation is needed to confirm whether the divergence is in the implementation's table or in the CTS-derived baseline.

#### Depth/stencil format reports `SAMPLED_IMAGE_BIT` without `SAMPLED_IMAGE_DEPTH_COMPARISON_BIT`

**Possible failure symptoms:** [`checkFlags()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57) reports a missing mask whose only set bit is `VK_FORMAT_FEATURE_2_SAMPLED_IMAGE_DEPTH_COMPARISON_BIT_KHR` for `linearTilingFeatures` or `optimalTilingFeatures` of a depth or depth/stencil format. The leaf fails with the corresponding `"<setName>: missing flags 0x..."` message.

**Possible implementation causes:** the implementation's format table reports the depth-comparison capability separately from the sampled-image capability and the depth-comparison bit was not set for this format. The Vulkan spec requires that depth/stencil formats supporting sampling also support depth comparison through `SAMPLED_IMAGE_DEPTH_COMPARISON_BIT`, so an implementation that reports `SAMPLED_IMAGE_BIT` without `SAMPLED_IMAGE_DEPTH_COMPARISON_BIT` for a depth format is non-conformant. Source-level investigation is needed to confirm whether the implementation's table is missing the depth-comparison bit entry for this specific format.

#### Extended storage format missing `STORAGE_READ_WITHOUT_FORMAT_BIT` or `STORAGE_WRITE_WITHOUT_FORMAT_BIT`

**Possible failure symptoms:** [`checkFlags()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57) reports a missing mask containing `VK_FORMAT_FEATURE_2_STORAGE_READ_WITHOUT_FORMAT_BIT_KHR` and/or `VK_FORMAT_FEATURE_2_STORAGE_WRITE_WITHOUT_FORMAT_BIT_KHR` for `linearTilingFeatures` or `optimalTilingFeatures` of a format identified as an extended storage format, when the device exposes the corresponding `shaderStorageImageReadWithoutFormat` or `shaderStorageImageWriteWithoutFormat` feature.

**Possible implementation causes:** the implementation exposes `STORAGE_IMAGE_BIT` for the format and exposes the relevant without-format storage feature, but its `VkFormatProperties3` table does not also set the corresponding without-format storage bit. The Vulkan spec requires that when a storage-image-capable format is used on a device with `shaderStorageImageReadWithoutFormat` or `shaderStorageImageWriteWithoutFormat`, the without-format storage bits be reported for that format's tiling. An implementation that omits the without-format bit under these conditions is non-conformant. Source-level investigation is needed to determine whether the omission is in the format table or in the feature-implication logic.

#### Non-SPIR-V-compatible format exposes `*_WITHOUT_FORMAT` storage bit without underlying storage bit

**Possible failure symptoms:** [`checkFlags()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57) reports a missing mask containing `VK_FORMAT_FEATURE_2_STORAGE_IMAGE_BIT_KHR` (for tiling) or `VK_FORMAT_FEATURE_2_STORAGE_TEXEL_BUFFER_BIT_KHR` (for buffer features) for a format that is not in the SPIR-V compatibility table, when the implementation already reports `STORAGE_READ_WITHOUT_FORMAT_BIT` or `STORAGE_WRITE_WITHOUT_FORMAT_BIT` for that path.

**Possible implementation causes:** the implementation reports a without-format storage bit for a format whose component layout is not compatible with the SPIR-V image format layout rules, but does not also report the underlying `STORAGE_IMAGE_BIT` or `STORAGE_TEXEL_BUFFER_BIT`. The Vulkan spec requires that such formats expose the underlying storage bit whenever they expose a without-format storage bit, because without-format access is the only spec-legal way to read or write such formats from storage images or texel buffers. An implementation that reports the without-format bit without the underlying storage bit is non-conformant. Source-level investigation is needed to confirm whether the implementation's table is missing the underlying storage bit entry.

#### Shared infrastructure failure: extension advertised but `VkFormatProperties3` not populated

**Possible failure symptoms:** [`checkFlags()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57) reports a missing mask equal to the entire required feature set, because the chained `VkFormatProperties3` returned by the implementation is zero or contains only a few bits, while the CTS-derived required mask is non-zero. The leaf fails on the first feature set with a near-full missing mask.

**Possible implementation causes:** the implementation advertises `VK_KHR_format_feature_flags2` (or Vulkan 1.3+) but does not populate the chained `VkFormatProperties3` struct on `vkGetPhysicalDeviceFormatProperties2`, or populates it from a different code path than the legacy `VkFormatProperties` query. This is a clear driver-side defect. The inspected test code does not perform sentinel-byte verification of the chained struct, so this cause would surface as a large missing mask in the diagnostic rather than as a dedicated sentinel check.

## Case Pruning

### Requirement-based pruning

- All 184 leaves are registered only for non-VulkanSC builds: the parent `addChild(createFormatPropertiesExtendedKHRTests(testCtx))` call is wrapped in `#ifndef CTS_USES_VULKANSC` in [`vktApiTests.cpp#L123-L126`](../../../modules/vulkan/api/vktApiTests.cpp#L123-L126). The Vulkan SC profile does not include this test family.
- [`checkSupport()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L39-L44) requires both `VK_KHR_format_feature_flags2` (device functionality) and `VK_KHR_get_physical_device_properties2` (instance functionality). Implementations that do not expose either extension skip every leaf in this family before any property query runs.
- No device features, queue-family capabilities, or device limits are checked. The test only requires the two extensions and the physical-device format-property query entry points they expose.

### Design-based pruning

- The format enumeration range is exactly the core Vulkan format enum interval `VK_FORMAT_R4G4_UNORM_PACK8` to `VK_CORE_FORMAT_LAST` exclusive [`createTestCases()` format loop](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L75-L76). YCbCr formats and extension-defined formats outside this interval are not generated as leaves in this family.
- The test only verifies that required bits are present; the inspected code does not check whether extra reported bits should be absent. A format that reports additional `VK_FORMAT_FEATURE_2_*` bits beyond the CTS-derived required mask still passes.
- The test does not vary tiling, image type, image usage, or `pNext` chain combinations. Those variations are exercised by the `api.info` family's `pnext_format_properties` and `image_format_properties` intermediate nodes, not by this family.
- The test does not re-query the legacy `VkFormatProperties` independently; it relies on `Context::getRequiredFormatProperties()` to issue that query internally and to apply the spec-derived implications. The implementation-reported and CTS-required queries both run inside the same leaf.

## Key Takeaways

- The `api.format_feature_flags2` family is a host-side property-validation family; it does not execute any device-side work beyond the physical-device format-property query.
- All 184 leaves share the identical superset-check mechanism in [`checkFlags()`](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57); they differ only in which Vulkan core format's `VkFormatProperties3` is being validated and which required bits `Context::getRequiredFormatProperties()` derives for that format.
- The CTS-required mask adds spec-derived implications on top of the legacy `VkFormatProperties` bits reinterpreted as 64-bit values: depth/stencil formats, extended storage formats with `shaderStorageImageRead/WriteWithoutFormat`, and non-SPIR-V-compatible formats exposing `*_WITHOUT_FORMAT` storage bits. See `## Behavior Parameters` for the category-by-category breakdown.
- The superset check is one-directional: missing required bits fail the leaf, but extra reported bits are not flagged. The diagnostic message names the affected feature set and prints the exact missing mask in 16-digit hexadecimal, which is enough to identify which `VK_FORMAT_FEATURE_2_*` bits the implementation failed to report.
- See `## Failure Meaning` for the case-by-case analysis of what each missing-bit pattern implies about the implementation's format-capability table.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createFormatPropertiesExtendedKHRTests()` | [vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L90-L93) | Public entry point that creates the `format_feature_flags2` test family. |
| `createTestCases()` | [vktApiFormatPropertiesExtendedKHRtests.cpp#L73-L80](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L73-L80) | Iterates the core Vulkan format enum and registers one leaf per format. |
| `checkSupport()` | [vktApiFormatPropertiesExtendedKHRtests.cpp#L39-L44](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L39-L44) | Shared support gate requiring `VK_KHR_format_feature_flags2` and `VK_KHR_get_physical_device_properties2`. |
| `test()` | [vktApiFormatPropertiesExtendedKHRtests.cpp#L59-L70](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L59-L70) | Per-leaf host-side flow: acquire reported and required `VkFormatProperties3`, validate the three feature sets. |
| `checkFlags()` | [vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.cpp#L46-L57) | Per-feature-set superset check; computes and prints the missing mask on failure. |
| Parent registration | [vktApiTests.cpp#L125-L125](../../../modules/vulkan/api/vktApiTests.cpp#L125-L125) | Where the `format_feature_flags2` group is attached to the `api` test category inside `#ifndef CTS_USES_VULKANSC`. |
| Header | [vktApiFormatPropertiesExtendedKHRtests.hpp](../../../modules/vulkan/api/vktApiFormatPropertiesExtendedKHRtests.hpp) | Public declaration of `createFormatPropertiesExtendedKHRTests()`. |
| `Context::getFormatProperties()` | [vktTestCase.cpp#L1671-L1688](../../../modules/vulkan/vktTestCase.cpp#L1671-L1688) | Returns the implementation-reported `VkFormatProperties3` via the chained `VkFormatProperties2` query. |
| `Context::getRequiredFormatProperties()` | [vktTestCase.cpp#L1616-L1669](../../../modules/vulkan/vktTestCase.cpp#L1616-L1669) | Builds the CTS-required `VkFormatProperties3` from the legacy query plus spec-derived implications. |
| Mustpass entries | [api.txt#L271425-L271608](../../../mustpass/main/vk-default/api.txt#L271425-L271608) | The 184 `dEQP-VK.api.format_feature_flags2.*` leaves in the canonical `api` mustpass. |
