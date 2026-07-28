# Understanding Brief: Buffer Device Address

## One-Sentence Test Purpose

This test checks whether Vulkan preserves and consumes buffer device addresses across shader pointer traversal, integer conversions, memory layouts, shader stages, capture replay, SPIR-V access chains, and copied buffer-reference structs.

## Background Knowledge

### Physical storage buffer addresses

`vkGetBufferDeviceAddress` returns the 64-bit base address of a buffer. The address range from that base through the buffer's size can identify bytes in the bound memory. Zero is reserved for null ([buffer device addresses](../../../../vulkan-docs/src/chapters/resources.adoc#L1391-L1440)). A shader can load such an address from a descriptor-backed block and use it as a `PhysicalStorageBuffer` pointer for dependent loads or stores. Every access through that pointer must fall within some buffer's address range ([physical storage buffer access](../../../../vulkan-docs/src/chapters/descriptors.adoc#L678-L698)).

Why it matters here:

- The ordinary matrix builds a ternary tree whose edges are buffer device addresses. The shader follows those edges and checks fields at each reached address.
- `uint64_t` and `uvec2` variants force the implementation to preserve the same address while converting between pointer and integer representations.
- `op_access_chain` checks address arithmetic after a pointer has entered the `PhysicalStorageBuffer` storage class.

### Capture replay addresses

The KHR capture-replay path saves opaque buffer and memory addresses, then supplies them when it recreates the objects. A nonzero buffer opaque capture address should come from an identically created buffer on the same implementation ([buffer address request](../../../../vulkan-docs/src/chapters/resources.adoc#L999-L1031)). Its matching memory allocation uses `VK_MEMORY_ALLOCATE_DEVICE_ADDRESS_CAPTURE_REPLAY_BIT` ([capture-replay allocation rules](../../../../vulkan-docs/src/chapters/memory.adoc#L1759-L1774)). The EXT path requests the old device address through `VkBufferDeviceAddressCreateInfoEXT`; `vkGetBufferDeviceAddress` must then return that capture-time address ([replayed device address](../../../../vulkan-docs/src/chapters/resources.adoc#L1428-L1436)).

Why it matters here:

- `replay` variants recreate the buffers used by the shader and require every queried device address to match its original value.
- `capture_replay_stress` performs the same address-preservation check on 100 buffers whose sizes come from a seeded random sequence, without running a shader.

### Layout and access-chain interpretation

Shader block members use offsets, array strides, matrix strides, and alignment rules. Scalar alignment permits tighter arrays and matrices than the extended alignment represented by GLSL `std140` ([alignment requirements](../../../../vulkan-docs/src/chapters/interfaces.adoc#L1809-L1900), [GLSL layout correspondence](../../../../vulkan-docs/src/chapters/interfaces.adoc#L2017-L2023)). An `OpAccessChain` computes a pointer from a base pointer plus type-directed indexes. For a physical pointer, the result must preserve the selected member and array offsets before `OpConvertPtrToU` exposes the numeric address.

Why it matters here:

- The host writes bytes with the same fixed offsets and layout-dependent strides declared by generated GLSL.
- `memory_model_offset` expects index 128 in a runtime array of 32-bit words to add 512 bytes to the base address.

## One Concrete Example

For `dEQP-VK.binding_model.buffer_device_address.set0.depth1.basessbo.load.nostore.single.std140.comp`, the host allocates one buffer and treats four aligned regions as the root plus its three depth-1 children. It writes child device addresses into root members `c[0]`, `c[1]`, and `d`. The compute shader reads the root through descriptor set 0 binding 1, follows each `T1` buffer reference, and compares the reached integer and matrix fields with deterministic values.

A simplified view is:

```text
root x
├── c[0] -> child 1
├── c[identity[1]] -> child 2
└── d -> child 3
```

All 256 by 256 invocations run the same checks. Each writes `1` to its `r32ui` texel if every field matches, or `0` if any load, layout calculation, dynamic index, or pointer traversal is wrong ([shader generation](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L370-L469), [host data construction](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L320-L368)).

## End-to-End Test Flow

```text
1. Ordinary pointer matrix
[host] choose descriptor set, depth, base block, conversion, local-store, topology, layout, stage, and memory-offset parameters
[host] create one or many device-addressable buffers; for replay, capture addresses, destroy the objects, recreate them, and compare addresses
[host] populate the pointer tree and deterministic fields, then bind the root block and r32ui result image
[host] create a compute or graphics pipeline and push identity[i] = i
[device] traverse the tree, check fields and pointer relations, and write 1 or 0 to every result texel
[host] copy the image to a host-visible buffer and require all 65,536 words to equal 1

2. Capture-replay stress
[host] create 100 capture-replay buffers with seeded sizes from 4 KiB through 4 MiB
[host] record every device address; on the KHR path, also record buffer and memory opaque addresses
[host] destroy all objects, recreate them in reverse order with the path-specific recorded addresses, and require exact device-address equality

3. Access-chain and miscellaneous leaves
[host] create the leaf-specific descriptor, device-addressable buffers, and pipeline
[device] compute and export an access-chain address, emit fragment debug-print data through nested physical pointers, or store through a copied buffer-reference struct
[host] wait, invalidate host-visible memory, and compare the exact expected word or word sequence
```

[`BufferAddressTestInstance::iterate`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L582-L1324) implements the ordinary flow. Three separate instances implement the specialized flows ([capture replay](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1400-L1542), [access-chain leaves](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1558-L1916), [struct copy](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2234-L2310)).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `BufferAddressTestCase::initPrograms` generates compute, vertex, or fragment GLSL from a common declaration block and recursive checks. The current source sets `ENABLE_RAYTRACING` to `0`, so registration excludes `rgen` leaves ([stage definitions](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L58-L74), [stage builders](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L444-L558)).
- Ordinary cases target SPIR-V 1.0 except `convertcheckuv2`, which targets SPIR-V 1.5 for its `uvec2` `OpBitcast` path ([build options](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L436-L469)).
- `memory_model_offset` supplies SPIR-V assembly at target SPIR-V 1.5 so the case can state `VulkanMemoryModel`, `PhysicalStorageBufferAddresses`, `OpAccessChain`, and `OpConvertPtrToU` directly ([assembly source](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1654-L1719)).
- `fragment_store` supplies a fragment SPIR-V assembly module with nested physical pointer access chains and `NonSemantic.DebugPrintf`; the generator also supplies its GLSL vertex shader ([fragment artifacts](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1935-L2210)).
- `copy_struct` generates one compute GLSL shader. It copies `Foo`, which contains a `T1` buffer reference, then stores `2` through the copied reference ([misc shader](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2330-L2358)).
- `capture_replay_stress` has no program artifact because it checks API address recreation directly ([empty program setup](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1327-L1337)).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Ordinary pointer-tree buffer or buffers | yes | yes | read | no | Holds fixed fields and the physical addresses followed by the shader. |
| Ordinary root descriptor | yes | yes | read | no | Exposes the root as a UBO or SSBO at the selected descriptor set and binding 1. |
| Ordinary `r32ui` image | yes | yes | written | copied to host buffer | Records one Boolean result per compute invocation, vertex, or fragment. |
| Ordinary push constants | yes | yes | read | no | Provide `identity[1] = 1` for dynamic indexing without changing the expected child. |
| Capture-replay buffers and allocations | yes | yes | no shader access | addresses checked by host | Test address preservation before and after object recreation. |
| `memory_model_offset` input SSBO | yes | yes | read and written | yes | Carries the base address and receives the converted address at word 3. |
| `fragment_store` root pointer, root node, and print buffers | yes | yes | read and written | print buffer only | Form a two-hop physical pointer chain and hold the exact debug-print record. |
| `copy_struct` storage buffer | yes | yes | read | no | Stores `index` and the `Foo` object containing the target address. |
| `copy_struct` target buffer | yes | yes | written | yes | Receives integer `2` through the copied reference. |

## What Is Checked

| Behavior | Pass condition |
|----------|----------------|
| Ordinary pointer matrix | Every copied result-image word is `1`; any failed shader check writes `0`. |
| Ordinary `replay` topology | Every recreated buffer's queried device address equals its address before destruction, then the ordinary shader result also passes. |
| `capture_replay_stress` | All 100 recreated buffers report their original device addresses. |
| `op_access_chain.memory_model_offset` | Input SSBO word 3 equals the low 32 bits of `bdaAddress + 128 * sizeof(uint32_t)`. |
| `op_access_chain.fragment_store` | The first 28 print-buffer words match the fixed `expectedValues` sequence. |
| `misc.copy_struct` | The first integer in the device-addressable target buffer equals `2`. |

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group
>
> **Candidate values:** `ordinary pointer tree (set0, set3, set7, set15, set31)`, `capture_replay_stress`, `op_access_chain`, `misc`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `ordinary pointer tree (set0, set3, set7, set15, set31)` | Physical pointer matrix execution and layout. |
| `capture_replay_stress` | Capture-replay address recreation. |
| `op_access_chain` | Access-chain lowering and output. |
| `misc` | Buffer-reference struct copy. |

## Important Variations and Special Cases

- The five `set*` intermediate nodes select descriptor set indices 0, 3, 7, 15, and 31. The test creates intervening layouts and skips a leaf if `maxBoundDescriptorSets` cannot include that index ([set support](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L173-L182), [pipeline layout construction](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L868-L893)).
- Depth values `depth1`, `depth2`, and `depth3` produce 4, 13, and 40 pointer-tree regions. The generator limits `depth3` and `scalar` to `set3` to control runtime ([matrix pruning](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2445-L2491)).
- `single` packs all tree regions into one buffer; `multi` allocates one buffer per region; `replay` uses multiple capture-replay buffers. Only `single` adds `_offset_nonzero` leaves.
- `std140` and `scalar` change array, pointer-array, and matrix strides. Scalar leaves require `scalarBlockLayout` ([layout support](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L199-L200)).
- `comp`, `frag`, and `vert` execute the same recursive checks through different pipeline stages. Vertex storage-image writes require `vertexPipelineStoresAndAtomics`; `fragment_store` requires `fragmentStoresAndAtomics` ([stage features](../../../../vulkan-docs/src/chapters/features.adoc#L492-L502)).
- `convert`, `convertuvec2`, `convertchecku64`, `convertcheckuv2`, `crossconvertu2p`, and `crossconvertp2u` separate integer-width, representation, round-trip, and equality behavior. The implementation gates 64-bit integer paths on `shaderInt64` and `uvec2` paths on `VK_KHR_buffer_device_address` ([conversion support](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L209-L218)).
- The default mustpass file contains 4,717 leaves for this test family: 672 each under `set0`, `set7`, `set15`, and `set31`; 2,016 under `set3`; 10 stress seeds; two access-chain leaves; and one misc leaf ([mustpass range](../../../mustpass/main/vk-default/binding-model.txt#L1-L4717)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test category routing | [`createChildren`](../../../modules/vulkan/binding_model/vktBindingModelTests.cpp#L52-L70) | Registers `buffer_device_address` in `binding_model`. |
| Ordinary support and generated checks | [`checkSupport`, `checkBuffer`, `fillBuffer`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L173-L368) | Defines feature gates, recursive shader checks, and matching host bytes. |
| Ordinary shader builders | [`BufferAddressTestCase::initPrograms`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L370-L559) | Produces stage-specific GLSL and target versions. |
| Ordinary runtime and validator | [`BufferAddressTestInstance::iterate`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L582-L1324) | Creates resources, handles replay, submits work, and scans the result image. |
| Capture-replay stress | [`CaptureReplayTestInstance::iterate`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1400-L1542) | Recreates 100 buffers and compares addresses. |
| Memory-model offset | [`MemoryModelOffsetTestCase` and instance](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1544-L1736) | Provides direct SPIR-V and checks the 512-byte address increment. |
| Fragment physical-pointer store | [`FragmentStoreTestCase` and instance](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L1738-L2218) | Builds the nested pointer resources and checks the 28-word print record. |
| Buffer-reference struct copy | [`BufferDeviceAddressMiscTestCase` and instance](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2220-L2363) | Copies `Foo` in GLSL and checks the target store. |
| Registration matrix | [`createBufferDeviceAddressTests`](../../../modules/vulkan/binding_model/vktBindingBufferDeviceAddressTests.cpp#L2367-L2535) | Defines all eight intermediate nodes, nested dimensions, and pruning. |

## Questions / Risk Points for User Audit

- Does the behavioral grouping keep the five set-index nodes visible without treating descriptor set number as the main semantic distinction?
- Is the difference between shader-executed `replay` leaves and shader-free `capture_replay_stress` clear?
- Does the access-chain explanation distinguish numeric address arithmetic from cross-invocation memory ordering?
- Are the host-visible result resources and exact pass conditions sufficient to interpret a failing path?

## Conversion Notes for Final Wiki Rewrite

- Keep the four behavioral groups as the primary axis and list all nested ordinary dimensions in a compact parameter table.
- Use the ordinary `set0.depth1.basessbo.load.nostore.single.std140.comp` shader to explain the pointer tree and output image.
- Use `op_access_chain.memory_model_offset` as the distinct direct-SPIR-V walkthrough because it isolates physical access-chain address arithmetic and pointer conversion.
- Explain capture replay in runtime prose because `capture_replay_stress` has no shader.
- Move source inventory to the appendix, preserve exact mustpass paths, and copy the Failure Cause Mapping table byte-for-byte.
