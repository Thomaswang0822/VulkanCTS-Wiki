## Overview

**Core question:** Do queried buffer device addresses remain valid and exact when shaders load, convert, copy, offset, and dereference them, and when capture-replay objects are recreated?

- The default Vulkan mustpass list contains 4,717 `buffer_device_address` leaves ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L1-L4717)). Their implementation covers recursive physical-pointer loads, pointer/integer conversions, block layouts, compute and graphics stages, capture replay, direct SPIR-V access chains, and a copied buffer-reference struct.
- Five ordinary intermediate nodes, `set0`, `set3`, `set7`, `set15`, and `set31`, run the same behavioral matrix at different descriptor set indices. `set3` carries the full depth and layout matrix; the other set nodes retain a reduced runtime sample.
- `capture_replay_stress` recreates 100 buffers per seed without a shader. `op_access_chain` contains `memory_model_offset` and `fragment_store`. `misc` contains `copy_struct`.
- The primary behavioral axis is the mechanism under test: the ordinary pointer tree, capture-replay stress, access-chain behavior, or copied-reference behavior. The descriptor set index is one matrix dimension inside the ordinary group, not a separate semantic mechanism.

## Background Knowledge

For the shared concepts of descriptor interfaces and availability and visibility, see [Background Knowledge](../../categories/binding_model.md#background-knowledge) of the `binding_model` page.

- **Physical storage buffer addresses.** `vkGetBufferDeviceAddress` returns the 64-bit base address of a buffer. Addresses from that base through the buffer's size identify its bound memory, while zero is reserved for null ([buffer device addresses](../../../../vulkan-docs/src/chapters/resources.adoc#L1391-L1440)). A shader can load an address from a descriptor-backed block and use it as a `PhysicalStorageBuffer` pointer. Every physical-pointer load, store, or atomic operation must access the address range of some buffer ([physical storage buffer access](../../../../vulkan-docs/src/chapters/descriptors.adoc#L678-L698)).
- **Capture-replay identity.** `bufferDeviceAddressCaptureReplay` allows a trace or application to save and reuse buffer and memory addresses ([feature meaning](../../../../vulkan-docs/src/chapters/features.adoc#L2875-L2884)). The KHR path requests saved opaque buffer and memory addresses through creation and allocation structures ([buffer opaque address request](../../../../vulkan-docs/src/chapters/resources.adoc#L999-L1031), [memory allocation rules](../../../../vulkan-docs/src/chapters/memory.adoc#L1759-L1774)). The EXT path requests the captured device address through `VkBufferDeviceAddressCreateInfoEXT`, after which the query must return that address ([replayed device address](../../../../vulkan-docs/src/chapters/resources.adoc#L1428-L1436)).
- **Block layout.** Vulkan derives scalar, base, and extended alignment from member types. GLSL `std140` satisfies extended alignment, while scalar layout permits tighter array, vector, and matrix placement when `scalarBlockLayout` is enabled ([alignment requirements](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1809-L1900), [GLSL layout correspondence](../../../../vulkan-docs/src/chapters/interfaces.adoc#L2017-L2023)). Host-written offsets and shader decorations must describe the same bytes.
- **Access chains and the Vulkan memory model.** `OpAccessChain` computes a typed pointer from a base pointer and indexes. Vulkan includes each access-chain index times its stride in the byte offset calculation ([buffer indexing calculations](../../../../vulkan-docs/src/appendices/spirvenv.adoc#L4125-L4148)). The `memory_model_offset` leaf uses the `PhysicalStorageBuffer64 Vulkan` memory model and converts the resulting pointer to an integer. The Vulkan memory model defines program order through function calls and instruction order within an invocation ([program order](../../../../vulkan-docs/src/appendices/memorymodel.adoc#L178-L205)); enabling its SPIR-V capability requires `vulkanMemoryModel` ([memory-model features](../../../../vulkan-docs/src/chapters/features.adoc#L2318-L2330)). This leaf tests pointer arithmetic, not communication between invocations.
- **Stage-specific stores.** Shaders run per workgroup, vertex, or fragment according to their pipeline stage ([shader execution](../../../../vulkan-docs/src/chapters/shaders.adoc#L5-L30)). Storage writes in the vertex stage require `vertexPipelineStoresAndAtomics`; fragment storage writes and atomics require `fragmentStoresAndAtomics` ([stage store features](../../../../vulkan-docs/src/chapters/features.adoc#L492-L502)).

## Registration Hierarchy

```text
binding_model.buffer_device_address
├── set0
├── set3
├── set7
├── set15
├── set31
├── capture_replay_stress
├── op_access_chain
└── misc
```

The default Vulkan mustpass file lists all 4,717 leaves in one contiguous range. It contains 672 leaves under each reduced set node, 2,016 under `set3`, 10 capture-replay seeds, two `op_access_chain` leaves, and one `misc` leaf ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L1-L4717)).

## Parameter Dimensions and Observed Values

### Ordinary pointer-tree matrix

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Descriptor set intermediate node | `set0`, `set3`, `set7`, `set15`, `set31` | Places the result image and root UBO/SSBO at set 0, 3, 7, 15, or 31. The shader's `DescriptorSet` value must stay below `maxBoundDescriptorSets` ([descriptor-set range](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1578-L1592)). | [set definitions](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2377-L2379) |
| Pointer depth | `depth1`, `depth2`, `depth3` | Builds 4, 13, or 40 logical tree regions. Every nonterminal region contains addresses for three children. | [depth definitions](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2381-L2385), [region count](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L688-L692) |
| Root descriptor type | `baseubo`, `basessbo` | Exposes the root block through a uniform-buffer or storage-buffer descriptor. Descendants remain physical storage buffers. | [base definitions](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2387-L2390), [descriptor type](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L647-L662) |
| Pointer representation | `load`, `convert`, `convertuvec2`, `convertchecku64`, `convertcheckuv2`, `crossconvertu2p`, `crossconvertp2u` | Loads references directly; round-trips them through `uint64_t` or `uvec2`; checks non-null, inequality, and terminal-null representations; or crosses the stored and conversion representations. | [conversion registration](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2392-L2407), [generated conversion checks](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L221-L317) |
| Intermediate-reference storage | `nostore`, `store` | Uses a pointer expression directly or copies each non-root reference to a local `T1`, with `restrict` on alternating generated locals. | [store definitions](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2409-L2414), [local generation](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L233-L238) |
| Buffer topology | `single`, `multi`, `replay` | Packs all regions into one allocation-backed buffer, uses one buffer per region, or recreates one capture-replay buffer per region before shader execution. | [topology definitions](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2416-L2423), [runtime topology](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L725-L832) |
| Layout | `std140`, `scalar` | Changes host and shader array, physical-pointer-array, vector, and matrix strides while preserving explicit member offsets. | [layout definitions](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2425-L2428), [host strides](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L320-L346) |
| Shader stage | `comp`, `frag`, `vert` | Runs the shared checks in a compute dispatch, full-viewport fragment draw, or point-list vertex draw. `rgen` source exists behind `ENABLE_RAYTRACING`, which is `0`. | [registered stages](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2430-L2438), [disabled ray tracing](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L58-L74) |
| Bound-memory offset | implicit zero, `_offset_nonzero` | Binds a `single` buffer at offset zero or at one memory-requirement alignment. The nonzero suffix appears only for the latter. | [offset definitions and naming](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2440-L2443), [binding offset](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L774-L792) |

The pointer tree uses fixed struct member offsets: `a` at 0, `b` at 32, `c` at 48, `d` at 80, and row-major `e` at 96. Scalar cases add `ivec3 f` at 36. `fillBuffer` writes the matching host bytes, including null child addresses at the terminal depth ([GLSL declarations](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L398-L424), [host population](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L320-L368)).

### Specialized leaves

| Intermediate node | Registered leaves | Meaning | Evidence |
|-------------------|-------------------|---------|----------|
| `capture_replay_stress` | `seed_0` through `seed_9` | Each seed chooses 100 power-of-two sizes from 4 KiB through 4 MiB, then recreates all buffers in reverse order. | [stress registration](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2517-L2522), [size generation](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1400-L1427) |
| `op_access_chain` | `memory_model_offset`, `fragment_store` | Isolates a physical-pointer offset and numeric conversion in compute, then a fragment-stage nested-pointer atomic/store sequence used by debug-print lowering. | [access-chain registration](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2524-L2529) |
| `misc` | `copy_struct` | Copies a `Foo` containing one `T1` buffer reference, then stores through the copied reference. | [misc registration](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2530-L2534), [shader](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2330-L2358) |

The specialized leaves occupy the first 13 lines of the default mustpass file ([exact mustpass entries](../../../mustpass/main/vk-default/binding-model.txt#L1-L13)):

```text
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_0
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_1
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_2
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_3
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_4
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_5
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_6
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_7
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_8
dEQP-VK.binding_model.buffer_device_address.capture_replay_stress.seed_9
dEQP-VK.binding_model.buffer_device_address.misc.copy_struct
dEQP-VK.binding_model.buffer_device_address.op_access_chain.fragment_store
dEQP-VK.binding_model.buffer_device_address.op_access_chain.memory_model_offset
```

## Behavior Parameters

The primary axis is the behavioral group. The ordinary matrix varies coverage around one recursive pointer mechanism; the three specialized groups exercise different contracts and have different result checks.

### `ordinary pointer tree (set0, set3, set7, set15, set31)`: load, transform, and follow addresses

The host writes a ternary tree of physical addresses and deterministic scalar or matrix fields. Generated shaders read the root through the selected descriptor set, recursively follow `c[0]`, dynamically indexed `c[1]`, and `d`, then OR every field mismatch into `accum`. Conversion variants change pointer representation before dereference or compare numeric forms for nullness and uniqueness ([recursive generator](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L221-L317)).

The five set nodes test the same property at increasingly high descriptor indices. The host creates `set + 1` pipeline-layout slots, fills early slots with nonempty layouts until per-stage resource limits require empty layouts, and binds the actual descriptor at the selected set ([layout slot construction](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L868-L893)).

### `capture_replay_stress`: recreate many addresses without shader execution

Each seeded leaf creates 100 capture-replay buffers and compatible memory allocations, then records every device address. The KHR path also records opaque buffer and memory capture addresses; the EXT path reuses the device address through `VkBufferDeviceAddressCreateInfoEXT`. After destroying the original objects, the test recreates them in reverse order. The leaf passes only when every new device address equals its recorded value ([stress runtime](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1400-L1542)).

This group has no shader. It separates API-level address replay from the ordinary `replay` topology, which first checks address identity and then runs the recursive shader against the recreated objects.

### `op_access_chain`: preserve physical offsets and nested fragment writes

`memory_model_offset` loads a physical `Node*` from an SSBO, computes element 128 of a runtime `uint` array with `OpAccessChain`, converts that pointer to `uint64_t`, truncates it to 32 bits in a helper, and writes it to the input SSBO. The host expects the base address plus 512 bytes ([assembly](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1654-L1719), [host check](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1623-L1634)).

`fragment_store` loads a physical pointer through two host-populated address levels. Its fragment SPIR-V atomically reserves print-buffer words and stores the debug-print record through repeated physical `OpAccessChain` instructions. The host compares the first 28 words with a fixed sequence ([resource chain](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1752-L1818), [expected output](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1899-L1915)).

### `misc`: retain a buffer reference across a struct copy

`copy_struct` reads `foo.f[foo.index]` into local `Foo new_foo`. `Foo` contains one `T1` physical reference. The shader stores `2` through `new_foo.b.a`, and the host requires the addressed target integer to become `2` ([shader and resources](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2234-L2308)).

## Shader Analysis

Two walkthroughs cover the distinct shader mechanisms. The first represents the large generated GLSL matrix and shows descriptor-to-physical pointer traversal. The second reconstructs the physical offset and pointer-to-integer conversion from the CTS-authored SPIR-V assembly for `memory_model_offset`. `capture_replay_stress` has no shader; `fragment_store` and `copy_struct` are described in the variation tables and runtime section.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.buffer_device_address.set0.depth1.basessbo.load.nostore.single.std140.comp
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `set0`, `basessbo` | Binding 1 is a root storage buffer at descriptor set 0; binding 0 is the result image. |
| `depth1`, `single` | The root and three child regions occupy one buffer at aligned device-address offsets. |
| `load`, `nostore` | Stored values have pointer type `T1`; generated expressions dereference them without integer conversion or a local pointer copy. |
| `std140`, `comp` | Uses extended-alignment strides and a 256 by 256 compute dispatch. |

#### Purpose

This shader checks the ordinary address path in its simplest complete form. It reads fixed root fields, follows three physical references, checks every child field, and writes one Boolean result per invocation.

#### Structural Design

| Shader element | Role |
|----------------|------|
| `T2 x` | Descriptor-backed root block with scalar data and three `T1` references. |
| `T1` | Physical-storage-buffer struct used for each child address. |
| `pc.identity[1]` | Supplies dynamic array index 1 without changing the expected path. |
| `accum` | OR-reduces every integer and matrix mismatch. |
| `image0_0` | Stores `1` for a complete match and `0` for any mismatch. |

#### Shader Code

```glsl
#version 450 core
#extension GL_EXT_shader_explicit_arithmetic_types_int64 : enable
#extension GL_EXT_buffer_reference : enable
#extension GL_EXT_scalar_block_layout : enable
#extension GL_EXT_buffer_reference_uvec2 : enable
layout (push_constant, std430) uniform Block { int identity[32]; } pc;
/// Binding 0 is a 256 by 256 r32ui storage image. Each invocation writes 1 when every pointer-tree field matches.
layout(r32ui, set = 0, binding = 0) uniform uimage2D image0_0;
layout(buffer_reference) buffer T1;
/// Binding 1 is the root std140 storage buffer. Its T1 members hold physical storage buffer references.
layout(set = 0, binding = 1, std140) buffer T2 {
   layout(offset = 0) int a[2]; // stride = 4 for scalar, 16 for std140
   layout(offset = 32) int b;
   layout(offset = 48) T1 c[2]; // stride = 8 for scalar, 16 for std140
   layout(offset = 80) T1 d;
   layout(offset = 96, row_major) mat2 e; // tightly packed for scalar, 16 byte matrix stride for std140
} x;
/// T1 describes every address-reached node. Its field offsets match the bytes populated by fillBuffer.
layout(buffer_reference, std140) buffer T1 {
   layout(offset = 0) int a[2]; // stride = 4 for scalar, 16 for std140
   layout(offset = 32) int b;
   layout(offset = 48) T1 c[2]; // stride = 8 for scalar, 16 for std140
   layout(offset = 80) T1 d;
   layout(offset = 96, row_major) mat2 e; // tightly packed for scalar, 16 byte matrix stride for std140
};
layout(local_size_x = 1, local_size_y = 1) in;
void main()
{
  int accum = 0, temp;
  ivec3 f;
  /// Check the root fields, including dynamic indexing through identity[1].
   accum |= x.a[0] - 0;
   accum |= x.a[pc.identity[1]] - 1;
   accum |= x.b - 2;
   accum |= int(x.e[0][0] - 3);
   accum |= int(x.e[0][1] - 5);
   accum |= int(x.e[1][0] - 4);
   accum |= int(x.e[1][1] - 6);
  /// Follow the three physical references stored in the root and check each depth-1 node.
   accum |= x.c[0].a[0] - 3;
   accum |= x.c[0].a[pc.identity[1]] - 4;
   accum |= x.c[0].b - 5;
   accum |= int(x.c[0].e[0][0] - 6);
   accum |= int(x.c[0].e[0][1] - 8);
   accum |= int(x.c[0].e[1][0] - 7);
   accum |= int(x.c[0].e[1][1] - 9);
   accum |= x.c[pc.identity[1]].a[0] - 6;
   accum |= x.c[pc.identity[1]].a[pc.identity[1]] - 7;
   accum |= x.c[pc.identity[1]].b - 8;
   accum |= int(x.c[pc.identity[1]].e[0][0] - 9);
   accum |= int(x.c[pc.identity[1]].e[0][1] - 11);
   accum |= int(x.c[pc.identity[1]].e[1][0] - 10);
   accum |= int(x.c[pc.identity[1]].e[1][1] - 12);
   accum |= x.d.a[0] - 9;
   accum |= x.d.a[pc.identity[1]] - 10;
   accum |= x.d.b - 11;
   accum |= int(x.d.e[0][0] - 12);
   accum |= int(x.d.e[0][1] - 14);
   accum |= int(x.d.e[1][0] - 13);
   accum |= int(x.d.e[1][1] - 15);
  uvec4 color = (accum != 0) ? uvec4(0,0,0,0) : uvec4(1,0,0,1);
  imageStore(image0_0, ivec2(gl_GlobalInvocationID.xy), color);
}
```

#### Additional Info

- The displayed `///` comments are wiki annotations. Compiling the annotated source and the exact comment-free reconstruction produced byte-identical SPIR-V. The generated `// stride` comments are preserved from [`initPrograms`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L398-L424).
- CTS passes explicit `ShaderBuildOptions` with `SPIRV_VERSION_1_0` for this conversion mode ([target selection](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L436-L469)).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Depth | Recursively adds three child checks per nonterminal region; depth 2 and 3 therefore produce much larger straight-line shaders. | [recursive calls](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L268-L317) |
| Conversion | Changes `c` and `d` between `T1`, `uint64_t`, and `uvec2`, adds pointer constructors, and for check modes emits non-null, inequality, and terminal equality tests. | [reference type and checks](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L380-L431) |
| `store` | Copies each non-root reference to local `T1`; odd generated buffer numbers receive `restrict`. | [local-reference branch](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L233-L238) |
| `scalar` | Adds `ivec3 f`, tightens array and pointer strides, and enables scalar-offset compilation. | [layout declarations and flags](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L398-L438) |
| Stage | Keeps the checks but changes the output coordinate to `gl_VertexIndex`, `gl_FragCoord`, or `gl_GlobalInvocationID`. Fragment cases add a fixed full-viewport vertex shader. | [stage builders](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L444-L558) |
| Descriptor set | Substitutes the selected set number in both shader resources; pointer behavior remains unchanged. | [resource declarations](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L374-L411) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 307
; Schema: 0
               OpCapability Shader
               OpCapability PhysicalStorageBufferAddresses
               OpExtension "SPV_KHR_physical_storage_buffer"
               OpExtension "SPV_KHR_storage_buffer_storage_class"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel PhysicalStorageBuffer64 GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_buffer_reference"
               OpSourceExtension "GL_EXT_buffer_reference_uvec2"
               OpSourceExtension "GL_EXT_scalar_block_layout"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types_int64"
               OpName %main "main"
               OpName %accum "accum"
               OpName %T2 "T2"
               OpMemberName %T2 0 "a"
               OpMemberName %T2 1 "b"
               OpMemberName %T2 2 "c"
               OpMemberName %T2 3 "d"
               OpMemberName %T2 4 "e"
               OpName %T1 "T1"
               OpMemberName %T1 0 "a"
               OpMemberName %T1 1 "b"
               OpMemberName %T1 2 "c"
               OpMemberName %T1 3 "d"
               OpMemberName %T1 4 "e"
               OpName %x "x"
               OpName %Block "Block"
               OpMemberName %Block 0 "identity"
               OpName %pc "pc"
               OpName %color "color"
               OpName %image0_0 "image0_0"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpDecorate %_arr_int_uint_2 ArrayStride 16
               OpDecorate %_arr_13_uint_2 ArrayStride 16
               OpDecorate %T2 Block
               OpMemberDecorate %T2 0 Offset 0
               OpMemberDecorate %T2 1 Offset 32
               OpMemberDecorate %T2 2 Offset 48
               OpMemberDecorate %T2 3 Offset 80
               OpMemberDecorate %T2 4 RowMajor
               OpMemberDecorate %T2 4 MatrixStride 16
               OpMemberDecorate %T2 4 Offset 96
               OpDecorate %_arr_int_uint_2_0 ArrayStride 16
               OpDecorate %_arr_13_uint_2_0 ArrayStride 16
               OpDecorate %T1 Block
               OpMemberDecorate %T1 0 Offset 0
               OpMemberDecorate %T1 1 Offset 32
               OpMemberDecorate %T1 2 Offset 48
               OpMemberDecorate %T1 3 Offset 80
               OpMemberDecorate %T1 4 RowMajor
               OpMemberDecorate %T1 4 MatrixStride 16
               OpMemberDecorate %T1 4 Offset 96
               OpDecorate %_arr__ptr_PhysicalStorageBuffer_T1_uint_2 ArrayStride 16
               OpDecorate %x Binding 1
               OpDecorate %x DescriptorSet 0
               OpDecorate %_arr_int_uint_32 ArrayStride 4
               OpDecorate %Block Block
               OpMemberDecorate %Block 0 Offset 0
               OpDecorate %image0_0 Binding 0
               OpDecorate %image0_0 DescriptorSet 0
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
%_ptr_Function_int = OpTypePointer Function %int
      %int_0 = OpConstant %int 0
       %uint = OpTypeInt 32 0
     %uint_2 = OpConstant %uint 2
%_arr_int_uint_2 = OpTypeArray %int %uint_2
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer_T1 PhysicalStorageBuffer
%_arr_13_uint_2 = OpTypeArray %_ptr_PhysicalStorageBuffer_T1 %uint_2
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%mat2v2float = OpTypeMatrix %v2float 2
         %T2 = OpTypeStruct %_arr_int_uint_2 %int %_arr_13_uint_2 %_ptr_PhysicalStorageBuffer_T1 %mat2v2float
%_arr_int_uint_2_0 = OpTypeArray %int %uint_2
%_arr_13_uint_2_0 = OpTypeArray %_ptr_PhysicalStorageBuffer_T1 %uint_2
         %T1 = OpTypeStruct %_arr_int_uint_2_0 %int %_arr_13_uint_2_0 %_ptr_PhysicalStorageBuffer_T1 %mat2v2float
%_ptr_PhysicalStorageBuffer_T1 = OpTypePointer PhysicalStorageBuffer %T1
%_arr__ptr_PhysicalStorageBuffer_T1_uint_2 = OpTypeArray %_ptr_PhysicalStorageBuffer_T1 %uint_2
%_ptr_StorageBuffer_T2 = OpTypePointer StorageBuffer %T2
          %x = OpVariable %_ptr_StorageBuffer_T2 StorageBuffer
%_ptr_StorageBuffer_int = OpTypePointer StorageBuffer %int
    %uint_32 = OpConstant %uint 32
%_arr_int_uint_32 = OpTypeArray %int %uint_32
      %Block = OpTypeStruct %_arr_int_uint_32
%_ptr_PushConstant_Block = OpTypePointer PushConstant %Block
         %pc = OpVariable %_ptr_PushConstant_Block PushConstant
      %int_1 = OpConstant %int 1
%_ptr_PushConstant_int = OpTypePointer PushConstant %int
      %int_2 = OpConstant %int 2
      %int_4 = OpConstant %int 4
     %uint_0 = OpConstant %uint 0
%_ptr_StorageBuffer_float = OpTypePointer StorageBuffer %float
    %float_3 = OpConstant %float 3
     %uint_1 = OpConstant %uint 1
    %float_5 = OpConstant %float 5
    %float_4 = OpConstant %float 4
    %float_6 = OpConstant %float 6
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer_T1
%_ptr_PhysicalStorageBuffer_int = OpTypePointer PhysicalStorageBuffer %int
      %int_3 = OpConstant %int 3
      %int_5 = OpConstant %int 5
%_ptr_PhysicalStorageBuffer_float = OpTypePointer PhysicalStorageBuffer %float
    %float_8 = OpConstant %float 8
    %float_7 = OpConstant %float 7
    %float_9 = OpConstant %float 9
      %int_6 = OpConstant %int 6
      %int_7 = OpConstant %int 7
      %int_8 = OpConstant %int 8
   %float_11 = OpConstant %float 11
   %float_10 = OpConstant %float 10
   %float_12 = OpConstant %float 12
      %int_9 = OpConstant %int 9
     %int_10 = OpConstant %int 10
     %int_11 = OpConstant %int 11
   %float_14 = OpConstant %float 14
   %float_13 = OpConstant %float 13
   %float_15 = OpConstant %float 15
     %v4uint = OpTypeVector %uint 4
%_ptr_Function_v4uint = OpTypePointer Function %v4uint
       %bool = OpTypeBool
        %288 = OpConstantComposite %v4uint %uint_0 %uint_0 %uint_0 %uint_0
        %289 = OpConstantComposite %v4uint %uint_1 %uint_0 %uint_0 %uint_1
     %v4bool = OpTypeVector %bool 4
        %293 = OpTypeImage %uint 2D 0 0 0 2 R32ui
%_ptr_UniformConstant_293 = OpTypePointer UniformConstant %293
   %image0_0 = OpVariable %_ptr_UniformConstant_293 UniformConstant
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
      %v2int = OpTypeVector %int 2
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
      %accum = OpVariable %_ptr_Function_int Function
      %color = OpVariable %_ptr_Function_v4uint Function
               OpStore %accum %int_0
         %26 = OpAccessChain %_ptr_StorageBuffer_int %x %int_0 %int_0
         %27 = OpLoad %int %26
         %28 = OpISub %int %27 %int_0
         %29 = OpLoad %int %accum
         %30 = OpBitwiseOr %int %29 %28
               OpStore %accum %30
         %38 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
         %39 = OpLoad %int %38
         %40 = OpAccessChain %_ptr_StorageBuffer_int %x %int_0 %39
         %41 = OpLoad %int %40
         %42 = OpISub %int %41 %int_1
         %43 = OpLoad %int %accum
         %44 = OpBitwiseOr %int %43 %42
               OpStore %accum %44
         %45 = OpAccessChain %_ptr_StorageBuffer_int %x %int_1
         %46 = OpLoad %int %45
         %48 = OpISub %int %46 %int_2
         %49 = OpLoad %int %accum
         %50 = OpBitwiseOr %int %49 %48
               OpStore %accum %50
         %54 = OpAccessChain %_ptr_StorageBuffer_float %x %int_4 %int_0 %uint_0
         %55 = OpLoad %float %54
         %57 = OpFSub %float %55 %float_3
         %58 = OpConvertFToS %int %57
         %59 = OpLoad %int %accum
         %60 = OpBitwiseOr %int %59 %58
               OpStore %accum %60
         %62 = OpAccessChain %_ptr_StorageBuffer_float %x %int_4 %int_0 %uint_1
         %63 = OpLoad %float %62
         %65 = OpFSub %float %63 %float_5
         %66 = OpConvertFToS %int %65
         %67 = OpLoad %int %accum
         %68 = OpBitwiseOr %int %67 %66
               OpStore %accum %68
         %69 = OpAccessChain %_ptr_StorageBuffer_float %x %int_4 %int_1 %uint_0
         %70 = OpLoad %float %69
         %72 = OpFSub %float %70 %float_4
         %73 = OpConvertFToS %int %72
         %74 = OpLoad %int %accum
         %75 = OpBitwiseOr %int %74 %73
               OpStore %accum %75
         %76 = OpAccessChain %_ptr_StorageBuffer_float %x %int_4 %int_1 %uint_1
         %77 = OpLoad %float %76
         %79 = OpFSub %float %77 %float_6
         %80 = OpConvertFToS %int %79
         %81 = OpLoad %int %accum
         %82 = OpBitwiseOr %int %81 %80
               OpStore %accum %82
         %84 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %int_0
         %85 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %84
         %87 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %85 %int_0 %int_0
         %88 = OpLoad %int %87 Aligned 16
         %90 = OpISub %int %88 %int_3
         %91 = OpLoad %int %accum
         %92 = OpBitwiseOr %int %91 %90
               OpStore %accum %92
         %93 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %int_0
         %94 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %93
         %95 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
         %96 = OpLoad %int %95
         %97 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %94 %int_0 %96
         %98 = OpLoad %int %97 Aligned 16
         %99 = OpISub %int %98 %int_4
        %100 = OpLoad %int %accum
        %101 = OpBitwiseOr %int %100 %99
               OpStore %accum %101
        %102 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %int_0
        %103 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %102
        %104 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %103 %int_1
        %105 = OpLoad %int %104 Aligned 16
        %107 = OpISub %int %105 %int_5
        %108 = OpLoad %int %accum
        %109 = OpBitwiseOr %int %108 %107
               OpStore %accum %109
        %110 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %int_0
        %111 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %110
        %113 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %111 %int_4 %int_0 %uint_0
        %114 = OpLoad %float %113 Aligned 4
        %115 = OpFSub %float %114 %float_6
        %116 = OpConvertFToS %int %115
        %117 = OpLoad %int %accum
        %118 = OpBitwiseOr %int %117 %116
               OpStore %accum %118
        %119 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %int_0
        %120 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %119
        %121 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %120 %int_4 %int_0 %uint_1
        %122 = OpLoad %float %121 Aligned 4
        %124 = OpFSub %float %122 %float_8
        %125 = OpConvertFToS %int %124
        %126 = OpLoad %int %accum
        %127 = OpBitwiseOr %int %126 %125
               OpStore %accum %127
        %128 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %int_0
        %129 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %128
        %130 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %129 %int_4 %int_1 %uint_0
        %131 = OpLoad %float %130 Aligned 4
        %133 = OpFSub %float %131 %float_7
        %134 = OpConvertFToS %int %133
        %135 = OpLoad %int %accum
        %136 = OpBitwiseOr %int %135 %134
               OpStore %accum %136
        %137 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %int_0
        %138 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %137
        %139 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %138 %int_4 %int_1 %uint_1
        %140 = OpLoad %float %139 Aligned 4
        %142 = OpFSub %float %140 %float_9
        %143 = OpConvertFToS %int %142
        %144 = OpLoad %int %accum
        %145 = OpBitwiseOr %int %144 %143
               OpStore %accum %145
        %146 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %147 = OpLoad %int %146
        %148 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %147
        %149 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %148
        %150 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %149 %int_0 %int_0
        %151 = OpLoad %int %150 Aligned 16
        %153 = OpISub %int %151 %int_6
        %154 = OpLoad %int %accum
        %155 = OpBitwiseOr %int %154 %153
               OpStore %accum %155
        %156 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %157 = OpLoad %int %156
        %158 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %157
        %159 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %158
        %160 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %161 = OpLoad %int %160
        %162 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %159 %int_0 %161
        %163 = OpLoad %int %162 Aligned 16
        %165 = OpISub %int %163 %int_7
        %166 = OpLoad %int %accum
        %167 = OpBitwiseOr %int %166 %165
               OpStore %accum %167
        %168 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %169 = OpLoad %int %168
        %170 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %169
        %171 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %170
        %172 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %171 %int_1
        %173 = OpLoad %int %172 Aligned 16
        %175 = OpISub %int %173 %int_8
        %176 = OpLoad %int %accum
        %177 = OpBitwiseOr %int %176 %175
               OpStore %accum %177
        %178 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %179 = OpLoad %int %178
        %180 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %179
        %181 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %180
        %182 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %181 %int_4 %int_0 %uint_0
        %183 = OpLoad %float %182 Aligned 4
        %184 = OpFSub %float %183 %float_9
        %185 = OpConvertFToS %int %184
        %186 = OpLoad %int %accum
        %187 = OpBitwiseOr %int %186 %185
               OpStore %accum %187
        %188 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %189 = OpLoad %int %188
        %190 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %189
        %191 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %190
        %192 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %191 %int_4 %int_0 %uint_1
        %193 = OpLoad %float %192 Aligned 4
        %195 = OpFSub %float %193 %float_11
        %196 = OpConvertFToS %int %195
        %197 = OpLoad %int %accum
        %198 = OpBitwiseOr %int %197 %196
               OpStore %accum %198
        %199 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %200 = OpLoad %int %199
        %201 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %200
        %202 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %201
        %203 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %202 %int_4 %int_1 %uint_0
        %204 = OpLoad %float %203 Aligned 4
        %206 = OpFSub %float %204 %float_10
        %207 = OpConvertFToS %int %206
        %208 = OpLoad %int %accum
        %209 = OpBitwiseOr %int %208 %207
               OpStore %accum %209
        %210 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %211 = OpLoad %int %210
        %212 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_2 %211
        %213 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %212
        %214 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %213 %int_4 %int_1 %uint_1
        %215 = OpLoad %float %214 Aligned 4
        %217 = OpFSub %float %215 %float_12
        %218 = OpConvertFToS %int %217
        %219 = OpLoad %int %accum
        %220 = OpBitwiseOr %int %219 %218
               OpStore %accum %220
        %221 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_3
        %222 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %221
        %223 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %222 %int_0 %int_0
        %224 = OpLoad %int %223 Aligned 16
        %226 = OpISub %int %224 %int_9
        %227 = OpLoad %int %accum
        %228 = OpBitwiseOr %int %227 %226
               OpStore %accum %228
        %229 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_3
        %230 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %229
        %231 = OpAccessChain %_ptr_PushConstant_int %pc %int_0 %int_1
        %232 = OpLoad %int %231
        %233 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %230 %int_0 %232
        %234 = OpLoad %int %233 Aligned 16
        %236 = OpISub %int %234 %int_10
        %237 = OpLoad %int %accum
        %238 = OpBitwiseOr %int %237 %236
               OpStore %accum %238
        %239 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_3
        %240 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %239
        %241 = OpAccessChain %_ptr_PhysicalStorageBuffer_int %240 %int_1
        %242 = OpLoad %int %241 Aligned 16
        %244 = OpISub %int %242 %int_11
        %245 = OpLoad %int %accum
        %246 = OpBitwiseOr %int %245 %244
               OpStore %accum %246
        %247 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_3
        %248 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %247
        %249 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %248 %int_4 %int_0 %uint_0
        %250 = OpLoad %float %249 Aligned 4
        %251 = OpFSub %float %250 %float_12
        %252 = OpConvertFToS %int %251
        %253 = OpLoad %int %accum
        %254 = OpBitwiseOr %int %253 %252
               OpStore %accum %254
        %255 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_3
        %256 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %255
        %257 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %256 %int_4 %int_0 %uint_1
        %258 = OpLoad %float %257 Aligned 4
        %260 = OpFSub %float %258 %float_14
        %261 = OpConvertFToS %int %260
        %262 = OpLoad %int %accum
        %263 = OpBitwiseOr %int %262 %261
               OpStore %accum %263
        %264 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_3
        %265 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %264
        %266 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %265 %int_4 %int_1 %uint_0
        %267 = OpLoad %float %266 Aligned 4
        %269 = OpFSub %float %267 %float_13
        %270 = OpConvertFToS %int %269
        %271 = OpLoad %int %accum
        %272 = OpBitwiseOr %int %271 %270
               OpStore %accum %272
        %273 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_T1 %x %int_3
        %274 = OpLoad %_ptr_PhysicalStorageBuffer_T1 %273
        %275 = OpAccessChain %_ptr_PhysicalStorageBuffer_float %274 %int_4 %int_1 %uint_1
        %276 = OpLoad %float %275 Aligned 4
        %278 = OpFSub %float %276 %float_15
        %279 = OpConvertFToS %int %278
        %280 = OpLoad %int %accum
        %281 = OpBitwiseOr %int %280 %279
               OpStore %accum %281
        %285 = OpLoad %int %accum
        %287 = OpINotEqual %bool %285 %int_0
        %291 = OpCompositeConstruct %v4bool %287 %287 %287 %287
        %292 = OpSelect %v4uint %291 %288 %289
               OpStore %color %292
        %296 = OpLoad %293 %image0_0
        %301 = OpLoad %v3uint %gl_GlobalInvocationID
        %302 = OpVectorShuffle %v2uint %301 %301 0 1
        %304 = OpBitcast %v2int %302
        %305 = OpLoad %v4uint %color
               OpImageWrite %296 %304 %305
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.binding_model.buffer_device_address.op_access_chain.memory_model_offset
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `op_access_chain` | Selects the direct physical-pointer access-chain test family. |
| `memory_model_offset` | Uses a physical pointer plus an index of 128 and exports the resulting address as an integer. |
| Compute, SPIR-V 1.5 | Runs one invocation with `VulkanMemoryModel` and `PhysicalStorageBufferAddresses` capabilities. |

#### Purpose

The CTS case supplies SPIR-V assembly that computes an address for element 128 of a physical runtime array, converts that pointer to a 64-bit integer, and stores the low 32 bits in an SSBO. The reconstructed GLSL below expresses the same pointer-offset and conversion operations for compiler and disassembler audit.

#### Structural Design

| Shader element | Role |
|----------------|------|
| `UintRef bda` | Physical-storage-buffer reference loaded from SSBO member 0. |
| `bda[128]` | Selects reference element 128, or an address 512 bytes after the base at the reference's 4-byte alignment. |
| `uint64_t(offsetPointer)` | Converts the adjusted physical pointer to a numeric address. |
| `storeLowWord` | Passes the address through a function and stores its low 32 bits in SSBO member 2. |

#### Shader Code

The CTS source for this case is direct SPIR-V assembly in [`MemoryModelOffsetTestCase::initPrograms`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1654-L1719). For the required compiler and disassembler audit, the following GLSL reconstruction preserves its tested operations and resource layout:

```glsl
#version 450
#extension GL_EXT_buffer_reference2 : require
#extension GL_EXT_shader_explicit_arithmetic_types_int64 : require
#extension GL_KHR_memory_scope_semantics : require
#pragma use_vulkan_memory_model

layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

/// One UintRef element spans one 32-bit word, so reference index 128 adds 512 bytes.
layout(std430, buffer_reference, buffer_reference_align = 4) buffer UintRef {
    uint value;
};

/// Binding 0 stores the target base address at offset 0 and the shader result at offset 12.
layout(set = 0, binding = 0, std430) buffer Input {
    UintRef bda;
    uint unusedValue;
    uint result;
} inputData;

void storeLowWord(uint64_t address) {
    inputData.result = uint(address);
}

void main() {
    /// Preserve the physical pointer offset when converting the adjusted reference to a 64-bit integer.
    UintRef offsetPointer = inputData.bda[128];
    storeLowWord(uint64_t(offsetPointer));
}
```

#### Additional Info

- The host places the base device address in SSBO member 0 and checks member 2 against the low 32 bits of base plus 512 ([host check](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1569-L1634)).
- The direct CTS assembly uses `OpAccessChain`, `OpConvertPtrToU`, and `VulkanMemoryModel`. The reconstruction uses `GL_EXT_buffer_reference2` indexing, which glslang lowers to physical pointer conversion, a 512-byte integer addition, and conversion back to a physical pointer.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| `fragment_store` sibling | Uses a fragment entry point, two nested physical pointer loads, `OpAtomicIAdd`, and repeated physical access-chain stores for a 28-word print-buffer record. | [fragment assembly](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1935-L2210) |
| Ordinary matrix | Uses generated GLSL and derives access chains from block member expressions. It validates loaded data through a result image rather than exporting one computed address. | [ordinary builder](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L370-L559) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.5`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.5
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 41
; Schema: 0
               OpCapability Shader
               OpCapability Int64
               OpCapability VulkanMemoryModel
               OpCapability PhysicalStorageBufferAddresses
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel PhysicalStorageBuffer64 Vulkan
               OpEntryPoint GLCompute %main "main" %inputData
               OpExecutionMode %main LocalSize 1 1 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_buffer_reference"
               OpSourceExtension "GL_EXT_buffer_reference2"
               OpSourceExtension "GL_EXT_shader_explicit_arithmetic_types_int64"
               OpSourceExtension "GL_KHR_memory_scope_semantics"
               OpName %main "main"
               OpName %storeLowWord_u641_ "storeLowWord(u641;"
               OpName %address "address"
               OpName %Input "Input"
               OpMemberName %Input 0 "bda"
               OpMemberName %Input 1 "unusedValue"
               OpMemberName %Input 2 "result"
               OpName %UintRef "UintRef"
               OpMemberName %UintRef 0 "value"
               OpName %inputData "inputData"
               OpName %offsetPointer "offsetPointer"
               OpName %param "param"
               OpDecorate %Input Block
               OpMemberDecorate %Input 0 Offset 0
               OpMemberDecorate %Input 1 Offset 8
               OpMemberDecorate %Input 2 Offset 12
               OpDecorate %UintRef Block
               OpMemberDecorate %UintRef 0 Offset 0
               OpDecorate %inputData Binding 0
               OpDecorate %inputData DescriptorSet 0
               OpDecorate %offsetPointer AliasedPointer
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %ulong = OpTypeInt 64 0
%_ptr_Function_ulong = OpTypePointer Function %ulong
          %8 = OpTypeFunction %void %_ptr_Function_ulong
               OpTypeForwardPointer %_ptr_PhysicalStorageBuffer_UintRef PhysicalStorageBuffer
       %uint = OpTypeInt 32 0
      %Input = OpTypeStruct %_ptr_PhysicalStorageBuffer_UintRef %uint %uint
    %UintRef = OpTypeStruct %uint
%_ptr_PhysicalStorageBuffer_UintRef = OpTypePointer PhysicalStorageBuffer %UintRef
%_ptr_StorageBuffer_Input = OpTypePointer StorageBuffer %Input
  %inputData = OpVariable %_ptr_StorageBuffer_Input StorageBuffer
        %int = OpTypeInt 32 1
      %int_2 = OpConstant %int 2
%_ptr_StorageBuffer_uint = OpTypePointer StorageBuffer %uint
%_ptr_Function__ptr_PhysicalStorageBuffer_UintRef = OpTypePointer Function %_ptr_PhysicalStorageBuffer_UintRef
      %int_0 = OpConstant %int 0
%_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_UintRef = OpTypePointer StorageBuffer %_ptr_PhysicalStorageBuffer_UintRef
  %ulong_512 = OpConstant %ulong 512
     %v3uint = OpTypeVector %uint 3
     %uint_1 = OpConstant %uint 1
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_1 %uint_1 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
%offsetPointer = OpVariable %_ptr_Function__ptr_PhysicalStorageBuffer_UintRef Function
      %param = OpVariable %_ptr_Function_ulong Function
         %28 = OpAccessChain %_ptr_StorageBuffer__ptr_PhysicalStorageBuffer_UintRef %inputData %int_0
         %29 = OpLoad %_ptr_PhysicalStorageBuffer_UintRef %28
         %30 = OpConvertPtrToU %ulong %29
         %32 = OpIAdd %ulong %30 %ulong_512
         %33 = OpConvertUToPtr %_ptr_PhysicalStorageBuffer_UintRef %32
               OpStore %offsetPointer %33
         %34 = OpLoad %_ptr_PhysicalStorageBuffer_UintRef %offsetPointer
         %35 = OpConvertPtrToU %ulong %34
               OpStore %param %35
         %37 = OpFunctionCall %void %storeLowWord_u641_ %param
               OpReturn
               OpFunctionEnd
%storeLowWord_u641_ = OpFunction %void None %8
    %address = OpFunctionParameter %_ptr_Function_ulong
         %11 = OpLabel
         %20 = OpLoad %ulong %address
         %21 = OpUConvert %uint %20
         %23 = OpAccessChain %_ptr_StorageBuffer_uint %inputData %int_2
               OpStore %23 %21
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Ordinary pointer matrix

- The host computes 128-byte-or-larger region alignment from UBO and SSBO offset limits. Depth determines the number of logical regions. `single` places all regions in one buffer; `multi` and `replay` create one buffer per region ([resource sizing](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L684-L738)).
- Every buffer uses `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT`; KHR allocations add `VK_MEMORY_ALLOCATE_DEVICE_ADDRESS_BIT`. A nonzero memory-offset leaf binds its single buffer at one `VkMemoryRequirements::alignment` offset ([allocation and binding](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L740-L792)).
- For `replay`, the host records each device address. The KHR path also queries opaque buffer and memory capture addresses; the EXT path requests the old device address through `VkBufferDeviceAddressCreateInfoEXT`. The host destroys all buffers and allocations, recreates them in reverse order, and returns `address mismatch` if any device address changes ([ordinary replay](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L794-L832)).
- `fillBuffer` writes every deterministic value and physical child address, then the host flushes each allocation. The selected descriptor set binds a storage image at binding 0 and the root UBO or SSBO at binding 1. Push constants set `identity[i] = i` ([data and descriptors](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L834-L900), [descriptor updates](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L953-L982)).
- Compute dispatches `256 x 256 x 1`. Vertex executes 65,536 points with rasterizer discard; fragment draws a full-viewport quad. The shader writes `1` or `0` to each result texel ([pipeline execution](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L991-L1229), [draw or dispatch](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1272-L1296)).
- A shader-to-transfer barrier precedes image copyback. After queue completion, the host invalidates the 65,536-word copy buffer and fails if any word differs from `1` ([copyback and scan](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1298-L1324)).

### Capture-replay stress

- Each seed initializes a deterministic random generator and chooses 100 buffer sizes as powers of two from 4 KiB through 4 MiB.
- The first pass creates every capture-replay buffer and memory allocation, records the buffer device address, and destroys all objects. The KHR path also records opaque buffer and memory addresses.
- The second pass recreates buffers from index 99 down to 0. The KHR path requests the opaque addresses; the EXT path requests the old device address. There is no command buffer or shader. Any unequal device address returns `address mismatch`; otherwise the leaf passes ([stress implementation](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1400-L1542)).

### `op_access_chain` and `misc`

- `memory_model_offset` creates a 1,024-byte device-addressable target and a 16-byte host-visible SSBO. It writes the target base address into SSBO words 0 and 1, dispatches once, then expects word 3 to contain the low 32 bits of base plus 512 ([offset resources and check](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1558-L1634)).
- `fragment_store` creates a 1,024-byte print buffer, a root node containing its address, and a descriptor-backed root-pointer buffer containing the node address. One triangle runs the fragment module. After completion, the host invalidates the print buffer and compares 28 exact `uint32_t` values ([fragment runtime](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1752-L1916)).
- `copy_struct` writes the target buffer address at byte 8 of a 16-byte SSBO, dispatches once, invalidates the target allocation, and requires its first integer to equal `2` ([misc runtime](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2234-L2310)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ordinary pointer tree (set0, set3, set7, set15, set31)` | Physical pointer matrix execution and layout. |
| `capture_replay_stress` | Capture-replay address recreation. |
| `op_access_chain` | Access-chain lowering and output. |
| `misc` | Buffer-reference struct copy. |

### Cause Analysis

#### Physical pointer matrix execution and layout

**Possible failure symptoms:** One or more result-image words are `0`, or a `replay` leaf returns `address mismatch` before shader execution. Failures may correlate with one conversion, depth, layout, set index, topology, stage, or nonzero binding offset.

**Possible implementation causes:** A shader compiler may produce wrong lowering for `PhysicalStorageBuffer` loads, pointer constructors, `OpConvertPtrToU`, `OpConvertUToPtr`, `OpBitcast`, dynamic indexes, or local pointer copies. The implementation may also calculate wrong `std140` or scalar member strides, expose the wrong root descriptor at a high set index, mishandle an offset-bound buffer, or fail to preserve an ordinary replay address. The spec requires physical accesses to stay within a buffer address range and defines the address returned for captured buffers ([physical access](../../../../vulkan-docs/src/chapters/descriptors.adoc#L678-L698), [address range and replay value](../../../../vulkan-docs/src/chapters/resources.adoc#L1419-L1439)). The narrowest failing matrix dimension indicates which source path to inspect.

#### Capture-replay address recreation

**Possible failure symptoms:** A stress seed returns `address mismatch` for one of 100 recreated buffers. Ordinary `replay` leaves may fail the same early comparison, while `single` and `multi` shader leaves pass.

**Possible implementation causes:** The implementation may return an unstable opaque buffer or memory capture address, fail to reserve the requested virtual address, associate an opaque address with incompatible creation or allocation state, or return a device address different from the captured one. Capture-replay memory requires the matching allocation flag and feature; querying a buffer opaque address requires a capture-replay-created buffer ([memory flags](../../../../vulkan-docs/src/chapters/memory.adoc#L1759-L1774), [opaque buffer query](../../../../vulkan-docs/src/chapters/resources.adoc#L1519-L1556)). A seed-specific failure can also expose allocator fragmentation or object-order sensitivity in the replay implementation.

#### Access-chain lowering and output

**Possible failure symptoms:** `memory_model_offset` reports a word-3 value other than base plus 512. `fragment_store` reports the first print-buffer index whose value differs from its fixed 28-word reference sequence.

**Possible implementation causes:** For `memory_model_offset`, the assembler/compiler or driver may apply the runtime-array stride or index at the wrong level, lose high address bits before `OpConvertPtrToU`, mishandle the 64-bit function parameter, or store to the wrong SSBO member. Its Vulkan memory-model capabilities must also be accepted only when the corresponding features are enabled ([feature contract](../../../../vulkan-docs/src/chapters/features.adoc#L2318-L2330)). For `fragment_store`, investigation should cover nested physical pointer loads, alignment operands, the physical-pointer atomic increment, access-chain indexes, and stores emitted for `NonSemantic.DebugPrintf`. The first differing output word separates reservation/count failures from payload stores.

#### Buffer-reference struct copy

**Possible failure symptoms:** `misc.copy_struct` leaves the target at its initial value or writes a value other than `2`.

**Possible implementation causes:** The shader compiler may copy only part of `Foo`, apply the wrong `std430` offset to `f[]`, change the 64-bit `T1` reference during the local copy, or dereference the copied reference through the wrong storage class or address. The host places the address at byte 8 because byte offsets 4 through 7 are padding, so source-level investigation must compare generated member and array-stride decorations with that host layout ([host address placement](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2251-L2266), [GLSL struct layout](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2330-L2355)).

## Case Pruning

### Requirement-based pruning

- Every ordinary and stress leaf requires buffer device address support. `replay` and `capture_replay_stress` also require `bufferDeviceAddressCaptureReplay` through either the KHR or EXT path ([ordinary support](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L173-L197), [stress support](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1353-L1372)).
- A set leaf skips when its set index is not below `maxBoundDescriptorSets`, the maximum simultaneous descriptor-set count ([source check](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L181-L182), [limit meaning](../../../../vulkan-docs/src/chapters/limits.adoc#L147-L150)).
- Vertex leaves require `vertexPipelineStoresAndAtomics`. Scalar leaves require `scalarBlockLayout`. `uint64_t` conversion paths require `shaderInt64`, and `uvec2` representation paths require `VK_KHR_buffer_device_address` ([ordinary feature checks](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L178-L218), [64-bit feature](../../../../vulkan-docs/src/chapters/features.adoc#L683-L688)).
- `memory_model_offset` requires `VK_KHR_buffer_device_address`, `VK_KHR_vulkan_memory_model`, `vulkanMemoryModel`, `vulkanMemoryModelDeviceScope`, and `shaderInt64` ([access-chain support](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1721-L1736)). `fragment_store` requires KHR buffer device address plus `fragmentStoresAndAtomics` ([fragment support](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2213-L2218)). `copy_struct` requires KHR buffer device address ([misc support](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2360-L2363)).

### Design-based pruning

- For all set nodes except `set3`, registration omits `depth3` and every non-`std140` layout. This keeps complex cases concentrated in one descriptor-set position while retaining broad set-index coverage ([runtime-reduction rule](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2485-L2487)).
- `_offset_nonzero` is generated only for `single`; multiple buffers do not add a second binding-offset axis ([offset pruning](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2489-L2491)).
- `offset_zero` has no suffix. The leaf name is only its stage, while the nonzero variant appends `_offset_nonzero` ([leaf naming](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2493-L2499)).
- `rgen` registration is compiled out because `ENABLE_RAYTRACING` is `0`. The active mustpass stage set is `comp`, `frag`, and `vert` ([stage source](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L66-L74), [registration](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2430-L2438)).

## Key Takeaways

- The large ordinary matrix checks one coherent data path: a descriptor supplies the root, physical addresses supply the edges, layout rules select the bytes, and a result image exposes every mismatch.
- `set0`, `set3`, `set7`, `set15`, and `set31` vary descriptor placement. `set3` carries the full depth and scalar-layout matrix; the other set nodes retain reduced coverage.
- Capture replay has two forms. Ordinary `replay` recreates the pointer tree and then runs a shader; `capture_replay_stress` checks 100 API-level address recreations per seed without shader execution.
- `op_access_chain` gives precise SPIR-V-level coverage of physical address arithmetic and nested physical writes. `misc.copy_struct` checks that a buffer reference survives an ordinary GLSL struct copy.
- See `## Failure Meaning` to interpret whether a failing path points toward pointer lowering, layout, capture replay, access-chain arithmetic, or copied-reference handling.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test category registration | [`createChildren`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L70) | Adds `buffer_device_address` under `binding_model`. |
| Ordinary support and recursive data model | [`checkSupport`, `checkBuffer`, `fillBuffer`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L173-L368) | Defines feature gates and matching shader/host tree traversal. |
| Ordinary shader generation | [`BufferAddressTestCase::initPrograms`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L370-L559) | Emits stage, conversion, and layout variants with explicit SPIR-V targets. |
| Ordinary runtime | [`BufferAddressTestInstance::iterate`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L582-L1324) | Creates addresses and resources, handles replay, executes, copies back, and scans. |
| Capture-replay stress | [`CaptureReplayTestCase` and instance](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1327-L1542) | Recreates 100 seeded buffers and compares addresses. |
| Memory-model offset | [`MemoryModelOffsetTestCase` and instance](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1544-L1736) | Supplies direct SPIR-V 1.5 and checks base plus 512. |
| Fragment physical-pointer output | [`FragmentStoreTestCase` and instance](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1738-L2218) | Builds a nested pointer chain and verifies the debug-print word sequence. |
| Buffer-reference struct copy | [`BufferDeviceAddressMiscTestCase` and instance](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2220-L2363) | Stores through a copied `Foo::b` reference and checks `2`. |
| Registration matrix | [`createBufferDeviceAddressTests`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2367-L2535) | Defines every intermediate node, ordinary dimension, specialized leaf, and design prune. |
| Default Vulkan mustpass | [`binding-model.txt`](../../../mustpass/main/vk-default/binding-model.txt#L1-L4717) | Lists all 4,717 executable paths for this test family. |
| CTS baseline SPIR-V target | [`getBaselineSpirvVersion`](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052) | Confirms SPIR-V 1.0 when a GLSL source does not request a higher target. |
| Buffer allocation helper | [`BufferWithMemory`](../../../framework/vulkan/vkBufferWithMemory.hpp#L43-L89) | Supplies the device-addressable and host-visible allocations used by the specialized leaves. |
