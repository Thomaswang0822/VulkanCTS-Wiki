# Understanding Brief: IndexingTests

## One-Sentence Test Purpose

This test family checks that Vulkan implementations form and dereference SPIR-V access-chain pointers correctly for nested buffer data, non-16-byte array strides, and graphics-stage output components.

## Background Knowledge

### SPIR-V access-chain instructions

`OpAccessChain` computes a pointer by walking a composite object with a base pointer and index operands. `OpInBoundsAccessChain` expresses the in-bounds form of that operation. `OpPtrAccessChain` also permits pointer arithmetic from a pointer into an array element, and these cases use the variable-pointers capability and storage-buffer storage class where required.

Why it matters here:

- The struct cases hold the same nested data layout and selector values constant while changing the access-chain instruction.
- A wrong pointer type, storage class, index conversion, or offset calculation produces a different element than the CPU reference selects.

### Buffer layout and array stride

SPIR-V decorations such as `ArrayStride`, member `Offset`, `Block`, and `BufferBlock` describe how composite data occupies a buffer. A float array with 18 elements has a 72-byte stride, which is deliberately not a multiple of 16.

Why it matters here:

- The `non16basealignment` cases must reach each struct instance using the declared 72-byte stride.
- The test avoids floating-point comparison noise by floor-rounding generated inputs before computing expected sums.

## One Concrete Example

The representative case is:

```text
dEQP-VKSC.spirv_assembly.instruction.compute.indexing.input.non16basealignment.opaccesschain
```

Its generated compute assembly declares a storage buffer containing a runtime array of `struct1`; each `struct1` contains `float f[18]`. Invocation `i` reads `gl_GlobalInvocationID.x`, forms pointers to `f[0]` through `f[17]` with `OpAccessChain`, sums the loaded values, and stores one sum at output element `i`. The host dispatches 32 invocations and compares all 32 output floats with sums computed from the same floor-rounded input array.

## End-to-End Test Flow

```text
[host] choose access-chain operation, index width, signedness, and applicable graphics stage
[host] generate random input data and selector vectors, then compute the expected output values
[host] specialize the CTS SPIR-V string template and bind input, selector, and output buffers
[host] request required integer or variable-pointer features where the variant needs them
[host] dispatch the compute work or create per-stage graphics tests
[device] form pointers with the selected access-chain instruction and load or store the selected component
[device] write a scalar result to the output buffer or graphics interface output
[host] compare the observed output against the precomputed expected values
[host] mark the CTS case pass or fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The implementation specializes SPIR-V assembly string templates for the struct and non-16-base-alignment compute paths. The template selects `OpAccessChain`, `OpInBoundsAccessChain`, or `OpPtrAccessChain`, integer declarations/conversions, and storage-class decorations.
- The graphics struct path uses the same conceptual nested access but creates cases for every graphics stage.
- The graphics `component` path builds stage-specific interface-operation fragments that write the indexed output component.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Nested input buffer | yes | yes | read | no | Holds two `InputData` objects for the struct cases. |
| Selector buffer | yes | yes | read | no | Supplies four indices for each selected nested element. |
| Expected/output buffer | yes | yes | written | yes | Carries the selected float or per-instance sum for comparison. |
| Graphics interface input/output | yes | yes | read and written | checked by graphics utility | Drives the `component` test across graphics stages. |

## What Is Checked

- Struct cases compare every output element with the CPU-selected float from the same selector vector.
- `non16basealignment` compares each output element with the CPU sum of its 18 floor-rounded input floats.
- Graphics component coverage uses `GraphicsInterfaces` and `createTestsForAllStages` to validate the stage-specific indexed output.

## Behavior Parameter Identification

> **Behavior parameter:** test-family behavior
>
> **Candidate values:** `struct`, `non16basealignment`, `component`

The `struct` behavior has compute and graphics registrations, while `non16basealignment` is compute-only and `component` is graphics-only.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `struct` | Incorrect nested-composite pointer traversal, index conversion, storage-class handling, or selected value store. |
| `non16basealignment` | Incorrect handling of the declared 72-byte runtime-array stride or `OpPtrAccessChain` base-pointer arithmetic. |
| `component` | Incorrect access-chain addressing of a graphics output interface component in one or more stages. |

## Important Variations and Special Cases

- `struct` varies `opaccesschain`, `opinboundsaccesschain`, and `opptraccesschain`; it also varies 16-, 32-, and 64-bit index operands and signedness.
- `OpPtrAccessChain` cases request `VK_KHR_variable_pointers`, `variablePointersStorageBuffer`, `SPV_KHR_variable_pointers`, and `SPV_KHR_storage_buffer_storage_class`.
- The 16- and 64-bit struct variants request `shaderInt16` and `shaderInt64`, respectively.
- The `_64bit_indexing` duplicate variants are compiled only when `CTS_USES_VULKANSC` is not defined.
- `non16basealignment` covers only `opaccesschain` and `opptraccesschain`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Compute struct generator | [addComputeIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L68-L293) | Defines the nested layout, selector conversion, expected-value calculation, and compute registration. |
| Graphics struct generator | [addGraphicsIndexingStructTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L295-L532) | Extends the nested-layout cases across graphics stages. |
| Graphics component generator | [addGraphicsOutputComponentIndexingTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L534-L595) | Defines the stage-specific output-component access chains. |
| Non-16-base-alignment generator | [addComputeIndexingNon16BaseAlignmentTests()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L597-L757) | Defines the 18-float layout, sum check, and access-chain specialization. |
| Registration entry points | [createIndexingComputeGroup() and createIndexingGraphicsGroup()](../../../modules/vulkan/spirv_assembly/vktSpvAsmIndexingTests.cpp#L761-L788) | Place the implemented test families under compute and graphics `indexing`. |

## Questions / Risk Points for User Audit

- Does the distinction between nested composite traversal and non-16-byte stride handling make the three behavior values clear?
- Does the host/device timeline make clear that the expected data is computed before execution?
- Does the representative assembly explain why `ArrayStride 72` is the key non-16-base-alignment fact?
- Should the final page retain one representative assembly walkthrough for `non16basealignment`, rather than duplicate the much larger struct template?

## Conversion Notes for Final Wiki Rewrite

- Distill the two prerequisite topics into short final-page bullets.
- Carry the failure-cause mapping table unchanged into `## Failure Meaning`.
- Use the `non16basealignment.opaccesschain` case as the representative walkthrough because it exposes the layout, per-invocation index, repeated element accesses, and result check in one assembly program.
- Keep the final page focused on behavior; retain source navigation in its appendix.
