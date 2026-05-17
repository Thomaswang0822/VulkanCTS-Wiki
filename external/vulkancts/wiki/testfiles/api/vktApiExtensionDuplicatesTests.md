# [vktApiExtensionDuplicatesTests.cpp](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1)

## Overview

[vktApiExtensionDuplicatesTests.cpp](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.extension_duplicates` subtree. The file registers two direct child groups under that root through [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L370-L389): `instance` and `device`. Each child then registers the same two direct leaf cases, `by_pointers` and `by_names`, to verify that duplicate extension names are accepted during Vulkan instance or device creation.

## Role of File

Implementation-heavy test file for the `api.extension_duplicates` subgroup. The public entry point is [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L370-L389).

## Source Code

- Primary source: [vktApiExtensionDuplicatesTests.cpp](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L1)
- Header: [vktApiExtensionDuplicatesTests.hpp](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L86-L142)

## Registration Hierarchy

```text
api.extension_duplicates
├── instance
└── device
```

The confirmed Level-3 root is `api.extension_duplicates`, created by [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L370-L389) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L138-L138). The exact direct child names are confirmed from the `types` array and loop in [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L372-L387): `instance` and `device`.

## Test Families

### instance — Instance-creation duplicate-extension acceptance

Covers the direct child group registered through [`new tcu::TestCaseGroup(testCtx, type.first)`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L381-L381) when `type.first` is `"instance"` in the `types` array at [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L373-L373). This branch creates [`InstanceExtensionDuplicatesInstance`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L154-L166) through [`ExtensionDuplicatesCase::createInstance()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L192-L197) and registers two direct leaves from the `methods` array at [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L375-L385): `by_pointers` and `by_names`.

For both leaves, [`InstanceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L204-L271) enumerates available instance extensions, converts them into an enabled-extension list, duplicates that list through [`ut::StringDuplicator`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L224-L227), builds a [`VkInstanceCreateInfo`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L239-L248), and calls [`createUncheckedInstance()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L251-L252). The only semantic difference between the two leaves is the duplication mode:

- `by_pointers` selects [`duplicatePointers()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L226-L226), reusing the same `const char*` pointer multiple times.
- `by_names` selects [`duplicateStrings()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L226-L226), creating separate strings that carry identical contents.

### device — Device-creation duplicate-extension acceptance

Covers the direct child group registered through the same `types` loop in [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L379-L387) when `type.first` is `"device"`. This branch creates [`DeviceExtensionDuplicatesInstance`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L168-L180) through [`ExtensionDuplicatesCase::createInstance()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L192-L197) and also registers the two direct leaves `by_pointers` and `by_names` from the `methods` array at [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L375-L385).

For both leaves, [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L273-L365) retrieves the device-creation extension list from [`Context::getDeviceCreationExtensions()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L287-L287), duplicates it through [`ut::StringDuplicator`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L287-L290), builds one [`VkDeviceQueueCreateInfo`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L297-L304) and one [`VkDeviceCreateInfo`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L319-L331), then calls [`createUncheckedDevice()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L333-L335). On success it explicitly destroys the created device through either [`DeviceDriver::destroyDevice()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L341-L343) on Vulkan SC or [`DeviceInterface::destroyDevice()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L345-L345) on regular Vulkan.

The direct leaves under this child use the same duplication split as the instance branch:

- `by_pointers` exercises pointer reuse via [`duplicatePointers()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L289-L289).
- `by_names` exercises same-content duplication via [`duplicateStrings()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L289-L289).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct child groups | `instance`, `device` from the `types` array in [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L373-L373) |
| Direct leaf cases per child | `by_pointers`, `by_names` from the `methods` array in [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L375-L375) |
| Duplication target | instance extensions in [`InstanceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L208-L227); device-creation extensions in [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L287-L290) |
| Duplication strategy | pointer reuse via [`duplicatePointers()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L226-L226) / [`duplicatePointers()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L289-L289); same-content copied strings via [`duplicateStrings()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L226-L226) / [`duplicateStrings()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L289-L289) |
| Duplicate multiplicity pattern | each input extension is duplicated 2, 3, or 4 times according to the `StringDuplicator` logic summarized in the existing page and implemented in the utility referenced around [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L224-L227) and [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L287-L290) |
| Queue/device setup inputs | universal queue-family index from [`m_context.getUniversalQueueFamilyIndex()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L284-L284) and queue priority `1.0f` in [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L285-L304) |

## Support / Feature Requirements

No explicit feature-bit or named extension requirement gate is enforced by this file.

Observed support behavior is input-driven instead:

- the instance branch requires at least one available instance extension, otherwise it returns `QP_TEST_RESULT_QUALITY_WARNING` in [`InstanceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L210-L214)
- the device branch requires at least one device-creation extension from the context, otherwise it returns `QP_TEST_RESULT_QUALITY_WARNING` in [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L291-L295)
- on Vulkan SC, the device branch prepends Vulkan SC-specific `pNext` structures before device creation in [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L307-L317)

## Verification Methods

Observed verification is based on Vulkan object-creation success or a documented quality-warning fallback:

- **instance creation success check**: [`createUncheckedInstance()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L251-L252) must return `VK_SUCCESS`, and the final result is decided at [`InstanceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L270-L270)
- **device creation success check**: [`createUncheckedDevice()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L333-L335) must return `VK_SUCCESS`, and the final result is decided at [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L365-L365)
- **empty-input quality-warning path**: the instance branch reports a quality warning when no instance extensions are available at [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L210-L214), and the device branch does the same when the device-extension list is empty at [`vktApiExtensionDuplicatesTests.cpp`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L291-L295)
- **cleanup-after-success behavior**: successful device creation is followed by explicit destruction in [`DeviceExtensionDuplicatesInstance::iterate()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L336-L347), preventing leakage from the acceptance check itself

## Test Principles Observed

- Verify duplicate-extension tolerance separately for instance creation and device creation.
- Cover two duplicate representations: repeated identical pointers and repeated equal strings stored at different addresses.
- Build duplicate lists from extensions actually exposed by the runtime or context instead of hardcoding one extension name.
- Treat absence of any candidate extensions as a quality-warning condition rather than a conformance failure.

## Notes / Uncertainties

- This normalization confirms the Level-3 root as `api.extension_duplicates` and the exact direct child groups as `instance` and `device` from [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L370-L389).
- The direct leaves `by_pointers` and `by_names` are registered beneath both children through the shared `methods` loop in [`createExtensionDuplicatesTests()`](../../../modules/vulkan/api/vktApiExtensionDuplicatesTests.cpp#L375-L385), but they are deeper descendants and therefore documented in prose rather than expanded in the canonical parseable tree.
- The inspected lines show the branch selection between pointer reuse and copied-string duplication, but the full `StringDuplicator` helper implementation was not reopened from line 1 during this normalization pass; wording about duplicate multiplicity therefore stays aligned with the previously documented observed behavior rather than making a stronger fresh re-derivation from the helper body.
