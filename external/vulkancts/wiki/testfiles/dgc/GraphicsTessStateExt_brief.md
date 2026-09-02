# Understanding Brief: EXT graphics tessellation state in device-generated commands

## One-Sentence Test Purpose

This test checks whether `VK_EXT_device_generated_commands` preserves selected tessellation primitive, spacing, patch-size, preprocessing, and dynamic patch-control-points state during graphics draws.

## Background Knowledge

### Tessellation state reaches the patch generator and shaders

A patch is the input unit processed by tessellation. The pipeline's `patchControlPoints` value determines the input patch size, and `gl_PatchVerticesIn` exposes that value to the tessellation control shader. When `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` is enabled, `vkCmdSetPatchControlPointsEXT` supplies the value for later draws instead of the static pipeline value.

Why it matters here:
- Regular cases use patch sizes `3` and `4` and specialize the tessellation control shader for each layer.
- Dynamic cases build a pipeline with static value `3`, then set `4` before the generated draws. The shaders make a wrong value visible by adding a `10.0` position offset.

### Primitive type and spacing change tessellation coordinates

The tessellation evaluation shader declares `triangles`, `quads`, or `isolines`, together with `equal_spacing`, `fractional_odd_spacing`, or `fractional_even_spacing`. The primitive type determines how `gl_TessCoord` represents a generated point, while spacing controls how tessellation levels are rounded and distributed.

Why it matters here:
- The regular test maps those coordinates back to known positions and compares each layer with a reference image.
- A regular case deliberately gives the two layers different state tuples, so state from one selected pipeline cannot be mistaken for the other.

## One Concrete Example

Consider the regular path:

```text
dEQP-VK.dgc.ext.graphics.tess_state.monolithic.triangles_quads.equal_spacing_fractional_odd_spacing.3_4_preprocess
```

The first layer uses triangular, equal-spaced tessellation with a three-control-point output patch. The second uses quadrilateral, fractional-odd-spaced tessellation with four control points. Both tessellation evaluation shaders emit points and write blue through the fragment shader, but they place those points according to their own `gl_TessCoord` interpretation and write to layer `0` or `1`.

The host builds the two pipelines, places an execution-set token and a draw token in the EXT command layout, preprocesses the stream, and executes one indirect draw per layer. The read-back image must match the two reference images selected by the corresponding primitive, spacing, and patch-size tuples.

## End-to-End Test Flow

```text
[host] choose construction type, two layer state tuples, and preprocessing mode
[host] generate vertex, tessellation-control, tessellation-evaluation, and fragment GLSL
[host] build two pipelines or shader-object execution-set entries
[host] create the two-layer color target and host-visible copyback buffer
[host] write one execution-set selection and one indirect draw token per layer
[host] optionally preprocess the generated command stream and issue the preprocess-to-execute barrier
[device] execute the vertex, tessellation, and fragment stages for each generated draw
[device] write blue point output to layer 0 or layer 1
[host] copy both layers to the readback buffer and compare them with exact reference images
[host] return pass or fail
```

The dynamic path follows the same broad order but renders four colored sections. The host records `vkCmdSetPatchControlPointsEXT` with `4`, executes generated draws with optional execution-set and preprocessing variants, renders an ordinary reference with static patch count `4`, and compares the two images.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The regular path generates one vertex shader, one fragment shader, and two tessellation-control and tessellation-evaluation shader pairs. Templates specialize `PATCH_SIZE`, output primitive, spacing, coordinate calculation, and `gl_Layer`.
- The regular path selects reference image data from `vktDGCGraphicsTessStateRefImages.hpp` by primitive type, spacing, and patch size.
- The dynamic path generates one vertex shader, one fragment shader, and one tessellation-control and tessellation-evaluation pair for each tessellation color. The shader uses `gl_PatchVerticesIn` to distinguish the dynamic value `4` from the static value `3`.
- The regular tessellation evaluation shader is compiled for SPIR-V 1.0 and SPIR-V 1.5 because the source uses the shader viewport/layer extension path.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Regular two-layer color image | yes | yes | written by fragment stage | yes, through a copy buffer | Holds one independently checked result layer per selected state tuple. |
| Dynamic result color image | yes | yes | written by fragment stage | yes | Holds the DGC rendering to compare with the ordinary reference. |
| Dynamic reference color image | yes | yes | written by fragment stage | yes | Provides the expected output when patch control points are statically set to `4`. |
| Vertex buffer in dynamic cases | yes | yes | read by vertex stage | no | Supplies four patch vertices; push constants move each draw into a quadrant. |
| DGC command buffer | yes | yes, through device address | read by generated-command execution | no | Contains execution-set selections where used, push-constant data where used, and indirect draw data. |
| Preprocess buffer | yes, where preprocessing is enabled | yes | written by preprocess and read by execution | no | Carries the preprocessed command representation to `cmdExecuteGeneratedCommandsEXT`. |
| Push constants in dynamic cases | yes | yes | read by vertex stage | no | Supplies the four draw offsets. |

`gl_TessCoord`, `gl_PatchVerticesIn`, `gl_Layer`, and GLSL `gl_in` / `gl_out` are shader interface variables, not host-created resources.

## What Is Checked

- Regular cases compare each framebuffer layer against the exact reference data for its `(primitive type, spacing, patch size)` key. The threshold is zero, so the color comparison expects exact values.
- Dynamic cases compare the DGC result image against an image rendered with ordinary pipeline binds, push constants, and draws. The threshold is also zero.
- A mismatch logs the image comparison and returns `Unexpected color in result buffer; check log for details`. A matching comparison returns `pass("Pass")`.
- A missing required feature or extension raises a support error before execution. It is not reported as an image-result failure.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group: regular tessellation-state pairs versus dynamic patch-control-points
>
> **Candidate values:** `Regular tessellation-state pairs`, `Dynamic patch-control-points`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `Regular tessellation-state pairs` | A selected primitive type, spacing mode, patch size, layer assignment, generated pipeline, or reference image did not produce the expected per-layer point pattern. |
| `Dynamic patch-control-points` | `VK_DYNAMIC_STATE_PATCH_CONTROL_POINTS_EXT` did not use the value recorded by `vkCmdSetPatchControlPointsEXT`, or the generated draw path differed from the ordinary reference path. |
| Both groups | Shared pipeline construction, DGC layout, command execution, synchronization, image copyback, or comparison setup failed. |

## Important Variations and Special Cases

- Regular cases use `monolithic`, `fast_lib`, and `shader_objects`. The dynamic-state family uses `monolithic` and `fast_lib`; the source omits shader objects because the relevant state is already dynamic for that construction type.
- Regular cases combine two primitive types, two spacing modes, two patch sizes, and optional preprocessing. The factory removes cases where both layers have the same primitive, spacing, and patch size, because those pairs do not test state differentiation.
- Dynamic cases vary execution-set use and preprocessing, producing the exact leaves `pcp`, `pcp_ies`, `pcp_preprocess`, and `pcp_ies_preprocess`.
- In regular cases, the two evaluation shaders write different image layers. In dynamic cases, push-constant offsets place the four draws in separate framebuffer sections and the tessellation color changes by sequence.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| State enumerations and parameter structures | [Spacing, PrimitiveType, TessStateParams](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L57-L170) | Defines exact names and the regular behavior tuple. |
| Regular shader generation | [TessStateCase::initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L240-L400) | Generates stage artifacts and specializes primitive, spacing, patch size, and layer. |
| Regular rendering and result check | [TessStateInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L403-L662) | Builds the two-layer target, executes DGC, selects references, and compares output. |
| Dynamic state parameters and shaders | [DynamicPCPInstance::Params and DynamicPCPCase::initPrograms](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L664-L867) | Defines the static-versus-dynamic patch-control-points check. |
| Dynamic rendering and reference check | [DynamicPCPInstance::iterate](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L869-L1155) | Renders the DGC result and ordinary reference image and compares them. |
| Case registration | [createDGCGraphicsTessStateTestsExt](../../../modules/vulkan/device_generated_commands/vktDGCGraphicsTessStateTestsExt.cpp#L1159-L1254) | Registers the exact hierarchy and pruning rules. |
| Patch-control-points semantics | [tessellation.adoc](../../../../vulkan-docs/src/chapters/tessellation.adoc#L570-L592) | Defines pipeline patch-control-points state. |
| Dynamic patch-control-points semantics | [pipelines.adoc](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6141-L6147) and [shaders.adoc](../../../../vulkan-docs/src/chapters/shaders.adoc#L2585-L2614) | Defines static-state override and `vkCmdSetPatchControlPointsEXT`. |

## Questions / Risk Points for User Audit

- Is the distinction between regular per-layer state and the dynamic patch-control-points check clear?
- Does the example make the two layer-specific tessellation tuples understandable?
- Are generated shaders clearly separated from host-created images, buffers, and command data?
- Does the exact comparison behavior distinguish support rejection from an unexpected-color failure?
- Is the reason for removing identical regular layer tuples clear?

## Conversion Notes for Final Wiki Rewrite

- Distill the patch-state and primitive/spacing explanations into the final page's `Background Knowledge` section.
- Keep the concrete `triangles_quads` example as the representative shader walkthrough, but use a concise source reconstruction rather than this teaching scaffolding.
- Carry the `Behavior Parameter Identification` conclusion into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table directly into `## Failure Meaning`; write `### Cause Analysis` separately from the implementation and comparison logic.
- Keep the exact registered identifiers, support-gate behavior, dynamic leaves, reference-image selection, and regular identical-tuple pruning.
