## Overview

**Core question:** Does `vkCmdClearAttachments` execute exactly when conditional rendering permits it, across primary, secondary, inherited, and nested command-buffer paths?

- This page covers the `conditional_rendering.clear_attachments` test family implemented in [vktConditionalClearAttachmentTests.cpp](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp).
- Each registered condition-data child contains one `clear_attachments` test case leaf. The implementation skips rows whose `clearInRenderPass` flag is true, leaving 60 mustpass leaves for this family.
- Conditional cases clear a full color attachment to blue inside a conditional rendering block; the four `no_condition_*` rows execute the same clear unconditionally. Setup first clears the same image to black, so a permitted clear and a suppressed clear produce distinct readback images.
- The condition data varies the predicate value and inversion, condition-buffer memory, command-buffer location, inheritance, and nested secondary execution. The host compares the submitted image against an all-blue or all-black reference.

## Background Knowledge

- **Conditional rendering.** `VK_EXT_conditional_rendering` makes selected rendering commands depend on a 32-bit value in a buffer. `vkCmdBeginConditionalRenderingEXT` selects the buffer, offset, and optional inversion flag. Commands between begin and end either execute or have no effect. The extension covers draws, compute dispatches, and attachment clears.
- **`vkCmdClearAttachments`.** This command clears color or depth/stencil regions inside an active render pass instance. It writes color attachments through the color attachment output stage and does not depend on the bound pipeline state. The test uses one color attachment and a `VkClearRect` covering the render area.
- **Secondary command-buffer inheritance.** `VkCommandBufferInheritanceConditionalRenderingInfoEXT::conditionalRenderingEnable` controls whether a secondary command buffer may execute while its primary has active conditional rendering. A nested secondary adds another `vkCmdExecuteCommands` level without changing the image-level correctness rule.

## Registration Hierarchy

```text
conditional_rendering.clear_attachments
├── condition_host_memory_expect_execution
├── condition_host_memory_expect_execution_inverted
├── condition_host_memory_expect_noop
├── condition_host_memory_expect_noop_inverted
├── condition_host_memory_inherited_expect_execution
├── condition_host_memory_inherited_expect_execution_inverted
├── condition_host_memory_inherited_expect_noop
├── condition_host_memory_inherited_expect_noop_inverted
├── condition_host_memory_nested_buffer_expect_execution
├── condition_host_memory_nested_buffer_expect_execution_inverted
├── condition_host_memory_nested_buffer_expect_noop
├── condition_host_memory_nested_buffer_expect_noop_inverted
├── condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── condition_host_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── condition_host_memory_nested_buffer_nested_inherited_expect_noop
├── condition_host_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── condition_host_memory_nested_inherited_expect_execution
├── condition_host_memory_nested_inherited_expect_execution_inverted
├── condition_host_memory_nested_inherited_expect_noop
├── condition_host_memory_nested_inherited_expect_noop_inverted
├── condition_host_memory_secondary_buffer_expect_execution
├── condition_host_memory_secondary_buffer_expect_execution_inverted
├── condition_host_memory_secondary_buffer_expect_noop
├── condition_host_memory_secondary_buffer_expect_noop_inverted
├── condition_host_memory_secondary_buffer_inherited_expect_execution
├── condition_host_memory_secondary_buffer_inherited_expect_execution_inverted
├── condition_host_memory_secondary_buffer_inherited_expect_noop
├── condition_host_memory_secondary_buffer_inherited_expect_noop_inverted
├── condition_local_memory_expect_execution
├── condition_local_memory_expect_execution_inverted
├── condition_local_memory_expect_noop
├── condition_local_memory_expect_noop_inverted
├── condition_local_memory_inherited_expect_execution
├── condition_local_memory_inherited_expect_execution_inverted
├── condition_local_memory_inherited_expect_noop
├── condition_local_memory_inherited_expect_noop_inverted
├── condition_local_memory_nested_buffer_expect_execution
├── condition_local_memory_nested_buffer_expect_execution_inverted
├── condition_local_memory_nested_buffer_expect_noop
├── condition_local_memory_nested_buffer_expect_noop_inverted
├── condition_local_memory_nested_buffer_nested_inherited_expect_execution
├── condition_local_memory_nested_buffer_nested_inherited_expect_execution_inverted
├── condition_local_memory_nested_buffer_nested_inherited_expect_noop
├── condition_local_memory_nested_buffer_nested_inherited_expect_noop_inverted
├── condition_local_memory_nested_inherited_expect_execution
├── condition_local_memory_nested_inherited_expect_execution_inverted
├── condition_local_memory_nested_inherited_expect_noop
├── condition_local_memory_nested_inherited_expect_noop_inverted
├── condition_local_memory_secondary_buffer_expect_execution
├── condition_local_memory_secondary_buffer_expect_execution_inverted
├── condition_local_memory_secondary_buffer_expect_noop
├── condition_local_memory_secondary_buffer_expect_noop_inverted
├── condition_local_memory_secondary_buffer_inherited_expect_execution
├── condition_local_memory_secondary_buffer_inherited_expect_execution_inverted
├── condition_local_memory_secondary_buffer_inherited_expect_noop
├── condition_local_memory_secondary_buffer_inherited_expect_noop_inverted
├── no_condition_host_memory_nested_buffer_nested_inherited_expect_execution
├── no_condition_host_memory_secondary_buffer_inherited_expect_execution
├── no_condition_local_memory_nested_buffer_nested_inherited_expect_execution
└── no_condition_local_memory_secondary_buffer_inherited_expect_execution
```

Each direct child above expands to the `clear_attachments` test case leaf. The complete executable paths are confirmed by the [conditional-rendering mustpass entries](../../../mustpass/main/vk-default/conditional-rendering.txt#L1-L60) and are created by [the registration loop](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L269-L290).

## Parameter Dimensions and Observed Values

The implementation consumes a shared `ConditionalData` row for each child. The matrix has 60 rows after the render-pass-clear rows are excluded.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Condition location | primary, secondary, or none | Selects where `vkCmdBeginConditionalRenderingEXT` is recorded. | [ConditionalData table](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L44-L103) |
| Condition value and inversion | `0`, `1`; inverted or non-inverted | Determines whether the clear should execute. | [condition fields and helper](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L46-L50), [begin helper](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L124-L135) |
| Buffer memory | `HOST`, `LOCAL` | Uses a host-visible conditional buffer directly, or copies it to a device-local buffer first. | [buffer creation](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121) |
| Inheritance | false, true | Controls whether a secondary command buffer inherits permission to execute under an active primary condition. | [capability check](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L45-L58) |
| Secondary topology | ordinary, nested | Selects direct execution of the clear secondary or execution through a nested secondary command buffer. | [nested recording path](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L114-L143), [nested execution](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L175-L213) |
| Expected result | `expect_execution`, `expect_noop` | Selects an all-blue or all-black reference image. | [reference selection](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L220-L249) |
| `clearInRenderPass` | false for this page | Excludes rows that test render-pass-start clearing instead of `vkCmdClearAttachments`. | [registration filter](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L269-L277) |
| `padConditionValue`, `allocationOffset` | false for this family | These utility dimensions are not varied by this registration table. | [condition table](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L61-L143) |

## Behavior Parameters

The primary behavioral axis is the condition-data row, expressed by the registered child name. Its values change the command-buffer context and predicate outcome that control the clear. Memory placement is a transport variation and does not change the expected color.

### Primary conditional block: condition recorded in the primary command buffer

The primary records `vkCmdBeginConditionalRenderingEXT`, then records either the inline clear or execution of a prepared secondary command buffer. The condition begins and ends in the primary, so the primary predicate controls the clear directly and, when inheritance is enabled, can also control the executed secondary.

### Secondary conditional block: condition recorded in the secondary command buffer

The secondary records its own conditional begin, `vkCmdClearAttachments`, and conditional end. The primary executes the secondary without an active condition from this test path. This checks conditional rendering state local to the secondary command buffer.

### Inherited conditional state: primary condition controls an inherited secondary

When `conditionInPrimaryCommandBuffer` and `conditionInherited` are both true, the secondary is begun with `conditionalRenderingEnable = VK_TRUE`, records the clear without its own conditional block, and the primary condition determines whether the secondary clear takes effect. The `conditionInSecondaryCommandBuffer` + `conditionInherited` rows are different: their conditional block is local to the secondary, while the inheritance flag only permits execution under a possible active primary condition; this test path has no such primary condition. The implementation requires inherited conditional rendering for both forms and, when inheritance is requested without a secondary-local condition, also requires `VK_KHR_maintenance7`.

### Nested secondary execution: the clear crosses two `vkCmdExecuteCommands` calls

The clear secondary is executed by a nested secondary command buffer, which the primary then executes. This adds command-buffer nesting to either the inherited or secondary-local condition path and requires nested command-buffer rendering support.

### No active condition: unconditional control case

The `no_condition_*` rows do not begin conditional rendering. They execute the clear through the corresponding secondary topology and provide a control for command-buffer inheritance and nesting without an active predicate.

### Predicate outcome: `expect_execution`, `expect_noop`, and inversion

With a non-inverted condition, the selected condition value determines whether the clear runs according to the extension's conditional rule. An inverted row flips that decision. The registered suffix names the expected outcome, while the host's reference image records the final contract: blue means the clear ran, black means setup remained visible.

## Shader Analysis

The test loads fixed vertex and fragment shaders for the graphics pipeline, but it records no draw command. The shaders therefore do not produce the image being checked. The walkthrough below documents the vertex stage as a representative pipeline artifact; the correctness behavior remains the fixed-function conditional clear.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.conditional_rendering.clear_attachments.condition_host_memory_expect_execution.clear_attachments
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `condition_host_memory_expect_execution` | Selects a host-visible condition buffer and a predicate outcome where the attachment clear is expected to execute. |
| `VertexFetch.vert` | The fixed vertex stage used to create the graphics pipeline. No draw consumes it in this test. |
| `VK_FORMAT_R8G8B8A8_UNORM` color attachment | The render target whose contents are checked after the command buffer completes. |

#### Purpose

This fixed vertex stage forwards vertex position and color to the next stage. The clear test does not record a draw, so the stage is not part of the observed pass/fail result.

#### Structural Design

| Stage action | Data path |
|-------------|-----------|
| Vertex input | Read `in_position` at location 0 and `in_color` at location 1. |
| Position output | Copy `in_position` to `gl_Position`. |
| Color output | Copy `in_color` to `out_color` at location 0. |

#### Shader Code

Reconstructed GLSL for the fixed vertex stage:

```glsl
#version 450
precision highp float;

/// Location 0 supplies the vertex position used by the fixed graphics pipeline.
layout(location = 0) in vec4 in_position;
/// Location 1 supplies a color that would pass to the fragment stage if a draw were recorded.
layout(location = 1) in vec4 in_color;

/// The stage forwards color at location 0 to the fixed fragment-stage interface.
layout(location = 0) out vec4 out_color;
out gl_PerVertex { vec4 gl_Position; };

void main() {
    /// The position controls rasterization for a draw, but this clear test records no draw.
    gl_Position = in_position;
    /// The color is part of the common pipeline artifact, not the clear result.
    out_color = in_color;
}
```

#### Additional Info

- The implementation binds the pipeline before recording the clear, but `vkCmdClearAttachments` is not affected by bound pipeline state according to the Vulkan clear-command specification.
- The fragment stage is loaded by the common draw base class but is not shown because no draw consumes it in this test.
- The representative condition row is one of the 60 rows that pass the `clearInRenderPass == false` registration filter.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Condition-data row | No shader text changes. The row changes conditional command recording and image expectation, while the fixed pipeline artifact remains the same. | [test specification and pipeline construction](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L50-L90) |
| Vertex input data | The base class supplies one zero-valued vertex element, but this test does not issue a draw. | [vertex data setup](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L82-L84) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 21
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position %out_color %in_color
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %in_position "in_position"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %in_position Location 0
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %in_position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
         %20 = OpLoad %v4float %in_color
               OpStore %out_color %20
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- **Capability checks.** Construction requires `VK_EXT_conditional_rendering` and the `conditionalRendering` feature. Every row also requires `VK_EXT_nested_command_buffer`, `nestedCommandBuffer`, and `nestedCommandBufferRendering`, because the constructor unconditionally calls `checkNestedRenderPassCapabilities()`; inherited rows additionally require `inheritedConditionalRendering`, and inherited primary cases also require `VK_KHR_maintenance7` [shared capability checks](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L68).
- **Condition buffer.** `createConditionalRenderingBuffer()` allocates a 32-bit host-visible buffer, writes the selected value, fills other bytes with `1`, and flushes the allocation. `HOST` passes that buffer to conditional rendering. `LOCAL` copies the host buffer to a device-local buffer on the selected queue before the graphics submission [buffer setup](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121).
- **Color target setup.** The common draw base creates a `VK_FORMAT_R8G8B8A8_UNORM` color image with color-attachment and transfer-source usage, an image view, a one-attachment render pass, and a framebuffer [base initialization](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L51-L115). `preRenderBarriers()` clears the image to black and inserts a transfer-write to color-attachment dependency [pre-render barrier](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L198-L216).
- **Render-pass recording.** The test begins a legacy render pass with inline contents, secondary contents, or `VK_SUBPASS_CONTENTS_INLINE_AND_SECONDARY_COMMAND_BUFFERS_KHR` as required by the condition-data row. It binds the graphics pipeline and prepares a full-frame color clear with `VK_IMAGE_ASPECT_COLOR_BIT` and one layer [render setup](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L101-L152).
- **Conditional command paths.** A secondary-local row wraps `vkCmdClearAttachments` in a conditional block in the secondary. An inherited row records the clear in a secondary begun with `VkCommandBufferInheritanceConditionalRenderingInfoEXT`. A primary row wraps either the inline clear or the secondary execution in the primary's conditional block. Nested rows execute the clear secondary through a nested secondary [conditional paths](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L160-L213).
- **Submission and check.** The primary command buffer ends the render pass, submits to the universal queue, and waits. The host builds a full-frame reference filled with `drawColor` when `expectCommandExecution` is true, otherwise `clearColor`. It reads the image in `VK_IMAGE_LAYOUT_GENERAL` and uses `tcu::fuzzyCompare()` with a `0.05f` threshold [submission and validation](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L215-L254).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Why it matters |
|----------|-----------------------------|---------------|---------------|---------------|----------------|
| Conditional buffer | Yes | `VkConditionalRenderingBeginInfoEXT` | Read for the predicate | No | Selects execution or suppression of the clear. |
| Color target image and view | Yes | Render-pass framebuffer | Cleared during setup and possibly by `vkCmdClearAttachments` | Yes, through `readSurface()` | Carries the result compared with the reference image. |
| Render pass and framebuffer | Yes | Render-pass instance | Supplies the active color attachment and render area | No | Gives `vkCmdClearAttachments` its required context. |
| Primary, secondary, and nested command buffers | Yes | Submission or `vkCmdExecuteCommands` | Record conditional state, clear commands, or nested execution commands | No | Exercise command-buffer placement, inheritance, and nesting. |
| Fixed graphics pipeline | Yes | Bound before the clear | No draw is recorded | No | Provides the valid pipeline context without determining the clear value. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Primary conditional block | The primary command buffer did not apply the condition to `vkCmdClearAttachments`, or it applied inversion incorrectly. |
| Secondary conditional block | The secondary command buffer did not apply its own conditional block to the clear, or it ended the block incorrectly. |
| Inherited conditional state | The inherited `conditionalRenderingEnable` state did not match the active primary condition when the secondary executed. |
| Nested secondary execution | Conditional state was not preserved across the nested `vkCmdExecuteCommands` chain. |
| No active condition | The unconditional secondary path changed the clear result or command-buffer execution state. |
| Any context with `expect_execution` or `expect_noop` | The condition buffer value, inversion flag, memory placement, or condition offset was interpreted incorrectly. |

### Cause Analysis

#### Conditional predicate handling

**Possible failure symptoms:** The readback is blue when the selected row expects a no-op, or black when it expects execution. The mismatch is detected by the full-frame fuzzy image comparison.

**Possible implementation causes:** The extension requires the implementation to evaluate the 32-bit buffer value and apply `VK_CONDITIONAL_RENDERING_INVERTED_BIT_EXT` when set. A failure can indicate incorrect predicate evaluation, inversion handling, or application of conditional rendering to `vkCmdClearAttachments`. The exact implementation cause requires investigation of the failing path.

#### Command-buffer conditional state

**Possible failure symptoms:** Rows that use a primary condition, a secondary-local condition, inherited state, or nested execution produce a different color from equivalent direct execution rows.

**Possible implementation causes:** The extension specification defines how an active primary condition affects a secondary whose inheritance structure enables conditional rendering. A mismatch between the recorded begin/end state and the command-buffer execution topology can cause the clear to be skipped or applied in the wrong context. The exact implementation cause requires investigation of the failing command-buffer path.

#### Condition-buffer transport

**Possible failure symptoms:** `HOST` rows pass while `LOCAL` rows produce the wrong all-blue or all-black image, or the result changes only for a condition-buffer placement variant.

**Possible implementation causes:** `LOCAL` rows depend on the host-to-device buffer copy completing before conditional rendering reads the buffer, and on the buffer's conditional-rendering usage and offset being honored. A failure can indicate a problem in buffer visibility, copy ordering, or conditional buffer access. The exact implementation cause requires investigation.

#### Attachment result or readback

**Possible failure symptoms:** The image differs from the expected uniform color, including stale black pixels after an expected clear or unexpected blue pixels after an expected no-op.

**Possible implementation causes:** `vkCmdClearAttachments` writes the selected color attachment inside the render pass and uses the supplied clear value and rectangle. The test also relies on the setup clear, transfer-to-color-attachment barrier, render-pass execution, image layout, and `readSurface()` copyback. A mismatch can originate in conditional clear execution, attachment writes, synchronization, layout handling, or host-side readback; source-level investigation is needed to distinguish them.

## Case Pruning

### Requirement-based pruning

- Every row requires `VK_EXT_conditional_rendering` and the `conditionalRendering` feature. Every row also requires `VK_EXT_nested_command_buffer`, `nestedCommandBuffer`, and `nestedCommandBufferRendering`, because `checkNestedRenderPassCapabilities()` is called unconditionally by the test constructor. Inherited rows additionally require `inheritedConditionalRendering` [capability checks](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L68).
- When conditional rendering is inherited by a secondary and the condition is established in the primary, the helper requires `VK_KHR_maintenance7` [maintenance requirement](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L56-L58).

### Design-based pruning

- Registration skips every `ConditionalData` row with `clearInRenderPass` set. Those rows belong to a different render-pass-clear behavior and are not `vkCmdClearAttachments` cases [registration filter](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L269-L277).
- `padConditionValue` and `allocationOffset` remain false for all rows registered by this family. The utility supports those dimensions for other conditional-rendering families, but this page does not exercise them [shared condition table](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L61-L143).
- The test uses one color attachment, a full render-area clear, one array layer, and a fixed pipeline artifact. It does not vary attachment aspect, clear rectangle size, shader behavior, or draw output.
- The family uses the universal queue and a legacy render pass. Compute-queue and dynamic-rendering variants belong to other conditional-rendering test families.

## Key Takeaways

- The observable contract is simple: an allowed clear changes the image from black to blue, while a suppressed clear leaves it black.
- The 60 registered children keep that contract while moving conditional state between primary and secondary command buffers, adding inheritance or nesting, changing predicate inversion, and changing condition-buffer memory.
- The bound shaders are not the source of the checked pixels because the test records no draw. The page's shader walkthrough documents pipeline setup only.
- Failures should be interpreted through both predicate outcome and command-buffer topology. A memory-placement-only failure points toward condition-buffer transport, while a topology-specific failure points toward conditional state propagation or inheritance.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `ConditionalClearAttachmentTest` construction | [constructor](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L50-L90) | Performs capability checks, initializes the draw base, and allocates secondary command buffers. |
| `ConditionalClearAttachmentTest::iterate()` | [execution and validation](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L92-L254) | Records the render pass and conditional clear paths, submits work, and checks the image. |
| `ConditionalClearAttachmentTests::init()` | [registration](../../../modules/vulkan/conditional_rendering/vktConditionalClearAttachmentTests.cpp#L259-L290) | Creates the condition-data children, skips render-pass-clear rows, and adds each `clear_attachments` leaf. |
| `ConditionalData` and `s_testsData` | [shared condition table](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.hpp#L38-L144) | Defines the matrix fields and the 60 rows used by this family. |
| `checkConditionalRenderingCapabilities()` | [feature checks](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L36-L58) | Gates extension, inherited, nested, and maintenance requirements. |
| `createConditionalRenderingBuffer()` | [condition-buffer setup](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L70-L121) | Implements host-visible and device-local condition-buffer paths. |
| `beginConditionalRendering()` | [conditional begin](../../../modules/vulkan/conditional_rendering/vktConditionalRenderingTestUtil.cpp#L124-L135) | Supplies the selected buffer offset and inversion flag. |
| `DrawTestsBaseClass::initialize()` | [graphics resources](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L51-L153) | Creates the target image, framebuffer, vertex buffer, command pool, and pipeline. |
| `DrawTestsBaseClass::preRenderBarriers()` | [image initialization](../../../modules/vulkan/draw/vktDrawBaseClass.cpp#L198-L216) | Clears the target to black and orders the transfer write before attachment access. |
| `VK_EXT_conditional_rendering` description | [extension specification](../../../../vulkan-docs/src/appendices/VK_EXT_conditional_rendering.adoc#L21-L45) | Defines conditional rendering scope and primary-to-secondary behavior. |
| `vkCmdClearAttachments` semantics | [clear specification](../../../../vulkan-docs/src/chapters/clears.adoc#L245-L295) | Defines the render-pass context, attachment writes, and pipeline independence. |
| Conditional inheritance | [command-buffer inheritance](../../../../vulkan-docs/src/chapters/cmdbuffers.adoc#L1288-L1321) | Defines `conditionalRenderingEnable` for secondary command-buffer execution. |
| `clear_attachments` mustpass | [registered leaves](../../../mustpass/main/vk-default/conditional-rendering.txt#L1-L60) | Confirms all 60 executable paths covered by the page. |
