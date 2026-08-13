# Understanding Brief: `tessellation.geometry_interaction.point_size`

## One-Sentence Test Purpose

This test checks whether `gl_PointSize` is set, replaced, and passed through the vertex, tessellation, and geometry stages so that the final point rasterizes at the size written by the last active operation.

## Background Knowledge

### Point-size selection across pre-rasterization stages

Vulkan rasterizes a point as a square whose width and height come from the `PointSize` built-in. The geometry shader supplies the rasterized size when present; otherwise the tessellation evaluation shader supplies it when present, and the vertex shader supplies it when neither later stage is active ([point rasterization](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-points)).

Why it matters here:

- A later stage can replace an earlier value, so the visible size identifies which stage's result reached rasterization.
- A stage can also read its input point size and add to it. That path tests stage-interface propagation as well as a final write.

### Tessellation point mode and point-size access

A tessellation evaluation shader with `point_mode` makes the tessellator produce points instead of lines or triangles. Access to `PointSize` in tessellation and geometry shaders requires `shaderTessellationAndGeometryPointSize` ([feature definition](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderTessellationAndGeometryPointSize)). A portability-subset implementation can separately report that tessellation point mode is unavailable ([point-mode requirement](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation-point-mode)).

Why it matters here:

- Cases with tessellation stages use triangle-domain point mode and move all but one generated point outside clip space.
- The cumulative case reads and writes point size in both the tessellation pair and the geometry stage.

## One Concrete Example

Consider `dEQP-VK.tessellation.geometry_interaction.point_size.vertex_set_control_pass_eval_add_geometry_add`.

The vertex shader starts with `gl_PointSize = 2.0`. The tessellation control shader copies that value from `gl_in[0]` to `gl_out[0]`; the tessellation evaluation shader writes `gl_in[0].gl_PointSize + 2.0`, producing `4.0`. The geometry shader then writes its input plus another `2.0`, producing the expected final size `6` ([shader generation](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L172-L288), [expected-size calculation](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L80-L103)).

The host draws one input item at the center of a `32 x 32` attachment. The tessellator generates multiple points because its levels are `3.0`, but the evaluation shader moves every invocation with `gl_TessCoord.x < 0.99` to x = `-2.0`. The remaining point passes through geometry and should cover an exact `6 x 6` non-black square.

## End-to-End Test Flow

```text
[host] select one registered combination of point-size stage operations
[host] generate the fixed vertex and fragment shaders plus optional tessellation and geometry shaders
[host] derive the expected final point size from the selected operations
[host] require tessellation, geometry, and tessellation/geometry point-size features and check the size limit
[host] create a 32 x 32 RGBA8 color attachment and host-visible readback buffer
[host] build a graphics pipeline with the stages selected by the case flags
[host] clear the attachment to opaque black and issue one non-indexed draw
[device] set, copy, replace, or add to gl_PointSize in the selected pre-rasterization stages
[device] rasterize one visible white point at the final stage's point size
[host] copy the attachment to the buffer, wait, invalidate memory, and inspect the image
[host] pass only if the non-black bounding box is square and matches the expected integer size
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`initPrograms()` always generates ESSL 3.10 vertex and fragment shaders. It adds a tessellation control/evaluation pair when the flags contain `evaluation_set` or `control_pass_eval_add`, and a geometry shader when they contain `geometry_set` or `geometry_add` ([program generation](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L172-L289)).

The selected flags control only point-size operations and stage presence. There are no descriptors, push constants, specialization constants, vertex attributes, or generated SPIR-V assembly strings. The CTS shader toolchain compiles the generated GLSL.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `32 x 32` `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | yes, as color attachment and transfer source | cleared and written | copied | Contains the white rasterized point against opaque black. |
| Host-visible color buffer | yes | yes, as transfer destination | written by image copy | yes | Supplies the pixels scanned by `verifyImage()`. |
| `gl_PerVertex` point-size interface | generated shader interface | yes, through active stages | read and written | no | Carries `gl_PointSize`; it is not a descriptor-backed resource. |

## What Is Checked

- `getExpectedPointSize()` models last-writer behavior: geometry `set` returns `6`; otherwise geometry `add` contributes `2`, tessellation `set` returns `4` plus that contribution, tessellation `add` contributes another `2`, and vertex `set` returns `2` plus accumulated additions.
- `verifyImage()` finds every pixel that differs from opaque black and forms their axis-aligned bounding box.
- The case fails if no non-black fragment exists, if the bounding box is not square, or if its width differs from the expected size.
- There is no tolerance or reference-image comparison. The expected widths are the exact integers `2`, `4`, and `6` ([verification](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L115-L170), [result handling](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L414-L430)).

## Behavior Parameter Identification

> **Behavior parameter:** point-size operation sequence (behavioral group)
>
> **Candidate values:** `single-stage set`, `downstream replacement`, `cumulative propagation`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single-stage set` | The selected vertex, tessellation evaluation, or geometry output did not supply the expected `gl_PointSize` to point rasterization; rendering or readback can produce the same missing or wrong bounding box. |
| `downstream replacement` | A downstream tessellation evaluation or geometry write did not replace an earlier point-size value as required, or the final stage value was not used for rasterization; shared rendering/readback causes also apply. |
| `cumulative propagation` | A point-size value was not copied through tessellation control, read and incremented by tessellation evaluation, or read and incremented by geometry before rasterization; shared rendering/readback causes also apply. |

## Important Variations and Special Cases

| Test case leaf | Active point-size operations | Expected size |
|----------------|------------------------------|---------------|
| `vertex_set` | vertex sets `2.0` | `2` |
| `evaluation_set` | tessellation evaluation sets `4.0` | `4` |
| `geometry_set` | geometry sets `6.0` | `6` |
| `vertex_set_evaluation_set` | vertex sets `2.0`; evaluation replaces it with `4.0` | `4` |
| `vertex_set_geometry_set` | vertex sets `2.0`; geometry replaces it with `6.0` | `6` |
| `vertex_set_evaluation_set_geometry_set` | vertex sets `2.0`; evaluation sets `4.0`; geometry replaces it with `6.0` | `6` |
| `vertex_set_control_pass_eval_add_geometry_add` | vertex sets `2.0`; tessellation passes then adds `2.0`; geometry adds `2.0` | `6` |

- Geometry-only cases use point-list input and no tessellation stages. Cases with tessellation stages use a one-control-point patch and triangle-domain `point_mode`; the pipeline builder switches input topology to patch list when a tessellation control shader is active ([pipeline setup](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L348-L379), [topology selection](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L201-L208)).
- The registration omits cases that depend on Vulkan's default point size. The source comment says those GLES 3.1 cases are not valid in Vulkan ([registration note](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L466-L480)).
- All leaves require tessellation, geometry, and tessellation/geometry point-size support in `test()`, even when a leaf's generated pipeline omits one or both optional stage sets.
- `checkPointSizeRequirements()` compares the expected size against the upper `pointSizeRange` limit. The source relies on point-size granularity being at most `1.0`, so its integer sizes need no separate granularity check.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Flags and expected-size model | [`FlagBits` and `getExpectedPointSize()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L62-L103) | Defines each stage operation and last-writer/addition result. |
| Host image check | [`verifyImage()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L115-L170) | Defines the exact non-black bounding-box pass rule. |
| Generated shader stages | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L172-L289) | Generates all set, pass, and add operations. |
| Feature and size gates | [`test()` requirements](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L291-L320) | Requires three core features and checks the expected point size. |
| Pipeline, draw, and readback | [`test()` runtime path](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L322-L430) | Creates resources, draws once, copies the image, and returns the result. |
| Case names and registration | [`getTestCaseName()` and `createGeometryPointSizeTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPointSizeTests.cpp#L433-L489) | Defines the seven exact test case leaves. |
| Test-family parent registration | [`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) | Places `point_size` under `tessellation.geometry_interaction`. |
| Point rasterization semantics | [`primsrast-points`](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-points) | Defines stage precedence and square point coverage. |
| Point-size stage feature | [`features-shaderTessellationAndGeometryPointSize`](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderTessellationAndGeometryPointSize) | Defines legal `PointSize` access in tessellation and geometry stages. |
| Default mustpass coverage | [`tessellation.txt#L25-L31`](../../../mustpass/main/vk-default/tessellation.txt#L25-L31) | Confirms all seven registered leaves. |

## Questions / Risk Points for User Audit

- Is grouping the seven leaves as `single-stage set`, `downstream replacement`, and `cumulative propagation` the clearest behavioral axis? It distinguishes direct writes, last-writer precedence, and stage-interface transport without treating every leaf as unrelated behavior.
- Is the cumulative case the right representative walkthrough? It exercises every nontrivial read/write path; fixed-value cases are simpler branches described by the variation table.
- Does the bounding-box explanation avoid overclaiming? The host measures the union of all non-black pixels. It does not compare point centering, per-pixel color, or an independent reference image.
- Should the final page call out the unconditional three-feature gate? It can explain an unsupported result on a leaf whose generated pipeline does not contain every optional stage.

The inspected implementation, utility builder, Vulkan point-rasterization and feature chapters, and default mustpass entries resolve these questions. They remain review prompts rather than blockers.

## Conversion Notes for Final Wiki Rewrite

- Distill point-size stage precedence, point mode, and the feature requirement into short prerequisite bullets.
- Use `dEQP-VK.tessellation.geometry_interaction.point_size.vertex_set_control_pass_eval_add_geometry_add` for one representative shader walkthrough. Show the tessellation pass/add stages and geometry add stage, with geometry as the SPIR-V target.
- Carry the three behavioral groups into `## Behavior Parameters`; keep the seven exact leaves and expected sizes in the parameter table.
- Copy the `### Failure Cause Mapping` table above directly into the final page. Write `### Cause Analysis` from source and spec evidence.
- Keep the exact bounding-box check in the runtime section and move source navigation to the appendix.
- Apply the mandatory `humanizer` and `stop-slop` passes conservatively so registered paths, code, links, and technical claims remain unchanged.
