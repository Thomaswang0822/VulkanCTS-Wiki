## Overview

**Core question:** Does `VK_EXT_conditional_rendering` suppress only the commands it specifies, while commands outside that affected set continue to operate?

- This page covers the `conditional_rendering.conditional_ignore` test family implemented in [vktConditionalIgnoreTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp).
- It exercises binding, transfer, image-clear, push-constant, update, and ray-tracing operations while a conditional-rendering block is active.
- The expected result is command-specific: the ignore-family commands must produce their ordinary effect inside the block. Where a later draw or dispatch observes state established by an ignored binding or push-constant command, that observer is recorded after the conditional block and therefore runs unconditionally.

## Background Knowledge

- **Affected-command lists:** Vulkan conditional rendering does not mean that every command inside the block is skipped. The specification defines which commands are affected; commands outside that list must execute normally.
- **Resource observations:** Image, buffer, depth/stencil, and ray-generation output provide independent ways to observe whether an ignored command ran.
- **Command recording and inheritance:** A command can be recorded directly, in a secondary command buffer, or in nested command-buffer paths. Inherited conditional state changes where the state is established, not the affected-command rule.

## Registration Hierarchy

```text
conditional_rendering.conditional_ignore
├── bind_descriptor_sets
├── bind_descriptor_sets_inverted
├── bind_index_buffer
├── bind_index_buffer_inverted
├── bind_pipeline
├── bind_pipeline_inverted
├── bind_shaders
├── bind_shaders_inverted
├── bind_vertex_buffers
├── bind_vertex_buffers_inverted
├── blit_image
├── blit_image_inverted
├── clear_color_condition_host_memory_expect_execution
├── clear_color_condition_host_memory_expect_execution_inverted
├── clear_color_condition_host_memory_expect_noop
├── clear_color_condition_host_memory_expect_noop_inverted
├── clear_color_condition_host_memory_inherited_expect_execution
├── clear_color_condition_host_memory_inherited_expect_execution_inverted
├── clear_color_condition_host_memory_inherited_expect_noop
├── clear_color_condition_host_memory_inherited_expect_noop_inverted
├── clear_color_condition_host_memory_nested_buffer_expect_execution
├── clear_color_condition_host_memory_nested_buffer_expect_execution_inverted
├── clear_color_condition_host_memory_nested_buffer_expect_noop
├── clear_color_condition_host_memory_nested_buffer_expect_noop_inverted
├── clear_color_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── clear_color_condition_host_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── clear_color_condition_host_memory_nested_buffer_nested_inherited_expect_noop
├── clear_color_condition_host_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── clear_color_condition_host_memory_nested_inherited_expect_execution
├── clear_color_condition_host_memory_nested_inherited_expect_execution_inverted
├── clear_color_condition_host_memory_nested_inherited_expect_noop
├── clear_color_condition_host_memory_nested_inherited_expect_noop_inverted
├── clear_color_condition_host_memory_secondary_buffer_expect_execution
├── clear_color_condition_host_memory_secondary_buffer_expect_execution_inverted
├── clear_color_condition_host_memory_secondary_buffer_expect_noop
├── clear_color_condition_host_memory_secondary_buffer_expect_noop_inverted
├── clear_color_condition_host_memory_secondary_buffer_inherited_expect_execution
├── clear_color_condition_host_memory_secondary_buffer_inherited_expect_execution_inverted
├── clear_color_condition_host_memory_secondary_buffer_inherited_expect_noop
├── clear_color_condition_host_memory_secondary_buffer_inherited_expect_noop_inverted
├── clear_color_condition_local_memory_expect_execution
├── clear_color_condition_local_memory_expect_execution_inverted
├── clear_color_condition_local_memory_expect_noop
├── clear_color_condition_local_memory_expect_noop_inverted
├── clear_color_condition_local_memory_inherited_expect_execution
├── clear_color_condition_local_memory_inherited_expect_execution_inverted
├── clear_color_condition_local_memory_inherited_expect_noop
├── clear_color_condition_local_memory_inherited_expect_noop_inverted
├── clear_color_condition_local_memory_nested_buffer_expect_execution
├── clear_color_condition_local_memory_nested_buffer_expect_execution_inverted
├── clear_color_condition_local_memory_nested_buffer_expect_noop
├── clear_color_condition_local_memory_nested_buffer_expect_noop_inverted
├── clear_color_condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── clear_color_condition_local_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── clear_color_condition_local_memory_nested_buffer_nested_inherited_expect_noop
├── clear_color_condition_local_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── clear_color_condition_local_memory_nested_inherited_expect_execution
├── clear_color_condition_local_memory_nested_inherited_expect_execution_inverted
├── clear_color_condition_local_memory_nested_inherited_expect_noop
├── clear_color_condition_local_memory_nested_inherited_expect_noop_inverted
├── clear_color_condition_local_memory_secondary_buffer_expect_execution
├── clear_color_condition_local_memory_secondary_buffer_expect_execution_inverted
├── clear_color_condition_local_memory_secondary_buffer_expect_noop
├── clear_color_condition_local_memory_secondary_buffer_expect_noop_inverted
├── clear_color_condition_local_memory_secondary_buffer_inherited_expect_execution
├── clear_color_condition_local_memory_secondary_buffer_inherited_expect_execution_inverted
├── clear_color_condition_local_memory_secondary_buffer_inherited_expect_noop
├── clear_color_condition_local_memory_secondary_buffer_inherited_expect_noop_inverted
├── clear_color_image
├── clear_color_image_inverted
├── clear_color_no_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── clear_color_no_condition_host_memory_secondary_buffer_inherited_expect_execution
├── clear_color_no_condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── clear_color_no_condition_local_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_condition_host_memory_expect_execution
├── clear_depth_condition_host_memory_expect_execution_inverted
├── clear_depth_condition_host_memory_expect_noop
├── clear_depth_condition_host_memory_expect_noop_inverted
├── clear_depth_condition_host_memory_inherited_expect_execution
├── clear_depth_condition_host_memory_inherited_expect_execution_inverted
├── clear_depth_condition_host_memory_inherited_expect_noop
├── clear_depth_condition_host_memory_inherited_expect_noop_inverted
├── clear_depth_condition_host_memory_nested_buffer_expect_execution
├── clear_depth_condition_host_memory_nested_buffer_expect_execution_inverted
├── clear_depth_condition_host_memory_nested_buffer_expect_noop
├── clear_depth_condition_host_memory_nested_buffer_expect_noop_inverted
├── clear_depth_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── clear_depth_condition_host_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── clear_depth_condition_host_memory_nested_buffer_nested_inherited_expect_noop
├── clear_depth_condition_host_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── clear_depth_condition_host_memory_nested_inherited_expect_execution
├── clear_depth_condition_host_memory_nested_inherited_expect_execution_inverted
├── clear_depth_condition_host_memory_nested_inherited_expect_noop
├── clear_depth_condition_host_memory_nested_inherited_expect_noop_inverted
├── clear_depth_condition_host_memory_secondary_buffer_expect_execution
├── clear_depth_condition_host_memory_secondary_buffer_expect_execution_inverted
├── clear_depth_condition_host_memory_secondary_buffer_expect_noop
├── clear_depth_condition_host_memory_secondary_buffer_expect_noop_inverted
├── clear_depth_condition_host_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_condition_host_memory_secondary_buffer_inherited_expect_execution_inverted
├── clear_depth_condition_host_memory_secondary_buffer_inherited_expect_noop
├── clear_depth_condition_host_memory_secondary_buffer_inherited_expect_noop_inverted
├── clear_depth_condition_local_memory_expect_execution
├── clear_depth_condition_local_memory_expect_execution_inverted
├── clear_depth_condition_local_memory_expect_noop
├── clear_depth_condition_local_memory_expect_noop_inverted
├── clear_depth_condition_local_memory_inherited_expect_execution
├── clear_depth_condition_local_memory_inherited_expect_execution_inverted
├── clear_depth_condition_local_memory_inherited_expect_noop
├── clear_depth_condition_local_memory_inherited_expect_noop_inverted
├── clear_depth_condition_local_memory_nested_buffer_expect_execution
├── clear_depth_condition_local_memory_nested_buffer_expect_execution_inverted
├── clear_depth_condition_local_memory_nested_buffer_expect_noop
├── clear_depth_condition_local_memory_nested_buffer_expect_noop_inverted
├── clear_depth_condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── clear_depth_condition_local_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── clear_depth_condition_local_memory_nested_buffer_nested_inherited_expect_noop
├── clear_depth_condition_local_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── clear_depth_condition_local_memory_nested_inherited_expect_execution
├── clear_depth_condition_local_memory_nested_inherited_expect_execution_inverted
├── clear_depth_condition_local_memory_nested_inherited_expect_noop
├── clear_depth_condition_local_memory_nested_inherited_expect_noop_inverted
├── clear_depth_condition_local_memory_secondary_buffer_expect_execution
├── clear_depth_condition_local_memory_secondary_buffer_expect_execution_inverted
├── clear_depth_condition_local_memory_secondary_buffer_expect_noop
├── clear_depth_condition_local_memory_secondary_buffer_expect_noop_inverted
├── clear_depth_condition_local_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_condition_local_memory_secondary_buffer_inherited_expect_execution_inverted
├── clear_depth_condition_local_memory_secondary_buffer_inherited_expect_noop
├── clear_depth_condition_local_memory_secondary_buffer_inherited_expect_noop_inverted
├── clear_depth_no_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── clear_depth_no_condition_host_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_no_condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── clear_depth_no_condition_local_memory_secondary_buffer_inherited_expect_execution
├── clear_depth_stencil_image
├── clear_depth_stencil_image_inverted
├── copy_buffer
├── copy_buffer_inverted
├── copy_buffer_to_image
├── copy_buffer_to_image_inverted
├── copy_image
├── copy_image_inverted
├── copy_image_to_buffer
├── copy_image_to_buffer_inverted
├── fill_buffer
├── fill_buffer_inverted
├── push_constant
├── push_constant_inverted
├── resolve_image
├── resolve_image_inverted
├── trace_rays
├── trace_rays_indirect
├── trace_rays_indirect2
├── trace_rays_indirect2_inverted
├── trace_rays_indirect_inverted
├── trace_rays_inverted
├── update_buffer
└── update_buffer_inverted
```

These direct children are the exact command components present in the current mustpass file. The clear-color and clear-depth condition-data combinations are listed individually rather than represented by a prefix or placeholder; rows marked `clearInRenderPass` are skipped by this family. The current source and mustpass data are authoritative for the exact leaf set.

## Parameter Dimensions and Observed Values

| Dimension | Registered values or areas | Meaning in this test | Evidence |
|---|---|---|---|
| Ignored command | Binding, transfer, image-clear, push-constant, update, and ray-tracing areas | Selects the command that must ignore active conditional rendering. | [`ConditionalIgnoreTests::init()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L2319-L2436) |
| Predicate form | Condition, inverted, and no-condition forms where registered | Places the command inside the conditional-state matrix or provides a control path. | [`s_testsData`](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L61-L144) |
| Command-buffer scope | Primary, secondary, inherited, and nested paths for the generated clear cases | Checks the ignored-command rule at different recording and execution scopes. | [`ConditionalIgnoreClearColorTestInstance::queuePass()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L135-L307) and [`ConditionalIgnoreClearDepthTestInstance::iterate()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L355-L528) |
| Observable result | Image, depth/stencil, buffer, or ray-generation output | Supplies the pass/fail signal for the selected command. | The command-specific test functions in [`vktConditionalIgnoreTests.cpp`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L135-L2305) |

## Behavior Parameters

The primary behavioral axis is the ignored command. Each direct child asks whether that command still has its normal effect while conditional rendering is active.

### Commands that ignore conditional rendering

The test records the selected command in the active conditional block, then validates the resource or result object that the command should have changed. A predicate that suppresses affected commands must not suppress an operation that the specification classifies as unaffected. For the generated clear cases, the selected clear is expected to happen in every condition-data row because `vkCmdClearColorImage` and `vkCmdClearDepthStencilImage` are unaffected commands.

### Inversion, memory placement, and command-buffer scope

These dimensions vary how conditional state is supplied and where the command is recorded. They should not change the expected ordinary behavior of an ignored command. If the result changes only with these dimensions, the failure is localized to state handling, command-buffer scope, or synchronization rather than to the command's ordinary operation alone.

## Shader Analysis

This family is primarily a command-semantics test. The representative `push_constant` case uses a compute shader only to compare two push-constant values after the conditional block; the shader does not evaluate conditional rendering. The other shader-bearing areas use graphics or ray-generation shaders as command-specific observation paths.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.conditional_rendering.conditional_ignore.push_constant
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `push_constant` | Records a push-constant update inside the conditional block and observes it with a compute dispatch after the block. |
| Non-inverted condition | The condition buffer is initialized to zero, so the push-constant update is the operation whose unaffected behavior is checked. |

#### Purpose

The compute shader compares the two pushed values and writes `1` when they match. The host initializes them to `(3, 7)`, conditionally writes the first value into the second slot, and expects the ignored push-constant update to make the values equal.

#### Structural Design

| Shader phase | Operation | Observable result |
|---|---|---|
| Inputs | Read `pc.a` and `pc.b` from the push-constant block. | The shader sees the state established by command recording. |
| Comparison | Evaluate `pc.a == pc.b`. | Equality becomes a Boolean result. |
| Output | Select `1` for equality and `0` otherwise, then store it in `outBuffer.value`. | Host readback distinguishes whether the update was retained. |

#### Shader Code

```glsl
#version 460

/// One invocation is enough because the host checks one scalar result.
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;

/// The compute shader writes the equality result for host validation.
layout (set=0, binding=0) buffer OutBlock { uint value; } outBuffer;

/// The command buffer writes the two values before dispatch.
layout (push_constant, std430) uniform PushConstantBlock { uint a; uint b; } pc;

void main(void) { outBuffer.value = ((pc.a == pc.b) ? 1u : 0u); }
```

#### Additional Info

- The shader is not the conditional-rendering decision point: `vkCmdBeginConditionalRenderingEXT` surrounds the push-constant command, while the dispatch and shader run after `vkCmdEndConditionalRenderingEXT`.
- The representative source uses the default SPIR-V 1.0 target because `pushConstantComputeShaders()` does not provide an explicit `ShaderBuildOptions` target.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Inversion | The shader is unchanged; the test pairs a zero predicate with no inversion and a nonzero predicate with inversion, so an affected command would be suppressed in both variants while the enclosed push-constant update must still be applied. | [`GeneralCmdParams`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L531-L544) and [`pushConstantTest()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L578-L630) |
| Push-constant values | The shader is unchanged; command recording changes the second value from `7` to `3` inside the conditional block. | [`pushConstantTest()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L562-L657) |
| Output buffer | The shader is unchanged; the host reads the storage-buffer value after the compute-stage barrier. | [`pushConstantTest()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L604-L657) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 30
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpName %main "main"
               OpName %OutBlock "OutBlock"
               OpMemberName %OutBlock 0 "value"
               OpName %outBuffer "outBuffer"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "a"
               OpMemberName %PushConstantBlock 1 "b"
               OpName %pc "pc"
               OpDecorate %OutBlock BufferBlock
               OpMemberDecorate %OutBlock 0 Offset 0
               OpDecorate %outBuffer Binding 0
               OpDecorate %outBuffer DescriptorSet 0
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
   %OutBlock = OpTypeStruct %uint
%_ptr_Uniform_OutBlock = OpTypePointer Uniform %OutBlock
  %outBuffer = OpVariable %_ptr_Uniform_OutBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%PushConstantBlock = OpTypeStruct %uint %uint
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
      %int_1 = OpConstant %int 1
       %bool = OpTypeBool
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %17 = OpLoad %uint %16
         %19 = OpAccessChain %_ptr_PushConstant_uint %pc %int_1
         %20 = OpLoad %uint %19
         %22 = OpIEqual %bool %17 %20
         %25 = OpSelect %uint %22 %uint_1 %uint_0
         %27 = OpAccessChain %_ptr_Uniform_uint %outBuffer %int_0
               OpStore %27 %25
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Support checks require `VK_EXT_conditional_rendering` and add command-specific extensions and features for registered operations. Unsupported rows are skipped before execution.
- The test creates the resources needed by the selected command, initializes them to known values, records the command inside the chosen conditional-rendering scope, submits, and waits for completion.
- Result checking is command-specific. Image and depth/stencil cases compare pixels, buffer cases inspect bytes, graphics-binding cases compare the rendered color, and ray-tracing cases inspect the storage-buffer result.
- A case passes when the selected ignored command produces its ordinary expected effect regardless of the active predicate. The `push_constant` shader-backed case is an observation of command-written state after the conditional block, not an affected operation inside the block.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `bind_descriptor_sets` | Conditional suppression incorrectly prevents descriptor-set binding, so the later draw observes the wrong resource. |
| `bind_index_buffer` | Conditional suppression incorrectly prevents index-buffer binding, so the later draw uses the wrong indices. |
| `bind_pipeline` | Conditional suppression incorrectly prevents pipeline binding, so the later draw uses the wrong pipeline. |
| `bind_shaders` | Conditional suppression incorrectly prevents shader-object binding, so the later draw uses the wrong shader state. |
| `bind_vertex_buffers` | Conditional suppression incorrectly prevents vertex-buffer binding, so the later draw uses the wrong vertices. |
| `blit_image`, `clear_color_image`, `clear_depth_stencil_image`, `copy_buffer`, `copy_buffer_to_image`, `copy_image`, `copy_image_to_buffer`, `fill_buffer`, `resolve_image`, or `update_buffer` | The transfer or resource-write command is incorrectly suppressed, or synchronization/readback is incomplete. |
| `push_constant` | Conditional suppression incorrectly prevents the command-side state update, or the later dispatch does not observe the expected value. |
| `trace_rays`, `trace_rays_indirect`, or `trace_rays_indirect2` | Conditional suppression incorrectly prevents ray generation, or the ray-tracing result is not made visible to the host. |

### Cause Analysis

#### Affected-command classification

**Possible failure symptoms:** An ignored clear, copy, update, binding, push-constant, or ray-tracing operation has no effect when it is recorded inside a conditional block.

**Possible implementation causes:** The implementation may apply conditional suppression to a command outside the specification's affected-command set. The exact failing command path requires source-level investigation.

#### Resource visibility and synchronization

**Possible failure symptoms:** The command appears to execute, but the host observes stale image or buffer data.

**Possible implementation causes:** The operation may be correct while a barrier, layout transition, memory visibility operation, or result retrieval path is incomplete. The test result does not identify the precise synchronization layer.

#### Command-buffer scope and inheritance

**Possible failure symptoms:** A direct primary case passes, but a secondary, inherited, or nested variant changes behavior under the same command and predicate.

**Possible implementation causes:** Active conditional state may be incorrectly propagated or applied at command-buffer boundaries. Source and specification review are needed to isolate the implementation layer.

## Case Pruning

### Requirement-based pruning

- Clear cases require `VK_EXT_conditional_rendering`; inherited clear rows additionally check `inheritedConditionalRendering`, and nested rows check `VK_EXT_nested_command_buffer` and `nestedCommandBuffer`.
- General command cases require `VK_EXT_conditional_rendering`; graphics shader-object binding additionally requires `VK_EXT_shader_object`.
- Ray-tracing cases require `VK_KHR_ray_tracing_pipeline`; `trace_rays_indirect2` additionally requires `VK_KHR_ray_tracing_maintenance1`.
- Unsupported command families are skipped by their support checks rather than treated as functional failures.

### Design-based pruning

- The matrix reuses shared predicate and command-buffer data instead of duplicating a separate condition model for each ignored command.
- Each command area uses the observable resource type that best exposes its ordinary effect.
- The clear-color and clear-depth condition-data combinations are listed as their exact mustpass components in the documented tree. Their shared condition dimensions are explained in prose, while the tree itself remains a complete list of real registration components.

## Key Takeaways

- Conditional rendering suppresses only the commands defined as affected; this page tests the complementary command set.
- The predicate is not a shader input in the representative push-constant case. Command execution determines whether the push-constant update inside the block occurs, and the later compute dispatch reads the resulting command state.
- A failure must be interpreted with its result type and command scope: stale data can indicate synchronization, while a missing command effect can indicate incorrect classification or state handling.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Registration | [`ConditionalIgnoreTests::init()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L2319-L2436) | Defines the generated clear children and direct command areas. |
| Clear execution and validation | [`ConditionalIgnoreClearColorTestInstance::queuePass()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L135-L307) and [`ConditionalIgnoreClearDepthTestInstance::iterate()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L355-L528) | Records clear operations and compares the resulting image data. |
| General command execution | [`pushConstantTest()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L562-L657) and the neighboring command test functions | Records each unaffected command and checks its command-specific result. |
| Graphics and ray tracing | [`graphicsBindTest()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L1791-L2048) and [`rayTracingTest()`](../../../modules/vulkan/conditional_rendering/vktConditionalIgnoreTests.cpp#L2083-L2305) | Exercises shader-backed binding and ray-generation command paths. |
| Shared condition data | [`ConditionalData` and `s_testsData`](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L144) | Supplies predicate, inversion, memory, inheritance, and nesting variants. |
| Conditional begin/end | [`beginConditionalRendering()`](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L124-L136) | Shows how the condition buffer and inversion flags enter command recording. |
| Mustpass coverage | [conditional-rendering.txt](../../../mustpass/main/vk-default/conditional-rendering.txt) | Lists executable `conditional_ignore` paths. |
| Specification semantics | [drawing.adoc](../../../../vulkan-docs/src/chapters/drawing.adoc#L2086-L2167) | Defines affected commands and conditional-rendering behavior. |
