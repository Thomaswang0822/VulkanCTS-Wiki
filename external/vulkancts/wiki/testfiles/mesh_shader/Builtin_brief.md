# Understanding Brief: NV mesh-shader built-in tests

## One-Sentence Test Purpose

This test family checks whether `VK_NV_mesh_shader` exposes mesh- and task-shader built-ins with the specified values and preserves primitive shading-rate outputs through rasterization.

## Background Knowledge

### Mesh and task workgroups

A mesh shader runs as a workgroup and emits vertices and primitives directly. A task shader is optional: when present, it emits the number of mesh workgroups and can pass a `PerTaskNV` payload to each generated mesh workgroup; without it, the draw command launches mesh workgroups directly. The NV specification describes this launch relationship and the `PrimitiveCountNV`/`PrimitiveIndicesNV` output contract in [Mesh Shading](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh).

Why it matters here:
- The `_in_mesh` and `_in_task` cases deliberately read the same conceptual identifiers in different stages.
- The task variants validate both task output/payload transport and the mesh shader's view of its spawned workgroup.

### Per-primitive and per-vertex built-ins

NV mesh output is arrayed: `gl_MeshVerticesNV` carries per-vertex values and `gl_MeshPrimitivesNV` carries per-primitive values. `PrimitiveIndicesNV` selects vertex-array entries for each emitted primitive. Layer, viewport index, and primitive ID therefore describe an emitted primitive, while position, point size, clip distance, and cull distance travel with vertices. The specification's mesh-output and built-in-variable rules define these scopes.

Why it matters here:
- The `layer_shared` and `viewport_index_shared` variants write several primitives from one shared vertex set, so the per-primitive index must remain distinct from vertex indexing.
- The clip/cull cases use interpolation or primitive rejection to turn per-vertex values into visible pixels.

### Fragment shading rate

`PrimitiveShadingRateKHR` contributes a per-primitive fragment shading-rate value. The fragment shader observes the resulting `ShadingRateKHR` value. In this family, the mesh shader gives the top two triangles one mask and the bottom two another; the fragment shader maps its `gl_FragCoord.y` half to the corresponding expected mask.

Why it matters here:
- The three supported sizes are `1x1`, `2x1`, and `2x2`, represented by GLSL masks `0`, horizontal `4`, and horizontal-plus-vertical `5` in the hand-authored SPIR-V path.
- The pipeline's fragment-size state is set to the first unsupported size for the pair, so the primitive contribution is the value that must replace the pipeline state.

## One Concrete Example

For `dEQP-VK.mesh_shader.nv.builtin.position`, the generator emits one triangle around the center of pixel `(0, 0)` in an `8x8` render target. The normalized coordinates are `(-1.0, -0.75)`, `(-0.75, -0.75)`, and `(-0.875, -1.0)`, so only that pixel receives the blue fragment shader color; all other pixels remain the black clear color. This is a reconstructed source example, not a replacement shader artifact.

## End-to-End Test Flow

```text
[host] select one registered built-in child and its fixed source-side parameters
[host] run the support gate for VK_NV_mesh_shader, mesh/task features, and any child-specific feature or limit
[host] generate GLSL task/mesh/fragment programs, or use the source's direct SPIR-V for primitive-id and shading-rate paths
[host] create an 8x8 R8G8B8A8_UNORM color image, render pass, framebuffer, empty descriptor set layout, and graphics pipeline
[host] optionally create and fill a host-visible indirect command buffer
[host] submit direct or indirect mesh-task draws
[device] execute task workgroups when selected, then mesh workgroups and the fragment shader
[device] rasterize the emitted primitives, including layer, viewport, clipping/culling, primitive ID, or shading rate
[host] transition the image, copy it to a host-visible buffer, wait, invalidate the allocation, and inspect pixels
[host] return pass when the selected verifier finds no mismatching pixel
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- GLSL generators create `mesh`, `task` when requested, and `frag` entries in the `SourceCollections` binary collection. Their branch choices change local size, primitive count, payload declarations, coordinates, and built-in expressions.
- `primitive_id_spirv` supplies a direct fragment SPIR-V string because the GLSL path would request the Geometry capability; the source changes that capability to `MeshShadingNV` and keeps `PrimitiveId`.
- Primitive shading-rate cases supply direct mesh SPIR-V with `PrimitiveShadingRateKHR` decorations and source-generated fragment GLSL with the selected top/bottom masks.
- The shared `triangleForPixel` generator converts an integer pixel ID and width into one-pixel-wide triangle coordinates and indexed vertex output.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| 8x8 `VK_FORMAT_R8G8B8A8_UNORM` color image | yes | framebuffer attachment | written by rasterization | copied | observable built-in result |
| Empty descriptor set layout and pipeline layout | yes | pipeline state | no shader descriptor access | no | proves these cases need no user resource |
| Host-visible indirect buffer | only for `draw_index_*` | indirect draw source | read by draw command | no | supplies repeated indirect draws whose `gl_DrawID` is checked |
| Host-visible output buffer | yes | transfer destination | written by image copy | yes | carries the rendered result to the verifier |
| `gl_MeshVerticesNV` / `gl_MeshPrimitivesNV` | no | shader output interface | written by mesh shader | indirectly | shader built-in storage, not host-created buffers |
| `TaskData` `PerTaskNV` block | no | task/mesh interface | task writes, mesh reads | indirectly | transports IDs and sizes in task variants |

## What Is Checked

The common instance uses an 8x8 (or 8x1 for ID/index families) color target cleared to black, executes a mesh draw, copies the target to host memory, and compares exact `tcu::Vec4` values. `FullScreenColorInstance` checks every pixel and layer against an expected color; `QuadrantsInstance` derives one expected color from the pixel quadrant; `PixelsInstance` checks a sparse coordinate-to-color map and a background color. The expected color is blue for the basic and ID/index cases, four fixed colors for layer output, four quadrant colors for viewport output, blue/black for clipping, blue/white/black for culling, and blue for every shading-rate pair.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family/direct child under `mesh_shader.nv.builtin`
>
> **Candidate values:** `position`, `point_size`, `clip_distance`, `cull_distance`, `primitive_id_glsl`, `primitive_id_spirv`, `layer`, `layer_shared`, `viewport_index`, `viewport_index_shared`, `work_group_id_in_mesh`, `work_group_id_in_task`, `local_invocation_id_in_mesh`, `local_invocation_id_in_task`, `local_invocation_index_in_task`, `local_invocation_index_in_mesh`, `global_invocation_id_in_mesh`, `global_invocation_id_in_task`, `draw_index_in_mesh`, `draw_index_in_task`, and the nine `primitive_shading_rate_<top>_<bottom>` values.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `position`, `point_size`, `clip_distance`, `cull_distance` | Incorrect mesh output built-in propagation or rasterization behavior; child-specific point-size, clip, or cull feature/limit handling |
| `primitive_id_glsl`, `primitive_id_spirv` | Incorrect per-primitive `PrimitiveId` propagation, or a GLSL-versus-direct-SPIR-V capability/lowering issue |
| `layer`, `layer_shared` | Incorrect layer selection from per-primitive output, or failure to honor the required layer feature and four-layer framebuffer |
| `viewport_index`, `viewport_index_shared` | Incorrect per-primitive viewport selection or viewport-array feature behavior |
| `work_group_id_in_mesh`, `work_group_id_in_task` | Incorrect mesh workgroup identification, task payload transport, or task-to-mesh launch mapping |
| `local_invocation_id_in_mesh`, `local_invocation_id_in_task`, `local_invocation_index_in_mesh`, `local_invocation_index_in_task` | Incorrect local identifier or linear-index value, `WorkgroupSize` handling, or task payload/index mapping |
| `global_invocation_id_in_mesh`, `global_invocation_id_in_task` | Incorrect global identifier calculation across the eight task groups and eight local invocations, or task payload transport |
| `draw_index_in_mesh`, `draw_index_in_task` | Incorrect dynamically uniform `DrawIndex` for repeated indirect draws, or task payload forwarding |
| any `primitive_shading_rate_<top>_<bottom>` child | Incorrect per-primitive shading-rate decoration, mask interpretation, fragment-state combination, or fragment `ShadingRateKHR` observation |

## Important Variations and Special Cases

- `_in_task` cases use a task shader and `PerTaskNV` data; `_in_mesh` cases use no task shader and read mesh built-ins directly.
- `layer_shared` and `viewport_index_shared` use one workgroup with four local invocations that share the three output vertices; their non-shared counterparts use four workgroups, one primitive each.
- `primitive_id_glsl` uses generated GLSL fragment code and consequently requires the core Geometry Shader feature; `primitive_id_spirv` uses direct SPIR-V instead.
- Primitive shading rate is the only nine-way Cartesian product: top and bottom each independently choose `2x2`, `2x1`, or `1x1`. The implementation passes the first unsupported size as pipeline fragment state and asks the primitive output to replace it.
- The old page's broad “task-needed toggles” description is incomplete: the exact source has fixed child registrations and no additional runtime matrix beyond these choices.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Common support and render/copy flow | [vktMeshShaderBuiltinTests.cpp#L170-L385](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L170-L385) | establishes resources, submission, readback, and NV gate |
| Pixel, quadrant, and layer result checks | [vktMeshShaderBuiltinTests.cpp#L387-L549](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L387-L549) | defines exact host-side pass/fail checks |
| Primitive ID, layer, viewport | [vktMeshShaderBuiltinTests.cpp#L551-L956](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L551-L956) | covers direct-SPIR-V and shared-output variants |
| Position, point, clip, cull | [vktMeshShaderBuiltinTests.cpp#L958-L1347](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L958-L1347) | covers fixed geometry and feature gates |
| Workgroup, local/global invocation, draw index | [vktMeshShaderBuiltinTests.cpp#L1349-L1759](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1349-L1759) | covers generator branches and task payloads |
| Primitive shading rate | [vktMeshShaderBuiltinTests.cpp#L1761-L2037](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L1761-L2037) | covers nine variants and direct SPIR-V |
| Exact registration | [vktMeshShaderBuiltinTests.cpp#L2041-L2091](../../../modules/vulkan/mesh_shader/vktMeshShaderBuiltinTests.cpp#L2041-L2091) | authoritative direct-child tree and Cartesian loop |
| NV support helper | [vktMeshShaderUtil.cpp#L34-L124](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L34-L124) | extension and task/mesh feature checks |
| NV mesh execution model | [Mesh Shading](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh) | task/mesh launch and output rules |
| Built-in semantics | [interfaces.adoc#interfaces-builtin-variables](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables) | specification source for IDs, layer, distances, and shading-rate variables |
| Mustpass coverage | `external/vulkancts/mustpass/main/vk-default/mesh-shader.txt` | exact vk-default leaf list |

## Questions / Risk Points for User Audit

- Does the final page retain the distinction between generated GLSL, direct SPIR-V, and the source's hand-authored SPIR-V strings?
- Is the task payload distinction clear without implying that task variants test a different built-in definition?
- Are the nine shading-rate names and their top/bottom ordering easy to map to the generated masks?
- Does the failure mapping distinguish host readback mismatches from support-time pruning?

## Conversion Notes for Final Wiki Rewrite

- Distill the mesh/task and per-primitive concepts into a short final `Background Knowledge` list.
- Keep the complete direct-child tree in `Registration Hierarchy`; put the 29 exact leaves and their mustpass status in the parameter section rather than expanding leaves in the tree.
- Use the behavior axis as the direct registered child and explain the groups by mechanism.
- Include no more than three walkthroughs. Use the `position` generator as the complete generated-GLSL example; describe the direct-SPIR-V primitive-ID and shading-rate branches in prose and a compact variation table rather than hand-editing their SPIR-V.
- Copy the failure mapping table into the final page and write fresh cause analysis.
- Explain requirement pruning separately from design pruning: unsupported Vulkan features/limits skip cases, while the 3x3 shading-rate matrix and shared/non-shared pairs are deliberate registrations.
