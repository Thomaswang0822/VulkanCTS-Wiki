# [vktApiDeviceAddressCommandsTests.cpp](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1)

## Overview

[`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1) is an implementation-heavy Level-3 file for the `api.device_address` subtree. It registers the direct child `misc` under `device_address`, and that subgroup contains five leaf cases covering sparse-buffer `vkCmdCopyMemoryKHR` scenarios plus vertex/index binding command interactions.

## Role of File

Implementation-heavy test file for the `api.device_address` subgroup. The public entry point is [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L768-L791).

## Source Code

- Primary source: [vktApiDeviceAddressCommandsTests.cpp](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1)
- Header: [vktApiDeviceAddressCommandsTests.hpp](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.hpp#L1)
- Parent-category registration: [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L100-L140)

## Registration Hierarchy

```text
api.device_address
└── misc
```

The confirmed Level-3 root is `api.device_address`, created by [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L768-L791) and registered under `api` in [`createApiTests()`](../../../modules/vulkan/api/vktApiTests.cpp#L136-L136). The exact direct child confirmed from the registration function is `misc`, created by [`new tcu::TestCaseGroup(testCtx, "misc")`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L771-L771). The leaf tests currently registered beneath that child are `copy_to_memory_with_unbound_ranges`, `copy_from_memory_with_unbound_ranges`, `use_all_vertex_index_binds`, `basic_set_stride`, and `complex_set_stride`, all added through the `caseVect` loop in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774-L788).

## Test Families

### misc — Sparse copy and vertex/index binding command coverage

Covers the `misc` direct child registered by [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L771-L789). This subgroup is the only immediate child under `device_address`, and it contains all five currently registered leaves.

| Leaf test | Mode / evidence | Instance class | Summary |
|---|---|---|---|
| `copy_to_memory_with_unbound_ranges` | `TM::COPY_TO_MEMORY_WITH_UNBOUND_RANGES` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774-L779) | `BufferAddressCommandTestCase` creating a [`BufferAddressCommandFlagsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L299-L321) | Uses [`vkCmdCopyMemoryKHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L201-L230) to copy into a sparse destination buffer while applying `VK_ADDRESS_COMMAND_UNTYPED_READ_BIT_KHR` and `VK_ADDRESS_COMMAND_UNTYPED_WRITE_BIT_KHR` through [`copyMemoryToAddress()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L201-L230). |
| `copy_from_memory_with_unbound_ranges` | `TM::COPY_FROM_MEMORY_WITH_UNBOUND_RANGES` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774-L779) | `BufferAddressCommandTestCase` creating a [`BufferAddressCommandFlagsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L299-L321) | Uses [`vkCmdCopyMemoryKHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L201-L230) to copy from a sparse source buffer with partially unbound ranges, then verifies the destination contents. |
| `use_all_vertex_index_binds` | `TM::USE_ALL_VERTEX_INDEX_BINDS` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774-L779) | `BufferAddressCommandTestCase` creating a [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L672-L718) | Exercises mixed generations of vertex/index binding commands, including classic binds, [`vkCmdBindVertexBuffers2`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L493-L501), [`vkCmdBindVertexBuffers3KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L482-L491), [`vkCmdBindIndexBuffer2KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L504-L506), and [`vkCmdBindIndexBuffer3KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L507-L508). |
| `basic_set_stride` | `TM::BASIC_SET_STRIDE` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774-L779) | `BufferAddressCommandTestCase` creating a [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L672-L718) | Focuses on whether stride state supplied through [`vkCmdBindVertexBuffers3KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L482-L491) is honored when `setStride` toggles across bindings. |
| `complex_set_stride` | `TM::COMPLEX_SET_STRIDE` in [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774-L779) | `BufferAddressCommandTestCase` creating a [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L672-L718) | Combines [`vkCmdSetVertexInputEXT`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L470-L480), [`vkCmdBindVertexBuffers2`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L493-L501), and [`vkCmdBindVertexBuffers3KHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L482-L491) to test stride precedence across multiple APIs. |

The copy-oriented leaves route through [`BufferAddressCommandFlagsTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L57-L297), which builds sparse buffers, configures partially bound memory ranges, and issues address-based copy commands. The binding-oriented leaves route through [`VertexIndexBindingTestInstance`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L324-L671), which renders indexed geometry and checks the resulting image.

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Direct child subgroup | `misc` from [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L770-L789) |
| Registered leaf cases | `copy_to_memory_with_unbound_ranges`, `copy_from_memory_with_unbound_ranges`, `use_all_vertex_index_binds`, `basic_set_stride`, `complex_set_stride` from [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774-L779) |
| Test mode enum | `COPY_TO_MEMORY_WITH_UNBOUND_RANGES`, `COPY_FROM_MEMORY_WITH_UNBOUND_RANGES`, `USE_ALL_VERTEX_INDEX_BINDS`, `BASIC_SET_STRIDE`, `COMPLEX_SET_STRIDE` in [`enum class TM`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L53-L55) and [`caseVect`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774-L779) |
| Sparse-memory binding size | `64u` bytes bound out of a `512u`-byte buffer in [`BufferAddressCommandFlagsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L106-L144) |
| Copy fill value | `253` written across the destination comparison range in [`BufferAddressCommandFlagsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L159-L176) and checked in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L237-L244) |
| Copy region size | `bufferSize` bytes via [`VkMemoryToAddressCopy`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L201-L230), with the current sparse-copy path using the same `512u` buffer size configured in [`iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L106-L144) |
| Vertex/index buffer count | `6u` buffers allocated and bound in [`VertexIndexBindingTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L380-L418) |
| Draw count | `6` indexed draws issued in the verification loop in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L527-L533) |
| Vertex input stride source | Derived from `unusedVertexFloats`, `bindingDescs`, and `strides` built in [`VertexIndexBindingTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L390-L468) |

## Support / Feature Requirements

- `VK_KHR_device_address_commands` is required for all modes by [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L720-L721).
- `VK_EXT_vertex_input_dynamic_state` is additionally required for `TM::COMPLEX_SET_STRIDE`, because that mode issues [`vkCmdSetVertexInputEXT`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L470-L480) and is gated in [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L722-L723).
- Sparse-copy modes require `DEVICE_CORE_FEATURE_SPARSE_BINDING` and `DEVICE_CORE_FEATURE_SPARSE_RESIDENCY_BUFFER`, enforced in [`checkSupport()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L724-L729).
- Sparse buffers are created with `VK_BUFFER_CREATE_SPARSE_BINDING_BIT`, `VK_BUFFER_USAGE_2_SHADER_DEVICE_ADDRESS_BIT_KHR`, and transfer usage flags in [`BufferAddressCommandFlagsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L110-L119).
- Vertex-binding modes rely on dynamic rendering helpers, vertex/index buffer device addresses, and the binding commands loaded in [`VertexIndexBindingTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L342-L379).

## Verification Methods

- **Copy leaves**: [`BufferAddressCommandFlagsTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L76-L297) clears memory, records [`vkCmdCopyMemoryToAddressKHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L201-L216) or [`vkCmdCopyAddressToMemoryKHR`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L217-L230), submits the command buffer, invalidates the allocation, and then checks every byte in the result buffer for the expected `253` value in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L237-L244).
- **Vertex/index binding leaves**: [`VertexIndexBindingTestInstance::iterate()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L324-L671) renders six indexed quads, copies the color image to a host-visible buffer, and validates alternating red-channel occupancy across sampled pixels in [`vktApiDeviceAddressCommandsTests.cpp`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L536-L553).

## Test Principles Observed

- Exercise address-based copy commands against sparse buffers with intentionally unbound regions.
- Compare legacy, intermediate, and KHR vertex/index binding command variants within one subtree.
- Validate stride-precedence behavior when multiple vertex-input state-setting commands interact.
- Use rendered-image verification for binding-command correctness and byte-accurate memory comparison for copy-command correctness.

## Notes / Uncertainties

- This normalization confirms the canonical Level-3 root as `api.device_address`, replacing the legacy split between `Registration Path` and `Test Hierarchy` sections.
- The direct child used in the canonical hierarchy is strictly the registered immediate child of [`createDeviceAddressCommandsTests()`](../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L768-L791): `misc`.
- The leaf test names remain documented in prose and tables rather than expanded in the parseable hierarchy, per the normalization contract.
