## Overview

**Core question:** Can Vulkan create a compute pipeline derivative when the parent is selected by a prior pipeline handle or by an earlier entry in the same creation call?

- [`vktPipelineDerivativeTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L1) implements the `derivative` test family in the `pipeline` test category.
- The family covers only monolithic compute-pipeline creation. It creates a parent with `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`, then creates a child with `VK_PIPELINE_CREATE_DERIVATIVE_BIT`.
- The three test case leaves exercise a parent selected through `basePipelineHandle`, the `VK_KHR_maintenance5` flags2 form of that handle path, and `basePipelineIndex` in a two-entry `vkCreateComputePipelines` call.
- The CTS attempts the pipeline creations and does not dispatch the shader or compare compute output. The handle cases use error-checking creation wrappers, but the index case calls `vkCreateComputePipelines` directly and ignores its `VkResult` before cleanup and returning `pass("OK")`.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A [pipeline derivative](../../../../vulkan-docs/src/chapters/pipelines.adoc#L7940-L7967) is a child pipeline created from a parent expected to have substantial commonality. `VK_PIPELINE_CREATE_DERIVATIVE_BIT` marks the child, while its parent must carry `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`.
- A derivative create info identifies exactly one parent. `basePipelineHandle` names an already-created pipeline; `basePipelineIndex` names an earlier element of the same creation-call array. `VK_NULL_HANDLE` and `-1` are their respective invalid values.
- `VkPipelineCreateFlags2CreateInfoKHR` provides the `VK_KHR_maintenance5` flags2 representation used by the dedicated test case. Pipeline derivatives are unavailable in Vulkan SC.

## Registration Hierarchy

```text
pipeline.monolithic.derivative
└── compute
```

[`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L198-L205) adds this test family only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`. [`createDerivativeTests`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L170-L186) registers these test case leaves below `compute`: `derivative_by_handle`, `derivative_by_handle_maintenance5`, and `derivative_by_index`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pipeline construction type | `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` | Limits the family to ordinary compute-pipeline creation; the source does not repeat compute cases for other construction types. | [`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L198-L205) |
| Parent-selection mechanism | `basePipelineHandle`, `basePipelineIndex` | Selects whether the child refers to a parent made in an earlier call or an earlier entry in the current two-entry call. | [handle path](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L80-L127), [index path](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L129-L166) |
| Flag representation | `VkComputePipelineCreateInfo::flags`, `VkPipelineCreateFlags2CreateInfoKHR::flags` | Exercises legacy create flags and the maintenance5 flags2 representation for the handle path. | [maintenance5 branch](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L97-L121) |
| Test case leaf | `derivative_by_handle`, `derivative_by_handle_maintenance5`, `derivative_by_index` | Selects the creation sequence and parent reference form. | [registration](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L175-L182) |

The default mustpass file lists three leaves under `pipeline.monolithic.derivative.compute`, matching the three source registrations in [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt#L32589-L32591).

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf changes the way the child identifies its parent during compute-pipeline creation.

### `derivative_by_handle`: previously created parent handle

The CTS creates a base pipeline with `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`. It then changes the same create info to `VK_PIPELINE_CREATE_DERIVATIVE_BIT`, assigns `basePipelineHandle` to the base pipeline, and makes a second creation call. The parent exists before the child call, which matches the handle contract.

### `derivative_by_handle_maintenance5`: parent handle with flags2

This leaf repeats the parent-handle relationship but requires `VK_KHR_maintenance5`. The source sets `VkPipelineCreateFlags2CreateInfoKHR::flags` to `VK_PIPELINE_CREATE_2_ALLOW_DERIVATIVES_BIT_KHR` for the parent and `VK_PIPELINE_CREATE_2_DERIVATIVE_BIT_KHR` for the child, clearing the legacy `flags` field in each stage.

### `derivative_by_index`: earlier entry in one creation call

The CTS supplies two `VkComputePipelineCreateInfo` entries to one `vkCreateComputePipelines` call. Entry 0 is the parent and carries `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`; entry 1 is the child, carries `VK_PIPELINE_CREATE_DERIVATIVE_BIT`, and sets `basePipelineIndex` to `0`. The parent therefore precedes the child in the supplied array.

## Shader Analysis

The source compiles one trivial `comp` shader with `local_size_x=1` and an empty `main`. The shader supplies a valid compute stage for pipeline creation, but the CTS never dispatches it. No shader walkthrough or SPIR-V analysis is needed because shader behavior is outside the tested property.

## Runtime Execution and Result Checking

1. The test creates a shader module from `comp` and an empty pipeline layout.
2. In each handle-based leaf, the source prepares `VkComputePipelineCreateInfo` with the compute stage, empty layout, `VK_NULL_HANDLE`, and `basePipelineIndex` `-1`. It creates the base first with `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`.
3. The handle path changes the flags to `VK_PIPELINE_CREATE_DERIVATIVE_BIT`, assigns the base handle to `basePipelineHandle`, and creates the derivative. The maintenance5 leaf performs the same sequence with a chained `VkPipelineCreateFlags2CreateInfoKHR` and requires `VK_KHR_maintenance5` before execution.
4. The index path builds two create-info entries and calls `vkCreateComputePipelines` once. Unlike the handle path's `createComputePipeline` wrapper, this direct call does not check the returned `VkResult`; the source then destroys both returned raw pipeline handles.
5. Each function returns `tcu::TestStatus::pass("OK")` after its creation/cleanup sequence reaches the return statement. The source contains no dispatch, synchronization, result buffer, or output comparison. Consequently, a Vulkan error from handle-based creation prevents that pass result, but an error returned by the index-path creation call is not itself converted into a test failure and can be masked unless cleanup or another framework mechanism exposes it.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `derivative_by_handle` | Compute pipeline creation rejects or mishandles a derivative whose parent is supplied through `basePipelineHandle`. |
| `derivative_by_handle_maintenance5` | The `VK_KHR_maintenance5` flags2 path rejects or mishandles the same parent-handle derivative relationship. |
| `derivative_by_index` | Batched compute pipeline creation rejects or mishandles an earlier parent selected through `basePipelineIndex`. |

### Cause Analysis

#### Parent-handle derivative creation fails

**Possible failure symptoms:** `derivative_by_handle` does not reach its `pass("OK")` result because creation of the base or derivative pipeline returns an error or the implementation crashes.

**Possible implementation causes:** The implementation may fail to retain or resolve the created parent pipeline for the derivative request, reject the valid `ALLOW_DERIVATIVES` and `DERIVATIVE` flag relationship, or mishandle the shared compute-stage and layout state. Vulkan requires a handle-selected parent to have been created already and to have been created with `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`; source-level investigation is needed to locate any failing implementation path.

#### Maintenance5 flags2 derivative creation fails

**Possible failure symptoms:** `derivative_by_handle_maintenance5` fails after its capability check has admitted the device, while the ordinary handle leaf can still succeed.

**Possible implementation causes:** The implementation may translate `VK_PIPELINE_CREATE_2_ALLOW_DERIVATIVES_BIT_KHR` or `VK_PIPELINE_CREATE_2_DERIVATIVE_BIT_KHR` differently from their legacy equivalents, or fail to process the chained `VkPipelineCreateFlags2CreateInfoKHR` consistently. The CTS deliberately clears the legacy field in this path, which isolates flags2 handling from a simultaneous legacy-flag value.

#### Parent-index derivative creation fails

**Possible failure symptoms:** `derivative_by_index` crashes or otherwise fails during the two-entry `vkCreateComputePipelines` call or subsequent cleanup. A non-success `VkResult` alone is not reported by this function because the direct call's return value is ignored.

**Possible implementation causes:** The implementation may fail to resolve `basePipelineIndex` within the submitted array, permit only handle-based lookup, or mishandle the required ordering. Vulkan requires an index-selected parent to appear earlier in `pCreateInfos`, and the base pipeline must have `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`; this test uses base index `0` for child entry `1`. Because the test ignores the direct call's `VkResult`, a rejected derivative may be silently treated as success rather than reaching this failure path.

## Case Pruning

### Requirement-based pruning

- `derivative_by_handle_maintenance5` calls `context.requireDeviceFunctionality("VK_KHR_maintenance5")` before its body runs.
- The ordinary derivative leaves rely on the derivative-pipeline feature defined for non-Vulkan-SC Vulkan. Pipeline derivatives are unsupported in Vulkan SC, and the source excludes the maintenance5 leaf under `CTS_USES_VULKANSC`.

### Design-based pruning

- The source registers only compute derivatives. It uses a fixed shader module and empty pipeline layout to keep the observation on creation-time parent selection rather than shader execution or graphics state.
- The family appears only under the monolithic construction type because the enclosing registration code avoids repeating compute pipeline tests for other construction types.
- The test uses one parent-handle path, one flags2 variant, and one parent-index path. It does not multiply those paths by pipeline-cache, descriptor, or dispatch-result variations because those do not change the derivative reference contract it tests.

## Key Takeaways

- The CTS exercises compute-pipeline derivative creation, not compute execution; the index case does not check the creation call's returned `VkResult`.
- Both parent selection forms must identify a parent made with `VK_PIPELINE_CREATE_ALLOW_DERIVATIVES_BIT`.
- `derivative_by_handle` requires a completed parent creation before the child call; `derivative_by_index` requires the parent to precede the child in the same call array.
- The maintenance5 leaf checks the flags2 representation of the handle path after requiring `VK_KHR_maintenance5`.
- Three mustpass leaves cover the three selected creation sequences under the monolithic pipeline root.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Capability check | [`checkSupport`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L60-L64) | Requires `VK_KHR_maintenance5` for its dedicated leaf |
| Compute fixture | [`initComputeDerivativePrograms`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L66-L78) | Defines the no-op shader used only to create a compute stage |
| Parent-handle path | [`testComputeDerivativeByHandle`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L80-L127) | Creates the base and derivative in separate calls and handles flags2 |
| Parent-index path | [`testComputeDerivativeByIndex`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L129-L166) | Supplies ordered base and derivative create infos in one call |
| Test-family registration | [`createDerivativeTests`](../../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L170-L186) | Registers the exact test case leaves below `compute` |
| Enclosing registration | [`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L198-L205) | Restricts the family to monolithic construction |
| Mustpass coverage | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt#L32589-L32591) | Lists the three default Vulkan leaves |
| Vulkan derivative rules | [Pipeline Derivatives](../../../../vulkan-docs/src/chapters/pipelines.adoc#L7940-L7967) | Defines derivative parent selection, ordering, and allowed-parent requirements |
| Compute pipeline validity | [Derivative create validity](../../../../vulkan-docs/src/chapters/pipelines.adoc#L888-L900) | Requires an earlier index and an allowed-derivatives parent for derivative compute creation |
