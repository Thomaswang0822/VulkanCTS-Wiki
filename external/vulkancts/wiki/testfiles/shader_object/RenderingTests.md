## Overview

**Core question:** Do graphics shader objects route generated fragment outputs to the correct dynamic-rendering color and depth attachments across output holes, format changes, render-pass boundaries, and shader binding times?

- [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp) implements the five direct intermediate nodes under `shader_object.rendering` and generates 240,686 default-mustpass cases.
- The ordinary matrix combines base color attachment counts `0`, `1`, `4`, and `8` with extra image attachments or extra fragment outputs, dummy render passes, same or mixed color formats, shader binding before or after real rendering begins, optional `gl_FragDepth`, and color/depth format leaves.
- `output_array` fixes six attachment slots and uses one output array whose selected elements skip two image-backed holes. Its two leaves compare normal shader-object rendering with and without the `colorWriteEnable` feature enabled on the device.
- The host checks copied color images with float or integer thresholds and scans optional depth pixels. A failure identifies wrong rendering or copyback, but not a single predetermined implementation layer.

## Background Knowledge

For the shared concepts shader objects, dynamic state, and dynamic rendering, see [Background Knowledge](../../categories/shader_object.md#background-knowledge) of the `shader_object` page.

- **Fragment output locations.** During dynamic rendering, a fragment output at `Location i` maps to `VkRenderingInfo::pColorAttachments[i]`. A null image view creates an output location with no image, while an image-backed slot with no matching output keeps its clear value.
- **Depth replacement.** A `gl_FragDepth` write replaces the calculated fragment depth used by depth testing and depth attachment writes. The generated vertex and fragment paths both provide `0.5` for the covered square in this test.

## Registration Hierarchy

```text
shader_object.rendering
├── color_attachment_count_0
├── color_attachment_count_1
├── color_attachment_count_4
├── color_attachment_count_8
└── output_array
```

These five direct children are intermediate nodes below the `rendering` test family. The first four expand through seven deeper dimensions before the color or color-plus-depth test case leaf. `output_array` expands through a format-named intermediate node and a color-write leaf. The root file registers `rendering` directly
([parent registration](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)), and the mustpass inventory contains all 240,686 paths
([rendering.txt](../../../mustpass/main/vk-default/shader-object/rendering.txt)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct intermediate node | `color_attachment_count_0`, `color_attachment_count_1`, `color_attachment_count_4`, `color_attachment_count_8`, `output_array` | Selects the base attachment count or the separate output-array mechanism. | [top-level registration](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1200-L1213), [output array](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1355-L1393) |
| Extra image attachment | `none`, `extra_attachment_before_1`, `extra_attachment_between_1`, `extra_attachment_after_1`, and the corresponding `_2` values | Inserts one or two image-backed attachment slots without matching fragment outputs. | [extraAttachmentTests](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1215-L1226) |
| Extra fragment output | `none`, `extra_output_before_1`, `extra_output_between_1`, `extra_output_after_1`, and the corresponding `_2` values | Adds one or two fragment outputs whose matching rendering attachment entries have null image views. | [extraOutputTests](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1228-L1239) |
| Dummy rendering mode | `none`, `dynamic`, `static` | Optionally binds shaders while a prior dynamic or traditional render pass is active, then reuses them in the real dynamic rendering instance. | [dummyRenderPassTests](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1241-L1245), [recording branch](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L869-L894) |
| Attachment formats | `same_color_formats`; `random_color_formats` for base counts 4 and 8 | Uses the named color format throughout or chooses supported later formats with fixed seed `102030`. | [format nodes](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1265-L1273), [selection](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L507-L549) |
| Shader bind time | `before`, `after` | Binds the graphics shader objects before or after `vkCmdBeginRendering` for the real draw. | [bind nodes](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1274-L1279), [draw recording](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L883-L950) |
| Depth mode | `gl_frag_write`, `none` | Generates a fragment depth write or omits it; only `none` also expands to leaves with depth attachments. | [depth nodes and leaves](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1280-L1336) |
| Color/depth format leaf | 109 named color formats, alone or suffixed with one of the depth formats from `formats::depthFormats` | Controls image format class, generated output type, clear value, copyback layout, and comparison path. | [colorFormats](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L96-L206), [leaf creation](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1308-L1336) |
| Output-array format name | `r8_unorm`, `r8g8b8a8_unorm`, `r8g8b8a8_snorm`, `r32_uint`, `r32_sint`, `r32_sfloat`, `r32g32b32a32_sfloat` | Names seven branches, but the current registration assigns `VK_FORMAT_R8G8B8A8_UNORM` to `TestParams::colorFormat` for all seven. | [output-array loop](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1361-L1389) |
| Color-write feature mode | `color_write_enable`, `color_write_disable` | Requires and uses the feature in the first leaf. The second uses the normal device when the feature is unsupported; otherwise it creates a custom device without the extension. Both paths still expect color writes. | [colorWriteTests](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1355-L1359), [device selection](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L607-L751), [dynamic state](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L939-L943) |

## Behavior Parameters

The primary behavioral axis is the **direct intermediate node below `shader_object.rendering`**. The attachment-count values share one generated matrix and scale its ordinary color-output mapping. `output_array` changes the shader interface and device feature setup.

### color_attachment_count_0: outputs without ordinary color images

This value begins with no base color attachment. Registered executable cases can still add fragment outputs, whose matching `VkRenderingAttachmentInfo` entries have null image views. Extra image attachments are excluded because their count would exceed the base attachment count. The draw must complete without treating an unbacked output location as an image write.

### color_attachment_count_1: single-attachment mapping

This value checks the smallest ordinary color target across the same output-hole, dummy-pass, bind-time, depth, and format dimensions. Registration excludes `random_color_formats` because fewer than two base attachments cannot demonstrate mixed attachment formats.

### color_attachment_count_4: multi-attachment mapping

Four base attachments allow inserted image holes, inserted output holes, and deterministic mixed formats while staying within common device limits. This branch exposes wrong location arithmetic because outputs after an inserted image attachment move to higher locations, while extra outputs create null attachment entries instead.

### color_attachment_count_8: largest registered base count

Eight base attachments apply the same mechanism at the largest fixed count. Support checks compare the complete attachment/output count with `maxColorAttachments`, so devices with smaller limits skip over-limit combinations rather than running an illegal draw.

### output_array: array locations and color-write feature state

This value creates four base color attachments plus two inserted attachments and generates `layout(location = 0) out vec4 outColor[6]`. The shader writes elements 0, 1, 2, and 5; elements 3 and 4 correspond to the inserted image attachments, receive no shader stores, and are not compared by the host. `color_write_enable` sets six true dynamic enable values. For `color_write_disable`, the host uses the normal device when the feature is unsupported; otherwise it removes `VK_EXT_color_write_enable` from a custom device. In either case, the feature-disabled default still permits writes according to the color write masks.

The seven format-named branches currently run the same `VK_FORMAT_R8G8B8A8_UNORM` setup because the loop variable is not assigned to `params.colorFormat`. The names therefore exceed the exercised format coverage; see `## Case Pruning` and the unresolved risk in `## Key Takeaways`.

## Shader Analysis

Two fragment shaders are needed because the ordinary matrix declares separate location-qualified outputs, while `output_array` declares one array and uses element indices to cross the attachment holes. Both walkthroughs come from `ShaderObjectRenderingCase::initPrograms`; their source collection uses the baseline SPIR-V 1.0 target.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.shader_object.rendering.color_attachment_count_4.extra_attachment_between_1.none.none.same_color_formats.after.none.r8g8b8a8_unorm
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `color_attachment_count_4` | Four ordinary outputs are generated. |
| `extra_attachment_between_1` | One image-backed attachment is inserted after output location 2, so the last shader output moves to location 4. |
| `none.none.same_color_formats.after.none` | There are no extra shader outputs or dummy pass, every image uses RGBA8 UNORM, shaders bind after real rendering begins, and the fragment shader does not replace depth. |
| `r8g8b8a8_unorm` | All generated outputs use `vec4(1.0)` and the host expects a white center square. |

#### Purpose

This shader checks that a missing fragment output at one image-backed dynamic-rendering slot does not shift later output-to-attachment mappings.

#### Structural Design

| Generated output | Dynamic attachment slot | Device write |
|------------------|-------------------------|--------------|
| `outColor0` | 0 | white center square |
| `outColor1` | 1 | white center square |
| `outColor2` | 2 | white center square |
| no output | 3, the inserted attachment | keeps clear value |
| `outColor4` | 4 | white center square |

#### Shader Code

```glsl
#version 450
/// Four vec4 outputs target five dynamic-rendering slots. Location 3 is the deliberate image-backed hole.
layout (location = 0) out vec4 outColor0;
layout (location = 1) out vec4 outColor1;
layout (location = 2) out vec4 outColor2;
layout (location = 4) out vec4 outColor4;
void main() {
    /// The rasterized quad supplies coverage; each declared output writes white to its matching image.
    outColor0 = vec4(1.0f);
    outColor1 = vec4(1.0f);
    outColor2 = vec4(1.0f);
    outColor4 = vec4(1.0f);
}
```

#### Additional Info

- The fixed vertex shader derives a four-vertex triangle strip from `gl_VertexIndex` and places it from `-0.5` to `0.5` in x and y. It does not vary across this page's cases and only supplies the covered center square.
- The host omits attachment 3 from color comparison because it was inserted to test the interface hole. Attachments 0, 1, 2, and 4 remain fully checked.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Extra image attachment placement/count | Moves later output locations forward by one or two slots, creating image-backed locations with no fragment output. | [location generation](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1150-L1163) |
| Extra fragment output placement/count | Adds outputs while the host places null image views at their matching dynamic-rendering slots. | [output generation](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1141-L1184) |
| Color format class | Selects `uvec4(255)`, `ivec4(255)`, or `vec4(1.0)` for the first written or same-format outputs. | [type and assignment branches](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1155-L1183) |
| Fragment depth | Adds `gl_FragDepth = 0.5f` in `gl_frag_write` cases. | [depth generation](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1185-L1187) |

#### SPIR-V

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
; Bound: 15
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor0 %outColor1 %outColor2 %outColor4
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %outColor0 "outColor0"
               OpName %outColor1 "outColor1"
               OpName %outColor2 "outColor2"
               OpName %outColor4 "outColor4"
               OpDecorate %outColor0 Location 0
               OpDecorate %outColor1 Location 1
               OpDecorate %outColor2 Location 2
               OpDecorate %outColor4 Location 4
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %outColor0 = OpVariable %_ptr_Output_v4float Output
    %float_1 = OpConstant %float 1
         %11 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
  %outColor1 = OpVariable %_ptr_Output_v4float Output
  %outColor2 = OpVariable %_ptr_Output_v4float Output
  %outColor4 = OpVariable %_ptr_Output_v4float Output
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %outColor0 %11
               OpStore %outColor1 %11
               OpStore %outColor2 %11
               OpStore %outColor4 %11
               OpReturn
               OpFunctionEnd
```

</details>

### Representative Shader Walkthrough 2

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.shader_object.rendering.output_array.r8g8b8a8_unorm.color_write_disable
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `output_array` | Generates one six-element output array at location 0 and writes around two inserted attachment holes. |
| `r8g8b8a8_unorm` | This branch name agrees with the fixed RGBA8 UNORM `TestParams::colorFormat` used by every output-array branch. |
| `color_write_disable` | Runs without the `colorWriteEnable` feature, creating a custom device without `VK_EXT_color_write_enable` only when the normal device exposes the feature; it does not disable the attachment writes themselves. |

#### Purpose

This shader checks consecutive location assignment for an output array when selected array elements skip image-backed attachment slots. The case also checks that shader-object rendering works when the color-write-enable feature is absent.

#### Structural Design

| Array element | Effective location | Device write |
|---------------|--------------------|--------------|
| `outColor[0]` | 0 | white center square |
| `outColor[1]` | 1 | white center square |
| `outColor[2]` | 2 | white center square |
| `outColor[3]`, `outColor[4]` | 3, 4 | no shader store; host does not compare these images |
| `outColor[5]` | 5 | white center square |

#### Shader Code

```glsl
#version 450
/// The six-element array consumes locations 0 through 5. Elements 3 and 4 match deliberate image-backed holes.
layout(location = 0) out vec4 outColor[6];
void main() {
    /// Only elements backed by the four ordinary attachments receive stores.
    outColor[0] = vec4(1.0f);
    outColor[1] = vec4(1.0f);
    outColor[2] = vec4(1.0f);
    outColor[5] = vec4(1.0f);
}
```

#### Additional Info

- The fixed vertex shader supplies the same center-square coverage as in Walkthrough 1 and does not participate in output-array indexing.
- The branch label `color_write_disable` means the active logical device lacks the `colorWriteEnable` feature. A custom device is needed only when the normal device exposes the feature. The host omits `vkCmdSetColorWriteEnableEXT`, and normal color writes remain enabled through the write masks.
- The six other format-named output-array branches reconstruct to this same shader because registration fixes `params.colorFormat` to `VK_FORMAT_R8G8B8A8_UNORM`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Color-write leaf | Does not alter GLSL; it changes device feature enablement and whether the host records `vkCmdSetColorWriteEnableEXT`. | [feature and command branches](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L618-L633), [dynamic command](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L939-L943) |
| Format-named intermediate node | Does not alter GLSL in current source because all seven registrations keep `params.colorFormat = VK_FORMAT_R8G8B8A8_UNORM`. | [output-array registration](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1361-L1389) |
| Output array versus separate outputs | Replaces separate location-qualified variables with `outColor[6]` and indexed stores. | [array generator](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1141-L1177) |

#### SPIR-V

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
; Bound: 25
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %outColor "outColor"
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
       %uint = OpTypeInt 32 0
     %uint_6 = OpConstant %uint 6
%_arr_v4float_uint_6 = OpTypeArray %v4float %uint_6
%_ptr_Output__arr_v4float_uint_6 = OpTypePointer Output %_arr_v4float_uint_6
   %outColor = OpVariable %_ptr_Output__arr_v4float_uint_6 Output
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
    %float_1 = OpConstant %float 1
         %16 = OpConstantComposite %v4float %float_1 %float_1 %float_1 %float_1
%_ptr_Output_v4float = OpTypePointer Output %v4float
      %int_1 = OpConstant %int 1
      %int_2 = OpConstant %int 2
      %int_5 = OpConstant %int 5
       %main = OpFunction %void None %3
          %5 = OpLabel
         %18 = OpAccessChain %_ptr_Output_v4float %outColor %int_0
               OpStore %18 %16
         %20 = OpAccessChain %_ptr_Output_v4float %outColor %int_1
               OpStore %20 %16
         %22 = OpAccessChain %_ptr_Output_v4float %outColor %int_2
               OpStore %22 %16
         %24 = OpAccessChain %_ptr_Output_v4float %outColor %int_5
               OpStore %24 %16
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The instance normally uses the context device. For `output_array.*.color_write_disable`, it creates a custom device without `VK_EXT_color_write_enable` only when the context reports the feature as supported; otherwise the already feature-disabled context device is used
  ([device selection](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L607-L755)).
- Every case uses a 32x32 render area. The host creates one color image and host-visible transfer buffer per image-backed color slot, plus an optional depth image. The output-array path therefore has six color images even though only four receive fragment stores
  ([resource setup](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L776-L851)).
- The vertex and fragment binaries become independent `VkShaderEXT` objects. Dummy cases begin an earlier dynamic or traditional render pass, bind the shader objects there, end it, and later begin the real dynamic rendering instance. Other cases bind before or after the real `vkCmdBeginRendering`, according to the registered `before` or `after` value
  ([recording](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L853-L950)).
- The host records the shared shader-object dynamic-state block, disables blending, enables all color components, enables depth test/write with compare op `LESS`, null-binds optional task and mesh stages, and draws a four-vertex triangle strip
  ([dynamic state and draw](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L916-L952), [shared state helper](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L244-L418)).
- The draw covers the central 16x16 part of each 32x32 image. Used color attachments contain `1.0` or integer `255` in each format channel inside that square and their clear value outside. Deliberate extra image attachments are skipped. Float formats use a `0.02` threshold, while non-float formats use an integer threshold of `2`
  ([expected image](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L551-L600), [color checks](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L997-L1029)).
- If a depth attachment exists, the host copies it through a temporary buffer and scans every pixel. Covered pixels must be within `0.02` of `0.5`; border pixels must be within `0.02` of the clear depth `1.0`
  ([depth copy](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L234-L311), [depth check](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1031-L1064)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `color_attachment_count_0` | Drawing with no ordinary color attachments, or with fragment outputs mapped to null dynamic-rendering attachment entries, is mishandled. |
| `color_attachment_count_1` | Single-attachment fragment output mapping, format conversion, shader binding timing, or optional depth handling is wrong. |
| `color_attachment_count_4` | A multi-attachment location map, inserted attachment/output hole, mixed-format selection, binding boundary, or depth path is wrong. |
| `color_attachment_count_8` | The same multi-attachment mechanisms fail at the largest registered base attachment count or near the device attachment limit. |
| `output_array` | Consecutive output-array locations, skipped array elements, or default/explicit color-write enable state is handled incorrectly. |

Shared failures across these values can also come from shader-object creation or binding, required dynamic state, image layout transitions, rendering, transfer copyback, or host-visible memory synchronization.

### Cause Analysis

#### Fragment output and attachment location mismatch

**Possible failure symptoms:** One used color image remains at its clear value, receives a neighboring output, or contains white at the wrong slot. Cases with an inserted attachment or output fail while their `none` counterpart passes. An output-array case may miss the checked write from element 5; the inserted images corresponding to unwritten elements 3 and 4 are not compared.

**Possible implementation causes:** The Vulkan fragment output interface maps `Location i` to dynamic color attachment slot `i`. A driver that compacts null image views, compacts missing shader locations, assigns array elements incorrectly, or builds the shader-object fragment output interface from the number of image-backed views rather than their positions will shift these writes.

#### Shader binding or render-pass boundary failure

**Possible failure symptoms:** `before` cases fail while `after` cases pass, or dummy `dynamic` and `static` cases fail while dummy `none` passes. All checked attachments may stay clear because the draw ran without the intended shader objects.

**Possible implementation causes:** Shader-object bindings are command-buffer state and are independent of a render pass instance. An implementation that clears or snapshots those bindings at `vkCmdBeginRendering`, `vkCmdEndRendering`, `vkCmdBeginRenderPass`, or `vkCmdEndRenderPass` can lose bindings recorded in the earlier dummy instance or mishandle the bind order around the real instance.

#### Format-class conversion or mixed-format failure

**Possible failure symptoms:** Only integer, scaled, normalized, sRGB, or mixed-format cases fail. The comparison log shows correct coverage but wrong channel values, or only later attachments fail in `random_color_formats` cases.

**Possible implementation causes:** The generated fragment interface selects signed integer, unsigned integer, or floating-point output types from the named format and emits `255` or `1.0`. A mismatch can result from incorrect shader-output type handling, fragment-output compatibility, color conversion, channel packing, or per-location format state. A transfer copy or host interpretation defect can produce the same image signature, so the failing log needs source-level investigation before assigning one layer.

#### Depth replacement or depth attachment failure

**Possible failure symptoms:** Color checks pass, but the depth scan reports a central value outside `0.5 ± 0.02` or a border value outside `1.0 ± 0.02`. Failures may follow a particular depth format.

**Possible implementation causes:** The covered fragments must pass `LESS` against clear depth 1.0 and write 0.5, from the fixed vertex depth in attachment cases. Incorrect shader depth, depth-test/write dynamic state, depth format storage, image barrier, aspect copy, or copyback conversion can create the mismatch. `gl_frag_write` cases have no depth attachment, so they check shader creation and draw execution with depth replacement declared, not depth image values.

#### Color-write feature-state failure

**Possible failure symptoms:** `output_array.*.color_write_enable` or `color_write_disable` leaves used attachments clear while the other leaf passes. When the feature is supported by the context, a failure in `color_write_disable` occurs on the custom-device path; otherwise that leaf uses the normal device.

**Possible implementation causes:** When the feature is enabled, shader-object draws require `vkCmdSetColorWriteEnableEXT` values for every active color attachment; the test supplies six true values. When the feature is disabled, the command is unavailable and color writes follow the masks without that dynamic state. A driver that requires the state despite the disabled feature, or defaults writes to false, will fail the custom-device case.

#### Rendering, synchronization, or copyback failure

**Possible failure symptoms:** Many unrelated branches fail with clear or corrupted images, comparison values vary across runs, or both color and depth results are wrong.

**Possible implementation causes:** The test transitions images to `GENERAL`, records attachment-write-to-transfer-read barriers, copies color images into host-visible buffers, waits for submission, and invalidates mapped allocations. A defect in rendering, barriers, image-to-buffer copy, format-aware row interpretation, or host cache invalidation can all surface through the same final comparisons. The specific image log and device trace are needed to distinguish them.

## Case Pruning

### Requirement-based pruning

- Every case requires `VK_EXT_shader_object`. The complete color attachment, extra attachment, and extra output count must not exceed `VkPhysicalDeviceLimits::maxColorAttachments`
  ([support check](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1092-L1103)).
- The named color format must support optimal-tiling color attachment and transfer-source usage. Depth leaves also require the selected depth format to support depth/stencil attachment and transfer-source usage
  ([format queries](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1105-L1121)).
- `output_array.*.color_write_enable` requires the `colorWriteEnable` feature. The `color_write_disable` leaf has no such requirement: it uses the normal device when the feature is unsupported and otherwise creates a device without the extension
  ([feature gate](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1122-L1126)).
- `setColorFormats` chooses each random later attachment only from formats that pass an image-format query on the device. The fixed seed keeps the accepted sequence deterministic for a given support set
  ([mixed-format selection](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L518-L540)).

### Design-based pruning

- Registration never combines a nonzero extra image attachment with a nonzero extra fragment output. Each case isolates one direction of the interface mismatch
  ([combination skip](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1251-L1257)).
- `random_color_formats` is skipped for base attachment counts 0 and 1 because there are fewer than two base outputs to compare
  ([format skip](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1265-L1269)).
- A case is omitted when `extraAttachmentCount` exceeds the base color attachment count. This removes placements whose inserted-hole model would dominate the ordinary outputs
  ([leaf skip](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1308-L1311)).
- Binding `after` is omitted when a dummy render pass exists. Dummy cases isolate whether a binding recorded inside the earlier instance survives its end; they do not add a second after-binding path
  ([bind/dummy skip](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1313-L1315)).
- `gl_frag_write` registers color-only leaves. The `none` depth-mode branch adds every depth format, so the depth attachment check uses the fixed vertex depth instead of combining two sources of 0.5
  ([depth expansion](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1322-L1336)).
- The `output_array` registration loops over seven format names but never copies the loop variable into `params.colorFormat`; every branch uses `VK_FORMAT_R8G8B8A8_UNORM`. This is not intentional pruning expressed by a source guard. It is an unresolved source coverage risk and requires investigation before the names can be treated as seven tested formats
  ([registration](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1361-L1389)).

## Key Takeaways

- The ordinary matrix checks both sides of fragment-output mismatch: shader locations with null attachment views and image-backed attachment slots with no shader output.
- Shader bindings must survive dynamic and traditional render-pass boundaries, and binding before or after real dynamic rendering begins must produce the same checked images.
- Format classes affect shader output types and host comparison methods; mixed-format cases also test independent per-location attachment formats.
- Output arrays consume consecutive locations, but this shader leaves elements 3 and 4 unwritten. The host validates the four written attachments and omits the two corresponding inserted images from comparison.
- The `color_write_disable` leaf runs with the device feature disabled; it does not disable the writes. The host still expects the four ordinary attachments to receive white center squares.
- The seven output-array format names currently collapse to one RGBA8 setup. This is an unresolved source coverage risk in [the registration code](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1361-L1389).
- The outside-depth failure diagnostic says "Color" and "expected to be 0.0" even though the check expects depth `1.0`; this affects failure reporting, not the pass condition
  ([depth diagnostic](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1053-L1059)).
- See `## Failure Meaning` for the evidence each comparison pattern provides and the implementation areas that can produce it.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Parameter model and format inventory | [vktShaderObjectRenderingTests.cpp#L54-L232](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L54-L232) | Defines attachment placement, dummy pass, color-write modes, and the ordinary color format pools. |
| Dynamic attachment list construction | [vktShaderObjectRenderingTests.cpp#L425-L505](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L425-L505) | Places image views and null entries at the locations consumed by fragment outputs. |
| Expected color image | [vktShaderObjectRenderingTests.cpp#L551-L600](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L551-L600) | Builds format-aware clear values and the rendered center square. |
| Custom device path | [vktShaderObjectRenderingTests.cpp#L607-L755](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L607-L755) | Removes `VK_EXT_color_write_enable` for the feature-disabled output-array leaf. |
| Main execution path | [vktShaderObjectRenderingTests.cpp#L757-L990](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L757-L990) | Creates resources and shader objects, records dummy and real rendering, draws, barriers, and copies color images. |
| Color and depth validation | [vktShaderObjectRenderingTests.cpp#L992-L1067](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L992-L1067) | Implements all thresholds, skipped inserted attachments, depth scan, and final status. |
| Support checks | [vktShaderObjectRenderingTests.cpp#L1092-L1127](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1092-L1127) | Applies extension, attachment-limit, image-format, depth-format, and feature requirements. |
| Shader generator | [vktShaderObjectRenderingTests.cpp#L1129-L1191](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1129-L1191) | Generates the fixed vertex shader and all separate-output or array fragment shaders. |
| Registration | [vktShaderObjectRenderingTests.cpp#L1200-L1395](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1200-L1395) | Builds the complete ordinary and output-array matrices and their design exclusions. |
| Shared shader-object helpers | [vktShaderObjectCreateUtil.cpp#L220-L447](../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L220-L447) | Builds shader create info, sets required dynamic state, and binds graphics stages. |
| Parent registration | [vktShaderObjectTests.cpp#L47-L63](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) | Adds the `rendering` test family under `shader_object`. |
| Mustpass inventory | [rendering.txt](../../../mustpass/main/vk-default/shader-object/rendering.txt) | Lists all 240,686 executable paths used for registration audit. |
| Shader object semantics | [shaders.adoc#L46-L60](../../../../vulkan-docs/src/chapters/shaders.adoc#L46-L60) | Defines per-stage shader objects and their dynamic-state model. |
| Shader object binding and state | [shaders.adoc#L911-L1023](../../../../vulkan-docs/src/chapters/shaders.adoc#L911-L1023) | Defines command-buffer stage binding and the requirement to set relevant dynamic state before drawing. |
| Fragment output interface | [interfaces.adoc#L327-L359](../../../../vulkan-docs/src/chapters/interfaces.adoc#L327-L359) | Maps output locations to dynamic-rendering attachment slots. |
| Dynamic rendering | [renderpass.adoc#L9-L46](../../../../vulkan-docs/src/chapters/renderpass.adoc#L9-L46) | Defines dynamic render pass instances and their feature requirement. |
| Depth replacement | [fragops.adoc#L1003-L1010](../../../../vulkan-docs/src/chapters/fragops.adoc#L1003-L1010) | Defines how `FragDepth` replaces calculated fragment depth. |
| Color-write enable | [framebuffer.adoc#L1914-L1925](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L1914-L1925) | Defines feature-disabled behavior and per-attachment write suppression. |
