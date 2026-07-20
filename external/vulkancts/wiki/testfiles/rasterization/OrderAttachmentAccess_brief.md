# Understanding Brief: rasterization.rasterization_order_attachment_access / vktRasterizationOrderAttachmentAccessTests.cpp

This brief prepares a future rewrite of the `rasterization_order_attachment_access` Level-3 wiki page. It is
intentionally explanation-first and uses the source code as the primary authority.

The Vulkan spec chapter directory at `external/vulkan-docs/src/chapters/` is not present in this checkout. The
Background Knowledge and Failure Cause Mapping below are therefore grounded in CTS source comments and source-visible
Vulkan API usage (`VK_ARM_rasterization_order_attachment_access` / `VK_EXT_rasterization_order_attachment_access`,
subpass description flags, pipeline color-blend and depth-stencil create flags, subpass self-dependencies, and
`vkCmdPipelineBarrier` calls). Spec-language claims are kept conservative and tied to the exact API handles the source
manipulates.

## One-Sentence Test Purpose

This test checks whether fragment-shader reads of color, depth, or stencil attachment data through input attachments
observe earlier fragment writes to the same attachment within a subpass, either because the implementation advertises
rasterization-order attachment access or because an explicit pipeline barrier orders the writes and reads.

Core question: **if overlapping draws, primitives, or instances in the same subpass write to a color/depth/stencil
attachment that is also bound as an input attachment, does a later fragment shader invocation that performs
`subpassLoad` on that input attachment see the value an earlier overlapping invocation wrote?**

## Background Knowledge

### Rasterization order attachment access

By default, the Vulkan spec does not guarantee any ordering between fragment shader invocations that read an attachment
through an input attachment and other fragment invocations that write to that same attachment within a single subpass.
The `VK_ARM_rasterization_order_attachment_access` and `VK_EXT_rasterization_order_attachment_access` extensions opt in
to a rasterization-order guarantee for that subpass. The CTS source activates the guarantee in two places:

- subpass description flags `VK_SUBPASS_DESCRIPTION_RASTERIZATION_ORDER_ATTACHMENT_COLOR_ACCESS_BIT_ARM`,
  `..._DEPTH_ACCESS_BIT_ARM`, and `..._STENCIL_ACCESS_BIT_ARM` on the subpasses
  [vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1340-L1351);
- pipeline create flags `VK_PIPELINE_COLOR_BLEND_STATE_CREATE_RASTERIZATION_ORDER_ATTACHMENT_ACCESS_BIT_ARM`,
  `VK_PIPELINE_DEPTH_STENCIL_STATE_CREATE_RASTERIZATION_ORDER_ATTACHMENT_DEPTH_ACCESS_BIT_ARM`, and
  `..._STENCIL_ACCESS_BIT_ARM` on the graphics pipeline
  [vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L126-L133),
  [vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L226-L231),
  [vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L280-L285).

The feature is queried through `VkPhysicalDeviceRasterizationOrderAttachmentAccessFeaturesEXT` with the
`rasterizationOrderColorAttachmentAccess`, `rasterizationOrderDepthAttachmentAccess`, and
`rasterizationOrderStencilAttachmentAccess` feature bits
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L846-L916).

Why it matters here:

- The extension-ordered paths rely on this guarantee to make `subpassLoad` return the most recent overlapping write
  instead of an indeterminate older value.
- The explicit-barrier paths exercise the same shader behavior but order the writes and reads using a subpass
  self-dependency plus an explicit `vkCmdPipelineBarrier` between draws.

### Input attachment feedback within a subpass

An input attachment is a descriptor-bound view of an attachment that the fragment shader reads through `subpassLoad`.
When the same attachment is also written by the same subpass (as a color attachment or depth/stencil attachment), the
attachment acts as a feedback buffer: fragment invocations can observe values written by other invocations in the same
subpass. The CTS test uses this pattern in a two-subpass render pass:

- subpass 0: `m_inputAttachmentNum` input attachments that are also color attachments, plus an optional depth/stencil
  attachment when `getInputAttachmentNum() > getColorAttachmentNum()`
  [vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1308-L1322);
- subpass 1: a single-sample resolve subpass that reads back subpass 0's color attachments as input attachments and
  writes a 2-channel result that the host validates
  [vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L743-L792).

Why it matters here:

- The first subpass is where the rasterization-order property is actually tested. The shader reads the attachment, then
  writes a new value that depends on what was read.
- The second subpass is a host-readable funnel: it loads each input attachment and writes the expected total to
  `out0.y` only if every pixel agrees with the expected running total.

### Subpass self-dependency and explicit pipeline barriers

When the test uses explicit synchronization (`m_explicitSync = true`, registered as the `multi_draw_barriers` leaf),
the source adds a subpass self-dependency on subpass 0 from `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT` to
`VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT` with `VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT` →
`VK_ACCESS_INPUT_ATTACHMENT_READ_BIT`, plus a depth/stencil analog when the case has a depth/stencil attachment
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1327-L1337).
The host loop then inserts an explicit `vkCmdPipelineBarrier` between consecutive overlapping draws so that the prior
draw's color/depth/stencil writes are visible to the next draw's input-attachment reads
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1617-L1633).

When the test uses extension-ordered access (the other four leaf cases), the source instead sets the
rasterization-order subpass description flags and pipeline create flags and inserts no inter-draw barrier. The
rasterization-order guarantee replaces the explicit barrier.

Why it matters here:

- The contrast between these two synchronization forms is the central design of the test family. The same shader source
  is used for both forms; only the synchronization mechanism differs.
- Failures on the explicit-barrier path point to a different implementation surface (subpass self-dependency handling
  and `vkCmdPipelineBarrier` between draws within a subpass) than failures on the extension-ordered path (subpass
  description flags, pipeline create flags, and feature bits).

### Overlap patterns

The test exercises five overlap shapes that change which invocations race on the same attachment
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1715-L1756):

| Leaf name | `explicitSync` | `overlapDraws` | `overlapPrimitives` | `overlapInstances` | What overlaps |
|---|---|---|---|---|---|
| `multi_draw_barriers` | true | true | false | false | Multiple draws in one subpass, separated by explicit barriers. |
| `multi_draw` | false | true | false | false | Multiple draws in one subpass, extension-ordered. |
| `multi_primitives` | false | false | true | false | One draw with multiple overlapping primitives rasterized in primitive order. |
| `multi_instances` | false | false | false | true | One draw with multiple overlapping instances rasterized in instance order. |
| `all` | false | true | true | true | All overlap dimensions combined, extension-ordered. |

The generator constants `ELEM_NUM = 6`, `PRIMITIVE_NUM = overlapPrimitives ? 6 : 1`,
`INSTANCE_NUM = overlapInstances ? 6 : 1`, and `DRAW_NUM = overlapDraws ? 6 : 1` flow into the shader through template
parameters and into the draw loop through `numDraws`, `numPrimitives`, and `numInstances`
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1608-L1635),
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L713-L721).

Why it matters here:

- The overlap pattern is the primary behavioral axis. Each pattern stresses a different rasterization-order surface:
  draw-to-draw, primitive-to-primitive, instance-to-instance, or all combined.
- Only `multi_draw_barriers` uses explicit barriers; the other four depend on the extension.

## One Concrete Example

### `multi_draw_barriers` with float color, one attachment, one sample

Representative test name from mustpass:

```text
dEQP-VK.rasterization.rasterization_order_attachment_access.format_float.attachments_1_samples_1.multi_draw_barriers
```

Simplified behavior for this case:

1. The render pass has two subpasses. Subpass 0 has one color attachment that is also bound as input attachment 0. A
   subpass self-dependency orders `COLOR_ATTACHMENT_OUTPUT` writes before `INPUT_ATTACHMENT_READ` reads within subpass 0.
2. The host clears the color image to zero, then records six overlapping draws in subpass 0. Between consecutive draws
   it inserts `vkCmdPipelineBarrier` with `COLOR_ATTACHMENT_WRITE` → `INPUT_ATTACHMENT_READ` and
   `COLOR_ATTACHMENT_OUTPUT` → `FRAGMENT_SHADER`.
3. Each fragment invocation reads `previous[0] = subpassLoad(in0).xy`. The `curIndex` is computed from `drawCur` (a
   push constant), `instanceCur`, and `primitiveCur`. If the previous write is zero and `curIndex` is zero, the shader
   writes `out0.y = 1 + zero + gl_SampleID + 0`. Otherwise, if `previous[0].y == curIndex + gl_SampleID + 0`, the
   shader writes `out0.y = previous[0].y + 1 + zero`. Otherwise it writes `out0.y = 0; out0.x = 1`.
4. After six draws, every pixel should have `out0.y == 6` (because `numDraws * numPrimitives / 2 * numInstances = 6 * 1 * 1 = 6`) and `out0.x == 0`.
5. Subpass 1 reads the color attachment through input attachment 0 and copies the per-pixel value to its color output.
6. The host copies the subpass 1 color output to a host-visible buffer and checks every pixel: `pixel[0] == 0 &&
   pixel[1] == 6` passes; any deviation fails.

Conceptual GLSL, reconstructed from the generator:

```glsl
layout(set = 0, binding = 0, input_attachment_index = 0) uniform subpassInput in0;
layout(location = 0) out vec2 out0;
layout(push_constant) uniform ConstBlock { uint drawCur; };

void main()
{
    uint instanceCur  = uint(round(gl_FragCoord.z * 256.0));
    uint primitiveCur = uint(prim_id) / 2u;
    uint primitiveNum = 1u;
    uint instanceNum  = 1u;
    uint drawNum      = 6u;
    uint curIndex     = drawCur * instanceNum * primitiveNum + instanceCur * primitiveNum + primitiveCur;
    uint total        = drawNum * instanceNum * primitiveNum;

    vec2 previous[1];
    previous[0] = subpassLoad(in0).xy;

    if (previous[0].y == 0 && curIndex == 0) {
        out0.y = previous[0].y + (1u + zero + gl_SampleID + 0u);
        out0.x = previous[0].x;
    } else if (previous[0].y == curIndex + gl_SampleID + 0u) {
        out0.y = previous[0].y + 1 + zero;
        out0.x = previous[0].x;
    } else {
        out0.y = 0u;
        out0.x = 1u;
    }
}
```

Important simplifications:

- The real generator includes `pre_fetch_loop` and `post_fetch_loop` busy work around the `subpassLoad` to give the
  rasterizer freedom in scheduling the fragment invocations.
- The depth and stencil generators are structurally similar but write `gl_FragDepth` for depth cases and read the
  depth/stencil input attachment's `.x` channel for stencil cases.

## End-to-End Test Flow

```text
1. [host] register and generate case hierarchy
   1.1 create the `rasterization_order_attachment_access` root
   1.2 generate `format_float` and `format_integer` children with attachment counts 1, 4, 8
   1.3 generate `depth` and `stencil` children with attachment count 1 (plus the DS attachment)
   1.4 for each child, expand `samples_1`, `samples_2`, `samples_4`, `samples_8`, `samples_16`, `samples_32`, `samples_64`
   1.5 under each sample-count group, add the five leaf cases `multi_draw_barriers`, `multi_draw`, `multi_primitives`, `multi_instances`, `all`

2. [host] prune unsupported cases at checkSupport time
   2.1 require instance extension `VK_KHR_get_physical_device_properties2`
   2.2 for non-explicit-sync cases, require `VK_ARM_rasterization_order_attachment_access` or `VK_EXT_rasterization_order_attachment_access`
   2.3 for non-explicit-sync color cases, require `rasterizationOrderColorAttachmentAccess`
   2.4 for non-explicit-sync depth cases, require `rasterizationOrderDepthAttachmentAccess`
   2.5 for non-explicit-sync stencil cases, require `rasterizationOrderStencilAttachmentAccess`
   2.6 require `sampleRateShading` when sample count is not 1
   2.7 require framebuffer and sampled-image sample-count support for the requested sample count
   2.8 require `maxFragmentOutputAttachments` and `maxPerStageDescriptorInputAttachments` >= attachment count
   2.9 require a supported combined depth/stencil format for depth and stencil cases

3. [host] generate shader program artifacts
   3.1 generate `vert1`, `vert2` vertex shaders
   3.2 generate `frag` fragment shader for subpass 0 (color, depth, or stencil variant)
   3.3 generate `frag_resolve` fragment shader for subpass 1
   3.4 specialize `PRIMITIVE_NUM`, `INSTANCE_NUM`, `DRAW_NUM`, `ATT_NUM`, `SAMPLE_NUM`, `SCALAR_NAME`, `VEC_NAME`, `SUBPASS_INPUT` through StringTemplate

4. [host] create and bind resources
   4.1 create color images for subpass 0 (1, 4, or 8 attachments for color; 1 for depth/stencil) with INPUT_ATTACHMENT | COLOR_ATTACHMENT | TRANSFER usage
   4.2 create a depth/stencil image with INPUT_ATTACHMENT | DEPTH_STENCIL_ATTACHMENT | TRANSFER usage for depth and stencil cases
   4.3 create one single-sample color image for subpass 1
   4.4 create a vertex buffer with ELEM_NUM*2 triangle pairs covering the 8x8 framebuffer
   4.5 create a host-visible result buffer of WIDTH*HEIGHT*UVec2
   4.6 create descriptor set with INPUT_ATTACHMENT descriptors for every input attachment

5. [host] build render pass
   5.1 attachment descriptions use LOAD/STORE for color and stencil, GENERAL layout
   5.2 subpass 0 references all input attachments as both input and color (and depth/stencil when applicable)
   5.3 subpass 1 references subpass 0's color attachments as input attachments and writes the single-sample resolve target
   5.4 add a subpass 0 → subpass 1 dependency on COLOR_ATTACHMENT_OUTPUT / COLOR_ATTACHMENT_WRITE → FRAGMENT_SHADER / INPUT_ATTACHMENT_READ with BY_REGION bit
   5.5 explicit-sync cases add a subpass 0 self-dependency on COLOR_ATTACHMENT_OUTPUT / COLOR_ATTACHMENT_WRITE (and EARLY/LATE_FRAGMENT_TESTS / DEPTH_STENCIL_ATTACHMENT_WRITE for DS cases) → FRAGMENT_SHADER / INPUT_ATTACHMENT_READ
   5.6 extension-ordered cases set the rasterization-order subpass description flags on both subpasses

6. [host] build pipelines
   6.1 subpass 0 pipeline uses `vert1` + `frag` with push constants for `drawCur` and sample shading enabled
   6.2 explicit-sync color cases set color-blend create flags to 0
   6.3 extension-ordered color cases set VK_PIPELINE_COLOR_BLEND_STATE_CREATE_RASTERIZATION_ORDER_ATTACHMENT_ACCESS_BIT_ARM
   6.4 extension-ordered depth cases set VK_PIPELINE_DEPTH_STENCIL_STATE_CREATE_RASTERIZATION_ORDER_ATTACHMENT_DEPTH_ACCESS_BIT_ARM
   6.5 extension-ordered stencil cases set VK_PIPELINE_DEPTH_STENCIL_STATE_CREATE_RASTERIZATION_ORDER_ATTACHMENT_STENCIL_ACCESS_BIT_ARM
   6.6 subpass 1 pipeline uses `vert2` + `frag_resolve`

7. [host] record command buffer
   7.1 layout-transfer barrier and clear all subpass 0 color images to zero
   7.2 layout-transfer barrier and clear depth/stencil image to 0/0 when present
   7.3 memory barrier TRANSFER_WRITE → (FRAGMENT_SHADER | COLOR_ATTACHMENT_OUTPUT | EARLY/LATE_FRAGMENT_TESTS for DS) with the appropriate access masks
   7.4 begin render pass, bind subpass 0 pipeline, bind descriptor set, bind vertex buffer
   7.5 for each of numDraws iterations:
       - push `drawCur = i` to the fragment shader (and vertex shader for DS cases)
       - explicit-sync only, i > 0: insert pipeline barrier COLOR_ATTACHMENT_WRITE → INPUT_ATTACHMENT_READ (and DEPTH_STENCIL_ATTACHMENT_WRITE → INPUT_ATTACHMENT_READ for DS) on each subpass 0 attachment
       - cmdDraw with numPrimitives * 3 vertices and numInstances instances
   7.6 advance to subpass 1, bind subpass 1 pipeline, bind descriptor set, draw a single 6-vertex fullscreen quad
   7.7 end render pass
   7.8 copy subpass 1 color image to host-visible result buffer

8. [device] subpass 0 fragment shader executes for each draw
   8.1 compute curIndex from drawCur, instanceCur, primitiveCur
   8.2 perform pre_fetch_loop busy work
   8.3 subpassLoad the input attachment(s)
   8.4 perform post_fetch_loop busy work
   8.5 if previous[i].y == 0 && curIndex == 0: write out[i].y = 1 + zero + gl_SampleID + i (depth cases also write gl_FragDepth)
   8.6 else if previous[i].y == curIndex + gl_SampleID + i: write out[i].y = previous[i].y + 1 + zero (depth cases also write gl_FragDepth)
   8.7 else: write out[i].y = 0; out[i].x = 1 (error marker)
   8.8 stencil cases: same logic but the validation condition is `ds.x == curIndex` against the stencil input attachment
   8.9 depth cases: validation also accepts ds.x within ±threshold of the expected 0.125 * (curIndex-1) / total + gl_SampleID/128.0

9. [device] subpass 1 fragment shader executes once
   9.1 for each input attachment, subpassLoad it
   9.2 if every sample's val == (total, i) write out0 = (0, total)
   9.3 otherwise forward the first mismatched val to out0

10. [host] inspect results
    10.1 invalidate the result buffer allocation
    10.2 scan every pixel of WIDTH*HEIGHT
    10.3 pass iff pixel[0] == 0 && pixel[1] == numDraws * numPrimitives / 2 * numInstances for every pixel
    10.4 fail on the first pixel that deviates
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

| Artifact | Generated/loaded where | Role |
|----------|------------------------|------|
| Color fragment shader `frag` | [AttachmentAccessOrderColorTestCase::addShadersInternal](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L425-L507) | Subpass 0 shader for `format_float` and `format_integer` cases; reads N input attachments, writes N color outputs. |
| Depth fragment shader `frag` | [AttachmentAccessOrderDepthTestCase::addShadersInternal](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L508-L618) | Subpass 0 shader for `depth` cases; reads color and depth/stencil input attachments, writes one color output and `gl_FragDepth`. |
| Stencil fragment shader `frag` | [AttachmentAccessOrderStencilTestCase::addShadersInternal](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L619-L711) | Subpass 0 shader for `stencil` cases; reads color and depth/stencil input attachments, writes one color output; no `gl_FragDepth` write. |
| Resolve fragment shader `frag_resolve` | [AttachmentAccessOrderTestCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L743-L792) | Subpass 1 shader; reads all subpass 0 color attachments as input attachments and forwards either the expected total or a mismatched value. |
| Simple vertex shader `vert2` | [AttachmentAccessOrderTestCase::addSimpleVertexShader](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L403-L423) | Used by subpass 1; emits `prim_id = gl_VertexIndex / 3` and `gl_Position` from `v_position`. |
| Depth-aware vertex shader `vert1` | [AttachmentAccessOrderDepthTestCase::addShadersInternal](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L511-L535) (also used by stencil) | Subpass 0 vertex shader for DS cases; computes `instance_index` and `curIndex` and writes `gl_Position.z = 0.125 * curIndex / indexNum` so depth varies per draw/instance/primitive. |
| Pipeline state | [AttachmentAccessOrderTestInstance::RenderSubpass::createPipeline](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1056-L1189) | Graphics pipeline with sample shading, additive blend, depth/stencil state with `VK_STENCIL_OP_INCREMENT_AND_WRAP`, and the rasterization-order create flags when extension-ordered. |
| Render pass | [AttachmentAccessOrderTestInstance::createRenderPass](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1280-L1367) | Two-subpass render pass with subpass 0 self-dependency for explicit-sync cases and rasterization-order subpass flags for extension-ordered cases. |

Important distinction: GLSL `previous[]` and the per-pixel running total live in attachment memory, not in
shader-local storage. The fragment shader reads and writes the same attachment through different paths
(input-attachment read and color/depth/stencil write).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Subpass 0 color image(s) | Yes, 1/4/8 images for color cases or 1 for DS cases | Yes, as color attachment and input attachment | Cleared to zero by host, written by subpass 0 fragment shader, read back as input attachment in subpass 0 and subpass 1 | No | The feedback target whose rasterization-order behavior is being tested. |
| Depth/stencil image | Yes, for `depth` and `stencil` cases | Yes, as depth/stencil attachment and input attachment | Cleared to 0/0, written by `gl_FragDepth` or `VK_STENCIL_OP_INCREMENT_AND_WRAP`, read as input attachment | No | Carries the depth or stencil value the test tries to observe through an input attachment. |
| Subpass 1 color image | Yes, single-sample | Yes, as color attachment | Written by subpass 1 fragment shader, copied to result buffer | Yes (via copyImageToBuffer) | The only attachment that the host reads; carries the per-pixel validation result. |
| Vertex buffer | Yes, host-visible | Yes, as vertex buffer | Read by vertex shader | No | Carries `ELEM_NUM*2` overlapping triangle pairs covering the 8x8 framebuffer. |
| Result buffer | Yes, host-visible | Yes, as transfer destination | Receives copied subpass 1 color image | Yes | The host scans this buffer to decide pass/fail. |
| Descriptor set | Yes | Yes | Binds all subpass 0 attachments as INPUT_ATTACHMENT descriptors | No | Connects attachment image views to the fragment shader's `subpassLoad` calls. |
| Push constants | Yes, 4 bytes | Yes | `drawCur` supplied to fragment shader (and vertex shader for DS cases) per draw | No | Lets the fragment shader compute `curIndex` from the current draw index. |

## What Is Checked

### Device-side checks

The device-side check lives in the subpass 1 fragment shader
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L743-L792).
For every pixel and (for multisample cases) every sample, it loads each subpass 0 color attachment as an input
attachment and compares its `(x, y)` channels against the expected `(0, totalNum + i)` (single-sample) or
`(0, totalNum + i + sample)` (multisample). If any sample deviates, the subpass 1 shader forwards the deviating value
to its color output. Otherwise it writes `(0, totalNum)`.

| Test family | Device-side pass condition |
|-------------|----------------------------|
| `format_float` | Each subpass 0 color attachment ends with `out0.y == totalNum + i` and `out0.x == 0` for every pixel and sample. |
| `format_integer` | Same as `format_float`, with `uvec2`/`usubpassInput` types and integer attachment format. |
| `depth` | The depth/stencil input attachment's depth channel ends with the expected `0.125 * (curIndex-1) / total + gl_SampleID / 128.0` per pixel and sample; the color output reports total success. |
| `stencil` | The depth/stencil input attachment's stencil channel ends with `curIndex` per pixel and sample; the color output reports total success. |

### Host-side checks

The host calls `validateResults(numDraws, numPrimitives, numInstances)`
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1658-L1699)
after `submitCommandsAndWait`. It invalidates the result buffer, then scans every pixel of the `WIDTH * HEIGHT = 8 * 8`
buffer:

- For integer cases, each `tcu::UVec2` pixel must satisfy `pixel[0] == 0 && pixel[1] == numDraws * numPrimitives / 2 * numInstances`.
- For float cases, each `tcu::Vec2` pixel must satisfy `pixel[0] == 0 && pixel[1] == (float)(numDraws * numPrimitives / 2 * numInstances)`.
- The first failing pixel stops the scan and returns `QP_TEST_RESULT_FAIL`.

There is no tolerance on the host side; depth-case tolerance is applied inside the subpass 0 fragment shader's depth
comparison, not in the host scan.

## Behavior Parameter Identification

> **Behavior parameter:** overlap pattern (the registered leaf name)
>
> **Candidate values:** `multi_draw_barriers`, `multi_draw`, `multi_primitives`, `multi_instances`, `all`

The attachment class (`format_float`, `format_integer`, `depth`, `stencil`) is a secondary axis. It changes which
attachment aspect is being read back (color float, color integer, depth, or stencil) and which feature bit and pipeline
create flag the case requires, but the core ordering question is the same across all four classes.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `multi_draw_barriers` | The implementation did not honor the subpass self-dependency or the explicit `vkCmdPipelineBarrier` between draws within subpass 0, so a later draw's `subpassLoad` observed a stale attachment value. |
| `multi_draw` | The implementation did not honor the rasterization-order color-attachment access guarantee across consecutive draws within a subpass. |
| `multi_primitives` | The implementation did not honor the rasterization-order guarantee across primitives within a single draw, so a fragment's `subpassLoad` observed a value from a non-most-recent overlapping primitive. |
| `multi_instances` | The implementation did not honor the rasterization-order guarantee across instances within a single draw, so a fragment's `subpassLoad` observed a value from a non-most-recent overlapping instance. |
| `all` | The implementation did not honor the rasterization-order guarantee when draws, primitives, and instances all overlap simultaneously. |

All five values share a common host-side validation surface: a nonzero `pixel[0]` or wrong `pixel[1]` in the result
buffer. The distinction between values is which rasterization-order surface the failing case exercises.

## Important Variations and Special Cases

### Attachment class differences

The four attachment classes use three different shader generators:

- `format_float` and `format_integer` share `AttachmentAccessOrderColorTestCase::addShadersInternal`. They differ only
  in the type tokens substituted through `StringTemplate`: `subpassInput`/`subpassInputMS` vs
  `usubpassInput`/`usubpassInputMS`, `vec` vs `uvec`, `float` vs `int`, and the host-side color format
  `VK_FORMAT_R32G32_SFLOAT` vs `VK_FORMAT_R32G32_UINT`.
- `depth` uses `AttachmentAccessOrderDepthTestCase::addShadersInternal`. Its shader writes `gl_FragDepth` per draw and
  per sample, reads the depth/stencil attachment as input attachment 1, and applies a small floating-point threshold
  when comparing the loaded depth against the expected depth.
- `stencil` uses `AttachmentAccessOrderStencilTestCase::addShadersInternal`. Its shader does not write `gl_FragDepth`
  and instead reads the stencil value (as an integer channel from the depth/stencil input attachment) and compares it
  exactly against `curIndex`.

### Sample count and sample shading

All cases enable `sampleShadingEnable = VK_TRUE` with `minSampleShading = 1.0` in the pipeline
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1106-L1116).
The shader uses `gl_SampleID` to differentiate per-sample writes, so a multisample case requires that each sample's
`subpassLoad` observes the per-sample write of the most recent overlapping invocation. Multisample cases additionally
require the `sampleRateShading` feature.

### Color attachment count

`format_float` and `format_integer` cases expand an `attachments_1_`, `attachments_4_`, or `attachments_8_` prefix
that controls `m_inputAttachmentNum`. The shader declares N input attachments and N color outputs and writes them in
lockstep. The subpass 1 resolve shader checks every attachment independently and forwards any mismatch. The host-side
limit checks `maxFragmentOutputAttachments` and `maxPerStageDescriptorInputAttachments` against this count.

### Subpass 1 is not the tested subpass

Subpass 1 always uses a single-sample attachment and a single draw. Its only purpose is to funnel the per-pixel
result of subpass 0 into a host-readable buffer. The rasterization-order property is not exercised in subpass 1.

### Stencil write mechanism

The stencil pipeline state uses `VK_STENCIL_OP_INCREMENT_AND_WRAP` for both `failOp`, `passOp`, and `depthFailOp`, with
`VK_COMPARE_OP_ALWAYS`
[vktRasterizationOrderAttachmentAccessTests.cpp](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1142-L1150).
The stencil value therefore increments by one for every fragment that passes the stencil test, regardless of depth
outcome. The stencil-case fragment shader reads this counter through the depth/stencil input attachment and checks it
against `curIndex`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test family factory | [createRasterizationOrderAttachmentAccessTests](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1831-L1852) | Builds the four direct children of the test family root. |
| Attachment-count expansion | [createRasterizationOrderAttachmentAccessFormatTests](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1802-L1829) | Builds `format_float`/`format_integer` with attachment counts 1/4/8. |
| Sample-count and leaf expansion | [createRasterizationOrderAttachmentAccessTestVariations](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1703-L1800) | Builds `samples_*` groups and the five leaf cases. |
| Leaf case table | [leafTestCreateParams](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1715-L1756) | Names and overlap/explicit-sync flags for each leaf. |
| Color fragment shader generator | [AttachmentAccessOrderColorTestCase::addShadersInternal](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L425-L507) | Generates the `format_float` and `format_integer` subpass 0 fragment shaders. |
| Depth fragment shader generator | [AttachmentAccessOrderDepthTestCase::addShadersInternal](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L508-L618) | Generates the `depth` subpass 0 fragment shader with `gl_FragDepth`. |
| Stencil fragment shader generator | [AttachmentAccessOrderStencilTestCase::addShadersInternal](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L619-L711) | Generates the `stencil` subpass 0 fragment shader. |
| Resolve shader generator | [AttachmentAccessOrderTestCase::initPrograms](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L713-L793) | Generates subpass 1 fragment shader and selects type tokens. |
| Support gates | [AttachmentAccessOrderTestCase::checkSupport](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L832-L917) | Applies instance/device/feature/format/sample-count/limit gates. |
| Render pass construction | [AttachmentAccessOrderTestInstance::createRenderPass](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1280-L1367) | Builds the two-subpass render pass with explicit-sync self-dependency or rasterization-order subpass flags. |
| Pipeline construction | [AttachmentAccessOrderTestInstance::RenderSubpass::createPipeline](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1056-L1189) | Builds the graphics pipeline with rasterization-order create flags and stencil increment-and-wrap state. |
| Attachment creation | [AttachmentAccessOrderTestInstance::RenderSubpass::createAttachments](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L951-L1054) | Creates color and depth/stencil images and views. |
| Runtime command buffer | [AttachmentAccessOrderTestInstance::iterate](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1548-L1656) | Clears attachments, runs subpass 0 with the explicit-sync barrier loop, runs subpass 1, copies result. |
| Host-side validation | [AttachmentAccessOrderTestInstance::validateResults](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1658-L1699) | Scans the result buffer for the first failing pixel. |
| Mustpass examples | [rasterization.txt](../../../mustpass/main/vk-default/rasterization.txt#L9302-L9351) | Concrete `depth.samples_*` and `format_float.attachments_1_samples_*` test names. |

## Questions / Risk Points for User Audit

- [x] The shader source for `multi_draw_barriers` and `multi_draw` is identical for the same attachment class, sample
  count, and attachment count; only the synchronization mechanism differs. The page should therefore use one color
  walkthrough and one depth or stencil walkthrough rather than a separate walkthrough for `multi_draw`.
- [x] The host validation `numDraws * numPrimitives / 2 * numInstances` is integer arithmetic. With `ELEM_NUM = 6` and
  multi-primitive overlap (`numPrimitives = 12`), `numPrimitives / 2 = 6` exactly, so there is no rounding ambiguity.
- [x] The subpass 1 resolve shader's multisample branch checks `val.y != totalNum + i + sample` per sample and forwards
  any mismatched `(val.x, val.y)` to `out0`. The host then checks `pixel[1] == numDraws * numPrimitives / 2 *
  numInstances`, which equals `totalNum` for single-sample cases and the per-sample expected value for multisample
  cases. Confirmed against [validateResults](../../../modules/vulkan/rasterization/vktRasterizationOrderAttachmentAccessTests.cpp#L1658-L1699).
- [x] The depth shader's tolerance comparison uses a fixed `0.0000001` threshold. The host does not re-check depth with
  tolerance; the host only checks the color output that the subpass 0 shader wrote when the depth comparison passed.
- [ ] The Vulkan spec chapter directory is missing from this checkout; spec-language claims above are tied to API
  handles the source manipulates but were not cross-checked against canonical spec wording.

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge into a compact prerequisite list covering rasterization-order attachment access,
  input-attachment feedback, subpass self-dependency vs explicit pipeline barriers, and the overlap-pattern axis.
- Use two representative shader walkthroughs:
  1. `format_float.attachments_1_samples_1.multi_draw_barriers` — the simplest color case with explicit
     synchronization; demonstrates the input-attachment read + color-write feedback pattern that all color cases share.
  2. `depth.samples_1.multi_draw` — the depth variant; demonstrates the materially different shader that writes
     `gl_FragDepth` and reads the depth/stencil input attachment with a tolerance comparison.
- The stencil variant is described in the Behavior Parameters section rather than getting a third walkthrough, since
  its shader structure is close to the depth variant and the difference (exact stencil comparison vs tolerance-based
  depth comparison) is best explained as a parameter variation.
- Carry the `### Failure Cause Mapping` table directly into the final page. Write `### Cause Analysis` fresh during the
  rewrite, with subsections grouped by the failure surface (explicit barrier handling, rasterization-order guarantee,
  stencil/depth write mechanism, host-side scan) rather than by overlap pattern.
- Move detailed support-gate and pruning rules into the Case Pruning section.
- Move detailed source mapping into the Source Reference Appendix.
- Do not copy the beginner-friendly prose verbatim; convert it to Level-3 wiki style.
