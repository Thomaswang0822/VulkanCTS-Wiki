# vktMultiViewRenderTests.cpp

## Overview

[`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1) is the only implementation file in the inspected `multiview` category that directly registers test groups and concrete test cases. It generates the legacy `multiview` subtree plus the non-legacy `renderpass2` and `dynamic_rendering` variants, and it also implements the support checks, shader generation, command-buffer setup, reference-image generation, query verification, and depth/stencil verification used by those tests at [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270), [`MultiViewRenderTestsCase::checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4577-L4689), and [`MultiViewRenderTestsCase::initPrograms()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4691-L4929).

The inspected Vulkan API test plan contributes only generic framework context for `TestCase` and `TestInstance` separation at [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L20-L54). Multiview-specific structure and semantics are therefore derived from the inspected source.

## Role

Implementation-heavy test file with subgroup and case registration.

## Source Code

- Primary source: [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1)
- Category dispatcher that calls this file: [`vktMultiViewTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewTests.cpp#L34-L37)
- Declared factory: [`vktMultiViewRenderTests.hpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.hpp#L34)
- Shared render helpers: [`vktMultiViewRenderUtil.hpp`](../../../modules/vulkan/multiview/vktMultiViewRenderUtil.hpp#L36-L78) and [`vktMultiViewRenderUtil.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderUtil.cpp#L53-L155)
- Shared render-pass wrappers: [`vktMultiViewRenderPassUtil.hpp`](../../../modules/vulkan/multiview/vktMultiViewRenderPassUtil.hpp#L33-L128) and [`vktMultiViewRenderPassUtil.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderPassUtil.cpp#L35-L230)
- Build inventory: [`CMakeLists.txt`](../../../modules/vulkan/multiview/CMakeLists.txt#L6-L15)

## Registration Hierarchy

```text
multiview.renderpass2
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
└── index
```

[`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270) builds the same direct-child layout for both non-legacy wrapper roots, `renderpass2` and `dynamic_rendering`, except that `dynamic_rendering` omits `input_attachments` because the file explicitly skips that family when `subpassLoad` would be required at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5128-L5130). This page uses `multiview.renderpass2` as the representative Level-3 root because the file itself creates that registered subgroup explicitly at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5088-L5093).

## Test Families

### masks — View-mask combinations rendered through common color comparison

The `masks` family is created from `TEST_TYPE_VIEW_MASK` via [`testTypeNames`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5001-L5031). For non-query families, the direct child under `masks` is always `no_queries`, because the query-type filter removes the other query groups for non-query test types at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5169-L5179). Under `no_queries`, the file registers one case per generated view-mask sequence plus the special `max_multi_view_view_count` case at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5198-L5218).

### input_attachments — Subpass input reads copied into fragment output

For `TEST_TYPE_INPUT_ATTACHMENTS`, the generated fragment shader binds an input attachment and writes `subpassLoad(in_color_attachment)` directly to `out_color` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4883-L4897). Registration still follows the non-query-family pattern of a `no_queries` child plus generated mask-pattern cases at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5221). The file explicitly omits this family from `dynamic_rendering` because `subpassLoad` cannot be used there at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5128-L5130).

### input_attachments_geometry — Input attachments plus geometry-stage multiview path

`input_attachments_geometry` shares the input-attachment implementation pattern but also sets `geometryShaderNeeded()` to true at [`TestParameters::geometryShaderNeeded()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L135-L140). The file then emits a geometry shader that forwards `gl_ViewIndex`-dependent color through emitted vertices at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4855-L4881).

### instanced — View-aware instanced rendering

The `instanced` family uses a dedicated vertex shader that offsets geometry by `gl_InstanceIndex % 4` and adds both `gl_ViewIndex * 0.10f` and instance-dependent color offsets to the output color at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4694-L4715). It is dispatched to [`MultiViewInstancedTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4530-L4531).

### input_instance — View-aware per-instance vertex-rate coverage

The `input_instance` family generates geometry from `gl_VertexIndex` while still encoding `gl_ViewIndex` and instance number into the output color in the dedicated vertex shader at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4717-L4740). It is dispatched to [`MultiViewInputRateInstanceTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4533-L4534).

### draw_indirect — Indirect non-indexed multiview draws

The `draw_indirect` family is routed to [`MultiViewDrawIndirectTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4536-L4538). Its vertex shader belongs to the generic non-specialized path, which adds `gl_ViewIndex * 0.10f` to color for `TEST_TYPE_DRAW_INDIRECT` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4787-L4805).

### draw_indirect_indexed — Indirect indexed multiview draws

`draw_indirect_indexed` shares the same instance class and generic color-generation path as `draw_indirect`, again through [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4536-L4538) and the `generateColor` branch at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4787-L4805).

### draw_indexed — Indexed direct rendering baseline

`draw_indexed` is one of the general render-test families handled by [`MultiViewRenderTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4557-L4562). It uses the common render-pass construction, draw, image readback, and reference-image comparison path visible in [`MultiViewRenderTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L453-L507).

### clear_attachments — Attachment clears within multiview subpasses

`clear_attachments` is dispatched to [`MultiViewClearAttachmentsTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4540-L4541). Its vertex shader also belongs to the `generateColor` set at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4787-L4805), and the family is registered under the ordinary non-query `no_queries` subgroup structure at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5221).

### secondary_cmd_buffer — Secondary command buffer execution with fragment-stage `gl_ViewIndex`

`secondary_cmd_buffer` is dispatched to [`MultiViewSecondaryCommandBufferTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4543-L4546). In its fragment shader path, the file adds `gl_ViewIndex * 0.10f` to the output color specifically for `TEST_TYPE_SECONDARY_CMD_BUFFER` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4921-L4924).

### secondary_cmd_buffer_geometry — Secondary command buffer plus geometry shader

`secondary_cmd_buffer_geometry` also uses [`MultiViewSecondaryCommandBufferTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4543-L4546), but the parameters additionally require geometry-shader support via [`geometryShaderNeeded()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L135-L140). The geometry shader writes `gl_ViewIndex`-dependent colors while emitting a triangle strip at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4855-L4881).

### point_size — Per-view point-size differences

`point_size` is handled by [`MultiViewPointSizeTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4548-L4549). The specialized vertex shader assigns point size `4` to view 0 and point size `2` to all other views at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4742-L4761), while support checks ensure those exact sizes are inside the device range and reachable through the reported point-size granularity at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4623-L4655).

### multisample — Multisampled multiview rendering

`multisample` is dispatched to [`MultiViewMultisampleTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4551-L4552). The factory forces `VK_SAMPLE_COUNT_4_BIT` and `VK_FORMAT_R32G32B32A32_SFLOAT` for this family at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5113-L5120), and iteration uses a render pass configured for sample count 4 at [`MultiViewMultisampleTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L2721-L2783).

### multisample_resolve — Multisampled rendering plus resolve verification

`multisample_resolve` shares [`MultiViewMultisampleTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4551-L4552), but the iteration path enables a resolve attachment through `useResolveAttachment` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L2721-L2733). Verification then ignores unresolved layers before doing per-layer float-threshold comparison in [`checkImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1283-L1306).

### queries — Precise occlusion queries and timestamps

The `queries` family differs structurally from the non-query families. Its direct children are `get_query_pool_results` and `cmd_copy_query_pool_results`, because the query-type filter excludes the `no_queries` branch for query test types at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5169-L5179). Execution uses [`MultiViewQueriesTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L2987-L3071), which verifies exact occlusion counts for the precise-query family at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3034-L3036).

### non_precise_queries — Non-precise occlusion queries and timestamps

`non_precise_queries` shares the same direct-child query structure and [`MultiViewQueriesTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4554-L4555). Its verification accepts any non-zero occlusion value instead of exact equality, as shown by the alternate failure rule at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3040-L3041).

### non_precise_queries_with_availability — Non-precise queries with availability bits

`non_precise_queries_with_availability` also uses the query-specific subgroup pattern and the same query instance class at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5221) and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4554-L4555). The naming indicates an availability-enabled variant, but this page does not overstate the exact buffer layout beyond the inspected query-copy and query-readback code paths.

### readback_implicit_clear — Readback validation after implicit clears

`readback_implicit_clear` is dispatched to [`MultiViewReadbackTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4565-L4567). Its iterate path renders, reads the layered image back, and reuses the common image-checking helper at [`MultiViewReadbackTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3419-L3473).

### readback_explicit_clear — Readback validation after explicit clears

`readback_explicit_clear` shares [`MultiViewReadbackTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4565-L4567) and the same readback-plus-compare pattern at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3419-L3473).

### depth — Depth attachment multiview cases

The `depth` family is one of the special depth/stencil groups that use a fixed `64x64x4` extent and the tripled depth/stencil mask sequence when registered at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5184-L5195). Execution uses [`MultiViewDepthStencilTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3831-L3886).

### depth_without_fragment_shader — Depth-only path without a color-format attachment

For `depth_without_fragment_shader`, the factory selects `VK_FORMAT_UNDEFINED` instead of a color format at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5121-L5125). The family still registers through the depth/stencil-specific branch at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5184-L5195) and runs through [`MultiViewDepthStencilTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4569-L4572).

### depth_different_ranges — Varying depth ranges across subpasses

`depth_different_ranges` shares the depth/stencil registration path and implementation class, but it additionally requires `VK_EXT_depth_range_unrestricted` at [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4594-L4595). The implementation can also fail immediately if the extension is unavailable during depth-range setup at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4158-L4160).

### stencil — Stencil attachment multiview cases

`stencil` is the stencil-only branch in the same depth/stencil registration cluster at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5184-L5195). It also executes through [`MultiViewDepthStencilTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4569-L4572).

### view_mask_iteration — Iterating visible layers and layout variants

`view_mask_iteration` is the only family that does not use query-type child groups. Instead, it registers direct cases named from the selected view-mask sequence and duplicates each one with an optional `_general_layout` suffix at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5132-L5154). Its shaders are also special: the vertex shader is emitted twice for SPIR-V 1.0 and SPIR-V 1.5 builds at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4763-L4783), while the fragment shader writes the layer index into a `uvec4` color at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4898-L4911).

### nested_cmd_buffer — Nested command buffer extension path

`nested_cmd_buffer` shares [`MultiViewSecondaryCommandBufferTestInstance`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4543-L4546), but support checking is stricter than for the ordinary secondary-command-buffer families. It requires `VK_EXT_nested_command_buffer`, and in Vulkan builds it also requires `nestedCommandBuffer` and `nestedCommandBufferRendering`; Vulkan SC rejects it unconditionally at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4598-L4599) and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4666-L4677).

### index — Shader-stage split for `gl_ViewIndex` coverage

The direct child `index` is created explicitly by name at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5103-L5104). Its own direct children are the stage-specific names `vertex_shader`, `fragment_shader`, `geometry_shader`, and `tessellation_shader`, because the registration switch routes those four families into `groupViewIndex` instead of the outer render-path root at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5254-L5258). Their shaders prove the intended stage coverage: the generic vertex path injects `gl_ViewIndex` for `vertex_shader` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4787-L4805), the fragment path injects it for `fragment_shader` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4921-L4924), the geometry shader injects it for `geometry_shader` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4855-L4881), and the tessellation-evaluation shader injects it for `tessellation_shader` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4808-L4852).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Test type | `TEST_TYPE_VIEW_MASK` through `TEST_TYPE_NESTED_CMD_BUFFER` in [`TestType`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L70-L102) |
| Rendering type | `RENDERING_TYPE_RENDERPASS_LEGACY`, `RENDERING_TYPE_RENDERPASS2`, and `RENDERING_TYPE_DYNAMIC_RENDERING` in [`RenderingType`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L110-L115) |
| Query mode | `QUERY_TYPE_NONE`, `QUERY_TYPE_GET_QUERY_POOL_RESULTS`, and `QUERY_TYPE_CMD_COPY_QUERY_POOL_RESULTS` in [`QueryType`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L117-L122) and [`queryTypeCases[]`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5167) |
| Base extents | Seven `VkExtent3D` values in [`extent3D[]`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5032-L5036) |
| Common mask patterns | `15`, `8`, `1_2_4_8`, `15_15_15_15`, `8_1_1_8`, `5_10_5_10`, and the one-bit sweep generated from `1` to `(1 << 6) - 1` in [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5037-L5067) |
| Depth/stencil mask base set | `3`, `6`, `12`, and `9` in [`depthStencilMasks`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5069-L5074), expanded by [`tripleDepthStencilMasks()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4984-L4997) |
| Sample count | `VK_SAMPLE_COUNT_4_BIT` for multisample families and `VK_SAMPLE_COUNT_1_BIT` otherwise at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5113-L5116) |
| Color format | `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R8G8B8A8_UINT`, `VK_FORMAT_UNDEFINED`, and `VK_FORMAT_R8G8B8A8_UNORM` selected by family at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5117-L5126) |
| Point sizes | `TEST_POINT_SIZE_SMALL = 2` and `TEST_POINT_SIZE_WIDE = 4` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L148-L149) |
| Max-view-count auto-fill | `fillMissingParameters()` replaces empty masks with `maxMultiviewViewCount` one-bit masks and sets `extent.depth` to that property at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L745-L773) |
| Layout variant | `view_mask_iteration` adds an optional `_general_layout` suffix through `useGeneralLayout` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5136-L5151) |

## Support / Feature Requirements

- All cases require `VK_KHR_multiview` at [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4592-L4593).
- Geometry-dependent families require core geometry-shader support and `multiviewGeometryShader` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4579-L4584).
- `renderpass2` requires `VK_KHR_create_renderpass2`, and `dynamic_rendering` requires `VK_KHR_dynamic_rendering`, at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4586-L4590).
- `tessellation_shader` requires `multiviewTessellationShader` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4600-L4604).
- The file queries `VkPhysicalDeviceMultiviewProperties::maxMultiviewViewCount` and requires at least six views on Vulkan or enough views for the test mask count on Vulkan SC at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4609-L4621).
- `point_size` requires `largePoints` and exact support for point sizes 2 and 4 within the reported range/granularity at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4623-L4655).
- Query families require queue timestamp support, and the precise `queries` family additionally requires `DEVICE_CORE_FEATURE_OCCLUSION_QUERY_PRECISE` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4596-L4597) and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4656-L4660).
- `depth_different_ranges` requires `VK_EXT_depth_range_unrestricted` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4594-L4595).
- `nested_cmd_buffer` requires `VK_EXT_nested_command_buffer`, and non-VulkanSC builds also require `nestedCommandBuffer` plus `nestedCommandBufferRendering` at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4662-L4677).
- [`initDeviceCapabilities()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4941-L4965) mirrors these dependencies for capability tracking, including `multiview`, `multiviewGeometryShader`, `multiviewTessellationShader`, `geometryShader`, `tessellationShader`, `multiDrawIndirect`, `occlusionQueryPrecise`, dynamic-rendering features, nested-command-buffer features, and `largePoints`.

## Verification Methods

- The general render path verifies layered images by copying them to a host-visible buffer in [`readImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1232-L1274) and comparing against generated reference layers in [`checkImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1276-L1331).
- Most color-image comparisons use [`tcu::floatThresholdCompare()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1301-L1302) or [`tcu::floatThresholdCompare()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1310-L1312) with `tcu::Vec4(0.01f)`, followed by per-layer logging on failure at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1315-L1327).
- `queries`, `non_precise_queries`, and `non_precise_queries_with_availability` verify query behavior in [`MultiViewQueriesTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L2987-L3071), reading data via either [`cmdCopyQueryPoolResults`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3306-L3330) or direct [`getQueryPoolResults`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3340-L3348).
- `readback_implicit_clear` and `readback_explicit_clear` verify by rendering, reading the image back, and reusing `checkImage()` in [`MultiViewReadbackTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3419-L3473).
- `depth`, `depth_without_fragment_shader`, `depth_different_ranges`, and `stencil` verify through [`MultiViewDepthStencilTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3831-L3886), with per-layer reference generation tied to the current depth ranges and masks at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3660-L3676).
- `view_mask_iteration` uses a different verification model: [`MultiViewMaskIterationTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4306-L4508) writes layer indices into verification buffers and compares them with [`tcu::intThresholdCompare()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4498-L4500), failing if any layer contains an unexpected value at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4505-L4506).
- `multisample_resolve` verification excludes layers never resolved by any subpass before comparing them, at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1283-L1306).

## Test Principles Observed

- This file uses a generated registration matrix rather than hand-writing every case: test type, rendering path, query mode, extent, mask pattern, and a special max-view-count probe are combined in nested loops at [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270).
- The category treats multiview as a cross-cutting behavior that must be rechecked across ordinary rendering, input attachments, instancing, indirect draws, secondary command buffers, multisampling, query collection, readback, and depth/stencil paths, as seen from the breadth of `TEST_TYPE_*` values in [`TestType`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L70-L102).
- Shader-stage-specific `gl_ViewIndex` semantics are isolated under the `index` branch and implemented by distinct shader-generation paths for vertex, fragment, geometry, and tessellation stages at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4787-L4929) and [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5254-L5258).
- Verification is intentionally image- and query-result-driven rather than API-call-success-driven: the file compares rendered layers against computed references, checks exact or non-zero occlusion results, validates timestamp behavior, and verifies explicit layer-index encodings.

## Notes / Uncertainties

- This page uses `multiview.renderpass2` as the canonical Level-3 root because the file explicitly constructs that registered subgroup in its own factory at [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5088-L5093). The same implementation also registers a sibling `multiview.dynamic_rendering` tree with nearly the same direct children, except for the omitted `input_attachments` family.
- The canonical one-level hierarchy tree cannot simultaneously encode both `renderpass2` and `dynamic_rendering`, nor can it expand nested groups such as `index -> vertex_shader` or `queries -> get_query_pool_results`, so those relationships are described in prose instead of the parseable tree.
