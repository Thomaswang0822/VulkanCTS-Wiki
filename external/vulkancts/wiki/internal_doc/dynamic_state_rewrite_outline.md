# dynamic_state Rewrite Outline

## Scope

- Category: `dynamic_state`
- Old Level-2 page: `external/vulkancts/wiki/categories/dynamic_state.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/dynamic_state/`
- Source category directory: `external/vulkancts/modules/vulkan/dynamic_state/`

## Page Count

- Old Level-3 pages found: 10
- Registration-only dispatcher pages to fold into Level-2: 1 (`vktDynamicStateTests.cpp` is registration-only; it only creates the seven pipeline-construction-type subgroups at `vktDynamicStateTests.cpp#L74-L104` and calls `createChildren()` at `vktDynamicStateTests.cpp#L49-L66` to attach the implementation files as direct children)
- Implementation-bearing Level-3 pages to rewrite: 10
- Counted rewrite files for batching: 10
  - 0 Understanding Briefs (no page in this category is pre-flagged for brief-driven rewriting in this outline; briefs may be added per page during inspection if a page proves non-mechanical)
  - 10 rewritten Level-3 pages

Rationale for no automatic briefs in the outline: every implementation file in this category follows the shared `DynamicStateBaseClass` harness with a clear functional theme (one dynamic-state area per file), so a brief is not required for the mechanical page pattern. Whether a page needs an Understanding Brief is decided per-page during Phase 1 inspection; the outline only fixes the dispatcher decision and batch structure.

## Dispatcher Decision

- `vktDynamicStateTests.cpp` should NOT be rewritten because it is registration-only. Its sole role is to construct the seven pipeline-construction-type subgroups (`monolithic`, `pipeline_library`, `fast_linked_library`, `shader_object_unlinked_spirv`, `shader_object_unlinked_binary`, `shader_object_linked_spirv`, `shader_object_linked_binary`) and attach the implementation files as direct children through `createChildren()`. It contains no test cases of its own.
- Fold category-specific dispatcher facts into the rewritten Level-2 `dynamic_state` page:
  - direct category tree, including the seven pipeline-construction-type subgroups and the conditional `compute_transfer` child that appears only under `monolithic` and `shader_object_unlinked_spirv`;
  - subgroup names: `vp_state`, `rs_state`, `cb_state`, `ds_state`, `general_state`, `inheritance`, `image`, `discard`, `line_width`, `compute_transfer`;
  - source-to-family routing for each implementation file, including the shared `DynamicStateBaseClass` and `vktDynamicStateTestCaseUtil.hpp` harness.

## Batch 1 — Viewport/scissor, rasterization, color blend

Counted files: 3

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktDynamicStateVPTests.md` | No | Implementation file for `vp_state`; covers viewport, scissor, viewport_array plus mesh-shader variants under VulkanSC guards. Direct rewrite. |
| `vktDynamicStateRSTests.md` | No | Implementation file for `rs_state`; rasterization dynamic states plus mesh-shader variants. Direct rewrite. |
| `vktDynamicStateCBTests.md` | No | Implementation file for `cb_state`; color-blend dynamic state plus mesh-shader variants. Direct rewrite. |

## Batch 2 — Depth/stencil, general state, clear

Counted files: 3

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktDynamicStateDSTests.md` | No | Implementation file for `ds_state`; depth/stencil dynamic states plus mesh-shader variants. Direct rewrite. |
| `vktDynamicStateGeneralTests.md` | No | Implementation file for `general_state`; mixed dynamic states plus mesh-shader variants and the `double_static_bind` group omitted for shader-object construction types. Direct rewrite. |
| `vktDynamicStateClearTests.md` | No | Implementation file for the `image` subgroup; tests that image-manipulation commands (clear, blit, copy, resolve) do not interfere with dynamic state. Direct rewrite. |

## Batch 3 — Inheritance, discard, line width, compute/transfer

Counted files: 4

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktDynamicStateInheritanceTests.md` | No | Implementation file for `inheritance`; covers `VK_NV_inherited_viewport_scissor`, `VK_EXT_extended_dynamic_state` with-count variants, and `VK_EXT_nested_command_buffer` nested variants. CPU reference rasterization plus exact comparison. Direct rewrite. |
| `vktDynamicStateDiscardTests.md` | No | Implementation file for `discard`; covers `VK_EXT_discard_rectangles` and similar. Direct rewrite. |
| `vktDynamicStateLineWidthTests.md` | No | Implementation file for `line_width`; covers `VK_DYNAMIC_STATE_LINE_WIDTH` plus `DEVICE_CORE_FEATURE_WIDE_LINES`. Direct rewrite. |
| `vktDynamicStateComputeTests.md` | No | Implementation file for `compute_transfer`; registered only under `monolithic` and `shader_object_unlinked_spirv` construction types, covering extended dynamic state plus NV/EXT extensions. Direct rewrite. |

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `dynamic_state.md` as the compact Level-2 category gateway.
- Include folded dispatcher information: the seven pipeline-construction-type subgroups, the conditional `compute_transfer` registration, and the `image` subgroup naming clarification (image-manipulation commands, not image-related dynamic state).
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating the dynamic-state-type coverage table, parameter matrices, and verification mechanics from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.

## Notes on Inspection Order

- The first Level-3 page inspected for this category should be `vktDynamicStateVPTests.md` because it is the smallest, most representative example of the shared `DynamicStateBaseClass` + mesh-shader-variant pattern used by every other file in the category.
- The `vktDynamicStateBaseClass.cpp`/`.hpp` shared base and `vktDynamicStateTestCaseUtil.hpp` instance-factory template have no Level-3 pages; the rewritten Level-3 pages must reference them as supporting evidence when explaining resource setup, the `setDynamicStates()` flow, and the `InstanceFactory` template.
- The `vktDynamicStateComputeTests.cpp` file is the only one whose registration is conditional on pipeline-construction-type; its Level-3 page must state this explicitly and the Level-2 page must call it out in the registration tree.
- The `vktDynamicStateGeneralTests.cpp` file omits the `double_static_bind` group for shader-object construction types; this must be reflected accurately in its Level-3 page.