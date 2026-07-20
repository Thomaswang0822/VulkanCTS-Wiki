# Understanding Brief: rasterization.shader_tile_image / vktShaderTileImageTests.cpp

This brief prepares the rewrite of the Level-3 Vulkan CTS wiki page for the `shader_tile_image`
test family. It is explanation-first and uses the source file as the primary authority.

The Vulkan spec chapters under `external/vulkan-docs/src/chapters/` were not present in this
checkout. Background Knowledge and Failure Cause Mapping below are therefore grounded in the
CTS source comments and code paths, with explicit notes wherever a spec-grounded claim could
not be independently verified.

## One-Sentence Test Purpose

This test checks whether `VK_EXT_shader_tile_image` fragment-shader reads of color, depth, and
stencil attachments return the value previously written by an earlier overlapping draw, under
coherent or non-coherent read semantics, across MSAA, helper-invocation, MRT, multi-draw, and
multi-patch variations.

Core question: **after a fragment shader writes a per-patch value to a color/depth/stencil
attachment through dynamic rendering, can a later fragment shader invocation in the same or a
subsequent draw read that exact value back through a `colorAttachmentReadEXT`,
`depthAttachmentReadEXT`, or `stencilAttachmentReadEXT` call?**

## Background Knowledge

### VK_EXT_shader_tile_image and tile image reads

`VK_EXT_shader_tile_image` exposes fragment-shader built-ins that read the current pixel's
color, depth, or stencil attachment directly from tile memory within a dynamic-rendering pass.
The CTS source declares the extension at the top of
[`vktShaderTileImageTests.cpp`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L22-L24)
and the test requires it together with `VK_KHR_dynamic_rendering` in
[`checkSupport()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L951-L961).

The shader-side reads are exposed as `colorAttachmentReadEXT`, `depthAttachmentReadEXT`, and
`stencilAttachmentReadEXT`. Color reads optionally take a sample ID for per-sample reads.
The generated fragment shaders declare the corresponding tile-image variables as
`attachmentEXT` / `iattachmentEXT` / `uattachmentEXT` selected by the color format's channel
class [initPrograms()](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L900-L944).

Why it matters here:

- The test's pass condition is whether the value read back through these built-ins equals the
  value the test host simulated.
- Coherent versus non-coherent read access is a property of the fragment shader invocation's
  tile-image read; non-coherent reads add the appropriate `non_coherent_*_attachment_readEXT`
  layout qualifier and require an explicit pipeline barrier between draw calls.

### Dynamic rendering and tile memory lifetime

Tests use `VK_KHR_dynamic_rendering` (`vkCmdBeginRendering` / `vkCmdEndRendering`) rather than a
traditional render pass. Color and depth/stencil attachments are bound through
`VkRenderingAttachmentInfoKHR` and the rendering info struct at
[`rendering()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1752-L1914).
The pipeline is created with `VkPipelineRenderingCreateInfoKHR` chained to the graphics pipeline
create info, so the attachment formats are known at pipeline creation
[`generateGraphicsPipeline()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1219-L1440).

Why it matters here:

- Tile-image reads only return valid data inside a dynamic-rendering pass for fragments that
  touch the same pixel as the prior write. The test relies on this property to chain values
  across draws.
- Because no `VkRenderPass` is used, the host must insert the correct memory barriers between
  draws for non-coherent reads, which the source does at
  [`vktShaderTileImageTests.cpp#L1871-L1910`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1871-L1910).

### Coherent versus non-coherent tile-image reads

Coherent reads are the default tile-image behavior: a fragment shader invocation can read the
most recent color/depth/stencil value written to its pixel by an earlier invocation in the
same rendering pass without an explicit memory barrier. Non-coherent reads add the layout
qualifiers `non_coherent_color_attachment_readEXT`, `non_coherent_depth_attachment_readEXT`,
and `non_coherent_stencil_attachment_readEXT` to the fragment shader, and the host inserts a
`VkMemoryBarrier2KHR` between draw calls to make the prior write visible to the next draw's
non-coherent read.

Why it matters here:

- `coherent` and `non_coherent` are the two direct children of the test family. The shader
  generator branches on `m_testParam.coherent` to add the qualifiers at
  [`vktShaderTileImageTests.cpp#L364-L367`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L364-L367),
  [`vktShaderTileImageTests.cpp#L495-L507`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L495-L507),
  [`vktShaderTileImageTests.cpp#L612-L615`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L612-L615),
  [`vktShaderTileImageTests.cpp#L689-L693`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L689-L693),
  and
  [`vktShaderTileImageTests.cpp#L758-L762`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L758-L762).
- The host inserts the inter-draw barrier only for non-coherent cases at
  [`vktShaderTileImageTests.cpp#L1871-L1910`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1871-L1910).
- For multi-patch cases (multiple overlapping patches within a single draw), the test design
  cannot guarantee non-coherent visibility between fragment shader invocations of the same
  draw, so non-coherent multi-patch cases are skipped at
  [`vktShaderTileImageTests.cpp#L2101-L2106`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2101-L2106).
- Coherent multi-patch cases exercise the strongest guarantee: every fragment shader
  invocation must observe the latest value written by an earlier overlapping invocation in
  the same draw.

### Helper fragment invocations

Helper invocations are fragment shader invocations generated by the rasterizer for pixels
adjacent to a covered pixel, used to provide derivatives such as `dFdx` / `dFdy`, but whose
color/depth/stencil writes are normally discarded. The Vulkan property
`shaderTileImageReadFromHelperInvocation` reports whether tile-image reads from helper
invocations return valid values.

Why it matters here:

- The `helper_class_color`, `helper_class_depth`, and `helper_class_stencil` test types
  explicitly verify that helper invocations observe correct tile-image values by using
  `dFdxFine` / `dFdyFine` to detect rasterization patterns
  [`getHelperClassTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L474-L584).
- The support check throws `NotSupportedError` for helper-class cases when
  `shaderTileImageReadFromHelperInvocation` is `VK_FALSE` at
  [`vktShaderTileImageTests.cpp#L1029-L1034`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1029-L1034).

### MSAA sample-rate reads

For multisampled attachments, `colorAttachmentReadEXT` can be called without a sample
parameter (returns the pixel-rate value), or with a `gl_SampleID` parameter (returns a
per-sample value). The property `shaderTileImageReadSampleFromPixelRateInvocation` reports
whether pixel-rate fragment invocations can read per-sample values when
`rasterizationSamples > 1`.

Why it matters here:

- The `msaa_sample_mask` test type iterates all covered samples per fragment using
  `gl_SampleMaskIn[0]` and calls `colorAttachmentReadEXT(colorIn0, i)` for each covered
  sample [`getSampleMaskTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L586-L672).
- This case is the only test type that uses an explicit `pSampleMask` (`0xaaaaaaaa`) and
  disables sample shading; the rest of the multi-sample cases enable sample shading.
- The support check throws `NotSupportedError` for `msaa_sample_mask` when
  `shaderTileImageReadSampleFromPixelRateInvocation` is `VK_FALSE` at
  [`vktShaderTileImageTests.cpp#L1017-L1026`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1017-L1026).
- `msaa_sample_mask` skips the `samples_1` case because the test requires more than one
  sample.

## One Concrete Example

### `coherent.color.samples_1.single_draw.single_patch.r8g8b8a8_unorm`

Representative test name pattern from `vk-default`:

```text
dEQP-VK.rasterization.shader_tile_image.coherent.color.samples_1.single_draw.single_patch.r8g8b8a8_unorm
```

Simplified behavior:

1. The host creates a 4×4 `R8G8B8A8_UNORM` color attachment, transitions it to
   `COLOR_ATTACHMENT_OPTIMAL`, and begins dynamic rendering.
2. The host issues a single draw of one triangle patch (`single_draw`, `single_patch`) with
   `patchIndex = 1` (computed in the vertex shader from `gl_VertexIndex` and `drawIndex`).
3. The fragment shader runs `colorAttachmentReadEXT(colorIn0)`, rounds and amplifies the
   result, then writes the next value to `out0`:
   - First fragment touched in the patch: `previous.x == 0 && patchIndex == 1`, so write
     `out0.y = patchIndex + zero + gl_SampleID + 0 = 1`.
   - Subsequent overlapping fragments: `previous.x == 0 && previous.y + 1 == patchIndex + 0`,
     so write `out0.y = previous.y + 1`.
   - Otherwise write `out0.x = 1` to mark an error.
4. After dynamic rendering, a compute shader copies the color attachment into a host-visible
   storage buffer.
5. The host reads back the buffer, scans each `(fx, fy, fs)` for the expected value
   `totalLayerCount + rt + sampleID = 1 + 0 + 0 = 1`, and fails if `out0.x != 0` or the
   expected value does not match.

Conceptual fragment shader logic, reconstructed from the generator:

```glsl
#version 450 core
#extension GL_EXT_shader_tile_image : require
layout(location = 0) tileImageEXT highp attachmentEXT colorIn0;
layout(location = 0) out highp vec4 out0;
layout(location = 0) flat in uint patchIndex;
void main()
{
    const float amplifier = 255.0; // for UNORM r8g8b8a8
    uvec2 previous = uvec2(round(colorAttachmentReadEXT(colorIn0) * amplifier).xy);
    if (previous.x == 0 && patchIndex == 1) {
        out0 = vec4(0, float(1 + 0 + 0 + 0) / amplifier, 0, 0);
    } else if (previous.x == 0 && (previous.y + 1) == (patchIndex + 0 + 0)) {
        out0 = vec4(0, float(previous.y + 1) / amplifier, 0, 0);
    } else {
        out0 = vec4(1, float(previous.y) / amplifier, 0, 0); // error
    }
}
```

Important simplifications: the real generator also inserts an "overhead" loop after the read
to discourage shader compiler reordering, picks the variable type and channel count from the
color format, and selects `gl_SampleID`-parameterized reads for multisampled cases.

## End-to-End Test Flow

```text
1. [host] register and generate case hierarchy
   1.1 create the `shader_tile_image` root
   1.2 add `coherent` and `non_coherent` direct children
   1.3 under each, add test-type, sample-count, draw-count, patch-count, and format leaves
       with the pruning rules in createShaderTileImageTestVariations()

2. [host] check device support
   2.1 require VK_KHR_dynamic_rendering and VK_EXT_shader_tile_image
   2.2 require shaderTileImageColorReadAccess for every case
   2.3 require shaderTileImageDepthReadAccess for depth and helper_class_depth cases
   2.4 require shaderTileImageStencilReadAccess for stencil and helper_class_stencil cases
   2.5 require shaderTileImageReadSampleFromPixelRateInvocation for msaa_sample_mask
   2.6 require shaderTileImageReadFromHelperInvocation for helper_class_* cases
   2.7 require sampleRateShading for non-msaa_sample_mask multi-sample cases
   2.8 verify format support for the chosen color and depth/stencil formats

3. [host] generate shaders
   3.1 vertex shader: computes `patchIndex` from `gl_VertexIndex` and `drawIndex`
   3.2 fragment shader: dispatched into one of five builder functions based on `TestType`
   3.3 compute shader: copies color attachment texels into a host-visible storage buffer

4. [host] create resources and pipelines
   4.1 create one or two color attachments (one for color/depth/stencil/msaa, two for MRT and helper class)
   4.2 create the depth/stencil attachment when the test type needs it
   4.3 create vertex buffers containing one or two triangle patches per draw
   4.4 build the main graphics pipeline, plus a second helper-class pipeline that disables
       writes to color0, depth, and stencil

5. [host] submit command buffer
   5.1 transition images to COLOR_ATTACHMENT_OPTIMAL / DEPTH_STENCIL_ATTACHMENT_OPTIMAL
   5.2 begin dynamic rendering with the color and depth/stencil attachments
   5.3 for each draw:
       5.3.1 if this is a helper-class second draw, bind the helper-class pipeline
       5.3.2 if non-coherent, insert a VkMemoryBarrier2KHR between draws for the relevant
             attachment type (color or depth/stencil)
       5.3.3 push the `drawIndex` constant and draw the patches for this draw
   5.4 end dynamic rendering
   5.5 transition color attachments to SHADER_READ_ONLY_OPTIMAL
   5.6 dispatch the compute shader to copy color attachment data into host-visible buffers
   5.7 insert a final barrier to make the buffer host-visible

6. [device] execute the selected fragment shader flow
   6.A color / mrt / mrt_dynamic_index
       6.A.1 read previous color value(s) through colorAttachmentReadEXT
       6.A.2 run the overhead loop
       6.A.3 if previous.x == 0 && patchIndex == 1: write initial patch value
       6.A.4 else if previous.y + 1 == patchIndex + gl_SampleID + i: write previous.y + 1
       6.A.5 else: write the error marker (out.x = 1)
   6.B depth
       6.B.1 read previous depth through depthAttachmentReadEXT and previous color through
             colorAttachmentReadEXT
       6.B.2 same chained-value rule, but the expected value is the previous depth value + 1
       6.B.3 multisample cases also write gl_FragDepth so all samples are forced
   6.C stencil
       6.C.1 read previous stencil through stencilAttachmentReadEXT and previous color
       6.C.2 same chained-value rule, but the expected value is the previous stencil value + 1
   6.D msaa_sample_mask
       6.D.1 iterate every sample from 0 to sampleCount - 1
       6.D.2 if the sample is covered (bit set in gl_SampleMaskIn[0]), read the per-sample
             color through colorAttachmentReadEXT(colorIn0, i)
       6.D.3 verify all covered samples agree on the same previous value; otherwise mark error
   6.E helper_class_color / _depth / _stencil
       6.E.1 first draw uses the main pipeline and writes a per-patch value to attachment 0
       6.E.2 second draw uses the helper-class pipeline that disables color0/depth/stencil
             writes, so its fragment shader invocations include helper invocations whose
             writes are discarded
       6.E.3 the fragment shader reads the previous value through colorAttachmentReadEXT,
             plus depthAttachmentReadEXT or stencilAttachmentReadEXT for depth/stencil
             variants
       6.E.4 the shader computes dFdxFine / dFdyFine of the previous value and uses that to
             distinguish helper-covered pixels from rasterized pixels
       6.E.5 the host compare accepts both possible outcomes for the diagonal where
             max(dx, dy) is ambiguous

7. [host] read back and verify
   7.1 invalidate the host-visible copy buffer and read its contents
   7.2 for each (rt, fy, fx, fs):
       7.2.1 read `resultValue` from the buffer; if `resultData[index] != 0`, the fragment
             shader wrote the error marker and result is `0xFFFFFFFF`
       7.2.2 compute `expectedValue` via `simulate()`
       7.2.3 compare the two according to the test type
             - helper class: allow `kDerivative1` on the off-diagonal
             - 6-vertex patches: compare only inside the filled triangle
             - 3-vertex patches: compare inside the triangle, allow zero or expected outside
   7.3 return PASS if every comparison succeeds; otherwise return FAIL
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|----------|------------------------|------|
| Vertex shader source | [`addVS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L317-L341) | Computes `patchIndex` per vertex from `gl_VertexIndex`, `drawIndex`, and `PATCH_COUNT_PER_DRAW`. |
| Color / MRT fragment shader | [`getColorTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L343-L472) | Reads color attachment(s) through `colorAttachmentReadEXT`, applies the chained-patch rule, and writes the next value or an error marker. |
| Helper-class fragment shader | [`getHelperClassTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L474-L584) | Reads color plus depth or stencil, uses derivatives to validate helper-invocation reads, and writes to two color attachments. |
| MSAA sample-mask fragment shader | [`getSampleMaskTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L586-L672) | Iterates covered samples from `gl_SampleMaskIn[0]`, reads each sample through `colorAttachmentReadEXT(colorIn0, i)`, and writes the chained value or an error marker. |
| Depth fragment shader | [`getDepthTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L674-L742) | Reads depth through `depthAttachmentReadEXT` and color through `colorAttachmentReadEXT`, writes the chained depth-derived value, and optionally writes `gl_FragDepth` to force all samples. |
| Stencil fragment shader | [`getStencilTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L744-L789) | Reads stencil through `stencilAttachmentReadEXT` and color through `colorAttachmentReadEXT`, writes the chained stencil-derived value. |
| Compute shader | [`addCS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L826-L898) | Copies color attachment texels into a `uvec2` storage buffer for host readback; uses `texture2DMS` for multi-sample cases and `texture2D` for single-sample cases. |
| Pipeline state | [`generateGraphicsPipeline()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1219-L1440) | Builds the graphics pipeline with dynamic-rendering create info, multisample state, blend state, and depth/stencil state. The second helper-class pipeline disables writes to color0, depth, and stencil. |

The shader generator selects `OUTPUT_VECTOR_NAME`, `OUTPUT_BASIC_TYPE`, and `TILE_IMAGE_TYPE`
template parameters from the color format's texture channel class at
[`initPrograms()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L900-L944).
A floating-point or normalized format uses `vec4` / `float` / `attachmentEXT`; an unsigned
integer format uses `uvec4` / `uint` / `uattachmentEXT`; a signed integer format uses `ivec4` /
`int` / `iattachmentEXT`. The compute shader similarly selects a `texture2D`,
`utexture2D`, or `itexture2D` sampler (or the `*MS` variants for multi-sample cases).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color attachment(s) | Yes, in `generateAttachments()` | Yes, as color attachment | Cleared, written by fragment shader, read by compute | No, only via copy buffer | Stores the per-patch chained values; tile-image reads happen against this image. Up to two attachments for MRT and helper-class tests. |
| Depth/stencil attachment | Yes, in `generateAttachments()` | Yes, as depth/stencil attachment | Cleared, written by depth/stencil tests, read by fragment shader | No | Required by depth, stencil, and helper_class_depth/_stencil tests; the aspect mask and layout depend on the format. |
| Vertex buffer | Yes, in `generateVertexBuffer()` | Yes, vertex buffer binding 0 | Read by vertex shader | No | Provides one or two triangle patches per draw; helper-class tests render a degenerate first patch. |
| Copy storage buffer(s) | Yes, in `generateAttachments()` | Yes, descriptor binding 1 in compute | Written by compute shader, read by host | Yes | Holds `uvec2` values for every `(fx, fy, fs)`; the host scans this buffer to decide pass/fail. |
| Push constants | Yes, 4-byte range | Yes, push constant | Provides `drawIndex` to vertex and fragment shaders | No | Used to compute `patchIndex` per draw and to drive the chained-value logic. |
| Descriptor set (compute) | Yes, in `generateComputePipeline()` | Yes, descriptor set | Binds color attachment as `SAMPLED_IMAGE` and copy buffer as `STORAGE_BUFFER` | No | The compute shader uses `texelFetch` on the color attachment to copy its data into the host-visible buffer. |

## What Is Checked

### Device-side checks

The fragment shader is the only place where the test detects failures. For every fragment, it
writes either a "good" value (`out0.x = 0`, `out0.y = expected next value`) or an "error
marker" (`out0.x = 1`). The error marker is what survives into the host-visible copy buffer
when the tile-image read returned the wrong value or when the chained-value rule was violated.

The shader writes the error marker in three situations:

1. The previous value's `x` channel was not zero (already errored or already at the maximum).
2. The previous value did not match the expected chained value (`previous.y + 1 !=
   patchIndex + gl_SampleID + i`).
3. For helper-class tests, the derivative check detected an unexpected rasterization pattern.

The `msaa_sample_mask` fragment shader marks error if any covered sample disagrees with the
others or if the chained value does not match `patchIndex`.

### Host-side checks

The host-side pass/fail rule is in
[`checkResult()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1669-L1750).
For each render target, sample, and pixel:

- `getResultValue(fx, fy, fs, rt)` reads the host-visible copy buffer. If the `x` channel is
  nonzero, the fragment shader wrote the error marker and the function returns `0xFFFFFFFF`.
- `simulate(fx, fy, fs, rt)` computes the expected value for that pixel:
  - `msaa_sample_mask`: `totalLayerCount + rt` if the sample is covered, otherwise zero.
  - `stencil`: `totalLayerCount + rt` (stencil does not include `gl_SampleID`).
  - `helper_class_*`: `kDerivative1` on the diagonal, `kDerivative0` elsewhere.
  - Everything else: `totalLayerCount + rt + fs`.
- The comparison accepts the expected value or, for helper-class tests, accepts `kDerivative1`
  on the off-diagonal as well.
- 6-vertex-patch cases fill the whole framebuffer, so every pixel must match. 3-vertex-patch
  cases fill only a triangle, so the host only enforces the expected value inside the triangle
  and accepts zero or the expected value outside.

There is no tolerance: the `uvec2` values compared on the host are exactly equal or the case
fails.

## Behavior Parameter Identification

> **Behavior parameter:** `testType` (test-type group below the coherency direct child)
>
> **Candidate values:** `color`, `mrt`, `mrt_dynamic_index`, `msaa_sample_mask`,
> `helper_class_color`, `helper_class_depth`, `helper_class_stencil`, `depth`, `stencil`

The `coherent` / `non_coherent` direct child is a secondary axis: it changes the shader
qualifiers and inter-draw barriers but does not change *what is being tested*. The
`testType` axis is what determines whether the shader reads color, depth, stencil, MSAA per-
sample, or helper-invocation tile-image data, and each value exercises a distinct extension
feature.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `color` | Coherent or non-coherent `colorAttachmentReadEXT` returned a value that was not the value written by the most recent overlapping fragment for the same pixel/sample. |
| `mrt` | Coherent or non-coherent `colorAttachmentReadEXT` returned a wrong value for at least one of multiple color attachments. |
| `mrt_dynamic_index` | The dynamically-indexed `colorIn[i]` array form returned a value for the wrong attachment, or the implementation mis-indexed the tile-image descriptor. |
| `msaa_sample_mask` | `colorAttachmentReadEXT(colorIn0, sampleID)` returned a wrong value for a covered sample, or `shaderTileImageReadSampleFromPixelRateInvocation` is reported as supported but does not actually return per-sample values from a pixel-rate invocation. |
| `helper_class_color` | `colorAttachmentReadEXT` returned a wrong value when called from a helper invocation; `shaderTileImageReadFromHelperInvocation` is reported as supported but is not honored. |
| `helper_class_depth` | `depthAttachmentReadEXT` returned a wrong value when called from a helper invocation, or the helper-invocation read path does not cover depth. |
| `helper_class_stencil` | `stencilAttachmentReadEXT` returned a wrong value when called from a helper invocation, or the helper-invocation read path does not cover stencil. |
| `depth` | `depthAttachmentReadEXT` returned a wrong depth value, or the implementation does not correctly chain depth writes between overlapping fragments. |
| `stencil` | `stencilAttachmentReadEXT` returned a wrong stencil value, or the implementation does not correctly chain stencil writes between overlapping fragments. |

All nine test types share the same host-side pass/fail mechanism: a fragment shader writes
an error marker into the color attachment, the compute shader copies it to a host-visible
buffer, and `checkResult()` scans the buffer for any mismatch.

## Important Variations and Special Cases

### Coherency versus non-coherency

The `coherent` and `non_coherent` direct children exercise two extension features that differ
only in the shader qualifiers and the inter-draw memory barrier. The shader generator branches
on `m_testParam.coherent` to add the `non_coherent_*_attachment_readEXT` qualifiers, and the
host branches on the same flag to insert a `VkMemoryBarrier2KHR` between draw calls.

### Sample count and per-sample reads

For multi-sample cases other than `msaa_sample_mask`, the host enables sample shading
(`sampleShadingEnable = VK_TRUE` with `minSampleShading = 1.0`) so the fragment shader runs
once per covered sample. The shader then calls `colorAttachmentReadEXT(colorIn0, gl_SampleID)`
or `depthAttachmentReadEXT(gl_SampleID)`. `msaa_sample_mask` is the exception: it disables
sample shading, sets `pSampleMask = 0xaaaaaaaa`, and explicitly iterates covered samples from
`gl_SampleMaskIn[0]`. This verifies that pixel-rate fragment invocations can read per-sample
values when the implementation reports `shaderTileImageReadSampleFromPixelRateInvocation`.

### Helper-class two-draw structure

Helper-class tests always run two draw calls. The first draw uses the main pipeline; the
second draw uses a pipeline that disables writes to color0, depth, and stencil, so the
fragment shader runs entirely as helper invocations. The shader reads the previous value
through tile-image reads and uses `dFdxFine` / `dFdyFine` to distinguish diagonal from
off-diagonal pixels. The host's `simulate()` and `checkResult()` allow either valid outcome
for the diagonal because `max(dx, dy)` could be zero or one there.

### Multi-draw and multi-patch coverage

`single_draw` issues one draw call; `multi_draws` issues three draw calls. `single_patch`
uses one patch per draw; `multi_patches` uses three patches per draw. The expected value at
the end is `drawCount * patchCountPerDraw + rt + sampleID` (or `drawCount * patchCountPerDraw
+ rt` for stencil), so adding draws or patches raises the final expected value. Non-coherent
multi-patch cases are skipped because the implementation cannot guarantee non-coherent
visibility between fragment shader invocations of the same draw.

### Color format and amplifier

For normalized color formats (signed or unsigned fixed-point), the shader multiplies the
read value by an `amplifier` derived from the channel bit depth before rounding to an
integer, and divides the output by `1.0 / amplifier` so that the integer chained-value rule
can run without precision loss. The format filter at
[`vktShaderTileImageTests.cpp#L2117-L2177`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2117-L2177)
rejects color formats whose channel bit depth cannot represent `maxResultValue` to avoid
overflow, and the helper-class tests skip normalized color formats entirely to keep the
derivative logic simple.

### Mustpass coverage

The `vk-default` mustpass file
[`external/vulkancts/mustpass/main/vk-default/rasterization.txt`](../../../mustpass/main/vk-default/rasterization.txt)
lists every generated `dEQP-VK.rasterization.shader_tile_image.*` case. The first
`shader_tile_image` entry is at line 9582 and the tree covers every coherency, test-type,
sample-count, draw-count, patch-count, and format combination that survives pruning. Concrete
examples include `coherent.color.samples_1.single_draw.single_patch.r8g8b8a8_unorm` at line
9729, `coherent.depth.samples_1.single_draw.single_patch.d32_sfloat` at line 10488, and
`coherent.msaa_sample_mask.samples_2.multi_draws.multi_patches.a2b10g10r10_uint_pack32` at
line 12553.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| File-level comment describing test design | [`vktShaderTileImageTests.cpp#L25-L37`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L25-L37) | Authoritative comment on the chained-patch design and the per-sample-shading exception for `msaa_sample_mask`. |
| Test parameter struct | [`vktShaderTileImageTests.cpp#L97-L107`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L97-L107) | Defines the per-case state used by shader generation and the host runtime. |
| Support checks | [`ShaderTileImageTestCase::checkSupport()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L951-L1087) | Applies all feature, property, format, and sample-count gates. |
| Vertex shader | [`addVS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L317-L341) | Computes `patchIndex` from `gl_VertexIndex` and `drawIndex`. |
| Color / MRT fragment shader | [`getColorTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L343-L472) | Generates the chained-value read/write for `color`, `mrt`, and `mrt_dynamic_index`. |
| Helper-class fragment shader | [`getHelperClassTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L474-L584) | Generates the helper-invocation read with derivative validation. |
| MSAA sample-mask fragment shader | [`getSampleMaskTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L586-L672) | Generates the per-sample loop using `gl_SampleMaskIn[0]`. |
| Depth fragment shader | [`getDepthTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L674-L742) | Generates the chained depth-value read/write and `gl_FragDepth` write. |
| Stencil fragment shader | [`getStencilTestTypeFS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L744-L789) | Generates the chained stencil-value read/write. |
| Compute shader | [`addCS()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L826-L898) | Copies color attachment texels into a host-visible storage buffer. |
| Pipeline setup | [`generateGraphicsPipeline()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1219-L1440) | Builds the graphics pipeline and the helper-class pipeline variant. |
| Color and depth/stencil attachments | [`generateAttachments()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1442-L1524) | Creates the test images and views. |
| Vertex buffer | [`generateVertexBuffer()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1526-L1591) | Generates the per-patch triangle vertices. |
| Compute pipeline and descriptor set | [`generateComputePipeline()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1107-L1217) | Builds the compute pipeline used to copy color attachment data into host memory. |
| Dynamic rendering loop | [`rendering()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1752-L1956) | Drives the dynamic-rendering pass, draw loop, non-coherent barriers, and the final compute copy. |
| Expected-value simulation | [`simulate()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1622-L1667) | Computes the expected value for a given `(fx, fy, fs, rt)`. |
| Result comparison | [`checkResult()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1669-L1750) | Reads the host-visible copy buffer and decides pass/fail. |
| Test hierarchy generation | [`createShaderTileImageTestVariations()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L1968-L2189) | Builds the full coherency / test-type / sample-count / draw-count / patch-count / format matrix with pruning. |
| Test family registration | [`createShaderTileImageTests()`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L2193-L2200) | Creates the `shader_tile_image` root group. |
| Mustpass entry list | [`rasterization.txt`](../../../mustpass/main/vk-default/rasterization.txt) | Lists every `dEQP-VK.rasterization.shader_tile_image.*` case in `vk-default`. |

## Questions / Risk Points for User Audit

- [x] Keep the primary behavioral axis as the test-type group (`color`, `mrt`, etc.). The
  coherency direct child is the secondary axis because it changes qualifiers and barriers
  but not what is being tested.
- [x] Select three representative shader walkthroughs: `coherent.color` (default), `coherent.depth`
  (materially different because it adds `depthAttachmentReadEXT` and `gl_FragDepth`), and
  `coherent.msaa_sample_mask` (materially different because it iterates `gl_SampleMaskIn[0]`
  and calls per-sample `colorAttachmentReadEXT`). Helper-class and stencil paths are
  documented in the variation table instead of receiving their own walkthroughs.
- [x] The host comparison logic in `checkResult()` and `simulate()` is the authoritative
  source for verification claims. The expected value for non-helper, non-stencil cases is
  `totalLayerCount + rt + fs`, where `totalLayerCount = drawCount * patchCountPerDraw`.
- [x] The Vulkan spec chapters at `external/vulkan-docs/src/chapters/` are not present in
  this checkout. The Background Knowledge and Failure Cause Mapping sections are grounded in
  the CTS source comments at [`vktShaderTileImageTests.cpp#L25-L37`](../../../modules/vulkan/rasterization/vktShaderTileImageTests.cpp#L25-L37)
  and in the implementation paths identified above. Spec-grounded claims about coherent
  versus non-coherent tile-image reads are derived from the shader qualifiers and host
  barrier insertion behavior shown in the source.

## Conversion Notes for Final Wiki Rewrite

- Carry the primary behavioral axis conclusion (test-type group) into `## Behavior Parameters`
  with `### <test-type name> — <description>` subsections.
- Distill the Background Knowledge into a compact prerequisite list: `VK_EXT_shader_tile_image`
  tile-image reads, `VK_KHR_dynamic_rendering` lifetime, coherent versus non-coherent reads,
  helper-invocation semantics, and MSAA sample-rate reads.
- Carry the `### Failure Cause Mapping` table directly into the final page's
  `### Failure Cause Mapping`. Write `### Cause Analysis` fresh.
- Use the three selected representative CTS cases for `## Shader Analysis` and invoke
  `shader-analyzer` for each, ending with a `shader-disassembler` `#### SPIR-V` subsection.
- Move the source mapping table into the final `## Source Reference Appendix` and link
  specific functions inline where they support claims.
- Note in `## Background Knowledge` or `## Runtime Execution and Result Checking` that the
  spec chapters were unavailable and the source is the authoritative ground for spec claims.
