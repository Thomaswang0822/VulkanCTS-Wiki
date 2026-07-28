## Overview

**Core question:** Does the implementation correctly report physical-device features, properties, format capabilities, and promoted-extension state through every Vulkan query path, and do the reported values satisfy spec-required minimums?

- Covers the `api.info` test family implemented in [`vktApiFeatureInfo.cpp`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1) and registered as a direct child of the `api` test category by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L96) via [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639).
- Exercises `vkGetPhysicalDeviceFormatProperties`, `vkGetPhysicalDeviceImageFormatProperties`, `vkGetPhysicalDeviceProperties2` and the related `*2` queries, Vulkan 1.2/1.3/1.4 feature/property consistency, limits validation, Vulkan profile conformance, and subgroup feature-flag consistency.
- The core test idea is query-result consistency: legacy Vulkan 1.0 queries must match their `*2` counterparts, reported values must satisfy spec-required minimums, promoted extensions must be reflected in the corresponding core version, and unsupported usage/feature combinations must not be reported as supported.
- The family is organized as 15 direct intermediate nodes, each covering one query area with its own behavior parameters, validation rule, and failure meaning; the shared validation mechanism (offset-table field-by-field comparison, guard-byte initialization checks, `tcu::ResultCollector` aggregation) underlies every leaf.

## Background Knowledge

This page assumes the reader understands Vulkan physical-device query entrypoints and the relationship between promoted extensions and core API versions.

- **Physical-device query pairs.** Vulkan exposes both `vkGetPhysicalDevice*` (Vulkan 1.0) and `vkGetPhysicalDevice*2` (provided by `VK_KHR_get_physical_device_properties2` and promoted into Vulkan 1.1). The `*2` forms accept a `pNext` chain so callers can request extension-specific structures. The two forms must report identical values for the overlapping fields.
- **Promoted extensions and core feature structs.** Many extensions introduced feature/property structs that were later folded into `VkPhysicalDeviceVulkan11Features`, `VkPhysicalDeviceVulkan12Features`, `VkPhysicalDeviceVulkan13Features`, and `VkPhysicalDeviceVulkan14Features`. When a Vulkan 1.x version advertises a feature bit, the corresponding extension struct must report the same value, and vice versa.
- **Limits and minimums.** The Vulkan spec defines required minimum values for many `VkPhysicalDeviceLimits` fields. A conformant implementation must report values at or above these minimums, or for maxima-style fields such as alignment, within the spec-required range.
- **`pNext` chains and structure initialization.** When a `*2` query walks a `pNext` chain, the driver must initialize every field of every chained structure and leave the trailing guard bytes untouched. CTS validates this by filling structures and trailing guard memory with sentinel patterns before the query and scanning for unchanged guard bytes afterwards.

## Registration Hierarchy

```text
api.info
├── format_properties
├── image_format_properties
├── unsupported_image_usage
├── extension_core_versions
├── get_physical_device_properties2
├── vulkan1p2
├── vulkan1p3
├── vulkan1p4
├── vulkan1p2_limits_validation
├── vulkan1p3_limits_validation
├── vulkan1p4_limits_validation
├── image_format_properties2
├── sparse_image_format_properties2
├── profiles
└── subgroup_features
```

The `info` test family is added to the `api` test category by [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L96) via [`createFeatureInfoTests()`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639), which registers the 15 direct intermediate nodes shown above. The source also registers an `android` subgroup at [`vktApiFeatureInfo.cpp#L8900-L8912`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8900-L8912), but `dEQP-VK.api.info.android` is absent from [`api.txt`](../../../mustpass/main/vk-default/api.txt), so it is excluded from the canonical mustpass tree and is documented only as auxiliary coverage.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Format range | core formats, YCbCr formats, YCbCr extended formats | Iterates `vkGetPhysicalDeviceFormatProperties` and the `*2` image-format queries over the core format range to verify per-format capability reporting. | [`vktApiFeatureInfo.cpp#L4606-L4641`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L4606-L4641), [`vktApiFeatureInfo.cpp#L8681-L8744`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8681-L8744) |
| Image type | `1d`, `2d`, `3d` | Each image-format query is repeated for every image type the spec allows. | [`vktApiFeatureInfo.cpp#L8255-L8266`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8255-L8266) |
| Image tiling | `optimal`, `linear` | Format-feature flags and image-format properties are queried for both tiling modes. | [`vktApiFeatureInfo.cpp#L8314-L8322`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8314-L8322) |
| Image usage | `sampled`, `storage`, `color_attachment`, `depth_stencil_attachment`, `input_attachment`, `fragment_shading_rate_attachment` | Each usage bit is checked against the format features it requires; unsupported combinations must be rejected. | [`vktApiFeatureInfo.cpp#L8279-L8312`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8279-L8312) |
| `pNext` flag combinations | `drm_format_mod_1`, `drm_format_mod_2`, `format_props_3`, `subpass_resolve_query`, and their mixed combinations | Each format under `pnext_format_properties` is queried with each single-flag and combined-flag chain to verify chained-struct initialization and value consistency. | [`vktApiFeatureInfo.cpp#L8689-L8723`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8689-L8723) |
| Vulkan versions | `vulkan1p2`, `vulkan1p3`, `vulkan1p4` | Each version has its own consistency and limits-validation subgroups because the corresponding `VkPhysicalDeviceVulkan*Features` and `VkPhysicalDeviceVulkan*Properties` structures are version-specific. | [`vktApiFeatureInfo.cpp#L8750-L8799`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8750-L8799), [`vktApiFeatureInfo.cpp#L8802-L8881`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802-L8881) |
| Extension-specific limits cases | `general`, `khr_multiview`, `ext_discard_rectangles`, `ext_sample_locations`, `ext_external_memory_host`, `ext_blend_operation_advanced`, `khr_maintenance_3`, `ext_conservative_rasterization`, `ext_descriptor_indexing`, `khr_vertex_attribute_divisor`, `timeline_semaphore`, `ext_line_rasterization`, `khr_line_rasterization`, `robustness2`, plus non-VulkanSC `khr_push_descriptor`, `ext_inline_uniform_block`, `ext_vertex_attribute_divisor`, `nv_mesh_shader`, `ext_transform_feedback`, `fragment_density_map`, `nv_ray_tracing` | Each extension-specific limits case validates the limits structure introduced by that extension against its spec-required minimums. | [`vktApiFeatureInfo.cpp#L8802-L8854`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8802-L8854) |

## Behavior Parameters

The primary behavioral axis is the **intermediate node**: each direct child of `info` exercises a distinct physical-device query area with its own validation rule. The 15 intermediate nodes form the parameter values documented below.

### `format_properties` — `vkGetPhysicalDeviceFormatProperties` per-format checks

For every core, YCbCr, and YCbCr-extended format, the test queries `VkFormatProperties` and checks that reported optimal-tiling and buffer features include the spec-required bits and contain no bits outside the allowed set. `VK_FORMAT_UNDEFINED` must return all-zero properties. Two additional leaves `depth_stencil` and `compressed_formats` verify the mandatory depth/stencil and compressed format support rules.

### `image_format_properties` — `vkGetPhysicalDeviceImageFormatProperties` per-format/type/tiling/usage checks

For every format × image type × tiling × valid usage-flag combination, the test queries image format properties and verifies that required combinations report `VK_SUCCESS` with extent, mip, array-layer, and sample-count values that satisfy spec minimums, and that unsupported combinations report `VK_ERROR_FORMAT_NOT_SUPPORTED` with all output fields zeroed.

### `unsupported_image_usage` — image usage and format-feature consistency

For every format × tiling × usage bit, the test checks that `vkGetPhysicalDeviceImageFormatProperties` reports `VK_ERROR_FORMAT_NOT_SUPPORTED` whenever the format's feature flags do not include the features required by that usage, and reports success otherwise. A mismatch in either direction fails.

### `extension_core_versions` — extension promotion and core-version consistency

Iterates the `extensionRequiredCoreVersion` table and verifies that any extension reported by the implementation as supported is also reflected in the advertised Vulkan core API version. An extension present without the matching core version fails.

### `get_physical_device_properties2` — `*2` query path consistency and `pNext` chain validation

Exercises `vkGetPhysicalDeviceFeatures2`, `vkGetPhysicalDeviceProperties2`, `vkGetPhysicalDeviceFormatProperties2`, `vkGetPhysicalDeviceQueueFamilyProperties2`, and `vkGetPhysicalDeviceMemoryProperties2`. Each direct case verifies that the `*2` result matches the legacy query for the overlapping fields, that `sType` and `pNext` are preserved, and that the `features` subgroup's per-feature leaves verify each individual feature struct. The `pnext_format_properties` subgroup generates per-format × per-flag-combination cases that chain `VkDrmFormatModifierPropertiesListEXT`, `VkDrmFormatModifierPropertiesList2EXT`, `VkFormatProperties3`, and `VkSubpassResolvePerformanceQueryEXT` (singly and in combination) and verify that the chained structures agree with the basic `VkFormatProperties2` query and that the `VkFormatProperties3` extension bits are a superset of the basic bits.

### `vulkan1p2` — Vulkan 1.2 feature/property consistency and feature-bit device-creation influence

Verifies that `VkPhysicalDeviceVulkan11Features` and `VkPhysicalDeviceVulkan12Features` are fully initialized by `vkGetPhysicalDeviceFeatures2`, that they match the corresponding per-extension feature structs (`VkPhysicalDevice16BitStorageFeatures`, `VkPhysicalDeviceMultiviewFeatures`, etc.), and that the corresponding Vulkan 1.2 properties match their per-extension counterparts. The `feature_extensions_consistency` and `property_extensions_consistency` cases verify the promoted-extension to core-feature/property relationship. The `feature_bits_influence` case verifies that device creation behaves correctly when individual Vulkan 1.2 feature bits are enabled.

### `vulkan1p3` — Vulkan 1.3 feature/property consistency and feature-bit device-creation influence

Mirrors `vulkan1p2` for Vulkan 1.3: validates `VkPhysicalDeviceVulkan13Features` and the corresponding properties, checks consistency with `VK_EXT_image_robustness`, `VK_EXT_inline_uniform_block`, `VK_KHR_pipeline_creation_cache_control`, and other Vulkan 1.3-promoted extensions, and exercises device creation with Vulkan 1.3 feature bits.

### `vulkan1p4` — Vulkan 1.4 feature/property consistency and feature-bit device-creation influence

Mirrors `vulkan1p2` and `vulkan1p3` for Vulkan 1.4: validates `VkPhysicalDeviceVulkan14Features` and properties, checks consistency with `VK_KHR_dynamic_rendering_local_read`, `VK_KHR_host_image_copy`, `VK_KHR_index_type_uint8`, `VK_KHR_line_rasterization`, `VK_KHR_maintenance5`, `VK_KHR_maintenance6`, `VK_EXT_pipeline_protected_access`, `VK_KHR_pipeline_robustness`, `VK_KHR_shader_expect_assume`, `VK_KHR_shader_float_controls2`, `VK_KHR_shader_subgroup_rotate`, and `VK_EXT_vertex_attribute_divisor`, and exercises device creation with Vulkan 1.4 feature bits.

### `vulkan1p2_limits_validation` — Vulkan 1.2 limits and extension-specific limits validation

Validates core `VkPhysicalDeviceLimits` and `VkPhysicalDeviceVulkan11Properties` / `VkPhysicalDeviceVulkan12Properties` against the Vulkan 1.2 spec-required minimums and maximums. Extension-specific leaves validate the limits structures introduced by `VK_KHR_multiview`, `VK_EXT_discard_rectangles`, `VK_EXT_sample_locations`, `VK_EXT_external_memory_host`, `VK_EXT_blend_operation_advanced`, `VK_KHR_maintenance_3`, `VK_EXT_conservative_rasterization`, `VK_EXT_descriptor_indexing`, `VK_KHR_vertex_attribute_divisor`, `VK_KHR_timeline_semaphore`, `VK_EXT_line_rasterization`, `VK_KHR_line_rasterization`, and `VK_EXT_robustness2`, plus non-VulkanSC `VK_KHR_push_descriptor`, `VK_EXT_inline_uniform_block`, `VK_EXT_vertex_attribute_divisor`, `VK_NV_mesh_shader`, `VK_EXT_transform_feedback`, `VK_EXT_fragment_density_map`, and `VK_NV_ray_tracing`.

### `vulkan1p3_limits_validation` — Vulkan 1.3 limits validation

Validates `VkPhysicalDeviceVulkan13Properties`-related limits: the `khr_maintenance4` leaf checks `VK_KHR_maintenance4` limits, and `max_inline_uniform_total_size` checks the spec-required minimum for that property.

### `vulkan1p4_limits_validation` — Vulkan 1.4 limits validation

Validates Vulkan 1.4 spec-required minimums (higher image dimensions, larger descriptor set counts, larger framebuffer sizes, etc.) through the `general` leaf.

### `image_format_properties2` — `vkGetPhysicalDeviceImageFormatProperties2` consistency

For every format × image type × tiling × valid usage × create-flag combination, queries both `vkGetPhysicalDeviceImageFormatProperties` and `vkGetPhysicalDeviceImageFormatProperties2` and verifies that the result codes and `VkImageFormatProperties` contents match exactly.

### `sparse_image_format_properties2` — `vkGetPhysicalDeviceSparseImageFormatProperties2` consistency

For every format × image type × sample count × usage × tiling combination, queries both sparse-image-format query entrypoints and verifies that the reported property counts and per-property `VkSparseImageFormatProperties` contents match exactly. Also verifies that devices without the `sparseBinding` feature report zero sparse-image properties.

### `profiles` — Vulkan profile conformance

Iterates `profileEntries` (defined in `vkProfileTests.inl`) and registers one leaf per profile entry, each of which validates that the device satisfies the mandatory features, properties, and limits required by that Vulkan profile.

### `subgroup_features` — subgroup feature-flag consistency

The `flags` leaf verifies that the subgroup partitioned feature bit (`VK_SUBGROUP_FEATURE_PARTITIONED_BIT_EXT`) is reported in `VkPhysicalDeviceVulkan11Properties::subgroupSupportedOperations` whenever `VkPhysicalDeviceShaderSubgroupPartitionedFeaturesEXT::shaderSubgroupPartitioned` is supported.

## Shader Analysis

No shader is involved in this test family. Every check runs on the host against values returned by physical-device query entrypoints; no pipeline, dispatch, or draw is executed.

## Runtime Execution and Result Checking

- Each test case calls the relevant `vkGetPhysicalDevice*` or `vkGetPhysicalDevice*2` entrypoint on the physical device chosen by the test context. The legacy and `*2` forms are called back-to-back when their results must be compared.
- For property and feature consistency cases, the test pre-fills the destination structures and trailing guard memory with sentinel bytes (`0xCD` or `0xFF * ndx`) before the query and verifies afterwards that every field was overwritten with a valid value and that the guard bytes were not touched. This catches both partial initialization and buffer overruns.
- For property and feature consistency cases, fields are compared field-by-field through offset tables rather than with `memcmp`, because some Vulkan structures contain padding bytes that drivers may or may not write. The offset tables are defined inline next to each validator, for example `feature11OffsetTable` and `feature12OffsetTable` for the Vulkan 1.2 features check.
- For format-property and image-format-property cases, the test uses `tcu::ResultCollector` to accumulate per-field failures (required, allowed, YCbCr, atomic-single-channel, sample-count, extent, mip, array-layer, and `maxResourceSize` checks) and returns the aggregate result.
- For limits-validation cases, the test builds a `FeatureLimitTableItem` table that pairs each spec-required minimum or maximum with the corresponding reported field, then scans the table to find any entry that violates its bound.
- For `feature_bits_influence` cases, the test calls `createTestDevice()` with a `pNext` chain that enables one feature bit at a time and verifies that device creation succeeds or fails according to the reported feature state.
- The final pass/fail condition is the aggregate `tcu::TestStatus` returned by each leaf: `pass` if no `ResultCollector` failure was recorded and no `TCU_FAIL` macro fired, `fail` otherwise. Quality warnings are recorded for non-conformance-quality results that are not hard failures.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `format_properties` | Format-feature flag violation: missing required feature bits, exposing disallowed bits, or non-zero properties for `VK_FORMAT_UNDEFINED`. |
| `image_format_properties` | Image-format property violation: required parameter combination reported as unsupported, unsupported combination reported as successful with non-zeroed output fields, or supported combination with extent/mip/array/sample-count values below spec minimums. |
| `unsupported_image_usage` | Image-usage and format-feature consistency violation: usage reported as supported without the required format features, or reported as unsupported despite the required features being present. |
| `extension_core_versions` | Extension promotion inconsistency: extension reported as supported without the corresponding core API version being advertised. |
| `get_physical_device_properties2` | vk1/vk2 query mismatch, `pNext` chain initialization failure (guard bytes touched or fields left uninitialized), or `VkFormatProperties3` extension bits not a superset of the basic `VkFormatProperties2` bits. |
| `vulkan1p2` | Vulkan 1.2 feature/property initialization failure, mismatch between `VkPhysicalDeviceVulkan11Features` or `VkPhysicalDeviceVulkan12Features` and the corresponding per-extension feature structs, promoted-extension feature/property not reflected in the core struct, or device creation behaves incorrectly with feature bits enabled. |
| `vulkan1p3` | Same class of failures as `vulkan1p2`, applied to `VkPhysicalDeviceVulkan13Features` and Vulkan 1.3-promoted extensions. |
| `vulkan1p4` | Same class of failures as `vulkan1p2`, applied to `VkPhysicalDeviceVulkan14Features` and Vulkan 1.4-promoted extensions. |
| `vulkan1p2_limits_validation` | Reported limit below spec-required minimum, above spec-required maximum, or extension-specific limits structure missing required values. |
| `vulkan1p3_limits_validation` | Reported `max_inline_uniform_total_size` below spec minimum, or `VK_KHR_maintenance4` limits structure violates its spec bounds. |
| `vulkan1p4_limits_validation` | Reported Vulkan 1.4 limit (image dimensions, descriptor counts, framebuffer sizes, etc.) below the Vulkan 1.4 spec-required minimum. |
| `image_format_properties2` | vk1/vk2 image-format query mismatch: different result codes or different `VkImageFormatProperties` contents for the same query parameters. |
| `sparse_image_format_properties2` | vk1/vk2 sparse-image-format query mismatch: different reported property counts, different per-property contents, or non-zero sparse properties reported by a device without the `sparseBinding` feature. |
| `profiles` | Device does not satisfy the mandatory features, properties, or limits required by the named Vulkan profile. |
| `subgroup_features` | Subgroup feature-flag inconsistency: `shaderSubgroupPartitioned` feature reported without the corresponding `VK_SUBGROUP_FEATURE_PARTITIONED_BIT_EXT` operation bit, or vice versa. |

All leaves share a common pass/fail mechanism (`ResultCollector` or direct `TCU_FAIL`), so a mismatch between any two reported values for the same logical field surfaces as a failure of the leaf that performs the comparison.

### Cause Analysis

#### Format-feature flag violation

**Possible failure symptoms:** the `format_properties` leaf reports that a required feature bit is missing from `linearTilingFeatures`, `optimalTilingFeatures`, or `bufferFeatures`, or that an unsupported bit is present, or that `VK_FORMAT_UNDEFINED` returns non-zero properties.

**Possible implementation causes:** the driver's format capability table is missing an entry, maps a format to the wrong feature set, or fails to zero the output structure for `VK_FORMAT_UNDEFINED`. Spec semantics for required format features are defined in the `formats` chapter of the Vulkan spec; an implementation reporting a sampled-image-capable format without `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` or `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` when `VK_KHR_maintenance1` is supported is the most common shape of this failure.

#### Image-format property violation

**Possible failure symptoms:** the `image_format_properties` leaf reports that a required image parameter combination returned `VK_ERROR_FORMAT_NOT_SUPPORTED`, that an unsupported combination returned `VK_SUCCESS`, that returned extent/mip/array/sample-count values are below the spec-required minimums, or that `maxResourceSize` is below the minimum required image resource size.

**Possible implementation causes:** the driver's image-format support table is incomplete or inconsistent with the format-feature flags it reports, the driver clamps reported extents to a device-specific limit below the spec minimum, or the driver fails to zero the output structure when returning `VK_ERROR_FORMAT_NOT_SUPPORTED` as required by the spec.

#### Image-usage and format-feature consistency violation

**Possible failure symptoms:** the `unsupported_image_usage` leaf reports that `vkGetPhysicalDeviceImageFormatProperties` returned `VK_SUCCESS` for a usage whose required format feature is not supported, or returned `VK_ERROR_FORMAT_NOT_SUPPORTED` for a usage whose required feature is supported.

**Possible implementation causes:** the driver's image-format query path does not consult the same feature table used by `vkGetPhysicalDeviceFormatProperties`, or the `VK_FORMAT_FEATURE_2_LINEAR_COLOR_ATTACHMENT_BIT_NV` handling for linear-tiling color attachments diverges from the `VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT` path. Source-level investigation is needed to confirm driver-specific causes for novel usage bits.

#### Extension promotion inconsistency

**Possible failure symptoms:** the `extension_core_versions` leaf reports that an extension is supported but the corresponding core API version is not advertised.

**Possible implementation causes:** the driver exposes a promoted extension without also advertising the core version it was promoted into. The mapping is defined in CTS by the `extensionRequiredCoreVersion` table; an implementation that supports an extension listed as a Vulkan 1.1 promotion without advertising Vulkan 1.1 would fail this check.

#### vk1/vk2 query mismatch and pNext chain initialization failure

**Possible failure symptoms:** the `get_physical_device_properties2` leaves report that the `*2` query returned different values than the legacy query for the same field, that the `sType` or `pNext` fields were modified by the driver, that guard bytes after a chained structure were overwritten, or that `VkFormatProperties3` extension bits do not form a superset of the basic `VkFormatProperties2` bits.

**Possible implementation causes:** the driver's `*2` query path uses a different code path than the legacy query and produces different values for the same logical field, the driver walks the `pNext` chain incorrectly and writes past the end of a chained structure, or the driver fails to initialize every field of every chained structure. The `VkFormatProperties3` superset rule reflects the spec requirement that `VkFormatFeatureFlags2` is a strict superset of `VkFormatFeatureFlags`.

#### Vulkan version feature/property consistency failure

**Possible failure symptoms:** the `vulkan1p2`, `vulkan1p3`, or `vulkan1p4` `features` leaf reports that `VkPhysicalDeviceVulkan11Features` or `VkPhysicalDeviceVulkan12Features` (or the 1.3/1.4 equivalents) was not fully initialized, or that a field disagrees with the corresponding per-extension feature struct; the `feature_extensions_consistency` or `property_extensions_consistency` leaf reports that a promoted extension is supported but its feature/property bit is not set in the core struct, or vice versa; the `feature_bits_influence` leaf reports that device creation behaved incorrectly when a feature bit was enabled.

**Possible implementation causes:** the driver populates the core feature struct from a different source than the extension feature struct and the two diverge, the driver fails to set a core feature bit when the corresponding extension is enabled, or the driver rejects device creation when a reported feature bit is enabled (or accepts it when the bit is not reported). Spec semantics for promoted extensions and core feature structs are defined in the `VK_KHR_get_physical_device_properties2` extension and the Vulkan 1.2, 1.3, and 1.4 core feature chapters.

#### Reported limit outside spec-required bounds

**Possible failure symptoms:** a `vulkan1p*_limits_validation` leaf reports that a `VkPhysicalDeviceLimits`, `VkPhysicalDeviceVulkan11Properties`, `VkPhysicalDeviceVulkan12Properties`, `VkPhysicalDeviceVulkan13Properties`, or extension-specific limits structure field is below the spec-required minimum or above the spec-required maximum.

**Possible implementation causes:** the driver reports a device-specific limit that falls below the spec minimum (for example, `maxImageDimension2D` below 4096 for Vulkan 1.2 or below 8192 for Vulkan 1.4), or reports an alignment value outside the spec-required range. The bounds are defined in the `limits` chapter of the Vulkan spec and in each extension's specification.

#### vk1/vk2 image-format or sparse-image-format query mismatch

**Possible failure symptoms:** the `image_format_properties2` leaf reports different result codes or different `VkImageFormatProperties` contents between `vkGetPhysicalDeviceImageFormatProperties` and `vkGetPhysicalDeviceImageFormatProperties2`; the `sparse_image_format_properties2` leaf reports different property counts, different per-property contents, or non-zero sparse properties on a device without `sparseBinding`.

**Possible implementation causes:** the driver's `*2` query path does not share the same image-format support table as the legacy path, or the sparse-binding feature gate is not consulted by the sparse-image-format query. Spec semantics for image-format queries are defined in the `memory` chapter; the sparse-binding consistency rule is defined in the `sparsememory` chapter.

#### Profile conformance failure

**Possible failure symptoms:** a `profiles` leaf reports that the device does not satisfy the mandatory features, properties, or limits required by the named Vulkan profile.

**Possible implementation causes:** the device is missing one or more of the mandatory capabilities listed by the profile definition. The specific missing capability is reported by the profile validator. Source-level investigation against the profile definition in `vkProfileTests.inl` is needed to identify the exact missing capability for a given failure.

#### Subgroup feature-flag inconsistency

**Possible failure symptoms:** the `subgroup_features.flags` leaf reports that `VK_SUBGROUP_FEATURE_PARTITIONED_BIT_EXT` is not set in `subgroupSupportedOperations` despite `shaderSubgroupPartitioned` being supported, or vice versa.

**Possible implementation causes:** the driver's subgroup capability table does not keep the partitioned feature bit and the partitioned operation bit in sync. The spec requires that the operation bit be set whenever the feature is supported; the relationship is defined in the `VK_EXT_shader_subgroup_partitioned` extension specification.

## Case Pruning

### Requirement-based pruning

- Vulkan-version consistency branches (`vulkan1p3`, `vulkan1p4`, `vulkan1p3_limits_validation`, `vulkan1p4_limits_validation`, `profiles`, `sparse_image_format_properties2`, `subgroup_features`) are gated on `!CTS_USES_VULKANSC` because the corresponding extensions and core versions are not part of Vulkan SC.
- The `feature_bits_influence` cases use `checkApiVersionSupport<1, 2>`, `checkApiVersionSupport<1, 3>`, and `checkApiVersionSupport<1, 4>` to skip when the implementation does not advertise the required Vulkan core version.
- Extension-specific limits-validation leaves use dedicated support checks such as `checkSupportKhrPushDescriptor`, `checkSupportExtDiscardRectangles`, `checkSupportExtDescriptorIndexing`, and `checkSupportRobustness2` to skip when the underlying extension is not supported.
- The `pnext_format_properties` flag-combination cases call `FormatPropsCase::checkSupport` to require `VK_EXT_image_drm_format_modifier`, `VK_KHR_format_feature_flags2`, or `VK_EXT_multisampled_render_to_single_sampled` depending on which `pNext` structures are chained.
- The Android-specific `android` subgroup uses `android::checkSupportAndroid` to skip on non-Android platforms. The source registers this subgroup, but `api.txt` omits it, so it does not appear in the canonical mustpass tree.

### Design-based pruning

- The `format_properties` and image-format tests iterate only the core format range, the YCbCr format range, and the YCbCr extended format range; extension-defined formats outside these ranges are intentionally not covered here.
- The `image_format_properties` test enumerates only valid usage-flag combinations via `isValidImageUsageFlagCombination` and only valid create-flag combinations via `isValidImageCreateFlagCombination`; redundant or spec-illegal combinations are skipped.
- The `pnext_format_properties` subgroup enumerates only the four basic `pNext` flag types and their pairwise and combined mixtures; deeper permutations are not generated.
- The `profiles` subgroup iterates the fixed `profileEntries` table; profile definitions not listed there are not tested.

## Key Takeaways

- The `api.info` test family is a host-side query-result consistency suite: it does not execute any shader, pipeline, or draw, and every pass/fail decision is derived from values returned by physical-device query entrypoints.
- The shared validation pattern is field-by-field comparison through offset tables, guard-byte initialization checks, and `tcu::ResultCollector` aggregation; understanding this pattern explains the shape of every leaf failure.
- The 15 direct intermediate nodes each cover one physical-device query area (format properties, image-format properties, properties2, version-specific feature/property consistency, limits validation, profile conformance, subgroup feature flags) and each failure points to a specific spec rule violated by the reported values.
- The `android` subgroup exists in source but is excluded from the mustpass tree; treat its leaves as auxiliary coverage, not as part of the canonical conformance run.
- For failure analysis, see `## Failure Meaning`: most failures reduce to either a vk1/vk2 mismatch, a reported value outside spec-required bounds, or a promoted-extension/core-version inconsistency.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent registration in `createApiTests()` | [`vktApiTests.cpp#L96`](../../../modules/vulkan/api/vktApiTests.cpp#L96) | Attaches the `info` test family to the `api` test category. |
| Local registration in `createFeatureInfoTests()` | [`vktApiFeatureInfo.cpp#L8639-L8925`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8639-L8925) | Registers the 15 direct intermediate nodes (plus source-only `android`) and delegates format/image-format subgroups to their helpers. |
| `formatProperties` per-format validator | [`vktApiFeatureInfo.cpp#L4308-L4402`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L4308-L4402) | Implements the `format_properties` leaves. |
| `createFormatTests` generator | [`vktApiFeatureInfo.cpp#L4606-L4641`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L4606-L4641) | Generates per-format leaves under `format_properties`. |
| `imageFormatProperties` validator | [`vktApiFeatureInfo.cpp#L4940-L5111`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L4940-L5111) | Implements the `image_format_properties` leaves. |
| `unsupportedImageUsage` validator | [`vktApiFeatureInfo.cpp#L5140-L5213`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L5140-L5213) | Implements the `unsupported_image_usage` leaves. |
| `extensionCoreVersions` validator | [`vktApiFeatureInfo.cpp#L3019-L3048`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L3019-L3048) | Implements the `extension_core_versions` leaf. |
| `deviceFeatures2` validator | [`vktApiFeatureInfo.cpp#L5232-L5259`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L5232-L5259) | Implements the `get_physical_device_properties2.features.core` leaf. |
| `deviceProperties2` validator | [`vktApiFeatureInfo.cpp#L5261-L5310`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L5261-L5310) | Implements the `get_physical_device_properties2.properties.basic` leaf. |
| `FormatPropsCase` and `FormatPropsTest::iterate` | [`vktApiFeatureInfo.cpp#L8497-L8602`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8497-L8602) | Implement the `pnext_format_properties` per-format × per-flag leaves. |
| `deviceFeaturesVulkan12` validator | [`vktApiFeatureInfo.cpp#L6196-L6367`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L6196-L6367) | Implements the `vulkan1p2.features` leaf. |
| `deviceFeatureExtensionsConsistencyVulkan12` validator | [`vktApiFeatureInfo.cpp#L6949-L7068`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L6949-L7068) | Implements the `vulkan1p2.feature_extensions_consistency` leaf. |
| `featureBitInfluenceOnDeviceCreate` template | [`vktApiFeatureInfo.cpp#L2137`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L2137) | Implements the `feature_bits_influence` leaves for Vulkan 1.2, 1.3, and 1.4. |
| `validateLimits12` validator | [`vktApiFeatureInfo.cpp#L827-L1162`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L827-L1162) | Implements the `vulkan1p2_limits_validation.general` leaf and the extension-specific limits-validation leaves. |
| `validateLimits14` validator | [`vktApiFeatureInfo.cpp#L1164-L1240`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L1164-L1240) | Implements the `vulkan1p4_limits_validation.general` leaf. |
| `imageFormatProperties2` validator | [`vktApiFeatureInfo.cpp#L8000-L8072`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8000-L8072) | Implements the `image_format_properties2` leaves. |
| `sparseImageFormatProperties2` validator | [`vktApiFeatureInfo.cpp#L8075-L8184`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8075-L8184) | Implements the `sparse_image_format_properties2` leaves. |
| `validateSubgroupFeatures` validator | [`vktApiFeatureInfo.cpp#L8603-L8619`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8603-L8619) | Implements the `subgroup_features.flags` leaf. |
| `createImageFormatTests` generator | [`vktApiFeatureInfo.cpp#L8255-L8266`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8255-L8266) | Generates per-format × per-type leaves for `image_format_properties`, `image_format_properties2`, and `sparse_image_format_properties2`. |
| `createImageUsageTests` generator | [`vktApiFeatureInfo.cpp#L8314-L8322`](../../../modules/vulkan/api/vktApiFeatureInfo.cpp#L8314-L8322) | Generates per-usage × per-tiling × per-format leaves for `unsupported_image_usage`. |
| Mustpass source | [`api.txt`](../../../mustpass/main/vk-default/api.txt) | Authoritative list of `dEQP-VK.api.info.*` leaves in the default mustpass set. |
