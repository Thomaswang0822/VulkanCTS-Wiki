# vktMultiViewTests.cpp

## Overview

[`vktMultiViewTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewTests.cpp#L1) is the root registration file for the `multiview` category. The category is attached to both the Vulkan and Vulkan SC root packages as `multiview` in [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1374) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1441). Its only job is to wrap [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270) in [`createTestGroup()`](../../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37), so the category structure and concrete case generation are delegated to [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1).


## Role

Registration / dispatcher file.

## Source Code

- Primary source: [`vktMultiViewTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewTests.cpp#L1)
- Root header: [`vktMultiViewTests.hpp`](../../../modules/vulkan/multiview/vktMultiViewTests.hpp#L29-L35)
- Delegated implementation and subgroup registration: [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270)
- Build inventory: [`CMakeLists.txt`](../../../modules/vulkan/multiview/CMakeLists.txt#L6-L15)
- Root package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1374) and [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1441)

## Registration Hierarchy

```text
multiview
├── masks
├── input_attachments
├── input_attachments_geometry
├── instanced
├── input_instance
├── draw_indirect
├── draw_indirect_indexed
├── draw_indexed
├── clear_attachments
├── secondary_cmd_buffer
├── secondary_cmd_buffer_geometry
├── point_size
├── multisample
├── multisample_resolve
├── queries
├── non_precise_queries
├── non_precise_queries_with_availability
├── readback_implicit_clear
├── readback_explicit_clear
├── depth
├── depth_without_fragment_shader
├── depth_different_ranges
├── stencil
├── view_mask_iteration
├── nested_cmd_buffer
├── index
├── renderpass2
└── dynamic_rendering (non-VulkanSC only)
```

The root file itself registers `multiview`, and the delegated factory populates the direct children shown above in the legacy render-pass branch plus the extra `renderpass2` and, when `CTS_USES_VULKANSC` is not defined, `dynamic_rendering` wrappers for non-legacy rendering paths at [`vktMultiViewTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37), [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5076-L5100), and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5266-L5269).

## Test Families

### masks — View-mask driven multiview rendering

The `masks` group name is mapped from `TEST_TYPE_VIEW_MASK` in [`testTypeNames`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5001-L5031). In legacy rendering it is added directly under `multiview`, while in `renderpass2` and `dynamic_rendering` it is recreated inside those wrapper groups at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5082-L5269). Concrete case names come from the generated view-mask vectors and the helper [`createViewMasksName()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4970-L4982).

### input_attachments — Multiview subpass input attachment reads

`input_attachments` maps from `TEST_TYPE_INPUT_ATTACHMENTS` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5007). The factory skips this family for `dynamic_rendering` because `subpassLoad` cannot be used there, via the explicit guard at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5128-L5130).

### input_attachments_geometry — Input attachments with geometry-stage participation

`input_attachments_geometry` maps from `TEST_TYPE_INPUT_ATTACHMENTS_GEOMETRY` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5008). The file-local `geometryShaderNeeded()` helper marks this family as geometry-dependent together with `geometry_shader` and `secondary_cmd_buffer_geometry` at [`TestParameters::geometryShaderNeeded()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L135-L140).

### instanced — Instance index combined with view index

`instanced` maps from `TEST_TYPE_INSTANCED_RENDERING` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5009). Its vertex shader offsets the quad by `gl_InstanceIndex % 4` and encodes both `gl_ViewIndex` and instance number into color at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4694-L4715).

### input_instance — Per-instance vertex-input stepping with multiview

`input_instance` maps from `TEST_TYPE_INPUT_RATE_INSTANCE` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5010). The generated vertex shader uses `gl_VertexIndex` to build the quad and still writes color components derived from `gl_ViewIndex` and instance number at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4717-L4740).

### draw_indirect — Non-indexed indirect draws under multiview

`draw_indirect` is registered from `TEST_TYPE_DRAW_INDIRECT` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5011). It is implemented by the draw-indirect instance path selected in [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4536-L4538).

### draw_indirect_indexed — Indexed indirect draws under multiview

`draw_indirect_indexed` maps from `TEST_TYPE_DRAW_INDIRECT_INDEXED` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5012). It shares the same implementation class as `draw_indirect`, again through [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4536-L4538).

### draw_indexed — Indexed direct draws under multiview

`draw_indexed` maps from `TEST_TYPE_DRAW_INDEXED` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5013). This family is routed to the general render-test instance path in [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4557-L4562).

### clear_attachments — Attachment clear behavior with multiview

`clear_attachments` maps from `TEST_TYPE_CLEAR_ATTACHMENTS` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5014). It uses the dedicated clear-attachments instance path chosen in [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4540-L4541).

### secondary_cmd_buffer — Secondary command buffer execution with multiview

`secondary_cmd_buffer` maps from `TEST_TYPE_SECONDARY_CMD_BUFFER` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5015). It is dispatched to the secondary-command-buffer instance path in [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4543-L4546), and its fragment shader variant also injects `gl_ViewIndex` into output color at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4921-L4924).

### secondary_cmd_buffer_geometry — Secondary command buffers plus geometry shader

`secondary_cmd_buffer_geometry` maps from `TEST_TYPE_SECONDARY_CMD_BUFFER_GEOMETRY` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5016). It shares the secondary-command-buffer instance path with `secondary_cmd_buffer` and is also flagged by [`geometryShaderNeeded()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L135-L140).

### point_size — View-dependent point size selection

`point_size` maps from `TEST_TYPE_POINT_SIZE` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5017). Its specialized vertex shader uses `gl_ViewIndex` to choose between `TEST_POINT_SIZE_WIDE = 4` and `TEST_POINT_SIZE_SMALL = 2` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L148-L149) and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4742-L4761).

### multisample — Multiview rendering with multisampled color attachments

`multisample` maps from `TEST_TYPE_MULTISAMPLE` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5018). The factory forces `VK_SAMPLE_COUNT_4_BIT` for this family and the resolve variant at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5113-L5116).

### multisample_resolve — Multiview rendering plus resolve attachment coverage

`multisample_resolve` maps from `TEST_TYPE_MULTISAMPLE_RESOLVE` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5019). Verification for this family explicitly ignores layers not resolved by any subpass before doing per-layer float-threshold comparison at [`checkImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1283-L1306).

### queries — Precise occlusion and timestamp queries in multiview passes

`queries` maps from `TEST_TYPE_QUERIES` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5020). Unlike most families, query families receive `get_query_pool_results` and `cmd_copy_query_pool_results` direct children instead of `no_queries`, via the query-type filter at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5169-L5179).

### non_precise_queries — Non-precise occlusion and timestamp queries

`non_precise_queries` maps from `TEST_TYPE_NON_PRECISE_QUERIES` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5021). It uses the same query subgroup structure and implementation class as `queries`, but without the precise occlusion query support requirement reserved for `TEST_TYPE_QUERIES` at [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4596-L4597).

### non_precise_queries_with_availability — Non-precise queries with availability data

`non_precise_queries_with_availability` maps from `TEST_TYPE_NON_PRECISE_QUERIES_WITH_AVAILABILITY` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5022). It also shares the query-specific grouping logic and implementation path visible at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5221) and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4554-L4555).

### readback_implicit_clear — Readback after implicit clears

`readback_implicit_clear` maps from `TEST_TYPE_READBACK_WITH_IMPLICIT_CLEAR` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5023). It is routed to the dedicated readback instance path in [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4565-L4567).

### readback_explicit_clear — Readback after explicit clear commands

`readback_explicit_clear` maps from `TEST_TYPE_READBACK_WITH_EXPLICIT_CLEAR` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5024). It shares the same readback instance path as `readback_implicit_clear` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4565-L4567).

### depth — Multiview depth attachment behavior

`depth` maps from `TEST_TYPE_DEPTH` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5025). Depth and stencil families use a dedicated depth/stencil test extent and a tripled mask sequence from [`tripleDepthStencilMasks()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4984-L4997) when the subgroup is populated at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5184-L5195).

### depth_without_fragment_shader — Depth-only multiview without fragment stage

`depth_without_fragment_shader` maps from `TEST_TYPE_DEPTH_WITHOUT_FRAGMENT_SHADER` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5026). The factory assigns `VK_FORMAT_UNDEFINED` as the color format for this family at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5121-L5125), which distinguishes it from the other depth variants.

### depth_different_ranges — Per-subpass depth range variation

`depth_different_ranges` maps from `TEST_TYPE_DEPTH_DIFFERENT_RANGES` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5027). It is the only family that additionally requires `VK_EXT_depth_range_unrestricted` in [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4594-L4595).

### stencil — Multiview stencil attachment behavior

`stencil` maps from `TEST_TYPE_STENCIL` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5028). Like the depth families, it uses the dedicated 64×64×4 extent and the tripled depth/stencil mask generator at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5184-L5195).

### view_mask_iteration — View-mask iteration and layout variants

`view_mask_iteration` maps from `TEST_TYPE_VIEW_MASK_ITERATION` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5029). Instead of query-type subgroups, this family directly registers mask-pattern case names and duplicates each one with and without the `_general_layout` suffix at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5132-L5154).

### nested_cmd_buffer — Nested command buffer extension coverage

`nested_cmd_buffer` maps from `TEST_TYPE_NESTED_CMD_BUFFER` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5030). It shares the secondary-command-buffer instance path in [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4543-L4546) and requires `VK_EXT_nested_command_buffer` plus nested-command-buffer features in non-VulkanSC builds at [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4598-L4599) and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4666-L4676).

### index — `gl_ViewIndex` coverage split by shader stage

The `index` group is created explicitly as a direct child under each rendering-path root at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5103-L5104). It contains the four stage-specific families `vertex_shader`, `fragment_shader`, `geometry_shader`, and `tessellation_shader`, because the switch at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5254-L5258) routes those names into `groupViewIndex` instead of the main root.

### renderpass2 — Alternate root for `VK_KHR_create_renderpass2`

The `renderpass2` wrapper is created only when the rendering-type loop selects `RENDERING_TYPE_RENDERPASS2` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5088-L5093). Inside this wrapper, the file recreates the same child-family structure used by the legacy root, except for any family-specific skips such as dynamic-rendering-only restrictions.

### dynamic_rendering — Alternate root for dynamic rendering multiview

The `dynamic_rendering` wrapper is created only in non-VulkanSC builds and only when the rendering-type loop selects `RENDERING_TYPE_DYNAMIC_RENDERING` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5076-L5100). The code then repopulates the multiview families under this wrapper, but omits `input_attachments` because the fragment shader uses `subpassLoad`, which the factory explicitly excludes for dynamic rendering at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5128-L5130).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Rendering path | Legacy root and `renderpass2`; `dynamic_rendering` is added only in non-VulkanSC builds by the rendering-type loop at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5076-L5100) |
| Test family selection | `TEST_TYPE_*` enumeration and user-facing names in [`TestType`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L70-L102) and [`testTypeNames`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5001-L5031) |
| Base extents | `{16,16,4}`, `{64,64,8}`, `{128,128,4}`, `{32,32,5}`, `{64,64,6}`, `{32,32,4}`, and `{16,16,10}` from [`extent3D[]`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5032-L5036) |
| View-mask sequences | Generated from `viewMasks[]`, including single-subpass `15`, per-subpass `1/2/4/8`, repeated `15`, alternating `8/1/1/8`, alternating `5/10/5/10`, and the shifting one-bit loop used for the last pattern at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5037-L5067) |
| Depth/stencil masks | Base masks `3`, `6`, `12`, `9` from [`depthStencilMasks`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5069-L5074), tripled by [`tripleDepthStencilMasks()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4984-L4997) |
| Query mode | `no_queries`, `get_query_pool_results`, and `cmd_copy_query_pool_results` from [`queryTypeCases[]`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5167) |
| Sample count | `VK_SAMPLE_COUNT_4_BIT` for `multisample` / `multisample_resolve`, otherwise `VK_SAMPLE_COUNT_1_BIT`, from [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5113-L5116) |
| Color format | `VK_FORMAT_R32G32B32A32_SFLOAT` for multisample families, `VK_FORMAT_R8G8B8A8_UINT` for `view_mask_iteration`, `VK_FORMAT_UNDEFINED` for `depth_without_fragment_shader`, otherwise `VK_FORMAT_R8G8B8A8_UNORM` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5117-L5126) |
| Max-view-count probe | The special `max_multi_view_view_count` case uses `{16,16,0}` extent and an empty mask vector so support code fills it from queried device properties at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5209-L5218) and [`fillMissingParameters()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L745-L773) |
| General-layout variant | `view_mask_iteration` duplicates each pattern with and without `_general_layout` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5134-L5151) |

## Support / Feature Requirements

- All multiview tests require `VK_KHR_multiview`, while `renderpass2` and `dynamic_rendering` variants additionally require `VK_KHR_create_renderpass2` and `VK_KHR_dynamic_rendering` respectively in [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4586-L4593).
- Geometry-dependent families require core geometry-shader support and `multiviewGeometryShader`, as enforced by [`geometryShaderNeeded()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L135-L140) and [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4579-L4584).
- `tessellation_shader` requires `multiviewTessellationShader` in [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4600-L4604).
- The file checks `VkPhysicalDeviceMultiviewProperties::maxMultiviewViewCount` through `vkGetPhysicalDeviceProperties2`, requiring at least six views on Vulkan and enough views for the generated mask count on Vulkan SC at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4609-L4621).
- `point_size` requires core `largePoints` plus point-size range and granularity compatibility for sizes `2` and `4` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4623-L4655).
- Query families require queue-family timestamp support, and `queries` additionally requires precise occlusion-query support at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4596-L4597) and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4656-L4660).
- `depth_different_ranges` requires `VK_EXT_depth_range_unrestricted` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4594-L4595).
- `nested_cmd_buffer` requires `VK_EXT_nested_command_buffer`; in Vulkan builds it also requires `nestedCommandBuffer` and `nestedCommandBufferRendering`, while Vulkan SC rejects the family outright at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4662-L4677).
- `initDeviceCapabilities()` advertises the same extension and feature dependencies for capability caching, including `multiview`, `multiviewGeometryShader`, `multiviewTessellationShader`, `geometryShader`, `tessellationShader`, `multiDrawIndirect`, `occlusionQueryPrecise`, dynamic rendering features, nested-command-buffer features, and `largePoints` for point-size cases at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4941-L4965).

## Verification Methods

- The common render-test path copies the rendered layered image to a host-visible buffer, then compares it against a generated `Texture2DArray` reference in [`readImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1232-L1274) and [`checkImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1276-L1331).
- Most image checks use [`tcu::floatThresholdCompare()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1301-L1302) and [`tcu::floatThresholdCompare()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1310-L1312) with a `0.01` threshold, and log per-layer mismatches when the full comparison fails at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1315-L1327).
- `multisample_resolve` verification differs by ignoring layers that no subpass resolved before running per-layer threshold comparison at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1283-L1306).
- Query families verify both occlusion and timestamp behavior in [`MultiViewQueriesTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L2987-L3071), failing on exact occlusion mismatches for precise queries, zero occlusion results for non-precise queries, or invalid timestamp ordering; results are read either via [`cmdCopyQueryPoolResults`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3306-L3330) or direct [`getQueryPoolResults`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3340-L3348).
- Readback-clear families run through [`MultiViewReadbackTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3419-L3473), which builds the render path, reads the image back, and reuses the common `checkImage()` comparison.
- Depth and stencil families run through [`MultiViewDepthStencilTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3831-L3886) and layer-aware image generation in [`checkImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3660-L3676); `depth_different_ranges` can additionally fail early if `VK_EXT_depth_range_unrestricted` is unavailable at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4158-L4160).
- `view_mask_iteration` uses a different verification strategy: it builds explicit layer verification images and compares them with [`tcu::intThresholdCompare()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4498-L4500), failing with a dedicated error when any verification buffer contains an unexpected layer index at [`MultiViewMaskIterationTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4306-L4508).

## Test Principles Observed

- The root file intentionally separates category registration from implementation: [`createTests()`](../../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37) only names the category, while all family generation is delegated to [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270).
- The category organization is primarily semantic by rendering behavior (`masks`, `input_attachments`, `queries`, `depth`, `view_mask_iteration`, and so on), with a second orthogonal split by rendering API path through the legacy root, `renderpass2`, and `dynamic_rendering` wrappers at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5082-L5100).
- A special `index` branch isolates `gl_ViewIndex` usage by shader stage instead of mixing those cases into the other top-level families, as shown by the stage-specific routing in [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5254-L5258).
- The registration file does not implement verification itself; all support checks, shader generation, and pass/fail logic live in the delegated implementation file.

## Notes / Uncertainties

- The one-level `## Registration Hierarchy` tree is intentionally limited to direct children of `multiview`, so nested direct children such as `index -> vertex_shader` and `queries -> get_query_pool_results` are described in prose instead of the parseable tree.
- Multiview semantics here are based solely on inspected source files under [`external/vulkancts/modules/vulkan/multiview/`](../../../modules/vulkan/multiview/).
