# Understanding Brief: `spirv_assembly.instruction` aggregator page

## One-Sentence Test Purpose

This test aggregator checks that the implementation correctly executes a broad catalog of SPIR-V instructions — authored directly as assembly text in C++ string templates — under both compute and graphics pipelines, with larger feature areas delegated to separate per-feature test families.

## Background Knowledge

### SPIR-V assembly authored in C++ string templates

Unlike GLSL/HLSL-driven CTS categories, the `spirv_assembly` category builds shader modules from SPIR-V assembly text that is concatenated from C++ string fragments at test construction time. The shader text is the source of truth: there is no GLSL frontend in the loop for the inline groups. A typical builder assembles the module from shared preamble helpers (`getComputeAsmShaderPreamble`, `getComputeAsmCommonTypes`, `getComputeAsmInputOutputBuffer`, `getComputeAsmInputOutputBufferTraits`) plus a per-test body that names the instructions under test.

Why it matters here:
- The validator for these tests is the SPIR-V instruction semantics itself, not a GLSL-to-SPIR-V translation the reader must reverse-engineer.
- The shared helpers fix the descriptor layout (binding 0 = input SSBO, binding 1 = output SSBO) and the execution mode (`LocalSize 1 1 1`), so per-test variation is concentrated in the body.

### `SpvAsmComputeShaderCase` harness

The inline compute groups are wrapped in `SpvAsmComputeShaderCase`, a skeleton that binds host-supplied input/output buffers as storage descriptors, dispatches `numWorkGroups` invocations, and compares the output buffer byte-for-byte against an expected buffer the test supplies. The skeleton allows a test to override two fields that matter for this aggregator:

- `verifyIO` — a custom callback used instead of the default byte comparison (for example, NaN-aware float64 comparison in `workgroup_memory`, byte comparison with epsilon in float-controls, `deMemCmp` in `amd_trinary_minmax`).
- `failResult` / `failMessage` — the status code returned when verification fails. The default is `QP_TEST_RESULT_FAIL`, but `OpSRem`/`OpSMod` cases override it to `QP_TEST_RESULT_PASS` (negative operands are undefined per SPIR-V, so a mismatch is still spec-compliant), `QP_TEST_RESULT_QUALITY_WARNING` (the `android` sub-groups), or `QP_TEST_RESULT_FAIL` under `VK_KHR_maintenance8` (which makes negative-operand behavior well-defined).

Why it matters here:
- The default pass/fail rule is exact byte equality between the device-written output buffer and the host-supplied expected buffer.
- The `failResult` override is the mechanism behind the `android` / `maintenance8` pruning story on this page; without it, the reader cannot interpret why the same `OpSRem` instruction has three different expected statuses.

### Legacy `Uniform` storage class + `BufferBlock` decoration

The shared compute helpers default to the legacy SPIR-V 1.0 storage-buffer encoding: variables in the `Uniform` storage class with the `BufferBlock` decoration, rather than the SPIR-V 1.3 `StorageBuffer` storage class. Both encodings map to a Vulkan `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`; the difference is purely textual in the assembly. A few groups (`opatomic_storage_buffer`, `opatomic_storage_buffer_volatile`) opt into the modern `StorageBuffer` storage class explicitly.

Why it matters here:
- A reader who greps the assembly for `OpVariable ... StorageBuffer` will not find it in the default-helpers groups; the storage buffer lives under `Uniform` + `BufferBlock`. This is conventional for SPIR-V 1.0 assembly and is not a defect.

## One Concrete Example

The `compute.opnop.all` case ([`createOpNopGroup`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L1089-L1141)) is the smallest representative of the inline compute pattern. The shader loads one `float` per invocation from the input SSBO, negates it with `OpFNegate`, and stores the result to the output SSBO. An `OpNop` is placed in the function body between the invocation-id extraction and the load. The host fills the input with 100 random positive floats in `[1, 100]`, expects the output to be the exact negation, and dispatches `100×1×1` invocations.

```text
; excerpt of the test body (full module under #### Source Code in the page)
%idval     = OpLoad %uvec3 %id
%x         = OpCompositeExtract %u32 %idval 0
             OpNop                          ; the instruction under test
%inloc     = OpAccessChain %f32ptr %indata %zero %x
%inval     = OpLoad %f32 %inloc
%neg       = OpFNegate %f32 %inval
%outloc    = OpAccessChain %f32ptr %outdata %zero %x
             OpStore %outloc %neg
```

This case is representative because the `OpNop` is the only thing that changes versus the baseline compute pattern; everything else (preamble, descriptor layout, dispatch, verification) is shared with dozens of sibling inline groups.

## End-to-End Test Flow

```text
[host] build SPIR-V assembly text from shared helpers + per-test body
[host] compile assembly to a shader module at program-build time
[host] create input SSBO(s) from host-supplied buffers, output SSBO zeroed
[host] bind descriptor set 0 with input(s) at binding 0..N-1, output at binding N
[host] vkCmdDispatch numWorkGroups (per-test, often numElements×1×1)
[device] each invocation reads input[id.x], runs the instruction(s) under test, writes output[id.x]
[host] invalidate output memory, read back bytes
[host] compare output bytes to expected bytes (default deMemCmp, or custom verifyIO)
[host] return TestStatus(failResult, failMessage) on mismatch, else pass
```

For graphics groups, the host-side flow instead renders through graphics shader utilities (vertex/fragment, and for some groups geometry/tessellation), and the verification is per-pixel or per-attachment rather than per-SSBO-element. Amber-backed subfamilies (`function_params`, `image_query`, `spirv1p4`, `terminate_invocation`) replace the C++ harness entirely with an Amber script that owns the dispatch/draw and probe.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline SPIR-V assembly text concatenated from C++ string helpers (the dominant artifact for inline compute/graphics groups).
- Amber scripts (`.amber` files) for `function_params`, `image_query`, `spirv1p4`, `terminate_invocation`, and a handful of inline Amber cases under `compute` (`oparraylength`, `signed_int_compare`, `signed_op`, `vector_shuffle`, `ptr_access_chain`, `ldexp`, integer-dot-product).
- Specialization constants for `localsize` (LocalSize execution mode) and `localsize_id` (LocalSizeId, SPIR-V 1.5).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Input SSBO(s) (`%indata`, `%indata1`, `%indata2`) | yes | yes (descriptor set 0, binding 0..N-1) | read by shader | no | Carries the per-invocation input operands |
| Output SSBO (`%outdata`) | yes (zeroed) | yes (descriptor set 0, last binding) | written by shader | yes | Carries the per-invocation result; compared byte-for-byte against expected |
| `gl_GlobalInvocationID` (`%id`, Input) | n/a (built-in) | n/a | read by shader | no | Per-invocation index into the SSBOs |
| `gl_WorkGroupSize` (`localsize` only) | yes (specialization constants) | n/a | read by shader | no | Specialization-constant-driven LocalSize mode |
| Amber SSBOs / color buffers | yes (Amber script) | yes | read/written per script | yes (Amber probe) | The Amber-backed subfamilies own their own resources |

## What Is Checked

- Default (inline compute/graphics groups): exact byte equality between the device-written output SSBO and the host-supplied expected buffer, element-by-element. The harness logs up to 16 mismatched bytes before stopping.
- Custom `verifyIO` callbacks: per-test logic, for example NaN-aware comparison for float64 `workgroup_memory` cases, epsilon comparison for float-controls, `deMemCmp` for `amd_trinary_minmax`.
- Binary verification (`verifyBinary`): a few groups (`opmoduleprocessed`) inspect the compiled SPIR-V binary itself rather than (or in addition to) execution output.
- Amber probes: the Amber-backed subfamilies use `probe ssbo ...` / `probe rgba ...` directives in the `.amber` script.
- The `failResult` field controls what status a mismatch produces: `FAIL` (default), `QUALITY_WARNING` (`android`), `PASS` (`OpSRem`/`OpSMod` negative-operand baseline), or `FAIL` under `VK_KHR_maintenance8`.

## Behavior Parameter Identification

> **Behavior parameter:** test family (the direct children of `spirv_assembly.instruction`)
>
> **Candidate values:** `compute`, `graphics`, `amd_trinary_minmax`, `function_params`, `image_query`, `maint9_vectorization`, `spirv1p4`, `terminate_invocation`

`compute` and `graphics` are themselves aggregators of ~50 inline groups plus delegated subfamilies; the other six are single-purpose delegated families. The page's `## Behavior Parameters` subsections explain each family at the level of what property its groups collectively exercise, and point at the delegated per-family pages for detail.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `compute` (inline groups) | SPIR-V instruction lowering or semantics bug in the compute pipeline; host-side SSBO setup, descriptor binding, or dispatch dimension mismatch; missing feature/capability not pruned at registration; `verifyIO` callback mismatch for custom-verification groups |
| `graphics` (inline groups) | Same instruction-lowering class as `compute` but exercised through graphics stages (vertex/fragment, plus geometry/tessellation for some groups); graphics-specific infrastructure failure (renderpass/framebuffer/varying interface); per-pixel verification mismatch |
| `amd_trinary_minmax` | `VK_AMD_shader_trinary_minmax` extension not supported or miscompiled; `FMin3`/`FMax3`/`FMid3`/`SMin3`/`SMax3`/`SMid3`/`UMin3`/`UMax3`/`UMid3` lowering wrong for a type or vector width; `deMemCmp`-based verification mismatch |
| `function_params` | Combined image sampler passed as a function parameter not handled (calling-convention or descriptor-indexing issue); Amber script skip vs. fail on missing support |
| `image_query` | `OpImageQuery` on a multisample storage image returns wrong `Samples`; `shaderStorageImageMultisample` feature not advertised (Amber should skip, not fail) |
| `maint9_vectorization` | `VK_KHR_maintenance9` vectorized `OpBitCount`/`OpBitReverse`/`OpBitFieldInsert`/`OpBitFieldSExtract`/`OpBitFieldUExtract` lowering wrong for a width or signedness; missing `shaderInt16`/`shaderInt64` not pruned |
| `spirv1p4` | SPIR-V 1.4 feature miscompiled or rejected: `OpCopyLogical`, selective image operands, `OpPtrEqual`/`OpPtrDiff`, entry-point interface changes; `VK_KHR_spirv_1_4` not supported (Amber should skip) |
| `terminate_invocation` | `VK_KHR_shader_terminate_invocation` not supported or `OpTerminateInvocation` fails to suppress subsequent stores/atomics/loads in the terminated invocation |

A cross-cutting cause shared by every family: the harness's default byte comparison treats any byte-level mismatch between device output and host expected as a failure, so an off-by-one in dispatch dimension, SSBO stride, or expected-buffer computation produces a mismatch even when the instruction under test is correct.

## Important Variations and Special Cases

- **`OpSRem` / `OpSMod` `failResult` variants.** The same instruction is registered three times with different expected statuses for negative operands: baseline (`compute.opsrem`/`compute.opsmod` and graphics counterparts, `negFailResult = PASS` — undefined per SPIR-V, any result accepted), `android` (`QUALITY_WARNING`), and `maintenance8` (`FAIL` — `VK_KHR_maintenance8` makes the behavior well-defined). The 64-bit variants (`opsrem64`/`opsmod64`) add `shaderInt64`.
- **`opatomic_storage_buffer_volatile`.** Requires `VK_KHR_vulkan_memory_model` and SPIR-V 1.3; tests volatile atomic operations through the `StorageBuffer` storage class.
- **`localsize_id`.** Requires `VK_KHR_maintenance4` and SPIR-V 1.5; tests the `LocalSizeId` execution mode (id-based rather than literal).
- **`nocontraction`.** Uses floating-point operands chosen so that fused multiply-add and separate multiply-then-add produce different bit results; the test fails if `NoContraction` is ignored.
- **`opfunord_nan`.** Requires `VK_KHR_shader_float_controls` with `shaderSignedZeroInfNanPreserveFloat32`; tests `OpFUnord*` comparisons with NaN operands.
- **Binary-verification groups.** `opmoduleprocessed` (and a few siblings) inspect the compiled SPIR-V binary rather than execution output.
- **Amber-backed inline cases.** Under `compute`, `oparraylength`, `signed_int_compare`, `signed_op`, `vector_shuffle`, `ptr_access_chain`, `ldexp`, the integer-dot-product family, and `opfma` are Amber-backed even though they live under the `compute` aggregator; their C++ builder is a pure dispatcher to `.amber` files.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `createInstructionTests` — aggregator root | [`vktSpvAsmInstructionTests.cpp#L21311-L21547`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21311-L21547) | Registers `compute`, `graphics`, and the six direct subfamilies |
| `computeTests` registration block | [`vktSpvAsmInstructionTests.cpp#L21316-L21449`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21316-L21449) | All inline compute groups + delegated subfamilies |
| `graphicsTests` registration block | [`vktSpvAsmInstructionTests.cpp#L21451-L21533`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21451-L21533) | All inline graphics groups + delegated subfamilies |
| `createOpNopGroup` (representative walkthrough) | [`vktSpvAsmInstructionTests.cpp#L1089-L1141`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L1089-L1141) | Smallest inline compute group; shows the shared-helpers + per-test-body pattern |
| `createOpSRemComputeGroup` (`failResult` story) | [`vktSpvAsmInstructionTests.cpp#L2526-L2626`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L2526-L2626) | Source of the `PASS` / `QUALITY_WARNING` / `FAIL` `failResult` variants |
| `android` sub-groups under compute | [`vktSpvAsmInstructionTests.cpp#L21384-L21391`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21384-L21391) | `QUALITY_WARNING` registration |
| `maintenance8` sub-groups under compute | [`vktSpvAsmInstructionTests.cpp#L21437-L21448`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21437-L21448) | `VK_KHR_maintenance8` `FAIL` registration |
| `createFunctionParamsGroup` | [`vktSpvAsmInstructionTests.cpp#L21096-L21118`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21096-L21118) | Amber-backed `function_params` family |
| `createQueryGroup` (`image_query`) | [`vktSpvAsmInstructionTests.cpp#L21283-L21309`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21283-L21309) | Amber-backed `image_query` family |
| `SpvAsmComputeShaderCase` harness | [`vktSpvAsmComputeShaderCase.cpp#L940-L999`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderCase.cpp#L940-L999) | Default byte comparison + `failResult`/`verifyIO` overrides |
| Compute assembly helpers | [`vktSpvAsmComputeShaderTestUtil.cpp#L65-L133`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L65-L133) | Shared preamble / types / SSBO layout helpers |

## Questions / Risk Points for User Audit

- Is the test-family-level behavioral axis the right choice for this aggregator, or should the page split `compute` and `graphics` into a separate inline-groups axis vs. delegated-subfamilies axis?
- Is one representative walkthrough (`compute.opnop.all`) enough, or should a second walkthrough cover a `failResult`-variant case (`compute.opsrem.all` under `maintenance8`) to make the pruning story concrete?
- Should the page enumerate all ~50 inline groups per pipeline variant, or only the ones with non-obvious behavior (NaN, atomics, NoContraction, OpSRem variants), with the rest summarized?
- Is the `Uniform` + `BufferBlock` legacy encoding note worth keeping in the final Background Knowledge, or is it too implementation-detail-heavy for a Level-3 page?

## Conversion Notes for Final Wiki Rewrite

- Carry `### Failure Cause Mapping` directly into the final page's `### Failure Cause Mapping`.
- Distill Background Knowledge into a short bullet list: SPIR-V-assembly-in-C++-templates, `SpvAsmComputeShaderCase` harness (SSBO I/O + byte comparison + `failResult`/`verifyIO` overrides), legacy `Uniform`+`BufferBlock` storage-buffer encoding.
- Use `compute.opnop.all` as the single representative shader walkthrough (extracted SPIR-V assembly under `#### Source Code`, no `#### SPIR-V` subsection per the spirv_assembly deviation). The `failResult` variant on `OpSRem` is explained in `## Behavior Parameters` and `## Failure Meaning` prose, not as a second walkthrough.
- Inline-group inventory moves to a compact table in `## Parameter Dimensions and Observed Values` (or a dedicated subsection), not to Background Knowledge.
- Delegated subfamilies (`8bit_storage`, `16bit_storage`, `composite_insert`, etc.) are listed with `(registration only)` markers in `## Registration Hierarchy` and linked from `## Behavior Parameters`; their mechanics belong on their own pages.
- The page must start with `## Overview` (no top-level `#` title), and the output filename is `InstructionTests.md`.
