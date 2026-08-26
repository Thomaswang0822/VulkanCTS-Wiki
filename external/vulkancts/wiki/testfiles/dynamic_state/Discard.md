## Overview

**Core question:** When the fragment shader discards every fragment, do dynamic state commands recorded before the draw leave the color, depth, and stencil attachments untouched at their clear values?

- This page covers the `discard` test family in the `dynamic_state` test category, implemented in [vktDynamicStateDiscardTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L1).
- Each leaf records one category of dynamic state command before a full-screen draw, while the fragment shader unconditionally calls `discard`. The case passes when the relevant attachment stays at its clear value.
- Six leaves cover the major dynamic state categories: `stencil`, `viewport`, `scissor`, `depth`, `blend`, and `line`.
- All leaves share the same vertex/fragment shader pair and a common harness derived from `DynamicStateBaseClass`.

## Background Knowledge

- **Fragment discard.** The GLSL `discard` keyword terminates the current fragment shader invocation. A discarded fragment does not update color, depth, or stencil attachments, so later per-fragment operations (depth test, stencil test, blending) have no effect for it.
- **Dynamic state.** Vulkan graphics state can be static, fixed at pipeline creation, or dynamic, set with a `vkCmdSet*` command during command-buffer recording. A dynamic state command affects subsequent draws that produce fragments reaching the output attachments.

## Registration Hierarchy

```text
dynamic_state.monolithic.discard
├── stencil
├── viewport
├── scissor
├── depth
├── blend
└── line
```

The same six leaves are registered once per pipeline construction type by the category dispatcher ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L759-L778)). The tree above shows the `monolithic` construction variant; `pipeline_library`, `fast_linked_library`, and `shader_object_*` variants follow the same shape.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Dynamic state type | `stencil`, `viewport`, `scissor`, `depth`, `blend`, `line` | The primary behavioral axis: selects which `vkCmdSet*` command is recorded before the draw and which attachment is read back. | [`TestDynamicStateDiscard` enum](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L51-L59), [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L759-L778) |
| Pipeline construction type | `monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_*` | Passed from the parent group. Shader-object construction replaces `vkCmdSetViewport`/`vkCmdSetScissor` with the with-count equivalents. | [ViewportTestInstance::setDynamicState](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L433-L448), [mustpass](../../../mustpass/main/vk-default/dynamic-state.txt#L188-L193) |
| Depth/stencil format | Runtime-selected by `pickSupportedStencilFormat()` for `stencil`, `viewport`, `scissor`, `blend`, `line`; `VK_FORMAT_D32_SFLOAT` for `depth` | The depth/stencil attachment format whose clear value is checked. Stencil leaves need a stencil-capable format; the depth leaf needs a depth-only format. | [pickSupportedStencilFormat](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L61-L74), [DepthTestInstance](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L531-L541) |
| Render dimensions | 128x128 | Fixed framebuffer size from the shared base class. | [DynamicStateBaseClass](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L90-L91) |

## Behavior Parameters

The primary behavioral axis is the dynamic state type. Each leaf records a different `vkCmdSet*` category before the same full-screen draw and reads back a different attachment, but every leaf tests the same property: discard must suppress state-dependent output.

### `stencil`: dynamic stencil state with discard

Records `vkCmdSetStencilCompareMask`, `vkCmdSetStencilWriteMask`, and `vkCmdSetStencilReference` for both front and back faces. The fragment shader discards every fragment. The test reads the stencil aspect of the depth/stencil image and requires every pixel to equal 0, the stencil clear value. The pipeline queries the device `depthBounds` feature at construction only to configure depth-bounds test state, not to gate the case ([StencilTestInstance](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L360-L419)).

### `viewport`: dynamic viewport with discard

Records `vkCmdSetViewport`, or `vkCmdSetViewportWithCount` under shader-object construction. The fragment shader discards every fragment. The test reads the color attachment and requires every pixel to equal `(0, 0, 0, 1)`, the black clear color ([ViewportTestInstance](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L421-L474)).

### `scissor`: dynamic scissor with discard

Records `vkCmdSetScissor`, or `vkCmdSetScissorWithCount` under shader-object construction. The fragment shader discards every fragment. The test reads the color attachment and requires every pixel to equal the black clear color ([ScissorTestInstance](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L476-L529)).

### `depth`: dynamic depth bias and bounds with discard

Records `vkCmdSetDepthBias` and `vkCmdSetDepthBounds` against a `VK_FORMAT_D32_SFLOAT` depth attachment. The fragment shader discards every fragment. The test reads the depth aspect and requires every pixel to equal `0.0f`, the depth clear value ([DepthTestInstance](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L531-L570)).

### `blend`: dynamic blend constants with discard

Records `vkCmdSetBlendConstants`. The fragment shader discards every fragment. The test reads the color attachment and requires every pixel to equal the black clear color ([BlendTestInstance](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L572-L614)).

### `line`: dynamic line width with discard

Records `vkCmdSetLineWidth`. The fragment shader discards every fragment. The test reads the color attachment and requires every pixel to equal the black clear color ([LineTestInstance](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L616-L657)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dynamic_state.monolithic.discard.stencil
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `monolithic` | Uses the monolithic graphics-pipeline construction path; shader-object viewport/scissor command substitutions are not involved. |
| `stencil` | Records dynamic stencil masks and references before the draw, then checks that discarded fragments leave the stencil clear value unchanged. |
| `discard_all = 0` | The host zero-fills the uniform buffer, making the fragment shader take the discard branch for every invocation. |

#### Purpose

This fragment shader terminates every fragment before it can contribute color, depth, or stencil updates. The `stencil` leaf therefore isolates whether dynamic stencil state can incorrectly cause attachment writes for discarded fragments.

#### Structural Design

| Phase | Shader behavior | Shader-visible data |
|-------|-----------------|---------------------|
| Read control | Load `discard_all` from the uniform block. | Set 0, binding 0; one host-written 32-bit integer with value 0. |
| Discard | Compare the value with zero and execute `discard` when equal. | The host value makes this branch uniform and true for every fragment. |
| Surviving path | Copy the interpolated vertex color to the fragment output. | Location 0 input and output; unreachable in this representative execution. |
| Result observation | No shader write records success directly. | The host verifies that the stencil attachment remains at its clear value 0. |

#### Shader Code

```glsl
#version 450

/// Set 0, binding 0 is a four-byte std140 uniform buffer. The host writes zero, so every
/// fragment takes the discard branch.
layout (set=0, binding=0, std140) uniform InputBlock {
    int discard_all;
} unif;

/// Location 0 carries the interpolated green vertex color; it is read only if the fragment survives.
layout (location = 0) in vec4 in_color;

/// Location 0 targets the color attachment, but the representative host value prevents this write.
layout (location = 0) out vec4 color;

void main ()
{
    /// Terminate every fragment before color, depth, or stencil can be updated.
    if (unif.discard_all == 0) {
        discard;
    }
    color = in_color;
}
```

#### Additional Info

- `DiscardTestInstance::iterate()` allocates exactly `sizeof(int)` bytes, clears them to zero, and binds that range as the binding-0 uniform buffer ([uniform setup](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L292-L337)).
- The fixed vertex shader passes position and color through unchanged; it does not vary among the six leaves and is omitted because fragment termination is the tested shader behavior ([shader generation](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L700-L738)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Dynamic state type | `stencil`, `viewport`, `scissor`, `depth`, `blend`, and `line` all reuse this exact fragment shader; only host-recorded dynamic commands and attachment verification change. | [`createInstance()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L677-L698) |
| Pipeline construction type | The same `discard.vert`/`discard.frag` pair is used for monolithic, pipeline-library, fast-linked-library, and shader-object construction; construction changes pipeline setup, not GLSL. | [`DiscardTestCase::initPrograms()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L700-L738) |
| Uniform value | This file registers no varying value: every case zero-fills `discard_all`, so the surviving color-write path is present in GLSL but not taken at runtime. | [`DiscardTestInstance::iterate()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L292-L351) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 26
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %color %in_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %InputBlock "InputBlock"
               OpMemberName %InputBlock 0 "discard_all"
               OpName %unif "unif"
               OpName %color "color"
               OpName %in_color "in_color"
               OpDecorate %InputBlock Block
               OpMemberDecorate %InputBlock 0 Offset 0
               OpDecorate %unif Binding 0
               OpDecorate %unif DescriptorSet 0
               OpDecorate %color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
 %InputBlock = OpTypeStruct %int
%_ptr_Uniform_InputBlock = OpTypePointer Uniform %InputBlock
       %unif = OpVariable %_ptr_Uniform_InputBlock Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_int = OpTypePointer Uniform %int
       %bool = OpTypeBool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %color = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %in_color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpAccessChain %_ptr_Uniform_int %unif %int_0
         %13 = OpLoad %int %12
         %15 = OpIEqual %bool %13 %int_0
               OpSelectionMerge %17 None
               OpBranchConditional %15 %16 %17
         %16 = OpLabel
               OpKill
         %17 = OpLabel
         %25 = OpLoad %v4float %in_color
               OpStore %color %25
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` only checks pipeline construction requirements for all leaves. No device extension is required ([checkSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L671-L675)).
- Each test instance creates a depth/stencil image and view in addition to the shared color target. The vertex data is a full-screen triangle strip in green ([constructor](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L114-L149)).
- `iterate()` allocates a uniform buffer, zeroes it, begins the render pass with a black color clear and a zeroed depth/stencil clear, records the leaf-specific `setDynamicState()` commands, binds the pipeline, draws the triangle strip, and ends the render pass. The shared harness submits and waits ([iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L292-L358)).
- Each leaf's `verifyResults()` reads the relevant attachment back to the host and iterates over every pixel. Any pixel that deviates from the expected clear value fails the case.

| Leaf | Attachment read | Expected value |
|------|-----------------|----------------|
| `stencil` | Stencil aspect of depth/stencil image | All pixels equal 0 |
| `viewport` | Color attachment | All pixels equal `(0, 0, 0, 1)` |
| `scissor` | Color attachment | All pixels equal `(0, 0, 0, 1)` |
| `depth` | Depth aspect of depth/stencil image | All pixels equal `0.0f` |
| `blend` | Color attachment | All pixels equal `(0, 0, 0, 1)` |
| `line` | Color attachment | All pixels equal `(0, 0, 0, 1)` |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `stencil` | A discarded fragment still wrote the stencil attachment, or dynamic stencil state caused an unexpected write. |
| `viewport` | A discarded fragment still wrote the color attachment, or dynamic viewport state altered the draw in a way that produced output. |
| `scissor` | A discarded fragment still wrote the color attachment, or dynamic scissor state altered the draw in a way that produced output. |
| `depth` | A discarded fragment still wrote the depth attachment, or depth bias/bounds state altered depth output. |
| `blend` | A discarded fragment still wrote the color attachment, or dynamic blend constants altered output. |
| `line` | A discarded fragment still wrote the color attachment, or dynamic line width altered output. |
| All leaves | Shared discard infrastructure failed: the fragment shader did not discard, the uniform buffer was not zeroed, or the clear value was wrong. |

### Cause Analysis

#### Discard did not prevent attachment writes

**Possible failure symptoms:** One or more pixels in the checked attachment deviate from the expected clear value. For a color leaf the framebuffer shows the green triangle; for the depth or stencil leaf the corresponding aspect shows the post-draw value instead of 0.

**Possible implementation causes:** The implementation may fail to suppress color, depth, or stencil writes for discarded fragments, or an early-fragment-test path may run depth/stencil updates before the shader discards. The Vulkan specification requires that a discarded fragment not update the color, depth, or stencil attachments, so any write after discard is a specification violation. Whether the defect lives in the fragment execution model, the early-z path, or the interaction with one specific dynamic state requires inspecting the failing leaf and the relevant specification text.

#### Shared discard mechanism broken

**Possible failure symptoms:** All six leaves fail identically, with the full-screen triangle visible in every attachment.

**Possible implementation causes:** The uniform buffer was not zeroed as expected, the shader read the wrong binding, or the `discard` keyword itself was not honored. Because every leaf shares the same shader and uniform setup, a uniform failure across leaves points at the discard mechanism rather than any single dynamic state.

## Case Pruning

### Requirement-based pruning

- All leaves check pipeline construction requirements via `checkSupport()`. No additional device features or extensions are required. The `depth` leaf uses `VK_FORMAT_D32_SFLOAT` directly, and the `stencil` leaf queries the `depthBounds` feature only to configure pipeline state, not to gate the case.

### Design-based pruning

- The six leaves are fixed. Each covers one representative state per category; the test records a representative value and checks that discard suppresses output. It does not enumerate every value of each dynamic state.
- The fragment shader discards unconditionally. There is no partial-discard variant in this file.

## Key Takeaways

- The dynamic state type is the behavioral axis, but every leaf tests the same property: discard must suppress state-dependent output.
- A passing result means the checked attachment stayed at its clear value. Any non-clear pixel is a failure, regardless of which dynamic state was set.
- A failure isolated to one leaf suggests that dynamic state interacted with discard incorrectly for that state category. A failure across all leaves suggests the discard mechanism itself is broken.
- Shader-object construction swaps the with-count viewport/scissor commands for the fixed-count variants, but the tested property is unchanged.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration | [`DynamicStateDiscardTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L759-L778) | Registers the six dynamic-state-type leaves. |
| Support check | [`DiscardTestCase::checkSupport()`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L671-L675) | Pipeline construction requirements for all leaves. |
| Shared base | [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) | Resource setup, render pass, and submit flow shared by all leaves. |
| `stencil` instance | [`StencilTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L360-L419) | Dynamic stencil state and stencil-aspect verification. |
| `viewport` instance | [`ViewportTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L421-L474) | Dynamic viewport state and color-attachment verification. |
| `scissor` instance | [`ScissorTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L476-L529) | Dynamic scissor state and color-attachment verification. |
| `depth` instance | [`DepthTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L531-L570) | Dynamic depth bias/bounds and depth-aspect verification. |
| `blend` instance | [`BlendTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L572-L614) | Dynamic blend constants and color-attachment verification. |
| `line` instance | [`LineTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L616-L657) | Dynamic line width and color-attachment verification. |
| Shaders | [vert/frag](../../../modules/vulkan/dynamic_state/vktDynamicStateDiscardTests.cpp#L700-L738) | Pass-through vertex shader and unconditionally-discarding fragment shader. |
