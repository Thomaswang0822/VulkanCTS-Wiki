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

- [x] Source line-reference repairs applied: 161 symbol-range repairs (mechanical, checker-proposed spans) + 16
      out-of-bounds references resolved individually (the WSI support refactor shortened several files, so the
      referenced functions moved and some referenced ranges shrank). Whole-wiki sweep now reports
      `errors=0 warnings=0 findings=0`.
      Individually resolved: `glsl/ShaderExpectAssumeTests.md` factory (`createShaderExpectAssumeTests` now
      `#L1511-L1514`); `wsi/ColorSpaceTests.md` (`surfaceFormatRenderTests` `#L657-L675`, `createColorSpaceTests`
      `#L696-L709`, `createColorspaceCompareTests` `#L711-L726`); `wsi/DisplayTimingTests.md`
      (`createDisplayTimingTests` `#L1085-L1114`); `wsi/FullScreenExclusiveTests.md` (`#L595-L614`);
      `wsi/PresentIdWaitTests.md` (`#L1465-L1483`); plus the matching briefs.
- [x] `robustness.md` gateway: dispatcher range `#L61-L99` -> `#L61-L101` and the new `bind_index_buffer2` `type` node
      recorded in the family summary.

### Category content work (one canonical page per worker)

- [x] `renderpasses` / `MultisampleResolve.md` — `mixed_sample_count_subpasses` documented (tree gained the
      `mixed_sample_count` group; matrix-shaped families and the fixed group are now separated).
- [x] `robustness` / `IndexAccess.md` + brief — narrow-index correctness, new `type` node leaves, `indexTypeUint8` gate.
- [x] `renderpasses` / `CustomResolve.md` — suspend/resume registration and the `_remap_first` resolve-attachment
      rewrites documented; registration block `#L7168-L7194` and the primary/partial-secondary gate
      `#L7168-L7176` verified against current source.
- [x] `fragment_shading_rate` gateway + `Basic.md` — `ds_baselayer` and `ds_baselevel_baselayer` families.
- [x] `dgc` — new page `ComputePushIndexHeapExt.md` for `dgc.ext.compute.push_index_heap.stage_compute` + gateway rows.
- [x] `wsi` gateway and support-gate statements across 14 Level-3 pages (15 sources reviewed).
- [x] `pipeline` / `AttachmentFeedbackLoopLayout.md`, `PushDescriptor.md`, `Sampler.md`, `ExtendedDynamicState.md`.
- [x] `transform_feedback` / `Simple.md`; `memory` / `Allocation.md`; `ssbo` / `SSBOLayoutTests.md`.
- [x] `glsl` / `AmberGlslTests.md` (amber CLI + new `dEQP-VK-amber` package) and `ShaderExpectAssumeTests.md`.
- [x] verify-only: `api`, `binding_model`, `compute`, `cooperative_vector`, `query_pool`, `sc`. `api`, `binding_model`,
      `compute`, and `sc` needed no content change; `cooperative_vector` (stage store/atomic gates) and `query_pool`
      (queue-result collection and reservation count) did receive statements.
- [x] `renderpasses` gateway — `mixed_sample_count_subpasses` row, `custom_resolve` suspend/resume and `_remap_first`
      additions, and a Category Note for `vktDynamicRenderingSuspendResumeTestsUtil.{cpp,hpp}`.
- [x] `CTS_Framework.md` section 1.3 "Sibling Top-Level Packages" — `dEQP-VK-amber` and `dEQP-VK-experimental`
      descriptors, `AmberTestPackage::init()`, `pathToTestName()`, and the `CaseListFilter` override.

Note: work produced before the interruption was committed by the user as `86b1ea2b8a`
("Update sync: init + some progress"). The four worker assignments listed as re-dispatched had not written any
page content at that point; the mechanical sweep, `MultisampleResolve.md` and `IndexAccess.md` did land.
The user's own saved inputs `_tmp_cr_diff.txt` and `_tmp_mp_diff.txt` are now tracked in `internal_doc/`;
they were not created or removed by this workflow.

### Line-reference audit beyond the mechanical sweep

`check_line_refs.py` reports only `RANGE_SYMBOL_MISMATCH` when a cited range partially overlaps exactly one
definition, so a reference that drifted entirely outside its named function is invisible to it. A separate
disjoint-range audit over the whole wiki found:

- 597 links whose label is a defined symbol but whose range does not intersect that definition at all;
- 38 of them inside files touched by this merge (the actionable set), and 559 in untouched files (pre-existing
  backlog, belongs to `wiki-auditor`);
- the earlier SequenceMatcher drift sweep had itself mis-shifted links whose baseline value was already stale,
  which is why the mechanical sweep could read zero while `glsl.md` still cited the three-line forwarder instead of
  `createGlslTests()` at `#L1292-L1366`.

Repair was applied through an explicit (page, old anchor, new anchor, expected count) table with a hard count guard:
27 anchor replacements across 14 pages, plus label corrections where upstream renamed the function
(`vktSSBOLayoutCase.cpp` now exposes a `queuePass()` OOM wrapper over a `queuePassImpl()` body; no `iterate()`
exists in that file). After the repairs the actionable set went from 38 to 7, and those 7 are class/constructor
alias false positives or the pre-existing `DescriptorHeap.md` appendix staleness.

### Validation

- [x] Per-category English structure, registration, and link checks after edits.
- [x] Whole-wiki structure + registration sweep: `verify_english_structure.py` PASS for the 16 affected categories
      (286 pages, 0 findings); `verify_registration_paths.py` reported "All paths verified successfully" for the same
      16 categories.
- [x] Source line-reference sweep back to zero: `check_line_refs.py . external/vulkancts/wiki` ->
      `errors=0 warnings=0 findings=0`.
- [x] Lookup DB: full rebuild, 55 categories, `site/mappings.json` 13474 -> 13485 mappings (the 11 new prefixes are
      exactly the new upstream families and all resolve to pages updated in this sync); 23 lookup unit tests passed;
      `py_compile` passed.
- [x] Configured mustpass coverage: 295364/295364 leaves resolved over the changed in-scope inputs
      (`vk-default` renderpasses, dgc, fragment-shading-rate, robustness; `vksc-default` sc).
- [x] `validate_wiki_links.py` over the 97 changed wiki pages: 3 findings, all pre-existing in
      `unresolved_findings/wsi.md`.
- [x] `git diff --check`.

### Unresolved findings handed over

- `unresolved_findings/wsi.md` links two never-committed documents (`wsi_audit_summary.md`, twice, and
  `draw_unresolved_findings.md`, whose actual sibling page is `draw.md`). Pre-existing at the local wiki parent, so
  the audit page was left for its owner to repoint.
- `check_line_refs.py` cannot see disjoint ranges, treats a class declaration as a same-named constructor, and does
  not check symbols for file-name or phrase labels.
- `binding_model/DescriptorHeap.md` appendix rows for `ReservedHeap` and `Spirv` are stale by roughly 775 lines.
- 559 disjoint-range candidates remain in files untouched by this merge.

### Boundary

- Chinese synchronization is **not** authorized yet; `vkcts-wiki-pages/` must stay untouched.
