## Overview

The `pipeline` test category collects tests that check graphics and compute pipeline creation, state selection, shader interfaces, resources, and result validation across Vulkan pipeline-construction models.

## Background Knowledge

- **Pipeline construction type.** This is a CTS parameter that reruns applicable test-family behavior through different Vulkan construction models. A **monolithic** graphics pipeline puts the shader stages and fixed-function state into one pipeline object. A **graphics pipeline library** divides that state among library subsets and links them into an executable pipeline; the `pipeline_library` route requests link-time optimization, while `fast_linked_library` omits it. A **shader-object** route binds independently created shader objects and dynamic state instead of a graphics pipeline; its `linked` variants create the shader stages with link-stage intent, and its `spirv` versus `binary` variants select the shader object's code source. These routes change how equivalent behavior is assembled and bound, while each test family defines the behavior being checked.

## Category Structure

```text
pipeline
├── monolithic
├── pipeline_library
├── fast_linked_library
├── shader_object_unlinked_spirv
├── shader_object_unlinked_binary
├── shader_object_linked_spirv
├── shader_object_linked_binary
└── no_queues
```

The seven construction-type roots are assembled by [`createTests()`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L224). `no_queues` is an independent root rather than a construction-type variant. The dispatcher applies construction-type predicates, so a test family need not appear under every root.

## How the Families Fit Together

- Fixed-function and vertex-input families vary the state that turns vertices and fragment outputs into attachment results.
- Descriptor, constant, and interface families vary how pipeline stages receive data and agree on their inputs and outputs.
- Image, sampler, attachment, and multisample families vary resource views, sampling, rendering state, and reference-image checks.
- Cache, binary, library, derivative, and lifetime families exercise the pipeline-object lifecycle rather than one draw-state mechanism.
- Dynamic-state, extension, bind-point, and queue-free families cover command-time state replacement and specialized API contracts.

## Level-3 Pages Navigation

### Fixed-function state and vertex input

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `stencil` | [Stencil.md](../testfiles/pipeline/Stencil.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for stencil. |
| `blend` | [Blend.md](../testfiles/pipeline/Blend.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for blend. |
| `dual-source blend` | [DualBlend.md](../testfiles/pipeline/DualBlend.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for dual-source blend. |
| `depth` | [Depth.md](../testfiles/pipeline/Depth.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for depth. |
| `logic operations` | [LogicOp.md](../testfiles/pipeline/LogicOp.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for logic operations. |
| `input assembly` | [InputAssembly.md](../testfiles/pipeline/InputAssembly.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for input assembly. |
| `vertex input` | [VertexInput.md](../testfiles/pipeline/VertexInput.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for vertex input. |
| `sRGB vertex input` | [VertexInputSRGB.md](../testfiles/pipeline/VertexInputSRGB.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for sRGB vertex input. |
| `legacy vertex attributes` | [LegacyAttr.md](../testfiles/pipeline/LegacyAttr.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for legacy vertex attributes. |
| `dynamic vertex attributes` | [DynamicVertexAttribute.md](../testfiles/pipeline/DynamicVertexAttribute.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for dynamic vertex attributes. |
| `input attribute offsets` | [InputAttributeOffset.md](../testfiles/pipeline/InputAttributeOffset.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for input attribute offsets. |
| `color write enable` | [ColorWriteEnable.md](../testfiles/pipeline/ColorWriteEnable.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for color write enable. |
| `primitive restart index` | [PrimitiveRestartIndex.md](../testfiles/pipeline/PrimitiveRestartIndex.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for custom primitive restart indices. |

### Descriptors, constants, and shader interfaces

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `descriptor limits` | [DescriptorLimits.md](../testfiles/pipeline/DescriptorLimits.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for descriptor limits. |
| `dynamic descriptor offsets` | [DynamicOffset.md](../testfiles/pipeline/DynamicOffset.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for dynamic descriptor offsets. |
| `push constants` | [PushConstant.md](../testfiles/pipeline/PushConstant.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for push constants. |
| `push descriptors` | [PushDescriptor.md](../testfiles/pipeline/PushDescriptor.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for push descriptors. |
| `specialization constants` | [SpecConstant.md](../testfiles/pipeline/SpecConstant.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for specialization constants. |
| `shader interface matching` | [InterfaceMatching.md](../testfiles/pipeline/InterfaceMatching.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for shader interface matching. |
| `component-decorated interface layout matching` | [ShaderComponentDecoratedLayoutMatching.md](../testfiles/pipeline/ShaderComponentDecoratedLayoutMatching.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for component-decorated interface layout matching. |
| `maximum varyings` | [MaxVaryings.md](../testfiles/pipeline/MaxVaryings.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for maximum varyings. |

### Images, sampling, and attachment behavior

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `image` | [Image.md](../testfiles/pipeline/Image.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for image. |
| `image views` | [ImageView.md](../testfiles/pipeline/ImageView.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for image views. |
| `2D views of 3D images` | [Image2DViewOf3D.md](../testfiles/pipeline/Image2DViewOf3D.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for 2D views of 3D images. |
| `sliced 3D-image views` | [ImageSlicedViewOf3D.md](../testfiles/pipeline/ImageSlicedViewOf3D.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for sliced 3D-image views. |
| `sampler` | [Sampler.md](../testfiles/pipeline/Sampler.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for sampler. |
| `render to image` | [RenderToImage.md](../testfiles/pipeline/RenderToImage.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for render to image. |
| `framebuffer attachments` | [FramebufferAttachment.md](../testfiles/pipeline/FramebufferAttachment.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for framebuffer attachments. |
| `matched attachments` | [MatchedAttachments.md](../testfiles/pipeline/MatchedAttachments.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for matched attachments. |
| `attachment feedback-loop layout` | [AttachmentFeedbackLoopLayout.md](../testfiles/pipeline/AttachmentFeedbackLoopLayout.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for attachment feedback-loop layout. |

### Multisample behavior

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `multisample state` | [Multisample.md](../testfiles/pipeline/Multisample.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for multisample state. |
| `multisample interpolation` | [MultisampleInterpolation.md](../testfiles/pipeline/MultisampleInterpolation.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for multisample interpolation. |
| `multisample shader built-ins` | [MultisampleShaderBuiltIn.md](../testfiles/pipeline/MultisampleShaderBuiltIn.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for multisample shader built-ins. |
| `multisample images` | [MultisampleImage.md](../testfiles/pipeline/MultisampleImage.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for multisample images. |
| `mixed attachment samples` | [MultisampleMixedAttachmentSamples.md](../testfiles/pipeline/MultisampleMixedAttachmentSamples.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for mixed attachment samples. |
| `multisampled render-to-single-sampled` | [MultisampledRenderToSingleSampled.md](../testfiles/pipeline/MultisampledRenderToSingleSampled.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for multisampled render-to-single-sampled. |
| `maintenance10 resolve` | [MultisampleResolveMaint10.md](../testfiles/pipeline/MultisampleResolveMaint10.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for maintenance10 resolve. |
| `multisample resolve render area` | [MultisampleResolveRenderArea.md](../testfiles/pipeline/MultisampleResolveRenderArea.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for multisample resolve render area. |
| `sample locations extension` | [MultisampleSampleLocationsExt.md](../testfiles/pipeline/MultisampleSampleLocationsExt.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for sample locations extension. |
| `shader fragment mask` | [MultisampleShaderFragmentMask.md](../testfiles/pipeline/MultisampleShaderFragmentMask.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for shader fragment mask. |

### Construction, cache, and lifetime behavior

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `cache` | [Cache.md](../testfiles/pipeline/Cache.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for cache. |
| `binary` | [Binary.md](../testfiles/pipeline/Binary.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for binary. |
| `creation feedback` | [CreationFeedback.md](../testfiles/pipeline/CreationFeedback.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for creation feedback. |
| `creation cache control` | [CreationCacheControl.md](../testfiles/pipeline/CreationCacheControl.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for creation cache control. |
| `executable properties` | [ExecutableProperties.md](../testfiles/pipeline/ExecutableProperties.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for executable properties. |
| `derivative` | [Derivative.md](../testfiles/pipeline/Derivative.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for derivative. |
| `library` | [Library.md](../testfiles/pipeline/Library.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for library. |
| `shader module identifiers` | [ShaderModuleIdentifier.md](../testfiles/pipeline/ShaderModuleIdentifier.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for shader module identifiers. |
| `robustness cache` | [RobustnessCache.md](../testfiles/pipeline/RobustnessCache.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for robustness cache. |
| `timestamp` | [Timestamp.md](../testfiles/pipeline/Timestamp.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for timestamp. |
| `early destruction` | [EarlyDestroy.md](../testfiles/pipeline/EarlyDestroy.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for early destruction. |

### Dynamic state and extension families

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `extended dynamic state` | [ExtendedDynamicState.md](../testfiles/pipeline/ExtendedDynamicState.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for extended dynamic state. |
| `extended dynamic state misc` | [ExtendedDynamicStateMisc.md](../testfiles/pipeline/ExtendedDynamicStateMisc.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for extended dynamic state misc. |
| `dynamic tessellation control points` | [DynamicControlPoints.md](../testfiles/pipeline/DynamicControlPoints.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for dynamic tessellation control points. |
| `advanced blend operations` | [BlendOperationAdvanced.md](../testfiles/pipeline/BlendOperationAdvanced.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for advanced blend operations. |
| `unrestricted depth range` | [DepthRangeUnrestricted.md](../testfiles/pipeline/DepthRangeUnrestricted.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for unrestricted depth range. |
| `shader stencil export` | [StencilExport.md](../testfiles/pipeline/StencilExport.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for shader stencil export. |

### Binding and independent-root behavior

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `bind points` | [BindPoint.md](../testfiles/pipeline/BindPoint.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for bind points. |
| `vertex-buffer binding 2` | [BindVertexBuffers2.md](../testfiles/pipeline/BindVertexBuffers2.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for vertex-buffer binding 2. |
| `no position output` | [NoPosition.md](../testfiles/pipeline/NoPosition.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for no position output. |
| `empty fragment stage` | [EmptyFS.md](../testfiles/pipeline/EmptyFS.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for empty fragment stage. |
| `miscellaneous pipeline behavior` | [Misc.md](../testfiles/pipeline/Misc.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for miscellaneous pipeline behavior. |
| `queue-free device creation` | [NoQueues.md](../testfiles/pipeline/NoQueues.md) | Test intent, behavioral axis, execution, validation, pruning, and failure meaning for queue-free device creation. |

## Category Notes

- [`vktPipelineTests.cpp`](../../modules/vulkan/pipeline/vktPipelineTests.cpp#L95-L220) is the registration-only category dispatcher. Its direct roots and construction-type predicates are represented here rather than as a standalone Level-3 page. The dispatcher adds `primitive_restart_index` to monolithic, graphics-pipeline-library, fast-linked-library, and unlinked-SPIR-V shader-object roots; the source excludes it for linked/binary shader-object variants.
- The category uses multiple mustpass files beneath [`mustpass/main/vk-default/pipeline`](../../mustpass/main/vk-default/pipeline/). Each Level-3 page records the construction roots relevant to its own test family.
