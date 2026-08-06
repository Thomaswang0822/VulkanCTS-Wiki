## Overview

The `ssbo` (Shader Storage Buffer Object) test category collects tests that check storage-buffer layout, descriptor-visible ranges, generated shader access, physical storage-buffer references, and a long-shader crash regression.

## Background Knowledge

- A storage buffer gives a shader a structured view of buffer bytes. Layout rules determine member offsets and array or matrix strides, so the host reference model and shader interface must agree.
- A descriptor binding supplies a buffer and a visible offset/range to a shader. For a runtime array, `length()` is derived from that visible range rather than from a declared final count.
- A physical storage-buffer reference uses a device address passed through the shader interface instead of an ordinary named descriptor access. This is why the `phys` and `corner_case` families have buffer-device-address support requirements.

## Category Structure

```text
ssbo
├── layout
├── unsized_array_length
├── readonly
├── phys
└── corner_case
```

`layout`, `readonly`, and `phys` are variants of the generated `SSBOLayoutTests` implementation. `unsized_array_length` is a dedicated runtime-array suite and appends `nested_unsized_arrays` from a separate implementation. `corner_case` is delegated to its own implementation. `vktSSBOLayoutCase.cpp` supplies shared layout computation, shader generation, dispatch, and comparison infrastructure; it is not a separate registered test family.

## How the Families Fit Together

The families exercise different ways that shader-visible storage-buffer layout and access can go wrong:

- **Generated layout:** compares shader reads and writes against a separately computed byte-layout reference across types, layouts, arrays, structs, matrices, and buffer placement modes.
- **Runtime-array length:** checks that the shader-reported length follows the descriptor offset and range, including `VK_WHOLE_SIZE` and supported 64-bit variants.
- **Access variants:** `readonly` removes write-dependent cases, while `phys` reaches equivalent storage through buffer device addresses and push constants.
- **Specialized coverage:** `nested_unsized_arrays` combines generated nested structures with non-uniform descriptor-array indexing and guard zones; `corner_case` stresses compilation and execution of a long buffer-reference comparison shader.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `layout`, `readonly`, `phys`, and the implementation of `unsized_array_length` | [SSBOLayoutTests](../testfiles/ssbo/SSBOLayoutTests.md) | Generated layout dimensions, shader access modes, reference-data checking, runtime-array length, and support gates |
| `unsized_array_length.nested_unsized_arrays` | [SSBOLayoutNestedUnsizedArraysTests](../testfiles/ssbo/SSBOLayoutNestedUnsizedArraysTests.md) | Nested generated structures, descriptor-array indexing, aligned ranges, and guard-zone verification |
| `corner_case.long_shader_bitwise_and` | [SSBOCornerCase](../testfiles/ssbo/SSBOCornerCase.md) | Physical-storage-buffer crash-regression workload and its dispatch-only pass condition |

## Category Notes

- The Vulkan SC mustpass retains the main layout, readonly, phys, and corner-case families while excluding the source-guarded 64-bit unsized-array cases.
- Each Level-3 page is limited to an implementation-bearing registered source file. Shared helpers are linked from the pages rather than published as standalone test-family documents.
