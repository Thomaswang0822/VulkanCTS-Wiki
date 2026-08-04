## Overview

**Core question:** Does the implementation apply static and dynamic per-attachment color write enables, component masks, and command ordering before a draw stores color output?

- This implementation supplies the `color_write_enable` and `color_write_enable_maxa` test families under each pipeline construction root that registers them.
- `color_write_enable` combines three color attachments, a depth/stencil attachment, six component masks, static and dynamic write-enable arrays, and several command orderings.
- `color_write_enable_maxa` changes the point at which dynamic state is recorded and varies the number of used and extra enable-array entries near `maxColorAttachments`.
- Both paths render, wait for completion, read attachments on the host, and compare every relevant pixel against an expected value.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

`VkPipelineColorBlendAttachmentState::colorWriteMask` selects the R, G, B, and A components that may be written. `VkPipelineColorWriteCreateInfoEXT` adds one boolean per color attachment. Vulkan states that `VK_FALSE` ignores the component mask and disables writes to every component of that attachment, whereas `VK_TRUE` leaves the component mask in control ([Color Write Enable](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L1905-L1925)).

A pipeline can set this state statically with `VkPipelineColorWriteCreateInfoEXT`. A pipeline that declares `VK_DYNAMIC_STATE_COLOR_WRITE_ENABLE_EXT` ignores the static array; `vkCmdSetColorWriteEnableEXT` must set the per-attachment values before a draw ([dynamic state contract](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6197-L6202)). The command sets state for subsequent draws and receives an ordered boolean array ([command definition](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L1952-L1974)).

## Registration Hierarchy

```text
pipeline.monolithic.color_write_enable
├── all_channels
├── red_channel
├── green_channel
├── blue_channel
├── alpha_channel
└── no_channels

pipeline.monolithic.color_write_enable_maxa
├── cwe_before_bind
└── cwe_after_bind
```

`createColorWriteEnableTests()` adds the six direct intermediate nodes for component-mask coverage. Each component-mask node contains the `static` node and seven dynamic-ordering nodes for construction types that support all orderings; shader-object construction types omit `between_pipelines` and `after_pipelines`. Every ordering node contains six enable and six inverse-disable leaves. `createColorWriteEnable2Tests()` adds the two bind-timing intermediate nodes, then registers `attachments{3|4|5}_more{0|1|2|3}` leaves. The dispatcher calls both factories for each applicable construction root ([registration calls](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L179-L188), [factory loops](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1660-L1860)).

## Parameter Dimensions and Observed Values

| Dimension | Registered or source values | What it changes | Evidence |
|-----------|-----------------------------|-----------------|----------|
| Test family | `color_write_enable`, `color_write_enable_maxa` | Selects the ordinary multi-ordering matrix or the attachment-count/bind-timing matrix. | [factories](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1660-L1860) |
| Component-mask intermediate node | `all_channels`, `red_channel`, `green_channel`, `blue_channel`, `alpha_channel`, `no_channels` | Selects `tcu::BVec4` values for all, one, or no RGBA components. | [channel cases](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1678-L1691) |
| Ordinary ordering | `cmd_buffer_start`, `before_draw`, `between_pipelines`, `after_pipelines`, `before_good_static`, `two_draws_dynamic`, `two_draws_static`, `static` | Changes where the dynamic command and static or dynamic pipeline binds occur. | [ordering cases](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1693-L1817) |
| Write-enable pattern | all, first, second, last, first-and-second, second-and-last, each enabled and inversely disabled | Selects which of the three ordinary color attachments can receive writes. | [leaf creation](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1666-L1768) |
| Max-attachment bind timing | `cwe_before_bind`, `cwe_after_bind` | Records `vkCmdSetColorWriteEnableEXT` before or after a dynamic pipeline bind. | [command sequence](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1618-L1637) |
| Max-attachment counts | used attachments `3`, `4`, `5`; extra array entries `0`, `1`, `2`, `3` | Changes draw attachments and the `pColorWriteEnables` array length. | [maxa registration](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1825-L1859) |
| Construction type | dispatcher parameter `pct` | Selects the pipeline-construction implementation; shader objects omit two ordering nodes. | [shader-object pruning](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1725-L1728) |

The inspected mustpass files contain 3,624 matching leaves. `monolithic`, `pipeline_library`, and `fast_linked_library` each contain 600; `shader_object_linked_binary`, `shader_object_linked_spirv`, `shader_object_unlinked_binary`, and `shader_object_unlinked_spirv` each contain 456. The smaller shader-object inventories follow the source pruning of `between_pipelines` and `after_pipelines`.

## Behavior Parameters

The primary behavioral axis is the **test family and its direct intermediate node**. `color_write_enable` uses component-mask nodes to test static and dynamic state across command orderings. `color_write_enable_maxa` uses bind-timing nodes to test dynamic state with larger arrays.

### `color_write_enable`: component masks and ordinary command ordering

The test creates three `VK_FORMAT_R8G8B8A8_UNORM` color attachments and selects a `tcu::BVec4` mask for all components, one component, or none. Each ordering runs one of six write-enable patterns or its inverse. The test can bind a deliberately wrong static pipeline and a dynamic pipeline with the expected values, or reverse them when the static pipeline must be correct for the final draw.

### `color_write_enable_maxa`: dynamic-state timing and array size

The test creates framebuffers with increasing attachment counts up to the selected leaf's `attachmentCount`. It alternates static and dynamic color-write-enable pipelines, uses a full enable array with `attachmentCount + attachmentMore` entries, and makes even attachment indices disabled. Each attachment has one different component removed from its `colorWriteMask`. The two intermediate nodes place the dynamic command before or after a pipeline bind.

## Shader Analysis

The shaders provide output colors and depth; they do not implement the attachment-write control under test. The ordinary family emits a vertex shader that positions a triangle fan from push constants and a fragment shader that writes one attenuated color to each of three output locations. Fixed-function color-write-enable state decides which attachment components are stored.

### Representative Shader Walkthrough

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.color_write_enable.red_channel.before_draw.enable_first
```

| Parameter choice | Meaning |
|------------------|---------|
| `red_channel` | The static component mask leaves only R writable. |
| `before_draw` | The test records `vkCmdSetColorWriteEnableEXT` immediately before drawing. |
| `enable_first` | The dynamic array enables attachment 0 and disables attachments 1 and 2. |
| Three attachments | The fragment stage writes locations 0, 1, and 2; each receives a separately attenuated source color. |

#### Purpose

The fragment stage makes attachment output observable. The write-enable array and component masks, not fragment arithmetic, determine the expected stored values.

#### Structural Design

```mermaid
flowchart LR
    A[Push constants] --> B[Vertex shader]
    B --> C[Triangle fan]
    C --> D[Fragment shader]
    D --> E[Locations 0, 1, 2]
    E --> F[Color-write-enable and component-mask state]
    F --> G[Color attachments]
```

#### Shader Code

```glsl
#version 450
layout(push_constant, std430) uniform PushConstantsBlock {
    vec4 triangleColor;
    float depthValue;
    float scaleX;
    float scaleY;
    float offsetX;
    float offsetY;
} pushConstants;
layout(location=0) out vec4 color0;
layout(location=1) out vec4 color1;
layout(location=2) out vec4 color2;
void main() {
    color0 = pushConstants.triangleColor * 1.0;
    color1 = pushConstants.triangleColor * 0.5;
    color2 = pushConstants.triangleColor * 0.25;
}
```

The snippet is the exact fragment source emitted by `ColorWriteEnableTest::initPrograms()` for `kNumColorAttachments == 3` ([source](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L310-L351)). The representative dynamic leaf configures triangle color `(1.0, 0.75, 0.5, 0.25)`, clear color `(0.25, 0.5, 0.75, 0.5)`, and an all-disabled static array before enabling only attachment 0 dynamically. With `red_channel`, attachment 0 should retain source red and clear GBA; attachments 1 and 2 should retain their clear colors. Depth is checked independently.

#### Parameter Variation Summary

| Variation | Shader effect | Fixed-function effect |
|-----------|---------------|-----------------------|
| Component mask | None | Selects writable R, G, B, A, all, or no components. |
| Enable pattern | None | Enables or disables complete attachments. |
| Ordinary ordering | None | Changes when the dynamic array takes effect relative to binds and draws. |
| Max-attachment count | The second family emits the required number of output declarations. | Changes attachment count and dynamic-state array length. |

#### SPIR-V

- Status: compiled with `glslangValidator -V --target-env spirv1.0`, then validated with `spirv-val --target-env spv1.0`.
- Source: the reconstructed representative GLSL above.
- Stage: `frag`; target: `spirv1.0`.

<details>
<summary>Click to expand SPIR-V assembly</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 30
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %color0 %color1 %color2
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %color0 "color0"
               OpName %PushConstantsBlock "PushConstantsBlock"
               OpMemberName %PushConstantsBlock 0 "triangleColor"
               OpMemberName %PushConstantsBlock 1 "depthValue"
               OpMemberName %PushConstantsBlock 2 "scaleX"
               OpMemberName %PushConstantsBlock 3 "scaleY"
               OpMemberName %PushConstantsBlock 4 "offsetX"
               OpMemberName %PushConstantsBlock 5 "offsetY"
               OpName %pushConstants "pushConstants"
               OpName %color1 "color1"
               OpName %color2 "color2"
               OpDecorate %color0 Location 0
               OpDecorate %PushConstantsBlock Block
               OpMemberDecorate %PushConstantsBlock 0 Offset 0
               OpMemberDecorate %PushConstantsBlock 1 Offset 16
               OpMemberDecorate %PushConstantsBlock 2 Offset 20
               OpMemberDecorate %PushConstantsBlock 3 Offset 24
               OpMemberDecorate %PushConstantsBlock 4 Offset 28
               OpMemberDecorate %PushConstantsBlock 5 Offset 32
               OpDecorate %color1 Location 1
               OpDecorate %color2 Location 2
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
     %color0 = OpVariable %_ptr_Output_v4float Output
%PushConstantsBlock = OpTypeStruct %v4float %float %float %float %float %float
%_ptr_PushConstant_PushConstantsBlock = OpTypePointer PushConstant %PushConstantsBlock
%pushConstants = OpVariable %_ptr_PushConstant_PushConstantsBlock PushConstant
        %int = OpTypeInt 32 1
      %int_0 = OpConstant %int 0
%_ptr_PushConstant_v4float = OpTypePointer PushConstant %v4float
    %float_1 = OpConstant %float 1
     %color1 = OpVariable %_ptr_Output_v4float Output
  %float_0_5 = OpConstant %float 0.5
     %color2 = OpVariable %_ptr_Output_v4float Output
 %float_0_25 = OpConstant %float 0.25
       %main = OpFunction %void None %3
          %5 = OpLabel
         %16 = OpAccessChain %_ptr_PushConstant_v4float %pushConstants %int_0
         %17 = OpLoad %v4float %16
         %19 = OpVectorTimesScalar %v4float %17 %float_1
               OpStore %color0 %19
         %21 = OpAccessChain %_ptr_PushConstant_v4float %pushConstants %int_0
         %22 = OpLoad %v4float %21
         %24 = OpVectorTimesScalar %v4float %22 %float_0_5
               OpStore %color1 %24
         %26 = OpAccessChain %_ptr_PushConstant_v4float %pushConstants %int_0
         %27 = OpLoad %v4float %26
         %29 = OpVectorTimesScalar %v4float %27 %float_0_25
               OpStore %color2 %29
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

### Ordinary family

`ColorWriteEnableInstance::iterate()` requires `VK_EXT_color_write_enable`, color-attachment plus transfer-source support for `VK_FORMAT_R8G8B8A8_UNORM`, a supported depth/stencil attachment format, and the selected construction requirements. It creates one 64 by 64 color image per attachment per draw iteration and one depth/stencil image per iteration. It builds a static and a dynamic pipeline, with static and dynamic arrays intentionally exchanged for ordering cases that bind the correct static pipeline last.

The command buffer starts render passes, binds the selected pipeline, records dynamic state at the selected point, pushes triangle color and depth, binds a six-vertex triangle fan, and draws. After submission and wait, the host reads each final color attachment and compares every pixel to the configured expected color with `kColorThreshold(0.005f)`. It reads the depth attachment and accepts values only in `expectedDepth ± 1.0e-07f`. Color or depth mismatches produce error-mask images ([recording and comparison](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L383-L986)).

### Max-attachment family

`ColorWriteEnable2Instance::iterate()` chooses an RGBA or sRGBA blendable format that supports color attachment, blending, and transfer-source usage. It rejects leaves whose used plus extra dynamic-state entries exceed `maxColorAttachments`. It creates 32 by 32 framebuffers containing prefixes from one through `attachmentCount`, then alternates static and dynamic pipelines. Even attachment indices receive `VK_FALSE` in the enable array; the array has `attachmentCount + attachmentMore` entries.

For each draw, the test binds its vertex buffer, optionally calls `vkCmdSetColorWriteEnableEXT` before binding a dynamic pipeline, or binds first and calls it after. It clears the attachments to `0.75`, submits, waits, reads every attachment, and checks each pixel. An enabled attachment expects an attenuated source color with its one masked component retained from the clear color. A disabled attachment expects the full clear color ([execution](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1580-L1655), [oracle](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1547-L1577)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `all_channels`, `red_channel`, `green_channel`, `blue_channel`, `alpha_channel`, or `no_channels` | Incorrect interaction between per-attachment color write enable and `colorWriteMask`, stale or incorrectly ordered dynamic state, incorrect static-state fallback, or an unrelated color/depth readback path. |
| `cwe_before_bind` | The implementation may lose dynamic color-write-enable state when a graphics pipeline is subsequently bound, apply an enable to the wrong attachment, or mishandle the supplied array length. |
| `cwe_after_bind` | The implementation may fail to apply dynamic state recorded after the pipeline bind before the draw, apply it to the wrong attachment, or mishandle the supplied array length. |

### Cause Analysis

#### Component-mask or attachment-enable errors

**Possible failure symptoms:** An ordinary component-mask intermediate node fails across one or more enable leaves. A disabled attachment changes, an enabled attachment fails to change in a writable component, or a component outside `colorWriteMask` changes. The depth result can still pass.

**Possible implementation causes:** The implementation may conflate `colorWriteEnable` with `colorWriteMask`, apply the boolean array to a wrong attachment index, or fail to suppress every component when the boolean is `VK_FALSE`. The final image combines enable state, mask state, draw ordering, and readback, so the source does not isolate one pipeline stage without investigating the implementation path.

#### Dynamic-state ordering or stale-state errors

**Possible failure symptoms:** A case fails only for `cmd_buffer_start`, `before_draw`, `between_pipelines`, `after_pipelines`, `before_good_static`, `two_draws_dynamic`, or `two_draws_static`. A static case passes while the dynamic counterpart fails, or the second draw has the first draw's result.

**Possible implementation causes:** The implementation may not retain `vkCmdSetColorWriteEnableEXT` state across a pipeline bind that permits it, may use static state when dynamic state was declared, or may apply the command too late. These leaves deliberately exchange good and bad static and dynamic arrays, so a mismatch can also identify incorrect pipeline-state precedence.

#### Bind-timing or dynamic-array-length errors

**Possible failure symptoms:** `cwe_before_bind` or `cwe_after_bind` fails for one attachment-count or `more` value. The mismatch can appear only on later attachments or only when an array contains entries beyond the framebuffer's used attachments.

**Possible implementation causes:** The implementation may clear dynamic state at bind time, require the command after a bind when Vulkan permits the recorded sequence, index the supplied array incorrectly, or mishandle entries near `maxColorAttachments`. The readback also includes image copies and host access; source-level investigation is required if the stored values do not distinguish a rendering-state defect from that path.

#### Depth or transfer-readback errors

**Possible failure symptoms:** Color comparison passes but depth comparison fails in the ordinary family, or expected colors do not reach host comparison despite correct rendering state.

**Possible implementation causes:** The implementation may incorrectly couple depth writes to color-write control, mishandle the selected depth/stencil format, or fail in a transfer/readback operation. The ordinary path checks depth independently, while the max-attachment path validates its copies through `readColorAttachment`.

## Case Pruning

### Requirement-based pruning

- Both families require `VK_EXT_color_write_enable` when they use color-write enables.
- The ordinary family requires `VK_FORMAT_R8G8B8A8_UNORM` with color-attachment and transfer-source support plus at least one depth/stencil format with depth/stencil-attachment and transfer-source support.
- The max-attachment family selects a format with color-attachment, blend, and transfer-source support, and skips any leaf where `attachmentCount + attachmentMore` exceeds `maxColorAttachments`.
- Both paths call `checkPipelineConstructionRequirements()` for the selected construction type.

### Design-based pruning

- Shader-object construction types omit `between_pipelines` and `after_pipelines` because the source identifies them as multi-pipeline ordering cases.
- The ordinary family has a `static` node to cover no dynamic state, while the other nodes test dynamic-state placement.
- The max-attachment matrix uses counts `3`, `4`, and `5`, and `more` values `0` through `3`, rather than generating every possible device limit. It still tests arrays at and below the declared limit.

## Key Takeaways

- `colorWriteEnable` acts at attachment granularity. `colorWriteMask` acts at component granularity when the attachment is enabled.
- The ordinary family changes masks, enable arrays, and command placement while independently checking color and depth.
- The max-attachment family tests dynamic command timing and array length with framebuffer prefixes and per-attachment component masks.
- The shaders only emit known output values. Fixed-function pipeline state controls whether those values reach attachment memory.
- A failed final image can expose a write-state defect, but its readback path means that source-level investigation may be needed to localize a failure.

## Source Reference Appendix

| Entry point or contract | Link | Why it matters |
|-------------------------|------|----------------|
| Ordinary support and program generation | [`ColorWriteEnableTest::checkSupport()` and `initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L277-L351) | Requires the extension and emits the representative shaders. |
| Ordinary command-state helper | [`setDynamicStates()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L372-L381) | Calls `cmdSetColorWriteEnableEXT` when dynamic values exist. |
| Ordinary execution and checks | [`ColorWriteEnableInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L383-L986) | Creates resources, records orderings, submits, and validates color and depth. |
| Max-attachment support | [`ColorWriteEnable2Test::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1231-L1263) | Enforces feature, limit, format, and construction requirements. |
| Max-attachment pipeline setup | [`setupAndBuildPipeline()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1437-L1545) | Builds static or dynamic color-write-enable state and component masks. |
| Max-attachment oracle and runtime | [`verifyAttachment()` and `iterate()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1547-L1655) | Defines expected values and command ordering. |
| Registration factories | [`createColorWriteEnableTests()` and `createColorWriteEnable2Tests()`](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1660-L1860) | Defines registered intermediate nodes and leaves. |
| Static and dynamic color-write-enable contract | [`Color Write Enable`](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L1886-L1974) | Defines structure fields, mask interaction, and command state. |
| Dynamic-state requirement | [`VK_DYNAMIC_STATE_COLOR_WRITE_ENABLE_EXT`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6197-L6202) | Requires dynamic state before any draw. |
