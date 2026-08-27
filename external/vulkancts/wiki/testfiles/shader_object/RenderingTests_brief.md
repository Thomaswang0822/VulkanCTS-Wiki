# Understanding Brief: `shader_object.rendering`

## One-Sentence Test Purpose

This test checks whether graphics shader objects render to dynamic color and depth attachments correctly when fragment output locations, attachment slots, formats, shader binding time, and color-write feature state vary.

## Background Knowledge

### Shader objects and dynamic graphics state

`VK_EXT_shader_object` represents each shader stage with a separate `VkShaderEXT` handle. The application binds those handles to a command buffer with `vkCmdBindShadersEXT` and supplies the graphics state needed by a later draw through dynamic-state commands. Shader objects are not tied to one pipeline or one render pass configuration.

Why it matters here:

- The test binds the same vertex and fragment shader objects either before or after `vkCmdBeginRendering` for the real draw.
- Some cases bind the shaders while an earlier dummy dynamic or traditional render pass is active, then end that pass and reuse the bindings for the real dynamic rendering instance.
- The host sets the required blend, color-write-mask, depth, viewport, scissor, topology, and other shader-object dynamic state before drawing.

### Fragment output locations and dynamic rendering attachment slots

A fragment output with `Location i` is associated with `VkRenderingInfo::pColorAttachments[i]` during dynamic rendering. The array can contain entries whose `imageView` is `VK_NULL_HANDLE`, so an output location can have no image attached. Conversely, the rendering instance can contain an image-backed attachment slot for which the fragment shader declares no output.

Why it matters here:

- Extra fragment outputs create null attachment entries at matching locations.
- Extra image attachments create holes in the shader's output locations. Those attachments keep their clear value because the fragment shader does not write them.
- An output array beginning at location 0 consumes consecutive locations, but the shader can write selected array elements and leave the image-backed holes unchanged.

### Fragment depth replacement

A fragment shader write to `gl_FragDepth` replaces the fragment's calculated depth value for later depth testing and depth attachment writes. If the fragment shader does not replace depth, the vertex shader's position supplies the interpolated depth. This test uses `0.5` in both paths, so the depth image has one stable expected pattern.

## One Concrete Example

Consider this registered case:

```text
dEQP-VK.shader_object.rendering.color_attachment_count_4.extra_attachment_between_1.none.none.same_color_formats.after.none.r8g8b8a8_unorm
```

The host creates five color images: four ordinary attachments plus one extra attachment inserted between them. The fragment shader still has four outputs. Its generator maps those outputs to locations `0`, `1`, `2`, and `4`, leaving location `3` without a fragment output:

```glsl
// Simplified but faithful reconstruction of the generated fragment interface.
layout(location = 0) out vec4 outColor0;
layout(location = 1) out vec4 outColor1;
layout(location = 2) out vec4 outColor2;
layout(location = 4) out vec4 outColor4;

void main()
{
    outColor0 = vec4(1.0);
    outColor1 = vec4(1.0);
    outColor2 = vec4(1.0);
    outColor4 = vec4(1.0);
}
```

A four-vertex triangle strip covers the central 16x16 pixels of each 32x32 image. Attachments 0, 1, 2, and 4 become white in that square. Attachment 3 stays at its clear value and is omitted from the host comparison because it is the deliberate extra attachment.

## End-to-End Test Flow

```text
[host] choose a registered attachment-count branch and its placement, format, binding, depth, and dummy-pass parameters
[host] generate the vertex shader and the parameter-specific fragment output declarations and assignments
[host] reject unsupported attachment counts, image formats, depth formats, or color-write feature requirements
[host] choose the normal device or create a custom device without VK_EXT_color_write_enable for color_write_disable
[host] create 32x32 color images, optional depth image, image views, and host-visible color readback buffers
[host] create vertex and fragment VkShaderEXT objects from the compiled programs
[host] optionally begin a dummy dynamic or traditional render pass and bind the shader objects before ending it
[host] transition real attachments, begin dynamic rendering, set shader-object dynamic state, and bind shaders if the after path was selected
[device] draw a four-vertex triangle strip into the real attachments
[device] write generated fragment outputs and, in gl_frag_write cases, write gl_FragDepth = 0.5
[host] end rendering, barrier color and depth writes for transfer, and copy color images to host-visible buffers
[host] submit and wait
[host] compare each used color attachment with a generated clear-plus-center-square image
[host] copy and inspect the optional depth attachment, expecting 0.5 inside the square and 1.0 outside
[host] return pass only when all required comparisons succeed
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `vertDepth` is fixed GLSL 4.50. It derives positions from `gl_VertexIndex`, emits a quad from `-0.5` to `0.5` in x and y, and sets clip-space z to `0.5`.
- `fragMulti` is generated for each `TestParams` value. It declares separate `vec4`, `ivec4`, or `uvec4` outputs, or one `vec4` output array. Location numbers skip extra image attachments, while extra fragment outputs add declarations whose matching dynamic-rendering entries have null image views.
- `fragMulti` writes `1.0` for floating-point outputs or `255` for integer outputs. It adds `gl_FragDepth = 0.5` in the `gl_frag_write` branch.
- The source collection supplies no explicit `ShaderBuildOptions`, so both programs use the baseline SPIR-V target, SPIR-V 1.0.
- The host configures the real rendering instance through `VkRenderingInfo` and dynamically sets shader-object graphics state. Dummy cases also construct a prior dynamic-rendering instance or a traditional render pass and framebuffer.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color images and views | yes | yes, as dynamic color attachments | cleared and optionally written | yes | They expose location-to-attachment mapping, format conversion, and color-write behavior. |
| Extra color images | yes | yes, at inserted attachment slots | cleared but have no matching shader output | no comparison for deliberate holes | They test image-backed attachment slots that the fragment shader does not write. |
| Null color-attachment entries | yes | yes, as `VkRenderingAttachmentInfo` entries with `imageView = VK_NULL_HANDLE` | receive no image writes | no | They test fragment outputs whose locations have no image attachment. |
| Optional depth image and view | yes | yes, as the dynamic depth attachment | cleared, depth-tested, and written | yes | It distinguishes the rendered center square from the untouched border. |
| Color readback buffers | yes | transfer destinations, not shader descriptors | written by image-to-buffer copies | yes | Host comparisons consume these bytes. |
| Temporary depth readback buffer | yes | transfer destination | written by the depth image copy | yes | The host scans depth values with a 0.02 tolerance. |
| Dummy image and optional framebuffer | yes | yes, in the prior dummy rendering instance | cleared only | no | They place shader binding before the real rendering instance and exercise binding persistence across render pass boundaries. |
| Vertex and fragment shader objects | yes | yes, as command-buffer shader bindings | executed by the draw | no | Their independent binding time is part of the matrix. |

No descriptor sets, push constants, vertex buffers, or shader-visible storage resources participate. The vertex shader synthesizes all positions from `gl_VertexIndex`.

## What Is Checked

- For each used color image, the host builds a 32x32 expected image. The image keeps its format-appropriate clear value outside the central 16x16 square and uses `1.0` or `255` in each used channel inside it.
- Deliberate extra image attachments are excluded from color comparison. They exist to create output-location holes, not to carry expected fragment data.
- Floating-point color formats use `tcu::floatThresholdCompare` with a per-channel threshold of `0.02`. Other formats use `tcu::intThresholdCompare` with a per-channel threshold of `2`.
- With a depth attachment, every central pixel must be within `0.02` of `0.5`, and every border pixel must be within `0.02` of the clear depth `1.0`.
- A case passes only after all applicable color and depth checks succeed. Output-array `color_write_disable` still expects ordinary color writes because the case creates a device without the `colorWriteEnable` feature instead of dynamically disabling attachment writes.

## Behavior Parameter Identification

> **Behavior parameter:** direct intermediate node below `shader_object.rendering`
>
> **Candidate values:** `color_attachment_count_0`, `color_attachment_count_1`, `color_attachment_count_4`, `color_attachment_count_8`, `output_array`

The first four values scale the ordinary dynamic-rendering output/attachment matrix. `output_array` changes the generated fragment interface and the color-write feature setup, so it is a separate behavior value rather than another attachment count.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `color_attachment_count_0` | Drawing with no ordinary color attachments, or with fragment outputs mapped to null dynamic-rendering attachment entries, is mishandled. |
| `color_attachment_count_1` | Single-attachment fragment output mapping, format conversion, shader binding timing, or optional depth handling is wrong. |
| `color_attachment_count_4` | A multi-attachment location map, inserted attachment/output hole, mixed-format selection, binding boundary, or depth path is wrong. |
| `color_attachment_count_8` | The same multi-attachment mechanisms fail at the largest registered base attachment count or near the device attachment limit. |
| `output_array` | Consecutive output-array locations, skipped array elements, or default/explicit color-write enable state is handled incorrectly. |

Shared failures across these values can also come from shader-object creation or binding, required dynamic state, image layout transitions, rendering, transfer copyback, or host-visible memory synchronization.

## Important Variations and Special Cases

- The ordinary matrix uses base color attachment counts `0`, `1`, `4`, and `8`. Extra image attachments and extra fragment outputs each vary among none, one or two before, between, or after the base range, but registration never combines an extra image attachment with an extra fragment output.
- Dummy pass mode is `none`, `dynamic`, or `static`. A non-`none` dummy pass is paired only with the `before` binding path because the source excludes binding after real rendering begins when a dummy pass exists.
- `random_color_formats` appears only for base counts `4` and `8`. A fixed seed selects supported formats for later attachments while preserving the case's named format for the first written attachment. `same_color_formats` uses the named format throughout.
- `gl_frag_write` writes depth from the fragment shader but registers no depth attachment. The `none` branch also registers color-plus-depth-format leaves, so the fixed vertex depth reaches the optional depth image.
- `output_array` fixes four base attachments and two inserted attachments, generates `outColor[6]`, and writes elements 0, 1, 2, and 5. `color_write_enable` requires `VK_EXT_color_write_enable` support and sets all six dynamic enable values to true. `color_write_disable` creates a custom device without that extension and does not issue `vkCmdSetColorWriteEnableEXT`; the name refers to feature disablement, not disabled color output.
- The seven format-named `output_array` intermediate nodes do not change `TestParams::colorFormat`: registration assigns `VK_FORMAT_R8G8B8A8_UNORM` for every one. They therefore generate and execute the same RGBA8 shader/attachment setup for a given color-write mode. This source-to-name mismatch is an unresolved coverage risk, not seven tested output formats.
- The mustpass file contains 240,686 paths: 24,416 under `color_attachment_count_0`, 34,880 under `color_attachment_count_1`, 90,688 each under `color_attachment_count_4` and `color_attachment_count_8`, and 14 under `output_array`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter model and format lists | [vktShaderObjectRenderingTests.cpp#L54-L232](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L54-L232) | Defines the attachment placement, dummy pass, color-write modes, full color format list, and mixed-format pool. |
| Dynamic rendering attachment construction | [vktShaderObjectRenderingTests.cpp#L425-L505](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L425-L505) | Inserts image-backed and null attachment entries at the generated locations. |
| Deterministic format selection | [vktShaderObjectRenderingTests.cpp#L507-L549](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L507-L549) | Selects supported mixed formats with a fixed random seed. |
| Expected image construction | [vktShaderObjectRenderingTests.cpp#L551-L600](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L551-L600) | Builds the clear border and rendered center square for each color format class. |
| Custom device selection | [vktShaderObjectRenderingTests.cpp#L607-L755](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L607-L755) | Removes `VK_EXT_color_write_enable` for the `color_write_disable` path. |
| Rendering and copyback | [vktShaderObjectRenderingTests.cpp#L757-L990](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L757-L990) | Creates attachments and shaders, records dummy and real rendering, draws, and copies color images. |
| Color and depth checks | [vktShaderObjectRenderingTests.cpp#L992-L1067](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L992-L1067) | Contains all pass/fail comparisons and thresholds. |
| Support checks | [vktShaderObjectRenderingTests.cpp#L1092-L1127](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1092-L1127) | Enforces extension, limit, format, depth, and color-write feature requirements. |
| Shader generator | [vktShaderObjectRenderingTests.cpp#L1129-L1191](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1129-L1191) | Generates the fixed vertex program and parameterized fragment outputs. |
| Registration matrix | [vktShaderObjectRenderingTests.cpp#L1200-L1395](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1200-L1395) | Builds all five direct intermediate nodes and applies design exclusions. |
| Shared dynamic-state and binding helpers | [vktShaderObjectCreateUtil.cpp#L244-L447](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L447) | Supplies the shader-object state block and per-stage binding calls used before the draw. |
| Mustpass inventory | [rendering.txt](../../../mustpass/main/vk-default/shader-object/rendering.txt) | Lists all 240,686 executable registration paths. |
| Shader object semantics | [shaders.adoc#L46-L60](../../../../vulkan-docs/src/chapters/shaders.adoc#L46-L60) | Defines independent per-stage shader objects and dynamic state ownership. |
| Fragment output mapping | [interfaces.adoc#L327-L359](../../../../vulkan-docs/src/chapters/interfaces.adoc#L327-L359) | Maps fragment output locations to dynamic-rendering color attachment slots. |
| Depth replacement | [fragops.adoc#L1003-L1010](../../../../vulkan-docs/src/chapters/fragops.adoc#L1003-L1010) | Defines how `FragDepth` replaces the calculated depth used for testing. |
| Color-write enable semantics | [framebuffer.adoc#L1914-L1925](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L1914-L1925) | Distinguishes the feature-disabled default from a false per-attachment enable value. |

## Questions / Risk Points for User Audit

- Is the distinction between an extra image attachment and an extra fragment output clear enough to explain both kinds of location holes?
- Does `color_write_disable` read unambiguously as a custom-device feature-disable case rather than a request to suppress color writes?
- Is the direct intermediate node the most useful behavior parameter, given that each attachment-count branch contains the larger placement, dummy-pass, format, binding, depth, and leaf-format matrix?
- Are two final shader walkthroughs justified: one separate-output hole case and one output-array/custom-device case?
- All seven format-named `output_array` branches execute with `VK_FORMAT_R8G8B8A8_UNORM` because registration never assigns the loop variable to `params.colorFormat`. This appears to leave the six other names without their advertised format coverage and requires source-owner investigation.
- The source's outside-depth failure log says "Color" and "expected to be 0.0" although the check expects depth `1.0`. The comparison itself is clear, but the diagnostic text is misleading and should be reported as a source risk rather than copied as expected behavior.

## Conversion Notes for Final Wiki Rewrite

- Keep short Background Knowledge bullets for shader-object dynamic state, fragment-output location mapping, and depth replacement. Move concrete matrix facts into the parameter and behavior sections.
- Use the concrete `color_attachment_count_4.extra_attachment_between_1...r8g8b8a8_unorm` case as Representative Shader Walkthrough 1. Its separate output declarations show the inserted location hole.
- Use `output_array.r8g8b8a8_unorm.color_write_disable` as Representative Shader Walkthrough 2. Its `outColor[6]` declaration and selected element stores explain the array behavior and the custom-device branch.
- Copy the `### Failure Cause Mapping` table unchanged into the final page. Write detailed cause analysis from the source and spec evidence.
- Keep attachment construction, shader generation, runtime recording, checks, support gates, and registration in the source appendix. Do not carry the brief's teaching flow or full resource table into the final page.
- Report the misleading outside-depth diagnostic as an unresolved source-level risk. Do not alter the C++ source in this documentation task.
