# Understanding Brief: EXT mesh-shader miscellaneous tests

## One-Sentence Test Purpose

This source checks whether `VK_EXT_mesh_shader` task and mesh pipelines preserve payloads, barriers, interfaces, output limits, pipeline state, and workgroup behavior while producing the expected framebuffer results.

## Background Knowledge

### EXT task and mesh execution

A task shader can launch mesh workgroups with `EmitMeshTasksEXT`; a mesh shader must set its valid vertex and primitive counts with `SetMeshOutputsEXT` before writing mesh outputs. A task payload is visible to the mesh workgroups launched by that task workgroup. The EXT forms use `gl_TaskCountEXT`, `taskPayloadSharedEXT`, `gl_MeshVerticesEXT`, and the EXT primitive-index arrays.

Why it matters here:
- The source switches between mesh-only and task-plus-mesh cases through `MiscTestParams::taskCount`.
- Payload, barrier, large-dispatch, first-invocation, and control-flow cases turn task/mesh state into visible geometry or a pass/fail color.

### Interface, primitive, and synchronization rules

Mesh outputs can carry per-vertex or per-primitive values to the fragment shader. Interface locations and interpolation qualifiers determine how those values arrive. `barrier()` synchronizes invocations in a workgroup; `memoryBarrierShared()` and `groupMemoryBarrier()` order memory accesses. Primitive topology and the output counts determine which emitted vertices and indices reach rasterization.

Why it matters here:
- `custom_attributes`, clip variants, multiple vertex outputs, and payload cases check stage interfaces and built-ins.
- The memory-barrier family intentionally accepts either of two complete images because its iteration parity is not fixed.

## One Concrete Example

`dEQP-VK.mesh_shader.ext.misc.complex_task_data` launches two task workgroups, each with a nested task payload containing scalar, array, structure, vector, and workgroup-ID-derived members. The mesh shader validates the payload, emits two triangles per mesh workgroup, and places the resulting quadrants from the payload row and mesh workgroup column. The host compares the resulting 8x8 RGBA8 image with the generated reference.

## End-to-End Test Flow

```text
[host] select one of 83 registered misc leaves and its fixed counts, extent, and leaf-specific dimensions
[host] generate GLSL or, for selected cases, source-controlled SPIR-V assembly for task/mesh/fragment stages
[host] create RGBA8 color resources, optional descriptors, push constants, staging/readback buffers, and the graphics pipeline
[device] execute vkCmdDrawMeshTasksEXT; task-enabled cases launch mesh workgroups and may pass task payload data
[device] emit points, lines, triangles, storage-image writes, or pipeline-dependent geometry
[host] transition/copy the result to a host-visible buffer, invalidate it, and compare it with the case reference
[host] return Pass only when the case-specific image or color/depth checks succeed
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Most builders append generated GLSL to `vk::SourceCollections` using `getMinMeshEXTBuildOptions`. That helper selects SPIR-V 1.4 with the EXT mesh-shader build options; the normal CTS build then compiles the source.
- The source generates task, mesh, and fragment code for payload transport, primitive topologies, large workgroups, zero output, barriers, custom attributes, clip/provoking/multiview combinations, push constants, output limits, pipeline mixing, first-invocation behavior, rebinds, and control-flow emission.
- `local_size_id_mesh` and `local_size_id_task` use explicit `SpirVAsmBuildOptions` and source-controlled SPIR-V assembly. `multiple_task_payloads` also has direct assembly, but its registration is inside `if (false)` and therefore does not execute.
- Documentation must describe generated code and preserve any compiler-produced or CTS-authored SPIR-V as an artifact. It must not hand-edit generated SPIR-V.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| RGBA8 color image | yes | color attachment; storage image for task-only paths | written by fragment or task shader | through a copy buffer | Main observable result for common cases. |
| Host-visible verification buffer | yes | transfer destination | written by image-to-buffer copy | yes | Supplies the image comparison. |
| Task storage-image descriptor | yes, task-only paths | task set binding 0 | task shader writes it in relevant paths | indirectly | Allows task-only cases to write the result image without a color attachment. |
| Storage buffers and sampled images | yes, rebind case | task binding 0 and mesh binding 1 | task/mesh shaders read them | no | Exercise descriptor rebinding between four draws. |
| Push constants | yes | task or mesh pipeline layout range | task/mesh shader reads them | no | Carry colors, offsets, or payload-selection data. |
| `taskPayloadSharedEXT` data | no | shader stage storage | task writes, mesh reads | no | Tests task-to-mesh transport and payload layouts. |
| Workgroup shared variables | no | shader-local | invocations read/write | no | Drive barrier and memory-ordering tests. |
| Classic vertex/index and mesh storage buffers | yes | classic and mesh pipeline bindings | stages read them | no | Support mixed-pipeline and work-group-ordering geometry. |
| D16 depth image and readback buffer | yes | depth attachment and transfer source | depth test writes | yes | Work-group ordering compares both color and depth against the final geometry batch. |

## What Is Checked

- The common `MeshShaderMiscInstance::iterate` path creates the configured RGBA8 image, binds generated binaries, dispatches with `vkCmdDrawMeshTasksEXT`, transitions the image to transfer-source layout, copies it to a host-visible buffer, and compares with `tcu::floatThresholdCompare` at `0.005` per channel.
- Primitive leaves compare a generated reference containing the expected point, center line, triangle, maximum output, or clear image. Payload and workgroup leaves derive positions/colors from the generated IDs and payload values.
- Memory-barrier leaves compare against both solid blue and solid black references and pass if either complete image matches within the common threshold.
- `custom_attributes` makes the fragment shader require valid primitive IDs, viewport index, interpolated and flat custom attributes, and per-primitive values before emitting blue.
- Clip variants use clip distances or clip planes and may compare multiview results. Mixed-pipeline and rebind cases issue multiple draws, update state or descriptors between draws, and compare quadrant colors. Work-group ordering copies both color and D16 depth and compares them to the final triangle batch.
- `emit_in_control_flow` uses a 2x1 image and an exact threshold: the correct branch colors the left pixel and leaves the right pixel at the different clear color; the `_bad_emit_last` variant checks the opposite `EmitMeshTasksEXT` control-flow placement.

## Behavior Parameter Identification

> **Behavior parameter:** registered test leaf under `mesh_shader.ext.misc`
>
> **Candidate values:** `complex_task_data`, `single_point`, `single_point_default_size`, `single_line`, `single_triangle`, `max_points`, `max_lines`, `max_triangles_workgroupsize_64`, `max_triangles_workgroupsize_32`, `max_triangles_workgroupsize_16`, `many_task_work_groups_x`, `many_mesh_work_groups_x`, `many_task_mesh_work_groups_x`, `many_task_work_groups_y`, `many_mesh_work_groups_y`, `many_task_mesh_work_groups_y`, `many_task_work_groups_z`, `many_mesh_work_groups_z`, `many_task_mesh_work_groups_z`, `no_points`, `no_lines`, `no_triangles`, `barrier_in_task`, `barrier_in_mesh`, `memory_barrier_shared_in_task_struct`, `memory_barrier_shared_in_task_float`, `memory_barrier_shared_in_task_vector`, `memory_barrier_shared_in_task_array`, `memory_barrier_shared_in_task_uint64`, `memory_barrier_shared_in_mesh_struct`, `memory_barrier_shared_in_mesh_float`, `memory_barrier_shared_in_mesh_vector`, `memory_barrier_shared_in_mesh_array`, `memory_barrier_shared_in_mesh_uint64`, `group_memory_barrier_in_task_struct`, `group_memory_barrier_in_task_float`, `group_memory_barrier_in_task_vector`, `group_memory_barrier_in_task_array`, `group_memory_barrier_in_task_uint64`, `group_memory_barrier_in_mesh_struct`, `group_memory_barrier_in_mesh_float`, `group_memory_barrier_in_mesh_vector`, `group_memory_barrier_in_mesh_array`, `group_memory_barrier_in_mesh_uint64`, `custom_attributes`, `custom_attributes_and_task_shader`, the 16 clip/plane task/provoking/multiview combinations, `push_constant`, `push_constant_and_task_shader`, `maximize_primitives`, `maximize_vertices`, `maximize_invocations_32`, `maximize_invocations_64`, `maximize_invocations_128`, `maximize_invocations_256`, `mixed_pipelines`, `mixed_pipelines_dynamic_topology`, `first_invocation_mesh`, `first_invocation_task`, `local_size_id_mesh`, `local_size_id_task`, `payload_read`, `rebind_sets`, `multiple_outputs_vertices`, `payload_not_accessed`, `emit_in_control_flow`, `emit_in_control_flow_bad_emit_last`, `work_group_ordering`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `complex_task_data` | Task-payload layout or value transport, mesh validation, workgroup-ID placement, primitive emission, rasterization, copyback, or reference mismatch. |
| `single_point`, `single_point_default_size`, `single_line`, `single_triangle` | Primitive topology, `SetMeshOutputsEXT`, point-size/default-size behavior, vertex/index emission, rasterization, or image comparison. |
| `max_points`, `max_lines`, `max_triangles_workgroupsize_64`, `max_triangles_workgroupsize_32`, `max_triangles_workgroupsize_16`, `maximize_primitives`, `maximize_vertices`, `maximize_invocations_32`, `maximize_invocations_64`, `maximize_invocations_128`, `maximize_invocations_256` | Mesh output-count/local-size limit handling, generated indexing, shader compilation, rasterization, or host reference construction. |
| `many_task_work_groups_x`, `many_mesh_work_groups_x`, `many_task_mesh_work_groups_x`, and the corresponding `_y`/`_z` leaves | Dispatch dimension limits, task-to-mesh indexing, generated point placement, or large-image copyback/comparison. |
| `no_points`, `no_lines`, `no_triangles` | Incorrect zero primitive count, illegal output writes, topology handling, or non-clear framebuffer result. |
| `barrier_in_task`, `barrier_in_mesh`, the `memory_barrier_shared_*` leaves, or the `group_memory_barrier_*` leaves | Workgroup control synchronization, shared-memory ordering, payload representation, atomic/update behavior, or accepted-reference handling. |
| `custom_attributes`, `custom_attributes_and_task_shader` | Custom interface qualifiers, primitive ID, viewport index, clip-distance data, task transport, or descriptor-backed value checks. |
| Any `clip_*` or `clip_plane*` leaf | Clip-distance/clip-plane behavior, multiview mesh support, provoking-vertex selection, task transport, or framebuffer comparison. |
| `push_constant`, `push_constant_and_task_shader` | Push-constant range/stage visibility, payload transport, primitive output, or image comparison. |
| `mixed_pipelines`, `mixed_pipelines_dynamic_topology` | Classic/mesh pipeline compatibility, dynamic topology state, descriptor or push-constant state, rasterization, or quadrant reference. |
| `first_invocation_mesh`, `first_invocation_task` | First-invocation semantics, subgroup-basic behavior, task count, mesh output count, or pixel-count comparison. |
| `local_size_id_mesh`, `local_size_id_task` | Maintenance4/SPIR-V `LocalSizeId` handling, specialization-map values, generated direct assembly, or output comparison. |
| `payload_read`, `rebind_sets`, `multiple_outputs_vertices`, `payload_not_accessed` | Payload visibility, descriptor-set rebinding, per-vertex interpolation, push constants, generated outputs, or copyback. |
| `emit_in_control_flow`, `emit_in_control_flow_bad_emit_last` | Dynamic control-flow placement of `EmitMeshTasksEXT`, first-invocation semantics, or exact 2x1 image result. |
| `work_group_ordering` | Task/mesh workgroup ordering, storage-buffer geometry reads, color/depth rasterization, or final-batch reference comparison. |

## Important Variations and Special Cases

- Every ordinary case uses `checkTaskMeshShaderSupportEXT(context, requireTask, true)`, which requires `VK_EXT_mesh_shader` and the EXT `meshShader` feature; task-enabled cases also require the EXT `taskShader` feature. `genericCheckSupport` adds `vertexPipelineStoresAndAtomics` only when a case requests it.
- `single_point_default_size` is the only single-point leaf with `writePointSize == false`; it additionally requires `VK_KHR_maintenance5` and checks the default point size of `1.0f`.
- `custom_attributes` requires core `multiViewport` and `shaderClipDistance`. Clip cases require those same core features; provoking-last cases require `VK_EXT_provoking_vertex`; multiview cases require both multiview and EXT `multiviewMeshShader`.
- Maximize cases query EXT mesh properties and prune when the requested local invocation count, output vertex count, or output primitive count is unsupported. The three large-workgroup dimension suffixes each select x, y, or z as the stressed dispatch coordinate.
- `local_size_id_*` requires `VK_KHR_maintenance4`, uses SPIR-V 1.5 with maintenance4 allowed, and specializes three workgroup dimensions through a specialization map. `first_invocation_*` additionally requires Vulkan API 1.1 and subgroup basic operations.
- `rebind_sets` requires task and mesh support, binds four storage buffers and four sampled 1x1 images, then changes descriptor sets and mesh push constants between four draws. `work_group_ordering` requires task/mesh support plus `vertexPipelineStoresAndAtomics`.
- `multiple_task_payloads` is disabled by `if (false)` because the source says the case may be illegal. `no_*_extra_writes` is also deliberately skipped by `continue` and is absent from registration. Neither belongs in mustpass coverage.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shared parameters, support, generated fragment, dispatch, copyback, comparison | [common EXT case and instance](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L72-L465) | Defines the common parameter model, EXT support gate, image resources, barriers, and threshold. |
| Payload, primitive, large-workgroup, zero-output, and barrier builders | [EXT miscellaneous implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L467-L2128) | Defines generated shader branches and references for the first behavior groups. |
| Attributes, clipping, push constants, and limit cases | [EXT attribute/clip/limit implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L2129-L4173) | Defines feature gates, interface outputs, clip variants, and maximization behavior. |
| First invocation and `LocalSizeId` | [EXT invocation/assembly paths](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L4379-L4954) | Defines subgroup/API gates and direct SPIR-V specialization behavior. |
| Payload, descriptor, output, control-flow, and ordering cases | [EXT later implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L4955-L6704) | Defines special resources, exact checks, and direct function-case runtime paths. |
| Registration hierarchy and pruning | [EXT registration function](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTestsEXT.cpp#L6708-L7200) | Defines all 83 registered leaves, dimensions, and disabled branches. |
| EXT support and shader build target | [mesh-shader utilities](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L149) | Requires the extension/features and selects SPIR-V 1.4 for generated GLSL. |
| vk-default coverage | [mesh-shader mustpass](../../../mustpass/main/vk-default/mesh-shader.txt#L1930-L2012) | Contains exactly the 83 `mesh_shader.ext.misc` paths. |
| Task/mesh execution and outputs | [mesh shader specification chapter](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc) | The chapter's EXT conditionals define task dispatch, payload, and mesh output semantics. |
| Shader interfaces and locations | [interfaces specification chapter](../../../../vulkan-docs/src/chapters/interfaces.adoc#L55-L292) | Grounds interpolation, interface matching, and location explanations. |
| Workgroups and barriers | [shaders specification chapter](../../../../vulkan-docs/src/chapters/shaders.adoc#L2387-L2481) | Grounds workgroup execution and synchronization explanations. |
| EXT feature and property gates | [features](../../../../vulkan-docs/src/chapters/features.adoc#L1845-L1911) and [mesh limits](../../../../vulkan-docs/src/chapters/limits.adoc#L6213-L6242) | Grounds `taskShader`, `meshShader`, multiview, and output-limit pruning. |
| Mesh pipeline stages and drawing | [pipelines](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1155-L1170) and [mesh draw validity](../../../../vulkan-docs/src/chapters/commonvalidity/draw_mesh_common.adoc) | Grounds pipeline stage and `vkCmdDrawMeshTasksEXT` behavior. |

## Questions / Risk Points for User Audit

- The source mixes ordinary generated GLSL with CTS-authored direct SPIR-V. The final page must keep that distinction and must not present hand-edited assembly.
- The common source registers 83 direct leaves, while the memory-barrier and clip families expand several naming dimensions. The final hierarchy must list the exact leaf names rather than inventing intermediate nodes.
- The `multiple_task_payloads` and extra-write code is useful for explaining pruning but must not be counted as executable coverage.

No unresolved semantic risk point remains after inspecting the complete source, specification chapters, registration function, shader build helpers, and `vk-default` list.

## Conversion Notes for Final Wiki Rewrite

- Use `complex_task_data` for the one representative shader walkthrough. It shows the task payload producer, mesh consumer, generated EXT GLSL, and image reference without duplicating every leaf.
- Explain `local_size_id_*` as a direct-SPIR-V workflow in prose; do not reproduce or edit its large assembly in the page.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Preserve all 83 direct children in one `mesh_shader.ext.misc` tree, then explain the dimensions and exact mustpass count in tables and prose.
