# Understanding Brief: EXT mesh-shader property tests

## One-Sentence Test Purpose

This test checks whether `VK_EXT_mesh_shader` reports legal mesh and task limits and whether shaders can use the advertised boundary resources, output counts, layers, views, and output-memory budgets.

## Background Knowledge

### Queried properties and executable limits

`VkPhysicalDeviceMeshShaderPropertiesEXT` is returned through the physical-device properties query and describes implementation-dependent task and mesh limits. Some fields are scalar limits, some are three-component dimensions, and the two output granularities control how output allocations are rounded.

Why it matters here:
- `limits` compares queried values with Vulkan's required minima or maxima.
- The shader-backed cases use the queried values to derive legal array sizes, output counts, view counts, and memory budgets.

### Mesh output memory and multiview

The Vulkan mesh-output formula counts effective scalar attributes, rounds vertex and primitive allocations to their reported granularities, and multiplies attributes that depend on `gl_ViewIndex` by the number of views. `gl_Position` and `gl_PointSize` consume built-in output storage; primitive indices do not count toward the output-memory total.

Why it matters here:
- The output-size cases vary payload use, per-vertex versus per-primitive locations, and whether values depend on `gl_ViewIndex`.
- Multiview requires both the core `multiview` feature and `multiviewMeshShader`, and the view count must fit `maxMeshMultiviewViewCount`.

## One Concrete Example

A representative `max_mesh_output_size_without_payload_per_primitive_no_view_index` case emits 96 points. The mesh shader writes one `uvec4` value for each selected per-primitive location and writes `gl_Position` and `gl_PointSize` for every point. A fragment shader reads the flat interface block and writes blue when every value matches the expected encoding. The source specializes `locationCount` from the device's output-memory and component limits, so the exact count is device-dependent.

## End-to-End Test Flow

```text
[host] select a registered property case and read EXT mesh-shader properties
[host] reject unsupported features or derive legal boundary sizes from the queried limits
[host] generate GLSL with specialization constants for payload and interface sizes
[host] create the task/mesh/fragment pipeline and host-visible result resource
[host] submit one mesh-task draw, with a task shader when the selected case uses payload
[device] execute payload/shared-memory checks and mesh output/interface checks
[device] write a result flag or color attachment
[host] copy and inspect the storage buffer or image
[host] decide pass/fail, or return a quality warning when the multiview probe is capped at 32 views
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `limits` has no shader-backed artifact. It runs a property-value checker.
- Payload and shared-memory cases generate task and mesh GLSL with specialization constants `payloadElements` and `sharedMemoryElements`.
- Output-size cases generate optional task, mesh, and fragment GLSL. `payloadElements` and `locationCount` become specialization constants, while location type and view-index mode select qualifiers and value expressions.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage buffer | yes | yes, set 0 binding 0 | task/mesh shaders write flags | yes | Carries payload and shared-memory validation results. |
| Color attachment | yes | yes, as a framebuffer attachment | mesh and fragment stages write it | yes, through a transfer buffer | Carries view/layer and output-component/output-size validation results. |
| `taskPayloadSharedEXT` variable | no, shader-local interface | no descriptor | task writes it and mesh reads it | no | Tests task-to-mesh payload transport. |
| `shared` array | no, shader workgroup storage | no descriptor | task or mesh invocations read and write it | no | Tests the stage's shared-memory allocation and barriers. |
| Output interface block | no, shader stage interface | no descriptor | mesh writes it and fragment reads it | indirectly through color | Tests per-vertex/per-primitive output allocation and interpolation-free data transport. |

## What Is Checked

- `limits` logs each value outside its allowed range. It checks required minimums for enabled task and mesh features and the maximum allowed values for `meshOutputPerVertexGranularity` and `meshOutputPerPrimitiveGranularity`.
- Payload and shared-memory shaders write known sequences, synchronize shared-memory accesses with `memoryBarrierShared()` and `barrier()`, and place `1` in result flags only when all values match.
- `max_view_index` reads back every pixel in every used view and expects red `z + 1` for view/layer `z`.
- `max_output_layers` reads back every layer and expects the corresponding layer index plus one.
- Primitive and vertex output-count cases require every SSBO flag to equal `1` after rasterization reaches the fragment shader.
- `max_mesh_output_components` and output-size cases compare a read-back image with the exact expected color. A black pixel records a shader-side interface or payload mismatch.

## Behavior Parameter Identification

> **Behavior parameter:** registered test case leaf
>
> **Candidate values:** `limits`; `task_payload_size`; `task_shared_memory_size`; `task_payload_and_shared_memory_size`; `max_view_index`; `max_output_layers`; `max_mesh_output_primitives_256`; `max_mesh_output_vertices_256`; `max_mesh_output_primitives_512`; `max_mesh_output_vertices_512`; `max_mesh_output_primitives_1024`; `max_mesh_output_vertices_1024`; `max_mesh_output_primitives_2048`; `max_mesh_output_vertices_2048`; `max_mesh_output_components`; `mesh_payload_size`; `mesh_shared_memory_size`; `mesh_payload_and_shared_memory_size`; and the 12 `max_mesh_output_size` combinations with and without payload, per-primitive or per-vertex locations, and the three view-index modes.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `limits` | The implementation reported an EXT property below a required minimum or above an allowed granularity maximum. |
| `task_payload_size` | Task payload allocation or task-to-mesh payload transport failed at the size derived from the reported limits. |
| `task_shared_memory_size` | Task-stage shared-memory allocation, barriers, or value updates failed at the derived size. |
| `task_payload_and_shared_memory_size` | The combined task payload/shared-memory budget or either data path failed. |
| `max_view_index` | Multiview rendering or `gl_ViewIndex` output failed for the tested view count. |
| `max_output_layers` | Layered mesh output, framebuffer-layer selection, or `gl_Layer` handling failed at the usable layer count. |
| `max_mesh_output_primitives_256`, `max_mesh_output_primitives_512`, `max_mesh_output_primitives_1024`, `max_mesh_output_primitives_2048` | The advertised primitive limit was too small, the case was unsupported, or primitive output/indexing failed at the requested count. |
| `max_mesh_output_vertices_256`, `max_mesh_output_vertices_512`, `max_mesh_output_vertices_1024`, `max_mesh_output_vertices_2048` | The advertised vertex limit was too small, the case was unsupported, or vertex output/rasterization failed at the requested count. |
| `max_mesh_output_components` | Mesh output-component allocation or per-primitive interface transport failed at the derived location count. |
| `mesh_payload_size` | The mesh payload/output or payload/shared-memory budget did not support the generated payload path. |
| `mesh_shared_memory_size` | Mesh-stage shared-memory allocation, barriers, or value updates failed at the derived size. |
| `mesh_payload_and_shared_memory_size` | The combined mesh payload/shared-memory budget or either data path failed. |
| Any `max_mesh_output_size_*` case | The selected payload, output location, view-index dependency, or output-memory calculation did not produce the expected interface values and color. |

## Important Variations and Special Cases

- Task payload cases require both task and mesh features. Mesh payload cases require a task feature only when payload is enabled; the mesh-only shared-memory variant does not.
- The output-count loop uses item counts `256`, `512`, `1024`, and `2048` for both primitives and vertices. A vertex case also uses point primitives, so the source limits it by both `maxMeshOutputVertices` and `maxMeshOutputPrimitives`.
- The output-size matrix has 18 registered leaves: two payload modes, two location qualifiers, and three view-index modes. The special no-payload, per-primitive, no-view-index case is also the only child called out in the obsolete page.
- `max_view_index` caps the actual probe at 32 views. A device with a larger `maxMeshMultiviewViewCount` receives a quality warning after a passing 32-view check.
- The `mesh_payload_size` child combines the two EXT properties that constrain mesh payload size; the source comment says it does not correspond to one property field.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| EXT registration | [createMeshShaderPropertyTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderPropertyTestsEXT.cpp#L2429-L2543) | Creates `properties`, all direct children, and the output-size matrix. |
| Common EXT support gate | [checkTaskMeshShaderSupportEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L139) | Requires `VK_EXT_mesh_shader` and selected task/mesh features. |
| Property definitions | [VkPhysicalDeviceMeshShaderPropertiesEXT](../../../../vulkan-docs/src/chapters/limits.adoc#L2325-L2469) | Defines the queried fields. |
| Required property ranges | [EXT mesh-shader limits](../../../../vulkan-docs/src/chapters/limits.adoc#L6873-L6902) | Gives the required minima and granularity maxima. |
| Output-memory formula | [Mesh Shader Output](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#L150-L198) | Defines the storage calculation used by output-size derivation. |
| Multiview feature dependency | [Mesh shader features](../../../../vulkan-docs/src/chapters/features.adoc#L1860-L1900) | Requires `multiview` with `multiviewMeshShader`. |

## Questions / Risk Points for User Audit

- Is the distinction between support skips, property-query failures, and shader-result failures clear?
- Is the 18-case output-size matrix represented without hiding any registered leaf?
- Is the role of output granularity in the derived size calculation clear?
- Does the payload/shared-memory example distinguish shader-local storage from host-created resources?

## Conversion Notes for Final Wiki Rewrite

Use the brief to keep the final page centered on the registered test leaves and the boundary values derived from `VkPhysicalDeviceMeshShaderPropertiesEXT`. Distill the background into queried properties, mesh-output allocation, and multiview prerequisites. Copy the failure mapping table into the final page, then write fresh cause analysis. Keep one representative output-size walkthrough, because the generated mesh and fragment shaders are central to the output-size behavior; do not include a full assembly dump for every matrix variant.
