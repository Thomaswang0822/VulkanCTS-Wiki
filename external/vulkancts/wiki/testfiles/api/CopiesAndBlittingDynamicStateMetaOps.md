## Overview

**Core question:** does interleaving a copy or blit meta-operation between two draws to a multisampled image, with rasterization samples set dynamically through `VK_EXT_extended_dynamic_state3`, corrupt either the meta-operation result or the multisampled image contents?

This page covers the `api.copy_and_blit.dynamic_state` test family, implemented in [`vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp). The family is non-VulkanSC only; the entire source file is guarded by `#ifndef CTS_USES_VULKANSC`.

The test family registers two intermediate nodes that each generate six test case leaves:

- `copy`: exercises `vkCmdCopyImage` (or `vkCmdCopyImage2`) on a separate source/destination image pair interleaved between two draws to a multisampled image.
- `blit`: exercises `vkCmdBlitImage` (or `vkCmdBlitImage2`) under the same interleaved draw, blit, draw sequence.

Each test case leaf is named `draw_multisampled_image_r8g8b8a8_unorm_samples_<N>`, where `<N>` is one of `2`, `4`, `8`, `16`, `32`, `64`. The multisampled image and the copy/blit source and destination images all use `VK_FORMAT_R8G8B8A8_UNORM`.

## Background Knowledge

- `VK_EXT_extended_dynamic_state3` with the `extendedDynamicState3RasterizationSamples` feature allows the rasterization sample count to be set per-command-buffer via `vkCmdSetRasterizationSamplesEXT` instead of being baked into the pipeline's `VkPipelineMultisampleStateCreateInfo`. This test relies on that dynamic state to set the multisampled image's sample count at draw time.
- `VK_ATTACHMENT_LOAD_OP_LOAD` preserves the existing contents of a color attachment at the start of a subpass, instead of clearing it. The test uses load op `LOAD` on the multisampled color attachment so that the second draw continues writing into image contents that the first draw produced. Without `LOAD`, the second draw would overwrite cleared contents and the test could not detect meta-operation corruption of pre-existing samples.
- `gl_SampleID` in a fragment shader identifies the sample index currently being shaded for a multisampled attachment. The test fragment shader writes a per-sample color pattern that differs by `gl_SampleID` and by draw index, so that corruption of any single sample is observable as a changed value.
- A Vulkan input attachment (`subpassInputMS` in GLSL) lets a fragment shader read the multisampled color attachment at the same pixel coordinate without going through a normal sampler. The verification pass uses a multisampled input attachment to read back each sample and compare it against the value the draw shader should have written.

## Registration Hierarchy

```text
api.copy_and_blit.dynamic_state
├── copy
└── blit
```

The `dynamic_state` group is created by [`createDynamicStateMetaOperationsTests()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1402) and added under `copy_and_blit` in [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L285). The two intermediate nodes `copy` and `blit` are added in the loop at [line 1483 through line 1507](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1483-L1507). Each intermediate node generates six test case leaves, one per sample count, in the inner loop at [line 1489 through line 1503](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1489-L1503).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Meta operation | `copy`, `blit` | Intermediate node directly below `dynamic_state`. Selects whether the meta-operation is a whole-image `vkCmdCopyImage` or `vkCmdBlitImage`. | [L1475](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1475) |
| Multisampled image format | `VK_FORMAT_R8G8B8A8_UNORM` | Format of the multisampled color attachment that the dynamic-state draw targets and the verification pass reads back as an input attachment. | [L1476](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1476) |
| Sample count | `2`, `4`, `8`, `16`, `32`, `64` | Number of samples per pixel in the multisampled image. Set dynamically via `vkCmdSetRasterizationSamplesEXT` rather than through pipeline creation. Drives the test case leaf name suffix `samples_<N>`. | [L1478-L1481](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1478-L1481) |
| Copy/blit image format | `VK_FORMAT_R8G8B8A8_UNORM` | Format of the separate source and destination images used by the copy or blit meta-operation. Constrained by `DE_ASSERT` to equal the source format. | [L1409](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1409), [L1415](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1415) |
| Copy/blit image type | `VK_IMAGE_TYPE_2D` | Image type of source and destination. Fixed by `DE_ASSERT`. | [L1408](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1408), [L1414](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1414) |
| Copy/blit image tiling | `VK_IMAGE_TILING_OPTIMAL` | Tiling of source and destination images. Fixed by `DE_ASSERT`. | [L1411](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1411), [L1417](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1417) |
| Copy/blit image extent | `defaultExtent` (64×64×1) | Whole-image region copied or blitted. Source and destination share the same extent. | [L1410](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1410), [L1416](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1416) |
| Allocation kind | `ALLOCATION_KIND_SUBALLOCATED` | Memory allocation mode for all images. Fixed by `DE_ASSERT`. | [L1420](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1420) |

## Behavior Parameters

The primary behavioral axis is the intermediate node below `dynamic_state`. Each value changes which meta-operation runs between the two draws to the multisampled image.

### `copy`: Whole-image copy interleaved with multisampled draws

The test sequence is: draw to the multisampled image, execute `vkCmdCopyImage` (or `vkCmdCopyImage2` when `COPY_COMMANDS_2` is set) on a separate single-sampled source/destination image pair, then draw to the multisampled image again. The copy uses one whole-image `VkImageCopy` region covering the full 64×64 extent. Verification compares the destination image against a host-computed reference using `tcu::bitwiseCompare`, treating `vkCmdCopyImage` as a memcpy of pixel data. The test case class is [`DynamicStateMetaOpsTestCase`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1187); the instance class is [`DynamicStateMetaOpsInstance`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L55).

### `blit`: Whole-image blit interleaved with multisampled draws

The sequence is identical to `copy`, but the meta-operation is `vkCmdBlitImage` (or `vkCmdBlitImage2`) with a 1:1 whole-image `VkImageBlit` region. There is no scaling or mirroring. Verification uses nearest-filtered comparison via [`checkNearestFilteredResult`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L173), which dispatches to `intNearestBlitCompare` for integer-format channel classes or `floatNearestBlitCompare` for float/fixed-point formats. Because both source and destination are `VK_FORMAT_R8G8B8A8_UNORM`, the float path applies format-specific thresholds. The blit parameters are configured in [`blitParams`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1438-L1468).

## Shader Analysis

Shader code is not part of the tested behavior. The vertex, fragment, and fragment-verification shaders are test infrastructure: the fragment shader writes a per-sample pattern into the multisampled image so that corruption is observable, and the verification fragment shader reads the multisampled image back as an input attachment and writes both actual and expected values to storage buffers for host comparison. No `### Representative Shader Walkthrough` subsection is created.

## Runtime Execution and Result Checking

The instance entry point is [`DynamicStateMetaOpsInstance::iterate()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1141).

[host] Allocate three images: a single-sampled source image (`m_source`), a single-sampled destination image (`m_destination`), and a multisampled color attachment (`m_multisampledImage`) with the test's sample count. Source and destination are created with `VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT`; the multisampled image adds `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT` ([line 96 through line 170](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L96-L170)).

[host] Initialize the source and destination images with `FILL_MODE_RED` and `FILL_MODE_BLACK` respectively, and compute the expected destination contents from the source via [`copyRegionToTextureLevel`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L248) ([line 906 through line 934](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L906-L934)).

[host] Build the draw pipeline: vertex shader passes through positions, fragment shader uses `gl_SampleID` to write a per-sample color on even samples for `drawCount == 0` and on odd samples for `drawCount != 0`. The pipeline uses `VK_DYNAMIC_STATE_RASTERIZATION_SAMPLES_EXT` and a render pass with `VK_ATTACHMENT_LOAD_OP_LOAD` on the multisampled color attachment ([line 322 through line 518](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L322-L518)).

[host] Begin command buffer.

[device] First draw (`drawCount = 0`): transition the multisampled image to `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL`, clear it to red, transition to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL`, begin render pass, call `vkCmdSetRasterizationSamplesEXT` with the test's sample count, draw a full-screen triangle strip, end render pass, transition the multisampled image to `VK_IMAGE_LAYOUT_GENERAL` ([line 520 through line 619](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L520-L619)).

[device] Meta-operation: transition the source and destination images to their operation layouts, then call `vkCmdCopyImage`/`vkCmdCopyImage2` for the `copy` intermediate node or `vkCmdBlitImage`/`vkCmdBlitImage2` for the `blit` intermediate node. The meta-operation acts only on the separate source/destination images; it does not touch the multisampled image ([line 936 through line 1132](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L936-L1132)).

[device] Second draw (`drawCount = 1`): transition the multisampled image back to `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` with `VK_ACCESS_COLOR_ATTACHMENT_READ_BIT | VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT` so that load op `LOAD` preserves the first draw's contents, begin render pass, draw again. The fragment shader now writes to the complementary set of samples (odd samples for `drawCount != 0`), leaving the first draw's samples intact ([line 585 through line 619](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L585-L619)).

[host] End command buffer and submit with `submitCommandsAndWait` ([line 1172 through line 1173](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1172-L1173)).

[host] Verify the meta-operation result by reading back the destination image and comparing against the expected texture level. For `copy`, [`checkTestResult`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L231) calls `tcu::bitwiseCompare`. For `blit`, it calls [`checkNearestFilteredResult`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L173) with nearest filtering and format-specific thresholds. If the meta-operation check fails, the test returns the failure immediately without running the draw verification ([line 1176 through line 1178](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1176-L1178)).

[host] Verify the multisampled image integrity via [`verifyDraws()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L621). This builds a second render pass that uses the multisampled image as an input attachment, binds a `fragVerify` fragment shader that reads each sample with `subpassLoad(msImageAtt, s)` and writes both the actual value and the host-computed expected value to two storage buffers, draws a full-screen pass with `VK_SAMPLE_COUNT_1_BIT`, and copies the results back to host-visible memory. The host then iterates every pixel and sample, computes `abs(expected - actual)`, and checks `boolAll(lessThanEqual(diff, tcu::Vec4(0.01f)))` at [line 891](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L891). On mismatch, the test logs the coordinates, sample index, actual value, and expected value, and returns `fail` ([line 893 through line 899](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L893-L899)).

Pass condition: the meta-operation destination matches the expected reference, and every sample of the multisampled image matches its expected value within the 0.01 tolerance.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `copy` | Copy destination mismatch; meta-operation interfered with the multisampled image contents; dynamic rasterization samples not applied on the second draw |
| `blit` | Blit destination mismatch (nearest-filtered); meta-operation interfered with the multisampled image contents; dynamic rasterization samples not applied on the second draw |

Both intermediate nodes share the multisampled-image integrity check. A failure of that check points to the same set of underlying causes regardless of whether the meta-operation was `copy` or `blit`.

### Cause Analysis

#### Copy destination mismatch

**Possible failure symptoms:** [`checkTestResult`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L231) returns `tcu::TestStatus::fail("Copy test")` after `tcu::bitwiseCompare` reports a mismatch between `m_expectedTextureLevel[0]` and the readback of `m_destination`. The comparison log includes the result and reference images on error.

**Possible implementation causes:** the destination image's pixels differ from the source image's pixels after `vkCmdCopyImage` (or `vkCmdCopyImage2`). Spec-level causes include incorrect layout transition barriers around the copy, failure to honor `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` or `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` for the source or destination, or a copy that writes the wrong region. Because `vkCmdCopyImage` is specified as a memcpy of pixel data when source and destination formats match, any deviation in the destination bytes indicates a copy-path defect. Source-level investigation would be needed to confirm whether the failure is in the copy command itself or in the surrounding layout transitions.

#### Blit destination mismatch

**Possible failure symptoms:** [`checkTestResult`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L231) returns `tcu::TestStatus::fail("Blit test")` after [`checkNearestFilteredResult`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L173) returns false. The test logs a `Compare` image set containing the result and an error mask that marks mismatched pixels in red.

**Possible implementation causes:** the destination image's pixels differ from the nearest-filtered source pixels after `vkCmdBlitImage` (or `vkCmdBlitImage2`). Because this test uses a 1:1 whole-image blit with no scaling or mirroring, every destination pixel should equal the corresponding source pixel within the format-specific float threshold. Spec-level causes include incorrect nearest-filter sampling, incorrect blit region handling, or layout transition faults around the blit. The blit path also requires `VK_FORMAT_FEATURE_BLIT_SRC_BIT` on the source format and `VK_FORMAT_FEATURE_BLIT_DST_BIT` on the destination format; these are checked in `checkSupport` before the case runs, so a missing feature bit skips rather than fails.

#### Multisampled image sample corruption

**Possible failure symptoms:** [`verifyDraws()`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L621) returns `tcu::TestStatus::fail` with a message of the form `Verification failed for coordinates (X, Y) sample S output: <actual> expected: <expected>`. The failure is reported per-sample, and the host loop stops at the first mismatched sample.

**Possible implementation causes:** the multisampled image's sample contents after the second draw differ from the values the fragment shader should have written. Because the first draw writes to even samples and the second draw writes to odd samples with load op `LOAD` preserving the first draw's contents, a corrupted even sample after the second draw points to the meta-operation or the surrounding layout transitions having modified the multisampled image. Spec-level causes include: the implementation did not preserve the multisampled image contents across the meta-operation's barriers; the implementation did not honor the dynamic rasterization samples state set on the first draw during the second draw, using a different sample count; the render pass load op `LOAD` did not load the existing contents; or the input-attachment read in the verification pass returned stale or wrong-sample data. The 0.01 tolerance absorbs floating-point rounding in the per-sample color computation; a failure beyond that tolerance indicates a substantive sample-value corruption rather than rounding noise. Source-level investigation would be needed to confirm which path applies to a specific failing case.

## Case Pruning

### Requirement-based pruning

- The whole test family is non-VulkanSC only. The source file is guarded by `#ifndef CTS_USES_VULKANSC`, and the dispatcher in [`vktApiCopiesAndBlittingTests.cpp`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L286) registers the family only on non-SC builds.
- `VK_EXT_extended_dynamic_state3` with the `extendedDynamicState3RasterizationSamples` feature is required. Cases skip with `NotSupportedError` when the feature is missing ([line 1217 through line 1218](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1217-L1218)).
- `VK_KHR_dynamic_rendering` is required ([line 1224](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1224)).
- The source and destination formats must support `VK_FORMAT_FEATURE_TRANSFER_SRC_BIT` and `VK_FORMAT_FEATURE_TRANSFER_DST_BIT` respectively. Cases skip when `getPhysicalDeviceImageFormatProperties` returns `VK_ERROR_FORMAT_NOT_SUPPORTED` ([line 1227 through line 1241](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1227-L1241)).
- For the `blit` intermediate node only, the source format must support `VK_FORMAT_FEATURE_BLIT_SRC_BIT` and the destination format must support `VK_FORMAT_FEATURE_BLIT_DST_BIT`. Cases skip when either bit is missing ([line 1243 through line 1266](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1243-L1266)).
- The multisampled image format and sample count must be supported. The case queries `getPhysicalDeviceImageFormatProperties` with the multisampled image's usage flags and skips when the requested sample count bit is not set in `sampleCounts` ([line 1289 through line 1311](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1289-L1311)).
- Image dimensions must not exceed `limits.maxImageDimension2D` ([line 1270 through line 1287](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1270-L1287)).

### Design-based pruning

- Only `VK_FORMAT_R8G8B8A8_UNORM` is used for both the multisampled image and the copy/blit source and destination. Other formats are not tested in this file ([line 1476](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1476)).
- The copy uses a single whole-image `VkImageCopy` region. Partial copies, multi-region copies, and 3D-to-2D-array copies are not tested ([line 1424 through line 1430](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1424-L1430)).
- The blit uses a single whole-image 1:1 `VkImageBlit` region with no scaling or mirroring. Filter mode is fixed by `m_params.filter` ([line 1456 through line 1462](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1456-L1462)).
- Several `DE_ASSERT` constraints in the test case constructor fix dimensions to defaults: source and destination formats must match, image type must be 2D, tiling must be optimal, allocation must be suballocated, `samples` must be `VK_SAMPLE_COUNT_1_BIT` for the copy/blit images, and `useGeneralLayout` must be false ([line 1196 through line 1207](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1196-L1207)).
- The multisampled image is separate from the copy/blit source and destination images. The test does not copy from or to the multisampled image itself.
- The `vert`, `frag`, and `fragVerify` shaders are fixed strings generated in [`initPrograms`](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1314); there is no shader permutation matrix.

## Key Takeaways

- The test interleaves a copy or blit meta-operation between two draws to a multisampled image whose sample count is set dynamically through `VK_EXT_extended_dynamic_state3`. The meta-operation acts on a separate source/destination pair; it must not disturb the multisampled image's contents.
- The fragment shader writes a per-sample pattern keyed on `gl_SampleID` and draw index, and load op `LOAD` preserves the first draw's samples across the second draw. This makes per-sample corruption observable as a value mismatch during the verification pass.
- Verification is split: the meta-operation destination is checked with a bitwise compare (`copy`) or a nearest-filtered compare (`blit`), and the multisampled image is checked independently through a second render pass that reads each sample as an input attachment and writes actual and expected values to storage buffers for a host-side comparison with a 0.01 tolerance.
- Sample counts 2 through 64 are exercised; cases skip when the implementation does not support the requested sample count for the multisampled image's format and usage.
- The `copy` and `blit` intermediate nodes share the multisampled-image integrity check, so a corruption failure points to the same underlying causes regardless of which meta-operation was used.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createDynamicStateMetaOperationsTests()` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1402](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1402) | Builds the `dynamic_state` group tree with `copy` and `blit` intermediate nodes. |
| `metaOpsParams` and sample-count loop | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1470-L1507](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1470-L1507) | Generates the 12 test case leaves (2 meta-operations × 6 sample counts). |
| `DynamicStateMetaOpsInstance` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L55](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L55) | Instance class: image creation, draw, copy/blit, and both verification paths. |
| `DynamicStateMetaOpsInstance::iterate()` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1141](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1141) | End-to-end command buffer sequence: draw → meta-operation → draw → verify. |
| `DynamicStateMetaOpsInstance::doDraw()` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L520](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L520) | Per-draw barriers, `vkCmdSetRasterizationSamplesEXT`, render pass begin/end. |
| `DynamicStateMetaOpsInstance::doCopy()` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L936](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L936) | `vkCmdCopyImage` / `vkCmdCopyImage2` execution and barriers. |
| `DynamicStateMetaOpsInstance::doBlit()` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1042](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1042) | `vkCmdBlitImage` / `vkCmdBlitImage2` execution and barriers. |
| `DynamicStateMetaOpsInstance::verifyDraws()` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L621](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L621) | Second render pass with `fragVerify`, input-attachment readback, host-side sample comparison. |
| `DynamicStateMetaOpsInstance::checkTestResult()` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L231](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L231) | Meta-operation result check: `tcu::bitwiseCompare` for copy, `checkNearestFilteredResult` for blit. |
| `DynamicStateMetaOpsTestCase::checkSupport` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1214](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1214) | Feature, format, sample-count, and limit support gates. |
| `DynamicStateMetaOpsTestCase::initPrograms` | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1314](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.cpp#L1314) | Generates `vert`, `frag`, and `fragVerify` GLSL sources. |
| Parent registration | [vktApiCopiesAndBlittingTests.cpp#L285](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L285) | Adds `dynamic_state` under `copy_and_blit`. |
| Header | [vktApiCopiesAndBlittingDynamicStateMetaOpsTests.hpp](../../../modules/vulkan/api/vktApiCopiesAndBlittingDynamicStateMetaOpsTests.hpp) | Public entry point exported from this translation unit. |
