# Understanding Brief: Extended Dynamic State

## One-Sentence Test Purpose

This test checks whether dynamically set graphics-pipeline state takes effect at the required command-buffer point and overrides deliberately incorrect static state for the draw that matters.

## Background Knowledge

### Static and dynamic graphics-pipeline state

A graphics pipeline can bake state such as culling, depth testing, blend state, or vertex input into pipeline creation. When a pipeline declares one of those states dynamic, the corresponding `vkCmdSet*` command supplies the value for subsequent draws. The command is stateful within command-buffer recording; the test therefore changes when it is recorded relative to pipeline binds and draws.

Why it matters here:

- The test uses a wrong static value and an expected dynamic value for most cases, so a rendered attachment reveals whether the dynamic command was retained.
- Some sequences reverse that arrangement. A correct static pipeline is bound last, which tests that the CTS harness tracks which value should be effective.

### Fixed-function state is observed through rendering

Most cases use small supporting shaders to draw geometry, while fixed-function state determines culling, clipping, depth/stencil behavior, rasterization, blending, and attachment writes. The shader is normally not the property under test.

Why it matters here:

- Color, depth, and stencil attachment readback turns state selection into a visible pass/fail result.
- A few cases also count fragment invocations with an atomic storage buffer when sample shading or representative-fragment behavior needs an observable count.

## One Concrete Example

A representative `cull_none` case uses a static pipeline that culls front-facing triangles and a dynamic value of `VK_CULL_MODE_NONE`. The draw uses a front-facing triangle. If `vkCmdSetCullMode` is effective at the selected ordering point, the triangle appears in the color attachment; if the implementation retains the static state, it is culled and the attachment remains at its clear value.

The same model applies to other state families, although their expected result can be a depth value, stencil value, blend result, or fragment-count result rather than simply a visible triangle.

## End-to-End Test Flow

```text
[host] create a TestConfig with static and, where applicable, dynamic values
[host] check extension, feature, format, construction-type, and limit requirements
[host] create color and depth/stencil attachments, pipelines, supporting shaders, and optional buffers
[host] record vkCmdSet* at the ordering selected by the registered test path
[host] bind static and/or dynamic pipelines and issue one, two, or three render-pass iterations, using separate framebuffers for multi-draw orderings
[device] apply the effective dynamic or static state to rasterization and fragment operations
[host] submit and wait, then read color, depth, and stencil attachments
[host] compare readback with expected values; check an atomic fragment counter when the case uses one
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`ExtendedDynamicStateTest::initPrograms()` generates vertex, fragment, and when needed geometry, tessellation, or mesh shader source from `TestConfig`. Push constants carry triangle color, depth, viewport index, scale, offsets, and strip scale. The generated shaders establish geometry and outputs; dynamic fixed-function state produces the behavior under test.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Color attachment, and resolve attachment when multisampled | yes | yes | fragment output writes it | yes | Primary visible result for most state cases. |
| Depth/stencil attachment | yes | yes | fixed-function depth/stencil operations update it | yes, unless multisampled depth/stencil is not read | Verifies depth, depth-bounds, and stencil state. |
| Vertex/index buffers or mesh-shader storage buffers | yes | yes | vertex/mesh stages read them | no | Supply geometry and exercise dynamic vertex input or stride. |
| Push constants | yes | yes | graphics stages read them | no | Set draw color, depth, placement, and scale. |
| Fragment counter storage buffer | selected cases only | yes | fragment shader atomically increments it | yes | Makes invocation-count behavior observable. |

## What Is Checked

- Color readback is compared pixel by pixel with the configured expected image. UNORM images use a small threshold; unsigned-integer images require exact equality.
- Non-multisampled depth and stencil readback are compared with the configured depth threshold and exact expected stencil value.
- Cases that use fragment atomics require either an exact expected count or a minimum count, depending on the feature being tested.
- Any mismatch logs the failing attachment and error mask, then returns a CTS failure.

## Behavior Parameter Identification

> **Behavior parameter:** direct intermediate node
>
> **Candidate values:** `cmd_buffer_start`, `before_draw`, `between_pipelines`, `after_pipelines`, `before_good_static`, `two_draws_dynamic`, `two_draws_static`, `three_draws_dynamic`, `mesh_shader`, and `misc`

The direct intermediate node is the primary behavioral axis. The eight ordinary nodes select command ordering, `mesh_shader` delegates to the same nested ordering matrix with mesh shaders, and `misc` delegates to the separate rasterization-sample implementation. Multi-draw orderings use separate framebuffer iterations; attachment validation reads the final iteration while optional counters can accumulate.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `cmd_buffer_start` | Dynamic state recorded before pipeline binding is not retained for the later dynamic draw. |
| `before_draw` | Dynamic state recorded immediately before drawing is not applied to that draw. |
| `between_pipelines` or `after_pipelines` | Pipeline binds incorrectly clear, replace, or ignore previously recorded dynamic state. |
| `before_good_static` | A final static pipeline does not restore the expected static behavior, or static/dynamic value reversal is handled incorrectly. |
| `two_draws_dynamic`, `two_draws_static`, or `three_draws_dynamic` | State or pipeline selection leaks across draws, or the expected final draw uses the wrong effective value. |
| `mesh_shader` | Dynamic state is applied inconsistently when mesh shaders supply the primitive data. |
| `misc` | A dynamic rasterization-sample or sample-shading interaction from the separate miscellaneous implementation fails; diagnose it from that leaf's own oracle rather than the main ordering flow. |

## Important Variations and Special Cases

- `VK_EXT_extended_dynamic_state` supplies EDS1 commands; EDS2 leaves require `VK_EXT_extended_dynamic_state2` and applicable EDS2 feature bits; EDS3 leaves require `VK_EXT_extended_dynamic_state3` and the particular EDS3 feature bit checked by the case.
- The mesh-shader branch is compiled only outside Vulkan SC and also requires mesh-shader support.
- Shader-object construction omits `between_pipelines` and `after_pipelines`, because those ordering concepts depend on the pipeline-binding sequence that shader objects do not use in the same way.
- Some state leaves need further extensions or features, such as line rasterization, depth-bias control, conservative rasterization, or `VK_KHR_maintenance10`; unsupported requirements result in NotSupported rather than an incorrect rendering failure.
- `misc` is registered by the main factory but implemented in `vktPipelineExtendedDynamicStateMiscTests.cpp`; its separate legacy page remains its navigation source.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Factory and ordering registration | [`createExtendedDynamicStateTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6974-L7036) | Defines the registered ordering names and shader-object omission. |
| Dynamic command recording and draw order | [`ExtendedDynamicStateInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6405-L6651) | Shows the placement of `setDynamicStates`, pipeline binds, and draws. |
| Attachment and counter validation | [result checking](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6653-L6890) | Defines color/depth/stencil and optional counter pass conditions. |
| Static/dynamic reversal | [value-swap rationale](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L3102-L3110) | Explains sequences that must finish with a correct static pipeline. |
| Vulkan dynamic-state rules | [pipeline dynamic state](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2143-L2297) | Supplies the API-level context for EDS3 dynamic state. |

## Questions / Risk Points for User Audit

- Does the page make clear that the ordering family is the behavior axis, while each leaf selects one state property?
- Is the distinction between a rendering mismatch and an unsupported optional feature clear?
- Does the `misc` boundary remain explicit without duplicating the separate implementation page?

## Conversion Notes for Final Wiki Rewrite

- Use the ordering family as the final page's behavior parameter and keep its failure-cause mapping unchanged.
- Keep shader discussion short: supporting shader generation is relevant, but representative shader reconstruction would not audit fixed-function dynamic state.
- Preserve the compact registration tree and summarize the large leaf matrix by state families rather than listing every leaf.
