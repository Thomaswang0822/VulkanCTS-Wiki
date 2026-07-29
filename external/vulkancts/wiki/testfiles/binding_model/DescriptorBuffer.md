## Overview

**Core question:** Can every registered descriptor-buffer layout, binding, residency mode, shader stage, and special descriptor contract produce the intended shader-visible resource access?

- [`vktBindingDescriptorBufferTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp) implements `binding_model.descriptor_buffer` as three residency intermediate nodes with a shared scenario matrix.
- The common path queries implementation-defined layout sizes and binding offsets, writes descriptor encodings into buffers, binds device addresses and per-set offsets, executes the selected shader stage, and checks a compact diagnostic result.
- The matrix covers ordinary descriptor types, multiple buffers and sets, binding limits, embedded immutable samplers, push descriptors, robustness, capture/replay, mutable descriptors, YCbCr conversion, graphics, compute, and ray tracing.
- Sparse binding and sparse residency change descriptor-buffer creation and memory binding. They do not change expected shader values or treat unbound descriptor bytes as readable data.
- Specialized host-side leaves check descriptor-buffer property limits, descriptor capture/replay consistency, and binding invalidation. Those checks remain distinct from the generated shader counter path.

## Background Knowledge

For the shared concepts of descriptor interfaces and availability and visibility, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Descriptor-buffer location.** Vulkan locates a descriptor array element at `bufferAddress + setOffset + bindingOffset + arrayElement * descriptorSize`. The application gets the layout size and binding offset from `vkGetDescriptorSetLayoutSizeEXT` and `vkGetDescriptorSetLayoutBindingOffsetEXT`, obtains opaque ordinary descriptor bytes with `vkGetDescriptorEXT`, then supplies the buffer address and set offset with descriptor-buffer binding commands ([descriptor memory layout](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L12-L122), [descriptor encoding](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L167-L206)).
- **Sparse descriptor storage.** `sparseBinding` permits sparse memory binding for buffers, and `sparseResidencyBuffer` permits partial residency ([sparse features](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L70-L130)). A shader access to descriptor data in an unbound region of a sparse partially resident buffer reads invalid descriptor data and has undefined behavior, so partial residency does not provide a zero-valued descriptor oracle ([unbound descriptor data](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L928-L939)).
- **Descriptor and resource visibility.** A device copy into descriptor memory needs a dependency whose destination access includes `VK_ACCESS_2_DESCRIPTOR_BUFFER_READ_BIT_EXT`; referenced image or buffer contents need their own resource dependency. Shader or transfer writes also need host visibility before readback ([descriptor update visibility](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L892-L940), [memory dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L110-L160)).
- **Stage interfaces.** A descriptor-set layout binding identifies the descriptor type, array count, and shader stages allowed to access it. Pipeline layouts connect those set layouts to shader resources ([layout bindings](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L469), [pipeline layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1169-L1182)). Graphics cases pass a `uvec4` diagnostic between stages through matching location 0 interfaces ([shader inputs and outputs](../../../../vulkan-docs/src/chapters/shaders.adoc#L2371-L2379)).

## Registration Hierarchy

```text
binding_model.descriptor_buffer
├── traditional_buffer
├── sparse_binding_buffer
└── sparse_residency_buffer
```

The source creates the `descriptor_buffer` test family and populates the three residency intermediate nodes with the same main scenario generator ([factory and residency registration](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7874-L7899)). The default Vulkan mustpass contains 5,432 leaves: 1,818 traditional, 1,807 sparse-binding, and 1,807 sparse-residency leaves ([`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L4718-L10149)). The Vulkan SC binding-model list has no `descriptor_buffer` leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Resource residency intermediate node | `traditional_buffer`, `sparse_binding_buffer`, `sparse_residency_buffer` | Selects ordinary `vkBindBufferMemory`, sparse full-range binding, or the sparse-residency allocation path. | [`ResourceResidency` and registration](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L216-L222), [`populateDescriptorBufferTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7874-L7892) |
| Scenario family intermediate node | `basic`, `single`, `multiple`, `max`, `embedded_imm_samplers`, `push_descriptor`, `push_template`, `robust`, `capture_replay`, `invalidation_rules`, `mutable_descriptor`, `ycbcr_sampler` | Selects the descriptor-buffer property or interaction contract. `invalidation_rules` is traditional-only. | [`populateDescriptorBufferTestGroup()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7174-L7872) |
| Shader stage | `vert`, `tesc`, `tese`, `geom`, `frag`, `comp`, `rgen`, `ahit`, `chit`, `miss`, `sect`, `call` | Places the generated descriptor access in a graphics, compute, or ray-tracing stage. | [stage choices](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7181-L7199) |
| Queue | `graphics`, `compute` | Uses a graphics-capable queue or a compute queue. Compute-only queues are paired only with `comp`. | [queue choices](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7181-L7184), [single registration](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7240-L7251) |
| Descriptor type | combined image sampler, sampled image, storage image, uniform/storage texel buffer, uniform/storage buffer, input attachment, inline uniform block, acceleration structure; sampler through image pairing | Changes encoding size, resource creation, GLSL declaration, access operation, and support gates. Dynamic buffer descriptor types are excluded because descriptor buffers do not allow them. | [single descriptor choices](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7216-L7230), [`glslDeclareBinding()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L910-L1011) |
| Descriptor-buffer and set shape | buffer counts `1`, `2`, `3`, `8`, `16`, `32`; sets per buffer `1`, `3`, `4`; arrays of `1` to `3` elements | Exercises multiple binding addresses, multiple set offsets in one buffer, binding offsets, and descriptor array stride. Exact legal values depend on the scenario. | [`multiple` options](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7283-L7343), [generated arrays](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1651-L1731) |
| Separate sampler/resource counts | `(1,1)`, `(2,2)`, `(4,4)`, `(8,8)`, `(16,16)`, `(1,7)`, `(1,15)`, `(1,31)`, `(7,1)`, `(15,1)`, `(31,1)` | Stresses separate sampler-only and resource-only descriptor buffers up to reported binding limits. | [`max` options](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7348-L7399) |
| Command and address forms | ordinary commands, `_commands_2`, `compute_maintenance5`, `non_buffer_aligned` | Selects legacy or `VK_KHR_maintenance6` structure-based commands, flags2 pipeline creation, or a buffer address shifted by `descriptorBufferOffsetAlignment` with a compensating set offset. | [case-name suffixes](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L767-L827), [address compensation](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3763-L3808) |
| Deterministic data | `--deqp-base-seed` plus scenario and case-name hashes | Determines generated binding order, array counts, resource values, and shader literals while retaining reproducible names. The command-line default seed is `0`. | [hash and expected data](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L767-L860), [base seed](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7174-L7219), [CLI default](../../../../../framework/common/tcuCommandLine.cpp#L233-L241) |
| Default mustpass population | 5,432 Vulkan leaves; none in Vulkan SC | Confirms current registered coverage rather than defining semantics. | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L4718-L10149), [Vulkan SC binding-model list](../../../mustpass/main/vksc-default/binding-model.txt) |

The three residency populations are almost parallel. Traditional mode has eleven additional leaves: three `invalidation_rules` leaves and eight capture/replay descriptor-data consistency leaves. This difference reflects specialized host-side tests, not broader shader-stage coverage.

## Behavior Parameters

Two axes materially change behavior. Resource residency changes how descriptor-buffer storage becomes resident. The scenario family changes the property being checked inside each residency intermediate node.

Resource-residency axis:

### `traditional_buffer`: Ordinary memory binding

The host creates each descriptor buffer without sparse flags and binds one allocation with `vkBindBufferMemory`. Only this mode registers binding invalidation and descriptor-data consistency leaves because those contracts do not require sparse descriptor storage.

### `sparse_binding_buffer`: Sparse buffer with a bound descriptor range

The host creates descriptor buffers with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT`, selects a sparse-capable queue, submits one `VkSparseMemoryBind` covering the descriptor buffer's memory requirement, and waits for the sparse-bind fence before obtaining and using the device address.

### `sparse_residency_buffer`: Sparse-residency allocation path

This mode requires both `sparseBinding` and `sparseResidencyBuffer`. When direct host-visible device-local memory is available, the allocation is enlarged by one alignment unit so the reported descriptor-buffer range can be sparsely bound. The shader still accesses descriptors within the bound range; the mode does not assign meaning to unbound descriptor bytes.

Scenario-family axis:

### `basic`: Property-limit checks

Each `limits` leaf compares reported descriptor-buffer properties with required minima, maxima, nonzero conditions, and alignment rules. It is an API property test, not a generated resource-access case.

### `single`: One target descriptor and required helpers

A single case creates one descriptor type at set 0, binding 0. Sampled images add a sampler, compute and ray-tracing paths add a result storage buffer, and ray-tracing paths add their service acceleration structure. These leaves isolate type encoding, binding offset, stage access, and readback.

### `multiple`: Packed sets, arrays, and descriptor types

The generator creates one or more sets per descriptor buffer, shuffles supported descriptor types, and assigns one to three array elements. Smaller multi-set layouts also have immutable-sampler variants. These cases combine address binding, aligned per-set packing, binding offsets, array strides, and several descriptor representations.

### `max`: Separate sampler and resource bindings

Sampler-only sets and sampled-image sets each receive their own descriptor-buffer binding. The shader pairs images and samplers and accesses every binding at least once, testing separate sampler and resource binding limits and usage flags.

### `embedded_imm_samplers`: Embedded sampler sets

Sampler-only layouts use `VK_DESCRIPTOR_SET_LAYOUT_CREATE_EMBEDDED_IMMUTABLE_SAMPLERS_BIT_EXT` and the corresponding binding command rather than storing sampler payloads in a descriptor buffer. A final sampled-image set provides resources used with those samplers.

### `push_descriptor`: Pushed and buffered sets together

One selected set is updated with push descriptors while the remaining sets use descriptor buffers. Cases vary the push-set index, set count, single-buffer arrangement, and ordinary versus maintenance6 command form.

### `push_template`: Template-based pushed set

This family keeps the mixed pushed/buffered layout but packs host update data according to a descriptor update template and records a push-with-template command. It tests template offsets and strides in addition to mixed set binding.

### `robust`: Out-of-bounds, null-data, and null-size behavior

`buffer_access` reads both in-range and out-of-range locations from zero-filled buffer resources and expects zero. `null_descriptor` encodes a selected null resource and expects zero-valued reads. `null_descriptor_size` calls `textureSize()` or `imageSize()` on a null texel buffer and expects zero.

### `capture_replay`: Opaque data and replayed resources

Generated cases obtain opaque capture data for a chosen resource class, recreate that resource for replay, regenerate the descriptor, require byte-for-byte descriptor equality, and execute the same shader-visible access. Custom-border-color variants and separate image/buffer descriptor-data consistency leaves extend the host-side checks.

### `invalidation_rules`: Legacy and descriptor-buffer binding transitions

The three traditional-only leaves switch from descriptor buffers to legacy sets, from legacy sets to descriptor buffers, or bind a descriptor buffer while using legacy descriptors. Their oracle targets binding invalidation and preservation under pipeline-layout compatibility, rather than the ordinary generated counter matrix.

### `mutable_descriptor`: Mutable layout, concrete runtime type

Selected bindings use `VK_DESCRIPTOR_TYPE_MUTABLE_EXT` in the layout. The test checks layout support, allocates each mutable slot using the maximum size of its allowed concrete types, writes one concrete descriptor encoding, and reads it through the matching shader declaration.

### `ycbcr_sampler`: Multiplanar combined image samplers

Two-plane and three-plane formats, scalar and two-element array forms, exercise the implementation-reported combined image sampler descriptor count and sampler conversion. The shader samples converted colors and compares channels with a `0.005` tolerance.

## Shader Analysis

The compute storage-buffer walkthrough shows the shared generated-shader contract: implementation-matched set and binding declarations, deterministic resource values, diagnostic fields, and storage-buffer readback. Sparse modes use the same shader logic. Other stages change result transport or add service shaders; robustness, acceleration-structure, and YCbCr scenarios change the type-specific access described below.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.descriptor_buffer.traditional_buffer.single.compute_comp_storage_buffer
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `traditional_buffer` | The descriptor buffer uses ordinary memory binding. |
| `single` and `storage_buffer` | Set 0 binding 0 is the target resource; binding 1 is the compute diagnostic buffer. |
| `compute_comp` | A compute queue and compute shader execute one workgroup. |
| default base seed `0` | Case-name hashing produces `0xaa2367fa`, the base resource value embedded as `2854447098u`. |

#### Purpose

The shader verifies that descriptor bytes at set 0 binding 0 resolve to the initialized storage buffer. It samples four indices across all 4,096 elements, counts exact matches, and writes count plus mismatch coordinates through a second descriptor in the same descriptor buffer.

#### Structural Design

| Phase | Shader operation | Diagnostic effect |
|-------|------------------|-------------------|
| Initialize | Clear local `uvec4 result`. | Count and coordinates start at zero. |
| Sample resource | Read indices `0`, `1365`, `2730`, and `4095` from `res_0_0`. | Spans the start, interior, and final element. |
| Compare | Require `value == 2854447098u + i`. | Each match increments `result.x`; a mismatch records binding and index data. |
| Return | Store all four result words through `res_0_1`. | Host expects the first word to equal `4`. |

#### Shader Code

```glsl
#version 460
#extension GL_EXT_debug_printf : enable
/// Binding 0 is the descriptor-buffer-backed storage resource under test. Its 4096 uint values follow the case-specific sequence.
layout(set = 0, binding = 0) buffer Buffer_0_0 {
    uint data[4096];
} res_0_0;
/// Binding 1 is a four-word storage buffer used only to return the pass count and mismatch coordinates to the host.
layout(set = 0, binding = 1) buffer Buffer_0_1 {
    uint data[4];
} res_0_1;

layout(local_size_x = 1) in;

void main (void) {
    uvec4 result = uvec4(0);

    /// Check four indices spanning the resource. Each successful comparison increments result.x; a mismatch stores its binding and index.
    for (uint i = 0; i < 4096u; i += 1365u) {
        uint value = res_0_0.data[i];
        if (value == (2854447098u + i)) {
            result.x += 1;
        } else if (result.y == 0) {
            result.y = 0u;
            result.z = i;
        }
    }
    res_0_1.data[0] = result.x;
    res_0_1.data[1] = result.y;
    res_0_1.data[2] = result.z;
    res_0_1.data[3] = result.w;
}
```

#### Additional Info

- `single` hashes the exact case suffix with the scenario hash. With the default base seed, `deStringHash("single") ^ deStringHash("compute_comp_storage_buffer")` is `0xaa2367fa` ([case hashing](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L767-L827), [`deStringHash()`](../../../../../framework/delibs/debase/deString.c#L34-L52)).
- The generator declares 4,096 `uint` elements because `ConstUniformBufferDwords` is `0x1000`. `ConstChecksPerBuffer` limits validation to four comparisons ([constants](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L70-L79), [loop generation](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1337-L1346)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Descriptor type | Declarations and accesses become texture sampling, image load, texel fetch/load, uniform `uvec4` loads, subpass load, inline-uniform loads, or ray queries. | [`glslDeclareBinding()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L910-L1011), [`glslOutputVerification()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1120-L1524) |
| Scenario family | Robustness expects zeros or zero size; `max` combines separate images and samplers; embedded samplers use explicit sampler/image constructors; YCbCr compares converted float channels. | [verification branches](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1120-L1524) |
| Shader stage | Graphics carries the `uvec4` through location 0 and writes four `R32_UINT` pixels; compute writes a storage buffer; ray-tracing stages write a result buffer and use service shaders and shader binding tables. | [`initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1889-L2349) |
| Resource residency | No shader change. Traditional and sparse modes change host buffer creation and memory binding before the same shader access. | [`createDescriptorBuffers()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3441-L3716) |
| Generated layout | More sets, shuffled binding types, and array counts add declarations and checks with exact set, binding, and array coordinates. | [`delayedInit()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1568-L1887) |

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
; Bound: 82
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main"
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 460
               OpSourceExtension "GL_EXT_debug_printf"
               OpName %main "main"
               OpName %result "result"
               OpName %i "i"
               OpName %value "value"
               OpName %Buffer_0_0 "Buffer_0_0"
               OpMemberName %Buffer_0_0 0 "data"
               OpName %res_0_0 "res_0_0"
               OpName %Buffer_0_1 "Buffer_0_1"
               OpMemberName %Buffer_0_1 0 "data"
               OpName %res_0_1 "res_0_1"
               OpDecorate %_arr_uint_uint_4096 ArrayStride 4
               OpDecorate %Buffer_0_0 BufferBlock
               OpMemberDecorate %Buffer_0_0 0 Offset 0
               OpDecorate %res_0_0 Binding 0
               OpDecorate %res_0_0 DescriptorSet 0
               OpDecorate %_arr_uint_uint_4 ArrayStride 4
               OpDecorate %Buffer_0_1 BufferBlock
               OpMemberDecorate %Buffer_0_1 0 Offset 0
               OpDecorate %res_0_1 Binding 1
               OpDecorate %res_0_1 DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
     %uint_0 = OpConstant %uint 0
         %11 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
%_ptr_Function_uint = OpTypePointer Function %uint
  %uint_4096 = OpConstant %uint 4096
       %bool = OpTypeBool
%_arr_uint_uint_4096 = OpTypeArray %uint %uint_4096
 %Buffer_0_0 = OpTypeStruct %_arr_uint_uint_4096
%_ptr_Uniform_Buffer_0_0 = OpTypePointer Uniform %Buffer_0_0
    %res_0_0 = OpVariable %_ptr_Uniform_Buffer_0_0 Uniform
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
%uint_2854447098 = OpConstant %uint 2854447098
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
  %uint_1365 = OpConstant %uint 1365
     %uint_4 = OpConstant %uint 4
%_arr_uint_uint_4 = OpTypeArray %uint %uint_4
 %Buffer_0_1 = OpTypeStruct %_arr_uint_uint_4
%_ptr_Uniform_Buffer_0_1 = OpTypePointer Uniform %Buffer_0_1
    %res_0_1 = OpVariable %_ptr_Uniform_Buffer_0_1 Uniform
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_3 = OpConstant %int 3
     %uint_3 = OpConstant %uint 3
     %v3uint = OpTypeVector %uint 3
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
     %result = OpVariable %_ptr_Function_v4uint Function
          %i = OpVariable %_ptr_Function_uint Function
      %value = OpVariable %_ptr_Function_uint Function
               OpStore %result %11
               OpStore %i %uint_0
               OpBranch %14
         %14 = OpLabel
               OpLoopMerge %16 %17 None
               OpBranch %18
         %18 = OpLabel
         %19 = OpLoad %uint %i
         %22 = OpULessThan %bool %19 %uint_4096
               OpBranchConditional %22 %15 %16
         %15 = OpLabel
         %30 = OpLoad %uint %i
         %32 = OpAccessChain %_ptr_Uniform_uint %res_0_0 %int_0 %30
         %33 = OpLoad %uint %32
               OpStore %value %33
         %34 = OpLoad %uint %value
         %36 = OpLoad %uint %i
         %37 = OpIAdd %uint %uint_2854447098 %36
         %38 = OpIEqual %bool %34 %37
               OpSelectionMerge %40 None
               OpBranchConditional %38 %39 %46
         %39 = OpLabel
         %42 = OpAccessChain %_ptr_Function_uint %result %uint_0
         %43 = OpLoad %uint %42
         %44 = OpIAdd %uint %43 %uint_1
         %45 = OpAccessChain %_ptr_Function_uint %result %uint_0
               OpStore %45 %44
               OpBranch %40
         %46 = OpLabel
         %47 = OpAccessChain %_ptr_Function_uint %result %uint_1
         %48 = OpLoad %uint %47
         %49 = OpIEqual %bool %48 %uint_0
               OpSelectionMerge %51 None
               OpBranchConditional %49 %50 %51
         %50 = OpLabel
         %52 = OpAccessChain %_ptr_Function_uint %result %uint_1
               OpStore %52 %uint_0
         %53 = OpLoad %uint %i
         %55 = OpAccessChain %_ptr_Function_uint %result %uint_2
               OpStore %55 %53
               OpBranch %51
         %51 = OpLabel
               OpBranch %40
         %40 = OpLabel
               OpBranch %17
         %17 = OpLabel
         %57 = OpLoad %uint %i
         %58 = OpIAdd %uint %57 %uint_1365
               OpStore %i %58
               OpBranch %14
         %16 = OpLabel
         %64 = OpAccessChain %_ptr_Function_uint %result %uint_0
         %65 = OpLoad %uint %64
         %66 = OpAccessChain %_ptr_Uniform_uint %res_0_1 %int_0 %int_0
               OpStore %66 %65
         %68 = OpAccessChain %_ptr_Function_uint %result %uint_1
         %69 = OpLoad %uint %68
         %70 = OpAccessChain %_ptr_Uniform_uint %res_0_1 %int_0 %int_1
               OpStore %70 %69
         %72 = OpAccessChain %_ptr_Function_uint %result %uint_2
         %73 = OpLoad %uint %72
         %74 = OpAccessChain %_ptr_Uniform_uint %res_0_1 %int_0 %int_2
               OpStore %74 %73
         %77 = OpAccessChain %_ptr_Function_uint %result %uint_3
         %78 = OpLoad %uint %77
         %79 = OpAccessChain %_ptr_Uniform_uint %res_0_1 %int_0 %int_3
               OpStore %79 %78
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Common generated resource-access path

- `DescriptorBufferTestCase::delayedInit()` expands registered parameters into `SimpleBinding` records. It creates helper samplers, result buffers, and service acceleration structures only when the selected descriptor or stage needs them.
- `checkSupport()` requires `VK_EXT_descriptor_buffer`, buffer device address, synchronization2, descriptor indexing, and maintenance4. It applies sparse features, stage features, descriptor-buffer binding limits, robustness, inline-uniform, push-descriptor, mutable-descriptor, YCbCr, maintenance5/6, acceleration-structure, ray-query, and ray-tracing gates as needed.
- The test creates descriptor-set layouts with `VK_DESCRIPTOR_SET_LAYOUT_CREATE_DESCRIPTOR_BUFFER_BIT_EXT`. It queries each layout's byte size and every binding's byte offset. Set regions in a descriptor buffer are rounded up to `descriptorBufferOffsetAlignment`.
- Each descriptor buffer uses `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` plus sampler, resource, transfer-destination, or push-descriptor usage as required. Traditional mode calls `vkBindBufferMemory`. Both sparse modes create a sparse buffer, submit `vkQueueBindSparse`, and wait for its fence before loading the device address ([buffer creation and sparse binding](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3441-L3716)).
- The host creates the resource behind each descriptor. It fills buffers, texel buffers, and images with case-specific values; creates sampler state and image layouts; or builds acceleration structures. `initializeBinding()` calls `vkGetDescriptorEXT` for ordinary descriptors and writes inline uniform words directly. Destination address calculation combines the set's buffer offset, implementation-reported binding offset, and descriptor-size array stride ([descriptor placement](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L4872-L4950)).
- At command recording, `vkCmdBindDescriptorBuffersEXT` receives each buffer's device address and usage. `vkCmdSetDescriptorBufferOffsetsEXT`, or its maintenance6 form, maps each set to a bound-buffer index and offset. The `non_buffer_aligned` leaf adds one alignment unit to the bound address and subtracts it from set offsets so the final descriptor location remains unchanged ([runtime binding](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3718-L3844)).
- If descriptor bytes live in a staging buffer, the command buffer copies each layout region and uses a transfer-write to descriptor-buffer-read dependency. Image uploads have separate layout transitions and transfer-write to shader-read dependencies ([staged upload](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L5581-L5619), [image upload](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L5623-L5757)).
- Compute dispatches `1 x 1 x 1`; ray tracing traces `1 x 1 x 1`; graphics draws six vertices over a `4 x 2` `R32_UINT` attachment. Compute and ray tracing make shader writes host-visible. Graphics copies the result image into a host-visible buffer and makes transfer writes host-visible.
- For compute and ray tracing, the host invalidates the result-buffer allocation before reading it. Graphics reads the copied color-buffer values. The host computes the expected success count from every tested descriptor and array element. Exact equality returns `Pass`; a mismatch reports expected and actual count plus the decoded set, binding, and array or buffer index ([host oracle](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L5889-L5995)).

### Specialized paths

- `basic.limits` compares descriptor-buffer properties directly and does not create the common generated pipeline ([`testLimits()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L6003-L6115)).
- Capture/replay generated cases run `iterate()` twice. The capture iteration saves opaque data. The replay iteration recreates selected resources, regenerates descriptor bytes, compares the bytes, and repeats shader access. Additional traditional-only capture/replay leaves compare descriptor payload and usage data for image and buffer objects.
- `invalidation_rules` owns a separate pipeline-layout and binding sequence. A failure there concerns switching or mixing legacy descriptor sets and descriptor-buffer bindings, not descriptor encoding through `vkGetDescriptorEXT`.
- Robustness uses the same count transport but different expected shader values. YCbCr uses float-channel comparisons with `0.005` tolerance rather than exact `uint` equality.

## Failure Meaning

A failed leaf identifies the selected residency and scenario contract, but the final counter or image alone does not prove whether descriptor placement, descriptor decoding, referenced resource access, shader execution, synchronization, or readback caused the mismatch. The exact path and diagnostic coordinates narrow the next investigation.

### Failure Cause Mapping

Resource-residency axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `traditional_buffer` | Traditional buffer memory binding, descriptor address/offset selection, descriptor encoding, resource access, synchronization, or readback failure. |
| `sparse_binding_buffer` | Sparse queue selection or binding failure, sparse descriptor-buffer address/range handling failure, or a shared descriptor encoding, resource access, synchronization, or readback failure. |
| `sparse_residency_buffer` | Sparse-residency feature or allocation-range handling failure, sparse descriptor-buffer address/range handling failure, or a shared descriptor encoding, resource access, synchronization, or readback failure. |

Scenario-family axis:

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Descriptor-buffer property reporting outside the extension's required limits. |
| `single` | Type-specific descriptor encoding, layout offset, shader-stage access, resource initialization, or result transport failure. |
| `multiple` | Multi-buffer or multi-set packing, array stride, immutable-sampler layout, binding-index selection, or broad descriptor-type interaction failure. |
| `max` | Sampler/resource binding-limit handling or separate sampler and resource descriptor-buffer usage failure. |
| `embedded_imm_samplers` | Embedded immutable sampler layout or binding command failure, or incorrect pairing with sampled-image descriptors. |
| `push_descriptor` | Coexistence of descriptor-buffer sets and directly pushed descriptors, push-buffer handle, set selection, or maintenance6 command failure. |
| `push_template` | Descriptor update-template packing or push-template execution failure while descriptor-buffer sets remain bound. |
| `robust` | Robust descriptor size selection, out-of-bounds zeroing, null-descriptor encoding, or null texel-buffer size-query failure. |
| `capture_replay` | Opaque capture-data retrieval, replay object creation, byte-for-byte descriptor reproduction, custom-border-color interaction, or replayed resource access failure. |
| `invalidation_rules` | Incorrect invalidation or preservation when switching between legacy descriptor sets and descriptor-buffer bindings under pipeline-layout compatibility rules. |
| `mutable_descriptor` | Mutable descriptor layout support, maximum descriptor-size allocation, concrete-type encoding, or runtime access failure. |
| `ycbcr_sampler` | Multiplanar descriptor count/layout, combined-image-sampler array placement, YCbCr conversion, or sampled-value comparison failure. |

### Cause Analysis

#### Traditional buffer memory binding or shared descriptor-access path failure

**Possible failure symptoms:** A traditional leaf returns an API error, reports a short comparison count, identifies a wrong set/binding/index, reports mismatched replay descriptor bytes, or produces wrong `R32_UINT` result pixels.

**Possible implementation causes:** The implementation may return an incorrect layout size or binding offset, encode the wrong descriptor bytes, apply the wrong device address or set offset, expose incorrect referenced resource contents, miss a required availability or visibility operation, or corrupt result copyback. Vulkan defines each descriptor location from independent address and offset terms, so the exact failing scenario and coordinates are needed to isolate the term.

#### Sparse queue, binding, allocation-range, or shared descriptor-access path failure

**Possible failure symptoms:** One or both sparse residency intermediate nodes fail sparse queue or memory binding, or their otherwise matching leaves report a short count or wrong result while traditional mode passes. A failure shared with traditional mode points away from sparse setup and toward common descriptor or execution behavior.

**Possible implementation causes:** The sparse path may select an unsuitable queue, mishandle `vkQueueBindSparse` completion, associate the device address with the wrong sparse memory range, or mishandle the extra allocation range used by sparse residency. If all three modes fail the same leaf, descriptor encoding, resource access, synchronization, shader execution, or readback is a stronger source-grounded candidate than sparse binding alone.

#### Descriptor-buffer property reporting outside required limits

**Possible failure symptoms:** `basic.limits` throws a `TestError` naming a property that is zero, below its required minimum, above its required maximum, or not a permitted power-of-two alignment.

**Possible implementation causes:** `VkPhysicalDeviceDescriptorBufferPropertiesEXT` may report a value that violates the extension's property requirements. This path checks reported properties directly, so no shader, descriptor payload, sparse bind, or copyback participates.

#### Type-specific descriptor encoding, placement, or resource observation failure

**Possible failure symptoms:** A `single` leaf reports fewer successes than expected and identifies its target set, binding, and element. The suffix identifies the descriptor type and stage; graphics uses result pixels, while compute and ray tracing use a result buffer.

**Possible implementation causes:** `vkGetDescriptorEXT` may encode the selected descriptor incorrectly, the implementation may fetch it from the wrong binding offset or array stride, or the selected stage may observe the wrong buffer, image, sampler, input attachment, inline data, or acceleration structure. Resource initialization and result transport remain part of the observed path, so the counter alone cannot assign the fault more narrowly.

#### Multi-buffer, multi-set, binding-limit, or immutable-sampler failure

**Possible failure symptoms:** `multiple`, `max`, or `embedded_imm_samplers` fails only when more binding addresses, packed set offsets, array elements, sampler-only buffers, or embedded samplers are present. `max` diagnostics can identify both failed image and sampler bindings.

**Possible implementation causes:** The implementation may apply a set offset to the wrong bound-buffer index, align packed set regions incorrectly, use the wrong per-type array stride, count sampler/resource binding points incorrectly, or fail to bind embedded immutable samplers for the selected set and stage. Device-limit gates distinguish unsupported counts from an executed failure.

#### Push descriptor or push-template coexistence failure

**Possible failure symptoms:** A `push_descriptor` or `push_template` leaf fails only for a selected push-set index, single-buffer form, template form, or `_commands_2` suffix. The common oracle reports a short count and the failed buffered or pushed binding when available.

**Possible implementation causes:** Descriptor-buffer offsets may disturb the wrong sets, the push descriptor may target an incorrect set, a required push-descriptor buffer handle may be wrong, or template offsets and strides may decode host data incorrectly. Maintenance6 variants can also expose incorrect stage flags or structure-based command handling.

#### Robust descriptor and size-query failure

**Possible failure symptoms:** `buffer_access` observes nonzero data for a checked out-of-range access, `null_descriptor` observes nonzero resource data, or `null_descriptor_size` observes a nonzero texel-buffer size. The result count is lower than the host expectation.

**Possible implementation causes:** The implementation may use a non-robust descriptor size when robust access requires the robust property, encode or interpret a null descriptor incorrectly, fail robust zeroing for an out-of-range buffer access, or return a nonzero size for a null texel buffer. The exact robust intermediate node separates data access from size-query behavior.

#### Capture/replay data or replayed access failure

**Possible failure symptoms:** The test reports `Replayed descriptor differs from the captured descriptor`, fails opaque-data consistency, or passes the byte comparison but returns a short shader comparison count on replay. Custom-border-color cases can report a sampled border mismatch.

**Possible implementation causes:** Opaque capture data may not recreate equivalent resource identity, replay-created buffers, images, samplers, or acceleration structures may produce different descriptor bytes, or equivalent descriptor bytes may resolve to the wrong replayed resource. A byte-comparison failure is earlier than shader access; a later counter failure includes replayed resource use and readback.

#### Legacy/descriptor-buffer invalidation failure

**Possible failure symptoms:** One of the three `invalidation_rules` leaves observes a binding that should have been invalidated, loses a binding that should remain usable, or reports a wrong result after switching binding models.

**Possible implementation causes:** Command-buffer binding state may fail to invalidate legacy sets after setting descriptor-buffer offsets, fail the inverse transition, or disturb sets under the wrong pipeline-layout compatibility scope. The specification states that these binding models cannot exist simultaneously at the same set binding point and defines the invalidation relationship ([binding interaction](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L661-L677), [set-offset invalidation](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L878-L890)).

#### Mutable descriptor layout or concrete-type failure

**Possible failure symptoms:** Layout support returns false, layout creation fails, or a `mutable_descriptor` leaf reports a wrong value for one of the concrete descriptor types selected by its type mask.

**Possible implementation causes:** The implementation may reject a supported mutable type list, allocate an insufficient mutable descriptor slot, report an incompatible binding offset, encode the concrete runtime type incorrectly, or decode the slot using the wrong allowed type. The test uses the maximum size among allowed concrete types for each mutable binding.

#### YCbCr descriptor layout or conversion failure

**Possible failure symptoms:** A `ycbcr_sampler` leaf samples channels outside the `0.005` tolerance. Failures may appear only for two-plane, three-plane, array, or a particular stage form.

**Possible implementation causes:** The implementation may report or place the wrong number of combined-image-sampler descriptors, mishandle the array layout, associate the wrong sampler conversion with an image view, or produce incorrect multiplanar sampling. Image upload, plane layout transitions, expected conversion, and result transport are also part of the observed path.

## Case Pruning

### Requirement-based pruning

- All generated cases require `VK_EXT_descriptor_buffer`, the `descriptorBuffer` feature, buffer device address, synchronization2, descriptor indexing, maintenance4, and a compatible execution queue ([common support gates](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L2351-L2410)).
- Sparse-binding cases require `sparseBinding`; sparse-residency cases also require `sparseResidencyBuffer` and a sparse-capable queue. A missing feature or queue produces `NotSupported`, not a failed descriptor comparison ([sparse support](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L2384-L2396), [queue selection](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L2893-L2952)).
- Tessellation, geometry, ray query, acceleration structure, ray-tracing pipeline, inline uniform block, push descriptor, descriptor-buffer push descriptor, robustness2 null descriptor, mutable descriptor, YCbCr conversion, maintenance5, and maintenance6 gates apply only to cases that request them.
- The source checks `maxBoundDescriptorSets`, descriptor-buffer binding limits, per-stage descriptor limits, inline-uniform limits, and mutable layout support. Counts above device limits are skipped as unsupported ([parameter limits](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L2435-L2564), [per-stage counts](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L2828-L2890)).
- Input attachments run only in fragment shaders. YCbCr cases query format properties and use the implementation-reported `combinedImageSamplerDescriptorCount`.
- Vulkan SC does not register this family.

### Design-based pruning

- Compute queues are paired only with the compute stage. Graphics queues cover graphics stages, ray-tracing stages, and registered compute cases.
- Dynamic buffer descriptor types are absent because descriptor-buffer layouts do not allow them. Standalone sampler behavior is normally observed by pairing the sampler with a sampled image.
- `multiple` retains 16- and 32-buffer cases only for vertex, fragment, and compute to limit long-running combinations. `max` removes counts above 15 for ray-tracing stages.
- Input attachments are removed from non-fragment matrices. Optional acceleration structures in broad matrix scenarios become storage buffers when ray query is unavailable, while a leaf that names acceleration structure requires the feature.
- `invalidation_rules` and eight descriptor-data consistency leaves are traditional-only because they test binding-model transitions or capture-data consistency rather than repeating sparse descriptor storage.
- `non_buffer_aligned` is one focused single-descriptor case. It shifts the bound address and compensates the set offset instead of multiplying this address test across every descriptor type and stage.

Requirement-based pruning says a requested legal path cannot run on the current build or device. Design-based pruning keeps the registered matrix finite and removes combinations that are invalid, redundant, or outside a specialized scenario's purpose.

## Key Takeaways

- Descriptor correctness depends on four placement terms: bound device address, per-set offset, implementation-reported binding offset, and per-type array stride. The test makes each term observable through real shader resource access.
- Traditional, sparse-binding, and sparse-residency modes share the descriptor and shader oracle but use different memory binding paths. Sparse residency never relies on reading descriptor bytes from an unbound region.
- Scenario families preserve distinct contracts: property reporting, ordinary type access, packed layouts, binding limits, embedded samplers, pushed sets, robustness, capture/replay, binding invalidation, mutable types, and YCbCr conversion.
- Graphics, compute, and ray-tracing stages carry the same compact success and coordinate record through different output paths. A failed count narrows the binding and scenario but does not assign the fault to descriptor state, resource access, synchronization, shader execution, or readback.
- The default Vulkan mustpass has 5,432 leaves. Device features and limits prune unsupported leaves before execution; source-side design rules prune invalid or redundant combinations during registration.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Descriptor-buffer family factory | [`createDescriptorBufferTests()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7874-L7899) | Registers the family and its three residency intermediate nodes. |
| Scenario registration | [`populateDescriptorBufferTestGroup()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L7174-L7872) | Defines scenario families, exact values, and design pruning. |
| Parameters and binding model | [`TestParams` and `SimpleBinding`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L187-L236) | Defines residency, stage, queue, descriptor, and layout dimensions. |
| Deterministic names and data | [`getCaseNameUpdateHash()` through `getExpectedData()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L767-L860) | Connects registered suffixes to reproducible resource values. |
| Generated GLSL | [`glslDeclareBinding()` through `glslOutputVerification()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L910-L1540) | Emits descriptor interfaces, type-specific reads, and diagnostic writes. |
| Binding expansion | [`DescriptorBufferTestCase::delayedInit()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1568-L1887) | Creates concrete set, binding, array, and helper-resource records. |
| Shader programs | [`DescriptorBufferTestCase::initPrograms()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L1889-L2349) | Builds graphics, compute, and ray-tracing sources. |
| Feature and limit gates | [`DescriptorBufferTestCase::checkSupport()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L2351-L2586) | Prunes unsupported descriptor, stage, sparse, robustness, and extension paths. |
| Descriptor memory layout | [`createDescriptorSetLayouts()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3355-L3439) | Creates descriptor-buffer layouts and queries sizes and binding offsets. |
| Traditional and sparse storage | [`createDescriptorBuffers()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3441-L3716) | Packs sets, binds memory, handles sparse submission, and selects direct or staged writes. |
| Runtime address and offset binding | [`bindDescriptorBuffers()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L3718-L3844) | Binds addresses, usage, embedded samplers, buffer indices, and set offsets. |
| Resource and descriptor initialization | [`initializeBinding()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L4310-L4994) | Creates backing resources and writes opaque or inline descriptor data. |
| Execution and result checking | [`DescriptorBufferTestInstance::iterate()`](../../../modules/vulkan/binding_model/vktBindingDescriptorBufferTests.cpp#L5208-L5995) | Uploads, synchronizes, executes, reads back, and applies the count oracle. |
| Default mustpass evidence | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L4718-L10149) | Confirms 5,432 Vulkan leaves and exact residency populations. |
| Descriptor-buffer specification | [Descriptor Buffers](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L4-L251), [Binding Descriptor Buffers](../../../../vulkan-docs/src/chapters/descriptorbuffers.adoc#L661-L940) | Defines descriptor encoding, location, address binding, set offsets, update visibility, and sparse access limits. |
| Sparse-memory specification | [Sparse Resource Features](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L70-L130), [`vkQueueBindSparse`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L1691-L1730) | Defines sparse feature tiers and sparse queue submission. |
| Descriptor and resource semantics | [Descriptor Types](../../../../vulkan-docs/src/chapters/descriptors.adoc#L46-L91), [Sampled Image](../../../../vulkan-docs/src/chapters/descriptors.adoc#L203-L223), [Storage Buffer](../../../../vulkan-docs/src/chapters/descriptors.adoc#L377-L414) | Defines resource classes represented by encoded descriptors. |
| Synchronization semantics | [Memory Dependencies](../../../../vulkan-docs/src/chapters/synchronization.adoc#L110-L160), [`VK_ACCESS_2_DESCRIPTOR_BUFFER_READ_BIT_EXT`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L1277-L1281) | Defines availability, visibility, and descriptor-buffer read access. |
| Shader resource interface | [`VkDescriptorSetLayoutBinding`](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L435-L469), [Pipeline Layouts](../../../../vulkan-docs/src/chapters/descriptorsets.adoc#L1169-L1182), [Shader Inputs and Outputs](../../../../vulkan-docs/src/chapters/shaders.adoc#L2371-L2379) | Connects descriptor bindings and result transport to shader stages. |
| SPIR-V target selection | [`getBaselineSpirvVersion()`](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052) | Establishes SPIR-V 1.0 for the representative compute shader. |
