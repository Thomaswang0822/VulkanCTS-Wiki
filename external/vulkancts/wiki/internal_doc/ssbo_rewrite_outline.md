# ssbo Rewrite Outline

## Scope

- Category: `ssbo`
- Old Level-2 page: `external/vulkancts/wiki/categories/ssbo.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/ssbo/`
- Source category directory: `external/vulkancts/modules/vulkan/ssbo/`

## Page Count

- Old Level-3 pages found: 3
- Registration-only dispatcher pages to fold into Level-2: 0
- Implementation-bearing Level-3 pages to rewrite: 3
- Counted rewrite files for batching: 5
  - 2 Understanding Briefs
  - 3 rewritten Level-3 pages

Brief pre-judgment rationale: the SSBO layout verification flow generates compute shaders, computes reference layouts, dispatches compute, and compares device-written data with reference data — this is generated-artifact + resource-layout + descriptor-binding territory. The nested unsized-array page adds descriptor-array nesting and guard-zone validation on top. The corner-case crash regression is the only mechanical page.

## Dispatcher Decision

- `vktSSBOLayoutTests.cpp` should be rewritten because it has implementation in addition to registration. The file owns both the `createTests()` category dispatcher entry point at `vktSSBOLayoutTests.cpp#L2235-L2255` and the `SSBOLayoutTests` class whose `init()` at `vktSSBOLayoutTests.cpp#L1297-L2188` registers the `layout`, `readonly`, and `phys` families. The `unsized_array_length` family is also registered in this file through `createUnsizedArrayTests()`. The file delegates only `corner_case` to `vktSSBOCornerCase.cpp` and the `nested_unsized_arrays` leaf to `vktSSBOLayoutNestedUnsizedArraysTests.cpp`.
- Fold category-specific dispatcher facts into the rewritten Level-2 `ssbo` page:
  - direct category tree: `layout`, `unsized_array_length`, `readonly`, `phys`, `corner_case`;
  - subgroup names and source-to-family routing: `layout`/`readonly`/`phys` → `SSBOLayoutTests` class in `vktSSBOLayoutTests.cpp`; `unsized_array_length` → `createUnsizedArrayTests()` in `vktSSBOLayoutTests.cpp` plus `nested_unsized_arrays` leaf delegated to `vktSSBOLayoutNestedUnsizedArraysTests.cpp`; `corner_case` → `createSSBOCornerCaseTests()` in `vktSSBOCornerCase.cpp`;
  - note that `vktSSBOLayoutCase.cpp` is shared execution infrastructure with no Level-3 page.

## Batch 1 — All implementation-bearing Level-3 pages

Counted files: 5

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSSBOLayoutTests.md` | Yes | Hybrid registration + implementation file. Generates compute shaders via `generateComputeShader()`, computes reference layouts, dispatches compute, verifies a shader-side pass counter, and compares device-written data with reference data. The `m_readonly`/`m_phys` mode switches and the `phys` path's push-constant buffer-device-address flow add nontrivial descriptor binding. Hits generated-artifact, resource-layout, and descriptor-binding brief conditions. |
| `vktSSBOCornerCase.md` | No | Delegated implementation file for `corner_case.long_shader_bitwise_and`; pass condition is that the buffer-reference stress dispatch does not crash. The core property, execution flow, validation rule, and failure meaning are clear. Direct rewrite. |
| `vktSSBOLayoutNestedUnsizedArraysTests.md` | Yes | Delegated leaf implementation file appended under `unsized_array_length.nested_unsized_arrays`. Varies generated struct shape, descriptor-array length/stride, and guard-zone-protected root array writes. Requires `runtimeDescriptorArray` and `shaderStorageBufferArrayNonUniformIndexing`. Hits generated test-matrix and nontrivial descriptor-binding brief conditions. |

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `ssbo.md` as the compact Level-2 category gateway.
- Include folded dispatcher information: the five direct children, the `SSBOLayoutTests` mode switches (`m_readonly`, `m_phys`), and the two delegated leaves.
- Note that `vktSSBOLayoutCase.cpp` is shared execution infrastructure (reference layout computation, compute-shader generation, dispatch, result comparison) with no Level-3 page.
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating parameter matrices, support gates, and verification mechanics from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.

## Notes on Inspection Order

- The first Level-3 page inspected for this category should be `vktSSBOLayoutTests.md` because it owns the dispatcher entry point and the `SSBOLayoutTests` class that controls `layout`, `readonly`, and `phys`. The `SSBOLayoutCase::checkSupport()` and `SSBOLayoutCaseInstance::iterate()` shared flow in `vktSSBOLayoutCase.cpp` must be understood before rewriting any of the three pages.
- The `vktSSBOLayoutCase.cpp`/`.hpp` files define the `LayoutFlags`, access flags, relaxed-layout flags, storage-size flags, and descriptor-indexing flags used by every layout case; the rewritten Level-3 pages must reference them as supporting evidence.
- Mustpass inspection confirms the five direct `ssbo` children in `vk-default/ssbo.txt` and `vksc-default/ssbo.txt`; the Level-2 page must reflect the Vulkan SC 64-bit-indexing exclusion accurately.