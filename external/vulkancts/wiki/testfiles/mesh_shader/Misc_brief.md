# Understanding Brief: NV mesh-shader miscellaneous and interface-variable tests

## One-Sentence Test Purpose

This source checks whether an implementation correctly executes a broad set of `VK_NV_mesh_shader` behaviors and preserves generated user-defined values across task, mesh, and fragment shader interfaces.

## Background Knowledge

### NV task and mesh workgroups

A task shader is optional. When present, each task workgroup writes `gl_TaskCountNV` to create zero or more mesh workgroups and may pass a task payload to them. A mesh workgroup writes the output primitive count, vertex data, primitive indices, and per-vertex or per-primitive attributes consumed by later stages.

Why it matters here:
- `misc` alternates between mesh-only pipelines and task-plus-mesh pipelines.
- Several cases turn shader-observed conditions into visible output by emitting primitives only after a task payload, barrier, push constant, or output-limit condition succeeds.

### User-defined interface matching and locations

Consecutive shader stages match user-defined inputs and outputs by interface type and location. Mesh outputs may be per-vertex or per-primitive. Wide 64-bit vectors can consume two locations, and flat interpolation is required for integer and per-primitive values used here.

Why it matters here:
- `in_out` builds mixed lists across ownership, scalar type, bit width, vector width, and interpolation.
- The fragment shader checks every selected variable; one bad value turns the rendered result black instead of blue.

## One Concrete Example

`dEQP-VK.mesh_shader.nv.misc.complex_task_data` dispatches two task workgroups. Each writes a nested task payload containing scalar, array, structure, vector, and row-identification fields and emits two mesh workgroups. The mesh shader validates those fields before emitting its quadrant; the host expects four colored quadrants. Missing or corrupted task data therefore removes geometry or changes the image.

## End-to-End Test Flow

```text
1. misc rendering path
[host] select one registered leaf and its fixed task count, mesh count, output extent, and special parameters
[host] generate the task/mesh/fragment GLSL required by that leaf
[host] create an RGBA8 color attachment and host-visible readback buffer; special leaves add push constants, descriptors, or classic-pipeline buffers
[host] record vkCmdDrawMeshTasksNV, then copy the attachment to the readback buffer
[device] run the selected task/mesh workgroups and rasterize the emitted points, lines, or triangles
[host] compare the image with the leaf-specific reference, normally with a 0.005 per-channel threshold

2. in_out path
[host] deterministically shuffle the legal interface-variable candidates, truncate the list to at most 16 locations, and choose mesh_only or task_mesh
[host] initialize per-vertex and per-primitive storage buffers with known values
[device] optionally copy those values into task payload memory, copy them to generated mesh outputs, and consume them as fragment inputs
[device] render blue only when every generated value check succeeds; otherwise render black
[host] copy back the 8x8 attachment and compare it with a solid-blue reference
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Every case emits GLSL into `vk::SourceCollections`; CTS compiles those sources to SPIR-V through its normal shader build path.
- `misc` has separate source builders for primitive emission, large workgroup counts, zero primitives, barriers, custom attributes, push constants, limit-oriented output patterns, and mixed classic/mesh pipelines.
- `in_out` generates explicit-arithmetic-type declarations and matching mesh outputs / fragment inputs from a pseudorandom but fixed-seed variable permutation. The test source does not contain generated SPIR-V, and documentation must not hand-edit disassembly.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| RGBA8 color attachment | yes | yes | written | indirectly, through a transfer buffer | Carries the observable pass/fail image for both roots. |
| Verification buffer | yes | transfer destination | written by copy | yes | Supplies the host-side image comparison. |
| `in_out` per-vertex storage buffer | yes | descriptor binding 0 | read by task/mesh and fragment shaders | no | Holds known per-vertex source and comparison values. |
| `in_out` per-primitive storage buffer | yes | descriptor binding 1 | read by task/mesh and fragment shaders | no | Holds known per-primitive source and comparison values. |
| Task payload (`taskNV`) | no | no | written by task, read by mesh | no | Carries generated data between task and mesh workgroups in task-enabled cases. |
| Workgroup `shared` variables | no | no | read and written inside one workgroup | no | Provide the state used by barrier and extra-write cases. |
| Mixed-pipeline vertex/index buffers | yes | vertex/index or storage binding | read | no | Let classic and mesh pipelines draw alternating quadrants from common position data. |
| Push constants | yes | pipeline layout range | read | no | Carry case-specific color/data and mixed-pipeline vertex offsets. |

## What Is Checked

- Most `misc` leaves compare a copied RGBA8 image against a generated reference with a 0.005 threshold. The reference encodes exact primitive coverage, quadrant colors, solid colors, or an unchanged clear image.
- Memory-barrier leaves accept either a solid blue or solid black image because the loop iteration parity is intentionally nondeterministic; any mixed or otherwise different image fails.
- `mixed_pipelines` alternates classic indexed draws and NV mesh draws in one render pass and requires four exact colored quadrants.
- `in_out` checks each selected fragment input against the same storage-buffer source data. Per-vertex interpolated values must remain within the component-wise source range; flat and per-primitive values must equal the expected source entry. All pixels must be blue.
- Mustpass coverage contains 33 executable `misc` leaves and 560 `in_out` leaves: seven feature groups × 40 deterministic permutations × two pipeline shapes.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `misc`, `in_out`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `misc` | Incorrect NV task/mesh dispatch, payload transport, primitive emission, workgroup synchronization, push-constant/attribute access, output-limit handling, pipeline switching, rasterization, transfer/readback, or reference comparison for the failing leaf. |
| `in_out` | Incorrect generated interface declaration or location handling, task-payload transport, type conversion, per-vertex interpolation, flat/per-primitive delivery, feature handling, descriptor-backed source reads, rasterization, transfer/readback, or fragment-side comparison. |

## Important Variations and Special Cases

- Every executable leaf requires `VK_NV_mesh_shader` and the NV mesh-shader feature; leaves with a task stage also require the NV task-shader feature.
- `custom_attributes` additionally requires `vertexPipelineStoresAndAtomics` because the tested vertex-pipeline stages access storage buffers.
- The maximize cases compare their requested local size, vertex count, and primitive count against NV mesh-shader properties before execution.
- `in_out` gates `shaderInt64`, `shaderFloat64`, `shaderInt16`, `shaderFloat16`, and `storageInputOutput16` according to the feature-group name. It also requires enough fragment input components for 16 tested locations plus glslang-generated built-ins.
- Integer variables, per-primitive variables, and interpolated 64-bit floats are never generated with normal interpolation. A 64-bit three- or four-component vector consumes two locations.
- The source fixes the random seed at `1636723398`, generates 40 permutations for each feature group, and truncates each shuffled list to the 16-location budget.
- `count_reads` is inside `if (false)` and is absent from registration and vk-default mustpass coverage.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shared support and image-comparison path | [common case and instance](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L69-L404) | Defines NV support, draw setup, copyback, and the default threshold comparison. |
| `misc` implementations | [case implementations](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L406-L2916) | Contains the generated GLSL and references for the main miscellaneous behaviors. |
| Interface-variable model | [`IfaceVar` and support checks](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L2920-L3436) | Defines ownership, types, location consumption, checks, and feature gates. |
| `in_out` shader generation and runtime | [interface shader/runtime path](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L3438-L4373) | Generates matching interfaces and validates the rendered result. |
| Mixed classic/mesh path | [`initMixedPipelinesPrograms` and `testMixedPipelines`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4380-L4701) | Covers pipeline switching and its exact reference image. |
| Both registration roots | [`createMeshShaderMiscTests` and `createMeshShaderInOutTests`](../../../modules/vulkan/mesh_shader/vktMeshShaderMiscTests.cpp#L4808-L5232) | Registers the 33 direct `misc` leaves and the 560 generated `in_out` leaves. |
| NV support helper | [`checkTaskMeshShaderSupportNV`](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L111-L124) | Requires the extension and requested task/mesh feature bits. |
| vk-default mustpass slice | [mesh-shader mustpass](../../../mustpass/main/vk-default/mesh-shader.txt#L27356-L27948) | Enumerates all covered `in_out` and `misc` executable cases. |
| NV mesh execution model | [Vulkan specification chapter](../../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc) | Defines task-generated mesh workgroups and mesh outputs. |
| Shader interface rules | [Vulkan specification chapter](../../../../../vulkan-docs/src/chapters/interfaces.adoc#L55-L292) | Defines interface matching and location allocation. |
| Shader workgroups and barriers | [Vulkan specification chapter](../../../../../vulkan-docs/src/chapters/shaders.adoc#L2389-L2480) | Defines task/mesh workgroups, shared data, and control barriers. |

## Questions / Risk Points for User Audit

- Is the split between the broad direct-leaf `misc` root and generated three-level `in_out` root clear?
- Does the resource table distinguish host buffers from task payload and workgroup shared memory?
- Is it clear that a black `in_out` image is a device-side aggregate failure signal rather than a direct report of which variable failed?
- Are the accepted dual outcomes of the memory-barrier leaves described without implying that either loop parity is required?

No unresolved semantic risk point remains after source, specification, registration, shader-generation, runtime, and mustpass inspection.

## Conversion Notes for Final Wiki Rewrite

- Use `complex_task_data` as the representative shader walkthrough because it exposes the task-to-mesh payload mechanism that many readers need to understand.
- Explain `in_out` generation and checking in prose and tables; a single exact permutation expands to a large generated interface and adds less value than the parameter/resource explanation.
- Keep the complete direct-child registration tree, exact 33/560 mustpass counts, feature gates, and disabled `count_reads` pruning.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
