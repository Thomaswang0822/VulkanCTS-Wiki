# Understanding Brief: `conditional_rendering.dispatch`

## One-Sentence Test Purpose

This test checks whether conditional rendering executes or discards compute dispatch commands according to a 32-bit buffer predicate across direct, indirect, base, inherited-command-buffer, allocation-offset, and compute-queue cases.

## Background Knowledge

### Conditional rendering predicates

`VK_EXT_conditional_rendering` lets a command buffer bracket affected commands with `vkCmdBeginConditionalRenderingEXT` and `vkCmdEndConditionalRenderingEXT`. The implementation reads a 32-bit predicate from the supplied buffer and byte offset. Without inversion, zero discards affected commands and nonzero executes them. `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` reverses that decision [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2085-L2167), [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2255-L2269).

Why it matters here:

- Compute dispatch commands are in the set affected by conditional rendering.
- The predicate occupies four bytes even when its nonzero bit appears outside the first byte.
- The begin offset selects the predicate inside the buffer, while a memory allocation offset changes where the buffer is bound within its allocation.

### Secondary command buffer inheritance

A secondary command buffer can execute while conditional rendering is active in its primary command buffer only when its inheritance information enables conditional rendering. The `inheritedConditionalRendering` feature controls support for this behavior [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2103-L2116), [cmdbuffers.adoc](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L1285-L1318).

Why it matters here:

- Some cases begin conditional rendering in the primary command buffer and place dispatches in a secondary or nested secondary command buffer.
- Other cases begin and end conditional rendering inside the secondary command buffer.
- The test separates command placement from predicate meaning so either part can be checked.

## One Concrete Example

Consider `dEQP-VK.conditional_rendering.dispatch.condition_host_memory_expect_execution.dispatch`.

- The host creates a host-visible condition buffer containing the 32-bit value `1`.
- The primary command buffer begins conditional rendering without inversion.
- It records three `vkCmdDispatch(1, 1, 1)` calls.
- Each dispatch runs one compute invocation, and that invocation atomically adds one to an output counter.
- The host expects the counter to equal `3`. A value of `0` means the implementation discarded work that the predicate should have allowed. Any other value means the observed dispatch count was wrong.

## End-to-End Test Flow

```text
[host] choose a registration area, command variant, command-buffer placement, predicate value, inversion state, memory type, and queue
[host] create a four-byte output storage buffer, initialize its counter to zero, and bind it at descriptor binding 0
[host] create an indirect argument buffer containing one 1 x 1 x 1 dispatch command
[host] create the conditional-rendering buffer in host-visible memory or copy it to device-local memory
[host] record primary, secondary, and optional nested secondary command buffers as selected by the case
[host] begin conditional rendering in the selected command buffer, record one or three dispatches, then end conditional rendering
[device] execute or discard each affected dispatch according to the 32-bit predicate and inversion flag
[device] each executed compute invocation atomically increments the output counter once
[host] wait for completion, invalidate the output allocation, and compare the counter with the expected dispatch count or zero
```

The main generated cases submit three dispatches. The focused `condition_size`, `alloc_offset`, and `compute_queue` cases submit one dispatch [recordDispatch](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L160-L186), [registration](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L414-L755).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The test generates one fixed ESSL 3.10 compute shader. Its local size is `1 x 1 x 1`, and its only operation is `atomicAdd(count, 1u)` on a coherent storage-buffer member [initPrograms](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L121-L136).

The command variant changes host command recording, not shader source:

- `dispatch` records `vkCmdDispatch(1, 1, 1)`.
- `dispatch_indirect` records `vkCmdDispatchIndirect` using an indirect buffer that contains `{1, 1, 1}`.
- `dispatch_base` records `vkCmdDispatchBase(0, 0, 0, 1, 1, 1)` [recordDispatch](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L160-L186).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Conditional-rendering buffer | yes | passed to `vkCmdBeginConditionalRenderingEXT` | read as a 32-bit predicate | no | Controls whether affected dispatches execute. It may use host-visible or device-local memory, padding, and an allocation offset. |
| Output storage buffer | yes | descriptor set 0, binding 0 | atomically incremented by the compute shader | yes | Converts each executed dispatch into a count the host can check. |
| Indirect argument buffer | yes | argument to `vkCmdDispatchIndirect` | read as `{1, 1, 1}` dispatch dimensions | no | Exercises the indirect dispatch command path without changing shader work size. |
| Compute pipeline and descriptor set | yes | compute pipeline state | runs the fixed shader and exposes the output buffer | no | Provides the common execution and observation path for all command variants. |
| Primary, secondary, and nested secondary command buffers | yes | submitted or executed by another command buffer | contain conditional-rendering and dispatch commands | no | Exercise direct placement, inheritance, and nesting behavior. |

The helper fills padding bytes with `0x01`, writes the selected four-byte predicate at the chosen begin offset, and can bind the buffer at a nonzero allocation offset. For device-local cases, it copies the bytes from a host-visible staging buffer before use [createConditionalRenderingBuffer](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121), [beginConditionalRendering](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L124-L136).

## What Is Checked

The shader increments the output counter once per executed dispatch. The host derives one exact expected value:

- `numCalls` when `expectCommandExecution` is true;
- `0` when `expectCommandExecution` is false.

The host invalidates the output allocation and compares its first 32-bit word with that value. There is no tolerance or aggregation across cases [result check](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L368-L400).

Focused checks add these meanings:

- `condition_size` places a nonzero bit in each of the four predicate bytes and surrounds a zero predicate with nonzero padding.
- `alloc_offset` distinguishes zero from nonzero predicates when the buffer has a nonzero memory allocation offset.
- `compute_queue` repeats direct or indirect dispatch with host-visible or device-local predicates on a compute queue.

## Behavior Parameter Identification

> **Behavior parameter:** registered behavior area
>
> **Candidate values:** `condition_*` and `no_condition_*`, `condition_size`, `alloc_offset`, `compute_queue`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `condition_*` and `no_condition_*` | Incorrect predicate, inversion, command-buffer placement, inheritance, nesting, or dispatch-command handling in the shared condition matrix. |
| `condition_size` | The implementation did not read exactly the selected 32-bit predicate at the begin offset. |
| `alloc_offset` | The implementation used the wrong memory address when the condition buffer was bound at a nonzero allocation offset. |
| `compute_queue` | Conditional dispatch behavior failed on a compute queue for a direct or indirect command or for the selected predicate memory type. |

## Important Variations and Special Cases

- The shared condition matrix produces 60 direct children after four `clearInRenderPass` entries are removed. Each child has `dispatch`, `dispatch_indirect`, and `dispatch_base` leaves, for 180 cases.
- `condition_size` uses four command-buffer locations and five predicate layouts: `first_byte`, `second_byte`, `third_byte`, `fourth_byte`, and `padded_zero`, for 20 cases.
- `alloc_offset` combines four locations, zero or nonzero predicate state, and device-local or host-visible memory, for 16 cases.
- `compute_queue` combines four locations, four predicate/inversion outcomes, direct or indirect dispatch, and host-visible or device-local memory, for 64 cases.
- `dispatch_base` requires `VK_KHR_device_group`. Inherited cases require `inheritedConditionalRendering`; nested cases require `VK_EXT_nested_command_buffer`; primary-active inheritance also requires `VK_KHR_maintenance7`. Compute-queue cases require an available compute queue [checkSupport](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L138-L147), [shared capability checks](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L58).
- The mustpass file contains 280 executable paths for this test family [conditional-rendering.txt](../../../mustpass/main/vk-default/conditional-rendering.txt#L219-L498).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Predicate and inheritance semantics | [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2085-L2167) | Defines affected commands, active scope, inheritance, and 32-bit predicate interpretation. |
| Inversion semantics | [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2255-L2269) | Defines the inverted predicate decision. |
| Shader generation | [initPrograms](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L121-L136) | Emits the fixed counter shader. |
| Command selection | [recordDispatch](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L160-L186) | Records direct, indirect, or base dispatch commands. |
| Runtime and result checking | [iterate](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L188-L400) | Builds resources and command buffers, submits work, and checks the counter. |
| Main and focused registration | [ConditionalDispatchTests::init](../../../modules/vulkan/conditional_rendering/vktConditionalDispatchTests.cpp#L414-L755) | Builds all four behavior areas and their parameter combinations. |
| Shared condition matrix | [s_testsData](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) | Defines predicate, placement, inversion, inheritance, nesting, expected result, and memory combinations. |
| Condition buffer construction | [createConditionalRenderingBuffer](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121) | Implements padding, allocation offset, host-visible memory, and device-local staging. |
| Mustpass coverage | [conditional-rendering.txt](../../../mustpass/main/vk-default/conditional-rendering.txt#L219-L498) | Lists all 280 executable dispatch paths. |

## Questions / Risk Points for User Audit

- Does the `registered behavior area` axis make the four distinct implementations easier to compare than treating all 63 direct children as separate behaviors?
- Is the distinction between the begin offset inside a buffer and the buffer's allocation offset clear?
- Does the fixed counter shader receive enough attention without obscuring the host command-buffer behavior that this test targets?
- No unresolved semantic risk remains after checking source, mustpass registration, and the conditional-rendering specification.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.conditional_rendering.dispatch.condition_host_memory_expect_execution.dispatch` for the representative shader walkthrough because it shows the fixed counter shader with the simplest direct command path.
- Preserve the four-value behavior axis and copy the Failure Cause Mapping table unchanged.
- Distill conditional predicate and secondary inheritance concepts into short Background Knowledge bullets.
- Put the 63-child parseable hierarchy in the final page, but keep the explanatory narrative organized by four behavior areas.
- Keep source navigation in the appendix. Preserve the 280-case count, focused matrix sizes, support gates, and exact counter validation rule in the body.
