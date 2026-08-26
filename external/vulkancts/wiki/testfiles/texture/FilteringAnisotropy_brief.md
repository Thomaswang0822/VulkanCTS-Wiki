# Understanding Brief: `texture.filtering_anisotropy`

## One-Sentence Test Purpose

This test checks whether enabled sampler anisotropy keeps an obliquely projected 2D texture close to the isotropic result and, where checked, changes it by a detectable amount in graphics and compute pipelines across level-0 and mipmapped configurations.

## Background Knowledge

### Anisotropic texture footprints

A screen pixel usually maps to an area rather than a point in texture space. Under an oblique projection, that footprint can be much longer along one texture axis than the other. Isotropic filtering treats both directions with one scale, while anisotropic filtering may take more samples along the major axis of the footprint.

Vulkan derives two footprint scale factors from coordinate derivatives. It limits their ratio by the sampler's `maxAnisotropy` and the device's `maxSamplerAnisotropy`. A ratio of one is isotropic; a larger ratio permits anisotropic sampling. The specification leaves approximation and sampling-rate choices to the implementation, so two conformant implementations need not produce one exact anisotropic image. See [scale-factor and anisotropy calculation](../../../../vulkan-docs/src/chapters/textures.adoc#L1535-L1651), [sampler anisotropy state](../../../../vulkan-docs/src/chapters/samplers.adoc#L99-L106), and [the device anisotropy limit](../../../../vulkan-docs/src/chapters/limits.adoc#L562-L567).

Why it matters here:

- The perspective-varying clip-space W values create a strongly nonuniform texture footprint across the quad.
- The test compares two device-produced images because the specification does not prescribe one exact anisotropic filter kernel.
- A large requested anisotropy does not bypass the device limit. The host clamps it before sampler creation.

### Graphics and compute gradient sources

A fragment shader can use implicit coordinate derivatives for `texture(...)`. A compute shader has no rasterizer-provided fragment derivatives, so the shared texture utility reconstructs perspective-correct coordinates at the current, X-adjacent, and Y-adjacent output positions, then supplies their differences to `textureGrad(...)`.

Why it matters here:

- Unsuffixed and `_compute` leaves exercise the same sampled image and sampler states through different derivative and output paths.
- A failure confined to one route can implicate derivative construction, interpolation, descriptor setup, or output handling for that route rather than anisotropic filtering shared by both.

## One Concrete Example

Consider `dEQP-VK.texture.filtering_anisotropy.mipmap.anisotropy_max.mag_linear_min_linear_mipmap_linear_compute`.

The host creates a 128 by 128 `VK_FORMAT_R8G8B8A8_UNORM` 2D texture with eight mip levels, from level 0 through level 7. Every level contains a black-and-white grid scaled to that level. The `anisotropy_max` token requests `10000.0`, which the host reduces to the device's `maxSamplerAnisotropy`. The compute backend then performs two otherwise identical dispatches:

```glsl
// Conceptual extract reconstructed from initializePrograms().
vec2 texCoord  = interpolate(vec2(coord), size);
vec2 texCoordX = interpolate(vec2(coord) + vec2(1.0, 0.0), size);
vec2 texCoordY = interpolate(vec2(coord) + vec2(0.0, 1.0), size);
vec2 dPdx = texCoordX - texCoord;
vec2 dPdy = texCoordY - texCoord;
vec4 result = textureGrad(u_sampler, texCoord, dPdx, dPdy);
```

The first dispatch binds a sampler with anisotropy disabled by passing `1.0` to the renderer. The second enables anisotropy and binds the clamped maximum. The tilted quad uses W values `3.5` along one side and `1.0` along the other, which creates the anisotropic footprint. The host first requires the two images to remain fuzzily similar. Because both selected texel filters are linear, it also requires at least one difference larger than the per-component `0.02` threshold. This second check is a diagnostic guard against silently leaving anisotropy disabled; it does not claim that Vulkan requires anisotropic and isotropic linear filtering to differ.

## End-to-End Test Flow

```text
[host] select basic, single_level, or mipmap parameters, an anisotropy request, filter state, and graphics or compute route
[host] reject the case if samplerAnisotropy is unsupported and reject a compute leaf if no compute queue route is available
[host] clamp the requested anisotropy to maxSamplerAnisotropy
[host] generate the shared 2D floating-point graphics and compute programs
[host] create a 128 by 128 RGBA8 texture and fill each used level with a black-and-white grid
[host] upload the image and prepare the perspective-varying quad
[host] draw or dispatch once with maxAnisotropy 1.0 and read back the isotropic image
[device] sample through fragment implicit derivatives or compute-supplied gradients
[host] draw or dispatch again with the selected anisotropy and read back the anisotropic image
[host] require fuzzy similarity at 0.05
[host] when both texel filters are non-nearest, require the images not to pass a 0.02 per-component equality threshold
[host] return pass only when the applicable comparison checks succeed
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

[`FilteringAnisotropyTests::initPrograms`](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L181-L186) selects `PROGRAM_2D_FLOAT`. [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L759) generates GLSL 4.50 vertex, fragment, and compute programs. The graphics route passes a `vec2` coordinate from the vertex shader and samples a `sampler2D` with `texture(...)`. The compute route reconstructs perspective interpolation, calls `textureGrad(...)`, and writes an `rgba8` storage image. No explicit `ShaderBuildOptions` are supplied, so the source collection uses its baseline SPIR-V 1.0 target.

Sampler state is generated twice per executable case. [`GraphicsBackend::createFrameResources`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L2212-L2330) and [`ComputeBackend::createFrameResources`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L2611-L2657) leave anisotropy disabled for `1.0`, and set `anisotropyEnable = VK_TRUE` with the requested value when it is greater than one.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Grid-pattern 2D image | yes | yes | read | no | High-frequency directional content makes filtering changes visible. |
| Isotropic sampler | yes | yes | read as sampling state | no | Supplies the within-case baseline with anisotropy disabled. |
| Anisotropic sampler | yes | yes | read as sampling state | no | Enables anisotropy at the clamped requested value. |
| Uniform block | yes | yes | read | no | Supplies output size plus shared scale and bias fields. |
| Quad vertex data | yes | yes | read | no | Supplies positions with unequal W values and full-range texture coordinates. |
| Compute geometry buffer | yes for `_compute` leaves | yes | read | no | Lets the compute shader reproduce perspective interpolation and gradients. |
| Graphics color image or compute storage image | yes | yes | written | yes | Holds one isotropic or anisotropic 128 by 128 result for host comparison. |
| Host `Surface` pair | yes | no | no | yes, host-only | Stores the two readbacks passed to the comparison functions. |

The source uses regular image backing through the default `add2DTexture` path. It registers no sparse variants.

## What Is Checked

Each executable case produces an isotropic image and an anisotropic image from the same texture, quad, filters, shader route, and output dimensions.

1. [`tcu::fuzzyCompare`](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L149-L152) must accept the pair with threshold `0.05`. This rejects anisotropic output that departs too far from the corresponding isotropic rendering.
2. When `minFilter` and `magFilter` are both different from plain `NEAREST`, [`floatThresholdCompare`](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L154-L163) must reject equality at `Vec4(0.02f)`. In other words, some image difference must exceed the threshold. The source omits this check when either texel filter is nearest because demanding a visible difference would be too strict.
3. Either failed applicable condition returns `Fail`; otherwise the case returns `Pass`.

This is comparison-based validation, not a CPU reference implementation of anisotropic filtering. The source comments state that Vulkan does not require anisotropic and bilinear results to differ even for linear filtering. The difference check is intended to catch likely setup errors, while the fuzzy check bounds the overall change.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node below `texture.filtering_anisotropy`
>
> **Candidate values:** `basic`, `single_level`, `mipmap`

These values change whether the texture object contains one mip level or a complete allocated chain, how many levels receive the grid pattern, and whether the minification filter can select or blend mip levels.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | Incorrect anisotropy enablement or clamping, 2D footprint handling, nearest or linear texel filtering, or graphics/compute execution with sampling restricted to level 0. |
| `single_level` | Incorrect anisotropic sampling of a physically single-level image, single-level image/view setup, or graphics/compute handling for that image shape. |
| `mipmap` | Incorrect anisotropic footprint-to-LOD handling, mip-level selection or blending, mip-chain sampling, or graphics/compute gradient handling. |

Failures shared by all three values can also come from grid upload, sampler creation, the shared perspective quad, readback, or comparison handling. A graphics-only or `_compute`-only pattern narrows investigation to the corresponding pipeline route.

## Important Variations and Special Cases

- `basic` and `single_level` register `nearest` and `linear` minification filters and set `maxLevel` to 0, so sampling stays at level 0. `basic` constructs the normal complete CPU texture object and fills level 0; `single_level` constructs a texture object with exactly one mip level.
- `mipmap` exposes levels 0 through 7 and registers `nearest_mipmap_nearest`, `nearest_mipmap_linear`, `linear_mipmap_nearest`, and `linear_mipmap_linear` as minification values.
- All three families cross magnification values `nearest` and `linear`, anisotropy requests `2.0`, `4.0`, `8.0`, and `10000.0`, and unsuffixed graphics with `_compute` execution. This produces 32 `basic`, 32 `single_level`, and 64 `mipmap` executable cases.
- `anisotropy_max` is a request for the device limit, not a literal sampler value of `10000.0`. The constructor clamps it before either sampler is created.
- The distinction test runs only if neither selected texel filter is plain `NEAREST`. Mipmap modes whose within-level filter is nearest still satisfy `minFilter != NEAREST` as represented by the CTS filter enum, so they receive the distinction check.
- The compute route requires a usable compute queue path. The shared utility raises `NotSupportedError` if that route is unavailable.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test category registration | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L66) | Attaches `filtering_anisotropy` directly under `texture`. |
| Parameter and sampler setup | [`AnisotropyParams` and constructor](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L55-L104) | Defines the matrix state, clamp, LOD range, and level exposure. |
| Texture, quad, and comparison flow | [`FilteringAnisotropyInstance::iterate`](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L106-L166) | Creates the grid, renders both sampler states, and applies both checks. |
| Support check | [`FilteringAnisotropyTests::checkSupport`](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L193-L199) | Requires `samplerAnisotropy`. |
| Registered matrix | [`createFilteringAnisotropyTests`](../../../modules/vulkan/texture/vktTextureFilteringAnisotropyTests.cpp#L207-L322) | Defines all three intermediate nodes, anisotropy requests, filters, and graphics/compute pairs. |
| Generated shaders | [`initializePrograms`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L210-L759) | Generates the graphics `texture` path and compute `textureGrad` path. |
| Sampler creation | [`GraphicsBackend` and `ComputeBackend`](../../../modules/vulkan/texture/vktTextureTestUtil.cpp#L2212-L2330) | Converts the renderer argument into disabled or enabled Vulkan anisotropy state. |
| Sampler mapping defaults | [`mapSampler`](../../../framework/vulkan/vkImageUtil.cpp#L4472-L4509) | Maps CTS filter values, mipmap mode, LOD range, and the initial disabled anisotropy state. |
| Mustpass examples | [`texture.txt`](../../../mustpass/main/vk-default/texture.txt#L9743-L9870) | Confirms all three intermediate nodes and paired graphics/compute leaves. |
| Vulkan anisotropy semantics | [`textures.adoc`](../../../../vulkan-docs/src/chapters/textures.adoc#L1574-L1651) | Defines footprint scales, anisotropy ratio, sampling rate, and implementation latitude. |
| Sampler validity and feature rules | [`samplers.adoc`](../../../../vulkan-docs/src/chapters/samplers.adoc#L99-L106) and [`samplers.adoc`](../../../../vulkan-docs/src/chapters/samplers.adoc#L234-L240) | Defines enablement, clamping state, feature dependence, and valid value range. |

## Questions / Risk Points for User Audit

- Is `basic`, `single_level`, and `mipmap` the most useful behavior axis for failure diagnosis?
- Is the difference between a physically single-level image and a full image restricted to level 0 clear?
- Does the explanation avoid presenting the 0.02 distinction check as a Vulkan requirement?
- Is the compute path described as an explicit-gradient counterpart without implying bit-identical gradients to rasterization?

No unresolved source ambiguity changes the planned page semantics. The final page should preserve the test's intentionally limited, device-to-device comparison model and state its diagnostic limits plainly.

## Conversion Notes for Final Wiki Rewrite

- Keep anisotropic footprints, implementation latitude, and graphics versus compute derivative sources as short Background Knowledge bullets.
- Use the mipmapped `anisotropy_max` compute leaf for the representative shader walkthrough because it exposes explicit gradients and the clamped sampler state.
- Carry `basic`, `single_level`, and `mipmap` into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` table unchanged.
- Preserve both comparison checks, including the non-nearest condition and the warning that the distinction check is diagnostic rather than a direct specification requirement.
- Move detailed function navigation to the source appendix.
