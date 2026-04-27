# Memory Pipeline Barrier Tests

Tests for memory visibility across Vulkan pipeline stages using `vkCmdPipelineBarrier`. Verifies that writes to buffers and images via various usage patterns (transfer, vertex, index, uniform, storage, etc.) are correctly made visible to subsequent read operations after a pipeline barrier.

## Source

[`vktMemoryPipelineBarrierTests.cpp`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp)

## Verified Group Name

`pipeline_barrier` ([line 1028](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:1028))

## Registration Path

```
memory → pipeline_barrier
```

## Test Hierarchy

```
pipeline_barrier/
├── host_write_host_read/
│   ├── 1024
│   ├── 8192
│   ├── 65536
│   └── 1048576
├── host_write_transfer_src/
│   └── ...
├── host_write_vertex_buffer/
│   ├── 1024_vertex_buffer_stride_2
│   ├── 1024_vertex_buffer_stride_4
│   ├── 8192_vertex_buffer_stride_2
│   └── ...
├── host_write_index_buffer/ ...
├── host_write_uniform_buffer/ ...
├── host_write_uniform_texel_buffer/ ...
├── host_write_storage_buffer/ ...
├── host_write_storage_texel_buffer/ ...
├── host_write_storage_image/ ...
├── host_write_sampled_image/ ...
├── transfer_dst_host_read/ ...
├── transfer_dst_transfer_src/ ...
├── transfer_dst_vertex_buffer/ ...
├── transfer_dst_index_buffer/ ...
├── transfer_dst_uniform_buffer/ ...
├── transfer_dst_uniform_texel_buffer/ ...
├── transfer_dst_storage_buffer/ ...
├── transfer_dst_storage_texel_buffer/ ...
├── transfer_dst_storage_image/ ...
├── transfer_dst_sampled_image/ ...
├── all/
│   ├── 1024_vertex_buffer_stride_2
│   ├── 1024_vertex_buffer_stride_4
│   ├── 8192_vertex_buffer_stride_2
│   └── ...
└── all_device/
    ├── 1024_vertex_buffer_stride_2
    └── ...
```

## Test Families

### Write→Read Barrier Pairs (host_write + transfer_dst)

For each write usage (`USAGE_HOST_WRITE`, `USAGE_TRANSFER_DST`), combined with each read usage ([`readUsages`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:10139)), a test group is created with the combined usage. The test writes data via the "write" usage, issues a `vkCmdPipelineBarrier`, then reads via the "read" usage, verifying the data is visible.

| Write Usage | Read Usages |
|-------------|-------------|
| `USAGE_HOST_WRITE` | host_read, transfer_src, vertex_buffer, index_buffer, uniform_buffer, uniform_texel_buffer, storage_buffer, storage_texel_buffer, storage_image, sampled_image |
| `USAGE_TRANSFER_DST` | Same read usages as above |

### All Usages Combined

- **`all`**: Combines all 12 usage flags ([line 10195](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:10195)), testing full barrier coverage with both host and device access.
- **`all_device`**: Same as `all` but with host read/write stripped ([line 10236](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:10236)), testing device-only barrier coverage.

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Buffer/image size | 1024, 8192, 65536, 1048576 (1M) | [line 1029](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:1029) |
| Write usage | HOST_WRITE, TRANSFER_DST | [`writeUsages`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:10144) |
| Read usage | 10 read usage flags | [`readUsages`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:10139) |
| Vertex buffer stride | 2, 4 (only for VERTEX_BUFFER read usage) | [line 10146](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:10146) |
| Memory type | All non-protected, compatible types (iterated at runtime) | [line 9492](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9492) |
| Iteration count | 5 per memory type | [line 9411](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9411) |
| Random ops per iteration | 50 | [line 9412](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9412) |

## Support / Feature Requirements

| Requirement | Condition | Source |
|-------------|-----------|--------|
| VK_KHR_portability_subset | Vertex buffer stride must be a multiple of `minVertexInputBindingStrideAlignment` | [`checkSupport()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:10108) |
| Host-visible memory | Required for `USAGE_HOST_READ` / `USAGE_HOST_WRITE` tests; non-host-visible types skipped | [line 9492](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9492) |
| VK_AMD_device_coherent_memory | Types with `DEVICE_COHERENT_BIT_AMD` skipped if feature not enabled | [line 9506](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9506) |
| Protected memory | Protected memory types are skipped | [line 9499](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9499) |

## Verification Methods

1. **Command-based verification**: Each test creates a sequence of `Command` objects (write, barrier, read) via [`createCommands()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9554). After execution, [`MemoryTestInstance::verify()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9633) walks through all commands calling `command.verify()` to check results.
2. **Buffer comparison**: For buffer usages, written reference data is compared against data read back after the barrier. For host reads, the mapped pointer is compared directly; for transfer reads, a staging buffer is used.
3. **Image comparison**: For image usages, rendered or transferred image data is compared against expected pixel values using `tcu::imageCompare`.
4. **Multi-iteration stress**: Each test runs 5 iterations with 50 random operations per iteration, varying the seed based on memory type index and iteration number ([line 9546](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9546)).

## Test Principles

- **Write-then-read with barrier**: The core pattern is: write data via usage A → `vkCmdPipelineBarrier` → read data via usage B → verify match.
- **Exhaustive usage coverage**: Tests all meaningful write→read usage combinations, ensuring that pipeline barriers correctly synchronize access across all pipeline stages defined by [`usageToStageFlags()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:413) and [`usageToAccessFlags()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:450).
- **Memory type iteration**: Tests iterate over all compatible memory types, returning `incomplete()` between types ([`MemoryTestInstance::iterate()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9664)).
- **Random operation mix**: Within each iteration, a random sequence of write/barrier/read operations exercises realistic usage patterns.

## Notes

- The pipeline barrier file is the largest in the memory category (~10,254 lines) due to the combinatorial explosion of usage patterns and the need for shader programs for each usage.
- Shader programs are generated in [`AddPrograms::init()`](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:9672), which creates vertex, fragment, and compute shaders tailored to each usage type.
- The `USAGE_INDIRECT_BUFFER` usage is defined but not included in the test registration due to implementation difficulty ([line 125](../../../modules/vulkan/memory/vktMemoryPipelineBarrierTests.cpp:125)).
- Color attachment and depth/stencil attachment usages are also defined in the `Usage` enum but not included in the main test matrix; they are covered only in the `all` combined group.
