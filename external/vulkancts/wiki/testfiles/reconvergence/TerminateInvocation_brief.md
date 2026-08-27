# Understanding Brief: `reconvergence.terminate_invocation`

## One-Sentence Test Purpose

This test checks whether fragment shader invocations that execute `terminateInvocation` stop participating in later subgroup, quad, memory-access, and color-output behavior.

## Background Knowledge

### Invocation termination

`OpTerminateInvocation` ends the current shader invocation. A terminated invocation has finished executing instructions, and early fragment termination clears the coverage of its samples. This differs from demotion, which keeps the invocation available as a helper for operations such as derivatives.

Why it matters here:

- Every case puts observable work after `terminateInvocation` and checks that selected invocations do not perform it.
- The cases use later ballots, votes, quad operations, memory accesses, or framebuffer writes to expose an invocation that remained active by mistake.

### Helper invocations, quads, and reconvergence

Fragment processing may create helper invocations so derivative and quad operations have the required neighbors. `layout(full_quads) in` requests four active invocations at the start of each quad. `[[maximally_reconverges]]` requires helper invocations to remain active for the lifetime of their quad unless shader termination ends them.

Why it matters here:

- `terminate_helpers` terminates helpers and then asks a subgroup vote whether any selected invocation remains.
- `quad_any` terminates selected invocations, including helpers, before a quad-scoped vote reads `gl_HelperInvocation`.
- `bit_count` compares subgroup population before and after selected invocations terminate.

## One Concrete Example

The `bit_count` test case uses divisor `2`. Each invocation computes two equivalent predicates from separate push-constant fields. Before termination, the shader records the complete subgroup ballot and the ballot for invocations with an even `gl_SubgroupInvocationID`. It executes `terminateInvocation` under the second predicate, then ballots the surviving invocations.

Passing requires:

```text
selected-for-termination count + surviving count == original active count
```

A surviving fragment writes the sampled red value with blue set to `1`. A terminated fragment writes nothing, so its framebuffer pixel retains the black clear color.

## End-to-End Test Flow

```text
[host] select one of bit_count, terminate_helpers, oob_read, or quad_any
[host] create a 32 by 32 red-gradient texture, black framebuffer, sampler, and one-vec4 storage buffer
[host] bind the sampled image at binding 0 and storage buffer at binding 1
[host] push duplicate divisors, valid and large indices, and framebuffer dimensions
[host] draw a full-screen triangle
[device] run the generated fragment-shader branch for the selected test case
[device] terminate the selected invocations before later subgroup, quad, buffer-read, or color-output work
[device] surviving invocations write the case-specific success color
[host] copy the framebuffer to a host-visible buffer
[host] compare every pixel against the case-specific reference image
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The fixed vertex shader emits a full-screen triangle from `gl_VertexIndex`.
- `TermInvCase::initPrograms` generates one fragment shader with a shared header and one of four test-case bodies.
- All fragment variants use `layout(full_quads) in`. `bit_count` and `terminate_helpers` also use `[[maximally_reconverges]]`.
- Cases that read `gl_HelperInvocation` target SPIR-V 1.6. The other cases target SPIR-V 1.3.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 32 by 32 input texture | yes | yes, descriptor binding `0` | sampled by fragment shader | host retains the source copy | Supplies a nonzero red gradient; successful paths set blue to `1`. |
| One-`vec4` storage buffer | yes | yes, descriptor binding `1` | `oob_read` reads element `0`; other cases do not need its value | no | Element `0` contains `(0, 0, 1, 0)`. The large index is assigned only to invocations that should have terminated. |
| Push constants | yes | yes | read by fragment shader | no | Carry duplicate divisors, indices `0` and `UINT32_MAX`, and framebuffer dimensions. |
| R8G8B8A8 framebuffer | yes | yes, color attachment | cleared, then written by surviving fragments | yes | Encodes termination as untouched black pixels and success as blue-bearing output. |
| Readback buffer | yes | transfer destination | receives copied framebuffer data | yes | Supplies the host-side pixel comparison input. |

## What Is Checked

| Test case leaf | Device-side condition | Host-side expected image |
|----------------|-----------------------|--------------------------|
| `bit_count` | The selected count plus the post-termination alive count equals the original active count. | Even-x pixels remain black; other pixels contain sampled red with blue `1`, with red tolerance `0.005`. |
| `terminate_helpers` | After helper termination, `subgroupAny(should_terminate)` is false. | Every covered pixel contains sampled red with blue `1`, with red tolerance `0.005`. |
| `oob_read` | Surviving invocations choose index `0`; the `UINT32_MAX` choice belongs only to invocations terminated before the load. | Even-x pixels remain black; other pixels contain sampled red plus `(0, 0, 1, 0)`, with red tolerance `0.005`; execution must also complete. |
| `quad_any` | After selected invocations and helpers terminate, `subgroupQuadAny(gl_HelperInvocation)` is false. | Even-x pixels remain black; other pixels are exactly `(0, 0, 1, 1)`. |

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `bit_count`, `terminate_helpers`, `oob_read`, `quad_any`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `bit_count` | Terminated invocations remain represented in the post-termination ballot, or the required reconvergence does not preserve the intended pre/post count relation. |
| `terminate_helpers` | Terminated helper invocations remain active in the later subgroup vote, or helper activity under maximal reconvergence is handled incorrectly. |
| `oob_read` | Code after `terminateInvocation` executes or is lowered so that a terminated invocation can issue the out-of-bounds storage-buffer read. |
| `quad_any` | Terminated helper or selected invocations remain active in the later quad vote, or full-quad participation is handled incorrectly around termination. |

## Important Variations and Special Cases

- `bit_count`, `oob_read`, and `quad_any` use divisor `2`; `terminate_helpers` uses `0` and selects helpers through `gl_HelperInvocation`.
- `bit_count` and `terminate_helpers` require `VK_KHR_shader_maximal_reconvergence`. The other two cases omit the maximal-reconvergence execution mode.
- `terminate_helpers` and `quad_any` require Vulkan 1.3 because they use `gl_HelperInvocation` and compile for SPIR-V 1.6. The other cases require Vulkan 1.1 and compile for SPIR-V 1.3.
- All four cases require fragment-stage subgroup basic support and `VK_KHR_shader_quad_control`. `bit_count` also needs subgroup ballot support; `terminate_helpers` and `quad_any` need subgroup vote support.
- `oob_read` does not test a robustness feature. It places the invalid index on a path that should have ended before the load.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter helpers and support checks | [vktReconvergenceTerminateInvocationTests.cpp#L55-L88](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L55-L88), [#L196-L226](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L196-L226) | Defines divisors, helper-built-in use, API versions, extensions, and subgroup operation requirements. |
| Shader generation | [vktReconvergenceTerminateInvocationTests.cpp#L228-L384](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L228-L384) | Emits the shared fragment interface and all four test-case bodies. |
| Runtime resources and draw | [vktReconvergenceTerminateInvocationTests.cpp#L386-L571](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L386-L571) | Creates resources, records the draw and copy, waits, and starts validation. |
| Pixel validation | [vktReconvergenceTerminateInvocationTests.cpp#L574-L648](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L574-L648) | Builds the three reference-image forms and compares results. |
| Registration | [vktReconvergenceTerminateInvocationTests.cpp#L653-L675](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L653-L675) | Registers the test family and its four executable leaves. |
| Parent attachment | [vktReconvergenceTests.cpp#L7943-L7948](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7943-L7948) | Attaches `terminate_invocation` to the `reconvergence` test category. |
| Mustpass entries | [reconvergence.txt#L3850-L3853](../../../mustpass/main/vk-default/reconvergence.txt#L3850-L3853) | Confirms all four complete registered paths. |
| Shader termination semantics | [shaders.adoc#L1841-L1859](../../../../vulkan-docs/src/chapters/shaders.adoc#L1841-L1859) | Defines invocation termination and `OpTerminateInvocation`. |
| Helper invocation semantics | [shaders.adoc#L3728-L3771](../../../../vulkan-docs/src/chapters/shaders.adoc#L3728-L3771) | Defines helpers and their activity under maximal reconvergence. |
| Quad control semantics | [VK_KHR_shader_quad_control.adoc#L87-L157](../../../../vulkan-docs/src/proposals/VK_KHR_shader_quad_control.adoc#L87-L157) | Defines full quads and quad-scoped all/any operations. |

## Questions / Risk Points for User Audit

- The four test case leaves form the behavioral axis because each selects a distinct post-termination observation.
- The `bit_count` shader is the representative walkthrough because it exposes the core pre-termination versus post-termination population check and includes maximal reconvergence.
- Source, registration, mustpass, runtime validation, and relevant Vulkan specification text resolve the behavior and failure claims used in the final page.
- No unresolved semantic risk changes the walkthrough selection or pass/fail description.

## Conversion Notes for Final Wiki Rewrite

- Distill invocation termination, helper activity, full quads, and maximal reconvergence into the final Background Knowledge section.
- Use `dEQP-VK.reconvergence.terminate_invocation.bit_count` for the representative shader walkthrough.
- Preserve the resource roles and four case-specific host checks, but move source-navigation detail to the appendix.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
