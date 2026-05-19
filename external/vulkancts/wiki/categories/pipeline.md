# Pipeline Tests

## Overview

The [`pipeline`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L224) category is the largest Vulkan CTS test bucket. It is structurally unique: rather than registering topic groups as direct children, it introduces an extra hierarchy layer through [`PipelineConstructionType`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L42) variant roots. Each variant root replicates most — but not all — topic groups via the shared dispatcher [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94). An additional independent root branch (`no_queues`) is registered outside the variant system.

The category covers fixed-function pipeline state (blend, depth, stencil, input assembly, vertex input, multisample, logic op), resource binding (descriptors, push constants, spec constants), image and sampler validation, pipeline construction models (monolithic, graphics pipeline library, shader object), cache and binary mechanics, dynamic state, and various extension-gated features.

## Registration Entry Point

The category is rooted in [`createTests()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L224), which creates eight direct children under `pipeline`:

```text
pipeline
├── monolithic                              (VK + VKSC)
├── pipeline_library                        (VK only)
├── fast_linked_library                     (VK only)
├── shader_object_unlinked_spirv            (VK only)
├── shader_object_unlinked_binary           (VK only)
├── shader_object_linked_spirv              (VK only)
├── shader_object_linked_binary             (VK only)
└── no_queues                               (VK only, independent root branch)
```

Source: [`createTests()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L224), cross-checked against mustpass files in [`vk-default`](../../mustpass/main/vk-default/).

### Variant Root to Mustpass Mapping

| Variant root | Mustpass file | Construction type enum |
|---|---|---|
| `monolithic` | `pipeline/monolithic/monolithic.txt` | [`PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L44) |
| `pipeline_library` | `pipeline-library.txt` | [`PIPELINE_CONSTRUCTION_TYPE_LINK_TIME_OPTIMIZED_LIBRARY`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L45) |
| `fast_linked_library` | `fast-linked-library.txt` | [`PIPELINE_CONSTRUCTION_TYPE_FAST_LINKED_LIBRARY`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L46) |
| `shader_object_unlinked_spirv` | `pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt` | [`PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_UNLINKED_SPIRV`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L47) |
| `shader_object_unlinked_binary` | `shader-object-unlinked-binary.txt` | [`PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_UNLINKED_BINARY`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L48) |
| `shader_object_linked_spirv` | `shader-object-linked-spirv.txt` | [`PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_LINKED_SPIRV`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L49) |
| `shader_object_linked_binary` | `shader-object-linked-binary.txt` | [`PIPELINE_CONSTRUCTION_TYPE_SHADER_OBJECT_LINKED_BINARY`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L50) |
| `no_queues` | `no-queues.txt` | Independent root branch |

Source: [`createTests()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L224), [`PipelineConstructionType`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L42).

## Variant-Root Architecture

Unlike other categories where each source file registers under one flat group, the pipeline category uses a two-axis structure:

- **Variant root axis**: Seven [`PipelineConstructionType`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L42) variants plus the independent `no_queues` branch.
- **Topic group axis**: Content groups registered under each variant root by [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94).

The shared dispatcher [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94) receives a `PipelineConstructionType` parameter and applies conditional predicates to decide which topic groups to register for each variant root.

### Root Predicates

These predicates control topic-group visibility across variant roots:

| Predicate | Definition | Effect |
|---|---|---|
| `isNotShaderObjectVariant` | [`isConstructionTypeShaderObject()`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L54) returns false | Excludes groups not applicable to any shader-object variant |
| `isNotExtraShaderObjectVariant` | Non-shader-object, or exactly `SHADER_OBJECT_UNLINKED_SPIRV` | Includes monolithic, library, and base shader-object variants only |
| `isMonolithicOrBaseESOVariant` | Exactly `MONOLITHIC` or `SHADER_OBJECT_UNLINKED_SPIRV` | Restricts to monolithic and base extended shader-object |
| `CTS_USES_VULKANSC` | Compile-time guard | Removes Vulkan-only roots and many topic groups |

Source: [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L96) through [`vktPipelineTests.cpp#L102`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L102).

## Topic-Group Registration Matrix

The following table shows each topic group's variant coverage, verified against [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94).

| Topic group | Condition class | VKSC | Registration line |
|---|---|---|---|
| `dynamic_control_points` | All variants | Available | [`vktPipelineTests.cpp#L106`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L106) |
| `stencil` | Not extra shader-object | Available | [`vktPipelineTests.cpp#L108`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L108) |
| `blend` | All variants | Available | [`vktPipelineTests.cpp#L109`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L109) |
| `depth` | All variants | Available | [`vktPipelineTests.cpp#L110`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L110) |
| `descriptor_limits` | All variants | Available | [`vktPipelineTests.cpp#L111`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L111) |
| `dynamic_offset` | All variants | Available | [`vktPipelineTests.cpp#L112`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L112) |
| `dynamic_vertex_attribute` | All variants | Available | [`vktPipelineTests.cpp#L113`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L113) |
| `early_destroy` | All variants | VK only | [`vktPipelineTests.cpp#L115`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L115) |
| `image` | Monolithic or base ESO | Available | [`vktPipelineTests.cpp#L118`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L118) |
| `sampler` | All variants | Available | [`vktPipelineTests.cpp#L119`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L119) |
| `image_view` | Monolithic or base ESO | Available | [`vktPipelineTests.cpp#L121`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L121) |
| `image_2d_view_3d_image` | All variants | VK only | [`vktPipelineTests.cpp#L123`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L123) |
| `logic_op` | All variants | Available | [`vktPipelineTests.cpp#L125`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L125) |
| `logic_op_na_formats` | All variants | Available | [`vktPipelineTests.cpp#L126`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L126) |
| `push_constant` | All variants | VK only | [`vktPipelineTests.cpp#L128`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L128) |
| `push_descriptor` | All variants | VK only | [`vktPipelineTests.cpp#L129`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L129) |
| `matched_attachments` | All variants | VK only | [`vktPipelineTests.cpp#L130`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L130) |
| `spec_constant` | All variants | Available | [`vktPipelineTests.cpp#L132`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L132) |
| `multisample` | All variants | Available | [`vktPipelineTests.cpp#L133`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L133) |
| `multisample_with_fragment_shading_rate` | All variants | Available | [`vktPipelineTests.cpp#L134`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L134) |
| `multisample_interpolation` | All variants | Available | [`vktPipelineTests.cpp#L135`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L135) |
| `multisample_shader_builtin` | Not shader-object | VK only | [`vktPipelineTests.cpp#L140`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L140) |
| `vertex_input` | All variants | Available | [`vktPipelineTests.cpp#L143`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L143) |
| `input_assembly` | All variants | Available | [`vktPipelineTests.cpp#L144`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L144) |
| `interface_matching` | All variants | Available | [`vktPipelineTests.cpp#L145`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L145) |
| `timestamp` | All variants | Available | [`vktPipelineTests.cpp#L146`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L146) |
| `cache` | All variants | VK only | [`vktPipelineTests.cpp#L148`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L148) |
| `pipeline_binary` | Not shader-object | VK only | [`vktPipelineTests.cpp#L152`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L152) |
| `framebuffer_attachment` | All variants | VK only | [`vktPipelineTests.cpp#L159`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L159) |
| `render_to_image` | All variants | Available | [`vktPipelineTests.cpp#L161`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L161) |
| `shader_stencil_export` | All variants | Available | [`vktPipelineTests.cpp#L162`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L162) |
| `creation_feedback` | All variants | VK only | [`vktPipelineTests.cpp#L164`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L164) |
| `depth_range_unrestricted` | All variants | VK only | [`vktPipelineTests.cpp#L165`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L165) |
| `executable_properties` | Not shader-object | VK only | [`vktPipelineTests.cpp#L168`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L168) |
| `max_varyings` | All variants | Available | [`vktPipelineTests.cpp#L171`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L171) |
| `blend_operation_advanced` | All variants | Available | [`vktPipelineTests.cpp#L172`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L172) |
| `extended_dynamic_state` | Not extra shader-object | Available | [`vktPipelineTests.cpp#L174`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L174) |
| `no_position` | All variants | Available | [`vktPipelineTests.cpp#L175`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L175) |
| `bind_point` | All variants | VK only | [`vktPipelineTests.cpp#L177`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L177) |
| `color_write_enable` | All variants | Available | [`vktPipelineTests.cpp#L179`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L179) |
| `attachment_feedback_loop_layout` | All variants | VK only | [`vktPipelineTests.cpp#L181`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L181) |
| `shader_module_identifier` | Not shader-object | VK only | [`vktPipelineTests.cpp#L184`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L184) |
| `pipeline_cache` | Not shader-object | VK only | [`vktPipelineTests.cpp#L185`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L185) |
| `color_write_enable_maxa` | All variants | Available | [`vktPipelineTests.cpp#L188`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L188) |
| `misc` | All variants | Available | [`vktPipelineTests.cpp#L189`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L189) |
| `bind_buffers_2` | All variants | Available | [`vktPipelineTests.cpp#L190`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L190) |
| `input_attribute_offset` | All variants | Available | [`vktPipelineTests.cpp#L191`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L191) |
| `derivative` | Monolithic only | VK only | [`vktPipelineTests.cpp#L202`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L202) |
| `creation_cache_control` | Monolithic only | VK only | [`vktPipelineTests.cpp#L205`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L205) |
| `sliced_view_of_3d_image` | Monolithic only | VK only | [`vktPipelineTests.cpp#L208`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L208) |
| `graphics_library` | Pipeline library only | VK only | [`vktPipelineTests.cpp#L215`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L215) |
| `empty_fs` | All variants | Available | [`vktPipelineTests.cpp#L219`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L219) |
| `no_queues` | Independent root branch | VK only | [`vktPipelineTests.cpp#L261`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L261) |

## File Inventory

### Registration and dispatcher

| File | Role | Verified group | Level-3 doc |
|---|---|---|---|
| [`vktPipelineTests.cpp`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L1) | Category root / variant-root dispatcher | (root) | — |

### Fixed-function pipeline state

| File | Verified group(s) | Variant coverage | Level-3 doc |
|---|---|---|---|
| [`vktPipelineStencilTests.cpp`](../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1) | `stencil` | Not extra shader-object | [`vktPipelineStencilTests.md`](../testfiles/pipeline/vktPipelineStencilTests.md) |
| [`vktPipelineBlendTests.cpp`](../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1) | `blend` | All variants | [`vktPipelineBlendTests.md`](../testfiles/pipeline/vktPipelineBlendTests.md) |
| [`vktPipelineDualBlendTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDualBlendTests.cpp#L1) | `blend.dual_source.multi_attachments` (nested) | All variants | [`vktPipelineDualBlendTests.md`](../testfiles/pipeline/vktPipelineDualBlendTests.md) |
| [`vktPipelineDepthTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1) | `depth` | All variants | [`vktPipelineDepthTests.md`](../testfiles/pipeline/vktPipelineDepthTests.md) |
| [`vktPipelineLogicOpTests.cpp`](../../modules/vulkan/pipeline/vktPipelineLogicOpTests.cpp#L1) | `logic_op`, `logic_op_na_formats` | All variants | [`vktPipelineLogicOpTests.md`](../testfiles/pipeline/vktPipelineLogicOpTests.md) |
| [`vktPipelineInputAssemblyTests.cpp`](../../modules/vulkan/pipeline/vktPipelineInputAssemblyTests.cpp#L1) | `input_assembly` | All variants | [`vktPipelineInputAssemblyTests.md`](../testfiles/pipeline/vktPipelineInputAssemblyTests.md) |
| [`vktPipelineVertexInputTests.cpp`](../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1) | `vertex_input` | All variants | [`vktPipelineVertexInputTests.md`](../testfiles/pipeline/vktPipelineVertexInputTests.md) |
| [`vktPipelineVertexInputSRGBTests.cpp`](../../modules/vulkan/pipeline/vktPipelineVertexInputSRGBTests.cpp#L1) | `vertex_input.srgb_vertex_formats` (nested) | All variants | [`vktPipelineVertexInputSRGBTests.md`](../testfiles/pipeline/vktPipelineVertexInputSRGBTests.md) |
| [`vktPipelineLegacyAttrTests.cpp`](../../modules/vulkan/pipeline/vktPipelineLegacyAttrTests.cpp#L1) | `vertex_input.legacy_vertex_attributes` (nested) | All variants | [`vktPipelineLegacyAttrTests.md`](../testfiles/pipeline/vktPipelineLegacyAttrTests.md) |
| [`vktPipelineDynamicVertexAttributeTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDynamicVertexAttributeTests.cpp#L1) | `dynamic_vertex_attribute` | All variants | [`vktPipelineDynamicVertexAttributeTests.md`](../testfiles/pipeline/vktPipelineDynamicVertexAttributeTests.md) |
| [`vktPipelineInputAttributeOffsetTests.cpp`](../../modules/vulkan/pipeline/vktPipelineInputAttributeOffsetTests.cpp#L1) | `input_attribute_offset` | All variants | [`vktPipelineInputAttributeOffsetTests.md`](../testfiles/pipeline/vktPipelineInputAttributeOffsetTests.md) |
| [`vktPipelineColorWriteEnableTests.cpp`](../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1) | `color_write_enable`, `color_write_enable_maxa` | All variants | [`vktPipelineColorWriteEnableTests.md`](../testfiles/pipeline/vktPipelineColorWriteEnableTests.md) |

### Resources and interfaces

| File | Verified group(s) | Variant coverage | Level-3 doc |
|---|---|---|---|
| [`vktPipelineDescriptorLimitsTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDescriptorLimitsTests.cpp#L1) | `descriptor_limits` | All variants | [`vktPipelineDescriptorLimitsTests.md`](../testfiles/pipeline/vktPipelineDescriptorLimitsTests.md) |
| [`vktPipelineDynamicOffsetTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDynamicOffsetTests.cpp#L1) | `dynamic_offset` | All variants | [`vktPipelineDynamicOffsetTests.md`](../testfiles/pipeline/vktPipelineDynamicOffsetTests.md) |
| [`vktPipelinePushConstantTests.cpp`](../../modules/vulkan/pipeline/vktPipelinePushConstantTests.cpp#L1) | `push_constant` | All variants, VK only | [`vktPipelinePushConstantTests.md`](../testfiles/pipeline/vktPipelinePushConstantTests.md) |
| [`vktPipelinePushDescriptorTests.cpp`](../../modules/vulkan/pipeline/vktPipelinePushDescriptorTests.cpp#L1) | `push_descriptor` | All variants, VK only | [`vktPipelinePushDescriptorTests.md`](../testfiles/pipeline/vktPipelinePushDescriptorTests.md) |
| [`vktPipelineSpecConstantTests.cpp`](../../modules/vulkan/pipeline/vktPipelineSpecConstantTests.cpp#L1) | `spec_constant` | All variants | [`vktPipelineSpecConstantTests.md`](../testfiles/pipeline/vktPipelineSpecConstantTests.md) |
| [`vktPipelineInterfaceMatchingTests.cpp`](../../modules/vulkan/pipeline/vktPipelineInterfaceMatchingTests.cpp#L1) | `interface_matching` | All variants | [`vktPipelineInterfaceMatchingTests.md`](../testfiles/pipeline/vktPipelineInterfaceMatchingTests.md) |
| [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp`](../../modules/vulkan/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.cpp#L1) | `interface_matching.shader_layout_component_matching` (nested) | All variants | [`vktPipelineShaderComponentDecoratedLayoutMatchingTests.md`](../testfiles/pipeline/vktPipelineShaderComponentDecoratedLayoutMatchingTests.md) |
| [`vktPipelineMaxVaryingsTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1) | `max_varyings` | All variants | [`vktPipelineMaxVaryingsTests.md`](../testfiles/pipeline/vktPipelineMaxVaryingsTests.md) |

### Images, samplers, attachments, render targets

| File | Verified group(s) | Variant coverage | Level-3 doc |
|---|---|---|---|
| [`vktPipelineImageTests.cpp`](../../modules/vulkan/pipeline/vktPipelineImageTests.cpp#L1) | `image` | Monolithic or base ESO | [`vktPipelineImageTests.md`](../testfiles/pipeline/vktPipelineImageTests.md) |
| [`vktPipelineImageViewTests.cpp`](../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L1) | `image_view` | Monolithic or base ESO | [`vktPipelineImageViewTests.md`](../testfiles/pipeline/vktPipelineImageViewTests.md) |
| [`vktPipelineImage2DViewOf3DTests.cpp`](../../modules/vulkan/pipeline/vktPipelineImage2DViewOf3DTests.cpp#L1) | `image_2d_view_3d_image` | All variants, VK only | [`vktPipelineImage2DViewOf3DTests.md`](../testfiles/pipeline/vktPipelineImage2DViewOf3DTests.md) |
| [`vktPipelineImageSlicedViewOf3DTests.cpp`](../../modules/vulkan/pipeline/vktPipelineImageSlicedViewOf3DTests.cpp#L1) | `sliced_view_of_3d_image` | Monolithic only, VK only | [`vktPipelineImageSlicedViewOf3DTests.md`](../testfiles/pipeline/vktPipelineImageSlicedViewOf3DTests.md) |
| [`vktPipelineSamplerTests.cpp`](../../modules/vulkan/pipeline/vktPipelineSamplerTests.cpp#L1) | `sampler` (incl. nested `border_swizzle`) | All variants | [`vktPipelineSamplerTests.md`](../testfiles/pipeline/vktPipelineSamplerTests.md) |
| [`vktPipelineRenderToImageTests.cpp`](../../modules/vulkan/pipeline/vktPipelineRenderToImageTests.cpp#L1) | `render_to_image` | All variants | [`vktPipelineRenderToImageTests.md`](../testfiles/pipeline/vktPipelineRenderToImageTests.md) |
| [`vktPipelineFramebufferAttachmentTests.cpp`](../../modules/vulkan/pipeline/vktPipelineFramebufferAttachmentTests.cpp#L1) | `framebuffer_attachment` | All variants, VK only | [`vktPipelineFramebufferAttachmentTests.md`](../testfiles/pipeline/vktPipelineFramebufferAttachmentTests.md) |
| [`vktPipelineMatchedAttachmentsTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMatchedAttachmentsTests.cpp#L1) | `matched_attachments` | All variants, VK only | [`vktPipelineMatchedAttachmentsTests.md`](../testfiles/pipeline/vktPipelineMatchedAttachmentsTests.md) |
| [`vktPipelineAttachmentFeedbackLoopLayoutTests.cpp`](../../modules/vulkan/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.cpp#L1) | `attachment_feedback_loop_layout` | All variants, VK only | [`vktPipelineAttachmentFeedbackLoopLayoutTests.md`](../testfiles/pipeline/vktPipelineAttachmentFeedbackLoopLayoutTests.md) |

### Multisample and interpolation

| File | Verified group(s) | Variant coverage | Level-3 doc |
|---|---|---|---|
| [`vktPipelineMultisampleTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L1) | `multisample`, `multisample_with_fragment_shading_rate` | All variants | [`vktPipelineMultisampleTests.md`](../testfiles/pipeline/vktPipelineMultisampleTests.md) |
| [`vktPipelineMultisampleInterpolationTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleInterpolationTests.cpp#L1) | `multisample_interpolation` | All variants | [`vktPipelineMultisampleInterpolationTests.md`](../testfiles/pipeline/vktPipelineMultisampleInterpolationTests.md) |
| [`vktPipelineMultisampleShaderBuiltInTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleShaderBuiltInTests.cpp#L1) | `multisample_shader_builtin` | Not shader-object, VK only | [`vktPipelineMultisampleShaderBuiltInTests.md`](../testfiles/pipeline/vktPipelineMultisampleShaderBuiltInTests.md) |
| [`vktPipelineMultisampleImageTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleImageTests.cpp#L1) | `sampled_image`, `storage_image`, etc. (nested) | All variants | [`vktPipelineMultisampleImageTests.md`](../testfiles/pipeline/vktPipelineMultisampleImageTests.md) |
| [`vktPipelineMultisampleMixedAttachmentSamplesTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.cpp#L1) | `mixed_attachment_samples` (nested) | All variants | [`vktPipelineMultisampleMixedAttachmentSamplesTests.md`](../testfiles/pipeline/vktPipelineMultisampleMixedAttachmentSamplesTests.md) |
| [`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1) | `multisampled_render_to_single_sampled`, `misc` (nested) | All variants | [`vktPipelineMultisampledRenderToSingleSampledTests.md`](../testfiles/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.md) |
| [`vktPipelineMultisampleResolveMaint10Tests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleResolveMaint10Tests.cpp#L1) | `m10_resolve` (nested) | All variants | [`vktPipelineMultisampleResolveMaint10Tests.md`](../testfiles/pipeline/vktPipelineMultisampleResolveMaint10Tests.md) |
| [`vktPipelineMultisampleResolveRenderAreaTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleResolveRenderAreaTests.cpp#L1) | `resolve` (nested) | All variants | [`vktPipelineMultisampleResolveRenderAreaTests.md`](../testfiles/pipeline/vktPipelineMultisampleResolveRenderAreaTests.md) |
| [`vktPipelineMultisampleSampleLocationsExtTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleSampleLocationsExtTests.cpp#L1) | `sample_locations_ext`, `std_sample_locations` (nested) | All variants | [`vktPipelineMultisampleSampleLocationsExtTests.md`](../testfiles/pipeline/vktPipelineMultisampleSampleLocationsExtTests.md) |
| [`vktPipelineMultisampleShaderFragmentMaskTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.cpp#L1) | `shader_fragment_mask` (nested) | All variants | [`vktPipelineMultisampleShaderFragmentMaskTests.md`](../testfiles/pipeline/vktPipelineMultisampleShaderFragmentMaskTests.md) |

### Construction, cache, binary, library, metadata

| File | Verified group(s) | Variant coverage | Level-3 doc |
|---|---|---|---|
| [`vktPipelineCacheTests.cpp`](../../modules/vulkan/pipeline/vktPipelineCacheTests.cpp#L1) | `cache` | All variants, VK only | [`vktPipelineCacheTests.md`](../testfiles/pipeline/vktPipelineCacheTests.md) |
| [`vktPipelineBinaryTests.cpp`](../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1) | `pipeline_binary` (aggregated: basic, creation feedback, dedicated) | Not shader-object, VK only | [`vktPipelineBinaryTests.md`](../testfiles/pipeline/vktPipelineBinaryTests.md) |
| [`vktPipelineCreationFeedbackTests.cpp`](../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1) | `creation_feedback` | All variants, VK only | [`vktPipelineCreationFeedbackTests.md`](../testfiles/pipeline/vktPipelineCreationFeedbackTests.md) |
| [`vktPipelineCreationCacheControlTests.cpp`](../../modules/vulkan/pipeline/vktPipelineCreationCacheControlTests.cpp#L1) | `creation_cache_control` | Monolithic only, VK only | [`vktPipelineCreationCacheControlTests.md`](../testfiles/pipeline/vktPipelineCreationCacheControlTests.md) |
| [`vktPipelineExecutablePropertiesTests.cpp`](../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1) | `executable_properties` | Not shader-object, VK only | [`vktPipelineExecutablePropertiesTests.md`](../testfiles/pipeline/vktPipelineExecutablePropertiesTests.md) |
| [`vktPipelineDerivativeTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDerivativeTests.cpp#L1) | `derivative` | Monolithic only, VK only | [`vktPipelineDerivativeTests.md`](../testfiles/pipeline/vktPipelineDerivativeTests.md) |
| [`vktPipelineLibraryTests.cpp`](../../modules/vulkan/pipeline/vktPipelineLibraryTests.cpp#L1) | `graphics_library` | Pipeline library only, VK only | [`vktPipelineLibraryTests.md`](../testfiles/pipeline/vktPipelineLibraryTests.md) |
| [`vktPipelineShaderModuleIdentifierTests.cpp`](../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L1) | `shader_module_identifier` | Not shader-object, VK only | [`vktPipelineShaderModuleIdentifierTests.md`](../testfiles/pipeline/vktPipelineShaderModuleIdentifierTests.md) |
| [`vktPipelineRobustnessCacheTests.cpp`](../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L1) | `pipeline_cache` (robustness-cache interaction) | Not shader-object, VK only | [`vktPipelineRobustnessCacheTests.md`](../testfiles/pipeline/vktPipelineRobustnessCacheTests.md) |
| [`vktPipelineTimestampTests.cpp`](../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L1) | `timestamp` | All variants | [`vktPipelineTimestampTests.md`](../testfiles/pipeline/vktPipelineTimestampTests.md) |
| [`vktPipelineEarlyDestroyTests.cpp`](../../modules/vulkan/pipeline/vktPipelineEarlyDestroyTests.cpp#L1) | `early_destroy` | All variants, VK only | [`vktPipelineEarlyDestroyTests.md`](../testfiles/pipeline/vktPipelineEarlyDestroyTests.md) |

### Dynamic state and extensions

| File | Verified group(s) | Variant coverage | Level-3 doc |
|---|---|---|---|
| [`vktPipelineExtendedDynamicStateTests.cpp`](../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L1) | `extended_dynamic_state` | Not extra shader-object | [`vktPipelineExtendedDynamicStateTests.md`](../testfiles/pipeline/vktPipelineExtendedDynamicStateTests.md) |
| [`vktPipelineExtendedDynamicStateMiscTests.cpp`](../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L1) | `extended_dynamic_state.misc` (nested) | Not extra shader-object | [`vktPipelineExtendedDynamicStateMiscTests.md`](../testfiles/pipeline/vktPipelineExtendedDynamicStateMiscTests.md) |
| [`vktPipelineDynamicControlPoints.cpp`](../../modules/vulkan/pipeline/vktPipelineDynamicControlPoints.cpp#L1) | `dynamic_control_points` | All variants | [`vktPipelineDynamicControlPoints.md`](../testfiles/pipeline/vktPipelineDynamicControlPoints.md) |
| [`vktPipelineBlendOperationAdvancedTests.cpp`](../../modules/vulkan/pipeline/vktPipelineBlendOperationAdvancedTests.cpp#L1) | `blend_operation_advanced` | All variants | [`vktPipelineBlendOperationAdvancedTests.md`](../testfiles/pipeline/vktPipelineBlendOperationAdvancedTests.md) |
| [`vktPipelineDepthRangeUnrestrictedTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDepthRangeUnrestrictedTests.cpp#L1) | `depth_range_unrestricted` | All variants, VK only | [`vktPipelineDepthRangeUnrestrictedTests.md`](../testfiles/pipeline/vktPipelineDepthRangeUnrestrictedTests.md) |
| [`vktPipelineStencilExportTests.cpp`](../../modules/vulkan/pipeline/vktPipelineStencilExportTests.cpp#L1) | `shader_stencil_export` | All variants | [`vktPipelineStencilExportTests.md`](../testfiles/pipeline/vktPipelineStencilExportTests.md) |
| [`vktPipelineBindPointTests.cpp`](../../modules/vulkan/pipeline/vktPipelineBindPointTests.cpp#L1) | `bind_point` | All variants, VK only | [`vktPipelineBindPointTests.md`](../testfiles/pipeline/vktPipelineBindPointTests.md) |
| [`vktPipelineBindVertexBuffers2Tests.cpp`](../../modules/vulkan/pipeline/vktPipelineBindVertexBuffers2Tests.cpp#L1) | `bind_buffers_2` | All variants | [`vktPipelineBindVertexBuffers2Tests.md`](../testfiles/pipeline/vktPipelineBindVertexBuffers2Tests.md) |
| [`vktPipelineNoPositionTests.cpp`](../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1) | `no_position` | All variants | [`vktPipelineNoPositionTests.md`](../testfiles/pipeline/vktPipelineNoPositionTests.md) |
| [`vktPipelineEmptyFSTests.cpp`](../../modules/vulkan/pipeline/vktPipelineEmptyFSTests.cpp#L1) | `empty_fs` | All variants | [`vktPipelineEmptyFSTests.md`](../testfiles/pipeline/vktPipelineEmptyFSTests.md) |
| [`vktPipelineMiscTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMiscTests.cpp#L1) | `misc` | All variants | [`vktPipelineMiscTests.md`](../testfiles/pipeline/vktPipelineMiscTests.md) |

### Independent root branch

| File | Verified group | Variant coverage | Level-3 doc |
|---|---|---|---|
| [`vktPipelineNoQueuesTests.cpp`](../../modules/vulkan/pipeline/vktPipelineNoQueuesTests.cpp#L1) | `no_queues` | Independent root branch, VK only | [`vktPipelineNoQueuesTests.md`](../testfiles/pipeline/vktPipelineNoQueuesTests.md) |

### Helper-only files (not Level-3 units)

These files support test implementation but do not register tests independently:

| File | Role |
|---|---|
| [`vktPipelineImageUtil.cpp`](../../modules/vulkan/pipeline/vktPipelineImageUtil.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineImageUtil.hpp#L1) | Image-related helper utilities |
| [`vktPipelineClearUtil.cpp`](../../modules/vulkan/pipeline/vktPipelineClearUtil.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineClearUtil.hpp#L1) | Clear/render helper utilities |
| [`vktPipelineMakeUtil.cpp`](../../modules/vulkan/pipeline/vktPipelineMakeUtil.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineMakeUtil.hpp#L1) | Pipeline object creation helpers |
| [`vktPipelineReferenceRenderer.cpp`](../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.hpp#L1) | Reference rendering and expected-output support |
| [`vktPipelineVertexUtil.cpp`](../../modules/vulkan/pipeline/vktPipelineVertexUtil.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineVertexUtil.hpp#L1) | Vertex data and layout helper utilities |
| [`vktPipelineMultisampleTestsUtil.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleTestsUtil.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleTestsUtil.hpp#L1) | Multisample shared helper utilities |
| [`vktPipelineSampleLocationsUtil.cpp`](../../modules/vulkan/pipeline/vktPipelineSampleLocationsUtil.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineSampleLocationsUtil.hpp#L1) | Sample-location helper utilities |
| [`vktPipelineSpecConstantUtil.cpp`](../../modules/vulkan/pipeline/vktPipelineSpecConstantUtil.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineSpecConstantUtil.hpp#L1) | Specialization-constant helper utilities |
| [`vktPipelineBlendTestsCommon.cpp`](../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineBlendTestsCommon.hpp#L1) | Shared blend-test support |
| [`vktPipelineCombinationsIterator.hpp`](../../modules/vulkan/pipeline/vktPipelineCombinationsIterator.hpp#L1) | Parameter-combination iterator helper |
| [`vktPipelineUniqueRandomIterator.hpp`](../../modules/vulkan/pipeline/vktPipelineUniqueRandomIterator.hpp#L1) | Randomized iterator helper |
| [`vktPipelineImageSamplingInstance.cpp`](../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineImageSamplingInstance.hpp#L1) | Shared image-sampling test-instance support |
| [`vktPipelineMultisampleBase.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleBase.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleBase.hpp#L1) | Multisample base classes and templates |
| [`vktPipelineMultisampleBaseResolve.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleBaseResolve.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleBaseResolve.hpp#L1) | Multisample resolve base support |
| [`vktPipelineMultisampleBaseResolveAndPerSampleFetch.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleBaseResolveAndPerSampleFetch.cpp#L1) / [`.hpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleBaseResolveAndPerSampleFetch.hpp#L1) | Multisample resolve and per-sample-fetch base support |

## VK / VKSC Split

Under `CTS_USES_VULKANSC`, only the `monolithic` variant root is registered ([`vktPipelineTests.cpp#L228`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L228)). All other variant roots (`pipeline_library`, `fast_linked_library`, and the four shader-object variants) are Vulkan-only. The independent `no_queues` branch is also Vulkan-only ([`vktPipelineTests.cpp#L261`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L261)).

Within [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94), the following topic groups are excluded from VKSC by `#ifndef CTS_USES_VULKANSC` guards:

`early_destroy`, `image_2d_view_3d_image`, `push_constant`, `push_descriptor`, `matched_attachments`, `multisample_shader_builtin`, `cache`, `pipeline_binary`, `framebuffer_attachment`, `creation_feedback`, `depth_range_unrestricted`, `executable_properties`, `bind_point`, `attachment_feedback_loop_layout`, `shader_module_identifier`, `pipeline_cache`, `derivative`, `creation_cache_control`, `sliced_view_of_3d_image`, `graphics_library`, `no_queues`.

Source: [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L114) through [`vktPipelineTests.cpp#L219`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L219), [`createTests()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L228).

## Cross-File Themes

### PipelineConstructionType as a universal parameter

Every topic group registered through [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94) receives a [`PipelineConstructionType`](../../framework/vulkan/vkPipelineConstructionUtil.hpp#L42) parameter. This drives the selection of pipeline construction path (monolithic `vkCreateGraphicsPipelines`, graphics pipeline library link-time optimization, fast-linked library, or shader object) via [`GraphicsPipelineWrapper`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L193). Representative files: [`vktPipelineBlendTests.cpp`](../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1), [`vktPipelineDepthTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1), [`vktPipelineMultisampleTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L1).

### Reference rendering and CPU comparison

The [`ReferenceRenderer`](../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1) helper is used across fixed-function state tests (blend, depth, stencil, logic op, input assembly, color write enable) to compute expected output on the CPU and compare against GPU results via `tcu::floatThresholdCompare()` or `tcu::fuzzyCompare()`.

### Format-driven parameterization

Many test files iterate over format lists as a primary dimension: blend factors across color formats ([`vktPipelineBlendTests.cpp`](../../modules/vulkan/pipeline/vktPipelineBlendTests.cpp#L1)), depth/stencil formats ([`vktPipelineDepthTests.cpp`](../../modules/vulkan/pipeline/vktPipelineDepthTests.cpp#L1), [`vktPipelineStencilTests.cpp`](../../modules/vulkan/pipeline/vktPipelineStencilTests.cpp#L1)), image view formats ([`vktPipelineImageViewTests.cpp`](../../modules/vulkan/pipeline/vktPipelineImageViewTests.cpp#L1)), and vertex input formats ([`vktPipelineVertexInputTests.cpp`](../../modules/vulkan/pipeline/vktPipelineVertexInputTests.cpp#L1)).

### Multisample test hierarchy

The multisample subtree is the deepest nested structure in the pipeline category. [`vktPipelineMultisampleTests.cpp`](../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L1) acts as a dispatcher, delegating to nine nested subgroup files for specialized functionality (resolve, interpolation, sample locations, shader builtins, image access, mixed attachment samples, render-to-single-sampled, maintenance-10 resolve, and shader fragment mask).

### Pipeline cache, binary, and creation feedback interaction

[`vktPipelineBinaryTests.cpp`](../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1) aggregates basic, creation-feedback, and dedicated pipeline-binary subgroups under `pipeline_binary` ([`vktPipelineTests.cpp#L152`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L152)). Separately, [`vktPipelineCreationFeedbackTests.cpp`](../../modules/vulkan/pipeline/vktPipelineCreationFeedbackTests.cpp#L1) registers its own `creation_feedback` topic group ([`vktPipelineTests.cpp#L164`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L164)). The robustness-cache interaction tests ([`vktPipelineRobustnessCacheTests.cpp`](../../modules/vulkan/pipeline/vktPipelineRobustnessCacheTests.cpp#L1)) test `pipeline_cache` as a distinct topic group. This means creation-feedback coverage spans two topic groups and two Level-3 pages.

### Variant-restricted topic groups

Several topic groups are intentionally restricted to specific variant roots because their semantics do not generalize across construction types:

| Restriction | Topic groups | Rationale |
|---|---|---|
| Monolithic only | `derivative`, `creation_cache_control`, `sliced_view_of_3d_image` | Compute pipeline tests and timing-sensitive creation tests not meaningful for library/shader-object variants |
| Pipeline library only | `graphics_library` | Library-specific linking behavior tested once |
| Not shader-object | `multisample_shader_builtin`, `cache`, `pipeline_binary`, `executable_properties`, `shader_module_identifier`, `pipeline_cache` | Input attachments or cache/binary semantics not applicable to shader objects |
| Not extra shader-object | `stencil`, `extended_dynamic_state` | Skipped by linked binary/linked spirv shader-object variants |
| Monolithic or base ESO | `image`, `image_view` | Restricted to monolithic and `shader_object_unlinked_spirv` |

Source: [`createChildren()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L94).

## Cross-File Recurring Verification Methods

- **CPU reference image comparison**: thresholded framebuffer comparison via `tcu::floatThresholdCompare()` or `tcu::fuzzyCompare()` against [`ReferenceRenderer`](../../modules/vulkan/pipeline/vktPipelineReferenceRenderer.cpp#L1) output (blend, depth, stencil, logic op, multisample, color write enable)
- **Structural validation**: pipeline creation success/failure, handle validity, state query consistency (cache, binary, creation feedback, executable properties, descriptor limits)
- **Format property verification**: iterating over format caps and verifying rendering correctness per format (image, image view, vertex input, depth, stencil, blend)
- **Extension feature gating**: checking extension availability before test execution (dynamic state, shader module identifier, pipeline binary, robustness, etc.)
- **Pipeline construction type validation**: verifying that the same rendering result is achieved regardless of construction type (most topic groups under variant roots)

## Notes

- Official tracker count: **8** direct children under `pipeline` (seven variant roots plus `no_queues`).
- The 62 Level-3 pages intentionally diverge from the direct-child count because topic groups are registered under variant roots, not directly under `pipeline`.
- VKSC exposes only the `monolithic` variant root with a reduced set of topic groups (21 VK-only topic groups are excluded).
- The `pipeline_binary` topic group is a composite: [`vktPipelineBinaryTests.cpp`](../../modules/vulkan/pipeline/vktPipelineBinaryTests.cpp#L1) aggregates three subgroups (basic, creation feedback, dedicated) that are added via separate factory calls ([`vktPipelineTests.cpp#L153`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L153) through [`vktPipelineTests.cpp#L156`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L156)).
- The `multisample` topic is registered twice per variant root: once as `multisample` and once as `multisample_with_fragment_shading_rate`, both from [`createMultisampleTests()`](../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7247) with different `useFragmentShadingRate` flags ([`vktPipelineTests.cpp#L133`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L133), [`vktPipelineTests.cpp#L134`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L134)).
- The `timestamp` topic group (registered at [`vktPipelineTests.cpp#L146`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L146)) is implemented in [`vktPipelineTimestampTests.cpp`](../../modules/vulkan/pipeline/vktPipelineTimestampTests.cpp#L1) and documented in [`vktPipelineTimestampTests.md`](../testfiles/pipeline/vktPipelineTimestampTests.md).
- Group names differ from factory symbol names in some cases. For example, `createCmdBindBuffers2Tests()` produces the group `bind_buffers_2`, not `cmd_bind_buffers_2`. All group names in this document are verified against mustpass files.
