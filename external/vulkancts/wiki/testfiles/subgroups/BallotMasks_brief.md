# Understanding Brief: Ballot Mask Built-ins

## One-Sentence Test Purpose

This test checks whether the legacy `VK_EXT_shader_subgroup_ballot` mask built-ins mark exactly the subgroup invocation IDs selected by their equality or ordering relation to the current invocation.

## Background Knowledge

### Subgroup masks and invocation IDs

A subgroup is a set of shader invocations that execute together and can use subgroup operations. Each invocation has a local ID from zero through `SubgroupSize - 1`. A subgroup mask assigns one bit to each possible invocation ID, starting at the least significant bit.

Why it matters here:

- The tested built-ins do not report active predicates. They encode a relation between each possible invocation ID and the current invocation's local ID.
- `SubgroupEqMask`, `SubgroupGeMask`, `SubgroupGtMask`, `SubgroupLeMask`, and `SubgroupLtMask` differ only in the comparison used to select bits.

### Legacy GLSL and SPIR-V forms

`VK_EXT_shader_subgroup_ballot` maps the GLSL names `gl_SubGroup*MaskARB` to the SPIR-V `Subgroup*MaskKHR` built-ins. GLSL exposes each value as a 64-bit integer, while the Vulkan SPIR-V interface describes subgroup masks as four 32-bit components. This test limits required subgroup size cases to 64 because its GLSL comparison logic uses `uint64_t` masks.

## One Concrete Example

For `dEQP-VK.subgroups.ballot_mask.ext_shader_subgroup_ballot.compute.gl_subgroupeqmaskarb`, consider an invocation whose local subgroup ID is 3. The expected `gl_SubGroupEqMaskARB` value has bit 3 set and every other relevant bit clear. The shader computes `uint64_t(1) << gl_SubGroupInvocationARB`, intersects it with the built-in value, and records `0xf` when the bit is present or `0x2` when it is absent.

This equality case is intentionally simple. The other four mask types iterate over all invocation IDs below `gl_SubGroupSizeARB` and check both sides of the comparison boundary.

## End-to-End Test Flow

```text
[host] select one mask relation, execution family, shader stage, and optional required subgroup size mode
[host] check subgroup, extension, Int64, stage, and optional subgroup-size-control support
[host] build the stage programs and allocate the stage-specific result target
[host] dispatch, draw, trace rays, or run the framebuffer path
[device] read the selected gl_SubGroup*MaskARB built-in for the current invocation
[device] compare every relevant bit with the relation defined by gl_SubGroupInvocationARB
[device] write 0xf for a correct mask or 0x2 for a mismatch
[host] make the result visible and scan every expected result element
[host] pass only when every checked element equals 0xf, including every requested subgroup size iteration
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms` chooses SPIR-V 1.3 for ordinary graphics and compute setup, and SPIR-V 1.4 for ray tracing or mesh stages. Its compute branch supplies CTS-authored SPIR-V assembly for each mask relation through `spirvAsmSources`.
- Non-compute stages are assembled from the extension header, a stage-specific result declaration, and the relation-specific body returned by `getBodySource`.
- `initFrameBufferPrograms` uses the same relation-specific body in vertex, tessellation, or geometry framebuffer shaders.
- Compute and mesh local sizes use specialization constants. Required subgroup size cases run a power-of-two sweep from the device minimum through `min(maxSubgroupSize, 64)`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage buffer | yes | yes | written | yes | Compute, graphics, mesh, and ray tracing paths store one `uint` result per checked invocation or stage-defined output position. |
| Framebuffer result attachment | yes | yes | written | yes | Framebuffer variants export the same `0xf` or `0x2` result through a stage output and validate the rendered values. |
| `gl_SubGroup*MaskARB` built-in | no | shader input built-in | read | no | This is the implementation-provided mask under test, not a descriptor resource. |
| Local-size specialization constants | yes | pipeline specialization | read as workgroup size | no | They vary compute or mesh execution dimensions without changing the mask relation. |

## What Is Checked

- The device-side shader checks the selected relation for each invocation.
- `gl_SubGroupEqMaskARB` must contain the current invocation's bit.
- The other masks must contain every bit on the selected side of the current invocation and no bit on the opposite side, for IDs below `gl_SubGroupSizeARB`.
- A correct shader check writes `0xf`; any detected mismatch writes `0x2`.
- Shared host callbacks require every relevant result element to equal `0xf`.
- Required subgroup size variants must pass for every tested power-of-two size in the supported range capped at 64.

## Behavior Parameter Identification

> **Behavior parameter:** mask relation test case leaf stem
>
> **Candidate values:** `gl_subgroupeqmaskarb`, `gl_subgroupgemaskarb`, `gl_subgroupgtmaskarb`, `gl_subgrouplemaskarb`, `gl_subgroupltmaskarb`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `gl_subgroupeqmaskarb` | The equality mask does not set the current invocation's bit, or shader lowering reads the wrong built-in value. |
| `gl_subgroupgemaskarb` | The greater-than-or-equal mask has an incorrect boundary at the current invocation or incorrect higher bits. |
| `gl_subgroupgtmaskarb` | The greater-than mask incorrectly includes the current invocation or mishandles higher bits. |
| `gl_subgrouplemaskarb` | The less-than-or-equal mask has an incorrect boundary at the current invocation or incorrect lower bits. |
| `gl_subgroupltmaskarb` | The less-than mask incorrectly includes the current invocation or mishandles lower bits. |

## Important Variations and Special Cases

- **Execution family:** The same five relations run through `compute`, `graphics`, `framebuffer`, `ray_tracing`, and `mesh` paths where those stages exist. This changes pipeline setup and result transport, not the relation being checked.
- **Required subgroup size:** Compute, mesh, and task cases add `_requiredsubgroupsize` leaves. Each case sweeps supported power-of-two subgroup sizes through 64, so failures can be size-specific.
- **Stage support:** Graphics and ray tracing cases use only stages that advertise subgroup support. Framebuffer leaves isolate vertex, tessellation control, tessellation evaluation, and geometry stages without relying on shader storage writes in the tested stage.
- **Vulkan SC:** Ray tracing and mesh registrations are excluded from Vulkan SC builds.
- **Known issue list:** `external/vulkancts/mustpass/main/src/test-issues.txt` has no entry for this test family.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Mask names and expected bit relations | [`getMaskTypeName` and `getBodySource`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L74-L149) | Defines the five behavior values and their device-side checks. |
| Program construction | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L211-L1263) | Selects target SPIR-V versions, supplies direct compute assembly, and delegates other stage generation. |
| Feature and stage requirements | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1265-L1317) | Establishes extension, Int64, subgroup-size-control, ray tracing, mesh, and stage gates. |
| Runtime path and subgroup-size sweep | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1340-L1407) | Chooses the shared execution helper and runs required subgroup sizes through 64. |
| Registration loops | [`createSubgroupsBallotMasksTests`](../../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1415-L1527) | Generates mask, execution-family, stage, and required-size paths. |
| Shared result callbacks | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Require every expected result value to equal the supplied reference. |
| Vulkan mask semantics | [`SubgroupEqMask` through `SubgroupLtMask`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L4983-L5120) | Defines the bit selected by each built-in relation. |
| Legacy extension mapping | [`VK_EXT_shader_subgroup_ballot`](../../../../vulkan-docs/src/appendices/VK_EXT_shader_subgroup_ballot.adoc#L21-L69) | Maps GLSL ARB names to SPIR-V subgroup built-ins. |
| Required subgroup size validity | [`VkPipelineShaderStageRequiredSubgroupSizeCreateInfo`](../../../../vulkan-docs/src/chapters/pipelines.adoc#L1524-L1548) | Requires power-of-two values within the device limits. |

## Questions / Risk Points for User Audit

- The representative compute case is source-mapped to `initPrograms`, whose compute branch uses CTS-authored SPIR-V rather than the shared GLSL generator. The final walkthrough must state this distinction while also carrying the required CCVDO-generated and validated semantic reconstruction.
- The equality shader verifies that the current bit is set but does not independently reject extra bits. The page must not overstate the check as full equality-mask validation for that leaf.
- The four ordered masks check IDs below `gl_SubGroupSizeARB`; bits outside that range are not part of their device-side loop.
- Stage-family failures can also involve stage-specific transport or shared harness behavior, so failure causes should not be assigned only to mask generation.

## Conversion Notes for Final Wiki Rewrite

- Keep the mask relation test case leaf stem as the primary behavioral axis.
- Use the exact compute equality path as the single representative walkthrough and identify `initPrograms` as its builder.
- Distill subgroup mask ordering and legacy GLSL-to-SPIR-V mapping into Background Knowledge.
- Keep stage families and required subgroup size as secondary dimensions.
- Copy the `### Failure Cause Mapping` table unchanged into the final page.
- Explain equality-case validation precisely: it requires the current bit but does not test absence of every other bit.
