## Overview

**Core question:** After rendering cubemap face 0, can a fragment shader sample four neighboring cube directions through a `samplerCube`, and does the final sampled image satisfy the source-defined red/green predicate?

- [`vktImageSampleDrawnCubeFaceTests.cpp`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L1) implements the single-leaf `image.sample_cubemap.write_face_0` family.
- The case creates an 8 x 8, six-layer `VK_FORMAT_R8G8B8A8_UNORM` cube-compatible image, renders face 0 twice with two colors, and runs a four-direction cube-sampling draw after each write.
- The page covers fixed resource setup, generated graphics shaders, the render-to-sample transitions, host readback, and the exact pass predicate.

## Background Knowledge

For the shared concepts image subresources, layouts, and synchronization, see [Background Knowledge](../../categories/image.md#background-knowledge) of the `image` page.

- **Cubemap sampling.** A cube-compatible image has six 2D array layers, and a cube image view exposes them to a `samplerCube`. A sampled direction selects one cube face from its dominant component and supplies coordinates on that face. This test forms four directions with a fixed `+Y`, `-Y`, `+Z`, or `-Z` component, then averages the samples.
- **Render-to-sample dependency.** The cubemap is written as a color attachment and subsequently read by a fragment shader. Render pass 1 transitions the attachment to `VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL`; the source then records an image barrier from color-attachment output to fragment shader execution, with both old and new layouts set to shader-read-only, before the sampling draw. The barrier uses `VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT` as its source access mask and `VK_ACCESS_INPUT_ATTACHMENT_READ_BIT` as its destination access mask.

## Registration Hierarchy

```text
image.sample_cubemap
└── write_face_0
```

[`createImageSampleDrawnCubeFaceTests()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L578-L587) creates `sample_cubemap` and adds the sole `write_face_0` test case.

## Parameter Dimensions and Observed Values

| Dimension | Registered or fixed value | Meaning in this test | Evidence |
|---|---|---|---|
| Test leaf | `write_face_0` | The only registered case; it renders through the full six-layer cube view and runs two internal write/sample iterations. | [factory](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L578-L587) |
| Format | `VK_FORMAT_R8G8B8A8_UNORM` | Selects the color-attachment, sampled-image, target-image, and host byte representation. | [factory](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L580-L585) |
| Extent | `8 x 8` | Sets the cubemap-face and target-image extent. | [factory](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L581-L585) |
| Cubemap layers and mip levels | six layers; one mip level | Creates the complete cube image and a base-level cube view. | [image setup](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L248-L281) |
| Write-pass color | pass 0: magenta `(1, 0, 1, 1)`; pass 1: cyan `(0, 1, 1, 1)` | Distinguishes the two writes to face 0. | [write fragment shader](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L528-L540) |
| Sample directions | `(u, +1, v)`, `(u, -1, v)`, `(u, v, +1)`, `(u, v, -1)` | Select the four cube directions averaged by the fragment shader. | [sampling fragment shader](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L552-L563) |
| Sampler state | linear min/mag filters, nearest mipmap mode, repeat addressing | Fixes the sampling configuration for the cube view. | [sampler setup](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L141-L164) |

There is no format, extent, face-index, filter, or sample-count registration matrix. The values above are fixed in the one registered case.

## Behavior Parameters

The primary behavior parameter is the **internal cubemap write/sample iteration**. It is not a separate registered path: `write_face_0` executes both values in one command buffer. The iteration changes the color rendered to face 0 while retaining the same cube-view, directions, target, and host predicate.

### `write_face_0` pass 0: first face-0 write

The write fragment shader receives push constant `pass == 0` and outputs magenta. The command buffer then transitions the cubemap for fragment sampling and draws the sampling pipeline into the target image.

### `write_face_0` pass 1: second face-0 write

After the source transitions the cubemap and target back to color-attachment layouts, `pass == 1` outputs cyan to face 0. The same barrier and sampling draw execute again. The target from this second iteration is copied to the result buffer and checked by the host.

## Shader Analysis

The representative shader is `frag2`, the sampling fragment shader used by the only registered leaf. The preceding write fragment shader supplies the pass-dependent face-0 color; this shader is the code that turns cube samples into the host-visible target image.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.image.sample_cubemap.write_face_0
```

| Parameter choice | Meaning in this representative case |
|---|---|
| `write_face_0` | Uses the fixed 8 x 8 cube-compatible image and two internal write/sample iterations. |
| `samplerCube` binding 0 | Reads the six-layer cubemap through the cube image view and linear sampler. |
| Four direction vectors | Samples directions with fixed `+Y`, `-Y`, `+Z`, and `-Z` components, with `u` and `v` from the vertex-provided texture coordinate. |

#### Purpose

For one target fragment, the shader samples the cubemap at four source-defined directions and writes their arithmetic mean. It makes cube-face direction selection, the sampler path, and the post-render image state observable through the target image readback.

#### Structural Design

| Phase | Shader action | Tested relationship |
|---|---|---|
| Input | Receives `fragTexCoord` from the second pipeline's vertex shader. | Supplies `u` and `v` to every cube direction. |
| First sample | Samples `(u, 1, v)`. | Exercises the `+Y` direction. |
| Remaining samples | Adds samples at `(u, -1, v)`, `(u, v, 1)`, and `(u, v, -1)`. | Exercises `-Y`, `+Z`, and `-Z` directions through the same cube view. |
| Average | Divides the accumulated color by four. | Produces the target color later copied to the host. |

#### Shader Code

```glsl
#version 450
layout(location = 0) out vec4 outColor;
layout(location = 1) in vec2 fragTexCoord;
layout(binding = 0) uniform samplerCube texSampler;

void main()
{
    outColor = texture(texSampler, vec3(fragTexCoord.x, 1.0, fragTexCoord.y));
    outColor += texture(texSampler, vec3(fragTexCoord.x, -1.0, fragTexCoord.y));
    outColor += texture(texSampler, vec3(fragTexCoord.x, fragTexCoord.y, 1.0));
    outColor += texture(texSampler, vec3(fragTexCoord.x, fragTexCoord.y, -1.0));
    outColor /= 4.;
}
```

#### Additional Info

- The source emits this GLSL directly in [`SampleDrawnCubeFaceTest::initPrograms()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L552-L568); it is not a reconstruction of a parameterized generator.
- The generated vertex shader passes the input UV unchanged. Its input buffer contains six vertices that cover the target framebuffer with two triangles.
- The shader uses implicit LOD sampling. The image has one mip level, and the sampler uses nearest mipmap selection.

#### Parameter Variation Summary

There are no registered shader variants in this file. Both internal passes use the same sampling shader; only the first pipeline's push constant changes its face-0 output color.

#### SPIR-V

- Status: generated and validated with `glslangValidator -V --target-env vulkan1.0`
- Source: the `frag2` GLSL emitted by `initPrograms()`
- Stage: `frag`
- Target SPIR-V version: `spirv1.0`

<details>
<summary>Click to expand SPIR-V assembly</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 62
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor %fragTexCoord
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %outColor "outColor"
               OpName %texSampler "texSampler"
               OpName %fragTexCoord "fragTexCoord"
               OpDecorate %outColor Location 0
               OpDecorate %texSampler Binding 0
               OpDecorate %texSampler DescriptorSet 0
               OpDecorate %fragTexCoord Location 1
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
         %10 = OpTypeImage %float Cube 0 0 0 1 Unknown
         %11 = OpTypeSampledImage %10
%_ptr_UniformConstant_11 = OpTypePointer UniformConstant %11
 %texSampler = OpVariable %_ptr_UniformConstant_11 UniformConstant
    %v2float = OpTypeVector %float 2
%_ptr_Input_v2float = OpTypePointer Input %v2float
%fragTexCoord = OpVariable %_ptr_Input_v2float Input
       %uint = OpTypeInt 32 0
     %uint_0 = OpConstant %uint 0
%_ptr_Input_float = OpTypePointer Input %float
    %float_1 = OpConstant %float 1
     %uint_1 = OpConstant %uint 1
    %v3float = OpTypeVector %float 3
   %float_n1 = OpConstant %float -1
    %float_4 = OpConstant %float 4
       %main = OpFunction %void None %3
          %5 = OpLabel
         %14 = OpLoad %11 %texSampler
         %21 = OpAccessChain %_ptr_Input_float %fragTexCoord %uint_0
         %22 = OpLoad %float %21
         %25 = OpAccessChain %_ptr_Input_float %fragTexCoord %uint_1
         %26 = OpLoad %float %25
         %28 = OpCompositeConstruct %v3float %22 %float_1 %26
         %29 = OpImageSampleImplicitLod %v4float %14 %28
               OpStore %outColor %29
         %30 = OpLoad %11 %texSampler
         %31 = OpAccessChain %_ptr_Input_float %fragTexCoord %uint_0
         %32 = OpLoad %float %31
         %34 = OpAccessChain %_ptr_Input_float %fragTexCoord %uint_1
         %35 = OpLoad %float %34
         %36 = OpCompositeConstruct %v3float %32 %float_n1 %35
         %37 = OpImageSampleImplicitLod %v4float %30 %36
         %38 = OpLoad %v4float %outColor
         %39 = OpFAdd %v4float %38 %37
               OpStore %outColor %39
         %40 = OpLoad %11 %texSampler
         %41 = OpAccessChain %_ptr_Input_float %fragTexCoord %uint_0
         %42 = OpLoad %float %41
         %43 = OpAccessChain %_ptr_Input_float %fragTexCoord %uint_1
         %44 = OpLoad %float %43
         %45 = OpCompositeConstruct %v3float %42 %44 %float_1
         %46 = OpImageSampleImplicitLod %v4float %40 %45
         %47 = OpLoad %v4float %outColor
         %48 = OpFAdd %v4float %47 %46
               OpStore %outColor %48
         %49 = OpLoad %11 %texSampler
         %50 = OpAccessChain %_ptr_Input_float %fragTexCoord %uint_0
         %51 = OpLoad %float %50
         %52 = OpAccessChain %_ptr_Input_float %fragTexCoord %uint_1
         %53 = OpLoad %float %52
         %54 = OpCompositeConstruct %v3float %51 %53 %float_n1
         %55 = OpImageSampleImplicitLod %v4float %49 %54
         %56 = OpLoad %v4float %outColor
         %57 = OpFAdd %v4float %56 %55
               OpStore %outColor %57
         %59 = OpLoad %v4float %outColor
         %60 = OpCompositeConstruct %v4float %float_4 %float_4 %float_4 %float_4
         %61 = OpFDiv %v4float %59 %60
               OpStore %outColor %61
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

[`SampleDrawnCubeFaceTestInstance::iterate()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L237-L495) performs the complete graphics sequence.

1. The host creates the cube-compatible image, a six-layer `VK_IMAGE_VIEW_TYPE_CUBE` view for the first framebuffer, a second cube view for the sampler descriptor, and an 8 x 8 2D target image/view. It also fills the full-screen position and UV vertex buffers.
2. The host creates `renderPass1`/pipeline 1 for the cubemap attachment and `renderPass2`/pipeline 2 for the target attachment. Pipeline 1 has a fragment-stage push constant; pipeline 2 has the combined image-sampler descriptor set.
3. `clearColorImage()` initializes every cubemap layer and the target image to black. The command buffer then binds the sampling descriptor set once.
4. For each `pass` value from 0 through 1, the command buffer pushes the pass value, draws pipeline 1 into the cube view, records a barrier from color-attachment output to fragment-shader execution (source access `COLOR_ATTACHMENT_WRITE`, destination access `INPUT_ATTACHMENT_READ`), binds pipeline 2, and draws the sampling quad into the target image.
5. After pass 0, the source records barriers that return the cubemap from shader-read-only to color-attachment layout and the target from transfer-source to color-attachment layout. Pass 1 then repeats the write, barrier, and sample draw.
6. The target image is copied to the host-visible result buffer. After command completion and allocation invalidation, the source copies the bytes into a `TextureLevel` and checks the rightmost pixel of every row.

The pass condition is exactly:

```text
val[0] == 0 && val[1] > 0
```

Here `val[0]` and `val[1]` are the red and green bytes of the copied `R8G8B8A8_UNORM` result. The source logs the complete target image whether the predicate passes or fails.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `write_face_0` pass 0 | Face-0 render setup, cubemap view/layer selection, the first render-to-sample barrier, cube-face selection, surrounding-face sampling, or target-image write. |
| `write_face_0` pass 1 | Reuse of the cubemap and target after the first iteration, the second render-to-sample barrier, face-0 rewrite, cube-face sampling, or final result handling. |

### Cause Analysis

#### Cubemap image, view, or sampled direction

**Possible failure symptoms:** The copied target contains a nonzero red byte, lacks a positive green byte, or shows a spatial pattern inconsistent with the logged image.

**Possible implementation causes:** The cube-compatible image or its six-layer view can be interpreted incorrectly; the sampled cube view can select a wrong face or map the generated directions incorrectly. A defect in linear cube sampling or edge handling can also change the four-sample average. The test does not isolate individual directions in separate result channels, so one failure covers the combined four-sample expression.

#### Face-0 rendering and iteration reuse

**Possible failure symptoms:** The final target does not meet the predicate even when the first iteration appears plausible, or failure appears tied to the transition between the two internal iterations.

**Possible implementation causes:** Pipeline 1 can render the wrong push-constant color, attach the wrong cube layer/view interpretation, or fail to overwrite the intended face on the second draw. The source also reuses both cubemap and target after pass 0, so incorrect layout restoration or attachment reuse can affect pass 1.

#### Render-to-sample visibility or layout transitions

**Possible failure symptoms:** The target reads stale, cleared, or otherwise unavailable cubemap data, potentially across many pixels.

**Possible implementation causes:** The color-attachment write may not become visible to the fragment shader, or the cubemap may not be used in the intended shader-read-only layout. The post-pass-0 barriers can likewise leave the cubemap or target in an incorrect layout for the next draw. These causes include the source's image barriers and render-pass attachment layout handling.

#### Target write, copyback, or host byte interpretation

**Possible failure symptoms:** The rendered-image log looks expected while the copied bytes fail, or all rows fail the same predicate unexpectedly.

**Possible implementation causes:** Pipeline 2 can write an incorrect target value, the transfer readback can copy or synchronize the wrong contents, or the host-visible allocation can expose stale data. The source copies only after the second target render pass and invalidates the allocation before the byte scan, so this path includes target layout, transfer, and host visibility behavior.

## Case Pruning

### Requirement-based pruning

The source contains no explicit `checkSupport()` method or extension/feature gate. It relies on the baseline graphics, cube-image-view, color-attachment, sampled-image, transfer, and `VK_FORMAT_R8G8B8A8_UNORM` capabilities used by the implementation.

### Design-based pruning

- Only face 0 is rendered; the source does not register a leaf for another write face.
- Only the four directions with fixed `+Y`, `-Y`, `+Z`, and `-Z` components are sampled.
- The test fixes one format, one small extent, one mip level, one sample, one sampler configuration, and one graphics queue.
- The pass predicate examines red and green only; blue and alpha are logged but do not independently decide pass or fail.

## Key Takeaways

- `image.sample_cubemap.write_face_0` is a single graphics test case with two internal face-0 write/sample iterations, not two registered leaves.
- The generated `samplerCube` fragment shader averages four explicit cube-direction samples into a separate 2D target image.
- The test makes the render-to-sample path observable through a source-defined host predicate: the red byte at the final rightmost pixel of every row must be zero and the green byte must be positive.
- A mismatch can arise from cube-face selection, rendering, synchronization/layout handling, target rendering, readback, or host visibility; the compact test does not individually diagnose those components.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Cube-image creation helper | [`makeImageCreateInfo()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L71-L96) | Defines the cube-compatible image, six-layer allocation, one mip level, format input, and attachment/sampling/transfer usages. |
| Sampler configuration | [`makeSampler()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L141-L165) | Fixes linear minification and magnification filters, nearest mipmap mode, and repeat addressing. |
| Resource, descriptor, and pipeline setup | [`SampleDrawnCubeFaceTestInstance::iterate()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L237-L403) | Creates the cube and target images/views, vertex buffers, combined image-sampler descriptor, render passes, graphics pipelines, result buffer, and initial clears. |
| Command recording and transitions | [`iterate()` pass loop](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L405-L463) | Records both face-0 draws, the cube image barriers, target sampling draws, inter-pass layout restoration, copyback, and submission. |
| Host predicate and attachment log | [`iterate()` result validation](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L465-L494) | Defines allocation invalidation, the rightmost-pixel red/green byte scan, image logging, and the CTS pass/fail result. |
| Generated GLSL programs | [`SampleDrawnCubeFaceTest::initPrograms()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L519-L569) | Emits the pass-dependent write shader and the four-direction `samplerCube` fragment shader. |
| Test registration | [`createImageSampleDrawnCubeFaceTests()`](../../../modules/vulkan/image/vktImageSampleDrawnCubeFaceTests.cpp#L578-L587) | Registers the `sample_cubemap.write_face_0` hierarchy with its fixed format and extent. |
| Cube-sampling specification context | [Vulkan image operations](../../../../vulkan-docs/src/chapters/images.adoc) | Defines the specification context for cube-compatible image views and cube-coordinate sampling. |
