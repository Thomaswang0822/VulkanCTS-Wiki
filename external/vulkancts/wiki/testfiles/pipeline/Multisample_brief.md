# Understanding Brief: pipeline multisample

## One-Sentence Test Purpose

This test family checks that graphics pipeline multisample state, related fragment operations, and selected multisample extensions produce the expected resolved color, depth, stencil, or per-sample results.

## Background Knowledge

### Coverage and samples

A rasterized fragment can cover some samples of a multisampled pixel. The pipeline sample mask removes selected covered samples. Alpha-to-coverage derives coverage from fragment alpha, while alpha-to-one changes the alpha value used by later operations. The Vulkan fragment-operations rules define this ordering and the relevant state in [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#L693-L1176).

Why it matters here:

- A resolved image can hide which individual samples were written, so several test cases copy samples separately or compare control renders.
- The same visible mismatch can originate in coverage creation, sample selection, depth or stencil processing, or resolve and readback.

### Sample-rate shading

With sample shading disabled, fragment shading can run once for a pixel and its result can apply to covered samples. With it enabled, the implementation must shade at least the fraction requested by `minSampleShading`. The family uses changing per-sample output to make that distinction observable.

## One Concrete Example

A representative `pipeline.monolithic.multisample.sample_mask.mask_one.samples_4.primitive_triangle` test renders the same triangle three times: with its selected mask, with all mask bits clear, and with all mask bits set. It counts unique colors in each resolved image and accepts the selected-mask count only when it lies between the two controls. This tests coverage restriction without requiring an exact implementation-specific coverage pattern.

## End-to-End Test Flow

```text
[host] choose a pipeline construction type, sample count, geometry, multisample state, and optional feature path
[host] create a render target, graphics pipeline, and a reference or control configuration when the case needs one
[host] submit a draw, resolve the multisample image or copy each sample into readable images
[device] rasterize fragments, apply sample shading, sample mask, alpha-to-coverage, alpha-to-one, and depth/stencil operations
[host] wait for the rendering work, read the result images, and run the case-specific comparison
[host] report pass, fail, or not-supported
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The implementation uses CTS shader programs and fixed-function pipeline state. The dispatcher also delegates image, resolve, sample-location, fragment-mask, mixed-attachment, and render-to-single-sampled paths to focused source files. This page does not document one stable generated shader artifact because the registered family spans many independently implemented mechanisms.

### Bound resources and memory objects

Cases use multisampled color targets and, where needed, depth/stencil attachments. The common renderer resolves a multisampled color target or copies individual samples to single-sampled images for host comparison. Sparse variants use a sparse image backing only when the device advertises the required sparse multisample support.

## What Is Checked

The family checks several observable properties:

- supported rasterization sample counts render the expected primitive shape and enough distinct coverage-derived colors;
- `minSampleShading` produces enough distinct per-sample values, while disabled sample shading averages back to the non-sample-shaded result;
- sample-mask output lies between all-off and all-on controls;
- alpha-to-one produces alpha 1.0 and an image component-wise no smaller than the disabled control;
- alpha-to-coverage, depth/stencil interaction, dynamic state, compatible render passes, varying subpass sample counts, and extension-specific paths meet their individual image or buffer checks.

## Behavior Parameter Identification

The primary behavioral axis is the direct intermediate node below `pipeline.<construction>.multisample`. Each node chooses a distinct multisample mechanism or extension contract, such as `raster_samples`, `sample_mask`, `alpha_to_coverage`, `variable_rate`, or `m10_resolve`. Sample count, geometry, backing mode, construction type, and fragment-shading-rate mode refine that mechanism rather than replace it.

## What Failure Means

### Failure Cause Mapping

| If this behavior fails | The observed result points to | The test can localize |
|---|---|---|
| Raster sample, sample-mask, alpha, or sample-shading nodes | Incorrect fixed-function multisample state or fragment-operation ordering | The selected mechanism and its control/reference images |
| Depth, stencil, resolve, compatible-render-pass, or mixed-count nodes | Attachment sample-count handling, attachment state, resolve, or subpass interaction | The registered node, but not necessarily one API stage |
| Delegated image or extension nodes | The delegated implementation's image access or extension-specific behavior | The named delegated test family and its own documentation/source |

## Important Variations and Special Cases

- `multisample` and `multisample_with_fragment_shading_rate` select whether the dispatcher passes `useFragmentShadingRate` to supported cases.
- Several image-access and extension nodes are absent when fragment shading rate is enabled; some nodes also admit only monolithic, fast-linked-library, or shader-object-unlinked-SPIR-V construction.
- Vulkan SC excludes non-SC registrations, including sparse and several extension paths.
- The core source registers direct mechanisms and delegates focused implementations to sibling source files.

## Source Mapping

- [`createMultisampleTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7256-L8096) creates the direct hierarchy and applies construction-type and fragment-shading-rate conditions.
- [`RasterizationSamplesInstance::verifyImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2465-L2541), [`MinSampleShadingInstance::verifySampleShadedImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2598-L2672), and [`SampleMaskInstance::verifyImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2793-L2816) show representative result checks.
- [`AlphaToOneInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2916-L3000) and [`AlphaToCoverageInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L3003-L3115) show paired-control and depth-check flows.
- Vulkan multisample state and fragment-operation rules: [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2188-L2200) and [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#L693-L1176).

## Questions / Risk Points for User Audit

None. The page treats this source as a mixed implementation and dispatcher: it documents direct mechanisms here and identifies delegated mechanisms without claiming their internal validators.

## Conversion Notes for Final Wiki Rewrite

Carry the behavioral-axis conclusion into `## Behavior Parameters` and copy the failure-cause table unchanged. Keep the final page focused on shared dispatch, representative direct validators, registration conditions, and the boundary between this source and delegated implementations.
