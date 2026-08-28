## Overview

**Core question:** Do indexed draws remain deterministic when the requested index lies outside the usable bound range?

- This page covers `robustness.index_access` and the non-VulkanSC `robustness.bind_index_buffer2` test families implemented and registered by [`vktRobustnessIndexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1-L1207).
- `index_access` puts `firstIndex` far beyond a six-index buffer and checks the zero-index behavior required by `robustBufferAccess2`.
- `bind_index_buffer2` varies the binding offset, explicit size, index value, and command form, then checks which indexed triangles appear.
- Both families observe correctness through a rendered color image rather than validation-layer output.

## Background Knowledge

For the shared model of indexed addressing and robustness contracts, see [Robustness Background Knowledge](../../categories/robustness.md#background-knowledge).

- **Indexed drawing:** the draw reads an index from the bound index buffer and uses it to select vertex data. The effective access depends on the draw's `firstIndex`, the stored index value, and the usable range of the index-buffer binding.
- **Robustness2:** `robustBufferAccess2` makes an out-of-bounds index fetch return zero. The resulting vertex selection gives the test a deterministic image result.
- **Sized index-buffer bindings:** `vkCmdBindIndexBuffer2` combines a binding offset with an explicit size. `VK_WHOLE_SIZE` instead extends the usable range from the binding offset to the end of the buffer.

## Registration Hierarchy

```text
robustness.index_access
├── draw_indexed_2
├── draw_indexed_2_device_address
├── draw_indexed_indirect_2
├── draw_indexed_indirect_2_device_address
├── draw_indexed_indirect_count_2
├── draw_indexed_indirect_count_2_device_address
└── draw_multi_indexed_2

robustness.bind_index_buffer2
├── offset_0
└── offset_100
```

`bind_index_buffer2` is added only outside `CTS_USES_VULKANSC`; its offset nodes expand into draw modes and `oo_*` test case leaves ([category registration](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L65-L94), [family registration](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1205)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `index_access`, `bind_index_buffer2` | Selects out-of-bounds `firstIndex` behavior or sized-binding behavior. | [registration](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1205) |
| Draw mode | `draw_indexed`, `draw_indexed_indirect`, `draw_indexed_indirect_count`, `draw_multi_indexed` | Exercises equivalent indexed access through different command paths. | [`TestMode` and mode arrays](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L61-L67) |
| Binding offset | `offset_0`, `offset_100` | Checks a binding at the buffer start and after leading index data. | [`offsets`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1132-L1140) |
| Out-of-range type | `oo_none`, `oo_index`, `oo_size`, `oo_whole_size` | Selects a valid baseline or the source of the unusable index access. | [`OutOfTypes`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1125-L1130) |
| Binding command | handle, `_device_address` | Compares classic binding/draw commands with device-address command variants where registered. | [variant generation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1153-L1164) |

## Behavior Parameters

The primary behavioral axis is the test family for `index_access`, and the `oo_*` test case leaf for `bind_index_buffer2`.

### `index_access` — out-of-bounds `firstIndex`

A six-point indexed draw uses a very large `firstIndex` (`UINT32_MAX - 100`). With robustness2, the invalid index-buffer fetch must yield index zero. Direct, indirect, indirect-count, multi-draw, and selected device-address commands all test that same requirement ([setup and command selection](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L165-L388)).

### `oo_none` — valid sized binding baseline

The selected binding range and index data are valid. The robustness-sensitive quadrant must therefore be drawn, establishing that the selected offset and command path work before an out-of-range condition is introduced.

### `oo_index` — index value outside available vertex data

The binding range remains usable, but an index value points beyond the intended vertex range. Robust handling must prevent that invalid fetch from producing the tested quadrant.

### `oo_size` — explicit binding size excludes the index

The index-buffer binding uses an explicit size that makes the selected index access fall outside the bound range. The implementation must honor this size rather than reading later buffer bytes.

### `oo_whole_size` — range derived from offset

The binding uses `VK_WHOLE_SIZE`, so the accessible range is derived from the binding offset and the buffer's end. This case checks that the derived range is applied correctly ([binding preparation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L831-L860)).

## Shader Analysis

The vertex shader is fixed across the `index_access` command variants, but it is the observation path for the tested index fetch: the fetched vertex attribute is copied directly to `gl_Position`, so zero substitution for an out-of-bounds index selects vertex zero's position in the framebuffer. The fragment shader only writes a constant color and does not implement the robustness condition.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.robustness.index_access.draw_indexed_2
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `index_access` | Selects the family that uses an out-of-bounds `firstIndex` with `robustBufferAccess2`. |
| `draw_indexed_2` | Uses the direct indexed-draw command path without the device-address variant. |
| Vertex shader | Shows the stage where the vertex position selected by the effective index becomes `gl_Position`. |

#### Purpose

The shader forwards the position produced by indexed vertex fetching without changing it. This lets the framebuffer expose whether the out-of-bounds index fetch selected vertex zero as required.

#### Structural Design

| Step | Shader-visible effect |
|------|-----------------------|
| Read `inPosition` | Receives the position associated with the effective fetched index. |
| Write `gl_Position` | Places the point at that position without transformation. |
| Write `gl_PointSize` | Produces a one-pixel point for deterministic image checking. |

#### Shader Code

```glsl
#version 450
/// The indexed vertex fetch supplies this position; an out-of-bounds index is expected to resolve to vertex index zero.
layout(location = 0) in vec4 inPosition;
void main(void)
{
    /// Forward the fetched position unchanged so framebuffer placement exposes the effective index value.
    gl_Position = inPosition;
    gl_PointSize = 1.0;
}
```

#### Additional Info

- The fixed fragment shader writes `vec4(0.2, 1.0, 0.5, 1.0)`; it supplies the expected image color but does not vary with the tested index access ([shader generation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L621-L641)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Draw mode | The vertex shader remains unchanged for direct, indirect, indirect-count, and multi-indexed command paths; only host-side command recording changes. | [`DrawIndexedTestCase::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L621-L641) |
| Binding command | Handle and `_device_address` variants use the same shader; the binding and draw command path changes outside the shader. | [variant generation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1153-L1164) |
| Test family | `bind_index_buffer2` uses the same position-forwarding structure but a separate fixed fragment color. | [`BindIndexBuffer2TestCase::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L740-L756) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 25
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPosition
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPosition "inPosition"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPosition Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
 %inPosition = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %inPosition
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %24 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %24 %float_1
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates deterministic vertex and index data, a color target, and any indirect command/count buffers required by the selected mode.
- `index_access` records a draw with the large `firstIndex`. Handle-based variants bind ordinary buffers; address variants use the device-address command path.
- After execution, the host reads the `16 x 16` color image. Robustness2 cases require exactly one expected-color fragment in the middle-top region ([image check](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L415-L461)).
- `bind_index_buffer2` populates leading index data for the selected offset, modifies index data or binding size for the selected `oo_*` leaf, and records the chosen draw mode.
- The host reads the `64 x 64` image and samples three representative locations. A required valid region must remain drawn. The robustness-sensitive region is drawn for `oo_none` and clear for every out-of-range type ([sampled verdict](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1080-L1113)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `index_access` | Out-of-bounds `firstIndex` handling did not produce the robustness2 zero-index result, or the selected command path used incorrect draw parameters. |
| `oo_none` | A valid sized binding failed to preserve the expected indexed draw. |
| `oo_index` | An out-of-range index value was not suppressed as required. |
| `oo_size` | The explicit binding size was not honored when determining the accessible index range. |
| `oo_whole_size` | `VK_WHOLE_SIZE` handling did not derive the usable range correctly from the binding offset. |

### Cause Analysis

#### Robust index-fetch behavior

**Possible failure symptoms:** `index_access` produces zero or multiple expected-color fragments, or an out-of-range `oo_*` case draws the quadrant that should remain clear.

**Possible implementation causes:** The indexed-fetch path may not apply `robustBufferAccess2` zero substitution, may use the wrong effective index-buffer range, or may apply robustness inconsistently across direct and indirect command paths.

#### Sized binding range calculation

**Possible failure symptoms:** `oo_size` or `oo_whole_size` differs from its expected clear/drawn pattern, especially only at `offset_100`.

**Possible implementation causes:** The accessible byte range may be computed without the binding offset, the explicit size may be ignored, or `VK_WHOLE_SIZE` may be interpreted as the full buffer rather than the remainder after the offset.

#### Command-path parameter handling

**Possible failure symptoms:** Only an indirect, indirect-count, multi-draw, or `_device_address` variant fails while the equivalent direct case passes.

**Possible implementation causes:** The selected command path may consume different first-index, draw-count, binding-address, or stride data than the host prepared. Source-level investigation is needed to distinguish command decoding from shared index-fetch behavior.

## Case Pruning

### Requirement-based pruning

- Indirect-count modes require `VK_KHR_draw_indirect_count`; multi-indexed modes require `VK_EXT_multi_draw`.
- Both test families require `VK_KHR_robustness2` or `VK_EXT_robustness2` and the `robustBufferAccess2` feature; `bind_index_buffer2` inherits this support check because its generated parameters retain robustness version 2.
- `_device_address` variants require `VK_KHR_device_address_commands` and its related features.
- `bind_index_buffer2` requires maintenance5 support through `DEPENDENT_MAINTENANCE_5_EXTENSION_NAME`.
- Portability-subset devices must expose `robustBufferAccess` ([support checks](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L492-L523)).

### Design-based pruning

- `bind_index_buffer2` is absent from Vulkan SC builds.
- `index_access` does not generate a device-address multi-draw leaf.
- `bind_index_buffer2` device-address variants are limited to `offset_100`, non-multi modes, and out-of-range types other than `oo_whole_size` ([generator restrictions](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1153-L1164)).

## Key Takeaways

- The tests turn invalid indexed accesses into deterministic framebuffer evidence.
- `index_access` isolates robustness2 handling of an extreme `firstIndex`; `bind_index_buffer2` isolates offset, size, and index-value range rules.
- Equivalent direct, indirect, multi-draw, and device-address variants expose command-path-specific regressions without changing the core expected result.

## Source Reference Appendix

- [`vktRobustnessIndexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1-L1207) — implementation and registration.
- [`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L165-L461) — `index_access` setup, command recording, and validation.
- [`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L787-L1113) — sized-binding setup, draws, and sampled validation.
- [`createCmdBindIndexBuffer2Tests()` and `createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1116-L1205) — registered matrix.
- [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99) — category registration and VulkanSC guard.
- [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L1-L41) and [`index_access` entries](../../../mustpass/main/vk-default/robustness.txt#L13746-L13752) — default mustpass evidence.
