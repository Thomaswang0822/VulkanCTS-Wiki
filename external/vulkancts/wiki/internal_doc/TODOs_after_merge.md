# TODOs After Merge — 2026-09-10 Sync

## 1. Baseline (verified)

- Integration branch: `merge_main_26-09-10`.
- Long-lived target branch: `vkcts-wiki`.
- Merge commit: `4bfe03344bbfbab939dcb0232196a8d9b4343e89` (`Merge branch 'main' into merge_main_26-09-10`).
- Merge parents:
  - local wiki parent: `4cb10a0ee5da3f43582293ef9a47976035d14bc0`;
  - upstream `main` parent: `659bbe6987197b4ff7ac20011261b92009286100`.
- Previous integrated upstream commit (`START`): `cf7edb26d3be2d8763595ed08fdc41f3c1b1966f`.
- New upstream commit (`END`): `659bbe6987197b4ff7ac20011261b92009286100`.
- `git merge-base START END` == `START`, so the range is contiguous with no gap from the previous sync.
- `main` tip equals `END`; 28 upstream commits; 74 changed paths (5285 insertions, 1258 deletions).
- Delta artifact: [git_diff_stat.txt](git_diff_stat.txt) (matches `git diff --stat` and
  `git diff --name-status --find-renames`; no renames or deletions in the range).
- Baseline validator state before any sync edit: structure PASS and registration PASS for every affected
  category; source line-reference sweep reported 177 errors, all pointing into files touched by this range.

## 2. Classification of the 74 changed paths

### A — unrelated to the Vulkan CTS wiki (recorded, no follow-up)

| Path | Reason |
| --- | --- |
| `AndroidGen.bp`, `AndroidKhronosCTSGen.bp` | Android build wiring for two new source files only. |
| `android/cts/main/vk-main-2026-03-01/{dgc,fragment-shading-rate,renderpasses,robustness}.txt` | Android case-list mirrors of the same mustpass additions; the wiki tracks `external/vulkancts/mustpass`. |
| `external/vulkancts/framework/vulkan/generated/vulkansc/vkKnownConformanceVersions.inl` | Generated SC conformance-version table trimmed; no wiki claim depends on the list. |

### B — indirect/shared impact, inspected individually

| Path | Decision | Evidence |
| --- | --- | --- |
| `framework/common/tcuCommandLine.{cpp,hpp}` | update `glsl/AmberGlslTests.md` | Adds `--deqp-amber-test` and `--deqp-amber-list-file`, and `--deqp-amber*` overrides `--deqp-case*` in `CaseListFilter`. |
| `external/vulkancts/modules/vulkan/vktTestPackage.{cpp,hpp}`, `vktTestPackageEntry.cpp` | update `glsl/AmberGlslTests.md` | New `AmberTestPackage` registered as top-level `dEQP-VK-amber` package; also `TestCaseExecutor::init` result/`beginTest` hygiene fixes. |
| `external/vulkancts/README.md` | no wiki update | Only documents the two new amber CLI options. |
| `framework/common/tcuTexture.{cpp,hpp}` | no wiki update | Adds a `TextureLevel(format, IVec3)` convenience constructor; no page cites this constructor. |
| `external/vulkancts/framework/vulkan/vkDeviceFeatures.{cpp,hpp}`, `generated/{vulkan,vulkansc}/vkDevice{Features,Properties}.inl`, `scripts/gen_framework.py` | no wiki update | Generated `sTypeToBlobStructMap` plus `getBlobStructFeatureList/getBlobStructPropertyList` reverse lookup; used only by the DevCaps self-check. |
| `external/vulkancts/modules/vulkan/vktContextManager.cpp` | no wiki update | `DevCaps::verifyFeature` now resolves blobs by absorbed feature instead of API version; internal self-check only. |
| `external/vulkancts/modules/vulkan/CMakeLists.txt` | no wiki update | Adds `include_directories(.)`; build wiring only. |
| `external/vulkancts/modules/vulkan/{device_generated_commands,renderpass}/CMakeLists.txt` | feed into C (`dgc`, `renderpasses`) | Registers the two new source files. |
| `external/vulkancts/modules/vulkan/shaderexecutor/vktShaderExpectAssumeTests.cpp` | feed into C (`glsl`) | Shared `VkShaderExecutor` area is unchanged; the expect/assume test source changed and `glsl/ShaderExpectAssumeTests.md` references it. |

### C — direct category impact

| Wiki category | Upstream evidence | Decision |
| --- | --- | --- |
| `renderpasses` | new `vktDynamicRenderingSuspendResumeTestsUtil.{cpp,hpp}` (+1439), `vktRenderPassCustomResolveTests.cpp` (+225), `renderpasses.txt` +170 (`custom_resolve.suspend_resume*`, `att_index_change*`, `mix_multi_upload_multi_resolve_*_remap_first`), `mixed_sample_count_subpasses` in renderpass1/renderpass2 (+2 vk-default, +2 vksc), new renderpass2/dynamic_rendering extension checks | update |
| `fragment_shading_rate` | `renderpass2.monolithic.ds_baselayer.*` (+160 vk-default, +80 vksc), `vktFragmentShadingRateBasic.cpp` ±49 | update |
| `dgc` | new `vktDGCComputePushIndexHeapTestsExt.{cpp,hpp}` (364 lines), `dgc.txt` +1 (`dgc.ext.compute.push_index_heap.stage_compute`), `vktDGCTests.cpp` registration | update (new page) |
| `robustness` | `bind_index_buffer2.type.*` uint8/uint16 variants (+14), `vktRobustnessIndexAccessTests.cpp` ±230, `vktRobustnessBufferAccessTests.cpp` ±2 | update |
| `wsi` | "Check requirements in checkSupport, part 13" across 15 WSI sources | update (support-gate facts + 117 stale line references) |
| `pipeline` | attachment-feedback-loop layout, extended dynamic state depth-clipping, push-descriptor `incremental_updates`, custom border-color component-only sampler tests | update |
| `transform_feedback` | `vktTransformFeedbackSimpleTests.cpp` ±12 | update |
| `memory` | watchdog touch in `vktMemoryAllocationTests.cpp` | update |
| `ssbo` | OOM handling and 32-bit build fixes in `vktSSBOLayoutCase.cpp` | update |
| `glsl` | `vktShaderExpectAssumeTests.cpp` ±16; amber runner CLI/package | update |
| `api` | duplicated used bit in `vktApiCopiesAndBlittingUtil.hpp` | verify, likely no wiki update |
| `binding_model` | descriptor-heap alignment, `incremental_updates` push descriptor, invalid-descriptor flush | verify, likely no wiki update |
| `compute` | `vktComputeBasicComputeShaderTests.cpp` +5 | verify, likely no wiki update |
| `cooperative_vector` | missing feature/property checks | verify, likely no wiki update |
| `query_pool` | object reservation count early-out fix | verify |
| `sc` | shared suspend/resume util is built into the VKSC render-pass source list; vksc mustpass gained `mixed_sample_count_subpasses` | verify only |

## 3. Work queue

### Mechanical (lead)

- [ ] Apply source line-reference repairs for the 177 findings (10 page groups + `unresolved_findings/wsi.md`);
      handle out-of-bounds findings individually because the referenced content shrank.

### Category content work (one canonical page per worker)

- [ ] `renderpasses` / `CustomResolve.md` — suspend/resume and remap-first custom resolve coverage.
- [ ] `renderpasses` / `MultisampleResolve.md` — `mixed_sample_count_subpasses`.
- [ ] `renderpasses` gateway (lead) — navigation for the above.
- [ ] `fragment_shading_rate` / `AttachmentRate.md` + gateway — `ds_baselayer` family.
- [ ] `dgc` / new `ComputePushIndexHeapExt.md` + gateway — DGC descriptor-heap push-index path.
- [ ] `robustness` / `IndexAccess.md` — 8-bit and 16-bit index-buffer robustness cases.
- [ ] `wsi` gateway — `checkSupport` requirement checks across the WSI group.
- [ ] `pipeline` / `AttachmentFeedbackLoopLayout.md` — support-check and layout changes.
- [ ] `pipeline` / `PushDescriptor.md` — `incremental_updates` fix.
- [ ] `pipeline` / `Sampler.md` — custom border-color component-only tests.
- [ ] `pipeline` / `ExtendedDynamicState.md` — depth-clipping verification fix.
- [ ] `transform_feedback` / `Simple.md` — source changes plus 9 stale references.
- [ ] `memory` / `Allocation.md` — watchdog touch during large allocations.
- [ ] `ssbo` / `SSBOLayoutTests.md` — 64-bit indexing OOM handling.
- [ ] `glsl` / `AmberGlslTests.md` — amber CLI options and `dEQP-VK-amber` package.
- [ ] `glsl` / `ShaderExpectAssumeTests.md` — expect/assume source changes.
- [ ] verify-only: `api`, `binding_model`, `compute`, `cooperative_vector`, `query_pool`, `sc`.

### Validation

- [ ] Per-category English structure, registration, and link checks after edits.
- [ ] Whole-wiki structure + registration sweep.
- [ ] Source line-reference sweep back to zero.
- [ ] Lookup DB: affected-category builds, full rebuild, lookup tests, configured mustpass coverage.
- [ ] `git diff --check`.

### Boundary

- Chinese synchronization is **not** authorized yet; `vkcts-wiki-pages/` must stay untouched.
