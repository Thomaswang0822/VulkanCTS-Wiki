# [vktApiDeviceAddressCommandsTests.cpp](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1)

## Overview

Tests for the `VK_KHR_device_address_commands` extension, which introduces device-address-based command variants for buffer copying and vertex/index binding. The file validates two distinct areas: memory copy commands that operate on device addresses with sparse buffer support and address-command flags, and vertex/index buffer binding commands that use the new `vkCmdBindVertexBuffers3KHR` and `vkCmdBindIndexBuffer3KHR` entry points.

## Role of File

Implementation-heavy. Contains two `TestInstance` subclasses ([BufferAddressCommandFlagsTestInstance](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L57), [VertexIndexBindingTestInstance](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L324)), a `TestCase` subclass ([BufferAddressCommandTestCase](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L697)), and the registration function. All test logic, shader programs, and support checks are defined within this file.

## Source Code

| File | Path |
|------|------|
| Source | [vktApiDeviceAddressCommandsTests.cpp](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L1) |
| Header | [vktApiDeviceAddressCommandsTests.hpp](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.hpp#L1) |
| Parent registration | [vktApiTests.cpp](../../modules/vulkan/api/vktApiTests.cpp#L136) |

## Registration Path

```
api
└── device_address_commands          (non-VKSC only, vktApiTests.cpp#L136)
    └── device_address               (createDeviceAddressCommandsTests, line 770)
        └── misc                     (line 771)
            ├── copy_to_memory_with_unbound_ranges
            ├── copy_from_memory_with_unbound_ranges
            ├── use_all_vertex_index_binds
            ├── basic_set_stride
            └── complex_set_stride
```

## Test Hierarchy

```
device_address
└── misc
    ├── copy_to_memory_with_unbound_ranges   (BufferAddressCommandFlagsTestInstance)
    ├── copy_from_memory_with_unbound_ranges (BufferAddressCommandFlagsTestInstance)
    ├── use_all_vertex_index_binds           (VertexIndexBindingTestInstance)
    ├── basic_set_stride                     (VertexIndexBindingTestInstance)
    └── complex_set_stride                   (VertexIndexBindingTestInstance)
```

## Test Families

### BufferAddressCommandFlagsTestInstance

Instantiated for `COPY_TO_MEMORY_WITH_UNBOUND_RANGES` and `COPY_FROM_MEMORY_WITH_UNBOUND_RANGES` modes ([line 759-761](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L759)). Tests `vkCmdCopyMemoryKHR` with sparse buffers that have unbound memory ranges.

- **copy_to_memory_with_unbound_ranges**: Creates a sparse-resident destination buffer with a single bound chunk, then copies into it using `vkCmdCopyMemoryKHR` with `VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR` set on the destination flags ([line 112](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L112)). The copy region's destination offset is replaced with the chunk size so the copy targets an unbound region, verifying the implementation correctly handles the unknown-storage flag.

- **copy_from_memory_with_unbound_ranges**: Creates a sparse-resident source buffer with a single bound chunk, then copies from it using `vkCmdCopyMemoryKHR` with source flags set to 0 ([line 123](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L123)). The copy region's source offset is replaced with the chunk size, reading from an unbound range.

Both tests verify correctness by checking that all 512 bytes of copied data match the expected test value (253) after the copy operation ([line 239-244](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L239)).

### VertexIndexBindingTestInstance

Instantiated for `USE_ALL_VERTEX_INDEX_BINDS`, `BASIC_SET_STRIDE`, and `COMPLEX_SET_STRIDE` modes ([line 763](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L763)). Tests the new device-address-based vertex and index buffer binding commands by rendering colored quads and verifying pixel output.

- **use_all_vertex_index_binds**: Draws three quads using three generations of bind commands: `vkCmdBindVertexBuffers`/`vkCmdBindIndexBuffer` (v1), `vkCmdBindVertexBuffers2`/`vkCmdBindIndexBuffer2` (v2), and `vkCmdBindVertexBuffers3KHR`/`vkCmdBindIndexBuffer3KHR` (v3) ([line 655-694](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L655)). Verifies all three quads render correctly by checking red channel pixel values.

- **basic_set_stride**: Tests the `setStride` field of `VkBindVertexBuffer3InfoKHR`. Draws two quads: first with `setStride=true` (explicit stride of 24), then with `setStride=false` (stride of 0, expecting the pipeline's previously set stride of 16 to be used) ([line 577-601](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L577)).

- **complex_set_stride**: Interleaves stride-setting via `vkCmdSetVertexInputEXT`, `vkCmdBindVertexBuffers2`, and `vkCmdBindVertexBuffers3KHR` across six draw calls to verify stride precedence and state tracking ([line 603-653](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L603)). The final draw uses `setStride=false` on `vkCmdBindVertexBuffers3KHR`, expecting the stride from the prior `vkCmdSetVertexInputEXT` call to persist.

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| CommandFlagTestMode | COPY_TO_MEMORY_WITH_UNBOUND_RANGES, COPY_FROM_MEMORY_WITH_UNBOUND_RANGES, USE_ALL_VERTEX_INDEX_BINDS, BASIC_SET_STRIDE, COMPLEX_SET_STRIDE | [line 41-50](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L41) |
| Sparse binding | Enabled for src or dst buffer in copy modes | [line 141-142](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L141) |
| Address command flags | VK_ADDRESS_COMMAND_UNKNOWN_STORAGE_BUFFER_USAGE_BIT_KHR, 0 | [line 112-123](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L112) |
| setStride flag | true, false | [line 588, 597](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L588) |

## Support / Feature Requirements

| Requirement | Modes | Source |
|-------------|-------|--------|
| VK_KHR_device_address_commands | All modes | [line 720](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L720) |
| VK_EXT_vertex_input_dynamic_state | COPY_TO_MEMORY_WITH_UNBOUND_RANGES | [line 722](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L722) |
| DEVICE_CORE_FEATURE_SPARSE_BINDING | COPY_TO_MEMORY_WITH_UNBOUND_RANGES, COPY_FROM_MEMORY_WITH_UNBOUND_RANGES | [line 727](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L727) |
| DEVICE_CORE_FEATURE_SPARSE_RESIDENCY_BUFFER | COPY_TO_MEMORY_WITH_UNBOUND_RANGES, COPY_FROM_MEMORY_WITH_UNBOUND_RANGES | [line 728](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L728) |
| VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT | All modes (added in constructBuffer) | [line 253](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L253) |

## Verification Methods

- **Memory copy tests**: After `vkCmdCopyMemoryKHR`, the destination buffer contents are read back and each byte is compared against the expected test value (253). Pass if all bytes match ([line 239-244](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L239)).
- **Vertex/index binding tests**: After rendering quads to a color attachment, the image is copied to a host-visible buffer. The red channel of specific pixels is sampled: even-indexed quad positions must have red > 253, odd-indexed gap positions must have red < 2 ([line 536-553](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L536)). On failure, the result image is logged ([line 558](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L558)).

## Test Principles Observed

- **Feature gating**: Sparse binding and vertex input dynamic state features are checked before use ([line 716-729](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L716)).
- **Isolation**: Each test mode configures its own buffer sizes, flags, and copy regions independently ([line 107-129](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L107)).
- **Positive and gap verification**: Vertex binding tests verify both that quads render (positive) and that gaps between quads are empty (negative), preventing false passes from full-screen draws ([line 543-552](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L543)).
- **State precedence testing**: The complex_set_stride test verifies that stride state from different API entry points is correctly tracked and overridden ([line 603-653](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L603)).

## Notes / Uncertainties

- The `VK_EXT_vertex_input_dynamic_state` requirement for `COPY_TO_MEMORY_WITH_UNBOUND_RANGES` mode ([line 722](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L722)) appears unusual since that mode tests memory copy, not vertex input. This may be a copy-paste error or may be needed for an indirect reason not visible in the code.
- The `m_useSingleChunk` flag is set to `true` for both copy modes ([line 116, 127](../../modules/vulkan/api/vktApiDeviceAddressCommandsTests.cpp#L116)), meaning only one chunk of sparse memory is bound and the copy targets an offset beyond that chunk.
- The `VK_CORE_FORMAT_LAST` boundary used in format iteration is not defined in this file; it comes from the Vulkan headers.
