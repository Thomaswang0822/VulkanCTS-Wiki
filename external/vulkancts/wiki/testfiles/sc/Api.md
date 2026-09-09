## Overview

**Core question:** Does a Vulkan SC implementation expose only the API surface and device state permitted by Vulkan SC 1.0?

- This page documents the API tests implemented in [`vktSafetyCriticalApiTests.cpp`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp), registered below `sc.api`.
- The six fixed cases check inaccessible commands, absent extensions, forbidden feature and property bits, and the allow-list for `VK_KHR_*` and `VK_EXT_*` extensions.
- These are host-side queries through the Vulkan interfaces; there is no shader, draw, dispatch, resource, or numerical-output component.
- The default Vulkan SC mustpass selects exactly `allowed_extensions`, `forbidden_core_commands`, `forbidden_core_extensions`, `forbidden_features`, `forbidden_promoted_commands`, and `forbidden_properties` ([`sc.txt#L1-L6`](../../../mustpass/main/vksc-default/sc.txt#L1-L6)).

## Background Knowledge

- **Vulkan SC API surface.** Vulkan SC is a safety-critical variant with a constrained command and extension surface. This matters because a command or extension being discoverable is itself the observable condition under test.
- **Device features and properties.** Features are capability bits reported for a physical device, while properties describe device limits or characteristics. The tests query selected fields and require particular values; they do not enable features or exercise the associated resource paths.
- **Dispatch lookup.** `vkGetDeviceProcAddr` returns a function pointer when a device command is accessible. The command cases use a null pointer as the expected result for commands removed from the Vulkan SC surface.

## Registration Hierarchy

```text
sc.api
├── allowed_extensions
├── forbidden_core_commands
├── forbidden_core_extensions
├── forbidden_features
├── forbidden_promoted_commands
└── forbidden_properties
```

The root is created by `createTests`, which calls `createTestGroup(testCtx, "sc", createChildren)` ([`vktSafetyCriticalTests.cpp#L45-L65`](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L65)). The `api` group is created by `createSafetyCriticalAPITests` ([`vktSafetyCriticalApiTests.cpp#L344-L360`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L344-L360)). The six leaves are the exact names listed in mustpass; the registration validator cannot infer these API leaf entries from the page tree alone, so mustpass lines are the authoritative coverage check.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| API case | `allowed_extensions`, `forbidden_core_commands`, `forbidden_core_extensions`, `forbidden_features`, `forbidden_promoted_commands`, `forbidden_properties` | Selects which Vulkan SC contract is queried. Each is a separate fixed test case, not a generated combination matrix. | [`vktSafetyCriticalApiTests.cpp#L344-L360`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L344-L360); [`sc.txt#L1-L6`](../../../mustpass/main/vksc-default/sc.txt#L1-L6) |
| Command set | Source-defined command lists | Determines which device procedure names must be inaccessible. | [`vktSafetyCriticalApiTests.cpp#L41-L77`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L41-L77); [`vktSafetyCriticalApiTests.cpp#L147-L203`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L147-L203) |
| Forbidden extension set | Source-defined `coreExtensions` set | Determines which advertised device extensions fail the negative check. | [`vktSafetyCriticalApiTests.cpp#L79-L145`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L79-L145) |
| Allowed extension set | Source-defined `extensions` set | Determines the complete permitted set for advertised names beginning with `VK_KHR` or `VK_EXT`. | [`vktSafetyCriticalApiTests.cpp#L249-L340`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L249-L340) |
| Forbidden feature fields | Ten sparse-related `VkPhysicalDeviceFeatures` fields | Requires each selected field to be `VK_FALSE`. | [`vktSafetyCriticalApiTests.cpp#L205-L229`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L205-L229) |
| Forbidden property fields | Five `sparseProperties` fields | Requires each selected `VkPhysicalDeviceSparseProperties` field to be `VK_FALSE`. | [`vktSafetyCriticalApiTests.cpp#L232-L247`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L232-L247) |

## Behavior Parameters

The primary behavioral axis is the fixed API case. The cases are independent checks over different queried aspects of the Vulkan SC device interface.

### `forbidden_core_commands` — removed core commands stay inaccessible

The test asks the device interface for each name in its source-defined vector, including memory, shader-module, descriptor-pool, query-pool, sparse-resource, command-pool, and swapchain commands. Any non-null function pointer raises a `TestError`; only null pointers produce the pass status ([`vktSafetyCriticalApiTests.cpp#L41-L77`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L41-L77)).

### `forbidden_core_extensions` — promoted or otherwise forbidden extensions are not advertised

The test enumerates cached device extension properties and fails if an advertised name is in the source-defined set of extensions that Vulkan SC explicitly forbids ([`vktSafetyCriticalApiTests.cpp#L79-L145`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L79-L145)). This is an advertisement check, not a command-pointer check.

### `forbidden_promoted_commands` — promoted extension entry points stay inaccessible

A second command list covers `KHR` entry points corresponding to promoted functionality, such as memory-requirement queries, physical-device queries, render-pass commands, semaphore operations, and indirect-count commands. The same `vkGetDeviceProcAddr` null-pointer condition is required ([`vktSafetyCriticalApiTests.cpp#L147-L203`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L147-L203)).

### `forbidden_features` — selected sparse features are false

The test checks `shaderResourceResidency`, `sparseBinding`, the sparse-residency fields, and `sparseResidencyAliased` in `context.getDeviceFeatures()`. A `VK_TRUE` value for any one of these fields fails the case; all checked fields must be `VK_FALSE` ([`vktSafetyCriticalApiTests.cpp#L205-L229`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L205-L229)).

### `forbidden_properties` — selected sparse properties are false

The test checks five fields under `context.getDeviceProperties().sparseProperties`: the standard 2D, multisample 2D, and 3D block-shape flags, aligned mip size, and nonresident-strict behavior. Any true value fails ([`vktSafetyCriticalApiTests.cpp#L232-L247`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L232-L247)).

### `allowed_extensions` — advertised KHR and EXT names are allow-listed

The test enumerates cached device extensions. Names that do not begin with `VK_KHR` or `VK_EXT` are ignored. Every name with either prefix must occur in the source-defined allow-list; an absent name fails, while an empty or fully allowed matching set passes ([`vktSafetyCriticalApiTests.cpp#L249-L340`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L249-L340)).

## Shader Analysis

This page has no shader component. The implementation performs only host-side command, extension, feature, and property queries; no shader code or shader-generated result participates in these six cases ([`vktSafetyCriticalApiTests.cpp#L41-L360`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L41-L360)).

## Runtime Execution and Result Checking

- The CTS context supplies the device, physical device, and instance/device interfaces used by the checks. The API test factory binds each function to a fixed leaf under `sc.api` ([`vktSafetyCriticalApiTests.cpp#L344-L360`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L344-L360)).
- Command cases call `getDeviceProcAddr` for each literal command name. A non-null pointer is an immediate failure; the loop must complete with null for every listed name ([`vktSafetyCriticalApiTests.cpp#L66-L76`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L66-L76), [`vktSafetyCriticalApiTests.cpp#L192-L202`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L192-L202)).
- Extension cases obtain cached physical-device extension properties. The forbidden case rejects any member of its negative set; the allowed case rejects any `VK_KHR` or `VK_EXT` name absent from its positive set ([`vktSafetyCriticalApiTests.cpp#L132-L145`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L132-L145), [`vktSafetyCriticalApiTests.cpp#L322-L340`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L322-L340)).
- Feature and property cases read the context’s already reported state and throw on any forbidden true bit ([`vktSafetyCriticalApiTests.cpp#L205-L247`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L205-L247)).
- A passing case returns a `TestStatus::pass` message. There is no shader output, buffer readback, tolerance, or cross-case aggregate comparison in this implementation.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `forbidden_core_commands` | A removed core command is still exposed through device procedure lookup. |
| `forbidden_core_extensions` | A Vulkan SC-forbidden extension is advertised by the physical device. |
| `forbidden_promoted_commands` | A promoted `KHR` entry point remains exposed. |
| `forbidden_features` | At least one checked sparse-related feature is reported `VK_TRUE`. |
| `forbidden_properties` | At least one checked sparse-related property is reported `VK_TRUE`. |
| `allowed_extensions` | A `VK_KHR` or `VK_EXT` device extension is advertised but is not in the implementation’s Vulkan SC allow-list. |

### Cause Analysis

#### API exposure or reported-state mismatch

**Possible failure symptoms:** The command cases report that a named procedure “should not be accessible”; extension cases report a forbidden or disallowed extension; feature/property cases identify a field that must be false ([`vktSafetyCriticalApiTests.cpp#L69-L76`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L69-L76), [`vktSafetyCriticalApiTests.cpp#L137-L145`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L137-L145), [`vktSafetyCriticalApiTests.cpp#L207-L246`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L207-L246)).

**Possible implementation causes:** The ICD or loader may expose an entry point that the Vulkan SC profile requires to be unavailable, advertise an extension outside the profile’s permitted set, or report a forbidden capability bit. This page localizes the mismatch to API discovery or reported physical-device state; it does not establish whether the defect is in the loader, ICD, or underlying device without further investigation.

## Case Pruning

### Requirement-based pruning

No per-case support or feature-pruning branch appears in `createSafetyCriticalAPITests` or in the six test functions. The factory unconditionally registers all six cases ([`vktSafetyCriticalApiTests.cpp#L344-L360`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L344-L360)). A test may fail because the observed implementation state violates its contract; that is not the same as a source-defined skip.

### Design-based pruning

The command and extension lists are deliberately finite source-defined sets. The allow-list applies only to advertised names beginning with `VK_KHR` or `VK_EXT`; other extension-name prefixes are intentionally outside that check ([`vktSafetyCriticalApiTests.cpp#L327-L336`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L327-L336)). Unlisted commands, fields, and extensions are outside this page’s documented coverage rather than implicitly proven compliant.

## Key Takeaways

- `sc.api` tests the Vulkan SC interface contract through six fixed host-side queries, not through rendering or compute workloads.
- Negative command checks require `vkGetDeviceProcAddr` to return null for every listed removed or promoted entry point.
- Extension conformance is checked in two directions: explicitly forbidden names must not be advertised, and every advertised `VK_KHR`/`VK_EXT` name must belong to the allow-list.
- The feature and property cases assert false values for selected sparse-related fields; they do not test sparse-resource execution.
- The default mustpass contains exactly these six leaves, so the source lists and `sc.txt` define the tested boundary rather than a claim about all Vulkan API surface.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createSafetyCriticalAPITests` | [`vktSafetyCriticalApiTests.cpp#L344-L362`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L344-L362) | Creates `api` and registers the six exact leaf names. |
| Command accessibility checks | [`vktSafetyCriticalApiTests.cpp#L41-L77`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L41-L77) | Defines the removed-core command list and null-pointer pass condition. |
| Promoted command checks | [`vktSafetyCriticalApiTests.cpp#L147-L203`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L147-L203) | Defines the promoted-command list and its lookup condition. |
| Extension checks | [`vktSafetyCriticalApiTests.cpp#L79-L145`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L79-L145), [`#L249-L340`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L249-L340) | Defines forbidden and allowed extension sets and enumeration logic. |
| Feature/property checks | [`vktSafetyCriticalApiTests.cpp#L205-L247`](../../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L205-L247) | Defines the exact fields required to be false. |
| `sc` root registration | [`vktSafetyCriticalTests.cpp#L45-L65`](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L65) | Places `api` below the Vulkan SC package root. |
| Default mustpass | [`sc.txt#L1-L6`](../../../mustpass/main/vksc-default/sc.txt#L1-L6) | Confirms the exact six default paths. |
