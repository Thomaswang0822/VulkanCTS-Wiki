## Overview

**Core question:** Does the fixed-function tessellator generate the expected tessellation-coordinate set for each primitive domain and spacing mode?

- `vktTessellationCoordinatesTests.cpp` implements the `tessellation.tesscoord` test family.
- Each registered leaf selects a primitive domain, a spacing mode, and whether the primitive and spacing execution modes come from the tessellation evaluation shader or only from source SPIR-V for the tessellation control shader.
- For nine level sets, the test captures every generated `gl_TessCoord` value in a storage buffer and compares the unordered result against CTS reference coordinates.
- The comparison checks both directions with a per-component tolerance of `0.01`, so it detects missing and unexpected coordinates without assuming invocation order.

## Background Knowledge

For the shared concepts tessellation pipeline stages, primitive domains, and spacing modes, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- **Tessellation domains.** Triangle coordinates are barycentric triples. Quad coordinates use `(u,v,0)` over a rectangular domain. Isoline coordinates use `u` along a line and `v` to select the line.
- **Spacing modes.** Equal, fractional-even, and fractional-odd spacing convert tessellation levels into different segment counts and placements. Most exact coordinates at non-integer fractional levels are implementation-dependent, so the fractional cases use rounded integer levels for reference comparison.
- **Execution-mode placement.** The primitive, spacing, winding, and point-mode execution modes may be declared by either tessellation shader stage. If both stages declare a mode, they must agree. This family checks both evaluation-shader declarations and control-shader-only source SPIR-V declarations.

## Registration Hierarchy

```text
tessellation.tesscoord
├── isolines_equal_spacing
├── isolines_equal_spacing_execution_mode_in_tesc
├── isolines_fractional_even_spacing
├── isolines_fractional_even_spacing_execution_mode_in_tesc
├── isolines_fractional_odd_spacing
├── isolines_fractional_odd_spacing_execution_mode_in_tesc
├── quads_equal_spacing
├── quads_equal_spacing_execution_mode_in_tesc
├── quads_fractional_even_spacing
├── quads_fractional_even_spacing_execution_mode_in_tesc
├── quads_fractional_odd_spacing
├── quads_fractional_odd_spacing_execution_mode_in_tesc
├── triangles_equal_spacing
├── triangles_equal_spacing_execution_mode_in_tesc
├── triangles_fractional_even_spacing
├── triangles_fractional_even_spacing_execution_mode_in_tesc
├── triangles_fractional_odd_spacing
└── triangles_fractional_odd_spacing_execution_mode_in_tesc
```

All 18 leaves appear directly under `tessellation.tesscoord` in the Vulkan default mustpass list.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Primitive domain | `triangles`, `quads`, `isolines` | Changes the coordinate domain, relevant inner/outer levels, and reference generator. | [`createCoordinatesTests()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L871-L886) |
| Spacing mode | `equal_spacing`, `fractional_even_spacing`, `fractional_odd_spacing` | Changes level rounding and segment placement. | [`getCaseName()` and `genTessLevelCases()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L70-L132) |
| Execution-mode stage | default leaf, `_execution_mode_in_tesc` | Places the primitive and spacing modes in the evaluation shader or only in the control shader's source SPIR-V. | [`TessCoordTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L412-L647) |
| Level set | nine fixed inner/outer arrays | Exercises low, high, asymmetric, and special fractional-spacing inputs within one registered case. | [`rawTessLevelCases`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L80-L132) |

## Behavior Parameters

The primary behavioral axis is the primitive-domain group because it changes the meaning of `TessCoord` and the reference construction.

### `triangles_*`: barycentric triangle coordinates

Triangle cases compare three-component barycentric coordinates. The CTS reference path clamps and rounds one inner level and three outer levels, then generates the expected triangular coordinate set.

### `quads_*`: rectangular coordinates

Quad cases compare `(u,v,0)` values. Two inner and four outer levels control subdivision along the two domain directions and four outer edges.

### `isolines_*`: line and segment coordinates

Isoline cases compare `(u,v,0)` values where one outer level selects the number of isolines and the other selects segments per line. The isoline-count dimension always follows equal-spacing rules even when the along-line dimension uses fractional spacing.

## Shader Analysis

The representative case shows the stage that captures each generated tessellation coordinate. The control shader supplies levels; the evaluation shader atomically allocates a result slot and writes `gl_TessCoord`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.tesscoord.triangles_equal_spacing
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `triangles` | Uses the barycentric triangular domain. |
| `equal_spacing` | Uses exact equal-length segment placement after level rounding. |
| execution modes in TES | The evaluation shader declares triangle, spacing, and point mode; GLSL's default `ccw` order supplies the winding mode. |

#### Purpose

The evaluation shader records the `TessCoord` value supplied to every generated point-mode invocation. The host later compares that unordered set with the CTS triangle reference.

#### Structural Design

| Phase | Operation | Observable data |
|-------|-----------|-----------------|
| TCS | Reads six level values from binding 0 and writes the tessellation-level built-ins. | Inner and outer levels drive primitive generation. |
| Tessellator | Generates point-mode vertices in the triangle domain. | Each invocation receives one `gl_TessCoord`. |
| TES | Atomically reserves a slot in binding 1 and stores the coordinate. | Host-visible count and coordinate array. |

#### Shader Code

##### Tessellation Control Shader

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require

layout(vertices = 1) out;
layout(set = 0, binding = 0, std430) readonly restrict buffer TessLevels {
    float inner0;
    float inner1;
    float outer0;
    float outer1;
    float outer2;
    float outer3;
} sb_levels;

void main (void)
{
    /// Copy the host-selected levels into the built-ins consumed by the tessellator.
    gl_TessLevelInner[0] = sb_levels.inner0;
    gl_TessLevelInner[1] = sb_levels.inner1;
    gl_TessLevelOuter[0] = sb_levels.outer0;
    gl_TessLevelOuter[1] = sb_levels.outer1;
    gl_TessLevelOuter[2] = sb_levels.outer2;
    gl_TessLevelOuter[3] = sb_levels.outer3;
}
```

##### Tessellation Evaluation Shader

```glsl
#version 310 es
#extension GL_EXT_tessellation_shader : require

layout(triangles, equal_spacing, point_mode) in;
layout(set = 0, binding = 1, std430) coherent restrict buffer Output {
    int numInvocations;
    vec3 tessCoord[];
} sb_out;

void main (void)
{
    /// Invocation order is unspecified, so reserve an output slot atomically.
    int index = atomicAdd(sb_out.numInvocations, 1);
    sb_out.tessCoord[index] = gl_TessCoord;
}
```

#### Additional Info

- The control shader is secondary but necessary to show where the level inputs enter the tested path. Its assignments do not vary with primitive or spacing mode.
- In the GLSL path, the test compiles a second TES that writes `gl_PointSize`; the pipeline selects it when the core `shaderTessellationAndGeometryPointSize` feature is enabled. The source-SPIR-V path registers the same non-writing TES under both binary names.
- No rasterization or attachment is used. The test observes only the storage-buffer capture.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|----------------------------------------|----------|
| Primitive domain | Changes the TES layout to `triangles`, `quads`, or `isolines`. | [`TessCoordTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L459-L647) |
| Spacing mode | Changes the spacing layout qualifier or its source-SPIR-V execution mode. | [`TessCoordTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L459-L647) |
| Execution-mode placement | Replaces GLSL TES declarations with a source-SPIR-V TCS path that carries the execution modes. | [`TessCoordTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L412-L647) |
| Point-size feature (GLSL path) | When `shaderTessellationAndGeometryPointSize` is enabled, selects the alternate TES that adds `GL_EXT_tessellation_point_size` and writes `gl_PointSize`. | [`TessCoordTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L460-L488) |

#### SPIR-V

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
; Bound: 46
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationControl %main "main" %gl_TessLevelInner %gl_TessLevelOuter
               OpExecutionMode %main OutputVertices 1
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %gl_TessLevelInner "gl_TessLevelInner"
               OpName %TessLevels "TessLevels"
               OpMemberName %TessLevels 0 "inner0"
               OpMemberName %TessLevels 1 "inner1"
               OpMemberName %TessLevels 2 "outer0"
               OpMemberName %TessLevels 3 "outer1"
               OpMemberName %TessLevels 4 "outer2"
               OpMemberName %TessLevels 5 "outer3"
               OpName %sb_levels "sb_levels"
               OpName %gl_TessLevelOuter "gl_TessLevelOuter"
               OpDecorate %gl_TessLevelInner BuiltIn TessLevelInner
               OpDecorate %gl_TessLevelInner Patch
               OpDecorate %TessLevels BufferBlock
               OpMemberDecorate %TessLevels 0 Restrict
               OpMemberDecorate %TessLevels 0 NonWritable
               OpMemberDecorate %TessLevels 0 Offset 0
               OpMemberDecorate %TessLevels 1 Restrict
               OpMemberDecorate %TessLevels 1 NonWritable
               OpMemberDecorate %TessLevels 1 Offset 4
               OpMemberDecorate %TessLevels 2 Restrict
               OpMemberDecorate %TessLevels 2 NonWritable
               OpMemberDecorate %TessLevels 2 Offset 8
               OpMemberDecorate %TessLevels 3 Restrict
               OpMemberDecorate %TessLevels 3 NonWritable
               OpMemberDecorate %TessLevels 3 Offset 12
               OpMemberDecorate %TessLevels 4 Restrict
               OpMemberDecorate %TessLevels 4 NonWritable
               OpMemberDecorate %TessLevels 4 Offset 16
               OpMemberDecorate %TessLevels 5 Restrict
               OpMemberDecorate %TessLevels 5 NonWritable
               OpMemberDecorate %TessLevels 5 Offset 20
               OpDecorate %sb_levels Restrict
               OpDecorate %sb_levels NonWritable
               OpDecorate %sb_levels Binding 0
               OpDecorate %sb_levels DescriptorSet 0
               OpDecorate %gl_TessLevelOuter BuiltIn TessLevelOuter
               OpDecorate %gl_TessLevelOuter Patch
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
 %TessLevels = OpTypeStruct %float %float %float %float %float %float
%_ptr_Uniform_TessLevels = OpTypePointer Uniform %TessLevels
  %sb_levels = OpVariable %_ptr_Uniform_TessLevels Uniform
%_ptr_Uniform_float = OpTypePointer Uniform %float
%_ptr_Output_float = OpTypePointer Output %float
      %int_1 = OpConstant %int 1
     %uint_4 = OpConstant %uint 4
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Output__arr_float_uint_4 = OpTypePointer Output %_arr_float_uint_4
%gl_TessLevelOuter = OpVariable %_ptr_Output__arr_float_uint_4 Output
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
      %int_4 = OpConstant %int 4
      %int_5 = OpConstant %int 5
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_Uniform_float %sb_levels %int_0
         %19 = OpLoad %float %18
         %21 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_0
               OpStore %21 %19
         %23 = OpAccessChain %_ptr_Uniform_float %sb_levels %int_1
         %24 = OpLoad %float %23
         %25 = OpAccessChain %_ptr_Output_float %gl_TessLevelInner %int_1
               OpStore %25 %24
         %31 = OpAccessChain %_ptr_Uniform_float %sb_levels %int_2
         %32 = OpLoad %float %31
         %33 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_0
               OpStore %33 %32
         %35 = OpAccessChain %_ptr_Uniform_float %sb_levels %int_3
         %36 = OpLoad %float %35
         %37 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_1
               OpStore %37 %36
         %39 = OpAccessChain %_ptr_Uniform_float %sb_levels %int_4
         %40 = OpLoad %float %39
         %41 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_2
               OpStore %41 %40
         %43 = OpAccessChain %_ptr_Uniform_float %sb_levels %int_5
         %44 = OpLoad %float %43
         %45 = OpAccessChain %_ptr_Output_float %gl_TessLevelOuter %int_3
               OpStore %45 %44
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
; Bound: 29
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationEvaluation %main "main" %gl_TessCoord
               OpExecutionMode %main Triangles
               OpExecutionMode %main SpacingEqual
               OpExecutionMode %main VertexOrderCcw
               OpExecutionMode %main PointMode
               OpSource ESSL 310
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %index "index"
               OpName %Output "Output"
               OpMemberName %Output 0 "numInvocations"
               OpMemberName %Output 1 "tessCoord"
               OpName %sb_out "sb_out"
               OpName %gl_TessCoord "gl_TessCoord"
               OpDecorate %_runtimearr_v3float ArrayStride 16
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 Restrict
               OpMemberDecorate %Output 0 Coherent
               OpMemberDecorate %Output 0 Offset 0
               OpMemberDecorate %Output 1 Restrict
               OpMemberDecorate %Output 1 Coherent
               OpMemberDecorate %Output 1 Offset 16
               OpDecorate %sb_out Restrict
               OpDecorate %sb_out Coherent
               OpDecorate %sb_out Binding 1
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %gl_TessCoord BuiltIn TessCoord
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %float = OpTypeFloat 32
    %v3float = OpTypeVector %float 3
%_runtimearr_v3float = OpTypeRuntimeArray %v3float
     %Output = OpTypeStruct %int %_runtimearr_v3float
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
      %int_0 = OpConstant %int 0
%_ptr_Uniform_int = OpTypePointer Uniform %int
      %int_1 = OpConstant %int 1
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
     %uint_0 = OpConstant %uint 0
%_ptr_Input_v3float = OpTypePointer Input %v3float
%gl_TessCoord = OpVariable %_ptr_Input_v3float Input
%_ptr_Uniform_v3float = OpTypePointer Uniform %v3float
       %main = OpFunction %void None %3
          %5 = OpLabel
      %index = OpVariable %_ptr_Function_int Function
         %17 = OpAccessChain %_ptr_Uniform_int %sb_out %int_0
         %22 = OpAtomicIAdd %int %17 %uint_1 %uint_0 %int_1
               OpStore %index %22
         %23 = OpLoad %int %index
         %26 = OpLoad %v3float %gl_TessCoord
         %28 = OpAccessChain %_ptr_Uniform_v3float %sb_out %int_1 %23
               OpStore %28 %26
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The instance creates a host-visible level buffer and a host-visible result buffer. Binding 0 supplies six floats; binding 1 stores an invocation count followed by captured `vec3` values.
- For each of nine level sets, the host uploads levels, clears the result buffer, draws one abstract vertex as one patch, waits for completion, and invalidates the result allocation.
- The invocation count must be at least the reference-coordinate count. The host then compares the result and reference sets in both directions.
- A point matches when every component differs by at most `0.01`. The comparison ignores order and permits extra invocations when their coordinates duplicate expected points; the lower-bound count check detects too few invocations but does not reject those permitted duplicates.
- A registered case passes only when all nine level sets pass.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `triangles_*` | Incorrect triangular-domain subdivision or barycentric `TessCoord` values; a spacing-specific failure can indicate wrong level clamping, rounding, or segment placement. |
| `quads_*` | Incorrect rectangular-domain subdivision, inner/outer level mapping, or `(u,v,0)` `TessCoord` values; a spacing-specific failure can indicate wrong level clamping, rounding, or segment placement. |
| `isolines_*` | Incorrect isoline count, segments per line, or `(u,v,0)` `TessCoord` values; the implementation may have applied spacing to the isoline-count dimension, which uses equal spacing. |

### Cause Analysis

#### Domain generation and coordinate assignment

**Possible failure symptoms:** The result count can differ from the reference count, or the comparison can report expected points that are missing and result points that are unexpected.

**Possible implementation causes:** The primitive generator may produce the wrong subdivision or assign incorrect domain coordinates. The primitive-specific reference routines and Vulkan tessellation-domain rules provide the expected sets.

#### Spacing and level interpretation

**Possible failure symptoms:** Only one spacing group or selected level sets fail, often near fractional-even or fractional-odd rounding boundaries.

**Possible implementation causes:** The implementation may clamp or round levels incorrectly, choose the wrong segment count, or place the symmetric fractional segments incorrectly. Exact fractional coordinates outside the source's selected special cases are not used as an oracle.

#### Execution-mode placement or result capture

**Possible failure symptoms:** `_execution_mode_in_tesc` leaves fail while their ordinary partners pass, or captured counts/coordinates are corrupt across all domains.

**Possible implementation causes:** The implementation may mishandle execution modes declared only by the control stage. A storage-buffer atomic, descriptor, synchronization, or host invalidation problem can also corrupt the captured set; the test cannot localize that shared path further from a coordinate mismatch alone.

## Case Pruning

### Requirement-based pruning

- The test requires the core `tessellationShader` and `vertexPipelineStoresAndAtomics` features.
- On portability-subset implementations, point mode must be supported; isoline leaves additionally require tessellation-isoline support. For ordinary GLSL leaves, the pipeline selects the point-size-writing TES when the core `shaderTessellationAndGeometryPointSize` feature is enabled; the source-SPIR-V leaves use the same non-writing module under either TES binary name.

### Design-based pruning

- Fractional-spacing inputs are rounded to integer effective levels because general non-integer fractional coordinates are implementation-dependent.
- The family captures point-mode vertices and compares sets. It does not test primitive emission order.
- Nine level sets run inside each leaf rather than becoming another registered hierarchy dimension.

## Key Takeaways

- The family checks generated coordinate sets, not rendered pixels or primitive order.
- Primitive domain is the main behavior axis; spacing and execution-mode placement refine each domain group.
- Bidirectional comparison catches missing and unexpected coordinates while tolerating unspecified invocation order.
- Failures can expose domain generation, spacing, execution-mode placement, or the shared storage-buffer capture path.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Case naming and level inputs | [`getCaseName()` and `genTessLevelCases()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L70-L132) | Defines the registered dimensions and nine level sets. |
| Reference dispatch | [`generateReferenceTessCoords()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L135-L200) | Selects primitive-specific coordinate generation and checks the fractional special cases. |
| Level interpretation | [`getClamped*()` helpers](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L364-L430) | Implements spacing-dependent clamping and rounding, including equal spacing for the isoline-count level. |
| Reference coordinate construction | [`generateReference*TessCoords()` helpers](../../../modules/vulkan/tessellation/vktTessellationUtil.cpp#L493-L629) | Constructs the triangle, quad, and isoline coordinate sets. |
| Bidirectional comparison | [`compareTessCoords()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L272-L365) | Defines the tolerance and missing/unexpected point checks. |
| Shader generation | [`TessCoordTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L412-L647) | Emits the GLSL and source-SPIR-V paths. |
| Runtime loop | [`TessCoordTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L670-L856) | Uploads levels, draws, reads the result buffer, and checks all nine inputs. |
| Feature checks | [`checkSupport()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L399-L410) and [`createInstance()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L858-L864) | Checks portability-subset restrictions and requires tessellation shaders plus vertex-pipeline stores and atomics. |
| Registration | [`createCoordinatesTests()`](../../../modules/vulkan/tessellation/vktTessellationCoordinatesTests.cpp#L871-L886) | Registers the 18 leaves. |
| Mustpass coverage | [`tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L984-L1001) | Lists all Vulkan `tesscoord` paths. |
| Tessellation semantics | [`tessellation.adoc`](../../../../vulkan-docs/src/chapters/tessellation.adoc#L7-L228) | Defines execution-mode placement, domains, and spacing rules. |
| `TessCoord` built-in | [`interfaces.adoc`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L5322-L5349) | Defines the coordinate values supplied to the TES. |
