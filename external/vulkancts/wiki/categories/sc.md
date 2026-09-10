## Overview

The `sc` test category collects tests that check the Vulkan SC API contract, reserved-resource accounting, pipeline metadata, fault handling, object refresh, and application-parameter validation.

Vulkan SC differs from ordinary Vulkan in two ways that shape this category. First, applications declare resource capacity before device creation or object use. Second, several interfaces are intentionally narrower or more deterministic than their Vulkan counterparts. The tests therefore emphasize reported limits, reservation structures, creation-time validation, and explicit result codes rather than rendering output.

## Background Knowledge

- **Safety-critical device creation.** Vulkan SC applications provide reservation information through `pNext` structures. The implementation must reject configurations that exceed available or declared capacity and must accept configurations that fit.
- **Offline pipeline metadata.** Pipeline identifiers and cache data are inputs to the SC creation workflow. Their validity is checked through identifiers, cache headers, and reserved object counts, not through shader output.
- **Fault and refresh services.** Fault callbacks, fault-data queries, and object-refresh commands are host/API operations. They have their own result, synchronization, and completion contracts.
- **SC application parameters.** Application parameters are supplied through instance and device creation chains. The tests check both accepted and rejected keys or values and distinguish unsupported vendor-defined hooks from core validation.
- **Package and path boundary.** The SC package uses the `dEQP-VKSC` prefix and the `vksc-default/sc.txt` inventory. The generic registration helper in this repository expects ordinary `dEQP-VK` paths, so SC coverage is checked directly against the SC mustpass file.

## Category Structure

```text
sc
├── api
│   ├── allowed_extensions
│   ├── forbidden_core_commands
│   ├── forbidden_core_extensions
│   ├── forbidden_features
│   ├── forbidden_promoted_commands
│   └── forbidden_properties
├── device_object_reservation
├── pipeline_identifier
├── pipeline_cache
├── fault_handling
├── command_pool_memory_reservation
├── object_refresh
└── application_parameters
```

The root and its eight direct families are created by `vkt::sc::createTests` and `createChildren`; the `api` family then creates six leaves ([SC root registration](../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L45-L65), [API registration](../../modules/vulkan/sc/vktSafetyCriticalApiTests.cpp#L344-L362)).

## How the Families Fit Together

The families cover different stages of the safety-critical application lifecycle:

- **API restrictions** check what the implementation exposes and reports before any workload is submitted.
- **Reservations and creation metadata** cover device-object capacity, command-pool memory, pipeline identifiers, and pipeline-cache identity.
- **Runtime services** cover fault reporting, callback configuration, and refreshing implementation-owned object state.
- **Application parameters** validate the instance/device creation contract and its vendor-defined extension points.

Reservations and pipeline metadata are related because both constrain creation-time resources. Fault handling and object refresh are related because both operate after or around device work, but they validate different APIs. The API and application-parameter families remain host-side contract tests and do not depend on shader execution.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `api` and its six leaves | [Api](../testfiles/sc/Api.md) | Vulkan SC command, extension, feature, and property restrictions. |
| `device_object_reservation` | [DeviceReservation](../testfiles/sc/DeviceReservation.md) | Device-object reservation dimensions and acceptance/rejection results. |
| `pipeline_identifier` | [PipelineIdentifier](../testfiles/sc/PipelineIdentifier.md) | Identifier generation, retrieval, and validation. |
| `pipeline_cache` | [PipelineCache](../testfiles/sc/PipelineCache.md) | Vendor/device identity validation for safety-critical cache data. |
| `fault_handling` | [FaultHandling](../testfiles/sc/FaultHandling.md) | Fault-data queries, callbacks, and result handling. |
| `command_pool_memory_reservation` | [CommandPoolReservation](../testfiles/sc/CommandPoolReservation.md) | Command-pool memory reservation and allocation accounting. |
| `object_refresh` | [ObjectRefresh](../testfiles/sc/ObjectRefresh.md) | Object enumeration, refresh commands, and completion. |
| `application_parameters` | [ApplicationParameters](../testfiles/sc/ApplicationParameters.md) | Instance/device application-parameter validation. |

## Category Notes

- The default SC inventory contains 161 entries in `vksc-default/sc.txt`; the Level-3 pages explain the families behind those paths rather than treating the inventory as ordinary Vulkan coverage.
- Several families use setup shaders to create valid pipeline objects, but the SC oracle is host-side creation, reservation, cache, or result behavior. The relevant Level-3 pages state when shader execution is outside scope.
- Registration validation must preserve the `dEQP-VKSC` prefix. A report produced by the ordinary `dEQP-VK` validator is a tool limitation, not evidence that the SC pages or mustpass paths are missing.
