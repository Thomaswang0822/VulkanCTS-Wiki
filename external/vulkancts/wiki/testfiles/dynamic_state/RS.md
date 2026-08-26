## Overview

**Core question:** Do dynamically set depth bias (constant factor and clamp) and line width values take effect and override static pipeline state, for both classic vertex pipelines and mesh shader pipelines?

- [vktDynamicStateRSTests.cpp](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1) implements the `rs_state` test family of the `dynamic_state` test category.
- It registers five behavior groups under `rs_state`: `depth_bias`, `depth_bias_clamp`, `line_width`, `nonzero_depth_bias_constant`, and `nonzero_depth_bias_clamp`. Each group has a `_mesh` sibling on non-VulkanSC builds that reruns the same logic through a mesh shader pipeline.
- The first three groups (`depth_bias`, `depth_bias_clamp`, `line_width`) drive `vkCmdSetDepthBias` and `vkCmdSetLineWidth` through the shared [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) / [`DepthBiasBaseCase`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L59) harness and validate with a fuzzy image comparison against a software reference frame. `depth_bias` and `depth_bias_clamp` extend `DepthBiasBaseCase` (a self-contained base in the RS file that adds a depth/stencil attachment); `line_width` extends `DynamicStateBaseClass` (color-only).
- The two `nonzero_depth_bias_*` groups use a self-contained [`DepthBiasNonZeroInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L848) that emits its own shaders, drives `vkCmdSetDepthBias` with large constant and clamp values, and validates with an exact float threshold comparison.
- The page explains what each group verifies, how the runtime and result checking work, and what a failure points to.

## Background Knowledge

- **Dynamic depth bias.** Depth bias shifts a fragment's depth value before the depth test, so that coplanar or decal geometry can win or lose the depth comparison predictably. Vulkan computes the bias as `dbclamp(m * depthBiasSlopeFactor + r * depthBiasConstantFactor)`, where `m` is the maximum depth slope of the primitive, `r` is the minimum resolvable difference for the depth attachment format, and `dbclamp` clamps the result to `depthBiasClamp` when that clamp is nonzero (see [primsrast.adoc](https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html#primsrast-depthbias) in the Vulkan spec). When `VK_DYNAMIC_STATE_DEPTH_BIAS` is set, `vkCmdSetDepthBias` supplies the constant factor, clamp, and slope factor at record time and overrides the static pipeline values.
- **Dynamic line width.** `VK_DYNAMIC_STATE_LINE_WIDTH` makes `vkCmdSetLineWidth` control the rasterized width of line primitives instead of the pipeline's static `lineWidth`. Wide lines beyond `1.0f` require the `DEVICE_CORE_FEATURE_WIDE_LINES` feature and are bounded by `limits.lineWidthRange[1]`.
- **Minimum resolvable difference `r`.** For a fixed-point depth attachment such as `VK_FORMAT_D16_UNORM`, `r` is implementation-dependent but must be at most `2 × 2^(-N)` for N depth bits, per the Vulkan spec. The nonzero tests use a large `depthBiasConstantFactor` so that `r * constantFactor` produces a measurable depth shift even though `r` is tiny.
- **Pipeline construction type subgroup.** Every behavior group below is registered as a direct child of one of the construction-type subgroups (`monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_unlinked_spirv`, `shader_object_unlinked_binary`, `shader_object_linked_spirv`, `shader_object_linked_binary`) created by the registration-only dispatcher. The construction type is passed in from the parent and is not a behavioral axis of this page.

## Registration Hierarchy

```text
dynamic_state.monolithic.rs_state
├── depth_bias
├── depth_bias_clamp
├── line_width
├── nonzero_depth_bias_constant
└── nonzero_depth_bias_clamp
```

Each leaf above also has a `_mesh` sibling on non-VulkanSC builds, registered in the same [`init()` loop](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1276-L1339). The mesh variants are siblings of their classic counterparts, not nested under them. The same `rs_state` subtree appears under every construction-type subgroup. The registration root shown here is the full category-qualified path for the `monolithic` subgroup; replace `monolithic` with the other subgroup names for the parallel subtrees.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Shader type | classic vertex, mesh | Runs the same rasterization logic through a vertex+fragment pipeline and a mesh+fragment pipeline. The mesh variant requires `VK_EXT_mesh_shader` and is excluded on VulkanSC. | [init() loop](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1276-L1294) |
| Depth bias constant factor | `0.0f`, `-1.0f`, `1000.0f`, `16384.0f` | The constant term multiplied by `r` in the bias formula. `depth_bias` flips it between draws; `depth_bias_clamp` pairs a large constant with a small clamp; the nonzero cases use `16384.0f` to make the `r * constant` shift measurable on a 16-bit depth buffer. | [DepthBiasParamTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L533-L537), [DepthBiasClampParamTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L637-L641), [nonzero params](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1310-L1338) |
| Depth bias clamp | `0.0f`, `0.005f`, `0.125f` | The clamp applied to the computed bias. `0.005f` caps a large constant in `depth_bias_clamp`; `0.125f` caps the shift in `nonzero_depth_bias_clamp`. A nonzero clamp requires the `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP` feature. | [DepthBiasClampParamTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L637), [nonzero params](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1325-L1338) |
| Line width | `floor(limits.lineWidthRange[1])` | The device's maximum supported line width, queried at runtime and set via `vkCmdSetLineWidth`. Requires `DEVICE_CORE_FEATURE_WIDE_LINES`. | [LineWidthParamTestInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L738) |
| Depth attachment format | `VK_FORMAT_D16_UNORM` (nonzero cases), runtime-selected `VK_FORMAT_D24_UNORM_S8_UINT` or `VK_FORMAT_D32_SFLOAT_S8_UINT` (others) | The nonzero cases pin a 16-bit depth format so the `r * constantFactor` shift is bounded; the `DepthBiasBaseCase` cases pick the first supported packed depth/stencil format. | [DepthBiasNonZeroInstance::iterate](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L982), [format selection in DepthBiasBaseCase](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L132-L151) |
| Render dimensions | 128x128 (base-class cases), 8x8 (nonzero cases) | The base-class cases use a full 128x128 framebuffer; the nonzero cases use a small 8x8 framebuffer because the fragment shader only emits color where the biased depth lands in a narrow window. | [WIDTH/HEIGHT](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L83-L86), [nonzero extent](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L986) |

## Behavior Parameters

The primary behavioral axis is the behavior group: each group of test case leaves tests a distinct dynamic rasterization property. The mesh variants repeat the same logic through a different pipeline and do not form a separate axis.

### depth_bias: Dynamic depth bias constant factor

Draws three full-screen quads at depth `0.5f` through a pipeline with depth test enabled (`VK_COMPARE_OP_GREATER_OR_EQUAL`, depth write enabled) and depth bias enabled. The first two draws use `vkCmdSetDepthBias` with constant factor `0.0f` (blue then green quads at depth `0.5f` and `1.0f`); because the green quad is at greater depth it passes and the center region becomes green. The third draw sets constant factor `-1.0f` and draws the red quad at depth `0.5f`; the negative bias shifts its effective depth down so it fails the `GREATER_OR_EQUAL` test against the stored green depth and does not overwrite the center. The reference frame expects green in the center and blue elsewhere. See [`DepthBiasParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L465).

### depth_bias_clamp: Dynamic depth bias clamp

Draws a blue full-screen quad at depth `0.0f` with `vkCmdSetDepthBias` constant factor `1000.0f` and clamp `0.005f`. Without the clamp, the huge constant factor would push the effective depth above the green quad's `0.01f`; with the clamp, the bias is capped at `0.005f`, so the blue quad's effective depth stays at `0.005f` and fails the `GREATER_OR_EQUAL` test against the green quad drawn next at depth `0.01f`. The reference frame expects the green center region to remain visible. See [`DepthBiasClampParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L591). Requires the `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP` feature.

### line_width: Dynamic line width

Draws a single horizontal green line (two vertices, `VK_PRIMITIVE_TOPOLOGY_LINE_LIST`) and sets `vkCmdSetLineWidth` to `floor(limits.lineWidthRange[1])`, the device's maximum supported width. The reference frame paints a horizontal band whose half-height equals `floor(lineWidthRange[1]) / frameHeight`, matching the widened rasterized line. See [`LineWidthParamTestInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L707). Requires the `DEVICE_CORE_FEATURE_WIDE_LINES` feature.

### nonzero_depth_bias_constant: Nonzero depth bias constant is actually applied

Uses [`DepthBiasNonZeroInstance`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L848) with a full-screen triangle at `geometryDepth = 0.375f`, a `VK_FORMAT_D16_UNORM` depth attachment, depth test `ALWAYS`, depth bias enabled, and `vkCmdSetDepthBias` constant factor `16384.0f` with clamp `0.0f`. The fragment shader only writes green where the post-bias depth falls in `[0.5f, 1.0f]` (passed in via push constants). On a 16-bit depth buffer the minimum resolvable difference `r` is implementation-dependent but at most `2 / 2^16`, so the applied bias `16384 * r` is at most `0.5`, giving a final depth no higher than `0.875f` — which still lands inside the `[0.5f, 1.0f]` window. If the constant factor were ignored, the depth would stay at `0.375f` and the fragment shader would emit nothing, leaving the cleared color buffer. Passing requires every pixel to be exactly green `(0, 1, 0, 1)`. See [params](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1310-L1323).

### nonzero_depth_bias_clamp: Nonzero depth bias clamp is actually applied

Same harness as the constant case, but with `depthBiasClamp = 0.125f` and a narrower acceptance window of `[0.46875f, 0.53125f]`. Without the clamp, the bias `16384 * r` would be large enough to push the final depth well past `0.53125f` (the spec bound gives at most `0.875f`); with the clamp the bias is capped at `0.125f`, giving a final depth of `0.5f` which lands inside the window. If the clamp were ignored the fragment shader would emit nothing. Passing requires every pixel to be exactly green `(0, 1, 0, 1)`. Requires the `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP` feature. See [params](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1324-L1338).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.dynamic_state.monolithic.rs_state.nonzero_depth_bias_constant
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `nonzero_depth_bias_constant` | Selects the nonzero-depth-bias oracle that checks whether a dynamic constant factor moves rasterized depth into a fragment acceptance window. |
| `depthBiasConstant = 16384.0f`, `depthBiasClamp = 0.0f` | Uses a large unclamped constant factor while keeping the clamp disabled, isolating the dynamic constant-factor path. |
| `geometryDepth = 0.375f`, `minDepth = 0.5f`, `maxDepth = 1.0f` | Places the triangle initially below the acceptance window; green output therefore requires the post-rasterization depth bias to be applied. |
| Classic `vert` + `frag` stages | Uses the exact recommended classic representative; the companion vertex shader supplies a full-screen triangle and the fragment shader is the validation payload. |

#### Purpose

This shader makes dynamic depth-bias application observable: it writes green only when the depth produced by rasterization, including dynamic bias, lies in the push-constant window. The host then requires every pixel of the 8x8 color image to equal green.

#### Structural Design

| Phase | Shader operation | Test meaning |
|-------|------------------|--------------|
| Interface | Read `minDepth` and `maxDepth` from a push-constant block; expose color output at location 0. | The host supplies the acceptance window and the shader supplies the pass/fail color. |
| Observation | Read `gl_FragCoord.z` into `depth`. | Observes the depth after rasterization and dynamic depth bias. |
| Predicate | Require `depth >= pc.minDepth && depth <= pc.maxDepth`. | Separates a correctly biased depth from the original `geometryDepth`. |
| Verdict | Store green `(0, 1, 0, 1)` when the predicate is true; otherwise perform no color store. | A uniformly green readback is the exact host oracle. |

#### Shader Code

```glsl
#version 450

layout (push_constant, std430) uniform PushConstantBlock {
    float geometryDepth;
    float minDepth;
    float maxDepth;
} pc;

layout (location=0) out vec4 outColor;

void main() {
    const float depth = gl_FragCoord.z;
    if (depth >= pc.minDepth && depth <= pc.maxDepth) {
        outColor = vec4(0.0, 1.0, 0.0, 1.0);
    }
}
```

#### Additional Info

- The companion classic vertex shader generated by the same `DepthBiasNonZeroCase::initPrograms` call emits `gl_Position = vec4(positions[gl_VertexIndex], pc.geometryDepth, 1.0)`, using `(-1,-1)`, `(3,-1)`, and `(-1,3)` to cover the 8x8 framebuffer. The mesh variant replaces it with a mesh stage but keeps the same push-constant geometry depth and fragment oracle; it is a sibling case, not a separate behavioral parameter.
- `DepthBiasNonZeroInstance::iterate` marks only `VK_DYNAMIC_STATE_DEPTH_BIAS` dynamic, records `cmdSetDepthBias` with the selected constant and clamp, and uses depth test `VK_COMPARE_OP_ALWAYS` with depth writes enabled. The color readback is checked with zero threshold, so the expected green must match exactly.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| `depthBiasConstant` | The fragment shader is unchanged, but the host-selected constant controls whether `gl_FragCoord.z` reaches the `[minDepth, maxDepth]` predicate window. The registered nonzero cases use `16384.0f`. | [`DepthBiasNonZeroCase::initPrograms`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L892-L970); [registered parameters](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1310-L1323) |
| `depthBiasClamp` | The fragment shader is unchanged; the clamp changes the biased depth observed by `gl_FragCoord.z`. The sibling clamp case uses `0.125f` and narrows the window to `[0.46875f, 0.53125f]`. | [clamp parameters](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1324-L1338); [`cmdSetDepthBias`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1187-L1192) |
| `useMeshShaders` | The fragment shader and push-constant interface remain the same; only the geometry-producing stage changes from `vert` to `mesh`, with mesh support required. | [mesh/classic generator branch](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L892-L947); [support check](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L880-L889) |

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
; Bound: 43
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %depth "depth"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %PushConstantBlock "PushConstantBlock"
               OpMemberName %PushConstantBlock 0 "geometryDepth"
               OpMemberName %PushConstantBlock 1 "minDepth"
               OpMemberName %PushConstantBlock 2 "maxDepth"
               OpName %pc "pc"
               OpName %outColor "outColor"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %PushConstantBlock Block
               OpMemberDecorate %PushConstantBlock 0 Offset 0
               OpMemberDecorate %PushConstantBlock 1 Offset 4
               OpMemberDecorate %PushConstantBlock 2 Offset 8
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_ptr_Input_float = OpTypePointer Input %float
       %bool = OpTypeBool
%PushConstantBlock = OpTypeStruct %float %float %float
%_ptr_PushConstant_PushConstantBlock = OpTypePointer PushConstant %PushConstantBlock
         %pc = OpVariable %_ptr_PushConstant_PushConstantBlock PushConstant
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
%_ptr_PushConstant_float = OpTypePointer PushConstant %float
      %int_2 = OpConstant %int 2
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %42 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %depth = OpVariable %_ptr_Function_float Function
         %15 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_2
         %16 = OpLoad %float %15
               OpStore %depth %16
         %18 = OpLoad %float %depth
         %25 = OpAccessChain %_ptr_PushConstant_float %pc %int_1
         %26 = OpLoad %float %25
         %27 = OpFOrdGreaterThanEqual %bool %18 %26
               OpSelectionMerge %29 None
               OpBranchConditional %27 %28 %29
         %28 = OpLabel
         %30 = OpLoad %float %depth
         %32 = OpAccessChain %_ptr_PushConstant_float %pc %int_2
         %33 = OpLoad %float %32
         %34 = OpFOrdLessThanEqual %bool %30 %33
               OpBranch %29
         %29 = OpLabel
         %35 = OpPhi %bool %27 %5 %34 %28
               OpSelectionMerge %37 None
               OpBranchConditional %35 %36 %37
         %36 = OpLabel
               OpStore %outColor %42
               OpBranch %37
         %37 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

The depth/stencil base-class cases (`depth_bias`, `depth_bias_clamp`) follow the [`DepthBiasBaseCase`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L59) flow, which extends `TestInstance` directly and sets up a color-plus-depth/stencil framebuffer:

- The host selects a depth/stencil attachment format at runtime, preferring `VK_FORMAT_D24_UNORM_S8_UINT` and falling back to `VK_FORMAT_D32_SFLOAT_S8_UINT` based on `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` support.
- The host creates a color attachment (`VK_FORMAT_R8G8B8A8_UNORM`) and a depth/stencil image, builds a graphics pipeline with depth bias enabled and `VK_DYNAMIC_STATE_DEPTH_BIAS` marked dynamic.
- Inside the render pass, the test records the dynamic rasterization commands between draws: `setDynamicRasterizationState(lineWidth, depthBiasConstantFactor, depthBiasClamp)` issues `vkCmdSetLineWidth` and `vkCmdSetDepthBias`.
- After submission, the host reads back the color attachment and builds a software reference frame encoding the expected color pattern.
- Pass/fail is decided by `tcu::fuzzyCompare()` with threshold `0.05f` comparing the rendered frame against the reference ([depth_bias](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L580), [depth_bias_clamp](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L696)).

The `line_width` case extends [`DynamicStateBaseClass`](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) (color-only, no depth attachment) and uses the same `setDynamicRasterizationState` / `tcu::fuzzyCompare()` pattern ([line_width](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L799)).

The nonzero cases follow a self-contained flow in [`DepthBiasNonZeroInstance::iterate`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L972-L1222):

- The host creates an 8x8 color image (`VK_FORMAT_R8G8B8A8_UNORM`) and a 16-bit depth image (`VK_FORMAT_D16_UNORM`), a render pass with clear load op and `TRANSFER_SRC_OPTIMAL` final layout, and a pipeline with depth test `ALWAYS`, depth write enabled, depth bias enabled, and only `VK_DYNAMIC_STATE_DEPTH_BIAS` marked dynamic.
- The static pipeline depth bias values are all `0.0f`; the real constant factor and clamp come from `vkd.cmdSetDepthBias(cmdBuffer, m_params.depthBiasConstant, m_params.depthBiasClamp, 0.0f)`.
- Push constants carry `geometryDepth`, `minDepth`, and `maxDepth` to both the vertex/mesh and fragment stages.
- After one draw (or one `cmdDrawMeshTasksEXT` for the mesh variant), the host reads back the color buffer and compares every pixel against the expected green `(0, 1, 0, 1)` with `tcu::floatThresholdCompare()` at threshold `0.0f` (exact match).

| Resource | Created/configured by host | Bound to GPU | Device access | Host readback | Role |
|----------|-----------------------------|--------------|---------------|---------------|------|
| Color attachment image | Yes | Color attachment | Written by fragment output | Yes, via `readSurface` | Captures the rendered result for comparison. |
| Depth/stencil image | Yes | Depth/stencil attachment | Read/written by depth test and depth bias | No (inferred from color) | Holds depth values shifted by the dynamic bias. |
| Vertex buffer / mesh descriptor | Yes | Vertex buffer or storage buffer | Read by vertex or mesh shader | No | Provides geometry positions and colors. |
| Push constants (nonzero cases) | Yes | Push constant range | Read by vertex/mesh and fragment shaders | No | Carries geometry depth and the acceptance window. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `depth_bias` / `depth_bias_mesh` | Dynamic depth bias constant factor not applied or not changed between draws. |
| `depth_bias_clamp` / `depth_bias_clamp_mesh` | Dynamic depth bias clamp not applied, so a large constant factor is not capped. |
| `line_width` / `line_width_mesh` | Dynamic line width not applied; line rasterizes at width `1.0f` instead of the set value. |
| `nonzero_depth_bias_constant` / `nonzero_depth_bias_constant_mesh` | Dynamic depth bias constant factor ignored, so the fragment depth never reaches the acceptance window. |
| `nonzero_depth_bias_clamp` / `nonzero_depth_bias_clamp_mesh` | Dynamic depth bias clamp ignored, so the bias is not capped and the fragment depth overshoots the narrow acceptance window. |

### Cause Analysis

#### Dynamic depth bias constant factor not applied or not changed between draws

**Possible failure symptoms:** The fuzzy image comparison fails for `depth_bias`. The red quad overwrites the green center (bias not applied at all, so red at depth `0.5f` ties the stored green depth and passes `GREATER_OR_EQUAL`), or the center is not green after the second draw (bias applied with the wrong sign or magnitude).

**Possible implementation causes:** The pipeline enables depth bias but the implementation ignores the constant factor set by `vkCmdSetDepthBias`, applies the static pipeline value instead of the dynamic one, or does not update the dynamic depth bias state between two draws recorded in the same command buffer. A depth-compare or depth-write defect in the `GREATER_OR_EQUAL` path could mimic a bias defect, so source-level investigation is needed to separate a bias bug from a depth-test bug.

#### Dynamic depth bias clamp not applied, so a large constant factor is not capped

**Possible failure symptoms:** The fuzzy image comparison fails for `depth_bias_clamp`. The blue quad overwrites the green center because the effective depth was pushed above `0.01f` by the unclamped `1000.0f` constant factor.

**Possible implementation causes:** The `depthBiasClamp` argument to `vkCmdSetDepthBias` is ignored, so the implementation computes the bias without applying the `dbclamp` rule from the spec. The `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP` feature gate is checked at support time, so a clamp that silently does nothing points to driver handling of the clamp operand rather than a missing feature.

#### Dynamic line width not applied

**Possible failure symptoms:** The fuzzy image comparison fails for `line_width`. The rendered green band is one pixel thick instead of `floor(lineWidthRange[1])` pixels, meaning the line rasterized at width `1.0f`.

**Possible implementation causes:** The implementation uses the static pipeline `lineWidth` instead of the value set by `vkCmdSetLineWidth`, or wide-line rasterization is not exercised even though the feature is reported. Because the reference frame's band width is derived from the same queried `lineWidthRange[1]`, a mismatch between the queried limit and the actually rasterized width would also fail.

#### Dynamic depth bias constant factor ignored (nonzero case)

**Possible failure symptoms:** The exact-threshold comparison fails for `nonzero_depth_bias_constant`. The color buffer is not uniformly green `(0, 1, 0, 1)`; typically it stays at the cleared value because the fragment shader's depth window `[0.5f, 1.0f]` is never entered.

**Possible implementation causes:** The `16384.0f` constant factor passed to `vkCmdSetDepthBias` is dropped or overridden, so the fragment depth stays at `geometryDepth = 0.375f` and the acceptance window is missed. Because the test pins `VK_FORMAT_D16_UNORM` and the acceptance window is computed from the bias range `16384 * r`, the window is wide enough to pass on any conformant `r`, so a failure here points to the constant factor not being applied rather than to a specific `r` value.

#### Dynamic depth bias clamp ignored (nonzero case)

**Possible failure symptoms:** The exact-threshold comparison fails for `nonzero_depth_bias_clamp`. The color buffer is not uniformly green because the unclamped bias pushes the fragment depth past `0.53125f`, outside the narrow `[0.46875f, 0.53125f]` window.

**Possible implementation causes:** The `0.125f` clamp is not applied, so the `dbclamp` rule from the spec is bypassed and the full `16384 * r` bias takes effect. As with the constant case, any conformant `r` would make the unclamped bias overshoot the narrow window, so a failure points to the clamp not being applied.

## Case Pruning

### Requirement-based pruning

- `depth_bias_clamp` and `nonzero_depth_bias_clamp` (classic and mesh) require the `DEVICE_CORE_FEATURE_DEPTH_BIAS_CLAMP` core feature, checked by [`checkDepthBiasClampSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1224-L1227) for the base-class case and by [`DepthBiasNonZeroCase::checkSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L880-L890) for the nonzero case.
- `line_width` (classic and mesh) requires the `DEVICE_CORE_FEATURE_WIDE_LINES` core feature, checked by [`checkWideLinesSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1229-L1232).
- All `_mesh` variants require `VK_EXT_mesh_shader`, checked by [`checkMeshShaderSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1234-L1237). On VulkanSC builds the mesh variants are compile-time excluded by `#ifndef CTS_USES_VULKANSC`.
- The combined mesh-plus-feature checks use [`checkMeshAndBiasClampSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1239-L1243) and [`checkMeshAndWideLinesSupport`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1245-L1249).
- Every nonzero case also checks pipeline construction requirements through [`checkPipelineConstructionRequirements`](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L888-L889).
- If no supported depth/stencil attachment format is found for a base-class case, the case throws `NotSupportedError`.

### Design-based pruning

- There is no generated matrix of bias or line-width values. Each behavior group uses a small hand-chosen set of values that produces a deterministic pass/fail outcome tied to the dynamic state.
- The two nonzero cases deliberately pair a constant-only and a constant-plus-clamp scenario on the same harness, so that a constant-factor bug and a clamp bug produce distinguishable failures.
- The nonzero cases pin `VK_FORMAT_D16_UNORM` rather than the runtime-selected packed format used by the `DepthBiasBaseCase` cases, because the bounded `r` of a fixed 16-bit depth format lets the acceptance windows be chosen to accommodate any conformant `r`.

## Key Takeaways

- The `rs_state` test family verifies that dynamic depth bias and line width override static pipeline state, using fuzzy image comparison for the visual cases and exact float comparison for the nonzero cases.
- `depth_bias` flips the constant factor between draws; `depth_bias_clamp` pairs a large constant with a small clamp so the clamp is the only thing preventing an overwrite.
- `line_width` rasterizes a line at the device's reported maximum width and checks the band thickness against a reference frame derived from the same limit.
- The two `nonzero_depth_bias_*` cases turn the color buffer into a direct oracle for whether the constant factor and clamp were applied, by gating fragment output on a narrow post-bias depth window computed from the 16-bit `r`.
- See `## Failure Meaning` for what a failing result implies for each behavior group.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family registration | [vktDynamicStateRSTests.cpp#L1269-L1340](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1269-L1340) | The `DynamicStateRSTests::init()` loop registers all behavior groups and their mesh variants. |
| DepthBiasParamTestInstance | [vktDynamicStateRSTests.cpp#L465-L589](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L465-L589) | Implements `depth_bias` and `depth_bias_mesh`. |
| DepthBiasClampParamTestInstance | [vktDynamicStateRSTests.cpp#L591-L705](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L591-L705) | Implements `depth_bias_clamp` and `depth_bias_clamp_mesh`. |
| LineWidthParamTestInstance | [vktDynamicStateRSTests.cpp#L707-L808](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L707-L808) | Implements `line_width` and `line_width_mesh`. |
| DepthBiasNonZeroCase | [vktDynamicStateRSTests.cpp#L827-L871](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L827-L871) | Case class for the two nonzero groups; owns params, support checks, and shader generation. |
| DepthBiasNonZeroCase::initPrograms | [vktDynamicStateRSTests.cpp#L892-L970](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L892-L970) | Emits the vertex/mesh and fragment shaders that gate color output on the post-bias depth window. |
| DepthBiasNonZeroInstance::iterate | [vktDynamicStateRSTests.cpp#L972-L1222](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L972-L1222) | Self-contained runtime: resources, pipeline, draw, and exact-threshold result check. |
| Nonzero params | [vktDynamicStateRSTests.cpp#L1310-L1338](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1310-L1338) | The hand-chosen constant, clamp, geometry depth, and acceptance window values for both nonzero cases. |
| Support checks | [vktDynamicStateRSTests.cpp#L1224-L1249](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L1224-L1249) | Depth bias clamp, wide lines, mesh shader, and combined feature checks. |
| DepthBiasBaseCase (depth_bias, depth_bias_clamp) | [vktDynamicStateRSTests.cpp#L59](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L59) | Self-contained base class extending `TestInstance` directly; owns the color-plus-depth/stencil framebuffer, format selection, and its own `setDynamicRasterizationState` ([L424-L429](../../../modules/vulkan/dynamic_state/vktDynamicStateRSTests.cpp#L424-L429)). |
| DynamicStateBaseClass (line_width) | [vktDynamicStateBaseClass.hpp#L43](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.hpp#L43) | Color-only base class; provides `setDynamicRasterizationState` ([vktDynamicStateBaseClass.cpp#L334-L339](../../../modules/vulkan/dynamic_state/vktDynamicStateBaseClass.cpp#L334-L339)) issuing `vkCmdSetLineWidth` and `vkCmdSetDepthBias`. |
| Passthrough shaders | [VertexFetch.vert](../../../data/vulkan/dynamic_state/VertexFetch.vert), [VertexFetch.frag](../../../data/vulkan/dynamic_state/VertexFetch.frag), [VertexFetch.mesh](../../../data/vulkan/dynamic_state/VertexFetch.mesh), [VertexFetchLines.mesh](../../../data/vulkan/dynamic_state/VertexFetchLines.mesh) | Shared passthrough shaders for the three base-class groups. |
| Mustpass entries | [dynamic-state.txt (vk-default)](../../../mustpass/main/vk-default/dynamic-state.txt#L231-L240) | The `monolithic.rs_state.*` entries; sibling entries exist under each construction-type subgroup. |
