# multiview

## Overview

The [`multiview`](../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37) category verifies multiview rendering behavior across ordinary color rendering, `gl_ViewIndex` use in multiple shader stages, input attachments, instancing, indirect and indexed draws, attachment clears, secondary and nested command buffers, multisampling and resolve, occlusion and timestamp queries, readback after clears, depth/stencil rendering, and view-mask iteration. The category is registered as a root child named `multiview` in the Vulkan and Vulkan SC packages at [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1375) and [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1442).

The inspected Vulkan API test plan provides only generic framework context for Vulkan CTS `TestCase` and `TestInstance` structure at [`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L20-L54). It does not provide multiview-specific coverage goals, so the category-specific statements below are derived from the inspected multiview source files.

## Registration Entry Point

The category entry point is [`createTests()`](../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37), which wraps [`multiViewRenderCreateTests()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270) in `createTestGroup()`. The direct children observed under the legacy `multiview` root are:

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
└── dynamic_rendering
```

Source: [`vktMultiViewTests.cpp`](../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37) and [`multiViewRenderCreateTests()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270).

## File Inventory

| File | Role | Registered group(s) / notes |
|---|---|---|
| [`vktMultiViewTests.cpp`](../../modules/vulkan/multiview/vktMultiViewTests.cpp#L1) | Root registration / dispatcher | Registers the category root `multiview` and delegates child population to [`multiViewRenderCreateTests()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270) |
| [`vktMultiViewTests.hpp`](../../modules/vulkan/multiview/vktMultiViewTests.hpp#L29-L35) | Category header | Declares the category factory used by root package registration |
| [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1) | Implementation-heavy registration file | Registers all concrete multiview families plus the `renderpass2` and `dynamic_rendering` wrapper subtrees |
| [`vktMultiViewRenderTests.hpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.hpp#L34) | Implementation header | Declares [`multiViewRenderCreateTests()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270) |
| [`vktMultiViewRenderUtil.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderUtil.cpp#L1) | Helper implementation | Shared render-pass, image, barrier, and descriptor helpers; no direct test registration observed in inspected lines |
| [`vktMultiViewRenderUtil.hpp`](../../modules/vulkan/multiview/vktMultiViewRenderUtil.hpp#L36-L78) | Helper header | Declares multiview render helpers used by the implementation file |
| [`vktMultiViewRenderPassUtil.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderPassUtil.cpp#L1) | Helper implementation | Wraps render-pass-structure variants for render pass 1 and 2; no direct test registration observed |
| [`vktMultiViewRenderPassUtil.hpp`](../../modules/vulkan/multiview/vktMultiViewRenderPassUtil.hpp#L33-L128) | Helper header | Declares render-pass helper structures and creators |
| [`CMakeLists.txt`](../../modules/vulkan/multiview/CMakeLists.txt#L6-L15) | Build file | Confirms the category source inventory used by the Vulkan and Vulkan SC multiview libraries |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktMultiViewTests.cpp`](../../modules/vulkan/multiview/vktMultiViewTests.cpp#L1) | [`vktMultiViewTests.md`](../testfiles/multiview/vktMultiViewTests.md) |
| [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1) | [`vktMultiViewRenderTests.md`](../testfiles/multiview/vktMultiViewRenderTests.md) |

## Subgroup Structure and Major Themes

### Core legacy-root families

Under the legacy `multiview` root, [`multiViewRenderCreateTests()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270) registers behavior-oriented families such as `masks`, `input_attachments`, `instanced`, `draw_indirect`, `secondary_cmd_buffer`, `multisample`, `queries`, `readback_implicit_clear`, `depth`, `stencil`, and `view_mask_iteration`. The user-facing family names come directly from the `TestType` to string map in [`testTypeNames`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5001-L5031).

### `index` — shader-stage split for `gl_ViewIndex`

The file creates a dedicated direct child named `index` at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5103-L5104). Stage-specific families `vertex_shader`, `fragment_shader`, `geometry_shader`, and `tessellation_shader` are routed under that group by the registration switch at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5254-L5258), rather than remaining as top-level siblings.

### `renderpass2` and `dynamic_rendering` — alternate rendering-path wrappers

The implementation loops over rendering modes and creates wrapper groups `renderpass2` and `dynamic_rendering` for non-legacy paths at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5076-L5100). Each wrapper is then populated with almost the same direct-child family set as the legacy root at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5106-L5269). One explicit exception is `input_attachments`, which is skipped for dynamic rendering because `subpassLoad` cannot be used there at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5128-L5130).

## Recurring Test Families

| Family / theme | Evidence-backed summary |
|---|---|
| View-mask rendering patterns | `masks` and many other families reuse generated view-mask sequences such as `15`, `1_2_4_8`, `5_10_5_10`, and a one-bit sweep up to the minimum supported six-view count at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5037-L5067) |
| Shader-stage `gl_ViewIndex` coverage | Dedicated stage families under `index`, plus stage-specific shader generation paths in vertex, fragment, geometry, and tessellation shaders at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4787-L4929) and [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5254-L5258) |
| Attachment and subpass interactions | `input_attachments`, `input_attachments_geometry`, `clear_attachments`, and the depth/stencil families exercise attachment read/write and subpass behavior; input attachments use `subpassLoad()` in the generated fragment shader at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4883-L4897) |
| Draw submission variants | `draw_indirect`, `draw_indirect_indexed`, `draw_indexed`, `secondary_cmd_buffer`, and `nested_cmd_buffer` cover multiple draw-command and command-buffer paths through specialized instance selection in [`createInstance()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4524-L4575) |
| Query collection variants | `queries`, `non_precise_queries`, and `non_precise_queries_with_availability` split into `get_query_pool_results` and `cmd_copy_query_pool_results` subgroups via [`queryTypeCases[]`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5167) and the query-specific filter at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5169-L5179) |
| Readback and verification families | `readback_implicit_clear`, `readback_explicit_clear`, `depth`, `stencil`, and `view_mask_iteration` all include explicit CPU-side verification logic in their instance implementations at [`MultiViewReadbackTestInstance::iterate()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3419-L3473), [`MultiViewDepthStencilTestInstance::iterate()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3831-L3886), and [`MultiViewMaskIterationTestInstance::iterate()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4306-L4508) |

## Recurring Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Rendering path | Legacy root plus `renderpass2` and `dynamic_rendering` wrappers at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5076-L5100) |
| Test family | `TEST_TYPE_*` enumeration and names in [`TestType`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L70-L102) and [`testTypeNames`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5001-L5031) |
| Query mode | `no_queries`, `get_query_pool_results`, and `cmd_copy_query_pool_results` from [`queryTypeCases[]`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5167) |
| Base image extent | Seven generated extents in [`extent3D[]`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5032-L5036) |
| View-mask sequences | Generated patterns in [`viewMasks[]`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5037-L5067), plus `max_multi_view_view_count` auto-filled from queried multiview properties by [`fillMissingParameters()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L745-L773) |
| Depth/stencil mask sequence | Base masks `3`, `6`, `12`, and `9`, then tripled by [`tripleDepthStencilMasks()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4984-L4997) for depth/stencil families at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5184-L5195) |
| Sample count | `VK_SAMPLE_COUNT_4_BIT` for `multisample` and `multisample_resolve`; `VK_SAMPLE_COUNT_1_BIT` otherwise at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5113-L5116) |
| Color format | `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_UNDEFINED`, and `VK_FORMAT_R8G8B8A8_UNORM` chosen by family at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5117-L5126) |
| Point sizes | `2` and `4` for the point-size family at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L148-L149) and [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4742-L4761) |
| Layout variant | `view_mask_iteration` adds optional `_general_layout` variants through `useGeneralLayout` at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5136-L5151) |

## Recurring Support Requirements

Observed support gates are centralized in [`MultiViewRenderTestsCase::checkSupport()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4577-L4689) and mirrored in [`initDeviceCapabilities()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4941-L4965). They include:

- `VK_KHR_multiview` for all families at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4592-L4593)
- `VK_KHR_create_renderpass2` for `renderpass2` at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4586-L4587)
- `VK_KHR_dynamic_rendering` for `dynamic_rendering` at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4589-L4590)
- Geometry shader plus `multiviewGeometryShader` for geometry-dependent families at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4579-L4584)
- `multiviewTessellationShader` for `tessellation_shader` at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4600-L4604)
- `maxMultiviewViewCount` property checks via `vkGetPhysicalDeviceProperties2` at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4609-L4621)
- `largePoints` plus point-size-range and granularity checks for `point_size` at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4623-L4655)
- Precise occlusion query support for `queries` and queue timestamp support for all query families at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4596-L4597) and [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4656-L4660)
- `VK_EXT_depth_range_unrestricted` for `depth_different_ranges` at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4594-L4595)
- `VK_EXT_nested_command_buffer` plus nested command buffer features for `nested_cmd_buffer`, with Vulkan SC rejecting the family outright at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4666-L4677)

## Recurring Verification Methods

The multiview category relies primarily on CPU-side validation of rendered layered images and collected query results.

- The common render path copies images to a host-visible buffer and compares them against generated references in [`readImage()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1232-L1274) and [`checkImage()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1276-L1331).
- Most image comparisons use [`tcu::floatThresholdCompare()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1301-L1302) and [`tcu::floatThresholdCompare()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1310-L1312) with a `0.01` threshold, and log each layer separately if the aggregate check fails at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1315-L1327).
- Query families validate occlusion and timestamp results in [`MultiViewQueriesTestInstance::iterate()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L2987-L3071), reading query values either via [`cmdCopyQueryPoolResults`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3306-L3330) or direct [`getQueryPoolResults`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3340-L3348).
- Readback-clear families reuse the common image comparison path in [`MultiViewReadbackTestInstance::iterate()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3419-L3473).
- Depth/stencil families run through [`MultiViewDepthStencilTestInstance::iterate()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3831-L3886), with layer-aware expected-image generation visible in the surrounding depth/stencil helpers at [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3660-L3676).
- `view_mask_iteration` uses a different mechanism: it writes the observed layer index into verification buffers and checks those buffers with [`tcu::intThresholdCompare()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4498-L4500), failing on any invalid layer value at [`MultiViewMaskIterationTestInstance::iterate()`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4306-L4508).

## Notes and Scope

- Only two inspected source files in this category register tests directly: [`vktMultiViewTests.cpp`](../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37) and [`vktMultiViewRenderTests.cpp`](../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270). The utility files provide shared helpers but no direct registration evidence was observed in the inspected lines.
- The non-legacy wrapper groups `renderpass2` and `dynamic_rendering` replicate most of the legacy family structure. This page documents them as category-level structure, while the Level-3 file pages capture the representative one-level hierarchy required by the validator.
- The inspected [`apitests.adoc`](../../../../doc/testspecs/VK/apitests.adoc#L1-L13) contains no multiview-specific objectives, so all category semantics are source-derived and limited to what is visible in the inspected multiview files.
