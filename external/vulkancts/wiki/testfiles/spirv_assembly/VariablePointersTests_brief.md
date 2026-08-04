# Understanding Brief: vktSpvAsmVariablePointersTests

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation correctly produces, transports, and dereferences SPIR-V pointers that are only known at runtime — through `OpSelect`, `OpPhi`, `OpFunctionCall`, `OpCopyObject`, and `OpPtrAccessChain` — under both the `SPV_KHR_variable_pointers` (logical, `StorageBuffer`/`Workgroup`) and `SPV_KHR_physical_storage_buffer` (physical, `PhysicalStorageBufferEXT`) pointer models, in compute and graphics pipelines.

## Background Knowledge

### Variable pointers vs physical storage buffer pointers

SPIR-V originally only allowed pointers known at compile time ( OpAccessChain into a known descriptor binding with constant indices ). Two extensions broaden this.

`SPV_KHR_variable_pointers` introduces logical variable pointers: a pointer value can be selected at runtime between two `OpAccessChain` results that point into the same `StorageBuffer` resource, or — when the stronger `VariablePointers` capability is advertised — into two different `StorageBuffer` resources. The memory model stays `Logical`; the pointer is still an opaque handle the implementation tracks back to its originating descriptor.

`SPV_KHR_physical_storage_buffer` introduces physical storage buffer pointers: a pointer is a 64-bit device address loaded from a `StorageBuffer` struct member of type `PhysicalStorageBufferEXT`, and the memory model becomes `PhysicalStorageBuffer64EXT`. The pointer can be stored, copied, and dereferenced through `OpLoad`/`OpStore` with `Aligned` memory operands.

Why it matters here:

- The file drives both paths through one C++ string template (`addPhysicalOrVariablePointersComputeGroup` and `addComplexTypesPhysicalOrVariablePointersComputeGroup` take a `physPtrs` flag). The `physPtrs` flag swaps the `OpCapability`, `OpExtension`, `OpMemoryModel`, the pointer storage class (`StorageBuffer` vs `PhysicalStorageBufferEXT`), and how the input buffers are reached (separate descriptor bindings vs addresses loaded from one `physPtrsStruct`).
- The `VariablePointersStorageBuffer` capability is the weaker form: variable pointers must remain within a single `StorageBuffer` binding. `VariablePointers` is the stronger form: variable pointers may span two different `StorageBuffer` bindings and may also live in `Workgroup` storage. The `single_buffer`/`two_buffers` parameter explicitly exercises both capability tiers.

### The "mux" pattern shared by almost every leaf

The shared test body loads a selector `s[i]` from a third input buffer, computes `is_neg = s[i] < 0`, then produces a `sb_f32ptr` (or `f32_wrkgrp_ptr`) by selecting between two candidate pointers `muxInput1` and `muxInput2`. The selected pointer is dereferenced and the value is stored to an output slot.

Why it matters here:

- The candidate pointers differ per `bufferType`: for `single_buffer`, both candidates live in `indata_a` (offsets `2*i` and `2*i+1`); for `two_buffers`, the candidates live in `indata_a[i]` and `indata_b[i]`.
- The *selection strategy* dimension swaps the SPIR-V instruction that produces the variable pointer: `OpSelect`, `OpFunctionCall` (the call returns a pointer), `OpPhi` (the pointer is selected by control flow), `OpCopyObject` (the pointer is copied then selected), or `OpPtrAccessChain` (the pointer is produced by pointer arithmetic). Each strategy stresses a different validator rule for variable pointers.

### `OpPtrAccessChain` versus `OpAccessChain`

`OpAccessChain` walks a struct/array path with constant-style indices but always returns a pointer rooted at the same storage-class variable it was given. `OpPtrAccessChain` performs pointer arithmetic: it takes a base pointer and an integer operand `i`, returning a pointer to the `i`-th element of the array pointed to by the base. This is the only SPIR-V opcode that genuinely creates a new pointer value at runtime, and it is the spine of the `complex_types_compute` and `*_read_only_graphics` families that walk seven levels of nested structures.

## One Concrete Example

Representative case: `spirv_assembly.instruction.compute.variable_pointers.compute.reads_opselect_two_buffers`.

The compute shader dispatches `numWorkGroups = (100, 1, 1)`. Per invocation `i` it loads `s[i]`, computes `is_neg = s[i] < 0`, then performs:

```text
%inloc_a_i   = OpAccessChain %sb_f32ptr %indata_a %zero %i
%inloc_b_i   = OpAccessChain %sb_f32ptr %indata_b %zero %i
%mux_output_var_ptr = OpSelect %sb_f32ptr %is_neg %inloc_a_i %inloc_b_i
%mux_output  = OpLoad %f32 %mux_output_var_ptr Aligned 4
                          OpStore %outloc_i %mux_output Aligned 4
```

`indata_a` and `indata_b` are two separate `StorageBuffer` bindings, so this case requires the `VariablePointers` capability (not just `VariablePointersStorageBuffer`). The expected output is computed on the host with the same mux expression: `output[i] = (s[i] < 0) ? A[i] : B[i]`.

## End-to-End Test Flow

```text
[host] fill inputAFloats (200), inputBFloats (200), inputSFloats (100) with random floats
[host] force inputSFloats to contain a shuffled mix of negative and positive values
[host] compute expectedOutput[i] = (s[i] < 0) ? A[i] : B[i] for the two_buffers variant
[host] build the SPIR-V assembly string by specializing the shared template
[host] select capability: VariablePointersStorageBuffer (single_buffer) or VariablePointers (two_buffers); PhysicalStorageBufferAddressesEXT for physPtrs
[host] enable VK_KHR_variable_pointers extension and required feature flags
[host] create the four StorageBuffer bindings (a, b, s, out) with the float vectors
[host] dispatch (100, 1, 1) workgroups of size (1, 1, 1)
[device] each invocation reads s[i], selects between two StorageBuffer pointers, loads through the selected pointer, stores to out[i]
[host] read back outdata and compare against expectedOutput with the SPIR-V-as-test-runner tolerance
[host] decide pass/fail
```

The `complex_types_compute` and `*_read_only_graphics` flows replace the simple mux with a seven-level nested-struct walk, dispatch `(1, 1, 1)`, and check a single float (compute) or the red channel of an output color (graphics). The `nullptr_*` flows initialize a `Function`-class pointer to `OpConstantNull`, then either overwrite it with a valid pointer before load, or `OpSelect` between a valid pointer and null (forced to choose the valid one).

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline SPIR-V assembly string built by `tcu::StringTemplate::specialize()` from a shared C++ template. There is no GLSL or HLSL source; the SPIR-V text *is* the authored program.
- The template is parameterized by `${ExtraCapability}`, `${ExtraTypes}`, `${ExtraDecorations}`, `${ExtraGlobalScopeVars}`, `${ExtraFunctionScopeVars}`, `${ExtraSetupComputations}`, `${ResultStrategy}`, and `${VarPtrName}` slots.
- For graphics groups, fragments are bound into the standard `vktSpvAsmGraphicsShaderTestUtil` pipeline (`capability`, `extension`, `decoration`, `pre_main`, `testfun`); `createTestsForAllStages()` expands each test into vertex, tessellation, geometry, and fragment variants.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|------------------------------|---------------|--------------------------|--------------------|-----------------|
| `indata_a` (`StorageBuffer`, runtime array of `f32`) | yes | yes | read by device | no | First mux input; candidate pointer source |
| `indata_b` (`StorageBuffer`, runtime array of `f32`) | yes | yes | read by device | no | Second mux input; present only in `two_buffers` and `physPtrs` variants |
| `indata_s` (`StorageBuffer`, runtime array of `f32`) | yes | yes | read by device | no | Selector values; sign of `s[i]` chooses the pointer |
| `outdata` (`StorageBuffer`, runtime array of `f32`) | yes | yes | written by device | yes | Holds the mux result for host comparison |
| `physPtrsStruct` (`StorageBuffer` of four `PhysicalStorageBufferEXT` addresses) | yes (physPtrs only) | yes | read by device | no | Packs `a`, `b`, `s`, `out` device addresses for the physical-pointer path |
| `inputA`/`inputB`/`inputC` (`StorageBuffer` structs) | yes (complex_types_compute only) | yes | read by device | no | Nested-struct targets; `inputC` packs both `outer_struct` members for the `single_buffer` variant |
| Workgroup variables `%AW`, `%BW` | yes (workgroup_two_buffers only) | n/a (shader-local) | read/written by device | no | Exercising variable pointers in `Workgroup` storage class |

## What Is Checked

- Compute mux tests: the host compares every `outdata[i]` against `expectedOutput[i] = (s[i] < 0) ? A[i] : B[i]` (or the `single_buffer` equivalent `A[2*i]`/`A[2*i+1]`). The increment tests add `+1` to the loaded value before storing back, so the expected buffer is `1 +` the mux result.
- Complex-types tests: a single output float is compared against `selectedInput[baseOffset]` where `baseOffset` is computed by `getBaseOffsetForSingleInputBuffer()` from the same nested indices the shader uses.
- Graphics tests: the red channel of the output color is compared against `selectedInput[baseOffset]` (or `inputBuffer[baseOffset]` for the single-buffer graphics variant).
- Nullptr tests: the output is compared against a known valid input value (`78` for compute, `78/255.f` for graphics), proving the valid pointer path was taken rather than the null path.
- All comparisons are performed by the CTS SPIR-V-as-test-runner infrastructure (`SpvAsmComputeShaderCase` for compute, `createTestsForAllStages()` for graphics); the host does not implement a custom check loop.

## Behavior Parameter Identification

> **Behavior parameter:** intermediate node — the test group below each registered test family.
>
> **Candidate values:** `compute`, `complex_types_compute`, `nullptr_compute`, `graphics`, `multi_buffer_read_only_graphics`, `single_buffer_read_only_graphics`, `nullptr_graphics` (with `64b_indexing` as a non-VulkanSC mirror of the first three).

A secondary axis applies inside the mux-shaped groups:

> **Behavior parameter:** selection strategy (within `compute`, `complex_types_compute`, `multi_buffer_read_only_graphics`, `single_buffer_read_only_graphics`).
>
> **Candidate values:** `opselect`, `opfunctioncall`, `opphi`, `opcopyobject`, `opptraccesschain`.

Tertiary parameter dimensions (configuration rather than behavior): pointer type (`variable_pointers` vs `physical_pointers`), buffer type (`single_buffer` vs `two_buffers`), input selection (`first_input` vs `second_input`), index level (0–6), store storage class (`Private` vs `Function`), 64-bit indexing (`true` vs `false`).

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute` (basic mux) | Driver/validator rejects legal `OpSelect`/`OpPhi`/`OpFunctionCall` on `StorageBuffer` pointers; wrong pointer selected; mis-compilation of `OpPtrAccessChain` stride; wrong value stored through the selected pointer. |
| `complex_types_compute` | Wrong offset computed by `OpPtrAccessChain` at one of the seven indirection levels; `OpSelect` type mismatch when pointers target nested types; `OpAccessChain` into a variable pointer produces an invalid pointer. |
| `nullptr_compute` | Driver rejects `OpConstantNull` of pointer type; `OpVariable` of `Function` storage class with pointer initializer rejected; null pointer dereferenced despite being forced to the valid branch. |
| `graphics` (basic mux in graphics stages) | Vertex/tessellation/geometry/fragment shader translator rejects variable pointers; missing `vertexPipelineStoresAndAtomics`/`fragmentStoresAndAtomics` feature gate; pointer value not preserved across shader stages. |
| `multi_buffer_read_only_graphics` | `VariablePointers` capability not honoured in graphics pipeline; `NonWritable` decoration wrongly enforced as no variable-pointer selection; `OpCompositeInsert` into the red channel ignored. |
| `single_buffer_read_only_graphics` | `VariablePointersStorageBuffer` capability not honoured in graphics pipeline; pointer confined to single buffer rejected; `OpPtrAccessChain` on `outer_struct_ptr` mishandled. |
| `nullptr_graphics` | Same as `nullptr_compute` but in graphics stages; `OpCompositeInsert` of `result_val` into the output color mishandled. |
| (shared across all `physical_pointers` variants) | `PhysicalStorageBufferAddressesEXT` capability mishandled; 64-bit address load/store with `Aligned` operand misaligned; pointer aliasing rules broken (`AliasedPointerEXT`/`Restrict` decorations ignored). |
| (shared across all `64b_indexing` variants) | 64-bit index truncation in `OpAccessChain`/`OpPtrAccessChain`; descriptor addressing mismatch when the runtime array index is widened. |

## Important Variations and Special Cases

- The `64b_indexing` sub-group mirrors `compute`, `complex_types_compute`, and `nullptr_compute` with `spec.uses64BitIndexing = true`, exercising 64-bit indices into runtime arrays. It is wrapped in `#ifndef CTS_USES_VULKANSC` and is absent from Vulkan SC builds.
- The `workgroup_two_buffers` case appears only when `!physPtrs && !isSingleInputBuffer`, because `VariablePointersStorageBuffer` does not extend to `Workgroup` storage — only the full `VariablePointers` capability does.
- The `stores_private`/`stores_function` cases swap the storage class of a `OpVariable` that holds a variable pointer. For physical pointers the variable is decorated `AliasedPointerEXT`; for logical pointers no alias decoration is emitted.
- The `writes_*` cases invert the mux direction: the selected pointer is loaded, incremented by 1, and stored back through the same variable pointer — exercising write-through, not just read-through.
- The physical-pointer path uses one `physPtrsStruct` with four `PhysicalStorageBufferEXT` members (offsets 0, 8, 16, 24) instead of four separate descriptor bindings. The shader `OpLoad`s each address out of the struct at function entry.
- `addVariablePointersComputeCustomTests()` folds in `vktSpvAsmOpSelectDifferentStridesTests.cpp` (non-VulkanSC only); that file owns its own implementation and is out of scope for this page beyond noting the fold-in.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Compute mux template (variable/physical) | [vktSpvAsmVariablePointersTests.cpp#L171-L641](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L171-L641) | Owns the shared SPIR-V string template and the `single_buffer`/`two_buffers` mux expansion. |
| Complex-types compute group | [vktSpvAsmVariablePointersTests.cpp#L643-L1255](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L643-L1255) | Seven-level nested-struct indirection via `OpSelect`/`OpFunctionCall`/`OpPhi`/`OpCopyObject`/`OpPtrAccessChain`. |
| Compute nullptr group | [vktSpvAsmVariablePointersTests.cpp#L1257-L1386](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1257-L1386) | `OpConstantNull` of pointer type and `OpVariable` of `Function`-class pointer. |
| Graphics basic mux group | [vktSpvAsmVariablePointersTests.cpp#L1408-L1807](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1408-L1807) | Same mux pattern, expanded across graphics stages via `createTestsForAllStages()`. |
| Two-input-buffer read-only graphics group | [vktSpvAsmVariablePointersTests.cpp#L1827-L2228](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1827-L2228) | `VariablePointers` capability in graphics with `NonWritable` inputs; result written to the red channel. |
| Single-input-buffer read-only graphics group | [vktSpvAsmVariablePointersTests.cpp#L2230-L2641](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2230-L2641) | `VariablePointersStorageBuffer` capability confined to one buffer in graphics. |
| Graphics nullptr group | [vktSpvAsmVariablePointersTests.cpp#L2643-L2743](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2643-L2743) | Nullptr usage with variable pointers in graphics pipeline. |
| Group creation / registration entry points | [vktSpvAsmVariablePointersTests.cpp#L2746-L2817](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2746-L2817) | `createVariablePointersComputeGroup`, `createPhysicalPointersComputeGroup`, `createVariablePointersGraphicsGroup` registration roots. |
| Expected color computation | [vktSpvAsmVariablePointersTests.cpp#L1809-L1825](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1809-L1825) | `getExpectedOutputColor()` packs the chosen float into the red channel for graphics comparisons. |
| Common SPIR-V types helper | [vktSpvAsmComputeShaderTestUtil.cpp#L82-L100](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L82-L100) | `getComputeAsmCommonTypes()` provides `%bool`, `%void`, `%f32`, `%u32`, `%f32arr`, etc. |

## Questions / Risk Points for User Audit

- Is the choice of the intermediate node (`compute`, `complex_types_compute`, etc.) as the primary behavioral axis correct, or should the selection strategy (`opselect`/`opphi`/...) be primary?
- The page covers three registered test families (`compute.variable_pointers`, `compute.physical_pointers`, `graphics.variable_pointers`) in one file. Is the structural reason for grouping them — "shared C++ template and shared mux logic" — clear enough?
- The `physical_pointers` family has no `nullptr_*` or `workgroup_*` intermediate node. Is it clear that this is a deliberate scope decision (physical pointers have no nullptr equivalent and `Workgroup` is logical-only)?
- The `64b_indexing` sub-group is a non-VulkanSC mirror. Should it have its own subsection in `## Behavior Parameters`, or remain a parameter dimension note?

## Conversion Notes for Final Wiki Rewrite

- Distil the variable-vs-physical and `VariablePointers` vs `VariablePointersStorageBuffer` concept explanations into the final `## Background Knowledge` list; drop the long tutorial prose.
- Promote the "mux" concrete example to `### Representative Shader Walkthrough 1` using `reads_opselect_two_buffers` as the representative case. Extract the SPIR-V assembly text from the C++ string template (not reconstructed GLSL), per the `TEMP-SPIRV-ASSEMBLY` deviation. Run `shader-disassembler` only as a `spirv-as` → `spirv-val` → `spirv-dis` validation gate; do not publish its output. Omit the `#### SPIR-V` subsection.
- Copy the `### Failure Cause Mapping` table directly into the final page's `### Failure Cause Mapping`. Write `### Cause Analysis` fresh, grouping causes by mechanism (selection-strategy failures, addressing failures, nullptr failures, physical-pointer aliasing, 64-bit indexing).
- Move the source-mapping table into the final `## Source Reference Appendix`.
- The `parameter dimensions` table from the old page is mostly accurate; rewrite it as `## Parameter Dimensions and Observed Values` with a `Meaning in this test` column added.
- Keep the registration tree showing all three test families (compute.variable_pointers, compute.physical_pointers, graphics.variable_pointers) since they are all owned by this one file.
