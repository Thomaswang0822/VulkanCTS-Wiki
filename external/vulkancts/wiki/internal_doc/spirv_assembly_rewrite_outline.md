# spirv_assembly Rewrite Outline

## Scope

- Category: `spirv_assembly`
- Old Level-2 page: `external/vulkancts/wiki/categories/spirv_assembly.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/spirv_assembly/`
- Source category directory: `external/vulkancts/modules/vulkan/spirv_assembly/`

## Page Count

- Old Level-3 pages found: 40
- Registration-only dispatcher pages to fold into Level-2: 1 (`vktSpvAsmTests.cpp`/`.hpp` — the category root)
- Implementation-bearing Level-3 pages to rewrite: 40
  - Phase 1 (HLSL pilot, existing harness): 1 page (`vktSpvAsmFromHlslTests`), 1 counted file
  - Phase 3 (C++-templated SPIR-V, single-mode temp harness): 32 pages, 58 counted files (26 briefs + 32 pages) — Batches 1-8
  - Phase 3 (Amber-backed, manual extraction): 7 pages, 8 counted files (1 brief + 7 pages) — Batch 9
- Total counted rewrite files: 67 (27 Understanding Briefs + 40 rewritten Level-3 pages)

## Dispatcher Decision

- `vktSpvAsmTests.cpp` should NOT be rewritten because it is registration-only. It only adds the `instruction` and `type` direct children at [`createChildren()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTests.cpp#L38-L46) and delegates all implementation.
- Fold category-specific dispatcher facts into the rewritten Level-2 `spirv_assembly` page:
  - direct category tree (`instruction`, `type`);
  - subgroup names: `instruction`, `type`;
  - source-to-family routing (compute/graphics split under `instruction`; scalar/vector split under `type`).

## Shader Workflow Decisions and Execution Plan

### Category property

This category is SPIR-V-centered: tests construct SPIR-V assembly shader text directly in C++ string templates rather than authoring GLSL/HLSL and compiling it. This breaks the GLSL/HLSL assumption that `shader-analyzer` and `shader-disassembler` are built on, and requires the category-scoped deviations documented below.

### Decision 1 — Round-trip as generation-time validation gate

The LLM extracts/reconstructs SPIR-V assembly text from C++ string-template source. That extraction is not robust: the LLM can drop operands, swap IDs, misread decorations, or merge template branches incorrectly.

The disassembler round-trip (`spirv-as` → `spirv-val` → `spirv-dis`) serves primarily as a **generation-time validation gate** on that extraction:

- `spirv-as` catches syntax/transcription errors (malformed assembly, wrong operand counts).
- `spirv-val` catches semantic violations against the target SPIR-V environment (missing capabilities, bad decorations).
- If either fails, the LLM reconstruction is rejected and re-extracted before the page ships.

The round-trip validates **well-formedness**, not full semantic fidelity to what CTS executes. Residual risk is an LLM transcription error that still assembles to valid but semantically different SPIR-V; that residual is low and acceptable.

### Decision 2 — Single snippet under `#### Source Code`, omit `#### SPIR-V` subsection

- `#### Source Code` holds the **CTS-authored SPIR-V assembly** (the source of truth), unfoldable, replacing the usual GLSL.
- The `#### SPIR-V` collapsed subsection is **omitted** for this category — it would be a duplicate SPIR-V snippet.
- `shader-disassembler` still runs during generation as a **validation gate only**; its disassembled output is not published.

This is a category-scoped deviation from `level3-template.md` and `validation-checklist.md`, both of which currently mandate the `#### SPIR-V` subsection. The deviation requires a temporary harness edit (see Execution Plan).

### Amber-backed sub-case

For the 7 Amber-backed pages in Batch 9 (`vktSpvAsmLdexpTests`, `vktSpvAsmSignedIntCompareTests`, `vktSpvAsmSignedOpTests`, `vktSpvAsmVectorShuffleTests`, `vktSpvAsmSpirvVersion1p4Tests`, `vktSpvAsmTerminateInvocationTests`, `vktSpvAsmPtrAccessChainTests`), the Amber script is the first-class artifact in `#### Source Code`. The C++ source is a pure dispatcher (test name → `.amber` file), and the Amber script embeds literal SPIR-V assembly text. Because the assembly is literal CTS test data (not reconstructed from C++ templates), no `spirv-as` validation gate is needed — the subagent extracts the assembly verbatim from the Amber script and places it under `#### Source Code` (Decision 2: omit `#### SPIR-V` subsection).

### Execution Plan

**Design principle: single-mode temp harness.**

The temporary harness edit is single-mode: it handles only C++-templated SPIR-V extraction. This eliminates per-page mode-selection by worker subagents, which see only one page at a time and lack full-category context to classify confidently. A dual-mode edit (C++-templated + Amber-embedded) would force that decision onto subagents and risk misclassification.

The Amber-backed pages in Batch 9 use manual extraction (no `shader-analyzer`/`shader-disassembler`), documented per-page in Batch 9 below. The HLSL pilot page (`vktSpvAsmFromHlslTests`) uses the existing GLSL/HLSL harness.

**Phase 1 — HLSL pilot (existing harness).**

Rewrite `vktSpvAsmFromHlslTests.md` with the existing, unmodified `wiki-rewriter` harness. The page uses genuine HLSL source (registered via `dst.hlslSources.add`), so `shader-analyzer` reconstructs HLSL and `shader-disassembler` compiles with `glslangValidator`. Normal `#### Source Code` (HLSL) + `#### SPIR-V` subsection both apply (different representations, not duplicates).

**Phase 2 — Single-mode temp harness edit.**

After Phase 1 completes, edit skill files to add a single, spirv_assembly-specific, concise, clearly-marked temporary deviation for C++-templated SPIR-V extraction only. No Amber branch, no mode-selection logic. Edits must be specific (not generalizable to other categories) and easy to revert. Files to edit:

- `shader-analyzer/SKILL.md` — add SPIR-V-assembly extraction mode: manual mode, extract authored assembly from C++ string templates (not reconstruct GLSL/HLSL), preserve CTS-generated `;` comments, annotate decorations/IO/descriptors as usual (annotation is source-language-agnostic).
- `shader-disassembler/SKILL.md` — assemble with `spirv-as` (assembly text → SPIR-V binary) instead of compiling with `glslangValidator`; then `spirv-val` + `spirv-dis` as usual. Output serves as generation-time validation gate only (Decision 1) and is NOT published as a `#### SPIR-V` subsection (Decision 2).
- `wiki-rewriter/references/level3-template.md` and `wiki-rewriter/references/validation-checklist.md` — add a spirv_assembly-scoped note: `#### Source Code` holds SPIR-V assembly; `#### SPIR-V` subsection is omitted; disassembler runs as generation-time validation only.

`wiki-rewriter/SKILL.md` itself does not need editing — its workflow phases are source-language-agnostic; only its referenced templates and the two worker skills carry the GLSL/HLSL assumption that needs the temporary deviation.

All edits are temporary: they will be restored to current state after the category finishes and before merge to `vkcts-wiki`.

**Phase 3 — Worker dispatch for remaining 39 pages.**

After Phase 2 edits land, dispatch worker subagents batch-by-batch for the remaining 39 pages (Batches 1-9). Subagents receive the single canonical (temporarily-edited) harness from the skill definitions for the 32 C++-templated pages. For the 7 Amber-backed pages in Batch 9, subagents receive the existing, unmodified harness plus the per-page manual-extraction instruction documented in Batch 9. No verbal overrides beyond what is recorded in this outline.

### Page classification by shader input shape

| Input shape | Pages | Phase | Harness path |
|---|---|---|---|
| HLSL source (confirmed genuine) | 1 (`vktSpvAsmFromHlslTests`) | Phase 1 | Existing GLSL/HLSL harness: `shader-analyzer` reconstruct HLSL → `shader-disassembler` compile with `glslangValidator`. Normal `#### Source Code` (HLSL) + `#### SPIR-V` subsection. |
| C++-templated SPIR-V assembly | 32 | Phase 3 (Batches 1-8) | Single-mode temp harness: `shader-analyzer` assembly-extract → `shader-disassembler` `spirv-as` validation gate |
| Amber-backed (SPIR-V assembly embedded) | 7 | Phase 3 (Batch 9) | Manual extraction from Amber script (no `shader-analyzer`/`shader-disassembler`). `#### Source Code` holds extracted SPIR-V assembly; `#### SPIR-V` subsection omitted (Decision 2). |

### Phase 1 Identification Result (Step 1a — completed)

**FromHlslTests** — Genuine HLSL source.

- Source: [`vktSpvAsmFromHlslTests.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmFromHlslTests.cpp) lines 65-75.
- HLSL registered via `dst.hlslSources.add("comp") << glu::ComputeSource(source)`.
- Single test case: `cbuffer_packing` — tests HLSL `cbuffer` packing corner case (`packoffset(c1.y)`) with `VK_EXT_scalar_block_layout`.
- Harness: existing GLSL/HLSL harness applies directly. Normal `#### Source Code` (HLSL) + `#### SPIR-V` subsection.
- Brief: No (single focused case, direct rewrite).
- Status: Complete. Rewritten page at [`FromHlslTests.md`](../../external/vulkancts/wiki/testfiles/spirv_assembly/FromHlslTests.md).

## Batch 1 — Core aggregators (hybrid registration + implementation)

Counted files: 4

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSpvAsmInstructionTests.md` | Yes | Largest hybrid file: `instruction` aggregator with `compute`/`graphics` branches, ~50 inline groups, and delegated subfamilies. Multi-axis behavior, generated matrices, and shader-heavy inline SPIR-V make direct rewriting risk source-navigation. |
| `vktSpvAsmTypeTests.md` | Yes | Hybrid `type` aggregator + templated `SpvAsmTypeTests<T>` framework with macro-expanded operation matrices (arithmetic, bitwise, comparison, shift, bit-field, constants). Generated test matrix and concept-heavy. |

## Batch 2 — Storage and basic pointer families

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSpvAsm8bitStorageTests.md` | Yes | Compute/graphics storage and conversion cases with `SPV_KHR_8bit_storage` capability matrix and feature gates; shader-heavy with generated descriptor/resource layout. |
| `vktSpvAsm16bitStorageTests.md` | Yes | Custom 16-bit comparison callbacks, feature paths, large source range; nontrivial validation and resource layout. |
| `vktSpvAsmVariablePointersTests.md` | Yes | Switches between logical variable pointers and physical-storage-buffer pointers; multi-mode addressing with capability/feature gates. |
| `vktSpvAsmPointerParameterTests.md` | Yes | Compute/graphics pointer-parameter cases requiring `VK_KHR_variable_pointers`; distinct compute vs graphics factories. |

## Batch 3 — Advanced pointers and raw access chains

Counted files: 6

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSpvAsmPhysicalStorageBufferPointerTests.md` | Yes | Physical-storage-buffer pointer/addressing cases; distinct addressing model needing concept scaffolding. |
| `vktSpvAsmUntypedPointersTests.md` | Yes | Very large source file; `vulkan_memory_model`/`glsl_memory_model` subtrees, cooperative-matrix interaction, `VK_KHR_shader_untyped_pointers` gates. |
| `vktSpvAsmRawAccessChainTests.md` | Yes | Generated load/store matrix over variable pointers, descriptor indexing, physical buffers, 64-bit indexing, bounds checks, qualifiers, stride, component size, alignment. Complex multi-dimension generation. |

> `vktSpvAsmPtrAccessChainTests.md` is in Batch 9 (Amber-backed).

## Batch 4 — Float controls and compute shader derivatives

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSpvAsmFloatControlsTests.md` | Yes | Operation and settings matrices, `VK_KHR_shader_float_controls`, custom byte-comparison verification, independence settings. |
| `vktSpvAsmFloatControls2Tests.md` | Yes | `float_controls2` compute/graphics; extends the float-controls concept with a second matrix. |
| `vktSpvAsmFloatControlsExtensionlessTests.md` | Yes | Extensionless path requiring `VK_KHR_spirv_1_4`, float16/int8/float64 feature selection; nontrivial support matrix. |
| `vktSpvAsmComputeShaderDerivativesTests.md` | Yes | Compute/mesh/task derivative cases, `VK_KHR_compute_shader_derivatives` + `VK_EXT_mesh_shader` gates, large source range. |

## Batch 5 — Compute workgroup, multi-shader, image/sampler, indexing

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSpvAsmWorkgroupMemoryTests.md` | Yes | Workgroup memory read/barrier/write flow with `OpMemoryBarrier`/`OpControlBarrier`; 11 numeric-type variants with per-type feature gates and NaN-aware float64 verification. |
| `vktSpvAsmMultipleShadersTests.md` | Yes | Multiple entry points in one SPIR-V module; module-structure concept and non-obvious validation. |
| `vktSpvAsmImageSamplerTests.md` | Yes | Image/sampler instruction families, compute/graphics; descriptor/resource layout and instruction-coverage matrix. |
| `vktSpvAsmIndexingTests.md` | Yes | Compute/graphics indexing cases; descriptor-indexing and bounds behavior. |

## Batch 6 — Graphics interface and operations I

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSpvAsmCrossStageInterfaceTests.md` | Yes | Graphics interface compatibility across stages; interface-matching semantics need scaffolding. |
| `vktSpvAsmVaryingNameTests.md` | No | Narrow graphics interface-name cases; core property (varying name matching) is focused and small. |
| `vktSpvAsmCompositeInsertTests.md` | Yes | Compute/graphics matrix and composite insertion across vector/matrix/struct; multi-target insertion matrix. |
| `vktSpvAsmVariableInitTests.md` | Yes | Compute/graphics initialization cases; initializer semantics and storage-class matrix. |
| `vktSpvAsmConditionalBranchTests.md` | No | Same-label branch tests; focused SPIR-V control-flow property, narrow source range. |

## Batch 7 — Operations and comparisons

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSpvAsmUboMatrixPaddingTests.md` | Yes | UBO matrix-padding compute/graphics; std140/std430 layout rules need concept scaffolding. |
| `vktSpvAsm64bitCompareTests.md` | Yes | Compute/graphics 64-bit comparisons; `Int64` capability and signed/unsigned matrix. |
| `vktSpvAsmTrinaryMinMaxTests.md` | Yes | `amd_trinary_minmax` operation/type/vector matrix, `VK_AMD_shader_trinary_minmax`, custom `deMemCmp` verification. |
| `vktSpvAsmIntegerDotProductTests.md` | Yes | Integer dot-product operation families; extension/feature matrix and instruction variants. |

## Batch 8 — Maintenance, version, non-semantic, FMA, simple compute

Counted files: 8

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktSpvAsmMaint9VectorizationTests.md` | Yes | `maint9_vectorization` vectorized bit-operation cases; conditional `VK_KHR_maintenance9`/`shaderInt64`/`shaderInt16` matrix. |
| `vktSpvAsmSpirvVersionTests.md` | Yes | Version/capability checks across compute/graphics; SPIR-V version semantics need scaffolding. |
| `vktSpvAsmNonSemanticInfoTests.md` | No | Non-semantic info cases; focused debug-info property, narrow source range. |
| `vktSpvAsmFmaTests.md` | No | `opfma` fused multiply-add; single operation family, focused property. |
| `vktSpvAsmEmptyStructTests.md` | No | Empty-structure compute cases; small, focused property. |
| `vktSpvAsmRelaxedWithForwardReferenceTests.md` | No | `relaxed_with_forward_reference` compute cases; narrow source range, focused property. |

> `vktSpvAsmFromHlslTests.md` is in Phase 1 (HLSL source, existing harness).

## Batch 9 — Amber-backed families (manual SPIR-V extraction)

Counted files: 8 (1 brief + 7 pages)

These 7 pages are Amber-backed: the C++ source is a pure dispatcher (test name → `.amber` file), and the Amber script embeds literal SPIR-V assembly text. Subagents extract the assembly verbatim from the representative Amber script and place it under `#### Source Code` (unfoldable). The `#### SPIR-V` subsection is omitted (Decision 2). No `shader-analyzer`/`shader-disassembler` invocation — the assembly is literal CTS test data, not reconstructed from C++ templates, so no validation gate is needed.

| Old Level-3 page | Brief? | Amber script path | Representative walkthrough case | Core property |
|---|---:|---|---|---|
| `vktSpvAsmLdexpTests.md` | No | `data/vulkan/amber/ldexp/` (36 `.amber` files) | `ldexp_float32_int32.amber` | `OpExtInst Ldexp` with float/int type width combinations |
| `vktSpvAsmSignedIntCompareTests.md` | No | `spirv_assembly/instruction/compute/signed_int_compare/` (4 `.amber`) | `uint_sgreaterthan.amber` | Signed comparison ops on unsigned int values |
| `vktSpvAsmSignedOpTests.md` | No | `spirv_assembly/instruction/compute/signed_op/` (21 `.amber`) | `glsl_int_findumsb.amber` | GLSL.std.450 signed operations on unsigned int values |
| `vktSpvAsmVectorShuffleTests.md` | No | `spirv_assembly/instruction/compute/vector_shuffle/` (2 `.amber`) | `vector_shuffle.amber` | `OpVectorShuffle` with `-1` undef indices |
| `vktSpvAsmSpirvVersion1p4Tests.md` | Yes | `spirv_assembly/instruction/spirv1p4/` (12 subgroups, ~80+ `.amber`) | `opselect/scalar_select.amber` | SPIR-V 1.4 new features (OpSelect, OpPtrEqual/Diff, OpCopyLogical, etc.) |
| `vktSpvAsmTerminateInvocationTests.md` | No | `spirv_assembly/instruction/terminate_invocation/` (15 registered `.amber`) | `no_output_write.amber` | `VK_KHR_shader_terminate_invocation` — terminated invocations must not perform subsequent stores/atomics/loads |
| `vktSpvAsmPtrAccessChainTests.md` | No | `spirv_assembly/instruction/compute/ptr_access_chain/` (2 `.amber`) | `workgroup.amber` | `OpPtrAccessChain` on workgroup memory with correct/incorrect `ArrayStride` |

Notes for subagents:
- Assembly format varies: `SHADER compute <name> SPIRV-ASM ... END` (ldexp, signed_op) or `[compute shader spirv] ... [test]` (signed_int_compare, vector_shuffle, spirv1p4, ptr_access_chain) or `#!amber` with `SHADER vertex/fragment ... SPIRV-ASM ... END` (terminate_invocation).
- For `terminate_invocation`, some Amber scripts contain multiple shaders (tested shader + GLSL reference shader `expect_fs`). Extract only the tested shader(s), not the GLSL reference.
- Status: All 7 pages were rewritten during a pilot run. Rewritten pages exist on disk.

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `spirv_assembly.md` as the compact Level-2 category gateway.
- Include folded dispatcher information when the dispatcher is registration-only.
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating detailed shader walkthroughs, parameter matrices, and validation mechanics from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.
