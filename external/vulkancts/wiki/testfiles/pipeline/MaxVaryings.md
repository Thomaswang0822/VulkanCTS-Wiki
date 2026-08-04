## Overview

**Core question:** Can a graphics-stage chain carry the maximum tested number of 32-bit varying components across a selected shader-stage interface and still produce the expected fragment result?

- This page documents the `max_varyings` test family implemented by [`vktPipelineMaxVaryingsTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L57-L1158).
- Six test case leaves select vertex-to-fragment, tessellation-evaluation-to-fragment, or geometry-to-fragment pipelines, then stress either the producer output or fragment input side of that interface.
- The test converts the device's component limits into a specialization-sized `ivec4` array, sends indexed values through the interface, and accepts only an all-green rendered image.
- The same six leaves occur under seven pipeline-construction roots in the Vulkan default mustpass scope: monolithic, two graphics-pipeline-library modes, and four shader-object modes.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- A user-defined shader interface uses `Location` decorations. For the 32-bit types used here, a location has four component slots, so an `ivec4` consumes one location. The Vulkan specification defines this accounting in [Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-locations).
- Stage-specific component limits translate to available interface locations by division by four. The [interface limits table](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-limits) lists the vertex-output, tessellation-evaluation input/output, geometry input/output, and fragment-input limits used here.
- `gl_Position` is a built-in vertex-like output. This test reserves one four-component output slot for it when it calculates a producer array length.
- A Vulkan specialization constant supplies a value when the shader is specialized during pipeline or shader-object creation. Here it makes the SPIR-V array type large enough for the current device without maintaining a separate shader binary for every limit.

## Registration Hierarchy

```text
pipeline.monolithic.max_varyings
├── test_vertex_io_between_vertex_fragment
├── test_fragment_io_between_vertex_fragment
├── test_tess_eval_io_between_tess_eval_fragment
├── test_fragment_io_between_tess_eval_fragment
├── test_geometry_io_between_geometry_fragment
└── test_fragment_io_between_geometry_fragment
```

The source registers these six leaves in [`createMaxVaryingsTests`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1133-L1158). Equivalent leaf sets are also present under `pipeline.pipeline_library`, `pipeline.fast_linked_library`, `pipeline.shader_object_unlinked_spirv`, `pipeline.shader_object_unlinked_binary`, `pipeline.shader_object_linked_spirv`, and `pipeline.shader_object_linked_binary`. Each of the seven mustpass files contains six `max_varyings` entries.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Test case leaf | `test_vertex_io_between_vertex_fragment`, `test_fragment_io_between_vertex_fragment`, `test_tess_eval_io_between_tess_eval_fragment`, `test_fragment_io_between_tess_eval_fragment`, `test_geometry_io_between_geometry_fragment`, `test_fragment_io_between_geometry_fragment` | Selects the stage chain and whether the stressed side is the producer or fragment input. | [`createMaxVaryingsTests`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1133-L1158) |
| `pipelineConstructionType` | monolithic, pipeline-library, fast-linked-library, shader-object-unlinked-SPIR-V, shader-object-unlinked-binary, shader-object-linked-SPIR-V, shader-object-linked-binary | Reuses the same interface test under the pipeline construction roots represented in the mustpass files. | [`vktPipelineTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L166-L176) |
| Producer stage | `VK_SHADER_STAGE_VERTEX_BIT`, `VK_SHADER_STAGE_TESSELLATION_EVALUATION_BIT`, `VK_SHADER_STAGE_GEOMETRY_BIT` | Determines the output-component limit used to size the producer array. | [`getMaxIOComponents`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L915-L948) |
| Consumer stage | `VK_SHADER_STAGE_FRAGMENT_BIT` | Supplies the input-component limit for the matching fragment array. | [`getMaxIOComponents`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L939-L942) |
| Array length | `min(maxOutput, maxInput)` `ivec4` elements, via `SpecId 0` | Sizes both ends to the largest common interface capacity for the selected pair. Producer capacities subtract one `vec4` for `gl_Position`. | [`test`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L995-L1025) |

## Behavior Parameters

The primary behavioral axis is the registered test case leaf. Each leaf chooses the interface side that must reach its device-reported capacity while the other side supplies the compatible endpoint.

### test_vertex_io_between_vertex_fragment: vertex output capacity

The vertex shader writes every element of its specialization-sized output array before rasterization. The fragment shader consumes the array, so this leaf tests the usable vertex output interface after reserving capacity for `gl_Position`.

### test_fragment_io_between_vertex_fragment: fragment input capacity after vertex output

The vertex shader provides the compatible array, while the fragment shader declares and checks the array at the fragment input limit. This separates fragment input capacity from the preceding vertex output stress leaf.

### test_tess_eval_io_between_tess_eval_fragment: tessellation-evaluation output capacity

A vertex and tessellation-control passthrough establish a patch pipeline. The tessellation-evaluation shader writes the indexed array, then the fragment shader checks it. This leaf requires `tessellationShader`.

### test_fragment_io_between_tess_eval_fragment: fragment input capacity after tessellation evaluation

The tessellation-evaluation stage supplies the compatible output array and the fragment stage is stressed at its input capacity. It also requires `tessellationShader`.

### test_geometry_io_between_geometry_fragment: geometry output capacity

The geometry shader reproduces the input triangle, writes the indexed array for each emitted vertex, and sends it to the fragment shader. This leaf requires `geometryShader`.

### test_fragment_io_between_geometry_fragment: fragment input capacity after geometry

The geometry shader provides the compatible array, while the fragment input array is sized to the fragment limit. It checks the consumer side of the geometry-to-fragment interface and requires `geometryShader`.

## Shader Analysis

[`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L98-L702) builds inline SPIR-V assembly rather than loading a standalone shader file. The producer modules declare a flat `ivec4` array at `Location 0` whose length comes from `SpecId 0`, then write `ivec4(i)` to every element. The fragment module declares the corresponding flat input array, compares each element with `ivec4(i)`, and writes green only if all comparisons pass. The source's vertex, tessellation-evaluation, and geometry variants differ in stage setup and position handling, but share this varying payload pattern.

The test does not embed a representative disassembly here. The inline SPIR-V assembly in the implementation is the authoritative shader source, and a full listing would duplicate it without improving the explanation of the shared interface mechanism.

## Runtime Execution and Result Checking

- The support callback queries features and physical-device limits. Tessellation leaves skip when `tessellationShader` is absent; geometry leaves skip when `geometryShader` is absent. It also skips incompatible producer and fragment capacities rather than attempting a non-common array size. See [`supportedCheck`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L704-L798).
- The test converts the selected producer and fragment limits into `ivec4` element counts, takes their minimum, and installs that integer as specialization constant ID 0 for both relevant stages. [`getMaxIOComponents`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L915-L948) subtracts one element from vertex, tessellation-evaluation, and geometry outputs for position data.
- It creates a 32x32 `VK_FORMAT_R8G8B8A8_UNORM` color attachment, a host-visible transfer-destination buffer, and a six-vertex screen-covering draw. Tessellation cases use patch topology; geometry cases attach a geometry module. The pipeline setup is in [`test`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L950-L1073).
- After the draw, the command buffer transitions the color image from color-attachment output to transfer source, copies it to the host-visible buffer, establishes transfer-write to host-read visibility, submits, and waits. The host invalidates the allocation, builds an all-green reference image, and uses `tcu::floatThresholdCompare` with `tcu::Vec4(0.02f)`. See [`test`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1102-L1129).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `VK_SHADER_STAGE_VERTEX_BIT` | Vertex output interface sizing, specialization, or vertex-to-fragment interpolation/consumption. |
| `VK_SHADER_STAGE_FRAGMENT_BIT` in the vertex-fragment family | Fragment input interface sizing or matching against vertex outputs. |
| `VK_SHADER_STAGE_TESSELLATION_EVALUATION_BIT` | Tessellation-evaluation output interface sizing, tessellation-stage plumbing, or its fragment consumer. |
| `VK_SHADER_STAGE_FRAGMENT_BIT` in the tessellation family | Fragment input interface sizing or matching across the tessellation chain. |
| `VK_SHADER_STAGE_GEOMETRY_BIT` | Geometry output interface sizing, emitted primitive data, or its fragment consumer. |
| `VK_SHADER_STAGE_FRAGMENT_BIT` in the geometry family | Fragment input interface sizing or matching across the geometry chain. |

### Cause Analysis

#### Producer output sizing and propagation

**Possible failure symptoms:** The fragment shader detects at least one indexed `ivec4` value that differs from its expected value, writes red, and the host image comparison fails.

**Possible implementation causes:** A failure may indicate that a stage's output-component limit was applied incorrectly when the specialized array was created, that the position reservation was not honored, or that user-defined output locations were not preserved through the selected stage chain. The Vulkan interface rules define the component accounting, while the CTS source supplies the stage-specific array sizing and payload checks. Further source-level investigation is needed to localize a failure to shader compilation, interface allocation, or a later pipeline stage.

#### Fragment input sizing and matching

**Possible failure symptoms:** A fragment-input stress leaf produces an image that is not within the all-green `0.02` threshold, even though the producer writes the indexed payload.

**Possible implementation causes:** The fragment input declaration may be allocated or matched incorrectly at the selected common capacity. In the tessellation and geometry families, the same visible symptom can also arise while carrying the interface through the intervening stages, so the final image alone does not isolate the fault path.

#### Tessellation or geometry stage handling

**Possible failure symptoms:** Only a tessellation or geometry leaf fails, or the affected chain produces red pixels while the vertex-to-fragment leaves pass.

**Possible implementation causes:** The implementation may mishandle stage-specific output accounting, tessellation patch processing, or geometry emission while transferring the payload to the fragment stage. The test source includes stage-local passthrough and pipeline topology setup, so a failure is an operation-chain classification rather than proof that a single shader stage caused it.

## Case Pruning

### Requirement-based pruning

- Tessellation leaves require the `tessellationShader` feature; geometry leaves require `geometryShader`. Otherwise [`supportedCheck`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L712-L725) reports the case as not supported.
- The support callback rejects a leaf when the selected producer's usable output capacity and fragment input capacity do not permit the leaf's intended limit. The implementation checks both directions so it does not present a smaller endpoint as a maximum-interface test. See [`supportedCheck`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L727-L793).
- The same callback checks requirements for the selected pipeline construction type. See [`supportedCheck`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L796-L797).

### Design-based pruning

- The family tests only vertex, tessellation-evaluation, and geometry producers paired with a fragment consumer. It does not enumerate every legal graphics-stage adjacency.
- The array uses `ivec4` elements at `Location 0`, which makes each element consume one four-component location and keeps the payload check uniform across all six leaves.
- The source uses a single common length, `min(maxOutput, maxInput)`, rather than attempting mismatched endpoint limits. This makes each leaf an executable data-preservation test instead of a pipeline-creation-only limit check.

## Key Takeaways

- `max_varyings` turns device component limits into a concrete cross-stage data path by specializing matching `ivec4` arrays.
- The producer-output leaves reserve one `vec4` for `gl_Position`; the fragment-input leaves test the consumer limit through the same indexed payload.
- The green-image result proves that every tested array element survived the selected graphics-stage chain, but a failure may involve any stage or interface boundary in that chain.
- Feature and capacity checks deliberately prune chains that cannot express the intended maximum-capacity case.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Parameters and names | [`MaxVaryingsParam` and `generateTestName`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L57-L96) | Defines the pipeline construction type, stage roles, stressed side, and exact leaf names. |
| Program generation | [`initPrograms`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L98-L702) | Provides the inline SPIR-V assembly, indexed payload, and selected module chains. |
| Feature and compatibility gates | [`supportedCheck`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L704-L798) | Enforces tessellation/geometry features, common capacities, and construction requirements. |
| Limit conversion | [`getMaxIOComponents`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L915-L948) | Converts physical-device component limits to the array length. |
| Draw and host comparison | [`test`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L950-L1130) | Specializes shaders, renders, copies back, and compares the result. |
| Family registration | [`createMaxVaryingsTests`](../../../modules/vulkan/pipeline/vktPipelineMaxVaryingsTests.cpp#L1133-L1158) | Registers all six leaves. |
| Category registration | [`createPipelineTests`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L166-L176) | Adds this family for each applicable construction root. |
| Vulkan interface accounting | [Location and Component Assignment](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-locations) | Defines locations and component slots. |
| Vulkan stage limits | [Input and output interface limits](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces-limits) | Maps the relevant limits to locations. |
