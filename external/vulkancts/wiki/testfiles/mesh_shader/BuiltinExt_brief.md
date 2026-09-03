# Understanding Brief: EXT mesh-shader built-in and pipeline-construction tests

## One-Sentence Test Purpose

This test checks whether `VK_EXT_mesh_shader` built-in inputs and outputs survive mesh/task execution, rasterization, and fragment observation, including selected graphics pipeline construction modes.

## Background Knowledge

### Mesh and task workgroups

A mesh draw launches mesh workgroups directly, or launches task workgroups that emit mesh workgroups. In the EXT model, a task shader passes a `taskPayloadSharedEXT` payload to the mesh workgroups created by `EmitMeshTasksEXT`; mesh shaders then call `SetMeshOutputsEXT` and provide indexed vertices and primitives.

Why it matters here:
- The `_in_mesh` and `_in_task` leaves compare reading a built-in in the mesh shader with copying the corresponding value through task payload data.
- `gl_WorkGroupID`, local invocation IDs, global invocation IDs, and `gl_DrawID` become visible as different pixel positions, making an identity error observable.

### Per-primitive built-ins and fragment shading rate

EXT mesh outputs can carry per-primitive values such as `gl_Layer`, `gl_ViewportIndex`, `gl_CullPrimitiveEXT`, `gl_PrimitiveID`, and `gl_PrimitiveShadingRateEXT`. These values travel with the primitive rather than with a vertex. The EXT specification also requires `SetMeshOutputsEXT` counts to stay within the shader's literal output limits. Primitive fragment shading rate is consumed by rasterization and can be observed as `gl_ShadingRateEXT` in the fragment shader.

## One Concrete Example

For `dEQP-VK.mesh_shader.ext.builtin.position`, the generator makes an `8x8` target and emits a single triangle around the top-left pixel. The mesh shader declares EXT mesh output, calls `SetMeshOutputsEXT(3u, 1u)`, writes indices `uvec3(0u, 1u, 2u)`, and computes positions `(-1,-0.75)`, `(-0.75,-0.75)`, and `(-0.875,-1)`. The fragment shader writes blue; the host expects only pixel `(0,0)` to be blue and the other pixels to retain the black clear color.

## End-to-End Test Flow

```text
[host] select a registered built-in child and, for the pipeline root, a construction type
[host] check VK_EXT_mesh_shader, task/mesh features, construction requirements, and child-specific features
[host] generate GLSL or direct SPIR-V program artifacts from the selected case
[host] create an 8x8 or 8x1 R8G8B8A8_UNORM color image, view, empty descriptor layout, pipeline layout, render pass, framebuffer, and graphics pipeline
[host] record direct or indirect mesh draws; use task shaders only for task variants
[device] execute task and/or mesh workgroups and rasterize the generated primitives
[device] write color output, then the command buffer transitions the image and copies it to a host-visible buffer
[host] wait, invalidate the allocation, scan the pixel buffer, and compare with the case-specific reference
[host] return pass only for an exact reference match; return NotSupported before execution when a support gate rejects the case
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- EXT GLSL is generated for mesh, task, and fragment stages. `getMinMeshEXTBuildOptions` selects SPIR-V 1.4 with Vulkan-version-dependent options; the primitive-ID SPIR-V fragment variant is a CTS-authored assembly string because it needs `MeshShadingEXT` and `SPV_EXT_mesh_shader` capability/decorations.
- The built-in root registers explicit children. The primitive-shading-rate loop generates the complete 3x3 product of `2x2`, `2x1`, and `1x1` top/bottom sizes. The pipeline factory reuses clip/cull cases while changing only the construction type.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| R8G8B8A8_UNORM color image and view | yes | yes, as color attachment | written by fragment stage | copied through output buffer | stores the observable built-in result |
| Host-visible output buffer | yes | yes, as transfer destination | written by image copy | yes | supplies the exact `tcu::ConstPixelBufferAccess` reference input |
| Indirect draw buffer | only for draw-index cases | yes | read by indirect draw | no | gives repeated draws whose `gl_DrawID` values differ |
| `taskPayloadSharedEXT` data | no, shader-local interface | yes, through task/mesh interface | written by task and read by mesh | no | transports task-side identifiers; it is not a descriptor resource |
| Empty descriptor set layout | yes | pipeline layout only | no descriptor access | no | confirms these built-in tests need no application descriptor data |

## What Is Checked

- `PixelsInstance` compares every pixel with a background plus explicit coordinate map.
- `QuadrantsInstance` selects one of four expected colors by quadrant.
- `FullScreenColorInstance` compares every pixel in every layer against an expected color vector.
- The fragment shader performs a device-side predicate for primitive ID and shading rate; a false predicate writes black, which the host then detects as a pixel mismatch.
- A successful case returns `Pass` only after all expected pixels match exactly.

## Behavior Parameter Identification

> **Behavior parameter:** registered built-in or pipeline-construction leaf
>
> **Candidate values:** `position`, `point_size`, `clip_distance`, `clip_distance_mix`, `cull_distance`, `cull_distance_mix`, `primitive_id_glsl`, `primitive_id_spirv`, `layer`, `layer_shared`, `layer_no_write`, `viewport_index`, `viewport_index_shared`, `viewport_index_no_write`, `work_group_id_in_mesh`, `work_group_id_in_task`, `num_work_groups_mesh`, `num_work_groups_task_and_mesh`, `local_invocation_id_in_mesh`, `local_invocation_id_in_task`, `local_invocation_index_in_mesh`, `local_invocation_index_in_task`, `global_invocation_id_in_mesh`, `global_invocation_id_in_task`, `draw_index_in_mesh`, `draw_index_in_task`, `view_index`, `cull_primitives`, `primitive_shading_rate_<top>_<bottom>`, and pipeline leaves under `optimized_lib`, `fast_lib`, and `shader_objects`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `position`, `point_size`, `clip_distance`, `cull_distance` and their mixed/pipeline variants | Incorrect EXT mesh output built-in propagation, clipping/culling/rasterization, or the selected child feature/limit behavior |
| `primitive_id_glsl`, `primitive_id_spirv` | Incorrect per-primitive `PrimitiveId` propagation or GLSL/direct-SPIR-V capability and lowering behavior |
| `layer`, `layer_shared`, `layer_no_write` | Incorrect layer output semantics, shared per-primitive indexing, or the required no-write behavior |
| `viewport_index`, `viewport_index_shared`, `viewport_index_no_write` | Incorrect viewport selection, shared per-primitive indexing, or the required no-write behavior |
| `work_group_id_*`, `num_work_groups_*`, `local_invocation_*`, `global_invocation_id_*`, `draw_index_*` | Incorrect built-in value, task payload transport, workgroup launch mapping, or indirect draw indexing |
| `view_index` | Incorrect multiview mesh execution or view-dependent per-primitive data |
| `cull_primitives` | Incorrect per-primitive cull decision |
| `primitive_shading_rate_<top>_<bottom>` | Incorrect shading-rate mask, per-primitive decoration, rasterization interpretation, or fragment observation |
| `pipeline.builtin.<optimized_lib|fast_lib|shader_objects>.*` | Correct built-in behavior not preserved by the selected pipeline construction path, or its construction requirements not met |

## Important Variations and Special Cases

- Task variants add a task stage and payload; mesh-only variants read the corresponding mesh built-in directly.
- `layer` and `viewport_index` each have shared-vertex forms. Invocation zero writes common vertices while each local invocation writes a separate primitive and per-primitive value.
- `*_no_write` leaves intentionally omit the output assignment and check the resulting behavior separately from explicit writes.
- `view_index` uses four multiview layers and checks `multiview`, `multiviewMeshShader`, and `maxMeshMultiviewViewCount`.
- Primitive shading rate uses `2x2`, `2x1`, and `1x1` masks, registers all nine ordered pairs, enables `VK_KHR_fragment_shading_rate`, and configures a nontrivial fragment size through the pipeline state.
- `primitive_id_spirv` uses direct CTS-authored SPIR-V. Do not rewrite or hand-edit that generated/authoritative assembly; it differs from the GLSL path by capability and extension details.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| common render/submit/readback flow | [MeshShaderBuiltinInstance::iterate](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L267-L490) | image, pipeline, draw, transfer, and exact result handoff |
| support gates | [MeshShaderBuiltinCase::checkSupport](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L493-L520) and [EXT support helper](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139) | construction and extension/feature checks |
| explicit and generated registrations | [built-in factory](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2560-L2621) | exact built-in children and 3x3 loop |
| pipeline construction factory | [pipeline factory](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L2623-L2652) | optimized, fast-linked, and shader-object roots |
| representative generated shader | [PositionCase::initPrograms](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L1148-L1196) | exact EXT GLSL generation |
| references | [verifier implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTestsEXT.cpp#L542-L703) | mismatch symptoms and reference rules |
| task/mesh semantics | [mesh shading specification](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-task-output) | task payload and EXT mesh output rules |
| built-in semantics | [shader interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables) | built-in interface rules and values |
| pipeline libraries and shader objects | [pipeline libraries](../../../../vulkan-docs/src/chapters/pipelines.adoc#pipelines-library) and [drawing](../../../../vulkan-docs/src/chapters/drawing.adoc#drawing) | construction/binding context |
| exact default coverage | [vk-default mesh-shader](../../../mustpass/main/vk-default/mesh-shader.txt#L541-L577) and [pipeline coverage](../../../mustpass/main/vk-default/mesh-shader.txt#L2013-L2024) | 37 built-in and 12 pipeline leaves |

## Questions / Risk Points for User Audit

- Is the distinction between explicit built-in children and the generated 3x3 shading-rate matrix clear?
- Is the task-payload path distinct enough from a real descriptor resource?
- Should the no-write cases receive a separate walkthrough, or is their behavior sufficiently covered by the parameter summary?
- Is one generated GLSL walkthrough sufficient for this page while direct-SPIR-V remains an authoritative source artifact?

## Conversion Notes for Final Wiki Rewrite

Use the registration factory as the page hierarchy authority. Distill the mesh/task prerequisite into a short Background Knowledge list, retain the resource and host/device timeline, and use one Position walkthrough plus a concise parameter-variation table. Explain the three pipeline construction children under the pipeline root without presenting them as additional built-in behaviors. Keep generated shader text distinct from CTS-authored direct SPIR-V and do not insert hand-edited SPIR-V. Copy the Failure Cause Mapping table into the final page, then write fresh Cause Analysis.
