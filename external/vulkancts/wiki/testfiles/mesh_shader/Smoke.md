## Overview

**Core question:** Can the NV mesh-shader path produce the expected triangle or fragment-shading-rate image?

- `vktMeshShaderSmokeTests.cpp` implements the six children under `mesh_shader.nv.smoke`.
- Three children exercise mesh-only, task-plus-mesh, and task-only pipeline behavior with a solid-color triangle.
- Three children render a 256 x 256 fullscreen gradient, with the latter two selecting fragment sizes `2x2` and `2x1`.
- The page explains the registered cases, their shader data flow, support checks, image validation, and the meaning of a failure.

## Background Knowledge

- A mesh shader workgroup writes a bounded set of vertices and primitives instead of consuming a fixed-function vertex-input stream. For the NV extension, `gl_PrimitiveCountNV` selects the emitted primitive count and `gl_PrimitiveIndicesNV` indexes the emitted vertex array. See [Mesh Shader Output](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-output).
- A task shader can emit mesh workgroups through `gl_TaskCountNV` and pass per-task data to those mesh workgroups. Without a task shader, the draw command launches mesh workgroups directly. See [Task Shader Output](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-task-output) and [Mesh Generation](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-generation).
- A fragment shading rate can make one fragment invocation cover a rectangular block of framebuffer pixels. The gradient cases therefore validate uniformity per block and accept a block color only when it equals one of that block's reference pixels. See [Primitive Fragment Shading Rate](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-fragment-shading-rate-primitive).

## Registration Hierarchy

```text
mesh_shader.nv.smoke
├── mesh_shader_triangle
├── mesh_task_shader_triangle
├── task_only_shader_triangle
├── fullscreen_gradient
├── fullscreen_gradient_fs2x2
└── fullscreen_gradient_fs2x1
```

The first three children are `TestCase` instances. The gradient children are function cases that share `initGradientPrograms` and `testFullscreenGradient`, with the fragment-size argument selecting the variant. The complete registration is in [`createMeshShaderSmokeTests`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137-L1152).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Triangle pipeline stages | `mesh_shader_triangle`, `mesh_task_shader_triangle`, `task_only_shader_triangle` | Selects whether the pipeline has a mesh shader only, a task shader that launches mesh work, or a task shader that launches no mesh work. | [`MeshOnlyTriangleCase`, `MeshTaskTriangleCase`, and `TaskOnlyTriangleCase`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L97-L174) |
| Gradient fragment size | `fullscreen_gradient`, `fullscreen_gradient_fs2x2`, `fullscreen_gradient_fs2x1` | Selects the ordinary `1x1` path or the `2x2` and `2x1` shading-rate paths. | [`createMeshShaderSmokeTests`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1145-L1150) |
| Triangle task count | `1` for `mesh_shader_triangle` and `task_only_shader_triangle`; `2` for `mesh_task_shader_triangle` | Controls the number of workgroups issued by `vkCmdDrawMeshTasksNV`. The task shader turns the two input workgroups into two mesh workgroups, each carrying one triangle index. | [`createInstance` methods and draw`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L341-L382), [`MeshTriangleRenderer::iterate`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L514-L522) |
| Triangle geometry and indices | Three vertices with `{0, 1, 2}`; four vertices with `{2, 0, 1, 1, 3, 2}`; three vertices with `{0, 1, 2}` | Supplies the coordinates and index order used by the mesh shader. The task-plus-mesh case uses two triangles to cover a rectangle; the other triangle cases use an oversized triangle. | [`createInstance` methods](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L341-L382) |
| Expected solid color | Blue `(0, 0, 1, 1)`; clear color `(0, 0, 0, 1)` for `task_only_shader_triangle` | Distinguishes a rendered triangle from a task shader that emits zero mesh workgroups. | [`createInstance` methods](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L341-L382) |
| Gradient image extent | `256 x 256 x 1` | Gives the gradient enough distinct pixel colors to detect incorrect primitive shading rates while keeping the test image bounded. | [`gradientImageExtent`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L547-L550) |

## Behavior Parameters

The primary behavioral axis is the registered child. Each child changes the stage topology or the fragment-shading-rate behavior being checked.

### `mesh_shader_triangle` | Mesh shader without a task shader

The graphics pipeline contains a mesh shader and fragment shader, but no task shader. One mesh workgroup emits one triangle, using the uniform coordinate buffer and storage-buffer indices. The host expects the 8 x 8 attachment to contain the exact blue color.

### `mesh_task_shader_triangle` | Task shader launches mesh work

The task shader runs with two input workgroups. Invocation zero writes `gl_TaskCountNV = 1u` and passes `gl_WorkGroupID.x` as `triangleIndex`; each resulting mesh workgroup reads three indices for one triangle. The host expects the two triangles to render the exact blue color.

### `task_only_shader_triangle` | Task shader emits no mesh work

The task shader writes `gl_TaskCountNV = 0u`, so the mesh shader is not launched. The mesh shader source is still supplied in the program collection, but it cannot contribute pixels. The host therefore expects the render target to remain at the black clear color.

### `fullscreen_gradient` | One-by-one fragment shading

The mesh shader emits two triangles covering the 256 x 256 target and passes four corner colors to the fragment shader. With no fragment-size parameter, the host uses a `1x1` rate and checks each pixel block as a single-pixel block.

### `fullscreen_gradient_fs2x2` | Two-by-two fragment shading

The mesh shader emits the same rectangle and writes the `PrimitiveShadingRateKHR` built-in in the direct SPIR-V path. The host treats each `2x2` block as one shading-rate block and accepts any reference color from that block, provided every result pixel in the block is identical.

### `fullscreen_gradient_fs2x1` | Two-by-one fragment shading

This case follows the same gradient construction as `fullscreen_gradient_fs2x2`, but uses a `2x1` block. The changed block dimensions exercise the width-only grouping path in the result checker.

## Shader Analysis

The source contains several shader generators. This walkthrough deliberately focuses on the fixed fragment stage, which receives the mesh stage's interpolated color and copies it to the attachment; the mesh-stage construction and its direct-SPIR-V shading-rate variant are covered in the behavior and variation sections. The `2x2` and `2x1` variants change the mesh primitive-rate output while the fragment stage remains the same.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.mesh_shader.nv.smoke.fullscreen_gradient
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `fullscreen_gradient` | Selects the ordinary gradient path without a fragment-size override. |
| `256 x 256` | Matches the fixed image extent used to derive the corner colors and reference image. |

#### Purpose

The fragment shader forwards the interpolated color produced by the mesh shader to the color attachment. This fragment-stage walkthrough covers the final shader dataflow; the mesh output, interpolation inputs, and host-side block check are described in the surrounding page sections.

#### Structural Design

| Stage | Input | Operation | Output |
|-------|-------|-----------|--------|
| Fragment | Mesh-produced location 0 `inColor` | Copy `inColor` to `outColor`. | RGBA8 color attachment |

#### Shader Code

```glsl
#version 450
layout (location=0) in vec4 inColor;
layout (location=0) out vec4 outColor;
void main ()
{
    /// Preserve the mesh-produced interpolated color for host-side checking.
    outColor = inColor;
}
```

#### Additional Info

- The fragment shader is fixed across all three gradient children. The selected fragment size changes the host block dimensions and, for the two non-default cases, the mesh primitive-rate path.
- The mesh generator is not reproduced in this fragment-stage walkthrough; its rectangle, corner colors, and primitive indices are covered by the page's behavior and runtime sections.
- The reconstructed shader adds one `///` annotation; the source-generated shader has no comments in this function.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|-----------------------------------------|----------|
| Fragment size | `fullscreen_gradient` uses the GLSL mesh generator. `fullscreen_gradient_fs2x2` and `fullscreen_gradient_fs2x1` use the direct SPIR-V mesh generator with a `PrimitiveShadingRateKHR` value (`5` for `2x2`, `4` for `2x1`). The fragment shader is unchanged. | [`initGradientPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L558-L922), [`getSPVShadingRateValue`](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L82-L108) |
| Image extent | The generator fixes `width` and `height` to `256`, so the four corner colors map the green and blue channels to pixel coordinates. | [`gradientImageExtent`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L547-L550), [`initGradientPrograms`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L595-L617) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed GLSL from this walkthrough
- Stage: frag
- Target SPIRV version: spirv1.0

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 13
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor %inColor
               OpExecutionMode %main OriginUpperLeft
               OpSource GLSL 450
               OpName %main "main"
               OpName %outColor "outColor"
               OpName %inColor "inColor"
               OpDecorate %outColor Location 0
               OpDecorate %inColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
%_ptr_Input_v4float = OpTypePointer Input %v4float
    %inColor = OpVariable %_ptr_Input_v4float Input
       %main = OpFunction %void None %3
          %5 = OpLabel
         %12 = OpLoad %v4float %inColor
               OpStore %outColor %12
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The triangle cases allocate host-visible coordinate and index buffers. The mesh shader reads them through descriptor bindings 0 and 1. The renderer creates an 8 x 8 `VK_FORMAT_R8G8B8A8_UNORM` color attachment, binds the optional task module when present, and issues `vkCmdDrawMeshTasksNV` with the case's `taskCount`.
- The renderer submits the command buffer, copies the color attachment into a host-visible output buffer, invalidates the allocation, and compares every pixel with the case's expected solid color using a zero threshold. The expected color is exact because the attachment format represents it exactly.
- The gradient cases use a 256 x 256 `VK_FORMAT_R8G8B8A8_UNORM` attachment. The mesh shader covers it with two triangles, and the fragment shader writes the interpolated location 0 color. The host copies the attachment, builds a reference image where pixel `(x, y)` is `(0, x, y, 255)`, then checks each shading-rate block.
- A gradient block must be uniform. Its color must also equal one of the reference image colors inside that block. A failing block turns its error-mask region red. The test logs the result, reference, and error-mask images before returning `Color mismatch; check log for more details`.

The common execution and triangle validation are implemented in [`MeshTriangleRenderer::iterate`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L385-L545). Gradient rendering and checking are implemented in [`testFullscreenGradient`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L934-L1133).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `mesh_shader_triangle` | Mesh-only pipeline setup, mesh output, descriptor reads, or solid-color attachment validation failed. |
| `mesh_task_shader_triangle` | Task-to-mesh workgroup creation or per-task triangle selection failed, or the resulting triangle did not produce the expected color. |
| `task_only_shader_triangle` | The task shader emitted mesh work unexpectedly, or the clear-color result and host readback path failed. |
| `fullscreen_gradient` | Mesh rectangle output, color interpolation, fragment output, or pixel-level gradient checking failed. |
| `fullscreen_gradient_fs2x2` | The `2x2` primitive shading-rate path or its shader/pipeline setup, block-uniformity, and reference-color check failed. |
| `fullscreen_gradient_fs2x1` | The `2x1` primitive shading-rate path or its block-uniformity and reference-color check failed. |

All six children share the NV extension and mesh-feature gate. A source or build failure before result checking has a separate setup or shader-compilation meaning, not a rendered-image mismatch.

### Cause Analysis

#### Stage topology and mesh output

**Possible failure symptoms:** A triangle case can return a solid-color comparison failure. The task-only case can return a non-black result if the implementation launches mesh work after `gl_TaskCountNV = 0u`.

**Possible implementation causes:** The symptom can result from incorrect task or mesh stage activation, incorrect handling of `gl_TaskCountNV`, `gl_PrimitiveCountNV`, `gl_PrimitiveIndicesNV`, or mesh output built-ins, or incorrect descriptor access. The Vulkan specification defines task output and mesh output limits and semantics in [Task Shader Output](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-task-output) and [Mesh Shader Output](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-output). The exact failing implementation layer requires investigation of the failing case and log.

#### Gradient block validation

**Possible failure symptoms:** The gradient checker logs either `Block not uniform` or `Block color does not match any reference color`, marks the affected block red in `ErrorMask`, and fails the case.

**Possible implementation causes:** The symptom can result from incorrect primitive shading-rate behavior, interpolation or rasterization differences, fragment output errors, or an image copyback problem. The test source does not assign one of these layers in advance, so the result and error-mask images must guide further investigation.

#### Host setup and result comparison

**Possible failure symptoms:** Triangle cases can fail the exact `floatThresholdCompare`, and gradient cases can fail while the rendered image does not satisfy the block checks even if shader compilation and submission completed.

**Possible implementation causes:** A failure can involve render-pass or pipeline setup, command submission, synchronization used by the helper copy path, image layout handling, or host-visible readback. The inspected source establishes the sequence, but it does not identify which layer is defective for a particular failure.

## Case Pruning

### Requirement-based pruning

- Each triangle child calls `checkTaskMeshShaderSupportNV` with `requireMesh = true`. The mesh-plus-task and task-only children also set `requireTask = true`; the mesh-only child does not.
- Each gradient child calls `checkMeshSupport`, which requires `VK_NV_mesh_shader` and the mesh-shader feature but does not require the task-shader feature. The two fragment-size variants additionally use `VK_KHR_fragment_shading_rate` through `PrimitiveShadingRateKHR` and `VkPipelineFragmentShadingRateStateCreateInfoKHR`; this helper does not explicitly check that extension or its primitive-fragment-shading-rate feature, so those prerequisites are not requirement-pruned here. The Vulkan specification defines the primitive rate and its feature requirements in [Primitive Fragment Shading Rate](../../../../vulkan-docs/src/chapters/primsrast.adoc#primsrast-fragment-shading-rate-primitive) and [Mesh Shader Features](../../../../vulkan-docs/src/chapters/features.adoc#features-primitiveFragmentShadingRateMeshShader).
- The mesh shader declares `max_vertices=256` and `max_primitives=256`. The Vulkan specification requires these literal output limits to respect the device's NV mesh-shader properties, and requires `gl_PrimitiveCountNV` to stay within the declared primitive limit. See [Mesh Shader Output](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-output).

A requirement-based skip means the current implementation does not expose the extension or feature needed by the selected case. It is not a rendered-result failure.

### Design-based pruning

- The registration contains one case for each intended triangle stage topology rather than generating a larger Cartesian product of stage presence and geometry.
- The gradient family fixes the image extent and rectangle geometry. It varies only the fragment-size choice needed to cover the ordinary, `2x2`, and `2x1` paths.
- `task_only_shader_triangle` deliberately keeps the mesh shader program available while setting the task output count to zero. The fixed black expectation makes the no-mesh-work behavior observable.

## Key Takeaways

- The six registered children cover three NV task and mesh stage topologies and three gradient shading-rate paths.
- The task-plus-mesh triangle case passes `triangleIndex` through a `PerTaskNV` block and uses two mesh workgroups to draw two triangles.
- The task-only case expects the clear color because `gl_TaskCountNV` is zero.
- Triangle cases use exact solid-color comparison. Gradient cases allow one reference color per shading-rate block but require uniform pixels within each block.
- A support skip records a missing NV extension or requested feature. A test failure means the selected stage behavior, image result, or host-side checking path did not meet the source-defined expectation.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `createMeshShaderSmokeTests` | [`vktMeshShaderSmokeTests.cpp#L1137-L1152`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L1137-L1152) | Registers the six smoke children and binds gradient parameters. |
| Triangle case support and shader setup | [`vktMeshShaderSmokeTests.cpp#L97-L338`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L97-L338) | Defines support gates and mesh/task/fragment shader sources. |
| Triangle case data | [`vktMeshShaderSmokeTests.cpp#L341-L382`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L341-L382) | Selects coordinates, indices, task counts, and expected colors. |
| `MeshTriangleRenderer::iterate` | [`vktMeshShaderSmokeTests.cpp#L385-L545`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L385-L545) | Builds resources and pipeline, draws mesh tasks, copies the image, and checks solid color. |
| `initGradientPrograms` | [`vktMeshShaderSmokeTests.cpp#L547-L922`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L547-L922) | Generates the gradient shaders and the direct SPIR-V shading-rate variant. |
| `testFullscreenGradient` | [`vktMeshShaderSmokeTests.cpp#L934-L1133`](../../../modules/vulkan/mesh_shader/vktMeshShaderSmokeTests.cpp#L934-L1133) | Builds the gradient reference image and performs block validation. |
| `checkTaskMeshShaderSupportNV` | [`vktMeshShaderUtil.cpp#L111-L124`](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L124) | Requires `VK_NV_mesh_shader` and the requested task or mesh feature bits. |
| NV mesh shader specification | [Mesh Shading](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh) | Defines task-to-mesh generation and mesh output semantics used by these cases. |
| Mesh draw common validity | [Mesh draw valid usage](../../../../vulkan-docs/src/chapters/commonvalidity/draw_mesh_common.adoc) | Provides common mesh-draw pipeline restrictions relevant to the command path. |
