## Overview

**Core question:** Do the query results reflect the fragments produced by a full-frame draw, including the cases where command-buffer inheritance or shader side effects change the invocation behavior?

- `query_pool.frag_invocations` is implemented by [`vktQueryPoolFragInvocationTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp) and registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L55).
- The test category contains `occlusion` and `frag_invs` test families. Each family has six test cases: `primary`, `primary_with_vertex_color`, `primary_with_atomic_counter`, and the corresponding `secondary` cases.
- Occlusion cases require an exact result of `4096`. Fragment-invocation cases require a lower bound. The flat shader has a shading-rate-dependent bound; the vertex-color and atomic variants require at least `4096`.
- Every case checks the copied color image. Atomic variants also check a storage-buffer counter.

## Background Knowledge

- An occlusion query counts passing samples. `VK_QUERY_CONTROL_PRECISE_BIT` requests the precise result used by this test.
- A pipeline-statistics query can select `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT`. Fragment shader invocations are not necessarily one-to-one with covered pixels when a side-effect-free shader produces the same result for different fragments.
- A secondary command buffer records work for execution inside a primary render pass. Its [`VkCommandBufferInheritanceInfo`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L283-L307) carries the query-related state needed by the draw.

## Registration Hierarchy

```text
query_pool.frag_invocations
├── occlusion
└── frag_invs
```

`createFragInvocationTests()` expands each family over the `primary` or `secondary` command-buffer mode and the three fragment-shader variants. The exact registered leaves come from [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L449-L485).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `occlusion`, `frag_invs` | Selects the query type and validation rule | [`getQueryTypeName()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L46-L66) |
| Command-buffer mode | `primary`, `secondary` | Chooses inline recording or inherited execution | [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L471-L478) |
| Fragment-shader variant | no suffix, `_with_vertex_color`, `_with_atomic_counter` | Changes shader data flow and side effects | [`fragShaderVariantCases`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L456-L464) |
| Framebuffer | `64 x 64 x 1` | Gives the expected full-coverage pixel count | [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L149-L154) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | Defines the color readback format | [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L152-L157) |
| Draw | one triangle, `VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST` | Covers the framebuffer | [`vertices`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L171-L176) and [`makeGraphicsPipeline()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L274-L277) |

The matrix is `2 x 2 x 3`, or 12 test cases. The query pool has one slot.

## Behavior Parameters

The primary behavioral axis is the test family. The shader variant and command-buffer mode are important secondary axes because they alter the query bound or command recording path.

### `occlusion`: exact covered-sample count

The test creates `VK_QUERY_TYPE_OCCLUSION` and begins it with `VK_QUERY_CONTROL_PRECISE_BIT`. The oversized triangle covers all `64 x 64` pixels, so the host requires the query result to equal `4096`.

### `frag_invs`: fragment-shader invocation lower bound

The test creates `VK_QUERY_TYPE_PIPELINE_STATISTICS` and selects `VK_QUERY_PIPELINE_STATISTIC_FRAGMENT_SHADER_INVOCATIONS_BIT`.

- For the flat shader, `testInvocations()` divides the framebuffer width and height by `maxFragmentSize`, obtained from `VK_KHR_fragment_shading_rate` when supported. Each divisor is clamped to at least 1. Without that extension, the fallback is `1 x 1`, giving a lower bound of `4096`.
- For `_with_vertex_color` and `_with_atomic_counter`, the minimum is the full pixel count, `4096`. The vertex-color path carries a vertex-to-fragment color varying, while the atomic variant writes a storage resource for each fragment.
- The check is `queryResult < minCount`, so results above the bound pass.

## Shader Analysis

The vertex-color primary case shows the only shader-interface variation that changes both stages. The flat and atomic variants keep the same draw and pipeline structure; their fragment differences are summarized below.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.query_pool.frag_invocations.frag_invs.primary_with_vertex_color
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `frag_invs` | Selects the pipeline-statistics query and fragment-invocation lower-bound check |
| `primary` | Records the draw directly in the primary command buffer |
| `_with_vertex_color` | Adds a vertex-to-fragment color interface, so the fragment shader consumes `vtxColor` |

#### Purpose

The shaders produce a full-frame blue draw while keeping a varying value in the fragment data path. The query must report at least one invocation per covered pixel.

#### Structural Design

| Stage | Input | Operation | Output |
|-------|-------|-----------|--------|
| Vertex | position and color at locations 0 and 1 | copy position to `gl_Position` and color to the stage output | location 0 color |
| Fragment | location 0 `vtxColor` | write the received color | location 0 color attachment |

#### Shader Code

##### Vertex Shader

```glsl
#version 460
/// The position and per-vertex color use separate locations.
layout (location=0) in vec4 inPos;
layout (location=1) in vec4 inColor;
layout (location=0) out vec4 outColor;
void main() {
    gl_Position = inPos;
    outColor = inColor;
}
```

##### Fragment Shader

```glsl
#version 460
/// The interpolated color is the shader input that distinguishes this variant.
layout (location=0) out vec4 outColor;
layout (location=0) in vec4 vtxColor;
void main() {
    outColor = vtxColor;
}
```

#### Additional Info

- The host assigns the same blue `tcu::Vec4` color to all three vertices. The variant still exercises the vertex-to-fragment interface rather than a fragment-local constant.
- The flat variant omits the interface and writes `vec4(0.0, 0.0, 1.0, 1.0)` directly. The atomic variant adds `layout (set=0, binding=0) buffer CounterBlock { uint counter; } cb;` and `atomicAdd(cb.counter, 1u);` before its color write.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Fragment-shader variant | `FLAT` removes the color interface; `VERTEX_COLOR` adds matching location 0/1 declarations; `ATOMIC_COUNTER` adds a storage-buffer declaration and atomic increment | [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L106-L131) |
| Command-buffer mode | `primary` and `secondary` use the same shader programs | [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L471-L478) |

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
; Bound: 24
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %inPos %outColor %inColor
               OpSource GLSL 460
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %inPos "inPos"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %inPos Location 0
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
      %inPos = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %inColor = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %inPos
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %23 = OpLoad %v4float %inColor
               OpStore %outColor %23
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
; Bound: 13
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor %vtxColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 460
               OpName %main "main"
               OpName %outColor "outColor"
               OpName %vtxColor "vtxColor"
               OpDecorate %outColor Location 0
               OpDecorate %vtxColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %vtxColor = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %v4float %vtxColor
               OpStore %outColor %12
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host clears the color attachment, resets the one-slot query pool, begins the query, and begins the render pass.
- The primary path binds the pipeline and vertex buffer and draws three vertices. The secondary path executes an inherited secondary command buffer containing those bindings and the draw.
- The test ends the render pass and query, transitions the color image for transfer, copies it to the readback buffer, and inserts a host-read barrier. Atomic cases also include fragment-shader writes in the synchronization source scope.
- After `submitCommandsAndWait()`, the host invalidates the allocation and retrieves the query result with `VK_QUERY_RESULT_WAIT_BIT`.
- The query check follows the family-specific exact or lower-bound rule above. The color readback must equal blue under `tcu::floatThresholdCompare()` with a zero threshold. Atomic cases require the readback counter to equal `4096`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `occlusion` | Occlusion query setup, precise result reporting, coverage, or query-result retrieval does not produce the exact covered count. |
| `frag_invs` with `FLAT` | Fragment-invocation reporting is below the source-derived lower bound, or the optional fragment-shading-rate property is handled incorrectly. |
| `frag_invs` with `VERTEX_COLOR` | Fragment-invocation reporting is below the full-pixel lower bound for a varying shader path. |
| `frag_invs` with `ATOMIC_COUNTER` | Fragment-invocation reporting, storage writes, synchronization, or atomic-counter readback is below the expected per-pixel result. |
| `primary` | Inline command recording, render-pass execution, or query boundaries do not produce the expected observable result. |
| `secondary` | Query inheritance, secondary execution, or primary/secondary render-pass coordination does not produce the expected observable result. |

### Cause Analysis

#### Query result does not meet its bound

**Possible failure symptoms:** The host reports an occlusion result other than `4096`, or a `frag_invs` result below its selected minimum.

**Possible implementation causes:** Source inspection points to query type, query flags, pipeline-statistics selection, coverage, or query-result handling as the relevant areas. The exact fault location needs implementation-specific investigation.

#### Color readback differs from blue

**Possible failure symptoms:** `tcu::floatThresholdCompare()` fails with a zero per-channel threshold.

**Possible implementation causes:** The draw, framebuffer setup, shader interface, image-to-buffer copy, layout transition, or host visibility synchronization may not match the test's expected path. Source inspection does not identify one universal fault location.

#### Atomic counter is not `4096`

**Possible failure symptoms:** The atomic variant's host-read counter differs from the full pixel count.

**Possible implementation causes:** The fragment storage-buffer binding, atomic operation, fragment-shader write visibility, or host readback may be incorrect. Further investigation must distinguish shader execution from synchronization and readback behavior.

#### Secondary execution differs from primary execution

**Possible failure symptoms:** A secondary case fails a query, color, or atomic check while the corresponding primary case passes.

**Possible implementation causes:** The inherited render pass, framebuffer, `occlusionQueryEnable`, query flags, pipeline-statistics mask, or `cmdExecuteCommands()` path may not preserve the intended query context.

## Case Pruning

### Requirement-based pruning

Runtime support checks skip cases when their required core feature is unavailable: `inheritedQueries` for secondary cases, `occlusionQueryPrecise` for `occlusion`, `pipelineStatisticsQuery` for `frag_invs`, and `fragmentStoresAndAtomics` for atomic variants.

### Design-based pruning

No cases are pruned by the registration code. The complete Cartesian product registers 12 leaves.

## Key Takeaways

- `occlusion` checks an exact `4096` result; `frag_invs` checks a lower bound.
- Only the flat fragment shader receives the invocation-reuse exception. Vertex-color and atomic variants require the full-pixel lower bound.
- Primary and secondary cases share the shaders and draw. Secondary cases add inherited query state and execution inside the primary render pass.
- Color verification is exact, and atomic variants add an independent exact counter check.

## Source Reference Appendix

- Registration: [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L55)
- Parameters and feature gates: [`vktQueryPoolFragInvocationTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L46-L104)
- Generated shaders: [`initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L106-L131)
- Query and command-buffer setup: [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L237-L358)
- Query, atomic, and color validation: [`testInvocations()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L363-L444)
- Case registration: [`createFragInvocationTests()`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L449-L485)
- Specification context: [`query_begin_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/query_begin_common.adoc) and [`query_results_common.adoc`](../../../../vulkan-docs/src/chapters/commonvalidity/query_results_common.adoc)
