## Overview

The `multiview` test category checks whether Vulkan renders the views selected by a render-pass view mask and preserves that behavior across draw, attachment, query, depth/stencil, command-buffer, and rendering-path variants.

## Background Knowledge

- **Multiview rendering.** A nonzero view mask makes a subpass execute for each set bit, treating the selected views as parallel instances of the subpass. A layered attachment supplies storage for those views, while `gl_ViewIndex` lets shader code observe the current view. See [multiview render-pass semantics](../../../vulkan-docs/src/chapters/renderpass.adoc#L2617-L2671).
- **View-local attachment state.** Input attachments and subpass dependencies can operate per view. This distinction matters for the input-attachment and multi-subpass cases, where one view must read the corresponding view's earlier result. See [view-local dependencies](../../../vulkan-docs/src/chapters/renderpass.adoc#L2680-L2686).

## Category Structure

```text
multiview
├── clear_attachments
├── depth
├── depth_different_ranges
├── depth_without_fragment_shader
├── draw_indexed
├── draw_indirect
├── draw_indirect_indexed
├── dynamic_rendering
├── index
├── input_attachments
├── input_attachments_geometry
├── input_instance
├── instanced
├── masks
├── multisample
├── multisample_resolve
├── nested_cmd_buffer
├── non_precise_queries
├── non_precise_queries_with_availability
├── point_size
├── queries
├── readback_explicit_clear
├── readback_implicit_clear
├── renderpass2
├── secondary_cmd_buffer
├── secondary_cmd_buffer_geometry
├── stencil
└── view_mask_iteration
```

`dynamic_rendering` is present in non-VulkanSC builds. The root dispatcher [`createTests()`](../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37) only delegates to the implementation registration function; the implementation families and their behavior are documented in the Level-3 page.

## How the Families Fit Together

The category varies the way multiview work is submitted and the observable result that proves each view behaved correctly.

- `masks`, the draw families, instancing, clears, and readback families compare rendered layers against generated reference images.
- `index` isolates `gl_ViewIndex` use in vertex, fragment, geometry, and tessellation stages; attachment, depth/stencil, multisample, and query families test the surrounding render-pass contracts.
- `secondary_cmd_buffer`, `nested_cmd_buffer`, `renderpass2`, and `dynamic_rendering` reuse the same view behavior through different command-buffer or rendering APIs.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| All implementation-bearing multiview families, including the `index`, `renderpass2`, and `dynamic_rendering` areas | [RenderTests.md](../testfiles/multiview/RenderTests.md) | Behavior parameters, generated shader paths, host-side image/query checks, support gates, and failure meaning |

The old [`vktMultiViewTests.md`](../testfiles/multiview/vktMultiViewTests.md) page describes only the registration dispatcher and is folded into this gateway rather than rewritten as a separate technical page.

## Category Notes

The default Vulkan mustpass contains 694 multiview paths. The non-VulkanSC-only `dynamic_rendering` paths are part of that registration evidence; the source loop omits `input_attachments` below that rendering path because dynamic rendering has no `subpassLoad()` operation.
