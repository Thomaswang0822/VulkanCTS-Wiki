## Overview

**Core question:** Do multisampled-image rendering, access, ordering, and resolve paths preserve the expected per-sample behavior and final image values?

- This page documents the `pipeline.multisample` image-access intermediate nodes implemented by [`vktPipelineMultisampleImageTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1-L2988).
- The source is mixed implementation and registration code. It implements `sampled_image`, `storage_image`, `standardsampleposition`, `samples_mapping_order`, and `3d`, while [`createMultisampleTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7247-L8096) attaches those intermediate nodes below each multisample construction root.
- The direct intermediate node is the behavioral axis. Format, extent, layer count, sample count, and construction type broaden the coverage of its selected mechanism.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Multisampled image access.** A multisampled image holds separate samples at each pixel. [`VkPipelineMultisampleStateCreateInfo`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2188-L2200) sets rasterization sample state, and graphics-pipeline rules require compatible attachment and rasterization sample counts ([`rasterizationSamples`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3016-L3028)). A shader sample or fetch can address an individual image sample.
- **Storage-image feature and locations.** [`shaderStorageImageMultisample`](../../../../vulkan-docs/src/chapters/features.adoc#L577-L581) enables multisampled storage-image access. `standardsampleposition` relies on the physical-device `standardSampleLocations` limit, which the source checks before execution.
- **Host observation.** The source makes device-side results visible through a checksum image, resolved image, or storage buffer. CTS waits for the submission, invalidates the mapped allocation, and applies a behavior-specific comparison.

## Registration Hierarchy

```text
pipeline.monolithic.multisample
├── sampled_image
├── storage_image
├── standardsampleposition
├── samples_mapping_order
└── 3d
```

The same factories create the corresponding intermediate nodes under `pipeline.fast_linked_library.multisample`, `pipeline.pipeline_library.multisample`, shader-object roots, and `pipeline.multisample_with_fragment_shading_rate`. The mustpass scope contains 216 leaves in each of `monolithic/monolithic.txt`, `fast-linked-library.txt`, and `shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt`; it contains 210 leaves in each of `pipeline-library.txt`, `shader-object-linked-binary.txt`, `shader-object-linked-spirv.txt`, and `shader-object-unlinked-binary.txt`. The latter files omit the six `samples_mapping_order` leaves.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Intermediate node | `sampled_image`, `storage_image`, `standardsampleposition`, `samples_mapping_order`, `3d` | Selects the image-access or sample-identity mechanism and its validator. | [Factories](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2916-L2988) |
| 2D extent and layers | `64x64_1`, `64x64_4`, `79x31_1`, `79x31_4` | Exercises square and non-square images with one or four array layers in the sampled and storage paths. | [`addTestCasesWithFunctions()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2748-L2799) |
| 3D extent and layers | `64x64x8_1` | Uses the separate 3D-image setup. | [`addTestCasesWithFunctions3d()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2801-L2845) |
| Format | `r8g8b8a8_unorm`, `r32_uint`, `r16g16_sint`, `r32g32b32a32_sfloat`; position path also uses `r32g32b32a32_sfloat` | Changes the storage and comparison representation. | [2D matrix](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2763-L2799), [position matrix](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2847-L2885) |
| Sample count | `samples_2`, `samples_4`, `samples_8`, `samples_16`, `samples_32`, `samples_64` | Changes the number of per-pixel values the selected mechanism must handle. | [Common matrix](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2754-L2799) |
| Pipeline construction type | Supported construction variants | Repeats each C++ matrix through the pipeline registration framework. | [Parent registration](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7247-L8096) |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node below `pipeline.monolithic.multisample`. Each value selects a different image-access or sample-identity contract.

### `sampled_image`: sampled per-sample reads

This intermediate node renders values into a multisampled image, then samples its individual values in a fragment shader. CTS copies a checksum image to host memory and rejects any pixel that reports an unexpected sample color ([validation](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1356-L1391)).

### `storage_image`: storage-image load/store comparison

This intermediate node accesses a multisampled image through storage-image operations. The test produces two layered outputs and applies [`compareImages()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2074-L2139), which permits the source-defined integer-format error handling before declaring a mismatch.

### `standardsampleposition`: standard-location identity

This intermediate node renders colors tied to standard sample positions and checks a checksum of the result. The support path requires `standardSampleLocations`, and the validator fails when a checksum pixel records one or more unexpected sample colors ([support and validation](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2278-L2491)).

### `samples_mapping_order`: cross-fragment sample order

This intermediate node writes a sample-index-weighted value for each pixel through a compute shader. The host reads the storage buffer and requires every result after the first to equal the first within `0.001`, so it detects an inconsistent sample-index mapping ([validation](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2708-L2723)).

### `3d`: resolving into a 3D image

This intermediate node renders per-sample values into a multisampled 2D image, clears a single-sampled `64x64x8` 3D image to green, and resolves the 2D image into the first depth slice of the 3D image. CTS compares every destination slice with a host-generated reference using a per-component threshold of `0.01`: slice zero must contain the average-resolved colors and the other seven slices must retain the green clear color ([implementation](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1396-L1860)).

## Shader Analysis

The source generates vertex, fragment, and, for storage-image and mapping-order paths, compute GLSL programs. Shader behavior is central to this family, but the five intermediate nodes generate distinct artifacts and parameter specializations rather than one stable representative artifact. This page therefore documents each shader's role in the behavioral sections and runtime sequence without reproducing generated GLSL or SPIR-V.

## Runtime Execution and Result Checking

- The 2D paths use [`checkImageFormatRequirements()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L590-L608) to check sample-count and format support for the requested usage. It also rejects a storage-image usage when `shaderStorageImageMultisample` is unavailable. The `3d` path instead checks the multisampled 2D source and single-sampled 3D destination format support separately ([support check](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1440-L1473)).
- The selected path creates multisampled images and views, descriptor sets, graphics pipelines, and, where required, a host-visible checksum or storage buffer. The `samples_mapping_order` path submits a graphics pass, runs compute work over the multisample image, inserts a compute-to-host barrier, and reads the buffer after completion.
- `sampled_image` and `standardsampleposition` copy a checksum image to a buffer, wait, invalidate its allocation, and fail on a nonzero error result. `storage_image` copies and compares its layered images. `samples_mapping_order` checks all computed values against the first value. `3d` resolves into depth slice zero, copies the full 3D image to a host-visible buffer, and threshold-compares all eight slices with generated references.
- A failing final image identifies the selected behavior class, but its result cannot independently isolate image creation, rasterization, shader access, copyback, or comparison code. The source-level validators define the localization boundary.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `sampled_image` | Per-sample sampled-image read or sample-derived checksum does not match rendered data. |
| `storage_image` | Multisampled storage-image load/store behavior disagrees with the reference image path. |
| `standardsampleposition` | Rendered sample identity does not match the required standard sample positions. |
| `samples_mapping_order` | Sample indices do not map to a consistent order across fragments. |
| `3d` | Resolving a multisampled 2D image into the first slice of a single-sampled 3D image produces incorrect data or modifies another depth slice. |

### Cause Analysis

#### Per-sample sampled-image read or checksum mismatch

**Possible failure symptoms:** `sampled_image` reports `Some samples have incorrect color` or a checksum mismatch after CTS copies and reads the checksum image.

**Possible implementation causes:** The graphics or fragment stage may render, address, or sample a multisample image value incorrectly. Image layout transitions, descriptor image views, copyback, or checksum generation can produce the same observation. The final checksum classifies the path but source-level investigation is needed to localize the stage.

#### Multisampled storage-image comparison mismatch

**Possible failure symptoms:** `storage_image` reports `Rendered images are not correct` after `compareImages()` compares the layered outputs.

**Possible implementation causes:** A driver may mishandle multisampled storage-image loads or stores, format conversion, or the synchronization and transfer sequence that exposes either output. The comparison operates on final images, so it does not distinguish those causes without inspecting the recorded images and execution path.

#### Standard sample-position mismatch

**Possible failure symptoms:** `standardsampleposition` reports that one or more multisamples have an unexpected color.

**Possible implementation causes:** The implementation may use an incorrect standard sample location, associate a rendered value with the wrong sample identity, or mishandle the checksum readback. The source checks the advertised `standardSampleLocations` limit before execution, so an unsupported-location device should not reach this failure path.

#### Inconsistent sample-index mapping

**Possible failure symptoms:** `samples_mapping_order` reports the first storage-buffer index whose weighted sample value differs from the first pixel beyond the `0.001` tolerance.

**Possible implementation causes:** Sample indices may map to different physical samples across fragments, or the compute shader's multisample fetch path may read a value from the wrong index. The buffer comparison exposes inconsistent final values but cannot separate rasterization order from image fetch behavior.

#### 3D multisampled-image result mismatch

**Possible failure symptoms:** `3d` returns `Fail` when any component in any destination depth slice differs from its reference by more than `0.01`.

**Possible implementation causes:** The path may mishandle rendering the multisampled 2D source, resolving into depth slice zero of the 3D destination, preserving the cleared values in the other depth slices, or transferring the 3D image for host comparison. The result is a whole-path observation, so the source does not justify an exclusive stage diagnosis.

## Case Pruning

### Requirement-based pruning

- The 2D paths call [`checkImageFormatRequirements()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L590-L608) for the requested sample count, format, and image usage. The `3d` path has separate source and destination image-format queries and checks sample-count support on the multisampled 2D source.
- `storage_image` and `samples_mapping_order` require `shaderStorageImageMultisample`; `3d` does not use a multisampled storage image and does not require that feature.
- `standardsampleposition` requires the `standardSampleLocations` device limit. Pipeline construction requirements also filter variants that the device cannot construct.

### Design-based pruning

- The 2D matrix uses two extents, two layer counts, four formats, and six sample counts. The 3D path intentionally narrows this to one extent, one layer count, and one format because it targets 3D multisample access rather than the full 2D format matrix.
- `standardsampleposition` uses a `1x1` target and two formats because its validator focuses on individual standard sample locations. `samples_mapping_order` fixes the target at `16x16` and `VK_FORMAT_R8G8B8A8_UNORM` because it compares a uniform weighted ordering over pixels.
- Some mustpass construction files omit `samples_mapping_order`; this is registration coverage, not a relaxed validator for the registered leaves.

## Key Takeaways

- The source implements five direct `multisample` intermediate nodes with distinct observation and validation mechanisms.
- `sampled_image` and `storage_image` test shader image access; `3d` tests a resolve from a multisampled 2D source into one depth slice of a single-sampled 3D destination; `standardsampleposition` checks sample identity against standard positions; `samples_mapping_order` checks that identity remains ordered across fragments.
- The common parameter matrix expands coverage, while the direct intermediate node determines what CTS treats as the behavior under test.
- The final checksum, image, or buffer exposes a path-level fault class. It does not establish one exclusive Vulkan pipeline stage.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Format and feature support | [`checkImageFormatRequirements()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L590-L608) | Checks image properties and multisampled storage-image support. |
| Sampled-image path | [`SampledImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1081-L1394) | Implements generated shaders and checksum validation for `sampled_image`. |
| 3D path | [`Image3d`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1396-L1863) | Implements the 3D image case. |
| Storage-image path | [`StorageImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1865-L2211) | Implements storage-image access and image comparison. |
| Position and ordering paths | [`StandardSamplePosition` and `SamplesMappingOrder`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2213-L2725) | Implement standard-position and sample-order validators. |
| Matrix and factories | [`addTestCasesWithFunctions()` through `createMultisample3dImageTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L2748-L2988) | Builds the registered matrices and intermediate nodes. |
| Parent dispatcher | [`createMultisampleTests()`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7247-L8096) | Attaches these factories below multisample construction roots. |
| Vulkan multisample state | [`VkPipelineMultisampleStateCreateInfo`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2188-L2200) | Defines pipeline multisample state. |
| Multisampled storage-image feature | [`shaderStorageImageMultisample`](../../../../vulkan-docs/src/chapters/features.adoc#L577-L581) | Defines support for multisampled storage images. |
