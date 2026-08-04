# Understanding Brief: spirv_assembly multiple_shaders_extended

## One-Sentence Test Purpose

This test checks whether an implementation can create and dispatch two compute pipelines that select `mainA` and `mainB` from one SPIR-V module, including a module with separate `LocalSizeId` execution-mode instructions and a module whose entry points declare different interfaces.

## Background Knowledge

### Entry-point selection in a shared shader module

A SPIR-V module can contain multiple `OpEntryPoint` instructions. A compute pipeline selects one entry point through `VkPipelineShaderStageCreateInfo::pName`; the selected name must identify an `OpEntryPoint` with a matching execution model ([pipeline validity rule](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1183-L1186)).

Why it matters here:
- The test creates one `VkShaderModule` and two compute pipelines, changing only `pName` from `mainB` to `mainA` ([pipeline setup](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L139-L178)).
- Each dispatch must execute its selected function rather than another function from the same module.

### Compute workgroup size and entry-point interfaces

`OpExecutionMode LocalSize` gives an entry point a literal workgroup size. `OpExecutionModeId LocalSizeId` supplies the dimensions as IDs; `VK_KHR_maintenance4` adds Vulkan support for `LocalSizeId` ([extension appendix](../../../../vulkan-docs/src/appendices/VK_KHR_maintenance4.adoc#L38-L40)). An `OpEntryPoint` also lists the interface variables used by that entry point.

Why it matters here:
- The first test case assigns `LocalSizeId 2 3 1` to both entry points and requires `VK_KHR_maintenance4` ([support gate](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L441-L445)).
- The second case gives `mainA` and `mainB` different interface lists and routes their storage-buffer accesses to bindings 0 and 1.

## One Concrete Example

In `two_entry_points_execution_mode_id`, the assembled module names both compute entry points and associates each with `LocalSizeId 2 3 1` ([assembly builder](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L240-L329)). `mainB` stores multiplication results at elements 18 through 23, then `mainA` stores subtraction results at elements 12 through 17. Since the ranges differ, the host can check both dispatches after one submission.

## End-to-End Test Flow

```text
[host] allocate and fill two 24-element host-visible buffers
[host] create a descriptor set with binding 0, plus binding 1 for different interfaces
[host] assemble the selected SPIR-V module and create one shader module
[host] create pipelineB with pName="mainB" and pipelineA with pName="mainA"
[host] record a host-write-to-compute-read barrier, then dispatch pipelineB and pipelineA
[device] run six local invocations for each selected entry point
[host] wait for submission completion, invalidate mapped allocations, and compare result slots
[host] fail on the first mismatched integer; otherwise pass
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `Programs::init` builds CTS-authored SPIR-V assembly strings. The first case supplies `SpirVAsmBuildOptions` for SPIR-V 1.5; the second calls `spirvAsmSources.add("comp")` without that explicit options object ([builder branches](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L237-L436)).
- The two artifacts contain two compute entry points rather than separate shader modules.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `bufferA` | yes | set 0, binding 0 | both operations in case 1; `mainA` in case 2 | yes | Contains inputs and `mainA` results. |
| `bufferB` | yes | set 0, binding 1 in case 2 | `mainB` in case 2 | yes | Makes the second entry point use a separate descriptor interface. |
| `VkShaderModule` | yes | used for both pipelines | n/a | n/a | Holds both entry points. |
| `pipelineA`, `pipelineB` | yes | bound before dispatch | n/a | n/a | Select `mainA` and `mainB` with distinct `pName` values. |

## What Is Checked

- `two_entry_points_execution_mode_id` checks `bufferA[12+i] == dataASrc[i] - dataASrc[6+i]` and `bufferA[18+i] == dataASrc[i] * dataASrc[6+i]` for `i = 0..5` ([comparison](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L207-L217)).
- `two_entry_points_different_interfaces` checks addition in `bufferA[12..17]` and reversed-index multiplication in `bufferB[12..17]` ([comparison](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L219-L229)).
- The oracle uses exact integer equality.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf, because each leaf chooses one distinct multi-entry-point module form.
>
> **Candidate values:** `two_entry_points_execution_mode_id`, `two_entry_points_different_interfaces`.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `two_entry_points_execution_mode_id` | Selection of `mainA` or `mainB` by `pName` is wrong; `LocalSizeId` execution-mode handling is wrong; the shared binding-0 storage-buffer accesses or result stores are wrong. |
| `two_entry_points_different_interfaces` | Selection of an entry point is wrong; the per-entry-point interface or binding-0/binding-1 routing is wrong; `mainB` computes its local-ID-based reversed index incorrectly. |

Both leaves also depend on the recorded host-write-to-compute-read barrier and ordered dispatches. Their readback cannot isolate a shared setup or synchronization fault from entry-point handling when both leaves fail.

## Important Variations and Special Cases

- The first leaf requires `VK_KHR_maintenance4`; the second has no source-level support gate.
- `mainB` is dispatched before `mainA` in both leaves, but each writes a different result range or buffer, so this order does not create a shader data dependency.
- Case 2 uses `idxOut = 2 * local_x + local_y`; for a `1 x 1 x 1` dispatch, `idxIn = 5 - idxOut`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Runtime setup and checks | [EntryPointsTest::iterate](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L78-L233) | Resources, pipeline creation, barrier, dispatches, and integer oracle. |
| SPIR-V assembly | [Programs::init](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L235-L436) | Exact module text for both leaves. |
| Support and registration | [checkSupport and createMultipleShaderExtendedGroup](../../../modules/vulkan/spirv_assembly/vktSpvAsmMultipleShadersTests.cpp#L441-L463) | Extension gate and executable leaf names. |
| Vulkan pipeline selection | [Compute pipelines](../../../../vulkan-docs/src/chapters/pipelines.adoc#L814-L820) | A compute pipeline selects its entry point through module and `pName`. |

## Questions / Risk Points for User Audit

- Does the page make clear that `multiple_shaders_extended` is the test family and the two direct children are executable test case leaves?
- Does the page distinguish the two assembly-build paths without assuming an SPIR-V target for the second leaf that the source does not specify?
- Does the failure mapping preserve the shared-setup localization limit?

## Conversion Notes for Final Wiki Rewrite

- Keep the test case leaf as the behavior parameter and copy the failure table verbatim.
- Use two assembly walkthroughs because the two leaves exercise separate module forms.
- Publish the exact extracted assembly under `#### Source Code`; for this `spirv_assembly` page, omit published `#### SPIR-V` sections and retain the assemble, validate, and disassemble round trip as a validation gate.
- Distill the background to the two prerequisites: pipeline entry-point selection and compute execution modes/interfaces.
