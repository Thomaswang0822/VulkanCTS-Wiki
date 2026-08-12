# Understanding Brief: WSI color-space tests

## One-Sentence Test Purpose

This test checks whether Vulkan WSI implementations can enumerate and use surface color spaces, render to swapchain images with those choices, apply HDR metadata when supported, and preserve the rendered pixel values across color-space selections.

## Background Knowledge

### Surface formats pair a pixel format with a color space

`vkGetPhysicalDeviceSurfaceFormatsKHR` returns `VkSurfaceFormatKHR` entries. Each entry pairs a `VkFormat` with a `VkColorSpaceKHR`. The format describes how the image stores components; the color space describes how presentation should interpret those components. `VK_EXT_swapchain_colorspace` adds non-`VK_COLOR_SPACE_SRGB_NONLINEAR_KHR` choices, but an application must enable the extension before using extension-provided choices in a swapchain. The Vulkan surface specification describes this query and swapchain relationship in [VK_KHR_surface/wsi.adoc](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc).

Why it matters here:
- The `extensions` case looks for at least one reported color space other than `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR`.
- The rendering cases pass each reported `VkSurfaceFormatKHR` to swapchain creation.
- The comparison cases group the queried entries by one `VkFormat` and compare an image produced with each supported color space.

### Presentation color space is not a shader conversion

The representative renderer writes the same clear color and triangle output for every swapchain. The test changes `VkSwapchainCreateInfoKHR::imageColorSpace`, not the GLSL output. The comparison therefore asks whether the raw values read from the swapchain image remain equal when the presentation color-space field changes. It does not test how a window-system compositor displays the result.

## One Concrete Example

For `dEQP-VK.wsi.headless.colorspace_compare.b8g8r8a8_unorm`, the host selects `VK_FORMAT_B8G8R8A8_UNORM`, collects every queried color space for that format, and requires at least two. It creates one swapchain per color space, records the same triangle, presents it, copies the selected swapchain image to a host-visible buffer, and reads pixel `(128, 128)`. The first value becomes the reference; every later value must compare equal to it.

The shared renderer uses a vertex buffer containing three positions and a fragment shader that writes `vec4(1.0, 0.0, 1.0, 1.0)`. The vertex shader rotates the triangle using the `frameNdx` push constant, so the 60-frame stress path changes the triangle transform while keeping the rendering setup common across color spaces.

## End-to-End Test Flow

```text
[host] create a WSI instance, surface, device, queue, and native window/display
[host] query VkSurfaceFormatKHR entries and select the requested format/color space
[host] generate the shared tri-vert and tri-frag program artifacts
[host] create a swapchain with VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT and VK_IMAGE_USAGE_TRANSFER_SRC_BIT
[host] acquire a swapchain image
[device] render the common triangle into the acquired image
[host] submit rendering and present the image
[host] for comparison cases, copy the image to a host-visible buffer and read pixel (128, 128)
[host] compare against the first color-space result or record a successful no-error rendering run
```

The `basic` and `hdr` cases repeat acquisition, rendering, and presentation for 60 frames per queried surface format. The comparison case performs one rendered frame for each supported color space of its selected format.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `WsiTriangleRenderer::getPrograms` emits the `tri-vert` vertex shader and `tri-frag` fragment shader. The source is in [vkWsiUtil.cpp#L1171-L1194](../../../framework/vulkan/vkWsiUtil.cpp#L1171-L1194).
- The source collection supplies those programs through `addFunctionCaseWithPrograms` for `basic`, `hdr`, and each comparison-format test. The registrations are in [vktWsiColorSpaceTests.cpp#L755-L779](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L755-L779).
- The graphics pipeline has one color attachment, a vertex-stage push-constant range containing one `uint32_t`, and no descriptor sets. The pipeline-layout setup is in [vkWsiUtil.cpp#L848-L865](../../../framework/vulkan/vkWsiUtil.cpp#L848-L865).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Swapchain images | yes, by swapchain creation | yes, as color attachments | written by the render pass | comparison cases copy one image back | Their format is fixed by `VkSurfaceFormatKHR`; their color-space selection is supplied through swapchain creation. |
| Vertex buffer | yes | yes, vertex binding 0 | read by the vertex shader | no | Contains three positions used for the common triangle. |
| Vertex push constant | yes, per frame | yes, pipeline layout | read by the vertex shader | no | Carries `frameNdx`, which changes the triangle rotation. |
| Host-visible result buffer | comparison cases only | transfer destination | written by `copyImageToBuffer` | yes | Holds the copied swapchain image used to read pixel `(128, 128)`. |
| Render pass color attachment | yes, as pipeline state | yes | cleared and written | no | Uses the selected swapchain format and transitions the image for rendering and presentation. |

The color value is generated by the fragment shader and the render-pass clear value. `VK_EXT_hdr_metadata` adds a `VkHdrMetadataEXT` structure to the presentation path; it does not add a shader resource.

## What Is Checked

- `extensions` requires `VK_EXT_swapchain_colorspace` and searches the queried surface formats for a color space other than `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR`.
- `basic` creates and renders with every queried `VkSurfaceFormatKHR` and returns pass if the 60-frame sequence completes without a Vulkan error.
- `hdr` follows the same 60-frame sequence and calls `setHdrMetadataEXT` with the source-defined metadata values before each frame submission.
- Each `colorspace_compare` case requires at least two color spaces for its selected format. It compares the `tcu::Vec4` returned by `getPixel` for each swapchain, using exact equality.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family, with `format` as the secondary comparison axis
>
> **Candidate values:** `extensions`, `basic`, `hdr`, `b8g8r8a8_unorm`, `r8g8b8a8_unorm`, `r8g8b8a8_srgb`, `r5g6b5_unorm_pack16`, `a2b10g10r10_unorm_pack32`, `r16g16b16a16_sfloat`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `extensions` | Missing `VK_EXT_swapchain_colorspace` support or no reported non-`VK_COLOR_SPACE_SRGB_NONLINEAR_KHR` surface format. |
| `basic` | Failure to create, acquire, render, submit, or present a swapchain for one queried surface format and color space. |
| `hdr` | The basic WSI rendering path fails, or `VK_EXT_hdr_metadata` is unavailable or rejects the metadata call. |
| `b8g8r8a8_unorm`, `r8g8b8a8_unorm`, `r8g8b8a8_srgb`, `r5g6b5_unorm_pack16`, `a2b10g10r10_unorm_pack32`, `r16g16b16a16_sfloat` | The selected format cannot expose two usable color spaces, or the exact pixel readback differs between color-space swapchains. |

## Important Variations and Special Cases

- The per-platform `colorspace` and `colorspace_compare` groups repeat under the WSI platform types registered by `vktWsiTests.cpp`. The brief uses `headless` as the representative path.
- The comparison format list is fixed in source. It is not an exhaustive query over every Vulkan format.
- A format with fewer than two supported color spaces is reported as not supported rather than compared.
- `VK_EXT_hdr_metadata` is enabled when advertised by the device, while the `hdr` test checks it again before the metadata call.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Extension instance setup | [createInstanceWithWsi](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L96-L125) | Enables `VK_EXT_swapchain_colorspace` when advertised. |
| Device extension setup | [createDeviceWithWsi](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L135-L165) | Requires `VK_KHR_swapchain` and optionally enables `VK_EXT_hdr_metadata`. |
| Swapchain parameters | [getBasicSwapchainParameters](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L250-L307) | Places the selected `VkColorSpaceKHR` in `VkSwapchainCreateInfoKHR`. |
| Pixel readback | [getPixel](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L346-L383) | Copies a presentable image and reads `(128, 128)`. |
| Color-space comparison | [colorspaceCompareTest](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L425-L563) | Defines the per-format comparison flow and exact pass/fail check. |
| HDR rendering | [surfaceFormatRenderTest](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L565-L693) | Adds the HDR metadata call to the common rendering loop. |
| Shader and pipeline | [WsiTriangleRenderer::getPrograms](../../../framework/vulkan/vkWsiUtil.cpp#L1171-L1194) | Provides the representative generated GLSL. |

## Questions / Risk Points for User Audit

- Does the distinction between presentation color-space metadata and shader color conversion remain clear?
- Should the final page show both generated shader stages or only the vertex stage that varies with `frameNdx`?
- Is exact pixel equality described narrowly enough to avoid implying compositor-output validation?
- Are the platform repetition and the fixed comparison-format list explained without turning them into separate test families?

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` short and use the surface-format/color-space distinction as the prerequisite.
- Carry the registered families and six exact format leaves into `## Behavior Parameters`.
- Use the common triangle renderer as one representative shader walkthrough. Show both stages because the fragment stage supplies the fixed output, but generate SPIR-V for the vertex stage because it contains the changing `frameNdx` logic.
- Copy the failure mapping table into the final page, then write `### Cause Analysis` separately from the source checks and Vulkan surface semantics.
- Keep implementation and framework source links in the final appendix rather than using them as the main narrative.
