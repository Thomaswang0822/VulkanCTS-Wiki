## Overview

**Core question:** How does the `data_graph` dispatcher expose the three registered data graph test families?

- This page covers the dispatcher in [`vktDataGraphTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L39-L47), not the implementation details of the `basic`, `cache`, or `properties` test families.
- The Vulkan test package registers the `data_graph` test category with `dataGraph::createTests`.
- The dispatcher creates the category root and attaches the direct children `basic`, `cache`, and `properties`.
- The child implementations own pipeline lifecycle, pipeline-cache, and property-query behavior. This page explains their routing, shared support boundary, and failure scope.

## Background Knowledge

- A Vulkan CTS test category is a named root in the test tree. Its child test families can register executable test cases below that root.
- A dispatcher is a registration function that creates a root and delegates each child to another factory. It does not itself define a test case, shader, runtime submission, or result comparison.
- A support check can remove a child test case before execution when the device lacks the required extension, feature, or parameter-dependent capability. The dispatcher only provides the route to those child checks.

## Registration Hierarchy

```text
data_graph
├── basic
├── cache
└── properties
```

The top-level Vulkan test package adds `data_graph` with `dataGraph::createTests` in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1398-L1400). The dispatcher adds the three direct children in order in [`vktDataGraphTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L39-L47). The mustpass file contains all three prefixes: `dEQP-VK.data_graph.basic`, `dEQP-VK.data_graph.cache`, and `dEQP-VK.data_graph.properties` in [`data-graph.txt`](../../../mustpass/main/vk-default/data-graph.txt#L1-L10176).

## Parameter Dimensions and Observed Values

The dispatcher has no parameterized test cases. It passes the test context and supplied root name to the root constructor, then delegates parameter generation to the child factories. The child pages should document the matrices that those factories generate.

| Dispatcher dimension | Observed value | Meaning in this page | Evidence |
|----------------------|----------------|----------------------|----------|
| Direct child group | `basic`, `cache`, `properties` | Selects which child factory owns registration and execution | [`vktDataGraphTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L41-L45) |

## Behavior Parameters

The dispatcher has no behavioral parameter of its own. Its only behavior choice is the direct child test family, and each child page owns the corresponding implementation details:

- `basic` covers `create_pipeline` and `submit_pipeline`, including the basic data graph pipeline lifecycle. See [`vktDataGraphBasicTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L423-L427).
- `cache` covers cache-aware `create_pipeline` and `submit_pipeline` paths. Its implementation registers `single_call` and `multi_calls` under creation, then registers submission cases. See [`vktDataGraphPipelineCacheTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L834-L855).
- `properties` covers `available` and `get` property-query paths. See [`vktDataGraphPropertiesTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L547-L551).

These are routing descriptions, not duplicates of the child pages' parameter matrices or execution explanations.

## Shader Analysis

The dispatcher source is registration-only: [`createTests`](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L39-L47) constructs the root and forwards each direct child to a factory, but contains no shader source, shader selection, shader-module build, or shader execution. The child implementations own any shader behavior, including the TOSA-backed paths represented in mustpass. This page is therefore recorded in the source-reviewed no-walkthrough exception registry; adding a representative shader here would misattribute child behavior to the dispatcher.

## Runtime Execution and Result Checking

- The test package calls `dataGraph::createTests` while constructing the Vulkan test tree. The function creates a `TestCaseGroup` using the supplied root name.
- The function attaches the `basic`, `cache`, and `properties` child groups through `createTestGroup`. Each child factory then registers its own executable cases.
- The dispatcher performs no Vulkan device query, command submission, output readback, or pass/fail comparison. Those operations remain within the child implementations and their shared data graph utilities.
- The shared child support path requires `VK_ARM_data_graph` and `VK_ARM_tensors`, then checks the `dataGraph`, `dataGraphShaderModule`, `tensors`, and `shaderTensorAccess` features. Parameter sets using non-packed resources also require `tensorNonPacked` in [`vktDataGraphTestUtil.hpp`](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L256). Cache cases add the pipeline-creation cache-control requirement in [`vktDataGraphPipelineCacheTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L129-L146).

## Failure Meaning

### Failure Cause Mapping

Because this page documents a single registration dispatcher rather than an executable behavioral axis, a failure maps to the dispatcher boundary itself.

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic`, `cache`, or `properties` | The category root was not registered, a direct child was omitted or renamed, or the child factory failed while constructing its test group |

### Cause Analysis

#### Dispatcher tree construction

**Possible failure symptoms:** The `data_graph` path is absent, a direct child path is absent or has a different name, or test-tree construction reports an error while creating a child group.

**Possible implementation causes:** The package registration call, the root group construction, or one of the three `createTestGroup` calls may not match the current registration contract. Source-level investigation is needed to distinguish a package-registration problem from a child-factory problem.

## Case Pruning

### Requirement-based pruning

The dispatcher does not prune executable cases. Each child test case runs its own support callback, so unsupported extension, feature, or limit combinations are skipped at the child boundary. The shared support checks require `VK_ARM_data_graph` and `VK_ARM_tensors`, the relevant data graph and tensor features, and `tensorNonPacked` when a parameter set uses non-packed resources. Cache tests add their cache-control requirement. See [`vktDataGraphTestUtil.hpp`](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L256) and [`vktDataGraphPipelineCacheTests.cpp`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L129-L146).

### Design-based pruning

The dispatcher intentionally exposes exactly three direct children. It does not add implementation-level cases or collapse the child families into one group. Parameter and combination pruning belongs to the child factories and shared utilities, not to this root implementation.

## Key Takeaways

- `data_graph` is a dispatcher/root implementation with exactly three direct children: `basic`, `cache`, and `properties`.
- The root page establishes the registered path and page boundary. It does not duplicate the child families' pipeline, cache, property-query, or shader details.
- Support checks and case pruning occur in child implementations after the dispatcher routes execution to them.
- A root-level failure points first to category registration or child-group construction. An executable test failure requires the corresponding child page and source path for analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Vulkan package root registration | [`vktTestPackage.cpp#L1398-L1400`](../../../modules/vulkan/vktTestPackage.cpp#L1398-L1400) | Adds `data_graph` to the Vulkan test package |
| Data graph dispatcher | [`vktDataGraphTests.cpp#L39-L47`](../../../modules/vulkan/data_graph/vktDataGraphTests.cpp#L39-L47) | Creates the root and registers its three direct children |
| Mustpass hierarchy | [`data-graph.txt#L1-L10176`](../../../mustpass/main/vk-default/data-graph.txt#L1-L10176) | Lists the registered `basic`, `cache`, and `properties` paths |
| Basic child registration | [`vktDataGraphBasicTests.cpp#L423-L427`](../../../modules/vulkan/data_graph/vktDataGraphBasicTests.cpp#L423-L427) | Defines the `basic` child boundary |
| Cache child registration | [`vktDataGraphPipelineCacheTests.cpp#L851-L855`](../../../modules/vulkan/data_graph/vktDataGraphPipelineCacheTests.cpp#L851-L855) | Defines the `cache` child boundary |
| Properties child registration | [`vktDataGraphPropertiesTests.cpp#L547-L551`](../../../modules/vulkan/data_graph/vktDataGraphPropertiesTests.cpp#L547-L551) | Defines the `properties` child boundary |
| Shared support routing | [`vktDataGraphTestUtil.hpp#L219-L256`](../../../modules/vulkan/data_graph/vktDataGraphTestUtil.hpp#L219-L256) | Defines common extension, feature, and parameter-dependent support checks |
