## Overview

**Core question:** Can tessellation shaders use near-limit, mixed-type control-to-evaluation interfaces and handle built-in tessellation levels without losing values or violating patch-discard rules?

- [`vktTessellationMaxIOTests.cpp`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1) implements both test families under `tessellation.tess_io`.
- `max_in_out` fills a device-dependent interface with shuffled per-vertex or per-patch variables. Cases select numeric features and whether the TCS, TES, both, or neither stage reads or checks the generated interface values.
- `level_io` checks TES reads of `gl_TessLevelInner` and `gl_TessLevelOuter`, then checks the different effects of writing inner or outer levels to zero.
- Both families render two quad patches into an 8 x 8 attachment and use image comparison to turn shader or tessellator behavior into a CTS result.

## Background Knowledge

For the shared concepts tessellation pipeline stages and patch interfaces, see [Background Knowledge](../../categories/tessellation.md#background-knowledge) of the `tessellation` page.

- **Tessellation stage IO.** A tessellation control shader (TCS) runs once per output control point and can write per-vertex arrays or per-patch values. The tessellation evaluation shader (TES) reads those values after fixed-function tessellation. User-defined variables consume locations containing four 32-bit components; some 64-bit vectors span two locations.
- **Tessellation levels and patch discard.** For the quad domain, the TCS writes four outer and two inner levels. A non-positive relevant outer level discards the patch, so no primitives are generated and the TES does not execute. A zero inner level does not by itself discard the patch.

## Registration Hierarchy

```text
tessellation.tess_io
├── max_in_out
└── level_io
```

[`createTessellationTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L65-L81) adds `tess_io` below `tessellation`. [`createTessIOTests()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1800-L1988) registers the two families shown above. The [Vulkan default mustpass list](../../../mustpass/main/vk-default/tessellation.txt#L416-L983) contains 568 paths: 560 for `max_in_out` and 8 for `level_io`.

## Parameter Dimensions and Observed Values

| Dimension | Registered or observed values | Meaning in this test | Evidence |
|-----------|-------------------------------|----------------------|----------|
| Test family | `max_in_out`, `level_io` | Switches between user-defined interface-capacity transport and built-in tessellation-level semantics. | [top-level registration](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1800-L1988) |
| `max_in_out` feature set | `32_bits_only`, `with_i64`, `with_f64`, `all_but_16_bits`, `with_i16`, `with_f16`, `all_types` | Selects which 16-, 32-, and 64-bit integer/float types may appear and which device features the case requires. | [feature table](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1807-L1821) |
| Variable permutation | `permutation_0` through `permutation_9` | Reorders the candidate interface deterministically. The implementation walks that order until a variable no longer fits the relevant limit, then retains the preceding prefix; its exclusive resize endpoint also omits the last variable that fit. | [shuffle and case loop](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1900-L1914) and [prefix trimming](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L510-L537) |
| Interface owner | `vert`, `patch` in leaf names | Chooses per-vertex arrays or per-patch variables, their source buffer, and the limit budget used to trim the list. | [case table](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1830-L1846) |
| TCS read | `writes`, `writes_reads` in leaf names | Keeps the TCS as producer only or adds a TCS-side value check and color output. | [TCS generation](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L761-L840) |
| TES read | `tes_reads`, `tes_na` in leaf names | Declares and checks the user-defined TES inputs or leaves them unconsumed by the TES. | [TES generation](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L666-L759) |
| Candidate variable type | integer/float; 16/32/64 bit; scalar, `vec2`, `vec3`, `vec4`; normal/flat | Changes type width, location consumption, qualifiers, storage-buffer packing, assignment, and validation expressions. | [`IfaceVar`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L155-L455) |
| `level_io` leaf | `tes_reads_inner`, `tes_reads_outer`, `tes_reads_both`, `tcs_writes0_inner_1`, `tcs_writes0_inner_all`, `tcs_writes0_outer_1`, `tcs_writes0_outer_all`, `tcs_writes0_outer_inner` | Selects which built-ins the TES reads or which level elements the TCS sets to zero. | [level registration](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1947-L1985) |
| Render result | 8 x 8 `VK_FORMAT_R8G8B8A8_UNORM`; blue outer patch and yellow centered patch, or clear black | Converts successful value checks, level reads, and patch survival/discard into exact reference images. | [reference generation and comparison](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1081-L1153) |

The `max_in_out` generator excludes normally interpolated integers, flat per-patch values, and normally interpolated 64-bit floats. It also excludes 8-bit stage IO. Ten copies of every surviving type are generated before shuffling, but the final declaration count depends on the selected permutation and device limits.

## Behavior Parameters

The primary behavior parameter is the **test family**. The two values use the same four-stage render/readback shell but exercise different Vulkan behavior.

### `max_in_out`: large user-defined tessellation interfaces

The TCS writes a shuffled collection of typed values into explicit user locations. The source first builds mock shaders with Vulkan's required minimum limits, then reconstructs the interface after it can query the current device. [`getUsableLocations()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L510-L537) walks the shuffled list against either the TCS per-vertex/TES-input budget or the TCS per-patch budget. It stops at the first variable that does not fit and resizes to the last fitting index as an exclusive endpoint, so the final fitting variable is omitted as well.

Every leaf selects one ownership mode and one of four read combinations:

| Leaf suffix | TCS action | TES action | What successful rendering establishes |
|-------------|------------|------------|----------------------------------------|
| `tcs_*_writes_tes_reads` | Writes interface values | Reads and checks them | Control-to-evaluation transport and TES interpretation succeed. |
| `tcs_*_writes_reads_tes_reads` | Writes and checks values; emits diagnostic color | Reads/checks interface and carries color | Both stage-local checking and inter-stage transport succeed. |
| `tcs_*_writes_tes_na` | Writes interface values | Does not consume user interface | The near-limit TCS output declarations and writes compile and execute. |
| `tcs_*_writes_reads_tes_na` | Writes and checks values; emits diagnostic color | Carries color only | TCS reads/writes and near-limit output declarations succeed without TES user-variable reads. |

Per-vertex TES checks allow each interpolated component to lie between the minimum and maximum source control-point values. Per-patch checks require exact equality with the value for `gl_PrimitiveID` 0 or 1. A failed device-side check changes the diagnostic color to black.

### `level_io`: built-in level reads and zero writes

The TCS always writes a blue or yellow per-patch color. The read leaves set all six tessellation levels to one; the TES reads inner levels, outer levels, or both. In `tes_reads_both`, the shader first computes an outer-level-based color and then overwrites it with the inner-level-based color, so the final image still depends only on the inner levels; with all levels one, the expected image stays blue/yellow.

The five write-zero leaves expose a semantic distinction:

| Leaves | TCS level values | Expected result |
|--------|------------------|-----------------|
| `tcs_writes0_inner_1`, `tcs_writes0_inner_all` | One or both inner values are zero; every outer value is one | Patches survive and render blue/yellow. |
| `tcs_writes0_outer_1`, `tcs_writes0_outer_all`, `tcs_writes0_outer_inner` | At least one relevant outer value is zero | Both quad patches are discarded; the attachment stays at clear black. |

## Shader Analysis

The walkthrough uses `level_io.tcs_writes0_outer_1`. It gives a fixed, exact TCS that exposes the outer-level discard condition. By contrast, an exact `max_in_out` shader depends on runtime-reported limits and the resulting trimmed interface, so one static reconstruction would not represent every device.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.tessellation.tess_io.level_io.tcs_writes0_outer_1
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `level_io` | Selects fixed built-in tessellation-level behavior rather than generated user-defined IO. |
| `tcs_writes0_outer_1` | Writes zero to the first relevant outer level and one to the remaining levels. |
| Quad domain, four control points | Makes all four outer levels relevant to patch discard. |
| Two submitted patches | Applies the same discard condition to the outer blue patch and inner yellow patch. |

#### Purpose

The TCS writes one relevant outer tessellation level to zero. Correct fixed-function tessellation discards each patch before TES execution, leaving the render target at its clear color.

#### Structural Design

| TCS action | Produced value | Observable consequence |
|------------|----------------|------------------------|
| Select color from `gl_PrimitiveID` | Blue for patch 0, yellow for patch 1 | Would identify each patch if it survived. |
| Copy `gl_in[gl_InvocationID].gl_Position` | One output control point per invocation | Preserves patch geometry for non-discard variants. |
| Write outer levels | `{0, 1, 1, 1}` | Causes quad patch discard because one relevant outer value is zero. |
| Write inner levels | `{1, 1}` | Does not alter the outer-level discard decision. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_tessellation_shader : require

/// Four TCS invocations produce the four output control points used by the quad patch.
layout (vertices = 4) out;

/// This per-patch color would reach the TES for a surviving patch.
layout (location=0) out patch vec4 perPatchColor;

in gl_PerVertex {
    vec4 gl_Position;
} gl_in[];

out gl_PerVertex {
    vec4 gl_Position;
} gl_out[];

void main ()
{
    /// Give the two patches distinct reference colors before applying the same discard condition.
    perPatchColor = (gl_PrimitiveID == 0) ? vec4(0.0, 0.0, 1.0, 1.0) : vec4(1.0, 1.0, 0.0, 1.0);
    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;

    /// Outer element zero is relevant for quads, so the tessellator must discard the patch.
    gl_TessLevelOuter = float[4]
        (0.000000, 1.000000, 1.000000, 1.000000);
    gl_TessLevelInner = float[2]
        (1.000000, 1.000000);
}
```

#### Additional Info

- The TES and fragment shader remain in the pipeline, but patch discard prevents TES invocation and fragment generation for this case.
- The host expects all copied pixels to equal transparent black, the render-pass clear value.
- The TCS source comes from the fixed `LevelIOTest::initPrograms()` path and uses the `SourceCollections` baseline SPIR-V target.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|------------------------------------------|----------|
| Outer-zero leaves | Set one outer element, all outer elements, or both outer and inner arrays to zero. Every variant still triggers discard. | [zero-value selection](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1552-L1608) |
| Inner-zero leaves | Keep all outer levels at one and set one or both inner values to zero. The patches remain visible. | [zero-value selection](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1552-L1608) |
| TES-read leaves | Set all levels to one; TES code reads outer, inner, or both arrays and uses them in its color expression. In the both-array variant, the later inner-level assignment overwrites the earlier outer-level result. | [TES read generation](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1464-L1515) |
| `max_in_out` family | Replaces this fixed interface with device-dependent generated locations, typed variables, storage buffers, and optional TCS/TES checks. | [`makeShaders()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L622-L844) |

#### SPIR-V

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
; Bound: 51
; Schema: 0
               OpCapability Tessellation
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint TessellationControl %main "main" %perPatchColor %gl_PrimitiveID %gl_out %gl_InvocationID %gl_in %gl_TessLevelOuter %gl_TessLevelInner
               OpExecutionMode %main OutputVertices 4
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_shader_io_blocks"
               OpSourceExtension "GL_EXT_tessellation_shader"
               OpName %main "main"
               OpName %perPatchColor "perPatchColor"
               OpName %gl_PrimitiveID "gl_PrimitiveID"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %gl_out "gl_out"
               OpName %gl_InvocationID "gl_InvocationID"
               OpName %gl_PerVertex_0 "gl_PerVertex"
               OpMemberName %gl_PerVertex_0 0 "gl_Position"
               OpName %gl_in "gl_in"
               OpName %gl_TessLevelOuter "gl_TessLevelOuter"
               OpName %gl_TessLevelInner "gl_TessLevelInner"
               OpDecorate %perPatchColor Patch
               OpDecorate %perPatchColor Location 0
               OpDecorate %gl_PrimitiveID BuiltIn PrimitiveId
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %gl_InvocationID BuiltIn InvocationId
               OpDecorate %gl_PerVertex_0 Block
               OpMemberDecorate %gl_PerVertex_0 0 BuiltIn Position
               OpDecorate %gl_TessLevelOuter BuiltIn TessLevelOuter
               OpDecorate %gl_TessLevelOuter Patch
               OpDecorate %gl_TessLevelInner BuiltIn TessLevelInner
               OpDecorate %gl_TessLevelInner Patch
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
%perPatchColor = OpVariable %_ptr_Output_v4float Output
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
%gl_PrimitiveID = OpVariable %_ptr_Input_int Input
      %int_0 = OpConstant %int 0
       %bool = OpTypeBool
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %19 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
         %20 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_1
     %v4bool = OpTypeVector %bool 4
%gl_PerVertex = OpTypeStruct %v4float
       %uint = OpTypeInt 32 0
     %uint_4 = OpConstant %uint 4
%_arr_gl_PerVertex_uint_4 = OpTypeArray %gl_PerVertex %uint_4
%_ptr_Output__arr_gl_PerVertex_uint_4 = OpTypePointer Output %_arr_gl_PerVertex_uint_4
     %gl_out = OpVariable %_ptr_Output__arr_gl_PerVertex_uint_4 Output
%gl_InvocationID = OpVariable %_ptr_Input_int Input
%gl_PerVertex_0 = OpTypeStruct %v4float
    %uint_32 = OpConstant %uint 32
%_arr_gl_PerVertex_0_uint_32 = OpTypeArray %gl_PerVertex_0 %uint_32
%_ptr_Input__arr_gl_PerVertex_0_uint_32 = OpTypePointer Input %_arr_gl_PerVertex_0_uint_32
      %gl_in = OpVariable %_ptr_Input__arr_gl_PerVertex_0_uint_32 Input
%_ptr_Input_v4float = OpTypePointer Input %v4float
%_arr_float_uint_4 = OpTypeArray %float %uint_4
%_ptr_Output__arr_float_uint_4 = OpTypePointer Output %_arr_float_uint_4
%gl_TessLevelOuter = OpVariable %_ptr_Output__arr_float_uint_4 Output
         %45 = OpConstantComposite %_arr_float_uint_4 %float_0 %float_1 %float_1 %float_1
     %uint_2 = OpConstant %uint 2
%_arr_float_uint_2 = OpTypeArray %float %uint_2
%_ptr_Output__arr_float_uint_2 = OpTypePointer Output %_arr_float_uint_2
%gl_TessLevelInner = OpVariable %_ptr_Output__arr_float_uint_2 Output
         %50 = OpConstantComposite %_arr_float_uint_2 %float_1 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %int %gl_PrimitiveID
         %16 = OpIEqual %bool %13 %int_0
         %22 = OpCompositeConstruct %v4bool %16 %16 %16 %16
         %23 = OpSelect %v4float %22 %19 %20
               OpStore %perPatchColor %23
         %31 = OpLoad %int %gl_InvocationID
         %37 = OpLoad %int %gl_InvocationID
         %39 = OpAccessChain %_ptr_Input_v4float %gl_in %37 %int_0
         %40 = OpLoad %v4float %39
         %41 = OpAccessChain %_ptr_Output_v4float %gl_out %31 %int_0
               OpStore %41 %40
               OpStore %gl_TessLevelOuter %45
               OpStore %gl_TessLevelInner %50
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Both families require `tessellationShader` and `multiViewport`. `max_in_out` also checks only the numeric and 16-bit IO features needed by its selected feature set.
- `max_in_out` queries the physical-device limits, trims the shuffled interface, and regenerates its four programs because explicit locations cannot be finalized earlier. It creates one host-visible storage buffer for the selected owner: `pvd` for per-vertex data or `ppd` for per-patch data.
- Both paths create an 8 x 8 `VK_FORMAT_R8G8B8A8_UNORM` color image and a host-visible transfer-destination buffer. The graphics pipeline has vertex, TCS, TES, and fragment stages, two viewports, two scissors, patch-list topology, and four control points per patch.
- One draw submits eight vertices, producing two patches. Patch 0 uses full-viewport geometry and is blue; patch 1 uses centered half-size geometry and is yellow when both survive and checks succeed. The pipeline creates two viewport entries, but these shaders do not write `gl_ViewportIndex`, so the geometry itself—not a selected smaller viewport—provides the centered half-size region.
- The command buffer transitions the color image for transfer, copies it to the verification buffer, inserts transfer-to-host visibility, submits, and waits. The host invalidates the allocation before comparison.
- [`commonVerifyResult()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1112-L1153) compares every pixel with a per-channel floating-point threshold of 0.005. Any difference fails with `Result does not match reference; check log for details`.
- `max_in_out` and non-discarding `level_io` leaves expect blue outside and yellow in the centered 4 x 4 region. Outer-zero `level_io` leaves expect transparent black throughout because no fragments are produced.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `max_in_out` | Incorrect accounting, declaration, compilation, transport, interpolation, or checking of a large mixed-type TCS-to-TES interface; incorrect handling of a required numeric feature; or a shared render/readback defect. |
| `level_io` | Incorrect TCS write or TES read behavior for `gl_TessLevelOuter`/`gl_TessLevelInner`, incorrect patch-discard handling for outer zero, or a shared render/readback defect. |

### Cause Analysis

#### Large mixed-type tessellation interface

**Possible failure symptoms:** Shader compilation or pipeline creation may fail, the draw may fail, or copied pixels may turn black or disagree with the expected blue/yellow image. Failures may correlate with one feature set, permutation, owner, or read combination.

**Possible implementation causes:** The compiler or pipeline linker may account for explicit locations, 64-bit two-location values, interpolation qualifiers, per-vertex arrays, or per-patch variables incorrectly. TCS stores, TCS reads, TCS-to-TES transport, TES interpolation, or typed comparisons may corrupt a value. A device may also report a component limit that its implementation cannot sustain for the generated fitting interface.

#### Optional numeric and 16-bit IO features

**Possible failure symptoms:** Only feature sets containing `i64`, `f64`, `i16`, or `f16` may fail during support checks, shader compilation, pipeline creation, or rendered checking, while `32_bits_only` succeeds.

**Possible implementation causes:** The exposed core numeric feature or `shaderFloat16`/`storageInputOutput16` support may not be implemented correctly in tessellation stage IO, conversions, declarations, or storage-buffer reference access. The case gates each optional type before execution, so a supported case should accept the corresponding generated operations.

#### Built-in level write/read or patch discard

**Possible failure symptoms:** A TES-read leaf may render the wrong color; an inner-zero leaf may disappear unexpectedly; or an outer-zero leaf may contain blue/yellow fragments instead of remaining clear black.

**Possible implementation causes:** TCS writes to the built-in level arrays may be lost or indexed incorrectly, TES reads may see wrong values, or the tessellator may apply the quad-domain relevance and discard rule incorrectly. The Vulkan tessellation rules require discard when any relevant outer level is non-positive and specify no TES execution for a discarded patch.

#### Shared render and readback path

**Possible failure symptoms:** Any leaf may show broad image corruption, an unchanged clear target when rendering was expected, or copied bytes that disagree with the color attachment.

**Possible implementation causes:** Pipeline stage linkage, viewport selection, rasterization, color attachment writes, image layout/access transitions, image-to-buffer copy, or host-cache visibility may be incorrect. The image comparison alone cannot distinguish one shared-path defect from another.

## Case Pruning

### Requirement-based pruning

- Every case requires `tessellationShader` and `multiViewport`; unsupported devices skip execution.
- `with_i64`, `with_f64`, and `all_but_16_bits`/`all_types` require the matching `shaderInt64` or `shaderFloat64` features.
- `with_i16` and `all_types` require `shaderInt16` plus `storageInputOutput16`. `with_f16` and `all_types` require `shaderFloat16` plus `storageInputOutput16`.
- Runtime regeneration rejects a program target above the SPIR-V version supported for the selected Vulkan version/device functionality.

### Design-based pruning

- The feature table uses seven representative combinations instead of the full power set of four optional type features.
- The generator uses ten deterministic random permutations rather than millions of possible variable orders.
- It removes invalid type/qualifier combinations and does not attempt 8-bit stage IO.
- The fitting algorithm walks in order and stops at the first variable that no longer fits; its `resize(vecEnd)` call also excludes the last variable that fit because `vecEnd` is used as an exclusive endpoint. It does not search later elements for a different maximal packing; permutations supply varied order coverage.
- The location budget reserves built-in use and one diagnostic color location when TCS-side checks feed color to the TES.
- `level_io` registers the three useful read combinations and five zero-write patterns. It does not enumerate arbitrary non-one levels because the family targets built-in read transport and zero semantics.

## Key Takeaways

- `max_in_out` tests near-limit interfaces with device-dependent generated declarations, deterministic mixed-type permutations, and four TCS/TES read combinations.
- `level_io` separates built-in level transport from tessellator behavior: outer zero discards a quad patch, while inner zero does not.
- Both families reduce the result to a small image. Blue/yellow means the expected patches survived and checks passed; black signals a device-side mismatch or the expected outer-level discard.
- A failure may originate in the selected interface/level mechanism or in the shared render, transfer, and host-visibility path. The case name and image pattern narrow the likely area.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Interface representation and checks | [`IfaceVar`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L155-L455) | Defines typed variable names, locations, buffer layout, assignments, and validation expressions. |
| Interface limit calculation | [`getMaxLocations()` and `getUsableLocations()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L490-L537) | Converts component limits to usable locations and trims each shuffled list. |
| Generated `max_in_out` shaders | [`makeShaders()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L622-L844) | Emits descriptors, TCS outputs/checks, TES inputs/checks, and diagnostic colors. |
| Support and dynamic compilation | [`MaxIOTest::checkSupport()` and `reGeneratePrograms()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L851-L1010) | Gates optional features and replaces mock shaders with device-specific binaries. |
| Common reference and comparison | [`commonGenerateReferenceLevel()` and `commonVerifyResult()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1081-L1153) | Builds the expected image and applies the 0.005 threshold. |
| `max_in_out` runtime | [`MaxIOTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1181-L1400) | Creates source buffers, descriptors, render/copy resources, draws, and checks. |
| Built-in level shaders | [`LevelIOTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1428-L1619) | Generates all TES read and TCS zero-write variants. |
| Built-in level runtime | [`LevelIOTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1648-L1790) | Draws and chooses blue/yellow or clear-black reference output. |
| Registration | [`createTessIOTests()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1800-L1988) | Registers seven feature sets, ten permutations, eight interface leaves, and eight level leaves. |
| Parent placement | [`createTessellationTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L65-L81) | Places `tess_io` under the `tessellation` test category. |
| Interface limit semantics | [Vulkan limits chapter](../../../../vulkan-docs/src/chapters/limits.adoc#limits-maxTessellationControlPerVertexOutputComponents) | Defines the TCS per-vertex/per-patch and TES input limits used by the fitting logic. |
| Tessellator semantics | [Vulkan tessellation chapter](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation) | Defines level-controlled subdivision and outer-level patch discard. |
| Built-in level access | [Vulkan built-in variables](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-tesslevelouter) | Defines TCS writes and TES reads for inner/outer level arrays. |
| Mustpass paths | [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L416-L983) | Confirms all 568 Vulkan paths documented by this page. |
