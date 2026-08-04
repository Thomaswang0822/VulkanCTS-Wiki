## Overview

**Core question:** Does pipeline depth state produce the expected attachment contents across formats, render configurations, and queue/layout transitions?

- This page describes the `pipeline.<construction type>.depth` test family implemented by [`vktPipelineDepthTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L65-L2885).
- The family tests fixed-function depth and depth/stencil behavior, rather than shader algorithms. It combines generated format and compare-state cases with focused tests for absent depth attachments, depth clip control, transfer queues, and depth-only passes.
- The implementation compares rendered attachments against a software reference or a fixed expected image, so each failure reports an observable result mismatch.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- **Fragment depth operations.** Vulkan can apply depth bounds, stencil, and depth tests during fragment operations; comparison and write-enable state control whether a fragment affects the depth/stencil attachment. [Fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-depth) defines the relevant sequence and state.
- **Depth/stencil aspects.** A depth/stencil image can have depth, stencil, or both aspects. A combined format can need distinct aspect layouts, while transfer and attachment access require compatible layouts and synchronization. [Formats](../../../../vulkan-docs/src/chapters/formats.adoc) specifies format capabilities.

## Registration Hierarchy

```text
pipeline.monolithic.depth
├── format_features
├── format
├── nocolor
├── no_depth_attachment
├── depth_clip_control
├── xfer_queue_layout
└── depth_only
```

[`createDepthTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2515-L2885) creates the same `depth` test family beneath each applicable pipeline-construction root. The direct children are intermediate nodes below the `depth` test family. `format_features` and `xfer_queue_layout` are monolithic-only. `format` and `nocolor` appear only when `genFormatTests` permits them. `depth_only` is registered for monolithic, fast linked library, and shader-object unlinked SPIR-V construction.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Depth/stencil format | `D16_UNORM`, `X8_D24_UNORM_PACK32`, `D32_SFLOAT`, `D16_UNORM_S8_UINT`, `D24_UNORM_S8_UINT`, `D32_SFLOAT_S8_UINT` | Changes attachment representation and combined-aspect availability. | [format loop](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2647-L2665) |
| Depth compare-op tuple | 72 four-quad tuples from `depthOps` | Provides pair-wise coverage of compare operators across four independently drawn quads. | [`depthOps`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2521-L2602) |
| Primitive topology | `POINT_LIST`, `LINE_LIST`, `TRIANGLE_LIST` | Changes rasterization input used by generated general depth cases. | [topology array](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2604-L2607) |
| Color attachment | `true`, `false` | Separates the `format` and `nocolor` intermediate nodes. | [color loop](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2638-L2761) |
| Separate depth/stencil layouts | `false`, `true` for combined formats | Exercises separate aspect layouts where a format has both depth and stencil components. | [separate-layout loop](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2649-L2665) |
| Depth bounds | disabled; enabled with `0.1` to `0.25`; the special `never_zerodepthbounds_depthdisabled_stencilenabled` case uses `0.0` to `0.0` | Adds a depth-bounds condition to generated comparison cases and exercises the zero-bounds, depth-disabled, stencil-enabled state combination. | [case construction](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2674-L2705) |
| Depth clip control | `NORMAL`, `NORMAL_W`, `BEFORE_STATIC`, `BEFORE_DYNAMIC`, `BEFORE_TWO_DYNAMICS`, `AFTER_DYNAMIC` | Changes viewport depth-range and dynamic-state ordering. | [clip-control cases](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2784-L2817) |
| Transfer aspect | `DEPTH_BIT`, `STENCIL_BIT`, `DEPTH_BIT|STENCIL_BIT` | Selects which depth/stencil aspect the transfer-queue case clears, copies, and verifies. | [`aspectCases`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2820-L2843) |
| Depth-only mode | `SEPARATE_RENDER_PASSES`, `SUBPASSES`, `DYNAMIC_RENDERING`; prepass/postpass; optional `add_view_index` | Changes the rendering boundary and whether the depth-only draw happens before or after the color draw. | [depth-only registration](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2845-L2883) |

## Behavior Parameters

The primary behavioral axis is the intermediate test branch. Each branch changes the property that the test family observes.

### `format` and `nocolor` - general depth-state rendering

These branches render four regions with generated compare-op tuples, formats, topology, optional depth bounds, and optional separate layouts. `format` binds a color attachment, while `nocolor` omits it. The test can therefore compare depth behavior with and without a color target. One special case enables stencil testing with `VK_COMPARE_OP_NEVER` and keep operations to exercise that pipeline-state combination. It observes stencil rejection indirectly through the color and depth results; the general validator does not read back the stencil plane.

### `no_depth_attachment` - depth bounds without an attachment

This branch enables depth bounds but binds `VK_FORMAT_UNDEFINED` and no depth attachment. The expected rendering behavior is a no-op depth-bounds test in this configuration; the test case is `depth_bound_test`. [The registration](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2763-L2782) fixes that state.

### `depth_clip_control` - viewport depth-range state

These cases require `VK_EXT_depth_clip_control` and exercise static and dynamic viewport ordering, including an alternate `w` value. They use `ALWAYS` and `LESS` comparisons for every quad to expose incorrect handling of the `negativeOneToOne` viewport range.

### `xfer_queue_layout` - depth/stencil aspect transitions

This monolithic-only branch uses a transfer queue and validates `depth`, `stencil`, and combined-aspect variants. It checks that selected aspects survive transfer clears/copies, transitions into depth/stencil attachment use, rendering, and later readback.

### `depth_only` - depth pre-pass and post-pass persistence

These cases establish one depth region, then draw a second region at another depth. Separate render passes, subpasses, and dynamic rendering vary the rendering boundary. In a pre-pass, the second draw passes only on the right; in a post-pass, the first color draw occupies the left and the later depth-only draw preserves the expected depth split. [The source description](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1623-L1641) defines the expected regions.

### `format_features` - mandatory format support

This monolithic-only branch checks `D16_UNORM` directly and checks that at least one format in each required depth-only and depth/stencil candidate pair supports depth/stencil attachment use. [The cases](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2612-L2635) use physical-device format properties.

## Shader Analysis

Shader code is not the behavior under test. The ordinary depth cases use a vertex shader that forwards position and an optional fragment shader that forwards color; fixed-function pipeline state performs depth, bounds, and stencil operations. [`DepthTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L307-L343) shows these supporting programs. The depth-only vertex shader supplies a chosen depth through position and push constants, but the test observes attachment behavior rather than shader computation. No representative shader walkthrough or SPIR-V artifact is needed.

## Runtime Execution and Result Checking

- `DepthTest::checkSupport()` requires the core depth-bounds feature when enabled, verifies depth/stencil attachment format support when an attachment is bound, checks `VK_KHR_separate_depth_stencil_layouts` when requested, and requires `VK_EXT_depth_clip_control` for clip-control cases. [Support checks](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L275-L296) also enforce the selected pipeline construction type.
- General cases create attachments and pipelines, draw each quad, submit the universal queue, and wait. [`DepthTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1017-L1025) then calls `verifyImage()`.
- `verifyImage()` configures `ReferenceRenderer` with the same depth state and draws the same quad geometry. It reads the optional color attachment with a small integer and position tolerance, reads the depth attachment when present, converts reference depth formats as needed, and performs a depth threshold comparison. The general path does not independently compare a stencil plane, even though one special case enables stencil state. [Reference setup, readback, and comparison](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1028-L1155) provide the comparison path.
- `xfer_queue_layout` first requires a transfer queue, chooses a combined format with depth/stencil attachment and transfer-source capability, and creates normal and staging depth/stencil images. [Transfer setup](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1254-L1326) makes the aspect-specific ownership visible.
- `depth_only` uses an `8x8` `D16_UNORM` depth image and an `R8G8B8A8_UNORM` color image. Its host check compares color with zero threshold and depth with `0.000025`, then fails if either comparison fails. [Final comparisons](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2498-L2510) define the pass condition.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `format` and `nocolor` | Incorrect fixed-function depth/bounds/stencil behavior, attachment handling, or reference-visible output. |
| `no_depth_attachment` | Depth-bounds state incorrectly affects rendering without a bound depth attachment. |
| `depth_clip_control` | Incorrect `VK_EXT_depth_clip_control` viewport depth-range or dynamic-state behavior. |
| `xfer_queue_layout` | Incorrect depth/stencil aspect layout transition, transfer-queue synchronization, clear, copy, or attachment reuse. |
| `depth_only` | Incorrect depth persistence or comparison across depth-only and color passes, subpasses, or dynamic rendering. |
| `format_features` | Required depth/stencil attachment format support is absent or reported incorrectly. |

### Cause Analysis

#### Fixed-function depth, bounds, stencil, or attachment behavior

**Possible failure symptoms:** The color or depth readback differs from the software reference in a `format` or `nocolor` case. A color-free case can only expose the depth result that the test reads.

**Possible implementation causes:** Source-level investigation is needed to localize a mismatch. The observed state covers compare operations, bounds, attachment format handling, optional separate layouts, and rasterized geometry; Vulkan fragment-operation rules constrain their combined result.

#### No-depth-attachment depth-bounds behavior

**Possible failure symptoms:** `no_depth_attachment.depth_bound_test` produces an unexpected rendered result while no depth attachment is bound.

**Possible implementation causes:** The implementation may apply depth-bounds state where the attachment-less configuration should not produce the tested depth effect. The single case cannot isolate pipeline-state setup from fragment-operation handling.

#### Depth clip control state

**Possible failure symptoms:** A `depth_clip_control` case differs from the reference after a static or dynamic viewport sequence, or only the `_different_w` case fails.

**Possible implementation causes:** Source-level investigation should examine the extension state chained into pipeline viewport state and dynamic viewport commands. The branch changes `negativeOneToOne` use and command ordering, so the failure may involve either static pipeline state or dynamic-state replacement.

#### Transfer-queue depth/stencil aspect transition

**Possible failure symptoms:** The checked depth, stencil, or combined aspect differs after transfer and attachment use.

**Possible implementation causes:** The failure may involve aspect selection, image layout transitions, queue-family synchronization, transfer clear/copy behavior, or later attachment reuse. The final image cannot isolate one operation without examining the command log and aspect-specific readback.

#### Depth-only pass persistence

**Possible failure symptoms:** The color and/or depth image differs from the fixed left/right reference for a pre-pass, post-pass, rendering-boundary, or multiview variant.

**Possible implementation causes:** Source-level investigation should check depth attachment load/store behavior, depth comparison and writes, and preservation across the selected render-pass, subpass, or dynamic-rendering boundary. The expected split requires the earlier `0.0` depth and later `0.5` depth to remain distinct.

#### Required format support reporting

**Possible failure symptoms:** `format_features` reports that `D16_UNORM` or both alternatives in a required candidate set lack `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`.

**Possible implementation causes:** Physical-device format-property reporting may be incorrect, or the implementation may not provide a capability that the CTS case requires. The test reads format properties directly through the instance interface.

## Case Pruning

### Requirement-based pruning

- Depth-bounds cases require `DEVICE_CORE_FEATURE_DEPTH_BOUNDS`; separate-layout cases require `VK_KHR_separate_depth_stencil_layouts`; clip-control cases require `VK_EXT_depth_clip_control`.
- `xfer_queue_layout` skips when the device has no transfer queue. `depth_only.dynamic_rendering` requires `VK_KHR_dynamic_rendering`.
- A bound depth attachment must expose `VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT`.

### Design-based pruning

- Separate depth/stencil layouts are generated only for formats that contain both aspects.
- General-layout depth-bounds variants are generated only when `(formatNdx + opsNdx) % 10 == 0`, which samples that layout path without multiplying the full matrix.
- The 72 compare-op tuples supply pair-wise coverage instead of exhaustive four-quad permutations.
- Shader-object construction omits `no_depth_attachment` and the separate-render-pass/subpass depth-only modes. Vulkan SC omits clip-control and dynamic-rendering registration where the source excludes them.

## Key Takeaways

- The `depth` test family treats depth/stencil attachment contents as the primary observable result, with color output available for selected branches.
- Generated `format` and `nocolor` cases combine format, topology, comparison, bounds, and layout coverage, while the other intermediate nodes isolate attachment absence, viewport range, queue transitions, depth-only persistence, and format requirements.
- The fixed-function depth path, not the simple supporting shaders, is the central behavior under test.
- A failure means an observed attachment or capability mismatch; `Failure Meaning` classifies the tested operation shape but does not claim a unique defect location.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Depth test support and program setup | [`DepthTest::checkSupport()` and `initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L275-L343) | Defines feature gates and shows that shaders only pass positions/colors through. |
| General draw and reference validation | [`DepthTestInstance::iterate()` and `verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1017-L1118) | Submits rendering, builds the matching reference, and reads attachments. |
| Transfer-queue case | [`transferLayoutChangeSupportCheck()` and `transferLayoutChangeTest()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1254-L1326) | Defines transfer-queue availability and aspect-specific image setup. |
| Depth-only modes and expected output | [depth-only setup](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1623-L1759) and [final comparison](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2498-L2510) | Documents the left/right depth result, generated shaders, and thresholds. |
| Registration | [`createDepthTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2515-L2885) | Registers direct intermediate nodes, matrix values, and construction-type predicates. |
| Vulkan fragment operations | [depth tests and depth/stencil state](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-depth) | Normative context for the tested fixed-function operations. |
