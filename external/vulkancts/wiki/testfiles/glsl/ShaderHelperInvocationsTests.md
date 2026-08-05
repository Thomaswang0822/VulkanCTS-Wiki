## Overview

[`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L1-L22) implements the `glsl.helper_invocations` GLSL shader-executor group. The group registers six direct cases that render a triangle twice: the first pass produces input data, and the second fragment shader reads that data through one selected resource-access mechanism. The cases then use `fwidth()` or an input attachment to exercise helper-invocation behavior and validate the resulting `VK_FORMAT_R32_UINT` image on the host.

This page describes the source-defined test coverage and verification logic. It does not claim that the cases were run on the current host.

## Source Code

- Implementation and group factory: [`vktShaderHelperInvocationsTests.cpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L47-L68) ([factory](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L615-L637))
- Public declaration: [`vktShaderHelperInvocationsTests.hpp`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.hpp#L29-L34)
- GLSL-package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1279)
- Test instance setup and execution: [`HelperInvocationsTestInstance`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L70-L448)
- Support checks and shader generation: [`HelperInvocationsTestCase`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L507-L613)

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

The six leaves are added directly to the group by [`addShaderHelperInvocationsTests()`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L615-L630). There are no generated subgroups beneath them.

## Test Families

Each leaf selects one `TestType` and corresponding constructor configuration ([enum and configuration](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L55-L68), [constructor](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L95-L142)). All cases use a 32×32, single-sample `VK_FORMAT_R32_UINT` color image ([render setup](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L162-L183)).

### `load_from_ssbo`

The default path binds the first rendering result as a read-only `std430` storage buffer. The second fragment shader computes a linear pixel index from `gl_FragCoord` and writes `uint(fwidth(v[i]))` ([shader source](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L551-L559)). The input buffer uses `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT` and `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER` ([configuration](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L101-L110)).

### `load_from_address`

This path reads the first rendering result through a buffer reference passed in a fragment-stage push constant. It uses `GL_EXT_buffer_reference` and computes `uint(fwidth(data.v[i]))` ([shader source](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L560-L570)). The buffer has shader-device-address usage, is allocated with the device-address memory requirement, and its address is pushed before the second draw ([configuration and allocation](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L112-L117), [address setup](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L197-L213), [push constant](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L337-L350)).

### `load_from_ubo`

The input is a uniform buffer declared as `uvec4 v[32*8]`. The shader maps the 32×32 image into four-component elements and applies `fwidth()` to the component corresponding to the current x coordinate ([shader source](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L571-L579)). The descriptor is a `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` ([configuration](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L118-L122)).

### `load_from_image`

The input is a read-only `r32ui` storage image. The shader loads the current pixel with `imageLoad()` and writes `uint(fwidth(c))` ([shader source](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L580-L587)). This case uses an image rather than a buffer, with `VK_IMAGE_USAGE_STORAGE_BIT` and `VK_DESCRIPTOR_TYPE_STORAGE_IMAGE` ([configuration](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L123-L128)).

### `load_from_texture`

The input is a sampled `usampler2D`. Normalized coordinates derived from `gl_FragCoord.xy / 32` select the source value, which is then passed to `fwidth()` ([shader source](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L588-L596)). The case creates a sampler and uses `VK_IMAGE_USAGE_SAMPLED_BIT` with `VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER` ([configuration](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L129-L135), [sampler and descriptor setup](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L214-L247)).

### `output_variables`

This case uses a second subpass and an input attachment instead of copying the first result to a separate resource. The first fragment shader writes `y*32+x`; the second reads it with `subpassLoad()` and writes `c + y*x` ([shader generation](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L541-L549), [input-attachment shader](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L597-L604)). Its configuration enables the second subpass and uses `VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT` with `VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT` ([configuration](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L136-L142)).

## Parameter Dimensions

| Dimension | Values / behavior |
|---|---|
| Registered leaves | `load_from_ssbo`, `load_from_address`, `load_from_ubo`, `load_from_image`, `load_from_texture`, and `output_variables` ([case list](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L619-L629)) |
| Internal test types | `LOAD_SSBO`, `LOAD_ADDRESS`, `LOAD_UBO`, `LOAD_IMAGE`, `LOAD_TEXTURE`, and `OUTPUT_VARIABLES` ([enum](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L55-L63)) |
| Render target | 32×32, `VK_FORMAT_R32_UINT`, one sample ([image setup](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L162-L183)) |
| Clear values | First pass clear is `21`; final-pass clear is `30` ([clear values](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L162-L170)) |
| Default derivative expectation | `m_expectedColor` is `63`; the `LOAD_*` verifier accepts `0`, `30`, `63`, or `126` ([constructor](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L101-L110), [verification](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L407-L439)) |
| Input mechanism | Storage buffer, buffer device address, uniform buffer, storage image, sampled texture, or input attachment ([configuration](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L101-L142)) |
| Pass structure | `LOAD_*` cases use two render passes; `output_variables` uses two subpasses in one render pass ([command recording](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L282-L353), [render-pass construction](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L450-L504)) |

## Support / Feature Requirements

| Requirement | Scope / evidence |
|---|---|
| `VK_KHR_buffer_device_address` | Required only by `load_from_address` in [`checkSupport()`](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L525-L529). |
| Device-address-capable allocation | The input buffer requests `MemoryRequirement::DeviceAddress` only for the address case ([allocation](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L197-L204)). |
| Other explicit per-case checks | This source file has no additional explicit checks in `checkSupport()`; other cases rely on the Vulkan resources, descriptors, shader compilation, and render-pass operations used by the instance. |

A missing required capability produces a not-supported result through the shared test infrastructure; it is distinct from a verification failure after a case executes.

## Verification Methods

The common execution path creates an input image, a final image, an input buffer, and a host-visible final buffer. For `LOAD_*`, it renders the triangle once, transfers the first image into the selected input resource where needed, renders again, and copies the final image back for host inspection ([resource setup](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L187-L208), [command recording and readback](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L282-L368)). `output_variables` instead records the two draws as consecutive subpasses with an input-attachment dependency ([render-pass setup](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L471-L504)).

- For `LOAD_*`, every final pixel must be one of `0`, `30`, `63`, or `126`. The test also requires minimum counts for the zero and derivative values and rejects any apparent helper-invocation write: a pixel clear in the input image must remain final-clear in the output ([histogram and write checks](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L407-L439)).
- For `output_variables`, the host checks each pixel against the final clear value or `x + y*32 + x*y`, matching the two generated fragment shaders ([host reference](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L384-L406)).
- A failed result logs both the input and final images before returning `Fail`, providing diagnostics for the executed case ([failure logging](../../../modules/vulkan/shaderexecutor/vktShaderHelperInvocationsTests.cpp#L442-L447)).

## Test Principles

- The six leaves isolate the input/resource access mechanism while sharing triangle geometry, render dimensions, integer format, synchronization, readback, and most validation infrastructure.
- The `LOAD_*` shaders apply `fwidth()` to values obtained through different resource paths. The allowed-value histogram checks both derivative behavior and the preservation of pixels outside the triangle.
- `output_variables` verifies a different path: output from one subpass is consumed as an input attachment in the next, and the result is checked against a per-pixel arithmetic invariant.
- A failure is evidence of disagreement somewhere in the generated shader, pipeline/resource setup, synchronization, or host oracle; it is not by itself proof that only the named GLSL operation is defective.
