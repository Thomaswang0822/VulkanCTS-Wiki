# Understanding Brief: Variable-pointer robust buffer access

## One-Sentence Test Purpose

This test checks whether robust storage-buffer access remains correct when a shader reads or writes through a runtime-selected SPIR-V variable pointer.

## Background Knowledge

### Descriptor ranges and robust buffer access

`robustBufferAccess` bounds checks accesses through a buffer descriptor against the descriptor's range, which can be smaller than the underlying allocation. Out-of-bounds reads may return zero or data from memory bound to the buffer. Out-of-bounds storage-buffer writes may be discarded or may change data within memory bound to that buffer, but must not modify unrelated memory. Non-atomic accesses wider than 32 bits may be checked as separate 32-bit accesses. These rules are described in [Robust Buffer Access](../../../vulkan-docs/src/chapters/shaders.adoc#L1925-L1975).

### Variable pointers in SPIR-V

The `variablePointersStorageBuffer` feature allows the `VariablePointersStorageBuffer` capability used by this test. The generated module declares `SPV_KHR_variable_pointers`, builds ordinary `OpAccessChain` candidates, and uses `OpSelect` to produce a pointer whose value depends on data loaded at runtime. The feature definition requires the implementation to support that SPIR-V capability ([feature definition](../../../vulkan-docs/src/chapters/features.adoc#L1066-L1077)).

## One Concrete Example

A representative scalar read case uses `16B_in_memory_with_scalar_f32`. The shader loads a source index from the uniform index buffer, builds two pointers into the input storage buffer, selects one with `OpSelect`, loads through the selected pointer, and stores the result through a regular output pointer. The write case keeps the same setup but makes the selected pointer the store destination.

## End-to-End Test Flow

```text
[host] choose a shader stage, scalar or vec4 copy type, format, access size, and backing-memory mode
[host] create input and output storage buffers and a three-element uniform index buffer
[host] generate direct SPIR-V assembly with VariablePointersStorageBuffer and SPV_KHR_variable_pointers
[host] bind the buffers at descriptor bindings 0, 1, and 2
[host] submit one compute dispatch or graphics draw and wait on a fence
[device] build pointer candidates with OpAccessChain and select a variable pointer with OpSelect
[device] load through the selected pointer for a read case, or store through it for a write case
[host] invalidate mapped output memory and classify each checked element
[host] pass when all values satisfy the robust-access rules
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The C++ generator emits direct SPIR-V assembly from `MakeShader()`.
- The module declares `Shader` and `VariablePointersStorageBuffer`; R64 formats also add `Int64`.
- The entry point is `GLCompute` with local size `1,1,1`, or `Vertex` or `Fragment` for graphics cases. The untested graphics stage receives a minimal pass-through module.
- The generator emits scalar or vec4 load/store sequences. R64 vector cases use the scalar path instead.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input storage buffer | yes | binding 0 | read | indirectly, for expected values | Holds deterministic format-specific source data. |
| Output storage buffer | yes | binding 1 | written | yes | Receives copied values and starts filled with `0xBA` bytes. |
| Index uniform buffer | yes | binding 2 | read | no | Supplies source and destination indices plus a zero selector value. |
| Vertex buffer | graphics only | vertex input | read by fixed-function input | no | Supplies the small draw used by vertex and fragment cases. |
| GLSL `shared` variable | no | no | no | no | The implementation uses storage-buffer pointers, not a host-created shared-memory object. |

## What Is Checked

- The input buffer contains deterministic values derived from the selected format. The output buffer starts with the `0xBA` filler pattern.
- `in_memory` selects an address inside the allocation but outside the descriptor-accessible range. `out_of_memory` selects the last entry of the 1024-element shader array, beyond the backing buffer allocation.
- In-bounds reads must match the deterministic input values. In-bounds write results must be an allowed input value or zero.
- Out-of-bounds reads must produce an allowed value from the input allocation or zero. A vec4 read may also match the permitted `[0, 0, 0, x]` pattern.
- Out-of-bounds writes must leave output bytes unchanged or produce a value allowed from the input allocation or zero. Partial accesses are checked by byte portion.
- A failed 64-bit check is retried as split 32-bit accesses, matching the Vulkan robust-access rule for wide non-atomic accesses.

## Behavior Parameter Identification

> **Behavior parameter:** access direction (`reads` or `writes`)
>
> **Candidate values:** `reads`, `writes`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `reads` | Variable-pointer selection, pointer dereference, descriptor-range handling, or robust out-of-bounds read result is incorrect. |
| `writes` | Variable-pointer store selection or robust out-of-bounds write containment is incorrect. |

## Important Variations and Special Cases

- `compute`, `graphics.reads.vertex`, `graphics.reads.fragment`, `graphics.writes.vertex`, and `graphics.writes.fragment` select the execution stage. Graphics cases use a pass-through shader for the stage that is not under test.
- `scalar` and `vec4` change the SPIR-V operand width and the number of source values copied. `VK_FORMAT_R64_SINT` and `VK_FORMAT_R64_UINT` require `shaderInt64` and use scalar generation for the vec4 selection.
- `1B`, `3B`, `4B`, `16B`, and `32B` select the descriptor access range. `in_memory` and `out_of_memory` distinguish a descriptor-range overrun from an address beyond the allocation.
- The source defines `SHADER_TYPE_MATRIX_COPY`, but the registration array contains only `vec4` and `scalar`, so no matrix leaves are registered.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| SPIR-V generation | [MakeShader()](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L839-L1239) | Emits capabilities, resources, pointer selection, and stage entry points. |
| Read and write program registration | [initPrograms()](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1278-L1349) | Maps each case to compute, vertex, and fragment SPIR-V modules. |
| Host setup | [AccessInstance constructor](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1352-L1540) | Creates buffers, descriptors, indices, and execution environments. |
| Result checking | [verifyResult()](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1632-L1848) | Defines accepted in-bounds, partial, and out-of-bounds results. |
| Registration matrix | [createBufferAccessWithVariablePointersTests()](../../../modules/vulkan/robustness/vktRobustBufferAccessWithVariablePointersTests.cpp#L1897-L2001) | Defines the registered hierarchy and generated leaf dimensions. |

## Questions / Risk Points for User Audit

- Is `reads` versus `writes` the clearest primary behavioral axis for this page?
- Should the final page show one direct-SPIR-V excerpt, or should a later pass generate and insert the complete representative assembly?
- Should the graphics stage split receive more space than the concise stage summary here?
- Are the accepted out-of-bounds values described narrowly enough for the Vulkan version used by this CTS source?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page focused on `robustness.buffer_access.through_pointers`, not on the broader robustness category.
- Distill the descriptor-range and variable-pointer explanations into short prerequisite bullets.
- Carry the `reads` and `writes` mapping table directly into `## Failure Meaning`.
- Add a source-reviewed direct-SPIR-V walkthrough for a representative `compute.reads` leaf. The current rewrite should not invent GLSL or HLSL, and the complete disassembly should be generated in a follow-up pass if required by the publication gate.
- Keep the full generated leaf matrix in `## Parameter Dimensions and Observed Values` rather than listing every mustpass leaf.
