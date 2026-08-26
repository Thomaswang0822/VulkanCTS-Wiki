## Overview

**Core question:** When several dynamic states are set together, switched between draws, reordered, or persist across pipeline binds, does each dynamic state still take effect as specified, and do edge cases around static-mask-zero and double static bind behave correctly?

- [vktDynamicStateGeneralTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L1) implements the `general_state` test family of the `dynamic_state` test category.
- The file groups several mixed dynamic-state behaviors that do not belong to a single state area: switching scissor state between draws, reordering dynamic-state setup, verifying that dynamic state survives a pipeline rebind, probing the static stencil write mask zero edge case, and checking that a double static bind still lets the dynamic value win.
- Each behavior is its own test case leaf and is driven by a distinct test instance or function-style case. Vertex and mesh-shader pipeline variants share the same test logic for the switching and bind-order cases; the remaining cases are vertex-only.
- A shared harness ([DynamicStateBaseClass](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43)) provides the 128x128 framebuffer, render pass, pipeline scaffold, and `setDynamic*State()` helpers.

## Background Knowledge

- **Dynamic state.** Vulkan pipeline state can be static, fixed at pipeline creation, or dynamic, set by a `vkCmdSet*` command during command-buffer recording. Dynamic state set before a draw applies to that draw; setting it again between draws changes what later draws see.
- **Scissor test.** The scissor rectangle clips rasterized fragments to a sub-region of the framebuffer. Pixels outside the scissor are discarded before color write, so changing the scissor between two draws of the same geometry produces a different visible region per draw.
- **Static stencil write mask.** The stencil write mask is a per-face bitfield controlling which stencil bits a stencil operation may modify. A static mask of zero means the pipeline is created with no stencil write bits enabled; a dynamic mask of `0xFF` set at recording time is expected to re-enable all bits for that draw.

## Registration Hierarchy

```text
dynamic_state.monolithic.general_state
├── state_switch
├── state_switch_mesh              (non-VulkanSC only)
├── bind_order
├── bind_order_mesh                (non-VulkanSC only)
├── state_persistence
├── static_stencil_mask_zero
└── double_static_bind             (non-shader-object construction types only)
```

The test family is registered once per pipeline construction type by the category dispatcher. The `_mesh` leaves are conditionally compiled out under `CTS_USES_VULKANSC`; `double_static_bind` is omitted entirely for shader-object construction types ([registration](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L927-L979)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test case leaf | `state_switch`, `state_switch_mesh`, `bind_order`, `bind_order_mesh`, `state_persistence`, `static_stencil_mask_zero`, `double_static_bind` | The primary behavioral axis: each leaf exercises a different mixed-state property. | [registration](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L927-L979) |
| Shader type | Vertex+Fragment vs. Mesh+Fragment | Selects the input assembly path. The `init()` loop runs both for `state_switch` and `bind_order`; the other cases are vertex-only. | [init loop](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L934-L968) |
| Pipeline construction type | Passed from the parent group | Selects monolithic, pipeline-library, fast-linked-library, or shader-object construction. `double_static_bind` is skipped for shader-object types. | [guard](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L975) |
| Scissor configuration | `{0,0,W/2,H/2}` and `{W/2,H/2,W/2,H/2}` | The two scissors that produce the two-quadrant reference pattern for the switching, bind-order, and persistence cases. | [StateSwitchTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L86-L87) |
| Render dimensions | 128x128 | Fixed framebuffer size from the shared base class. | [DynamicStateBaseClass](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L90-L91) |

## Behavior Parameters

The primary behavioral axis is the test case leaf. Each leaf tests a different property of mixed dynamic-state handling.

### `state_switch` and `state_switch_mesh`: scissor change between draws

The leaf sets dynamic rasterization, blend, and depth/stencil state once, then performs two draws of the same full-screen green quad with different dynamic scissors: the first scissor covers the top-left quadrant, the second covers the bottom-right quadrant. The reference frame is green in exactly those two quadrants and black elsewhere. This verifies that changing dynamic scissor state between draws takes effect per-draw. The `_mesh` variant uses a mesh-shader pipeline that fetches the same vertex data from a storage buffer and dispatches one workgroup per triangle ([StateSwitchTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L76-L171)).

### `bind_order` and `bind_order_mesh`: reordered dynamic-state setup

Same geometry and reference pattern as `state_switch`, but after binding the pipeline the dynamic states are set again in a different order (blend, then rasterization, then depth/stencil, then viewport) before the two scissor-switched draws. This verifies that the order in which `vkCmdSet*` commands are recorded does not affect the final rendering result ([BindOrderTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L190-L293)).

### `state_persistence`: dynamic state survives a pipeline rebind

Two pipelines with different topologies (`VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP` and `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`) are built with the same dynamic rasterization, blend, depth/stencil, viewport, and scissor states enabled. The rasterization, blend, and depth/stencil state is set once before the first draw; the viewport and scissor are set before each draw. The first draw uses the strip pipeline with the top-left scissor and green geometry; the second draw rebinds the list pipeline and sets the bottom-right scissor with blue geometry. Because dynamic state is not reset by `vkCmdBindPipeline`, the rasterization, blend, and depth/stencil state set before the first bind must still apply to the second draw after the rebind. The reference frame is green in the top-left quadrant and blue in the bottom-right. This case is vertex-only; the mesh variant is intentionally omitted because the test does not apply to mesh pipelines ([StatePersistenceTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L374-L451), [guard](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L963)).

### `static_stencil_mask_zero`: static mask zero with dynamic override

The pipeline is created with a static stencil write mask of zero, but `vkCmdSetStencilWriteMask` sets the dynamic write mask to `0xFF` before the draw. The fragment shader discards every fragment (the geometry color matches the discard condition), so no fragment should reach the stencil or depth/stencil output. The test checks color, depth, and stencil buffers against their clear values with exact thresholds. This probes the interaction between a zero static mask and a nonzero dynamic mask, a combination that has caused issues on some implementations ([staticStencilMaskZeroProgramsTest](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L519-L792)).

### `double_static_bind`: dynamic value wins over a second static bind

The pipeline is created with a deliberately bad static viewport (1x1) and a good static scissor. The test binds the pipeline, records a bad dynamic scissor, rebinds the same pipeline, sets a good dynamic viewport, and draws a full-screen blue triangle. The dynamic viewport must override the bad static viewport, and the bad dynamic scissor recorded before the rebind must not be applied because scissor is static in this pipeline. The framebuffer must be filled entirely with blue. This case is omitted for shader-object construction types because the test relies on `vkCmdBindPipeline` rebind semantics that do not apply to shader objects ([doubleBindTest](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L824-L910), [guard](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L975)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dynamic_state.monolithic.general_state.static_stencil_mask_zero
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `static_stencil_mask_zero` | Selects the edge case in which a static stencil write mask of zero is overridden dynamically while the fragment shader discards every covered fragment. |
| `monolithic` | Uses a monolithic graphics pipeline; the same generated shader pair is also used by the other registered pipeline construction types. |
| Fragment input color `(0, 0, 1, 1)` | Matches the discard comparison exactly, making every fragment from the full-screen triangle execute `discard`. |

#### Purpose

The fragment shader makes discard part of the test oracle: every covered fragment must be killed before it can change color, depth, or stencil, even though the dynamic stencil write mask enables all bits.

#### Structural Design

| Phase | Shader action | Observable consequence |
|-------|---------------|------------------------|
| Input | Receive the interpolated vertex color at location 0. | Every generated vertex supplies blue, so the fragment input is exactly `(0, 0, 1, 1)`. |
| Discard decision | Compare `inColor` with the blue sentinel and execute `discard` on equality. | No covered fragment proceeds to attachment writes. |
| Fallback output | Copy any nonmatching color to location 0. | This path is present in the generated shader but is unreachable for this representative case. |

#### Shader Code

```glsl
#version 460
/// Location 0 receives the interpolated color emitted by the pass-through vertex shader; all three host-provided
/// vertices are blue in this case, so every covered fragment receives the discard sentinel.
layout (location=0) in vec4 inColor;
/// Location 0 targets the 1x1 R8G8B8A8_UNORM color attachment, but the selected input prevents this write.
layout (location=0) out vec4 outColor;
void main (void) {
    /// Kill the fragment before color output and before the configured stencil REPLACE operation can update stencil.
    if (inColor == vec4(0.0, 0.0, 1.0, 1.0)) {
        discard;
    }
    /// This fallback makes a non-blue input visible; it is unreachable with the selected host vertex data.
    outColor = inColor;
}
```

#### Additional Info

- The host creates a full-screen triangle with blue assigned to every vertex, explicitly noting that the value must match the fragment shader's discard color ([vertex data](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L533-L589)).
- The pipeline enables stencil testing with `VK_STENCIL_OP_REPLACE`, uses static write mask `0`, then records dynamic write mask `0xFF`; unchanged clear values in all three attachments therefore prove that discard suppressed every write ([pipeline and draw setup](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L627-L710), [result checks](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L755-L791)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Test case leaf | `state_switch`, `bind_order`, and `state_persistence` use pass-through fragment shading instead of the blue-equality discard; `double_static_bind` uses a fixed solid-blue fragment output. | [shared shader registration](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L927-L968), [`initDoubleBindPrograms()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L794-L815) |
| Vertex vs. mesh input path | The `_mesh` switching and bind-order leaves replace vertex fetching with a mesh shader, but still use the shared pass-through fragment shader; this discard shader belongs only to the vertex-only `static_stencil_mask_zero` leaf. | [registration loop](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L927-L968) |
| Pipeline construction type | `initStaticStencilMaskZeroPrograms()` ignores its construction-type argument, so changing pipeline construction does not change this GLSL. | [`initStaticStencilMaskZeroPrograms()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L465-L490) |

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
; Bound: 24
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %inColor %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %inColor "inColor"
               OpName %outColor "outColor"
               OpDecorate %inColor Location 0
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %inColor = OpVariable %_ptr_Input_v4float Input
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %13 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
       %bool = OpTypeBool
     %v4bool = OpTypeVector %bool 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
         %10 = OpLoad %v4float %inColor
         %16 = OpFOrdEqual %v4bool %10 %13
         %17 = OpAll %bool %16
               OpSelectionMerge %19 None
               OpBranchConditional %17 %18 %19
         %18 = OpLabel
               OpKill
         %19 = OpLabel
         %23 = OpLoad %v4float %inColor
               OpStore %outColor %23
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The `state_switch`, `bind_order`, and `state_persistence` instances share the base harness: a 128x128 color target, a render pass, a graphics pipeline built with the relevant dynamic states enabled, and a green (and for persistence, blue) full-screen quad in `m_data`. Each `iterate()` begins the render pass, sets the dynamic states, binds the pipeline, records the draws with scissor switches, ends and submits the command buffer ([StateSwitchTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L76-L171), [BindOrderTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L190-L293)).
- The mesh variants of `state_switch` and `bind_order` bind the descriptor set holding the vertex storage buffer, push the vertex offset, and call `cmdDrawMeshTasksEXT` with one workgroup per triangle instead of `cmdDraw` ([mesh path](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L96-L112)).
- `state_persistence` builds a second pipeline (`m_pipelineAdditional`) with `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST`, binds it between the two draws, and uses a vertex offset of 4 into the combined green+blue vertex data ([StatePersistenceTestInstance::initPipeline](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L327-L372)).
- `static_stencil_mask_zero` is a function-style case: it creates a 1x1 color image plus a depth/stencil image (format chosen at runtime from `VK_FORMAT_D32_SFLOAT_S8_UINT` or `VK_FORMAT_D24_UNORM_S8_UINT`), builds a pipeline with stencil test enabled and a REPLACE op, sets the dynamic write mask to `0xFF`, draws three vertices forming a full-screen triangle whose color triggers discard, then copies color, depth, and stencil aspects back to host buffers ([staticStencilMaskZeroProgramsTest](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L519-L792)).
- `double_static_bind` creates a 2x2 color image, builds a pipeline with a bad static viewport and good static scissor, binds the pipeline twice with a bad dynamic scissor in between, sets a good dynamic viewport, draws a full-screen triangle, and copies the color image back ([doubleBindTest](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L824-L910)).

### Pass/fail conditions

| Leaf | Comparison method | Reference | Threshold |
|------|-------------------|-----------|-----------|
| `state_switch`, `bind_order`, `state_persistence` | `tcu::fuzzyCompare` on color attachment | Two-quadrant software reference frame | `0.05f` |
| `static_stencil_mask_zero` | `tcu::floatThresholdCompare` (color) + `tcu::dsThresholdCompare` (depth, stencil) | Clear values: color `(0,0,0,1)`, depth `1.0f`, stencil `0` | `(0,0,0,0)` and `0.0f` |
| `double_static_bind` | `tcu::floatThresholdCompare` on color attachment | Solid blue `(0,0,1,1)` | `(0,0,0,0)` |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `state_switch` or `state_switch_mesh` | The dynamic scissor change between draws did not take effect, so one or both quadrants are wrong or missing. |
| `bind_order` or `bind_order_mesh` | Reordering the dynamic-state setup changed the result, meaning the implementation is sensitive to `vkCmdSet*` order when it should not be. |
| `state_persistence` | Dynamic state set before the first bind (rasterization, blend, depth/stencil, viewport, or scissor) was reset or lost when the second pipeline was bound. |
| `static_stencil_mask_zero` | The static zero stencil write mask suppressed the dynamic `0xFF` override, or a discarded fragment still wrote to color, depth, or stencil. |
| `double_static_bind` | The bad static viewport was not overridden by the dynamic viewport, or the bad dynamic scissor was applied despite scissor being static. |
| All leaves | Shared infrastructure: the base harness, render pass, vertex data, or reference frame is wrong. |

### Cause Analysis

#### Dynamic state change between draws not applied

**Possible failure symptoms:** For `state_switch` and `bind_order`, the reference two-quadrant pattern is wrong: one quadrant is black where it should be green, or the whole framebuffer is one color instead of two.

**Possible implementation causes:** The implementation may cache dynamic state per-draw and fail to pick up the second `vkCmdSetScissor`, or the command may be recorded but not propagated to the hardware scissor unit. The same symptom in `bind_order` implies sensitivity to the order of unrelated `vkCmdSet*` commands, which the Vulkan specification does not allow. Whether the defect is in command-buffer recording or in the hardware state-tracking path requires source-level investigation.

#### Dynamic state not persistent across pipeline bind

**Possible failure symptoms:** For `state_persistence`, the second draw renders incorrectly after the rebind: the blue quadrant is misplaced, mis-sized, or absent, or the rasterization, blend, or depth/stencil state set before the first bind is not applied to the second draw.

**Possible implementation causes:** `vkCmdBindPipeline` may incorrectly reset dynamic state that the specification requires to persist. The rasterization, blend, and depth/stencil state is set once before the first bind and never re-recorded, so any deviation in the second draw's result points at dynamic state lost or clobbered by the rebind. Pinning the failure to the pipeline-bind path requires checking the implementation's bind handling against the specification.

#### Static stencil write mask zero blocks dynamic override

**Possible failure symptoms:** For `static_stencil_mask_zero`, the color buffer is not the clear color (a discarded fragment wrote color), or the depth buffer is not the clear depth, or the stencil buffer is not zero.

**Possible implementation causes:** The fragment shader discards every fragment, so the Vulkan specification requires that no color, depth, or stencil writes occur. A stencil value other than zero suggests that the static zero write mask prevented the dynamic `0xFF` mask from taking effect, or that a discarded fragment still updated stencil. A color or depth mismatch suggests discard was not honored or early fragment tests ran before the discard. The comment in the source notes this combination has caused issues on some implementations, so an implementation that bakes the static mask into the pipeline and ignores the dynamic one is a known failure mode.

#### Double static bind does not let dynamic value win

**Possible failure symptoms:** For `double_static_bind`, the framebuffer is not entirely blue: the bad static viewport clipped the triangle, or the bad dynamic scissor was applied and cut the output.

**Possible implementation causes:** The test sets a good dynamic viewport after the second bind; if the static bad viewport is used instead, the implementation did not let the dynamic state override the static one. The bad dynamic scissor is recorded before the rebind and scissor is static in this pipeline, so if that scissor took effect the implementation applied a dynamic command for a non-dynamic state. Both behaviors contradict the Vulkan specification's rules on dynamic versus static state precedence.

## Case Pruning

### Requirement-based pruning

- The `_mesh` variants require `VK_EXT_mesh_shader` and are conditionally compiled out under `CTS_USES_VULKANSC` ([checkMeshShaderSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L455-L458)).
- `static_stencil_mask_zero` checks pipeline construction requirements and selects a supported depth/stencil format at runtime from `VK_FORMAT_D32_SFLOAT_S8_UINT` or `VK_FORMAT_D24_UNORM_S8_UINT` ([checkStaticStencilMaskZeroSupport](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L492-L498), [chooseDepthStencilFormat](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L501-L515)).
- `state_switch` and `bind_order` (vertex) require no additional features ([checkNothing](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L461-L463)).

### Design-based pruning

- `state_persistence` has no mesh variant by design: the test asserts `!m_isMesh` in its constructor because the property it checks does not apply to mesh pipelines ([assert](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L311)).
- `double_static_bind` is omitted for shader-object construction types because the test depends on `vkCmdBindPipeline` rebind semantics that do not exist for shader objects, which are set with `vkCmdSet*` / `vkCmdBindShadersEXT` instead ([guard](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L975)).
- `static_stencil_mask_zero` and `double_static_bind` are single test cases, not iterated over a parameter matrix; each probes one specific edge case.

## Key Takeaways

- The behavioral axis is the test case leaf. The switching and bind-order cases share a reference pattern and differ only in whether the dynamic-state setup is reordered; comparing the two isolates order-sensitivity from per-draw switching.
- `state_persistence` extends the same pattern across a pipeline rebind to verify that `vkCmdBindPipeline` does not reset dynamic state, using topology as the only difference between the two pipelines.
- `static_stencil_mask_zero` is an edge-case probe: a zero static mask plus a nonzero dynamic mask, combined with unconditional discard, is a combination that has broken implementations before.
- `double_static_bind` relies on the precedence of dynamic state over static state and on the non-application of a dynamic command for a static state. Its absence from shader-object construction types is a design consequence of the shader-object bind model, not a feature gap.
- The vertex and mesh variants of the switching and bind-order cases test the same property through different input-assembly paths; a divergence between them points at mesh-shader-specific state handling.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration | [`DynamicStateGeneralTests::init()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L927-L979) | Registers all leaves, the mesh-shader loop, and the `double_static_bind` shader-object guard. |
| State switch instance | [`StateSwitchTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L60-L172) | Two draws with different dynamic scissors; fuzzy comparison against two-quadrant reference. |
| Bind order instance | [`BindOrderTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L174-L294) | Same as state switch with reordered dynamic-state setup. |
| State persistence instance | [`StatePersistenceTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L296-L452) | Two pipelines, same dynamic state, verifies persistence across rebind. |
| Static stencil mask zero case | [`staticStencilMaskZeroProgramsTest()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L519-L792) | Zero static mask, dynamic `0xFF`, discard-all fragment shader, triple buffer comparison. |
| Double static bind case | [`doubleBindTest()`](../../../modules/vulkan/dynamic_state/vktDynamicStateGeneralTests.cpp#L824-L910) | Bad static viewport, double bind, dynamic override must win. |
| Shared base | [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) | Framebuffer, render pass, pipeline scaffold, and `setDynamic*State()` helpers. |
| Shaders (switch/bind/persistence) | [VertexFetch.vert](../../../data/vulkan/dynamic_state/VertexFetch.vert), [VertexFetch.frag](../../../data/vulkan/dynamic_state/VertexFetch.frag), [VertexFetch.mesh](../../../data/vulkan/dynamic_state/VertexFetch.mesh) | Pass-through vertex, fragment, and mesh shaders. |
