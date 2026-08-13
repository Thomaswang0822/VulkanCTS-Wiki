# Understanding Brief: `tessellation.primitive_discard`

## One-Sentence Test Purpose

This test checks whether the fixed-function tessellator discards a patch whenever any outer tessellation level relevant to the selected primitive type is non-positive, while leaving patches with non-positive inner or irrelevant outer levels active.

## Background Knowledge

### Relevant tessellation levels and patch discard

A tessellation control shader writes per-patch inner and outer tessellation levels. The fixed-function tessellator uses those values to subdivide the patch, then invokes the tessellation evaluation shader for generated coordinates. The Vulkan specification requires a patch to be discarded when any **relevant** outer level is less than or equal to zero; a discarded patch generates no primitives and does not execute the tessellation evaluation shader. The relevant set depends on the primitive mode: two outer levels for isolines, three for triangles, and four for quads. Negative inner levels do not discard a patch; they are clamped instead. These rules are stated in [Tessellator Patch Discard](../../../../vulkan-docs/src/chapters/tessellation.adoc#L163-L178).

Why it matters here:
- The test must vary all six supplied levels while deciding validity from only the primitive type's relevant outer subset.
- A white pixel or a tessellation-evaluation invocation from a patch that should be discarded is direct evidence that the discard rule was not applied.
- A surviving patch may legitimately contain a non-positive inner level or, for isolines and triangles, a non-positive unused outer level.

### Tessellation evaluation as an observability point

The tessellation control shader does not discard patches itself. It copies input attributes into `gl_TessLevelInner` and `gl_TessLevelOuter`. The fixed-function tessellator then decides whether to emit coordinates. Each emitted coordinate causes a tessellation evaluation shader invocation, which both increments an SSBO counter and positions output in one patch-sized image cell. Thus, the test observes the tessellator in two ways: rasterized white coverage and the number of evaluation invocations.

Why it matters here:
- Image coverage distinguishes surviving cells from the trailing region assigned to discarded patches.
- The invocation count is a secondary sanity check, not the sole verdict, because duplicate tessellation coordinates need not cause duplicate shader invocations in non-point rendering.

## One Concrete Example

Consider `dEQP-VK.tessellation.primitive_discard.quads_equal_spacing_ccw`.

Each draw patch carries ten scalar attributes:

```text
inner levels:       [3, 4]
outer levels:       [5, 6, -0.42, 8]
cell scale/offset:  [2/27, 2/27, cell_x, cell_y]
```

The tessellation control shader writes the four outer values to `gl_TessLevelOuter`. Because quads use all four outer levels, `-0.42` in the third slot requires the tessellator to discard this patch. Its image cell must stay black, and its tessellation evaluation shader must not increment the invocation counter. If the same tuple were used for isolines, only the first two outer levels would be relevant, so the patch would survive.

This example is conceptual but faithful to [`genAttributes()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L93-L150), which uses base levels `3.0` through `8.0` and invalid choices `-0.42` and `0.0`.

## End-to-End Test Flow

```text
[host] select primitive type, spacing, winding, point mode, and level-set variant
[host] generate 729 ten-float patch tuples in a 27 x 27 image-cell order
[host] place all surviving tuples before the first tuple with an invalid relevant outer level
[host] create the vertex buffer, zeroed invocation-count SSBO, 256 x 256 color image, and readback buffer
[host] build a four-stage graphics pipeline and clear the color image to black
[host] draw 729 patches, each represented by ten one-float control points
[device] vertex and tessellation-control stages transport the six levels plus cell placement
[device] fixed-function tessellator discards patches with a non-positive relevant outer level
[device] tessellation evaluation increments the SSBO once per executed invocation and maps survivors into image cells
[device] fragment shader writes white for generated rasterization
[host] copy the color image, wait for completion, invalidate host-visible allocations, and read both results
[host] reject an invocation count below the reference lower bound when that bound is defined
[host] require white coverage around every surviving patch and black pixels throughout the trailing discarded region
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

[`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L256-L365) generates four GLSL ES 3.10 stages:

- The vertex shader passes one scalar attribute per control point.
- The tessellation control shader assembles ten scalar inputs into two inner levels, four outer levels, and two two-component placement values.
- The tessellation evaluation shader declares the selected primitive type, spacing, winding, and optional `point_mode`; it atomically increments the result counter and maps `gl_TessCoord.xy` into the patch's image cell.
- The fragment shader writes opaque white.
- Point-mode cases have a second tessellation evaluation binary that writes `gl_PointSize` when `shaderTessellationAndGeometryPointSize` is available. Runtime feature state selects the appropriate binary.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex attribute buffer | yes | yes | read | no | Supplies six tessellation levels and four image-cell placement scalars for each patch. |
| Invocation-count SSBO at set 0, binding 0 | yes | yes | atomic write in tessellation evaluation | yes | Shows how many tessellation evaluation invocations occurred. |
| `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | yes, as color attachment | fragment write | indirectly | Starts black; surviving patches render white into assigned cells. |
| Host-visible color readback buffer | yes | transfer destination | transfer write | yes | Receives the 256 x 256 color image for pixel verification. |
| `gl_TessLevelInner` / `gl_TessLevelOuter` | no | no descriptor binding | written by tessellation control, consumed by tessellator | no | Built-in per-patch outputs that drive the behavior under test. |

## What Is Checked

- **Invocation lower bound:** [`expectedVertexCount()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L244-L254) computes a point-mode reference count. The observed SSBO count must not be smaller when the count is checked; extra invocations are logged but accepted.
- **Count exception:** for triangles or quads with fractional-odd spacing and generated inner levels less than or equal to one, the CTS source treats the number of interior vertices as implementation-dependent and does not check the count.
- **Surviving patches:** [`verifyResultImage()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L153-L242) requires at least one white pixel near every patch whose relevant outer levels are positive.
- **Discarded patches:** after the first discarded patch, every pixel in the remaining grid region must stay black.
- **Final result:** the case passes only if the applicable count check does not underflow and image verification succeeds.

## Behavior Parameter Identification

> **Behavior parameter:** `primitive type`
>
> **Candidate values:** `isolines`, `quads`, `triangles`

Primitive type is the primary behavioral axis because it changes which subset of `gl_TessLevelOuter` controls discard: two, four, or three values, respectively. Spacing, winding, and point mode broaden pipeline coverage but do not change the discard predicate.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `isolines` | Incorrect use of the two relevant outer levels, or incorrect execution suppression after isoline patch discard. |
| `quads` | Incorrect use of all four outer levels, or incorrect execution suppression after quad patch discard. |
| `triangles` | Incorrect use of the first three outer levels, or incorrect execution suppression after triangle patch discard. |

All three values also depend on correct transport of the generated levels through the vertex and tessellation control stages, correct image placement and readback, and correct visibility of the tessellation evaluation shader's SSBO writes.

## Important Variations and Special Cases

- The full registration matrix has 44 mustpass test cases: three primitive types, three spacing modes, two winding modes, and point mode on/off, plus eight `_valid_levels` cases for fractional-odd triangles and quads.
- Cases without `_valid_levels` generate all combinations of valid base values, `-0.42`, and `0.0` across six level slots. This exercises non-positive inner levels, irrelevant outer levels, and relevant outer levels in one ordered grid.
- `_valid_levels` cases repeat base values in every slot. They retain a deterministic count baseline for the triangle/quad fractional-odd configurations whose low inner-level vertex count is otherwise implementation-dependent.
- Winding does not change the patch-discard rule. Point mode changes output topology and may select a `gl_PointSize`-writing evaluation shader, but it also leaves the discard predicate unchanged.
- `VK_KHR_portability_subset` may reject isoline or point-mode cases when the matching portability feature is false. The runtime also requires `tessellationShader` and `vertexPipelineStoresAndAtomics`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Case definition and generated tuples | [`CaseDefinition`, `lessThanOneInnerLevelsDefined()`, and `genAttributes()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L58-L151) | Defines the five registration dimensions and the ordered 729-patch input grid. |
| Image verdict | [`verifyResultImage()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L153-L242) | Defines white-survivor and black-discarded-region checks. |
| Generated GLSL | [`initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L256-L365) | Shows level transport, invocation counting, placement, and white output. |
| Host execution and result checks | [`test()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L367-L615) | Defines features, resources, draw, barriers, readback, count handling, and final result. |
| Registration | [`createPrimitiveDiscardTests()`](../../../modules/vulkan/tessellation/vktTessellationPrimitiveDiscardTests.cpp#L619-L655) | Generates exact test case leaves and prunes redundant `_valid_levels` combinations. |
| Relevant-outer predicate | [`numOuterTessellationLevels()` and `isPatchDiscarded()`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L433-L456) | Encodes the two/three/four-level reference decision used by host verification. |
| Feature and portability checks | [`checkSupportCase()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L525-L550), [`requireFeatures()`](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L802-L824) | Explains unsupported-case handling. |
| Vulkan semantics | [Tessellator Patch Discard](../../../../vulkan-docs/src/chapters/tessellation.adoc#L163-L178), [Tessellator Spacing](../../../../vulkan-docs/src/chapters/tessellation.adoc#L181-L228) | Grounds discard, relevant-level, inner-level, and fractional-odd behavior. |
| Mustpass inventory | [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L344-L387) | Confirms all 44 Vulkan test paths. |

## Questions / Risk Points for User Audit

- Is primitive type the clearest primary behavioral axis, given that it alone changes the relevant outer-level set?
- Is the distinction between a discarded patch and a surviving patch with invalid inner or irrelevant outer levels explicit enough?
- Is the invocation count correctly presented as a lower-bound sanity check rather than an exact verdict in every case?
- Is the purpose of the `_valid_levels` cases clear without implying that they directly exercise discard?
- Does the resource table make the built-in tessellation levels distinct from host-created buffers?

No unresolved source/spec/mustpass risk changes the test purpose, representative shader choice, or validation claims.

## Conversion Notes for Final Wiki Rewrite

- Distill the patch-discard rule and evaluation-stage observability into two short Background Knowledge bullets.
- Use `quads_equal_spacing_ccw` for the representative shader walkthrough because all four outer levels are relevant and the case avoids point-mode-specific shader variation.
- Keep the full 44-leaf registration tree because every child is a mustpass case and the canonical hierarchy requires exactly one level below `tessellation.primitive_discard`.
- Carry `primitive type` and the values `isolines`, `quads`, and `triangles` into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table above unchanged into the final page, then write a fresh cause analysis.
- Keep source navigation in the appendix; retain the flow and resource facts as compact runtime prose rather than copying this brief verbatim.
