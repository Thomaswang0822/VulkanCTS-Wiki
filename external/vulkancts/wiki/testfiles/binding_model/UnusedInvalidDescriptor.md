## Overview

**Core question:** Can a partially bound descriptor array execute correctly when an unaccessed element is undefined or incompatible with shader access?

- This page covers the `binding_model.unused_invalid_descriptor` test family implemented in [`vktBindingUnusedInvalidDescriptorTests.cpp`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp).
- The `write` family independently checks an array with an unpopulated element and an array whose third element would be incompatible with the generated shader's image type if accessed.
- The `copy` family destroys the resource behind a source element, copies the descriptors to a destination set, and checks that the destination's unaccessed undefined element does not affect execution.
- All cases use a three-element descriptor binding with `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`, but the generated compute shader accesses only elements `0` and `1`.
- The host validates the device result by copying a 32 by 32 result image to a host-visible buffer and comparing every pixel with `(1.0, 1.0, 1.0, 1.0)`.

## Background Knowledge

For the shared concepts of descriptor validity, dynamic use, and descriptor copies, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Static use and dynamic descriptor use.** Vulkan static use is a property of a shader entry point and its call tree. Dynamic descriptor use is an execution property: a descriptor is dynamically used only when a shader invocation executes an instruction that performs a memory access through that descriptor. The distinction controls which elements of a partially bound binding must be populated. See [Static Use](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-staticuse) and [`VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#VkDescriptorBindingFlagBits).
- **Descriptor validity.** When Vulkan determines that a descriptor is accessed, an undefined descriptor is not valid. A populated descriptor still has to match the pipeline's consuming descriptor type. An accessed image must also satisfy the image-view, sample-count, format, layout, and shader-operation compatibility rules. See [descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptor-validity) and [Texel Input Validation](../../../../vulkan-docs/src/chapters/textures.adoc#textures-input-validation).
- **Partial binding.** For a binding created with `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`, descriptors that are not dynamically used need not contain valid descriptors when the descriptors are consumed. This does not excuse an element that any invocation dynamically uses.
- **Descriptor copying.** Copying a descriptor copies the reference and does not use the referenced resource. Vulkan permits copying an undefined descriptor or one whose underlying resource was destroyed; the destination descriptor is undefined in either case. See [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-sets-updates).

## Registration Hierarchy

```text
binding_model.unused_invalid_descriptor
├── write
└── copy
```

`write` contains the intermediate nodes `unused` and `invalid`. Their executable leaves select resource types. `copy` directly contains its resource-type leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Descriptor update behavior | `write.unused`, `write.invalid`, `copy` | Selects whether the third element is left undefined, contains an access-incompatible image, or becomes undefined in the destination after a copy. | [`createUnusedInvalidDescriptorTests()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1283-L1354) |
| Resource type | `uniform_buffer`, `storage_buffer`, `sampled_image`, `combined_image_sampler`, `storage_image` | Changes the descriptor type, GLSL declaration, resource initialization, and memory access instruction. | [`ResourceType` and type helpers](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L61-L152) |
| Write subfamily coverage | `unused`: all five resource types; `invalid`: `sampled_image`, `combined_image_sampler`, `storage_image` | Restricts the access-incompatible construction to image resources. | [`write` registration](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1287-L1329) |
| Descriptor array | API binding `1` has three elements; shader array has two elements | Keeps one additional API-side element available for the unaccessed state under test. | [`getResourceDeclaration()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L245-L293), [`DescriptorSetLayoutBuilder`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L776-L782) |
| Push-constant index | Host value `0` | Makes the two accesses select elements `0` and `1`, so element `2` is not dynamically used. | [`queuePass()` push constant](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L896-L906), [`getResourceAccess()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L295-L337) |
| Result extent | `32 x 32 x 1` | Gives one compute invocation and one output pixel for each dispatch coordinate. | [`kExtent`, render-target setup, and dispatch](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L57-L59), [write execution](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L707-L725), [dispatch](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L901-L911) |
| Availability | Vulkan only | The category root registers this family inside the `#ifndef CTS_USES_VULKANSC` branch. | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L32-L42), [`createChildren()` registration](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L61-L71) |

## Behavior Parameters

The primary behavioral axis is descriptor state and update path. The resource type is a secondary axis that changes how the valid elements are represented and accessed, but the three behavioral values change the condition being tested.

| Term in this page | Exact role in these cases |
|-------------------|---------------------------|
| Statically unused | The separate sampler at binding `2` has a generated GLSL declaration in every resource variant, but only the `sampled_image` shader uses it in an access expression. In the other compiled shader variants, it is not part of the entry point's static resource use. This is separate from the behavior axis. |
| Dynamically unaccessed | Binding `1` element `2` belongs to a statically used resource-array binding, but no invocation performs a memory access through that element because the host pushes `index = 0`. |
| Undefined or access-incompatible | `write.unused` leaves element `2` undefined; `write.invalid` writes a live image that would be incompatible with the shader's image type if accessed; `copy` makes the destination element undefined. |
| Copied | Only `copy` transfers all three source references to a destination set. Copying element `2` is legal and leaves the destination element undefined. |
| Dynamically accessed | Every invocation reads binding `1` elements `0` and `1` and writes binding `0`. The `sampled_image` shader also accesses the separate sampler at binding `2`. These descriptors must be valid and compatible. |

### `write.unused`: leave the third element undefined

The host writes valid resources to binding `1` elements `0` and `1` and does not update element `2`. The binding is partially bound, and the shader accesses only the first two elements. The case checks that the undefined third element does not need to be populated when no shader invocation dynamically uses it.

### `write.invalid`: populate the third element with an access-incompatible image

The host writes two valid resources and then writes element `2` with a live image resource that would not match the generated shader if accessed. Sampled-image and combined-image-sampler cases use a four-sample image while the shader declares a non-multisampled image. The storage-image case uses a `VK_FORMAT_R32_UINT` view while the shader declares `rgba32f image2D`. The shader still accesses only elements `0` and `1`, so this case checks that an unaccessed access-incompatible descriptor does not affect the dispatch.

### `copy`: copy a descriptor after its referenced resource is destroyed

The source set receives three valid resources. The host destroys the resource internals behind source element `2`: the buffer, or the image and view, plus the per-resource sampler in `combined_image_sampler` cases. It then copies binding `1` elements `0` through `2` into a new destination set. The destination element `2` becomes undefined because the source descriptor references a destroyed resource. The shader executes with the destination set and accesses only elements `0` and `1`.

## Shader Analysis

One representative sampled-image shader is sufficient because every resource variant preserves the same control flow: read two valid binding elements, add their `vec4` values, and write the sum. The resource declaration and access instruction change by resource type; those changes are summarized after the walkthrough.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.unused_invalid_descriptor.write.invalid.sampled_image
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `write.invalid` | Writes a live four-sample image into element `2`; the shader must not access that element. |
| `sampled_image` | Binding `1` contains separate `texture2D` descriptors, and binding `2` contains the sampler used to form sampled images. |
| `index = 0` | The host push constant makes the shader select elements `0` and `1`. |
| `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT` | Element `2` is outside the set of descriptors that the shader dynamically uses. |

#### Purpose

This shader checks that two valid sampled-image descriptors produce the expected white result even though the third descriptor has an image sample count incompatible with the shader's non-multisampled declaration. The output records accesses to elements `0` and `1`; it does not directly inspect element `2`.

#### Structural Design

| Phase | Shader operation | Descriptor consequence |
|-------|------------------|------------------------|
| Select | Read `pc.index`, which the host set to `0`. | The two indices become `0` and `1`. |
| Access 0 | Load `u_textures[ndx + 0]`, combine it with `u_sampler`, and sample at the invocation coordinate. | Element `0` is dynamically used and must be valid. |
| Access 1 | Load `u_textures[ndx + 1]`, combine it with `u_sampler`, and sample at the invocation coordinate. | Element `1` is dynamically used and must be valid. |
| Store | Add the sampled values and call `imageStore` on `o_color`. | The host expects four components of `1.0` in every output pixel. |

#### Shader Code

```glsl
#version 450
layout(push_constant) uniform PushConstants
{
    /// The host always pushes zero, so the two expressions below select elements 0 and 1.
    uint index;
} pc;
/// Binding 0 is the 32 by 32 rgba32f storage image that carries the observable result.
layout(set = 0, binding = 0, rgba32f) writeonly uniform image2D o_color;
/// Binding 1 is declared as two non-multisampled sampled images. The descriptor set layout has
/// three elements, but only these two shader-declared elements can be selected by this program.
layout(set = 0, binding = 1) uniform texture2D u_textures[2];
/// Binding 2 supplies the separate nearest sampler used by the sampled-image resource case.
layout(set = 0, binding = 2) uniform sampler u_sampler;

void main()
{
    uint ndx = pc.index;
    /// Every invocation reads the two valid resources selected by index zero.
    vec4 color0 = texture(sampler2D(u_textures[ndx + 0], u_sampler), ivec2(gl_GlobalInvocationID.x, gl_GlobalInvocationID.y));
    vec4 color1 = texture(sampler2D(u_textures[ndx + 1], u_sampler), ivec2(gl_GlobalInvocationID.x, gl_GlobalInvocationID.y));
    vec4 color = color0 + color1;
    /// Two input values of 0.5 produce the exact expected output value of 1.0.
    imageStore(o_color, ivec2(gl_GlobalInvocationID.x, gl_GlobalInvocationID.y), color);
}
```

#### Additional Info

- [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L635-L655) emits this source through `getResourceDeclaration()` and `getResourceAccess()`. The source has no explicit `ShaderBuildOptions`, so CTS uses its baseline SPIR-V 1.0 target.
- The host sets `index` to zero and dispatches `32, 32, 1`. The source has no local-size declaration, so the default local size is `1, 1, 1`.
- The four-sample image is used for the invalid sampled-image element because a non-multisampled `OpTypeImage` must bind a single-sample image when the descriptor is accessed. The incompatibility matters only on access.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Resource type | `uniform_buffer` and `storage_buffer` replace the image array with a two-element block array and read `.data`; `combined_image_sampler` uses `sampler2D`; `storage_image` uses `rgba32f image2D` and `imageLoad`. | [`getResourceDeclaration()` and `getResourceAccess()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L245-L337) |
| Descriptor behavior | `write.unused` leaves element `2` undefined; `write.invalid` writes an access-incompatible image; `copy` consumes a destination set whose copied element `2` became undefined after destruction of the source resource. | [write set population](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L793-L825), [copy preparation](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1071-L1164) |
| Push constant | The generated source always reads `pc.index`; this test instance always pushes `0`, so no registered case accesses element `2`. | [push constant range and value](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L831-L839), [dispatch setup](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L896-L906) |
| Output operation | The result image declaration remains `rgba32f writeonly image2D`; only the input resource access changes. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L635-L655) |

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
; Bound: 87
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpName %main "main"
               OpName %ndx "ndx"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "index"
               OpName %pc "pc"
               OpName %color0 "color0"
               OpName %u_textures "u_textures"
               OpName %u_sampler "u_sampler"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %color1 "color1"
               OpName %color "color"
               OpName %o_color "o_color"
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpDecorate %u_textures Binding 1
               OpDecorate %u_textures DescriptorSet 0
               OpDecorate %u_sampler Binding 2
               OpDecorate %u_sampler DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %o_color NonReadable
               OpDecorate %o_color Binding 0
               OpDecorate %o_color DescriptorSet 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
%PushConstants = OpTypeStruct %uint
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
         %pc = OpVariable %_ptr_PushConstant_PushConstants PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %21 = OpTypeImage %float 2D 0 0 0 1 Unknown
     %uint_2 = OpConstant %uint 2
%_arr_21_uint_2 = OpTypeArray %21 %uint_2
%_ptr_UniformConstant__arr_21_uint_2 = OpTypePointer UniformConstant %_arr_21_uint_2
 %u_textures = OpVariable %_ptr_UniformConstant__arr_21_uint_2 UniformConstant
     %uint_0 = OpConstant %uint 0
%_ptr_UniformConstant_21 = OpTypePointer UniformConstant %21
         %32 = OpTypeSampler
%_ptr_UniformConstant_32 = OpTypePointer UniformConstant %32
  %u_sampler = OpVariable %_ptr_UniformConstant_32 UniformConstant
         %36 = OpTypeSampledImage %21
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
%_ptr_Input_uint = OpTypePointer Input %uint
     %uint_1 = OpConstant %uint 1
      %v2int = OpTypeVector %int 2
    %v2float = OpTypeVector %float 2
    %float_0 = OpConstant %float 0
         %75 = OpTypeImage %float 2D 0 0 0 2 Rgba32f
%_ptr_UniformConstant_75 = OpTypePointer UniformConstant %75
    %o_color = OpVariable %_ptr_UniformConstant_75 UniformConstant
       %main = OpFunction %void None %3
          %5 = OpLabel
        %ndx = OpVariable %_ptr_Function_uint Function
     %color0 = OpVariable %_ptr_Function_v4float Function
     %color1 = OpVariable %_ptr_Function_v4float Function
      %color = OpVariable %_ptr_Function_v4float Function
         %15 = OpAccessChain %_ptr_PushConstant_uint %pc %int_0
         %16 = OpLoad %uint %15
               OpStore %ndx %16
         %26 = OpLoad %uint %ndx
         %28 = OpIAdd %uint %26 %uint_0
         %30 = OpAccessChain %_ptr_UniformConstant_21 %u_textures %28
         %31 = OpLoad %21 %30
         %35 = OpLoad %32 %u_sampler
         %37 = OpSampledImage %36 %31 %35
         %42 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %43 = OpLoad %uint %42
         %44 = OpBitcast %int %43
         %46 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %47 = OpLoad %uint %46
         %48 = OpBitcast %int %47
         %50 = OpCompositeConstruct %v2int %44 %48
         %52 = OpConvertSToF %v2float %50
         %54 = OpImageSampleExplicitLod %v4float %37 %52 Lod %float_0
               OpStore %color0 %54
         %56 = OpLoad %uint %ndx
         %57 = OpIAdd %uint %56 %uint_1
         %58 = OpAccessChain %_ptr_UniformConstant_21 %u_textures %57
         %59 = OpLoad %21 %58
         %60 = OpLoad %32 %u_sampler
         %61 = OpSampledImage %36 %59 %60
         %62 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %63 = OpLoad %uint %62
         %64 = OpBitcast %int %63
         %65 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %66 = OpLoad %uint %65
         %67 = OpBitcast %int %66
         %68 = OpCompositeConstruct %v2int %64 %67
         %69 = OpConvertSToF %v2float %68
         %70 = OpImageSampleExplicitLod %v4float %61 %69 Lod %float_0
               OpStore %color1 %70
         %72 = OpLoad %v4float %color0
         %73 = OpLoad %v4float %color1
         %74 = OpFAdd %v4float %72 %73
               OpStore %color %74
         %78 = OpLoad %75 %o_color
         %79 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_0
         %80 = OpLoad %uint %79
         %81 = OpBitcast %int %80
         %82 = OpAccessChain %_ptr_Input_uint %gl_GlobalInvocationID %uint_1
         %83 = OpLoad %uint %82
         %84 = OpBitcast %int %83
         %85 = OpCompositeConstruct %v2int %81 %84
         %86 = OpLoad %v4float %color
               OpImageWrite %78 %85 %86
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- `commonCheckSupport()` requires `VK_EXT_descriptor_indexing`, `descriptorBindingPartiallyBound`, and the dynamic-indexing feature for the selected resource type. The selected feature names are `shaderUniformBufferArrayDynamicIndexing`, `shaderStorageBufferArrayDynamicIndexing`, `shaderSampledImageArrayDynamicIndexing`, or `shaderStorageImageArrayDynamicIndexing`.
- The host creates a result image with `VK_FORMAT_R32G32B32A32_SFLOAT`, a host-visible transfer destination, a universal nearest sampler, and two valid input resources. `Resource::update()` fills buffers with `(0.5, 0.5, 0.5, 0.5)` or clears images to that value, then makes image data available to the compute shader.
- The descriptor set layout contains binding `0` as one storage image, binding `1` as three descriptors of the selected type with `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`, and binding `2` as one sampler. The host populates the destination result image and sampler before handling binding `1`.
- The write path creates two valid resources and, for `write.invalid`, a third image with the selected incompatibility. It writes elements `0` and `1`; it writes element `2` only for `write.invalid`.
- The copy path creates and updates three source resources, allocates a destination set with the same layout, destroys the internals of resource `2`, and copies binding `0`, binding `2`, and all three elements of binding `1` into the destination. The destination set is the set bound for dispatch.
- Both paths create a compute pipeline, clear the result image to `(1.0, 0.0, 0.0, 1.0)`, transition it to `VK_IMAGE_LAYOUT_GENERAL`, bind the selected set, push `index = 0`, and dispatch `32, 32, 1`.
- The command buffer copies the result image to the host-visible buffer with the shader-write access mask, then the queue submission waits for completion. `MultiQueueRunnerTestInstance` runs the same `queuePass()` for the universal queue and an additional compute queue when the context exposes one.
- The host invalidates the readback allocation, interprets it as a 32 by 32 pixel buffer, builds an all-white reference, and calls `tcu::floatThresholdCompare` with a zero threshold. A mismatch returns `TestStatus::fail("Failed")`; a complete match returns `TestStatus::pass("Pass")`.

The host uses `VK_CHECK` for object creation and memory operations where those calls return a `VkResult`. The final conformance result comes from the host-side pixel comparison, not from a query that reports whether element `2` was valid. A dispatch failure, device loss, validation error, or crash before comparison is therefore a failure of the exercised execution path, but this page does not assign it to a specific hardware or driver component without more evidence.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `write.unused` | Incorrect handling of an undefined, dynamically unaccessed array element in a partially bound descriptor binding. |
| `write.invalid` | Incorrect validation or execution treatment of a live but access-incompatible image descriptor that no invocation accesses. |
| `copy` | Incorrect copying or later consumption of a destination binding whose unaccessed element became undefined after its source resource was destroyed. |

A mismatch shared by all three values can instead come from their common dynamic indexing, descriptor selection, resource initialization, compute execution, transfer, or host comparison path.

### Cause Analysis

#### Undefined, dynamically unaccessed descriptor handling

**Possible failure symptoms:** `write.unused` fails before producing the all-white image, or the output contains pixels other than `(1.0, 1.0, 1.0, 1.0)`. The failure can appear as a dispatch error, device loss, incomplete result image, or pixel mismatch.

**Possible implementation causes:** the implementation may require or consume the undefined third element even though the binding is partially bound and no invocation dynamically accesses it. The source and spec establish the descriptor state and the access pattern, but they do not identify whether a failure would arise in descriptor fetching, shader lowering, resource lifetime handling, or another implementation path. Source-level investigation is needed for a specific failure.

#### Live but access-incompatible descriptor not accessed

**Possible failure symptoms:** `write.invalid` fails while elements `0` and `1` still contain the initialized single-sample or correctly formatted resources. The result may be a dispatch failure or an image mismatch rather than a targeted host error about element `2`.

**Possible implementation causes:** the implementation may validate the sample-count or image-format compatibility of the live third image as though a shader invocation accessed it. Vulkan's image compatibility rules apply when an image view is accessed, while the partially bound rule makes the dynamically unaccessed element exempt from the validity requirement. A failure could also come from an independent mismatch in the selected valid resources or generated shader. The test does not distinguish those causes without diagnostics.

#### Copying and consuming a descriptor made undefined by destruction

**Possible failure symptoms:** `copy` fails during descriptor update, dispatch, queue completion, or the final pixel comparison. If elements `0` and `1` were mishandled, the result differs from white; if the implementation consumes element `2`, the case may fail before the host can compare pixels.

**Possible implementation causes:** the implementation may treat copying a reference as resource use, fail to propagate the undefined state to the destination, or later require the destination's unaccessed element to be valid despite `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`. The source also destroys the resource internals before copying, so a concrete diagnosis must check descriptor update handling and object lifetime together. Vulkan does not imply that a failure belongs to hardware, the driver, or the host by itself.

## Case Pruning

### Requirement-based pruning

- The family is Vulkan-only because [`vktBindingModelTests.cpp`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L32-L42) includes and registers it only when `CTS_USES_VULKANSC` is not defined.
- Each case is skipped with `NotSupportedError` when `VK_EXT_descriptor_indexing`, `descriptorBindingPartiallyBound`, or the selected resource-array dynamic-indexing feature is unavailable. A skip is not a conformance failure.
- `write.invalid` uses only image resource types because `makeImageCI()` provides controlled sample-count and format incompatibilities for images. The source does not construct an equivalent invalid buffer case.


### Design-based pruning

- The API binding has three elements, while the generated GLSL array has two and the host fixes `index` at zero. This deliberate shape makes element `2` the unaccessed state under test.
- `write.unused` leaves element `2` undefined rather than writing a placeholder resource. `write.invalid` writes the controlled image incompatibility only for image types.
- `copy` always copies three elements after destroying the resource behind element `2`, but the shader still reads only elements `0` and `1`. Accessing element `2` would test a different requirement and would not represent the intended partial-binding case.
- The generated program has one common control-flow shape. Resource-type differences are covered by the registered matrix and the variation summary rather than by separate shader walkthroughs.

## Key Takeaways

- `statically used`, `dynamically used`, `valid`, `invalid`, and `copied` describe different properties. A shader can statically use a descriptor array while a particular invocation set dynamically accesses only selected elements.
- `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT` makes the unaccessed element legal to leave undefined or access-incompatible in these cases. It does not make a dynamically accessed descriptor safe.
- `write.invalid` keeps the image object alive and tests access compatibility. `copy` destroys the source resource before copying and tests the destination's resulting undefined descriptor. They are not the same invalid state.
- The host checks only the observable result from elements `0` and `1`. A passing result supports the tested descriptor-consumption behavior for the selected resource type and queue path; it does not establish a blanket hardware or driver property.
- `write.unused`, `write.invalid`, and `copy` are the behavior axis. The five resource types are coverage variants over the same two-access execution pattern.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Resource and descriptor-type mapping | [`ResourceType`, `getVkDescriptorType()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L61-L152) | Defines the five registered resource types and their Vulkan descriptor types. |
| Image invalidity construction | [`makeImageCI()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L155-L215) | Selects `VK_SAMPLE_COUNT_4_BIT` for sampled-image invalidity and `VK_FORMAT_R32_UINT` for storage-image invalidity. |
| Generated declaration and access | [`getResourceDeclaration()`, `getResourceAccess()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L245-L337) | Emits the shader-side resource arrays and the two accesses selected by `pc.index`. |
| Resource lifecycle | [`Resource`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L339-L599) | Creates, initializes, and destroys the buffers, images, views, and samplers used by each case. |
| Write shader and support | [`UnusedInvalidDescriptorWriteTestCase`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L601-L699) | Generates the write shader and applies descriptor-indexing feature gates. |
| Write execution | [`UnusedInvalidDescriptorWriteTestInstance::queuePass()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L701-L946) | Builds the set, writes the selected descriptor states, dispatches, copies back, and compares. |
| Copy execution | [`InvalidDescriptorCopyTestInstance::queuePass()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1014-L1279) | Destroys the third source resource, copies all three elements, and executes with the destination set. |
| Registration | [`createUnusedInvalidDescriptorTests()`](../../../modules/vulkan/binding_model/vktBindingUnusedInvalidDescriptorTests.cpp#L1283-L1354) | Registers `write.unused`, `write.invalid`, `copy`, and their exact leaves. |
| Category availability | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71) | Places this family under the Vulkan-only registration branch. |
| Mustpass paths | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L146935-L146947) | Confirms all thirteen executable paths in the default Vulkan mustpass list. |
| Descriptor initial state and partial binding | [Descriptor set allocation and binding flags](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptor-set-initial-state) | Defines undefined descriptors, partial binding, and dynamic use. |
| Descriptor validity | [Descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptor-validity) | Defines validity in terms of undefined state, binding flags, and consuming descriptor type. |
| Descriptor copy semantics | [Descriptor Set Updates](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#descriptors-sets-updates) | States that copying does not use the referenced resource and that an undefined source makes the destination undefined. |
| Static use | [Static Use](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-staticuse) | Defines static use for SPIR-V objects and entry-point interfaces. |
| Image access compatibility | [Texel Input Validation](../../../../vulkan-docs/src/chapters/textures.adoc#textures-input-validation) | Defines sample-count, sampled-type, format, and image-view compatibility on image access. |
| Queue iteration | [`MultiQueueRunnerTestInstance`](../../../modules/vulkan/vktTestCase.cpp#L1815-L1877) | Shows how the test repeats `queuePass()` across available compute-capable queues and aggregates results. |
