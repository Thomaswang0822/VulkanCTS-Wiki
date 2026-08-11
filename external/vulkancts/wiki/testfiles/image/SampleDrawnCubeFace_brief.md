# Understanding Brief: `image.sample_cubemap`

## One-Sentence Test Purpose

This test checks whether a cubemap sampler selects and filters the four faces surrounding cubemap face 0 after face 0 has been rendered twice.

## Background Knowledge

### Cubemap face selection

A cubemap view exposes six 2D array layers as the six directions of a cube. A `samplerCube` chooses a face from the major direction component of a normalized direction and uses the remaining components as coordinates on that face. The test renders only face 0, then samples directions whose dominant components are `+Y`, `-Y`, `+Z`, and `-Z`; these directions should address the four faces adjacent to face 0 rather than face 0 itself.

Why it matters here:
- The result depends on the implementation's cube-face selection and coordinate mapping, not only on ordinary 2D sampling.
- The test uses four explicit direction constructions so that a value written to face 0 cannot satisfy the surrounding-face samples by accident.

### Render-to-sample synchronization

The cubemap is first used as a color attachment and then read through a combined image sampler in a later draw. The command buffer inserts an image barrier between the render pass and the sampling draw, changing the cubemap from `VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL` to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL` and making color-attachment writes available to fragment-shader reads.

Why it matters here:
- A failure can come from either cubemap sampling or the visibility/layout transition between the two graphics passes.
- After the first sampling draw, the source and target images are transitioned back so the second write/sample iteration can run.

## One Concrete Example

The only registered case is:

```text
dEQP-VK.image.sample_cubemap.write_face_0
```

It creates an 8 x 8 `VK_FORMAT_R8G8B8A8_UNORM` cubemap with six layers and one mip level. The first draw writes magenta (`1, 0, 1, 1`) to face 0. The sampling fragment shader samples the four directions `(u, 1, v)`, `(u, -1, v)`, `(u, v, 1)`, and `(u, v, -1)`, averages them, and writes the result to a separate 2D target. The second iteration writes cyan (`0, 1, 1, 1`) to face 0 and samples the surrounding faces again.

The host copies the target to a host-visible buffer and checks the rightmost pixel of every row. It requires the red byte to be zero and the green byte to be greater than zero. The red-zero condition shows that the sampled value did not come from the magenta face-0 write; the positive-green condition shows that it observed the cyan write after the second pass's cubemap sampling path.

## End-to-End Test Flow

```text
[host] create an 8 x 8, six-layer R8G8B8A8_UNORM cube-compatible image and cube view
[host] create a linear sampler, a 2D target image/view, vertex buffers, render passes, and two graphics pipelines
[host] clear cubemap and target images
[host] record pass 0: render magenta to face 0, barrier cubemap, sample four surrounding directions into target
[host] transition cubemap and target back for the next iteration
[host] record pass 1: render cyan to face 0, barrier cubemap, sample the same four directions into target
[host] copy the target image to a host-visible result buffer
[host] require result red == 0 and green > 0 at x = width - 1 for every row
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`SampleDrawnCubeFaceTest::initPrograms()` generates four GLSL 4.50 shaders:

- `vert1` passes a full-screen position for the cubemap-writing pipeline.
- `frag1` selects magenta for push-constant `pass == 0` and cyan for `pass == 1`.
- `vert2` passes position and 2D texture coordinates for the sampling pipeline.
- `frag2` declares `samplerCube`, performs four `texture()` calls, averages the four `vec4` results, and writes the target color.

The source registers these programs through `SourceCollections`; it does not load a prebuilt shader or use a compute dispatch.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---|---|---|---|---|
| Cubemap image | Yes | Color attachment and sampled cube view | Face 0 is rendered; all six layers are sampled through the cube view | No | Holds the rendered cube faces under test. |
| Target 2D image | Yes | Color attachment | Receives the four-sample average | Indirectly through result buffer | Converts sampled output into a host-checkable image. |
| Position vertex buffer | Yes | Vertex input of both pipelines | Read by vertex stages | No | Covers the render area with two triangles. |
| UV/position vertex buffer | Yes | Vertex input of the sampling pipeline | Read by vertex stage | No | Supplies normalized coordinates used to form four cube directions. |
| Combined image sampler and descriptor set | Yes | Fragment binding 0 | `frag2` reads the cubemap | No | Selects the cube view, sampler filtering, and address modes. |
| Push constant | Yes | Fragment stage of the write pipeline | Selects magenta or cyan | No | Distinguishes the two writes to face 0. |
| Result buffer | Yes | Transfer destination | Receives target-image copy | Yes | Supplies the final per-row byte checks. |

## What Is Checked

- The cubemap image is created with `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT`, six layers, one mip level, and the usages needed for transfer, color attachment, input attachment, and sampling.
- The first and second write passes use the push constant to render magenta and cyan, respectively, to the same cubemap view.
- Four `samplerCube` samples are averaged for each target fragment.
- After copyback, the host checks one pixel per row: `val[0] == 0` and `val[1] > 0`. The target image is also logged as a test attachment.

## Behavior Parameter Identification

> **Behavior parameter:** cubemap face write/sample iteration
>
> **Candidate values:** `write_face_0` pass 0; `write_face_0` pass 1.

The subgroup has one leaf, `write_face_0`, and the source runs its write/sample sequence twice. The pass value changes the color written to face 0, while the sampling directions and target validation remain fixed. The two iterations together distinguish a stale or wrongly selected face-0 sample from a sample that observes the intended post-render cubemap state.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `write_face_0` pass 0 | Face-0 render setup, cubemap view/layer selection, the first render-to-sample barrier, cube-face selection, surrounding-face sampling, or target-image write. |
| `write_face_0` pass 1 | Reuse of the cubemap and target after the first iteration, the second render-to-sample barrier, face-0 rewrite, cube-face sampling, or final result handling. |

## Important Variations and Special Cases

- The factory registers only `write_face_0`; there is no matrix of formats, sizes, face indices, filtering modes, or sample counts.
- `VK_FORMAT_R8G8B8A8_UNORM`, 8 x 8 extent, six layers, one mip level, linear minification/magnification, nearest mipmap mode, and repeat addressing are fixed by the source.
- The sampled directions cover `+Y`, `-Y`, `+Z`, and `-Z` around face 0. The source does not independently register tests for the other cube faces or the remaining direction combinations.
- The host checks only red and green. Blue and alpha are not independent pass criteria.
- The test uses the universal graphics queue and a single primary command buffer; it does not exercise queue-family ownership transfers.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Cubemap creation and fixed parameters | [`makeImageCreateInfo()` and `createImageSampleDrawnCubeFaceTests()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L71-L96) | Defines cube compatibility, six layers, usages, format, and the 8 x 8 case. |
| Resource and pipeline setup | [`SampleDrawnCubeFaceTestInstance::iterate()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L237-L399) | Creates images, views, sampler, descriptors, render passes, pipelines, and buffers. |
| Two-pass execution and barriers | [`iterate()` pass loop](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L405-L463) | Shows both face-0 writes, four-face sampling draws, layout transitions, and copyback. |
| Host result check | [`iterate()` result validation](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L465-L494) | Defines the exact red/green byte predicate and logged attachment. |
| Generated shaders | [`SampleDrawnCubeFaceTest::initPrograms()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L519-L569) | Defines the write colors, cube-direction samples, and four-sample average. |
| Parent registration | [`createImageSampleDrawnCubeFaceTests()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L578-L587) | Registers `sample_cubemap.write_face_0`. |
| Cubemap sampling rules | [Vulkan image operations](../../../../vulkan-docs/src/chapters/images.adoc) | Provides the specification context for cube-compatible views and sampled cube coordinates. |

## Questions / Risk Points for User Audit

- Is the distinction between rendering face 0 and sampling the four surrounding faces clear enough?
- Does the pass-0/pass-1 explanation avoid implying that the test registers two separate leaves?
- Is the red-zero/green-positive predicate clear despite the source shader using magenta and cyan rather than pure red and blue?

## Conversion Notes for Final Wiki Rewrite

- Use `write_face_0` as the sole registration leaf and describe the two internal passes as the behavior axis.
- Preserve the exact four cube-direction expressions, colors, 8 x 8 extent, six layers, and host predicate from the source.
- Include one compact fragment-shader walkthrough; do not invent coverage for unregistered faces, formats, or filtering modes.
- Explain the image barriers as part of the observable render-to-sample path and retain the source links for the pass loop and result check.
