# [vktApiDeviceAddressCommandsTests.cpp](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1)

## Overview

Tests VK_KHR_device_address_commands extension, covering two areas: (1) `vkCmdCopyMemoryKHR` with `VkAddressCommandFlagsKHR` for copying to/from sparsely bound memory with unbound ranges, and (2) vertex/index buffer binding commands (`vkCmdBindVertexBuffers3KHR`, `vkCmdBindIndexBuffer3KHR`) including stride management with `vkCmdSetVertexInputEXT` and `vkCmdBindVertexBuffers2`.

## Role of File

Implementation-heavy. Contains two test instance classes, shader generation, sparse memory management, and registration logic.

## Source Code

| File | Description |
|------|-------------|
| [vktApiDeviceAddressCommandsTests.cpp](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1) | Test implementation and registration |
| [vktApiDeviceAddressCommandsTests.hpp](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.hpp#L1) | Declares `createDeviceAddressCommandsTests` |
| [vktApiTests.cpp](../../../../../modules/vulkan/api/vktApiTests.cpp#L136) | Parent registration: `apiTests->addChild(createDeviceAddressCommandsTests(testCtx))` |

## Registration Path

```
api
  +-- device_address
       +-- misc
            +-- copy_to_memory_with_unbound_ranges
            +-- copy_from_memory_with_unbound_ranges
            +-- use_all_vertex_index_binds
            +-- basic_set_stride
            +-- complex_set_stride
```

## Test Hierarchy

```
device_address
  +-- misc
       +-- copy_to_memory_with_unbound_ranges
       |    Uses vkCmdCopyMemoryKHR with sparse destination buffer
       |    and VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR
       +-- copy_from_memory_with_unbound_ranges
       |    Uses vkCmdCopyMemoryKHR with sparse source buffer
       +-- use_all_vertex_index_binds
       |    Tests vkCmdBindVertexBuffers, vkCmdBindVertexBuffers2,
       |    vkCmdBindVertexBuffers3KHR, vkCmdBindIndexBuffer,
       |    vkCmdBindIndexBuffer2, vkCmdBindIndexBuffer3KHR
       +-- basic_set_stride
       |    Tests vkCmdBindVertexBuffers3KHR with setStride=true/false
       +-- complex_set_stride
            Tests stride interaction between vkCmdSetVertexInputEXT,
            vkCmdBindVertexBuffers2, and vkCmdBindVertexBuffers3KHR
```

## Test Families

### device_address

Group name verified at [vktApiDeviceAddressCommandsTests.cpp:770](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L770): `new tcu::TestCaseGroup(testCtx, "device_address")`.

Five test cases defined at [lines 774-779](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L774):

| Test Name | CommandFlagTestMode | Instance Class | Description |
|-----------|---------------------|----------------|-------------|
| `copy_to_memory_with_unbound_ranges` | COPY_TO_MEMORY_WITH_UNBOUND_RANGES | BufferAddressCommandFlagsTestInstance | Copy to sparse dst with UNKNOWN_STORAGE_BUFFER_USAGE flag |
| `copy_from_memory_with_unbound_ranges` | COPY_FROM_MEMORY_WITH_UNBOUND_RANGES | BufferAddressCommandFlagsTestInstance | Copy from sparse src buffer |
| `use_all_vertex_index_binds` | USE_ALL_VERTEX_INDEX_BINDS | VertexIndexBindingTestInstance | Exercise all 3 generations of vertex/index bind commands |
| `basic_set_stride` | BASIC_SET_STRIDE | VertexIndexBindingTestInstance | Test setStride flag in vkCmdBindVertexBuffers3KHR |
| `complex_set_stride` | COMPLEX_SET_STRIDE | VertexIndexBindingTestInstance | Test stride priority across multiple bind APIs |

**BufferAddressCommandFlagsTestInstance** ([line 57](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L57)): Creates sparse buffers with partial memory binding, writes test data, uses `vkCmdCopyMemoryKHR` with device address ranges and `VkAddressCommandFlagsKHR`, then verifies the copied data matches the original.

**VertexIndexBindingTestInstance** ([line 324](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L324)): Renders colored quads using different vertex/index binding APIs, then reads back the color attachment and verifies expected pixel patterns.

## Parameter Dimensions

| Dimension | Observed Values | Notes |
|-----------|----------------|-------|
| Test mode | 5 modes | See table above |
| Sparse buffer usage | Yes/No | Only for copy tests |
| Buffer size | 64, 512, 1<<18 | Varies by test mode |
| Copy size | 512 bytes | Hard-coded in copy region |
| Vertex buffer count | 3-6 | Varies by test mode |
| Stride values | Various | Based on unusedVertexFloats configuration |

## Support / Feature Requirements

- `VK_KHR_device_address_commands` required for all tests ([line 720](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L720))
- `VK_EXT_vertex_input_dynamic_state` required for `COPY_TO_MEMORY_WITH_UNBOUND_RANGES` ([line 722](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L722))
- `DEVICE_CORE_FEATURE_SPARSE_BINDING` and `DEVICE_CORE_FEATURE_SPARSE_RESIDENCY_BUFFER` required for copy tests ([lines 724-729](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L724))
- `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` required for all buffers ([line 253](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L253))

## Verification Methods

- **Copy tests**: After `vkCmdCopyMemoryKHR`, reads back the destination buffer and compares byte-by-byte against the test value (253). Passes if all `size` bytes match ([lines 237-244](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L237)).
- **Vertex/index binding tests**: Renders quads to a color attachment, reads back pixels, and checks that even-indexed fragment pairs have red channel > 253 and odd-indexed pairs have red channel < 2 ([lines 536-553](../../../../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L536)).

## Test Principles Observed

- Sparse memory coverage: tests device address commands with partially bound sparse buffers
- API generation coverage: exercises v1, v2, and v3 vertex/index binding commands
- Stride priority testing: verifies that the most recent stride-setting command takes effect

## Notes / Uncertainties

- The `COPY_TO_MEMORY_WITH_UNBOUND_RANGES` mode requires `VK_EXT_vertex_input_dynamic_state` but does not appear to use vertex input dynamic state in its test logic; this may be a dependency error or a requirement for device creation
- The copy tests use a single chunk of sparse memory binding, leaving most of the buffer unbound
- The group name is `device_address` (not `device_address_commands`), which differs from the file name
