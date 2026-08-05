# compute Rewrite Outline

## Scope

- Category: `compute`
- Old Level-2 page: `external/vulkancts/wiki/categories/compute.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/compute/`
- Source category directory: `external/vulkancts/modules/vulkan/compute/`

## Page Count

- Old Level-3 pages found: 8
- Registration-only dispatcher pages to fold into Level-2: 1 (`vktComputeTests.cpp` is registration-only; its `createTests()` at `vktComputeTests.cpp#L68-L85` creates three pipeline-construction-type subgroups (`pipeline`, `shader_object_spirv`, `shader_object_binary`) and calls `createChildren()` at `vktComputeTests.cpp#L48-L64` to attach the seven implementation factories. The old page `vktComputeTests.md` is a navigation-only dispatcher page and should be folded into the rewritten Level-2 page, not rewritten as a Level-3 page.)
- Implementation-bearing Level-3 pages to rewrite: 7
- Counted rewrite files for batching: 11
  - 4 Understanding Briefs
  - 7 rewritten Level-3 pages

Brief pre-judgment rationale: basic compute, cooperative matrix, indirect dispatch, and workgroup-memory explicit layout all involve generated artifacts, nontrivial synchronization, complex concepts, or multiple distinct mechanisms. The null-constant delegated test, the built-in-variable test, and the zero-initialize test have clear core mechanisms that can be summarized in a few sentences.

## Dispatcher Decision

- `vktComputeTests.cpp` should NOT be rewritten because it is registration-only. Its sole role is to construct the three pipeline-construction-type subgroups (`pipeline`, `shader_object_spirv`, `shader_object_binary`) and attach the implementation factories through `createChildren()`. It contains no test cases of its own. The `shader_object_spirv` and `shader_object_binary` subgroups are non-VulkanSC only.
- Fold category-specific dispatcher facts into the rewritten Level-2 `compute` page:
  - direct category tree: three construction-type subgroups, each with the same child factories (`basic`, `64b_indexing`, `device_group`, `cooperative_matrix` non-VulkanSC only, `indirect_dispatch`, `builtin_var`, `zero_initialize_workgroup_memory`, `workgroup_memory_explicit_layout` non-VulkanSC only);
  - subgroup names and source-to-family routing for each implementation file;
  - note that `vktComputeTestsUtil.cpp` is shared utility infrastructure with no Level-3 page.

## Batch 1 — Basic compute, cooperative matrix, indirect dispatch

Counted files: 7

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktComputeBasicComputeShaderTests.md` | Yes | Covers `basic`, `64b_indexing`, and `device_group` with many themes: buffer/image side effects, barriers, shared variables, empty workgroups, max local sizes, compute-only queues, replicated composites, Amber regressions, undefined values, dispatch sequencing, and large SSBO indexing. Generates shaders mapping `gl_NumWorkGroups`/`gl_WorkGroupSize`/`gl_GlobalInvocationID` to buffer elements. The theme count risks source-navigation documentation. Hits generated-artifact and inability-to-summarize brief conditions. |
| `vktComputeCooperativeMatrixTests.md` | Yes | `cooperative_matrix` (non-VulkanSC only). Varies use type, scope, test type, subgroup-size mode, component type, storage class, layout, and address method. Cooperative matrix is a complex concept and the generated test matrix is large. Hits generated-test-matrix and complex-concept brief conditions. |
| `vktComputeCooperativeMatrixOpConstantNullTests.md` | No | Delegated nested file that adds `op_constant_null` and its `null_a`/`null_b`/`null_c`/`null_r` children under `cooperative_matrix`. The core property (null constant in cooperative matrix op), execution flow, and validation are clear. Direct rewrite. |
| `vktComputeIndirectComputeDispatchTests.md` | Yes | `indirect_dispatch`. Covers uploaded and compute-generated indirect dispatch command buffers with offsets, empty commands, multi-dispatch, and device-address commands. Compute-generated command buffers require a compute-to-indirect barrier. Hits generated-artifact and nontrivial-synchronization brief conditions. |

## Batch 2 — Builtin vars, zero-init, explicit layout

Counted files: 4

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktComputeShaderBuiltinVarTests.md` | No | `builtin_var`. Compute built-ins for workgroup counts, IDs, sizes, global IDs, local IDs, and local invocation index. Result-buffer comparison. Core mechanism (write builtin values to buffer, compare against expected) is clear. Direct rewrite. |
| `vktComputeZeroInitializeWorkgroupMemoryTests.md` | No | `zero_initialize_workgroup_memory`; `VK_KHR_zero_initialize_workgroup_memory`. Core mechanism (workgroup memory should be zero-initialized) is clear; variants (types, composites, max dimensions, spec constants, repeated creation) are parameter dimensions, not distinct mechanisms. Direct rewrite. |
| `vktComputeWorkgroupMemoryExplicitLayoutTests.md` | Yes | `workgroup_memory_explicit_layout` (non-VulkanSC only); `VK_KHR_workgroup_memory_explicit_layout`. Multiple distinct mechanisms: layout aliasing, zeroing, padding, size, copy-memory, and zero-initialize-extension interactions. The aliasing concept is non-trivial. Hits complex-concept, multiple-distinct-mechanisms, and extension-interaction brief conditions. |

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `compute.md` as the compact Level-2 category gateway.
- Include folded dispatcher information: the three construction-type subgroups, the non-VulkanSC-only guards on `cooperative_matrix` and `workgroup_memory_explicit_layout`, and the shared child-factory list.
- Note that `vktComputeTestsUtil.cpp` is shared utility infrastructure with no Level-3 page.
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating parameter matrices, support gates, and verification mechanics from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.

## Notes on Inspection Order

- The first Level-3 page inspected for this category should be `vktComputeBasicComputeShaderTests.md` because it is the largest implementation file, covers the `basic`/`64b_indexing`/`device_group` subgroups, and establishes the shared compute-dispatch and buffer-comparison pattern used by other files.
- The `vktComputeTestsUtil.cpp` utility file has no Level-3 page; the rewritten Level-3 pages must reference it as supporting evidence when explaining buffer/image helpers and shared compute infrastructure.
- `vktComputeCooperativeMatrixOpConstantNullTests.cpp` is a delegated nested registration source under `cooperative_matrix`; it has a Level-3 page because it registers the `op_constant_null` subtree even though it is not a root-level child. The Level-3 page must state the delegation relationship clearly.
- The `shader_object_spirv` and `shader_object_binary` construction-type subgroups reuse the same child factories as `pipeline`, but several Amber-based or extension-heavy branches are conditionally absent; the Level-2 page must state this and the Level-3 pages must document per-file shader-object exclusions.