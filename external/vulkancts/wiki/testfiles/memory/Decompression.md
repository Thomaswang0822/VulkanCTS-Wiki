## Overview

**Core question:** Does `VK_EXT_memory_decompression` decompress exactly the requested GDeflate regions, whether the command receives its parameters directly or through device memory?

- This page covers the implementation and registration in [`vktMemoryDecompressionTests.cpp`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp), under the `memory.decompression` test family.
- The tests exercise `vkCmdDecompressMemoryEXT()` and `vkCmdDecompressMemoryIndirectCountEXT()` with GDeflate 1.0 data.
- Each case varies the compression level, number of parameter entries, executed count, stride, and decompressed data size.
- The result check verifies both sides of the count contract: executed regions must contain the reference bytes, while unexecuted regions must remain different from them.

## Background Knowledge

For the shared concept memory dependencies, see [Background Knowledge](../../categories/memory.md#background-knowledge) of the `memory` page.

- A Vulkan memory-decompression region names a device address containing compressed bytes, a destination device address, and the compressed and decompressed sizes. The Vulkan [memory decompression chapter](../../../../vulkan-docs/src/chapters/memory_decompression.adoc#L79-L112) requires both addresses to come from buffers created with `VK_BUFFER_USAGE_2_MEMORY_DECOMPRESSION_BIT_EXT`.
- The [indirect command](../../../../vulkan-docs/src/chapters/memory_decompression.adoc#L183-L220) reads a 32-bit count from a buffer and uses a byte stride to locate successive `VkDecompressMemoryRegionEXT` entries. The command executes the smaller of that count and `maxDecompressionCount`.
- Vulkan assigns decompression commands their own pipeline stage and read/write access types. The [region synchronization rules](../../../../vulkan-docs/src/chapters/memory_decompression.adoc#L93-L99) require synchronization of accesses to the compressed source and decompressed destination through that stage and the corresponding access types. This test records a barrier after decompression and before copyback.

## Registration Hierarchy

```text
memory.decompression
├── direct
└── indirect
```

`direct` and `indirect` share the same compression-level, count, and data-size matrix. The command path is the primary difference between the two test families.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `direct`, `indirect` | Selects whether the command reads a host-provided `VkDecompressMemoryInfoEXT` or device-resident parameters and count | [`createMemoryDecompressionTests`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L395-L454) |
| Compression level | `compression_level_0`, `compression_level_6`, `compression_level_12` | Selects the compressed GDeflate input while keeping the expected decompressed data unchanged | [`levels`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L411-L417) and [`init`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L142-L157) |
| Region count | `count_1_1`, `count_20_12`, `count_30_30_longstride`, `count_32_32`, `count_64_64`, `count_128_128` | Sets the number of parameter entries, the number expected to execute, and, for one case, the spacing between entries | [`decompressionParams`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L422-L429) |
| Decompressed size | `decompressed_size_17k`, `decompressed_size_64k` | Selects the reference payload and tests the GDeflate size range, including the 64 KiB upper boundary | [`decompressedSizes`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L415-L420) and [`VkDecompressMemoryInfoEXT` limits](https://registry.khronos.org/vulkan/specs/latest/html/chapters/memory.html#memory-decompression) |

The count values expand as follows:

| Registered value | Total regions | Executed regions | Stride |
|------------------|---------------|------------------|--------|
| `count_1_1` | 1 | 1 | `sizeof(VkDecompressMemoryRegionEXT)` |
| `count_20_12` | 20 | 12 | `sizeof(VkDecompressMemoryRegionEXT)` |
| `count_30_30_longstride` | 30 | 30 | `sizeof(VkDecompressMemoryRegionEXT) + 64` |
| `count_32_32` | 32 | 32 | `sizeof(VkDecompressMemoryRegionEXT)` |
| `count_64_64` | 64 | 64 | `sizeof(VkDecompressMemoryRegionEXT)` |
| `count_128_128` | 128 | 128 | `sizeof(VkDecompressMemoryRegionEXT)` |

Each registered count is combined with both decompressed-size leaves and all three compression levels in each test family. The mustpass file therefore contains 36 cases per family: 3 levels × 6 count values × 2 data sizes.

## Behavior Parameters

The primary behavioral axis is the test family, because `direct` and `indirect` select different Vulkan command interfaces and different parameter delivery mechanisms.

### `direct`: Host-provided region array

The test builds a `VkDecompressMemoryInfoEXT` structure in host memory. Its `regionCount` is `executedDecompressionCount`, and `pRegions` points to the beginning of the region array. The direct command therefore receives exactly the regions that the test expects to execute. The full allocated output still has `decompressionCount` slots so the test can check that slots beyond the executed count remain untouched.

### `indirect`: Device-resident region array and count

The test writes all region records into an indirect buffer at offsets separated by `stride`, and writes `executedDecompressionCount` into a separate count buffer. It records `vkCmdDecompressMemoryIndirectCountEXT()` with `maxDecompressionCount` equal to `decompressionCount`. The command must read the count and process only the requested prefix. `count_30_30_longstride` checks that the implementation advances by the supplied stride rather than assuming tightly packed records.

The secondary dimensions change the input representation or batch shape, but they do not change this contract: each executed destination must equal the selected decompressed reference, and each non-executed destination must not equal it.

## Shader Analysis

No shader participates in these tests. The implementation uses Vulkan memory-decompression and transfer commands, so no `shader-analyzer` or `shader-disassembler` walkthrough is applicable.

## Runtime Execution and Result Checking

- The test loads `compressed_<size>_level_<level>.gdef` and `decompressed_<size>.gdef` from the embedded `vulkan/data/gdeflate/` archive. It normalizes CRLF pairs in the reference data before comparison.
- It creates a host-visible, device-addressable source buffer, a device-addressable decompression buffer, and a host-visible destination buffer. The source and decompression buffers use `VK_BUFFER_USAGE_2_MEMORY_DECOMPRESSION_BIT_EXT`; the destination buffer is a transfer target.
- For indirect cases it also creates host-visible, device-addressable indirect and count buffers. Each region points at the same compressed source and at a destination slot aligned to 64 bytes. The destination buffer starts filled with `0xFF`.
- The test records either `vkCmdDecompressMemoryEXT()` or `vkCmdDecompressMemoryIndirectCountEXT()`, then inserts a `VkMemoryBarrier2` from decompression writes to decompression reads before copying the complete decompression buffer to the destination buffer.
- After submission completes, the host compares the first `executedDecompressionCount` slots byte-for-byte with the reference payload. It compares every remaining slot with the same payload and requires each of those comparisons to differ. The case passes only if all executed and non-executed checks succeed.
- Support checks require `VK_EXT_memory_decompression`, the `memoryDecompression` feature, the `VK_MEMORY_DECOMPRESSION_METHOD_GDEFLATE_1_0_BIT_EXT` property, and a sufficient `maxDecompressionIndirectCount` for the requested region count.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `direct` | Incorrect direct region-count handling, region address or size interpretation, GDeflate decompression, destination writes, or post-decompression visibility |
| `indirect` | Incorrect indirect count handling, stride-based region fetch, region address or size interpretation, GDeflate decompression, destination writes, or post-decompression visibility |

The same decompression and copyback machinery is shared by both families. A failure across both families points to that shared path; a failure limited to `indirect` points first to the indirect parameter buffer, count, or stride path, while a failure limited to `direct` points first to the `VkDecompressMemoryInfoEXT` path.

### Cause Analysis

#### Decompression data or destination addressing

**Possible failure symptoms:** An executed slot differs from the reference bytes, or several slots show the wrong payload. The host reports `Test failed` after the byte comparison.

**Possible implementation causes:** The implementation may decode the GDeflate stream incorrectly, use the wrong compressed or decompressed size, misread a device address, or write a destination slot at the wrong offset. The source assigns each destination by a 64-byte-aligned slot and reuses the same compressed region for every entry, so the exact cause requires investigation of the failing parameter combination.

#### Executed-count boundary

**Possible failure symptoms:** A slot at or after `executedDecompressionCount` matches the reference when it should remain different, or an earlier slot remains equal to the initial `0xFF` pattern instead of containing the reference.

**Possible implementation causes:** The command may process too many or too few region entries. For the direct family, this concerns `regionCount`; for the indirect family, it concerns the count read from `indirectCommandsCountAddress` and its clamp to `maxDecompressionCount`. The source and Vulkan specification define the expected boundary, but a failing case does not identify whether the problem lies in command execution, parameter decoding, or memory writes.

#### Indirect parameter layout

**Possible failure symptoms:** An indirect case fails only for `count_30_30_longstride`, or fails when the indirect count is greater than one while `count_1_1` passes. The resulting bytes can be wrong in later slots even though the first slot is correct.

**Possible implementation causes:** The implementation may assume tightly packed `VkDecompressMemoryRegionEXT` records, apply the stride in the wrong unit, or read the count buffer incorrectly. Vulkan requires the stride to be at least the region structure size and to be a multiple of four. The test supplies the records at `t * stride`, so source-level investigation should compare the failing count and stride with the device-side parameter fetch.

#### Decompression-to-copy visibility

**Possible failure symptoms:** Decompression appears to complete, but the copied destination buffer contains stale or partially updated data. Executed-slot comparisons fail while the region parameters and reference data remain valid.

**Possible implementation causes:** The copied bytes may not reflect completed decompression writes. The source records `VK_ACCESS_2_MEMORY_DECOMPRESSION_WRITE_BIT_EXT` to `VK_ACCESS_2_MEMORY_DECOMPRESSION_READ_BIT_EXT` at the decompression stage before the transfer copy. The observed mismatch alone cannot distinguish a synchronization implementation issue from a decompression or address error, so source-level investigation is needed.

## Case Pruning

### Requirement-based pruning

- `checkSupport()` skips the case when `VK_EXT_memory_decompression` is unavailable, `memoryDecompression` is disabled, GDeflate 1.0 is not listed in `decompressionMethods`, or the device's `maxDecompressionIndirectCount` is smaller than the requested total count.
- The GDeflate Vulkan rules limit each `decompressedSize` to 65536 bytes. The registered 17 KiB and 64 KiB inputs stay within that limit.
- The test uses device addresses and buffers with the required decompression and indirect-buffer usage flags. A device that cannot provide those capabilities cannot run the case.

### Design-based pruning

- The matrix uses only compression levels 0, 6, and 12, the levels for which the archive provides matching compressed files.
- It tests one partial batch, `count_20_12`, to distinguish total capacity from the executed prefix, and one padded-stride batch, `count_30_30_longstride`, to exercise indirect indexing. The remaining counts cover single, 32, 64, and 128 region batches without adding every possible count.
- The two decompressed sizes reuse the same count and command combinations. Their purpose is to vary the payload size, not to create a separate execution model.

## Key Takeaways

- The direct and indirect families test the same GDeflate result contract through different parameter delivery paths.
- `count_20_12` verifies that the command stops at the requested executed count and does not process the unused region records.
- `count_30_30_longstride` verifies that indirect records are located using the supplied stride.
- The host checks both positive and negative evidence: executed slots must match the reference, and unexecuted slots must not match it.
- The barrier and the device-address usage flags are part of the test's correctness path. A correct decompressor result is not enough if the transfer reads stale data.

## Source Reference Appendix

| Entry point or purpose | Link | Why it matters |
|------------------------|------|----------------|
| Test registration and full matrix | [`createMemoryDecompressionTests`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L395-L456) | Registers `direct` and `indirect`, the three compression levels, six count variants, and two data sizes |
| Test support checks | [`DecompressionTestCase::checkSupport`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L374-L391) | Requires the extension, feature, GDeflate method, and indirect-count limit |
| Input loading | [`MemoryDecompressionTestInstance::init`](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L142-L158) | Selects compressed and decompressed archive resources and normalizes CRLF |
| Resource and region setup | [`MemoryDecompressionTestInstance::iterate`, buffer setup](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L160-L267) | Creates the buffers, addresses, aligned output slots, indirect records, and count value |
| Direct and indirect command recording | [`MemoryDecompressionTestInstance::iterate`, command selection](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L269-L288) | Shows the two Vulkan command paths and their parameter sources |
| Barrier and copyback | [`MemoryDecompressionTestInstance::iterate`, barrier and copy](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L290-L320) | Records the post-decompression barrier and copies the output for host checking |
| Result validation | [`MemoryDecompressionTestInstance::iterate`, validation](../../../modules/vulkan/memory/vktMemoryDecompressionTests.cpp#L322-L342) | Compares executed slots with the reference and rejects matching unexecuted slots |
| Mustpass coverage | [`memory.txt`, decompression entries](../../../mustpass/main/vk-default/memory.txt#L581-L652) | Lists the 72 registered direct and indirect test cases |
| Vulkan memory-decompression semantics | [Vulkan memory decompression chapter](https://registry.khronos.org/vulkan/specs/latest/html/chapters/memory.html#memory-decompression) | Defines region addresses, direct and indirect count semantics, stride requirements, and feature limits |
| Decompression synchronization | [Vulkan synchronization chapter](https://registry.khronos.org/vulkan/specs/latest/html/chapters/synchronization.html#synchronization-pipeline-stages) | Defines the decompression pipeline stage and access types used by the barrier |
