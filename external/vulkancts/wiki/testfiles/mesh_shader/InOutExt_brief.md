# Understanding Brief: EXT mesh-shader interface variables

## One-Sentence Test Purpose

This test checks whether `VK_EXT_mesh_shader` preserves selected user-defined interface variables from task or mesh shader outputs into fragment shader inputs across types, widths, dimensions, ownership, and interpolation qualifiers.

## Background Knowledge

### Mesh outputs form the next-stage fragment inputs

A mesh shader writes user-defined output variables with explicit locations. The fragment shader declares matching inputs, and rasterization supplies vertex-owned values by interpolation while primitive-owned values remain per primitive. The interface contract includes type, location occupancy, interpolation decoration, and the `perprimitiveEXT` qualifier.

Why it matters here:
- The test deliberately mixes vertex and primitive ownership in one generated interface.
- A `flat` integer or primitive value must arrive as the corresponding discrete value, while a normally interpolated floating-point vertex value may vary inside the triangle.

### Location accounting and feature-qualified types

A scalar or vector consumes one location except a 64-bit vector with three or four components, which consumes two. The generated list is cut before it exceeds 16 locations. The EXT mesh properties expose `maxMeshOutputComponents`; the implementation also reserves room for four glslang-generated built-ins.

## One Concrete Example

For a representative `mesh_only` case, the host provides per-vertex and per-primitive values in two storage buffers. The mesh shader writes four vertices and two triangles, assigns `gl_MeshPrimitivesEXT[].gl_PrimitiveID`, and copies each selected value to a location-decorated output. The fragment shader reads the matching inputs and emits blue only when all checks succeed.

A task-enabled case inserts a task shader between the host buffers and mesh shader. It copies the same values into `taskPayloadSharedEXT` and calls `EmitMeshTasksEXT(1, 1, 1)`; the mesh shader then reads the payload instead of the storage buffers.

## End-to-End Test Flow

```text
[host] select a feature group, shuffle the eligible interface-variable list, and retain the prefix that fits 16 locations
[host] create host-visible storage buffers for per-vertex and per-primitive source data
[host] generate fragment and mesh GLSL; generate task GLSL for task_mesh cases
[host] create the graphics pipeline and bind both storage buffers
[host] submit one mesh-task draw with a 1 x 1 x 1 count
[device] task shader, when present, copies source values into taskPayloadSharedEXT and launches the mesh shader
[device] mesh shader emits four vertices, two triangles, primitive IDs, and the selected interface outputs
[device] fragment shader checks every received value and writes blue for success or black for failure
[host] transition the color image, copy it to a host-visible verification buffer, invalidate the allocation, and compare with a blue reference image
[host] return pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The implementation generates GLSL for `frag` and `mesh`, plus `task` when `task_mesh` is selected. `getMinMeshEXTBuildOptions` requests SPIR-V 1.4.
- `IfaceVar::getName`, `getGLSLType`, `getLocationDecl`, `getAssignmentStatement`, and `getCheckStatement` derive declarations, data movement, and validation from the same variable descriptor.
- The permutation is deterministic: a `deRandom` instance seeded with `1636723398u` shuffles each eligible list, repeats the process for 40 permutations, and uses the same shuffled vector for `mesh_only` and `task_mesh`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Per-vertex storage buffer, set 0 binding 0 | yes | yes | read by task or mesh | no | supplies four source values for vertex-owned variables |
| Per-primitive storage buffer, set 0 binding 1 | yes | yes | read by task or mesh | no | supplies two source values for primitive-owned variables |
| `taskPayloadSharedEXT` payload | no, shader-local | yes, between task and mesh | written by task and read by mesh | no | tests the task-to-mesh transport path |
| 8 x 8 color image | yes | yes | written by fragment output | copied | records whether all interface checks passed |
| Host-visible verification buffer | yes | yes | written by image-to-buffer copy | yes | supplies pixels to the host comparison |

The source buffers use plain 32-bit `float` or `int` members even when the interface variable is 16 or 64 bits. Generated shader assignments convert to the selected GLSL type.

## What Is Checked

- The reference image is an 8 x 8 `VK_FORMAT_R8G8B8A8_UNORM` image cleared to `(0, 0, 1, 1)`.
- The fragment shader combines one boolean per selected variable. Vertex-owned values pass when the received value lies between the component-wise minimum and maximum of the four source values. This accepts valid interpolation. Primitive-owned values pass only when `gl_PrimitiveID` is 0 or 1 and the input equals the corresponding source entry.
- A black pixel means at least one interface value failed its generated check. `tcu::floatThresholdCompare` compares the copied image with the blue reference using a threshold of `0.005` per component.

## Behavior Parameter Identification

> **Behavior parameter:** feature group
>
> **Candidate values:** `32_bits_only`, `with_i64`, `with_f64`, `all_but_16_bits`, `with_i16`, `with_f16`, `all_types`

The feature group is the primary behavioral axis because it changes which interface types can enter the generated shader. `mesh_only` versus `task_mesh` is an execution-path dimension shared by every group.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `32_bits_only` | Basic 32-bit float/int interface declaration, location matching, interpolation, mesh-to-fragment transfer, or generated check failure |
| `with_i64` | 64-bit integer interface support, conversion, location use, or transfer failure in addition to the 32-bit baseline |
| `with_f64` | 64-bit floating-point interface support, conversion, interpolation restriction, location use, or transfer failure |
| `all_but_16_bits` | Combined 64-bit integer and floating-point interface behavior or location accounting failure |
| `with_i16` | 16-bit integer interface support, storage feature, conversion, or transfer failure |
| `with_f16` | 16-bit floating-point interface support, storage feature, conversion, or transfer failure |
| `all_types` | Combined 16-bit and 64-bit type coverage, feature interaction, location accounting, or interface transfer failure |

## Important Variations and Special Cases

- Integer variables are always `flat`; primitive-owned variables are always `flat`; 64-bit floating-point variables are not normally interpolated. The constructor assertions and registration filters remove these invalid combinations.
- The source comment says 8-bit interface variables are unavailable. The width dimension therefore contains 64, 32, and 16 bits only.
- `all_but_16_bits` enables both 64-bit flags but omits 16-bit flags. `all_types` enables all four flags.
- The generated vector is trimmed to the usable location count rather than generating every possible cross-product. A 64-bit three- or four-component variable consumes two locations.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Variable dimensions and legal combinations | [IfaceVar and enums](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L76-L291) | Defines owner, data type, width, dimension, interpolation, naming, location size, declarations, assignments, and checks |
| Feature-group and permutation registration | [createMeshShaderInOutTestsEXT](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L1597-L1724) | Defines the seven groups, 40 permutations, and `mesh_only`/`task_mesh` leaves |
| Support gates | [InterfaceVariablesCase::checkSupport](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L590-L630) | Shows extension, shader feature, numeric feature, 16-bit storage, and output-component requirements |
| Generated shaders | [InterfaceVariablesCase::initPrograms](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L632-L924) | Shows bindings, interface declarations, mesh outputs, task payload, and fragment checks |
| Runtime and reference checking | [InterfaceVariablesInstance::iterate](../../../modules/vulkan/mesh_shader/vktMeshShaderInOutTestsEXT.cpp#L986-L1593) | Shows resources, draw, barriers, copyback, reference image, and comparison |
| Shared EXT helpers | [mesh shader utility helpers](../../../modules/vulkan/mesh_shader/vktMeshShaderUtil.cpp#L126-L148) | Defines extension/feature checks and SPIR-V 1.4 build options |
| Shader interface rules | [Vulkan Shader Input and Output Interfaces](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-iointerfaces) | Defines matching and interface semantics |
| Interpolation rules | [Vulkan Interpolation Decorations](../../../../vulkan-docs/src/chapters/shaders.adoc#shaders-interpolation-decorations) | Defines interpolation behavior and qualifiers |
| EXT mesh output limits | [EXT mesh shader properties](../../../../vulkan-docs/src/chapters/limits.adoc#limits-maxMeshOutputComponents) | Defines `maxMeshOutputComponents` and related limits |
| Mesh output locations | [Mesh shader output interface](../../../../vulkan-docs/src/chapters/VK_NV_mesh_shader/mesh.adoc#mesh-output) | Describes location accounting for mesh outputs |

## Questions / Risk Points for User Audit

- Does the feature-group axis clearly explain why the seven registered groups are not seven different algorithms?
- Is the distinction between interpolation acceptance for vertex-owned values and exact primitive matching clear?
- Is the task payload described as shader-local transport rather than a host-created resource?
- Does the 16-location pruning rule make the pseudorandom coverage boundary clear?

## Conversion Notes for Final Wiki Rewrite

Use the feature group as the primary behavior axis and carry the mapping table directly into `## Failure Meaning`. Distill the background into interface matching, interpolation, and mesh-output location concepts. Use one representative walkthrough for the generated fragment check plus mesh output path. Keep the full 560-case vk-default coverage as a compact exact count and list the path grammar rather than enumerating all leaves.