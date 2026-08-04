## Overview

**Core question:** Does Vulkan apply each requested extended dynamic state value at the intended point in command-buffer recording, across ordinary draws, multi-iteration sequences, pipeline-construction modes, and mesh-shader variants?

- `vktPipelineExtendedDynamicStateTests.cpp` implements the `pipeline.<construction type>.extended_dynamic_state` test family. It covers EDS1, EDS2, EDS3, and related extension state, including cull mode, front face, rasterization discard, logic operations, color blending, depth/stencil state, vertex input, viewport state, multisampling, conservative rasterization, and line state.
- Each leaf pairs a static pipeline value with a dynamic value, records `vkCmdSet*` at a selected ordering point, draws controlled geometry, and checks the resulting color, depth, and stencil attachments. Some leaves check fragment invocation counts through an atomic buffer.
- The source also registers a `mesh_shader` branch outside Vulkan SC. The `misc` child is implemented by `vktPipelineExtendedDynamicStateMiscTests.cpp` and is kept as a separate implementation boundary.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- Vulkan pipeline state may be static, fixed when a pipeline is created, or dynamic, supplied by a `vkCmdSet*` command for subsequent commands. A dynamic state command must be recorded in a valid command-buffer context and its value remains relevant to later draws until replaced.
- Pipeline construction type changes how state is supplied and bound. The test matrix uses monolithic pipelines and available pipeline-library or shader-object forms, while pruning ordering cases that do not apply to the selected construction.
- Fixed-function state is observed indirectly. The generated shaders supply positions and colors, but rasterization, depth/stencil tests, blending, attachment writes, and sample behavior determine what the host reads back.

## Registration Hierarchy

```text
pipeline.monolithic.extended_dynamic_state
├── cmd_buffer_start
├── before_draw
├── between_pipelines
├── after_pipelines
├── before_good_static
├── two_draws_dynamic
├── two_draws_static
├── three_draws_dynamic
├── mesh_shader
└── misc
```

The listed entries are the direct intermediate nodes beneath the test family. The eight ordering nodes contain ordinary vertex-input leaves. `mesh_shader`, available only outside Vulkan SC, contains its own copy of those ordering nodes. Shader-object construction omits `between_pipelines` and `after_pipelines` in both locations. The factory adds `misc` from the separate source file ([factory](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6974-L7031), [dispatcher](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L156-L180)).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Direct intermediate node | eight ordinary ordering nodes, `mesh_shader`, or `misc` | Selects an ordinary ordering matrix, the nested mesh-shader ordering matrix, or the separately implemented miscellaneous tests. | [factory](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6974-L7031) |
| Ordering | `cmd_buffer_start`, `before_draw`, `between_pipelines`, `after_pipelines`, `before_good_static`, `two_draws_dynamic`, `two_draws_static`, `three_draws_dynamic` | Selects when dynamic state is recorded and how many pipeline binds or render-pass iterations surround it. These values appear directly for ordinary cases and beneath `mesh_shader` for mesh cases. | [ordering table](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6987-L7000) |
| Dynamic state property | EDS1, EDS2, EDS3, and related extension-state leaves | Selects the fixed-function state being compared, such as cull mode, depth compare op, stencil operation, topology, viewport, blend equation, or sample mask. | [test registration](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L7043-L7065) |
| Static/dynamic value pair | deliberately different static and dynamic values; reversed cases | Makes the selected state observable and checks both dynamic-first and correct-static-last arrangements. | [swap rationale](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L3102-L3110) |
| Render-pass iteration count | one, two, or three | Tests state persistence and replacement across separately rendered framebuffers; the first iteration in `three_draws_dynamic` moves its draw off-screen because it is only a setup step. | [iteration sequence](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6408-L6515) |
| Pipeline construction | `monolithic`, `pipeline_library`, `fast_linked_library`, and `shader_object_unlinked_spirv` in the inspected `vk-default` lists | Selects the construction path used to bind the state. Shader-object construction prunes two ordering nodes. | [construction dispatch](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L156-L180) |

The inspected `vk-default` mustpass inventories contain 14,920 matching `extended_dynamic_state` leaves in total. The two named pipeline-library lists contain 4,027 entries each. Counts include the large state matrix and the smaller `misc` leaves; the registered source hierarchy, not a hand-maintained leaf list, is the authoritative scope.

## Behavior Parameters

The primary behavioral axis is the direct intermediate node. The eight ordinary nodes directly select an ordering, `mesh_shader` delegates to the same ordering matrix using mesh shaders, and `misc` delegates to a separate implementation. Within either main ordering matrix, the ordering determines the host/device timeline while the leaf name determines the state contract.

### `cmd_buffer_start`: dynamic state before pipeline binding

`setDynamicStates()` records the selected dynamic values before the render pass and pipeline binds. The later draw must use those values. This catches implementations that fail to retain dynamic state recorded before a pipeline is bound.

### `before_draw`: dynamic state immediately before drawing

The test binds the dynamic pipeline and records the dynamic state after push constants and before the draw. This is the direct command-to-draw case and provides a baseline for the other orderings.

### `between_pipelines`: dynamic state between static and dynamic pipeline binds

The test begins rendering, binds the static pipeline, records dynamic state, and then binds the dynamic pipeline. Shader-object construction skips this node. The case checks that the second pipeline does not discard the dynamic value recorded between binds.

### `after_pipelines`: dynamic state after pipeline binds

The static and dynamic pipelines are bound before the dynamic command is recorded. The subsequent draw must use the command's value rather than a value left by either pipeline.

### `before_good_static`: correct static pipeline bound after dynamic state

The test records the dynamic value after a dynamic pipeline has been bound, then binds a second static pipeline whose value is correct. These cases reverse the usual wrong-static/good-dynamic arrangement and verify that the final static pipeline supplies the expected value.

### `two_draws_dynamic`: static draw followed by dynamic draw

The first render-pass iteration uses a bad static pipeline. The second iteration uses a separate framebuffer, binds the dynamic pipeline, sets the expected dynamic state, and draws the relevant geometry. The host checks the attachments from that second iteration.

### `two_draws_static`: dynamic draw followed by correct static draw

The first render-pass iteration uses a bad dynamic value or dynamic pipeline configuration. The second iteration uses a separate framebuffer and binds a correct static pipeline. This is the two-iteration counterpart to `before_good_static`.

### `three_draws_dynamic`: three-stage dynamic transition

The source records three render-pass iterations, each with its own framebuffer. The first dynamic draw is forced off-screen, a middle iteration uses the static pipeline, and the final iteration returns to the dynamic pipeline. The host reads only the final iteration's attachments; an optional fragment counter can accumulate invocations across iterations.

### `mesh_shader`: nested mesh-shader ordering matrix

This intermediate node repeats all eight ordering nodes with mesh shaders. Mesh shader storage-buffer descriptors provide vertex-like data, and `vkCmdDrawMeshTasksEXT` launches the mesh work. The same fixed-function state is checked, but mesh-shader support and non-VulkanSC availability become additional requirements.

### `misc`: separate miscellaneous implementation

This intermediate node is registered by the main factory but implemented by `vktPipelineExtendedDynamicStateMiscTests.cpp`. Its rasterization-sample and sample-shading behavior is outside this page's main ordering matrix; the boundary is documented here without attributing the main implementation's runtime flow to those leaves.

## Shader Analysis

The shaders support the test rather than implement the dynamic-state property. `initPrograms()` generates a vertex shader that computes positions from vertex-generator output and push constants, and a fragment shader that writes configured colors to the requested attachments. Depending on the case, the source also generates geometry/tessellation stages, mesh shaders, or an atomic counter declaration.

No representative shader walkthrough is included: reconstructing the shader would explain geometry setup, but it would not explain why a fixed-function dynamic value should affect the readback. The useful shader facts are the output locations, pushed depth/color values, generated geometry, and optional fragment counter.

## Runtime Execution and Result Checking

- `checkSupport()` derives required extensions from the selected state property and checks EDS1/EDS3 feature bits, device features, format/sample-count support, queue and limit requirements, mesh-shader support, and construction-type constraints. Optional unsupported combinations raise `NotSupportedError`.
- `iterate()` chooses a depth/stencil format, creates one color image per color attachment and iteration, creates a depth/stencil image per iteration, and creates resolve images for multisample cases. It then builds render-pass/framebuffer objects, pipeline layouts, static/dynamic pipelines, and optional descriptor sets.
- The command buffer records one, two, or three render-pass iterations. The placement of `setDynamicStates()`, static and dynamic pipeline binds, vertex-buffer binds, push constants, and draw commands follows the selected ordering family.
- Geometry uses `vkCmdDraw`, `vkCmdDrawIndexed`, or `vkCmdDrawMeshTasksEXT`, depending on the leaf. A dynamic vertex stride may move the vertex-buffer bind to the same ordering point as the dynamic state.
- After `vk::submitCommandsAndWait`, the test reads the last color/resolve image and, for non-multisampled depth/stencil, reads both depth and stencil aspects. It generates a reference color image, compares color pixels with a UNORM threshold or exact integer equality, checks depth within the selected format threshold, and requires the exact expected stencil value.
- When fragment atomics are enabled, the host invalidates the counter allocation and checks either a minimum invocation count for representative-fragment tests or an exact sample-count-times-framebuffer-area result for sample-count tests.

## Failure Meaning

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

### Cause Analysis

#### Dynamic-state command or pipeline-state interaction

**Possible failure symptoms:** The final color image differs from the generated reference, or a state-specific depth/stencil result is outside the expected range.

**Possible implementation causes:** The implementation may retain a static value after a valid dynamic command, reset dynamic state on a pipeline bind, apply the command to the wrong pipeline or draw, or use the wrong EDS1/EDS3 feature mapping. The exact property determines which Vulkan state contract is violated.

#### Multi-draw state lifetime

**Possible failure symptoms:** A one-draw case passes but the second or final draw in `two_draws_dynamic`, `two_draws_static`, or `three_draws_dynamic` produces the wrong attachment image or fragment count.

**Possible implementation causes:** State may leak from the earlier draw, fail to persist until the later draw, or be overwritten when the next pipeline is bound. The source intentionally uses wrong and correct values in sequence, so the symptom must be compared with the selected draw order rather than assigned to a particular driver or hardware component in advance.

#### State-specific rendering or shader-support behavior

**Possible failure symptoms:** Only leaves for one state property fail, or an attachment is correct while the optional fragment counter is too low or differs from the exact expected count.

**Possible implementation causes:** The affected EDS state may be applied with incorrect values, feature-specific state may be ignored, or generated geometry/shader-stage interactions may expose an implementation error. For a property-specific diagnosis, inspect the corresponding leaf configuration and Vulkan specification rules.

## Case Pruning

### Requirement-based pruning

- EDS1 cases require `VK_EXT_extended_dynamic_state`; EDS2 cases require `VK_EXT_extended_dynamic_state2` and, where applicable, its logic-op or patch-control-point feature; EDS3 cases require `VK_EXT_extended_dynamic_state3` and the relevant EDS3 feature bit.
- Device features, format usage, sample counts, depth/stencil support, queue availability, viewport limits, mesh-shader support, and optional extensions are checked per configuration. Unsupported combinations are reported as NotSupported.
- Shader-object construction skips `between_pipelines` and `after_pipelines`. Vulkan SC excludes mesh-shader and EDS3-only paths through conditional compilation.
- Some cases require `VK_KHR_maintenance10`, line-rasterization functionality, `VK_EXT_depth_bias_control`, conservative-rasterization properties, or mixed-attachment-sample support.

### Design-based pruning

- The factory does not duplicate the ordering tree for shader objects where the pipeline-bind sequence cannot represent the same test.
- The `mesh_shader` intermediate node contains the same ordering model but uses storage-buffer-backed mesh input instead of ordinary vertex-input setup.
- `bind_unused_ms` leaves, extra pipelines, null-state leaves, and special vertex/topology variants are added only for the configurations where they test a distinct interaction.
- The first draw in `three_draws_dynamic` is moved off-screen when it is a setup draw, preventing it from changing the final framebuffer while preserving the state transition.

## Key Takeaways

- The page's direct axis comprises eight ordering nodes plus the delegated `mesh_shader` and `misc` nodes. In the main and mesh matrices, the ordering determines the command timeline and the leaf state name identifies the fixed-function property being compared.
- A passing case requires more than a successful `vkCmdSet*` call: the effective value must produce the expected attachment contents or fragment count after the complete pipeline/draw sequence.
- Reversed and multi-draw cases distinguish state lifetime and pipeline interaction from the simpler before-draw path.
- The shaders establish controlled geometry and output. The correctness claim belongs to Vulkan's dynamic fixed-function state and the host-side readback checks.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Factory and ordering table | [`createExtendedDynamicStateTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6974-L7036) | Registers the direct families and construction-specific ordering coverage. |
| Dynamic-state support checks | [`ExtendedDynamicStateTest::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L3272-L3745) | Shows feature, extension, format, limit, and construction requirements. |
| Generated programs | [`ExtendedDynamicStateTest::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L3747-L4040) | Defines supporting vertex, fragment, geometry, tessellation, and mesh shader artifacts. |
| Command recording | [`ExtendedDynamicStateInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6405-L6651) | Defines the host/device sequence and command placement. |
| Result checks | [attachment and counter checks](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateTests.cpp#L6653-L6890) | Defines pass/fail conditions and error reporting. |
| Separate misc implementation | [`createExtendedDynamicStateMiscTests()`](../../../modules/vulkan/pipeline/vktPipelineExtendedDynamicStateMiscTests.cpp#L795-L822) | Supports the page boundary for the `misc` registration child. |
| Vulkan dynamic-state specification | [pipeline dynamic state](../../../../vulkan-docs/src/chapters/pipelines.adoc#L2143-L2297) | Grounds the explanation of EDS2/EDS3 state and dynamic command rules. |
