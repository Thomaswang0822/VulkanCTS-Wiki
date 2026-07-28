## Overview

**Core question:** Can each mutable descriptor element change to an allowed active type and still expose the correct resource when the test varies writes, copies, arrays, pool declarations, update timing, and shader stages?

- [`vktBindingMutableTests.cpp`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp) implements `binding_model.mutable_descriptor` and creates eight test families: `single`, `single_nonmutable`, `one_array`, `multiple_arrays`, `multiple_arrays_mixed`, `single_and_array`, `multiple`, and `misc`.
- A mutable layout binding uses `VK_DESCRIPTOR_TYPE_MUTABLE_EXT` and a list of permitted descriptor types. The test updates or copies concrete descriptors into that binding, then generates one shader per active-type iteration so the shader's declared resource type matches the element it consumes.
- The families cover scalar bindings, fixed and runtime-sized arrays, several typed declarations over one aliased binding, mixed mutable and fixed-type layouts, all ordered type switches, and an out-of-range pool type-list rule.
- Device-side checks read deterministic resource values and write selected storage resources. The host requires a result value of `2` for every iteration and verifies every shader writeback.

## Background Knowledge

For the shared concepts of descriptor interfaces, active state, and validity, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Mutable and non-mutable bindings.** A non-mutable binding fixes its descriptor type in `VkDescriptorSetLayoutBinding`. A mutable binding uses `VK_DESCRIPTOR_TYPE_MUTABLE_EXT`, while its `VkMutableDescriptorTypeListEXT` lists permitted active types. Each descriptor element has an active type. A write selects the write's concrete `descriptorType`; a copy transfers an active type under the mutable-copy rules ([mutable descriptors](../../../../vulkan-docs/src/chapters/descriptors.adoc#L593-L637), [mutable writes](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3204-L3207), [mutable copies](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3927-L3946)).
- **Mutable descriptor feature contract.** Enabling `mutableDescriptorType` guarantees support for any combination of sampled image, storage image, uniform texel buffer, storage texel buffer, uniform buffer, and storage buffer types. Implementations may support more types; applications can query a specific layout with `vkGetDescriptorSetLayoutSupport` ([mutable descriptor feature](../../../../vulkan-docs/src/chapters/features.adoc#L5552-L5605)).
- **Shader resource type and descriptor validity.** `DescriptorSet` and `Binding` decorations associate a shader resource variable with a layout binding. When a shader consumes a mutable descriptor, its resource type must match the element's active descriptor type. An uninitialized mutable element, or an element whose active type does not match, is undefined ([resource binding assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1575-L1611), [descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4596-L4619)).
- **Aliased shader declarations.** Several resource variables may use the same set and binding decorations. An array whose elements have different active types needs several typed declarations over that one binding. The shader accesses each element only through the declaration matching its active type. Vulkan's shader-interface rules permit shared set and binding values, subject to type use and aliasing rules ([shared declarations](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1694-L1715)).
- **Descriptor indexing flags.** An aliased binding uses `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`, so only dynamically used elements need valid descriptors. A runtime-sized final binding uses `VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT`, and set allocation supplies its actual count ([binding flags](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L775-L814), [descriptor population](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2581-L2589)).
- **Update-after-bind.** With `VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT`, an application may update a binding after it binds the set when the pool and layout carry the matching flags and the device supports updates for every concrete type involved ([layout and pool contract](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L363-L375), [per-type features](../../../../vulkan-docs/src/chapters/features.adoc#L2078-L2121)). The `maxUpdateAfterBindDescriptorsInAllPools` property bounds descriptors allocated across all pools with the update-after-bind flag ([descriptor indexing property](../../../../vulkan-docs/src/chapters/limits.adoc#L2523-L2531)).

## Registration Hierarchy

```text
binding_model.mutable_descriptor
├── single
├── single_nonmutable
├── one_array
├── multiple_arrays
├── multiple_arrays_mixed
├── single_and_array
├── multiple
└── misc
```

The binding-model factory attaches `mutable_descriptor` only in non-Vulkan-SC builds ([`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71)). The mutable factory creates all eight children in the same implementation file ([`createDescriptorMutableTests()` and `createChildren()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3948-L4344)).

## Parameter Dimensions and Observed Values

The default Vulkan mustpass file contains 14,310 leaves from line 46,192 through 60,501. The family counts are `misc` 6, `multiple` 60, `multiple_arrays` 192, `multiple_arrays_mixed` 192, `one_array` 192, `single` 12,285, `single_and_array` 288, and `single_nonmutable` 1,095 ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L46192-L60501)).

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `single`, `single_nonmutable`, `one_array`, `multiple_arrays`, `multiple_arrays_mixed`, `single_and_array`, `multiple`, `misc` | Selects the descriptor-set shape and mutable versus fixed-type relationship. | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3953-L4344) |
| Basic concrete type | `sampler`, `combined_image_sampler`, `sampled_image`, `storage_image`, `uniform_texel_buffer`, `storage_texel_buffer`, `uniform_buffer`, `storage_buffer`, `input_attachment`, `acceleration_structure_khr` | Selects the resource object, GLSL declaration, read operation, and whether the shader also writes the resource. | [basic type list](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3957-L3968), [declarations and checks](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1134-L1350) |
| Mandatory mutable list | `sampled_image`, `storage_image`, `uniform_texel_buffer`, `storage_texel_buffer`, `uniform_buffer`, `storage_buffer` | Supplies the cross-class list used by `all_mandatory`, arrays, and multi-binding families. | [`getMandatoryMutableTypes()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L204-L211) |
| Array extent | `constant_size`, `unbounded` | Chooses a six-element GLSL array or a runtime-sized final binding allocated with an explicit variable descriptor count. | [array registration](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4079-L4188) |
| Per-iteration array type pattern | `noaliasing`, `aliasing` | Gives all elements one active type, or rotates the type list per element so several concrete types share one binding during an iteration. | [array construction](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L4088-L4164) |
| Update operation | `update_write`, `update_copy` | Writes concrete descriptors into the destination or writes a source set and copies whole bindings into the destination. | [`createMutableTestVariants()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3758-L3765) |
| Copy source binding form | `mutable_source`, `nonmutable_source`; `no_source` for writes | Uses a mutable-compatible source layout or a per-iteration fixed-type source layout. | [source strategies](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3767-L3775), [`genSourceSet()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1575-L1588) |
| Copy source allocation | `normal_source`, `host_only_source`; `no_source` for writes | Allocates the copy source from an ordinary pool or a host-only pool. | [source types](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3777-L3785), [source flags](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2239-L2295) |
| Mutable pool type-list strategy | `pool_same_types`, `pool_no_types`, `pool_expand_types` | Keeps the layout's lists, omits pool lists, or broadens each list with all mandatory types. | [pool strategies](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3787-L3795), [`makeDescriptorPool()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1590-L1687) |
| Update moment | `pre_update`, `update_after_bind` | Orders descriptor update before binding or binding before descriptor update. | [registered values](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3797-L3804), [command order](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3632-L3667) |
| Array access | `index_constant`, `index_push_constant`; `no_array` for scalar layouts | Uses literal array indices or adds a zero push constant to produce dynamically uniform indices. | [access values](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3806-L3814), [index generation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1204-L1217) |
| Shader stage | `comp`, `vert`, `tesc`, `tese`, `geom`, `frag`, `rgen`, `isec`, `ahit`, `chit`, `miss`, `call` | Runs the checks at a compute, graphics, or ray-tracing stage. Each family uses an appropriate subset. | [stage table](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3816-L3825), [family stage sets](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3972-L3989) |
| Active-type iteration | `0` through the longest binding list minus one | Selects one concrete active type per scalar element and one active type per array element. The generator builds a separate shader and pipeline for each iteration. | [`maxTypes()` and `typesAtIteration()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1042-L1067), [iteration shaders](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2521-L2640) |

## Behavior Parameters

The primary behavioral axis is the top-level test family. Each value changes the descriptor-set shape or the relationship between mutable and non-mutable bindings. The update, source, pool, timing, access, stage, and concrete-type dimensions exercise that shape through different legal paths.

### `single` - One mutable descriptor and type switching

A single mutable binding covers each basic concrete descriptor type. `all_mandatory` rotates one slot through the six mandatory types, while `switches` constructs every ordered pair of distinct basic types and verifies that the same slot can change from the initial type to the final type. This family carries the widest stage coverage.

### `single_nonmutable` - Fixed-type destination baseline

The destination layout uses one ordinary descriptor type rather than `VK_DESCRIPTOR_TYPE_MUTABLE_EXT`. Write cases update it directly. Copy cases create a mutable or non-mutable source compatible with the fixed destination for the current iteration. This isolates copy compatibility and ordinary descriptor behavior from destination mutation.

### `one_array` - One mutable descriptor array

One six-element binding rotates through the mandatory type list. `noaliasing` makes every element share one active type per iteration. `aliasing` gives each element a different rotation, so several active types coexist in the binding and the compute shader declares several typed arrays at the same set and binding. Constant and runtime-sized arrays use literal or push-constant-adjusted indices.

### `multiple_arrays` - Several independent mutable arrays

Six mutable array bindings each start from a different rotation of the mandatory list. The test switches many bindings and elements in one set, including aliased, runtime-sized final-binding, update-after-bind, and copy variants. Each binding keeps its own permitted list and active-type sequence.

### `multiple_arrays_mixed` - Mutable and fixed-type arrays interleaved

The mutable arrays use the same rotation scheme as `multiple_arrays`. A fixed-type array follows each mutable array except after an unbounded final binding. The resulting layout checks that mutable type-list metadata, binding flags, writes, copies, and shader mapping do not shift or corrupt neighboring non-mutable bindings.

### `single_and_array` - Extended lists across scalar and array bindings

A scalar mutable binding precedes a mutable array. Their type list contains the six mandatory types plus one legal non-mandatory type selected by the intermediate node: `sampler`, `combined_image_sampler`, or `acceleration_structure_khr`. The factory excludes input attachments because this family uses arrays. The array can use aliased or uniform active types.

### `multiple` - Several mutable scalar bindings

Six mutable scalar bindings start from different list rotations, so every iteration assigns them different active types. `mutable_only` contains those six bindings. `mixed` interleaves a fixed-type scalar after each mutable scalar, testing multi-binding offsets and metadata without array indexing.

### `misc` - Out-of-range mutable pool lists

These six leaves place zero to two non-mutable uniform-buffer bindings before one or two mutable storage-buffer bindings. The pool's mutable type-list count stops before the mutable entries. Vulkan treats an out-of-range pool list like an omitted list, so allocation must still support any mutable type. The generated compute shader then checks the resulting storage-buffer descriptors and their writes.

## Shader Analysis

One walkthrough captures the central generated-shader mechanism. The selected `one_array` case places all six mandatory active types in one mutable array during iteration 0, declares six typed GLSL arrays over that binding, updates after binding, and checks both reads and storage writes. Later iterations rotate the element-to-type mapping without changing the checking protocol. The shader has no explicit `ShaderBuildOptions`, so it uses the CTS baseline SPIR-V 1.0 target.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.mutable_descriptor.one_array.constant_size.aliasing.update_write.no_source.no_source.pool_same_types.update_after_bind.index_constant.comp
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `one_array.constant_size.aliasing` | Uses one six-element mutable array whose elements have different active types in each iteration. |
| `update_write` | Writes the six concrete descriptors straight into the destination set. |
| `pool_same_types` | Gives the pool the same six-type list as the layout. |
| `update_after_bind` | Binds the destination set before the host writes its descriptors. |
| `index_constant.comp` | Uses literal array-element indices in a `1 x 1 x 1` compute dispatch. |
| Iteration `0` | Maps elements 0 through 5 to sampled image, storage image, uniform texel buffer, storage texel buffer, uniform buffer, and storage buffer. |

#### Purpose

The shader proves that six elements in one mutable binding can hold six different active descriptor types at once. It reads each element through the matching shader resource declaration, records any mismatch, and writes back through the three storage-capable elements.

#### Structural Design

| Phase | Shader operation | Observable meaning |
|-------|------------------|--------------------|
| Claim result slot | `atomicCompSwap` changes `outputBuffer.value[0]` from `0` to `1`. | Only the first invocation performs the checks. |
| Select typed views | Six arrays share set 0 binding 0; each check uses the element matching that declaration's active type. | Makes descriptor-element type aliasing visible in the shader interface. |
| Verify resources | Sample, load, or fetch deterministic values `0x5a000000` through `0x5a000005`. | Confirms each descriptor resolves to the host-created resource for its active type. |
| Verify writes | OR storage image, storage texel buffer, and storage buffer values with `0xFF000000`. | Gives the host an independent resource writeback check. |
| Record success | Add one to the result slot when `anyError` remains zero. | The host requires the final value `2`. |

#### Shader Code

```glsl
#version 460
#extension GL_EXT_nonuniform_qualifier : enable
#extension GL_EXT_debug_printf : enable

layout (local_size_x=1, local_size_y=1, local_size_z=1) in;

/// Set 1 binding 0 is a six-element result buffer, one uint for each mutable-type iteration.
layout (set=1, binding=0) buffer OutputBufferBlock { uint value[6]; } outputBuffer;
/// Set 1 binding 1 supplies the sampler needed to read sampled-image descriptors.
layout (set=1, binding=1) uniform sampler externalSampler;

/// Six shader resource variables alias set 0 binding 0. Each variable views the same six-element binding through one active descriptor type.
layout (set=0, binding=0) uniform utexture2D sampledImage_0_0[6];
layout (set=0, binding=0, r32ui) uniform uimage2D storageImage_0_0[6];
layout (set=0, binding=0) uniform utextureBuffer uniformTexel_0_0[6];
layout (set=0, binding=0, r32ui) uniform uimageBuffer storageTexel_0_0[6];
layout (set=0, binding=0) uniform uboBlock_0_0 { uint val; } ubo_0_0[6];
layout (set=0, binding=0) buffer sboBlock_0_0 { uint val; } ssbo_0_0[6];

void main() {
  const uint flag = atomicCompSwap(outputBuffer.value[0], 0u, 1u);
  if (flag == 0u) {
    uint anyError = 0u;
    {
      uint readValue = texture(usampler2D(sampledImage_0_0[0], externalSampler), vec2(0, 0)).r;
      debugPrintfEXT("iteration-0_0_0[0]: 0x%xu\n", readValue);
      anyError |= ((readValue == 0x5a000000u) ? 0u : 1u);
    }
    {
      uint readValue = imageLoad(storageImage_0_0[1], ivec2(0, 0)).x;
      debugPrintfEXT("iteration-0_0_0[1]: 0x%xu\n", readValue);
      anyError |= ((readValue == 0x5a000001u) ? 0u : 1u);
      readValue |= 0xFF000000u;
      imageStore(storageImage_0_0[1], ivec2(0, 0), uvec4(readValue, 0, 0, 0));
    }
    {
      uint readValue = texelFetch(uniformTexel_0_0[2], 0).x;
      debugPrintfEXT("iteration-0_0_0[2]: 0x%xu\n", readValue);
      anyError |= ((readValue == 0x5a000002u) ? 0u : 1u);
    }
    {
      uint readValue = imageLoad(storageTexel_0_0[3], 0).x;
      debugPrintfEXT("iteration-0_0_0[3]: 0x%xu\n", readValue);
      anyError |= ((readValue == 0x5a000003u) ? 0u : 1u);
      readValue |= 0xFF000000u;
      imageStore(storageTexel_0_0[3], 0, uvec4(readValue, 0, 0, 0));
    }
    {
      uint readValue = ubo_0_0[4].val;
      debugPrintfEXT("iteration-0_0_0[4]: 0x%xu\n", readValue);
      anyError |= ((readValue == 0x5a000004u) ? 0u : 1u);
    }
    {
      uint readValue = ssbo_0_0[5].val;
      debugPrintfEXT("iteration-0_0_0[5]: 0x%xu\n", readValue);
      anyError |= ((readValue == 0x5a000005u) ? 0u : 1u);
      ssbo_0_0[5].val = (readValue | 0xFF000000u);
    }
    if (anyError == 0u) {
      atomicAdd(outputBuffer.value[0], 1u);
    }
  }
}
```

#### Additional Info

- The shader shown is the exact iteration-0 result of `ArrayBinding::glslDeclarations()` and `glslCheckStatements()` for this binding construction. The `///` comments are wiki annotations; the executable statements follow the source generator ([array declarations and checks](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1478-L1528), [shader assembly](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2521-L2608)).
- Descriptor values use `0x5aIIBBDD`. Here `II=0`, `BB=0`, and `DD` runs from 0 through 5 ([`getDescriptorNumericValue()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L142-L149)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Later active-type iterations | Rotates which typed declaration reads each array element and changes `II` in the expected values. | [`typesAtIteration()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1402-L1410), [iteration loop](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2521-L2640) |
| `noaliasing` | Emits one typed array declaration because every element has the same active type during an iteration. | [`ArrayBinding::glslDeclarations()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1478-L1509) |
| `unbounded` | Replaces `[6]` with `[]`; host allocation still supplies six descriptors. | [array suffix generation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1134-L1144), [variable count allocation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3271-L3286) |
| `index_push_constant` | Changes each element expression from `[N]` to `[N + pc.zero]`. The host pushes zero. | [index generation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1210-L1217), [push](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3669-L3671) |
| Resource type | Samplers and sampled images use external partners; buffers, images, texel buffers, input attachments, and acceleration structures use type-specific declarations and checks. | [`SingleBinding::glslDeclarations()` and `glslCheckStatements()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1134-L1350) |
| Shader stage | The check body stays the same. Stage-specific preambles, passthrough shaders, and dispatch, draw, or trace commands make it execute in the selected stage. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2411-L2735), [`iterate()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3482-L3693) |

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
; Bound: 178
; Schema: 0
               OpCapability Shader
               OpCapability SampledBuffer
               OpCapability ImageBuffer
               OpExtension "SPV_KHR_non_semantic_info"
          %1 = OpExtInstImport "GLSL.std.450"
         %50 = OpExtInstImport "NonSemantic.DebugPrintf"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
         %48 = OpString "iteration-0_0_0[0]: 0x%xu
"
         %71 = OpString "iteration-0_0_0[1]: 0x%xu
"
         %98 = OpString "iteration-0_0_0[2]: 0x%xu
"
        %118 = OpString "iteration-0_0_0[3]: 0x%xu
"
        %141 = OpString "iteration-0_0_0[4]: 0x%xu
"
        %158 = OpString "iteration-0_0_0[5]: 0x%xu
"
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_debug_printf"
               OpSourceExtension "GL_EXT_nonuniform_qualifier"
               OpName %main "main"
               OpName %flag "flag"
               OpName %OutputBufferBlock "OutputBufferBlock"
               OpMemberName %OutputBufferBlock 0 "value"
               OpName %outputBuffer "outputBuffer"
               OpName %anyError "anyError"
               OpName %readValue "readValue"
               OpName %sampledImage_0_0 "sampledImage_0_0"
               OpName %externalSampler "externalSampler"
               OpName %readValue_0 "readValue"
               OpName %storageImage_0_0 "storageImage_0_0"
               OpName %readValue_1 "readValue"
               OpName %uniformTexel_0_0 "uniformTexel_0_0"
               OpName %readValue_2 "readValue"
               OpName %storageTexel_0_0 "storageTexel_0_0"
               OpName %readValue_3 "readValue"
               OpName %uboBlock_0_0 "uboBlock_0_0"
               OpMemberName %uboBlock_0_0 0 "val"
               OpName %ubo_0_0 "ubo_0_0"
               OpName %readValue_4 "readValue"
               OpName %sboBlock_0_0 "sboBlock_0_0"
               OpMemberName %sboBlock_0_0 0 "val"
               OpName %ssbo_0_0 "ssbo_0_0"
               OpDecorate %_arr_uint_uint_6 ArrayStride 4
               OpDecorate %OutputBufferBlock BufferBlock
               OpMemberDecorate %OutputBufferBlock 0 Offset 0
               OpDecorate %outputBuffer Binding 0
               OpDecorate %outputBuffer DescriptorSet 1
               OpDecorate %sampledImage_0_0 Binding 0
               OpDecorate %sampledImage_0_0 DescriptorSet 0
               OpDecorate %externalSampler Binding 1
               OpDecorate %externalSampler DescriptorSet 1
               OpDecorate %storageImage_0_0 Binding 0
               OpDecorate %storageImage_0_0 DescriptorSet 0
               OpDecorate %uniformTexel_0_0 Binding 0
               OpDecorate %uniformTexel_0_0 DescriptorSet 0
               OpDecorate %storageTexel_0_0 Binding 0
               OpDecorate %storageTexel_0_0 DescriptorSet 0
               OpDecorate %uboBlock_0_0 Block
               OpMemberDecorate %uboBlock_0_0 0 Offset 0
               OpDecorate %ubo_0_0 Binding 0
               OpDecorate %ubo_0_0 DescriptorSet 0
               OpDecorate %sboBlock_0_0 BufferBlock
               OpMemberDecorate %sboBlock_0_0 0 Offset 0
               OpDecorate %ssbo_0_0 Binding 0
               OpDecorate %ssbo_0_0 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_6 = OpConstant %uint 6
%_arr_uint_uint_6 = OpTypeArray %uint %uint_6
%OutputBufferBlock = OpTypeStruct %_arr_uint_uint_6
%_ptr_Uniform_OutputBufferBlock = OpTypePointer Uniform %OutputBufferBlock
%outputBuffer = OpVariable %_ptr_Uniform_OutputBufferBlock Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
       %bool = OpTypeBool
         %28 = OpTypeImage %uint 2D 0 0 0 1 Unknown
%_arr_28_uint_6 = OpTypeArray %28 %uint_6
%_ptr_UniformConstant__arr_28_uint_6 = OpTypePointer UniformConstant %_arr_28_uint_6
%sampledImage_0_0 = OpVariable %_ptr_UniformConstant__arr_28_uint_6 UniformConstant
%_ptr_UniformConstant_28 = OpTypePointer UniformConstant %28
         %35 = OpTypeSampler
%_ptr_UniformConstant_35 = OpTypePointer UniformConstant %35
%externalSampler = OpVariable %_ptr_UniformConstant_35 UniformConstant
         %39 = OpTypeSampledImage %28
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
    %float_0 = OpConstant %float 0
         %44 = OpConstantComposite %v2float %float_0 %float_0
     %v4uint = OpTypeVector %uint 4
%uint_1509949440 = OpConstant %uint 1509949440
         %59 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_arr_59_uint_6 = OpTypeArray %59 %uint_6
%_ptr_UniformConstant__arr_59_uint_6 = OpTypePointer UniformConstant %_arr_59_uint_6
%storageImage_0_0 = OpVariable %_ptr_UniformConstant__arr_59_uint_6 UniformConstant
      %int_1 = OpConstant %int 1
%_ptr_UniformConstant_59 = OpTypePointer UniformConstant %59
      %v2int = OpTypeVector %int 2
         %68 = OpConstantComposite %v2int %int_0 %int_0
%uint_1509949441 = OpConstant %uint 1509949441
%uint_4278190080 = OpConstant %uint 4278190080
         %88 = OpTypeImage %uint Buffer 0 0 0 1 Unknown
%_arr_88_uint_6 = OpTypeArray %88 %uint_6
%_ptr_UniformConstant__arr_88_uint_6 = OpTypePointer UniformConstant %_arr_88_uint_6
%uniformTexel_0_0 = OpVariable %_ptr_UniformConstant__arr_88_uint_6 UniformConstant
      %int_2 = OpConstant %int 2
%_ptr_UniformConstant_88 = OpTypePointer UniformConstant %88
%uint_1509949442 = OpConstant %uint 1509949442
        %108 = OpTypeImage %uint Buffer 0 0 0 2 R32ui
%_arr_108_uint_6 = OpTypeArray %108 %uint_6
%_ptr_UniformConstant__arr_108_uint_6 = OpTypePointer UniformConstant %_arr_108_uint_6
%storageTexel_0_0 = OpVariable %_ptr_UniformConstant__arr_108_uint_6 UniformConstant
      %int_3 = OpConstant %int 3
%_ptr_UniformConstant_108 = OpTypePointer UniformConstant %108
%uint_1509949443 = OpConstant %uint 1509949443
%uboBlock_0_0 = OpTypeStruct %uint
%_arr_uboBlock_0_0_uint_6 = OpTypeArray %uboBlock_0_0 %uint_6
%_ptr_Uniform__arr_uboBlock_0_0_uint_6 = OpTypePointer Uniform %_arr_uboBlock_0_0_uint_6
    %ubo_0_0 = OpVariable %_ptr_Uniform__arr_uboBlock_0_0_uint_6 Uniform
      %int_4 = OpConstant %int 4
%uint_1509949444 = OpConstant %uint 1509949444
%sboBlock_0_0 = OpTypeStruct %uint
%_arr_sboBlock_0_0_uint_6 = OpTypeArray %sboBlock_0_0 %uint_6
%_ptr_Uniform__arr_sboBlock_0_0_uint_6 = OpTypePointer Uniform %_arr_sboBlock_0_0_uint_6
   %ssbo_0_0 = OpVariable %_ptr_Uniform__arr_sboBlock_0_0_uint_6 Uniform
      %int_5 = OpConstant %int 5
%uint_1509949445 = OpConstant %uint 1509949445
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
       %flag = OpVariable %_ptr_Function_uint Function
   %anyError = OpVariable %_ptr_Function_uint Function
  %readValue = OpVariable %_ptr_Function_uint Function
%readValue_0 = OpVariable %_ptr_Function_uint Function
%readValue_1 = OpVariable %_ptr_Function_uint Function
%readValue_2 = OpVariable %_ptr_Function_uint Function
%readValue_3 = OpVariable %_ptr_Function_uint Function
%readValue_4 = OpVariable %_ptr_Function_uint Function
         %17 = OpAccessChain %_ptr_Uniform_uint %outputBuffer %int_0 %int_0
         %20 = OpAtomicCompareExchange %uint %17 %uint_1 %uint_0 %uint_0 %uint_1 %uint_0
               OpStore %flag %20
         %21 = OpLoad %uint %flag
         %23 = OpIEqual %bool %21 %uint_0
               OpSelectionMerge %25 None
               OpBranchConditional %23 %24 %25
         %24 = OpLabel
               OpStore %anyError %uint_0
         %33 = OpAccessChain %_ptr_UniformConstant_28 %sampledImage_0_0 %int_0
         %34 = OpLoad %28 %33
         %38 = OpLoad %35 %externalSampler
         %40 = OpSampledImage %39 %34 %38
         %46 = OpImageSampleExplicitLod %v4uint %40 %44 Lod %float_0
         %47 = OpCompositeExtract %uint %46 0
               OpStore %readValue %47
         %49 = OpLoad %uint %readValue
         %51 = OpExtInst %void %50 1 %48 %49
         %52 = OpLoad %uint %readValue
         %54 = OpIEqual %bool %52 %uint_1509949440
         %55 = OpSelect %uint %54 %uint_0 %uint_1
         %56 = OpLoad %uint %anyError
         %57 = OpBitwiseOr %uint %56 %55
               OpStore %anyError %57
         %65 = OpAccessChain %_ptr_UniformConstant_59 %storageImage_0_0 %int_1
         %66 = OpLoad %59 %65
         %69 = OpImageRead %v4uint %66 %68
         %70 = OpCompositeExtract %uint %69 0
               OpStore %readValue_0 %70
         %72 = OpLoad %uint %readValue_0
         %73 = OpExtInst %void %50 1 %71 %72
         %74 = OpLoad %uint %readValue_0
         %76 = OpIEqual %bool %74 %uint_1509949441
         %77 = OpSelect %uint %76 %uint_0 %uint_1
         %78 = OpLoad %uint %anyError
         %79 = OpBitwiseOr %uint %78 %77
               OpStore %anyError %79
         %81 = OpLoad %uint %readValue_0
         %82 = OpBitwiseOr %uint %81 %uint_4278190080
               OpStore %readValue_0 %82
         %83 = OpAccessChain %_ptr_UniformConstant_59 %storageImage_0_0 %int_1
         %84 = OpLoad %59 %83
         %85 = OpLoad %uint %readValue_0
         %86 = OpCompositeConstruct %v4uint %85 %uint_0 %uint_0 %uint_0
               OpImageWrite %84 %68 %86
         %94 = OpAccessChain %_ptr_UniformConstant_88 %uniformTexel_0_0 %int_2
         %95 = OpLoad %88 %94
         %96 = OpImageFetch %v4uint %95 %int_0
         %97 = OpCompositeExtract %uint %96 0
               OpStore %readValue_1 %97
         %99 = OpLoad %uint %readValue_1
        %100 = OpExtInst %void %50 1 %98 %99
        %101 = OpLoad %uint %readValue_1
        %103 = OpIEqual %bool %101 %uint_1509949442
        %104 = OpSelect %uint %103 %uint_0 %uint_1
        %105 = OpLoad %uint %anyError
        %106 = OpBitwiseOr %uint %105 %104
               OpStore %anyError %106
        %114 = OpAccessChain %_ptr_UniformConstant_108 %storageTexel_0_0 %int_3
        %115 = OpLoad %108 %114
        %116 = OpImageRead %v4uint %115 %int_0
        %117 = OpCompositeExtract %uint %116 0
               OpStore %readValue_2 %117
        %119 = OpLoad %uint %readValue_2
        %120 = OpExtInst %void %50 1 %118 %119
        %121 = OpLoad %uint %readValue_2
        %123 = OpIEqual %bool %121 %uint_1509949443
        %124 = OpSelect %uint %123 %uint_0 %uint_1
        %125 = OpLoad %uint %anyError
        %126 = OpBitwiseOr %uint %125 %124
               OpStore %anyError %126
        %127 = OpLoad %uint %readValue_2
        %128 = OpBitwiseOr %uint %127 %uint_4278190080
               OpStore %readValue_2 %128
        %129 = OpAccessChain %_ptr_UniformConstant_108 %storageTexel_0_0 %int_3
        %130 = OpLoad %108 %129
        %131 = OpLoad %uint %readValue_2
        %132 = OpCompositeConstruct %v4uint %131 %uint_0 %uint_0 %uint_0
               OpImageWrite %130 %int_0 %132
        %139 = OpAccessChain %_ptr_Uniform_uint %ubo_0_0 %int_4 %int_0
        %140 = OpLoad %uint %139
               OpStore %readValue_3 %140
        %142 = OpLoad %uint %readValue_3
        %143 = OpExtInst %void %50 1 %141 %142
        %144 = OpLoad %uint %readValue_3
        %146 = OpIEqual %bool %144 %uint_1509949444
        %147 = OpSelect %uint %146 %uint_0 %uint_1
        %148 = OpLoad %uint %anyError
        %149 = OpBitwiseOr %uint %148 %147
               OpStore %anyError %149
        %156 = OpAccessChain %_ptr_Uniform_uint %ssbo_0_0 %int_5 %int_0
        %157 = OpLoad %uint %156
               OpStore %readValue_4 %157
        %159 = OpLoad %uint %readValue_4
        %160 = OpExtInst %void %50 1 %158 %159
        %161 = OpLoad %uint %readValue_4
        %163 = OpIEqual %bool %161 %uint_1509949445
        %164 = OpSelect %uint %163 %uint_0 %uint_1
        %165 = OpLoad %uint %anyError
        %166 = OpBitwiseOr %uint %165 %164
               OpStore %anyError %166
        %167 = OpLoad %uint %readValue_4
        %168 = OpBitwiseOr %uint %167 %uint_4278190080
        %169 = OpAccessChain %_ptr_Uniform_uint %ssbo_0_0 %int_5 %int_0
               OpStore %169 %168
        %170 = OpLoad %uint %anyError
        %171 = OpIEqual %bool %170 %uint_0
               OpSelectionMerge %173 None
               OpBranchConditional %171 %172 %173
        %172 = OpLabel
        %174 = OpAccessChain %_ptr_Uniform_uint %outputBuffer %int_0 %int_0
        %175 = OpAtomicIAdd %uint %174 %uint_1 %uint_0 %uint_1
               OpBranch %173
        %173 = OpLabel
               OpBranch %25
         %25 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Layout, pool, and descriptor preparation

- The destination layout has one `VkDescriptorSetLayoutBinding` per modeled binding. Mutable entries carry their permitted type lists through `VkMutableDescriptorTypeCreateInfoEXT`; non-mutable entries have empty lists. Pool variants retain, omit, or expand the corresponding mutable lists ([layout construction](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1725-L1839), [pool construction](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1590-L1687)).
- Aliased bindings receive `VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT`. A runtime-sized final binding also receives `VK_DESCRIPTOR_BINDING_VARIABLE_DESCRIPTOR_COUNT_BIT`. Update-after-bind variants add the binding bit, layout flag, and pool flag required by descriptor indexing ([binding flags](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1765-L1816), [pool and layout flags](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2239-L2295)).
- Each iteration creates one resource per active descriptor element. `0x5aIIBBDD` records iteration, binding, and element in its initial value. The resource can be a sampler, image, combined image and sampler, buffer, buffer view, or acceleration structure ([resource mapping](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L384-L435), [resource creation](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L619-L930)).
- Write variants issue one or more `VkWriteDescriptorSet` operations using each concrete active type. Copy variants write an iteration-specific source set and copy every binding to the destination. Mutable sources preserve a mutable binding; non-mutable sources fix the binding to that iteration's concrete type ([writes](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1887-L1987), [copies](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1989-L2018)).

### Bind, update, and execute

- `pre_update` calls the write or copy path first, then binds the pipeline and descriptor sets. `update_after_bind` reverses those two steps. Both paths execute only after the descriptor state is complete for the iteration ([command order](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3632-L3667)).
- Compute cases dispatch one workgroup. Graphics cases draw one triangle and use passthrough stages where required. Ray cases trace one ray or invoke a callable shader through a passthrough ray-generation shader ([pipeline construction](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3482-L3628), [execution commands](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3669-L3693)).
- Input attachments become render-pass and framebuffer attachments. Ray-query descriptor checks build an acceleration structure for each descriptor; non-ray-generation ray-stage tests create another acceleration structure to invoke the selected stage ([input attachment setup](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3065-L3234), [extra resources](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3296-L3384)).

### Device and host checks

- One invocation claims the current output slot with an atomic compare-exchange. It compares every descriptor read with its deterministic value. If all reads match, it atomically increments the slot. The host requires the slot to contain `2` ([shader result protocol](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2561-L2580), [host check](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3695-L3708)).
- Storage buffers, storage images, and storage texel buffers write the value ORed with `0xFF000000`. After queue completion, the host reads each writable resource and requires that exact result ([shader stores](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1269-L1310), [writeback check](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3710-L3747)).
- The process repeats for `descriptorSet->maxTypes()` iterations. A case passes only after every generated active-type configuration satisfies both checks.

## Failure Meaning

A failure means that the selected descriptor-set shape, update path, and shader stage did not produce the expected typed resource accesses or writebacks. The failure does not identify a driver, hardware, compiler, or test-host location by itself. The family, suffix, iteration number, output value, and any writable-resource message narrow the contract that needs investigation.

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single` | Single-element active-type selection, descriptor write or copy, type switching, shader access, or selected-stage execution failure. |
| `single_nonmutable` | Mutable or non-mutable source-copy compatibility failure, ordinary fixed-type descriptor update failure, or shader access failure. |
| `one_array` | Mutable array active-type mapping, aliased declaration, descriptor indexing, partially-bound handling, variable-count allocation, or array access failure. |
| `multiple_arrays` | Independent type rotation across several mutable arrays, multi-binding layout, descriptor indexing, or shader access failure. |
| `multiple_arrays_mixed` | Interleaved mutable and non-mutable array layout, update or copy, active-type mapping, or shader access failure. |
| `single_and_array` | Extended mutable type-list handling across scalar and array bindings, aliased array access, or descriptor update and shader access failure. |
| `multiple` | Independent switching across several mutable scalar bindings, mutable and non-mutable interleaving, or multi-binding update and access failure. |
| `misc` | Out-of-range mutable pool type-list interpretation, pool allocation, storage-buffer descriptor update, or compute verification failure. |

### Cause Analysis

#### Single-element active-type selection, descriptor write or copy, type switching, shader access, or selected-stage execution failure

**Possible failure symptoms:** A `single` iteration leaves its output value at `0` or `1`, or a writable resource lacks the `0xFF000000` mask. A `switches` failure identifies the initial and final types in the registered path. The final suffix identifies the update, source, pool, timing, and shader-stage path.

**Possible implementation causes:** The implementation may reject or misstore a permitted active type, fail to change active type on a write, transfer the wrong active type on a copy, or expose a descriptor representation that does not match the generated shader resource type. Stage-specific failures can also come from pipeline construction, passthrough-stage invocation, or compiler lowering of the shared result protocol. The output alone cannot distinguish those causes, so the exact iteration and resource log need source-level investigation.

#### Mutable or non-mutable source-copy compatibility failure, ordinary fixed-type descriptor update failure, or shader access failure

**Possible failure symptoms:** A `single_nonmutable` copy case fails while the equivalent direct write passes, or mutable-source and non-mutable-source variants differ. The shader reports a wrong read through an ordinary fixed-type destination, and storage-capable cases may also report missing writeback.

**Possible implementation causes:** The copy path may mishandle active-type compatibility when the source is mutable and the destination is not, choose the wrong descriptor representation when source conversion fixes its type for the current iteration, or copy the wrong resource reference. Vulkan requires a mutable source's active type to match a non-mutable destination type ([copy validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4027-L4039)). A failure shared with direct writes can instead lie in fixed-type updates, resource access, execution, or readback.

#### Mutable array active-type mapping, aliased declaration, descriptor indexing, partially-bound handling, variable-count allocation, or array access failure

**Possible failure symptoms:** A `one_array` case reports a wrong result for one iteration or names one writable descriptor index with an unexpected value. Failures may appear only for `aliasing`, `unbounded`, `index_push_constant`, or `update_after_bind` suffixes.

**Possible implementation causes:** The implementation may associate an array element with the wrong active type, map one of several typed shader variables to the wrong descriptor element, require validity for elements that the partially-bound rule leaves unused, allocate the wrong variable count, or lower a dynamically uniform index incorrectly. An update-after-bind-only failure can come from the binding, layout, pool, or per-type feature path. The exact differing suffix separates these mechanisms.

#### Independent type rotation across several mutable arrays, multi-binding layout, descriptor indexing, or shader access failure

**Possible failure symptoms:** A `multiple_arrays` case fails at one binding and element while the simpler `one_array` shape passes, or it fails only when several binding lists rotate independently. The output buffer can remain at `1`, and writable-resource diagnostics name the affected binding and index.

**Possible implementation causes:** The implementation may attach a mutable list or binding flag to the wrong layout binding, calculate descriptor storage offsets incorrectly across arrays, reuse active-type state between bindings, or map shader set and binding decorations incorrectly. Runtime-sized final-binding and aliased variants also carry the indexing causes described for `one_array`.

#### Interleaved mutable and non-mutable array layout, update or copy, active-type mapping, or shader access failure

**Possible failure symptoms:** `multiple_arrays_mixed` fails while the corresponding `multiple_arrays` path passes. The reported binding may point to a mutable array or to the fixed-type array that follows it.

**Possible implementation causes:** Mutable list metadata, descriptor counts, or binding flags may shift across the interleaved fixed-type entries. The update or copy path may use mutable descriptor storage size or active-type state for a neighboring non-mutable binding, or vice versa. Shader binding offsets and pool accounting can also diverge. Comparing the matching non-mixed path narrows the investigation but does not prove which layer is at fault.

#### Extended mutable type-list handling across scalar and array bindings, aliased array access, or descriptor update and shader access failure

**Possible failure symptoms:** A `single_and_array` case fails only when the permitted list adds `sampler`, `combined_image_sampler`, or `acceleration_structure_khr`, or only when that type appears in the array during a particular iteration. The result or storage writeback check fails after the host updates both a scalar and an array binding.

**Possible implementation causes:** The implementation may size or compare the extended list incorrectly, omit the added type from pool or layout handling, attach the list to the wrong binding, or mishandle the external sampler, external image, or acceleration-structure resources required by the added type. Aliasing and array-indexing causes remain possible for the second binding.

#### Independent switching across several mutable scalar bindings, mutable and non-mutable interleaving, or multi-binding update and access failure

**Possible failure symptoms:** A `multiple` iteration reports failure when several scalar mutable bindings hold different active types, or only the `mixed` intermediate node fails. Writable-resource diagnostics identify one binding, with no array index greater than zero.

**Possible implementation causes:** The implementation may share active-type state between scalar bindings, calculate descriptor storage offsets from the wrong type list, or shift mutable metadata across interleaved fixed-type bindings. It may also update or copy the wrong binding range. The absence of array indexing makes partially-bound and variable-count handling unlikely for this family.

#### Out-of-range mutable pool type-list interpretation, pool allocation, storage-buffer descriptor update, or compute verification failure

**Possible failure symptoms:** A `misc.mutable_type_out_of_range_NM` leaf fails during pool or set allocation, or the compute result and storage-buffer writeback fail after allocation. `N` records the number of preceding non-mutable descriptors and `M` the number of trailing mutable descriptors.

**Possible implementation causes:** The pool may incorrectly require an in-range type-list entry for each trailing mutable pool size, misinterpret the out-of-range entry instead of treating it as an omitted list, or calculate the list index from mutable entries rather than pool-size position. The specification states that an absent or out-of-range pool list can allocate any supported mutable type ([pool rule](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2249-L2268)). If allocation succeeds, ordinary storage-buffer update, compute access, or readback remains possible and needs source-level investigation.

## Case Pruning

### Requirement-based pruning

- The device must support `VK_VALVE_mutable_descriptor_type` or `VK_EXT_mutable_descriptor_type` and enable `mutableDescriptorType`. The whole family is absent from Vulkan SC registration ([extension and feature gate](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2808-L2823), [registration guard](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L61-L71)).
- The source calls `vkGetDescriptorSetLayoutSupport` for the destination and for every source layout used by copy variants. Unsupported mutable lists, binding flags, stage visibility, or descriptor counts produce `NotSupported` before execution ([layout checks](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2998-L3034)).
- `unbounded` requires `VK_EXT_descriptor_indexing` and `descriptorBindingVariableDescriptorCount`. `aliasing` requires the extension and `descriptorBindingPartiallyBound` ([indexing gates](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2743-L2757), [case checks](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2841-L2854)).
- `update_after_bind` checks the feature corresponding to every concrete descriptor type used by the set. Acceleration structures use their own update-after-bind feature. Input attachments do not have this test mode ([per-type checks](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2856-L2931)).
- `index_push_constant` checks dynamic array indexing for every array descriptor type. Uniform and storage texel buffers use descriptor-indexing features; the other buffer and image classes use core device features ([dynamic indexing checks](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2933-L2996)).
- Acceleration-structure descriptors require acceleration structures and ray queries. Ray stages also require acceleration structures and the ray-tracing pipeline extension. Geometry and tessellation stages require their stage features. Vertex-pipeline and fragment writes and atomics require the matching features ([ray gates](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2824-L2839), [stage gates](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3036-L3055)).

These checks mark a case unsupported when the selected legal mechanism is unavailable. They do not report a mutable-descriptor conformance failure.

### Design-based pruning

- Direct writes keep only `no_source`. Copies keep mutable and non-mutable source strategies plus normal and host-only source allocations. Combinations with an irrelevant source field are never registered.
- The generator omits a non-mutable source when an aliased array needs several concrete types in one binding during the same iteration. One fixed-type source binding cannot represent that shape.
- Array layouts keep `index_constant` and `index_push_constant`; scalar layouts keep only `no_array`.
- Input attachments are scalar, fragment-only, and exclude update-after-bind. `single_and_array` therefore excludes input attachments.
- Array and multi-binding families use compute only to contain the matrix. `single` carries full stage coverage; `all_mandatory` and `single_nonmutable` use the reduced compute, vertex, fragment, and ray-generation set.
- `switches` skips identical initial and final types because single-type and `all_mandatory` cases already cover stable active types.

This pruning removes meaningless or redundant combinations from the generated matrix. It is part of the test design rather than a device support result.

## Key Takeaways

- A mutable binding still has a precise active descriptor type per element. The layout list limits legal active types, and the shader type must match the active type when the shader consumes the descriptor.
- The test switches types by iteration and precompiles one shader interface for each concrete active-type arrangement. This makes active-type errors observable instead of relying only on API success.
- Aliased arrays place several typed shader variables at one set and binding, then access each element only through its matching declaration. Partially-bound and variable-count flags make those array layouts legal when the required descriptor-indexing features exist.
- Writes and copies cover mutable and fixed-type source relationships. `pre_update` and `update_after_bind` differ only in whether update precedes binding or follows it.
- Device checks require every typed read to match `0x5aIIBBDD`; host checks also require `2` in each result slot and masked writeback from each storage resource.
- A failure identifies the selected descriptor shape and observation path. Use `## Failure Meaning` with the exact suffix and iteration log before assigning a cause.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Binding-model category attachment | [`createChildren()`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L71) | Attaches `mutable_descriptor` in Vulkan builds and excludes it from Vulkan SC. |
| Mutable test-family factory | [`createDescriptorMutableTests()` and `createChildren()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3948-L4344) | Creates the eight top-level families and their descriptor-set shapes. |
| Mandatory and forbidden type lists | [`getForbiddenMutableTypes()` and `getMandatoryMutableTypes()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L193-L211) | Defines legal exclusions and the six-type mandatory list used by the matrix. |
| Resource objects and deterministic values | [`Resource`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L619-L932), [`getDescriptorNumericValue()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L142-L149) | Creates each concrete descriptor resource and its expected contents. |
| Scalar binding model | [`SingleBinding`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1008-L1352) | Rotates active types and emits type-specific resources, declarations, checks, and writes. |
| Array binding model | [`ArrayBinding`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1354-L1530) | Implements fixed, runtime-sized, aliased, and non-aliased arrays. |
| Pool, layout, write, and copy helpers | [`DescriptorSet`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L1536-L2075) | Builds mutable lists and flags, updates concrete descriptors, and copies whole bindings. |
| Runtime parameter mapping | [`TestParams`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2077-L2305) | Maps stage, update timing, and source type to Vulkan flags and bind points. |
| Generated shaders | [`MutableTypesTest::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2384-L2735) | Emits one shader per active-type iteration and any passthrough stages. |
| Support and layout pruning | [`MutableTypesTest::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L2808-L3056) | Applies extension, feature, indexing, stage, and layout gates. |
| Execution and result checks | [`MutableTypesInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3236-L3751) | Creates resources and pipelines, orders bind and update, submits work, and validates two result channels. |
| Secondary variant expansion | [`createMutableTestVariants()`](../../../modules/vulkan/binding_model/vktBindingMutableTests.cpp#L3755-L3928) | Generates update, source, pool, timing, access, and stage suffixes and prunes invalid combinations. |
| Mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L46192-L60501) | Confirms all 14,310 registered leaves and exact path spelling. |
| Mutable descriptor specification | [Mutable descriptors](../../../../vulkan-docs/src/chapters/descriptors.adoc#L593-L652) | Defines permitted lists, per-element active types, update changes, consumption, and undefined mismatch. |
| Mutable descriptor feature contract | [Mutable descriptor feature](../../../../vulkan-docs/src/chapters/features.adoc#L5552-L5605) | Defines the mandatory supported type combination and descriptor-indexing interactions. |
| Mutable list and pool specification | [Layout lists](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L179-L335), [pool lists](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L2249-L2280) | Defines list validity, binding association, pool subset rules, and omitted or out-of-range lists. |
| Descriptor indexing and update-after-bind specification | [Binding flags](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L620-L814), [features](../../../../vulkan-docs/src/chapters/features.adoc#L2078-L2135) | Defines per-type post-bind updates, partially-bound validity, and variable descriptor counts. |
| Descriptor indexing property | [`maxUpdateAfterBindDescriptorsInAllPools`](../../../../vulkan-docs/src/chapters/limits.adoc#L2523-L2531) | Bounds descriptors allocated across all update-after-bind pools. |
| Mutable copy and validity specification | [Copy rules](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L3927-L4046), [descriptor validity](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L4596-L4619) | Defines active-type transfer and the required shader-consumer match. |
| Shader resource-interface specification | [Set and binding assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1575-L1611), [shared declarations](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1694-L1715) | Defines descriptor decoration mapping and several variables sharing one binding. |
| Baseline shader target | [`getBaselineSpirvVersion()`](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052) | Establishes SPIR-V 1.0 for the representative compute shader. |
