## Overview

**Core question:** Does multiview rendering select and update the expected image layers across render-pass, shader-stage, resource, and query variants?

- [`vktMultiViewRenderTests.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L70-L115) defines the implementation and the `TestType`, `RenderingType`, and `QueryType` dimensions for this Level-3 page.
- [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270) registers the legacy `multiview` tree, `renderpass2`, and, outside Vulkan SC, `dynamic_rendering`. The same implementation file owns all three rendering paths.
- The families exercise view masks, `gl_ViewIndex` in several shader stages, input attachments, instancing, indirect and indexed draws, clears, secondary and nested command buffers, point size, multisampling, queries, readback, depth, and stencil.
- The test submits graphics work, copies layered results to host-visible memory, and compares each layer with a generated reference. Query families use query results instead of the common color-image check.

## Background Knowledge

- A Vulkan multiview render pass uses a view mask as a bitfield. Bit *i* enables view index *i*, and the enabled views address layers of a 2D array image. The same concept is supplied as `VkRenderingInfo::viewMask` for dynamic rendering. See [multiview render passes](../../../../vulkan-docs/src/chapters/renderpass.adoc#renderpass-multiview).
- `gl_ViewIndex` identifies the view selected for the current shader invocation. It is distinct from `gl_InstanceIndex` and can be consumed in the vertex, geometry, tessellation-evaluation, or fragment stage. The [Vulkan shader built-ins](../../../../vulkan-docs/src/chapters/shaders.adoc) and the multiview rules in [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#renderpass-multiview) define its scope.
- An input attachment is read through a subpass-aware `subpassInput`. That relationship depends on render-pass subpass semantics, so the `input_attachments` family has no dynamic-rendering registration. See [input attachments](../../../../vulkan-docs/src/chapters/renderpass.adoc#renderpass-input-attachments).

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
└── dynamic_rendering
```

The 28 direct children above exactly match the default Vulkan mustpass namespace. `renderpass2` and the non-VulkanSC `dynamic_rendering` child are wrapper roots that repeat the applicable implementation families below their own paths; `dynamic_rendering` omits `input_attachments`. Under `index`, the implementation registers `vertex_shader`, `fragment_shader`, `geometry_shader`, and `tessellation_shader`. Query families add `get_query_pool_results` and `cmd_copy_query_pool_results`; non-query families add `no_queries`. Those deeper paths are listed in the parameter and family sections rather than nested in the parseable tree.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Rendering type | legacy `multiview`, `renderpass2`, and non-VulkanSC `dynamic_rendering` | Selects the API used to create and execute the multiview rendering operation. | [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5076-L5100) |
| Test family | `masks`, `input_attachments`, `input_attachments_geometry`, `instanced`, `input_instance`, `draw_indirect`, `draw_indirect_indexed`, `draw_indexed`, `clear_attachments`, `secondary_cmd_buffer`, `secondary_cmd_buffer_geometry`, `point_size`, `multisample`, `multisample_resolve`, `queries`, `non_precise_queries`, `non_precise_queries_with_availability`, `readback_implicit_clear`, `readback_explicit_clear`, `depth`, `depth_without_fragment_shader`, `depth_different_ranges`, `stencil`, `view_mask_iteration`, `nested_cmd_buffer`, and `index` | Chooses the multiview behavior under test and, through `TestType`, selects the instance and shader path. | [`TestType`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L70-L102), [`createInstance()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4524-L4574) |
| View-mask sequence | `15`, `8`, `1_2_4_8`, `15_15_15_15`, `8_1_1_8`, `5_10_5_10`, and `1_2_4_8_16_32` | Changes which array layers each subpass or rendering instance writes. | [`extent3D[]` and `viewMasks[]`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5032-L5067) |
| Depth/stencil sequence | `3_6_12_9_6_12_9_3_6_12_9_3` | Rotates four two-view masks through three passes for depth and stencil behavior. | [`depthStencilMasks`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5069-L5074), [`tripleDepthStencilMasks()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4984-L4997) |
| Query mode | `no_queries`, `get_query_pool_results`, `cmd_copy_query_pool_results` | Selects no query, host retrieval, or command-buffer copyback. Query families use the latter two modes. | [`queryTypeCases[]`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5159-L5179) |
| Extent | `16x16x4`, `64x64x8`, `128x128x4`, `32x32x5`, `64x64x6`, `32x32x4`, `16x16x10` | Sets width, height, and array-layer capacity for the ordinary matrix. | [`extent3D[]`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5032-L5036) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R32G32B32A32_SFLOAT`, `VK_FORMAT_R8G8B8A8_UINT`, or `VK_FORMAT_UNDEFINED` | Exercises normalized color, multisample floating-point color, integer layer-index output, or depth-only rendering. | [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5113-L5126) |
| Sample count | `VK_SAMPLE_COUNT_1_BIT` or `VK_SAMPLE_COUNT_4_BIT` | Enables four-sample rendering for `multisample` and `multisample_resolve`. | [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5113-L5116) |
| Layout variant | absent or `_general_layout` | `view_mask_iteration` checks both transfer/color-attachment layouts and `VK_IMAGE_LAYOUT_GENERAL`. | [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5132-L5154) |
| Special case | `max_multi_view_view_count` | Fills masks from the device's `maxMultiviewViewCount` and uses that property as the layer count. | [`fillMissingParameters()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L744-L775), [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5209-L5218) |
| Point size | `2` and `4` | Uses different point sizes for view 0 and the remaining views. | [`TEST_POINT_SIZE_SMALL` and `TEST_POINT_SIZE_WIDE`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L148-L149), [`initPrograms()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4742-L4761) |

## Behavior Parameters

The primary behavioral axis is the registered test family. The rendering type, query mode, mask sequence, and format dimensions configure each family; they do not replace the family as the choice of property being tested.

### `masks` | view-mask selection

The shader keeps the vertex color unchanged. The reference image checks that each enabled view mask bit affects the corresponding layer.

### `input_attachments` | subpass input reads

The fragment shader reads `in_color_attachment` with `subpassLoad()` and writes that value to the color output. This family exists only for legacy and `renderpass2` render passes.

### `input_attachments_geometry` | geometry-stage input-attachment path

A geometry shader forwards the primitive, while the fragment shader reads `in_color_attachment` with `subpassLoad()` and writes that value; the checked path is the subpass input attachment, not the geometry shader's interpolated color.

### `instanced` | instance and view addressing

The vertex shader uses `gl_InstanceIndex` to move a square and encodes both instance and view into color. This checks that instancing and multiview addressing coexist.

### `input_instance` | instance-rate vertex input

The vertex shader forms the square from `gl_VertexIndex` while the two vertex attributes advance at instance rate. It encodes instance and view in the output color.

### `draw_indirect` | indirect non-indexed draw

The family uses the common view-index color path with an indirect draw implementation. The result check still compares the affected layers with the generated reference.

### `draw_indirect_indexed` | indirect indexed draw

This variant combines indirect execution with the shuffled index buffer path and checks the same per-view color relationship.

### `draw_indexed` | direct indexed draw

The host shuffles the index mapping with the test seed, binds an index buffer, and issues indexed draws. The reference uses the same mapping when it computes expected colors.

### `clear_attachments` | multiview attachment clear

The specialized instance performs attachment clears inside the multiview rendering sequence and compares the resulting layers.

### `secondary_cmd_buffer` | secondary command buffer

The test executes the rendering through a secondary command-buffer path. Its fragment shader adds `gl_ViewIndex * 0.10f` to the green channel.

### `secondary_cmd_buffer_geometry` | secondary command buffer with geometry shader

The secondary path includes the geometry shader, which emits the triangle strip and applies the view-dependent color.

### `point_size` | per-view point size

The vertex shader uses point size `4` for view 0 and point size `2` for every other view. The rasterized points provide the view-dependent image difference.

### `multisample` | four-sample multiview rendering

The instance uses `VK_SAMPLE_COUNT_4_BIT` and `VK_FORMAT_R32G32B32A32_SFLOAT`, then verifies the multisampled attachment through the common readback path.

### `multisample_resolve` | four-sample resolve

The instance adds a resolve attachment. Verification compares only layers resolved by at least one view mask.

### `queries` | precise query results

The test collects occlusion and timestamp query results and requires precise occlusion-query support. Precise occlusion results use the expected exact value.

### `non_precise_queries` | non-precise query results

The same query execution path accepts any non-zero occlusion result instead of requiring the precise count.

### `non_precise_queries_with_availability` | query availability

This variant checks the query path with availability-enabled result handling through both result retrieval modes.

### `readback_implicit_clear` | implicit-clear readback

The readback instance renders with the attachment's implicit clear behavior, copies the layered image, and compares the result.

### `readback_explicit_clear` | explicit-clear readback

This variant performs an explicit clear before rendering and uses the same layered-image comparison path.

### `depth` | depth attachment

The depth/stencil instance renders with depth enabled and checks per-layer depth-derived reference results using the fixed depth/stencil mask sequence.

### `depth_without_fragment_shader` | depth-only rendering

The factory selects `VK_FORMAT_UNDEFINED` for the color format and the instance uses a vertex-only pipeline to test depth behavior.

### `depth_different_ranges` | depth ranges across subpasses

The depth path changes the depth range between subpasses and requires `VK_EXT_depth_range_unrestricted`.

### `stencil` | stencil attachment

The depth/stencil instance uses stencil operations and checks the per-layer result with the same fixed mask sequence.

### `view_mask_iteration` | one rendering per mask

The instance creates one rendering operation for each mask, writes `gl_ViewIndex` into an integer color, and checks every layer exactly. It tests both the ordinary and `_general_layout` variants.

### `nested_cmd_buffer` | nested command buffer

The secondary-command-buffer instance exercises `VK_EXT_nested_command_buffer` and its nested rendering features while preserving the multiview view-index color check.

### `index` | shader-stage `gl_ViewIndex`

The `index` family contains four test families: `vertex_shader`, `fragment_shader`, `geometry_shader`, and `tessellation_shader`. Each places the view-index color contribution in the named shader stage.

## Shader Analysis

Shader generation is part of the tested behavior. The following walkthrough uses the exact `vertex_shader` path. Other ordinary families reuse the same generated vertex structure, while stage-specific `index` families move the `gl_ViewIndex` contribution to the selected stage. The mandatory SPIR-V artifact below was compiled with `glslangValidator`, validated with `spirv-val`, and disassembled with `spirv-dis` for the reconstructed GLSL.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.multiview.renderpass2.index.vertex_shader.no_queries.15
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `renderpass2` | Uses the `VK_KHR_create_renderpass2` render-pass wrapper. |
| `index.vertex_shader` | Places the view-index color change in the vertex stage. |
| `no_queries` | Uses the ordinary image result path. |
| `15` | Enables views 0 through 3 in one subpass. |

#### Purpose

The vertex shader carries the input color to the fragment stage and adds a green offset derived from `gl_ViewIndex`. The resulting layer colors distinguish the views selected by the render-pass view mask.

#### Structural Design

| Phase | Shader operation | Result |
|---|---|---|
| Inputs | Read position at location 0 and color at location 1. | The host-provided square geometry and base color enter the stage. |
| Position | Assign `in_position` to `gl_Position`. | Geometry keeps its host-defined placement. |
| View encoding | Convert `gl_ViewIndex` to float and multiply by `0.10`. | Each view receives a distinct green contribution. |
| Interface | Add the contribution to `in_color` and write `out_color`. | The fragment stage receives the expected per-view value. |

#### Shader Code

```glsl
#version 450
#extension GL_EXT_multiview : enable
layout(location = 0) in highp vec4 in_position;
layout(location = 1) in vec4 in_color;
layout(location = 0) out vec4 out_color;
void main (void)
{
    /// Preserve host geometry and encode the active multiview index in green.
    gl_Position = in_position;
    out_color = in_color + vec4(0.0, gl_ViewIndex * 0.10f, 0.0, 0.0);
}
```

#### Additional Info

- `gl_ViewIndex` is a built-in input supplied by multiview execution; the host does not provide it as a vertex attribute.
- The `15` case uses four views in one render-pass view mask, while the same shader generator serves the other mask sequences.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---|---|---|
| Test family | `vertex_shader` enables `generateColor`; the other stage-specific `index` families select fragment, geometry, or tessellation code paths. | [`initPrograms()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4787-L4929) |
| View-mask sequence | The GLSL is unchanged; the render-pass view mask changes which `gl_ViewIndex` invocations produce layers. | [`view-mask generation`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L5032-L5067) |
| Rendering type | The GLSL is unchanged; legacy and `renderpass2` use corresponding render-pass wrappers. | [`makeRenderPass()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L151-L211) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 33
; Schema: 0
               OpCapability Shader
               OpCapability MultiView
               OpExtension "SPV_KHR_multiview"
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position %out_color %in_color %gl_ViewIndex
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_multiview"
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpName %in_position "in_position"
               OpName %out_color "out_color"
               OpName %in_color "in_color"
               OpName %gl_ViewIndex "gl_ViewIndex"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
               OpDecorate %in_position Location 0
               OpDecorate %out_color Location 0
               OpDecorate %in_color Location 1
               OpDecorate %gl_ViewIndex BuiltIn ViewIndex
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %out_color = OpVariable %_ptr_Output_v4float Output
   %in_color = OpVariable %_ptr_Input_v4float Input
    %float_0 = OpConstant %float 0
%_ptr_Input_int = OpTypePointer Input %int
%gl_ViewIndex = OpVariable %_ptr_Input_int Input
%float_0_100000001 = OpConstant %float 0.100000001
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpLoad %v4float %in_position
         %20 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %20 %18
         %23 = OpLoad %v4float %in_color
         %27 = OpLoad %int %gl_ViewIndex
         %28 = OpConvertSToF %float %27
         %30 = OpFMul %float %28 %float_0_100000001
         %31 = OpCompositeConstruct %v4float %float_0 %30 %float_0 %float_0
         %32 = OpFAdd %v4float %23 %31
               OpStore %out_color %32
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The common instance creates a layered 2D image view. Its extent depth is the number of array layers needed by the selected mask sequence. It uploads position and color vertex buffers, and creates an index buffer for indexed families. See [`ImageAttachment`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L287-L330) and [`createVertexBuffer()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L778-L842).
- For legacy and `renderpass2`, the helper creates a render pass and framebuffer from the view-mask sequence. Dynamic rendering supplies the view mask in `VkRenderingInfo` and uses one rendering operation per subpass-like iteration. See [`MultiViewRenderTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L453-L507) and [`draw()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L618-L692).
- The command buffer clears the layered color image, transitions it to attachment use, binds one pipeline per subpass, and issues direct or indexed draws. Repeated view-mask use receives an attachment barrier before the next rendering operation. See [`beforeRenderPass()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L509-L610).
- The host copies the image to a host-visible buffer, waits for completion, invalidates the allocation, and compares the returned layers with generated references using a `0.01` float threshold. See [`readImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1190-L1274) and [`checkImage()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L1276-L1331).
- Query families use [`MultiViewQueriesTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L2987-L3071). They retrieve results with either `getQueryPoolResults` or `cmdCopyQueryPoolResults`; precise occlusion tests require the expected value, while non-precise tests require a non-zero value.
- Depth and stencil families use [`MultiViewDepthStencilTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3831-L3886). `view_mask_iteration` instead clears one layered image, performs one rendering per mask, copies all layers to verification buffers, and requires exact integer colors. See [`MultiViewMaskIterationTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4306-L4508).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `masks`, `draw_indexed`, `draw_indirect`, `draw_indirect_indexed` | View-mask selection, vertex/index addressing, draw execution, or layered color output. |
| `index` | `gl_ViewIndex` handling or the selected shader-stage interface. |
| `input_attachments`, `input_attachments_geometry` | Subpass input-attachment setup or geometry/input-attachment data flow. |
| `instanced`, `input_instance` | Instance addressing or vertex-input-rate handling. |
| `clear_attachments`, `readback_implicit_clear`, `readback_explicit_clear` | Attachment clear, load, layout, or copyback behavior. |
| `secondary_cmd_buffer`, `secondary_cmd_buffer_geometry`, `nested_cmd_buffer` | Command-buffer inheritance, nested rendering support, or view-index propagation. |
| `point_size` | Point-size capability, rasterization, or view-dependent point output. |
| `multisample`, `multisample_resolve` | Four-sample attachment or resolve behavior. |
| `queries`, `non_precise_queries`, `non_precise_queries_with_availability` | Query generation, availability, result retrieval, or timestamp behavior. |
| `depth`, `depth_without_fragment_shader`, `depth_different_ranges`, `stencil` | Per-layer depth/stencil state, range, attachment, or comparison behavior. |
| `view_mask_iteration` | View-mask layer selection, layout transition, or exact layer-index output. |

### Cause Analysis

#### Layer selection and rendered output

**Possible failure symptoms:** One or more enabled layers contain the wrong color, or a layer that no view mask enables contains rendered data.

**Possible implementation causes:** The implementation may apply the render-pass or dynamic-rendering view mask to the wrong array layers, propagate the wrong `gl_ViewIndex`, or mishandle repeated masks. The source and the multiview rules in [renderpass.adoc](../../../../vulkan-docs/src/chapters/renderpass.adoc#renderpass-multiview) provide the evidence needed to investigate the exact failing path.

#### Shader-stage interface

**Possible failure symptoms:** The image differs only for an `index` family or for a geometry/tessellation variant.

**Possible implementation causes:** The compiler or implementation may mishandle the `ViewIndex` built-in or the stage-to-stage interface. Source inspection is needed to distinguish shader compilation from rasterization or attachment errors.

#### Attachment and layout handling

**Possible failure symptoms:** Input-attachment, clear, readback, resolve, or `_general_layout` cases return stale, cleared, unresolved, or otherwise mismatched layers.

**Possible implementation causes:** The failure may involve subpass attachment setup, image layout transitions, load/store operations, synchronization, or resolve handling. The relevant cause depends on the first failing operation in the logged layer comparison.

#### Query result handling

**Possible failure symptoms:** A precise query differs from its expected value, a non-precise query is zero, availability is wrong, or timestamps cannot be read.

**Possible implementation causes:** Source-level investigation is needed to separate query-pool execution, availability propagation, copyback, and host retrieval. The test does not identify one implementation layer in advance.

#### Depth and stencil state

**Possible failure symptoms:** Layers disagree with the depth/stencil reference, including cases with no fragment shader or with different depth ranges.

**Possible implementation causes:** The implementation may mishandle per-view depth/stencil attachment state, depth-range setup, or stencil operations. `depth_different_ranges` also depends on the extension path checked by the test.

#### Command-buffer execution

**Possible failure symptoms:** The direct path passes but a secondary or nested command-buffer family produces missing or incorrect layers.

**Possible implementation causes:** Source-level investigation is needed for command-buffer inheritance, nested rendering feature handling, and propagation of the active view mask through command execution.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_multiview`. `renderpass2` requires `VK_KHR_create_renderpass2`; dynamic rendering requires `VK_KHR_dynamic_rendering` and is not registered for Vulkan SC. See [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4577-L4593).
- Geometry families require core `geometryShader` and `multiviewGeometryShader`; `tessellation_shader` requires `multiviewTessellationShader`. See [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4579-L4604).
- `point_size` requires `largePoints` and device limits/granularity that represent point sizes `2` and `4`. Query families require timestamp support, and `queries` additionally requires precise occlusion queries. See [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4623-L4660).
- `depth_different_ranges` requires `VK_EXT_depth_range_unrestricted`. `nested_cmd_buffer` requires `VK_EXT_nested_command_buffer` and, outside Vulkan SC, both `nestedCommandBuffer` and `nestedCommandBufferRendering`. See [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4594-L4599) and [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4662-L4677).
- Vulkan builds require `maxMultiviewViewCount` of at least six for the ordinary matrix. Vulkan SC checks that the device supports the number of views used by the selected case. See [`checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4609-L4621).

### Design-based pruning

- Query families are registered only under `get_query_pool_results` and `cmd_copy_query_pool_results`; other families are registered only under `no_queries`. This avoids meaningless query combinations.
- `input_attachments` is skipped for dynamic rendering because its shader calls `subpassLoad()`, which requires subpass input-attachment semantics.
- Depth and stencil use one fixed `64x64x4` case with the tripled mask sequence. `view_mask_iteration` adds `_general_layout` rather than combining that layout choice with every other family.
- `max_multi_view_view_count` uses empty masks as an intentional signal for `fillMissingParameters()` to query the device property and generate the one-bit sweep.

## Key Takeaways

- The same implementation checks multiview at several API boundaries: render-pass view masks, dynamic-rendering view masks, shader built-ins, layered attachments, and query result paths.
- The view mask controls which layers receive work. `view_mask_iteration` makes that relationship observable with an exact integer layer-index color.
- The `index` families differ by the shader stage that consumes `gl_ViewIndex`; the other rendering families vary host execution, attachments, or rasterization around the common layered result check.
- A passing color comparison or query check validates the produced result, not only successful Vulkan object creation or command submission.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Test registration matrix | [`multiViewRenderCreateTests()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4999-L5270) | Defines roots, families, masks, formats, query modes, and special cases. |
| Support checks | [`MultiViewRenderTestsCase::checkSupport()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4577-L4689) | Defines feature, extension, limit, and device-property gates. |
| Shader generation | [`MultiViewRenderTestsCase::initPrograms()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4691-L4929) | Emits the vertex, tessellation, geometry, and fragment shader variants. |
| Common render path | [`MultiViewRenderTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L453-L507) | Creates pipelines, submits rendering, reads layers, and checks the result. |
| Render helpers | [`vktMultiViewRenderUtil.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderUtil.cpp#L159-L230) | Builds multiview render passes and attachment descriptions. |
| Render-pass wrappers | [`vktMultiViewRenderPassUtil.cpp`](../../../modules/vulkan/multiview/vktMultiViewRenderPassUtil.cpp#L35-L230) | Supplies legacy and `renderpass2` wrapper types. |
| Query execution | [`MultiViewQueriesTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L2987-L3071) | Checks precise, non-precise, availability, and retrieval variants. |
| Depth and stencil execution | [`MultiViewDepthStencilTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L3831-L3886) | Implements depth/stencil rendering and result checking. |
| View-mask iteration | [`MultiViewMaskIterationTestInstance::iterate()`](../../../modules/vulkan/multiview/vktMultiViewRenderTests.cpp#L4306-L4508) | Checks exact per-layer view-index output and layout variants. |
