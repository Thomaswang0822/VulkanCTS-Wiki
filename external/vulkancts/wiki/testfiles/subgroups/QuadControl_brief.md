# Understanding Brief: `subgroups.shader_quad_control`

## One-Sentence Test Purpose

This test checks whether a fragment shader uses quad scope control, quad operations, and terminated-invocation rules correctly when rasterization supplies real and helper invocations.

## Background Knowledge

### Quad scope and helper invocations

A quad scope instance contains the four fragment invocations used by quad operations. Fragment shaders that need derivatives or quad group operations can also involve helper invocations for framebuffer locations not covered by rasterized fragments. The Vulkan specification identifies helper invocations through `HelperInvocation` and does not give their stores or atomics ordinary memory effects.

Why it matters here:
- `quad_derivatives` makes the derivative group a quad scope instance with `QuadDerivativesKHR` and calls `subgroupQuadAny`.
- `require_full_quads` uses `gl_HelperInvocation` and quad swaps to distinguish complete quads from quads containing helpers.
- `divergent_condition` tests quad vote results while a fragment-dependent branch is active.

### Termination and quad control

`OpTerminateInvocation` finishes one shader invocation. Later quad operations must observe the active invocation set required by the shader execution rules. `shaderQuadControl` enables the `QuadControlKHR` capability; the fragment source selects related execution modes such as `QuadDerivativesKHR` or `FullQuadsKHR` through GLSL layouts.

Why it matters here:
- `terminated_invocation` removes the bottom-right invocation of each 2 by 2 quad, then checks ballots and quad votes.
- The test's support checks keep the termination case behind `VK_KHR_shader_terminate_invocation` and a reconvergence feature.

## One Concrete Example

The `quad_derivatives` case draws five triangles. One fragment coordinate on each triangle satisfies the generated predicate. The fragment shader asks `subgroupQuadAny` whether any invocation in its quad satisfies that predicate. If so, it samples a different mip level through interpolated texture coordinates; otherwise, it writes a red fallback color. The host later checks five selected pixels against the mip colors that the vertex data is intended to select.

## End-to-End Test Flow

```text
[host] select one of the four `TestMode` values and construct mode-specific vertices
[host] create a 32 by 32 `VK_FORMAT_R8G8B8A8_UNORM` color image and a host-visible output buffer
[host] create a 16 by 16 five-mip sampled texture and clear each mip level to a distinct color
[host] create a nearest, clamp-to-edge sampler and bind it at descriptor set 0, binding 0
[host] generate `vert` and the mode-specific fragment shader with SPIR-V 1.3 build options
[host] record layout transitions, the render pass, one draw, color-image copyback, and a queue wait
[device] execute the fragment shader's quad control and subgroup operations
[device] write either sampled texture color, encoded vote results, or the green/error output
[host] inspect the copied color image with the mode-specific `isResultCorrect` implementation
[host] return pass only when that mode's expected pixel conditions hold
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `vert` is a GLSL vertex shader that copies position and texture coordinates to the fragment stage.
- `frag` is a GLSL fragment shader generated from the selected `TestMode`. Its build options request SPIR-V 1.3.
- `frag_ucf` is an additional termination shader variant using `GL_EXT_subgroup_uniform_control_flow`. The test also prepares `frag` with `GL_EXT_maximal_reconvergence` and selects between them at instance construction.
- The selected `quad_derivatives` shader uses `layout(quad_derivatives) in`, which compiles to the `QuadDerivativesKHR` execution mode.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Vertex buffer | yes | yes | read by vertex input | no | Supplies positions and `inTexCoords`, including coordinates that select the five mip colors. |
| Color image and view | yes | yes as color attachment | written by fragment output | copied to output buffer | Carries the observable result for all four modes. |
| Five-mip texture and view | yes | yes at set 0, binding 0 | sampled by `quad_derivatives` and available to the other fragment shaders | no | Each mip level has a distinct clear color, so the derivative result becomes a visible mip choice. |
| Combined image sampler | yes | yes at set 0, binding 0 | read by the fragment shader | no | Supplies nearest, clamped texture sampling. |
| Host-visible output buffer | yes | transfer destination | written by `cmdCopyImageToBuffer` | yes | Provides the pixel data consumed by `isResultCorrect`. |
| `gl_HelperInvocation` and quad scope | no, shader built-ins | no descriptor binding | observed by fragment shader | indirectly | These are shader execution state, not host-created resources. |

## What Is Checked

- `quad_derivatives` samples five selected pixels and accepts them when each is within `0.1` of the expected mip clear color.
- `require_full_quads` counts rendered pixels, validates the four quad IDs produced by horizontal, vertical, and diagonal swaps, and requires more than 50 pixels in both helper and non-helper classifications.
- `divergent_condition` checks red and green channels against the `subgroupQuadAny` and `subgroupQuadAll` result expected for each 2 by 2 coordinate quad.
- `terminated_invocation` ignores bottom-right pixels, rejects red or blue error channels, and requires more than one row of green triangle pixels.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `quad_derivatives`, `require_full_quads`, `divergent_condition`, `terminated_invocation`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `quad_derivatives` | Incorrect quad derivative grouping or `subgroupQuadAny` participation; implicit texture LOD or coordinate derivatives produce the wrong mip selection; fragment interpolation or image sampling setup is wrong. |
| `require_full_quads` | Incorrect helper invocation creation or `gl_HelperInvocation` reporting; quad lane IDs or quad swap operations are wrong; `subgroupQuadAny` or `subgroupQuadAll` includes the wrong lanes. |
| `divergent_condition` | Quad vote operations do not evaluate the intended four-lane scope under divergent control flow; active-lane participation or coordinate-based expectation is wrong. |
| `terminated_invocation` | Invocation termination does not remove the selected lane from later ballots and quad votes; reconvergence or quad-control handling is wrong; the fragment output records an error. |

## Important Variations and Special Cases

- The four test families share the same draw harness, descriptor binding, color format, and copyback path, but use different vertex geometry and fragment logic.
- `quad_derivatives` renders five triangles at 32 by 32 and uses texture coordinates chosen for mip levels 1, 2, 5, 4, and 3 in the selected pixels. The expected colors are indexed by the source's `expectedColorPerFragment` array.
- `require_full_quads` uses a triangle strip at 128 by 128 to create many helper and non-helper cases.
- `divergent_condition` uses a 16 by 16 full-screen triangle strip and evaluates a coordinate predicate both before and inside a divergent branch.
- `terminated_invocation` uses a 32 by 32 half-screen triangle. It selects `frag_ucf` when maximal reconvergence is unavailable, while support still requires either maximal reconvergence or subgroup uniform control flow.
- The dispatcher and this whole branch are excluded from VulkanSC builds by `#ifndef CTS_USES_VULKANSC`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test mode enumeration and shared draw instance | [`TestMode` and `DrawWithQuadControlInstanceBase`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L53-L100) | Defines the four behavior values and common render state. |
| Host resources, layout transitions, draw, and copyback | [`iterate`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L124-L336) | Shows the resource graph and the host/device timeline. |
| Mode-specific geometry and checks | [`mode instances and result checks`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L339-L597) | Defines the observed outputs for every behavior value. |
| Feature gates and instance selection | [`checkSupport` and `createInstance`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L621-L646) | Establishes the support requirements and mode dispatch. |
| Generated vertex and fragment shaders | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L648-L805) | Provides exact shader branches and the SPIR-V 1.3 target. |
| Registration | [`createSubgroupsQuadControlTests`](../../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L807-L818) | Registers the four direct children under `subgroups.shader_quad_control`. |
| Mustpass evidence | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L38070-L38073) | Lists the four exact default mustpass paths. |
| Quad operations and derivatives | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3572-L3647) | Defines quad scope operations, derivative groups, and helper launches. |
| Helper invocations | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3728-L3773) | Defines helper invocation identity and output/memory effects. |
| Invocation termination | [`shaders.adoc`](../../../../vulkan-docs/src/chapters/shaders.adoc#L1841-L1859) | Defines the effect of `OpTerminateInvocation`. |
| Quad-control feature | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L8889-L8906) | Defines `shaderQuadControl` and the `QuadControlKHR` capability. |
| Termination feature | [`features.adoc`](../../../../vulkan-docs/src/chapters/features.adoc#L5250-L5283) | Defines support for `SPV_KHR_terminate_invocation`. |

## Questions / Risk Points for User Audit

- Does the page distinguish shader execution state such as helper invocations from host-created resources?
- Is the selected `quad_derivatives` path exact enough to audit the generated shader and expected mip colors?
- Are the four family-specific checks clear without requiring the reader to inspect C++ first?
- Should the page expand any additional generated fragment variant into a second walkthrough?
- Are the Vulkan specification links sufficient for the control-flow and termination claims?

## Conversion Notes for Final Wiki Rewrite

- Keep the four test families as the primary behavior axis because each selects a distinct fragment shader and result checker.
- Distill the background into quad scope, helper invocation, and termination prerequisites. Move concrete geometry, resource setup, and expected output details into the corresponding sections.
- Use the `quad_derivatives` case as the single representative shader walkthrough. Its exact mustpass path, `initPrograms` branch, `layout(quad_derivatives) in`, `subgroupQuadAny`, sampler binding, and mip check provide a complete audit trail.
- Copy the `### Failure Cause Mapping` table above directly into the final page. Write the cause analysis fresh.
- Keep the full generated SPIR-V artifact under the walkthrough's final `#### SPIR-V` subsection.
