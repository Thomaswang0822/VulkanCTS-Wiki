## Overview

**Core question:** Does the `multisample` test family apply the selected multisample pipeline state and related extension behavior so that the rendered samples, resolved results, and attachment observations match the case contract?

[`vktPipelineMultisampleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7256-L8096) is both an implementation file for core multisample mechanisms and a dispatcher for focused sibling implementations. It registers `multisample` and `multisample_with_fragment_shading_rate` for each supported pipeline construction type. The direct intermediate nodes cover rasterization sample count, sample shading, sample mask, alpha operations, depth/stencil interaction, compatible render passes, and varying subpass sample counts. Other direct nodes delegate image access, resolve, sample-location, and extension-specific behavior to dedicated source files.

The mustpass lists cover construction roots independently. For example, `vk-default/pipeline/monolithic/monolithic.txt` contains `dEQP-VK.pipeline.monolithic.multisample...` leaves, while `fast-linked-library.txt`, `pipeline-library.txt`, and shader-object lists contain their corresponding construction-qualified leaves. The source conditions, not a single shared leaf inventory, determine which nodes each root receives.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

### Multisample coverage

A multisampled pixel has several samples. Rasterization produces a coverage mask, and the pipeline sample mask can remove covered samples. Alpha-to-coverage derives coverage from fragment alpha; alpha-to-one changes the alpha value used by later fragment operations. Vulkan specifies the sample-mask test and multisample-coverage order in [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#L693-L1176).

### Per-sample observation

A resolved image combines samples and can conceal per-sample differences. The core tests therefore use control renders or copy samples into separate readable images when they need to observe sample-rate shading or a mask effect. `minSampleShading` specifies the fraction of samples that must receive distinct shading work when sample shading is enabled; its graphics-pipeline state is described in [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2188-L2200).

## Registration Hierarchy

```text
pipeline.monolithic.multisample
├── raster_samples
├── raster_samples_consistency
├── min_sample_shading
├── min_sample_shading_enabled
├── min_sample_shading_disabled
├── sample_mask
├── alpha_to_one
├── alpha_to_coverage
├── alpha_to_coverage_no_color_attachment
├── alpha_to_coverage_unused_attachment
├── sample_rate_a2c
├── sampled_image
├── 3d
├── storage_image
├── standardsampleposition
├── samples_mapping_order
├── shader_fragment_mask
├── resolve
├── multisampled_render_to_single_sampled
├── misc
├── sample_locations_ext
├── std_sample_locations
├── mixed_attachment_samples
├── sample_mask_with_depth_test
├── m10_resolve
├── conservative_with_full_coverage
├── compatible_render_pass
├── variable_rate
├── mixed_count
├── z_export
└── a2c_with_a2one
```

`pipeline.monolithic.multisample` is the concrete canonical root used above. The same implementation also creates `multisample_with_fragment_shading_rate` when its `useFragmentShadingRate` argument is true. The root's direct children are intermediate nodes, not separate test families.

The source omits some intermediate nodes by build or runtime configuration. Non-VulkanSC-only nodes include the image, resolve, sample-location, mixed-attachment, and several extension paths. The image-access and some extension nodes are absent with fragment shading rate. `samples_mapping_order`, `multisampled_render_to_single_sampled`, `misc`, `std_sample_locations`, and `m10_resolve` have additional construction-type restrictions. The registration code records these decisions in [`createMultisampleTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7685-L8096).

## Parameter Dimensions and Observed Values

| Dimension | Values used by the direct implementation | What it changes |
|---|---|---|
| Rasterization samples | `VK_SAMPLE_COUNT_1_BIT` through `VK_SAMPLE_COUNT_64_BIT`, with many core matrices using 2 through 64 | Sample count, attachment setup, and sample-mask word size |
| Sample shading | `sampleShadingEnable`; `minSampleShading` 0.0, 0.25, 0.5, 0.75, 1.0 | Required per-sample shading fraction |
| Sample mask | all on, all off, one, and random masks | Which covered samples remain active |
| Alpha state | alpha-to-coverage and alpha-to-one enabled or disabled; static and selected dynamic paths | Coverage from alpha or forced alpha value |
| Geometry | triangle, line, point, opaque/translucent/invisible quad | Coverage shape and observable color/depth result |
| Image backing | regular and, outside Vulkan SC, sparse | Image allocation and sparse-residency coverage |
| Pipeline construction | monolithic, libraries, and shader-object variants | Registered construction path and availability of selected nodes |
| Fragment shading rate mode | `multisample` or `multisample_with_fragment_shading_rate` | Whether supported cases receive `useFragmentShadingRate=true` |

The implementation checks feature support before execution. This includes `sampleRateShading`, `alphaToOne`, sample-count/image support, sparse-residency support for sparse cases, and extension or construction-type requirements in the relevant paths.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node below `pipeline.<construction>.multisample`. Each subsection below corresponds to one value on that axis. Sample count and the other table dimensions refine the selected behavior.

### `raster_samples`: rasterization sample count

Draws triangle, line, point, depth, and stencil cases with sample counts from 2 through 64. The validator requires enough unique resolved colors and fuzzy-compares the rendered primitive with a software reference.

### `raster_samples_consistency`: sample-count monotonicity

Renders the same narrow triangle at each supported multisample count and requires the number of unique resolved colors not to decrease as the count increases.

### `min_sample_shading`: minimum sample shading

Enables sample shading at several `minSampleShading` values, copies individual samples, and requires enough distinct per-sample colors for covered pixels.

### `min_sample_shading_enabled`: enabled-state coverage

Exercises the enabled sample-shading state across the registered sample-count, geometry, and backing combinations.

### `min_sample_shading_disabled`: disabled-state equivalence

Disables sample shading, averages the copied sample values, and requires the average color to match the no-sample-shading control.

### `sample_mask`: pipeline sample mask

Compares a configured mask with all-zero and all-one controls and requires its unique-color count to remain within the two control counts.

### `alpha_to_one`: forced alpha

Compares enabled and disabled renders, requiring every enabled-result alpha to equal 1.0 and every enabled-result component to be no smaller than its control value.

### `alpha_to_coverage`: alpha-derived coverage

Checks geometry-dependent resolved-color bounds and, for depth variants, redraws while retaining depth to verify the depth result indirectly.

### `alpha_to_coverage_no_color_attachment`: coverage without color output

Runs alpha-to-coverage with a depth/stencil-only render target and requires the rendered result to remain full red, so a clear-color result fails.

### `alpha_to_coverage_unused_attachment`: unused color attachment

Exercises alpha-to-coverage when a color attachment exists but its attachment reference is unused.

### `sample_rate_a2c`: sample-rate shading with alpha-to-coverage

Combines sample-rate shading with alpha-to-coverage and checks their interaction in the direct implementation.

### `sampled_image`: delegated sampled-image behavior

Dispatches to the focused sampled multisample image implementation; that source owns its resource setup and oracle.

### `3d`: delegated 3D image behavior

Dispatches to the focused multisample 3D image implementation.

### `storage_image`: delegated storage-image behavior

Dispatches to the focused multisample storage-image implementation.

### `standardsampleposition`: delegated standard sample positions

Dispatches to the focused standard-sample-position implementation.

### `samples_mapping_order`: delegated sample mapping order

Dispatches to the focused sample-mapping-order implementation for supported construction types.

### `shader_fragment_mask`: delegated fragment-mask behavior

Dispatches to the focused fragment-mask implementation.

### `resolve`: delegated resolve behavior

Dispatches to the focused multisample resolve implementation.

### `multisampled_render_to_single_sampled`: delegated render-to-single-sampled behavior

Dispatches to the focused render-to-single-sampled implementation for supported construction types.

### `misc`: delegated miscellaneous behavior

Dispatches miscellaneous extension cases to their focused implementation for supported construction types.

### `sample_locations_ext`: delegated programmable sample locations

Dispatches to the focused sample-locations implementation.

### `std_sample_locations`: delegated standard sample locations

Dispatches to the focused standard-sample-locations implementation for supported construction types.

### `mixed_attachment_samples`: delegated mixed attachment samples

Dispatches to the focused mixed-attachment-samples implementation.

### `sample_mask_with_depth_test`: sample mask around depth testing

Uses `gl_SampleMaskIn` with early fragment tests, with and without post-depth coverage, to check which coverage mask is visible to the fragment shader.

### `m10_resolve`: delegated maintenance10 resolve behavior

Dispatches to the focused maintenance10 resolve implementation for supported construction types.

### `conservative_with_full_coverage`: conservative rasterization coverage

Combines conservative rasterization with full-coverage multisample state and checks the registered mode combinations.

### `compatible_render_pass`: compatible render-pass state

Exercises pipelines against compatible render-pass state in the static and supported dynamic paths.

### `variable_rate`: varying subpass sample counts

Forms two- and three-subpass sample-count combinations, rejects combinations that do not vary, and includes selected non-empty-framebuffer and unused-attachment cases.

### `mixed_count`: empty-subpass and framebuffer sample counts

Uses different sample counts for an empty subpass and its framebuffer, with both absent and unused attachment references.

### `z_export`: fragment depth, stencil, and sample-mask export

Combines alpha-to-coverage with fragment-shader depth, stencil, or sample-mask writes across supported static, dynamic, and dynamic-rendering paths.

### `a2c_with_a2one`: alpha-to-coverage with alpha-to-one

Combines static or dynamic alpha-to-coverage and alpha-to-one with optional fragment-depth export and sample-rate shading.

## Shader Analysis

The direct mechanisms depend on CTS shader programs, but this mixed implementation/dispatcher page has no single representative shader that explains all registered behaviors. The key observables come from fixed-function multisample state and host comparison. Shader walkthroughs belong with narrower delegated pages when a shader's image access or extension behavior is the property under test.

## Runtime Execution and Result Checking

1. The case chooses a construction type, sample count, geometry, backing mode, and `VkPipelineMultisampleStateCreateInfo` values. The dispatcher constructs intermediate nodes and leaves from these dimensions.
2. A direct core case creates a `MultisampleRenderer` with color targets and, when needed, depth/stencil targets. The renderer performs a draw and either resolves the color target or copies each sample to an individual image.
3. The case waits for the renderer's result before host validation. Raster-sample cases count unique colors and fuzzy-compare the primitive against the reference renderer. `RasterizationSamplesInstance` implements that flow in [`vktPipelineMultisampleTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2459-L2541).
4. Sample-shading cases render a no-sample-shading control, render the test configuration with sample copies, and examine each covered pixel. The enabled check requires enough unique per-sample colors; the disabled check requires the per-sample average to equal the control. See [`MinSampleShadingInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2548-L2744).
5. Sample-mask cases render the configured mask plus all-off and all-on controls. The configured result passes when its unique-color count lies within the control bounds, as implemented by [`SampleMaskInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2749-L2816).
6. Alpha-to-one compares enabled and disabled renders pixel by pixel. Alpha-to-coverage compares the resolved image against geometry-dependent bounds and can redraw with preserved depth to check depth behavior. See [`AlphaToOneInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2916-L3000) and [`AlphaToCoverageInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L3003-L3115).
7. Delegated nodes run their own specialized resource setup and validation after registration. A failure in one of those nodes identifies the named delegated mechanism, rather than the core renderer alone.

## Failure Meaning

### Failure Cause Mapping

| If this behavior fails | The observed result points to | The test can localize |
|---|---|---|
| Raster sample, sample-mask, alpha, or sample-shading nodes | Incorrect fixed-function multisample state or fragment-operation ordering | The selected mechanism and its control/reference images |
| Depth, stencil, resolve, compatible-render-pass, or mixed-count nodes | Attachment sample-count handling, attachment state, resolve, or subpass interaction | The registered node, but not necessarily one API stage |
| Delegated image or extension nodes | The delegated implementation's image access or extension-specific behavior | The named delegated test family and its own documentation/source |

### Cause Analysis

#### Core multisample state or fragment-operation failure

**Possible failure symptoms:** A primitive has too few distinct colors or the wrong shape; a configured sample mask falls outside its all-off/all-on control bounds; per-sample colors do not meet the requested `minSampleShading`; alpha-to-one fails to produce alpha 1.0; or alpha-to-coverage misses its color or depth expectation.

**Possible implementation causes:** The implementation may apply `rasterizationSamples`, `pSampleMask`, sample shading, alpha-to-coverage, or alpha-to-one at the wrong stage, or fail to preserve the requested coverage through later fragment operations. Vulkan's fragment-operation and pipeline-state rules provide the contract; source-level investigation is needed to isolate a failing driver stage.

#### Attachment, resolve, or render-pass interaction failure

**Possible failure symptoms:** A depth/stencil check fails after a redraw, a resolved image disagrees with its reference, compatible render-pass output differs between static and dynamic paths, or varying sample-count subpasses produce an unexpected image.

**Possible implementation causes:** The failure can involve attachment sample-count compatibility, render-pass or dynamic-rendering state, depth/stencil preservation, resolve processing, or a subpass transition. The final image generally cannot identify one exclusive operation, so the registered intermediate node supplies the reliable localization boundary.

#### Delegated image or extension failure

**Possible failure symptoms:** An image-access, sample-location, fragment-mask, render-to-single-sampled, mixed-attachment, or maintenance resolve leaf fails its own comparison.

**Possible implementation causes:** The core source only selects and registers these paths. Inspect the delegated implementation and its case-specific resource and comparison code before attributing the fault to image sampling, storage access, extension state, or resolve behavior.

## Case Pruning

### Requirement-based pruning

The code excludes cases when their required feature, extension, sample count, image usage, or sparse multisample support is unavailable. Vulkan SC removes non-SC registrations. Fragment-shading-rate, sample-location, mixed-attachment, conservative-rasterization, fragment-mask, and render-to-single-sampled paths retain their specific feature gates.

### Design-based pruning

The dispatcher does not repeat every mechanism with fragment shading rate. It restricts several delegated nodes to construction types that support their required setup. Variable-rate generation discards sample-count combinations with no variation, and non-empty-framebuffer variants limit the combination size to keep the matrix bounded.

## Key Takeaways

- `multisample` is a mixed core implementation and dispatcher whose intermediate nodes are the primary behavioral axis.
- Direct core nodes make multisample behavior observable with resolved-image references, control renders, separate sample copies, and depth/stencil checks.
- The family covers both `multisample` and `multisample_with_fragment_shading_rate`, but source conditions intentionally omit unsupported or redundant paths.
- A delegated-node failure localizes to its named mechanism; detailed diagnosis requires that implementation's source and validator.

## Source Reference Appendix

- Registration and construction conditions: [`createMultisampleTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L7256-L8096).
- Core renderer result checks: [`RasterizationSamplesInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2459-L2541), [`MinSampleShadingInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2548-L2744), [`SampleMaskInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2749-L2816), [`AlphaToOneInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L2916-L3000), and [`AlphaToCoverageInstance`](../../../modules/vulkan/pipeline/vktPipelineMultisampleTests.cpp#L3003-L3115).
- Vulkan state and fragment-operation contracts: [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2188-L2200) and [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#L693-L1176).
- Mustpass provenance: [`monolithic/monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt), [`fast-linked-library.txt`](../../../mustpass/main/vk-default/pipeline/fast-linked-library.txt), [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt), and the shader-object mustpass lists under [`mustpass/main/vk-default/pipeline`](../../../mustpass/main/vk-default/pipeline/).
