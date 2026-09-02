## Overview

**Core question:** Does each descriptor array type return the resource selected by a non-uniform shader index, including the supported lifetime, update, loop, and array-declaration variants?

- [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L218-L4497) implements the descriptor-set indexing cases and their generated GLSL or SPIR-V inputs.
- [`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4736-L4924) registers the main descriptor matrix, the minimum-`NonUniform` cases, the no-runtime-array cases, `non_uniform_atomics`, and the delegated misc registrations.
- The default `descriptor-indexing` mustpass contains 114 executable leaves. The page explains the matrix rather than repeating every leaf's full path.
- The common path creates sparse descriptor arrays, selects prime-numbered elements, executes graphics or compute work, and compares observed data with a host-built reference.

## Background Knowledge

- A descriptor set layout declares a descriptor type, array count, and shader-stage visibility for each binding. A shader array access therefore depends on both the descriptor-set layout and the resource declaration ([`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-setlayout)).
- A non-uniform index can differ between shader invocations. The matching descriptor-indexing feature must be enabled for the descriptor type, such as `shaderStorageBufferArrayNonUniformIndexing` or `shaderSampledImageArrayNonUniformIndexing` ([`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#features-shaderStorageBufferArrayNonUniformIndexing)).
- A runtime descriptor array has no compile-time element count in the shader. Vulkan exposes this through `runtimeDescriptorArray`; a fixed array remains valid for the no-runtime-array cases ([`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#features-runtimeDescriptorArray)).
- Update-after-bind allows selected descriptor bindings to change after command-buffer binding when the matching descriptor-binding feature and layout or pool flags are present ([`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#features-descriptorBindingStorageBufferUpdateAfterBind), [`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptorsetlayout-update-after-bind)).

## Registration Hierarchy

The main registration function adds the matrix and direct function case to the `descriptor_indexing` test category. The four `misc_common_nonuniform_index_*` entries are added by `createDescriptorIndexingMiscTests`; this page records that routing only. Their implementation belongs to [`vktDescriptorIndexingMiscTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612) and its separate page.

```text
descriptor_indexing
├── combined_image_sampler
├── combined_image_sampler_after_bind
├── combined_image_sampler_after_bind_in_loop
├── combined_image_sampler_after_bind_in_loop_lifetime
├── combined_image_sampler_after_bind_in_loop_with_lod
├── combined_image_sampler_after_bind_in_loop_with_lod_lifetime
├── combined_image_sampler_after_bind_lifetime
├── combined_image_sampler_after_bind_with_lod
├── combined_image_sampler_after_bind_with_lod_lifetime
├── combined_image_sampler_in_loop
├── combined_image_sampler_in_loop_lifetime
├── combined_image_sampler_in_loop_with_lod
├── combined_image_sampler_in_loop_with_lod_lifetime
├── combined_image_sampler_lifetime
├── combined_image_sampler_minNonUniform
├── combined_image_sampler_no_runtime_array
├── combined_image_sampler_with_lod
├── combined_image_sampler_with_lod_lifetime
├── combined_image_sampler_with_lod_minNonUniform
├── input_attachment
├── input_attachment_in_loop
├── input_attachment_in_loop_lifetime
├── input_attachment_lifetime
├── misc_common_nonuniform_index_arraysize_64_at_0 (registration only)
├── misc_common_nonuniform_index_arraysize_64_at_mid (registration only)
├── misc_common_nonuniform_index_arraysize_8_at_0 (registration only)
├── misc_common_nonuniform_index_arraysize_8_at_mid (registration only)
├── non_uniform_atomics
├── sampled_image
├── sampled_image_after_bind
├── sampled_image_after_bind_in_loop
├── sampled_image_after_bind_in_loop_lifetime
├── sampled_image_after_bind_in_loop_with_lod
├── sampled_image_after_bind_in_loop_with_lod_lifetime
├── sampled_image_after_bind_lifetime
├── sampled_image_after_bind_with_lod
├── sampled_image_after_bind_with_lod_lifetime
├── sampled_image_in_loop
├── sampled_image_in_loop_lifetime
├── sampled_image_in_loop_with_lod
├── sampled_image_in_loop_with_lod_lifetime
├── sampled_image_lifetime
├── sampled_image_with_lod
├── sampled_image_with_lod_lifetime
├── sampler
├── sampler_after_bind
├── sampler_after_bind_in_loop
├── sampler_after_bind_in_loop_lifetime
├── sampler_after_bind_in_loop_with_lod
├── sampler_after_bind_in_loop_with_lod_lifetime
├── sampler_after_bind_lifetime
├── sampler_after_bind_with_lod
├── sampler_after_bind_with_lod_lifetime
├── sampler_in_loop
├── sampler_in_loop_lifetime
├── sampler_in_loop_with_lod
├── sampler_in_loop_with_lod_lifetime
├── sampler_lifetime
├── sampler_with_lod
├── sampler_with_lod_lifetime
├── storage_buffer
├── storage_buffer_after_bind
├── storage_buffer_after_bind_in_loop
├── storage_buffer_after_bind_in_loop_lifetime
├── storage_buffer_after_bind_lifetime
├── storage_buffer_dynamic
├── storage_buffer_dynamic_in_loop
├── storage_buffer_dynamic_in_loop_lifetime
├── storage_buffer_dynamic_lifetime
├── storage_buffer_in_loop
├── storage_buffer_in_loop_lifetime
├── storage_buffer_lifetime
├── storage_buffer_minNonUniform
├── storage_buffer_no_runtime_array
├── storage_image
├── storage_image_after_bind
├── storage_image_after_bind_in_loop
├── storage_image_after_bind_in_loop_lifetime
├── storage_image_after_bind_lifetime
├── storage_image_in_loop
├── storage_image_in_loop_lifetime
├── storage_image_lifetime
├── storage_image_minNonUniform
├── storage_image_no_runtime_array
├── storage_texel_buffer
├── storage_texel_buffer_after_bind
├── storage_texel_buffer_after_bind_in_loop
├── storage_texel_buffer_after_bind_in_loop_lifetime
├── storage_texel_buffer_after_bind_lifetime
├── storage_texel_buffer_in_loop
├── storage_texel_buffer_in_loop_lifetime
├── storage_texel_buffer_lifetime
├── storage_texel_buffer_minNonUniform
├── storage_texel_buffer_no_runtime_array
├── uniform_buffer
├── uniform_buffer_dynamic
├── uniform_buffer_dynamic_in_loop
├── uniform_buffer_dynamic_in_loop_lifetime
├── uniform_buffer_dynamic_lifetime
├── uniform_buffer_in_loop
├── uniform_buffer_in_loop_lifetime
├── uniform_buffer_lifetime
├── uniform_buffer_minNonUniform
├── uniform_buffer_no_runtime_array
├── uniform_texel_buffer
├── uniform_texel_buffer_after_bind
├── uniform_texel_buffer_after_bind_in_loop
├── uniform_texel_buffer_after_bind_in_loop_lifetime
├── uniform_texel_buffer_after_bind_lifetime
├── uniform_texel_buffer_in_loop
├── uniform_texel_buffer_in_loop_lifetime
├── uniform_texel_buffer_lifetime
├── uniform_texel_buffer_minNonUniform
└── uniform_texel_buffer_no_runtime_array
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Descriptor type | `storage_buffer`, `storage_texel_buffer`, `uniform_texel_buffer`, `storage_image`, `sampler`, `sampled_image`, `combined_image_sampler`, `uniform_buffer`, `storage_buffer_dynamic`, `uniform_buffer_dynamic`, `input_attachment` | Selects the descriptor layout, resource objects, shader access expression, support feature, and result path. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4746-L4791) |
| Stage path | Graphics for the buffer, texel-buffer, sampler, sampled-image, combined-image-sampler, uniform-buffer, dynamic-buffer, and input-attachment cases; compute for `storage_image` | Selects vertex plus fragment execution or the storage-image compute implementation. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4819-L4822), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4069-L4073) |
| Update-after-bind | Base and `_after_bind` where `descriptorTypeSupportsUpdateAfterBind` returns true | Moves descriptor writes after the set is bound. Dynamic buffer and input-attachment variants are pruned. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4719-L4733), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4817) |
| Index calculation | Base and `_in_loop` | Uses flat vertex indices directly, or reads an index stream in a bounded loop with `lowerBound` and `upperBound`. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1347-L1377), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1750-L1767) |
| Mipmap and LOD | Base and `_with_lod` for `sampler`, `sampled_image`, and `combined_image_sampler` | Adds mip levels and samples a selected mip level. Other descriptor types do not receive this suffix. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4713-L4717), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3839-L3873) |
| Lifetime | Base and `_lifetime` | Fills unused descriptor slots with resources, destroys those unused resources before submission, and leaves prime-indexed resources in use. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1276-L1284), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1446-L1454) |
| Array declaration | Runtime array for the main and minimum-`NonUniform` paths; fixed minimum-size array for `_no_runtime_array` | Separates `RuntimeDescriptorArray` coverage from `ShaderNonUniform` coverage that does not need a runtime array. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L2841-L2849), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4900-L4918) |
| Non-uniform decoration | GLSL-generated normal cases and `_minNonUniform` SPIR-V assembly cases | The assembly path controls the minimum required placement of `NonUniform` decorations. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4838-L4897), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4390-L4455) |
| Valid descriptor selection | Prime indices from the available descriptor count | Leaves non-prime slots unused or filled with a disposable resource, then makes shader indices visit prime slots. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L596-L627), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1063-L1128) |
| Count and limits | Device-derived available count, capped by implementation limits and `MAX_DESCRIPTORS` | Exercises arrays sized from device capability without assuming that every implementation exposes the same count. | [`vktDescriptorSetsIndexingTestsUtils.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L628-L776), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L74-L75) |

## Behavior Parameters

The primary behavioral axis is the descriptor type. Each value selects a concrete `TestInstance` in [`DescriptorIndexingTestCase::createInstance`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4240-L4280); suffixes then alter the shared execution around that type.

### `storage_buffer` and `storage_buffer_dynamic` | Storage-buffer records

The shader declares `buffer Data { vec4 cnew, cold; } data[]` and reads `cold` through `nonuniformEXT`. The dynamic form uses a dynamic offset for each available descriptor and does not receive update-after-bind. When vertex stores are supported, the vertex shader also copies a selected `cold` value into another selected descriptor's `cnew` field.

### `uniform_buffer` and `uniform_buffer_dynamic` | Uniform-buffer records

The shader reads `uniform Data { vec4 c; } data[]`. Host records are placed at offsets rounded to `minUniformBufferOffsetAlignment`; the dynamic form supplies those offsets at bind time and follows the same loop and lifetime variants without update-after-bind.

### `storage_texel_buffer` and `uniform_texel_buffer` | Texel-buffer access

The storage form uses `imageBuffer` and can perform a vertex-stage `imageStore` after reading a selected texel. The uniform form uses `samplerBuffer` and reads with `texelFetch`. Both use non-uniform indexing over buffer views, with their own descriptor-type feature checks.

### `sampler`, `sampled_image`, and `combined_image_sampler` | Sampled-image access

`sampler` indexes an array of samplers and combines each selected sampler with the additional `texture2D` binding. `sampled_image` indexes `texture2D` objects and combines them with the additional sampler. `combined_image_sampler` indexes complete `sampler2D` descriptors. The `_with_lod` variants use mipmapped images and `textureLod` or the final queried mip level.

### `input_attachment` | Input attachment access

The fragment shader reads `subpassInput` with `subpassLoad`. The render pass inserts `VK_ATTACHMENT_UNUSED` gaps so the prime-indexed input attachments occupy their registered attachment positions. This family remains graphics-only and has no update-after-bind or LOD suffix.

### `storage_image` | Compute image access

The compute shader indexes an `uimage2D` array. A separate `idxs` image supplies per-pixel descriptor indices in the direct path. The loop path divides the selected index interval between a 128-invocation workgroup and uses `imageAtomicAdd` to update the selected image.

### `_minNonUniform` and `_no_runtime_array` | Decoration and declaration controls

The selected `_minNonUniform` leaves use direct SPIR-V assembly so the test can place only the required `NonUniform` decorations. The `_no_runtime_array` leaves use fixed arrays sized to each descriptor type's minimum requirement and still exercise non-uniform indexing.

### `non_uniform_atomics` | Runtime-array storage-buffer atomics

This direct function case uses two descriptor sets with 128 storage-buffer descriptors per set. It dispatches 1024 compute invocations, but the shader guard runs the body only for the first 128 invocations: each writes its index plus one to one buffer and atomically increments a counter selected with `nonuniformEXT(gl_GlobalInvocationID.x & 0x7FFFFCu)`.

## Shader Analysis

The walkthrough below shows the ordinary graphics fragment path for `storage_buffer`. It is representative of the shared descriptor lookup and result flow. The descriptor-specific declarations and access expressions vary as summarized above; `_minNonUniform` uses direct SPIR-V instead of this GLSL source path.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.descriptor_indexing.storage_buffer
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `storage_buffer` | Selects a graphics test with a runtime array of storage-buffer records. |
| Base case without `_in_loop`, `_after_bind`, `_with_lod`, or `_lifetime` | Keeps the direct index and ordinary descriptor-update path visible. |
| `rIndex` | Carries a prime descriptor index from the flat vertex input to the fragment shader. |

#### Purpose

The fragment shader must read the `cold` member from the storage-buffer descriptor selected by the flat per-invocation index. A wrong descriptor-array lookup changes the output color.

#### Structural Design

| Phase | Shader operation | Observable role |
|---|---|---|
| Vertex | Copy `index.x` to flat output `rIndex` | Preserve one descriptor index for each point. |
| Fragment input | Load `rIndex` | Give the fragment invocation its selected descriptor element. |
| Fragment descriptor access | Evaluate `data[nonuniformEXT(rIndex)].cold` | Exercise non-uniform indexing over a runtime storage-buffer array. |
| Fragment output | Store the selected `vec4` in `FragColor` | Supply the image that the host compares. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_nonuniform_qualifier : require

/// Binding 0 is a runtime array of storage-buffer records. Each record has the
/// value read by the fragment stage and the value used by optional vertex writes.
layout(set=0, binding = 0) buffer Data { vec4 cnew, cold; } data[];

layout(location = 0) out vec4 FragColor;
/// These flat inputs carry the vertex-selected descriptor index and its companion
/// index used by the optional storage-write variant.
layout(location = 0) in flat vec2 normalpos;
layout(location = 1) in flat int rIndex;
layout(location = 2) in flat int gIndex;

void main(void)
{
    /// The explicit qualifier keeps the descriptor-array access non-uniform.
    FragColor = data[nonuniformEXT(rIndex)].cold;
}
```

#### Additional Info

- The source generator emits `GL_EXT_nonuniform_qualifier` for the normal GLSL path and uses `nonuniformEXT` at the descriptor access ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L2771-L2849)).
- The host vertex buffer repeats prime indices in `index.x`, so the fragment shader reads valid sparse elements rather than the disposable gaps ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L596-L627)).
- This walkthrough reconstructs the fragment stage only. The vertex stage supplies `rIndex`; its fixed prolog is shown in the source and is not a second shader artifact here.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Descriptor type | Changes the declaration and access expression, such as `buffer`, `uniform`, `imageBuffer`, `samplerBuffer`, `subpassInput`, or `uimage2D`. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L2786-L2819) |
| `_in_loop` | Adds push constants and an `isamplerBuffer` enumerator, then reads a second descriptor index inside the loop. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L2779-L2784), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L2913-L2922) |
| `_with_lod` | Changes sampled-image expressions to `textureLod` or a final-level query; it does not apply to storage buffers. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1698-L1737) |
| `_after_bind` | Leaves the shader expression unchanged but moves descriptor updates into the bound-command path. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1408-L1411) |
| `_minNonUniform` | Replaces generated GLSL with SPIR-V assembly generated by `getShaderAsm`, allowing exact decoration placement. | [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4390-L4455) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.4`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.4
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 27
; Schema: 0
               OpCapability Shader
               OpCapability ShaderNonUniform
               OpCapability RuntimeDescriptorArray
               OpCapability StorageBufferArrayNonUniformIndexing
               OpExtension "SPV_EXT_descriptor_indexing"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %FragColor %data %rIndex %normalpos %gIndex
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_nonuniform_qualifier"
               OpName %main "main"
               OpName %FragColor "FragColor"
               OpName %Data "Data"
               OpMemberName %Data 0 "cnew"
               OpMemberName %Data 1 "cold"
               OpName %data "data"
               OpName %rIndex "rIndex"
               OpName %normalpos "normalpos"
               OpName %gIndex "gIndex"
               OpDecorate %FragColor Location 0
               OpDecorate %Data Block
               OpMemberDecorate %Data 0 Offset 0
               OpMemberDecorate %Data 1 Offset 16
               OpDecorate %data Binding 0
               OpDecorate %data DescriptorSet 0
               OpDecorate %rIndex Flat
               OpDecorate %rIndex Location 1
               OpDecorate %18 NonUniform
               OpDecorate %21 NonUniform
               OpDecorate %22 NonUniform
               OpDecorate %normalpos Flat
               OpDecorate %normalpos Location 0
               OpDecorate %gIndex Flat
               OpDecorate %gIndex Location 2
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %FragColor = OpVariable %_ptr_Output_v4float Output
       %Data = OpTypeStruct %v4float %v4float
%_runtimearr_Data = OpTypeRuntimeArray %Data
%_ptr_StorageBuffer__runtimearr_Data = OpTypePointer StorageBuffer %_runtimearr_Data
       %data = OpVariable %_ptr_StorageBuffer__runtimearr_Data StorageBuffer
        %int = OpTypeInt 32 1
%_ptr_Input_int = OpTypePointer Input %int
     %rIndex = OpVariable %_ptr_Input_int Input
      %int_1 = OpConstant %int 1
%_ptr_StorageBuffer_v4float = OpTypePointer StorageBuffer %v4float
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
  %normalpos = OpVariable %_ptr_Input_v2float Input
     %gIndex = OpVariable %_ptr_Input_int Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %17 = OpLoad %int %rIndex
         %18 = OpCopyObject %int %17
         %21 = OpAccessChain %_ptr_StorageBuffer_v4float %data %18 %int_1
         %22 = OpLoad %v4float %21
               OpStore %FragColor %22
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The common setup chooses a `64 x 64` frame, creates a descriptor-set layout and pool, computes the available and prime-valid descriptor counts, creates resources, and builds the pipeline. Graphics cases use point-list rendering; storage-image cases use compute dispatch ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L69-L81), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1221-L1274), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L770-L898)).
- For graphics, the common iterator renders a `4 x 4` sweep of scissored tiles. It writes descriptors before binding for ordinary cases and after binding for `_after_bind` cases, then draws `vertexCount` points ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1383-L1425)).
- The vertex buffer carries `rIndex` in `index.x` and sets `gIndex` at selected prime positions. The fragment shader reads or combines descriptor values. Storage buffers and storage texel buffers may also receive vertex-stage writes when `vertexPipelineStoresAndAtomics` is enabled ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L596-L635), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1770-L1787)).
- Image cases copy host-populated staging data into images before shader execution and copy image results back afterward. Input attachments instead expose the prepared images through a render pass with sparse input-attachment references ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L992-L1036), [`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3505-L3595)).
- The host reads the framebuffer, builds a reference image from the color scheme and prime-valid count, and uses `tcu::floatThresholdCompare` with a `0.02f` threshold per channel. If vertex writes are enabled, it also checks the descriptor-backed records ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1473-L1518)).
- `non_uniform_atomics` invalidates its 128 index and counter buffers, expects index `i` to contain `i + 1`, and expects counter `i` to contain the CPU reference count. Any mismatch logs the index or counter and fails the case ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4651-L4708)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `storage_buffer` | Storage-buffer non-uniform lookup or storage-buffer resource setup. |
| `storage_buffer_dynamic` | Storage-buffer lookup combined with dynamic offset binding. |
| `uniform_buffer` | Uniform-buffer non-uniform lookup or aligned buffer setup. |
| `uniform_buffer_dynamic` | Uniform-buffer lookup combined with dynamic offset binding. |
| `storage_texel_buffer` | Storage texel-buffer view lookup or optional vertex store. |
| `uniform_texel_buffer` | Uniform texel-buffer view lookup. |
| `sampler` | Sampler-array lookup or separate image and sampler combination. |
| `sampled_image` | Sampled-image-array lookup or separate sampler combination. |
| `combined_image_sampler` | Combined image-sampler lookup or mip-level access. |
| `input_attachment` | Input-attachment lookup, attachment mapping, or render-pass setup. |
| `storage_image` | Storage-image lookup, image copyback, or compute execution. |
| `non_uniform_atomics` | Runtime storage-buffer array lookup, atomic update, or counter readback. |

### Cause Analysis

#### Descriptor lookup and `NonUniform` handling

**Possible failure symptoms:** The output image differs from the reference at the pixels driven by prime indices, or a minimum-`NonUniform` case fails during shader validation or execution.

**Possible implementation causes:** The implementation may mishandle the descriptor-type-specific non-uniform indexing capability, propagate a missing or misplaced `NonUniform` decoration, or select the wrong descriptor element. The source supports the distinction between GLSL-generated cases and direct SPIR-V cases, but it does not identify a driver or hardware fault location.

#### Descriptor resource and layout setup

**Possible failure symptoms:** A buffer, texel buffer, sampler, sampled image, combined image sampler, or input attachment produces the wrong value while other descriptor types pass.

**Possible implementation causes:** The implementation may mishandle the resource type, descriptor array element, buffer offset, image view, sampler pairing, or input-attachment reference. A failure can also indicate a test-environment setup issue in the corresponding resource path; source-level investigation is needed to separate those causes.

#### Update, lifetime, and dynamic binding

**Possible failure symptoms:** A base case passes but `_after_bind`, `_lifetime`, or a dynamic-buffer case produces stale, changed, or missing data.

**Possible implementation causes:** The implementation may fail to preserve the descriptor value across the allowed update-after-bind or lifetime sequence, or may apply a dynamic offset to the wrong descriptor element. The test's host sequence and the relevant Vulkan feature gate identify the exercised contract, not the location of a defect.

#### Compute image and atomic result handling

**Possible failure symptoms:** `storage_image` output pixels or `non_uniform_atomics` index and counter values do not match their CPU references.

**Possible implementation causes:** The implementation may mishandle non-uniform storage-image indexing, atomic updates to independently selected storage buffers, shader writes, image-to-buffer copyback, or host visibility. The observed mismatch does not by itself distinguish shader compilation, execution, synchronization, or readback causes.

## Case Pruning

### Requirement-based pruning

- The registration loop omits `_after_bind` when the descriptor type lacks the matching update-after-bind support in the main matrix. It also omits `_with_lod` for types that cannot use mipmaps ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4793-L4809)).
- `checkSupport` skips unsupported cases by requiring `runtimeDescriptorArray` for runtime-array parameters and the descriptor-type-specific non-uniform indexing feature. It requires the matching update-after-bind feature when that suffix is present ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4283-L4387)).
- `non_uniform_atomics` requires `VK_EXT_descriptor_indexing`, runtime descriptor arrays, storage-buffer non-uniform indexing, and enough per-stage and per-set storage-buffer limits for its 256 buffers ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4534-L4556)).

### Design-based pruning

- The prime-index pattern deliberately leaves gaps in each descriptor array. The common update path writes valid resources only at prime indices and fills other slots with one reusable resource, so the shader cannot pass by reading only a densely initialized prefix ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1131-L1209)).
- `_no_runtime_array` is a separate family because its fixed shader declaration tests non-uniform indexing without requiring `runtimeDescriptorArray`; it is not a reduced form of the runtime-array cases ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4900-L4918)).
- `_minNonUniform` is restricted to selected descriptor types and uses SPIR-V assembly so the test can isolate decoration placement rather than letting the GLSL compiler choose it ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4842-L4897)).
- Dynamic buffer cases omit update-after-bind because `checkSupport` rejects that combination, and input attachments omit both update-after-bind and LOD because their render-pass and descriptor semantics do not use those branches ([`vktDescriptorSetsIndexingTests.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4326-L4351)).

## Key Takeaways

- The 114-leaf default mustpass is a product of a descriptor-type matrix plus suffix and special-case families, not 114 unrelated implementations.
- Every main matrix case uses a per-descriptor-type non-uniform indexing feature gate, and runtime-array cases additionally require `runtimeDescriptorArray`.
- Prime-indexed valid descriptors and disposable gaps make accidental contiguous-array behavior visible.
- `_after_bind`, `_in_loop`, `_with_lod`, `_lifetime`, `_minNonUniform`, and `_no_runtime_array` change distinct contracts. Registration guards keep unsupported combinations out of the mustpass.
- Failures identify an observed lookup, resource, execution, or checking mismatch. They do not locate the defect without further source, compiler, driver, and device investigation.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Main registration and 114-leaf family construction | [`descriptorIndexingDescriptorSetsCreateTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4736-L4924) |
| Shared setup, descriptor updates, lifetime, rendering, and checking | [`CommonDescriptorInstance`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L218-L1787) |
| Generated GLSL and direct SPIR-V assembly | [`getShaderSource`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L2771-L2955), [`getShaderAsm`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L1790-L2769) |
| Descriptor-specific resource implementations | [`StorageBufferInstance`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L2957-L3050), [`DynamicBuffersInstance`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3244-L3457), [`InputAttachmentInstance`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3459-L3610), [`SamplerInstance`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3612-L3760), [`SampledImageInstance`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L3762-L3910), [`StorageImageInstance`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTests.cpp#L4052-L4238) |
| Shared helpers and device-derived counts | [`vktDescriptorSetsIndexingTestsUtils.cpp`](../../../modules/vulkan/descriptor_indexing/vktDescriptorSetsIndexingTestsUtils.cpp#L628-L776) |
| Delegated misc registration boundary | [`createDescriptorIndexingMiscTests`](../../../modules/vulkan/descriptor_indexing/vktDescriptorIndexingMiscTests.cpp#L587-L612) |
| Default mustpass evidence | [`descriptor-indexing.txt`](../../../mustpass/main/vk-default/descriptor-indexing.txt#L1-L114) |
| Descriptor-set layout and binding semantics | [`descriptorsets.adoc`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-setlayout) |
| Descriptor-indexing features and limits | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#features-descriptorIndexing), [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#features-runtimeDescriptorArray) |

Risks: the page documents source-backed behavior and does not attribute a failure to a particular driver, compiler, hardware block, or host path. The generated SPIR-V walkthrough uses a faithful representative storage-buffer fragment shader and the local toolchain's validated `spirv1.4` output; it is not the CTS-authored direct-SPIR-V artifact used by `_minNonUniform` cases. The misc implementation remains outside this page's ownership.
