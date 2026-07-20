# Understanding Brief: ray_tracing_pipeline.complexcontrolflow

## One-Sentence Test Purpose

This test checks whether a ray tracing pipeline preserves correct GLSL control-flow semantics, including conditionals, switches, loops, nested loops, and function-call patterns, when a shader-call instruction (`executeCallableEXT`, `traceRayEXT`, or `reportIntersectionEXT`) is embedded inside that control flow, so that the shader-call executes exactly the number of times and on the payload indices that the surrounding control flow prescribes.

## Background Knowledge

### Ray tracing shader-call instructions

The test centers on three shader-call instructions defined by `GL_EXT_ray_tracing` and exposed in SPIR-V as `OpExecuteCallableKHR`, `OpTraceRayKHR`, and `OpReportIntersectionKHR`. Each one suspends the calling shader invocation, runs another shader stage, and resumes the caller with side effects visible through shared storage.

- `executeCallableEXT(sbtIndex, location)` runs the callable shader at the given SBT index. Caller and callee share data through `callableDataEXT` and `callableDataInEXT` variables at the same `location`. The callee can mutate that data, and the caller sees the mutation after the call returns.
- `traceRayEXT(...)` runs the full traversal pipeline. Caller and callee share data through `rayPayloadEXT` and `rayPayloadInEXT` variables at the same `location`. After traversal, the caller resumes with the payload in whatever state the hit or miss shader left it.
- `reportIntersectionEXT(t, hitKind)` is only legal inside an intersection shader. It declares a candidate hit and triggers any-hit and closest-hit processing for that candidate.

Why these matter here: the test wraps these instructions inside nontrivial control flow. If a compiler lowers an `if`, `for`, `switch`, or function-call pattern incorrectly around the shader call, the wrong payload gets sent, the call runs the wrong number of times, or the post-call side effects land in the wrong image layer.

### Result image layout used by the test

The test writes a 3D `r32ui` storage image of size `width x height x 16`. The 16 Z-layers carry distinct observable signals:

- Z = 0: the per-launch `result` accumulator computed by the tested control-flow block.
- Z = 1..6: push constants `p.a` through `p.miss`, written verbatim so the host can confirm the push-constant block arrived unchanged.
- Z = 7: the launch index `id`, written by the callee. Confirms the callee ran with the right invocation coordinates.
- Z = 8..15: per-iteration or per-branch `v0`/`v1` values written by the callee, addressed by `(payload.x % 8) + 8`.

The host mirrors this layout in `getExpectedValues` and compares every layer element-by-element with a zero threshold.

## One Concrete Example

Reconstructed rgen shader body for the `if.execute_callable.rgen` case (`p = {41, 10000, 0x0F, 0xF0, 1, 1}`):

```glsl
v2 = v3 = uvec2(0, p.b);

if ((p.a & id) != 0)
    { v0 = uvec2(0, p.c & id); v1 = uvec2(0, (p.d & id) + 1); executeCallableEXT(0, 0); }
else
    { v0 = uvec2(0, p.d & id); v1 = uvec2(0, (p.c & id) + 1); executeCallableEXT(0, 1); }

result = v0.y + v1.y + v2.y + v3.y;
```

The `if` picks which payload (`v0` at location 0, or `v1` at location 1) the callable receives. The callee writes `v.y` into the layer addressed by `v.x`, then increments `v.y`. The host computes the same expected `result` and the same per-layer writes by mirroring the `if` condition in C++. Any divergence in branch direction, payload selection, or post-call increment surfaces as a mismatch.

## End-to-End Test Flow

```text
[host] choose testType x testOp x stage from the registration loop
[host] compute push constants for the chosen testType
[host] build descriptor set: storage image (binding 0) + top-level AS (binding 1)
[host] build ray tracing pipeline with shader groups: raygen, miss, hit, callable
[host] build shader binding tables for each group
[host] clear image to DEFAULT_CLEAR_VALUE (999999), barrier to GENERAL
[host] build bottom + top acceleration structures (single AABB geometry at z = -1 or z = +1)
[host] cmdTraceRays with launch size width x height x 1 (4 x 4 x 1)
[device] rgen runs the tested control-flow block; shader-call instructions suspend rgen and run callee / hit / miss / callable
[device] callee writes per-payload image layers and increments payload.y
[device] rgen resumes, accumulates result, writes Z = 0..6
[host] copy image to host-visible buffer, invalidate mapped range
[host] compute expected values via the same testType switch in C++
[host] compare every (z, y, x) element with zero threshold
[host] pass iff all 16 * 4 * 4 elements match
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL strings emitted by `initPrograms` with `vk::SPIRV_VERSION_1_4` build options. Source: [initPrograms](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1233-L1788).
- A shared `calleeMainPart` body used by both callable and miss callee shaders, plus a `shaderCallInstruction` template that substitutes `executeCallableEXT`, `traceRayEXT`, or `reportIntersectionEXT` for the `$` payload-index placeholder. Source: [calleeMainPart and shaderCallInstruction](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1236-L1251).
- Per-testType `opInMain` blocks that wrap the shader-call instruction in `if`, `for`, `switch`, or function-call patterns. Source: [opInMain switch](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1283-L1502).
- Pass-through ahit, chit, miss, and intersection shaders used as no-op stages when the testOp is `execute_callable` or `trace_ray`. Source: [getHitPassthrough, getMissPassthrough, getIntersectionPassthrough](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1189-L1231).
- A second miss/ahit/chit/sect set (`miss2`, `ahit2`, `chit2`, `sect2`) used for nested `trace_ray` cases where the inner trace hits a different SBT record. Source: [trace_ray shader set](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1631-L1738).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `resultImage` (3D `r32ui`, `4 x 4 x 16`) | yes | yes (binding 0) | written by rgen and callee | yes, via `cmdCopyImageToBuffer` | Carries the per-layer pass/fail signal |
| Top-level AS wrapping one BLAS | yes | yes (binding 1) | read by `traceRayEXT` | no | Required so `traceRayEXT` and `reportIntersectionEXT` cases have a valid AS to query |
| Single AABB BLAS at `z = -1` or `z = +1` | yes | yes | read by traversal | no | `z = -1` for hit cases, `z = +1` for miss cases, so the same rgen shader observes both paths |
| Push constants (6 `uint32_t`) | yes | yes (push_constant) | read by every shader | indirectly, via Z = 1..6 echoes | Drives the per-testType branch and loop bounds |
| Host-visible readback buffer | yes | yes | written by `cmdCopyImageToBuffer` | yes | Holds the 256-element result for host comparison |
| Raygen / miss / hit / callable SBTs | yes | yes | read by `cmdTraceRays` | no | Selects the callee shader and per-stage shader records |

## What Is Checked

- Z = 0 must equal the C++ `getExpectedValues` per-testType formula for `result`, computed from the same push constants and per-launch `id`.
- Z = 1..6 must equal the push constants `p.a`, `p.b`, `p.c`, `p.d`, `p.hitOfs`, `p.miss` in order. The rgen echoes them so the host can confirm the push-constant block reached the shader intact.
- Z = 7 must equal `id = gl_LaunchIDEXT.x + gl_LaunchSizeEXT.x * gl_LaunchIDEXT.y`. Written by the callee, so it confirms the callee ran with the right launch coordinates.
- Z = 8..15 must equal the per-iteration or per-branch `v0` / `v1` values, addressed by `(payload.x % 8) + 8`. The host computes the same addressing.
- The check is `bufferPtr[pos] != expected[pos]` for every `(z, y, x)`, with `failures` counted. Pass iff `failures == 0`. Source: [iterate](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1077-L1129).
- For `report_intersection` cases, the `fixed` flag is true, which suppresses the post-call `v0++` / `v1++` increment in both the shader and the host expected-value formula. For the other two ops, `fixed` is false and the increment applies on both sides.

## Behavior Parameter Identification

The primary behavioral axis is `testType`, the registered direct child of `complexcontrolflow` that selects the GLSL control-flow construct wrapped around the shader call.

> **Behavior parameter:** `testType` (intermediate node below `complexcontrolflow`)
>
> **Candidate values:** `if`, `loop`, `switch`, `loop_double_call`, `loop_double_call_sparse`, `nested_loop`, `nested_loop_loop_before`, `nested_loop_loop_after`, `function_call`, `nested_function_call`

A secondary axis is `testOp` (`execute_callable`, `trace_ray`, `report_intersection`), which selects the shader-call instruction. A third axis is `stage` (`rgen`, `chit`, `miss`, `sect`, `call`), which selects the stage that contains the control flow. Both are registered dimensions, but `testType` is the one that changes what control-flow property is being tested.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `if` | Branch direction mismatch: shader-call ran on the wrong payload, or the post-call increment landed on the wrong `v0` / `v1`, or the `result` sum used the wrong branch's values. |
| `loop` | Loop iteration count or accumulation mismatch: the shader-call ran the wrong number of times, or `result` did not accumulate per-iteration `v0.y + v1.y + v3.y` correctly. |
| `switch` | Case selection or fall-through mismatch: the wrong case body ran for a given `p.a & id`, or the `default` path executed when a defined case should have. |
| `loop_double_call` | Two shader calls per iteration executed in the wrong order, on the wrong payloads, or with wrong per-call `v0` / `v1` values; accumulation diverged. |
| `loop_double_call_sparse` | Sparse iteration filter `(x & p.b) != 0` was evaluated incorrectly, so calls ran on excluded iterations or were skipped on included ones. |
| `nested_loop` | Nested loop bounds or the `n = x + y * p.a` index computation diverged, so the shader-call ran at the wrong `n` or with the wrong `v0`. |
| `nested_loop_loop_before` | The pre-loop accumulator ran the wrong number of iterations or the second loop reused stale state from the first; ordering between the two loops was not preserved. |
| `nested_loop_loop_after` | Same as above but with the inner trace loop first and the accumulator second; the after-loop must not perturb the trace-loop's writes. |
| `function_call` | The `f1()` function did not run the shader-call in its own scope, or its local array initialization and accumulation diverged from the host formula. |
| `nested_function_call` | `f0()` called from `f1()` did not preserve callable-data side effects, or the nested call stack did not return to the correct caller state. |
| (all `testOp` values for a given `testType`) | If failure appears across all three `testOp` values for one `testType`, the cause is the control-flow construct itself, not the specific shader-call instruction. |
| (all `testType` values for one `testOp`/`stage`) | If failure appears across all `testType` values for one `testOp`, the cause is the shader-call instruction or its stage binding, not the control-flow construct. |

## Important Variations and Special Cases

- The `report_intersection` op is only registered for the `sect` stage, because `reportIntersectionEXT` is only legal inside an intersection shader. The registration loop skips all other stage combinations for this op.
- The `execute_callable` op is registered for `rgen`, `chit`, `miss`, and `call`. The `call` stage case uses a two-level callable invocation: rgen calls an outer callable (SBT index 1), which in turn calls the inner callable (SBT index 0) from inside the tested control flow. This exercises callable-from-callable recursion.
- The `trace_ray` op is registered for `rgen`, `chit`, and `miss`. When the stage is not `rgen`, the pipeline sets `maxRayRecursionDepth(2)` to allow the rgen's initial trace plus the inner trace issued from the tested stage. The `chit` and `miss` cases bind a second SBT hit group and miss group (`miss2`, `ahit2`, `chit2`, `sect2`) so the inner trace resolves to a different callee.
- The `fixed` flag (`testOp == TEST_OP_REPORT_INTERSECTION`) suppresses the post-call `v0++` / `v1++` increment in both the shader and the host formula. For `report_intersection`, the any-hit callee does not increment `inValue.y`, while for `execute_callable` and `trace_ray` the callee does.
- The bottom-level AS uses `z = -1.0f` for hit stages and `z = +1.0f` for the miss stage, so a single rgen shader that traces straight down `-Z` hits for `chit`, `ahit`, `sect`, and `call` cases, and misses for `miss` cases.
- Push constants differ per `testType` to exercise the relevant branches of each construct. For example, `TEST_TYPE_IF` uses `p.a = 32 | 8 | 1 = 41` so that the `(p.a & id)` condition varies across the 4x4 launch grid, while `TEST_TYPE_LOOP_DOUBLE_CALL_SPARSE` uses `p.a = 16` and `p.b = 5` so the sparse filter `(x & p.b) != 0` excludes roughly half the iterations.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `CaseDef` and `TestType` enum | [vktRayTracingComplexControlFlowTests.cpp#L61-L98](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L61-L98) | Defines the ten testType values and the case structure. |
| `getPushConstants` per-testType values | [vktRayTracingComplexControlFlowTests.cpp#L476-L550](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L476-L550) | Encodes the per-testType input values that drive branch and loop behavior. |
| `getExpectedValues` host-side mirror | [vktRayTracingComplexControlFlowTests.cpp#L707-L1075](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L707-L1075) | Reference image computation; the source of truth for pass/fail. |
| `initPrograms` GLSL emission | [vktRayTracingComplexControlFlowTests.cpp#L1233-L1788](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1233-L1788) | Generator for every case's shader set; basis for the walkthrough reconstruction. |
| `runTest` host flow | [vktRayTracingComplexControlFlowTests.cpp#L552-L705](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L552-L705) | Image clear, AS build, trace, copyback, host invalidation. |
| `iterate` pass/fail decision | [vktRayTracingComplexControlFlowTests.cpp#L1077-L1129](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1077-L1129) | Element-wise zero-threshold comparison. |
| `checkSupport` feature gates | [vktRayTracingComplexControlFlowTests.cpp#L1159-L1187](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1159-L1187) | Requires `VK_KHR_acceleration_structure` and `VK_KHR_ray_tracing_pipeline`, plus `maxRayRecursionDepth >= 2` for nested trace cases. |
| Registration loop | [vktRayTracingComplexControlFlowTests.cpp#L1797-L1884](../../../modules/vulkan/ray_tracing/vktRayTracingComplexControlFlowTests.cpp#L1797-L1884) | Builds the `complexcontrolflow.<testType>.<testOp>.<stage>` tree. |

## Questions / Risk Points for User Audit

- Is the primary behavioral axis correctly identified as `testType`? An alternative reading would treat `testOp` as the primary axis because it changes which shader-call instruction is tested, while `testType` only changes the surrounding control-flow construct. The brief picks `testType` because the family name `complexcontrolflow` and the test purpose both center on control-flow correctness, with `testOp` as a secondary axis that varies the kind of shader call being wrapped.
- Is the `report_intersection` op correctly described as `fixed = true`? The source flag is `const bool fixed = m_data.testOp == TEST_OP_REPORT_INTERSECTION`, and the any-hit callee for `report_intersection` does not include the `inValue.y++` line. Confirmed by inspection.
- Is the Z-layer addressing `(payload.x % 8) + 8` correctly attributed to the callee? Yes, the `calleeMainPart` string contains this expression verbatim.
- Should the walkthrough cover a multi-call case (`loop_double_call` or `nested_function_call`) instead of the simpler `if.execute_callable.rgen`? The brief recommends `if.execute_callable.rgen` as the default because it cleanly exposes branch-direction payload selection, which is the most fundamental control-flow property. A second walkthrough on `loop_double_call` could be added if the reader needs to see per-iteration accumulation, but the page can cover that variation in `Parameter Variation Summary` without a separate SPIR-V block.

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge list into a brief unordered list: shader-call instructions, payload sharing, result image Z-layer layout, push-constant-driven control flow.
- Use `if.execute_callable.rgen` as the single representative walkthrough. Reconstruct the rgen shader and the shared callable shader; generate SPIR-V for the rgen with target SPIR-V 1.4 (matching the source `ShaderBuildOptions`).
- Carry the `### Failure Cause Mapping` table directly into the final page's `### Failure Cause Mapping`.
- Write `### Cause Analysis` fresh, with one `####` subsection per distinct failure mechanism: branch-direction mismatch, loop accumulation divergence, sparse-filter mis-evaluation, nested-loop index computation, function-call scope, shared infrastructure (image clear / SBT / copyback).
- Move the per-testType push-constant table and the C++ expected-value formula references to the Source Reference Appendix.
- Keep the `testType` em-dash subsections short: one sentence for the construct, one for the test mechanism, one for the relation to other testType values.
