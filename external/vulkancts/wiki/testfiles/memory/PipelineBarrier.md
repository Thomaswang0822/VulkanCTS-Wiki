## Overview

**Core question:** Do pipeline barriers and host cache operations make each write visible to the next legal consumer across the tested memory types and resource views?

- This page covers the `memory.pipeline_barrier` test family implemented by `vktMemoryPipelineBarrierTests.cpp`.
- The family generates deterministic randomized command sequences over one memory allocation, using host accesses, transfer commands, vertex/index fetch, shader resources, and image layouts.
- A software state model chooses legal operations and tracks expected data. Command-specific checks compare mapped bytes, copied bytes, or rendered pixels with that model.
- Registered usage pairs isolate domain and consumer transitions. `all` and `all_device` mix the supported registered usages in longer sequences.

## Background Knowledge

For the shared concepts memory dependencies and host-visible and non-coherent memory, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- **Image layout transition:** an image memory barrier can change layout between the dependency's availability and visibility operations. The transition must match the image's next use.

## Registration Hierarchy

```text
memory.pipeline_barrier
├── host_read_host_write
├── host_write_transfer_src
├── host_write_vertex_buffer
├── host_write_index_buffer
├── host_write_uniform_buffer
├── host_write_uniform_texel_buffer
├── host_write_storage_buffer
├── host_write_storage_texel_buffer
├── host_write_storage_image
├── host_write_image_sampled
├── host_read_transfer_dst
├── transfer_src_transfer_dst
├── transfer_dst_vertex_buffer
├── transfer_dst_index_buffer
├── transfer_dst_uniform_buffer
├── transfer_dst_uniform_texel_buffer
├── transfer_dst_storage_buffer
├── transfer_dst_storage_texel_buffer
├── transfer_dst_storage_image
├── transfer_dst_image_sampled
├── all
└── all_device
```

The first 20 intermediate nodes are the Cartesian product of two write usages and ten read usages. Token order comes from `usageToName()`, not producer-before-consumer order. Thus `host_read_transfer_dst` represents transfer-destination writes and host reads.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Write usage | `host_write`, `transfer_dst` | Selects host-domain or transfer-stage production for each pair group. | [`writeUsages`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L10144) |
| Read usage | `host_read`, `transfer_src`, `vertex_buffer`, `index_buffer`, `uniform_buffer`, `uniform_texel_buffer`, `storage_buffer`, `storage_texel_buffer`, `storage_image`, `image_sampled` | Selects the destination domain, pipeline stage, access type, and verification command. | [`readUsages`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L10139-L10142) |
| Combined usage | `all`, `all_device` | Mixes all twelve registered usages, with host usages removed from `all_device`. | [`all` registration](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L10194-L10247) |
| Allocation size | `1024`, `8192`, `65536`, `1048576` bytes | Changes allocation pressure and the amount of reference data. | [`sizes`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L10129-L10134) |
| Vertex stride | `2`, `4` | Changes vertex-input byte interpretation. It appears on vertex-buffer pair groups and both combined groups. | [`vertexStrides`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L10146-L10149) |
| Memory type | Every compatible non-protected type; host groups require host visibility | Exercises the same registered leaf across supported memory properties. | [`createCommandsAndAllocateMemory()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9476-L9558) |
| Randomized workload | 5 iterations × 50 operations per memory type | Produces deterministic legal sequences rather than a fixed write-barrier-read triplet. | [`MemoryTestInstance` constructor](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9407-L9417) |

## Behavior Parameters

The primary behavioral axis is the **access-domain and consumer-mechanism group**. It groups registered usage-pair intermediate nodes by the handoff that the barrier must establish. Size and stride vary stress and interpretation but do not change this synchronization question.

### `host-to-host`: host write and host read

`host_read_host_write` keeps both accesses in the host domain. The sequence still exercises mapping state, flush/invalidate decisions, and host-stage memory dependencies while checking bytes against the reference model.

### `host-to-device`: host write to a device consumer

The nine `host_write_*` non-host readers cover transfer source, vertex/index input, uniform and storage buffers, texel buffers, storage images, and sampled images. Host-produced bytes must reach the destination stage and access type selected by the consumer.

### `device-to-host`: transfer write to host read

`host_read_transfer_dst` writes through transfer commands and later reads mapped memory. Queue completion, the host destination scope, and invalidation for non-coherent memory must expose the transfer result to the CPU.

### `device-to-device`: transfer write to a device consumer

The nine `transfer_dst_*` non-host readers cover transfer, vertex input, and shader reads. Barriers must make transfer writes available and visible to each selected access while image cases also maintain a legal layout.

### `all`: mixed host and device access

`all` enables the twelve usages in the registration array. Its generator may move between host and command-buffer work, create buffer or image views, and use global, buffer, or image barriers. It does not include indirect, attachment, or input-attachment enum values that registration omits.

### `all_device`: mixed device-only access

`all_device` removes `USAGE_HOST_READ` and `USAGE_HOST_WRITE` from `all`. It concentrates on transfer, vertex-input, shader-resource, barrier, and image-layout behavior without host-domain handoffs.

## Shader Analysis

Shaders are direct consumers in the uniform/storage buffer, texel-buffer, storage-image, and sampled-image groups. Vertex and index groups instead use fixed-function vertex input as the synchronization consumer; their shaders convert the fetched vertex attribute or resulting vertex index into a point position. Shaders do not implement synchronization. They translate shader-visible memory into point positions or color values so the host can compare rendered output with its reference model. One storage-buffer vertex shader is enough to show this role; the other generated programs change resource declaration and decoding rather than the barrier mechanism.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.memory.pipeline_barrier.host_write_storage_buffer.1024
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `host_write_storage_buffer` | Host writes must become visible to a vertex-stage storage-buffer read. |
| `1024` | The test allocates 1024 bytes and iterates all compatible host-visible memory types. |
| Vertex shader from `AddPrograms::init()` | The central shader consumer reads packed coordinates from binding 0 and turns them into points. |

#### Purpose

The vertex shader exposes the storage-buffer values observed after synchronization. Each invocation decodes one packed coordinate and writes it as `gl_Position`, allowing framebuffer verification to detect stale or incorrect data.

#### Structural Design

| Phase | Shader action | Observable role |
|-------|---------------|-----------------|
| Resource read | Load one `uvec4` from descriptor set 0, binding 0 | Samples the synchronized allocation through a storage-buffer view. |
| Packed-value decode | Select a 32-bit lane, then its low or high 16 bits | Recovers one encoded two-byte position. |
| Position output | Normalize two bytes and write `gl_Position` | Converts memory contents into a rendered point location. |

#### Shader Code

```glsl
#version 310 es
precision highp float;
/// Binding 0 exposes the tested memory as a read-only storage buffer.
readonly layout(set=0, binding=0) buffer Block
{
    highp uvec4 values[];
} block;
void main (void) {
    gl_PointSize = 1.0;
    /// Decode one packed 16-bit position component from the storage-buffer contents.
    highp uvec4 vecVal = block.values[gl_VertexIndex / 8];
    highp uint val;
    if (((gl_VertexIndex / 2) % 4 == 0))
        val = vecVal.x;
    else if (((gl_VertexIndex / 2) % 4 == 1))
        val = vecVal.y;
    else if (((gl_VertexIndex / 2) % 4 == 2))
        val = vecVal.z;
    else if (((gl_VertexIndex / 2) % 4 == 3))
        val = vecVal.w;
    if ((gl_VertexIndex % 2) == 0)
        val = val & 0xFFFFu;
    else
        val = val >> 16u;
    highp vec2 pos = vec2(val & 0xFFu, val >> 8u) / vec2(255.0);
    /// A visible point encodes the buffer value as a framebuffer position for host verification.
    gl_Position = vec4(1.998 * pos - vec2(0.999), 0.0, 1.0);
}
```

#### Additional Info

- The source adds this program whenever `USAGE_STORAGE_BUFFER` is enabled; the exact pair case also enables `USAGE_HOST_WRITE`.
- Descriptor and render-pass setup live in the storage-buffer render command classes. The shader itself contains no barrier instruction.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Read usage | Vertex/index input uses direct fixed-function fetch; uniform/storage buffers use blocks; texel buffers use `texelFetch` or `imageLoad`; image cases use `imageLoad` or `texelFetch` on 2D resources. | [`AddPrograms::init()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9672-L10105) |
| Shader stage | Shader-readable resources have vertex and fragment consumers. The fragment paths emit encoded colors rather than point positions. | [`AddPrograms::init()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9704-L10079) |
| Size | The runtime-sized storage block keeps the GLSL unchanged; host-side resource sizing and draw counts vary. | [`storage-buffer programs`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9789-L9860) |

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
; Bound: 117
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %gl_VertexIndex
               OpSource ESSL 310
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpName %_ ""
               OpName %vecVal "vecVal"
               OpName %Block "Block"
               OpMemberName %Block 0 "values"
               OpName %block "block"
               OpName %gl_VertexIndex "gl_VertexIndex"
               OpName %val "val"
               OpName %pos "pos"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpDecorate %_runtimearr_v4uint ArrayStride 16
               OpDecorate %Block BufferBlock
               OpMemberDecorate %Block 0 NonWritable
               OpMemberDecorate %Block 0 Offset 0
               OpDecorate %block NonWritable
               OpDecorate %block Binding 0
               OpDecorate %block DescriptorSet 0
               OpDecorate %gl_VertexIndex BuiltIn VertexIndex
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float %float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_1 = OpConstant %int 1
    %float_1 = OpConstant %float 1
%_ptr_Output_float = OpTypePointer Output %float
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
%_runtimearr_v4uint = OpTypeRuntimeArray %v4uint
      %Block = OpTypeStruct %_runtimearr_v4uint
%_ptr_Uniform_Block = OpTypePointer Uniform %Block
      %block = OpVariable %_ptr_Uniform_Block Uniform
      %int_0 = OpConstant %int 0
%_ptr_Input_int = OpTypePointer Input %int
%gl_VertexIndex = OpVariable %_ptr_Input_int Input
      %int_8 = OpConstant %int 8
%_ptr_Uniform_v4uint = OpTypePointer Uniform %v4uint
      %int_2 = OpConstant %int 2
      %int_4 = OpConstant %int 4
       %bool = OpTypeBool
%_ptr_Function_uint = OpTypePointer Function %uint
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
     %uint_2 = OpConstant %uint 2
      %int_3 = OpConstant %int 3
     %uint_3 = OpConstant %uint 3
 %uint_65535 = OpConstant %uint 65535
    %uint_16 = OpConstant %uint 16
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
   %uint_255 = OpConstant %uint 255
     %uint_8 = OpConstant %uint 8
  %float_255 = OpConstant %float 255
        %103 = OpConstantComposite %v2float %float_255 %float_255
%float_1_99800003 = OpConstant %float 1.99800003
%float_0_999000013 = OpConstant %float 0.999000013
        %109 = OpConstantComposite %v2float %float_0_999000013 %float_0_999000013
    %float_0 = OpConstant %float 0
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
     %vecVal = OpVariable %_ptr_Function_v4uint Function
        %val = OpVariable %_ptr_Function_uint Function
        %pos = OpVariable %_ptr_Function_v2float Function
         %15 = OpAccessChain %_ptr_Output_float %_ %int_1
               OpStore %15 %float_1
         %27 = OpLoad %int %gl_VertexIndex
         %29 = OpSDiv %int %27 %int_8
         %31 = OpAccessChain %_ptr_Uniform_v4uint %block %int_0 %29
         %32 = OpLoad %v4uint %31
               OpStore %vecVal %32
         %33 = OpLoad %int %gl_VertexIndex
         %35 = OpSDiv %int %33 %int_2
         %37 = OpSMod %int %35 %int_4
         %39 = OpIEqual %bool %37 %int_0
               OpSelectionMerge %41 None
               OpBranchConditional %39 %40 %47
         %40 = OpLabel
         %45 = OpAccessChain %_ptr_Function_uint %vecVal %uint_0
         %46 = OpLoad %uint %45
               OpStore %val %46
               OpBranch %41
         %47 = OpLabel
         %48 = OpLoad %int %gl_VertexIndex
         %49 = OpSDiv %int %48 %int_2
         %50 = OpSMod %int %49 %int_4
         %51 = OpIEqual %bool %50 %int_1
               OpSelectionMerge %53 None
               OpBranchConditional %51 %52 %57
         %52 = OpLabel
         %55 = OpAccessChain %_ptr_Function_uint %vecVal %uint_1
         %56 = OpLoad %uint %55
               OpStore %val %56
               OpBranch %53
         %57 = OpLabel
         %58 = OpLoad %int %gl_VertexIndex
         %59 = OpSDiv %int %58 %int_2
         %60 = OpSMod %int %59 %int_4
         %61 = OpIEqual %bool %60 %int_2
               OpSelectionMerge %63 None
               OpBranchConditional %61 %62 %67
         %62 = OpLabel
         %65 = OpAccessChain %_ptr_Function_uint %vecVal %uint_2
         %66 = OpLoad %uint %65
               OpStore %val %66
               OpBranch %63
         %67 = OpLabel
         %68 = OpLoad %int %gl_VertexIndex
         %69 = OpSDiv %int %68 %int_2
         %70 = OpSMod %int %69 %int_4
         %72 = OpIEqual %bool %70 %int_3
               OpSelectionMerge %74 None
               OpBranchConditional %72 %73 %74
         %73 = OpLabel
         %76 = OpAccessChain %_ptr_Function_uint %vecVal %uint_3
         %77 = OpLoad %uint %76
               OpStore %val %77
               OpBranch %74
         %74 = OpLabel
               OpBranch %63
         %63 = OpLabel
               OpBranch %53
         %53 = OpLabel
               OpBranch %41
         %41 = OpLabel
         %78 = OpLoad %int %gl_VertexIndex
         %79 = OpSMod %int %78 %int_2
         %80 = OpIEqual %bool %79 %int_0
               OpSelectionMerge %82 None
               OpBranchConditional %80 %81 %86
         %81 = OpLabel
         %83 = OpLoad %uint %val
         %85 = OpBitwiseAnd %uint %83 %uint_65535
               OpStore %val %85
               OpBranch %82
         %86 = OpLabel
         %87 = OpLoad %uint %val
         %89 = OpShiftRightLogical %uint %87 %uint_16
               OpStore %val %89
               OpBranch %82
         %82 = OpLabel
         %93 = OpLoad %uint %val
         %95 = OpBitwiseAnd %uint %93 %uint_255
         %96 = OpConvertUToF %float %95
         %97 = OpLoad %uint %val
         %99 = OpShiftRightLogical %uint %97 %uint_8
        %100 = OpConvertUToF %float %99
        %101 = OpCompositeConstruct %v2float %96 %100
        %104 = OpFDiv %v2float %101 %103
               OpStore %pos %104
        %106 = OpLoad %v2float %pos
        %107 = OpVectorTimesScalar %v2float %106 %float_1_99800003
        %110 = OpFSub %v2float %107 %109
        %112 = OpCompositeExtract %float %110 0
        %113 = OpCompositeExtract %float %110 1
        %114 = OpCompositeConstruct %v4float %112 %113 %float_0 %float_1
        %116 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %116 %114
               OpReturn
               OpFunctionEnd

```

</details>

## Runtime Execution and Result Checking

- `MemoryTestInstance` walks every physical-device memory type. It skips host-invisible types for host cases, protected types, and disabled AMD device-coherent types.
- For each usable type, five deterministic seeds generate 50 operations from a state machine. Available operations depend on mapping, resource binding, image layout, queue state, cache state, and which usages the leaf enables.
- Buffer and image resources bind to the selected allocation. Image support uses optimal-tiled `VK_FORMAT_R8G8B8A8_UNORM` images sized to fit that allocation and memory type.
- Barrier generation asks the cache model for pending source and destination scopes, masks some bits, removes access bits illegal for the chosen stages, and records a global, buffer, or image barrier. Layout-transition operations use image barriers with a supported next layout.
- Host commands map, write, read, flush, and invalidate. Device commands copy, draw, and submit primary or secondary command buffers. The sequence can use queue or device idle operations when required by its current state.
- After execution, `deviceWaitIdle` completes outstanding work. `verify()` visits every generated command. Read commands compare captured bytes or rendered/copied pixels with `VerifyContext`'s reference memory or image.
- A mismatch, or a preparation, execution, or verification exception, records failure. The case passes only after all supported memory types and iterations finish cleanly.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `host-to-host` | Host cache management or host-stage dependency does not preserve the expected bytes. |
| `host-to-device` | Host writes do not become available and visible to the selected transfer, vertex-input, or shader read. |
| `device-to-host` | Device transfer writes do not become visible to the host read after submission and invalidation. |
| `device-to-device` | Transfer writes do not become visible to the selected transfer, vertex-input, or shader read. |
| `all` | A mixed host/device command sequence fails in barrier scope, cache maintenance, image layout handling, or resource interpretation. |
| `all_device` | A device-only mixed command sequence fails in barrier scope, image layout handling, or resource interpretation. |

### Cause Analysis

#### Host cache management or host-stage dependency failure

**Possible failure symptoms:** a mapped read differs from the reference bytes, or a later device consumer observes values older than the host write.

**Possible implementation causes:** the implementation may mishandle host-stage access scopes or non-coherent flush/invalidate behavior. The Vulkan memory-dependency rules require the selected availability and visibility operations to connect the producer and consumer; the test generator supplies cache operations only when its state model requires them.

#### Transfer-to-host visibility failure

**Possible failure symptoms:** mapped bytes after a transfer write differ from the reference state.

**Possible implementation causes:** transfer writes may not become available to the host domain or visible to host reads under the recorded dependency, or mapped-memory invalidation may fail to expose the completed device write.

#### Device consumer visibility failure

**Possible failure symptoms:** transfer readback bytes, vertex/index-derived points, or shader-derived pixels differ from the reference data.

**Possible implementation causes:** the recorded source stage/access scope may fail to make a write available, or the destination stage/access scope may fail to make it visible to the fixed-function or shader consumer. A shader compiler or resource-view defect can produce the same observed mismatch, so the failing command and usage must guide investigation.

#### Image layout or image-view failure

**Possible failure symptoms:** storage/sampled-image rendering or image copyback differs from the expected pixels, or command execution reports an error around an image operation.

**Possible implementation causes:** the image layout transition may not occur between availability and visibility as required, or image binding, view, sampling, storage access, or copy interpretation may disagree with the specified `VK_FORMAT_R8G8B8A8_UNORM` resource.

#### Mixed-sequence state failure

**Possible failure symptoms:** only `all` or `all_device` fails, often at one logged command in a longer sequence, while isolated pair groups pass.

**Possible implementation causes:** interaction between valid barriers, resource lifetime changes, primary/secondary command-buffer submission, host/device handoffs, or repeated buffer/image aliasing may expose state that simpler pairs do not. The deterministic seed and command log identify the sequence for source-level investigation.

## Case Pruning

### Requirement-based pruning

- Host access groups skip memory types without `VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT`.
- Protected memory types are skipped because this test does not execute protected submissions.
- A type with `VK_MEMORY_PROPERTY_DEVICE_COHERENT_BIT_AMD` is skipped when `deviceCoherentMemory` is disabled.
- A memory type is skipped if none of its enabled non-host buffer or image usages can bind a supported resource.
- With `VK_KHR_portability_subset`, vertex stride must satisfy `minVertexInputBindingStrideAlignment`; otherwise the leaf reports not supported.

### Design-based pruning

- Registration uses only `HOST_WRITE` and `TRANSFER_DST` as pair-group producers and ten consumers as pair-group readers.
- `USAGE_INDIRECT_BUFFER`, `USAGE_COLOR_ATTACHMENT`, `USAGE_INPUT_ATTACHMENT`, and `USAGE_DEPTH_STENCIL_ATTACHMENT` are not in the registered `usages` array. Despite its name, `all` does not add them.
- Only vertex-buffer reader groups expand stride because stride changes that consumer's interpretation. Other pair groups use the default stride only.
- Resource support can reduce the operations generated for a memory type; the state machine never emits an operation that its current resource, mapping, layout, or dependency state cannot legally support.

## Key Takeaways

- These are deterministic randomized state-machine tests, not fixed three-command write-barrier-read tests.
- The pair groups identify producer/consumer handoffs; `all` and `all_device` stress interactions among the same registered usages.
- Shader programs provide observable consumers. The core property remains availability, visibility, execution order, host cache management, and image layout correctness.
- Each leaf runs across compatible memory types and compares every read result with a software reference model. See `## Failure Meaning` for how mismatches narrow the investigation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Usage names and Vulkan flags | [`usageToName()` through `usageToAccessFlags()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L305-L494) | Maps registered names to resource, stage, and access flags. |
| Cache-state dependency model | [`CacheState`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L7500-L7927) | Tracks execution completion, write availability, and access visibility. |
| Legal operation generation | [`State`, `getAvailableOps()`, and `applyOp()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L8024-L8870) | Defines legal randomized state transitions. |
| Barrier command construction | [`createCmdCommand()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L8918-L9053) | Constructs image transitions and global, buffer, and image barriers. |
| Sequence construction | [`createCommands()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9266-L9330) | Builds each deterministic 50-operation workload. |
| Runtime and verification | [`MemoryTestInstance`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9407-L9669) | Iterates memory types and workloads, then collects command results. |
| Shader builders | [`AddPrograms::init()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L9672-L10105) | Generates programs for shader-visible consumers. |
| Test family registration | [`createPipelineBarrierTests()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp#L10126-L10250) | Registers usage groups, sizes, and vertex strides. |
| Parent registration | [`createChildren()`](../../../modules/vulkan/memory/vktMemoryTests.cpp#L52-L78) | Registers `pipeline_barrier` under `memory` for Vulkan, not Vulkan SC. |
| Default mustpass inventory | [`memory.txt`](../../../mustpass/main/vk-default/memory.txt#L5607-L5710) | Lists the default registered leaves. |
| Vulkan synchronization semantics | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L114-L147) | Defines availability, visibility, and memory dependencies. |
| Pipeline barrier specification | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc#L6508-L6685) | Defines pipeline barrier commands and dependency scopes. |
