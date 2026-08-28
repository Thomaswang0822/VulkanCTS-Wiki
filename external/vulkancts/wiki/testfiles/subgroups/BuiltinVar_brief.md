# Understanding Brief: `subgroups.builtin_var`

## One-Sentence Test Purpose

This test checks whether shader invocations report the four subgroup built-in values consistently with their specified ranges and the subgroup configuration observed by the host.

## Background Knowledge

### Subgroups and built-in values

A subgroup is an implementation-formed set of shader invocations that can execute subgroup operations together. `SubgroupSize` reports its invocation capacity, while `SubgroupLocalInvocationId` identifies an invocation within that range. For shaders with workgroups, `NumSubgroups` reports how many subgroups make up the local workgroup, and `SubgroupId` identifies one of them.

Why it matters here:

- `SubgroupLocalInvocationId` is in `[0, SubgroupSize - 1]`, but inactive invocation slots mean the IDs observed in an ordinary workgroup need not form a complete set.
- `SubgroupId` is in `[0, NumSubgroups - 1]`; both workgroup-level built-ins are available only in compute, mesh, and task execution models.
- A required subgroup size changes the pipeline configuration and makes `SubgroupSize` match the requested power-of-two value.

## One Concrete Example

For `dEQP-VK.subgroups.builtin_var.compute.subgroupsize_compute`, `initPrograms` emits one compute shader. Every invocation calculates a linear output-buffer offset and stores
`uvec4(gl_SubgroupSize, gl_SubgroupInvocationID, gl_NumSubgroups, gl_SubgroupID)`.
The host scans the first component of every record and requires it to equal the subgroup size reported by the subgroup test harness.

## End-to-End Test Flow

```text
[host] select a built-in value, execution path, stage, and optional required-subgroup-size variant
[host] generate the selected GLSL or direct SPIR-V programs
[host] check subgroup, stage, extension, feature, and required-size support
[host] create the output resource and the selected compute, graphics, framebuffer, ray-tracing, or mesh pipeline
[host] submit dispatch or draw work, iterating required subgroup sizes when requested
[device] each tested shader invocation writes its built-in observations to an SSBO or framebuffer attachment
[host] wait, make the output host-visible, and scan the relevant component or invocation-ID counts
[host] pass only if every checked value obeys the selected built-in's invariant
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L983-L1628) builds the compute GLSL directly, delegates mesh/task and ray-tracing GLSL generation to `initStdPrograms`, and supplies direct SPIR-V assembly for the ordinary graphics-stage path. Its targets are SPIR-V 1.3 for compute/graphics and SPIR-V 1.4 for mesh/task and ray tracing.
- [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L317-L962) supplies direct SPIR-V 1.3 programs for framebuffer cases.
- Compute, task, and mesh local sizes use specialization constant IDs 0, 1, and 2. Required-size cases rebuild or run the pipeline across supported power-of-two sizes.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Output SSBO of `uvec4` records | yes | yes | written | yes | Carries the four built-in values for compute, graphics, mesh/task, and ray-tracing checks. |
| `R32G32B32A32_UINT` color attachment | yes | yes | written | yes, through an image-to-buffer copy | Carries subgroup size and offset invocation ID for framebuffer cases without shader storage writes. |
| Required subgroup-size pipeline state | yes | pipeline state, not a descriptor | controls execution | no | Selects each supported power-of-two subgroup size for required-size variants. |

## What Is Checked

- `subgroupsize`: every observed first component equals the harness-provided subgroup size. Required-size variants repeat this check for every supported power-of-two size.
- `subgroupinvocationid`: every observed ID is below `subgroupSize`, and the number of recorded valid IDs equals the number of invocations that ran. Framebuffer and ordinary graphics/ray-tracing paths add 1024 in the shader and subtract it during checking.
- `numsubgroups`: every observed value is no greater than the number of local invocations in the workgroup.
- `subgroupid`: every observed ID is strictly less than the `NumSubgroups` value stored by the same invocation.

## Behavior Parameter Identification

> **Behavior parameter:** `built-in value`
>
> **Candidate values:** `subgroupsize`, `subgroupinvocationid`, `numsubgroups`, `subgroupid`

The primary axis is the built-in value, because it selects a different specified invariant and a different host check. Execution path, shader stage, and required subgroup size broaden where and under which pipeline configuration that invariant is tested.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroupsize` | Incorrect subgroup-size built-in value or required-subgroup-size application. |
| `subgroupinvocationid` | Out-of-range invocation index or incorrect recording of active invocations. |
| `numsubgroups` | Invalid workgroup subgroup-count built-in value. |
| `subgroupid` | Invalid subgroup index relative to the invocation's reported subgroup count. |

All values also depend on correct shader lowering, output addressing, pipeline execution, synchronization, and readback in the selected execution path.

## Important Variations and Special Cases

- `subgroupsize` and `subgroupinvocationid` cover graphics, compute, framebuffer, ray-tracing, mesh, and task paths where those paths are available. `numsubgroups` and `subgroupid` are limited to compute, mesh, and task shaders, matching their execution-model restrictions.
- Compute, mesh, and task leaves have ordinary and `_requiredsubgroupsize` forms. The latter iterate from `minSubgroupSize` through `maxSubgroupSize` by powers of two.
- `ray_tracing` and `mesh` are omitted in Vulkan SC builds. Runtime support checks also gate ray tracing, mesh/task features, subgroup support in the selected stage, and required subgroup-size support.
- The framebuffer path tests only `subgroupsize` and `subgroupinvocationid`, uses a color attachment instead of an SSBO, and covers vertex, tessellation control, tessellation evaluation, and geometry stages.
- The current `test-issues.txt` contains no entry matching `subgroups.builtin_var`; no issue-list exclusion changes this family's mustpass interpretation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Built-in definitions and host checks | [`TestType` and check callbacks](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L43-L304) | Defines the four values and their exact pass conditions. |
| Framebuffer program builder | [`initFrameBufferPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L317-L962) | Builds the non-SSBO stage programs and encodes the built-ins in color output. |
| Main program builder | [`initPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L983-L1628) | Generates compute GLSL and selects shared or direct-SPIR-V builders for other paths. |
| Support gates and runtime dispatch | [`supportedCheck`, `noSSBOtest`, and `test`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1630-L1944) | Applies feature gates and chooses the execution/check helper. |
| Registration loops | [`createSubgroupsBuiltinVarTests`](../../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1946-L2106) | Defines paths, built-in coverage, stages, and required-size variants. |
| Shared generated-stage helper | [`initStdPrograms`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1406-L1675) | Expands mesh/task and ray-tracing shader text used by this file. |
| Framebuffer copyback and verdict | [`makeTessellationEvaluationFrameBufferTestRequiredSubgroupSize`](../../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2438-L2637) | Shows draw, image-to-buffer copy, callback, and final pass/fail handling. |
| Vulkan built-in semantics | [`NumSubgroups`, `SubgroupId`, `SubgroupLocalInvocationId`, and `SubgroupSize`](../../../../vulkan-docs/src/chapters/interfaces.adoc#L3891-L3916) | Defines the values and their legal ranges/execution models; later definitions occur at lines 4955-4979 and 5123-5246. |
| Vulkan subgroup scope | [`Subgroup`](../../../../vulkan-docs/src/chapters/shaders.adoc#L3219-L3247) | Defines the invocation set represented by the built-ins. |

## Questions / Risk Points for User Audit

- Is the host's `numsubgroups <= totalLocalSize` check described narrowly enough? It establishes a valid upper bound, not an exact expected partition count.
- Is the invocation-ID check clearly distinguished from a dense-ID requirement? It validates range and that every invocation produced a valid record, but does not require every possible ID to appear.
- The graphics and framebuffer builders contain CTS-authored direct SPIR-V. The representative walkthrough deliberately uses the compute GLSL path so mandatory CCVDO output can be compiler-generated from an exact reconstruction.

No unresolved question changes the behavior axis, representative path, or validation claims.

## Conversion Notes for Final Wiki Rewrite

- Use `dEQP-VK.subgroups.builtin_var.compute.subgroupsize_compute` with the exact `initPrograms` builder for the representative walkthrough.
- Preserve the `built-in value` behavior axis and its four values exactly.
- Copy the Failure Cause Mapping table unchanged into the final page.
- Keep the exact-but-weak `NumSubgroups` upper-bound check and the invocation-ID counting semantics explicit.
- Move registration, support, and helper links to the source appendix; keep only the minimum subgroup and built-in semantics in Background Knowledge.
