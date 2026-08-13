## Overview

**Core question:** Does the fixed-function tessellator preserve every primitive, edge, triangle, and coordinate relationship required by Vulkan's eight tessellation invariance rules?

- `vktTessellationInvarianceTests.cpp` implements all nine direct test families under `tessellation.invariance`.
- The tests feed controlled tessellation levels into attachment-free draws and capture generated `TessCoord` values in host-visible storage buffers.
- Seven families compare complete primitives, edge-coordinate sets, or triangle subsets. Two families inspect individual coordinate components.
- The registered matrix has 192 Vulkan test case leaves across triangles, quads, isolines, three spacing modes, both winding orders, and optional point mode where each rule permits them.

## Background Knowledge

For the shared concepts primitive domains, spacing modes, and CTS observables, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- The fixed-function tessellator turns inner and outer tessellation levels into domain coordinates and output primitives. Vulkan leaves parts of this subdivision implementation-dependent, but its [tessellation invariance rules](../../../../vulkan-docs/src/appendices/invariance.adoc#tessellation-invariance) require specific results to remain identical when an application changes inputs that should be irrelevant to them.
- Tessellation evaluation invocations have no useful ordering guarantee for host comparison. A geometry shader can observe one assembled tessellated primitive at a time, preserve its vertex order, and write the primitive to an atomic storage-buffer slot. The host can then recover sets of complete primitives without treating invocation order as evidence.
- A triangle is interior when none of its vertices lies on a patch edge. An outer triangle connects an outer edge to the corresponding inner tessellation region. Rules 6 and 7 apply to these subsets rather than to every generated triangle.

## Registration Hierarchy

```text
tessellation.invariance
├── primitive_set
├── outer_edge_division
├── outer_edge_symmetry
├── outer_edge_index_independence
├── triangle_set
├── inner_triangle_set
├── outer_triangle_set
├── tess_coord_component_range
└── one_minus_tess_coord_component
```

These nine direct children implement rules 1 through 8. Rule 8 is split into range and exact-subtraction families. The default mustpass list contains 192 leaves across the hierarchy ([mustpass entries](../../../mustpass/main/vk-default/tessellation.txt#L35-L226)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `primitive_set`, `outer_edge_division`, `outer_edge_symmetry`, `outer_edge_index_independence`, `triangle_set`, `inner_triangle_set`, `outer_triangle_set`, `tess_coord_component_range`, `one_minus_tess_coord_component` | Selects the invariance rule and comparison relation. This is the primary behavioral axis. | [`createInvarianceTests()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2438-L2513) |
| Primitive type | `triangles`, `quads`, `isolines` | Selects the tessellation domain, defined coordinate components, edge descriptions, and output primitive shape. Families register only the domains covered by their rule. | [`outerEdgeDescriptions()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L429-L495), [registration conditions](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2457-L2500) |
| Spacing mode | `equal_spacing`, `fractional_odd_spacing`, `fractional_even_spacing` | Selects segment rounding and placement. Every family covers all three modes. | [`createInvarianceTests()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2457-L2465) |
| Winding | `ccw`, `cw` | Changes vertex order. It is a leaf dimension for primitive, symmetry, edge-index, and coordinate-component families. `outer_edge_division` varies both programs internally, while `triangle_set`, `inner_triangle_set`, and `outer_triangle_set` compare both winding programs inside each leaf. | [`getWindingCases()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L68-L106), [registration](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2479-L2499) |
| Point mode | omitted, `_point_mode` | Switches output from lines or triangles to points. It appears only where the rule applies to point output or where the same coordinate property remains meaningful. | [`getUsePointModeCases()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L108-L142), [registration](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2479-L2499) |
| Tessellation levels | fixed cases plus deterministic random values | Exercises low, high, integer, and fractional levels. Some families preserve relevant levels while varying irrelevant ones. These values are runtime subcases, not registered names. | [shared level cases](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1456-L1483), [rule-8 cases](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2102-L2120) |

The family sizes show how the registration conditions apply:

| Test family | Leaves | Registered dimensions per family |
|-------------|-------:|----------------------------------|
| `primitive_set` | 36 | 3 primitives x 3 spacing modes x 2 windings x 2 point-mode choices |
| `outer_edge_division` | 6 | 2 area primitives x 3 spacing modes |
| `outer_edge_symmetry` | 36 | 3 primitives x 3 spacing modes x 2 windings x 2 point-mode choices |
| `outer_edge_index_independence` | 24 | 2 area primitives x 3 spacing modes x 2 windings x 2 point-mode choices |
| `triangle_set` | 6 | 2 area primitives x 3 spacing modes |
| `inner_triangle_set` | 6 | 2 area primitives x 3 spacing modes |
| `outer_triangle_set` | 6 | 2 area primitives x 3 spacing modes |
| `tess_coord_component_range` | 36 | 3 primitives x 3 spacing modes x 2 windings x 2 point-mode choices |
| `one_minus_tess_coord_component` | 36 | 3 primitives x 3 spacing modes x 2 windings x 2 point-mode choices |

## Behavior Parameters

The direct test family is the primary behavioral axis. Each family tests one required relationship; the other dimensions apply that relationship to different tessellator configurations.

### `primitive_set`: identical primitive output

This family covers rule 1. It draws two patches with identical levels in one draw and compares their captured primitives. Primitive storage order may differ, but each matched primitive must have the same ordered vertex coordinates ([exact comparator](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1358-L1386), [rule-1 comparison](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1739-L1767)). Because the comparator searches the second collection without consuming matches, it checks neither the specification's primitive-number correspondence nor strict multiset equality when duplicate primitive records exist.

### `outer_edge_division`: edge output depends only on its level and spacing

This family covers rule 2. For each triangle or quad edge and each of 12 selected outer levels, it draws ten patches that preserve the selected edge level while randomizing all other levels. The host extracts coordinates on that edge and requires the same set across patches, winding modes, and point-mode choices ([rule-2 loop](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L775-L879)).

### `outer_edge_symmetry`: reflected edge coordinates occur in pairs

This family covers rule 3 for triangles, quads, and isolines. Its evaluation shader reflects coordinates from one half of each edge onto the other half and marks reflected values in the fourth output component. The host removes permitted special points, checks required triangle and quad endpoints, then compares reflected and unreflected coordinate sets exactly ([mirroring generator](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L293-L337), [symmetry check](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L986-L1115)).

### `outer_edge_index_independence`: equivalent edges subdivide alike

This family covers rule 4 for triangles and quads. It applies the same selected outer level to each edge in turn, extracts that edge's coordinates, and swizzles them into the first edge's component order. All normalized sets must match ([rule-4 comparison](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L881-L984)).

### `triangle_set`: winding changes order, not membership

This family covers rule 5. It runs clockwise and counter-clockwise evaluation programs with the same levels, then compares unordered sets of triangles. Before insertion into a set, the host sorts the three coordinates within each triangle, so triangle order and vertex order do not affect equality ([triangle-set comparator](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1278-L1355), [rule-5 class](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1769-L1791)).

### `inner_triangle_set`: outer levels do not alter interior triangles

This family covers rule 6. Each level case has four variants that keep the relevant inner levels fixed while changing outer levels and, for triangles, the unused second inner level. The host excludes every triangle that touches a patch edge and compares the remaining unordered sets ([variant generation and predicates](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1793-L1876)).

### `outer_triangle_set`: one edge region ignores unrelated levels

This family covers rule 7. For each edge, it keeps that edge's outer level and the corresponding inner level fixed while varying other outer levels. The host selects triangles that connect the chosen outer edge to its inner region and compares only that subset ([rule-7 level variants and comparison](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1878-L2024)).

### `tess_coord_component_range`: defined components stay in range

This family covers the range half of rule 8. The evaluation shader writes each generated `gl_TessCoord` to storage. The host checks three components for triangles and two for quads or isolines, requiring every checked value to lie in the inclusive range `[0, 1]` ([range comparator](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2124-L2133), [shader branch](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2189-L2206)).

### `one_minus_tess_coord_component`: subtraction from one is exact

This family covers the exactness half of rule 8. For every defined component `x`, the evaluation shader computes a temporary `1.0 - x`, adds it back to `x`, and stores the result. The intended host check requires exact equality with `1.0` ([exactness comparator](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2135-L2145), [generated arithmetic](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2193-L2205)).

## Shader Analysis

The representative shader is the ordinary evaluation path used to capture unmodified tessellation coordinates for rules 1, 2, 4, 5, 6, and 7. It isolates the fixed-function output that those families compare. The geometry capture stage and rule-8 direct-write path are summarized after the code because their differences do not require separate walkthroughs.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.invariance.primitive_set.triangles_fractional_even_spacing_ccw
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `primitive_set` | Compares the complete generated primitive representation required by rule 1. |
| `triangles` | Uses three-component barycentric `gl_TessCoord` values and triangle output. |
| `fractional_even_spacing` | Selects the fractional-even subdivision rule. |
| `ccw`, point mode omitted | Uses counter-clockwise triangle output rather than point output. |

#### Purpose

The shader exposes each generated `gl_TessCoord` and patch `gl_PrimitiveID` to the geometry stage without transforming them. The host can then determine whether the two identical patches produced identical primitives.

#### Structural Design

| Shader operation | Captured fact | Role in validation |
|------------------|---------------|--------------------|
| Declare triangle, fractional-even, counter-clockwise evaluation | The selected fixed-function tessellation configuration | Anchors the result to the registered leaf. |
| Copy `gl_TessCoord` into the interface block | Exact generated domain coordinate | Supplies every coordinate later compared by the host. |
| Copy `gl_PrimitiveID` into the interface block | Source patch identity | Lets the host sort geometry records and split duplicate patches. |

#### Shader Code

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require

/// This leaf evaluates a triangle domain with fractional-even spacing and counter-clockwise output.
layout(triangles, fractional_even_spacing, ccw) in;

/// The geometry stage receives each generated coordinate together with its source patch ID.
layout(location = 0) out VertexData {
    vec4 in_gs_tessCoord;
    int  in_gs_primitiveID;
} ib_out;

void main (void)
{
    /// Preserve the fixed-function tessellator coordinate exactly for capture and host comparison.
    ib_out.in_gs_tessCoord   = vec4(gl_TessCoord, 0.0);
    ib_out.in_gs_primitiveID = gl_PrimitiveID;
}
```

#### Additional Info

- The fixed tessellation control shader reads six scalar attributes per patch and assigns them to the two inner and four outer tessellation levels.
- The geometry shader atomically appends one `PerPrimitive` record per assembled output primitive. It preserves vertex order within each record and writes dummy positions only to complete the graphics stage ([geometry generator](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L369-L425)).
- No explicit `vk::ShaderBuildOptions` changes the source collection target, so this walkthrough uses the baseline SPIR-V 1.0 target.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Primitive type | `quads` changes the domain layout and uses two defined coordinate components; `isolines` changes the domain and geometry input shape. | [`addDefaultPrograms()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L339-L425) |
| Spacing mode | Replaces `fractional_even_spacing` with `equal_spacing` or `fractional_odd_spacing` in the layout. | [`addDefaultPrograms()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L347-L366) |
| Winding and point mode | Replaces `ccw` with `cw`; point leaves add `point_mode` and select point geometry capture. | [`addDefaultPrograms()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L339-L425) |
| `outer_edge_symmetry` | Replaces the direct coordinate copy with primitive-specific reflection logic and uses `.w` as a reflected-half marker. | [mirroring branch](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L293-L337) |
| Rule-8 families | Use a separate evaluation builder with a storage buffer and atomic invocation counter; the shader stores coordinates or `x + (1.0 - x)` directly. | [`TessCoordComponent::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2147-L2243) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tese`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 30
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %ib_out %gl_TessCoord %gl_PrimitiveID
               OpExecutionMode %main Triangles
               OpExecutionMode %main SpacingFractionalEven
               OpExecutionMode %main VertexOrderCcw
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %VertexData "VertexData"
               OpMemberName %VertexData 0 "in_gs_tessCoord"
               OpMemberName %VertexData 1 "in_gs_primitiveID"
               OpName %ib_out "ib_out"
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %gl_PrimitiveID "gl_PrimitiveID"
               OpDecorate %VertexData Block
               OpDecorate %ib_out Location 0
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpDecorate %gl_PrimitiveID BuiltIn PrimitiveId
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
        %int = OpTypeInt 32 1
 %VertexData = OpTypeStruct %v4float %int
%_ptr_Output_VertexData = OpTypePointer Output %VertexData
     %ib_out = OpVariable %_ptr_Output_VertexData Output
      %int_0 = OpConstant %int 0
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_PrimitiveID = OpVariable %_ptr_Input_int Input
%_ptr_Output_int = OpTypePointer Output %int
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpLoad %v3float %gl_TessCoord
         %18 = OpCompositeExtract %float %16 0
         %19 = OpCompositeExtract %float %16 1
         %20 = OpCompositeExtract %float %16 2
         %21 = OpCompositeConstruct %v4float %18 %19 %20 %float_0
         %23 = OpAccessChain %_ptr_Output_v4float %ib_out %int_0
               OpStore %23 %21
         %27 = OpLoad %int %gl_PrimitiveID
         %29 = OpAccessChain %_ptr_Output_int %ib_out %int_1
               OpStore %29 %27
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- [host] Every path places six levels per patch in a host-visible `VK_FORMAT_R32_SFLOAT` vertex buffer. The vertex and control stages forward them into `gl_TessLevelInner[0..1]` and `gl_TessLevelOuter[0..3]`.
- [host] The tests create an attachment-free render pass, a `1 x 1` framebuffer, and one host-visible storage buffer at descriptor set 0 binding 0. They clear the buffer before each draw.
- [device] The fixed-function tessellator generates domain coordinates. Geometry-capture families pass them through the evaluation shader, assemble them into output primitives, and atomically append `PerPrimitive` records from the geometry shader.
- [host] A graphics-to-host buffer barrier follows the draw. After queue completion and memory invalidation, the host reads the atomic count and captured records.
- [host] Geometry-capture paths reject a count below the CTS reference count. They sort records by patch ID, compare two identical patches exactly, then run the selected edge or triangle comparator across program or level variants ([shared runtime](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1485-L1737)).
- [host] Edge rules iterate each applicable outer edge and 12 selected levels. `outer_edge_division` draws ten patches at once; the symmetry and edge-index families draw one patch and compare filtered coordinate sets ([edge runtime](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L775-L1115)).
- [host] Rule-8 paths run 32 deterministic random level sets. Their evaluation shader writes one record per generated vertex, and the host loops over the recorded components ([rule-8 runtime](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2245-L2411)).

The geometry-capture path also has an observable comparison limitation. `comparePrimitivesExact()` searches for each primitive from the first collection anywhere in the second collection and does not mark a match as consumed. This accommodates nondeterministic geometry-shader storage order, but it cannot enforce rule 1's primitive-number correspondence and can accept unequal multisets when duplicate records allow one second-collection record to satisfy more than one search ([exact comparator](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1358-L1386)).

The rule-8 path has two further observable source limitations. It reads the atomic invocation count but never compares it with the reference vertex count, so missing invocations are not detected. On a bad component it constructs `tcu::TestStatus::fail("Invalid tessellation coordinate component")` but does not return that status. The function then reaches its final pass return. The comparator logs a component violation, but this source path does not propagate it into the case result ([validation loop](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2381-L2411)).

## Failure Meaning

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

### Cause Analysis

#### Primitive or triangle repeatability failure

**Possible failure symptoms:** `primitive_set` reports different ordered coordinates for a matched primitive. A triangle family reports a triangle present in one result but absent from the other after its allowed order changes and filtering rules are applied.

**Possible implementation causes:** The tessellator may use an input that the selected invariance rule excludes, or may fail to reproduce coordinates for identical effective inputs. For `triangle_set`, only membership is wrong; winding may legally change triangle and vertex order. For inner and outer subsets, the failure may come from allowing unrelated levels to alter the selected region ([rules 1 and 5 through 7](../../../../vulkan-docs/src/appendices/invariance.adoc#tessellation-invariance)).

#### Outer-edge relation failure

**Possible failure symptoms:** The host logs two unequal edge-coordinate sets, unequal reflected and unreflected halves, or a missing triangle/quad endpoint.

**Possible implementation causes:** Edge subdivision may depend on unrelated levels, fail to place exact reflected partners, or vary by edge identity after coordinate normalization. Which relation failed follows the family: division, symmetry, or edge-index independence ([rules 2 through 4](../../../../vulkan-docs/src/appendices/invariance.adoc#tessellation-invariance)).

#### Coordinate component failure

**Possible failure symptoms:** The comparator logs a component outside `[0, 1]`, an exactness result other than `1.0`, and the offending coordinate. Because the current loop omits a return, these logs do not make the rule-8 case return failure. The path produces no failure symptom when it captures too few invocations because it does not compare the count with a reference.

**Possible implementation causes:** The tessellator may emit a defined component outside the permitted range or a value that does not support the exact `1.0 - x` property required by rule 8. A shader compiler could also lower the generated subtraction/addition differently from the source expression. Source-level investigation is needed to distinguish those paths. The absent count check and missing host return are separate CTS validation defects, not permitted implementation results.

#### Capture or readback failure

**Possible failure symptoms:** Several unrelated families report too few records, malformed primitive groups, or broad mismatches without following one rule, primitive type, or spacing mode.

**Possible implementation causes:** Tessellation or geometry execution may fail to produce the expected minimum work. Geometry assembly, atomic storage writes, the graphics-to-host barrier, memory invalidation, or host parsing may fail to preserve the captured records. A family-specific mismatch alone does not establish a capture-path defect.

## Case Pruning

### Requirement-based pruning

- Every leaf requires `tessellationShader` and `vertexPipelineStoresAndAtomics`. Families that capture assembled primitives also require `geometryShader` ([feature checks](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L666-L667), [shared comparison path](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1485-L1489), [rule-8 path](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2245-L2248)).
- The pipeline selects a geometry or tessellation shader variant that writes `gl_PointSize` only when `shaderTessellationAndGeometryPointSize` is available.
- Under `VK_KHR_portability_subset`, `checkSupportCase()` rejects point mode when `tessellationPointMode` is unavailable and rejects isolines when `tessellationIsolines` is unavailable ([feature predicates](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L410-L435), [case dispatch](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L526-L549)).

### Design-based pruning

- Rules 2, 4, 5, 6, and 7 apply to triangle and quad tessellation, so their families do not register isolines. Rule 3 and both rule-8 families include isolines.
- `outer_edge_division` varies winding and point mode internally, so those dimensions do not appear in its leaf names. The three triangle-set families also compare the required winding or level variants inside each leaf.
- Triangle-set comparisons do not register point mode because their subject is a set of generated triangles.
- The generator registers every combination left after these rule-based exclusions. It does not sample or skip combinations within those matrices.

## Key Takeaways

- The page covers all eight Vulkan tessellation invariance rules; rule 8 is split into two direct test families.
- Geometry capture turns unordered evaluation activity into complete primitive records, while host comparators preserve only the ordering guarantees relevant to each rule.
- Edge and triangle families vary inputs selectively so each comparison can separate relevant tessellation levels from irrelevant ones.
- The shared exact-primitive comparator ignores primitive collection order and does not consume matches, so it cannot validate rule 1's primitive-number correspondence and is not a strict multiset comparison in the presence of duplicates.
- The current rule-8 code neither rejects a short invocation count nor returns its constructed status after a bad component. Those two families therefore miss absent invocations and do not propagate logged component violations into the final case result.
- See `## Failure Meaning` to distinguish a family-specific invariance violation from a shared capture or readback failure.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Tessellation invariance specification | [`invariance.adoc#tessellation-invariance`](../../../../vulkan-docs/src/appendices/invariance.adoc#tessellation-invariance) | Defines rules 1 through 8 and their allowed ordering differences. |
| Program naming and shared generation | [`getProgramName()` and `addDefaultPrograms()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L162-L427) | Emits level transport, evaluation variants, mirrored coordinates, and geometry capture. |
| Edge descriptions | [`outerEdgeDescriptions()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L429-L495) | Maps triangle, quad, and isoline coordinates to their outer edges. |
| Shared edge resources and draw | [`InvariantOuterEdge::BaseTestInstance`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L497-L773) | Creates the storage capture path and returns sorted primitive records. |
| Rules 2, 4, and 3 | [`InvariantOuterEdge` comparisons](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L775-L1235) | Implements edge division, index independence, and symmetry. |
| Primitive and triangle equality | [`compareTriangleSets()` and `comparePrimitivesExact()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1278-L1386) | Defines exact primitive matching and order-independent triangle matching. |
| Shared rules 1, 5, 6, and 7 runtime | [`InvarianceTestInstance`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1388-L1737) | Draws duplicate patches, reads records, and compares program or level variants. |
| Rule-specific triangle comparisons | [`PrimitiveSetInvariance` subclasses](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L1739-L2024) | Selects whole, interior, or edge-connected triangle sets. |
| Rule-8 implementation | [`TessCoordComponent`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2082-L2428) | Generates coordinate checks, reads individual invocations, and contains the result-propagation limitation. |
| Registration matrix | [`createInvarianceTests()`](../../../modules/vulkan/tessellation/vktTessellationInvarianceTests.cpp#L2434-L2513) | Registers all nine families and 192 leaves. |
| Portability checks | [`checkSupportCase()`](../../../modules/vulkan/tessellation/vktTessellationUtil.hpp#L526-L549) | Prunes unsupported primitive and point-mode combinations. |
| Default mustpass entries | [`tessellation.txt#L35-L226`](../../../mustpass/main/vk-default/tessellation.txt#L35-L226) | Confirms the complete Vulkan leaf inventory. |
