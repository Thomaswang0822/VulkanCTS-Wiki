# Merge Update Log

## Purpose

Historical change log for periodic updates from the official upstream Vulkan-GL-CTS repository
(https://github.com/KhronosGroup/VK-GL-CTS.git) into this wiki branch.

For each merge update, this log records:
- upstream Vulkan CTS source or mustpass changes;
- completed wiki categories reviewed because of those upstream changes;
- wiki files updated accordingly;
- reviewed categories that did not need wiki changes.

## 2026-05 Sync: upstream `main` into `vkcts-wiki`

### Git Baseline

- Integration branch: `merge_main_26-05-18`.
- Long-lived target branch: `vkcts-wiki`.
- Upstream range already handled: `634a3fc62d82c34de68c3b1add25e6b7f5777524..e6b2240610e7d1dcefd84c8c5c32f88306e05f87`.
- Merge commit after conflict resolution: `5143e893129c68c70b09070b39c8240a95c2d121`.
- Merge parents:
  - local wiki parent: `d021ba9bba2698d6c6f975a9d4181367b0594958`;
  - upstream main parent: `e6b2240610e7d1dcefd84c8c5c32f88306e05f87`.
- Only real merge conflict observed: [external/.gitignore](../../../.gitignore), resolved by accepting the upstream
  `main` side.

### Scope Decisions

- No added or deleted top-level Vulkan module directories were found under [modules/vulkan](../../modules/vulkan), so
  [README.md](../README.md) did not need category row additions or removals for this sync.
- Upstream source changes in not-started wiki categories were recorded for future category writing, but they did not
  require immediate user-facing wiki updates during this cleanup.
- Factual wiki refresh was limited to completed categories whose current Vulkan source or mustpass files showed stale
  registration paths, test families, parameters, support gates, verification logic, or scope notes.

### Mustpass and Validator Notes

- `renderpass.txt` under `mustpass/main/vk-default/` was deleted; current renderpass validation uses
  [renderpasses.txt](../../mustpass/main/vk-default/renderpasses.txt).
- Pipeline mustpass files moved into nested directories:
  - [monolithic.txt](../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt);
  - [shader-object-unlinked-spirv.txt](../../mustpass/main/vk-default/pipeline/shader-object-unlinked-spirv/shader-object-unlinked-spirv.txt).
- [verify_registration_paths.py](../../../../.agents/skills/wiki-analyzer/scripts/verify_registration_paths.py) was
  updated so pipeline/category mustpass discovery uses recursive `*.txt` discovery instead of top-level-only globbing.
- Deleted ASTC mustpass files did not invalidate existing image wiki claims because `general_layout.astc_sample` paths
  remained covered by [general-layout.txt](../../mustpass/main/vk-default/image/general-layout.txt).

### Completed Categories Reviewed

Categories with user-facing wiki updates:
- [api.md](../categories/api.md)
- [binding_model.md](../categories/binding_model.md)
- [image.md](../categories/image.md)
- [memory.md](../categories/memory.md)
- [pipeline.md](../categories/pipeline.md)
- [query_pool.md](../categories/query_pool.md)
- [renderpasses.md](../categories/renderpasses.md)
- [ycbcr.md](../categories/ycbcr.md)

Categories reviewed with no user-facing wiki content update required:
- [draw.md](../categories/draw.md)
- [dynamic_state.md](../categories/dynamic_state.md)
- [rasterization.md](../categories/rasterization.md)
- [shader_object.md](../categories/shader_object.md)
- [synchronization.md](../categories/synchronization.md) and [synchronization2.md](../categories/synchronization2.md)
- [texture.md](../categories/texture.md)

Completed categories not touched by upstream source changes in this sync:
- [info.md](../categories/info.md)
- [imageless_framebuffer.md](../categories/imageless_framebuffer.md)
- [image_processing.md](../categories/image_processing.md)
- [fragment_operations.md](../categories/fragment_operations.md)
- [clipping.md](../categories/clipping.md)
- [multiview.md](../categories/multiview.md)
- [geometry.md](../categories/geometry.md)

### Notable User-Facing Updates

- `api`: refreshed stale source facts in blitting, device-address command, fill-buffer, maintenance3, and object
  management docs; repaired validator hygiene/link issues in related Level-3 pages.
- `binding_model`: refreshed buffer-device-address, descriptor-heap, and unused-invalid-descriptor docs.
- `image`: refreshed depth/stencil separate support checks, sparse host-image-copy fence waits, swapchain mutable-image
  synchronization, non-uniform-offset compute-stage implicit-LOD pruning, and host-image-copy hierarchy normalization.
- `memory`: refreshed Vulkan SC parent-process memory-type selection behavior and repaired stale binding source links.
- `pipeline`: refreshed nested mustpass mapping and stale blend, library, and multisample-resolve-maintenance10 facts.
- `query_pool`: refreshed Vulkan SC behavior for `early` discard cases.
- `renderpasses`: documented new `single_sample_clear` and `density_formula` coverage and removed stale legacy
  `renderpass.txt` assumptions.
- `ycbcr`: documented new non-SC `VK_EXT_descriptor_buffer` and `VK_EXT_descriptor_heap` variants for `format` and
  `plane_view` coverage.

### Validation Summary

- Category-scoped link validation passed for every edited/reviewed completed category.
- Registration-path validation passed for every edited/reviewed completed category.
- User-facing wiki link sweep over [categories](../categories) and [testfiles](../testfiles) passed after cleanup.
- Whole-wiki link validation still reports expected non-actionable findings from not-yet-created [README.md](../README.md)
  category links and temporary/internal tracker evidence links.
