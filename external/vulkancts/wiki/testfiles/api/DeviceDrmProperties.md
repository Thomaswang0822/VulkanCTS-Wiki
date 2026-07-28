## Overview

**Core question:** When `VK_EXT_physical_device_drm` reports DRM primary and render major/minor node numbers, do those numbers correspond to real DRM device files visible on the host system?

- Covers the `api.device_drm_properties` test family, registered as `dEQP-VK.api.device_drm_properties.drm_files_exist` in the default `api` mustpass.
- Implemented in [`vktApiDeviceDrmPropertiesTests.cpp`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L1) for non-VulkanSC builds. The family has one direct test case leaf, `drm_files_exist`.
- The leaf queries `VkPhysicalDeviceDrmPropertiesEXT` through the `pNext` chain of `VkPhysicalDeviceProperties2`, then cross-checks each reported DRM major/minor pair against DRM device files enumerated via `tcu::LibDrm`.
- The page explains what the test verifies, how the two node categories (`primary` and `render`) are checked in parallel, what an unsupported outcome means, and which build and platform conditions gate the validation.

## Background Knowledge

- `VK_EXT_physical_device_drm` is a Vulkan extension that exposes DRM metadata for a physical device through `VkPhysicalDeviceDrmPropertiesEXT`, chained into `VkPhysicalDeviceProperties2::pNext`. The struct reports `hasPrimary` / `hasRender` flags plus the `primaryMajor` / `primaryMinor` and `renderMajor` / `renderMinor` pairs that identify the device's DRM node files.
- DRM primary and render nodes are Linux Direct Rendering Manager character device files under `/dev/dri/`. A primary node (`cardN`) is the legacy privileged entry point; a render node (`renderDN`) is the unprivileged entry point intended for compute and media workloads. A Vulkan implementation may expose either or both.
- `tcu::LibDrm` is the CTS framework helper that dynamically loads `libdrm` and enumerates DRM devices known to the host. The test uses it to translate a reported major/minor pair back to a real device file path.

## Registration Hierarchy

```text
api.device_drm_properties
└── drm_files_exist
```

The family is created by [`createDeviceDrmPropertiesTests()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L118-L121) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L96-L98) only inside `#ifndef CTS_USES_VULKANSC`. The single direct test case leaf `drm_files_exist` is added by [`createTestCases()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L110-L114) through `addFunctionCase(group, "drm_files_exist", checkSupport, testDeviceDrmProperties, TEST_FILES_EXIST)`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct test case leaf | `drm_files_exist` | Single executable case that runs the full DRM-properties query and file-existence check. | [`createTestCases()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L110-L114) |
| Internal test type enum | `TEST_FILES_EXIST` | Selects the file-existence validation branch inside `testDeviceDrmProperties()`. The only enum value defined in `TestType`. | [`enum TestType`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L42-L45) |
| DRM node category | `primary`, `render` | Two parallel validation targets driven by the `hasPrimary` / `hasRender` flags and corresponding major/minor fields. | [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L53-L78) |
| Property-query fill pattern | `0xaa` | Pre-fills `VkPhysicalDeviceProperties2` before the query so uninitialized extension fields are detectable during debugging. | [`testDeviceDrmProperties()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L84-L94) |

## Behavior Parameters

The primary behavioral axis is the DRM node category reported via `VK_EXT_physical_device_drm`: `primary` versus `render`. Each category has its own `has*` flag and major/minor pair, drives a separate `findDeviceNode()` lookup, and contributes independently to the final pass/skip decision. The test family registers only one test case leaf, but the leaf's validation logic is structured around these two parallel targets.

### `primary`: DRM primary node (`cardN`)

The implementation reports `hasPrimary = VK_TRUE` with a `primaryMajor` / `primaryMinor` pair. The test enumerates DRM devices via `tcu::LibDrm` and checks whether any available DRM device node character file has a `st_rdev` whose `major()` and `minor()` match the reported pair. The primary node is the legacy privileged DRM entry point.

If `hasPrimary` is `VK_FALSE`, the primary check is treated as already satisfied and no lookup is performed.

### `render`: DRM render node (`renderDN`)

The implementation reports `hasRender = VK_TRUE` with a `renderMajor` / `renderMinor` pair. The test performs the same `findDeviceNode()` lookup as for `primary`, but using the render pair. Render nodes are the unprivileged DRM entry points intended for compute and media workloads.

If `hasRender` is `VK_FALSE`, the render check is treated as already satisfied and no lookup is performed.

## Shader Analysis

No shader is involved in this test. The leaf performs only host-side Vulkan property queries and DRM device enumeration, and never submits any pipeline work.

## Runtime Execution and Result Checking

The leaf's flow is entirely host-side; no device work is submitted.

- Acquire the physical device from the `Context` and prepare two structures: `VkPhysicalDeviceDrmPropertiesEXT` zero-initialized, and `VkPhysicalDeviceProperties2` pre-filled with the `0xaa` pattern. The DRM struct is chained through `pNext` so the implementation writes DRM metadata into it during the query.
- Call `getPhysicalDeviceProperties2()` to populate both structures.
- Inside [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L53-L78), initialize `primaryFound` from `!hasPrimary` and `renderFound` from `!hasRender`, so an unreported category auto-satisfies its check.
- When `DEQP_SUPPORT_DRM` is defined and the build is not VulkanSC, enumerate DRM devices through [`tcu::LibDrm`](../../../../../framework/common/tcuLibDrm.hpp#L1), call `findDeviceNode()` once for the primary pair and once for the render pair, and free the enumerated device list. A successful lookup flips the corresponding `*Found` flag to `true`.
- Pass condition: at least one of `primaryFound` or `renderFound` is `true` after the lookups. The leaf returns `tcu::TestStatus::pass("Pass")`.
- Skip condition: both `primaryFound` and `renderFound` are `false`. The leaf throws `NotSupportedError`, which CTS logs as a skip rather than as a hard `TestStatus::failure`.

The lookup itself, in [`tcu::LibDrm::findDeviceNode()`](../../../../../framework/common/tcuLibDrm.cpp#L111-L135), iterates every available node of every enumerated DRM device, calls `stat()` on the node path, and matches the reported major/minor pair against `major(statBuf.st_rdev)` and `minor(statBuf.st_rdev)`. The lookup considers only character device files.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primary` | Driver reports `hasPrimary = VK_TRUE` with a major/minor pair that does not resolve to any DRM device file visible to the test process. |
| `render` | Driver reports `hasRender = VK_TRUE` with a major/minor pair that does not resolve to any DRM device file visible to the test process. |
| Both `primary` and `render` | Both reported pairs fail to resolve; `testFilesExist()` throws `NotSupportedError`. This is the only path that produces a non-pass outcome. |

A single unresolved reported category does not, by itself, change the test result: the other category's auto-satisfaction or successful lookup keeps the leaf passing.

### Cause Analysis

#### Reported DRM node not resolvable on the host

**Possible failure symptoms:** [`testFilesExist()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L53-L78) exits with `primaryFound` and `renderFound` both `false`, and the leaf throws `NotSupportedError` with the message `"Neither DRM primary nor render device files were found"`. CTS logs the case as `NotSupported`, a skip rather than a hard `TestStatus::failure`.

**Possible implementation causes:** The driver's `VK_EXT_physical_device_drm` reporting reflects host DRM state, so an unresolved node points to a mismatch between the implementation's view of the device and the test process's view of the same host. Possible reasons include:

- The reported major/minor pair does not match any character device under `/dev/dri/` that the test process can `stat()`.
- The DRM device is present but `libdrm` skips it because `libdrm` is too old or its discovery filters out the device.
- The test process lacks permissions to `stat()` the node.
- The build was compiled without `DEQP_SUPPORT_DRM`, in which case the lookup block is compiled out and any reported DRM flag automatically fails to resolve.

Distinguishing between a driver reporting wrong metadata and a test-environment visibility problem requires source-level investigation on the specific host.

## Case Pruning

### Requirement-based pruning

- The test case is registered only for non-VulkanSC builds: the parent `addChild(createDeviceDrmPropertiesTests(testCtx))` call is wrapped in `#ifndef CTS_USES_VULKANSC` in [`vktApiTests.cpp`](../../../modules/vulkan/api/vktApiTests.cpp#L96-L98), and the `testFilesExist()` DRM enumeration block carries the same guard.
- [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L47-L51) requires the `VK_EXT_physical_device_drm` device functionality. Implementations that do not expose the extension skip the case before any DRM enumeration runs.
- The DRM enumeration path requires the `DEQP_SUPPORT_DRM` build flag and a loadable `libdrm`. Builds without `DEQP_SUPPORT_DRM` skip the host enumeration and rely only on the `hasPrimary` / `hasRender` flags.
- DRM device enumeration is a Linux/DRM-platform concept; non-Linux platforms effectively skip the lookup block.

### Design-based pruning

- The test family registers exactly one test case leaf (`drm_files_exist`) and one internal test type (`TEST_FILES_EXIST`). Other plausible checks, such as matching the reported `primaryMajor` to a specific expected node path, are intentionally not generated.
- The auto-satisfaction of an unreported category is an intentional design choice: the test does not require the implementation to report both primary and render nodes, only that any reported node resolves to a real file.

## Key Takeaways

- The leaf cross-checks `VK_EXT_physical_device_drm` metadata against host-visible DRM device files, not against the Vulkan implementation's internal state.
- Primary and render node categories are independent validation targets; an unreported category auto-satisfies its check.
- The only non-pass outcome is `NotSupportedError`, thrown when both reported categories fail to resolve. A single unresolved reported category does not change the result.
- The DRM enumeration block is compiled out on VulkanSC builds or builds without `DEQP_SUPPORT_DRM`; on such builds the test relies entirely on the reported `hasPrimary` / `hasRender` flags.
- See `## Failure Meaning` for why an unresolved reported node is more likely a host-environment or test-visibility mismatch than a driver bug, and how to confirm it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDeviceDrmPropertiesTests()` | [vktApiDeviceDrmPropertiesTests.cpp#L118-L121](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L118-L121) | Public entry point that creates the `device_drm_properties` test family. |
| `createTestCases()` | [vktApiDeviceDrmPropertiesTests.cpp#L110-L114](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L110-L114) | Registers the single `drm_files_exist` test case leaf. |
| `checkSupport()` | [vktApiDeviceDrmPropertiesTests.cpp#L47-L51](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L47-L51) | Requires `VK_EXT_physical_device_drm`. |
| `testDeviceDrmProperties()` | [vktApiDeviceDrmPropertiesTests.cpp#L80-L108](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L80-L108) | Host-side query flow: zero the DRM struct, `0xaa`-fill `VkPhysicalDeviceProperties2`, chain via `pNext`, call `getPhysicalDeviceProperties2()`. |
| `testFilesExist()` | [vktApiDeviceDrmPropertiesTests.cpp#L53-L78](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L53-L78) | Auto-satisfies unreported categories, enumerates DRM devices, throws `NotSupportedError` if neither resolves. |
| `enum TestType` | [vktApiDeviceDrmPropertiesTests.cpp#L42-L45](../../../modules/vulkan/api/vktApiDeviceDrmPropertiesTests.cpp#L42-L45) | Defines the only internal test type, `TEST_FILES_EXIST`. |
| Parent registration | [vktApiTests.cpp#L96-L98](../../../modules/vulkan/api/vktApiTests.cpp#L96-L98) | Adds the family under `api` only for non-VulkanSC builds. |
| Mustpass entry | [api.txt#L269229](../../../mustpass/main/vk-default/api.txt#L269229) | Registers `dEQP-VK.api.device_drm_properties.drm_files_exist` in the default `api` mustpass. |
| `tcu::LibDrm` header | [tcuLibDrm.hpp](../../../../../framework/common/tcuLibDrm.hpp) | Framework helper that loads `libdrm` and exposes `getDevices()` / `findDeviceNode()`. |
| `findDeviceNode()` | [tcuLibDrm.cpp#L111-L135](../../../../../framework/common/tcuLibDrm.cpp#L111-L135) | Stats each DRM device node and matches the reported major/minor pair against `st_rdev`. |
