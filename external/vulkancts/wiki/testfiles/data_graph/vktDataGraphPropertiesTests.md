# vktDataGraphPropertiesTests

This page documents the implementation file for the `dEQP-VK.data_graph.properties` tests.

## Overview

`vktDataGraphPropertiesTests.cpp` verifies data graph pipeline property-query entry points. It builds a TOSA-backed data graph pipeline using the same shared resource-generation path as the basic tests, queries available properties, and then queries property data either in a single call or one property at a time.

## Role of File

- **Registration file:** yes. It registers the direct children under `data_graph.properties`.
- **Implementation file:** yes. It implements available-property and get-property query tests.

## Source Code Links

| Item | Evidence |
|------|----------|
| `properties` root child registration | [vktDataGraphTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L43-L45) |
| Properties subgroup registration | [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L547-L551) |
| Shared support check delegation | [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L138-L146) |
| Property query implementation | [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L148-L270), [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L273-L501) |

## Registration Hierarchy

```text
data_graph.properties
├── available
└── get
```

## Test Families

### available — Available-property enumeration

`available` registers one case for each shared `TestParams` value and each query return mode (`COMPLETE`, `INCOMPLETE`) [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L506-L522). The implementation creates tensor resources, descriptor state, and a data graph pipeline, then calls `getDataGraphPipelineAvailablePropertiesARM` once to get the property count [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L148-L249). If there are properties, the complete path supplies enough storage and expects `VK_SUCCESS`; the incomplete path decrements the property count and expects `VK_INCOMPLETE` [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L256-L268).

### get — Property data queries

`get` registers one case for each shared `TestParams` value, two call-count modes (`SINGLE_CALL`, `MULTIPLE_CALLS`), and two return modes (`COMPLETE`, `INCOMPLETE`) [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L524-L545). The implementation first obtains the available property descriptors, then prepares `VkDataGraphPipelinePropertyQueryResultARM` entries [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L368-L395). In single-call mode it allocates one contiguous buffer for all returned data and verifies that every queried property buffer was written [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L397-L464). In multiple-call mode it queries one property at a time and checks for either success or `VK_INCOMPLETE` depending on the selected return mode [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L465-L499).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Available-property return mode | `COMPLETE` and `INCOMPLETE` [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L67-L77), [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L512-L520) |
| Get-property call-count mode | `SINGLE_CALL` and `MULTIPLE_CALLS` [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L61-L65), [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L529-L542) |
| Get-property return mode | `COMPLETE` and `INCOMPLETE` [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L67-L84), [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L534-L542) |
| Shared graph parameters | Instruction set, session memory, resource cardinality, stride modes, shuffled bindings, tiling, sparse constants, and format strings are produced by `getTestParamsVariations()` [vktDataGraphTestUtil.cpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L175-L220) |
| Generated case names | Operators combine query mode text with the shared parameter name [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L86-L136) |

## Support and Feature Requirements

Both property test parameter wrappers delegate to `TestParams::checkSupport()` [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L138-L146). That shared check requires `VK_ARM_data_graph`, `VK_ARM_tensors`, `dataGraph`, `dataGraphShaderModule`, `tensors`, and `shaderTensorAccess`, with conditional `tensorNonPacked` support for non-packed resources [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L220-L256).

## Verification Methods

- The `available` family checks `VK_SUCCESS` for complete enumeration and `VK_INCOMPLETE` when the test intentionally supplies room for fewer properties than reported [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L256-L268).
- The `get` family rejects text properties that report `dataSize == 0` because there would be no room for a NUL terminator [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L403-L410), [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L467-L473).
- In single-call mode, the test initializes the result buffer to `0x7F`, calls `getDataGraphPipelinePropertiesARM`, and fails if any returned property data range still contains the initializer byte [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L426-L463).
- In incomplete modes, the implementation reduces available storage where possible and checks for `VK_INCOMPLETE` [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L412-L424), [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L475-L493).

## Test Principles

- Cover both enumeration and retrieval APIs for data graph pipeline properties.
- Exercise complete and intentionally incomplete return paths for available properties and property data.
- Reuse real data graph pipeline construction before property queries, rather than querying an uninitialized or synthetic object [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L222-L249), [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L347-L371).

## Notes and Uncertainties

When the implementation reports zero available properties, both property families return pass early [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L251-L254), [vktDataGraphPropertiesTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L376-L379). This page does not claim any minimum property count.