## Overview

**Core question:** Do Vulkan SC graphics and compute pipeline creation requests select exactly the pipeline identified by the application, and report an unmatched request correctly?

- This page documents `vktPipelineIdentifierTests.cpp`, registered below `sc.pipeline_identifier`.
- The family varies pipeline kind (`graphics` or `compute`), identifier scenario (`missing_pid`, `nonexisting_pid`, or `match_control`), and request cardinality (`single` or `multiple`). The registration therefore produces 12 executable leaves.
- A source pass creates pipelines with distinct application identifiers. A subprocess then repeats the create operation with `VkPipelineOfflineCreateInfo` attached through each pipeline create-info's `pNext` chain.
- The subprocess calls `vkCreateGraphicsPipelines` or `vkCreateComputePipelines` directly and checks both the returned `VkResult` and every returned `VkPipeline` handle. Shader execution is never part of the oracle.

## Background Knowledge

- `VkPipelineOfflineCreateInfo` is an extension structure chained to a pipeline create-info. Its application-provided identifier and match-control fields tell Vulkan SC how the requested pipeline is to be found.
- `VK_PIPELINE_MATCH_CONTROL_APPLICATION_UUID_EXACT_MATCH` selects application-identifier equality as the matching rule. The identifier is a fixed byte array, not a pipeline handle or an API-returned shader hash.
- A multi-pipeline create call returns one handle slot per input. This page distinguishes the call-level `VkResult` from per-index handle validity because an unmatched entry can coexist with successfully matched entries.
- An offline pipeline cache stores precompiled pipeline data. Application identifiers name entries independently of shader-module handles; `poolEntrySize` supplies the resource size associated with an entry. The host can therefore prepare resource accounting before requesting an identifier match.

## Registration Hierarchy

```text
sc.pipeline_identifier
├── graphics
└── compute
```

The exact registered leaves are also present in the default SC mustpass file: [pipeline-identifier entries](../../../mustpass/main/vksc-default/sc.txt#L150-L161). The source constructs this product in [createPipelineIdentifierTests](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L614-L685).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Effect on the test | Evidence |
|---|---|---|---|
| pipeline kind | `graphics`, `compute` | Selects the corresponding Vulkan pipeline create command and the graphics or compute setup. | [pipeline types](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L619-L628) |
| identifier scenario | `missing_pid`, `nonexisting_pid`, `match_control` | Controls whether index 0 has no identifier, an identifier absent from the source set, or the matching identifier. | [test types](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L630-L638) |
| match control | `exact_match` | Sets `matchControl` to `VK_PIPELINE_MATCH_CONTROL_APPLICATION_UUID_EXACT_MATCH` for every pipeline. | [match controls](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L640-L646) |
| cardinality | `single`, `multiple` | Creates one pipeline or three pipeline requests; the latter tests an unmatched first entry beside two matched entries. | [cardinalities](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L648-L655) |

The implementation uses `IDG_0000`, `IDG_1111`, and `IDG_2222` for graphics, and `IDC_0000`, `IDC_1111`, and `IDC_2222` for compute. The wrong identifier is the corresponding `*_XXXX` value. [Graphics identifier construction](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L265-L304) and [compute identifier construction](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L466-L505) define these exact values.

Every leaf includes the `exact_match` intermediate node, including the two negative scenarios:

| Exact default SC test case | Expected result |
|---|---|
| `dEQP-VKSC.sc.pipeline_identifier.compute.match_control.exact_match.multiple` | `VK_SUCCESS` |
| `dEQP-VKSC.sc.pipeline_identifier.compute.match_control.exact_match.single` | `VK_SUCCESS` |
| `dEQP-VKSC.sc.pipeline_identifier.compute.missing_pid.exact_match.multiple` | `VK_ERROR_NO_PIPELINE_MATCH` |
| `dEQP-VKSC.sc.pipeline_identifier.compute.missing_pid.exact_match.single` | `VK_ERROR_NO_PIPELINE_MATCH` |
| `dEQP-VKSC.sc.pipeline_identifier.compute.nonexisting_pid.exact_match.multiple` | `VK_ERROR_NO_PIPELINE_MATCH` |
| `dEQP-VKSC.sc.pipeline_identifier.compute.nonexisting_pid.exact_match.single` | `VK_ERROR_NO_PIPELINE_MATCH` |
| `dEQP-VKSC.sc.pipeline_identifier.graphics.match_control.exact_match.multiple` | `VK_SUCCESS` |
| `dEQP-VKSC.sc.pipeline_identifier.graphics.match_control.exact_match.single` | `VK_SUCCESS` |
| `dEQP-VKSC.sc.pipeline_identifier.graphics.missing_pid.exact_match.multiple` | `VK_ERROR_NO_PIPELINE_MATCH` |
| `dEQP-VKSC.sc.pipeline_identifier.graphics.missing_pid.exact_match.single` | `VK_ERROR_NO_PIPELINE_MATCH` |
| `dEQP-VKSC.sc.pipeline_identifier.graphics.nonexisting_pid.exact_match.multiple` | `VK_ERROR_NO_PIPELINE_MATCH` |
| `dEQP-VKSC.sc.pipeline_identifier.graphics.nonexisting_pid.exact_match.single` | `VK_ERROR_NO_PIPELINE_MATCH` |

## Behavior Parameters

The primary behavior axis is `identifier scenario`; pipeline kind and cardinality are orthogonal coverage dimensions. `exact_match` is the only registered match-control value, so this family does not compare other matching policies.

The host constructs identifiers; it does not query them from the Vulkan implementation. `resetPipelineOfflineCreateInfo` clears the identifier array, initializes the structure type, selects exact matching, and sets `poolEntrySize` to zero. `applyPipelineIdentifier` copies string bytes into the array up to `VK_UUID_SIZE`; it does not hash the name. For these fixed strings, the remaining bytes retain their initial zeros. [Identifier helpers](../../../framework/vulkan/vkSafetyCriticalUtil.cpp#L64-L84).

| Index | Graphics source name | Compute source name | Role in a multiple request |
|---|---|---|---|
| 0 | `IDG_0000` | `IDC_0000` | The entry whose identifier is omitted, replaced, or preserved. |
| 1 | `IDG_1111` | `IDC_1111` | A matching entry retained in every scenario. |
| 2 | `IDG_2222` | `IDC_2222` | A second matching entry retained in every scenario. |

`single` uses only index 0. Both negative scenarios initialize the destination-name vector with `IDG_XXXX` or `IDC_XXXX` at index 0, but only `nonexisting_pid` attaches that replacement to a request. `missing_pid` skips the extension structure instead. This is an absent-structure test, not a test of an all-zero identifier.

### `missing_pid` — omit the first identifier

The source pipeline at index 0 receives an application identifier, but the subprocess omits `VkPipelineOfflineCreateInfo` for that requested entry. Other entries in a `multiple` case receive their matching identifiers. The expected call result is `VK_ERROR_NO_PIPELINE_MATCH`; index 0 must be null, while indices 1 and 2 must be non-null when present. [Graphics expectation setup](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L334-L349) and [compute expectation setup](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L535-L550) make the omission explicit.

### `nonexisting_pid` — request an unknown identifier

The subprocess supplies `IDG_XXXX` or `IDC_XXXX` for index 0, while the remaining entries use their source identifiers. Because the first identifier is not in the source set, the expected result is `VK_ERROR_NO_PIPELINE_MATCH`; index 0 is null and the other requested pipelines are non-null. [Graphics non-existing case](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L350-L361) and [compute non-existing case](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L551-L561) define the per-index expectation.

### `match_control` — request matching identifiers

The subprocess supplies the same identifiers used by source creation and applies exact-match control. The expected result is `VK_SUCCESS`, and every returned handle must be non-null. [Graphics success case](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L362-L373) and [compute success case](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L563-L573) define this contract.

## Shader Analysis

No shader participates. The graphics and compute modules are created only as pipeline-construction inputs; no draw, dispatch, or shader-output check is performed. The oracle is pipeline identifier creation and retrieval.

## Runtime Execution and Result Checking

- Both pipeline kinds use a main-process preparation path and a subprocess validation path.
- All observable checks run on the host. The test creates no command buffer, framebuffer, output image, or readback buffer and submits no GPU work.

- **Create isolated state.** Each case creates its own instance and custom device, preventing identifiers from unrelated cases from colliding. It creates a pipeline layout and the minimal graphics render pass or compute state required by the selected API call. [Graphics setup](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L164-L265) and [compute setup](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L410-L464) show the construction.
- **Reserve source pipelines in the main process.** The main process attaches distinct source identifiers and creates the source pipelines through CTS helpers. This establishes the SC reservation/accounting state and returns `Pass`; it does not assert the matching behavior. [Graphics main-process path](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L306-L319) and [compute main-process path](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L507-L520) show the boundary.
- **Prepare the checked subprocess call.** The subprocess fills each `VkPipelineOfflineCreateInfo` pool-entry size, obtains the resource-interface pipeline cache, attaches the case-specific destination identifiers, and obtains the direct Vulkan function pointer. The direct call avoids the framework's pipeline wrapper while retaining SC resource accounting. [Graphics subprocess preparation](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L322-L332) and [compute subprocess preparation](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L523-L533) show these steps.
- **Check the call and handles.** The test invokes the selected create command. For each index, it checks the expected null/non-null state; separately, it compares the returned `VkResult` with `VK_SUCCESS` or `VK_ERROR_NO_PIPELINE_MATCH`. It destroys all returned handles afterward. [Graphics oracle](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L378-L407) and [compute oracle](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L579-L609) implement these checks.

### Pool-size lookup before identifier mutation

The subprocess calls `fillPoolEntrySize` while `pipelineIDs` still contains the source identifiers. The resource interface searches its recorded pipeline-size table for that identifier, throws `InternalError` if it cannot find an entry, and copies the recorded size into `poolEntrySize`. Only afterward does the test apply destination names or omit the extension structure. Thus `nonexisting_pid` reaches pipeline creation with the original entry size and a changed identifier; it does not first try to look up a size for the unknown name. [Size lookup](../../../framework/vulkan/vkResourceInterface.cpp#L275-L282), [graphics ordering](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L322-L359), [compute ordering](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L523-L560).

The test obtains `vkGetDeviceProcAddr` through the instance interface, then resolves the selected create command and `vkDestroyPipeline` for the custom device. This function-pointer lookup queries entry points, not pipeline identifiers. `getPipelineCache(device)` supplies the cache passed to the create call; the test does not inspect cache bytes or query an identifier from the returned pipeline.

### Result matrix and diagnostic limits

| Scenario | Call-level result | `single` handle | `multiple` handles at indices 0, 1, 2 |
|---|---|---|---|
| `missing_pid` | `VK_ERROR_NO_PIPELINE_MATCH` | null | null, non-null, non-null |
| `nonexisting_pid` | `VK_ERROR_NO_PIPELINE_MATCH` | null | null, non-null, non-null |
| `match_control` | `VK_SUCCESS` | non-null | non-null, non-null, non-null |

The host initializes the output vector and expected-nullness vector, performs one batched create call in the subprocess, and checks every output slot even if the call returns an error. A null handle where success was expected logs `Pipeline <index> should be created`; an unexpected non-null handle logs `Pipeline <index> should not be created`. A result mismatch logs `vkCreateGraphicsPipelines returned wrong VkResult` or its compute equivalent. Any mismatch sets `isOK` false; the final status is `Pass` or `Fail` after cleanup. The oracle checks handle nullness, not handle identity, uniqueness, shader execution, or the content of the selected pipeline. [Graphics checks](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L378-L407), [compute checks](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L579-L609).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `missing_pid` | Missing-identifier handling or per-entry batch results. |
| `nonexisting_pid` | Identifier lookup/equality or per-entry batch results. |
| `match_control` | Exact-match lookup or success/result reporting. |

### Cause Analysis

#### Identifier lookup and exact-match control

**Possible failure symptoms:** The returned `VkResult` differs from the expected value, or one or more pipeline handles violate the case-specific null/non-null expectation.

**Possible implementation causes:** The implementation may compare the supplied identifier incorrectly, interpret exact-match control incorrectly, or assemble the batch result inconsistently. The CTS does not localize the fault beyond the create call and returned handles; further investigation must inspect pipeline-identifier lookup and batch error handling.

#### Batch result and handle preservation

**Possible failure symptoms:** A `multiple` case reports the wrong handle state for one index, especially when index 0 fails and later entries should succeed.

**Possible implementation causes:** The implementation may mishandle partial results or associate the call-level error with every output slot instead of preserving per-entry handle state.

#### Setup and resource-accounting failures

**Possible failure symptoms:** The case cannot reach the intended create-call oracle, or device/resource setup fails before the identifier check.

**Possible implementation causes:** The failure may be in device creation, pipeline reservation accounting, pipeline-cache handling, or another prerequisite rather than identifier matching itself. The source uses a separate device and explicitly fills pool-entry sizes in the subprocess to keep those SC setup requirements visible. [Resource accounting calls](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L523-L524)

## Case Pruning

### Requirement-based pruning

The registration supplies shader-generation and test functions without a case-specific support callback. This file contains no feature-dependent pruning of the registered product. Custom-device creation is runtime setup, not an explicit `NotSupported` gate. It requests a universal queue and copies the context device-extension list. [Registration](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L670-L677), [custom-device setup](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L133-L162).

### Design-based pruning

- Only `exact_match` is registered; other match-control values are outside this family's scope.
- Only graphics and compute pipelines are registered.
- The source covers three pipeline requests at most, the fixed identifiers shown above, and the three identifier scenarios. Other identifier strings, batch sizes, and pipeline state combinations are not tested here.

## Key Takeaways

- The family tests application-provided pipeline identifiers during both graphics and compute pipeline creation.
- Missing or unknown identifiers must yield `VK_ERROR_NO_PIPELINE_MATCH`; in a multiple request, the unmatched first handle is null while matching later handles remain non-null.
- Equal identifiers under `VK_PIPELINE_MATCH_CONTROL_APPLICATION_UUID_EXACT_MATCH` must yield `VK_SUCCESS` and non-null handles.
- The main process establishes reservation state; the subprocess performs the direct checked create call.
- Shaders are setup-only inputs. Shader execution and shader output do not determine pass or fail.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Category registration | [createPipelineIdentifierTests](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L614-L685) | Defines the exact hierarchy and 12-leaf parameter product. |
| Graphics implementation | [testGraphicsPipelineIdentifier](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L164-L407) | Builds source state, performs the subprocess create call, and checks result/handles. |
| Compute implementation | [testComputePipelineIdentifier](../../../modules/vulkan/sc/vktPipelineIdentifierTests.cpp#L410-L609) | Provides the compute analogue and its oracle. |
| SC root registration | [SC createChildren](../../../modules/vulkan/sc/vktSafetyCriticalTests.cpp#L34-L47) | Places `pipeline_identifier` under the `sc` category. |
| Default SC mustpass | [sc.txt pipeline-identifier entries](../../../mustpass/main/vksc-default/sc.txt#L150-L161) | Confirms all registered leaves in the default package. |
