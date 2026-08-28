# Understanding Brief: `subgroups.builtin_mask_var`

## One-Sentence Test Purpose

This test checks whether each subgroup mask built-in marks exactly the invocation IDs defined by its relation to the current invocation, and whether ballot bit-count operations interpret that mask consistently across supported shader-stage paths.

## Background Knowledge

### Subgroup-local IDs and relational masks

A subgroup is a set of shader invocations that can execute subgroup operations together. Each invocation has a `gl_SubgroupInvocationID` in `[0, gl_SubgroupSize)`. The five mask built-ins are four-component 32-bit integer vectors whose bits describe invocation IDs relative to the current one: equal, greater-or-equal, greater, less-or-equal, or less.

Why it matters here:
- The expected bit at position `i` can be calculated directly by comparing `i` with `gl_SubgroupInvocationID`.
- Bits outside the relation must remain clear, and the same vector must produce the same population count whether counted component by component or with `subgroupBallotBitCount`.

### Stage-independent subgroup semantics

The mask meaning is not tied to one pipeline type. The CTS places the same core check in compute, graphics, framebuffer, ray-tracing, mesh, and task execution paths when those stages and features are supported. Framebuffer cases use CTS-authored SPIR-V assembly, while the other paths are built through the shared GLSL program generator.

## One Concrete Example

For `dEQP-VK.subgroups.builtin_mask_var.compute.subgroupeqmask`, `initPrograms` builds a compute shader using `gl_SubgroupEqMask`. Each invocation loops over every valid subgroup-local ID `i` and compares the expected predicate `i == gl_SubgroupInvocationID` with `subgroupBallotBitExtract(gl_SubgroupEqMask, i)`. It records `1` only if every bit agrees and the built-in mask's subgroup ballot bit count equals the sum of `bitCount` over its four words.

## End-to-End Test Flow

```text
[host] select one mask relation, execution family, stage set, and optional required-subgroup-size variant
[host] check subgroup, ballot, stage, and family-specific feature support
[host] build the generated GLSL programs, or direct SPIR-V framebuffer program, for the selected case
[host] create output resources and dispatch, draw, trace, or launch the selected pipeline path
[device] each tested invocation compares every mask bit with the expected invocation-ID relation
[device] each tested invocation independently checks the mask population count and writes 1 for success or 0 for failure
[host] read the result data through the shared subgroup harness
[host] pass only if every checked result is 1; required-subgroup-size cases repeat this for every supported power-of-two size
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `initPrograms` generates GLSL through `subgroups::initStdPrograms`. The compute, graphics, ray-tracing, mesh, and task variants embed the same `subgroupMask` body in stage-specific wrappers. They target SPIR-V 1.3, except ray-tracing and mesh-shading paths, which target SPIR-V 1.4.
- `initFrameBufferPrograms` supplies CTS-authored SPIR-V 1.3 assembly for vertex, tessellation-evaluation, tessellation-control, and geometry cases. It substitutes the selected built-in decoration and matching integer comparison instruction.
- Compute-like local sizes use specialization constants. Required-subgroup-size variants additionally create pipelines for each supported power-of-two subgroup size.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `result[]` output storage buffer | yes | yes | written | yes | Stores one `uint` verdict per tested invocation for compute, graphics, ray-tracing, mesh, and task paths. |
| `result` framebuffer output | yes, as an `R32_UINT` attachment | yes | written | yes | Carries the same 1/0 verdict when framebuffer tests avoid shader storage buffers. |
| Selected subgroup mask built-in | no | shader input built-in | read | no | Supplies the four-word mask whose bits and count are checked. |
| Local-size specialization constants | yes | pipeline specialization state | read as workgroup size | no | Determine the compute-like invocation grid; they are not ordinary descriptor resources. |

## What Is Checked

- For every `i` from zero to `gl_SubgroupSize - 1`, the shader compares the relation expected for the selected built-in with `subgroupBallotBitExtract(var, i)`. Any mismatch changes the invocation's verdict to `0`.
- The shader sums `bitCount` for all four words of the mask and requires `subgroupBallotBitCount(var)` to equal that sum.
- Shared host callbacks require every returned `uint` to equal `1`.
- A required-subgroup-size test must pass for every power-of-two size from `minSubgroupSize` through `maxSubgroupSize`.

## Behavior Parameter Identification

> **Behavior parameter:** `mask relation test case`
>
> **Candidate values:** `subgroupeqmask`, `subgroupgemask`, `subgroupgtmask`, `subgrouplemask`, `subgroupltmask`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupeqmask` | The equal mask does not contain exactly the current invocation's bit, or mask bit extraction/counting is inconsistent. |
| `subgroupgemask` | The greater-than-or-equal mask mishandles the current bit, a higher invocation bit, or the subgroup upper boundary. |
| `subgroupgtmask` | The greater-than mask includes the current invocation, omits a higher invocation, or mishandles the subgroup upper boundary. |
| `subgrouplemask` | The less-than-or-equal mask mishandles the current bit, a lower invocation bit, or the zero boundary. |
| `subgroupltmask` | The less-than mask includes the current invocation, omits a lower invocation, or mishandles the zero boundary. |

All values can also fail if `subgroupBallotBitExtract`, `subgroupBallotBitCount`, or result transport/readback disagrees with the direct relation and component-wise population-count checks.

## Important Variations and Special Cases

- The execution-family axis changes how verdicts are produced and transported, not the relational definition being tested. `graphics`, `compute`, `framebuffer`, `ray_tracing`, and `mesh` all reuse the same five relation choices.
- Compute and mesh/task cases have ordinary and `_requiredsubgroupsize` variants. The latter repeat execution over supported powers of two and require subgroup-size-control support.
- Mesh test names append `_mesh` or `_task`; framebuffer names append `_vertex`, `_tess_eval`, `_tess_control`, or `_geometry`.
- Ray-tracing and mesh families are excluded from Vulkan SC builds. Ray-tracing built-ins are volatile because invocation repacking can change subgroup composition and therefore the mask values.
- No `builtin_mask_var` entry appears in `mustpass/main/src/test-issues.txt`; the issue file does not add a page-specific exclusion or caveat.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Mask relation inventory | [enum and lookup tables](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L43-L66) | Defines the five exact registered relation choices and their comparison operators. |
| Core generated check | [`subgroupMask`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L139-L163) | Generates per-bit relation checking and independent population-count checking. |
| Framebuffer program builder | [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L165-L1143) | Builds direct SPIR-V 1.3 framebuffer-stage variants. |
| Standard program builder | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L1178-L1194) | Selects SPIR-V target and invokes the shared stage generator. |
| Stage wrappers | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1675) | Embeds the core check in compute, graphics, mesh/task, and ray-tracing shaders. |
| Support checks | [`supportedCheck`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L1196-L1245) | Applies subgroup, ballot, stage, subgroup-size, mesh, and ray-tracing requirements. |
| Runtime routing | [`test`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L1266-L1333) | Selects execution helper and loops over required subgroup sizes. |
| Registration | [`createSubgroupsBuiltinMaskVarTests`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L1335-L1450) | Constructs all families and exact leaf names. |
| Result callbacks | [`check` and `checkComputeOrMesh`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2640-L2663) | Require every returned value to equal one. |
| Built-in semantics | [Vulkan interfaces chapter](../../../../../vulkan-docs/src/chapters/interfaces.adoc#L4983-L5120) | Defines the five relational masks and their input-vector form. |
| Ray invocation repacking | [Vulkan ray-tracing chapter](../../../../../vulkan-docs/src/chapters/raytracing.adoc#L150-L175) | Explains why ray-tracing mask built-ins use volatile semantics around repack instructions. |

## Questions / Risk Points for User Audit

- Is `mask relation test case` the clearest name for the primary behavioral axis?
- Does the page clearly separate relation semantics from execution-family transport differences?
- The selected walkthrough uses generated compute GLSL. The framebuffer path instead uses direct SPIR-V assembly; is one generated compute walkthrough sufficient to explain the shared core behavior without duplicating the much larger framebuffer artifacts?

No inspected evidence leaves the selected representative path, its `initPrograms` builder, or the host pass condition unresolved.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.subgroups.builtin_mask_var.compute.subgroupeqmask` as the representative shader walkthrough through `initPrograms`.
- Preserve the `mask relation test case` axis and its five values in `## Behavior Parameters`.
- Copy the Failure Cause Mapping table above unchanged into the final page.
- Keep direct-SPIR-V framebuffer construction as a documented variation and source appendix entry; do not add a second walkthrough unless it materially improves explanation beyond the common mask check.
- Distill the subgroup-mask and stage-independence background into brief prerequisite bullets.
