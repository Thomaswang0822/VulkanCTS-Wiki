## Overview

The `mesh_shader` test category collects Vulkan CTS tests that check task and mesh shader execution, mesh-generated primitives, shader built-ins and interfaces, draw and synchronization commands, limits, queries, and related EXT mesh-shader pipeline behavior.

## Background Knowledge

- A task shader optionally launches mesh workgroups and can pass per-task payload data to them. A mesh shader runs as a workgroup, explicitly sets its output counts, and emits indexed vertices and primitives for rasterization. The NV and EXT branches expose closely related concepts through different extension interfaces.
- Mesh-shader tests replace the ordinary vertex-input and vertex-shader path with shader-generated geometry. Per-vertex values, per-primitive values, primitive indices, and fragment inputs therefore form explicit interfaces that several families validate.
- Vulkan memory dependencies combine execution ordering with availability and visibility for selected access scopes. They matter when a host, transfer, task, mesh, or fragment operation consumes a value produced by an earlier memory access; task-to-mesh payload data is instead carried through the shader interface.
- Vulkan query results have both numerical data and availability state. Mesh-primitives-generated queries count emitted primitives that reach the fragment stage, while pipeline-statistics queries can count task and mesh shader invocations; multiview and command-buffer variants change where or how those results are recorded and retrieved.

## Category Structure

```text
mesh_shader
├── nv
└── ext
```

The `nv` and `ext` branches are registered directly by [vktMeshShaderTests.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderTests.cpp#L55-L85). The NV branch has seven direct families. The EXT branch has eleven direct families, including `pipeline`, which is registered by the EXT built-in implementation file.

## How the Families Fit Together

The category separates tests by the mechanism used to launch mesh work, expose shader state, or observe the result:

- **when** the test checks basic geometry generation or a particular shader built-in, use the smoke and built-in pages;
- **when** the test checks a Vulkan command, memory dependency, property, or query contract, use the corresponding API, synchronization, property, or query page;
- **when** the test changes shader interface declarations or generated output, use the NV miscellaneous/in-out page or the EXT interface page;
- **when** the test combines EXT mesh shaders with conditional rendering, provoking-vertex selection, pipeline construction, or broader miscellaneous state, use the focused EXT pages.

NV and EXT pages are kept separate because their shader built-ins, command entry points, feature structures, and support checks differ even where the observable behavior is similar.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `mesh_shader.nv.api` | [Api](../testfiles/mesh_shader/Api.md) | Direct, indirect, and indirect-count NV mesh draws, buffer layouts, task use, and image checking. |
| `mesh_shader.nv.smoke` | [Smoke](../testfiles/mesh_shader/Smoke.md) | Basic NV mesh/task triangles, task-only behavior, fullscreen gradients, and shading-rate output. |
| `mesh_shader.nv.synchronization` | [Sync](../testfiles/mesh_shader/Sync.md) | NV stage pairs, resource and barrier combinations, memory dependencies, and value propagation. |
| `mesh_shader.nv.property` | [Property](../testfiles/mesh_shader/Property.md) | NV mesh/task limits and property-backed validation. |
| `mesh_shader.nv.builtin` | [Builtin](../testfiles/mesh_shader/Builtin.md) | NV built-in variables, primitive shading rate, generated shader behavior, and rasterized checks. |
| `mesh_shader.nv.misc` and `mesh_shader.nv.in_out` | [Misc](../testfiles/mesh_shader/Misc.md) | NV miscellaneous execution plus the NV mesh/task interface-variable matrix. |
| `mesh_shader.ext.api` | [ApiExt](../testfiles/mesh_shader/ApiExt.md) | EXT direct, indirect, indirect-count, secondary-command-buffer, and device-address draw forms. |
| `mesh_shader.ext.smoke` | [SmokeExt](../testfiles/mesh_shader/SmokeExt.md) | EXT smoke geometry, task launch, partial output, gradients, shared fragments, depth paths, and construction modes. |
| `mesh_shader.ext.synchronization` | [SyncExt](../testfiles/mesh_shader/SyncExt.md) | EXT synchronization stage/resource/access matrix and the secondary-command-buffer barrier case. |
| `mesh_shader.ext.builtin` and `mesh_shader.ext.pipeline.builtin` | [BuiltinExt](../testfiles/mesh_shader/BuiltinExt.md) | EXT built-ins, primitive behavior, and pipeline, graphics-pipeline-library, and shader-object construction. |
| `mesh_shader.ext.in_out` | [InOutExt](../testfiles/mesh_shader/InOutExt.md) | EXT interface-variable feature groups, stage ownership, types, interpolation, and permutations. |
| `mesh_shader.ext.properties` | [PropertyExt](../testfiles/mesh_shader/PropertyExt.md) | EXT properties, limits, query-backed values, and shader-supported property checks. |
| `mesh_shader.ext.misc` | [MiscExt](../testfiles/mesh_shader/MiscExt.md) | EXT miscellaneous shader, resource, command, and rendering paths. |
| `mesh_shader.ext.conditional_rendering` | [ConditionalRenderingExt](../testfiles/mesh_shader/ConditionalRenderingExt.md) | Conditional predicate execution around EXT mesh draws and secondary command buffers. |
| `mesh_shader.ext.provoking_vertex` | [ProvokingVertexExt](../testfiles/mesh_shader/ProvokingVertexExt.md) | First and last provoking-vertex modes for mesh-generated lines and triangles. |
| `mesh_shader.ext.query` | [QueryExt](../testfiles/mesh_shader/QueryExt.md) | Mesh primitive and pipeline-statistics queries across reset, retrieval, availability, draw, task, multiview, and command-buffer variants. |

## Category Notes

The registration-only dispatcher is represented by this gateway rather than a separate technical page. The utility helper [vktMeshShaderUtil.cpp](../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L139) supplies common NV and EXT support checks but does not register test cases. The Level-3 pages retain the original `vkt*.md` files as obsolete source-navigation records and use shortened CamelCase names for the rewritten documents.
