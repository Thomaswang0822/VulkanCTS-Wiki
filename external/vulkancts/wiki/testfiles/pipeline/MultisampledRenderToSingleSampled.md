## Overview

**Core question:** Does `VK_EXT_multisampled_render_to_single_sampled` produce the expected single-sampled color, depth, and stencil results when the implementation renders with multiple samples?

This test family documents `pipeline.monolithic.multisample.multisampled_render_to_single_sampled`. Its direct children are intermediate nodes that select a rendering scenario: basic rendering, clears, pass sequencing, input attachments, a query, or dynamic rendering. The same source also registers the parallel `pipeline.monolithic.multisample.misc` test family, which uses the shared machinery without enabling the extension path.

For rendering cases, the implementation creates single-sampled images with `VK_IMAGE_CREATE_MULTISAMPLED_RENDER_TO_SINGLE_SAMPLED_BIT_EXT` when `isMultisampledRenderToSingleSampled` is enabled. It renders sample-distinct values, exposes the single-sampled result through image views, and uses compute shaders plus host readback to determine pass or fail. The query subgroup is an exception: it only validates the value returned through a chained format-properties query.

The default mustpass scope contains 4,288 leaves under the monolithic root, 4,288 under `pipeline.fast_linked_library`, and 1,520 under `pipeline.shader_object_unlinked_spirv`. Each count uses the literal `multisampled_render_to_single_sampled` path component in the corresponding file.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- Multisampled render to single-sampled rendering changes attachment rendering behavior while the application owns a single-sampled image. The image requires `VK_IMAGE_CREATE_MULTISAMPLED_RENDER_TO_SINGLE_SAMPLED_BIT_EXT`; the render pass or dynamic-rendering state supplies the multisample information. See [the Vulkan pipeline requirements](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3036-L3048).
- A resolve mode selects one single-sampled value from multiple samples. The generated shaders make sample values differ, so `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` and modes such as `VK_RESOLVE_MODE_MAX_BIT` can be observed through the resulting attachment. See [multisample and resolve operations](../../../../vulkan-docs/src/chapters/fragops.adoc#L2530-L2545).
- Color, depth, and stencil results use different representations. The checker therefore uses floating-point tolerances where required and exact comparisons for integer and stencil values.

## Registration Hierarchy

```text
pipeline.monolithic.multisample.multisampled_render_to_single_sampled
├── basic
├── clear_attachments
├── multi_subpass
├── multi_renderpass
├── input_attachments
├── subpass_resolve_efficiency_query
└── dynamic_rendering
```

[`createMultisampledRenderToSingleSampledTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6099-L6105) supplies this test family. [`createMultisampledRenderToSingleSampledTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6067-L6080) omits the non-dynamic path for shader-object construction types, because shader objects require dynamic rendering. The separate [`createMultisampledMiscTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6107-L6111) registers `pipeline.monolithic.multisample.misc`; it is a separate test family and does not appear in this canonical tree.

## Parameter Dimensions and Observed Values

| Dimension | Representative values | Observed effect |
|---|---|---|
| Color and depth/stencil formats | floating-point color, signed or unsigned integer color, depth-only, stencil-only, combined depth/stencil | Selects attachment views and the appropriate verification comparison |
| Sample count | 2, 4, 8, 16 | Selects the number of sample-distinct fragment outputs |
| Resolve mode | `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT`, `VK_RESOLVE_MODE_MAX_BIT` | Selects the expected depth/stencil resolve value; color resolve behavior is fixed by the attachment setup |
| Render area | whole framebuffer or partial area | Partial cases also verify pixels outside the rendered area |
| Attachment memory | default, Android Hardware Buffer color, Android Hardware Buffer depth/stencil | Exercises allocation and image binding variants |
| Pipeline construction type | monolithic, fast linked library, shader-object variants | Changes registered paths and restricts shader-object cases to dynamic rendering |
| Rendering form | render pass or dynamic rendering | Changes attachment setup while retaining the target behavior |
| Input attachment form | color, depth, or stencil input types | Selects the later attachment access scenario |

The generator initializes `TestParams` with attachment formats, sample counts, clear values, per-pass configuration, render-area state, memory type, and the construction type. [`makeImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L440-L466) applies the MSRTSS image-create flag only when the image is single-sampled and the extension path is enabled. AHB memory variants are generated by `basic`; the other generated scenarios use the default image-memory path.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node under `pipeline.monolithic.multisample.multisampled_render_to_single_sampled`.

### basic: Sample-distinct rendering and resolve

The generator draws a fullscreen triangle and uses sample-dependent floating-point and integer color outputs plus sample-dependent depth. Stencil is checked when present, but this basic fragment shader does not write a per-sample stencil output; the expected stencil value comes from the test's stencil setup. It verifies that the resulting attachments match the selected sample count and depth/stencil resolve mode.

### clear_attachments: Clears in an MSRTSS attachment setup

The test calls `vkCmdClearAttachments` in the configured rendering path, then verifies the affected attachment values.

### multi_subpass: MSRTSS across subpasses

The test uses one render pass with multiple subpasses. It checks attachment state and results across subpass boundaries. This intermediate node requires render-pass rendering.

### multi_renderpass: MSRTSS across rendering sequences

The test distributes work over multiple rendering sequences, checking that attachment contents and transitions remain valid between passes. The non-dynamic form uses multiple render-pass instances; the dynamic form uses multiple dynamic-rendering instances.

### input_attachments: Read rendered values as input attachments

The test renders multisampled data, then accesses it through input attachments. Dynamic rendering and shader objects do not cover this intermediate node.

### subpass_resolve_efficiency_query: Resolve query reporting

This path runs only for the extension path, monolithic construction, and non-dynamic render-pass construction. For each format in the generated attachment-format ranges, it chains `VkSubpassResolvePerformanceQueryEXT` to `vkGetPhysicalDeviceFormatProperties2` and checks that `optimal` is populated with a valid Vulkan boolean.

### dynamic_rendering: MSRTSS without a render-pass object

This path repeats supported scenarios with dynamic-rendering attachment state. Non-monolithic construction types add `garbage_color_attachment`, which probes dynamic attachment handling when a color attachment contains deliberately unusable data.

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.fast_linked_library.multisample.multisampled_render_to_single_sampled.basic.r8g8b8a8_unorm_r16g16b16a16_sfloat_r16g16b16a16_sint_d16_unorm.16x.ds_resolve_max.sub_framebuffer.ahb_color
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `basic` | Uses the one-pass sample-distinct rendering generator and its gradient verifier. |
| `r8g8b8a8_unorm`, `r16g16b16a16_sfloat`, `r16g16b16a16_sint`, `d16_unorm` | Enables two floating-point color outputs, one signed-integer color output, and a depth attachment; stencil is absent for this exact path. |
| `16x` | The graphics pipeline runs the fragment shader for 16 samples, while the MSRTSS images themselves are single-sampled. |
| `ds_resolve_max` | Selects `VK_RESOLVE_MODE_MAX_BIT` for depth/stencil resolve; the verifier therefore expects depth `1.0`. |
| `sub_framebuffer`, `ahb_color`, `fast_linked_library` | Renders only a configured subregion, uses Android Hardware Buffer color-image allocation, and exercises the fast-linked-library construction path. |

#### Purpose

This generated shader pair makes per-sample rendering observable after multisampled render-to-single-sampled conversion. The fragment shader encodes sample identity into color and depth, while the compute verifier checks the resulting single-sampled attachments and records per-pixel diagnostics.

#### Structural Design

| Stage | Dataflow |
|-------|----------|
| Vertex | The fullscreen-triangle vertex position is copied directly into `gl_Position`. |
| Fragment input | `gl_FragCoord` and push-constant `area` form normalized horizontal/vertical coordinates; `gl_SampleID` selects one of 16 generated output branches. |
| Fragment outputs | Two `vec4` attachments receive sample-specific gradients, the signed `ivec4` attachment receives sample-specific integer vectors, and `gl_FragDepth` alternates between `1.0` and `0.9375`. |
| Attachment observation | The compute shader fetches the resolved color/depth images, accepts the expected horizontal or vertical integer gradient with source-defined tolerances, atomically counts matches, and writes green/red status layers to `verify`. |

#### Shader Code

##### Vertex Shader

```glsl
#version 450

/// Location 0 is the host-provided fullscreen-triangle position. No varying is needed because the fragment shader derives its gradient from gl_FragCoord.
layout(location = 0) in vec4 in_position;

/// The generated vertex stage writes only the required position built-in.
out gl_PerVertex {
    vec4 gl_Position;
};

void main(void)
{
    gl_Position = in_position;
}
```

##### Fragment Shader

```glsl
#version 450

/// Locations 0 and 1 are the two floating-point color attachments; location 2 is the signed R16G16B16A16_SINT attachment.
layout(location = 0) out vec4 o_color1;
layout(location = 1) out vec4 o_color2;
layout(location = 2) out ivec4 o_color3;

/// The host pushes render-area origin and extent. The fragment stage uses them to normalize its two gradient axes.
layout(push_constant) uniform PushConstants {
    uvec4 area;
} params;

void main(void)
{
    vec2 uv = (gl_FragCoord.xy - vec2(params.area.xy)) / vec2(params.area.zw);
    if (gl_SampleID == 0)
    {
        o_color1 = vec4(0, 1, 1, 1) * uv.x;
        o_color2 = vec4(0, 1, 1, 1) * uv.x;
        o_color3 = ivec4(vec4(10, 11, 12, 13) * uv.x);
        gl_FragDepth = 1;
    }
    else if (gl_SampleID == 1)
    {
        o_color1 = vec4(1, 0, 1, 1) * uv.y;
        o_color2 = vec4(1, 0, 1, 1) * uv.y;
        o_color3 = ivec4(vec4(40, 41, 42, 43) * uv.y);
        gl_FragDepth = 0.9375;
    }
    else if (gl_SampleID == 2)
    {
        o_color1 = vec4(1, 1, 0, 1) * uv.x;
        o_color2 = vec4(1, 1, 0, 1) * uv.x;
        o_color3 = ivec4(vec4(90, 91, 92, 93) * uv.x);
        gl_FragDepth = 1;
    }
    else if (gl_SampleID == 3)
    {
        o_color1 = vec4(1, 1, 1, 0) * uv.y;
        o_color2 = vec4(1, 1, 1, 0) * uv.y;
        o_color3 = ivec4(vec4(160, 161, 162, 163) * uv.y);
        gl_FragDepth = 0.9375;
    }
    else if (gl_SampleID == 4)
    {
        o_color1 = vec4(0, 0.8, 0.8, 0.8) * uv.x;
        o_color2 = vec4(0, 0.8, 0.8, 0.8) * uv.x;
        o_color3 = ivec4(vec4(250, 251, 252, 253) * uv.x);
        gl_FragDepth = 1;
    }
    else if (gl_SampleID == 5)
    {
        o_color1 = vec4(0.8, 0, 0.8, 0.8) * uv.y;
        o_color2 = vec4(0.8, 0, 0.8, 0.8) * uv.y;
        o_color3 = ivec4(vec4(360, 361, 362, 363) * uv.y);
        gl_FragDepth = 0.9375;
    }
    else if (gl_SampleID == 6)
    {
        o_color1 = vec4(0.8, 0.8, 0, 0.8) * uv.x;
        o_color2 = vec4(0.8, 0.8, 0, 0.8) * uv.x;
        o_color3 = ivec4(vec4(490, 491, 492, 493) * uv.x);
        gl_FragDepth = 1;
    }
    else if (gl_SampleID == 7)
    {
        o_color1 = vec4(0.8, 0.8, 0.8, 0) * uv.y;
        o_color2 = vec4(0.8, 0.8, 0.8, 0) * uv.y;
        o_color3 = ivec4(vec4(640, 641, 642, 643) * uv.y);
        gl_FragDepth = 0.9375;
    }
    else if (gl_SampleID == 8)
    {
        o_color1 = vec4(0.6, 0.6, 0.6, 0.6) * uv.x;
        o_color2 = vec4(0.6, 0.6, 0.6, 0.6) * uv.x;
        o_color3 = ivec4(vec4(810, 811, 812, 813) * uv.x);
        gl_FragDepth = 1;
    }
    else if (gl_SampleID == 9)
    {
        o_color1 = vec4(0.6, 0, 0.6, 0.6) * uv.y;
        o_color2 = vec4(0.6, 0, 0.6, 0.6) * uv.y;
        o_color3 = ivec4(vec4(1000, 1001, 1002, 1003) * uv.y);
        gl_FragDepth = 0.9375;
    }
    else if (gl_SampleID == 10)
    {
        o_color1 = vec4(0.6, 0.6, 0, 0.6) * uv.x;
        o_color2 = vec4(0.6, 0.6, 0, 0.6) * uv.x;
        o_color3 = ivec4(vec4(1210, 1211, 1212, 1213) * uv.x);
        gl_FragDepth = 1;
    }
    else if (gl_SampleID == 11)
    {
        o_color1 = vec4(0.6, 0.6, 0.6, 0) * uv.y;
        o_color2 = vec4(0.6, 0.6, 0.6, 0) * uv.y;
        o_color3 = ivec4(vec4(1440, 1441, 1442, 1443) * uv.y);
        gl_FragDepth = 0.9375;
    }
    else if (gl_SampleID == 12)
    {
        o_color1 = vec4(0.4, 0.4, 0.4, 0.4) * uv.x;
        o_color2 = vec4(0.4, 0.4, 0.4, 0.4) * uv.x;
        o_color3 = ivec4(vec4(1690, 1691, 1692, 1693) * uv.x);
        gl_FragDepth = 1;
    }
    else if (gl_SampleID == 13)
    {
        o_color1 = vec4(0.4, 0, 0.4, 0.4) * uv.y;
        o_color2 = vec4(0.4, 0, 0.4, 0.4) * uv.y;
        o_color3 = ivec4(vec4(1960, 1961, 1962, 1963) * uv.y);
        gl_FragDepth = 0.9375;
    }
    else if (gl_SampleID == 14)
    {
        o_color1 = vec4(0.4, 0.4, 0, 0.4) * uv.x;
        o_color2 = vec4(0.4, 0.4, 0, 0.4) * uv.x;
        o_color3 = ivec4(vec4(2250, 2251, 2252, 2253) * uv.x);
        gl_FragDepth = 1;
    }
    else if (gl_SampleID == 15)
    {
        o_color1 = vec4(0.4, 0.4, 0.4, 0) * uv.y;
        o_color2 = vec4(0.4, 0.4, 0.4, 0) * uv.y;
        o_color3 = ivec4(vec4(2560, 2561, 2562, 2563) * uv.y);
        gl_FragDepth = 0.9375;
    }
}
```

##### Compute Shader

```glsl
#version 450
#extension GL_EXT_samplerless_texture_functions : require

layout(push_constant) uniform PushConstants {
    uvec4 area;
    uint stencilExpect;
} params;

layout(local_size_x = 8, local_size_y = 8) in;

layout(set = 0, binding = 0, std430) writeonly buffer Output {
    uint colorVerification[3];
    uint depthVerification;
    uint stencilVerification;
} sb_out;
layout(set = 0, binding = 1) uniform texture2D color1Image;
layout(set = 0, binding = 2) uniform texture2D color2Image;
layout(set = 0, binding = 3) uniform itexture2D color3Image;
layout(set = 0, binding = 4) uniform texture2D depthImage;
layout(set = 0, binding = 6, rgba8) uniform writeonly image2DArray verify;

bool fmatches(float a, float b, float error)
{
    return abs(a - b) < error;
}

bool v4matches(vec4 a, vec4 b, vec4 error)
{
    return all(lessThan(abs(a - b), error));
}

bool i4matchesEither(ivec4 a, ivec4 b, ivec4 c, int errorB, int errorC)
{
    return all(lessThanEqual(abs(a - b), ivec4(errorB))) ||
           all(lessThanEqual(abs(a - c), ivec4(errorC)));
}

void main(void)
{
    if (any(greaterThanEqual(gl_GlobalInvocationID.xy, params.area.zw)))
        return;

    uvec2 coords = params.area.xy + gl_GlobalInvocationID.xy;
    vec2 uv = (vec2(gl_GlobalInvocationID.xy) + vec2(0.5)) / vec2(params.area.zw);

    vec4 result1 = vec4(1, 0, 0, 1);
    vec4 color1 = texelFetch(color1Image, ivec2(coords), 0);
    vec4 expected1H = vec4(0.35, 0.7, 0.35, 0.7);
    vec4 expected1V = vec4(0.7, 0.35, 0.7, 0.35);
    vec4 expected1 = (expected1H * uv.x + expected1V * uv.y) / 2.0;
    if (v4matches(color1, expected1,
                  max(expected1H / float(params.area.z), expected1V / float(params.area.w)) + 2.0/255.0))
    {
        atomicAdd(sb_out.colorVerification[0], 1);
        result1 = vec4(0, 1, 0, 1);
    }
    imageStore(verify, ivec3(coords, 0), result1);

    vec4 result2 = vec4(1, 0, 0, 1);
    vec4 color2 = texelFetch(color2Image, ivec2(coords), 0);
    if (v4matches(color2, expected1,
                  max(expected1H / float(params.area.z), expected1V / float(params.area.w)) + 2.0/1024.0))
    {
        atomicAdd(sb_out.colorVerification[1], 1);
        result2 = vec4(0, 1, 0, 1);
    }
    imageStore(verify, ivec3(coords, 1), result2);

    vec4 result3 = vec4(1, 0, 0, 1);
    ivec4 color3 = texelFetch(color3Image, ivec2(coords), 0);
    if (i4matchesEither(color3, ivec4(vec4(10, 11, 12, 13) * uv.x), ivec4(vec4(10, 11, 12, 13) * uv.y), 10 / int(params.area.z) + 1, 10 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(40, 41, 42, 43) * uv.x), ivec4(vec4(40, 41, 42, 43) * uv.y), 40 / int(params.area.z) + 1, 40 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(90, 91, 92, 93) * uv.x), ivec4(vec4(90, 91, 92, 93) * uv.y), 90 / int(params.area.z) + 1, 90 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(160, 161, 162, 163) * uv.x), ivec4(vec4(160, 161, 162, 163) * uv.y), 160 / int(params.area.z) + 1, 160 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(250, 251, 252, 253) * uv.x), ivec4(vec4(250, 251, 252, 253) * uv.y), 250 / int(params.area.z) + 1, 250 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(360, 361, 362, 363) * uv.x), ivec4(vec4(360, 361, 362, 363) * uv.y), 360 / int(params.area.z) + 1, 360 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(490, 491, 492, 493) * uv.x), ivec4(vec4(490, 491, 492, 493) * uv.y), 490 / int(params.area.z) + 1, 490 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(640, 641, 642, 643) * uv.x), ivec4(vec4(640, 641, 642, 643) * uv.y), 640 / int(params.area.z) + 1, 640 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(810, 811, 812, 813) * uv.x), ivec4(vec4(810, 811, 812, 813) * uv.y), 810 / int(params.area.z) + 1, 810 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(1000, 1001, 1002, 1003) * uv.x), ivec4(vec4(1000, 1001, 1002, 1003) * uv.y), 1000 / int(params.area.z) + 1, 1000 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(1210, 1211, 1212, 1213) * uv.x), ivec4(vec4(1210, 1211, 1212, 1213) * uv.y), 1210 / int(params.area.z) + 1, 1210 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(1440, 1441, 1442, 1443) * uv.x), ivec4(vec4(1440, 1441, 1442, 1443) * uv.y), 1440 / int(params.area.z) + 1, 1440 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(1690, 1691, 1692, 1693) * uv.x), ivec4(vec4(1690, 1691, 1692, 1693) * uv.y), 1690 / int(params.area.z) + 1, 1690 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(1960, 1961, 1962, 1963) * uv.x), ivec4(vec4(1960, 1961, 1962, 1963) * uv.y), 1960 / int(params.area.z) + 1, 1960 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(2250, 2251, 2252, 2253) * uv.x), ivec4(vec4(2250, 2251, 2252, 2253) * uv.y), 2250 / int(params.area.z) + 1, 2250 / int(params.area.w) + 1) ||
        i4matchesEither(color3, ivec4(vec4(2560, 2561, 2562, 2563) * uv.x), ivec4(vec4(2560, 2561, 2562, 2563) * uv.y), 2560 / int(params.area.z) + 1, 2560 / int(params.area.w) + 1))
    {
        atomicAdd(sb_out.colorVerification[2], 1);
        result3 = vec4(0, 1, 0, 1);
    }
    imageStore(verify, ivec3(coords, 2), result3);

    vec4 resultDepth = vec4(1, 0, 0, 1);
    float depth = texelFetch(depthImage, ivec2(coords), 0).r;
    if (fmatches(depth, 1.0, 0.01))
    {
        atomicAdd(sb_out.depthVerification, 1);
        resultDepth = vec4(0, 1, 0, 1);
    }
    imageStore(verify, ivec3(coords, 3), resultDepth);
}
```

The compute verifier is generated from the same `initBasicPrograms` branch as the selected 16-sample signed-integer/depth case. It samples the resolved attachments, compares the float and integer gradients with source-defined tolerances, atomically accumulates verification counts, and writes per-aspect diagnostics to the `verify` image.

#### Additional Info

- `initBasicPrograms` emits the fragment branch for each `sampleID` from `0` through `numSamples - 1`; this representative therefore has 16 branches. The compute verifier emits one integer-gradient alternative per generated sample, even though the compact code block above shows the common helper/dataflow rather than every repeated alternative.
- The MSRTSS distinction is host/pipeline state, not a shader declaration: `generateBasicTest` sets all four image sample counts to `VK_SAMPLE_COUNT_1_BIT` and disables resolve attachments when the extension path is enabled, while retaining `perPass.numSamples = 16` for the graphics pipeline.
- The exact case has `r16g16b16a16_sint`, so the generated integer output and verifier use signed `ivec4`/`itexture2D`; depth is present and stencil is not.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Sample count | Changes `perPass.numSamples`, the number of `gl_SampleID` branches, sample-specific integer vectors, and the generated expected-value alternatives; `numSamples` is 2, 4, 8, or 16. | [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3028-L3096) |
| Integer color format | Selects `ivec4`/`itexture2D` for `VK_FORMAT_R16G16B16A16_SINT` or unsigned counterparts for the unsigned format. | [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3028-L3030), [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3153-L3156) |
| Depth/stencil format | Conditionally emits depth and/or stencil descriptors and verification code; depth expected value depends on `VK_RESOLVE_MODE_SAMPLE_ZERO_BIT` versus other modes. | [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3157-L3160), [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3239-L3262) |
| Render area | Push-constant origin/extent changes `uv`, dispatch bounds, and tolerance terms; the shader returns for invocations outside the configured area. | [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3181-L3187) |
| MSRTSS versus ordinary multisampling | Does not change GLSL text; host generation changes image sample counts and resolve attachment setup while retaining the graphics sample count. | [`generateBasicTest`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3455-L3482) |

#### SPIR-V

##### Vertex Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 18
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %_ %in_position
               OpSource GLSL 450
               OpName %main "main"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpName %_ ""
               OpName %in_position "in_position"
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpDecorate %in_position Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%gl_PerVertex = OpTypeStruct %v4float
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_Input_v4float = OpTypePointer Input %v4float
%in_position = OpVariable %_ptr_Input_v4float Input
%_ptr_Output_v4float = OpTypePointer Output %v4float
       %main = OpFunction %void None %3
          %5 = OpLabel
         %15 = OpLoad %v4float %in_position
         %17 = OpAccessChain %_ptr_Output_v4float %_ %int_0
               OpStore %17 %15
               OpReturn
               OpFunctionEnd
```

</details>

##### Fragment Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `frag`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 404
; Schema: 0
               OpCapability Shader
               OpCapability SampleRateShading
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %gl_FragCoord %gl_SampleID %o_color1 %o_color2 %o_color3 %gl_FragDepth
               OpExecutionMode %main OriginUpperLeft
               OpExecutionMode %main DepthReplacing
               OpSource GLSL 450
               OpName %main "main"
               OpName %uv "uv"
               OpName %gl_FragCoord "gl_FragCoord"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "area"
               OpName %params "params"
               OpName %gl_SampleID "gl_SampleID"
               OpName %o_color1 "o_color1"
               OpName %o_color2 "o_color2"
               OpName %o_color3 "o_color3"
               OpName %gl_FragDepth "gl_FragDepth"
               OpDecorate %gl_FragCoord BuiltIn FragCoord
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpDecorate %gl_SampleID BuiltIn SampleId
               OpDecorate %gl_SampleID Flat
               OpDecorate %o_color1 Location 0
               OpDecorate %o_color2 Location 1
               OpDecorate %o_color3 Location 2
               OpDecorate %gl_FragDepth BuiltIn FragDepth
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
%gl_FragCoord = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %v4uint = OpTypeVector %uint 4
%PushConstants = OpTypeStruct %v4uint
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
     %params = OpVariable %_ptr_PushConstant_PushConstants PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
     %v2uint = OpTypeVector %uint 2
%_ptr_PushConstant_v4uint = OpTypePointer PushConstant %v4uint
%_ptr_Input_int = OpTypePointer Input %int
%gl_SampleID = OpVariable %_ptr_Input_int Input
       %bool = OpTypeBool
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %o_color1 = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %45 = OpConstantComposite %v4float %float_0 %float_1 %float_1 %float_1
     %uint_0 = OpConstant %uint 0
%_ptr_Function_float = OpTypePointer Function %float
   %o_color2 = OpVariable %_ptr_Output_v4float Output
      %v4int = OpTypeVector %int 4
%_ptr_Output_v4int = OpTypePointer Output %v4int
   %o_color3 = OpVariable %_ptr_Output_v4int Output
   %float_10 = OpConstant %float 10
   %float_11 = OpConstant %float 11
   %float_12 = OpConstant %float 12
   %float_13 = OpConstant %float 13
         %62 = OpConstantComposite %v4float %float_10 %float_11 %float_12 %float_13
%_ptr_Output_float = OpTypePointer Output %float
%gl_FragDepth = OpVariable %_ptr_Output_float Output
      %int_1 = OpConstant %int 1
         %75 = OpConstantComposite %v4float %float_1 %float_0 %float_1 %float_1
     %uint_1 = OpConstant %uint 1
   %float_40 = OpConstant %float 40
   %float_41 = OpConstant %float 41
   %float_42 = OpConstant %float 42
   %float_43 = OpConstant %float 43
         %87 = OpConstantComposite %v4float %float_40 %float_41 %float_42 %float_43
%float_0_9375 = OpConstant %float 0.9375
      %int_2 = OpConstant %int 2
         %99 = OpConstantComposite %v4float %float_1 %float_1 %float_0 %float_1
   %float_90 = OpConstant %float 90
   %float_91 = OpConstant %float 91
   %float_92 = OpConstant %float 92
   %float_93 = OpConstant %float 93
        %110 = OpConstantComposite %v4float %float_90 %float_91 %float_92 %float_93
      %int_3 = OpConstant %int 3
        %121 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_0
  %float_160 = OpConstant %float 160
  %float_161 = OpConstant %float 161
  %float_162 = OpConstant %float 162
  %float_163 = OpConstant %float 163
        %132 = OpConstantComposite %v4float %float_160 %float_161 %float_162 %float_163
      %int_4 = OpConstant %int 4
%float_0_800000012 = OpConstant %float 0.800000012
        %144 = OpConstantComposite %v4float %float_0 %float_0_800000012 %float_0_800000012 %float_0_800000012
  %float_250 = OpConstant %float 250
  %float_251 = OpConstant %float 251
  %float_252 = OpConstant %float 252
  %float_253 = OpConstant %float 253
        %155 = OpConstantComposite %v4float %float_250 %float_251 %float_252 %float_253
      %int_5 = OpConstant %int 5
        %166 = OpConstantComposite %v4float %float_0_800000012 %float_0 %float_0_800000012 %float_0_800000012
  %float_360 = OpConstant %float 360
  %float_361 = OpConstant %float 361
  %float_362 = OpConstant %float 362
  %float_363 = OpConstant %float 363
        %177 = OpConstantComposite %v4float %float_360 %float_361 %float_362 %float_363
      %int_6 = OpConstant %int 6
        %188 = OpConstantComposite %v4float %float_0_800000012 %float_0_800000012 %float_0 %float_0_800000012
  %float_490 = OpConstant %float 490
  %float_491 = OpConstant %float 491
  %float_492 = OpConstant %float 492
  %float_493 = OpConstant %float 493
        %199 = OpConstantComposite %v4float %float_490 %float_491 %float_492 %float_493
      %int_7 = OpConstant %int 7
        %210 = OpConstantComposite %v4float %float_0_800000012 %float_0_800000012 %float_0_800000012 %float_0
  %float_640 = OpConstant %float 640
  %float_641 = OpConstant %float 641
  %float_642 = OpConstant %float 642
  %float_643 = OpConstant %float 643
        %221 = OpConstantComposite %v4float %float_640 %float_641 %float_642 %float_643
      %int_8 = OpConstant %int 8
%float_0_600000024 = OpConstant %float 0.600000024
        %233 = OpConstantComposite %v4float %float_0 %float_0_600000024 %float_0_600000024 %float_0_600000024
  %float_810 = OpConstant %float 810
  %float_811 = OpConstant %float 811
  %float_812 = OpConstant %float 812
  %float_813 = OpConstant %float 813
        %244 = OpConstantComposite %v4float %float_810 %float_811 %float_812 %float_813
      %int_9 = OpConstant %int 9
        %255 = OpConstantComposite %v4float %float_0_600000024 %float_0 %float_0_600000024 %float_0_600000024
 %float_1000 = OpConstant %float 1000
 %float_1001 = OpConstant %float 1001
 %float_1002 = OpConstant %float 1002
 %float_1003 = OpConstant %float 1003
        %266 = OpConstantComposite %v4float %float_1000 %float_1001 %float_1002 %float_1003
     %int_10 = OpConstant %int 10
        %277 = OpConstantComposite %v4float %float_0_600000024 %float_0_600000024 %float_0 %float_0_600000024
 %float_1210 = OpConstant %float 1210
 %float_1211 = OpConstant %float 1211
 %float_1212 = OpConstant %float 1212
 %float_1213 = OpConstant %float 1213
        %288 = OpConstantComposite %v4float %float_1210 %float_1211 %float_1212 %float_1213
     %int_11 = OpConstant %int 11
        %299 = OpConstantComposite %v4float %float_0_600000024 %float_0_600000024 %float_0_600000024 %float_0
 %float_1440 = OpConstant %float 1440
 %float_1441 = OpConstant %float 1441
 %float_1442 = OpConstant %float 1442
 %float_1443 = OpConstant %float 1443
        %310 = OpConstantComposite %v4float %float_1440 %float_1441 %float_1442 %float_1443
     %int_12 = OpConstant %int 12
%float_0_400000006 = OpConstant %float 0.400000006
        %322 = OpConstantComposite %v4float %float_0 %float_0_400000006 %float_0_400000006 %float_0_400000006
 %float_1690 = OpConstant %float 1690
 %float_1691 = OpConstant %float 1691
 %float_1692 = OpConstant %float 1692
 %float_1693 = OpConstant %float 1693
        %333 = OpConstantComposite %v4float %float_1690 %float_1691 %float_1692 %float_1693
     %int_13 = OpConstant %int 13
        %344 = OpConstantComposite %v4float %float_0_400000006 %float_0 %float_0_400000006 %float_0_400000006
 %float_1960 = OpConstant %float 1960
 %float_1961 = OpConstant %float 1961
 %float_1962 = OpConstant %float 1962
 %float_1963 = OpConstant %float 1963
        %355 = OpConstantComposite %v4float %float_1960 %float_1961 %float_1962 %float_1963
     %int_14 = OpConstant %int 14
        %366 = OpConstantComposite %v4float %float_0_400000006 %float_0_400000006 %float_0 %float_0_400000006
 %float_2250 = OpConstant %float 2250
 %float_2251 = OpConstant %float 2251
 %float_2252 = OpConstant %float 2252
 %float_2253 = OpConstant %float 2253
        %377 = OpConstantComposite %v4float %float_2250 %float_2251 %float_2252 %float_2253
     %int_15 = OpConstant %int 15
        %388 = OpConstantComposite %v4float %float_0_400000006 %float_0_400000006 %float_0_400000006 %float_0
 %float_2560 = OpConstant %float 2560
 %float_2561 = OpConstant %float 2561
 %float_2562 = OpConstant %float 2562
 %float_2563 = OpConstant %float 2563
        %399 = OpConstantComposite %v4float %float_2560 %float_2561 %float_2562 %float_2563
       %main = OpFunction %void None %3
          %5 = OpLabel
         %uv = OpVariable %_ptr_Function_v2float Function
         %13 = OpLoad %v4float %gl_FragCoord
         %14 = OpVectorShuffle %v2float %13 %13 0 1
         %24 = OpAccessChain %_ptr_PushConstant_v4uint %params %int_0
         %25 = OpLoad %v4uint %24
         %26 = OpVectorShuffle %v2uint %25 %25 0 1
         %27 = OpConvertUToF %v2float %26
         %28 = OpFSub %v2float %14 %27
         %29 = OpAccessChain %_ptr_PushConstant_v4uint %params %int_0
         %30 = OpLoad %v4uint %29
         %31 = OpVectorShuffle %v2uint %30 %30 2 3
         %32 = OpConvertUToF %v2float %31
         %33 = OpFDiv %v2float %28 %32
               OpStore %uv %33
         %36 = OpLoad %int %gl_SampleID
         %38 = OpIEqual %bool %36 %int_0
               OpSelectionMerge %40 None
               OpBranchConditional %38 %39 %69
         %39 = OpLabel
         %48 = OpAccessChain %_ptr_Function_float %uv %uint_0
         %49 = OpLoad %float %48
         %50 = OpVectorTimesScalar %v4float %45 %49
               OpStore %o_color1 %50
         %52 = OpAccessChain %_ptr_Function_float %uv %uint_0
         %53 = OpLoad %float %52
         %54 = OpVectorTimesScalar %v4float %45 %53
               OpStore %o_color2 %54
         %63 = OpAccessChain %_ptr_Function_float %uv %uint_0
         %64 = OpLoad %float %63
         %65 = OpVectorTimesScalar %v4float %62 %64
         %66 = OpConvertFToS %v4int %65
               OpStore %o_color3 %66
               OpStore %gl_FragDepth %float_1
               OpBranch %40
         %69 = OpLabel
         %70 = OpLoad %int %gl_SampleID
         %72 = OpIEqual %bool %70 %int_1
               OpSelectionMerge %74 None
               OpBranchConditional %72 %73 %93
         %73 = OpLabel
         %77 = OpAccessChain %_ptr_Function_float %uv %uint_1
         %78 = OpLoad %float %77
         %79 = OpVectorTimesScalar %v4float %75 %78
               OpStore %o_color1 %79
         %80 = OpAccessChain %_ptr_Function_float %uv %uint_1
         %81 = OpLoad %float %80
         %82 = OpVectorTimesScalar %v4float %75 %81
               OpStore %o_color2 %82
         %88 = OpAccessChain %_ptr_Function_float %uv %uint_1
         %89 = OpLoad %float %88
         %90 = OpVectorTimesScalar %v4float %87 %89
         %91 = OpConvertFToS %v4int %90
               OpStore %o_color3 %91
               OpStore %gl_FragDepth %float_0_9375
               OpBranch %74
         %93 = OpLabel
         %94 = OpLoad %int %gl_SampleID
         %96 = OpIEqual %bool %94 %int_2
               OpSelectionMerge %98 None
               OpBranchConditional %96 %97 %115
         %97 = OpLabel
        %100 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %101 = OpLoad %float %100
        %102 = OpVectorTimesScalar %v4float %99 %101
               OpStore %o_color1 %102
        %103 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %104 = OpLoad %float %103
        %105 = OpVectorTimesScalar %v4float %99 %104
               OpStore %o_color2 %105
        %111 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %112 = OpLoad %float %111
        %113 = OpVectorTimesScalar %v4float %110 %112
        %114 = OpConvertFToS %v4int %113
               OpStore %o_color3 %114
               OpStore %gl_FragDepth %float_1
               OpBranch %98
        %115 = OpLabel
        %116 = OpLoad %int %gl_SampleID
        %118 = OpIEqual %bool %116 %int_3
               OpSelectionMerge %120 None
               OpBranchConditional %118 %119 %137
        %119 = OpLabel
        %122 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %123 = OpLoad %float %122
        %124 = OpVectorTimesScalar %v4float %121 %123
               OpStore %o_color1 %124
        %125 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %126 = OpLoad %float %125
        %127 = OpVectorTimesScalar %v4float %121 %126
               OpStore %o_color2 %127
        %133 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %134 = OpLoad %float %133
        %135 = OpVectorTimesScalar %v4float %132 %134
        %136 = OpConvertFToS %v4int %135
               OpStore %o_color3 %136
               OpStore %gl_FragDepth %float_0_9375
               OpBranch %120
        %137 = OpLabel
        %138 = OpLoad %int %gl_SampleID
        %140 = OpIEqual %bool %138 %int_4
               OpSelectionMerge %142 None
               OpBranchConditional %140 %141 %160
        %141 = OpLabel
        %145 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %146 = OpLoad %float %145
        %147 = OpVectorTimesScalar %v4float %144 %146
               OpStore %o_color1 %147
        %148 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %149 = OpLoad %float %148
        %150 = OpVectorTimesScalar %v4float %144 %149
               OpStore %o_color2 %150
        %156 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %157 = OpLoad %float %156
        %158 = OpVectorTimesScalar %v4float %155 %157
        %159 = OpConvertFToS %v4int %158
               OpStore %o_color3 %159
               OpStore %gl_FragDepth %float_1
               OpBranch %142
        %160 = OpLabel
        %161 = OpLoad %int %gl_SampleID
        %163 = OpIEqual %bool %161 %int_5
               OpSelectionMerge %165 None
               OpBranchConditional %163 %164 %182
        %164 = OpLabel
        %167 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %168 = OpLoad %float %167
        %169 = OpVectorTimesScalar %v4float %166 %168
               OpStore %o_color1 %169
        %170 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %171 = OpLoad %float %170
        %172 = OpVectorTimesScalar %v4float %166 %171
               OpStore %o_color2 %172
        %178 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %179 = OpLoad %float %178
        %180 = OpVectorTimesScalar %v4float %177 %179
        %181 = OpConvertFToS %v4int %180
               OpStore %o_color3 %181
               OpStore %gl_FragDepth %float_0_9375
               OpBranch %165
        %182 = OpLabel
        %183 = OpLoad %int %gl_SampleID
        %185 = OpIEqual %bool %183 %int_6
               OpSelectionMerge %187 None
               OpBranchConditional %185 %186 %204
        %186 = OpLabel
        %189 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %190 = OpLoad %float %189
        %191 = OpVectorTimesScalar %v4float %188 %190
               OpStore %o_color1 %191
        %192 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %193 = OpLoad %float %192
        %194 = OpVectorTimesScalar %v4float %188 %193
               OpStore %o_color2 %194
        %200 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %201 = OpLoad %float %200
        %202 = OpVectorTimesScalar %v4float %199 %201
        %203 = OpConvertFToS %v4int %202
               OpStore %o_color3 %203
               OpStore %gl_FragDepth %float_1
               OpBranch %187
        %204 = OpLabel
        %205 = OpLoad %int %gl_SampleID
        %207 = OpIEqual %bool %205 %int_7
               OpSelectionMerge %209 None
               OpBranchConditional %207 %208 %226
        %208 = OpLabel
        %211 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %212 = OpLoad %float %211
        %213 = OpVectorTimesScalar %v4float %210 %212
               OpStore %o_color1 %213
        %214 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %215 = OpLoad %float %214
        %216 = OpVectorTimesScalar %v4float %210 %215
               OpStore %o_color2 %216
        %222 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %223 = OpLoad %float %222
        %224 = OpVectorTimesScalar %v4float %221 %223
        %225 = OpConvertFToS %v4int %224
               OpStore %o_color3 %225
               OpStore %gl_FragDepth %float_0_9375
               OpBranch %209
        %226 = OpLabel
        %227 = OpLoad %int %gl_SampleID
        %229 = OpIEqual %bool %227 %int_8
               OpSelectionMerge %231 None
               OpBranchConditional %229 %230 %249
        %230 = OpLabel
        %234 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %235 = OpLoad %float %234
        %236 = OpVectorTimesScalar %v4float %233 %235
               OpStore %o_color1 %236
        %237 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %238 = OpLoad %float %237
        %239 = OpVectorTimesScalar %v4float %233 %238
               OpStore %o_color2 %239
        %245 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %246 = OpLoad %float %245
        %247 = OpVectorTimesScalar %v4float %244 %246
        %248 = OpConvertFToS %v4int %247
               OpStore %o_color3 %248
               OpStore %gl_FragDepth %float_1
               OpBranch %231
        %249 = OpLabel
        %250 = OpLoad %int %gl_SampleID
        %252 = OpIEqual %bool %250 %int_9
               OpSelectionMerge %254 None
               OpBranchConditional %252 %253 %271
        %253 = OpLabel
        %256 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %257 = OpLoad %float %256
        %258 = OpVectorTimesScalar %v4float %255 %257
               OpStore %o_color1 %258
        %259 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %260 = OpLoad %float %259
        %261 = OpVectorTimesScalar %v4float %255 %260
               OpStore %o_color2 %261
        %267 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %268 = OpLoad %float %267
        %269 = OpVectorTimesScalar %v4float %266 %268
        %270 = OpConvertFToS %v4int %269
               OpStore %o_color3 %270
               OpStore %gl_FragDepth %float_0_9375
               OpBranch %254
        %271 = OpLabel
        %272 = OpLoad %int %gl_SampleID
        %274 = OpIEqual %bool %272 %int_10
               OpSelectionMerge %276 None
               OpBranchConditional %274 %275 %293
        %275 = OpLabel
        %278 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %279 = OpLoad %float %278
        %280 = OpVectorTimesScalar %v4float %277 %279
               OpStore %o_color1 %280
        %281 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %282 = OpLoad %float %281
        %283 = OpVectorTimesScalar %v4float %277 %282
               OpStore %o_color2 %283
        %289 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %290 = OpLoad %float %289
        %291 = OpVectorTimesScalar %v4float %288 %290
        %292 = OpConvertFToS %v4int %291
               OpStore %o_color3 %292
               OpStore %gl_FragDepth %float_1
               OpBranch %276
        %293 = OpLabel
        %294 = OpLoad %int %gl_SampleID
        %296 = OpIEqual %bool %294 %int_11
               OpSelectionMerge %298 None
               OpBranchConditional %296 %297 %315
        %297 = OpLabel
        %300 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %301 = OpLoad %float %300
        %302 = OpVectorTimesScalar %v4float %299 %301
               OpStore %o_color1 %302
        %303 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %304 = OpLoad %float %303
        %305 = OpVectorTimesScalar %v4float %299 %304
               OpStore %o_color2 %305
        %311 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %312 = OpLoad %float %311
        %313 = OpVectorTimesScalar %v4float %310 %312
        %314 = OpConvertFToS %v4int %313
               OpStore %o_color3 %314
               OpStore %gl_FragDepth %float_0_9375
               OpBranch %298
        %315 = OpLabel
        %316 = OpLoad %int %gl_SampleID
        %318 = OpIEqual %bool %316 %int_12
               OpSelectionMerge %320 None
               OpBranchConditional %318 %319 %338
        %319 = OpLabel
        %323 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %324 = OpLoad %float %323
        %325 = OpVectorTimesScalar %v4float %322 %324
               OpStore %o_color1 %325
        %326 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %327 = OpLoad %float %326
        %328 = OpVectorTimesScalar %v4float %322 %327
               OpStore %o_color2 %328
        %334 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %335 = OpLoad %float %334
        %336 = OpVectorTimesScalar %v4float %333 %335
        %337 = OpConvertFToS %v4int %336
               OpStore %o_color3 %337
               OpStore %gl_FragDepth %float_1
               OpBranch %320
        %338 = OpLabel
        %339 = OpLoad %int %gl_SampleID
        %341 = OpIEqual %bool %339 %int_13
               OpSelectionMerge %343 None
               OpBranchConditional %341 %342 %360
        %342 = OpLabel
        %345 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %346 = OpLoad %float %345
        %347 = OpVectorTimesScalar %v4float %344 %346
               OpStore %o_color1 %347
        %348 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %349 = OpLoad %float %348
        %350 = OpVectorTimesScalar %v4float %344 %349
               OpStore %o_color2 %350
        %356 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %357 = OpLoad %float %356
        %358 = OpVectorTimesScalar %v4float %355 %357
        %359 = OpConvertFToS %v4int %358
               OpStore %o_color3 %359
               OpStore %gl_FragDepth %float_0_9375
               OpBranch %343
        %360 = OpLabel
        %361 = OpLoad %int %gl_SampleID
        %363 = OpIEqual %bool %361 %int_14
               OpSelectionMerge %365 None
               OpBranchConditional %363 %364 %382
        %364 = OpLabel
        %367 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %368 = OpLoad %float %367
        %369 = OpVectorTimesScalar %v4float %366 %368
               OpStore %o_color1 %369
        %370 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %371 = OpLoad %float %370
        %372 = OpVectorTimesScalar %v4float %366 %371
               OpStore %o_color2 %372
        %378 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %379 = OpLoad %float %378
        %380 = OpVectorTimesScalar %v4float %377 %379
        %381 = OpConvertFToS %v4int %380
               OpStore %o_color3 %381
               OpStore %gl_FragDepth %float_1
               OpBranch %365
        %382 = OpLabel
        %383 = OpLoad %int %gl_SampleID
        %385 = OpIEqual %bool %383 %int_15
               OpSelectionMerge %387 None
               OpBranchConditional %385 %386 %387
        %386 = OpLabel
        %389 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %390 = OpLoad %float %389
        %391 = OpVectorTimesScalar %v4float %388 %390
               OpStore %o_color1 %391
        %392 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %393 = OpLoad %float %392
        %394 = OpVectorTimesScalar %v4float %388 %393
               OpStore %o_color2 %394
        %400 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %401 = OpLoad %float %400
        %402 = OpVectorTimesScalar %v4float %399 %401
        %403 = OpConvertFToS %v4int %402
               OpStore %o_color3 %403
               OpStore %gl_FragDepth %float_0_9375
               OpBranch %387
        %387 = OpLabel
               OpBranch %365
        %365 = OpLabel
               OpBranch %343
        %343 = OpLabel
               OpBranch %320
        %320 = OpLabel
               OpBranch %298
        %298 = OpLabel
               OpBranch %276
        %276 = OpLabel
               OpBranch %254
        %254 = OpLabel
               OpBranch %231
        %231 = OpLabel
               OpBranch %209
        %209 = OpLabel
               OpBranch %187
        %187 = OpLabel
               OpBranch %165
        %165 = OpLabel
               OpBranch %142
        %142 = OpLabel
               OpBranch %120
        %120 = OpLabel
               OpBranch %98
         %98 = OpLabel
               OpBranch %74
         %74 = OpLabel
               OpBranch %40
         %40 = OpLabel
               OpReturn
               OpFunctionEnd

```

</details>

##### Compute Shader

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `comp`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 845
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint GLCompute %main "main" %gl_GlobalInvocationID
               OpExecutionMode %main LocalSize 8 8 1
               OpSource GLSL 450
               OpSourceExtension "GL_EXT_samplerless_texture_functions"
               OpName %main "main"
               OpName %fmatches_f1_f1_f1_ "fmatches(f1;f1;f1;"
               OpName %a "a"
               OpName %b "b"
               OpName %error "error"
               OpName %v4matches_vf4_vf4_vf4_ "v4matches(vf4;vf4;vf4;"
               OpName %a_0 "a"
               OpName %b_0 "b"
               OpName %error_0 "error"
               OpName %i4matchesEither_vi4_vi4_vi4_i1_i1_ "i4matchesEither(vi4;vi4;vi4;i1;i1;"
               OpName %a_1 "a"
               OpName %b_1 "b"
               OpName %c "c"
               OpName %errorB "errorB"
               OpName %errorC "errorC"
               OpName %gl_GlobalInvocationID "gl_GlobalInvocationID"
               OpName %PushConstants "PushConstants"
               OpMemberName %PushConstants 0 "area"
               OpMemberName %PushConstants 1 "stencilExpect"
               OpName %params "params"
               OpName %coords "coords"
               OpName %uv "uv"
               OpName %result1 "result1"
               OpName %color1 "color1"
               OpName %color1Image "color1Image"
               OpName %expected1H "expected1H"
               OpName %expected1V "expected1V"
               OpName %expected1 "expected1"
               OpName %param "param"
               OpName %param_0 "param"
               OpName %param_1 "param"
               OpName %Output "Output"
               OpMemberName %Output 0 "colorVerification"
               OpMemberName %Output 1 "depthVerification"
               OpMemberName %Output 2 "stencilVerification"
               OpName %sb_out "sb_out"
               OpName %verify "verify"
               OpName %result2 "result2"
               OpName %color2 "color2"
               OpName %color2Image "color2Image"
               OpName %param_2 "param"
               OpName %param_3 "param"
               OpName %param_4 "param"
               OpName %result3 "result3"
               OpName %color3 "color3"
               OpName %color3Image "color3Image"
               OpName %param_5 "param"
               OpName %param_6 "param"
               OpName %param_7 "param"
               OpName %param_8 "param"
               OpName %param_9 "param"
               OpName %param_10 "param"
               OpName %param_11 "param"
               OpName %param_12 "param"
               OpName %param_13 "param"
               OpName %param_14 "param"
               OpName %param_15 "param"
               OpName %param_16 "param"
               OpName %param_17 "param"
               OpName %param_18 "param"
               OpName %param_19 "param"
               OpName %param_20 "param"
               OpName %param_21 "param"
               OpName %param_22 "param"
               OpName %param_23 "param"
               OpName %param_24 "param"
               OpName %param_25 "param"
               OpName %param_26 "param"
               OpName %param_27 "param"
               OpName %param_28 "param"
               OpName %param_29 "param"
               OpName %param_30 "param"
               OpName %param_31 "param"
               OpName %param_32 "param"
               OpName %param_33 "param"
               OpName %param_34 "param"
               OpName %param_35 "param"
               OpName %param_36 "param"
               OpName %param_37 "param"
               OpName %param_38 "param"
               OpName %param_39 "param"
               OpName %param_40 "param"
               OpName %param_41 "param"
               OpName %param_42 "param"
               OpName %param_43 "param"
               OpName %param_44 "param"
               OpName %param_45 "param"
               OpName %param_46 "param"
               OpName %param_47 "param"
               OpName %param_48 "param"
               OpName %param_49 "param"
               OpName %param_50 "param"
               OpName %param_51 "param"
               OpName %param_52 "param"
               OpName %param_53 "param"
               OpName %param_54 "param"
               OpName %param_55 "param"
               OpName %param_56 "param"
               OpName %param_57 "param"
               OpName %param_58 "param"
               OpName %param_59 "param"
               OpName %param_60 "param"
               OpName %param_61 "param"
               OpName %param_62 "param"
               OpName %param_63 "param"
               OpName %param_64 "param"
               OpName %param_65 "param"
               OpName %param_66 "param"
               OpName %param_67 "param"
               OpName %param_68 "param"
               OpName %param_69 "param"
               OpName %param_70 "param"
               OpName %param_71 "param"
               OpName %param_72 "param"
               OpName %param_73 "param"
               OpName %param_74 "param"
               OpName %param_75 "param"
               OpName %param_76 "param"
               OpName %param_77 "param"
               OpName %param_78 "param"
               OpName %param_79 "param"
               OpName %param_80 "param"
               OpName %param_81 "param"
               OpName %param_82 "param"
               OpName %param_83 "param"
               OpName %param_84 "param"
               OpName %resultDepth "resultDepth"
               OpName %depth "depth"
               OpName %depthImage "depthImage"
               OpName %param_85 "param"
               OpName %param_86 "param"
               OpName %param_87 "param"
               OpDecorate %gl_GlobalInvocationID BuiltIn GlobalInvocationId
               OpDecorate %PushConstants Block
               OpMemberDecorate %PushConstants 0 Offset 0
               OpMemberDecorate %PushConstants 1 Offset 16
               OpDecorate %color1Image Binding 1
               OpDecorate %color1Image DescriptorSet 0
               OpDecorate %_arr_uint_uint_3 ArrayStride 4
               OpDecorate %Output BufferBlock
               OpMemberDecorate %Output 0 NonReadable
               OpMemberDecorate %Output 0 Offset 0
               OpMemberDecorate %Output 1 NonReadable
               OpMemberDecorate %Output 1 Offset 12
               OpMemberDecorate %Output 2 NonReadable
               OpMemberDecorate %Output 2 Offset 16
               OpDecorate %sb_out NonReadable
               OpDecorate %sb_out Binding 0
               OpDecorate %sb_out DescriptorSet 0
               OpDecorate %verify NonReadable
               OpDecorate %verify Binding 6
               OpDecorate %verify DescriptorSet 0
               OpDecorate %color2Image Binding 2
               OpDecorate %color2Image DescriptorSet 0
               OpDecorate %color3Image Binding 3
               OpDecorate %color3Image DescriptorSet 0
               OpDecorate %depthImage Binding 4
               OpDecorate %depthImage DescriptorSet 0
               OpDecorate %gl_WorkGroupSize BuiltIn WorkgroupSize
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
%_ptr_Function_float = OpTypePointer Function %float
       %bool = OpTypeBool
          %9 = OpTypeFunction %bool %_ptr_Function_float %_ptr_Function_float %_ptr_Function_float
    %v4float = OpTypeVector %float 4
%_ptr_Function_v4float = OpTypePointer Function %v4float
         %17 = OpTypeFunction %bool %_ptr_Function_v4float %_ptr_Function_v4float %_ptr_Function_v4float
        %int = OpTypeInt 32 1
      %v4int = OpTypeVector %int 4
%_ptr_Function_v4int = OpTypePointer Function %v4int
%_ptr_Function_int = OpTypePointer Function %int
         %27 = OpTypeFunction %bool %_ptr_Function_v4int %_ptr_Function_v4int %_ptr_Function_v4int %_ptr_Function_int %_ptr_Function_int
     %v4bool = OpTypeVector %bool 4
       %uint = OpTypeInt 32 0
     %v3uint = OpTypeVector %uint 3
%_ptr_Input_v3uint = OpTypePointer Input %v3uint
%gl_GlobalInvocationID = OpVariable %_ptr_Input_v3uint Input
     %v2uint = OpTypeVector %uint 2
     %v4uint = OpTypeVector %uint 4
%PushConstants = OpTypeStruct %v4uint %uint
%_ptr_PushConstant_PushConstants = OpTypePointer PushConstant %PushConstants
     %params = OpVariable %_ptr_PushConstant_PushConstants PushConstant
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_v4uint = OpTypePointer PushConstant %v4uint
     %v2bool = OpTypeVector %bool 2
%_ptr_Function_v2uint = OpTypePointer Function %v2uint
    %v2float = OpTypeVector %float 2
%_ptr_Function_v2float = OpTypePointer Function %v2float
  %float_0_5 = OpConstant %float 0.5
        %112 = OpConstantComposite %v2float %float_0_5 %float_0_5
    %float_1 = OpConstant %float 1
    %float_0 = OpConstant %float 0
        %122 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
        %124 = OpTypeImage %float 2D 0 0 0 1 Unknown
%_ptr_UniformConstant_124 = OpTypePointer UniformConstant %124
%color1Image = OpVariable %_ptr_UniformConstant_124 UniformConstant
      %v2int = OpTypeVector %int 2
%float_0_349999994 = OpConstant %float 0.349999994
%float_0_699999988 = OpConstant %float 0.699999988
        %135 = OpConstantComposite %v4float %float_0_349999994 %float_0_699999988 %float_0_349999994 %float_0_699999988
        %137 = OpConstantComposite %v4float %float_0_699999988 %float_0_349999994 %float_0_699999988 %float_0_349999994
     %uint_0 = OpConstant %uint 0
     %uint_1 = OpConstant %uint 1
    %float_2 = OpConstant %float 2
     %uint_2 = OpConstant %uint 2
%_ptr_PushConstant_uint = OpTypePointer PushConstant %uint
     %uint_3 = OpConstant %uint 3
%float_0_00784313772 = OpConstant %float 0.00784313772
%_arr_uint_uint_3 = OpTypeArray %uint %uint_3
     %Output = OpTypeStruct %_arr_uint_uint_3 %uint %uint
%_ptr_Uniform_Output = OpTypePointer Uniform %Output
     %sb_out = OpVariable %_ptr_Uniform_Output Uniform
%_ptr_Uniform_uint = OpTypePointer Uniform %uint
        %187 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
        %188 = OpTypeImage %float 2D 0 1 0 2 Rgba8
%_ptr_UniformConstant_188 = OpTypePointer UniformConstant %188
     %verify = OpVariable %_ptr_UniformConstant_188 UniformConstant
      %v3int = OpTypeVector %int 3
%color2Image = OpVariable %_ptr_UniformConstant_124 UniformConstant
%float_0_001953125 = OpConstant %float 0.001953125
      %int_1 = OpConstant %int 1
        %242 = OpTypeImage %int 2D 0 0 0 1 Unknown
%_ptr_UniformConstant_242 = OpTypePointer UniformConstant %242
%color3Image = OpVariable %_ptr_UniformConstant_242 UniformConstant
   %float_10 = OpConstant %float 10
   %float_11 = OpConstant %float 11
   %float_12 = OpConstant %float 12
   %float_13 = OpConstant %float 13
        %253 = OpConstantComposite %v4float %float_10 %float_11 %float_12 %float_13
     %int_10 = OpConstant %int 10
   %float_40 = OpConstant %float 40
   %float_41 = OpConstant %float 41
   %float_42 = OpConstant %float 42
   %float_43 = OpConstant %float 43
        %287 = OpConstantComposite %v4float %float_40 %float_41 %float_42 %float_43
     %int_40 = OpConstant %int 40
   %float_90 = OpConstant %float 90
   %float_91 = OpConstant %float 91
   %float_92 = OpConstant %float 92
   %float_93 = OpConstant %float 93
        %322 = OpConstantComposite %v4float %float_90 %float_91 %float_92 %float_93
     %int_90 = OpConstant %int 90
  %float_160 = OpConstant %float 160
  %float_161 = OpConstant %float 161
  %float_162 = OpConstant %float 162
  %float_163 = OpConstant %float 163
        %357 = OpConstantComposite %v4float %float_160 %float_161 %float_162 %float_163
    %int_160 = OpConstant %int 160
  %float_250 = OpConstant %float 250
  %float_251 = OpConstant %float 251
  %float_252 = OpConstant %float 252
  %float_253 = OpConstant %float 253
        %392 = OpConstantComposite %v4float %float_250 %float_251 %float_252 %float_253
    %int_250 = OpConstant %int 250
  %float_360 = OpConstant %float 360
  %float_361 = OpConstant %float 361
  %float_362 = OpConstant %float 362
  %float_363 = OpConstant %float 363
        %427 = OpConstantComposite %v4float %float_360 %float_361 %float_362 %float_363
    %int_360 = OpConstant %int 360
  %float_490 = OpConstant %float 490
  %float_491 = OpConstant %float 491
  %float_492 = OpConstant %float 492
  %float_493 = OpConstant %float 493
        %462 = OpConstantComposite %v4float %float_490 %float_491 %float_492 %float_493
    %int_490 = OpConstant %int 490
  %float_640 = OpConstant %float 640
  %float_641 = OpConstant %float 641
  %float_642 = OpConstant %float 642
  %float_643 = OpConstant %float 643
        %497 = OpConstantComposite %v4float %float_640 %float_641 %float_642 %float_643
    %int_640 = OpConstant %int 640
  %float_810 = OpConstant %float 810
  %float_811 = OpConstant %float 811
  %float_812 = OpConstant %float 812
  %float_813 = OpConstant %float 813
        %532 = OpConstantComposite %v4float %float_810 %float_811 %float_812 %float_813
    %int_810 = OpConstant %int 810
 %float_1000 = OpConstant %float 1000
 %float_1001 = OpConstant %float 1001
 %float_1002 = OpConstant %float 1002
 %float_1003 = OpConstant %float 1003
        %567 = OpConstantComposite %v4float %float_1000 %float_1001 %float_1002 %float_1003
   %int_1000 = OpConstant %int 1000
 %float_1210 = OpConstant %float 1210
 %float_1211 = OpConstant %float 1211
 %float_1212 = OpConstant %float 1212
 %float_1213 = OpConstant %float 1213
        %602 = OpConstantComposite %v4float %float_1210 %float_1211 %float_1212 %float_1213
   %int_1210 = OpConstant %int 1210
 %float_1440 = OpConstant %float 1440
 %float_1441 = OpConstant %float 1441
 %float_1442 = OpConstant %float 1442
 %float_1443 = OpConstant %float 1443
        %637 = OpConstantComposite %v4float %float_1440 %float_1441 %float_1442 %float_1443
   %int_1440 = OpConstant %int 1440
 %float_1690 = OpConstant %float 1690
 %float_1691 = OpConstant %float 1691
 %float_1692 = OpConstant %float 1692
 %float_1693 = OpConstant %float 1693
        %672 = OpConstantComposite %v4float %float_1690 %float_1691 %float_1692 %float_1693
   %int_1690 = OpConstant %int 1690
 %float_1960 = OpConstant %float 1960
 %float_1961 = OpConstant %float 1961
 %float_1962 = OpConstant %float 1962
 %float_1963 = OpConstant %float 1963
        %707 = OpConstantComposite %v4float %float_1960 %float_1961 %float_1962 %float_1963
   %int_1960 = OpConstant %int 1960
 %float_2250 = OpConstant %float 2250
 %float_2251 = OpConstant %float 2251
 %float_2252 = OpConstant %float 2252
 %float_2253 = OpConstant %float 2253
        %742 = OpConstantComposite %v4float %float_2250 %float_2251 %float_2252 %float_2253
   %int_2250 = OpConstant %int 2250
 %float_2560 = OpConstant %float 2560
 %float_2561 = OpConstant %float 2561
 %float_2562 = OpConstant %float 2562
 %float_2563 = OpConstant %float 2563
        %777 = OpConstantComposite %v4float %float_2560 %float_2561 %float_2562 %float_2563
   %int_2560 = OpConstant %int 2560
      %int_2 = OpConstant %int 2
 %depthImage = OpVariable %_ptr_UniformConstant_124 UniformConstant
%float_0_00999999978 = OpConstant %float 0.00999999978
      %int_3 = OpConstant %int 3
     %uint_8 = OpConstant %uint 8
%gl_WorkGroupSize = OpConstantComposite %v3uint %uint_8 %uint_8 %uint_1
       %main = OpFunction %void None %3
          %5 = OpLabel
     %coords = OpVariable %_ptr_Function_v2uint Function
         %uv = OpVariable %_ptr_Function_v2float Function
    %result1 = OpVariable %_ptr_Function_v4float Function
     %color1 = OpVariable %_ptr_Function_v4float Function
 %expected1H = OpVariable %_ptr_Function_v4float Function
 %expected1V = OpVariable %_ptr_Function_v4float Function
  %expected1 = OpVariable %_ptr_Function_v4float Function
      %param = OpVariable %_ptr_Function_v4float Function
    %param_0 = OpVariable %_ptr_Function_v4float Function
    %param_1 = OpVariable %_ptr_Function_v4float Function
    %result2 = OpVariable %_ptr_Function_v4float Function
     %color2 = OpVariable %_ptr_Function_v4float Function
    %param_2 = OpVariable %_ptr_Function_v4float Function
    %param_3 = OpVariable %_ptr_Function_v4float Function
    %param_4 = OpVariable %_ptr_Function_v4float Function
    %result3 = OpVariable %_ptr_Function_v4float Function
     %color3 = OpVariable %_ptr_Function_v4int Function
    %param_5 = OpVariable %_ptr_Function_v4int Function
    %param_6 = OpVariable %_ptr_Function_v4int Function
    %param_7 = OpVariable %_ptr_Function_v4int Function
    %param_8 = OpVariable %_ptr_Function_int Function
    %param_9 = OpVariable %_ptr_Function_int Function
   %param_10 = OpVariable %_ptr_Function_v4int Function
   %param_11 = OpVariable %_ptr_Function_v4int Function
   %param_12 = OpVariable %_ptr_Function_v4int Function
   %param_13 = OpVariable %_ptr_Function_int Function
   %param_14 = OpVariable %_ptr_Function_int Function
   %param_15 = OpVariable %_ptr_Function_v4int Function
   %param_16 = OpVariable %_ptr_Function_v4int Function
   %param_17 = OpVariable %_ptr_Function_v4int Function
   %param_18 = OpVariable %_ptr_Function_int Function
   %param_19 = OpVariable %_ptr_Function_int Function
   %param_20 = OpVariable %_ptr_Function_v4int Function
   %param_21 = OpVariable %_ptr_Function_v4int Function
   %param_22 = OpVariable %_ptr_Function_v4int Function
   %param_23 = OpVariable %_ptr_Function_int Function
   %param_24 = OpVariable %_ptr_Function_int Function
   %param_25 = OpVariable %_ptr_Function_v4int Function
   %param_26 = OpVariable %_ptr_Function_v4int Function
   %param_27 = OpVariable %_ptr_Function_v4int Function
   %param_28 = OpVariable %_ptr_Function_int Function
   %param_29 = OpVariable %_ptr_Function_int Function
   %param_30 = OpVariable %_ptr_Function_v4int Function
   %param_31 = OpVariable %_ptr_Function_v4int Function
   %param_32 = OpVariable %_ptr_Function_v4int Function
   %param_33 = OpVariable %_ptr_Function_int Function
   %param_34 = OpVariable %_ptr_Function_int Function
   %param_35 = OpVariable %_ptr_Function_v4int Function
   %param_36 = OpVariable %_ptr_Function_v4int Function
   %param_37 = OpVariable %_ptr_Function_v4int Function
   %param_38 = OpVariable %_ptr_Function_int Function
   %param_39 = OpVariable %_ptr_Function_int Function
   %param_40 = OpVariable %_ptr_Function_v4int Function
   %param_41 = OpVariable %_ptr_Function_v4int Function
   %param_42 = OpVariable %_ptr_Function_v4int Function
   %param_43 = OpVariable %_ptr_Function_int Function
   %param_44 = OpVariable %_ptr_Function_int Function
   %param_45 = OpVariable %_ptr_Function_v4int Function
   %param_46 = OpVariable %_ptr_Function_v4int Function
   %param_47 = OpVariable %_ptr_Function_v4int Function
   %param_48 = OpVariable %_ptr_Function_int Function
   %param_49 = OpVariable %_ptr_Function_int Function
   %param_50 = OpVariable %_ptr_Function_v4int Function
   %param_51 = OpVariable %_ptr_Function_v4int Function
   %param_52 = OpVariable %_ptr_Function_v4int Function
   %param_53 = OpVariable %_ptr_Function_int Function
   %param_54 = OpVariable %_ptr_Function_int Function
   %param_55 = OpVariable %_ptr_Function_v4int Function
   %param_56 = OpVariable %_ptr_Function_v4int Function
   %param_57 = OpVariable %_ptr_Function_v4int Function
   %param_58 = OpVariable %_ptr_Function_int Function
   %param_59 = OpVariable %_ptr_Function_int Function
   %param_60 = OpVariable %_ptr_Function_v4int Function
   %param_61 = OpVariable %_ptr_Function_v4int Function
   %param_62 = OpVariable %_ptr_Function_v4int Function
   %param_63 = OpVariable %_ptr_Function_int Function
   %param_64 = OpVariable %_ptr_Function_int Function
   %param_65 = OpVariable %_ptr_Function_v4int Function
   %param_66 = OpVariable %_ptr_Function_v4int Function
   %param_67 = OpVariable %_ptr_Function_v4int Function
   %param_68 = OpVariable %_ptr_Function_int Function
   %param_69 = OpVariable %_ptr_Function_int Function
   %param_70 = OpVariable %_ptr_Function_v4int Function
   %param_71 = OpVariable %_ptr_Function_v4int Function
   %param_72 = OpVariable %_ptr_Function_v4int Function
   %param_73 = OpVariable %_ptr_Function_int Function
   %param_74 = OpVariable %_ptr_Function_int Function
   %param_75 = OpVariable %_ptr_Function_v4int Function
   %param_76 = OpVariable %_ptr_Function_v4int Function
   %param_77 = OpVariable %_ptr_Function_v4int Function
   %param_78 = OpVariable %_ptr_Function_int Function
   %param_79 = OpVariable %_ptr_Function_int Function
   %param_80 = OpVariable %_ptr_Function_v4int Function
   %param_81 = OpVariable %_ptr_Function_v4int Function
   %param_82 = OpVariable %_ptr_Function_v4int Function
   %param_83 = OpVariable %_ptr_Function_int Function
   %param_84 = OpVariable %_ptr_Function_int Function
%resultDepth = OpVariable %_ptr_Function_v4float Function
      %depth = OpVariable %_ptr_Function_float Function
   %param_85 = OpVariable %_ptr_Function_float Function
   %param_86 = OpVariable %_ptr_Function_float Function
   %param_87 = OpVariable %_ptr_Function_float Function
         %80 = OpLoad %v3uint %gl_GlobalInvocationID
         %81 = OpVectorShuffle %v2uint %80 %80 0 1
         %88 = OpAccessChain %_ptr_PushConstant_v4uint %params %int_0
         %89 = OpLoad %v4uint %88
         %90 = OpVectorShuffle %v2uint %89 %89 2 3
         %92 = OpUGreaterThanEqual %v2bool %81 %90
         %93 = OpAny %bool %92
               OpSelectionMerge %95 None
               OpBranchConditional %93 %94 %95
         %94 = OpLabel
               OpReturn
         %95 = OpLabel
         %99 = OpAccessChain %_ptr_PushConstant_v4uint %params %int_0
        %100 = OpLoad %v4uint %99
        %101 = OpVectorShuffle %v2uint %100 %100 0 1
        %102 = OpLoad %v3uint %gl_GlobalInvocationID
        %103 = OpVectorShuffle %v2uint %102 %102 0 1
        %104 = OpIAdd %v2uint %101 %103
               OpStore %coords %104
        %108 = OpLoad %v3uint %gl_GlobalInvocationID
        %109 = OpVectorShuffle %v2uint %108 %108 0 1
        %110 = OpConvertUToF %v2float %109
        %113 = OpFAdd %v2float %110 %112
        %114 = OpAccessChain %_ptr_PushConstant_v4uint %params %int_0
        %115 = OpLoad %v4uint %114
        %116 = OpVectorShuffle %v2uint %115 %115 2 3
        %117 = OpConvertUToF %v2float %116
        %118 = OpFDiv %v2float %113 %117
               OpStore %uv %118
               OpStore %result1 %122
        %127 = OpLoad %124 %color1Image
        %128 = OpLoad %v2uint %coords
        %130 = OpBitcast %v2int %128
        %131 = OpImageFetch %v4float %127 %130 Lod %int_0
               OpStore %color1 %131
               OpStore %expected1H %135
               OpStore %expected1V %137
        %139 = OpLoad %v4float %expected1H
        %141 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %142 = OpLoad %float %141
        %143 = OpVectorTimesScalar %v4float %139 %142
        %144 = OpLoad %v4float %expected1V
        %146 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %147 = OpLoad %float %146
        %148 = OpVectorTimesScalar %v4float %144 %147
        %149 = OpFAdd %v4float %143 %148
        %151 = OpCompositeConstruct %v4float %float_2 %float_2 %float_2 %float_2
        %152 = OpFDiv %v4float %149 %151
               OpStore %expected1 %152
        %153 = OpLoad %v4float %expected1H
        %156 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %157 = OpLoad %uint %156
        %158 = OpConvertUToF %float %157
        %159 = OpCompositeConstruct %v4float %158 %158 %158 %158
        %160 = OpFDiv %v4float %153 %159
        %161 = OpLoad %v4float %expected1V
        %163 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %164 = OpLoad %uint %163
        %165 = OpConvertUToF %float %164
        %166 = OpCompositeConstruct %v4float %165 %165 %165 %165
        %167 = OpFDiv %v4float %161 %166
        %168 = OpExtInst %v4float %1 FMax %160 %167
        %170 = OpCompositeConstruct %v4float %float_0_00784313772 %float_0_00784313772 %float_0_00784313772 %float_0_00784313772
        %171 = OpFAdd %v4float %168 %170
        %173 = OpLoad %v4float %color1
               OpStore %param %173
        %175 = OpLoad %v4float %expected1
               OpStore %param_0 %175
               OpStore %param_1 %171
        %177 = OpFunctionCall %bool %v4matches_vf4_vf4_vf4_ %param %param_0 %param_1
               OpSelectionMerge %179 None
               OpBranchConditional %177 %178 %179
        %178 = OpLabel
        %185 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_0 %int_0
        %186 = OpAtomicIAdd %uint %185 %uint_1 %uint_0 %uint_1
               OpStore %result1 %187
               OpBranch %179
        %179 = OpLabel
        %191 = OpLoad %188 %verify
        %192 = OpLoad %v2uint %coords
        %193 = OpBitcast %v2int %192
        %195 = OpCompositeExtract %int %193 0
        %196 = OpCompositeExtract %int %193 1
        %197 = OpCompositeConstruct %v3int %195 %196 %int_0
        %198 = OpLoad %v4float %result1
               OpImageWrite %191 %197 %198
               OpStore %result2 %122
        %202 = OpLoad %124 %color2Image
        %203 = OpLoad %v2uint %coords
        %204 = OpBitcast %v2int %203
        %205 = OpImageFetch %v4float %202 %204 Lod %int_0
               OpStore %color2 %205
        %206 = OpLoad %v4float %expected1H
        %207 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %208 = OpLoad %uint %207
        %209 = OpConvertUToF %float %208
        %210 = OpCompositeConstruct %v4float %209 %209 %209 %209
        %211 = OpFDiv %v4float %206 %210
        %212 = OpLoad %v4float %expected1V
        %213 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %214 = OpLoad %uint %213
        %215 = OpConvertUToF %float %214
        %216 = OpCompositeConstruct %v4float %215 %215 %215 %215
        %217 = OpFDiv %v4float %212 %216
        %218 = OpExtInst %v4float %1 FMax %211 %217
        %220 = OpCompositeConstruct %v4float %float_0_001953125 %float_0_001953125 %float_0_001953125 %float_0_001953125
        %221 = OpFAdd %v4float %218 %220
        %223 = OpLoad %v4float %color2
               OpStore %param_2 %223
        %225 = OpLoad %v4float %expected1
               OpStore %param_3 %225
               OpStore %param_4 %221
        %227 = OpFunctionCall %bool %v4matches_vf4_vf4_vf4_ %param_2 %param_3 %param_4
               OpSelectionMerge %229 None
               OpBranchConditional %227 %228 %229
        %228 = OpLabel
        %231 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_0 %int_1
        %232 = OpAtomicIAdd %uint %231 %uint_1 %uint_0 %uint_1
               OpStore %result2 %187
               OpBranch %229
        %229 = OpLabel
        %233 = OpLoad %188 %verify
        %234 = OpLoad %v2uint %coords
        %235 = OpBitcast %v2int %234
        %236 = OpCompositeExtract %int %235 0
        %237 = OpCompositeExtract %int %235 1
        %238 = OpCompositeConstruct %v3int %236 %237 %int_1
        %239 = OpLoad %v4float %result2
               OpImageWrite %233 %238 %239
               OpStore %result3 %122
        %245 = OpLoad %242 %color3Image
        %246 = OpLoad %v2uint %coords
        %247 = OpBitcast %v2int %246
        %248 = OpImageFetch %v4int %245 %247 Lod %int_0
               OpStore %color3 %248
        %254 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %255 = OpLoad %float %254
        %256 = OpVectorTimesScalar %v4float %253 %255
        %257 = OpConvertFToS %v4int %256
        %258 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %259 = OpLoad %float %258
        %260 = OpVectorTimesScalar %v4float %253 %259
        %261 = OpConvertFToS %v4int %260
        %263 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %264 = OpLoad %uint %263
        %265 = OpBitcast %int %264
        %266 = OpSDiv %int %int_10 %265
        %267 = OpIAdd %int %266 %int_1
        %268 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %269 = OpLoad %uint %268
        %270 = OpBitcast %int %269
        %271 = OpSDiv %int %int_10 %270
        %272 = OpIAdd %int %271 %int_1
        %274 = OpLoad %v4int %color3
               OpStore %param_5 %274
               OpStore %param_6 %257
               OpStore %param_7 %261
               OpStore %param_8 %267
               OpStore %param_9 %272
        %279 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_5 %param_6 %param_7 %param_8 %param_9
        %280 = OpLogicalNot %bool %279
               OpSelectionMerge %282 None
               OpBranchConditional %280 %281 %282
        %281 = OpLabel
        %288 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %289 = OpLoad %float %288
        %290 = OpVectorTimesScalar %v4float %287 %289
        %291 = OpConvertFToS %v4int %290
        %292 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %293 = OpLoad %float %292
        %294 = OpVectorTimesScalar %v4float %287 %293
        %295 = OpConvertFToS %v4int %294
        %297 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %298 = OpLoad %uint %297
        %299 = OpBitcast %int %298
        %300 = OpSDiv %int %int_40 %299
        %301 = OpIAdd %int %300 %int_1
        %302 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %303 = OpLoad %uint %302
        %304 = OpBitcast %int %303
        %305 = OpSDiv %int %int_40 %304
        %306 = OpIAdd %int %305 %int_1
        %308 = OpLoad %v4int %color3
               OpStore %param_10 %308
               OpStore %param_11 %291
               OpStore %param_12 %295
               OpStore %param_13 %301
               OpStore %param_14 %306
        %313 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_10 %param_11 %param_12 %param_13 %param_14
               OpBranch %282
        %282 = OpLabel
        %314 = OpPhi %bool %279 %229 %313 %281
        %315 = OpLogicalNot %bool %314
               OpSelectionMerge %317 None
               OpBranchConditional %315 %316 %317
        %316 = OpLabel
        %323 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %324 = OpLoad %float %323
        %325 = OpVectorTimesScalar %v4float %322 %324
        %326 = OpConvertFToS %v4int %325
        %327 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %328 = OpLoad %float %327
        %329 = OpVectorTimesScalar %v4float %322 %328
        %330 = OpConvertFToS %v4int %329
        %332 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %333 = OpLoad %uint %332
        %334 = OpBitcast %int %333
        %335 = OpSDiv %int %int_90 %334
        %336 = OpIAdd %int %335 %int_1
        %337 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %338 = OpLoad %uint %337
        %339 = OpBitcast %int %338
        %340 = OpSDiv %int %int_90 %339
        %341 = OpIAdd %int %340 %int_1
        %343 = OpLoad %v4int %color3
               OpStore %param_15 %343
               OpStore %param_16 %326
               OpStore %param_17 %330
               OpStore %param_18 %336
               OpStore %param_19 %341
        %348 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_15 %param_16 %param_17 %param_18 %param_19
               OpBranch %317
        %317 = OpLabel
        %349 = OpPhi %bool %314 %282 %348 %316
        %350 = OpLogicalNot %bool %349
               OpSelectionMerge %352 None
               OpBranchConditional %350 %351 %352
        %351 = OpLabel
        %358 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %359 = OpLoad %float %358
        %360 = OpVectorTimesScalar %v4float %357 %359
        %361 = OpConvertFToS %v4int %360
        %362 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %363 = OpLoad %float %362
        %364 = OpVectorTimesScalar %v4float %357 %363
        %365 = OpConvertFToS %v4int %364
        %367 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %368 = OpLoad %uint %367
        %369 = OpBitcast %int %368
        %370 = OpSDiv %int %int_160 %369
        %371 = OpIAdd %int %370 %int_1
        %372 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %373 = OpLoad %uint %372
        %374 = OpBitcast %int %373
        %375 = OpSDiv %int %int_160 %374
        %376 = OpIAdd %int %375 %int_1
        %378 = OpLoad %v4int %color3
               OpStore %param_20 %378
               OpStore %param_21 %361
               OpStore %param_22 %365
               OpStore %param_23 %371
               OpStore %param_24 %376
        %383 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_20 %param_21 %param_22 %param_23 %param_24
               OpBranch %352
        %352 = OpLabel
        %384 = OpPhi %bool %349 %317 %383 %351
        %385 = OpLogicalNot %bool %384
               OpSelectionMerge %387 None
               OpBranchConditional %385 %386 %387
        %386 = OpLabel
        %393 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %394 = OpLoad %float %393
        %395 = OpVectorTimesScalar %v4float %392 %394
        %396 = OpConvertFToS %v4int %395
        %397 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %398 = OpLoad %float %397
        %399 = OpVectorTimesScalar %v4float %392 %398
        %400 = OpConvertFToS %v4int %399
        %402 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %403 = OpLoad %uint %402
        %404 = OpBitcast %int %403
        %405 = OpSDiv %int %int_250 %404
        %406 = OpIAdd %int %405 %int_1
        %407 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %408 = OpLoad %uint %407
        %409 = OpBitcast %int %408
        %410 = OpSDiv %int %int_250 %409
        %411 = OpIAdd %int %410 %int_1
        %413 = OpLoad %v4int %color3
               OpStore %param_25 %413
               OpStore %param_26 %396
               OpStore %param_27 %400
               OpStore %param_28 %406
               OpStore %param_29 %411
        %418 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_25 %param_26 %param_27 %param_28 %param_29
               OpBranch %387
        %387 = OpLabel
        %419 = OpPhi %bool %384 %352 %418 %386
        %420 = OpLogicalNot %bool %419
               OpSelectionMerge %422 None
               OpBranchConditional %420 %421 %422
        %421 = OpLabel
        %428 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %429 = OpLoad %float %428
        %430 = OpVectorTimesScalar %v4float %427 %429
        %431 = OpConvertFToS %v4int %430
        %432 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %433 = OpLoad %float %432
        %434 = OpVectorTimesScalar %v4float %427 %433
        %435 = OpConvertFToS %v4int %434
        %437 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %438 = OpLoad %uint %437
        %439 = OpBitcast %int %438
        %440 = OpSDiv %int %int_360 %439
        %441 = OpIAdd %int %440 %int_1
        %442 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %443 = OpLoad %uint %442
        %444 = OpBitcast %int %443
        %445 = OpSDiv %int %int_360 %444
        %446 = OpIAdd %int %445 %int_1
        %448 = OpLoad %v4int %color3
               OpStore %param_30 %448
               OpStore %param_31 %431
               OpStore %param_32 %435
               OpStore %param_33 %441
               OpStore %param_34 %446
        %453 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_30 %param_31 %param_32 %param_33 %param_34
               OpBranch %422
        %422 = OpLabel
        %454 = OpPhi %bool %419 %387 %453 %421
        %455 = OpLogicalNot %bool %454
               OpSelectionMerge %457 None
               OpBranchConditional %455 %456 %457
        %456 = OpLabel
        %463 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %464 = OpLoad %float %463
        %465 = OpVectorTimesScalar %v4float %462 %464
        %466 = OpConvertFToS %v4int %465
        %467 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %468 = OpLoad %float %467
        %469 = OpVectorTimesScalar %v4float %462 %468
        %470 = OpConvertFToS %v4int %469
        %472 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %473 = OpLoad %uint %472
        %474 = OpBitcast %int %473
        %475 = OpSDiv %int %int_490 %474
        %476 = OpIAdd %int %475 %int_1
        %477 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %478 = OpLoad %uint %477
        %479 = OpBitcast %int %478
        %480 = OpSDiv %int %int_490 %479
        %481 = OpIAdd %int %480 %int_1
        %483 = OpLoad %v4int %color3
               OpStore %param_35 %483
               OpStore %param_36 %466
               OpStore %param_37 %470
               OpStore %param_38 %476
               OpStore %param_39 %481
        %488 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_35 %param_36 %param_37 %param_38 %param_39
               OpBranch %457
        %457 = OpLabel
        %489 = OpPhi %bool %454 %422 %488 %456
        %490 = OpLogicalNot %bool %489
               OpSelectionMerge %492 None
               OpBranchConditional %490 %491 %492
        %491 = OpLabel
        %498 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %499 = OpLoad %float %498
        %500 = OpVectorTimesScalar %v4float %497 %499
        %501 = OpConvertFToS %v4int %500
        %502 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %503 = OpLoad %float %502
        %504 = OpVectorTimesScalar %v4float %497 %503
        %505 = OpConvertFToS %v4int %504
        %507 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %508 = OpLoad %uint %507
        %509 = OpBitcast %int %508
        %510 = OpSDiv %int %int_640 %509
        %511 = OpIAdd %int %510 %int_1
        %512 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %513 = OpLoad %uint %512
        %514 = OpBitcast %int %513
        %515 = OpSDiv %int %int_640 %514
        %516 = OpIAdd %int %515 %int_1
        %518 = OpLoad %v4int %color3
               OpStore %param_40 %518
               OpStore %param_41 %501
               OpStore %param_42 %505
               OpStore %param_43 %511
               OpStore %param_44 %516
        %523 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_40 %param_41 %param_42 %param_43 %param_44
               OpBranch %492
        %492 = OpLabel
        %524 = OpPhi %bool %489 %457 %523 %491
        %525 = OpLogicalNot %bool %524
               OpSelectionMerge %527 None
               OpBranchConditional %525 %526 %527
        %526 = OpLabel
        %533 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %534 = OpLoad %float %533
        %535 = OpVectorTimesScalar %v4float %532 %534
        %536 = OpConvertFToS %v4int %535
        %537 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %538 = OpLoad %float %537
        %539 = OpVectorTimesScalar %v4float %532 %538
        %540 = OpConvertFToS %v4int %539
        %542 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %543 = OpLoad %uint %542
        %544 = OpBitcast %int %543
        %545 = OpSDiv %int %int_810 %544
        %546 = OpIAdd %int %545 %int_1
        %547 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %548 = OpLoad %uint %547
        %549 = OpBitcast %int %548
        %550 = OpSDiv %int %int_810 %549
        %551 = OpIAdd %int %550 %int_1
        %553 = OpLoad %v4int %color3
               OpStore %param_45 %553
               OpStore %param_46 %536
               OpStore %param_47 %540
               OpStore %param_48 %546
               OpStore %param_49 %551
        %558 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_45 %param_46 %param_47 %param_48 %param_49
               OpBranch %527
        %527 = OpLabel
        %559 = OpPhi %bool %524 %492 %558 %526
        %560 = OpLogicalNot %bool %559
               OpSelectionMerge %562 None
               OpBranchConditional %560 %561 %562
        %561 = OpLabel
        %568 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %569 = OpLoad %float %568
        %570 = OpVectorTimesScalar %v4float %567 %569
        %571 = OpConvertFToS %v4int %570
        %572 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %573 = OpLoad %float %572
        %574 = OpVectorTimesScalar %v4float %567 %573
        %575 = OpConvertFToS %v4int %574
        %577 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %578 = OpLoad %uint %577
        %579 = OpBitcast %int %578
        %580 = OpSDiv %int %int_1000 %579
        %581 = OpIAdd %int %580 %int_1
        %582 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %583 = OpLoad %uint %582
        %584 = OpBitcast %int %583
        %585 = OpSDiv %int %int_1000 %584
        %586 = OpIAdd %int %585 %int_1
        %588 = OpLoad %v4int %color3
               OpStore %param_50 %588
               OpStore %param_51 %571
               OpStore %param_52 %575
               OpStore %param_53 %581
               OpStore %param_54 %586
        %593 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_50 %param_51 %param_52 %param_53 %param_54
               OpBranch %562
        %562 = OpLabel
        %594 = OpPhi %bool %559 %527 %593 %561
        %595 = OpLogicalNot %bool %594
               OpSelectionMerge %597 None
               OpBranchConditional %595 %596 %597
        %596 = OpLabel
        %603 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %604 = OpLoad %float %603
        %605 = OpVectorTimesScalar %v4float %602 %604
        %606 = OpConvertFToS %v4int %605
        %607 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %608 = OpLoad %float %607
        %609 = OpVectorTimesScalar %v4float %602 %608
        %610 = OpConvertFToS %v4int %609
        %612 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %613 = OpLoad %uint %612
        %614 = OpBitcast %int %613
        %615 = OpSDiv %int %int_1210 %614
        %616 = OpIAdd %int %615 %int_1
        %617 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %618 = OpLoad %uint %617
        %619 = OpBitcast %int %618
        %620 = OpSDiv %int %int_1210 %619
        %621 = OpIAdd %int %620 %int_1
        %623 = OpLoad %v4int %color3
               OpStore %param_55 %623
               OpStore %param_56 %606
               OpStore %param_57 %610
               OpStore %param_58 %616
               OpStore %param_59 %621
        %628 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_55 %param_56 %param_57 %param_58 %param_59
               OpBranch %597
        %597 = OpLabel
        %629 = OpPhi %bool %594 %562 %628 %596
        %630 = OpLogicalNot %bool %629
               OpSelectionMerge %632 None
               OpBranchConditional %630 %631 %632
        %631 = OpLabel
        %638 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %639 = OpLoad %float %638
        %640 = OpVectorTimesScalar %v4float %637 %639
        %641 = OpConvertFToS %v4int %640
        %642 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %643 = OpLoad %float %642
        %644 = OpVectorTimesScalar %v4float %637 %643
        %645 = OpConvertFToS %v4int %644
        %647 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %648 = OpLoad %uint %647
        %649 = OpBitcast %int %648
        %650 = OpSDiv %int %int_1440 %649
        %651 = OpIAdd %int %650 %int_1
        %652 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %653 = OpLoad %uint %652
        %654 = OpBitcast %int %653
        %655 = OpSDiv %int %int_1440 %654
        %656 = OpIAdd %int %655 %int_1
        %658 = OpLoad %v4int %color3
               OpStore %param_60 %658
               OpStore %param_61 %641
               OpStore %param_62 %645
               OpStore %param_63 %651
               OpStore %param_64 %656
        %663 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_60 %param_61 %param_62 %param_63 %param_64
               OpBranch %632
        %632 = OpLabel
        %664 = OpPhi %bool %629 %597 %663 %631
        %665 = OpLogicalNot %bool %664
               OpSelectionMerge %667 None
               OpBranchConditional %665 %666 %667
        %666 = OpLabel
        %673 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %674 = OpLoad %float %673
        %675 = OpVectorTimesScalar %v4float %672 %674
        %676 = OpConvertFToS %v4int %675
        %677 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %678 = OpLoad %float %677
        %679 = OpVectorTimesScalar %v4float %672 %678
        %680 = OpConvertFToS %v4int %679
        %682 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %683 = OpLoad %uint %682
        %684 = OpBitcast %int %683
        %685 = OpSDiv %int %int_1690 %684
        %686 = OpIAdd %int %685 %int_1
        %687 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %688 = OpLoad %uint %687
        %689 = OpBitcast %int %688
        %690 = OpSDiv %int %int_1690 %689
        %691 = OpIAdd %int %690 %int_1
        %693 = OpLoad %v4int %color3
               OpStore %param_65 %693
               OpStore %param_66 %676
               OpStore %param_67 %680
               OpStore %param_68 %686
               OpStore %param_69 %691
        %698 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_65 %param_66 %param_67 %param_68 %param_69
               OpBranch %667
        %667 = OpLabel
        %699 = OpPhi %bool %664 %632 %698 %666
        %700 = OpLogicalNot %bool %699
               OpSelectionMerge %702 None
               OpBranchConditional %700 %701 %702
        %701 = OpLabel
        %708 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %709 = OpLoad %float %708
        %710 = OpVectorTimesScalar %v4float %707 %709
        %711 = OpConvertFToS %v4int %710
        %712 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %713 = OpLoad %float %712
        %714 = OpVectorTimesScalar %v4float %707 %713
        %715 = OpConvertFToS %v4int %714
        %717 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %718 = OpLoad %uint %717
        %719 = OpBitcast %int %718
        %720 = OpSDiv %int %int_1960 %719
        %721 = OpIAdd %int %720 %int_1
        %722 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %723 = OpLoad %uint %722
        %724 = OpBitcast %int %723
        %725 = OpSDiv %int %int_1960 %724
        %726 = OpIAdd %int %725 %int_1
        %728 = OpLoad %v4int %color3
               OpStore %param_70 %728
               OpStore %param_71 %711
               OpStore %param_72 %715
               OpStore %param_73 %721
               OpStore %param_74 %726
        %733 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_70 %param_71 %param_72 %param_73 %param_74
               OpBranch %702
        %702 = OpLabel
        %734 = OpPhi %bool %699 %667 %733 %701
        %735 = OpLogicalNot %bool %734
               OpSelectionMerge %737 None
               OpBranchConditional %735 %736 %737
        %736 = OpLabel
        %743 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %744 = OpLoad %float %743
        %745 = OpVectorTimesScalar %v4float %742 %744
        %746 = OpConvertFToS %v4int %745
        %747 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %748 = OpLoad %float %747
        %749 = OpVectorTimesScalar %v4float %742 %748
        %750 = OpConvertFToS %v4int %749
        %752 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %753 = OpLoad %uint %752
        %754 = OpBitcast %int %753
        %755 = OpSDiv %int %int_2250 %754
        %756 = OpIAdd %int %755 %int_1
        %757 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %758 = OpLoad %uint %757
        %759 = OpBitcast %int %758
        %760 = OpSDiv %int %int_2250 %759
        %761 = OpIAdd %int %760 %int_1
        %763 = OpLoad %v4int %color3
               OpStore %param_75 %763
               OpStore %param_76 %746
               OpStore %param_77 %750
               OpStore %param_78 %756
               OpStore %param_79 %761
        %768 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_75 %param_76 %param_77 %param_78 %param_79
               OpBranch %737
        %737 = OpLabel
        %769 = OpPhi %bool %734 %702 %768 %736
        %770 = OpLogicalNot %bool %769
               OpSelectionMerge %772 None
               OpBranchConditional %770 %771 %772
        %771 = OpLabel
        %778 = OpAccessChain %_ptr_Function_float %uv %uint_0
        %779 = OpLoad %float %778
        %780 = OpVectorTimesScalar %v4float %777 %779
        %781 = OpConvertFToS %v4int %780
        %782 = OpAccessChain %_ptr_Function_float %uv %uint_1
        %783 = OpLoad %float %782
        %784 = OpVectorTimesScalar %v4float %777 %783
        %785 = OpConvertFToS %v4int %784
        %787 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_2
        %788 = OpLoad %uint %787
        %789 = OpBitcast %int %788
        %790 = OpSDiv %int %int_2560 %789
        %791 = OpIAdd %int %790 %int_1
        %792 = OpAccessChain %_ptr_PushConstant_uint %params %int_0 %uint_3
        %793 = OpLoad %uint %792
        %794 = OpBitcast %int %793
        %795 = OpSDiv %int %int_2560 %794
        %796 = OpIAdd %int %795 %int_1
        %798 = OpLoad %v4int %color3
               OpStore %param_80 %798
               OpStore %param_81 %781
               OpStore %param_82 %785
               OpStore %param_83 %791
               OpStore %param_84 %796
        %803 = OpFunctionCall %bool %i4matchesEither_vi4_vi4_vi4_i1_i1_ %param_80 %param_81 %param_82 %param_83 %param_84
               OpBranch %772
        %772 = OpLabel
        %804 = OpPhi %bool %769 %737 %803 %771
               OpSelectionMerge %806 None
               OpBranchConditional %804 %805 %806
        %805 = OpLabel
        %808 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_0 %int_2
        %809 = OpAtomicIAdd %uint %808 %uint_1 %uint_0 %uint_1
               OpStore %result3 %187
               OpBranch %806
        %806 = OpLabel
        %810 = OpLoad %188 %verify
        %811 = OpLoad %v2uint %coords
        %812 = OpBitcast %v2int %811
        %813 = OpCompositeExtract %int %812 0
        %814 = OpCompositeExtract %int %812 1
        %815 = OpCompositeConstruct %v3int %813 %814 %int_2
        %816 = OpLoad %v4float %result3
               OpImageWrite %810 %815 %816
               OpStore %resultDepth %122
        %820 = OpLoad %124 %depthImage
        %821 = OpLoad %v2uint %coords
        %822 = OpBitcast %v2int %821
        %823 = OpImageFetch %v4float %820 %822 Lod %int_0
        %824 = OpCompositeExtract %float %823 0
               OpStore %depth %824
        %827 = OpLoad %float %depth
               OpStore %param_85 %827
               OpStore %param_86 %float_1
               OpStore %param_87 %float_0_00999999978
        %830 = OpFunctionCall %bool %fmatches_f1_f1_f1_ %param_85 %param_86 %param_87
               OpSelectionMerge %832 None
               OpBranchConditional %830 %831 %832
        %831 = OpLabel
        %833 = OpAccessChain %_ptr_Uniform_uint %sb_out %int_1
        %834 = OpAtomicIAdd %uint %833 %uint_1 %uint_0 %uint_1
               OpStore %resultDepth %187
               OpBranch %832
        %832 = OpLabel
        %835 = OpLoad %188 %verify
        %836 = OpLoad %v2uint %coords
        %837 = OpBitcast %v2int %836
        %839 = OpCompositeExtract %int %837 0
        %840 = OpCompositeExtract %int %837 1
        %841 = OpCompositeConstruct %v3int %839 %840 %int_3
        %842 = OpLoad %v4float %resultDepth
               OpImageWrite %835 %841 %842
               OpReturn
               OpFunctionEnd
%fmatches_f1_f1_f1_ = OpFunction %bool None %9
          %a = OpFunctionParameter %_ptr_Function_float
          %b = OpFunctionParameter %_ptr_Function_float
      %error = OpFunctionParameter %_ptr_Function_float
         %14 = OpLabel
         %35 = OpLoad %float %a
         %36 = OpLoad %float %b
         %37 = OpFSub %float %35 %36
         %38 = OpExtInst %float %1 FAbs %37
         %39 = OpLoad %float %error
         %40 = OpFOrdLessThan %bool %38 %39
               OpReturnValue %40
               OpFunctionEnd
%v4matches_vf4_vf4_vf4_ = OpFunction %bool None %17
        %a_0 = OpFunctionParameter %_ptr_Function_v4float
        %b_0 = OpFunctionParameter %_ptr_Function_v4float
    %error_0 = OpFunctionParameter %_ptr_Function_v4float
         %22 = OpLabel
         %43 = OpLoad %v4float %a_0
         %44 = OpLoad %v4float %b_0
         %45 = OpFSub %v4float %43 %44
         %46 = OpExtInst %v4float %1 FAbs %45
         %47 = OpLoad %v4float %error_0
         %49 = OpFOrdLessThan %v4bool %46 %47
         %50 = OpAll %bool %49
               OpReturnValue %50
               OpFunctionEnd
%i4matchesEither_vi4_vi4_vi4_i1_i1_ = OpFunction %bool None %27
        %a_1 = OpFunctionParameter %_ptr_Function_v4int
        %b_1 = OpFunctionParameter %_ptr_Function_v4int
          %c = OpFunctionParameter %_ptr_Function_v4int
     %errorB = OpFunctionParameter %_ptr_Function_int
     %errorC = OpFunctionParameter %_ptr_Function_int
         %34 = OpLabel
         %53 = OpLoad %v4int %a_1
         %54 = OpLoad %v4int %b_1
         %55 = OpISub %v4int %53 %54
         %56 = OpExtInst %v4int %1 SAbs %55
         %57 = OpLoad %int %errorB
         %58 = OpCompositeConstruct %v4int %57 %57 %57 %57
         %59 = OpSLessThanEqual %v4bool %56 %58
         %60 = OpAll %bool %59
         %61 = OpLogicalNot %bool %60
               OpSelectionMerge %63 None
               OpBranchConditional %61 %62 %63
         %62 = OpLabel
         %64 = OpLoad %v4int %a_1
         %65 = OpLoad %v4int %c
         %66 = OpISub %v4int %64 %65
         %67 = OpExtInst %v4int %1 SAbs %66
         %68 = OpLoad %int %errorC
         %69 = OpCompositeConstruct %v4int %68 %68 %68 %68
         %70 = OpSLessThanEqual %v4bool %67 %69
         %71 = OpAll %bool %70
               OpBranch %63
         %63 = OpLabel
         %72 = OpPhi %bool %60 %34 %71 %62
               OpReturnValue %72
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

1. The host selects a format matrix, sample count, resolve mode, rendering form, memory type, and pipeline construction type. It skips unsupported feature combinations through the test requirements.
2. The host creates color and depth/stencil images, optional resolve images, views, a vertex buffer, verification buffer, diagnostic image, graphics pipeline, and compute pipeline. For the extension path, the relevant single-sampled image receives `VK_IMAGE_CREATE_MULTISAMPLED_RENDER_TO_SINGLE_SAMPLED_BIT_EXT`.
3. The host records attachment clears or initialization, graphics rendering, and any required subpass, render-pass, input-attachment, or dynamic-rendering sequence.
4. For rendering cases, the device runs the fragment shader at the configured sample count and produces the attachment result according to the configured state. In the MSRTSS path the target image itself is single-sampled and carries the extension image-create flag; ordinary `misc` cases use the normal multisample/resolve control path.
5. The host binds the result views to the compute checker through [`setupVerifyDescriptorSetAndPipeline`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L2354-L2427). The compute dispatch compares attachment values over the target area. Partial-area helpers separately check that untouched pixels retain their expected values.
6. [`postVerifyBarrier`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L2429-L2447) makes compute writes available for host reads. The host submits, waits, reads `verificationBuffer`, and logs the diagnostic `verify` image on failure.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | MSRTSS image creation, multisample evaluation, resolve selection, attachment setup, or result verification |
| `clear_attachments` | Clear command handling, clear/load interaction, attachment state, or result verification |
| `multi_subpass` | Subpass dependency, attachment transition, input/resolve state, or multisample handling across subpasses |
| `multi_renderpass` | Resource lifetime, layout transition, synchronization, or MSRTSS state across render passes |
| `input_attachments` | Input-attachment visibility, subpass ordering, resolve state, or attachment format handling |
| `subpass_resolve_efficiency_query` | Resolve-efficiency query support or reported query value |
| `dynamic_rendering` | Dynamic-rendering attachment state, MSRTSS state, resolve behavior, or garbage-attachment handling |

### Cause Analysis

#### `basic`

**Possible failure symptoms:** The computed counters show mismatching color, depth, stencil, or integer pixels. The diagnostic image marks those pixels red.

**Possible implementation causes:** Investigate creation of the single-sampled MSRTSS image, attachment sample state, fragment sample evaluation, resolve-mode selection, format conversion, and the transition to shader-readable layouts. The final resolved image localizes the failure to this rendering-and-observation path, but cannot isolate one pipeline stage without a smaller reproducer.

#### `clear_attachments`

**Possible failure symptoms:** A cleared attachment differs from the configured clear value while adjacent rendering scenarios pass.

**Possible implementation causes:** Investigate `vkCmdClearAttachments` execution, attachment layout and load/clear state, aspect selection, and interaction between the clear and MSRTSS attachment setup. Source-level tracing is needed to distinguish command processing from later verification.

#### `multi_subpass`

**Possible failure symptoms:** Results diverge only when the sequence crosses subpass boundaries.

**Possible implementation causes:** Investigate subpass dependencies, attachment references, layout transitions, visibility to subsequent subpasses, and preservation of the MSRTSS state. This intermediate node combines several attachment operations, so its image result does not identify an exclusive cause.

#### `multi_renderpass`

**Possible failure symptoms:** An earlier rendering sequence appears correct but a later sequence mismatches.

**Possible implementation causes:** Investigate image layout transitions, synchronization and visibility between rendering sequences, attachment lifetime, and restoration of the required multisample state for the next sequence. The relevant sequence is a render-pass instance in the non-dynamic form and a dynamic-rendering instance in the dynamic form.

#### `input_attachments`

**Possible failure symptoms:** Rendering succeeds, but values read through input attachments fail the later comparison.

**Possible implementation causes:** Investigate input-attachment descriptors and references, subpass ordering, depth/stencil aspect selection, shader-readable layout state, and resolve behavior before the input read.

#### `subpass_resolve_efficiency_query`

**Possible failure symptoms:** The query is unavailable despite the case's feature conditions, or its `optimal` field is not populated with a valid boolean value.

**Possible implementation causes:** Investigate the `VkSubpassResolvePerformanceQueryEXT` format-property query and the extension-specific capability path. This intermediate node does not render or compare attachment pixels: it only checks that the queried `optimal` field is populated as `VK_TRUE` or `VK_FALSE`.

#### `dynamic_rendering`

**Possible failure symptoms:** Render-pass cases pass while equivalent dynamic-rendering cases fail, including garbage-color-attachment cases for non-monolithic construction.

**Possible implementation causes:** Investigate dynamic-rendering attachment descriptors, sample-count state, resolve configuration, image layouts, and garbage-attachment validation. Compare the recorded dynamic-rendering state with the corresponding render-pass path before attributing the failure to resolve hardware.

## Case Pruning

### Requirement-based pruning

- The family requires `VK_EXT_multisampled_render_to_single_sampled` for the extension path.
- Format, resolve-mode, sample-count, and Android Hardware Buffer cases are pruned by support checks and test requirements.

### Design-based pruning

- Shader-object construction types register only dynamic-rendering cases.
- `multi_subpass` requires render-pass rendering; `subpass_resolve_efficiency_query` is also restricted to the non-dynamic render-pass construction path.
- `input_attachments` excludes dynamic rendering and shader objects.
- `subpass_resolve_efficiency_query` further requires the extension path and monolithic pipeline construction.
- `garbage_color_attachment` is registered only inside `dynamic_rendering` for non-monolithic construction types.

## Key Takeaways

- This test family checks MSRTSS rendering through observable single-sampled attachment data, not merely successful pipeline creation.
- `basic` provides the central signal: sample-distinct shader values make sample count and resolve choice externally visible.
- The remaining intermediate nodes extend the same core behavior across clears, pass boundaries, input attachment reads, query reporting, and dynamic rendering.
- The `misc` family shares implementation code but remains a separate test family because it exercises the ordinary multisample control configuration.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Main implementation | [`vktPipelineMultisampledRenderToSingleSampledTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L1) |
| Test parameter model | [`TestParams`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L174-L300) |
| MSRTSS image creation | [`makeImage`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L440-L466) |
| Generated basic shaders | [`initBasicPrograms`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L3007-L3250) |
| Group generation | [`createMultisampledTestsInGroup`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L5641-L6065) |
| Extension-family registration | [`createMultisampledRenderToSingleSampledTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6099-L6105) |
| Control-family registration | [`createMultisampledMiscTests`](../../../modules/vulkan/pipeline/vktPipelineMultisampledRenderToSingleSampledTests.cpp#L6107-L6111) |
| Vulkan MSRTSS requirements | [`pipelines.adoc`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L3036-L3048) |
| Vulkan multisample and resolve rules | [`fragops.adoc`](../../../../vulkan-docs/src/chapters/fragops.adoc#L2530-L2545) |
| Monolithic mustpass coverage | [`monolithic.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/monolithic/monolithic.txt) |
| Fast-linked-library mustpass coverage | [`fast-linked-library.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/fast-linked-library.txt) |
| Unlinked shader-object mustpass coverage | [`shader-object-unlinked-spirv.txt`](../../../../vulkancts/mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt) |
