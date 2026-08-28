## Overview

**Core question:** Can each descriptor family be indexed with a subgroup-uniform index without requiring `nonuniformEXT` at the descriptor access?

- This page covers the implementation-bearing `uniform_descriptor_indexing` test family created by [`createSubgroupsUniformDescriptorIndexingTests()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L786-L831).
- The family registers nine descriptor-type test cases. Each draws one full-frame triangle, selects a descriptor from fragment-coordinate-derived values, and records the selected resource value in an R8 color attachment.
- The shader uses `subgroupBroadcastFirst()` to peel one descriptor index at a time from each subgroup. The access is uniform within the subgroup, although different subgroups can choose different descriptors.
- The page explains the descriptor-specific resource setup, source-side support gates, exact storage-buffer shader specialization, host-side color-group verdict, and failure meaning.

## Background Knowledge

For the shared concepts subgroup identity, active invocations, and collective result shapes, see [Background Knowledge](../../categories/subgroups.md#background-knowledge) of the `subgroups` page.

- **Subgroup-scoped uniformity.** A value can be uniform within one subgroup without being uniform across the entire draw. The test relies on this distinction when it selects descriptor elements.
- **Runtime descriptor arrays.** A shader declaration such as `data[]` is a runtime descriptor array. `runtimeDescriptorArray` enables the SPIR-V `RuntimeDescriptorArray` capability, while each descriptor class has its own non-uniform-indexing feature when an array is indexed by an expression that is not uniform. This test instead makes the actual descriptor access subgroup-uniform through the broadcast and peeling loop.
- **Descriptor-specific resource views.** A descriptor array can contain buffers, buffer views, images, samplers, combined image-sampler objects, or input attachments, but each class has its own shader operation and host setup. An input attachment is connected to a render-pass subpass and is read with `subpassLoad`, rather than sampled as an ordinary image.

## Registration Hierarchy

The include and registration call are inside `#ifndef CTS_USES_VULKANSC`, so this entire branch is non-VulkanSC-only.

```text
subgroups.uniform_descriptor_indexing
├── storage_buffer
├── storage_texel_buffer
├── uniform_texel_buffer
├── storage_image
├── sampler
├── sampled_image
├── combined_image_sampler
├── uniform_buffer
└── input_attachment
```

The nine direct children are added by the `caseList` loop. The default mustpass list contains one executable path for each child.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Descriptor family | `storage_buffer`, `storage_texel_buffer`, `uniform_texel_buffer`, `storage_image`, `sampler`, `sampled_image`, `combined_image_sampler`, `uniform_buffer`, `input_attachment` | Selects the descriptor type, GLSL declaration, access expression, host resource path, descriptor count, and minimum accepted color-group count. | [`caseList`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L786-L829) |
| Descriptor count | `4`, `12`, `16` | Sets the runtime descriptor-array length and the upper bound for distinct output colors. | [`configurationMap`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L103-L139) |
| Image count | `0`, `1`, `4`, `16` | Controls the number of host-created images for image, sampler, combined, and input-attachment paths. | [`configurationMap` and image setup](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L126-L195) |
| Buffer count | `0`, `1`, `4` | Controls whether the family uses several storage buffers or one backing allocation for uniform and texel-buffer views. | [`configurationMap` and buffer setup](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L126-L211) |
| Sampler count | `0`, `1`, `4` | Controls sampler resources for sampler, sampled-image, and combined image-sampler paths. | [`configurationMap` and sampler setup](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L126-L231) |
| Minimum color groups | `2`, `4`, `5`, `9`, `10` | Supplies the source-selected lower bound for distinct non-background R8 values accepted by the host verifier. | [`configurationMap` and result check](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L103-L139) and [result check](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L353-L378) |
| SPIR-V target | `spirv1.3` | Fixes the generated shader artifact target through explicit `ShaderBuildOptions`. | [`initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L686-L774) |

## Behavior Parameters

The primary behavioral axis is the registered descriptor family. It changes the resource class being indexed and the operation used to read one selected element. The exact values below follow `caseList` order.

### storage_buffer - Storage-buffer descriptor arrays

Four storage buffers contain repeated float colors. The fragment specialization declares `buffer Data { float c; } data[]` and reads `data[i].c`. The host accepts at least four distinct output groups and no more than four descriptor-derived groups.

### storage_texel_buffer - Storage-texel-buffer descriptor arrays

Sixteen R8 storage texel-buffer views are backed by one allocation. The shader declares `uniform imageBuffer data[]` and reads `imageLoad(data[i], 0).r`; the layout includes `r8,` for the image format.

### uniform_texel_buffer - Uniform-texel-buffer descriptor arrays

Sixteen R8 uniform texel-buffer views are backed by one allocation. The shader declares `uniform samplerBuffer data[]` and reads `texelFetch(data[i], 0).r`.

### storage_image - Storage-image descriptor arrays

Four 3 by 3 R8 storage images are cleared and read with `imageLoad(data[i], ivec2(0)).r`. The descriptor layout includes `r8,`, and the images use `VK_IMAGE_LAYOUT_GENERAL` for the shader access.

### sampler - Sampler descriptor arrays

Four samplers are indexed while one auxiliary `texture2D tex` at binding 4 supplies the image. The shader constructs `sampler2D(tex, data[i])` and samples at `vec2(1.5)`. One 3 by 3 sampled image supplies the auxiliary image path, while the four samplers are the tested array.

### sampled_image - Sampled-image descriptor arrays

Sixteen 3 by 3 sampled images are indexed while one auxiliary sampler at binding 16 supplies the sampler. The shader constructs `sampler2D(data[i], samp)` and samples at `vec2(0.5)`.

### combined_image_sampler - Combined image-sampler descriptor arrays

Four combined descriptors each provide an image and sampler. The shader samples the selected `data[i]` with `texture(data[i], uvec2(0.5)).r`.

### uniform_buffer - Uniform-buffer descriptor arrays

Twelve descriptor elements refer to aligned float ranges in one host-visible uniform buffer. The shader declares `uniform Data { float c; } data[]` and reads `data[i].c`; the host rounds each element to `minUniformBufferOffsetAlignment`.

### input_attachment - Input-attachment descriptor arrays

Four 32 by 32 R8 images become input attachments in the render pass. The shader declares `uniform subpassInput data[]` and reads `subpassLoad(data[i]).r`; the layout includes `input_attachment_index=0,`. The selected attachment is read at the current fragment location.

## Shader Analysis

The representative walkthrough uses the exact storage-buffer case because it exposes the shared selection algorithm with the smallest descriptor-backed resource setup. The other eight families keep the same fragment control flow and vary the specialized declaration and access expression.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.subgroups.uniform_descriptor_indexing.storage_buffer
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `storage_buffer` | Selects four storage-buffer descriptors and the `data[i].c` access specialization. |
| `descriptorCount = 4` | Makes `materialIndex` range from 0 through 3 and bounds the accepted number of color groups. |
| Fragment shader, SPIR-V 1.3 | Uses the generated graphics fragment stage and the explicit target from `ShaderBuildOptions`. |

#### Purpose

This fragment shader checks that a descriptor-array access remains valid when the selected index is made uniform within each subgroup by `subgroupBroadcastFirst()`. It should expose several resource colors across the draw without leaving any fragment at the background value.

#### Structural Design

| Phase | Shader operation | Tested consequence |
|-------|------------------|--------------------|
| Candidate selection | Compute `noize` from `gl_FragCoord`, then convert `noize * 4` to `materialIndex`. | Different fragments can propose different descriptor elements. |
| Subgroup peeling | Broadcast the first candidate to `i`, then continue only for invocations whose candidate equals `i`. | The descriptor access is uniform for the active subgroup portion. |
| Resource read | Evaluate `data[i].c` without `nonuniformEXT(i)`. | Exercises subgroup-uniform descriptor indexing rather than an explicitly non-uniform access. |
| Result write | Store the selected float in `fragColor`. | Produces color groups that the host can count after copyback. |

#### Shader Code

```glsl
#version 450
#extension GL_KHR_shader_subgroup_ballot: enable
#extension GL_EXT_nonuniform_qualifier: enable
layout(location = 0) out highp float fragColor;
/// Binding 0 is a runtime array of four storage-buffer descriptors. Each
/// descriptor contains one float color repeated across a host-created buffer.
layout(binding = 0) buffer Data { float c; } data[];
void main (void)
{
  // use cosine to generate pseudo-random value for each fragment; coordinates of each fragment are used
  // to calculate angle for cosine; both coordinates are multiplied by big numbers in order to make small
  // change in coordinates produce completely different cosine value; amplitude is also multiplied by big
  // number before calculating fraction in order to reduce any visible pattern for selected image size;
  // there was no reason why those numbers were hosen and they could be replaced with any other big
  // numbers to get different noize
  const float noize = fract(9876.54 * cos(654.3267 * gl_FragCoord.x + 1234.5678 * gl_FragCoord.y));
  // pseudo-randomly select material for fragment
  const uint materialIndex = uint(noize * 4);
  fragColor.r = 0.0;
  // do a "peeling loop" - iterate over each unique index used such that the accessed resource
  // is always uniform within the subgroup; and in a way that it's not uniform across the draw
  for(;;)
  {
    uint i = subgroupBroadcastFirst(materialIndex);
    if(i == materialIndex)
    {
      //     we don't use nonuniformEXT(i) - that is the purpose of tests in this file
      fragColor.r = data[i].c;
      break;
    }
  }
}
```

#### Additional Info

- The source template enables `GL_EXT_nonuniform_qualifier`, but the source comment explicitly records that `nonuniformEXT(i)` is not used for the tested access.
- `clearColors[1 + i]` initializes storage buffer `i` to a repeated value. The output attachment uses `VK_ATTACHMENT_LOAD_OP_DONT_CARE`; the shader instead initializes `fragColor.r` to the zero background sentinel before a successful descriptor read overwrites it, and the host rejects any zero output byte.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Descriptor family | Changes `declaration`, `count`, `accessMethod`, `extraDeclarations`, and `extraLayout` in the fragment template. | [`shaderPartsMap`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L691-L726) |
| Descriptor count | Changes the multiplier in `uint(noize * count)` and the runtime array size. | [`fragTemplate`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L728-L759) |
| Descriptor-specific access | Changes buffer member reads, texel loads, image loads, subpass loads, or texture sampling. | [`shaderPartsMap`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L706-L725) |
| Auxiliary image or sampler | Adds a fixed binding for the complementary resource in `sampler` and `sampled_image` cases. | [`shaderPartsMap`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L716-L721) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.3`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.3
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 63
; Schema: 0
               OpCapability Shader
               OpCapability GroupNonUniform
               OpCapability GroupNonUniformBallot
               OpCapability RuntimeDescriptorArray
               OpExtension "SPV_EXT_descriptor_indexing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %fragColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_nonuniform_qualifier"
               OpSourceExtension "GL_KHR_shader_subgroup_ballot"
               OpSourceExtension "GL_KHR_shader_subgroup_basic"
               OpName %main "main"
               OpName %noize "noize"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %materialIndex "materialIndex"
               OpName %fragColor "fragColor"
               OpName %i "i"
               OpName %Data "Data"
               OpMemberName %Data 0 "c"
               OpName %data "data"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %fragColor Location 0
               OpDecorate %Data Block
               OpMemberDecorate %Data 0 Offset 0
               OpDecorate %data Binding 0
               OpDecorate %data DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
%float_9876_54004 = OpConstant %float 9876.54004
%float_654_326721 = OpConstant %float 654.326721
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
%float_1234_56775 = OpConstant %float 1234.56775
     %uint_1 = OpConstant %uint 1
%_ptr_Function_uint = OpTypePointer Function %uint
    %float_4 = OpConstant %float 4
%_ptr_Output_float = OpTypePointer Output %float
  %fragColor = OpVariable %_ptr_Output_float Output
    %float_0 = OpConstant %float 0
     %uint_3 = OpConstant %uint 3
       %bool = OpTypeBool
       %Data = OpTypeStruct %float
%_runtimearr_Data = OpTypeRuntimeArray %Data
%_ptr_StorageBuffer__runtimearr_Data = OpTypePointer StorageBuffer %_runtimearr_Data
       %data = OpVariable %_ptr_StorageBuffer__runtimearr_Data StorageBuffer
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
       %main = OpFunction %void None %3
          %5 = OpLabel
      %noize = OpVariable %_ptr_Function_float Function
%materialIndex = OpVariable %_ptr_Function_uint Function
          %i = OpVariable %_ptr_Function_uint Function
         %17 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_0
         %18 = OpLoad %float %17
         %19 = OpFMul %float %float_654_326721 %18
         %22 = OpAccessChain %_ptr_Input_float %gl_FragCoord %uint_1
         %23 = OpLoad %float %22
         %24 = OpFMul %float %float_1234_56775 %23
         %25 = OpFAdd %float %19 %24
         %26 = OpExtInst %float %1 Cos %25
         %27 = OpFMul %float %float_9876_54004 %26
         %28 = OpExtInst %float %1 Fract %27
               OpStore %noize %28
         %31 = OpLoad %float %noize
         %33 = OpFMul %float %31 %float_4
         %34 = OpConvertFToU %uint %33
               OpStore %materialIndex %34
               OpStore %fragColor %float_0
               OpBranch %38
         %38 = OpLabel
               OpLoopMerge %40 %41 None
               OpBranch %39
         %39 = OpLabel
         %43 = OpLoad %uint %materialIndex
         %45 = OpGroupNonUniformBroadcastFirst %uint %uint_3 %43
               OpStore %i %45
         %46 = OpLoad %uint %i
         %47 = OpLoad %uint %materialIndex
         %49 = OpIEqual %bool %46 %47
               OpSelectionMerge %51 None
               OpBranchConditional %49 %50 %51
         %50 = OpLabel
         %56 = OpLoad %uint %i
         %60 = OpAccessChain %_ptr_StorageBuffer_float %data %56 %int_0
         %61 = OpLoad %float %60
               OpStore %fragColor %61
               OpBranch %40
         %51 = OpLabel
               OpBranch %41
         %41 = OpLabel
               OpBranch %38
         %40 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `checkSupport()` applies the gates in this order: subgroup size must be greater than one; the fragment stage must support subgroup operations; `runtimeDescriptorArray` must be enabled; then the descriptor-family-specific non-uniform-indexing feature must be enabled.
- The common gates are checked before the `switch` over descriptor type. The final gate is selected as follows: storage buffer uses `shaderStorageBufferArrayNonUniformIndexing`; uniform buffer uses `shaderUniformBufferArrayNonUniformIndexing`; storage texel buffer uses `shaderStorageTexelBufferArrayNonUniformIndexing`; uniform texel buffer uses `shaderUniformTexelBufferArrayNonUniformIndexing`; input attachment uses `shaderInputAttachmentArrayNonUniformIndexing`; sampler, sampled image, and combined image sampler use `shaderSampledImageArrayNonUniformIndexing`; storage image uses `shaderStorageImageArrayNonUniformIndexing` ([`checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L625-L684)).
- Those source checks do not match the generated shader requirements. None of the nine generated artifacts decorates the descriptor index `NonUniform` or declares a descriptor-class `...NonUniformIndexing` capability. Conversely, the storage-texel-buffer, uniform-texel-buffer, and input-attachment artifacts declare `StorageTexelBufferArrayDynamicIndexing`, `UniformTexelBufferArrayDynamicIndexing`, and `InputAttachmentArrayDynamicIndexing`, respectively, but `checkSupport()` does not query the corresponding dynamic-indexing features. This is an unresolved implementation-side support-gating defect; this page reports it rather than treating the source checks as Vulkan requirements.
- The host creates a 32 by 32 R8 output image. It creates the selected family resources, fills them with descriptor-specific clear colors, writes the tested array at set 0, binding 0, and creates the graphics pipeline with the generated vertex and fragment modules.
- Storage-buffer resources use four host-visible buffers of `32 * 32` floats. Uniform-buffer resources use one aligned allocation with twelve float ranges. Texel-buffer resources use one allocation and sixteen R8 buffer views. Image resources are 3 by 3 R8 images, except input attachments, which are 32 by 32 to match the framebuffer.
- The command buffer clears family images when needed, inserts transfer-to-fragment visibility barriers for images and buffers, begins the render pass, binds the pipeline and descriptor set, and draws three vertices. It then transitions the output image, copies it to a host-visible buffer, submits to the universal queue, waits, and invalidates the allocation.
- The host counts each byte in the copied output image as a `uint32_t` key. The test passes only when `resultMap` contains no zero key, has at least `minGroupsCount` entries, and has no more than `descriptorCount` entries. A failing result is logged as an image and reports either the number of background fragments or the observed group count.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `storage_buffer` | Storage-buffer descriptor-array indexing or buffer-backed value propagation produced an invalid or insufficient set of output color groups. |
| `storage_texel_buffer` | Storage-texel-buffer view indexing, R8 texel loading, or descriptor-specific resource setup produced an invalid or insufficient set of output color groups. |
| `uniform_texel_buffer` | Uniform-texel-buffer view indexing, texel loading, or descriptor-specific resource setup produced an invalid or insufficient set of output color groups. |
| `storage_image` | Storage-image descriptor-array indexing, image layout, or `imageLoad` behavior produced an invalid or insufficient set of output color groups. |
| `sampler` | Sampler-array indexing or construction of the sampled image from the selected sampler and auxiliary texture produced an invalid or insufficient set of output color groups. |
| `sampled_image` | Sampled-image-array indexing or construction of the sampled image from the selected image and auxiliary sampler produced an invalid or insufficient set of output color groups. |
| `combined_image_sampler` | Combined-image-sampler descriptor-array indexing or sampling of the selected image and sampler pair produced an invalid or insufficient set of output color groups. |
| `uniform_buffer` | Uniform-buffer descriptor-array indexing, aligned range setup, or buffer-backed value propagation produced an invalid or insufficient set of output color groups. |
| `input_attachment` | Input-attachment descriptor-array indexing, render-pass attachment wiring, or `subpassLoad` behavior produced an invalid or insufficient set of output color groups. |

### Cause Analysis

#### storage_buffer descriptor access and value propagation

**Possible failure symptoms:** The output contains background pixels, fewer than four distinct color groups, or more than four groups.

**Possible implementation causes:** The descriptor-array access, subgroup-uniform index handling, storage-buffer read, or buffer visibility before the fragment draw did not produce the initialized descriptor value expected by the host check. The source and descriptor-indexing feature semantics identify the tested operations, but they do not identify a single implementation fault location.

#### storage_texel_buffer view access

**Possible failure symptoms:** The R8 output contains background pixels or a number of groups outside the five through sixteen bound for this family.

**Possible implementation causes:** A storage texel-buffer view could have been indexed or loaded incorrectly, or its format, range, alignment, or transfer-to-fragment visibility could have been mishandled. The exact fault location requires source-level or implementation-level investigation.

#### uniform_texel_buffer view access

**Possible failure symptoms:** The R8 output contains background pixels or a number of groups outside the five through sixteen bound for this family.

**Possible implementation causes:** A uniform texel-buffer view could have been indexed or fetched incorrectly, or its format, range, alignment, or uniform-read visibility could have been mishandled. The exact fault location requires source-level or implementation-level investigation.

#### storage_image access and layout

**Possible failure symptoms:** The output contains background pixels or a number of groups outside the four through four bound for this family.

**Possible implementation causes:** The storage-image descriptor selection, `VK_IMAGE_LAYOUT_GENERAL` access, R8 image load, image clear transition, or fragment visibility could have produced an unexpected value. The source evidence does not isolate one implementation fault location.

#### sampler-array construction

**Possible failure symptoms:** The output contains background pixels or a number of groups outside the two through four bound for this family.

**Possible implementation causes:** The sampler descriptor selection or construction of `sampler2D(tex, data[i])` could have produced the wrong sampling state or image-sampler combination. The auxiliary binding and tested sampler array have separate descriptor roles, so source-level investigation must distinguish them.

#### sampled-image-array construction

**Possible failure symptoms:** The output contains background pixels or a number of groups outside the ten through sixteen bound for this family.

**Possible implementation causes:** The sampled-image descriptor selection or construction of `sampler2D(data[i], samp)` could have selected the wrong image, sampler, or sampled value. The exact implementation cause requires investigation of descriptor lookup and sampling behavior.

#### combined image-sampler access

**Possible failure symptoms:** The output contains background pixels or a number of groups outside the four through four bound for this family.

**Possible implementation causes:** The combined descriptor lookup or sampled image-sampler state could have produced an unexpected R8 value. The source establishes the access and validation contract but not a unique hardware, driver, or host fault location.

#### uniform-buffer range access

**Possible failure symptoms:** The output contains background pixels, fewer than nine distinct color groups, or more than twelve groups.

**Possible implementation causes:** The descriptor array could have resolved an incorrect aligned range, or the uniform-buffer read and pre-draw visibility could have returned a value not initialized for that descriptor element. The precise implementation cause requires investigation.

#### input-attachment render-pass access

**Possible failure symptoms:** The output contains background pixels or a number of groups outside the four through four bound for this family.

**Possible implementation causes:** The input-attachment descriptor selection, render-pass attachment mapping, input-attachment layout, or `subpassLoad` at the current fragment location could have produced an unexpected value. The source does not support assigning the symptom to one fixed implementation layer.

## Case Pruning

### Requirement-based pruning

- The entire `uniform_descriptor_indexing` branch is excluded from VulkanSC builds by the dispatcher and local registration guards.
- `checkSupport()` skips a case when subgroup size is one, when the fragment stage does not support subgroup operations, when `runtimeDescriptorArray` is unavailable, or when the descriptor family's selected non-uniform-indexing feature is unavailable.
- The non-uniform feature checks impose source-side over-pruning even though the descriptor access is subgroup-uniform. The missing dynamic-indexing checks identified in the runtime section are an unresolved source defect, not an intentional pruning rule.

### Design-based pruning

- The source registers one test case per descriptor family rather than multiplying the branch by image size, sampler address mode, or a generated shader matrix.
- The output verifier uses family-specific minimum group thresholds selected from implementation results. It intentionally does not require every descriptor to appear in the final image, because subgroup formation and the coordinate-derived noise affect which groups are observed.
- The sampler and sampled-image families add one complementary descriptor only to construct a complete sampled image. That auxiliary descriptor is not a second tested behavior axis.

## Key Takeaways

- The central property is subgroup-uniform descriptor access, not global uniformity across the 32 by 32 draw.
- The nine families share one fragment selection and peeling algorithm, but each family changes the descriptor declaration, access operation, and host resource setup.
- The output check is a bounded color-group observation. It rejects background pixels and implausible group counts, but it does not require every descriptor element to be observed.
- The source's support checks are ordered and descriptor-specific after the common subgroup and runtime-array gates, but their feature selection does not match the generated artifacts.
- The storage-buffer case is the smallest exact walkthrough of the algorithm: four repeated-color buffers are selected by a broadcast index and read without `nonuniformEXT`.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createSubgroupsUniformDescriptorIndexingTests()` and `caseList` | [`caseList and registration`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L786-L831) | Registers the exact nine direct children in order. |
| `UniformDescriptorIndexingTestCase::checkSupport()` | [`checkSupport()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L625-L684) | Defines the ordered common and descriptor-specific gates. |
| `UniformDescriptorIndexingTestCase::initPrograms()` | [`initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L686-L774) | Defines the exact fragment template, shader specializations, fixed vertex shader, and SPIR-V 1.3 target. |
| `UniformDescriptorIndexingTestCaseTestInstance::iterate()` configuration | [`configurationMap`](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L103-L139) | Defines counts and minimum accepted color groups. |
| Resource creation and descriptor writes | [`iterate()` setup](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L141-L282) | Creates resources, layouts, descriptors, and the graphics pipeline. |
| Buffer and image helper implementations | [`setupImages()` and buffer helpers](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L438-L581) | Defines sizes, formats, colors, alignment, and views. |
| Barriers, draw, and copyback | [`iterate()` command flow](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L284-L351) | Defines synchronization, render-pass execution, copyback, and queue completion. |
| Host-side result classification | [`iterate()` result check](../../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L353-L378) | Defines the pass condition and failure messages. |
| Category dispatcher | [`createChildren()`](../../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L40-L81) | Establishes the non-VulkanSC include and registration boundary. |
| Default mustpass coverage | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L47808-L47816) | Lists the nine executable descriptor-family paths. |
| Descriptor-indexing expression requirements | [Descriptor resource indexing](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1358-L1405) | Distinguishes the feature/capability pairs for dynamically uniform and non-uniform indexing for every descriptor class. |
| Descriptor-indexing feature semantics | [Descriptor-indexing features](../../../../vulkan-docs/src/chapters/features.adoc#L2004-L2077) | Defines descriptor-array non-uniform-indexing feature behavior. |
| Runtime descriptor array semantics | [Runtime descriptor arrays](../../../../vulkan-docs/src/chapters/features.adoc#L2141-L2145) | Defines the runtime-array prerequisite. |
| Subgroup scope and broadcast context | [Subgroup operations](../../../../vulkan-docs/src/chapters/shaders.adoc#L3239-L3269) | Defines the scope in which subgroup operations are meaningful. |
| Input-attachment context | [Render-pass subpasses](../../../../vulkan-docs/src/chapters/renderpass.adoc#L2219-L2263) | Defines input-attachment reads and subpass attachment roles. |
