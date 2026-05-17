# [vktApiCommandBuffersTests.cpp](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1)

## Overview

Tests Vulkan command buffer lifecycle, recording, submission, and execution semantics. Covers command pool creation and reset, primary and secondary command buffer allocation and reuse, render-pass-continue behavior, simultaneous use, nested command buffers, state transitions, and indirect dispatch alignment.

## Role of File

Implementation-heavy. Contains all test logic, helper classes, and the registration function [createCommandBuffersTests()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6266).

## Source Code

- Implementation: [vktApiCommandBuffersTests.cpp](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1)
- Header: [vktApiCommandBuffersTests.hpp](../../../modules/vulkan/api/vktApiCommandBuffersTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L107)

## Registration Hierarchy

```text
api.command_buffers
├── pool_create_null_params
├── pool_create_non_null_allocator (non-VulkanSC only)
├── pool_create_transient_bit
├── pool_create_reset_bit
├── pool_reset_release_res (non-VulkanSC only)
├── pool_reset_no_flags_res
├── pool_reset_reuse (non-VulkanSC only)
├── allocate_single_primary
├── allocate_many_primary
├── allocate_single_secondary
├── allocate_many_secondary
├── execute_small_primary
├── execute_large_primary
├── reset_implicit
├── trim_command_pool (non-VulkanSC only)
├── trim_command_pool_secondary (non-VulkanSC only)
├── record_single_primary
├── record_many_primary
├── record_single_secondary
├── record_many_secondary
├── record_many_draws_primary_1
├── record_many_draws_secondary_1
├── record_many_draws_primary_2 (non-VulkanSC only)
├── record_many_draws_secondary_2 (non-VulkanSC only)
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
├── indirect_compute_dispatch_offsets_0_0
├── indirect_compute_dispatch_offsets_0_4
├── indirect_compute_dispatch_offsets_0_8
├── indirect_compute_dispatch_offsets_0_12
├── indirect_compute_dispatch_offsets_0_16
├── indirect_compute_dispatch_offsets_0_20
├── indirect_compute_dispatch_offsets_0_24
├── indirect_compute_dispatch_offsets_0_28
├── indirect_compute_dispatch_offsets_4_0
├── indirect_compute_dispatch_offsets_4_4
├── indirect_compute_dispatch_offsets_4_8
├── indirect_compute_dispatch_offsets_4_12
├── indirect_compute_dispatch_offsets_4_16
├── indirect_compute_dispatch_offsets_4_20
├── indirect_compute_dispatch_offsets_4_24
├── indirect_compute_dispatch_offsets_4_28
├── indirect_compute_dispatch_offsets_8_0
├── indirect_compute_dispatch_offsets_8_4
├── indirect_compute_dispatch_offsets_8_8
├── indirect_compute_dispatch_offsets_8_12
├── indirect_compute_dispatch_offsets_8_16
├── indirect_compute_dispatch_offsets_8_20
├── indirect_compute_dispatch_offsets_8_24
├── indirect_compute_dispatch_offsets_8_28
├── indirect_compute_dispatch_offsets_12_0
├── indirect_compute_dispatch_offsets_12_4
├── indirect_compute_dispatch_offsets_12_8
├── indirect_compute_dispatch_offsets_12_12
├── indirect_compute_dispatch_offsets_12_16
├── indirect_compute_dispatch_offsets_12_20
├── indirect_compute_dispatch_offsets_12_24
├── indirect_compute_dispatch_offsets_12_28
├── indirect_compute_dispatch_offsets_16_0
├── indirect_compute_dispatch_offsets_16_4
├── indirect_compute_dispatch_offsets_16_8
├── indirect_compute_dispatch_offsets_16_12
├── indirect_compute_dispatch_offsets_16_16
├── indirect_compute_dispatch_offsets_16_20
├── indirect_compute_dispatch_offsets_16_24
├── indirect_compute_dispatch_offsets_16_28
├── indirect_compute_dispatch_offsets_20_0
├── indirect_compute_dispatch_offsets_20_4
├── indirect_compute_dispatch_offsets_20_8
├── indirect_compute_dispatch_offsets_20_12
├── indirect_compute_dispatch_offsets_20_16
├── indirect_compute_dispatch_offsets_20_20
├── indirect_compute_dispatch_offsets_20_24
├── indirect_compute_dispatch_offsets_20_28
├── indirect_compute_dispatch_offsets_24_0
├── indirect_compute_dispatch_offsets_24_4
├── indirect_compute_dispatch_offsets_24_8
├── indirect_compute_dispatch_offsets_24_12
├── indirect_compute_dispatch_offsets_24_16
├── indirect_compute_dispatch_offsets_24_20
├── indirect_compute_dispatch_offsets_24_24
├── indirect_compute_dispatch_offsets_24_28
├── indirect_compute_dispatch_offsets_28_0
├── indirect_compute_dispatch_offsets_28_4
├── indirect_compute_dispatch_offsets_28_8
├── indirect_compute_dispatch_offsets_28_12
├── indirect_compute_dispatch_offsets_28_16
├── indirect_compute_dispatch_offsets_28_20
├── indirect_compute_dispatch_offsets_28_24
└── indirect_compute_dispatch_offsets_28_28
```

Evidence:
- `command_buffers` group created at [`createCommandBuffersTests()`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6266)
- All direct children are individual test cases registered via `addFunctionCase` or `addChild` from [`vktApiCommandBuffersTests.cpp`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6270) through [`vktApiCommandBuffersTests.cpp`](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6458)

## Test Families

### pool_create_null_params — Command Pool Creation

Tests creation of command pools with various flags and parameters. [createPoolNullParamsTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L380) creates a pool with default parameters. `pool_create_non_null_allocator` tests allocation with a non-null allocator (non-VulkanSC only, via [createPoolNonNullAllocatorTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L392)). `pool_create_transient_bit` and `pool_create_reset_bit` test `VK_COMMAND_POOL_CREATE_TRANSIENT_BIT` and `VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT` respectively (via [createPoolTransientBitTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L412) and [createPoolResetBitTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L430)).

### pool_reset_release_res — Command Pool Reset

`pool_reset_release_res` resets with `VK_COMMAND_POOL_RESET_RELEASE_RESOURCES_BIT` (non-VulkanSC only, via [resetPoolReleaseResourcesBitTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L449)). `pool_reset_no_flags_res` resets with no flags (via [resetPoolNoFlagsTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L470)). `pool_reset_reuse` verifies command buffers remain usable after pool reset (non-VulkanSC only, via [resetPoolReuseTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L511)).

### allocate_single_primary — Command Buffer Lifetime

`allocate_single_primary` and `allocate_single_secondary` test single buffer allocation (via [allocatePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L564) and [allocateSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L638)). `allocate_many_primary` and `allocate_many_secondary` allocate many buffers (via [allocateManyPrimaryBuffersTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L591) and [allocateManySecondaryBuffersTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L665)). `execute_small_primary` and `execute_large_primary` verify execution via event signaling (via [executePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L712) and [executeLargePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L764)). `reset_implicit` tests implicit reset by re-recording (via [resetBufferImplicitlyTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L830)).

### trim_command_pool — Trim Command Pool

`trim_command_pool` and `trim_command_pool_secondary` exercise `vkTrimCommandPool` with repeated allocation, recording, submission, freeing, and trimming cycles for primary and secondary levels respectively (non-VulkanSC only, via [trimCommandPoolTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L999)).

### record_single_primary — Command Buffer Recording

`record_single_primary` and `record_many_primary` test recording of primary buffers with varying command counts (via [recordSinglePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1088) and [recordLargePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1126)). `record_single_secondary` and `record_many_secondary` test recording of secondary buffers (via [recordSingleSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1186) and [recordLargeSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1241)).

### record_many_draws_primary_1 — Many Draws

[ManyDrawsCase](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4713) is a TestCase subclass that records many draw calls in a single command buffer and verifies rendering output. `record_many_draws_primary_1` and `record_many_draws_secondary_1` use a 128x128 image extent. `record_many_draws_primary_2` and `record_many_draws_secondary_2` use a 512x256 extent (non-VulkanSC only).

### submit_twice_primary — Submit Twice / One-Time Submit

`submit_twice_primary` and `submit_twice_secondary` verify that a command buffer can be submitted multiple times (via [submitPrimaryBufferTwiceTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1337) and [submitSecondaryBufferTwiceTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1399)). `record_one_time_submit_primary` and `record_one_time_submit_secondary` test `VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT` (via [oneTimeSubmitFlagPrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1519) and [oneTimeSubmitFlagSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1594)).

### render_pass_continue — Render Pass Continue

`render_pass_continue` tests `VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT` with optional framebuffer hint (via [renderPassContinueTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1726)). `nested_render_pass_continue` tests nested command buffers within a render pass (via [renderPassContinueNestedTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1926)). `render_pass_continue_no_fb` tests render pass continue without a framebuffer (via [renderPassContinueTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1726) with `false` parameter).

### record_simul_use_secondary_one_primary — Simultaneous Use

`record_simul_use_secondary_one_primary` executes a secondary buffer twice within one primary buffer using `VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT` (via [simultaneousUseSecondaryBufferOnePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1778)). `record_simul_use_secondary_two_primary` does the same across two primaries (via [simultaneousUseSecondaryBufferTwoPrimaryBuffersTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2543)). `record_simul_use_nested` and `record_simul_use_twice_nested` test simultaneous use with nested command buffers (via [simultaneousUseNestedSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2048) and [simultaneousUseNestedSecondaryBufferTwiceTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2205)).

### record_query_precise_w_flag — Query Recording

`record_query_precise_w_flag`, `record_query_imprecise_w_flag`, and `record_query_imprecise_wo_flag` test occlusion query recording in secondary command buffers (via [recordBufferQueryPreciseWithFlagTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2714), [recordBufferQueryImpreciseWithFlagTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2803), and [recordBufferQueryImpreciseWithoutFlagTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2892)).

### bad_inheritance_info_random — Bad Inheritance Info

[badInheritanceInfoTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2371) tests that secondary command buffers with invalid or garbage inheritance info pointers still execute correctly when the inheritance info is not actually used. Parameterized by `BadInheritanceInfoCase` enum: `bad_inheritance_info_random` (RANDOM_PTR), `bad_inheritance_info_random_cont` (RANDOM_PTR_CONTINUATION), `bad_inheritance_info_random_data` (RANDOM_DATA_PTR), `bad_inheritance_info_invalid_type` (INVALID_STRUCTURE_TYPE), `bad_inheritance_info_valid_nonsense_type` (VALID_NONSENSE_TYPE).

### submit_count_non_zero — Command Buffer Submission

`submit_count_non_zero` submits 5 command buffers at once (via [submitBufferCountNonZero()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2982)). `submit_count_equal_zero` submits with zero count (via [submitBufferCountEqualZero()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3074)). `submit_wait_single_semaphore` and `submit_wait_many_semaphores` test semaphore wait handling. `submit_null_fence` tests submission with a null fence. `submit_two_buffers_one_buffer_null_with_fence` tests submission with one null buffer and a fence.

### secondary_execute — Secondary Command Buffer Execution

`secondary_execute` executes a secondary buffer via `cmdExecuteCommands` (via [executeSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3647)). `secondary_execute_twice` executes the same secondary buffer in two separate primary submissions (via [executeSecondaryBufferTwiceTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3978)).

### order_bind_pipeline — Pipeline Binding Order

[orderBindPipelineTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4144) verifies that the last bound pipeline before a dispatch is the one that executes, using compute shaders.

### recording_to_ininitial — State Transitions

[executeStateTransitionTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4366) tests command buffer state transitions: `recording_to_ininitial` (RECORDING_TO_INITIAL), `executable_to_ininitial` (EXECUTABLE_TO_INITIAL), `recording_to_invalid` (RECORDING_TO_INVALID), and `executable_to_invalid` (EXECUTABLE_TO_INVALID).

### many_indirect_draws_on_secondary — Indirect Draws/Dispatches on Secondary

`many_indirect_draws_on_secondary` tests many indirect draw calls on a secondary command buffer. `many_indirect_disps_on_secondary` tests many indirect dispatch calls on a secondary command buffer.

### nested_execute — Nested Command Buffers

`nested_execute` tests `VK_EXT_nested_command_buffer` by executing a secondary within a secondary (via [executeNestedBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3741)). `nested_execute_multiple_levels` tests multi-level nesting (via [executeMultipleLevelsNestedBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3871)).

### indirect_compute_dispatch_offsets_0_0 — Indirect Dispatch Alignment

[IndirectDispatchAlignmentCase](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5592) tests `vkCmdDispatchIndirect` with various memory and dispatch offsets. The 64 generated tests are parameterized by 8x8 combinations of memory offset (0, 4, 8, 12, 16, 20, 24, 28) and dispatch offset (0, 4, 8, 12, 16, 20, 24, 28), producing test names `indirect_compute_dispatch_offsets_{memOffset}_{dispatchOffset}`.

### secondary_push_constants_2 — Secondary Extra Commands (non-VulkanSC only)

Tests secondary command buffers with push constants 2 (`secondary_push_constants_2`), push descriptor set 2 (`secondary_push_descriptor_set_2`), and push descriptor set with template (`secondary_push_descriptor_set_with_template`) extensions.

### pipeline_shader_object_mix_with_secondaries — Pipeline Shader Object Mix (non-VulkanSC only)

Tests mixing pipeline shader objects with secondary command buffers.

### secondary_on_transfer_queue — Secondary on Transfer Queue

Tests secondary command buffer execution on a transfer-only queue.

## Parameter Dimensions

| Dimension | Observed Values |
|---|---|
| Command buffer level | VK_COMMAND_BUFFER_LEVEL_PRIMARY, VK_COMMAND_BUFFER_LEVEL_SECONDARY |
| Pool create flags | 0, TRANSIENT_BIT, RESET_COMMAND_BUFFER_BIT |
| Command buffer usage flags | 0, ONE_TIME_SUBMIT_BIT, SIMULTANEOUS_USE_BIT, RENDER_PASS_CONTINUE_BIT |
| Framebuffer hint | true, false |
| Buffer count for allocation | 1, 1024, 10000 (100 on SC) |
| Large buffer command count | 10000 (1000 on SC) |
| Indirect dispatch offsets | 0, 4, 8, 12, 16, 20, 24, 28 |
| BadInheritanceInfoCase | RANDOM_PTR, RANDOM_PTR_CONTINUATION, RANDOM_DATA_PTR, INVALID_STRUCTURE_TYPE, VALID_NONSENSE_TYPE |
| StateTransitionTest | RECORDING_TO_INITIAL, EXECUTABLE_TO_INITIAL, RECORDING_TO_INVALID, EXECUTABLE_TO_INVALID |
| Image extent for ManyDraws | 128x128, 512x256 |

## Support / Feature Requirements

| Feature / Extension | Used By |
|---|---|
| VK_KHR_maintenance1 | trimCommandPoolTest |
| VK_EXT_nested_command_buffer | nested_render_pass_continue, nested_execute, nested_execute_multiple_levels |
| VK_KHR_maintenance7 | nested_render_pass_continue (alternative to VK_EXT_nested_command_buffer) |
| VK_KHR_push_descriptor | secondary_push_descriptor_set_2, secondary_push_descriptor_set_with_template |
| VK_KHR_shader_object | pipeline_shader_object_mix_with_secondaries |
| VK_KHR_timeline_semaphore | secondary_execute_twice |
| Events support | Multiple tests via checkEventSupport |

## Verification Methods

- **Event signaling**: Most tests record vkCmdSetEvent and verify VK_EVENT_SET after submission (e.g., [executePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L712))
- **Pixel comparison**: renderPassContinueTest and ManyDrawsInstance read back color attachment and compare against expected clear/draw values
- **Compute atomic increment**: simultaneousUse tests use a compute shader that atomically increments a counter; the final count is checked
- **VK_CHECK**: API calls are checked for VK_SUCCESS; unexpected results cause test failure
- **Crash detection**: resetPoolReuseTest and trimCommandPoolTest pass if no crash occurs
- **Buffer content comparison**: orderBindPipelineTest and indirect dispatch tests compare output buffer contents against expected values

## Test Principles Observed

- Positive conformance: most tests verify that valid API usage succeeds
- Robustness: badInheritanceInfo tests verify that unused invalid pointers do not cause failures
- State coverage: state transition tests exercise all documented command buffer state transitions
- Resource reuse: pool reset and trim tests verify that resources can be recycled without leaks
- SC divergence: many tests are gated by CTS_USES_VULKANSC with reduced iteration counts or omitted features

## Notes / Uncertainties

- The file is very large (6463 lines) and contains many test functions; the hierarchy above lists all registered test names including all 64 generated indirect_compute_dispatch_offsets tests
- Some test functions referenced in the registration (e.g., submitBufferWaitSingleSemaphore, submitBufferWaitManySemaphores, submitBufferNullFence, submitTwoBuffersOneBufferNullWithFence) were not fully read due to file size but are registered at [lines 6376-6385](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6376)
- The checkEventSupport and other support-check functions gate tests based on device features
- Vulkan SC tests have significantly reduced iteration counts and some features are omitted entirely
