# Memory Model Tests

The Vulkan CTS `memory_model` category verifies Vulkan/SPIR-V memory-model behavior through generated synchronization tests,
structure-padding preservation checks, and randomized shared-memory layout checks. The inspected implementation is concentrated
in the `external/vulkancts/modules/vulkan/memory_model/` module and is registered as the top-level `memory_model` CTS category.

## Registration Entry Point

The Vulkan test package registers `memory_model` as a root child by passing `MemoryModel::createTests` to `addRootChild`
[vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1370-L1380). The VulkanSC package initialization also registers
`memory_model` in its root list [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1413-L1447). The factory is declared
in [vktMemoryModelTests.hpp](../../modules/vulkan/memory_model/vktMemoryModelTests.hpp#L30-L35) and implemented in
[vktMemoryModelMessagePassing.cpp](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2060-L2415).

## Subgroup Structure

The category root is constructed in `createTests(testCtx, name)`. The direct registered children observed in source are:

```text
memory_model
├── message_passing
├── write_after_read
├── transitive
├── padding
└── shared
```

| Subgroup | What it verifies | Evidence | Level-3 details |
|----------|------------------|----------|-----------------|
| `message_passing` | Release/acquire ordering where a payload write is made visible through guard synchronization before a partner payload read. | [registration and matrix](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2070-L2339) | [vktMemoryModelMessagePassing.md](../testfiles/memory_model/vktMemoryModelMessagePassing.md) |
| `write_after_read` | Read-before-partner-write hazards using the same main parameter matrix as `message_passing`. | [test-type cases](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2070-L2073), [write-after-read shader path](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L795-L814) | [vktMemoryModelMessagePassing.md](../testfiles/memory_model/vktMemoryModelMessagePassing.md) |
| `transitive` | Availability/visibility chains for device-scope compute message-passing cases. | [transitive registration](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2341-L2408), [transitive shader generation](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1075-L1327) | [vktMemoryModelMessagePassing.md](../testfiles/memory_model/vktMemoryModelMessagePassing.md) |
| `padding` | `std140` structure assignment must not corrupt destination padding bytes. | [delegated registration](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L360-L367) | [vktMemoryModelPadding.md](../testfiles/memory_model/vktMemoryModelPadding.md) |
| `shared` | Randomized shared-memory structure layouts write, synchronize, and compare every generated field. | [delegated registration](../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L330) | [vktMemoryModelSharedLayout.md](../testfiles/memory_model/vktMemoryModelSharedLayout.md) |

## File Inventory

| File | Documentation role | Notes |
|------|--------------------|-------|
| [vktMemoryModelTests.hpp](../../modules/vulkan/memory_model/vktMemoryModelTests.hpp) | Root factory declaration | Declares `createTests(testCtx, name)`. |
| [vktMemoryModelMessagePassing.cpp](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp) | Registration plus implementation | Builds the category root and the main generated synchronization families; delegates `padding` and `shared`. |
| [vktMemoryModelPadding.cpp](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp) | Registered implementation file | Builds `memory_model.padding.test`. |
| [vktMemoryModelPadding.hpp](../../modules/vulkan/memory_model/vktMemoryModelPadding.hpp) | Helper declaration | Declares `createPaddingTests`. |
| [vktMemoryModelSharedLayout.cpp](../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp) | Registered implementation file | Builds `memory_model.shared` and its layout-case families. |
| [vktMemoryModelSharedLayout.hpp](../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.hpp) | Helper declaration | Declares `createSharedMemoryLayoutTests`. |
| [vktMemoryModelSharedLayoutCase.cpp](../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp) | Helper implementation | Generates shared-layout shaders and executes shared-layout cases; no standalone registration was observed. |
| [vktMemoryModelSharedLayoutCase.hpp](../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.hpp) | Helper declarations | Declares shared-layout interfaces and case classes. |
| [CMakeLists.txt](../../modules/vulkan/memory_model/CMakeLists.txt#L7-L24) | Build inventory | Lists the source files compiled into the memory-model module. |

## Recurring Test Families and Themes

### Memory synchronization matrix

The largest family is a generated matrix under `message_passing` and `write_after_read`. Source arrays define two test types,
two API/memory-model modes, four data types, coherent/noncoherent payload modes, six synchronization forms, atomic write/RMW,
four scopes, payload/guard locality, payload/guard storage classes, and compute/vertex/fragment stages
[vktMemoryModelMessagePassing.cpp](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2070-L2167). The nested
registration loops instantiate the matrix and apply code-level pruning for unsupported or intentionally reduced combinations,
including workgroup-memory locality restrictions that are separate from stage/scope pruning
[vktMemoryModelMessagePassing.cpp](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2169-L2339).

### Transitive availability/visibility chains

`transitive` focuses on device-scope compute message passing. It fixes the test type to message passing, data type to `u32`,
and stage to compute while varying coherence, synchronization type, storage placement, and whether the visibility step is done
by the destination invocation or invocation `(0,0)` [vktMemoryModelMessagePassing.cpp](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2341-L2408).

### Padding preservation

`padding` uses explicit CPU-side padding arrays for 12-byte, 8-byte, and 4-byte padding structures, then copies matching
shader-side `std140` structures and checks that destination padding bytes remain at the initialized output value
[vktMemoryModelPadding.cpp](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L44-L133) and
[vktMemoryModelPadding.cpp](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L350-L355).

### Shared-memory layout coverage

`shared` generates deterministic randomized cases for scalar, vector, basic, array, arrays-of-arrays, nested-struct, and
nested-struct-with-array layouts, and registers the same seven families inside separate `16bit` and `8bit` groups whose cases
enable the corresponding type-generation feature bits [vktMemoryModelSharedLayout.cpp](../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L330).

## Recurring Parameter Dimensions

| Area | Dimensions | Evidence |
|------|------------|----------|
| Main synchronization matrix | Test type, core-vs-extension mode, data type, coherence, sync form, atomic operation kind, scope, payload locality/storage, guard locality/storage, stage. | [case arrays](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2070-L2167) |
| Matrix pruning | Excludes selected core11, workgroup-memory locality, stage/scope, control-barrier, RMW, non-32-bit, and 64-bit image combinations. | [filters](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2235-L2313) |
| Transitive matrix | Coherence, sync form, payload/guard locality and storage, and `nontransvis`/`transvis`. | [transitive loops](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2341-L2408) |
| Padding | Three `std140`-aligned structures, array length `3`, scalar values `1/2/3`, input padding `0xFE`, output padding `0x7F`. | [structures and constants](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L44-L75), [constants](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L242-L258) |
| Shared layout | Seven root layout families, repeated under `16bit` and `8bit`; 10 generated cases per family. | [shared registration](../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L330) |

## Recurring Support Requirements and Feature Gates

| Requirement | Applies to | Evidence |
|-------------|------------|----------|
| Vulkan 1.1 | Main generated `MemoryModelTestCase` variants. | [Vulkan 1.1 check](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L181-L186) |
| `vulkanMemoryModel` and `vulkanMemoryModelDeviceScope` | `ext` and device-scope extension-mode memory-model variants. | [memory-model feature checks](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L188-L199) |
| Subgroup basic, ballot, shuffle, and selected stage support | `subgroup` scope variants. | [subgroup checks](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L201-L239) |
| Integer and floating-point atomic features | `u64`, `f32`, and `f64` atomic variants. | [atomic feature checks](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L241-L305) |
| Availability/visibility chain feature | `transitive` variants. | [chain check](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L308-L309) |
| Buffer device address | Physical-storage-buffer variants. | [physical-buffer check](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L311-L313) |
| Vertex/fragment stores and atomics | Vertex and fragment stage variants. | [stage feature checks](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L315-L328) |
| `VK_KHR_vulkan_memory_model` | Padding test. | [padding support](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L225-L232) |
| `VK_KHR_shader_float16_int8`, `shaderFloat16`, `shaderInt8` | Shared-layout `16bit` and `8bit` variants. | [shared support](../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L347-L358) |

## Recurring Verification Methods

- Main synchronization tests use shader code to write a nonzero entry in a fail buffer whenever the observed value violates the
  expected payload/guard ordering. Host code scans that fail buffer after repeated dispatches/draws and fails on any nonzero
  entry [vktMemoryModelMessagePassing.cpp](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L953-L1004) and
  [vktMemoryModelMessagePassing.cpp](../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L1881-L2017).
- Padding tests compare the output structure values and explicit destination padding bytes against host-side expectations
  [vktMemoryModelPadding.cpp](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L99-L133) and
  [vktMemoryModelPadding.cpp](../../modules/vulkan/memory_model/vktMemoryModelPadding.cpp#L350-L355).
- Shared-layout tests generate comparison functions, compare every generated shared-memory leaf after `barrier()` and
  `memoryBarrier()`, increment a 4-byte pass counter only when all comparisons succeed, and require that counter to equal `1`
  on the host [vktMemoryModelSharedLayoutCase.cpp](../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L271-L344) and
  [vktMemoryModelSharedLayoutCase.cpp](../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L470-L488).

## Level-3 Documents

| Document | Coverage |
|----------|----------|
| [vktMemoryModelMessagePassing.md](../testfiles/memory_model/vktMemoryModelMessagePassing.md) | Category root registration, message-passing, write-after-read, transitive, and delegated children overview. |
| [vktMemoryModelPadding.md](../testfiles/memory_model/vktMemoryModelPadding.md) | `memory_model.padding.test`. |
| [vktMemoryModelSharedLayout.md](../testfiles/memory_model/vktMemoryModelSharedLayout.md) | `memory_model.shared` randomized shared-memory layout tests. |

## Scope and Uncertainties

- The audited scope relies on current source and mustpass evidence for exact registration, parameter matrices, feature gates,
  and verification behavior.
- A mustpass search found `dEQP-VK.memory_model` paths in `external/vulkancts/mustpass/main/vk-default/memory-model.txt`, but
  the inspected search did not find `dEQP-VKSC.memory_model` entries. The VulkanSC package source still registers the root
  category.
- The shared-layout helper source does not register a separate group, so it is treated as supporting evidence for
  [vktMemoryModelSharedLayout.md](../testfiles/memory_model/vktMemoryModelSharedLayout.md), not as its own Level-3 page.
