# vktMemoryModelSharedLayout.cpp

This document describes the delegated `memory_model.shared` tests registered in
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp) and implemented with helper
logic from [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp).

## Overview

The `shared` branch generates randomized compute-shader cases that declare shared-memory structures, write generated literal
values into every reachable leaf field, synchronize, then compare the shared-memory contents against the expected values. The
branch is organized by feature sets such as scalar/vector/basic types, arrays, arrays of arrays, nested structs, plus separate
16-bit and 8-bit type groups whose cases have feature-specific support checks.

## Role of File

- **Registered implementation file.** `vktMemoryModelSharedLayout.cpp` constructs the `shared` group and its direct children.
- `vktMemoryModelSharedLayoutCase.cpp` provides helper and execution logic, but it does not register its own group; therefore it
  is documented here rather than as a separate Level-3 page.
- The category root adds the returned `shared` group in
  [vktMemoryModelMessagePassing.cpp](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2410-L2413).

## Source Code

| Purpose | Link |
|---------|------|
| Feature-bit definitions | [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L45-L56) |
| Random case-group registration helper | [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L94-L104) |
| Shared-object generation | [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L134-L160) |
| Random type generation | [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L162-L283) |
| `shared` group registration | [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L330) |
| Shader write/compare generation | [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L197-L269) |
| Compute shader generation | [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L271-L344) |
| Support checks | [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L347-L358) |
| Execution and result check | [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L360-L488) |

## Other Inspected Related Files

| File | Role |
|------|------|
| [vktMemoryModelSharedLayout.hpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.hpp) | Declares `createSharedMemoryLayoutTests`. |
| [vktMemoryModelSharedLayoutCase.hpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.hpp) | Declares shared-layout case data structures and classes. |
| [util/vktTypeComparisonUtil.cpp](../../../modules/vulkan/util/vktTypeComparisonUtil.cpp) | Provides type comparison helpers used by generated shaders. |

## Registration Hierarchy

```text
memory_model.shared
├── scalar_types
├── vector_types
├── basic_types
├── basic_arrays
├── arrays_of_arrays
├── nested_structs
├── nested_structs_arrays
├── 16bit
└── 8bit
```

The parseable tree lists only direct children of `memory_model.shared`. Source generation is a three-pass loop in
[`createSharedMemoryLayoutTests()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L327):

| Loop pass | Parent group receiving the seven case families | Extra type feature bit |
|-----------|-----------------------------------------------|------------------------|
| `i == 0` | `memory_model.shared` itself | none |
| `i == 1` | newly added `memory_model.shared.16bit` group | `FEATURE_16BIT_TYPES` |
| `i == 2` | newly added `memory_model.shared.8bit` group | `FEATURE_8BIT_TYPES` |

In each pass, the same seven `createRandomCaseGroup()` calls create `scalar_types`, `vector_types`, `basic_types`,
`basic_arrays`, `arrays_of_arrays`, `nested_structs`, and `nested_structs_arrays`, each with 10 numbered randomized cases
[`vktMemoryModelSharedLayout.cpp`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L326). Therefore
`16bit` and `8bit` are not just attributes on the root families; they are actual child groups containing their own copies of
those seven families with additional type-generation flags.

## Test Families

### scalar_types — Scalar shared-memory variables

At the root of `shared`, `scalar_types` creates 10 randomized cases with unused variables/members enabled and no vector,
matrix, array, or struct feature bits [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L314).

### vector_types — Vector shared-memory variables

`vector_types` creates 10 randomized cases with vector types enabled, still including unused variables and members
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L314).

### basic_types — Scalar, vector, and matrix mix

`basic_types` is one of the seven families emitted in every loop pass. At the root, it uses `allBasicTypes`
(`FEATURE_VECTORS | FEATURE_MATRICES`) without 16-bit or 8-bit type flags; inside `16bit`, the same family name is emitted
with `FEATURE_16BIT_TYPES`; inside `8bit`, it is emitted with `FEATURE_8BIT_TYPES`
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L292-L314).

### basic_arrays — Arrays of basic types

`basic_arrays` adds array generation to the basic scalar/vector/matrix feature mix
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L315-L316).

### arrays_of_arrays — Nested array layouts

`arrays_of_arrays` enables both arrays and arrays-of-arrays, creating 10 cases with a base seed of 950
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L317-L320).

### nested_structs — Nested struct layouts

`nested_structs` enables struct generation in addition to basic types and unused-variable/member coverage
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L321-L322).

### nested_structs_arrays — Nested structs with array nesting

`nested_structs_arrays` combines basic types, structs, arrays, and arrays-of-arrays
[vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L323-L326).

### 16bit — 16-bit type variants

`16bit` is a direct child of `shared`; inside it, the same seven case-family names are generated with `FEATURE_16BIT_TYPES`
added [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L295-L327).

### 8bit — 8-bit type variants

`8bit` is a direct child of `shared`; inside it, the same seven case-family names are generated with `FEATURE_8BIT_TYPES`
added [vktMemoryModelSharedLayout.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L295-L327).

## Parameter Dimensions and Observed Values

| Dimension | Observed values / ranges | Evidence |
|-----------|--------------------------|----------|
| Cases per generated family | `10` cases, named `0` through `9` by the loop index | [createRandomCaseGroup](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L94-L104) |
| Base seeds | `0`, `25`, `50`, `50`, `950`, `100`, `150`, plus command-line base seed | [registration](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L310-L326), [base seed adjustment](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L94-L104) |
| Shared object count | The constructor passes `1` and `m_maxSharedObjects` (`3`) to `rnd.getInt` when deciding how many shared objects to generate. | [constructor loop](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L115-L123), [limits](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.hpp#L218-L235) |
| Members per shared object | The generator passes `2` and `m_maxSharedObjectMembers` (`4`) to `rnd.getInt` when deciding how many members to generate. | [member generation](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L134-L143), [limits](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.hpp#L218-L235) |
| Array length | When arrays are enabled, `m_maxArrayLength` is set to `3`, and the type generator passes `1` and `m_maxArrayLength` to `rnd.getInt`. | [constructor](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L108-L114), [array generation](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L185-L191) |
| Type depth | Depth `3` when struct or arrays-of-arrays features are enabled; otherwise depth `1` | [type-depth choice](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L145-L153) |
| Basic 32-bit/bool types | `float`, `int`, `uint`, `bool`, optional vectors and matrices | [type candidates](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L234-L268) |
| 16-bit candidates | `uint16`, `int16`, `float16`, optional 16-bit vectors | [16-bit candidates](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L195-L218) |
| 8-bit candidates | `uint8`, `int8`, optional 8-bit vectors | [8-bit candidates](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L219-L233) |

## Support / Feature Requirements

The shared-layout base cases do not add an explicit Vulkan memory-model feature gate in the inspected support function. When
16-bit or 8-bit types are enabled, the test requires `VK_KHR_shader_float16_int8`; `16bit` additionally checks the
`shaderFloat16` member from the Vulkan 1.2 feature query, and `8bit` checks `shaderInt8`
[vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L347-L358).

## Verification Methods

During delayed initialization, every shared variable is flattened into reference entries and populated with generated literal
values [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L502-L519).

The generated compute shader declares shared-memory structures, writes the expected values, executes `barrier()` and
`memoryBarrier()`, compares every field through generated comparison functions, and increments a storage-buffer `passed` counter
only if all comparisons succeed [vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L271-L344).

The host creates a 4-byte storage buffer initialized to zero, dispatches one workgroup, invalidates the buffer, and passes only
when the counter equals `1`; otherwise it logs the observed and expected counts
[vktMemoryModelSharedLayoutCase.cpp](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L360-L488).

## Test Principles Observed

- Use randomized but deterministic seeds to cover many shared-memory type layouts while keeping case names stable.
- Flatten complex arrays/structs to compare every basic leaf value after synchronization.
- Separate root, 16-bit, and 8-bit variants so optional feature gates only affect cases that need them.

## Notes / Uncertainties

- `vktMemoryModelSharedLayoutCase.cpp` is helper-heavy and contains no standalone registration function in the inspected
  source, so no separate Level-3 page was created for it.
