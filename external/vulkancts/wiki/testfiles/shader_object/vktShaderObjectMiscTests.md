# [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L1)

## Overview

[`vktShaderObjectMiscTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L1) implements the `shader_object/misc` branch. It registers a broad `misc` branch at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3498-L4080). Observed families include a blend/vertex-input/stride/destruction matrix, a large `state` subtree comparing shader-object and pipeline modes across shader sets and dynamic states, `unused_variable`, `tessellation_modes`, `tess_patch_non_match`, and `push_const`. Verification combines pixel comparisons, depth/stencil checks, transform-feedback/storage-buffer checks, a tessellation patch mismatch image comparison, and push-constant result comparison at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L390-L410), [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L1778-L2002), [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3128-L3229), and [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3394-L3405).

## Role of File

Implementation-heavy test file for the root-level `misc` branch.

## Source Code

- Primary source: [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L60)
- Shared utility include: [vktShaderObjectCreateUtil.hpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Path

```text
shader_object
+-- misc
    +-- {on,off}/{on,off}/{before,after}/{null,non_null}/{16,32,48,40}/{set,destroyed}
    +-- state/{shaders,pipeline}/{shader-set}/{state-family}/{case}
    +-- unused_variable/{unlinked,linked}/{output,builtin}/{vert,tesc,tese,geom}
    +-- tessellation_modes/{one,two}/{equal,even,odd}
    +-- tess_patch_non_match/{standard,reverse}
    +-- push_const/{57_64_all,63_64_all,17_64,63_64,17_37_all,36_37_all,17_37,36_37}
```

Explicit registration path prefixes for verifier extraction:

```text
`shader_object.misc`
`shader_object.misc.on.on.before.null.16.destroyed`
`shader_object.misc.state.shaders.vert_frag.color_blend.enabled`
`shader_object.misc.unused_variable.unlinked.output.vert`
`shader_object.misc.tessellation_modes.one.equal`
`shader_object.misc.tess_patch_non_match.standard`
`shader_object.misc.push_const.57_64_all`
```

The displayed branch name is verified from `TestCaseGroup(testCtx, "misc")` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3498-L3500). The root file registers this branch directly at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L60).

## Test Hierarchy

```text
misc
+-- blend/vertex-input/stride/destruction matrix
+-- state
|   +-- shaders / pipeline
|       +-- shader-set
|           +-- alphaToOne, depth, discard_rectangles, rasterization_discard, color_blend, primitives,
|               stencil, logic_op, geometry_streams, provoking_vertex, sample_locations, lines, cull,
|               conservative_rasterization, color_write
+-- unused_variable
+-- tessellation_modes
+-- tess_patch_non_match
+-- push_const
```

## Test Families

### Blend, vertex input, stride, and destruction matrix

The first family iterates two blend toggles, vertex-input timing (`before`/`after`), null versus non-null stride, four stride values, and two descriptor-set-layout destruction names at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3502-L3552). The corresponding `ShaderObjectMiscInstance` uses dynamic vertex input and vertex-buffer binding helpers at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L90-L122).

### Dynamic state comparison subtree

The `state` subtree varies pipeline mode (`shaders` versus `pipeline`) at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3554-L3561), six shader sets at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3563-L3620), and many state families registered from arrays at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3622-L3973). It is the largest family in this file and compares shader-object operation with pipeline/dynamic-rendering operation under selected state combinations.

### Unused variable, tessellation, patch mismatch, and push constants

`unused_variable` combines linked state, output/builtin selector, and four shader stages at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3975-L4023). `tessellation_modes` combines subdivision count names `one`/`two` with spacing names `equal`/`even`/`odd` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L4025-L4058). `tess_patch_non_match` registers standard and reverse tessellation-control binding orders through function cases at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L4060-L4068). `push_const` registers eight offset/size/all-stage combinations at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L4070-L4079).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Blend toggles | Two nested `on`/`off` levels at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3508-L3516) |
| Vertex-input timing | `before`, `after` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3516-L3521) |
| Vertex-buffer stride | `16`, `32`, `48`, `40` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3502-L3506) |
| State pipeline mode | `shaders`, `pipeline` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3554-L3561) |
| State shader set | `vert`, `vert_frag`, `vert_tess_frag`, `vert_geom_frag`, `vert_tess_geom_frag`, `mesh_frag` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3563-L3620) |
| State families | `alphaToOne`, `depth`, `discard_rectangles`, `rasterization_discard`, `color_blend`, `primitives`, `stencil`, `logic_op`, `geometry_streams`, `provoking_vertex`, `sample_locations`, `lines`, `cull`, `conservative_rasterization`, `color_write` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3801-L3967) |
| Unused-variable matrix | linked/unlinked, output/builtin, and stages `vert`, `tesc`, `tese`, `geom` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3975-L4023) |
| Tessellation modes | subdivisions `one`/`two` and spacings `equal`/`even`/`odd` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L4025-L4058) |
| Push constants | Eight registered offset/size/all-stage case names at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L4070-L4079) |

## Support / Feature Requirements

- The blend/vertex-input/stride matrix requires `VK_EXT_shader_object` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L436-L439).
- State cases require a depth/stencil format, `vertexPipelineStoresAndAtomics`, and either `VK_EXT_shader_object` for shader-object mode or `VK_KHR_dynamic_rendering` for pipeline mode at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2026-L2044).
- State cases additionally gate selected parameters on core features or extensions including logic op, alpha-to-one, depth bounds/clamp, depth clip enable/control, color write enable, transform feedback geometry streams, discard rectangles version 2, conservative rasterization, sample locations, provoking vertex, line rasterization, geometry/tessellation shader, mesh shader, and extended dynamic state features at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2045-L2180).
- `unused_variable` cases require `VK_EXT_shader_object`, geometry shader, and tessellation shader support at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2569-L2574).
- `tessellation_modes` cases require `VK_EXT_shader_object` and tessellation shader support at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2950-L2954).
- `push_const` cases require `VK_EXT_shader_object` and `VK_KHR_8bit_storage` at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3437-L3441).
- Registration itself is unconditional once the root adds the branch factory at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L60).

## Verification Methods

- The blend/vertex-input/stride matrix compares each pixel against expected reference colors with a threshold and fails on mismatches at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L390-L410).
- State tests verify transform-feedback output for line/primitive modes, storage-buffer values for vertex/tessellation/geometry stages, rendered color output, and depth/stencil values with explicit expected ranges and values at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L1778-L2002).
- `unused_variable` cases compare rendered output: white inside the drawn area and black outside it at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2518-L2543).
- `tessellation_modes` cases compare rendered output against white inside the primitive and black outside it at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2898-L2923).
- `tess_patch_non_match` renders with two tessellation-control shaders, rebinds the tessellation-control stage, copies the result image to a buffer, and uses `tcu::floatThresholdCompare()` against a reference color image at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3128-L3229).
- `push_const` cases read back the output buffer and fail if any pixel value differs from the expected push-constant-derived color at [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3394-L3405).

## Test Principles Observed

- Collect shader-object edge cases that do not fit the narrower API/create/link/rendering branches.
- Compare shader-object and pipeline-style state behavior where the `state` subtree has both modes.
- Use targeted output checks for color, depth/stencil, transform feedback, storage buffers, tessellation rebinding, and push constants.

## Notes / Uncertainties

- The state subtree is very large; this page documents the observed registration dimensions and representative verification checks without expanding every generated leaf.
