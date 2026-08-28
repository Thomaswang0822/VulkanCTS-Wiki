# Understanding Brief: `subgroups.quad`

## One-Sentence Test Purpose

This test checks whether subgroup quad broadcast and swap operations return the value from the required invocation in compute, graphics, framebuffer, mesh, and ray-tracing execution paths.

## Background Knowledge

### Quad scope inside a subgroup

A quad scope instance contains four invocations with adjacent subgroup invocation indices. The indices within one quad are 0, 1, 2, and 3, and the first index of each quad is a multiple of four. The Vulkan specification defines quad operations as operations on that four-invocation scope, even though the SPIR-V instructions carry a subgroup scope operand.

Why it matters here:
- `subgroupQuadBroadcast` selects one of the four values with an explicit index.
- The three swap operations use fixed partner mappings within the quad.
- The test must compare against the partner in the same quad, not against an arbitrary invocation in the subgroup.

### Subgroup invocation IDs and active invocations

`gl_SubgroupInvocationID` identifies an invocation within its subgroup. The test uses a ballot of `true` to record which invocations are active before it reads the selected partner. A ballot bit check prevents the test from treating an inactive partner as a valid result.

Why it matters here:
- The quad base is `gl_SubgroupInvocationID & ~0x3`.
- The local quad position is `gl_SubgroupInvocationID & 0x3`.
- A valid result requires the selected partner's ballot bit and equal data values.

## One Concrete Example

For `dEQP-VK.subgroups.quad.compute.subgroupquadswaphorizontal_uint`, each invocation reads `data[gl_SubgroupInvocationID]`. The horizontal mapping `{1, 0, 3, 2}` changes local quad positions 0 and 1 into partners and changes positions 2 and 3 into partners. The shader computes the partner index as the quad base plus that mapped local position, then writes 0 if the operation result differs from `data[otherID]`.

The test data is nonzero and indexed by subgroup invocation ID. This makes an incorrect partner mapping observable in the result buffer.

## End-to-End Test Flow

```text
[host] select the `subgroupquadswaphorizontal_uint` compute case
[host] create result and input storage buffers and initialize the input buffer with nonzero values
[host] generate the compute GLSL program from `initPrograms()` and `getTestSrc()`
[host] submit one compute dispatch through the common subgroup harness
[device] compute a global result index and capture the active subgroup mask
[device] apply `subgroupQuadSwapHorizontal` and derive the expected partner index
[device] write 1 for a matching active partner, or 0 otherwise
[host] read the result buffer after the harness wait
[host] require every checked result to equal 1
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The compute path combines the common `#version 450` header, subgroup extension declarations, specialization-constant local size, buffer declarations, global invocation index calculation, and the operation body returned by `getTestSrc()`. Ordinary operations use SPIR-V 1.3 build options. The dynamic-index broadcast case uses SPIR-V 1.5 because its index is not a constant.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `Buffer2.data` | yes | yes, set 0 binding 1 | read | no | Supplies distinct nonzero values for subgroup invocation IDs. |
| `Buffer1.result` | yes | yes, set 0 binding 0 | written | yes | Receives one pass value per global invocation and supplies the host check. |
| `gl_SubgroupInvocationID` | no, built-in | yes, as a shader input | read | no | Identifies the local subgroup position and selects the quad partner. |
| ballot mask | no, shader-local value | no | written and read by the shader | no | Records active invocations before the partner comparison. |

`Buffer1.result` and `Buffer2.data` use `std430` storage-buffer declarations in the compute program. The shared helper sizes the arrays for the maximum supported subgroup size and passes the observed subgroup size to the result callback.

## What Is Checked

- `subgroupBallot(true)` provides the active-invocation mask.
- The shader sets `tempRes` to 1, computes the operation result, and changes it to 0 when the selected partner is active but the values differ.
- The compute callback checks every element for the reference value 1.
- A required-subgroup-size case repeats the compute harness for each supported power-of-two size in the reported range and stops at the first failing size.

## Behavior Parameter Identification

> **Behavior parameter:** quad operation
>
> **Candidate values:** `subgroupquadbroadcast`, `subgroupquadbroadcast_nonconst`, `subgroupquadswaphorizontal`, `subgroupquadswapvertical`, `subgroupquadswapdiagonal`

The quad operation is the primary behavioral axis because it changes which invocation supplies the compared value or how the broadcast index is formed. Format, stage family, explicit stage, and required subgroup size change representation or execution conditions around that operation.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupquadbroadcast` | Incorrect constant quad index handling, quad membership, value selection, or result transport/checking. |
| `subgroupquadbroadcast_nonconst` | Incorrect dynamically uniform broadcast-index handling, quad membership, value selection, or result transport/checking. |
| `subgroupquadswaphorizontal` | Incorrect horizontal partner mapping, quad membership, value selection, or result transport/checking. |
| `subgroupquadswapvertical` | Incorrect vertical partner mapping, quad membership, value selection, or result transport/checking. |
| `subgroupquadswapdiagonal` | Incorrect diagonal partner mapping, quad membership, value selection, or result transport/checking. |

All five values also depend on correct stage support reporting, input binding, shader execution, and result readback.

## Important Variations and Special Cases

- The constant broadcast case emits four calls with literal indices 0 through 3. The nonconstant broadcast case loops over indices and also checks an index that is uniform only in active lanes and an index that is quad-uniform but not subgroup-uniform.
- Horizontal, vertical, and diagonal swaps use the fixed tables `{1, 0, 3, 2}`, `{2, 3, 0, 1}`, and `{3, 2, 1, 0}`.
- Compute and mesh cases can request each supported power-of-two subgroup size. The framebuffer family uses a std140 uniform input buffer because its helper does not use the storage-buffer compute path.
- Mesh and ray-tracing families are excluded from Vulkan SC registration by preprocessor guards.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Operation names and generated body | [`getOpTypeName()`, `getOpTypeCaseName()`, and `getTestSrc()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadTests.cpp#L77-L179) | Defines the five operation variants, swap tables, ballot guard, and comparison. |
| Compute program wrapper | [`initPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadTests.cpp#L193-L212) | Selects the SPIR-V target and passes the body to the common shader generator. |
| Common compute shader generation | [`initStdPrograms()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1434) | Adds the local-size inputs, buffers, global index, and result write. |
| Compute execution and required sizes | [`test()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadTests.cpp#L314-L368) | Selects the compute harness and iterates the required subgroup-size range. |
| Registration matrix | [`createSubgroupsQuadTests()`](../../../modules/vulkan/subgroups/vktSubgroupsQuadTests.cpp#L412-L565) | Registers operation, format, stage-family, stage, and required-size combinations. |
| Result callback | [`checkComputeOrMesh()`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2655-L2663) | Checks the full compute or mesh result range against 1. |
| Quad semantics | [Quad group operations](../../../../vulkan-docs/src/chapters/shaders.adoc#L3572-L3597) | Defines the quad operation scope and index interpretation. |
| Quad membership | [Quad scope](../../../../vulkan-docs/src/chapters/shaders.adoc#L3326-L3355) | Defines adjacent subgroup invocation indices and scope membership. |
| Dynamic broadcast index | [Subgroup broadcast feature](../../../../vulkan-docs/src/chapters/features.adoc#L952-L957) | Specifies when the broadcast index may be dynamically uniform. |

## Questions / Risk Points for User Audit

- Does the distinction between a subgroup invocation ID and the local position within a four-invocation quad remain clear?
- Is the ballot check's role in inactive-partner handling clear?
- Should the final page show only the compute walkthrough, or should a framebuffer example be added for the different std140 path?
- Are the five operation names and their exact registration tokens preserved?
- Is the SPIR-V 1.3 target for the representative ordinary compute case consistent with the source build options?

## Conversion Notes for Final Wiki Rewrite

- Use the compute horizontal-swap case as the representative walkthrough because its fixed partner table and comparison are compact and directly visible.
- Distill the quad scope and invocation-ID material into short page-local prerequisite bullets.
- Keep the operation, format, stage family, explicit stage, and required subgroup size dimensions in the page's parameter table.
- Put the full operation body in the shader walkthrough and keep host dispatch, required-size iteration, and result scanning in runtime execution.
- The `### Failure Cause Mapping` table from `## What Failure Means` should be copied directly into the final page's `## Failure Meaning` section. Write fresh cause analysis in the final page.
- Keep source links in the appendix after the explanatory sections.
