# [vktApiCommandBuffersTests.cpp](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1)

## Overview

Tests Vulkan command buffer lifecycle, recording, submission, and execution semantics. Covers command pool creation and reset, primary and secondary command buffer allocation and reuse, render-pass-continue behavior, simultaneous use, nested command buffers, state transitions, and indirect dispatch alignment.

## Role of File

Implementation-heavy. Contains all test logic, helper classes, and the registration function [createCommandBuffersTests()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6266).

## Source Code

- Implementation: [vktApiCommandBuffersTests.cpp](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1)
- Header: [vktApiCommandBuffersTests.hpp](../../../modules/vulkan/api/vktApiCommandBuffersTests.hpp#L1)
- Parent registration: [vktApiTests.cpp](../../../modules/vulkan/api/vktApiTests.cpp#L107)

## Registration Path

```
api
  +-- command_buffers
```

## Test Hierarchy

```
command_buffers
  +-- pool_create_null_params
  +-- pool_create_non_null_allocator           [non-SC]
  +-- pool_create_transient_bit
  +-- pool_create_reset_bit
  +-- pool_reset_release_res                   [non-SC]
  +-- pool_reset_no_flags_res
  +-- pool_reset_reuse                         [non-SC]
  +-- allocate_single_primary
  +-- allocate_many_primary
  +-- allocate_single_secondary
  +-- allocate_many_secondary
  +-- execute_small_primary
  +-- execute_large_primary
  +-- reset_implicit
  +-- trim_command_pool                        [non-SC]
  +-- trim_command_pool_secondary              [non-SC]
  +-- record_single_primary
  +-- record_many_primary
  +-- record_single_secondary
  +-- record_many_secondary
  +-- record_many_draws_primary_1
  +-- record_many_draws_secondary_1
  +-- record_many_draws_primary_2              [non-SC]
  +-- record_many_draws_secondary_2            [non-SC]
  +-- submit_twice_primary
  +-- submit_twice_secondary
  +-- record_one_time_submit_primary
  +-- record_one_time_submit_secondary
  +-- render_pass_continue
  +-- nested_render_pass_continue
  +-- render_pass_continue_no_fb
  +-- record_simul_use_secondary_one_primary
  +-- record_simul_use_secondary_two_primary
  +-- record_simul_use_nested
  +-- record_simul_use_twice_nested
  +-- record_query_precise_w_flag
  +-- record_query_imprecise_w_flag
  +-- record_query_imprecise_wo_flag
  +-- bad_inheritance_info_random
  +-- bad_inheritance_info_random_cont
  +-- bad_inheritance_info_random_data
  +-- bad_inheritance_info_invalid_type
  +-- bad_inheritance_info_valid_nonsense_type
  +-- submit_count_non_zero
  +-- submit_count_equal_zero
  +-- submit_wait_single_semaphore
  +-- submit_wait_many_semaphores
  +-- submit_null_fence
  +-- submit_two_buffers_one_buffer_null_with_fence
  +-- secondary_execute
  +-- secondary_execute_twice
  +-- order_bind_pipeline
  +-- recording_to_ininitial
  +-- executable_to_ininitial
  +-- recording_to_invalid
  +-- executable_to_invalid
  +-- many_indirect_draws_on_secondary
  +-- many_indirect_disps_on_secondary
  +-- nested_execute
  +-- nested_execute_multiple_levels
  +-- indirect_compute_dispatch_offsets_*       [8x8 = 64 tests]
  +-- secondary_push_constants_2               [non-SC]
  +-- secondary_push_descriptor_set_2          [non-SC]
  +-- secondary_push_descriptor_set_with_template [non-SC]
  +-- pipeline_shader_object_mix_with_secondaries [non-SC]
  +-- secondary_on_transfer_queue
```

## Test Families

### Command Pool Creation (Spec 19.1)

Tests creation of command pools with various flags and parameters. [createPoolNullParamsTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L380) creates a pool with default parameters. [createPoolNonNullAllocatorTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L392) tests allocation with a non-null allocator (non-SC only). [createPoolTransientBitTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L412) and [createPoolResetBitTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L430) test VK_COMMAND_POOL_CREATE_TRANSIENT_BIT and VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT respectively.

### Command Pool Reset

[resetPoolReleaseResourcesBitTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L449) resets with VK_COMMAND_POOL_RESET_RELEASE_RESOURCES_BIT (non-SC). [resetPoolNoFlagsTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L470) resets with no flags. [resetPoolReuseTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L511) verifies command buffers remain usable after pool reset (non-SC).

### Command Buffer Lifetime (Spec 19.2)

[allocatePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L564) and [allocateSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L638) test single buffer allocation. [allocateManyPrimaryBuffersTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L591) and [allocateManySecondaryBuffersTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L665) allocate many buffers. [executePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L712) and [executeLargePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L764) verify execution via event signaling. [resetBufferImplicitlyTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L830) tests implicit reset by re-recording.

### Trim Command Pool

[trimCommandPoolTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L999) exercises vkTrimCommandPool with repeated allocation, recording, submission, freeing, and trimming cycles for both primary and secondary levels (non-SC).

### Command Buffer Recording (Spec 19.3)

[recordSinglePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1088), [recordLargePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1126), [recordSingleSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1186), and [recordLargeSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1241) test recording of primary and secondary buffers with varying command counts.

### ManyDraws

[ManyDrawsCase](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4713) is a TestCase subclass that records many draw calls in a single command buffer and verifies rendering output. Parameterized by command buffer level and image extent.

### Submit Twice / One-Time Submit

[submitPrimaryBufferTwiceTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1337) and [submitSecondaryBufferTwiceTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1399) verify that a command buffer can be submitted multiple times. [oneTimeSubmitFlagPrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1519) and [oneTimeSubmitFlagSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1594) test VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT.

### Render Pass Continue

[renderPassContinueTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1726) tests VK_COMMAND_BUFFER_USAGE_RENDER_PASS_CONTINUE_BIT with optional framebuffer hint. [renderPassContinueNestedTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1926) tests nested command buffers within a render pass.

### Simultaneous Use

[simultaneousUseSecondaryBufferOnePrimaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L1778) executes a secondary buffer twice within one primary buffer using VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT. [simultaneousUseSecondaryBufferTwoPrimaryBuffersTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2543) does the same across two primaries. [simultaneousUseNestedSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2048) and [simultaneousUseNestedSecondaryBufferTwiceTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2205) test simultaneous use with nested command buffers.

### Query Recording

[recordBufferQueryPreciseWithFlagTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2714), [recordBufferQueryImpreciseWithFlagTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2803), and [recordBufferQueryImpreciseWithoutFlagTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2892) test occlusion query recording in secondary command buffers.

### Bad Inheritance Info

[badInheritanceInfoTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2371) tests that secondary command buffers with invalid or garbage inheritance info pointers still execute correctly when the inheritance info is not actually used. Parameterized by BadInheritanceInfoCase enum.

### Command Buffer Submission (Spec 19.4)

[submitBufferCountNonZero()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L2982) submits 5 command buffers at once. [submitBufferCountEqualZero()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3074) submits with zero count. Semaphore wait and fence handling tests follow.

### Secondary Command Buffer Execution (Spec 19.5)

[executeSecondaryBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3647) executes a secondary buffer via cmdExecuteCommands. [executeSecondaryBufferTwiceTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3978) executes the same secondary buffer in two separate primary submissions.

### Pipeline Binding Order

[orderBindPipelineTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4144) verifies that the last bound pipeline before a dispatch is the one that executes, using compute shaders.

### State Transitions

[executeStateTransitionTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L4366) tests command buffer state transitions: recording-to-initial, executable-to-initial, recording-to-invalid, and executable-to-invalid.

### Nested Command Buffers

[executeNestedBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3741) tests VK_EXT_nested_command_buffer by executing a secondary within a secondary. [executeMultipleLevelsNestedBufferTest()](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L3871) tests multi-level nesting.

### Indirect Dispatch Alignment

[IndirectDispatchAlignmentCase](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L5592) tests vkCmdDispatchIndirect with various memory and dispatch offsets, parameterized by 8x8 combinations.

### Secondary Extra Commands (non-SC)

Tests secondary command buffers with push constants 2, push descriptor set 2, and push descriptor set with template extensions.

### Pipeline Shader Object Mix (non-SC)

Tests mixing pipeline shader objects with secondary command buffers.

### Secondary on Transfer Queue

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

- The file is very large (6463 lines) and contains many test functions; the hierarchy above lists all registered test names but does not enumerate every generated indirect_dispatch_offsets test individually
- Some test functions referenced in the registration (e.g., submitBufferWaitSingleSemaphore, submitBufferWaitManySemaphores, submitBufferNullFence, submitTwoBuffersOneBufferNullWithFence) were not fully read due to file size but are registered at [lines 6376-6385](../../../modules/vulkan/api/vktApiCommandBuffersTests.cpp#L6376)
- The checkEventSupport and other support-check functions gate tests based on device features
- Vulkan SC tests have significantly reduced iteration counts and some features are omitted entirely
