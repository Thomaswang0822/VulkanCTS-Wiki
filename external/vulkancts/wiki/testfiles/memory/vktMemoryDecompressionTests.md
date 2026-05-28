# Memory Decompression Tests

Tests for `VK_EXT_memory_decompression`. Validates GPU-accelerated memory decompression using the GDeflate 1.0 algorithm, covering both direct and indirect dispatch modes across multiple compression levels, batch sizes, and data sizes.

## Source

- [vktMemoryDecompressionTests.cpp](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp)

## Verified Group Name

`decompression` ([line 397](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L397))

## Registration Hierarchy

```text
memory.decompression
├── direct
└── indirect
```

## Test Families

### direct — Direct decompression dispatch

Tests decompression using `vkCmdDecompressMemoryEXT()` with a `VkDecompressMemoryInfoEXT` structure containing an array of `VkDecompressMemoryRegionEXT` regions. The command processes exactly `executedDecompressionCount` regions from the array ([vktMemoryDecompressionTests.cpp:276-282](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L276)).

Internal structure under `direct`:

- `compression_level_0` / `compression_level_6` / `compression_level_12` — each compression level contains the same set of count subgroups
- Each count subgroup (`count_1_1`, `count_20_12`, `count_30_30_longstride`, `count_32_32`, `count_64_64`, `count_128_128`) contains two leaf tests: `decompressed_size_17k` and `decompressed_size_64k`

### indirect — Indirect decompression dispatch

Tests decompression using `vkCmdDecompressMemoryIndirectCountEXT()` where the decompression parameters are stored in a GPU buffer. The command reads `executedDecompressionCount` from a count buffer and processes that many entries from the indirect parameter buffer, using the specified stride between entries ([vktMemoryDecompressionTests.cpp:283-288](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L283)).

Internal structure under `indirect` mirrors `direct` with the same compression levels, count subgroups, and decompressed-size leaf tests.

## Parameter Dimensions

### Test mode

| Mode | Command | Description |
|------|---------|-------------|
| `direct` | `vkCmdDecompressMemoryEXT` | CPU-provided decompression info structure |
| `indirect` | `vkCmdDecompressMemoryIndirectCountEXT` | GPU buffer containing decompression parameters |

### Compression levels

| Level | Name | Description |
|-------|------|-------------|
| 0 | `compression_level_0` | No compression (baseline) |
| 6 | `compression_level_6` | Medium compression |
| 12 | `compression_level_12` | Maximum compression |

### Decompression count parameters

| Name | Total Count | Executed Count | Stride | Description |
|------|-------------|----------------|--------|-------------|
| `count_1_1` | 1 | 1 | `sizeof(VkDecompressMemoryRegionEXT)` | Single decompression |
| `count_20_12` | 20 | 12 | `sizeof(VkDecompressMemoryRegionEXT)` | Partial batch (12 of 20) |
| `count_30_30_longstride` | 30 | 30 | `sizeof(VkDecompressMemoryRegionEXT) + 64` | Full batch with extended stride |
| `count_32_32` | 32 | 32 | `sizeof(VkDecompressMemoryRegionEXT)` | Full batch (warp-sized) |
| `count_64_64` | 64 | 64 | `sizeof(VkDecompressMemoryRegionEXT)` | Full batch (2 warps) |
| `count_128_128` | 128 | 128 | `sizeof(VkDecompressMemoryRegionEXT)` | Large batch |

### Decompressed data sizes

| Name | Source File | Description |
|------|-------------|-------------|
| `decompressed_size_17k` | `vulkan/data/gdeflate/decompressed_17k.gdef` | ~17KB test data |
| `decompressed_size_64k` | `vulkan/data/gdeflate/decompressed_64k.gdef` | ~64KB test data |

## Support / Feature Requirements

| Extension/Feature | Required by |
|-------------------|-------------|
| `VK_EXT_memory_decompression` | All tests ([vktMemoryDecompressionTests.cpp:379](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L379)) |
| `memoryDecompression` feature | All tests ([vktMemoryDecompressionTests.cpp:381-383](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L381)) |
| `VK_MEMORY_DECOMPRESSION_METHOD_GDEFLATE_1_0_BIT_EXT` | All tests ([vktMemoryDecompressionTests.cpp:386-387](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L386)) |
| `maxDecompressionIndirectCount >= requested count` | Tests with count > 1 ([vktMemoryDecompressionTests.cpp:389-390](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L389)) |

## Verification Methods

### Data correctness validation ([vktMemoryDecompressionTests.cpp:322-342](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L322))

1. **Executed regions:** For each of the first `executedDecompressionCount` regions, the decompressed output is compared byte-by-byte against the expected reference data loaded from `vulkan/data/gdeflate/decompressed_*.gdef`
2. **Non-executed regions:** For regions beyond `executedDecompressionCount`, the output buffer (pre-filled with `0xFF`) must NOT match the reference data, confirming those regions were not processed
3. **64-byte alignment:** Each decompressed region is aligned to 64 bytes (`decompressedSizeAligned64`) to meet hardware requirements ([vktMemoryDecompressionTests.cpp:173](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L173))

### Synchronization

A `VK_PIPELINE_STAGE_2_MEMORY_DECOMPRESSION_BIT_EXT` memory barrier with `VK_ACCESS_2_MEMORY_DECOMPRESSION_WRITE_BIT_EXT` → `VK_ACCESS_2_MEMORY_DECOMPRESSION_READ_BIT_EXT` is inserted after the decompression command and before the copy to the destination buffer ([vktMemoryDecompressionTests.cpp:291-310](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L291)).

## Test Principles

- **Buffer setup:** Three buffers are used:
  - **Source buffer:** Contains compressed GDeflate data (host-visible, device-addressable)
  - **Decompress buffer:** Receives decompressed output (device-addressable only)
  - **Destination buffer:** Copy target for CPU validation (host-visible)
  - **Indirect buffer:** Contains `VkDecompressMemoryRegionEXT` array (for indirect mode)
  - **Count buffer:** Contains the executed count (for indirect mode)
- **CRLF normalization:** Reference data has Windows-style line endings (`\r\n`) converted to Unix-style (`\n`) before comparison ([vktMemoryDecompressionTests.cpp:102-121](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L102))
- **Partial execution:** Tests where `executedDecompressionCount < decompressionCount` verify that only the specified number of regions are processed
- **Stride testing:** The `count_30_30_longstride` test uses an extended stride (`sizeof(VkDecompressMemoryRegionEXT) + 64`) to verify correct parameter buffer indexing

## Notes

- Test data files are loaded from the embedded archive (`vulkan/data/gdeflate/`) via `tcu::Archive` ([vktMemoryDecompressionTests.cpp:123-140](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L123))
- The indirect mode test uses `VK_BUFFER_USAGE_2_TRANSFER_SRC_BIT_KHR` on the decompress buffer to allow the subsequent `vkCmdCopyBuffer` operation ([vktMemoryDecompressionTests.cpp:188](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L188))
- The `longstride` test is the only one that uses a non-standard stride, testing buffer alignment edge cases
