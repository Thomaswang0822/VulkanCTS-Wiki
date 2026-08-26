## Overview

**Core question:** Do dynamic descriptor offsets select the intended aligned buffer regions for graphics, compute, and mixed pipeline work?

- [`vktPipelineDynamicOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1) implements the `dynamic_offset` test family under the `pipeline` test category.
- The family covers graphics and compute cases with dynamic uniform or storage buffer descriptors, plus monolithic mixed graphics-and-compute cases.
- Each case binds descriptor sets with an offset array, executes a draw, dispatch, or both, and checks image data, buffer data, or both.
- This page explains the registered matrix, the offset-ordering behavior, host/device flow, and what a mismatch can mean.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC` or `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC` descriptor combines a descriptor base offset with a dynamic offset supplied at bind time. Vulkan uses their sum as the effective address while keeping the descriptor range fixed ([descriptor buffer information](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3571-L3574), [effective dynamic offset](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4638-L4643)).
- Vulkan consumes dynamic offsets in set order, then binding-number order, then array-element order. `dynamicOffsetCount` must equal the number of dynamic descriptors ([dynamic-offset binding order](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4627-L4636)). The test changes how descriptors are grouped to expose mistakes in that ordering.
- Uniform and storage dynamic offsets use different device alignment limits. The source pads its color blocks to the selected limit before creating offset values.

## Registration Hierarchy

```text
pipeline.monolithic.dynamic_offset
├── graphics
├── compute
└── combined_descriptors
```

The `graphics` intermediate node is registered for each construction root. The `compute` and `combined_descriptors` intermediate nodes are added only below `monolithic.dynamic_offset` because compute cannot use the graphics-pipeline-library construction in this implementation. The source registration is in [`createDynamicOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2310-L2545).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Direct intermediate node | `graphics`, `compute`, `combined_descriptors` | Selects the observable pipeline path and result oracle. | [`createDynamicOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2372-L2482) |
| Grouping strategy | `single_set`, `multiset`, `arrays` | Places dynamic descriptors in one set, separate sets, or descriptor arrays. | [`GroupingStrategy`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L71-L75) and layout setup ([compute](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L948-L969)) |
| Descriptor type | `uniform_buffer`, `storage_buffer` | Selects the dynamic descriptor alignment and buffer type. | [`descriptorTypes`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2325-L2330) |
| Command buffers | `numcmdbuffers_1`, `numcmdbuffers_2` | Tests one command buffer or multiple submissions. | [`numCmdBuffers`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2332-L2336) |
| Order | `sameorder`, `reverseorder` | Changes the order in which command buffers are recorded and submitted. `reverseorder` requires two buffers. | [`reverseOrders`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2338-L2343) |
| Descriptor-set bindings | `numdescriptorsetbindings_1`, `numdescriptorsetbindings_2` | Changes the number of descriptor-set bind operations. The value `2` is omitted with two command buffers. | [`numDescriptorSetBindings`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2344-L2348) |
| Dynamic bindings | `numdynamicbindings_1`, `numdynamicbindings_2` | Changes how many input descriptors receive dynamic offsets. | [`numDynamicBindings`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2350-L2354) |
| Non-dynamic bindings | `numnondynamicbindings_0`, `numnondynamicbindings_1` | Adds fixed-offset descriptors beside the dynamic descriptors. | [`numNonDynamicBindings`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2356-L2360) |
| Bind command | `bind`, `bind2` | Selects `vkCmdBindDescriptorSets`; `bind2` selects `vkCmdBindDescriptorSets2KHR` and is absent on VulkanSC. | [`descriptorBindCommands`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2362-L2370) |
| Combined offset mode | `all_offsets`, `single_offset` | Varies every mixed instance or targets one selected offset. | [`combined_descriptors` registration](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2478-L2542) |
| Combined descriptor order | `same_order`, `reverse_order` | Reorders the five mixed descriptor bindings and the offset-array mapping. | [`orders`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2484-L2489) |
| Combined offset count | `16`, `64`, `256` | Selects the number of aligned instances exercised by the mixed case. | [`numOffsets`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2491-L2497) |
| Combined pipeline order | `graphics_first`, `compute_first` | Runs the graphics and compute paths in opposite order. | [`pipelineOrders`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2499-L2503) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node below the `dynamic_offset` test family. This choice changes which descriptor consumers run and which observable output the host validates.

### `graphics`: Graphics pipeline dynamic offsets

The `graphics` intermediate node binds dynamic UBO or SSBO descriptors before drawing colored quads. It uses the grouping, descriptor-count, command-buffer, ordering, and bind-command dimensions to vary the mapping from offset-array entries to descriptors. The image comparison detects a quad that uses data from the wrong buffer region.

### `compute`: Compute pipeline dynamic offsets

The `compute` intermediate node binds the same classes of dynamic input descriptors and a dynamic output storage descriptor, then dispatches once per binding operation. The compute shader sums selected color blocks into aligned output slots. This intermediate node exists only for the monolithic construction type.

### `combined_descriptors`: Mixed graphics and compute descriptors

The monolithic-only `combined_descriptors` intermediate node places three dynamic UBOs and two dynamic SSBOs in one descriptor set. Graphics reads vertex, shared, and fragment data; compute reads shared and input SSBO data and writes an output SSBO. `same_order` and `reverse_order` change the descriptor binding order, so the five supplied offsets must follow the resulting binding order.

Within this intermediate node, `all_offsets` exercises every instance in a repeated pattern. `single_offset` supplies explicit offsets for the vertex UBO, shared UBO, fragment UBO, SSBO read, and SSBO write paths, allowing one selected instance to become visible in each output.

## Shader Analysis

The representative case is the graphics `arrays` path with one dynamic storage-buffer descriptor and no non-dynamic descriptors. `DynamicOffsetGraphicsTest::initPrograms()` emits a vertex shader that sums the selected descriptor element into the vertex color; the fragment shader simply forwards that color. The host creates the aligned color blocks, binds the descriptor array at set 0/binding 0, and supplies one dynamic offset per bind operation, so the shader makes an incorrect offset-to-region association visible as an image mismatch.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.shader_object_linked_binary.dynamic_offset.graphics.arrays.storage_buffer.numcmdbuffers_1.sameorder.numdescriptorsetbindings_1.numdynamicbindings_1.numnondynamicbindings_0.bind
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `graphics` | Selects the vertex/fragment graphics path and image-comparison oracle. |
| `arrays` + `storage_buffer` | Places dynamic descriptors in an array at set 0/binding 0 and uses `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC`, so the host-selected offset addresses a padded color block. |
| `numcmdbuffers_1` + `sameorder` + `numdescriptorsetbindings_1` | Records one command buffer, one descriptor-set bind, and one draw without command-buffer reordering. |
| `numdynamicbindings_1` + `numnondynamicbindings_0` + `bind` | Supplies one dynamic offset and no fixed-offset descriptor, using `vkCmdBindDescriptorSets`. |

#### Purpose

The shader renders the vertex geometry with the RGB value read from the dynamically selected storage-buffer region. The image check therefore detects whether the implementation consumes the dynamic offset for the descriptor-array element and selects the intended aligned color block.

#### Structural Design

| Phase | Shader operation | Observable effect |
|---|---|---|
| Inputs | Read `position` and the interpolated `color` input interface; declare `inputDataDyn[1]`. | Vertex position is supplied by the host; the descriptor is the shader-visible dynamic resource. |
| Vertex setup | Copy `position` to `gl_Position` and initialize `vtxColor` to opaque black. | Geometry is unchanged by descriptor addressing. |
| Descriptor contribution | Add `inputDataDyn[0].color.rgb` to `vtxColor.rgb`. | The effective dynamic offset selects the rendered RGB block. |
| Fragment handoff | Pass `vtxColor` to the fragment stage, which writes it unchanged. | A wrong descriptor region becomes an image-color mismatch. |

#### Shader Code

The vertex stage is the primary shader because it reads the dynamic descriptor; the fragment stage is fixed pass-through code and is not independently varied by this case.

```glsl
#version 450
/// Per-vertex position and color arrive from the host vertex buffer at locations 0 and 1.
layout(location = 0) in highp vec4 position;
layout(location = 1) in highp vec4 color;
/// The fragment stage consumes the accumulated color at location 0.
layout(location = 0) out highp vec4 vtxColor;
/// This one-element descriptor array is set 0, binding 0. Its readonly storage-buffer descriptor is dynamic on the host.
layout(set = 0, binding = 0) readonly buffer Block0
{
    vec4 color;
} inputDataDyn[1];

/// The explicit block exposes the vertex-stage built-in position written below.
out gl_PerVertex { vec4 gl_Position; };

void main()
{
    /// Geometry comes directly from the vertex input; the descriptor affects only the rendered color.
    gl_Position = position;
    vtxColor = vec4(0, 0, 0, 1);
    /// The dynamically selected buffer region supplies the sole RGB contribution in this case.
    vtxColor.rgb += inputDataDyn[0].color.rgb;
}
```

#### Additional Info

- `colorBlockInputSize` is `kColorSize` rounded up to the selected storage-buffer alignment; each descriptor's base offset is then combined with the dynamic offset supplied at bind time ([graphics initialization](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L227-L239), [descriptor updates](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L498-L545)).
- The source emits `inputDataDyn[1]` once for the arrays strategy and accesses element zero for this one-dynamic-binding representative case ([shader generation](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L810-L852)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Grouping strategy | `single_set` and `multiset` change descriptor set/binding declarations and access suffixes; `arrays` declares dynamic and non-dynamic descriptor arrays once per type. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L810-L852) |
| Descriptor type | `uniform_buffer` changes the block qualifier to `uniform`; `storage_buffer` uses `readonly buffer`, as in this representative shader. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L799-L802) |
| Dynamic/non-dynamic binding counts | The generator emits one contribution per descriptor; increasing either count changes declarations and the RGB sum. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L799-L853) |
| Command/bind parameters | Command-buffer count, submission order, descriptor-set bind count, and `bind` versus `bind2` alter host binding behavior but do not change this generated vertex source. | [`init()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L636-L687), [`createDynamicOffsetTests()`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2332-L2370) |

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
; Bound: 46
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %position %vtxColor %color
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %position "position"
               OpName %vtxColor "vtxColor"
               OpName %Block0 "Block0"
               OpMemberName %Block0 0 "color"
               OpName %inputDataDyn "inputDataDyn"
               OpName %color "color"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %position Location 0
               OpDecorate %vtxColor Location 0
               OpDecorate %Block0 BufferBlock
               OpMemberDecorate %Block0 0 NonWritable
               OpMemberDecorate %Block0 0 Offset 0
               OpDecorate %inputDataDyn NonWritable
               OpDecorate %inputDataDyn Binding 0
               OpDecorate %inputDataDyn DescriptorSet 0
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
   %vtxColor = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %21 = OpConstantComposite %v4float %float_0 %float_0 %float_0 %float_1
     %Block0 = OpTypeStruct %v4float
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_Block0_uint_1 = OpTypeArray %Block0 %uint_1
%_ptr_Uniform__arr_Block0_uint_1 = OpTypePointer Uniform %_arr_Block0_uint_1
%inputDataDyn = OpVariable %_ptr_Uniform__arr_Block0_uint_1 Uniform
    %v3float = OpTypeVector %float 3
%_ptr_Uniform_v4float = OpTypePointer Uniform %v4float
     %uint_0 = OpConstant %uint 0
%_ptr_Output_float = OpTypePointer Output %float
     %uint_2 = OpConstant %uint 2
      %color = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
               OpStore %vtxColor %21
         %30 = OpAccessChain %_ptr_Uniform_v4float %inputDataDyn %int_0 %int_0
         %31 = OpLoad %v4float %30
         %32 = OpVectorShuffle %v3float %31 %31 0 1 2
         %33 = OpLoad %v4float %vtxColor
         %34 = OpVectorShuffle %v3float %33 %33 0 1 2
         %35 = OpFAdd %v3float %34 %32
         %38 = OpAccessChain %_ptr_Output_float %vtxColor %uint_0
         %39 = OpCompositeExtract %float %35 0
               OpStore %38 %39
         %40 = OpAccessChain %_ptr_Output_float %vtxColor %uint_1
         %41 = OpCompositeExtract %float %35 1
               OpStore %40 %41
         %43 = OpAccessChain %_ptr_Output_float %vtxColor %uint_2
         %44 = OpCompositeExtract %float %35 2
               OpStore %43 %44
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The graphics instance determines the selected uniform or storage alignment, pads input color blocks, creates a color image and render passes, builds descriptor layouts, and writes host-visible vertex data ([graphics initialization](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L215-L692)).
- For each command buffer, it binds the pipeline and vertex buffer, creates the dynamic-offset array, binds descriptor sets with either `vkCmdBindDescriptorSets` or `vkCmdBindDescriptorSets2KHR`, and draws one quad for each descriptor-set binding. The command-buffer index is reversed when `reverseorder` is selected.
- After submission, graphics compares the image against the reference renderer with `tcu::intThresholdPositionDeviationCompare()` and threshold `UVec4(2, 2, 2, 2)` ([image verification](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L709-L758)).
- The compute instance creates aligned input and output buffers, writes each descriptor's base range, records offsets for dynamic input and output descriptors, dispatches, and inserts a compute-to-host barrier ([compute command recording](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1216-L1293)). It invalidates the output allocation and compares every `Vec4` with the calculated reference ([compute verification](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1311-L1344)).
- The combined instance creates vertex, color, and SSBO resources, records one command buffer at a time, and submits each recording immediately. It alternates graphics and compute work in the selected order, then binds five offsets per instance ([combined binding](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1965-L2053)). It compares the copied image with `tcu::floatThresholdCompare()` at `0.01f`, then compares SSBO vectors with `0.01f` tolerance ([combined checks](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L2056-L2153)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `graphics` | Dynamic-offset address calculation, offset-array ordering, graphics descriptor binding, or image result handling selects wrong data. |
| `compute` | Dynamic-offset address calculation, offset-array ordering, compute descriptor binding, or output-buffer visibility selects wrong data. |
| `combined_descriptors` with `all_offsets` | One or more UBO or SSBO offsets, their alignment, or their reordered binding association selects the wrong region across repeated draws or dispatches. |
| `combined_descriptors` with `single_offset` | A selected UBO, SSBO-read, or SSBO-write offset selects the wrong single target, or graphics and compute use inconsistent descriptor bindings. |

### Cause Analysis

#### `graphics` intermediate node

**Possible failure symptoms:** The rendered quads have the wrong colors or positions, and image comparison reports a mismatch.

**Possible implementation causes:** The implementation may add the dynamic offset to the wrong descriptor base, consume offset entries in the wrong set/binding/array order, or apply a descriptor binding to the wrong graphics pipeline state. The host-side source and image comparison cannot distinguish these subcauses without further investigation.

#### `compute` intermediate node

**Possible failure symptoms:** One or more host-visible output `Vec4` values differ from the color sum calculated by the CTS.

**Possible implementation causes:** The implementation may select an incorrect dynamic input or output region, mishandle alignment, associate offsets with the wrong compute binding, or expose shader writes to the host incorrectly. Source-level investigation is needed to separate descriptor addressing from synchronization or readback defects.

#### Combined descriptors with `all_offsets`

**Possible failure symptoms:** The image gradient or one or more SSBO vectors differs from its expected value after repeated graphics and compute operations.

**Possible implementation causes:** The implementation may apply the five dynamic offsets in the wrong order, mishandle the reordered descriptor layout, or retain stale binding state between draws and dispatches. The combined oracle shows the selected data is wrong but cannot isolate one of the five bindings when their contributions overlap.

#### Combined descriptors with `single_offset`

**Possible failure symptoms:** The selected colored square is at the wrong location, the image uses the wrong color, or the expected SSBO write slot remains unchanged or changes at another index.

**Possible implementation causes:** The implementation may map one explicit offset to the wrong UBO or SSBO, use the wrong binding numbers after `reverse_order`, or fail to preserve descriptor state across the graphics-first and compute-first sequences. Further source-level investigation is needed when more than one result differs.

## Case Pruning

### Requirement-based pruning

- The source omits `bind2` on Vulkan SC at compile time. On supported non-SC builds, the test's support check requires the pipeline construction requirements and `VK_KHR_maintenance6` for the `bind2` path ([support check](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L789-L795)).

### Design-based pruning

- The factory skips `reverseorder` when `numCmdBuffers` is one because there is no second command buffer to reorder.
- It skips `numDescriptorSetBindings == 2` when two command buffers are selected, avoiding that combination in the registered matrix.
- It omits `compute` and `combined_descriptors` for non-monolithic construction types because the implementation excludes compute from those pipeline construction modes.
- The inspected split `vk-default/pipeline` mustpass scope contains 1,560 matching leaves: 408 in `monolithic/monolithic.txt` and 192 in each of `pipeline-library.txt`, `fast-linked-library.txt`, `shader-object-linked-binary.txt`, `shader-object-linked-spirv.txt`, `shader-object-unlinked-binary.txt`, and `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`.

## Key Takeaways

- Dynamic descriptor offsets are relative additions to descriptor base offsets, and Vulkan orders the offset array by set, binding, and array element.
- The ordinary `graphics` and `compute` intermediate nodes stress descriptor grouping, descriptor type, command-buffer order, dynamic/non-dynamic mixtures, and both bind command forms.
- The combined monolithic intermediate node makes five reordered UBO and SSBO bindings observable through both graphics and compute outputs.
- A failure proves that an expected image or buffer value was not produced. The exact fault location requires follow-up investigation of offset mapping, descriptor state, shader access, synchronization, or host readback.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Original navigation page | [`vktPipelineDynamicOffsetTests.md`](vktPipelineDynamicOffsetTests.md) |
| Implementation and registration | [`vktPipelineDynamicOffsetTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp) |
| Public declaration | [`vktPipelineDynamicOffsetTests.hpp`](../../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.hpp) |
| Pipeline category registration | [`vktPipelineTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L102-L115) |
| Dynamic descriptor semantics | [`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3571-L3574) and [`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4627-L4672) |
| Split mustpass directory | [`vk-default/pipeline`](../../../mustpass/main/vk-default/pipeline/) |
