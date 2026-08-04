# Understanding Brief: `spirv_assembly` VariableInitTests

## One-Sentence Test Purpose

This test family checks that Vulkan implementations honor SPIR-V `OpVariable` initializer operands for `Private` variables and vertex-stage `Output` variables, then make the initialized value observable through a storage buffer.

## Background Knowledge

### `OpVariable` initialization and storage classes

`OpVariable` declares a SPIR-V variable and can name an initializer. The initializer must match the variable's pointee type. This family uses an initializer that represents `1.0` in scalar, vector, matrix, array, or structure form.

`Private` storage gives an invocation its own variable. The compute and graphics-private cases load that variable and write its value into a storage buffer. `Output` variables form shader-stage interfaces. The output cases initialize a vertex output, then let the fragment shader receive and store that value.

Why it matters here:

- A pass requires the initializer to survive the storage-class-specific declaration and subsequent load or stage interface transfer.
- A value in a storage buffer gives the host a concrete result to compare with the expected sequence of `1.0f` values.

### Workgroup pointer initialization

The compute `*_from_workgroup` leaves initialize a `Private` variable with a pointer to a `Workgroup` variable. The shader loads that pointer, writes the all-ones composite to the workgroup object, then loads the selected typed value through the pointer. This uses `VariablePointers`; it tests pointer-valued initialization rather than direct data initialization.

## One Concrete Example

The representative leaf is:

```text
dEQP-VK.spirv_assembly.instruction.compute.variable_init.private.float
```

It declares `%f1` as `Private` with `%f32_1` as its initializer. Each one-invocation workgroup reads its `GlobalInvocationId.x`, loads `%f1`, and writes one `float` to that storage-buffer element. The host expects 128 floats equal to `1.0f`.

## End-to-End Test Flow

```text
[host] select a type and initialization source from testParams
[host] create an expected Float32 storage-buffer result filled with 1.0f
[host] specialize the CTS-authored SPIR-V assembly and select required extensions/features
[host] dispatch compute workgroups or create the graphics pipeline
[device] execute OpVariable initialization, loads, and stores
[device] write initialized data to a storage buffer, directly or through a vertex-to-fragment interface
[host] run the framework comparison against the expected buffer
[host] report pass only when the observed values match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The source directly specializes SPIR-V assembly templates. It does not generate GLSL or HLSL. The compute-private builder emits `OpVariable` in `Private` storage with either a typed constant or a Workgroup-pointer initializer. The output builder supplies authored vertex and fragment SPIR-V modules to `spirvAsmSources`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Expected `Float32Buffer` | yes | yes, as descriptor-set 0 binding 0 | shader writes | framework compares it | Records values produced by initialized variables. |
| `Private` variable | no, it is in SPIR-V | no descriptor | shader reads | no | Holds a directly initialized value or a Workgroup pointer. |
| `Workgroup` variable | no, it is in SPIR-V | no descriptor | compute shader writes then reads | no | Supplies the pointee for `*_from_workgroup` leaves. |
| Vertex `Output` interface variable | no, it is in SPIR-V | pipeline interface | vertex writes by initialization, fragment reads | indirectly | Carries the output-initializer value to the fragment stage. |

## What Is Checked

- Compute-private leaves use a 128-float expected buffer of `1.0f`; each workgroup writes one selected typed element.
- Graphics-private leaves run the common graphics-stage helper and expect the same all-ones storage-buffer result.
- Graphics-output leaves expect `numComponents` floats of `1.0f`; the vertex shader initializes the `Output` value and the fragment shader copies its input to the storage buffer.
- The page documents 39 observed mustpass leaves: 9 compute-private, 25 graphics-private, and 5 graphics-output leaves in both inspected default mustpass files.

## Behavior Parameter Identification

> **Behavior parameter:** behavior group
>
> **Candidate values:** `compute.private`, `graphics.private`, `graphics.output`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute.private` | Incorrect `Private` `OpVariable` initialization or load/store lowering; for `*_from_workgroup`, incorrect pointer initialization or Workgroup access. |
| `graphics.private` | Incorrect `Private` initializer handling in a generated vertex, fragment, geometry, tessellation-control, or tessellation-evaluation stage, or incorrect storage-buffer write behavior. |
| `graphics.output` | Incorrect `Output` initializer handling in the vertex stage, interface transfer to the fragment stage, or fragment storage-buffer write behavior. |

## Important Variations and Special Cases

- Direct constant initialization covers `float`, `vec4`, `matrix`, `floatarray`, and `struct`. The matrix has 8 components, the array has 8, and the structure has 16.
- Compute alone includes `float_from_workgroup`, `vec4_from_workgroup`, `floatarray_from_workgroup`, and `struct_from_workgroup`. The graphics-private and graphics-output builders skip these global-source parameters.
- The compute Workgroup-pointer leaves require `VK_KHR_variable_pointers` and `variablePointers`. The array and structure Workgroup leaves also request `VK_KHR_workgroup_memory_explicit_layout` and SPIR-V 1.4.
- All leaves request `VK_KHR_storage_buffer_storage_class`. Graphics-private requests vertex and fragment storage-buffer feature support. Graphics-output requests `fragmentStoresAndAtomics`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test matrix and composite constants | [testParams and common assembly](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L47-L111) | Defines exact leaf names, types, component counts, and the all-ones constants. |
| Compute `Private` generator | [addComputeVariableInitPrivateTest](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L113-L229) | Builds direct and Workgroup-pointer assembly, expected output, and support requests. |
| Graphics `Private` generator | [addGraphicsVariableInitPrivateTest](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L231-L317) | Builds the constant-initialized graphics stage cases. |
| Graphics `Output` assembly and runner | [addShaderCodeOutput](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L329-L600) and [addGraphicsVariableInitOutputTest](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L602-L654) | Supplies the vertex/fragment modules and the custom pipeline case. |
| Registration | [createVariableInitComputeGroup and createVariableInitGraphicsGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariableInitTests.cpp#L658-L674) | Registers the compute and graphics `variable_init` test families. |

## Questions / Risk Points for User Audit

- Does the distinction between direct data initialization and pointer-valued Workgroup initialization make the compute variants clear?
- Does the output path make clear that the storage-buffer oracle observes a vertex `Output` only after fragment-stage consumption?
- Should the final page retain one exact SPIR-V assembly walkthrough for auditability?

## Conversion Notes for Final Wiki Rewrite

- Retain the compact `OpVariable` and storage-class prerequisites, but move concrete matrix values and execution details to their dedicated sections.
- Use `compute.private`, `graphics.private`, and `graphics.output` as the behavior groups in the final page.
- Copy the failure mapping table unchanged into the final page.
- Publish one CTS-authored SPIR-V assembly walkthrough for the direct compute `float` leaf. Validate it by assembling, validating, and disassembling it during final-page verification; do not publish a duplicate disassembly subsection.
