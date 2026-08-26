## Overview

**Core question:** Under dynamic rendering, when fragment shaders read back attachments written by earlier draws in the same render pass instance, does `VK_KHR_dynamic_rendering_local_read` map color attachment locations and input attachment indices correctly across the full range of remapping, depth/stencil interaction, and extension-interaction cases?

- [vktDynamicRenderingLocalReadTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp) implements the `local_read` test family under the `dynamic_rendering` test category.
- The test family is registered under both `primary_cmd_buff` and `partial_secondary_cmd_buff`, so most cases run once on a primary command buffer and once when the draws are recorded into secondary command buffers
  [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8535),
  [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8544).
- The core test idea is a two-phase render: a write pipeline stores values into color and depth/stencil attachments using a `VkRenderingAttachmentLocationInfo` remapping, then a memory barrier inside the render pass instance makes those writes visible, and a read pipeline loads the same images as input attachments using a `VkRenderingInputAttachmentIndexInfo` remapping. The output buffer must equal a host-computed expected value derived from the two remapping tables.
- The page explains what each registered case changes about that remapping contract, how the shaders consume the remapped indices, and what a mismatched output means.

## Background Knowledge

- **Dynamic rendering local read.** `VK_KHR_dynamic_rendering_local_read` lets a fragment shader read values written by an earlier draw in the same dynamic render pass instance. Pipeline barriers with `VK_DEPENDENCY_BY_REGION_BIT` between framebuffer-space stages make prior attachment writes visible to a later input attachment load. Resources used this way live in `VK_IMAGE_LAYOUT_RENDERING_LOCAL_READ_KHR` (or `VK_IMAGE_LAYOUT_GENERAL`). The proposal treats this as the dynamic-rendering equivalent of a subpass self-dependency in a render pass object
  [VK_KHR_dynamic_rendering_local_read proposal](../../../../vulkan-docs/src/proposals/VK_KHR_dynamic_rendering_local_read.adoc).
- **Color attachment location remapping.** `VkRenderingAttachmentLocationInfoKHR` reorders which framebuffer color location a given color attachment index maps to. The mapping is supplied both at pipeline creation (chained to `VkPipelineRenderingCreateInfo`) and at record time (`vkCmdSetRenderingAttachmentLocations`). Shader `location` outputs follow the remapped location, not the raw attachment index. Blend state and format always track the raw attachment index, so remapping changes where a shader writes but not how blending applies
  [proposal, Color Attachment Remapping](../../../../vulkan-docs/src/proposals/VK_KHR_dynamic_rendering_local_read.adoc).
- **Input attachment index remapping.** `VkRenderingInputAttachmentIndexInfoKHR` controls which `InputAttachmentIndex` a given color or depth/stencil attachment is reachable through. Setting a pointer to `NULL` means the attachment is only reachable through a shader variable that omits the `InputAttachmentIndex` decoration; setting it to `VK_ATTACHMENT_UNUSED` means the attachment is not reachable as an input attachment at all. When the structure is not provided, each color attachment defaults to `InputAttachmentIndex` equal to its index
  [proposal, Input Attachment Mapping](../../../../vulkan-docs/src/proposals/VK_KHR_dynamic_rendering_local_read.adoc).
- **Input attachment descriptor binding.** Regardless of the remapping, the shader still loads an input attachment through a descriptor. The test binds all input attachments into a single descriptor set whose binding order matches the `InputAttachmentIndex` values the read shader expects, so a correct remapping must line the descriptor up with the right image view.

## Registration Hierarchy

```text
renderpasses.dynamic_rendering.primary_cmd_buff.local_read
├── depth_mapping_stencil_not
├── depth_stencil_mapping_to_large_index
├── depth_stencil_mapping_to_no_index
├── depth_stencil_mapping_to_no_index_depth_clear
├── depth_stencil_mapping_to_no_index_stencil_clear
├── depth_stencil_mapping_to_same_index
├── feedback_loop
├── feedback_loop_msaa
├── feedback_loop_with_shader_object
├── input_attachments_without_mapping
├── interaction_with_color_write_enable
├── interaction_with_extended_dynamic_state3
├── interaction_with_graphics_pipeline_library
├── interaction_with_shader_object
├── mapping_1_attachments_to_locs_from_1
├── mapping_1_attachments_to_locs_from_2
├── mapping_1_attachments_to_locs_from_3
├── mapping_2_attachments_to_locs_from_2
├── mapping_not_affecting_blend_state
├── max_attachments_remapped_repeatedly
├── max_input_attachments
├── null_color_attachment_location_with_command
├── null_color_attachment_location_with_command_after_remap
├── null_color_attachment_location_with_locationinfo
├── null_color_attachment_location_with_locationinfo_before_identity
├── remap_single_attachment_fast_lib
├── remap_single_attachment_monolithic
├── remap_single_attachment_shader_object
└── unused_writen_discarded
```

The same 21 `TestType`-driven cases are also registered under `renderpasses.dynamic_rendering.partial_secondary_cmd_buff.local_read`, and the four `mapping_*_attachments_to_locs_from_*` cases are registered under both command buffer modes, giving 25 `partial_secondary_cmd_buff` leaves. Only the four `null_color_attachment_location_*` cases are added solely under `primary_cmd_buff`, because they exercise pipeline-create info paths guarded by `!grpParams->useSecondaryCmdBuffer`
[registration](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3744-L3821).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| TestType | 21 enum values | Selects the remapping shape, the attachment count, and which extension interaction is exercised. Each value maps to exactly one registered case name. | [TestType](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L59-L123), [testConfigs](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3751-L3773) |
| Command buffer mode | `primary_cmd_buff`, `partial_secondary_cmd_buff` | Runs the same TestType with draws recorded into secondary command buffers, exercising the `VkCommandBufferInheritanceInfo` pNext path for both remapping structures. | [registration sites](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8535), [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8544) |
| Color attachment count | device-dependent for `max_*`; fixed 0, 2, 3, or 4 otherwise | Drives the width of the `pColorAttachmentLocations` and `pColorAttachmentInputIndices` arrays and the number of shader color outputs. | [constructor switch](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L267-L425) |
| Depth/stencil input indices | `VK_ATTACHMENT_UNUSED`, same index, large index (20, 21), or NULL | Tests the four spec-permitted shapes for `pDepthInputAttachmentIndex` and `pStencilInputAttachmentIndex`. | [constructor switch](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L352-L402) |
| Null location mode | `commandMode`, `nullAfterRemap`, `nullBeforeIdentity` | For `null_color_attachment_location_*` cases, picks whether the NULL `pColorAttachmentLocations` is set by command or by pipeline-create info, and whether a non-identity remap precedes it. | [registration](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3782-L3798) |
| High-location remap | `numAttachments` in {1, 2}, `firstRemapLocation` in 1..3 | For `mapping_*_attachments_to_locs_from_*` cases, maps attachments to locations at or above their default indices, including otherwise unused high locations. | [registration](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3802-L3818) |

## Behavior Parameters

The primary behavioral axis is the registered case leaf (the `TestType` value). Each case changes the remapping contract being verified: which attachments are mapped, whether depth/stencil participates, which extension the remapping interacts with, or whether the remapping is expressed through command state versus pipeline-create state. The 29 `primary_cmd_buff` leaves group into seven behavioral clusters.

### Color and depth/stencil remapping shape

These cases use the `BasicLocalReadTestInstance` write-then-read flow with different `VkRenderingInputAttachmentIndexInfo` shapes.

- `depth_stencil_mapping_to_no_index` sets both depth and stencil pointers to NULL, so the read shader must reach them through SPIR-V variables that omit `InputAttachmentIndex`. Because glslang cannot yet emit that GLSL, the read shader is hand-written SPIR-V assembly
  [frag1 SPIR-V](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2629-L2730).
- `depth_stencil_mapping_to_no_index_depth_clear` and `depth_stencil_mapping_to_no_index_stencil_clear` isolate one aspect of the depth/stencil image (depth-only or stencil-only format), clear it, and read it back through a NULL index using SPIR-V assembly
  [constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L360-L378),
  [frag1 SPIR-V](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2774-L2840).
- `depth_stencil_mapping_to_same_index` maps both depth and stencil to input attachment index 2.
- `depth_stencil_mapping_to_large_index` maps depth to 20 and stencil to 21, requiring `maxPerStageDescriptorInputAttachments >= 21`.
- `depth_mapping_stencil_not` maps depth to index 4 and sets stencil to `VK_ATTACHMENT_UNUSED`, so the shader reads depth but not stencil
  [constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L396-L402).
- `max_input_attachments` sizes the color attachment count to `min(maxColorAttachments, maxPerStageDescriptorInputAttachments - 2)` and clears the input index array so the implementation uses the default identity mapping
  [constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L269-L293),
  [descriptor clear](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L733-L735).
- `max_attachments_remapped_repeatedly` uses half as many input draws as attachments and three output draws, each with a different full-attachment remapping (reversed, alternating low-high, and identity), to stress repeated remapping of the same attachment set
  [constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L294-L334).
- `input_attachments_without_mapping` never calls the remapping commands and expects the default identity mapping to work, reading three color attachments plus depth through a NULL index
  [constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L336-L342).
- `unused_writen_discarded` marks color attachment locations 0 and 2 as `VK_ATTACHMENT_UNUSED` and confirms those writes are discarded while the mapped locations still produce the expected readback
  [constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L344-L350).

### Blend-state isolation

- `mapping_not_affecting_blend_state` uses `MappingWithBlendStateTestInstance`. Four color attachments each have a distinct blend state, and the location array is `{3, 0, 2, 1}`. The test confirms that remapping changes which attachment receives each shader output but leaves blend state tied to the raw attachment index, so each blended result lands in the attachment whose blend configuration produced it
  [blend attachment states](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1207-L1216),
  [location array](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1219).

### Extension interactions

- `interaction_with_graphics_pipeline_library` builds the pipeline as a fragment-shader library plus a fragment-output library and merges them, providing valid formats only in the fragment-output library. This checks that local-read remapping information flows correctly through `VK_EXT_graphics_pipeline_library` pipeline libraries
  [pipeline library construction](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1573-L1618).
- `interaction_with_color_write_enable` enables `VK_EXT_color_write_enable` and disables writes to two of four attachments via `vkCmdSetColorWriteEnableEXT`, combining that with a `{0, 3, 1, 2}` location remap
  [constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L404-L411).
- `interaction_with_extended_dynamic_state3` uses `VK_EXT_extended_dynamic_state3` to set rasterization samples by command, confirming that command-side rasterization sample state does not disturb the local-read remapping
  [constructor](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L413-L420).
- `interaction_with_shader_object` exercises the `VK_EXT_shader_object` path where remapping is set only through commands because there is no pipeline-create info to chain to.

### Single-attachment remap across pipeline forms

- `remap_single_attachment_monolithic`, `remap_single_attachment_fast_lib`, and `remap_single_attachment_shader_object` all use `MappingWithShaderObjectOrSingleAttachmentTestInstance` to remap one attachment across three draws with three different location arrays (`{2,0,1}`, `{0,1,2}`, `{1,2,0}`). The three cases differ only in pipeline construction type, confirming the remapping works for monolithic pipelines, fast-linked graphics pipeline libraries, and shader objects
  [pipeline type selection](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L137-L147),
  [pipeline build](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1866-L1888).

### Feedback loop

- `feedback_loop`, `feedback_loop_with_shader_object`, and `feedback_loop_msaa` use `FeedbackLoopTestInstance`. A single attachment is both the color output and the input attachment in the same draw, with a barrier inside the render pass instance making the write visible. The MSAA variant uses 4x sampling and a shader-based init pass; the shader object variant uses `VK_EXT_shader_object`. The shader adds or subtracts 0.2 based on the loaded value, and verification checks the delta against the input noise within a tolerance band
  [feedback shader](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3057-L3070),
  [verification](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2400-L2412).

### Null color attachment location

- `null_color_attachment_location_with_locationinfo` and `null_color_attachment_location_with_locationinfo_before_identity` provide the NULL mapping through pipeline-create info (`withLocationInfo`), with the latter first issuing an identity remap by command before the pipeline's NULL state takes effect.
- `null_color_attachment_location_with_command` and `null_color_attachment_location_with_command_after_remap` provide the NULL mapping through `vkCmdSetRenderingAttachmentLocations`, with the latter first issuing a non-identity remap. All four use `NullAttachmentLocationsTestInstance` and compare four color attachments against solid expected colors with `tcu::floatThresholdCompare`
  [iterate](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3282-L3477).

### High-location remap

- `mapping_1_attachments_to_locs_from_1`, `mapping_1_attachments_to_locs_from_2`, `mapping_1_attachments_to_locs_from_3`, and `mapping_2_attachments_to_locs_from_2` use `RemapToHighLocationTestInstance`. The shader writes to locations starting at `firstRemapLocation`, and the location info maps each attachment index to `index + firstRemapLocation`. This covers remapping to locations that are higher than the default and that may otherwise be unused
  [shader generation](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3537-L3573),
  [iterate](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3581-L3739).

## Shader Analysis

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.renderpasses.dynamic_rendering.primary_cmd_buff.local_read.mapping_2_attachments_to_locs_from_2
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `primary_cmd_buff` | Selects the primary-command-buffer registration of the exact mustpass leaf. |
| `mapping_2_attachments_to_locs_from_2` | `numAttachments` is 2 and `firstRemapLocation` is 2, so the fragment shader declares outputs at locations 2 and 3 while dynamic rendering exposes two color attachments at indices 0 and 1. |
| Attachment-location map `{2, 3}` | Both pipeline creation and command recording map attachment index 0 to location 2 and attachment index 1 to location 3. |

#### Purpose

This fragment shader verifies that outputs declared at the otherwise unused high locations 2 and 3 reach color attachment indices 0 and 1 through `VkRenderingAttachmentLocationInfo`. It writes distinct colors so the host can detect either output being dropped or routed to the wrong attachment.

#### Structural Design

| Shader output | Declared location | Mapped attachment index | Written value | Host expectation |
|---------------|-------------------|-------------------------|---------------|------------------|
| `outColor0` | 2 | 0 | opaque green | attachment 0 is entirely green |
| `outColor1` | 3 | 1 | opaque red | attachment 1 is entirely red |

#### Shader Code

```glsl
#version 450

/// The selected case creates two R8G8B8A8_UNORM color attachments. The
/// attachment-location map {2, 3} routes fragment locations 2 and 3 to
/// attachment indices 0 and 1, respectively.
layout(location=2) out vec4 outColor0;
layout(location=3) out vec4 outColor1;

void main() {
    /// Attachment 0 must receive opaque green through remapped location 2.
    outColor0 = vec4(0.0f, 1.0f, 0.0f, 1.0f);
    /// Attachment 1 must receive opaque red through remapped location 3.
    outColor1 = vec4(1.0f, 0.0f, 0.0f, 1.0f);
}
```

#### Additional Info

- `RemappingToHighLocationTestCase::initPrograms()` is the owning builder for this exact leaf. `glu::getGLSLVersionDeclaration(glu::GLSL_VERSION_450)` emits the reconstructed `#version 450`; no explicit `ShaderBuildOptions` are attached, so the CTS default target is baseline SPIR-V 1.0 [shader generation](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3537-L3573), [baseline target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052).
- Runtime creates two `VK_FORMAT_R8G8B8A8_UNORM` images, installs `{2, 3}` in both the dynamic-rendering pipeline info and `vkCmdSetRenderingAttachmentLocations`, then compares copied attachment 0 against green and attachment 1 against red with a `0.005` threshold [runtime mapping](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3581-L3693), [verification](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3716-L3737).

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| `numAttachments` | The one-attachment variants emit only `outColor0` and one green store; this two-attachment variant additionally emits `outColor1` and the red store. | [output generation loops](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3551-L3571) |
| `firstRemapLocation` | Each output declaration uses `location = attIdx + firstRemapLocation`; the one-attachment leaves therefore place their sole output at location 1, 2, or 3, while this leaf uses locations 2 and 3. | [location calculation](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3557-L3561), [registered combinations](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3801-L3817) |
| Command buffer registration | The same `RemappingToHighLocationTestCase` builder is registered from both dynamic-rendering command-buffer groups, so registration mode does not change this generated fragment source. | [case registration](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3801-L3817) |

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
               OpEntryPoint Fragment %main "main" %outColor0 %outColor1
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %outColor0 "outColor0"
               OpName %outColor1 "outColor1"
               OpDecorate %outColor0 Location 2
               OpDecorate %outColor1 Location 3
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
  %outColor0 = OpVariable %_ptr_Output_v4float Output
    %float_0 = OpConstant %float 0
    %float_1 = OpConstant %float 1
         %12 = OpConstantComposite %v4float %float_0 %float_1 %float_0 %float_1
  %outColor1 = OpVariable %_ptr_Output_v4float Output
         %14 = OpConstantComposite %v4float %float_1 %float_0 %float_0 %float_1
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpStore %outColor0 %12
               OpStore %outColor1 %14
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- Each `BasicLocalReadTestInstance` case allocates color images (`VK_FORMAT_R32_UINT`) and one depth/stencil image (`VK_FORMAT_D24_UNORM_S8_UINT` or `VK_FORMAT_D32_SFLOAT_S8_UINT`), all with `VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT`, and transitions them into `VK_IMAGE_LAYOUT_RENDERING_LOCAL_READ_KHR` before rendering begins
  [image creation](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L632-L660).
- A single dynamic render pass instance begins. The write pipeline(s) run first: before each write draw, `vkCmdSetRenderingAttachmentLocations` installs the per-draw location array, the pipeline is bound, a push constant identifies the draw, and a fullscreen quad is drawn
  [write draw recording](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L887-L898),
  [primary loop](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1028-L1042).
- A `vkCmdPipelineBarrier` with `VK_DEPENDENCY_BY_REGION_BIT` separates the write phase from the read phase, making color and depth/stencil writes visible to input attachment reads
  [mid-render barrier](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1044-L1047).
- The read pipeline(s) run next: before each read draw, `vkCmdSetRenderingInputAttachmentIndices` installs the per-draw input index array, the pipeline and its descriptor sets are bound, and a fullscreen quad draws. The read shader stores its computed sum into a host-visible storage buffer
  [read draw recording](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L900-L909),
  [read loop](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1055-L1069).
- After the render pass instance ends and commands submit, the host invalidates each output buffer and compares every element against `m_expectedValues[drawIndex]`. The expected value is computed by `CalculateExpectedValues` from the same remapping tables the shaders use, so a mismatch points directly at the remapping rather than at image content
  [verification loop](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1076-L1099).
- On failure the host copies each color attachment back to a scratch buffer and logs its first element, so the test log records what each attachment actually contained
  [failure logging](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1108-L1142).
- The blend-state, pipeline-library, shader-object, feedback-loop, null-location, and high-location cases each have their own `iterate()` but follow the same shape: set up attachments, begin one dynamic render pass instance, issue draws with the relevant remapping and extension state, copy back, and compare against known expected colors with `tcu::floatThresholdCompare` or a direct byte check.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `depth_stencil_mapping_to_no_index` and `_depth_clear` / `_stencil_clear` | NULL depth/stencil index pointer not honored, so the shader cannot reach the attachment without an `InputAttachmentIndex`. |
| `depth_stencil_mapping_to_same_index` / `_large_index` | Depth and stencil index remap applied to the wrong descriptor binding, or `maxPerStageDescriptorInputAttachments` clamp rejected a valid index. |
| `depth_mapping_stencil_not` | Stencil marked `VK_ATTACHMENT_UNUSED` but still read, or depth index remap dropped. |
| `max_input_attachments` | Default identity mapping applied incorrectly when `pColorAttachmentInputIndices` is NULL, or shader for the device-specific attachment count picked the wrong variant. |
| `max_attachments_remapped_repeatedly` | Per-draw input index remap not switched between output draws, so later reads use a stale mapping. |
| `input_attachments_without_mapping` | Default identity mapping wrong when no remap command is ever issued. |
| `unused_writen_discarded` | Writes to `VK_ATTACHMENT_UNUSED` locations not discarded, or mapped locations clobbered. |
| `mapping_not_affecting_blend_state` | Blend state applied to the remapped location instead of the raw attachment index. |
| `interaction_with_graphics_pipeline_library` | Remapping info not propagated from the fragment-output library into the merged pipeline. |
| `interaction_with_color_write_enable` | Color write enable evaluated against the wrong attachment after remap. |
| `interaction_with_extended_dynamic_state3` | Command-side rasterization sample state disturbed the remapping. |
| `interaction_with_shader_object` / `remap_single_attachment_shader_object` | Shader object path ignored command-side remap because there is no pipeline-create info to chain to. |
| `remap_single_attachment_monolithic` / `_fast_lib` | Monolithic or fast-linked library pipeline applied a stale create-time remap instead of the command state. |
| `feedback_loop` / `_with_shader_object` / `_msaa` | In-render barrier did not make the same-draw write visible to the input attachment load, or MSAA resolve path produced the wrong sample. |
| `null_color_attachment_location_*` | NULL `pColorAttachmentLocations` did not reset to identity, or the non-identity remap before the NULL was not cleared. |
| `mapping_*_attachments_to_locs_from_*` | Remap to a high (possibly unused) location did not reach the correct attachment. |

### Cause Analysis

#### Remapping state not applied or applied to the wrong resource

**Possible failure symptoms:** The output buffer (or compared color attachment) differs from the host-computed expected value. For `BasicLocalReadTestInstance` cases the failure log names the buffer index, the expected value, the received value, and the offending pixel index. For image-comparison cases the logged image shows which attachment received the wrong color
[verification](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1086-L1099),
[image logging](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3470-L3474).

**Possible implementation causes:** The extension requires the remapping to match between pipeline-create state and command-buffer state at draw time. A driver that consumes the remapping only at one of those points, or that caches it per pipeline without re-checking on later draws, will produce a consistent but wrong mapping for one or more draws. For depth/stencil NULL-index cases the driver must let the shader reach the attachment through a variable with no `InputAttachmentIndex`; a driver that requires a present pointer will fail only these cases. Source-level investigation is needed to distinguish a driver remap bug from a descriptor-binding mistake in the test itself, but the host computes expected values from the same tables the shader uses, which narrows the cause to the remapping contract.

#### Writes to unmapped or unused locations not discarded

**Possible failure symptoms:** In `unused_writen_discarded` and the `null_color_attachment_location_*` cases, an attachment that should have stayed at its clear color receives a shader-written value, or an attachment that should have received a shader write stays cleared
[expected colors](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3454-L3456).

**Possible implementation causes:** The spec says writes to a location mapped to `VK_ATTACHMENT_UNUSED` are discarded, and that a NULL `pColorAttachmentLocations` resets every location to its identity mapping. A driver that routes the shader output by raw output index instead of by remapped location will write to the wrong attachment. Source-level investigation is needed to confirm whether the driver or the test's descriptor setup is the source of the mismatch.

#### In-render visibility barrier missing or ineffective

**Possible failure symptoms:** In the feedback-loop cases the output pixels fall outside the tolerance band around the expected plus-or-minus 0.2 delta, and the failure message reports the percentage of wrong fragments
[feedback verification](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2400-L2412),
[fail message](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2421-L2424).

**Possible implementation causes:** The feedback-loop cases rely on a `VK_DEPENDENCY_BY_REGION_BIT` memory barrier inside the render pass instance to make a fragment's color write visible to a later input attachment load at the same coordinate. A driver that does not serialize framebuffer-space writes and reads across that barrier will read stale or undefined data. The MSAA variant adds resolve and sample-index paths, so a failure there could also come from sample-incorrect `subpassLoadMS`. Source-level investigation is needed to separate a barrier-propagation bug from a feedback-loop rasterization hazard.

## Case Pruning

### Requirement-based pruning

- All cases require `VK_KHR_dynamic_rendering_local_read` (core in Vulkan 1.4)
  [checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2455).
- `depth_stencil_mapping_to_large_index` requires `maxPerStageDescriptorInputAttachments >= 21`
  [limit check](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2457-L2462).
- `depth_stencil_mapping_to_no_index_depth_clear` and `_stencil_clear` require the depth-only or stencil-only format to support the needed usage
  [format check](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2463-L2475).
- `interaction_with_color_write_enable` requires `VK_EXT_color_write_enable`.
- `interaction_with_graphics_pipeline_library` and `remap_single_attachment_fast_lib` require `VK_EXT_graphics_pipeline_library`.
- `interaction_with_shader_object`, `remap_single_attachment_shader_object`, and `feedback_loop_with_shader_object` require `VK_EXT_shader_object`.
- `remap_single_attachment_monolithic` and `_fast_lib` require `VK_EXT_extended_dynamic_state`.
- `interaction_with_extended_dynamic_state3` requires `VK_EXT_extended_dynamic_state3` with the `extendedDynamicState3RasterizationSamples` feature
  [feature checks](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2476-L2492).
- On Vulkan 1.4 without the `dynamicRenderingLocalReadDepthStencilAttachments` property, depth/stencil-reading cases are reported as unsupported and the shader variant that omits depth/stencil is selected instead
  [property guard](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2494-L2504),
  [shader selection](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L427-L438).

### Design-based pruning

- The four `null_color_attachment_location_*` cases are registered only under `primary_cmd_buff` because they exercise pipeline-create info paths guarded by `!grpParams->useSecondaryCmdBuffer` and do not add coverage when recorded into secondaries
  [registration guard](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3782-L3798).
- The four `mapping_*_attachments_to_locs_from_*` cases are registered under both `primary_cmd_buff` and `partial_secondary_cmd_buff` (no secondary guard), so they account for 4 of the 25 secondary mustpass leaves
  [registration](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3801-L3818).
- The `max_input_attachments` case generates shaders for a fixed list of possible attachment counts (`inputAttachmentsPossibleValues`) rather than for every device-specific count, and asserts at runtime that the device's count is in that list
  [possible values](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L152),
  [assertion](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L275-L278).
- The high-location remap cases are limited to `firstRemapLocation <= kMaxLocation (3)` and break early when the last used location would exceed it, so only four combinations are registered
  [loop bound](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3803-L3810).

## Key Takeaways

- Every case in this family tests one specific shape of the color-location and input-attachment-index remapping contract; the write phase encodes the remapping into stored values and the read phase decodes it, so a wrong output pinpoints which side of the contract failed.
- The host computes expected values from the same remapping tables the shaders use, so validation is self-consistent and does not depend on a golden image.
- Depth and stencil can be reached through a NULL pointer (no `InputAttachmentIndex`), a shared index, a large index, or `VK_ATTACHMENT_UNUSED`, and each shape has a dedicated case; the NULL-index cases use SPIR-V assembly because glslang cannot emit the needed decoration-less variables.
- Blend state and format always track the raw attachment index regardless of location remapping, which is why `mapping_not_affecting_blend_state` exists as a dedicated case.
- Remapping state must match between pipeline creation and command recording; several cases exist specifically to catch drivers that consume the state at only one of those points.
- See `## Failure Meaning` for the failure interpretation: a failing case means the implementation did not honor the remapping contract for that case's specific shape.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [createDynamicRenderingLocalReadTests](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3744-L3821) | Registers all cases under `local_read`, including the TestType-driven set and the null-location and high-location sets. |
| TestType enum | [vktDynamicRenderingLocalReadTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L59-L123) | Defines the 21 behavioral cases and their shader-resource needs. |
| BasicLocalReadTestInstance constructor | [vktDynamicRenderingLocalReadTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L224-L441) | Switches on TestType to set attachment counts, remapping tables, and depth/stencil indices. |
| Expected value computation | [CalculateExpectedValues](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L480-L556) | Mirrors shader arithmetic so validation is table-driven. |
| Basic iterate | [vktDynamicRenderingLocalReadTests.cpp](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L563-L1145) | Write-then-read render pass instance, mid-render barrier, and output verification. |
| Blend-state instance | [MappingWithBlendStateTestInstance](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1147-L1441) | Isolates remapping from blend-state application. |
| Pipeline-library instance | [MappingWithGraphicsPipelineLibraryTestInstance](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1443-L1762) | Tests remapping through merged graphics pipeline libraries. |
| Shader-object and single-attachment instance | [MappingWithShaderObjectOrSingleAttachmentTestInstance](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L1764-L2069) | Tests remapping across monolithic, fast-linked, and shader-object pipeline forms. |
| Feedback-loop instance | [FeedbackLoopTestInstance](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2071-L2425) | Tests same-draw feedback through an in-render barrier, with MSAA variant. |
| Null-location instance | [NullAttachmentLocationsTestInstance](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3130-L3478) | Tests NULL `pColorAttachmentLocations` through command and pipeline-create paths. |
| High-location instance | [RemapToHighLocationTestInstance](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L3480-L3740) | Tests remapping to locations above the default indices. |
| Shader generation | [initPrograms](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2507-L3112) | Generates write and read fragment shaders, including SPIR-V assembly for NULL-index cases. |
| Feature and limit checks | [checkSupport](../../../modules/vulkan/renderpass/vktDynamicRenderingLocalReadTests.cpp#L2450-L2505) | Guards extension, feature, format, and limit requirements per case. |
| Registration in render pass tests | [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8535) | Attaches the family under `primary_cmd_buff`. |
| Registration in render pass tests (secondaries) | [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8544) | Attaches the family under `partial_secondary_cmd_buff`. |
| Mustpass (primary) | [renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt#L19646-L19674) | Lists the 29 `primary_cmd_buff.local_read` cases. |
| Mustpass (secondary) | [renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt#L11802-L11826) | Lists the 25 `partial_secondary_cmd_buff.local_read` cases. |
| Extension proposal | [VK_KHR_dynamic_rendering_local_read.adoc](../../../../vulkan-docs/src/proposals/VK_KHR_dynamic_rendering_local_read.adoc) | Authoritative description of the remapping structures and their defaults. |
