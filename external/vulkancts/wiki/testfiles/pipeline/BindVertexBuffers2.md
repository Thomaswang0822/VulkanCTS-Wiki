## Overview

**Core question:** Does `vkCmdBindVertexBuffers2` update the buffer, offset, bound size, and dynamic stride used by subsequent vertex fetches across its regular, non-contiguous-binding, and maintenance5 paths?

- [`vktPipelineBindVertexBuffers2Tests.cpp`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1) implements the `pipeline.*.bind_buffers_2` test family.
- Its direct intermediate nodes are `single`, `separate`, `dynamic_stride`, and, outside Vulkan SC builds, `maintenance5`.
- The regular nodes render four colored quadrants from dynamically bound attributes. The mismatch node checks a gap between the vertex-input bindings used by the pipeline. The maintenance5 node varies bound ranges and includes robust out-of-range fetches.
- The family uses `VK_EXT_extended_dynamic_state`; maintenance5 paths also require `VK_KHR_maintenance5`, while `robustness2` has extra robustness requirements.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- [`vkCmdBindVertexBuffers2`](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L765-L849) updates consecutive vertex bindings. Each update supplies a buffer and offset, optionally a bound size, and optionally a stride. Attributes that use those bindings use the updated addresses in later draws.
- Under `VK_KHR_maintenance5`, `VK_WHOLE_SIZE` gives a bound range from the supplied offset to the end of the buffer. An explicit size can expose a shorter range even when the allocation contains more bytes.
- A pipeline that enables `VK_DYNAMIC_STATE_VERTEX_INPUT_BINDING_STRIDE` obtains its active strides from this command rather than the static `VkVertexInputBindingDescription::stride` values ([dynamic state setup](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L389-L411)).
- Robustness leaves require `robustBufferAccess`, `robustBufferAccess2`, and `VK_KHR_robustness2` or `VK_EXT_robustness2`; they make some position fetches extend beyond the allocation or explicit bound range ([support check](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1642-L1669)).

## Registration Hierarchy

```text
pipeline.monolithic.bind_buffers_2
├── single
├── separate
├── dynamic_stride
└── maintenance5
```

The root above is the concrete monolithic path used for hierarchy validation. `single` and `separate` are present for every construction root. `dynamic_stride` is monolithic-only. `maintenance5` is omitted from Vulkan SC by source conditional compilation. The exact registration code is [`createCmdBindBuffers2Tests()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1780-L1904) and [`createCmdBindVertexBuffers2Tests()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1906-L2016).

The default Vulkan mustpass files contain 97 monolithic leaves and 96 leaves for each non-monolithic construction root: 56 regular leaves, 40 maintenance5 leaves, plus the monolithic mismatch leaf. The Vulkan SC monolithic file contains 57 leaves because it has the 56 regular leaves and the mismatch leaf but no `maintenance5` paths. See [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) and [`vksc-default/pipeline/monolithic.txt`](../../../mustpass/main/vksc-default/pipeline/monolithic.txt).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Intermediate node | `single`, `separate`, `dynamic_stride`, `maintenance5` | Selects a bind-call shape, a non-contiguous vertex-input binding check, or maintenance5 range behavior. | [registration](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1783-L2016) |
| Regular stride and offset tuple | `stride_0_4_offset_0_0`, `stride_0_4_offset_1_0`, `stride_4_4_offset_0_0`, `stride_5_5_offset_0_7`, `stride_5_8_offset_15_22`, `stride_7_22_offset_100_0`, `stride_40_28_offset_0_0` | Provides color stride, vertex stride, color offset, and vertex offset in float units. | [tuple array](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1813-L1864) |
| Regular count leaf | `count_1` to `count_4` | Chooses one through four color/position buffer pairs and the matching generated input layout. | [count array](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1877-L1885) |
| Maintenance5 topology | `triangle_list`, `triangle_strip` | Chooses a six-vertex list or four-vertex strip draw. | [topology selection](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1372-L1384) |
| Maintenance5 buffer count | `buffers5`, `buffers9` | Sets one color buffer plus four or eight position buffers. | [registration](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1909-L2016) |
| Random layout seed | 321, 432, 543, 654 | Creates reproducible nonzero padding offsets and strides for maintenance5 buffers. | [seed arrays](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1909-L1913) |
| Bound-size mode | `whole_size`, `true_size` | Uses `VK_WHOLE_SIZE` or an explicit returned byte range. | [size assignment](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1249-L1313) |
| Robustness overrun mode | `beyond_buffer`, `beyond_size` | Places the intended position fetch beyond allocation bytes or only beyond the explicit range. `beyond_size` occurs only with `true_size`. | [robust registration](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1961-L2011) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node under `bind_buffers_2`. The remaining dimensions alter data layout or refine the selected node's behavior.

### `single`: replace all regular bindings in one call

`single` binds `2 * count` color and position buffers with one call beginning at binding zero. It checks that the command consumes parallel buffer, offset, size, and stride arrays consistently across all updated bindings.

### `separate`: replace each regular binding in a separate call

`separate` records the same logical bindings one at a time, increasing `firstBinding` for each call. It checks that a later update does not lose or corrupt state already set for earlier bindings.

### `dynamic_stride`: preserve binding-number indexing across an unused binding

`dynamic_stride.binding_stride_index_mismatch` creates attributes on bindings 0 and 2, skipping binding 1. It then calls `vkCmdBindVertexBuffers2` with `firstBinding = 0`, `bindingCount = 3`, and three array elements for bindings 0, 1, and 2. The middle element reuses the color buffer with zero offset, size, and stride, while the third element supplies the position buffer and its stride. This checks that the implementation preserves the command's consecutive binding-number mapping instead of compacting state according to the two bindings used by the pipeline.

### `maintenance5`: apply dynamic offsets, strides, and ranges to multi-buffer vertex input

`maintenance5` binds 5 or 9 buffers in one command. Ordinary leaves vary topology, seeded layout, and whole versus explicit ranges. Its `robustness2` intermediate node makes selected coordinate data extend beyond the allocated buffer or the bound range, so it tests the robust result for each range model.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.shader_object_linked_binary.bind_buffers_2.maintenance5.robustness2.triangle_list.buffers5.stride_offset_rnd543.true_size.beyond_buffer
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `maintenance5.robustness2` | Exercises explicit bound ranges together with robust vertex-fetch behavior for accesses beyond the allocated buffer. |
| `triangle_list.buffers5` | The draw consumes six vertices from one color binding and four position bindings, so all four position inputs participate in the generated vertex expression. |
| `stride_offset_rnd543` | Uses deterministic nonzero per-buffer offsets and strides generated from seed 543. |
| `true_size.beyond_buffer` | Supplies explicit sizes rather than `VK_WHOLE_SIZE`; the position data is arranged so the final list vertex is beyond the allocation and should be robustly fetched. |

#### Purpose

This generated shader makes the result of dynamic vertex-buffer binding observable: the vertex stage combines the four fetched position attributes and forwards the fetched color. The maintenance5 robustness2 host oracle then detects whether explicit bound ranges and out-of-buffer fetches produced the expected bounded image result.

#### Structural Design

| Dataflow phase | Shader operation | Observable effect |
|----------------|------------------|-------------------|
| Vertex fetch | Read `in_color` at location 0 and `pos1` through `pos4` at locations 1 through 4. | Every buffer supplied by the `vkCmdBindVertexBuffers2` call contributes to the draw. |
| Position assembly | Add the four `vec2` position inputs and construct `(x, y, 0, 1)`. | The fixed-function vertex fetch result determines primitive placement. |
| Interface transport | Store the color in `out_color` at location 0. | The fragment stage receives the fetched color without changing it. |
| Raster output | Convert the color to `vec4(in_color, 1.0)` and write the color attachment. | The host image comparison observes the combined fetch result. |

#### Shader Code

##### Vertex Shader

```glsl
#version 450
/// The maintenance5 representative has one color binding and four position bindings.
layout(location = 0) in vec3 in_color;
layout(location = 1) in vec2 pos1;
layout(location = 2) in vec2 pos2;
layout(location = 3) in vec2 pos3;
layout(location = 4) in vec2 pos4;
/// The fetched color is passed to the fragment stage for image comparison.
layout(location = 0) out vec3 out_color;
void main() {
  /// Summing all four position attributes makes every bound coordinate buffer observable.
  gl_Position = vec4(pos1+pos2+pos3+pos4, 0.0, 1.0);
  out_color = in_color;
}
```

##### Fragment Shader

```glsl
#version 450
layout (location = 0) in  vec3 in_color;
layout (location = 0) out vec4 out_color;
void main() {
    out_color = vec4(in_color, 1.0);
}
```

#### Additional Info

- The vertex source is generated by `BindVertexBuffers2Case::initPrograms()` with `m_params.bufferCount == 5`; the loop therefore emits `pos1` through `pos4` and the `pos1+pos2+pos3+pos4` expression.
- For this `triangle_list` robustness2 case, the source code sets `sourceSize = allocSize = returnSize = 5` for `BeyondType::BUFFER`; the point template still contains the extra robust-fetch position, while each explicit position bound size covers five records.
- The fragment shader is fixed across the maintenance5 matrix and only exposes the vertex-stage result; the vertex stage is the primary shader because it consumes the dynamically bound attributes under test.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `bufferCount` | Emits one color input and `bufferCount - 1` `vec2` position inputs; the generated position sum changes accordingly. | [`BindVertexBuffers2Case::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1672-L1701) |
| `topology` | Does not change shader text; it changes the host vertex count and the position data template consumed by the same shader. | [`BindVertexBuffers2Instance::createBuffers()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1138-L1218) |
| `rndSeed` | Does not change shader text; it changes host-side buffer offsets and strides while the interface locations remain fixed. | [`BindVertexBuffers2Instance::createBuffers()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1252-L1313) |
| `wholeSize` / `beyondType` | Does not change shader text; it changes the bound range and which fetched record is out of bounds, with robustness determining the observed value. | [`BindVertexBuffers2Instance::createBuffers()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1249-L1313) |

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
; Bound: 42
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %pos1 %pos2 %pos3 %pos4 %out_color %in_color
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %pos1 "pos1"
               OpName %pos2 "pos2"
               OpName %pos3 "pos3"
               OpName %pos4 "pos4"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %pos1 Location 1
               OpDecorate %pos2 Location 2
               OpDecorate %pos3 Location 3
               OpDecorate %pos4 Location 4
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
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
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
       %pos1 = OpVariable %_ptr_Input_v2float Input
       %pos2 = OpVariable %_ptr_Input_v2float Input
       %pos3 = OpVariable %_ptr_Input_v2float Input
       %pos4 = OpVariable %_ptr_Input_v2float Input
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
%_ptr_Output_v4float = OpTypePointer Output %v4float
    %v3float = OpTypeVector %float 3
%_ptr_Output_v3float = OpTypePointer Output %v3float
  %out_color = OpVariable %_ptr_Output_v3float Output
%_ptr_Input_v3float = OpTypePointer Input %v3float
   %in_color = OpVariable %_ptr_Input_v3float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %19 = OpLoad %v2float %pos1
         %21 = OpLoad %v2float %pos2
         %22 = OpFAdd %v2float %19 %21
         %24 = OpLoad %v2float %pos3
         %25 = OpFAdd %v2float %22 %24
         %27 = OpLoad %v2float %pos4
         %28 = OpFAdd %v2float %25 %27
         %31 = OpCompositeExtract %float %28 0
         %32 = OpCompositeExtract %float %28 1
         %33 = OpCompositeConstruct %v4float %31 %32 %float_0 %float_1
         %35 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %35 %33
         %41 = OpLoad %v3float %in_color
               OpStore %out_color %41
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
; Bound: 19
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %out_color %in_color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
    %v3float = OpTypeVector %float 3
%_ptr_Input_v3float = OpTypePointer Input %v3float
   %in_color = OpVariable %_ptr_Input_v3float Input
    %float_1 = OpConstant %float 1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %13 = OpLoad %v3float %in_color
         %15 = OpCompositeExtract %float %13 0
         %16 = OpCompositeExtract %float %13 1
         %17 = OpCompositeExtract %float %13 2
         %18 = OpCompositeConstruct %v4float %15 %16 %17 %float_1
               OpStore %out_color %18
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. A regular leaf creates a 32 by 32 `VK_FORMAT_R32G32B32A32_SFLOAT` color image, framebuffer, host-visible readback buffer, and a pipeline with dynamic binding stride enabled. It creates `count` color buffers and `count` position buffers, including requested initial padding and per-record padding.
2. The regular command buffer begins the render pass, binds the pipeline, and either calls `cmdBindVertexBuffers2` once for all bindings or once per binding. It draws four vertices with four instances, copies the color image to the readback buffer, submits, waits, and invalidates the host allocation ([regular recording and readback](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L493-L599)).
3. The regular oracle examines every pixel. The expected color depends on the image quadrant and on whether a zero color stride repeatedly fetches the first record. Any unequal pixel fails.
4. The mismatch instance follows the same image-readback structure, but its attributes use bindings 0 and 2. One `cmdBindVertexBuffers2` call updates three consecutive bindings, including a dummy binding 1 entry with zero size and stride, before the test checks the complete rendered image ([mismatch setup](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L678-L895)).
5. A maintenance5 leaf builds a color buffer and 4 or 8 coordinate buffers. It fills nonzero offsets and strides from a fixed seed, sets each bound size to `VK_WHOLE_SIZE` or an explicit byte count, then binds all `bufferCount` buffers and draws a strip or list ([buffer construction](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1128-L1316)).
6. The maintenance5 oracle counts clear-color pixels in the upper-left quarter and samples its inner corner. Without robustness, the sampled RGB must not be below `(0.2, 0.2, 0.2)` and the clear-color fraction must be zero. With robustness2, the sample must be below that threshold and the clear-color fraction must be less than 0.25 ([oracle](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1413-L1509)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single` | Incorrect multi-binding replacement, offset/size/stride application, or vertex fetch. |
| `separate` | Incorrect persistence or replacement of state supplied by successive one-binding calls. |
| `dynamic_stride` | Incorrect association of stride-array elements with non-contiguous binding numbers. |
| `maintenance5` | Incorrect bound-size, `VK_WHOLE_SIZE`, maintenance5, or robust bound-range vertex-fetch behavior. |

### Cause Analysis

#### Multi-binding offset, size, stride, or fetch error

**Possible failure symptoms:** `single` leaves fail for particular stride/offset tuples or counts. The exact image comparison reports a wrong quadrant color or position-derived coverage.

**Possible implementation causes:** The implementation may associate a buffer, offset, size, or stride with the wrong parallel-array element, use the static stride after dynamic stride was enabled, or calculate vertex addresses incorrectly. Inspect the recorded `buffers`, `offsets`, `sizes`, and `strides` arrays before attributing the defect to the shader.

#### Separate-call state persistence error

**Possible failure symptoms:** `separate` fails while the otherwise matching `single` leaf passes, often when `count_2` through `count_4` requires several earlier calls to remain active.

**Possible implementation causes:** A one-binding update may reset unrelated bindings, preserve a stale buffer or stride, or apply `firstBinding` incorrectly. The regular images cannot distinguish every state component, so compare the failing path with the matching one-call configuration to localize the replacement logic.

#### Non-contiguous vertex-input binding association error

**Possible failure symptoms:** `dynamic_stride.binding_stride_index_mismatch` fails while regular contiguous-binding leaves pass.

**Possible implementation causes:** The source deliberately uses pipeline binding numbers 0 and 2 while the command updates bindings 0, 1, and 2 with three array elements. An implementation may compact the command state according to the pipeline's two active bindings, fail to preserve the unused binding 1 slot, or associate binding 2 with the middle element's zero stride instead of the third element's vertex stride. This leaf narrows the issue to that association, though a wrong attribute address can produce the same final image.

#### Maintenance5 bound-range or robustness error

**Possible failure symptoms:** A `maintenance5` path fails only for `whole_size` or `true_size`, only under a topology or seed, or only in `robustness2`. The log includes the observed range mode, offsets, sizes, strides, mismatch percentage, and sampled pixel.

**Possible implementation causes:** The implementation may derive `VK_WHOLE_SIZE` from the wrong start offset, ignore an explicit bound size, calculate a padded vertex address incorrectly, or fail to apply robust bound-range behavior. The threshold oracle covers both geometry and color coverage rather than each fetched component, so source-level investigation is needed to separate range handling from rasterization or attribute-assembly faults.

## Case Pruning

### Requirement-based pruning

- Every path requires `VK_EXT_extended_dynamic_state` and its selected pipeline-construction requirements ([regular support](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1543-L1549)).
- Maintenance5 leaves require `VK_KHR_maintenance5` and are not registered in Vulkan SC builds.
- A `robustness2` leaf also requires core `robustBufferAccess`, `robustBufferAccess2`, and either `VK_KHR_robustness2` or `VK_EXT_robustness2`. It creates a custom device with those features enabled ([custom device setup](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1704-L1777)).

### Design-based pruning

- The regular matrix contains 2 bind-call modes times 7 tuples times 4 counts, or 56 leaves per construction root.
- The mismatch node has one leaf and is limited to monolithic construction because registration explicitly guards it with `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`.
- Ordinary maintenance5 registration covers 2 topologies times 2 buffer counts times 2 seeds times 2 size modes, or 16 leaves. Robustness2 covers 2 topologies times 2 counts times 2 seeds times 3 valid size/overrun combinations, or 24 leaves. `whole_size.beyond_size` is intentionally absent because the whole-buffer range cannot be shorter than the allocation through its end.

## Key Takeaways

- `single` and `separate` use the same data matrix but stress one multi-binding command versus state accumulated by multiple calls.
- `dynamic_stride` checks that a three-element command update preserves the unused binding 1 slot when the pipeline consumes bindings 0 and 2.
- Maintenance5 expands the command from offset and stride state to explicit bound ranges, including `VK_WHOLE_SIZE`.
- The regular oracle compares every pixel exactly; the maintenance5 robustness oracle checks a sampled pixel and bounded clear-color coverage, so it localizes a failure to the operation shape without uniquely identifying a driver layer.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Regular case parameters and execution | [`BindBuffers2Instance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L266-L600) | Creates regular data, records binding calls, and checks every output pixel. |
| Mismatch instance | [`BindBuffers2MismatchInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L623-L895) | Uses bindings 0 and 2 to test stride association. |
| Maintenance5 buffer construction | [`BindVertexBuffers2Instance::createBuffers()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1128-L1316) | Defines seeded data layout, explicit sizes, and deliberate robustness overruns. |
| Maintenance5 execution and oracle | [`BindVertexBuffers2Instance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1331-L1510) | Records the multi-buffer draw and evaluates the two predicates. |
| Generated programs and support checks | [`BindBuffers2Case` and `BindVertexBuffers2Case`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1512-L1778) | Defines generated shaders, requirements, and robust-device creation. |
| Registration | [`createCmdBindBuffers2Tests()` and `createCmdBindVertexBuffers2Tests()`](../../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1780-L2016) | Defines the exact hierarchy and leaf matrix. |
| Vulkan command contract | [vertex-input binding updates](../../../../vulkan-docs/src/chapters/fxvertex.adoc#L765-L849) | Defines the offset, size, `VK_WHOLE_SIZE`, and dynamic-stride semantics. |
| Default Vulkan mustpass evidence | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) | Confirms monolithic executable leaves. |
| Vulkan SC mustpass evidence | [`monolithic.txt`](../../../mustpass/main/vksc-default/pipeline/monolithic.txt) | Confirms the maintenance5 exclusion from Vulkan SC coverage. |
