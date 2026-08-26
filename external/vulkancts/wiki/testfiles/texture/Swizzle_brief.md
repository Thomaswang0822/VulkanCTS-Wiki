# Understanding Brief: `texture.swizzle`

## One-Sentence Test Purpose

This test checks whether sampled 2D images return the component order or texture-coordinate interpretation selected by the test, with the same result through graphics and compute rendering and through regular and sparse image backing.

## Background Knowledge

### Image-view component mapping

`VkImageViewCreateInfo::components` assigns one `VkComponentSwizzle` to each returned R, G, B, and A component. A mapping can select an original component, inject zero or one, or use the component's identity mapping. Vulkan applies this mapping to texel input instructions, so the shader uses an ordinary texture lookup; the mapping is image-view state rather than a GLSL result swizzle.

Why it matters here:

- The `component_mapping` family passes the selected mapping into the sampled image view.
- Missing source color components have format-defined defaults before view swizzling: absent color channels behave as zero and absent alpha behaves as one. The software reference reproduces that rule.
- `ONE` means `1.0` for floating-point components and `1` for integer components, as specified in [Component Swizzle](../../../../vulkan-docs/src/chapters/textures.adoc#L731-L792).

### Depth/stencil image views and `ONE`

A depth/stencil image view selects one aspect. The Vulkan specification normally leaves a depth/stencil texel undefined after `VK_COMPONENT_SWIZZLE_ONE`; Vulkan 1.4 or `VK_KHR_maintenance5` defines that behavior only when `depthStencilSwizzleOneSupport` is true. The relevant exception appears in the [component-swizzle rules](../../../../vulkan-docs/src/chapters/textures.adoc#L800-L810), and the property is described in [Physical Device Limits](../../../../vulkan-docs/src/chapters/limits.adoc#L1863-L1868).

Why it matters here:

- The depth and stencil branches test only `oooo`, where all four returned components select `ONE`.
- Their support check requires `VK_KHR_maintenance5` and `depthStencilSwizzleOneSupport` before execution.

### Coordinate swizzling

A GLSL suffix such as `.yx`, `.xx`, or `.yy` changes the coordinate sent to the sampling operation. It does not alter image-view state or rearrange the returned texel. `.yx` swaps the two axes; `.xx` uses the original x coordinate for both axes; `.yy` does the same with y.

Why it matters here:

- `texture_coordinate` inserts the suffix into generated fragment and compute shaders.
- The software renderer applies the matching two-entry coordinate map before interpolation and sampling.

## One Concrete Example

Consider `dEQP-VK.texture.swizzle.component_mapping.color.r8g8b8a8_unorm_2d_pot_abgr`. The host creates a 128 by 64 texture and an image view with:

```cpp
// Conceptual reconstruction of the registered mapping.
components = { A, B, G, R };
```

The fragment shader still performs an ordinary lookup:

```glsl
vec4 result = texture(u_sampler, v_texCoord) * u_colorScale + u_colorBias;
```

If the unswizzled sampled value is `(r, g, b, a)`, the image view returns `(a, b, g, r)`. The host samples the same software texture, applies the same ABGR permutation to every reference pixel, and compares the two R8G8B8A8_UNORM images.

A coordinate case changes a different stage of the lookup. For `...texture_coordinate.r8g8b8a8_unorm_2d_pot_yx`, generated GLSL samples `texture(u_sampler, v_texCoord.yx)`, while the image view keeps RGBA mapping.

## End-to-End Test Flow

```text
[host] choose color, depth, or stencil behavior; format; POT or NPOT extent; mapping or coordinate suffix; backing mode; and graphics or compute execution
[host] create a generated TestTexture2D with known data
[host] generate shared texture shaders, inserting a coordinate suffix only for texture_coordinate cases
[host] create an optimally tiled sampled image, upload the texture through the regular or sparse path, and create an image view with the selected aspect and VkComponentMapping
[host] bind the image view and sampler; prepare a graphics render target or compute storage-image output
[host] submit a quad draw or a 16 by 16 workgroup-grid dispatch
[device] obtain coordinates, apply any shader-side coordinate suffix, sample the image, and apply image-view component mapping to the texel result
[device] write an R8G8B8A8_UNORM result image
[host] read the result and render a software reference from the original test texture
[host] apply the matching coordinate map before reference sampling and the matching component map after reference sampling
[host] compare every output pixel with the configured threshold and return pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`SwizzleTestCase::initPrograms`](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L69-L73) calls the shared [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L331).
- Graphics cases use a pass-through vertex shader and a fragment shader with `texture(...)`. `texture_coordinate` adds `.yx`, `.xx`, or `.yy` where the fragment shader initializes `texCoord`.
- Compute cases use 16 by 16 local workgroups. They reconstruct the quad's perspective-correct coordinate, calculate neighboring coordinates, sample with `textureGrad(...)`, and write a storage image. The coordinate suffix is applied to the center and both neighboring coordinates.
- Component mapping never appears as a GLSL suffix. [`TextureBinding::updateTextureViewMipLevels`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L923-L966) puts it in `VkImageViewCreateInfo::components`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Generated 2D test texture | yes | no, but supplies upload data | no | used directly by host | Provides the same known texels to Vulkan upload and the software reference. |
| Sampled `VkImage` | yes | yes | read | no | Holds the texture in regular memory or fully resident sparse memory. |
| `VkImageView` | yes | yes, through the sampled-image descriptor | read through sampling | no | Carries the selected color, depth, or stencil aspect and the tested component mapping. |
| Sampler | yes | yes | read through sampling | no | Uses nearest minification and magnification filtering with repeat addressing. |
| Graphics uniform and vertex data | yes | yes | read | no | Supply texture coordinates and the output color transform to the draw path. |
| Compute uniform, push-constant, and geometry data | yes | yes | read | no | Supply output dimensions, offset, quad positions, and texture coordinates to the dispatch path. |
| R8G8B8A8_UNORM output image | yes | yes | written as a color attachment or storage image | copied to host-visible memory | Contains the implementation result that the host compares. |
| Host software reference surface | yes | no | no | read by host | Models coordinate selection, nearest sampling, component mapping, and output conversion. |

## What Is Checked

[`Swizzle2DTestInstance::iterate`](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L147-L307) checks the complete output image:

- It renders or dispatches over the full selected extent.
- The software path samples a `tcu::Texture2DView` with the same sampler, exact LOD mode, format lookup scale, and lookup bias.
- For coordinate cases, the reference swaps or duplicates the coordinate vectors before interpolation and LOD calculation.
- For non-default component mappings, it rewrites each reference pixel. `ZERO` and missing RGB components use the transformed zero value; `ONE` and missing alpha use the transformed one value; R, G, B, and A select existing source components.
- It compares the GPU image and reference with `pixelFormat.getColorThreshold() + RGBA(2,2,2,2)`. Any pixel outside that threshold fails the case.

## Behavior Parameter Identification

> **Behavior parameter:** test family or aspect branch below `texture.swizzle`
>
> **Candidate values:** `component_mapping.color`, `component_mapping.depth`, `component_mapping.stencil`, `texture_coordinate`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `component_mapping.color` | Incorrect image-view component selection, zero/one substitution, identity handling, missing-component defaults, or sampled-format conversion. |
| `component_mapping.depth` | Incorrect `ONE` swizzle handling for a depth-aspect image view, or incorrect depth-format sampling and conversion under maintenance5 support. |
| `component_mapping.stencil` | Incorrect `ONE` swizzle handling for a stencil-aspect image view, or incorrect unsigned-integer stencil sampling and conversion under maintenance5 support. |
| `texture_coordinate` | Incorrect shader coordinate swizzle, coordinate interpolation or compute reconstruction, explicit-gradient handling, or nearest sampling at the remapped coordinates. |

A failure in any branch can also come from image upload, sparse binding/residency, image-view creation, descriptor binding, graphics/compute output, synchronization, readback, or software-reference disagreement shared by the matrix.

## Important Variations and Special Cases

- The color branch covers 119 formats: 81 uncompressed formats and 38 ETC2, EAC, and ASTC compressed formats. It tests `zzzz`, `oooo`, `rrrr`, `gggg`, `bbbb`, `aaaa`, `rgba`, `iiii`, and `abgr`.
- The depth branch covers six depth or depth/stencil formats; the stencil branch covers four stencil or depth/stencil formats. Both use only `oooo` and exist only outside Vulkan SC.
- Every branch uses 128 by 64 `pot` and 51 by 65 `npot` extents. The non-square sizes make `yx`, `xx`, and `yy` visibly different.
- Vulkan builds register regular and `_sparse` leaves. Vulkan SC registers regular leaves only and omits depth/stencil branches.
- Every generated combination receives a graphics leaf and a `_compute` leaf. The texture utility rejects depth/stencil formats when `m_useCompute` is true, so registered depth/stencil `_compute` leaves report not supported instead of running the compute pipeline.
- Sparse cases request sparse binding and residency image flags, verify that the format exposes sparse image properties, then upload a fully resident sparse texture. They test that swizzle behavior does not depend on the image's backing path.
- The Vulkan default mustpass lists 11,504 leaves: 8,568 color component-mapping, 48 depth, 32 stencil, and 2,856 coordinate-swizzle cases.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category dispatch | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L66) | Registers `swizzle` under `texture`. |
| Test-family registration | [`populateTextureSwizzleTests`](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L311-L649) | Defines formats, extents, mappings, backing modes, execution variants, hierarchy, and leaf names. |
| Support gates | [`SwizzleTestCase::checkSupport`](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L75-L90) | Applies shared support checks and maintenance5 depth/stencil requirements. |
| GPU setup | [`Swizzle2DTestInstance` constructor](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L129-L145) | Creates the test texture and selects graphics or compute rendering. |
| Software reference and comparison | [`Swizzle2DTestInstance::iterate`](../../../modules/vulkan/texture/vktTextureSwizzleTests.cpp#L147-L307) | Implements coordinate remapping, sampling, component remapping, and final image comparison. |
| Shader generation | [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L510) | Generates graphics and compute lookup code and inserts coordinate suffixes. |
| Image backing and view mapping | [`TextureBinding::updateTextureData` and `updateTextureViewMipLevels`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L808-L966) | Creates regular or sparse images, uploads data, chooses the aspect, and installs `VkComponentMapping`. |
| Compute execution | [`ComputeBackend`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L2528-L2806) | Binds compute resources, dispatches workgroups, copies the result, and exposes it to the host. |
| Component-swizzle semantics | [Vulkan texture specification](../../../../vulkan-docs/src/chapters/textures.adoc#L731-L810) | Defines texel component rearrangement, constants, identity, and the depth/stencil exception. |
| Current conformance list | [`vk-default/texture.txt`](../../../mustpass/main/vk-default/texture.txt#L15774-L27277) | Confirms the executable Vulkan hierarchy and generated leaves. |

## Questions / Risk Points for User Audit

- Is the separation between image-view component mapping and shader-side coordinate swizzling explicit enough?
- Is it clear that depth/stencil `_compute` leaves are registered but rejected by shared texture setup before dispatch?
- Should the final page keep both representative shaders, or is one graphics component-mapping walkthrough plus a compact compute explanation sufficient?
- Does the transformed zero/one explanation make clear why the byte-valued reference uses lookup scale and bias rather than hard-coded 0 and 255?

No unresolved source ambiguity changes the planned page semantics. The final page should retain two walkthroughs because the image-view mapping is invisible in shader text while the coordinate suffix and compute reconstruction are shader-visible.

## Conversion Notes for Final Wiki Rewrite

- Distill image-view mapping, coordinate swizzling, and the maintenance5 depth/stencil exception into concise Background Knowledge bullets.
- Use one graphics `component_mapping.color...abgr` case to show that `VkComponentMapping` is bound through the view, not emitted in GLSL.
- Use one compute `texture_coordinate...yx_compute` case to show coordinate suffix insertion, explicit gradients, and storage-image output.
- Keep the four behavior values as the primary axis.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Keep the registered-but-pruned depth/stencil compute detail under Case Pruning.
- Move detailed source navigation into the final appendix.
