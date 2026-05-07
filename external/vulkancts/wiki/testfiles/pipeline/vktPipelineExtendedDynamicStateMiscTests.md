# vktPipelineExtendedDynamicStateMiscTests.cpp

## Overview

[`vktPipelineExtendedDynamicStateMiscTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L1) implements the [`misc`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L798) subgroup under `extended_dynamic_state`. It verifies miscellaneous extended dynamic state behaviors that don't fit in the main EDS test file, including edge cases and interaction tests.

## Role

Implementation file. Nested subgroup registered under `extended_dynamic_state`.

## Source Code

- Primary source: [`vktPipelineExtendedDynamicStateMiscTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L1)
- Header: [`vktPipelineExtendedDynamicStateMiscTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.hpp#L1)

## Registration Path

[`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795) returns the `misc` group, added to the `extended_dynamic_state` group.

**Variant coverage**: Not extra shader-object, VK only.

## Test Hierarchy

```text
extended_dynamic_state
└── misc
    └── {test_case}
```

## Test Families

| Family | Description |
|---|---|
| EDS misc tests | Verifies miscellaneous extended dynamic state edge cases and interactions |

## Parameter Dimensions

| Parameter | Source | Values |
|---|---|---|
| PipelineConstructionType | Parameter | Non-extra-shader-object variant types |

## Support/Feature Requirements

| Requirement | Context |
|---|---|
| `VK_EXT_extended_dynamic_state` | Required for EDS1 misc tests |
| `VK_EXT_extended_dynamic_state3` | Required for EDS3 misc tests |

## Verification Methods

- **Rendering comparison**: Set state dynamically, render, compare against expected output
- **Edge case verification**: Verify edge cases in dynamic state interaction

## Notes

- This file provides the `misc` subgroup nested under `extended_dynamic_state`
- VK only (guarded by `CTS_USES_VULKANSC` exclusion)
