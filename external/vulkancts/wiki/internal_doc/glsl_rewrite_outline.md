# glsl Rewrite Outline

## Scope

- Category: `glsl`
- Old Level-2 page: `external/vulkancts/wiki/categories/glsl.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/glsl/`
- Source category directory: not applicable — `glsl` has no dedicated `modules/vulkan/glsl/` directory. Its tests are aggregated by `createGlslTests()` in [`vktTestPackage.cpp`](../../modules/vulkan/vktTestPackage.cpp#L1215-L1288) from four source areas:
  - `external/vulkancts/modules/vulkan/vktShaderLibrary.cpp` (ShaderLibrary infrastructure + ES 3.10 and `440.linkage` `.test` data)
  - `external/vulkancts/modules/vulkan/shaderrender/` (rendered-image groups)
  - `external/vulkancts/modules/vulkan/shaderexecutor/` (execution/result-buffer groups)
  - `external/vulkancts/modules/vulkan/amber/` (non-VulkanSC Amber groups)

## Page Count

- Old Level-3 pages found: 23
- Registration-only dispatcher pages to fold into Level-2: 0
- Implementation-bearing Level-3 pages to rewrite: 23
- Counted rewrite files for batching: 23
  - 0 Understanding Briefs (none of the 23 pages are flagged for brief-driven rewriting in this outline; briefs may be added per page during inspection if a page proves non-mechanical)
  - 23 rewritten Level-3 pages

Rationale for no automatic briefs in the outline: every Level-3 page in this category is small-to-medium and follows a clear pattern (ShaderRender, ShaderExecutor, ShaderLibrary, or Amber) shared across the category. Whether a page needs an Understanding Brief is decided per-page during Phase 1 inspection; the outline only fixes the dispatcher decision and batch structure.

## Dispatcher Decision

- `vktTestPackage.cpp::createGlslTests()` is the only aggregator and is shared by other categories. It is not a separate dispatcher file in the `glsl` source area; therefore no separate `vktGlslTests.cpp` page is created or rewritten.
- Fold category-specific dispatcher facts into the rewritten Level-2 `glsl` page:
  - direct category tree, including the `440.linkage` nested group and the `#ifndef CTS_USES_VULKANSC` boundaries;
  - subgroup names for each of the four source areas: ShaderLibrary groups, ShaderRender groups, ShaderExecutor groups, Amber groups;
  - source-to-family routing that maps each implementation file to its registered group.

## Batch 1 — ShaderLibrary + ShaderRender (visual) and the ShaderRender evaluator-heavy half

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktShaderLibrary.md` | No | One implementation-bearing file (`vktShaderLibrary.cpp`) plus declarative `.test` data; the page must explain the ShaderLibrary case generation/execution flow without making every `.test` group a sub-page. Direct rewrite. |
| `vktShaderRenderBuiltinVarTests.md` | No | ShaderRenderCase-based with builtin-variable evaluator; mechanical page. Direct rewrite. |
| `vktShaderRenderDerivateTests.md` | No | ShaderRenderCase-based with derivative-interval evaluator; mechanical page. Direct rewrite. |
| `vktShaderRenderDiscardTests.md` | No | ShaderRenderCase-based for discard/demote; mechanical page. Direct rewrite. |
| `vktShaderRenderIndexingTests.md` | No | ShaderRenderCase-based for opaque indexing into arrays/matrices; mechanical page. Direct rewrite. |
| `vktShaderRenderInvarianceTests.md` | No | ShaderRenderCase-based for `invariant`/`precise`; mechanical page. Direct rewrite. |
| `vktShaderRenderLimitTests.md` | No | ShaderRenderCase-based with pixel-threshold compare; mechanical page. Direct rewrite. |
| `vktShaderRenderLoopTests.md` | No | ShaderRenderCase-based for loop control flow; mechanical page. Direct rewrite. |

## Batch 2 — ShaderRender operator/matrix and texture sampling half

Counted files: 7

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktShaderRenderMatrixTests.md` | No | ShaderRenderCase-based with `MatrixShaderEvaluator`; the evaluator is the only specialized comparator so a brief is not required. Direct rewrite. |
| `vktShaderRenderOperatorTests.md` | No | ShaderRenderCase-based with `OperatorShaderEvaluator` and `ShaderDataSpec`; mechanical page once evaluator purpose is explained. Direct rewrite. |
| `vktShaderRenderReturnTests.md` | No | ShaderRenderCase-based for return-from-function; mechanical page. Direct rewrite. |
| `vktShaderRenderStructTests.md` | No | ShaderRenderCase-based for struct field access; mechanical page. Direct rewrite. |
| `vktShaderRenderSwitchTests.md` | No | ShaderRenderCase-based for switch control flow; mechanical page. Direct rewrite. |
| `vktShaderRenderTextureFunctionTests.md` | No | ShaderRenderCase-based with `TexLookupEvaluator` and several feature-gated checkSupport paths; mechanical page. Direct rewrite. |
| `vktShaderRenderTextureGatherTests.md` | No | ShaderRenderCase-based with `TextureGatherInstance::verify()` and offset-based reference; mechanical page. Direct rewrite. |

## Batch 3 — ShaderExecutor execution/result-buffer families

Counted files: 7

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktShaderBuiltinTests.md` | No | ShaderExecutor-based for builtin functions; mechanical page. Direct rewrite. |
| `vktOpaqueTypeIndexingTests.md` | No | ShaderExecutor-based with `VK_KHR_storage_buffer_storage_class` gating; mechanical page. Direct rewrite. |
| `vktAtomicOperationTests.md` | No | ShaderExecutor-based with multi-feature branches (`shaderImageInt64Atomics`, float atomics, float16-vector, reference); mechanical page. Direct rewrite. |
| `vktShaderClockTests.md` | No | ShaderExecutor-based with `VK_KHR_shader_clock` gating; mechanical page. Direct rewrite. |
| `vktShaderHelperInvocationsTests.md` | No | ShaderExecutor-based with `VK_KHR_buffer_device_address` for address-load variants; mechanical page. Direct rewrite. |
| `vktShaderBFloat16Tests.md` | No | ShaderExecutor-based BFloat16 group with delegated constant/conversion/combo files. The BFloat16 area has multiple source files; the Level-3 page must explain the delegation. Direct rewrite. |
| `vktShaderExpectAssumeTests.md` | No | ShaderExecutor-based with `VK_KHR_shader_expect_assume` + 16-bit / 8-bit storage gating; mechanical page. Direct rewrite. |

## Batch 4 — Amber scripted GLSL groups + Level-2 synthesis

Counted files: 1 + Level-2

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktAmberGlslTests.md` | No | Amber-based with three groups (`combined_operations`, `crash_test`, `logical_copy`); non-VulkanSC only. Direct rewrite. |

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `glsl.md` as the compact Level-2 category gateway.
- Include the four-source-area routing: ShaderLibrary, ShaderRender, ShaderExecutor, Amber.
- Note that the aggregator `createGlslTests()` is shared with other categories and lives in `vktTestPackage.cpp`.
- Mark non-VulkanSC-only children (`demote`, `bfloat16`, Amber groups, `shader_expect_assume`) accurately.
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating shader walkthroughs, parameter matrices, and verification mechanics from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.

## Notes on Inspection Order

- The first Level-3 page inspected for any category should be the dispatcher/aggregator equivalent. For `glsl` the closest equivalent is the shared `createGlslTests()` block in `vktTestPackage.cpp`; the dedicated dispatcher file `vktDynamicStateTests.cpp` does not exist in `glsl`.
- The ShaderLibrary page (`vktShaderLibrary.md`) must be inspected and rewritten early because its case-generation flow is referenced by every ShaderRender / ShaderExecutor / ShaderLibrary page that uses the common `vktShaderExecutor`/`vktShaderRender` harness.
- BFloat16 has additional files (`vktShaderBFloat16ConstantTests.cpp`, `vktShaderBFloat16DotTests.cpp`, `vktShaderBFloat16ComboTests.cpp`, `vktShaderBFloat16Tests.cpp`, `vktShaderFConvertTests.cpp`) that are referenced by the `bfloat16` group. The Level-3 page should record the delegation but the implementation files do not have their own Level-3 pages because their names are not on the Level-2 file inventory; this should be confirmed during inspection and the file inventory updated if a separate page is required.