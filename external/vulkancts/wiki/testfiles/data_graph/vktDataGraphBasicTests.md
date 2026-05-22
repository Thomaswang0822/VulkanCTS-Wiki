# vktDataGraphBasicTests

This page documents the implementation file for the `dEQP-VK.data_graph.basic` tests.

## Overview

`vktDataGraphBasicTests.cpp` registers basic `VK_ARM_data_graph` coverage for creating data graph pipelines and submitting data graph dispatch commands. The file uses a shared parameter matrix, obtains a TOSA-backed `DataGraphTest`, creates tensor resources and descriptors, builds a data graph pipeline, optionally creates a pipeline session, and verifies output tensors after dispatch.

## Role of File

- **Registration file:** yes. It registers the direct children under `data_graph.basic`.
- **Implementation file:** yes. It implements the `create_pipeline` and `submit_pipeline` functions.

## Source Code Links

| Item | Evidence |
|------|----------|
| Header included by root dispatcher | [vktDataGraphTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L28-L30) |
| `basic` root child registration | [vktDataGraphTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L43-L45) |
| Basic subgroup registration | [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L423-L427) |
| Shared parameter generation | [vktDataGraphTestUtil.cpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L175-L220) |
| TOSA provider dispatch | [vktDataGraphTestProvider.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.hpp#L44-L62) |

## Registration Hierarchy

```text
data_graph.basic
├── create_pipeline
└── submit_pipeline
```

## Test Families

### create_pipeline — Pipeline and session creation

`create_pipeline` iterates over every generated `TestParams` value, both shader-module input modes (`BINARY`, `MODULE`), and both compiler-control modes (`NONE`, `EMPTY_STR`) [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L397-L411). The test creates tensors and views, descriptor set layout entries for tensor resources, graph resource and constant arrays, a pipeline layout, and a `VkDataGraphPipelineCreateInfoARM` before calling `createDataGraphPipelineARM` [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L122-L238). It then creates a `DataGraphSessionWithMemory` and checks both the pipeline and session handles [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L239-L248).

### submit_pipeline — Pipeline dispatch and output validation

`submit_pipeline` registers one case per generated `TestParams` value [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L414-L420). It creates and initializes tensor resources, descriptor sets, a `DataGraphPipelineWrapper`, and a pipeline session [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L251-L354). It records commands to bind the data graph pipeline, bind tensor descriptors, and call `cmdDispatchDataGraphARM`, then submits and waits [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L355-L373). After execution, it verifies only tensor resources marked as outputs by `requiresVerify()` [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L375-L390).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Shader input mode for `create_pipeline` | `MODULE` and `BINARY` [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L66-L70) |
| Compiler-control mode for `create_pipeline` | no compiler-control struct or an empty vendor-options string [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L72-L81), [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L219-L225) |
| Instruction set | Default generation uses `TOSA` [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440) |
| Session memory | `false` and `true` from shared generation [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440) |
| Resource cardinalities | Input, output, and constant cardinality combinations from `allResourceCardinalityCombinations`; combinations with no outputs are excluded by construction and validation [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L127-L132), [vktDataGraphTestUtil.cpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L166-L170) |
| Resource stride modes | implicit, packed, and not-packed combinations from `allStrideModesCombinations`; constants cannot be not-packed [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L113-L125), [vktDataGraphTestUtil.cpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L146-L155) |
| Binding order | ordered and shuffled bindings [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), with output names reflecting `_orderedBindings` or `_unorderedBindings` [vktDataGraphTestUtil.cpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L80-L116) |
| Tensor tiling | `VK_TENSOR_TILING_LINEAR_ARM` and `VK_TENSOR_TILING_OPTIMAL_ARM`; explicit strides are invalid for optimal tiling [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [vktDataGraphTestUtil.cpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.cpp#L139-L145) |
| Sparse constants | `false` and `true`, but sparse constants require constant resources and provider sparsity information [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L434-L440), [vktDataGraphTestProvider.cpp](../../../modules/vulkan/data_graph/vktDataGraphTestProvider.cpp#L108-L138) |
| Format strings | Provider-selected per TOSA graph family, such as `i32`, `fp32`, `fp16`, `i8`, and multi-format convolution strings [vktDataGraphTosaUtil.hpp](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L235-L253), [vktDataGraphTosaUtil.hpp](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L1205-L1238) |

## Support and Feature Requirements

Every basic test delegates support checking to `TestParams::checkSupport()` [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L117-L120). That shared check requires `VK_ARM_data_graph`, `VK_ARM_tensors`, `dataGraph`, `dataGraphShaderModule`, `tensors`, and `shaderTensorAccess`; it also requires `tensorNonPacked` when the parameter set requests non-packed resources [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L220-L256).

## Verification Methods

- Pipeline creation succeeds if `createDataGraphPipelineARM` returns a non-null pipeline and the session wrapper returns a non-null session [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L233-L248).
- Dispatch tests validate each output tensor by calling the `DataGraphTest` provider's `verifyData()` method [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L375-L390).
- The common tensor comparator uses SNR for floating-point tensors and exact element equality for non-floating-point tensors [vktDataGraphTestUtil.hpp](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L380-L425).
- TOSA-backed tests assemble and validate SPIR-V before returning the binary; for example, the add/sub implementation calls SPIRV-Tools assemble and validate before returning [vktDataGraphTosaUtil.hpp](../../../modules/vulkan/data_graph/tosa/vktDataGraphTosaUtil.hpp#L121-L158).

## Test Principles

- Exercise two creation paths: a shader-module path and a raw SPIR-V binary path [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L195-L217).
- Exercise optional compiler-control chaining with an empty vendor-options string [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L219-L225).
- Reuse the same provider-backed resource model for creation and execution so that tensor descriptions, constants, descriptor bindings, and reference verification are derived from the same `DataGraphTest` object [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L128-L190), [vktDataGraphBasicTests.cpp](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L259-L346).

## Notes and Uncertainties

The inspected API test plan did not provide a data-graph-specific section. The parameter matrix and verification descriptions above are therefore derived from implementation files and mustpass naming evidence.