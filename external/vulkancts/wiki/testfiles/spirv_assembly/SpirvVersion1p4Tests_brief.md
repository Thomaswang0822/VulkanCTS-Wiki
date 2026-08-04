# Understanding Brief: vktSpvAsmSpirvVersion1p4Tests

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation that enables `VK_KHR_spirv_1_4` accepts and correctly executes the SPIR-V 1.4 surface area — composite `OpSelect`, pointer comparison/difference instructions, `OpCopyLogical`, `OpCopyMemory` access operands, `UniformId` decoration, `NonWritable` on Function/Private variables, expanded entry-point interface listing, HLSL functionality decorations, new loop controls, `UConvert` inside `OpSpecConstantOp`, and integer wrap decorations — across 102 Amber-driven compute/graphics cases in 13 subgroups.

## Background Knowledge

### SPIR-V 1.4 entry-point interface rule

In SPIR-V 1.4, `OpEntryPoint` must list every module-scope variable the entry point statically uses, not just the variables with input/output storage class. The `entrypoint` subgroup verifies this for compute, fragment, geometry, tessellation-control, tessellation-evaluation, and vertex stages with push-constant, SSBO, UBO, and workgroup variables.

Why it matters here:
- A driver that still follows the SPIR-V 1.0/1.3 interface rule (where only Input/Output variables need to be listed) may reject valid 1.4 modules or silently mis-bind descriptors.
- The `entrypoint` cases are stage-parameterized, so failures are reported per stage/per resource kind, not as one monolithic failure.

### Pointer comparison and difference instructions

SPIR-V 1.4 promotes `OpPtrEqual`, `OpPtrNotEqual`, and `OpPtrDiff` from extensions into the core spec. They operate on pointers in the `StorageBuffer`, `Workgroup`, and (with variable pointers) cross-variable contexts. `OpPtrEqual`/`OpPtrNotEqual` return a boolean; `OpPtrDiff` returns the element count between two pointers into the same array.

Why it matters here:
- The `opptrequal`, `opptrnotequal`, and `opptrdiff` subgroups depend on variable-pointer features (`VariablePointerFeatures.variablePointersStorageBuffer` and `VariablePointerFeatures.variablePointers`). Storage-class and pointer-storage choices (Function vs Private vs SSBO vs Workgroup) are the behavioral axis, not just the comparison op.
- Null pointer comparisons are tested explicitly through dedicated cases (`null_comparisons_ssbo_*`, `null_comparisons_wg_*`).

### `OpSelect` extension to composites

SPIR-V 1.0 only allowed `OpSelect` on scalar or vector pointers (the selector being a scalar boolean or a vector of booleans for component-wise selection). SPIR-V 1.4 extends `OpSelect` to composites: arrays, structs, nested composites, and pointers. The `opselect` subgroup mixes regression cases (scalar/vector selection, present since SPIR-V 1.0) with new 1.4 cases (array, struct, nested array/struct, SSBO/workgroup pointers).

Why it matters here:
- The `scalar_select` Amber script (the representative walkthrough) is a regression case verifying SPIR-V 1.0 behavior under SPIR-V 1.4 build options. The composite cases are the actual 1.4 surface, but the regression case is a useful smallest-shader reference for the dispatch/probe mechanism.
- Workgroup-pointer `OpSelect` cases additionally require `VK_KHR_workgroup_memory_explicit_layout`.

### `OpCopyLogical` and `OpCopyMemory` access operands

`OpCopyLogical` produces a value with a different logical memory layout — for example, copying a UBO-layout struct into an SSBO-layout struct with the same member types but different offsets, array strides, or matrix strides. `OpCopyMemory` in SPIR-V 1.4 gains the `Aligned` access operand form, allowing per-source and per-target alignment hints. The `opcopylogical` and `opcopymemory` subgroups cover these.

Why it matters here:
- `OpCopyLogical` cases mix UBO-to-SSBO and SSBO-to-UBO layout conversions with same-storage-class layout differences (different matrix strides, nested-array inner/outer strides, two IDs for the same array/struct).
- `OpCopyMemory` cases vary the `Aligned` operands on source and target; the `different_alignments` case shows four `OpCopyMemory` calls with `Aligned 16 Aligned 4`.

### Decorations folded in from extensions

SPIR-V 1.4 folds several extensions into core without requiring the original extension declarations:
- `SPV_KHR_no_integer_wrap_decoration` → `NoSignedWrap` and `NoUnsignedWrap` decorations (the `wrap` subgroup).
- `SPV_GOOGLE_hlsl_functionality1` → `CounterBuffer` decoration, `OpDecorateString`, `OpMemberDecorateString` (the `hlsl_functionality1` subgroup).
- `SPV_KHR_workgroup_memory_explicit_layout` is *not* folded in; it remains a required extension for the workgroup-pointer `OpSelect` cases.
- `UniformId` decoration and the `NonWritable` relaxation to Function/Private variables are SPIR-V 1.4 features.

### `UConvert` in `OpSpecConstantOp`

SPIR-V 1.4 permits `UConvert` inside `OpSpecConstantOp`, enabling specialization-constant-time unsigned integer conversions between 16-bit, 32-bit, and 64-bit widths. The `uconvert` subgroup exercises extend, truncate, and zero-extend cases, gated by `Features.shaderInt16`, `VK_KHR_16bit_storage` + `Storage16BitFeatures.storageBuffer16BitAccess`, and `Features.shaderInt64`.

### Loop control hints

SPIR-V 1.4 adds the loop controls `MinIterations`, `MaxIterations`, `IterationMultiple`, `PeelCount`, and `PartialCount`. They are hints, not requirements — a conformant implementation may ignore them. The `loop_control` subgroup verifies the SPIR-V is accepted and the loop still produces the expected result.

## One Concrete Example

The representative walkthrough is `spirv_assembly.instruction.spirv1p4.opselect.scalar_select`. The Amber script (`opselect/scalar_select.amber`) embeds SPIR-V assembly directly:

- A compute shader with `LocalSize 1 1 1`, dispatched as `compute 1 1 2` (two invocations along Z).
- Two SSBOs: `input_buffer` at descriptor set 0 binding 0 (4-byte `int` runtime array, `ArrayStride 4`) and `output_buffer` at descriptor set 0 binding 1.
- BuiltIn `gl_GlobalInvocationID` provides the dispatch index; the shader uses the Z component (`OpAccessChain ... %uint_2`).
- Body: load `input[gl_GlobalInvocationID.z]`; if equal to `0`, select `int_1` (`1`), otherwise select `int_2` (`2`); store to `output[gl_GlobalInvocationID.z]`.
- Host data: `input = {0, 1}`; expected `output = {1, 2}`.

This is the SPIR-V 1.0 scalar `OpSelect` form running under SPIR-V 1.4 build options. It is the smallest reference for the Amber-driven dispatch/probe pattern used by every other case in the file.

## End-to-End Test Flow

```text
[host] CTS creates the spirv1p4 test group with 13 subgroup CaseGroup objects
[host] addTestsForAmberFiles() loads each <subgroup>/<basename>.amber script
[host] each case adds the VK_KHR_spirv_1_4 requirement plus subgroup-specific feature requirements
[host] each case sets SpirVAsmBuildOptions to (Vulkan 1.1, SPIR-V 1.4, supports_VK_KHR_spirv_1_4)
[host] Amber runner compiles the embedded SPIR-V assembly, creates the pipeline, allocates the [test] resources
[host] Amber runner dispatches/draws per the [test] block (mostly compute 1x1xN)
[device] shader executes the embedded SPIR-V; reads input SSBO/UBO/workgroup/push-constant data; writes output SSBO
[host] Amber runner probes the output SSBO at the byte offsets stated in [test]
[host] each probe assertion must match for the case to pass
```

The registration and Amber execution flow is uniform across all 13 subgroups; the embedded SPIR-V, `[test]` commands, and per-case feature gates differ.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Amber scripts under `data/vulkan/amber/spirv_assembly/instruction/spirv1p4/<subgroup>/<basename>.amber` are the only program artifacts. Each script embeds the SPIR-V assembly directly between `[compute shader spirv]` (or fragment/geometry/tessellation/vertex equivalents) and `[test]`. No GLSL/HLSL source is generated by CTS for this file; the SPIR-V is hand-authored test data.
- All cases target SPIR-V 1.4 through `SpirVAsmBuildOptions(VK_MAKE_API_VERSION(0, 1, 1, 0), vk::SPIRV_VERSION_1_4)` and `asm_options.supports_VK_KHR_spirv_1_4 = true`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input SSBO (`binding 0`) | yes, through Amber `[test]` `ssbo` and `subdata` commands | yes | yes (read by shader) | no | Drives shader control flow |
| Output SSBO (`binding 1`) | yes, through Amber `ssbo` command (sometimes pre-initialized to sentinel like `-1`) | yes | yes (written by shader) | yes (through `probe`) | The pass/fail observable |
| Input UBO (`binding 0`, in `opcopylogical`/`opptrequal`/etc.) | yes, through `uniform ubo` commands | yes | yes (read by shader) | no | Provides sized uniform data with explicit offsets |
| Counter SSBOs (in `hlsl_functionality1/counter_buffer`) | yes, through `ssbo` commands at bindings 1 and 3 | yes | yes (atomic add by shader) | yes | Tests `CounterBuffer` decoration |
| Push constants (in `entrypoint/*_pc_entry_point`) | yes, through Amber push-constant commands | yes | yes (read by shader) | no | Tests the entry-point interface rule for push constants |
| Workgroup variables (in `opselect/wg_*` and `entrypoint/comp_workgroup_entry_point`) | declared in shader; no host binding | n/a (shader-local) | yes (read/write by shader) | no | Tests workgroup storage and `VK_KHR_workgroup_memory_explicit_layout` |

## What Is Checked

- All cases use Amber `probe ssbo int|uint 0:<binding> <offset> == <values>...` assertions against the output SSBO. Some cases probe multiple offsets to cover all members of a struct or array.
- The `opptrequal`/`opptrnotequal` cases typically encode boolean comparison results as `0`/`1` integers in the output SSBO, so the probe checks the encoded booleans.
- The `opptrdiff` cases encode element-count differences as integers.
- The `uniformid` cases probe that all invocations in a workgroup (or subgroup) consumed the same uniform-loaded value, even when only one invocation actually performed the load.
- The `entrypoint` cases verify that the entry-point interface listing is accepted; the output value is a simple copy of the input, so the pass condition reduces to "the descriptor was bound and the variable was reachable".
- The `loop_control` cases verify that the loop body executes the expected number of times and produces the expected copied array.
- The `wrap` cases verify that `OpIAdd` with `NoSignedWrap`/`NoUnsignedWrap` produces the wrapped result for the test input (which does not actually overflow).

## Behavior Parameter Identification

> **Behavior parameter:** test family (the 13 registered subgroups under `spirv_assembly.instruction.spirv1p4`)
>
> **Candidate values:** `opcopylogical`, `opptrdiff`, `opptrequal`, `opptrnotequal`, `opcopymemory`, `uniformid`, `nonwritable`, `entrypoint`, `hlsl_functionality1`, `loop_control`, `opselect`, `uconvert`, `wrap`

A secondary axis exists for some test families: shader stage for `entrypoint` (`comp`, `frag`, `geom`, `tess_con`, `tess_eval`, `vert`) and variable-pointer feature level for the pointer families (`Varptr_ssbo`, `Varptr_full`, `Varptr_full_explicitLayout`). These secondary axes are documented under `## Parameter Dimensions and Observed Values` in the final page; the primary axis remains the test family.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `opcopylogical` | SPIR-V `OpCopyLogical` layout conversion (UBO↔SSBO offsets, matrix/array strides, nested-array strides) is computed incorrectly or rejected by the shader compiler. |
| `opptrdiff` | `OpPtrDiff` element-count computation is wrong, or variable pointers in SSBO/Workgroup storage are not honored. |
| `opptrequal` | `OpPtrEqual` returns the wrong boolean, or null-pointer / cross-variable comparisons are mishandled. |
| `opptrnotequal` | `OpPtrNotEqual` returns the wrong boolean (mirror of `OpPtrEqual`); same root causes. |
| `opcopymemory` | `OpCopyMemory` with `Aligned` access operands reads or writes at the wrong offset, or the access operands are rejected. |
| `uniformid` | `OpDecorateId UniformId` does not propagate a uniform value across the workgroup/subgroup, especially under nonuniform control flow. |
| `nonwritable` | `NonWritable` on a Function or Private variable is rejected, or the variable is nonetheless mutated by the compiler. |
| `entrypoint` | The entry-point interface does not list a module-scope variable, the variable is unreachable, or the descriptor binding for the listed variable is wrong. |
| `hlsl_functionality1` | `CounterBuffer` decoration, `OpDecorateString`, or `OpMemberDecorateString` is rejected or ignored. |
| `loop_control` | A SPIR-V 1.4 loop control hint (`MinIterations`, `MaxIterations`, `IterationMultiple`, `PeelCount`, `PartialCount`) is rejected or alters the loop body's effect. |
| `opselect` | `OpSelect` on a composite type (array, struct, nested composite, SSBO/workgroup pointer) selects the wrong operand, or the SPIR-V 1.0 scalar/vector forms regress under SPIR-V 1.4. |
| `uconvert` | `UConvert` inside `OpSpecConstantOp` does not extend, truncate, or zero-extend correctly between 16/32/64-bit widths. |
| `wrap` | `NoSignedWrap` or `NoUnsignedWrap` decoration is rejected, or the decoration incorrectly changes the arithmetic result. |
| (all families) | Common infrastructure: SPIR-V 1.4 build options not applied, `VK_KHR_spirv_1_4` requirement not enforced, Amber runner failure, or descriptor/barrier setup issue. |

## Important Variations and Special Cases

- The `opselect` subgroup mixes SPIR-V 1.0 regression cases (`scalar_select`, `vector_element_select`, `ssbo_pointers_select`, `wg_pointers_select`) with SPIR-V 1.4 new cases (`array_select`, `array_stride_select`, `nested_array_select`, `nested_struct_select`, `struct_select`, `vector_select`). The 1.0 cases verify that the new build options do not regress existing behavior.
- The `entrypoint` subgroup has 19 cases: compute covers push constant, SSBO, UBO, and Workgroup; each of fragment, geometry, tessellation control, tessellation evaluation, and vertex covers push constant, SSBO, and UBO. Geometry cases require `Features.geometryShader`; tessellation cases require `Features.tessellationShader`.
- The pointer families (`opptrequal`, `opptrnotequal`, `opptrdiff`) use three variable-pointer requirement tiers: `Varptr_ssbo` (storage-buffer-only variable pointers), `Varptr_full` (adds `VariablePointerFeatures.variablePointers`), and `Varptr_full_explicitLayout` (adds `VK_KHR_workgroup_memory_explicit_layout`, used only by the `opselect/wg_*` cases).
- The `uniformid` cases assume a subgroup size ≤ 8 because the compute dispatch uses `LocalSize 8 1 1`. Devices with larger subgroups may still pass, but the test design assumes the subgroup fits inside one workgroup.
- The `uconvert` cases split across three feature tiers: `Features.shaderInt16` alone, `Features.shaderInt16` + `VK_KHR_16bit_storage` + `Storage16BitFeatures.storageBuffer16BitAccess`, and `Features.shaderInt64`.
- All tests are non-VulkanSC only — the `addTestsForAmberFiles` helper is wrapped in `#ifndef CTS_USES_VULKANSC`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `createSpirvVersion1p4Group()` | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L124-L409`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L124-L409) | Top-level group creation; defines all 13 subgroups and their case lists. |
| `addTestsForAmberFiles()` | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L75-L120`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L75-L120) | Amber test factory: adds `VK_KHR_spirv_1_4`, sets SPIR-V 1.4 build options, registers each case. |
| `CaseGroup` and `Case` structs | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L44-L73`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L44-L73) | Carrier for the per-subgroup basename list and per-case requirements. |
| Feature requirement vectors | [`vktSpvAsmSpirvVersion1p4Tests.cpp#L133-L156`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersion1p4Tests.cpp#L133-L156) | `Geom`, `Tess`, `Varptr_ssbo`, `Varptr_full`, `Varptr_full_explicitLayout`, `Int16`, `Int16_storage`, `Int64` definitions. |
| Representative Amber script | [`opselect/scalar_select.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/spirv1p4/opselect/scalar_select.amber) | Smallest representative walkthrough; embeds SPIR-V assembly for `OpSelect` on scalars. |
| OpCopyLogical UBO→SSBO Amber | [`opcopylogical/ubo_to_ssbo.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/spirv1p4/opcopylogical/ubo_to_ssbo.amber) | Demonstrates layout conversion through `OpCopyLogical`. |
| NoSignedWrap Amber | [`wrap/no_signed_wrap.amber`](../../../data/vulkan/amber/spirv_assembly/instruction/spirv1p4/wrap/no_signed_wrap.amber) | Demonstrates integer wrap decoration. |

## Questions / Risk Points for User Audit

None. The source, Amber directory, and standard mustpass list agree on 13 registered subgroups and 102 leaves; Vulkan SC excludes this dispatcher at compile time.

## Conversion Notes for Final Wiki Rewrite

- The detailed page retains the same behavior-axis conclusion and failure-cause mapping.
- The representative assembly is extracted verbatim from `opselect/scalar_select.amber` under `#### Source Code`; Batch 9 omits `#### SPIR-V` because it would duplicate the literal Amber assembly.
