## Overview

**Core question:** When a physical device advertises tessellation shader support, does it report every baseline tessellation limit at or above the minimum required by Vulkan?

- This page covers the `tessellation.limits` test family implemented in [vktTessellationLimitsTests.cpp](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp).
- The family contains eight independent state-query test cases. Each case reads one `VkPhysicalDeviceLimits` member and compares it with the minimum encoded in the CTS registration table.
- These cases do not create a pipeline, compile a shader, or submit GPU work. They check the device properties reported by the Vulkan implementation.
- A supported case passes when the reported value is greater than or equal to its expected minimum. A device without `tessellationShader` support receives a not-supported result instead of a limit failure.

## Background Knowledge

- **Physical-device features and limits.** Features report whether an operation is supported; limits report numeric bounds for supported operations. The tessellation limit members used here are meaningful when the device supports `tessellationShader`.
- **Minimum requirement for a maximum limit.** A field named `max...` describes the largest value an implementation accepts. Vulkan can still require that maximum to reach a specified floor. For example, `maxTessellationPatchSize = 32` means the implementation must accept patch sizes through 32, while a larger reported maximum also satisfies the requirement.
- **Tessellation component counts.** The input and output limits count scalar components, not complete variables. A four-component vector consumes four components. Per-vertex and per-patch values describe different tessellation-control-shader interfaces, while the total-output limit covers their combined output budget.

## Registration Hierarchy

```text
tessellation.limits
├── max_tessellation_control_per_patch_output_components
├── max_tessellation_control_per_vertex_input_components
├── max_tessellation_control_per_vertex_output_components
├── max_tessellation_control_total_output_components
├── max_tessellation_evaluation_input_components
├── max_tessellation_evaluation_output_components
├── max_tessellation_generation_level
└── max_tessellation_patch_size
```

The source registers all eight test case leaves directly under `tessellation.limits`, and the Vulkan mustpass list contains the same eight paths.

## Parameter Dimensions and Observed Values

The test case leaf is the only registered dimension. It selects both the queried `VkPhysicalDeviceLimits` member and the minimum passed to the common comparison function.

| Test case leaf | Queried limit | Expected minimum | Meaning in this test | Evidence |
|----------------|---------------|-----------------:|----------------------|----------|
| `max_tessellation_generation_level` | `maxTessellationGenerationLevel` | `64` | Minimum required maximum generation level for the fixed-function tessellation primitive generator. | [case table](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L138), [limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L425-L429) |
| `max_tessellation_patch_size` | `maxTessellationPatchSize` | `32` | Minimum required maximum number of control points in a patch. | [case table](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L138), [limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L430-L438) |
| `max_tessellation_control_per_vertex_input_components` | `maxTessellationControlPerVertexInputComponents` | `64` | Minimum per-vertex input component capacity of the tessellation control shader. | [case table](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L138), [limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L439-L442) |
| `max_tessellation_control_per_vertex_output_components` | `maxTessellationControlPerVertexOutputComponents` | `64` | Minimum per-vertex output component capacity of the tessellation control shader. | [case table](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L138), [limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L443-L446) |
| `max_tessellation_control_per_patch_output_components` | `maxTessellationControlPerPatchOutputComponents` | `120` | Minimum per-patch output component capacity of the tessellation control shader. | [case table](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L138), [limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L447-L450) |
| `max_tessellation_control_total_output_components` | `maxTessellationControlTotalOutputComponents` | `2048` | Minimum total tessellation-control output component budget across per-vertex and per-patch outputs. | [case table](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L138), [limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L451-L454) |
| `max_tessellation_evaluation_input_components` | `maxTessellationEvaluationInputComponents` | `64` | Minimum per-vertex input component capacity of the tessellation evaluation shader. | [case table](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L138), [limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L455-L458) |
| `max_tessellation_evaluation_output_components` | `maxTessellationEvaluationOutputComponents` | `64` | Minimum per-vertex output component capacity of the tessellation evaluation shader. | [case table](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L121-L138), [limit definition](../../../../vulkan-docs/src/chapters/limits.adoc#L459-L462) |

The test constants match the baseline minima in the Vulkan limits table. Other specification configurations may impose higher minima, but this family checks the constants shown above.

## Behavior Parameters

The primary behavioral axis is the test case leaf. Every value follows the same query-and-compare path, but each selects a different tessellation capability bound.

### `max_tessellation_generation_level`: primitive-generation level

This case checks how finely the fixed-function tessellation primitive generator can tessellate a patch. The common test function reads `maxTessellationGenerationLevel` and requires a value of at least `64`.

### `max_tessellation_patch_size`: control points per patch

This case checks the largest patch, measured in vertices, that the tessellation control shader and primitive generator can process. It reads `maxTessellationPatchSize` and requires at least `32`.

### `max_tessellation_control_per_vertex_input_components`: control-stage per-vertex input

This case checks the component budget available for each input vertex entering the tessellation control shader. It reads `maxTessellationControlPerVertexInputComponents` and requires at least `64`.

### `max_tessellation_control_per_vertex_output_components`: control-stage per-vertex output

This case checks the component budget for each output vertex written by the tessellation control shader. It reads `maxTessellationControlPerVertexOutputComponents` and requires at least `64`.

### `max_tessellation_control_per_patch_output_components`: control-stage per-patch output

This case checks the component budget for outputs shared by the whole patch rather than attached to one output vertex. It reads `maxTessellationControlPerPatchOutputComponents` and requires at least `120`.

### `max_tessellation_control_total_output_components`: total control-stage output

This case checks the aggregate tessellation-control output budget, including per-vertex and per-patch components. It reads `maxTessellationControlTotalOutputComponents` and requires at least `2048`.

### `max_tessellation_evaluation_input_components`: evaluation-stage per-vertex input

This case checks the component budget for per-vertex data consumed by the tessellation evaluation shader. It reads `maxTessellationEvaluationInputComponents` and requires at least `64`.

### `max_tessellation_evaluation_output_components`: evaluation-stage per-vertex output

This case checks the component budget for per-vertex data emitted by the tessellation evaluation shader. It reads `maxTessellationEvaluationOutputComponents` and requires at least `64`.

## Shader Analysis

This test family reads physical-device properties without creating or executing shaders. There is no shader to walk through.

## Runtime Execution and Result Checking

- The dispatcher attaches `createLimitsTests()` directly under the `tessellation` test category. The factory creates the `limits` test family and registers one function case for each row of its static case table.
- Each test case queries `VkPhysicalDeviceFeatures`. If `tessellationShader` is false, the function throws `NotSupportedError` before reading or validating a tessellation limit.
- For a supported device, the function queries `VkPhysicalDeviceProperties` and selects one member of `properties.limits` according to the test case definition.
- `expectGreaterOrEqual()` logs the expected and reported values. It returns pass when `actual >= expected`; otherwise it returns fail with `Value doesn't meet minimal spec requirements`.

The test function uses the physical device and instance interface supplied by the CTS context. It creates no queue, command buffer, memory allocation, pipeline, descriptor, or readback resource for these cases, and it never accesses the context's logical-device interface.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `max_tessellation_generation_level` | The reported `maxTessellationGenerationLevel` is below `64`. |
| `max_tessellation_patch_size` | The reported `maxTessellationPatchSize` is below `32`. |
| `max_tessellation_control_per_vertex_input_components` | The reported `maxTessellationControlPerVertexInputComponents` is below `64`. |
| `max_tessellation_control_per_vertex_output_components` | The reported `maxTessellationControlPerVertexOutputComponents` is below `64`. |
| `max_tessellation_control_per_patch_output_components` | The reported `maxTessellationControlPerPatchOutputComponents` is below `120`. |
| `max_tessellation_control_total_output_components` | The reported `maxTessellationControlTotalOutputComponents` is below `2048`. |
| `max_tessellation_evaluation_input_components` | The reported `maxTessellationEvaluationInputComponents` is below `64`. |
| `max_tessellation_evaluation_output_components` | The reported `maxTessellationEvaluationOutputComponents` is below `64`. |

Across all eight leaves, the implementation advertises `tessellationShader` support but reports a related maximum below the floor checked by the CTS.

### Cause Analysis

#### Tessellation limit reported below the required minimum

**Possible failure symptoms:** The log shows the expected threshold and a smaller value returned through `VkPhysicalDeviceProperties::limits`. The selected test case then fails with `Value doesn't meet minimal spec requirements`. A device that reports `tessellationShader = false` does not produce this failure because the case stops as unsupported.

**Possible implementation causes:** The physical-device property query may expose an incorrect limit value, or the implementation may advertise `tessellationShader` even though its supported tessellation bounds do not reach the checked baseline minimum. This test only reads feature and property data, so it cannot distinguish an incorrect report from a capability shortfall behind that report. It does not exercise shader compilation, pipeline creation, tessellation execution, or rendered output.

## Case Pruning

### Requirement-based pruning

- All eight test cases require `tessellationShader`. When the feature is not supported, each case returns not-supported before the limit comparison.
- There are no separate per-case extension, format, stage, or resource requirements.

### Design-based pruning

- The source registers one case for each of eight tessellation limits. It does not generate combinations because each leaf selects one independent property and one fixed threshold.
- The family does not try values around each threshold or run workloads at the reported maximum. It checks the reported property value against the encoded minimum.

## Key Takeaways

- `tessellation.limits` is a state-query family with eight direct test case leaves. It has no shader or GPU execution path.
- Each leaf selects one `VkPhysicalDeviceLimits` member and its baseline threshold; larger reported values pass.
- A device without tessellation support receives a not-supported result. A failure means a supported device reported one of these limits below the checked minimum.
- See `## Failure Meaning` for the bounds of that diagnosis: the test establishes a reporting or advertised-capability inconsistency, but it does not localize the cause beyond the queried feature and property data.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test category attachment | [vktTessellationTests.cpp#L64-L80](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L64-L80) | Adds the `limits` test family under the `tessellation` test category. |
| Limit selectors and case definition | [vktTessellationLimitsTests.cpp#L45-L61](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L45-L61) | Defines the eight selectable limits and the expected-minimum field. |
| Comparison helper | [vktTessellationLimitsTests.cpp#L63-L71](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L63-L71) | Logs expected and actual values and implements the pass/fail comparison. |
| Feature query and property dispatch | [vktTessellationLimitsTests.cpp#L73-L112](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L73-L112) | Checks `tessellationShader`, queries physical-device properties, and selects the requested limit member. |
| Test case registration | [vktTessellationLimitsTests.cpp#L116-L143](../../../modules/vulkan/tessellation/vktTessellationLimitsTests.cpp#L116-L143) | Defines the eight names and thresholds, then registers their function cases. |
| Mustpass coverage | [tessellation.txt#L227-L234](../../../mustpass/main/vk-default/tessellation.txt#L227-L234) | Lists all eight `dEQP-VK.tessellation.limits.*` paths. |
| Vulkan tessellation limit meanings | [limits.adoc#L425-L462](../../../../vulkan-docs/src/chapters/limits.adoc#L425-L462) | Defines the semantic meaning of every queried `VkPhysicalDeviceLimits` member. |
| Feature dependency table | [limits.adoc#L6062-L6069](../../../../vulkan-docs/src/chapters/limits.adoc#L6062-L6069) | Associates all eight queried limit members with `tessellationShader`. |
| Baseline limit values | [limits.adoc#L6621-L6633](../../../../vulkan-docs/src/chapters/limits.adoc#L6621-L6633) | Shows the baseline minimum values that correspond to the CTS constants. |
