# Understanding Brief: `tessellation.invariance`

## One-Sentence Test Purpose

This test checks the Vulkan tessellator's eight repeatability guarantees by capturing generated tessellation coordinates and comparing the primitive, edge, triangle, and coordinate properties that each rule requires.

## Background Knowledge

### Tessellation invariance

The fixed-function tessellator turns tessellation levels into points, lines, or triangles and assigns a `TessCoord` to each generated vertex. Vulkan does not prescribe every detail of that subdivision, but it does prescribe relationships that must remain stable when an application repeats a patch or changes an input that a particular result must not depend on. Those relationships are the eight tessellation invariance rules ([Tessellation Invariance](../../../../vulkan-docs/src/appendices/invariance.adoc#tessellation-invariance)).

Why it matters here:

- Rules 1 through 7 compare generated primitive or edge sets under controlled changes to levels, winding, point mode, or edge identity.
- Rule 8 constrains each defined `TessCoord` component to `[0, 1]` and requires `1.0 - x` to be exact for values that the tessellator emits.

### Capturing fixed-function output

Tessellation evaluation shader invocations do not have a defined order. The tests that compare complete primitives therefore pass `gl_TessCoord` and `gl_PrimitiveID` to a geometry shader. Each geometry invocation sees one assembled output primitive, assigns it an atomic output slot, and stores the primitive's ordered coordinates in a storage buffer. The host sorts records by patch ID before comparison ([shared shader generation](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L240-L427), [readback](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L735-L760)).

The two rule-8 families need only individual evaluation invocations. Their tessellation evaluation shader writes coordinates, or `x + (1.0 - x)`, directly to a storage buffer ([coordinate shader generation](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2147-L2243)).

## One Concrete Example

Consider `dEQP-VK.tessellation.invariance.inner_triangle_set.triangles_fractional_even_spacing`.

For each base tessellation-level set, the host creates four variants. It preserves the triangle domain's relevant inner level and changes every outer level plus the unused second inner level. Each variant draws two identical patches. The geometry shader records all triangle coordinates. The host first requires the two patches in one draw to match exactly, then removes triangles that touch an outer edge and compares the remaining triangles as unordered sets ([variant generation](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1808-L1835), [inner-triangle predicate and comparison](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1838-L1875)).

A pass means outer-level changes did not alter the interior triangle set. It does not require triangle order or vertex order within a triangle to remain fixed, because rule 6 explicitly allows those orders to differ.

## End-to-End Test Flow

```text
[host] select one invariance family and its registered primitive, spacing, winding, and point-mode values
[host] generate fixed and deterministic-random tessellation-level cases
[host] create a host-visible vertex buffer for levels and a host-visible storage buffer for captured output
[host] generate the required vertex, tessellation-control, tessellation-evaluation, and optional geometry shaders
[host] clear the storage buffer, bind the pipeline and descriptor, and draw one or more patches without attachments
[device] copy the six input levels into gl_TessLevelInner and gl_TessLevelOuter
[device] run the fixed-function tessellator and expose generated gl_TessCoord values
[device] write individual coordinates in rule-8 cases, or assemble and atomically record primitives in the geometry shader
[host] wait, invalidate the storage allocation, and read the count plus captured records
[host] apply the selected family's exact set, symmetry, range, or arithmetic comparison
[host] fail on a missing primitive or the first violated family-specific relation; otherwise continue through all cases
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`addDefaultPrograms()` generates a vertex shader, tessellation control shader, tessellation evaluation variants, and geometry variants. The evaluation layout changes with primitive type, spacing, winding, and point mode. `outer_edge_symmetry` also generates mirrored coordinate output so the host can split each edge into original and reflected halves ([default program generator](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L240-L427)).

The rule-8 path has a separate `initPrograms()`. Its evaluation shader either stores `gl_TessCoord` or computes each defined component as `x + (1.0 - x)` before storage. It emits variants that do or do not write `gl_PointSize`, then selects the supported form at runtime ([rule-8 shaders](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2147-L2243)).

No fragment shader, color attachment, depth attachment, push constant, specialization constant, or generated SPIR-V assembly string participates. The CTS shader toolchain compiles the generated ESSL 3.10 sources.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Host-visible vertex buffer | yes | yes | read | no | Supplies six tessellation levels per patch as scalar vertex attributes. |
| Host-visible result storage buffer | yes | yes, at set 0 binding 0 | written with an atomic count and coordinate records | yes | Carries fixed-function tessellator output to the family-specific host comparator. |
| Attachment-free render pass and `1 x 1` framebuffer | yes | yes | used for draw execution | no | Runs the graphics stages without using rasterized pixels as evidence. |
| Tessellation and geometry stage interfaces | generated interface | yes, through pipeline stages | read and written | no | Preserve `TessCoord`, patch `PrimitiveId`, and vertices grouped by output primitive. |

## What Is Checked

- Geometry-capture draws check that the primitive count is at least the count computed by CTS reference helpers. Rule-8 draws record an invocation count but do not compare it with a reference count. Buffer-capacity assertions in both paths guard the test implementation rather than define a conformance result.
- `primitive_set` compares ordered vertex coordinates within each primitive and treats primitive storage order as irrelevant.
- Edge families filter coordinates to one outer edge, then compare sets across unrelated levels, mirrored halves, or normalized edge-component order.
- Triangle families compare unordered triangle sets. The inner and outer variants filter to the triangles covered by rules 6 and 7.
- `tess_coord_component_range` checks every defined component with an inclusive `[0, 1]` comparison.
- `one_minus_tess_coord_component` checks exact equality of the shader-computed `x + (1.0 - x)` result with `1.0` ([comparators](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1278-L1386), [coordinate checks](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2122-L2145)).

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `primitive_set`, `outer_edge_division`, `outer_edge_symmetry`, `outer_edge_index_independence`, `triangle_set`, `inner_triangle_set`, `outer_triangle_set`, `tess_coord_component_range`, `one_minus_tess_coord_component`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `primitive_set` | The tessellator produced different primitive coordinates for two patches with identical levels and evaluation decorations in one draw. |
| `outer_edge_division` | Edge vertices depended on unrelated inner or outer levels, winding, or point mode instead of only the selected outer level and spacing. |
| `outer_edge_symmetry` | A generated edge coordinate lacked its exact reflected counterpart, or a required triangle/quad endpoint was absent. |
| `outer_edge_index_independence` | Equivalent outer edges generated different normalized coordinate sets for the same outer level and spacing. |
| `triangle_set` | Changing winding changed the triangle set rather than only triangle order and vertex order. |
| `inner_triangle_set` | Changing outer levels, or the irrelevant triangle-domain inner level, changed the unordered set of interior triangles. |
| `outer_triangle_set` | Changing levels unrelated to one selected edge changed the unordered set of triangles connecting that outer edge to its inner edge. |
| `tess_coord_component_range` | The tessellator emitted a defined coordinate component below `0.0` or above `1.0`. |
| `one_minus_tess_coord_component` | The tessellator emitted a coordinate component for which shader evaluation of `x + (1.0 - x)` was not exactly `1.0`. |

Geometry-capture families can also fail if the capture path reports too few primitives. A broad failure across otherwise different geometry-capture families may therefore point to tessellation execution, geometry assembly, storage-buffer writes, synchronization, or host readback rather than to one invariance relation. The rule-8 path does not reject too few invocations.

## Important Variations and Special Cases

- The registered matrix contains 192 Vulkan test case leaves: 36 each for `primitive_set`, `outer_edge_symmetry`, `tess_coord_component_range`, and `one_minus_tess_coord_component`; 24 for `outer_edge_index_independence`; and 6 each for the four triangle/edge families with shorter names ([default mustpass range](../../../mustpass/main/vk-default/tessellation.txt#L35-L226)).
- Triangles, quads, and isolines appear where the corresponding rule applies. Rules 2, 4, 5, 6, and 7 only register triangle and quad cases. Rule 3 and rule 8 also cover isolines.
- All three spacing modes are registered. Winding and point mode appear in names only for families whose rule or observation path includes those dimensions.
- `outer_edge_division` compares ten patches per draw and iterates 12 selected outer levels, including fractional values and `63.0`; unrelated levels come from a deterministic random generator.
- `primitive_set`, `triangle_set`, and the inner/outer triangle families draw two identical patches per comparison. The latter two generate four related level sets for each comparison.
- Portability-subset checks prune unsupported primitive modes or point mode. Runtime feature checks require tessellation plus storage writes; geometry-capture families also require geometry shaders.
- The rule-8 runtime records an invocation count but never compares it with the reference vertex count. It also constructs `tcu::TestStatus::fail(...)` after a bad component without returning it, so the function reaches its final pass status ([rule-8 validation loop](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2381-L2411)). The final wiki should describe the intended component checks and both observed source limitations.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Vulkan tessellation rules | [`invariance.adoc#tessellation-invariance`](../../../../vulkan-docs/src/appendices/invariance.adoc#tessellation-invariance) | Defines the eight required relationships tested by the nine families. |
| Shared program generation | [`addDefaultPrograms()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L240-L427) | Emits level transport, evaluation layouts, mirrored coordinates, and geometry capture. |
| Shared edge draw/readback | [`BaseTestInstance`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L583-L773) | Creates resources, draws patches, synchronizes storage writes, and returns captured primitives. |
| Rules 2, 4, and 3 | [`InvariantOuterEdge`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L775-L1235) | Implements edge division, edge-index independence, and symmetry checks. |
| Primitive and triangle comparators | [`compareTriangleSets()` and `comparePrimitivesExact()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1278-L1386) | Defines ordered primitive and unordered triangle equality. |
| Shared rules 1, 5, 6, and 7 runtime | [`InvarianceTestInstance`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1388-L2024) | Generates level variants, performs duplicate-patch checks, and dispatches family-specific comparisons. |
| Rule-8 shader and runtime | [`TessCoordComponent`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2082-L2428) | Writes and checks coordinate components. |
| Registration | [`createInvarianceTests()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2434-L2513) | Registers all nine families and their parameter matrices. |
| Portability support helper | [`checkSupportCase()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L526-L549) | Rejects unsupported point-mode or primitive combinations under the portability subset. |
| Default mustpass coverage | [`tessellation.txt#L35-L226`](../../../mustpass/main/vk-default/tessellation.txt#L35-L226) | Lists all 192 Vulkan leaves. |

## Questions / Risk Points for User Audit

- Is `test family` the correct behavior parameter? Each direct family maps to one invariance property or one half of rule 8, while primitive and spacing values condition that property.
- Does the explanation distinguish exact ordered primitive comparison from unordered triangle-set and coordinate-set comparison?
- Is the geometry shader described as a capture mechanism rather than part of the tessellation property itself?
- Should the final page call out the absent rule-8 invocation-count check and missing `return` in its component loop? Both affect the observable CTS result and are directly visible in source.

The implementation, specification appendix, generated shader paths, and mustpass list resolve the first three questions. The rule-8 count and result-propagation issues are retained as explicit source limitations because omitting them would overstate what the current code reports.

## Conversion Notes for Final Wiki Rewrite

- Distill the fixed-function invariance model and geometry-capture rationale into short prerequisite bullets.
- Use `dEQP-VK.tessellation.invariance.primitive_set.triangles_fractional_even_spacing_ccw` for one representative tessellation evaluation shader walkthrough. The shader is small, and the variation table can cover mirroring, point mode, primitive type, and the separate rule-8 output path.
- Carry `test family` and all nine values into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table above directly into the final page, including the shared capture-path paragraph.
- Keep the 192-leaf matrix compact by listing dimensions and per-family counts instead of expanding leaves in the registration tree.
- Explain both rule-8 validation limitations in runtime checking, failure analysis, and takeaways without presenting a source fix.
