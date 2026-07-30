# Understanding Brief: api.copy_and_blit.<core|copy_commands2>.depth_stencil_msaa_copy / vktApiCopyDepthStencilMSAATests.cpp

This brief prepares a rewrite of the multisampled depth/stencil image-to-image copy Level-3 wiki page. It is intentionally
explanation-first and uses the source code and mustpass evidence as the primary authority. Vulkan spec references in this
brief rely on the canonical copy-image and depth/stencil aspect semantics; the `external/vulkan-docs/src/chapters/` tree was
not present in the inspected checkout, so the brief relies on the spec rules as published in the Vulkan API Specification
(`VK_KHR_copy_commands2`, `VkImageCopy`, `VkImageAspectFlagBits`, multisampled image copy rules).

## One-Sentence Test Purpose

This test checks whether `vkCmdCopyImage` and `vkCmdCopyImage2` preserve every individual sample of a multisampled
depth/stencil image when copying between two multisampled depth/stencil images of the same format, across whole-image,
subregion, and per-array-layer copies, with the depth and stencil aspects exercised independently.

Core question: **if a multisampled depth/stencil source is copied to a multisampled destination with the same format and
sample count, is the per-sample depth (or stencil) value at every copied coordinate identical between source and
destination, and are uncopied coordinates left untouched?**

## Background Knowledge

### Multisampled depth/stencil image copies

The Vulkan `vkCmdCopyImage` rule for multisampled images states that when both source and destination images have the same
number of samples and the same format, each sample is copied to the corresponding sample in the destination. There is no
sample resolution, no averaging, and no sample masking: the per-sample depth or stencil value at coordinate `(x, y)` sample
`s` in the source must appear verbatim at `(x, y)` sample `s` in the destination for every sample of every copied texel.
This differs from a resolve operation (`vkCmdResolveImage`), which produces a single-sample image by averaging or
selecting samples; this test never resolves.

Why it matters here:

- The test specifically checks every sample independently. A driver that confuses a copy with a resolve (or that only
  copies one sample) would fail.
- The verification path reads every sample of both images through multisampled input attachments and compares them
  per-sample on the host.

### Depth and stencil aspects in `VkImageCopy`

A `VkImageCopy` region names a single aspect through `srcSubresource.aspectMask` and `dstSubresource.aspectMask`. The
source and destination aspect masks must match. For combined depth/stencil formats (`VK_FORMAT_D16_UNORM_S8_UINT`,
`VK_FORMAT_D24_UNORM_S8_UINT`, `VK_FORMAT_D32_SFLOAT_S8_UINT`), depth and stencil are independent aspects that must be
copied in separate regions; a region with `VK_IMAGE_ASPECT_DEPTH_BIT` only touches the depth channel, and a region with
`VK_IMAGE_ASPECT_STENCIL_BIT` only touches the stencil channel. Depth-only formats (`VK_FORMAT_D32_SFLOAT`) and the
stencil-only format (`VK_FORMAT_S8_UINT`) expose a single aspect.

Why it matters here:

- The test matrix generates one set of cases with `copyAspect = VK_IMAGE_ASPECT_DEPTH_BIT` (the `_D_` leaf suffix) and
  another with `copyAspect = VK_IMAGE_ASPECT_STENCIL_BIT` (the `_S_` leaf suffix). They never combine the two aspects in a
  single region.
- A driver that, for a combined depth/stencil format, copied both aspects when only one was requested would still pass this
  test, but a driver that failed to copy the requested aspect independently of the other would fail.

### Multisampled input attachments and `subpassInputMS`

GLSL `subpassInputMS` (and its unsigned counterpart `usubpassInputMS`) declares a multisampled input attachment. The
`subpassLoad(attachment, sampleID)` form loads the value of a specific sample at the current fragment coordinate. This is
the only shader-side mechanism that lets a fragment shader read every sample of a multisampled depth/stencil attachment
without enabling `sampleRateShading`.

Why it matters here:

- The verification fragment shader runs under a single-sample pipeline and iterates `sampleID` from `0` to `samples - 1`
  in a loop, calling `subpassLoad(attachment, sampleID)` for each sample. This avoids the `sampleRateShading` feature
  requirement and still touches every sample.
- The verification shader uses `subpassInputMS` (float) for the depth aspect and `usubpassInputMS` (unsigned) for the
  stencil aspect. The host pipeline-state object sets `rasterizationSamples` to `VK_SAMPLE_COUNT_1_BIT` for verification,
  even though the input attachments are multisampled with `m_params.samples`.

### `fragmentStoresAndAtomics`

The `fragmentStoresAndAtomics` device feature enables storage-buffer writes from fragment shaders. The verification shader
writes per-sample depth/stencil values into two SSBOs (one for the source image samples, one for the destination image
samples), and the host later reads those buffers back. Without this feature, the test cannot run its verification path and
is skipped.

Why it matters here:

- This is a verification-only feature dependency. The Vulkan copy command itself does not require it; the test framework
  requires it to inspect multisampled depth/stencil image contents because Vulkan does not provide a direct host-readable
  layout for multisampled optimal-tiled depth/stencil images.

### Layout transitions around the copy

The Vulkan spec requires the source image of a transfer command to be in `VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL` or
`VK_IMAGE_LAYOUT_GENERAL`, and the destination image to be in `VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL` or
`VK_IMAGE_LAYOUT_GENERAL`. This test exercises all four combinations of these layouts, but only for the `whole` copy
option, to limit test count. Partial and array-layer copies use only the optimal layouts.

Why it matters here:

- A driver that handles the optimal layout correctly but mishandles `VK_IMAGE_LAYOUT_GENERAL` for transfer operations would
  pass partial and array-to-array cases but fail some `whole` cases.

## One Concrete Example

### `whole.d32_sfloat_general_general_D_4_bit`

Representative registered path (mustpass):

```text
dEQP-VK.api.copy_and_blit.core.depth_stencil_msaa_copy.whole.d32_sfloat_general_general_D_4_bit
```

Simplified behavior for this case:

1. The host creates two `VK_FORMAT_D32_SFLOAT` images, each `defaultExtent` wide and tall, single-layer,
   `VK_SAMPLE_COUNT_4_BIT`, optimal tiling, with usage
   `VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_OPTIMAL |
   VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT`.
2. The host creates a render pass that clears the source image to depth 0.1f (and stencil 0x10, which is irrelevant for a
   depth-only format), then renders a single triangle that covers the upper-right half of the image. The triangle is drawn
   with `depthTestEnable = VK_TRUE`, `depthWriteEnable = VK_TRUE`, `depthCompareOp = VK_COMPARE_OP_ALWAYS`. Rasterization
   uses `VK_SAMPLE_COUNT_4_BIT`. The destination image is separately cleared to depth 0.0f.
3. The host transitions both images to `VK_IMAGE_LAYOUT_GENERAL` and records `vkCmdCopyImage` with one
   `VkImageCopy` region whose `aspectMask == VK_IMAGE_ASPECT_DEPTH_BIT` and `extent == defaultExtent`.
4. The host transitions both images to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` for the verification render pass. A
   fullscreen quad is drawn with a single-sample pipeline. The verification fragment shader loops over `sampleID` from 0
   to 3, calls `subpassLoad(attachment0, sampleID)` for the source image and `subpassLoad(attachment1, sampleID)` for the
   destination image, and writes the depth `.r` component of each into a separate SSBO.
5. The host reads back both SSBOs and, for every `(x, y, s)` in the copied region, compares the source value at
   `(x, y, s)` against the destination value at `(x, y, s)`. The case passes only if every comparison is equal.

The same case is also registered under `api.copy_and_blit.copy_commands2.depth_stencil_msaa_copy.whole.d32_sfloat_general_general_D_4_bit`,
which records `vkCmdCopyImage2` instead of `vkCmdCopyImage` but otherwise shares the parameter matrix.

Conceptual verification shader for the depth aspect, reconstructed from the generator:

```glsl
#version 450

layout (push_constant, std430) uniform PushConstants {
    int width;
    int height;
    int samples;
};

layout (set=0, binding=0) buffer OriginalValues { float outputOriginal[]; };
layout (set=0, binding=1) buffer CopiedValues   { float outputCopied[];   };

layout (input_attachment_index=0, set=1, binding=0) uniform subpassInputMS attachment0;
layout (input_attachment_index=1, set=1, binding=1) uniform subpassInputMS attachment1;

void main() {
    for (int sampleID = 0; sampleID < samples; ++sampleID) {
        ivec3 coords  = ivec3(int(gl_FragCoord.x), int(gl_FragCoord.y), sampleID);
        int bufferPos = (coords.y * width + coords.x) * samples + coords.z;
        vec4 orig = subpassLoad(attachment0, sampleID);
        vec4 copy1 = subpassLoad(attachment1, sampleID);
        outputOriginal[bufferPos] = orig.r;
        outputCopied[bufferPos]   = copy1.r;
    }
}
```

Important simplifications:

- The real generator switches between `subpassInputMS` and `usubpassInputMS` based on the aspect being verified, and uses
  `0` (not `0.0`) for the empty-layer comparison in the stencil shader.
- The `array_to_array` generator adds per-layer `subpassLoad` calls, hard-codes `layerToVerify = "copy4"` for the target
  layer 3, and emits an `equalEmptyLayers` expression over the four non-target layers.

## End-to-End Test Flow

```text
1. [host] choose parameters
   1.1 select format, sample count, copy option (whole / partial / array_to_array), aspect (D or S),
       source/destination layouts (whole only), allocation kind, and extension flag (NONE or COPY_COMMANDS_2)
   1.2 build one or two VkImageCopy regions:
       - whole: one full-extent region at offset (0, 0)
       - partial: two half-extent regions, one bottom-right to bottom-left, one top-right to bottom-right
       - array_to_array: one full-extent region with srcBaseArrayLayer=2, dstBaseArrayLayer=3 on a 5-layer image

2. [host] create resources
   2.1 create the multisampled source image with depth/stencil + transfer-src + transfer-dst + input-attachment usage
   2.2 create the multisampled destination image with the same parameters
   2.3 when imageOffset is set, bind the source image memory at an offset equal to req.alignment
   2.4 create the triangle vertex buffer for the source rendering phase
   2.5 (verify phase) create two host-visible storage buffers sized fbWidth * fbHeight * samples * sizeof(float)
   2.6 (verify phase) create the fullscreen-quad vertex buffer

3. [host] initialize the source image by drawing
   3.1 record a command buffer that transitions both images to TRANSFER_DST_OPTIMAL and clears them
       (source to depth=0.1f, stencil=0x10; destination to depth=0.0f, stencil=0)
   3.2 transition the source image to DEPTH_STENCIL_ATTACHMENT_OPTIMAL
   3.3 begin a render pass that loads the source image as a depth/stencil attachment with LOAD_OP_CLEAR
   3.4 draw a single triangle covering the upper-right half of the framebuffer, with depthWriteEnable=TRUE,
       depthCompareOp=ALWAYS, and stencil passOp=REPLACE; rasterizationSamples = m_params.samples
   3.5 end the render pass; the source image is left in DEPTH_STENCIL_ATTACHMENT_OPTIMAL
   3.6 submit and wait

4. [host] record the copy
   4.1 transition the source image to m_srcImage.operationLayout (TRANSFER_SRC_OPTIMAL or GENERAL)
   4.2 transition the destination image to m_dstImage.operationLayout (TRANSFER_DST_OPTIMAL or GENERAL)
   4.3 record vkCmdCopyImage (extensionFlags == NONE) or vkCmdCopyImage2 (extensionFlags == COPY_COMMANDS_2)
       with the prepared regions
   4.4 submit and wait

5. [host] verify per-sample equality
   5.1 (per used aspect) build a verification render pass with N+1 input attachments, where N is the destination
       array layer count (1 for whole and partial, 5 for array_to_array) and the first attachment is the source image
   5.2 bind two SSBOs (outputOriginal, outputCopied) and N+1 input attachment descriptors
   5.3 push width, height, and samples as push constants
   5.4 transition images as needed for the verification render pass
   5.5 draw a fullscreen quad with a single-sample pipeline; the verification fragment shader iterates samples in-shader,
       loads each sample from each attachment via subpassLoad, and writes per-sample .r values to the SSBOs
   5.6 for array_to_array, the shader additionally checks that all non-target layers equal 0 (or 0.0); if not, it
       decrements outputCopied[bufferPos] to force a mismatch
   5.7 submit and wait; the host invalidates the SSBO allocations

6. [host] compare results
   6.1 for each copied region, for each (x, y, s) in the region, compare outputOriginal[srcIndex] against
       outputCopied[dstIndex]; fail on first mismatch
   6.2 for partial, additionally verify that every (x, y, s) in the upper half of the destination image has
       outputCopied[bufferIndex] == 0.0f (the clear value)
   6.3 for array_to_array, the in-shader empty-layer check already guarantees that the four non-target layers are 0,
       so the host does not re-check them
   6.4 pass only if all checks succeed for every used aspect (depth and/or stencil)
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|----------|------------------------|------|
| Triangle vertex shader | [`DepthStencilMSAATestCase::initPrograms()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1137-L1167) | Static `#version 310 es` vertex shader that emits `a_position` with z=1.0; used to draw a triangle into the source image. |
| Triangle fragment shader | [`DepthStencilMSAATestCase::initPrograms()`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1137-L1167) | Empty `#version 310 es` fragment shader; the rendering phase only writes depth/stencil through the pipeline state. |
| Depth verification fragment shader | [`createVerificationShader()` with `VK_IMAGE_ASPECT_DEPTH_BIT`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1055-L1132) | Iterates `sampleID`, loads multisampled depth input attachments, writes per-sample `.r` values into two SSBOs. |
| Stencil verification fragment shader | [`createVerificationShader()` with `VK_IMAGE_ASPECT_STENCIL_BIT`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1055-L1132) | Same shape as the depth shader but uses `usubpassInputMS` and compares non-target layers against `0` (integer literal) instead of `0.0`. |
| Verification vertex shader | Reuses the static triangle vertex shader | Reused as the vertex stage of the verification pipeline. |
| Pipeline state | Host pipeline setup | The render pipeline uses `m_params.samples` rasterizationSamples and the depth/stencil state for the aspect being exercised; the verification pipeline uses `VK_SAMPLE_COUNT_1_BIT` rasterizationSamples. |
| Render pass descriptions | Host render pass setup | Two render passes are created: one for the rendering phase (depth/stencil attachment with `m_params.samples`), one for the verification phase (N+1 input attachments with `m_params.samples`). |

Important distinction: GLSL `shared` variables and push-constant structures are generated shader declarations, not
host-created Vulkan resources. The host only creates the SSBOs, the images, and the vertex buffers.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|------------------------------|---------------|--------------------------|--------------------|------------------|
| Source multisampled depth/stencil image | Yes, `VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT \| VK_IMAGE_USAGE_TRANSFER_SRC_BIT \| VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT` | Yes, image memory bound (with optional alignment offset when `imageOffset` is true) | Cleared, drawn to, copied from, read as input attachment | No | Holds the source samples that must be preserved by the copy. |
| Destination multisampled depth/stencil image | Yes, same usage flags as the source | Yes, image memory bound | Cleared, copied to, read as input attachment | No | Holds the copied samples that the host verifies. |
| Triangle vertex buffer | Yes, host-visible | Yes, vertex buffer binding | Read by vertex shader during rendering | No | Drives the rasterization that produces known depth/stencil values in the source image. |
| Fullscreen-quad vertex buffer (verify phase) | Yes, host-visible | Yes, vertex buffer binding | Read by vertex shader during verification | No | Ensures every framebuffer pixel is visited by the verification shader. |
| Storage buffer for source samples | Yes, host-visible, `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` | Yes, descriptor binding `0` of set 0 | Written per-sample by the verification shader | Yes, invalidated then read | Carries the source image's per-sample `.r` values back to the host. |
| Storage buffer for destination samples | Yes, host-visible, `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` | Yes, descriptor binding `1` of set 0 | Written per-sample by the verification shader | Yes, invalidated then read | Carries the destination image's per-sample `.r` values back to the host. |
| Descriptor sets | Yes | Yes | Bind SSBOs and input attachments to the verification pipeline | No | Set 0 carries the two SSBOs; set 1 carries N+1 input attachment bindings. |
| Push constants | Yes, range size 12 bytes | Yes | Read by the verification fragment shader | No | Carries `width`, `height`, `samples`. |
| Render pass and framebuffer (render phase) | Yes | Yes | Single depth/stencil attachment | No | Drives the source image initialization. |
| Render pass and framebuffer (verify phase) | Yes | Yes | N+1 input attachments | No | Routes source and destination images into the verification shader. |

## What Is Checked

### Device-side checks

| Copy option | Device-side condition (in-shader) |
|-------------|------------------------------------|
| `whole` | The verification shader writes per-sample `.r` values into `outputOriginal` and `outputCopied`; it does not perform any comparison itself. |
| `partial` | Same as `whole`. The partial-specific clear-value check is done on the host. |
| `array_to_array` | The shader additionally checks that every non-target layer (layers 0, 1, 2, 4 of a 5-layer image) has `.r == 0` (or `0.0` for the depth aspect). If any non-target layer is nonzero, the shader decrements `outputCopied[bufferPos]` to force a host-side mismatch at that coordinate. |

### Host-side checks

The host walks each `VkImageCopy` region and, for every `(x, y, s)` in the region:

- Computes `srcIndex = (y + srcOffset.y) * fbWidth + (x + srcOffset.x)) * sampleCount + s`.
- Computes `dstIndex = (y + dstOffset.y) * fbWidth + (x + dstOffset.x)) * sampleCount + s`.
- Compares `outputOriginal[srcIndex]` against `outputCopied[dstIndex]`.
- Fails the case on the first mismatch, logging the coordinate, sample, expected, and actual values.

For `partial` only, the host additionally walks the upper half of the destination image (every `(x, y, s)` with
`y < extent.height / 2`) and verifies `outputCopied[bufferIndex] == m_clearValue` (which is `0.0f`). This guarantees the
copy did not touch any texel outside the requested regions.

For `array_to_array`, the host does not re-walk the non-target layers because the in-shader check already enforces they
equal zero; if a non-target layer is nonzero, the in-shader decrement surfaces as a mismatch on the target layer.

There is no tolerance or partial success rule: the first mismatched sample fails the case.

## Behavior Parameter Identification

> **Behavior parameter:** `copyOptions` (the registered copy option, encoded as the `whole` / `partial` / `array_to_array`
> intermediate node directly below the `depth_stencil_msaa_copy` test family)
>
> **Candidate values:** `whole`, `partial`, `array_to_array`

The `copyAspect` dimension (depth vs. stencil, encoded as the `_D_` / `_S_` leaf suffix) is a parameter dimension rather
than the primary behavioral axis. It changes which aspect is the target of the copy and which verification shader is
generated, but it does not change the structure of the regions, the verification flow, or the failure mechanisms in a way
that warrants separate behavioral-axis subsections. The `samples`, format, layouts, allocation kind, and command extension
are configuration dimensions, not behavioral axes.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `whole` | Per-sample depth/stencil value not preserved by `vkCmdCopyImage`/`vkCmdCopyImage2` for a full-extent, single-region, same-format, same-sample-count copy. Includes incorrect layout handling when the `GENERAL` layout variants fail but the optimal-layout variants pass. |
| `partial` | Same per-sample preservation failure as `whole`, or the implementation writes outside the requested regions (the upper-half clear-value check fails). |
| `array_to_array` | Per-sample preservation failure on the target layer, or the implementation writes to non-target array layers (the in-shader `equalEmptyLayers` check fails and surfaces as a forced mismatch). |

A shared infrastructure cause affects all three values: incorrect source-image rendering that produces unknown sample
values, incorrect verification-shader `subpassLoad`/SSBO-write behavior, or incorrect host-side index arithmetic. These
would produce failures across multiple cases uniformly.

## Important Variations and Special Cases

### Whole-image versus partial versus array-to-array

The three copy options differ in three ways:

- **Region shape**: `whole` copies a single full-extent region; `partial` copies two half-extent regions into different
  destination offsets; `array_to_array` copies a single full-extent region between two specific array layers.
- **Image array layer count**: `whole` and `partial` use a single-layer image; `array_to_array` uses a 5-layer image and
  copies from layer 2 to layer 3.
- **Verification scope**: `whole` only checks per-sample equality on the copied region; `partial` additionally checks that
  the upper half of the destination image is still at the clear value; `array_to_array` additionally checks (in-shader)
  that the four non-target layers are still at zero.

### Layout variations

The `whole` copy option is the only one that varies source and destination layouts (`TRANSFER_OPTIMAL` vs. `GENERAL`). The
`partial` and `array_to_array` options use only the optimal layouts, registered under the `<format>_D_<samples>` and
`<format>_S_<samples>` leaf names. The `whole` option generates the four layout-combination leaves
`<format>_<srcLayoutCase>_<dstLayoutCase>_D_<samples>` (and the `_S_` variant).

### Bind-offset variant

Each non-dedicated-allocation case is registered twice: once without a bind offset and once with a `_bind_offset` suffix.
The bind-offset variant binds the source image memory at an offset equal to `VkMemoryRequirements::alignment`, exercising
the implementation's handling of non-zero `vkBindImageMemory` offsets. The dedicated-allocation path skips the bind-offset
variant because dedicated allocations cannot have a nonzero offset.

### Command extension

The test family is registered under two parent intermediate nodes inside `copy_and_blit`:

- `api.copy_and_blit.core.depth_stencil_msaa_copy.*` exercises `vkCmdCopyImage` with `extensionFlags = NONE`.
- `api.copy_and_blit.copy_commands2.depth_stencil_msaa_copy.*` exercises `vkCmdCopyImage2` with
  `extensionFlags = COPY_COMMANDS_2`.

Both branches share the same parameter matrix and source implementation; the only difference is the recorded command.

### Stencil `checkSupport` observation

The `checkSupport()` implementation queries `framebufferDepthSampleCounts` for both the depth and the stencil aspect
([lines 1033-1035](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1033-L1035)). The Vulkan spec exposes
`framebufferStencilSampleCounts` separately for stencil, so this looks like a CTS-side oversight. In practice, many
implementations report the same sample count support for depth and stencil attachments, so the gate is usually equivalent.
The behavior is a CTS implementation detail, not a Vulkan implementation issue, and does not change the failure analysis.

### Source-image rendering, not buffer upload

The source image is initialized by rendering a triangle, not by uploading buffer data via `vkCmdCopyBufferToImage`. This
means the per-sample depth/stencil values are determined by the rendering pipeline (depth test `ALWAYS` writes the
interpolated depth, and rasterization produces known sample locations for the triangle fragment). The test does not
assert specific source values; it only checks that the destination matches the source. A correct copy of any source
contents passes; an incorrect copy fails regardless of the source values.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test class declaration and parameter struct | [`vktApiCopyDepthStencilMSAATests.cpp#L35-L82`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L35-L82) | Defines `DepthStencilMSAA`, `CopyOptions`, `TestParameters`, and the copy-region construction. |
| Constructor — region construction | [`vktApiCopyDepthStencilMSAATests.cpp#L84-L200`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L84-L200) | Builds the `VkImageCopy` regions for whole, partial, and array-to-array copy options. |
| Render phase — image creation, render pass, pipeline | [`vktApiCopyDepthStencilMSAATests.cpp#L226-L558`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L226-L558) | Creates the multisampled source image, draws the initializing triangle, and clears both images. |
| Copy phase — layout transition and `vkCmdCopyImage`/`vkCmdCopyImage2` | [`vktApiCopyDepthStencilMSAATests.cpp#L564-L641`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L564-L641) | Records the copy command under test. |
| Verify phase — `checkCopyResults()` | [`vktApiCopyDepthStencilMSAATests.cpp#L661-L1001`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L661-L1001) | Builds the verification render pass, SSBOs, descriptor sets, fullscreen-quad pipeline, and host-side per-sample comparison. |
| Host-side partial-copy clear-value check | [`vktApiCopyDepthStencilMSAATests.cpp#L979-L997`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L979-L997) | Verifies the upper half of the destination image remains at the clear value for `COPY_PARTIAL`. |
| `DepthStencilMSAATestCase` class | [`vktApiCopyDepthStencilMSAATests.cpp#L1003-L1135`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1003-L1135) | Holds `checkSupport()` and `initPrograms()`; builds the verification shader source. |
| Verification shader generator | [`vktApiCopyDepthStencilMSAATests.cpp#L1055-L1132`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1055-L1132) | Emits the depth/stencil verification GLSL with `subpassInputMS`/`usubpassInputMS` and the `equalEmptyLayers` check for `array_to_array`. |
| Sample count list | [`vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1169-L1170) | The 2/4/8/16/32/64 sample count matrix. |
| `addDepthStencilCopyMSAATest()` | [`vktApiCopyDepthStencilMSAATests.cpp#L1172-L1256`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1172-L1256) | Generates the format x aspect x sample x layout x bind-offset leaf matrix for one copy option. |
| `addCopyDepthStencilMSAATests()` | [`vktApiCopyDepthStencilMSAATests.cpp#L1260-L1275`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1260-L1275) | Registers `whole`, `partial`, and `array_to_array` subgroups under the parent test group. |
| Parent registration | [`vktApiCopiesAndBlittingTests.cpp#L138`](../../../modules/vulkan/api/vktApiCopiesAndBlittingTests.cpp#L138) | Routes `depth_stencil_msaa_copy` to `addCopyDepthStencilMSAATests()` under both `core` and `copy_commands2` parents. |
| Mustpass evidence (core path) | [`api.txt#L174767`](../../../mustpass/main/vk-default/api.txt#L174767) | Concrete `dEQP-VK.api.copy_and_blit.core.depth_stencil_msaa_copy.*` entries. |
| Mustpass evidence (copy_commands2 path) | [`api.txt#L23616`](../../../mustpass/main/vk-default/api.txt#L23616) | Concrete `dEQP-VK.api.copy_and_blit.copy_commands2.depth_stencil_msaa_copy.*` entries. |

## Questions / Risk Points for User Audit

- [x] The primary behavioral axis is the copy option (`whole` / `partial` / `array_to_array`). Each value changes the
  region shape, the array layer count, and the verification logic. Confirmed by source at
  [`vktApiCopyDepthStencilMSAATests.cpp#L84-L200`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L84-L200)
  and
  [`vktApiCopyDepthStencilMSAATests.cpp#L979-L997`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L979-L997).
- [x] The `copyAspect` (depth vs. stencil) is a parameter dimension, not a behavioral axis. It only selects which aspect
  is the target of the copy and which verification shader is generated. Confirmed by
  [`vktApiCopyDepthStencilMSAATests.cpp#L1151-L1166`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1151-L1166).
- [x] No `### Representative Shader Walkthrough` subsections will be created in the final page. The verification shader is
  the only shader in this test family, and per the harness instructions for this page, Phase 5 is skipped. The shader's
  structure will be summarized in the `## Shader Analysis` section without a full walkthrough.
- [x] The `framebufferDepthSampleCounts` check for stencil aspects is a CTS-side observation, not a Vulkan implementation
  issue. It is documented as a CTS implementation detail in the final page's `## Case Pruning` section, not in
  `## Failure Meaning`.
- [x] Layout variations (`TRANSFER_OPTIMAL` vs. `GENERAL`) are documented as a parameter dimension that applies only to
  the `whole` copy option. This matches the source at
  [`vktApiCopyDepthStencilMSAATests.cpp#L1186-L1255`](../../../modules/vulkan/api/vktApiCopyDepthStencilMSAATests.cpp#L1186-L1255).
- [x] The dual registration under `core` and `copy_commands2` is documented as a parameter dimension, not a behavioral
  axis. Both branches share the same parameter matrix and source implementation; only the recorded command differs.
- [x] No external `vulkan-docs/src/chapters/` tree was present in the inspected checkout. Background Knowledge was grounded
  in canonical Vulkan spec semantics (`VK_KHR_copy_commands2`, `VkImageCopy`, `VkImageAspectFlagBits`, multisampled image
  copy rules) from the spec-as-published; no in-repo spec source was inspected.

## Conversion Notes for Final Wiki Rewrite

- Keep the one-sentence purpose as the final page's short problem statement.
- Distill the Background Knowledge into a compact prerequisite list: multisampled depth/stencil copy semantics,
  per-aspect `VkImageCopy` regions, multisampled input attachments and `subpassInputMS`/`usubpassInputMS`,
  `fragmentStoresAndAtomics`, and layout transition rules around transfers.
- Carry the `## Behavior Parameter Identification` conclusion directly into `## Behavior Parameters` with three subsections
  (`whole`, `partial`, `array_to_array`).
- Carry the `### Failure Cause Mapping` table directly into the final page's `### Failure Cause Mapping`.
- Write `### Cause Analysis` fresh during the rewrite; do not carry it from the brief.
- Summarize the verification shader structure in `## Shader Analysis` without a full walkthrough, per the harness
  Phase 5 skip instruction.
- Document the `framebufferDepthSampleCounts` check as a CTS-side observation in `## Case Pruning`, not as a failure cause.
- Document the dual `core`/`copy_commands2` registration in the `## Registration Hierarchy` section with two parallel
  trees or a single tree plus a note describing the second registration path.
- Move detailed parameter matrix information into `## Parameter Dimensions and Observed Values` and keep it concise.
- Move all source-code link tables to `## Source Reference Appendix`.
- Do not copy the beginner-focused prose verbatim into the final page; convert it to the Level-3 wiki style.
