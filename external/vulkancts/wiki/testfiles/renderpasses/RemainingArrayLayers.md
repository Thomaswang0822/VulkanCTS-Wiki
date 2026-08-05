## Overview

**Core question:** When a 3D image is viewed as a 2D array with `subresourceRange.layerCount` set to `VK_REMAINING_ARRAY_LAYERS`, does the implementation attach and render to the correct set of layers across single-layer and multi-layer framebuffers?

- This page covers the `remaining_array_layers` test family implemented in [vktRenderPassRemainingArrayLayersTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp) and registered under the `renderpass1` and `renderpass2` roots of the `renderpasses` test category.
- The family is registered only for legacy render pass and render pass 2; the dispatcher excludes it from dynamic rendering at [vktRenderPassTests.cpp#L8596-L8598](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596-L8598).
- Each test creates a 3D image with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT`, builds a `VK_IMAGE_VIEW_TYPE_2D_ARRAY` view whose `layerCount` is `VK_REMAINING_ARRAY_LAYERS` starting at a nonzero `baseArrayLayer`, and renders white into a framebuffer built from that view.
- Three framebuffer variants change how many layers the framebuffer exposes and how the draw reaches them: a single-layer framebuffer, a multi-layer framebuffer drawn once, and a multi-layer framebuffer drawn once per layer through a geometry shader that writes `gl_Layer`.
- Passing requires every checked pixel to be `(1.0, 1.0, 1.0, 1.0)` across all drawn layers.

## Background Knowledge

- **`VK_REMAINING_ARRAY_LAYERS`.** This sentinel, used in `VkImageViewSubresourceRange::layerCount`, means the view includes every array layer of the image from `baseArrayLayer` onward. The implementation must resolve it to the actual remaining layer count at view creation time. See [resources.adoc#L5708-L5712](../../../../vulkan-docs/src/chapters/resources.adoc#L5708-L5712).
- **`VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT`.** A 3D image created with this flag can be viewed as `VK_IMAGE_VIEW_TYPE_2D` or `VK_IMAGE_VIEW_TYPE_2D_ARRAY`. Each slice of the 3D image's depth dimension maps to one array layer of the 2D-array view. See [resources.adoc#L4160-L4162](../../../../vulkan-docs/src/chapters/resources.adoc#L4160-L4162).
- **Framebuffer layer count versus draw layer routing.** A framebuffer attachment carries its own layer count, taken here from the image view. A draw can reach those layers in two ways: by default, all instances land on framebuffer layer 0; or, when a geometry shader writes `gl_Layer`, each invocation can direct its primitives to a chosen framebuffer layer. This distinction is what the three framebuffer variants exercise.

## Registration Hierarchy

```text
renderpasses.renderpass1.remaining_array_layers
├── single_layer_fb
├── multi_layer_fb
└── multi_layer_fb_gl_layer
```

The same three intermediate nodes exist under `renderpasses.renderpass2.remaining_array_layers`. Each intermediate node holds the four layer-count test case leaves `1_1`, `2_2`, `4_1`, and `1_4`, registered by [createRenderPassRemainingArrayLayersTests](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L488-L530).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Framebuffer variant | `single_layer_fb`, `multi_layer_fb`, `multi_layer_fb_gl_layer` | Selects the framebuffer layer count and whether a geometry shader routes instances to layers. This is the primary behavioral axis. | [framebufferTests](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L505-L514) |
| Layer counts (leaf) | `1_1`, `2_2`, `4_1`, `1_4` | Each leaf is `{baseLayer, additionalLayers}`. The image depth is `1 + baseLayer + additionalLayers`, and `VK_REMAINING_ARRAY_LAYERS` must expand to `additionalLayers + 1` layers starting at `baseLayer`. | [layerTests](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L493-L503) |
| Rendering type | legacy render pass, render pass 2 | Builds the render pass with the corresponding create-info structures. Dynamic rendering is excluded by the dispatcher. | [dispatcher gate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596-L8598) |

## Behavior Parameters

The primary behavioral axis is the framebuffer variant. Each variant changes both the framebuffer layer count and how the draw reaches those layers. The four layer-count leaves are a secondary axis that varies the numerical configuration of `baseLayer` and the remaining layer count; they do not change the rendering mechanism.

### `single_layer_fb`: one-layer framebuffer baseline

The framebuffer is created with `layers = 1` regardless of how many layers the image view exposes. One draw instance is recorded. With no geometry shader, the draw lands on framebuffer layer 0, which maps to image slice `baseLayer`. This is the baseline: it confirms that a view using `VK_REMAINING_ARRAY_LAYERS` can back a single-layer framebuffer and that the draw hits the correct slice.

### `multi_layer_fb`: multi-layer framebuffer, single draw

The framebuffer layer count is `depth - baseLayer`, matching the full remaining-layer span implied by `VK_REMAINING_ARRAY_LAYERS` starting at `baseLayer`. One draw instance is recorded with no geometry shader, so all fragments land on framebuffer layer 0. The other framebuffer layers are attached but not rendered into. This variant checks that the implementation accepts a multi-layer framebuffer built from a `VK_REMAINING_ARRAY_LAYERS` view without error, even though only one layer is actually drawn.

### `multi_layer_fb_gl_layer`: multi-layer framebuffer, per-layer routing

The framebuffer layer count is again `depth - baseLayer`, but now `instanceCount` equals the framebuffer layer count and a geometry shader writes `gl_Layer = layerIndex`, where `layerIndex` is passed from the vertex shader as `gl_InstanceIndex`. Each draw instance is routed to its own framebuffer layer, so every layer of the remaining span is filled. This variant exercises the full multi-layer path end to end: `VK_REMAINING_ARRAY_LAYERS` view expansion, a matching multi-layer framebuffer, and layer-routed rendering. It requires `DEVICE_CORE_FEATURE_GEOMETRY_SHADER` ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L482-L483)).

## Shader Analysis

The shaders are not the tested behavior. The vertex shader generates a full-coverage triangle from `gl_VertexIndex`, the optional geometry shader forwards `gl_InstanceIndex` to `gl_Layer`, and the fragment shader outputs a constant white. They exist only to fill the rendered layers with a known color so the host can verify which layers received output. No representative walkthrough is needed.

## Runtime Execution and Result Checking

- The host creates a 3D `VK_FORMAT_R8G8B8A8_UNORM` image with extent `{32, 32, depth}` where `depth = 1 + baseLayer + additionalLayers`, `arrayLayers = 1`, and flag `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` ([imageCreateInfo](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L184-L200)).
- A `VK_IMAGE_VIEW_TYPE_2D_ARRAY` view is created with `subresourceRange = {COLOR, baseMipLevel 0, levelCount 1, baseArrayLayer baseLayer, layerCount VK_REMAINING_ARRAY_LAYERS}` ([imageViewCreateInfo](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L205-L215)).
- The render pass has one color attachment cleared on load and stored on `STORE`, in `VK_IMAGE_LAYOUT_GENERAL` ([createRenderPass](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L96-L145)).
- The framebuffer layer count is `1` for `single_layer_fb` and `depth - baseLayer` for the multi-layer variants ([framebufferLayers](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L226)).
- A pipeline barrier transitions the image to `VK_IMAGE_LAYOUT_GENERAL`, the render pass is begun, the pipeline is bound, and `cmdDraw(3, instanceCount)` is recorded where `instanceCount` is `framebufferLayers` when `writeGlLayer` is true and `1` otherwise ([draw](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L327-L356)).
- After the render pass ends, a memory barrier makes the color attachment write visible to transfer, and `vkCmdCopyImageToBuffer` copies `instanceCount` slices starting at depth `baseLayer` into a host-visible buffer ([copyback](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L358-L375)).
- The host invalidates the buffer allocation and scans every pixel of every copied layer. The case passes only if every pixel equals `(1.0, 1.0, 1.0, 1.0)` ([result check](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L385-L405)).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|----------|-----------------------------|---------------|---------------|---------------|------|
| 3D color image | Yes | Image view | Rendered into as color attachment | Yes, via copyback | Backs the `VK_REMAINING_ARRAY_LAYERS` 2D-array view. |
| 2D-array image view | Yes | Framebuffer attachment | Provides the layer span under test | Indirectly | Carries `layerCount = VK_REMAINING_ARRAY_LAYERS`. |
| Render pass and framebuffer | Yes | Command buffer | Defines the attachment and layer count | No | Combines the view with the framebuffer layer count variant. |
| Graphics pipeline | Yes | Pipeline state | Runs the vertex, optional geometry, and fragment shaders | No | Fills rendered layers with white. |
| Color output buffer | Yes | Transfer destination | Receives copied image data | Yes | Host-side pixel source for the final scan. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `single_layer_fb` | Single-layer framebuffer built from a `VK_REMAINING_ARRAY_LAYERS` view did not render to the correct slice. |
| `multi_layer_fb` | Multi-layer framebuffer built from a `VK_REMAINING_ARRAY_LAYERS` view was rejected or the single draw did not land on framebuffer layer 0. |
| `multi_layer_fb_gl_layer` | `gl_Layer` routing did not reach every framebuffer layer, or one or more layers of the remaining span were not filled. |
| Any variant | Shared infrastructure failure: image or view creation, layout transition, copyback, or the pixel scan. |

### Cause Analysis

#### Single-layer framebuffer did not render to the correct slice

**Possible failure symptoms:** For a `single_layer_fb` case, the copied slice at depth `baseLayer` is not uniformly white; at least one pixel differs from `(1.0, 1.0, 1.0, 1.0)`.

**Possible implementation causes:** The view's `baseArrayLayer` was set to `baseLayer` and `layerCount` to `VK_REMAINING_ARRAY_LAYERS`, but the framebuffer exposes only layer 0. If the implementation mis-resolves `VK_REMAINING_ARRAY_LAYERS` or maps the framebuffer's single layer to the wrong slice of the 3D image, the draw writes to a slice other than `baseLayer`. Source-level investigation would be needed to distinguish a view-creation resolution bug from a framebuffer-layer-mapping bug.

#### Multi-layer framebuffer rejected or single draw misrouted

**Possible failure symptoms:** For a `multi_layer_fb` case, framebuffer creation fails, or the single copied slice at depth `baseLayer` is not white.

**Possible implementation causes:** The framebuffer layer count is `depth - baseLayer`, taken from the same `VK_REMAINING_ARRAY_LAYERS` span as the view. If the implementation computes a different remaining-layer count for the view than for the framebuffer, framebuffer creation could fail or expose the wrong layer range. Because no geometry shader is present, the draw defaults to framebuffer layer 0; if that mapping is wrong, the rendered output lands elsewhere and the checked slice stays at the clear value. Source-level investigation would be needed to separate a layer-count resolution mismatch from a layer-routing bug.

#### `gl_Layer` routing did not reach every framebuffer layer

**Possible failure symptoms:** For a `multi_layer_fb_gl_layer` case, one or more of the `framebufferLayers` copied slices are not uniformly white, while others are.

**Possible implementation causes:** Each instance is routed by the geometry shader to `gl_Layer = gl_InstanceIndex`, so all layers from 0 to `framebufferLayers - 1` should be filled. A partial failure points at incorrect `gl_Layer` handling when the framebuffer is backed by a `VK_REMAINING_ARRAY_LAYERS` view of a 3D image, or at instance-to-layer mapping that drops or duplicates a layer. If all layers fail together, a shared cause such as geometry-shader feature gating or framebuffer setup is more likely than per-layer routing.

#### Shared infrastructure failure

**Possible failure symptoms:** Failures appear across all three variants or all four layer-count leaves for a variant, or the copyback reads back the wrong region.

**Possible implementation causes:** The image-to-buffer copy uses `imageOffset.z = baseLayer` and `imageExtent.depth = instanceCount` on the 3D image ([copyRegion](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L362-L374)). A mistake in that region, in the layout transition around the render pass, or in the host pixel scan would corrupt every case using the affected path rather than only one variant.

## Case Pruning

### Requirement-based pruning

- Render pass 2 cases require `VK_KHR_create_renderpass2` ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L475-L476)).
- The `multi_layer_fb_gl_layer` variant requires the `geometryShader` core feature ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L482-L483)).
- The whole family is excluded from dynamic rendering by the dispatcher, so no `RENDERING_TYPE_DYNAMIC_RENDERING` cases are registered ([dispatcher gate](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596-L8598)).

### Design-based pruning

- The four layer-count leaves cover a small set of `baseLayer` and remaining-layer combinations rather than enumerating every possible pair. `1_1` and `2_2` keep the two counts equal; `4_1` sets a high base with one remaining layer; `1_4` sets a low base with several remaining layers ([layerTests](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L493-L503)).
- The framebuffer variants are limited to three: a single-layer baseline, a multi-layer framebuffer drawn once, and a multi-layer framebuffer drawn per layer through `gl_Layer`. Other combinations, such as a single-layer framebuffer with a geometry shader, are not registered.

## Key Takeaways

- The family probes one property: `VK_REMAINING_ARRAY_LAYERS` in a 2D-array view of a 3D image must resolve to the correct remaining-layer span and back a framebuffer whose layer count matches that span.
- The three framebuffer variants separate the concerns: `single_layer_fb` checks basic view-to-framebuffer mapping, `multi_layer_fb` checks that a multi-layer framebuffer is accepted, and `multi_layer_fb_gl_layer` checks that every layer of the remaining span can be rendered to.
- Only `multi_layer_fb_gl_layer` actually fills every layer; the other two variants draw to framebuffer layer 0 and check only that layer.
- The shaders are not under test; they only paint a known color so the host scan can tell which layers received output.
- See `## Failure Meaning` for how a non-white pixel is interpreted depending on which variant produced it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Dispatcher attachment (dynamic-rendering gate) | [vktRenderPassTests.cpp#L8596-L8598](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8596-L8598) | Adds the family only for legacy render pass and render pass 2. |
| Factory function | [vktRenderPassRemainingArrayLayersTests.cpp#L488-L530](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L488-L530) | Builds the three framebuffer groups and the four layer-count leaves under each. |
| Test parameters | [vktRenderPassRemainingArrayLayersTests.cpp#L49-L65](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L49-L65) | Defines `baseLayer`, `additionalLayers`, `multiLayeredFramebuffer`, and `writeGlLayer`. |
| Image and view creation | [vktRenderPassRemainingArrayLayersTests.cpp#L184-L217](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L184-L217) | Creates the 3D image with `VK_IMAGE_CREATE_2D_ARRAY_COMPATIBLE_BIT` and the 2D-array view with `VK_REMAINING_ARRAY_LAYERS`. |
| Render pass creation | [vktRenderPassRemainingArrayLayersTests.cpp#L96-L145](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L96-L145) | Defines the single color attachment and subpass. |
| Runtime execution and draw | [vktRenderPassRemainingArrayLayersTests.cpp#L171-L378](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L171-L378) | Builds the framebuffer, pipeline, records the draw, and copies back. |
| Result check | [vktRenderPassRemainingArrayLayersTests.cpp#L385-L405](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L385-L405) | Scans every pixel of every copied layer for white. |
| Shader generation | [vktRenderPassRemainingArrayLayersTests.cpp#L427-L465](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L427-L465) | Emits the vertex, optional geometry, and fragment shaders. |
| Support checks | [vktRenderPassRemainingArrayLayersTests.cpp#L472-L484](../../../modules/vulkan/renderpass/vktRenderPassRemainingArrayLayersTests.cpp#L472-L484) | Requires render pass 2 extension and geometry shader feature as applicable. |
| Mustpass entries (renderpass1) | [renderpasses.txt#L36309-L36320](../../../mustpass/main/vk-default/renderpasses.txt#L36309-L36320) | 12 leaves under `renderpass1.remaining_array_layers`. |
| Mustpass entries (renderpass2) | [renderpasses.txt#L71602-L71613](../../../mustpass/main/vk-default/renderpasses.txt#L71602-L71613) | 12 leaves under `renderpass2.remaining_array_layers`. |
