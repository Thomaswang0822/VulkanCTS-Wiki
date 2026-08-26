# Understanding Brief: `texture.texel_offset`

## One-Sentence Test Purpose

This test checks whether four constant `textureOffset` operands move a nearest-filtered 2D sample by exactly one texel in the requested x or y direction.

## Background Knowledge

### Normalized coordinates and texel offsets

A normalized 2D texture coordinate is scaled by the selected image level's width and height before the sampler selects texels. An image instruction's `ConstOffset` or `Offset` operand contributes an integer offset during that normalized-to-unnormalized transformation. With nearest filtering, the resulting unnormalized position selects one integer texel coordinate.

Why it matters here:

- The test derives the base coordinate from `floor(gl_FragCoord.xy) / 255.0` and uses a 256 by 256 image. For interior pixels, the unshifted lookup selects the texel with the same integer x and y indices.
- The four constant offsets `(0,-1)`, `(0,1)`, `(-1,0)`, and `(1,0)` should reach the immediate lower, upper, left, and right neighbors.

The Vulkan specification adds image-instruction offsets during the [(s,t,r,q,a) to (u,v,w,a) transformation](../../../../vulkan-docs/src/chapters/textures.adoc#L1805-L1859), before [nearest filtering selects integer texel coordinates](../../../../vulkan-docs/src/chapters/textures.adoc#L1894-L1915). The tested values `-1` and `1` lie within the Vulkan-required [`minTexelOffset` and `maxTexelOffset` range](../../../../vulkan-docs/src/chapters/limits.adoc#L667-L676), whose required bounds include at least `-8` through `7` ([limit requirements](../../../../vulkan-docs/src/chapters/limits.adoc#L6703-L6710)).

### UNORM storage as a byte-exact signal

`VK_FORMAT_R8G8B8A8_UNORM` converts each stored byte to a floating-point value in `[0,1]`. Values of the form `k / 255.0` correspond to byte value `k`. This lets the setup pass encode integer x and y positions in red and green, then lets the tested pass encode four Boolean results as a four-bit mask in the red byte.

Why it matters here:

- A one-texel move in x changes the sampled red value; a one-texel move in y changes green.
- When all four direction checks succeed, bits `1`, `2`, `4`, and `8` produce mask `15`, so Amber can compare the final byte pattern exactly against RGBA `(15,0,0,0)`.

## One Concrete Example

At output pixel `(100,80)`, both Amber draw passes evaluate `floor(gl_FragCoord.xy)` as `(100,80)`. The base coordinate is `(100/255, 80/255)`. The setup pass has stored red `100/255` and green `80/255` at texture texel `(100,80)`.

The tested fragment shader performs these four checks:

```glsl
textureOffset(tex, base, ivec2( 0, -1)).g < base.y  // bit 1
textureOffset(tex, base, ivec2( 0,  1)).g > base.y  // bit 2
textureOffset(tex, base, ivec2(-1,  0)).r < base.x  // bit 4
textureOffset(tex, base, ivec2( 1,  0)).r > base.x  // bit 8
```

Correct offset handling reaches y values `79/255` and `81/255`, and x values `99/255` and `101/255`. Every comparison is true, so the fragment writes `15/255` to red. The final RGBA8 byte is `(15,0,0,0)`.

## End-to-End Test Flow

```text
[host] load texel_offset.amber and compile the fixed setup and test fragment shaders
[host] create a 256 by 256 R8G8B8A8_UNORM image named texture and a default nearest sampler
[host] configure the setup graphics pipeline with texture as its color target
[device] draw a full rectangle; frag_setup writes x/255 to red and y/255 to green
[host] configure the second graphics pipeline with texture as a combined image sampler and framebuffer as its color target
[device] draw a full rectangle; frag_shader performs four textureOffset samples and packs the comparisons into a red-channel bit mask
[host] inspect framebuffer pixels in the interior rectangle from index (1,1), size 254 by 254
[host] pass only when every inspected pixel equals RGBA byte value (15,0,0,0)
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`texel_offset.amber`](../../../data/vulkan/amber/texture/texel_offset/texel_offset.amber#L1-L58) is the complete executable test description. It contains both fragment shaders, the image and sampler declarations, two graphics pipelines, two full-rectangle draws, and the final expectation.
- `vert_shader` is Amber's fixed `PASSTHROUGH` vertex shader. Both graphics pipelines reuse it; its behavior does not vary.
- `frag_setup` generates the coordinate gradient. `frag_shader` performs the tested `textureOffset` operations and creates the four-bit result mask.
- The C++ registration layer passes the Amber filename and data directory to `createAmberTestCase`; it does not generate shader variants or perform result checking.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `texture`, 256 by 256 `R8G8B8A8_UNORM` image | yes | setup color target, then combined image sampler | written, then read | no direct comparison | Stores byte-exact x and y gradients for directional offset checks. |
| `sampler` | yes | with `texture` at descriptor set 0, binding 0 | controls sampled access | no | Its default nearest filters make each offset lookup select one neighboring texel. |
| `framebuffer`, `R8G8B8A8_UNORM` buffer | yes | second-pass color target | written | yes | Stores one four-bit pass mask per fragment for Amber's final comparison. |
| `gl_FragCoord` | no, shader built-in | available to both fragment shaders | read | no | Gives both passes the same integer pixel index after `floor`. |

## What Is Checked

Amber checks every pixel in the 254 by 254 interior rectangle beginning at `(1,1)`. Each output must equal RGBA byte value `(15,0,0,0)`.

| Bit | Offset and component | Required relation |
|-----|----------------------|-------------------|
| `1` | `(0,-1)`, green | sampled value is less than `base.y` |
| `2` | `(0,1)`, green | sampled value is greater than `base.y` |
| `4` | `(-1,0)`, red | sampled value is less than `base.x` |
| `8` | `(1,0)`, red | sampled value is greater than `base.x` |

Requiring red byte `15` proves that all four relations hold at every checked fragment. The expectation excludes the one-pixel border, so repeat addressing at the outer edge cannot turn a valid neighbor check into a wraparound comparison.

## Behavior Parameter Identification

> **Behavior parameter:** none; this is one fixed test case
>
> **Candidate values:** not applicable (`texel_offset` is the only executable test case leaf)

## What Failure Means

### Failure Cause Mapping

Because this family has no varying behavior parameter, any failure means that at least one fixed directional offset check did not set its expected mask bit, or that shared setup, binding, rendering, or comparison work prevented the expected `(15,0,0,0)` image from being produced.

## Important Variations and Special Cases

- The test uses four one-texel constant offsets. It does not vary offset magnitude, filter mode, image format, mip level, dimensionality, or shader stage.
- Amber's sampler defaults to nearest minification, magnification, and mipmap filters, repeat addressing, and normalized coordinates ([sampler defaults](../../../../amber/src/src/sampler.h#L98-L110)). The final expectation checks only interior pixels, where wrapping is irrelevant.
- Both draws cover all 256 by 256 pixels. Only the 254 by 254 interior is validated because each lookup needs an immediate neighbor on both sides.
- The texture dispatcher registers this family only for Vulkan builds that do not define `CTS_USES_VULKANSC`. The family has no Vulkan SC test path.
- The common Amber executor rejects this graphics test when CTS runs with the compute-only option.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Texture category dispatch | [`createTextureTests`](../../../modules/vulkan/texture/vktTextureTests.cpp#L48-L66) | Attaches `texel_offset` under `texture` and excludes it from Vulkan SC. |
| Family and case registration | [`createTextureTexelOffsetTests`](../../../modules/vulkan/texture/vktTextureTexelOffsetTests.cpp#L36-L55) | Registers the sole `texel_offset` Amber file and test case leaf. |
| Complete Amber program | [`texel_offset.amber`](../../../data/vulkan/amber/texture/texel_offset/texel_offset.amber#L1-L58) | Defines shaders, resources, pipelines, draws, and the exact expected image region. |
| Amber compilation | [`AmberTestCase::initPrograms`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L435-L499) | Shows the default SPIR-V 1.0 target and GLSL stage insertion. |
| Amber execution and result | [`AmberTestInstance::iterate`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Executes with Vulkan and maps Amber success or failure to the CTS result. |
| Exact mustpass leaf | [`vk-default/texture.txt`](../../../mustpass/main/vk-default/texture.txt#L27301) | Confirms `dEQP-VK.texture.texel_offset.texel_offset`. |
| Offset coordinate semantics | [`textures.adoc`](../../../../vulkan-docs/src/chapters/textures.adoc#L1805-L1915) | Defines offset addition and nearest texel-coordinate selection. |
| Offset limits | [`limits.adoc`](../../../../vulkan-docs/src/chapters/limits.adoc#L667-L676) | Defines device limits for sample and fetch offset operands. |

## Questions / Risk Points for User Audit

- Does the `x/255` and `y/255` gradient explanation show why each comparison identifies the requested immediate neighbor?
- Is it clear that the four output bits diagnose direction checks, while Amber reports one aggregate test case result?
- Does the one-pixel border exclusion make the role of repeat addressing unambiguous?
- Are the setup color target, sampled texture, and final framebuffer distinct in the flow and resource table?

No unresolved source ambiguity changes the page semantics. The final page should keep the fixed-case behavior model and avoid inventing a parameter axis.

## Conversion Notes for Final Wiki Rewrite

- Distill normalized-coordinate offset application and UNORM byte encoding into short Background Knowledge bullets.
- Use the sole mustpass path for the representative shader walkthrough.
- Show both fragment shaders because `frag_setup` creates the directional evidence consumed by `frag_shader`; generate SPIR-V only for the primary tested fragment shader.
- Carry the no-behavior-parameter conclusion into `## Behavior Parameters`.
- Copy the `### Failure Cause Mapping` paragraph unchanged into the final page.
- Keep the two-draw timeline and bit table, but move detailed source navigation into the final appendix.
