# [vktApiBufferComputeInstance.cpp](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L1)

## Overview

Provides helper functions for creating and configuring buffers, descriptor sets, and descriptor layouts used by compute-based API tests. These utilities create uniform buffers with initialized data, storage buffers for results, and wire up descriptor sets connecting them to compute shaders.

## Role of File

Utility/helper. Provides buffer creation and descriptor setup functions consumed by other compute-based test files.

## Source Code

- Implementation: [vktApiBufferComputeInstance.cpp](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L1)
- Header: [vktApiBufferBufferComputeInstance.hpp](../../modules/vulkan/api/vktApiBufferComputeInstance.hpp#L1)

## Registration Path

Utility file. Not directly registered in the test hierarchy. Used by other test files that need compute instance buffer utilities.

## Test Hierarchy

Not applicable (utility file).

## Classes and Utilities

### createDataBuffer ([L36](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L36))

Creates a uniform buffer of the given size, fills a specified region with `initData` and the remainder with `uninitData`. Parameters: `offset` (start of initialized region), `bufferSize`, `initData` (byte value for initialized region), `initDataSize` (size of initialized region), `uninitData` (byte value for uninitialized padding). Returns the buffer and outputs the allocation via pointer.

### createColorDataBuffer ([L77](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L77))

Creates a uniform buffer and writes two `tcu::Vec4` color values at the specified offset. Padding before and after the color data is filled with `0x5A`. Returns the buffer and outputs the allocation via pointer.

### createDescriptorSetLayout ([L121](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L121))

Creates a descriptor set layout with two bindings:
- Binding 0: `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` for compute shader output
- Binding 1: `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` for compute shader input

### createDescriptorPool ([L135](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L135))

Creates a descriptor pool supporting one storage buffer and one uniform buffer descriptor, with `VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT`.

### createDescriptorSet (single buffer) ([L146](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L146))

Creates and updates a descriptor set that connects a result buffer (binding 0, storage) and a data buffer (binding 1, uniform) with the given offset. The data buffer descriptor range is `sizeof(tcu::Vec4[2])`.

### createDescriptorSet (two buffers) ([L175](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L175))

Creates and updates a descriptor set that connects a result buffer (binding 0, storage) and one of two data buffers (binding 1, uniform) with the given offset. The second data buffer parameter (`viewB`/`offsetB`) is accepted but only the first buffer (`viewA`/`offsetA`) is bound in the current implementation.

## Parameter Dimensions

Not applicable (utility file). Parameters are determined by consuming test code.

## Support / Feature Requirements

No extension requirements. Uses core Vulkan functionality only.

## Verification Methods

Not applicable (utility file). These functions provide infrastructure for creating test resources; verification is performed by the consuming test instances.

## Test Principles Observed

- **Separation of concerns**: Buffer creation, descriptor layout, pool, and set creation are factored into separate functions, allowing test code to compose them as needed.
- **Consistent initialization**: Both `createDataBuffer` and `createColorDataBuffer` fill the entire buffer with known values (either `uninitData` or `0x5A`), preventing undefined data from affecting test results.

## Notes / Uncertainties

- The two-buffer overload of `createDescriptorSet` ([L175](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L175)) accepts `viewB` and `offsetB` parameters but only binds `viewA`/`offsetA` at binding 1. The `viewB`/`offsetB` parameters appear unused in the current implementation, which may be intentional (for future use) or a potential oversight.
- The `createDataBuffer` function uses `VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT` only ([L45](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L45)), which means buffers created by this function cannot be used as storage buffers or texel buffers.
- The `createColorDataBuffer` function hardcodes the padding byte as `0x5A` ([L108](../../modules/vulkan/api/vktApiBufferComputeInstance.cpp#L108)), which is a recognizable pattern for detecting uninitialized memory access.
- These utilities depend on `ComputeInstanceResultBuffer::DATA_SIZE` from [vktApiComputeInstanceResultBuffer.hpp](../../modules/vulkan/api/vktApiComputeInstanceResultBuffer.hpp#L43) for the result buffer descriptor info size.
