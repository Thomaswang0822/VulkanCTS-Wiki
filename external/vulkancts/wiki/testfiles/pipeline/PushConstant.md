## Overview

**Core question:** Do graphics and compute pipelines consume the bytes written by push-constant commands from the correct range, stage, and compatible layout after updates and pipeline changes?

[`vktPipelinePushConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3337-L3832) builds the `push_constant` group. Its graphics leaves cover disjoint and overlapping ranges, range sizes, stage combinations, partial and repeated updates, dynamic indexing, unused declarations, and overwrites. The monolithic-only compute leaves cover a simple read, an uninitialized read survival case, and overwrite behavior. Nine lifetime leaves arrange pushes and graphics/compute pipeline binds in different sequences.

For a diagnostic summary, start with [PushConstant_brief.md](PushConstant_brief.md). This page records the implementation and coverage evidence behind that failure map.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Range and update state.** A `VkPushConstantRange` specifies its byte interval and the shader stages that can access it. `vkCmdPushConstants` updates a byte interval for stages in a pipeline layout; `vkCmdPushConstants2KHR` receives the corresponding information through `VkPushConstantsInfo`. The command interval must be represented by the layout's ranges ([pipeline layouts and ranges](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1702-L1891), [common command validity](../../../../vulkan-docs/src/chapters/commonvalidity/push_constants_common.adoc#L5-L26)).
- **Compatible layouts and bind points.** Push-constant values are consumed through a pipeline layout compatible for push constants with the layout used to establish them. Graphics and compute commands have separate bind points, which matters to the lifetime sequences that switch between them ([push constant state and compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L5160-L5295)).
- **Device limits and stages.** A range cannot exceed `maxPushConstantsSize`. Geometry and tessellation shader stages need their corresponding device features; the source checks them when a generated configuration uses those stages ([limits](../../../../vulkan-docs/src/chapters/limits.adoc#L2015-L2025), [support checks](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1154-L1200)).

## Registration Hierarchy

```text
pipeline.monolithic.push_constant
├── graphics_pipeline
├── compute_pipeline                 (monolithic only)
└── lifetime
```

The pipeline dispatcher creates this family only outside `CTS_USES_VULKANSC` ([dispatcher guard](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L125-L131)). `createPushConstantTests` creates graphics and lifetime for every permitted pipeline construction type; it creates compute only when `pipelineConstructionType == PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` ([group construction](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3606-L3637), [conditional groups](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3809-L3829)).

The split default pipeline mustpass directory has five non-monolithic lists containing this family: `fast-linked-library.txt`, `pipeline-library.txt`, `shader-object-linked-binary.txt`, `shader-object-linked-spirv.txt`, and `shader-object-unlinked-binary.txt`. Each has **62 leaves**: **53** under `graphics_pipeline` and **9** under `lifetime`; none lists `compute_pipeline`. Thus the five files contain 310 path occurrences, but they represent the same 62-leaf registration shape for five construction modes. This page does not infer monolithic mustpass coverage from that split.

## Parameter Dimensions and Observed Values

The primary behavior axis is how a value is established and consumed: graphics range configuration, overwrite updates, compute consumption, or compatibility/lifetime sequencing. Size and stage selection broaden the graphics configurations rather than define independent mechanisms.

| Group / axis | Registered values and shape | Source |
|---|---|---|
| `graphics_pipeline` disjoint cases | 16 `graphicsParams` entries: range sizes, four stage-count cases, three update cases, and two dynamic-index cases. Each is registered once with `vkCmdPushConstants` and once with `_command2`; Vulkan SC omits the latter. | [table and loop](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3340-L3450), [registration](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3608-L3625) |
| Graphics overlap cases | Four overlapping range configurations, each in ordinary and `_command2` form. | [table](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3452-L3485), [registration](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3627-L3635) |
| Unused declarations | Six disjoint and six overlapping cases vary declared ranges and the subset of stages that actually reads a push constant. | [disjoint cases](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3639-L3733), [overlap cases](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3735-L3805) |
| Graphics overwrite | One `overwrite` leaf records four draws and updates several fields before each draw. | [registration helper](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3290-L3333) |
| `compute_pipeline` | `simple_test`, `uninitialized`, and `overwrite`; only monolithic construction creates this group. | [parameter table](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3487-L3505), [conditional registration](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3811-L3819) |
| `lifetime` | Nine fixed command lists covering pushes, graphics binds, compute binds, compatible same ranges, and overlapping different ranges. | [table](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3507-L3604), [registration](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3822-L3829) |

The 53 graphics leaves seen in each split mustpass file are mechanically accounted for as `(16 disjoint + 4 overlap) × 2 command forms + 6 unused disjoint + 6 unused overlap + 1 overwrite = 53`. `_command2` variants exist only for the first two tables; unused and overwrite cases use the ordinary command path.

## Behavior Parameters

The primary behavior axis is how a value is established and consumed: graphics range configuration, overwrite updates, compute consumption, or compatibility/lifetime sequencing. The subsections below describe those values and their mechanisms.

### Graphics range configuration

#### Disjoint ranges, sizes, updates, and indexing

The disjoint table samples 4, 16, 128, and 256-byte ranges; two long-vector forms; and a `range_size_max` configuration whose size is obtained from the device. It also includes one shared vertex/fragment range, two-, three-, and five-range stage configurations, partial updates at two offsets, per-triangle updates, and dynamically uniform vector/matrix/array indexing ([graphics parameters](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3347-L3450)).

Each ordinary case records `vkCmdPushConstants`; the paired `_command2` leaf records `vkCmdPushConstants2KHR` through the source's `pushConstants` helper. The graphics support check requires `VK_KHR_maintenance6` for the latter ([maintenance6 gate](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1154-L1161)). It checks each fixed range against `maxPushConstantsSize`; the maximum-size case is explicitly sourced from the device instead ([size gate](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1162-L1182)).

#### Overlap and unused declarations

The overlap table exercises two through five ranges whose byte intervals overlap across vertex, fragment, geometry, and tessellation stages. The unused tables reuse representative disjoint and overlapping layouts while choosing `PC_USE_STAGE_NONE`, one selected stage, or tessellation stages for actual shader consumption ([stage-use enum](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L103-L114), [unused registration](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3639-L3805)). They therefore distinguish declared layout visibility from the stages the generated shader actually reads.

When a selected range includes geometry or tessellation stages, the support check requires `geometryShader` or `tessellationShader`, respectively ([stage feature checks](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1184-L1200)). Long-vector configurations are excluded from Vulkan SC at registration and require the `longVector` feature elsewhere ([long-vector entries](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3364-L3377), [feature check](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1175-L1180)).

#### Graphics result checking

The graphics instance submits its command buffer and compares the color attachment with an image rendered by `ReferenceRenderer`. `intThresholdPositionDeviationCompare` permits the source's integer threshold and position deviation before returning `Image mismatch` on failure ([submission](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L678-L688), [comparison](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L691-L755)). A graphics failure can therefore involve the push command/range/stage path, generated shader behavior, rendering, attachment readback, or the reference comparison—not just range declaration.

### Overwrite updates

The graphics and compute `overwrite` leaves push each member of one range separately, in a deliberately non-struct order, before each of four draws or dispatches. Each execution writes one storage-image pixel, so the final four-pixel comparison checks both repeated replacement of the same byte intervals and preservation of the other intervals ([push sequence](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3187-L3238), [validation](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3263-L3289)).

### Compute consumption

The monolithic-only compute leaves separate an ordinary initialized read from a dynamically unused, uninitialized read. The ordinary leaf compares eight shader-written vectors with the pushed value; the uninitialized leaf intentionally checks only that execution completes without a crash ([command recording](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2191-L2215), [verification](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2225-L2247)).

### Compatibility and lifetime sequencing

The nine `lifetime` leaves use fixed command sequences to test whether push-constant state survives compatible pipeline-layout binds and whether updates through layouts with different overlapping ranges affect later graphics or compute consumption as required. Their image and buffer checks observe the final consumer output rather than any intermediate push-constant state ([command interpreter](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2754-L2867), [validation](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2870-L2927)).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.shader_object_linked_binary.push_constant.graphics_pipeline.count_1_shader_vert_frag
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `graphics_pipeline` | The test consumes push-constant state through a graphics pipeline, with a vertex producer and fragment consumer. |
| `count_1_shader_vert_frag` | One 4-byte range is visible to both vertex and fragment stages at offset 0; both generated shaders read the same `int kind`. |
| `shader_object_linked_binary` | This construction-mode leaf uses the same generated shader interfaces while exercising the linked-binary pipeline construction path. |

#### Purpose

This case checks that a value pushed into one range shared by the vertex and fragment stages is consumed correctly after graphics pipeline construction. The selector changes the generated stage outputs, making an incorrect range, offset, or stage association visible in the rendered image.

#### Structural Design

| Phase | Push-constant dataflow | Observable result |
|---|---|---|
| Host update | `vkCmdPushConstants` writes the 4-byte `kind` field at offset 0 for vertex and fragment stages. | Both stages can observe the same range. |
| Vertex stage | Reads `matInst.kind`, selects green, blue, red, or the incoming vertex color, and forwards the result as `vtxColor`. | The selected color is carried through the graphics interface. |
| Fragment stage | Reads the same `matInst.kind`; cases 0/1/2 select green/blue/`vtxColor`, and the default selects white. | The framebuffer color is compared against the reference renderer. |

#### Shader Code

##### Vertex Shader

```glsl
#version 450
#extension GL_EXT_long_vector : enable
layout(location = 0) in highp vec4 position;
layout(location = 1) in highp vec4 color;
layout(location = 0) out highp vec4 vtxColor;
out gl_PerVertex { vec4 gl_Position; };
/// The single declared range is shared by vertex and fragment stages.
layout(push_constant) uniform Material {
    int kind;
} matInst;
void main()
{
    gl_Position = position;
    /// The pushed selector controls the vertex-stage color payload.
    switch (matInst.kind) {
    case 0: vtxColor = vec4(0.0, 1.0, 0, 1.0); break;
    case 1: vtxColor = vec4(0.0, 0.0, 1.0, 1.0); break;
    case 2: vtxColor = vec4(1.0, 0.0, 0, 1.0); break;
    default: vtxColor = color; break;}
}
```

##### Fragment Shader

```glsl
#version 450
layout(location = 0) in highp vec4 vtxColor;
layout(location = 0) out highp vec4 fragColor;
/// The fragment stage consumes the same offset-zero four-byte range.
layout(push_constant) uniform Material {
    layout(offset = 0) int kind;
} matInst;
void main (void)
{
    /// Each selector value chooses a distinct output, making byte consumption visible.
    switch (matInst.kind) {
    case 0: fragColor = vec4(0, 1.0, 0, 1.0); break;
    case 1: fragColor = vec4(0, 0.0, 1.0, 1.0); break;
    case 2: fragColor = vtxColor; break;
    default: fragColor = vec4(1.0, 1.0, 1.0, 1.0); break;}
}
```

#### Additional Info

- The source emits the fragment push-constant member with `layout(offset = 0)` for this shared vertex/fragment range; the vertex declaration is equivalent because its first member is naturally at offset 0 ([graphics shader generator](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1264-L1491), [fragment generator](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1596-L1680)).
- The vertex shader is shown because it is the producer of `vtxColor` and is part of the selected graphics dataflow; the fragment shader remains the primary SPIR-V stage because it directly performs the final push-constant-selected framebuffer write.
- Graphics validation compares the submitted image with the `ReferenceRenderer` output, so a mismatch also includes possible rasterization, synchronization, readback, or reference-comparison causes ([graphics submission and comparison](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L678-L755)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Range size | Changes the push-constant member layout and generated read/aggregation logic: 4 bytes uses `int kind`, while 16/32/48/128/256-byte cases use different vector or array forms. | [range-size mapping and generator](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1202-L1232), [declaration and use](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1290-L1450) |
| Stage/range count | Adds push-constant declarations and consumers to vertex, fragment, geometry, or tessellation stages; a shared vertex/fragment range uses the same offset-zero selector represented here. | [graphics parameter table](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3384-L3419), [stage generators](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1272-L1680) |
| Index/update mode | Dynamic indexing replaces the literal selector with dynamically uniform vector, matrix, and array accesses; multi-update cases alter the host update sequence while preserving generated stage interfaces. | [dynamic-index generator](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1452-L1478), [registration table](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3347-L3450) |
| Command form | `_command2` uses `vkCmdPushConstants2KHR` with the same shader-side range semantics and requires `VK_KHR_maintenance6`; ordinary leaves use `vkCmdPushConstants`. | [registration and command selection](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3608-L3635), [support gate](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1154-L1161) |

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
               OpEntryPoint Vertex %main "main" %_ %position %vtxColor %color
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_long_vector"
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %position "position"
               OpName %Material "Material"
               OpMemberName %Material 0 "kind"
               OpName %matInst "matInst"
               OpName %vtxColor "vtxColor"
               OpName %color "color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %position Location 0
               OpDecorate %Material Block
               OpMemberDecorate %Material 0 Offset 0
               OpDecorate %vtxColor Location 0
               OpDecorate %color Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %Material = OpTypeStruct %int
%_ptr_PushConstant_Material = OpTypePointer PushConstant %Material
    %matInst = OpVariable %_ptr_PushConstant_Material PushConstant
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
   %vtxColor = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %32 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %34 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
         %36 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
      %color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
         %22 = OpAccessChain %_ptr_PushConstant_int %matInst %int_0
         %23 = OpLoad %int %22
               OpSelectionMerge %28 None
               OpSwitch %23 %27 0 %24 1 %25 2 %26
         %27 = OpLabel
         %39 = OpLoad %v4float %color
               OpStore %vtxColor %39
               OpBranch %28
         %24 = OpLabel
               OpStore %vtxColor %32
               OpBranch %28
         %25 = OpLabel
               OpStore %vtxColor %34
               OpBranch %28
         %26 = OpLabel
               OpStore %vtxColor %36
               OpBranch %28
         %28 = OpLabel
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
; Bound: 36
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %fragColor %vtxColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %Material "Material"
               OpMemberName %Material 0 "kind"
               OpName %matInst "matInst"
               OpName %fragColor "fragColor"
               OpName %vtxColor "vtxColor"
               OpDecorate %Material Block
               OpMemberDecorate %Material 0 Offset 0
               OpDecorate %fragColor Location 0
               OpDecorate %vtxColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
   %Material = OpTypeStruct %int
%_ptr_PushConstant_Material = OpTypePointer PushConstant %Material
    %matInst = OpVariable %_ptr_PushConstant_Material PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %fragColor = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %25 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
         %27 = OpConstantComposite %v4float %float_0 %float_0 %float_1 %float_1
%_ptr_Input_v4float = OpTypePointer Input %v4float
   %vtxColor = OpVariable %_ptr_Input_v4float Input
         %33 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpAccessChain %_ptr_PushConstant_int %matInst %int_0
         %13 = OpLoad %int %12
               OpSelectionMerge %18 None
               OpSwitch %13 %17 0 %14 1 %15 2 %16
         %17 = OpLabel
               OpStore %fragColor %33
               OpBranch %18
         %14 = OpLabel
               OpStore %fragColor %25
               OpBranch %18
         %15 = OpLabel
               OpStore %fragColor %27
               OpBranch %18
         %16 = OpLabel
         %31 = OpLoad %v4float %vtxColor
               OpStore %fragColor %31
               OpBranch %18
         %18 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

The graphics, compute, overwrite, and lifetime subsections below describe their device execution and host-side result checks.

### Compute and overwrite behavior

#### Compute simple and uninitialized paths

The compute shader writes eight output `vec4` elements. `simple_test` expects eight copies of `(1, 0, 0, 1)` after dispatch and host invalidation. `uninitialized` deliberately does not compare a value: after execution, it passes if reading the undefined value did not crash. This survival case requires `VK_KHR_maintenance4` ([shader setup](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2051-L2060), [maintenance4 gate](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2045-L2049), [verification](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2225-L2247)).

#### Overwrite shader and execution

`overwrite` is added to both graphics and monolithic compute groups. It uses a 2×2 `rgba8ui` storage image and four executions. Before each draw or dispatch, the host changes push-constant fields that select a pixel and calculate its color. The shader reads those fields and stores the result.

```glsl
#version 450
layout (push_constant, std430) uniform PushConstants {
    ivec4 coords;
    uvec4 baseColor;
    uvec4 multiplier;
    uint  colorOffsets[4];
    uvec4 transparentGreen;
} pc;
layout(rgba8ui, set=0, binding=0) uniform uimage2D simage;
void main() {
    uvec4 colorOffsets = uvec4(pc.colorOffsets[0], pc.colorOffsets[1],
                                pc.colorOffsets[2], pc.colorOffsets[3]);
    uvec4 finalColor = pc.baseColor * pc.multiplier + colorOffsets + pc.transparentGreen;
    imageStore(simage, pc.coords.xy, finalColor);
}
```

This is the GLSL emitted by the source for the compute stage and graphics fragment stage ([shader generator](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2994-L3035)). The graphics form also has a separate full-screen vertex shader; it does not read push constants. After image-to-buffer copy and host invalidation, the host recomputes each expected pixel using the same expression and compares all four `getPixelUint()` results ([readback and validation](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3250-L3289)).

### Lifetime sequences and checks

The lifetime leaves use fixed `CommandData` sequences rather than a cross-product. They cover binding a different layout with the same range, pushing through one layout then rebinding, overlapping ranges, and switching graphics and compute pipelines with same or different overlapping ranges ([lifetime table](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3512-L3604)). The instance decides whether a sequence produces graphics output, compute output, or both, then submits once ([execution completion](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2849-L2867)).

For graphics, the check uses the reference renderer and `intThresholdPositionDeviationCompare`. For compute, it invalidates the output allocation and compares eight `Vec4(0.25, 0.75, 0.75, 1.0)` values. A failure reports either `Image mismatch` or `Wrong output value` ([lifetime validation](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2870-L2927)). These checks locate an observable result inconsistency; they do not alone establish which command or layout transition caused it.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| Disjoint size/count/update/dynamic-index graphics | Push command byte interval, `VkPushConstantRange` stage/offset/size, shader-stage generation, and reference-render comparison. |
| Overlap or unused graphics | Overlap handling and whether declarations not consumed by a shader incorrectly affect values used by another stage. |
| `_command2` only | `VK_KHR_maintenance6` enablement and `vkCmdPushConstants2KHR` command path. |
| Long-vector only | `VK_EXT_shader_long_vector` feature path and long-vector shader lowering. |
| Graphics or compute overwrite | Repeated command updates and the storage-image output calculation/readback. |
| Compute simple | Compute push range, dispatch, output-buffer write, and host invalidation. |
| Compute uninitialized | This is a no-crash/survival case; first check maintenance4 support and undefined-value handling rather than an expected value. |
| Lifetime | Push-constant layout compatibility, command ordering, and graphics/compute bind-point state. |
| Broad failures | Pipeline construction requirements, command submission, generated shader interface, synchronization, or host result readback. |

### Cause Analysis

#### Range, stage, and command-form handling

**Possible failure symptoms:** Graphics output differs from the reference only for a particular range size, overlap, shader-stage combination, partial update, dynamic index, or `_command2` variant.

**Possible implementation causes:** The implementation may have associated updated bytes with the wrong offset, size, stage set, or compatible layout, or lowered a generated shader interface incorrectly. A failure confined to `_command2` after the maintenance6 support check points more specifically to the `VkPushConstantsInfoKHR` command path; a geometry-, tessellation-, or long-vector-only failure also requires investigation of that stage or type's shader lowering.

#### Repeated overwrite and storage-image path

**Possible failure symptoms:** One or more of the four integer pixels remains unchanged or differs from `baseColor * multiplier + colorOffsets + transparentGreen` after the repeated member updates.

**Possible implementation causes:** A stale or incorrectly bounded push update can produce that symptom, but the final image cannot isolate it from shader storage-image addressing, shader-write-to-transfer synchronization, image copy, or host readback failures. The source pushes every structure member separately before each execution and validates only the resulting pixels ([updates](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3187-L3238), [copy and comparison](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3243-L3289)).

#### Compute output and survival behavior

**Possible failure symptoms:** `simple_test` reports a vector different from `(1, 0, 0, 1)`, while `uninitialized` fails only if execution does not complete normally; the latter has no expected-value comparison.

**Possible implementation causes:** For `simple_test`, investigate compute push-constant consumption, dispatch, storage-buffer writes, shader-to-host synchronization, and invalidation. For `uninitialized`, investigate maintenance4 undefined-value handling or a device failure during the dynamically unused read path rather than assigning significance to the returned bytes.

#### Compatible-layout and bind-point state

**Possible failure symptoms:** A lifetime leaf reports `Image mismatch` or `Wrong output value` after one of its fixed graphics/compute bind, push, draw, and dispatch sequences.

**Possible implementation causes:** The implementation may have incorrectly preserved or disturbed push-constant state across compatible or overlapping layouts, or associated state with the wrong graphics or compute bind point. Because validation sees only final graphics or compute output, it cannot identify a particular transition without comparing which lifetime sequences fail.

## Case Pruning

### Requirement-based pruning

- The enclosing pipeline category excludes the whole family in Vulkan SC builds ([dispatcher guard](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L125-L131)). Within the source, `_command2` registration is also skipped in Vulkan SC ([command2 guard](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3609-L3615)).
- `_command2` needs `VK_KHR_maintenance6`; `uninitialized` needs `VK_KHR_maintenance4`; long-vector entries need the long-vector feature; and stage-specific configurations need geometry or tessellation support.
- Fixed-size configurations larger than `maxPushConstantsSize` produce `NotSupportedError`; `range_size_max` instead queries a suitable size from the device ([support logic](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1154-L1200)).
- Compute is deliberately monolithic-only by registration, so the non-monolithic split mustpass lists have no compute leaves.

### Design-based pruning

- Range sizes sample minimum, common specification-limit milestones, long-vector forms, and the implementation maximum; they do not enumerate every aligned size.
- Stage coverage samples one shared range and 2-, 3-, and 5-range arrangements rather than every stage-mask permutation.
- Overlap coverage uses four selected layouts; unused coverage uses six disjoint and six overlap representatives.
- Lifetime uses nine meaningful command sequences, not every permutation of push, bind, draw, and dispatch operations.

## Key Takeaways

- The five split pipeline mustpass lists each encode the same 62 non-monolithic leaves: 53 graphics plus 9 lifetime. Compute is source-registered only for monolithic construction.
- `_command2`, long-vector, geometry, tessellation, maximum-size, and uninitialized configurations have distinct support behavior; a missing feature is not a value mismatch.
- Graphics validation is image-versus-reference; simple compute validation is an eight-vector byte comparison; uninitialized compute is survival-only; overwrite uses four independently calculated storage-image pixels.
- The lifetime tests test observable outcomes of particular compatible and overlapping layout/bind sequences. A failure narrows investigation to those sequences but does not by itself prove a specific Vulkan implementation defect.

## Source Reference Appendix

| Topic | Evidence |
|---|---|
| Pipeline-category registration and Vulkan SC exclusion | [`vktPipelineTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L125-L131) |
| Group construction, parameter tables, and leaf registration | [`vktPipelinePushConstantTests.cpp`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3337-L3832) |
| Graphics support requirements | [graphics `checkSupport`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1154-L1200) |
| Graphics reference comparison | [graphics `iterate` and `verifyImage`](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L678-L755) |
| Compute requirements and checks | [compute support and verification](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2045-L2049), [compute result check](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2225-L2247) |
| Lifetime execution and validation | [completion](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2849-L2867), [validator](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2870-L2927) |
| Overwrite shader and validation | [GLSL generation](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L2994-L3035), [pixel comparison](../../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L3250-L3289) |
| Non-monolithic mustpass coverage | [`external/vulkancts/mustpass/main/vk-default/pipeline/`](../../../mustpass/main/vk-default/pipeline/) — five lists named in the registration section, each with 62 `push_constant` paths |
| Push constant specification | [ranges and layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1702-L1891), [updates and compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L5160-L5295), [common validity](../../../../vulkan-docs/src/chapters/commonvalidity/push_constants_common.adoc#L5-L26) |
