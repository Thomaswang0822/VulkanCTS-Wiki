# Understanding Brief: Uniform control flow

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation preserves subgroup reconvergence when divergent compute or fragment control flow uses the stronger guarantees from `VK_KHR_shader_subgroup_uniform_control_flow`.

## Background Knowledge

### Subgroup reconvergence

A subgroup is a set of shader invocations that can execute a common control-flow path. Divergent branches can temporarily split those invocations. `VK_KHR_shader_subgroup_uniform_control_flow` provides stronger guarantees that a divergent subgroup reconverges in the same manner as invocation groups. The guarantee is attached to an entry point through the `SubgroupUniformControlFlowKHR` execution mode and requires the corresponding feature and supported stage.

Why it matters here:
- The cases deliberately diverge through branches, loops, `break`, `continue`, `return`, `switch`, atomics, and subgroup votes.
- The expected result depends on a later subgroup operation observing the intended subgroup participation after the divergent region.

### Full and partial subgroups

The compute cases use either a workgroup with a full final subgroup or one without a full final subgroup. The large cases use 256 invocations, while the small cases use a smaller workgroup. The source registers both full and partial forms, but the `*partial*` paths are excluded from the default mustpass file by Issue 4372. That exclusion is a test-selection rule, not evidence that the source does not register those cases.

## One Concrete Example

The exact representative case is `dEQP-VK.subgroups.subgroup_uniform_control_flow.large_full.subgroup_reconverge00`. Its Amber file declares a 128 by 2 compute workgroup and four coherent storage buffers. The test shader computes an index from `gl_SubgroupID`, `gl_SubgroupSize`, and `gl_SubgroupInvocationID`. When `a.a[gl_SubgroupID]` is even, invocation 0 adds 4 to `c`, other invocations increment `c`, and `subgroupElect()` writes a single elected invocation marker to `b`.

The Amber `fill` shader computes the expected marker and expected `c` contribution for the odd case, then the script runs `fill_pipe` followed by `test_pipe`. `EXPECT compare IDX 0 EQ 1 0 0 0` checks the first expected value and `EXPECT b EQ_BUFFER compare` compares the marker buffer with the expected buffer. The `test` shader is reconstructed directly from the Amber GLSL, not from a C++ `initPrograms` builder.

## End-to-End Test Flow

```text
[host] create the registered Amber-backed test case and select its `large` Amber directory
[host] parse `subgroup_reconverge00.amber` and load its `fill` and `test` GLSL programs
[host] compile the Amber GLSL with the script's `TARGET_ENV spv1.3`
[host] bind buffers `a`, `c`, and `compare` to `fill_pipe`
[host] run `fill_pipe` once to create expected values
[host] bind buffers `a`, `b`, `c`, and `d` to `test_pipe`
[device] run `test_pipe` once; divergent invocations update `c` and subgroup election updates `b`
[host] evaluate `compare` at index 0 and compare buffer `b` with `compare`
[host] return Amber success as CTS pass, or log the Amber error and return CTS fail
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The C++ registration creates an `AmberTestCase` whose filename is `vulkan/amber/subgroup_uniform_control_flow/large/subgroup_reconverge00.amber`.
- Amber parses the script during delayed initialization. Its shader metadata supplies the GLSL source, compute stage, and `spv1.3` target.
- `AmberTestCase::initPrograms` maps GLSL compute shaders to `glu::ComputeSource` and `vk::ShaderBuildOptions` with the parsed SPIR-V version. This page therefore documents the actual Amber route and does not invent a page-local `initPrograms` implementation.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `a` | yes, by Amber | yes | read by both shaders | indirectly through results | Supplies one parity selector per subgroup and is initialized as the series 0 through 255. |
| `b` | yes, by Amber | yes | written by `test` | compared with `compare` | Records the elected invocation for each index. |
| `c` | yes, by Amber | yes | read by `fill`, read and written by `test` | indirectly through the expected buffer flow | Records the branch-dependent increment or add operation. |
| `d` | yes, by Amber | yes | bound to `test`; not accessed by the shown GLSL | no | Completes the test pipeline's declared binding layout. |
| `compare` | yes, by Amber | yes | written by `fill`, read by the expectation logic | yes | Holds the expected `b` values for the buffer comparison. |
| `gl_SubgroupID`, `gl_SubgroupSize`, `gl_SubgroupInvocationID` | no, built-in values | no | read by both shaders | no | Define subgroup-local indexing and election behavior. |

## What Is Checked

- `fill` writes `compare.x[idx]` as 1 for the elected invocation when the subgroup selector is even, and as 4 for all entries when it is odd.
- The script checks `compare` index 0 against `1 0 0 0`.
- The script checks that `b` equals `compare`.
- Amber reports execution success only when all expectations pass. The C++ Amber instance maps that result to CTS `Pass` or `Fail`.

## Behavior Parameter Identification

> **Behavior parameter:** reconvergence axis
>
> **Candidate values:** workgroup size (`large`, `small`), final subgroup occupancy (`full`, `partial`), subgroup-size-control route (`control`, non-control), control-flow form (`subgroup_reconverge00` through `subgroup_reconverge20`), and fragment discard (`subgroup_reconverge_discard00`)

The primary behavioral axis is the reconvergence control-flow form. The other registered dimensions select the occupancy and feature environment in which that form runs. The default mustpass set includes the full compute forms and `discard`; the source-registered partial forms are excluded by the `*partial*` issue rule.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `subgroup_reconverge00` through `subgroup_reconverge20` | Incorrect subgroup reconvergence or compiler/control-flow lowering for the selected branch, loop, early-exit, switch, atomic, vote, or nested-control-flow form. |
| `large` or `small` | Incorrect handling of the corresponding compute workgroup size or its subgroup indexing. |
| `full` or `partial` | Incorrect handling of final subgroup occupancy. Partial values are source-registered but excluded from default mustpass by Issue 4372. |
| `control` or non-control | Incorrect feature or subgroup-size-control variant selection, including execution with the wrong `computeFullSubgroups` support route. |
| `subgroup_reconverge_discard00` | Incorrect fragment-stage subgroup behavior when invocations discard. |

## Important Variations and Special Cases

- The source builds four compute families from the Cartesian choices of large or small workgroups, full or partial final subgroups, and subgroup-size-control enabled or disabled. Each family uses the same 21 base control-flow forms with corresponding Amber filenames.
- `large_full` and `small_full` use the non-control route. `large_full_control` and `small_full_control` use the subgroup-size-control route. The support check rejects a compute case when its `computeFullSubgroups` support does not match the selected route.
- `large` requires at least 256 compute workgroup invocations. `small` does not take that large-workgroup limit path.
- The discard case is a separate fragment-stage Amber program under `discard`, with `small_workgroups` true and subgroup-size control disabled.
- The vote forms `subgroup_reconverge18` and `subgroup_reconverge19` add `VK_SUBGROUP_FEATURE_VOTE_BIT` to the required operation mask. The other forms require subgroup basic operations.
- The Amber scripts use `TARGET_ENV spv1.3`, while the C++ Amber loader maps that string to `vk::SPIRV_VERSION_1_3` for the source collection. The representative CCVDO uses `spirv1.3` for compilation and `spv1.3` for validation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test-family construction and four compute axes | [`createSubgroupUniformControlFlowTests()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L206-L337) | Registers large and small, full and partial, control and non-control families and their 21 Amber basenames. |
| Small and discard registration | [`createSubgroupUniformControlFlowTests()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L339-L451) | Registers the small variants and the fragment discard case. |
| Amber filename route | [`addTestsForAmberFiles()`](../../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L175-L201) | Builds the `vulkan/amber/<data_dir>/<subdir>/<basename>.amber` path and constructs `AmberTestCase`. |
| Amber parse and GLSL program route | [`AmberTestCase::parse()` and `initPrograms()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L475) | Shows delayed script parsing and GLSL compute source compilation from Amber metadata. |
| Amber execution and result mapping | [`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Executes the recipe and maps Amber success to CTS pass or fail. |
| Representative Amber script | [`subgroup_reconverge00.amber`](../../../data/vulkan/amber/subgroup_uniform_control_flow/large/subgroup_reconverge00.amber#L1-L76) | Defines the two shaders, buffers, pipelines, runs, and expectations. |
| Partial-case exclusion | [`test-issues.txt`](../../../mustpass/main/src/test-issues.txt#L23-L24) | Excludes every path containing `partial` from the default mustpass selection. |
| Representative mustpass path | [`subgroups.txt`](../../../mustpass/main/vk-default/subgroups.txt#L47724) | Confirms the exact `large_full.subgroup_reconverge00` case is selected. |
| Vulkan feature semantics | [`VK_KHR_shader_subgroup_uniform_control_flow`](../../../vulkan-docs/src/appendices/VK_KHR_shader_subgroup_uniform_control_flow.adoc#L21-L34) | Defines the stronger reconvergence guarantee and its SPIR-V extension relationship. |
| SPIR-V execution-mode requirements | [`spirvenv.adoc`](../../../vulkan-docs/src/appendices/spirvenv.adoc#L2742-L2752) | Requires the feature and supported stage for `SubgroupUniformControlFlowKHR`. |

## Questions / Risk Points for User Audit

- Does the reconvergence control-flow axis read as the primary behavior choice while the workgroup and feature axes remain test conditions?
- Is the distinction between source registration and default mustpass selection clear for all partial forms?
- Does the Amber-backed route make clear that the script, rather than a page-local C++ shader builder, owns the representative GLSL?
- Is the `fill` versus `test` expectation flow sufficient to explain why `b` is compared with `compare`?
- Is the distinction between the `VK_KHR_shader_subgroup_uniform_control_flow` feature, its SPIR-V execution mode, and the separate subgroup-size-control feature clear?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page centered on the four compute axes and the separate discard family. Use exact registered direct children in the hierarchy and explain deeper case names in parameter prose.
- Distill the background to subgroup reconvergence and the full versus partial final subgroup distinction.
- Use `dEQP-VK.subgroups.subgroup_uniform_control_flow.large_full.subgroup_reconverge00` as the single representative walkthrough.
- Reconstruct both Amber compute shaders only as needed to explain the selected `test` shader. Keep the `fill` shader's role in `Additional Info` or the runtime section.
- Copy the `### Failure Cause Mapping` table directly into the final page. Write `### Cause Analysis` during the rewrite.
- Keep the C++ registration path and `AmberTestCase` execution path in the Source Reference Appendix. Do not claim an ordinary C++ `initPrograms` implementation for this page.
