## Overview

**Core question:** does the implementation clip primitives correctly against the fixed clip volume, apply depth clamp and explicit depth clip as configured, honor shader-written `gl_ClipDistance[]` and `gl_CullDistance[]` half-spaces across shader stages, and preserve clip-distance complementarity?

This page covers the entire `clipping` test category, implemented in one source file: [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1). That file registers four test families under the `clipping` test category:

- `clip_volume`: fixed clip-volume behavior for 10 primitive topologies at depth positions inside, outside, straddling (depth clamp), and with explicit depth clip control. Also covers large-point and wide-line clipping.
- `user_defined`: shader-defined `gl_ClipDistance[]` and `gl_CullDistance[]` across clip/cull counts (1-8), static versus dynamic indexing, four shader-stage combinations (vert, vert_tess, vert_geom, vert_tess_geom), and optional fragment-shader readback.
- `complementarity`: complementary clip-distance signs verified through additive blending on a 128x128 framebuffer.
- `misc`: a single cull-distance half-space corner case where no shared negative half-space exists.

The tests rely entirely on rendered image evidence. Pass/fail decisions come from pixel counting, color-range matching, reference-image comparison, and threshold checks, not API return values.

## Background Knowledge

- **Clip volume and primitive clipping.** After vertex processing, the GPU clips each primitive against the half-space clip volume defined by the viewport and depth range. Primitives fully inside are drawn; primitives fully outside are discarded; primitives intersecting a boundary are cut so only the inside portion remains. The depth range defines near and far clip planes at `z=0` and `z=1` in clip-space depth. The `clip_volume` family tests this fixed-function behavior with controlled vertex depth values.

- **Depth clamp.** When `depthClampEnable` is set in pipeline state, fragments whose depth would fall outside `[0,1]` are clamped to the nearest bound instead of being clipped. This lets primitives that straddle the near or far plane still render in the region that would otherwise be empty. The `depth_clamp` cases toggle this state for primitives intersecting near (`z=-0.5`) and far (`z=0.5` with slope) clip planes.

- **Explicit depth clip control (`VK_EXT_depth_clip_enable`).** This extension decouples depth clamp from depth clipping. `depthClipEnable=true` clips primitives outside the depth range even when depth clamp is also enabled. The `depth_clip` cases test both with depth clamp disabled and with depth clamp enabled, isolating the two behaviors that are normally linked.

- **User-defined clip and cull distances.** Shaders declare `gl_ClipDistance[]` and `gl_CullDistance[]` arrays as `gl_PerVertex` built-ins. Each component defines a half-space: a negative value means the vertex is outside that half-space. If all vertices of a primitive have negative `gl_ClipDistance[i]`, the primitive is clipped (cut) against that plane. If all vertices have negative `gl_CullDistance[i]`, the primitive is culled entirely (no rasterization). Fragment shaders can read interpolated distance values. The `user_defined` family exercises these arrays across indexing modes, shader stages, and counts.

- **Clip-distance complementarity.** If two identical primitive sets have opposite `gl_ClipDistance` signs, the clipped regions of one set should exactly fill the gaps left by the other. With additive blending, both sets together should produce a uniform half-intensity image with no gaps (black pixels) or overlaps (white pixels). The `complementarity` family tests this property.

## Registration Hierarchy

```text
clipping
├── clip_volume
├── user_defined
├── complementarity
└── misc
```

All four test families are implemented in [`vktClippingTests.cpp`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1952). There are no delegated registration-only families.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Render size | `RENDER_SIZE = 16` (16x16), `RENDER_SIZE_LARGE = 128` (128x128) | Most families use 16x16. Complementarity uses 128x128 to accommodate its blending pattern across 16 sections. | [`TestConstants`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L51-L60) |
| Clip-volume topologies | `point_list`, `line_list`, `line_list_with_adjacency`, `line_strip`, `line_strip_with_adjacency`, `triangle_list`, `triangle_list_with_adjacency`, `triangle_strip`, `triangle_strip_with_adjacency`, `triangle_fan` | Cross-cutting dimension for inside, outside, depth_clamp, and depth_clip. Adjacency topologies require geometry shader support. | [`cases[]`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1766-L1777) |
| Clip-volume z positions | Inside: `0.0`, `0.5`, `1.0`. Outside: `-0.5`, `1.5`. Depth clamp/clip: `-0.5` (near) and `0.5` with slope=1.0 (far). | Controls whether primitives are fully inside, fully outside, or straddling a clip plane. | [`testPrimitivesInside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L488-L505), [`testPrimitivesOutside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L537-L550) |
| Depth clamp toggle | `depthClampEnable = false/true` | Disabled: straddling portion is clipped away. Enabled: straddling portion is clamped and rendered in a distinct color. | [`testPrimitivesDepthClamp()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L595-L611) |
| Depth clip toggle | `depthClipEnable = false/true`, tested with depth clamp both disabled and enabled | Separates depth clip from depth clamp using `VK_EXT_depth_clip_enable`. | [`testPrimitivesDepthClip()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L694-L810) |
| Wide-line orientation | `LINE_ORIENTATION_AXIS_ALIGNED`, `LINE_ORIENTATION_DIAGONAL` | Lines placed just outside the clip volume in axis-aligned or diagonal directions. | [`LineOrientation`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L330-L335) |
| Clip/cull distance counts | Clip: 1-8. Cull: `min(8, 8 - numClipPlanes)`. Combined max: 8. | Controls how many half-spaces the shader writes. Cull count decreases as clip count increases. | [`TestConstants`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L56-L60), [registration](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1897-L1910) |
| Indexing mode | Static indexing, dynamic loop indexing | Static: each `gl_ClipDistance[i]` assigned individually. Dynamic: loop with runtime index. Selected by `_dynamic_index` suffix. | [`initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1146-L1186) |
| Shader-stage path | `vert`, `vert_tess`, `vert_geom`, `vert_tess_geom` | Tests clip/cull distance propagation through optional tessellation and geometry stages. | [`shaderMask`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1887-L1895) |
| Fragment shader readback | Empty suffix, `_fragmentshader_read` | Without: fragment shader ignores distance arrays. With: fragment shader reads interpolated midpoint distance values into color channels. | [`fragmentShaderReads[]`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1867-L1874) |
| Complementarity clip count | Case names `1` through `8` | Number of enabled `gl_ClipDistance[]` components; only the last is assigned from `v_position.w`. | [registration](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1932-L1936) |

## Behavior Parameters

The primary behavioral axis is the test family. Each family tests a distinct clipping property.

### clip_volume: fixed clip-volume behavior

Tests whether the fixed-function clipper handles primitives correctly for each topology at controlled depth positions. The family has five intermediate nodes:

- **inside:** draws primitives at three depth values (`z=0.0`, `0.5`, `1.0`) and requires enough non-black pixels for the topology. Triangle topologies must fill the entire render area; line topologies allow some error margin; points require their specific pixel count ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L451-L527)).
- **outside:** draws primitives at `z=-0.5` and `z=1.5` and requires every pixel to remain black, confirming that primitives fully outside the clip volume are completely discarded ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L530-L576)).
- **depth_clamp:** draws primitives straddling near and far clip planes with `depthClampEnable` toggled on and off. With clamp disabled, the straddling portion is clipped (black); with clamp enabled, the straddling portion is clamped and rendered in red (near) or yellow (far). Each sub-case checks colored-pixel counts in half-frame regions against topology-specific minimums ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L585-L673)).
- **depth_clip:** uses `VK_EXT_depth_clip_enable` to explicitly enable or disable depth clipping, independent of depth clamp. Tests two passes: first with depth clamp disabled, then with depth clamp enabled. When `depthClipEnable=true`, straddling portions are clipped even if depth clamp is on ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L684-L815)).
- **clipped:** contains three test case leaves. `large_points` draws points just outside the clip volume with a point size nearly the size of the framebuffer and accepts either all-black output or all points rendered, depending on the reported `VK_KHR_maintenance2` point clipping behavior ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L823-L904)). `wide_lines_axis_aligned` and `wide_lines_diagonal` draw wide lines just outside the clip volume and either accept all-black output or compare against a reference rasterization of expanded line quads using `tcu::intThresholdCompare()` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L961-L1081)).

### user_defined: shader clip and cull distances

Tests shader-written `gl_ClipDistance[]` and `gl_CullDistance[]` across a generated matrix. The vertex shader assigns clip distances from `v_position.y` using a bar-based scheme: 8 vertical bars are drawn, and `gl_ClipDistance[barNdx]` receives `v_position.y` for bar `barNdx`, making the upper half of each bar negative (clipped). Cull distances are assigned from position thresholds ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1130-L1186)).

The test instance draws all 8 bars, counts black pixels, and checks three conditions: (1) the exact expected black-pixel count from clip and cull regions, (2) zero black guard pixels in the bottom half (detecting corruption), and (3) for `_fragmentshader_read` cases, correct interpolated distance values read back through color channels ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1486-L1553)).

The fragment-shader-readback variant uses sentinel values (0.1f, 0.2f, 0.3f, 0.4f) in the cull distance to detect whether each shader stage correctly passes the value forward or overrides it. The `checkFragColors()` helper verifies the expected sentinel chain: vertex writes 0.1f, tessellation control transforms it to 0.2f or 0.3f, and geometry transforms it to 0.4f if the chain is broken ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L274-L319)).

### complementarity: complementary clip-distance signs

Generates two identical primitive sets on a 128x128 framebuffer. The first set uses random clip distances from `v_position.w`; the second uses the negated signs. With additive blending enabled, each pixel should receive exactly one contribution from one set, producing uniform gray (0.5 intensity). The test requires every pixel to match gray within a 0.02 tolerance ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1613-L1679)).

### misc: cull-distance half-space corner case

Tests a triangle strip where each of three vertices has one negative `gl_CullDistance` component, but no single half-space is negative for all vertices. Per the Vulkan specification, a primitive is culled only when all vertices share a negative `gl_CullDistance[i]` for some `i`. The test expects the triangle to be drawn and fill exactly half (128 out of 256) of the 16x16 framebuffer with red ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1726-L1753)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.clipping.user_defined.clip_cull_distance_dynamic_index.vert_tess_geom.4_4_fragmentshader_read
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `clip_cull_distance_dynamic_index` | Generates both built-in arrays and accesses their four components through runtime loop indices. |
| `vert_tess_geom` | Runs the distance data through vertex, tessellation-control, tessellation-evaluation, and geometry stages before rasterization. |
| `4_4` | Uses four clip plus four cull distances, reaching the required combined-distance minimum of eight. |
| `_fragmentshader_read` | Declares both arrays as fragment inputs and exposes component 2 in the green and blue color channels. |

#### Purpose

This case verifies dynamically indexed `gl_ClipDistance[4]` and `gl_CullDistance[4]` generation, propagation through tessellation and geometry, fixed-function clipping/culling, and fragment-stage interpolation/readback. Its sentinel chain makes a broken producer stage visible as an incorrect blue channel rather than only as missing coverage.

#### Structural Design

| Stage | Distance-array responsibility | Observable effect |
|-------|-------------------------------|-------------------|
| Vertex | Writes bar-selective clip values and `0.1` cull sentinels. | Establishes dynamic indexing and the producer value checked downstream. |
| Tessellation control | Copies clip values and changes valid cull sentinels from `0.1` to `0.3` (`0.2` on mismatch). | Confirms per-control-point transport into tessellation. |
| Tessellation evaluation | Barycentrically evaluates position, clip, and cull arrays. | Supplies interpolated per-vertex values to geometry without adding subdivision. |
| Geometry | Copies clip values and converts valid `0.3` cull sentinels to `-0.5` below `y=0` or `+0.5` above it (`0.4` on mismatch). | Produces the final clipping/culling half-spaces and the primary stage audited in SPIR-V. |
| Fragment | Reads `gl_ClipDistance[2]` and `gl_CullDistance[2]`. | Encodes them into green/blue for `checkFragColors()`. |

#### Shader Code

##### Vertex Shader

```glsl
#version 450

/// Each draw vertex belongs to one of eight six-vertex bars; color transports the bar gradient.
layout(location = 0) in  vec4 v_position;
layout(location = 0) out vec4 out_color;

/// Four clip and four cull components exactly fill the required combined-distance minimum of eight.
out gl_PerVertex {
    vec4  gl_Position;
    float gl_ClipDistance[4];
    float gl_CullDistance[4];
};

void main (void)
{
    gl_Position = v_position;
    out_color   = vec4(1.0, 0.5 * (v_position.x + 1.0), 0.0, 1.0);

    /// Dynamic loop indices exercise runtime indexing of both built-in distance arrays.
    const int barNdx = gl_VertexIndex / 6;
    for (int i = 0; i < 4; ++i)
        gl_ClipDistance[i] = (barNdx == i ? v_position.y : 0.0);
    /// The 0.1 sentinel must become 0.3 in TCS and a signed half-space in geometry.
    for (int i = 0; i < 4; ++i)
        gl_CullDistance[i] = 0.1f;
}
```

##### Tessellation Control Shader

```glsl
#version 450

/// Three invocations forward one triangle patch and keep tessellation at a single triangle.
layout(vertices = 3) out;

layout(location = 0) in  vec4 in_color[];
layout(location = 0) out vec4 out_color[];

in gl_PerVertex {
    vec4  gl_Position;
    float gl_ClipDistance[4];
    float gl_CullDistance[4];
} gl_in[gl_MaxPatchVertices];

out gl_PerVertex {
    vec4  gl_Position;
    float gl_ClipDistance[4];
    float gl_CullDistance[4];
} gl_out[];

void main (void)
{
    /// Unit tessellation levels avoid subdivision while still exercising TCS/TES transport.
    gl_TessLevelInner[0] = 1.0;
    gl_TessLevelInner[1] = 1.0;

    gl_TessLevelOuter[0] = 1.0;
    gl_TessLevelOuter[1] = 1.0;
    gl_TessLevelOuter[2] = 1.0;
    gl_TessLevelOuter[3] = 1.0;

    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
    out_color[gl_InvocationID]          = in_color[gl_InvocationID];

    /// Clip distances pass through; dynamic indexing remains visible in this stage.
    for (int i = 0; i < 4; ++i)
        gl_out[gl_InvocationID].gl_ClipDistance[i] = gl_in[gl_InvocationID].gl_ClipDistance[i];
    /// Correct vertex input (0.1) becomes 0.3 for the following geometry-stage check; 0.2 flags failure.
    for (int i = 0; i < 4; ++i)
    {
        gl_out[gl_InvocationID].gl_CullDistance[i] = (gl_in[gl_InvocationID].gl_CullDistance[i] == 0.1f) ? 0.3f : 0.2f;
    }
}
```

##### Tessellation Evaluation Shader

```glsl
#version 450

/// Barycentric triangle evaluation reconstructs every per-vertex output for the geometry stage.
layout(triangles, equal_spacing, ccw) in;

layout(location = 0) in  vec4 in_color[];
layout(location = 0) out vec4 out_color;

in gl_PerVertex {
    vec4  gl_Position;
    float gl_ClipDistance[4];
    float gl_CullDistance[4];
} gl_in[gl_MaxPatchVertices];

out gl_PerVertex {
    vec4  gl_Position;
    float gl_ClipDistance[4];
    float gl_CullDistance[4];
};

void main (void)
{
    /// Position and color are evaluated from the three control points.
    vec3 px     = gl_TessCoord.x * gl_in[0].gl_Position.xyz;
    vec3 py     = gl_TessCoord.y * gl_in[1].gl_Position.xyz;
    vec3 pz     = gl_TessCoord.z * gl_in[2].gl_Position.xyz;
    gl_Position = vec4(px + py + pz, 1.0);
    out_color   = (in_color[0] + in_color[1] + in_color[2]) / 3.0;

    /// Both built-in arrays are barycentrically interpolated with dynamic indices.
    for (int i = 0; i < 4; ++i)
        gl_ClipDistance[i] = gl_TessCoord.x * gl_in[0].gl_ClipDistance[i]
                           + gl_TessCoord.y * gl_in[1].gl_ClipDistance[i]
                           + gl_TessCoord.z * gl_in[2].gl_ClipDistance[i];
    for (int i = 0; i < 4; ++i)
        gl_CullDistance[i] = gl_TessCoord.x * gl_in[0].gl_CullDistance[i]
                           + gl_TessCoord.y * gl_in[1].gl_CullDistance[i]
                           + gl_TessCoord.z * gl_in[2].gl_CullDistance[i];
}
```

##### Geometry Shader

```glsl
#version 450

/// One input triangle is re-emitted as a three-vertex strip, preserving primitive shape.
layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

layout(location = 0) in  vec4 in_color[];
layout(location = 0) out vec4 out_color;

in gl_PerVertex {
    vec4  gl_Position;
    float gl_ClipDistance[4];
    float gl_CullDistance[4];
} gl_in[];

out gl_PerVertex {
    vec4  gl_Position;
    float gl_ClipDistance[4];
    float gl_CullDistance[4];
};

void main (void)
{
    /// For each source vertex, copy position/clip values and finalize the cull half-space.
    gl_Position = gl_in[0].gl_Position;
    out_color   = in_color[0];
    for (int i = 0; i < 4; ++i)
        gl_ClipDistance[i] = gl_in[0].gl_ClipDistance[i];
    for (int i = 0; i < 4; ++i)
    {
        /// The expected 0.3 sentinel becomes -0.5 below y=0 or +0.5 above; 0.4 exposes bad transport.
        gl_CullDistance[i] = (gl_in[0].gl_CullDistance[i] == 0.3f) ? ((gl_in[0].gl_Position.y < 0) ? -0.5f : 0.5f) : 0.4f;
    }
    EmitVertex();

    gl_Position = gl_in[1].gl_Position;
    out_color   = in_color[1];
    for (int i = 0; i < 4; ++i)
        gl_ClipDistance[i] = gl_in[1].gl_ClipDistance[i];
    for (int i = 0; i < 4; ++i)
    {
        gl_CullDistance[i] = (gl_in[1].gl_CullDistance[i] == 0.3f) ? ((gl_in[1].gl_Position.y < 0) ? -0.5f : 0.5f) : 0.4f;
    }
    EmitVertex();

    gl_Position = gl_in[2].gl_Position;
    out_color   = in_color[2];
    for (int i = 0; i < 4; ++i)
        gl_ClipDistance[i] = gl_in[2].gl_ClipDistance[i];
    for (int i = 0; i < 4; ++i)
    {
        gl_CullDistance[i] = (gl_in[2].gl_CullDistance[i] == 0.3f) ? ((gl_in[2].gl_Position.y < 0) ? -0.5f : 0.5f) : 0.4f;
    }
    EmitVertex();
}
```

##### Fragment Shader

```glsl
#version 450

/// Flat color supplies red; interpolated built-ins supply the green/blue validation channels.
layout(location = 0) in flat vec4 in_color;
layout(location = 0) out vec4 o_color;
in float gl_ClipDistance[4];
in float gl_CullDistance[4];

void main (void)
{
    /// Read the midpoint components: clip[2] into green and cull[2] into blue.
    o_color = vec4(in_color.r, gl_ClipDistance[2], gl_CullDistance[2],  1.0);
}
```

#### Additional Info

- The vertex shader is the initial producer of four clip values and four `0.1` cull sentinels; the tessellation-control and tessellation-evaluation shaders preserve those dynamically indexed values through a unit-tessellation triangle patch ([vertex source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1130-L1190), [tessellation source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1192-L1327)).
- The fragment shader varies only with `_fragmentshader_read` and distance counts; here it reads midpoint component 2 from each four-element array, while `checkFragColors()` compares the rendered channels with interpolated expectations using a `0.01` tolerance ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1410-L1447), [runtime check](../../../modules/vulkan/clipping/vktClippingTests.cpp#L274-L319)).
- The geometry shader is the primary shader because it performs the final sentinel check and emits the final clip/cull arrays. The registered case is present verbatim in [`clipping.txt`](../../../mustpass/main/vk-default/clipping.txt#L172), and runtime uses a three-control-point patch, then requires exact black coverage, zero guard pixels, and successful fragment-color validation ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1487-L1553)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Clip/cull counts | Array extents and loop bounds follow the selected counts; registration caps the combined total at eight and reduces cull count as clip count rises. | [`initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1113-L1128), [registration](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1897-L1919) |
| Indexing mode | Dynamic cases emit loops over variable `i`; static cases unroll assignments with literal array indices. | [`initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1145-L1186) |
| Stage path | `_tess` adds TCS/TES, `_geom` adds geometry, and their combination changes the cull sentinel expected by each downstream stage. | [`initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1192-L1408) |
| Fragment readback | Readback cases declare built-in fragment inputs and write midpoint clip/cull components to green/blue; other cases omit those inputs and add a constant blue component to the transported color. | [`initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1410-L1447) |

#### SPIR-V

##### Vertex Shader

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
; Bound: 81
; Schema: 0
               OpCapability Shader
               OpCapability ClipDistance
               OpCapability CullDistance
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %v_position %out_color %gl_VertexIndex
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 2 "gl_CullDistance"
               OpName %_ ""
               OpName %v_position "v_position"
               OpName %out_color "out_color"
               OpName %barNdx "barNdx"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %i "i"
               OpName %i_0 "i"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 2 BuiltIn CullDistance
               OpDecorate %v_position Location 0
               OpDecorate %out_color Location 0
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%gl_PerVertex = OpTypeStruct %v4float %_arr_float_uint_4 %_arr_float_uint_4
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
 %v_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
  %float_0_5 = OpConstant %float 0.5
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
    %float_0 = OpConstant %float 0
%_ptr_Function_int = OpTypePointer Function %int
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_6 = OpConstant %int 6
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
      %int_1 = OpConstant %int 1
%_ptr_Function_float = OpTypePointer Function %float
     %uint_1 = OpConstant %uint 1
%_ptr_Output_float = OpTypePointer Output %float
      %int_2 = OpConstant %int 2
%float_0_100000001 = OpConstant %float 0.100000001
       %main = OpFunction %void None %3
          %5 = OpLabel
     %barNdx = OpVariable %_ptr_Function_int Function
          %i = OpVariable %_ptr_Function_int Function
         %55 = OpVariable %_ptr_Function_float Function
        %i_0 = OpVariable %_ptr_Function_int Function
         %18 = OpLoad %v4float %v_position
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %26 = OpAccessChain %_ptr_Input_float %v_position %uint_0
         %27 = OpLoad %float %26
         %28 = OpFAdd %float %27 %float_1
         %29 = OpFMul %float %float_0_5 %28
         %31 = OpCompositeConstruct %v4float %float_1 %29 %float_0 %float_1
               OpStore %out_color %31
         %36 = OpLoad %int %gl_VertexIndex
         %38 = OpSDiv %int %36 %int_6
               OpStore %barNdx %38
               OpStore %i %int_0
               OpBranch %40
         %40 = OpLabel
               OpLoopMerge %42 %43 None
               OpBranch %44
         %44 = OpLabel
         %45 = OpLoad %int %i
         %48 = OpSLessThan %bool %45 %int_4
               OpBranchConditional %48 %41 %42
         %41 = OpLabel
         %50 = OpLoad %int %i
         %51 = OpLoad %int %barNdx
         %52 = OpLoad %int %i
         %53 = OpIEqual %bool %51 %52
               OpSelectionMerge %57 None
               OpBranchConditional %53 %56 %61
         %56 = OpLabel
         %59 = OpAccessChain %_ptr_Input_float %v_position %uint_1
         %60 = OpLoad %float %59
               OpStore %55 %60
               OpBranch %57
         %61 = OpLabel
               OpStore %55 %float_0
               OpBranch %57
         %57 = OpLabel
         %62 = OpLoad %float %55
         %64 = OpAccessChain %_ptr_Output_float %_ %int_1 %50
               OpStore %64 %62
               OpBranch %43
         %43 = OpLabel
         %65 = OpLoad %int %i
         %66 = OpIAdd %int %65 %int_1
               OpStore %i %66
               OpBranch %40
         %42 = OpLabel
               OpStore %i_0 %int_0
               OpBranch %68
         %68 = OpLabel
               OpLoopMerge %70 %71 None
               OpBranch %72
         %72 = OpLabel
         %73 = OpLoad %int %i_0
         %74 = OpSLessThan %bool %73 %int_4
               OpBranchConditional %74 %69 %70
         %69 = OpLabel
         %76 = OpLoad %int %i_0
         %78 = OpAccessChain %_ptr_Output_float %_ %int_2 %76
               OpStore %78 %float_0_100000001
               OpBranch %71
         %71 = OpLabel
         %79 = OpLoad %int %i_0
         %80 = OpIAdd %int %79 %int_1
               OpStore %i_0 %80
               OpBranch %68
         %70 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

##### Tessellation Control Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `tesc`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 103
; Schema: 0
               OpCapability Tessellation
               OpCapability ClipDistance
               OpCapability CullDistance
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationControl %main "main" %gl_TessLevelInner %gl_TessLevelOuter %gl_out %gl_InvocationID %gl_in %out_color %in_color
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_TessLevelInner "gl_TessLevelInner"
               OpName %gl_TessLevelOuter "gl_TessLevelOuter"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 2 "gl_CullDistance"
               OpName %gl_out "gl_out"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 2 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpName %i "i"
               OpName %i_0 "i"
               OpDecorate %gl_TessLevelInner BuiltIn TessLevelInner
               OpDecorate %gl_TessLevelInner Patch
               OpDecorate %gl_TessLevelOuter BuiltIn TessLevelOuter
               OpDecorate %gl_TessLevelOuter Patch
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 2 BuiltIn CullDistance
               OpDecorate %gl_InvocationID BuiltIn InvocationId
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn CullDistance
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_float_uint_2 = OpTypeArray %float %uint_2
%_ptr_Output__arr_float_uint_2 = OpTypePointer Output %_arr_float_uint_2
%gl_TessLevelInner = OpVariable %_ptr_Output__arr_float_uint_2 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
      %int_1 = OpConstant %int 1
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Output__arr_float_uint_4 = OpTypePointer Output %_arr_float_uint_4
%gl_TessLevelOuter = OpVariable %_ptr_Output__arr_float_uint_4 Output
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %_arr_float_uint_4 %_arr_float_uint_4
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_uint_3 = OpTypeArray %gl_PerVertex %uint_3
%_ptr_Output__arr_gl_PerVertex_uint_3 = OpTypePointer Output %_arr_gl_PerVertex_uint_3
     %gl_out = OpVariable %_ptr_Output__arr_gl_PerVertex_uint_3 Output
%_ptr_Input_int = OpTypePointer Input %int
%gl_InvocationID = OpVariable %_ptr_Input_int Input
%gl_PerVertex_0 = OpTypeStruct %v4float %_arr_float_uint_4 %_arr_float_uint_4
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%_ptr_Output__arr_v4float_uint_3 = OpTypePointer Output %_arr_v4float_uint_3
  %out_color = OpVariable %_ptr_Output__arr_v4float_uint_3 Output
%_arr_v4float_uint_32 = OpTypeArray %v4float %uint_32
%_ptr_Input__arr_v4float_uint_32 = OpTypePointer Input %_arr_v4float_uint_32
   %in_color = OpVariable %_ptr_Input__arr_v4float_uint_32 Input
%_ptr_Function_int = OpTypePointer Function %int
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
%_ptr_Input_float = OpTypePointer Input %float
%float_0_100000001 = OpConstant %float 0.100000001
%float_0_300000012 = OpConstant %float 0.300000012
%float_0_200000003 = OpConstant %float 0.200000003
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
        %i_0 = OpVariable %_ptr_Function_int Function
         %16 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_0
               OpStore %16 %float_1
         %18 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_1
               OpStore %18 %float_1
         %23 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_0
               OpStore %23 %float_1
         %24 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_1
               OpStore %24 %float_1
         %26 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_2
               OpStore %26 %float_1
         %28 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_3
               OpStore %28 %float_1
         %37 = OpLoad %int %gl_InvocationID
         %43 = OpLoad %int %gl_InvocationID
         %45 = OpAccessChain %_ptr_Input_v4float %gl_in %43 %int_0
         %46 = OpLoad %v4float %45
         %48 = OpAccessChain %_ptr_Output_v4float %gl_out %37 %int_0
               OpStore %48 %46
         %52 = OpLoad %int %gl_InvocationID
         %56 = OpLoad %int %gl_InvocationID
         %57 = OpAccessChain %_ptr_Input_v4float %in_color %56
         %58 = OpLoad %v4float %57
         %59 = OpAccessChain %_ptr_Output_v4float %out_color %52
               OpStore %59 %58
               OpStore %i %int_0
               OpBranch %62
         %62 = OpLabel
               OpLoopMerge %64 %65 None
               OpBranch %66
         %66 = OpLabel
         %67 = OpLoad %int %i
         %70 = OpSLessThan %bool %67 %int_4
               OpBranchConditional %70 %63 %64
         %63 = OpLabel
         %71 = OpLoad %int %gl_InvocationID
         %72 = OpLoad %int %i
         %73 = OpLoad %int %gl_InvocationID
         %74 = OpLoad %int %i
         %76 = OpAccessChain %_ptr_Input_float %gl_in %73 %int_1 %74
         %77 = OpLoad %float %76
         %78 = OpAccessChain %_ptr_Output_float %gl_out %71 %int_1 %72
               OpStore %78 %77
               OpBranch %65
         %65 = OpLabel
         %79 = OpLoad %int %i
         %80 = OpIAdd %int %79 %int_1
               OpStore %i %80
               OpBranch %62
         %64 = OpLabel
               OpStore %i_0 %int_0
               OpBranch %82
         %82 = OpLabel
               OpLoopMerge %84 %85 None
               OpBranch %86
         %86 = OpLabel
         %87 = OpLoad %int %i_0
         %88 = OpSLessThan %bool %87 %int_4
               OpBranchConditional %88 %83 %84
         %83 = OpLabel
         %89 = OpLoad %int %gl_InvocationID
         %90 = OpLoad %int %i_0
         %91 = OpLoad %int %gl_InvocationID
         %92 = OpLoad %int %i_0
         %93 = OpAccessChain %_ptr_Input_float %gl_in %91 %int_2 %92
         %94 = OpLoad %float %93
         %96 = OpFOrdEqual %bool %94 %float_0_100000001
         %99 = OpSelect %float %96 %float_0_300000012 %float_0_200000003
        %100 = OpAccessChain %_ptr_Output_float %gl_out %89 %int_2 %90
               OpStore %100 %99
               OpBranch %85
         %85 = OpLabel
        %101 = OpLoad %int %i_0
        %102 = OpIAdd %int %101 %int_1
               OpStore %i_0 %102
               OpBranch %82
         %84 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

##### Tessellation Evaluation Shader

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
; Bound: 148
; Schema: 0
               OpCapability Tessellation
               OpCapability ClipDistance
               OpCapability CullDistance
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %gl_TessCoord %gl_in %_ %out_color %in_color
               OpExecutionMode %main Triangles
               OpExecutionMode %main SpacingEqual
               OpExecutionMode %main VertexOrderCcw
               OpSource GLSL 450
               OpName %main "main"
               OpName %px "px"
               OpName %gl_TessCoord "gl_TessCoord"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 2 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpName %py "py"
               OpName %pz "pz"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 2 "gl_CullDistance"
               OpName %_ ""
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpName %i "i"
               OpName %i_0 "i"
               OpDecorate %gl_TessCoord BuiltIn TessCoord
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 2 BuiltIn CullDistance
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn CullDistance
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_ptr_Function_v3float = OpTypePointer Function %v3float
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
    %v4float = OpTypeVector %float 4
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%gl_PerVertex = OpTypeStruct %v4float %_arr_float_uint_4 %_arr_float_uint_4
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_uint_32 = OpTypeArray %gl_PerVertex %uint_32
%_ptr_Input__arr_gl_PerVertex_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_uint_32 Input
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
     %uint_1 = OpConstant %uint 1
      %int_1 = OpConstant %int 1
     %uint_2 = OpConstant %uint 2
      %int_2 = OpConstant %int 2
%gl_PerVertex_0 = OpTypeStruct %v4float %_arr_float_uint_4 %_arr_float_uint_4
%_ptr_Output_gl_PerVertex_0 = OpTypePointer Output %gl_PerVertex_0
          %_ = OpVariable %_ptr_Output_gl_PerVertex_0 Output
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
%_arr_v4float_uint_32 = OpTypeArray %v4float %uint_32
%_ptr_Input__arr_v4float_uint_32 = OpTypePointer Input %_arr_v4float_uint_32
   %in_color = OpVariable %_ptr_Input__arr_v4float_uint_32 Input
    %float_3 = OpConstant %float 3
%_ptr_Function_int = OpTypePointer Function %int
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
%_ptr_Output_float = OpTypePointer Output %float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %px = OpVariable %_ptr_Function_v3float Function
         %py = OpVariable %_ptr_Function_v3float Function
         %pz = OpVariable %_ptr_Function_v3float Function
          %i = OpVariable %_ptr_Function_int Function
        %i_0 = OpVariable %_ptr_Function_int Function
         %15 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %16 = OpLoad %float %15
         %28 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %29 = OpLoad %v4float %28
         %30 = OpVectorShuffle %v3float %29 %29 0 1 2
         %31 = OpVectorTimesScalar %v3float %30 %16
               OpStore %px %31
         %34 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %35 = OpLoad %float %34
         %37 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %38 = OpLoad %v4float %37
         %39 = OpVectorShuffle %v3float %38 %38 0 1 2
         %40 = OpVectorTimesScalar %v3float %39 %35
               OpStore %py %40
         %43 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_2
         %44 = OpLoad %float %43
         %46 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
         %47 = OpLoad %v4float %46
         %48 = OpVectorShuffle %v3float %47 %47 0 1 2
         %49 = OpVectorTimesScalar %v3float %48 %44
               OpStore %pz %49
         %53 = OpLoad %v3float %px
         %54 = OpLoad %v3float %py
         %55 = OpFAdd %v3float %53 %54
         %56 = OpLoad %v3float %pz
         %57 = OpFAdd %v3float %55 %56
         %59 = OpCompositeExtract %float %57 0
         %60 = OpCompositeExtract %float %57 1
         %61 = OpCompositeExtract %float %57 2
         %62 = OpCompositeConstruct %v4float %59 %60 %61 %float_1
         %64 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %64 %62
         %69 = OpAccessChain %_ptr_Input_v4float %in_color %int_0
         %70 = OpLoad %v4float %69
         %71 = OpAccessChain %_ptr_Input_v4float %in_color %int_1
         %72 = OpLoad %v4float %71
         %73 = OpFAdd %v4float %70 %72
         %74 = OpAccessChain %_ptr_Input_v4float %in_color %int_2
         %75 = OpLoad %v4float %74
         %76 = OpFAdd %v4float %73 %75
         %78 = OpCompositeConstruct %v4float %float_3 %float_3 %float_3 %float_3
         %79 = OpFDiv %v4float %76 %78
               OpStore %out_color %79
               OpStore %i %int_0
               OpBranch %82
         %82 = OpLabel
               OpLoopMerge %84 %85 None
               OpBranch %86
         %86 = OpLabel
         %87 = OpLoad %int %i
         %90 = OpSLessThan %bool %87 %int_4
               OpBranchConditional %90 %83 %84
         %83 = OpLabel
         %91 = OpLoad %int %i
         %92 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
         %93 = OpLoad %float %92
         %94 = OpLoad %int %i
         %95 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_1 %94
         %96 = OpLoad %float %95
         %97 = OpFMul %float %93 %96
         %98 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
         %99 = OpLoad %float %98
        %100 = OpLoad %int %i
        %101 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_1 %100
        %102 = OpLoad %float %101
        %103 = OpFMul %float %99 %102
        %104 = OpFAdd %float %97 %103
        %105 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_2
        %106 = OpLoad %float %105
        %107 = OpLoad %int %i
        %108 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_1 %107
        %109 = OpLoad %float %108
        %110 = OpFMul %float %106 %109
        %111 = OpFAdd %float %104 %110
        %113 = OpAccessChain %_ptr_Output_float %_ %int_1 %91
               OpStore %113 %111
               OpBranch %85
         %85 = OpLabel
        %114 = OpLoad %int %i
        %115 = OpIAdd %int %114 %int_1
               OpStore %i %115
               OpBranch %82
         %84 = OpLabel
               OpStore %i_0 %int_0
               OpBranch %117
        %117 = OpLabel
               OpLoopMerge %119 %120 None
               OpBranch %121
        %121 = OpLabel
        %122 = OpLoad %int %i_0
        %123 = OpSLessThan %bool %122 %int_4
               OpBranchConditional %123 %118 %119
        %118 = OpLabel
        %124 = OpLoad %int %i_0
        %125 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_0
        %126 = OpLoad %float %125
        %127 = OpLoad %int %i_0
        %128 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_2 %127
        %129 = OpLoad %float %128
        %130 = OpFMul %float %126 %129
        %131 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_1
        %132 = OpLoad %float %131
        %133 = OpLoad %int %i_0
        %134 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_2 %133
        %135 = OpLoad %float %134
        %136 = OpFMul %float %132 %135
        %137 = OpFAdd %float %130 %136
        %138 = OpAccessChain %_ptr_Input_float %gl_TessCoord %uint_2
        %139 = OpLoad %float %138
        %140 = OpLoad %int %i_0
        %141 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_2 %140
        %142 = OpLoad %float %141
        %143 = OpFMul %float %139 %142
        %144 = OpFAdd %float %137 %143
        %145 = OpAccessChain %_ptr_Output_float %_ %int_2 %124
               OpStore %145 %144
               OpBranch %120
        %120 = OpLabel
        %146 = OpLoad %int %i_0
        %147 = OpIAdd %int %146 %int_1
               OpStore %i_0 %147
               OpBranch %117
        %119 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

##### Geometry Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `geom`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 176
; Schema: 0
               OpCapability Geometry
               OpCapability ClipDistance
               OpCapability CullDistance
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Geometry %main "main" %_ %gl_in %out_color %in_color
               OpExecutionMode %main Triangles
               OpExecutionMode %main Invocations 1
               OpExecutionMode %main OutputTriangleStrip
               OpExecutionMode %main OutputVertices 3
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 2 "gl_CullDistance"
               OpName %_ ""
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpMemberName %gl_PerVertex_0 1 "gl_ClipDistance"
               OpMemberName %gl_PerVertex_0 2 "gl_CullDistance"
               OpName %gl_in "gl_in"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpName %i "i"
               OpName %i_0 "i"
               OpName %i_1 "i"
               OpName %i_2 "i"
               OpName %i_3 "i"
               OpName %i_4 "i"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 2 BuiltIn CullDistance
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex_0 1 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex_0 2 BuiltIn CullDistance
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%gl_PerVertex = OpTypeStruct %v4float %_arr_float_uint_4 %_arr_float_uint_4
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%gl_PerVertex_0 = OpTypeStruct %v4float %_arr_float_uint_4 %_arr_float_uint_4
     %uint_3 = OpConstant %uint 3
%_arr_gl_PerVertex_0_uint_3 = OpTypeArray %gl_PerVertex_0 %uint_3
%_ptr_Input__arr_gl_PerVertex_0_uint_3 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_3
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_3 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
%_arr_v4float_uint_3 = OpTypeArray %v4float %uint_3
%_ptr_Input__arr_v4float_uint_3 = OpTypePointer Input %_arr_v4float_uint_3
   %in_color = OpVariable %_ptr_Input__arr_v4float_uint_3 Input
%_ptr_Function_int = OpTypePointer Function %int
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
      %int_1 = OpConstant %int 1
%_ptr_Input_float = OpTypePointer Input %float
%_ptr_Output_float = OpTypePointer Output %float
      %int_2 = OpConstant %int 2
%float_0_300000012 = OpConstant %float 0.300000012
%_ptr_Function_float = OpTypePointer Function %float
     %uint_1 = OpConstant %uint 1
    %float_0 = OpConstant %float 0
 %float_n0_5 = OpConstant %float -0.5
  %float_0_5 = OpConstant %float 0.5
%float_0_400000006 = OpConstant %float 0.400000006
       %main = OpFunction %void None %3
          %5 = OpLabel
          %i = OpVariable %_ptr_Function_int Function
        %i_0 = OpVariable %_ptr_Function_int Function
         %69 = OpVariable %_ptr_Function_float Function
        %i_1 = OpVariable %_ptr_Function_int Function
        %i_2 = OpVariable %_ptr_Function_int Function
        %119 = OpVariable %_ptr_Function_float Function
        %i_3 = OpVariable %_ptr_Function_int Function
        %i_4 = OpVariable %_ptr_Function_int Function
        %164 = OpVariable %_ptr_Function_float Function
         %22 = OpAccessChain %_ptr_Input_v4float %gl_in %int_0 %int_0
         %23 = OpLoad %v4float %22
         %25 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %25 %23
         %30 = OpAccessChain %_ptr_Input_v4float %in_color %int_0
         %31 = OpLoad %v4float %30
               OpStore %out_color %31
               OpStore %i %int_0
               OpBranch %34
         %34 = OpLabel
               OpLoopMerge %36 %37 None
               OpBranch %38
         %38 = OpLabel
         %39 = OpLoad %int %i
         %42 = OpSLessThan %bool %39 %int_4
               OpBranchConditional %42 %35 %36
         %35 = OpLabel
         %44 = OpLoad %int %i
         %45 = OpLoad %int %i
         %47 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_1 %45
         %48 = OpLoad %float %47
         %50 = OpAccessChain %_ptr_Output_float %_ %int_1 %44
               OpStore %50 %48
               OpBranch %37
         %37 = OpLabel
         %51 = OpLoad %int %i
         %52 = OpIAdd %int %51 %int_1
               OpStore %i %52
               OpBranch %34
         %36 = OpLabel
               OpStore %i_0 %int_0
               OpBranch %54
         %54 = OpLabel
               OpLoopMerge %56 %57 None
               OpBranch %58
         %58 = OpLabel
         %59 = OpLoad %int %i_0
         %60 = OpSLessThan %bool %59 %int_4
               OpBranchConditional %60 %55 %56
         %55 = OpLabel
         %62 = OpLoad %int %i_0
         %63 = OpLoad %int %i_0
         %64 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_2 %63
         %65 = OpLoad %float %64
         %67 = OpFOrdEqual %bool %65 %float_0_300000012
               OpSelectionMerge %71 None
               OpBranchConditional %67 %70 %80
         %70 = OpLabel
         %73 = OpAccessChain %_ptr_Input_float %gl_in %int_0 %int_0 %uint_1
         %74 = OpLoad %float %73
         %76 = OpFOrdLessThan %bool %74 %float_0
         %79 = OpSelect %float %76 %float_n0_5 %float_0_5
               OpStore %69 %79
               OpBranch %71
         %80 = OpLabel
               OpStore %69 %float_0_400000006
               OpBranch %71
         %71 = OpLabel
         %82 = OpLoad %float %69
         %83 = OpAccessChain %_ptr_Output_float %_ %int_2 %62
               OpStore %83 %82
               OpBranch %57
         %57 = OpLabel
         %84 = OpLoad %int %i_0
         %85 = OpIAdd %int %84 %int_1
               OpStore %i_0 %85
               OpBranch %54
         %56 = OpLabel
               OpEmitVertex
         %86 = OpAccessChain %_ptr_Input_v4float %gl_in %int_1 %int_0
         %87 = OpLoad %v4float %86
         %88 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %88 %87
         %89 = OpAccessChain %_ptr_Input_v4float %in_color %int_1
         %90 = OpLoad %v4float %89
               OpStore %out_color %90
               OpStore %i_1 %int_0
               OpBranch %92
         %92 = OpLabel
               OpLoopMerge %94 %95 None
               OpBranch %96
         %96 = OpLabel
         %97 = OpLoad %int %i_1
         %98 = OpSLessThan %bool %97 %int_4
               OpBranchConditional %98 %93 %94
         %93 = OpLabel
         %99 = OpLoad %int %i_1
        %100 = OpLoad %int %i_1
        %101 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_1 %100
        %102 = OpLoad %float %101
        %103 = OpAccessChain %_ptr_Output_float %_ %int_1 %99
               OpStore %103 %102
               OpBranch %95
         %95 = OpLabel
        %104 = OpLoad %int %i_1
        %105 = OpIAdd %int %104 %int_1
               OpStore %i_1 %105
               OpBranch %92
         %94 = OpLabel
               OpStore %i_2 %int_0
               OpBranch %107
        %107 = OpLabel
               OpLoopMerge %109 %110 None
               OpBranch %111
        %111 = OpLabel
        %112 = OpLoad %int %i_2
        %113 = OpSLessThan %bool %112 %int_4
               OpBranchConditional %113 %108 %109
        %108 = OpLabel
        %114 = OpLoad %int %i_2
        %115 = OpLoad %int %i_2
        %116 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_2 %115
        %117 = OpLoad %float %116
        %118 = OpFOrdEqual %bool %117 %float_0_300000012
               OpSelectionMerge %121 None
               OpBranchConditional %118 %120 %126
        %120 = OpLabel
        %122 = OpAccessChain %_ptr_Input_float %gl_in %int_1 %int_0 %uint_1
        %123 = OpLoad %float %122
        %124 = OpFOrdLessThan %bool %123 %float_0
        %125 = OpSelect %float %124 %float_n0_5 %float_0_5
               OpStore %119 %125
               OpBranch %121
        %126 = OpLabel
               OpStore %119 %float_0_400000006
               OpBranch %121
        %121 = OpLabel
        %127 = OpLoad %float %119
        %128 = OpAccessChain %_ptr_Output_float %_ %int_2 %114
               OpStore %128 %127
               OpBranch %110
        %110 = OpLabel
        %129 = OpLoad %int %i_2
        %130 = OpIAdd %int %129 %int_1
               OpStore %i_2 %130
               OpBranch %107
        %109 = OpLabel
               OpEmitVertex
        %131 = OpAccessChain %_ptr_Input_v4float %gl_in %int_2 %int_0
        %132 = OpLoad %v4float %131
        %133 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %133 %132
        %134 = OpAccessChain %_ptr_Input_v4float %in_color %int_2
        %135 = OpLoad %v4float %134
               OpStore %out_color %135
               OpStore %i_3 %int_0
               OpBranch %137
        %137 = OpLabel
               OpLoopMerge %139 %140 None
               OpBranch %141
        %141 = OpLabel
        %142 = OpLoad %int %i_3
        %143 = OpSLessThan %bool %142 %int_4
               OpBranchConditional %143 %138 %139
        %138 = OpLabel
        %144 = OpLoad %int %i_3
        %145 = OpLoad %int %i_3
        %146 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_1 %145
        %147 = OpLoad %float %146
        %148 = OpAccessChain %_ptr_Output_float %_ %int_1 %144
               OpStore %148 %147
               OpBranch %140
        %140 = OpLabel
        %149 = OpLoad %int %i_3
        %150 = OpIAdd %int %149 %int_1
               OpStore %i_3 %150
               OpBranch %137
        %139 = OpLabel
               OpStore %i_4 %int_0
               OpBranch %152
        %152 = OpLabel
               OpLoopMerge %154 %155 None
               OpBranch %156
        %156 = OpLabel
        %157 = OpLoad %int %i_4
        %158 = OpSLessThan %bool %157 %int_4
               OpBranchConditional %158 %153 %154
        %153 = OpLabel
        %159 = OpLoad %int %i_4
        %160 = OpLoad %int %i_4
        %161 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_2 %160
        %162 = OpLoad %float %161
        %163 = OpFOrdEqual %bool %162 %float_0_300000012
               OpSelectionMerge %166 None
               OpBranchConditional %163 %165 %171
        %165 = OpLabel
        %167 = OpAccessChain %_ptr_Input_float %gl_in %int_2 %int_0 %uint_1
        %168 = OpLoad %float %167
        %169 = OpFOrdLessThan %bool %168 %float_0
        %170 = OpSelect %float %169 %float_n0_5 %float_0_5
               OpStore %164 %170
               OpBranch %166
        %171 = OpLabel
               OpStore %164 %float_0_400000006
               OpBranch %166
        %166 = OpLabel
        %172 = OpLoad %float %164
        %173 = OpAccessChain %_ptr_Output_float %_ %int_2 %159
               OpStore %173 %172
               OpBranch %155
        %155 = OpLabel
        %174 = OpLoad %int %i_4
        %175 = OpIAdd %int %174 %int_1
               OpStore %i_4 %175
               OpBranch %152
        %154 = OpLabel
               OpEmitVertex
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 30
; Schema: 0
               OpCapability Shader
               OpCapability ClipDistance
               OpCapability CullDistance
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %o_color %in_color %gl_ClipDistance %gl_CullDistance
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %o_color "o_color"
               OpName %in_color "in_color"
               OpName %gl_ClipDistance "gl_ClipDistance"
               OpName %gl_CullDistance "gl_CullDistance"
               OpDecorate %o_color Location 0
               OpDecorate %in_color Flat
               OpDecorate %in_color Location 0
               OpDecorate %gl_ClipDistance BuiltIn ClipDistance
               OpDecorate %gl_CullDistance BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %o_color = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %in_color = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Input__arr_float_uint_4 = OpTypePointer Input %_arr_float_uint_4
%gl_ClipDistance = OpVariable %_ptr_Input__arr_float_uint_4 Input
        %int = OpTypeInt 32 1
      %int_2 = OpConstant %int 2
%gl_CullDistance = OpVariable %_ptr_Input__arr_float_uint_4 Input
    %float_1 = OpConstant %float 1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpAccessChain %_ptr_Input_float %in_color %uint_0
         %16 = OpLoad %float %15
         %23 = OpAccessChain %_ptr_Input_float %gl_ClipDistance %int_2
         %24 = OpLoad %float %23
         %26 = OpAccessChain %_ptr_Input_float %gl_CullDistance %int_2
         %27 = OpLoad %float %26
         %29 = OpCompositeConstruct %v4float %16 %24 %27 %float_1
               OpStore %o_color %29
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Resource setup and draw

- All families use `VulkanDrawContext` for rendering. The host creates a framebuffer (16x16 for most cases, 128x128 for complementarity), builds a pipeline with the selected state, and submits draw calls with generated vertices ([`genVertices()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L117-L236) for clip_volume, inline vertex construction for user_defined, complementarity, and misc).
- For `user_defined` cases with tessellation, the pipeline sets `numPatchControlPoints = 3` and uses `VK_PRIMITIVE_TOPOLOGY_PATCH_LIST`. Other cases use `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1526-L1528)).
- The `clip_volume` family generates vertices with an optional `slope` parameter. For depth_clamp and depth_clip, slope=1.0 creates a depth gradient across each primitive so it straddles the clip plane ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L654)).

### Result checking

- **inside/outside:** `countPixels()` counts black pixels and compares against topology-specific minimums (inside) or exact full-framebuffer count (outside) ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L507-L527), [`testPrimitivesOutside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L555-L576)).
- **depth_clamp/depth_clip:** `countPixels()` with a region offset and size checks colored-pixel counts in the left half (near plane) or right half (far plane) of the framebuffer against topology-specific thresholds ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L613-L673), [`testPrimitivesDepthClip()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L712-L815)).
- **large_points:** accepts either all-black or all-points-rendered depending on `VK_KHR_maintenance2` point clipping behavior. When `pointClippingOutside` is true (default or `ALL_CLIP_PLANES`), both outcomes pass. When false (`USER_CLIP_PLANES_ONLY`), all points must be rendered ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L894-L904)).
- **wide_lines:** first checks for all-black output (pass). If not all-black, builds a reference image from expanded line quads using the software rasterizer (`ReferenceDrawContext`) and compares with `tcu::intThresholdCompare()` at threshold `UVec4(1)` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1022-L1081)).
- **user_defined:** checks three conditions: exact black-pixel count matching clip plus cull regions, zero guard pixels in the bottom half of the clip region, and for fragment-read cases, `checkFragColors()` verifying interpolated distance values within 0.01 tolerance ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1535-L1553)).
- **complementarity:** counts gray pixels (0.5 +/- 0.02) and requires the full 128x128 framebuffer to match ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1674-L1679)).
- **misc:** counts red pixels (1.0 +/- 0.02) and requires exactly half (128 out of 256) to match ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1745-L1753)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `inside` | Incorrect clip-volume computation for the selected topology or depth value. |
| `outside` | Primitives not fully clipped outside the depth range. |
| `depth_clamp` | Depth clamp not applied or applied incorrectly for the selected depth/clamp combination. |
| `depth_clip` | Explicit depth clip enable/disable not handled correctly. |
| `large_points` | Point clipping behavior inconsistent with reported maintenance2 properties. |
| `wide_lines` | Wide-line clipping or expansion incorrect compared to reference. |
| `user_defined` | Shader clip/cull distance incorrectly written, interpolated, or applied by the clipper. |
| `complementarity` | Clip-distance complementarity violated: gaps or overlaps in blended output. |
| `misc` | Cull-distance culling incorrectly applied when no half-space is negative for all vertices. |

### Cause Analysis

#### Clip-volume or depth handling mismatch

**Possible failure symptoms:** Wrong pixel count in inside, outside, depth clamp, or depth clip cases. For inside, not enough non-black pixels are present. For outside, non-black pixels appear where the framebuffer should be entirely black. For depth clamp/clip, the colored-pixel count in the expected region falls below the topology-specific minimum.

**Possible implementation causes:** The implementation may compute the clip volume incorrectly, handle depth clamp/clip state improperly, or apply topology-specific clipping rules incorrectly. The depth_clip cases with depth clamp enabled specifically test whether `VK_EXT_depth_clip_enable` correctly overrides depth clamp. Source-level investigation is needed to determine whether the failure originates in the fixed-function clipper, the pipeline state configuration, or the rasterizer.

#### Large point or wide line clipping mismatch

**Possible failure symptoms:** For large_points, the output is neither all-black nor all-points-rendered when `pointClippingOutside` is true, or not all points are rendered when `pointClippingOutside` is false. For wide_lines, the output is not all-black and the integer threshold comparison against the reference image fails.

**Possible implementation causes:** The point clipping behavior may be inconsistent with the `VkPointClippingBehavior` reported through `VK_KHR_maintenance2`. For wide lines, the implementation may expand or clip wide lines differently from the reference rasterizer, particularly when `strictLines` is false and the implementation uses a non-perpendicular line expansion algorithm.

#### User-defined distance mismatch

**Possible failure symptoms:** Wrong black-pixel count, non-zero guard pixels in the bottom half of the clip region, or incorrect fragment-read color channels (distance values outside the 0.01 tolerance).

**Possible implementation causes:** The shader may write incorrect distance values, the fixed-function clipper may apply half-space clipping incorrectly, or fragment-stage distance interpolation may be wrong. Dynamic indexing cases isolate indexing-related issues from static ones. The sentinel-value chain in fragment-read cases (0.1f from vertex, 0.2f/0.3f from tessellation control, 0.4f from geometry) pinpoints which shader stage failed to forward the cull distance correctly. Source-level investigation is needed to determine whether the failure is in shader compilation, the clipper, or the interpolator.

#### Complementarity violation

**Possible failure symptoms:** Non-gray pixels in the blended framebuffer. Black pixels indicate gaps where neither primitive set contributed. White pixels indicate overlaps where both sets contributed.

**Possible implementation causes:** The clipper may handle signed clip distances asymmetrically, clipping more or less than expected for one sign. The blend configuration may also interact with clipped primitives incorrectly, though this is less likely since blending is a well-established fixed-function stage.

#### Cull-distance half-space error

**Possible failure symptoms:** The triangle is culled when it should be drawn (all black or too few red pixels), or the triangle is drawn but fills the wrong area (red-pixel count differs from 128).

**Possible implementation causes:** The implementation may cull based on individual vertex cull distances rather than requiring all vertices to share a negative `gl_CullDistance[i]` for some component `i`. This is a specific interpretation error of the cull-distance specification rule. Source-level investigation is needed to confirm whether the implementation applies culling per-vertex or per-half-space.

## Case Pruning

### Requirement-based pruning

- **Depth clamp feature:** `depth_clamp` cases require `features.depthClamp`. Cases are pruned via `NotSupportedError` when the feature is absent ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L579-L583)).
- **`VK_EXT_depth_clip_enable`:** `depth_clip` cases require the extension's `depthClipEnable` feature. The entire `depth_clip` family is pruned when the extension is absent ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L676-L682)).
- **Large points feature:** `large_points` requires `features.largePoints` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L818-L821)).
- **Wide lines feature:** `wide_lines_axis_aligned` and `wide_lines_diagonal` require `features.wideLines` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L956-L959)).
- **Geometry shader for adjacency topologies:** All four clip-volume sub-families (inside, outside, depth_clamp, depth_clip) require geometry shader support for adjacency topologies (`*_with_adjacency`). Cases are pruned via `NotSupportedError` when geometry shaders are unavailable ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L432-L448)).
- **Triangle fan portability subset:** Triangle fan cases are pruned when `VK_KHR_portability_subset` is present without `triangleFans` support ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L416-L430)).
- **Shader clip/cull distance features:** `user_defined` clip-distance cases require `shaderClipDistance`; cull-distance cases additionally require `shaderCullDistance`. Complementarity requires `shaderClipDistance`. Misc requires `shaderCullDistance` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1450-L1467), [complementarity](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1605-L1611), [misc](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1686-L1692)).
- **Tessellation and geometry shader features:** `user_defined` cases with `_tess` require `tessellationShader`; cases with `_geom` require `geometryShader` ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1461-L1464)).
- **Device limits:** `testClipDistance()` fails (not prunes) if reported `maxClipDistances`, `maxCullDistances`, or `maxCombinedClipAndCullDistances` are below the spec minimum of 8 ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1469-L1485)).

### Design-based pruning

- **Combined clip and cull count limit:** For `clip_cull_distance` families, the cull count is computed as `min(MAX_CULL_DISTANCES, MAX_COMBINED_CLIP_AND_CULL_DISTANCES - numClipPlanes)`. When `numClipPlanes = 8`, cull count is 0, so the case name has no cull suffix (e.g., `vert.8` instead of `vert.8_0`). This is a spec-mandated constraint, not an arbitrary exclusion ([source](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1897-L1910)).

## Key Takeaways

- The `clip_volume` family separates five distinct fixed-function clipping behaviors (inside, outside, depth clamp, depth clip, clipped primitives) across 10 topologies, localizing failures to a topology-depth combination.
- The `depth_clip` cases uniquely test the decoupling of depth clamp from depth clipping via `VK_EXT_depth_clip_enable`, including the combination where both are enabled simultaneously.
- The `user_defined` family uses a bar-based vertex shader scheme to create predictable clip regions, and a sentinel-value chain through tessellation and geometry stages to detect which stage fails to forward cull distances.
- The `complementarity` family provides a strong correctness check: any asymmetry in clip-distance sign handling produces visible gaps or overlaps in the blended output.
- The `misc` case catches a specific cull-distance misinterpretation where an implementation culls based on per-vertex negative values instead of requiring a shared negative half-space across all vertices.
- All pass/fail decisions rely on rendered image evidence (pixel counts, color ranges, reference comparison, thresholds), not API return values.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Registration and dispatch | [`addClippingTests()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1758-L1952) | Registers all four test families and their parameter matrices. |
| Feature support helper | [`requireFeatures()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L78-L115) | Maps local feature flags to physical-device feature checks. |
| Test constants | [`TestConstants`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L51-L60) | Render sizes, max clip/cull distances, patch control points. |
| Vertex generation | [`genVertices()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L117-L236) | Generates topology-specific vertices for clip-volume cases. |
| Pixel counting | [`countPixels()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L247-L272) | Shared helper for color-range pixel counting. |
| Fragment color checking | [`checkFragColors()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L274-L319) | Verifies interpolated clip/cull distance values in fragment-read cases. |
| Clip-volume shaders | [`addSimplePrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L360-L397) | Trivial vert/frag shaders used by inside, outside, depth_clamp, depth_clip, wide_lines. |
| Topology support check | [`checkTopologySupport()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L416-L430) | Prunes triangle fans on portability subset without triangleFans. |
| Inside test instance | [`testPrimitivesInside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L451-L527) | Draws primitives at three depths, checks minimum non-black pixels. |
| Outside test instance | [`testPrimitivesOutside()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L530-L576) | Draws primitives outside clip volume, requires all-black output. |
| Depth clamp test instance | [`testPrimitivesDepthClamp()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L585-L673) | Toggles depthClampEnable for near/far straddling primitives. |
| Depth clip test instance | [`testPrimitivesDepthClip()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L684-L815) | Tests explicit depthClipEnable with and without depth clamp. |
| Large points test instance | [`testLargePoints()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L823-L904) | Point clipping with maintenance2 behavior query. |
| Wide lines test instance | [`testWideLines()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L961-L1081) | Wide-line clipping with reference image comparison. |
| User-defined shader generation | [`ClipDistance::initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1113-L1448) | Generates vert, tesc, tese, geom, frag shaders for clip/cull distance cases. |
| User-defined test instance | [`testClipDistance()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1486-L1553) | Draws bars, checks black-pixel counts and fragment-read colors. |
| Complementarity shaders | [`ClipDistanceComplementarity::initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1561-L1602) | Vertex shader writes last clip distance from w; fragment outputs blend color. |
| Complementarity test instance | [`testComplementarity()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1613-L1679) | Two primitive sets with flipped signs, blended, expects uniform gray. |
| Misc cull-distance shaders | [`CullDistance::initPrograms()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1694-L1724) | Per-vertex negative cull component without shared negative half-space. |
| Misc test instance | [`testCullDistance()`](../../../modules/vulkan/clipping/vktClippingTests.cpp#L1726-L1753) | Expects triangle drawn with half framebuffer red. |
| Mustpass evidence | [`clipping.txt`](../../../mustpass/main/vk-default/clipping.txt#L1-L308) | 308 mustpass entries across all four families. |
