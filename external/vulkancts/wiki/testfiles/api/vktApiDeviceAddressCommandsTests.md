# [vktApiDeviceAddressCommandsTests.cpp](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1)

## Overview

[`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.device_address` subtree. It registers the direct child `misc` under `device_address`, and that subgroup contains six leaf cases covering sparse-buffer `vkCmdCopyMemoryKHR` scenarios, vertex/index binding command interactions, and a memory-range barrier between compute dispatches.

## Role of File

Implementation-heavy test file for the `api.device_address` subgroup. The public entry point is [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L926-L949).

## Source Code

- Primary source: [vktApiDeviceAddressCommandsTests.cpp](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1)
- Header: [vktApiDeviceAddressCommandsTests.hpp](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L100-L140)

## Registration Hierarchy

```text
api.device_address
└── misc
```

The confirmed Level-3 root is `api.device_address`, created by [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L926-L949) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L136-L136). The exact direct child confirmed from the registration function is `misc`, created by [`new tcu::TestCaseGroup(testCtx, "misc")`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L929-L929). The leaf tests currently registered beneath that child are `copy_to_memory_with_unbound_ranges`, `copy_from_memory_with_unbound_ranges`, `use_all_vertex_index_binds`, `basic_set_stride`, `complex_set_stride`, and `memory_range_barrier`, all added through the `caseVect` loop in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L945).

## Test Families

### misc — Sparse copy, binding-command, and memory-range-barrier coverage

Covers the `misc` direct child registered by [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L926-L949). This subgroup is the only immediate child under `device_address`, and it contains all six currently registered leaves.

| Leaf test | Mode / evidence | Instance class | Summary |
|---|---|---|---|
| `copy_to_memory_with_unbound_ranges` | `TM::COPY_TO_MEMORY_WITH_UNBOUND_RANGES` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) | `BufferAddressCommandTestCase` creating a [`BufferAddressCommandFlagsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L912-L921) | Uses [`vkCmdCopyMemoryKHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L201-L230) to copy into a sparse destination buffer while applying `VK_ADDRESS_COMMAND_UNTYPED_READ_BIT_KHR` and `VK_ADDRESS_COMMAND_UNTYPED_WRITE_BIT_KHR` through [`copyMemoryToAddress()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L201-L230). |
| `copy_from_memory_with_unbound_ranges` | `TM::COPY_FROM_MEMORY_WITH_UNBOUND_RANGES` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) | `BufferAddressCommandTestCase` creating a [`BufferAddressCommandFlagsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L912-L921) | Uses [`vkCmdCopyMemoryKHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L201-L230) to copy from a sparse source buffer with partially unbound ranges, then verifies the destination contents. |
| `use_all_vertex_index_binds` | `TM::USE_ALL_VERTEX_INDEX_BINDS` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) | `BufferAddressCommandTestCase` creating a [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L912-L921) | Exercises mixed generations of vertex/index binding commands, including classic binds, [`vkCmdBindVertexBuffers2`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L680), [`vkCmdBindVertexBuffers3KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L694), [`vkCmdBindIndexBuffer2`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L681), and [`vkCmdBindIndexBuffer3KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L695). |
| `basic_set_stride` | `TM::BASIC_SET_STRIDE` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) | `BufferAddressCommandTestCase` creating a [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L912-L921) | Focuses on whether stride state supplied through [`vkCmdBindVertexBuffers3KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L592) is honored when `setStride` toggles across bindings. |
| `complex_set_stride` | `TM::COMPLEX_SET_STRIDE` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) | `BufferAddressCommandTestCase` creating a [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L912-L921) | Combines [`vkCmdSetVertexInputEXT`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L576), [`vkCmdBindVertexBuffers2`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L625), and [`vkCmdBindVertexBuffers3KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L634) to test stride precedence across multiple APIs. |
| `memory_range_barrier` | `TM::MEMORY_RANGE_BARRIER` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) | `BufferAddressCommandTestCase` creating a [`MemoryRangeBarrierBetweenOperationsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L912-L919) | Dispatches one compute shader to write `v[i] = i`, uses [`VkMemoryRangeBarrierKHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L758-L767) through [`vkCmdPipelineBarrier2()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L785-L786), dispatches a second compute shader to add `3`, then validates the host-visible results. |

The copy-oriented leaves route through [`BufferAddressCommandFlagsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L59-L298), which builds sparse buffers, configures partially bound memory ranges, and issues address-based copy commands. The binding-oriented leaves route through [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L323-L697), which renders indexed geometry and checks the resulting image. The memory-range-barrier leaf routes through [`MemoryRangeBarrierBetweenOperationsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L699-L826), which verifies buffer-address memory-range synchronization between two compute operations.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct child subgroup | `misc` from [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L926-L949) |
| Registered leaf cases | `copy_to_memory_with_unbound_ranges`, `copy_from_memory_with_unbound_ranges`, `use_all_vertex_index_binds`, `basic_set_stride`, `complex_set_stride`, `memory_range_barrier` from [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) |
| Test mode enum | `COPY_TO_MEMORY_WITH_UNBOUND_RANGES`, `COPY_FROM_MEMORY_WITH_UNBOUND_RANGES`, `USE_ALL_VERTEX_INDEX_BINDS`, `BASIC_SET_STRIDE`, `COMPLEX_SET_STRIDE`, and `MEMORY_RANGE_BARRIER` in [`enum class TM`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L44-L52) and [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L931-L938) |
| Sparse-memory binding size | `64u` bytes bound out of sparse buffers with larger copy ranges in [`BufferAddressCommandFlagsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L134-L298) |
| Copy fill value | `253` written across the destination comparison range in [`BufferAddressCommandFlagsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L134-L298) and checked in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L278-L296) |
| Copy region size | `512u` bytes via the `m_copyRegion` initialized for the sparse-copy modes in [`BufferAddressCommandFlagsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L108-L131) |
| Vertex/index buffer count | `6u` buffers allocated and bound in [`VertexIndexBindingTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L323-L563) |
| Draw count | the binding tests issue six draw calls for set-stride modes and three indexed draw calls for all-bind variants in [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L579-L697) |
| Vertex input stride source | Derived from `unusedVertexFloats`, `bindingDescs`, and `strides` built in [`VertexIndexBindingTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L323-L563) |
| Memory-range-barrier dispatch size | `groupCount = 16`, with `outputOffset = 16` and `outputSize = groupCount * sizeof(uint32_t)` in [`MemoryRangeBarrierBetweenOperationsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L713-L725) |

## Support / Feature Requirements

- `VK_KHR_device_address_commands` is required for all modes by [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L847-L855).
- `VK_EXT_vertex_input_dynamic_state` is additionally required for `TM::COPY_TO_MEMORY_WITH_UNBOUND_RANGES` and `TM::COMPLEX_SET_STRIDE`, as gated in [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L851-L853).
- `VK_KHR_synchronization2` is additionally required for `TM::MEMORY_RANGE_BARRIER`, because that mode records and submits synchronization2 structures in [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L854-L855) and [`MemoryRangeBarrierBetweenOperationsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L758-L806).
- Sparse-copy modes require `DEVICE_CORE_FEATURE_SPARSE_BINDING` and `DEVICE_CORE_FEATURE_SPARSE_RESIDENCY_BUFFER`, enforced in [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L857-L862).
- Sparse buffers are created with sparse binding/residency flags and transfer usage in [`BufferAddressCommandFlagsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L143-L156).
- Vertex-binding modes rely on dynamic rendering helpers, vertex/index buffer device addresses, and the binding commands loaded in [`VertexIndexBindingTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L323-L697).

## Verification Methods

- **Copy leaves**: [`BufferAddressCommandFlagsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L134-L298) clears memory, records address-copy commands, submits the command buffer, invalidates the allocation, and then checks every byte in the result buffer for the expected `253` value in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L278-L296).
- **Vertex/index binding leaves**: [`VertexIndexBindingTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L323-L563) renders quads, copies the color image to a host-visible buffer, and validates the expected red-channel occupancy pattern in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L536-L553).
- **Memory-range-barrier leaf**: [`MemoryRangeBarrierBetweenOperationsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L713-L826) writes an indexed sequence with one compute dispatch, applies a buffer-address [`VkMemoryRangeBarrierKHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L758-L767), adds `3` in a second compute dispatch, performs a host-read barrier, and verifies each result element equals `i + 3` in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L811-L824).

## Test Principles Observed

- Exercise address-based copy commands against sparse buffers with intentionally unbound regions.
- Compare legacy, intermediate, and KHR vertex/index binding command variants within one subtree.
- Validate stride-precedence behavior when multiple vertex-input state-setting commands interact.
- Verify `VkMemoryRangeBarrierKHR` can synchronize address-described storage-buffer memory between compute operations.
- Use rendered-image verification for binding-command correctness, byte-accurate memory comparison for copy-command correctness, and explicit integer readback for the memory-range-barrier path.

## Notes / Uncertainties

- This normalization confirms the canonical Level-3 root as `api.device_address`, replacing the legacy split between `Registration Path` and `Test Hierarchy` sections.
- The direct child used in the canonical hierarchy is strictly the registered immediate child of [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L926-L949): `misc`.
- The leaf test names remain documented in prose and tables rather than expanded in the parseable hierarchy, per the normalization contract.
