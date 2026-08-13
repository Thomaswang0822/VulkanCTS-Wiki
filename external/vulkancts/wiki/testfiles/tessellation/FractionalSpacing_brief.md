# Understanding Brief: `tessellation.fractional_spacing`

## One-Sentence Test Purpose

This test checks whether fractional-even and fractional-odd tessellation split a single isoline according to Vulkan's segment-count, length, symmetry, and cross-level consistency rules in both GLSL and HLSL shader paths.

## Background Knowledge

### Fractional tessellator spacing

A floating-point tessellation level `f` does not directly become a segment count. For fractional-even spacing, Vulkan clamps `f` to at least `2` and rounds upward to an even integer `n`. For fractional-odd spacing, Vulkan clamps `f` to `[1, maxTessellationGenerationLevel - 1]` and rounds upward to an odd `n`. See [`tessellation.adoc#tessellation-tessellator-spacing`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-tessellator-spacing).

When `n` is greater than one, the tessellator creates `n - 2` equal-length regular segments and two equal-length additional segments. The additional segments sit symmetrically on opposite sides of the edge. Their relative length decreases as `n - f` grows. Their exact location is implementation-dependent, but two edges with the same clamped `f` must place them identically.

Why it matters here:

- The verifier cannot compare captured coordinates with one fixed reference array because Vulkan leaves the additional segments' exact location implementation-dependent.
- The test instead checks the required structural properties within each line and the required consistency across many levels.

### Observing an isoline through tessellation coordinates

The control shader fixes the first outer level at `1.0`, which requests one isoline, and supplies the tested level as the second outer level, which controls subdivision along that line. The evaluation shader runs in point mode and records `gl_TessCoord.x` for every generated point. Sorting those values reconstructs the line's endpoints and segment lengths without rasterizing an image.

## One Concrete Example

Consider `dEQP-VK.tessellation.fractional_spacing.glsl_even` with an input level of `7.3`. Fractional-even spacing rounds upward to the next even final level, `8`, so the evaluation shader should run for `9` points. After sorting the captured `x` coordinates, the host expects endpoints `0.0` and `1.0`. The eight intervals may contain six regular segments and two shorter additional segments. The two additional segments must have equal lengths and symmetric indices.

This example is conceptual because Vulkan does not prescribe which symmetric pair receives the additional segments. The CTS derives their observed location from the captured coordinates and compares that location only where the specification requires consistency.

## End-to-End Test Flow

```text
[host] select shader language and fractional spacing mode
[host] generate 93 tessellation levels: 30 samples across [7,10) and 63 values from 0.3 through 62.3
[host] create one level buffer, one tessellation-coordinate result buffer, and one atomic counter buffer
[host] generate vertex, tessellation control, and tessellation evaluation programs
[host] for each level, upload outer level 1, clear result and counter storage, then draw one patch
[device] the control shader requests one isoline and writes the tested along-line level
[device] the tessellator generates point-mode positions using fractional-even or fractional-odd spacing
[device] each evaluation invocation atomically reserves a result slot and stores TessCoord.x
[host] wait, invalidate the result allocations, sort the captured coordinates, and check one-line rules
[host] after all levels pass, compare observed additional-segment lengths and locations across levels
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L427-L559) emits GLSL or HLSL vertex, tessellation control, and tessellation evaluation shaders.
- The GLSL evaluation layout selects `fractional_even_spacing` or `fractional_odd_spacing`; HLSL selects `fractional_even` or `fractional_odd` partitioning.
- A second evaluation-shader binary writes point size when `shaderTessellationAndGeometryPointSize` is enabled. This changes one output, not the captured spacing data.
- [`genTessLevelCases()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L392-L411) builds the fixed 93-level runtime sequence.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Tessellation-level buffer, binding 0 | yes | yes, storage buffer visible to the control stage | read by control shader | no | Supplies the current `outer1` level. |
| Tessellation-coordinate buffer, binding 1 | yes | yes, storage buffer visible to the evaluation stage | written by evaluation shader | yes | Stores every generated `TessCoord.x`. |
| Invocation counter, binding 2 | yes | yes, coherent storage buffer visible to the evaluation stage | atomically incremented by evaluation shader | yes | Reports the captured coordinate count and allocates result slots. |
| `gl_TessCoord` / `SV_DOMAINLOCATION` | no, shader built-in input | supplied by the tessellator | read by evaluation shader | no | Carries each generated point's normalized line coordinate. |
| Attachmentless render pass and framebuffer | yes | yes | used to execute the graphics pipeline | no | Runs tessellation without making rasterized pixels part of the result. |

## What Is Checked

For each of the 93 input levels, [`verifyFractionalSpacingSingle()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L153-L294) checks:

- captured point count equals final segment count plus one;
- sorted coordinates start at `0.0` and end at `1.0`;
- segment lengths form no more than two groups, with `0.001` used when grouping approximately equal lengths;
- an integral clamped level produces equal-length segments;
- when two additional segments can be identified, they are no longer than the regular segments and occupy symmetric indices.

After all levels pass, [`verifyFractionalSpacingMultiple()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L303-L390) checks:

- identical clamped levels use the same determinable additional-segment location;
- within one final rounded level, observed additional-segment length changes monotonically with `n - f`;
- identical clamped levels produce identical observed additional-segment lengths when the length is determinable.

## Behavior Parameter Identification

> **Behavior parameter:** spacing-mode behavioral group
>
> **Candidate values:** `*_even`, `*_odd`

The shader-language prefix, `glsl` or `hlsl`, selects a source and compiler path for the same spacing rules. The suffix selects different clamping and parity rules and therefore controls the tested tessellator behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `*_even` | Incorrect fractional-even level clamping or even rounding; wrong point count; invalid additional-segment lengths, symmetry, or cross-level consistency; or a failure in the selected GLSL/HLSL capture path. |
| `*_odd` | Incorrect fractional-odd level clamping or odd rounding, including the one-segment case; wrong point count; invalid additional-segment lengths, symmetry, or cross-level consistency; or a failure in the selected GLSL/HLSL capture path. |

## Important Variations and Special Cases

- `glsl_even` and `hlsl_even` exercise the same fractional-even behavior through different source languages. `glsl_odd` and `hlsl_odd` do the same for fractional-odd behavior.
- Levels below each mode's minimum expose its clamping rule. The sequence extends through `62.3`, producing final levels up to `64` for fractional-even and `63` for fractional-odd.
- The dense samples from `7.0` through `9.9` compare nearby levels within the same rounded parity band. The `i + 0.3` sequence covers low-level clamping and a wide set of transitions.
- A four-segment line can produce two length groups of two segments each. The verifier treats the shorter pair as the additional pair and records no location when both pairs have indistinguishable lengths.
- A negative recorded length means there is only one segment. A negative recorded location means the verifier could not identify the additional pair reliably. Cross-level checks skip those unknown observations.
- Portability-subset implementations must support isolines and point mode before these cases can run.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Fractional-spacing specification | [`tessellation.adoc#tessellation-tessellator-spacing`](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-tessellator-spacing) | Defines clamping, rounding, additional-segment, monotonicity, symmetry, and location-consistency rules. |
| Single-line checks | [`verifyFractionalSpacingSingle()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L153-L294) | Derives segment counts, lengths, and symmetric placement from one capture. |
| Cross-level checks | [`verifyFractionalSpacingMultiple()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L303-L390) | Checks location consistency and monotonic length behavior. |
| Runtime level matrix | [`genTessLevelCases()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L392-L411) | Generates all 93 levels used by every registered case. |
| Shader generation | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L427-L559) | Emits the GLSL and HLSL capture paths. |
| Resource setup and execution | [`test()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L561-L744) | Creates buffers, draws each level, reads results, and combines both verification phases. |
| Registration | [`createFractionalSpacingTests()`](../../../modules/vulkan/tessellation/vktTessellationFractionalSpacingTests.cpp#L763-L777) | Registers the four language and spacing combinations. |
| Mustpass coverage | [`tessellation.txt#L13-L16`](../../../mustpass/main/vk-default/tessellation.txt#L13-L16) | Confirms all four registered paths. |
| CTS level helpers | [`getClampedTessLevel()` and `getRoundedTessLevel()`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L364-L407) | Implements the reference clamping and parity rounding used by the verifier. |

## Questions / Risk Points for User Audit

- Is `*_even` versus `*_odd` the clearest primary behavior axis, with GLSL versus HLSL treated as an equivalent-language dimension?
- Does the concrete `7.3` fractional-even example make the implementation-dependent segment location clear?
- Does the distinction between one-line structural checks and cross-level checks explain why the test needs 93 draws?
- Is the verifier's conservative handling of four-segment and otherwise indeterminate locations clear enough?

## Conversion Notes for Final Wiki Rewrite

- Distill the spacing rules and isoline observation model into two short prerequisite bullets.
- Use `dEQP-VK.tessellation.fractional_spacing.glsl_even` with the base GLSL tessellation evaluation shader as the representative walkthrough. Generate SPIR-V from the exact reconstructed `initPrograms()` branch at target `spirv1.0`.
- Keep one walkthrough. HLSL differs in source representation but captures the same value and belongs in the variation table.
- Copy the `### Failure Cause Mapping` table above directly into the final page. Write `### Cause Analysis` from the page's validation and spec evidence.
- Keep the two-stage verification distinction in the runtime and failure sections. Move source navigation to the appendix.
