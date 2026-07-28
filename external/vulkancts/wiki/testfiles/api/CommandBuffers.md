## Overview

**Core question:** does the implementation correctly handle the full command buffer lifecycle across pool creation, primary and secondary buffer allocation, recording, submission, secondary execution, state transitions, and indirect dispatch alignment, under the documented flag, count, and offset combinations?

- Source file covered: [`vktApiCommandBuffersTests.cpp`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1).
- Test category: `api`. Test family: `command_buffers`. The family has no intermediate nodes; all 129 registered mustpass leaves are direct test case leaves of `api.command_buffers`.
- Core test idea: drive `vkCreateCommandPool`, `vkAllocateCommandBuffers`, `vkBeginCommandBuffer` / `vkEndCommandBuffer`, `vkQueueSubmit`, `vkCmdExecuteCommands`, `vkResetCommandPool` / `vkResetCommandBuffer`, and `vkTrimCommandPool` across the documented flag and parameter matrix, and verify behavior through event signaling, color-attachment readback, atomic counter readback, buffer-content comparison, and absence of crashes.
- The 64 `indirect_compute_dispatch_offsets_*` leaves form a generated 8×8 matrix that probes `vkCmdDispatchIndirect` alignment under paired memory and dispatch offsets.
- The remaining sections cover the behavioral groups, what each group changes, what is checked, and what a failure of each group means.

## Background Knowledge

- **Command pool ownership.** A `VkCommandPool` is the allocation unit that owns command buffer storage. Resetting or trimming the pool affects every command buffer allocated from it. Several tests in this family exercise pool reset and reuse, so the pool-level versus buffer-level distinction matters for interpreting `pool_reset_*` and `trim_command_pool_*` failures.
- **Primary versus secondary command buffers.** Primary command buffers (`VK_COMMAND_BUFFER_LEVEL_PRIMARY`) can be submitted directly to a queue. Secondary command buffers (`VK_COMMAND_BUFFER_LEVEL_SECONDARY`) cannot be submitted directly; they must be executed inside a primary through `vkCmdExecuteCommands`. Many leaves in this family rerun the same scenario at both levels (`allocate_*_primary` versus `allocate_*_secondary`, `record_*_primary` versus `record_*_secondary`); a level-specific failure points at the secondary-recording or execute path rather than the primary-recording path.
- **Command buffer states.** A command buffer moves between initial, recording, executable, and invalid states. `vkBeginCommandBuffer` transitions from initial or executable back to recording; `vkEndCommandBuffer` transitions to executable; `vkResetCommandBuffer` transitions back to initial. Destroying an object referenced by a pending recording transitions the buffer to invalid. The four `recording_to_*` / `executable_to_*` leaves verify each documented transition back to a usable state.
- **Usage flags.** `VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT` asserts a buffer will be submitted once; `VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT` allows the same buffer to be pending multiple times concurrently; `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` is required for secondary buffers that execute inside a render pass instance and supplies inheritance info. Several behavioral groups are distinguished by which usage flag they exercise.
- **Inheritance info.** `VkCommandBufferInheritanceInfo` carries render pass, subpass, framebuffer, and query state into a secondary command buffer. When a secondary is executed outside any render pass or without using the inheritance fields, the spec allows the implementation to ignore the pointer; the `bad_inheritance_info_*` leaves verify this robustness property.

## Registration Hierarchy

```text
api.command_buffers
├── pool_create_null_params
├── pool_create_non_null_allocator
├── pool_create_transient_bit
├── pool_create_reset_bit
├── pool_reset_release_res
├── pool_reset_no_flags_res
├── pool_reset_reuse
├── allocate_single_primary
├── allocate_many_primary
├── allocate_single_secondary
├── allocate_many_secondary
├── execute_small_primary
├── execute_large_primary
├── reset_implicit
├── trim_command_pool
├── trim_command_pool_secondary
├── record_single_primary
├── record_many_primary
├── record_single_secondary
├── record_many_secondary
├── record_many_draws_primary_1
├── record_many_draws_secondary_1
├── record_many_draws_primary_2
├── record_many_draws_secondary_2
├── submit_twice_primary
├── submit_twice_secondary
├── record_one_time_submit_primary
├── record_one_time_submit_secondary
├── render_pass_continue
├── nested_render_pass_continue
├── render_pass_continue_no_fb
├── record_simul_use_secondary_one_primary
├── record_simul_use_secondary_two_primary
├── record_simul_use_nested
├── record_simul_use_twice_nested
├── record_query_precise_w_flag
├── record_query_imprecise_w_flag
├── record_query_imprecise_wo_flag
├── bad_inheritance_info_random
├── bad_inheritance_info_random_cont
├── bad_inheritance_info_random_data
├── bad_inheritance_info_invalid_type
├── bad_inheritance_info_valid_nonsense_type
├── submit_count_non_zero
├── submit_count_equal_zero
├── submit_wait_single_semaphore
├── submit_wait_many_semaphores
├── submit_null_fence
├── submit_two_buffers_one_buffer_null_with_fence
├── secondary_execute
├── secondary_execute_twice
├── order_bind_pipeline
├── recording_to_ininitial
├── executable_to_ininitial
├── recording_to_invalid
├── executable_to_invalid
├── many_indirect_draws_on_secondary
├── many_indirect_disps_on_secondary
├── nested_execute
├── nested_execute_multiple_levels
├── secondary_push_constants_2
├── secondary_push_descriptor_set_2
├── secondary_push_descriptor_set_with_template
├── pipeline_shader_object_mix_with_secondaries
└── secondary_on_transfer_queue
```

The 64 generated `indirect_compute_dispatch_offsets_{memOffset}_{dispatchOffset}` leaves are direct children of `command_buffers` and are documented in `## Parameter Dimensions and Observed Values`. The family is created by [`createCommandBuffersTests()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6266) and attached to the `api` test category by [`vktApiTests.cpp#L107`](../../../modules/vulkan/api/vktApiTests.cpp#L107).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Command buffer level | `VK_COMMAND_BUFFER_LEVEL_PRIMARY`, `VK_COMMAND_BUFFER_LEVEL_SECONDARY` | Selects which level the buffer is allocated and recorded at. Several leaves rerun the same scenario at both levels. | [`vktApiCommandBuffersTests.cpp#L6285-L6288`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6285-L6288) |
| Pool create flags | `0`, `VK_COMMAND_POOL_CREATE_TRANSIENT_BIT`, `VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT` | Each pool_create_* and several recording leaves exercise one flag value. The reset bit is required for any test that calls `vkResetCommandBuffer` on an individual buffer. | [`vktApiCommandBuffersTests.cpp#L6270-L6276`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6270-L6276) |
| Pool reset flags | `0`, `VK_COMMAND_POOL_RESET_RELEASE_RESOURCES_BIT` | Distinguishes "reset keeping resources" from "reset releasing resources" on the pool_reset_* leaves. The release bit is non-VulkanSC only. | [`vktApiCommandBuffersTests.cpp#L6278-L6280`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6278-L6280) |
| Command buffer usage flags | `0`, `VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT`, `VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT`, `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` | Each recording behavioral group exercises one or a combination of these flags. | [`vktApiCommandBuffersTests.cpp#L6327-L6334`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6327-L6334) |
| Framebuffer hint | `true`, `false` | Selects whether `VkCommandBufferInheritanceInfo::framebuffer` is `VK_NULL_HANDLE` for the render_pass_continue leaves. | [`vktApiCommandBuffersTests.cpp#L6334-L6338`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6334-L6338) |
| Buffer allocation count | `1`, `1024`, `10000` (100 on Vulkan SC) | Drives allocate_*_many leaves. The 32-bit path uses 1024 and the 64-bit path uses 10000 to probe driver limits. | [`vktApiCommandBuffersTests.cpp#L607-L615`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L607-L615) |
| Large buffer command count | `10000` (`1000` on Vulkan SC) | Drives execute_large_primary, record_many_*, and record_large_secondary. Each iteration records a set/reset event pair. | [`vktApiCommandBuffersTests.cpp#L1164-L1168`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1164-L1168) |
| Bad inheritance info case | `RANDOM_PTR`, `RANDOM_PTR_CONTINUATION`, `RANDOM_DATA_PTR`, `INVALID_STRUCTURE_TYPE`, `VALID_NONSENSE_TYPE` | Each `bad_inheritance_info_*` leaf populates `VkCommandBufferBeginInfo::pInheritanceInfo` with one form of unused invalid data and checks that recording and execution still succeed. | [`vktApiCommandBuffersTests.cpp#L6359-L6373`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6359-L6373) |
| State transition | `STT_RECORDING_TO_INITIAL`, `STT_EXECUTABLE_TO_INITIAL`, `STT_RECORDING_TO_INVALID`, `STT_EXECUTABLE_TO_INVALID` | Each `recording_to_*` / `executable_to_*` leaf drives one transition, then verifies the buffer is usable again after `vkResetCommandBuffer`. | [`vktApiCommandBuffersTests.cpp#L4358-L4364`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4358-L4364) |
| Image extent for many-draws | `128×128`, `512×256` | Drives the four `record_many_draws_*` leaves. The larger extent is non-VulkanSC only. | [`vktApiCommandBuffersTests.cpp#L6309-L6325`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6309-L6325) |
| Submit count | `0`, `1`, `5` | Drives `submit_count_non_zero` (5), `submit_count_equal_zero` (0), and the per-buffer submit leaves (1). | [`vktApiCommandBuffersTests.cpp#L6375-L6377`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6375-L6377) |
| Indirect dispatch memory offset | `0, 4, 8, 12, 16, 20, 24, 28` | First axis of the 8×8 generated matrix. The storage buffer is bound at this offset within an allocated device memory object. | [`vktApiCommandBuffersTests.cpp#L6418-L6428`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6418-L6428) |
| Indirect dispatch offset | `0, 4, 8, 12, 16, 20, 24, 28` | Second axis of the 8×8 generated matrix. The byte offset passed to `vkCmdDispatchIndirect` within the indirect buffer. | [`vktApiCommandBuffersTests.cpp#L6418-L6428`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6418-L6428) |

The 64 `indirect_compute_dispatch_offsets_{memOffset}_{dispatchOffset}` leaves are generated by a nested loop over the two offset axes above ([`vktApiCommandBuffersTests.cpp#L6420-L6427`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6420-L6427)). Each leaf records a `vkCmdDispatchIndirect` on a secondary command buffer, with the storage buffer bound at `memOffset` inside an allocation and the dispatch command read from `dispatchOffset` inside the indirect buffer. The host then verifies that each of the 64 storage buffer slots holds the expected `gl_LocalInvocationIndex + 1000000` value.

## Behavior Parameters

The primary behavioral axis is the behavioral group: the 129 test case leaves cluster into groups that each exercise a distinct command buffer property. The groups follow the API section comments in the source file (`19.1` through `19.6` plus extension-driven groups).

### command_pool_create_reset — Pool creation and reset

Exercises `vkCreateCommandPool` with each documented create flag and `vkResetCommandPool` with each reset flag. Covers `pool_create_null_params`, `pool_create_non_null_allocator`, `pool_create_transient_bit`, `pool_create_reset_bit`, `pool_reset_release_res`, `pool_reset_no_flags_res`, and `pool_reset_reuse`. The reuse leaf records and submits two command buffers, resets the pool with the release bit, then re-records and re-submits to confirm that pool reset returns the buffers to a usable state. Implemented by [`createPoolNullParamsTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L380) through [`resetPoolReuseTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L511).

### buffer_lifetime — Allocation, execution, and implicit reset

Exercises `vkAllocateCommandBuffers` at primary and secondary levels with single and large counts, executes primary buffers via event signaling, and tests implicit reset by re-recording without an explicit reset call. Covers `allocate_single_primary`, `allocate_many_primary`, `allocate_single_secondary`, `allocate_many_secondary`, `execute_small_primary`, `execute_large_primary`, and `reset_implicit`. The `trim_command_pool` and `trim_command_pool_secondary` leaves exercise `vkTrimCommandPool` across 300 allocation/recording/free cycles. Implemented by [`allocatePrimaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L564) through [`resetBufferImplicitlyTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L830) and [`trimCommandPoolTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L999).

### recording — Recording primary and secondary buffers

Exercises `vkBeginCommandBuffer` / `vkEndCommandBuffer` with small and large command counts at both levels. The large leaves record 5000 set/reset event pairs. Covers `record_single_primary`, `record_many_primary`, `record_single_secondary`, `record_many_secondary`. Implemented by [`recordSinglePrimaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1088) through [`recordLargeSecondaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1241).

### many_draws — Many draws in one buffer

Exercises a single command buffer that records one triangle draw per output pixel and verifies color and stencil output through readback. The four leaves vary command buffer level (primary/secondary) and image extent (128×128, 512×256). Implemented by the [`ManyDrawsCase`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4713) test case class and `ManyDrawsInstance::iterate`. The 512×256 leaves are non-VulkanSC only.

### submit_twice_and_one_time — Submit semantics

Exercises submitting the same buffer twice and the `VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT` flag at both levels. Covers `submit_twice_primary`, `submit_twice_secondary`, `record_one_time_submit_primary`, `record_one_time_submit_secondary`. Implemented by [`submitPrimaryBufferTwiceTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1337) through [`oneTimeSubmitFlagSecondaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1594).

### render_pass_continue — Render pass continue behavior

Exercises `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` with optional framebuffer hint, including nested command buffer variants gated by `VK_EXT_nested_command_buffer` or `VK_KHR_maintenance7`. Covers `render_pass_continue`, `nested_render_pass_continue`, `render_pass_continue_no_fb`. Verification is by color attachment readback compared against the clear value. Implemented by [`renderPassContinueTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1726) and [`renderPassContinueNestedTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1926).

### simultaneous_use — Concurrent execution of the same buffer

Exercises `VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT` by executing the same secondary buffer multiple times within one primary, across two primaries, and in nested configurations. Verification uses a compute shader that atomically increments a counter; the host checks that the counter reached the expected number of executions. Covers `record_simul_use_secondary_one_primary`, `record_simul_use_secondary_two_primary`, `record_simul_use_nested`, `record_simul_use_twice_nested`. Implemented by [`simultaneousUseSecondaryBufferOnePrimaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1778) through [`simultaneousUseNestedSecondaryBufferTwiceTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2205).

### query_recording — Occlusion query recording in secondary buffers

Exercises `vkCmdBeginQuery` / `vkCmdEndQuery` with precise and imprecise query control flags, gated by the `inheritedQueries` feature. Covers `record_query_precise_w_flag`, `record_query_imprecise_w_flag`, `record_query_imprecise_wo_flag`. Implemented by [`recordBufferQueryPreciseWithFlagTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2714) through [`recordBufferQueryImpreciseWithoutFlagTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2892).

### bad_inheritance_info — Robustness to unused invalid inheritance data

Exercises the spec rule that an unused `pInheritanceInfo` pointer is not dereferenced. Each leaf populates the pointer with random garbage, random data, an invalid structure type, or a valid-but-wrong structure type, and verifies that recording and execution still succeed. The compute shader increments a counter that the host checks. Implemented by [`badInheritanceInfoTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2371) parameterized over the `BadInheritanceInfoCase` enum at [`vktApiCommandBuffersTests.cpp#L6359-L6373`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6359-L6373).

### submission — Queue submission edge cases

Exercises `vkQueueSubmit` with non-zero and zero submit counts, single and many wait semaphores, a null fence, and one null buffer with a fence. The zero-count leaf verifies that the first submission is ignored when `submitCount=0`. Implemented by [`submitBufferCountNonZero()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2982) through [`submitTwoBuffersOneBufferNullWithFence()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3555).

### secondary_execution — Secondary command buffer execution

Exercises `vkCmdExecuteCommands` once and twice across separate primary submissions, plus nested execution of secondaries within secondaries via `VK_EXT_nested_command_buffer`. Covers `secondary_execute`, `secondary_execute_twice`, `nested_execute`, `nested_execute_multiple_levels`. Implemented by [`executeSecondaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3647), [`executeSecondaryBufferTwiceTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3978), [`executeNestedBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3741), and [`executeMultipleLevelsNestedBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3871).

### pipeline_binding_order — Pipeline binding order

Exercises the rule that the last bound pipeline before a dispatch is the one that executes. Two compute pipelines are bound in sequence; only the second should run. Verification compares four `vec4` result values against the colors that the second pipeline writes. Implemented by [`orderBindPipelineTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4144).

### state_transitions — Command buffer state transitions

Exercises the four documented transitions back to a usable state: recording→initial, executable→initial, recording→invalid (by destroying a referenced render pass), executable→invalid (by destroying a referenced event). After each transition, `vkResetCommandBuffer` returns the buffer to initial, and a fresh recording/submission cycle verifies the buffer is usable. Implemented by [`executeStateTransitionTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4366) parameterized over the `StateTransitionTest` enum at [`vktApiCommandBuffersTests.cpp#L4358-L4364`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4358-L4364).

### many_indirect — Many indirect draws and dispatches on secondary

Exercises a secondary command buffer recording many `vkCmdDrawIndirect` (4096 draws over a 64×64 image) or `vkCmdDispatchIndirect` (4096 dispatches) calls. The draws leaf verifies color output by readback; the dispatches leaf verifies 4096 storage buffer slots. Implemented by [`manyIndirectDrawsTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5313) and [`manyIndirectDispatchesTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5458).

### indirect_dispatch_alignment — Indirect dispatch alignment matrix

Exercises `vkCmdDispatchIndirect` across the 8×8 memory-offset × dispatch-offset matrix. The 64 leaves are generated by [`IndirectDispatchAlignmentCase`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5592); each verifies 64 storage buffer slots against `gl_LocalInvocationIndex + 1000000`.

### secondary_extras — Secondary command buffers with extra commands

Exercises secondary command buffers that use `VK_KHR_maintenance6` push constants and `VK_KHR_push_descriptor` push descriptor sets, with and without `VK_KHR_descriptor_update_template`. The cases destroy some structures before the primary is recorded to catch capture/replay use-after-free in Mesa-style drivers. Covers `secondary_push_constants_2`, `secondary_push_descriptor_set_2`, `secondary_push_descriptor_set_with_template`. Implemented by [`secCmdExtraCaseTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5802). Non-VulkanSC only.

### pipeline_shader_object_mix — Mixing pipelines and shader objects with secondaries

Exercises interleaving `vkCmdBindPipeline` (compute) on the primary with `vkCmdBindShadersEXT` (`VK_EXT_shader_object`) on a secondary, then dispatching from both. Verifies that specialization constants route the correct values into each slot of the output buffer. Implemented by [`PipelineShaderObjMixSecondariesRun()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6022). Non-VulkanSC only.

### secondary_on_transfer_queue — Secondary execution on a transfer queue

Exercises `vkCmdExecuteCommands` on a transfer-only queue family. A primary copies source→staging then executes a secondary that copies staging→destination, separated by a pipeline barrier. Verifies that the destination buffer matches the source. Implemented by [`SecondariesXferQueueRun()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6199).

## Shader Analysis

No shader walkthrough is provided for this page. Several behavioral groups use compute or graphics shaders as observation tools (atomic counter increment, color output, specialized constant routing), but the shader logic is not what is being tested; the tested behavior is command buffer lifecycle, recording, submission, and execution. The shader source is small and visible at [`genComputeSource()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4471), [`genComputeIncrementSource()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4529), and the inline program strings in [`ManyDrawsCase::initPrograms()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4891), [`initManyIndirectDrawsPrograms()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5293), [`initManyIndirectDispatchesPrograms()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5438), [`IndirectDispatchAlignmentCase::initPrograms()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5619), [`secCmdExtraCaseInitPrograms()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5786), and [`PipelineShaderObjMixSecondariesPrograms()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6010).

## Runtime Execution and Result Checking

The host side of every leaf follows one of a small number of templates:

- **Pool and allocation leaves.** Create the pool or buffers, optionally submit a buffer that records `vkCmdSetEvent`, then check that no error was returned by `VK_CHECK`. The `pool_reset_reuse` and `trim_command_pool_*` leaves add repeated allocation/recording/free cycles with a final `vkTrimCommandPool` call, and pass if no crash or unexpected `VkResult` occurs ([`resetPoolReuseTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L511), [`trimCommandPoolTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L999)).
- **Event signaling leaves.** Record `vkCmdSetEvent` in a primary or secondary buffer, submit, then poll `vk.getEventStatus`. Pass only if `VK_EVENT_SET` is returned ([`executePrimaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L712), [`recordLargePrimaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1126), [`submitBufferCountNonZero()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2982)). The `submit_count_equal_zero` leaf inverts the check: it passes only if the first event is **not** signaled, because `submitCount=0` must be ignored ([`submitBufferCountEqualZero()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3074)).
- **Color attachment readback leaves.** Begin a render pass, execute a secondary that clears attachments or draws primitives, end the pass, copy the color attachment to a host-visible buffer, and compare each pixel against the expected clear or draw color ([`renderPassContinueTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1725), [`ManyDrawsInstance::iterate()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4927)).
- **Atomic counter readback leaves.** Bind a storage buffer with a `coherent uint count;` field, dispatch a compute shader that calls `atomicAdd(b_in_out.count, 1u)`, issue a `VK_ACCESS_SHADER_WRITE_BIT` → `VK_ACCESS_HOST_READ_BIT` barrier, and read the counter. Pass only if the counter equals the expected number of dispatches ([`simultaneousUseSecondaryBufferOnePrimaryBufferTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1778), [`badInheritanceInfoTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2371)).
- **Buffer content comparison leaves.** Dispatch a compute shader that writes known values into a storage buffer, copy back, and compare against the reference. The reference is `gl_LocalInvocationIndex + 1000000` for the indirect dispatch alignment matrix, the `vec4` colors written by the second-bound pipeline for `order_bind_pipeline`, and 4096 indexed values for `many_indirect_disps_on_secondary` ([`orderBindPipelineTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4144), [`manyIndirectDispatchesTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5458), [`IndirectDispatchAlignmentInstance::iterate()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5637)).
- **State transition leaves.** Drive one of the four transitions, call `vkResetCommandBuffer(*cmdBuffer, 0u)`, then begin, record `vkCmdSetEvent`, end, and submit. Pass only if the post-reset execution signals the event ([`executeStateTransitionTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4366)).

Final pass/fail is always derived from one of these checks; the test does not aggregate results across leaves.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `command_pool_create_reset` | Pool or reset API returns unexpected `VkResult`; pool reset leaves return buffers to an unusable state |
| `buffer_lifetime` | Allocation fails at scale; event not signaled after submit; trim crashes or corrupts subsequent allocations |
| `recording` | `vkBeginCommandBuffer` / `vkEndCommandBuffer` returns unexpected error on a large recording; event not signaled after submit |
| `many_draws` | Color or stencil mismatch after many draws in one buffer; out-of-memory at allocation time |
| `submit_twice_and_one_time` | One-time-submit buffer accepted on second submit; same buffer submitted twice but only one execution observed |
| `render_pass_continue` | Color attachment does not match expected clear value; nested command buffer execution rejected by `VK_EXT_nested_command_buffer` or `VK_KHR_maintenance7` |
| `simultaneous_use` | Atomic counter does not reach the expected number of executions, indicating one or more simultaneous instances did not run |
| `query_recording` | `vkCmdBeginQuery` / `vkCmdEndQuery` rejected on a secondary buffer with the inherited-queries feature enabled |
| `bad_inheritance_info` | Implementation dereferences the unused `pInheritanceInfo` pointer or rejects the begin call, instead of ignoring the unused data |
| `submission` | `vkQueueSubmit` with `submitCount=0` signals the first event anyway; semaphore wait, null fence, or null-buffer-with-fence handling is wrong |
| `secondary_execution` | `vkCmdExecuteCommands` does not run the secondary buffer; nested execution rejected by `VK_EXT_nested_command_buffer` |
| `pipeline_binding_order` | Result `vec4` values match the first-bound (bad) pipeline instead of the second-bound (good) pipeline |
| `state_transitions` | Command buffer is not usable after `vkResetCommandBuffer` following a transition to invalid or back to initial |
| `many_indirect` | Storage buffer slots do not match expected values; 4096 indirect draws produce wrong color output |
| `indirect_dispatch_alignment` | Storage buffer slot mismatch on a specific `memOffset`/`dispatchOffset` pair, indicating an alignment or offset-handling bug in `vkCmdDispatchIndirect` |
| `secondary_extras` | Output `vec4` does not match expected, indicating a push-constant, push-descriptor, or template use-after-free defect on secondary command buffers |
| `pipeline_shader_object_mix` | Output buffer slots do not match `{1, 2, 1}`, indicating incorrect specialization-constant routing between pipeline and shader object paths |
| `secondary_on_transfer_queue` | Destination buffer does not match source, indicating that secondary execution on a transfer-only queue mishandles the barrier or copy |

### Cause Analysis

#### API returns unexpected VkResult

**Possible failure symptoms:** a `VK_CHECK(...)` macro reports a non-`VK_SUCCESS` return value from `vkCreateCommandPool`, `vkResetCommandPool`, `vkAllocateCommandBuffers`, `vkBeginCommandBuffer`, `vkEndCommandBuffer`, `vkQueueSubmit`, `vkQueueWaitIdle`, or `vkResetCommandBuffer`. The test terminates with the framework's `VK_CHECK` failure message.

**Possible implementation causes:** the driver rejected a parameter combination that the spec requires it to accept (for example, a pool create with `VK_COMMAND_POOL_CREATE_TRANSIENT_BIT`, or a secondary buffer begin with `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` and a null framebuffer). A consistent failure restricted to one flag or parameter value points at a driver-side defect in that code path. Source-level investigation is needed before claiming a hardware or driver root cause for any single `VkResult`.

#### Event not signaled after submit

**Possible failure symptoms:** the test records `vk.cmdSetEvent`, submits, waits on a fence, then calls `vk.getEventStatus` and the result is not `VK_EVENT_SET`. The leaf returns a fail status with a string such as `"Execute Primary Command Buffer FAILED"` or `"An event was not set."`.

**Possible implementation causes:** the submitted command buffer did not execute, the event set command was not recorded correctly, or the host-side wait returned before the device finished executing. Because the test always uses `submitCommandsAndWait` (which calls `vkQueueWaitIdle` or waits on a fence), host/device ordering is not the likely cause; the failure more often indicates that the recorded commands were dropped or that the implementation incorrectly advanced the command buffer through its state machine.

#### Counter mismatch on simultaneous-use dispatches

**Possible failure symptoms:** `simultaneousUse*` leaves read the atomic counter from the result buffer and find a value smaller than the expected number of dispatches (1, 2, or 4 depending on the leaf).

**Possible implementation causes:** the implementation did not honor `VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT`, so one or more invocations of the secondary buffer were skipped or serialized in a way that dropped an `atomicAdd`. The compute shader itself is trivial and is not the variable being tested; the variable is whether the same secondary buffer can be pending more than once at the same time.

#### Color or stencil mismatch on readback

**Possible failure symptoms:** `render_pass_continue`, `nested_render_pass_continue`, `record_many_draws_*`, or `many_indirect_draws_on_secondary` reads back the color or stencil attachment and finds a pixel that does not match the reference. `renderPassContinueTest` reports `"clear value mismatch"`; the many-draws instance reports `"Mismatched output and reference color or stencil; please check test log --"`.

**Possible implementation causes:** the secondary command buffer's `vkCmdClearAttachments` or draw commands did not execute, the render pass instance did not load or store the attachment as expected, or, for the many-draws leaves, the implementation dropped one or more of the per-pixel draw calls. A mismatch confined to the stencil channel points at the stencil state configuration in the many-draws pipeline; a mismatch across the whole image points at the secondary execution or render pass continue path.

#### Bad inheritance info dereference

**Possible failure symptoms:** `badInheritanceInfoTest` reports `"Invalid value found in results buffer (expected value 1u but found <N>)"`, or the test crashes during `vkBeginCommandBuffer`.

**Possible implementation causes:** the implementation dereferenced the `pInheritanceInfo` pointer even though the spec requires it to be ignored when the secondary command buffer is not executed inside a render pass and the inheritance fields are not used. The five `BadInheritanceInfoCase` variants cover random pointer, random pointer with the render-pass-continue flag set, random data inside a valid struct, an invalid `sType`, and a valid `sType` from an unrelated structure. A failure on `RANDOM_PTR_CONTINUATION` indicates the implementation read the inheritance info when the `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` flag was set without an actual render pass.

#### Submit count handling

**Possible failure symptoms:** `submit_count_equal_zero` returns a fail with `"The first event was signaled."`, meaning the implementation executed the command buffer even though `submitCount=0` was passed to `vkQueueSubmit`.

**Possible implementation causes:** the implementation did not ignore a zero `submitCount` as required by the spec. The leaf records a command buffer, submits with `submitCount=0`, then submits a second buffer with `submitCount=1`; the first event must remain unset.

#### State transition reset failure

**Possible failure symptoms:** `executeStateTransitionTest` reports `"Submit failed"` after `vkResetCommandBuffer(*cmdBuffer, 0u)` followed by a fresh begin/record/end/submit cycle.

**Possible implementation causes:** the implementation did not return the command buffer to the initial state after the documented transition, or did not allow a buffer in the invalid state (after destroying a referenced render pass or event) to be reset and reused. The four `StateTransitionTest` variants isolate the transition: recording→initial, executable→initial, recording→invalid, executable→invalid. A failure on the invalid variants indicates that destroying a referenced object did not correctly invalidate the buffer or that `vkResetCommandBuffer` cannot recover from the invalid state.

#### Indirect dispatch alignment mismatch

**Possible failure symptoms:** an `indirect_compute_dispatch_offsets_*` leaf reports `"Unexpected value found at position <i>: expected <ref> but found <val>"` for one or more slots in the 64-element storage buffer.

**Possible implementation causes:** `vkCmdDispatchIndirect` read the dispatch command from the wrong offset, the storage buffer was bound at the wrong memory offset, or the implementation's alignment handling for one of the `memOffset`/`dispatchOffset` pairs differs from the spec-required behavior. The 8×8 matrix surfaces alignment defects that only appear at non-zero offsets. Source-level investigation is needed to identify which offset axis is mishandled before claiming a driver root cause.

#### Secondary extras output mismatch

**Possible failure symptoms:** `secCmdExtraCaseTest` reports `"Unexpected result in output buffer: expected <ref> but found <result>"`, or the test crashes during primary recording after the descriptor update template was destroyed.

**Possible implementation causes:** a Mesa-style capture/replay secondary-command-buffer implementation kept a pointer to a structure (push constant data, push descriptor info, or descriptor update template) that was destroyed before the primary command buffer was recorded, producing a use-after-free. The test destroys the template before recording the primary for the `PUSH_DESCRIPTOR_SET_WITH_TEMPLATE` case. The failure could also indicate incorrect `VK_KHR_maintenance6` push-constant handling or `VK_KHR_push_descriptor` push-descriptor-set handling on secondary command buffers.

#### Pipeline and shader object specialization mismatch

**Possible failure symptoms:** `pipeline_shader_object_mix_with_secondaries` reports `"Unexpected values found in output buffer; check log for details --"` because the three output slots do not equal `{1, 2, 1}`.

**Possible implementation causes:** specialization constants were not applied correctly when the same compute shader was used both through a `VkPipeline` (specialized to write `1`) and through a `VK_EXT_shader_object` shader object (specialized to write `2`), or the binding state was not correctly partitioned between the primary and the executed secondary. A result of `{1, 1, 1}` indicates the shader object specialization was ignored; a result of `{2, 2, 2}` indicates the pipeline specialization was ignored.

#### Transfer queue secondary execution mismatch

**Possible failure symptoms:** `secondary_on_transfer_queue` reports `"Expected <src> but found <dst>"` after copying source→staging on the primary, executing a secondary that copies staging→destination, and reading back the destination.

**Possible implementation causes:** the secondary command buffer's `vkCmdCopyBuffer` did not execute on the transfer-only queue family, or the pipeline barrier between the primary's staging write and the secondary's staging read did not establish the required `VK_ACCESS_TRANSFER_WRITE_BIT` → `VK_ACCESS_TRANSFER_READ_BIT` availability and visibility. The test uses a staging buffer and an inter-copy barrier to catch driver bugs in barrier handling across primary/secondary boundaries on transfer queues.

## Case Pruning

### Requirement-based pruning

- **Events.** Leaves that rely on `vkCmdSetEvent` and `vk.getEventStatus` are gated by [`checkEventSupport()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4555), which throws `NotSupportedError` when `VK_KHR_portability_subset` is enabled without the `events` feature.
- **`VK_KHR_maintenance1`.** `trim_command_pool` and `trim_command_pool_secondary` require `VK_KHR_maintenance1` ([`trimCommandPoolTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L999)).
- **`VK_EXT_nested_command_buffer` or `VK_KHR_maintenance7`.** `nested_render_pass_continue`, `nested_execute`, and `nested_execute_multiple_levels` require either `VK_EXT_nested_command_buffer` with `nestedCommandBuffer` (and `nestedCommandBufferRendering` for the render pass variant) or `VK_KHR_maintenance7` with the `maintenance7` feature enabled ([`renderPassContinueNestedTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1926), [`checkNestedCommandBufferSupport`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6409)).
- **`inheritedQueries` feature.** `record_query_precise_w_flag`, `record_query_imprecise_w_flag`, and `record_query_imprecise_wo_flag` are gated by `context.getDeviceFeatures().inheritedQueries` ([`recordBufferQueryPreciseWithFlagTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6272)).
- **`VK_KHR_maintenance6`.** `secondary_push_constants_2` and `secondary_push_descriptor_set_2` require `VK_KHR_maintenance6` ([`secCmdExtraCaseSupportCheck()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5773)).
- **`VK_KHR_push_descriptor`.** `secondary_push_descriptor_set_2` and `secondary_push_descriptor_set_with_template` require `VK_KHR_push_descriptor` ([`secCmdExtraCaseSupportCheck()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5773)).
- **`VK_KHR_descriptor_update_template`.** `secondary_push_descriptor_set_with_template` requires `VK_KHR_descriptor_update_template` ([`secCmdExtraCaseSupportCheck()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5773)).
- **`VK_EXT_shader_object`.** `pipeline_shader_object_mix_with_secondaries` requires `VK_EXT_shader_object` ([`PipelineShaderObjMixSecondariesCheck()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6005)).
- **Transfer queue.** `secondary_on_transfer_queue` is gated by [`SecondariesXferQueueCheckSupport()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6190), which throws `NotSupportedError` when no transfer-only queue family is available.
- **Compute queue.** `many_indirect_disps_on_secondary` and the `indirect_compute_dispatch_offsets_*` matrix are gated by `context.getComputeQueue()` / `context.getComputeQueueFamilyIndex()` ([`checkManyIndirectDispatchesSupport()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5451), [`IndirectDispatchAlignmentCase::checkSupport()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5613)).
- **`VK_KHR_timeline_semaphore` and simultaneous use.** `secondary_execute_twice` is gated by [`checkEventAndTimelineSemaphoreAndSimultaneousUseAndSecondaryCommandBufferNullFramebufferSupport()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6388-L6390), which requires timeline semaphore support and the simultaneous-use property on Vulkan SC.
- **Vulkan SC `commandPoolResetCommandBuffer` property.** `reset_implicit` and the four state-transition leaves are gated by the `commandPoolResetCommandBuffer` property on Vulkan SC ([`resetBufferImplicitlyTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L830), [`executeStateTransitionTest()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4366)).
- **Vulkan SC `secondaryCommandBufferNullOrImagelessFramebuffer` property.** Several secondary-buffer leaves are gated by this property on Vulkan SC through `checkSecondaryCommandBufferNullOrImagelessFramebufferSupport()`.

### Design-based pruning

- The non-null allocator, pool reset release-resources, pool reset reuse, trim, `record_many_draws_*_2`, `secondary_extras`, and `pipeline_shader_object_mix_with_secondaries` leaves are excluded on Vulkan SC through `#ifndef CTS_USES_VULKANSC` ([`vktApiCommandBuffersTests.cpp#L6271-L6273`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6271-L6273), [`vktApiCommandBuffersTests.cpp#L6277-L6283`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6277-L6283), [`vktApiCommandBuffersTests.cpp#L6293-L6298`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6293-L6298), [`vktApiCommandBuffersTests.cpp#L6317-L6325`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6317-L6325), [`vktApiCommandBuffersTests.cpp#L6430-L6452`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6430-L6452)).
- Large iteration counts are reduced on Vulkan SC: `10000` command buffers becomes `100`, `10000` set/reset event pairs becomes `1000`, and `10000` large-buffer events becomes `100` ([`vktApiCommandBuffersTests.cpp#L607-L615`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L607-L615), [`vktApiCommandBuffersTests.cpp#L769-L774`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L769-L774), [`vktApiCommandBuffersTests.cpp#L1164-L1168`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1164-L1168)).
- The indirect dispatch alignment matrix uses fixed offset values `{0, 4, 8, 12, 16, 20, 24, 28}` and a fixed storage buffer slot count of 64; no other offset or slot combinations are generated ([`vktApiCommandBuffersTests.cpp#L6418`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6418)).
- `submit_count_non_zero` uses a fixed `BUFFER_COUNT` of 5; `submit_count_equal_zero` uses 2; `secondary_execute_twice` uses 10 secondaries. These counts are not parameterized ([`vktApiCommandBuffersTests.cpp#L2989`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2989), [`vktApiCommandBuffersTests.cpp#L3081`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3081), [`vktApiCommandBuffersTests.cpp#L3980`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3980)).
- The `record_many_draws_*` leaves use two fixed image extents (`128×128` and `512×256`) rather than a generated extent matrix ([`vktApiCommandBuffersTests.cpp#L6309-L6325`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6309-L6325)).

## Key Takeaways

- The `command_buffers` family proves that the implementation handles the full command buffer lifecycle across pool creation, primary and secondary allocation, recording, submission, and reset, with verification through event signaling, color attachment readback, atomic counter readback, buffer content comparison, and absence of crashes.
- The 64 generated `indirect_compute_dispatch_offsets_*` leaves form the only generated matrix in the family; they probe `vkCmdDispatchIndirect` alignment at every paired memory and dispatch offset in `{0, 4, 8, 12, 16, 20, 24, 28}`².
- The four `recording_to_*` and `executable_to_*` leaves are the only leaves that test state machine recovery through `vkResetCommandBuffer`; a failure here means a buffer in the invalid or initial state could not be reused.
- The five `bad_inheritance_info_*` leaves verify a spec robustness rule: an unused `pInheritanceInfo` pointer must not be dereferenced. A failure here is a driver-side dereference bug, not a shader or execution bug.
- The `secondary_extras`, `pipeline_shader_object_mix_with_secondaries`, and `secondary_on_transfer_queue` leaves exercise recent extension and queue-family interactions that are more likely to expose driver bugs than the legacy lifecycle leaves.
- See `## Failure Meaning` for the per-cause failure analysis.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createCommandBuffersTests()` | [`vktApiCommandBuffersTests.cpp#L6266`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6266) | Top-level registration for the `command_buffers` test family; adds all 129 test case leaves and the 64-case generated matrix. |
| Parent registration | [`vktApiTests.cpp#L107`](../../../modules/vulkan/api/vktApiTests.cpp#L107) | `apiTests->addChild(createCommandBuffersTests(testCtx))` attaches the family to the `api` test category. |
| `createPoolNullParamsTest()` | [`vktApiCommandBuffersTests.cpp#L380`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L380) | Pool creation leaves. |
| `resetPoolReuseTest()` | [`vktApiCommandBuffersTests.cpp#L511`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L511) | Pool reset and reuse leaf. |
| `trimCommandPoolTest()` | [`vktApiCommandBuffersTests.cpp#L999`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L999) | Trim leaves, parameterized by command buffer level. |
| `allocatePrimaryBufferTest()` | [`vktApiCommandBuffersTests.cpp#L564`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L564) | Allocation leaves. |
| `executePrimaryBufferTest()` | [`vktApiCommandBuffersTests.cpp#L712`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L712) | Primary buffer execution via event signaling. |
| `resetBufferImplicitlyTest()` | [`vktApiCommandBuffersTests.cpp#L830`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L830) | Implicit reset by re-recording. |
| `recordSinglePrimaryBufferTest()` | [`vktApiCommandBuffersTests.cpp#L1088`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1088) | Recording leaves. |
| `recordLargeSecondaryBufferTest()` | [`vktApiCommandBuffersTests.cpp#L1241`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1241) | Large secondary recording with embedded `cmdExecuteCommands`. |
| `submitPrimaryBufferTwiceTest()` | [`vktApiCommandBuffersTests.cpp#L1337`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1337) | Submit-twice leaves. |
| `oneTimeSubmitFlagPrimaryBufferTest()` | [`vktApiCommandBuffersTests.cpp#L1519`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1519) | One-time submit leaves. |
| `renderPassContinueTest()` | [`vktApiCommandBuffersTests.cpp#L1725`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1725) | Render pass continue leaves, parameterized by framebuffer hint. |
| `renderPassContinueNestedTest()` | [`vktApiCommandBuffersTests.cpp#L1926`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1926) | Nested render pass continue leaf. |
| `simultaneousUseSecondaryBufferOnePrimaryBufferTest()` | [`vktApiCommandBuffersTests.cpp#L1778`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1778) | Simultaneous-use leaves. |
| `badInheritanceInfoTest()` | [`vktApiCommandBuffersTests.cpp#L2371`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2371) | Bad inheritance info leaves, parameterized by `BadInheritanceInfoCase`. |
| `recordBufferQueryPreciseWithFlagTest()` | [`vktApiCommandBuffersTests.cpp#L2714`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2714) | Query recording leaves. |
| `submitBufferCountNonZero()` | [`vktApiCommandBuffersTests.cpp#L2982`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2982) | Submission count leaves. |
| `submitBufferCountEqualZero()` | [`vktApiCommandBuffersTests.cpp#L3074`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3074) | Zero-count submit leaf; inverts the event check. |
| `submitBufferWaitSingleSemaphore()` | [`vktApiCommandBuffersTests.cpp#L3178`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3178) | Semaphore wait leaves. |
| `submitBufferNullFence()` | [`vktApiCommandBuffersTests.cpp#L3451`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3451) | Null-fence submit leaf. |
| `submitTwoBuffersOneBufferNullWithFence()` | [`vktApiCommandBuffersTests.cpp#L3555`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3555) | Null-buffer-with-fence submit leaf. |
| `executeSecondaryBufferTest()` | [`vktApiCommandBuffersTests.cpp#L3647`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3647) | Secondary execution leaf. |
| `executeNestedBufferTest()` | [`vktApiCommandBuffersTests.cpp#L3741`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3741) | Nested execution leaf. |
| `executeMultipleLevelsNestedBufferTest()` | [`vktApiCommandBuffersTests.cpp#L3871`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3871) | Multi-level nested execution leaf. |
| `executeSecondaryBufferTwiceTest()` | [`vktApiCommandBuffersTests.cpp#L3978`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3978) | Secondary execute twice leaf. |
| `orderBindPipelineTest()` | [`vktApiCommandBuffersTests.cpp#L4144`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4144) | Pipeline binding order leaf. |
| `executeStateTransitionTest()` | [`vktApiCommandBuffersTests.cpp#L4366`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4366) | State transition leaves, parameterized by `StateTransitionTest`. |
| `genComputeSource()` | [`vktApiCommandBuffersTests.cpp#L4471`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4471) | Compute source for `order_bind_pipeline` (good and bad variants). |
| `genComputeIncrementSource()` | [`vktApiCommandBuffersTests.cpp#L4529`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4529) | Atomic-counter compute source for simultaneous-use and bad-inheritance leaves. |
| `ManyDrawsCase` class | [`vktApiCommandBuffersTests.cpp#L4713`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4713) | `record_many_draws_*` test case class. |
| `manyIndirectDrawsTest()` | [`vktApiCommandBuffersTests.cpp#L5313`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5313) | Many indirect draws leaf. |
| `manyIndirectDispatchesTest()` | [`vktApiCommandBuffersTests.cpp#L5458`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5458) | Many indirect dispatches leaf. |
| `IndirectDispatchAlignmentCase` class | [`vktApiCommandBuffersTests.cpp#L5592`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5592) | 64-leaf generated matrix for `vkCmdDispatchIndirect` alignment. |
| `secCmdExtraCaseTest()` | [`vktApiCommandBuffersTests.cpp#L5802`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5802) | Secondary extras leaves. |
| `PipelineShaderObjMixSecondariesRun()` | [`vktApiCommandBuffersTests.cpp#L6022`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6022) | Pipeline and shader object mix leaf. |
| `SecondariesXferQueueRun()` | [`vktApiCommandBuffersTests.cpp#L6199`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6199) | Secondary on transfer queue leaf. |
| Header | [`vktApiCommandBuffersTests.hpp#L1`](../../../modules/vulkan/api/vktApiCommandBuffersTests.hpp#L1) | Declares `createCommandBuffersTests()`. |
