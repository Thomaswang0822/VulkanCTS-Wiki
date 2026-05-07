# vktPipelineExecutablePropertiesTests.cpp

## Overview

[`vktPipelineExecutablePropertiesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1) implements the [`executable_properties`](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1217) topic group. It verifies VK_KHR_pipeline_executable_properties functionality, testing queries for pipeline executable properties, statistics, and internal representations.

## Role

Implementation file.

## Source Code

- Primary source: [`vktPipelineExecutablePropertiesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1)
- Header: [`vktPipelineExecutablePropertiesTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.hpp#L1)

## Registration Path

[`createExecutablePropertiesTests()`](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1213) returns the `executable_properties` group, attached under each variant root by `createChildren()`.

**Variant coverage**: Not shader-object, VK only.

## Test Hierarchy

```text
executable_properties
└── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| Executable properties test | Verifies pipeline executable property queries return valid results |
| Executable statistics test | Verifies pipeline executable statistic queries return valid results |
| Executable internal representations test | Verifies pipeline executable internal representation queries |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Non-shader-object variant types |
| Pipeline type | Enum | Graphics, compute |
| Query type | Enum | Properties, statistics, internal representations |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_KHR_pipeline_executable_properties` | Primary extension for all tests |

## Verification Methods

- **Property query verification**: Verify that `vkGetPipelineExecutablePropertiesKHR` returns valid executable info
- **Statistics query verification**: Verify that `vkGetPipelineExecutableStatisticsKHR` returns valid statistics
- **Internal representation verification**: Verify that `vkGetPipelineExecutableInternalRepresentationsKHR` returns valid data
- **Consistency check**: Verify that reported executable count matches between property and statistic queries

## Notes

- Pipeline executable properties are implementation-exposed metadata; test verifies structure validity rather than specific values
- Excluded from shader-object variants
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
