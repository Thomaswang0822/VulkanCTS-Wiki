## Overview

**Core question:** Does a data graph pipeline report its available properties and return each requested property through both complete and deliberately incomplete queries?

- This page covers `data_graph.properties`, implemented by `vktDataGraphPropertiesTests.cpp` and registered below the `available` and `get` test families [propertiesTestsGroup()](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L547-L551).
- `available` checks the two-call count-and-array form of `vkGetDataGraphPipelineAvailablePropertiesARM`; `get` first obtains the property list and then queries property data with either one call for the whole array or one call per property [availablePropertiesTests()](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L506-L522), [getPropertiesTests()](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L524-L545).
- Every generated case uses the current TOSA provider and a valid generated data graph pipeline. The generated suffix records graph shape, memory and tensor-layout choices, while the query prefix records complete/incomplete and, for `get`, single-call/multiple-call retrieval.
- The test checks the API return code and, for the single-call `get` path, checks that each supplied result buffer was overwritten. It does not compare property contents with a fixed string or binary format.

## Background Knowledge

- `vkGetDataGraphPipelineAvailablePropertiesARM` is an enumeration query. A call with `pProperties == NULL` returns the number of available property enums; a call with storage returns the number written and may return `VK_INCOMPLETE` when the supplied capacity is smaller [Vulkan data graph properties](../../../../vulkan-docs/src/chapters/VK_ARM_data_graph/graphs.adoc#L1120-L1146).
- `VkDataGraphPipelinePropertyQueryResultARM` describes one property request. A size-only query uses `pData == NULL`; a data query supplies a buffer and receives the number of bytes written in `dataSize`. Text data is UTF-8 and includes a terminating NUL when the buffer is nonzero [property query result](../../../../vulkan-docs/src/chapters/VK_ARM_data_graph/graphs.adoc#L1210-L1244).
- `VK_INCOMPLETE` means that the caller's array or byte buffer was too small for the complete result. It is different from a failed query: the implementation may have written the portion that fits, and the caller must use the returned count or size to interpret that partial result.

## Registration Hierarchy

```text
 data_graph.properties
 ├── available
 └── get
```

## Parameter Dimensions and Observed Values

The source forms `TestParams` as a Cartesian product, then keeps only valid combinations and expands each supported provider format. The mustpass file contains 636 distinct graph-parameter suffixes, with 1,272 `available` cases and 2,544 `get` cases [parameter generation](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [variation filtering](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L175-L219), [mustpass entries](../../../mustpass/main/vk-default/data-graph.txt#L6361-L10176).

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Instruction set | `tosa` | Selects the TOSA provider; source spelling is `TOSA`, rendered lower-case in the case name. | [provider dispatch](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp#L44-L74), [case-name formatter](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L80-L116) |
| Graph shape | `oneIn`, `manyIn`; `oneOut`, `manyOut`; `noConst`, `manyConst` | Selects the provider-backed graph family and the number of resource classes present. The provider currently exposes five supported shapes: one-layer max-pool, one-layer convolution, two-layer max-pool, two-layer convolution, and add/sub. | [TOSA provider selection](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1203-L1275) |
| Session memory | `noSession`, `session` | Selects whether the chosen TOSA graph uses session memory; it also participates in provider selection. | [default variation dimensions](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [provider selection](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1210-L1238) |
| Format | `i32`, `i8`, `fp16`, `fp32`, `i8i8i32`, `fp16fp16fp16`, `fp32fp32fp32` | Selects the provider's format combination for the chosen graph shape. The available strings depend on that shape. | [TOSA format lists](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L235-L253), [provider format selection](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1206-L1240) |
| Input, output, and constant strides | `implicitIn`, `packedIn`, `notPackedIn`; `implicitOut`, `packedOut`, `notPackedOut`; `implicitConst`, `packedConst` | Changes tensor stride descriptions used while creating the graph pipeline. Constants never use `notPackedConst` in the generated names. | [stride dimensions](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L113-L162), [case-name formatter](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L80-L114) |
| Binding order | `orderedBindings`, `unorderedBindings` | Keeps descriptor bindings in source order or shuffles the bindings before pipeline construction. | [case-name formatter](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L96-L97), [TOSA resource setup](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L76-L82) |
| Tensor tiling | `linearTiling`, `optimalTiling` | Selects the tensor tiling passed to tensor descriptions for non-constant resources. | [tiling generation](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [provider validation](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L57-L66) |
| Constant sparsity | optional `sparseConstants` suffix | Requests and validates sparsity metadata for constant resources. The suffix appears only in supported constant-bearing combinations. | [sparsity generation](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [sparsity validation](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L108-L134) |
| Available-property return mode | `complete`, `incomplete` | Controls whether the second available-property call receives the full capacity or one fewer enum slot. | [available registration](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L512-L520), [available query](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L243-L270) |
| Property-data call count | `singleCall`, `multiCalls` | Selects one `vkGetDataGraphPipelinePropertiesARM` call for all properties or one call for each property. | [get registration](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L529-L541), [retrieval branches](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L397-L499) |
| Property-data return mode | `complete`, `incomplete` | Controls whether each data buffer has the full queried size or, where possible, one fewer byte. | [incomplete sizing](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L401-L424), [result-code checks](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L438-L497) |

## Behavior Parameters

The primary behavioral axis is the query operation. The graph parameters provide the pipeline under test, while the registered query values alter the API contract being exercised.

### available: enumerate property identifiers

The test builds a TOSA-backed pipeline, calls `vkGetDataGraphPipelineAvailablePropertiesARM` with a null property array to obtain `numProperties`, allocates that many enums, and repeats the call. In `complete`, the second call uses the full count and requires `VK_SUCCESS`. In `incomplete`, it decrements the count and requires `VK_INCOMPLETE`; the implementation therefore tests both capacity outcomes [available query implementation](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L148-L270).

### get: retrieve property data

The test first enumerates the available property enums, initializes one `VkDataGraphPipelinePropertyQueryResultARM` per enum, and performs a size query with `pData == nullptr`. It allocates result storage from the returned sizes, then retrieves data. `singleCall` passes all query structures in one call; `multiCalls` passes one structure per call [get query setup](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L368-L399), [retrieval branches](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L397-L499).

For `complete`, the test keeps each returned size and requires `VK_SUCCESS`. For `incomplete`, it reduces each size by one only when that leaves storage, and requires `VK_INCOMPLETE`. A one-byte query is skipped in the multiple-call incomplete loop because the source cannot reduce it further; if the aggregate reduced size is zero in the single-call path, the test reports `NotSupportedError` because that incomplete case cannot be formed [incomplete sizing and handling](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L401-L424), [multiple-call handling](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L465-L498).

## Shader Analysis

This page uses the reviewed no-walkthrough exception. The TOSA provider supplies a shader module, and the property tests attach it while building a valid data graph pipeline [pipeline construction](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L222-L241), [provider dispatch](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp#L44-L62). The tests do not dispatch the graph, inspect shader instructions, or validate shader outputs: after pipeline construction, their observable work is the host-side available-property and property-data queries and their return-code/overwrite checks [available query](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L243-L270), [property-data query](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L368-L501). The shader therefore establishes a valid pipeline handle but is not part of the property-query behavior being tested, so a representative shader walkthrough would be misleading.

## Runtime Execution and Result Checking

- Each case asks `DataGraphTestProvider` for a TOSA test. The provider creates the graph description and shader module; the test creates tensor descriptions, tensor memory and views for tensor resources, initializes tensor or host data, builds a descriptor set for tensors, and builds a `DataGraphPipelineWrapper` pipeline [available setup](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L148-L241), [provider dispatch](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp#L44-L62).
- The test does not dispatch the graph. It only needs the created pipeline handle in `VkDataGraphPipelineInfoARM` for the two property-query commands [pipeline info setup](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L241-L249), [get pipeline setup](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L347-L374).
- `available` performs a null-array count query followed by an enum-array query. When the count is zero, it returns pass without a second query [available count path](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L243-L255).
- `get` repeats the available-property count/array sequence. When no properties are available, it returns pass. Otherwise, it size-queries every property, allocates one contiguous byte array for the `singleCall` path, and points each query structure at its slice [get size query and allocation](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L373-L439).
- In the `singleCall` path, the byte array starts filled with `0x7F`. After retrieval, the test scans every supplied result range and fails with `Property data not written` if any byte still has the initialization value. This is an overwrite check, not a semantic comparison of the returned property [overwrite check](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L426-L463).
- `VK_CHECK` accepts only the expected success result; `VK_CHECK_INCOMPLETE` accepts the incomplete result expected from a deliberately undersized array or data buffer [available result checks](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L258-L268), [get result checks](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L438-L497).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `available_complete` | The available-property query returned a status other than `VK_SUCCESS`. The test does not independently compare the returned count or property-enum values. |
| `available_incomplete` | The available-property query with a deliberately short enum-array capacity returned a status other than `VK_INCOMPLETE`. The test does not independently compare the returned count or enum values. |
| `get_singleCall_complete` | The all-properties data query returned the wrong status, or the implementation left a supplied result range containing the sentinel bytes. |
| `get_singleCall_incomplete` | The all-properties query did not report `VK_INCOMPLETE` for reduced storage, or it failed to write the supplied partial ranges. |
| `get_multiCalls_complete` | One per-property data-retrieval query returned a status other than `VK_SUCCESS`. |
| `get_multiCalls_incomplete` | A reduced per-property query returned a status other than `VK_INCOMPLETE`; one-byte properties are intentionally not reduced in this branch. |

### Cause Analysis

#### Available-property enumeration status

**Possible failure symptoms:** The full-capacity `available` case fails its `VK_SUCCESS` check, or the short-capacity case fails its `VK_INCOMPLETE` check.

**Possible implementation causes:** The implementation may not apply the available-property array-capacity rule from the Vulkan data graph properties specification, or it may return a result code inconsistent with the number of enums written. Source-level investigation is needed to distinguish the cause.

#### Property-data retrieval status

**Possible failure symptoms:** A `get` case fails a `VK_SUCCESS` or `VK_INCOMPLETE` check for all-properties or one-property retrieval.

**Possible implementation causes:** The implementation may mishandle `dataSize` as input capacity and output byte count, or may not apply the partial-data rule for an undersized buffer. The specification requires `VK_INCOMPLETE` when not all property bytes fit [property data contract](../../../../vulkan-docs/src/chapters/VK_ARM_data_graph/graphs.adoc#L1231-L1244). Source-level investigation is needed for a more specific cause.

#### Property-data overwrite

**Possible failure symptoms:** A `get_singleCall_*` case reports `Property data not written` because at least one byte in a supplied result range remains `0x7F`.

**Possible implementation causes:** The implementation may have failed to write a requested property range, or the host-side query descriptors may not have described the returned buffers correctly. The test source provides the symptom but does not identify which implementation layer caused it [overwrite check](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L452-L462).

## Case Pruning

### Requirement-based pruning

- `TestParams::checkSupport` requires `VK_ARM_data_graph` and `VK_ARM_tensors`, plus the `dataGraph`, `dataGraphShaderModule`, `tensors`, and `shaderTensorAccess` features. Cases with any missing requirement are not supported [support checks](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L251).
- A parameter set using any `notPacked` resource requires the `tensorNonPacked` feature. The support check rejects it when that feature is absent [non-packed support gate](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L253-L256).
- The variation generator removes invalid combinations before registration: optimal tiling with explicit strides, non-packed constant strides, explicit strides for absent resource classes, sparse constants when there are no constants, and any graph with no outputs [validity rules](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L172).
- The TOSA provider returns no formats for unsupported graph-shape/session combinations, so those combinations do not become cases. It also validates that the selected test actually contains the requested resource cardinalities, tiling, strides, and sparsity metadata [provider formats](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1206-L1241), [provider validation](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L37-L134).

### Design-based pruning

- The available-property incomplete variant reduces the reported capacity by one, while the complete variant uses the full capacity [available modes](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L258-L268).
- The get incomplete variants reduce each queried data size by one when possible. The multiple-call implementation skips a one-byte property rather than constructing a zero-byte reduction; the single-call implementation marks an all-zero reduced allocation as unsupported [get incomplete modes](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L401-L424), [multiple-call reduction](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L475-L485).
- The source registers query modes as test-case name prefixes, not as deeper registered hierarchy components. The parser-visible hierarchy therefore stops at `available` and `get`; generated case dimensions remain in the leaf names listed in mustpass [registration loops](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L506-L545).

## Key Takeaways

- `available` tests both the count query and the array-capacity rule for `vkGetDataGraphPipelineAvailablePropertiesARM`.
- `get` tests both size discovery and data retrieval, with one-call and per-property call patterns.
- Complete cases require `VK_SUCCESS`; deliberately short cases require `VK_INCOMPLETE`, which means the result was truncated to caller-provided capacity.
- The single-call data path uses `0x7F` sentinels to detect unwritten result ranges. It does not validate the meaning of the returned creation log or identifier.
- TOSA graph selection and tensor support gates determine which generated graph cases exist; they are setup and pruning dimensions for the property queries, not shader behaviors documented on this page.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| `propertiesTestsGroup()` | [registration](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L547-L551) | Registers the `available` and `get` test families. |
| `availablePropertiesTests()` | [available registration](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L506-L522) | Adds `complete` and `incomplete` cases for every valid generated parameter set. |
| `getPropertiesTests()` | [get registration](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L524-L545) | Adds single/multiple-call and complete/incomplete combinations. |
| `availablePropertiesTest()` | [available implementation](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L148-L270) | Builds the pipeline, queries available property enums, and checks return modes. |
| `getPropertiesTest()` | [get implementation](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L273-L501) | Performs size queries, data retrieval, result-code checks, and overwrite checking. |
| `TestParams::checkSupport()` | [support gate](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L257) | Defines extension, feature, and non-packed tensor requirements. |
| `getTestParamsVariations()` | [parameter generation](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [filtering](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L219) | Defines the generated matrix and removes invalid combinations. |
| `DataGraphTestProviderTosa` | [provider selection](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1203-L1275) | Maps supported graph shapes and format strings to TOSA implementations. |
| `VkDataGraphPipelinePropertyQueryResultARM` | [Vulkan contract](../../../../vulkan-docs/src/chapters/VK_ARM_data_graph/graphs.adoc#L1210-L1246) | Defines property data size, text termination, and incomplete-result semantics. |
| `data-graph.txt` | [mustpass prefixes](../../../mustpass/main/vk-default/data-graph.txt#L6361-L10176) | Confirms the `data_graph.properties.available.*` and `data_graph.properties.get.*` generated paths. |
