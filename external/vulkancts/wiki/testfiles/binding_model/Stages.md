## Overview

**Core question:** Does one stage-scoped descriptor-set bind establish valid bindings for both graphics and compute pipelines?

- [`vktBindingStagesTests.cpp`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L1-L617) implements the `binding_model.stages` test family.
- The family contains exactly three descriptor-type test case leaves: `storage_buffer`, `uniform_buffer`, and `combined_image_sampler`.
- Each case updates two descriptor sets, then calls `vkCmdBindDescriptorSets2` once with fragment and compute stage bits. It draws before dispatching, using one pipeline layout for both pipelines.
- The fragment shader produces a color image and the compute shader produces four floats. The host checks both outputs, so the test can detect a binding that works at one pipeline bind point but not the other.

## Background Knowledge

For the shared concepts of descriptor interfaces, pipeline layouts, validity, and availability and visibility, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Stage-scoped descriptor-set binding.** `VkBindDescriptorSetsInfo::stageFlags` selects shader stages, then applies the binding to every pipeline bind point represented by those stages. Fragment plus compute is equivalent to one traditional graphics bind and one traditional compute bind ([`VkBindDescriptorSetsInfo`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4720-L4764)).
- **Pipeline layouts and bind points.** Compatible pipeline layouts let a descriptor set remain valid across pipeline changes. Graphics and compute pipeline bindings are independent; binding one does not disturb the other ([pipeline layout compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055), [pipeline bind points](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9794-L9819)).

## Registration Hierarchy

```text
binding_model.stages
├── storage_buffer
├── uniform_buffer
└── combined_image_sampler
```

The binding-model factory adds `stages` only outside `CTS_USES_VULKANSC` builds ([`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71)). [`createStagesTests()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L586-L613) creates the family and its three direct leaves. The default Vulkan mustpass file confirms `dEQP-VK.binding_model.stages.combined_image_sampler`, `dEQP-VK.binding_model.stages.storage_buffer`, and `dEQP-VK.binding_model.stages.uniform_buffer` ([mustpass paths](../../../mustpass/main/vk-default/binding-model.txt#L146932-L146934)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Descriptor-type test case leaf | `storage_buffer`, `uniform_buffer`, `combined_image_sampler` | Selects the set 0 descriptor type, input resource, shader declarations, read operation, and image setup requirements. | [`descriptorTypeTests`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L592-L610) |
| Descriptor-binding stage mask | `VK_SHADER_STAGE_FRAGMENT_BIT | VK_SHADER_STAGE_COMPUTE_BIT` | Makes one `vkCmdBindDescriptorSets2` operation apply descriptor-set state to graphics and compute bind points. | [set layouts](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L100-L110), [bind info](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L372-L384) |
| Pipeline operation | graphics draw, then compute dispatch | Observes set 0 through a fragment shader and a compute shader after the single binding call. | [command order](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L404-L412) |
| Output observation | `32 x 32` RGBA image, four-float storage buffer | Separates graphics and compute evidence while keeping the expected logical values equivalent. | [output setup](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L303-L350), [checks](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L436-L468) |
| Required functionality | `VK_KHR_maintenance6` | Provides the `vkCmdBindDescriptorSets2` path used by every leaf. | [`checkSupport()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L579-L582) |

## Behavior Parameters

The primary behavioral axis is the descriptor-type test case leaf under `binding_model.stages`. It changes how set 0 represents and reads the same four logical values while the one-call binding mechanism, pipeline layout, command order, and result checks stay fixed.

### `storage_buffer` - Storage-block reads at both bind points

Set 0 binding 0 is a `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` backed by a 16-byte host-visible buffer containing `1.0` through `4.0`. The compute shader indexes a runtime float array and copies one value per invocation to set 1. The fragment shader reads all four array entries, divides them by four, and writes the expected color ([buffer setup](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L143-L187), [shader branches](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L498-L503)).

### `uniform_buffer` - Uniform-block reads at both bind points

Set 0 binding 0 is a `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` backed by the same four floats. The shaders declare one `vec4 readValues`, then index its components for compute output or construct the normalized fragment color. This leaf keeps the values and commands fixed while changing descriptor-class handling and uniform-block access ([uniform declaration branches](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L504-L509), [buffer shader operations](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L519-L523)).

### `combined_image_sampler` - Texture reads at both bind points

Set 0 binding 0 combines a sampler and a view of a `4 x 4` `VK_FORMAT_R8G8B8A8_UNORM` image. The host uploads repeating RGBA bytes close to quarter steps, then transitions the image to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`. Compute samples at `(0, 0)` and multiplies each selected component by four; fragment samples at `(0.5, 0.5)` and writes the color directly ([image and descriptor setup](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L189-L300), [image shader operations](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L510-L512), [sampling branches](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L524-L527)).

## Shader Analysis

Two walkthroughs distinguish the materially different shader resource paths. The storage-buffer compute shader shows indexed buffer input and the set 1 result write. The combined-image-sampler fragment shader shows image sampling and graphics output. The uniform-buffer leaf changes the set 0 declaration to a uniform `vec4` but keeps the buffer arithmetic, so a third walkthrough would repeat the same logic.

The reconstructed GLSL bytes were compiled with `glslangValidator` 16.3.0 using `-V --target-env spirv1.0` and the exact stage, validated with `spirv-val` from SPIRV-Tools v2026.2 using `--target-env spv1.0`, and disassembled with `spirv-dis` from SPIRV-Tools v2026.2. `initPrograms()` supplies no explicit build options, so SPIR-V 1.0 matches the CTS baseline target ([baseline target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)).

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.stages.storage_buffer
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `storage_buffer` | Set 0 exposes the initialized input as a runtime float array in a storage block. |
| Compute stage | Exercises the compute bind point and writes the observed values to set 1 for host comparison. |
| Four invocations | `gl_GlobalInvocationID.x` selects one of the four initialized floats. |

#### Purpose

The shader proves that the one stage-scoped binding call made both descriptor sets usable by the compute pipeline. Each invocation copies one value from set 0 to the host-readable result in set 1.

#### Structural Design

| Shader object | Operation | Observable result |
|---------------|-----------|-------------------|
| Set 0 binding 0 `readBuffer` | Load `readValues[gl_GlobalInvocationID.x]`. | Reads one of `1.0`, `2.0`, `3.0`, `4.0` through the selected descriptor. |
| Set 1 binding 0 `writeBuffer` | Store the loaded float at the same index. | Lets the host verify compute descriptor state independently from graphics output. |

#### Shader Code

```glsl
#version 450

/// Set 0 carries the selected storage-buffer input and is visible to compute and fragment stages.
layout(set = 0, binding = 0) buffer readBuffer{
    float readValues[];
};
/// Set 1 is the compute result buffer; four invocations write one float each.
layout(set = 1, binding = 0) buffer writeBuffer{
    float writeValues[];
};

void main (void) {
    /// Copy one input element so the host can compare the compute result with 1, 2, 3, 4.
    writeValues[gl_GlobalInvocationID.x] = readValues[gl_GlobalInvocationID.x];
}
```

#### Additional Info

- The source adds the compute shader as `glu::ComputeSource` without an explicit local-size declaration. GLSL therefore uses the default local size of one, and `vkCmdDispatch(4, 1, 1)` produces four invocations ([program insertion](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L529-L531), [dispatch](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L411-L412)).
- The fragment shader for this leaf uses the same set 0 block and reads all four floats to produce the color image. Set 1 is not statically used by the graphics shaders.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| `uniform_buffer` | Replaces the runtime storage array with a uniform block containing `vec4 readValues`; the indexed copy expression stays the same. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L504-L523) |
| `combined_image_sampler` | Replaces the buffer block with `sampler2D`; compute samples at `(0, 0)`, selects a component by invocation index, and multiplies it by four. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L510-L527) |
| Fragment stage | Removes set 1, reads all four buffer values, divides them by four, and writes location 0. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L543-L576) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 31
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %writeBuffer "writeBuffer"
               OpMemberName %writeBuffer 0 "writeValues"
               OpName %_ ""
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %readBuffer "readBuffer"
               OpMemberName %readBuffer 0 "readValues"
               OpName %__0 ""
               OpDecorate %_runtimearr_float ArrayStride 4
               OpDecorate %writeBuffer BufferBlock
               OpMemberDecorate %writeBuffer 0 Offset 0
               OpDecorate %_ Binding 0
               OpDecorate %_ DescriptorSet 1
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %_runtimearr_float_0 ArrayStride 4
               OpDecorate %readBuffer BufferBlock
               OpMemberDecorate %readBuffer 0 Offset 0
               OpDecorate %__0 Binding 0
               OpDecorate %__0 DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_runtimearr_float = OpTypeRuntimeArray %float
%writeBuffer = OpTypeStruct %_runtimearr_float
%_ptr_Uniform_writeBuffer = OpTypePointer Uniform %writeBuffer
          %_ = OpVariable %_ptr_Uniform_writeBuffer Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %uint_0 = OpConstant %uint 0
%_ptr_Input_uint = OpTypePointer Input %uint
%_runtimearr_float_0 = OpTypeRuntimeArray %float
 %readBuffer = OpTypeStruct %_runtimearr_float_0
%_ptr_Uniform_readBuffer = OpTypePointer Uniform %readBuffer
        %__0 = OpVariable %_ptr_Uniform_readBuffer Uniform
%_ptr_Uniform_float = OpTypePointer Uniform %float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %19 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %20 = OpLoad %uint %19
         %25 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %26 = OpLoad %uint %25
         %28 = OpAccessChain %_ptr_Uniform_float %__0 %int_0 %26
         %29 = OpLoad %float %28
         %30 = OpAccessChain %_ptr_Uniform_float %_ %int_0 %20
               OpStore %30 %29
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.stages.combined_image_sampler
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `combined_image_sampler` | Set 0 contains the image view and sampler used through one `sampler2D`. |
| Fragment stage | Exercises the graphics bind point and writes the sampled value to the color attachment. |
| Center coordinate `(0.5, 0.5)` | Samples the initialized image. Every texel carries the same RGBA pattern. |

#### Purpose

The shader proves that the same descriptor-set binding operation made the combined image sampler usable by the graphics pipeline. Its sampled color becomes the independent graphics result.

#### Structural Design

| Shader object | Operation | Observable result |
|---------------|-----------|-------------------|
| Set 0 binding 0 `readImage` | Sample at normalized coordinate `(0.5, 0.5)`. | Reads the uploaded quarter-step RGBA value through the image view and sampler. |
| Location 0 `color` | Store the sampled `vec4`. | Fills the color attachment for image-to-buffer copy and host comparison. |

#### Shader Code

```glsl
#version 450

/// Set 0 carries the combined image sampler shared by the fragment and compute stages.
layout(set = 0, binding = 0) uniform sampler2D readImage;
/// The fragment stage writes the sampled value into the color attachment for host readback.
layout(location = 0) out vec4 color;
void main (void) {
    /// Every covered pixel samples the center of the initialized 4 by 4 image.
    color = texture(readImage, vec2(0.5f));
}
```

#### Additional Info

- The fixed vertex shader generates the four framebuffer-covering corners from `gl_VertexIndex`. It does not access a descriptor and does not participate in the tested binding state ([vertex shader generation](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L533-L541)).
- The image contains the same byte pattern in every texel, so linear filtering and the selected coordinate do not change the expected value.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Compute stage | Keeps `sampler2D`, adds the set 1 storage block, samples at `(0, 0)`, selects a component using `gl_GlobalInvocationID.x`, and multiplies by four. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L510-L527) |
| Buffer leaves | Replace `sampler2D` and `texture` with a storage-array or uniform-`vec4` declaration and direct component reads divided by four. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L546-L573) |
| Vertex stage | Stays fixed for all leaves and has no descriptor declarations. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L533-L541) |

#### SPIR-V

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
               OpEntryPoint Fragment %main "main" %color
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %color "color"
               OpName %readImage "readImage"
               OpDecorate %color Location 0
               OpDecorate %readImage Binding 0
               OpDecorate %readImage DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %color = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float 2D 0 0 0 1 Unknown
         %11 = OpTypeSampledImage %10
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
  %readImage = OpVariable %_ptr_UniformConstant_11 UniformConstant
    %v2float = OpTypeVector %float 2
  %float_0_5 = OpConstant %float 0.5
         %17 = OpConstantComposite %v2float %float_0_5 %float_0_5
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpLoad %11 %readImage
         %18 = OpImageSampleImplicitLod %v4float %14 %17
               OpStore %color %18
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The host creates set 0 with the selected read descriptor and set 1 with a storage-buffer descriptor. Both layout bindings are visible to fragment and compute stages. One shared pipeline layout contains the two set layouts ([descriptor layouts](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L90-L113)).
- Buffer leaves allocate a 16-byte host-visible input buffer, update set 0 with `VK_WHOLE_SIZE`, write `1.0` through `4.0`, and flush the allocation. The image leaf creates a `4 x 4` UNORM image, view, and linear clamp sampler; updates set 0; then copies repeated `63`, `127`, `191`, `255` bytes into the image. Transfer barriers move it from undefined to transfer destination, then to shader-read-only with visibility for fragment and compute shader reads ([input setup](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L116-L300)).
- The host creates the four-float write buffer and updates set 1. It also creates a `32 x 32` color image, render pass, framebuffer, and host-visible transfer destination for color readback ([output resources](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L303-L350), [color output buffer](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L386-L390)).
- Graphics and compute pipelines use the same pipeline layout. `VkBindDescriptorSetsInfoKHR` names both descriptor sets and uses `VK_SHADER_STAGE_FRAGMENT_BIT | VK_SHADER_STAGE_COMPUTE_BIT`. The host records exactly one `vkCmdBindDescriptorSets2` before binding either pipeline ([pipelines and bind info](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L352-L405)).
- The command buffer binds `VK_PIPELINE_BIND_POINT_GRAPHICS`, calls `vkCmdDraw` for four vertices, ends the render pass, then binds `VK_PIPELINE_BIND_POINT_COMPUTE` and calls `vkCmdDispatch` with `(4, 1, 1)`. The draw and dispatch both read set 0 but write separate outputs. No inter-operation data hazard requires a graphics-to-compute memory barrier ([mixed command order](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L407-L412)).
- After the dispatch command, a barrier makes color attachment writes available for transfer reads and changes the color image to `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL`. The host records an image-to-buffer copy, submits the command buffer once, and waits for completion ([color copyback](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L414-L434)).
- The host invalidates the compute output allocation and compares its four floats with `1.0`, `2.0`, `3.0`, `4.0`. Any absolute difference of at least `0.02` fails the case.
- The host invalidates the color output allocation and scans all four components of every `32 x 32` pixel. The expected value is `(0.25, 0.5, 0.75, 1.0)`, again with an exclusive `0.02` tolerance. The case passes only after both result paths match ([result comparisons](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L436-L468)).

## Failure Meaning

A failure means at least one selected bind point did not produce the expected descriptor-backed result, or that a resource, execution, synchronization, or readback step corrupted that result. The two outputs narrow the symptom: the float buffer observes compute, and the color image observes graphics. A single mismatch does not identify the implementation layer by itself.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `storage_buffer` | Storage-buffer descriptor binding or stage visibility failure, storage-buffer load failure, or shared graphics/compute execution and readback failure. |
| `uniform_buffer` | Uniform-buffer descriptor binding or stage visibility failure, uniform-block load failure, or shared graphics/compute execution and readback failure. |
| `combined_image_sampler` | Combined-image-sampler binding or stage visibility failure, image layout or sampling failure, or shared graphics/compute execution and readback failure. |

### Cause Analysis

#### Storage-buffer descriptor binding or stage visibility failure, storage-buffer load failure, or shared graphics/compute execution and readback failure

**Possible failure symptoms:** One or more compute floats differ from `1.0` through `4.0`, one or more framebuffer components differ from the quarter-step color, or both outputs fail in `storage_buffer`. A compute-only mismatch points to the compute observation path; an image-only mismatch points to graphics; failure in both paths leaves the shared descriptor and setup paths in scope.

**Possible implementation causes:** `vkCmdBindDescriptorSets2` may fail to establish set state for one selected bind point, or compatible pipeline-layout state may be disturbed or interpreted incorrectly. The implementation may expose the wrong storage-buffer descriptor, range, or stage visibility, or lower the runtime-array load incorrectly. Shared command execution, host-visible buffer handling, color attachment output, image-to-buffer copy, or result invalidation can produce the same host symptoms, so the exact failed output needs source-level investigation. The required bind-point and descriptor-validity behavior follows [`VkBindDescriptorSetsInfo`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4720-L4764) and [descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4583-L4618).

#### Uniform-buffer descriptor binding or stage visibility failure, uniform-block load failure, or shared graphics/compute execution and readback failure

**Possible failure symptoms:** The compute buffer, framebuffer, or both contain wrong components in `uniform_buffer`, while another descriptor-type leaf may still pass. Differences from `storage_buffer` isolate the uniform descriptor and uniform-block representation, subject to the failing output path.

**Possible implementation causes:** The implementation may bind set 0 incorrectly for graphics or compute, apply the wrong stage visibility, expose the wrong uniform-buffer range, or lower indexed loads from the uniform `vec4` incorrectly. The same pipeline, command, copyback, and host-memory paths used by all leaves remain possible if failures are not isolated to this descriptor type. Layout bindings require the descriptor type and permitted shader stages to match the shaders ([layout binding rules](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L469)).

#### Combined-image-sampler binding or stage visibility failure, image layout or sampling failure, or shared graphics/compute execution and readback failure

**Possible failure symptoms:** The compute floats, rendered pixels, or both differ from their references in `combined_image_sampler`. An image-only failure can affect center sampling or graphics output; a compute-only failure can affect component selection, multiplication, or compute binding. Failure in both paths points toward shared sampler, view, layout, descriptor binding, or image initialization.

**Possible implementation causes:** The implementation may expose the wrong combined image sampler at one bind point, apply incorrect stage visibility, or mishandle sampler/image-view descriptor state. The transfer copy or transition may fail to make image writes visible to fragment and compute sampling, or sampling may use incorrect texels or UNORM conversion. Graphics output, compute output, and host readback remain possible shared causes. The descriptor write must supply a valid sampler and image view ([descriptor update validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2971-L2992)), and the source's barriers provide the transfer-to-shader memory dependency required by the [synchronization model](../../../../vulkan-docs/src/chapters/synchronization.adoc#L110-L182).

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_KHR_maintenance6`; an implementation without that functionality reports the case as unsupported before execution ([`checkSupport()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L579-L582)).
- The parent factory places `stages` inside `#ifndef CTS_USES_VULKANSC`, so the family is absent from Vulkan SC builds ([parent registration](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L61-L71)).
- No descriptor-type-specific optional feature gate or runtime device-limit pruning appears in this test family. The resources use fixed small sizes and ordinary storage-buffer, uniform-buffer, combined-image-sampler, color-attachment, and transfer usage.

Requirement-based pruning means the maintenance6 command path or build target is unavailable. It does not represent a failed descriptor binding.

### Design-based pruning

- Registration deliberately covers three descriptor classes: writable/readable storage-buffer representation, read-only uniform-buffer representation, and sampled image plus sampler representation. It does not generate every Vulkan descriptor type.
- Vertex-stage descriptor access is excluded. The stage mask uses fragment to select the graphics bind point and compute to select the compute bind point; the fixed vertex shader only creates geometry.
- The family fixes one shared pipeline layout, two descriptor sets, graphics-before-compute order, and four logical values. These constants isolate whether one stage-scoped call updates both bind points rather than creating a broad descriptor matrix.

Design-based omissions define the test's focused contract. They are not unsupported-device outcomes.

## Key Takeaways

- One `vkCmdBindDescriptorSets2` call with fragment and compute bits must establish descriptor-set state for graphics and compute pipeline bind points.
- Both pipelines use one compatible layout. Graphics reads set 0; compute reads set 0 and writes set 1.
- The draw precedes the dispatch, but the operations have no producer-consumer relationship. They read the same input and write independent outputs.
- The descriptor-type leaf changes buffer versus image resource behavior while preserving the binding call and logical reference values.
- The host requires both four-float compute output and every framebuffer pixel to match. See `## Failure Meaning` to interpret which path a mismatch implicates.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Binding-model category attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71) | Attaches `stages` outside Vulkan SC builds. |
| Stages registration | [`createStagesTests()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L586-L613) | Registers the exact three descriptor-type leaves. |
| Descriptor layouts and shared pipeline layout | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L90-L113) | Makes set bindings visible to fragment and compute stages. |
| Buffer input path | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L143-L187) | Creates, updates, initializes, and flushes storage or uniform input. |
| Image input path | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L189-L300) | Creates the combined image sampler and performs upload synchronization. |
| Output resources | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L303-L350) | Creates compute and graphics outputs. |
| Pipeline and descriptor binding setup | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L352-L405) | Uses one shared layout and one fragment-plus-compute descriptor bind. |
| Command order and copyback | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L407-L434) | Records draw, dispatch, color barrier, and image-to-buffer copy. |
| Host result checks | [`StagesTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L436-L468) | Compares four compute floats and every graphics pixel component. |
| GLSL generation | [`StagesTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L493-L576) | Defines all descriptor-type and shader-stage branches. |
| Support gate | [`StagesTestCase::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingStagesTests.cpp#L579-L582) | Requires `VK_KHR_maintenance6`. |
| Exact mustpass paths | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L146932-L146934) | Confirms all three executable leaves. |
| Descriptor updates | [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2900-L2992) | Defines descriptor writes and resource validity used before binding. |
| Stage-scoped descriptor binding | [`vkCmdBindDescriptorSets2` and `VkBindDescriptorSetsInfo`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4688-L4774) | Defines the one-call binding and stage-mask-to-bind-point behavior. |
| Layout and descriptor rules | [stage visibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L469), [layout compatibility](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2021-L2055), [descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4583-L4618) | Defines legal access by both pipelines. |
| Pipeline bind points | [Pipeline Binding](../../../../vulkan-docs/src/chapters/pipelines.adoc#L9794-L9819) | States that graphics and compute bindings do not disturb each other. |
| Resource synchronization | [Execution and Memory Dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L71-L182) | Grounds the upload and color-copy barriers. |
| Shader compilation target | [`getBaselineSpirvVersion()`](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052) | Establishes SPIR-V 1.0 for shaders without explicit build options. |
