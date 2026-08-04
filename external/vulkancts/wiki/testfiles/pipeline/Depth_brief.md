# Understanding Brief: `pipeline.depth`

## One-Sentence Test Purpose

This test family checks whether pipeline depth and depth/stencil attachment state produce the expected depth, stencil, and color results across format, attachment, layout, queue, and rendering-mode variations.

## Background Knowledge

### Fragment depth operations

After rasterization, Vulkan can apply depth bounds, stencil, and depth tests to a fragment. A depth comparison can reject a fragment before its color and depth updates take effect; a depth write is separately controlled by pipeline state. The specification describes the ordering and state controlled by `VkPipelineDepthStencilStateCreateInfo` in [fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-depth).

Why it matters here:

- The `format` and `nocolor` branches vary comparison state and use the resulting attachments as the observable output.
- `depth_only` makes an earlier depth write determine which region a later draw can update.

### Depth/stencil images and layouts

A depth/stencil image may expose depth, stencil, or both aspects. Attachment use requires an appropriate depth/stencil attachment format feature, and operations that transfer or read an aspect need layouts and synchronization compatible with that use. The format feature and depth/stencil attachment rules are specified in [formats](../../../../vulkan-docs/src/chapters/formats.adoc) and [fragment operations](../../../../vulkan-docs/src/chapters/fragops.adoc#fragops-depth).

Why it matters here:

- Combined formats optionally use separate depth/stencil layouts.
- The transfer-queue branch clears, renders, copies, and compares selected aspects.

## One Concrete Example

Consider `dEQP-VK.pipeline.monolithic.depth.depth_only.separate_render_passes_prepass`.

The test clears depth to `1.0`, then uses a depth-only pre-pass to write `0.0` into the left side. A later full-screen draw uses depth `0.5` with depth testing. It fails on the left where `0.5` loses against `0.0`, and passes on the right where the cleared depth is `1.0`. The final image therefore has clear color on the left and geometry color on the right; the depth image contains `0.0` and `0.5` in the corresponding regions. [The source comment](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1623-L1641) defines this expected result.

## End-to-End Test Flow

```text
[host] select the pipeline construction type and a depth branch
[host] check format features, required device features, extensions, and queue availability
[host] create depth/stencil and optional color attachments, pipelines, and simple vertex/fragment programs
[host] record draws, clears, layout transitions, or render-pass/dynamic-rendering boundaries
[device] execute fragment depth/stencil operations and attachment writes
[host] submit work, wait, read back relevant color/depth/stencil data, and compare it with a reference or fixed expected image
[host] report failure when a comparison detects an unexpected value or position
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`DepthTest::initPrograms()` emits a simple vertex program and, when a color attachment exists, a fragment program that forwards the vertex color. The shader has no depth-test logic: fixed-function pipeline state performs the tested work. [`DepthTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L307-L343) provides the source.

`DepthOnlyCase::initPrograms()` emits a vertex program whose push constant supplies scale, offset, and depth, and a fragment program with a constant output color. [`DepthOnlyCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1728-L1759) provides the source.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Depth/stencil attachment | Yes | Yes | Written and tested by fragment operations | Yes for checked branches | Holds the tested depth or stencil result. |
| Optional color attachment | Yes | Yes | Written by fragments that pass relevant tests | Yes | Makes passing and rejected fragments visible in `format`, `nocolor`, and `depth_only` scenarios. |
| Reference-renderer image | Yes, host-side model | No | No | Yes | Supplies expected color/depth results for the general depth tests. |
| Transfer staging depth/stencil image | Yes | Yes | Cleared or copied by transfer commands | Yes | Lets `xfer_queue_layout` validate selected aspects after queue and layout changes. |

## What Is Checked

- `format` and `nocolor` submit the draws, render a matching software reference, then compare the optional color image and the depth attachment. [`DepthTestInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1017-L1025) and [`DepthTestInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1028-L1118) implement this path.
- `xfer_queue_layout` reads the chosen depth/stencil aspects after transfer and attachment use and compares them with exact expected data. [`transferLayoutChangeTest()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1277-L1326) owns the resource setup.
- `depth_only` compares a fixed color reference with zero tolerance and a depth reference with `0.000025` tolerance. [`DepthOnlyInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2498-L2510) performs the final checks.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate test branch
>
> **Candidate values:** `format` and `nocolor`, `no_depth_attachment`, `depth_clip_control`, `xfer_queue_layout`, `depth_only`, `format_features`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `format` and `nocolor` | Incorrect fixed-function depth/bounds/stencil behavior, attachment handling, or reference-visible output. |
| `no_depth_attachment` | Depth-bounds state incorrectly affects rendering without a bound depth attachment. |
| `depth_clip_control` | Incorrect `VK_EXT_depth_clip_control` viewport depth-range or dynamic-state behavior. |
| `xfer_queue_layout` | Incorrect depth/stencil aspect layout transition, transfer-queue synchronization, clear, copy, or attachment reuse. |
| `depth_only` | Incorrect depth persistence or comparison across depth-only and color passes, subpasses, or dynamic rendering. |
| `format_features` | Required depth/stencil attachment format support is absent or reported incorrectly. |

## Important Variations and Special Cases

- `format` has a color attachment; `nocolor` registers the same generated format structure without one. The distinction checks whether attachment presence changes depth behavior.
- The generated compare-op matrix assigns four compare operations across four quads and uses pair-wise coverage rather than every possible four-quad tuple. [`createDepthTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2521-L2602) defines the matrix.
- Combined depth/stencil formats add a separate-layout variant. Depth-bounds variants require the core depth-bounds feature; depth-clip-control variants require `VK_EXT_depth_clip_control`. [`DepthTest::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L275-L296) owns these gates.
- `depth_only` selects separate render passes, subpasses, or dynamic rendering. Shader-object construction skips the first two types, and Vulkan SC omits dynamic rendering. [`createDepthTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2845-L2883) registers these variants.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Support gates and ordinary test construction | [`DepthTest::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L275-L304) | Connects generated cases to required features, extensions, and pipeline construction checks. |
| General reference comparison | [`DepthTestInstance::verifyImage()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1028-L1118) | Builds reference rendering state and reads back the tested attachments. |
| Transfer-queue setup | [`transferLayoutChangeTest()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1277-L1326) | Shows aspect selection and transfer/depth-stencil resource setup. |
| Depth-only expected regions and shaders | [depth-only description and setup](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1623-L1759) | Defines the pre-pass/post-pass result and generated programs. |
| Registration matrix | [`createDepthTests()`](../../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L2515-L2885) | Registers the direct branches and their construction-type predicates. |

## Questions / Risk Points for User Audit

- The inspected source resolves the behavioral-axis and validation questions for this rewrite.
- Shader programs are supporting inputs rather than the behavior under test, so the final page should retain `## Shader Analysis` without a representative shader walkthrough or SPIR-V artifact.

## Conversion Notes for Final Wiki Rewrite

- Use the intermediate test branch as the final page's behavior parameter.
- Copy the failure cause mapping table above verbatim into the final page.
- Distill the two prerequisite concepts into brief final-page bullets, then move setup, generated values, and validation detail to their dedicated sections.
- Keep the depth-only example as runtime explanation, not a shader walkthrough.
