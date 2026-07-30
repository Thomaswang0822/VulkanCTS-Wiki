## Overview

**Core question:** Does the implementation report `VkPhysicalDeviceMaintenance3Properties` values meeting Vulkan minimums, and correctly answer `vkGetDescriptorSetLayoutSupport` queries for maximal and variable-count descriptor set layouts?

- This page covers the `maintenance3_check` test family in [vktApiMaintenance3Check.cpp](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp), registered under the `api` test category by [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L119).
- The test family registers 178 test case leaves: two named cases (`maintenance3_properties`, `descriptor_set`) and 176 generated `support_count_*` leaves enumerated from descriptor type and option suffixes.
- The three behavioral groups verify distinct maintenance3 mechanisms: property minimum reporting, maximal descriptor set layout support, and variable descriptor count layout support.
- Passing requires every queried property value to meet or exceed the Vulkan-spec minimum, every maximal layout to be reported as supported, and every variable-count query to return a consistent and usable `maxVariableDescriptorCount`.

## Background Knowledge

- **`VK_KHR_maintenance3` properties.** The extension exposes `VkPhysicalDeviceMaintenance3Properties`, chained into `VkPhysicalDeviceProperties2`. Its two fields, `maxPerSetDescriptors` and `maxMemoryAllocationSize`, cap descriptor set size and memory allocation size. Vulkan mandates minimum values of 1024 descriptors and 1073741824 bytes; implementations may report larger values.
- **Descriptor set layout support query.** `vkGetDescriptorSetLayoutSupport` lets the host ask whether a proposed `VkDescriptorSetLayoutCreateInfo` would succeed, returning `supported` in `VkDescriptorSetLayoutSupport`. The query is a pure host-side check; no layout object is created.
- **Variable descriptor count.** `VK_EXT_descriptor_indexing` adds the `VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT` binding flag and the `VkDescriptorSetVariableDescriptorCountLayoutSupport` structure chained to the support query. The chained structure reports `maxVariableDescriptorCount`: the largest descriptor count the implementation can accept for the variable-size binding. The `descriptorBindingVariableDescriptorCount` feature gates this behavior.
- **Inline uniform block sizing.** For `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK`, `descriptorCount` represents bytes, not descriptor slots, and must be a multiple of 4 per VUID 02209. This affects how the test constructs and validates inline uniform block bindings.

## Registration Hierarchy

```text
api.maintenance3_check
├── maintenance3_properties
└── descriptor_set
```

The two named leaves are registered directly by [createMaintenance3Tests()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L868-L918). The remaining 176 direct children are generated `support_count_*` test case leaves, enumerated from descriptor type and four option suffixes; their full matrix appears in `## Parameter Dimensions and Observed Values` because the generated range is too large to list in the tree. The complete leaf set is visible in [api.txt](../../../mustpass/main/vk-default/api.txt#L327103-L327280).

## Parameter Dimensions and Observed Values

The `maintenance3_properties` and `descriptor_set` leaves are fixed cases with no parameter matrix. The `support_count_*` leaves are generated from the following dimensions:

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Descriptor type | `sampler`, `combined_image_sampler`, `sampled_image`, `storage_image`, `uniform_texel_buffer`, `storage_texel_buffer`, `uniform_buffer`, `storage_buffer`, `uniform_buffer_dynamic`, `storage_buffer_dynamic`, `input_attachment`, `inline_uniform_block` | Selects the descriptor type of the single tested binding. Each type exercises its own limit pool. | [descriptorTypes registration](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L875-L890) |
| Extra bindings | `true`, `false` | When true, adds 3 uniform buffer bindings before the tested binding to exercise multi-binding layouts. | [extraBindings loop](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L893) |
| Variable size | `true`, `false` | When true, sets `VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT` on the tested binding and checks `maxVariableDescriptorCount`. The `_no_variable_size` suffix marks the false case. | [useVariableSize loop](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L894) |
| Binding offset | `0`, `1` | When 1, shifts all binding numbers by one to test non-zero starting binding numbers. The `_nonzero_binding_offset` suffix marks the offset case. | [bindingOffset loop](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L895) |
| Create layout | `true`, `false` | When true, creates the descriptor set layout after querying support to confirm the supported layout is creatable. The `_create_layout` suffix marks the true case. | [createLayout loop](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L896) |

The registration assembles the case name as `support_count_<descriptor_type_short_name>` plus the suffixes for the active options in [createMaintenance3Tests()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L902-L908).

## Behavior Parameters

The primary behavioral axis is the behavioral group: the test family's leaves cluster into three groups, each exercising a distinct maintenance3 mechanism.

### `maintenance3_properties` — Maintenance3 property minimum validation

This case queries `VkPhysicalDeviceMaintenance3Properties` through `VkPhysicalDeviceProperties2` and checks that `maxMemoryAllocationSize >= 1073741824` and `maxPerSetDescriptors >= 1024`, the Vulkan-spec minimums encoded as [maxMemoryAllocationSize](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L66) and [maxDescriptorsInSet](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L67). The test initializes the struct with values one below the minimum before the query, so the returned values must come from the implementation rather than the caller's input. [Maintenance3StructTestInstance::iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L414-L444) implements this case.

### `descriptor_set` — Maximal descriptor set layout support query

This case iterates over every combination of descriptor types from size 1 to the full set, distributes descriptor counts across the selected types to saturate device limits, and queries `vkGetDescriptorSetLayoutSupport` for the resulting layout. Each combination must report `supported == VK_TRUE` because the layout fits within the implementation's reported limits. The count distribution algorithm is [distributeCounts()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L139-L227), and [Maintenance3DescriptorTestInstance::iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L475-L612) implements this case.

### `support_count_*` — Variable descriptor count layout support matrix

These 176 generated leaves query `VkDescriptorSetVariableDescriptorCountLayoutSupport` for a single tested binding of a specific descriptor type, with optional extra bindings, variable-size flag, binding offset, and layout creation. Cases with `useVariableSize=true` verify that `maxVariableDescriptorCount` is consistent across zero, one, and maximum descriptor counts, and that the reported maximum is usable; inline uniform block cases additionally check that the count is a multiple of 4 and within `maxInlineUniformBlockSize`. Cases with `useVariableSize=false` verify that `maxVariableDescriptorCount` is zero. [testCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L682-L855) implements the case body.

## Shader Analysis

No shader is involved in this test family. All checks are host-side API queries against `vkGetPhysicalDeviceProperties2` and `vkGetDescriptorSetLayoutSupport`, plus optional `vkCreateDescriptorSetLayout` calls. No `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

### `maintenance3_properties` execution

- The host chains a `VkPhysicalDeviceMaintenance3Properties` struct into `VkPhysicalDeviceProperties2`, initializing `maxPerSetDescriptors` and `maxMemoryAllocationSize` to values one below the spec minimum ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L419-L424)).
- The host calls `vkGetPhysicalDeviceProperties2` ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L431)).
- Pass requires `maintProp3.maxMemoryAllocationSize >= 1073741824` and `maintProp3.maxPerSetDescriptors >= 1024` ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L433-L437)).

### `descriptor_set` execution

- The host queries `VkPhysicalDeviceMaintenance3Properties` and, when `VK_EXT_inline_uniform_block` is supported, chains `VkPhysicalDeviceInlineUniformBlockPropertiesEXT` ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L483-L526)).
- For every combination of descriptor types from size 1 to the full set, the host builds a bindings vector by [calculateBindings()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L308-L375), which constructs a limits vector from device properties and distributes counts evenly across selected types using [distributeCounts()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L139-L227).
- The host calls `vkGetDescriptorSetLayoutSupport` for each combination ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L601)).
- Pass requires `supported == VK_TRUE` for every combination ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L602-L607)).

### `support_count_*` execution

- The host builds a `VkDescriptorSetLayoutCreateInfo` with one tested binding of the case's descriptor type, optionally preceded by 3 uniform buffer bindings ([testCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L717-L794)).
- When `useVariableSize=true`, the tested binding gets `VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT` via [VkDescriptorSetLayoutBindingFlagsCreateInfo](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L781-L786).
- The host queries support with `VkDescriptorSetVariableDescriptorCountLayoutSupport` chained to `VkDescriptorSetLayoutSupport` through [getSetLayoutSupportAndCount()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L668-L680), pre-filling `maxVariableDescriptorCount` with `UINT32_MAX` to detect untouched returns.
- When `useVariableSize=false`, pass requires `maxVariableDescriptorCount == 0` ([testCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L801-L805)).
- When `useVariableSize=true`, pass requires: the reported maximum is consistent across zero, one, and maximum descriptor counts; inline uniform block counts are multiples of 4 and within `maxInlineUniformBlockSize`; and the implementation reports the layout with the maximum count as supported ([testCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L806-L841)).
- When `createLayout=true`, the host calls `vkCreateDescriptorSetLayout` to confirm the supported layout is creatable ([testCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L843-L852)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `maintenance3_properties` | Maintenance3 property value below Vulkan-spec minimum. |
| `descriptor_set` | Maximal descriptor set layout reported unsupported despite fitting within reported limits. |
| `support_count_*` | Variable descriptor count query returned inconsistent, invalid, or unusable `maxVariableDescriptorCount`, or supported layout creation failed. |

### Cause Analysis

#### Maintenance3 property value below Vulkan-spec minimum

**Possible failure symptoms:** `Maintenance3StructTestInstance::iterate()` returns `fail` because `maxMemoryAllocationSize < 1073741824` or `maxPerSetDescriptors < 1024` ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L433-L437)).

**Possible implementation causes:** The implementation either does not support `VK_KHR_maintenance3` correctly or reports property values that violate the Vulkan spec minimums. The `checkSupport()` gate requires the extension ([Maintenance3StructTestCase::checkSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L457-L460)), so a failure here indicates the extension is present but the reported values are too small. Source-level investigation is needed to determine whether the driver under-reports a limit or the extension advertisement is inconsistent with the property values.

#### Maximal descriptor set layout reported unsupported despite fitting within reported limits

**Possible failure symptoms:** `Maintenance3DescriptorTestInstance::iterate()` returns `fail` with a message listing the descriptor type counts that were rejected ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L602-L607)).

**Possible implementation causes:** The test distributes descriptor counts to saturate the device's reported limits using [distributeCounts()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L139-L227) and [buildLimitsVector()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L230-L305). A failure means `vkGetDescriptorSetLayoutSupport` returned `supported == VK_FALSE` for a layout whose per-type and total counts fit within the limits the implementation reported. This can happen when the support query applies a tighter constraint than the advertised limits, or when the implementation's support logic does not account for all limit interactions the test exercises. Source-level investigation is needed to determine which combination triggered the rejection.

#### Variable descriptor count query returned inconsistent, invalid, or unusable maxVariableDescriptorCount, or supported layout creation failed

**Possible failure symptoms:** `testCountLayoutSupport()` triggers `TCU_FAIL` because: `maxVariableDescriptorCount` is nonzero when no variable-size binding is present; the count differs between zero and one descriptor queries; the maximum-count query is reported unsupported; the reported maximum differs between one-descriptor and maximum-descriptor queries; for inline uniform blocks, the count exceeds `maxInlineUniformBlockSize` or is not a multiple of 4; or `vkCreateDescriptorSetLayout` fails for a layout reported as supported ([testCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L801-L852)).

**Possible implementation causes:** The `getSetLayoutSupportAndCount()` helper pre-fills `maxVariableDescriptorCount` with `UINT32_MAX` to catch implementations that leave the field untouched ([getSetLayoutSupportAndCount()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L668-L680)). A failure can come from the implementation not writing the chained structure, applying inconsistent limits across query inputs, mishandling the inline uniform block byte-count semantics, or reporting a layout as supported when creation would fail. The inline uniform block multiple-of-4 check enforces VUID-VkDescriptorSetLayoutBinding-descriptorType-02209; a violation there indicates the implementation returned a count that the spec does not permit for that descriptor type. Source-level investigation is needed to identify which check failed for the specific case.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_maintenance3` ([Maintenance3StructTestCase::checkSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L457-L460), [Maintenance3DescriptorTestCase::checkSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L625-L628), [checkSupportCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L646)).
- All `support_count_*` cases require `VK_EXT_descriptor_indexing` ([checkSupportCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L647)).
- `support_count_*` cases with `useVariableSize=true` require the `descriptorBindingVariableDescriptorCount` feature; otherwise the case throws `NotSupportedError` ([checkSupportCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L649-L654)).
- On non-Vulkan SC builds, `support_count_inline_uniform_block` cases require `VK_EXT_inline_uniform_block` ([checkSupportCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L656-L659)).
- On Vulkan SC builds, `#ifndef CTS_USES_VULKANSC` excludes `VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK` from registration ([descriptorTypes registration](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L887-L889)).

### Design-based pruning

- `support_count_*` cases with `useVariableSize=true` skip `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC` and `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC` because variable-size descriptors are not valid for dynamic buffer types ([registration loop](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L898-L900)). This removes 16 redundant cases that the spec does not permit.
- The `descriptor_set` case limits inline uniform block testing when `maxPerStageDescriptorInlineUniformBlocks > 64` and the combination size is neither 1 nor the full set, to avoid an impractical number of bindings ([iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L582-L587)).
- On Vulkan SC builds, `calculateBindings()` caps each type's count at `maxReasonableBindingCounts = 1024` to keep `descriptorSetLayoutBindingRequestCount` and `descriptorSetLayoutBindingLimit` within reasonable bounds ([calculateBindings()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L328-L332)).

## Key Takeaways

- The test family groups three distinct maintenance3 checks: property minimum validation, maximal descriptor set layout support, and variable descriptor count layout support.
- `maintenance3_properties` is the only case that checks a hard spec minimum; the other two groups check internal consistency against the implementation's reported limits.
- The `descriptor_set` case has the largest combination space: it enumerates every descriptor type combination from size 1 to the full set and distributes counts to saturate all reported limits.
- The `support_count_*` matrix verifies `maxVariableDescriptorCount` consistency across zero, one, and maximum descriptor counts, and confirms a supported layout is creatable when `createLayout=true`.
- See `## Failure Meaning` for the failure interpretation: property below minimum, maximal layout rejected despite fitting reported limits, or variable-count query returning inconsistent or unusable results.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parent registration | [vktApiTests.cpp#L119](../../../modules/vulkan/api/vktApiTests.cpp#L119) | Adds `maintenance3_check` under the `api` test category. |
| Test family factory | [createMaintenance3Tests()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L868-L918) | Registers the two named leaves and generates the 176 `support_count_*` leaves. |
| Spec minimum constants | [vktApiMaintenance3Check.cpp#L66-L67](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L66-L67) | Defines `maxMemoryAllocationSize = 1073741824u` and `maxDescriptorsInSet = 1024u`. |
| Property check | [Maintenance3StructTestInstance::iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L414-L444) | Queries and validates `VkPhysicalDeviceMaintenance3Properties`. |
| Count distribution | [distributeCounts()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L139-L227) | Evenly distributes descriptor counts across selected types to saturate device limits. |
| Limits vector | [buildLimitsVector()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L230-L305) | Constructs the limit-to-type map used by the distribution algorithm. |
| Binding calculation | [calculateBindings()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L308-L375) | Builds the `VkDescriptorSetLayoutBinding` vector for a type combination. |
| Descriptor set support check | [Maintenance3DescriptorTestInstance::iterate()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L475-L612) | Iterates type combinations and queries `vkGetDescriptorSetLayoutSupport`. |
| Variable count support check | [testCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L682-L855) | Queries `VkDescriptorSetVariableDescriptorCountLayoutSupport` and validates consistency. |
| Support and count helper | [getSetLayoutSupportAndCount()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L668-L680) | Chains the variable-count structure and pre-fills `maxVariableDescriptorCount` with `UINT32_MAX`. |
| Support gates | [checkSupportCountLayoutSupport()](../../../modules/vulkan/api/vktApiMaintenance3Check.cpp#L644-L660) | Requires `VK_KHR_maintenance3`, `VK_EXT_descriptor_indexing`, the variable-count feature, and `VK_EXT_inline_uniform_block` where applicable. |
| Mustpass entries | [api.txt#L327103-L327280](../../../mustpass/main/vk-default/api.txt#L327103-L327280) | Lists all 178 `dEQP-VK.api.maintenance3_check.*` leaves. |
