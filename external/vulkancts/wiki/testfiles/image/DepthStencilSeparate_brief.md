# Understanding Brief: `image.depth_stencil_separate_access`

## One-Sentence Test Purpose

This family checks that a combined depth/stencil image can expose one aspect for fragment-shader sampling while the render pass accesses the other aspect as a framebuffer attachment.

## Background Knowledge

### A depth/stencil image has two independently addressable aspects

`VK_FORMAT_D16_UNORM_S8_UINT`, `VK_FORMAT_D24_UNORM_S8_UINT`, and `VK_FORMAT_D32_SFLOAT_S8_UINT` contain depth and stencil data. The test creates a full depth/stencil view for the attachment and a second view containing only the sampled aspect. A fragment shader fetches the sampled depth as floating-point data or the sampled stencil as unsigned-integer data, then writes that value to a storage image.

Why it matters here:

- A `write_depth` case samples stencil while depth participates in attachment operations.
- A `write_stencil` case samples depth while stencil participates in attachment operations.
- The storage image makes the shader-observed, read-only aspect available for host comparison.

### Attachment access can use one combined layout or two aspect layouts

The ordinary layout path uses `VK_IMAGE_LAYOUT_GENERAL` or a combined depth/stencil layout chosen for the read/write direction. The `separate_layouts` path supplies depth and stencil layouts independently through render-pass-2 depth/stencil-layout structures. It uses `DEPTH_READ_ONLY_OPTIMAL` with `STENCIL_ATTACHMENT_OPTIMAL`, or the inverse, according to the selected write aspect.

Why it matters here:

- The ordinary and general paths exercise access to the two aspects while one image layout represents the attachment.
- The separate-layout path exercises the per-aspect layout interface and barriers for the same sampling-and-attachment arrangement.

### The write mechanism selects the attachment behavior

The family uses four mechanisms: render-pass clear, render-pass `DONT_CARE`, depth/stencil test followed by store, and test followed by depth/stencil resolve. The read-only aspect always uses `LOAD` and `STORE`, so its prefilled data must survive the render pass. The write aspect receives the load/store behavior selected by the mechanism.

`DONT_CARE` does not define the resulting written aspect. The host therefore skips comparison of that aspect and still checks the shader-observed opposite aspect.

## One Concrete Example

`dEQP-VK.image.depth_stencil_separate_access.d24_unorm_s8_uint.write_depth_test_and_store_separate_layouts` initializes every texel of a 16 x 16 `VK_FORMAT_D24_UNORM_S8_UINT` image with a generated depth and stencil value. The render pass uses the depth aspect as a writable attachment in `DEPTH_ATTACHMENT_OPTIMAL` and the stencil aspect as a sampled read-only image in `STENCIL_READ_ONLY_OPTIMAL`. Each point primitive covers one pixel. Its fragment shader writes the generated color to the color attachment and stores `texelFetch(stencilSampler, texCoords, 0)` to an `R32_UINT` storage image. The depth test always passes and writes each point's generated depth. After rendering, the host checks color, the sampled-stencil storage image, and depth; it does not need to compare the stencil attachment separately because the storage image already observed it.

## End-to-End Test Flow

```text
[host] select depth/stencil format, write aspect, mechanism, layout mode, and stencil-reference mode
[host] check maintenance7/property, format, sample-count, and selected-path extension support
[host] generate 256 point vertices with one depth, stencil reference, and color per pixel
[host] prefill both aspects of a single-sample depth/stencil image through buffer-to-image copies
[host] create full attachment and one-aspect sampled views, a storage image, render pass, descriptors, and graphics pipeline
[host] transition the image to combined, general, or per-aspect attachment/sample layouts
[device] render one point per pixel; sample the read-only aspect and write the selected aspect through the attachment operation
[host] copy color, storage, depth, and stencil results to host-visible buffers
[host] compare color and sampled-aspect storage data; compare the defined written attachment aspect
```

## Generated Test Artifacts and Bound Resources

### Generated programs

- [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) generates GLSL 4.60 vertex and fragment shaders.
- The vertex shader forwards position, color, and a per-point stencil-reference field.
- The fragment shader selects `sampler2D` plus `r32f image2D` for a depth read, or `usampler2D` plus `r32ui uimage2D` for a stencil read. Dynamic-stencil-reference leaves enable `GL_ARB_shader_stencil_export` and assign `gl_FragStencilRefARB`.

### Bound resources and memory objects

| Resource | Host-created | Device use | Host readback | Role |
|----------|--------------|------------|---------------|------|
| Vertex buffer | Yes | Vertex input | No | Supplies one point, color, depth, and stencil reference per framebuffer pixel. |
| Single-sample depth/stencil image | Yes | Attachment, sampled image, transfer source/destination | Yes | Holds both aspects; a full view attaches it and an aspect-only view samples it. |
| Optional 4x multisample depth/stencil image | Resolve leaves only | Multisample attachment | No | Supplies the depth/stencil source for sample-zero resolve into the single-sample image. |
| Color image with readback buffer | Yes | Color attachment, transfer source | Yes | Confirms that the point draw reached every pixel. |
| `R32_SFLOAT` or `R32_UINT` storage image with readback buffer | Yes | Fragment storage write, transfer source | Yes | Captures values sampled from the read-only aspect. |
| Depth and stencil prefill buffers | Yes | Transfer source | No | Initialize the two aspects before the render pass. |
| Depth and stencil verification buffers | Yes | Transfer destination | Yes | Hold copied attachment results for direct comparison. |
| Sampler and descriptor set | Yes | Fragment descriptors | No | Bind the aspect-only sampled view at binding 0 and storage image at binding 1. |

## What Is Checked

- Color readback must equal the per-vertex generated color within `0.005` ([comparison](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1385-L1387)).
- The storage image must equal the values prefilled into the sampled depth or stencil aspect. Depth uses a format-specific float threshold; stencil uses exact integer comparison ([storage comparison](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1389-L1394)).
- The defined written depth or stencil aspect must equal its reference image. The test skips direct comparison when that aspect was sampled, and skips the written `DONT_CARE` aspect because the attachment operation leaves it undefined ([attachment comparisons](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1396-L1406)).

## Behavior Parameter Identification

> **Behavior parameter:** selected write mechanism
>
> **Candidate values:** `render_pass_clears`, `render_pass_dont_care`, `test_and_store`, `test_and_resolve`

The selected write aspect, format, layout mode, and optional dynamic stencil reference choose legal implementations around the mechanism. The mechanism determines whether the attachment path relies on load-op clear, `DONT_CARE`, fragment testing with store, or multisample resolve.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `render_pass_clears` | Depth/stencil attachment clearing, preservation and sampling of the opposite aspect, or readback synchronization. |
| `render_pass_dont_care` | Access to the preserved sampled aspect, the `DONT_CARE` attachment path, or color/storage readback. The test does not diagnose a resulting value for the written aspect. |
| `test_and_store` | Depth/stencil test and write behavior, sampled opposite-aspect preservation, dynamic state/reference handling, or result comparison. |
| `test_and_resolve` | Multisample attachment access, sample-zero depth/stencil resolve, sampled resolve-target aspect preservation, or result readback. |

## Important Variations and Special Cases

- **Write aspect.** `write_depth` samples stencil and writes depth. `write_stencil` samples depth and writes stencil.
- **Formats.** The factory registers `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, and `d32_sfloat_s8_uint`. The depth comparison threshold follows the selected depth representation.
- **General layout.** `_general_layout` causes `VK_IMAGE_LAYOUT_GENERAL` to replace the ordinary combined layout.
- **Separate layouts.** `_separate_layouts` creates aspect-specific layouts and requires `VK_KHR_separate_depth_stencil_layouts`.
- **Dynamic stencil reference.** `_dynamic_stencil_ref` exists only for `write_stencil` test/resolve mechanisms. It exports the per-vertex reference from the fragment shader; other stencil-test leaves issue one-point draws and set dynamic stencil reference before each draw.
- **Resolve pruning.** Resolve leaves use four samples and `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT`. The factory excludes their separate-layout combinations to limit the matrix.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameters and layout selection | [`TestParams`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L83-L185) | Defines the read/write aspect inversion, layouts, sample count, and storage format. |
| Support checks | [`DepthStencilSeparateCase::checkSupport()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L316-L399) | Checks required functionality, property, format, sample count, and variant extensions. |
| Shader generation | [`DepthStencilSeparateCase::initPrograms()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L401-L460) | Emits the sampler/storage-image fragment path and optional stencil export. |
| Render-pass setup | [`makeSeparateRenderPass()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L558-L797) | Configures aspect load/store behavior, layouts, and resolve attachments. |
| Execution and verification | [`DepthStencilSeparateInstance::iterate()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L833-L1411) | Creates resources, records barriers/draws/copies, and reports comparisons. |
| Case matrix | [`createImageDepthStencilSeparateTests()`](../../../modules/vulkan/image/vktImageDepthStencilSeparateTests.cpp#L1415-L1485) | Registers formats, mechanisms, layout variants, dynamic reference leaves, and pruned combinations. |

## Questions / Risk Points for User Audit

- Does the distinction between the written attachment aspect and the sampled, preserved aspect remain clear across all four mechanisms?
- Does the `test_and_resolve` description make clear that the source checks sample-zero resolve behavior rather than a general depth/stencil reduction rule?
- Are the `DONT_CARE` comparison boundary and the dynamic-stencil-reference variants described without implying a defined written result?

## Conversion Notes for Final Wiki Rewrite

- Keep write mechanism as the behavior parameter and preserve the failure-cause table.
- Use a `write_depth`/`separate_layouts` store case for the shader walkthrough because it shows an aspect-only stencil sampler beside a writable depth attachment.
- State that `DONT_CARE` suppresses comparison of the written aspect, rather than claiming that it validates a specific post-render value.
- Retain the generated matrix, requirements, resource roles, and resolve/layout pruning rules in the final page.
