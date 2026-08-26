## Overview

**Core question:** Do `invariant` and `precise` keep a decorated position calculation stable when unrelated shader calculations change?

- This page covers the `glsl.invariance` and `glsl.precise` test families implemented by [`vktShaderRenderInvarianceTests.cpp`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L90-L1140). The families share one implementation because they use the same paired-shader render oracle.
- Each test case renders identical geometry twice. The first draw uses one vertex-shader variant and a red fragment color; the second uses another vertex-shader variant and green. Any red pixel left after the second draw means the two vertex paths did not produce matching coverage.
- The basic matrix changes shared expressions, expression precision, and loop structure around a decorated result. The `precise` family adds focused cases for five GLSL built-in functions.

## Background Knowledge

- **Invariance in multipass rendering.** Vulkan does not require pixel-exact agreement across different implementations, but it does require some results from the same implementation to match. The [Vulkan invariance appendix](../../../../vulkan-docs/src/appendices/invariance.adoc#L51-L60) identifies redrawing a primitive in another color as a multipass use that depends on invariance.
- **Decorated shader results.** The tests place `invariant` or `precise` on `gl_Position`, and some basic cases also decorate a user-defined output that is copied into `gl_Position`. The expected position calculation must stay stable when calculations for an unrelated varying are present in one shader and absent in the other.
- **Coverage as an equality oracle.** If both vertex shaders produce the same clip-space positions for the same triangles, the second draw covers the first. Residual red therefore makes a position difference visible without reading vertex values back to the host.

## Registration Hierarchy

```text
glsl.invariance
├── highp
├── lowp
└── mediump

glsl.precise
├── extended_instructions
├── highp
├── lowp
└── mediump
```

The tree shows one registered level below each test-family root. Under each precision, the basic matrix continues through `gl_position` and `user_defined` intermediate nodes to executable leaves. `extended_instructions` contains direct leaves and exists only under `glsl.precise`.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family and qualifier | `invariance` with `invariant`; `precise` with `precise` | Selects the GLSL constraint applied to the position-producing path. | [Factory functions](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1140) |
| Basic calculation precision | `highp`, `mediump`, `lowp` | Selects precision-qualified inputs, temporaries, literals, and loop constants. | [`precisions[]`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L370) |
| Decorated target | `gl_position`, `user_defined` | Decorates `gl_Position` directly, or decorates both `gl_Position` and `v_value` before assigning `v_value` to `gl_Position`. | [Declarations and assignments](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L376-L382) |
| Basic behavior leaf | `common_subexpression_0` through `_3`; `subexpression_precision_lowp`, `_mediump`, `_highp`; `loop_0` through `_4` | Exercises shared arithmetic, mixed-precision expressions, and loop-carried calculations around the decorated result. | [Basic registration](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L441-L911) |
| Extended built-in | `smoothstep`, `mix`, `dot`, `cross`, `distance` | Places a `precise` result from the selected built-in on the position path while a related built-in calculation feeds an unrelated varying in the first shader. | [Extended registration](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L953-L1116) |
| Extended precision pair | Calculation precision and unrelated-output precision, each chosen from `highp`, `mediump`, `lowp` | Checks each selected built-in across nine precision pairings. | [Nested precision loops](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L937-L951) |
| Geometry | 72 narrow triangles and 72 ordinary triangles, seed `123` | Uses both near-degenerate and general triangle shapes with deterministic input vertices. | [Geometry generation](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L163-L187) |
| Render target and depth candidates | 256 x 256; `D32_SFLOAT`, `D24_UNORM_S8_UINT`, `X8_D24_UNORM_PACK32` | Fixes the image scanned by the host and the depth formats accepted by the render harness. | [Render setup](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L244-L268) |

For each test-family root, the basic matrix contains `3 x 2 x (4 + 3 + 5) = 72` leaves. The extended matrix adds `3 x 3 x 5 = 45` leaves to `precise`, so the registered totals are 72 `invariance` leaves and 117 `precise` leaves.

## Behavior Parameters

The primary behavioral axis is the test family because it selects the GLSL qualifier contract and determines whether the extended built-in matrix exists.

### `invariance`: stable decorated outputs

The `invariance` family applies `invariant` to `gl_Position`; the `user_defined` path also applies it to `v_value`. Each leaf keeps the decorated position expression equivalent across two vertex shaders while changing calculations that feed `v_unrelated`. The four common-subexpression cases vary expression sharing and association, the three precision cases vary the unrelated path's precision, and the five loop cases vary loop-carried arithmetic.

### `precise`: stable precise calculations

The `precise` family runs the same 72-leaf basic matrix with `precise` declarations. The source states that the `precise` keyword also makes invariance guarantees, so these cases use the same two-draw position oracle. This family also has 45 `extended_instructions` leaves. They apply `precise` to a built-in result used by `gl_Position` and vary whether a related calculation contributes to `v_unrelated`.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.glsl.invariance.highp.gl_position.common_subexpression_0
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `invariance` / `invariant` | `createShaderInvarianceTests()` calls `addBasicTests(mainGroup, "invariant")`; the generated declaration decorates `gl_Position`. |
| `highp` | Selects `precisions[]` entry `highp`: input arithmetic is `highp`, with `HIGH_VALUE = 1.0e20` and `HIGH_VALUE_INV = 1.0e-20`. |
| `gl_position` | Selects the direct decorated target (`invariant gl_Position;`), rather than the `user_defined` interface path. |
| `common_subexpression_0` | The first vertex shader keeps a large shared expression in `v_unrelated`; the second retains only the position expression and writes zero to `v_unrelated`. |

#### Purpose

This exact specialization checks that an invariant `gl_Position` remains stable when a large common subexpression is also used by an unrelated varying in the first vertex shader. The paired render passes expose any coverage difference as residual red pixels.

#### Structural Design

| Phase | Primary vertex shader (`vertex1`) | Paired comparison role |
|-------|-----------------------------------|------------------------|
| Interface | `a_input` at location 0; `v_unrelated` at location 0; invariant built-in position | `vertex2` has the same position interface and writes zero to the unrelated output |
| Unrelated path | Computes the high-exponent shared expression, multiplies it by a zero-producing difference, and adds a normalized copy | Keeps the expression live without changing the intended position path |
| Decorated path | `a_input + (1.0e20 * x/x-swizzles + 1.0e20 * y/y-swizzles) * 1.0e-20` | Must produce matching coverage in the second green draw |

#### Shader Code

Source mapping: `external/vulkancts/modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L441-L478`, generated by `addBasicTests()` using `new InvarianceTest(...)`; the case is registered under `createShaderInvarianceTests()` at `#L1123-L1129`. The block below is the exact `vertex1` result for the selected arguments, with only `///` wiki annotations added.

```glsl
#version 450
layout(location = 0) in highp vec4 a_input;
layout(location = 0) out mediump vec4 v_unrelated;
invariant gl_Position;
void main ()
{
    /// The unrelated varying retains the first-pass arithmetic live; its value is not used for the position.
    v_unrelated = a_input.xzxz + (1.0e20*a_input.x*a_input.xxxx + 1.0e20*a_input.y*a_input.yyyy) * (1.08 * a_input.zyzy * a_input.xzxz) * 1.0e-20 * (a_input.z * a_input.zzxz - a_input.z * a_input.zzxz) + (1.0e20*a_input.x*a_input.xxxx + 1.0e20*a_input.y*a_input.yyyy) / 1.0e20;
    /// The decorated position path is shared with vertex2 and is the value tested by the two-draw oracle.
    gl_Position = a_input + (1.0e20*a_input.x*a_input.xxxx + 1.0e20*a_input.y*a_input.yyyy) * 1.0e-20;
}
```

The paired `vertex2` generated by the same `new InvarianceTest` call writes `v_unrelated = vec4(0.0, 0.0, 0.0, 0.0);` and retains the same `gl_Position` assignment. The shared fragment generator reads the binding-0 `ColorUniform`, combines its red/green channels with `dot(v_unrelated, vec4(1.0))` as blue, and writes location-0 `fragColor`; the host binds red for pass 0 and green for pass 1.

#### Additional Info

- `InvarianceTest::initPrograms()` attaches the two generated vertex strings as `vertex1` and `vertex2`, plus the generated fragment string (`vktShaderRenderInvarianceTests.cpp#L123-L128`).
- The host uses 72 narrow plus 72 ordinary triangles from deterministic seed `123`, draws both shaders at 256 x 256, and checks that no pixel has a nonzero red channel (`#L163-L187`, `#L270-L301`, `#L304-L342`).
- No explicit `vk::ShaderBuildOptions` is supplied in this insertion path, so the shader-disassembler target follows the `SourceCollections` baseline: `spirv1.0`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Basic calculation precision | Changes `IN_PREC`, literal magnitudes, and loop constants across the basic matrix; this case uses `highp`, `1.0e20`, and `1.0e-20`. | [`precision matrix`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L438) |
| Decorated target | `gl_position` emits `invariant gl_Position;`; `user_defined` additionally emits location-1 `invariant highp out vec4 v_value` and assigns it to `gl_Position`. | [`decorated-target generation`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L376-L423) |
| Basic behavior leaf | `common_subexpression_0` varies the first shader's unrelated arithmetic; its second shader keeps the position expression and zeroes `v_unrelated`. | [`basic behavior generation`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L441-L478) |
| Test family | `invariance` injects `invariant`; `precise` reuses the basic generator with `precise` and adds extended built-in cases. | [`family registration`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1140) |

#### SPIR-V

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
; Bound: 95
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %v_unrelated %a_input %_
               OpSource GLSL 450
               OpName %main "main"
               OpName %v_unrelated "v_unrelated"
               OpName %a_input "a_input"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpDecorate %v_unrelated RelaxedPrecision
               OpDecorate %v_unrelated Location 0
               OpDecorate %a_input Location 0
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 0 Invariant
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
%v_unrelated = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %a_input = OpVariable %_ptr_Input_v4float Input
%float_1_00000002e_20 = OpConstant %float 1.00000002e+20
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
     %uint_1 = OpConstant %uint 1
%float_1_08000004 = OpConstant %float 1.08000004
%float_9_99999968en21 = OpConstant %float 9.99999968e-21
     %uint_2 = OpConstant %uint 2
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %v4float %a_input
         %13 = OpVectorShuffle %v4float %12 %12 0 2 0 2
         %18 = OpAccessChain %_ptr_Input_float %a_input %uint_0
         %19 = OpLoad %float %18
         %20 = OpFMul %float %float_1_00000002e_20 %19
         %21 = OpLoad %v4float %a_input
         %22 = OpVectorShuffle %v4float %21 %21 0 0 0 0
         %23 = OpVectorTimesScalar %v4float %22 %20
         %25 = OpAccessChain %_ptr_Input_float %a_input %uint_1
         %26 = OpLoad %float %25
         %27 = OpFMul %float %float_1_00000002e_20 %26
         %28 = OpLoad %v4float %a_input
         %29 = OpVectorShuffle %v4float %28 %28 1 1 1 1
         %30 = OpVectorTimesScalar %v4float %29 %27
         %31 = OpFAdd %v4float %23 %30
         %33 = OpLoad %v4float %a_input
         %34 = OpVectorShuffle %v4float %33 %33 2 1 2 1
         %35 = OpVectorTimesScalar %v4float %34 %float_1_08000004
         %36 = OpLoad %v4float %a_input
         %37 = OpVectorShuffle %v4float %36 %36 0 2 0 2
         %38 = OpFMul %v4float %35 %37
         %39 = OpFMul %v4float %31 %38
         %41 = OpVectorTimesScalar %v4float %39 %float_9_99999968en21
         %43 = OpAccessChain %_ptr_Input_float %a_input %uint_2
         %44 = OpLoad %float %43
         %45 = OpLoad %v4float %a_input
         %46 = OpVectorShuffle %v4float %45 %45 2 2 0 2
         %47 = OpVectorTimesScalar %v4float %46 %44
         %48 = OpAccessChain %_ptr_Input_float %a_input %uint_2
         %49 = OpLoad %float %48
         %50 = OpLoad %v4float %a_input
         %51 = OpVectorShuffle %v4float %50 %50 2 2 0 2
         %52 = OpVectorTimesScalar %v4float %51 %49
         %53 = OpFSub %v4float %47 %52
         %54 = OpFMul %v4float %41 %53
         %55 = OpFAdd %v4float %13 %54
         %56 = OpAccessChain %_ptr_Input_float %a_input %uint_0
         %57 = OpLoad %float %56
         %58 = OpFMul %float %float_1_00000002e_20 %57
         %59 = OpLoad %v4float %a_input
         %60 = OpVectorShuffle %v4float %59 %59 0 0 0 0
         %61 = OpVectorTimesScalar %v4float %60 %58
         %62 = OpAccessChain %_ptr_Input_float %a_input %uint_1
         %63 = OpLoad %float %62
         %64 = OpFMul %float %float_1_00000002e_20 %63
         %65 = OpLoad %v4float %a_input
         %66 = OpVectorShuffle %v4float %65 %65 1 1 1 1
         %67 = OpVectorTimesScalar %v4float %66 %64
         %68 = OpFAdd %v4float %61 %67
         %69 = OpCompositeConstruct %v4float %float_1_00000002e_20 %float_1_00000002e_20 %float_1_00000002e_20 %float_1_00000002e_20
         %70 = OpFDiv %v4float %68 %69
         %71 = OpFAdd %v4float %55 %70
               OpStore %v_unrelated %71
         %78 = OpLoad %v4float %a_input
         %79 = OpAccessChain %_ptr_Input_float %a_input %uint_0
         %80 = OpLoad %float %79
         %81 = OpFMul %float %float_1_00000002e_20 %80
         %82 = OpLoad %v4float %a_input
         %83 = OpVectorShuffle %v4float %82 %82 0 0 0 0
         %84 = OpVectorTimesScalar %v4float %83 %81
         %85 = OpAccessChain %_ptr_Input_float %a_input %uint_1
         %86 = OpLoad %float %85
         %87 = OpFMul %float %float_1_00000002e_20 %86
         %88 = OpLoad %v4float %a_input
         %89 = OpVectorShuffle %v4float %88 %88 1 1 1 1
         %90 = OpVectorTimesScalar %v4float %89 %87
         %91 = OpFAdd %v4float %84 %90
         %92 = OpVectorTimesScalar %v4float %91 %float_9_99999968en21
         %93 = OpFAdd %v4float %78 %92
         %94 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %94 %93
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host compiles `vertex1`, `vertex2`, and `fragment` for the selected leaf.
- It generates 144 triangles from seed `123`: 72 narrow triangles followed by 72 ordinary triangles. Both draws use the same vertex data.
- It creates two host-visible uniform buffers and descriptor sets. Pass 0 receives `(1, 0, 0, 1)` and pass 1 receives `(0, 1, 0, 1)`.
- It selects the first candidate depth format whose optimal-tiling features include `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`. If none qualifies, `iterate()` returns a test failure before drawing.
- The harness registers two draw objects against the same 256 x 256 target. Pass 0 uses `vertex1` and the red uniform; pass 1 uses `vertex2` and the green uniform. Both use the same fragment shader.
- [`checkImage()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L304-L342) scans every pixel as integers. Any nonzero red channel produces an error mask and the failure message `Detected variance between two invariant values`. A result with no red pixels passes.

The checker does not compare vertex outputs or all color channels. It asks whether any fragment from the first draw remains visible after the second draw.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `invariance` | Decorated output instability, or a failure in the shared rendering and overwrite path. |
| `precise` | Precise calculation instability, including the selected built-in for an `extended_instructions` leaf, or a failure in the shared rendering and overwrite path. |

A failure before either behavior runs can also come from the depth-format prerequisite.

### Cause Analysis

#### Decorated output instability

**Possible failure symptoms:** One or more pixels retain a nonzero red channel after the green draw in an `invariance` leaf. The log reports fragments from the first render pass and emits an error mask.

**Possible implementation causes:** Compilation or execution changed the decorated position-producing path when unrelated common-subexpression, precision, or loop calculations changed. The image oracle identifies a coverage difference but cannot separate shader translation, arithmetic transformation, clipping, or rasterization without further source-level investigation.

#### Precise calculation instability

**Possible failure symptoms:** One or more pixels retain red in a `precise` leaf. For an `extended_instructions` leaf, the symptom appears for a named built-in and precision pair.

**Possible implementation causes:** Compilation or execution failed to preserve the position result required by the source's `precise` construction when the unrelated calculation changed. An extended leaf narrows the affected source pattern to `smoothstep`, `mix`, `dot`, `cross`, or `distance`, but the host check cannot identify the faulty compiler or graphics stage by itself.

#### Shared rendering and overwrite failure

**Possible failure symptoms:** Red remains even though both generated vertex paths produce matching positions, or setup fails before image verification.

**Possible implementation causes:** The common graphics path may have failed to execute the second draw over the first, bind the second pass's descriptor data, or return the rendered target for checking. These possibilities require source-level investigation because the final red-channel scan does not isolate pipeline setup, draw execution, or readback.

#### Unavailable depth attachment format

**Possible failure symptoms:** `iterate()` returns `There must be at least one depth depth format handled (Vulkan spec 37.3, table 65)` before registering the draws.

**Possible implementation causes:** None of the three formats accepted by this test reports `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT` for optimal tiling. The file reports this condition as failure rather than `NotSupportedError`.

## Case Pruning

### Requirement-based pruning

The file defines no per-case `checkSupport()` and requires no optional extension or feature for these families. Registration is unconditional for Vulkan and Vulkan SC in the inspected GLSL package path. At execution time, the harness requires one supported depth attachment format from its three-item candidate list. It does not prune or skip the leaf when that requirement fails; it returns a failure.

### Design-based pruning

- The basic generator deliberately limits the matrix to four common-subexpression leaves, three unrelated-precision leaves, and five loop leaves for each calculation precision and decorated target.
- `extended_instructions` belongs only to `precise` and covers five named built-ins. The 45 leaves are focused coverage of those operations, not all GLSL built-ins or all extended instructions.
- The source uses the same 72-leaf basic shapes for both roots. It changes the injected decoration instead of creating different basic matrices for `invariant` and `precise`.

## Key Takeaways

- The two-draw oracle converts position instability into residual red pixels. It does not perform a saved-image comparison or read vertex values back.
- The 72 basic leaves vary expression sharing, precision, and loops for direct `gl_Position` and user-defined decorated-output paths.
- `precise` adds 45 leaves for five built-ins and nine precision pairings, giving 117 leaves beside the 72 `invariance` leaves.
- A red pixel proves that the first draw was not covered by the second at that pixel. See `Failure Meaning` for the causes the checker can and cannot distinguish.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test case and runtime implementation | [`InvarianceTest` and `InvarianceTestInstance`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L90-L342) | Defines shader collection, geometry and resources, two-pass drawing, and red-channel validation. |
| Precision records | [`PrecisionCase` and `precisions[]`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L347-L370) | Supplies registered precision names, arithmetic literals, and loop parameters. |
| Basic matrix generator | [`addBasicTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L372-L915) | Generates common-subexpression, mixed-precision, and loop leaves for both decorated targets. |
| Extended built-in generator | [`addExtendedInstructionsTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L917-L1121) | Generates the 45 `precise` leaves for five built-ins and nine precision pairs. |
| Test-family factories | [`createShaderInvarianceTests()` and `createShaderPreciseTests()`](../../../modules/vulkan/shaderrender/vktShaderRenderInvarianceTests.cpp#L1123-L1140) | Names the two roots and selects their generated matrices. |
| GLSL package attachment | [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1253-L1267) | Attaches both test families under `glsl`. |
| Vulkan invariance rules | [Invariance appendix](../../../../vulkan-docs/src/appendices/invariance.adoc#L9-L116) | Defines the same-implementation and multipass invariance context used to interpret the render oracle. |
| Vulkan default mustpass coverage | [`vk-default/glsl.txt`](../../../mustpass/main/vk-default/glsl.txt#L7943-L8014) and [`precise` range](../../../mustpass/main/vk-default/glsl.txt#L14491-L14607) | Lists 72 `invariance` and 117 `precise` executable paths. |
| Vulkan SC default mustpass coverage | [`vksc-default/glsl.txt`](../../../mustpass/main/vksc-default/glsl.txt#L7024-L7095) and [`precise` range](../../../mustpass/main/vksc-default/glsl.txt#L13570-L13686) | Confirms the same suffix hierarchy for the Vulkan SC package. |

