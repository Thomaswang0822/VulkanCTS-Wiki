# Understanding Brief: shader_object misc

## One-Sentence Test Purpose

This test checks whether shader objects preserve the behavior of graphics state, stage interfaces, tessellation modes, shader destruction, and push-constant layouts across the `shader_object.misc` test family.

## Background Knowledge

### Shader objects and dynamic graphics state

A shader object represents one compiled shader stage. Unlike a graphics pipeline, it does not carry the complete graphics state with it. Commands in the command buffer set the stage bindings and the dynamic state used by a draw. The same test can therefore run with individual shader objects or with a conventional graphics pipeline while exercising the same state values.

Why it matters here:
- The `state` family compares those two binding models with the same shader stages, resources, and expected output.
- A state value can affect rasterization, depth and stencil tests, blending, color writes, line generation, or whether the draw produces fragments at all.

### Tessellation domains and patch interfaces

A tessellation control shader writes per-patch tessellation levels. The fixed-function tessellator turns each patch into primitives, and the tessellation evaluation shader receives normalized coordinates such as `gl_TessCoord` and computes each generated vertex position. `SpacingEqual`, `SpacingFractionalEven`, and `SpacingFractionalOdd` determine how edge segments are placed; the tessellation control and evaluation stages must agree on the modes that they declare. Shader-object creation also treats stage interfaces, including patch-qualified variables, as part of the stage contract.

Why it matters here:
- `tessellation_modes` changes the control shader's subdivision level and the evaluation shader's spacing mode, then checks the rasterized pattern.
- `tess_patch_non_match` deliberately binds two tessellation-control shaders with different patch output declarations and changes the bound stage between draws.

## One Concrete Example

Consider `dEQP-VK.shader_object.misc.tessellation_modes.one.equal`. The vertex shader emits four control points. The tessellation control shader declares `layout(vertices = 4) out` and writes all inner and outer tessellation levels as `1.0`. The tessellation evaluation shader declares `layout(quads, equal_spacing) in` and bilinearly interpolates the four input positions using `gl_TessCoord`. A fragment shader writes white. The host sets polygon mode to line, draws one patch, and compares the resulting 32 by 32 image with a fixed white/black pattern.

The evaluation shader's central operation is conceptually:

```glsl
// Reconstructed example from the CTS generator.
float u = gl_TessCoord.x;
float v = gl_TessCoord.y;
vec2 weights = vec2(1.0 - u, 1.0 - v);
gl_Position = weights.x * weights.y * gl_in[0].gl_Position
            + u * weights.y * gl_in[2].gl_Position
            + u * v * gl_in[3].gl_Position
            + weights.x * v * gl_in[1].gl_Position;
```

This is an illustrative reduction of the generated shader. The final page walkthrough keeps the generated declarations and expression.

## End-to-End Test Flow

```text
[host] select one registered family and its parameter values
[host] check the required VK_EXT_shader_object, core features, and optional extension features
[host] generate GLSL program artifacts for the selected stages
[host] create images, buffers, descriptor sets, a pipeline layout, and shader objects or a graphics pipeline
[host] begin rendering and set the selected dynamic state
[host] bind shader stages or bind the conventional graphics pipeline
[host] submit one or more draws, with a second draw for cases that test rebinding or blending
[device] execute the selected vertex, tessellation, geometry, mesh, and fragment stages
[device] write color, depth, stencil, transform-feedback, or storage-buffer results
[host] insert barriers, copy images to host-visible buffers, and invalidate allocations
[host] compare results with exact values, ranges, thresholds, or reference images
[host] decide pass/fail
```

The `tess_patch_non_match` flow has two draws. The host pushes the geometry color, draws with one tessellation-control shader, rebinds the tessellation-control stage, and draws again. Both generated tessellation-control shaders write the pushed color through the shared `patchColor` output, so the final one-pixel image must equal the geometry color. The source comment describes the first draw as a no-op with the clear color, but the code pushes `geomColor` before that draw; this discrepancy remains a source-level risk. The `state` flow can use a second draw with a different descriptor set when depth-clamp and depth-clip are disabled.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The blend and vertex-input matrix generates `inputVert` and `multiFrag`. The vertex shader reads location 0 and scales the input position; the fragment shader reads a storage-buffer `vec4` and writes it to two color outputs.
- The `state` family generates `vert`, `tesc`, `tese`, `geom`, `frag`, and, for `mesh_frag`, `mesh`. The selected booleans change stage presence, primitive topology, tessellation layout, geometry output, mesh output, and storage-buffer writes.
- `unused_variable` generates all five graphics-stage sources for each selected stage, but adds either an unused user output or an unused built-in write to the selected stage. The `linked` cases set `VK_SHADER_CREATE_LINK_STAGE_BIT_EXT` on the created stages.
- `tessellation_modes` generates four stages. The control shader uses subdivision `1.0` or `2.0`; the evaluation shader uses one of the three spacing execution modes.
- `tess_patch_non_match` generates two tessellation-control shaders. Both write `patchColor` at location 1, while the second also declares `foo` at location 0 and `bar` at location 2. The host swaps which shader handle is bound for the second draw.
- `push_const` generates a vertex shader and a fragment shader using `GL_EXT_shader_8bit_storage`. Depending on the case, the fragment push-constant block declares every byte in the tested range or only `g` and `b` at the selected offset.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 32 by 32 color image(s) | yes | as color attachments | written by fragment output | yes, through transfer buffers | Carries the color and rasterization result. |
| Depth/stencil image in `state` | yes | as depth and stencil attachments | written by depth and stencil tests | yes, through temporary buffers | Exposes depth bounds, clamp, clip, bias, and stencil behavior. |
| Host-visible storage buffer(s) | yes | descriptor binding 0 | written by vertex, tessellation, geometry, or mesh stages; read by `multiFrag` in the blend matrix | yes | Records stage execution and fragment input values. |
| Vertex buffer in the blend matrix | yes | vertex binding 0 | read by the vertex stage | indirectly through color | Its stride, null stride pointer, and vertex-input timing are tested. |
| Transform-feedback buffer | yes, only for `geometry_streams` | transform-feedback binding 0 | written by geometry output | yes | Records the value emitted on each geometry stream vertex. |
| Push-constant range | yes | pipeline layout and fragment shader | read by the fragment shader | indirectly through `R8G8B8A8_UINT` color | Tests offsets, sizes, and bytes outside the declared member set. |
| GLSL `gl_PerVertex`, patch variables, and built-ins | no, shader interface objects | stage interface | read or written by shader stages | indirectly through rendering | They are not host-created descriptors; they test interface matching and unused-variable handling. |

## What Is Checked

- The blend matrix compares each pixel in both color attachments with black outside the inner rectangle and with either `(0.75, 0.75, 0.75, 0.75)` or `(0.5, 0.5, 0.5, 0.5)` inside it, using a per-component threshold of `1.0f / 256.0f`.
- `state` checks stage marker values in storage buffers, transform-feedback values for geometry streams, color values inside and outside the expected primitive, depth within parameter-specific ranges, and stencil values of `255` inside and `0` outside when enabled.
- `unused_variable` requires white pixels inside a 24 by 24 region and black pixels outside it. This checks that the selected unused output or built-in does not prevent shader creation or alter the draw.
- `tessellation_modes` compares the line-rasterized 32 by 32 image with a parameter-specific reference matrix. `tess_patch_non_match` compares a one-pixel `R8G8B8A8_UNORM` image with the expected geometry color using `tcu::floatThresholdCompare()`.
- `push_const` reads every `R8G8B8A8_UINT` pixel and requires the packed value derived from the selected push-constant bytes. The test aggregates mismatches across the whole image.

## Behavior Parameter Identification

> **Behavior parameter:** test family under `shader_object.misc`
>
> **Candidate values:** `on` and `off`, `state`, `unused_variable`, `tessellation_modes`, `tess_patch_non_match`, `push_const`

The `on` and `off` names are the two outer blend branches. Their deeper `on`/`off` child controls the second attachment's blend state. The `state` family has its own independent axes for pipeline mode, stage set, dynamic state family, and state value. The remaining four families each exercise a distinct shader-object behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `on` or `off` | Dynamic vertex-input setup, vertex-buffer stride handling, descriptor-set-layout lifetime handling, or color-blend state produces the wrong attachment pixels. |
| `state` | A selected shader-object or pipeline state value is not applied, is applied at the wrong time, or produces the wrong color, depth, stencil, storage-buffer, or transform-feedback result. |
| `unused_variable` | Shader creation or stage linking mishandles an unused user output or built-in in the selected stage. |
| `tessellation_modes` | Tessellation control/evaluation execution modes or shader-object stage binding produce the wrong subdivision pattern. |
| `tess_patch_non_match` | Rebinding the tessellation-control stage with a different patch interface is mishandled, or the second draw does not use the newly bound stage. |
| `push_const` | Push-constant byte offsets, declared ranges, 8-bit member layout, or fragment reads produce the wrong packed color. |

## Important Variations and Special Cases

- The blend matrix has two outer blend values, two inner blend values, two vertex-input ordering values, two stride-pointer modes, four stride values, and two descriptor-set-layout lifetime values. The source registration produces 256 leaves; the default `misc.txt` contains 128 leaves for these two branches.
- The `state` family has `shaders` and `pipeline` branches and six stage sets: `vert`, `vert_frag`, `vert_tess_frag`, `vert_geom_frag`, `vert_tess_geom_frag`, and `mesh_frag`. The registered state names include extra `lines` leaves for rasterizer discard and triangle topology.
- Some `state` values require optional extensions or features. `discard_rectangles` requires extension version 2 or later; `geometry_streams` requires transform feedback geometry streams; line cases accept either `VK_KHR_line_rasterization` or `VK_EXT_line_rasterization`.
- `unused_variable` has `linked` and `unlinked` branches, `output` and `builtin` forms, and `vert`, `tesc`, `tese`, and `geom` stage leaves. The built-in form writes values such as `gl_PointSize` and `gl_ClipDistance[0]`; the output form writes a location 0 variable only in the selected stage.
- `tessellation_modes` registers all six combinations of `one`/`two` subdivision and `equal`/`even`/`odd` spacing. `tess_patch_non_match` has `standard` and `reverse` binding order.
- `push_const` registers `57_64_all`, `63_64_all`, `17_64`, `63_64`, `17_37_all`, `36_37_all`, `17_37`, and `36_37`. The `_all` forms declare the complete byte range in the fragment block; the other forms declare only the two bytes needed at the selected word offset.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Blend, vertex input, stride, and layout lifetime | [blend matrix and `ShaderObjectMiscInstance`](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L54-L61) | Defines the first matrix's parameters and host setup. |
| Blend matrix registration | [registration loop](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3497-L3551) | Provides the exact `on` and `off` hierarchy and values. |
| Dynamic state setup | [state setter](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L877-L1187) | Shows how selected state values become command-buffer state. |
| State registration | [state registration](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3553-L3972) | Defines the pipeline, stage-set, and state-family matrix. |
| State result checks | [state validation](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L1760-L2000) | Defines color, depth, stencil, storage-buffer, and transform-feedback checks. |
| Unused-variable generation and validation | [unused-variable code](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2349-L2704) | Shows the output/built-in and linked/unlinked variants. |
| Tessellation mode generation | [tessellation mode sources](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2925-L3017) | Shows subdivision and spacing execution-mode branches. |
| Tessellation semantics | [tessellation chapter](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L19) | Defines the control, tessellator, and evaluation stages. |
| Tessellation spacing | [spacing rules](../../../../vulkan-docs/src/chapters/tessellation.adoc#L181-L220) | Grounds the `equal`, `even`, and `odd` interpretation. |
| Patch interface mismatch | [mismatch generation and run](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3019-L3227) | Shows the two patch declarations and stage rebind. |
| Push-constant layout and check | [push-constant implementation](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3230-L3405) | Defines offsets, ranges, generated 8-bit members, and packed output. |
| Push constants specification | [push constant validity](../../../../vulkan-docs/src/chapters/commonvalidity/push_constants_common.adoc#L1-L40) | Provides the relevant range and stage-layout rules. |

## Questions / Risk Points for User Audit

- Does the page distinguish the two outer blend branches from the inner blend child clearly enough?
- Is the large `state` matrix explained without pretending that its state-family names are all independent top-level test families?
- Is the difference between a shader-local interface variable and a host-created descriptor resource clear?
- Does the tessellation example explain why both tessellation stages matter and why spacing changes the reference image?
- Are the optional extension and feature requirements clear enough for a reader to understand why a case may be skipped?
- Is the push-constant explanation precise about byte offsets and the `_all` versus sparse declarations?

## Conversion Notes for Final Wiki Rewrite

- Use the `shader_object.misc` root tree with its seven direct children and keep the large generated state descendants in parameter tables and prose.
- Carry the test-family axis and the mapping table into the final page unchanged.
- Distill the shader-object, dynamic-state, and tessellation prerequisites into short page-local bullets.
- Use the `tessellation_modes.one.equal` evaluation shader as the representative walkthrough. Keep the vertex, tessellation-control, and fragment stages in the page-level explanation, but do not add boilerplate stage walkthroughs.
- Put the full matrix and validation details in the corresponding page sections, not in the source appendix.
- Write fresh cause analysis for the six mapped behavior values. Do not copy this brief's teaching scaffolding verbatim.
