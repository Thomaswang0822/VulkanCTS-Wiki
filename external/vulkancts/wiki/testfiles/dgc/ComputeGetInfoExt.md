## Overview

**Core question:** Does `vkGetGeneratedCommandsMemoryRequirementsEXT` return stable requirements for equivalent EXT compute inputs and a nondecreasing size when `maxSequenceCount` increases?

- This page covers the `dgc.ext.compute.get_info` test family implemented by `vktDGCComputeGetInfoTestsExt.cpp`.
- The family registers five test case leaves that vary the layout tokens, layout usage flags, execution-set form, or `maxSequenceCount` passed to `vkGetGeneratedCommandsMemoryRequirementsEXT`.
- Each case builds the required layout and query structures, calls the memory-requirements query twice, and compares `size`, `alignment`, and `memoryTypeBits`.
- The generated compute shader creates a compatible compute pipeline and is not executed by these tests. The tested behavior is the memory-requirements query.

## Background Knowledge

- **Generated command layout.** A `VkIndirectCommandsLayoutEXT` describes the token types and byte offsets in an indirect command stream. The layout also carries usage flags, such as `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT` or `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`.
- **Memory-requirements query inputs.** `VkGeneratedCommandsMemoryRequirementsInfoEXT` combines the layout with `maxSequenceCount` and `maxDrawCount`. The EXT helper stores an indirect execution set in the structure when one is used, or chains a pipeline description through `pNext` when the query uses a direct pipeline. The query returns a `VkMemoryRequirements2` whose nested `VkMemoryRequirements` contains a byte size, an alignment, and memory type bits.
- **Indirect execution sets.** An indirect execution set lets generated commands select a pipeline or shader object. The pipeline-token case uses a pipeline-based `VkIndirectExecutionSetEXT`; the other cases pass a regular compute pipeline directly.

## Registration Hierarchy

```text
dgc.ext.compute.get_info
├── constant_cmd_memory_requirements_basic_case
├── constant_cmd_memory_requirements_basic_case_with_pipeline
├── constant_cmd_memory_requirements_ignore_unordered_flag
├── constant_cmd_memory_requirements_increase_count
└── constant_cmd_memory_requirements_max_sequence_count
```

The root is attached to the EXT compute branch by [vktDGCTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L95-L101). The five direct children come from the factory in [vktDGCComputeGetInfoTestsExt.cpp](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L256-L280) and appear in [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L57-L61).

## Parameter Dimensions and Observed Values

The registered test case leaf is the primary dimension. The implementation changes the query inputs and layout form for each leaf rather than generating a larger cross-product.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `constant_cmd_memory_requirements_basic_case`, `constant_cmd_memory_requirements_basic_case_with_pipeline`, `constant_cmd_memory_requirements_increase_count`, `constant_cmd_memory_requirements_max_sequence_count`, `constant_cmd_memory_requirements_ignore_unordered_flag` | Selects which query input changes between the two calls. | [case table](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L262-L280) |
| Command layout tokens | One `DISPATCH_EXT`; `EXECUTION_SET_EXT` plus `DISPATCH_EXT`; `PUSH_CONSTANT_EXT` plus `DISPATCH_EXT` | Changes the layout data represented in the memory-requirements query. | [layout construction](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L169-L190) |
| Layout usage flags | No flag; `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`; `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT` on the second layout | Checks that the explicit-preprocess and unordered-sequence forms produce the expected requirement invariance where the test applies it. | [usage flags](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L151-L166) |
| `maxSequenceCount` | `1024u`; `context.getDeviceGeneratedCommandsPropertiesEXT().maxIndirectSequenceCount`; doubled value for `increase_count` | Supplies the sequence bound used by the query. The increase case changes it from the initial value to twice that value. | [sequence-count selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L199-L207), [second query inputs](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L209-L221) |
| Pipeline selection | Direct `VkPipeline`; pipeline-based `VkIndirectExecutionSetEXT` with `maxPipelineCount = 64u` | Exercises the query with a direct pipeline for ordinary cases and an indirect execution set for the pipeline-token case. | [pipeline and execution-set setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L108-L149) |

## Behavior Parameters

The primary behavioral axis is the registered test case leaf. Each value changes the memory-requirements query in a specific way.

### `constant_cmd_memory_requirements_basic_case` | Basic dispatch layout

The test builds one `VK_INDIRECT_COMMANDS_TOKEN_TYPE_DISPATCH_EXT` token and enables `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_EXPLICIT_PREPROCESS_BIT_EXT`. It queries requirements with `maxSequenceCount = 1024u`, then repeats the same query. The returned size, alignment, and memory type bits must remain unchanged.

### `constant_cmd_memory_requirements_basic_case_with_pipeline` | Pipeline token and execution set

The layout contains a compute pipeline token followed by a dispatch token. The test creates a pipeline-based `VkIndirectExecutionSetEXT` with room for `64u` pipelines and supplies that handle to the query instead of a direct pipeline. Repeating the query must return the same three requirement fields.

### `constant_cmd_memory_requirements_increase_count` | Larger sequence bound

The layout contains a push-constant token followed by a dispatch token, and the pipeline layout exposes a one-word compute push-constant range. The second query doubles `maxSequenceCount`. The test permits the required size to grow or stay equal, but it fails if the second size is smaller; alignment and memory type bits must remain equal.

### `constant_cmd_memory_requirements_max_sequence_count` | Device maximum sequence bound

The test reads `maxIndirectSequenceCount` from `VkPhysicalDeviceDeviceGeneratedCommandsPropertiesEXT` and passes that value to both queries. The layout contains one dispatch token, so this case checks the query at the device-reported sequence limit.

### `constant_cmd_memory_requirements_ignore_unordered_flag` | Unordered-layout flag

The test creates two otherwise identical dispatch layouts. The second adds `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`, then supplies that second layout to the second query. The size, alignment, and memory type bits must match the first query.

## Shader Analysis

The source generates one compute shader for all five cases. It declares a storage buffer at set `0`, binding `0`, uses a `local_size` of `64 x 1 x 1`, and adds a one-word push-constant block only for `constant_cmd_memory_requirements_increase_count`. The shader computes a global invocation index and would write `uint(sqrt(float(globalInvocationIndex))) + offset` to the output buffer if a dispatch executed it.

The test never submits generated commands or a dispatch. The shader therefore supplies the compute pipeline module used while constructing the memory-requirements inputs; its arithmetic and output buffer are outside the behavior checked here. This page intentionally has no representative shader walkthrough. The source-backed exception is recorded as `dgc/ComputeGetInfoExt.md` in [walkthrough_exceptions.py](../../../../../.agents/skills/wiki-rewriter/scripts/walkthrough_exceptions.py).

## Runtime Execution and Result Checking

- The factory selects a support callback for each leaf. Four leaves use `checkDGCExtComputeSupport` with `DGCComputeSupportType::BASIC`; the pipeline-token leaf uses `DGCComputeSupportType::BIND_PIPELINE`. Both paths require `VK_EXT_device_generated_commands` and compute-stage support. The latter also requires compute-stage pipeline binding support. See [support helpers](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L44-L75).
- The test creates a descriptor-set layout with one compute storage-buffer binding and a pipeline layout. Only the increase-count case adds a one-word push-constant range. It compiles the generated `comp` source and creates either a direct compute pipeline or a pipeline-based indirect execution set. See [program and pipeline setup](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L60-L149).
- `IndirectCommandsLayoutBuilderExt` turns the selected token list and usage flags into a `VkIndirectCommandsLayoutEXT`. Its `getStreamRange()` is based on each token's offset and data size, and `build()` requires one work-provoking token at the end of the list. See [layout helper](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L661-L706).
- `DGCMemReqsInfo` initializes `VkGeneratedCommandsMemoryRequirementsInfoEXT`, fills in the execution set, layout, sequence and draw counts, and attaches either pipeline information or shader information when needed. This page uses the pipeline form or an indirect execution set. See [query-info helper](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L252-L286).
- The test calls `getGeneratedCommandsMemoryRequirementsExt` twice. The helper wraps `getGeneratedCommandsMemoryRequirementsEXT` and returns the nested `VkMemoryRequirements`. No command buffer, preprocessing buffer, generated-command buffer, or result readback is needed. See [query wrapper](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L354-L360).
- The host compares the first and second query results. In the increase-count case it checks that size does not decrease. In all other cases it requires equal size. Every case requires equal alignment and equal `memoryTypeBits`. A mismatch logs both records and returns `fail`; otherwise the test returns `pass("Pass")`. See [comparison logic](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L209-L251).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `constant_cmd_memory_requirements_basic_case` | The query returns unstable or inconsistent requirements for a basic dispatch layout, including the explicit-preprocess usage form. |
| `constant_cmd_memory_requirements_basic_case_with_pipeline` | The query does not handle the pipeline token and pipeline-based indirect execution set consistently. |
| `constant_cmd_memory_requirements_increase_count` | The query reports a smaller required size after the test doubles `maxSequenceCount`, or changes alignment or memory type bits. |
| `constant_cmd_memory_requirements_max_sequence_count` | The query does not handle the device-reported `maxIndirectSequenceCount` consistently. |
| `constant_cmd_memory_requirements_ignore_unordered_flag` | The query changes requirements when the otherwise matching layout gains the unordered-sequences usage flag. |

### Cause Analysis

#### Requirement invariance for a basic dispatch layout

**Possible failure symptoms:** The basic case reports changed `size`, `alignment`, or `memoryTypeBits` between identical calls. The failure log contains the first and second `VkMemoryRequirements` records.

**Possible implementation causes:** The query path may derive different results from equivalent input structures, or may account inconsistently for the explicit-preprocess usage flag. The test does not identify which implementation layer produced the difference, so source-level investigation is needed.

#### Pipeline-token or indirect-execution-set handling

**Possible failure symptoms:** The pipeline case reports a difference in one of the three requirement fields between repeated queries using the same pipeline-based indirect execution set and layout.

**Possible implementation causes:** The implementation may process the `EXECUTION_SET_EXT` token or its pipeline metadata inconsistently when calculating requirements. The observed mismatch does not distinguish query handling from pipeline or execution-set state, so source-level investigation is needed.

#### Sequence-count monotonicity or limit handling

**Possible failure symptoms:** `constant_cmd_memory_requirements_increase_count` reports that required size became smaller after the test doubled `maxSequenceCount`, or reports changed alignment or memory type bits. The maximum-count case reports a mismatch between identical queries using the device-reported maximum.

**Possible implementation causes:** The query may handle the sequence bound inconsistently, calculate the size for a larger bound incorrectly, or use unstable alignment or memory-type selection. The source provides the comparison rule but not a narrower implementation diagnosis.

#### Unordered-sequence flag handling

**Possible failure symptoms:** The unordered-flag case reports different size, alignment, or memory type bits for the layout with `VK_INDIRECT_COMMANDS_LAYOUT_USAGE_UNORDERED_SEQUENCES_BIT_EXT`.

**Possible implementation causes:** The query may include the usage flag in its memory calculation when these two layouts should produce equal requirements, or may otherwise fail to treat equivalent layout inputs consistently. Source-level investigation is needed to locate the cause of a field mismatch.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `VK_EXT_device_generated_commands` and support for the compute shader stage. The pipeline-token leaf additionally requires compute-stage pipeline binding support through `DGCComputeSupportType::BIND_PIPELINE`. Unsupported devices skip the case through the support callback rather than producing a test failure. See [EXT compute support](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L44-L75).
- The test reads `maxIndirectSequenceCount` only for the maximum-count case. The other cases use the fixed value `1024u`; the source has no additional device-limit pruning for that value. See [sequence-count selection](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L199-L207).

### Design-based pruning

- The source registers only the five leaves in `cmdMemCases`; it does not form a cross-product of token types, flags, pipeline forms, and sequence counts. See [case registration](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L262-L280).
- The generated shader is shared by all leaves, and the source does not execute it. The page therefore does not treat shader arithmetic, storage-buffer contents, or dispatch dimensions as behavior parameters.
- `maxPipelineCount` is `64u` only to construct the indirect execution set for the pipeline-token case. The test does not populate or exercise a 64-pipeline matrix.

## Key Takeaways

- These cases test the stability and comparison rules of `vkGetGeneratedCommandsMemoryRequirementsEXT`; they do not execute generated command streams.
- The primary behavioral axis is the five registered test case leaves. Each leaf changes one query input or layout form and compares the fields that the API returns.
- Increasing `maxSequenceCount` may increase required size, but the source rejects a decrease and requires alignment and memory type bits to remain unchanged.
- The pipeline-token case supplies a pipeline-based indirect execution set, while the other cases use a direct compute pipeline.
- The host determines pass or fail from the two `VkMemoryRequirements` records. A failure identifies a requirement mismatch, not a specific implementation component.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test case registration | [createDGCComputeGetInfoTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L256-L283) | Creates `get_info` and registers all five exact leaves. |
| Query test body | [constantCommandsMemReqs](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L103-L251) | Builds the selected inputs, performs both queries, and compares the returned fields. |
| Generated compute source | [initBasicProgram](../../../modules/vulkan/device_generated_commands/vktDGCComputeGetInfoTestsExt.cpp#L60-L83) | Defines the pipeline-compatible shader that the tests compile but do not dispatch. |
| Layout construction | [IndirectCommandsLayoutBuilderExt](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L370-L706) | Implements token insertion, stream-range calculation, and layout creation. |
| Memory-requirements input wrapper | [DGCMemReqsInfo](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L252-L286) | Builds the EXT query structure and its optional `pNext` metadata. |
| Memory-requirements query wrapper | [getGeneratedCommandsMemoryRequirementsExt](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L354-L360) | Calls `getGeneratedCommandsMemoryRequirementsEXT` and returns `VkMemoryRequirements`. |
| EXT compute support | [checkDGCExtComputeSupport](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.cpp#L44-L75) | Applies extension, compute-stage, and pipeline-binding support checks. |
| EXT utility declarations | [vktDGCUtilExt.hpp](../../../modules/vulkan/device_generated_commands/vktDGCUtilExt.hpp#L42-L53) | Declares the support types used by the test factory. |
| Category registration | [vktDGCTests.cpp](../../../modules/vulkan/device_generated_commands/vktDGCTests.cpp#L72-L120) | Places `get_info` under `dgc.ext.compute`. |
| vk-default mustpass paths | [dgc.txt](../../../mustpass/main/vk-default/dgc.txt#L57-L61) | Lists the five registered EXT compute get-info paths. |
