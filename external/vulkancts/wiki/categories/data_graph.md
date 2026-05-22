# Data Graph Tests

The `data_graph` category documents Vulkan CTS coverage for `VK_ARM_data_graph` tests. The inspected source registers one category root with three direct groups: `basic`, `cache`, and `properties`. The implementation builds TOSA-backed data graph pipelines over tensor resources, exercises pipeline creation and dispatch, verifies pipeline-cache behavior, and queries data graph pipeline properties.

## Registration Entry Point

The Vulkan test package registers the top-level category as `data_graph` in [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1398-L1400). The category root function creates a `TestCaseGroup` with the supplied name and adds the `basic`, `cache`, and `properties` child groups in [vktDataGraphTests.cpp](../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L39-L47).

## Subgroup Structure

```text
data_graph
├── basic
├── cache
└── properties
```

| Registered group | Level-3 page | Source registration | Role |
|------------------|--------------|---------------------|------|
| `data_graph` | [vktDataGraphTests](../testfiles/data_graph/vktDataGraphTests.md) | [vktDataGraphTests.cpp](../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L39-L47) | Root dispatcher for the category |
| `basic` | [vktDataGraphBasicTests](../testfiles/data_graph/vktDataGraphBasicTests.md) | [vktDataGraphBasicTests.cpp](../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L423-L427) | Basic pipeline creation and dispatch |
| `cache` | [vktDataGraphPipelineCacheTests](../testfiles/data_graph/vktDataGraphPipelineCacheTests.md) | [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L851-L855) | Data graph pipeline-cache hit, miss, and dispatch behavior |
| `properties` | [vktDataGraphPropertiesTests](../testfiles/data_graph/vktDataGraphPropertiesTests.md) | [vktDataGraphPropertiesTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L547-L551) | Available-property and property-data queries |

## File Inventory

| File | Documentation status | Notes |
|------|----------------------|-------|
| [vktDataGraphTests.cpp](../../modules/vulkan/data_graph/vktDataGraphTests.cpp) | [Level-3](../testfiles/data_graph/vktDataGraphTests.md) | Registers the category's direct child groups. |
| [vktDataGraphBasicTests.cpp](../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp) | [Level-3](../testfiles/data_graph/vktDataGraphBasicTests.md) | Registers and implements `create_pipeline` and `submit_pipeline`. |
| [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp) | [Level-3](../testfiles/data_graph/vktDataGraphPipelineCacheTests.md) | Registers and implements cache-aware creation and dispatch tests. |
| [vktDataGraphPropertiesTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp) | [Level-3](../testfiles/data_graph/vktDataGraphPropertiesTests.md) | Registers and implements property-query tests. |
| [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp) and [vktDataGraphTestUtil.cpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp) | Utility evidence | Define shared parameter generation, support checks, resource descriptors, and tensor verification. |
| [vktDataGraphTestProvider.hpp](../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp) and [vktDataGraphTestProvider.cpp](../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp) | Utility evidence | Select and validate provider-backed `DataGraphTest` implementations. |
| [tosa/vktDataGraphTosaUtil.hpp](../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp) | Utility evidence | Defines TOSA graph families and supported format strings. |
| [tosa/vktDataGraphTosaSpirv.cpp](../../modules/vulkan/data_graph/tosa/vktDataGraphTosaSpirv.cpp) | Utility evidence | Builds TOSA data graph SPIR-V source and graph entry points. |
| [tosa/vktDataGraphTosaReference.hpp](../../modules/vulkan/data_graph/tosa/vktDataGraphTosaReference.hpp) | Utility evidence | Provides reference operations used by TOSA-backed verification. |

## Recurring Test Families and Themes

### Basic pipeline lifecycle

The `basic` group has `create_pipeline` and `submit_pipeline` direct children. Creation tests cover shader-module versus binary input and optional compiler-control chaining [vktDataGraphBasicTests.cpp](../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L397-L411). Submit tests bind a data graph pipeline, bind tensor descriptors, dispatch with `cmdDispatchDataGraphARM`, and verify output resources [vktDataGraphBasicTests.cpp](../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L355-L390).

### Pipeline cache behavior

The `cache` group covers creation and submission through `VkPipelineCache`. Creation tests register single-call and multi-call paths with fill, hit, and miss sequences [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L796-L838). The implementation checks pipeline-creation feedback bits, compile-required results, null handles on expected failure, and early-return behavior in batched creation [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L289-L340), [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L390-L405), [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L540-L575).

### Pipeline property queries

The `properties` group covers available-property enumeration and property-data retrieval. It registers complete and incomplete return modes for available-property tests [vktDataGraphPropertiesTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L506-L522), and combines single-call or multiple-call retrieval with complete or incomplete return modes for `get` tests [vktDataGraphPropertiesTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L524-L545).

### TOSA-backed graph providers

The source currently dispatches instruction set `TOSA` to `DataGraphTestProviderTosa` [vktDataGraphTestProvider.hpp](../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp#L44-L62). The TOSA provider selects graph implementations based on resource cardinalities, including max-pool, convolution, two-layer max-pool, two-layer convolution, and add/sub families [vktDataGraphTosaUtil.hpp](../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1205-L1273). TOSA graph helpers assemble and validate SPIR-V binaries before returning them to pipeline creation paths [vktDataGraphTosaUtil.hpp](../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L121-L158).

## Recurring Parameter Dimensions

| Dimension | Evidence |
|-----------|----------|
| Instruction set | Shared generation defaults to `TOSA` [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440). |
| Session memory | Shared generation uses both `false` and `true` session-memory options [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440). |
| Resource cardinalities | Shared generation uses `allResourceCardinalityCombinations`, which covers input, output, and constant cardinalities except no-output cases [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L127-L132), [vktDataGraphTestUtil.cpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L166-L170). |
| Stride modes | Shared generation uses implicit, packed, and not-packed stride combinations, subject to validity rules for constants, missing resources, and optimal tiling [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L113-L125), [vktDataGraphTestUtil.cpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L172). |
| Binding order | Shared generation covers ordered and shuffled binding layouts [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), and names cases as ordered or unordered bindings [vktDataGraphTestUtil.cpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L80-L116). |
| Tensor tiling | Shared generation covers linear and optimal tiling; explicit strides are rejected for optimal tiling [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [vktDataGraphTestUtil.cpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L145). |
| Sparse constants | Shared generation includes sparse-constant variants, and provider validation requires actual constant sparsity metadata when requested [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [vktDataGraphTestProvider.cpp](../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L108-L138). |
| Format strings | TOSA graph implementations advertise format strings such as `i32`, `fp32`, `fp16`, `i8`, and multi-resource strings selected by provider logic [vktDataGraphTosaUtil.hpp](../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L235-L253), [vktDataGraphTosaUtil.hpp](../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1205-L1238). |

## Recurring Support Requirements

Shared `TestParams::checkSupport()` requires `VK_ARM_data_graph` and `VK_ARM_tensors`, then queries features and requires `dataGraph`, `dataGraphShaderModule`, `tensors`, and `shaderTensorAccess` [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L220-L251). When the selected parameter set uses non-packed resources, it additionally requires `tensorNonPacked` [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L253-L256). Cache tests add a separate requirement for `pipelineCreationCacheControl` before delegating to the shared support check [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L129-L146).

## Recurring Verification Methods

- Data graph creation paths check created pipeline and session handles [vktDataGraphBasicTests.cpp](../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L233-L248).
- Dispatch paths verify output tensor resources after command submission [vktDataGraphBasicTests.cpp](../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L375-L390), [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L769-L790).
- Shared tensor comparison uses SNR for floating-point data and exact equality for other types [vktDataGraphTestUtil.hpp](../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L380-L425).
- Property-query tests verify expected `VK_SUCCESS` or `VK_INCOMPLETE` return codes and, in single-call property retrieval, check that result buffers were overwritten [vktDataGraphPropertiesTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L256-L268), [vktDataGraphPropertiesTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L426-L463).
- Cache tests verify cache-hit feedback bits, compile-required results, null handles for failed creation, and batch early-return effects [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L289-L340), [vktDataGraphPipelineCacheTests.cpp](../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L553-L575).

## Notes on Scope and Uncertainty

The inspected Vulkan API test plan did not contain a data-graph-specific section, so the category summary is based on source code under `external/vulkancts/modules/vulkan/data_graph/`, the root registration in `external/vulkancts/modules/vulkan/vktTestPackage.cpp`, and mustpass evidence from `external/vulkancts/mustpass/main/vk-default/data-graph.txt`. This page does not claim coverage for instruction sets other than the source-observed `TOSA` provider path.