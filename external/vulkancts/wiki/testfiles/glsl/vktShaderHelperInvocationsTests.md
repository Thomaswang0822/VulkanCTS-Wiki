# vktShaderHelperInvocationsTests.cpp

## Overview

[`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L1) documents the GLSL `helper_invocations` group registered under the `glsl` package. The file comment identifies it as helper-invocation tests, and the GLSL root adds the group through [`createShaderHelperInvocationsTests()`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1279). The implementation focuses on fragment-shader helper invocations by rendering a generated triangle, feeding the first result back into a second fragment shader through one selected input mechanism, and checking that derivative reads and output writes have the expected visible behavior.

## Role

Combined registration and implementation file. It defines the `helper_invocations` test group, registers six leaf cases, creates per-case shaders, builds graphics pipelines and render passes, and performs host-side readback validation in one source file.

## Source Code

- Primary source: [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L1)
- Header declaration: [`vktShaderHelperInvocationsTests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.hpp#L29-L33)
- GLSL root registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1279)
- Test type enum and parameters: [`TestType`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L55-L68)
- Test instance configuration and execution: [`HelperInvocationsTestInstance`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L70-L448)
- Test case support, shader generation, and instance creation: [`HelperInvocationsTestCase`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L507-L613)
- Group population and factory: [`addShaderHelperInvocationsTests()`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L615-L630) and [`createShaderHelperInvocationsTests()`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L634-L637)

## Registration Hierarchy

```text
glsl.helper_invocations
├── load_from_ssbo
├── load_from_address
├── load_from_ubo
├── load_from_image
├── load_from_texture
└── output_variables
```

## Test Families

### load_from_ssbo — Storage-buffer input to derivative read

The default instance configuration corresponds to `LOAD_SSBO`: it uses a buffer, a descriptor set, `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT`, `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`, and expected derivative color `63` at [`HelperInvocationsTestInstance::HelperInvocationsTestInstance()`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L95-L110). The read fragment shader declares a `std430` storage buffer, indexes it with `uint(gl_FragCoord.y)*32+uint(gl_FragCoord.x)`, and writes `uint(fwidth(v[i]))` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L551-L559).

### load_from_address — Buffer-device-address input to derivative read

`load_from_address` sets `m_usingDescriptorSet = false`, enables `m_usingDeviceAddress`, and adds `VK_BUFFER_USAGE_SHADER_DEVICE_ADDRESS_BIT` to the tested buffer usage at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L112-L117). During execution, the code obtains the buffer device address and passes it as a fragment-stage push constant before the second draw at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L210-L213) and [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L345-L349). The generated shader requires `GL_EXT_buffer_reference`, reads through a buffer-reference `Data` object, and writes `uint(fwidth(data.v[i]))` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L560-L570).

### load_from_ubo — Uniform-buffer input to derivative read

`load_from_ubo` switches the buffer usage to `VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT` and the descriptor type to `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L118-L122). Its shader declares `layout(binding=0) uniform Input { uvec4 v[32*8]; }`, maps the 32x32 render area into 256 four-component elements, and applies `fwidth()` to the selected component at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L571-L579).

### load_from_image — Storage-image input to derivative read

`load_from_image` disables buffer use, configures the first rendered image with `VK_IMAGE_USAGE_STORAGE_BIT`, and uses `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L123-L128). The descriptor update path binds the input image view in `VK_IMAGE_LAYOUT_GENERAL` when the case is image-backed rather than buffer-backed at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L241-L247). The read shader declares a readonly `r32ui` `uimage2D`, performs `imageLoad()`, and writes `uint(fwidth(c))` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L580-L587).

### load_from_texture — Sampled-texture input to derivative read

`load_from_texture` enables sampler use, disables buffer use, selects `VK_IMAGE_USAGE_SAMPLED_BIT`, and binds the input as `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L129-L135). Execution creates a sampler only for sampler-backed cases at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L214-L216). The shader samples a `usampler2D` using normalized coordinates derived from `gl_FragCoord.xy / 32` and writes `uint(fwidth(c))` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L588-L596).

### output_variables — Input-attachment path for output-variable behavior

`output_variables` differs from the `LOAD_*` cases: it disables buffer use, enables a second subpass, uses `VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT`, and binds `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L136-L142). The write fragment shader changes from the default constant output `84` to a per-fragment value `uint(gl_FragCoord.y)*32+uint(gl_FragCoord.x)` for this case at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L541-L549). The read shader loads a `usubpassInput` value and writes `c + uint(gl_FragCoord.y) * uint(gl_FragCoord.x)` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L597-L604).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Registered leaf cases | `load_from_ssbo`, `load_from_address`, `load_from_ubo`, `load_from_image`, `load_from_texture`, and `output_variables` are generated from the `testCases` vector at [`addShaderHelperInvocationsTests()`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L619-L629). |
| Internal test type enum | `LOAD_SSBO`, `LOAD_ADDRESS`, `LOAD_UBO`, `LOAD_IMAGE`, `LOAD_TEXTURE`, and `OUTPUT_VARIABLES` are the six `TestType` values at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L55-L63). |
| Render target | All cases use a 32x32 `VK_FORMAT_R32_UINT` image with one sample at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L162-L183). |
| Clear and expected values | `inputClearColor = 21`, `finalClearColor = 30`, and default `m_expectedColor = 63` are set at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L168-L170) and [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L101-L110). |
| Resource binding mode | Cases select storage buffer, device address push constant, uniform buffer, storage image, combined image sampler, or input attachment through constructor flags and descriptor types at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L101-L142). |
| Render-pass mode | `LOAD_*` cases use separate write and read render passes; `output_variables` uses two subpasses in one render pass, controlled by `m_usingSecondSubpass` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L284-L353). |

## Support / Feature Requirements

| Requirement | Evidence |
|---|---|
| Buffer device address for `load_from_address` | `HelperInvocationsTestCase::checkSupport()` calls `context.requireDeviceFunctionality("VK_KHR_buffer_device_address")` only when the selected type is `LOAD_ADDRESS` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L525-L529). |
| Device-address memory requirement | The input buffer allocation requests `MemoryRequirement::DeviceAddress` only when `m_usingDeviceAddress` is true at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L201-L204). |
| No other explicit per-case feature gate in this file | The inspected `checkSupport()` method contains no additional feature checks beyond `LOAD_ADDRESS`; the remaining cases rely on the resources, descriptors, shaders, and render-pass operations created in `iterate()` at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L145-L448). |

## Verification Methods

- For `LOAD_*` cases, the test first draws a triangle to identify covered fragments, then uses the first rendering result as the second fragment shader's input by buffer copy, image descriptor, sampled image, or device address. The implementation comment describes the expected four output classes: final clear color outside relevant quads, zero inside fully covered quads, and one of two edge values derived from the first draw at [`HelperInvocationsTestInstance::iterate()`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L145-L155).
- The command buffer records either two render passes for `LOAD_*` cases or a two-subpass render pass for `output_variables`, then copies the final `VK_FORMAT_R32_UINT` image to a host-visible buffer for validation at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L282-L368).
- `LOAD_*` validation counts fragments equal to zero, final clear color, `m_expectedColor`, and `2 * m_expectedColor`; it passes only when every fragment belongs to those four classes, minimum counts for zero and edge values are met, and fragments that were clear in the input image did not receive a non-clear final color at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L407-L439).
- `output_variables` validation recomputes each pixel's expected value on the host. Pixels still equal to the final clear color remain clear; other pixels must equal `x + y * 32 + x * y`, matching the write shader plus read shader expressions at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L384-L406) and [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L541-L604).
- On failure, the test logs the input and final images before returning fail, which provides diagnostic evidence rather than a separate acceptance path at [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L442-L447).

## Test Principles

- The registered matrix isolates one resource access path per leaf case, while sharing the same triangle geometry, render size, integer color format, and host readback pattern across the six cases.
- The `LOAD_*` cases deliberately apply `fwidth()` to values read through the selected storage, address, uniform, image, or sampler mechanism so helper-invocation reads affect the visible derivative result.
- The validation distinguishes helper-invocation reads from helper-invocation writes: edge derivative values are required for `LOAD_*` cases, but the `helperWroteColor` check rejects writes to fragments that were clear in the input image.
- The `output_variables` case uses an input attachment and two subpasses to check output-variable behavior through a per-fragment arithmetic invariant rather than through the four-class derivative histogram used by the `LOAD_*` cases.

## Notes / Uncertainties

- The inspected source file registers only leaf cases directly under `glsl.helper_invocations`; no deeper subgroups are generated by this file.
- No historical Vulkan API test-plan citation is used here because the inspected helper-invocation behavior is a narrow GLSL shader-execution test and the current behavior is fully derived from source code.
