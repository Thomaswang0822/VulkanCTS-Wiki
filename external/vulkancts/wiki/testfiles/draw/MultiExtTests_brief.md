## One-Sentence Test Purpose

This brief explains how `multi_draw` checks that the `VK_EXT_multi_draw` commands execute an ordered packed sequence of ordinary or indexed draws with the intended record, instance, view, and shader-stage behavior.

## Background Knowledge

### Multi-draw records

`vkCmdDrawMultiEXT` receives an array of `VkMultiDrawInfoEXT` records. `vkCmdDrawMultiIndexedEXT` receives `VkMultiDrawIndexedInfoEXT` records. Each command executes the requested record count in order, using the supplied byte stride to locate successive records. The draw count may be zero.

For indexed multi-draw, a non-null `pVertexOffset` supplies one offset for every draw and causes the record-level `vertexOffset` members to be ignored. A null pointer makes the command read each record-level offset.

Why it matters here:

- The case matrix checks contiguous records, padded records, and a legal zero-stride form that reuses one record.
- Indexed cases test both offset selection rules and a packed form that stores only the portion used when the common offset pointer is present.

### Color, depth, and stencil observations

A final color value can show which primitive won a pixel, but it cannot always show how many earlier operations occurred. Depth testing selects a surviving triangle among overlapping geometry. Stencil increment-and-wrap provides a separate count of the expected stencil-writing fragments.

Why it matters here:

- Mosaic geometry makes the expected color vary per pixel.
- Overlapping geometry makes the depth-selected color uniform while stencil still exposes repeated draw effects.

## One Concrete Example

Consider `dEQP-VK.draw.renderpass.multi_draw.mosaic.indexed_random.one_draw.standard_stride.2_instances_base_3.vert_only.single_view.offset_6`.

The host packs one indexed draw record and supplies a non-null common vertex-offset pointer with value 6. It uploads 1024 small triangles, with padding that makes the offset meaningful, and runs two instances starting at instance index 3. The vertex shader encodes the draw or primitive identity in red and green and encodes the highest instance index in blue. The host reads color and stencil, then compares every pixel to the CPU reference for this parameter path.

The `indexed_random` record members contain random offset values, but the non-null common pointer must override them. This makes the case sensitive to the override rule without depending on a particular record-member value.

## End-to-End Test Flow

```text
[host] choose mesh, command form, draw count, stride, instance range, stage path, view mode, draw-ID mode, and indexed offset mode
[host] require the extension and each selected feature
[host] generate GLSL and create the color, depth/stencil, vertex, optional index, and host-visible output resources
[host] generate 1024 mosaic or overlapping triangles and pack multi-draw records
[host] record a legacy-render-pass or dynamic-rendering command sequence
[device] execute vkCmdDrawMultiEXT or vkCmdDrawMultiIndexedEXT and write integer color plus stencil
[host] transition and copy color and stencil aspects to host-visible buffers
[host] construct color and stencil references for each pixel and view layer
[host] compare readback exactly and report a color or stencil mismatch
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`MultiDrawTest::initPrograms` generates vertex and fragment GLSL for every case. The vertex shader writes the input position and an integer color. It derives the red and green components from `gl_DrawID` when draw-ID mode is enabled, otherwise from `gl_VertexIndex / 3`; blue derives from `gl_InstanceIndex`; alpha derives from `gl_ViewIndex` in multiview cases. The fragment shader copies that integer value to the color attachment.

Tessellation and geometry variants generate pass-through stages that retain the same position and integer interface. They exercise the multi-draw result through those selected graphics-stage paths.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | vertex shader reads it | no | Holds 1024 generated triangles and any offset padding. |
| Index buffer | indexed cases | yes | indexed draw reads it | no | Reverses triangle order and makes indexed offset cases observable. |
| Packed draw-info memory | yes | command argument | multi-draw command reads it | no | Supplies the ordered draw records and stride layout. |
| Unsigned color image | yes | color attachment | fragment shader writes it | yes | Records encoded draw or primitive, instance, and layer identity. |
| Depth/stencil image | yes | depth/stencil attachment | fixed function reads and writes it | stencil aspect only | Selects overlap results and counts expected work. |
| Output buffers | yes | transfer destination | transfer writes them | yes | Provide host-visible color and stencil readback per layer. |

## What Is Checked

- The host generates an exact reference color and stencil value for every pixel and each multiview layer.
- Color channels encode the expected draw or primitive identity, highest instance index, and view layer. The test compares all four channels with zero threshold.
- Stencil uses the expected number of increment-and-wrap operations. The test compares the copied stencil aspect with zero threshold.
- A case passes only if both comparisons pass. Color and stencil mismatches report separate failure messages.

## Behavior Parameter Identification

> **Behavior parameter:** mesh layout
>
> **Candidate values:** `mosaic`, `overlapping`

`mosaic` and `overlapping` choose distinct observation mechanisms. The remaining registered dimensions configure legal command, storage, invocation, and execution-path variations within those mechanisms.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `mosaic` | Incorrect multi-draw record selection, stride advancement, indexed vertex-offset handling, draw-ID propagation, or per-pixel reference/readback handling. |
| `overlapping` | Incorrect ordered multi-draw execution, depth or stencil interaction, record selection, or the shared reference/readback handling. |

## Important Variations and Special Cases

- `no_draws` and `no_instances` preserve clear color and zero stencil because no drawable work reaches the attachments.
- `stride_zero` intentionally reuses one draw record. Its expected mosaic coverage, visible value, and stencil increments differ from nonzero-stride cases.
- For more than one draw, the source only retains strides that meet the commands' four-byte alignment and minimum-record-size requirements.
- Indexed variants use `mixed`, `random`, and `packed` offset representations. The first uses record-level offsets; the latter two use a common offset pointer, with `packed` using the smaller non-indexed-sized record layout plus required end padding.
- Dynamic-rendering secondary-command-buffer registrations use a reduced `mosaic`, one-draw, random-offset matrix. Nested-secondary parent configurations do not register this family.
- The test requires `VK_EXT_multi_draw`; selected draw-ID, tessellation, geometry, multiview, and dynamic-rendering paths require the corresponding extension or feature support.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Vulkan multi-draw semantics | [multi-draw commands](../../../../vulkan-docs/src/chapters/drawing.adoc#L1283-L1425) | Defines ordered execution, stride, count, instances, indexed records, and offset override behavior. |
| Parameter model and record packer | [types and `DrawInfoPacker`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L60-L369) | Defines the selected dimensions and legal packed data layout. |
| Feature checks and generated shaders | [`checkSupport` and `initPrograms`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L423-L604) | Defines capability gates and attachment color encoding. |
| Command call sites | [`drawCommands`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L798-L821) | Calls the two extension commands with the selected records and offset pointer. |
| Runtime and validation | [`iterate`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L823-L1392) | Creates resources, records work, copies attachments, and constructs exact references. |
| Registered matrix | [`createDrawMultiExtTests`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1396-L1637) | Defines hierarchy values and pruning rules. |
| Parent placement | [`createChildren` and `createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L190) | Adds the family to render-pass and applicable dynamic-rendering paths. |
| Default-profile examples | [dynamic-rendering](../../../mustpass/main/vk-default/draw.txt#L1130-L1142) and [render-pass](../../../mustpass/main/vk-default/draw.txt#L28660-L28672) | Confirms default Vulkan mustpass entries. |

## Questions / Risk Points for User Audit

- Does the distinction between color identity and stencil work count make the two mesh layouts clear?
- Does the brief explain the indexed common-offset override without suggesting that `random` record offsets affect those cases?
- Does the explanation of zero stride make clear that it is legal and intentionally changes the expected reference?
- Should the final page remain a generated-shader summary rather than include a shader-analyzer walkthrough, given that the shader only carries the tested identity values?

## Conversion Notes for Final Wiki Rewrite

- Keep `mosaic` and `overlapping` as the primary behavior parameters and copy the failure-cause mapping table unchanged.
- Retain the packed-record, indexed-offset, and zero-stride explanations because they define the command behavior under test.
- Keep the final page's shader analysis as a source-grounded generated-shader summary. Do not add a reconstructed shader walkthrough without shader-analyzer and shader-disassembler output.
- Preserve the separate color and stencil reference checks and the exact zero-threshold comparison rule.
