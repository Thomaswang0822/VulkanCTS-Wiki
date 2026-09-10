## Overview

**Core question:** At which Vulkan creation boundary does an implementation accept or reject the `VkApplicationParametersEXT` record supplied by the application, and does it return the result required for that record?

This page covers the implementation in [`vktApplicationParametersTests.cpp`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L40-L69), registered below `sc.application_parameters`. It is a creation-time API test: it does not submit work to a queue and does not create a pipeline, image, buffer, or shader.

The family has two creation targets and five scenario names. `create_instance` attaches the extension structure through `VkApplicationInfo` and checks `vkCreateInstance`; `create_device` attaches it directly to `VkDeviceCreateInfo` and checks device creation. The source constructs the test record from the active physical device's queried IDs, changes selected fields for negative cases, and compares the returned `VkResult` with the record's expected result. The default source defines deterministic data for the invalid identity and invalid-key scenarios. The invalid-value and valid scenarios are vendor-data hooks; their names are registered and present in the default mustpass file, but the default generator does not supply records for them.

## Background Knowledge

- `VkApplicationParametersEXT` is the extension structure carrying a `vendorID`, `deviceID`, parameter key, and 64-bit parameter value. It is passed through Vulkan's extensible `pNext` mechanism at instance or device creation. The extension's creation-time rules are specified in [`initialization.adoc`](../../../../vulkan-docs/src/chapters/initialization.adoc#L923-L996).
- A `pNext` chain is a linked sequence of extension structures reached from a Vulkan create-info structure. In the instance case the chain is `VkInstanceCreateInfo.pApplicationInfo -> VkApplicationInfo.pNext -> VkApplicationParametersEXT`; in the device case it is `VkDeviceCreateInfo.pNext -> VkApplicationParametersEXT`.
- `VkResult` is the observable result used here. The test distinguishes `VK_ERROR_INCOMPATIBLE_DRIVER`, `VK_ERROR_INITIALIZATION_FAILED`, and `VK_SUCCESS`; it does not infer correctness from later use of a created object.

## Registration Hierarchy

```text
sc.application_parameters
├── create_device
└── create_instance
```

Each creation group contains the five leaves `invalid_device_id`, `invalid_parameter_key`, `invalid_parameter_value`, `invalid_vendor_id`, and `valid`.

The root and both groups are created by [`createApplicationParametersTests`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L322-L359). The ten paths above are the default mustpass registrations, confirmed by [`sc.txt`](../../../mustpass/main/vksc-default/sc.txt#L7-L16). Registration does not mean that every leaf necessarily reaches a creation call: support/data checks can stop a leaf before execution.

## Parameter Dimensions and Observed Values

| Dimension | Values in the registered matrix | What the value changes | Evidence |
|---|---|---|---|
| Creation target | `create_instance`, `create_device` | Chooses the object-creation API and the location of `VkApplicationParametersEXT` in the chain. | [`vktApplicationParametersTests.cpp#L193-L240`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L193-L240), [`vktApplicationParametersTests.cpp#L257-L299`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L257-L299) |
| Scenario | `invalid_vendor_id`, `invalid_device_id`, `invalid_parameter_key`, `invalid_parameter_value`, `valid` | Selects the field deliberately made invalid, or a vendor-supplied invalid/valid key-value pair. | [`vktApplicationParametersTests.cpp#L46-L53`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L46-L53), [`vktApplicationParametersTests.cpp#L90-L111`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L90-L111) |
| Baseline identity | `vendorID` and `deviceID` queried from the active physical device | Supplies the identity used by the default record and by vendor-data matching. | [`vktApplicationParametersTests.cpp#L71-L81`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L71-L81) |
| Invalid identity value | `0x01234567` | Replaces exactly one queried ID in each invalid-identity default record. | [`vktApplicationParametersTests.cpp#L90-L100`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L90-L100) |
| Default invalid key | `0x7fffffff` | Supplies an unknown parameter key with a zero-initialized value. | [`vktApplicationParametersTests.cpp#L102-L105`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L102-L105) |
| Vendor key/value | Defined only when vendor data is added | Supplies the vendor-specific cases that cannot be generalized by CTS. | [`vktApplicationParametersTests.cpp#L128-L160`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L128-L160) |

## Behavior Parameters

### `create_instance` — validate the application-parameter chain during instance creation

For each available record, the test initializes `VkApplicationParametersEXT` with `pNext = nullptr`, puts it in `VkApplicationInfo.pNext`, and points `VkInstanceCreateInfo.pApplicationInfo` at that application info. It calls `platformInterface.createInstance`, records the returned result, and destroys the instance if the implementation returned one—even for a case expected to fail. This cleanup makes each record independent. The construction and comparison are in [`createInstanceTest`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L257-L319).

The default negative identity cases expect `VK_ERROR_INCOMPATIBLE_DRIVER`. The default invalid-key case expects `VK_ERROR_INITIALIZATION_FAILED`. A vendor-supplied `valid` record expects `VK_SUCCESS`; a vendor-supplied invalid-value record expects `VK_ERROR_INITIALIZATION_FAILED`.

### `create_device` — validate the application-parameter chain during device creation

The test first creates a custom instance. For each available record it chains `VkApplicationParametersEXT` to `VkDeviceCreateInfo.pNext`, requests one queue from queue family zero, and supplies the Vulkan SC feature and default device-object-reservation structures needed by this surrounding device-creation call. It then calls `createUncheckedDevice` and compares the result. No device is used for rendering or compute. See [`createDeviceTest`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L193-L255).

For device records, the source overwrites the expected result with `VK_ERROR_INITIALIZATION_FAILED` for every scenario other than `valid`. Thus the device invalid-identity cases intentionally do not use the instance path's `VK_ERROR_INCOMPATIBLE_DRIVER` expectation. A vendor-supplied `valid` record expects `VK_SUCCESS`.

### `invalid_vendor_id` — exercise a nonmatching vendor identity

The default record starts with the active device's IDs, replaces `vendorId` with `0x01234567`, and leaves the device ID at its queried value. Instance creation must return `VK_ERROR_INCOMPATIBLE_DRIVER`; device creation must return `VK_ERROR_INITIALIZATION_FAILED` because of the device-path normalization described above. The test checks the API result only; it does not prove which internal identity-matching component produced it. See [`vktApplicationParametersTests.cpp#L88-L100`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L88-L100) and [`vktApplicationParametersTests.cpp#L114-L117`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L114-L117).

### `invalid_device_id` — exercise a nonmatching device identity

The default record preserves the queried vendor ID and replaces `deviceId` with `0x01234567`. The expected result is `VK_ERROR_INCOMPATIBLE_DRIVER` for instance creation and `VK_ERROR_INITIALIZATION_FAILED` for device creation. The source does not independently establish that `0x01234567` is absent from every possible implementation; it uses this fixed value as its invalid-ID test input.

### `invalid_parameter_key` — exercise rejection of an unknown key

The default record uses parameter key `0x7fffffff`, leaves the value at its zero-initialized value, and expects `VK_ERROR_INITIALIZATION_FAILED`. This is a key-recognition/validation check, not a test of a vendor-defined value range. See [`vktApplicationParametersTests.cpp#L102-L105`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L102-L105).

### `invalid_parameter_value` — vendor-supplied invalid value

The generic generator intentionally emits no default record for this scenario. The conditional vendor block shows the required shape: matching vendor/device identity, a vendor-defined key, an invalid value, and `VK_ERROR_INITIALIZATION_FAILED` for both creation targets. Until a vendor adds such data, the registered leaf has no executable record. See [`vktApplicationParametersTests.cpp#L107-L111`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L107-L111) and [`vktApplicationParametersTests.cpp#L140-L160`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L140-L160).

### `valid` — vendor-supplied accepted value

This scenario is likewise data-driven. A vendor must provide a recognized key and accepted value for the relevant creation target; the expected result is `VK_SUCCESS`. The generic source does not claim that zero is a valid parameter value, so the placeholder values in the disabled example are not coverage. See [`vktApplicationParametersTests.cpp#L128-L160`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L128-L160).

## Shader Analysis

No shader participates. The implementation performs only instance/device creation and physical-device parameter checks; it creates no shader module, pipeline, command buffer, draw, or dispatch.

## Runtime Execution and Result Checking

1. The case's support callback enumerates instance extensions and requires `VK_EXT_application_parameters`. If the extension is absent, it raises `NotSupportedError`; this is a support skip, not a failed `VkResult` comparison. It then obtains the data list and raises `TestError` if that list is empty. See [`checkSupport`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L179-L191).
2. Data construction queries `VkPhysicalDeviceProperties` from the active physical device. The queried `vendorID` and `deviceID` form the baseline for default records and the matching keys for vendor records. See [`readIDsFromDevice`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L71-L81).
3. The selected record is copied into `VkApplicationParametersEXT`. Instance tests reach it through `VkApplicationInfo`; device tests put it in `VkDeviceCreateInfo.pNext`. The device path also creates the prerequisite custom instance and surrounding queue/SC structures. See [`vktApplicationParametersTests.cpp#L199-L234`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L199-L234) and [`vktApplicationParametersTests.cpp#L266-L292`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L266-L292).
4. Each creation call's returned `VkResult` is compared directly to `testData.expectedResult`. A mismatch marks the aggregate test as failed, while all matching records return `Pass`. The implementation continues through the available records rather than returning at the first mismatch. See [`vktApplicationParametersTests.cpp#L239-L254`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L239-L254) and [`vktApplicationParametersTests.cpp#L307-L319`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L307-L319).

These outcomes have different meanings:

- missing extension: unsupported implementation and `NotSupportedError`;
- empty data list: test-data/configuration error and `TestError`;
- returned result differs from the record: executed conformance failure;
- all available records match: test pass.

## Failure Meaning

### Failure Cause Mapping

| Failing path or condition | What the source observed | Evidence-backed investigation scope |
|---|---|---|
| `create_instance.invalid_vendor_id` or `create_instance.invalid_device_id` | Instance creation did not return `VK_ERROR_INCOMPATIBLE_DRIVER`. | Check application-parameter identity matching and result mapping at instance creation. The CTS result does not identify the internal subsystem. |
| `create_device.invalid_vendor_id` or `create_device.invalid_device_id` | Device creation did not return `VK_ERROR_INITIALIZATION_FAILED`. | Check device-creation validation of the supplied identity and the error returned at that boundary. |
| `invalid_parameter_key` | Creation did not return `VK_ERROR_INITIALIZATION_FAILED`. | Check recognition/rejection of the supplied key. The test does not inspect internal key tables. |
| Vendor `invalid_parameter_value` | A vendor-provided invalid value did not return its recorded expected result, normally `VK_ERROR_INITIALIZATION_FAILED`. | Check the vendor key's value validation and confirm the vendor data itself matches the intended invalid condition. |
| Vendor `valid` | A vendor-provided valid pair did not return `VK_SUCCESS`. | Check recognition and application of the vendor key/value pair, then verify the vendor data's target IDs and expected result. |
| Any executed record | The direct `VkResult` comparison failed. | The failure localizes the symptom to the creation call and record, not to a particular driver subsystem. |

### Cause Analysis

#### Identity validation

**Possible failure symptoms:** An identity case returns a result other than the expected creation-target-specific error.

**Possible implementation causes:** The implementation may accept a nonmatching identity, reject a matching identity, or map the rejection to a different error at the selected creation boundary. The test cannot distinguish those internal causes.

#### Key/value validation

**Possible failure symptoms:** The unknown key, vendor invalid value, or vendor valid value returns a result different from its record.

**Possible implementation causes:** Key recognition or vendor-specific value validation/application may be incorrect. For vendor cases, source-level investigation must also confirm the vendor data defines the intended key and value.

## Case Pruning

### Requirement-based pruning

- Every registered leaf first requires `VK_EXT_application_parameters`. Missing support stops the case with `NotSupportedError`, so no creation call is made. See [`vktApplicationParametersTests.cpp#L181-L185`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L181-L185).

### Design-based pruning

- `getTestDataList` always adds one default record for the three default-defined scenarios (`invalid_vendor_id`, `invalid_device_id`, and `invalid_parameter_key`). It deliberately does not add a default record for `invalid_parameter_value` or `valid`. See [`vktApplicationParametersTests.cpp#L120-L165`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L120-L165).
- Vendor records are added only when creation target and scenario match, the vendor ID equals the active physical device's vendor ID, and the vendor device ID is either zero (wildcard) or equals the active device ID. See [`vktApplicationParametersTests.cpp#L166-L174`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L166-L174).
- If filtering leaves no record, `checkSupport` raises `TestError` with `No test data available - please update vendorTestDataList`. This is not a valid way to obtain a pass and should not be described as ordinary pruning or unsupported-extension behavior. See [`vktApplicationParametersTests.cpp#L187-L190`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L187-L190).
- The default matrix does not enumerate arbitrary identities, keys, values, or combinations. Such coverage requires explicit vendor data; the page should not infer universal valid values from the disabled example block.

## Key Takeaways

- The same extension structure is tested at two boundaries: through `VkApplicationInfo` for instance creation and through `VkDeviceCreateInfo` for device creation.
- The default records use the active physical device's identity as a baseline, replace one ID with `0x01234567` for negative identity checks, and use `0x7fffffff` for the invalid-key check.
- Expected errors are creation-target dependent: instance invalid-identity records expect `VK_ERROR_INCOMPATIBLE_DRIVER`, while device non-`valid` records are normalized to `VK_ERROR_INITIALIZATION_FAILED` by the source.
- The `invalid_parameter_value` and `valid` leaves are registered hooks, not universally populated tests. Vendor data is required before either leaf reaches a creation call.
- A pass or failure is determined by direct `VkResult` equality for every available record; it does not reveal the driver's internal failure location.

## Source Reference Appendix

| Source | Relevant lines | Purpose |
|---|---:|---|
| [`vktApplicationParametersTests.cpp`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L40-L117) | 40–117 | Test dimensions, record fields, queried IDs, default invalid records, and expected results. |
| [`vktApplicationParametersTests.cpp`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L120-L176) | 120–176 | Vendor-data hook and filtering rules. |
| [`vktApplicationParametersTests.cpp`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L179-L191) | 179–191 | Extension support and empty-data handling. |
| [`vktApplicationParametersTests.cpp`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L193-L255) | 193–255 | Device creation setup, call, logging, and result aggregation. |
| [`vktApplicationParametersTests.cpp`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L257-L319) | 257–319 | Instance creation setup, cleanup, call, and result aggregation. |
| [`vktApplicationParametersTests.cpp`](../../../modules/vulkan/sc/vktApplicationParametersTests.cpp#L322-L359) | 322–359 | Exact root, group, and leaf registration. |
| [`vktSafetyCriticalTests.cpp`](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L64) | 45–64 | Places `application_parameters` under the `sc` root. |
| [`sc.txt`](../../../mustpass/main/vksc-default/sc.txt#L7-L16) | 7–16 | Confirms the ten default mustpass paths. |
| [`initialization.adoc`](../../../../vulkan-docs/src/chapters/initialization.adoc#L923-L996) | 923–996 | Extension structure and creation-time semantics. |
