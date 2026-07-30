## Overview

**Core question:** does the implementation correctly return texel data from a `VkBufferView` when the view is read through a graphics or compute pipeline, across allocation kinds, view offsets, texel buffer usage modes, and a wide format matrix?

- Source file: [vktApiBufferViewAccessTests.cpp](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1) in the `api` source directory.
- Test category `api`, test family `buffer_view.access`, registered under `dEQP-VK.api.buffer_view.access`.
- Five intermediate nodes: `suballocation` and `dedicated_alloc` exercise end-to-end buffer view reads through a graphics or compute pipeline with `R32_UINT` data; `uniform_texel_buffer`, `storage_texel_buffer`, and `uniform_storage_texel_buffer` exercise a compute-shader all-formats matrix that reads back four sample texels per format.
- The test family is created by [createBufferViewAccessTests()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1435-L1607); the parent `buffer_view` group is attached to the `api` test category at [vktApiTests.cpp#L106](../../../modules/vulkan/api/vktApiTests.cpp#L106) via [createBufferViewTests()](../../../modules/vulkan/api/vktApiTests.cpp#L78-L84).
- The page covers behavior only. Source-navigation material is concentrated in the Source Reference Appendix.

## Background Knowledge

- A `VkBufferView` is a handle that lets shader code treat a range of a `VkBuffer` as a texel buffer. The view is created with a `VkFormat`, a byte `offset`, and a byte `range`; shader `texelFetch`/`imageLoad` calls index texels inside that range. The implementation must honor the offset and range when servicing shader reads.
- Vulkan distinguishes two texel buffer usage paths. `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` pairs with `VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER` and read-only `texelFetch` in GLSL (`uniform textureBuffer`). `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` pairs with `VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER` and `imageLoad` in GLSL (`readonly imageBuffer`). Storage texel buffer support is more restricted and depends on `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT`.
- A dedicated allocation is a `VkDeviceMemory` bound to exactly one resource, in contrast to suballocation where one `VkDeviceMemory` object backs multiple resources. Buffer view correctness must hold under both allocation paths.
- `VK_KHR_maintenance5` allows the usage passed at `vkCreateBufferView` time (the bind usage) to differ from the buffer's create usage, expressed through `VkBufferUsageFlags2CreateInfoKHR` chained in the `VkBufferViewCreateInfo::pNext`. This lets a buffer created with both uniform and storage texel buffer usages be bound as either.

## Registration Hierarchy

```text
api.buffer_view.access
├── suballocation
├── dedicated_alloc
├── uniform_texel_buffer
├── storage_texel_buffer
└── uniform_storage_texel_buffer
```

The test family has five intermediate nodes. `suballocation` and `dedicated_alloc` are created at [vktApiBufferViewAccessTests.cpp#L1444-L1448](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1444-L1448) and hold test case leaves produced by the allocation loop at [L1450-L1500](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1450-L1500). `uniform_texel_buffer` and `storage_texel_buffer` are created at [L1508-L1549](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1508-L1549) and hold one test case leaf per supported format. `uniform_storage_texel_buffer` is created at [L1553-L1604](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1553-L1604) under `#ifndef CTS_USES_VULKANSC`, so the entire intermediate node is absent from Vulkan SC builds. Its two intermediate nodes `bind_as_uniform` and `bind_as_storage` carry the per-format test case leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `suballocation`, `dedicated_alloc`, `uniform_texel_buffer`, `storage_texel_buffer`, `uniform_storage_texel_buffer` | Selects the test mechanism: end-to-end graphics/compute readback with `R32_UINT`, or compute-shader all-formats readback over `formats::bufferViewAccessFormats`. | [L1435-L1607](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1435-L1607) |
| Buffer allocation kind | `ALLOCATION_KIND_SUBALLOCATION`, `ALLOCATION_KIND_DEDICATED` | Selects how the source `VkBuffer` is backed. Combined with image allocation kind to form the `dedicated_alloc` leaf names. | [AllocationKind enum](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L61-L66), [L1444-L1448](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1444-L1448) |
| Image allocation kind | `ALLOCATION_KIND_SUBALLOCATION`, `ALLOCATION_KIND_DEDICATED` | Selects how the destination image (color attachment or storage image) is backed. Only the all-suballocation combination routes to the `suballocation` node; the other three combinations route to `dedicated_alloc`. | [L1450-L1455](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1450-L1455) |
| Queue type | `graphics`, `compute` | Selects pipeline type for the memory tests. Graphics uses vertex+fragment shaders writing to a color attachment; compute writes to a storage image. The all-formats nodes are compute-only. | [L1441](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1441) |
| Buffer/view size configuration | `complete` (512/512, offset 0), `partial_offset0` (4096/512, offset 0), `partial_offset1` (4096/512, offset 128) | Tests view boundary behavior: full view of the whole buffer, view starting at 0 of a larger buffer, and view starting at a nonzero offset of a larger buffer. | [L1457-L1499](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1457-L1499) |
| Texel buffer create usage | `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT`, `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT`, or both | Selects descriptor type, shader access function, and (for storage) format filtering. | [L1509-L1516](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1509-L1516), [L1559-L1562](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1559-L1562) |
| Texel buffer bind usage | `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT`, `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` | Only used by `uniform_storage_texel_buffer`. The bind usage is set independently of the create usage via `VkBufferUsageFlags2CreateInfoKHR` and selects the `bind_as_uniform` or `bind_as_storage` intermediate node. | [L1558-L1562](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1558-L1562), [L1036-L1044](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1036-L1044) |
| Format | 107 entries from `formats::bufferViewAccessFormats` | Format matrix used by the all-formats nodes. Includes UNORM/SNORM/UINT/SINT/SFLOAT/USCALED/SSCALED variants from 8-bit to 64-bit, plus packed and `_PACK16`/`_PACK32` formats. | [vkFormatLists.inl](../../../framework/vulkan/generated/vulkan/vkFormatLists.inl#L1394-L1503) |

The mustpass file lists 268 test case leaves under this test family. The `suballocation` and `dedicated_alloc` nodes together account for 24 leaves (3 size configurations × 2 queue types × 4 allocation-kind combinations, with the all-suballocation combination routed to `suballocation` and the other three to `dedicated_alloc`). The `uniform_texel_buffer` node lists 107 leaves, one per format. The `storage_texel_buffer` node lists 15 leaves because [isSupportedImageLoadStore()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1383-L1433) keeps only RGBA and packed `A2B10G10R10_*` formats that the GLSL `imageLoad` path can target. The `uniform_storage_texel_buffer` node lists 122 leaves: 107 under `bind_as_uniform` (same matrix as `uniform_texel_buffer`) and 15 under `bind_as_storage` (same matrix as `storage_texel_buffer`).

## Behavior Parameters

The primary behavioral axis is the intermediate node. The five values cluster into three mechanisms: end-to-end memory readback with `R32_UINT` data, all-formats readback with single-usage texel buffers, and all-formats readback where the bind usage differs from the create usage.

### `suballocation`: end-to-end memory readback with suballocated resources

The buffer and the destination image are both suballocated. Test case leaves are named `buffer_view_memory_test_complete_<queue>`, `buffer_view_memory_test_partial_offset0_<queue>`, and `buffer_view_memory_test_partial_offset1_<queue>` with `<queue>` in `{graphics, compute}`. The source buffer holds `uint32_t` values generated by [generateBuffer()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L155-L159) as `factor * i`. A graphics or compute pipeline reads the buffer view and writes the value at texel `i` to pixel `i` of the destination image; the image is copied to a host-visible buffer and scanned along the diagonal at [checkResult()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L591-L624). The test runs twice with `factor = 1` then `factor = 2` ([L783-L805](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L783-L805)) to confirm the buffer view reflects updated contents.

### `dedicated_alloc`: end-to-end memory readback with at least one dedicated allocation

Same mechanism as `suballocation`, but at least one of the buffer or image uses a dedicated allocation. The four allocation-kind combinations are produced by the loop at [L1450-L1455](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1450-L1455); the all-suballocation case routes to `suballocation`, the other three (buffer dedicated, image dedicated, or both) route here. Test case leaves carry the suffix `_with_<buffer-alloc>_<image-alloc>_<queue>` so the allocation combination is visible in the registered name.

### `uniform_texel_buffer`: all-formats readback via uniform texel buffer

The source buffer is populated by [populateSourceBuffer()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L938-L960) with a deterministic gradient (red ramp, green M-pattern, blue triangle wave, alpha = red XOR green). A compute shader runs with `local_size_x = 1` and dispatches 4 workgroups; each workgroup reads one of four fixed sample positions (6, 51, 42, 25) via `texelFetch` on a `uniform textureBuffer` and writes the result to a `std140` storage buffer ([initPrograms()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1329-L1379)). The host reads back the four `vec4` results and compares them against the source buffer pixels at the same positions. Integer and unsigned formats use exact comparison at [checkResult()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1193-L1225); floating-point formats use a `1.0 / 255.0` tolerance at [checkResultFloat()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1227-L1259). All 107 formats in `formats::bufferViewAccessFormats` are registered.

### `storage_texel_buffer`: all-formats readback via storage texel buffer

Same compute-shader mechanism as `uniform_texel_buffer`, but the buffer is created with `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT`, the descriptor type is `VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER`, and the shader reads via `imageLoad` on a `readonly imageBuffer` with an explicit format layout qualifier. The format matrix is filtered by [isSupportedImageLoadStore()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1383-L1433), which keeps only RGBA non-packed formats with component types that GLSL `imageLoad` can target, plus the packed `VK_FORMAT_A2B10G10R10_UNORM_PACK32` and `VK_FORMAT_A2B10G10R10_UINT_PACK32` formats. 15 formats remain.

### `uniform_storage_texel_buffer`: dual-usage buffer bound as uniform or as storage

The buffer is created with both `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` and `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT`. The view is then bound with a single usage selected through `VkBufferUsageFlags2CreateInfoKHR` chained into `VkBufferViewCreateInfo::pNext` at [L1035-L1045](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1035-L1045). Two intermediate nodes split the bind mode: `bind_as_uniform` registers the 107-format uniform matrix, and `bind_as_storage` registers the 15-format storage matrix. The mechanism otherwise matches `uniform_texel_buffer` and `storage_texel_buffer`. This entire intermediate node is built under `#ifndef CTS_USES_VULKANSC` at [L1553](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1553) and is absent from Vulkan SC builds.

## Shader Analysis

Shader code is part of the execution path but is not the behavior under test. The shaders exist to read from the buffer view and write a result the host can compare. The memory tests use small fixed shaders inlined at [initPrograms()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L831-L862); the all-formats tests use a compute shader generated at [L1329-L1379](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1329-L1379) whose only variation is whether the resource declaration is `uniform textureBuffer` (read with `texelFetch`) or `readonly imageBuffer` with a format layout qualifier (read with `imageLoad`). No representative shader walkthrough is provided.

## Runtime Execution and Result Checking

Memory tests (`suballocation`, `dedicated_alloc`), [BufferViewTestInstance](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L105-L806):

- Source buffer of `bufferSize * sizeof(uint32_t)` bytes is created suballocated, host-visible, with `testCase.createUsage` (uniform texel buffer) at [L288-L292](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L288-L292). A `VkBufferView` is created with `format = VK_FORMAT_R32_UINT`, `offset = elementOffset * 4`, `range = bufferViewSize * 4` at [L294-L304](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L294-L304).
- The destination image is `bufferViewSize × bufferViewSize` `VK_FORMAT_R32_UINT`. For graphics, it is a color attachment at [L200-L209](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L200-L209); for compute, it is a storage image at [L404-L416](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L404-L416).
- The graphics pipeline runs a full-screen quad through vertex+fragment shaders; the fragment shader writes `texelFetch(u_buffer, int(gl_FragCoord.x)).x` to the color attachment at [L840-L848](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L840-L848).
- The compute pipeline dispatches `bufferViewSize × bufferViewSize × 1` workgroups; the compute shader writes `texelFetch(u_buffer, int(gl_GlobalInvocationID.x)).x` to `ivec2(index, index)` of the storage image at [L850-L861](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L850-L861).
- The recorded command buffer transitions the image layout, runs the pipeline, and copies the image to a host-visible `resultBuffer` at [L626-L764](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L626-L764).
- [queuePass()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L766-L806) generates `factor * i` data with `factor = 1`, submits, calls [checkResult(1)](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L591-L624); if it passes, regenerates with `factor = 2`, submits again, and calls `checkResult(2)`.
- `checkResult(factor)` scans the diagonal: `expected = factor * (elementOffset + i)`, `actual = pixelBuffer.getPixelInt(i, i)[0]`. Any mismatch returns `fail` with the expected and actual values.

All-formats tests (`uniform_texel_buffer`, `storage_texel_buffer`, `uniform_storage_texel_buffer`), [BufferViewAllFormatsTestInstance](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L864-L1318):

- [checkTexelBufferSupport()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L912-L931) throws `NotSupportedError` if the format does not expose the required `VkFormatFeatureFlags` bit. For the dual-usage node, it also throws if `VK_KHR_maintenance5` is not supported.
- Source buffer of `bufferSize` bytes is created suballocated and host-visible at [L1019-L1023](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1019-L1023), filled by [populateSourceBuffer()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L938-L960). The buffer view is created with `offset = 0`, `range = VK_WHOLE_SIZE` at [L1025-L1047](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1025-L1047); for the dual-usage node, the bind usage is supplied through `VkBufferUsageFlags2CreateInfoKHR`.
- The compute pipeline binds a storage buffer (4 `vec4` slots) at binding 0 and the texel buffer view at binding 1, dispatches `(4, 1, 1)` workgroups at [L1144-L1177](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1144-L1177), with a host-to-compute barrier before dispatch and a compute-to-host barrier after.
- [iterate()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1261-L1273) submits, waits, and routes to [checkResult()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1193-L1225) for integer/unsigned formats or [checkResultFloat()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1227-L1259) for floating-point formats.
- Each check compares four `vec4` results against `m_sourceView.getPixel(Uint)(fetchPos)` for sample positions 6, 51, 42, 25. Integer paths use threshold 0; float paths use `1.0 / 255.0`. Any out-of-threshold result fails with the expected and actual values logged.
- [BufferViewAllFormatsTestCase::checkSupport()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1289-L1309) is the case-level support gate: it requires `VK_KHR_maintenance5` for `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR`, and requires `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT` for any case whose create usage includes storage texel buffer.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `suballocation` | Memory-test readback mismatch: the graphics or compute pipeline returned a diagonal pixel whose value did not equal `factor * (elementOffset + i)` for `R32_UINT` data on a suballocated buffer and image. |
| `dedicated_alloc` | Memory-test readback mismatch on a path where at least one of the buffer or image uses a dedicated allocation; same symptom as `suballocation`. |
| `uniform_texel_buffer` | All-formats readback mismatch: `texelFetch` on a uniform texel buffer returned a texel that did not match the source buffer at one of the four sample positions for at least one format. |
| `storage_texel_buffer` | All-formats readback mismatch: `imageLoad` on a storage texel buffer returned a texel that did not match the source buffer at one of the four sample positions for at least one filtered format. |
| `uniform_storage_texel_buffer` (`bind_as_uniform`, `bind_as_storage`) | Dual-usage bind mismatch: a buffer created with both uniform and storage texel buffer usages, bound through `VkBufferUsageFlags2CreateInfoKHR` with a usage that differs from the create usage, returned a texel that did not match the source buffer at one of the four sample positions. |

### Cause Analysis

#### Memory-test readback mismatch

**Possible failure symptoms:** the case returns `tcu::TestStatus::fail("BufferView test failed. expected: <expected> actual: <actual>")` produced at [L617-L620](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L617-L620). The mismatch is on a diagonal pixel `i` of the `R32_UINT` result image. The first pass with `factor = 1` may pass while the second pass with `factor = 2` fails, or vice versa, or both may fail.

**Possible implementation causes:** the test isolates buffer view reads from data generation and result copyback, so a mismatch points to one of four areas. Incorrect handling of `VkBufferViewCreateInfo::offset` or `range` is most likely to surface in `partial_offset1`, where `elementOffset = 128`. Incorrect texel indexing in the shader read path would affect every configuration for a given queue type. Stale data served on the second pass would indicate the buffer view caches contents instead of reflecting the rewritten buffer. A copy-image-to-buffer layout transition that drops or reorders pixels would surface as a diagonal mismatch even when the shader wrote the right value. The `dedicated_alloc` cases add the dedicated-allocation binding path; a failure that appears only under dedicated allocation and not under suballocation suggests the dedicated-allocation memory binding or image barrier handling diverges from the suballocated path. The test symptom alone does not identify whether the bug is in the buffer view servicing, the pipeline, or the copyback; source-level investigation of the failing allocation combination and configuration is needed to localize it.

#### All-formats readback mismatch

**Possible failure symptoms:** the case returns `tcu::TestStatus::fail("Invalid result values")` from [checkResult()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1224) or [checkResultFloat()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1258). The log message at [L1216-L1217](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1216-L1217) or [L1250-L1251](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1250-L1251) records the failing sample index (0-3), the expected `vec4`, and the actual `vec4`. The failing sample position is one of 6, 51, 42, or 25.

**Possible implementation causes:** the source pattern is generated host-side and copied in by `deMemcpy`, so the expected values are deterministic. A mismatch points to one of three areas. Incorrect format conversion when the buffer view serves texels to the shader: wrong channel ordering for packed formats, wrong scaling for `_SNORM`/`_UNORM`/`_USCALED`/`_SSCALED` formats, or wrong component count for `_A8_UNORM`/`_A1B5G5R5_*`. Incorrect storage-texel-buffer format support being reported, where a format advertises `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT` but the shader read path produces wrong values. Or a `texelFetch`/`imageLoad` implementation returning stale or zero data. A failure limited to the `storage_texel_buffer` node and not the `uniform_texel_buffer` node for the same format suggests the storage texel buffer read path diverges from the uniform path. A failure that appears only on float formats and exceeds the `1.0 / 255.0` tolerance suggests a conversion-precision issue rather than a data-routing issue.

#### Dual-usage bind readback mismatch

**Possible failure symptoms:** the case returns `tcu::TestStatus::fail("Invalid result values")` with the same log shape as the all-formats mismatch. The failing case is registered under `uniform_storage_texel_buffer.bind_as_uniform.<format>` or `uniform_storage_texel_buffer.bind_as_storage.<format>`, where the bind usage passed through `VkBufferUsageFlags2CreateInfoKHR` differs from the create usage on the buffer.

**Possible implementation causes:** the buffer is created with both `VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT` and `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT`. A failure that appears in `bind_as_storage` for a format that passes the single-usage `storage_texel_buffer` node (or in `bind_as_uniform` for a format that passes the single-usage `uniform_texel_buffer` node) suggests the implementation does not honor the `VkBufferUsageFlags2CreateInfoKHR::usage` field when servicing reads through the buffer view, and instead dispatches reads based on the buffer's create usage or on a fixed usage chosen at view creation time. A failure that appears only on a subset of formats may indicate the bind-usage override interacts with format-specific descriptor lowering. The test symptom alone does not identify whether the implementation ignores the bind usage entirely or dispatches to the wrong read path; source-level investigation of the driver's buffer view creation and descriptor binding is needed when this cause is suspected.

## Case Pruning

### Requirement-based pruning

- The `uniform_storage_texel_buffer` intermediate node and its `bind_as_uniform` / `bind_as_storage` children are built under `#ifndef CTS_USES_VULKANSC` at [L1553](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1553); they do not exist in Vulkan SC builds.
- `VK_KHR_maintenance5` is required for the dual-usage node. [checkTexelBufferSupport()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L925-L930) throws `NotSupportedError` if the extension is not supported.
- `VK_FORMAT_A8_UNORM_KHR` and `VK_FORMAT_A1B5G5R5_UNORM_PACK16_KHR` require `VK_KHR_maintenance5`. [BufferViewAllFormatsTestCase::checkSupport()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1294-L1298) throws `NotSupportedError` if the extension is missing.
- Any case whose create usage includes `VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT` requires `VK_FORMAT_FEATURE_STORAGE_TEXEL_BUFFER_BIT` for the format. [checkSupport()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1300-L1308) throws `NotSupportedError` if the bit is missing.
- All-formats cases also call [checkTexelBufferSupport()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L912-L931) at instance construction, which throws `NotSupportedError` if `properties.bufferFeatures & testCase.feature` is zero.

### Design-based pruning

- The `storage_texel_buffer` and `uniform_storage_texel_buffer.bind_as_storage` nodes skip formats that [isSupportedImageLoadStore()](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1383-L1433) rejects. The function keeps non-packed RGBA formats with FLOAT, HALF_FLOAT, *INT32/16/8, UNORM_INT16/8, SNORM_INT16/8 component types, plus the packed `VK_FORMAT_A2B10G10R10_UNORM_PACK32` and `VK_FORMAT_A2B10G10R10_UINT_PACK32`. Other packed and non-RGBA formats are intentionally excluded because GLSL `imageLoad` on `imageBuffer` requires a matching layout qualifier and these formats cannot be expressed.
- The memory tests are compute-or-graphics parameterized. The all-formats tests are compute-only because the format matrix is exercised through a single compute shader, avoiding a per-format graphics pipeline.
- The `suballocation` and `dedicated_alloc` nodes share the same `R32_UINT` format. Format coverage is delegated to the all-formats nodes; the memory tests focus on allocation kind, view offset, and queue type.

## Key Takeaways

- The test family isolates buffer view readback: shader logic is trivially simple, source data is deterministic, and the host comparison is exact (or within `1.0 / 255.0` for float formats). A failure means the implementation served the wrong texel through the buffer view.
- The `suballocation` and `dedicated_alloc` nodes share the same shader and readback logic; they differ only in allocation kind, so a divergence between them localizes the failure to the allocation or memory binding path.
- The `partial_offset1` configuration with `elementOffset = 128` is the only case that exercises a nonzero view offset. A failure limited to that configuration points to `VkBufferViewCreateInfo::offset` handling.
- The two-pass `factor = 1` then `factor = 2` re-run in the memory tests checks that the buffer view does not serve stale data when the underlying buffer is rewritten.
- The `uniform_storage_texel_buffer` node is the only place where bind usage is decoupled from create usage via `VkBufferUsageFlags2CreateInfoKHR`. A failure here that does not reproduce in the single-usage nodes suggests the bind-usage override is not honored.
- The `storage_texel_buffer` and `bind_as_storage` nodes use a strict format filter; missing support for a filtered format is reported through `NotSupportedError` and is not a failure of the test family itself.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createBufferViewAccessTests()` | [vktApiBufferViewAccessTests.cpp#L1435-L1607](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1435-L1607) | Owns the registration of all five intermediate nodes and their test case leaves. |
| `createBufferViewTests()` | [vktApiTests.cpp#L78-L84](../../../modules/vulkan/api/vktApiTests.cpp#L78-L84) | Parent dispatcher that attaches `createBufferViewAccessTests()` under the `buffer_view` group. |
| `buffer_view` group attachment | [vktApiTests.cpp#L106](../../../modules/vulkan/api/vktApiTests.cpp#L106) | Attaches the `buffer_view` group to the `api` test category. |
| `AllocationKind` enum | [vktApiBufferViewAccessTests.cpp#L61-L66](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L61-L66) | Defines the suballocated/dedicated allocation dimension. |
| `BufferViewCaseParams` struct | [vktApiBufferViewAccessTests.cpp#L68-L103](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L68-L103) | Carries buffer/view size, offset, allocation kinds, queue type, format, create/bind usage, feature flag, and descriptor type. |
| `BufferViewTestInstance` | [vktApiBufferViewAccessTests.cpp#L105-L806](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L105-L806) | Memory-test instance: builds graphics or compute pipeline, runs two-pass readback, scans the diagonal. |
| `BufferViewTestInstance::checkResult()` | [vktApiBufferViewAccessTests.cpp#L591-L624](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L591-L624) | Diagonal pixel check for the memory tests. |
| `BufferViewTestInstance::queuePass()` | [vktApiBufferViewAccessTests.cpp#L766-L806](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L766-L806) | Two-pass driver: `factor = 1` then `factor = 2`. |
| `BufferViewTestCase::initPrograms()` (memory tests) | [vktApiBufferViewAccessTests.cpp#L831-L862](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L831-L862) | Inlined vertex, fragment, and compute shaders for the memory tests. |
| `BufferViewAllFormatsTestInstance` | [vktApiBufferViewAccessTests.cpp#L864-L1318](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L864-L1318) | All-formats instance: populates source buffer, dispatches compute, reads back four samples. |
| `BufferViewAllFormatsTestInstance::populateSourceBuffer()` | [vktApiBufferViewAccessTests.cpp#L938-L960](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L938-L960) | Deterministic gradient pattern used as the source of truth for the all-formats check. |
| `BufferViewAllFormatsTestInstance::checkTexelBufferSupport()` | [vktApiBufferViewAccessTests.cpp#L912-L931](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L912-L931) | Instance-level support gate, including `VK_KHR_maintenance5` for the dual-usage node. |
| `VkBufferUsageFlags2CreateInfoKHR` chaining | [vktApiBufferViewAccessTests.cpp#L1035-L1045](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1035-L1045) | Where the dual-usage node sets the bind usage independently of the create usage. |
| `BufferViewAllFormatsTestInstance::checkResult()` | [vktApiBufferViewAccessTests.cpp#L1193-L1225](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1193-L1225) | Integer/unsigned format check with threshold 0. |
| `BufferViewAllFormatsTestInstance::checkResultFloat()` | [vktApiBufferViewAccessTests.cpp#L1227-L1259](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1227-L1259) | Float format check with `1.0 / 255.0` tolerance. |
| `BufferViewAllFormatsTestCase::checkSupport()` | [vktApiBufferViewAccessTests.cpp#L1289-L1309](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1289-L1309) | Case-level support gate, including `VK_KHR_maintenance5` for `A8_UNORM` and `A1B5G5R5_UNORM_PACK16`. |
| `BufferViewAllFormatsTestCase::initPrograms()` | [vktApiBufferViewAccessTests.cpp#L1329-L1379](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1329-L1379) | Generates the all-formats compute shader; switches between `texelFetch` on `textureBuffer` and `imageLoad` on `imageBuffer`. |
| `isSupportedImageLoadStore()` | [vktApiBufferViewAccessTests.cpp#L1383-L1433](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1383-L1433) | Format filter for the storage nodes. |
| Allocation loop for `suballocation`/`dedicated_alloc` | [vktApiBufferViewAccessTests.cpp#L1450-L1500](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1450-L1500) | Routes the four allocation-kind combinations to the correct intermediate node and registers the three size configurations. |
| `uniform_texel_buffer` / `storage_texel_buffer` registration | [vktApiBufferViewAccessTests.cpp#L1507-L1551](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1507-L1551) | Registers one leaf per format under each usage name. |
| `uniform_storage_texel_buffer` registration | [vktApiBufferViewAccessTests.cpp#L1553-L1604](../../../modules/vulkan/api/vktApiBufferViewAccessTests.cpp#L1553-L1604) | Vulkan SC-excluded node with `bind_as_uniform` and `bind_as_storage` children. |
| `formats::bufferViewAccessFormats` | [vkFormatLists.inl#L1394-L1503](../../../framework/vulkan/generated/vulkan/vkFormatLists.inl#L1394-L1503) | Canonical format matrix for the all-formats nodes. |
| Header | [vktApiBufferViewAccessTests.hpp](../../../modules/vulkan/api/vktApiBufferViewAccessTests.hpp#L1) | Declares `createBufferViewAccessTests()`. |
