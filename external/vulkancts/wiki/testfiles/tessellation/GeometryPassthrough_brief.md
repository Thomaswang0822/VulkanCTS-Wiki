# Understanding Brief: `tessellation.geometry_interaction.passthrough`

## One-Sentence Test Purpose

This test checks whether inserting an identity geometry stage after tessellation, or inserting identity tessellation stages before geometry shading, preserves the rendered image.

## Background Knowledge

### Optional programmable stages and identity behavior

A Vulkan graphics pipeline can place tessellation control and evaluation stages between vertex and geometry shading. The tessellator turns patches into points, lines, or triangles, and the evaluation shader computes positions and attributes for the generated vertices. A geometry shader receives one assembled primitive and can emit new primitives. See [Tessellation](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L32) and [Geometry Shading](../../../../vulkan-docs/src/chapters/geometry.adoc#L6-L28).

An identity stage preserves the observable primitive stream even though the GPU still executes the stage. Here, identity has two forms:

- The passthrough geometry shader copies each incoming vertex position and color and emits the vertices in order.
- The passthrough tessellation stages use tessellation levels of `1.0` and interpolate the original triangle or line endpoints, so the following geometry shader receives an equivalent primitive.

### Differential image checking

The test renders the same intended output through two pipeline arrangements instead of comparing either arrangement with a stored reference image. A match checks equivalence between the arrangements. It does not isolate which arrangement caused a difference.

Why it matters here:

- Both draws use the same vertex input, color attachment format, render area, and fragment shader.
- Additive blending makes omitted, duplicated, or overlapping primitive contributions visible in the compared images.

## One Concrete Example

Consider the executable test case:

```text
dEQP-VK.tessellation.geometry_interaction.passthrough.tessellate_triangles_passthrough_geometry_no_change
```

The host renders four control points as tessellated triangle patches twice. Both pipelines use the same tessellation control and evaluation shaders with level `14.0`. The first pipeline then runs this conceptual geometry operation:

```glsl
/// Conceptual form of the generated identity geometry shader.
for (int ndx = 0; ndx < gl_in.length(); ++ndx)
{
    gl_Position = gl_in[ndx].gl_Position;
    v_fragment_color = v_evaluated_color[ndx];
    EmitVertex();
}
```

The second pipeline sends the evaluation shader output straight to fragment shading. The two copied RGBA8 images must match within the CTS color and position tolerances. The source constructs this pair in [`IdentityGeometryShaderTestCase::createInstance()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L670-L708).

## End-to-End Test Flow

```text
[host] select one of five registered cases and construct its two pipeline descriptions
[host] upload the common vertex positions
[host] upload tessellation level 14.0 when testing a passthrough geometry shader
[host] create one RGBA8 color attachment and two host-visible readback buffers
[host] build the first pipeline, clear the attachment, draw, and copy the image to readback buffer 0
[device] execute the first stage arrangement and blend its fragments into the attachment
[host] wait, build the second pipeline, clear the same attachment, draw, and copy the image to readback buffer 1
[device] execute the comparison stage arrangement and blend its fragments into the attachment
[host] invalidate both readback allocations and compare the two images
[host] pass on a thresholded positional match; otherwise fail with "Image comparison failed"
```

[`PassthroughTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L465-L668) implements this shared timeline.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The case classes generate all shaders as GLSL ES 3.10 source:

- The common vertex shader forwards `a_position` to `gl_Position` and derives a position-dependent color. The fragment shader writes that interpolated color.
- Geometry-passthrough cases generate a tessellation control shader that reads six tessellation levels from a storage buffer, a nonlinear tessellation evaluation shader, and an identity geometry shader. They compile two evaluation variants because one names its color output for the geometry stage and the other names it for the fragment stage.
- Tessellation-passthrough cases generate identity tessellation stages with levels fixed to `1.0`. They compile two geometry variants so the same geometry operation can read either the evaluation shader output or the vertex shader output.
- The pipeline descriptions choose which optional stages and shader-name variants each of the two draws uses.

The generators and stage pairings appear in [`IdentityGeometryShaderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L164-L235), [`IdentityTessellationShaderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L320-L387), and the two [`createInstance()` implementations](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L670-L743).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | device reads | no | Supplies the common control points and the position values used to derive color. |
| Tessellation-level storage buffer | yes | only for geometry-passthrough cases | tessellation control shader reads | no | Supplies six values fixed to `14.0`, creating enough primitives to expose geometry-stage passthrough errors. |
| Descriptor set at set 0, binding 0 | yes | only for geometry-passthrough cases | device consumes binding | no | Makes the tessellation-level buffer visible to the tessellation control shader. |
| 256 by 256 `VK_FORMAT_R8G8B8A8_UNORM` color attachment | yes | yes | color output writes, transfer reads | indirectly | Holds each rendered result before copyback. The host clears it before each draw. |
| Two host-visible color buffers | yes | yes, as transfer destinations | transfer writes | yes | Preserve one image from each pipeline arrangement for comparison. |

The host creates the resources in [`PassthroughTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L475-L560). The descriptor exists for both behavioral groups to share setup code, but the host binds it only when `useTessLevels` is true.

## What Is Checked

- The host compares all pixels from the two 256 by 256 RGBA8 renderings.
- Each color channel allows an integer difference of `8`; alpha allows `255`.
- The comparator searches a 3 by 3 neighborhood through position deviation `(1, 1, 0)` and ignores out-of-bounds candidates.
- A successful comparison returns `pass("OK")`. A mismatch returns `fail("Image comparison failed")`.

The oracle is [`tcu::intThresholdPositionDeviationCompare()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L648-L667).

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group selected by the test case leaf prefix
>
> **Candidate values:** `tessellate_*_passthrough_geometry_no_change`, `passthrough_tessellation_geometry_shade_*_no_change`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `tessellate_*_passthrough_geometry_no_change` | The geometry stage changes positions, colors, primitive assembly, emission count, or rasterized overlap relative to the no-geometry pipeline. |
| `passthrough_tessellation_geometry_shade_*_no_change` | The identity tessellation stages change control-point transport, tessellator output, evaluated positions or colors, or the primitive stream received by geometry shading. |

A failure in either group can also come from shared pipeline setup, blending, image transitions, image-to-buffer copy, host-memory visibility, or differential image comparison.

## Important Variations and Special Cases

- Primitive type forms the secondary dimension. Geometry-passthrough coverage includes `triangles`, `quads`, and `isolines`; tessellation-passthrough coverage includes `triangles` and `isolines`.
- Geometry-passthrough cases use level `14.0` and a nonlinear evaluation function. The dense output stresses whether the added geometry stage emits each generated primitive once.
- Tessellation-passthrough cases use level `1.0`. Their tessellation stages must reconstruct the triangle or line that the geometry shader would otherwise receive from the vertex stage.
- The source excludes a tessellation-passthrough quad case. With tessellation disabled, the comparison pipeline has no quad-domain stage; the helper geometry generator implements only triangle and isoline inputs.
- Both pipeline arrangements use additive blending. This makes a duplicate primitive brighter and helps expose an emission-count error even when covered geometry has the same outline.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category attachment | [`createGeometryInteractionTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L52-L61) | Attaches `passthrough` below `tessellation.geometry_interaction`. |
| Common vertex and fragment stages | [`addVertexAndFragmentShaders()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L58-L91) | Defines common position and color behavior. |
| Geometry-passthrough shaders | [`IdentityGeometryShaderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L164-L235) | Generates level-buffer TCS, nonlinear TES variants, and identity GS. |
| Tessellation-passthrough shaders | [`IdentityTessellationShaderTestCase::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L320-L387) | Generates identity tessellation and geometry-input variants. |
| Shared execution and oracle | [`PassthroughTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L465-L668) | Builds both pipelines, renders, copies, and compares. |
| Pipeline pairs | [`createInstance()` implementations](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L670-L743) | Defines the exact stage arrangements and input data. |
| Registration | [`createGeometryPassthroughTests()`](../../../modules/vulkan/tessellation/vktTessellationGeometryPassthroughTests.cpp#L766-L781) | Registers the three geometry-passthrough and two tessellation-passthrough leaves. |
| Vulkan default mustpass | [`tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L20-L24) | Lists all five executable Vulkan paths. |
| Tessellation model | [`tessellation.adoc`](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L32) | Defines the control, fixed-function tessellator, and evaluation sequence. |
| Geometry model | [`geometry.adoc`](../../../../vulkan-docs/src/chapters/geometry.adoc#L6-L28) | Defines geometry shader input and emitted output primitives. |

## Questions / Risk Points for User Audit

- Does the two-pipeline equivalence model make clear that neither image is an external reference?
- Is the distinction between a passthrough geometry stage and passthrough tessellation stages clear?
- Does the resource table make clear that two readback buffers hold the compared images while one color attachment is reused?
- Is the design reason for omitting a quad tessellation-passthrough case convincing from the source branches?
- Does the failure mapping avoid assigning a mismatch to one pipeline arrangement without further investigation?

## Conversion Notes for Final Wiki Rewrite

- Keep the optional-stage identity concept and differential comparison model as compact prerequisites.
- Use the triangle geometry-passthrough case for the representative shader walkthrough because its identity geometry shader shows the central preservation contract directly.
- Carry the two behavioral groups into `## Behavior Parameters` and copy the failure mapping table unchanged.
- Put the fixed tessellation levels, primitive coverage, tolerance, and omitted quad case in their dedicated page sections rather than in Background Knowledge.
- Retain links to both spec chapters because they ground the stage semantics used in the failure analysis.
