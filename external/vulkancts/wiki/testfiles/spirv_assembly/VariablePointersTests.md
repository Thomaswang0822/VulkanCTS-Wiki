## Overview

**Core question:** when a SPIR-V pointer is only known at runtime, does the implementation correctly produce, transport, and dereference it through `OpSelect`, `OpPhi`, `OpFunctionCall`, `OpCopyObject`, and `OpPtrAccessChain`, under both the logical `SPV_KHR_variable_pointers` and the physical `SPV_KHR_physical_storage_buffer` pointer models?

- Covers the implementation file [vktSpvAsmVariablePointersTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp), which owns three registered test families: `spirv_assembly.instruction.compute.variable_pointers`, `spirv_assembly.instruction.compute.physical_pointers`, and `spirv_assembly.instruction.graphics.variable_pointers`.
- The three families share one C++ string template and one "mux" pattern: a selector value picks one of two candidate pointers, the selected pointer is dereferenced, and the loaded value is stored to an output slot.
- The file swaps the SPIR-V capability (`VariablePointers`/`VariablePointersStorageBuffer`/`PhysicalStorageBufferAddressesEXT`), the memory model (`Logical`/`PhysicalStorageBuffer64EXT`), and the pointer storage class (`StorageBuffer`/`PhysicalStorageBufferEXT`) using template parameters.
- The page explains what each registered test family and selection-strategy leaf exercises, how the host validates results, and what a failure points to.

## Background Knowledge

- **`VariablePointersStorageBuffer` vs `VariablePointers` capability.** The weaker `VariablePointersStorageBuffer` capability allows a runtime pointer to be selected between two `OpAccessChain` results that point into the *same* `StorageBuffer` binding. The stronger `VariablePointers` capability lifts that restriction: the candidate pointers may live in two different `StorageBuffer` bindings, and `Workgroup`-class variable pointers are also legal. The `single_buffer` / `two_buffers` parameter explicitly exercises both tiers.
- **`SPV_KHR_physical_storage_buffer`.** Physical storage buffer pointers are 64-bit device addresses carried in a `StorageBuffer` struct member of type `OpTypePointer PhysicalStorageBufferEXT <T>`. The memory model is `PhysicalStorageBuffer64EXT`. The shader `OpLoad`s an address out of the struct and dereferences it with `OpLoad`/`OpStore` carrying the `Aligned` memory operand. In this template, `Restrict` decorates the selector function's pointer parameters; the physical `stores_*` leaves additionally decorate their `Private` or `Function` pointer variable with `AliasedPointerEXT`.
- **`OpSelect` on pointer type.** Unlike `OpAccessChain`, which derives a pointer by traversing a typed struct/array path, `OpSelect` between two pointer values produces a runtime-selected pointer value. SPIR-V validators must accept this only when the appropriate variable-pointer capability is declared; the test file enumerates several equivalent ways to produce such a value (`OpSelect`, `OpPhi`, `OpFunctionCall` returning a pointer, `OpCopyObject` followed by `OpSelect`, `OpPtrAccessChain`).
- **`OpPtrAccessChain`.** This op performs pointer arithmetic: given a base pointer to an array element and an integer `i`, it returns a pointer to the `i`-th element. It is the pointer-arithmetic operation in these tests and is the spine of the `complex_types_compute` and `*_read_only_graphics` families; `OpSelect`, `OpPhi`, function returns, and `OpCopyObject` can also produce runtime-selected or transported pointer values.
- **Graphics-stage stores.** Writing through a variable pointer into a `StorageBuffer` from a vertex, tessellation, geometry, or fragment shader requires `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`. The graphics groups request both features; the read-only graphics groups use `NonWritable` decorations instead.

## Registration Hierarchy

The file owns three registered test families under three different parent paths. The `physical_pointers` family has no `nullptr_*` or `workgroup_*` intermediate node: physical pointers have no nullptr equivalent, and `Workgroup` storage is logical-only.

```text
spirv_assembly.instruction.compute.variable_pointers
├── compute
├── complex_types_compute
├── nullptr_compute
└── 64b_indexing (non-VulkanSC only)

spirv_assembly.instruction.compute.physical_pointers
├── compute
├── complex_types_compute
└── 64b_indexing (non-VulkanSC only)

spirv_assembly.instruction.graphics.variable_pointers
├── graphics
├── multi_buffer_read_only_graphics
├── single_buffer_read_only_graphics
└── nullptr_graphics
```

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Pointer type | `variable_pointers`, `physical_pointers` | Top-level family axis. Swaps the capability, memory model, and pointer storage class. Physical pointers carry device addresses in a `physPtrsStruct`; logical pointers use separate descriptor bindings. | [createVariablePointersComputeGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2746-L2775), [createPhysicalPointersComputeGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2777-L2800) |
| Pipeline type | `compute`, `graphics` | Top-level family axis. Graphics groups route through `createTestsForAllStages()` and exercise vertex/tessellation/geometry/fragment shader translation; compute groups use `SpvAsmComputeShaderCase`. | [createVariablePointersGraphicsGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2802-L2817) |
| Buffer type | `single_buffer`, `two_buffers` | Selects `VariablePointersStorageBuffer` (single buffer, candidates live in different offsets of one binding) versus `VariablePointers` (two bindings, candidates live in `indata_a` and `indata_b`). | [addPhysicalOrVariablePointersComputeGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L335-L345) |
| Selection strategy | `opselect`, `opfunctioncall`, `opphi`, `opcopyobject`, `opptraccesschain` | The SPIR-V op that produces the runtime pointer. Each stresses a different validator rule and lowering path. | [addPhysicalOrVariablePointersComputeGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L357-L561) |
| Store storage class | `Private`, `Function` | Where a `OpVariable` of pointer type lives when testing store-then-reload of a variable pointer. Private is module-scoped; Function is per-invocation. | [stores_private / stores_function](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L486-L520) |
| Index level | `0` to `6` | Depth of nested-struct indirection in the complex-types families. Level 0 selects between `outer_struct` pointers; level 6 selects between `f32` pointers; intermediate levels walk matrices, arrays, inner structs, vec4 arrays, and vec4s. | [numLevels constant](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L716) |
| Input selection | `first_input`, `second_input` | In complex-types tests, which outer_struct member (or which of the two input buffers) is the expected source. The shader's `OpSelect` boolean is set to force this branch. | [selectInputA loop](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L949-L963) |
| 64-bit indexing | `true`, `false` | When true, `spec.uses64BitIndexing = true` requests `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` at compute-pipeline creation and requires `shader64BitIndexing`. It does not change this template's SPIR-V index operands. Non-VulkanSC only. | [64b_indexing registration](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2759-L2773), [pipeline flag](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.cpp#L405-L415) |

## Behavior Parameters

The primary behavioral axis is the intermediate node below each test family. The `compute`, `complex_types_compute`, `nullptr_compute`, `graphics`, `multi_buffer_read_only_graphics`, `single_buffer_read_only_graphics`, and `nullptr_graphics` groups each test a different property of variable pointers. Within the mux-shaped groups, the selection strategy is a secondary axis.

### `compute`: basic mux in a compute shader

Tests the simplest form of runtime pointer selection. A compute shader of `LocalSize 1 1 1` dispatched over `(100, 1, 1)` workgroups loads a selector `s[i]`, computes `is_neg = s[i] < 0`, and selects between two `StorageBuffer` `f32` pointers. The selected pointer is dereferenced and the value is stored to `outdata[i]`. The five selection-strategy leaves (`reads_opselect`, `reads_opfunctioncall`, `reads_opphi`, `reads_opcopyobject`, `reads_opptraccesschain`) cover the legal SPIR-V ways to produce the runtime pointer.

The `stores_private` and `stores_function` leaves store the result of an `OpSelect` into a `Private` or `Function` `OpVariable` of pointer type and reload it before dereferencing. The `writes_*` leaf inverts the mux direction: it loads through the selected pointer, increments the value, and stores it back through the same pointer. The `workgroup_two_buffers` leaf, present only when `!physPtrs && !isSingleInputBuffer`, exercises `OpSelect` between two `Workgroup`-class pointers.

### `complex_types_compute`: seven-level nested-struct indirection

Tests variable pointers that target progressively deeper types inside `outer_struct.r[?][?].(x|y)[?][?]`. The shader walks seven index levels (`outer_struct`, matrices of structs, arrays of structs, structs, arrays of `vec4`, `vec4`, and `f32`) using `OpAccessChain`, `OpPtrAccessChain`, or the strategy-specific op to produce a runtime pointer at the chosen level, then `OpAccessChain`-ing further to a `f32`. Dispatched `(1, 1, 1)`; the single output float is compared against `selectedInput[baseOffset]` computed by [getBaseOffsetForSingleInputBuffer()](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L150-L169).

The `OpPtrAccessChain` path at the deepest level rewrites the obvious `OpPtrAccessChain %sb_f32ptr baseA %c_i32_0 %c_i32_0 %c_i32_1 %c_i32_1 %c_i32_1 %c_i32_1 %c_i32_3` form to exercise a non-zero first `OpPtrAccessChain` index: it produces `%a_loc_arr` with `OpPtrAccessChain`, takes the first element with `OpAccessChain`, and then chains `OpPtrAccessChain` again with `%c_i32_1 %c_i32_3`. This forces the validator to track the stride of the inner array independently of the outer structure.

### `nullptr_compute`: `OpConstantNull` of pointer type

Tests the two legal ways to mention a null pointer under `SPV_KHR_variable_pointers`. The `opvariable_initialized_null` leaf declares `%f32_ptr_var = OpVariable %func_f32ptrptr Function %c_null_ptr` and then overwrites the variable with a valid pointer before loading through it. The `opselect_null_or_valid_ptr` leaf `OpSelect`s between a valid pointer and `%c_null_ptr`, with the selector forced to `%c_bool_true` so the null path is never dereferenced. Both require the full `VariablePointers` capability, not `VariablePointersStorageBuffer`.

### `graphics`: basic mux across all graphics stages

Tests the same mux pattern as `compute` but routed through [createTestsForAllStages()](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1602-L1603), producing vertex, tessellation, geometry, and fragment variants. Because the test function writes its result into a `StorageBuffer` (`outdata`), every stage requires `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`. The graphics `testfun` guards its internal 100-iteration loop with the boilerplate's `isUniqueIdZero` predicate, so the designated invocation performs the mux loop rather than every invocation.

### `multi_buffer_read_only_graphics`: read-only variable pointers across two `StorageBuffer` bindings

Tests `OpSelect`/`OpCopyObject`/`OpPhi`/`OpFunctionCall`/`OpPtrAccessChain` over seven levels of nested-struct indirection in graphics stages, with both input buffers decorated `NonWritable`. Uses the `VariablePointers` capability (two bindings). [OpCompositeInsert](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1987-L1994) writes the result float into the red channel of the output color; the host compares the red channel against `selectedInput[baseOffset]`. No `vertexPipelineStoresAndAtomics` is required because the test function returns a color rather than writing to an SSBO.

### `single_buffer_read_only_graphics`: read-only variable pointers within one buffer

Same seven-level nested-struct pattern as the multi-buffer variant, but with both candidate pointers confined to one `input_buffer` struct (`%input` of type `{ outer_struct a; outer_struct b; }`). Uses the weaker `VariablePointersStorageBuffer` capability. The shader walks `input.a` or `input.b` to the chosen level, selects between the two pointers, and dereferences.

### `nullptr_graphics`: nullptr usage in graphics stages

Same as `nullptr_compute`, but routed through `createTestsForAllStages()`. The shader writes the loaded float into the red channel of the output color via `OpCompositeInsert` instead of into an SSBO.

## Shader Analysis

> **TEMP-SPIRV-ASSEMBLY: spirv_assembly category deviation (temporary, revert before merge to vkcts-wiki).**
>
> For the `spirv_assembly` category only:
> - `#### Source Code` holds the **CTS-authored SPIR-V assembly** (the source of truth), unfoldable, replacing the usual GLSL/HLSL.
> - `shader-analyzer` extracts the assembly from C++ string templates (not reconstructs GLSL/HLSL); preserves CTS-generated `;` comments.
> - The `#### SPIR-V` collapsed subsection is **omitted** because it would duplicate the assembly already shown under `#### Source Code`.
> - `shader-disassembler` runs as a **generation-time validation gate only** (`spirv-as` → `spirv-val` → `spirv-dis`); its output is not published.
> - Amber-backed pages in Batch 9 do not invoke `shader-analyzer`/`shader-disassembler`; the assembly is literal CTS test data extracted verbatim from Amber scripts.

The walkthrough below uses one representative case. The remaining selection-strategy leaves and the physical-pointer path swap a small `${ResultStrategy}` slot and a few capability/extension lines but otherwise share the same template; their variation is summarised in `#### Parameter Variation Summary`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
spirv_assembly.instruction.compute.variable_pointers.compute.reads_opselect_two_buffers
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `variable_pointers` (logical) | Memory model is `Logical`; pointer storage class is `StorageBuffer`; candidates are two `OpVariable` bindings. |
| `compute` pipeline | `OpEntryPoint GLCompute` with `LocalSize 1 1 1`; `numWorkGroups = (100, 1, 1)`. |
| `two_buffers` | Requires the full `VariablePointers` capability, not `VariablePointersStorageBuffer`. Candidates live in `indata_a` and `indata_b`. |
| `opselect` | The runtime pointer is produced by `OpSelect %sb_f32ptr %is_neg %inloc_a_i %inloc_b_i`. |
| `reads_*` (not `writes_*` or `stores_*`) | The selected pointer is dereferenced with a plain `OpLoad`, then stored to `outdata[i]`. No write-through. |

#### Purpose

Confirm that an implementation accepts `OpSelect` between two `StorageBuffer` `f32` pointers from different bindings, dereferences the chosen pointer, and produces the value the host computed with the same mux expression. This is the minimum viable variable-pointer test; every other leaf extends it.

#### Structural Design

The shader has two functions: a host-callable `choose_input_func` selector (unused by this leaf but always present in the template) and `main`. Each invocation runs the mux pipeline once.

```mermaid
flowchart TD
    A[Load gl_GlobalInvocationID.x = i] --> B[Compute AccessChains: inloc_a_i, inloc_b_i, inloc_s_i, outloc_i]
    B --> C[Load s[i] from inloc_s_i]
    C --> D[is_neg = s[i] &lt; 0]
    D --> E[OpSelect sb_f32ptr is_neg inloc_a_i inloc_b_i<br/>= mux_output_var_ptr]
    E --> F[Load f32 from mux_output_var_ptr]
    F --> G[OpStore outloc_i with loaded value]
```

#### Source Code

The extracted SPIR-V assembly below is the specialised output of the C++ string template for `physPtrs=false`, `uses64BitIndexing=false`, `isSingleInputBuffer=false`, `ResultStrategy=reads_opselect`. CTS-authored comments and alignment are preserved; wiki-authored annotations use `;` SPIR-V comment syntax.

```llvm
; Walkthrough: spirv_assembly.instruction.compute.variable_pointers.compute.reads_opselect_two_buffers
; Extracted from the shared string template in addPhysicalOrVariablePointersComputeGroup()
; Specialised with: physPtrs=false, isSingleInputBuffer=false, ResultStrategy=OpSelect

OpCapability Shader
OpCapability VariablePointers                                    ; required because two StorageBuffer bindings are muxed
OpExtension "SPV_KHR_variable_pointers"
OpExtension "SPV_KHR_storage_buffer_storage_class"
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %id
OpExecutionMode %main LocalSize 1 1 1

OpSource GLSL 430
OpName %main           "main"
OpName %id             "gl_GlobalInvocationID"

; --- Decorations ---
OpDecorate %id BuiltIn GlobalInvocationId
OpDecorate %f32arr ArrayStride 4
OpDecorate %sb_f32ptr ArrayStride 4
OpDecorate %buf Block
OpMemberDecorate %buf 0 Offset 0
; (ExtraDecorations slot is empty for reads_opselect)
OpDecorate %indata_a DescriptorSet 0
OpDecorate %indata_a Binding 0
OpDecorate %indata_b DescriptorSet 0
OpDecorate %indata_b Binding 1
OpDecorate %indata_s DescriptorSet 0
OpDecorate %indata_s Binding 2
OpDecorate %outdata DescriptorSet 0
OpDecorate %outdata Binding 3

; --- Common types from getComputeAsmCommonTypes() ---
%bool      = OpTypeBool
%void      = OpTypeVoid
%voidf     = OpTypeFunction %void
%u32       = OpTypeInt 32 0
%i32       = OpTypeInt 32 1
%f32       = OpTypeFloat 32
%uvec3     = OpTypeVector %u32 3
%fvec3     = OpTypeVector %f32 3
%uvec3ptr  = OpTypePointer Input %uvec3
%i32ptr    = OpTypePointer StorageBuffer %i32
%f32ptr    = OpTypePointer StorageBuffer %f32
%i32arr    = OpTypeRuntimeArray %i32
%f32arr    = OpTypeRuntimeArray %f32

; --- Test-specific types (logical variable pointers path) ---
%sb_f32ptr = OpTypePointer StorageBuffer %f32                  ; the pointer type that gets selected at runtime
%buf       = OpTypeStruct %f32arr                              ; StorageBuffer block: runtime array of f32
%bufptr    = OpTypePointer StorageBuffer %buf

; --- Input/output variables (four StorageBuffer bindings) ---
%indata_a  = OpVariable %bufptr StorageBuffer                  ; first mux input
%indata_b  = OpVariable %bufptr StorageBuffer                  ; second mux input (only for two_buffers)
%indata_s  = OpVariable %bufptr StorageBuffer                  ; selector values
%outdata   = OpVariable %bufptr StorageBuffer                  ; result buffer

%id        = OpVariable %uvec3ptr Input
%zero      = OpConstant %i32 0
%one       = OpConstant %i32 1
%two       = OpConstant %i32 2
%three     = OpConstant %i32 3
%fzero     = OpConstant %f32 0
%fone      = OpConstant %f32 1

; --- Helper selector function (always emitted; used only by reads_opfunctioncall) ---
%selector_func_type   = OpTypeFunction %sb_f32ptr %bool %sb_f32ptr %sb_f32ptr
%choose_input_func    = OpFunction %sb_f32ptr None %selector_func_type
%is_neg_param         = OpFunctionParameter %bool
%first_ptr_param      = OpFunctionParameter %sb_f32ptr
%second_ptr_param     = OpFunctionParameter %sb_f32ptr
%selector_func_begin  = OpLabel
%result_ptr           = OpSelect %sb_f32ptr %is_neg_param %first_ptr_param %second_ptr_param
OpReturnValue %result_ptr
OpFunctionEnd

; --- main entry point ---
%main      = OpFunction %void None %voidf
%label     = OpLabel

; Resolve invocation index i and precompute 2*i and 2*i+1 (used by single_buffer; still emitted here)
%idval               = OpLoad %uvec3 %id
%i                   = OpCompositeExtract %u32 %idval 0
%two_i               = OpIAdd %u32 %i %i
%two_i_plus_1        = OpIAdd %u32 %two_i %one

; Compute the four candidate pointers and the output slot
%inloc_a_i           = OpAccessChain %sb_f32ptr %indata_a %zero %i
%inloc_b_i           = OpAccessChain %sb_f32ptr %indata_b %zero %i
%inloc_s_i           = OpAccessChain %sb_f32ptr %indata_s %zero %i
%outloc_i            = OpAccessChain %sb_f32ptr %outdata  %zero %i
%inloc_a_2i          = OpAccessChain %sb_f32ptr %indata_a %zero %two_i
%inloc_a_2i_plus_1   = OpAccessChain %sb_f32ptr %indata_a %zero %two_i_plus_1

; Load the selector and compute is_neg = s[i] < 0
%inval_s_i           = OpLoad %f32 %inloc_s_i Aligned 4
%is_neg              = OpFOrdLessThan %bool %inval_s_i %fzero

; ResultStrategy slot (reads_opselect, two_buffers): select between two binding pointers
%mux_output_var_ptr  = OpSelect %sb_f32ptr %is_neg %inloc_a_i %inloc_b_i

; Dereference the selected pointer and store to outdata[i]
%mux_output          = OpLoad %f32 %mux_output_var_ptr Aligned 4
OpStore %outloc_i %mux_output Aligned 4
OpReturn
OpFunctionEnd
```

#### Additional Info

- The `choose_input_func` selector is emitted by every leaf in this template even when `ResultStrategy` does not use it; the `reads_opfunctioncall` leaf is the only one that calls it. Keeping it unconditional lets the shared template compile for all variants.
- The host pre-computes the expected output as `expectedOutput[i] = (s[i] < 0) ? A[i] : B[i]` for the `two_buffers` variant and `(s[i] < 0) ? A[2*i] : A[2*i+1]` for the `single_buffer` variant. The shader mirrors these expressions exactly.
- For the `single_buffer` variant, `muxInput1` and `muxInput2` become `%inloc_a_2i` and `%inloc_a_2i_plus_1`; the capability is downgraded to `VariablePointersStorageBuffer`.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Selection strategy | `${ResultStrategy}` slot swaps the `OpSelect` for `OpFunctionCall %choose_input_func`, an `OpPhi` block, `OpCopyObject` + `OpSelect`, or `OpPtrAccessChain` chains. | [ResultStrategy specs](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L357-L593) |
| Buffer type | `single_buffer` swaps `muxInput1`/`muxInput2` to in-buffer offsets and downgrades the capability to `VariablePointersStorageBuffer`. | [single_buffer branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L335-L354) |
| Pointer type (physical) | `physPtrs=true` swaps capability to `PhysicalStorageBufferAddressesEXT`, memory model to `PhysicalStorageBuffer64EXT`, replaces the four descriptor bindings with one `physPtrsStruct`, and adds `OpLoad`s of the four device addresses at function entry. | [physPtrs branch](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L299-L308) |
| Store storage class | `stores_*` adds `%sb_f32ptrptr = OpTypePointer <Private\|Function> %sb_f32ptr` and a `OpVariable` of that type, decorated `AliasedPointerEXT` for the physical-pointer path. | [stores block](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L486-L520) |
| 64-bit indexing | `uses64BitIndexing=true` is passed unchanged to the compute runner, which requires `shader64BitIndexing` and chains `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` into pipeline creation; the embedded assembly is otherwise unchanged. | [uses64BitIndexing field](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L370-L372), [runner support and flag](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.cpp#L493-L500) |
| Pipeline (graphics) | Graphics groups wrap the mux in a `for` loop inside `testfun`, return a `v4f32` color, and are expanded by `createTestsForAllStages()` into vertex/tessellation/geometry/fragment variants. | [graphics testFunction](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1498-L1554) |

## Runtime Execution and Result Checking

- The host fills `inputAFloats` (200 floats), `inputBFloats` (200 floats), and `inputSFloats` (100 floats) with random values. `inputSFloats` is forced to contain a shuffled mix of negative and positive values so that both branches of the mux are exercised across the dispatch.
- The host pre-computes four expected buffers (`AmuxAOutputFloats` for `single_buffer` reads, `AmuxBOutputFloats` for `two_buffers` reads, and the `+1`-incremented counterparts for the `writes_*` leaves) using the same mux expression the shader implements.
- The basic compute tests dispatch `(100, 1, 1)` workgroups of size `(1, 1, 1)`. Each invocation reads `s[i]`, selects the pointer, and writes to `outdata[i]`. Logical variants use the four `StorageBuffer` resources directly; physical variants allocate device-address-capable buffers, then replace their descriptors with the address-table `physPtrsStruct`. The runner reads back the expected output buffer for comparison.
- The `complex_types_compute` tests dispatch `(1, 1, 1)` and compare a single output float against `selectedInput[baseOffset]`, where `baseOffset` is computed by [getBaseOffsetForSingleInputBuffer()](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L150-L169) from the same nested indices the shader uses.
- Graphics cases issue one draw and expand the tested assembly to one graphics stage at a time. Basic `graphics` mux cases validate their `outdata` resource against the expected buffer; the read-only complex-type and `nullptr_graphics` cases validate the red channel of the output colors against the value packed by [getExpectedOutputColor()](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1809-L1825). The basic mux loop is guarded so only the boilerplate-defined unique invocation performs it.
- The `nullptr_*` tests compare the output against the known valid input value (`78` for compute, `78/255.f` for graphics), confirming the shader took the valid pointer path rather than the null path.
- All comparisons are performed by the CTS SPIR-V-as-test-runner infrastructure; the host does not implement a custom check loop.

## Failure Meaning

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

### Cause Analysis

#### Selection-strategy failures

**Possible failure symptoms:** the output buffer mismatches the host-computed expected values; the mismatch pattern tracks the selection strategy (e.g. only `opphi` leaves fail, or only `opptraccesschain` leaves fail).

**Possible implementation causes:** the SPIR-V validator or driver translator mishandles one specific way of producing a runtime pointer. For `OpSelect`, the validator may not accept a pointer result type even with the correct capability. For `OpPhi`, the driver may not propagate the pointer value across the merge block. For `OpFunctionCall`, the calling convention may not preserve the pointer's storage-class origin. For `OpPtrAccessChain`, the stride computation for the inner array may be wrong. Source-level investigation is needed to confirm which lowering path is at fault before attributing the cause to a specific compiler stage.

#### Addressing failures

**Possible failure symptoms:** `complex_types_compute` or `*_read_only_graphics` leaves produce a wrong float at one specific index level; the wrong offset is loaded.

**Possible implementation causes:** the implementation computes `OpPtrAccessChain` strides incorrectly for one of the seven nested types (matrix of structs, array of structs, array of `vec4`, etc.), or the `OpAccessChain` into a variable pointer does not preserve the original binding. The complex-types test is built to expose this: each level exercises a different `OpTypePointer` target type, so a per-type stride bug surfaces as a failure at exactly one level.

#### Nullptr-handling failures

**Possible failure symptoms:** `nullptr_compute` or `nullptr_graphics` leaves crash, return zero, or return a wrong value; the device-side validation layer reports a null dereference.

**Possible implementation causes:** the driver rejects `OpConstantNull` of pointer type as a constant value, or rejects `OpVariable` of `Function` storage class with a pointer initializer. If the failure is a crash, the driver may have dereferenced the null branch of `OpSelect` despite the constant-foldable `c_bool_true` selector. Source-level investigation is needed to confirm whether the failure is a validation-layer reject or an actual null dereference.

#### Graphics-stage translation failures

**Possible failure symptoms:** only the `graphics`, `multi_buffer_read_only_graphics`, `single_buffer_read_only_graphics`, or `nullptr_graphics` leaves fail; the corresponding compute leaves pass.

**Possible implementation causes:** the graphics-stage shader translator does not lower variable pointers the same way the compute translator does. Specific suspects include the per-stage store-and-atomic feature gate (`vertexPipelineStoresAndAtomics`/`fragmentStoresAndAtomics`) being silently missing, the `NonWritable` decoration on read-only inputs being over-enforced as a ban on variable-pointer selection, and the `OpCompositeInsert` into the output color being dropped by a stage-specific optimiser.

#### Physical-pointer aliasing failures

**Possible failure symptoms:** only the `physical_pointers` family fails; the `variable_pointers` family passes with the same selection strategy.

**Possible implementation causes:** the `PhysicalStorageBufferAddressesEXT` capability is not honoured, the 64-bit address loads from `physPtrsStruct` or the subsequent `Aligned 4` pointee accesses are mishandled, or the relevant decorations are mishandled (`Restrict` on selector parameters and `AliasedPointerEXT` only on physical `stores_*` local variables). The `physPtrsStruct` packing four addresses at offsets 0/8/16/24 is the specific shape that exercises this; a misalignment of the struct layout in the driver would surface as a wrong address being loaded.

#### 64-bit indexing failures

**Possible failure symptoms:** only the `64b_indexing` sub-group fails; the matching 32-bit-indexing leaves pass.

**Possible implementation causes:** the implementation does not honour `VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT`, or its `shader64BitIndexing` support path rejects or mishandles this otherwise unchanged assembly. This subgroup does not widen the template's `OpAccessChain` or `OpPtrAccessChain` operands. Because `64b_indexing` is non-VulkanSC only, this is also a place to confirm whether the build configuration flag is set, rather than blaming the driver.

## Case Pruning

### Requirement-based pruning

- `VariablePointersStorageBuffer` capability is required for `single_buffer` leaves; `VariablePointers` is required for `two_buffers`, `workgroup_two_buffers`, and all `nullptr_*` leaves. Implementations advertising only the weaker capability skip the stronger leaves automatically through the Vulkan feature gate.
- `PhysicalStorageBufferAddressesEXT` capability (and `bufferDeviceAddress`-related features) is required for the entire `physical_pointers` family.
- Graphics groups that write to `outdata` require both `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`; the read-only graphics groups drop this requirement and use `NonWritable` instead.
- The entire `64b_indexing` sub-group is wrapped in `#ifndef CTS_USES_VULKANSC` and is absent from Vulkan SC builds.

### Design-based pruning

- The `workgroup_two_buffers` leaf is generated only when `!physPtrs && !isSingleInputBuffer`, because `VariablePointersStorageBuffer` does not extend to `Workgroup` storage; only the full `VariablePointers` capability does. There is no `workgroup_single_buffer` or `workgroup_physical` leaf.
- The `physical_pointers` family has no `nullptr_*` intermediate node: physical pointers have no SPIR-V `OpConstantNull` equivalent worth testing under this template, and the file does not synthesise one.
- The `physical_pointers` family has no `graphics` intermediate node: physical storage buffer pointers are exercised in compute only within this file.
- The `complex_types_compute` family fixes the index tuple per level via the `indexesForLevel[numLevels][6]` table rather than enumerating every combination; the table ensures "at any level, any given offset is exercised" exactly once.

## Key Takeaways

- The page covers three registered test families (`compute.variable_pointers`, `compute.physical_pointers`, `graphics.variable_pointers`) that share one C++ string template and one mux pattern; the structural reason for grouping them is the shared template, not shader-content similarity.
- `single_buffer` versus `two_buffers` is the explicit switch between the `VariablePointersStorageBuffer` and `VariablePointers` capability tiers; the file generates both so a weaker implementation can still run the in-buffer leaves.
- The five selection strategies (`opselect`, `opfunctioncall`, `opphi`, `opcopyobject`, `opptraccesschain`) are not redundant: each stresses a different validator and lowering rule for runtime pointers, and a per-strategy failure isolates the affected lowering path.
- The `complex_types_compute` seven-level index table exists to expose per-type `OpPtrAccessChain` stride bugs; a failure at exactly one level points to that type's stride handling.
- The physical-pointer path is the same mux logic with the storage class, memory model, capability, and descriptor layout swapped. A failure isolated to `physical_pointers` points to address handling or alias decoration, not to the mux logic itself.
- See `## Failure Meaning` for the detailed cause analysis; each behavior-parameter value maps to a distinct cause cluster.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `addPhysicalOrVariablePointersComputeGroup` | [vktSpvAsmVariablePointersTests.cpp#L171-L641](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L171-L641) | Owns the shared compute mux template and the `single_buffer`/`two_buffers` expansion for both variable and physical pointers. |
| `addComplexTypesPhysicalOrVariablePointersComputeGroup` | [vktSpvAsmVariablePointersTests.cpp#L643-L1255](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L643-L1255) | Owns the seven-level nested-struct indirection matrix. |
| `addNullptrVariablePointersComputeGroup` | [vktSpvAsmVariablePointersTests.cpp#L1257-L1386](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1257-L1386) | Owns the `OpConstantNull` and `OpSelect null` compute leaves. |
| `addVariablePointersComputeCustomTests` | [vktSpvAsmVariablePointersTests.cpp#L1388-L1406](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1388-L1406) | Folds `vktSpvAsmOpSelectDifferentStridesTests.cpp` into the compute `variable_pointers` group (non-VulkanSC only). |
| `addVariablePointersGraphicsGroup` | [vktSpvAsmVariablePointersTests.cpp#L1408-L1807](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1408-L1807) | Owns the graphics basic-mux group; routes through `createTestsForAllStages()`. |
| `getExpectedOutputColor` | [vktSpvAsmVariablePointersTests.cpp#L1809-L1825](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1809-L1825) | Packs the chosen float into the red channel for graphics comparisons. |
| `addTwoInputBufferReadOnlyVariablePointersGraphicsGroup` | [vktSpvAsmVariablePointersTests.cpp#L1827-L2228](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L1827-L2228) | Owns the two-input-buffer read-only graphics group; uses `VariablePointers` and `NonWritable`. |
| `addSingleInputBufferReadOnlyVariablePointersGraphicsGroup` | [vktSpvAsmVariablePointersTests.cpp#L2230-L2641](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2230-L2641) | Owns the single-input-buffer read-only graphics group; uses `VariablePointersStorageBuffer`. |
| `addNullptrVariablePointersGraphicsGroup` | [vktSpvAsmVariablePointersTests.cpp#L2643-L2743](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2643-L2743) | Owns the graphics nullptr leaves. |
| Registration entry points | [vktSpvAsmVariablePointersTests.cpp#L2746-L2817](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L2746-L2817) | `createVariablePointersComputeGroup`, `createPhysicalPointersComputeGroup`, `createVariablePointersGraphicsGroup`. |
| `getBaseOffset` / `getBaseOffsetForSingleInputBuffer` | [vktSpvAsmVariablePointersTests.cpp#L103-L169](../../../modules/vulkan/spirv_assembly/vktSpvAsmVariablePointersTests.cpp#L103-L169) | Host-side offset computation that mirrors the shader's nested-struct indexing. |
| `getComputeAsmCommonTypes` | [vktSpvAsmComputeShaderTestUtil.cpp#L82-L100](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L82-L100) | Provides the common SPIR-V types (`%bool`, `%void`, `%f32`, `%u32`, `%f32arr`, etc.) shared by every compute SPIR-V-as test. |
