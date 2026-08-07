## Overview

**Core question:** Do `vkCmdDrawMultiEXT` and `vkCmdDrawMultiIndexedEXT` execute every packed draw correctly across draw counts, strides, indexed offsets, shader stages, views, and command-buffer modes?

- [`vktDrawMultiExtTests.cpp`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L60-L1637) implements the `multi_draw` test family for `VK_EXT_multi_draw`.
- Each case submits an ordered sequence through either the non-indexed or indexed multi-draw command, then compares color and stencil readback against a CPU-generated image.
- Mosaic geometry makes each triangle address a separate pixel. Overlapping geometry uses depth testing so the surviving triangle exposes ordering and repeated-draw behavior.
- The page describes the registered matrix, the generated shaders, the render and readback path, and what a mismatch isolates.

## Background Knowledge

- `vkCmdDrawMultiEXT` records `drawCount` ordinary draw operations from `VkMultiDrawInfoEXT` records. Each record supplies `firstVertex` and `vertexCount`; `stride` gives the byte distance to the next record.
- `vkCmdDrawMultiIndexedEXT` does the indexed equivalent with `VkMultiDrawIndexedInfoEXT`. A non-null `pVertexOffset` overrides each record's `vertexOffset`; a null pointer makes each record's member effective.
- A depth test can make many overlapping primitives produce one visible result, while stencil operations can count fragments that pass the configured stencil test. The test uses both observations because final color alone cannot prove that all intended operations occurred.

## Registration Hierarchy

The parent draw registration adds this family for legacy render passes and for three dynamic-rendering command-buffer arrangements. Secondary-command-buffer variants register a reduced matrix. The family is Vulkan-only: [`CTS_USES_VULKANSC` excludes its declaration](../../../modules/vulkan/draw/vktDrawTests.cpp#L51-L57) and [its registration](../../../modules/vulkan/draw/vktDrawTests.cpp#L103-L120).

```text
draw.renderpass.multi_draw
├── mosaic
└── overlapping

draw.dynamic_rendering.primary_cmd_buff.multi_draw
├── mosaic
└── overlapping

draw.dynamic_rendering.partial_secondary_cmd_buff.multi_draw
└── mosaic

draw.dynamic_rendering.complete_secondary_cmd_buff.multi_draw
└── mosaic
```

The parent does not add the family beneath either nested-secondary-command-buffer group. `createChildren()` omits it when `nestedSecondaryCmdBuffer` is set.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Mesh layout | `mosaic`, `overlapping` | Separates per-pixel draw placement from depth-selected full-screen overlap. | [mesh registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1402-L1409) |
| Command form | `normal`; `indexed_mixed`, `indexed_random`, `indexed_packed` | Chooses `vkCmdDrawMultiEXT` or `vkCmdDrawMultiIndexedEXT`, and exercises record-supplied, common-pointer, and packed indexed offsets. | [draw and offset registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1411-L1429) |
| Draw count | `no_draws`, `one_draw`, `16_draws`, `max_draws` | Checks zero, one, several, and 1024 draw records. `1024` is the minimum permitted `maxMultiDrawCount`. | [count registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1431-L1440) |
| Record stride | `stride_zero`, `standard_stride`, `stride_extra_4`, `stride_extra_12` | Checks zero stride where no record advancement is needed, the base record layout, and valid padding between records. | [stride registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1442-L1451) |
| Instance range | `no_instances`, `1_instance`, `10_instances`, `2_instances_base_3` | Exercises zero instances, multiple instances, and a nonzero `firstInstance`. | [instance registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1453-L1463) |
| Shader-stage path | `vert_only`, `with_geom`, `with_tess`, `tess_geom` | Carries the generated integer value through optional geometry and tessellation stages. | [shader registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1465-L1475) |
| View and draw ID | `single_view`, `multiview`; `no_offset`, `no_offset_no_draw_id`, and indexed `offset_6`, `offset_6_no_draw_id` | Makes output depend on `gl_ViewIndex` when applicable and on `gl_DrawID` or a primitive-derived fallback. | [view and draw-ID registration](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1477-L1493) |

The source removes invalid or unhelpful combinations while it builds the hierarchy. Normal draws have no indexed-offset form; indexed draws always have one. Multi-record cases must use a four-byte-aligned stride at least as large as the applicable record. Overlapping cases omit instance counts above one.

## Behavior Parameters

The primary behavior axis is the mesh layout. It changes how the test makes the effects of the submitted sequence observable. Command form, count, stride, instances, shader stages, views, and offsets then stress that observation under different registered configurations.

### `mosaic`: independently placed triangles

The generator places one small triangle around each pixel center in a 32 by 32 target. A correct sequence distributes triangles according to the packed records, so the reference can identify which draw or primitive produced every pixel.

### `overlapping`: depth-selected full-screen triangles

The generator gives 1024 full-screen triangles decreasing depths. Depth testing retains the expected frontmost result, while stencil records the number of relevant fragments. This layout exposes ordering, depth, and draw-count effects without requiring a different output geometry for each triangle.

## Shader Analysis

`MultiDrawTest::initPrograms` generates GLSL instead of loading fixed shader files. The vertex shader copies the input position and writes an unsigned four-component value at location 0. Its red and green components encode either `gl_DrawID` or `gl_VertexIndex / 3`; blue encodes `255 - gl_InstanceIndex`; alpha encodes `255 - gl_ViewIndex` for multiview and `255` otherwise. The fragment shader flatly copies that value to the unsigned color attachment.

Optional tessellation and geometry shaders preserve the same position and integer color interface. Their purpose is to test that the multi-draw-dependent value survives the selected graphics-stage path, not to add a separate shader correctness property. The generated source is available in [initPrograms](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L454-L604).

## Runtime Execution and Result Checking

- The case requires `VK_EXT_multi_draw`; draw-ID cases also require `VK_KHR_shader_draw_parameters`. Tessellation, geometry, multiview, and dynamic-rendering cases check their corresponding feature or extension requirements before execution.
- `iterate()` creates a 32 by 32 `VK_FORMAT_R8G8B8A8_UINT` color image and a supported depth/stencil image. Multiview uses two array layers. It also creates host-visible transfer-destination buffers for each color and stencil layer.
- The host generates 1024 triangles, uploads a vertex buffer, and creates reversed indices for indexed cases. `DrawInfoPacker` serializes the applicable multi-draw records, including padded storage and the extra trailing bytes needed to keep packed indexed records legal.
- The test records either `vkCmdDrawMultiEXT` or `vkCmdDrawMultiIndexedEXT`. It supports a legacy render pass, dynamic rendering in a primary command buffer, and the registered dynamic-rendering secondary-command-buffer modes.
- After rendering, the command buffer transitions the color and depth/stencil images, copies the color and stencil aspects to host-visible buffers, and makes transfer writes available to the host.
- The CPU builds a reference for every pixel and view layer. It derives the encoded draw or primitive value, highest used instance index, view layer, and expected stencil increment count from the case parameters. Exact color and stencil comparisons decide the result.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `mosaic` | Incorrect multi-draw record selection, stride advancement, indexed vertex-offset handling, draw-ID propagation, or per-pixel reference/readback handling. |
| `overlapping` | Incorrect ordered multi-draw execution, depth or stencil interaction, record selection, or the shared reference/readback handling. |

### Cause Analysis

#### Multi-draw record interpretation and draw identity

**Possible failure symptoms:** Mosaic color differs from the exact reference at one or more pixels, often in the encoded red and green draw or primitive components. Indexed offset cases, stride variants, or draw-ID variants can fail independently.

**Possible implementation causes:** The command implementation may read the wrong record, advance by the wrong byte stride, apply an indexed offset from the wrong source, or provide an incorrect draw ID. The command definitions require sequential record interpretation and specify the `pVertexOffset` override rule for indexed draws in [Multi-draw commands](../../../../vulkan-docs/src/chapters/drawing.adoc#L1283-L1393).

#### Ordered depth and stencil behavior

**Possible failure symptoms:** An overlapping case has the wrong uniform color, the wrong stencil value, or both. A mismatch can vary with draw count because that parameter changes how the 1024 triangles are divided among records.

**Possible implementation causes:** The implementation may execute the sequence out of order, use incorrect depth comparison or depth writes for the selected geometry, or apply stencil increment-and-wrap incorrectly. The source-level reference combines these effects, so inspection of the failing attachment and parameter path is needed to distinguish them.

#### Shared rendering, copyback, or reference handling

**Possible failure symptoms:** Both mesh layouts fail across unrelated command forms or shader-stage paths, or a failure affects only a multiview layer despite otherwise matching color encoding.

**Possible implementation causes:** Source-level investigation is needed to distinguish pipeline setup, multiview layer selection, command-buffer recording, image transitions, attachment copies, host invalidation, or reference generation from command execution defects.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_multi_draw`; draw-ID cases require `VK_KHR_shader_draw_parameters`.
- Tessellation and geometry variants require their core features. Multiview variants require `multiview`, plus the relevant multiview tessellation or geometry feature.
- Dynamic-rendering registrations require `VK_KHR_dynamic_rendering`.
- For more than one draw, the source retains only strides that meet the commands' minimum-size and four-byte-alignment valid-usage rules.

### Design-based pruning

- Secondary-command-buffer registrations retain only `mosaic` and `one_draw`; normal commands remain, while indexed commands retain only the `random` offset representation.
- Normal commands do not register indexed offset variants; indexed commands do not register an absent offset type.
- Overlapping geometry omits instance counts greater than one because its depth-selected observation is designed for one instance.
- The two nested-secondary-command-buffer parent configurations do not add this family.

## Key Takeaways

- The family uses two independent observables: encoded integer color identifies the winning draw or primitive, and stencil verifies the expected amount of rendering work.
- `stride_zero` is registered only with zero or one draw. Because no command in those cases advances to another record, it does not exercise repeated-record execution.
- Indexed tests distinguish per-record offsets, a command-wide offset pointer, and packed storage while preserving the same color and stencil contract.
- The registered dynamic-rendering secondary modes reduce the matrix, but mustpass still includes real `multi_draw` cases for both complete-secondary and render-pass paths.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test parameters and draw-info packing | [parameter types and `DrawInfoPacker`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L60-L369) | Defines command form, offset modes, record packing, and packed-indexed safety padding. |
| Support checks and generated shaders | [`checkSupport` and `initPrograms`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L423-L604) | Defines feature gates and the color encoding carried through the graphics stages. |
| Command recording | [`drawCommands`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L798-L821) | Calls the two extension commands and selects indexed offset-pointer behavior. |
| Resource setup, rendering, and comparison | [`MultiDrawInstance::iterate`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L823-L1392) | Creates resources, records rendering, copies attachments, and compares exact CPU references. |
| Matrix registration | [`createDrawMultiExtTests`](../../../modules/vulkan/draw/vktDrawMultiExtTests.cpp#L1396-L1637) | Registers the mesh, command, count, stride, instance, shader, view, and draw-ID hierarchy. |
| Parent draw registration | [`createChildren` and `createTests`](../../../modules/vulkan/draw/vktDrawTests.cpp#L70-L190) | Places the family in legacy and applicable dynamic-rendering branches. |
| Default Vulkan mustpass | [dynamic-rendering examples](../../../mustpass/main/vk-default/draw.txt#L1130-L1142) and [render-pass examples](../../../mustpass/main/vk-default/draw.txt#L28660-L28672) | Confirms registered default-profile entries in both execution paths. |
| Vulkan command semantics | [multi-draw commands](../../../../vulkan-docs/src/chapters/drawing.adoc#L1283-L1425) | Defines ordered records, stride, instance behavior, indexed offsets, and valid usage. |
