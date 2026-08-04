# Understanding Brief: pipeline color write enable

## One-sentence test purpose

This implementation checks whether Vulkan applies static and dynamic per-attachment color write enables, component masks, and ordering rules before a draw stores color output.

## Background knowledge

### Two layers of write control

`colorWriteMask` in `VkPipelineColorBlendAttachmentState` selects the R, G, B, and A components that can be written. `VkPipelineColorWriteCreateInfoEXT` adds one boolean per color attachment. When that boolean is `VK_FALSE`, Vulkan ignores the component mask and disables writes to every component of that attachment. When it is `VK_TRUE`, the component mask determines the writable components.

Why it matters here:

- `color_write_enable` varies both the per-attachment enable array and one of six component masks.
- `color_write_enable_maxa` gives each attachment a different omitted component, so a readback exposes confusion between whole-attachment enable and component masking.

### Static and dynamic state

A pipeline can provide color write enables through `VkPipelineColorWriteCreateInfoEXT`. If it declares `VK_DYNAMIC_STATE_COLOR_WRITE_ENABLE_EXT`, that static array is ignored and `vkCmdSetColorWriteEnableEXT` must set the state before a draw. The command supplies an ordered boolean array, one value per attachment.

Why it matters here:

- The ordinary family records the command at several positions around pipeline binds and draws.
- The max-attachment family records it before or after the pipeline bind and tests arrays that extend beyond the attachments used by the current draw.

## One concrete example

Consider `dEQP-VK.pipeline.monolithic.color_write_enable.red_channel.before_draw.enable_first`. The CTS creates three `VK_FORMAT_R8G8B8A8_UNORM` color attachments and a depth/stencil attachment. Its fragment shader writes the configured triangle color, then half and quarter of that color, to locations 0, 1, and 2. For this dynamic leaf, the source configures clear color `(0.25, 0.5, 0.75, 0.5)`, triangle color `(1.0, 0.75, 0.5, 0.25)`, and a static all-disabled array. Immediately before the draw, `vkCmdSetColorWriteEnableEXT` enables only the first attachment. The host expects attachment 0 to retain only the source red component and the clear values for GBA, while the other attachments retain their clear color. It also expects depth to be written.

## End-to-end test flow

```text
[host] select a construction type, channel mask, write-enable pattern, and command ordering
[host] require VK_EXT_color_write_enable and supported attachment/readback formats
[host] create color and depth/stencil images, views, render passes, pipelines, and a vertex buffer
[device] record static state and, where selected, vkCmdSetColorWriteEnableEXT around pipeline binds
[device] draw a full-screen triangle fan and write depth plus eligible color components
[host] submit and wait, copy/read each attachment, and compare color and depth with expected values
```

## Generated test artifacts and bound resources

| Resource or artifact | Created/configured by host? | Used by device? | Read by host? | Why it matters |
|---|---:|---:|---:|---|
| Three color attachments in the ordinary family | yes | color output writes them | yes | Exposes attachment-specific enable state and channel masking. |
| Depth/stencil attachment | yes | depth testing and writes use it | yes | Confirms color-write control does not suppress depth writes. |
| `VkPipelineColorWriteCreateInfoEXT` or `vkCmdSetColorWriteEnableEXT` | yes | graphics pipeline or command execution consumes it | no | Supplies static or dynamic per-attachment enables. |
| Push constants | yes | vertex and fragment shaders read them | no | Provide triangle color, depth, and geometry placement. |
| Max-attachment framebuffer set | yes | each draw uses a prefix of the attachment array | yes | Tests dynamic-state array length and `maxColorAttachments` boundaries. |

## What is checked

- The ordinary family compares all pixels of each final color attachment with a threshold of `0.005f`; it logs a result and error-mask image on a mismatch.
- It reads depth with a `1.0e-07f` interval around the expected depth, even when color writes are disabled.
- The max-attachment family clears each attachment to `(0.75, 0.75, 0.75, 0.75)`, renders a known attenuated source color, and checks every pixel. Disabled attachments must remain clear; enabled attachments retain the source except for the component omitted by their `colorWriteMask`.

## Behavior parameter identification

> **Behavior parameter:** test family and its direct intermediate node
>
> **Candidate values:** `color_write_enable` with `all_channels`, `red_channel`, `green_channel`, `blue_channel`, `alpha_channel`, or `no_channels`; and `color_write_enable_maxa` with `cwe_before_bind` or `cwe_after_bind`.

## What failure means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `all_channels`, `red_channel`, `green_channel`, `blue_channel`, `alpha_channel`, or `no_channels` | Incorrect interaction between per-attachment color write enable and `colorWriteMask`, stale or incorrectly ordered dynamic state, incorrect static-state fallback, or an unrelated color/depth readback path. |
| `cwe_before_bind` | The implementation may lose dynamic color-write-enable state when a graphics pipeline is subsequently bound, apply an enable to the wrong attachment, or mishandle the supplied array length. |
| `cwe_after_bind` | The implementation may fail to apply dynamic state recorded after the pipeline bind before the draw, apply it to the wrong attachment, or mishandle the supplied array length. |

## Important variations and special cases

- The ordinary family uses three color attachments and six component masks. It creates seven dynamic ordering nodes plus a `static` node, each with six attachment-enable patterns and their inverse disable patterns.
- `between_pipelines` and `after_pipelines` are omitted for shader-object construction types because those orderings require multiple pipeline binds.
- The max-attachment family registers attachment counts `3`, `4`, and `5`, each with `more` values `0` through `3`. It skips a leaf when `attachmentCount + attachmentMore` exceeds `maxColorAttachments`.
- The complete inspected mustpass scope contains 3,624 matching leaves: 600 each under `monolithic`, `pipeline_library`, and `fast_linked_library`, and 456 each under four shader-object roots.

## Source mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Ordinary-family programs, support, and runtime | [ColorWriteEnableTest and ColorWriteEnableInstance](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L277-L987) | Requires the extension, emits shaders, records state, and compares color and depth. |
| Max-attachment support and execution | [ColorWriteEnable2Test and ColorWriteEnable2Instance](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1101-L1655) | Checks limits, builds static/dynamic pipelines, records commands, and validates each attachment. |
| Registration | [createColorWriteEnableTests() and createColorWriteEnable2Tests()](../../../modules/vulkan/pipeline/vktPipelineColorWriteEnableTests.cpp#L1660-L1860) | Defines the tree and parameter loops. |
| Vulkan color-write-enable contract | [Color Write Enable](../../../../vulkan-docs/src/chapters/framebuffer.adoc#L1886-L1974) | Defines the static structure, mask interaction, and dynamic command. |
| Dynamic-state requirement | [graphics pipeline dynamic state](../../../../vulkan-docs/src/chapters/pipelines.adoc#L6197-L6202) | Requires the command before any draw when this state is dynamic. |

## Conversion notes for final wiki rewrite

- Keep the Failure Cause Mapping table unchanged in the final page.
- Treat the shaders as output suppliers. The behavior under test is fixed-function attachment write control.
- Use the ordinary red-channel dynamic case as the walkthrough and keep max-attachment behavior separate because it tests array length and bind timing.
