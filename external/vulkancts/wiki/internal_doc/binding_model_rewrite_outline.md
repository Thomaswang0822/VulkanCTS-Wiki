# binding_model Rewrite Outline

## Scope

- Category: `binding_model`
- Old Level-2 page: `external/vulkancts/wiki/categories/binding_model.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/binding_model/`
- Source category directory: `external/vulkancts/modules/vulkan/binding_model/`

## Page Count

- Old Level-3 pages found: 15
- Registration-only old Level-3 pages to fold into Level-2: 0
- Implementation-bearing Level-3 pages to rewrite: 15
- Registration-only root source files represented directly in Level-2: 1 (`vktBindingModelTests.cpp`, not one of the 15 old Level-3 pages)
- Counted rewrite files for batching: 30
  - 15 Understanding Briefs
  - 15 rewritten Level-3 pages

## Dispatcher Decision

- None of the 15 old Level-3 pages is registration-only; all 15 cover implementation-bearing source and remain Level-3 rewrite targets.
- `vktBindingModelTests.cpp` has no old Level-3 page and should NOT receive one because it is registration-only.
- Fold category-specific dispatcher facts into the rewritten Level-2 `binding_model` page:
  - direct category tree;
  - test family names: `shader_access`, `descriptor_update`, `descriptorset_random`, `descriptor_copy`, `buffer_device_address`, `dynamic_offset`, `mutable_descriptor`, `descriptor_buffer`, `descriptor_combination`, `push_constant_bank`, `descriptor_heap`, `stages`, `inline_uniform_blocks`, and `unused_invalid_descriptor`;
  - source-to-family routing;
  - the Vulkan and Vulkan SC registration split.

## Batch 1 — Descriptor access and update paths

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktBindingShaderAccessTests.md` | Yes | Generated shaders, descriptor-set layouts, primary and secondary command buffers, update methods, descriptor types, stages, and shader-visible validation require a complete execution model. |
| `vktBindingDescriptorSetRandomTests.md` | Yes | Randomized descriptor-set layouts, generated shaders, multi-set resource binding, stage variation, and result checking require a concrete representative case. |
| `vktBindingDescriptorUpdateTests.md` | Yes | The page combines empty-binding, samplerless, randomized update, graphics/compute, and delegated acceleration-structure behavior, so the behavior axis and page boundary need explicit analysis. |
| `vktBindingDescriptorUpdateASTests.md` | Yes | Acceleration-structure descriptor updates combine ray-query and ray-tracing shaders, generated resources, descriptor writes/copies, synchronization, and host validation. |

## Batch 2 — Copy, inline, invalid, and dynamic-offset paths

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktBindingDescriptorCopyTests.md` | Yes | Descriptor copies span compute, graphics, update-after-bind, descriptor-type matrices, immutable samplers, generated shaders, and shader-visible checking. |
| `vktBindingDescriptorInlineUniformTests.md` | Yes | Inline uniform block writes and copies vary byte size and source/destination offsets, then expose the resulting bytes through shader execution and host checks. |
| `vktBindingUnusedInvalidDescriptorTests.md` | Yes | The distinction between unused, invalid, copied, and actually accessed descriptors depends on descriptor validity rules, generated resources, shader access, and exact validation behavior. |
| `vktBindingDynamicOffsetTests.md` | Yes | Amber cases and generated two-pipeline cases combine layout compatibility, pipeline reuse, push-constant ordering, descriptor-set selection, dynamic offsets, and output-buffer validation. |

## Batch 3 — Alternative descriptor storage and extension interactions

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktBindingDescriptorBufferTests.md` | Yes | The large `VK_EXT_descriptor_buffer` matrix covers traditional and sparse residency modes, descriptor encoding and binding, many resource types, generated shaders, synchronization, and readback. |
| `vktBindingMutableTests.md` | Yes | Mutable and non-mutable bindings, arrays, aliasing, descriptor-type switching, stage variation, generated shaders, and feature-driven pruning require a stable resource and behavior model. |
| `vktBindingDescriptorCombinationTests.md` | Yes | Its two cases exercise distinct cross-extension mechanisms: legacy and descriptor-buffer state interaction, and capture-replay combined with custom border color. |
| `vktBindingPushConstantBankTests.md` | Yes | Basic push-constant banks and descriptor-heap push-data paths use different command mechanisms, generated shaders, bank/member layouts, and shader-visible validation. |

## Batch 4 — Device addresses, descriptor heaps, and bind-point stages

Counted files: 6

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktBindingBufferDeviceAddressTests.md` | Yes | Physical storage buffer pointers, pointer depth, conversions, storage, buffer topology, capture replay, layouts, stages, memory-model access chains, and offsets form a shader-heavy generated matrix. |
| `vktBindingDescriptorHeapTests.md` | Yes | The large descriptor-heap implementation spans many distinct registered behaviors, shader mappings, heap state changes, concurrent access, graphics/compute paths, generated artifacts, and specialized validation. |
| `vktBindingStagesTests.md` | Yes | Although the leaf inventory is small, each case combines descriptor updates from different pipeline bind points, generated compute/graphics shaders, resource binding, command ordering, and result comparison. |

## Level-3 Output Naming

Drop the fixed `vktBinding` prefix and `Tests` suffix consistently:

| Old page | Rewritten page |
|---|---|
| `vktBindingShaderAccessTests.md` | `ShaderAccess.md` |
| `vktBindingDescriptorUpdateTests.md` | `DescriptorUpdate.md` |
| `vktBindingDescriptorUpdateASTests.md` | `DescriptorUpdateAS.md` |
| `vktBindingDescriptorSetRandomTests.md` | `DescriptorSetRandom.md` |
| `vktBindingDescriptorCopyTests.md` | `DescriptorCopy.md` |
| `vktBindingBufferDeviceAddressTests.md` | `BufferDeviceAddress.md` |
| `vktBindingDynamicOffsetTests.md` | `DynamicOffset.md` |
| `vktBindingMutableTests.md` | `Mutable.md` |
| `vktBindingDescriptorBufferTests.md` | `DescriptorBuffer.md` |
| `vktBindingDescriptorCombinationTests.md` | `DescriptorCombination.md` |
| `vktBindingPushConstantBankTests.md` | `PushConstantBank.md` |
| `vktBindingDescriptorHeapTests.md` | `DescriptorHeap.md` |
| `vktBindingStagesTests.md` | `Stages.md` |
| `vktBindingDescriptorInlineUniformTests.md` | `DescriptorInlineUniform.md` |
| `vktBindingUnusedInvalidDescriptorTests.md` | `UnusedInvalidDescriptor.md` |

Each brief uses the rewritten filename plus `_brief.md`.

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `external/vulkancts/wiki/categories/binding_model.md` in place as the compact Level-2 category gateway. This user-approved Level-2 operation is the exception to the new-file preservation rule; obsolete Level-3 pages still remain untouched.
- Include folded dispatcher information from `vktBindingModelTests.cpp`.
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating detailed shader walkthroughs, parameter matrices, and validation mechanics from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.
