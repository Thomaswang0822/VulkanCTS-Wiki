## Overview

The `imageless_framebuffer` test category checks whether an imageless framebuffer accepts compatible image views at render-pass begin time and produces the expected color, depth, stencil, resolve, and input-attachment results.

## Background Knowledge

- **Imageless framebuffer.** A framebuffer created with `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT` records attachment constraints such as format, usage, and dimensions without binding concrete image views. The render-pass begin structure supplies the views for that render-pass instance. See [imageless framebuffer semantics](../../../vulkan-docs/src/chapters/renderpass.adoc#L6265-L6277).
- **Resolve attachments.** A multisampled attachment stores several samples per pixel. A resolve attachment receives the combined single-sample result when the subpass ends. The resolve families therefore use both multisample and single-sample images.
- **Input attachments.** An input attachment lets a later subpass read an earlier subpass's attachment through a descriptor. The multi-subpass family uses this relationship to test that begin-time attachment binding and subpass reads agree.

## Category Structure

```text
imageless_framebuffer
├── color
├── depth_stencil
├── color_resolve
├── depth_stencil_resolve
├── multisubpass
└── different_attachments
```

The six direct test families are registered by [`createTests()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L3027-L3041). The default Vulkan mustpass contains one test case for each family.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| All six imageless-framebuffer test families | [Tests.md](../testfiles/imageless_framebuffer/Tests.md) | Attachment binding, resolve and subpass variants, host-side checks, support gates, and failure meaning |

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test family | `color`, `depth_stencil`, `color_resolve`, `depth_stencil_resolve`, `multisubpass`, `different_attachments` | Selects the attachment and render-pass scenario. | [`createTests()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2953-L3023) |
| Color format | `VK_FORMAT_R8G8B8A8_UNORM` | Defines the color attachment and host readback format. | [`imagelessColorTests()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2953-L2959) |
| Depth/stencil format | `VK_FORMAT_D24_UNORM_S8_UINT` or `VK_FORMAT_UNDEFINED` | Adds a combined depth/stencil attachment only to the depth/stencil families. | [`imagelessDepthStencilTests()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2965-L2971) |
| Sample count | `1` or `4` | Selects single-sample rendering or multisample resolve behavior. | [`ColorResolveImagelessTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1684-L1694), [`DepthResolveImagelessTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1974-L1984) |
| Render extent | `32 x 32` | Fixes the image and readback dimensions used by all six families. | [`ColorImagelessTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1222-L1235) |

## Behavior Parameters

The primary behavioral axis is the test-family leaf. Each leaf changes the attachment roles or render-pass structure while retaining the same imageless-framebuffer binding contract.

### `color`: one color attachment

The test supplies one color image view at render-pass begin, draws the test geometry, copies the image to a host-visible buffer, and compares the result with the generated color reference.

### `depth_stencil`: color and combined depth/stencil attachments

The test binds color and `VK_FORMAT_D24_UNORM_S8_UINT` depth/stencil views. It validates color, depth, and stencil readback separately after the render pass.

### `color_resolve`: multisampled color and color resolve

The test renders to a four-sample color attachment and resolves it into a single-sample color image. The host checks the resolve image, so this family tests both the imageless description and the resolve attachment relationship.

### `depth_stencil_resolve`: multisampled color/depth/stencil and resolve targets

This family combines four-sample color and depth/stencil attachments with resolve targets, including the `VK_KHR_depth_stencil_resolve` path. It validates the resolved color, depth, and stencil data.

### `multisubpass`: input attachment across two subpasses

The first subpass writes one color image. The second subpass reads its input attachment and writes the resulting color to another attachment. The host copies and verifies both subpass outputs.

### `different_attachments`: one framebuffer reused with two views

The test creates one imageless framebuffer and begins separate render-pass instances with different compatible color image views. It verifies that begin-time view selection changes the image used by each instance without recreating the framebuffer.

## Shader Analysis

The test shaders only provide fixed vertex and fragment rendering for the attachment experiments. No single shader path carries the behavior under test, so this page does not use a representative shader walkthrough. The attachment binding and render-pass structures, rather than shader transformation, determine the tested behavior.

## Runtime Execution and Result Checking

- Each instance creates images, image views, buffers, a render pass, an imageless framebuffer, a graphics pipeline, and a command buffer. The framebuffer stores attachment constraints and uses `VkRenderPassAttachmentBeginInfo` to receive the concrete views at begin time.
- The draw paths clear the attachments, bind the fixed pipeline and vertex data, draw the test geometry, transition images for transfer, and copy attachment data to host-visible buffers.
- `multisubpass` creates two color images with input-attachment usage. It verifies the buffer copied from subpass 0 and the buffer copied from subpass 1 after the two render-pass subpasses complete.
- `different_attachments` runs two render-pass instances with different color views and checks each copied image independently.
- Color, depth, and stencil readback use procedural reference data and `tcu::intThresholdCompare` with a `tcu::UVec4(1)` threshold. Resolve families additionally inspect the resolved results and, where applicable, per-sample behavior.
- A family returns pass only when every required attachment comparison succeeds. The source reports which color, depth, or stencil part is incorrect when a comparison fails.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `color` | Imageless color-attachment description, begin-time binding, rendering, transfer, or color comparison failure. |
| `depth_stencil` | Color, depth, or stencil attachment binding, rendering, readback, or comparison failure. |
| `color_resolve` | Multisampled color rendering, resolve binding, resolve operation, or resolved-image comparison failure. |
| `depth_stencil_resolve` | Multisampled color/depth/stencil setup, resolve extension path, resolve operation, or readback failure. |
| `multisubpass` | Input-attachment relationship, subpass dependency, one of the two attachment views, or either image comparison failure. |
| `different_attachments` | Begin-time selection of a compatible image view or one of the two render-pass results failed. |

### Cause Analysis

#### Imageless attachment description or begin-time binding mismatch

**Possible failure symptoms:** The render pass cannot begin, or the copied attachment contains a result inconsistent with the image view supplied at begin time.

**Possible implementation causes:** The implementation may mishandle `VK_FRAMEBUFFER_CREATE_IMAGELESS_BIT`, attachment constraints, or `VkRenderPassAttachmentBeginInfo` view binding. The source creates the framebuffer and supplies the views in each instance's render-pass begin sequence.

#### Attachment-role, resolve, or subpass processing failure

**Possible failure symptoms:** A color, depth, stencil, resolve, or second-subpass buffer differs from its procedural reference.

**Possible implementation causes:** The failure may involve attachment load/store handling, multisample resolve, depth/stencil aspect processing, input-attachment reads, or subpass dependencies. The failing family narrows the mechanism, but the image comparison alone cannot identify a driver stage.

#### Shared transfer, synchronization, or comparison path failure

**Possible failure symptoms:** One or more copied buffers fail even though the render-pass scenario is otherwise valid.

**Possible implementation causes:** The image-to-buffer transition, transfer operation, host-read visibility, or comparison format conversion may be wrong. The source uses image and buffer barriers before host verification; further source or API-log investigation is needed to localize this cause.

## Case Pruning

### Requirement-based pruning

- All families require `VK_KHR_imageless_framebuffer` or its core equivalent and the `imagelessFramebuffer` feature through the shared test context and imageless framebuffer creation path.
- Resolve families require `standardSampleLocations`. `depth_stencil_resolve` also requires the depth/stencil resolve support used by its render-pass construction.
- The implementation checks image-format properties for the requested format, usage, extent, and sample count. Unsupported combinations do not execute.

### Design-based pruning

The six leaves hold the color format and extent fixed so each leaf isolates an attachment or render-pass relationship. The test intentionally uses one color format and one depth/stencil format rather than generating a broader format matrix.

## Key Takeaways

- The core contract is split between framebuffer-time attachment constraints and render-pass-begin image-view selection.
- Resolve, input-attachment, depth/stencil, and repeated-begin cases test different consequences of that same late binding point.
- A pass requires every attachment result relevant to the selected family to match its host-side reference; successful render-pass submission alone is insufficient.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Category factory | [`createTests()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L3027-L3041) | Registers all six direct test families. |
| Test parameters | [`TestType` and `TestParameters`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L60-L89) | Defines the family and attachment-format choices. |
| Color execution | [`ColorImagelessTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1222-L1315) | Creates, renders, copies, and verifies a color attachment. |
| Depth/stencil execution | [`DepthImagelessTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1436-L1600) | Verifies color, depth, and stencil attachment behavior. |
| Color resolve execution | [`ColorResolveImagelessTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1684-L1820) | Exercises four-sample color and single-sample resolve binding. |
| Depth/stencil resolve execution | [`DepthResolveImagelessTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L1974-L2130) | Exercises multisampled depth/stencil and resolve attachments. |
| Multi-subpass execution | [`MultisubpassTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2285-L2689) | Reads one color attachment as input in a later subpass and verifies both outputs. |
| Different-attachment execution | [`DifferentAttachmentsTestInstance::iterate()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2533-L2689) | Reuses a framebuffer with different begin-time image views. |
| Support and shader setup | [`BaseTestCase::checkSupport()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2715-L2722) and [`BaseTestCase::initPrograms()`](../../modules/vulkan/imageless_framebuffer/vktImagelessFramebufferTests.cpp#L2724-L2765) | Defines resolve support and the fixed rendering shaders. |
