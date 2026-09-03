# Understanding Brief: EXT mesh shader smoke tests

## One-Sentence Test Purpose

This test family checks that `VK_EXT_mesh_shader` rendering works across the supported pipeline construction modes, with mesh-only, task-to-mesh, no-output task, partial-output, shading-rate, shared-library, and depth-only paths producing the expected framebuffer contents.

## Background Knowledge

### Mesh and task shader execution

A mesh shader workgroup explicitly sets its output vertex and primitive counts, writes `gl_MeshVerticesEXT` and primitive-index built-ins, and replaces the input-assembly and vertex-shader path. An optional task shader runs first and calls `EmitMeshTasksEXT`; each emitted mesh workgroup then produces geometry. A task shader that emits `(0, 0, 0)` launches no mesh workgroup, so its paired mesh shader must not affect the image.

### Pipeline construction choices

The EXT smoke factory uses four registered construction choices. `monolithic` creates one graphics pipeline. `optimized_lib` and `fast_lib` build graphics pipeline libraries and link them with different optimization flags. `shader_objects` uses `VK_EXT_shader_object` stage objects and dynamic binding/state. The construction choice changes API setup, not the expected rendering result.

## One Concrete Example

For `dEQP-VK.mesh_shader.ext.smoke.monolithic.mesh_shader_triangle`, the mesh shader declares a 32x4x4 local size, sets three vertices and one triangle, reads three coordinates and indices from descriptor bindings 0 and 1, and writes a blue per-primitive color. A fragment shader passes that color to an `R8G8B8A8_UNORM` attachment. The host draws one mesh task and expects the 8x8 image to be blue. The `mesh_shader_triangle_rasterization_disabled` sibling omits the fragment shader and enables rasterizer discard, so it expects the clear color instead.

## End-to-End Test Flow

```text
[host] register one of four construction groups and one smoke test case
[host] generate EXT mesh/task/fragment GLSL and compile it with the minimum EXT mesh build options
[host] create host-visible coordinate/index or generated-data buffers, descriptor sets, attachments, and pipeline state
[host] record a mesh-task draw, or the shared-library/shader-object draw sequence
[device] execute task and mesh workgroups when the selected path emits them
[device] rasterize color or depth output, or leave the attachment unchanged for discard/no-output cases
[host] copy the attachment to a host-visible buffer and invalidate it
[host] compare pixels or depth values with the case-specific reference
[host] return pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- EXT GLSL mesh, task, vertex, and fragment sources are emitted by the case-specific `initPrograms` functions and compiled with `getMinMeshEXTBuildOptions`.
- The construction matrix selects a monolithic pipeline, a linked graphics-pipeline-library assembly, or shader objects. The shared-fragment cases also generate both a classic vertex path and a mesh path.
- Gradient cases optionally add `GL_EXT_fragment_shading_rate`, a per-primitive shading-rate output, and a matching pipeline shading-rate state.
- Depth-only cases generate either point or triangle output and either assign `gl_Position` as one vector or component by component.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Coordinate/index buffers | yes | descriptor bindings 0 and 1 | mesh shader reads them | no | Drive the basic triangle vertices and indices. |
| Partial-usage vertex and primitive buffers | yes | descriptor bindings 0 and 1 in two descriptor sets | mesh shader reads them | no | Select front triangles and their per-primitive colors. |
| Push constants | yes | mesh-stage push-constant range | mesh shader reads total count, depth, and red component | no | Selects emitted primitive count and colors in `partial_usage`. |
| Color attachment and copyback buffer | yes | render target, then transfer destination | rasterization writes the image | yes | Supplies pixel data to host checking. |
| Depth attachment and copyback buffer | yes | depth attachment, then transfer source | depth testing and writes update the image | yes | Supplies depth values for depth-only cases. |
| Shader-local task payload | no separate host object | no descriptor binding | task and mesh stages share it | no | Carries the triangle index from task to mesh in `mesh_task_shader_triangle`. |

## What Is Checked

- Basic triangle, partial-usage, and shared-stage cases compare copied color pixels against exact or thresholded reference colors.
- Rasterizer-discard and task-only cases expect the cleared color because no fragment output should reach the color attachment.
- The gradient cases build a 256x256 reference where red is 0, green follows x, and blue follows y. Each shading-rate block must be uniform and its color must match one reference pixel in that block; diagonal blocks crossing two primitives are exempt from the uniformity check.
- Shared fragment cases use `gl_Layer` or `gl_PrimitiveID` to distinguish classic and mesh draws. The host checks every framebuffer/layer pixel against the expected layer or primitive color.
- Depth-only cases build a 64x32 depth reference from deterministic random values and compare the copied `D16_UNORM` image with a threshold of `0.000025f`.

## Behavior Parameter Identification

> **Behavior parameter:** behavioral group, represented by registered test case leaves
>
> **Candidate values:** `mesh_shader_triangle` / `mesh_shader_triangle_rasterization_disabled`, `mesh_task_shader_triangle` / `task_only_shader_triangle`, `partial_usage` / `partial_usage_without_compaction`, `fullscreen_gradient` / `fullscreen_gradient_fs2x1` / `fullscreen_gradient_fs2x2`, `shared_frag_library*` and `shared_frag_shader*`, `depth_only_points*` and `depth_only_triangles*`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `mesh_shader_triangle` / `mesh_shader_triangle_rasterization_disabled` | Mesh output assembly, descriptor reads, rasterizer discard, or basic color attachment handling is wrong. |
| `mesh_task_shader_triangle` / `task_only_shader_triangle` | Task payload propagation, task-to-mesh launch count, or no-output task behavior is wrong. |
| `partial_usage` / `partial_usage_without_compaction` | Variable mesh output counts, unused vertices, per-primitive data, or push-constant addressing is wrong. |
| `fullscreen_gradient` / `fullscreen_gradient_fs2x1` / `fullscreen_gradient_fs2x2` | Mesh interpolation, primitive shading-rate output, or fragment-shading-rate block behavior is wrong. |
| `shared_frag_library*` / `shared_frag_shader*` | Shared fragment-stage interfaces, `gl_Layer` or `gl_PrimitiveID`, pipeline-library linking, or shader-object rebinding is wrong. |
| `depth_only_points*` / `depth_only_triangles*` | Point/triangle mesh output, depth coordinates, depth testing/writes, or component-wise position assignment is wrong. |

## Important Variations and Special Cases

- `optimized_lib` adds link-time optimization flags; `fast_lib` omits the optimization request. Both use the same four library pieces and link either classic vertex or mesh pre-rasterization state with shared fragment/output libraries.
- `shader_objects` is used only for the shared fragment cases in the default mustpass list. The registration code suppresses the ordinary triangle, partial, and gradient children for this construction type, while retaining the depth-only leaves and the eight `shared_frag_shader*` variants.
- `meshFirst` swaps whether mesh or classic drawing occurs first. `primitiveID` uses two framebuffers and a two-pixel-high target; layer cases use one layered framebuffer. `extraInput` adds a location-0 float that multiplies the fragment output.
- `fullscreen_gradient_fs2x1` and `fullscreen_gradient_fs2x2` require `primitiveFragmentShadingRateMeshShader`; the 1x1 case does not.
- All cases call `checkTaskMeshShaderSupportEXT` and `checkPipelineConstructionRequirements`. Task-emitting cases require task and mesh support; mesh-only, gradient, shared, and depth-only paths require mesh support. The `gl_PrimitiveID` shared path also requires the core geometry-shader feature. Layer paths require `VK_EXT_shader_viewport_index_layer` before Vulkan 1.2, or Vulkan 1.2 `shaderOutputLayer`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and construction matrix | [createMeshShaderSmokeTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2547-L2635) | Defines the four construction groups and all registered case leaves. |
| Basic mesh, task, and no-output task shaders | [triangle case builders](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L222-L634) | Shows generated stages, buffers, draw count, and exact color checking. |
| Gradient generation and validation | [gradient builder and runner](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L637-L997) | Shows shading-rate variants and block-based image checking. |
| Partial usage | [PartialUsageCase](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L999-L1545) | Shows compact/non-compact output, two draw calls, and reference construction. |
| Shared fragment variants | [SharedFragLibraryCase](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L1547-L2265) | Shows layer/primitive-ID variants, GPL, ESO, and image comparison. |
| Depth-only variants | [depth-only functions](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTestsEXT.cpp#L2267-L2543) | Shows generated point/triangle geometry and depth comparison. |
| EXT support helpers | [vktMeshShaderUtil.cpp](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L141) | Defines common task/mesh feature checks and EXT shader build setup. |
| Default coverage | [mesh-shader.txt](../../../mustpass/main/vk-default/mesh-shader.txt) | Contains 67 smoke paths: 13 monolithic, 21 optimized-library, 21 fast-library, and 12 shader-object paths. |
| Mesh/task specification | [VK_EXT_mesh_shader](../../../../vulkan-docs/src/chapters/VK_EXT_mesh_shader.adoc) | Defines task/mesh shader execution and output rules. |
| Pipeline libraries | [VK_EXT_graphics_pipeline_library](../../../../vulkan-docs/src/chapters/VK_EXT_graphics_pipeline_library.adoc) | Defines graphics pipeline library construction and linking. |
| Shader objects | [VK_EXT_shader_object](../../../../vulkan-docs/src/chapters/VK_EXT_shader_object.adoc) | Defines per-stage shader-object creation and binding. |

## Questions / Risk Points for User Audit

- [x] Is the construction matrix accurately separated from the behavioral groups?
- [x] Are task-only and mesh-only semantics distinguished?
- [x] Are the gradient and depth reference checks explicit?
- [x] Are shader-object and graphics-pipeline-library variants tied to the actual source branches?
- [x] Are the 67 default mustpass smoke entries counted by construction group?
- [x] Are feature gates stated without claiming that unsupported cases silently pass?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page explanation-first and use `mesh_shader.ext.smoke` with its four direct children as the only registration tree.
- Use construction type as a matrix dimension, but make the behavioral group the primary axis because it changes shader behavior and checking.
- Include one generated-shader walkthrough for the basic mesh-only triangle. The task, partial, gradient, shared-stage, and depth paths belong in parameter and runtime explanations rather than separate walkthroughs.
- Copy the failure mapping table directly into the final page. Write fresh cause-analysis subsections for each distinct mechanism.
- Distill the brief's prerequisites into short mesh/task and construction bullets. Keep the concrete triangle example in the walkthrough.
