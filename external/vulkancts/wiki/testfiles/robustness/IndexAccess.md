## Overview

**Core question:** Do indexed draws remain deterministic when the requested index lies outside the usable bound range, including when that range ends on a byte offset that is not a multiple of four?

- This page covers `robustness.index_access` and the non-VulkanSC `robustness.bind_index_buffer2` test families implemented and registered by [`vktRobustnessIndexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1-L1425).
- `index_access` draws from a seven-index buffer with `firstIndex` outside the bound range — far beyond the end for `uint32`, exactly one index past the end for `uint8` and `uint16` — and checks the zero-index behavior required by `robustBufferAccess2`.
- `bind_index_buffer2` varies the binding offset, explicit size, index element width, stored index value, and command form, then checks which indexed triangles appear.
- Both families observe correctness through a rendered color image rather than validation-layer output.

## Background Knowledge

For the shared model of indexed addressing and robustness contracts, see [Robustness Background Knowledge](../../categories/robustness.md#background-knowledge).

- **Indexed drawing:** the draw reads an index from the bound index buffer and uses it to select vertex data. The effective access depends on the draw's `firstIndex`, the stored index value, and the usable range of the index-buffer binding.
- **Robustness2:** `robustBufferAccess2` makes an out-of-bounds index fetch return zero. The resulting vertex selection gives the test a deterministic image result.
- **Sized index-buffer bindings:** `vkCmdBindIndexBuffer2` combines a binding offset with an explicit size. `VK_WHOLE_SIZE` instead extends the usable range from the binding offset to the end of the buffer.
- **Index element widths:** `VK_INDEX_TYPE_UINT32`, `VK_INDEX_TYPE_UINT16`, and `VK_INDEX_TYPE_UINT8` store one index in 4, 2, and 1 bytes, and the 8-bit type requires `indexTypeUint8`. A binding offset and binding size are byte quantities, and a binding only has to begin on a multiple of the element size, so only the narrow element widths let the usable range start or end on a byte offset that is not a multiple of 4.

## Registration Hierarchy

```text
robustness.index_access
├── draw_indexed_2
├── draw_indexed_2_device_address
├── draw_indexed_2_uint16
├── draw_indexed_2_uint16_device_address
├── draw_indexed_2_uint8
├── draw_indexed_2_uint8_device_address
├── draw_indexed_indirect_2
├── draw_indexed_indirect_2_device_address
├── draw_indexed_indirect_2_uint16
├── draw_indexed_indirect_2_uint16_device_address
├── draw_indexed_indirect_2_uint8
├── draw_indexed_indirect_2_uint8_device_address
├── draw_indexed_indirect_count_2
├── draw_indexed_indirect_count_2_device_address
├── draw_indexed_indirect_count_2_uint16
├── draw_indexed_indirect_count_2_uint16_device_address
├── draw_indexed_indirect_count_2_uint8
├── draw_indexed_indirect_count_2_uint8_device_address
├── draw_indexed_indirect_count_pipeline_robustness_1_vert_frag
├── draw_indexed_indirect_count_pipeline_robustness_1_vert_geom_frag
├── draw_indexed_indirect_count_pipeline_robustness_1_vert_tess_frag
├── draw_indexed_indirect_count_pipeline_robustness_1_vert_tess_geom_frag
├── draw_indexed_indirect_count_pipeline_robustness_2_vert_frag
├── draw_indexed_indirect_count_pipeline_robustness_2_vert_geom_frag
├── draw_indexed_indirect_count_pipeline_robustness_2_vert_tess_frag
├── draw_indexed_indirect_count_pipeline_robustness_2_vert_tess_geom_frag
├── draw_indexed_indirect_pipeline_robustness_1_vert_frag
├── draw_indexed_indirect_pipeline_robustness_1_vert_geom_frag
├── draw_indexed_indirect_pipeline_robustness_1_vert_tess_frag
├── draw_indexed_indirect_pipeline_robustness_1_vert_tess_geom_frag
├── draw_indexed_indirect_pipeline_robustness_2_vert_frag
├── draw_indexed_indirect_pipeline_robustness_2_vert_geom_frag
├── draw_indexed_indirect_pipeline_robustness_2_vert_tess_frag
├── draw_indexed_indirect_pipeline_robustness_2_vert_tess_geom_frag
├── draw_indexed_pipeline_robustness_1_vert_frag
├── draw_indexed_pipeline_robustness_1_vert_geom_frag
├── draw_indexed_pipeline_robustness_1_vert_tess_frag
├── draw_indexed_pipeline_robustness_1_vert_tess_geom_frag
├── draw_indexed_pipeline_robustness_2_vert_frag
├── draw_indexed_pipeline_robustness_2_vert_geom_frag
├── draw_indexed_pipeline_robustness_2_vert_tess_frag
├── draw_indexed_pipeline_robustness_2_vert_tess_geom_frag
├── draw_multi_indexed_2
├── draw_multi_indexed_2_uint16
├── draw_multi_indexed_2_uint8
├── draw_multi_indexed_pipeline_robustness_1_vert_frag
├── draw_multi_indexed_pipeline_robustness_1_vert_geom_frag
├── draw_multi_indexed_pipeline_robustness_1_vert_tess_frag
├── draw_multi_indexed_pipeline_robustness_1_vert_tess_geom_frag
├── draw_multi_indexed_pipeline_robustness_2_vert_frag
├── draw_multi_indexed_pipeline_robustness_2_vert_geom_frag
├── draw_multi_indexed_pipeline_robustness_2_vert_tess_frag
└── draw_multi_indexed_pipeline_robustness_2_vert_tess_geom_frag

robustness.bind_index_buffer2
├── offset_0
├── offset_100
└── type
```

`bind_index_buffer2` is added only outside `CTS_USES_VULKANSC`. Its `offset_*` nodes expand into draw modes and `oo_*` test case leaves, while `type` holds test case leaves that pair each draw mode with a `uint8` or `uint16` index width ([category registration](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L91-L96), [family registration](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1264-L1423)).

## Parameter Dimensions and Observed Values

The `uint8`/`uint16` and pipeline-robustness leaves of `robustness.index_access` are direct test cases; they vary the index element width, indirect/count draw form, device-address path, and selected vertex/geometry/tessellation/fragment pipeline stages, and are not descendants of another intermediate registration node. The `robustness.bind_index_buffer2.type` node has the same flat shape: its fourteen leaves name a draw mode and an index width, always with `oo_size` binding semantics.

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `index_access`, `bind_index_buffer2` | Selects out-of-bounds `firstIndex` behavior or sized-binding behavior. | [registration](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1264-L1423) |
| Draw mode | `draw_indexed`, `draw_indexed_indirect`, `draw_indexed_indirect_count`, `draw_multi_indexed` | Exercises equivalent indexed access through different command paths. | [`TestMode`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L51-L57), [`testModes`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L95-L100) |
| Binding offset | `offset_0`, `offset_100` | Checks a binding at the buffer start and after leading index data. | [`offsets`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1273-L1281) |
| Out-of-range type | `oo_none`, `oo_index`, `oo_size`, `oo_whole_size` | Selects a valid baseline or the source of the unusable index access; the `type` node fixes it to `oo_size`. | [`OutOfTypes`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1266-L1271) |
| Binding command | handle, `_device_address` | Compares classic binding/draw commands with device-address command variants where registered. | [variant generation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1295-L1306) |
| Index type | `uint8`, `uint16`, `uint32` | Exercises the core and extended index-buffer element widths; only the narrow widths let a bound range end on a byte offset that is not a multiple of 4. `uint8` requires `indexTypeUint8`. | [`typeCombinations`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L102-L103) |
| Starting index offset | one index element or none | Shifts the start of the binding by a single element. With a 1- or 2-byte index this moves the start, and with it the end, onto a byte offset that a 4-byte index could never produce. Chosen from draw-mode parity, so both the unaligned-start and the unaligned-end shape appear inside one node. | [binding-offset computation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L431-L432), [parity selection](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1320-L1330) |
| `firstIndex` | `0` for `bind_index_buffer2`; `UINT32_MAX - 100` for the `index_access` `uint32` leaves; `7` for the `index_access` `uint8`/`uint16` leaves | Decides whether the out-of-range fetch starts far beyond the buffer or at the first index after the bound range. | [registration of the two choices](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1361-L1384) |
| Pipeline robustness | Versions 1 and 2; vertex/fragment, geometry, tessellation, and combined stage paths | Applies pipeline robustness to the indexed draw and varies the stages used by the pipeline. | [pipeline-robustness registration](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1404-L1418) |

## Behavior Parameters

The primary behavioral axis is the test family for `index_access`, and the `oo_*` test case leaf for `bind_index_buffer2`.

### `index_access` — out-of-bounds `firstIndex`

A seven-index indexed draw starts at a `firstIndex` outside the bound range. With `robustBufferAccess2`, every invalid index fetch must yield index zero, so each of the seven points lands on vertex zero's position and the image keeps exactly one expected-color pixel. Direct, indirect, indirect-count, multi-draw, and selected device-address commands all test that same requirement ([index data](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L194-L232), [command recording](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L446-L521)).

Which `firstIndex` the leaves use depends on the index width. The `uint32` `_2` and `_2_device_address` leaves keep `UINT32_MAX - 100`, which is beyond any plausible bound computation. The `_uint8` and `_uint16` leaves instead start at `firstIndex = 7`, the first index after the seven bound ones, and take their one-element starting offset from draw-mode parity. Only that combination separates a correctly clipped access from one whose usable range was rounded up to a 4-byte boundary; the extreme value cannot, because rounding still leaves it far outside ([narrow-width registration](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1378-L1402)). The index values themselves are `0` through `6`, so the vertex buffer holds seven vertices and every in-range index addresses real vertex data.

### `oo_none` — valid sized binding baseline

The selected binding range and index data are valid. The robustness-sensitive quadrant must therefore be drawn, establishing that the selected offset and command path work before an out-of-range condition is introduced.

### `oo_index` — index value outside available vertex data

The binding range remains usable, but the last stored index value is replaced with 33, which is beyond the twelve vertices the draw can address; that value survives serialization at all three element widths. Robust handling must prevent that invalid fetch from producing the tested quadrant.

### `oo_size` — explicit binding size excludes the index

The index-buffer binding uses an explicit size of five elements while the draw still requests six, so the last index lies inside the buffer but outside the bound range. The implementation must honor this size rather than reading later buffer bytes. The `bind_index_buffer2.type` leaves fix this condition and vary only the index width, the starting index offset, and the command path, which turns that five-element size into a binding of 5 or 10 bytes whose start and end land on byte offsets that a 4-byte index element could never produce.

### `oo_whole_size` — range derived from offset

The binding uses `VK_WHOLE_SIZE`, so the accessible range is derived from the binding offset and the buffer's end, and here the buffer itself is made one index shorter than the draw needs. This case checks that the derived range is applied correctly ([binding preparation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L959-L991)).

## Shader Analysis

The vertex shader is fixed across the `index_access` command variants and index widths, but it is the observation path for the tested index fetch: the fetched vertex attribute is copied directly to `gl_Position`, so zero substitution for an out-of-bounds index selects vertex zero's position in the framebuffer. The fragment shader only writes a constant color and does not implement the robustness condition.

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

- The fixed fragment shader writes `vec4(0.2, 1.0, 0.5, 1.0)`; it supplies the expected image color but does not vary with the tested index access ([shader generation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L748-L767)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Draw mode | The vertex shader remains unchanged for direct, indirect, indirect-count, and multi-indexed command paths; only host-side command recording changes. | [`DrawIndexedTestCase::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L748-L801) |
| Index type | Unchanged; only the host-side index serialization and the byte offset of the binding change, so an out-of-range fetch must still resolve to vertex zero. | [index data per width](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L200-L216) |
| Binding command | Handle and `_device_address` variants use the same shader; the binding and draw command path changes outside the shader. | [variant generation](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1295-L1306) |
| Test family | `bind_index_buffer2` uses the same position-forwarding structure but a separate fixed fragment color. | [`BindIndexBuffer2TestCase::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L881-L897) |

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

- The host creates vertex data, index data serialized at the tested element width, a color target, and any indirect command/count buffers required by the selected mode.
- `index_access` shifts the index-buffer binding by one element when the leaf asks for it and records the draw with the selected `firstIndex`. Handle-based variants pass a byte offset to the bind command; address variants move the bound address forward by the same amount and shrink the address-range size to match.
- After execution, the host reads the `16 x 16` color image. Robustness2 cases require exactly one expected-color fragment in the middle-top region ([image check](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L547-L593)).
- `bind_index_buffer2` fills a logical index list, applies the selected `oo_*` modification, serializes it into the tested index width, and derives the binding offset, binding size, and buffer size from the element size before recording the chosen draw mode.
- The host reads the `64 x 64` image and samples three representative locations. A required valid region must remain drawn. The robustness-sensitive region is drawn for `oo_none` and clear for every out-of-range type ([sampled verdict](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1228-L1262)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `index_access` | Out-of-bounds `firstIndex` handling did not produce the `robustBufferAccess2` zero-index result, the usable index range was rounded wider than the binding, or the selected command path used incorrect draw parameters. |
| `oo_none` | A valid sized binding failed to preserve the expected indexed draw. |
| `oo_index` | An out-of-range index value was not suppressed as required. |
| `oo_size` | The explicit binding size was not honored when determining the accessible index range, or that size was derived for the wrong element width. |
| `oo_whole_size` | `VK_WHOLE_SIZE` handling did not derive the usable range correctly from the binding offset. |

### Cause Analysis

#### Robust index-fetch behavior

**Possible failure symptoms:** `index_access` produces zero or multiple expected-color fragments, or an out-of-range `oo_*` case draws the quadrant that should remain clear.

**Possible implementation causes:** The indexed-fetch path may not apply `robustBufferAccess2` zero substitution, may use the wrong effective index-buffer range, or may apply robustness inconsistently across direct and indirect command paths.

#### Index-width and range-alignment handling

**Possible failure symptoms:** A narrow-width leaf fails while the equivalent `uint32` case of the same condition passes — the `_2` sibling in `index_access`, the matching `oo_size` leaf in `bind_index_buffer2`. Inside `index_access` the failing leaves are the ones whose `firstIndex` sits one element past the binding rather than far beyond the buffer. The image then shows the expected-color fragment outside the middle-top region, an extra fragment, or a wrongly drawn robustness-sensitive quadrant.

**Possible implementation causes:** The usable index range was computed in 4-byte units or rounded up to a 4-byte boundary, so a fetch that starts one or two bytes past the intended end is treated as in range and returns stored or padding bytes instead of zero. An element size that does not follow `indexType` shifts both ends of the usable range and produces the same picture, so telling the two apart needs driver-side investigation.

#### Sized binding range calculation

**Possible failure symptoms:** `oo_size` or `oo_whole_size` differs from its expected clear/drawn pattern, especially only at `offset_100` or only at one index width.

**Possible implementation causes:** The accessible byte range may be computed without the binding offset, the explicit size may be ignored, `VK_WHOLE_SIZE` may be interpreted as the full buffer rather than the remainder after the offset, or the offset and size may be computed for a 4-byte element regardless of the tested index width.

#### Command-path parameter handling

**Possible failure symptoms:** Only an indirect, indirect-count, multi-draw, or `_device_address` variant fails while the equivalent direct case passes.

**Possible implementation causes:** The selected command path may consume different first-index, draw-count, binding-address, or stride data than the host prepared. Source-level investigation is needed to distinguish command decoding from shared index-fetch behavior.

## Case Pruning

### Requirement-based pruning

- Indirect-count modes require `VK_KHR_draw_indirect_count`; multi-indexed modes require `VK_EXT_multi_draw`.
- Both test families require `VK_KHR_robustness2` or `VK_EXT_robustness2` and the `robustBufferAccess2` feature; `bind_index_buffer2` inherits this support check because its generated parameters retain robustness version 2.
- `_device_address` variants require `VK_KHR_device_address_commands` and its related features.
- `bind_index_buffer2` requires maintenance5 support through `DEPENDENT_MAINTENANCE_5_EXTENSION_NAME`.
- Every `uint8` leaf — in both families — requires the `indexTypeUint8` feature, which the test also enables on the device it creates.
- Portability-subset devices must expose `robustBufferAccess` ([support checks](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L620-L665)).

### Design-based pruning

- `bind_index_buffer2` is absent from Vulkan SC builds.
- `index_access` does not generate a device-address multi-draw leaf.
- `bind_index_buffer2` device-address variants are limited to `offset_100`, non-multi modes, and out-of-range types other than `oo_whole_size` ([generator restrictions](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1295-L1306)).
- The `type` node fixes the out-of-range type to `oo_size` and drops the device-address variant of `draw_multi_indexed`, so it registers fourteen leaves instead of the full mode × width × out-of-range-type matrix ([type-node generator](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1313-L1344)).
- The narrow-width `index_access` leaves give up the extreme `firstIndex` in favor of `firstIndex = 7`. An access far beyond the buffer stays out of range however the bound is rounded, so only a start right after the binding can reveal a usable range that was rounded up to the next 4 bytes.

## Key Takeaways

- The tests turn invalid indexed accesses into deterministic framebuffer evidence.
- `index_access` isolates `robustBufferAccess2` handling of an out-of-range `firstIndex`; `bind_index_buffer2` isolates offset, size, index-width, and index-value range rules.
- A narrow index width only becomes a real test when the out-of-range access sits immediately after the binding. The odd element count, the one-element binding offset, and `firstIndex = 7` together expose a usable range that was rounded up to 4 bytes.
- Equivalent direct, indirect, multi-draw, and device-address variants expose command-path-specific regressions without changing the core expected result.

## Source Reference Appendix

- [`vktRobustnessIndexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1-L1425) — implementation and registration.
- [`DrawIndexedInstance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L162-L594) — `index_access` setup, command recording, and validation.
- [`BindIndexBuffer2Instance::iterate()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L906-L1262) — sized-binding setup, draws, and sampled validation.
- [`getIndexSize()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L90-L93) — byte width of one index element, used by every offset, binding-size, and buffer-size computation.
- [`createCmdBindIndexBuffer2Tests()` and `createIndexAccessTests()`](../../../modules/vulkan/robustness/vktRobustnessIndexAccessTests.cpp#L1264-L1423) — registered matrix.
- [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L101) — category registration and VulkanSC guard.
- [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L1-L55) and [`index_access` entries](../../../mustpass/main/vk-default/robustness.txt#L13760-L13812) — default mustpass evidence.
