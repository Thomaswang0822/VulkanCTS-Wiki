# Understanding Brief: `spirv_assembly.instruction.compute.ubo_padding` / `graphics.ubo_padding`

This brief prepares a Level-3 rewrite of the UBO matrix-padding page. It is explanation-first and treats the current CTS implementation as the source of truth.

## One-Sentence Test Purpose

These tests check whether Vulkan correctly applies SPIR-V uniform-buffer layout decorations when a shader reads an array of 128 column-major `mat2x2` values whose columns have a 16-byte stride and whose array elements have a 32-byte stride, then copies the four matrix components into one output `vec4` per element.

The core question is: **does the implementation skip the two-float padding at the end of each two-component matrix column and the corresponding padded space between array elements, while preserving the declared column-major indexing?**

## Background Knowledge

### `mat2x2` in SPIR-V

The source represents `mat2x2` as `OpTypeMatrix %v2float 2`: two column vectors, each containing two 32-bit floats. A matrix therefore has four meaningful scalar components, but its memory representation is controlled separately by decorations.

For the UBO member under test:

- `ColMajor` means matrix indexing addresses columns.
- `MatrixStride 16` means successive columns begin 16 bytes apart. A `vec2` contains only 8 bytes, so each column has 8 bytes of padding.
- `ArrayStride 32` means successive matrices begin 32 bytes apart. This is exactly two 16-byte column slots.

The host makes the padding observable by supplying two `vec4` values per matrix. The first stores `(x, y, 0, 0)` and the second stores `(z, w, 0, 0)`. The shader must read only `(x, y)` from column 0 and `(z, w)` from column 1.

### Descriptor-backed buffers

The compute shader declares an input `Uniform` variable decorated as a `Block` at descriptor set 0, binding 0, and an output `Uniform` variable decorated as a `BufferBlock` at set 0, binding 1. The compute utility binds the input as `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` and the output as the default output resource.

The graphics path uses the same SPIR-V layout decorations and the same two-buffer payload. Its resources are initially built with an input uniform buffer and output storage buffer; the input descriptor type is explicitly set to `VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER` before stage cases are created.

### Compute and graphics execution

The compute path dispatches `numElements = 128` workgroups in `x`, with local size 1, so invocation `x` reads matrix `x` and writes output element `x`.

The graphics path puts the same read/write function in a selected graphics stage. The function loops from 0 through 127, reads all four matrix scalars, writes one output `vec4` for each matrix, and returns its input parameter unchanged. The graphics utility creates five stage-specific cases: vertex, tessellation control, tessellation evaluation, geometry, and fragment.

## Representative Data Flow

```text
[host] generate 128 random Vec4 values v = (x, y, z, w)
[host] expected output[i] = v
[host] UBO element i = (x, y, 0, 0), (z, w, 0, 0)
[device] read UBO[i].column[0].component[0..1] -> output[i].x/y
[device] read UBO[i].column[1].component[0..1] -> output[i].z/w
[host] compare output readback against expected Vec4 array
```

## Source Anchors

- Compute assembly and data generation: `vktSpvAsmUboMatrixPaddingTests.cpp`, lines 46–146.
- Graphics resources, assembly fragments, and data generation: lines 149–252.
- Graphics stage registration and feature selections: lines 254–273.
- Compute and graphics group factories: lines 278–293.
- Parent registration under `instruction.compute` and `instruction.graphics`: `vktSpvAsmInstructionTests.cpp`, lines 21399 and 21498.
- Default Vulkan mustpass leaves: `mustpass/main/vk-default/spirv-assembly.txt`, lines 16208 and 38934–38938.
- Vulkan SC mustpass leaves: `mustpass/main/vksc-default/spirv-assembly.txt`, lines 5648 and 20759–20763.

## Important Audit Points

- There is one compute leaf (`mat2x2`) and five graphics leaves, not a matrix-shape family: the source only defines `mat2x2`.
- The shader reads 128 matrices; it does not test a runtime-sized or dynamically selected matrix count.
- The compute path uses `GlobalInvocationId.x` directly. The graphics path performs the 128-element loop inside one shader invocation.
- Graphics vertex, tessellation-control, tessellation-evaluation, and geometry cases request `vertexPipelineStoresAndAtomics`; the fragment case instead requests `fragmentStoresAndAtomics`.
- The source passes no explicit extensions, specialization constants, push constants, or graphics interfaces for these cases.
- The implementation uses legacy SPIR-V `Uniform` plus `Block`/`BufferBlock` declarations. This is part of the authored test and should not be silently rewritten as modern storage-class syntax.

## Conversion Notes

The final page should explain the memory offsets with one concrete matrix, retain the exact registration trees and feature qualifications, and include one representative authored compute assembly block under `#### Source Code`. A separate disassembly section is unnecessary because the source already contains the test's SPIR-V assembly text; any assembler/validator run is a generation-time check, not a CTS runtime behavior parameter.
