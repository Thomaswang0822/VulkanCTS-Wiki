## Overview

**Core question:** Do the DRM-backed Vulkan display commands identify, acquire, and release a display with the result and ownership rules required by the WSI specification?

- `vktWsiAcquireDrmDisplayTests.cpp` implements ten compact API tests under the `wsi.acquire_drm_display` test family. The header exposes its `createAcquireDrmDisplayTests` registration function.
- The tests call `vkGetDrmDisplayEXT`, `vkAcquireDrmDisplayEXT`, and `vkReleaseDisplayEXT` with valid and deliberately invalid DRM file descriptors, connector IDs, and DRM ownership states.
- The implementation uses `tcu::LibDrm` to find the DRM primary node associated with the selected physical device, inspect connected connectors, check master status, and create a DRM lease where needed.
- The tests perform no rendering and compile their test body only when `DEQP_SUPPORT_DRM` is enabled and `CTS_USES_VULKANSC` is not defined. They validate `VkResult` values and, for display lookup, the returned `VkDisplayKHR` handle.

## Background Knowledge

For the shared concept direct-display objects, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- DRM exposes displays through file descriptors, connectors, CRTCs, and ownership permissions. A DRM lease can restrict a file descriptor to selected DRM objects, which lets these tests distinguish an owned connector from another connected connector.
- `VkDisplayKHR` identifies a Vulkan display. `vkGetDrmDisplayEXT` maps a DRM connector ID to that handle without requiring DRM master permissions. `vkAcquireDrmDisplayEXT` gives the Vulkan instance control of the display and requires a DRM master file descriptor. `vkReleaseDisplayEXT` ends that control.
- The Vulkan specification requires the DRM file descriptor to correspond to the selected physical device. It specifies `VK_ERROR_UNKNOWN` for an invalid device association and for a connector not owned by the supplied descriptor, and `VK_ERROR_INITIALIZATION_FAILED` when display acquisition encounters an error. See [the DRM display command descriptions](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L1604-L1676).

## Registration Hierarchy

```text
wsi.acquire_drm_display
├── get_drm_display
├── get_drm_display_invalid_fd
├── get_drm_display_invalid_connector_id
├── get_drm_display_not_master
├── get_drm_display_unowned_connector_id
├── acquire_drm_display
├── acquire_drm_display_invalid_fd
├── acquire_drm_display_not_master
├── acquire_drm_display_unowned_connector_id
└── release_display
```

The ten names are registered by [`createAcquireDrmDisplayTests`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L750-L775). The `wsi.acquire_drm_display` group is attached directly to the WSI test category by [`createWsiTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L91). The same ten paths appear in the default Vulkan mustpass list, for example [`vk-default/wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L1-L10).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `get_drm_display`, `get_drm_display_invalid_fd`, `get_drm_display_invalid_connector_id`, `get_drm_display_not_master`, `get_drm_display_unowned_connector_id`, `acquire_drm_display`, `acquire_drm_display_invalid_fd`, `acquire_drm_display_not_master`, `acquire_drm_display_unowned_connector_id`, `release_display` | Selects one fixed API scenario. The `DrmTestIndex` value reaches the corresponding method through the `iterate()` switch. | [`DrmTestIndex`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L58-L72), [`iterate`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L137-L171) |
| DRM file descriptor | A device fd, a second fd, an invalid fd opened on `/`, or a DRM lease fd, depending on the test case | Changes whether the command receives a device-associated descriptor, a descriptor without master status, an unusable descriptor, or a descriptor that owns only leased DRM objects. | [`getDrmFdPtr`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L203-L230), [`testGetDrmDisplayEXTInvalidFd`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L341-L363), [`testAcquireDrmDisplayEXTUnownedConnectorId`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L623-L662) |
| Connector ownership | A connected connector, `connectorId + 1234`, or a second connector excluded from a DRM lease | Controls whether `vkGetDrmDisplayEXT` can identify a display and whether the leased descriptor owns the requested connector. | [`getConnectedConnectorId`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L239-L257), [`testGetDrmDisplayEXTUnownedConnectorId`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L448-L483) |
| DRM permissions | Master fd or a second fd used as the non-master fd | Separates operations that only gather display information from acquisition and release operations that require control of the display. | [`isDrmMaster`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L286-L300), [`testGetDrmDisplayEXTNotMaster`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L405-L431) |

The test family has no `wsiType` parameter and no generated data, shader, or rendering matrix. Each registered leaf runs one fixed scenario.

## Behavior Parameters

The primary behavioral axis is the **test case leaf**. Each leaf selects a different ownership or lifecycle condition.

### `get_drm_display`: identify a connected display

The test passes a device-associated DRM fd and a connected connector ID to `vkGetDrmDisplayEXT`. It expects `VK_SUCCESS` and checks that the function replaces the `INVALID_DISPLAY` sentinel with a non-null display handle.

### `get_drm_display_invalid_fd`: reject an unusable descriptor

The test opens `/` with `O_RDONLY | O_PATH` and passes that descriptor to `vkGetDrmDisplayEXT` with an otherwise valid connector ID. It expects `VK_ERROR_UNKNOWN`.

### `get_drm_display_invalid_connector_id`: reject an unknown connector

The test adds `1234` to a connected connector ID and passes the fabricated value with a valid DRM fd. It expects `VK_ERROR_UNKNOWN` and requires the output handle to be `VK_NULL_HANDLE`.

### `get_drm_display_not_master`: allow lookup without master permission

The test opens two DRM descriptors and uses the second descriptor for connector lookup and `vkGetDrmDisplayEXT`. It expects `VK_SUCCESS` and a valid display handle. This case covers the specification rule that display identification uses the fd for information gathering and does not require DRM master permissions.

### `get_drm_display_unowned_connector_id`: reject a connector outside a lease

The test creates a lease containing one connected connector and a compatible CRTC, then asks `vkGetDrmDisplayEXT` on the lease fd for a different connected connector. It expects `VK_ERROR_UNKNOWN` and `VK_NULL_HANDLE`.

### `acquire_drm_display`: acquire a connected display

The test identifies a connected display with `vkGetDrmDisplayEXT`, then passes the same master fd and display handle to `vkAcquireDrmDisplayEXT`. Both calls must return `VK_SUCCESS`.

### `acquire_drm_display_invalid_fd`: reject acquisition with an unusable descriptor

The test first obtains a valid display, then calls `vkAcquireDrmDisplayEXT` with the descriptor opened on `/`. It expects `VK_ERROR_UNKNOWN`, which covers the required physical-device and DRM-fd association check.

### `acquire_drm_display_not_master`: reject acquisition without master permission

The test obtains a display through the second of two DRM descriptors and then calls `vkAcquireDrmDisplayEXT` with that descriptor. It expects `VK_ERROR_INITIALIZATION_FAILED`. Unlike the lookup case, acquisition needs the descriptor to have DRM master permissions.

### `acquire_drm_display_unowned_connector_id`: reject acquisition through a lease that lacks the display

The test uses the original master fd to identify a display for the second connected connector, then creates a lease containing the first connector and a compatible CRTC. It calls `vkAcquireDrmDisplayEXT` with the lease fd and the display identified for the second connector, and expects `VK_ERROR_INITIALIZATION_FAILED` because that display is not among the DRM objects owned by the leased descriptor.

### `release_display`: complete the acquire and release lifecycle

The test identifies and acquires a connected display with a master fd, then calls `vkReleaseDisplayEXT`. All three calls must return `VK_SUCCESS`. The release case is registered in this source file with the `VK_EXT_direct_mode_display` tests, and it completes the DRM display ownership lifecycle.

## Shader Analysis

This test family has no shader code or device-side rendering. The checks use Vulkan API return values and display handles, so no shader walkthrough or SPIR-V analysis applies.

## Runtime Execution and Result Checking

- The `AcquireDrmDisplayTestInstance` constructor creates a custom Vulkan instance with `VK_KHR_surface`, `VK_KHR_display`, `VK_EXT_direct_mode_display`, and `VK_EXT_acquire_drm_display`. If any required instance extension is unavailable, it throws `NotSupportedError` rather than failing the test. See [`createInstanceWithAcquireDrmDisplay`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L179-L195).
- `getDrmFdPtr` queries `VkPhysicalDeviceDrmPropertiesEXT`, requires `hasPrimary`, maps the reported major and minor numbers to a DRM node through `LibDrm`, and opens the node. Missing primary-device or DRM-node support produces `NotSupportedError`.
- `getConnectedConnectorId` scans DRM resources and returns a connector whose state is `DRM_MODE_CONNECTED`. The optional connector argument excludes one connector, which supplies the second connector for lease tests. `getValidCrtcId` finds a CRTC compatible with the leased connector.
- The two invalid-fd cases open `/` with `O_RDONLY | O_PATH`. The tests close that descriptor after the Vulkan call and compare the returned error with the expected value.
- The non-master cases open two DRM descriptors and require distinct descriptor values. The implementation uses the second descriptor for the lookup or acquisition operation. `isDrmMaster` probes `drmAuthMagic` with an invalid magic value: a non-master fd returns `-EACCES`, while another result indicates master access. Tests that need master access convert a missing permission into `NotSupportedError`.
- The unowned-connector cases require two connected displays. They create a DRM lease containing the first connector and a compatible CRTC, then use the lease fd for the operation that must not access the other connector.
- A successful lookup must return a handle that is neither `VK_NULL_HANDLE` nor the `INVALID_DISPLAY` sentinel. Lookup error cases that validate the output require `VK_NULL_HANDLE`.
- A Vulkan call returning `VK_ERROR_EXTENSION_NOT_PRESENT` becomes `NotSupportedError`. Other unexpected results call `TCU_FAIL`. A test returns `tcu::TestStatus::pass("pass")` only after all checks for its scenario succeed. See the individual implementations for [`vkGetDrmDisplayEXT`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L309-L332), [`vkAcquireDrmDisplayEXT`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L499-L528), and [`vkReleaseDisplayEXT`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L679-L712).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `get_drm_display` | The implementation could not map a valid, connected, device-owned connector to a `VkDisplayKHR`, or it did not write a usable handle. |
| `get_drm_display_invalid_fd` | The implementation accepted a file descriptor that does not represent the selected physical device's DRM node. |
| `get_drm_display_invalid_connector_id` | The implementation did not reject a connector ID for which no display exists, or it wrote a non-null output handle on error. |
| `get_drm_display_not_master` | The implementation incorrectly required DRM master permission for display identification, or it failed a valid connector lookup through a non-master fd. |
| `get_drm_display_unowned_connector_id` | The implementation accepted a connector that the supplied DRM lease does not own, or it did not clear the output display handle. |
| `acquire_drm_display` | The implementation could not grant control of a valid display through a matching master fd. |
| `acquire_drm_display_invalid_fd` | The implementation did not reject acquisition through a non-DRM or wrong-device file descriptor with `VK_ERROR_UNKNOWN`. |
| `acquire_drm_display_not_master` | The implementation did not reject acquisition through a descriptor without DRM master permissions with `VK_ERROR_INITIALIZATION_FAILED`. |
| `acquire_drm_display_unowned_connector_id` | The implementation allowed acquisition through a lease that lacks the display's required DRM ownership. |
| `release_display` | The implementation failed to release a display acquired by the same physical device and did not complete the expected lifecycle. |

### Cause Analysis

#### DRM fd and physical-device association

**Possible failure symptoms:** A valid-looking lookup or acquisition returns an unexpected error, or an invalid-fd case does not return the expected error.

**Possible implementation causes:** The Vulkan implementation may not associate the supplied DRM fd with the physical device as required by the WSI specification. The test source establishes the association by querying `VkPhysicalDeviceDrmPropertiesEXT` and opening the matching primary node. A lower-level cause requires source-level investigation.

#### Connector lookup and ownership

**Possible failure symptoms:** `vkGetDrmDisplayEXT` returns success for the fabricated or leased-out connector, returns the wrong result for a valid connector, or leaves a non-null display handle after an invalid lookup.

**Possible implementation causes:** The implementation may map connector IDs incorrectly, fail to enforce ownership by the supplied DRM fd, or mishandle the output parameter on an error. The specification states that an unknown or unowned connector returns `VK_ERROR_UNKNOWN` and `VK_NULL_HANDLE` when no corresponding display exists. The exact implementation cause requires investigation of the DRM connector-to-display mapping.

#### DRM master permission

**Possible failure symptoms:** `get_drm_display_not_master` fails even though the lookup should only gather information, or either acquisition case accepts a descriptor without the required master permission.

**Possible implementation causes:** The implementation may apply the master-permission rule to the lookup command, omit it from acquisition, or translate the acquisition failure to the wrong `VkResult`. The specification requires master permissions for acquisition but not for `vkGetDrmDisplayEXT`; it specifies `VK_ERROR_INITIALIZATION_FAILED` for acquisition errors.

#### Display ownership lifecycle

**Possible failure symptoms:** A valid acquisition fails, or `release_display` fails after a successful lookup and acquisition.

**Possible implementation causes:** The implementation may fail to grant ownership to the Vulkan instance, track the acquired display incorrectly, or release a display handle associated with the wrong physical device. The source keeps the DRM fd alive through the test instance and releases the display only after acquisition. The precise cause requires investigation of display-control state and the DRM/Vulkan handoff.

#### Test-environment prerequisites

**Possible failure symptoms:** The test reports `NotSupportedError` before reaching its Vulkan result check.

**Possible implementation causes:** The environment may lack a DRM primary node, a connected connector, a compatible CRTC, two connected displays, the required extension, or DRM master access. These are prerequisites reported by the test, not conformance failures. A desktop compositor or another DRM client can prevent the master and multi-display cases from running.

## Case Pruning

### Requirement-based pruning

- The implementation does not prune registered leaves based on a parameter matrix. Each leaf maps directly to one `DrmTestIndex` value and one test method.
- Runtime prerequisite checks can report `NotSupportedError` when the build lacks DRM support, the required instance extensions are missing, no matching DRM primary node exists, no connected connector exists, no compatible CRTC exists, or the environment cannot provide the requested DRM ownership state.
- The two unowned-connector cases need two connected displays. The master-dependent cases also need an environment in which the test process can obtain DRM master permissions, such as a system without another client owning the display.

### Design-based pruning

The source registers the ten leaves directly; environment-dependent support checks determine whether a registered leaf can execute.

## Key Takeaways

- `vkGetDrmDisplayEXT` is tested as an information query. It must accept a valid connector without DRM master permission, reject invalid or unowned connectors, and return a usable display handle only on success.
- `vkAcquireDrmDisplayEXT` is tested as the ownership transition. It must use the physical device's DRM fd, require DRM master permissions, and reject invalid or insufficiently owned descriptors with the specified error results.
- `vkReleaseDisplayEXT` closes the successful acquire path. The test does not render; it checks that the display can be identified, acquired, and released in order.
- A skipped case caused by missing DRM infrastructure is different from a failed Vulkan result check. The test reports those environment limitations as `NotSupportedError`.

## Source Reference Appendix

| Topic | Source link | Why it matters |
|---|---|---|
| Test index and dispatch | [`DrmTestIndex` and `iterate`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L58-L171) | Maps each registered leaf to its implementation method. |
| Required instance extensions | [`createInstanceWithAcquireDrmDisplay`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L179-L195) | Defines the extension prerequisites and skip behavior. |
| DRM device discovery | [`getDrmFdPtr`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L203-L230) | Maps the selected physical device to its DRM primary node. |
| Connector and CRTC helpers | [`getConnectedConnectorId` and `getValidCrtcId`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L239-L283) | Select connected connectors and a CRTC for DRM leases. |
| Master detection | [`isDrmMaster`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L286-L300) | Determines whether the environment can run master-dependent cases. |
| Display lookup cases | [`vkGetDrmDisplayEXT` tests](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L309-L483) | Covers valid, invalid-fd, invalid-connector, non-master, and unowned-connector lookup. |
| Acquisition cases | [`vkAcquireDrmDisplayEXT` tests](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L499-L662) | Covers successful acquisition and the invalid ownership cases. |
| Release case | [`testReleaseDisplayEXT`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L679-L712) | Checks the lookup, acquire, and release sequence. |
| Registration | [`createAcquireDrmDisplayTests`](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L750-L775) | Provides the exact test case names. |
| WSI dispatcher | [`createWsiTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L91) | Places the family at `wsi.acquire_drm_display`. |
| Vulkan specification | [`VK_EXT_acquire_drm_display` command descriptions](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L1604-L1676) | Defines fd association, master-permission, connector-ownership, acquisition, and release semantics. |
| Mustpass coverage | [`vk-default/wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L1-L10) | Lists all ten registered leaves in the default mustpass set. |
